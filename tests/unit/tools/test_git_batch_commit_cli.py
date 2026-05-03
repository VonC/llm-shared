"""Tests for split git batch commit CLI result branches.

Fix: Cover the `main()` argument-validation, dry-run, warning, and error
paths in `tools.git_batch_commit_workflow` without growing the workflow test
file.

Fix: Keep monkeypatched read-and-parse helpers keyword-compatible with the
production `main()` calls.
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


def _return_project_root(project_root: Path) -> Callable[[Path], Path]:
    def fake_find_project_root(_start_path: Path) -> Path:
        return project_root

    return fake_find_project_root


def _return_blocks(
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


def _return_no_blocks(
    root: Path,
    filename: str | None,
    interactive: object,
) -> list[git_batch_models.CommitBlock]:
    del root, filename, interactive
    return []


def _noop_validate_missing_files(
    _blocks: list[git_batch_models.CommitBlock],
    _root: Path,
) -> None:
    return None


def _valid_block() -> git_batch_models.CommitBlock:
    commit_message = "fix(scope): title\n\nWhy:\n\nreason before\n\nreason after\n\nWhat:\n\n- change"
    return git_batch_models.CommitBlock(
        git_adds=["git add -A src/example.py"],
        commit_message=commit_message,
        commit_title="fix(scope): title",
    )


def test_main_handles_root_a_commit_filename_conflict(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CLI validation should reject `--root-a-commit` when a filename is also given."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Cannot combine --root-a-commit with filename",
    ):
        git_batch_workflow.main(["plan.txt", "--root-a-commit"])


def test_main_handles_root_a_commit_dry_run_conflict(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """CLI validation should reject `--root-a-commit` together with `--dry-run`."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )

    with pytest.raises(
        git_batch_models.GitBatchCommitError,
        match="Cannot combine --root-a-commit with --dry-run",
    ):
        git_batch_workflow.main(["--root-a-commit", "--dry-run"])


def test_main_logs_clean_content_for_dry_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Dry runs should validate missing files and log clean content on success."""
    block = _valid_block()
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _return_blocks([block]),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_validate_missing_files_for_blocks",
        _noop_validate_missing_files,
    )

    assert git_batch_workflow.main(["plan.txt", "--dry-run"]) == 0
    assert "clean content" in capsys.readouterr().out


def test_main_warns_when_no_valid_blocks_are_found(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Normal execution should warn when there are no commit blocks to process."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )
    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        _return_no_blocks,
    )

    assert git_batch_workflow.main(["plan.txt"]) == 0
    assert "No valid commit blocks found in clipboard." in capsys.readouterr().out


def test_main_returns_one_on_clipboard_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Clipboard failures should become a non-zero CLI exit code."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )

    def fake_read_and_parse_content(
        root: Path,
        *,
        filename: str | None,
        interactive: bool,
    ) -> list[git_batch_models.CommitBlock]:
        del root, filename, interactive
        msg = "clipboard failed"
        raise git_batch_models.ClipboardError(msg)

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        fake_read_and_parse_content,
    )

    assert git_batch_workflow.main(["plan.txt"]) == 1


def test_main_returns_one_on_commit_message_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Commit-message failures should become a non-zero CLI exit code."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )

    def fake_read_and_parse_content(
        root: Path,
        *,
        filename: str | None,
        interactive: bool,
    ) -> list[git_batch_models.CommitBlock]:
        del root, filename, interactive
        msg = "bad message"
        raise git_batch_models.CommitMessageError(msg, [])

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        fake_read_and_parse_content,
    )

    assert git_batch_workflow.main(["plan.txt"]) == 1


def test_main_returns_one_on_git_operation_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Git-operation failures should become a non-zero CLI exit code."""
    monkeypatch.setattr(
        git_batch_workflow,
        "find_project_root",
        _return_project_root(tmp_path),
    )

    def fake_read_and_parse_content(
        root: Path,
        *,
        filename: str | None,
        interactive: bool,
    ) -> list[git_batch_models.CommitBlock]:
        del root, filename, interactive
        msg = "git failed"
        raise git_batch_models.GitOperationError(msg)

    monkeypatch.setattr(
        git_batch_workflow,
        "_read_and_parse_content",
        fake_read_and_parse_content,
    )

    assert git_batch_workflow.main(["plan.txt"]) == 1


# eof
