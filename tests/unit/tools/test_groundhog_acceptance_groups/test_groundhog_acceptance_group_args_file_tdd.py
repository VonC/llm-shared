"""A group too long for one command line reaches pytest through one argument file.

A group of many long test paths once failed to spawn on Windows
(``[WinError 206]``, exit 5). The child now receives one ``@<file>`` argument
in place of its selection tail; expanded the way pytest expands it, the
command equals the inline command of the same run, and the file is gone once
the child exits, passing or failing. A covered full run moves its coverage
folder options into the file too, before the test paths.

Fix: writing 60 long test files and walking them twice cost the failing case
0.125 s of CPU, over the 0.1 s lifecycle limit. The tests now lower
``COMMAND_LINE_BUDGET`` to what three long paths exceed on their own, so the
smallest group that proves the spill is three files: the same split, file and
cleanup, every assertion kept.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_acceptance_support import failing_transcript, make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import args_file, cli
from tools.groundhog.models import EXIT_TEST_FAILURES

if TYPE_CHECKING:
    import subprocess

# Long group test paths whose selection alone exceeds the lowered budget.
_EXTRA_TESTS = 3
_NAME_PADDING = 120
_BUDGET = _EXTRA_TESTS * _NAME_PADDING
_AFFECTED = ["affected", "--no-cov", "--group=sentinel"]


class _ArgsFileSpawns(CoverageSpawns):
    """Expand the child's argument file at spawn time, as pytest would."""

    def __init__(self, root: Path, *, failing: bool = False) -> None:
        """Script a passing child, or a failing one."""
        super().__init__(root)
        if failing:
            self._lines, self._returncode = failing_transcript(), 1
        self.args_files: list[Path] = []
        self.expanded: list[list[str]] = []

    def __call__(self, command: list[str], cwd: Path) -> subprocess.Popen[str]:
        """Record the expanded command and the file it was read from."""
        head, last = command[:-1], command[-1]
        if last.startswith(args_file.FILE_PREFIX):
            path = Path(last.removeprefix(args_file.FILE_PREFIX))
            self.args_files.append(path)
            text = path.read_text(encoding=sys.getfilesystemencoding(), errors=sys.getfilesystemencodeerrors())
            self.expanded.append([*head, *text.splitlines()])
        else:
            self.expanded.append(command)
        return super().__call__(command, cwd)


def _long_group(root: Path) -> Path:
    """Add long test files to the sentinel group of the shared group project."""
    group_project(root)
    for index in range(_EXTRA_TESTS):
        name = f"test_{index:03}_{'x' * _NAME_PADDING}.py"
        (root / "tests" / "sentinel" / name).write_text("def test_ok():\n    pass\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("failing", [False, True])
def test_long_group_selection_reaches_pytest_through_one_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, failing: bool,
) -> None:
    """The expanded command equals the inline one, and the file never outlives the child."""
    root = _long_group(tmp_path)
    expected = EXIT_TEST_FAILURES if failing else 0
    monkeypatch.setattr(args_file, "COMMAND_LINE_BUDGET", _BUDGET)
    spilled = _ArgsFileSpawns(root, failing=failing)
    assert cli.main([*_AFFECTED, "--root", str(root)], make_deps(spilled)) == expected
    monkeypatch.setattr(args_file, "COMMAND_LINE_BUDGET", sys.maxsize)
    inline = _ArgsFileSpawns(root, failing=failing)
    assert cli.main([*_AFFECTED, "--root", str(root)], make_deps(inline)) == expected
    assert inline.args_files == []
    assert len(spilled.args_files) == 1
    assert spilled.commands[0][-1] == f"{args_file.FILE_PREFIX}{spilled.args_files[0]}"
    assert spilled.expanded == inline.commands
    assert len(inline.commands[0]) > _EXTRA_TESTS
    assert not spilled.args_files[0].exists()


def test_covered_full_run_moves_coverage_folders_with_the_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The coverage folder options lead the file, ahead of the group test paths."""
    root = _long_group(tmp_path)
    monkeypatch.setattr(args_file, "COMMAND_LINE_BUDGET", _BUDGET)
    spawns = _ArgsFileSpawns(root)
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(root)], make_deps(spawns)) == 0
    assert len(spawns.args_files) == 1
    assert "--cov=src/sentinel" not in spawns.commands[0]
    tail = spawns.expanded[0][len(spawns.commands[0]) - 1:]
    assert tail[:2] == ["--cov=src/sentinel", "--cov-fail-under=0"]
    assert len(tail) == 2 + _EXTRA_TESTS + 1
    assert all(path.startswith("tests/sentinel/test_") for path in tail[2:])
    assert not spawns.args_files[0].exists()


# eof
