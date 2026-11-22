"""Consumption and requestor-takeover proof tests over declared durable records.

Step 7 of v0.14.0 resume-paused: each proof is computed from one declared
``Durable`` read, the receipt parsed from declared bytes and the exchange
carrying a declared marked claim. A removed, replaced or unreadable pause
fails; no receipt yet waits; another launch's receipt fails; an exchange that
is not observed waits, blocks or fails by its kind; a missing claim waits; a
superseded claim, another launch's claim or a changed occurrence blocks (a
competing pickup); a receipt that is not a requestor's never proves a
counterpart, and a switched pair names its switched reviewer.

Code review round 1: bound to the digest the plan accepted, a fresh prompt
behind an older receipt waits, and any other saved prompt fails as replaced,
with or without a receipt; the takeover proofs pass that digest through.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from tests.unit.tools.test_resume_paused_planner.planner_world import API, snapshot
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    GENERATION,
    OTHER_LAUNCH,
    REQUESTOR_PANE,
    REVIEWER_PANE,
    ROOT,
    THIRD_PANE,
    Declared,
    FakeExchanges,
    accepted,
    exchange,
    marker,
    older,
    pair,
    single,
    taken,
    unused,
    used,
)
from tools.resume_paused_artifacts import CheckoutSnapshot, PromptState
from tools.resume_paused_marker import LiveExchange, Marker
from tools.resume_paused_models import ArtifactError, CanonicalRoot, SessionRole
from tools.resume_paused_profiles import Host
from tools.resume_paused_review import ExchangeObservationKind, ExchangeSnapshot
from tools.resume_paused_takeover_proof import (
    MARKED_SCHEMA,
    Durable,
    Proof,
    ProofState,
    consumption,
    current_claim,
    read_durable,
    requestor_marker,
    takeover,
    takeover_ready,
)
from tools.review_exchange_models import Actor

SECOND_ROUND = 2
SECOND_OCCURRENCE = 2
UNMARKED_SCHEMA = 2


def unmarked() -> CheckoutSnapshot:
    """Return the saved pause consumed by a schema 2 receipt, which names no launch."""
    return snapshot(API, pair(), receipt={"schema": UNMARKED_SCHEMA})


def paired_pause(root: CanonicalRoot) -> CheckoutSnapshot:
    """Read the consumed pair pause."""
    del root
    return used()


def single_pause(root: CanonicalRoot) -> CheckoutSnapshot:
    """Read the consumed single-agent pause."""
    del root
    return single()[0]


def unreadable(root: CanonicalRoot) -> CheckoutSnapshot:
    """Declare a saved pause whose evidence does not parse."""
    del root
    message = "receipt-malformed"
    raise ArtifactError(message)


def test_durable_read_observes_the_exchange_only_when_routing_names_one() -> None:
    """One read takes the saved pause, then the saved exchange of a pair; a single agent has none."""
    exchanges = FakeExchanges(Declared([taken()]))
    paired = read_durable(ROOT, paired_pause, exchanges)
    alone = read_durable(ROOT, single_pause, exchanges)
    assert isinstance(paired, Durable)
    assert isinstance(alone, Durable)
    assert (paired.exchange, alone.exchange, exchanges.declared.reads) == (taken(), None, 1)
    assert paired.routing is not None


def test_unreadable_evidence_fails_the_read() -> None:
    """A saved pause that does not parse is a failure, never absence."""
    proof = read_durable(ROOT, unreadable, FakeExchanges(Declared([taken()])))
    assert isinstance(proof, Proof)
    assert (proof.state, proof.reason) == (ProofState.FAILED, "evidence-invalid")


def test_the_requestor_marker_is_rebuilt_from_a_complete_marked_receipt_only() -> None:
    """A schema 3 receipt names the requestor marker; an older schema names none."""
    receipt, older = used().receipt, unmarked().receipt
    assert receipt is not None
    assert older is not None
    assert (receipt.schema, requestor_marker(receipt), requestor_marker(older)) == (MARKED_SCHEMA, marker(), None)


@pytest.mark.parametrize(
    ("state", "verdict"),
    [
        (unused(), (ProofState.WAITING, "receipt-absent")),
        (used(changes={"digest": "0" * 64}), (ProofState.FAILED, "prompt-replaced")),
        (CheckoutSnapshot(ROOT, None, PromptState.NO_PROMPT), (ProofState.FAILED, "prompt-removed")),
        (CheckoutSnapshot(ROOT, None, PromptState.ERROR, diagnostic="unreadable"), (ProofState.FAILED, "checkout-unreadable")),
        (used(changes={"Launch id": OTHER_LAUNCH}), (ProofState.FAILED, "receipt-other-launch")),
        (used(changes={"Resumed by": "chatgpt"}), (ProofState.FAILED, "receipt-host-mismatch")),
        (used(changes={"Resumed by": "gemini"}), (ProofState.FAILED, "receipt-host-mismatch")),
    ],
)
def test_consumption_needs_this_launch_receipt_on_the_unchanged_prompt(state: CheckoutSnapshot, verdict: tuple[ProofState, str]) -> None:
    """Only the delivered launch's schema 3 receipt, resumed by the planned host, proves consumption."""
    proof = consumption(Durable(state), marker(), Host.CLAUDE)
    assert (proof.state, proof.reason) == verdict


