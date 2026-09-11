"""Planner tests for feature destinations and umbrella integration branches."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.prepare_release import prepare_release_plan_workflow as workflow
from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    ReleaseAction,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

from .prepare_release_plan_test_support import (
    commit_file,
    git,
    initialize_repository,
    repository_for,
)


@pytest.fixture(autouse=True)
def recorded_workflow_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run workflow decisions against the synthetic Git topology."""
    monkeypatch.setattr(workflow, "GitRepository", repository_for)


class _FeatureRepositoryStub:
    """In-memory topology for feature-target selection tests."""

    def __init__(
        self,
        root: Path,
        *,
        integration_exists: bool,
        integration_contains_feature: bool = False,
    ) -> None:
        self.root = root
        self.integration_exists = integration_exists
        self.integration_contains_feature = integration_contains_feature

    def verify_repository(self) -> None:
        """Accept the synthetic repository."""

    def assert_supported_version(self) -> str:
        """Return a supported version without launching Git."""
        return "2.50.0"

    def current_branch(self) -> str:
        """Return the feature branch used by these tests."""
        return "feature"

    def resolve(self, ref: str) -> str:
        """Resolve the small synthetic ref set."""
        return {
            "main": "main-tip",
            "develop": "develop-current",
            "feature": "feature-tip",
        }.get(ref, ref)

    def config_value(self, _key: str) -> None:
        """Return no configured integration branch."""

    def branch_exists(self, branch: str) -> bool:
        """Expose develop only in integration-target scenarios."""
        return branch == "develop" and self.integration_exists

    def remote_default_branch(self) -> None:
        """Return no remote default branch."""

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Answer only the topology relationships the planner asks about."""
        pair = self.resolve(ancestor), self.resolve(descendant)
        ancestors = {
            ("develop-tip", "feature-tip"),
            ("develop-tip", "develop-current"),
        }
        if self.integration_contains_feature:
            ancestors.add(("develop-current", "feature-tip"))
        return pair in ancestors

    def commit_count(self, _revision_range: str) -> int:
        """Return the single selected feature commit."""
        return 1

    def contains_merge(self, _revision_range: str) -> bool:
        """The synthetic feature range is linear."""
        return False

    def commits(self, _revision_range: str) -> tuple[CommitSummary, ...]:
        """Return the selected feature commit."""
        return (CommitSummary(oid="feature-tip", subject="feat: selected work"),)


def _stub_feature_repository(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    integration_exists: bool,
    integration_contains_feature: bool = False,
) -> None:
    """Install one in-memory repository behind the public planner entry point."""
    repository = _FeatureRepositoryStub(
        tmp_path,
        integration_exists=integration_exists,
        integration_contains_feature=integration_contains_feature,
    )

    def repository_factory(_root: Path) -> _FeatureRepositoryStub:
        return repository

    monkeypatch.setattr(workflow, "GitRepository", repository_factory)


@pytest.fixture
def umbrella_feature_repository(tmp_path: Path) -> tuple[Path, Path]:
    """Prepare a topic whose umbrella slug names an underscore branch."""
    repo = tmp_path / "repo"
    initialize_repository(repo)
    git(repo, "switch", "-c", "review_mode")
    umbrella = repo / "docs/v0.11.0/draft.v0.11.0.review-mode.md"
    umbrella.parent.mkdir(parents=True)
    umbrella.write_text(
        "# Review mode\n\n- Draft role: umbrella\n",
        encoding="utf-8",
    )
    commit_file(
        repo,
        "docs/v0.11.0/draft.v0.11.0.review-mode.md",
        umbrella.read_text(encoding="utf-8"),
        "docs: record umbrella",
    )
    git(repo, "switch", "-c", "commit-plan-check")
    commit_file(repo, "feature.txt", "feature\n", "feat: selected work")
    return repo, umbrella.relative_to(repo)


def test_plan_umbrella_topic_targets_its_slug_integration_branch(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """A collection topic returns to its umbrella branch before main."""
    repo, umbrella = umbrella_feature_repository

    plan = build_release_plan(
        repo,
        branch="commit-plan-check",
        umbrella=umbrella,
        preview_conflicts=False,
    )

    assert plan.integration_branch == "review_mode"
    assert plan.feature_target_branch == "review_mode"
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.operations[-1] == "git merge --no-ff commit-plan-check"


def test_plan_umbrella_topic_rejects_an_explicit_main_target(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """Caller input cannot bypass a topic's declared collection branch."""
    repo, umbrella = umbrella_feature_repository

    with pytest.raises(ReleasePlanError, match="umbrella integration branch"):
        build_release_plan(
            repo,
            branch="commit-plan-check",
            umbrella=umbrella,
            feature_target="main",
            preview_conflicts=False,
        )


