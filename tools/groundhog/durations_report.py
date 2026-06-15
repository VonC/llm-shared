"""The bounded duration-outlier report window for a groundhog full run (Q47).

The pure rule lives in ``durations.py``; this module renders its
``DurationSummary`` into the bounded window the report shows -- the flagged
outliers, the marked floor, then up to three runners-up; one slowest-call
line on a green run; a notice on an empty map. It is split out of the rule so
``durations.py`` stays under its line budget, and it stays out of
``reporting.py`` so that module keeps its own budget. Pure string building,
no IO.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from tools.groundhog.durations import DurationCall, DurationSummary

# The window header above the flagged outliers (Q47).
_MSG_OUTLIER_HEADER: Final = "Duration outliers (call time, multiple of the median):"
# The window line on a run that captured no durations.
_MSG_NO_DURATIONS: Final = "No call durations captured."


def window_lines(summary: DurationSummary) -> list[str]:
    """Build the bounded report window around the floor (Q47).

    Args:
        summary: The run verdict from ``durations.summarize``.

    Returns:
        On flagged outliers: a header, the uncapped outlier lines, the
        marked floor, then up to three runners-up. On a green run: one
        slowest-call line with the floor. On an empty map: one notice line.
    """
    if not summary.outliers and not summary.runners_up:
        return [_MSG_NO_DURATIONS]
    if not summary.outliers:
        return [_green_line(summary)]
    lines = [_MSG_OUTLIER_HEADER]
    lines.extend(_call_line(call) for call in summary.outliers)
    lines.append(_floor_line(summary.floor))
    lines.extend(_call_line(call) for call in summary.runners_up)
    return lines


def _green_line(summary: DurationSummary) -> str:
    """Build the single slowest-call line of a run with no outliers (Q47).

    Args:
        summary: The run verdict; its first runner-up is the slowest call.

    Returns:
        The slowest-call line, with the floor and the zero count.
    """
    slowest = summary.runners_up[0]
    return (
        f"Slowest call: {slowest.node} {slowest.seconds:.2f}s "
        f"({slowest.ratio:.0f}x median); floor={summary.floor:.2f}s; outliers=0"
    )


def _call_line(call: DurationCall) -> str:
    """Build one windowed call line: node, seconds, multiple of the median.

    Args:
        call: The timed call to render.

    Returns:
        The indented ``node  secs  Nx median`` line.
    """
    return f"  {call.node}  {call.seconds:.2f}s  {call.ratio:.0f}x median"


def _floor_line(floor: float) -> str:
    """Build the marked floor line shown between outliers and runners-up.

    Args:
        floor: The active floor in seconds.

    Returns:
        The floor marker line.
    """
    return f"  -- floor {floor:.2f}s --"


# eof
