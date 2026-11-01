"""Exercise persistent discovery, including concurrent and interrupted publication.

The first round is declared as answered inside measured setup. Each case
then drives a real publication, discovery, claim and answer cycle with the
same discovery object: the code exchange's next round or a later family.
Only the later-family case constructs that second exchange.
"""

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
from tests.unit.tools.test_review_resume.prepared_phase import prepare_phase
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
    from collections.abc import Callable
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
def prepared_code_review(
    tmp_path: Path, stable_review_inputs: Callable[[], None],
) -> tuple[_RequestDiscovery, ReviewExchangeCore]:
    """Prepare the first actor without unrelated later-family prerequisites."""
    configuration = ReviewArtifactConfiguration.load(tmp_path)
    configuration.prepare_home()
    (configuration.home / "a.review-mode").write_text("", encoding="utf-8")
    stable_review_inputs()
    clock = FakeTime()
    discovery = _RequestDiscovery(tmp_path, wall_clock=clock.now)
    context = fixtures._context(tmp_path, ReviewFamily.CODE, "first", step="5")
    core = ReviewExchangeCore(ReviewExchangeStore(derive_artifact_paths(tmp_path, context)), context,
                              fixtures._policy(context), ReviewConfiguration(enabled=True), wall_clock=clock.now)
    prepare_phase(core, context, clock, "started")
    return discovery, core


@pytest.fixture
def first_round_answered(
    prepared_code_review: tuple[_RequestDiscovery, ReviewExchangeCore],
) -> tuple[_RequestDiscovery, ReviewExchangeCore]:
    """Declare the answered first round before exercising the next discovery."""
    discovery, core = prepared_code_review
    assert discovery.rescan() == ()
    prepare_phase(core, core.context, FakeTime(), "answer")
    assert discovery.rescan() == ()
    return prepared_code_review


def test_one_discovery_serves_the_next_round(
    first_round_answered: tuple[_RequestDiscovery, ReviewExchangeCore],
) -> None:
    """An idle reviewer stays global during requestor work and serves round 2."""
    discovery, core = first_round_answered
    core.pickup_ownership(Actor.REQUESTOR)
    core.consume_answer(reviewed_work_changed=True)
    core.continue_round()
    _publish_request(core, 2)
    _review_once(discovery, core, 2)


def test_one_discovery_serves_a_later_family(
    first_round_answered: tuple[_RequestDiscovery, ReviewExchangeCore], tmp_path: Path,
) -> None:
    """The same idle reviewer handles a later specification request."""
    discovery, _ = first_round_answered
    clock = FakeTime()
    context = fixtures._context(tmp_path, ReviewFamily.SPECIFICATION, "later")
    specification = ReviewExchangeCore(ReviewExchangeStore(derive_artifact_paths(tmp_path, context)), context,
                                       fixtures._policy(context), ReviewConfiguration(enabled=True), wall_clock=clock.now)
    prepare_phase(specification, context, clock, "started")
    _publish_request(specification, 1)
    _review_once(discovery, specification, 1)


def test_discovery_defers_publication_until_its_locked_snapshot_is_complete(
    prepared_code_review: tuple[_RequestDiscovery, ReviewExchangeCore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A visible request with an unfinished transcript never terminates the global waiter."""
    discovery, core = prepared_code_review
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
    prepared_code_review: tuple[_RequestDiscovery, ReviewExchangeCore],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deferring a busy publisher never hides evidence left damaged after its lock releases."""
    discovery, core = prepared_code_review
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
