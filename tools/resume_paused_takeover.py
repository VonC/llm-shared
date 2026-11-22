"""Takeover observation and verified missing-reviewer activation of the bulk resume.

Step 7 of v0.14.0 resume-paused implements the Step 6 ``Takeover`` seam
(design, "Takeover observation and later reviewer continuation"):

1. ``MarkedTakeover.received`` observes every accepted resume's receiver
   read-only for at most 120 seconds after its acceptance, on a bound of its
   own that no later look extends. No event channel is pinned, so each look is
   a bounded read with backoff from half a second to five seconds, and every
   look re-reads every piece of evidence; nothing seen earlier is reused. A
   remaining-time check precedes every read, and a read completed after the
   bound is never acted on. A requestor of a live exchange settles once the
   durable records prove its takeover (``CLAIMED`` with the claim's
   generation); any other receiver once its schema 3 receipt consumed the
   prompt (``CONSUMED``). At the bound a receipt alone stays ``CONSUMED`` and
   nothing durable is ``COMPLETION_UNCONFIRMED``: both remain successes. A
   failed compact result line for this launch, a pane blocked on a question,
   a receipt of another launch, a replaced or removed prompt and damaged
   evidence fail the receiver.
2. Compact result lines come from the injected ``ResultSource`` (at most 100
   characters, host-profile allowlisted, ``tools.resume_paused_marker``
   grammar). They are supplementary: only ``failed`` is acted on, and a
   masked, truncated or evicted line is never proof; the durable receipt and
   marked claim decide. ``NoResults`` reads none while no profile is pinned.
3. ``MarkedTakeover.reviewer`` decides a conditional reviewer from fresh
   evidence, on initial activation and on a later continuation alike (the
   requestor marker then comes from the receipt alone; no continuation file
   exists): consumption and a live exchange, then the exact active-reviewer
   leave-alone check, then the requestor's current marked claim, whose
   counterpart must be the planned reviewer, then positive no-wait evidence
   (``tools.resume_paused_reviewer_wait``). Only a resumed requestor
   activates a pair. It then delivers through ``PairDelivery.deliver`` with
   two pre-send checks run under the held guard immediately before the send:
   the same decision refreshed from the send's fresh listing (before a Codex
   recovery Enter only the durable takeover is refreshed, since the pane then
   holds the command), and the design Q27=B all-pane idle guard
   (``tools.resume_paused_pane_guard``). Their refusals report the reviewer
   pending; an accepted reviewer is observed for its own 120 seconds until
   its marked claim is current. Nothing is ever resent. The delivered
   reviewer marker keeps the planned launch id but binds the exchange's live
   occurrence and round, which the reviewer's validator rebuilds: a requestor
   that published a new round since planning keeps a valid reviewer marker,
   and a round that moves again before the send stops it, pending.
4. Every Claude reviewer outcome carries ``limits=claude-wait-scope``;
   ``preview_notes`` gives the same code to a conditional-activation preview,
   and ``CLAUDE_WAIT_LIMITS`` defines the five disclosed limits for Step 8's
   help and reference.

Fix (code review round 1): observation and each reviewer decision bind the
plan's accepted prompt (``PairDelivery.digest``): an older receipt waits, a
changed prompt fails, even before any receipt; no exchange read starts once
the saved-prompt read spent the bound. ``CLAUDE_WAIT_SCOPE`` moved to the model.

Nothing here writes a file, persists or prints a conversation, log, token or
token digest, or parses arguments.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import timedelta
from functools import partial
from types import MappingProxyType
from typing import TYPE_CHECKING, Final, Protocol, cast

from tools.resume_paused_delivery import FIRST_WAIT_SECONDS, WAIT_CAP_SECONDS
from tools.resume_paused_delivery_model import (
    CALL_BOUND_SECONDS,
    CLAUDE_WAIT_SCOPE,
    ActionReport,
    DeliveryOutcome,
    Phase,
    ReceiverState,
    Refusal,
)
from tools.resume_paused_marker import (
    LiveExchange,
    Marker,
    ResultLine,
    marker_in_command,
    resolve_assignment,
)
from tools.resume_paused_models import ArtifactError, SessionRole, timestamp_instant
from tools.resume_paused_plan_model import ActionKind
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import DISCLOSED_LIMITS, Host
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_reviewer_wait import WaitScope, reviewer_active
from tools.resume_paused_takeover_proof import (
    Proof,
    ProofState,
    consumption,
    current_claim,
    read_durable,
    read_exchange,
    read_pause,
    takeover,
    takeover_ready,
)
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from tools.resume_paused_artifacts import (
        CheckoutSnapshot,
        PromptMetadata,
        UsageReceipt,
    )
    from tools.resume_paused_delivery_model import (
        PairDelivery,
        PaneTransport,
        PreSendCheck,
        SendStep,
        Sleeper,
    )
    from tools.resume_paused_evidence import ObservedCommand, PaneObservation
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_models import CanonicalRoot, PromptDigest
    from tools.resume_paused_plan_model import PlannedAction
    from tools.resume_paused_planner import ExchangeObserver
    from tools.resume_paused_profiles import Clock
    from tools.resume_paused_review import ExchangeSnapshot
    from tools.resume_paused_reviewer_wait import ReviewerWait
    from tools.resume_paused_routing import SavedRouting
    from tools.resume_paused_takeover_proof import Durable

OBSERVATION_BOUND: Final = timedelta(seconds=120)
FAILED_RESULT: Final = "failed"
CLAUDE_WAIT_LIMITS: Final[Mapping[str, str]] = MappingProxyType(dict(zip(DISCLOSED_LIMITS, (
    "processes detached by completed foreground commands or hooks may be missed (Q20=A)",
    "earlier hook-handler configuration history is unavailable (Q20=A)",
    "backward clock changes since the last OS boot, offsetting ones included, can remain undetectable (Q21=A)",
    "work of Claude roots with no records in the read set can be missed: persistence-disabled roots, other "
    "configuration roots, transcripts removed without detectable evidence and unrecorded work surviving a recorded "
    "parent's validated end after ordinary exit, kill, TaskStop or timeout (Q26=A)",
    "a local shell command still running whose input is not yet recorded, and work it starts meanwhile, can be "
    "missed in a Claude root that has no TUIOS pane (Q27=B)",
), strict=True)))


def preview_notes(action: PlannedAction) -> tuple[str, ...]:
    """Return the notes a preview shows for one planned action: the wait-scope limits of a conditional Claude reviewer."""
    claude_reviewer = action.conditional and action.host is Host.CLAUDE and action.command is not None
    return (CLAUDE_WAIT_SCOPE,) if claude_reviewer else ()


class ResultSource(Protocol):
    """Injected compact result lines of one pane, restricted by its host profile to the result grammar."""

    def results(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Return the pane's candidate result lines, ``None`` when unreadable."""
        ...


