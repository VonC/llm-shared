"""Post-acceptance receiver observation tests of the resume-paused takeover.

Step 7 of v0.15.0 resume-paused: ``MarkedTakeover.received`` observes each
accepted receiver for its own 120-second bound on a fake clock, with backoff
from half a second capped at five seconds that never extends the bound, and
re-reads every piece of evidence at every look. A requestor settles on its
proved takeover, any other receiver on its receipt; a receipt alone at the
bound stays consumed and nothing durable is completion-unconfirmed, both
successes. A failed result for this launch, a question on the pane, another
launch's receipt, a replaced prompt and damaged evidence fail; masked or
foreign result lines prove nothing, and a look completed after the bound is
never acted on.

Code review round 1: observation binds the prompt the plan accepted. A fresh
prompt behind an older receipt keeps the receiver waiting until its own
receipt and claim; a saved prompt changed since planning fails, before any
receipt as behind an older one. A saved-prompt read that spends the bound
starts no exchange read.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    GENERATION,
    OTHER_LAUNCH,
    QUESTION,
    REQUESTOR_LAUNCH,
    REQUESTOR_PANE,
    REVIEWER_PANE,
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
    resumed,
    single,
    taken,
    unused,
    used,
)
from tools.resume_paused_delivery_model import (
    ActionReport,
    DeliveryOutcome,
    ReceiverState,
)
from tools.resume_paused_models import ArtifactError, SessionRole
from tools.resume_paused_plan_model import ActionKind, PlannedAction
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import Host
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_takeover import OBSERVATION_BOUND
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from tools.resume_paused_artifacts import CheckoutSnapshot
    from tools.resume_paused_input import PaneRecord
    from tools.resume_paused_review import ExchangeSnapshot

BOUND = OBSERVATION_BOUND.total_seconds()
FIRST_WAITS = [0.5, 1.0, 2.0, 4.0]
CAP = 5.0
LAST_WAIT = 2.5
SECOND_READ = 2


def receive(world: TakeoverWorld, report: ActionReport | None = None) -> ActionReport:
    """Observe one accepted resume through the declared takeover."""
    return world.takeover().received(FakePair(world), report or resumed())


def receipts(*states: CheckoutSnapshot | Exception) -> FakeSnapshots:
    """Declare the saved pause across looks."""
    return FakeSnapshots(Declared(list(states)))


def exchanges(*observed: ExchangeSnapshot) -> FakeExchanges:
    """Declare the exchange across looks."""
    return FakeExchanges(Declared(list(observed)))


def test_a_requestor_settles_claimed_once_its_takeover_is_durable() -> None:
    """No receipt yet, then the receipt and the current marked claim: claimed at the claim's generation."""
    world = TakeoverWorld(snapshots=receipts(unused(), used()), exchanges=exchanges(exchange(None), taken()))
    report = receive(world)
    assert (report.outcome, report.receiver, report.generation, report.failed) == (DeliveryOutcome.ACCEPTED, ReceiverState.CLAIMED, GENERATION, False)
    assert (world.clock.sleeps, world.snapshots.declared.reads, world.exchanges.declared.reads) == ([FIRST_WAITS[0]], 2, 2)


def implementation_resume() -> tuple[TakeoverWorld, ActionReport]:
    """Return the world and accepted report of a single Claude implementation pause."""
    state, receiver = single()
    command = marked_command(Host.CLAUDE, ActionKind.RESUME, receiver)
    action = PlannedAction(ActionKind.RESUME, SessionRole.IMPLEMENTATION, Host.CLAUDE, "s", REQUESTOR_PANE, "single", command)
    return TakeoverWorld(snapshots=receipts(state)), ActionReport(action, DeliveryOutcome.ACCEPTED)


def test_a_single_agent_settles_consumed_on_its_receipt() -> None:
    """A single agent claims nothing: its schema 3 receipt settles it at once, with no exchange read."""
    world, accepted = implementation_resume()
    report = receive(world, accepted)
    assert (report.receiver, report.generation, world.clock.sleeps, world.exchanges.declared.reads) == (ReceiverState.CONSUMED, None, [], 0)


def test_a_paused_reviewer_resumes_only_itself() -> None:
    """A reviewer pause's receiver settles on its receipt; it never waits for a requestor claim."""
    state, receiver = single(SessionRole.REVIEWER, changes={"Resumed by": "chatgpt"})
    command = marked_command(Host.CODEX, ActionKind.RESUME, receiver)
    action = PlannedAction(ActionKind.RESUME, SessionRole.REVIEWER, Host.CODEX, "s", REVIEWER_PANE, "reviewer", command)
    world = TakeoverWorld(snapshots=receipts(state), exchanges=exchanges(exchange(None)))
    report = receive(world, ActionReport(action, DeliveryOutcome.ACCEPTED))
    assert (report.receiver, world.clock.sleeps) == (ReceiverState.CONSUMED, [])


