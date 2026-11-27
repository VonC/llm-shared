"""Typed vocabulary and ports of the guarded bulk delivery.

Step 6 of v0.15.0 resume-paused separates the values and injected ports of
delivery from the state machine that uses them
(``tools.resume_paused_delivery``), so Step 7's takeover observation and
Step 8's composition and reporting share one model:

- ``Phase``: the send a pre-send check guards: clear, resume, reviewer
  command or the single Codex recovery Enter;
- ``Refusal``: why one send must not happen, an expected skip or a
  classification failure; ``PreSendCheck`` returns one, or ``None``, for each
  ``SendStep`` immediately before the send, under the held checkout guard;
- ``DeliveryProfile`` and ``InputScreen``: the pinned delivery signatures of
  one pane, its new-conversation command, background-shell line and, for
  Codex, its input-box signatures. ``ProfileGate`` selects them per pane;
  ``UnpinnedProfiles`` answers while no host is pinned (plan Q05), so every
  real pane stays unsupported and receives no input;
- ``AgentLog``: a Claude pane's prompt and clear events;
- ``GuardState``, ``ActionReport`` and ``CheckoutDelivery``: the guard state
  of each delivered checkout and one outcome per planned action. The OS guard
  adapter (``tools.resume_paused_guard``) uses this vocabulary; the model
  never imports the adapter at run time;
- ``PaneTransport``: the transport port, whose ``select`` keeps the TUIOS
  selector syntax in the adapter and whose blocking calls take the remaining
  budget of the send in progress as their bound (code review round 1);
- ``Takeover`` and ``PairDelivery``: the seam through which Step 7 decides
  each conditional reviewer under the same held guard; ``NoTakeover`` keeps
  every conditional reviewer pending until Step 7 exists.

Fix (Step 7): after its acceptance, every resume goes through
``Takeover.received``, which observes that receiver under its own 120-second
bound and records what it saw in ``ActionReport.receiver`` and
``ActionReport.generation`` (``ReceiverState``). ``PairDelivery.root`` names
the checkout the takeover reads, so the takeover's own durable reads need no
other argument.

Fix (Step 7 code review round 1): ``PairDelivery.digest`` names the saved
prompt the checkout's plan accepted, which the takeover's observation binds.
``CLAUDE_WAIT_SCOPE`` lives here so the worker's own report of a Claude
reviewer whose requestor was not accepted carries it too.

The module holds values and protocols only: no IO and no input.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import StrEnum
from typing import TYPE_CHECKING, Final, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from datetime import datetime

    from tools.resume_paused_dispatch import SharedDelivery
    from tools.resume_paused_evidence import PaneObservation, ScreenProbe
    from tools.resume_paused_guard import GuardLease
    from tools.resume_paused_input import InputProver, PaneRecord
    from tools.resume_paused_models import CanonicalRoot, PromptDigest
    from tools.resume_paused_plan_model import PlannedAction
    from tools.resume_paused_profiles import Clock, Host
    from tools.resume_paused_transport import AskOutcome, Selection

ACTION_BUDGET: Final = timedelta(seconds=100)
CALL_BOUND_SECONDS: Final = 30.0
CLAUDE_WAIT_SCOPE: Final = "limits=claude-wait-scope"


class GuardState(StrEnum):
    """Result of one checkout guard acquisition: only ``ACQUIRED`` permits input to the checkout."""

    ACQUIRED = "acquired"
    HELD = "held"
    UNAVAILABLE = "unavailable"


class Phase(StrEnum):
    """The send that a pre-send check guards."""

    CLEAR = "clear"
    RESUME = "resume"
    REVIEWER = "reviewer"
    RECOVERY = "recovery"


class DeliveryOutcome(StrEnum):
    """Outcome of one planned action; only ``UNCONFIRMED`` means input may have been typed unproved."""

    ACCEPTED = "accepted"
    REFUSED = "refused"
    UNCONFIRMED = "unconfirmed"
    PENDING = "pending"


class ClearOutcome(StrEnum):
    """What happened to the clear of one action; ``NONE`` when no clear was sent."""

    NONE = "none"
    REDUNDANT = "redundant"
    CONFIRMED = "confirmed"
    UNCONFIRMED = "unconfirmed"


class ReceiverState(StrEnum):
    """What the post-acceptance observation of one receiver saw (Step 7).

    ``CLAIMED`` means durable records prove this launch's current marked
    claim, ``CONSUMED`` that its schema 3 receipt consumed the prompt, and
    ``COMPLETION_UNCONFIRMED`` that the bound passed with neither, which is
    still a success; only ``FAILED`` fails the action.
    """

    UNOBSERVED = "unobserved"
    CONSUMED = "consumed"
    CLAIMED = "claimed"
    COMPLETION_UNCONFIRMED = "completion-unconfirmed"
    FAILED = "failed"


@dataclass(frozen=True)
class Refusal:
    """Why one send must not happen; ``failed`` marks a classification failure, otherwise an expected skip."""

    reason: str
    failed: bool = False


@dataclass(frozen=True)
class ActionReport:
    """The outcome of one planned action, with its clear, any recovery Enter and report-only notes.

    ``receiver`` and ``generation`` record the Step 7 observation of an
    accepted receiver: its state and, once claimed, the claim's ownership
    generation (non-secret).
    """

    action: PlannedAction
    outcome: DeliveryOutcome
    reason: str = ""
    failed: bool = False
    clear: ClearOutcome = ClearOutcome.NONE
    recovery: tuple[Phase, ...] = ()
    notes: tuple[str, ...] = ()
    receiver: ReceiverState = ReceiverState.UNOBSERVED
    generation: int | None = None


@dataclass(frozen=True)
class CheckoutDelivery:
    """The guard state of one delivered checkout and the report of each of its planned actions."""

    root: CanonicalRoot
    guard: GuardState
    reports: tuple[ActionReport, ...] = ()

    @property
    def failed(self) -> bool:
        """Return whether the checkout failed: an unavailable guard or a failed action."""
        return self.guard is GuardState.UNAVAILABLE or any(report.failed for report in self.reports)


@dataclass(frozen=True)
class SendStep:
    """One imminent send: its phase, checkout, planned action, fresh observation and fresh target record."""

    phase: Phase
    root: CanonicalRoot
    action: PlannedAction
    observation: PaneObservation
    pane: PaneRecord


class PreSendCheck(Protocol):
    """One injected check run immediately before each send, under the held checkout guard."""

    def check(self, step: SendStep) -> Refusal | None:
        """Return why the send must not happen, or ``None`` to permit it."""
        ...


@dataclass(frozen=True)
class InputScreen:
    """Pinned Codex screen signatures: input-line prefix, empty-input placeholder, working, cleared and footer lines.

    ``working_pattern``, ``cleared_pattern`` and each of ``footer_lines`` are
    regular expressions that must match a whole captured line. The lines
    below the input line must be exactly the pinned footer layout, one line
    per ``footer_lines`` entry in that order (code review rounds 1 and 2), so
    the input box holds exactly one line and a missing, repeated or extra
    footer line is unrecognized; with no entry, no line may follow it.
    """

    input_prefix: str
    placeholder: str
    working_pattern: str
    cleared_pattern: str
    footer_lines: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeliveryProfile:
    """The pinned delivery signatures of one pane's host version.

    ``background_pattern`` matches a whole captured line reporting background
    shells, empty when the profile has none; ``screen`` is required for Codex.
    """

    host: Host
    clear_command: str
    background_pattern: str = ""
    screen: InputScreen | None = None


class ProfileGate(Protocol):
    """Injected selection of a pane's pinned delivery profile from pane-tied version evidence."""

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Return the pane's supported profile, ``None`` when its version is not pinned."""
        ...


