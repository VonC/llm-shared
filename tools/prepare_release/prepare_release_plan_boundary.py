"""Resolve exact feature boundaries from Git topology and reflog evidence."""

# Planner errors intentionally include the rejected refs at the raise site.
# ruff: noqa: EM102, TRY003

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_models import (
    BoundaryCandidate,
    ReleasePlanError,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tools.prepare_release.prepare_release_plan_git import GitRepository

_REBASE_ONTO_RE = re.compile(r"\brebase.*\bonto\s+([0-9a-f]{7,40})\b", re.IGNORECASE)
_RESET_TARGET_RE = re.compile(r"reset: moving to (.+)$")
_CREATED_FROM_RE = re.compile(r"branch: Created from (.+)$")
_MIN_MERGE_PARENTS = 2


@dataclass(frozen=True)
class _RankedBoundary:
    candidate: BoundaryCandidate
    priority: int


def resolve_feature_boundary(
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
        if base != branch_tip and repository.is_ancestor(base, branch):
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


# eof
