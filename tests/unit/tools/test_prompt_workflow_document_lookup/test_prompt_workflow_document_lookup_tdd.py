"""Preserve document lookup behavior while extracting its implementation.

Exercise the docs facade with real files so callers retain exact ambiguity,
canonical-parent preference, plan distinctions and deterministic timestamp ties.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import PromptWorkflowError, Topic

if TYPE_CHECKING:
    from pathlib import Path


def _document(directory: Path, name: str, timestamp: int = 1_000) -> Path:
    """Create a real document with a controlled modification timestamp."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text("document", encoding="utf-8")
    os.utime(path, (timestamp, timestamp))
    return path


def test_exact_ambiguity_and_local_preference_share_the_facade(tmp_path: Path) -> None:
    """General resolution reports both duplicates while a topic selects its parent."""
    root_docs = tmp_path / "docs"
    parent = root_docs / "v0.12.0"
    name = "design.v0.12.0.lookup-topic.md"
    elsewhere = _document(root_docs, name, 2_000)
    local = _document(parent, name)
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")

    assert docs.find_documents(tmp_path, topic.version, topic.slug, "design") == [
        elsewhere, local,
    ]
    with pytest.raises(PromptWorkflowError, match="Ambiguous design document") as error:
        docs.resolve_document(tmp_path, topic.version, topic.slug, "design")
    assert elsewhere.relative_to(tmp_path).as_posix() in str(error.value)
    assert local.relative_to(tmp_path).as_posix() in str(error.value)
    assert docs.find_matching_documents(tmp_path, topic, "design") == [local]
    assert docs.select_document(tmp_path, topic, "design") == local


@pytest.mark.parametrize(
    ("document_type", "role", "suffix"),
    [("plan", "plan", ".md"), ("validation-plan", "validation_plan", ".validation.md")],
)
def test_exact_and_workflow_plan_kinds_remain_distinct(
    tmp_path: Path,
    document_type: str,
    role: str,
    suffix: str,
) -> None:
    """Each lookup entry point selects its own plan kind despite a sibling plan."""
    parent = tmp_path / "docs"
    _document(parent, "plan.v0.12.0.lookup-topic.md")
    _document(parent, "plan.v0.12.0.lookup-topic.validation.md")
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")
    expected = parent / f"plan.v0.12.0.lookup-topic{suffix}"

    assert docs.resolve_document(tmp_path, topic.version, topic.slug, document_type) == expected
    assert docs.find_matching_documents(tmp_path, topic, role) == [expected]
    assert docs.select_document(tmp_path, topic, role) == expected


def test_local_timestamp_ties_preserve_sorted_candidate_order(tmp_path: Path) -> None:
    """Equal mtimes retain the first sorted path; a newer subtopic still wins."""
    parent = tmp_path / "docs" / "v0.12.0"
    subtopic = _document(parent, "design.v0.12.0.lookup_topic_extra.md")
    exact = _document(parent, "design.v0.12.0.lookup-topic.md")
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")

    assert docs.find_matching_documents(tmp_path, topic, "design") == [exact, subtopic]
    assert docs.select_document(tmp_path, topic, "design") == exact
    assert docs.most_recent([subtopic, exact]) == subtopic
    os.utime(subtopic, (2_000, 2_000))
    assert docs.select_document(tmp_path, topic, "design") == subtopic
    assert docs.most_recent([]) is None


# eof
