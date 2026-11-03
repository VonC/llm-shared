"""Scheduled publication wakes a reviewer parked at a gate or after conclusion.

Prerequisite ownership uses the production identity transaction directly;
publication, notification rescans and the eventual wait claim remain live.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.review_resume.notification_simulation import (
    NotificationSchedule,
    assert_quiet,
)
from tests.acceptance.review_resume.prepared_request import prepare_convergence
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
    ConfirmationOutcome,
    ReviewConfiguration,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.acceptance.review_resume.conftest import ReviewRepository

@pytest.mark.parametrize("kind", ["gate", "concluded"])
def test_wait_survives_convergence_and_conclusion_then_wakes(
    repository: ReviewRepository, monkeypatch: pytest.MonkeyPatch, kind: str,
    stable_review_inputs: Callable[[], None],
) -> None:
    """Rescan on unrelated hints without claiming, then claim only the new request."""
    stable_review_inputs()
    repo = repository
    _prepare_parked_state(repo, kind)
    before = repo.evidence()

    def unrelated_hint() -> bool:
        """A notification is only a hint; it conveys no pending request."""
        assert_quiet()
        (repo.home / "a.unrelated.md").write_text("unrelated notification", encoding="utf-8")
        return True

    def publication() -> bool:
        """Publish after the unrelated rescan remained quiet and read-only."""
        assert_quiet()
        assert repo.evidence() == before
        _publish_next(repo, kind)
        return True

    schedule = NotificationSchedule(unrelated_hint, publication)
    monkeypatch.setattr(resume_cli, "WatchdogNotificationAdapter", schedule.adapter)
    result = repo.run("wait-any-request", nature="claude")
    assert result.code == 0
    assert result.payload["outcome"] == "found"
    expected_family, expected_round = {"gate": ("code", 2), "concluded": ("specification", 1)}[kind]
    assert result.payload["identity"]["family"] == expected_family
    assert result.payload["candidates"][0]["round"] == expected_round
    assert not schedule.actions
    assert schedule.lifecycle == ["schedule", "start", "stop", "join"]


def _prepare_parked_state(repo: ReviewRepository, kind: str) -> None:
    """Declare the gate prerequisite; completion and subsequent waits remain live."""
    capability = prepare_convergence(repo, authorized=kind == "concluded")
    if kind == "concluded":
        assert repo.exchange("complete", capability=capability).code == 0


def _publish_next(repo: ReviewRepository, kind: str) -> None:
    """Advance the selected gate state before a notification rescan."""
    if kind == "gate":
        _continue_gate(repo)
    else:
        repo.context = review_context(repo.root, ReviewFamily.SPECIFICATION, "later-specification")
        repo.paths = derive_artifact_paths(repo.root, repo.context)
        repo.start_request()


def _continue_gate(repo: ReviewRepository) -> None:
    """Use real requestor transitions while the public reviewer wait is parked."""
    core = ReviewExchangeCore(ReviewExchangeStore(repo.paths), repo.context,
                              review_policy(repo.context), ReviewConfiguration(enabled=True))
    capability = claim_selected(core, ReviewRole.REQUESTOR, LlmNature.CODEX,
                                round_number=1, occurrence=1, override=False)
    core.present_ownership(capability)
    confirmed = core.confirm("Rework and review again")
    assert confirmed.outcome is ConfirmationOutcome.ANOTHER_ROUND
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(os, "environ", session_environment(os.environ, "codex"))
        core.publish_request(review_artifact(repo.context, ReviewRole.REQUESTOR, 2), "Replacement request.\n")


# eof
