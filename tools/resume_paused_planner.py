"""Read-only checkout planner of the human-launched bulk resume.

Step 5 of v0.15.0 resume-paused builds, from read-only evidence, the one
classified plan that a preview reports and a later delivery executes, so both
share every decision and no target is guessed. ``plan_run``:

1. refuses a recognized agent caller (design Q08, dry runs included) and a
   failed discovery before any checkout is read;
2. indexes every discovered pane once, by full pane UUID and by canonical
   checkout root (O(P + C)), excluded and caller panes included;
3. requires every ``--except`` name to equal a TUIOS session, a complete pane
   label or a checkout folder name, and every ``--switch-roles`` name a
   session or folder name, never a pane label, exactly and case-insensitively;
   any unmatched name refuses the whole run;
4. reads each discovered checkout's saved pause once through the injected
   reader and plans every prompt-bearing checkout in isolation, in root order:
   an unreadable pause or evidence fails that checkout alone; an excluded
   folder skips it; a switch that names a checkout without a saved requestor
   pair fails it; a used prompt reports its receipt and only lets the resumed
   requestor's pair continue its reviewer (a switched pair needs the switch
   again); then the pausing agent, the routing, the checkout-wide duplicate
   evidence of ``tools.resume_paused_evidence`` and the saved targets decide;
5. validates each saved target against live discovery by full pane UUID,
   TUIOS session, checkout and host (design Q10): a missing UUID, a gone saved
   session, a pane without an agent (a shell) or an unreadable checkout skips;
   a reused UUID, another session, host or checkout, or contradictory host
   evidence fails the checkout. A changed label or agent session id is a note;
6. protects the resumed target (exclusion, caller pane, blocked, question,
   draft, not ready, busy or unknown activity) and the counterpart statically (exclusion,
   caller pane, shell); the counterpart's activity is checked when it is
   activated, conditionally on takeover;
7. observes the saved exchange read-only through the injected observer and
   binds each planned command's marker to the assignment that
   ``resolve_assignment`` rebuilds, with one fresh launch id per command.

``--switch-roles`` swaps only the saved requestor and reviewer of a saved
requestor pause; it never selects another pane. A dry run plans exactly the
same checkouts and allows no input. The typed result lives in
``tools.resume_paused_plan_model``. Nothing here sends input, clears a pane,
writes a file or parses command-line arguments (Step 8); Step 6 revalidates
every action immediately before its send through ``plan_checkout``, which
replans one checkout from a fresh observation with the same checkout gates.

Fix (Step 7): ``marked_command`` renders the native marked command of one
host and action kind, so the takeover rebuilds a requestor's marked input
from its durable receipt with the planner's own spelling.

Fix (Step 7 code review round 1): each checkout plan records the digest of
the saved prompt it accepted, which the takeover's observation binds.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Final, Protocol, cast

from tools.resume_paused_artifacts import PromptState, RoutingState
from tools.resume_paused_evidence import (
    Activity,
    DuplicateEvidence,
    DuplicateSignal,
    PauseFacts,
    classify_duplicates,
    input_eligibility,
)
from tools.resume_paused_input import pane_host
from tools.resume_paused_marker import (
    MARKER_FLAG,
    LiveExchange,
    Marker,
    new_launch_id,
    resolve_assignment,
)
from tools.resume_paused_models import (
    ArtifactError,
    CanonicalRoot,
    SessionRole,
    host_for_agent,
    timestamp_instant,
)
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    CheckoutPlan,
    ErrorReason,
    GlobalFailure,
    GlobalReason,
    PlannedAction,
    RunPlan,
    SkipReason,
)
from tools.resume_paused_profiles import CallerOrigin, Host
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_routing import RoutingTarget, SavedExchange, Unresolved

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from tools.resume_paused_artifacts import (
        CheckoutSnapshot,
        PromptMetadata,
        RoutingReading,
        UsageReceipt,
    )
    from tools.resume_paused_evidence import (
        CommandHistory,
        JournalIndex,
        PaneActivity,
        PaneObservation,
        ScreenProbe,
    )
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_plan_model import PlanRequest
    from tools.resume_paused_review import ExchangeSnapshot
    from tools.resume_paused_routing import SavedRouting

_MARKED_SCHEMA: Final = 3


class ExchangeObserver(Protocol):
    """Injected read-only observation of one saved exchange of a checkout."""

    def observe(self, root: CanonicalRoot, exchange: SavedExchange) -> ExchangeSnapshot:
        """Return the validated snapshot of the saved exchange."""
        ...


@dataclass(frozen=True)
class PlannerPorts:
    """Injected readers: saved pauses, exchanges, command histories, captures, journal, launch ids."""

    read_snapshot: Callable[[CanonicalRoot], CheckoutSnapshot]
    exchanges: ExchangeObserver
    history: CommandHistory
    probe: ScreenProbe
    journal: JournalIndex
    launch_id: Callable[[], str] = new_launch_id


@dataclass(frozen=True)
class _Refusal:
    """Why one target or checkout gets no input."""

    reason: SkipReason | ErrorReason
    detail: str = ""


@dataclass(frozen=True)
class _Slot:
    """One saved target in the role this run assigns it."""

    kind: ActionKind
    role: SessionRole
    target: RoutingTarget


type _Examined = tuple[_Slot, _Refusal | None, tuple[str, ...]]

_DUPLICATE_SKIPS: Final = {
    DuplicateSignal.RECEIPT: SkipReason.ALREADY_USED,
    DuplicateSignal.JOURNAL: SkipReason.JOURNAL_RESUMED,
    DuplicateSignal.COMMAND: SkipReason.ALREADY_RESUMING,
    DuplicateSignal.OVERRIDE: SkipReason.OVERRIDE_PENDING,
}
_ACTIVITY_SKIPS: Final = {
    Activity.BUSY: SkipReason.PANE_BUSY,
    Activity.BLOCKED: SkipReason.PANE_BLOCKED,
    Activity.DRAFT: SkipReason.PANE_DRAFT,
    Activity.NOT_READY: SkipReason.PANE_NOT_READY,
    Activity.UNKNOWN: SkipReason.PANE_STATE_UNKNOWN,
}
_ROUTING_SKIPS: Final = {RoutingState.ABSENT: SkipReason.ROUTING_MISSING, RoutingState.TABLE_ONLY: SkipReason.ROUTING_TABLE_ONLY}
_EXCHANGE_REFUSALS: Final = {
    ExchangeObservationKind.NOT_LIVE: SkipReason.EXCHANGE_NOT_LIVE,
    ExchangeObservationKind.BUSY: SkipReason.EXCHANGE_BUSY,
    ExchangeObservationKind.SELECTION_CHANGED: ErrorReason.EXCHANGE_SELECTION_CHANGED,
}
_NATIVE: Final = {
    (Host.CLAUDE, ActionKind.RESUME): "/resume-session",
    (Host.CODEX, ActionKind.RESUME): "$llm-shared:resume-session",
    (Host.CLAUDE, ActionKind.REVIEWER): "/review-resume",
    (Host.CODEX, ActionKind.REVIEWER): "$llm-shared:review-resume",
    (Host.CLAUDE, ActionKind.CONTINUE_REVIEWER): "/review-resume",
    (Host.CODEX, ActionKind.CONTINUE_REVIEWER): "$llm-shared:review-resume",
}


def marked_command(host: Host, kind: ActionKind, marker: Marker) -> str:
    """Return the native command of this host and action kind followed by the rendered marker."""
    return f"{_NATIVE[host, kind]} {MARKER_FLAG} {marker.render()}"


def _root_of(pane: PaneRecord) -> CanonicalRoot | None:
    """Return the canonical checkout a pane works in, or ``None`` when its path is unusable."""
    try:
        return CanonicalRoot.parse(pane.cwd, "pane checkout")
    except ArtifactError:
        return None


def _folder(root: CanonicalRoot) -> str:
    """Return the case-folded checkout folder name."""
    return root.display.rsplit("\\", 1)[-1].casefold()


@dataclass(frozen=True)
class _PaneIndex:
    """Every live pane, indexed once by full UUID and by canonical checkout root."""

    by_id: Mapping[str, tuple[PaneRecord, ...]]
    by_root: Mapping[CanonicalRoot, tuple[PaneRecord, ...]]
    activity: Mapping[str, PaneActivity]
    sessions: frozenset[str]

    @classmethod
    def build(cls, observation: PaneObservation) -> _PaneIndex:
        """Group the listing in one pass; discovery order never matters."""
        by_id: dict[str, list[PaneRecord]] = {}
        by_root: dict[CanonicalRoot, list[PaneRecord]] = {}
        for pane in observation.panes:
            by_id.setdefault(pane.pane_id, []).append(pane)
            root = _root_of(pane)
            if root is not None:
                by_root.setdefault(root, []).append(pane)
        return cls(
            {key: tuple(panes) for key, panes in by_id.items()},
            {root: tuple(panes) for root, panes in by_root.items()},
            observation.activity,
            frozenset(pane.session for pane in observation.panes),
        )

    def names(self, *, labels: bool) -> frozenset[str]:
        """Return the case-folded session and folder names, and pane labels when asked."""
        names = {session.casefold() for session in self.sessions} | {_folder(root) for root in self.by_root}
        if labels:
            names |= {pane.name.casefold() for panes in self.by_id.values() for pane in panes}
        return frozenset(names)


def _unmatched(names: Iterable[str], known: frozenset[str]) -> tuple[str, ...]:
    """Return the names that match nothing, in their given order."""
    return tuple(name for name in names if name.casefold() not in known)


def _name_failures(request: PlanRequest, index: _PaneIndex) -> tuple[GlobalFailure, ...]:
    """Refuse the run for any unmatched exclusion or switch name."""
    failures: list[GlobalFailure] = []
    excepts = _unmatched(request.excepts, index.names(labels=True))
    if excepts:
        failures.append(GlobalFailure(GlobalReason.EXCEPT_UNMATCHED, excepts))
    switches = _unmatched(request.switch_roles, index.names(labels=False))
    if switches:
        failures.append(GlobalFailure(GlobalReason.SWITCH_UNMATCHED, switches))
    return tuple(failures)


def _resolved(reading: RoutingReading) -> SavedRouting | None:
    """Return the routing only when every part of it is resolved."""
    return reading.routing if reading.state is RoutingState.RESOLVED else None


def _switchable(routing: SavedRouting | None) -> bool:
    """Return whether the routing is a saved requestor pause with a recorded pair."""
    return (
        routing is not None
        and routing.pause.session_role is SessionRole.REQUESTOR
        and isinstance(routing.requestor, RoutingTarget)
        and isinstance(routing.reviewer, RoutingTarget)
    )


def _pair(routing: SavedRouting, *, switched: bool) -> tuple[RoutingTarget, RoutingTarget]:
    """Return the requestor and reviewer targets this run assigns; the switch swaps them."""
    requestor, reviewer = cast("RoutingTarget", routing.requestor), cast("RoutingTarget", routing.reviewer)
    return (reviewer, requestor) if switched else (requestor, reviewer)


def _assigned(routing: SavedRouting, *, switched: bool) -> tuple[_Slot, _Slot | None]:
    """Return the resumed slot and, for a saved requestor pair only, the counterpart reviewer slot."""
    resumed = cast("RoutingTarget", routing.resumed)
    paired = switched or (_switchable(routing) and resumed.role is SessionRole.REQUESTOR)
    if not paired:
        return _Slot(ActionKind.RESUME, resumed.role, resumed), None
    requestor, reviewer = _pair(routing, switched=switched)
    return _Slot(ActionKind.RESUME, SessionRole.REQUESTOR, requestor), _Slot(ActionKind.REVIEWER, SessionRole.REVIEWER, reviewer)


def _verdict(base: CheckoutPlan, refusal: _Refusal, actions: tuple[PlannedAction, ...] = ()) -> CheckoutPlan:
    """Return a skipped checkout with its skipped actions, or a failed one with none."""
    if isinstance(refusal.reason, SkipReason):
        return replace(base, outcome=CheckoutOutcome.SKIPPED, reason=refusal.reason, detail=refusal.detail, actions=actions)
    return replace(base, outcome=CheckoutOutcome.ERROR, reason=refusal.reason, detail=refusal.detail, actions=())


def _changes(target: RoutingTarget, pane: PaneRecord) -> tuple[str, ...]:
    """Report a changed label or agent session id; neither is a conflict."""
    notes: list[str] = []
    if pane.name != target.label:
        notes.append("label-changed")
    if target.agent_session_id is not None and pane.agent_session_id != target.agent_session_id:
        notes.append("agent-session-changed")
    return tuple(notes)


@dataclass(frozen=True)
class _RunContext:
    """What every checkout of one run shares: request, index, ports and the case-folded selector names."""

    request: PlanRequest
    index: _PaneIndex
    ports: PlannerPorts
    excepts: frozenset[str]
    switches: frozenset[str]

    @classmethod
    def of(cls, request: PlanRequest, index: _PaneIndex, ports: PlannerPorts) -> _RunContext:
        """Normalize the exclusion and switch names once for the whole run."""
        return cls(
            request, index, ports,
            frozenset(name.casefold() for name in request.excepts), frozenset(name.casefold() for name in request.switch_roles),
        )


class _CheckoutPlanner:
    """Plan one discovered checkout in isolation from the shared run context.

    Fix (code review round 1): the selector names arrive normalized once per
    run instead of being folded again for each checkout.
    """

    def __init__(self, run: _RunContext, root: CanonicalRoot) -> None:
        """Bind the run's shared context to one checkout root."""
        self.request = run.request
        self.index = run.index
        self.ports = run.ports
        self.root = root
        self.panes = run.index.by_root[root]
        self.excepts = run.excepts
        self.named = _folder(root) in run.switches or any(pane.session.casefold() in run.switches for pane in self.panes)

    def plan(self) -> CheckoutPlan | None:
        """Return the checkout's plan, ``None`` without a saved prompt; failing evidence stays local."""
        try:
            snapshot = self.ports.read_snapshot(self.root)
            if snapshot.state is PromptState.NO_PROMPT:
                return None
            return self._classify(snapshot)
        except ArtifactError as error:
            return CheckoutPlan(self.root, PromptState.ERROR, CheckoutOutcome.ERROR, ErrorReason.EVIDENCE_INVALID, str(error))

    def _classify(self, snapshot: CheckoutSnapshot) -> CheckoutPlan:
        """Apply the checkout-level gates: readable pause, folder exclusion and switch applicability."""
        prompt = snapshot.prompt
        base = CheckoutPlan(
            self.root, snapshot.state, CheckoutOutcome.PLANNED,
            title=prompt.title if prompt else None, author=prompt.author if prompt else None,
            paused_at=prompt.snapshot if prompt else None, digest=prompt.digest if prompt else None,
        )
        if snapshot.state is PromptState.ERROR:
            return _verdict(base, _Refusal(ErrorReason.CHECKOUT_UNREADABLE, snapshot.diagnostic))
        if _folder(self.root) in self.excepts:
            return _verdict(base, _Refusal(SkipReason.EXCLUDED, "checkout folder"))
        if self.named and not _switchable(_resolved(cast("RoutingReading", snapshot.routing))):
            return _verdict(base, _Refusal(ErrorReason.SWITCH_NOT_APPLICABLE, "no saved requestor pair"))
        return self._prompted(replace(base, switched=self.named), snapshot)

    def _prompted(self, base: CheckoutPlan, snapshot: CheckoutSnapshot) -> CheckoutPlan:
        """Classify a readable prompt: used, unsupported pauser, unusable routing, or fresh."""
        prompt, reading = cast("PromptMetadata", snapshot.prompt), cast("RoutingReading", snapshot.routing)
        if snapshot.state is PromptState.USED:
            return self._used(base, cast("UsageReceipt", snapshot.receipt), prompt, _resolved(reading))
        if host_for_agent(prompt.author) is None:
            return _verdict(base, _Refusal(SkipReason.UNSUPPORTED_PAUSER, prompt.author or "unknown"))
        if reading.state is RoutingState.ERROR:
            return _verdict(base, _Refusal(ErrorReason.ROUTING_INVALID, "; ".join(reading.reasons)))
        if reading.state is RoutingState.UNRESOLVED:
            exchange = cast("SavedRouting", reading.routing).exchange
            reason = SkipReason.PAIRING_AMBIGUOUS if isinstance(exchange, Unresolved) else SkipReason.ROUTING_UNRESOLVED
            return _verdict(base, _Refusal(reason, "; ".join(reading.reasons)))
        if reading.state is not RoutingState.RESOLVED:
            return _verdict(base, _Refusal(_ROUTING_SKIPS[reading.state]))
        return self._fresh(base, prompt, cast("SavedRouting", reading.routing))

    def _used(self, base: CheckoutPlan, receipt: UsageReceipt, prompt: PromptMetadata, routing: SavedRouting | None) -> CheckoutPlan:
        """Report the receipt; only the resumed requestor's saved pair may continue its reviewer."""
        evidence = DuplicateEvidence(DuplicateSignal.RECEIPT, receipt.receiving_pane, receipt.resumed_by or "unknown", timestamp_instant(receipt.used_at))
        base = replace(base, duplicates=(evidence,))
        if receipt.schema != _MARKED_SCHEMA or routing is None or not _switchable(routing):
            return _verdict(base, _Refusal(SkipReason.ALREADY_USED))
        requestor, reviewer = _pair(routing, switched=base.switched)
        if receipt.receiving_pane == requestor.pane_id:
            return self._continue(base, prompt, routing, _Slot(ActionKind.CONTINUE_REVIEWER, SessionRole.REVIEWER, reviewer))
        detail = f"resumed requestor {receipt.receiving_pane}"
        if base.switched:
            return _verdict(base, _Refusal(ErrorReason.SWITCH_MISMATCH, detail))
        if receipt.receiving_pane == reviewer.pane_id:
            return _verdict(base, _Refusal(SkipReason.SWITCH_REQUIRED, f"{detail}; continuing the switched pair needs --switch-roles"))
        return _verdict(base, _Refusal(SkipReason.ALREADY_USED, detail))

    def _continue(self, base: CheckoutPlan, prompt: PromptMetadata, routing: SavedRouting, slot: _Slot) -> CheckoutPlan:
        """Plan the later reviewer continuation, conditional on its verified missing reviewer."""
        examined = self._examine(slot, check_activity=False)
        if examined[1] is not None:
            return self._refused(base, examined)
        return self._bind(base, prompt, routing, (examined,))

    def _fresh(self, base: CheckoutPlan, prompt: PromptMetadata, routing: SavedRouting) -> CheckoutPlan:
        """Suppress on checkout-wide duplicate evidence, fail on uncertainty, then plan the targets."""
        pause = PauseFacts(self.root, timestamp_instant(prompt.snapshot), reviewer=routing.pause.session_role is SessionRole.REVIEWER)
        verdict = classify_duplicates(pause, self.panes, self.ports.history, self.index.activity, self.ports.journal)
        base = replace(base, duplicates=verdict.evidence)
        if verdict.evidence:
            return _verdict(base, _Refusal(_DUPLICATE_SKIPS[verdict.evidence[0].signal]))
        if verdict.uncertain:
            return _verdict(base, _Refusal(ErrorReason.DUPLICATE_UNCERTAIN, "; ".join(verdict.uncertain)))
        resumed, counterpart = _assigned(routing, switched=base.switched)
        examined = self._examine(resumed, check_activity=True)
        if examined[1] is not None:
            return self._refused(base, examined)
        planned = [examined]
        if counterpart is not None:
            other = self._examine(counterpart, check_activity=False)
            if other[1] is not None and isinstance(other[1].reason, ErrorReason):
                return _verdict(base, other[1])
            planned.append(other)
        return self._bind(base, prompt, routing, tuple(planned))

    def _examine(self, slot: _Slot, *, check_activity: bool) -> _Examined:
        """Validate one saved target against discovery, then its protections."""
        target = slot.target
        located = self._locate(target)
        if isinstance(located, _Refusal):
            return slot, located, ()
        notes = _changes(target, located)
        refusal = self._identify(target, located) or self._protect(located)
        if refusal is not None or not check_activity:
            return slot, refusal, notes
        eligibility = input_eligibility(located, target.host, self.index.activity.get(located.pane_id), self.ports.probe)
        skip = _ACTIVITY_SKIPS.get(eligibility.activity)
        return slot, None if skip is None else _Refusal(skip, eligibility.activity.value), notes + ((eligibility.note,) if eligibility.note else ())

    def _locate(self, target: RoutingTarget) -> PaneRecord | _Refusal:
        """Find the one live record of the saved UUID in its saved TUIOS session."""
        records = self.index.by_id.get(target.pane_id, ())
        if len(records) != 1:
            return _Refusal(ErrorReason.PANE_AMBIGUOUS if records else SkipReason.TARGET_ABSENT, target.pane_id)
        (pane,) = records
        if pane.session == target.session:
            return pane
        moved = target.session in self.index.sessions
        reason = ErrorReason.TARGET_SESSION_CHANGED if moved else SkipReason.TARGET_ABSENT
        return _Refusal(reason, f"{target.pane_id} is in session {pane.session}")

    @staticmethod
    def _identify(target: RoutingTarget, pane: PaneRecord) -> _Refusal | None:
        """Require the saved host and checkout; a shell pane is no agent."""
        try:
            host = pane_host(pane)
        except ArtifactError:
            return _Refusal(ErrorReason.HOST_CONTRADICTORY, pane.pane_id)
        if host is None:
            return _Refusal(SkipReason.TARGET_NOT_AGENT, pane.pane_id)
        if host is not target.host:
            return _Refusal(ErrorReason.TARGET_HOST_CHANGED, f"saved {target.host.value}, live {host.value}")
        root = _root_of(pane)
        if root is None:
            return _Refusal(SkipReason.TARGET_IDENTITY_UNAVAILABLE, pane.pane_id)
        return None if root == target.checkout else _Refusal(ErrorReason.TARGET_CHECKOUT_CHANGED, root.display)

    def _protect(self, pane: PaneRecord) -> _Refusal | None:
        """Protect excluded sessions and pane labels and the caller's own pane."""
        if pane.session.casefold() in self.excepts or pane.name.casefold() in self.excepts:
            return _Refusal(SkipReason.EXCLUDED, "pane")
        if pane.pane_id == self.request.caller_pane:
            return _Refusal(SkipReason.CALLER_PANE, pane.pane_id)
        return None

    def _live(self, routing: SavedRouting) -> LiveExchange | _Refusal | None:
        """Observe the saved exchange read-only; ``None`` when no exchange applies."""
        exchange = routing.exchange
        if not isinstance(exchange, SavedExchange):
            return None
        observed = self.ports.exchanges.observe(self.root, exchange)
        if observed.kind is ExchangeObservationKind.OBSERVED and observed.occurrence is not None and observed.round_number is not None:
            return LiveExchange(observed.occurrence, observed.round_number)
        return _Refusal(_EXCHANGE_REFUSALS.get(observed.kind, ErrorReason.EXCHANGE_DAMAGED), observed.diagnostic)

    def _bind(self, base: CheckoutPlan, prompt: PromptMetadata, routing: SavedRouting, examined: tuple[_Examined, ...]) -> CheckoutPlan:
        """Bind each unrefused slot's marked command to the live exchange; the resume comes first."""
        live = self._live(routing)
        if isinstance(live, _Refusal):
            return _verdict(base, live)
        actions = tuple(self._action(item, None if item[1] else self._command(item[0], prompt, routing, live)) for item in examined)
        return replace(base, outcome=CheckoutOutcome.PLANNED, actions=actions)

    def _command(self, slot: _Slot, prompt: PromptMetadata, routing: SavedRouting, live: LiveExchange | None) -> str:
        """Render the native command with a fresh marker bound to the rebuilt assignment."""
        assignment = resolve_assignment(routing, prompt.digest, slot.target.pane_id, slot.role, live)
        marker = Marker(self.ports.launch_id(), slot.target.pane_id, slot.role, assignment.digest())
        return marked_command(slot.target.host, slot.kind, marker)

    def _refused(self, base: CheckoutPlan, examined: _Examined) -> CheckoutPlan:
        """Return the checkout refused by one slot: skipped with that slot's action, or failed."""
        refusal = cast("_Refusal", examined[1])
        actions = (self._action(examined, None),) if isinstance(refusal.reason, SkipReason) else ()
        return _verdict(base, refusal, actions)

    def _action(self, examined: _Examined, command: str | None) -> PlannedAction:
        """Describe one slot's planned command or its skip reason."""
        slot, refusal, notes = examined
        target = slot.target
        return PlannedAction(
            slot.kind, slot.role, target.host, target.session, target.pane_id, target.label, command,
            clear=self.request.clear and slot.kind is ActionKind.RESUME,
            conditional=slot.kind is not ActionKind.RESUME,
            skip=None if refusal is None else cast("SkipReason", refusal.reason),
            notes=notes,
        )


