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

Fix: add the exit-9 wording of a project with no pytest suite: the reason
line says the pytest steps do not apply and that nothing needs installing,
and the next step sends the caller to the project's own test commands. The
missing-pytest reason (Q21) moves here too, so ``commands.py`` keeps its line
budget.

Fix: the exit-8 exclusion hint names the floor file at its real location, the
artifact home path the verdict carries, instead of a bare ``a.ghog.outliers``
that read as a project-root file. Still pure: the location comes in with the
verdict, never from IO here.

Fix (v0.13.0 full_suite_levels, Step 2): every fixed restart string becomes a
builder fed by one helper, :func:`restart_command`, so the carried level
travels through the whole repair loop: ``ghog day --full=<level>``, or plain
``ghog day`` at ``none``, whose selector is empty, so no line ever prints a
``none`` level. Each repair command the report sends the caller to carries
``--full=<level>`` the same way (:func:`carried_selector`). Success lines are
one per level (:func:`success_line`), the noop line names the requested level
and the saved proof (:func:`noop_line`), and a green parallel ``speed`` full
run outside a walk says durations were not measured. A :class:`StepContext`
carries the level, the walk flag and the parallel flag, so a step inside a day
walk leaves its next step to the walk and a standalone ``ghog affected
--no-cov`` with no carried level keeps ``Next: ghog full``. A focus run
without a failure baseline names ``ghog full`` with the carried level
(:func:`no_baseline_line`), so the run that writes the baseline keeps the
selected objective.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.groundhog.levels import ACCEPTED_LEVELS, FullLevel, level_selector
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

# The restart command every post-fix line names (Q30).
_DAY: Final = "ghog day"
# The scope every Step 2 success line names: groups arrive with Step 4.
_WHOLE_SUITE: Final = "the whole suite"
# Next-step messages of the run-state table in the spec.
MSG_CHECK_OK: Final = "Next: ghog affected --no-cov"
MSG_CHECK_MISSING: Final = (
    "check.bat not found - skipped; pytest collection will catch compile errors"
)
MSG_CHECK_EXIT_MISMATCH: Final = (
    "check.bat printed ERROR lines but exited 0 - treating the check as "
    "failed; fix check.bat so it exits with its failed status (Q26)"
)
MSG_NO_PYTEST: Final = (
    "ghog: pytest not found on PATH; "
    "run through the ghog wrapper so senv.bat loads the project venv (Q21)."
)
MSG_NOT_PYTEST_PROJECT: Final = (
    "ghog: not a pytest project - no pyproject.toml, pytest.ini or conftest.py, "
    "and no pytest section in setup.cfg or tox.ini at the project root; the "
    "pytest steps do not apply. This is not a setup error: do not install "
    "pytest or create a venv to get past it"
)
MSG_NOT_PYTEST_PROJECT_NEXT: Final = (
    "Next: no ghog step left - validate with the project's own test commands; "
    "in a ghog day walk, the check step above was the whole groundhog verdict"
)
# The standalone ptanc next step when no level is carried.
MSG_AFFECTED_NOCOV_OK: Final = "Next: ghog full"
MSG_NO_TESTS_RUN: Final = (
    "0 tests ran in this step (testmon: nothing affected since the last run) "
    "- treated as green"
)
MSG_GAP_LINES_HEADER: Final = "Uncovered lines (file and ranges are the covg input):"
# The floor file named by the exclusion hint when the verdict carries no
# location: it lives in the artifact home, never at the project root.
_FLOOR_FILE_IN_HOME: Final = "a.ghog.outliers in the artifact home (.reviews by default)"
MSG_TIMINGS_OK: Final = "Duration gate clean; the parallel walk carries the rest"
# The covered standalone affected run at no carried level (unchanged).
MSG_AFFECTED_COV_OK: Final = (
    "Coverage gate reached - no ghog full needed; "
    "finish with ghog check (new tests are code too)"
)
# The focus-run notice without a failure baseline: the full run that writes
# one carries the level (filled in by :func:`no_baseline_line`).
_NO_BASELINE: Final = (
    "no full-run baseline, comparison skipped; run ghog full{selector} for "
    "suite-level truth"
)
# A green parallel full run outside a walk never measured durations.
MSG_SPEED_NOT_MEASURED: Final = (
    "Durations were not measured: the parallel full run carries no timing "
    "pass, so the speed objective is not established; prove it with "
    "ghog day --full=speed"
)
# The per-level success lines, each naming its scope (filled in by
# :func:`success_line`); ``none`` is the skip line of the default walk.
_SUCCESS: Final = {
    FullLevel.NONE: (
        "Full suite skipped on purpose (no level requested): check.bat and the "
        "affected tests of {scope} are green; do not run the full suite unless "
        "the calling instruction asks for a level: {choices}; carry on with "
        "the calling instruction"
    ),
    FullLevel.PASS: (
        "Objective met at pass for {scope}: every test passes; the coverage and "
        "duration gates are not required by this objective; carry on with the "
        "calling instruction"
    ),
    FullLevel.COV: (
        "Objective met at cov for {scope}: every test passes and the coverage "
        "gate over its sources is met; the duration gate is not required by "
        "this objective; carry on with the calling instruction"
    ),
    FullLevel.SPEED: (
        "Objective met at speed for {scope}: every test passes, the coverage "
        "gate over its sources is met, and no unaccepted duration outlier "
        "remains under the configured exclusions; carry on with the calling "
        "instruction"
    ),
}


