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

A per-test exclusion is layered on as a pure post-step (Q67):
:func:`apply_exclusions` takes the :class:`DurationSummary` and the recorded
``node -> baseline`` map, spares any flagged excluded call (Q54), leaves
excluded calls out of the average (Q64), and classifies each excluded node
against its baseline (``ok``, ``slower``, ``faster`` or ``stale``). It runs
after the rule, so the median, MAD and floor still cover the whole run -- an
exclusion changes what is flagged, never the scale the rest is judged against.
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
# The drift verdict of an excluded call against its recorded baseline (Q63).
STATUS_OK: Final = "ok"
STATUS_SLOWER: Final = "slower"
STATUS_FASTER: Final = "faster"
STATUS_STALE: Final = "stale"
# The fixed baseline tolerance: a call within two seconds either way is
# accepted (``ok``); beyond it slower drives a restore (Q63) and faster
# ratchets the baseline down (Q69) -- noise within the band moves it neither.
_BASELINE_TOLERANCE: Final = 2.0


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
class DurationExclusion:
    """One accepted-slow call judged against its recorded baseline (Q56, Q68).

    Attributes:
        node: The excluded test node id.
        recorded: The baseline call seconds the entry was recorded at.
        current: This run's call seconds, or ``None`` when the node ran no
            call this run -- a stale entry (Q61).
        status: The drift verdict against the baseline: :data:`STATUS_OK`
            within two seconds either way, :data:`STATUS_SLOWER` more than two
            seconds over (Q63), :data:`STATUS_FASTER` more than two seconds
            under (Q60), or :data:`STATUS_STALE` when the node is absent (Q61).
    """

    node: str
    recorded: float
    current: float | None
    status: str


@dataclass(frozen=True)
class DurationSummary:
    """The verdict of the duration rule over one full run.

    Attributes:
        average: The mean call seconds over the non-outlier calls (Q37).
        outliers: The flagged calls, slowest first, uncapped (Q51).
        runners_up: Up to three next-slowest non-outlier calls (Q51).
        floor: The active floor in seconds the rule judged against.
        median: The run median call seconds.
        exclusions: The accepted-slow calls judged against their baselines,
            empty until :func:`apply_exclusions` runs the post-step (Q67).
    """

    average: float
    outliers: tuple[DurationCall, ...]
    runners_up: tuple[DurationCall, ...]
    floor: float
    median: float
    exclusions: tuple[DurationExclusion, ...] = ()


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


def apply_exclusions(
    summary: DurationSummary,
    durations: Mapping[str, float],
    exclusions: Mapping[str, float],
) -> tuple[DurationSummary, dict[str, float]]:
    """Spare excluded calls and judge each against its baseline (Q54, Q67).

    A pure post-step over the rule's :class:`DurationSummary` (Q67), so
    ``summarize`` and its scale -- the median, MAD and floor over the whole run
    -- stay unchanged (Q54). Every flagged call whose node is excluded is
    dropped from the outliers, and every excluded call is left out of the run
    average (Q64), so one accepted slow call cannot lift the suite-wide avg.
    Each excluded node is classified against its recorded baseline, and the
    section the tool will write is computed alongside: a baseline is lowered
    only on a more-than-two-second improvement (Q69), a below-floor or stale
    entry is dropped (Q60, Q61), and the baseline is never raised, so a
    slower-drifted call keeps its recorded value (Q57).

    Args:
        summary: The verdict from :func:`summarize` over the whole run.
        durations: Node id to call-phase seconds, the run the summary judged.
        exclusions: Node id to recorded baseline seconds, the accepted calls.

    Returns:
        The summary with excluded calls spared and the excluded-call list
        attached, paired with the ``node -> seconds`` section the tool writes.
    """
    excluded_nodes = set(exclusions)
    spared_outliers = tuple(
        call for call in summary.outliers if call.node not in excluded_nodes
    )
    records: list[DurationExclusion] = []
    updated: dict[str, float] = {}
    for node, recorded in exclusions.items():
        record, baseline = _classify(node, recorded, durations, summary.floor)
        records.append(record)
        if baseline is not None:
            updated[node] = baseline
    spared = DurationSummary(
        average=_average_without(durations, summary.outliers, excluded_nodes),
        outliers=spared_outliers,
        runners_up=summary.runners_up,
        floor=summary.floor,
        median=summary.median,
        exclusions=tuple(records),
    )
    return spared, updated


def _classify(
    node: str,
    recorded: float,
    durations: Mapping[str, float],
    floor: float,
) -> tuple[DurationExclusion, float | None]:
    """Classify one excluded node and yield the baseline the tool will keep.

    The compare is slower-only (Q63): a call more than two seconds over its
    baseline is a ``slower`` drift that keeps its recorded value -- the
    baseline is never raised (Q57); more than two seconds under is a ``faster``
    real improvement that ratchets the baseline down to the new time (Q69),
    removed once that time drops below the floor (Q60); within two seconds is
    ``ok`` and left alone; a node absent from the run is ``stale`` (Q61).

    Args:
        node: The excluded test node id.
        recorded: The baseline call seconds the entry was recorded at.
        durations: Node id to call-phase seconds of the whole run.
        floor: The active floor in seconds, the below-floor removal mark.

    Returns:
        The :class:`DurationExclusion` record paired with the baseline to
        write, ``None`` to drop the entry (a stale or below-floor call).
    """
    if node not in durations:
        return DurationExclusion(node, recorded, None, STATUS_STALE), None
    current = durations[node]
    if current - recorded > _BASELINE_TOLERANCE:
        return DurationExclusion(node, recorded, current, STATUS_SLOWER), recorded
    if recorded - current > _BASELINE_TOLERANCE:
        baseline = None if current < floor else current
        return DurationExclusion(node, recorded, current, STATUS_FASTER), baseline
    return DurationExclusion(node, recorded, current, STATUS_OK), recorded


def _average_without(
    durations: Mapping[str, float],
    outliers: Sequence[DurationCall],
    excluded_nodes: set[str],
) -> float:
    """Mean call seconds over the calls that are neither outlier nor excluded.

    The run average keeps its v0.2.0 meaning -- the mean over the calls left
    unflagged (Q37) -- with the excluded calls now also left out, the same as
    an outlier (Q64), so one accepted slow call cannot lift the suite-wide avg.

    Args:
        durations: Node id to call-phase seconds of the whole run.
        outliers: The flagged calls of the run, before sparing.
        excluded_nodes: The node ids accepted as slow.

    Returns:
        The mean of the kept calls, or ``0.0`` when none are kept.
    """
    flagged = {call.node for call in outliers}
    kept = [
        secs
        for node, secs in durations.items()
        if node not in flagged and node not in excluded_nodes
    ]
    return sum(kept) / len(kept) if kept else 0.0


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
