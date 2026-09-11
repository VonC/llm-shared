"""TDD contracts for the closed review-artifact registry and locator."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactLocator,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import (
    ArchiveKind,
    ExchangeIdentity,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)

if TYPE_CHECKING:
    from pathlib import Path


def _identity() -> ExchangeIdentity:
    """Return one stable code-review identity."""
    return ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "artifact-home")


def test_registry_recognizes_every_exchange_kind_and_role() -> None:
    """Each fixed exchange kind parses with identity and settled authorship."""
    registry = ReviewArtifactRegistry()
    identity = _identity()
    expected = {
        RegisteredArtifactKind.REQUEST: ReviewRole.REQUESTOR,
        RegisteredArtifactKind.ANSWER: ReviewRole.REVIEWER,
        RegisteredArtifactKind.COORDINATION: None,
        RegisteredArtifactKind.TOMBSTONE: ReviewRole.REVIEWER,
        RegisteredArtifactKind.TRANSITION_LOCK: None,
    }

    for kind, role in expected.items():
        parsed = registry.parse_name(registry.name_for(kind, identity))
        assert parsed is not None
        assert parsed.kind is kind
        assert parsed.identity == identity
        assert parsed.authored_role is role


def test_registry_excludes_transcripts_and_unrelated_scratch_names() -> None:
    """Documentation transcripts and broad `a.*` scratch files never migrate."""
    registry = ReviewArtifactRegistry()

    assert registry.parse_name("review.code.v0.11.0.artifact-home.md") is None
    assert registry.parse_name("a.commit") is None
    assert registry.parse_name("a.random-review-notes.md") is None


def test_registry_includes_closed_non_exchange_runtime_names() -> None:
    """Marker, retained, guidance, and question-state names are explicit kinds."""
    registry = ReviewArtifactRegistry()
    expected = {
        "a.review-mode": RegisteredArtifactKind.REVIEW_MODE,
        "a.code-review-evidence.v0.11.0.artifact-home.step-0.json": (
            RegisteredArtifactKind.RETAINED_MANIFEST
        ),
        "a.code-review-evidence.v0.11.0.artifact-home.step-1.json": (
            RegisteredArtifactKind.RETAINED_MANIFEST
        ),
        "a.review-guidance.artifact-home.md": RegisteredArtifactKind.REVIEW_GUIDANCE,
        "a.reviewer-assessment.md": RegisteredArtifactKind.QUESTION_STATE,
        "a.question-verdicts.md": RegisteredArtifactKind.QUESTION_STATE,
        "a.writer-instructions.md": RegisteredArtifactKind.QUESTION_STATE,
        "a.requested-changes.md": RegisteredArtifactKind.QUESTION_STATE,
    }

    for name, kind in expected.items():
        parsed = registry.parse_name(name)
        assert parsed is not None
        assert parsed.kind is kind


def test_locator_keeps_transcripts_beside_document_and_transients_in_home(
    tmp_path: Path,
) -> None:
    """One locator places every runtime path below home without moving history."""
    document = tmp_path / "docs" / "plan.v0.11.0.artifact-home.md"
    document.parent.mkdir()
    document.write_text("# Plan\n", encoding="utf-8")
    context = ReviewContext(_identity(), document, None, "1")
    locator = ReviewArtifactLocator(ReviewArtifactConfiguration.load(tmp_path))

    paths = locator.exchange_paths(context)

    assert paths.transcript.parent == document.parent
    assert all(
        path.parent == tmp_path / ".reviews"
        for path in (
            paths.request,
            paths.answer,
            paths.coordination,
            paths.tombstone,
            paths.transition_lock,
        )
    )


def test_registry_renders_every_supported_step_retained_manifest() -> None:
    """Retained evidence supports numbered steps and named sub-steps."""
    registry = ReviewArtifactRegistry()

    for step in ("0", "1", "12", "4A"):
        name = registry.retained_manifest_name("v0.11.0", "artifact-home", step)
        parsed = registry.parse_name(name)
        assert name.endswith(f".step-{step}.json")
        assert parsed is not None
        assert parsed.kind is RegisteredArtifactKind.RETAINED_MANIFEST


def test_registry_rejects_unsupported_render_requests() -> None:
    """Every renderer fails closed when its arguments cannot name a registered kind."""
    registry = ReviewArtifactRegistry()
    identity = _identity()
    with pytest.raises(ReviewExchangeError, match="no identity name"):
        registry.name_for(RegisteredArtifactKind.ARCHIVE, identity)
    with pytest.raises(ReviewExchangeError, match="archive name"):
        registry.archive_name(identity, "not-a-timestamp", ArchiveKind.REQUEST)
    with pytest.raises(ReviewExchangeError, match="retained-manifest"):
        registry.retained_manifest_name("v0.11.0", "artifact-home", "../zero")
    with pytest.raises(ReviewExchangeError, match="no unique fixed name"):
        registry.fixed_name(RegisteredArtifactKind.REQUEST)


# eof