@dataclass(frozen=True)
class StepContext:
    """What a step's next-step lines need beyond its exit code.

    Attributes:
        level: The carried level the restart lines name.
        in_walk: Whether the step runs inside a day walk, which then owns
            the next step.
        parallel: Whether the project runs its full suite on xdist workers.
    """

    level: FullLevel = FullLevel.NONE
    in_walk: bool = False
    parallel: bool = False


def restart_command(level: FullLevel, scope_selector: str = "") -> str:
    """Render the walk restart every post-fix line names (Q30).

    Args:
        level: The carried level; ``none`` adds no level selector.
        scope_selector: The scope selector to carry, empty for none.

    Returns:
        ``ghog day``, then ``--full=<level>`` above ``none``, then the scope
        selector when given.
    """
    parts = (_DAY, level_selector(level), scope_selector)
    return " ".join(part for part in parts if part)


def carried_selector(level: FullLevel) -> str:
    """Render the level suffix a repair command carries.

    Args:
        level: The carried level.

    Returns:
        `` --full=<level>`` with its leading space, empty at ``none``.
    """
    selector = level_selector(level)
    return f" {selector}" if selector else ""


def success_line(level: FullLevel) -> str:
    """Render the success line of one level, naming its scope.

    Args:
        level: The level the walk or run met.

    Returns:
        The skip line at ``none``, else the objective-met line of the level.
    """
    choices = ", ".join(restart_command(choice) for choice in ACCEPTED_LEVELS)
    return _SUCCESS[level].format(scope=_WHOLE_SUITE, choices=choices)


def noop_line(requested: FullLevel, saved: FullLevel) -> str:
    """Render the noop line of a day walk met by saved proof.

    Args:
        requested: The level the walk was asked to prove.
        saved: The valid saved proof that meets it.

    Returns:
        The line naming the requested level, the scope and the saved proof,
        and saying nothing ran, not even check.bat.
    """
    return (
        f"Requested objective {requested.token} for {_WHOLE_SUITE} is met by "
        f"saved proof at {saved.token} on unchanged sources - nothing ran in "
        "this invocation, not even check.bat (use --force to walk anyway)"
    )


def check_fail_line(level: FullLevel) -> str:
    """Render the compile-error next step, restarting at the carried level.

    Args:
        level: The carried level.

    Returns:
        The next step naming the walk restart.
    """
    return (
        f"Next: fix the compile errors above, re-run {restart_command(level)} "
        "(the walk opens with this check)"
    )


def affected_fail_line(level: FullLevel) -> str:
    """Render the affected-failure next step, carrying the level.

    Args:
        level: The carried level.

    Returns:
        The next step naming the ptanc repair and the walk restart.
    """
    return (
        f"Next: fix these, re-run ghog affected --no-cov{carried_selector(level)} "
        f"until green, then {restart_command(level)}"
    )


def coverage_gap_line(level: FullLevel) -> str:
    """Render the coverage-gap next step, carrying the level.

    Args:
        level: The carried level.

    Returns:
        The covg next step naming the covered affected verification.
    """
    return (
        "Next: covg <file> <ranges> to name the uncovered functions "
        "(use the Missing column above, never a coverage.json export), "
        f"add tests, verify with ghog affected{carried_selector(level)}"
    )


def outliers_line(level: FullLevel) -> str:
    """Render the exit-8 next step (Q47), restarting at the carried level.

    Fix only the calls above the floor, confirm the new time alone, then
    restart the walk (Q30). Named ghog day, never a standalone re-run before
    the walk's compile check. Points at the dedicated fix-slow-test
    instruction so the per-call procedure is acted upon whatever flow ran the
    walk.

    Args:
        level: The carried level.

    Returns:
        The outlier next step.
    """
    return (
        "Next: a call only slightly above the floor will flap on the next jitter, "
        "so do not just re-measure - shorten each call listed above the floor (how "
        "to: <llm-shared>/instructions/fix_slow_test.md) until it lands well below "
        "the floor with margin to spare, confirm it alone with ghog single "
        f"<file>{carried_selector(level)}, then {restart_command(level)}"
    )


