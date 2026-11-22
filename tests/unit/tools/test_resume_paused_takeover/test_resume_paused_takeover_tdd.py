"""Verified missing-reviewer activation tests of the resume-paused takeover.

Step 7 of v0.14.0 resume-paused: ``MarkedTakeover.reviewer`` decides from
fresh durable records and panes, on initial activation and later
continuation alike: an exact active reviewer is left alone; a requestor
receipt without its current marked claim, a competing pickup, an unknown wait,
an uncertain earlier delivery or a non-requestor receipt keep the reviewer
pending with no input; a replaced prompt or exchange invalidates the
continuation; a switched pair activates its switched reviewer. The decision is
refreshed under the guard immediately before the send, together with the
design Q27=B all-pane idle guard: a busy non-target Claude pane, a busy
requestor, a running local command behind a closed-looking transcript,
unreadable and unknown screens and a change between the check and the send
all stop the send. Every Claude reviewer outcome carries
``limits=claude-wait-scope``. Two runs go through the real Step 6 delivery.

Code review round 1: a question with no blocking reason on the target or on
another Claude pane keeps the reviewer pending with no send, on both routes;
the decision binds the prompt the plan accepted, so a prompt changed since
planning fails the continuation and an older receipt keeps it pending; the
real delivery hands the plan's digest to the takeover.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_delivery.delivery_world import (
    CLAUDE_PROFILE,
    EMPTY,
    World,
    checkout,
)
from tests.unit.tools.test_resume_paused_planner.planner_world import binding, live
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    ASKING,
    CLAIMED_GENERATION,
    OTHER_LAUNCH,
    REQUESTOR_PANE,
    REVIEWER_LAUNCH,
    REVIEWER_PANE,
    ROOT,
    THIRD_PANE,
    WORKING,
    Declared,
    FakeExchanges,
    FakePair,
    FakeSnapshots,
    TakeoverWorld,
    accepted,
    exchange,
    listing,
    marker,
    older,
    pane,
    planned,
    resumed,
    reviewing,
    taken,
    unused,
    used,
)
from tools.resume_paused_claude_ledger import Absence, LedgerDecision
from tools.resume_paused_delivery_model import (
    ActionReport,
    DeliveryOutcome,
    Phase,
    ReceiverState,
)
from tools.resume_paused_evidence import ObservedCommand, PaneObservation, ScreenVerdict
from tools.resume_paused_marker import LiveExchange, Marker
from tools.resume_paused_models import ArtifactError, SessionRole, timestamp_instant
from tools.resume_paused_pane_guard import ClaudeScreen
from tools.resume_paused_plan_model import ActionKind, PlannedAction
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import DISCLOSED_LIMITS, Host, ReadAccount, Reason
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_reviewer_wait import WaitScope
from tools.resume_paused_takeover import (
    CLAUDE_WAIT_LIMITS,
    CLAUDE_WAIT_SCOPE,
    NoResults,
    TakeoverPorts,
    preview_notes,
)
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_review import ExchangeSnapshot

type Route = Callable[[TakeoverWorld], tuple[ActionReport, FakePair]]

SINCE = timestamp_instant("2026-11-18T07:25:09+01:00")
SWITCHED = marker(SessionRole.REQUESTOR, pane=REVIEWER_PANE, launch=OTHER_LAUNCH)
UNPROVED = LedgerDecision(Absence.PENDING, (Reason("background-start-unmatched"),), ReadAccount())
REVIEWER_MARKED = marked_command(Host.CODEX, ActionKind.REVIEWER, marker(SessionRole.REVIEWER))
SECOND_ROUND = 2


def claiming(world: TakeoverWorld, phases: tuple[Phase, ...] = ()) -> FakePair:
    """Return the worker whose delivery makes the activated reviewer's marked claim current."""

    def claim() -> None:
        world.exchanges.declared.items = [reviewing(world.reviewer_host)]

    return FakePair(world, phases=phases, on_deliver=claim)


def initial(world: TakeoverWorld, pair: FakePair | None = None, action: PlannedAction | None = None) -> tuple[ActionReport, FakePair]:
    """Decide the reviewer right after the accepted resume."""
    pair = pair or claiming(world)
    action = action or planned(ActionKind.REVIEWER, world.reviewer_host)
    return world.takeover().reviewer(pair, resumed(world.reviewer_host), action), pair


