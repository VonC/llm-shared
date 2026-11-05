"""Pass a long pytest selection to the child through an argument file.

A grouped run appends every group test file, and one ``--cov=<folder>`` per
group source folder, to the pytest command line. A group of a few hundred test
files outgrew the 32767 characters of a Windows ``CreateProcess`` command line:
the spawn failed with ``[WinError 206] Filename or extension too long`` before
pytest started, and ``affected``, ``full`` and ``single`` alike exited 5.

Fix: :func:`spilled` measures the rendered command at the spawn boundary. Above
``COMMAND_LINE_BUDGET`` characters, it writes the selection tail, from the
first selection argument to the end of the command, into one file of the
project's artifact home, and passes ``@<file>`` in its place. A command within
the budget spawns unchanged, so an ordinary run keeps the command line it had.
The budget stays below the 8191 characters of a ``cmd.exe`` line, the limit
when the pytest found on ``PATH`` is a batch shim, and far below the
``CreateProcess`` limit.

pytest 8.2 and later expand ``@<file>`` in place through argparse
``fromfile_prefix_chars``: each line is one argument, never quoted and never
split on whitespace, read in the filesystem encoding. A path with spaces or a
non-ASCII name survives, and the tests, the coverage folders and their order
stay the same. The options before the selection stay on the command line, as
pytest scans some of them (``-p``) before it expands the file. A tail that
lines cannot hold one argument each (an argument carrying a line break) keeps
the command unchanged.

The file name carries the groundhog process id, so two groundhog processes of
one checkout never share a file. It is removed once the child has exited,
whether the run passed, failed or raised.
"""

from __future__ import annotations

import os
import subprocess
import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING, Final

from tools.artifact_home import artifact_path

if TYPE_CHECKING:
    from collections.abc import Collection, Generator, Sequence
    from pathlib import Path

# The longest rendered child command spawned as is: below the 8191 characters
# of a cmd.exe line (a batch pytest shim) and the 32767 of CreateProcess.
COMMAND_LINE_BUDGET: Final = 8000
# The argparse prefix pytest reads an argument file from (pytest 8.2+).
FILE_PREFIX: Final = "@"
# The argument file in the artifact home, one per groundhog process.
FILE_NAME: Final = "a.ghog.pytest-args.{pid}.txt"


def selection_arguments(
    test_paths: Sequence[str], files: Sequence[str], cov_folders: Sequence[str],
) -> frozenset[str]:
    """Collect the selection arguments a pytest command may carry.

    Args:
        test_paths: The bound group test files.
        files: The test files of a ``single`` run.
        cov_folders: The minimal containing folders of the group sources.

    Returns:
        The test paths, the single-run files and one ``--cov=<folder>`` option
        per folder, spelled as ``runner.pytest_command`` spells it.
    """
    return frozenset((*test_paths, *files, *(f"--cov={folder}" for folder in cov_folders)))


def file_text(arguments: Sequence[str]) -> str:
    """Render arguments as argument-file lines.

    Args:
        arguments: The arguments, in command order.

    Returns:
        One line per argument, each ended by a newline.
    """
    return "".join(f"{argument}\n" for argument in arguments)


def spill_start(command: Sequence[str], selection: Collection[str]) -> int:
    """Return where the argument-file tail of a child command starts.

    Args:
        command: The full child command line, the executable first.
        selection: The selection arguments of the run.

    Returns:
        The index of the first selection argument after the executable when
        the rendered command exceeds ``COMMAND_LINE_BUDGET`` and its tail reads
        back from lines unchanged; ``len(command)``, an empty tail, otherwise.
    """
    if len(subprocess.list2cmdline(command)) <= COMMAND_LINE_BUDGET:
        return len(command)
    start = next((index for index in range(1, len(command)) if command[index] in selection), len(command))
    tail = list(command[start:])
    return start if file_text(tail).splitlines() == tail else len(command)


@contextmanager
def spilled(command: list[str], selection: Collection[str], root: Path) -> Generator[list[str]]:
    """Yield the command to spawn, its selection tail in a file while too long.

    Args:
        command: The full child command line, the executable first.
        selection: The selection arguments of the run.
        root: The project root, whose artifact home holds the file; resolved
            only when the command spills.

    Yields:
        The command unchanged when it fits the budget; otherwise its head plus
        one ``@<file>`` argument, the file holding the tail one argument per
        line. The file is removed when the block exits, normally or not.
    """
    start = spill_start(command, selection)
    if start == len(command):
        yield command
        return
    path = artifact_path(root, FILE_NAME.format(pid=os.getpid()))
    try:
        path.write_text(
            file_text(command[start:]),
            encoding=sys.getfilesystemencoding(),
            errors=sys.getfilesystemencodeerrors(),
            newline="\n",
        )
        yield [*command[:start], f"{FILE_PREFIX}{path}"]
    finally:
        path.unlink(missing_ok=True)


# eof
