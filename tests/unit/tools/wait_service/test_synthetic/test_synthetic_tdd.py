"""Synthetic ports preserve transport identity without claiming workflow authority."""

from dataclasses import replace

import pytest

from tests.unit.tools.wait_service.test_monitoring.test_monitoring_tdd import intent
from tools.wait_service.models import Capability, Event, Observation, Outcome
from tools.wait_service.synthetic import SyntheticHost

pytestmark = pytest.mark.timeout(10)


def test_host_transport_receipt_and_explicit_rearm() -> None:
    """The fixture distinguishes normal end, transport acceptance and incarnation."""
    host = SyntheticHost()
    recipient = intent().recipient
    binding = host.arm(recipient)
    observation = Observation("ready", "generation", 0)
    event = Event("event", "wait", Outcome("ready", observation, "indefinite", clock_uncertain=False), 0)
    delivery = host.deliver(event, binding)
    assert delivery.event_id == event.event_id
    assert delivery.incarnation == binding.incarnation
    assert host.reconcile(delivery) == delivery
    assert not host.normal_end(binding)
    host.ended = True
    assert host.normal_end(binding)
    rearmed = host.rearm(binding)
    assert rearmed.recipient == recipient
    assert rearmed.incarnation != binding.incarnation


def test_fixture_cannot_advertise_support_for_production_hosts() -> None:
    """A synthetic probe does not confer installed production-route support."""
    host = SyntheticHost()
    recipient = replace(intent().recipient, host="production")
    assert host.capability(recipient) == Capability.UNAVAILABLE
    assert not host.validate(recipient)


# eof
