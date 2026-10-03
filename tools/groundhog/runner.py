"""Child-process running for groundhog (Q17).

Step 3 adds the groups command name for read-only CLI dispatch; the runner
continues to execute the whole suite until group execution is introduced.

groundhog runs from the llm-shared venv and spawns pytest (or check.bat) as
a child process of the project environment prepared by senv.bat, reading
its output streams live. A hard crash of the suite kills only the child,
so the parent always survives to print the crash block (Q06) and to set
the exit code. The process factory is injectable, which is the single
faked element of the acceptance tests.

Fix: Run the full suite on xdist workers. Setup, not assertions, dominated
the walk, so the full run now spawns workers and drops ``--testmon``, which
cannot share a session with ``pytest-xdist``. The affected run keeps testmon
and owns the incremental map, so nothing resets that database any more.

Fix: :func:`is_pytest_project` tells whether the root carries a pytest suite at
all, so the pytest steps refuse a project with no pytest configuration before
looking for pytest on PATH.

Fix (v0.13.0 full_suite_levels, Step 2): :func:`pytest_command` shapes the full
run by its level. At ``pass`` it is today's full command with ``--no-cov`` and
no ``--durations``; at ``cov`` it keeps coverage and drops ``--durations``; at
``speed`` it is today's command. Runs below ``speed`` therefore never rewrite
the floor file, and the duration verdict, derived from the built command,
follows the level by construction. :func:`run_pytest` also flags a child
interrupted before it reported any failure, which judges no proof gate. An
interruption banner marks the run crashed whatever its return code, since
``pytest.exit`` may end an unfinished suite with 0 or 1.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.groundhog.levels import FullLevel
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

# Worker options of the full run. `loadgroup` schedules by the ``xdist_group``
# mark, so one parameter of an expensive module-scoped fixture can run on its
# own worker while its own tests stay together. `loadscope` could only keep a
# whole module on one worker, which left the longest parameterized module as
# the critical path. A module whose fixtures must not be rebuilt per worker
# carries a module-level mark; everything else is distributed test by test.
PARALLEL_OPTIONS: Final = ("-n", "auto", "--dist", "loadgroup")
# The testmon database a sequential full run resets, the reset of ptr (Q05).
TESTMON_DATA_FILE: Final = ".testmondata"
# Versioned opt-in marker at the consuming project root. groundhog is shared
# tooling: a project without pytest-xdist installed would fail outright on
# "-n", and a project whose module-scoped fixtures carry no xdist_group mark
# would rebuild them per worker. So the parallel full run is opt-in and every
# project keeps the sequential command until it declares otherwise.
PARALLEL_MARKER: Final = ".ghog-parallel"
# Root files that make a project a pytest project by their presence alone.
PYTEST_ROOT_FILES: Final = ("pyproject.toml", "pytest.ini", "conftest.py")
# Shared ini files that count only when they carry pytest's own section, since
# setup.cfg and tox.ini also serve projects that never run pytest.
PYTEST_INI_SECTIONS: Final = (("setup.cfg", "[tool:pytest]"), ("tox.ini", "[pytest]"))
# Subcommand names, shared with the CLI.
SUB_FULL: Final = "full"
SUB_AFFECTED: Final = "affected"
SUB_SINGLE: Final = "single"
SUB_TIMINGS: Final = "timings"
SUB_CHECK: Final = "check"
SUB_DAY: Final = "day"
SUB_INIT: Final = "init"
SUB_STATUS: Final = "status"
SUB_EXCLUDE: Final = "exclude"
SUB_GROUPS: Final = "groups"


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


def parallel_enabled(root: Path) -> bool:
    """Tell whether this project opted its full run into xdist workers.

    Args:
        root: The consuming project root.

    Returns:
        True when the project declares the parallel marker file.
    """
    return (root / PARALLEL_MARKER).is_file()


def is_pytest_project(root: Path) -> bool:
    """Tell whether the project root carries a pytest suite at all.

    Args:
        root: The consuming project root.

    Returns:
        True when the root holds a ``pyproject.toml``, ``pytest.ini`` or
        ``conftest.py``, or a ``setup.cfg`` or ``tox.ini`` with a pytest
        section.
    """
    if any((root / name).is_file() for name in PYTEST_ROOT_FILES):
        return True
    for name, section in PYTEST_INI_SECTIONS:
        path = root / name
        if path.is_file() and section in path.read_text(encoding="utf-8", errors="replace"):
            return True
    return False


def pytest_command(  # noqa: PLR0913
    pytest_exe: str,
    sub: str,
    *,
    no_cov: bool,
    files: Sequence[str],
    parallel: bool = False,
    level: FullLevel = FullLevel.SPEED,
) -> list[str]:
    """Build the pytest command of one groundhog subcommand.

    Args:
        pytest_exe: The pytest executable of the project environment.
        sub: The subcommand: ``full``, ``affected`` or ``single``.
        no_cov: Whether coverage is disabled (the ptanc variant).
        files: The test files of a ``single`` run.
        parallel: Whether this project opted its full run into xdist workers.
        level: The full-suite level shaping a ``full`` run: below ``cov`` it
            measures no coverage, below ``speed`` it times no call; every
            other subcommand ignores it.

    Returns:
        The pytest command line, alias-faithful plus ``-v`` for node ids;
        the full run at ``speed`` also times every call with ``--durations``
        (Q39).

    The full run is the only parallel one. It is the only subcommand wide
    enough for worker startup to pay for itself, and ``pytest-testmon`` cannot
    share a session with ``pytest-xdist`` -- together they abort the run with
    an ``INTERNALERROR``. So the full run drops ``--testmon`` and the affected
    run keeps it: the full run proves every test, the affected run owns the
    incremental selection map.
    """
    if sub == SUB_SINGLE:
        return [pytest_exe, "--no-header", "--no-cov", "-rxX", "-v", *files]
    if sub == SUB_TIMINGS:
        # Sequential and uninstrumented on purpose: a contended or covered
        # call time measures the scheduler, not the test (Q39).
        return [pytest_exe, "--no-header", "--no-cov", "-v",
                "--durations=0", "--durations-min=0"]
    worker_run = sub == SUB_FULL and parallel
    command = [pytest_exe, *(PARALLEL_OPTIONS if worker_run else ("--testmon",))]
    covered, timed = _measures(sub, level, no_cov=no_cov, worker_run=worker_run)
    if not covered:
        command.extend(["--no-header", "--no-cov", "-v"])
        return command
    if sub == SUB_AFFECTED:
        command.append("--cov-append")
    command.extend(
        ["--no-header", "--cov-report", "term-missing:skip-covered", "-v"],
    )
    if timed:
        command.extend(["--durations=0", "--durations-min=0"])
    return command


def _measures(sub: str, level: FullLevel, *, no_cov: bool, worker_run: bool) -> tuple[bool, bool]:
    """Tell what a covered or affected pytest run measures at its level.

    Args:
        sub: The subcommand: ``full`` or ``affected``.
        level: The full-suite level shaping a ``full`` run.
        no_cov: Whether coverage is disabled (the ptanc variant).
        worker_run: Whether the run spreads over xdist workers.

    Returns:
        Whether it measures coverage (never for a ``full`` run below
        ``cov``) and whether it times each call. A sequential full run still
        sees every test and still measures it honestly, so at ``speed`` it
        keeps the outlier rule exactly as before (Q39); below ``speed``
        nothing judges the timing, so nothing is timed.
    """
    full_run = sub == SUB_FULL
    covered = not no_cov and not (full_run and level < FullLevel.COV)
    timed = covered and full_run and not worker_run and level is FullLevel.SPEED
    return covered, timed


def reset_testmon(root: Path) -> None:
    """Delete the testmon database, the reset of a sequential full run (Q05).

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
        died mid-suite (Q06), and the interrupted flag when it was stopped
        before judging anything.
    """
    parser = PytestOutputParser()

    def _feed(line: str) -> None:
        parser.feed(line)
        on_update(parser.stats)

    code = run_streaming(config, _feed)
    # An interruption banner means the suite never finished, whatever return
    # code pytest.exit chose (0 and 1 included).
    crashed = (
        parser.internal_error
        or parser.interruption_banner
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
        interrupted=_interrupted(parser, code),
    )


def _interrupted(parser: PytestOutputParser, code: int) -> bool:
    """Tell whether a child was interrupted before it judged anything.

    A signal exit, or pytest's interruption banner (a ``KeyboardInterrupt``
    or a ``pytest.exit``, whatever its message or return code, 0 included; a
    collection error ends with exit 2 and another banner), counts only while
    no failure and no internal error were reported: a failure seen before the
    interruption is still evidence about the sources.

    Args:
        parser: The parser that read the child's output.
        code: The child exit code.

    Returns:
        True for an interruption that judged no gate.
    """
    stopped = code < 0 or parser.interruption_banner
    return stopped and not parser.internal_error and parser.stats.failed == 0


# eof
