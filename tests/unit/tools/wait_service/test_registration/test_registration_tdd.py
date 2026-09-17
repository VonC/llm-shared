"""Keep early outcomes and failed arming independent under exact intent retries."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.wait_service.test_monitoring.test_monitoring_tdd import (
    intent,
    settle,
)
from tools.wait_service.models import (
    Capability,
    HostBinding,
    NormalEnd,
    Observation,
    Recipient,
    WaitError,
)
from tools.wait_service.monitoring import SourceMonitor, SourcePolicy
from tools.wait_service.registration import RegistrationService
from tools.wait_service.store import WaitStore
from tools.wait_service.synthetic import (
    ControlledIO,
    SyntheticClock,
    SyntheticHost,
    SyntheticSource,
)
from tools.wait_service.work import WorkResult

if TYPE_CHECKING:
    from pathlib import Path


pytestmark = pytest.mark.timeout(10)


def test_failed_arming_retains_early_result_and_identical_retry(tmp_path: Path) -> None:
    """Preparation survives route failure; retry returns one wait and one outcome."""
    clock, workers = SyntheticClock(100.0), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    requested = intent()
    source.ready(requested.source, completed_utc=99.0)
    host.error = WaitError("route-unavailable")
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        preparing = service.register(requested)
        assert preparing.state == "preparing"
        settle(monitor, workers)
        assert store.get_registration(preparing.wait_id).state == "preparing"
        event = store.get_event(preparing.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        host.error = None
        service.register(requested)
        settle(monitor, workers)
        armed = service.register(requested)
        assert armed.wait_id == preparing.wait_id
        assert armed.state == "armed"
        assert store.get_event(armed.wait_id) == event
        expected_calls = 2
        assert host.arm_calls == expected_calls
        monitor.close()


@pytest.mark.parametrize("field", ["recipient", "role", "provenance"])
def test_registration_rejects_counterpart_and_unverified_provenance(tmp_path: Path, field: str) -> None:
    """Sharing a source never permits registration on behalf of another role/session."""
    clock, workers = SyntheticClock(), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    requested = intent()
    invalid = {
        "recipient": replace(requested, recipient=replace(requested.recipient, thread_id="other")),
        "role": replace(requested, role="reviewer"),
        "provenance": replace(requested, provenance="claiming-permission"),
    }[field]
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        with pytest.raises(WaitError, match="registration-authority"):
            service.register(invalid)
        assert list(store.recover_registrations()) == []
        monitor.close()


@pytest.mark.parametrize(("capability", "gate", "state"), [
    (Capability.STRICT, NormalEnd.DIRECT, "armed"),
    (Capability.FUNCTIONAL, NormalEnd.HOST_GATED, "armed"),
    (Capability.RETAINED, NormalEnd.UNAVAILABLE, "retained"),
    (Capability.STRICT, NormalEnd.UNAVAILABLE, "preparing"),
    (Capability.PENDING, NormalEnd.UNAVAILABLE, "preparing"),
    (Capability.UNAVAILABLE, NormalEnd.UNAVAILABLE, "preparing"),
])
def test_only_usable_declared_routes_acknowledge_arming(tmp_path: Path, capability: Capability, gate: NormalEnd, state: str) -> None:
    """Arming acknowledges committed capability and normal-end gate evidence."""
    clock, workers = SyntheticClock(), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    host.support, host.gate = capability, gate
    requested = intent()
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        registration = service.register(requested)
        assert registration.state == "preparing"
        monitor.pump()
        assert host.arm_calls == 0
        workers.run_all()
        monitor.pump()
        assert store.get_registration(registration.wait_id).state == "preparing"
        settle(monitor, workers)
        assert store.get_registration(registration.wait_id).state == state
        assert not host.normal_end(host.arm(requested.recipient))
        monitor.close()


def test_invalid_recipient_can_retry_arming_while_source_pending(tmp_path: Path) -> None:
    """An exact retry makes progress even when the existing watch has no new hint."""
    clock, workers = SyntheticClock(), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    host.valid = False
    requested = intent()
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        registration = service.register(requested)
        settle(monitor, workers)
        assert store.get_registration(registration.wait_id).diagnostic == "recipient-unavailable"
        host.valid = True
        service.register(requested)
        settle(monitor, workers)
        assert store.get_registration(registration.wait_id).state == "armed"
        assert store.get_event(registration.wait_id) is None
        monitor.close()


def test_wrong_binding_recipient_cannot_arm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Host evidence must agree with the independently authenticated caller."""
    clock, workers = SyntheticClock(), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    requested = intent()

    def wrong(recipient: Recipient) -> HostBinding:
        return HostBinding(replace(recipient, thread_id="other"), "incarnation", Capability.STRICT, NormalEnd.DIRECT, "v1", "proof")

    monkeypatch.setattr(host, "arm", wrong)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        registration = service.register(requested)
        settle(monitor, workers)
        assert store.get_registration(registration.wait_id).diagnostic == "route-identity-mismatch"
        assert store.get_binding(registration.wait_id) is None
        monitor.close()


