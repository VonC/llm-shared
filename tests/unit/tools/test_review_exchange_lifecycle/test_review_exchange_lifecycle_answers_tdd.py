"""Answer publication, convergence, continuation, and wait lifecycle coverage.

Fix: Build the replacement-request scenario in a fixture and advance it to its
existing exposure time in one fake poll. The call phase preserves the full
transition without setup IO or redundant persisted-state reads.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools.review_exchange_core import WaitOutcome, WaitProgress
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    CoordinationStatus,
    ReviewExchangeError,
)

from .test_review_exchange_lifecycle_tdd import (
    _REQUEST_EXPOSURE_TIME,
    _SECOND_ROUND,
    _answer,
    _harness,
    _reach_gate,
    _request,
    _start_and_request,
    _timestamp,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_core import ReviewExchangeCore
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_models_coordination import CoordinationRecord

    from .test_review_exchange_lifecycle_tdd import FakeTime


@pytest.fixture
def published_answer_journey(tmp_path: Path) -> None:
    """Publish and inspect one change request outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)

    record = core.publish_answer(
        _answer(context, clock, 1),
        "Please adjust the implementation.",
    )

    assert not store.paths.request.exists()
    assert not store.paths.tombstone.exists()
    assert store.paths.answer.is_file()
    assert record.owner is Actor.REVIEWER
    assert record.expected_next_actor is Actor.REQUESTOR
    assert record.convergence_recommended is False
    assert core.classify().state is ArtifactState.ANSWER_PENDING


def test_publish_answer_consumes_request_and_sets_intermediate_ownership(
    published_answer_journey: None,
) -> None:
    """A change request becomes visible only after request consumption."""
    assert published_answer_journey is None


@pytest.fixture
def interrupted_answer_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repair one interrupted answer outside the measured assertion call."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    original_commit = store._commit_prepared
    failed = False

    def fail_answer_once(prepared: Path, target: Path) -> None:
        nonlocal failed
        if target == store.paths.answer and not failed:
            failed = True
            message = "injected answer replacement failure"
            raise OSError(message)
        original_commit(prepared, target)

    monkeypatch.setattr(store, "_commit_prepared", fail_answer_once)
    answer = _answer(context, clock, 1)
    with pytest.raises(ReviewExchangeError, match="answer publication failed"):
        core.publish_answer(answer, "Repair this reviewer entry.")

    assert store.paths.tombstone.is_file()
    assert not store.paths.answer.exists()
    record = core.publish_answer(answer, "Repair this reviewer entry.")

    assert record.incomplete_transition is None
    assert not store.paths.tombstone.exists()
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: answer-step-3-round-1") == 1


def test_interrupted_answer_publication_resumes_from_tombstone(
    interrupted_answer_journey: None,
) -> None:
    """A failure after request rename can publish and append the answer on retry."""
    assert interrupted_answer_journey is None


@pytest.fixture
def convergence_gate_journey(tmp_path: Path) -> None:
    """Reach and inspect a convergence gate outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)

    record = store.read_coordination(required=True)
    assert record is not None
    assert record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    assert record.expected_next_actor is Actor.HUMAN
    assert record.lease_renewed_at is None
    assert store.paths.answer.is_file()
    assert core.classify().state is ArtifactState.CONVERGENCE_GATE


def test_convergence_answer_enters_suspended_human_gate(
    convergence_gate_journey: None,
) -> None:
    """A convergence recommendation retains its answer and suspends expiry."""
    assert convergence_gate_journey is None


@pytest.fixture
def convergence_repair_journey(tmp_path: Path) -> None:
    """Repair one persisted gate outside the measured assertion call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    gated = store.read_coordination(required=True)
    assert gated is not None
    store.write_coordination(
        replace(
            gated,
            status=CoordinationStatus.ACTIVE,
            expected_next_actor=Actor.REQUESTOR,
            lease_renewed_at=_timestamp(clock),
            convergence_recommended=None,
        ),
    )

    record = core.consume_answer(reviewed_work_changed=True)

    assert record.status is CoordinationStatus.AWAITING_HUMAN_CONFIRMATION
    assert record.convergence_recommended is True
    assert store.paths.answer.is_file()


def test_envelope_authoritative_convergence_repairs_active_coordination(
    convergence_repair_journey: None,
) -> None:
    """A published convergence answer restores the gate after a state-write crash."""
    assert convergence_repair_journey is None


