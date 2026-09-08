"""Exercise persistent discovery with real transitions and separately prepared cores."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_acceptance import (
    test_review_exchange_acceptance_tdd as fixtures,
)
from tests.unit.tools.test_review_exchange_lifecycle.test_review_exchange_lifecycle_tdd import (
    FakeTime,
)
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_cli_resume import _RequestDiscovery
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    Actor,
    ReviewConfiguration,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_ownership import OwnershipCapability
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume_wait import GlobalReviewerWait, GlobalWaitOutcome

if TYPE_CHECKING:
    from pathlib import Path


def _publish_request(core: ReviewExchangeCore, round_number: int) -> None:
    """Publish the exact fixture context through the real protocol boundary."""
    core.publish_request(fixtures._artifact(core.context, ReviewRole.REQUESTOR, round_number), "Requestor report")


def _review_once(discovery: _RequestDiscovery, core: ReviewExchangeCore, round_number: int) -> None:
    """Discover, claim and answer only the returned exact request."""
    waiter = GlobalReviewerWait(
        rescan_candidates=discovery.rescan, claim_candidate=discovery.claim,
        wait_for_notification=lambda _: False, fallback_poll=lambda: None, poll_interval_seconds=1,
    )
    found = waiter.wait(max_quiet_intervals=0)
    assert found.outcome is GlobalWaitOutcome.FOUND
    capability = discovery.capability(found.candidate)
    core.present_ownership(OwnershipCapability(int(str(capability["ownership_generation"])), str(capability["ownership_token"])))
    core.publish_answer(fixtures._artifact(
        core.context, ReviewRole.REVIEWER, round_number, disposition=ReviewDisposition.CHANGES_REQUESTED,
    ), "Reviewer report")
    assert discovery.rescan() == ()


@pytest.fixture
def prepared_review_families(tmp_path: Path) -> tuple[_RequestDiscovery, ReviewExchangeCore, ReviewExchangeCore]:
    """Prepare real actors without publishing requests or exercising discovery."""
    configuration = ReviewArtifactConfiguration.load(tmp_path)
    configuration.prepare_home()
    (configuration.home / "a.review-mode").write_text("", encoding="utf-8")
    clock = FakeTime()
    discovery = _RequestDiscovery(tmp_path, wall_clock=clock.now)
    context = fixtures._context(tmp_path, ReviewFamily.CODE, "first", step="5")
    core = ReviewExchangeCore(ReviewExchangeStore(derive_artifact_paths(tmp_path, context)), context,
                              fixtures._policy(context), ReviewConfiguration(enabled=True), wall_clock=clock.now)
    core.start()
    context = fixtures._context(tmp_path, ReviewFamily.SPECIFICATION, "later")
    specification = ReviewExchangeCore(ReviewExchangeStore(derive_artifact_paths(tmp_path, context)), context,
                                       fixtures._policy(context), ReviewConfiguration(enabled=True), wall_clock=clock.now)
    return discovery, core, specification


def test_one_discovery_serves_next_round_and_new_family(
    prepared_review_families: tuple[_RequestDiscovery, ReviewExchangeCore, ReviewExchangeCore],
) -> None:
    """An idle reviewer stays global during requestor work and handles a later specification."""
    discovery, core, specification = prepared_review_families
    assert discovery.rescan() == ()
    _publish_request(core, 1)
    _review_once(discovery, core, 1)
    core.pickup_ownership(Actor.REQUESTOR)
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    _publish_request(core, 2)
    _review_once(discovery, core, 2)
    specification.start()
    _publish_request(specification, 1)
    _review_once(discovery, specification, 1)


# eof
