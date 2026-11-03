"""Planner tests over declared branch, reflog, tag, and conflict observations.

Fix (v0.13.0 full_suite_levels, Step 2): the integration sync and the feature
replay name ``ghog day --full=cov``, since plain ``ghog day`` no longer runs
the full suite.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.prepare_release import prepare_release_plan_workflow as workflow
from tools.prepare_release.prepare_release_plan_models import (
    CommitSummary,
    MergePreview,
    ReleaseAction,
    ReleaseMode,
    ReleasePlanError,
)
from tools.prepare_release.prepare_release_plan_workflow import build_release_plan

from .prepare_release_plan_test_support import (
    BASE,
    MERGE,
    PARENT,
    TIP,
    declare_repository,
    repository_for,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prepare_release.prepare_release_plan_models import ReleasePlan

_EXPECTED_CANDIDATES = 2

@pytest.fixture(autouse=True)
def recorded_workflow_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """Run workflow decisions against declared repository observations."""
    monkeypatch.setattr(workflow, "GitRepository", repository_for)


@pytest.fixture
def integration_merge_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the synthetic integration merge plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs = {"main": BASE, "develop": TIP}
    facts.ranges["main..develop"] = (CommitSummary(TIP, "feat: integrated work"),)
    facts.merge_previews["main", "develop"] = MergePreview(clean=True, tree_oid="tree", conflicted_files=(), conflicts=())
    return build_release_plan(repo, branch="develop", integration_branch="develop")


@pytest.fixture
def integration_conflict_plan(tmp_path: Path) -> ReleasePlan:
    """Declare a divergent integration branch and its conflict observation."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs = {"main": PARENT, "develop": TIP}
    facts.ranges["main..develop"] = (CommitSummary(TIP, "feat: develop change"),)
    facts.merge_previews["develop", "main"] = MergePreview(clean=False, tree_oid="tree", conflicted_files=("shared.txt",), conflicts=())
    return build_release_plan(repo, branch="develop", integration_branch="develop")


@pytest.fixture
def explicit_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the first-parent boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["develop"] = MERGE
    facts.ancestors.add((TIP, MERGE))
    facts.histories["develop"] = (BASE, MERGE)
    facts.parents = {BASE: (), MERGE: (BASE, TIP)}
    facts.bases[TIP, BASE, False] = BASE
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_parent="develop",
        feature_target="main",
        preview_conflicts=False,
    )
    return BASE, plan


@pytest.fixture
def single_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the sole-parent boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["main"] = PARENT
    facts.reflogs.clear()
    facts.bases["main", "feature", False] = BASE
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_target="main",
        preview_conflicts=False,
    )
    return BASE, plan


@pytest.fixture
def ambiguous_parent_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the deduplicated-parent plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs = {"main": "5" * 40, "develop": MERGE, "feature": TIP, "other": "5" * 40}
    # No reflog or fork-point observation survives. The planner must rank
    # the declared merge bases and combine the same-base parent candidates.
    facts.reflogs.clear()
    facts.bases = {("main", "feature", False): BASE, ("other", "feature", False): BASE,
                   ("develop", "feature", False): PARENT}
    facts.ancestors.update({(BASE, PARENT), (PARENT, TIP)})
    facts.ranges[f"{BASE}..feature"] = (CommitSummary(PARENT, "feat: parent work"), CommitSummary(TIP, "feat: feature change"))
    facts.ranges[f"{PARENT}..feature"] = (CommitSummary(TIP, "feat: feature change"),)
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_target="main",
        preview_conflicts=False,
    )
    return PARENT, plan


@pytest.fixture
def rebased_feature_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the reflog-backed rebase plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["main"] = PARENT
    facts.ancestors.add((PARENT, TIP))
    facts.reflogs["feature"] += ((TIP, f"rebase (finish): returning to feature onto {PARENT}"),)
    facts.ranges[f"{PARENT}..feature"] = (CommitSummary(TIP, "feat: feature change"),)
    plan = build_release_plan(repo, preview_conflicts=False)
    return PARENT, plan


