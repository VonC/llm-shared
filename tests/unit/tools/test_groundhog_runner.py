"""Unit tests for the groundhog child-process runner (Q17).

Cover the per-subcommand pytest command lines, the full run's
``--durations`` timing flags (Q39), the live streaming loop (with the real
process factory), and the crash classification of a pytest child (Q06).

Fix: the full command now also carries --durations=0 and
--durations-min=0 so the full run times every call; the affected and
single commands stay untimed.

Fix: the full command carries the xdist worker options instead of
``--testmon``, which cannot share a session with ``pytest-xdist``. The
affected run keeps testmon and owns the incremental map, so no test covers a
testmon reset any more.

Fix: cover the pytest-suite probe of the project root: a bare root has no
suite, each root marker file makes one, and setup.cfg or tox.ini count only
with pytest's own section.

The real streaming child skips site initialization and inherited Python setup;
the scenario needs only builtin output and exit status.

Fix (v0.13.0 full_suite_levels, Step 2): cover the full-run shape per level,
sequential and parallel: ``pass`` carries ``--no-cov`` and no ``--durations``,
``cov`` keeps coverage without ``--durations``, ``speed`` is today's command;
the level never shapes another subcommand. Cover the interrupted flag too: a
signal, or pytest's interruption banner (a bare or messaged
KeyboardInterrupt, a pytest.exit with any return code), before any failure or
internal error, never a collection error.

Step 4: verify group paths, coverage options and environment restoration on successful and raising spawns.
"""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, cast

import pytest

from tools.groundhog import runner
from tools.groundhog.levels import FullLevel
from tools.groundhog.models import (
    PYTEST_INTERNAL_ERROR,
    PYTEST_INTERRUPTED,
    PYTEST_OK,
    PYTEST_TEST_FAILURES,
)

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
    """A project that did not opt in keeps the sequential ptr command (Q39).

    groundhog is shared tooling, so the default must stay exactly what every
    consuming project already runs: testmon, coverage and the timing flags that
    feed the outlier rule.
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


def test_opted_in_full_command_runs_on_workers_without_timing_or_testmon() -> None:
    """The opted-in full run swaps testmon and timing flags for workers.

    testmon cannot share a session with xdist, and a contended call time
    measures the scheduler rather than the test, so the sequential timings run
    owns the outlier rule for such a project.
    """
    command = runner.pytest_command(
        "pytest", runner.SUB_FULL, no_cov=False, files=(), parallel=True,
    )
    assert command == [
        "pytest",
        "-n",
        "auto",
        "--dist",
        "loadgroup",
        "--no-header",
        "--cov-report",
        "term-missing:skip-covered",
        "-v",
    ]
    assert "--testmon" not in command
    assert "--durations=0" not in command


def test_full_command_shape_per_level() -> None:
    """Pass drops coverage and timing, cov drops timing, speed keeps both."""
    for parallel in (False, True):
        passing = runner.pytest_command(
            "pytest", runner.SUB_FULL, no_cov=False, files=(), parallel=parallel, level=FullLevel.PASS,
        )
        assert "--no-cov" in passing
        assert "--durations=0" not in passing
        covered = runner.pytest_command(
            "pytest", runner.SUB_FULL, no_cov=False, files=(), parallel=parallel, level=FullLevel.COV,
        )
        assert "--cov-report" in covered
        assert "--durations=0" not in covered
    speed = runner.pytest_command("pytest", runner.SUB_FULL, no_cov=False, files=(), level=FullLevel.SPEED)
    assert speed == runner.pytest_command("pytest", runner.SUB_FULL, no_cov=False, files=())


def test_level_never_shapes_the_other_subcommands() -> None:
    """Only the full run is shaped: affected stays covered at pass."""
    affected = runner.pytest_command(
        "pytest", runner.SUB_AFFECTED, no_cov=False, files=(), level=FullLevel.PASS,
    )
    assert "--cov-append" in affected


def test_timings_command_is_sequential_uninstrumented_and_timed() -> None:
    """The timing pass sees every test with no workers and no coverage (Q39).

    Workers make a call time a measure of contention and coverage inflates it,
    so the only run that judges durations carries neither.
    """
    command = runner.pytest_command("pytest", runner.SUB_TIMINGS, no_cov=False, files=())
    assert command == [
        "pytest",
        "--no-header",
        "--no-cov",
        "-v",
        "--durations=0",
        "--durations-min=0",
    ]
    assert "-n" not in command
    assert "--testmon" not in command


def test_worker_run_never_shares_a_session_with_testmon() -> None:
    """Testmon and xdist abort together, so only the affected run keeps testmon."""
    full_no_cov = runner.pytest_command(
        "pytest", runner.SUB_FULL, no_cov=True, files=(), parallel=True,
    )
    affected = runner.pytest_command(
        "pytest", runner.SUB_AFFECTED, no_cov=False, files=(), parallel=True,
    )
    assert full_no_cov == ["pytest", "-n", "auto", "--dist", "loadgroup", "--no-header", "--no-cov", "-v"]
    assert "--testmon" in affected
    assert "-n" not in affected


def test_parallel_is_opt_in_per_project(tmp_path: Path) -> None:
    """Only a project declaring the marker file gets the worker command."""
    assert runner.parallel_enabled(tmp_path) is False
    (tmp_path / runner.PARALLEL_MARKER).write_text("opt in\n", encoding="utf-8")
    assert runner.parallel_enabled(tmp_path) is True


def test_bare_root_is_not_a_pytest_project(tmp_path: Path) -> None:
    """A root with no pytest marker, like a batch-only project, has no suite."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    assert runner.is_pytest_project(tmp_path) is False


