"""Acceptance tests of the full-suite levels (v0.13.0 full_suite_levels).

Step 2: one test per level row of the design's "Acceptance Cases", driven
through ``cli.main`` on a ``tmp_path`` project with the process boundary
faked: the default walk with its skip line; ``GHOG_FULL`` and ``--full``
resolution, precedence and their exit-5 errors (never argparse's 2); each
level's run shape and verdict, including the parallel ``speed`` timing pass
and the direct ``ghog full`` that never claims speed; the level carried by
every restart line, the no-baseline focus notice included; and the
no-argument ``ghog_cycle.bat`` running ``day`` alone.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    closing_line_of,
    passing_transcript,
)
from tests.unit.tools.test_groundhog_acceptance_levels.support import (
    AFFECTED_OK,
    CHECK_OK,
    FULL_GREEN,
    GAP_TOTAL,
    TESTS_FAILING,
    project,
    run,
    slow_transcript,
)
from tools.groundhog import baseline, reporting_nextstep
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_DURATION_OUTLIERS,
    EXIT_OBJECTIVE_MET,
    EXIT_SETUP_ERROR,
    EXIT_TEST_FAILURES,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

# The accepted values every level error names.
_ACCEPTED = "accepted values: pass, cov, speed"
# The no-argument cycle launcher at the llm-shared root.
_CYCLE = Path(__file__).resolve().parents[4] / "bin" / "ghog_cycle.bat"


def _has(out: str, *snippets: str) -> bool:
    """Tell whether every snippet appears in the captured report."""
    return all(snippet in out for snippet in snippets)


def test_default_walk_skips_the_full_suite(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A green default walk runs check and affected only, with the skip line."""
    code, spawns = run(project(tmp_path), ["day"], [CHECK_OK, AFFECTED_OK])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected"))
    out = capsys.readouterr().out
    assert reporting_nextstep.success_line(FullLevel.NONE) in out
    assert closing_line_of(out).endswith("full=none src=default proof=none reused=none scope=whole")


