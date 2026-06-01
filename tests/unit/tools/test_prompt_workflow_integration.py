"""Integration test for prompt_workflow against a real temporary git repository.

Fix: Drive the whole flow with real git plumbing (branch, fork point, porcelain
parsing) so the draft on the working tree is detected, the prompt is built, and
the memory file is written, with only the menu and clipboard stubbed.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_memory as memory

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

pytestmark = pytest.mark.skipif(
    shutil.which("git") is None,
    reason="git is required for the integration test",
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init")
    _git(repo, "config", "user.email", "tester@example.com")
    _git(repo, "config", "user.name", "Tester")
    (repo / "README.md").write_text("readme", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "-c", "commit.gpgsign=false", "commit", "-m", "init")


def test_run_end_to_end_with_real_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A working-tree draft drives a real run to a written prompt and memory."""
    _init_repo(tmp_path)
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")

    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)

    assert prompt_workflow.run(tmp_path) == 0

    prompt = (tmp_path / "a.prompt.txt").read_text(encoding="utf-8")
    assert "llm-shared/instructions/split-and-define.md" in prompt
    assert "this is about v9.8.0 iso." in prompt
    assert "docs/draft.v9.8.0.iso.md" in prompt

    record = memory.read_memory(tmp_path)
    assert record is not None
    assert record.step == 1
    assert record.instruction == "split-and-define.md"


def test_run_detects_draft_committed_on_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A draft committed on a feature branch is found via the fork-point diff."""
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature/iso")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")
    _git(tmp_path, "add", "docs/draft.v9.8.0.iso.md")
    _git(tmp_path, "-c", "commit.gpgsign=false", "commit", "-m", "add draft")

    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)

    assert prompt_workflow.run(tmp_path) == 0
    prompt = (tmp_path / "a.prompt.txt").read_text(encoding="utf-8")
    assert "docs/draft.v9.8.0.iso.md" in prompt


# eof
