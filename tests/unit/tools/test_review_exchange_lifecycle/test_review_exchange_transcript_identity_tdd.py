"""Failure-boundary tests for restarted-exchange transcript identity.

The main lifecycle module proves successful publication and repair. These
focused tests keep rejection and corrupt-marker branches out of that growing
journey file while exercising the same real core and store.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    _answer,
    _harness,
    _reach_gate,
    _request,
)
from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    IncompleteTransitionKind,
    ReviewExchangeError,
    ReviewRole,
)
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_transcript_identity import render_nature_completion_entry

if TYPE_CHECKING:
    from tools.review_exchange_core import ReviewExchangeCore
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_store import ReviewExchangeStore

    from .test_review_exchange_lifecycle_tdd import FakeTime


def test_nature_completion_identity_is_unique_by_role_and_exchange() -> None:
    """Completion headings and markers distinguish both durable dimensions."""
    requestor = render_nature_completion_entry(
        ReviewRole.REQUESTOR,
        2,
        LlmNature.CODEX,
        (Path(".reviews/a.request.md"),),
    )
    reviewer = render_nature_completion_entry(
        ReviewRole.REVIEWER,
        2,
        LlmNature.CLAUDE,
        (Path(".reviews/a.answer.md"),),
    )

    assert requestor.entry_id != reviewer.entry_id
    assert "LLM nature completion for requestor (exchange 2)" in requestor.markdown
    assert "review-entry-id: llm-nature-completion-requestor-exchange-2" in (
        requestor.markdown
    )


@pytest.mark.parametrize(
    ("role", "occurrence", "message"),
    [
        (ReviewRole.HUMAN, 1, "human role"),
        (ReviewRole.REQUESTOR, 0, "occurrence must be positive"),
    ],
)
def test_nature_completion_rejects_invalid_identity(
    role: ReviewRole,
    occurrence: int,
    message: str,
) -> None:
    """Completion entries fail closed for non-LLM roles and invalid occurrences."""
    with pytest.raises(ValueError, match=message):
        render_nature_completion_entry(role, occurrence, LlmNature.CODEX, ())


def test_publication_preserves_requestor_then_adds_reviewer_nature(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Request, answer, coordination, and transcript carry evolving snapshots."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    monkeypatch.delenv("CLAUDECODE", raising=False)
    monkeypatch.setenv("CODEX_THREAD_ID", "not-persisted")
    core.publish_request(_request(context, clock, 1), "Request summary.")

    request, _content = parse_envelope_markdown(
        store.paths.request.read_text(encoding="utf-8"),
    )
    assert request.role_natures.requestor is LlmNature.CODEX
    assert request.role_natures.reviewer is None

    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    monkeypatch.setenv("CLAUDECODE", "also-not-persisted")
    core.publish_answer(_answer(context, clock, 1), "Answer summary.")

    answer, _content = parse_envelope_markdown(
        store.paths.answer.read_text(encoding="utf-8"),
    )
    assert answer.role_natures.requestor is LlmNature.CODEX
    assert answer.role_natures.reviewer is LlmNature.CLAUDE
    record = store.read_coordination(required=True)
    assert record is not None
    assert record.role_natures == answer.role_natures
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "- Requestor LLM nature: codex" in transcript
    assert "- Reviewer LLM nature: claude" in transcript
    assert "not-persisted" not in transcript


@pytest.fixture
def pending_legacy_request(
    tmp_path: Path,
) -> tuple[ReviewExchangeCore, ReviewExchangeStore, ReviewContext, FakeTime]:
    """Prepare exchange two's legacy request outside the measured call phase."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    core.confirm("Commit")
    assert core.complete()
    core.start()
    core.publish_request(_request(context, clock, 1), "Exchange two request.")
    transcript = store.paths.transcript.read_text(encoding="utf-8")
    legacy = transcript.replace(" - Step 3 (exchange 2)", " - Step 3").replace(
        "request-step-3-round-1-exchange-2",
        "request-step-3-round-1",
    )
    store.paths.transcript.write_text(legacy, encoding="utf-8")
    return core, store, context, clock


def test_request_transcript_repair_requires_a_pending_request(tmp_path: Path) -> None:
    """An active authoring round has no published entry to replace."""
    core, _, _, _ = _harness(tmp_path)
    core.start()

    with pytest.raises(ReviewExchangeError, match="pending request"):
        core.repair_current_request_transcript("No pending request.")


@pytest.fixture
def later_round_request(
    tmp_path: Path,
) -> ReviewExchangeCore:
    """Publish a normal round-two request outside the measured call phase."""
    core, _, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "Round one request.")
    core.publish_answer(_answer(context, clock, 1), "Round one answer.")
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    core.publish_request(_request(context, clock, 2), "Round two request.")
    return core


