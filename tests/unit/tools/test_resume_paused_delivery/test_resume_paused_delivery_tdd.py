"""Example tests of the guarded delivery of resume-paused: run, guard, checks, Claude and pairs.

Step 6 of v0.14.0 resume-paused: a dry run delivers nothing; each planned
checkout runs under its own nonblocking guard, released on every exit, and
independent checkouts run concurrently while a pane never has two operations.
Every send is preceded by fresh checks; an unpinned profile refuses all
input. A Claude resume is accepted only by its logged prompt and the full
input proof within the 100-second fake-clock budget, and never retyped; a
redundant clear is skipped, an unconfirmed one stops the resume, and the
requestor always precedes its conditional reviewer. Code review round 2:
each proof's prover is built for the remaining budget, and a log read that
spends it starts no proof. Step 7: every resume report goes through the
takeover's ``received`` with its checkout before the reviewer is decided.
Step 7 code review round 1: the worker hands the takeover its plan's
accepted prompt digest, and its own report of a Claude reviewer whose
requestor was refused or unconfirmed carries ``limits=claude-wait-scope``.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field, replace
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    API,
    CLAUDE_COMMAND,
    CLAUDE_PANE,
    CODEX_COMMAND,
    CODEX_PANE,
    CODEX_PROFILE,
    EMPTY,
    HUMAN,
    IDLE,
    PAUSED_AT,
    SESSION,
    T0,
    WEB,
    WEB_PANE,
    FakeTransport,
    World,
    action,
    checkout,
    observation,
    record,
)
from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_delivery import deliver_run
from tools.resume_paused_delivery_model import (
    CLAUDE_WAIT_SCOPE,
    ActionReport,
    ClearOutcome,
    DeliveryOutcome,
    LogKind,
    PairDelivery,
    Phase,
    ReceiverState,
    Refusal,
    UnpinnedProfiles,
)
from tools.resume_paused_guard import GuardState
from tools.resume_paused_models import PromptDigest
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    CheckoutPlan,
    GlobalFailure,
    GlobalReason,
    PlannedAction,
    RunPlan,
    SkipReason,
)
from tools.resume_paused_profiles import Host

if TYPE_CHECKING:
    from datetime import datetime

    from tools.resume_paused_delivery_model import CheckoutDelivery, LogEvent, SendStep
    from tools.resume_paused_evidence import PaneActivity, PaneObservation
    from tools.resume_paused_input import PaneRecord

SELECTOR = f"session:{SESSION} name:Claude*api"
WEB_COMMAND = f"/resume-session --resume-paused 03.rp1.{WEB_PANE}.requestor.b3"
CLAUDE_REVIEWER_COMMAND = f"/review-resume --resume-paused 04.rp1.{WEB_PANE}.reviewer.b4"
NOT_READY = replace(IDLE, ready=False)
DIGEST = PromptDigest.of(b"the saved prompt the plan read")


@dataclass
class RecordingCheck:
    """Pre-send check recording each phase and fresh record, refusing at one declared phase."""

    refuse_at: Phase | None = None
    failed: bool = False
    seen: list[tuple[Phase, str]] = field(default_factory=list[tuple[Phase, str]])

    def check(self, step: SendStep) -> Refusal | None:
        """Record the step and refuse at the declared phase."""
        self.seen.append((step.phase, step.pane.pane_id))
        return Refusal("declared-refusal", failed=self.failed) if step.phase is self.refuse_at else None


@dataclass
class RecordingTakeover:
    """Takeover recording what it was handed, delivering the reviewer when asked.

    Step 7: ``received`` records each resume report with the worker's checkout
    and returns it marked consumed, so a test sees the observed report reach
    the reviewer decision. Code review round 1: it also records the worker's
    accepted prompt digest.
    """

    deliver: bool = False
    checks: tuple[RecordingCheck, ...] = ()
    handed: list[tuple[ActionReport | None, PlannedAction]] = field(default_factory=list[tuple[ActionReport | None, PlannedAction]])
    received_reports: list[tuple[str, ActionReport]] = field(default_factory=list[tuple[str, ActionReport]])
    digests: list[PromptDigest | None] = field(default_factory=list[PromptDigest | None])

    def received(self, pair: PairDelivery, report: ActionReport) -> ActionReport:
        """Record the resume report with its checkout and the plan's digest, and return it observed as consumed."""
        self.received_reports.append((pair.root.key, report))
        self.digests.append(pair.digest)
        return replace(report, receiver=ReceiverState.CONSUMED)

    def reviewer(self, pair: PairDelivery, resumed: ActionReport | None, action: PlannedAction) -> ActionReport:
        """Record the hand-over, then deliver or report pending."""
        self.handed.append((resumed, action))
        if self.deliver:
            return pair.deliver(action, Phase.REVIEWER, self.checks)
        return ActionReport(action, DeliveryOutcome.PENDING, "declared")


