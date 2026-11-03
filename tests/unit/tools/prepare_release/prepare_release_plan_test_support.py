"""Declared repository observations for the real release planner.

Each scenario supplies dependency answers directly. No Git command parser,
commit graph traversal, merge calculation, shell, or native repository exists.
"""

# These methods implement the production repository query protocol.
# ruff: noqa: D102, D103, D107

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    MergePreview,
    RebasePreview,
)

if TYPE_CHECKING:
    from pathlib import Path

BASE = "1" * 40
TIP = "2" * 40
PARENT = "3" * 40
MERGE = "4" * 40


@dataclass
class RepositoryFacts:
    """Answer declared dependency observations without deriving topology."""

    root: Path
    current: str = "feature"
    refs: dict[str, str] = field(default_factory=lambda: {"main": BASE, "feature": TIP})
    ancestors: set[tuple[str, str]] = field(default_factory=lambda: {(BASE, TIP)})
    config: dict[str, str] = field(default_factory=dict[str, str])
    reflogs: dict[str, tuple[tuple[str, str], ...]] = field(
        default_factory=lambda: {"feature": ((BASE, "branch: Created from main"),)},
    )
    ranges: dict[str, tuple[CommitSummary, ...]] = field(
        default_factory=lambda: {f"{BASE}..feature": (CommitSummary(TIP, "feat: feature change"),)},
    )
    bases: dict[tuple[str, str, bool], str | None] = field(default_factory=dict[tuple[str, str, bool], str | None])
    histories: dict[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    parents: dict[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    merged_ranges: set[str] = field(default_factory=set[str])
    containing_tags: dict[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    latest_tags: dict[str, str | None] = field(default_factory=lambda: {"main": "v1.0.0"})
    merge_previews: dict[tuple[str, str], MergePreview] = field(default_factory=dict[tuple[str, str], MergePreview])
    rebase_previews: dict[tuple[str, str, str], RebasePreview] = field(default_factory=dict[tuple[str, str, str], RebasePreview])

    def verify_repository(self) -> None:
        """The scenario explicitly declares a valid repository."""

    @staticmethod
    def assert_supported_version() -> str:
        return "2.50.0"

    def current_branch(self) -> str:
        return self.current

    def resolve(self, ref: str) -> str:
        return self.refs.get(ref, ref)

    def config_value(self, key: str) -> str | None:
        return self.config.get(key)

    def branch_exists(self, branch: str) -> bool:
        return branch in self.refs

    @staticmethod
    def remote_default_branch() -> None:
        return None

    def latest_tag(self, ref: str) -> str | None:
        return self.latest_tags[ref]

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        pair = self.resolve(ancestor), self.resolve(descendant)
        return pair[0] == pair[1] or pair in self.ancestors

    def merge_base(self, left: str, right: str, *, fork_point: bool = False) -> str | None:
        return self.bases.get((left, right, fork_point))

    def commit_count(self, revision_range: str) -> int:
        return len(self.ranges[revision_range])

    def commits(self, revision_range: str) -> tuple[CommitSummary, ...]:
        return self.ranges[revision_range]

    def contains_merge(self, revision_range: str) -> bool:
        return revision_range in self.merged_ranges

    def tags_containing(self, ref: str) -> tuple[str, ...]:
        return self.containing_tags[ref]

    def reflog(self, branch: str) -> tuple[tuple[str, str], ...]:
        return self.reflogs.get(branch, ())

    def first_parent_history(self, branch: str) -> tuple[str, ...]:
        return self.histories.get(branch, ())

    def commit_parents(self, commit: str) -> tuple[str, ...]:
        return self.parents[commit]

    def local_branches(self) -> tuple[str, ...]:
        return tuple(self.refs)

    @staticmethod
    def isolated_object_environment() -> AbstractContextManager[dict[str, str]]:
        return nullcontext({})

    def preview_merge(self, destination: str, source: str, *, env: dict[str, str] | None = None) -> MergePreview:
        assert env == {}
        return self.merge_previews[destination, source]

    def preview_rebase(self, base: str, branch: str, target: str) -> RebasePreview:
        return self.rebase_previews[base, branch, target]


_REPOSITORIES: dict[Path, RepositoryFacts] = {}


def repository_for(root: Path) -> RepositoryFacts:
    return _REPOSITORIES[root]


def declare_repository(root: Path) -> RepositoryFacts:
    """Register independent facts for one scenario; scratch storage is virtual."""
    root.mkdir()
    facts = RepositoryFacts(root)
    _REPOSITORIES[root] = facts
    return facts


# eof
