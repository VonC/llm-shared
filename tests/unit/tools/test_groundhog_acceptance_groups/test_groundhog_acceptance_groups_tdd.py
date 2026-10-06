"""Exercise grouped walks and proof reuse through the real CLI."""

from pathlib import Path

import pytest

from tests.unit.tools.groundhog_acceptance_support import (
    Spawns,
    closing_line_of,
    failing_transcript,
    make_deps,
)
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import cli, exclusions, floor
from tools.groundhog.models import (
    EXIT_DURATION_OUTLIERS,
    EXIT_SETUP_ERROR,
    EXIT_TEST_FAILURES,
)


def test_walk_narrows_collection_and_names_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Both test steps collect only the selected group's tests and carry its proof."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    expected_spawns = 2
    assert len(spawns.commands) == expected_spawns
    _assert_group_commands(spawns.commands)
    output = capsys.readouterr().out
    assert "for group sentinel" in output
    assert "scope=group:sentinel" in closing_line_of(output)
    assert "proof=cov" in closing_line_of(output)


def _assert_group_commands(commands: list[list[str]]) -> None:
    """Check collection and coverage selection at the spawn boundary."""
    for command in commands:
        assert command[-1] == "tests/sentinel/test_core.py"
        assert "tests/other/test_core.py" not in command
    assert "--cov=src/sentinel" in commands[-1]
    assert "--cov-fail-under=0" in commands[-1]


def test_proof_isolated_by_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Whole and different group proofs never satisfy another group's walk."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    for selector in ("--whole-suite", "--group=sentinel", "--group=other"):
        before = len(spawns.commands)
        assert cli.main(["day", "--full=cov", selector, "--root", str(tmp_path)], make_deps(spawns)) == 0
        assert len(spawns.commands) == before + 2
    before = len(spawns.commands)
    assert cli.main(["day", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert len(spawns.commands) == before
    assert "for group sentinel is met by saved proof" in capsys.readouterr().out


@pytest.mark.parametrize("problem", ["unknown", "unreadable", "test", "source", "malformed"])
def test_bad_group_stops_before_spawn(tmp_path: Path, problem: str, capsys: pytest.CaptureFixture[str]) -> None:
    """An unusable explicit group is a setup error, never a whole-suite fallback."""
    group_project(tmp_path)
    name = _damage_group(tmp_path, problem)
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", f"--group={name}", "--root", str(tmp_path)], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert spawns.commands == []
    output = capsys.readouterr().out
    assert name in output or "unreadable" in output
    if problem in ("test", "source"):
        assert f"empty {problem} side" in output


def _damage_group(root: Path, problem: str) -> str:
    """Set up each distinct invalid declaration or membership boundary."""
    removed = {
        "unreadable": ".ghog-groups",
        "test": "tests/sentinel/test_core.py",
        "source": "src/sentinel/core.py",
    }
    if problem in removed:
        (root / removed[problem]).unlink()
    return {"unknown": "nope", "malformed": "../bad"}.get(problem, "sentinel")


def test_whole_ignores_invalid_environment_and_declaration(tmp_path: Path) -> None:
    """An explicit whole walk overrides ambient selection without opening declarations."""
    group_project(tmp_path)
    (tmp_path / ".ghog-groups").unlink()
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", "--full=cov", "--whole-suite", "--root", str(tmp_path)],
                    make_deps(spawns, {"GHOG_GROUP": "nope"})) == 0


@pytest.mark.parametrize("selector", ["--group=sentinel", "--whole-suite"])
def test_failure_repair_carries_explicit_scope(tmp_path: Path, selector: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Repair and restart retain the chosen level and scope despite ambient values."""
    group_project(tmp_path)
    spawns = Spawns(failing_transcript(), 1)
    assert cli.main(["day", "--full=cov", selector, "--root", str(tmp_path)],
                    make_deps(spawns, {"GHOG_GROUP": "other"})) == EXIT_TEST_FAILURES
    output = capsys.readouterr().out
    assert f"ghog affected --no-cov --full=cov {selector}" in output
    assert f"ghog day --full=cov {selector}" in output


@pytest.mark.parametrize("change", ["membership", "pattern"])
def test_group_edits_invalidate_proof(tmp_path: Path, change: str) -> None:
    """Membership and pattern identity both participate in proof reuse."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    arguments = ["day", "--full=pass", "--group=sentinel", "--root", str(tmp_path)]
    assert cli.main(arguments, make_deps(spawns)) == 0
    if change == "membership":
        (tmp_path / "tests/sentinel/test_more.py").write_text("def test_more(): pass\n", encoding="utf-8")
    else:
        path = tmp_path / ".ghog-groups"
        path.write_text(path.read_text(encoding="utf-8").replace("tests/sentinel/**", "tests/sentinel/*.py"), encoding="utf-8")
    assert cli.main(arguments, make_deps(spawns)) == 0
    expected_spawns = 4
    assert len(spawns.commands) == expected_spawns


@pytest.mark.parametrize(("sub", "extra", "code", "proof"), [
    ("day", [], 0, "none"), ("full", ["--full=pass"], 5, "unproven"),
])
def test_nothing_affected_is_green_but_empty_full_is_error(  # noqa: PLR0913
    tmp_path: Path, sub: str, extra: list[str], code: int, proof: str, capsys: pytest.CaptureFixture[str],
) -> None:
    """Empty incremental selection proves only the default walk; full must collect."""
    group_project(tmp_path)
    spawns = Spawns(["collected 0 items", "====== no tests ran in 0.01s ======"], 5)
    assert cli.main([sub, *extra, "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == code
    assert f"proof={proof}" in closing_line_of(capsys.readouterr().out)


def test_grouped_speed_reads_floor_and_preserves_exclusions(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A small group uses the floor alone and never manages shared exclusions."""
    group_project(tmp_path)
    floor.write_floor(tmp_path, 99, 1.0)
    exclusions.write_exclusions(tmp_path, {"tests/other/test_core.py::test_ok": 5.0})
    path = tmp_path / floor.floor_location(tmp_path)
    before = path.read_bytes()
    spawns = CoverageSpawns(tmp_path)
    spawns._lines.extend(["=== slowest durations ===", "1.50s call tests/sentinel/test_core.py::test_ok"])
    assert cli.main(["day", "--full=speed", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == EXIT_DURATION_OUTLIERS
    assert path.read_bytes() == before
    assert "tests/other/test_core.py::test_ok" not in capsys.readouterr().out


def test_changed_exclusions_cap_group_speed_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A timing fingerprint edit reuses check and affected but re-establishes speed."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    spawns._lines.extend(["=== slowest durations ===", "0.10s call tests/sentinel/test_core.py::test_ok"])
    arguments = ["day", "--full=speed", "--group=sentinel", "--root", str(tmp_path)]
    assert cli.main(arguments, make_deps(spawns)) == 0
    exclusions.write_exclusions(tmp_path, {"tests/other/test_core.py::test_ok": 5.0})
    assert cli.main(arguments, make_deps(spawns)) == 0
    expected_spawns = 3
    assert len(spawns.commands) == expected_spawns
    assert "reused=check+affected" in capsys.readouterr().out