def no_baseline_line(level: FullLevel) -> str:
    """Render the focus-run notice when no full run left a failure baseline.

    Args:
        level: The carried level, so the full run that writes the baseline
            keeps the selected objective.

    Returns:
        The notice naming ``ghog full`` with the level selector, plain at
        ``none``.
    """
    return _NO_BASELINE.format(selector=carried_selector(level))


def single_restart_line(level: FullLevel) -> str:
    """Render the failing focus-run next step, carrying the level.

    Args:
        level: The carried level.

    Returns:
        The line keeping the caller on ghog single, then restarting the walk.
    """
    return (
        f"Stay on ghog single{carried_selector(level)} until green, then restart "
        f"the walk: {restart_command(level)}"
    )


def single_green_line(level: FullLevel) -> str:
    """Render the green focus-run next step, restarting at the carried level.

    Args:
        level: The carried level.

    Returns:
        The walk restart, naming what the walk re-proves at that level.
    """
    proves = "check and affected" if level is FullLevel.NONE else "check, affected and full"
    return f"Next: {restart_command(level)} (the walk re-proves {proves})"


def timings_failed_line(level: FullLevel, failing_files: Sequence[str]) -> str:
    """Render the next step of a failure inside the sequential timing pass.

    A failure there is a real failure, fixed with ghog single before any
    duration verdict is trusted.

    Args:
        level: The carried level.
        failing_files: The unique failing test files, for the focus run.

    Returns:
        The next step naming the focus run and the walk restart.
    """
    files = "".join(f" {name}" for name in failing_files)
    return (
        "Next: a failure in the sequential timing pass is a real failure; fix it "
        f"with ghog single{files}{carried_selector(level)} before trusting any "
        f"duration verdict, then {restart_command(level)}"
    )


def next_after_timings(
    exit_code: int,
    failing_files: Sequence[str],
    summary: DurationSummary | None,
    context: StepContext,
) -> list[str]:
    """Build the next-step lines after a sequential ``ghog timings`` run.

    Inside a ``speed`` day walk the green pass is the walk's success; a
    standalone pass keeps its own line.

    Args:
        exit_code: The groundhog exit code of the run.
        failing_files: The unique failing test files, for the focus hint.
        summary: The duration verdict, for the exclusion hint on exit 8.
        context: The carried level and the walk flag.

    Returns:
        The next-step lines of the run-state table.
    """
    if exit_code == EXIT_DURATION_OUTLIERS:
        return [outliers_line(context.level), _exclusion_hint(summary)]
    if exit_code == EXIT_TEST_FAILURES:
        return [timings_failed_line(context.level, failing_files)]
    if exit_code == EXIT_OBJECTIVE_MET:
        if context.in_walk:
            return [success_line(context.level)]
        return [MSG_TIMINGS_OK]
    return []


def next_after_full(
    exit_code: int,
    failing_files: Sequence[str],
    summary: DurationSummary | None,
    context: StepContext,
) -> list[str]:
    """Build the next-step lines after a ``ghog full`` run.

    Args:
        exit_code: The groundhog exit code of the run.
        failing_files: The unique failing test files, for the focus hint.
        summary: The duration verdict, for the floor-override hint on exit 8.
        context: The run level, the walk flag and the parallel flag.

    Returns:
        The next-step lines of the run-state table.
    """
    if exit_code == EXIT_TEST_FAILURES:
        files = " ".join(failing_files)
        return [f"Next: ghog single {files}".rstrip() + carried_selector(context.level)]
    if exit_code == EXIT_COVERAGE_GAP:
        return [coverage_gap_line(context.level)]
    if exit_code == EXIT_DURATION_OUTLIERS:
        return [outliers_line(context.level), _exclusion_hint(summary)]
    if exit_code == EXIT_OBJECTIVE_MET:
        return _full_success(context)
    return []


def _full_success(context: StepContext) -> list[str]:
    """Build the success lines of a green full run.

    A parallel full run at ``speed`` never measures durations: inside a walk
    the timing pass follows and owns the success line; a direct run proves
    ``cov`` and says the speed objective is not established.

    Args:
        context: The run level, the walk flag and the parallel flag.

    Returns:
        The success lines of the run, possibly none.
    """
    if context.level is FullLevel.SPEED and context.parallel:
        if context.in_walk:
            return []
        return [success_line(FullLevel.COV), MSG_SPEED_NOT_MEASURED]
    return [success_line(context.level)]


