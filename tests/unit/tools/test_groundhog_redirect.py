"""Unit tests for the groundhog self-redirect guard (Q31).

Cover the pipe detection behind the guard, the arming rules (LLM mode
plus a captured stdout, with the user-mode, redirected-file and
unwritable-log fallbacks), the envelope mirror, the senv side-log
replay, and one end-to-end check run proving the report lands in
``a.ghog.log`` while the captured stdout receives only the notice,
next-step and closing lines.

Fix: new test module for the Q31 guard — a real pdfsplitter session ran
``ghog day`` unredirected five times, flooding its context with the full
reports and losing one report to a harness timeout; the guard makes the
redirect contract tool-side instead of docs-only.
"""

from __future__ import annotations

import io
import logging
import os
import sys
from typing import TYPE_CHECKING, cast

from tools.groundhog import cli, redirect, reporting
from tools.groundhog.models import EXIT_OBJECTIVE_MET, Mode

if TYPE_CHECKING:
    import subprocess
    from pathlib import Path

    import pytest


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


def _deps(lines: list[str], code: int) -> cli.Deps:
    """Build CLI deps around one canned child process.

    Args:
        lines: The scripted child output lines.
        code: The scripted child exit code.

    Returns:
        The injectable seams.
    """

    def _factory(command: list[str], cwd: Path) -> subprocess.Popen[str]:
        del command, cwd
        return cast("subprocess.Popen[str]", _FakeProcess(lines, code))

    return cli.Deps(popen_factory=_factory)


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


def _close_log_handlers() -> None:
    """Release the guard's file handler so the log can be read."""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.close()
    root_logger.handlers.clear()


def test_stdout_is_captured_on_pipes_and_capture_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A pipe or a capture file arms the probe; the log itself does not.

    The one regular file that keeps streaming is the project's own
    ``a.ghog.log``: that is the caller-side redirect of the contract,
    where stdout already lands in the log (Q31).
    """
    read_fd, writer = _pipe_stdout(monkeypatch)
    assert redirect.stdout_is_captured(tmp_path) is True
    _drain(read_fd, writer)
    with (tmp_path / "harness-capture.tmp").open("w", encoding="utf-8") as stream:
        monkeypatch.setattr(sys, "stdout", stream)
        assert redirect.stdout_is_captured(tmp_path) is True
    with (tmp_path / redirect.LOG_NAME).open("w", encoding="utf-8") as stream:
        monkeypatch.setattr(sys, "stdout", stream)
        assert redirect.stdout_is_captured(tmp_path) is False
    with open(os.devnull, "w", encoding="utf-8") as stream:  # noqa: PTH123
        monkeypatch.setattr(sys, "stdout", stream)
        assert redirect.stdout_is_captured(tmp_path) is False
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    assert redirect.stdout_is_captured(tmp_path) is False


def test_stdout_probe_survives_a_failing_fstat(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A failing fstat keeps the guard off instead of crashing (Q31)."""
    with (tmp_path / "out.log").open("w", encoding="utf-8") as stream:
        monkeypatch.setattr(sys, "stdout", stream)

        def _boom(fd: int) -> os.stat_result:
            raise OSError(9, "bad file descriptor", str(fd))

        monkeypatch.setattr(os, "fstat", _boom)
        assert redirect.stdout_is_captured(tmp_path) is False