@pytest.mark.parametrize(
    ("state", "verdict"),
    [
        (unused(), (ProofState.WAITING, "receipt-absent")),
        (older(), (ProofState.WAITING, "receipt-earlier")),
        (used(), (ProofState.PROVED, "")),
        (unused(Host.CLAUDE), (ProofState.FAILED, "prompt-replaced")),
        (used(Host.CLAUDE), (ProofState.FAILED, "prompt-replaced")),
        (CheckoutSnapshot(ROOT, None, PromptState.NO_PROMPT), (ProofState.FAILED, "prompt-removed")),
        (CheckoutSnapshot(ROOT, None, PromptState.ERROR, diagnostic="unreadable"), (ProofState.FAILED, "checkout-unreadable")),
    ],
)
def test_consumption_binds_the_prompt_the_plan_accepted(state: CheckoutSnapshot, verdict: tuple[ProofState, str]) -> None:
    """An older receipt of the accepted prompt waits; any other saved prompt is replaced, with or without a receipt."""
    proof = consumption(Durable(state), marker(), Host.CLAUDE, accepted(unused()))
    assert (proof.state, proof.reason) == verdict


def test_the_takeover_proofs_pass_the_accepted_prompt_through() -> None:
    """Readiness and the whole takeover wait behind an older receipt and fail on a replaced prompt."""
    intended = accepted(unused())
    waiting = takeover(Durable(older(), taken()), marker(), Host.CLAUDE, intended)
    replaced = takeover_ready(Durable(used(Host.CLAUDE), taken()), marker(), Host.CLAUDE, intended)
    proved = takeover(Durable(used(), taken()), marker(), Host.CLAUDE, intended)
    assert [(proof.state, proof.reason) for proof in (waiting, replaced)] == [(ProofState.WAITING, "receipt-earlier"), (ProofState.FAILED, "prompt-replaced")]
    assert (proved.state, proved.generation) == (ProofState.PROVED, GENERATION)


def test_consumption_proves_the_marker_and_host() -> None:
    """A proved consumption carries the delivered marker, or the one rebuilt from the receipt, and its host."""
    delivered = consumption(Durable(used()), marker(), Host.CLAUDE)
    rebuilt = consumption(Durable(used()))
    assert (delivered.state, delivered.marker, delivered.host) == (ProofState.PROVED, marker(), Host.CLAUDE)
    assert (rebuilt.state, rebuilt.marker, rebuilt.host) == (ProofState.PROVED, marker(), Host.CLAUDE)


def test_an_unmarked_receipt_proves_no_continuation() -> None:
    """A schema 2 receipt names no launch, so a continuation cannot rebuild its requestor."""
    proof = consumption(Durable(unmarked()))
    assert (proof.state, proof.reason) == (ProofState.FAILED, "receipt-unmarked")


@pytest.mark.parametrize(
    ("observed", "verdict"),
    [
        (None, (ProofState.BLOCKED, "pairing-not-applicable")),
        (exchange(kind=ExchangeObservationKind.BUSY), (ProofState.WAITING, "exchange-busy")),
        (exchange(kind=ExchangeObservationKind.NOT_LIVE), (ProofState.BLOCKED, "exchange-not-live")),
        (exchange(kind=ExchangeObservationKind.SELECTION_CHANGED), (ProofState.FAILED, "exchange-selection-changed")),
        (exchange(kind=ExchangeObservationKind.DAMAGED), (ProofState.FAILED, "exchange-damaged")),
        (exchange(requestor_nature=None), (ProofState.WAITING, "role-nature-unrecorded")),
        (exchange(requestor_nature="codex"), (ProofState.BLOCKED, "role-nature-mismatch")),
    ],
)
def test_readiness_needs_a_live_exchange_with_the_requestor_nature(observed: ExchangeSnapshot | None, verdict: tuple[ProofState, str]) -> None:
    """A missing, busy, closed, changed or damaged exchange, or another requestor nature, is not ready."""
    proof = takeover_ready(Durable(used(), observed), marker(), Host.CLAUDE)
    assert (proof.state, proof.reason) == verdict


