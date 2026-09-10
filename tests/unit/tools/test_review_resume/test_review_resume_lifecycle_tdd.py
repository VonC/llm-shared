"""Exercise persistent discovery, including concurrent and interrupted publication."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Event
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
    ReviewExchangeError,
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


def test_discovery_defers_publication_until_its_locked_snapshot_is_complete(
    prepared_review_families: tuple[_RequestDiscovery, ReviewExchangeCore, ReviewExchangeCore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A visible request with an unfinished transcript never terminates the global waiter."""
    discovery, core, _ = prepared_review_families
    published, finish = Event(), Event()
    # This race requires the real lock bypassed by the unit suite's fast fixture.
    monkeypatch.setattr(core.store, "transition_lock", core.store.ownership_store.transition_lock)
    publish = core.store.publish_request

    def pause_after_request(content: str) -> None:
        """Expose the exact partial-publication window until the reader observes it."""
        publish(content)
        published.set()
        assert finish.wait(timeout=5)

    monkeypatch.setattr(core.store, "publish_request", pause_after_request)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_publish_request, core, 1)
        try:
            assert published.wait(timeout=5)
            assert discovery.rescan() == ()
        finally:
            finish.set()
        future.result(timeout=5)
    candidates = discovery.rescan()
    assert len(candidates) == 1
    assert discovery.claim(candidates[0])


def test_unlocked_interrupted_publication_still_fails_closed(
    prepared_review_families: tuple[_RequestDiscovery, ReviewExchangeCore, ReviewExchangeCore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deferring a busy publisher never hides evidence left damaged after its lock releases."""
    discovery, core, _ = prepared_review_families
    publish = core.store.publish_request
    failure = "publication interrupted after request became visible"

    def interrupt_after_request(content: str) -> None:
        """Leave the production publication marker behind, like a failed writer."""
        publish(content)
        raise OSError(failure)

    monkeypatch.setattr(core.store, "publish_request", interrupt_after_request)
    with pytest.raises(OSError, match=failure):
        _publish_request(core, 1)
    with pytest.raises(ReviewExchangeError, match="trustworthy review status"):
        discovery.rescan()


# eof
