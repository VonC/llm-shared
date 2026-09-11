"""Table-driven state classification for the review-exchange lifecycle.

Step 3 requires one fail-closed classifier over exact artifacts, durable
coordination, repair markers, suspended confirmation, and lease expiry.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from functools import partial
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    IncompleteTransitionKind,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import Envelope, render_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

_NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)
_CURRENT = "2026-08-04T11:59:30+00:00"
_EXPIRED = "2026-08-04T11:00:00+00:00"


def _context(root: Path, slug: str = "review-exchange-core") -> ReviewContext:
    """Create one valid code-review context below a temporary project."""
    document = root / "docs" / f"plan.v0.11.0.{slug}.md"
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text("# Plan\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", slug),
        document,
        None,
        "3",
    )


def _core(root: Path) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext]:
    """Build one deterministic core and its exact persistence store."""
    context = _context(root)
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    core = ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=60),
        wall_clock=lambda: _NOW,
        monotonic_clock=lambda: 0.0,
        sleeper=lambda _: None,
    )
    return core, store, context


def _record(
    context: ReviewContext,
    *,
    status: CoordinationStatus = CoordinationStatus.ACTIVE,
    current: bool = True,
    marker: IncompleteTransitionKind | None = None,
    outcome: ConfirmationOutcome | None = None,
) -> CoordinationRecord:
    """Create one valid durable state for a classifier scenario."""
    owner, expected = _record_actors(status)
    lease = _record_lease(status, current=current)
    label, timestamp = _confirmation_fields(outcome)
    return CoordinationRecord(
        context=context,
        policy=FamilyPolicy("ready", "Another round", "Commit"),
        status=status,
        owner=owner,
        expected_next_actor=expected,
        round_number=1,
        lease_renewed_at=lease,
        convergence_recommended=(
            True
            if status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
            else None
        ),
        incomplete_transition=marker,
        transcript_entry_id="entry-round-1" if marker is not None else None,
        transcript_offset=0 if marker is not None else None,
        escalation_reason=(
            "manual review required" if status is CoordinationStatus.ESCALATED else None
        ),
        confirmation_label=label,
        confirmed_outcome=outcome,
        confirmation_timestamp=timestamp,
    )


def _record_actors(status: CoordinationStatus) -> tuple[Actor, Actor]:
    """Return owner and next actor for one durable status."""
    if status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION:
        return Actor.REVIEWER, Actor.HUMAN
    if status is CoordinationStatus.ESCALATED:
        return Actor.REQUESTOR, Actor.HUMAN
    return Actor.REQUESTOR, Actor.REVIEWER


def _record_lease(status: CoordinationStatus, *, current: bool) -> str | None:
    """Return a valid lease only for active coordination."""
    if status is not CoordinationStatus.ACTIVE:
        return None
    return _CURRENT if current else _EXPIRED


def _confirmation_fields(outcome: ConfirmationOutcome | None) -> tuple[str | None, str | None]:
    """Return the paired label and timestamp for a durable outcome."""
    if outcome is None:
        return None, None
    return "Commit", _CURRENT


def _artifact(
    context: ReviewContext,
    role: ReviewRole,
    *,
    disposition: ReviewDisposition | None = None,
) -> str:
    """Render valid identity-bearing content for one exact artifact."""
    return render_envelope_markdown(
        Envelope(
            context.identity,
            context.umbrella_path,
            context.document_path,
            context.implementation_step,
            role,
            1,
            _CURRENT,
            disposition,
        ),
        "Substantive content.\n",
    )


def _publish_request(store: ReviewExchangeStore, context: ReviewContext) -> None:
    """Publish one valid request without running a lifecycle transition."""
    store.publish_atomic(store.paths.request, _artifact(context, ReviewRole.REQUESTOR))


def _publish_answer(
    store: ReviewExchangeStore,
    context: ReviewContext,
    disposition: ReviewDisposition = ReviewDisposition.CHANGES_REQUESTED,
) -> None:
    """Publish one valid reviewer answer without consuming a request."""
    store.publish_atomic(
        store.paths.answer,
        _artifact(context, ReviewRole.REVIEWER, disposition=disposition),
    )


def _setup_idle(_store: ReviewExchangeStore, _context: ReviewContext) -> None:
    """Leave all live artifacts absent."""


def _setup_round(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    current: bool,
) -> None:
    """Arrange a bare active round."""
    store.write_coordination(_record(context, current=current))


def _setup_request(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    current: bool | None,
) -> None:
    """Arrange request evidence with current, expired, or absent coordination."""
    _publish_request(store, context)
    if current is not None:
        store.write_coordination(_record(context, current=current))


def _setup_answer(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    current: bool | None,
) -> None:
    """Arrange answer evidence with current, expired, or absent coordination."""
    _publish_answer(store, context)
    if current is not None:
        store.write_coordination(_record(context, current=current))


def _setup_tombstone(store: ReviewExchangeStore, context: ReviewContext) -> None:
    """Arrange one orphan request tombstone."""
    store.publish_atomic(store.paths.tombstone, _artifact(context, ReviewRole.REQUESTOR))


def _setup_answer_transition(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    current: bool,
    answer_present: bool,
) -> None:
    """Arrange one marked answer transition before or after answer publication."""
    _setup_tombstone(store, context)
    if answer_present:
        _publish_answer(store, context)
    store.write_coordination(
        _record(
            context,
            current=current,
            marker=IncompleteTransitionKind.PUBLISH_ANSWER,
        ),
    )


def _setup_gate(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    recovery: bool,
) -> None:
    """Arrange a durable or answer-authoritative convergence gate."""
    _publish_answer(store, context, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    status = (
        CoordinationStatus.ACTIVE
        if recovery
        else CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    )
    store.write_coordination(_record(context, status=status))


def _setup_owning(
    store: ReviewExchangeStore,
    context: ReviewContext,
    *,
    answer_present: bool,
) -> None:
    """Arrange durable owning authorization with optional retained answer."""
    if answer_present:
        _publish_answer(store, context, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    store.write_coordination(
        _record(
            context,
            status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
            outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
        ),
    )


def _setup_escalated(store: ReviewExchangeStore, context: ReviewContext) -> None:
    """Arrange stopped coordination with retained request evidence."""
    _publish_request(store, context)
    store.write_coordination(_record(context, status=CoordinationStatus.ESCALATED))


def _setup_both_live(store: ReviewExchangeStore, context: ReviewContext) -> None:
    """Arrange the impossible request-plus-answer live shape."""
    _publish_request(store, context)
    _publish_answer(store, context)
    store.write_coordination(_record(context))


_SCENARIO_SETUPS: dict[str, Callable[[ReviewExchangeStore, ReviewContext], None]] = {
    "idle": _setup_idle,
    "round-current": partial(_setup_round, current=True),
    "round-expired": partial(_setup_round, current=False),
    "request-current": partial(_setup_request, current=True),
    "request-expired": partial(_setup_request, current=False),
    "request-orphan": partial(_setup_request, current=None),
    "answer-current": partial(_setup_answer, current=True),
    "answer-expired": partial(_setup_answer, current=False),
    "answer-orphan": partial(_setup_answer, current=None),
    "tombstone-orphan": _setup_tombstone,
    "answer-publishing": partial(
        _setup_answer_transition,
        current=True,
        answer_present=False,
    ),
    "answer-publishing-expired": partial(
        _setup_answer_transition,
        current=False,
        answer_present=False,
    ),
    "answer-append": partial(
        _setup_answer_transition,
        current=True,
        answer_present=True,
    ),
    "answer-append-expired": partial(
        _setup_answer_transition,
        current=False,
        answer_present=True,
    ),
    "gate": partial(_setup_gate, recovery=False),
    "gate-recovery": partial(_setup_gate, recovery=True),
    "owning": partial(_setup_owning, answer_present=True),
    "owning-after-answer-cleanup": partial(_setup_owning, answer_present=False),
    "escalated": _setup_escalated,
    "both-live": _setup_both_live,
}


@pytest.mark.parametrize(
    ("setup", "expected"),
    [
        ("idle", ArtifactState.IDLE),
        ("round-current", ArtifactState.ROUND_IN_PROGRESS),
        ("round-expired", ArtifactState.ABANDONED_MID_ROUND),
        ("request-current", ArtifactState.REQUEST_PENDING),
        ("request-expired", ArtifactState.ABANDONED_REQUEST),
        ("request-orphan", ArtifactState.ABANDONED_REQUEST),
        ("answer-current", ArtifactState.ANSWER_PENDING),
        ("answer-expired", ArtifactState.ABANDONED_ANSWER),
        ("answer-orphan", ArtifactState.ABANDONED_ANSWER),
        ("tombstone-orphan", ArtifactState.INTERRUPTED_ANSWER_PUBLICATION),
        ("answer-publishing", ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS),
        ("answer-publishing-expired", ArtifactState.INTERRUPTED_ANSWER_PUBLICATION),
        ("answer-append", ArtifactState.TRANSCRIPT_REPAIR_PENDING),
        ("answer-append-expired", ArtifactState.INTERRUPTED_TRANSCRIPT_APPEND),
        ("gate", ArtifactState.CONVERGENCE_GATE),
        ("gate-recovery", ArtifactState.CONVERGENCE_GATE),
        ("owning", ArtifactState.OWNING_ACTION_PENDING),
        ("owning-after-answer-cleanup", ArtifactState.OWNING_ACTION_PENDING),
        ("escalated", ArtifactState.ESCALATED),
        ("both-live", ArtifactState.INCONSISTENT),
    ],
)
def test_classify_covers_every_observable_state(
    tmp_path: Path,
    setup: str,
    expected: ArtifactState,
) -> None:
    """Every listed artifact and lease shape has one stable state."""
    core, store, context = _core(tmp_path)
    _SCENARIO_SETUPS[setup](store, context)

    assert core.classify().state is expected


def test_incomplete_marker_overlays_live_state_until_repaired(tmp_path: Path) -> None:
    """A current marker blocks its identity even before artifact publication."""
    core, store, context = _core(tmp_path)
    store.write_coordination(
        _record(context, marker=IncompleteTransitionKind.PUBLISH_REQUEST),
    )

    observation = core.classify()

    assert observation.state is ArtifactState.TRANSCRIPT_REPAIR_PENDING
    assert observation.record is not None
    assert observation.record.incomplete_transition is IncompleteTransitionKind.PUBLISH_REQUEST


def test_identity_conflict_fails_before_clock_is_consulted(tmp_path: Path) -> None:
    """Cross-identity evidence is inconsistent regardless of lease timing."""
    core, store, _ = _core(tmp_path)
    other = _context(tmp_path, "another-document")
    store.paths.request.parent.mkdir(parents=True, exist_ok=True)
    store.paths.request.write_text(
        _artifact(other, ReviewRole.REQUESTOR),
        encoding="utf-8",
    )
    core._wall_clock = lambda: (_ for _ in ()).throw(AssertionError("clock used"))

    observation = core.classify()

    assert observation.state is ArtifactState.INCONSISTENT
    assert "identity" in observation.diagnostic


def test_malformed_coordination_and_impossible_confirmation_fail_closed(
    tmp_path: Path,
) -> None:
    """Unreadable state and an orphan another-round outcome never gain authority."""
    core, store, context = _core(tmp_path)
    store.paths.coordination.parent.mkdir(parents=True, exist_ok=True)
    store.paths.coordination.write_text("not JSON", encoding="utf-8")
    assert core.classify().state is ArtifactState.INCONSISTENT

    store.paths.coordination.unlink()
    _publish_answer(store, context, ReviewDisposition.CONVERGENCE_RECOMMENDED)
    record = _record(
        context,
        status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
        outcome=ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW,
    )
    store.write_coordination(
        replace(
            record,
            confirmation_label="Another round",
            confirmed_outcome=ConfirmationOutcome.ANOTHER_ROUND,
        ),
    )

    assert core.classify().state is ArtifactState.INCONSISTENT


# eof