class NoResults:
    """``ResultSource`` while no host profile is pinned: no result line is readable."""

    def results(self, pane: PaneRecord, timeout: float) -> tuple[str, ...] | None:
        """Read nothing."""
        del pane, timeout


@dataclass(frozen=True)
class TakeoverPorts:
    """Every injected dependency of the takeover: time, panes, durable records, reviewer wait and the Q27 guard."""

    clock: Clock
    sleeper: Sleeper
    transport: PaneTransport
    read_snapshot: Callable[[CanonicalRoot], CheckoutSnapshot]
    exchanges: ExchangeObserver
    wait: ReviewerWait
    guard: PreSendCheck
    results: ResultSource = field(default_factory=NoResults)


@dataclass(frozen=True)
class _Seen:
    """What one look established about a receiver."""

    state: ReceiverState
    reason: str = ""
    generation: int | None = None


@dataclass(frozen=True)
class _Gate:
    """The decision on one reviewer activation: ``None`` permits it, a pending refusal reports it pending.

    A permitting gate carries ``command``: the planned reviewer command with
    its marker rebound to the exchange's live occurrence and round.
    """

    refusal: Refusal | None
    pending: bool = False
    notes: tuple[str, ...] = ()
    command: str | None = None


@dataclass(frozen=True)
class Activation:
    """One reviewer activation to decide: its checkout, planned action and the delivered requestor marker.

    ``expected`` is ``None`` for a later continuation, whose requestor marker
    comes from the receipt alone; ``digest`` is the prompt the plan accepted.
    """

    root: CanonicalRoot
    action: PlannedAction
    expected: Marker | None = None
    digest: PromptDigest | None = None


