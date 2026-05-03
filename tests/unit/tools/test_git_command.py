"""Tests for cross-platform Git command dispatch branches.

Fix: Cover shell-command assembly and both Windows and Linux subprocess
dispatch paths in `tools.git_command`.
"""

from __future__ import annotations

import shlex
import subprocess
from typing import TYPE_CHECKING

from tools import git_command

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def _build_linux_status_command(_git_args: list[str]) -> str:
    return "command git status --short"


def test_build_linux_git_shell_command_quotes_arguments() -> None:
    """The Linux helper should join Git arguments with shell-safe quoting."""
    git_args = ["commit", "-m", "message with spaces"]

    assert git_command._build_linux_git_shell_command(git_args) == (
        f"{git_command._GIT_COMMAND_PREFIX} {shlex.join(git_args)}"
    )


def test_run_cross_platform_git_command_uses_windows_defaults(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The dispatcher should call Git directly on Windows with default options."""
    captured: dict[str, object] = {}

    def fake_run(
        command: list[str], **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="ok")

    monkeypatch.setattr(git_command, "_IS_WINDOWS", True)
    monkeypatch.setattr(git_command.subprocess, "run", fake_run)

    result = git_command.run_cross_platform_git_command(
        ["status", "--short"], cwd=tmp_path,
    )

    assert result.stdout == "ok"
    assert captured["command"] == [git_command._GIT_COMMAND_PREFIX, "status", "--short"]
    assert captured["cwd"] == tmp_path
    assert captured["check"] is True
    assert captured["capture_output"] is False
    assert captured["text"] is True
    assert captured["encoding"] is None
    assert captured["env"] is None


def test_run_cross_platform_git_command_uses_linux_shell_and_options(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The dispatcher should route Git through the cached Linux shell wrapper."""
    captured: dict[str, object] = {}
    options = git_command.GitCommandOptions(
        check=False,
        capture_output=True,
        encoding="utf-8",
        env={"GIT_TRACE": "1"},
    )

    def fake_run(
        command: list[str], **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="ok")

    monkeypatch.setattr(git_command, "_IS_WINDOWS", False)
    monkeypatch.setattr(
        git_command,
        "_build_linux_git_shell_command",
        _build_linux_status_command,
    )
    monkeypatch.setattr(git_command.subprocess, "run", fake_run)

    result = git_command.run_cross_platform_git_command(
        ["status", "--short"],
        cwd=tmp_path,
        options=options,
    )

    assert result.stdout == "ok"
    assert captured["command"] == [
        *git_command._GIT_LINUX_SHELL,
        "command git status --short",
    ]
    assert captured["cwd"] == tmp_path
    assert captured["check"] is False
    assert captured["capture_output"] is True
    assert captured["text"] is True
    assert captured["encoding"] == "utf-8"
    assert captured["env"] == {"GIT_TRACE": "1"}


# eof
