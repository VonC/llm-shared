"""A group too long for one command line reaches pytest through one argument file.

A group of many long test paths once failed to spawn on Windows
(``[WinError 206]``, exit 5). The child now receives one ``@<file>`` argument
in place of its selection tail; expanded the way pytest expands it, the
command equals the inline command of the same run, and the file is gone once
the child exits, passing or failing. A covered full run moves its coverage
folder options into the file too, before the test paths.

Fix: each test lowers the command-line budget instead of building sixty files
with long names to exceed the real one. Resolving that group dominated the
CPU of every lifecycle, which ran above the ceiling; three short files now
cross the lowered budget, a precondition checks that the inline command is
longer than it, and every assertion is unchanged.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tests.unit.tools.groundhog_acceptance_support import failing_transcript, make_deps
from tests.unit.tools.groundhog_group_support import CoverageSpawns, group_project
from tools.groundhog import args_file, cli
from tools.groundhog.models import EXIT_TEST_FAILURES

# A few group test paths and a budget the inline command exceeds.
_EXTRA_TESTS = 3
_BUDGET = 100
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


def _long_group(root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Add test files to the sentinel group and lower the budget below its command."""
    group_project(root)
    for index in range(_EXTRA_TESTS):
        (root / "tests" / "sentinel" / f"test_{index:03}.py").write_text("def test_ok():\n    pass\n", encoding="utf-8")
    monkeypatch.setattr(args_file, "COMMAND_LINE_BUDGET", _BUDGET)
    return root


@pytest.mark.parametrize("failing", [False, True])
def test_long_group_selection_reaches_pytest_through_one_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, failing: bool,
) -> None:
    """The expanded command equals the inline one, and the file never outlives the child."""
    root = _long_group(tmp_path, monkeypatch)
    expected = EXIT_TEST_FAILURES if failing else 0
    spilled = _ArgsFileSpawns(root, failing=failing)
    assert cli.main([*_AFFECTED, "--root", str(root)], make_deps(spilled)) == expected
    monkeypatch.setattr(args_file, "COMMAND_LINE_BUDGET", sys.maxsize)
    inline = _ArgsFileSpawns(root, failing=failing)
    assert cli.main([*_AFFECTED, "--root", str(root)], make_deps(inline)) == expected
    _assert_one_file_matches_inline(spilled, inline)


def _assert_one_file_matches_inline(spilled: _ArgsFileSpawns, inline: _ArgsFileSpawns) -> None:
    """Check that only the over-budget run used one file, which expands to the inline command."""
    assert len(subprocess.list2cmdline(inline.commands[0])) > _BUDGET
    assert inline.args_files == []
    assert len(spilled.args_files) == 1
    assert spilled.commands[0][-1] == f"{args_file.FILE_PREFIX}{spilled.args_files[0]}"
    assert spilled.expanded == inline.commands
    assert len(inline.commands[0]) > _EXTRA_TESTS
    assert not spilled.args_files[0].exists()


def test_covered_full_run_moves_coverage_folders_with_the_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The coverage folder options lead the file, ahead of the group test paths."""
    root = _long_group(tmp_path, monkeypatch)
    spawns = _ArgsFileSpawns(root)
    assert cli.main(["full", "--full=cov", "--group=sentinel", "--root", str(root)], make_deps(spawns)) == 0
    assert len(spawns.args_files) == 1
    assert len(subprocess.list2cmdline(spawns.expanded[0])) > _BUDGET
    assert "--cov=src/sentinel" not in spawns.commands[0]
    tail = spawns.expanded[0][len(spawns.commands[0]) - 1:]
    assert tail[:2] == ["--cov=src/sentinel", "--cov-fail-under=0"]
    assert len(tail) == 2 + _EXTRA_TESTS + 1
    assert all(path.startswith("tests/sentinel/test_") for path in tail[2:])
    assert not spawns.args_files[0].exists()


# eof