def _exclusion_hint(summary: DurationSummary | None) -> str:
    """Build the must-stay-slow escape shown beside the outlier next step (Q62).

    Replaces the v0.2.0 "raise line 2" advice for one call: line 2 is the
    project-wide floor, so a call proven irreducible by ``fix_slow_test.md`` is
    accepted on its own with the ``ghog exclude`` command at its measured time,
    not by lifting the floor for the whole suite (Q59, Q62). A slower-drifted
    exclusion already on exit 8 is restored to within two seconds of its
    recorded baseline, the per-call instruction the exclusion block carries.

    Fix (v0.13.0 full_suite_levels, Step 2): the hint states that an exclusion
    is accepted only after an attempted improvement.

    Args:
        summary: The duration verdict, for the active floor and the floor
            file location named in the hint.

    Returns:
        The hint naming the ``ghog exclude`` command and pointing at
        ``fix_slow_test.md``, with the floor it would otherwise raise and
        the floor file's location in the artifact home.
    """
    floor_secs = summary.floor if summary is not None else 0.0
    floor_file = summary.floor_file if summary is not None else ""
    return (
        "A call that must stay slow is not a bug: once "
        "<llm-shared>/instructions/fix_slow_test.md proves it irreducible, run "
        "ghog exclude <node id> <measured seconds> to accept it at its time, "
        f"not raise line 2 of {floor_file or _FLOOR_FILE_IN_HOME} "
        f"(the {floor_secs:.2f}s suite floor); an exclusion is accepted only "
        "after an attempted improvement"
    )


def next_after_affected_cov(exit_code: int, level: FullLevel) -> list[str]:
    """Build the next-step lines after a covered ``ghog affected`` run.

    Args:
        exit_code: The groundhog exit code of the run.
        level: The carried level.

    Returns:
        The next-step lines of the run-state table; at a carried level the
        gate-reached line names ``ghog check`` then the walk restart.
    """
    if exit_code == EXIT_OBJECTIVE_MET:
        if level is FullLevel.NONE:
            return [MSG_AFFECTED_COV_OK]
        return [
            "Coverage gate reached - finish with ghog check"
            f"{carried_selector(level)} (new tests are code too), then "
            f"{restart_command(level)}",
        ]
    if exit_code == EXIT_COVERAGE_GAP:
        return [coverage_gap_line(level)]
    if exit_code == EXIT_TEST_FAILURES:
        return [affected_fail_line(level)]
    return []


def next_after_affected_nocov(*, failed: bool, context: StepContext) -> list[str]:
    """Build the next-step lines after a ``ghog affected --no-cov`` run.

    Args:
        failed: Whether the run had failing tests.
        context: The carried level and the walk flag.

    Returns:
        The next-step lines of the run-state table: none for a green step
        inside a walk, ``Next: ghog full`` for a standalone run with no
        carried level, the walk restart otherwise.
    """
    if failed:
        return [affected_fail_line(context.level)]
    if context.in_walk:
        return []
    if context.level is FullLevel.NONE:
        return [MSG_AFFECTED_NOCOV_OK]
    return [f"Next: {restart_command(context.level)}"]


def next_after_check(*, code: int, missing: bool, level: FullLevel) -> list[str]:
    """Build the next-step lines after a ``ghog check`` run.

    Args:
        code: The check.bat exit code, 0 when it was skipped.
        missing: Whether check.bat was absent (Q10).
        level: The carried level.

    Returns:
        The next-step lines of the run-state table.
    """
    green = f"{MSG_CHECK_OK}{carried_selector(level)}"
    if missing:
        return [MSG_CHECK_MISSING, green]
    return [green] if code == 0 else [check_fail_line(level)]


def comparison_lines(
    comparison: FocusComparison | None,
    *,
    failed: bool,
    level: FullLevel,
) -> list[str]:
    """Build the focus-run lines: the two Q07 lists and the next step.

    Args:
        comparison: The baseline comparison, or ``None`` without baseline.
        failed: Whether the focus run had failing tests.
        level: The carried level the restart names.

    Returns:
        The comparison and next-step lines of the run-state table.
    """
    if comparison is None:
        return [no_baseline_line(level)]
    lines = ["Still failing in focus (fix these first):"]
    lines.extend(_id_lines(comparison.still_failing))
    lines.append(
        "Passing in focus but failing in the full suite "
        "(interaction or ordering suspects, fix second):",
    )
    lines.extend(_id_lines(comparison.suspects))
    lines.append(single_restart_line(level) if failed else single_green_line(level))
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
