"""Scheduled competing claims, ambiguous discovery and foreground cancellation."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.notification_simulation import (
    NotificationSchedule,
    assert_quiet,
)
from tests.acceptance.review_resume.prepared_request import prepare_assessed_round
from tests.unit.tools.review_exchange_test_support import (
    review_artifact,
    review_context,
    review_policy,
    session_environment,
)
from tools import review_exchange_cli_resume as resume_cli
from tools.llm_nature import LlmNature
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ReviewConfiguration,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_ownership import OwnershipCapability
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.acceptance.review_resume.conftest import ReviewRepository

_NONFATAL_STATUS = 3
_REPLACEMENT_ROUND = 2


def _advance_review_round(repo: ReviewRepository) -> None:
    """Publish from the declared completed assessment at the notification boundary."""
    core = ReviewExchangeCore(ReviewExchangeStore(repo.paths), repo.context,
                              review_policy(repo.context), ReviewConfiguration(enabled=True))
    # The producer's answer/consume sequence is not the competing-wait
    # contract. Only its assessed state is needed for real continue/publish.
    core.present_ownership(prepare_assessed_round(repo))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(os, "environ", session_environment(os.environ, "codex"))
        assert core.continue_round().round_number == _REPLACEMENT_ROUND
        core.publish_request(review_artifact(repo.context, ReviewRole.REQUESTOR, _REPLACEMENT_ROUND),
                             "## requestor evidence\n\nReplacement request.\n")


def test_competing_reviewers_have_one_winner_and_loser_waits_for_replacement(
    stable_review_inputs: Callable[[], None],
    repository: ReviewRepository, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Interleave real claims with fixed configuration and live protocol evidence."""
    repo = repository
    repo.start_request()
    stable_review_inputs()
    first: dict[str, Any] = {}
    claim = resume_cli._RequestDiscovery.claim
    competing = False

    def interleave(discovery: resume_cli._RequestDiscovery, candidate: object) -> bool:
        """Let a second session claim between the first session's scan and claim."""
        nonlocal competing
        if not competing:
            competing = True
            # Both actors race for the request actually observed by the outer
            # wait. A second discovery of the unchanged home adds no competing
            # claim evidence; give that same candidate to the real claimant.
            assert isinstance(candidate, resume_cli.ExchangeStatus)
            winner = resume_cli._RequestDiscovery(repo.root)
            assert claim(winner, candidate)
            first.update(winner.capability(candidate))
            first["identity"] = candidate.identity.to_dict()
            first["round"] = candidate.round_number
            assert not claim(discovery, candidate)
            return False
        return claim(discovery, candidate)

    def replacement() -> bool:
        """The losing wait emits nothing and retains no capability before replacement."""
        assert_quiet()
        _advance_review_round(repo)
        return True

    schedule = NotificationSchedule(replacement)
    monkeypatch.setattr(resume_cli._RequestDiscovery, "claim", interleave)
    monkeypatch.setattr(resume_cli, "WatchdogNotificationAdapter", schedule.adapter)
    second = repo.run("wait-any-request", nature="claude")
    assert second.code == 0
    _assert_replacement_claim(first, second.payload)
    _assert_tokens_private(repo, first, second.payload)
    assert not schedule.actions


def _assert_replacement_claim(first: dict[str, Any], second: dict[str, Any]) -> None:
    """Check identity, round replacement and capability generation."""
    assert second["outcome"] == "found"
    assert first["round"] == 1
    assert second["candidates"][0]["round"] == _REPLACEMENT_ROUND
    assert first["identity"] == second["identity"]
    assert first["ownership_generation"] < second["ownership_generation"]


def test_discovered_capability_is_reused_by_selected_resume(
    repository: ReviewRepository, stable_review_inputs: Callable[[], None],
) -> None:
    """Discovery's real winning capability survives pickup without another lease."""
    repo = repository
    repo.start_request()
    stable_review_inputs()
    discovery = resume_cli._RequestDiscovery(repo.root)
    candidate, = discovery.rescan()
    assert discovery.claim(candidate)
    first = discovery.capability(candidate)
    core = ReviewExchangeCore(ReviewExchangeStore(repo.paths), repo.context,
                              review_policy(repo.context), ReviewConfiguration(enabled=True))
    core.present_ownership(OwnershipCapability(int(str(first["ownership_generation"])), str(first["ownership_token"])))
    resumed = claim_selected(core, ReviewRole.REVIEWER, LlmNature.CLAUDE,
                             round_number=1, occurrence=1, override=False)
    assert resumed.generation == first["ownership_generation"]
    assert resumed.token == first["ownership_token"]
    assert resumed.token.encode() not in b"\n".join(repo.evidence().values())


def _assert_tokens_private(repo: ReviewRepository, first: dict[str, Any], second: dict[str, Any]) -> None:
    """Neither session capability may appear in durable evidence."""
    evidence = b"\n".join(repo.evidence().values())
    assert first["ownership_token"].encode() not in evidence
    assert second["ownership_token"].encode() not in evidence


def test_simultaneous_requests_return_ambiguity_without_claiming(
    repository: ReviewRepository, stable_review_inputs: Callable[[], None],
) -> None:
    """Two pending identities require selection and leave review evidence unchanged."""
    repo = repository
    stable_review_inputs()
    repo.start_request()
    first = repo.evidence()
    repo.context = review_context(repo.root, ReviewFamily.SPECIFICATION, "second")
    repo.paths = derive_artifact_paths(repo.root, repo.context)
    repo.start_request()
    before = repo.evidence()
    result = repo.run("wait-any-request", nature="claude")
    assert result.code == _NONFATAL_STATUS
    assert result.payload["outcome"] == "ambiguous"
    assert len(result.payload["candidates"]) == len((first, before))
    assert "ownership_token" not in result.payload
    assert before == repo.evidence()
    for name, content in first.items():
        assert (repo.root / name).read_bytes() == content


def test_graceful_foreground_cancellation_has_one_result_and_no_durable_waiter(
    repository: ReviewRepository, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cancel at a notification boundary after production preflight and discovery."""
    repo = repository
    before = _home_files(repo)

    def interrupt() -> bool:
        """Supply the host cancellation observation without signals or waiting."""
        assert_quiet()
        raise KeyboardInterrupt

    schedule = NotificationSchedule(interrupt)
    monkeypatch.setattr(resume_cli, "WatchdogNotificationAdapter", schedule.adapter)
    result = repo.run("wait-any-request", nature="claude")
    assert result.code == _NONFATAL_STATUS
    assert result.stderr == ""
    assert result.payload["outcome"] == "cancelled"
    assert set(result.payload) == {"operation", "outcome", "identity", "candidates", "diagnostic"}
    assert result.payload["identity"] is None
    assert result.payload["candidates"] == []
    assert before == _home_files(repo)
    assert schedule.lifecycle == ["schedule", "start", "stop", "join"]


def _home_files(repo: ReviewRepository) -> dict[str, bytes]:
    """Snapshot caller artifacts independently of the result under test."""
    return {path.name: path.read_bytes() for path in repo.home.iterdir() if path.is_file()}


# eof
