"""Unit tests for the groundhog run lifecycle and status verdicts (Q32).

Cover the ``a.ghog.status`` read/write mechanics, the pid liveness probe on
both platforms, the read-only ``ghog status`` verdicts and their exit codes,
the live-run refusal, and the running/done bracket around a real dispatch.

Fix (split): the detached day walk and survivor-spawn tests moved to
``test_groundhog_detach.py`` so each test file stays within the repository
line budget; the ``write_running``/``write_done`` round trip split into a
write_running test and a write_done test, each below the complexity gate.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from typing import TYPE_CHECKING, Final, cast

import pytest

from tools.groundhog import cli, commands, redirect, reporting, runner, status
from tools.groundhog.models import (
    EXIT_COVERAGE_GAP,
    EXIT_OBJECTIVE_MET,
    EXIT_RUN_LIVE,
    EXIT_RUN_LOST,
    EXIT_SETUP_ERROR,
    Mode,
)

if TYPE_CHECKING:
    import io
    from pathlib import Path

# A pid no Windows or POSIX system hands out in practice: DWORD-safe,
# multiple of 4, close to the 32-bit ceiling.
_NEVER_A_PID: Final = 0xFFFF_FFF0


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


def _invocation(sub: str, root: Path, *, force: bool = False) -> cli.Invocation:
    """Build an invocation for direct executor tests.

    Args:
        sub: The subcommand name.
        root: The project root.
        force: The day --force flag.

    Returns:
        The invocation.
    """
    return cli.Invocation(
        sub=sub,
        files=(),
        no_cov=False,
        mode=Mode.LLM,
        root=root,
        force=force,
    )


def _pipe_stdout(monkeypatch: pytest.MonkeyPatch) -> tuple[int, io.TextIOWrapper]:
    """Swap stdout for the write end of a fresh pipe.

    Args:
        monkeypatch: The patcher restoring stdout after the test.

    Returns:
        The read file descriptor and the writer now sitting as stdout.
    """
    read_fd, write_fd = os.pipe()
    writer = os.fdopen(write_fd, "w", encoding="utf-8")
    monkeypatch.setattr(sys, "stdout", writer)
    return read_fd, writer


def _drain(read_fd: int, writer: io.TextIOWrapper) -> str:
    """Close the pipe writer and read everything from the read end.

    Args:
        read_fd: The pipe read file descriptor.
        writer: The pipe writer to close first.

    Returns:
        The captured pipe content.
    """
    writer.close()
    with os.fdopen(read_fd, "r", encoding="utf-8") as reader:
        return reader.read()


def test_write_running_records_the_running_pid(tmp_path: Path) -> None:
    """write_running stamps the running state, this pid, no exit, and the line."""
    status.write_running(tmp_path, "affected --no-cov")
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_RUNNING
    assert recorded.pid == os.getpid()
    assert recorded.exit_code is None
    assert f"{tmp_path.name}: ghog affected --no-cov state=running" in recorded.line


def test_write_done_drops_the_pid_for_the_exit_code(tmp_path: Path) -> None:
    """write_done replaces the running line: done state, the exit, no pid (Q32).

    The atomic side file is consumed by the replace, so it never lingers.
    """
    status.write_running(tmp_path, "affected --no-cov")
    status.write_done(tmp_path, "affected --no-cov", EXIT_COVERAGE_GAP)
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_DONE
    assert recorded.pid is None
    assert recorded.exit_code == EXIT_COVERAGE_GAP
    side = tmp_path / f"{status.STATUS_FILE_NAME}.tmp"
    assert not side.exists()


def test_read_status_on_missing_corrupt_or_unreadable_files(
    tmp_path: Path,
) -> None:
    """No file, no state= key, junk bytes or a directory all read as None."""
    assert status.read_status(tmp_path) is None
    path = tmp_path / status.STATUS_FILE_NAME
    path.write_text("garbage without the key\n", encoding="utf-8")
    assert status.read_status(tmp_path) is None
    path.write_bytes(b"\xff\xfe broken")
    assert status.read_status(tmp_path) is None
    path.unlink()
    path.mkdir()
    assert status.read_status(tmp_path) is None


def test_status_write_failure_is_reported_not_fatal(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An unwritable status file logs a notice instead of killing the run."""
    (tmp_path / status.STATUS_FILE_NAME).mkdir()
    with caplog.at_level(logging.INFO, logger="groundhog"):
        status.write_running(tmp_path, "day")
    assert "could not write" in caplog.text


