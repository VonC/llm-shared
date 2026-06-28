"""The duration-outlier window and the exclusion block of a full run (Q47, Q58).

The pure rule lives in ``durations.py``; this module renders its
``DurationSummary`` into the report text. :func:`window_lines` builds the
bounded floor window -- the flagged outliers, the marked floor, then up to
three runners-up; one slowest-call line on a green run; a notice on an empty
map. :func:`exclusion_block` builds the per-test exclusion list shown after
that window (Q58): one line per accepted-slow call with its recorded and
current time and its drift verdict -- ``ok``, the restore instruction when
slower (Q57), the baseline the tool lowered it to (Q69), or ``removed`` (below
floor, Q60, or stale, Q61). The block is a named function behind
``window_lines`` (Q68), not folded into it, so it is tested on its own.
:func:`action_block` adds a short exit-8 recap containing only duration items
that require action, so a slower accepted-slow drift is not buried among many
``ok`` exclusions.

It is split out of the rule so ``durations.py`` stays under its line budget,
and it stays out of ``reporting.py`` so that module keeps its own budget. Pure
string building, no IO.
"""

from __future__ import annotations

from typing import Final

from tools.groundhog import durations

# The window header above the flagged outliers (Q47).
_MSG_OUTLIER_HEADER: Final = "Duration outliers (call time, multiple of the median):"
# The window line on a run that captured no durations.
_MSG_NO_DURATIONS: Final = "No call durations captured."
# The header above the per-test exclusion list, after the floor window (Q58).
_MSG_EXCLUSION_HEADER: Final = (
    "Excluded (accepted slow; slower by 2s+ restores; "
    "the tool ratchets down or removes the rest):"
)
# The exit-8 recap header, printed only for actionable timing verdicts.
_MSG_ACTION_HEADER: Final = "Duration warnings requiring action:"
# The current-time placeholder of a stale entry whose test ran no call (Q61).
_MSG_NOT_RUN: Final = "(not run)"
# The drift verdicts the exclusion line carries beside recorded and current.
_MSG_STATUS_OK: Final = "ok"
_MSG_REMOVED_STALE: Final = "removed (stale)"
_MSG_REMOVED_FLOOR: Final = "removed (now under the floor)"


def window_lines(summary: durations.DurationSummary) -> list[str]:
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
    lines.append("")
    lines.append(_floor_line(summary.floor))
    lines.append("")
    lines.extend(_call_line(call) for call in summary.runners_up)
    return lines


def exclusion_block(summary: durations.DurationSummary) -> list[str]:
    """Build the per-test exclusion list shown after the floor window (Q58).

    Args:
        summary: The run verdict, carrying the excluded-call records.

    Returns:
        A header then one line per excluded call -- ``ok``, the restore
        instruction, the lowered baseline, or ``removed`` -- or ``[]`` when the
        run has no exclusions, so the block is absent on a clean run.
    """
    if not summary.exclusions:
        return []
    lines = ["", _MSG_EXCLUSION_HEADER]
    lines.extend(
        _exclusion_line(record, summary.floor) for record in summary.exclusions
    )
    return lines


def action_block(summary: durations.DurationSummary) -> list[str]:
    """Build the exit-8 recap of only the duration items needing action.

    Args:
        summary: The run verdict, carrying true outliers and exclusions.

    Returns:
        A blank line, a header, then one line per true outlier or slower
        excluded drift. Empty when no timing item requires action.
    """
    lines = [_action_outlier_line(call, summary.floor) for call in summary.outliers]
    lines.extend(
        _exclusion_line(record, summary.floor)
        for record in summary.exclusions
        if record.status == durations.STATUS_SLOWER
    )
    if not lines:
        return []
    return ["", _MSG_ACTION_HEADER, *lines]


def _exclusion_line(record: durations.DurationExclusion, floor: float) -> str:
    """Build one exclusion line: node, recorded, current, and the verdict.

    Args:
        record: The excluded-call record judged against its baseline.
        floor: The active floor, the below-floor removal mark for a faster call.

    Returns:
        The indented ``node  recorded=Xs  current=Ys  <verdict>`` line.
    """
    return (
        f"  {record.node}  recorded={record.recorded:.2f}s  "
        f"current={_current_text(record)}  {_status_text(record, floor)}"
    )


def _current_text(record: durations.DurationExclusion) -> str:
    """Render the current-time field, ``(not run)`` for a stale entry (Q61).

    Args:
        record: The excluded-call record.

    Returns:
        This run's call seconds, or the not-run placeholder when the node ran
        no call this run.
    """
    if record.current is None:
        return _MSG_NOT_RUN
    return f"{record.current:.2f}s"


def _status_text(record: durations.DurationExclusion, floor: float) -> str:
    """Render the drift verdict of one excluded call (Q57, Q60, Q61, Q69).

    The verdict mirrors the section update the tool writes: a ``slower`` call
    is brought back within two seconds of its recorded baseline (Q57); a stale
    entry, with no current time, is removed (Q61); a ``faster`` call shows the
    baseline the tool lowered it to, or ``removed`` once it dropped below the
    floor (Q60, Q69); within tolerance reads ``ok``.

    Args:
        record: The excluded-call record judged against its baseline.
        floor: The active floor, the below-floor removal mark.

    Returns:
        The verdict text shown at the end of the exclusion line.
    """
    if record.status == durations.STATUS_SLOWER:
        return f"restore to within 2s of {record.recorded:.2f}s"
    current = record.current
    if current is None:
        return _MSG_REMOVED_STALE
    if record.status == durations.STATUS_FASTER:
        if current < floor:
            return _MSG_REMOVED_FLOOR
        return f"baseline lowered to {current:.2f}s"
    return _MSG_STATUS_OK


def _green_line(summary: durations.DurationSummary) -> str:
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


def _call_line(call: durations.DurationCall) -> str:
    """Build one windowed call line: node, seconds, multiple of the median.

    Args:
        call: The timed call to render.

    Returns:
        The indented ``node  secs  Nx median`` line.
    """
    return f"  {call.node}  {call.seconds:.2f}s  {call.ratio:.0f}x median"


def _action_outlier_line(call: durations.DurationCall, floor: float) -> str:
    """Build one actionable true-outlier recap line."""
    return (
        f"  {call.node}  current={call.seconds:.2f}s  floor={floor:.2f}s  "
        "shorten below the floor with margin"
    )


def _floor_line(floor: float) -> str:
    """Build the marked floor line shown between outliers and runners-up.

    Args:
        floor: The active floor in seconds.

    Returns:
        The floor marker line.
    """
    return f"  -- floor {floor:.2f}s --"


# eof
