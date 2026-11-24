"""Declared world of the resume-paused takeover tests.

Step 7 of v0.15.0 resume-paused: the saved pause and its receipt are parsed
from declared bytes (``planner_world.snapshot``); exchange observations carry
a declared marked claim; panes, activity, histories, screens, result lines and
the Claude ledger decision are declared. Snapshots and exchange observations
are consumed in order, the last one repeating, so a test declares how the
durable records change from one look to the next. ``FakePair`` stands for the
Step 6 worker: it runs the pre-send checks of each declared phase against a
fresh declared listing, records each delivery and runs its declared effect. A
fake clock moves only when the takeover waits or an effect spends time; no
process, pane or real wait is involved.

Fix (code review round 1): ``FakePair.digest`` names the prompt the plan
accepted. It defaults to the digest of the world's first declared pause,
which stands for the pause the plan read; a test declares another digest to
model a prompt changed since planning. ``older`` returns a fresh pause whose
receipt names older bytes, and ``ASKING`` is an idle, ready pane that reports
a question with no blocking reason.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    FakeClock,
    FakeTransport,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import (
    API,
    FIRST,
    FakeHistory,
    FakeProbe,
    binding,
    live,
    routing,
    snapshot,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    THIRD_PANE,
    part,
    single_agent,
    slot,
)
from tools.resume_paused_claude_ledger import Absence, LedgerDecision
from tools.resume_paused_delivery_model import (
    ActionReport,
    DeliveryOutcome,
    Phase,
    SendStep,
)
from tools.resume_paused_evidence import PaneActivity, PaneObservation, ScreenVerdict
from tools.resume_paused_marker import Marker
from tools.resume_paused_models import CanonicalRoot, SessionRole
from tools.resume_paused_pane_guard import AllPaneIdleGuard, ClaudeScreen
from tools.resume_paused_plan_model import ActionKind, PlannedAction
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import Host, ReadAccount
from tools.resume_paused_review import ExchangeObservationKind, ExchangeSnapshot
from tools.resume_paused_reviewer_wait import ReviewerWait, WaitScope
from tools.resume_paused_takeover import MarkedTakeover, TakeoverPorts
from tools.review_exchange_models import Actor
from tools.review_exchange_models_coordination import MarkedClaimEvidence

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_delivery_model import PreSendCheck
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_marker import LiveExchange
    from tools.resume_paused_models import PromptDigest
    from tools.resume_paused_routing import SavedExchange, SavedRouting

ROOT = CanonicalRoot.from_path(API)
REQUESTOR_LAUNCH = "a1" * 16
REVIEWER_LAUNCH = "b2" * 16
OTHER_LAUNCH = "c3" * 16
GENERATION = 5
CLAIMED_GENERATION = 6
IDLE = PaneActivity("idle", "", draft_held=False, question="", ready=True)
WORKING = PaneActivity("working", "", draft_held=False, question="", ready=None)
QUESTION = PaneActivity("idle", "user", draft_held=False, question="Override the author?", ready=True)
ASKING = PaneActivity("idle", "", draft_held=False, question="Proceed?", ready=True)
IDLE_LINES = ("Claude Code", "> ")
PROVED = LedgerDecision(Absence.PROVED, (), ReadAccount())


def pair(reviewer_host: Host = Host.CODEX) -> SavedRouting:
    """Return the saved requestor pair: a Claude requestor and a reviewer of the declared host."""

    def change(mapping: dict[str, object]) -> None:
        slot(mapping, "reviewer")["host"] = reviewer_host.value

    return routing(API, change)


def unused(reviewer_host: Host = Host.CODEX) -> CheckoutSnapshot:
    """Return the saved pause before any receipt."""
    return snapshot(API, pair(reviewer_host))


def older() -> CheckoutSnapshot:
    """Return the fresh saved pause whose only receipt, an earlier schema 2 one, names older bytes."""
    return snapshot(API, pair(), receipt={"schema": 2, "digest": "c" * 64})


def accepted(state: CheckoutSnapshot | Exception) -> PromptDigest | None:
    """Return the digest of the prompt a plan reading this pause accepts, ``None`` without one."""
    return None if isinstance(state, Exception) or state.prompt is None else state.prompt.digest


def marker(role: SessionRole = SessionRole.REQUESTOR, reviewer_host: Host = Host.CODEX, *, pane: str | None = None, launch: str | None = None) -> Marker:
    """Return the marker a planned command of this role carries, bound to the first round."""
    pane = pane or (REQUESTOR_PANE if role is SessionRole.REQUESTOR else REVIEWER_PANE)
    launch = launch or (REQUESTOR_LAUNCH if role is SessionRole.REQUESTOR else REVIEWER_LAUNCH)
    return Marker(launch, pane, role, binding(unused(reviewer_host), pane, role, FIRST))


def used(reviewer_host: Host = Host.CODEX, requestor: Marker | None = None, changes: Mapping[str, str | None] | None = None) -> CheckoutSnapshot:
    """Return the saved pause consumed by the requestor's schema 3 receipt, with optional receipt field changes."""
    requestor = requestor or marker(reviewer_host=reviewer_host)
    fields: dict[str, Any] = {
        "schema": 3, "Launch id": requestor.launch_id, "Receiving pane": requestor.pane_id, "Assignment binding": requestor.binding,
    }
    return snapshot(API, pair(reviewer_host), receipt=fields | dict(changes or {}))


