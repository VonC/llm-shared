"""Report text and progress cadence for groundhog.

This module owns the user-visible words: the key=value progress and closing
lines (Q16), the progress cadence governor (Q04), the next-step messages of
the run-state table, the crash block (Q06), the focus comparison lists
(Q07) and the warnings nag line (Q09). Everything here is pure text
building, so the whole report contract is unit-testable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from tools.groundhog.baseline import FocusComparison
    from tools.groundhog.models import RunStats

# One progress line per this percentage step (Q04).
PERCENT_STEP: Final = 10
# One progress line at least this often, in seconds (Q04).
SILENCE_FLOOR_SECONDS: Final = 60.0

# Next-step messages of the run-state table in the spec.
MSG_CHECK_OK: Final = "Next: ghog affected --no-cov"
MSG_CHECK_FAIL: Final = "Next: fix the compile errors above, re-run ghog check"
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
    "Next: fix these, re-run ghog affected --no-cov until green, then ghog full"
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
    "Stay on ghog single until green, then restart at ghog check"
)
MSG_SINGLE_GREEN: Final = (
    "Next: ghog check, then ghog affected --no-cov, then ghog full"
)
MSG_NO_BASELINE: Final = (
    "no full-run baseline, comparison skipped; run ghog full for suite-level truth"
)
_MSG_CRASH_HEADER: Final = "ghog: the test suite crashed mid-run."
_MSG_CRASH_INSTRUCTION: Final = (
    "Fix the test suite now: make it robust against this exception, based on "
    "the tests and stack above, so it cannot break the suite again. "
    "Then re-run ghog check."
)
# Coverage placeholders of the closing line (Q16).
COV_SKIPPED: Final = "skipped"
COV_WITHHELD: Final = "withheld"
COV_UNREAD: Final = "unread"


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


def progress_line(sub_label: str, stats: RunStats) -> str:
    """Build one LLM-mode progress line (Q16).

    Args:
        sub_label: The subcommand label, such as ``full``.
        stats: The counters parsed so far.

    Returns:
        The key=value progress line.
    """
    percent = stats.done * 100 // stats.total if stats.total > 0 else 0
    return (
        f"ghog {sub_label}: {percent}% ({stats.done}/{stats.total}) "
        f"fail={stats.failed} warn={stats.warnings} xfail={stats.xfailed}"
    )


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
    cov_value: str,
) -> str:
    """Build the closing done line merging the alias echo and the keys.

    Args:
        project: The consuming project folder name.
        sub_label: The subcommand label, such as ``full``.
        stats: The final counters of the run.
        exit_code: The groundhog exit code (Q12).
        cov_value: The ``cov=`` value, from :func:`cov_text`.

    Returns:
        The closing key=value line (Q16).
    """
    return (
        f"{project}: ghog {sub_label} done fail={stats.failed} "
        f"warn={stats.warnings} xfail={stats.xfailed} "
        f"cov={cov_value} exit={exit_code}"
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


def next_after_full(exit_code: int, failing_files: Sequence[str]) -> list[str]:
    """Build the next-step lines after a ``ghog full`` run.

    Args:
        exit_code: The groundhog exit code of the run.
        failing_files: The unique failing test files, for the focus hint.

    Returns:
        The next-step lines of the run-state table.
    """
    if exit_code == EXIT_TEST_FAILURES:
        files = " ".join(failing_files)
        return [f"Next: ghog single {files}".rstrip()]
    if exit_code == EXIT_COVERAGE_GAP:
        return [MSG_COVERAGE_GAP]
    if exit_code == EXIT_OBJECTIVE_MET:
        return [MSG_FULL_OK]
    return []


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
