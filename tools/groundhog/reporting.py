"""Report text and progress cadence for groundhog.

This module owns the user-visible words: the key=value progress and closing
lines (Q16), the progress cadence governor (Q04), the next-step messages of
the run-state table, the crash block (Q06), the focus comparison lists
(Q07) and the warnings nag line (Q09). Everything here is pure text
building, so the whole report contract is unit-testable.

Every next-step message that follows a fix names ``ghog day`` as the
restart (Q30): the walk is the loop's only re-entry point and opens with
the compile check, so the older ``re-run ghog check`` wording made a real
session pay check.bat twice — once standalone, once inside the resumed
walk.

Fix: the module also owns the Q32 lifecycle words — the four ``ghog
status`` verdicts, the live-run refusal and the detached-walk lines —
so the status contract reads from one place like the run-state table.

Fix: the duration-outlier feature adds the ``avg=``/``outliers=`` suffix of
the final progress line and the bar (Q37), the ``outliers=`` key of the
closing line through :class:`ClosingMetrics`, and the exit-8 next step with
the floor-override hint (Q47); the windowed list itself is built in
``durations_report.py`` to keep this module's budget.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.groundhog.baseline import FocusComparison
    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunStats

# One progress line per this percentage step (Q04).
PERCENT_STEP: Final = 10
# One progress line at least this often, in seconds (Q04).
SILENCE_FLOOR_SECONDS: Final = 60.0

# Next-step messages of the run-state table in the spec.
MSG_CHECK_OK: Final = "Next: ghog affected --no-cov"
MSG_CHECK_FAIL: Final = (
    "Next: fix the compile errors above, re-run ghog day "
    "(the walk opens with this check)"
)
MSG_CHECK_MISSING: Final = (
    "check.bat not found - skipped; pytest collection will catch compile errors"
)
MSG_CHECK_EXIT_MISMATCH: Final = (
    "check.bat printed ERROR lines but exited 0 - treating the check as "
    "failed; fix check.bat so it exits with its failed status (Q26)"
)
MSG_AFFECTED_NOCOV_OK: Final = "Next: ghog full"
MSG_NO_TESTS_RUN: Final = (
    "0 tests ran in this step (testmon: nothing affected since the last run) "
    "- treated as green"
)
MSG_DAY_NOOP: Final = (
    "No Python file changed since the last green ghog day walk - nothing to "
    "do (use --force to walk anyway)"
)
MSG_AFFECTED_NOCOV_FAIL: Final = (
    "Next: fix these, re-run ghog affected --no-cov until green, then ghog day"
)
MSG_COVERAGE_GAP: Final = (
    "Next: covg <file> <ranges> to name the uncovered functions "
    "(use the Missing column above, never a coverage.json export), "
    "add tests, verify with ghog affected"
)
MSG_GAP_LINES_HEADER: Final = "Uncovered lines (file and ranges are the covg input):"
MSG_FULL_OK: Final = "Objective reached"
MSG_AFFECTED_COV_OK: Final = (
    "Coverage gate reached - no ghog full needed; "
    "finish with ghog check (new tests are code too)"
)
MSG_SINGLE_RESTART: Final = (
    "Stay on ghog single until green, then restart the walk: ghog day"
)
MSG_SINGLE_GREEN: Final = (
    "Next: ghog day (the walk re-proves check, affected and full)"
)
MSG_NO_BASELINE: Final = (
    "no full-run baseline, comparison skipped; run ghog full for suite-level truth"
)
# The exit-8 next step (Q47): fix only the calls above the floor, confirm the
# new time alone, then restart the walk (Q30). Named ghog day, never a
# standalone re-run before the walk's compile check.
MSG_OUTLIERS: Final = (
    "Next: shorten each call listed above the floor, confirm it alone with "
    "ghog single <file>, then ghog day to re-measure the whole suite"
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
    """The cov= and outliers= values carried by the closing line (Q16, Q37).

    Kept as one value object so the closing line stays within the project's
    five-argument limit; the simple callers pass only the coverage value and
    let the outlier value default to ``skipped``.

    Attributes:
        cov: The ``cov=`` value, from :func:`cov_text`.
        outliers: The ``outliers=`` value, from :func:`outliers_text`.
    """

    cov: str
    outliers: str = OUTLIERS_SKIPPED


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
        metrics: The ``cov=`` and ``outliers=`` values (Q16, Q37).

    Returns:
        The closing key=value line (Q16).
    """
    return (
        f"{project}: ghog {sub_label} done fail={stats.failed} "
        f"warn={stats.warnings} xfail={stats.xfailed} "
        f"cov={metrics.cov} outliers={metrics.outliers} exit={exit_code}"
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


def next_after_full(
    exit_code: int,
    failing_files: Sequence[str],
    summary: DurationSummary | None = None,
) -> list[str]:
    """Build the next-step lines after a ``ghog full`` run.

    Args:
        exit_code: The groundhog exit code of the run.
        failing_files: The unique failing test files, for the focus hint.
        summary: The duration verdict, for the floor-override hint on exit 8.

    Returns:
        The next-step lines of the run-state table.
    """
    if exit_code == EXIT_TEST_FAILURES:
        files = " ".join(failing_files)
        return [f"Next: ghog single {files}".rstrip()]
    if exit_code == EXIT_COVERAGE_GAP:
        return [MSG_COVERAGE_GAP]
    if exit_code == EXIT_DURATION_OUTLIERS:
        return [MSG_OUTLIERS, _override_hint(summary)]
    if exit_code == EXIT_OBJECTIVE_MET:
        return [MSG_FULL_OK]
    return []


def _override_hint(summary: DurationSummary | None) -> str:
    """Build the floor-override escape shown beside the outlier next step (Q47).

    Args:
        summary: The duration verdict, for the active floor in the hint.

    Returns:
        The hint naming the line-2 override of ``a.ghog.outliers`` for a call
        that must stay slow, with the active floor it has to clear.
    """
    floor_secs = summary.floor if summary is not None else 0.0
    return (
        "A call that must stay slow is not a bug: raise line 2 of "
        f"a.ghog.outliers above {floor_secs:.2f}s (the override), not shorten it"
    )


def next_after_affected_cov(exit_code: int) -> list[str]:
    """Build the next-step lines after a covered ``ghog affected`` run.

    Args:
        exit_code: The groundhog exit code of the run.

    Returns:
        The next-step lines of the run-state table.
    """
    if exit_code == EXIT_OBJECTIVE_MET:
        return [MSG_AFFECTED_COV_OK]
    if exit_code == EXIT_COVERAGE_GAP:
        return [MSG_COVERAGE_GAP]
    if exit_code == EXIT_TEST_FAILURES:
        return [MSG_AFFECTED_NOCOV_FAIL]
    return []


def next_after_affected_nocov(*, failed: bool) -> list[str]:
    """Build the next-step lines after a ``ghog affected --no-cov`` run.

    Args:
        failed: Whether the run had failing tests.

    Returns:
        The next-step lines of the run-state table.
    """
    return [MSG_AFFECTED_NOCOV_FAIL] if failed else [MSG_AFFECTED_NOCOV_OK]


def next_after_check(*, code: int, missing: bool) -> list[str]:
    """Build the next-step lines after a ``ghog check`` run.

    Args:
        code: The check.bat exit code, 0 when it was skipped.
        missing: Whether check.bat was absent (Q10).

    Returns:
        The next-step lines of the run-state table.
    """
    if missing:
        return [MSG_CHECK_MISSING, MSG_CHECK_OK]
    return [MSG_CHECK_OK] if code == 0 else [MSG_CHECK_FAIL]


def comparison_lines(
    comparison: FocusComparison | None,
    *,
    failed: bool,
) -> list[str]:
    """Build the focus-run lines: the two Q07 lists and the next step.

    Args:
        comparison: The baseline comparison, or ``None`` without baseline.
        failed: Whether the focus run had failing tests.

    Returns:
        The comparison and next-step lines of the run-state table.
    """
    if comparison is None:
        return [MSG_NO_BASELINE]
    lines = ["Still failing in focus (fix these first):"]
    lines.extend(_id_lines(comparison.still_failing))
    lines.append(
        "Passing in focus but failing in the full suite "
        "(interaction or ordering suspects, fix second):",
    )
    lines.extend(_id_lines(comparison.suspects))
    lines.append(MSG_SINGLE_RESTART if failed else MSG_SINGLE_GREEN)
    return lines


def _id_lines(node_ids: Sequence[str]) -> list[str]:
    """Render a node id list, with an explicit none marker.

    Args:
        node_ids: The node ids of one comparison list.

    Returns:
        One indented line per id, or a single ``- none`` line.
    """
    if not node_ids:
        return ["- none"]
    return [f"- {node_id}" for node_id in node_ids]


# eof
