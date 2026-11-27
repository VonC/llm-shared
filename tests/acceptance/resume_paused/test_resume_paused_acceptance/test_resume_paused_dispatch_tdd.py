"""Exercise dispatch reservations and their receiver checks against one routed checkout."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from tests.acceptance.resume_paused.fakes import (
    NATURES,
    REQUESTOR_PANE,
    REVIEWER_PANE,
    Scenario,
)
from tools.resume_paused_artifacts import read_checkout_snapshot
from tools.resume_paused_claim import marked_claim_verifier
from tools.resume_paused_delivery_model import Phase
from tools.resume_paused_dispatch import Dispatch, SharedDelivery, read_dispatch
from tools.resume_paused_input import CarriedIdentity, TuiosDiscovery
from tools.resume_paused_marker import marker_in_command
from tools.resume_paused_models import ArtifactError, PromptDigest, SessionRole
from tools.resume_paused_plan_model import ActionKind, PlannedAction
from tools.resume_paused_planner import ExchangeObserver, marked_command
from tools.resume_paused_profiles import Host
from tools.resume_paused_review import ExchangeObservationKind, ExchangeSnapshot
from tools.resume_paused_validation import ValidationRequest, default_validator
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from pathlib import Path


def requestor(scenario: Scenario) -> PlannedAction:
    """Build the action bound to this requestor and its current round."""
    pane = scenario.requestor.record
    marker = scenario.checkout.marker(pane.pane_id, SessionRole.REQUESTOR, "1" * 32)
    command = marked_command(Host.CODEX, ActionKind.RESUME, marker)
    return PlannedAction(ActionKind.RESUME, marker.role, Host.CODEX, pane.session, pane.pane_id, pane.name, command)


@pytest.mark.parametrize(("first", "second", "reason"), [
    (Phase.RESUME, Phase.RESUME, "dispatch-already-reserved"),
    (Phase.RESUME, Phase.CLEAR, "dispatch-already-reserved"),
    (Phase.CLEAR, Phase.RESUME, "clear-already-reserved"),
])
def test_conflicting_launch_cannot_reserve_input(tmp_path: Path, first: Phase, second: Phase, reason: str) -> None:
    """An exclusive reservation survives another attempt at the same prompt."""
    scenario = Scenario(tmp_path)
    action = requestor(scenario)
    assert action.command
    pane = scenario.requestor.record
    digest = PromptDigest.of(scenario.checkout.prompt)
    shared = SharedDelivery(scenario.runtime().exchanges)
    shared.check(pane, action, first, digest)
    other = replace(marker_in_command(action.command), launch_id="2" * 32)
    with pytest.raises(ArtifactError, match=reason):
        shared.check(pane, replace(action, command=marked_command(action.host, action.kind, other)), second, digest)
    existing = read_dispatch(read_checkout_snapshot(scenario.root), first)
    assert existing is not None
    assert existing.command == action.command


@pytest.mark.parametrize("payload", ['{"command":1,"generation":1}', '{"command":"x","generation":true}'])
def test_malformed_reservation_is_a_retry_fence(tmp_path: Path, payload: str) -> None:
    """Incorrect fields or generation types retain the unreadable reservation."""
    scenario = Scenario(tmp_path)
    snapshot = read_checkout_snapshot(scenario.root)
    assert snapshot.home is not None
    assert snapshot.prompt is not None
    path = snapshot.home / f"a.resume-paused.{snapshot.prompt.digest.value}.resume.local.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ArtifactError, match="dispatch-unreadable"):
        read_dispatch(snapshot, Phase.RESUME)
    assert path.read_text(encoding="utf-8") == payload


def test_unavailable_reservation_storage(tmp_path: Path) -> None:
    """A missing checkout cannot supply history, and a failed exclusive write is reported."""
    with pytest.raises(ArtifactError, match="dispatch-unreadable"):
        read_dispatch(read_checkout_snapshot(tmp_path), Phase.RESUME)
    with pytest.raises(ArtifactError, match="dispatch-write-failed"):
        Dispatch("command", None).save(tmp_path / "missing" / "reservation.json")


def test_changed_assignment_and_consumption_prevent_dispatch(tmp_path: Path) -> None:
    """Revalidate the intended bytes, assignment and consumption before input."""
    scenario = Scenario(tmp_path)
    action = requestor(scenario)
    assert action.command
    marker = marker_in_command(action.command)
    pane = scenario.requestor.record
    shared = SharedDelivery(scenario.runtime().exchanges)
    digest = PromptDigest.of(scenario.checkout.prompt)
    with pytest.raises(ArtifactError, match="dispatch-prompt-changed"):
        shared.check(pane, action, Phase.RESUME, PromptDigest.of(b"replacement"))
    wrong = marked_command(action.host, action.kind, replace(marker, binding="0" * 64))
    with pytest.raises(ArtifactError, match="dispatch-binding-changed"):
        shared.check(pane, replace(action, command=wrong), Phase.RESUME, digest)
    scenario.checkout.consume(marker)
    with pytest.raises(ArtifactError, match="dispatch-prompt-consumed"):
        shared.check(pane, action, Phase.RESUME, digest)
    assert read_dispatch(read_checkout_snapshot(scenario.root), Phase.RESUME) is None


def test_missing_exchange_generation_blocks_reservation(tmp_path: Path) -> None:
    """An unobservable generation cannot authorize any input to the pair."""
    scenario = Scenario(tmp_path)
    observer = Mock(spec=ExchangeObserver)
    observer.observe.return_value = ExchangeSnapshot(ExchangeObservationKind.OBSERVED, "pair")
    with pytest.raises(ArtifactError, match="dispatch-exchange-unavailable"):
        SharedDelivery(observer).check(scenario.requestor.record, requestor(scenario), Phase.RESUME, PromptDigest.of(scenario.checkout.prompt))


def test_reviewer_requires_a_proved_takeover(tmp_path: Path) -> None:
    """An unused requestor prompt authorizes neither reviewer delivery nor acceptance."""
    scenario = Scenario(tmp_path)
    shared = SharedDelivery(scenario.runtime().exchanges)
    pane = scenario.reviewer.record
    marker = scenario.checkout.marker(pane.pane_id, SessionRole.REVIEWER, "2" * 32)
    command = marked_command(Host.CLAUDE, ActionKind.REVIEWER, marker)
    action = PlannedAction(ActionKind.REVIEWER, marker.role, Host.CLAUDE, pane.session, pane.pane_id, pane.name, command)
    digest = PromptDigest.of(scenario.checkout.prompt)
    assert not shared.accepted(pane, action, digest)
    assert not shared.accepted(pane, replace(action, command=None), digest)
    with pytest.raises(ArtifactError, match="dispatch-takeover-changed"):
        shared.check(pane, action, Phase.REVIEWER, digest)


@pytest.mark.parametrize("reason", ["dispatch-generation-changed", "carried-pane-mismatch"])
def test_receiver_rechecks_reservation_at_validation_and_claim(tmp_path: Path, reason: str) -> None:
    """Both receiver entry points reject a stale generation or another pane's carried identity."""
    scenario = Scenario(tmp_path)
    action = requestor(scenario)
    assert action.command
    marker = marker_in_command(action.command)
    shared = SharedDelivery(scenario.runtime().exchanges)
    shared.check(scenario.requestor.record, action, Phase.RESUME, PromptDigest.of(scenario.checkout.prompt))
    scenario.checkout.consume(marker)
    if reason == "dispatch-generation-changed":
        claim_selected(scenario.checkout.core, ReviewRole.REVIEWER, NATURES[Host.CLAUDE], round_number=1, occurrence=1, override=True)
    carried = CarriedIdentity(REVIEWER_PANE if reason == "carried-pane-mismatch" else REQUESTOR_PANE, marker.launch_id)
    env = {"TUIOS_PANE_ID": marker.pane_id}
    checker = default_validator(env, scenario.checkout.clock.now)
    checker.discovery = TuiosDiscovery(scenario.tuios)
    assert checker.validate(ValidationRequest(scenario.root, action.command, Host.CODEX, carried)).reasons == (reason,)
    verify = marked_claim_verifier(scenario.root, marker.render(), ReviewRole.REQUESTOR, Host.CODEX, carried, environ=env)
    before = scenario.checkout.store.read_coordination(required=True)
    with pytest.raises(ReviewExchangeError, match=reason):
        claim_selected(scenario.checkout.core, ReviewRole.REQUESTOR, NATURES[Host.CODEX], round_number=1, occurrence=1, override=True, marked=verify)
    assert scenario.checkout.store.read_coordination(required=True) == before


# eof
