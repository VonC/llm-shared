"""Competing launcher claims, simultaneous candidates and foreground cancellation.

Fix: the parked-wait scenarios moved to ``test_review_resume_parked_wait_tdd``
and the independent-waiter helpers to the package conftest. ``--dist loadscope``
keeps one module on one worker, so the split lets both halves run in parallel.
Every remaining scenario and assertion is unchanged.
"""

# ruff: noqa: PLR2004, S603
from __future__ import annotations

import json
import subprocess
from contextlib import chdir, redirect_stderr, redirect_stdout
from io import StringIO
from time import monotonic, sleep
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from tests.acceptance.review_resume.conftest import (
    ReviewRepository,
    assert_still_quiet,
    start_wait,
    terminal_result,
)
from tests.unit.tools.review_exchange_test_support import review_context
from tools import review_exchange_cli
from tools.review_exchange_models import ReviewFamily, ReviewRole
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_resume_notifications import WatchdogNotificationAdapter

if TYPE_CHECKING:
    import subprocess

# Keep this module's scenarios on one xdist worker so its module-scoped
# fixtures are built once rather than once per worker (--dist loadgroup).
pytestmark = pytest.mark.xdist_group("resume-concurrency")


def first_completed(processes: list[subprocess.Popen[str]]) -> list[int]:
    """Bound the initial claim without starting the losing process's pipe deadline."""
    deadline = monotonic() + 15
    while True:
        completed = [index for index, process in enumerate(processes) if process.poll() is not None]
        if completed:
            return completed
        remaining = deadline - monotonic()
        assert remaining > 0, "No reviewer claimed the initial request within 15 seconds"
        sleep(min(0.05, remaining))


def _advance_review_round(repo: ReviewRepository, first: dict[str, Any]) -> list[Any]:
    """Answer with the winning capability and let only the requestor publish round two."""
    resumed = repo.resume("resume", role="reviewer", nature="claude", capability=first)
    answer = repo.publish(ReviewRole.REVIEWER, resumed[-1].payload, nature="claude")
    assert answer.code == 0, answer
    requestor = repo.resume("resume")
    consumed = repo.exchange("consume-answer", "--reviewed-work-changed", "true",
                             capability=requestor[-1].payload)
    assert consumed.code == 0, consumed
    continued = repo.exchange("continue", capability=requestor[-1].payload)
    assert continued.code == 0, continued
    published = repo.publish(ReviewRole.REQUESTOR, requestor[-1].payload, round_number=2)
    assert published.code == 0, published
    return resumed


@pytest.fixture(scope="module")
def competing_journey(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Race two real reviewer processes; the losing process survives into round two."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-race") / "caller", home="runtime/reviews")
    processes = [start_wait(repo), start_wait(repo)]
    try:
        for process in processes:
            assert_still_quiet(process)
        repo.start_request()
        completed = first_completed(processes)
        assert len(completed) == 1
        first_index = completed[0]
        winner = processes[first_index]
        first = terminal_result(winner, winner.communicate(timeout=5))
        other = processes[1 - first_index]
        assert other.poll() is None
        resumed = _advance_review_round(repo, first)
        # Start the losing waiter's deadline only after replacement publication.
        second = terminal_result(other, other.communicate(timeout=15))
        return {"first": first, "second": second, "resumed": resumed, "evidence": repo.evidence()}
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)


def test_competing_reviewers_have_one_winner_and_loser_waits_for_replacement(competing_journey: dict[str, Any]) -> None:
    """AC12,19: one process claims round one; its competitor remains quiet and claims round two."""
    journey = competing_journey
    assert journey["first"]["outcome"] == journey["second"]["outcome"] == "found"
    assert journey["first"]["candidates"][0]["round"] == 1
    assert journey["second"]["candidates"][0]["round"] == 2
    assert journey["first"]["identity"] == journey["second"]["identity"]
    assert journey["first"]["ownership_generation"] < journey["second"]["ownership_generation"]
    assert journey["resumed"][-1].payload["ownership_generation"] == journey["first"]["ownership_generation"]
    evidence = b"\n".join(journey["evidence"].values())
    assert journey["first"]["ownership_token"].encode() not in evidence
    assert journey["second"]["ownership_token"].encode() not in evidence


@pytest.fixture(scope="module")
def ambiguous_wait_journey(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Publish two identities before one observation, preserving selection for the human."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-ambiguous") / "caller")
    repo.start_request()
    first_before = repo.evidence()
    repo.context = review_context(repo.root, ReviewFamily.SPECIFICATION, "second")
    repo.paths = derive_artifact_paths(repo.root, repo.context)
    repo.start_request()
    before = repo.evidence()
    result = repo.run("wait-any-request", nature="claude")
    return {"result": result, "before": before, "after": repo.evidence(), "first": first_before, "root": repo.root}


def test_simultaneous_requests_return_ambiguity_without_claiming(ambiguous_wait_journey: dict[str, Any]) -> None:
    """AC12: simultaneous code and specification candidates require explicit selection."""
    journey = ambiguous_wait_journey
    result = journey["result"]
    assert result.code == 3
    assert result.payload["outcome"] == "ambiguous"
    assert len(result.payload["candidates"]) == 2
    assert "ownership_token" not in result.payload
    assert journey["before"] == journey["after"]
    for name, content in journey["first"].items():
        assert (journey["root"] / name).read_bytes() == content


def _home_bytes(repo: ReviewRepository) -> dict[str, bytes]:
    """Snapshot the local home to detect any persisted waiter or unexpected claim."""
    return {path.name: path.read_bytes() for path in repo.home.iterdir() if path.is_file()}


def test_graceful_foreground_cancellation_has_one_result_and_no_durable_waiter(
    repository: ReviewRepository, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC19: interrupt the host wait seam after real preflight and discovery, then stop quietly."""
    repo = repository
    before = _home_bytes(repo)
    stdout, stderr = StringIO(), StringIO()
    monkeypatch.setenv("PRJ_DIR", str(repo.root))
    with (chdir(repo.root), redirect_stdout(stdout), redirect_stderr(stderr),
          patch.object(WatchdogNotificationAdapter, "wait", side_effect=KeyboardInterrupt)):
        code = review_exchange_cli.main(["wait-any-request"])
    assert code == 3
    assert stderr.getvalue() == ""
    assert len(stdout.getvalue().splitlines()) == 1
    payload = json.loads(stdout.getvalue())
    assert payload["outcome"] == "cancelled"
    assert set(payload) == {"operation", "outcome", "identity", "candidates", "diagnostic"}
    assert payload["identity"] is None
    assert payload["candidates"] == []
    assert before == _home_bytes(repo)


# eof
