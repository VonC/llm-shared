"""The run-state table text of a groundhog run: next steps and focus lists.

This module owns the words the run-state table prints after each step: the
next-step messages of every branch (check, affected, full, single), the
coverage-gap and no-tests notices, the day-walk noop line, the exit-8 outlier
next step with its ``ghog exclude`` escape hint (Q47, Q62), and the focus
comparison lists of a ``ghog single`` run (Q07). Pure text building, so the
whole run-state contract is unit-testable on its own.

Every next-step message that follows a fix names ``ghog day`` as the restart
(Q30): the walk is the loop's only re-entry point and opens with the compile
check, so the older ``re-run ghog check`` wording made a real session pay
check.bat twice — once standalone, once inside the resumed walk.

Fix: split out of ``reporting.py`` so that module keeps its own line budget.
``reporting.py`` had grown past the per-file limit once the duration-outlier
and per-test exclusion features each added their next-step wording here; the
run-state table is a single responsibility distinct from the progress and
closing line text that stays behind, so it moves whole into this module. Pure
string building, no IO.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.groundhog.baseline import FocusComparison
    from tools.groundhog.durations import DurationSummary

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
# standalone re-run before the walk's compile check. Points at the dedicated
# fix-slow-test instruction so the per-call procedure is acted upon whatever
# flow ran the walk.
MSG_OUTLIERS: Final = (
    "Next: a call only slightly above the floor will flap on the next jitter, "
    "so do not just re-measure - shorten each call listed above the floor (how "
    "to: <llm-shared>/instructions/fix_slow_test.md) until it lands well below "
    "the floor with margin to spare, confirm it alone with ghog single <file>, "
    "then ghog day"
)


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
        return [MSG_OUTLIERS, _exclusion_hint(summary)]
    if exit_code == EXIT_OBJECTIVE_MET:
        return [MSG_FULL_OK]
    return []


def _exclusion_hint(summary: DurationSummary | None) -> str:
    """Build the must-stay-slow escape shown beside the outlier next step (Q62).

    Replaces the v0.2.0 "raise line 2" advice for one call: line 2 is the
    project-wide floor, so a call proven irreducible by ``fix_slow_test.md`` is
    accepted on its own with the ``ghog exclude`` command at its measured time,
    not by lifting the floor for the whole suite (Q59, Q62). A slower-drifted
    exclusion already on exit 8 is restored to within two seconds of its
    recorded baseline, the per-call instruction the exclusion block carries.

    Args:
        summary: The duration verdict, for the active floor named in the hint.

    Returns:
        The hint naming the ``ghog exclude`` command and pointing at
        ``fix_slow_test.md``, with the floor it would otherwise raise.
    """
    floor_secs = summary.floor if summary is not None else 0.0
    return (
        "A call that must stay slow is not a bug: once "
        "<llm-shared>/instructions/fix_slow_test.md proves it irreducible, run "
        "ghog exclude <node id> <measured seconds> to accept it at its time, "
        f"not raise line 2 of a.ghog.outliers (the {floor_secs:.2f}s suite floor)"
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
