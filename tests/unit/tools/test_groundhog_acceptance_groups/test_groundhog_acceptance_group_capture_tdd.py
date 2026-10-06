"""Captured scope stays bound through detached execution and declaration edits."""

from dataclasses import replace
from pathlib import Path

import pytest

from tests.unit.tools.groundhog_acceptance_support import make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import cli, groups, scope, snapshot
from tools.groundhog.models import EXIT_RUN_LIVE, EXIT_SETUP_ERROR


def test_capture_survives_changed_declaration(tmp_path: Path) -> None:
    """A same-name edit cannot widen a launcher's bound test membership."""
    group_project(tmp_path)
    selected = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    capture = scope.write_detach_capture(tmp_path, selected)
    (tmp_path / ".ghog-groups").write_text("[sentinel]\ntests = tests/other/**\nsources = src/other/**\n", encoding="utf-8")
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", "--full=cov", f"--scope-file={capture}", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert all(command[-1] == "tests/sentinel/test_core.py" for command in spawns.commands)


@pytest.mark.parametrize("damage", ["deleted", "edited", "conflict"])
def test_unusable_bound_scope_stops(tmp_path: Path, damage: str, capsys: pytest.CaptureFixture[str]) -> None:
    """No bound-scope failure can degrade to ambient group resolution."""
    group_project(tmp_path)
    selected = groups.resolve_group(tmp_path, "sentinel", snapshot.source_files(tmp_path))
    capture = scope.write_detach_capture(tmp_path, selected)
    extra = []
    if damage == "deleted":
        (tmp_path / selected.test_files[0]).unlink()
    elif damage == "edited":
        capture.write_text(capture.read_text(encoding="utf-8").replace("sentinel", "other"), encoding="utf-8")
    else:
        extra = ["--group=sentinel"]
    spawns = CoverageSpawns(tmp_path)
    assert cli.main(["day", f"--scope-file={capture}", *extra, "--root", str(tmp_path)], make_deps(spawns)) == EXIT_SETUP_ERROR
    assert not spawns.commands
    output = capsys.readouterr().out
    assert ("--group" if damage == "conflict" else "bound scope unusable:") in output


@pytest.mark.parametrize("selector", ["--group=sentinel", "--whole-suite"])
def test_detach_writes_capture_before_child_and_status_keeps_scope(
    tmp_path: Path, selector: str, capsys: pytest.CaptureFixture[str],
) -> None:
    """The detach boundary receives an explicit whole selector or an already-written capture."""
    group_project(tmp_path)
    spawns = CoverageSpawns(tmp_path)
    spawned: list[list[str]] = []

    def child(command: list[str], _log: Path, _preamble: str, _cwd: Path) -> int:
        spawned.append(command)
        if selector == "--group=sentinel":
            capture_arg = next(arg for arg in command if arg.startswith("--scope-file="))
            assert Path(capture_arg.split("=", 1)[1]).is_file()
            (tmp_path / ".ghog-groups").unlink()
        else:
            assert "--whole-suite" in command
        assert cli.main(command[2:], make_deps(spawns)) == 0
        return 123

    def no_sleep(_seconds: float) -> None:
        pass

    deps = replace(make_deps(spawns), detach_factory=child, sleep=no_sleep)
    assert cli.main(["day", "--detach", "--full=cov", selector, "--root", str(tmp_path)], deps) == EXIT_RUN_LIVE
    assert len(spawned) == 1
    assert cli.main(["status", "--root", str(tmp_path)], make_deps(spawns)) == 0
    assert ("scope=group:sentinel" if "group" in selector else "scope=whole") in capsys.readouterr().out
