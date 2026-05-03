"""Tests for git batch commit root-workflow branches.

Fix: Cover the `--root-a-commit` workflow result paths in a dedicated file so
the main workflow test file stays under the repository size limit.

Fix: Keep monkeypatched root-workflow helpers compatible with keyword-based
calls into `_read_and_parse_content()`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import git_batch_commit

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _valid_block() -> git_batch_commit.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_commit.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


def _empty_read_and_parse_content(
    root: Path,
    filename: str | None,
    interactive: object,
) -> list[git_batch_commit.CommitBlock]:
    del root, filename, interactive
    return []


def _return_commit_blocks(
    blocks: list[git_batch_commit.CommitBlock],
) -> Callable[[Path, str | None, object], list[git_batch_commit.CommitBlock]]:
    def fake_read_and_parse_content(
        root: Path,
        filename: str | None,
        interactive: object,
    ) -> list[git_batch_commit.CommitBlock]:
        del root, filename, interactive
        return blocks

    return fake_read_and_parse_content


def _noop_validate_missing_files(
    _blocks: list[git_batch_commit.CommitBlock],
    _root: Path,
) -> None:
    return None


def _return_false_for_root(_root: Path) -> bool:
    return False


def _return_process_all_commits(
    result: object,
) -> Callable[[list[git_batch_commit.CommitBlock], Path, object], bool]:
    def fake_process_all_commits(
        blocks: list[git_batch_commit.CommitBlock],
        root: Path,
        trace_git_commit: object = None,
    ) -> bool:
        del blocks, root, trace_git_commit
        return bool(result)

    return fake_process_all_commits


def test_run_root_a_commit_workflow_rejects_empty_plans(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The root workflow should fail when `a.commit` contains no valid blocks."""
    monkeypatch.setattr(
        git_batch_commit,
        "_read_and_parse_content",
        _empty_read_and_parse_content,
    )

    with pytest.raises(
        git_batch_commit.GitBatchCommitError,
        match="No valid commit blocks",
    ):
        git_batch_commit._run_root_a_commit_workflow(tmp_path)


@pytest.mark.parametrize("expected_exit", [0, 1])
def test_run_root_a_commit_workflow_runs_commit_phase_when_tree_is_dirty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    expected_exit: int,
) -> None:
    """The root workflow should validate first and then return the commit-phase result."""
    block = _valid_block()
    process_result = expected_exit == 0

    monkeypatch.setattr(
        git_batch_commit,
        "_read_and_parse_content",
        _return_commit_blocks([block]),
    )
    monkeypatch.setattr(
        git_batch_commit,
        "_validate_missing_files_for_blocks",
        _noop_validate_missing_files,
    )
    monkeypatch.setattr(git_batch_commit, "_is_worktree_clean", _return_false_for_root)
    monkeypatch.setattr(
        git_batch_commit,
        "_process_all_commits",
        _return_process_all_commits(process_result),
    )

    assert git_batch_commit._run_root_a_commit_workflow(tmp_path) == expected_exit


# eof
