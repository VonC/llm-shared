"""Branch-role detection and operation planning for prepare-release."""

# Planner errors intentionally include the rejected refs at the raise site.
# ruff: noqa: EM102, TRY003

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_git import GitRepository
from tools.prepare_release.prepare_release_plan_models import (
    BoundaryCandidate,
    ReleaseAction,
    ReleaseMode,
    ReleasePlan,
    ReleasePlanError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

_REBASE_ONTO_RE = re.compile(r"\brebase.*\bonto\s+([0-9a-f]{7,40})\b", re.IGNORECASE)
_RESET_TARGET_RE = re.compile(r"reset: moving to (.+)$")
_CREATED_FROM_RE = re.compile(r"branch: Created from (.+)$")
_MIN_MERGE_PARENTS = 2


@dataclass(frozen=True)
class _RankedBoundary:
    candidate: BoundaryCandidate
    priority: int


def build_release_plan(  # noqa: PLR0913
    root: Path,
    *,
    main_branch: str = "main",
    integration_branch: str | None = None,
    branch: str | None = None,
    feature_base: str | None = None,
    feature_parent: str | None = None,
    preview_conflicts: bool = True,
) -> ReleasePlan:
    """Build a deterministic release plan from local repository evidence."""
    repository = GitRepository(root)
    repository.verify_repository()
    git_version = repository.assert_supported_version()
    selected_branch = branch or repository.current_branch()
    selected_oid = repository.resolve(selected_branch)
    repository.resolve(main_branch)
    resolved_integration = _resolve_integration_branch(
        repository,
        integration_branch,
        main_branch=main_branch,
    )

    if selected_branch == main_branch:
        return _plan_on_main(repository, git_version, selected_branch, main_branch, resolved_integration)
    if resolved_integration is not None and selected_branch == resolved_integration:
        return _plan_integration(
            repository,
            git_version,
            selected_branch,
            selected_oid,
            main_branch,
            resolved_integration,
            preview_conflicts=preview_conflicts,
        )
    return _plan_feature(
        repository,
        git_version,
        selected_branch,
        selected_oid,
        main_branch,
        resolved_integration,
        feature_base=feature_base,
        feature_parent=feature_parent,
        preview_conflicts=preview_conflicts,
    )


def _resolve_integration_branch(
    repository: GitRepository,
    requested: str | None,
    *,
    main_branch: str,
) -> str | None:
    """Resolve integration via CLI, environment, config, develop, then origin HEAD."""
    candidates = (
        requested,
        os.environ.get("PREPARE_RELEASE_INTEGRATION_BRANCH"),
        repository.config_value("prepare-release.integrationBranch"),
        repository.config_value("release.integrationBranch"),
        "develop" if repository.branch_exists("develop") else None,
        repository.remote_default_branch(),
    )
    return next(
        (candidate for candidate in candidates if candidate and candidate != main_branch),
        None,
    )


def _plan_on_main(
    repository: GitRepository,
    git_version: str,
    branch: str,
    main_branch: str,
    integration_branch: str | None,
) -> ReleasePlan:
    tag = repository.latest_tag(main_branch)
    scope = f"{tag}..{main_branch}" if tag else main_branch
    return ReleasePlan(
        repository=str(repository.root),
        git_version=git_version,
        branch=branch,
        branch_oid=repository.resolve(branch),
        main_branch=main_branch,
        integration_branch=integration_branch,
        mode=ReleaseMode.ON_MAIN,
        action=ReleaseAction.PREPARE_IN_PLACE,
        scope=scope,
        commits=repository.commits(scope),
        operations=("prepare version and release notes in place",),
        notes=("No rebase and no branch merge are required.",),
    )


def _plan_integration(  # noqa: PLR0913
    repository: GitRepository,
    git_version: str,
    branch: str,
    branch_oid: str,
    main_branch: str,
    integration_branch: str,
    *,
    preview_conflicts: bool,
) -> ReleasePlan:
    scope = f"{main_branch}..{branch}"
    contains_main = repository.is_ancestor(main_branch, branch)
    if contains_main:
        action = ReleaseAction.MERGE_NO_FF
        operations = (
            f"git switch --ignore-other-worktrees {main_branch}",
            f"git merge --no-ff {branch}",
        )
        preview_destination, preview_source = main_branch, branch
    else:
        action = ReleaseAction.SYNC_INTEGRATION_THEN_MERGE
        operations = (
            f"git switch {branch}",
            f"git merge --no-ff {main_branch}",
            "run ghog day",
            f"git switch --ignore-other-worktrees {main_branch}",
            f"git merge --no-ff {branch}",
        )
        preview_destination, preview_source = branch, main_branch
    merge_preview = None
    if preview_conflicts:
        with repository.isolated_object_environment() as env:
            merge_preview = repository.preview_merge(
                preview_destination,
                preview_source,
                env=env,
            )
    note = (
        f"Conflict preview models merging {preview_source} into {preview_destination}."
        if preview_conflicts
        else "Conflict preview was skipped."
    )
    return ReleasePlan(
        repository=str(repository.root),
        git_version=git_version,
        branch=branch,
        branch_oid=branch_oid,
        main_branch=main_branch,
        integration_branch=integration_branch,
        mode=ReleaseMode.INTEGRATION,
        action=action,
        scope=scope,
        commits=repository.commits(scope),
        operations=operations,
        merge_preview=merge_preview,
        notes=(note, "The long-lived integration branch is never rebased."),
    )


def _plan_feature(  # noqa: PLR0913
    repository: GitRepository,
    git_version: str,
    branch: str,
    branch_oid: str,
    main_branch: str,
    integration_branch: str | None,
    *,
    feature_base: str | None,
    feature_parent: str | None,
    preview_conflicts: bool,
) -> ReleasePlan:
    if repository.is_ancestor(branch, main_branch):
        tags = repository.tags_containing(branch)
        action = (
            ReleaseAction.ALREADY_RELEASED if tags else ReleaseAction.ALREADY_INTEGRATED
        )
        note = (
            f"Branch tip is already contained by release tag {tags[0]}."
            if tags
            else "Branch tip is already in main; invoke from main only to release all main changes."
        )
        return ReleasePlan(
            repository=str(repository.root),
            git_version=git_version,
            branch=branch,
            branch_oid=branch_oid,
            main_branch=main_branch,
            integration_branch=integration_branch,
            mode=ReleaseMode.FEATURE,
            action=action,
            scope=f"{branch}..{main_branch}",
            commits=(),
            operations=(),
            containing_release_tags=tags,
            notes=(note,),
        )

    boundary, candidates = _resolve_feature_boundary(
        repository,
        branch,
        explicit_base=feature_base,
        explicit_parent=feature_parent,
    )
    if boundary is None:
        return ReleasePlan(
            repository=str(repository.root),
            git_version=git_version,
            branch=branch,
            branch_oid=branch_oid,
            main_branch=main_branch,
            integration_branch=integration_branch,
            mode=ReleaseMode.FEATURE,
            action=ReleaseAction.NEEDS_FEATURE_BOUNDARY,
            scope=f"<feature-base>..{branch}",
            commits=(),
            operations=(),
            boundary_candidates=candidates,
            notes=(
                "Select --feature-base or --feature-parent; the planner will not guess.",
            ),
        )

    scope = f"{boundary.base}..{branch}"
    if repository.contains_merge(scope):
        return ReleasePlan(
            repository=str(repository.root),
            git_version=git_version,
            branch=branch,
            branch_oid=branch_oid,
            main_branch=main_branch,
            integration_branch=integration_branch,
            mode=ReleaseMode.FEATURE,
            action=ReleaseAction.NEEDS_FEATURE_BOUNDARY,
            scope=scope,
            commits=repository.commits(scope),
            operations=(),
            feature_base=boundary.base,
            feature_parent_refs=boundary.parent_refs,
            boundary_evidence=boundary.evidence,
            boundary_candidates=candidates,
            notes=("The selected feature range contains merges; select commits explicitly.",),
        )

    commits = repository.commits(scope)
    direct_merge = repository.is_ancestor(boundary.base, main_branch) and repository.is_ancestor(
        main_branch, branch,
    )
    if direct_merge:
        merge_preview = None
        if preview_conflicts:
            with repository.isolated_object_environment() as env:
                merge_preview = repository.preview_merge(main_branch, branch, env=env)
        return ReleasePlan(
            repository=str(repository.root),
            git_version=git_version,
            branch=branch,
            branch_oid=branch_oid,
            main_branch=main_branch,
            integration_branch=integration_branch,
            mode=ReleaseMode.FEATURE,
            action=ReleaseAction.MERGE_NO_FF,
            scope=scope,
            commits=commits,
            operations=(
                f"git switch --ignore-other-worktrees {main_branch}",
                f"git merge --no-ff {branch}",
            ),
            feature_base=boundary.base,
            feature_parent_refs=boundary.parent_refs,
            boundary_evidence=boundary.evidence,
            boundary_candidates=candidates,
            merge_preview=merge_preview,
            notes=("Original feature branch can be merged without replay.",),
        )

    promotion = _promotion_branch_name(branch)
    rebase_preview = (
        repository.preview_rebase(boundary.base, branch, main_branch)
        if preview_conflicts
        else None
    )
    return ReleasePlan(
        repository=str(repository.root),
        git_version=git_version,
        branch=branch,
        branch_oid=branch_oid,
        main_branch=main_branch,
        integration_branch=integration_branch,
        mode=ReleaseMode.FEATURE,
        action=ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE,
        scope=scope,
        commits=commits,
        operations=(
            f"git branch {promotion} {branch}",
            f"git rebase --onto {main_branch} {boundary.base} {promotion}",
            "run git range-diff and ghog day",
            f"git switch --ignore-other-worktrees {main_branch}",
            f"git merge --no-ff {promotion}",
        ),
        feature_base=boundary.base,
        feature_parent_refs=boundary.parent_refs,
        boundary_evidence=boundary.evidence,
        boundary_candidates=candidates,
        rebase_preview=rebase_preview,
        notes=(
            "Rebase preview stops at the first conflicting commit; later conflicts depend on its resolution.",
            "The original feature branch remains unchanged.",
        ),
    )


def _resolve_feature_boundary(
    repository: GitRepository,
    branch: str,
    *,
    explicit_base: str | None,
    explicit_parent: str | None,
) -> tuple[BoundaryCandidate | None, tuple[BoundaryCandidate, ...]]:
    """Return a proven feature boundary, or candidates requiring user selection."""
    if explicit_base is not None:
        return _explicit_base_boundary(repository, branch, explicit_base)

    if explicit_parent is not None:
        return _explicit_parent_boundary(repository, branch, explicit_parent)

    return _automatic_boundary(repository, branch)


def _explicit_base_boundary(
    repository: GitRepository,
    branch: str,
    explicit_base: str,
) -> tuple[BoundaryCandidate, tuple[BoundaryCandidate, ...]]:
    """Validate and return a caller-selected boundary commit."""
    base = repository.resolve(explicit_base)
    if not repository.is_ancestor(base, branch) or base == repository.resolve(branch):
        raise ReleasePlanError(f"Feature base {explicit_base} is not a proper ancestor of {branch}.")
    candidate = BoundaryCandidate(
        base=base,
        parent_refs=(),
        evidence="explicit --feature-base",
        commit_count=repository.commit_count(f"{base}..{branch}"),
    )
    return candidate, (candidate,)


def _explicit_parent_boundary(
    repository: GitRepository,
    branch: str,
    explicit_parent: str,
) -> tuple[BoundaryCandidate, tuple[BoundaryCandidate, ...]]:
    """Derive and return a boundary from a caller-selected parent branch."""
    repository.resolve(explicit_parent)
    ranked = _boundary_from_parent(repository, branch, explicit_parent)
    if ranked is None:
        raise ReleasePlanError(
            f"Could not derive a boundary between {explicit_parent} and {branch}.",
        )
    return ranked.candidate, (ranked.candidate,)


def _automatic_boundary(
    repository: GitRepository,
    branch: str,
) -> tuple[BoundaryCandidate | None, tuple[BoundaryCandidate, ...]]:
    """Resolve a boundary from reflog and local branch topology evidence."""
    reflog_boundary = _boundary_from_reflog(repository, branch)
    if reflog_boundary is not None:
        return reflog_boundary, (reflog_boundary,)

    ranked = [
        candidate
        for parent in repository.local_branches()
        if parent != branch
        for candidate in [_boundary_from_parent(repository, branch, parent)]
        if candidate is not None
    ]
    candidates = _deduplicate_candidates(ranked)
    if len(candidates) == 1:
        return candidates[0], candidates
    nearest = _unique_nearest_candidate(repository, candidates)
    return nearest, candidates


def _boundary_from_reflog(
    repository: GitRepository,
    branch: str,
) -> BoundaryCandidate | None:
    """Use the latest unsuperseded branch-positioning reflog entry."""
    selected: tuple[str, str, tuple[str, ...]] | None = None
    local_branches = set(repository.local_branches())
    branch_tip = repository.resolve(branch)
    for entry_oid, subject in repository.reflog(branch):
        parsed = _parse_positioning_entry(
            repository,
            entry_oid,
            subject,
            local_branches,
        )
        if parsed is None:
            continue
        base, evidence, parents = parsed
        if (
            base != branch_tip
            and repository.is_ancestor(base, branch)
        ):
            selected = (base, evidence, parents)
    if selected is None:
        return None
    base, evidence, parents = selected
    return BoundaryCandidate(
        base=base,
        parent_refs=parents,
        evidence=evidence,
        commit_count=repository.commit_count(f"{base}..{branch}"),
    )


def _parse_positioning_entry(
    repository: GitRepository,
    entry_oid: str,
    subject: str,
    local_branches: set[str],
) -> tuple[str, str, tuple[str, ...]] | None:
    """Parse one branch-creation, reset, or completed-rebase reflog entry."""
    rebase_match = _REBASE_ONTO_RE.search(subject)
    if rebase_match:
        return repository.resolve(rebase_match.group(1)), f"reflog: {subject}", ()
    target = _positioning_target(subject)
    if target is None:
        return None
    parents = (target,) if target in local_branches else ()
    return entry_oid, f"reflog: {subject}", parents


def _positioning_target(subject: str) -> str | None:
    """Return a reset/creation target label from one reflog subject."""
    reset_match = _RESET_TARGET_RE.search(subject)
    if reset_match:
        return reset_match.group(1)
    created_match = _CREATED_FROM_RE.search(subject)
    return created_match.group(1) if created_match else None


def _boundary_from_parent(
    repository: GitRepository,
    branch: str,
    parent: str,
) -> _RankedBoundary | None:
    """Derive one boundary candidate from a possible parent branch."""
    branch_tip = repository.resolve(branch)
    if repository.is_ancestor(branch, parent):
        base = _introduced_feature_base(repository, branch_tip, parent)
        evidence = f"first-parent merge into {parent}"
        priority = 3
    else:
        base = repository.merge_base(parent, branch, fork_point=True)
        evidence = f"merge-base --fork-point {parent} {branch}"
        priority = 2
        if base is None:
            base = repository.merge_base(parent, branch)
            evidence = f"merge-base {parent} {branch}"
            priority = 1
    if base is None or base == branch_tip or not repository.is_ancestor(base, branch):
        return None
    return _RankedBoundary(
        candidate=BoundaryCandidate(
            base=base,
            parent_refs=(parent,),
            evidence=evidence,
            commit_count=repository.commit_count(f"{base}..{branch}"),
        ),
        priority=priority,
    )


def _introduced_feature_base(
    repository: GitRepository,
    branch_tip: str,
    containing_branch: str,
) -> str | None:
    """Find the first first-parent merge that introduced a feature tip."""
    for commit in repository.first_parent_history(containing_branch):
        parents = repository.commit_parents(commit)
        if len(parents) < _MIN_MERGE_PARENTS:
            continue
        if repository.is_ancestor(branch_tip, commit) and not repository.is_ancestor(
            branch_tip, parents[0],
        ):
            return repository.merge_base(branch_tip, parents[0])
    return None


def _deduplicate_candidates(
    ranked: Sequence[_RankedBoundary],
) -> tuple[BoundaryCandidate, ...]:
    """Keep highest-quality evidence and combine parent refs per base."""
    if not ranked:
        return ()
    highest = max(item.priority for item in ranked)
    by_base: dict[str, list[_RankedBoundary]] = {}
    for item in ranked:
        if item.priority == highest:
            by_base.setdefault(item.candidate.base, []).append(item)
    result: list[BoundaryCandidate] = []
    for base, items in by_base.items():
        parent_refs = tuple(
            sorted({parent for item in items for parent in item.candidate.parent_refs}),
        )
        evidence = "; ".join(sorted({item.candidate.evidence for item in items}))
        result.append(
            BoundaryCandidate(
                base=base,
                parent_refs=parent_refs,
                evidence=evidence,
                commit_count=items[0].candidate.commit_count,
            ),
        )
    return tuple(sorted(result, key=lambda item: (item.commit_count, item.base)))


def _unique_nearest_candidate(
    repository: GitRepository,
    candidates: Sequence[BoundaryCandidate],
) -> BoundaryCandidate | None:
    """Select a unique candidate descended from every other candidate."""
    nearest = [
        candidate
        for candidate in candidates
        if all(
            other.base == candidate.base or repository.is_ancestor(other.base, candidate.base)
            for other in candidates
        )
    ]
    return nearest[0] if len(nearest) == 1 else None


def _promotion_branch_name(branch: str) -> str:
    """Return a valid suggested promotion branch name without creating it."""
    sanitized = re.sub(r"[^A-Za-z0-9._/-]+", "-", branch).strip("-./")
    return f"prepare-release/{sanitized}-onto-main"


# eof
