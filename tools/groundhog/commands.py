"""Subcommand executors of the groundhog CLI.

Split out of ``cli.py`` so the entry point stays under the repo line
budget: this module runs the subcommands — check (Q10, Q26, Q29), the
pytest runs, the day walk (Q22, Q28) and init (Q23, Q25) — classifies
their results into the exit-code contract (Q12), and assembles the final
reports (next-step messages, crash block, coverage-gap rows, nag and
closing lines). The envelope lines — next step, setup reason, nag and
closing — go through ``emit_summary``, which mirrors them to the captured
stdout when the Q31 self-redirect guard armed, so an unredirected LLM
caller still branches without reading the log.

Fix: the pytest steps first ask the ``pytest_project`` seam whether the root
has a pytest suite at all. A project with none exits 9 with its own reason and
next step, instead of the missing-pytest setup error that blamed senv.bat.

Fix (v0.13.0 full_suite_levels, Step 1): the exit-code classification and
setup reasons moved to ``verdicts.py``, the progress sink, postfix and
subcommand label to ``progress.py``, with no behavior change, so this module
keeps headroom for the level-shaped runs of the next steps.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from tools.groundhog import (
    baseline,
    durations_report,
    durations_summary,
    gate,
    init_files,
    progress,
    redirect,
    reporting,
    reporting_nextstep,
    runner,
    verdicts,
)
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_NOT_PYTEST_PROJECT,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    GroundhogError,
    RunStats,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.groundhog.context import Deps, Invocation
    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunResult

LOGGER = logging.getLogger("groundhog")

# An echos-style error line of check.bat (" ERROR : [check.bat] ..."), the
# Q26 guard against check scripts that fail but exit 0.
_CHECK_ERROR_RE = re.compile(r"^\s*ERROR\s*:")
# ANSI escape sequences of colored check.bat output, stripped before the
# guard matches and before the line is re-emitted (Q29): a real colored
# check.bat hid its ERROR lines from the Q26 guard behind color codes.
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def run_check(invocation: Invocation, deps: Deps) -> int:
    """Run the ``ghog check`` subcommand (Q10).

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        check.bat's exit code, or 0 when check.bat is absent.
    """
    check_bat = invocation.root / "check.bat"
    missing = not check_bat.is_file()
    if missing:
        code = EXIT_OBJECTIVE_MET
    else:
        config = runner.StreamConfig(
            command=["cmd.exe", "/d", "/c", str(check_bat)],
            cwd=invocation.root,
            popen_factory=deps.popen_factory,
        )
        error_lines_seen = False

        def _stream_check_line(line: str) -> None:
            nonlocal error_lines_seen
            plain = _ANSI_ESCAPE_RE.sub("", line)
            if _CHECK_ERROR_RE.match(plain):
                error_lines_seen = True
            emit_line(plain)

        code = runner.run_streaming(config, _stream_check_line)
        if code == 0 and error_lines_seen:
            emit_summary(_section([reporting_nextstep.MSG_CHECK_EXIT_MISMATCH]))
            code = 1
    emit_summary(_section(reporting_nextstep.next_after_check(code=code, missing=missing)))
    closing = reporting.closing_line(
        invocation.root.name,
        runner.SUB_CHECK,
        RunStats(),
        code,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    emit_summary(_section([closing]))
    return code


def run_tests(invocation: Invocation, deps: Deps) -> int:
    """Run one pytest subcommand: full, affected or single.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The contract exit code (Q12); exit 9 when the root has no pytest
        suite, checked before the pytest lookup.
    """
    if not deps.pytest_project(invocation.root):
        return _exit_before_pytest(
            invocation,
            [
                reporting_nextstep.MSG_NOT_PYTEST_PROJECT,
                reporting_nextstep.MSG_NOT_PYTEST_PROJECT_NEXT,
            ],
            EXIT_NOT_PYTEST_PROJECT,
        )
    pytest_exe = deps.which("pytest")
    if pytest_exe is None:
        return _exit_before_pytest(invocation, [reporting_nextstep.MSG_NO_PYTEST], EXIT_SETUP_ERROR)
    parallel = runner.parallel_enabled(invocation.root)
    if invocation.sub == runner.SUB_FULL and not parallel:
        # A worker run carries no testmon, so it owns no map to reset and
        # must leave the affected run's database alone.
        runner.reset_testmon(invocation.root)
    command = runner.pytest_command(
        pytest_exe,
        invocation.sub,
        no_cov=invocation.no_cov,
        files=invocation.files,
        parallel=parallel,
    )
    sink = progress.Progress(invocation, deps)
    config = runner.StreamConfig(
        command=command,
        cwd=invocation.root,
        popen_factory=deps.popen_factory,
    )
    result = runner.run_pytest(config, sink.update)
    gate_value = (
        gate.read_coverage_gate(invocation.root)
        if verdicts.measures_coverage(invocation)
        else None
    )
    # Judge outliers last (Q34): the base code gates the verdict, so a failure
    # or a gap keeps its own exit code and withholds the timing verdict.
    base_code = verdicts.classify(invocation, result, gate_value)
    summary = durations_summary.judge(invocation, result, base_code)
    sink.finish(result.stats, completed=not result.crashed, summary=summary)
    if invocation.sub == runner.SUB_FULL and not result.crashed:
        baseline.write_baseline(invocation.root, result.stats.failed_ids)
    # Exit 8 fires on a slower-drifted exclusion too, already spared from outliers (Q57).
    flagged = 0 if summary is None else len(summary.outliers) + reporting.excluded_count(summary)
    exit_code = verdicts.classify(invocation, result, gate_value, flagged)
    _report(invocation, result, exit_code, gate_value, summary)
    return exit_code


def run_init(invocation: Invocation, deps: Deps) -> int:
    """Register the skill pointers in the consuming project (Q23, Q25).

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams, for the user home lookup.

    Returns:
        0 on success, the setup-error code when llm-shared is missing
        its instruction file.
    """
    try:
        lines = init_files.run_init(invocation.root, deps.home())
    except GroundhogError as error:
        emit_summary(_section([f"ghog: {error}"]))
        code = EXIT_SETUP_ERROR
    else:
        emit(lines)
        code = EXIT_OBJECTIVE_MET
    closing = reporting.closing_line(
        invocation.root.name,
        runner.SUB_INIT,
        RunStats(),
        code,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    emit_summary(_section([closing]))
    return code


def _exit_before_pytest(invocation: Invocation, lines: Sequence[str], code: int) -> int:
    """Report a pytest step that stops before spawning pytest.

    Serves the root with no pytest suite (exit 9) and the missing pytest
    executable (Q21, exit 5): both print their reason, then the closing line.

    Args:
        invocation: The parsed invocation.
        lines: The reason and next-step lines.
        code: The contract exit code of the stop.

    Returns:
        ``code``, unchanged.
    """
    emit_summary(_section(lines))
    closing = reporting.closing_line(
        invocation.root.name,
        progress.sub_label(invocation),
        RunStats(),
        code,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    emit_summary(_section([closing]))
    return code


def _report(
    invocation: Invocation,
    result: RunResult,
    exit_code: int,
    gate_value: float | None,
    summary: DurationSummary | None,
) -> None:
    """Print the final report: context, next step, nag and closing line.

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        exit_code: The contract exit code.
        gate_value: The coverage gate, ``None`` for uncovered runs.
        summary: The duration verdict of a full run, or ``None``.
    """
    measured = gate_value is not None
    _report_run_context(invocation, result, exit_code, summary)
    emit_summary(_section(_next_steps(invocation, result, exit_code, summary)))
    if exit_code == EXIT_SETUP_ERROR and not result.crashed:
        emit_summary(_section([verdicts.setup_reason(result, measured=measured)]))
    if exit_code == EXIT_OBJECTIVE_MET and measured:
        nag = reporting.nag_line(result.stats)
        if nag is not None:
            emit_summary(_section([nag]))
    times_calls = durations_summary.measures_durations(invocation)
    closing = reporting.closing_line(
        invocation.root.name,
        progress.sub_label(invocation),
        result.stats,
        exit_code,
        reporting.ClosingMetrics(
            reporting.cov_text(result.stats, measured=measured),
            reporting.outliers_text(result.stats, summary, measured=times_calls),
            reporting.excluded_text(result.stats, summary, measured=times_calls),
        ),
    )
    emit_summary(_section([closing]))


def _report_run_context(
    invocation: Invocation,
    result: RunResult,
    exit_code: int,
    summary: DurationSummary | None,
) -> None:
    """Print the fixing material of the run, before the next-step lines.

    The crash block (Q06), the failure context (Q08), the coverage-gap rows
    (Q24), the zero-test note of an unaffected run (Q27), the bounded duration
    window of a green full run (Q47), and the per-test exclusion block after it
    (Q58); the block is empty, so absent, on a run with no exclusions.

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        exit_code: The contract exit code.
        summary: The duration verdict of a full run, or ``None``.
    """
    if result.crashed:
        emit(_section(reporting.crash_block(result.stats, result.tail)))
    elif result.stats.failed > 0:
        emit(_section(result.failure_block))
    if exit_code == EXIT_COVERAGE_GAP and result.coverage_block:
        emit(
            _section(
                [reporting_nextstep.MSG_GAP_LINES_HEADER, *result.coverage_block],
            ),
        )
    if (
        invocation.sub == runner.SUB_AFFECTED
        and exit_code == EXIT_OBJECTIVE_MET
        and result.stats.done == 0
    ):
        emit(_section([reporting_nextstep.MSG_NO_TESTS_RUN]))
    if summary is not None:
        emit(["", *durations_report.window_lines(summary)])
        emit(durations_report.exclusion_block(summary))
        if exit_code == EXIT_DURATION_OUTLIERS:
            emit(durations_report.action_block(summary))


def _next_steps(
    invocation: Invocation,
    result: RunResult,
    exit_code: int,
    summary: DurationSummary | None,
) -> list[str]:
    """Build the next-step lines of the run-state table.

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        exit_code: The contract exit code.
        summary: The duration verdict of a full run, for the exit-8 hint.

    Returns:
        The next-step lines for this subcommand and outcome.
    """
    if invocation.sub == runner.SUB_FULL:
        failing = baseline.failing_files(result.stats.failed_ids)
        return reporting_nextstep.next_after_full(exit_code, failing, summary)
    if invocation.sub == runner.SUB_TIMINGS:
        return reporting_nextstep.next_after_timings(exit_code, summary)
    if invocation.sub == runner.SUB_AFFECTED:
        if invocation.no_cov:
            return reporting_nextstep.next_after_affected_nocov(
                failed=result.stats.failed > 0,
            )
        return reporting_nextstep.next_after_affected_cov(exit_code)
    return _single_lines(invocation, result)


def _single_lines(invocation: Invocation, result: RunResult) -> list[str]:
    """Build the focus-run comparison lines (Q07, Q18).

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.

    Returns:
        The two comparison lists and the next step, or the no-baseline
        notice.
    """
    baseline_ids = baseline.read_baseline(invocation.root)
    comparison = (
        None
        if baseline_ids is None
        else baseline.compare_focus(
            baseline_ids,
            invocation.files,
            result.stats.failed_ids,
        )
    )
    return reporting_nextstep.comparison_lines(
        comparison,
        failed=result.stats.failed > 0,
    )


def emit(lines: Sequence[str]) -> None:
    """Print report lines through the message-only stdout logger.

    Args:
        lines: The lines to print.
    """
    for line in lines:
        emit_line(line)


def _section(lines: Sequence[str]) -> list[str]:
    """Return lines with one leading blank separator when non-empty."""
    if not lines:
        return []
    if lines[0] == "":
        return list(lines)
    return ["", *lines]


def emit_summary(lines: Sequence[str]) -> None:
    """Print envelope lines: the report stream plus the Q31 mirror.

    The next-step, setup-reason, nag and closing lines are the branching
    material of the caller; when the self-redirect guard armed, they are
    mirrored to the captured stdout so the caller never needs a log read
    to pick its next move.

    Args:
        lines: The lines to print.
    """
    emit(lines)
    redirect.mirror(lines)


def emit_line(line: str) -> None:
    """Print one line through the message-only stdout logger.

    Args:
        line: The line to print.
    """
    LOGGER.info("%s", line)


# eof