class UnpinnedProfiles:
    """``ProfileGate`` while no host profile is pinned (plan Q05): every pane is unsupported."""

    def profile(self, pane: PaneRecord) -> DeliveryProfile | None:
        """Report the pane unsupported."""
        del pane


class LogKind(StrEnum):
    """Claude agent-log events the delivery reads."""

    PROMPT = "prompt"
    CLEAR = "clear"


@dataclass(frozen=True)
class LogEvent:
    """One agent-log event: a prompt in the profile's logged form, or a session started by a clear."""

    kind: LogKind
    at: datetime
    text: str = ""


class AgentLog(Protocol):
    """Injected agent log of one Claude pane."""

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Return the pane's prompt and clear events, oldest first, or ``None`` when unreadable."""
        ...


class Sleeper(Protocol):
    """Injected wait; tests advance a fake clock instead of sleeping."""

    def sleep(self, seconds: float) -> None:
        """Wait for the given number of seconds."""
        ...


class PaneTransport(Protocol):
    """Injected pane transport: fresh discovery, exact selection, captures, the ask and the recovery Enter.

    Every blocking call takes ``timeout``, the seconds its caller grants: the
    remaining budget of the send in progress, or ``CALL_BOUND_SECONDS``
    before a send starts.
    """

    def observe(self, timeout: float) -> PaneObservation | None:
        """List every live pane and its activity, or ``None`` when discovery failed."""
        ...

    def select(self, panes: Sequence[PaneRecord], target: PaneRecord) -> Selection:
        """Return the transport selector that reaches only the target among the listed panes, or why none does."""
        ...

    def capture(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Capture the pane's unwrapped lines, or ``None`` on failure."""
        ...

    def ask(self, selector: str, command: str, timeout: float, pane_id: str = "") -> AskOutcome:
        """Type one command through the resolved selector."""
        ...

    def enter(self, session: str, pane_id: str, timeout: float) -> bool:
        """Press Enter once in the pane with this full UUID."""
        ...


class GuardPort(Protocol):
    """Injected nonblocking per-checkout guard."""

    def acquire(self, root: CanonicalRoot) -> GuardLease:
        """Take the checkout's guard, or report it held or unavailable."""
        ...


class PairDelivery(Protocol):
    """What Step 7 may do under the held guard: deliver one more planned action with extra checks."""

    @property
    def root(self) -> CanonicalRoot:
        """Return the checkout whose guard is held."""
        ...

    @property
    def digest(self) -> PromptDigest | None:
        """Return the digest of the saved prompt the checkout's plan accepted, ``None`` when none was read."""
        ...

    def deliver(self, action: PlannedAction, phase: Phase, checks: tuple[PreSendCheck, ...] = ()) -> ActionReport:
        """Deliver one planned action, running the extra checks before each of its sends."""
        ...


class Takeover(Protocol):
    """Step 7: observe each accepted receiver and decide each conditional reviewer."""

    def received(self, pair: PairDelivery, report: ActionReport) -> ActionReport:
        """Return the resume's report with its post-acceptance observation; other reports stay unchanged."""
        ...

    def reviewer(self, pair: PairDelivery, resumed: ActionReport | None, action: PlannedAction) -> ActionReport:
        """Return the conditional reviewer's outcome; ``resumed`` is ``None`` for a later continuation."""
        ...


class NoTakeover:
    """``Takeover`` without Step 7 composition: no receiver is observed and every conditional reviewer stays pending."""

    def received(self, pair: PairDelivery, report: ActionReport) -> ActionReport:
        """Return the report unobserved."""
        del pair
        return report

    def reviewer(self, pair: PairDelivery, resumed: ActionReport | None, action: PlannedAction) -> ActionReport:
        """Report the reviewer pending; no takeover is observed."""
        del pair, resumed
        return ActionReport(action, DeliveryOutcome.PENDING, "takeover-unobserved")


type Remaining = Callable[[], float]
"""Return the seconds left in the send in progress at the moment of the call; zero or less once spent."""

type ProverFactory = Callable[[Remaining], InputProver]
"""Build one host's input prover whose nested reads ask ``Remaining`` before each of them."""


@dataclass(frozen=True)
class DeliveryPorts:
    """Every injected dependency of one delivery run.

    ``provers`` holds one ``ProverFactory`` per host (code review round 2):
    each acceptance proof gets a prover built for its send. Since round 3 the
    factory receives a ``Remaining`` callable rather than a figure, so each
    nested read of the proof (``tools.resume_paused_budget``) is bounded by
    the time left when it starts, and none starts once the budget is spent.
    """

    transport: PaneTransport
    guard: GuardPort
    clock: Clock
    sleeper: Sleeper
    profiles: ProfileGate
    log: AgentLog
    provers: Mapping[Host, ProverFactory]
    probe: ScreenProbe
    checks: tuple[PreSendCheck, ...] = ()
    takeover: Takeover = field(default_factory=NoTakeover)
    shared: SharedDelivery | None = None


__all__ = [
    "ACTION_BUDGET",
    "CALL_BOUND_SECONDS",
    "CLAUDE_WAIT_SCOPE",
    "ActionReport",
    "AgentLog",
    "CheckoutDelivery",
    "ClearOutcome",
    "DeliveryOutcome",
    "DeliveryPorts",
    "DeliveryProfile",
    "GuardPort",
    "GuardState",
    "InputScreen",
    "LogEvent",
    "LogKind",
    "NoTakeover",
    "PairDelivery",
    "PaneTransport",
    "Phase",
    "PreSendCheck",
    "ProfileGate",
    "ProverFactory",
    "ReceiverState",
    "Refusal",
    "Remaining",
    "SendStep",
    "Sleeper",
    "Takeover",
    "UnpinnedProfiles",
]


# eof
