"""Declared world of the guarded delivery tests of resume-paused.

Code review round 1: the transport records the bound granted to every call,
captures and proofs can spend declared time, and Codex screens carry the
pinned footer line below the input box. Round 2: provers are handed out by
per-host factories, and a test may declare its own factory, such as one
building the concrete Codex prover. Round 3: a factory receives the send's
remaining-time callable; the default ones record the time left at each proof.

Step 6 of v0.15.0 resume-paused: a fake clock that only moves when the
delivery waits or a declared transport effect spends time, a transport whose
listings and captures are declared in order (the last one repeats), a
declared agent log, input provers, profiles and guard. ``World.deliver`` runs
the real ``deliver_run`` over a declared plan; no process, pane or real wait
is involved.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_delivery import deliver_run
from tools.resume_paused_delivery_model import (
    DeliveryPorts,
    DeliveryProfile,
    GuardState,
    InputScreen,
    LogEvent,
    LogKind,
    NoTakeover,
    ProverFactory,
)
from tools.resume_paused_evidence import PaneActivity, PaneObservation, ScreenVerdict
from tools.resume_paused_guard import GuardLease
from tools.resume_paused_input import InputEvidence, PaneRecord
from tools.resume_paused_models import CanonicalRoot, SessionRole
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    CheckoutPlan,
    PlannedAction,
    PlanRequest,
    RunPlan,
    SkipReason,
)
from tools.resume_paused_profiles import CallerDecision, CallerOrigin, Host, ReadAccount
from tools.resume_paused_transport import AskOutcome, resolve_selector

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.resume_paused_delivery_model import (
        CheckoutDelivery,
        PreSendCheck,
        Remaining,
        Takeover,
    )
    from tools.resume_paused_input import CarriedIdentity, InputProver
    from tools.resume_paused_transport import Selection

T0 = datetime(2026, 11, 20, 12, 0, tzinfo=UTC)
PAUSED = "2026-11-20T11:00:00+00:00"
PAUSED_AT = datetime(2026, 11, 20, 11, 0, tzinfo=UTC)
SESSION = "llm-shared_resume-paused"
API = CanonicalRoot.parse("C:\\work\\api")
WEB = CanonicalRoot.parse("C:\\work\\web")
CLAUDE_PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
CODEX_PANE = "2fd92f30-1111-4222-8333-444455556666"
WEB_PANE = "5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3"
CLAUDE_COMMAND = f"/resume-session --resume-paused 01.rp1.{CLAUDE_PANE}.requestor.b1"
CODEX_COMMAND = f"$llm-shared:review-resume --resume-paused 02.rp1.{CODEX_PANE}.reviewer.b2"
IDLE = PaneActivity("idle", "", draft_held=False, question="", ready=True)
HUMAN = PlanRequest(CallerDecision(CallerOrigin.UNPROVED, ()))
PROMPT = "\N{SINGLE RIGHT-POINTING ANGLE QUOTATION MARK} "
PLACEHOLDER = "Ask Codex to do anything"
FOOTER = "  ? for shortcuts"
SCREEN = InputScreen(PROMPT, PLACEHOLDER, r"• Working.*", r"New conversation started\.", (r"  \? for shortcuts",))
CLAUDE_PROFILE = DeliveryProfile(Host.CLAUDE, "/clear", r"\d+ shells? running")
CODEX_PROFILE = DeliveryProfile(Host.CODEX, "/new", r"\d+ background terminals? running", SCREEN)
EMPTY = ("OpenAI Codex", PROMPT + PLACEHOLDER, FOOTER)


def typed(command: str) -> tuple[str, ...]:
    """Return a Codex capture holding the command unsubmitted as its whole input box."""
    return ("OpenAI Codex", PROMPT + command, FOOTER)


def submitted(command: str) -> tuple[str, ...]:
    """Return a Codex capture showing the command submitted and working."""
    return ("OpenAI Codex", PROMPT + command, "• Working (3s)", PROMPT + PLACEHOLDER, FOOTER)


def record(pane: str = CLAUDE_PANE, root: CanonicalRoot = API, *, name: str | None = None, session: str = SESSION) -> PaneRecord:
    """Declare one live agent record of the declared host."""
    codex = pane == CODEX_PANE
    label = name if name is not None else ("Codex api" if codex else "Claude api")
    return PaneRecord(pane, session, label, root.display, "" if codex else "claude-code", ("codex",) if codex else (), None)


def action(  # noqa: PLR0913 - one declared field of the planned action per argument
    pane: str = CLAUDE_PANE, command: str | None = CLAUDE_COMMAND, *, kind: ActionKind = ActionKind.RESUME,
    clear: bool = False, conditional: bool | None = None, skip: SkipReason | None = None,
) -> PlannedAction:
    """Declare one planned action; the host follows the pane, the role follows the kind."""
    host = Host.CODEX if pane == CODEX_PANE else Host.CLAUDE
    role = SessionRole.REQUESTOR if kind is ActionKind.RESUME else SessionRole.REVIEWER
    label = "Codex api" if host is Host.CODEX else "Claude api"
    conditional = kind is not ActionKind.RESUME if conditional is None else conditional
    return PlannedAction(kind, role, host, SESSION, pane, label, command, clear=clear, conditional=conditional, skip=skip)


def checkout(*actions: PlannedAction, root: CanonicalRoot = API, paused_at: str | None = PAUSED) -> CheckoutPlan:
    """Declare one planned checkout."""
    return CheckoutPlan(root, PromptState.UNUSED, CheckoutOutcome.PLANNED, paused_at=paused_at, actions=actions)


@dataclass
class FakeClock:
    """A clock that moves only when the delivery waits or a declared effect spends time."""

    current: datetime = T0
    sleeps: list[float] = field(default_factory=list[float])

    def now(self) -> datetime:
        """Return the declared instant."""
        return self.current

    def sleep(self, seconds: float) -> None:
        """Record the wait and advance the clock."""
        self.sleeps.append(seconds)
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        """Spend time, as a slow transport call does."""
        self.current += timedelta(seconds=seconds)


@dataclass
class FakeTransport:
    """Declared listings and captures, consumed in order (the last one repeats), recording every call."""

    observations: list[PaneObservation | None]
    captures: dict[str, list[tuple[str, ...] | None]] = field(default_factory=dict[str, list[tuple[str, ...] | None]])
    exit_code: int = 0
    entered: bool = True
    on_ask: Callable[[str], None] | None = None
    on_enter: Callable[[], None] | None = None
    on_capture: Callable[[int], None] | None = None
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])
    bounds: list[tuple[str, float]] = field(default_factory=list[tuple[str, float]])

    @staticmethod
    def _next[T](items: list[T]) -> T:
        """Return the next declared item; the last one repeats."""
        return items.pop(0) if len(items) > 1 else items[0]

    def observe(self, timeout: float) -> PaneObservation | None:
        """Return the next declared listing."""
        self.calls.append(("observe",))
        self.bounds.append(("observe", timeout))
        return self._next(self.observations)

    @staticmethod
    def select(panes: Sequence[PaneRecord], target: PaneRecord) -> Selection:
        """Resolve the selector with the real TUIOS selector rule."""
        return resolve_selector(panes, target)

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Return the pane's next declared capture, none by default, after its declared effect."""
        self.calls.append(("capture", pane.pane_id))
        self.bounds.append(("capture", timeout))
        if self.on_capture is not None:
            self.on_capture(sum(1 for call in self.calls if call[0] == "capture"))
        return self._next(self.captures.get(pane.pane_id, [None]))

    def ask(self, selector: str, command: str, timeout: float, pane_id: str = "") -> AskOutcome:
        """Record the ask and run its declared effect."""
        del pane_id
        self.calls.append(("ask", selector, command))
        self.bounds.append(("ask", timeout))
        if self.on_ask is not None:
            self.on_ask(command)
        return AskOutcome(self.exit_code)

    def enter(self, session: str, pane_id: str, timeout: float) -> bool:
        """Record the Enter and run its declared effect."""
        self.calls.append(("enter", session, pane_id))
        self.bounds.append(("enter", timeout))
        if self.on_enter is not None:
            self.on_enter()
        return self.entered

    def sent(self) -> list[tuple[str, ...]]:
        """Return every input call: asks and Enters."""
        return [call for call in self.calls if call[0] in {"ask", "enter"}]


