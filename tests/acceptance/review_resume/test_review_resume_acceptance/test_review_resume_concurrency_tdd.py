"""Competing launcher claims, simultaneous candidates and foreground cancellation.

Fix: the parked-wait scenarios moved to ``test_review_resume_parked_wait_tdd``
and the independent-waiter helpers to the package conftest. ``--dist loadscope``
keeps one module on one worker, so the split lets both halves run in parallel.
Every remaining scenario and assertion is unchanged.

Fix: the waiters' claim bounds use the shared ``PROCESS_TIMEOUT_SECONDS`` hang
guard instead of 15 seconds, since a claim runs the same Python and ``git``
children that once outlasted a 30-second bound under the parallel full run.

Fix: the foreground cancellation runs in process, and its preflight spawned
four ``git`` processes (three home-tracking checks and one ignore check), which
kept the call above the one-second duration floor. ``_IgnoredHomeGit`` answers
those two reads as real git does for the fixture's self-ignored home; the
process-based scenarios of this package keep the real git path covered.
"""

# ruff: noqa: PLR2004, S603
from __future__ import annotations

import json
import subprocess
from contextlib import chdir, redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from time import monotonic, sleep
from typing import Any
from unittest.mock import patch

import pytest

from tests.acceptance.review_resume.conftest import (
    PROCESS_TIMEOUT_SECONDS,
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

# Keep this module's scenarios on one xdist worker so its module-scoped
# fixtures are built once rather than once per worker (--dist loadgroup).
pytestmark = pytest.mark.xdist_group("resume-concurrency")


def first_completed(processes: list[subprocess.Popen[str]]) -> list[int]:
    """Bound the initial claim without starting the losing process's pipe deadline."""
    deadline = monotonic() + PROCESS_TIMEOUT_SECONDS
    while True:
        completed = [index for index, process in enumerate(processes) if process.poll() is not None]
        if completed:
            return completed
        remaining = deadline - monotonic()
        assert remaining > 0, f"No reviewer claimed the initial request within {PROCESS_TIMEOUT_SECONDS} seconds"
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
        second = terminal_result(other, other.communicate(timeout=PROCESS_TIMEOUT_SECONDS))
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


class _IgnoredHomeGit:
    """Answer the preflight's two git reads for a home git ignores and never tracks.

    The fixture's home holds its own ``*`` ignore file, so real git lists
    nothing tracked below it and reports every path under it ignored. Any
    other command, or a query outside the home, fails the test.
    """

    def __init__(self, repo: ReviewRepository) -> None:
        """Bind the stand-in to one repository and its home.

        Args:
            repo: The fixture repository whose home the preflight checks.
        """
        self._root = repo.root.resolve()
        self._home = repo.home.resolve()

    def __call__(self, command: list[str], **options: Any) -> subprocess.CompletedProcess[str]:
        """Return the completed git process real git gives for one home query.

        Args:
            command: The git command line.
            **options: The ``subprocess.run`` options: ``cwd`` and ``input``.

        Returns:
            The completed process with git's exit code and output.
        """
        assert Path(options["cwd"]).resolve() == self._root
        if command[:3] == ["git", "ls-files", "--"]:
            assert (self._root / command[3]).resolve() == self._home
            return subprocess.CompletedProcess(command, 0, "", "")
        assert command == ["git", "check-ignore", "-z", "--stdin"]
        queried = [path for path in options["input"].split("\0") if path]
        assert all((self._root / path).resolve().is_relative_to(self._home) for path in queried)
        return subprocess.CompletedProcess(command, 0, options["input"], "")


def test_graceful_foreground_cancellation_has_one_result_and_no_durable_waiter(
    repository: ReviewRepository, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC19: interrupt the host wait seam after real preflight and discovery, then stop quietly.

    The preflight's git reads are answered in process (``_IgnoredHomeGit``):
    they spawned four git processes and kept the call above one second.
    """
    repo = repository
    before = _home_bytes(repo)
    stdout, stderr = StringIO(), StringIO()
    monkeypatch.setenv("PRJ_DIR", str(repo.root))
    monkeypatch.setattr(subprocess, "run", _IgnoredHomeGit(repo))
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
