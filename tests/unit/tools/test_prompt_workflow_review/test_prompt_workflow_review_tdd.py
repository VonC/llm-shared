"""Tests for exact-path specification review routing.

Step 3 resolves only the requirement, design, and plan already selected for one
topic. These tests pin type mapping, live-state precedence, ambiguity handling,
marker gating, and the ban on scans or transcript reads.
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_review as review
from tools.prompt_workflow_models import Topic, WorkflowState
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewContext,
)

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def _path(value: Path | None) -> Path:
    """Return a required test-state path with its optional type narrowed."""
    assert value is not None
    return value


def _topic_and_state(tmp_path: Path) -> tuple[Topic, WorkflowState]:
    """Create one topic with all three exact specification candidates."""
    docs = tmp_path / "docs"
    docs.mkdir()
    umbrella = docs / "draft.v1.2.3.umbrella.md"
    umbrella.write_text("# umbrella\n", encoding="utf-8")
    draft = docs / "draft.v1.2.3.routing.md"
    draft.write_text(
        "# draft\n\n- Umbrella: docs/draft.v1.2.3.umbrella.md\n",
        encoding="utf-8",
    )
    paths = tuple(
        docs / name
        for name in (
            "feature-request.v1.2.3.routing.md",
            "design.v1.2.3.routing.md",
            "plan.v1.2.3.routing.md",
        )
    )
    for path in paths:
        path.write_text("# document\n", encoding="utf-8")
    topic = Topic(version="v1.2.3", slug="routing", draft_path=draft)
    state = WorkflowState(
        requirement=paths[0],
        design=paths[1],
        plan=paths[2],
        validation_plan=None,
        requirement_has_open_questions=False,
        design_has_open_questions=False,
        plan_has_open_questions=False,
        memory_step=None,
    )
    return topic, state


def test_contexts_use_exact_candidates_and_registered_design_mapping(
    tmp_path: Path,
) -> None:
    """Requirement, design, and plan become three exact shared contexts."""
    topic, state = _topic_and_state(tmp_path)

    contexts = review.specification_contexts(tmp_path, topic, state)

    assert tuple(context.document_path for context in contexts) == (
        _path(state.requirement).resolve(),
        _path(state.design).resolve(),
        _path(state.plan).resolve(),
    )
    assert tuple(context.identity.type_token for context in contexts) == (
        "feature-request",
        "design-specification",
        "plan",
    )
    assert all(
        context.umbrella_path == (tmp_path / "docs/draft.v1.2.3.umbrella.md")
        for context in contexts
    )


def test_contexts_accept_a_standalone_draft_without_an_umbrella(tmp_path: Path) -> None:
    """A topic draft with no umbrella marker produces standalone contexts."""
    topic, state = _topic_and_state(tmp_path)
    topic.draft_path.write_text("# standalone draft\n", encoding="utf-8")

    assert all(
        context.umbrella_path is None
        for context in review.specification_contexts(tmp_path, topic, state)
    )


@pytest.mark.parametrize(
    "marker",
    [
        "- Umbrella: docs/one.md\n- Umbrella: docs/two.md",
        "- Umbrella: ",
    ],
)
def test_contexts_reject_an_ambiguous_umbrella_marker(
    marker: str,
    tmp_path: Path,
) -> None:
    """Duplicate and empty umbrella declarations fail closed."""
    topic, state = _topic_and_state(tmp_path)
    topic.draft_path.write_text(f"# draft\n\n{marker}\n", encoding="utf-8")

    with pytest.raises(review.SpecificationReviewRoutingError, match="ambiguous"):
        review.specification_contexts(tmp_path, topic, state)


def test_contexts_reject_an_umbrella_outside_the_root(tmp_path: Path) -> None:
    """An umbrella marker cannot escape the resolved project root."""
    topic, state = _topic_and_state(tmp_path)
    topic.draft_path.write_text("# draft\n\n- Umbrella: ../outside.md\n", encoding="utf-8")

    with pytest.raises(review.SpecificationReviewRoutingError, match="outside"):
        review.specification_contexts(tmp_path, topic, state)


def test_contexts_reject_a_missing_umbrella(tmp_path: Path) -> None:
    """A declared in-root umbrella must be an existing file."""
    topic, state = _topic_and_state(tmp_path)
    topic.draft_path.write_text("# draft\n\n- Umbrella: docs/missing.md\n", encoding="utf-8")

    with pytest.raises(review.SpecificationReviewRoutingError, match="does not exist"):
        review.specification_contexts(tmp_path, topic, state)


def test_contexts_reject_a_document_from_another_topic(tmp_path: Path) -> None:
    """Resolved candidate identity must match the topic version and slug."""
    topic, state = _topic_and_state(tmp_path)
    mismatched = Topic("v9.9.9", topic.slug, topic.draft_path)

    with pytest.raises(review.SpecificationReviewRoutingError, match="differs"):
        review.specification_contexts(tmp_path, mismatched, state)


@pytest.mark.parametrize(
    "live_state",
    [
        ArtifactState.ROUND_IN_PROGRESS,
        ArtifactState.REQUEST_PENDING,
        ArtifactState.ANSWER_PENDING,
        ArtifactState.ABANDONED_REQUEST,
        ArtifactState.ABANDONED_ANSWER,
        ArtifactState.ESCALATED,
        ArtifactState.OWNING_ACTION_PENDING,
    ],
)
def test_live_document_routes_every_resumable_or_stopped_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    live_state: ArtifactState,
) -> None:
    """Any exact non-idle exchange takes precedence, including expired state."""
    topic, state = _topic_and_state(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")

    def classify(
        _root: Path,
        context: ReviewContext,
        _configuration: ReviewConfiguration,
    ) -> ArtifactState:
        document = context.document_path
        return (
            live_state
            if document == _path(state.design).resolve()
            else ArtifactState.IDLE
        )

    monkeypatch.setattr(review, "_classify_context", classify)

    assert review.live_specification_document(tmp_path, topic, state) == _path(
        state.design,
    )


def test_live_document_fails_closed_with_every_ambiguous_identity(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Two live exact candidates report both full identities and documents."""
    topic, state = _topic_and_state(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        review,
        "_classify_context",
        lambda _root, _context, _configuration: ArtifactState.REQUEST_PENDING,
    )

    with pytest.raises(review.SpecificationReviewRoutingError) as raised:
        review.live_specification_document(tmp_path, topic, state)

    message = str(raised.value)
    for token in (
        "specification/feature-request/v1.2.3/routing",
        "specification/design-specification/v1.2.3/routing",
        "specification/plan/v1.2.3/routing",
        "feature-request.v1.2.3.routing.md",
        "design.v1.2.3.routing.md",
        "plan.v1.2.3.routing.md",
    ):
        assert token in message