def test_activate_needs_llm_mode_and_a_capture(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """User mode and the caller-side redirect never arm the guard."""
    monkeypatch.setattr(redirect, "_summary", None)
    read_fd, writer = _pipe_stdout(monkeypatch)
    assert redirect.activate_if_captured(Mode.USER, tmp_path) is False
    _drain(read_fd, writer)
    with (tmp_path / redirect.LOG_NAME).open("w", encoding="utf-8") as stream:
        monkeypatch.setattr(sys, "stdout", stream)
        assert redirect.activate_if_captured(Mode.LLM, tmp_path) is False
    assert (tmp_path / redirect.LOG_NAME).read_text(encoding="utf-8") == ""


def test_activate_arms_the_log_and_mirrors_the_notice(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An armed guard logs to a.ghog.log and mirrors the notice (Q31)."""
    monkeypatch.setattr(redirect, "_summary", None)
    read_fd, writer = _pipe_stdout(monkeypatch)
    assert redirect.activate_if_captured(Mode.LLM, tmp_path) is True
    with caplog.at_level(logging.INFO, logger="groundhog"):
        logging.getLogger("groundhog").info("report body line")
    _close_log_handlers()
    captured = _drain(read_fd, writer)
    log_text = (tmp_path / redirect.LOG_NAME).read_text(encoding="utf-8")
    assert redirect.MSG_SELF_REDIRECT in captured
    assert "report body line" not in captured
    assert "report body line" in log_text


def test_activate_falls_back_on_an_unopenable_log(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An unwritable log keeps the run streaming as before (Q31)."""
    monkeypatch.setattr(redirect, "_summary", None)
    (tmp_path / redirect.LOG_NAME).mkdir()
    read_fd, writer = _pipe_stdout(monkeypatch)
    assert redirect.activate_if_captured(Mode.LLM, tmp_path) is False
    captured = _drain(read_fd, writer)
    assert captured == ""


def test_mirror_is_a_noop_while_inactive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without an armed guard the mirror writes nothing."""
    monkeypatch.setattr(redirect, "_summary", None)
    redirect.mirror(["never shown"])
    buffer = io.StringIO()
    monkeypatch.setattr(redirect, "_summary", buffer)
    redirect.mirror(["echoed line"])
    assert buffer.getvalue() == "echoed line\n"


def test_replay_senv_log_without_the_env_variable(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """No side-log variable means nothing to replay."""
    monkeypatch.delenv(redirect.SENV_LOG_ENV, raising=False)
    with caplog.at_level(logging.INFO, logger="groundhog"):
        redirect.replay_senv_log()
    assert caplog.text == ""


def test_replay_senv_log_with_a_missing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A vanished side log is silently skipped."""
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(tmp_path / "absent.log"))
    with caplog.at_level(logging.INFO, logger="groundhog"):
        redirect.replay_senv_log()
    assert caplog.text == ""


def test_replay_senv_log_replays_and_deletes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The parked senv preamble is replayed line by line, then deleted."""
    side = tmp_path / "a.ghog.senv.log"
    side.write_text(
        " OK    : [senv.bat] Environment initialized\n INFO  : [senv.bat] applied\n",
        encoding="utf-8",
    )
    monkeypatch.setenv(redirect.SENV_LOG_ENV, str(side))
    with caplog.at_level(logging.INFO, logger="groundhog"):
        redirect.replay_senv_log()
    assert "Environment initialized" in caplog.text
    assert "[senv.bat] applied" in caplog.text
    assert not side.exists()


def test_unredirected_check_run_hands_back_the_envelope_only(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """End to end: the report fills a.ghog.log, stdout gets the envelope.

    The check body lines stay in the log; the captured stdout carries
    the notice, the next-step message and the closing line — the exact
    branching material of the loop contract (Q31).
    """
    monkeypatch.setattr(redirect, "_summary", None)
    monkeypatch.delenv(redirect.SENV_LOG_ENV, raising=False)
    (tmp_path / "check.bat").write_text("@echo off\n", encoding="utf-8")
    read_fd, writer = _pipe_stdout(monkeypatch)
    deps = _deps([" INFO  : [check.bat] body detail line"], 0)
    code = cli.main(["check", "--root", str(tmp_path), "--llm"], deps)
    _close_log_handlers()
    captured = _drain(read_fd, writer)
    log_text = (tmp_path / redirect.LOG_NAME).read_text(encoding="utf-8")
    assert code == EXIT_OBJECTIVE_MET
    assert redirect.MSG_SELF_REDIRECT in captured
    assert reporting.MSG_CHECK_OK in captured
    assert "ghog check done" in captured
    assert "body detail line" not in captured
    assert "body detail line" in log_text
    assert reporting.MSG_CHECK_OK in log_text


# eof