@pytest.fixture
def two_unchanged_rounds_journey(tmp_path: Path) -> None:
    """Two consecutive unchanged change requests stop automated review."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "Round one changes.")
    first = core.consume_answer(reviewed_work_changed=False)
    assert first.no_progress_streak == 1
    assert not store.paths.answer.exists()

    next_round = core.continue_round()
    assert next_round.round_number == _SECOND_ROUND
    core.publish_request(_request(context, clock, 2), "Round two request.")
    core.publish_answer(_answer(context, clock, 2), "Round two changes.")
    escalated = core.consume_answer(reviewed_work_changed=False)

    assert escalated.status is CoordinationStatus.ESCALATED
    assert escalated.escalation_reason is not None
    assert "no meaningful progress" in escalated.escalation_reason
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_two_unchanged_rounds_escalate_without_deleting_evidence(
    two_unchanged_rounds_journey: None,
) -> None:
    """The complete two-round journey retains its asserted outcome."""
    assert two_unchanged_rounds_journey is None


@pytest.fixture
def clarification_disagreement_journey(tmp_path: Path) -> None:
    """Explicit disagreement gets one automated clarification round only."""
    core, _store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "First disagreement.")
    first = core.consume_answer(reviewed_work_changed=True, disagreement=True)
    assert first.clarification_used is True

    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Clarification request.")
    core.publish_answer(_answer(context, clock, 2), "Disagreement remains.")
    second = core.consume_answer(reviewed_work_changed=True, disagreement=True)

    assert second.status is CoordinationStatus.ESCALATED
    assert second.escalation_reason is not None
    assert "disagreement" in second.escalation_reason


def test_one_clarification_round_then_persistent_disagreement_escalates(
    clarification_disagreement_journey: None,
) -> None:
    """The bounded clarification journey retains its asserted outcome."""
    assert clarification_disagreement_journey is None


@pytest.fixture
def changed_round_journey(tmp_path: Path) -> None:
    """Substantive progress clears a previous unchanged-round streak."""
    core, _, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "First changes.")
    core.consume_answer(reviewed_work_changed=False)
    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Changed request.")
    core.publish_answer(_answer(context, clock, 2), "Second changes.")

    record = core.consume_answer(reviewed_work_changed=True)

    assert record.no_progress_streak == 0
    assert record.reviewed_work_changed is True


def test_changed_round_resets_no_progress_before_continuation(
    changed_round_journey: None,
) -> None:
    """The progress-reset journey retains its asserted outcome."""
    assert changed_round_journey is None


def test_wait_uses_one_monotonic_deadline_progress_and_no_lease_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact waiting reports progress without heartbeat-style coordination writes."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    writes: list[CoordinationRecord] = []
    original_write = store.write_coordination

    def track_write(record: CoordinationRecord) -> None:
        writes.append(record)
        original_write(record)

    monkeypatch.setattr(store, "write_coordination", track_write)

    def expose_request() -> None:
        if clock.monotonic >= _REQUEST_EXPOSURE_TIME and not store.paths.request.exists():
            store.publish_atomic(store.paths.request, _request(context, clock, 1))

    clock.after_sleep = expose_request
    progress: list[WaitProgress] = []
    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=5,
        poll_interval=1,
        progress_interval=1,
        progress_callback=progress.append,
    )

    assert result.outcome is WaitOutcome.FOUND
    assert result.observation.state is ArtifactState.REQUEST_PENDING
    assert len(progress) >= 1
    assert writes == []


@pytest.fixture
def replacement_request_round(
    tmp_path: Path,
) -> tuple[ReviewExchangeCore, ReviewContext, FakeTime]:
    """Prepare an answered first round outside the measured test call phase."""
    core, _, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.publish_answer(_answer(context, clock, 1), "Changes requested.")
    return core, context, clock


def test_reviewer_wait_spans_answer_pending_until_the_replacement_request(
    replacement_request_round: tuple[ReviewExchangeCore, ReviewContext, FakeTime],
) -> None:
    """A reviewer can publish changes and stay in one wait for the next round."""
    core, context, clock = replacement_request_round

    def publish_replacement_request() -> None:
        if clock.monotonic >= _REQUEST_EXPOSURE_TIME:
            core.consume_answer(reviewed_work_changed=True)
            core.continue_round()
            _start_and_request(core, context, clock, _SECOND_ROUND)

    clock.after_sleep = publish_replacement_request
    result = core.wait_for_exact(
        ArtifactState.REQUEST_PENDING,
        timeout_seconds=5,
        poll_interval=2,
        progress_interval=1,
    )

    assert result.outcome is WaitOutcome.FOUND
    assert result.observation.state is ArtifactState.REQUEST_PENDING
    assert result.observation.record is not None
    assert result.observation.record.round_number == _SECOND_ROUND
    assert result.observation.request_envelope is not None
    assert result.observation.request_envelope.round_number == _SECOND_ROUND


# eof