def test_readiness_stops_at_an_unproved_consumption() -> None:
    """A receipt that is not there yet keeps the takeover waiting before the exchange is judged."""
    proof = takeover(Durable(unused(), taken()), marker(), Host.CLAUDE)
    assert (proof.state, proof.reason) == (ProofState.WAITING, "receipt-absent")


@pytest.mark.parametrize(
    ("observed", "verdict"),
    [
        (exchange(None), (ProofState.WAITING, "claim-absent")),
        (exchange(marker(), owner=Actor.REVIEWER), (ProofState.BLOCKED, "claim-superseded")),
        (exchange(marker(launch=OTHER_LAUNCH)), (ProofState.BLOCKED, "claim-other-launch")),
        (exchange(marker(), host=Host.CODEX), (ProofState.BLOCKED, "claim-other-launch")),
        (replace(exchange(marker()), occurrence=SECOND_OCCURRENCE), (ProofState.BLOCKED, "claim-occurrence-changed")),
        (exchange(marker(), live_exchange=LiveExchange(SECOND_OCCURRENCE, 1)), (ProofState.BLOCKED, "receipt-not-requestor")),
        (exchange(marker(), reviewer_nature="claude"), (ProofState.BLOCKED, "role-nature-mismatch")),
    ],
)
def test_only_the_current_requestor_marked_claim_proves_takeover(observed: ExchangeSnapshot, verdict: tuple[ProofState, str]) -> None:
    """A missing claim waits; a superseded, foreign, moved or unbound claim, or another reviewer nature, blocks."""
    proof = takeover(Durable(used(), observed), marker(), Host.CLAUDE)
    assert (proof.state, proof.reason) == verdict


def test_a_proved_takeover_names_its_generation_and_counterpart() -> None:
    """The current requestor claim proves the takeover of the saved reviewer pane at its generation."""
    proof = takeover(Durable(used(), exchange(marker(), reviewer_nature="codex")), marker(), Host.CLAUDE)
    assert (proof.state, proof.generation, proof.counterpart, proof.marker) == (ProofState.PROVED, GENERATION, REVIEWER_PANE, marker())


def test_normal_owner_transitions_keep_the_claimed_round_binding() -> None:
    """Later rounds by the same owner keep the generation, and the binding is rebuilt at the claimed round."""
    later = replace(exchange(marker()), round_number=SECOND_ROUND)
    proof = takeover(Durable(used(), later), marker(), Host.CLAUDE)
    assert (proof.state, proof.counterpart) == (ProofState.PROVED, REVIEWER_PANE)


def test_a_paused_reviewer_receipt_never_proves_a_counterpart() -> None:
    """A reviewer's own receipt rebuilds a requestor marker whose binding is not the requestor assignment."""
    reviewer = Marker(OTHER_LAUNCH, REVIEWER_PANE, SessionRole.REVIEWER, marker(SessionRole.REVIEWER).binding)
    state = used(requestor=reviewer, changes={"Resumed by": "chatgpt"})
    observed = exchange(reviewer, host=Host.CODEX, requestor_nature="codex")
    proof = takeover(Durable(state, observed))
    assert (proof.state, proof.reason) == (ProofState.BLOCKED, "receipt-not-requestor")


def test_a_receipt_on_an_unrouted_pane_never_proves_a_counterpart() -> None:
    """A receipt naming a pane outside the saved pair cannot rebuild a requestor assignment."""
    stray = Marker(OTHER_LAUNCH, THIRD_PANE, SessionRole.REQUESTOR, "e" * 64)
    proof = takeover(Durable(used(requestor=stray), exchange(stray)))
    assert (proof.state, proof.reason) == (ProofState.BLOCKED, "receipt-not-requestor")


def test_a_switched_pair_names_its_switched_reviewer() -> None:
    """The saved reviewer resumed as requestor proves the saved requestor pane as its counterpart."""
    switched = marker(SessionRole.REQUESTOR, pane=REVIEWER_PANE, launch=OTHER_LAUNCH)
    state = used(requestor=switched, changes={"Resumed by": "chatgpt"})
    observed = exchange(switched, host=Host.CODEX, requestor_nature="codex", reviewer_nature="claude")
    proof = takeover(Durable(state, observed))
    assert (proof.state, proof.host, proof.counterpart) == (ProofState.PROVED, Host.CODEX, REQUESTOR_PANE)


def test_the_claim_check_extends_the_ready_proof() -> None:
    """The claim check keeps the ready proof's marker and host and adds the generation and counterpart."""
    durable = Durable(used(), taken())
    ready = takeover_ready(durable, marker(), Host.CLAUDE)
    claim = current_claim(durable, ready)
    assert (ready.state, ready.generation, ready.counterpart) == (ProofState.PROVED, None, None)
    assert (claim.marker, claim.host, claim.generation, claim.counterpart) == (marker(), Host.CLAUDE, GENERATION, REVIEWER_PANE)