@dataclass
class FakeLog:
    """Declared agent-log events per pane; ``None`` models an unreadable log."""

    events: dict[str, list[LogEvent] | None] = field(default_factory=dict[str, list[LogEvent] | None])

    def read(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Return the pane's declared events."""
        declared = self.events.get(pane.pane_id, [])
        return None if declared is None else tuple(declared)

    def add(self, pane: str, kind: LogKind, at: datetime, text: str = "") -> None:
        """Append one event to the pane's log."""
        events = self.events.setdefault(pane, [])
        assert events is not None
        events.append(LogEvent(kind, at, text))


@dataclass
class LogPort:
    """``AgentLog`` over the declared log."""

    log: FakeLog

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Return the pane's declared events."""
        return self.log.read(pane)


@dataclass
class FakeProver:
    """Declared proofs: the commands proved as each pane's latest input, recording each proof's lower bound."""

    proved: set[tuple[str, str]] = field(default_factory=set[tuple[str, str]])
    bounds: list[datetime] = field(default_factory=list[datetime])
    on_prove: Callable[[], None] | None = None

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Prove the command when declared, after the declared effect (a slow read spends time)."""
        assert carried is None
        self.bounds.append(not_before)
        if self.on_prove is not None:
            self.on_prove()
        proved = (pane.pane_id, command) in self.proved
        return InputEvidence(proved=proved, session_id=None, reasons=() if proved else ("marked-input-not-latest",), account=ReadAccount())


@dataclass
class FakeProfiles:
    """Declared delivery profiles per pane, in order (the last one repeats)."""

    by_pane: dict[str, list[DeliveryProfile | None]] = field(
        default_factory=lambda: {CLAUDE_PANE: [CLAUDE_PROFILE], CODEX_PANE: [CODEX_PROFILE], WEB_PANE: [CLAUDE_PROFILE]},
    )

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Return the pane's next declared profile."""
        declared = self.by_pane.get(pane.pane_id, [None])
        return declared.pop(0) if len(declared) > 1 else declared[0]


@dataclass
class FakeProbe:
    """No Codex capture supports a stale working override unless declared."""

    verdict: ScreenVerdict = ScreenVerdict.UNSUPPORTED

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the declared verdict."""
        del pane
        return self.verdict


@dataclass
class FakeGuard:
    """Declared guard states per checkout, recording acquisitions and releases, with optional hooks."""

    states: dict[str, GuardState] = field(default_factory=dict[str, GuardState])
    on_acquire: dict[str, Callable[[], None]] = field(default_factory=dict[str, Callable[[], None]])
    on_release: dict[str, Callable[[], None]] = field(default_factory=dict[str, Callable[[], None]])
    events: list[str] = field(default_factory=list[str])

    def acquire(self, root: CanonicalRoot) -> GuardLease:
        """Return a declared lease whose release is recorded."""
        hook = self.on_acquire.get(root.key)
        if hook is not None:
            hook()
        state = self.states.get(root.key, GuardState.ACQUIRED)
        self.events.append(f"acquire {root.key} {state.value}")
        if state is not GuardState.ACQUIRED:
            return GuardLease(state, Path(root.display))
        return GuardLease(state, Path(root.display), _RecordingLock(self, root.key), 1)


@dataclass
class _RecordingLock:
    """Lock primitive that records the release of one declared lease."""

    guard: FakeGuard
    key: str

    def open(self, path: Path) -> int | None:
        """Never used: the lease is declared already open."""
        del path
        return None

    def try_lock(self, descriptor: int) -> GuardState:
        """Never used: the lease is declared already locked."""
        del descriptor
        return GuardState.HELD

    def unlock(self, descriptor: int) -> None:
        """Record the release and run its hook."""
        del descriptor
        self.guard.events.append(f"release {self.key}")
        hook = self.guard.on_release.get(self.key)
        if hook is not None:
            hook()

    def close(self, descriptor: int) -> None:
        """Nothing to close."""
        del descriptor


@dataclass
class World:
    """Every declared port of one delivery run."""

    transport: FakeTransport = field(default_factory=lambda: FakeTransport([PaneObservation((record(),), {CLAUDE_PANE: IDLE})]))
    clock: FakeClock = field(default_factory=FakeClock)
    log: FakeLog = field(default_factory=FakeLog)
    claude: FakeProver = field(default_factory=FakeProver)
    codex: FakeProver = field(default_factory=FakeProver)
    profiles: FakeProfiles = field(default_factory=FakeProfiles)
    probe: FakeProbe = field(default_factory=FakeProbe)
    guard: FakeGuard = field(default_factory=FakeGuard)
    checks: tuple[PreSendCheck, ...] = ()
    takeover: Takeover = field(default_factory=NoTakeover)
    factories: dict[Host, ProverFactory] = field(default_factory=dict[Host, ProverFactory])
    prover_bounds: list[tuple[Host, float]] = field(default_factory=list[tuple[Host, float]])

    def _factory(self, host: Host, prover: FakeProver) -> ProverFactory:
        """Return a factory handing out the declared prover, recording the time left when each proof starts."""

        def build(remaining: Remaining) -> InputProver:
            self.prover_bounds.append((host, remaining()))
            return prover

        return build

    def ports(self) -> DeliveryPorts:
        """Bundle the declared ports; declared factories replace the default provers."""
        provers = {Host.CLAUDE: self._factory(Host.CLAUDE, self.claude), Host.CODEX: self._factory(Host.CODEX, self.codex)}
        provers |= self.factories
        return DeliveryPorts(
            self.transport, self.guard, self.clock, self.clock, self.profiles, LogPort(self.log), provers, self.probe,
            self.checks, self.takeover,
        )

    def deliver(self, *checkouts: CheckoutPlan, request: PlanRequest = HUMAN, dry_run: bool = False) -> tuple[CheckoutDelivery, ...]:
        """Run the real delivery over the declared plan."""
        return deliver_run(RunPlan(dry_run, (), checkouts), request, self.ports())

    def accept_claude(self, command: str = CLAUDE_COMMAND, pane: str = CLAUDE_PANE) -> Callable[[str], None]:
        """Return an ask effect that makes the Claude command logged and proved when it is typed."""

        def effect(typed_command: str) -> None:
            if typed_command == command:
                self.log.add(pane, LogKind.PROMPT, self.clock.now(), command)
                self.claude.proved.add((pane, command))

        return effect


def observation(*records: PaneRecord, activity: dict[str, PaneActivity] | None = None) -> PaneObservation:
    """Return one listing; every pane is idle and ready unless declared."""
    return PaneObservation(records, activity if activity is not None else dict.fromkeys((item.pane_id for item in records), IDLE))


__all__ = [
    "API",
    "CLAUDE_COMMAND",
    "CLAUDE_PANE",
    "CLAUDE_PROFILE",
    "CODEX_COMMAND",
    "CODEX_PANE",
    "CODEX_PROFILE",
    "EMPTY",
    "FOOTER",
    "HUMAN",
    "IDLE",
    "PAUSED",
    "PAUSED_AT",
    "PLACEHOLDER",
    "PROMPT",
    "SCREEN",
    "SESSION",
    "T0",
    "WEB",
    "WEB_PANE",
    "FakeClock",
    "FakeGuard",
    "FakeLog",
    "FakeProfiles",
    "FakeProver",
    "FakeTransport",
    "LogPort",
    "World",
    "action",
    "checkout",
    "observation",
    "record",
    "submitted",
    "typed",
]


# eof
