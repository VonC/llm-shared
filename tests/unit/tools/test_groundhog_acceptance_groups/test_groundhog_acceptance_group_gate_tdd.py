"""Group gates measure exact sources, branch gaps and unusable evidence."""

from pathlib import Path

import pytest

from tests.unit.tools.groundhog_acceptance_support import make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import cli, snapshot
from tools.groundhog.models import EXIT_COVERAGE_GAP, EXIT_SETUP_ERROR


def test_unexecuted_source_fails_hundred_percent_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The group's missing source defeats both the project gate and a green TOTAL."""
    group_project(tmp_path)
    (tmp_path / "src/sentinel/unexecuted.py").write_text("value = 2\n", encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == EXIT_COVERAGE_GAP
    output = capsys.readouterr().out
    assert "unexecuted.py" in output
    assert "0%" in output
    assert "cov=50" in output


def test_external_source_and_omit(tmp_path: Path) -> None:
    """Extra cov folders measure sources outside project source while preserving omit."""
    group_project(tmp_path)
    (tmp_path / "lib").mkdir()
    (tmp_path / "lib/widget.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "lib/omit.py").write_text("value = 2\n", encoding="utf-8")
    (tmp_path / ".ghog-groups").write_text("[sentinel]\ntests = tests/sentinel/**\nsources = lib/**\n", encoding="utf-8")
    config = tmp_path / "pyproject.toml"
    config.write_text('[tool.coverage.run]\nsource = ["src"]\nomit = ["lib/omit.py"]\n', encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    spawns.lines = {str(tmp_path / "lib/widget.py"): [1]}
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert "--cov=lib" in spawns.commands[-1]


@pytest.mark.parametrize("problem", ["invalid", "missing", "stale"])
def test_bad_data_preserves_saved_proof(tmp_path: Path, problem: str, capsys: pytest.CaptureFixture[str]) -> None:
    """An evidence failure is setup exit 5 and cannot erase an earlier valid proof."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    arguments = ["day", "--full=cov", "--group=sentinel", "--root", str(tmp_path)]
    assert cli.main(arguments, make_deps(spawns)) == 0
    marker = snapshot.marker_path_for(tmp_path, "group:sentinel")
    before = marker.read_bytes()
    spawns.data = problem
    assert cli.main([*arguments, "--force"], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert marker.read_bytes() == before
    assert "coverage evidence" in capsys.readouterr().out


def test_missed_branch_fails_group_gate(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A branch-enabled project includes branch opportunities in its group gate."""
    group_project(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.coverage.run]\nbranch = true\n", encoding="utf-8")
    source = tmp_path / "src/sentinel/core.py"
    source.write_text("if flag:\n    value = 1\nvalue = 2\n", encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    spawns.arcs = {str(source): [(-1, 1), (1, 2), (2, 3), (3, -1)]}
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == EXIT_COVERAGE_GAP
    assert "1->3" in capsys.readouterr().out


def test_covered_affected_appends_without_proof(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Covered incremental checks share only the group's data and save no proof."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["affected", "--group=sentinel", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert "--cov-append" in spawns.commands[-1]
    assert "scope=group:sentinel" in capsys.readouterr().out
    assert not snapshot.marker_path_for(tmp_path, "group:sentinel").exists()
