"""Design Q27=B all-pane idle guard tests over declared listings, captures and screen readings.

Step 7 of v0.15.0 resume-paused: before a Claude reviewer send, every live
Claude pane of the checkout (its subdirectories included, the requestor and
the target included) must rest in TUIOS and read idle under the pinned
Claude screen profile. A busy non-target pane, a busy requestor, a running
local command behind a closed-looking transcript (a busy screen), an
unreadable capture and an unknown layout each keep activation pending; a pane
whose checkout cannot be read cannot be excluded. Captures stay inside the
guard's own budget, and other phases and Codex reviewers pass untouched.

Code review round 1: a question on the target or on another Claude pane
refuses the send even with no blocking reason; a screen reading of the last
pane that spends the budget keeps activation pending; and discovery keeps the
listing's order with one capture per pane.

Code review round 2: the budget expiring between a pane's TUIOS check and its
capture starts no capture on that pane, and whenever the budget expires, no
capture starts with a nonpositive timeout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    FakeClock,
    FakeTransport,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import WEB, live
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    ASKING,
    IDLE_LINES,
    QUESTION,
    REQUESTOR_PANE,
    REVIEWER_PANE,
    ROOT,
    THIRD_PANE,
    WORKING,
    FakeScreens,
    listing,
    planned,
)
from tools.resume_paused_delivery_model import (
    CALL_BOUND_SECONDS,
    Phase,
    Refusal,
    SendStep,
)
from tools.resume_paused_evidence import PaneActivity, PaneObservation
from tools.resume_paused_input import PaneRecord
from tools.resume_paused_pane_guard import (
    GUARD_BUDGET,
    AllPaneIdleGuard,
    ClaudeScreen,
    UnpinnedClaudeScreens,
    checkout_claude_panes,
)
from tools.resume_paused_plan_model import ActionKind
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from datetime import datetime

    from tools.resume_paused_plan_model import PlannedAction

SUBDIRECTORY_PANE = "9a8b7c6d-5e4f-4a3b-9c2d-1e0f9a8b7c6d"
OUTSIDE_PANE = "1b2c3d4e-5f60-4718-8293-a4b5c6d7e8f9"
NEAR_PANE = "0f1e2d3c-4b5a-4968-8776-655443322110"
DRAFT = PaneActivity("idle", "", draft_held=True, question="", ready=True)
SLOW_CAPTURE = 20.0
SECOND_PANE_SAMPLE = 5
LAST_CALL = 8


@dataclass
class SteppingClock(FakeClock):
    """A fake clock that spends the guard's whole budget on one declared call of ``now``, counting the calls."""

    step_at: int = 0
    calls: int = 0

    def now(self) -> datetime:
        """Advance by the whole budget on the declared call, then return the instant."""
        self.calls += 1
        if self.calls == self.step_at:
            self.advance(GUARD_BUDGET.total_seconds())
        return super().now()


def claude_step(observation: PaneObservation, phase: Phase = Phase.REVIEWER, action: PlannedAction | None = None) -> SendStep:
    """Return the imminent send of the Claude reviewer over one fresh listing."""
    action = action or planned(ActionKind.REVIEWER, Host.CLAUDE)
    (target,) = (pane for pane in observation.panes if pane.pane_id == action.pane_id)
    return SendStep(phase, ROOT, action, observation, target)


def guard(observation: PaneObservation, screens: FakeScreens | None = None) -> tuple[AllPaneIdleGuard, FakeTransport, FakeClock]:
    """Return the guard over a transport whose every pane captures the idle lines."""
    transport = FakeTransport([observation], {pane.pane_id: [IDLE_LINES] for pane in observation.panes})
    clock = FakeClock()
    return AllPaneIdleGuard(transport, screens or FakeScreens(), clock), transport, clock


def captured(transport: FakeTransport) -> list[str]:
    """Return the panes the guard captured, in order."""
    return [call[1] for call in transport.calls if call[0] == "capture"]


def third(root: str = str(ROOT.display), host: Host = Host.CLAUDE, pane_id: str = THIRD_PANE) -> PaneRecord:
    """Return one more live pane of the declared host and directory."""
    return live(pane_id, host, root)


def test_every_live_claude_pane_of_the_checkout_must_read_idle() -> None:
    """The all-idle control: requestor, reviewer and a subdirectory pane are captured, other panes are not."""
    observation = listing(
        Host.CLAUDE, third(ROOT.display + "\\docs", pane_id=SUBDIRECTORY_PANE), third(str(WEB), pane_id=OUTSIDE_PANE),
        third(ROOT.display + "iary", pane_id=NEAR_PANE), third(host=Host.CODEX),
    )
    check, transport, _ = guard(observation)
    assert check.check(claude_step(observation)) is None
    assert captured(transport) == [REQUESTOR_PANE, REVIEWER_PANE, SUBDIRECTORY_PANE]


