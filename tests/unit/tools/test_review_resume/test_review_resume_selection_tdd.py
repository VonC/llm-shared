"""Reviewer discovery selects actionable requests without hiding safety gates."""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_resume.test_review_exchange_cli_resume_tdd import (
    FakeEntry,
)
from tools import review_exchange_cli_resume as subject
from tools.review_exchange_cli_parser import parser
from tools.review_exchange_models import ArtifactState, ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

_STOP_EXIT = 3


@pytest.fixture
def review_status(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Inject status evidence while exercising the real CLI selection and role policy."""
    status = SimpleNamespace(
        outcome=subject.ReviewStatusOutcome.TRUSTWORTHY, exchanges=(),
    )
    monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
    monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
    return status


def _inspect(root: Path, *arguments: str) -> tuple[dict[str, Any], int]:
    """Run non-mutating inspection with an explicit host independent of the runner."""
    args = parser().parse_args([
        "resume-inspect", "--trusted-host-hint", "claude", *arguments,
    ])
    return subject.execute_resume_operation(args, root)


@pytest.mark.parametrize("state", [ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST])
def test_reviewer_selects_request_beside_answered_plan(
    tmp_path: Path, review_status: SimpleNamespace, state: ArtifactState,
) -> None:
    """The screenshot scenario resumes its design directly, even with an expired lease."""
    request = FakeEntry(state)
    request.reviewed_document = "docs/design.v0.11.0.resume.md"
    review_status.exchanges = (FakeEntry(ArtifactState.CONVERGENCE_GATE), request)
    if state is ArtifactState.ABANDONED_REQUEST:
        review_status.outcome = subject.ReviewStatusOutcome.UNTRUSTWORTHY

    payload, code = _inspect(tmp_path, "--role", "reviewer")

    assert code == 0
    assert payload["action"] == "review-request"
    assert [item["document"] for item in payload["candidates"]] == [request.reviewed_document]
    assert "ownership_token" not in payload


@pytest.mark.parametrize("state", [
    ArtifactState.ANSWER_PENDING, ArtifactState.ABANDONED_ANSWER,
    ArtifactState.CONVERGENCE_GATE, ArtifactState.OWNING_ACTION_PENDING,
    ArtifactState.ROUND_IN_PROGRESS, ArtifactState.ABANDONED_MID_ROUND,
])
def test_reviewer_without_requests_waits_without_selecting_an_exchange(
    tmp_path: Path, review_status: SimpleNamespace, state: ArtifactState,
) -> None:
    """Requestor work never sends the reviewer into an irrelevant choice or claim."""
    review_status.exchanges = (FakeEntry(state), FakeEntry(ArtifactState.CONVERGENCE_GATE))

    payload, code = _inspect(tmp_path, "--role", "reviewer")

    assert code == 0
    assert payload["action"] == "wait-any-request"
    assert payload["candidates"] == []
    assert payload["identity"] is None


def test_multiple_pending_requests_still_require_selection(
    tmp_path: Path, review_status: SimpleNamespace,
) -> None:
    """Filtering requestor work does not choose arbitrarily between genuine requests."""
    first, second = FakeEntry(), FakeEntry()
    second.reviewed_document = "docs/design.v0.11.0.second.md"
    review_status.exchanges = (first, FakeEntry(ArtifactState.CONVERGENCE_GATE), second)

    payload, code = _inspect(tmp_path, "--role", "reviewer")

    assert code == _STOP_EXIT
    assert payload["outcome"] == "exchange-selection-required"
    assert [item["document"] for item in payload["candidates"]] == [
        first.reviewed_document, second.reviewed_document,
    ]


@pytest.mark.parametrize("arguments", [(), ("--role", "requestor")])
def test_other_role_selection_keeps_all_exchanges(
    tmp_path: Path, review_status: SimpleNamespace, arguments: tuple[str, ...],
) -> None:
    """An unspecified role or requestor keeps the existing ambiguity boundary."""
    review_status.exchanges = (FakeEntry(), FakeEntry(ArtifactState.CONVERGENCE_GATE))

    payload, code = _inspect(tmp_path, *arguments)

    assert code == _STOP_EXIT
    assert payload["outcome"] == "exchange-selection-required"
    assert len(payload["candidates"]) == len(review_status.exchanges)


def test_explicit_reviewer_document_is_not_replaced_by_another_request(
    tmp_path: Path, review_status: SimpleNamespace,
) -> None:
    """A selected answered plan remains exact rather than silently switching to design."""
    plan = FakeEntry(ArtifactState.CONVERGENCE_GATE)
    request = FakeEntry()
    request.reviewed_document = "docs/design.v0.11.0.resume.md"
    review_status.exchanges = (plan, request)

    payload, code = _inspect(tmp_path, "--role", "reviewer", "--document", plan.reviewed_document)

    assert code == 0
    assert payload["action"] == "wait-any-request"
    assert [item["document"] for item in payload["candidates"]] == [plan.reviewed_document]


def test_selected_request_still_checks_reviewer_identity(
    tmp_path: Path, review_status: SimpleNamespace,
) -> None:
    """Automatic selection cannot bypass a conflicting recorded reviewer host."""
    request = FakeEntry()
    request.reviewer_llm_nature.value = subject.LlmNature.CODEX
    review_status.exchanges = (request, FakeEntry(ArtifactState.CONVERGENCE_GATE))

    payload, code = _inspect(tmp_path, "--role", "reviewer")

    assert code == _STOP_EXIT
    assert payload["outcome"] == "confirmation-required"


@pytest.mark.parametrize("state", [
    ArtifactState.ESCALATED, ArtifactState.INCONSISTENT,
    ArtifactState.TRANSCRIPT_REPAIR_PENDING,
    ArtifactState.INTERRUPTED_ANSWER_PUBLICATION,
])
def test_damaged_neighbor_blocks_before_reviewer_filtering(
    tmp_path: Path, review_status: SimpleNamespace, state: ArtifactState,
) -> None:
    """A usable request cannot conceal damaged or stopped evidence elsewhere in the home."""
    review_status.outcome = subject.ReviewStatusOutcome.UNTRUSTWORTHY
    review_status.exchanges = (FakeEntry(ArtifactState.ABANDONED_REQUEST), FakeEntry(state))

    with pytest.raises(ReviewExchangeError, match="trustworthy review status"):
        _inspect(tmp_path, "--role", "reviewer")


@pytest.mark.parametrize("neighbor", [None, ArtifactState.REQUEST_PENDING, ArtifactState.ABANDONED_REQUEST])
def test_active_answer_publication_blocks_before_reviewer_filtering(
    tmp_path: Path, review_status: SimpleNamespace, neighbor: ArtifactState | None,
) -> None:
    """Discovery cannot hide an incomplete publication, even beside a recoverable request."""
    publishing = FakeEntry(ArtifactState.ANSWER_PUBLICATION_IN_PROGRESS)
    review_status.exchanges = (publishing,) if neighbor is None else (publishing, FakeEntry(neighbor))
    if neighbor is ArtifactState.ABANDONED_REQUEST:
        review_status.outcome = subject.ReviewStatusOutcome.UNTRUSTWORTHY

    with pytest.raises(ReviewExchangeError, match="blocked while answer publication is in progress"):
        _inspect(tmp_path, "--role", "reviewer")
