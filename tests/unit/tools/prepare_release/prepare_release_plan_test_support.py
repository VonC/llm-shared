"""Real-repository fixtures for prepare-release planner tests."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def git(repo: Path, *args: str) -> str:
    """Run Git in a temporary test repository and return stripped stdout."""
    result = subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def initialize_repository(repo: Path) -> str:
    """Initialize a main branch with one tagged base commit."""
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Release Planner Tests")
    git(repo, "config", "user.email", "release-planner@example.invalid")
    (repo / "shared.txt").write_text("base\n", encoding="utf-8")
    git(repo, "add", "shared.txt")
    git(repo, "commit", "-m", "feat: base")
    git(repo, "tag", "v1.0.0")
    return git(repo, "rev-parse", "HEAD")


def commit_file(repo: Path, path: str, content: str, message: str) -> str:
    """Write and commit one file, returning the new commit OID."""
    (repo / path).write_text(content, encoding="utf-8")
    git(repo, "add", path)
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


# eof
