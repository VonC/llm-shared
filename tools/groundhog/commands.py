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
"""

from __future__ import annotations

import logging
import re
from dataclasses import replace
from typing import TYPE_CHECKING

from tools.groundhog import (
    baseline,
    durations_report,
    durations_summary,
    gate,
    init_files,
    redirect,
    reporting,
    runner,
    snapshot,
)
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    PYTEST_NO_TESTS,
    PYTEST_USAGE_ERROR,
    GroundhogError,
    Mode,
    RunStats,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.groundhog.context import Deps, Invocation
    from tools.groundhog.durations import DurationSummary
    from tools.groundhog.models import RunResult
    from tools.groundhog.render import ProgressBar

LOGGER = logging.getLogger("groundhog")

# An echos-style error line of check.bat (" ERROR : [check.bat] ..."), the
# Q26 guard against check scripts that fail but exit 0.
_CHECK_ERROR_RE = re.compile(r"^\s*ERROR\s*:")
# ANSI escape sequences of colored check.bat output, stripped before the
# guard matches and before the line is re-emitted (Q29): a real colored
# check.bat hid its ERROR lines from the Q26 guard behind color codes.
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


class _Progress:
    """Per-mode progress sink: governed LLM lines or the user bar (Q03).

    In LLM mode the cadence governor decides when a key=value line goes
    out (Q04, Q16). In user mode a tqdm bar advances per finished test
    and its postfix carries the same counters to the end of the run (Q20).
    A run that ended without crashing tops the bar off to its total, so
    the bar always closes full instead of just short of 100%.
    """

    def __init__(self, invocation: Invocation, deps: Deps) -> None:
        """Wire the sink for one run.

        Args:
            invocation: The parsed invocation, for the mode and label.
            deps: The injectable seams, for the clock and bar factory.
        """
        self._label = sub_label(invocation)
        self._mode = invocation.mode
        self._deps = deps
        self._governor = reporting.ProgressGovernor(deps.clock)
        self._bar: ProgressBar | None = None
        self._seen = 0

    def update(self, stats: RunStats) -> None:
        """Handle one statistics update from the streamed run.

        Args:
            stats: The counters parsed so far.
        """
        if self._mode is Mode.LLM:
            if self._governor.should_emit(stats):
                LOGGER.info("%s", reporting.progress_line(self._label, stats))
            return
        if self._bar is None and stats.total > 0:
            self._bar = self._deps.bar_factory(stats.total, f"ghog {self._label}")
        if self._bar is not None:
            if stats.done > self._seen:
                self._bar.update(stats.done - self._seen)
                self._seen = stats.done
            self._bar.set_postfix_str(postfix(stats))

    def finish(
        self,
        stats: RunStats,
        *,
        completed: bool,
        summary: DurationSummary | None = None,
    ) -> None:
        """Close the run with the final counters and the timing verdict (Q20).

        In LLM mode a full run emits exactly one final summary line carrying
        the ``avg=``/``outliers=`` verdict, after the governor's bare 100%
        line (Q52); any other run emits nothing here, as before.

        In user mode a completed run fills the bar to its total before closing,
        so it reads 100% even when a parameterized node id escaped the parser
        pattern; a crashed run only catches up to the parsed count (Q06). The
        closed bar carries the same verdict in its postfix (Q37).

        Args:
            stats: The final counters of the run.
            completed: Whether the child ended without crashing.
            summary: The duration verdict of a full run, or ``None``.
        """
        if self._mode is Mode.LLM:
            if summary is not None:
                LOGGER.info(
                    "%s",
                    reporting.progress_line(self._label, stats, summary),
                )
            return
        if self._bar is None:
            return
        target = stats.total if completed else stats.done
        if target > self._seen:
            self._bar.update(target - self._seen)
            self._seen = target
        self._bar.set_postfix_str(postfix(stats, summary))
        self._bar.close()


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
            emit_summary([reporting.MSG_CHECK_EXIT_MISMATCH])
            code = 1
    emit_summary(reporting.next_after_check(code=code, missing=missing))
    closing = reporting.closing_line(
        invocation.root.name,
        runner.SUB_CHECK,
        RunStats(),
        code,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    emit_summary([closing])
    return code


def run_tests(invocation: Invocation, deps: Deps) -> int:
    """Run one pytest subcommand: full, affected or single.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The contract exit code (Q12).
    """
    pytest_exe = deps.which("pytest")
    if pytest_exe is None:
        return _setup_exit_no_pytest(invocation)
    if invocation.sub == runner.SUB_FULL:
        runner.reset_testmon(invocation.root)
    command = runner.pytest_command(
        pytest_exe,
        invocation.sub,
        no_cov=invocation.no_cov,
        files=invocation.files,
    )
    progress = _Progress(invocation, deps)
    config = runner.StreamConfig(
        command=command,
        cwd=invocation.root,
        popen_factory=deps.popen_factory,
    )
    result = runner.run_pytest(config, progress.update)
    gate_value = (
        gate.read_coverage_gate(invocation.root)
        if _measures_coverage(invocation)
        else None
    )
    # Judge outliers last (Q34): the base code gates the verdict, so a failure
    # or a gap keeps its own exit code and withholds the timing verdict.
    base_code = classify(invocation, result, gate_value)
    summary = durations_summary.judge(invocation, result, base_code)
    progress.finish(result.stats, completed=not result.crashed, summary=summary)
    if invocation.sub == runner.SUB_FULL and not result.crashed:
        baseline.write_baseline(invocation.root, result.stats.failed_ids)
    outlier_count = 0 if summary is None else len(summary.outliers)
    exit_code = classify(invocation, result, gate_value, outlier_count)
    _report(invocation, result, exit_code, gate_value, summary)
    return exit_code


def run_day(invocation: Invocation, deps: Deps) -> int:
    """Walk the whole chain: check, affected --no-cov, full (Q22).

    The walk stops at the first non-green step, whose report already
    names the fix to apply; the fixing, and the loop around it, stay
    with the caller. A missing check.bat skips to the test steps (Q10).
    A walk whose source snapshot matches the last green walk is a noop
    (Q28), unless forced, so chained instructions may call it twice for
    free; a fully green walk records the new snapshot.

    Args:
        invocation: The parsed invocation.
        deps: The injectable seams.

    Returns:
        The exit code of the first non-green step, or the full run's.
    """
    if not invocation.force and snapshot.is_unchanged(invocation.root):
        emit_summary([reporting.MSG_DAY_NOOP])
        closing = reporting.closing_line(
            invocation.root.name,
            runner.SUB_DAY,
            RunStats(),
            EXIT_OBJECTIVE_MET,
            reporting.ClosingMetrics(reporting.COV_SKIPPED),
        )
        emit_summary([closing])
        return EXIT_OBJECTIVE_MET
    code = run_check(replace(invocation, sub=runner.SUB_CHECK), deps)
    if code != EXIT_OBJECTIVE_MET:
        return code
    code = run_tests(
        replace(invocation, sub=runner.SUB_AFFECTED, no_cov=True),
        deps,
    )
    if code != EXIT_OBJECTIVE_MET:
        return code
    code = run_tests(
        replace(invocation, sub=runner.SUB_FULL, no_cov=False),
        deps,
    )
    if code == EXIT_OBJECTIVE_MET:
        snapshot.write_marker(invocation.root)
    return code


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
        emit_summary([f"ghog: {error}"])
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
    emit_summary([closing])
    return code


def _setup_exit_no_pytest(invocation: Invocation) -> int:
    """Report the missing-pytest setup error (Q21).

    Args:
        invocation: The parsed invocation.

    Returns:
        ``EXIT_SETUP_ERROR``.
    """
    emit_summary(
        [
            "ghog: pytest not found on PATH; "
            "run through the ghog wrapper so senv.bat loads the project venv (Q21).",
        ],
    )
    closing = reporting.closing_line(
        invocation.root.name,
        sub_label(invocation),
        RunStats(),
        EXIT_SETUP_ERROR,
        reporting.ClosingMetrics(reporting.COV_SKIPPED),
    )
    emit_summary([closing])
    return EXIT_SETUP_ERROR


def _measures_coverage(invocation: Invocation) -> bool:
    """Tell whether the invocation measures coverage.

    Args:
        invocation: The parsed invocation.

    Returns:
        True for ``full`` and covered ``affected`` runs.
    """
    covered_subs = (runner.SUB_FULL, runner.SUB_AFFECTED)
    return invocation.sub in covered_subs and not invocation.no_cov


def classify(
    invocation: Invocation,
    result: RunResult,
    gate_value: float | None,
    outlier_count: int = 0,
) -> int:
    """Map a run result to the contract exit code (Q12).

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        gate_value: The coverage gate, ``None`` for uncovered runs.
        outlier_count: The flagged-outlier count, judged last (Q34).

    Returns:
        The contract exit code; exit 8 only on a run already green on tests
        and coverage that still carries a true outlier (Q34).
    """
    if result.crashed:
        return EXIT_SUITE_CRASH
    if result.pytest_exit == PYTEST_USAGE_ERROR:
        return EXIT_SETUP_ERROR
    if result.pytest_exit == PYTEST_NO_TESTS:
        return _classify_no_tests(invocation, result, gate_value)
    if result.stats.failed > 0:
        return EXIT_TEST_FAILURES
    code = _classify_coverage(result.stats.cov_percent, gate_value)
    if code == EXIT_OBJECTIVE_MET and outlier_count > 0:
        return EXIT_DURATION_OUTLIERS
    return code


def _classify_no_tests(
    invocation: Invocation,
    result: RunResult,
    gate_value: float | None,
) -> int:
    """Classify a run that collected no tests.

    An ``affected`` run with nothing affected is a green step; an empty
    ``full`` or ``single`` run is a setup error.

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        gate_value: The coverage gate, ``None`` for uncovered runs.

    Returns:
        The contract exit code.
    """
    if invocation.sub != runner.SUB_AFFECTED:
        return EXIT_SETUP_ERROR
    if gate_value is not None and result.stats.cov_percent is not None:
        return _classify_coverage(result.stats.cov_percent, gate_value)
    return EXIT_OBJECTIVE_MET


def _classify_coverage(cov_percent: float | None, gate_value: float | None) -> int:
    """Classify a green run against the coverage gate (Q14, Q19).

    Args:
        cov_percent: The parsed TOTAL percentage, ``None`` on a miss.
        gate_value: The coverage gate, ``None`` for uncovered runs.

    Returns:
        The contract exit code; a TOTAL parse miss is the loud exit 5.
    """
    if gate_value is None:
        return EXIT_OBJECTIVE_MET
    if cov_percent is None:
        return EXIT_SETUP_ERROR
    if cov_percent < gate_value:
        return EXIT_COVERAGE_GAP
    return EXIT_OBJECTIVE_MET


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
    emit_summary(_next_steps(invocation, result, exit_code, summary))
    if exit_code == EXIT_SETUP_ERROR and not result.crashed:
        emit_summary([setup_reason(result, measured=measured)])
    if exit_code == EXIT_OBJECTIVE_MET and measured:
        nag = reporting.nag_line(result.stats)
        if nag is not None:
            emit_summary([nag])
    closing = reporting.closing_line(
        invocation.root.name,
        sub_label(invocation),
        result.stats,
        exit_code,
        reporting.ClosingMetrics(
            reporting.cov_text(result.stats, measured=measured),
            reporting.outliers_text(
                result.stats,
                summary,
                measured=durations_summary.measures_durations(invocation),
            ),
        ),
    )
    emit_summary([closing])


def _report_run_context(
    invocation: Invocation,
    result: RunResult,
    exit_code: int,
    summary: DurationSummary | None,
) -> None:
    """Print the fixing material of the run, before the next-step lines.

    The crash block (Q06), the failure context (Q08), the coverage-gap rows
    (Q24), the zero-test note of an unaffected run (Q27), and the bounded
    duration window of a green full run (Q47).

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        exit_code: The contract exit code.
        summary: The duration verdict of a full run, or ``None``.
    """
    if result.crashed:
        emit(reporting.crash_block(result.stats, result.tail))
    elif result.stats.failed > 0:
        emit(result.failure_block)
    if exit_code == EXIT_COVERAGE_GAP and result.coverage_block:
        emit([reporting.MSG_GAP_LINES_HEADER, *result.coverage_block])
    if (
        invocation.sub == runner.SUB_AFFECTED
        and exit_code == EXIT_OBJECTIVE_MET
        and result.stats.done == 0
    ):
        emit([reporting.MSG_NO_TESTS_RUN])
    if summary is not None:
        emit(durations_report.window_lines(summary))


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
        return reporting.next_after_full(exit_code, failing, summary)
    if invocation.sub == runner.SUB_AFFECTED:
        if invocation.no_cov:
            return reporting.next_after_affected_nocov(
                failed=result.stats.failed > 0,
            )
        return reporting.next_after_affected_cov(exit_code)
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
    return reporting.comparison_lines(
        comparison,
        failed=result.stats.failed > 0,
    )


def setup_reason(result: RunResult, *, measured: bool) -> str:
    """Name the failing precondition of a setup-error exit.

    Args:
        result: The parsed run result.
        measured: Whether the run measured coverage.

    Returns:
        The reason line of the run-state table.
    """
    if result.pytest_exit == PYTEST_USAGE_ERROR:
        return "ghog: pytest usage error; check the command and project configuration."
    if result.pytest_exit == PYTEST_NO_TESTS:
        return "ghog: no tests collected; check the test files and arguments."
    if measured and result.stats.cov_percent is None:
        return "ghog: coverage TOTAL line not found; cannot judge the gate (Q19)."
    return "ghog: setup error."


def sub_label(invocation: Invocation) -> str:
    """Return the subcommand label of the progress and closing lines.

    Args:
        invocation: The parsed invocation.

    Returns:
        The label, ``affected --no-cov`` for the ptanc variant.
    """
    if invocation.sub == runner.SUB_AFFECTED and invocation.no_cov:
        return f"{runner.SUB_AFFECTED} --no-cov"
    return invocation.sub


def postfix(stats: RunStats, summary: DurationSummary | None = None) -> str:
    """Build the user-bar postfix carrying the runtime counters (Q20).

    Args:
        stats: The counters parsed so far.
        summary: The duration verdict of a full run, for the closed bar (Q37).

    Returns:
        The postfix text, with the coverage percentage once parsed and the
        ``avg=``/``outliers=`` verdict once the run is judged.
    """
    text = f"fail={stats.failed} warn={stats.warnings} xfail={stats.xfailed}"
    if stats.cov_percent is not None:
        text = f"{text} cov={reporting.format_percent(stats.cov_percent)}"
    if summary is not None:
        text = f"{text} {reporting.progress_suffix(summary)}"
    return text


def emit(lines: Sequence[str]) -> None:
    """Print report lines through the message-only stdout logger.

    Args:
        lines: The lines to print.
    """
    for line in lines:
        emit_line(line)


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
