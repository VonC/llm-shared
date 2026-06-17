"""The two-line floor file behind the duration outlier gate (Q38, Q40).

The duration rule judges each call against an absolute floor in seconds
(Q46), persisted in ``a.ghog.outliers`` at the project root -- the
``a.ghog.*`` family the tool writes and Git ignores (Q38). Two lines (Q40):

- line 1: the auto floor, ``k * median`` of this run's calls. A write-only
  record the gate never reads back, so it cannot lag a run behind (Q46, Q48).
- line 2: the floor the gate uses, default ``1.0`` second, seeded on a fresh
  run so every project flags any call at or above a second; a project raises
  it to accept a slow call or lowers it to catch faster ones (Q43). Below
  zero, missing, partial or binary all fall back to the default; deleting the
  file re-seeds line 2 with it next run (Q45), so a hand-edit cannot crash a
  run.
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
# The line-2 default: the floor the gate uses until a project tunes it. One
# second, so a fresh project flags any call at or above a second (Q43).
DEFAULT_FLOOR: Final = 1.0
# The two lines the file always carries: the auto floor then the gate floor.
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
    """Return the line-2 floor, or ``None`` when it is unset (Q48).

    Line 1 (the auto floor) is never read here: the gate uses line 2 when it is
    set, else the one-second default, so line 1 stays a record only (Q48). A
    missing, unreadable, malformed or partial file, and any value below zero,
    all read as unset so the caller falls back to the default.

    Args:
        root: The project root directory.

    Returns:
        The floor seconds when line 2 is a number ``>= 0``, else ``None``.
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


def active_floor(override: float | None) -> float:
    """Resolve the floor the rule gates against, the default when unset (Q48).

    Args:
        override: The line-2 floor from :func:`read_floor`, or ``None`` when
            the file is unset, malformed or below zero.

    Returns:
        The override when set (``>= 0``), else the one-second
        :data:`DEFAULT_FLOOR`.
    """
    if override is not None and override >= 0:
        return override
    return DEFAULT_FLOOR


def write_floor(root: Path, auto: float, override: float) -> None:
    """Write the two-line floor file atomically (Q40, Q45).

    Line 1 records this run's auto floor (write-only, Q48); line 2 carries the
    floor the gate uses, the one-second default when a project has not tuned
    it. The write is a side-file replace, the atomic pattern of ``snapshot.py``
    and ``status.py``; a write failure is logged, never raised, so it cannot
    crash the run.

    Args:
        root: The project root directory.
        auto: This run's ``k * median`` auto floor, written to line 1.
        override: The floor to persist on line 2 (the one-second default when
            the project has not set its own).
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
