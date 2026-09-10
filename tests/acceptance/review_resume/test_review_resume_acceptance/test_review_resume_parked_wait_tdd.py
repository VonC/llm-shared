"""A parked reviewer wait woken by a replacement round or a new family.

Fix: split out of ``test_review_resume_concurrency_tdd``. Its two parameters
were the longest-running fixture of that module, and ``--dist loadscope``
keeps a whole module on one worker, so they held the module's scenarios
behind them. The scenario and every assertion are unchanged.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import (
    ReviewRepository,
    assert_still_quiet,
    start_wait,
    terminal_result,
)
from tests.unit.tools.review_exchange_test_support import review_context
from tools.review_exchange_models import ReviewFamily, ReviewRole
from tools.review_exchange_paths import derive_artifact_paths


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(kind, marks=pytest.mark.xdist_group(f"parked-{kind}"))
        for kind in ("gate", "concluded")
    ],
)
def parked_wait_journey(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Wake a reviewer from the human gate or after release into a different family."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-parked") / "caller")
    repo.start_request()
    reviewer = repo.resume("resume", role="reviewer", nature="claude")
    answer = repo.publish(ReviewRole.REVIEWER, reviewer[-1].payload, ready=True, nature="claude")
    assert answer.code == 3
    assert answer.payload["outcome"] == "published"
    assert answer.payload["state"] == "convergence-gate"
    requestor = repo.resume("resume")
    if request.param == "concluded":
        repo.exchange("confirm", "--choice-label", "Commit", capability=requestor[-1].payload)
        assert repo.exchange("complete", capability=requestor[-1].payload).code == 0
    process = start_wait(repo)
    try:
        assert_still_quiet(process)
        before = repo.evidence()
        (repo.home / "a.unrelated.md").write_text("unrelated notification", encoding="utf-8")
        assert_still_quiet(process)
        unchanged = repo.evidence()
        if request.param == "gate":
            confirmed = repo.exchange("confirm", "--choice-label", "Rework and review again",
                                      capability=requestor[-1].payload)
            assert confirmed.code == 0, confirmed
            published = repo.publish(ReviewRole.REQUESTOR, requestor[-1].payload, round_number=2)
            assert published.code == 0, published
        else:
            repo.context = review_context(repo.root, ReviewFamily.SPECIFICATION, "later-specification")
            repo.paths = derive_artifact_paths(repo.root, repo.context)
            repo.start_request()
        result = terminal_result(process, process.communicate(timeout=15))
        return {"kind": request.param, "result": result, "before": before, "unchanged": unchanged}
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


def test_wait_survives_convergence_and_conclusion_then_wakes(parked_wait_journey: dict[str, Any]) -> None:
    """AC12: a gate wakes for a replacement; a released exchange wakes for a new specification."""
    journey = parked_wait_journey
    assert journey["before"] == journey["unchanged"]
    result = journey["result"]
    assert result["outcome"] == "found"
    expected_family = "code" if journey["kind"] == "gate" else "specification"
    assert result["identity"]["family"] == expected_family
    assert result["candidates"][0]["round"] == (2 if journey["kind"] == "gate" else 1)


# eof