def continued(world: TakeoverWorld, pair: FakePair | None = None, action: PlannedAction | None = None) -> tuple[ActionReport, FakePair]:
    """Decide the reviewer in a later continuation, from durable records alone."""
    pair = pair or claiming(world)
    action = action or planned(ActionKind.CONTINUE_REVIEWER, world.reviewer_host)
    return world.takeover().reviewer(pair, None, action), pair


ROUTES: list[Route] = [initial, continued]


def verdict(report: ActionReport) -> tuple[DeliveryOutcome, str, bool]:
    """Return a report's outcome, reason and failure flag."""
    return report.outcome, report.reason, report.failed


def receipts(*states: CheckoutSnapshot) -> FakeSnapshots:
    """Declare the saved pause across reads."""
    return FakeSnapshots(Declared(list(states)))


def exchanges(*observed: ExchangeSnapshot) -> FakeExchanges:
    """Declare the exchange across reads."""
    return FakeExchanges(Declared(list(observed)))


@pytest.mark.parametrize("route", ROUTES)
def test_a_codex_reviewer_is_activated_after_proved_takeover_and_an_idle_capture(route: Route) -> None:
    """Initial activation and an unchanged later continuation deliver once, then observe the reviewer's claim."""
    report, pair = route(TakeoverWorld())
    assert (report.outcome, report.receiver, report.generation, report.failed) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, CLAIMED_GENERATION, False)
    assert ([phase for _, phase in pair.delivered], pair.checked, CLAUDE_WAIT_SCOPE in report.notes) == ([Phase.REVIEWER], [Phase.REVIEWER] * 2, False)


@pytest.mark.parametrize("route", ROUTES)
def test_a_claude_reviewer_binds_the_requestor_scope_and_carries_the_limits(route: Route) -> None:
    """The ledger scope binds the proved requestor's pane and rebuilt marked input, at decision and before the send."""
    world = TakeoverWorld.claude_reviewer()
    report, pair = route(world)
    requestor_input = marked_command(Host.CLAUDE, ActionKind.RESUME, marker(reviewer_host=Host.CLAUDE))
    scope = WaitScope(ROOT, pane(REVIEWER_PANE, Host.CLAUDE), SINCE, pane(REQUESTOR_PANE, Host.CLAUDE), requestor_input)
    assert (report.outcome, report.receiver, report.notes[-1]) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, CLAUDE_WAIT_SCOPE)
    assert (world.absence.scopes, len(pair.delivered)) == ([scope, scope], 1)
    assert sorted(set(world.screens.read_panes)) == sorted([REQUESTOR_PANE, REVIEWER_PANE])


def test_every_claude_reviewer_outcome_carries_the_limits() -> None:
    """Pending and skipped Claude reviewers disclose the wait-scope limits too; Codex reviewers do not."""
    pending = TakeoverWorld.claude_reviewer()
    pending.exchanges = exchanges(exchange(None))
    left = TakeoverWorld.claude_reviewer()
    left.exchanges = exchanges(reviewing(Host.CLAUDE))
    codex = TakeoverWorld(exchanges=exchanges(exchange(None)))
    notes = [initial(world)[0].notes for world in (pending, left, codex)]
    assert notes == [(CLAUDE_WAIT_SCOPE,), (CLAUDE_WAIT_SCOPE,), ()]


@pytest.mark.parametrize("route", ROUTES)
def test_an_exact_active_reviewer_is_left_alone(route: Route) -> None:
    """The reviewer owning the current generation, with an agreeing pane, receives no input and nothing fails."""
    world = TakeoverWorld(exchanges=exchanges(reviewing()))
    report, pair = route(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.REFUSED, "reviewer-active", False), [])


def test_an_unmarked_reviewer_claim_is_left_alone_when_the_pane_agrees() -> None:
    """Without a marked claim, the reviewer pane's latest typed reviewer entry agrees with the protocol owner."""
    world = TakeoverWorld(exchanges=exchanges(exchange(None, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION)))
    world.history.by_pane = {REVIEWER_PANE: (ObservedCommand("$llm-shared:review-resume as reviewer", SINCE),)}
    assert verdict(initial(world)[0]) == (DeliveryOutcome.REFUSED, "reviewer-active", False)


