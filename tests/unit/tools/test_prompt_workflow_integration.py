"""Full prompt and memory workflows over explicit branch/status observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_memory as memory

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

def _branch_git(args: list[str], *, cwd: Path) -> str:
    """Supply the exact branch-history observations needed by draft discovery."""
    del cwd
    outputs: dict[tuple[str, ...], str] = {
        ("rev-parse", "--abbrev-ref", "HEAD"): "feature/iso\n",
        ("for-each-ref", "--format=%(refname:short)", "refs/heads/"): "main\nfeature/iso\n",
        ("rev-list", "--first-parent", "--boundary", "HEAD", "--not", "main", "--"): "tip\n-base\n",
        ("diff", "--name-only", "--diff-filter=AMR", "base", "HEAD", "--"): "docs/draft.v9.8.0.iso.md\n",
        ("status", "--porcelain", "--untracked-files=all"): "",
    }
    return outputs[tuple(args)]


def _working_tree_git(args: list[str], *, cwd: Path) -> str:
    """Return the bounded read-only Git view for a new working-tree draft."""
    del cwd
    command = tuple(args)
    if command == ("rev-parse", "--abbrev-ref", "HEAD"):
        return "main\n"
    if command[:1] == ("for-each-ref",):
        return "main\n"
    if command[:2] == ("status", "--porcelain"):
        return "?? docs/draft.v9.8.0.iso.md\n"
    return ""


@pytest.fixture
def working_tree_repo(tmp_path: Path) -> Path:
    """Return a repo with a draft present in the working tree."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def branch_draft_repo(tmp_path: Path) -> Path:
    """Return a repo with a draft committed on a feature branch."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def completed_working_tree_run(
    monkeypatch: pytest.MonkeyPatch,
    working_tree_repo: Path,
) -> tuple[Path, int]:
    """Run production discovery, prompt rendering and memory persistence."""
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)
    monkeypatch.setattr(prompt_workflow.git, "run_git", _working_tree_git)
    return working_tree_repo, prompt_workflow.run(working_tree_repo)


@pytest.fixture
def completed_branch_draft_run(
    monkeypatch: pytest.MonkeyPatch,
    branch_draft_repo: Path,
) -> tuple[Path, int]:
    """Run branch-draft discovery outside the measured assertion call."""
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)
    monkeypatch.setattr(prompt_workflow.git, "run_git", _branch_git)
    return branch_draft_repo, prompt_workflow.run(branch_draft_repo)


def test_run_end_to_end_with_declared_worktree(
    completed_working_tree_run: tuple[Path, int],
) -> None:
    """A working-tree draft drives a real run to a written prompt and memory."""
    working_tree_repo, status = completed_working_tree_run

    assert status == 0

    prompt = (working_tree_repo / "a.prompt.txt").read_text(encoding="utf-8")
    assert "llm-shared/instructions/split-and-define.md" in prompt
    assert "this is about v9.8.0 iso." in prompt
    assert "docs/draft.v9.8.0.iso.md" in prompt

    record = memory.read_memory(working_tree_repo)
    assert record is not None
    assert record.step == 1
    assert record.instruction == "split-and-define.md"


def test_run_detects_draft_committed_on_branch(
    completed_branch_draft_run: tuple[Path, int],
) -> None:
    """A draft committed on a feature branch is found via the fork-point diff."""
    branch_draft_repo, status = completed_branch_draft_run

    assert status == 0
    prompt = (branch_draft_repo / "a.prompt.txt").read_text(encoding="utf-8")
    assert "docs/draft.v9.8.0.iso.md" in prompt


# eof
