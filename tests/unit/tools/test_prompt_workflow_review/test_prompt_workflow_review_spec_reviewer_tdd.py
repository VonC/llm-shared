"""Tests for immutable state-aware specification reviewer routes.

Step 1 must expose the exact context and the state observed in the same routing
pass so command selection cannot classify the exchange a second time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow_review as review
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewContext,
)

from .test_prompt_workflow_review_tdd import _path, _topic_and_state

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

EXPECTED_CONTEXT_COUNT = 3

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def test_live_route_preserves_document_and_observed_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """One classification pass supplies both role-selection inputs."""
    topic, state = _topic_and_state(tmp_path)
    (tmp_path / "a.review-mode").write_text("", encoding="utf-8")
    calls = 0

    def classify(
        _root: Path,
        context: ReviewContext,
        _configuration: ReviewConfiguration,
    ) -> ArtifactState:
        nonlocal calls
        calls += 1
        return (
            ArtifactState.REQUEST_PENDING
            if context.document_path == _path(state.plan).resolve()
            else ArtifactState.IDLE
        )

    monkeypatch.setattr(review, "_classify_context", classify)

    route = review.live_specification_route(tmp_path, topic, state)

    assert route is not None
    assert route.context.document_path == _path(state.plan).resolve()
    assert route.state is ArtifactState.REQUEST_PENDING
    assert calls == EXPECTED_CONTEXT_COUNT


def test_document_compatibility_view_uses_the_state_aware_route(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Legacy requestor callers receive only the document without reclassification."""
    topic, state = _topic_and_state(tmp_path)
    context = review.specification_contexts(tmp_path, topic, state)[0]
    route = review.LiveSpecificationRoute(context, ArtifactState.ANSWER_PENDING)
    monkeypatch.setattr(review, "live_specification_route", lambda *_args: route)

    assert review.live_specification_document(tmp_path, topic, state) == context.document_path


# eof
