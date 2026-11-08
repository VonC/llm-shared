"""Programmatic repository facts for release policy, without Git startup.

Fixtures declare metadata, indexes and configuration directly. The boundary
supplies only observations consumed by production, never a Git interpreter.

Step 1 of v0.14.0 version-sources adds a declared release history: commits
with their parents, HEAD, main, tags and listing names. The five typed release
observations are answered from it by reachability over the declared parents,
without interpreting Git arguments, and each call is recorded. The tips query
keeps the production command-line guard. A declared tag of a tag carries its
inner tag's commit, as the production record parser reports it.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git import (
    GitExecutionContext,
    GitRevisionNotFoundError,
    TagRecord,
)
from tools.release_workflow.git_environment import (
    ConfigEntry,
    GitPolicyError,
    controlled_environment,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_MISSING_STATUS = 129


@dataclass
class ReleaseHistory:
    """Declared commits, HEAD, main, tags and listing names, with recorded calls."""

    parents: dict[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    head: str | None = None
    main: str | None = None
    tags: list[TagRecord] = field(default_factory=list[TagRecord])
    names: tuple[str, ...] = ()
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])

    def commit(self, name: str, *parents: str) -> str:
        """Declare one commit after its parents and return its id."""
        self.parents[name] = parents
        return name

    def tag(self, name: str, commit: str, annotation: str | None = None) -> TagRecord:
        """Declare an annotated tag, or a lightweight one without annotation."""
        record = TagRecord(name, "commit" if annotation is None else "tag", commit, annotation)
        self.tags.append(record)
        return record

    def nested_tag(self, name: str, inner: str, annotation: str) -> TagRecord:
        """Declare an annotated tag of the inner tag: it carries the inner tag's commit."""
        commit = next(tag.commit for tag in self.tags if tag.name == inner)
        return self.tag(name, commit, annotation)

    def resolve(self, revision: str) -> str:
        """Resolve HEAD, main, a tag ref or a declared commit; anything else is missing."""
        named = {"HEAD": self.head, "main": self.main, **{f"refs/tags/{tag.name}": tag.commit for tag in self.tags}}
        commit = named.get(revision, revision if revision in self.parents else None)
        if commit is None:
            result = subprocess.CompletedProcess(["for-each-ref"], _MISSING_STATUS, "", f"error: malformed object name {revision}\n")
            raise GitRevisionNotFoundError(result, revision)
        return commit

    def reachable(self, revision: str) -> frozenset[str]:
        """Return the commits reachable from a revision, visiting each once."""
        pending, seen = [self.resolve(revision)], set[str]()
        while pending:
            commit = pending.pop()
            if commit not in seen:
                seen.add(commit)
                pending.extend(self.parents[commit])
        return frozenset(seen)


@dataclass
class RepositoryFacts:
    """Independent index, effective configuration and release history for one scenario."""

    indexes: dict[Path, tuple[str, ...]] = field(default_factory=dict[Path, tuple[str, ...]])
    configurations: dict[Path, tuple[ConfigEntry, ...]] = field(default_factory=dict[Path, tuple[ConfigEntry, ...]])
    history: ReleaseHistory = field(default_factory=ReleaseHistory)


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

    def tag_records(self, *, cwd: Path, merged: str | None = None) -> tuple[TagRecord, ...]:
        """Return the declared tags, or those reachable from the filter revision."""
        del cwd
        history = self.facts.history
        history.calls.append(("tag_records", *(() if merged is None else (merged,))))
        if merged is None:
            return tuple(history.tags)
        reachable = history.reachable(merged)
        return tuple(tag for tag in history.tags if tag.commit in reachable)

    def independent_commits(self, commits: Sequence[str], *, cwd: Path) -> tuple[str, ...]:
        """Keep the candidates that no other candidate reaches, after the production guard."""
        del cwd
        self._independent_arguments(commits)
        history = self.facts.history
        history.calls.append(("independent_commits", *commits))
        ancestors = {ancestor for commit in commits for ancestor in history.reachable(commit) - {commit}}
        return tuple(dict.fromkeys(commit for commit in commits if commit not in ancestors))

    def tag_names(self, *, cwd: Path, merged: str, not_merged: str) -> tuple[str, ...]:
        """Name the declared tags reachable from one revision and not from another."""
        del cwd
        history = self.facts.history
        history.calls.append(("tag_names", merged, not_merged))
        included, excluded = history.reachable(merged), history.reachable(not_merged)
        return tuple(tag.name for tag in history.tags if tag.commit in included and tag.commit not in excluded)

    def commit_count(self, revision_range: str, *, cwd: Path) -> int:
        """Count the declared commits of `end` or of `start..end`."""
        del cwd
        history = self.facts.history
        history.calls.append(("commit_count", revision_range))
        start, separator, end = revision_range.partition("..")
        if not separator:
            return len(history.reachable(start))
        return len(history.reachable(end) - history.reachable(start))

    def listing(self, *, cwd: Path) -> tuple[str, ...]:
        """Return the declared candidate listing names."""
        del cwd
        self.facts.history.calls.append(("listing",))
        return self.facts.history.names


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
