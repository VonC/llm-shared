"""Process-free Git topology used by prepare-release workflow tests."""

# The public method names deliberately mirror the production Git protocol.
# ruff: noqa: D102, D103, D107

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    MergePreview,
    RebasePreview,
)

_CREATE_FROM_ARGUMENTS = 2

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class _Commit:
    oid: str
    subject: str
    parents: tuple[str, ...]
    changed_paths: frozenset[str]


class SyntheticGitRepository:
    """Model the small ref, graph, reflog, tag, and preview protocol in memory."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.current = "main"
        self.refs: dict[str, str] = {}
        self.commits_by_oid: dict[str, _Commit] = {}
        self.config: dict[str, str] = {}
        self.reflogs: dict[str, list[tuple[str, str]]] = {}
        self.tags: dict[str, str] = {}
        self._next_oid = 1

    def add_commit(
        self,
        subject: str,
        changed_paths: frozenset[str],
        *,
        parents: tuple[str, ...] | None = None,
    ) -> str:
        """Advance the current branch with one deterministic commit."""
        if parents is None:
            parent = self.refs.get(self.current)
            parents = (parent,) if parent is not None else ()
        oid = f"{self._next_oid:040x}"
        self._next_oid += 1
        self.commits_by_oid[oid] = _Commit(oid, subject, parents, changed_paths)
        self.refs[self.current] = oid
        return oid

    def verify_repository(self) -> None:
        """Accept this deliberately constructed repository."""

    @staticmethod
    def assert_supported_version() -> str:
        return "2.50.0"

    def current_branch(self) -> str:
        return self.current

    def resolve(self, ref: str) -> str:
        if ref == "HEAD":
            return self.refs[self.current]
        return self.refs.get(ref, ref)

    def config_value(self, key: str) -> str | None:
        return self.config.get(key)

    def branch_exists(self, branch: str) -> bool:
        return branch in self.refs

    @staticmethod
    def remote_default_branch() -> None:
        return None

    def latest_tag(self, ref: str) -> str | None:
        tip = self.resolve(ref)
        matching = [name for name, oid in self.tags.items() if self.is_ancestor(oid, tip)]
        return matching[-1] if matching else None

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        return self.resolve(ancestor) in self._ancestors(self.resolve(descendant))

    def merge_base(
        self,
        left: str,
        right: str,
        *,
        fork_point: bool = False,
    ) -> str | None:
        if fork_point and not (self.root / ".git" / "logs").is_dir():
            return None
        left_distances = self._distances(self.resolve(left))
        right_distances = self._distances(self.resolve(right))
        common = left_distances.keys() & right_distances.keys()
        if not common:
            return None
        return min(
            common,
            key=lambda oid: (left_distances[oid] + right_distances[oid], -int(oid, 16)),
        )

    def commit_count(self, revision_range: str) -> int:
        return len(self.commits(revision_range))

    def commits(self, revision_range: str) -> tuple[CommitSummary, ...]:
        if ".." not in revision_range:
            selected = self._ancestors(self.resolve(revision_range))
        else:
            base, branch = revision_range.split("..", maxsplit=1)
            selected = self._ancestors(self.resolve(branch)) - self._ancestors(
                self.resolve(base),
            )
        return tuple(
            CommitSummary(oid, self.commits_by_oid[oid].subject)
            for oid in sorted(selected, key=lambda value: int(value, 16))
        )

    def contains_merge(self, revision_range: str) -> bool:
        return any(
            len(self.commits_by_oid[commit.oid].parents) > 1
            for commit in self.commits(revision_range)
        )

    def tags_containing(self, ref: str) -> tuple[str, ...]:
        oid = self.resolve(ref)
        return tuple(name for name, tip in self.tags.items() if self.is_ancestor(oid, tip))

    def reflog(self, branch: str) -> tuple[tuple[str, str], ...]:
        if not (self.root / ".git" / "logs").is_dir():
            return ()
        return tuple(self.reflogs.get(branch, ()))

    def first_parent_history(self, branch: str) -> tuple[str, ...]:
        history: list[str] = []
        oid: str | None = self.resolve(branch)
        while oid is not None:
            history.append(oid)
            parents = self.commits_by_oid[oid].parents
            oid = parents[0] if parents else None
        history.reverse()
        return tuple(history)

    def commit_parents(self, commit: str) -> tuple[str, ...]:
        return self.commits_by_oid[self.resolve(commit)].parents

    def local_branches(self) -> tuple[str, ...]:
        return tuple(self.refs)

    @staticmethod
    def isolated_object_environment() -> AbstractContextManager[dict[str, str]]:
        return nullcontext({})

    def preview_merge(
        self,
        destination: str,
        source: str,
        *,
        env: dict[str, str] | None = None,
    ) -> MergePreview:
        del env
        base = self.merge_base(destination, source)
        destination_paths = self._changed_since(base, self.resolve(destination))
        source_paths = self._changed_since(base, self.resolve(source))
        conflicts = tuple(sorted(destination_paths & source_paths))
        return MergePreview(not conflicts, "tree", conflicts, ())

    @staticmethod
    def preview_rebase(
        _base: str,
        _branch: str,
        _target: str,
    ) -> RebasePreview:
        return RebasePreview(
            clean=True,
            checked_commits=1,
            conflict_commit=None,
            conflict_subject=None,
            merge=None,
        )

    def _ancestors(self, tip: str) -> set[str]:
        pending = [tip]
        result: set[str] = set()
        while pending:
            oid = pending.pop()
            if oid in result or oid not in self.commits_by_oid:
                continue
            result.add(oid)
            pending.extend(self.commits_by_oid[oid].parents)
        return result

    def _distances(self, tip: str) -> dict[str, int]:
        distances = {tip: 0}
        pending = [tip]
        while pending:
            oid = pending.pop(0)
            for parent in self.commits_by_oid.get(oid, _Commit(oid, "", (), frozenset())).parents:
                distance = distances[oid] + 1
                if parent not in distances or distance < distances[parent]:
                    distances[parent] = distance
                    pending.append(parent)
        return distances

    def _changed_since(self, base: str | None, tip: str) -> frozenset[str]:
        excluded: set[str] = self._ancestors(base) if base is not None else set()
        selected = self._ancestors(tip) - excluded
        return frozenset(
            path
            for oid in selected
            for path in self.commits_by_oid[oid].changed_paths
        )


_REPOSITORIES: dict[Path, SyntheticGitRepository] = {}


def repository_for(root: Path) -> SyntheticGitRepository:
    return _REPOSITORIES[root.resolve()]


def git(repo: Path, *args: str) -> str:  # noqa: C901, PLR0911
    """Apply one supported Git-shaped topology command in memory."""
    repository = repository_for(repo)
    operation = args[0]
    if operation == "switch":
        _switch(repository, args[1:])
        return ""
    if operation == "merge":
        source = args[args.index("--no-ff") + 1]
        subject = args[args.index("-m") + 1]
        repository.add_commit(
            subject,
            frozenset(),
            parents=(repository.refs[repository.current], repository.refs[source]),
        )
        return ""
    if operation == "tag":
        repository.tags[args[1]] = repository.refs[repository.current]
        return ""
    if operation == "config":
        repository.config[args[1]] = args[2]
        return ""
    if operation == "branch":
        repository.refs[args[1]] = repository.resolve(args[2])
        return ""
    if operation == "rebase":
        _rebase(repository, args[1], args[2])
        return ""
    if operation == "reset":
        target = args[-1]
        repository.refs[repository.current] = repository.resolve(target)
        repository.reflogs.setdefault(repository.current, []).append(
            (repository.resolve(target), f"reset: moving to {target}"),
        )
        return ""
    if operation == "rev-parse":
        return repository.resolve(args[1])
    raise AssertionError(args)


def initialize_repository(repo: Path) -> str:
    """Initialize the deterministic main graph and release tag."""
    repo.mkdir()
    (repo / ".git" / "logs").mkdir(parents=True)
    repository = SyntheticGitRepository(repo)
    _REPOSITORIES[repo.resolve()] = repository
    base = repository.add_commit("feat: base", frozenset({"shared.txt"}))
    repository.tags["v1.0.0"] = base
    return base


def commit_file(repo: Path, path: str, _content: str, message: str) -> str:
    """Advance one synthetic branch with the same changed-path evidence."""
    return repository_for(repo).add_commit(message, frozenset({path}))


def _switch(repository: SyntheticGitRepository, args: tuple[str, ...]) -> None:
    if args[0] == "--orphan":
        repository.current = args[1]
        repository.refs.pop(repository.current, None)
        repository.reflogs[repository.current] = []
        return
    if args[0] == "-c":
        branch = args[1]
        source = (
            args[2]
            if len(args) > _CREATE_FROM_ARGUMENTS
            else repository.current
        )
        base = repository.resolve(source)
        repository.refs[branch] = base
        repository.reflogs[branch] = [(base, f"branch: Created from {source}")]
        repository.current = branch
        return
    repository.current = args[0]


def _rebase(repository: SyntheticGitRepository, target: str, branch: str) -> None:
    target_oid = repository.resolve(target)
    branch_oid = repository.resolve(branch)
    base = repository.merge_base(target_oid, branch_oid)
    excluded: set[str] = (
        repository._ancestors(base) if base is not None else set()  # noqa: SLF001
    )
    selected = repository._ancestors(branch_oid) - excluded  # noqa: SLF001
    parent = target_oid
    repository.current = branch
    for oid in sorted(selected, key=lambda value: int(value, 16)):
        commit = repository.commits_by_oid[oid]
        parent = repository.add_commit(
            commit.subject,
            commit.changed_paths,
            parents=(parent,),
        )
    repository.refs[branch] = parent
    repository.reflogs.setdefault(branch, []).append(
        (parent, f"rebase (finish): returning to {branch} onto {target_oid}"),
    )