def test_first_occurrence_in_a_later_round_is_not_an_exchange_collision(
    later_round_request: ReviewExchangeCore,
) -> None:
    """A normal round-two request cannot use the legacy collision repair."""
    with pytest.raises(ReviewExchangeError, match="no exchange collision"):
        later_round_request.repair_current_request_transcript("Round two replacement.")


@pytest.fixture
def different_step_identity_journey(tmp_path: Path) -> None:
    """Publish two plan steps outside the measured assertion call."""
    core, store, context, clock = _harness(tmp_path)
    _reach_gate(core, context, clock)
    core.confirm("Commit")
    assert core.complete()
    step_four_core, _, step_four, step_four_clock = _harness(
        tmp_path,
        implementation_step="4",
    )
    step_four_core.start()
    step_four_core.publish_request(
        _request(step_four, step_four_clock, 1),
        "Step four request.",
    )
    step_four_core.publish_answer(
        _answer(step_four, step_four_clock, 1),
        "Step four answer.",
    )

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "review-entry-id: request-step-3-round-1" in transcript
    assert "review-entry-id: answer-step-3-round-1" in transcript
    assert "review-entry-id: request-step-4-round-1" in transcript
    assert "review-entry-id: answer-step-4-round-1" in transcript
    assert "Step 4 (exchange 2)" not in transcript


def test_same_round_in_a_different_step_has_its_own_identity(
    different_step_identity_journey: None,
) -> None:
    """Code-review identities distinguish plan steps before counting exchanges."""
    assert different_step_identity_journey is None


def test_answer_occurrence_follows_a_restarted_request_without_prior_answer(
    tmp_path: Path,
) -> None:
    """A closed request-only exchange cannot desynchronize paired headings."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    core.publish_request(_request(context, clock, 1), "First request only.")
    store.paths.request.unlink()
    store.paths.coordination.unlink()

    core.start()
    core.publish_request(_request(context, clock, 1), "Restarted request.")
    core.publish_answer(_answer(context, clock, 1), "Restarted answer.")

    transcript = store.paths.transcript.read_text(encoding="utf-8")
    assert "by requestor - Step 3 (exchange 2)" in transcript
    assert "by reviewer - Step 3 (exchange 2)" in transcript
    assert "review-entry-id: answer-step-3-round-1-exchange-2" in transcript


def test_pending_legacy_repair_rejects_a_foreign_marker_identity(
    pending_legacy_request: tuple[
        ReviewExchangeCore,
        ReviewExchangeStore,
        ReviewContext,
        FakeTime,
    ],
) -> None:
    """A persisted repair marker cannot be retargeted to another entry."""
    core, store, _, _ = pending_legacy_request
    record = store.read_coordination(required=True)
    assert record is not None
    offset = store.current_entry_offset("request-step-3-round-1")
    store.write_coordination(
        replace(
            record,
            incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            transcript_entry_id="foreign-request-entry",
            transcript_offset=offset,
        ),
    )

    with pytest.raises(ReviewExchangeError, match="identity differs"):
        core.repair_current_request_transcript("Corrected exchange two request.")


def test_pending_legacy_repair_resumes_its_matching_marker(
    pending_legacy_request: tuple[
        ReviewExchangeCore,
        ReviewExchangeStore,
        ReviewContext,
        FakeTime,
    ],
) -> None:
    """A matching durable marker resumes the exact interrupted replacement."""
    core, store, _, _ = pending_legacy_request
    record = store.read_coordination(required=True)
    assert record is not None
    offset = store.current_entry_offset("request-step-3-round-1")
    store.write_coordination(
        replace(
            record,
            incomplete_transition=IncompleteTransitionKind.PUBLISH_REQUEST,
            transcript_entry_id="request-step-3-round-1-exchange-2",
            transcript_offset=offset,
        ),
    )

    repaired = core.repair_current_request_transcript("Corrected exchange two request.")

    assert repaired.incomplete_transition is None
    assert "request-step-3-round-1-exchange-2" in store.paths.transcript.read_text(
        encoding="utf-8",
    )


def test_legacy_entry_boundary_requires_a_final_entry_and_prior_footer(
    tmp_path: Path,
) -> None:
    """Boundary lookup fails closed without an exact final historical entry."""
    core, store, context, clock = _harness(tmp_path)
    core.start()
    with pytest.raises(ReviewExchangeError, match="not the final entry"):
        store.current_entry_offset("missing-request")

    core.publish_request(_request(context, clock, 1), "First request.")
    with pytest.raises(ReviewExchangeError, match="boundary is unavailable"):
        store.current_entry_offset("request-step-3-round-1")


# eof