def test_discovery_keeps_the_listing_order_with_one_capture_per_pane() -> None:
    """One linear scan: members come in the listing's order, whatever their UUIDs, and each is captured once."""
    base = listing(Host.CLAUDE, third(ROOT.display + "\\docs", pane_id=SUBDIRECTORY_PANE), third(str(WEB), pane_id=OUTSIDE_PANE))
    observation = PaneObservation(tuple(reversed(base.panes)), base.activity)
    members = checkout_claude_panes(observation, ROOT)
    check, transport, _ = guard(observation)
    assert check.check(claude_step(observation)) is None
    assert not isinstance(members, Refusal)
    expected = [SUBDIRECTORY_PANE, REVIEWER_PANE, REQUESTOR_PANE]
    assert ([pane.pane_id for pane in members], captured(transport)) == (expected, expected)
    assert expected != sorted(expected)


@pytest.mark.parametrize(
    ("pane_id", "activity", "reason"),
    [
        (THIRD_PANE, WORKING, "claude-pane-busy"),
        (REQUESTOR_PANE, WORKING, "claude-pane-busy"),
        (THIRD_PANE, QUESTION, "claude-pane-blocked"),
        (THIRD_PANE, ASKING, "claude-pane-question"),
        (REVIEWER_PANE, ASKING, "claude-pane-question"),
        (THIRD_PANE, DRAFT, "claude-pane-draft"),
        (THIRD_PANE, None, "claude-pane-state-unknown"),
    ],
)
def test_a_pane_that_does_not_rest_keeps_activation_pending(pane_id: str, activity: PaneActivity | None, reason: str) -> None:
    """A busy non-target pane, a requestor whose turn has not closed, a question on any pane, a draft or no activity: no send."""
    observation = listing(Host.CLAUDE, third())
    declared = dict(observation.activity)
    if activity is None:
        declared.pop(pane_id)
    else:
        declared[pane_id] = activity
    check, _, _ = guard(PaneObservation(observation.panes, declared))
    assert check.check(claude_step(PaneObservation(observation.panes, declared))) == Refusal(reason)


@pytest.mark.parametrize(
    ("reading", "reason"),
    [(ClaudeScreen.BUSY, "claude-pane-busy"), (ClaudeScreen.UNKNOWN, "claude-pane-unknown-layout")],
)
def test_a_running_local_command_or_an_unknown_layout_keeps_activation_pending(reading: ClaudeScreen, reason: str) -> None:
    """A screen still running a local command (its transcript looks closed) or an unknown layout is not idle."""
    observation = listing(Host.CLAUDE, third())
    check, _, _ = guard(observation, FakeScreens({THIRD_PANE: reading}))
    assert check.check(claude_step(observation)) == Refusal(reason)


def test_an_unreadable_capture_keeps_activation_pending() -> None:
    """A capture that fails proves nothing."""
    observation = listing(Host.CLAUDE)
    check, transport, _ = guard(observation)
    transport.captures[REVIEWER_PANE] = [None]
    assert check.check(claude_step(observation)) == Refusal("claude-pane-unreadable")


def test_a_claude_pane_whose_checkout_cannot_be_read_cannot_be_excluded() -> None:
    """An unreadable directory of a Claude pane keeps activation pending; a Codex one is ignored."""
    codex = listing(Host.CLAUDE, third("relative\\path", Host.CODEX))
    claude = listing(Host.CLAUDE, third("relative\\path"))
    assert checkout_claude_panes(codex, ROOT) == codex.panes[:2]
    assert checkout_claude_panes(claude, ROOT) == Refusal("claude-pane-checkout-unknown")


def test_a_pane_that_cannot_be_classified_refuses_the_send_before_any_capture() -> None:
    """The guard itself stops the send when a Claude pane's checkout cannot be read."""
    observation = listing(Host.CLAUDE, third("relative\\path"))
    check, transport, _ = guard(observation)
    assert check.check(claude_step(observation)) == Refusal("claude-pane-checkout-unknown")
    assert captured(transport) == []


def test_contradictory_host_evidence_in_the_checkout_fails_the_guard() -> None:
    """A pane of the checkout claiming both hosts is a classification failure; outside the checkout it is ignored."""
    contradictory = PaneRecord(THIRD_PANE, "s", "both", ROOT.display, "claude-code", ("codex",), None)
    outside = PaneRecord(OUTSIDE_PANE, "s", "both", str(WEB), "claude-code", ("codex",), None)
    kept = checkout_claude_panes(listing(Host.CLAUDE, outside), ROOT)
    assert checkout_claude_panes(listing(Host.CLAUDE, contradictory), ROOT) == Refusal("pane-host-contradictory", failed=True)
    assert not isinstance(kept, Refusal)
    assert [pane.pane_id for pane in kept] == [REQUESTOR_PANE, REVIEWER_PANE]