def test_marker_absence_preserves_ordinary_routing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No marker means no context classification and no review route."""
    topic, state = _topic_and_state(tmp_path)
    classify = monkeypatch.setattr(
        review,
        "_classify_context",
        lambda *_args: pytest.fail("marker absence must short-circuit"),
    )

    assert review.live_specification_document(tmp_path, topic, state) is None
    assert classify is None


def test_forced_document_requires_marker_and_one_open_question_document(
    tmp_path: Path,
) -> None:
    """Question delegation targets only one exact open specification."""
    topic, state = _topic_and_state(tmp_path)
    _path(state.design).write_text("# design\n\n## Open questions\n", encoding="utf-8")
    state = replace(state, design_has_open_questions=True)
    assert review.forced_specification_document(tmp_path, topic, state) is None

    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    assert review.forced_specification_document(tmp_path, topic, state) == _path(
        state.design,
    )


def test_forced_document_prefers_an_existing_live_exchange(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Explicit delegation resumes live authority before new questions."""
    topic, state = _topic_and_state(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    context = review.specification_contexts(tmp_path, topic, state)[0]
    monkeypatch.setattr(
        review,
        "_one_live_route",
        lambda *_args: review.LiveSpecificationRoute(
            context,
            ArtifactState.REQUEST_PENDING,
        ),
    )

    assert review.forced_specification_document(tmp_path, topic, state) == context.document_path


def test_forced_document_rejects_multiple_open_question_documents(
    tmp_path: Path,
) -> None:
    """Forced routing never guesses between two question-bearing candidates."""
    topic, state = _topic_and_state(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    state = replace(
        state,
        requirement_has_open_questions=True,
        design_has_open_questions=True,
    )

    with pytest.raises(review.SpecificationReviewRoutingError) as raised:
        review.forced_specification_document(tmp_path, topic, state)

    assert "feature-request.v1.2.3.routing.md" in str(raised.value)
    assert "design.v1.2.3.routing.md" in str(raised.value)


def test_module_has_a_constant_candidate_set_and_no_scan_or_transcript_access() -> None:
    """The routing adapter stays on bounded exact paths."""
    source = inspect.getsource(review)
    for forbidden in ("rglob", ".glob(", "iterdir", "review.feature-request"):
        assert forbidden not in source
    assert "state.requirement" in source
    assert "state.design" in source
    assert "state.plan" in source
    assert ".transcript" not in source


# eof