def test_environment_level_walks_and_restarts_explicitly(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GHOG_FULL=cov walks the covered full run and restarts with --full=cov."""
    env = {"GHOG_FULL": "cov"}
    code, spawns = run(project(tmp_path), ["day"], [CHECK_OK, AFFECTED_OK, FULL_GREEN], env)
    assert code == EXIT_OBJECTIVE_MET
    assert "--cov-report" in spawns.commands[2]
    assert closing_line_of(capsys.readouterr().out).endswith("full=cov src=env proof=cov reused=none scope=whole")
    code, _ = run(tmp_path, ["day", "--force"], [CHECK_OK, TESTS_FAILING], env)
    assert code == EXIT_TEST_FAILURES
    assert reporting_nextstep.affected_fail_line(FullLevel.COV) in capsys.readouterr().out


def test_parameter_wins_over_the_environment(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """GHOG_FULL=cov with ghog full --full=pass runs one pass run, src=param."""
    code, spawns = run(project(tmp_path), ["full", "--full=pass"], [FULL_GREEN], {"GHOG_FULL": "cov"})
    assert code == EXIT_OBJECTIVE_MET
    assert "--no-cov" in spawns.commands[0]
    assert closing_line_of(capsys.readouterr().out).endswith("full=pass src=param proof=pass scope=whole")


@pytest.mark.parametrize(
    ("argv", "environ", "origin"),
    [
        (["day"], {"GHOG_FULL": "fast"}, "'fast' from GHOG_FULL"),
        (["day", "--full=fast"], {}, "'fast' from --full"),
        (["day", "--full=none"], {}, "'none' from --full"),
    ],
)
def test_invalid_levels_exit_five_naming_the_values(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    environ: dict[str, str],
    origin: str,
) -> None:
    """An invalid variable or parameter, none included, exits 5, never 2."""
    code, spawns = run(project(tmp_path), argv, [], environ)
    assert code == EXIT_SETUP_ERROR
    assert spawns.commands == []
    assert _has(capsys.readouterr().out, origin, _ACCEPTED)


def test_valid_parameter_overrides_an_invalid_variable(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GHOG_FULL=fast is never read when --full=cov selects the level."""
    env = {"GHOG_FULL": "fast"}
    code, _ = run(project(tmp_path), ["day", "--full=cov"], [CHECK_OK, AFFECTED_OK, FULL_GREEN], env)
    assert code == EXIT_OBJECTIVE_MET
    assert "src=param proof=cov" in closing_line_of(capsys.readouterr().out)


def test_pass_level_judges_neither_coverage_nor_speed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A gap and a slow call are not judged below their levels: exit 0."""
    full = (slow_transcript(GAP_TOTAL), 0)
    code, spawns = run(project(tmp_path), ["day", "--full=pass"], [CHECK_OK, AFFECTED_OK, full])
    assert code == EXIT_OBJECTIVE_MET
    assert "--no-cov" in spawns.commands[2]
    out = capsys.readouterr().out
    assert reporting_nextstep.success_line(FullLevel.PASS) in out
    assert reporting_nextstep.coverage_gap_line(FullLevel.PASS) not in out
    assert "Duration outliers" not in out


def test_cov_level_in_a_parallel_project_runs_no_timing_pass(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--full=cov in a parallel project stops after the covered worker run."""
    root = project(tmp_path, parallel=True)
    code, spawns = run(root, ["day", "--full=cov"], [CHECK_OK, AFFECTED_OK, FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    assert len(spawns.commands) == len(("check", "affected", "full"))
    assert "-n" in spawns.commands[2]
    assert reporting_nextstep.success_line(FullLevel.COV) in capsys.readouterr().out


def test_parallel_speed_walk_judges_the_timing_pass(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An outlier in the timing pass exits 8 and restarts at --full=speed."""
    root = project(tmp_path, parallel=True)
    timings = (slow_transcript(None), 0)
    code, spawns = run(root, ["day", "--full=speed"], [CHECK_OK, AFFECTED_OK, FULL_GREEN, timings])
    assert code == EXIT_DURATION_OUTLIERS
    assert "--durations=0" in spawns.commands[3]
    out = capsys.readouterr().out
    assert "== ghog timings == started" in out
    assert reporting_nextstep.outliers_line(FullLevel.SPEED) in out
    assert "ghog day --full=speed" in reporting_nextstep.outliers_line(FullLevel.SPEED)


def test_direct_parallel_full_never_claims_speed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A green direct parallel ghog full proves cov and says speed was not measured."""
    code, _ = run(project(tmp_path, parallel=True), ["full"], [FULL_GREEN])
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert reporting_nextstep.MSG_SPEED_NOT_MEASURED in out
    assert reporting_nextstep.success_line(FullLevel.SPEED) not in out
    assert closing_line_of(out).endswith("full=speed src=default proof=cov scope=whole")


def test_direct_pass_failure_is_unproven_and_carries_the_level(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A failing direct pass run exits 2, unproven, focused at --full=pass."""
    code, _ = run(project(tmp_path), ["full", "--full=pass"], [TESTS_FAILING])
    assert code == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert "Next: ghog single tests/test_a.py tests/test_b.py --full=pass" in out
    assert closing_line_of(out).endswith("full=pass src=param proof=unproven scope=whole")


def test_green_single_restarts_the_walk_at_the_carried_level(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A green ghog single --full=cov prints Next: ghog day --full=cov."""
    root = project(tmp_path)
    baseline.write_baseline(root, ["tests/test_a.py::test_two"])
    focus = (passing_transcript(1, None), 0)
    code, _ = run(root, ["single", "tests/test_a.py", "--full=cov"], [focus])
    assert code == EXIT_OBJECTIVE_MET
    out = capsys.readouterr().out
    assert "Next: ghog day --full=cov" in out
    assert closing_line_of(out).endswith("exit=0 scope=whole")


def test_single_without_baseline_keeps_the_carried_level(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With no failure baseline, ghog single --full=cov names ghog full --full=cov."""
    focus = (passing_transcript(1, None), 0)
    code, _ = run(project(tmp_path), ["single", "tests/test_a.py", "--full=cov"], [focus])
    assert code == EXIT_OBJECTIVE_MET
    assert reporting_nextstep.no_baseline_line(FullLevel.COV) in capsys.readouterr().out
    assert "run ghog full --full=cov for suite-level truth" in reporting_nextstep.no_baseline_line(FullLevel.COV)


def test_environment_speed_restarts_a_failing_check_explicitly(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """GHOG_FULL=speed and a failing check restart with ghog day --full=speed."""
    code, _ = run(project(tmp_path), ["day"], [(["compile error"], 1)], {"GHOG_FULL": "speed"})
    assert code == 1
    assert reporting_nextstep.check_fail_line(FullLevel.SPEED) in capsys.readouterr().out


def test_failing_default_walk_restarts_plainly(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A default walk failing in affected restarts with plain ghog day, unproven."""
    code, _ = run(project(tmp_path), ["day"], [CHECK_OK, TESTS_FAILING])
    assert code == EXIT_TEST_FAILURES
    out = capsys.readouterr().out
    assert reporting_nextstep.affected_fail_line(FullLevel.NONE) in out
    assert "--full=" not in reporting_nextstep.affected_fail_line(FullLevel.NONE)
    assert closing_line_of(out).endswith("full=none src=default proof=unproven reused=none scope=whole")


def _cycle_lines() -> Sequence[str]:
    """Return the lines of the no-argument branch of ghog_cycle.bat."""
    text = _CYCLE.read_text(encoding="utf-8").splitlines()
    start = text.index('if "%~1"=="" (')
    end = text.index(")", start)
    return text[start:end]


def test_cycle_without_arguments_runs_day_alone() -> None:
    """The no-argument ghog_cycle.bat runs one ghog day walk and no timings."""
    branch = _cycle_lines()
    assert "    call :run_one day" in branch
    assert not any("timings" in line for line in branch)


# eof
