"""Tests for the git batch commit helper-backed command dispatch.

Fix: Verify the tool routes parsed Git commands through the shared cached
cross-platform helper instead of spawning plain `git` directly.

Fix: Verify commit commands use live Git output, reject detached consoles, and
optionally pass a trace environment for post-commit diagnostics.

Fix: Verify root a.commit replay fails early on a clean tree, commit blocks skip
clean path sets instead of calling `git commit`, and interactive stop paths
return a non-zero CLI result.

Fix: Import the shared Git helper types through the `tools` package so test
imports stay consistent with the repository package layout.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools import git_batch_commit
from tools.git_command import GitCommandOptions

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


def test_run_git_command_strips_leading_git_before_helper_dispatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The local wrapper should pass only Git subcommand arguments to the helper."""
    captured_git_args: list[str] = []
    captured_kwargs: dict[str, object] = {}

    def fake_run(
        git_args: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured_git_args.extend(git_args)
        captured_kwargs.update(kwargs)
        return subprocess.CompletedProcess(git_args, 0, stdout="ok")

    monkeypatch.setattr(git_batch_commit, "run_cross_platform_git_command", fake_run)

    result = git_batch_commit._run_git_command(
        ["git", "commit", "-m", "message"],
        cwd=tmp_path,
        options=git_batch_commit._GitCommandOptions(check=False),
    )

    assert result.stdout == "ok"
    assert captured_git_args == ["commit", "-m", "message"]
    assert captured_kwargs == {
        "cwd": tmp_path,
        "options": GitCommandOptions(
            capture_output=True,
            check=False,
            env=None,
        ),
    }


def test_run_git_command_rejects_non_git_commands(tmp_path: Path) -> None:
    """The wrapper should fail fast when a parsed command does not start with git."""
    with pytest.raises(git_batch_commit.GitOperationError):
        git_batch_commit._run_git_command(["python", "-V"], cwd=tmp_path)


def test_run_git_command_rejects_missing_console_for_interactive_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Interactive Git commands should fail fast without a real console."""
    monkeypatch.setattr(git_batch_commit, "_has_interactive_console", lambda: False)

    with pytest.raises(
        git_batch_commit.GitOperationError,
        match="interactive console",
    ):
        git_batch_commit._run_git_command(
            ["git", "commit", "-m", "message"],
            cwd=tmp_path,
            options=git_batch_commit._GitCommandOptions(
                capture_output=False,
                require_tty=True,
            ),
        )


def test_run_git_command_adds_trace_environment_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Tracing should be added only for the Git command that requests it."""
    captured_kwargs: dict[str, object] = {}

    def fake_run(
        git_args: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured_kwargs.update(kwargs)
        return subprocess.CompletedProcess(git_args, 0, stdout="ok")

    monkeypatch.setattr(git_batch_commit, "run_cross_platform_git_command", fake_run)
    monkeypatch.setattr(
        git_batch_commit,
        "_build_git_trace_environment",
        lambda: {"GIT_TRACE": "1"},
    )

    git_batch_commit._run_git_command(
        ["git", "commit", "-m", "message"],
        cwd=tmp_path,
        options=git_batch_commit._GitCommandOptions(trace_git=True),
    )

    assert captured_kwargs["options"] == GitCommandOptions(
        capture_output=True,
        check=True,
        env={"GIT_TRACE": "1"},
    )


def test_git_commit_uses_live_output_and_trace_toggle(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """git_commit should stream Git output live and pass the trace toggle through."""
    captured_args: list[str] = []
    captured_kwargs: dict[str, object] = {}

    def fake_run_git_command(
        args: list[str],
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        captured_args.extend(args)
        captured_kwargs.update(kwargs)
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(git_batch_commit, "_run_git_command", fake_run_git_command)

    git_batch_commit.git_commit(
        "message body",
        "title",
        tmp_path,
        trace_git_commit=True,
    )

    assert captured_args == ["git", "commit", "-m", "message body"]
    assert captured_kwargs["cwd"] == tmp_path
    assert captured_kwargs["options"] == git_batch_commit._GitCommandOptions(
        capture_output=False,
        require_tty=True,
        trace_git=True,
    )


def test_run_root_a_commit_workflow_rejects_clean_tree_before_commit_phase(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The root a.commit workflow should fail early when there is nothing left to replay."""
    block = git_batch_commit.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message="refactor(example): title\n\nWhy:\n\nreason\n\nmore reason\n\nWhat:\n\n- change",
        commit_title="refactor(example): title",
    )
    validation_calls: list[str] = []

    def fake_read_and_parse_content(
        root: Path,
        *,
        filename: str | None,
        interactive: bool,
    ) -> list[git_batch_commit.CommitBlock]:
        assert root == tmp_path
        assert filename == "a.commit"
        assert interactive is False
        return [block]

    def fake_validate_missing_files_for_blocks(
        blocks: list[git_batch_commit.CommitBlock],
        root: Path,
    ) -> None:
        assert blocks == [block]
        assert root == tmp_path
        validation_calls.append("validated")

    def fake_is_worktree_clean(root: Path) -> bool:
        assert root == tmp_path
        return True

    def fail_process_all_commits(
        blocks: list[git_batch_commit.CommitBlock],
        root: Path,
        *,
        trace_git_commit: bool = False,
    ) -> bool:
        assert blocks == [block]
        assert root == tmp_path
        assert trace_git_commit is False
        return pytest.fail("commit phase should not run")

    monkeypatch.setattr(
        git_batch_commit,
        "_read_and_parse_content",
        fake_read_and_parse_content,
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_validate_missing_files_for_blocks",
        fake_validate_missing_files_for_blocks,
    )
    monkeypatch.setattr(git_batch_commit, "_is_worktree_clean", fake_is_worktree_clean)
    monkeypatch.setattr(
        git_batch_commit,
        "_process_all_commits",
        fail_process_all_commits,
    )

    with pytest.raises(
        git_batch_commit.GitBatchCommitError,
        match="working tree is clean",
    ):
        git_batch_commit._run_root_a_commit_workflow(tmp_path)

    assert validation_calls == ["validated"]


def test_process_commit_block_skips_when_group_has_no_staged_diff(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A clean group should be skipped with a clear already-applied message."""
    block = git_batch_commit.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message="refactor(example): title",
        commit_title="refactor(example): title",
    )

    def fake_git_add_files(git_adds: list[str], root: Path) -> bool:
        assert git_adds == block.git_adds
        assert root == tmp_path
        return True

    def fake_block_has_staged_changes(git_adds: list[str], root: Path) -> bool:
        assert git_adds == block.git_adds
        assert root == tmp_path
        return False

    def fail_git_commit(
        commit_message: str,
        commit_title: str,
        root: Path,
        *,
        trace_git_commit: bool = False,
    ) -> None:
        assert commit_message == block.commit_message
        assert commit_title == block.commit_title
        assert root == tmp_path
        assert trace_git_commit is False
        pytest.fail("git_commit should not be called")

    monkeypatch.setattr(git_batch_commit, "git_add_files", fake_git_add_files)
    monkeypatch.setattr(
        git_batch_commit,
        "_block_has_staged_changes",
        fake_block_has_staged_changes,
    )
    monkeypatch.setattr(
        git_batch_commit,
        "git_commit",
        fail_git_commit,
    )

    caplog.set_level("WARNING")

    should_continue = git_batch_commit._process_commit_block(
        block,
        1,
        3,
        tmp_path,
    )

    assert should_continue is True
    assert "already applied or the tree is clean" in caplog.text


def test_process_all_commits_returns_false_when_user_stops_after_git_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Stopping after a Git operation failure should report an unsuccessful run."""
    block = git_batch_commit.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message="refactor(example): title",
        commit_title="refactor(example): title",
    )

    def fake_git_reset(root: Path) -> None:
        assert root == tmp_path

    monkeypatch.setattr(git_batch_commit, "git_reset", fake_git_reset)

    def fake_process_commit_block(
        block_arg: git_batch_commit.CommitBlock,
        index: int,
        total: int,
        root: Path,
        *,
        trace_git_commit: bool = False,
    ) -> bool:
        assert block_arg == block
        assert index == 1
        assert total == 1
        assert root == tmp_path
        assert trace_git_commit is False
        msg = "boom"
        raise git_batch_commit.GitOperationError(msg)

    def fake_input(prompt: str) -> str:
        assert prompt == "\nContinue with next commit or stop? [continue/stop]: "
        return "stop"

    monkeypatch.setattr(
        git_batch_commit,
        "_process_commit_block",
        fake_process_commit_block,
    )
    monkeypatch.setattr("builtins.input", fake_input)

    assert git_batch_commit._process_all_commits([block], tmp_path) is False


def test_main_returns_non_zero_when_commit_processing_stops(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The CLI should return a failing exit code when commit processing aborts."""
    block = git_batch_commit.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message="refactor(example): title",
        commit_title="refactor(example): title",
    )

    def fake_find_project_root(start: Path) -> Path:
        assert start == Path.cwd()
        return tmp_path

    def fake_read_and_parse_content(
        root: Path,
        *,
        filename: str | None,
        interactive: bool,
    ) -> list[git_batch_commit.CommitBlock]:
        assert root == tmp_path
        assert filename == "commit-plan.txt"
        assert interactive is True
        return [block]

    def fake_process_all_commits(
        blocks: list[git_batch_commit.CommitBlock],
        root: Path,
        *,
        trace_git_commit: bool = False,
    ) -> bool:
        assert blocks == [block]
        assert root == tmp_path
        assert trace_git_commit is False
        return False

    monkeypatch.setattr(git_batch_commit, "find_project_root", fake_find_project_root)
    monkeypatch.setattr(
        git_batch_commit,
        "_read_and_parse_content",
        fake_read_and_parse_content,
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_process_all_commits",
        fake_process_all_commits,
    )

    assert git_batch_commit.main(["commit-plan.txt"]) == 1


# eof
