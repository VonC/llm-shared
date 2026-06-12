"""Unit tests for the groundhog report contract (Q04, Q16).

Cover the key=value progress and closing lines, the coverage placeholder
rules, the cadence governor (percent step and silence floor), the
next-step messages of the run-state table, the crash block (Q06), the
focus comparison lines (Q07) and the nag line (Q09). Also cover the Q30
rule: every next-step message that follows a fix names ghog day, the
loop's only re-entry point, never a standalone subcommand to re-run
first (a real session paid check.bat twice that way).
"""

from __future__ import annotations

from tools.groundhog import reporting
from tools.groundhog.baseline import FocusComparison
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    RunStats,
)

_PARTIAL_COVERAGE = 97.4


class _FakeClock:
    """A controllable monotonic clock for the cadence governor."""

    def __init__(self) -> None:
        """Start the clock at zero."""
        self.now = 0.0

    def __call__(self) -> float:
        """Return the current fake time.

        Returns:
            The fake monotonic time.
        """
        return self.now


def _stats(**values: int) -> RunStats:
    """Build run statistics with keyword overrides.

    Args:
        values: RunStats integer fields to override.

    Returns:
        The statistics object.
    """
    stats = RunStats()
    for name, value in values.items():
        setattr(stats, name, value)
    return stats


def test_format_percent_drops_the_trailing_zero() -> None:
    """100.0 renders as 100 and 97.4 stays 97.4."""
    assert reporting.format_percent(100.0) == "100"
    assert reporting.format_percent(_PARTIAL_COVERAGE) == "97.4"


def test_progress_line_grammar() -> None:
    """The progress line carries the key=value grammar (Q16)."""
    stats = _stats(total=250, done=125, failed=2, warnings=1)
    line = reporting.progress_line("full", stats)
    assert line == "ghog full: 50% (125/250) fail=2 warn=1 xfail=0"


def test_progress_line_with_unknown_total() -> None:
    """Before the collected line, the percent stays at zero."""
    line = reporting.progress_line("full", _stats(done=0))
    assert line.startswith("ghog full: 0% (0/0)")


def test_cov_text_rules() -> None:
    """cov= reads skipped, withheld, unread or the percentage (Q16)."""
    assert reporting.cov_text(_stats(), measured=False) == reporting.COV_SKIPPED
    assert (
        reporting.cov_text(_stats(failed=1), measured=True) == reporting.COV_WITHHELD
    )
    assert reporting.cov_text(_stats(), measured=True) == reporting.COV_UNREAD
    covered = _stats()
    covered.cov_percent = 100.0
    assert reporting.cov_text(covered, measured=True) == "100"


def test_closing_line_grammar() -> None:
    """The closing line merges the alias echo with the keys (Q16)."""
    line = reporting.closing_line(
        "pdfss",
        "full",
        _stats(failed=2, warnings=1),
        EXIT_TEST_FAILURES,
        reporting.COV_WITHHELD,
    )
    assert line == (
        "pdfss: ghog full done fail=2 warn=1 xfail=0 cov=withheld exit=2"
    )


def test_nag_line_only_with_material() -> None:
    """The nag line appears only when warnings or xfails remain (Q09)."""
    assert reporting.nag_line(_stats()) is None
    assert reporting.nag_line(_stats(warnings=3, xfailed=1)) == (
        "nag: warn=3 xfail=1 worth a look"
    )


def test_crash_block_carries_tests_tail_and_instruction() -> None:
    """The crash block lists the last tests and the instruction (Q06)."""
    stats = _stats()
    stats.last_started = ["tests/test_a.py::test_one"]
    block = reporting.crash_block(stats, ("Traceback line",))
    assert block[0] == "ghog: the test suite crashed mid-run."
    assert "- tests/test_a.py::test_one" in block
    assert "  Traceback line" in block
    assert block[-1].startswith("Fix the test suite now:")


def test_governor_emits_per_percent_step() -> None:
    """One line per crossed 10% bucket, none in between (Q04)."""
    clock = _FakeClock()
    governor = reporting.ProgressGovernor(clock)
    stats = _stats(total=20)
    assert governor.should_emit(stats) is True
    stats.done = 1
    assert governor.should_emit(stats) is False
    stats.done = 2
    assert governor.should_emit(stats) is True


def test_governor_emits_on_the_silence_floor() -> None:
    """A long quiet stretch forces a line out (Q04)."""
    clock = _FakeClock()
    governor = reporting.ProgressGovernor(clock)
    stats = _stats(total=1000)
    assert governor.should_emit(stats) is True
    stats.done = 1
    clock.now = reporting.SILENCE_FLOOR_SECONDS
    assert governor.should_emit(stats) is True


