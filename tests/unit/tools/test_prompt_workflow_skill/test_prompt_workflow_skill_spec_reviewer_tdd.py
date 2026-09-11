"""Tests for ordinary and forced specification reviewer command routing.

Step 1 assigns pending requests to the reviewer while retaining all writer and
cold-recovery states in the requestor role.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_review as review
from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import Topic
from tools.review_exchange_models import ArtifactState

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def _topic(tmp_path: Path) -> Topic:
    """Create a settled plan-stage topic for command tests."""
    docs = tmp_path / "docs"
    docs.mkdir()
    draft = docs / "draft.v1.0.0.routing.md"
    draft.write_text("# draft\n", encoding="utf-8")
    (docs / "feature-request.v1.0.0.routing.md").write_text("# requirement\n", encoding="utf-8")
    (docs / "design.v1.0.0.routing.md").write_text("# design\n", encoding="utf-8")
    (docs / "plan.v1.0.0.routing.md").write_text("# plan\n", encoding="utf-8")
    return Topic("v1.0.0", "routing", draft)


def _route(target: Path, state: ArtifactState) -> review.LiveSpecificationRoute:
    """Build one exact immutable route."""
    return review.LiveSpecificationRoute(review.specification_context(target, None), state)


@pytest.mark.parametrize(
    ("state", "role"),
    [
        (ArtifactState.REQUEST_PENDING, "spec-reviewer"),
        (ArtifactState.ABANDONED_REQUEST, "spec-review-requestor"),
        (ArtifactState.ANSWER_PENDING, "spec-review-requestor"),
        (ArtifactState.CONVERGENCE_GATE, "spec-review-requestor"),
    ],
)
def test_normal_route_maps_state_to_one_owner(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    state: ArtifactState,
    role: str,
) -> None:
    """Pending work is reviewer-owned and writer states remain requestor-owned."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/plan.v1.0.0.routing.md"
    monkeypatch.setattr(review, "live_specification_route", lambda *_args: _route(target, state))

    command = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})

    assert command == f"/{role} on docs/plan.v1.0.0.routing.md"


def test_forced_reviewer_accepts_only_a_pending_request(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Explicit reviewer routing cannot activate writer work."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/plan.v1.0.0.routing.md"
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: _route(target, ArtifactState.REQUEST_PENDING),
    )

    assert skill.forced_command(
        tmp_path,
        topic,
        "spec-reviewer",
        {"CODEX_THREAD_ID": "x"},
    ) == "$llm-shared:spec-reviewer on docs/plan.v1.0.0.routing.md"


@pytest.mark.parametrize("route_state", [None, ArtifactState.ANSWER_PENDING])
def test_forced_reviewer_rejects_absent_and_writer_owned_routes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    route_state: ArtifactState | None,
) -> None:
    """Explicit reviewer routing returns no command without pending authority."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/plan.v1.0.0.routing.md"
    route = None if route_state is None else _route(target, route_state)
    monkeypatch.setattr(review, "live_specification_route", lambda *_args: route)

    assert skill.forced_command(
        tmp_path,
        topic,
        "spec-reviewer",
        {"CLAUDECODE": "1"},
    ) is None


def test_forced_reviewer_reports_the_cold_requestor_reclaim_handoff(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A cold abandoned request fails closed with its exact requestor handoff."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/plan.v1.0.0.routing.md"
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: _route(target, ArtifactState.ABANDONED_REQUEST),
    )

    with pytest.raises(review.SpecificationReviewRoutingError) as raised:
        skill.forced_command(tmp_path, topic, "spec-reviewer", {"CLAUDECODE": "1"})

    assert "spec-review-requestor reclaim" in str(raised.value)
    assert "specification/plan/v1.0.0/routing" in str(raised.value)


# eof
