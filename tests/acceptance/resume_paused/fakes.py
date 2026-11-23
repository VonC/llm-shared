"""Fake TUIOS, host adapters and receiving agents of the resume-paused acceptance tests.

Step 8 of v0.14.0 resume-paused validates the whole installed workflow at the
process boundary without live TUIOS. ``FakeTuios`` is the argument-list runner
behind the real ``TuiosTransport``: it answers ``list-agents --json``,
``capture-pane``, ``ask-agent`` (resolving the ``session:S name:N`` glob
selector) and ``send-keys``, records every call, and types each asked command
into its pane. A pane's ``ReceiverAgent`` then runs the Step 4 receiver
harness: the real validator over live fake discovery, then the real schema 3
receipt, journal entry and locked marked claim against the temporary
checkout's files. The planner, delivery, takeover, checkout guard, saved-pause
reader and saved-exchange observer are the production ones composed by
``tools.resume_paused.compose``; only the host-profile adapters (command
history, agent log, delivery profiles, input proofs, screen and ledger
verdicts) are declared, because no host profile is pinned yet (plan Q05).
A fake clock moves only when the run waits. Nothing starts a process.
"""

from __future__ import annotations

import io
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fnmatch import fnmatchcase
from functools import partial
from itertools import count
from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.resume_paused_receiver_test_support import (
    NATURES,
    ReceiverCheckout,
    ReceiverHarness,
    SequenceOutcome,
    Step,
    scenario_routing,
)
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
)
from tests.unit.tools.test_resume_paused_cli.test_resume_paused_cli_tdd import (
    listing_json,
)
from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    CLAUDE_PROFILE,
    CODEX_PROFILE,
    EMPTY,
    FOOTER,
    PLACEHOLDER,
    PROMPT,
    FakeClock,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    THIRD_PANE,
    part,
)
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    FakeAbsence,
    FakeScreens,
)
from tools import resume_paused as cli
from tools.resume_paused_artifacts import read_checkout_snapshot, render_routing_section
from tools.resume_paused_claim import marked_claim_verifier
from tools.resume_paused_delivery_model import LogEvent, LogKind
from tools.resume_paused_evidence import (
    JournalIndex,
    ObservedCommand,
    PaneActivity,
    ScreenVerdict,
)
from tools.resume_paused_guard import CheckoutGuard
from tools.resume_paused_input import (
    InputEvidence,
    PaneRecord,
    TuiosDiscovery,
    pane_host,
)
from tools.resume_paused_marker import (
    MARKER_FLAG,
    Marker,
    ResultLine,
    marker_in_command,
)
from tools.resume_paused_models import PROMPT_NAME, SessionRole
from tools.resume_paused_profiles import CommandResult, Host, ReadAccount
from tools.resume_paused_validation import ReceiverValidator
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_delivery_model import DeliveryProfile, Remaining
    from tools.resume_paused_input import CarriedIdentity, InputProver
    from tools.resume_paused_models import CanonicalRoot

T0 = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
CODEX_SESSION = "019a0000-0000-7000-8000-000000000001"
IDLE = PaneActivity("idle", "", draft_held=False, question="", ready=True)
WORKING = PaneActivity("working", "", draft_held=False, question="", ready=None)
CLEARED = "New conversation started."
AGENT_IDS = {Host.CLAUDE: "claude", Host.CODEX: "chatgpt"}
_REVIEW_ROLES = {SessionRole.REQUESTOR: ReviewRole.REQUESTOR, SessionRole.REVIEWER: ReviewRole.REVIEWER}


@dataclass
class FakePane:
    """One live TUIOS pane: its record, activity, screen, typed inputs and agent log, and what reacts to input.

    ``screen`` ``None`` makes every capture fail. ``typing`` is how the pane
    takes an asked command: ``submit`` runs it, ``hold`` leaves it unsubmitted
    in a Codex input box, ``drop`` loses it. ``clears`` is whether a Codex
    ``/new`` shows its cleared line.
    """

    record: PaneRecord
    activity: PaneActivity | None = IDLE
    screen: tuple[str, ...] | None = ()
    typed: list[tuple[str, datetime]] = field(default_factory=list[tuple[str, datetime]])
    log: list[LogEvent] | None = field(default_factory=list[LogEvent])
    agent: Callable[[str], None] | None = None
    typing: str = "submit"
    clears: bool = True
    results: list[str] = field(default_factory=list[str])

    @property
    def host(self) -> Host | None:
        """Return the host the record shows."""
        return pane_host(self.record)