def plan_run(request: PlanRequest, observation: PaneObservation | None, ports: PlannerPorts) -> RunPlan:
    """Build the read-only plan of one human launch; a run-wide refusal reads no checkout."""
    if request.caller.origin is CallerOrigin.AGENT:
        signals = tuple(reason.code for reason in request.caller.reasons)
        return RunPlan(request.dry_run, (GlobalFailure(GlobalReason.AGENT_CALLER, signals),))
    if observation is None:
        return RunPlan(request.dry_run, (GlobalFailure(GlobalReason.DISCOVERY_FAILED),))
    index = _PaneIndex.build(observation)
    failures = _name_failures(request, index)
    if failures:
        return RunPlan(request.dry_run, failures)
    checkouts = _plan_checkouts(request, index, ports)
    return RunPlan(request.dry_run, (), checkouts, _omitted(observation, checkouts))


def plan_checkout(request: PlanRequest, observation: PaneObservation, ports: PlannerPorts, root: CanonicalRoot) -> CheckoutPlan | None:
    """Replan one checkout from a fresh observation, as Step 6 does immediately before each send.

    The run's global gates already passed; the checkout's own gates, duplicate
    evidence, targets and exchange are read again. ``None`` when the checkout
    has no live pane or no saved prompt any more.
    """
    index = _PaneIndex.build(observation)
    if root not in index.by_root:
        return None
    return _CheckoutPlanner(_RunContext.of(request, index, ports), root).plan()


def _plan_checkouts(request: PlanRequest, index: _PaneIndex, ports: PlannerPorts) -> tuple[CheckoutPlan, ...]:
    """Plan every discovered checkout in canonical root order; prompt-less ones are omitted."""
    run = _RunContext.of(request, index, ports)
    plans = (_CheckoutPlanner(run, root).plan() for root in sorted(index.by_root, key=lambda root: root.key))
    return tuple(plan for plan in plans if plan is not None)


def _omitted(observation: PaneObservation, checkouts: tuple[CheckoutPlan, ...]) -> int:
    """Count the live panes that no reported checkout targets."""
    targeted = {action.pane_id for checkout in checkouts for action in checkout.actions}
    return sum(1 for pane in observation.panes if pane.pane_id not in targeted)


__all__ = [
    "ExchangeObserver",
    "PlannerPorts",
    "marked_command",
    "plan_checkout",
    "plan_run",
]


# eof
