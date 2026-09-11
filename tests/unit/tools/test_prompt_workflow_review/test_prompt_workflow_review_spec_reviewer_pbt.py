"""Exhaustive checks for immutable specification reviewer route snapshots.

Each artifact state is a separate test call so filesystem routing work stays
below the duration floor while still covering the complete enum.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from tools import prompt_workflow_review as review
from tools import prompt_workflow_skill as skill
from tools.review_exchange_models import (
    ArtifactState,
    ReviewConfiguration,
    ReviewContext,
)

from .test_prompt_workflow_review_tdd import _topic_and_state

EXPECTED_CONTEXT_COUNT = 3


@pytest.mark.parametrize("observed", tuple(ArtifactState))
def test_generated_state_maps_once_to_one_owner_or_no_route(
    observed: ArtifactState,
) -> None:
    """Every supported state selects one owner without reclassification."""
    with TemporaryDirectory() as directory:
        root = Path(directory)
        topic, state = _topic_and_state(root)
        (root / "a.review-mode").write_text("", encoding="utf-8")
        contexts = review.specification_contexts(root, topic, state)
        context = contexts[-1]
        route = review.LiveSpecificationRoute(context, observed)
        classifications = 0

        def classify(
            _root: Path,
            candidate: ReviewContext,
            _configuration: ReviewConfiguration,
        ) -> ArtifactState:
            nonlocal classifications
            classifications += 1
            return observed if candidate == context else ArtifactState.IDLE

        with pytest.MonkeyPatch.context() as monkeypatch:
            monkeypatch.setattr(review, "_classify_context", classify)
            command = skill.next_command(root, topic, "routing", {"CLAUDECODE": "1"})

        assert route.state is observed
        with pytest.raises(FrozenInstanceError):
            route.state = ArtifactState.IDLE  # type: ignore[misc]  # ty: ignore[invalid-assignment]
        assert classifications == EXPECTED_CONTEXT_COUNT
        if observed is ArtifactState.IDLE:
            assert "spec-review" not in command
        else:
            role = (
                "spec-reviewer"
                if observed is ArtifactState.REQUEST_PENDING
                else "spec-review-requestor"
            )
            instruction, separator, target = command.partition(" on ")
            assert (instruction, separator) == (f"/{role}", " on ")
            document, umbrella_separator, umbrella = target.partition(
                " with umbrella ",
            )
            assert document.endswith("docs/plan.v1.2.3.routing.md")
            assert umbrella_separator == " with umbrella "
            assert umbrella.endswith("docs/draft.v1.2.3.umbrella.md")


# eof