@pytest.mark.parametrize(
    ("state", "observed", "reason"),
    [
        (unused(), taken(), "receipt-absent"),
        (used(), exchange(None), "claim-absent"),
        (used(), exchange(marker(launch=OTHER_LAUNCH)), "claim-other-launch"),
        (used(), exchange(None, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION), "claim-absent"),
        (used(), exchange(marker(), owner=Actor.REVIEWER), "claim-superseded"),
        (used(), exchange(kind=ExchangeObservationKind.BUSY), "exchange-busy"),
        (used(), exchange(kind=ExchangeObservationKind.NOT_LIVE), "exchange-not-live"),
    ],
)
def test_an_unproved_takeover_keeps_the_reviewer_pending(state: CheckoutSnapshot, observed: ExchangeSnapshot, reason: str) -> None:
    """A requestor receipt without its current bound claim, or a competing pickup, never triggers the counterpart."""
    world = TakeoverWorld(snapshots=receipts(state), exchanges=exchanges(observed))
    report, pair = initial(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, reason, False), [])


def test_only_a_resumed_requestor_activates_a_pair() -> None:
    """A resumed reviewer or a failed requestor never activates its counterpart."""
    world = TakeoverWorld()
    reviewer_resume = replace_action(resumed(), role=SessionRole.REVIEWER)
    takeover, pair = world.takeover(), claiming(world)
    action = planned(ActionKind.REVIEWER, Host.CODEX)
    refused = takeover.reviewer(pair, reviewer_resume, action)
    failed = takeover.reviewer(pair, ActionReport(resumed().action, DeliveryOutcome.ACCEPTED, "receiver-question", failed=True), action)
    assert ([verdict(refused), verdict(failed)], pair.delivered) == (
        [(DeliveryOutcome.REFUSED, "resumed-not-requestor", False), (DeliveryOutcome.REFUSED, "requestor-failed", False)], [],
    )


def replace_action(report: ActionReport, role: SessionRole) -> ActionReport:
    """Return the report of the same command delivered in another role."""
    action = report.action
    moved = PlannedAction(action.kind, role, action.host, action.session, action.pane_id, action.label, action.command)
    return ActionReport(moved, report.outcome)


def test_a_paused_reviewer_receipt_never_continues_a_pair() -> None:
    """A continuation whose receipt is a reviewer's own stays pending: it proves no requestor."""
    reviewer = Marker(OTHER_LAUNCH, REVIEWER_PANE, SessionRole.REVIEWER, marker(SessionRole.REVIEWER).binding)
    world = TakeoverWorld(
        snapshots=receipts(used(requestor=reviewer, changes={"Resumed by": "chatgpt"})),
        exchanges=exchanges(exchange(reviewer, host=Host.CODEX, requestor_nature="codex")),
    )
    report, pair = continued(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "receipt-not-requestor", False), [])


@pytest.mark.parametrize(
    ("probe", "reason", "notes"),
    [(ScreenVerdict.WORKING, "codex-wait-unproved", ("screen-working",)), (ScreenVerdict.UNSUPPORTED, "codex-wait-unproved", ("screen-unsupported",))],
)
def test_an_unproved_codex_wait_keeps_the_reviewer_pending(probe: ScreenVerdict, reason: str, notes: tuple[str, ...]) -> None:
    """A Codex reviewer whose capture does not prove an idle, empty, turn-free pane receives no input."""
    world = TakeoverWorld()
    world.probe.verdicts = {REVIEWER_PANE: probe}
    report, pair = continued(world)
    assert (verdict(report), report.notes, pair.delivered) == ((DeliveryOutcome.PENDING, reason, False), notes, [])