@dataclass(frozen=True)
class _Candidate:
    """The reviewer one decision judges: its fresh listing, live record and history read once."""

    observation: PaneObservation
    pane: PaneRecord
    commands: tuple[ObservedCommand, ...] | None


def _locate(observation: PaneObservation | None, pane_id: str) -> PaneRecord | None:
    """Return the one live record of a pane, ``None`` when absent, repeated or undiscovered."""
    records = [] if observation is None else [pane for pane in observation.panes if pane.pane_id == pane_id]
    return records[0] if len(records) == 1 else None


def _gate(proof: Proof) -> _Gate:
    """Turn an unproved takeover into its gate: a failure, or a pending refusal."""
    failed = proof.state is ProofState.FAILED
    return _Gate(Refusal(proof.reason, failed=failed), pending=not failed)


def _rebound(action: PlannedAction, durable: Durable) -> str | None:
    """Return the planned reviewer command with its marker rebound to the exchange's live occurrence and round.

    The reviewer's validator rebuilds its assignment from the live round, so a
    requestor that published a new round since planning would otherwise make
    the planned marker refuse. The launch id stays the planned one; ``None``
    when the planned marker does not parse.
    """
    exchange, routing = cast("ExchangeSnapshot", durable.exchange), cast("SavedRouting", durable.routing)
    prompt = cast("PromptMetadata", durable.snapshot.prompt)
    live = LiveExchange(cast("int", exchange.occurrence), cast("int", exchange.round_number))
    try:
        planned = marker_in_command(cast("str", action.command))
        binding = resolve_assignment(routing, prompt.digest, action.pane_id, SessionRole.REVIEWER, live).digest()
    except ArtifactError:
        return None
    return marked_command(action.host, action.kind, Marker(planned.launch_id, action.pane_id, SessionRole.REVIEWER, binding))


class _Watch:
    """Observe one receiver under its own fixed post-acceptance bound, re-reading all evidence at every look."""

    def __init__(self, ports: TakeoverPorts, pane_id: str, launch_id: str) -> None:
        """Start the receiver's bound now, right after its acceptance."""
        self._ports = ports
        self._pane_id = pane_id
        self._launch_id = launch_id
        self._deadline = ports.clock.now() + OBSERVATION_BOUND
        self.best: _Seen | None = None

    def left(self) -> float:
        """Return the seconds left in the bound."""
        return (self._deadline - self._ports.clock.now()).total_seconds()

    def spent(self) -> bool:
        """Return whether the bound is spent, so no further read may start."""
        return self.left() <= 0

    def bound(self) -> float:
        """Return the seconds one blocking read may take: what is left, at most the call bound."""
        return max(0.0, min(CALL_BOUND_SECONDS, self.left()))

    def run(self, look: Callable[[], _Seen | None]) -> _Seen:
        """Look until a look settles or the bound passes; a look completed after the bound is not acted on."""
        wait = FIRST_WAIT_SECONDS
        while not self.spent():
            seen = look()
            if self.spent():
                break
            if seen is not None:
                return seen
            self._ports.sleeper.sleep(min(wait, self.left()))
            wait = min(wait * 2, WAIT_CAP_SECONDS)
        return self.best or _Seen(ReceiverState.COMPLETION_UNCONFIRMED)

    def failure(self) -> _Seen | None:
        """Return a failure the receiver shows: a question on its pane or a failed result for this launch."""
        observation = self._ports.transport.observe(self.bound())
        pane = _locate(observation, self._pane_id)
        if self.spent() or pane is None:
            return None
        activity = cast("PaneObservation", observation).activity.get(pane.pane_id)
        if activity is not None and (activity.blocked or activity.question):
            return _Seen(ReceiverState.FAILED, "receiver-question")
        lines = self._ports.results.results(pane, self.bound())
        if self.spent() or not lines:
            return None
        return _Seen(ReceiverState.FAILED, "receiver-failed") if self._failed(lines) else None

    def _failed(self, lines: tuple[str, ...]) -> bool:
        """Return whether a well-formed result line reports this launch failed; other lines prove nothing."""
        for line in lines:
            try:
                result = ResultLine.parse(line)
            except ArtifactError:
                continue
            if result.launch_id == self._launch_id and result.outcome == FAILED_RESULT:
                return True
        return False

    def durable(self, root: CanonicalRoot) -> Durable | _Seen | None:
        """Read the durable records once, ``None`` when the bound is spent before, between or after the two reads."""
        if self.spent():
            return None
        snapshot = read_pause(root, self._ports.read_snapshot)
        if self.spent():
            return None
        if isinstance(snapshot, Proof):
            return _Seen(ReceiverState.FAILED, snapshot.reason)
        durable = read_exchange(root, snapshot, self._ports.exchanges)
        return None if self.spent() else durable

    def look(self, root: CanonicalRoot) -> Durable | _Seen | None:
        """Look for a failure first, then read the durable records: a failure, nothing or the records."""
        return self.failure() or self.durable(root)


