"""Spill a long pytest selection into an argument file, never changing it.

A command within ``COMMAND_LINE_BUDGET`` spawns unchanged and writes no file.
A longer one keeps its options inline and passes its selection tail, from the
first selection argument on, through one ``@<file>`` argument whose lines read
back as exactly that tail, in order: paths with spaces and non-ASCII names
included. The file is gone once the block exits, normally or by an exception.
A tail that lines cannot hold, or a long command without selection, spawns
unchanged.
"""

import os
import sys
from pathlib import Path

import pytest

from tools.groundhog import args_file

# Long relative test paths with a space and a non-ASCII letter, enough of them
# that the command exceeds the budget.
_PATHS = tuple(f"tests/my group/test_ü_{index:03}_{'x' * 100}.py" for index in range(70))
_COV = "--cov=src/my group"
_HEAD = ["pytest", "--testmon", "--no-header", "-v"]
_LONG = [*_HEAD, _COV, "--cov-fail-under=0", *_PATHS]
_SELECTION = frozenset({_COV, *_PATHS})


def _args_path(root: Path) -> Path:
    """Return the argument file the current groundhog process would write."""
    return root / ".reviews" / args_file.FILE_NAME.format(pid=os.getpid())


def _read(path: Path) -> list[str]:
    """Read an argument file the way pytest's argparse reads it."""
    text = path.read_text(encoding=sys.getfilesystemencoding(), errors=sys.getfilesystemencodeerrors())
    return text.splitlines()


def test_selection_arguments_spell_coverage_folders_as_the_command() -> None:
    """Test paths, single files and one coverage option per folder are the selection."""
    chosen = args_file.selection_arguments(("tests/t.py",), ("tests/s.py",), ("src", "lib/a b"))
    assert chosen == {"tests/t.py", "tests/s.py", "--cov=src", "--cov=lib/a b"}


@pytest.mark.parametrize(("command", "expected"), [
    (["pytest", "-v", "tests/t.py"], 3),
    ([*_HEAD, "--durations=0", *(f"--opt{'y' * 200}" for _ in range(50))], 55),
    (_LONG, len(_HEAD)),
    ([*_LONG[:-1], "tests/broken\nname.py"], len(_LONG)),
])
def test_spill_start_moves_only_a_long_line_safe_selection(command: list[str], expected: int) -> None:
    """Short commands, commands without selection and line-breaking tails stay inline."""
    assert args_file.spill_start(command, {*_SELECTION, "tests/t.py", "tests/broken\nname.py"}) == expected


@pytest.mark.parametrize(("extra", "expected"), [(0, 2), (1, 1)])
def test_budget_is_the_rendered_length(extra: int, expected: int) -> None:
    """A command rendered at exactly the budget stays inline; one more character spills."""
    path = "a" * (args_file.COMMAND_LINE_BUDGET - len("pytest ") + extra)
    assert args_file.spill_start(["pytest", path], {path}) == expected


def test_short_command_spawns_unchanged_without_a_file(tmp_path: Path) -> None:
    """Within the budget the command object is yielded as is and no home is prepared."""
    command = ["pytest", "-v", "tests/t.py"]
    with args_file.spilled(command, {"tests/t.py"}, tmp_path) as spawned:
        assert spawned is command
    assert not (tmp_path / ".reviews").exists()


def test_long_selection_reads_back_in_order_and_is_removed(tmp_path: Path) -> None:
    """The head stays inline and one file holds the exact tail, one argument per line."""
    with args_file.spilled(_LONG, _SELECTION, tmp_path) as spawned:
        path = _args_path(tmp_path)
        assert spawned == [*_HEAD, f"{args_file.FILE_PREFIX}{path}"]
        assert [*_HEAD, *_read(path)] == _LONG
    assert not path.exists()


def _spawn_failing(root: Path) -> None:
    """Fail while the spilled child runs, after checking its file exists."""
    with args_file.spilled(_LONG, _SELECTION, root):
        assert _args_path(root).is_file()
        message = "child failed"
        raise RuntimeError(message)


def test_failing_block_still_removes_the_file(tmp_path: Path) -> None:
    """An exception raised while the child runs still removes the argument file."""
    with pytest.raises(RuntimeError, match="child failed"):
        _spawn_failing(tmp_path)
    assert not _args_path(tmp_path).exists()


# eof