def test_nothing_durable_within_the_bound_is_completion_unconfirmed() -> None:
    """Capped backoff fills exactly the bound, every look re-reads, and the outcome stays a success."""
    world = TakeoverWorld(snapshots=receipts(unused()))
    report = receive(world)
    sleeps = world.clock.sleeps
    assert (report.outcome, report.receiver, report.failed) == (DeliveryOutcome.ACCEPTED, ReceiverState.COMPLETION_UNCONFIRMED, False)
    assert (sleeps[: len(FIRST_WAITS)], max(sleeps), sleeps[-1], sum(sleeps)) == (FIRST_WAITS, CAP, LAST_WAIT, BOUND)
    assert world.snapshots.declared.reads == len(sleeps)
    observe_bounds = [bound for name, bound in world.transport.bounds if name == "observe"]
    assert (max(observe_bounds), observe_bounds[-1]) == (30.0, LAST_WAIT)


@pytest.mark.parametrize(
    "observed",
    [exchange(None), exchange(marker(), owner=Actor.REVIEWER), exchange(kind=ExchangeObservationKind.BUSY)],
)
def test_a_receipt_without_a_current_claim_stays_consumed_at_the_bound(observed: ExchangeSnapshot) -> None:
    """No claim, a competing pickup or a busy exchange: the requestor consumed but its takeover is unproved."""
    world = TakeoverWorld(snapshots=receipts(used()), exchanges=exchanges(observed))
    report = receive(world)
    assert (report.receiver, report.generation, report.failed, sum(world.clock.sleeps)) == (ReceiverState.CONSUMED, None, False, BOUND)


def failing(change: str) -> TakeoverWorld:
    """Return a world whose receiver shows one declared failure."""
    world = TakeoverWorld()
    if change == "result":
        world.results.lines = {REQUESTOR_PANE: (f"resume-paused {REQUESTOR_LAUNCH} failed",)}
    elif change == "question":
        world.transport.observations = [listing(activity={REQUESTOR_PANE: QUESTION})]
    elif change == "other-launch":
        world.snapshots = receipts(used(changes={"Launch id": OTHER_LAUNCH}))
    elif change == "unreadable":
        world.snapshots = receipts(ArtifactError("receipt-malformed"))
    else:
        world.exchanges = exchanges(exchange(kind=ExchangeObservationKind.DAMAGED))
    return world


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        ("result", "receiver-failed"),
        ("question", "receiver-question"),
        ("other-launch", "receipt-other-launch"),
        ("unreadable", "evidence-invalid"),
        ("damaged", "exchange-damaged"),
    ],
)
def test_receiver_failures_fail_the_action(change: str, reason: str) -> None:
    """A failed result, a repeated question, another launch's receipt or damaged evidence fails."""
    report = receive(failing(change))
    assert (report.outcome, report.receiver, report.reason, report.failed) == (DeliveryOutcome.ACCEPTED, ReceiverState.FAILED, reason, True)


def test_an_older_receipt_of_the_accepted_prompt_keeps_the_receiver_waiting() -> None:
    """The planner accepts a fresh prompt behind an older receipt: the receiver is awaited, then claimed."""
    world = TakeoverWorld(snapshots=receipts(older(), used()), exchanges=exchanges(exchange(None), taken()))
    report = receive(world)
    assert (report.receiver, report.generation, report.failed, world.clock.sleeps) == (ReceiverState.CLAIMED, GENERATION, False, FIRST_WAITS[:1])


def test_an_older_receipt_alone_at_the_bound_is_completion_unconfirmed() -> None:
    """A receiver that never writes its own receipt behind the older one is unconfirmed, never failed as replaced."""
    world = TakeoverWorld(snapshots=receipts(older()))
    report = receive(world)
    assert (report.receiver, report.failed, sum(world.clock.sleeps)) == (ReceiverState.COMPLETION_UNCONFIRMED, False, BOUND)


