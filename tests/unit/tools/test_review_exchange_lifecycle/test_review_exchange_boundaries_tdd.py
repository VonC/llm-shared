"""Boundary and fail-closed coverage for the review-exchange lifecycle.

These tests exercise defensive branches that valid happy-path orchestration
cannot normally reach, plus recovery states that require deliberately staged
durable evidence. Multi-harness journeys use fixtures so Groundhog measures the
boundary assertions rather than repeated temporary repository setup.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _answer,
    _context,
    _harness,
    _reach_gate,
    _request,
    _timestamp,
)
from tools.review_exchange_core import ReviewExchangeCore, WaitOutcome
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
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_envelope import (
    Envelope,
    parse_envelope_markdown,
    render_envelope_markdown,
)
from tools.review_exchange_observer import ExchangeObservation
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_state import (
    ArtifactSnapshot,
    _classify_confirmation,
    _classify_marker,
    _classify_record_status,
    classify_snapshot,
)
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models_coordination import CoordinationRecord


def _new_core(store: ReviewExchangeStore, context: ReviewContext) -> ReviewExchangeCore:
    """Bind a core for constructor and observer boundary tests."""
    return ReviewExchangeCore(
        store,
        context,
        FamilyPolicy("commit-ready", "Another round", "Commit"),
        ReviewConfiguration(enabled=True, wait_timeout_seconds=60),
    )


def _different_context(
    root: Path,
    context: ReviewContext,
    *,
    different_identity: bool = False,
    different_parent: bool = False,
) -> ReviewContext:
    """Create a valid context differing in identity or document parent."""
    identity = context.identity
    if different_identity:
        identity = ExchangeIdentity(
            context.identity.family,
            context.identity.type_token,
            context.identity.version,
            "other-review",
        )
    parent = root / "elsewhere" if different_parent else context.document_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    document = parent / f"plan.{identity.version}.{identity.slug}.md"
    document.write_text("# Other plan\n", encoding="utf-8")
    return ReviewContext(identity, document, context.umbrella_path, "3")


def _confirmation_record(record: CoordinationRecord) -> CoordinationRecord:
    """Convert active coordination into a valid suspended gate."""
    return replace(
        record,
        status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
        owner=Actor.REVIEWER,
        expected_next_actor=Actor.HUMAN,
        lease_renewed_at=None,
        convergence_recommended=True,
    )


def _snapshot(
    *,
    record: CoordinationRecord | None = None,
    answer: Envelope | None = None,
    request_present: bool = False,
    answer_present: bool = False,
    tombstone_present: bool = False,
) -> ArtifactSnapshot:
    """Build a pure classifier snapshot for one defensive branch."""
    return ArtifactSnapshot(
        request_present=request_present,
        answer_present=answer_present,
        tombstone_present=tombstone_present,
        request_envelope=None,
        answer_envelope=answer,
        tombstone_envelope=None,
        record=record,
    )


def _lease_is_current(_record: CoordinationRecord) -> bool:
    """Return a deterministic current-lease verdict for pure state tests."""
    return True


def test_core_constructor_rejects_identity_and_document_parent_mismatch(
    tmp_path: Path,
) -> None:
    """A core cannot bind a store to a different identity or document folder."""
    context = _context(tmp_path)
    store = ReviewExchangeStore(derive_artifact_paths(tmp_path, context))

    with pytest.raises(ReviewExchangeError, match="store identity"):
        _new_core(store, _different_context(tmp_path, context, different_identity=True))
    with pytest.raises(ReviewExchangeError, match="transcript parent"):
        _new_core(store, _different_context(tmp_path, context, different_parent=True))


@pytest.fixture
def request_boundary_journey(
    tmp_path: Path,
) -> None:
    """Request publication fails before mutation at every authority boundary."""
    core, _, context, clock = _harness(tmp_path)
    core.start()

    with pytest.raises(ReviewExchangeError, match="artifact role"):
        core.publish_request(_answer(context, clock, 1), "Wrong role.")
    other = _different_context(tmp_path, context, different_parent=True)
    with pytest.raises(ReviewExchangeError, match="review context"):
        core.publish_request(_request(other, clock, 1), "Wrong context.")
    with pytest.raises(ReviewExchangeError, match="artifact round"):
        core.publish_request(_request(context, clock, 2), "Wrong round.")

    core.publish_request(_request(context, clock, 1), "First publication.")
    with pytest.raises(ReviewExchangeError, match="round in progress"):
        core.publish_request(_request(context, clock, 1), "Duplicate publication.")

    second, _, second_context, second_clock = _harness(tmp_path / "guided")
    _reach_gate(second, second_context, second_clock)
    second.confirm("Another round", guidance="Preserve this instruction.")
    with pytest.raises(ReviewExchangeError, match="omits confirmed human guidance"):
        second.publish_request(
            _request(second_context, second_clock, 2),
            "Missing guidance.",
        )


def test_request_boundaries_reject_wrong_state_role_context_round_and_guidance(
    request_boundary_journey: None,
) -> None:
    """Every request boundary remains covered by the prepared journey."""
    assert request_boundary_journey is None


def test_core_defensive_helpers_reject_missing_or_conflicting_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unreachable inconsistent inputs remain explicitly fail closed."""
    core, _, _, _ = _harness(tmp_path)
    record = core.start()
    without_record = ExchangeObservation(
        ArtifactState.IDLE,
        None,
        None,
        None,
        "synthetic missing coordination",
    )
    with pytest.raises(ReviewExchangeError, match="durable coordination"):
        core._require_record(without_record)

    marked = core._mark_transition(
        record,
        IncompleteTransitionKind.PUBLISH_REQUEST,
        "request-step-3-round-1",
    )
    with pytest.raises(ReviewExchangeError, match="another transcript repair"):
        core._mark_transition(
            marked,
            IncompleteTransitionKind.PUBLISH_ANSWER,
            "answer-step-3-round-1",
        )

    synthetic = ExchangeObservation(
        ArtifactState.ANSWER_PENDING,
        record,
        None,
        None,
        "synthetic answer without envelope",
    )
    monkeypatch.setattr(core, "classify", lambda: synthetic)
    with pytest.raises(ReviewExchangeError, match="lacks a change request"):
        core.consume_answer(reviewed_work_changed=True)
    with pytest.raises(ReviewExchangeError, match="authoritative answer"):
        core._restore_convergence_gate(record, None)


