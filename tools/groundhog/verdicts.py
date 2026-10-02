"""Exit-code verdicts of the groundhog pytest runs (Q12).

Split out of ``commands.py`` (v0.13.0 full_suite_levels, Step 1) so the
subcommand executors keep headroom for the level-shaped runs: this module
maps one parsed run to the contract exit code, tells whether a run measures
coverage, and names the failing precondition of a setup-error exit. The
functions moved verbatim; ``measures_coverage`` is the former private
``_measures_coverage``, made public for its callers.

Fix (v0.13.0 full_suite_levels, Step 2): a ``full`` run at ``pass`` measures
no coverage (its command carries ``--no-cov``), so ``measures_coverage`` is
false for it and :func:`classify` reads no gate: a coverage gap is never
judged below the ``cov`` level.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.groundhog import runner
from tools.groundhog.levels import FullLevel, effective_level
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    PYTEST_NO_TESTS,
    PYTEST_USAGE_ERROR,
)

if TYPE_CHECKING:
    from tools.groundhog.context import Invocation
    from tools.groundhog.models import RunResult


def measures_coverage(invocation: Invocation) -> bool:
    """Tell whether the invocation measures coverage.

    Args:
        invocation: The parsed invocation.

    Returns:
        True for covered ``affected`` runs and for ``full`` runs at ``cov``
        or ``speed``; a ``full`` run at ``pass`` measures no coverage.
    """
    if invocation.sub == runner.SUB_FULL:
        level = effective_level(invocation.level, invocation.sub)
        return not invocation.no_cov and level >= FullLevel.COV
    return invocation.sub == runner.SUB_AFFECTED and not invocation.no_cov


def classify(
    invocation: Invocation,
    result: RunResult,
    gate_value: float | None,
    flagged: int = 0,
) -> int:
    """Map a run result to the contract exit code (Q12).

    Args:
        invocation: The parsed invocation.
        result: The parsed run result.
        gate_value: The coverage gate, ``None`` for uncovered runs.
        flagged: The outliers plus slower-drifted exclusions judged last, turning a green run to exit 8 (Q34, Q57).

    Returns:
        The contract exit code; exit 8 only on a run already green on tests and
        coverage that still carries a true outlier or slower-drift (Q34, Q57).
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
    if code == EXIT_OBJECTIVE_MET and flagged > 0:
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


# eof