def test_each_root_file_marks_a_pytest_project(tmp_path: Path) -> None:
    """pyproject.toml, pytest.ini or conftest.py alone make a pytest project."""
    for name in runner.PYTEST_ROOT_FILES:
        root = tmp_path / name.replace(".", "_")
        root.mkdir()
        (root / name).write_text("", encoding="utf-8")
        assert runner.is_pytest_project(root) is True


def test_shared_ini_counts_only_with_its_pytest_section(tmp_path: Path) -> None:
    """setup.cfg and tox.ini mark a pytest project only through pytest's section."""
    for name, section in runner.PYTEST_INI_SECTIONS:
        root = tmp_path / name.replace(".", "_")
        root.mkdir()
        ini = root / name
        ini.write_text("[metadata]\nname = demo\n", encoding="utf-8")
        assert runner.is_pytest_project(root) is False
        ini.write_text(f"{section}\naddopts = -q\n", encoding="utf-8")
        assert runner.is_pytest_project(root) is True


def test_affected_and_single_never_time_durations() -> None:
    """Only a full or timings run carries --durations flags (Q39)."""
    for sub, files in (
        (runner.SUB_AFFECTED, ()),
        (runner.SUB_SINGLE, ("tests/test_a.py",)),
    ):
        command = runner.pytest_command("pytest", sub, no_cov=False, files=files)
        assert "--durations=0" not in command, sub
        assert "--durations-min=0" not in command, sub


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


def test_run_streaming_with_the_real_factory(tmp_path: Path) -> None:
    """The default factory streams a real child and returns its code."""
    config = runner.StreamConfig(
        command=[
            sys.executable,
            "-I",
            "-S",
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


def test_run_pytest_flags_an_interruption_that_judged_nothing(tmp_path: Path) -> None:
    """A signal, a KeyboardInterrupt or a pytest.exit before any failure judged no gate.

    The banners are the ones the installed pytest prints. A pytest.exit
    crashes the run with any return code of its own, 0 and 1 included, since
    the suite never finished. pytest's interrupted exit with the
    collection-error banner is a collection error, and a failure or an
    internal error seen first is still evidence: neither counts as an
    interruption.
    """
    banner = "!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!"
    messaged = "!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt: stopped !!!!!!!!!!!!!!!!!!!!!!!!!!"
    exited = "!!!!!!!!!!!!!!!!!!!!!!! _pytest.outcomes.Exit: stopped !!!!!!!!!!!!!!!!!!!!!!!!"
    collection = "!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!"
    passed = "tests/test_a.py::test_one PASSED [ 50%]"
    failed = "tests/test_a.py::test_two FAILED [100%]"
    cases = (
        ([passed, banner], PYTEST_INTERRUPTED, True),
        ([passed, messaged], PYTEST_INTERRUPTED, True),
        ([passed, exited], PYTEST_INTERRUPTED, True),
        ([passed, exited], PYTEST_INTERNAL_ERROR, True),
        ([passed, exited], PYTEST_TEST_FAILURES, True),
        ([passed, exited], PYTEST_OK, True),
        ([failed, exited], PYTEST_TEST_FAILURES, False),
        ([passed], -9, True),
        ([passed], PYTEST_INTERRUPTED, False),
        ([collection], PYTEST_INTERRUPTED, False),
        ([failed, banner], PYTEST_INTERRUPTED, False),
        (["INTERNALERROR> boom", banner], PYTEST_INTERRUPTED, False),
    )
    for lines, code, expected in cases:
        result = runner.run_pytest(_config(lines, code, tmp_path), lambda _stats: None)
        assert (result.crashed, result.interrupted) == (True, expected), (lines, code)


@pytest.mark.parametrize("sub", ["full", "affected", "timings", "single"])
def test_group_collection_and_coverage_options(sub: str) -> None:
    """Scope narrows suite commands while single retains explicitly named files."""
    command = runner.pytest_command("pytest", sub, no_cov=False, files=("focus.py",),
                                    test_paths=("tests/group/test_a.py",), cov_folders=("src/group",))
    assert command[-1] == ("focus.py" if sub == "single" else "tests/group/test_a.py")
    if sub in ("full", "affected"):
        assert "--cov=src/group" in command
        assert "--cov-fail-under=0" in command
    else:
        assert "--cov=src/group" not in command


@pytest.mark.parametrize("previous", [None, "previous.coverage"])
@pytest.mark.parametrize("raises", [True, False])
def test_spawn_environment_restored(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, previous: str | None, *, raises: bool) -> None:
    """A temporary coverage override ends immediately after either spawn outcome."""
    if previous is None:
        monkeypatch.delenv("COVERAGE_FILE", raising=False)
    else:
        monkeypatch.setenv("COVERAGE_FILE", previous)

    def factory(_command: list[str], _cwd: Path) -> subprocess.Popen[str]:
        assert os.environ["COVERAGE_FILE"] == "group.coverage"
        if raises:
            message = "spawn failed"
            raise OSError(message)
        return cast("subprocess.Popen[str]", _FakeProcess(["output"], 0))

    def on_line(_line: str) -> None:
        assert os.environ.get("COVERAGE_FILE") == previous

    config = runner.StreamConfig(["pytest"], tmp_path, factory, env_overrides={"COVERAGE_FILE": "group.coverage"})
    if raises:
        with pytest.raises(OSError, match="spawn failed"):
            runner.run_streaming(config, on_line)
    else:
        assert runner.run_streaming(config, on_line) == 0
    assert os.environ.get("COVERAGE_FILE") == previous


# eof
