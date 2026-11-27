"""Example tests of the fresh pre-send checks of resume-paused delivery.

Step 6 of v0.15.0 resume-paused: before every send, the planned full pane
UUID must still be listed once, in its session, with its host and checkout,
unprotected and eligible; the recovery Enter tolerates only the pane's own
unsubmitted command. ``PlanRecheck`` replans the checkout through the real
Step 5 planner over the declared planner world, so a changed prompt digest,
a later duplicate, an uncertain history or a removed prompt refuses the send,
while only the fresh launch id may differ.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from itertools import count
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    API,
    CLAUDE_PANE,
    CODEX_PANE,
    HUMAN,
    IDLE,
    WEB,
    action,
    observation,
    record,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import World, snapshot
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
)
from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_delivery_checks import (
    PlanRecheck,
    TargetContext,
    target_refusal,
)
from tools.resume_paused_delivery_model import Phase, Refusal, SendStep
from tools.resume_paused_evidence import (
    ObservedCommand,
    PaneActivity,
    PaneObservation,
    ScreenVerdict,
)
from tools.resume_paused_models import PromptDigest
from tools.resume_paused_plan_model import ActionKind, CheckoutOutcome, CheckoutPlan
from tools.resume_paused_planner import PlannerPorts, plan_checkout

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_models import CanonicalRoot
    from tools.resume_paused_plan_model import PlannedAction, PlanRequest

LATER = datetime(2026, 11, 17, 17, 0, tzinfo=UTC)
WORKING = PaneActivity("working", "", draft_held=False, question="", ready=False)


class Probe:
    """Declared screen verdict for a busy Codex pane."""

    def __init__(self, verdict: ScreenVerdict = ScreenVerdict.UNSUPPORTED) -> None:
        """Keep the declared verdict."""
        self.verdict = verdict

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the declared verdict."""
        del pane
        return self.verdict


def context(request: PlanRequest = HUMAN, verdict: ScreenVerdict = ScreenVerdict.UNSUPPORTED) -> TargetContext:
    """Return the checks context of the declared checkout."""
    return TargetContext.of(API, request, Probe(verdict))


def refused(listing: PaneObservation, phase: Phase = Phase.RESUME, planned: PlannedAction | None = None, ctx: TargetContext | None = None) -> object:
    """Return the target check's verdict: the reason and severity of a refusal, or the pane id."""
    verdict = target_refusal(phase, planned or action(), listing, ctx or context())
    return (verdict.reason, verdict.failed) if isinstance(verdict, Refusal) else verdict.pane_id


def test_an_unchanged_eligible_target_passes_with_its_fresh_record() -> None:
    """The fresh record is returned for the send."""
    assert refused(observation(record())) == CLAUDE_PANE


@pytest.mark.parametrize(
    ("listing", "expected"),
    [
        (observation(), ("target-absent", False)),
        (observation(record(), record()), ("pane-ambiguous", True)),
        (observation(record(session="other")), ("target-session-changed", True)),
        (observation(replace(record(), apps=("codex",))), ("host-contradictory", True)),
        (observation(replace(record(), harness="")), ("target-not-agent", False)),
        (observation(replace(record(), harness="", apps=("codex",))), ("target-host-changed", True)),
        (observation(replace(record(), cwd="relative")), ("target-identity-unavailable", False)),
        (observation(record(root=WEB)), ("target-checkout-changed", True)),
    ],
)
def test_a_target_that_changed_identity_is_refused(listing: PaneObservation, expected: tuple[str, bool]) -> None:
    """Design Q10 again, immediately before the send: absent and shell panes skip, other changes fail."""
    assert refused(listing) == expected


@pytest.mark.parametrize(
    ("request_", "expected"),
    [
        (replace(HUMAN, caller_pane=CLAUDE_PANE), ("caller-pane", False)),
        (replace(HUMAN, excepts=("LLM-SHARED_resume-paused",)), ("excluded", False)),
        (replace(HUMAN, excepts=("claude API",)), ("excluded", False)),
        (replace(HUMAN, excepts=("web",)), CLAUDE_PANE),
    ],
)
def test_protected_panes_are_refused(request_: PlanRequest, expected: object) -> None:
    """The caller's pane, an excluded session and an excluded pane label never receive input."""
    assert refused(observation(record()), ctx=context(request_)) == expected


