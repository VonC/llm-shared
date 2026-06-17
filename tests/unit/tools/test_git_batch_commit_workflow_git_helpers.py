"""Tests for split git batch commit Git helper branches.

Fix: Cover Git wrapper, path-check, and repository-state helpers from the
split `tools.git_batch_commit_git` module without keeping a large monolithic
workflow test file.

Fix: Cover the staged-file count, plan git-add count, and the staged-count
validation gate used by the root a.commit workflow.

Fix: Cover that the staged-file count passes `--no-renames` and counts a
staged rename as its two paths, matching a plan that adds both sides.
"""

from __future__ import annotations

import os
import subprocess
import sys
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


def _run_git_command_with_stdout(
    stdout: str,
) -> Callable[..., subprocess.CompletedProcess[str]]:
    def fake_run_git_command(
        args: list[str],
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
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


def _return_staged_count(count: int) -> Callable[[Path], int]:
    def fake_count_staged_files(_root: Path) -> int:
        return count

    return fake_count_staged_files


def _run_cross_platform_git_command_success(
    git_args: list[str],
    **_kwargs: object,
) -> subprocess.CompletedProcess[str]:
    return _completed_process(git_args)


class _DummyStream:
    def __init__(self, is_tty_value: object) -> None:
        self._is_tty = bool(is_tty_value)
        self.flush_calls = 0

    def isatty(self) -> bool:
        return self._is_tty

    def flush(self) -> None:
        self.flush_calls += 1


def _valid_block(path: str = "src/example.py") -> git_batch_models.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_models.CommitBlock(
        git_adds=[f"git add -A {path}"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


def test_build_git_trace_environment_sets_defaults_without_mutating_os_environ(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Trace-environment building should populate defaults on a copied mapping."""
    for key in ("GIT_TRACE", "GIT_TRACE_SETUP", "GIT_TRACE_PERFORMANCE"):
        monkeypatch.delenv(key, raising=False)

    env = git_batch_git._build_git_trace_environment()

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

    assert git_batch_git._has_interactive_console() is False


def test_is_worktree_clean_uses_git_status_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Worktree cleanliness should follow the trimmed output from `git status --short`."""
    monkeypatch.setattr(
        git_batch_git,
        "_run_git_command",
        _run_git_command_with_stdout(""),
    )
    assert git_batch_git._is_worktree_clean(tmp_path) is True

    monkeypatch.setattr(
        git_batch_git,
        "_run_git_command",
        _run_git_command_with_stdout(" M file.py\n"),
    )
    assert git_batch_git._is_worktree_clean(tmp_path) is False


def test_is_tracked_path_and_is_path_in_head_use_non_checking_git_calls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Tracked-path helpers should call Git with `check=False` and map return codes."""
    calls: list[tuple[list[str], git_batch_models._GitCommandOptions | None]] = []

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd
        calls.append((args, options))
        returncode = 0 if args[1] == "ls-files" else 1
        return _completed_process(args, returncode=returncode)

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)

    assert git_batch_git._is_tracked_path(tmp_path, "tracked.py") is True
    assert git_batch_git._is_path_in_head(tmp_path, "tracked.py") is False
    assert calls == [
        (
            ["git", "ls-files", "--error-unmatch", "--", "tracked.py"],
            git_batch_models._GitCommandOptions(check=False),
        ),
        (
            ["git", "cat-file", "-e", "HEAD:tracked.py"],
            git_batch_models._GitCommandOptions(check=False),
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
        git_batch_git,
        "_parse_git_add_command",
        _return_parsed_git_add_command(parts),
    )

    assert git_batch_git._extract_file_path("git add placeholder") == expected


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
        git_batch_git,
        "_extract_file_path",
        _extract_path_from_mapping(extracted_paths),
    )

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        captured_args.extend(args)
        return _completed_process(args, stdout="src/one.py\n")

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)

    assert git_batch_git._collect_git_add_paths(["cmd1", "cmd2", "cmd3"]) == [
        "src/one.py",
        "src/two.py",
    ]
    assert git_batch_git._block_has_staged_changes(["cmd1", "cmd2", "cmd3"], tmp_path) is True
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
        git_batch_git,
        "_extract_file_path",
        _extract_path_from_mapping(extracted_paths),
    )
    monkeypatch.setattr(git_batch_git, "_is_tracked_path", _return_false_for_file_path)
    monkeypatch.setattr(git_batch_git, "_is_path_in_head", _return_false_for_file_path)
    caplog.set_level("WARNING")

    assert git_batch_git._check_missing_files(["cmd1", "cmd2", "cmd3"], tmp_path) == [
        "missing.py",
    ]
    assert "File not found: missing.py" in caplog.text


def test_check_missing_files_ignores_git_pathspec_targets(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Git pathspec targets should not be treated as missing disk paths."""
    tracked_checks: list[str] = []
    head_checks: list[str] = []

    def fake_is_tracked_path(root: Path, file_path_str: str) -> bool:
        assert root == tmp_path
        tracked_checks.append(file_path_str)
        return False

    def fake_is_path_in_head(root: Path, file_path_str: str) -> bool:
        assert root == tmp_path
        head_checks.append(file_path_str)
        return False

    monkeypatch.setattr(git_batch_git, "_is_tracked_path", fake_is_tracked_path)
    monkeypatch.setattr(git_batch_git, "_is_path_in_head", fake_is_path_in_head)

    missing_files = git_batch_git._check_missing_files(
        ['git add -A ":(glob)src/**/test_job_restore_request_sidecar/**"'],
        tmp_path,
    )

    assert missing_files == []
    assert tracked_checks == []
    assert head_checks == []


def test_validate_missing_files_for_blocks_raises_grouped_details(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validation should group missing files by commit title in the raised message."""
    first_block = _valid_block("src/one.py")
    second_block = git_batch_models.CommitBlock(
        git_adds=["git add -A src/missing.py"],
        commit_message=first_block.commit_message,
        commit_title="fix(other): second",
    )

    def fake_check_missing_files(git_adds: list[str], root: Path) -> list[str]:
        del root
        return [] if git_adds == first_block.git_adds else ["src/missing.py"]

    monkeypatch.setattr(git_batch_git, "_check_missing_files", fake_check_missing_files)

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match=r"fix\(other\): second",
    ):
        git_batch_git._validate_missing_files_for_blocks([first_block, second_block], tmp_path)


def test_count_staged_files_counts_only_non_empty_lines(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Staged-file counting should ignore blank lines from `git diff --cached`."""
    monkeypatch.setattr(
        git_batch_git,
        "_run_git_command",
        _run_git_command_with_stdout("src/one.py\nsrc/two.py\n\n"),
    )

    expected_staged = 2
    assert git_batch_git._count_staged_files(tmp_path) == expected_staged


def test_count_staged_files_passes_no_renames_and_counts_both_sides(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Staged counting should ask git for `--no-renames` so a rename counts twice.

    A staged rename is two paths in the plan (old removed, new added), so the
    count must come from a diff that splits the rename instead of collapsing it.
    """
    captured_args: list[str] = []

    def fake_run_git_command(
        args: list[str],
        *,
        cwd: Path,
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        del cwd, options
        captured_args.extend(args)
        # git --no-renames reports a rename as the old and the new path.
        return _completed_process(args, stdout="bin/pw.bat\nbin/prompt_workflow.bat\n")

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)

    expected_staged = 2
    assert git_batch_git._count_staged_files(tmp_path) == expected_staged
    assert captured_args == [
        "git",
        "diff",
        "--cached",
        "--name-only",
        "--no-renames",
    ]


def test_count_plan_git_adds_sums_block_commands() -> None:
    """Plan counting should sum the git add commands across every block."""
    block_one = _valid_block("src/one.py")
    block_two = git_batch_models.CommitBlock(
        git_adds=["git add -A src/two.py", "git add -A src/three.py"],
        commit_message=block_one.commit_message,
        commit_title="fix(scope): second",
    )

    expected_plan_adds = 3
    assert git_batch_git._count_plan_git_adds([block_one, block_two]) == expected_plan_adds


def test_validate_staged_count_matches_git_adds_passes_when_counts_match(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validation should stay silent when the plan covers exactly the staged files."""
    blocks = [_valid_block("src/one.py")]
    monkeypatch.setattr(git_batch_git, "_count_staged_files", _return_staged_count(1))

    assert git_batch_git._validate_staged_count_matches_git_adds(blocks, tmp_path) is None


def test_validate_staged_count_matches_git_adds_raises_on_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Validation should fail when staged files outnumber the plan's git add commands."""
    blocks = [_valid_block("src/one.py")]
    monkeypatch.setattr(git_batch_git, "_count_staged_files", _return_staged_count(2))

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match=r"2 file\(s\) are staged",
    ):
        git_batch_git._validate_staged_count_matches_git_adds(blocks, tmp_path)


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
        options: git_batch_models._GitCommandOptions | None = None,
    ) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["cwd"] = cwd
        captured["options"] = options
        return _completed_process(args)

    monkeypatch.setattr(git_batch_git, "_run_git_command", fake_run_git_command)

    git_batch_git.git_reset(tmp_path)

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
        git_batch_git,
        "run_cross_platform_git_command",
        _run_cross_platform_git_command_success,
    )

    git_batch_git._run_git_command(
        ["git", "status"],
        cwd=tmp_path,
        options=git_batch_models._GitCommandOptions(capture_output=False),
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
        git_batch_git,
        "run_cross_platform_git_command",
        failing_run_cross_platform_git_command,
    )

    with pytest.raises(git_batch_models.GitOperationError, match="Git command failed"):
        git_batch_git._run_git_command(["git", "status"], cwd=tmp_path)


# eof
