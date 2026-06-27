"""Integration test for prompt_workflow against a real temporary git repository.

Fix: Drive the whole flow with real git plumbing (branch, fork point, porcelain
parsing) so the draft on the working tree is detected, the prompt is built, and
the memory file is written, with only the menu and clipboard stubbed.

Fix: Supply the commit identity through the GIT_AUTHOR_*/GIT_COMMITTER_* env
vars on every git call and drop the two `git config` subprocess calls from
`_init_repo`. Each git spawn costs a few hundred milliseconds on Windows, so
removing the redundant config processes cuts the test's setup wall time.
"""

from __future__ import annotations

import os
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

# Identity through the environment so the repo setup needs no `git config`
# subprocess calls; merged onto os.environ to keep PATH and the Windows
# system variables git relies on.
_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Tester",
    "GIT_AUTHOR_EMAIL": "tester@example.com",
    "GIT_COMMITTER_NAME": "Tester",
    "GIT_COMMITTER_EMAIL": "tester@example.com",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env=_GIT_ENV,
    )


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-m", "init")


@pytest.fixture
def working_tree_repo(tmp_path: Path) -> Path:
    """Return a repo with a draft present in the working tree."""
    _init_repo(tmp_path)
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def branch_draft_repo(tmp_path: Path) -> Path:
    """Return a repo with a draft committed on a feature branch."""
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-q", "-b", "feature/iso")
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "draft.v9.8.0.iso.md").write_text("# Draft\n", encoding="utf-8")
    _git(tmp_path, "add", "docs/draft.v9.8.0.iso.md")
    _git(tmp_path, "-c", "commit.gpgsign=false", "commit", "-m", "add draft")
    return tmp_path


def test_run_end_to_end_with_real_git(
    monkeypatch: pytest.MonkeyPatch,
    working_tree_repo: Path,
) -> None:
    """A working-tree draft drives a real run to a written prompt and memory."""
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)

    assert prompt_workflow.run(working_tree_repo) == 0

    prompt = (working_tree_repo / "a.prompt.txt").read_text(encoding="utf-8")
    assert "llm-shared/instructions/split-and-define.md" in prompt
    assert "this is about v9.8.0 iso." in prompt
    assert "docs/draft.v9.8.0.iso.md" in prompt

    record = memory.read_memory(working_tree_repo)
    assert record is not None
    assert record.step == 1
    assert record.instruction == "split-and-define.md"


def test_run_detects_draft_committed_on_branch(
    monkeypatch: pytest.MonkeyPatch,
    branch_draft_repo: Path,
) -> None:
    """A draft committed on a feature branch is found via the fork-point diff."""
    monkeypatch.setattr(
        prompt_workflow.menu,
        "select",
        lambda _message, options: options[0][1],
    )
    monkeypatch.setattr(prompt_workflow, "set_clipboard_text", lambda _text: None)

    assert prompt_workflow.run(branch_draft_repo) == 0
    prompt = (branch_draft_repo / "a.prompt.txt").read_text(encoding="utf-8")
    assert "docs/draft.v9.8.0.iso.md" in prompt


# eof
