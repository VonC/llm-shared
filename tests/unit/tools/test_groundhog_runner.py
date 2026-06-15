"""Unit tests for the groundhog child-process runner (Q17).

Cover the per-subcommand pytest command lines, the full run's
``--durations`` timing flags (Q39), the testmon reset of a full run, the
live streaming loop (with the real process factory), and the crash
classification of a pytest child (Q06).

Fix: the full command now also carries --durations=0 and
--durations-min=0 so the full run times every call; the affected and
single commands stay untimed.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

from tools.groundhog import runner
from tools.groundhog.models import PYTEST_INTERNAL_ERROR, PYTEST_INTERRUPTED

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

    from tools.groundhog.models import RunStats

_CHILD_EXIT = 3


class _FakeProcess:
    """A canned child process: scripted output lines and exit code."""

    def __init__(self, lines: list[str], returncode: int) -> None:
        """Script the child.

        Args:
            lines: The output lines, newline free.
            returncode: The exit code returned by wait().
        """
        self.stdout = iter([f"{line}\n" for line in lines])
        self._returncode = returncode

    def wait(self) -> int:
        """Return the scripted exit code.

        Returns:
            The scripted exit code.
        """
        return self._returncode


def _config(
    lines: list[str],
    returncode: int,
    cwd: Path,
) -> runner.StreamConfig:
    """Build a stream configuration around a canned child.

    Args:
        lines: The scripted output lines.
        returncode: The scripted exit code.
        cwd: The working directory of the run.

    Returns:
        The configuration with a fake process factory.
    """

    def _factory(command: list[str], directory: Path) -> subprocess.Popen[str]:
        del command, directory
        return cast("subprocess.Popen[str]", _FakeProcess(lines, returncode))

    return runner.StreamConfig(command=["pytest"], cwd=cwd, popen_factory=_factory)


def test_full_command_is_alias_faithful() -> None:
    """The full command keeps the ptr alias flags, -v and the timing flags.

    The full run alone times every call (Q39), so it carries
    --durations=0 and --durations-min=0 after the alias flags.
    """
    command = runner.pytest_command("pytest", runner.SUB_FULL, no_cov=False, files=())
    assert command == [
        "pytest",
        "--testmon",
        "--no-header",
        "--cov-report",
        "term-missing:skip-covered",
        "-v",
        "--durations=0",
        "--durations-min=0",
    ]


def test_only_the_full_command_times_durations() -> None:
    """The affected and single commands carry no --durations flags (Q39)."""
    affected = runner.pytest_command(
        "pytest",
        runner.SUB_AFFECTED,
        no_cov=False,
        files=(),
    )
    single = runner.pytest_command(
        "pytest",
        runner.SUB_SINGLE,
        no_cov=False,
        files=("tests/test_a.py",),
    )
    assert "--durations=0" not in affected
    assert "--durations-min=0" not in affected
    assert "--durations=0" not in single
    assert "--durations-min=0" not in single


def test_affected_command_appends_coverage() -> None:
    """The affected command carries --cov-append, the pta alias."""
    command = runner.pytest_command(
        "pytest",
        runner.SUB_AFFECTED,
        no_cov=False,
        files=(),
    )
    assert "--cov-append" in command
    assert "--testmon" in command


def test_affected_no_cov_command() -> None:
    """The ptanc variant disables coverage."""
    command = runner.pytest_command(
        "pytest",
        runner.SUB_AFFECTED,
        no_cov=True,
        files=(),
    )
    assert command == ["pytest", "--testmon", "--no-header", "--no-cov", "-v"]


def test_single_command_names_the_files() -> None:
    """The single command keeps the pts alias flags plus the files."""
    command = runner.pytest_command(
        "pytest",
        runner.SUB_SINGLE,
        no_cov=False,
        files=("tests/test_a.py",),
    )
    assert command == [
        "pytest",
        "--no-header",
        "--no-cov",
        "-rxX",
        "-v",
        "tests/test_a.py",
    ]


def test_reset_testmon_deletes_the_database(tmp_path: Path) -> None:
    """The full-run reset deletes .testmondata, twice without error."""
    database = tmp_path / runner.TESTMON_DATA_FILE
    database.write_text("stale", encoding="utf-8")
    runner.reset_testmon(tmp_path)
    assert not database.exists()
    runner.reset_testmon(tmp_path)


def test_run_streaming_with_the_real_factory(tmp_path: Path) -> None:
    """The default factory streams a real child and returns its code."""
    config = runner.StreamConfig(
        command=[
            sys.executable,
            "-c",
            "import sys; print('alpha'); print('beta'); sys.exit(3)",
        ],
        cwd=tmp_path,
        popen_factory=runner.default_popen_factory,
    )
    seen: list[str] = []
    code = runner.run_streaming(config, seen.append)
    assert seen == ["alpha", "beta"]
    assert code == _CHILD_EXIT


def test_run_pytest_parses_and_reports(tmp_path: Path) -> None:
    """A failing transcript yields parsed statistics, no crash."""
    lines = [
        "collected 2 items",
        "tests/test_a.py::test_one PASSED [ 50%]",
        "tests/test_a.py::test_two FAILED [100%]",
        "=================== FAILURES ===================",
        "E   AssertionError",
    ]
    updates: list[int] = []

    def _on_update(stats: RunStats) -> None:
        updates.append(stats.done)

    result = runner.run_pytest(_config(lines, 1, tmp_path), _on_update)
    assert result.stats.failed == 1
    assert result.pytest_exit == 1
    assert result.crashed is False
    assert result.failure_block[0].endswith("FAILURES ===================")
    assert updates[-1] == result.stats.done


def test_run_pytest_flags_internal_error_as_crash(tmp_path: Path) -> None:
    """An INTERNALERROR line flags the run as crashed (Q06)."""
    lines = ["INTERNALERROR> Traceback"]
    result = runner.run_pytest(_config(lines, 0, tmp_path), lambda _stats: None)
    assert result.crashed is True


def test_run_pytest_flags_crash_exit_codes(tmp_path: Path) -> None:
    """Interrupted, internal-error and signal exits read as crashes."""
    for code in (PYTEST_INTERRUPTED, PYTEST_INTERNAL_ERROR, -9):
        result = runner.run_pytest(_config([], code, tmp_path), lambda _stats: None)
        assert result.crashed is True


# eof