@pytest.mark.parametrize(
    ("decision", "reason", "notes"),
    [(UNPROVED, "claude-wait-unproved", ("ledger-background-start-unmatched", CLAUDE_WAIT_SCOPE)), (None, "claude-ledger-unavailable", (CLAUDE_WAIT_SCOPE,))],
)
@pytest.mark.parametrize("route", ROUTES)
def test_an_unknown_claude_wait_keeps_the_reviewer_pending(route: Route, decision: LedgerDecision | None, reason: str, notes: tuple[str, ...]) -> None:
    """A watcher started after the latest input, restarted after an answer, or no pinned ledger: pending, no input."""
    world = TakeoverWorld.claude_reviewer()
    world.absence.decision = decision
    report, pair = route(world)
    assert (verdict(report), report.notes, pair.delivered) == ((DeliveryOutcome.PENDING, reason, False), notes, [])


def test_an_uncertain_earlier_reviewer_delivery_is_never_resent() -> None:
    """A marked reviewer entry already typed since the receipt is diagnosed and nothing is typed again."""
    world = TakeoverWorld()
    world.history.by_pane = {REVIEWER_PANE: (ObservedCommand(REVIEWER_MARKED, SINCE + timedelta(seconds=5)),)}
    report, pair = continued(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "reviewer-delivery-uncertain", False), [])


@pytest.mark.parametrize(
    ("state", "observed", "reason"),
    [
        (used(Host.CLAUDE), taken(), "prompt-replaced"),
        (used(), exchange(kind=ExchangeObservationKind.SELECTION_CHANGED), "exchange-selection-changed"),
        (used(), exchange(kind=ExchangeObservationKind.DAMAGED), "exchange-damaged"),
    ],
)
def test_prompt_or_exchange_replacement_invalidates_the_continuation(state: CheckoutSnapshot, observed: ExchangeSnapshot, reason: str) -> None:
    """A prompt changed since the plan read it, or a changed exchange identity, fails the continuation instead of redirecting it."""
    world = TakeoverWorld(snapshots=receipts(state), exchanges=exchanges(observed))
    report, pair = continued(world, FakePair(world, digest=accepted(used())))
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.REFUSED, reason, True), [])


@pytest.mark.parametrize("route", ROUTES)
def test_an_older_receipt_of_the_accepted_prompt_keeps_the_reviewer_pending(route: Route) -> None:
    """The requestor has not yet written its own receipt behind an older one: pending, never a replaced prompt."""
    world = TakeoverWorld(snapshots=receipts(older()))
    report, pair = route(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "receipt-earlier", False), [])


@pytest.mark.parametrize(
    ("reviewer_host", "pane_id", "reason"),
    [(Host.CLAUDE, REVIEWER_PANE, "reviewer-question"), (Host.CLAUDE, THIRD_PANE, "claude-pane-question"), (Host.CODEX, REVIEWER_PANE, "reviewer-question")],
)
@pytest.mark.parametrize("route", ROUTES)
def test_a_question_with_no_blocking_reason_keeps_the_reviewer_pending(route: Route, reviewer_host: Host, pane_id: str, reason: str) -> None:
    """A question on the target, or on another Claude pane of the checkout, stops the activation with zero sends."""
    world = TakeoverWorld.claude_reviewer() if reviewer_host is Host.CLAUDE else TakeoverWorld()
    world.transport.observations = [listing(reviewer_host, live(THIRD_PANE, Host.CLAUDE), activity={pane_id: ASKING})]
    report, pair = route(world)
    notes = (CLAUDE_WAIT_SCOPE,) if reviewer_host is Host.CLAUDE else ()
    assert (verdict(report), report.notes, pair.delivered) == ((DeliveryOutcome.PENDING, reason, False), notes, [])


def test_a_switched_continuation_activates_the_switched_reviewer() -> None:
    """The saved reviewer resumed as requestor: its continuation activates the saved requestor pane as reviewer."""
    switched_reviewer = marker(SessionRole.REVIEWER, pane=REQUESTOR_PANE)
    world = TakeoverWorld(
        snapshots=receipts(used(requestor=SWITCHED, changes={"Resumed by": "chatgpt"})),
        exchanges=exchanges(exchange(SWITCHED, host=Host.CODEX, requestor_nature="codex", reviewer_nature="claude")),
    )
    world.transport.captures = {REQUESTOR_PANE: [("Claude Code",)]}
    action = planned(ActionKind.CONTINUE_REVIEWER, Host.CLAUDE, pane_id=REQUESTOR_PANE, command=marked_command(Host.CLAUDE, ActionKind.CONTINUE_REVIEWER, switched_reviewer))

    def claim() -> None:
        world.exchanges.declared.items = [exchange(switched_reviewer, host=Host.CLAUDE, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION)]

    report, pair = continued(world, FakePair(world, on_deliver=claim), action)
    assert (report.outcome, report.receiver, len(pair.delivered)) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, 1)
    assert world.absence.scopes[0].requestor is None