def _log_claude(pane: FakePane, command: str, now: datetime) -> None:
    """Log a typed prompt, or the session a ``/clear`` starts, unless the pane's log is unreadable."""
    if pane.log is None:
        return
    clear = command == CLAUDE_PROFILE.clear_command
    pane.log.append(LogEvent(LogKind.CLEAR, now) if clear else LogEvent(LogKind.PROMPT, now, command))


def _redraw_codex(pane: FakePane, command: str) -> None:
    """Show an empty Codex input box, with one more cleared line after a confirmed ``/new``."""
    cleared = (CLEARED,) if command == CODEX_PROFILE.clear_command and pane.clears else ()
    kept = [line for line in pane.screen or () if line == CLEARED]
    pane.screen = (EMPTY[0], *kept, *cleared, PROMPT + PLACEHOLDER, FOOTER)


@dataclass
class ScenarioClock(FakeClock):
    """Fake clock whose every wait also lets the receiving agents work, as real agents do while the run waits."""

    after_sleep: Callable[[], None] | None = None

    def sleep(self, seconds: float) -> None:
        """Advance the clock, then run the declared effect."""
        super().sleep(seconds)
        if self.after_sleep is not None:
            self.after_sleep()


@dataclass
class FakeTuios:
    """Argument-list runner standing for the ``tuios`` executable, recording every call.

    A marked command typed into a pane does not run its receiving workflow at
    once: like a real agent, it works while the launch waits, so the
    delivery's own acceptance proof sees the command as the pane's latest
    input before the receiver acts (``flush``).
    """

    clock: FakeClock
    panes: dict[str, FakePane] = field(default_factory=dict[str, FakePane])
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])
    discovery_exit: int = 0
    on_listing: Callable[[int], None] | None = None
    pending: list[partial[None]] = field(default_factory=list[partial[None]])
    _lock: threading.RLock = field(default_factory=threading.RLock)

    def runner_for(self, seconds: float) -> FakeTuios:
        """Return this runner whatever bound the transport grants."""
        del seconds
        return self

    def add(self, pane: FakePane) -> FakePane:
        """Declare one live pane."""
        self.panes[pane.record.pane_id] = pane
        return pane

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Answer one ``tuios`` command by its verb; an unknown command fails."""
        handlers: dict[str, Callable[[Sequence[str]], CommandResult]] = {
            "list-agents": self._listing, "capture-pane": self._capture, "ask-agent": self._asked, "send-keys": self._entered,
        }
        with self._lock:
            self.calls.append(tuple(arguments))
            handler = handlers.get(arguments[1])
            return CommandResult(1, "") if handler is None else handler(arguments)

    def _listing(self, arguments: Sequence[str]) -> CommandResult:
        """Answer ``list-agents --json`` from every declared pane, after the declared listing effect."""
        del arguments
        if self.on_listing is not None:
            self.on_listing(sum(1 for call in self.calls if call[1] == "list-agents"))
        activity = {key: pane.activity for key, pane in self.panes.items() if pane.activity is not None}
        return CommandResult(self.discovery_exit, listing_json([pane.record for pane in self.panes.values()], activity))

    def _capture(self, arguments: Sequence[str]) -> CommandResult:
        """Answer ``capture-pane`` with the pane's screen; an unknown pane or a ``None`` screen fails."""
        pane = self.panes.get(arguments[5])
        screen = None if pane is None else pane.screen
        return CommandResult(1, "") if screen is None else CommandResult(0, "\n".join(screen))

    def _asked(self, arguments: Sequence[str]) -> CommandResult:
        """Answer ``ask-agent``: the selector follows ``--select``, the command is the last argument."""
        return CommandResult(0 if self._ask(arguments[3], arguments[-1]) else 1, "")

    def _entered(self, arguments: Sequence[str]) -> CommandResult:
        """Answer ``send-keys``: the full pane id follows ``-w``."""
        return CommandResult(0 if self._enter(arguments[5]) else 1, "")

    def _ask(self, selector: str, command: str) -> bool:
        """Type the command into the one pane the glob selector names."""
        terms = dict(term.split(":", 1) for term in selector.split(" "))
        matches = [
            pane for pane in self.panes.values()
            if fnmatchcase(pane.record.session.casefold(), terms["session"].casefold())
            and fnmatchcase(pane.record.name.casefold(), terms["name"].casefold())
        ]
        if len(matches) != 1:
            return False
        pane = matches[0]
        if pane.typing == "submit":
            self._submit(pane, command)
        elif pane.typing == "hold":
            pane.screen = (EMPTY[0], PROMPT + command, FOOTER)
        return True

    def _enter(self, pane_id: str) -> bool:
        """Submit the command a Codex pane holds unsubmitted."""
        pane = self.panes[pane_id]
        assert pane.screen is not None
        self._submit(pane, pane.screen[1].removeprefix(PROMPT))
        return True

    def _submit(self, pane: FakePane, command: str) -> None:
        """Record the typed input, then its host's trace: a Claude log event or a fresh Codex screen; queue the agent."""
        now = self.clock.now()
        pane.typed.append((command, now))
        if pane.host is Host.CLAUDE:
            _log_claude(pane, command, now)
        elif pane.host is Host.CODEX:
            _redraw_codex(pane, command)
        if pane.agent is not None and MARKER_FLAG in command:
            self.pending.append(partial(pane.agent, command))

    def flush(self) -> None:
        """Let every agent that received a marked command run its receiving workflow now, in typing order."""
        with self._lock:
            ready, self.pending[:] = list(self.pending), []
        for reaction in ready:
            reaction()

    def inputs(self) -> list[tuple[str, ...]]:
        """Return every call that types into a pane."""
        return [call for call in self.calls if call[1] in {"ask-agent", "send-keys"}]


