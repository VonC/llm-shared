"""Tests for ordinary and forced implementation code-reviewer routing."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_code_review as code_review
from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import Topic
from tools.review_exchange_models import (
    ArtifactState,
    ExchangeIdentity,
    ReviewContext,
    ReviewFamily,
)

if TYPE_CHECKING:
    from pathlib import Path

# Test doubles intentionally replace functions with smaller signatures.
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def _topic(tmp_path: Path) -> Topic:
    """Create the exact plan topic used by the route renderer."""
    docs = tmp_path / "docs"
    docs.mkdir()
    draft = docs / "draft.v1.0.0.routing.md"
    plan = docs / "plan.v1.0.0.routing.md"
    draft.write_text("# draft\n", encoding="utf-8")
    plan.write_text("# plan\n", encoding="utf-8")
    return Topic("v1.0.0", "routing", draft)


def _route(
    tmp_path: Path,
    state: ArtifactState,
    actor: code_review.CodeReviewActor,
) -> code_review.CodeReviewRoute:
    """Build one exact immutable code-review route."""
    context = ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v1.0.0", "routing"),
        tmp_path / "docs/plan.v1.0.0.routing.md",
        None,
        "5",
    )
    return code_review.CodeReviewRoute(context, state, actor)


@pytest.mark.parametrize(
    ("state", "actor", "role"),
    [
        (ArtifactState.REQUEST_PENDING, code_review.CodeReviewActor.REVIEWER, "code-reviewer"),
        (ArtifactState.ROUND_IN_PROGRESS, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (ArtifactState.ABANDONED_REQUEST, code_review.CodeReviewActor.REVIEWER, "code-reviewer"),
        (ArtifactState.ANSWER_PENDING, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (ArtifactState.ABANDONED_ANSWER, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (ArtifactState.CONVERGENCE_GATE, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (ArtifactState.OWNING_ACTION_PENDING, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (ArtifactState.ESCALATED, code_review.CodeReviewActor.REQUESTOR, "code-review-requestor"),
        (
            ArtifactState.TRANSCRIPT_REPAIR_PENDING,
            code_review.CodeReviewActor.REQUESTOR,
            "code-review-requestor",
        ),
    ],
)
def test_ordinary_route_uses_the_single_typed_actor(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    state: ArtifactState,
    actor: code_review.CodeReviewActor,
    role: str,
) -> None:
    """Ordinary routing assigns active or reclaimable requests to the reviewer."""
    topic = _topic(tmp_path)
    route = _route(tmp_path, state, actor)
    monkeypatch.setattr(skill.steps, "compute_state", lambda *_args: object())
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: object())
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: route)

    command = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})

    assert command == f"/{role} on docs/plan.v1.0.0.routing.md step 5"


def test_forced_reviewer_accepts_only_the_exact_pending_route(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The explicit reviewer role cannot enter requestor-owned work."""
    topic = _topic(tmp_path)
    pending = _route(
        tmp_path,
        ArtifactState.REQUEST_PENDING,
        code_review.CodeReviewActor.REVIEWER,
    )
    monkeypatch.setattr(skill.steps, "compute_state", lambda *_args: object())
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: object())
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: pending)

    assert skill.forced_command(
        tmp_path,
        topic,
        "code-reviewer",
        {"CODEX_THREAD_ID": "x"},
    ) == "$llm-shared:code-reviewer on docs/plan.v1.0.0.routing.md step 5"

    writer = _route(
        tmp_path,
        ArtifactState.ANSWER_PENDING,
        code_review.CodeReviewActor.REQUESTOR,
    )
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: writer)
    assert skill.forced_command(
        tmp_path,
        topic,
        "code-reviewer",
        {"CLAUDECODE": "1"},
    ) is None
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: None)
    assert skill.forced_command(
        tmp_path,
        topic,
        "code-reviewer",
        {"CLAUDECODE": "1"},
    ) is None


def test_forced_requestor_accepts_only_a_requestor_owned_route(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The explicit requestor role renders its exact plan and step."""
    topic = _topic(tmp_path)
    writer = _route(
        tmp_path,
        ArtifactState.ANSWER_PENDING,
        code_review.CodeReviewActor.REQUESTOR,
    )
    monkeypatch.setattr(skill.steps, "compute_state", lambda *_args: object())
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: object())
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: writer)

    assert skill.forced_command(
        tmp_path,
        topic,
        "code-review-requestor",
        {"CODEX_THREAD_ID": "x"},
    ) == (
        "$llm-shared:code-review-requestor on "
        "docs/plan.v1.0.0.routing.md step 5"
    )


def test_forced_reviewer_accepts_a_cold_abandoned_request(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Cold lease recovery enters the reviewer that owns the request."""
    topic = _topic(tmp_path)
    abandoned = _route(
        tmp_path,
        ArtifactState.ABANDONED_REQUEST,
        code_review.CodeReviewActor.REVIEWER,
    )
    monkeypatch.setattr(skill.steps, "compute_state", lambda *_args: object())
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: object())
    monkeypatch.setattr(code_review, "resolve_code_review_route", lambda *_args: abandoned)

    assert skill.forced_command(
        tmp_path,
        topic,
        "code-reviewer",
        {"CLAUDECODE": "1"},
    ) == "/code-reviewer on docs/plan.v1.0.0.routing.md step 5"


# eof
