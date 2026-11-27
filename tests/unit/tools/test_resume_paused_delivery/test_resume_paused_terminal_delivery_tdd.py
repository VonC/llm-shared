"""Exercise changes between terminal preparation, dispatch and acceptance within one send."""

from __future__ import annotations

from dataclasses import replace
from unittest.mock import Mock

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    CLAUDE_PANE,
    HUMAN,
    World,
    action,
    checkout,
    observation,
)
from tools.resume_paused_delivery import deliver_run
from tools.resume_paused_delivery_model import (
    ACTION_BUDGET,
    ActionReport,
    ClearOutcome,
    DeliveryOutcome,
)
from tools.resume_paused_dispatch import SharedDelivery
from tools.resume_paused_marker import Marker
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_plan_model import ActionKind, RunPlan
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import Host

BORDER = "\u2500" * 12
EDITOR = (BORDER, "\u276f \x1b[2mSuggestion\x1b[0m", BORDER, "  ? for shortcuts")


def deliver(world: World, shared: Mock, *, clear: bool = False) -> ActionReport:
    """Deliver one Claude requestor action through the shared dispatch port."""
    marker = Marker("a" * 32, CLAUDE_PANE, SessionRole.REQUESTOR, "b" * 64)
    command = marked_command(Host.CLAUDE, ActionKind.RESUME, marker)
    plan = RunPlan(dry_run=False, failures=(), checkouts=(checkout(action(command=command, clear=clear)),))
    result, = deliver_run(plan, HUMAN, replace(world.ports(), shared=shared))
    report, = result.reports
    return report


@pytest.mark.parametrize(("capture", "reason"), [
    (None, "capture-failed"),
    ((BORDER, "\u276f unsaved draft", BORDER), "pane-draft"),
])
def test_last_capture_protects_input(capture: tuple[str, ...] | None, reason: str) -> None:
    """A lost capture or new draft just before dispatch stops the first ask."""
    world = World()
    world.transport.captures[CLAUDE_PANE] = [capture]
    shared = Mock(spec=SharedDelivery)
    report = deliver(world, shared)
    assert (report.reason, world.transport.sent()) == (reason, [])
    shared.check.assert_not_called()


def test_refused_reservation_prevents_ask() -> None:
    """No transport call may type after the final reservation refuses."""
    world = World()
    world.transport.captures[CLAUDE_PANE] = [EDITOR]
    shared = Mock(spec=SharedDelivery)
    shared.check.side_effect = ArtifactError("manual-resume-attempt")
    assert deliver(world, shared).reason == "manual-resume-attempt"
    assert not world.transport.sent()


def test_expired_acceptance_does_not_start_another_capture() -> None:
    """A durable evidence read that spends the budget ends the send immediately."""
    world = World()
    world.transport.captures[CLAUDE_PANE] = [EDITOR]
    shared = Mock(spec=SharedDelivery)

    def expire(*_args: object) -> bool:
        world.clock.advance(ACTION_BUDGET.total_seconds())
        return False

    shared.accepted.side_effect = expire
    assert deliver(world, shared).outcome is DeliveryOutcome.UNCONFIRMED
    assert [call[0] for call in world.transport.calls] == ["observe", "capture", "ask"]


@pytest.mark.parametrize("available", [True, False])
def test_clear_confirmation_requires_a_fresh_eligible_target(available: bool) -> None:  # noqa: FBT001
    """Failed discovery or a vanished target leaves the clear unconfirmed and prevents resume."""
    world = World()
    world.transport.captures[CLAUDE_PANE] = [EDITOR]
    world.transport.observations.append(observation() if available else None)
    report = deliver(world, Mock(spec=SharedDelivery), clear=True)
    assert (report.reason, report.clear) == ("clear-unconfirmed", ClearOutcome.UNCONFIRMED)
    assert [call[-1] for call in world.transport.sent()] == ["/clear"]


# eof
