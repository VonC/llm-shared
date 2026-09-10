"""Real-launcher identity acceptance for legacy completion across providers.

Fix: the conflict scenarios moved to ``test_review_resume_conflict_tdd`` and
``legacy_natures`` to the package conftest, so ``--dist loadscope`` can run the
four-provider journey and the conflict journey on separate workers. Neither
scenario changed.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import ReviewRepository, legacy_natures
from tools.review_exchange_models import ReviewRole
from tools.review_exchange_models_envelope import parse_json_markdown


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(nature, marks=pytest.mark.xdist_group(f"identity-{nature}"))
        for nature in ("claude", "codex", "gemini", "unknown")
    ],
)
def identity_journey(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Resume legacy evidence under each supported provider without outer host leakage."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-identity") / "caller")
    repo.start_request()
    legacy_natures(repo.paths.request, None)
    legacy_natures(repo.paths.coordination, None)
    body_before = parse_json_markdown(repo.paths.request.read_text(encoding="utf-8"))[1]
    before = repo.evidence()
    ambiguous = repo.run("resume-inspect", nature="unknown")
    after_ambiguous = repo.evidence()
    trace = repo.resume("resume", role="reviewer", nature=request.param)
    capability = trace[-1].payload
    same = repo.resume("resume", role="reviewer", nature=request.param, capability=capability)
    recorded = {path.name: repo.natures(path) for path in (repo.paths.request, repo.paths.coordination)}
    body_after = parse_json_markdown(repo.paths.request.read_text(encoding="utf-8"))[1]
    answer = repo.publish(ReviewRole.REVIEWER, same[-1].payload, nature=request.param)
    return {"repo": repo, "nature": request.param, "before": before, "after_ambiguous": after_ambiguous,
                "ambiguous": ambiguous, "trace": trace, "same": same, "recorded": recorded,
                "body_before": body_before, "body_after": body_after, "answer": answer,
                "published": repo.natures(repo.paths.answer)}


def test_legacy_role_prompt_is_read_only_and_explicit_role_continues(identity_journey: dict[str, Any]) -> None:
    """AC7,10-11,14: missing trace asks once; explicit role resolves it without a second gate."""
    journey = identity_journey
    assert journey["ambiguous"].payload["outcome"] == "role-selection-required"
    assert journey["ambiguous"].code == 3
    assert journey["before"] == journey["after_ambiguous"]
    assert all(result.code == 0 for result in journey["trace"])
    assert journey["trace"][-1].payload["action"] == "review-request"
    assert journey["same"][-1].payload["ownership_generation"] == journey["trace"][-1].payload["ownership_generation"]
    assert journey["same"][-1].payload["ownership_token"] == journey["trace"][-1].payload["ownership_token"]
    assert journey["body_before"] == journey["body_after"]


def test_selected_identity_backfills_all_runtime_evidence_and_leaves_counterpart_missing(identity_journey: dict[str, Any]) -> None:
    """AC6-7,10: known providers fill only their role; unknown remains absent until publication."""
    journey = identity_journey
    expected = None if journey["nature"] == "unknown" else journey["nature"]
    for snapshot in journey["recorded"].values():
        assert snapshot.get("reviewer") == expected
        assert snapshot.get("requestor") is None
    assert journey["answer"].code == 0
    assert journey["published"]["reviewer"] == journey["nature"]
    assert journey["published"]["requestor"] is None


# eof
