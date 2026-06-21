"""Tests for split git batch commit root-workflow branches.

Fix: Cover the `--root-a-commit` workflow result paths in a dedicated file so
the main workflow test file stays under the repository size limit.

Fix: Keep monkeypatched root-workflow helpers compatible with keyword-based
calls into `_read_and_parse_content()`.

Fix: Cover the staged-count validation gate and the a.commit emptying that runs
after every block has been committed in the root workflow.

Fix: Cover that the root workflow forwards its interactive flag to the commit
loop, so `--non-interactive --root-a-commit` runs without prompting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import git_batch_commit_models as git_batch_models
from tools import git_batch_commit_workflow as git_batch_workflow

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def _valid_block() -> git_batch_models.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_models.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


def _empty_read_and_parse_content(
    root: Path,
    filename: str | None,
    interactive: object,
) -> list[git_batch_models.CommitBlock]:
    del root, filename, interactive
    return []


def _return_commit_blocks(
    blocks: list[git_batch_models.CommitBlock],
) -> Callable[[Path, str | None, object], list[git_batch_models.CommitBlock]]:
    def fake_read_and_parse_content(
        root: Path,
        filename: str | None,
        interactive: object,
    ) -> list[git_batch_models.CommitBlock]:
        del root, filename, interactive
        return blocks

    return fake_read_and_parse_content


def _noop_validate_missing_files(
    _blocks: list[git_batch_models.CommitBlock],
    _root: Path,
) -> None:
    return None


def _noop_validate_staged_count(
    _blocks: list[git_batch_models.CommitBlock],
    _root: Path,
) -> None:
    return None


def _raise_staged_count_mismatch(
    _blocks: list[git_batch_models.CommitBlock],
    _root: Path,
) -> None:
    msg = (
        "Validation failed: the commit plan lists 1 'git add' command(s) "
        "but 2 file(s) are staged."
    )
    raise git_batch_models.GitBatchCommitError(msg)


def _return_false_for_root(_root: Path) -> bool:
    return False


def _return_process_all_commits(
    result: object,
) -> Callable[..., bool]:
    def fake_process_all_commits(
        blocks: list[git_batch_models.CommitBlock],
        root: Path,
        *,
        interactive: object = True,
        trace_git_commit: object = None,
    ) -> bool:
        del blocks, root, interactive, trace_git_commit
        return bool(result)

    return fake_process_all_commits


def test_run_root_a_commit_workflow_rejects_empty_plans(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The root workflow should fail when `a.commit` contains no valid blocks."""
    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _empty_read_and_parse_content,
    )

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="No valid commit blocks",
    ):
        git_batch_workflow._run_root_a_commit_workflow(tmp_path)


@pytest.mark.parametrize("expected_exit", [0, 1])
def test_run_root_a_commit_workflow_runs_commit_phase_when_tree_is_dirty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    expected_exit: int,
) -> None:
    """The root workflow should validate first and then return the commit-phase result.

    On a fully successful run (exit 0) a.commit is emptied; on a failed run
    (exit 1) the plan is kept so the user can retry.
    """
    block = _valid_block()
    process_result = expected_exit == 0
    a_commit_path = tmp_path / "a.commit"
    a_commit_path.write_text("git add -A src/example.py\n", encoding="utf-8")

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _return_commit_blocks([block]),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_missing_files_for_blocks",
        _noop_validate_missing_files,
    )
    monkeypatch.setattr(
        git_batch_workflow, "_is_worktree_clean", _return_false_for_root,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_staged_count_matches_git_adds",
        _noop_validate_staged_count,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_all_commits",
        _return_process_all_commits(process_result),
    )

    assert git_batch_workflow._run_root_a_commit_workflow(tmp_path) == expected_exit
    if process_result:
        # Assert: a fully applied plan is emptied.
        assert a_commit_path.read_text(encoding="utf-8") == ""
    else:
        # Assert: a failed run keeps the plan for a retry.
        assert a_commit_path.read_text(encoding="utf-8") != ""


def test_run_root_a_commit_workflow_stops_on_staged_count_mismatch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A staged-count mismatch should stop before commits run and keep a.commit."""
    block = _valid_block()
    a_commit_path = tmp_path / "a.commit"
    a_commit_path.write_text("git add -A src/example.py\n", encoding="utf-8")

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _return_commit_blocks([block]),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_missing_files_for_blocks",
        _noop_validate_missing_files,
    )
    monkeypatch.setattr(
        git_batch_workflow, "_is_worktree_clean", _return_false_for_root,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_staged_count_matches_git_adds",
        _raise_staged_count_mismatch,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_all_commits",
        _return_process_all_commits(result=True),
    )

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Validation failed",
    ):
        git_batch_workflow._run_root_a_commit_workflow(tmp_path)

    # Assert: the plan is untouched when validation stops the run.
    assert a_commit_path.read_text(encoding="utf-8") != ""


def _capture_process_all_commits(
    store: dict[str, object],
) -> Callable[..., bool]:
    def fake_process_all_commits(
        blocks: list[git_batch_models.CommitBlock],
        root: Path,
        *,
        interactive: object = True,
        trace_git_commit: object = None,
    ) -> bool:
        del blocks, root, trace_git_commit
        store["interactive"] = interactive
        return True

    return fake_process_all_commits


def test_run_root_a_commit_workflow_forwards_interactive_flag(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The root workflow should forward interactive=False to the commit loop."""
    block = _valid_block()
    captured: dict[str, object] = {}
    a_commit_path = tmp_path / "a.commit"
    a_commit_path.write_text("git add -A src/example.py\n", encoding="utf-8")

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _return_commit_blocks([block]),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_missing_files_for_blocks",
        _noop_validate_missing_files,
    )
    monkeypatch.setattr(
        git_batch_workflow, "_is_worktree_clean", _return_false_for_root,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_staged_count_matches_git_adds",
        _noop_validate_staged_count,
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_process_all_commits",
        _capture_process_all_commits(captured),
    )

    assert (
        git_batch_workflow._run_root_a_commit_workflow(tmp_path, interactive=False) == 0
    )
    assert captured["interactive"] is False


def test_empty_a_commit_file_warns_when_write_fails(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Emptying should warn and return instead of raising when the write fails."""
    # A directory at the a.commit path makes write_text raise OSError.
    (tmp_path / "a.commit").mkdir()
    caplog.set_level("WARNING")

    git_batch_workflow._empty_a_commit_file(tmp_path)

    assert "Could not empty" in caplog.text


# eof
