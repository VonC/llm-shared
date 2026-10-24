"""Reusable real Git templates and isolated repository copies.

Initialize one empty repository and verify Git once, then copy only that small
template. Create indexes and linked worktrees only where they are asserted.
Use Git for Windows' native binary when present to avoid its launcher process.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_environment import controlled_environment

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


@dataclass(frozen=True)
class GitSandbox:
    """One isolated A/B/linked/nested repository matrix."""

    home: Path
    verified_git: GitExecutionContext
    environment: Mapping[str, str]

    def context(self, **overrides: str) -> GitExecutionContext:
        """Reuse the verified executable while isolating each case's environment."""
        source = dict(self.environment, **overrides)
        return replace(self.verified_git, original_cwd=self.home, environment=controlled_environment(source, non_interactive=True))

    def git(self, args: Sequence[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        """Run fixture Git with fixed executable/environment and a hang bound."""
        return subprocess.run(  # noqa: S603
            [str(self.verified_git.executable), *args], cwd=cwd, env=dict(self.environment),
            check=True, capture_output=True, text=True, encoding="utf-8", timeout=10,
        )

    def junction(self, name: str, target: Path) -> Path:
        """Create a real Windows directory junction without elevation."""
        junction = self.home / name
        subprocess.run(  # noqa: S603
            [os.environ["COMSPEC"], "/d", "/c", "mklink", "/J", str(junction), str(target)],
            cwd=self.home, check=True, capture_output=True, timeout=10,
        )
        return junction

    def linked_worktree(self) -> Path:
        """Build real linked metadata only for the linked-worktree case."""
        root = self.home / "A"
        self.git(["-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "-c", "maintenance.auto=false", "commit", "--allow-empty", "-m", "Fixture"], cwd=root)
        linked = self.home / "linked"
        self.git(["worktree", "add", "--no-checkout", "--detach", str(linked)], cwd=root)
        return linked


def create_template(home: Path) -> GitSandbox:
    """Pay one native init/version probe, without unused commit/worktree setup."""
    executable = shutil.which("git.exe")
    assert executable is not None
    installed = Path(executable).resolve()
    native = installed.parent.parent / "mingw64" / "bin" / "git.exe"
    if native.is_file():
        installed = native
    environment = {key: value for key, value in os.environ.items() if not key.upper().startswith("GIT_")}
    environment.update(GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0", GIT_EDITOR="false")
    path_key = next(key for key in environment if key.upper() == "PATH")
    environment[path_key] = os.pathsep.join((str(installed.parent), environment[path_key]))
    verified = GitExecutionContext.create(environment, original_cwd=home, non_interactive=True)
    sandbox = GitSandbox(home, verified, environment)
    template = home / "empty-template"
    template.mkdir()
    root = home / "B"
    root.mkdir()
    sandbox.git(["init", "--initial-branch=main", f"--template={template}"], cwd=root)
    (root / "B.txt").write_text("B", encoding="utf-8")
    (root / "sub").mkdir()
    return sandbox


def copy_template(template: GitSandbox, destination: Path) -> GitSandbox:
    """Copy real minimal metadata; no absolute worktree pointers need repair."""
    for name in ("A", "B", "A/nested"):
        shutil.copytree(template.home / "B", destination / name)
    (destination / "A" / "A.txt").write_text("A", encoding="utf-8")
    return GitSandbox(destination, template.verified_git, template.environment)


# eof
