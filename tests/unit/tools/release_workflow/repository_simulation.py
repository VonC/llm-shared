"""Programmatic repository facts for release policy, without Git startup.

Fixtures declare metadata, indexes and configuration directly. The boundary
supplies only observations consumed by production, never a Git interpreter.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_environment import (
    ConfigEntry,
    GitPolicyError,
    controlled_environment,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


@dataclass
class RepositoryFacts:
    """Independent index and effective configuration for one scenario."""

    indexes: dict[Path, tuple[str, ...]] = field(default_factory=dict[Path, tuple[str, ...]])
    configurations: dict[Path, tuple[ConfigEntry, ...]] = field(default_factory=dict[Path, tuple[ConfigEntry, ...]])


@dataclass(frozen=True)
class RepositoryObservations(GitExecutionContext):
    """Exercise production Git policy using explicit external observations."""

    facts: RepositoryFacts

    def _root(self, cwd: Path) -> Path | None:
        """Locate a declared identity, without interpreting Git arguments."""
        directory = cwd.resolve()
        return next((path for path in (directory, *directory.parents) if path in self.facts.indexes), None)

    def read_version(self, *, cwd: Path) -> tuple[int, int, int]:
        """Return the fixture's verified version."""
        del cwd
        return self.version

    def effective_config(self, *, cwd: Path) -> tuple[ConfigEntry, ...]:
        """Supply typed entries to the real configuration policy."""
        root = self._root(cwd)
        entries = list(self.facts.configurations.get(root, ()) if root is not None else ())
        for selector in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG"):
            selected = self.environment.values.get(selector)
            if selected:
                entries.extend(self.facts.configurations.get(Path(selected), ()))
        return tuple(entries)

    def index(self, *, cwd: Path, directory: str | None = None) -> tuple[str, ...]:
        """Read the explicitly supplied index inventory."""
        root = self._root(cwd)
        paths = self.facts.indexes.get(root, ()) if root is not None else ()
        return tuple(path for path in paths if directory is None or Path(path).is_relative_to(directory))

    def metadata(self, *, cwd: Path) -> tuple[Path, Path, Path]:
        """Return declared worktree metadata as paths, never command output."""
        root = self._root(cwd)
        if root is None:
            message = "not a git repository"
            raise GitPolicyError(message)
        marker = root / ".git"
        git_dir = Path(marker.read_text(encoding="utf-8").removeprefix("gitdir: ").strip()) if marker.is_file() else marker
        common = git_dir.parent.parent if marker.is_file() else git_dir
        return root, git_dir, common


@dataclass(frozen=True)
class GitSandbox:
    """One isolated A/B/linked/nested repository state."""

    home: Path
    verified_git: RepositoryObservations
    environment: Mapping[str, str]

    def context(self, **overrides: str) -> RepositoryObservations:
        """Retain production environment policy with scenario-specific facts."""
        source = dict(self.environment, **overrides)
        return replace(self.verified_git, original_cwd=self.home,
                       environment=controlled_environment(source, non_interactive=True))

    def stage(self, root: Path, *paths: str) -> None:
        """Declare an index without initializing or executing Git."""
        self.verified_git.facts.indexes[root.resolve()] = tuple(paths)

    def configure(self, source: Path, *entries: ConfigEntry) -> None:
        """Declare observations; production still validates each entry."""
        self.verified_git.facts.configurations[source] = tuple(entries)

    def junction(self, name: str, target: Path) -> Path:
        """Create a directory link via Python, without starting a shell."""
        import _winapi  # noqa: PLC0415 - native Windows filesystem boundary

        junction = self.home / name
        _winapi.CreateJunction(str(target), str(junction))
        return junction

    def linked_worktree(self) -> Path:
        """Declare linked metadata with a separate common directory."""
        root = self.home / "A"
        linked = self.home / "linked"
        linked.mkdir()
        git_dir = root / ".git/worktrees/linked"
        git_dir.mkdir(parents=True)
        (linked / ".git").write_text(f"gitdir: {git_dir}\n", encoding="utf-8")
        self.stage(linked)
        self.configure(linked, ConfigEntry("local", f"file:{root / '.git/config'}", "core.bare", "false"))
        return linked


def _repository(root: Path) -> None:
    """Write only filesystem boundaries inspected by production policy."""
    (root / ".git").mkdir(parents=True)
    (root / "sub").mkdir()
    (root / "B.txt").write_text("B", encoding="utf-8")


def create_template(home: Path) -> GitSandbox:
    """Construct facts without executable discovery or process startup."""
    binary = home / "bin/git.exe"
    binary.parent.mkdir()
    binary.write_bytes(b"not executable: simulated repository port")
    environment = {"PATH": str(binary.parent), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}
    git = RepositoryObservations(binary, (2, 45, 0), controlled_environment(environment, non_interactive=True), home, non_interactive=True, facts=RepositoryFacts())
    _repository(home / "B")
    git.facts.indexes[(home / "B").resolve()] = ()
    return GitSandbox(home, git, environment)


def copy_template(template: GitSandbox, destination: Path) -> GitSandbox:
    """Build independent tiny metadata and index state without copying Git."""
    for name in ("A", "B", "A/nested"):
        _repository(destination / name)
    (destination / "A/A.txt").write_text("A", encoding="utf-8")
    facts = RepositoryFacts(indexes={(destination / name).resolve(): () for name in ("A", "B", "A/nested")})
    return GitSandbox(destination, replace(template.verified_git, facts=facts), template.environment)


# eof