@pytest.fixture
def main_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the synthetic on-main plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.current = "main"
    facts.refs = {"main": TIP}
    facts.ranges["v1.0.0..main"] = (CommitSummary(TIP, "feat: release work"),)
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_on_main_prepares_in_place(main_plan: ReleasePlan) -> None:
    """Starting from main never proposes a rebase or branch merge."""
    plan = main_plan

    assert plan.mode is ReleaseMode.ON_MAIN
    assert plan.action is ReleaseAction.PREPARE_IN_PLACE
    assert plan.scope == "v1.0.0..main"
    assert plan.operations == (
        "run ghog day --full=cov --whole-suite",
        "prepare version and release notes in place",
    )


def test_plan_integration_merges_no_ff_when_it_contains_main(
    integration_merge_plan: ReleasePlan,
) -> None:
    """A current integration branch is promoted directly with --no-ff."""
    plan = integration_merge_plan

    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True
    assert plan.operations[:2] == (
        "git switch develop",
        "run ghog day --full=cov --whole-suite",
    )
    assert plan.operations[-1] == "git merge --no-ff develop"


@pytest.fixture
def configured_integration_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare the configured integration plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.current = "next"
    facts.refs = {"main": BASE, "next": TIP}
    facts.config["prepare-release.integrationBranch"] = "next"
    facts.ranges["main..next"] = (CommitSummary(TIP, "feat: integrated work"),)
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_uses_configured_integration_role(
    configured_integration_plan: ReleasePlan,
) -> None:
    """Repository config can name a non-develop integration branch."""
    plan = configured_integration_plan

    assert plan.integration_branch == "next"
    assert plan.mode is ReleaseMode.INTEGRATION
    assert plan.action is ReleaseAction.MERGE_NO_FF


def test_plan_integration_previews_main_sync_conflict(
    integration_conflict_plan: ReleasePlan,
) -> None:
    """A stale integration branch previews the main-into-integration sync first."""
    plan = integration_conflict_plan

    assert plan.action is ReleaseAction.SYNC_INTEGRATION_THEN_MERGE
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is False
    assert plan.merge_preview.conflicted_files == ("shared.txt",)
    assert plan.operations[1] == "git merge --no-ff main"
    assert plan.operations[2] == "run ghog day --full=cov --whole-suite"


@pytest.fixture
def nested_feature_plan(tmp_path: Path) -> tuple[str, str, ReleasePlan]:
    """Declare a feature forked from the current integration tip."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs.update({"develop": PARENT, "main": MERGE})
    facts.ancestors.add((PARENT, TIP))
    facts.ranges[f"{PARENT}..feature"] = (CommitSummary(TIP, "feat: selected work"),)
    facts.merge_previews["develop", "feature"] = MergePreview(clean=True, tree_oid="tree", conflicted_files=(), conflicts=())

    plan = build_release_plan(
        repo,
        branch="feature",
        integration_branch="develop",
        feature_base=PARENT,
    )
    return PARENT, TIP, plan


def test_plan_nested_feature_uses_exact_integration_replay(
    nested_feature_plan: tuple[str, str, ReleasePlan],
) -> None:
    """A feature forked from develop returns only its commits to develop."""
    develop_tip, feature_tip, plan = nested_feature_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_target_branch == "develop"
    assert plan.feature_base == develop_tip
    assert [commit.oid for commit in plan.commits] == [feature_tip]
    assert plan.rebase_preview is None
    assert plan.operations == (
        "git switch feature",
        "run ghog day --full=cov --whole-suite",
        "git switch --ignore-other-worktrees develop",
        "git merge --no-ff feature",
    )


@pytest.fixture
def auto_detected_boundary_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare automatic branch-boundary detection outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.reflogs["feature"] = ((BASE, "commit: ignored"), *facts.reflogs["feature"])
    return BASE, build_release_plan(repo, preview_conflicts=False)


def test_plan_auto_detects_branch_creation_boundary(
    auto_detected_boundary_plan: tuple[str, ReleasePlan],
) -> None:
    """The latest branch-positioning reflog entry can prove the feature fork."""
    base, plan = auto_detected_boundary_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog:")


@pytest.fixture
def already_released_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare an already-released feature plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["main"] = MERGE
    facts.ancestors.add((TIP, MERGE))
    facts.containing_tags["feature"] = ("v1.1.0",)
    plan = build_release_plan(repo, branch="feature", preview_conflicts=False)
    return TIP, plan


def test_plan_stops_feature_already_contained_by_release_tag(
    already_released_plan: tuple[str, ReleasePlan],
) -> None:
    """An old feature tip produces no empty replay when main already released it."""
    feature_tip, plan = already_released_plan

    assert plan.branch_oid == feature_tip
    assert plan.action is ReleaseAction.ALREADY_RELEASED
    assert plan.containing_release_tags == ("v1.1.0",)


@pytest.fixture
def orphan_boundary_plan(tmp_path: Path) -> ReleasePlan:
    """Prepare an orphan-branch boundary plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.current = "rescue"
    facts.refs = {"main": BASE, "rescue": TIP}
    facts.ancestors.clear()
    facts.reflogs.clear()
    return build_release_plan(repo, preview_conflicts=False)


