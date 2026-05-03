"""Tests for grouped-commit prompt helper branches and script entry points.

Fix: Cover logging setup, Git and clipboard wrappers, empty staged input,
fatal-exit handling, and `__main__` execution in
`tools.group_commit_message_prompt`.

Fix: Cover staged porcelain filtering when a line should be kept and trimmed.
"""

from __future__ import annotations

import logging
import runpy
import shutil
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest

from tools import group_commit_message_prompt

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

_FATAL_EXIT_CODE = 2


def _which_git(_name: str) -> str:
    return "git"


def _which_pwsh(_name: str) -> str:
    return "pwsh"


def _which_powershell(_name: str) -> str:
    return "powershell"


def _which_identity(name: str) -> str:
    return name


def test_build_group_commit_prompt_returns_empty_log_when_no_files() -> None:
    """The grouped prompt should still emit an empty fenced log block."""
    assert group_commit_message_prompt.build_group_commit_prompt(0, []) == (
        "/group-commits-msg for those 0 files:\n\n```log\n```\n\nContext: "
    )


def test_filter_staged_porcelain_lines_keeps_only_real_staged_entries() -> None:
    """Porcelain filtering should keep staged lines and trim their trailing spaces."""
    status_text = (
        "\n M unstaged.py\n?? untracked.py\nM  staged.py\nA  added.py  "
    )

    assert group_commit_message_prompt._filter_staged_porcelain_lines(status_text) == [
        "M  staged.py",
        "A  added.py",
    ]


def test_configure_logging_resets_root_logger() -> None:
    """Logging setup should replace handlers and switch the root level."""
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level

    try:
        root_logger.addHandler(logging.StreamHandler(sys.stderr))
        group_commit_message_prompt._configure_logging(debug=True)

        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) == 1
        assert getattr(root_logger.handlers[0], "stream", None) is sys.stdout
    finally:
        root_logger.handlers.clear()
        for handler in original_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(original_level)


def test_run_git_text_returns_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The Git text helper should return stdout from a successful command."""
    captured: dict[str, object] = {}

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="diff output")

    monkeypatch.setattr(shutil, "which", _which_git)
    monkeypatch.setattr(group_commit_message_prompt.subprocess, "run", fake_run)

    assert group_commit_message_prompt._run_git_text(
        ["diff", "--cached"],
        cwd=tmp_path,
    ) == ("diff output")
    assert captured["command"] == ["git", "diff", "--cached"]
    assert captured["cwd"] == tmp_path
    assert captured["check"] is True


def test_run_git_text_wraps_called_process_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Git wrapper errors should include stderr text when it is available."""

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command, stderr="boom")

    monkeypatch.setattr(shutil, "which", _which_git)
    monkeypatch.setattr(group_commit_message_prompt.subprocess, "run", fake_run)

    with pytest.raises(group_commit_message_prompt.GitCommandError, match="boom"):
        group_commit_message_prompt._run_git_text(
            ["status", "--porcelain"],
            cwd=tmp_path,
        )


def test_set_clipboard_text_uses_powershell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clipboard writes should go through PowerShell with the given text input."""
    captured: dict[str, object] = {}

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="")

    monkeypatch.setattr(shutil, "which", _which_pwsh)
    monkeypatch.setattr(group_commit_message_prompt.subprocess, "run", fake_run)

    group_commit_message_prompt._set_clipboard_text("clipboard text")

    captured_command = cast("list[str]", captured["command"])
    assert captured_command[0] == "pwsh"
    assert captured["input"] == "clipboard text"
    assert captured["check"] is True


def test_set_clipboard_text_wraps_subprocess_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clipboard wrapper errors should be converted into `ClipboardError`."""

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(shutil, "which", _which_powershell)
    monkeypatch.setattr(group_commit_message_prompt.subprocess, "run", fake_run)

    with pytest.raises(
        group_commit_message_prompt.ClipboardError,
        match="Failed to write clipboard",
    ):
        group_commit_message_prompt._set_clipboard_text("clipboard text")


def test_group_commit_message_prompt_script_runs_as_main(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Running the script as `__main__` should build artifacts and exit with code 0."""
    diff_text = "diff --git a/one.py b/one.py\n"
    status_text = "M  src/one.py\n"
    script_path = Path(group_commit_message_prompt.__file__)

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        if command[0] == "git" and command[1:] == ["diff", "--cached"]:
            return subprocess.CompletedProcess(command, 0, stdout=diff_text)
        if command[0] == "git" and command[1:] == ["status", "--porcelain"]:
            return subprocess.CompletedProcess(command, 0, stdout=status_text)
        if command[0] in {"pwsh", "powershell"}:
            return subprocess.CompletedProcess(command, 0, stdout="")
        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(shutil, "which", _which_identity)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", [str(script_path), "--root", str(tmp_path)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(script_path), run_name="__main__")

    assert excinfo.value.code == 0
    assert (tmp_path / "a.diff").read_text(encoding="utf-8") == diff_text
    assert (tmp_path / "a.commit").read_text(encoding="utf-8") == ""


def test_group_commit_message_prompt_script_logs_fatal_on_git_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Script execution should convert grouped-prompt failures into exit code 2."""
    script_path = Path(group_commit_message_prompt.__file__)

    def fake_run(
        command: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        if command[0] == "git" and command[1:] == ["diff", "--cached"]:
            raise subprocess.CalledProcessError(1, command, stderr="bad diff")
        msg = f"Unexpected command: {command}"
        raise AssertionError(msg)

    monkeypatch.setattr(shutil, "which", _which_identity)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(sys, "argv", [str(script_path), "--root", str(tmp_path)])

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(script_path), run_name="__main__")

    assert excinfo.value.code == _FATAL_EXIT_CODE


# eof