def only(deliveries: tuple[CheckoutDelivery, ...]) -> ActionReport:
    """Return the single action report of a single delivered checkout."""
    (delivery,) = deliveries
    (report,) = delivery.reports
    return report


def asks(world: World) -> list[str]:
    """Return the typed texts, in order."""
    return [call[2] for call in world.transport.calls if call[0] == "ask"]


def test_a_dry_run_or_a_refused_run_delivers_nothing() -> None:
    """No guard, listing or input for a preview or a run-wide refusal."""
    world = World()
    refused = RunPlan(dry_run=False, failures=(GlobalFailure(GlobalReason.AGENT_CALLER),), checkouts=(checkout(action()),))
    assert world.deliver(checkout(action()), dry_run=True) == ()
    assert deliver_run(refused, HUMAN, world.ports()) == ()
    assert (world.transport.calls, world.guard.events) == ([], [])


def test_only_planned_checkouts_are_delivered() -> None:
    """A skipped or failed checkout plan is never delivered."""
    world = World()
    skipped = CheckoutPlan(API, PromptState.UNUSED, CheckoutOutcome.SKIPPED, SkipReason.PANE_BUSY)
    assert world.deliver(skipped) == ()
    assert world.guard.events == []


def test_an_accepted_claude_resume_is_one_selected_ask_proved_by_log_and_input() -> None:
    """The ask targets the live session and wildcarded name; acceptance is proved from the send instant."""
    world = World()
    world.transport.on_ask = world.accept_claude()
    (delivery,) = world.deliver(checkout(action()))
    assert delivery.reports == (ActionReport(action(), DeliveryOutcome.ACCEPTED),)
    assert (delivery.guard, delivery.failed) == (GuardState.ACQUIRED, False)
    assert world.transport.calls == [("observe",), ("capture", CLAUDE_PANE), ("ask", SELECTOR, CLAUDE_COMMAND)]
    assert world.claude.bounds == [T0]
    assert world.guard.events == ["acquire c:\\work\\api acquired", "release c:\\work\\api"]


def test_unproved_acceptance_is_unconfirmed_at_the_deadline_and_never_retyped() -> None:
    """Observation backs off to five seconds and stops at exactly 100 seconds; one ask only."""
    world = World()
    report = only(world.deliver(checkout(action())))
    assert (report.outcome, report.reason, report.failed) == (DeliveryOutcome.UNCONFIRMED, "acceptance-unproved", True)
    assert world.transport.sent() == [("ask", SELECTOR, CLAUDE_COMMAND)]
    assert world.clock.current == T0 + timedelta(seconds=100)
    assert (world.clock.sleeps[:5], max(world.clock.sleeps), world.clock.sleeps[-1]) == ([0.5, 1.0, 2.0, 4.0, 5.0], 5.0, 2.5)