def _implementation(mapping: dict[str, object]) -> None:
    """Turn the pause into a single Claude implementation pause."""
    single_agent(mapping)
    part(mapping, "pause")["session_role"] = "implementation"


def _reviewer_pause(mapping: dict[str, object]) -> None:
    """Turn the pause into a saved reviewer pause of the pair, resuming the Codex reviewer."""
    part(mapping, "pause")["session_role"] = "reviewer"
    part(mapping, "targets")["resumed"] = dict(slot(mapping, "reviewer"))


def single(role: SessionRole = SessionRole.IMPLEMENTATION, changes: Mapping[str, str | None] | None = None) -> tuple[CheckoutSnapshot, Marker]:
    """Return a single-agent or reviewer pause consumed by its receipt, and the receiver's marker."""
    reviewer = role is SessionRole.REVIEWER
    saved = routing(API, _reviewer_pause if reviewer else _implementation)
    state = snapshot(API, saved, role=role.value)
    receiver_pane = REVIEWER_PANE if reviewer else REQUESTOR_PANE
    live_exchange = FIRST if reviewer else None
    receiver = Marker(REQUESTOR_LAUNCH, receiver_pane, role, binding(state, receiver_pane, role, live_exchange))
    fields: dict[str, Any] = {"schema": 3, "Launch id": receiver.launch_id, "Receiving pane": receiver.pane_id, "Assignment binding": receiver.binding}
    return snapshot(API, saved, role=role.value, receipt=fields | dict(changes or {})), receiver


def exchange(  # noqa: PLR0913 - one declared field of the observed exchange per argument
    claim: Marker | None = None, *, host: Host = Host.CLAUDE, owner: Actor = Actor.REQUESTOR, generation: int = GENERATION,
    live_exchange: LiveExchange = FIRST, kind: ExchangeObservationKind = ExchangeObservationKind.OBSERVED,
    requestor_nature: str | None = "claude", reviewer_nature: str | None = None,
) -> ExchangeSnapshot:
    """Return one observed exchange whose current marked claim names the declared marker, or none."""
    marked = None
    if claim is not None:
        evidence = MarkedClaimEvidence(claim.launch_id, claim.pane_id, host.value, claim.binding, live_exchange.round_number, live_exchange.occurrence)
        marked = evidence.issued(generation)
    return ExchangeSnapshot(
        kind, "exchange", "declared", round_number=live_exchange.round_number, occurrence=live_exchange.occurrence, owner=owner,
        ownership_generation=generation, requestor_nature=requestor_nature, reviewer_nature=reviewer_nature, marked_claim=marked,
    )


def taken(reviewer_host: Host = Host.CODEX) -> ExchangeSnapshot:
    """Return the exchange after the requestor's marked claim."""
    return exchange(marker(reviewer_host=reviewer_host))


def reviewing(reviewer_host: Host = Host.CODEX) -> ExchangeSnapshot:
    """Return the exchange after the activated reviewer's marked claim."""
    return exchange(
        marker(SessionRole.REVIEWER, reviewer_host), host=reviewer_host, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION,
    )


def pane(pane_id: str, host: Host) -> PaneRecord:
    """Return one live agent record in the checkout."""
    return live(pane_id, host)


def planned(kind: ActionKind, host: Host, *, pane_id: str | None = None, command: str | None = None) -> PlannedAction:
    """Return one planned reviewer action of the declared host, or a resume, with its marked command unless declared."""
    resume = kind is ActionKind.RESUME
    role = SessionRole.REQUESTOR if resume else SessionRole.REVIEWER
    target = pane_id or (REQUESTOR_PANE if resume else REVIEWER_PANE)
    if command is None:
        command = marked_command(host, kind, marker(role, Host.CODEX if resume else host, pane=target))
    return PlannedAction(kind, role, host, SESSION, target, f"{role.value} | pane", command, conditional=not resume)