def test_governor_stays_silent_before_collection() -> None:
    """Without a collected total there is nothing to report (Q04)."""
    governor = reporting.ProgressGovernor(_FakeClock())
    assert governor.should_emit(_stats()) is False


def test_next_after_full_per_exit_code() -> None:
    """The full-run next step follows the run-state table."""
    failing = ("tests/test_a.py", "tests/test_b.py")
    assert reporting.next_after_full(EXIT_TEST_FAILURES, failing) == [
        "Next: ghog single tests/test_a.py tests/test_b.py",
    ]
    assert reporting.next_after_full(EXIT_COVERAGE_GAP, ()) == [
        reporting.MSG_COVERAGE_GAP,
    ]
    assert reporting.next_after_full(EXIT_OBJECTIVE_MET, ()) == [
        reporting.MSG_FULL_OK,
    ]
    assert reporting.next_after_full(EXIT_SUITE_CRASH, ()) == []


def test_next_after_affected_cov_per_exit_code() -> None:
    """The covered affected-run next step follows the table."""
    assert reporting.next_after_affected_cov(EXIT_OBJECTIVE_MET) == [
        reporting.MSG_AFFECTED_COV_OK,
    ]
    assert reporting.next_after_affected_cov(EXIT_COVERAGE_GAP) == [
        reporting.MSG_COVERAGE_GAP,
    ]
    assert reporting.next_after_affected_cov(EXIT_TEST_FAILURES) == [
        reporting.MSG_AFFECTED_NOCOV_FAIL,
    ]
    assert reporting.next_after_affected_cov(EXIT_SUITE_CRASH) == []


def test_next_after_affected_nocov() -> None:
    """The uncovered affected-run next step follows the table."""
    assert reporting.next_after_affected_nocov(failed=False) == [
        reporting.MSG_AFFECTED_NOCOV_OK,
    ]
    assert reporting.next_after_affected_nocov(failed=True) == [
        reporting.MSG_AFFECTED_NOCOV_FAIL,
    ]


def test_next_after_check() -> None:
    """The check next step covers missing, green and failing (Q10)."""
    assert reporting.next_after_check(code=0, missing=True) == [
        reporting.MSG_CHECK_MISSING,
        reporting.MSG_CHECK_OK,
    ]
    assert reporting.next_after_check(code=0, missing=False) == [
        reporting.MSG_CHECK_OK,
    ]
    assert reporting.next_after_check(code=1, missing=False) == [
        reporting.MSG_CHECK_FAIL,
    ]


def test_post_fix_messages_restart_at_ghog_day() -> None:
    """Every post-fix next-step message names ghog day (Q30).

    The walk is the loop's only re-entry point and opens with the
    compile check, so no message may prescribe a standalone subcommand
    re-run before it.
    """
    post_fix_messages = (
        reporting.MSG_CHECK_FAIL,
        reporting.MSG_AFFECTED_NOCOV_FAIL,
        reporting.MSG_SINGLE_RESTART,
        reporting.MSG_SINGLE_GREEN,
    )
    for message in post_fix_messages:
        assert "ghog day" in message
        assert "re-run ghog check" not in message
    crash = reporting.crash_block(_stats(), ())
    assert crash[-1].endswith("Then re-run ghog day.")


def test_comparison_lines_without_baseline() -> None:
    """No baseline yields the comparison-skipped notice (Q18)."""
    assert reporting.comparison_lines(None, failed=True) == [
        reporting.MSG_NO_BASELINE,
    ]


def test_comparison_lines_with_both_lists() -> None:
    """The two Q07 lists and the restart step are rendered."""
    comparison = FocusComparison(
        still_failing=("tests/test_a.py::test_one",),
        suspects=("tests/test_a.py::test_two",),
    )
    lines = reporting.comparison_lines(comparison, failed=True)
    assert lines[0] == "Still failing in focus (fix these first):"
    assert "- tests/test_a.py::test_one" in lines
    assert "- tests/test_a.py::test_two" in lines
    assert lines[-1] == reporting.MSG_SINGLE_RESTART


def test_comparison_lines_green_focus() -> None:
    """A green focus run renders none markers and the restart chain."""
    comparison = FocusComparison(still_failing=(), suspects=())
    lines = reporting.comparison_lines(comparison, failed=False)
    assert lines.count("- none") == len(("still", "suspects"))
    assert lines[-1] == reporting.MSG_SINGLE_GREEN


# eof