def test_plan_orphan_branch_requires_a_boundary(orphan_boundary_plan: ReleasePlan) -> None:
    """A branch without provable topology stops instead of guessing a base."""
    plan = orphan_boundary_plan

    assert plan.mode is ReleaseMode.FEATURE
    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.boundary_candidates == ()
    assert plan.commits == ()
    assert any("--feature-base" in note for note in plan.notes)


@pytest.fixture
def explicit_merge_scope_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare the explicit merge-scope plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["feature"] = MERGE
    facts.ancestors.add((BASE, MERGE))
    facts.merged_ranges.add(f"{BASE}..feature")
    facts.ranges[f"{BASE}..feature"] = (
        CommitSummary(TIP, "feat: feature change"), CommitSummary(PARENT, "feat: side change"),
        CommitSummary(MERGE, "merge side"),
    )
    plan = build_release_plan(
        repo,
        branch="feature",
        feature_base=BASE,
        preview_conflicts=False,
    )
    return BASE, plan


def test_plan_flags_merges_inside_an_explicit_feature_scope(
    explicit_merge_scope_plan: tuple[str, ReleasePlan],
) -> None:
    """A feature range containing a merge asks for explicit commit selection."""
    base, plan = explicit_merge_scope_plan

    assert plan.action is ReleaseAction.NEEDS_FEATURE_BOUNDARY
    assert plan.feature_base == base
    assert plan.commits != ()
    assert any("contains merges" in note for note in plan.notes)


@pytest.fixture
def direct_merge_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare a direct-merge preview plan outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.merge_previews["main", "feature"] = MergePreview(clean=True, tree_oid="tree", conflicted_files=(), conflicts=())
    return BASE, build_release_plan(repo)


def test_plan_direct_merge_previews_conflicts(
    direct_merge_plan: tuple[str, ReleasePlan],
) -> None:
    """A feature still rooted at the main tip previews the merge itself."""
    base, plan = direct_merge_plan

    assert plan.action is ReleaseAction.MERGE_NO_FF
    assert plan.feature_base == base
    assert plan.merge_preview is not None
    assert plan.merge_preview.clean is True