def test_a_reviewer_that_is_not_the_proved_counterpart_fails() -> None:
    """The planned reviewer must be the pair's other pane, never another listed agent."""
    world = TakeoverWorld()
    world.transport.observations = [listing(Host.CODEX, live(THIRD_PANE, Host.CODEX))]
    report, pair = initial(world, action=planned(ActionKind.REVIEWER, Host.CODEX, pane_id=THIRD_PANE, command=REVIEWER_MARKED))
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.REFUSED, "reviewer-not-paired", True), [])


@pytest.mark.parametrize(
    ("listed", "reviewer_host", "reason", "failed"),
    [
        (None, Host.CODEX, "discovery-failed", True),
        (listing().panes[:1], Host.CODEX, "target-absent", False),
        (listing(Host.CLAUDE).panes[1:], Host.CLAUDE, "requestor-pane-absent", False),
    ],
)
def test_missing_panes_stop_the_decision(listed: tuple[PaneRecord, ...] | None, reviewer_host: Host, reason: str, failed: bool) -> None:  # noqa: FBT001
    """A failed discovery fails; a missing reviewer, or a missing Claude requestor for a Claude reviewer, is pending."""
    world = TakeoverWorld.claude_reviewer() if reviewer_host is Host.CLAUDE else TakeoverWorld()
    world.transport.observations = [None if listed is None else PaneObservation(listed, listing(reviewer_host).activity)]
    report, pair = initial(world)
    assert (report.reason, report.failed, report.outcome is DeliveryOutcome.ACCEPTED, pair.delivered) == (reason, failed, False, [])


def test_a_reviewer_that_turns_busy_before_the_send_is_not_sent() -> None:
    """The decision is refreshed on the send's fresh listing: a change since the decision stops the send."""
    world = TakeoverWorld()
    world.transport.observations = [listing(), listing(activity={REVIEWER_PANE: WORKING})]
    report, pair = initial(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "reviewer-busy", False), [])


def guarded(change: str) -> TakeoverWorld:
    """Return a Claude-reviewer world with one more Claude pane and one declared Q27=B change at the send."""
    world = TakeoverWorld.claude_reviewer()
    idle = listing(Host.CLAUDE, live(THIRD_PANE, Host.CLAUDE))
    at_send = idle
    if change == "busy-non-target":
        at_send = listing(Host.CLAUDE, live(THIRD_PANE, Host.CLAUDE), activity={THIRD_PANE: WORKING})
    elif change == "busy-requestor":
        at_send = listing(Host.CLAUDE, live(THIRD_PANE, Host.CLAUDE), activity={REQUESTOR_PANE: WORKING})
    elif change == "local-command":
        world.screens.readings = {THIRD_PANE: ClaudeScreen.BUSY}
    elif change == "unreadable":
        world.transport.captures[THIRD_PANE] = [None]
    elif change == "unknown-layout":
        world.screens.readings = {REVIEWER_PANE: ClaudeScreen.UNKNOWN}
    world.transport.observations = [idle, at_send]
    return world


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ("busy-non-target", "claude-pane-busy"),
        ("busy-requestor", "claude-pane-busy"),
        ("local-command", "claude-pane-busy"),
        ("unreadable", "claude-pane-unreadable"),
        ("unknown-layout", "claude-pane-unknown-layout"),
    ],
)
@pytest.mark.parametrize("route", ROUTES)
def test_the_all_pane_idle_guard_stops_a_claude_reviewer_send(route: Route, change: str, reason: str) -> None:
    """A busy non-target or requestor pane, a running local command, an unreadable or unknown screen: pending, no input."""
    world = guarded(change)
    report, pair = route(world)
    assert (verdict(report), report.notes, pair.delivered) == ((DeliveryOutcome.PENDING, reason, False), (CLAUDE_WAIT_SCOPE,), [])