def test_plan_umbrella_topic_rejects_a_conflicting_integration_branch(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """An explicit generic integration cannot override the umbrella slug."""
    repo, umbrella = umbrella_feature_repository

    with pytest.raises(ReleasePlanError, match="conflicts with umbrella"):
        build_release_plan(
            repo,
            branch="commit-plan-check",
            umbrella=umbrella,
            integration_branch="develop",
            preview_conflicts=False,
        )


def test_plan_rejects_an_umbrella_outside_the_repository(
    umbrella_feature_repository: tuple[Path, Path],
    tmp_path: Path,
) -> None:
    """Umbrella evidence must belong to the planned repository."""
    repo, _umbrella = umbrella_feature_repository
    outside = tmp_path / "draft.v0.11.0.outside.md"

    with pytest.raises(ReleasePlanError, match="outside the repository"):
        build_release_plan(repo, umbrella=outside, preview_conflicts=False)


def test_plan_rejects_a_missing_umbrella(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """A missing declared umbrella cannot silently select a fallback branch."""
    repo, _umbrella = umbrella_feature_repository

    with pytest.raises(ReleasePlanError, match="does not exist"):
        build_release_plan(
            repo,
            umbrella=Path("docs/v0.11.0/draft.v0.11.0.missing.md"),
            preview_conflicts=False,
        )


def test_plan_rejects_a_draft_without_the_umbrella_role(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """A canonical name alone does not make a draft an umbrella."""
    repo, umbrella = umbrella_feature_repository
    (repo / umbrella).write_text("# Review mode\n", encoding="utf-8")

    with pytest.raises(ReleasePlanError, match="not marked as an umbrella"):
        build_release_plan(repo, umbrella=umbrella, preview_conflicts=False)


def test_plan_rejects_a_noncanonical_umbrella_filename(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """The integration slug must come from a canonical draft filename."""
    repo, _umbrella = umbrella_feature_repository
    umbrella = repo / "docs/v0.11.0/umbrella.md"
    umbrella.write_text("- Draft role: umbrella\n", encoding="utf-8")

    with pytest.raises(ReleasePlanError, match="no canonical slug"):
        build_release_plan(
            repo,
            umbrella=umbrella.relative_to(repo),
            preview_conflicts=False,
        )


def test_plan_rejects_an_umbrella_without_a_matching_branch(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """A missing slug branch stops instead of falling back to main."""
    repo, _umbrella = umbrella_feature_repository
    umbrella = repo / "docs/v0.11.0/draft.v0.11.0.missing.md"
    umbrella.write_text("- Draft role: umbrella\n", encoding="utf-8")

    with pytest.raises(ReleasePlanError, match="found none"):
        build_release_plan(
            repo,
            umbrella=umbrella.relative_to(repo),
            preview_conflicts=False,
        )


def test_plan_rejects_ambiguous_folded_umbrella_branches(
    umbrella_feature_repository: tuple[Path, Path],
) -> None:
    """Hyphen and underscore aliases cannot both claim one umbrella."""
    repo, umbrella = umbrella_feature_repository
    git(repo, "branch", "review-mode", "review_mode")

    with pytest.raises(ReleasePlanError, match="found review_mode, review-mode"):
        build_release_plan(repo, umbrella=umbrella, preview_conflicts=False)


def test_plan_feature_can_land_on_current_integration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Feature completion targets integration before release preparation."""
    _stub_feature_repository(
        monkeypatch,
        tmp_path,
        integration_exists=True,
        integration_contains_feature=True,
    )

    plan = build_release_plan(
        tmp_path,
        branch="feature",
        integration_branch="develop",
        feature_base="develop-tip",
        feature_target="integration",
        preview_conflicts=False,
    )

    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_target_branch == "develop"
    assert plan.operations == (
        "git switch --ignore-other-worktrees develop",
        "git merge --no-ff feature",
    )


def test_plan_stale_feature_replays_only_its_range_onto_integration(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An advanced integration branch gets an isolated feature replay."""
    _stub_feature_repository(
        monkeypatch,
        tmp_path,
        integration_exists=True,
    )

    plan = build_release_plan(
        tmp_path,
        branch="feature",
        integration_branch="develop",
        feature_base="develop-tip",
        feature_target="integration",
        preview_conflicts=False,
    )

    assert plan.action is ReleaseAction.REBASE_ONTO_INTEGRATION_THEN_MERGE
    assert [commit.oid for commit in plan.commits] == ["feature-tip"]
    assert plan.operations[1].startswith("git rebase --onto develop develop-tip")
    assert plan.operations[-2:] == (
        "git switch --ignore-other-worktrees develop",
        "git merge --no-ff prepare-release/feature-onto-develop",
    )


def test_plan_integration_target_requires_a_resolved_branch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The planner cannot silently substitute main for a requested integration."""
    _stub_feature_repository(monkeypatch, tmp_path, integration_exists=False)

    with pytest.raises(ReleasePlanError, match="requires a resolved integration"):
        build_release_plan(
            tmp_path,
            feature_target="integration",
            preview_conflicts=False,
        )


def test_plan_rejects_an_unknown_feature_target(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Direct API callers receive an actionable target validation error."""
    _stub_feature_repository(monkeypatch, tmp_path, integration_exists=False)

    with pytest.raises(ReleasePlanError, match="Unknown feature target"):
        build_release_plan(
            tmp_path,
            feature_target="qa",
            preview_conflicts=False,
        )


# eof
