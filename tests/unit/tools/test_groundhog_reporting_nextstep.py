"""Unit tests for the groundhog run-state table text (Q07, Q30, Q47).

Cover the next-step messages of every branch (check, affected, full), the
exit-8 outlier next step with its ``ghog exclude`` escape hint, and the focus
comparison lists of a ``ghog single`` run. Also cover the Q30 rule: every
next-step message that follows a fix names ghog day, the loop's only re-entry
point, never a standalone subcommand to re-run first (a real session paid
check.bat twice that way).

Fix: split out of ``test_groundhog_reporting.py`` alongside the production
split of ``reporting.py`` into ``reporting_nextstep.py``. The run-state table
moved to its own module to keep ``reporting.py`` under the per-file line
limit, so its tests follow it here; the progress, closing line and crash-block
tests stay with ``reporting`` in the sibling test module. The post-fix
``ghog day`` rule spans both, so it keeps the crash-block tail check against
``reporting`` here, beside the next-step messages it now belongs with.
"""

from __future__ import annotations

from tools.groundhog import reporting, reporting_nextstep
from tools.groundhog.baseline import FocusComparison
from tools.groundhog.durations import DurationCall, DurationSummary
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    RunStats,
)

# A duration verdict with one flagged outlier, for the exit-8 next-step cases.
_AVERAGE = 0.012
_FLOOR = 1.65
_OUTLIER = DurationCall(node="tests/test_slow.py::test_freak", seconds=5.0, ratio=30.0)


def _summary(*, outliers: tuple[DurationCall, ...]) -> DurationSummary:
    """Build a duration verdict for the exit-8 next-step tests.

    Args:
        outliers: The flagged outliers carried by the verdict.

    Returns:
        The summary, with a fixed average, floor and median.
    """
    return DurationSummary(
        average=_AVERAGE,
        outliers=outliers,
        runners_up=(),
        floor=_FLOOR,
        median=0.1,
        exclusions=(),
    )


def test_next_after_full_per_exit_code() -> None:
    """The full-run next step follows the run-state table."""
    failing = ("tests/test_a.py", "tests/test_b.py")
    assert reporting_nextstep.next_after_full(EXIT_TEST_FAILURES, failing) == [
        "Next: ghog single tests/test_a.py tests/test_b.py",
    ]
    assert reporting_nextstep.next_after_full(EXIT_COVERAGE_GAP, ()) == [
        reporting_nextstep.MSG_COVERAGE_GAP,
    ]
    assert reporting_nextstep.next_after_full(EXIT_OBJECTIVE_MET, ()) == [
        reporting_nextstep.MSG_FULL_OK,
    ]
    assert reporting_nextstep.next_after_full(EXIT_SUITE_CRASH, ()) == []


def test_next_after_full_outliers_names_the_fix_and_the_exclusion() -> None:
    """Exit 8 lists the outlier fix step and the ghog exclude hint (Q47, Q62)."""
    summary = _summary(outliers=(_OUTLIER,))
    lines = reporting_nextstep.next_after_full(EXIT_DURATION_OUTLIERS, (), summary)
    assert lines[0] == reporting_nextstep.MSG_OUTLIERS
    # The reworded hint names the add-exclusion command and the investigation,
    # not raising line 2; the floor it would otherwise raise is still shown.
    assert "ghog exclude" in lines[1]
    assert "fix_slow_test.md" in lines[1]
    assert "a.ghog.outliers" in lines[1]
    assert f"{_FLOOR:.2f}s" in lines[1]


def test_next_after_full_outliers_without_a_summary() -> None:
    """The exclusion hint falls back to a zero floor without a summary (Q47)."""
    lines = reporting_nextstep.next_after_full(EXIT_DURATION_OUTLIERS, ())
    assert lines[0] == reporting_nextstep.MSG_OUTLIERS
    assert "ghog exclude" in lines[1]
    assert "0.00s" in lines[1]