def test_unknown_policy_rejected_before_preparation(tmp_path: Path) -> None:
    """A source cannot silently fall back to a guessed kind or policy version."""
    clock, workers = SyntheticClock(), ControlledIO()
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {})
        requested = intent()
        service = RegistrationService(store, monitor, SyntheticHost(), requested.recipient, "requestor")
        with pytest.raises(WaitError, match="source-policy-unavailable"):
            service.register(requested)
        assert list(store.recover_registrations()) == []
        monitor.close()


@pytest.mark.parametrize("phase", ["before-subscribe", "during-read", "during-arm", "before-normal-end"])
def test_completion_at_each_registration_boundary_is_retained(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str) -> None:
    """Early completion is independent of route arming and the registering turn."""
    clock, workers = SyntheticClock(), ControlledIO()
    source, host = SyntheticSource(clock), SyntheticHost()
    requested = intent()
    original_arm = host.arm

    def complete_and_arm(recipient: Recipient) -> HostBinding:
        source.ready(requested.source)
        return original_arm(recipient)

    if phase == "before-subscribe":
        source.ready(requested.source)
    elif phase == "during-read":
        source.on_read = source.ready
    elif phase == "during-arm":
        monkeypatch.setattr(host, "arm", complete_and_arm)
    with WaitStore(tmp_path / "wait.sqlite3") as store:
        monitor = SourceMonitor(store, clock, workers, {("synthetic", "v1"): (source, SourcePolicy())})
        service = RegistrationService(store, monitor, host, requested.recipient, "requestor")
        registration = service.register(requested)
        settle(monitor, workers)
        if phase == "before-normal-end":
            source.ready(requested.source)
            settle(monitor, workers)
        event = store.get_event(registration.wait_id)
        assert event is not None
        assert event.outcome.kind == "ready"
        assert not host.ended
        assert service.register(requested).state == "armed"
        monitor.close()


def test_source_evidence_cannot_acknowledge_host_arming(tmp_path: Path) -> None:
    """A misdirected worker result remains a retryable preparation failure."""
    clock, workers = SyntheticClock(), ControlledIO()
    with WaitStore(tmp_path / "wait.db") as store:
        monitor = SourceMonitor(store, clock, workers, {})
        requested = intent()
        registration = store.register(requested, clock.utc())
        service = RegistrationService(store, monitor, SyntheticHost(), requested.recipient, "requestor")
        service._armed(registration, WorkResult(Observation("ready", requested.source.generation, 0), 0, uncertain=False))
        assert store.get_registration(registration.wait_id).state == "preparing"
        assert store.get_registration(registration.wait_id).diagnostic == "invalid-host-result"
        monitor.close()


# eof
