"""Pure observable-state classification for review exchanges.

Step 3 isolates the artifact/status decision table from persistence and
orchestration. Identity or parsing errors fail closed before lease time is
consulted, incomplete transcript markers overlay live states, and only the
explicit design-table shapes receive operational authority.
"""


from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.review_exchange_models import (
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    IncompleteTransitionKind,
    ReviewDisposition,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_models_envelope import Envelope


@dataclass(frozen=True)
class ArtifactSnapshot:
    """Validated exact artifact presence and parsed current-round metadata."""

    request_present: bool
    answer_present: bool
    tombstone_present: bool
    request_envelope: Envelope | None
    answer_envelope: Envelope | None
    tombstone_envelope: Envelope | None
    record: CoordinationRecord | None
    errors: tuple[str, ...] = ()

    @property
    def shape(self) -> tuple[bool, bool, bool]:
        """Return request, answer, and tombstone presence in table order."""
        return self.request_present, self.answer_present, self.tombstone_present


@dataclass(frozen=True)
class StateDecision:
    """Pure classifier output with a human-diagnosable explanation."""

    state: ArtifactState
    diagnostic: str


def classify_snapshot(
    snapshot: ArtifactSnapshot,
    lease_is_current: Callable[[CoordinationRecord], bool],
) -> StateDecision:
    """Map one validated fixed-path snapshot to the complete observable table."""
    if snapshot.errors:
        decision = _decision(ArtifactState.INCONSISTENT, "; ".join(snapshot.errors))
    else:
        decision = _classify_valid_snapshot(snapshot, lease_is_current)
    return decision


def _classify_valid_snapshot(
    snapshot: ArtifactSnapshot,
    lease_is_current: Callable[[CoordinationRecord], bool],
) -> StateDecision:
    """Classify a snapshot whose exact-path evidence parsed successfully."""
    record = snapshot.record
    if record is not None and record.incomplete_transition is not None:
        return _classify_marker(snapshot, lease_is_current)
    if record is not None and record.status is CoordinationStatus.ESCALATED:
        return _decision(ArtifactState.ESCALATED, record.escalation_reason or "escalated")

    invalid_shape = _classify_invalid_live_shape(snapshot)
    if invalid_shape is not None:
        return invalid_shape
    return _classify_record_status(snapshot, lease_is_current)


def _classify_invalid_live_shape(snapshot: ArtifactSnapshot) -> StateDecision | None:
    """Reject mutually exclusive live artifact combinations."""
    request, answer, tombstone = snapshot.shape
    if request and answer:
        return _decision(ArtifactState.INCONSISTENT, "request and answer are both present")
    if request and tombstone:
        return _decision(ArtifactState.INCONSISTENT, "request and tombstone are both present")
    return None


def _classify_record_status(
    snapshot: ArtifactSnapshot,
    lease_is_current: Callable[[CoordinationRecord], bool],
) -> StateDecision:
    """Delegate a valid artifact shape according to its coordination status."""
    record = snapshot.record

    if record is None:
        return _classify_without_coordination(snapshot)
    if record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION:
        return _classify_confirmation(snapshot)
    if record.status is not CoordinationStatus.ACTIVE:
        return _decision(ArtifactState.INCONSISTENT, "unsupported coordination status")
    return _classify_active(snapshot, current=lease_is_current(record))


def _classify_marker(
    snapshot: ArtifactSnapshot,
    lease_is_current: Callable[[CoordinationRecord], bool],
) -> StateDecision:
    """Apply the identity-scoped incomplete-transition overlay."""
    record = snapshot.record
    if record is None or record.incomplete_transition is None:
        return _decision(ArtifactState.INCONSISTENT, "marker has no coordination")
    marker = record.incomplete_transition
    shape = snapshot.shape
    valid = {
        IncompleteTransitionKind.PUBLISH_REQUEST: shape in {
            (False, False, False),
            (True, False, False),
        },
        IncompleteTransitionKind.PUBLISH_ANSWER: shape in {
            (True, False, False),
            (False, False, True),
            (False, True, True),
            (False, True, False),
        },
        IncompleteTransitionKind.ESCALATION: True,
        IncompleteTransitionKind.HUMAN_CONFIRMATION: shape in {
            (False, True, False),
            (False, False, False),
        },
        IncompleteTransitionKind.HUMAN_COMPLETION: shape == (False, False, False),
        IncompleteTransitionKind.HUMAN_RECLAIM: True,
        IncompleteTransitionKind.HUMAN_RESOLUTION: True,
    }[marker]
    if not valid:
        return _decision(
            ArtifactState.INCONSISTENT,
            f"artifact shape contradicts {marker.value} repair marker",
        )
    current = (
        True
        if record.status is not CoordinationStatus.ACTIVE
        else lease_is_current(record)
    )
    if marker is IncompleteTransitionKind.PUBLISH_ANSWER and shape == (
        False,
        False,
        True,
    ):
        state = (
            ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS
            if current
            else ArtifactState.INTERRUPTED_ANSWER_PUBLICATION
        )
        return _decision(state, "answer publication owns the consumed request")
    state = (
        ArtifactState.TRANSCRIPT_REPAIR_PENDING
        if current
        else ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND
    )
    return _decision(state, f"{marker.value} transcript repair is pending")


def _classify_without_coordination(snapshot: ArtifactSnapshot) -> StateDecision:
    """Classify preserved orphan evidence without inferring a lease."""
    states = {
        (False, False, False): (
            ArtifactState.IDLE,
            "no live exchange artifacts",
        ),
        (True, False, False): (
            ArtifactState.ABANDONED_REQUEST,
            "request has no active coordination",
        ),
        (False, True, False): (
            ArtifactState.ABANDONED_ANSWER,
            "answer has no active coordination",
        ),
        (False, False, True): (
            ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
            "consumed request has no active coordination",
        ),
    }
    state = states.get(snapshot.shape)
    if state is None:
        return _decision(
            ArtifactState.INCONSISTENT,
            "artifact combination has no coordination record",
        )
    return _decision(*state)


def _classify_confirmation(snapshot: ArtifactSnapshot) -> StateDecision:
    """Classify the suspended human gate and durable owning authorization."""
    record = snapshot.record
    if record is None:
        decision = _decision(ArtifactState.INCONSISTENT, "confirmation has no record")
    elif snapshot.request_present or snapshot.tombstone_present:
        decision = _decision(
            ArtifactState.INCONSISTENT,
            "confirmation state contains request-side evidence",
        )
    elif record.confirmed_outcome is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW:
        decision = _decision(
            ArtifactState.OWNING_ACTION_PENDING,
            "human authorization is durable and awaits owning action completion",
        )
    elif record.confirmed_outcome is ConfirmationOutcome.ANOTHER_ROUND:
        decision = _decision(
            ArtifactState.INCONSISTENT,
            "another-round confirmation was not completed",
        )
    elif not snapshot.answer_present:
        decision = _decision(
            ArtifactState.INCONSISTENT,
            "convergence gate has no retained answer",
        )
    elif (
        snapshot.answer_envelope is None
        or snapshot.answer_envelope.disposition
        is not ReviewDisposition.CONVERGENCE_RECOMMENDED
    ):
        decision = _decision(
            ArtifactState.INCONSISTENT,
            "confirmation gate answer is not a convergence recommendation",
        )
    else:
        decision = _decision(
            ArtifactState.CONVERGENCE_GATE,
            "human confirmation is required",
        )
    return decision


def _classify_active(snapshot: ArtifactSnapshot, *, current: bool) -> StateDecision:
    """Classify an unmarked active record after validating its artifact shape."""
    request, answer, tombstone = snapshot.shape
    if tombstone:
        return _decision(
            ArtifactState.INCONSISTENT,
            "unmarked active coordination contains a request tombstone",
        )
    if answer:
        envelope = snapshot.answer_envelope
        if envelope is not None and envelope.disposition is (
            ReviewDisposition.CONVERGENCE_RECOMMENDED
        ):
            return _decision(
                ArtifactState.CONVERGENCE_GATE,
                "convergence answer authoritatively requires gate recovery",
            )
        state = ArtifactState.ANSWER_PENDING if current else ArtifactState.ABANDONED_ANSWER
        return _decision(state, "reviewer answer awaits requestor action")
    if request:
        state = ArtifactState.REQUEST_PENDING if current else ArtifactState.ABANDONED_REQUEST
        return _decision(state, "request awaits reviewer action")
    state = (
        ArtifactState.ROUND_IN_PROGRESS
        if current
        else ArtifactState.ABANDONED_MID_ROUND
    )
    return _decision(state, "active round has no counterpart artifact")


def _decision(state: ArtifactState, diagnostic: str) -> StateDecision:
    """Construct a concise immutable state decision."""
    return StateDecision(state, diagnostic)


# eof
