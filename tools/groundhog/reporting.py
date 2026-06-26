"""Report text and progress cadence for groundhog.

This module owns the user-visible line text: the key=value progress and
closing lines (Q16), the progress cadence governor (Q04), the day-walk phase
headers and banners, the crash block (Q06), the Q32 lifecycle words and the
warnings nag line (Q09). Everything here is pure text building, so the whole
report contract is unit-testable.

Fix: the run-state table words — the next-step messages of every branch and
the focus comparison lists (Q07) — move to ``reporting_nextstep.py`` so this
module stays under the per-file line limit; the duration-outlier and per-test
exclusion features had each grown the table wording past the budget. What
stays here is the line text proper; what leaves is the run-state routing.

Fix: the module also owns the Q32 lifecycle words — the four ``ghog
status`` verdicts, the live-run refusal and the detached-walk lines —
so the status contract reads from one place.

Fix: the duration-outlier feature adds the ``avg=``/``outliers=`` suffix of
the final progress line and the bar (Q37) and the ``outliers=`` key of the
closing line through :class:`ClosingMetrics`; the windowed list itself is
built in ``durations_report.py`` and the exit-8 next step in
``reporting_nextstep.py``, to keep this module's budget.

Fix: the per-test exclusion feature adds the ``excluded=`` key of the closing
line through :class:`ClosingMetrics` (Q58, Q65), counting the slower-drifted
exclusions with :func:`excluded_count`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final

from tools.groundhog import durations

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunStats

# One progress line per this percentage step (Q04).
PERCENT_STEP: Final = 10
# One progress line at least this often, in seconds (Q04).
SILENCE_FLOOR_SECONDS: Final = 60.0
# Width of the dashed rule that brackets each day-walk phase in a.ghog.log.
STEP_RULE_WIDTH: Final = 60
# The side dashes that flank the vvv/^^^ banner opening and closing a phase.
_BANNER_SIDE: Final = "-------"
# Unit conversions for the human-readable step duration of an end header.
_SECONDS_PER_MINUTE: Final = 60.0
_MINUTES_PER_HOUR: Final = 60


def now_local() -> str:
    """Return the current local wall-clock time as a full ISO timestamp.

    The full date and time in the user's local timezone, with the UTC offset,
    so a step header in ``a.ghog.log`` is unambiguous and a stale log (read
    after a silent no-op run) is obvious at a glance.
    """
    return datetime.now(tz=UTC).astimezone().isoformat(timespec="seconds")


def step_rule(project: str) -> str:
    """Build the dashed separator rule inside a day-walk phase block."""
    return f"{project}: {'-' * STEP_RULE_WIDTH}"


def _phase_banner(project: str, fill: str) -> str:
    """Build a phase banner: side dashes around a run of the fill char."""
    inner = STEP_RULE_WIDTH - 2 * (len(_BANNER_SIDE) + 1)
    return f"{project}: {_BANNER_SIDE} {fill * inner} {_BANNER_SIDE}"


def step_open_banner(project: str) -> str:
    """Build the ``vvv`` banner that marks the start of a day-walk phase."""
    return _phase_banner(project, "v")


def step_close_banner(project: str) -> str:
    """Build the ``^^^`` banner that marks the end of a day-walk phase."""
    return _phase_banner(project, "^")


def step_started_line(project: str, sub: str, when: str) -> str:
    """Build the per-step start header of a day walk (full local timestamp)."""
    return f"{project}: == ghog {sub} == started | {when}"


def _format_duration(seconds: float) -> str:
    """Render a non-negative duration in seconds as a human-readable string.

    Sub-minute spans stay precise as ``45.3s``; longer spans break into
    ``4m 51.9s`` and ``1h 04m 51.9s`` so a step duration in ``a.ghog.log``
    reads at a glance instead of as a raw second count.
    """
    if seconds < _SECONDS_PER_MINUTE:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(seconds, _SECONDS_PER_MINUTE)
    if minutes < _MINUTES_PER_HOUR:
        return f"{int(minutes)}m {secs:04.1f}s"
    hours, minutes = divmod(int(minutes), _MINUTES_PER_HOUR)
    return f"{hours}h {minutes:02d}m {secs:04.1f}s"


def step_ended_line(project: str, sub: str, when: str, duration_s: float) -> str:
    """Build the per-step end header of a day walk: timestamp plus duration."""
    return (
        f"{project}: == ghog {sub} == ended | {when} "
        f"| duration={_format_duration(duration_s)}"
    )


# Lifecycle verdicts of the ghog status reporter (Q32).
MSG_STATUS_NONE: Final = "ghog: no run recorded in a.ghog.status - Next: ghog day"
MSG_STATUS_RUNNING: Final = (
    "ghog: run in progress - poll ghog status until state=done; "
    "never start a second run while this one is alive"
)
MSG_STATUS_KILLED: Final = (
    "ghog: the recorded pid is gone without state=done - the run was killed; "
    "Next: ghog day (--detach when the harness kills long calls)"
)
MSG_STATUS_DONE: Final = (
    "ghog: run finished - branch on the exit= above, then read the a.ghog.log tail"
)
MSG_DETACH_SILENT: Final = (
    "ghog: the detached walk wrote no a.ghog.status in time; "
    "read a.ghog.log and a.ghog.status before retrying"
)
_MSG_CRASH_HEADER: Final = "ghog: the test suite crashed mid-run."
_MSG_CRASH_INSTRUCTION: Final = (
    "Fix the test suite now: make it robust against this exception, based on "
    "the tests and stack above, so it cannot break the suite again. "
    "Then re-run ghog day."
)
# Coverage placeholders of the closing line (Q16).
COV_SKIPPED: Final = "skipped"
COV_WITHHELD: Final = "withheld"
COV_UNREAD: Final = "unread"
# Outlier placeholders of the closing line (Q37): skipped on a run that times
# no calls (any subcommand but full), withheld while a failure or a crash
# hides the timing verdict (outliers judged last), else the count.
OUTLIERS_SKIPPED: Final = "skipped"
OUTLIERS_WITHHELD: Final = "withheld"


@dataclass(frozen=True)
class ClosingMetrics:
    """The cov=, outliers= and excluded= values of the closing line (Q16, Q37, Q58).

    Kept as one value object so the closing line stays within the project's
    five-argument limit; the simple callers pass only the coverage value and
    let the outlier and excluded values default to ``skipped``.

    Attributes:
        cov: The ``cov=`` value, from :func:`cov_text`.
        outliers: The ``outliers=`` value, from :func:`outliers_text`.
        excluded: The ``excluded=`` value, from :func:`excluded_text`: the count
            of slower-drifted exclusions, the ones that drive a fix (Q65).
    """

    cov: str
    outliers: str = OUTLIERS_SKIPPED
    excluded: str = OUTLIERS_SKIPPED


class ProgressGovernor:
    """Decide when an LLM-mode progress line should be emitted (Q04).

    A line goes out at every ``PERCENT_STEP`` of the collected tests, plus
    whenever ``SILENCE_FLOOR_SECONDS`` pass without one.
    """

    def __init__(self, clock: Callable[[], float]) -> None:
        """Start the governor.

        Args:
            clock: A monotonic time source, injectable for tests.
        """
        self._clock = clock
        self._last_bucket = -1
        self._last_time = clock()

    def should_emit(self, stats: RunStats) -> bool:
        """Tell whether a progress line is due for the current statistics.

        Args:
            stats: The counters parsed so far.

        Returns:
            True when a percent step was crossed or the silence floor was
            reached; always False before the collected total is known.
        """
        if stats.total <= 0:
            return False
        now = self._clock()
        bucket = (stats.done * 100 // stats.total) // PERCENT_STEP
        if bucket > self._last_bucket:
            self._last_bucket = bucket
            self._last_time = now
            return True
        if now - self._last_time >= SILENCE_FLOOR_SECONDS:
            self._last_time = now
            return True
        return False


def format_percent(value: float) -> str:
    """Format a coverage percentage without a trailing ``.0``.

    Args:
        value: The percentage value.

    Returns:
        ``100`` for 100.0, ``97.4`` for 97.4.
    """
    return format(value, "g")


def progress_line(
    sub_label: str,
    stats: RunStats,
    summary: DurationSummary | None = None,
) -> str:
    """Build one LLM-mode progress line (Q16).

    The live lines carry no timing; the final line of a full run is given the
    summary, so it alone appends the ``avg=``/``outliers=`` verdict (Q37).

    Args:
        sub_label: The subcommand label, such as ``full``.
        stats: The counters parsed so far.
        summary: The duration verdict for the final line, or ``None``.

    Returns:
        The key=value progress line.
    """
    percent = stats.done * 100 // stats.total if stats.total > 0 else 0
    line = (
        f"ghog {sub_label}: {percent}% ({stats.done}/{stats.total}) "
        f"fail={stats.failed} warn={stats.warnings} xfail={stats.xfailed}"
    )
    if summary is None:
        return line
    return f"{line} {progress_suffix(summary)}"


def progress_suffix(summary: DurationSummary) -> str:
    """Build the ``avg=``/``outliers=`` suffix of the final line and bar (Q37).

    Args:
        summary: The duration verdict of the full run.

    Returns:
        The ``avg=<mean call seconds>s outliers=<count>`` suffix; the mean is
        over the non-outlier calls, so one slug never drags the average up.
    """
    return f"avg={summary.average:.3f}s outliers={len(summary.outliers)}"


def outliers_text(
    stats: RunStats,
    summary: DurationSummary | None,
    *,
    measured: bool,
) -> str:
    """Build the ``outliers=`` value of the closing line (Q37).

    Args:
        stats: The final counters of the run.
        summary: The duration verdict, or ``None`` when none was formed.
        measured: Whether the run times its calls (a ``full`` run, Q39).

    Returns:
        ``skipped`` when no calls are timed, ``withheld`` while a failure
        hides the verdict (outliers judged last), else the outlier count.
    """
    if not measured:
        return OUTLIERS_SKIPPED
    if stats.failed > 0:
        return OUTLIERS_WITHHELD
    if summary is None:
        return OUTLIERS_SKIPPED
    return str(len(summary.outliers))


def excluded_count(summary: DurationSummary) -> int:
    """Count the slower-drifted exclusions that drive the exit-8 verdict (Q65).

    These are the only accepted-slow calls that drive a fix: a call within two
    seconds of its baseline reads ``ok``, and a faster or stale entry is
    auto-managed by the tool (the baseline ratchets down, or the entry is
    removed), so neither changes the exit (Q57, Q60, Q61). The same count both
    keeps an otherwise-green run on exit 8 and fills the ``excluded=`` field.

    Args:
        summary: The run verdict carrying the excluded-call records.

    Returns:
        The number of excluded calls flagged :data:`durations.STATUS_SLOWER`.
    """
    return sum(
        1 for record in summary.exclusions if record.status == durations.STATUS_SLOWER
    )


def excluded_text(
    stats: RunStats,
    summary: DurationSummary | None,
    *,
    measured: bool,
) -> str:
    """Build the ``excluded=`` value of the closing line (Q58, Q65).

    The count is the slower-drifted exclusions only (Q65), so an all-zero
    ``excluded=0`` reads as a clean list, parallel to ``outliers=``. Like the
    outlier count it is judged last: a run that times no calls skips it, a
    failure withholds it while the timing verdict is hidden.

    Args:
        stats: The final counters of the run.
        summary: The duration verdict, or ``None`` when none was formed.
        measured: Whether the run times its calls (a ``full`` run, Q39).

    Returns:
        ``skipped`` when no calls are timed, ``withheld`` while a failure hides
        the verdict, else the slower-drifted exclusion count.
    """
    if not measured:
        return OUTLIERS_SKIPPED
    if stats.failed > 0:
        return OUTLIERS_WITHHELD
    if summary is None:
        return OUTLIERS_SKIPPED
    return str(excluded_count(summary))


def cov_text(stats: RunStats, *, measured: bool) -> str:
    """Build the ``cov=`` value of the closing line (Q16).

    Args:
        stats: The final counters of the run.
        measured: Whether the run measured coverage at all.

    Returns:
        ``skipped`` when not measured, ``withheld`` while failures hide
        the number, ``unread`` on a TOTAL parse miss (Q19), else the
        percentage.
    """
    if not measured:
        return COV_SKIPPED
    if stats.failed > 0:
        return COV_WITHHELD
    if stats.cov_percent is None:
        return COV_UNREAD
    return format_percent(stats.cov_percent)


def closing_line(
    project: str,
    sub_label: str,
    stats: RunStats,
    exit_code: int,
    metrics: ClosingMetrics,
) -> str:
    """Build the closing done line merging the alias echo and the keys.

    Args:
        project: The consuming project folder name.
        sub_label: The subcommand label, such as ``full``.
        stats: The final counters of the run.
        exit_code: The groundhog exit code (Q12).
        metrics: The ``cov=``, ``outliers=`` and ``excluded=`` values
            (Q16, Q37, Q58).

    Returns:
        The closing key=value line (Q16).
    """
    return (
        f"{project}: ghog {sub_label} done fail={stats.failed} "
        f"warn={stats.warnings} xfail={stats.xfailed} "
        f"cov={metrics.cov} outliers={metrics.outliers} "
        f"excluded={metrics.excluded} exit={exit_code}"
    )


def nag_line(stats: RunStats) -> str | None:
    """Build the success nag line counting warnings and xfails (Q09).

    Args:
        stats: The final counters of the run.

    Returns:
        The nag line, or ``None`` when there is nothing to nag about.
    """
    if stats.warnings == 0 and stats.xfailed == 0:
        return None
    return f"nag: warn={stats.warnings} xfail={stats.xfailed} worth a look"


def run_live_line(pid: int | None) -> str:
    """Build the refusal line of a run started over a live one (Q32).

    Args:
        pid: The recorded pid of the live run.

    Returns:
        The refusal line; nothing was started.
    """
    return (
        f"ghog: a run is already live (pid={pid}) - nothing started; "
        "poll ghog status until state=done"
    )


def detached_line(pid: int) -> str:
    """Build the acknowledgment of a detached day walk (Q32).

    Args:
        pid: The survivor pid.

    Returns:
        The acknowledgment naming the log and the poll to run.
    """
    return (
        f"ghog: day walk detached (pid={pid}) - report streams to a.ghog.log; "
        "poll ghog status until state=done, then branch on its exit="
    )


def crash_block(stats: RunStats, tail: Sequence[str]) -> list[str]:
    """Build the crash block printed when the suite dies mid-run (Q06).

    Args:
        stats: The counters parsed before the crash.
        tail: The most recent raw output lines, the stack context.

    Returns:
        The crash block lines: header, last started tests, output tail,
        and the immediate-fix instruction.
    """
    lines = [_MSG_CRASH_HEADER, "Last started tests:"]
    lines.extend(f"- {node_id}" for node_id in stats.last_started)
    lines.append("Output tail:")
    lines.extend(f"  {raw}" for raw in tail)
    lines.append(_MSG_CRASH_INSTRUCTION)
    return lines


# eof