@dataclass
class WorldHistory:
    """``CommandHistory`` over each fake pane's typed inputs, oldest first."""

    tuios: FakeTuios
    unreadable: set[str] = field(default_factory=set[str])

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return the pane's typed commands with their times, ``None`` when declared unreadable."""
        if pane.pane_id in self.unreadable:
            return None
        live = self.tuios.panes.get(pane.pane_id)
        return () if live is None else tuple(ObservedCommand(text, at) for text, at in live.typed)


@dataclass
class WorldLog:
    """``AgentLog`` over each fake Claude pane's prompt and clear events."""

    tuios: FakeTuios

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Return the pane's events, ``None`` when its log is declared unreadable."""
        live = self.tuios.panes.get(pane.pane_id)
        return None if live is None or live.log is None else tuple(live.log)


@dataclass
class WorldProver:
    """``InputProver`` proving a marked command from the pane's latest typed input, at or after the lower bound.

    The receiver harness validates the marker under its canonical
    ``/resume-session`` spelling, so the proof matches the marker the latest
    input carries; the delivery's own proof passes the exact typed command.
    """

    tuios: FakeTuios

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Prove the marker of the pane's latest typed input."""
        del carried
        live = self.tuios.panes.get(pane.pane_id)
        latest = live.typed[-1] if live is not None and live.typed else None
        proved = latest is not None and latest[1] >= not_before and _marker_text(latest[0]) == _marker_text(command) is not None
        session = CODEX_SESSION if pane_host(pane) is Host.CODEX else None
        reasons = () if proved else ("marked-input-not-latest",)
        return InputEvidence(proved=proved, session_id=session if proved else None, reasons=reasons, account=ReadAccount())


def _marker_text(command: str) -> str | None:
    """Return the marker one command carries, ``None`` without one."""
    return command.split(MARKER_FLAG, 1)[1].strip() if MARKER_FLAG in command else None


@dataclass
class HostProfiles:
    """``ProfileGate`` pinning the synthetic delivery profile of each pane's host."""

    unsupported: set[str] = field(default_factory=set[str])

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Return the declared profile of the pane's host, ``None`` for a declared unsupported pane."""
        if pane.pane_id in self.unsupported:
            return None
        host = pane_host(pane)
        return None if host is None else {Host.CLAUDE: CLAUDE_PROFILE, Host.CODEX: CODEX_PROFILE}[host]