@pytest.mark.parametrize(
    ("activity", "expected"),
    [
        (WORKING, ("pane-busy", False)),
        (PaneActivity("needs_input", "", draft_held=False, question="Allow?", ready=False), ("pane-blocked", False)),
        (replace(IDLE, draft_held=True), ("pane-draft", False)),
        (replace(IDLE, ready=None), ("pane-not-ready", False)),
        (replace(IDLE, state="starting"), ("pane-state-unknown", False)),
        (None, ("pane-state-unknown", False)),
    ],
)
def test_an_ineligible_target_is_refused_before_a_clear_resume_or_reviewer(activity: PaneActivity | None, expected: tuple[str, bool]) -> None:
    """Busy, blocked, draft, not-ready and unknown panes skip, as Step 5 decides."""
    listing = observation(record(), activity={} if activity is None else {CLAUDE_PANE: activity})
    for phase in (Phase.CLEAR, Phase.RESUME, Phase.REVIEWER):
        assert refused(listing, phase) == expected


def test_a_stale_working_codex_pane_needs_a_supported_idle_capture() -> None:
    """Only a supported idle, empty-input capture overrides a stale working status."""
    listing = observation(record(CODEX_PANE), activity={CODEX_PANE: WORKING})
    planned = action(CODEX_PANE)
    assert refused(listing, planned=planned) == ("pane-busy", False)
    assert refused(listing, planned=planned, ctx=context(verdict=ScreenVerdict.IDLE_EMPTY)) == CODEX_PANE


@pytest.mark.parametrize(
    ("activity", "expected"),
    [
        (WORKING, CODEX_PANE),
        (IDLE, CODEX_PANE),
        (PaneActivity("done", "", draft_held=False, question="", ready=True), CODEX_PANE),
        (PaneActivity("working", "permission", draft_held=False, question="", ready=False), ("pane-blocked", False)),
        (replace(WORKING, draft_held=True), ("pane-draft", False)),
        (replace(IDLE, ready=False), ("pane-not-ready", False)),
        (replace(IDLE, state="exited"), ("pane-state-unknown", False)),
        (None, ("pane-state-unknown", False)),
    ],
)
def test_the_recovery_enter_tolerates_only_the_panes_own_unsubmitted_command(activity: PaneActivity | None, expected: object) -> None:
    """A stale working status is no refusal there; a blocked, draft, not-ready or unknown pane is."""
    listing = observation(record(CODEX_PANE), activity={} if activity is None else {CODEX_PANE: activity})
    assert refused(listing, Phase.RECOVERY, action(CODEX_PANE)) == expected


def replanner(world: World, request: PlanRequest = HUMAN) -> Callable[[CanonicalRoot, PaneObservation], CheckoutPlan | None]:
    """Bind the real single-checkout planner to the declared planner world, with fresh launch ids."""
    ids = (f"{number:032x}" for number in count(100))
    ports = PlannerPorts(world.read, world.exchanges, world.history, world.probe, world.journal, lambda: next(ids))
    return lambda root, listing: plan_checkout(request, listing, ports, root)


def planned_step(world: World, phase: Phase = Phase.RESUME, index: int = 0) -> SendStep:
    """Plan the declared world once and return the send step of one of its actions."""
    (checkout,) = world.plan().checkouts
    listing = PaneObservation(tuple(world.panes), world.activity)
    planned = checkout.actions[index]
    (pane,) = (item for item in world.panes if item.pane_id == planned.pane_id)
    return SendStep(phase, checkout.root, planned, listing, pane)


@pytest.mark.parametrize("phase", [Phase.CLEAR, Phase.RESUME, Phase.RECOVERY])
def test_an_unchanged_checkout_replans_the_same_action(phase: Phase) -> None:
    """Only the launch id differs between the plan and its fresh replan."""
    world = World()
    step = planned_step(world, phase)
    assert PlanRecheck(replanner(world)).check(step) is None


def test_a_changed_prompt_digest_refuses_the_send() -> None:
    """The marker binding covers the prompt digest: a rewritten prompt is another assignment."""
    world = World()
    step = planned_step(world)
    original = snapshot()
    assert original.prompt is not None
    world.snapshots["c:\\work\\api"] = replace(original, prompt=replace(original.prompt, digest=PromptDigest.parse("c" * 64)))
    assert PlanRecheck(replanner(world)).check(step) == Refusal("plan-changed", failed=True)


