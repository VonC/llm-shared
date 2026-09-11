"""Tests for specification-review precedence in ``pw skill``.

Step 3 keeps exchange parsing outside the main router. These tests replace the
focused adapter calls and pin forced question delegation, ordinary live resume,
marker-preserving fallback, and fail-closed diagnostics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_review as review
from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import Topic
from tools.review_exchange_state import ArtifactState

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def _topic(tmp_path: Path) -> Topic:
    """Create a plan-stage topic for routing tests."""
    docs = tmp_path / "docs"
    docs.mkdir()
    draft = docs / "draft.v1.0.0.routing.md"
    draft.write_text("# draft\n", encoding="utf-8")
    requirement = docs / "feature-request.v1.0.0.routing.md"
    design = docs / "design.v1.0.0.routing.md"
    plan = docs / "plan.v1.0.0.routing.md"
    requirement.write_text("## Requirement clarifications\n\n| Q01 | x |\n", encoding="utf-8")
    design.write_text("## Design decisions\n\n| Q01 | x |\n", encoding="utf-8")
    plan.write_text("## Open questions\n", encoding="utf-8")
    return Topic("v1.0.0", "routing", draft)


def _route(target: Path, state: ArtifactState) -> review.LiveSpecificationRoute:
    """Build one immutable route for command-selection tests."""
    return review.LiveSpecificationRoute(
        review.specification_context(target, None),
        state,
    )


def test_forced_spec_requestor_targets_the_current_question_document(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The explicit role emits its exact current specification target."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/plan.v1.0.0.routing.md"
    monkeypatch.setattr(
        review,
        "forced_specification_document",
        lambda *_args: target,
    )

    command = skill.forced_command(
        tmp_path,
        topic,
        "spec-review-requestor",
        {"CODEX_THREAD_ID": "x"},
    )

    assert command == (
        "$llm-shared:spec-review-requestor on docs/plan.v1.0.0.routing.md"
    )


def test_normal_routing_prefers_one_live_specification_exchange(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A live exchange wins over the ordinary consolidate command."""
    topic = _topic(tmp_path)
    target = tmp_path / "docs/design.v1.0.0.routing.md"
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: _route(target, ArtifactState.REQUEST_PENDING),
    )

    command = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})

    assert command == "/spec-reviewer on docs/design.v1.0.0.routing.md"


def test_reviewer_routing_names_the_umbrella_the_reviewer_must_pass(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An effort with an umbrella names it, so the reviewer can pass it.

    A reviewer builds its exchange context from this line. Without the
    umbrella on it, its core context omits one the published request and the
    coordination record both carry, and every operation reports `inconsistent`
    with a diagnostic that names neither the umbrella nor the missing flag.
    """
    topic = _topic(tmp_path)
    target = tmp_path / "docs/design.v1.0.0.routing.md"
    umbrella = tmp_path / "docs/draft.v1.0.0.umbrella.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: review.LiveSpecificationRoute(
            review.specification_context(target, umbrella),
            ArtifactState.REQUEST_PENDING,
        ),
    )

    command = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})

    assert command == (
        "/spec-reviewer on docs/design.v1.0.0.routing.md"
        " with umbrella docs/draft.v1.0.0.umbrella.md"
    )


def test_normal_routing_keeps_existing_command_without_live_exchange(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No live route leaves current disk-derived behavior intact."""
    topic = _topic(tmp_path)
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: None,
    )

    command = skill.next_command(tmp_path, topic, "routing", {"CLAUDECODE": "1"})

    assert command == (
        "/consolidate-then-review-ask-questions on docs/plan.v1.0.0.routing.md"
    )


def test_cli_reports_all_live_exchange_ambiguity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A routing ambiguity fails without selecting an ordinary command."""
    topic = _topic(tmp_path)
    monkeypatch.setattr(skill.git, "current_branch", lambda _root: "routing")
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: None)
    monkeypatch.setattr(
        skill.handoff,
        "resolve_current_topic",
        lambda *_args: topic,
    )
    monkeypatch.setattr(
        review,
        "live_specification_route",
        lambda *_args: (_ for _ in ()).throw(
            review.SpecificationReviewRoutingError("identity-a; identity-b"),
        ),
    )

    with pytest.raises(review.SpecificationReviewRoutingError) as raised:
        skill.run_skill(tmp_path, None, skill.HOST_CLAUDE)

    assert "identity-a; identity-b" in str(raised.value)


# eof