@pytest.mark.parametrize("route", ROUTES)
def test_an_all_idle_checkout_lets_the_claude_reviewer_send(route: Route) -> None:
    """The all-idle control: every Claude pane of the checkout reads idle, so the reviewer is activated."""
    world = guarded("none")
    report, pair = route(world)
    assert (report.outcome, len(pair.delivered), sorted(set(world.screens.read_panes))) == (
        DeliveryOutcome.ACCEPTED, 1, sorted([REQUESTOR_PANE, REVIEWER_PANE, THIRD_PANE]),
    )


def test_a_codex_recovery_refreshes_only_the_durable_takeover() -> None:
    """Before the recovery Enter the pane holds the command; the takeover is refreshed without judging its wait."""
    world = TakeoverWorld()
    world.transport.observations = [listing(), listing(), listing(activity={REVIEWER_PANE: WORKING})]
    report, pair = initial(world, claiming(world, (Phase.REVIEWER, Phase.RECOVERY)))
    assert (report.outcome, pair.checked) == (DeliveryOutcome.ACCEPTED, [Phase.REVIEWER, Phase.REVIEWER, Phase.RECOVERY, Phase.RECOVERY])


def test_a_takeover_superseded_before_the_recovery_enter_stops_it() -> None:
    """A competing pickup between the send and the recovery Enter withholds the Enter."""
    world = TakeoverWorld(exchanges=exchanges(taken(), taken(), exchange(marker(), owner=Actor.REVIEWER)))
    report, pair = initial(world, claiming(world, (Phase.REVIEWER, Phase.RECOVERY)))
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "claim-superseded", False), [])


def test_an_independent_delivery_failure_is_reported_unchanged() -> None:
    """An unproved acceptance is the delivery's own failure: never retyped, never turned into pending."""
    world = TakeoverWorld()
    report, pair = initial(world, FakePair(world, outcome=DeliveryOutcome.UNCONFIRMED, failed=True))
    assert (verdict(report), len(pair.delivered)) == ((DeliveryOutcome.UNCONFIRMED, "acceptance-unproved", True), 1)


def test_a_reviewer_claim_not_seen_within_its_bound_is_completion_unconfirmed() -> None:
    """Reviewer acceptance does not prove completion: a busy exchange or another launch's claim settles nothing."""
    world = TakeoverWorld()
    other = exchange(marker(SessionRole.REVIEWER, launch=OTHER_LAUNCH), host=Host.CODEX, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION)

    def later() -> None:
        world.exchanges.declared.items = [exchange(kind=ExchangeObservationKind.BUSY), other, reviewing()]

    report, _ = initial(world, FakePair(world, on_deliver=later))
    assert (report.receiver, report.generation, world.clock.sleeps) == (ReceiverState.CLAIMED, CLAIMED_GENERATION, [0.5, 1.0])
    world = TakeoverWorld()
    report, _ = initial(world, FakePair(world))
    assert (report.outcome, report.receiver, report.failed) == (DeliveryOutcome.ACCEPTED, ReceiverState.COMPLETION_UNCONFIRMED, False)


def test_a_failed_reviewer_result_fails_the_activation() -> None:
    """The activated reviewer reporting failure for its launch fails the action."""
    world = TakeoverWorld()

    def fail() -> None:
        world.results.lines = {REVIEWER_PANE: (f"resume-paused {REVIEWER_LAUNCH} failed",)}

    report, _ = initial(world, FakePair(world, on_deliver=fail))
    assert (report.receiver, report.reason, report.failed) == (ReceiverState.FAILED, "receiver-failed", True)


@pytest.mark.parametrize(
    "code",
    [
        "turn-open",
        "background-start-unmatched",
        "parent-missing",
        "continuation-predecessor-missing",
        "read-failed",
        "marked-input-unproved",
        "process-binding-changed",
    ],
)
@pytest.mark.parametrize("route", ROUTES)
def test_recorded_blockers_keep_a_claude_reviewer_pending(route: Route, code: str) -> None:
    """Open recorded turns, unmatched starts, partial records, missing history, incomplete reads or a changed Q23 binding block."""
    world = TakeoverWorld.claude_reviewer()
    world.absence.decision = LedgerDecision(Absence.PENDING, (Reason(code),), ReadAccount())
    report, pair = route(world)
    assert (verdict(report), report.notes, pair.delivered) == (
        (DeliveryOutcome.PENDING, "claude-wait-unproved", False), (f"ledger-{code}", CLAUDE_WAIT_SCOPE), [],
    )