@pytest.mark.parametrize(("logged", "proved"), [(True, False), (False, True)])
def test_a_logged_prompt_or_an_input_proof_alone_does_not_accept(*, logged: bool, proved: bool) -> None:
    """Claude acceptance needs the prompt event and the full latest-input proof together."""
    world = World()

    def effect(command: str) -> None:
        if logged:
            world.log.add(CLAUDE_PANE, LogKind.PROMPT, world.clock.now(), command)
        if proved:
            world.claude.proved.add((CLAUDE_PANE, command))

    world.transport.on_ask = effect
    assert only(world.deliver(checkout(action()))).outcome is DeliveryOutcome.UNCONFIRMED


def test_a_prompt_logged_before_the_send_does_not_prove_acceptance() -> None:
    """Only a prompt event at or after the send instant counts."""
    world = World()
    world.log.add(CLAUDE_PANE, LogKind.PROMPT, T0 - timedelta(seconds=1), CLAUDE_COMMAND)
    world.claude.proved.add((CLAUDE_PANE, CLAUDE_COMMAND))
    assert only(world.deliver(checkout(action()))).outcome is DeliveryOutcome.UNCONFIRMED


@dataclass
class SlowLog:
    """Agent log whose every read spends one second of the declared clock."""

    world: World

    def events(self, pane: PaneRecord) -> tuple[LogEvent, ...] | None:
        """Spend a second, then return the declared events."""
        self.world.clock.advance(1)
        return self.world.log.read(pane)


def test_a_log_read_that_spends_the_budget_starts_no_proof() -> None:
    """Code review round 2: once the prompt read ends past the deadline, no prover is built."""
    world = World()
    accept = world.accept_claude()

    def slow_ask(command: str) -> None:
        accept(command)
        world.clock.advance(99.5)

    world.transport.on_ask = slow_ask
    ports = replace(world.ports(), log=SlowLog(world))
    report = only(deliver_run(RunPlan(dry_run=False, failures=(), checkouts=(checkout(action()),)), HUMAN, ports))
    assert (report.outcome, report.reason) == (DeliveryOutcome.UNCONFIRMED, "acceptance-unproved")
    assert world.prover_bounds == []


def test_each_proof_is_granted_the_remaining_budget() -> None:
    """The prover of a proof started right after the ask reads the whole remaining budget."""
    world = World()
    world.transport.on_ask = world.accept_claude()
    assert only(world.deliver(checkout(action()))).outcome is DeliveryOutcome.ACCEPTED
    assert world.prover_bounds == [(Host.CLAUDE, 100.0)]


def test_the_unpinned_registry_refuses_every_real_pane_before_any_input() -> None:
    """Plan Q05: with no pinned profile, nothing is ever typed."""
    world = World()
    ports = replace(world.ports(), profiles=UnpinnedProfiles())
    report = only(deliver_run(RunPlan(dry_run=False, failures=(), checkouts=(checkout(action()),)), HUMAN, ports))
    assert (report.outcome, report.reason, report.failed) == (DeliveryOutcome.REFUSED, "host-profile-unsupported", True)
    assert world.transport.sent() == []


def test_a_profile_of_another_host_or_a_missing_input_proof_refuses_the_send() -> None:
    """The selected profile must be the planned host's, and its input proof must exist."""
    world = World()
    world.profiles.by_pane[CLAUDE_PANE] = [CODEX_PROFILE]
    assert only(world.deliver(checkout(action()))).reason == "host-profile-unsupported"
    world = World()
    ports = replace(world.ports(), provers={Host.CODEX: world.ports().provers[Host.CODEX]})
    assert only(deliver_run(RunPlan(dry_run=False, failures=(), checkouts=(checkout(action()),)), HUMAN, ports)).reason == "input-proof-unavailable"
    assert world.transport.sent() == []