def test_plan_explicit_parent_uses_the_first_parent_merge_boundary(
    explicit_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """A parent branch that merged the feature proves the fork point."""
    base, plan = explicit_parent_plan

    assert plan.feature_base == base
    assert plan.boundary_evidence == "first-parent merge into develop"
    assert plan.action is ReleaseAction.MERGE_NO_FF


@pytest.fixture
def explicit_parent_boundary_error(tmp_path: Path) -> ReleasePlanError:
    """Capture an underivable parent-boundary error outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.refs["twin"] = TIP
    facts.histories["twin"] = (BASE, TIP)
    facts.parents = {BASE: (), TIP: (BASE,)}

    with pytest.raises(ReleasePlanError) as caught:
        build_release_plan(
            repo,
            branch="feature",
            feature_parent="twin",
            preview_conflicts=False,
        )
    return caught.value


def test_plan_explicit_parent_without_a_boundary_fails(
    explicit_parent_boundary_error: ReleasePlanError,
) -> None:
    """A parent giving no derivable fork point raises instead of guessing."""
    assert "Could not derive a boundary" in str(explicit_parent_boundary_error)


@pytest.fixture
def explicit_base_error(tmp_path: Path) -> ReleasePlanError:
    """Capture the improper explicit-base error outside assertion time."""
    repo = tmp_path / "repo"
    declare_repository(repo)

    with pytest.raises(ReleasePlanError) as caught:
        build_release_plan(repo, branch="feature", feature_base="feature", preview_conflicts=False)
    return caught.value


def test_plan_explicit_base_must_be_a_proper_ancestor(explicit_base_error: ReleasePlanError) -> None:
    """The branch tip itself is rejected as its own feature base."""
    assert "not a proper ancestor of feature" in str(explicit_base_error)


def test_plan_rebased_feature_uses_the_reflog_onto_evidence(
    rebased_feature_plan: tuple[str, ReleasePlan],
) -> None:
    """A completed rebase leaves the exact new base in the branch reflog."""
    main_tip, plan = rebased_feature_plan

    assert plan.feature_base == main_tip
    assert plan.boundary_evidence is not None
    assert plan.boundary_evidence.startswith("reflog: rebase")
    assert plan.action is ReleaseAction.MERGE_NO_FF


@pytest.fixture
def reset_reflog_plan(tmp_path: Path) -> tuple[str, ReleasePlan]:
    """Prepare reset reflog evidence outside assertion time."""
    repo = tmp_path / "repo"
    facts = declare_repository(repo)
    facts.reflogs["feature"] += ((BASE, "reset: moving to main"),)
    facts.ranges[f"{BASE}..feature"] = (CommitSummary(TIP, "feat: kept work"),)
    return BASE, build_release_plan(repo, preview_conflicts=False)


def test_plan_reset_reflog_entry_wins_as_latest_evidence(
    reset_reflog_plan: tuple[str, ReleasePlan],
) -> None:
    """The newest branch-positioning entry supersedes the creation entry."""
    base, plan = reset_reflog_plan

    assert plan.feature_base == base
    assert plan.feature_parent_refs == ("main",)
    assert plan.boundary_evidence == "reflog: reset: moving to main"


def test_plan_single_parent_candidate_is_selected_without_ranking(
    single_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """One surviving parent candidate is the boundary without a nearest vote."""
    base, plan = single_parent_plan

    assert plan.feature_base == base
    assert plan.boundary_evidence == "merge-base main feature"
    (candidate,) = plan.boundary_candidates
    assert candidate.parent_refs == ("main",)
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE
    assert plan.operations[2] == "run git range-diff and ghog day --full=cov --whole-suite"


def test_plan_ambiguous_parents_select_the_unique_nearest_boundary(
    ambiguous_parent_plan: tuple[str, ReleasePlan],
) -> None:
    """Without reflogs, deduplicated candidates elect the nearest fork point."""
    fork_point, plan = ambiguous_parent_plan

    assert plan.feature_base == fork_point
    assert plan.feature_parent_refs == ("develop",)
    assert len(plan.boundary_candidates) == _EXPECTED_CANDIDATES
    # The two same-base candidates from main and other merge into one entry.
    assert plan.boundary_candidates[1].parent_refs == ("main", "other")
    assert plan.action is ReleaseAction.REBASE_ONTO_MAIN_THEN_MERGE


# eof
