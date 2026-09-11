"""Focused validation tests for stateless prompt-workflow document lookup.

The v0.11.0 layout selector rejects malformed versions and document types,
and distinguishes implementation plans from validation plans exactly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import PromptWorkflowError

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


def test_docs_dirs_for_version_rejects_non_version_selector(tmp_path: Path) -> None:
    """A stateless lookup accepts only minor or full version tokens."""
    with pytest.raises(PromptWorkflowError, match="Invalid document version"):
        docs.docs_dirs_for_version(tmp_path, "latest")


def test_exact_document_match_rejects_unknown_type() -> None:
    """The exact matcher reports the supported selector vocabulary."""
    with pytest.raises(PromptWorkflowError, match="Unknown document type"):
        docs._exact_doc_matches("plan.v0.11.0.topic.md", "other", "v0.11.0", "topic")


def test_exact_plan_match_excludes_validation_and_wrong_slug() -> None:
    """Plain plan selection never consumes a validation plan or another topic."""
    assert not docs._exact_doc_matches(
        "plan.v0.11.0.topic.validation.md",
        "plan",
        "v0.11.0",
        "topic",
    )
    assert not docs._exact_doc_matches(
        "plan.v0.11.0.other.md",
        "plan",
        "v0.11.0",
        "topic",
    )


def test_find_documents_rejects_unknown_type_before_directory_access(
    tmp_path: Path,
) -> None:
    """Invalid selector input fails before documentation directories are read."""
    with pytest.raises(PromptWorkflowError, match="Unknown document type"):
        docs.find_documents(tmp_path, "v0.11.0", "topic", "other")


# eof