@pytest.mark.parametrize(
    ("listing", "expected"),
    [
        (None, ("discovery-failed", True)),
        (observation(record(), activity={CLAUDE_PANE: replace(IDLE, state="working", ready=False)}), ("pane-busy", False)),
        (observation(), ("target-absent", False)),
        (observation(record(), record(WEB_PANE, WEB, name="Claude-api")), ("selector-ambiguous", True)),
    ],
)
def test_fresh_refusals_stop_the_send_without_input(listing: PaneObservation | None, expected: tuple[str, bool]) -> None:
    """Discovery, eligibility, identity and the selector are rechecked immediately before typing."""
    world = World(transport=FakeTransport([listing]))
    report = only(world.deliver(checkout(action())))
    assert (report.outcome, report.reason, report.failed) == (DeliveryOutcome.REFUSED, *expected)
    assert world.transport.sent() == []


@pytest.mark.parametrize("clear", [False, True])
def test_an_unreadable_agent_log_refuses_a_claude_send(*, clear: bool) -> None:
    """Without the log neither a clear nor acceptance could be proved, so nothing is typed."""
    world = World()
    world.log.events[CLAUDE_PANE] = None
    report = only(world.deliver(checkout(action(clear=clear))))
    assert (report.reason, report.failed, report.clear) == ("agent-log-unreadable", True, ClearOutcome.NONE)
    assert world.transport.sent() == []


def test_a_background_shell_and_a_failed_ask_exit_are_reported_only() -> None:
    """The indicator and the exit code are notes; nothing else is sent and acceptance still decides."""
    world = World()
    world.transport.captures[CLAUDE_PANE] = [("Claude Code", "2 shells running")]
    world.transport.exit_code = 1
    world.transport.on_ask = world.accept_claude()
    report = only(world.deliver(checkout(action())))
    assert (report.outcome, report.notes) == (DeliveryOutcome.ACCEPTED, ("background-shell", "resume-ask-exit-1"))
    assert world.transport.sent() == [("ask", SELECTOR, CLAUDE_COMMAND)]


def clearing(world: World) -> None:
    """Make the declared Claude pane log a clear for ``/clear`` and accept the resume command."""
    accept = world.accept_claude()

    def effect(command: str) -> None:
        if command == "/clear":
            world.log.add(CLAUDE_PANE, LogKind.CLEAR, world.clock.now())
        accept(command)

    world.transport.on_ask = effect


def test_a_redundant_claude_clear_is_skipped_and_the_resume_still_sent() -> None:
    """A clear logged after the pause with no later prompt makes another clear useless."""
    world = World()
    world.log.add(CLAUDE_PANE, LogKind.CLEAR, PAUSED_AT + timedelta(minutes=5))
    clearing(world)
    report = only(world.deliver(checkout(action(clear=True))))
    assert (report.outcome, report.clear) == (DeliveryOutcome.ACCEPTED, ClearOutcome.REDUNDANT)
    assert asks(world) == [CLAUDE_COMMAND]


@pytest.mark.parametrize(
    "earlier",
    [
        [(LogKind.CLEAR, PAUSED_AT + timedelta(minutes=5)), (LogKind.PROMPT, PAUSED_AT + timedelta(minutes=6))],
        [(LogKind.CLEAR, PAUSED_AT)],
        [],
    ],
)
def test_a_needed_claude_clear_is_sent_confirmed_then_the_resume_follows(earlier: list[tuple[LogKind, datetime]]) -> None:
    """A prompt after the last clear, a clear not after the pause, or none: clear, confirm, resume."""
    world = World()
    for kind, at in earlier:
        world.log.add(CLAUDE_PANE, kind, at)
    clearing(world)
    report = only(world.deliver(checkout(action(clear=True))))
    assert (report.outcome, report.clear) == (DeliveryOutcome.ACCEPTED, ClearOutcome.CONFIRMED)
    assert asks(world) == ["/clear", CLAUDE_COMMAND]


