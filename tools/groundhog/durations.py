"""The pure duration rule for a groundhog full run (Q35, Q46).

A full run captures each test's call-phase seconds (Q36); this module judges
that map with no IO and no import of the IO, report or floor modules, so the
whole rule is unit-testable in isolation. It owns the auto floor
(``k * median``), the two-condition true-outlier rule (a robust modified
z-score AND the floor, Q46), and the average over the calls left unflagged
(Q37). The bounded report window (Q47) is rendered from the returned
:class:`DurationSummary` by ``durations_report.py``, split apart so this rule
module stays under its line budget.

The aim is the call truly outside the norm, not the merely slower test: a
call two or three times the median is slower, never an outlier (Q46). When
more than half the calls tie and the MAD collapses to zero, the modified
z-score is undefined, so the rule falls back to the floor alone (Q50). A
uniformly-fast suite never reaches the one-second default floor, so nothing is
flagged and the tidy suite is green from the start (Q41); a project that drops
its floor to zero spares every call, the by-hand way to switch the gate off.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# The auto floor as a multiple of the median: a call must run about an order
# of magnitude slower than the typical test before it can count (Q46).
K_DEFAULT: Final = 10.0
# The Iglewicz-Hoaglin modified z-score cutoff for "far out" (Q46).
MODZ_CUTOFF: Final = 3.5
# The 0.6745 constant of the modified z-score (the standard-normal MAD scale).
_MODZ_SCALE: Final = 0.6745
# How many under-floor runners-up the window shows for tuning (Q51).
_RUNNERS_UP_MAX: Final = 3


@dataclass(frozen=True)
class DurationCall:
    """One timed test call, with its multiple of the run median.

    Attributes:
        node: The test node id.
        seconds: The call-phase seconds.
        ratio: The seconds as a multiple of the run median.
    """

    node: str
    seconds: float
    ratio: float


@dataclass(frozen=True)
class DurationSummary:
    """The verdict of the duration rule over one full run.

    Attributes:
        average: The mean call seconds over the non-outlier calls (Q37).
        outliers: The flagged calls, slowest first, uncapped (Q51).
        runners_up: Up to three next-slowest non-outlier calls (Q51).
        floor: The active floor in seconds the rule judged against.
        median: The run median call seconds.
    """

    average: float
    outliers: tuple[DurationCall, ...]
    runners_up: tuple[DurationCall, ...]
    floor: float
    median: float


def auto_floor(durations: Mapping[str, float]) -> float:
    """Return this run's auto floor, ``k * median`` of the call times (Q46).

    Args:
        durations: Node id to call-phase seconds; empty on a non-full run.

    Returns:
        The generous floor in seconds, or ``0.0`` for an empty map.
    """
    values = list(durations.values())
    if not values:
        return 0.0
    return K_DEFAULT * _median(values)


def summarize(durations: Mapping[str, float], floor: float) -> DurationSummary:
    """Judge a durations map against an active floor (Q46, Q50).

    A call is a true outlier when it is at or above the floor AND far out by
    the modified z-score (cutoff ``MODZ_CUTOFF``); when the MAD is zero the
    z-condition is dropped and the floor alone decides (Q50). The average is
    the mean of the calls left unflagged (Q37).

    Args:
        durations: Node id to call-phase seconds.
        floor: The active floor in seconds (the override or the auto value).

    Returns:
        The :class:`DurationSummary` of the run.
    """
    items = list(durations.items())
    if not items:
        return DurationSummary(0.0, (), (), floor, 0.0)
    values = [secs for _, secs in items]
    median = _median(values)
    mad = _median([abs(value - median) for value in values])
    outliers: list[DurationCall] = []
    spared: list[tuple[str, float]] = []
    for node, secs in items:
        if _is_outlier(secs, median, mad, floor):
            outliers.append(_call(node, secs, median))
        else:
            spared.append((node, secs))
    outliers.sort(key=lambda call: call.seconds, reverse=True)
    slowest = sorted(spared, key=lambda pair: pair[1], reverse=True)[:_RUNNERS_UP_MAX]
    return DurationSummary(
        average=sum(secs for _, secs in spared) / len(spared) if spared else 0.0,
        outliers=tuple(outliers),
        runners_up=tuple(_call(node, secs, median) for node, secs in slowest),
        floor=floor,
        median=median,
    )


def _is_outlier(secs: float, median: float, mad: float, floor: float) -> bool:
    """Tell whether one call is a true outlier (Q46, Q50).

    A call counts only when it is at or above the active floor — the line-2
    value, or the one-second default when a project has not tuned it (Q43) —
    and far out by the modified z-score; when the MAD is zero the floor alone
    decides (Q50). A non-positive floor spares every call: setting line 2 to
    ``0`` is the by-hand way to switch the gate off (Q41).

    Args:
        secs: The call-phase seconds.
        median: The run median.
        mad: The run median absolute deviation.
        floor: The active floor.

    Returns:
        True when the call is at or above a positive floor and far out; when
        the MAD is zero the floor alone decides (Q50); a non-positive floor
        spares every call (Q41).
    """
    if floor <= 0 or secs < floor:
        return False
    if mad <= 0:
        return True
    return _MODZ_SCALE * (secs - median) / mad >= MODZ_CUTOFF


def _call(node: str, secs: float, median: float) -> DurationCall:
    """Build a :class:`DurationCall` with its multiple of the median.

    Args:
        node: The test node id.
        secs: The call-phase seconds.
        median: The run median, the ratio base.

    Returns:
        The call entry; the ratio is ``0.0`` when the median is zero.
    """
    ratio = secs / median if median > 0 else 0.0
    return DurationCall(node=node, seconds=secs, ratio=ratio)


def _median(values: Sequence[float]) -> float:
    """Return the median of a non-empty sequence.

    Args:
        values: The numbers to take the median of.

    Returns:
        The middle value, or the mean of the two middle values.
    """
    ordered = sorted(values)
    count = len(ordered)
    middle = count // 2
    if count % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


# eof
