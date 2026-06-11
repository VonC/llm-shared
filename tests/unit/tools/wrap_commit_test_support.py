"""Shared typed monkeypatch helpers of the wrap-commit tests.

Split out of ``test_wrap_commit.py`` for the repo line budget: the
backtick-pass, word-rule, reflow, and CLI test files all pin the same
two seams -- the project-root lookup and the wrap-list collector -- so
the typed replacement factories live here. Using small typed functions
instead of inline lambdas also keeps pyright strict happy about the
``monkeypatch.setattr`` value types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def fixed_project_root(root: Path) -> Callable[[Path], Path]:
    """Build a ``find_project_root`` replacement pinned to ``root``.

    Args:
        root: The directory the fake lookup should always return.

    Returns:
        A function with the ``find_project_root`` signature that
        ignores its start path and returns ``root``.
    """

    def fake_find_project_root(_start: Path) -> Path:
        """Return the pinned project root, ignoring the start path."""
        return root

    return fake_find_project_root


def fixed_wrap_list_literals(literals: list[str]) -> Callable[[Path], list[str]]:
    """Build a wrap-list collector replacement pinned to ``literals``.

    Args:
        literals: The literal strings the fake collector should return.

    Returns:
        A function with the collector signature that ignores its start
        directory and returns ``literals``.
    """

    def fake_collect_wrap_list_literals(_start: Path) -> list[str]:
        """Return the pinned literals, ignoring the start directory."""
        return literals

    return fake_collect_wrap_list_literals


# eof