def resumed(reviewer_host: Host = Host.CODEX, **changes: Any) -> ActionReport:  # noqa: ANN401 - declared report fields
    """Return the accepted resume report of the Claude requestor."""
    command = marked_command(Host.CLAUDE, ActionKind.RESUME, marker(reviewer_host=reviewer_host))
    return ActionReport(planned(ActionKind.RESUME, Host.CLAUDE, command=command), DeliveryOutcome.ACCEPTED, **changes)


@dataclass
class Declared[T]:
    """Items consumed in order, the last one repeating, counting the reads and running an optional effect."""

    items: list[T]
    reads: int = 0
    on_read: Callable[[int], None] | None = None

    def next(self) -> T:
        """Return the next item after the declared effect."""
        self.reads += 1
        if self.on_read is not None:
            self.on_read(self.reads)
        return self.items.pop(0) if len(self.items) > 1 else self.items[0]


@dataclass
class FakeSnapshots:
    """Declared saved pauses; an exception models unreadable evidence."""

    declared: Declared[CheckoutSnapshot | Exception]

    def read(self, root: CanonicalRoot) -> CheckoutSnapshot:
        """Return or raise the next declared snapshot."""
        assert root == ROOT
        item = self.declared.next()
        if isinstance(item, Exception):
            raise item
        return item


@dataclass
class FakeExchanges:
    """Declared observations of the saved exchange."""

    declared: Declared[ExchangeSnapshot]

    def observe(self, root: CanonicalRoot, exchange: SavedExchange) -> ExchangeSnapshot:
        """Return the next declared observation."""
        del root, exchange
        return self.declared.next()


@dataclass
class FakeAbsence:
    """Declared Claude ledger decision, recording each scope it was asked about."""

    decision: LedgerDecision | None = PROVED
    scopes: list[WaitScope] = field(default_factory=list[WaitScope])

    def decide(self, scope: WaitScope) -> LedgerDecision | None:
        """Record the scope and return the declared decision."""
        self.scopes.append(scope)
        return self.decision


@dataclass
class FakeScreens:
    """Declared Claude screen readings per pane, idle by default, recording each read."""

    readings: dict[str, ClaudeScreen] = field(default_factory=dict[str, ClaudeScreen])
    read_panes: list[str] = field(default_factory=list[str])
    on_read: Callable[[], None] | None = None

    def read(self, pane: PaneRecord, lines: tuple[str, ...]) -> ClaudeScreen:
        """Return the declared reading of the pane, after the declared effect."""
        del lines
        self.read_panes.append(pane.pane_id)
        if self.on_read is not None:
            self.on_read()
        return self.readings.get(pane.pane_id, ClaudeScreen.IDLE)