def test_answer_repair_validates_visible_content_in_both_recovery_shapes(
    tmp_path: Path,
) -> None:
    """Visible repair evidence is accepted only when its bytes are authoritative."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    answer = _answer(context, clock, 1)
    different = answer.replace("Reviewer feedback.", "Different reviewer feedback.")
    store.publish_atomic(store.paths.answer, answer)

    core._publish_or_repair_answer(answer)
    with pytest.raises(ReviewExchangeError, match="differs from repair content"):
        core._publish_or_repair_answer(different)

    store.publish_atomic(store.paths.tombstone, _request(context, clock, 1))
    with pytest.raises(ReviewExchangeError, match="differs from repair content"):
        core._publish_or_repair_answer(different)
    core._publish_or_repair_answer(answer)

    store.remove_exact(store.paths.answer)
    store.remove_exact(store.paths.tombstone)
    with pytest.raises(ReviewExchangeError, match="no authoritative request"):
        core._publish_or_repair_answer(answer)


def test_escalation_validates_reason_recovers_orphan_and_repairs_marked_state(
    tmp_path: Path,
) -> None:
    """Escalation is strict, can adopt orphan evidence, and resumes idempotently."""
    core, store, context, clock = _harness(tmp_path)
    with pytest.raises(ReviewExchangeError, match="non-empty"):
        core.escalate("   ")

    store.publish_atomic(store.paths.request, _request(context, clock, 1))
    orphan = core.escalate("Adopt orphan request")
    assert orphan.round_number == 1

    repair_core, repair_store, _, _ = _harness(tmp_path / "repair")
    active = repair_core.start()
    marked = repair_core._mark_transition(
        active,
        IncompleteTransitionKind.ESCALATION,
        "escalation-round-1",
    )
    pending = replace(
        marked,
        status=CoordinationStatus.ESCALATED,
        expected_next_actor=Actor.HUMAN,
        lease_renewed_at=None,
        escalation_reason="Repair escalation",
    )
    repair_store.write_coordination(pending)

    with pytest.raises(ReviewExchangeError, match="different reason"):
        repair_core.escalate("Changed escalation")

    repaired = repair_core.escalate("Repair escalation")
    assert repaired.incomplete_transition is None


@pytest.fixture
def rejected_human_operations_journey(tmp_path: Path) -> None:
    """Reject invalid human operations outside the measured assertion call."""
    core, _, _, _ = _harness(tmp_path)
    core.start()
    with pytest.raises(ReviewExchangeError, match="convergence gate"):
        core.confirm("Commit")
    with pytest.raises(ReviewExchangeError, match="convergence gate"):
        core.cancel("Too early")
    with pytest.raises(ReviewExchangeError, match="durably authorized"):
        core.complete()
    with pytest.raises(ReviewExchangeError, match="non-empty"):
        core.resolve_escalation(" ", archive=False)
    with pytest.raises(ReviewExchangeError, match="escalated exchange"):
        core.resolve_escalation("Not escalated", archive=False)

    gated_core, gated_store, context, clock = _harness(tmp_path / "gated")
    _reach_gate(gated_core, context, clock)
    gated = gated_store.read_coordination(required=True)
    assert gated is not None
    marked = gated_core._mark_transition(
        gated,
        IncompleteTransitionKind.HUMAN_CONFIRMATION,
        "human-confirmation-round-1",
    )
    staged = replace(
        marked,
        confirmation_label="Another round",
        confirmed_outcome=ConfirmationOutcome.ANOTHER_ROUND,
        confirmation_timestamp=_timestamp(clock),
        human_guidance="Original guidance",
    )
    gated_store.write_coordination(staged)
    with pytest.raises(ReviewExchangeError, match="differs from durable choice"):
        gated_core.confirm("Another round", guidance="Changed guidance")


def test_human_operations_reject_wrong_state_or_changed_replay(
    rejected_human_operations_journey: None,
) -> None:
    """Human actions require the persisted gate, authorization, and exact retry."""
    assert rejected_human_operations_journey is None


@pytest.fixture
def rejected_authorization_replay_journey(
    tmp_path: Path,
) -> None:
    """Reject a changed authorization label outside the measured call."""
    core, _, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    core.confirm("Commit")

    with pytest.raises(ReviewExchangeError, match="another label"):
        core.confirm("Another round")


def test_authorized_confirmation_rejects_a_different_persisted_label(
    rejected_authorization_replay_journey: None,
) -> None:
    """Replaying owning authorization cannot substitute another registered label."""
    assert rejected_authorization_replay_journey is None


def test_resolution_rejects_an_incomplete_escalation_transition(tmp_path: Path) -> None:
    """Human resolution cannot overtake a marker-owned escalation repair."""
    core, store, _, _ = _harness(tmp_path)
    active = core.start()
    marked = core._mark_transition(
        active,
        IncompleteTransitionKind.ESCALATION,
        "escalation-round-1",
    )
    store.write_coordination(
        replace(
            marked,
            status=CoordinationStatus.ESCALATED,
            expected_next_actor=Actor.HUMAN,
            lease_renewed_at=None,
            escalation_reason="Pending repair",
        ),
    )

    with pytest.raises(ReviewExchangeError, match="pending transition"):
        core.resolve_escalation("Resolve too early", archive=False)


def test_observer_reports_context_policy_round_and_artifact_context_conflicts(
    tmp_path: Path,
) -> None:
    """Every parsed metadata disagreement makes the exact snapshot inconsistent."""
    core, store, context, clock = _harness(tmp_path)
    record = core.start()

    store.write_coordination(replace(record, context=replace(context, implementation_step="4")))
    assert "coordination context" in core.classify().diagnostic

    store.write_coordination(
        replace(record, policy=FamilyPolicy("other", "Again", "Continue")),
    )
    assert "family policy" in core.classify().diagnostic

    store.write_coordination(record)
    store.publish_atomic(store.paths.request, _request(context, clock, 2))
    assert "round differs" in core.classify().diagnostic

    store.remove_exact(store.paths.request)
    mismatched = Envelope(
        context.identity,
        context.umbrella_path,
        context.document_path,
        "4",
        ReviewRole.REQUESTOR,
        1,
        _timestamp(clock),
    )
    store.publish_atomic(
        store.paths.request,
        render_envelope_markdown(mismatched, "Mismatched context.\n"),
    )
    assert "artifact context" in core.classify().diagnostic

    suspended = _confirmation_record(record)
    assert core._observer._lease_is_current(suspended) is False


def test_pure_classifier_defensive_states_fail_closed(tmp_path: Path) -> None:
    """Missing or unsupported coordination never grants authority."""
    core, _, _, _ = _harness(tmp_path)
    active = core.start()

    unsupported = replace(
        active,
        status=CoordinationStatus.ESCALATED,
        expected_next_actor=Actor.HUMAN,
        lease_renewed_at=None,
        escalation_reason="Synthetic",
    )
    assert _classify_record_status(
        _snapshot(record=unsupported),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT
    assert _classify_marker(
        _snapshot(),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT
    assert _classify_confirmation(_snapshot()).state is ArtifactState.INCONSISTENT


def test_pure_classifier_conflicting_shapes_fail_closed(tmp_path: Path) -> None:
    """Every unlisted artifact combination remains inconsistent."""
    core, _, _, _ = _harness(tmp_path)
    active = core.start()

    assert classify_snapshot(
        _snapshot(answer_present=True, tombstone_present=True),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT
    assert classify_snapshot(
        _snapshot(request_present=True, tombstone_present=True),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT
    assert classify_snapshot(
        _snapshot(record=active, tombstone_present=True),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT


def test_pure_classifier_marker_and_gate_conflicts_fail_closed(tmp_path: Path) -> None:
    """Contradictory marker and confirmation shapes stay unauthoritative."""
    core, _, context, clock = _harness(tmp_path)
    active = core.start()

    invalid_marker = replace(
        active,
        incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
        transcript_entry_id="request-step-3-round-1",
        transcript_offset=0,
    )
    assert classify_snapshot(
        _snapshot(record=invalid_marker, answer_present=True),
        _lease_is_current,
    ).state is ArtifactState.INCONSISTENT

    answer_markdown = _answer(context, clock, 1)
    answer, _ = parse_envelope_markdown(answer_markdown)
    waiting = _confirmation_record(active)
    assert _classify_confirmation(
        _snapshot(record=waiting, request_present=True),
    ).state is ArtifactState.INCONSISTENT
    assert _classify_confirmation(
        _snapshot(record=waiting),
    ).state is ArtifactState.INCONSISTENT
    assert _classify_confirmation(
        _snapshot(record=waiting, answer=answer, answer_present=True),
    ).state is ArtifactState.INCONSISTENT


@pytest.fixture
def wait_terminal_states_journey(
    tmp_path: Path,
) -> tuple[WaitOutcome, WaitOutcome, WaitOutcome]:
    """Prepare invalid-policy and terminal-state evidence outside call timing."""
    core, _store, _, _ = _harness(tmp_path)
    core.start()
    with pytest.raises(ReviewExchangeError, match="wait target"):
        core.wait_for_exact(ArtifactState.IDLE)
    with pytest.raises(ReviewExchangeError, match="intervals must be positive"):
        core.wait_for_exact(ArtifactState.REQUEST_PENDING, poll_interval=0)

    core.escalate("Already stopped")
    escalated = core.wait_for_exact(ArtifactState.REQUEST_PENDING)

    inconsistent_core, inconsistent_store, _, _ = _harness(tmp_path / "inconsistent")
    inconsistent_core.start()
    inconsistent_store.paths.request.parent.mkdir(parents=True, exist_ok=True)
    inconsistent_store.paths.request.write_text("invalid", encoding="utf-8")
    inconsistent = inconsistent_core.wait_for_exact(ArtifactState.REQUEST_PENDING)

    repair_core, _, _, _ = _harness(tmp_path / "repair-wait")
    record = repair_core.start()
    repair_core._mark_transition(
        record,
        IncompleteTransitionKind.PUBLISH_REQUEST,
        "request-step-3-round-1",
    )
    repair = repair_core.wait_for_exact(ArtifactState.ANSWER_PENDING)
    return escalated.outcome, inconsistent.outcome, repair.outcome


def test_wait_rejects_invalid_policy_and_returns_terminal_states(
    wait_terminal_states_journey: tuple[WaitOutcome, WaitOutcome, WaitOutcome],
) -> None:
    """Bounded waits validate inputs and expose stopped or repair states immediately."""
    assert wait_terminal_states_journey == (
        WaitOutcome.ESCALATED,
        WaitOutcome.INCONSISTENT,
        WaitOutcome.REPAIR_REQUIRED,
    )


def test_wait_polls_through_the_counterpart_in_flight_publication(
    tmp_path: Path,
) -> None:
    """A current counterpart publication marker never aborts the bounded wait."""
    core, _, context, clock = _harness(tmp_path)
    record = core.start()
    core._mark_transition(
        record,
        IncompleteTransitionKind.PUBLISH_REQUEST,
        "request-step-3-round-1",
    )
    assert core.classify().state is ArtifactState.TRANSCRIPT_REPAIR_PENDING

    def _finish_publication() -> None:
        clock.after_sleep = None
        core.publish_request(_request(context, clock, 1), "Request one.")

    clock.after_sleep = _finish_publication
    result = core.wait_for_exact(ArtifactState.REQUEST_PENDING)

    assert result.outcome is WaitOutcome.FOUND
    assert result.observation.state is ArtifactState.REQUEST_PENDING


# eof
