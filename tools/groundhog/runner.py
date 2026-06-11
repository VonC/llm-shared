"""Child-process running for groundhog (Q17).

groundhog runs from the llm-shared venv and spawns pytest (or check.bat) as
a child process of the project environment prepared by senv.bat, reading
its output streams live. A hard crash of the suite kills only the child,
so the parent always survives to print the crash block (Q06) and to set
the exit code. The process factory is injectable, which is the single
faked element of the acceptance tests.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.groundhog.models import (
    PYTEST_INTERNAL_ERROR,
    PYTEST_INTERRUPTED,
    RunResult,
)
from tools.groundhog.parser import PytestOutputParser

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from pathlib import Path

    from tools.groundhog.models import RunStats

# The testmon database deleted by a full run, the reset of ptr.
TESTMON_DATA_FILE: Final = ".testmondata"
# Subcommand names, shared with the CLI.
SUB_FULL: Final = "full"
SUB_AFFECTED: Final = "affected"
SUB_SINGLE: Final = "single"
SUB_CHECK: Final = "check"
SUB_DAY: Final = "day"
SUB_INIT: Final = "init"


@dataclass(frozen=True)
class StreamConfig:
    """One streaming child run.

    Attributes:
        command: The child command line.
        cwd: The working directory, the consuming project root.
        popen_factory: The process factory, injectable for tests.
    """

    command: list[str]
    cwd: Path
    popen_factory: Callable[[list[str], Path], subprocess.Popen[str]]


def default_popen_factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
    """Spawn a streaming child process, stderr folded into stdout.

    Args:
        command: The child command line.
        cwd: The working directory of the child.

    Returns:
        The started process, with a text stdout stream.
    """
    return subprocess.Popen(  # noqa: S603
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )


def pytest_command(
    pytest_exe: str,
    sub: str,
    *,
    no_cov: bool,
    files: Sequence[str],
) -> list[str]:
    """Build the pytest command of one groundhog subcommand.

    Args:
        pytest_exe: The pytest executable of the project environment.
        sub: The subcommand: ``full``, ``affected`` or ``single``.
        no_cov: Whether coverage is disabled (the ptanc variant).
        files: The test files of a ``single`` run.

    Returns:
        The pytest command line, alias-faithful plus ``-v`` for node ids.
    """
    if sub == SUB_SINGLE:
        return [pytest_exe, "--no-header", "--no-cov", "-rxX", "-v", *files]
    if no_cov:
        return [pytest_exe, "--testmon", "--no-header", "--no-cov", "-v"]
    command = [pytest_exe, "--testmon"]
    if sub == SUB_AFFECTED:
        command.append("--cov-append")
    command.extend(
        ["--no-header", "--cov-report", "term-missing:skip-covered", "-v"],
    )
    return command


def reset_testmon(root: Path) -> None:
    """Delete the testmon database, the reset of a full run (Q05).

    Args:
        root: The project root directory.
    """
    (root / TESTMON_DATA_FILE).unlink(missing_ok=True)


def run_streaming(config: StreamConfig, on_line: Callable[[str], None]) -> int:
    """Run one child and hand each output line to a callback.

    Args:
        config: The command, working directory and process factory.
        on_line: Called with each output line, newline stripped.

    Returns:
        The child exit code.
    """
    process = config.popen_factory(config.command, config.cwd)
    for raw in process.stdout or []:
        on_line(raw.rstrip("\n"))
    return process.wait()


def run_pytest(
    config: StreamConfig,
    on_update: Callable[[RunStats], None],
) -> RunResult:
    """Run one pytest child and parse its output live (Q17).

    Args:
        config: The command, working directory and process factory.
        on_update: Called with the running statistics after each line.

    Returns:
        The parsed run result, with the crash flag set when the child
        died mid-suite (Q06).
    """
    parser = PytestOutputParser()

    def _feed(line: str) -> None:
        parser.feed(line)
        on_update(parser.stats)

    code = run_streaming(config, _feed)
    crashed = (
        parser.internal_error
        or code < 0
        or code in (PYTEST_INTERRUPTED, PYTEST_INTERNAL_ERROR)
    )
    return RunResult(
        stats=parser.stats,
        pytest_exit=code,
        crashed=crashed,
        failure_block=parser.failure_block,
        tail=parser.tail,
        coverage_block=parser.coverage_block,
    )


# eof