def test_each_capture_is_bounded_by_the_guard_budget() -> None:
    """A slow capture leaves the next one only what is left of the guard's own budget."""
    observation = listing(Host.CLAUDE)
    check, transport, clock = guard(observation)

    def slow_first(count: int) -> None:
        clock.advance(SLOW_CAPTURE if count == 1 else 0)

    transport.on_capture = slow_first
    assert check.check(claude_step(observation)) is None
    bounds = [bound for name, bound in transport.bounds if name == "capture"]
    assert bounds == [CALL_BOUND_SECONDS, GUARD_BUDGET.total_seconds() - SLOW_CAPTURE]


def test_a_capture_completed_after_the_budget_is_not_acted_on() -> None:
    """A capture that spends the whole budget refuses the send, even with an idle screen."""
    observation = listing(Host.CLAUDE)
    check, transport, clock = guard(observation)

    def spend_all(count: int) -> None:
        del count
        clock.advance(GUARD_BUDGET.total_seconds())

    transport.on_capture = spend_all
    assert check.check(claude_step(observation)) == Refusal("idle-guard-deadline")
    assert len(captured(transport)) == 1


def test_no_capture_starts_once_the_budget_is_spent() -> None:
    """A slow screen reading leaves no budget, so the next pane is never captured."""
    observation = listing(Host.CLAUDE)
    screens = FakeScreens()
    check, transport, clock = guard(observation, screens)
    screens.on_read = lambda: clock.advance(GUARD_BUDGET.total_seconds())
    assert check.check(claude_step(observation)) == Refusal("idle-guard-deadline")
    assert len(captured(transport)) == 1


def stepping(step_at: int) -> tuple[AllPaneIdleGuard, FakeTransport, PaneObservation]:
    """Return the guard over the requestor and reviewer, whose clock spends the budget on one declared call."""
    observation = listing(Host.CLAUDE)
    transport = FakeTransport([observation], {pane.pane_id: [IDLE_LINES] for pane in observation.panes})
    return AllPaneIdleGuard(transport, FakeScreens(), SteppingClock(step_at=step_at)), transport, observation


def test_a_budget_spent_between_the_pane_check_and_its_capture_starts_no_capture() -> None:
    """The budget expires as the second pane's capture is about to start: that pane is never captured."""
    check, transport, observation = stepping(SECOND_PANE_SAMPLE)
    assert (check.check(claude_step(observation)), captured(transport)) == (Refusal("idle-guard-deadline"), [REQUESTOR_PANE])


@pytest.mark.parametrize("step_at", range(1, LAST_CALL + 1))
def test_no_capture_ever_starts_with_a_nonpositive_timeout(step_at: int) -> None:
    """Wherever the budget expires, every capture that starts gets the positive time left, and the send never passes late."""
    check, transport, observation = stepping(step_at)
    refusal = check.check(claude_step(observation))
    bounds = [bound for name, bound in transport.bounds if name == "capture"]
    assert all(bound > 0 for bound in bounds)
    assert refusal in {None, Refusal("idle-guard-deadline")}


def test_a_last_screen_reading_that_spends_the_budget_keeps_activation_pending() -> None:
    """An idle reading of the last pane that completes after the budget never authorizes the send."""
    observation = listing(Host.CLAUDE)
    screens = FakeScreens()
    check, transport, clock = guard(observation, screens)

    def spend_on_last() -> None:
        if len(screens.read_panes) == len(observation.panes):
            clock.advance(GUARD_BUDGET.total_seconds())

    screens.on_read = spend_on_last
    refusal = check.check(claude_step(observation))
    assert (refusal, captured(transport), screens.read_panes) == (Refusal("idle-guard-deadline"), [REQUESTOR_PANE, REVIEWER_PANE], [REQUESTOR_PANE, REVIEWER_PANE])


@pytest.mark.parametrize("phase", [Phase.CLEAR, Phase.RESUME, Phase.RECOVERY])
def test_other_phases_pass_untouched(phase: Phase) -> None:
    """Only a reviewer send is guarded."""
    observation = listing(Host.CLAUDE, third(), activity={THIRD_PANE: WORKING})
    check, transport, _ = guard(observation)
    assert check.check(claude_step(observation, phase)) is None
    assert captured(transport) == []


def test_a_codex_reviewer_send_is_not_guarded() -> None:
    """The guard covers Claude reviewer activations; a Codex reviewer has its own idle proof."""
    observation = listing(Host.CODEX, third(), activity={THIRD_PANE: WORKING})
    check, transport, _ = guard(observation)
    assert check.check(claude_step(observation, action=planned(ActionKind.REVIEWER, Host.CODEX))) is None
    assert captured(transport) == []


def test_no_pinned_claude_screen_profile_reads_every_screen_unknown() -> None:
    """Until a Claude screen profile is pinned, every capture is unknown and every activation stays pending."""
    observation = listing(Host.CLAUDE)
    transport = FakeTransport([observation], {pane.pane_id: [IDLE_LINES] for pane in observation.panes})
    check = AllPaneIdleGuard(transport, UnpinnedClaudeScreens(), FakeClock())
    assert check.check(claude_step(observation)) == Refusal("claude-pane-unknown-layout")