def test_a_continuation_survives_log_eviction_and_a_daemon_restart() -> None:
    """With every result line evicted or unreadable, the unchanged durable records still decide the continuation."""
    world = TakeoverWorld()
    world.results.lines = {REQUESTOR_PANE: None, REVIEWER_PANE: None}
    report, pair = continued(world)
    assert (report.outcome, report.receiver, len(pair.delivered)) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, 1)


def test_unreadable_evidence_fails_the_decision() -> None:
    """A saved pause that does not parse fails the reviewer decision with no input."""
    world = TakeoverWorld(snapshots=FakeSnapshots(Declared([ArtifactError("receipt-malformed")])))
    report, pair = continued(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.REFUSED, "evidence-invalid", True), [])


def test_no_pinned_profile_reads_no_result_line() -> None:
    """The default result source reads nothing, so only durable records can prove anything."""
    world = TakeoverWorld()
    composed = world.ports()
    ports = TakeoverPorts(world.clock, world.clock, world.transport, world.snapshots.read, world.exchanges, composed.wait, composed.guard)
    assert isinstance(ports.results, NoResults)
    assert NoResults().results(pane(REQUESTOR_PANE, Host.CLAUDE), 1.0) is None


def rebound(round_number: int) -> Marker:
    """Return the planned reviewer marker rebound to the first occurrence at the given round."""
    return Marker(REVIEWER_LAUNCH, REVIEWER_PANE, SessionRole.REVIEWER, binding(unused(), REVIEWER_PANE, SessionRole.REVIEWER, LiveExchange(1, round_number)))


def test_a_reviewer_marker_is_rebound_to_the_live_round() -> None:
    """A requestor that published a new round since planning gets a reviewer marker for that round, same launch id."""
    later = replace(taken(), round_number=SECOND_ROUND)
    world = TakeoverWorld(exchanges=exchanges(later))

    def claim() -> None:
        world.exchanges.declared.items = [exchange(rebound(SECOND_ROUND), host=Host.CODEX, owner=Actor.REVIEWER, generation=CLAIMED_GENERATION)]

    report, pair = initial(world, FakePair(world, on_deliver=claim))
    ((delivered, _),) = pair.delivered
    assert delivered.command == marked_command(Host.CODEX, ActionKind.REVIEWER, rebound(SECOND_ROUND))
    assert delivered.command != planned(ActionKind.REVIEWER, Host.CODEX).command
    assert (report.outcome, report.receiver) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED)


def test_a_round_that_moves_before_the_send_stops_it() -> None:
    """The binding refreshed under the guard must still be the delivered one; otherwise the reviewer stays pending."""
    world = TakeoverWorld(exchanges=exchanges(taken(), replace(taken(), round_number=SECOND_ROUND)))
    report, pair = initial(world)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.PENDING, "reviewer-binding-changed", False), [])


def test_an_unreadable_planned_reviewer_marker_fails() -> None:
    """A planned reviewer command whose marker does not parse cannot be rebound and is never sent."""
    world = TakeoverWorld()
    broken = planned(ActionKind.REVIEWER, Host.CODEX, command="$llm-shared:review-resume --resume-paused broken")
    report, pair = initial(world, action=broken)
    assert (verdict(report), pair.delivered) == ((DeliveryOutcome.REFUSED, "reviewer-marker-unreadable", True), [])


def test_previews_disclose_the_limits_of_a_conditional_claude_reviewer_only() -> None:
    """A conditional Claude reviewer preview carries the code; a Codex reviewer, a resume or a skip does not."""
    skipped = PlannedAction(ActionKind.REVIEWER, SessionRole.REVIEWER, Host.CLAUDE, "s", REVIEWER_PANE, "r", None, conditional=True)
    actions = [planned(ActionKind.REVIEWER, Host.CLAUDE), planned(ActionKind.REVIEWER, Host.CODEX), resumed().action, skipped]
    assert [preview_notes(action) for action in actions] == [(CLAUDE_WAIT_SCOPE,), (), (), ()]