class HostedCheckout(ReceiverCheckout):
    """``ReceiverCheckout`` whose receipts name the receiving pane's agent id, as that host's resume-session writes it."""

    def __init__(self, tmp_path: Path, phase: str) -> None:
        """Prepare the checkout; each receiving pane's agent id is declared later."""
        super().__init__(tmp_path, phase)
        self.agents: dict[str, str] = {}

    def consume(self, marker: Marker, changes: dict[str, str | None] | None = None) -> bytes:
        """Write the schema 3 receipt with the receiving pane's agent as its resumer."""
        resumer: dict[str, str | None] = {"Resumed by": self.agents.get(marker.pane_id, "claude")}
        return super().consume(marker, resumer | (changes or {}))


class MarkedHarness(ReceiverHarness):
    """The Step 4 harness with ``review-resume``'s marked override.

    When the claim reports a role conflict for the marker's role, the valid
    marker authorizes ``--override`` for this attempt only (``review-resume``,
    "Continue a marked review role"), as a switched pair needs; any other
    refusal stops the sequence.
    """

    def _write(  # noqa: PLR0913 - one protected write with its full binding, as the base harness takes it
        self, step: Step, marker: Marker, host: Host, role: ReviewRole | None, carried: CarriedIdentity | None, outcome: SequenceOutcome,
    ) -> bool:
        """Claim once, then with the marker's override on a role conflict; other steps write as the base harness does."""
        if step is not Step.CLAIM or role is None:
            return super()._write(step, marker, host, role, carried, outcome)
        verifier = marked_claim_verifier(self.receiver.root, marker.render(), role, host, carried)
        for override in (False, True):
            try:
                capability = claim_selected(self.receiver.core, role, NATURES[host], round_number=1, occurrence=1, override=override, marked=verifier)
            except ReviewExchangeError as error:
                if override or "Override" not in str(error):
                    outcome.stopped_at, outcome.reason = step, str(error)
                    return False
                continue
            outcome.generation = capability.generation
            return True
        return False  # pragma: no cover - the loop always returns


@dataclass
class ReceiverAgent:
    """A pane's receiving workflow: the Step 4 harness over the real validator, receipt, journal and claim."""

    checkout: ReceiverCheckout
    tuios: FakeTuios
    journal: Path
    host: Host
    before: Callable[[Step], None] | None = None
    outcomes: list[SequenceOutcome] = field(default_factory=list[SequenceOutcome])

    def __call__(self, command: str) -> None:
        """Run the marked receiving sequence of the role the marker selects."""
        marker = marker_in_command(command)
        validator = ReceiverValidator(TuiosDiscovery(self.tuios), {self.host: WorldProver(self.tuios)}, self.checkout.clock.now)
        harness = MarkedHarness(self.checkout, validator, self.journal)
        role = _REVIEW_ROLES.get(marker.role)
        if "review-resume" in command.split(MARKER_FLAG, 1)[0]:
            steps: tuple[Step, ...] = (Step.CLAIM,)
        else:
            steps = (Step.RECEIPT, Step.JOURNAL) if role is None else (Step.RECEIPT, Step.JOURNAL, Step.CLAIM)
        outcome = harness.run(marker, self.host, role, steps=steps, before=self.before)
        self.outcomes.append(outcome)
        if outcome.stopped_at is not None:
            self.tuios.panes[marker.pane_id].results.append(ResultLine(marker.launch_id, "failed").render())