@pytest.mark.parametrize("states", [(unused(), unused(Host.CLAUDE)), (older(), used(Host.CLAUDE))])
def test_a_prompt_changed_since_planning_fails_the_receiver(states: tuple[CheckoutSnapshot, ...]) -> None:
    """Before any receipt, or behind an older one, a saved prompt other than the accepted one fails as replaced."""
    world = TakeoverWorld(snapshots=receipts(*states))
    report = receive(world)
    assert (report.receiver, report.reason, report.failed, world.clock.sleeps) == (ReceiverState.FAILED, "prompt-replaced", True, FIRST_WAITS[:1])


def test_a_prompt_accepted_by_the_plan_but_already_replaced_fails_at_once() -> None:
    """The plan read other bytes than the saved prompt now holds: the first look fails it."""
    world = TakeoverWorld(snapshots=receipts(unused()))
    report = world.takeover().received(FakePair(world, digest=accepted(unused(Host.CLAUDE))), resumed())
    assert (report.receiver, report.reason, world.clock.sleeps) == (ReceiverState.FAILED, "prompt-replaced", [])


def test_no_exchange_read_starts_once_the_prompt_read_spent_the_bound() -> None:
    """A saved-prompt read that ends at the bound leaves no time: the exchange observer is never called."""
    world = TakeoverWorld(snapshots=receipts(used()))

    def spend_bound(count: int) -> None:
        del count
        world.clock.advance(BOUND)

    world.snapshots.declared.on_read = spend_bound
    report = receive(world)
    assert (report.receiver, world.snapshots.declared.reads, world.exchanges.declared.reads) == (ReceiverState.COMPLETION_UNCONFIRMED, 1, 0)


@pytest.mark.parametrize(
    "lines",
    [
        None,
        (
            "resume-paused a1a1",
            f"resume-paused {OTHER_LAUNCH} failed",
            f"resume-paused {REQUESTOR_LAUNCH} claimed g{GENERATION}",
            f"resume-paused {REQUESTOR_LAUNCH} failed " + "x" * 80,
        ),
    ],
)
def test_masked_foreign_or_unreadable_results_prove_nothing(lines: tuple[str, ...] | None) -> None:
    """Truncated, over-long or foreign lines and an unreadable source never decide; durable records do."""
    world = TakeoverWorld()
    world.results.lines = {REQUESTOR_PANE: lines}
    report = receive(world)
    assert (report.receiver, report.generation) == (ReceiverState.CLAIMED, GENERATION)


@pytest.mark.parametrize("listed", [None, listing(Host.CODEX).panes[1:]])
def test_an_unlisted_receiver_is_judged_on_durable_records(listed: tuple[PaneRecord, ...] | None) -> None:
    """A failed discovery or a receiver missing from the listing shows no failure; the records still decide."""
    world = TakeoverWorld()
    base = listing()
    world.transport.observations = [None if listed is None else replace(base, panes=listed)]
    assert receive(world).receiver is ReceiverState.CLAIMED


def test_a_look_completed_after_the_bound_is_not_acted_on() -> None:
    """A read that ends after the bound is ignored even when it shows the takeover."""
    world = TakeoverWorld(snapshots=receipts(unused(), used()))
    world.snapshots.declared.on_read = lambda count: world.clock.advance(BOUND if count == SECOND_READ else 0)
    report = receive(world)
    assert (report.receiver, report.generation) == (ReceiverState.COMPLETION_UNCONFIRMED, None)


def test_a_failure_read_after_the_bound_is_not_acted_on() -> None:
    """A failed result line whose read ends after the bound fails nothing."""
    world = TakeoverWorld(snapshots=receipts(unused()))
    world.results.lines = {REQUESTOR_PANE: (f"resume-paused {REQUESTOR_LAUNCH} failed",)}
    world.results.on_read = lambda: world.clock.advance(BOUND)
    report = receive(world)
    assert (report.receiver, report.failed) == (ReceiverState.COMPLETION_UNCONFIRMED, False)


def test_unaccepted_reports_stay_unobserved() -> None:
    """A refused or unconfirmed send has no receiver to observe."""
    world = TakeoverWorld()
    refused = replace(resumed(), outcome=DeliveryOutcome.REFUSED)
    commandless = replace(resumed(), action=replace(resumed().action, command=None))
    assert (receive(world, refused), receive(world, commandless), world.snapshots.declared.reads) == (refused, commandless, 0)


def test_an_unreadable_marker_fails_the_receiver() -> None:
    """A delivered command whose marker does not parse cannot be observed."""
    world = TakeoverWorld()
    broken = replace(resumed(), action=replace(resumed().action, command="/resume-session --resume-paused broken"))
    report = receive(world, broken)
    assert (report.receiver, report.reason, report.failed) == (ReceiverState.FAILED, "marker-unreadable", True)