@pytest.mark.parametrize(("logs_clear", "ready"), [(False, IDLE), (True, NOT_READY)])
def test_an_unconfirmed_claude_clear_fails_and_no_resume_follows(*, logs_clear: bool, ready: PaneActivity) -> None:
    """The clear event and a ready pane are both required within the clear's own 100 seconds."""
    first = observation(record())
    world = World(transport=FakeTransport([first, observation(record(), activity={CLAUDE_PANE: ready})]))
    if logs_clear:
        clearing(world)
    report = only(world.deliver(checkout(action(clear=True))))
    assert (report.outcome, report.reason, report.failed, report.clear) == (DeliveryOutcome.UNCONFIRMED, "clear-unconfirmed", True, ClearOutcome.UNCONFIRMED)
    assert asks(world) == ["/clear"]
    assert world.clock.current == T0 + timedelta(seconds=100)


def test_checks_run_before_the_clear_and_again_before_the_resume() -> None:
    """A check refusing the resume after a confirmed clear stops it; the clear was rechecked first."""
    check = RecordingCheck(refuse_at=Phase.RESUME)
    world = World(checks=(check,))
    clearing(world)
    report = only(world.deliver(checkout(action(clear=True))))
    assert (report.outcome, report.reason, report.failed, report.clear) == (DeliveryOutcome.REFUSED, "declared-refusal", False, ClearOutcome.CONFIRMED)
    assert check.seen == [(Phase.CLEAR, CLAUDE_PANE), (Phase.RESUME, CLAUDE_PANE)]
    assert asks(world) == ["/clear"]


def test_a_check_failing_before_the_clear_sends_nothing() -> None:
    """The failing check's severity is the action's."""
    world = World(checks=(RecordingCheck(refuse_at=Phase.CLEAR, failed=True),))
    report = only(world.deliver(checkout(action(clear=True))))
    assert (report.outcome, report.failed, report.clear) == (DeliveryOutcome.REFUSED, True, ClearOutcome.NONE)
    assert world.transport.sent() == []


def paired(world: World) -> CheckoutPlan:
    """Declare the requestor and its Codex reviewer, both listed, and accept the requestor."""
    world.transport.observations = [observation(record(), record(CODEX_PANE))]
    world.transport.on_ask = world.accept_claude()
    return checkout(action(), action(CODEX_PANE, CODEX_COMMAND, kind=ActionKind.REVIEWER))


def test_a_conditional_reviewer_waits_on_the_takeover_after_an_accepted_resume() -> None:
    """Before Step 7, the reviewer of an accepted requestor stays pending; that is no failure."""
    world = World()
    (delivery,) = world.deliver(paired(world))
    assert [(report.outcome, report.reason) for report in delivery.reports] == [
        (DeliveryOutcome.ACCEPTED, ""), (DeliveryOutcome.PENDING, "takeover-unobserved"),
    ]
    assert (delivery.failed, asks(world)) == (False, [CLAUDE_COMMAND])


def test_a_reviewer_is_never_attempted_after_an_unconfirmed_resume() -> None:
    """The requestor precedes its reviewer; the takeover is not consulted."""
    takeover = RecordingTakeover()
    world = World(takeover=takeover)
    plan = paired(world)
    world.transport.on_ask = None
    (delivery,) = world.deliver(plan)
    assert [(report.outcome, report.reason) for report in delivery.reports] == [
        (DeliveryOutcome.UNCONFIRMED, "acceptance-unproved"), (DeliveryOutcome.REFUSED, "requestor-not-accepted"),
    ]
    assert (takeover.handed, [report.outcome for _, report in takeover.received_reports]) == ([], [DeliveryOutcome.UNCONFIRMED])
    assert delivery.reports[1].notes == ()