@dataclass
class WorldResults:
    """``ResultSource`` over the compact result lines each fake pane's receiving agent printed."""

    tuios: FakeTuios

    def results(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Return the pane's printed result lines."""
        del timeout
        live = self.tuios.panes.get(pane.pane_id)
        return () if live is None else tuple(live.results)


def single_agent(pane_id: str = REQUESTOR_PANE, label: str = "requestor | pane") -> Callable[[dict[str, object]], None]:
    """Return the routing change of a single-agent Codex implementation pause of one pane."""

    def change(mapping: dict[str, object]) -> None:
        """Route only the resumed implementation agent; no pair and no exchange apply."""
        part(mapping, "pause")["session_role"] = "implementation"
        targets = part(mapping, "targets")
        part(targets, "resumed").update(role="implementation", host="codex", pane_id=pane_id, label=label)
        absent = {"not_applicable": "single agent"}
        targets.update(requestor=absent, reviewer=dict(absent))
        mapping["exchange"] = dict(absent)

    return change


def record(pane_id: str, host: Host | None, root: Path, *, name: str | None = None, session: str = SESSION) -> PaneRecord:
    """Declare one live TUIOS record in the checkout; ``None`` declares a plain shell pane."""
    harness, apps = {Host.CLAUDE: ("claude-code", ()), Host.CODEX: ("", ("codex",)), None: ("", ())}[host]
    label = name if name is not None else {REQUESTOR_PANE: "requestor | pane", REVIEWER_PANE: "reviewer | pane"}.get(pane_id, "shell")
    return PaneRecord(pane_id, session, label, str(root), harness, apps, None)


class Scenario:
    """One temporary checkout with a prepared exchange, its routed pause, live fake panes and the composed command."""

    def __init__(self, tmp_path: Path, phase: str = "request") -> None:
        """Prepare the checkout, a Codex requestor pane and a Claude reviewer pane, both idle and receiving."""
        self.tmp_path = tmp_path
        self.checkout = HostedCheckout(tmp_path, phase)
        self.root = self.checkout.root
        self.clock = ScenarioClock(T0)
        self.tuios = FakeTuios(self.clock)
        self.clock.after_sleep = self.tuios.flush
        self.history = WorldHistory(self.tuios)
        self.profiles = HostProfiles()
        self.probe: dict[str, ScreenVerdict] = {REVIEWER_PANE: ScreenVerdict.IDLE_EMPTY}
        self.absence = FakeAbsence()
        self.screens = FakeScreens()
        self.environ: dict[str, str] = {}
        self.ancestry: tuple[str, ...] | None = ("cmd.exe", "WindowsTerminal.exe")
        self.guard = CheckoutGuard(temp_dir=lambda: str(tmp_path / "temp"))
        self.journal = tmp_path / "sessions.journal.md"
        self.sessions = JournalIndex()
        self.requestor = self.pane(REQUESTOR_PANE, Host.CODEX, screen=EMPTY)
        self.reviewer = self.pane(REVIEWER_PANE, Host.CLAUDE, screen=("Claude Code", "> "))

    def pane(self, pane_id: str, host: Host | None, *, screen: tuple[str, ...] | None = (), name: str | None = None) -> FakePane:
        """Add one live pane of the checkout whose agent runs the receiving workflow of its host."""
        agent = None if host is None else ReceiverAgent(self.checkout, self.tuios, self.journal, host)
        if host is not None:
            self.checkout.agents[pane_id] = AGENT_IDS[host]
        return self.tuios.add(FakePane(record(pane_id, host, self.root, name=name), screen=screen, agent=agent))

    def agent(self, pane: FakePane) -> ReceiverAgent:
        """Return the receiving agent of one pane."""
        assert isinstance(pane.agent, ReceiverAgent)
        return pane.agent

    def declare_takeover(self, *, switched: bool = False) -> None:
        """Declare the state an earlier launch left: the requestor's marked receipt, journal entry and claim.

        The requestor pane, the saved reviewer pane when ``switched``, holds
        the marked command an earlier launch typed, and its receiving agent
        wrote what it writes; the counterpart got nothing.
        """
        if switched:
            self._receive(self.reviewer, f"/resume-session {MARKER_FLAG}", SessionRole.REQUESTOR, 1)
            assert self.marked_claim() == (REVIEWER_PANE, "claude", 2)
            return
        self._receive(self.requestor, f"$llm-shared:resume-session {MARKER_FLAG}", SessionRole.REQUESTOR, 1)
        assert self.marked_claim() == (REQUESTOR_PANE, "codex", 2)

    def declare_reviewer(self) -> None:
        """Declare an earlier activation: after the takeover, the reviewer's marked review-resume and its claim."""
        self.declare_takeover()
        self._receive(self.reviewer, f"/review-resume {MARKER_FLAG}", SessionRole.REVIEWER, 2)
        assert self.marked_claim() == (REVIEWER_PANE, "claude", 3)

    def _receive(self, pane: FakePane, prefix: str, role: SessionRole, launch: int) -> None:
        """Type one marked command an earlier launch delivered, with its launch number, and let the pane's agent receive it."""
        marker = self.checkout.marker(pane.record.pane_id, role, f"{launch:032x}")
        command = f"{prefix} {marker.render()}"
        pane.typed.append((command, self.clock.now()))
        if pane.log is not None and pane.host is Host.CLAUDE:
            pane.log.append(LogEvent(LogKind.PROMPT, self.clock.now(), command))
        self.agent(pane)(command)

    def single(self) -> None:
        """Replace the paired pause with a single-agent Codex implementation pause of the requestor pane."""
        self.checkout.publish(scenario_routing(self.root, single_agent()), role="implementation")

    def other_checkout(self, name: str, pane_id: str = THIRD_PANE, *, home: str = ".reviews") -> Path:
        """Add another checkout, named by its folder, holding a single-agent pause of its own Codex pane, with no receiving agent."""
        root = self.tmp_path / f"{name}-checkout"
        (root / home).mkdir(parents=True)
        (root / home / ".gitignore").write_bytes(b"*\n")
        if home != ".reviews":
            (root / ".review-artifacts.ini").write_text(f"[review-artifacts]\nhome = {home}\n", encoding="utf-8")
        label = f"{name} | pane"
        routing = scenario_routing(root, single_agent(pane_id, label))
        section = "\n".join(render_routing_section(routing)) + "\n"
        (root / home / PROMPT_NAME).write_text(prompt_text(root, section, role="implementation"), encoding="utf-8")
        self.tuios.add(FakePane(record(pane_id, Host.CODEX, root, name=label), screen=EMPTY))
        return root

    def runtime(self) -> cli.Runtime:
        """Compose the production runtime over the fake TUIOS and the declared host adapters."""
        ids = (f"{number:032x}" for number in count(1))
        probe = _Probe(self.probe)
        hosts = cli.HostAdapters(
            self.history, probe, WorldLog(self.tuios), self.profiles, {Host.CLAUDE: self._prover, Host.CODEX: self._prover},
            self.absence, self.screens, WorldResults(self.tuios),
        )
        return cli.Runtime(
            self.environ, lambda: self.ancestry, self.tuios.runner_for, self.clock, self.clock, self.guard, hosts,
            _read_snapshot, self._sessions, cli.SavedExchanges(self.checkout.clock.now), lambda: next(ids),
        )

    def _sessions(self) -> JournalIndex:
        """Read the private session journal index as it stands now; a test may replace it between reads."""
        return self.sessions

    def _prover(self, remaining: Remaining) -> InputProver:
        """Build one proof's prover; the fake reads no budget-bound file."""
        del remaining
        return WorldProver(self.tuios)

    def run(self, *argv: str) -> tuple[int, list[str]]:
        """Run the command once in process; return its exit code and output lines."""
        out, err = io.StringIO(), io.StringIO()
        code = cli.main(list(argv), stdout=out, stderr=err, runtime=self.runtime)
        assert err.getvalue() == ""
        return code, out.getvalue().splitlines()

    def evidence(self) -> dict[str, bytes]:
        """Return the prompt, receipt and exchange bytes a no-input run must leave unchanged."""
        return self.checkout.evidence()

    def marked_claim(self) -> tuple[str, str, int] | None:
        """Return the current marked claim's pane, host and issued generation, ``None`` without one."""
        coordination = self.checkout.store.read_coordination(required=True)
        assert coordination is not None
        claim = coordination.marked_claim
        return None if claim is None else (claim.evidence.pane_id, claim.evidence.host, claim.issued_generation)


@dataclass
class _Probe:
    """``ScreenProbe`` returning the declared Codex verdict per pane."""

    verdicts: dict[str, ScreenVerdict]

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the declared verdict, unsupported by default."""
        return self.verdicts.get(pane.pane_id, ScreenVerdict.UNSUPPORTED)


def _read_snapshot(root: CanonicalRoot) -> CheckoutSnapshot:
    """Read one checkout's saved pause with the production reader."""
    return read_checkout_snapshot(Path(root.display))


__all__ = [
    "AGENT_IDS",
    "CLEARED",
    "IDLE",
    "REQUESTOR_PANE",
    "REVIEWER_PANE",
    "SESSION",
    "T0",
    "THIRD_PANE",
    "WORKING",
    "FakePane",
    "FakeTuios",
    "HostedCheckout",
    "MarkedHarness",
    "ReceiverAgent",
    "Scenario",
    "record",
    "single_agent",
]


# eof
