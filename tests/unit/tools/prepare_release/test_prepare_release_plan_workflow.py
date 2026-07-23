"""Branch-role and operation selection tests for the release planner.

Fix: cover the remaining planning branches for the coverage gate: the
boundary-less orphan branch, merges inside an explicit feature scope, the
direct-merge conflict preview, explicit `--feature-parent` boundaries (a
first-parent merge success and an underivable failure), an explicit base
that is not a proper ancestor, rebase and reset reflog evidence, and the
ambiguity path where deduplicated parent candidates elect a unique nearest
boundary with reflogs disabled.
"""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import pytest

from tools.prepare_release.prepare_release_plan_models import (
    ReleaseAction,
    ReleaseMode,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

from .prepare_release_plan_test_support import commit_file, git, initialize_repository

if TYPE_CHECKING:
    from pathlib import Path

_EXPECTED_CANDIDATES = 2


def test_plan_on_main_prepares_in_place(tmp_path: Path) -> None:
    """Starting from main never proposes a rebase or branch merge."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    commit_file(repo, "main.txt", "main\n", "feat: release work")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.mode is ReleaseMode.ON_MAIN
    assert plan.action is ReleaseAction.PREPARE_IN_PLACE
    assert plan.scope == "v1.0.0..main"
    assert plan.operations == ("prepare version and release notes in place",)


def test_plan_integration_merges_no_ff_when_it_contains_main(tmp_path: Path) -> None:
    """A current integration branch is promoted directly with --no-ff."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    commit_file(repo, "develop.txt", "develop\n", "feat: integrated work")
    git(repo, "switch", "main")

    plan = build_release_plan(repo, branch="develop", integration_branch="develop")

    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True
    assert plan.operations[0] == "git switch --ignore-other-worktrees main"
    assert plan.operations[-1] == "git merge --no-ff develop"


def test_plan_uses_configured_integration_role(tmp_path: Path) -> None:
    """Repository config can name a non-develop integration branch."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "next")
    commit_file(repo, "next.txt", "next\n", "feat: integrated work")
    git(repo, "config", "prepare-release.integrationBranch", "next")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.integration_branch == "next"
    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF


def test_plan_integration_previews_main_sync_conflict(tmp_path: Path) -> None:
    """A stale integration branch previews the main-into-integration sync first."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    commit_file(repo, "shared.txt", "develop\n", "feat: develop change")
    git(repo, "switch", "main")
    commit_file(repo, "shared.txt", "main\n", "fix: main change")

    plan = build_release_plan(repo, branch="develop", integration_branch="develop")

    assert plan.action is ReleaseAction.SYNC_INTEGRATION_THEN_MERGE
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is False
    assert plan.merge_preview.conflicted_files == ("shared.txt",)
    assert plan.operations[1] == "git merge --no-ff main"


def test_plan_nested_feature_uses_exact_onto_replay(tmp_path: Path) -> None:
    """A feature forked from develop replays only commits after that fork."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    develop_tip = commit_file(repo, "parent.txt", "develop\n", "feat: parent work")
    git(repo, "switch", "-c", "feature")
    feature_tip = commit_file(repo, "feature.txt", "feature\n", "feat: selected work")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")

    plan = build_release_plan(
        repo,
        branch="feature",
        integration_branch="develop",
        feature_base=develop_tip,
    )

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE
    assert plan.feature_base == develop_tip
    assert [commit.oid for commit in plan.commits] == [feature_tip]
    assert plan.rebase_preview is not None
    assert plan.rebase_preview.clean is True
    assert plan.operations[1].startswith(f"git rebase --onto main {develop_tip}")


def test_plan_auto_detects_branch_creation_boundary(tmp_path: Path) -> None:
    """The latest branch-positioning reflog entry can prove the feature fork."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog:")


def test_plan_stops_feature_already_contained_by_release_tag(tmp_path: Path) -> None:
    """An old feature tip produces no empty replay when main already released it."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    feature_tip = commit_file(repo, "feature.txt", "feature\n", "feat: feature")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "feature", "-m", "merge feature")
    git(repo, "tag", "v1.1.0")

    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)

    assert plan.branch_oid == feature_tip
    assert plan.action is ReleaseAction.ALREADY_RELEASED
    assert plan.containing_release_tags == ("v1.1.0",)


def test_plan_orphan_branch_requires_a_boundary(tmp_path: Path) -> None:
    """A branch without provable topology stops instead of guessing a base."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "--orphan", "rescue")
    commit_file(repo, "orphan.txt", "orphan\n", "feat: unrelated history")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.boundary_candidates == ()
    assert plan.commits == ()
    assert any("--feature-base" in note for note in plan.notes)


