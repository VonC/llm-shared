"""The two-line floor file behind the duration outlier gate (Q38, Q40).

The duration rule judges each call against an absolute floor in seconds
(Q46). That floor persists across runs in ``a.ghog.outliers`` at the project
root, in the ``a.ghog.*`` family the tool already writes and Git ignores the
same way (Q38). The file holds two lines (Q40):

- line 1: the tool's auto floor, ``k * median`` of this run's call times (Q46).
  It is a write-only record, never read back for gating, so each run judges
  itself against its own freshly computed floor and Q43's convergence never
  lags a run behind (Q48).
- line 2: the user override in seconds, default ``-1``. While line 2 is ``-1``
  the run's auto value is active; a positive line 2 replaces it, so a project
  accepts a legitimately slow call by raising the floor above it (Q43).

Deleting the file drops the override: the next full run rewrites line 1 and
resets line 2 to ``-1`` (Q45). A missing, partial or binary file reads as "no
override" and falls back to the auto floor, so a hand-edit cannot crash a run.
"""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger("groundhog")

# The floor file at the project root, the a.ghog.* family (Q38).
FLOOR_FILE: Final = "a.ghog.outliers"
# The line-2 default: no user override, so the run's auto floor is active (Q43).
NO_OVERRIDE: Final = -1.0
# The two lines the file always carries: the auto floor then the override.
_LINE_COUNT: Final = 2


def floor_path(root: Path) -> Path:
    """Return the floor file path for a project root.

    Args:
        root: The project root directory.

    Returns:
        The ``a.ghog.outliers`` path under that root.
    """
    return root / FLOOR_FILE


def read_floor(root: Path) -> float | None:
    """Return the user override (line 2), or ``None`` when unset (Q48).

    Line 1 (the auto floor) is never read here: each run gates against its own
    freshly computed auto value, so only the override is persistent state
    (Q48). A missing, unreadable, malformed or partial file, and the ``-1``
    sentinel (any negative value), all read as "no override".

    Args:
        root: The project root directory.

    Returns:
        The override seconds when line 2 is a number ``>= 0``, else ``None``.
    """
    text = _read_text(root)
    if text is None:
        return None
    lines = text.splitlines()
    if len(lines) < _LINE_COUNT:
        return None
    try:
        override = float(lines[1].strip())
    except ValueError:
        return None
    return override if override >= 0 else None


def active_floor(override: float | None, auto: float) -> float:
    """Resolve the floor the rule gates against, override first (Q48).

    Args:
        override: The user override from :func:`read_floor`, or ``None``.
        auto: This run's freshly computed ``k * median`` auto floor.

    Returns:
        The override when set (``>= 0``), else the auto floor.
    """
    if override is not None and override >= 0:
        return override
    return auto


def write_floor(root: Path, auto: float, override: float) -> None:
    """Write the two-line floor file atomically (Q40, Q45).

    Line 1 records this run's auto floor (write-only, Q48); line 2 carries the
    preserved override (``-1`` when none). The write is a side-file replace,
    the atomic pattern of ``snapshot.py`` and ``status.py``; a write failure is
    logged, never raised, so it cannot crash the run.

    Args:
        root: The project root directory.
        auto: This run's ``k * median`` auto floor, written to line 1.
        override: The override to preserve on line 2 (``-1`` for none).
    """
    path = floor_path(root)
    side = path.with_name(f"{FLOOR_FILE}.tmp")
    try:
        side.write_text(f"{auto}\n{override}\n", encoding="utf-8")
        side.replace(path)
    except OSError as error:
        LOGGER.info("ghog: could not write %s: %s", FLOOR_FILE, error)


def _read_text(root: Path) -> str | None:
    """Read the floor file text, tolerating a missing or binary file.

    Args:
        root: The project root directory.

    Returns:
        The file text, or ``None`` when it is absent or unreadable.
    """
    with contextlib.suppress(OSError, UnicodeDecodeError):
        return floor_path(root).read_text(encoding="utf-8")
    return None


# eof