def test_the_five_disclosed_limits_are_defined() -> None:
    """Help and reference define the three Q20=A limits, Q26=A's fourth and Q27=B's fifth, with Q21's boot scope."""
    assert tuple(CLAUDE_WAIT_LIMITS) == DISCLOSED_LIMITS
    meanings = list(CLAUDE_WAIT_LIMITS.values())
    assert ["Q20=A" in meanings[0], "Q20=A" in meanings[1], "since the last OS boot" in meanings[2]] == [True] * 3
    assert ["TaskStop" in meanings[3], "no TUIOS pane" in meanings[4]] == [True] * 2


def delivered_pair(reviewer_host: Host) -> tuple[World, TakeoverWorld]:
    """Return a real Step 6 delivery whose takeover is the declared one, with typed commands changing the records."""
    takeover_world = TakeoverWorld.claude_reviewer() if reviewer_host is Host.CLAUDE else TakeoverWorld()
    takeover_world.snapshots = receipts(unused(reviewer_host))
    takeover_world.exchanges = exchanges(exchange(None))
    delivery = World(transport=takeover_world.transport, clock=takeover_world.clock, takeover=takeover_world.takeover())
    resume = resumed(reviewer_host).action
    reviewer = planned(ActionKind.REVIEWER, reviewer_host)
    accept = delivery.accept_claude(str(resume.command), REQUESTOR_PANE)

    def typed(command: str) -> None:
        accept(command)
        if command == resume.command:
            takeover_world.snapshots.declared.items = [used(reviewer_host)]
            takeover_world.exchanges.declared.items = [taken(reviewer_host)]
        elif command == reviewer.command:
            delivery.codex.proved.add((REVIEWER_PANE, command))
            takeover_world.exchanges.declared.items = [reviewing(reviewer_host)]

    delivery.transport.on_ask = typed
    delivery.transport.captures.setdefault(REVIEWER_PANE, [EMPTY])
    delivery.profiles.by_pane[REVIEWER_PANE] = [CLAUDE_PROFILE] if reviewer_host is Host.CLAUDE else delivery.profiles.by_pane[REVIEWER_PANE]
    return delivery, takeover_world


def test_a_pair_resumes_then_activates_its_codex_reviewer_through_the_delivery() -> None:
    """End to end on the real Step 6 delivery: resume accepted and claimed, then the Codex reviewer activated and claimed.

    The plan carries the digest of the prompt it read, which the worker hands to the takeover.
    """
    delivery, _ = delivered_pair(Host.CODEX)
    plan = replace(checkout(resumed().action, planned(ActionKind.REVIEWER, Host.CODEX)), digest=accepted(unused()))
    (result,) = delivery.deliver(plan)
    requestor, reviewer = result.reports
    assert [(report.outcome, report.receiver, report.generation) for report in result.reports] == [
        (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, 5), (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, CLAIMED_GENERATION),
    ]
    assert [call[2] for call in delivery.transport.sent()] == [requestor.action.command, reviewer.action.command]


def test_the_real_delivery_runs_the_all_pane_idle_guard_before_a_claude_reviewer_send() -> None:
    """End to end: a busy non-target Claude pane stops the reviewer send under the guard; only the resume is typed."""
    delivery, takeover_world = delivered_pair(Host.CLAUDE)
    busy = listing(Host.CLAUDE, live(THIRD_PANE, Host.CLAUDE), activity={THIRD_PANE: WORKING})
    takeover_world.transport.observations = [busy]
    (result,) = delivery.deliver(checkout(resumed(Host.CLAUDE).action, planned(ActionKind.REVIEWER, Host.CLAUDE)))
    requestor, reviewer = result.reports
    assert (requestor.receiver, verdict(reviewer), reviewer.notes[-1]) == (ReceiverState.CLAIMED, (DeliveryOutcome.PENDING, "claude-pane-busy", False), CLAUDE_WAIT_SCOPE)
    assert [call[2] for call in delivery.transport.sent()] == [requestor.action.command]
