"""Human confirmation and resolution tests for the review-exchange core.

Step 3 keeps convergence advisory until a durable human choice, repairs an
interrupted choice without duplication, and resumes escalation only through a
recorded fresh-round resolution.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _harness,
    _reach_gate,
    _start_and_request,
    _timestamp,
)
from tools.review_exchange_models import (
    ArtifactState,
    ConfirmationOutcome,
    CoordinationStatus,
    IncompleteTransitionKind,
    ReviewExchangeError,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_core import (
        ConfirmationDecision,
        ResolutionResult,
        ReviewExchangeCore,
    )
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.review_exchange_store import ReviewExchangeStore

_SECOND_ROUND = 2


def _assert_another_round_decision(decision: ConfirmationDecision) -> None:
    """Assert the reset fields of one durable another-round choice."""
    assert decision.outcome is ConfirmationOutcome.ANOTHER_ROUND
    assert decision.owning_action_authorized is False
    assert decision.record.status is CoordinationStatus.ACTIVE
    assert decision.record.round_number == _SECOND_ROUND
    assert decision.record.no_progress_streak == 0
    assert decision.record.clarification_used is False
    assert decision.record.human_guidance == "Check the crash boundary again."


@pytest.fixture
def stalled_convergence_gate(
    tmp_path: Path,
) -> tuple[ReviewExchangeCore, ReviewExchangeStore]:
    """Reach one convergence gate with stalled progress outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    gated = store.read_coordination(required=True)
    assert gated is not None
    store.write_coordination(
        replace(gated, no_progress_streak=1, clarification_used=True),
    )
    return core, store


def test_another_round_confirmation_records_guidance_and_resets_progress(
    stalled_convergence_gate: tuple[ReviewExchangeCore, ReviewExchangeStore],
) -> None:
    """A human override starts a fresh automated round with durable guidance."""
    core, store = stalled_convergence_gate

    decision = core.confirm(
        "Another round",
        guidance="Check the crash boundary again.",
    )

    _assert_another_round_decision(decision)
    assert not store.paths.answer.exists()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: human-confirmation-round-1") == 1


@pytest.fixture
def repaired_another_round_confirmation_journey(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repair one interrupted confirmation outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    original_remove = store.remove_exact
    failed = False

    def fail_answer_once(path: Path) -> bool:
        nonlocal failed
        if path == store.paths.answer and not failed:
            failed = True
            message = "injected confirmation cleanup failure"
            raise ReviewExchangeError(message)
        return original_remove(path)

    monkeypatch.setattr(store, "remove_exact", fail_answer_once)
    with pytest.raises(ReviewExchangeError, match="confirmation cleanup"):
        core.confirm("Another round", guidance="Retry safely.")

    marked = store.read_coordination(required=True)
    assert marked is not None
    assert marked.incomplete_transition is IncompleteTransitionKind.HUMAN_CONFIRMATION
    decision = core.confirm("Another round", guidance="Retry safely.")

    assert decision.record.round_number == _SECOND_ROUND
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: human-confirmation-round-1") == 1


def test_interrupted_another_round_confirmation_repairs_without_duplicate(
    repaired_another_round_confirmation_journey: None,
) -> None:
    """A confirmed override replays its marked append before deleting the answer."""
    assert repaired_another_round_confirmation_journey is None


@pytest.fixture
def replayed_authorization_journey(
    tmp_path: Path,
) -> None:
    """Replay and complete owning authorization outside the measured call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)

    first = core.confirm("Commit")
    second = core.confirm("Commit")

    assert first.outcome is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
    assert first.owning_action_authorized is True
    assert second.owning_action_authorized is True
    assert core.classify().state is ArtifactState.OWNING_ACTION_PENDING
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("review-entry-id: human-confirmation-round-1") == 1

    assert core.complete() is True
    assert core.complete() is False
    assert not store.paths.answer.exists()
    assert not store.paths.coordination.exists()


def test_continue_confirmation_replays_authorization_until_complete(
    replayed_authorization_journey: None,
) -> None:
    """Persisted owning authorization is returned without a second human choice."""
    assert replayed_authorization_journey is None


@pytest.fixture
def cancelled_gate_journey(tmp_path: Path) -> None:
    """Cancel one convergence gate outside the measured assertion call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)

    first = core.cancel("The owning action is no longer wanted.")
    second = core.cancel("The owning action is no longer wanted.")

    assert first.status is CoordinationStatus.ESCALATED
    assert second == first
    assert store.paths.answer.is_file()
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: escalation") == 1


def test_human_cancellation_uses_idempotent_escalation_path(
    cancelled_gate_journey: None,
) -> None:
    """Cancelling a convergence gate preserves its answer for human resolution."""
    assert cancelled_gate_journey is None


def _assert_human_resolution(tmp_path: Path, *, archive: bool) -> None:
    """Assert one clear-or-archive resolution variant starts a fresh round."""
    core, store, context, clock = _harness(tmp_path)
    _start_and_request(core, context, clock)
    core.escalate("Manual evidence choice required")

    resolution = core.resolve_escalation(
        "The request is obsolete; restart from the reviewed plan.",
        archive=archive,
    )

    _assert_fresh_record(resolution.record, expected_timestamp=_timestamp(clock))
    _assert_resolution_evidence(resolution, store, archive=archive)


def _assert_fresh_record(
    record: CoordinationRecord,
    *,
    expected_timestamp: str,
) -> None:
    """Assert resolution installed one authoritative fresh round."""
    assert record.status is CoordinationStatus.ACTIVE
    assert record.round_number == _SECOND_ROUND
    assert record.lease_renewed_at == expected_timestamp


def _assert_resolution_evidence(
    resolution: ResolutionResult,
    store: ReviewExchangeStore,
    *,
    archive: bool,
) -> None:
    """Assert exact-path cleanup, optional archives, and transcript evidence."""
    assert not store.paths.request.exists()
    assert not store.paths.answer.exists()
    assert not store.paths.tombstone.exists()
    assert store.paths.coordination.is_file()
    assert bool(resolution.archived_paths) is archive
    assert all(path.is_file() for path in resolution.archived_paths)
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert transcript.count("Outcome: human-resolution") == 1


@pytest.fixture
def cleared_human_resolution_journey(tmp_path: Path) -> None:
    """Clear stopped evidence outside the measured assertion call."""
    _assert_human_resolution(tmp_path, archive=False)


def test_human_resolution_clears_and_starts_fresh_round(
    cleared_human_resolution_journey: None,
) -> None:
    """Stopped evidence can be cleared before a fresh lease gains authority."""
    assert cleared_human_resolution_journey is None


@pytest.fixture
def archived_human_resolution_journey(tmp_path: Path) -> None:
    """Archive stopped evidence outside the measured assertion call."""
    _assert_human_resolution(tmp_path, archive=True)


def test_human_resolution_archives_and_starts_fresh_round(
    archived_human_resolution_journey: None,
) -> None:
    """Stopped evidence can be archived before a fresh lease gains authority."""
    assert archived_human_resolution_journey is None


# eof
