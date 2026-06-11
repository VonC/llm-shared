"""Shared commit-plan builders of the git batch commit tests.

Split out of ``test_git_batch_commit_parsing.py`` for the repo line
budget: the parsing tests and the workflow/entry-point tests both build
the same canonical conventional commit message, and the entry-point
tests pin the project-root lookup, so those helpers live here as public
names.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def valid_commit_lines(title: str = "fix(scope): title") -> list[str]:
    """Build the canonical valid commit-message lines.

    Args:
        title: The conventional commit title placed on the first line.

    Returns:
        The commit-message lines: title, Why section with two reason
        paragraphs, and a What section with two list items.
    """
    return [
        title,
        "",
        "Why:",
        "",
        "reason before",
        "",
        "reason after",
        "",
        "What:",
        "",
        "- change one",
        "- change two",
    ]


def valid_commit_message(title: str = "fix(scope): title") -> str:
    """Build the canonical valid commit message as one string.

    Args:
        title: The conventional commit title placed on the first line.

    Returns:
        The joined commit-message text of ``valid_commit_lines``.
    """
    return "\n".join(valid_commit_lines(title))


def return_project_root(project_root: Path) -> Callable[[Path], Path]:
    """Build a ``find_project_root`` replacement pinned to ``project_root``.

    Args:
        project_root: The directory the fake lookup should always return.

    Returns:
        A function with the ``find_project_root`` signature that
        ignores its start path and returns ``project_root``.
    """

    def fake_find_project_root(_start_path: Path) -> Path:
        """Return the pinned project root, ignoring the start path."""
        return project_root

    return fake_find_project_root


# eof
