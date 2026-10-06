"""Scope boundaries preserve explicit files, settings, evidence and recovery.

Fix (v0.13.0 full_suite_levels, Step 4): no affected tests preserve proof,
and whole-suite checks never scan the source inventory.
"""

from pathlib import Path

import pytest
from coverage import CoverageData

from tests.unit.tools.groundhog_acceptance_support import Spawns, make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import (
    cli,
    day,
    exclusions,
    floor,
    group_coverage,
    snapshot,
    status,
)
from tools.groundhog.context import Invocation
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_DURATION_OUTLIERS,
    EXIT_RUN_LOST,
    EXIT_SETUP_ERROR,
    EXIT_SUITE_CRASH,
    EXIT_TEST_FAILURES,
    Mode,
)


@pytest.mark.parametrize("sub", ["check", "single"])
def test_scope_does_not_replace_check_or_explicit_files(tmp_path: Path, sub: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Check remains project-wide and single retains the caller's files."""
    group_project(tmp_path)
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    files = ["tests/other/test_core.py"] if sub == "single" else []
    assert cli.main([sub, *files, "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert "tests/sentinel/test_core.py" not in spawns.commands[0]
    assert ("tests/other/test_core.py" in spawns.commands[0]) == (sub == "single")
    assert "scope=group:sentinel" in capsys.readouterr().out


@pytest.mark.parametrize(("seconds", "code"), [(1.5, 0), (0.1, 0), (5.0, EXIT_DURATION_OUTLIERS)])
def test_parallel_timing_keeps_group_and_readonly_exclusions(tmp_path: Path, seconds: float, code: int) -> None:
    """Timing uses group files and saved exclusions without ratcheting or deleting them."""
    group_project(tmp_path)
    (tmp_path / ".ghog-parallel").touch()
    floor.write_floor(tmp_path, 99, 1.0)
    exclusions.write_exclusions(tmp_path, {
        "tests/sentinel/test_core.py::test_ok": 2.0,
        "tests/other/test_core.py::test_ok": 5.0,
    })
    path = tmp_path / floor.floor_location(tmp_path)
    before = path.read_bytes()
    spawns = CoverageSpawns(tmp_path)
    spawns._lines.extend(["=== slowest durations ===", f"{seconds:.2f}s call tests/sentinel/test_core.py::test_ok"])
    assert cli.main(["day", "--full=speed", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == code
    assert "--durations=0" in spawns.commands[-1]
    assert spawns.commands[-1][-1] == "tests/sentinel/test_core.py"
    assert path.read_bytes() == before


@pytest.mark.parametrize(("sub", "expected"), [("full", EXIT_COVERAGE_GAP), ("affected", 0)])
def test_full_resets_while_affected_retains_data(tmp_path: Path, sub: str, expected: int) -> None:
    """The same old execution can complete an append but cannot prove a fresh full run."""
    group_project(tmp_path)
    source = tmp_path / "src/sentinel/core.py"
    source.write_text("first = 1\nsecond = 2\n", encoding="utf-8")
    data = CoverageData(basename=str(group_coverage.data_file(tmp_path, "sentinel")))
    data.add_lines({str(source): [2]})
    data.write()
    spawns = CoverageSpawns(tmp_path)
    assert cli.main([sub, "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == expected


@pytest.mark.parametrize("options", [
    ["--group"], ["--scope-file"], ["--whole-suite=no"], ["--group=sentinel", "--whole-suite"],
])
def test_invalid_cli_selectors_are_setup_errors(tmp_path: Path, options: list[str]) -> None:
    """Free scope flags cannot escape through argparse exit 2 or launch tests."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", "--root", str(tmp_path), *options], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert not spawns.commands


def test_unrelated_unknown_option_preserves_argparse_contract(tmp_path: Path) -> None:
    """Unknown non-scope options retain argparse's usage exit before any spawn."""
    spawns = CoverageSpawns(tmp_path)
    with pytest.raises(SystemExit) as error:
        cli.main(["day", "--root", str(tmp_path), "--unknown-option"], make_deps(spawns))
    usage_error = 2
    assert error.value.code == usage_error
    assert not spawns.commands


def test_unwritable_evidence_stops_before_spawn(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A data destination that cannot be reset is reported as setup failure."""
    group_project(tmp_path)
    group_coverage.data_file(tmp_path, "sentinel").mkdir()
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert not spawns.commands
    assert "run setup failed" in capsys.readouterr().out


def test_killed_group_status_restarts_same_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Recorded group scope survives status recovery without reading declarations."""
    (tmp_path / status.STATUS_FILE_NAME).write_text(
        "project: ghog day state=running full=cov scope=group:sentinel started=now\n", encoding="utf-8",
    )
    assert cli.main(["status", "--root", str(tmp_path)]) == EXIT_RUN_LOST
    assert "ghog day --full=cov --group=sentinel" in capsys.readouterr().out


@pytest.mark.parametrize(("lines", "child_code", "expected"), [
    (["tests/sentinel/test_core.py::test_ok FAILED", "=== 1 failed in 0.01s ==="], 1, EXIT_TEST_FAILURES),
    (["no tests ran in 0.01s"], 5, EXIT_SETUP_ERROR),
    (["INTERNALERROR> broken runner"], 3, EXIT_SUITE_CRASH),
])
def test_unsuccessful_group_run_keeps_test_verdict(
    tmp_path: Path, lines: list[str], child_code: int, expected: int, capsys: pytest.CaptureFixture[str],
) -> None:
    """Missing coverage cannot replace a failed, empty or crashed test verdict."""
    group_project(tmp_path)
    spawns = Spawns(lines, child_code)
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == expected
    assert "coverage evidence" not in capsys.readouterr().out


def test_group_without_durations_leaves_settings_untouched(tmp_path: Path) -> None:
    """A runner without duration rows cannot create or rewrite shared settings."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["full", "--full=speed", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert not (tmp_path / floor.floor_location(tmp_path)).exists()


def test_empty_covered_affected_keeps_group_proof(tmp_path: Path) -> None:
    """An unrelated child TOTAL cannot turn nothing-affected into a coverage gap."""
    group_project(tmp_path)
    passing = CoverageSpawns(tmp_path)
    assert cli.main(["day", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(passing)) == 0
    marker = snapshot.marker_path_for(tmp_path, "group:sentinel")
    before = marker.read_bytes()
    empty = Spawns(["TOTAL 2 1 50%", "no tests ran in 0.01s"], 5)
    assert cli.main(["affected", "--group=sentinel", "--root", str(tmp_path)], make_deps(empty)) == 0
    assert marker.read_bytes() == before


@pytest.mark.parametrize("selector", [[], ["--whole-suite"]])
def test_whole_check_does_not_scan_sources(
    tmp_path: Path, selector: list[str], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A whole-suite check needs no declaration resolution or proof inventory."""
    def unexpected_scan(_root: Path) -> list[Path]:
        pytest.fail("whole-suite check must not scan the source tree")

    monkeypatch.setattr(snapshot, "source_files", unexpected_scan)
    assert cli.main(["check", *selector, "--root", str(tmp_path)], make_deps(Spawns([], 0))) == 0


def test_direct_walk_builds_inventory_for_proof(tmp_path: Path) -> None:
    """Callers outside the CLI still get a reusable proof from their source tree."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    invocation = Invocation(sub="day", files=(), no_cov=False, mode=Mode.LLM, root=tmp_path)
    assert day.walk(invocation, make_deps(spawns)).code == 0
    marker = snapshot.read_proof_marker(snapshot.marker_path(tmp_path))
    assert marker is not None
    assert marker.proof is FullLevel.NONE
    count = len(spawns.commands)
    assert day.walk(invocation, make_deps(spawns)).code == 0
    assert len(spawns.commands) == count
