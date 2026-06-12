"""Unit tests for the groundhog run lifecycle (Q32).

Cover the ``a.ghog.status`` read/write mechanics, the pid liveness
probe on both platforms, the read-only ``ghog status`` verdicts and
their exit codes, the live-run refusal, the running/done bracket
around a real dispatch, and the detached day walk: command shape,
senv preamble hand-off, stale-status clearing, start handshake, spawn
fallbacks and failures.

Fix: the survivor spawn switched from DETACHED_PROCESS to
CREATE_NO_WINDOW — a console-free survivor made its console children
(check.bat, pytest) pop a visible console window during a detached
walk. The spawn tests now pin the hidden-console flags on the
breakaway try and on its fallback, and reject DETACHED_PROCESS.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
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
_DETACHED_PID: Final = 4242


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


class _FakeSurvivor:
    """A fake detached process: only the pid matters to the launcher."""

    def __init__(self, pid: int) -> None:
        """Record the scripted pid.

        Args:
            pid: The pid handed back to the launcher.
        """
        self.pid = pid


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


def test_write_running_then_done_round_trip(tmp_path: Path) -> None:
    """A run brackets itself: running with the pid, done with the exit.

    The atomic side file is consumed by the replace, and the done line
    drops the pid in favor of the exit code (Q32).
    """
    status.write_running(tmp_path, "affected --no-cov")
    recorded = status.read_status(tmp_path)
    assert recorded is not None
    assert recorded.state == status.STATE_RUNNING
    assert recorded.pid == os.getpid()
    assert recorded.exit_code is None
    assert f"{tmp_path.name}: ghog affected --no-cov state=running" in recorded.line
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
        [sys.executable, "-c", "pass"],
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


def test_day_detach_spawns_the_survivor_and_acknowledges(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The launcher hands command, log, preamble and root to the spawn.

    The acknowledgment is exit 6 — a run is live — once the child's
    first status write lands, and the senv side log is consumed (Q32).
    """
    side = tmp_path / "a.ghog.senv.log"
    side.write_text("senv preamble line\n", encoding="utf-8")
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(side))
    calls: list[tuple[list[str], Path, str, Path]] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        calls.append((command, log_path, preamble, cwd))
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    command, log_path, preamble, cwd = calls[0]
    assert command[0] == sys.executable
    assert command[1].endswith("cli.py")
    assert runner.SUB_DAY in command
    assert "--llm" in command
    assert str(tmp_path) in command
    assert "--force" not in command
    assert log_path == tmp_path / redirect.LOG_NAME
    assert "senv preamble line" in preamble
    assert cwd == tmp_path
    assert f"detached (pid={_DETACHED_PID})" in capsys.readouterr().out
    assert not side.exists()


def test_day_detach_forwards_the_force_flag(
    tmp_path: Path,
) -> None:
    """A forced detached walk carries --force to the survivor command."""
    commands_seen: list[list[str]] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del log_path, preamble, cwd
        commands_seen.append(command)
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    argv = ["day", "--detach", "--force", "--root", str(tmp_path), "--llm"]
    code = cli.main(argv, deps)
    assert code == EXIT_RUN_LIVE
    assert "--force" in commands_seen[0]


def test_day_detach_clears_a_stale_status_before_the_handshake(
    tmp_path: Path,
) -> None:
    """A leftover done file is cleared, so the handshake sees the child."""
    status.write_done(tmp_path, "day", EXIT_OBJECTIVE_MET)
    observed: list[status.RunStatus | None] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del command, log_path, preamble, cwd
        observed.append(status.read_status(tmp_path))
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    assert observed == [None]


def test_day_detach_reports_a_spawn_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A spawn error is the loud setup exit, not a silent fork."""

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del command, log_path, preamble, cwd
        message = "blocked by the sandbox"
        raise OSError(message)

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_SETUP_ERROR
    assert "failed to start" in capsys.readouterr().out


def test_day_detach_reports_a_silent_child(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A child that never writes its status fails the handshake."""
    naps: list[float] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del command, log_path, preamble, cwd
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=naps.append)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_SETUP_ERROR
    assert reporting.MSG_DETACH_SILENT in capsys.readouterr().out
    assert len(naps) == status._HANDSHAKE_TRIES


