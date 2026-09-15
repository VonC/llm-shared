"""Prevent inherited project environments from redirecting branch workflows."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import prompt_workflow


@pytest.mark.parametrize("git_marker", ["directory", "file"])
@pytest.mark.parametrize("location", [".", "docs/v0.13.0"])
def test_main_uses_current_checkout_despite_stale_project_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    git_marker: str,
    location: str,
) -> None:
    """A checkout or linked worktree wins over a valid but stale PRJ_DIR."""
    main_root = tmp_path / "main"
    (main_root / ".git").mkdir(parents=True)
    worktree = tmp_path / "no_polling"
    worktree.mkdir()
    marker = worktree / ".git"
    if git_marker == "directory":
        marker.mkdir()
    else:
        marker.write_text("gitdir: ../main/.git/worktrees/no_polling\n", encoding="utf-8")
    working_directory = worktree / location
    working_directory.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(working_directory)
    monkeypatch.setenv("PRJ_DIR", str(main_root))
    seen: list[Path] = []

    def run(root: Path, *, pick: bool = False) -> int:
        assert not pick
        seen.append(root)
        return 0

    monkeypatch.setattr(prompt_workflow, "run", run)

    assert prompt_workflow.main([]) == 0
    assert seen == [worktree.resolve()]


@pytest.mark.parametrize("use_override", [False, True])
def test_main_preserves_explicit_root_and_environment_fallback(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    use_override: bool,
) -> None:
    """An explicit root wins; outside a checkout PRJ_DIR remains available."""
    project = tmp_path / "project"
    (project / ".git").mkdir(parents=True)
    caller = tmp_path / "caller"
    caller.mkdir()
    if use_override:
        (caller / ".git").mkdir()
    monkeypatch.chdir(caller)
    monkeypatch.setenv("PRJ_DIR", str(project))
    original_exists = Path.exists

    def exists(path: Path) -> bool:
        # A user's dotfiles checkout can contain pytest's temporary directory.
        if path.name == ".git" and not path.is_relative_to(tmp_path):
            return False
        return original_exists(path)

    monkeypatch.setattr(Path, "exists", exists)
    seen: list[Path] = []

    def run(root: Path, *, pick: bool = False) -> int:
        assert not pick
        seen.append(root)
        return 0

    monkeypatch.setattr(prompt_workflow, "run", run)
    arguments = ["--root", str(project)] if use_override else []

    assert prompt_workflow.main(arguments) == 0
    assert seen == [project.resolve()]


# eof
