"""Tests for git batch commit workflow and Git-operation branches.

Fix: Cover Git helper wrappers, add-phase outcomes, workflow control flow,
and CLI branches in `tools.git_batch_commit`.

Fix: Keep monkeypatched Git-command helpers compatible with keyword-based
`cwd=` and `options=` calls.
"""

from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

import pytest

from tools import git_batch_commit

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


def _valid_block(path: str = "src/example.py") -> git_batch_commit.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_commit.CommitBlock(
        git_adds=[f"git add -A {path}"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


class _DummyStream:
    def __init__(self, is_tty_value: object) -> None:
        self._is_tty = bool(is_tty_value)
        self.flush_calls = 0

    def isatty(self) -> bool:
        return self._is_tty

    def flush(self) -> None:
        self.flush_calls += 1


def _run_git_command_with_stdout(
    stdout: str,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    def fake_run_git_command(
        args: list[str],
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        return _completed_process(args, stdout=stdout)

    return fake_run_git_command


def _return_parsed_git_add_command(
    parts: list[str] | None,
) -> Callable[[str], list[str] | None]:
    def fake_parse_git_add_command(_cmd: str) -> list[str] | None:
        return parts

    return fake_parse_git_add_command


def _extract_path_from_mapping(
    extracted_paths: dict[str, str | None],
) -> Callable[[str], str | None]:
    def fake_extract_file_path(cmd: str) -> str | None:
        return extracted_paths[cmd]

    return fake_extract_file_path


def _return_false_for_file_path(_root: Path, _file_path_str: str) -> bool:
    return False


def _return_prompt_outcome(
    outcome: git_batch_commit._GitAddOutcome,
) -> Callable[[list[str], list[str]], git_batch_commit._GitAddOutcome]:
    def fake_prompt_add_issues_action(
        _missing_files: list[str],
        _failed_adds: list[str],
    ) -> git_batch_commit._GitAddOutcome:
        return outcome

    return fake_prompt_add_issues_action


def _return_string_list(
    values: list[str],
) -> Callable[[list[str], Path], list[str]]:
    def fake_string_list(_git_adds: list[str], _root: Path) -> list[str]:
        return values

    return fake_string_list


def _noop_git_reset(_root: Path) -> None:
    return None


def _return_false_process_commit_block(
    _block_arg: git_batch_commit.CommitBlock,
    _index: int,
    _total: int,
    _root: Path,
    trace_git_commit: object = None,
) -> bool:
    del trace_git_commit
    return False


def _return_true_process_commit_block(
    _block_arg: git_batch_commit.CommitBlock,
    _index: int,
    _total: int,
    _root: Path,
    trace_git_commit: object = None,
) -> bool:
    del trace_git_commit
    return True


def _return_git_add_outcome(
    outcome: git_batch_commit._GitAddOutcome,
) -> Callable[[list[str], Path], git_batch_commit._GitAddOutcome]:
    def fake_git_add_files(
        _git_adds: list[str],
        _root: Path,
    ) -> git_batch_commit._GitAddOutcome:
        return outcome

    return fake_git_add_files


def _raise_unexpected_diff_check(_git_adds: list[str], _root: Path) -> bool:
    msg = "unexpected diff check"
    raise AssertionError(msg)


def _return_true_staged_changes(_git_adds: list[str], _root: Path) -> bool:
    return True


def _run_cross_platform_git_command_success(
    git_args: list[str],
    **_kwargs: object,
) -> subprocess.CompletedProcess[str]:
    return _completed_process(git_args)


def test_build_git_trace_environment_sets_defaults_without_mutating_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Trace-environment building should populate defaults on a copied mapping."""
    for key in ("GIT_TRACE", "GIT_TRACE_SETUP", "GIT_TRACE_PERFORMANCE"):
        monkeypatch.delenv(key, raising=False)

    env = git_batch_commit._build_git_trace_environment()

    assert env["GIT_TRACE"] == "1"
    assert env["GIT_TRACE_SETUP"] == "1"
    assert env["GIT_TRACE_PERFORMANCE"] == "1"
    assert os.environ.get("GIT_TRACE") is None


def test_has_interactive_console_reflects_stream_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Interactive-console detection should require stdin, stdout, and stderr to be TTYs."""
    monkeypatch.setattr(sys, "stdin", _DummyStream(is_tty_value=True))
    monkeypatch.setattr(sys, "stdout", _DummyStream(is_tty_value=True))
    monkeypatch.setattr(sys, "stderr", _DummyStream(is_tty_value=False))

    assert git_batch_commit._has_interactive_console() is False


def test_is_worktree_clean_uses_git_status_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Worktree cleanliness should follow the trimmed output from `git status --short`."""
    monkeypatch.setattr(
        git_batch_commit,
        "_run_git_command",
        _run_git_command_with_stdout(""),
    )
    assert git_batch_commit._is_worktree_clean(tmp_path) is True

    monkeypatch.setattr(
        git_batch_commit,
        "_run_git_command",
        _run_git_command_with_stdout(" M file.py\n"),
    )
    assert git_batch_commit._is_worktree_clean(tmp_path) is False


def test_is_tracked_path_and_is_path_in_head_use_non_checking_git_calls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Tracked-path helpers should call Git with `check=False` and map return codes."""
    calls: list[tuple[list[str], git_batch_commit._GitCommandOptions | None]] = []

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd
        calls.append((args, options))
        returncode = 0 if args[1] == "ls-files" else 1
        return _completed_process(args, returncode=returncode)

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)

    assert git_batch_commit._is_tracked_path(tmp_path, "tracked.py") is True
    assert git_batch_commit._is_path_in_head(tmp_path, "tracked.py") is False
    assert calls == [
        (
            ["git", "ls-files", "--error-unmatch", "--", "tracked.py"],
            git_batch_commit._GitCommandOptions(check=False),
        ),
        (
            ["git", "cat-file", "-e", "HEAD:tracked.py"],
            git_batch_commit._GitCommandOptions(check=False),
        ),
    ]


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        (None, None),
        (["git", "add"], None),
        (["git", "add", "-A", "--", "folder/file.py"], "folder/file.py"),
        (["git", "add", "-A", "--"], None),
        (["git", "add", "-A"], None),
    ],
)
def test_extract_file_path_handles_none_empty_and_separator_variants(
    monkeypatch: pytest.MonkeyPatch,
    parts: list[str] | None,
    expected: str | None,
) -> None:
    """Path extraction should cope with invalid parses, options, and `--` separators."""
    monkeypatch.setattr(
        git_batch_commit,
        "_parse_git_add_command",
        _return_parsed_git_add_command(parts),
    )

    assert git_batch_commit._extract_file_path("git add placeholder") == expected


def test_collect_git_add_paths_and_block_has_staged_changes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Path collection should ignore None values and feed the staged-diff check."""
    extracted_paths = {
        "cmd1": "src/one.py",
        "cmd2": None,
        "cmd3": "src/two.py",
    }
    captured_args: list[str] = []

    monkeypatch.setattr(
        git_batch_commit,
        "_extract_file_path",
        _extract_path_from_mapping(extracted_paths),
    )

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        captured_args.extend(args)
        return _completed_process(args, stdout="src/one.py\n")

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)

    assert git_batch_commit._collect_git_add_paths(["cmd1", "cmd2", "cmd3"]) == [
        "src/one.py",
        "src/two.py",
    ]
    assert (
        git_batch_commit._block_has_staged_changes(["cmd1", "cmd2", "cmd3"], tmp_path)
        is True
    )
    assert captured_args == [
        "git",
        "diff",
        "--cached",
        "--name-only",
        "--",
        "src/one.py",
        "src/two.py",
    ]


def test_check_missing_files_handles_none_existing_and_missing_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Missing-file checks should skip None entries and report real missing paths."""
    existing_file = tmp_path / "present.py"
    existing_file.write_text("print('ok')\n", encoding="utf-8")
    extracted_paths = {
        "cmd1": None,
        "cmd2": "present.py",
        "cmd3": "missing.py",
    }

    monkeypatch.setattr(
        git_batch_commit,
        "_extract_file_path",
        _extract_path_from_mapping(extracted_paths),
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_is_tracked_path",
        _return_false_for_file_path,
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_is_path_in_head",
        _return_false_for_file_path,
    )
    caplog.set_level("WARNING")

    assert git_batch_commit._check_missing_files(
        ["cmd1", "cmd2", "cmd3"],
        tmp_path,
    ) == [
        "missing.py",
    ]
    assert "File not found: missing.py" in caplog.text


def test_validate_missing_files_for_blocks_raises_grouped_details(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validation should group missing files by commit title in the raised message."""
    first_block = _valid_block("src/one.py")
    second_block = git_batch_commit.CommitBlock(
        git_adds=["git add -A src/missing.py"],
        commit_message=first_block.commit_message,
        commit_title="fix(other): second",
    )

    def fake_check_missing_files(git_adds: list[str], root: Path) -> list[str]:
        del root
        return [] if git_adds == first_block.git_adds else ["src/missing.py"]

    monkeypatch.setattr(
        git_batch_commit,
        "_check_missing_files",
        fake_check_missing_files,
    )

    with pytest.raises(
        git_batch_commit.GitBatchCommitError,
        match=r"fix\(other\): second",
    ):
        git_batch_commit._validate_missing_files_for_blocks(
            [first_block, second_block],
            tmp_path,
        )


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        (
            "confirm",
            git_batch_commit._GitAddOutcome(
                should_continue=True,
                should_skip_commit=False,
            ),
        ),
        (
            "skip",
            git_batch_commit._GitAddOutcome(
                should_continue=True,
                should_skip_commit=True,
            ),
        ),
        (
            "stop",
            git_batch_commit._GitAddOutcome(
                should_continue=False,
                should_skip_commit=False,
            ),
        ),
    ],
)
def test_prompt_add_issues_action_returns_requested_outcome(
    monkeypatch: pytest.MonkeyPatch,
    response: str,
    expected: git_batch_commit._GitAddOutcome,
) -> None:
    """Prompted add-phase actions should preserve confirm, skip, and stop separately."""

    def fake_input(_prompt: str) -> str:
        return response

    monkeypatch.setattr("builtins.input", fake_input)

    assert (
        git_batch_commit._prompt_add_issues_action(
            ["missing.py"],
            ["git add -A bad.py"],
        )
        == expected
    )


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

    monkeypatch.setattr(
        git_batch_commit,
        "_parse_git_add_command",
        fake_parse_git_add_command,
    )

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        if args[-1] == "bad.py":
            return _completed_process(args, returncode=1, stderr="nope")
        return _completed_process(args)

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)
    caplog.set_level("WARNING")

    assert git_batch_commit._execute_git_adds(
        ["invalid", "failed", "ok"],
        tmp_path,
    ) == [
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
        git_batch_commit,
        "_parse_git_add_command",
        _return_parsed_git_add_command(["git", "add", "-A", "plain.py"]),
    )

    def fake_run_git_command(
        args: list[str],
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        return _completed_process(args, returncode=1)

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)
    caplog.set_level("WARNING")

    assert git_batch_commit._execute_git_adds(["plain"], tmp_path) == ["plain"]
    assert "git add failed: plain" in caplog.text


def test_git_add_files_returns_prompt_outcome_and_clean_success(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Add-phase execution should return the prompt outcome or a clean success result."""
    prompt_outcome = git_batch_commit._GitAddOutcome(
        should_continue=False,
        should_skip_commit=False,
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_check_missing_files",
        _return_string_list(["missing.py"]),
    )
    monkeypatch.setattr(git_batch_commit, "_execute_git_adds", _return_string_list([]))
    monkeypatch.setattr(
        git_batch_commit,
        "_prompt_add_issues_action",
        _return_prompt_outcome(prompt_outcome),
    )

    assert (
        git_batch_commit.git_add_files(["git add -A missing.py"], tmp_path)
        == prompt_outcome
    )

    monkeypatch.setattr(
        git_batch_commit,
        "_check_missing_files",
        _return_string_list([]),
    )
    monkeypatch.setattr(git_batch_commit, "_execute_git_adds", _return_string_list([]))

    assert git_batch_commit.git_add_files(
        ["git add -A ok.py"],
        tmp_path,
    ) == git_batch_commit._GitAddOutcome(
        should_continue=True,
        should_skip_commit=False,
    )


def test_git_reset_runs_plain_git_reset(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Resetting should invoke `git reset` in the repository root."""
    captured: dict[str, object] = {}

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_commit._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["cwd"] = cwd
        captured["options"] = options
        return _completed_process(args)

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)

    git_batch_commit.git_reset(tmp_path)

    assert captured == {"args": ["git", "reset"], "cwd": tmp_path, "options": None}


def test_run_git_command_flushes_live_output_and_wraps_subprocess_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Live Git commands should flush stdio, and subprocess errors should be wrapped."""
    stdout_stream = _DummyStream(is_tty_value=True)
    stderr_stream = _DummyStream(is_tty_value=True)
    monkeypatch.setattr(sys, "stdout", stdout_stream)
    monkeypatch.setattr(sys, "stderr", stderr_stream)
    monkeypatch.setattr(
        git_batch_commit,
        "run_cross_platform_git_command",
        _run_cross_platform_git_command_success,
    )

    git_batch_commit._run_git_command(
        ["git", "status"],
        cwd=tmp_path,
        options=git_batch_commit._GitCommandOptions(capture_output=False),
    )

    assert stdout_stream.flush_calls == 1
    assert stderr_stream.flush_calls == 1

    def failing_run_cross_platform_git_command(
        git_args: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.CalledProcessError(1, git_args)

    monkeypatch.setattr(
        git_batch_commit,
        "run_cross_platform_git_command",
        failing_run_cross_platform_git_command,
    )

    with pytest.raises(git_batch_commit.GitOperationError, match="Git command failed"):
        git_batch_commit._run_git_command(["git", "status"], cwd=tmp_path)


def test_process_commit_block_skips_when_add_phase_requests_skip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A skip result from the add phase should skip the commit without diff checks."""
    block = _valid_block()
    monkeypatch.setattr(
        git_batch_commit,
        "git_add_files",
        _return_git_add_outcome(
            git_batch_commit._GitAddOutcome(
                should_continue=True,
                should_skip_commit=True,
            ),
        ),
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_block_has_staged_changes",
        _raise_unexpected_diff_check,
    )
    caplog.set_level("WARNING")

    assert git_batch_commit._process_commit_block(block, 1, 1, tmp_path) is True
    assert "Skipping commit 1." in caplog.text


def test_process_commit_block_commits_when_staged_changes_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A commit block with staged changes should call `git_commit` and continue."""
    block = _valid_block()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        git_batch_commit,
        "git_add_files",
        _return_git_add_outcome(
            git_batch_commit._GitAddOutcome(
                should_continue=True,
                should_skip_commit=False,
            ),
        ),
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_block_has_staged_changes",
        _return_true_staged_changes,
    )

    def fake_git_commit(
        commit_message: str,
        commit_title: str,
        root: Path,
        *,
        trace_git_commit: bool = False,
    ) -> None:
        captured["commit_message"] = commit_message
        captured["commit_title"] = commit_title
        captured["root"] = root
        captured["trace_git_commit"] = trace_git_commit

    monkeypatch.setattr(git_batch_commit, "git_commit", fake_git_commit)

    assert (
        git_batch_commit._process_commit_block(
            block,
            1,
            1,
            tmp_path,
            trace_git_commit=True,
        )
        is True
    )
    assert captured == {
        "commit_message": block.commit_message,
        "commit_title": block.commit_title,
        "root": tmp_path,
        "trace_git_commit": True,
    }


def test_process_all_commits_stops_when_commit_block_requests_stop(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Commit processing should return False when a block asks the batch to stop."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_commit, "git_reset", _noop_git_reset)
    monkeypatch.setattr(
        git_batch_commit,
        "_process_commit_block",
        _return_false_process_commit_block,
    )

    assert git_batch_commit._process_all_commits([block], tmp_path) is False


def test_process_all_commits_logs_success_when_all_blocks_complete(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Successful commit processing should log the final success banner."""
    block = _valid_block()
    monkeypatch.setattr(git_batch_commit, "git_reset", _noop_git_reset)
    monkeypatch.setattr(
        git_batch_commit,
        "_process_commit_block",
        _return_true_process_commit_block,
    )
    caplog.set_level("INFO")

    assert git_batch_commit._process_all_commits([block], tmp_path) is True
    assert "All commits processed successfully" in caplog.text


# eof