def _observed(report: ActionReport, seen: _Seen) -> ActionReport:
    """Record a receiver's observation in its report; only a failure fails the action."""
    if seen.state is ReceiverState.FAILED:
        return replace(report, receiver=seen.state, reason=seen.reason, failed=True)
    return replace(report, receiver=seen.state, generation=seen.generation)


class _Recorded:
    """``PreSendCheck`` wrapper that records the last refusal of the check it wraps."""

    def __init__(self, check: PreSendCheck) -> None:
        """Wrap one check."""
        self._check = check
        self.refused: Refusal | None = None

    def check(self, step: SendStep) -> Refusal | None:
        """Run the wrapped check and record a refusal."""
        refusal = self._check.check(step)
        if refusal is not None:
            self.refused = refusal
        return refusal

    def pending(self, report: ActionReport) -> bool:
        """Return whether the wrapped check's expected (not failed) refusal stopped the delivered send."""
        refusal = self.refused
        return refusal is not None and not refusal.failed and refusal.reason == report.reason


class _ReviewerGate:
    """``PreSendCheck`` that refreshes the whole reviewer decision from the send's fresh listing, keeping its last refusal."""

    def __init__(self, takeover: MarkedTakeover, activation: Activation) -> None:
        """Keep the takeover and the activation it refreshes."""
        self._takeover = takeover
        self._activation = activation
        self.refused: _Gate | None = None

    def check(self, step: SendStep) -> Refusal | None:
        """Refuse the send unless the takeover still holds and the live round still binds the delivered command.

        Before a recovery Enter only the durable takeover is read.
        """
        gate = self._takeover.decide(self._activation, step.observation, wait=step.phase is not Phase.RECOVERY)
        if gate.refusal is None and gate.command != step.action.command:
            gate = _Gate(Refusal("reviewer-binding-changed"), pending=True)
        if gate.refusal is not None:
            self.refused = gate
        return gate.refusal

    def pending(self, report: ActionReport) -> bool:
        """Return whether this gate's pending refusal stopped the delivered send."""
        gate = self.refused
        return gate is not None and gate.pending and cast("Refusal", gate.refusal).reason == report.reason


