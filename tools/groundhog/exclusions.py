"""The tool-managed ``[exclusion]`` section of the floor file (Q53, Q66).

The v0.2.0 floor is one number for the whole suite; it cannot accept one
must-stay-slow call without lifting the bar for every other test. So an
optional ``[exclusion]`` section follows the two floor lines of
``a.ghog.outliers`` (Q53), one accepted call per line::

    0.0
    1.0
    [exclusion]
    src/pkg/.../test_init_all_writes_hashes = 11.41
    src/pkg/.../test_only_the_exact_session_cookie = 6.80

Each entry is ``<node id> = <recorded seconds>``: the full pytest node id
kept whole (a parametrized id with spaces survives), and the call time at the
moment of exclusion, the baseline the call is later held to.

This module is the read/write seam for that section, beside ``floor.py`` and
``gate.py`` (Q66): ``floor.py`` keeps its two-line read unchanged, so the
floor lines (1 and 2) stay user-owned while the tool owns the section. The
read is tolerant like the floor read -- a missing, partial or binary file, and
any malformed entry, read as no exclusions, never a crash -- and the write is
the same atomic side-file replace, logged not raised on failure. The
add / lower-baseline / remove decisions are caller policy (the rule and the
``ghog`` command); this module only writes the ``node -> seconds`` map handed
to it.
"""

from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Final

from tools.groundhog import floor

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

LOGGER = logging.getLogger("groundhog")

# The header that opens the section; every line after it is one accepted call,
# everything before it (the two floor lines) belongs to the floor reader (Q53).
_EXCLUSION_HEADER: Final = "[exclusion]"
# The two floor lines kept verbatim above the section on a write (Q53).
_FLOOR_LINE_COUNT: Final = 2
# The floor head seeded when the file has fewer than two lines yet (no full run
# before): line 1 the auto record, line 2 the one-second default of floor.py.
_DEFAULT_HEAD: Final = ("0.0", str(floor.DEFAULT_FLOOR))


def read_exclusions(root: Path) -> dict[str, float]:
    """Return the ``node -> recorded seconds`` map of the section (Q53).

    Only well-formed ``node = number`` lines after the ``[exclusion]`` header
    are read; the floor lines before the header, blank lines, comments and
    malformed entries are skipped without raising. A missing, partial or binary
    file, and a file with no section, all read as ``{}`` -- a hand-edit can
    never crash a run, the safe fallback of the floor file (Q53).

    Args:
        root: The project root directory, where the floor file lives.

    Returns:
        The exclusion map, ``{}`` when the section is absent or unreadable.
    """
    text = _read_text(root)
    if text is None:
        return {}
    result: dict[str, float] = {}
    in_section = False
    for raw in text.splitlines():
        line = raw.strip()
        if not in_section:
            in_section = line == _EXCLUSION_HEADER
            continue
        if not line or line.startswith("#"):
            continue
        entry = _parse_entry(line)
        if entry is not None:
            result[entry[0]] = entry[1]
    return result


def write_exclusions(root: Path, exclusions: Mapping[str, float]) -> None:
    """Write the section back, preserving the floor lines, atomically (Q66).

    The two floor lines (1 and 2) are kept verbatim, then the ``[exclusion]``
    header and one ``node = seconds`` line per entry are written through the
    side-file replace ``floor.py`` uses. An empty map drops the header, so the
    file returns to a clean two-line floor file. The add, lower-baseline and
    remove decisions are the caller's (the rule and the ``ghog`` command); this
    writer only persists the map handed to it. A write failure is logged, never
    raised, so it cannot crash the run.

    Args:
        root: The project root directory, where the floor file lives.
        exclusions: The ``node -> recorded seconds`` map to persist.
    """
    head = _floor_head(root)
    if exclusions:
        body = "".join(f"{node} = {secs}\n" for node, secs in exclusions.items())
        text = f"{head}{_EXCLUSION_HEADER}\n{body}"
    else:
        text = head
    path = floor.floor_path(root)
    side = path.with_name(f"{floor.FLOOR_FILE}.tmp")
    try:
        side.write_text(text, encoding="utf-8")
        side.replace(path)
    except OSError as error:
        LOGGER.info("ghog: could not write %s exclusions: %s", floor.FLOOR_FILE, error)


def _floor_head(root: Path) -> str:
    """Return the two floor lines to keep above the section, as one block.

    The first two lines of the existing file are kept verbatim; when the file
    has fewer than two lines yet (no full run has written the floor), the
    missing lines fall back to :data:`_DEFAULT_HEAD` so the section always sits
    at line three and the file stays well-formed for the floor reader.

    Args:
        root: The project root directory, where the floor file lives.

    Returns:
        The two floor lines, each newline-terminated, as one string.
    """
    text = _read_text(root)
    lines = text.splitlines() if text is not None else []
    head = lines[:_FLOOR_LINE_COUNT]
    head += list(_DEFAULT_HEAD[len(head):])
    return "".join(f"{line}\n" for line in head)


def _parse_entry(line: str) -> tuple[str, float] | None:
    """Parse one ``node = number`` line into a ``(node, seconds)`` pair.

    The split is on the last ``=`` (``rpartition``), so a parametrized node id
    carrying its own ``=`` or spaces survives -- the recorded seconds is always
    the trailing number. A line with no ``=``, an empty node, or a non-numeric
    value is malformed and yields ``None``, skipped by the caller.

    Args:
        line: The already-stripped section line to parse.

    Returns:
        The ``(node, recorded seconds)`` pair, or ``None`` when malformed.
    """
    node, sep, value = line.rpartition("=")
    if not sep:
        return None
    node = node.strip()
    if not node:
        return None
    try:
        seconds = float(value.strip())
    except ValueError:
        return None
    return node, seconds


def _read_text(root: Path) -> str | None:
    """Read the floor file text, tolerating a missing or binary file.

    Args:
        root: The project root directory, where the floor file lives.

    Returns:
        The file text, or ``None`` when it is absent or unreadable.
    """
    with contextlib.suppress(OSError, UnicodeDecodeError):
        return floor.floor_path(root).read_text(encoding="utf-8")
    return None


# eof
