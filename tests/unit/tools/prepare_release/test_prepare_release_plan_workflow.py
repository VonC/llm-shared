"""Branch-role and operation selection tests for the release planner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_models import ReleaseAction, ReleaseMode
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

from .prepare_release_plan_test_support import commit_file, git, initialize_repository

if TYPE_CHECKING:
    from pathlib import Path


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


# eof