def test_next_after_affected_cov_per_exit_code() -> None:
    """The covered affected-run next step follows the table."""
    assert reporting_nextstep.next_after_affected_cov(EXIT_OBJECTIVE_MET) == [
        reporting_nextstep.MSG_AFFECTED_COV_OK,
    ]
    assert reporting_nextstep.next_after_affected_cov(EXIT_COVERAGE_GAP) == [
        reporting_nextstep.MSG_COVERAGE_GAP,
    ]
    assert reporting_nextstep.next_after_affected_cov(EXIT_TEST_FAILURES) == [
        reporting_nextstep.MSG_AFFECTED_NOCOV_FAIL,
    ]
    assert reporting_nextstep.next_after_affected_cov(EXIT_SUITE_CRASH) == []


def test_next_after_affected_nocov() -> None:
    """The uncovered affected-run next step follows the table."""
    assert reporting_nextstep.next_after_affected_nocov(failed=False) == [
        reporting_nextstep.MSG_AFFECTED_NOCOV_OK,
    ]
    assert reporting_nextstep.next_after_affected_nocov(failed=True) == [
        reporting_nextstep.MSG_AFFECTED_NOCOV_FAIL,
    ]


def test_next_after_check() -> None:
    """The check next step covers missing, green and failing (Q10)."""
    assert reporting_nextstep.next_after_check(code=0, missing=True) == [
        reporting_nextstep.MSG_CHECK_MISSING,
        reporting_nextstep.MSG_CHECK_OK,
    ]
    assert reporting_nextstep.next_after_check(code=0, missing=False) == [
        reporting_nextstep.MSG_CHECK_OK,
    ]
    assert reporting_nextstep.next_after_check(code=1, missing=False) == [
        reporting_nextstep.MSG_CHECK_FAIL,
    ]


def test_post_fix_messages_restart_at_ghog_day() -> None:
    """Every post-fix next-step message names ghog day (Q30).

    The walk is the loop's only re-entry point and opens with the
    compile check, so no message may prescribe a standalone subcommand
    re-run before it.
    """
    post_fix_messages = (
        reporting_nextstep.MSG_CHECK_FAIL,
        reporting_nextstep.MSG_AFFECTED_NOCOV_FAIL,
        reporting_nextstep.MSG_SINGLE_RESTART,
        reporting_nextstep.MSG_SINGLE_GREEN,
        reporting_nextstep.MSG_OUTLIERS,
    )
    for message in post_fix_messages:
        assert "ghog day" in message
        assert "re-run ghog check" not in message
    crash = reporting.crash_block(RunStats(), ())
    assert crash[-1].endswith("Then re-run ghog day.")


def test_comparison_lines_without_baseline() -> None:
    """No baseline yields the comparison-skipped notice (Q18)."""
    assert reporting_nextstep.comparison_lines(None, failed=True) == [
        reporting_nextstep.MSG_NO_BASELINE,
    ]


def test_comparison_lines_with_both_lists() -> None:
    """The two Q07 lists and the restart step are rendered."""
    comparison = FocusComparison(
        still_failing=("tests/test_a.py::test_one",),
        suspects=("tests/test_a.py::test_two",),
    )
    lines = reporting_nextstep.comparison_lines(comparison, failed=True)
    assert lines[0] == "Still failing in focus (fix these first):"
    assert "- tests/test_a.py::test_one" in lines
    assert "- tests/test_a.py::test_two" in lines
    assert lines[-1] == reporting_nextstep.MSG_SINGLE_RESTART


def test_comparison_lines_green_focus() -> None:
    """A green focus run renders none markers and the restart chain."""
    comparison = FocusComparison(still_failing=(), suspects=())
    lines = reporting_nextstep.comparison_lines(comparison, failed=False)
    assert lines.count("- none") == len(("still", "suspects"))
    assert lines[-1] == reporting_nextstep.MSG_SINGLE_GREEN


# eof