@dataclass
class FakeResults:
    """Declared compact result lines per pane; ``None`` models an unreadable source."""

    lines: dict[str, tuple[str, ...] | None] = field(default_factory=dict[str, tuple[str, ...] | None])
    on_read: Callable[[], None] | None = None

    def results(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Return the pane's declared lines after the declared effect."""
        del timeout
        if self.on_read is not None:
            self.on_read()
        return self.lines.get(pane.pane_id, ())


def listing(reviewer_host: Host = Host.CODEX, *extra: PaneRecord, activity: dict[str, PaneActivity] | None = None) -> PaneObservation:
    """Return one listing of the requestor, the reviewer and extra panes, all idle unless declared."""
    panes = (pane(REQUESTOR_PANE, Host.CLAUDE), pane(REVIEWER_PANE, reviewer_host), *extra)
    declared = dict.fromkeys((item.pane_id for item in panes), IDLE) | (activity or {})
    return PaneObservation(panes, declared)


@dataclass
class TakeoverWorld:
    """Every declared port of the takeover."""

    reviewer_host: Host = Host.CODEX
    clock: FakeClock = field(default_factory=FakeClock)
    transport: FakeTransport = field(default_factory=lambda: FakeTransport([listing()]))
    snapshots: FakeSnapshots = field(default_factory=lambda: FakeSnapshots(Declared([used()])))
    exchanges: FakeExchanges = field(default_factory=lambda: FakeExchanges(Declared([taken()])))
    history: FakeHistory = field(default_factory=FakeHistory)
    probe: FakeProbe = field(default_factory=lambda: FakeProbe({REVIEWER_PANE: ScreenVerdict.IDLE_EMPTY}))
    absence: FakeAbsence = field(default_factory=FakeAbsence)
    screens: FakeScreens = field(default_factory=FakeScreens)
    results: FakeResults = field(default_factory=FakeResults)

    @classmethod
    def claude_reviewer(cls) -> TakeoverWorld:
        """Return the taken-over world of a Claude requestor and a Claude reviewer."""
        world = cls(Host.CLAUDE, transport=FakeTransport([listing(Host.CLAUDE)]))
        world.snapshots = FakeSnapshots(Declared([used(Host.CLAUDE)]))
        world.exchanges = FakeExchanges(Declared([taken(Host.CLAUDE)]))
        world.transport.captures = {REQUESTOR_PANE: [IDLE_LINES], REVIEWER_PANE: [IDLE_LINES], THIRD_PANE: [IDLE_LINES]}
        return world

    def ports(self) -> TakeoverPorts:
        """Bundle the declared ports, with the real reviewer wait and the real Q27 guard."""
        wait = ReviewerWait(self.history, self.probe, self.absence)
        guard = AllPaneIdleGuard(self.transport, self.screens, self.clock)
        return TakeoverPorts(self.clock, self.clock, self.transport, self.snapshots.read, self.exchanges, wait, guard, self.results)

    def takeover(self) -> MarkedTakeover:
        """Return the takeover over the declared ports."""
        return MarkedTakeover(self.ports())


@dataclass
class FakePair:
    """The Step 6 worker as the takeover sees it: checks each declared phase on a fresh listing, then delivers.

    ``digest`` defaults to the prompt of the world's first declared pause.
    """

    world: TakeoverWorld
    root: CanonicalRoot = ROOT
    outcome: DeliveryOutcome = DeliveryOutcome.ACCEPTED
    failed: bool = False
    phases: tuple[Phase, ...] = ()
    on_deliver: Callable[[], None] | None = None
    delivered: list[tuple[PlannedAction, Phase]] = field(default_factory=list[tuple[PlannedAction, Phase]])
    checked: list[Phase] = field(default_factory=list[Phase])
    digest: PromptDigest | None = None

    def __post_init__(self) -> None:
        """Take the plan's accepted prompt from the first declared pause unless one is declared."""
        if self.digest is None:
            self.digest = accepted(self.world.snapshots.declared.items[0])

    def deliver(self, action: PlannedAction, phase: Phase, checks: tuple[PreSendCheck, ...] = ()) -> ActionReport:
        """Run every check before each declared phase; a refusal stops the send without input."""
        for current in self.phases or (phase,):
            refused = self._refused(current, action, checks)
            if refused is not None:
                return refused
        self.delivered.append((action, phase))
        if self.on_deliver is not None:
            self.on_deliver()
        return ActionReport(action, self.outcome, "acceptance-unproved" if self.failed else "", self.failed)

    def _refused(self, phase: Phase, action: PlannedAction, checks: tuple[PreSendCheck, ...]) -> ActionReport | None:
        """Run every check of one phase on a fresh listing; return the refused report of the first refusal."""
        observation = self.world.transport.observe(30.0)
        assert observation is not None
        (target,) = (item for item in observation.panes if item.pane_id == action.pane_id)
        step = SendStep(phase, self.root, action, observation, target)
        for check in checks:
            self.checked.append(phase)
            refusal = check.check(step)
            if refusal is not None:
                return ActionReport(action, DeliveryOutcome.REFUSED, refusal.reason, refusal.failed)
        return None


__all__ = [
    "ASKING",
    "CLAIMED_GENERATION",
    "GENERATION",
    "IDLE",
    "IDLE_LINES",
    "OTHER_LAUNCH",
    "PROVED",
    "QUESTION",
    "REQUESTOR_LAUNCH",
    "REQUESTOR_PANE",
    "REVIEWER_LAUNCH",
    "REVIEWER_PANE",
    "ROOT",
    "THIRD_PANE",
    "WORKING",
    "Declared",
    "FakeAbsence",
    "FakeExchanges",
    "FakePair",
    "FakeResults",
    "FakeScreens",
    "FakeSnapshots",
    "TakeoverWorld",
    "accepted",
    "exchange",
    "listing",
    "marker",
    "older",
    "pair",
    "pane",
    "planned",
    "resumed",
    "reviewing",
    "single",
    "taken",
    "unused",
    "used",
]


# eof
