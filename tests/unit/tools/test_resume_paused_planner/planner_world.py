"""Declared evidence world for the resume-paused planner tests.

Step 5 of v0.14.0 resume-paused: snapshots are parsed from prompt and receipt
bytes in memory, never read from files; live panes, activity, command
histories, screen probes, exchange observations and the session journal are
declared. ``World.plan`` runs the real planner with deterministic launch ids,
so both the example and the property tests compare whole plans.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING, Any

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
    receipt_text,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    routing_mapping,
)
from tools.resume_paused_artifacts import (
    CheckoutSnapshot,
    PromptState,
    classify_usage,
    parse_prompt,
    parse_receipt,
    render_routing_section,
)
from tools.resume_paused_evidence import (
    JournalIndex,
    ObservedCommand,
    PaneActivity,
    PaneObservation,
    ScreenVerdict,
)
from tools.resume_paused_input import PaneRecord
from tools.resume_paused_marker import LiveExchange, resolve_assignment
from tools.resume_paused_models import CanonicalRoot, SessionRole
from tools.resume_paused_plan_model import PlanRequest
from tools.resume_paused_planner import PlannerPorts, plan_run
from tools.resume_paused_profiles import CallerDecision, CallerOrigin, Host
from tools.resume_paused_review import ExchangeObservationKind, ExchangeSnapshot
from tools.resume_paused_routing import SavedRouting

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_plan_model import RunPlan
    from tools.resume_paused_routing import SavedExchange

API = Path("C:\\work\\api")
WEB = Path("C:\\work\\web")
HUMAN = CallerDecision(CallerOrigin.UNPROVED, ())
IDLE = PaneActivity("idle", "", draft_held=False, question="", ready=True)
FIRST = LiveExchange(1, 1)
LABELS = {REQUESTOR_PANE: "requestor | pane", REVIEWER_PANE: "reviewer | pane"}


def routing(root: Path = API, change: Callable[[dict[str, object]], None] | None = None) -> SavedRouting:
    """Return the paired requestor routing of one checkout, after an optional change."""
    mapping = routing_mapping(root)
    if change is not None:
        change(mapping)
    return SavedRouting.from_mapping(mapping)


def snapshot(  # noqa: PLR0913 - one declared part of the saved pause per argument
    root: Path = API, saved: SavedRouting | None = None, *, section: str | None = None,
    author: str = "claude", role: str = "requestor", receipt: dict[str, Any] | None = None,
) -> CheckoutSnapshot:
    """Parse one checkout's saved pause from declared bytes, with an optional receipt."""
    if section is None:
        section = "\n".join(render_routing_section(saved or routing(root))) + "\n"
    canonical = CanonicalRoot.from_path(root)
    data = prompt_text(root, section, author=author, role=role).encode("utf-8")
    prompt, reading = parse_prompt(data, canonical)
    parsed = None
    if receipt is not None:
        digest = receipt.pop("digest", prompt.digest.value)
        parsed = parse_receipt(receipt_text(receipt.pop("schema"), digest, root, receipt).encode("utf-8"))
    return CheckoutSnapshot(canonical, root / ".reviews", classify_usage(prompt, parsed, canonical), prompt, parsed, reading)


def live(  # noqa: PLR0913 - one declared field of the live record per argument
    pane: str, host: Host | None = Host.CLAUDE, root: Path | str = API, *,
    session: str = SESSION, name: str | None = None, agent_session: str | None = None,
) -> PaneRecord:
    """Declare one live TUIOS record; a ``None`` host declares a plain shell pane."""
    harness, apps = {Host.CLAUDE: ("claude-code", ()), Host.CODEX: ("", ("codex",)), None: ("", ())}[host]
    return PaneRecord(pane, session, LABELS.get(pane, "shell") if name is None else name, str(root), harness, apps, agent_session)


def binding(state: CheckoutSnapshot, pane: str, role: SessionRole, live_exchange: LiveExchange | None = FIRST) -> str:
    """Return the assignment binding a planned marker must carry."""
    assert state.prompt is not None
    assert state.routing is not None
    assert state.routing.routing is not None
    return resolve_assignment(state.routing.routing, state.prompt.digest, pane, role, live_exchange).digest()