@pytest.mark.parametrize("unaccepted", [DeliveryOutcome.REFUSED, DeliveryOutcome.UNCONFIRMED])
def test_a_claude_reviewer_of_an_unaccepted_requestor_carries_the_wait_scope_limits(unaccepted: DeliveryOutcome) -> None:
    """The worker's own report of a Claude reviewer whose requestor was refused or unconfirmed discloses the limits."""
    refused = unaccepted is DeliveryOutcome.REFUSED
    takeover = RecordingTakeover()
    world = World(takeover=takeover, checks=(RecordingCheck(refuse_at=Phase.RESUME),) if refused else ())
    world.transport.observations = [observation(record(), record(WEB_PANE, name="Claude review"))]
    (delivery,) = world.deliver(checkout(action(), action(WEB_PANE, CLAUDE_REVIEWER_COMMAND, kind=ActionKind.REVIEWER)))
    requestor, reviewer = delivery.reports
    assert (requestor.outcome, reviewer.outcome, reviewer.reason, reviewer.notes) == (unaccepted, DeliveryOutcome.REFUSED, "requestor-not-accepted", (CLAUDE_WAIT_SCOPE,))
    assert (reviewer.action.host, takeover.handed) == (Host.CLAUDE, [])


def test_every_resume_report_is_observed_before_its_reviewer_is_decided() -> None:
    """Step 7's seam: the resume report goes through ``received`` with its checkout and plan digest, and the reviewer gets the observed one."""
    takeover = RecordingTakeover()
    world = World(takeover=takeover)
    (delivery,) = world.deliver(replace(paired(world), digest=DIGEST))
    ((root, report),) = takeover.received_reports
    ((resumed, _),) = takeover.handed
    assert (root, report.outcome, report.receiver, takeover.digests) == (API.key, DeliveryOutcome.ACCEPTED, ReceiverState.UNOBSERVED, [DIGEST])
    assert resumed is not None
    assert (resumed.receiver, delivery.reports[0].receiver) == (ReceiverState.CONSUMED, ReceiverState.CONSUMED)


def test_a_later_continuation_goes_to_the_takeover_without_a_resume() -> None:
    """A used prompt's reviewer continuation has no resume to wait for."""
    takeover = RecordingTakeover()
    continuation = action(CODEX_PANE, CODEX_COMMAND, kind=ActionKind.CONTINUE_REVIEWER)
    report = only(World(takeover=takeover).deliver(checkout(continuation)))
    assert (report.outcome, takeover.handed) == (DeliveryOutcome.PENDING, [(None, continuation)])


def test_planned_skips_are_reported_without_input() -> None:
    """A target the plan skipped keeps its reason; an action without a command is not planned."""
    world = World()
    world.transport.on_ask = world.accept_claude()
    skipped = action(CODEX_PANE, None, kind=ActionKind.REVIEWER, skip=SkipReason.TARGET_ABSENT)
    unplanned = action(CODEX_PANE, None, kind=ActionKind.REVIEWER)
    (delivery,) = world.deliver(checkout(action(), skipped, unplanned))
    assert [(report.outcome, report.reason) for report in delivery.reports[1:]] == [
        (DeliveryOutcome.REFUSED, "target-absent"), (DeliveryOutcome.REFUSED, "not-planned"),
    ]


def test_the_takeover_delivers_a_reviewer_under_the_held_guard_with_its_checks_and_no_clear() -> None:
    """Step 7's seam: the reviewer send runs its extra checks, never clears, and precedes the release."""
    check = RecordingCheck()
    takeover = RecordingTakeover(deliver=True, checks=(check,))
    world = World(takeover=takeover)
    plan = paired(world)
    plan = replace(plan, actions=(plan.actions[0], replace(plan.actions[1], clear=True)))
    world.transport.captures[CODEX_PANE] = [EMPTY]
    accept = world.accept_claude()

    def effect(command: str) -> None:
        accept(command)
        world.codex.proved.add((CODEX_PANE, command))
        world.guard.events.append(f"ask {command.split(maxsplit=1)[0]}")

    world.transport.on_ask = effect
    (delivery,) = world.deliver(plan)
    assert [report.outcome for report in delivery.reports] == [DeliveryOutcome.ACCEPTED, DeliveryOutcome.ACCEPTED]
    assert check.seen == [(Phase.REVIEWER, CODEX_PANE)]
    assert asks(world) == [CLAUDE_COMMAND, CODEX_COMMAND]
    assert world.guard.events[-3:] == ["ask /resume-session", "ask $llm-shared:review-resume", "release c:\\work\\api"]


