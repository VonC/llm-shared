"""Whole-suite gates precede promotion to every supported destination."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.prepare_release.prepare_release_plan_test_support import (
    commit_file,
    git,
    initialize_repository,
    repository_for,
)
from tools.prepare_release import prepare_release_plan_workflow as workflow
from tools.prepare_release.prepare_release_plan_models import ReleaseAction

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prepare_release.prepare_release_plan_models import ReleasePlan

_TARGETS = ("main", "develop", "next", "umbrella_flow")
_INTEGRATIONS = _TARGETS[1:]
_GATE = "run ghog day --full=cov --whole-suite"


@pytest.fixture(autouse=True)
def synthetic_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep Git process-free and expose a conflicting ambient group."""
    monkeypatch.setattr(workflow, "GitRepository", repository_for)
    monkeypatch.delenv("PREPARE_RELEASE_INTEGRATION_BRANCH", raising=False)
    monkeypatch.setenv("GHOG_GROUP", "only-topic")


def _destination(repo: Path, target: str) -> Path | None:
    """Resolve generic integration through config, or an umbrella through its slug."""
    initialize_repository(repo)
    if target == "main":
        return None
    git(repo, "switch", "-c", target)
    if target != "umbrella_flow":
        git(repo, "config", "prepare-release.integrationBranch", target)
        return None
    umbrella = repo / "docs/draft.v9.9.0.umbrella-flow.md"
    umbrella.parent.mkdir()
    umbrella.write_text("# Collection\n\n- Draft role: umbrella\n", encoding="utf-8")
    return umbrella.relative_to(repo)


@pytest.mark.parametrize("target", _TARGETS)
@pytest.mark.parametrize("route", ["direct", "replay", "integrated"])
def test_topic_gate_precedes_every_destination_promotion(
    tmp_path: Path, target: str, route: str,
) -> None:
    """Topic promotion and resumed completion validate the exact candidate tree."""
    repo = tmp_path / "repo"
    umbrella = _destination(repo, target)
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "-c", "topic")
    commit_file(repo, "topic.txt", "topic\n", "feat: topic")
    git(repo, "switch", target)
    if route == "replay":
        commit_file(repo, "later.txt", "later\n", "feat: later integration work")
    elif route == "integrated":
        git(repo, "merge", "--no-ff", "topic", "-m", "merge topic")

    plan = workflow.build_release_plan(
        repo, branch="topic", feature_base=base, umbrella=umbrella,
        preview_conflicts=False,
    )

    assert plan.feature_target_branch == target
    gates = [index for index, operation in enumerate(plan.operations) if "ghog day" in operation]
    assert len(gates) == 1
    gate = gates[0]
    assert "ghog day --full=cov --whole-suite" in plan.operations[gate]
    _assert_gate_position(plan, gate, target, base, route)


def _assert_gate_position(plan: ReleasePlan, gate: int, target: str, base: str, route: str) -> None:
    """Check which candidate is validated and when promotion can begin."""
    if route == "integrated":
        assert plan.action is ReleaseAction.ALREADY_INTEGRATED
        assert plan.operations[gate - 1] == f"git switch --ignore-other-worktrees {target}"
        assert not any("git merge" in operation for operation in plan.operations)
    else:
        assert plan.operations[gate + 1] == f"git switch --ignore-other-worktrees {target}"
        assert plan.operations[-1].startswith("git merge --no-ff ")
        if route == "direct":
            assert plan.operations[gate - 1] == "git switch topic"
        else:
            assert plan.operations[gate - 1].startswith(f"git rebase --onto {target} {base} ")


@pytest.mark.parametrize("target", _INTEGRATIONS)
@pytest.mark.parametrize("stale", [False, True], ids=("current", "sync"))
def test_integration_gate_runs_with_or_without_main_sync(
    tmp_path: Path, target: str, *, stale: bool,
) -> None:
    """All long-lived integration roles validate before promotion to main."""
    repo = tmp_path / "repo"
    umbrella = _destination(repo, target)
    commit_file(repo, "integration.txt", "integration\n", "feat: integrated topics")
    git(repo, "switch", "main")
    if stale:
        commit_file(repo, "main.txt", "main\n", "fix: main hotfix")

    plan = workflow.build_release_plan(repo, branch=target, umbrella=umbrella, preview_conflicts=False)

    assert plan.integration_branch == target
    assert plan.operations.count(_GATE) == 1
    gate = plan.operations.index(_GATE)
    assert plan.operations[0] == f"git switch {target}"
    if stale:
        assert plan.operations[gate - 1] == "git merge --no-ff main"
    assert plan.operations[gate + 1:] == (
        "git switch --ignore-other-worktrees main",
        f"git merge --no-ff {target}",
    )


def test_already_released_topic_remains_a_noop(tmp_path: Path) -> None:
    """An old released topic cannot launch a redundant lifecycle gate."""
    repo = tmp_path / "repo"
    _destination(repo, "main")
    git(repo, "switch", "-c", "topic")
    commit_file(repo, "topic.txt", "topic\n", "feat: topic")
    git(repo, "switch", "main")
    git(repo, "merge", "--no-ff", "topic", "-m", "merge topic")
    git(repo, "tag", "v1.1.0")

    plan = workflow.build_release_plan(repo, branch="topic", preview_conflicts=False)

    assert plan.action is ReleaseAction.ALREADY_RELEASED
    assert plan.operations == ()


# eof
