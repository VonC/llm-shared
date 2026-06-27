"""Unit tests for the detached groundhog day walk and its survivor spawn (Q32).

Cover the launcher hand-off (command shape, log path, senv preamble and
root), the exit-6 acknowledgment once the child's first status write lands,
the ``--force`` forwarding, the stale-status clearing before the handshake,
the spawn-failure and silent-child paths, the launcher envelope kept on
stdout, the default detach factory and its preamble handling, the survivor
creation flags, and the senv side-log consumption.

Fix: the survivor spawn switched from DETACHED_PROCESS to CREATE_NO_WINDOW --
a console-free survivor made its console children (check.bat, pytest) pop a
visible console window during a detached walk. The spawn tests pin the
hidden-console flags on the breakaway try and on its fallback, and reject
DETACHED_PROCESS.

Fix (split): these tests were carved out of ``test_groundhog_status.py`` so
each test file stays within the repository line budget; the status read/write,
pid probe, verdict and lifecycle tests stay in that file.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Final, cast

from tools.groundhog import cli, redirect, reporting, runner, status
from tools.groundhog.models import (
    EXIT_OBJECTIVE_MET,
    EXIT_RUN_LIVE,
    EXIT_SETUP_ERROR,
)

if TYPE_CHECKING:
    import io
    from pathlib import Path

    import pytest

_DETACHED_PID: Final = 4242


class _FakeSurvivor:
    """A fake detached process: only the pid matters to the launcher."""

    def __init__(self, pid: int) -> None:
        """Record the scripted pid.

        Args:
            pid: The pid handed back to the launcher.
        """
        self.pid = pid


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


def test_day_detach_hands_the_command_to_the_spawn(
    tmp_path: Path,
) -> None:
    """The launcher builds the survivor command: cli.py day, llm, root, no force."""
    calls: list[list[str]] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del log_path, preamble, cwd
        calls.append(command)
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    command = calls[0]
    assert command[0] == sys.executable
    assert command[1].endswith("cli.py")
    assert runner.SUB_DAY in command
    assert "--llm" in command
    assert str(tmp_path) in command
    assert "--force" not in command


def test_day_detach_acknowledges_and_consumes_the_preamble(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The launcher hands log, preamble and root to the spawn, then acks exit 6.

    The acknowledgment is exit 6 -- a run is live -- once the child's first
    status write lands, and the senv side log is consumed (Q32).
    """
    side = tmp_path / "a.ghog.senv.log"
    side.write_text("senv preamble line\n", encoding="utf-8")
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(side))
    calls: list[tuple[Path, str, Path]] = []

    def _factory(command: list[str], log_path: Path, preamble: str, cwd: Path) -> int:
        del command
        calls.append((log_path, preamble, cwd))
        status.write_running(tmp_path, "day")
        return _DETACHED_PID

    deps = cli.Deps(detach_factory=_factory, sleep=lambda _seconds: None)
    code = cli.main(["day", "--detach", "--root", str(tmp_path), "--llm"], deps)
    assert code == EXIT_RUN_LIVE
    log_path, preamble, cwd = calls[0]
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
    command = (
        ["cmd", "/d", "/c", "echo detached-mark"]
        if sys.platform == "win32"
        else [sys.executable, "-S", "-c", "print('detached-mark')"]
    )
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