def test_day_detach_keeps_the_launcher_envelope_on_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An unredirected launcher never arms the Q31 guard (Q32)."""
    read_fd, writer = _pipe_stdout(monkeypatch)

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del command, log_path, preamble, cwd
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    captured = _drain(read_fd, writer)
    assert code == EXIT_RUN_LIVE
    assert f"detached (pid={_DETACHED_PID})" in captured
    assert not (tmp_path / redirect.LOG_NAME).exists()


def test_default_detach_factory_spawns_a_real_survivor(tmp_path: Path) -> None:
    """End to end: the survivor writes after the preamble in the log."""
    log_path = tmp_path / "detached.log"
    command = [sys.executable, "-c", "print('detached-mark')"]
    pid = status.default_detach_factory(command, log_path, "senv preamble", tmp_path)
    assert pid > 0
    deadline = time.monotonic() + 30.0
    text = ""
    while time.monotonic() < deadline:
        text = log_path.read_text(encoding="utf-8")
        if "detached-mark" in text:
            break
        time.sleep(0.05)
    assert text.startswith("senv preamble\n")
    assert "detached-mark" in text
    while status.pid_alive(pid) and time.monotonic() < deadline:
        time.sleep(0.05)


def test_default_detach_factory_skips_an_empty_preamble(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Without a preamble the log opens empty for the child."""

    def _fake_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        del args, kwargs
        return cast("subprocess.Popen[bytes]", _FakeSurvivor(_DETACHED_PID))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    log_path = tmp_path / "detached.log"
    pid = status.default_detach_factory(["child"], log_path, "", tmp_path)
    assert pid == _DETACHED_PID
    assert log_path.read_text(encoding="utf-8") == ""


def test_default_detach_factory_keeps_a_terminated_preamble(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A preamble already ending in a newline is written verbatim."""

    def _fake_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        del args, kwargs
        return cast("subprocess.Popen[bytes]", _FakeSurvivor(_DETACHED_PID))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    log_path = tmp_path / "detached.log"
    status.default_detach_factory(["child"], log_path, "preamble\n", tmp_path)
    assert log_path.read_text(encoding="utf-8") == "preamble\n"


def test_spawn_survivor_hides_the_console_window(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The survivor spawns with a hidden console, never console-free.

    DETACHED_PROCESS would make the walk's console children
    (check.bat, pytest) allocate a fresh visible console window;
    CREATE_NO_WINDOW hands them a hidden console to inherit.
    """
    kwargs_seen: dict[str, object] = {}

    def _fake_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        del args
        kwargs_seen.update(kwargs)
        return cast("subprocess.Popen[bytes]", _FakeSurvivor(_DETACHED_PID))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    log_path = tmp_path / "detached.log"
    pid = status.default_detach_factory(["child"], log_path, "", tmp_path)
    assert pid == _DETACHED_PID
    flags = cast("int", kwargs_seen.get("creationflags", 0))
    assert flags & subprocess.CREATE_NO_WINDOW
    assert flags & subprocess.CREATE_NEW_PROCESS_GROUP
    assert flags & subprocess.CREATE_BREAKAWAY_FROM_JOB
    assert flags & subprocess.DETACHED_PROCESS == 0


def test_spawn_survivor_falls_back_when_breakaway_is_denied(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A job that forbids breakaway gets the plain no-window flags."""
    attempts: list[int] = []

    def _fake_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        del args
        flags = cast("int", kwargs.get("creationflags", 0))
        attempts.append(flags)
        if flags & subprocess.CREATE_BREAKAWAY_FROM_JOB:
            message = "breakaway denied"
            raise OSError(message)
        return cast("subprocess.Popen[bytes]", _FakeSurvivor(_DETACHED_PID))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    log_path = tmp_path / "detached.log"
    pid = status.default_detach_factory(["child"], log_path, "", tmp_path)
    assert pid == _DETACHED_PID
    expected_attempts = 2
    assert len(attempts) == expected_attempts
    assert attempts[1] & subprocess.CREATE_BREAKAWAY_FROM_JOB == 0
    assert attempts[1] & subprocess.CREATE_NO_WINDOW
    assert attempts[1] & subprocess.DETACHED_PROCESS == 0


def test_spawn_survivor_uses_a_new_session_off_windows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Off Windows the survivor starts its own session, no Windows flags."""
    monkeypatch.setattr(sys, "platform", "linux")
    kwargs_seen: dict[str, object] = {}

    def _fake_popen(*args: object, **kwargs: object) -> subprocess.Popen[bytes]:
        del args
        kwargs_seen.update(kwargs)
        return cast("subprocess.Popen[bytes]", _FakeSurvivor(_DETACHED_PID))

    monkeypatch.setattr(subprocess, "Popen", _fake_popen)
    log_path = tmp_path / "detached.log"
    pid = status.default_detach_factory(["child"], log_path, "", tmp_path)
    assert pid == _DETACHED_PID
    assert kwargs_seen.get("start_new_session") is True
    assert "creationflags" not in kwargs_seen


def test_consume_senv_log_returns_the_text_and_deletes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The side log is handed back once, then gone (Q31, Q32)."""
    side = tmp_path / "a.ghog.senv.log"
    side.write_text("preamble text\n", encoding="utf-8")
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(side))
    assert redirect.consume_senv_log() == "preamble text\n"
    assert not side.exists()
    assert redirect.consume_senv_log() == ""
    monkeypatch.delenv(redirect.SENV_LOG_ENV)
    assert redirect.consume_senv_log() == ""


# eof
