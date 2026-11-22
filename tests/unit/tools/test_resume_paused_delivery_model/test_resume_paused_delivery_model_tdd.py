"""Example tests of the delivery vocabulary and its default ports.

Step 6 of v0.14.0 resume-paused: a checkout fails on an unavailable guard or a
failed action, never on contention or a pending reviewer; the fixed action
budget is 100 seconds; until a profile is pinned every pane is unsupported,
and without Step 7's composed takeover every conditional reviewer stays
pending. Step 7: the default takeover returns each resume report unobserved,
and a report starts with no receiver observation. Step 7 code review round 1:
a pair delivery also names its plan's accepted prompt digest.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    API,
    CODEX_COMMAND,
    CODEX_PANE,
    LogPort,
    World,
    action,
    record,
)
from tools.resume_paused_delivery_model import (
    ACTION_BUDGET,
    ActionReport,
    CheckoutDelivery,
    DeliveryOutcome,
    DeliveryPorts,
    NoTakeover,
    ReceiverState,
    UnpinnedProfiles,
)
from tools.resume_paused_guard import GuardState
from tools.resume_paused_plan_model import ActionKind

if TYPE_CHECKING:
    from tools.resume_paused_delivery_model import Phase, PreSendCheck
    from tools.resume_paused_models import CanonicalRoot, PromptDigest
    from tools.resume_paused_plan_model import PlannedAction

PENDING = ActionReport(action(CODEX_PANE, CODEX_COMMAND, kind=ActionKind.REVIEWER), DeliveryOutcome.PENDING, "takeover-unobserved")
FAILED = ActionReport(action(), DeliveryOutcome.UNCONFIRMED, "acceptance-unproved", failed=True)


@pytest.mark.parametrize(
    ("delivery", "failed"),
    [
        (CheckoutDelivery(API, GuardState.HELD), False),
        (CheckoutDelivery(API, GuardState.UNAVAILABLE), True),
        (CheckoutDelivery(API, GuardState.ACQUIRED, (PENDING,)), False),
        (CheckoutDelivery(API, GuardState.ACQUIRED, (PENDING, FAILED)), True),
    ],
)
def test_a_checkout_fails_on_an_unavailable_guard_or_a_failed_action(delivery: CheckoutDelivery, failed: bool) -> None:  # noqa: FBT001
    """Contention and a pending reviewer are expected outcomes."""
    assert delivery.failed is failed


def test_the_action_budget_is_the_fixed_100_seconds() -> None:
    """Design Q05=A: no human override."""
    assert timedelta(seconds=100) == ACTION_BUDGET


def test_default_ports_refuse_every_pane_and_keep_reviewers_pending() -> None:
    """No pinned profile yet (plan Q05); without Step 7 composition no extra check, no observation, no takeover."""
    world = World()
    ports = DeliveryPorts(world.transport, world.guard, world.clock, world.clock, world.profiles, LogPort(world.log), {}, world.probe)
    planned = action(CODEX_PANE, CODEX_COMMAND, kind=ActionKind.REVIEWER)
    assert UnpinnedProfiles().profile(record()) is None
    assert ports.takeover.reviewer(Pair(), None, planned) == ActionReport(planned, DeliveryOutcome.PENDING, "takeover-unobserved")
    assert ports.takeover.received(Pair(), FAILED) is FAILED
    assert (isinstance(ports.takeover, NoTakeover), ports.checks) == (True, ())


def test_a_report_starts_unobserved() -> None:
    """Step 7: a report carries no receiver observation and no generation until the takeover records them."""
    assert (FAILED.receiver, FAILED.generation) == (ReceiverState.UNOBSERVED, None)


class Pair:
    """A pair delivery the default takeover never uses."""

    @property
    def root(self) -> CanonicalRoot:
        """Return the declared checkout."""
        return API

    @property
    def digest(self) -> PromptDigest | None:
        """Return no accepted prompt; the default takeover never reads it."""
        return None

    def deliver(self, action: PlannedAction, phase: Phase, checks: tuple[PreSendCheck, ...] = ()) -> ActionReport:
        """Fail if the default takeover ever delivered."""
        del phase, checks
        raise AssertionError(action)


# eof
