"""Dated-prompt cut of a trimmed conversation.

Split out of ``tools.trim_thinking`` so that module stays under the repository
line budget. Once a conversation is trimmed, the lines before the first prompt
stamped with one of the requested dates are dropped; ``trim_transcript``
applies this cut when the caller passes dates.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from datetime import date

# A dated prompt opens with an optional one-character marker and its space,
# then an eight-digit YYYYMMDD date followed by a space.
_DATED_LINE_PATTERN = re.compile(r"^(?:.\s)?(?P<date>\d{8})\s")


def date_forms(day: date) -> frozenset[str]:
    """Return the digit string one date is recognized as.

    Args:
        day: The date a dated prompt line may carry.

    Returns:
        Its `YYYYMMDD` rendering.
    """
    return frozenset({day.strftime("%Y%m%d")})


def drop_lines_before_dated_prompts(
    lines: Sequence[str],
    dates: Iterable[date],
) -> list[str]:
    """Drop every line before the first prompt bearing one of these dates.

    A dated prompt is a line whose first token, after an optional one-character
    marker such as the Claude prompt ornament, is a date followed by a space.
    Only the dates given are recognized, so an unrelated number opening a line
    keeps the transcript unchanged.

    Args:
        lines: Lines of the already trimmed conversation.
        dates: Dates a prompt line may be stamped with.

    Returns:
        The lines from the first matching dated prompt onward, or all lines
        when no dated prompt matches.
    """
    wanted: set[str] = set()
    for day in dates:
        wanted |= date_forms(day)
    if not wanted:
        return list(lines)
    for index, line in enumerate(lines):
        match = _DATED_LINE_PATTERN.match(line)
        if match is not None and match.group("date") in wanted:
            return list(lines[index:])
    return list(lines)


# eof