@pytest.mark.parametrize("phase", [Phase.RESUME, Phase.RECOVERY])
def test_a_later_duplicate_resume_refuses_every_send(phase: Phase) -> None:
    """A resume typed elsewhere since planning skips, before the recovery Enter too."""
    world = World()
    step = planned_step(world, phase)
    world.history.by_pane[REVIEWER_PANE] = (ObservedCommand("/resume-session", LATER),)
    assert PlanRecheck(replanner(world)).check(step) == Refusal("already-resuming")


def test_an_uncertain_history_fails_the_send() -> None:
    """Uncertainty is never permission to deliver."""
    world = World()
    step = planned_step(world)
    world.history.by_pane[REVIEWER_PANE] = None
    assert PlanRecheck(replanner(world)).check(step) == Refusal("duplicate-uncertain", failed=True)


def test_a_removed_prompt_or_checkout_is_unplanned() -> None:
    """Without a saved prompt or a live pane, nothing is left to deliver."""
    world = World()
    step = planned_step(world)
    world.snapshots.clear()
    assert PlanRecheck(replanner(world)).check(step) == Refusal("checkout-unplanned")


def test_a_busy_target_refuses_a_resume_but_not_its_recovery_enter() -> None:
    """Before the Enter, the target's own activity is read as ready; nothing else is discounted."""
    world = World()
    resume, recovery = planned_step(world), planned_step(world, Phase.RECOVERY)
    world.activity[REQUESTOR_PANE] = WORKING
    busy = PaneObservation(tuple(world.panes), world.activity)
    check = PlanRecheck(replanner(world))
    assert check.check(replace(resume, observation=busy)) == Refusal("pane-busy")
    assert check.check(replace(recovery, observation=busy)) is None


def test_a_reviewer_continuation_matches_a_planned_reviewer() -> None:
    """A used prompt replans the reviewer as a later continuation of the same assignment."""
    world = World(snapshots={"c:\\work\\api": snapshot(receipt={"schema": 3})})
    step = planned_step(world, Phase.REVIEWER)
    assert step.action.kind is ActionKind.CONTINUE_REVIEWER
    check = PlanRecheck(replanner(world))
    assert check.check(replace(step, action=replace(step.action, kind=ActionKind.REVIEWER))) is None
    assert check.check(replace(step, action=replace(step.action, kind=ActionKind.RESUME))) == Refusal("plan-changed", failed=True)


def test_a_command_without_a_readable_marker_never_matches() -> None:
    """A malformed planned or replanned command is another action."""
    world = World()
    step = planned_step(world)
    unmarked = replace(step.action, command="/resume-session")
    replanned = CheckoutPlan(API, PromptState.UNUSED, CheckoutOutcome.PLANNED, actions=(unmarked,))
    assert PlanRecheck(lambda _root, _listing: replanned).check(step) == Refusal("plan-changed", failed=True)
    assert PlanRecheck(replanner(world)).check(replace(step, action=unmarked)) == Refusal("plan-changed", failed=True)
    assert PlanRecheck(replanner(world)).check(replace(step, action=replace(step.action, command=None))) == Refusal("plan-changed", failed=True)


def test_the_planned_requestor_is_the_declared_pane() -> None:
    """The planner world's requestor is the pane these checks replan."""
    assert planned_step(World()).pane.pane_id == REQUESTOR_PANE


@pytest.mark.parametrize("phase", [Phase.RESUME, Phase.RECOVERY])
def test_terminal_mode_preserves_a_working_pane(phase: Phase) -> None:
    """A working pane remains busy even if its editor capture looks idle."""
    class TerminalProbe(Probe):
        """Require a resting target for physical terminal input."""

        require_empty = True

    listing = observation(record(CODEX_PANE), activity={CODEX_PANE: WORKING})
    ctx = TargetContext.of(API, HUMAN, TerminalProbe(ScreenVerdict.IDLE_EMPTY))
    assert refused(listing, phase, action(CODEX_PANE), ctx) == ("pane-busy", False)


# eof
