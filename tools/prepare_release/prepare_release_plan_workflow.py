"""Branch-role detection and operation planning for prepare-release."""

# Planner errors intentionally include the rejected refs at the raise site.
# ruff: noqa: EM102, TRY003

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_boundary import resolve_feature_boundary
from tools.prepare_release.prepare_release_plan_git import GitRepository
from tools.prepare_release.prepare_release_plan_models import (
    ReleaseAction,
    ReleaseMode,
    ReleasePlan,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_naming import promotion_branch_name
from tools.prepare_release.prepare_release_plan_umbrella import (
    resolve_umbrella_integration,
    slug_key,
)

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class _FeaturePlanContext:
    repository: GitRepository
    git_version: str
    branch: str
    branch_oid: str
    main_branch: str
    integration_branch: str | None


def build_release_plan(  # noqa: PLR0913
    root: Path,
    *,
    main_branch: str = "main",
    integration_branch: str | None = None,
    umbrella: Path | None = None,
    branch: str | None = None,
    feature_base: str | None = None,
    feature_parent: str | None = None,
    feature_target: str = "auto",
    preview_conflicts: bool = True,
) -> ReleasePlan:
    """Build a deterministic release plan from local repository evidence."""
    repository = GitRepository(root)
    repository.verify_repository()
    git_version = repository.assert_supported_version()
    selected_branch = branch or repository.current_branch()
    selected_oid = repository.resolve(selected_branch)
    repository.resolve(main_branch)
    umbrella_integration = resolve_umbrella_integration(repository, umbrella)
    resolved_integration = _resolve_integration_branch(
        repository,
        integration_branch,
        umbrella_branch=umbrella_integration,
        main_branch=main_branch,
    )

    if selected_branch == main_branch:
        return _plan_on_main(
            repository,
            git_version,
            selected_oid,
            main_branch,
            resolved_integration,
        )
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
        feature_target=feature_target,
        umbrella_bound=umbrella_integration is not None,
        preview_conflicts=preview_conflicts,
    )


def _resolve_integration_branch(
    repository: GitRepository,
    requested: str | None,
    *,
    umbrella_branch: str | None,
    main_branch: str,
) -> str | None:
    """Resolve umbrella integration first, then generic repository roles."""
    if umbrella_branch is not None:
        if requested is not None and slug_key(requested) != slug_key(umbrella_branch):
            raise ReleasePlanError(
                f"Requested integration branch {requested!r} conflicts with umbrella "
                f"integration branch {umbrella_branch!r}.",
            )
        return umbrella_branch
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
    branch_oid: str,
    main_branch: str,
    integration_branch: str | None,
) -> ReleasePlan:
    tag = repository.latest_tag(main_branch)
    scope = f"{tag}..{main_branch}" if tag else main_branch
    return ReleasePlan(
        repository=str(repository.root),
        git_version=git_version,
        branch=main_branch,
        branch_oid=branch_oid,
        main_branch=main_branch,
        integration_branch=integration_branch,
        feature_target_branch=None,
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
        feature_target_branch=None,
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
    feature_target: str,
    umbrella_bound: bool,
    preview_conflicts: bool,
) -> ReleasePlan:
    target_branch = _feature_target(
        main_branch,
        integration_branch,
        feature_target,
        umbrella_bound=umbrella_bound,
    )
    context = _FeaturePlanContext(
        repository,
        git_version,
        branch,
        branch_oid,
        main_branch,
        integration_branch,
    )
    integrated = _already_integrated_feature(context, target_branch)
    if integrated is not None:
        return integrated

    boundary, candidates = resolve_feature_boundary(
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
            feature_target_branch=target_branch,
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
            feature_target_branch=target_branch,
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
    direct_merge = repository.is_ancestor(
        boundary.base,
        target_branch,
    ) and repository.is_ancestor(target_branch, branch)
    if direct_merge:
        merge_preview = None
        if preview_conflicts:
            with repository.isolated_object_environment() as env:
                merge_preview = repository.preview_merge(target_branch, branch, env=env)
        return ReleasePlan(
            repository=str(repository.root),
            git_version=git_version,
            branch=branch,
            branch_oid=branch_oid,
            main_branch=main_branch,
            integration_branch=integration_branch,
            feature_target_branch=target_branch,
            mode=ReleaseMode.FEATURE,
            action=ReleaseAction.MERGE_NO_FF,
            scope=scope,
            commits=commits,
            operations=(
                f"git switch --ignore-other-worktrees {target_branch}",
                f"git merge --no-ff {branch}",
            ),
            feature_base=boundary.base,
            feature_parent_refs=boundary.parent_refs,
            boundary_evidence=boundary.evidence,
            boundary_candidates=candidates,
            merge_preview=merge_preview,
            notes=("Original feature branch can be merged without replay.",),
        )

    promotion = promotion_branch_name(branch, target_branch)
    rebase_preview = (
        repository.preview_rebase(boundary.base, branch, target_branch)
        if preview_conflicts
        else None
    )
    rebase_action = (
        ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE
        if target_branch == main_branch
        else ReleaseAction.REBASE_ONTO_INTEGRATION_THEN_MERGE
    )
    return ReleasePlan(
        repository=str(repository.root),
        git_version=git_version,
        branch=branch,
        branch_oid=branch_oid,
        main_branch=main_branch,
        integration_branch=integration_branch,
        feature_target_branch=target_branch,
        mode=ReleaseMode.FEATURE,
        action=rebase_action,
        scope=scope,
        commits=commits,
        operations=(
            f"git branch {promotion} {branch}",
            f"git rebase --onto {target_branch} {boundary.base} {promotion}",
            "run git range-diff and ghog day",
            f"git switch --ignore-other-worktrees {target_branch}",
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


def _feature_target(
    main_branch: str,
    integration_branch: str | None,
    feature_target: str,
    *,
    umbrella_bound: bool,
) -> str:
    """Resolve and validate the branch receiving a feature."""
    if feature_target not in {"auto", "main", "integration"}:
        raise ReleasePlanError(
            f"Unknown feature target {feature_target!r}; use 'auto', 'main', or 'integration'.",
        )
    if umbrella_bound and feature_target == "main":
        message = "A topic with an umbrella integration branch cannot target main directly."
        raise ReleasePlanError(message)
    if feature_target == "auto":
        return integration_branch or main_branch
    if feature_target == "integration":
        if integration_branch is None:
            message = (
                "Feature target 'integration' requires a resolved integration branch."
            )
            raise ReleasePlanError(message)
        return integration_branch
    return main_branch


def _already_integrated_feature(
    context: _FeaturePlanContext,
    target_branch: str,
) -> ReleasePlan | None:
    """Return the terminal plan when the feature is already integrated."""
    if not context.repository.is_ancestor(context.branch, target_branch):
        return None
    tags = (
        context.repository.tags_containing(context.branch)
        if target_branch == context.main_branch
        else ()
    )
    action = ReleaseAction.ALREADY_RELEASED if tags else ReleaseAction.ALREADY_INTEGRATED
    note = (
        f"Branch tip is already contained by release tag {tags[0]}."
        if tags
        else f"Branch tip is already integrated into {target_branch}."
    )
    return ReleasePlan(
        repository=str(context.repository.root),
        git_version=context.git_version,
        branch=context.branch,
        branch_oid=context.branch_oid,
        main_branch=context.main_branch,
        integration_branch=context.integration_branch,
        feature_target_branch=target_branch,
        mode=ReleaseMode.FEATURE,
        action=action,
        scope=f"{context.branch}..{target_branch}",
        commits=(),
        operations=(),
        containing_release_tags=tags,
        notes=(note,),
    )


# eof
