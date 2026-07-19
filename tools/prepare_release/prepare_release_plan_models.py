"""Data models for the read-only prepare-release planner."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class ReleaseMode(StrEnum):
    """Branch role selected by the invocation ref."""

    ON_MAIN = "on-main"
    INTEGRATION = "integration"
    FEATURE = "feature"


class ReleaseAction(StrEnum):
    """Next topology-changing action proposed by the planner."""

    PREPARE_IN_PLACE = "prepare-in-place"
    MERGE_NO_FF = "merge-no-ff"
    SYNC_INTEGRATION_THEN_MERGE = "sync-integration-then-merge"
    REBASE_ONTO_MAIN_THEN_MERGE = "rebase-onto-main-then-merge"
    ALREADY_RELEASED = "already-released"
    ALREADY_INTEGRATED = "already-integrated"
    NEEDS_FEATURE_BOUNDARY = "needs-feature-boundary"


@dataclass(frozen=True)
class CommitSummary:
    """One commit selected by a release range."""

    oid: str
    subject: str


@dataclass(frozen=True)
class BoundaryCandidate:
    """One possible feature boundary and the evidence supporting it."""

    base: str
    parent_refs: tuple[str, ...]
    evidence: str
    commit_count: int


@dataclass(frozen=True)
class ConflictRecord:
    """Stable merge-tree conflict type plus its affected paths and message."""

    conflict_type: str
    paths: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class MergePreview:
    """Result of one merge-tree simulation."""

    clean: bool
    tree_oid: str
    conflicted_files: tuple[str, ...]
    conflicts: tuple[ConflictRecord, ...]


@dataclass(frozen=True)
class RebasePreview:
    """Result of replaying a feature range in an isolated object store."""

    clean: bool
    checked_commits: int
    conflict_commit: str | None
    conflict_subject: str | None
    merge: MergePreview | None


@dataclass(frozen=True)
class ReleasePlan:
    """Complete deterministic plan emitted by the release planner."""

    repository: str
    git_version: str
    branch: str
    branch_oid: str
    main_branch: str
    integration_branch: str | None
    mode: ReleaseMode
    action: ReleaseAction
    scope: str
    commits: tuple[CommitSummary, ...]
    operations: tuple[str, ...]
    feature_base: str | None = None
    feature_parent_refs: tuple[str, ...] = ()
    boundary_evidence: str | None = None
    boundary_candidates: tuple[BoundaryCandidate, ...] = ()
    containing_release_tags: tuple[str, ...] = ()
    merge_preview: MergePreview | None = None
    rebase_preview: RebasePreview | None = None
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the plan."""
        return asdict(self)


class ReleasePlanError(RuntimeError):
    """Raised when repository evidence cannot produce a valid plan."""


# eof