def test_pid_alive_on_windows_probes(tmp_path: Path) -> None:
    """The probe sees this process alive, junk and finished pids dead."""
    del tmp_path
    assert status.pid_alive(os.getpid()) is True
    assert status.pid_alive(0) is False
    assert status.pid_alive(-7) is False
    assert status.pid_alive(_NEVER_A_PID) is False
    child = subprocess.Popen(  # noqa: S603
        [sys.executable, "-S", "-c", "pass"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    child.wait()
    # The held Popen handle keeps the pid reserved, so the probe takes
    # the opened-but-exited path instead of the open-failure path.
    assert status.pid_alive(child.pid) is False


def test_pid_alive_posix_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    """Off Windows the probe signals 0: gone, owned-by-other, alive.

    A signal failing with any other OSError (an invalid pid value, for
    example) also reads as dead — the relaunch direction.
    """
    monkeypatch.setattr(sys, "platform", "linux")
    outcomes: list[Exception | None] = [
        ProcessLookupError(),
        PermissionError(),
        None,
        OSError(22, "invalid argument"),
    ]

    def _fake_kill(pid: int, sig: int) -> None:
        del pid, sig
        outcome = outcomes.pop(0)
        if outcome is not None:
            raise outcome

    monkeypatch.setattr(os, "kill", _fake_kill)
    assert status.pid_alive(123) is False
    assert status.pid_alive(123) is True
    assert status.pid_alive(123) is True
    assert status.pid_alive(123) is False


def test_live_run_only_reports_a_running_alive_pid(tmp_path: Path) -> None:
    """Missing, done, pid-free and dead-pid statuses are never live."""
    assert status.live_run(tmp_path) is None
    status.write_done(tmp_path, "day", EXIT_OBJECTIVE_MET)
    assert status.live_run(tmp_path) is None
    path = tmp_path / status.STATUS_FILE_NAME
    path.write_text("x: ghog day state=running started=now\n", encoding="utf-8")
    assert status.live_run(tmp_path) is None
    path.write_text(
        f"x: ghog day state=running pid={_NEVER_A_PID} started=now\n",
        encoding="utf-8",
    )
    assert status.live_run(tmp_path) is None
    status.write_running(tmp_path, "day")
    live = status.live_run(tmp_path)
    assert live is not None
    assert live.pid == os.getpid()


def test_lifecycle_brackets_a_run_with_running_and_done(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A check run is running while the child works, done after (Q32)."""
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    seen: list[str | None] = []

    def _factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
        del command, cwd
        recorded = status.read_status(tmp_path)
        seen.append(None if recorded is None else recorded.state)
        return cast(
            "subprocess.Popen[str]",
            _FakeProcess([" OK    : [check.bat] fine"], 0),
        )

    code = cli.main(
        ["check", "--root", str(tmp_path), "--llm"],
        cli.Deps(popen_factory=_factory),
    )
    assert code == EXIT_OBJECTIVE_MET
    assert seen == [status.STATE_RUNNING]
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_DONE
    assert recorded.exit_code == EXIT_OBJECTIVE_MET
    assert "ghog check done" in capsys.readouterr().out


def test_lifecycle_records_done_even_when_the_dispatch_raises(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A crashing dispatch still leaves state=done with the setup code."""
    monkeypatch.setattr(redirect, "_summary", None)

    def _boom(invocation: cli.Invocation, deps: cli.Deps) -> int:
        del invocation, deps
        message = "dispatch broke"
        raise RuntimeError(message)

    monkeypatch.setattr(commands, "run_check", _boom)
    with pytest.raises(RuntimeError, match="dispatch broke"):
        status.run_with_lifecycle(
            _invocation(runner.SUB_CHECK, tmp_path),
            cli.Deps(),
        )
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_DONE
    assert recorded.exit_code == EXIT_SETUP_ERROR


def test_status_without_a_recorded_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No status file means no proof: exit 7 and the relaunch hint."""
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    assert code == EXIT_RUN_LOST
    assert reporting.MSG_STATUS_NONE in capsys.readouterr().out


def test_status_on_a_live_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A running state with an alive pid polls as exit 6."""
    status.write_running(tmp_path, "day")
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    assert code == EXIT_RUN_LIVE
    out = capsys.readouterr().out
    assert "state=running" in out
    assert reporting.MSG_STATUS_RUNNING in out


def test_status_on_a_killed_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A running state with a dead pid is a lost run: exit 7."""
    path = tmp_path / status.STATUS_FILE_NAME
    path.write_text(
        f"x: ghog day state=running pid={_NEVER_A_PID} started=now\n",
        encoding="utf-8",
    )
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    assert code == EXIT_RUN_LOST
    assert reporting.MSG_STATUS_KILLED in capsys.readouterr().out


def test_status_done_passes_the_recorded_exit_through(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A done state answers with the run's own exit code."""
    status.write_done(tmp_path, "day", EXIT_COVERAGE_GAP)
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    assert code == EXIT_COVERAGE_GAP
    out = capsys.readouterr().out
    assert "state=done" in out
    assert reporting.MSG_STATUS_DONE in out


def test_status_done_without_an_exit_reads_as_lost(
    tmp_path: Path,
) -> None:
    """A done line missing its exit= key cannot be branched on: exit 7."""
    path = tmp_path / status.STATUS_FILE_NAME
    path.write_text("x: ghog day state=done ended=now\n", encoding="utf-8")
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    assert code == EXIT_RUN_LOST


def test_status_never_arms_the_self_redirect(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The poll keeps its envelope on stdout and discards the senv log.

    A redirect-armed poll would truncate the live walk's a.ghog.log;
    the senv preamble would bloat the two-line envelope (Q32).
    """
    side = tmp_path / "a.ghog.senv.log"
    side.write_text("senv noise line\n", encoding="utf-8")
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(side))
    status.write_done(tmp_path, "day", EXIT_OBJECTIVE_MET)
    read_fd, writer = _pipe_stdout(monkeypatch)
    code = cli.main(["status", "--root", str(tmp_path), "--llm"])
    captured = _drain(read_fd, writer)
    assert code == EXIT_OBJECTIVE_MET
    assert "state=done" in captured
    assert "senv noise line" not in captured
    assert not side.exists()
    assert not (tmp_path / redirect.LOG_NAME).exists()


def test_run_refused_while_another_run_is_live(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A second run exits 6 without spawning and leaves the status alone."""
    status.write_running(tmp_path, "day")
    spawned: list[list[str]] = []

    def _factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
        del cwd
        spawned.append(command)
        return cast("subprocess.Popen[str]", _FakeProcess([], 0))

    code = cli.main(
        ["check", "--root", str(tmp_path), "--llm"],
        cli.Deps(popen_factory=_factory),
    )
    assert code == EXIT_RUN_LIVE
    assert spawned == []
    assert "already live" in capsys.readouterr().out
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_RUNNING


def test_refusal_keeps_the_live_log_untouched(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An unredirected refused run never opens a.ghog.log (Q32)."""
    status.write_running(tmp_path, "day")
    read_fd, writer = _pipe_stdout(monkeypatch)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"])
    captured = _drain(read_fd, writer)
    assert code == EXIT_RUN_LIVE
    assert "already live" in captured
    assert not (tmp_path / redirect.LOG_NAME).exists()


# eof