class MarkedTakeover:
    """``Takeover`` of marked resumes: receiver observation and verified missing-reviewer activation."""

    def __init__(self, ports: TakeoverPorts) -> None:
        """Keep the injected ports."""
        self._ports = ports

    def received(self, pair: PairDelivery, report: ActionReport) -> ActionReport:
        """Observe an accepted resume's receiver for its own bound; other reports stay unchanged."""
        command = report.action.command
        if report.outcome is not DeliveryOutcome.ACCEPTED or command is None:
            return report
        try:
            marker = marker_in_command(command)
        except ArtifactError:
            return replace(report, receiver=ReceiverState.FAILED, reason="marker-unreadable", failed=True)
        watch = _Watch(self._ports, marker.pane_id, marker.launch_id)
        return _observed(report, watch.run(partial(self._resume_look, watch, pair, report.action, marker)))

    @staticmethod
    def _resume_look(watch: _Watch, pair: PairDelivery, action: PlannedAction, marker: Marker) -> _Seen | None:
        """Look once at a resumed receiver: a failure, its consumption of the accepted prompt, then a requestor's takeover."""
        durable = watch.look(pair.root)
        if durable is None or isinstance(durable, _Seen):
            return durable
        consumed = consumption(durable, marker, action.host, pair.digest)
        if consumed.state is not ProofState.PROVED:
            return _Seen(ReceiverState.FAILED, consumed.reason) if consumed.state is ProofState.FAILED else None
        watch.best = _Seen(ReceiverState.CONSUMED)
        if action.role is not SessionRole.REQUESTOR or durable.exchange is None:
            return watch.best
        proof = takeover(durable, marker, action.host, pair.digest)
        if proof.state is ProofState.PROVED:
            return _Seen(ReceiverState.CLAIMED, generation=proof.generation)
        return _Seen(ReceiverState.FAILED, proof.reason) if proof.state is ProofState.FAILED else None

    def reviewer(self, pair: PairDelivery, resumed: ActionReport | None, action: PlannedAction) -> ActionReport:
        """Decide one conditional reviewer; every Claude reviewer outcome carries the wait-scope limits."""
        report = self._reviewer(pair, resumed, action)
        return replace(report, notes=(*report.notes, CLAUDE_WAIT_SCOPE)) if action.host is Host.CLAUDE else report

    def _reviewer(self, pair: PairDelivery, resumed: ActionReport | None, action: PlannedAction) -> ActionReport:
        """Activate the reviewer only after a fresh decision, then observe its claim for its own bound."""
        expected = self._expected(resumed, action)
        if isinstance(expected, ActionReport):
            return expected
        gate = self.decide(Activation(pair.root, action, expected, pair.digest), self._ports.transport.observe(CALL_BOUND_SECONDS), wait=True)
        if gate.refusal is not None:
            return self._refused(action, gate)
        action = replace(action, command=gate.command)
        refresh, guard = _ReviewerGate(self, Activation(pair.root, action, expected, pair.digest)), _Recorded(self._ports.guard)
        delivered = pair.deliver(action, Phase.REVIEWER, (refresh, guard))
        if delivered.outcome is not DeliveryOutcome.ACCEPTED:
            pending = refresh.pending(delivered) or guard.pending(delivered)
            return replace(delivered, outcome=DeliveryOutcome.PENDING) if pending else delivered
        delivered = replace(delivered, notes=(*delivered.notes, *gate.notes))
        marker = marker_in_command(cast("str", action.command))
        watch = _Watch(self._ports, marker.pane_id, marker.launch_id)
        return _observed(delivered, watch.run(partial(self._reviewer_look, watch, pair.root, marker)))

    @staticmethod
    def _expected(resumed: ActionReport | None, action: PlannedAction) -> Marker | ActionReport | None:
        """Return the delivered requestor's marker, ``None`` for a continuation, or why no reviewer may follow."""
        if resumed is None:
            return None
        if resumed.action.role is not SessionRole.REQUESTOR or resumed.action.kind is not ActionKind.RESUME:
            return ActionReport(action, DeliveryOutcome.REFUSED, "resumed-not-requestor")
        if resumed.failed:
            return ActionReport(action, DeliveryOutcome.REFUSED, "requestor-failed")
        return marker_in_command(cast("str", resumed.action.command))

    @staticmethod
    def _refused(action: PlannedAction, gate: _Gate) -> ActionReport:
        """Report a reviewer that receives no input: pending, an expected skip or a failure."""
        refusal = cast("Refusal", gate.refusal)
        outcome = DeliveryOutcome.PENDING if gate.pending else DeliveryOutcome.REFUSED
        return ActionReport(action, outcome, refusal.reason, refusal.failed, notes=gate.notes)

    def decide(self, activation: Activation, observation: PaneObservation | None, *, wait: bool) -> _Gate:
        """Decide one activation from fresh evidence: takeover, leave-alone, current claim, then no-wait evidence.

        ``wait`` is ``False`` only before a Codex recovery Enter, whose pane
        already holds the reviewer command: the durable takeover is refreshed
        without judging the pane's wait.
        """
        pane = _locate(observation, activation.action.pane_id)
        if observation is None or pane is None:
            return _Gate(Refusal("discovery-failed", failed=True)) if observation is None else _Gate(Refusal("target-absent"), pending=True)
        candidate = _Candidate(observation, pane, self._ports.wait.commands(pane))
        proved = self._takeover(activation, candidate)
        if isinstance(proved, _Gate):
            return proved
        command = _rebound(activation.action, proved[0])
        if command is None:
            return _Gate(Refusal("reviewer-marker-unreadable", failed=True))
        gate = self._wait(activation, *proved, candidate) if wait else _Gate(None)
        return gate if gate.refusal is not None else replace(gate, command=command)

    def _takeover(self, activation: Activation, candidate: _Candidate) -> tuple[Durable, Proof] | _Gate:
        """Prove the requestor's takeover, leaving an exact active reviewer alone before the claim check."""
        durable = read_durable(activation.root, self._ports.read_snapshot, self._ports.exchanges)
        if isinstance(durable, Proof):
            return _gate(durable)
        ready = takeover_ready(durable, activation.expected, intended=activation.digest)
        if ready.state is not ProofState.PROVED:
            return _gate(ready)
        if reviewer_active(cast("ExchangeSnapshot", durable.exchange), candidate.pane, candidate.commands):
            return _Gate(Refusal("reviewer-active"))
        claim = current_claim(durable, ready)
        if claim.state is not ProofState.PROVED:
            return _gate(claim)
        if claim.counterpart != activation.action.pane_id:
            return _Gate(Refusal("reviewer-not-paired", failed=True))
        return durable, claim

    def _wait(self, activation: Activation, durable: Durable, claim: Proof, candidate: _Candidate) -> _Gate:
        """Require positive no-wait evidence for the reviewer, binding the proved requestor's pane and marked input."""
        marker, host = cast("Marker", claim.marker), cast("Host", claim.host)
        claude = host is Host.CLAUDE
        requestor = _locate(candidate.observation, marker.pane_id) if claude else None
        if claude and requestor is None:
            return _Gate(Refusal("requestor-pane-absent"), pending=True)
        marked = marked_command(host, ActionKind.RESUME, marker) if claude else None
        since = timestamp_instant(cast("UsageReceipt", durable.snapshot.receipt).used_at)
        scope = WaitScope(activation.root, candidate.pane, since, requestor, marked)
        activity = candidate.observation.activity.get(candidate.pane.pane_id)
        verdict = self._ports.wait.verdict(scope, activation.action.host, activity, candidate.commands)
        return _Gate(verdict.refusal, pending=verdict.refusal is not None, notes=verdict.notes)

    @staticmethod
    def _reviewer_look(watch: _Watch, root: CanonicalRoot, marker: Marker) -> _Seen | None:
        """Look once at an activated reviewer: a failure, or its marked claim current at the reviewer's generation."""
        durable = watch.look(root)
        if durable is None or isinstance(durable, _Seen):
            return durable
        exchange = durable.exchange
        if exchange is None or exchange.kind is not ExchangeObservationKind.OBSERVED:
            return None
        binding, generation = exchange.marked_claim, exchange.ownership_generation
        if binding is None or binding.issued_generation != generation or exchange.owner is not Actor.REVIEWER:
            return None
        claim = binding.evidence
        if (claim.launch_id, claim.pane_id, claim.assignment_binding) != (marker.launch_id, marker.pane_id, marker.binding):
            return None
        return _Seen(ReceiverState.CLAIMED, generation=generation)


__all__ = [
    "CLAUDE_WAIT_LIMITS",
    "CLAUDE_WAIT_SCOPE",
    "FAILED_RESULT",
    "OBSERVATION_BOUND",
    "Activation",
    "MarkedTakeover",
    "NoResults",
    "ResultSource",
    "TakeoverPorts",
    "preview_notes",
]


# eof
