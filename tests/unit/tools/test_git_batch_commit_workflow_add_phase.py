"""Tests for split git batch commit add-phase branches.

Fix: Cover add-phase prompting and git-add failure handling from the split
`tools.git_batch_commit_git` module without keeping a monolithic workflow test
file.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import git_batch_commit_git as git_batch_git
from tools import git_batch_commit_models as git_batch_models

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _completed_process(
    args: list[str],
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr=stderr)


def _return_parsed_git_add_command(
    parts: list[str] | None,
) -> Callable[[str], list[str] | None]:
    def fake_parse_git_add_command(_cmd: str) -> list[str] | None:
        return parts

    return fake_parse_git_add_command


def _return_prompt_outcome(
    outcome: git_batch_models._GitAddOutcome,
) -> Callable[[list[str], list[str]], git_batch_models._GitAddOutcome]:
    def fake_prompt_add_issues_action(
        _missing_files: list[str],
        _failed_adds: list[str],
    ) -> git_batch_models._GitAddOutcome:
        return outcome

    return fake_prompt_add_issues_action


def _return_string_list(
    values: list[str],
) -> Callable[[list[str], Path], list[str]]:
    def fake_string_list(_git_adds: list[str], _root: Path) -> list[str]:
        return values

    return fake_string_list


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (
            "confirm",
            git_batch_models._GitAddOutcome(
                should_continue=True,
                should_skip_commit=False,
            ),
        ),
        (
            "skip",
            git_batch_models._GitAddOutcome(
                should_continue=True,
                should_skip_commit=True,
            ),
        ),
        (
            "stop",
            git_batch_models._GitAddOutcome(
                should_continue=False,
                should_skip_commit=False,
            ),
        ),
    ],
)
def test_prompt_add_issues_action_returns_requested_outcome(
    monkeypatch: pytest.MonkeyPatch,
    response: str,
    expected: git_batch_models._GitAddOutcome,
) -> None:
    """Prompted add-phase actions should preserve confirm, skip, and stop separately."""

    def fake_input(_prompt: str) -> str:
        return response

    monkeypatch.setattr("builtins.input", fake_input)

    assert git_batch_git._prompt_add_issues_action(["missing.py"], ["git add -A bad.py"]) == expected


def test_execute_git_adds_collects_invalid_and_failed_commands(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Git-add execution should keep invalid commands and non-zero exits in the failure list."""
    parsed_commands = {
        "invalid": None,
        "failed": ["git", "add", "-A", "bad.py"],
        "ok": ["git", "add", "-A", "good.py"],
    }

    def fake_parse_git_add_command(cmd: str) -> list[str] | None:
        return parsed_commands[cmd]

    monkeypatch.setattr(git_batch_git, "_parse_git_add_command", fake_parse_git_add_command)

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        if args[-1] == "bad.py":
            return _completed_process(args, returncode=1, stderr="nope")
        return _completed_process(args)

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)
    caplog.set_level("WARNING")

    assert git_batch_git._execute_git_adds(["invalid", "failed", "ok"], tmp_path) == [
        "invalid",
        "failed",
    ]
    assert "git add failed (failed): nope" in caplog.text


def test_execute_git_adds_logs_commands_without_stderr_text(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Git-add failures without stderr should still log the plain command warning."""
    monkeypatch.setattr(
        git_batch_git,
        "_parse_git_add_command",
        _return_parsed_git_add_command(["git", "add", "-A", "plain.py"]),
    )

    def fake_run_git_command(
        args: list[str],
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        return _completed_process(args, returncode=1)

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)
    caplog.set_level("WARNING")

    assert git_batch_git._execute_git_adds(["plain"], tmp_path) == ["plain"]
    assert "git add failed: plain" in caplog.text


def test_git_add_files_returns_prompt_outcome_and_clean_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Add-phase execution should return the prompt outcome or a clean success result."""
    prompt_outcome = git_batch_models._GitAddOutcome(
        should_continue=False,
        should_skip_commit=False,
    )
    monkeypatch.setattr(
        git_batch_git,
        "_check_missing_files",
        _return_string_list(["missing.py"]),
    )
    monkeypatch.setattr(git_batch_git, "_execute_git_adds", _return_string_list([]))
    monkeypatch.setattr(
        git_batch_git,
        "_prompt_add_issues_action",
        _return_prompt_outcome(prompt_outcome),
    )

    assert git_batch_git.git_add_files(["git add -A missing.py"], tmp_path) == prompt_outcome

    monkeypatch.setattr(git_batch_git, "_check_missing_files", _return_string_list([]))
    monkeypatch.setattr(git_batch_git, "_execute_git_adds", _return_string_list([]))

    assert git_batch_git.git_add_files(["git add -A ok.py"], tmp_path) == git_batch_models._GitAddOutcome(
        should_continue=True,
        should_skip_commit=False,
    )


# eof
