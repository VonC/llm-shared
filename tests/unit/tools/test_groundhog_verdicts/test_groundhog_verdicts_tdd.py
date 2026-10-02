"""Unit tests for the groundhog exit-code verdicts (Q12).

v0.13.0 full_suite_levels, Step 1: the classification, setup-reason and
outliers-last cases moved here unchanged from ``test_groundhog_cli.py`` and
``test_groundhog_commands.py``, beside the functions that moved from
``commands.py`` to ``verdicts.py``; the coverage-measure rule, now public as
``measures_coverage``, gains its own case.

Fix (v0.13.0 full_suite_levels, Step 2): a full run at ``pass`` measures no
coverage, so no gate is read below ``cov``.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from tools.groundhog import runner, verdicts
from tools.groundhog.context import Invocation
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    PYTEST_NO_TESTS,
    PYTEST_USAGE_ERROR,
    Mode,
    RunResult,
    RunStats,
)

if TYPE_CHECKING:
    from pathlib import Path

_GATE_FULL = 100.0
_GATE_LOW = 90.0


def _result(stats: RunStats, pytest_exit: int, *, crashed: bool = False) -> RunResult:
    """Build a run result for classification tests.

    Args:
        stats: The run statistics.
        pytest_exit: The pytest child exit code.
        crashed: The crash flag.

    Returns:
        The run result.
    """
    return RunResult(
        stats=stats,
        pytest_exit=pytest_exit,
        crashed=crashed,
        failure_block=(),
        tail=(),
    )


def _invocation(sub: str, *, no_cov: bool, root: Path) -> Invocation:
    """Build an invocation for direct helper tests.

    Args:
        sub: The subcommand name.
        no_cov: The coverage toggle.
        root: The project root.

    Returns:
        The invocation.
    """
    return Invocation(
        sub=sub,
        files=(),
        no_cov=no_cov,
        mode=Mode.LLM,
        root=root,
    )


def _green_full(stats: RunStats) -> RunStats:
    """Mark statistics green on tests and coverage for classification.

    Args:
        stats: The statistics to complete.

    Returns:
        The same statistics with a full coverage percentage.
    """
    stats.cov_percent = _GATE_FULL
    return stats


def test_classify_usage_error(tmp_path: Path) -> None:
    """A pytest usage error is a setup error (Q12)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    result = _result(RunStats(), PYTEST_USAGE_ERROR)
    assert verdicts.classify(invocation, result, _GATE_FULL) == EXIT_SETUP_ERROR


def test_classify_crash_wins(tmp_path: Path) -> None:
    """The crash flag beats every other signal (Q06)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    result = _result(RunStats(), 0, crashed=True)
    assert verdicts.classify(invocation, result, _GATE_FULL) == EXIT_SUITE_CRASH


def test_classify_no_tests_per_subcommand(tmp_path: Path) -> None:
    """No tests collected: green for affected, setup error elsewhere."""
    full = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    affected = _invocation(runner.SUB_AFFECTED, no_cov=False, root=tmp_path)
    bare = _result(RunStats(), PYTEST_NO_TESTS)
    assert verdicts.classify(full, bare, _GATE_FULL) == EXIT_SETUP_ERROR
    assert verdicts.classify(affected, bare, None) == EXIT_OBJECTIVE_MET
    covered = RunStats()
    covered.cov_percent = _GATE_LOW
    below = _result(covered, PYTEST_NO_TESTS)
    assert verdicts.classify(affected, below, _GATE_FULL) == EXIT_COVERAGE_GAP


def test_classify_coverage_rules(tmp_path: Path) -> None:
    """Coverage classification: gate, parse miss and gap (Q14, Q19)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    unread = _result(RunStats(), 0)
    assert verdicts.classify(invocation, unread, _GATE_FULL) == EXIT_SETUP_ERROR
    low = RunStats()
    low.cov_percent = _GATE_LOW
    assert verdicts.classify(invocation, _result(low, 0), _GATE_FULL) == (
        EXIT_COVERAGE_GAP
    )
    full = RunStats()
    full.cov_percent = _GATE_FULL
    assert verdicts.classify(invocation, _result(full, 0), _GATE_FULL) == (
        EXIT_OBJECTIVE_MET
    )
    assert verdicts.classify(invocation, _result(RunStats(), 0), None) == (
        EXIT_OBJECTIVE_MET
    )


def test_classify_failures(tmp_path: Path) -> None:
    """Failing tests classify as exit 2 before any coverage look."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    stats = RunStats()
    stats.failed = 1
    assert verdicts.classify(invocation, _result(stats, 1), _GATE_FULL) == (
        EXIT_TEST_FAILURES
    )


def test_classify_judges_outliers_last(tmp_path: Path) -> None:
    """Exit 8 only on a green run; a gap or a failure keeps its code (Q34)."""
    invocation = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    green = _result(_green_full(RunStats()), 0)
    assert verdicts.classify(invocation, green, _GATE_FULL, 1) == (
        EXIT_DURATION_OUTLIERS
    )
    assert verdicts.classify(invocation, green, _GATE_FULL, 0) == EXIT_OBJECTIVE_MET
    low = RunStats()
    low.cov_percent = 90.0
    assert verdicts.classify(invocation, _result(low, 0), _GATE_FULL, 1) == (
        EXIT_COVERAGE_GAP
    )
    failing = RunStats()
    failing.failed = 1
    assert verdicts.classify(invocation, _result(failing, 1), _GATE_FULL, 1) == (
        EXIT_TEST_FAILURES
    )


def test_setup_reason_per_precondition() -> None:
    """Every setup-error reason names its failing precondition."""
    usage = _result(RunStats(), PYTEST_USAGE_ERROR)
    assert "usage error" in verdicts.setup_reason(usage, measured=True)
    empty = _result(RunStats(), PYTEST_NO_TESTS)
    assert "no tests collected" in verdicts.setup_reason(empty, measured=True)
    unread = _result(RunStats(), 0)
    assert "TOTAL line not found" in verdicts.setup_reason(unread, measured=True)
    assert verdicts.setup_reason(unread, measured=False) == "ghog: setup error."


def test_measures_coverage_per_subcommand(tmp_path: Path) -> None:
    """Only covered full and affected runs measure coverage."""
    assert verdicts.measures_coverage(_invocation(runner.SUB_FULL, no_cov=False, root=tmp_path))
    assert verdicts.measures_coverage(_invocation(runner.SUB_AFFECTED, no_cov=False, root=tmp_path))
    assert not verdicts.measures_coverage(_invocation(runner.SUB_AFFECTED, no_cov=True, root=tmp_path))
    assert not verdicts.measures_coverage(_invocation(runner.SUB_SINGLE, no_cov=False, root=tmp_path))


def test_full_run_measures_coverage_from_cov_up(tmp_path: Path) -> None:
    """A full run at pass reads no coverage gate; cov and speed do."""
    full = _invocation(runner.SUB_FULL, no_cov=False, root=tmp_path)
    assert not verdicts.measures_coverage(replace(full, level=FullLevel.PASS))
    assert verdicts.measures_coverage(replace(full, level=FullLevel.COV))
    assert verdicts.measures_coverage(replace(full, level=FullLevel.SPEED))
    assert not verdicts.measures_coverage(replace(full, no_cov=True))


# eof
