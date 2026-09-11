"""Explicit Stop and Override on one recorded role-nature conflict.

Fix: split out of ``test_review_resume_identity_tdd``, whose four-provider
journey dominated that module. ``--dist loadscope`` keeps a whole module on
one worker, so the conflict scenarios now run beside it rather than behind it.
The scenarios and their assertions are unchanged, and ``legacy_natures`` moved
to the package conftest because both halves seed the same legacy shape.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import ReviewRepository, legacy_natures

# Keep this module's scenarios on one xdist worker so its module-scoped
# fixtures are built once rather than once per worker (--dist loadgroup).
pytestmark = pytest.mark.xdist_group("resume-conflict")


@pytest.fixture(scope="module")
def conflict_journey(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Observe Stop and then an independently authorized Override on the same legacy gap."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-conflict") / "caller")
    repo.start_request()
    legacy_natures(repo.paths.request, {"requestor": "codex", "reviewer": None})
    legacy_natures(repo.paths.coordination, {"requestor": "codex", "reviewer": "claude"})
    before = repo.evidence()
    stopped = repo.resume("resume", role="reviewer", nature="codex")
    after_stop = repo.evidence()
    override = repo.resume("resume", role="reviewer", nature="codex", override=True)
    snapshots = {path.name: repo.natures(path) for path in (repo.paths.request, repo.paths.coordination)}
    return {"repo": repo, "stopped": stopped, "before": before, "after_stop": after_stop,
                "override": override, "snapshots": snapshots}


def test_conflict_stop_makes_no_partial_backfill_and_returns_all_evidence(conflict_journey: dict[str, Any]) -> None:
    """AC8-9: a known mismatch stops before claim and reports the conflicting artifact."""
    journey = conflict_journey
    result = journey["stopped"][-1]
    assert result.payload["outcome"] == "confirmation-required"
    assert result.code == 3
    assert journey["before"] == journey["after_stop"]
    assert "ownership_token" not in result.payload
    candidate = result.payload["candidates"][0]
    assert candidate["reviewer_llm_nature"] == "claude"
    assert candidate["reviewer_evidence"][0]["nature"] == "claude"


def test_override_preserves_conflict_and_fills_only_missing_selected_role(conflict_journey: dict[str, Any]) -> None:
    """AC9: approved Override claims while keeping existing contrary evidence intact."""
    journey = conflict_journey
    repo = journey["repo"]
    assert journey["override"][-1].code == 0
    assert journey["snapshots"][repo.paths.coordination.name] == {"requestor": "codex", "reviewer": "claude"}
    assert journey["snapshots"][repo.paths.request.name] == {"requestor": "codex", "reviewer": "codex"}
    assert journey["override"][-1].payload["action"] == "review-request"


# eof