def test_a_held_guard_skips_the_checkout_without_reading_any_pane() -> None:
    """Contention is an expected, immediate skip."""
    world = World()
    world.guard.states[API.key] = GuardState.HELD
    (delivery,) = world.deliver(checkout(action()))
    assert (delivery.guard, delivery.reports, delivery.failed) == (GuardState.HELD, (), False)
    assert world.transport.calls == []


def test_an_unavailable_guard_fails_the_checkout_without_input() -> None:
    """A guard that cannot be taken permits no input and fails."""
    world = World()
    world.guard.states[API.key] = GuardState.UNAVAILABLE
    (delivery,) = world.deliver(checkout(action()))
    assert (delivery.guard, delivery.failed, world.transport.calls) == (GuardState.UNAVAILABLE, True, [])


def test_the_guard_is_released_when_the_protected_sequence_raises() -> None:
    """An unexpected transport error propagates after the release."""
    world = World()

    def explode(command: str) -> None:
        del command
        message = "transport crashed"
        raise RuntimeError(message)

    world.transport.on_ask = explode
    with pytest.raises(RuntimeError, match="transport crashed"):
        world.deliver(checkout(action()))
    assert world.guard.events[-1] == "release c:\\work\\api"


def two_checkouts(world: World) -> tuple[CheckoutPlan, CheckoutPlan]:
    """Declare one Claude resume in each of two independent checkouts."""
    world.transport.observations = [observation(record(), record(WEB_PANE, WEB, name="Claude web"))]
    world.profiles.by_pane[WEB_PANE] = world.profiles.by_pane[CLAUDE_PANE]
    return checkout(action()), checkout(replace(action(WEB_PANE, WEB_COMMAND), label="Claude web"), root=WEB)


def test_independent_checkouts_are_delivered_concurrently() -> None:
    """Both workers reach their ask together; results keep the plan's checkout order."""
    world = World()
    barrier = threading.Barrier(2, timeout=5)
    accept_api, accept_web = world.accept_claude(), world.accept_claude(WEB_COMMAND, WEB_PANE)

    def effect(command: str) -> None:
        barrier.wait()
        accept_api(command)
        accept_web(command)

    world.transport.on_ask = effect
    deliveries = world.deliver(*two_checkouts(world))
    assert [(delivery.root, delivery.reports[0].outcome) for delivery in deliveries] == [
        (API, DeliveryOutcome.ACCEPTED), (WEB, DeliveryOutcome.ACCEPTED),
    ]


def test_one_pane_never_has_two_input_operations_at_once() -> None:
    """A second worker reaching a pane already in use refuses before reading anything."""
    world = World()
    api, web = two_checkouts(world)
    web = replace(web, actions=(action(),))
    in_ask, web_done = threading.Event(), threading.Event()
    accept = world.accept_claude()

    def effect(command: str) -> None:
        in_ask.set()
        assert web_done.wait(5)
        accept(command)

    def after_the_api_ask() -> None:
        assert in_ask.wait(5)

    world.transport.on_ask = effect
    world.guard.on_acquire[WEB.key] = after_the_api_ask
    world.guard.on_release[WEB.key] = web_done.set
    deliveries = world.deliver(api, web)
    assert deliveries[0].reports[0].outcome is DeliveryOutcome.ACCEPTED
    assert (deliveries[1].reports[0].reason, deliveries[1].failed) == ("pane-in-use", True)
    assert asks(world) == [CLAUDE_COMMAND]


# eof
