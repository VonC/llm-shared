"""Tests for the pure new_draft models: version, slug, paths, and skeleton.

Cover semantic-version parsing and bumping, the pyproject version read/replace,
slug validation, the worktree directory-name rule, and the draft skeleton text.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from tools import new_draft_models as models


def test_semantic_version_parse_and_str() -> None:
    """Parse reads MAJOR.MINOR.PATCH and __str__ renders it back."""
    version = models.SemanticVersion.parse("0.3.0")
    assert version == models.SemanticVersion(0, 3, 0)
    assert str(version) == "0.3.0"


def test_semantic_version_parse_rejects_bad_text() -> None:
    """Parse raises NewDraftError on text that is not three integers."""
    with pytest.raises(models.NewDraftError, match="Not a MAJOR"):
        models.SemanticVersion.parse("1.2")


def test_semantic_version_bumped_each_part() -> None:
    """Bumped increments the named part and resets the lower parts."""
    base = models.SemanticVersion(1, 2, 3)
    assert base.bumped("patch") == models.SemanticVersion(1, 2, 4)
    assert base.bumped("minor") == models.SemanticVersion(1, 3, 0)
    assert base.bumped("major") == models.SemanticVersion(2, 0, 0)


def test_semantic_version_bumped_rejects_unknown_part() -> None:
    """Bumped raises NewDraftError for an unknown bump kind."""
    with pytest.raises(models.NewDraftError, match="Unknown bump part"):
        models.SemanticVersion(0, 0, 0).bumped("build")


def test_read_pyproject_version_finds_project_line() -> None:
    """read_pyproject_version reads the version line and skips dependency pins."""
    content = '[project]\nname = "x"\nversion = "0.3.0"\n\ndeps = ["ty>=0.0.30"]\n'
    assert models.read_pyproject_version(content) == models.SemanticVersion(0, 3, 0)


def test_read_pyproject_version_missing_raises() -> None:
    """read_pyproject_version raises when no version line exists."""
    with pytest.raises(models.NewDraftError, match="No 'version"):
        models.read_pyproject_version('[project]\nname = "x"\n')


def test_validate_slug_accepts_and_trims() -> None:
    """validate_slug trims surrounding whitespace and accepts hyphen/underscore."""
    assert models.validate_slug("  my_slug-2  ") == "my_slug-2"


@pytest.mark.parametrize("bad", ["", "Bad", "with space", "-leading", "_under"])
def test_validate_slug_rejects_invalid(bad: str) -> None:
    """validate_slug rejects empty, uppercase, spaced, or bad-start slugs."""
    with pytest.raises(models.NewDraftError, match="Invalid slug"):
        models.validate_slug(bad)


def test_draft_filename_builds_versioned_name() -> None:
    """draft_filename builds the docs draft name from version and slug."""
    name = models.draft_filename(models.SemanticVersion(0, 3, 1), "topic")
    assert name == "draft.v0.3.1.topic.md"


def test_worktree_dir_name_strips_trailing_suffix() -> None:
    """worktree_dir_name drops a trailing _<suffix> from the root folder name."""
    assert models.worktree_dir_name("llm-shared_main", "topic") == "llm-shared_topic"


def test_worktree_dir_name_without_underscore() -> None:
    """worktree_dir_name keeps the whole name when there is no underscore."""
    assert models.worktree_dir_name("llm-shared", "topic") == "llm-shared_topic"


def test_compute_worktree_path_is_sibling() -> None:
    """compute_worktree_path places the worktree next to the project root."""
    root = Path("/repos/llm-shared_main")
    assert models.compute_worktree_path(root, "topic") == Path("/repos/llm-shared_topic")


def test_draft_skeleton_has_unique_sections_and_metadata() -> None:
    """draft_skeleton stamps version/branch/date and uses unique section titles."""
    today = datetime.date(2026, 6, 17)
    text = models.draft_skeleton(
        version=models.SemanticVersion(0, 3, 1),
        slug="topic",
        branch="topic",
        today=today,
    )
    assert "# Draft v0.3.1 for topic" in text
    assert "- Version: v0.3.1" in text
    assert "- Branch: topic" in text
    assert "- Date: 2026-06-17" in text
    assert "## Context for topic" in text
    assert "## Goal for topic" in text
    assert "## Notes for topic" in text


# eof