@dataclass
class FakeHistory:
    """Declared typed commands per pane; ``None`` models an unreadable history."""

    by_pane: dict[str, tuple[ObservedCommand, ...] | None] = field(default_factory=dict[str, tuple[ObservedCommand, ...] | None])

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return the declared commands of one pane."""
        return self.by_pane.get(pane.pane_id, ())


@dataclass
class FakeProbe:
    """Declared screen verdicts per pane, recording each probe."""

    verdicts: dict[str, ScreenVerdict] = field(default_factory=dict[str, ScreenVerdict])
    probed: list[str] = field(default_factory=list[str])

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the declared verdict, unsupported by default."""
        self.probed.append(pane.pane_id)
        return self.verdicts.get(pane.pane_id, ScreenVerdict.UNSUPPORTED)


@dataclass
class FakeExchanges:
    """Declared observation of every saved exchange, recording each observed checkout."""

    kind: ExchangeObservationKind = ExchangeObservationKind.OBSERVED
    round_number: int | None = 1
    occurrence: int | None = 1
    observed: list[str] = field(default_factory=list[str])

    def observe(self, root: CanonicalRoot, exchange: SavedExchange) -> ExchangeSnapshot:
        """Return the declared observation."""
        self.observed.append(root.key)
        return ExchangeSnapshot(self.kind, exchange.identity().key, "declared", round_number=self.round_number, occurrence=self.occurrence)


@dataclass
class World:
    """Every declared observation one planner run reads."""

    snapshots: dict[str, CheckoutSnapshot | Exception] = field(default_factory=lambda: {"c:\\work\\api": snapshot()})
    panes: list[PaneRecord] = field(default_factory=lambda: [live(REQUESTOR_PANE), live(REVIEWER_PANE, Host.CODEX)])
    activity: dict[str, PaneActivity] = field(default_factory=lambda: {REQUESTOR_PANE: IDLE, REVIEWER_PANE: IDLE})
    history: FakeHistory = field(default_factory=FakeHistory)
    probe: FakeProbe = field(default_factory=FakeProbe)
    exchanges: FakeExchanges = field(default_factory=FakeExchanges)
    journal: JournalIndex = field(default_factory=JournalIndex)
    reads: list[str] = field(default_factory=list[str])

    def read(self, root: CanonicalRoot) -> CheckoutSnapshot:
        """Return the declared snapshot, a prompt-less one by default, or raise a declared failure."""
        self.reads.append(root.key)
        declared = self.snapshots.get(root.key, CheckoutSnapshot(root, None, PromptState.NO_PROMPT))
        if isinstance(declared, Exception):
            raise declared
        return declared

    def plan(self, *, discovered: bool = True, caller: CallerDecision = HUMAN, **request: Any) -> RunPlan:  # noqa: ANN401
        """Run the planner over the declared world with launch ids 1, 2, ..."""
        ids = (f"{number:032x}" for number in count(1))
        ports = PlannerPorts(self.read, self.exchanges, self.history, self.probe, self.journal, lambda: next(ids))
        observation = PaneObservation(tuple(self.panes), self.activity) if discovered else None
        return plan_run(PlanRequest(caller, **request), observation, ports)


type Change = Callable[[World], None]


def unchanged(world: World) -> None:
    """Keep the declared world as it is."""
    del world


def replacing(pane: str, record: PaneRecord | None) -> Change:
    """Replace the live record of one pane, or remove it when ``record`` is ``None``."""

    def apply(world: World) -> None:
        world.panes = [live_record for live_record in world.panes if live_record.pane_id != pane]
        if record is not None:
            world.panes.append(record)

    return apply


def adding(record: PaneRecord) -> Change:
    """Add one more live record, keeping every other."""

    def apply(world: World) -> None:
        world.panes.append(record)

    return apply


def active(pane: str, activity: PaneActivity | None) -> Change:
    """Declare one pane's activity, or remove it when ``activity`` is ``None``."""

    def apply(world: World) -> None:
        if activity is None:
            world.activity.pop(pane)
        else:
            world.activity[pane] = activity

    return apply


__all__ = [
    "API",
    "FIRST",
    "HUMAN",
    "IDLE",
    "WEB",
    "Change",
    "FakeExchanges",
    "FakeHistory",
    "FakeProbe",
    "World",
    "active",
    "adding",
    "binding",
    "live",
    "replacing",
    "routing",
    "snapshot",
    "unchanged",
]


# eof
