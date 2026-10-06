"""Scope-aware repair and restart expectations.

Unit tests for the groundhog run-state table text (Q07, Q30, Q47).

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

Fix: the exit-8 hint names the floor file at the location the verdict
carries, in the artifact home, never as a bare project-root file name.

Fix (v0.13.0 full_suite_levels, Step 2): the fixed restart strings became
level-aware builders, so these tests drive each builder at each level. The
Q30 rule is extended: every post-fix line names ``ghog day`` and never a
``none`` level selector, and at a level it carries ``--full=<level>``; the
success, noop and not-measured lines, the walk-owned silence of a green
affected or parallel ``speed`` full step, and the standalone ``Next: ghog
full`` with no carried level are covered too.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Final

import pytest

from tools.groundhog import reporting, reporting_nextstep
from tools.groundhog.baseline import FocusComparison
from tools.groundhog.durations import DurationCall, DurationSummary
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    RunStats,
)
from tools.groundhog.reporting_nextstep import StepContext

# A duration verdict with one flagged outlier, for the exit-8 next-step cases.
_AVERAGE = 0.012
_FLOOR = 1.65
_OUTLIER = DurationCall(node="tests/test_slow.py::test_freak", seconds=5.0, ratio=30.0)
# The reserved selector no line may ever print.
_NONE_SELECTOR: Final = "--full=none"
# The failing files a full or timing pass hands to the focus run.
_FAILING: Final = ("tests/test_a.py", "tests/test_b.py")


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


def test_restart_command_carries_the_level_and_the_scope() -> None:
    """The one restart helper omits the level selector at none only."""
    assert reporting_nextstep.restart_command(FullLevel.NONE) == "ghog day --whole-suite"
    assert reporting_nextstep.restart_command(FullLevel.COV) == "ghog day --full=cov --whole-suite"
    assert (
        reporting_nextstep.restart_command(FullLevel.SPEED, "--whole-suite")
        == "ghog day --full=speed --whole-suite"
    )
    assert reporting_nextstep.carried_selector(FullLevel.NONE) == " --whole-suite"
    assert reporting_nextstep.carried_selector(FullLevel.PASS) == " --full=pass --whole-suite"


def test_success_lines_are_one_per_level() -> None:
    """Each level has its own success line naming the whole suite."""
    skip = reporting_nextstep.success_line(FullLevel.NONE)
    assert skip.startswith("Full suite skipped on purpose")
    for choice in ("ghog day --full=pass --whole-suite", "ghog day --full=cov --whole-suite", "ghog day --full=speed --whole-suite"):
        assert choice in skip
    assert reporting_nextstep.success_line(FullLevel.PASS).startswith(
        "Objective met at pass for the whole suite",
    )
    cov = reporting_nextstep.success_line(FullLevel.COV)
    assert "coverage gate over its sources is met" in cov
    assert "duration gate is not required" in cov
    speed = reporting_nextstep.success_line(FullLevel.SPEED)
    assert "no unaccepted duration outlier remains" in speed
    for level in FullLevel:
        assert reporting_nextstep.success_line(level).endswith("carry on with the calling instruction")


def test_noop_line_names_both_levels_and_no_check() -> None:
    """The noop line states the request, the scope, the saved proof, no check."""
    line = reporting_nextstep.noop_line(FullLevel.COV, FullLevel.SPEED)
    assert "Requested objective cov for the whole suite" in line
    assert "saved proof at speed" in line
    assert "not even check.bat" in line


@pytest.mark.parametrize(
    ("level", "single"),
    [
        (FullLevel.PASS, "Next: ghog single tests/test_a.py tests/test_b.py --full=pass --whole-suite"),
        (FullLevel.SPEED, "Next: ghog single tests/test_a.py tests/test_b.py --full=speed --whole-suite"),
    ],
)
def test_next_after_full_failure_carries_the_level(level: FullLevel, single: str) -> None:
    """A failing full run sends the caller to ghog single at its level."""
    lines = reporting_nextstep.next_after_full(EXIT_TEST_FAILURES, _FAILING, None, StepContext(level))
    assert lines == [single]


def test_next_after_full_per_exit_code() -> None:
    """The full-run next step follows the run-state table at its level."""
    context = StepContext(FullLevel.COV)
    assert reporting_nextstep.next_after_full(EXIT_COVERAGE_GAP, (), None, context) == [
        reporting_nextstep.coverage_gap_line(FullLevel.COV),
    ]
    assert reporting_nextstep.next_after_full(EXIT_OBJECTIVE_MET, (), None, context) == [
        reporting_nextstep.success_line(FullLevel.COV),
    ]
    assert reporting_nextstep.next_after_full(EXIT_SUITE_CRASH, (), None, context) == []


def test_parallel_speed_full_success_depends_on_the_walk() -> None:
    """A green parallel speed run proves cov alone; inside a walk timings own it."""
    direct = StepContext(FullLevel.SPEED, parallel=True)
    assert reporting_nextstep.next_after_full(EXIT_OBJECTIVE_MET, (), None, direct) == [
        reporting_nextstep.success_line(FullLevel.COV),
        reporting_nextstep.MSG_SPEED_NOT_MEASURED + " --whole-suite",
    ]
    walk = StepContext(FullLevel.SPEED, in_walk=True, parallel=True)
    assert reporting_nextstep.next_after_full(EXIT_OBJECTIVE_MET, (), None, walk) == []
    sequential = StepContext(FullLevel.SPEED)
    assert reporting_nextstep.next_after_full(EXIT_OBJECTIVE_MET, (), None, sequential) == [
        reporting_nextstep.success_line(FullLevel.SPEED),
    ]
    assert "ghog day --full=speed --whole-suite" in reporting_nextstep.next_after_full(
        EXIT_OBJECTIVE_MET, (), None, direct,
    )[-1]


def test_next_after_timings_per_exit_code() -> None:
    """The timing-pass next step follows the same run-state table.

    A crash yields no next step, as the full run does: the crash block already
    carries the instruction, so a second one would only compete with it.
    Inside a speed walk the green pass is the walk's success line.
    """
    standalone = StepContext()
    assert reporting_nextstep.next_after_timings(EXIT_OBJECTIVE_MET, (), None, standalone) == [
        reporting_nextstep.MSG_TIMINGS_OK,
    ]
    walk = StepContext(FullLevel.SPEED, in_walk=True, parallel=True)
    assert reporting_nextstep.next_after_timings(EXIT_OBJECTIVE_MET, (), None, walk) == [
        reporting_nextstep.success_line(FullLevel.SPEED),
    ]
    assert reporting_nextstep.next_after_timings(EXIT_TEST_FAILURES, _FAILING, None, walk) == [
        reporting_nextstep.timings_failed_line(FullLevel.SPEED, _FAILING),
    ]
    assert reporting_nextstep.next_after_timings(EXIT_SUITE_CRASH, (), None, walk) == []


def test_timings_failed_line_names_the_focus_run_and_the_restart() -> None:
    """A timing-pass failure is fixed with ghog single, then the walk restarts."""
    line = reporting_nextstep.timings_failed_line(FullLevel.SPEED, _FAILING)
    assert "ghog single tests/test_a.py tests/test_b.py --full=speed --whole-suite" in line
    assert line.endswith("then ghog day --full=speed --whole-suite")


def test_next_after_timings_outliers_names_the_fix_and_the_exclusion() -> None:
    """Exit 8 from the sequential pass carries the same outlier guidance."""
    summary = _summary(outliers=(_OUTLIER,))
    context = StepContext(FullLevel.SPEED, in_walk=True)
    lines = reporting_nextstep.next_after_timings(EXIT_DURATION_OUTLIERS, (), summary, context)
    assert lines[0] == reporting_nextstep.outliers_line(FullLevel.SPEED)
    assert lines[0].endswith("then ghog day --full=speed --whole-suite")
    assert "ghog exclude" in lines[1]


def test_next_after_full_outliers_names_the_fix_and_the_exclusion() -> None:
    """Exit 8 lists the outlier fix step and the ghog exclude hint (Q47, Q62)."""
    summary = _summary(outliers=(_OUTLIER,))
    context = StepContext(FullLevel.SPEED)
    lines = reporting_nextstep.next_after_full(EXIT_DURATION_OUTLIERS, (), summary, context)
    assert lines[0] == reporting_nextstep.outliers_line(FullLevel.SPEED)
    # The reworded hint names the add-exclusion command and the investigation,
    # not raising line 2; the floor it would otherwise raise is still shown.
    assert "ghog exclude" in lines[1]
    assert "fix_slow_test.md" in lines[1]
    assert "a.ghog.outliers in the artifact home" in lines[1]
    assert f"{_FLOOR:.2f}s" in lines[1]
    assert lines[1].endswith("accepted only after an attempted improvement")


def test_outlier_hint_names_the_floor_file_location() -> None:
    """The hint names the floor file where the verdict says it lives."""
    location = "C:/work/project/.reviews/a.ghog.outliers"
    summary = replace(_summary(outliers=(_OUTLIER,)), floor_file=location)
    lines = reporting_nextstep.next_after_full(EXIT_DURATION_OUTLIERS, (), summary, StepContext(FullLevel.SPEED))
    assert f"not raise line 2 of {location} (" in lines[1]


def test_next_after_full_outliers_without_a_summary() -> None:
    """The exclusion hint falls back to a zero floor without a summary (Q47)."""
    lines = reporting_nextstep.next_after_full(EXIT_DURATION_OUTLIERS, (), None, StepContext(FullLevel.SPEED))
    assert lines[0] == reporting_nextstep.outliers_line(FullLevel.SPEED)
    assert "ghog exclude" in lines[1]
    assert "0.00s" in lines[1]


def test_next_after_affected_cov_per_exit_code() -> None:
    """The covered affected-run next step follows the table at its level."""
    assert reporting_nextstep.next_after_affected_cov(EXIT_OBJECTIVE_MET, FullLevel.NONE) == [
        reporting_nextstep.MSG_AFFECTED_COV_OK.replace("ghog check", "ghog check --whole-suite"),
    ]
    (reached,) = reporting_nextstep.next_after_affected_cov(EXIT_OBJECTIVE_MET, FullLevel.COV)
    assert "finish with ghog check --full=cov --whole-suite" in reached
    assert reached.endswith("then ghog day --full=cov --whole-suite")
    assert reporting_nextstep.next_after_affected_cov(EXIT_COVERAGE_GAP, FullLevel.COV) == [
        reporting_nextstep.coverage_gap_line(FullLevel.COV),
    ]
    assert reporting_nextstep.next_after_affected_cov(EXIT_TEST_FAILURES, FullLevel.NONE) == [
        reporting_nextstep.affected_fail_line(FullLevel.NONE),
    ]
    assert reporting_nextstep.next_after_affected_cov(EXIT_SUITE_CRASH, FullLevel.NONE) == []


def test_next_after_affected_nocov() -> None:
    """A walk owns its green step; a standalone run keeps or restarts by level."""
    standalone = StepContext()
    assert reporting_nextstep.next_after_affected_nocov(failed=False, context=standalone) == [
        reporting_nextstep.MSG_AFFECTED_NOCOV_OK + " --whole-suite",
    ]
    carried = StepContext(FullLevel.COV)
    assert reporting_nextstep.next_after_affected_nocov(failed=False, context=carried) == [
        "Next: ghog day --full=cov --whole-suite",
    ]
    walk = StepContext(FullLevel.NONE, in_walk=True)
    assert reporting_nextstep.next_after_affected_nocov(failed=False, context=walk) == []
    assert reporting_nextstep.next_after_affected_nocov(failed=True, context=carried) == [
        reporting_nextstep.affected_fail_line(FullLevel.COV),
    ]


def test_next_after_check() -> None:
    """The check next step covers missing, green and failing (Q10)."""
    assert reporting_nextstep.next_after_check(code=0, missing=True, level=FullLevel.NONE) == [
        reporting_nextstep.MSG_CHECK_MISSING,
        reporting_nextstep.MSG_CHECK_OK + " --whole-suite",
    ]
    assert reporting_nextstep.next_after_check(code=0, missing=False, level=FullLevel.SPEED) == [
        "Next: ghog affected --no-cov --full=speed --whole-suite",
    ]
    assert reporting_nextstep.next_after_check(code=1, missing=False, level=FullLevel.SPEED) == [
        reporting_nextstep.check_fail_line(FullLevel.SPEED),
    ]


def test_post_fix_messages_restart_at_ghog_day() -> None:
    """Every post-fix next-step message names ghog day (Q30), at its level.

    The walk is the loop's only re-entry point and opens with the
    compile check, so no message may prescribe a standalone subcommand
    re-run before it. No line ever prints a none level selector; above none
    every line carries the level.
    """
    for level in FullLevel:
        post_fix_messages = (
            reporting_nextstep.check_fail_line(level),
            reporting_nextstep.affected_fail_line(level),
            reporting_nextstep.single_restart_line(level),
            reporting_nextstep.single_green_line(level),
            reporting_nextstep.outliers_line(level),
            reporting_nextstep.timings_failed_line(level, _FAILING),
        )
        for message in post_fix_messages:
            assert "ghog day" in message
            assert "re-run ghog check" not in message
            assert _NONE_SELECTOR not in message
            if level is not FullLevel.NONE:
                assert f"ghog day --full={level.token}" in message
        crash = reporting.crash_block(RunStats(), (), level)
        assert crash[-1].endswith(f"Then re-run {reporting_nextstep.restart_command(level)}.")
    assert reporting.crash_block(RunStats(), ())[-1].endswith("Then re-run ghog day --whole-suite.")


def test_single_green_line_names_what_the_walk_reproves() -> None:
    """At none the walk re-proves check and affected; at a level also full."""
    assert reporting_nextstep.single_green_line(FullLevel.NONE) == (
        "Next: ghog day --whole-suite (the walk re-proves check and affected)"
    )
    assert reporting_nextstep.single_green_line(FullLevel.COV) == (
        "Next: ghog day --full=cov --whole-suite (the walk re-proves check, affected and full)"
    )


def test_comparison_lines_without_baseline() -> None:
    """No baseline yields the comparison-skipped notice (Q18), at its level."""
    assert reporting_nextstep.comparison_lines(None, failed=True, level=FullLevel.NONE) == [
        "no full-run baseline, comparison skipped; run ghog full --whole-suite for suite-level truth",
    ]
    for level in (FullLevel.PASS, FullLevel.COV, FullLevel.SPEED):
        (line,) = reporting_nextstep.comparison_lines(None, failed=False, level=level)
        assert line == reporting_nextstep.no_baseline_line(level)
        assert f"run ghog full --full={level.token} --whole-suite for suite-level truth" in line
    assert _NONE_SELECTOR not in reporting_nextstep.no_baseline_line(FullLevel.NONE)


def test_comparison_lines_with_both_lists() -> None:
    """The two Q07 lists and the restart step are rendered."""
    comparison = FocusComparison(
        still_failing=("tests/test_a.py::test_one",),
        suspects=("tests/test_a.py::test_two",),
    )
    lines = reporting_nextstep.comparison_lines(comparison, failed=True, level=FullLevel.COV)
    assert lines[0] == "Still failing in focus (fix these first):"
    assert "- tests/test_a.py::test_one" in lines
    assert "- tests/test_a.py::test_two" in lines
    assert lines[-1] == reporting_nextstep.single_restart_line(FullLevel.COV)


def test_comparison_lines_green_focus() -> None:
    """A green focus run renders none markers and the restart chain."""
    comparison = FocusComparison(still_failing=(), suspects=())
    lines = reporting_nextstep.comparison_lines(comparison, failed=False, level=FullLevel.COV)
    assert lines.count("- none") == len(("still", "suspects"))
    assert lines[-1] == "Next: ghog day --full=cov --whole-suite (the walk re-proves check, affected and full)"


# eof