def test_plan_flags_merges_inside_an_explicit_feature_scope(tmp_path: Path) -> None:
    """A feature range containing a merge asks for explicit commit selection."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "-c", "side")
    commit_file(repo, "side.txt", "side\n", "feat: side change")
    git(repo, "switch", "feature")
    git(repo, "merge", "--no-ff", "side", "-m", "merge side")

    plan = build_release_plan(
        repo,
        branch="feature",
        feature_base=base,
        preview_conflicts=False,
    )

    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.feature_base == base
    assert plan.commits != ()
    assert any("contains merges" in note for note in plan.notes)


def test_plan_direct_merge_previews_conflicts(tmp_path: Path) -> None:
    """A feature still rooted at the main tip previews the merge itself."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")

    plan = build_release_plan(repo)

    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True


def test_plan_explicit_parent_uses_the_first_parent_merge_boundary(
    tmp_path: Path,
) -> None:
    """A parent branch that merged the feature proves the fork point."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "-c", "develop", "main")
    git(repo, "merge", "--no-ff", "feature", "-m", "merge feature")

    plan = build_release_plan(
        repo,
        branch="feature",
        feature_parent="develop",
        preview_conflicts=False,
    )

    assert plan.feature_base == base
    assert plan.boundary_evidence == "first-parent merge into develop"
    assert plan.action is ReleaseAction.MERGE_NO_FF


def test_plan_explicit_parent_without_a_boundary_fails(tmp_path: Path) -> None:
    """A parent giving no derivable fork point raises instead of guessing."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "branch", "twin", "feature")

    with pytest.raises(ReleasePlanError, match="Could not derive a boundary"):
        build_release_plan(
            repo,
            branch="feature",
            feature_parent="twin",
            preview_conflicts=False,
        )


def test_plan_explicit_base_must_be_a_proper_ancestor(tmp_path: Path) -> None:
    """The branch tip itself is rejected as its own feature base."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")

    with pytest.raises(ReleasePlanError, match="not a proper ancestor of feature"):
        build_release_plan(
            repo,
            branch="feature",
            feature_base="feature",
            preview_conflicts=False,
        )


def test_plan_rebased_feature_uses_the_reflog_onto_evidence(tmp_path: Path) -> None:
    """A completed rebase leaves the exact new base in the branch reflog."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "main")
    main_tip = commit_file(repo, "main.txt", "main\n", "fix: main work")
    git(repo, "rebase", "main", "feature")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.feature_base == main_tip
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog: rebase")
    assert plan.action is ReleaseAction.MERGE_NO_FF


def test_plan_reset_reflog_entry_wins_as_latest_evidence(tmp_path: Path) -> None:
    """The newest branch-positioning entry supersedes the creation entry."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: discarded work")
    git(repo, "reset", "--hard", "main")
    commit_file(repo, "feature.txt", "again\n", "feat: kept work")

    plan = build_release_plan(repo, preview_conflicts=False)

    assert plan.feature_base == base
    assert plan.feature_parent_refs == ("main",)
    assert plan.boundary_evidence == "reflog: reset: moving to main"


def test_plan_single_parent_candidate_is_selected_without_ranking(
    tmp_path: Path,
) -> None:
    """One surviving parent candidate is the boundary without a nearest vote."""
    repo = tmp_path / "repo"
    base = initialize_repository(repo)
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")
    shutil.rmtree(repo / ".git" / "logs")

    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)

    assert plan.feature_base == base
    assert plan.boundary_evidence == "merge-base main feature"
    (candidate,) = plan.boundary_candidates
    assert candidate.parent_refs == ("main",)
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE


def test_plan_ambiguous_parents_select_the_unique_nearest_boundary(
    tmp_path: Path,
) -> None:
    """Without reflogs, deduplicated candidates elect the nearest fork point."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "develop")
    fork_point = commit_file(repo, "parent.txt", "develop\n", "feat: parent work")
    git(repo, "switch", "-c", "feature")
    commit_file(repo, "feature.txt", "feature\n", "feat: feature change")
    # Advance develop and main past the fork and drop every reflog, so no
    # fork-point or branch-creation answer survives and the planner must
    # weigh plain merge-base candidates from every parent branch.
    git(repo, "switch", "develop")
    commit_file(repo, "parent.txt", "develop again\n", "feat: later parent work")
    git(repo, "switch", "main")
    commit_file(repo, "main.txt", "main\n", "fix: main work")
    git(repo, "branch", "other", "main")
    shutil.rmtree(repo / ".git" / "logs")

    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)

    assert plan.feature_base == fork_point
    assert plan.feature_parent_refs == ("develop",)
    assert len(plan.boundary_candidates) == _EXPECTED_CANDIDATES
    # The two same-base candidates from main and other merge into one entry.
    assert plan.boundary_candidates[1].parent_refs == ("main", "other")
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE


# eof
