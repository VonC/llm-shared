"""User-mode progress rendering for groundhog: the tqdm thin wrapper (Q20).

This module is the rendering seam, excluded from coverage like
``tools/uv_run.py``: it needs a TTY (and the tqdm dependency) to exercise.
The CLI receives the bar factory as an injectable, so its user-mode logic
stays unit-tested against the :class:`ProgressBar` protocol with a fake
bar, and only this thin wrapper touches tqdm itself. tqdm is imported
dynamically so the rest of the tool runs even before ``uv sync`` installs
it; only a user-mode run requires it.
"""

from __future__ import annotations

import importlib
from typing import Any, Protocol, cast

from tools.groundhog.models import GroundhogError


class ProgressBar(Protocol):
    """The minimal slice of the tqdm bar the CLI relies on (Q20)."""

    def update(self, n: int) -> object:
        """Advance the bar by ``n`` finished tests."""
        ...

    def set_postfix_str(self, s: str) -> object:
        """Show the runtime counters next to the bar (Q20)."""
        ...

    def close(self) -> object:
        """Close the bar before the final report is printed."""
        ...


def make_bar(total: int, description: str) -> ProgressBar:
    """Create the user-mode tqdm bar.

    Args:
        total: The collected test count.
        description: The bar label, such as ``ghog full``.

    Returns:
        The live bar, seen through the :class:`ProgressBar` protocol.

    Raises:
        GroundhogError: When the tqdm dependency is not installed.
    """
    try:
        module = importlib.import_module("tqdm")
    except ModuleNotFoundError as exc:
        msg = "tqdm is required for the user-mode progress bar; run uv sync"
        raise GroundhogError(msg) from exc
    bar_ctor: Any = module.tqdm
    return cast("ProgressBar", bar_ctor(total=total, desc=description, unit="test"))


# eof
