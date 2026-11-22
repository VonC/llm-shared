"""Pure consumption and requestor-takeover proofs of the human-launched bulk resume.

Step 7 of v0.14.0 resume-paused keeps command acceptance, prompt consumption
and ownership restoration separate (design, "Takeover observation and later
reviewer continuation"). Every proof here is computed from one fresh
``Durable`` read of the records receivers write: the checkout's saved pause
with its usage receipt, and the saved exchange with its current marked claim.
Nothing is cached between proofs, so a later call never reuses stale evidence.

- ``consumption``: the prompt is still the saved one (a removed, replaced or
  unreadable pause fails) and its schema 3 receipt names this launch, pane and
  assignment binding, resumed by the planned host. No receipt yet is waiting;
  a receipt of another launch, or an unmarked one, fails. Without a planned
  marker (a later continuation), the requestor marker and host are rebuilt
  from the receipt alone (``requestor_marker``).
- ``takeover_ready``: consumption, then a live exchange whose recorded
  requestor nature is the requestor's host.
- ``current_claim``: the coordination record's marked claim names this
  launch, pane, host and binding, was issued at the current ownership
  generation, is owned by the requestor and keeps the exchange occurrence.
  The binding is rebuilt with ``resolve_assignment`` for the requestor role
  at the claimed round, which proves the receipt is a requestor's: a paused
  reviewer's receipt never triggers a counterpart. The proved counterpart is
  the other pane of that assignment's pair, so a switched pair names its
  switched reviewer, and a recorded reviewer nature must be its host.
- ``takeover``: both, for an observation that needs no leave-alone check.

The exact active-reviewer leave-alone check sits between the two
(``tools.resume_paused_reviewer_wait``). A claim owned by anyone else, or
another marked claim, is ``BLOCKED`` (a competing pickup) and a missing claim
is ``WAITING``; neither permits input. The module performs no IO.

Fix (Step 7 code review round 1): each proof binds the ``intended`` digest,
the saved prompt the plan accepted for delivery. The bulk planner accepts a
fresh prompt whose older receipt names other bytes (``NEW_SINCE_USE``), so
that older receipt keeps the proof waiting, while a saved prompt whose digest
differs from the intended one fails as replaced, even before any receipt
exists. ``read_pause`` and ``read_exchange`` split ``read_durable`` so an
observer can stop between the two reads once its bound is spent.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Final, cast

from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_marker import LiveExchange, Marker, resolve_assignment
from tools.resume_paused_models import ArtifactError, SessionRole, host_for_agent
from tools.resume_paused_review import ExchangeObservationKind
from tools.resume_paused_routing import SavedExchange
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_artifacts import (
        CheckoutSnapshot,
        PromptMetadata,
        UsageReceipt,
    )
    from tools.resume_paused_marker import AssignedPane
    from tools.resume_paused_models import CanonicalRoot, PromptDigest
    from tools.resume_paused_planner import ExchangeObserver
    from tools.resume_paused_profiles import Host
    from tools.resume_paused_review import ExchangeSnapshot
    from tools.resume_paused_routing import SavedRouting
    from tools.review_exchange_models_coordination import MarkedClaimEvidence

MARKED_SCHEMA: Final = 3


class ProofState(StrEnum):
    """One proof's verdict: proved, not yet (waiting), definitively no input (blocked) or a failure."""

    PROVED = "proved"
    WAITING = "waiting"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True)
class Proof:
    """A proof verdict with its reason.

    A proved consumption carries the requestor marker and host it proved; a
    proved claim adds the current generation and the counterpart pane.
    """

    state: ProofState
    reason: str = ""
    marker: Marker | None = None
    host: Host | None = None
    generation: int | None = None
    counterpart: str | None = None


_PAUSE_FAILURES: Final = {
    PromptState.ERROR: Proof(ProofState.FAILED, "checkout-unreadable"),
    PromptState.NO_PROMPT: Proof(ProofState.FAILED, "prompt-removed"),
}
_REPLACED: Final = Proof(ProofState.FAILED, "prompt-replaced")
_UNCONSUMED: Final = {
    PromptState.UNUSED: Proof(ProofState.WAITING, "receipt-absent"),
    PromptState.NEW_SINCE_USE: Proof(ProofState.WAITING, "receipt-earlier"),
}
_EXCHANGE_STATES: Final = {
    ExchangeObservationKind.BUSY: Proof(ProofState.WAITING, "exchange-busy"),
    ExchangeObservationKind.NOT_LIVE: Proof(ProofState.BLOCKED, "exchange-not-live"),
    ExchangeObservationKind.SELECTION_CHANGED: Proof(ProofState.FAILED, "exchange-selection-changed"),
    ExchangeObservationKind.DAMAGED: Proof(ProofState.FAILED, "exchange-damaged"),
}


@dataclass(frozen=True)
class Durable:
    """One fresh read of the durable records: the saved pause and, when routing names one, its exchange."""

    snapshot: CheckoutSnapshot
    exchange: ExchangeSnapshot | None = None

    @property
    def routing(self) -> SavedRouting | None:
        """Return the saved routing, ``None`` when the prompt has none that parsed."""
        reading = self.snapshot.routing
        return None if reading is None else reading.routing


def _saved_exchange(snapshot: CheckoutSnapshot) -> SavedExchange | None:
    """Return the exchange the saved routing names, ``None`` for a single-agent or unreadable routing."""
    reading = snapshot.routing
    routing = None if reading is None else reading.routing
    exchange = None if routing is None else routing.exchange
    return exchange if isinstance(exchange, SavedExchange) else None


def read_pause(root: CanonicalRoot, read_snapshot: Callable[[CanonicalRoot], CheckoutSnapshot]) -> CheckoutSnapshot | Proof:
    """Read the checkout's saved pause once, or fail on unreadable evidence."""
    try:
        return read_snapshot(root)
    except ArtifactError:
        return Proof(ProofState.FAILED, "evidence-invalid")


def read_exchange(root: CanonicalRoot, snapshot: CheckoutSnapshot, exchanges: ExchangeObserver) -> Durable:
    """Complete one read of the saved pause with its saved exchange, observed only when routing names one."""
    saved = _saved_exchange(snapshot)
    return Durable(snapshot, None if saved is None else exchanges.observe(root, saved))


def read_durable(root: CanonicalRoot, read_snapshot: Callable[[CanonicalRoot], CheckoutSnapshot], exchanges: ExchangeObserver) -> Durable | Proof:
    """Read the checkout's saved pause and its saved exchange once, or fail on unreadable evidence."""
    snapshot = read_pause(root, read_snapshot)
    return snapshot if isinstance(snapshot, Proof) else read_exchange(root, snapshot, exchanges)


def requestor_marker(receipt: UsageReceipt) -> Marker | None:
    """Rebuild the requestor's marker from a complete schema 3 receipt, ``None`` otherwise."""
    launch, pane, binding = receipt.launch_id, receipt.receiving_pane, receipt.assignment_binding
    if receipt.schema != MARKED_SCHEMA or launch is None or pane is None or binding is None:
        return None
    return Marker(launch, pane, SessionRole.REQUESTOR, binding)


def _pause(snapshot: CheckoutSnapshot, intended: PromptDigest | None) -> Proof | None:
    """Return why the saved pause proves no consumption yet, ``None`` once a receipt names its prompt.

    Without an intended digest, a receipt for other bytes means the prompt was
    replaced after its use; with one, it is an older receipt and the prompt
    must still be the intended one.
    """
    state = snapshot.state
    if state in _PAUSE_FAILURES:
        return _PAUSE_FAILURES[state]
    prompt = cast("PromptMetadata", snapshot.prompt)
    replaced = state is PromptState.NEW_SINCE_USE if intended is None else prompt.digest != intended
    return _REPLACED if replaced else _UNCONSUMED.get(state)


def consumption(durable: Durable, marker: Marker | None = None, host: Host | None = None, intended: PromptDigest | None = None) -> Proof:
    """Prove that this launch's schema 3 receipt consumed the unchanged saved prompt.

    Args:
        durable: One fresh read of the checkout's records.
        marker: The delivered marker, or ``None`` to rebuild the requestor's from the receipt.
        host: The receiver's planned host, or ``None`` to take the receipt's.
        intended: The digest of the prompt the plan accepted for delivery, or
            ``None`` to judge the saved prompt against its receipt alone. An
            older receipt then waits, and any other prompt fails as replaced.
    """
    pause = _pause(durable.snapshot, intended)
    if pause is not None:
        return pause
    receipt = cast("UsageReceipt", durable.snapshot.receipt)
    expected = marker or requestor_marker(receipt)
    if expected is None:
        return Proof(ProofState.FAILED, "receipt-unmarked")
    if (receipt.schema, receipt.launch_id, receipt.receiving_pane, receipt.assignment_binding) != (
        MARKED_SCHEMA, expected.launch_id, expected.pane_id, expected.binding,
    ):
        return Proof(ProofState.FAILED, "receipt-other-launch")
    resumed = host_for_agent(receipt.resumed_by)
    if resumed is None or (host is not None and resumed is not host):
        return Proof(ProofState.FAILED, "receipt-host-mismatch")
    return Proof(ProofState.PROVED, marker=expected, host=resumed)


def takeover_ready(durable: Durable, marker: Marker | None = None, host: Host | None = None, intended: PromptDigest | None = None) -> Proof:
    """Prove consumption of the intended prompt and a live exchange whose recorded requestor nature is the requestor's host."""
    consumed = consumption(durable, marker, host, intended)
    if consumed.state is not ProofState.PROVED:
        return consumed
    exchange = durable.exchange
    if exchange is None:
        return Proof(ProofState.BLOCKED, "pairing-not-applicable")
    if exchange.kind is not ExchangeObservationKind.OBSERVED:
        return _EXCHANGE_STATES[exchange.kind]
    if exchange.requestor_nature is None:
        return Proof(ProofState.WAITING, "role-nature-unrecorded")
    if exchange.requestor_nature != cast("Host", consumed.host).value:
        return Proof(ProofState.BLOCKED, "role-nature-mismatch")
    return consumed


def _pair(durable: Durable, marker: Marker, claim: MarkedClaimEvidence) -> tuple[AssignedPane, AssignedPane] | None:
    """Return the requestor assignment's pair at the claimed round when its digest is the marker binding."""
    routing, prompt = cast("SavedRouting", durable.routing), cast("PromptMetadata", durable.snapshot.prompt)
    try:
        assignment = resolve_assignment(routing, prompt.digest, marker.pane_id, SessionRole.REQUESTOR, LiveExchange(claim.occurrence, claim.round_number))
    except ArtifactError:
        return None
    pair = assignment.pair
    if assignment.digest() != marker.binding or pair is None or pair[0].pane_id != marker.pane_id:
        return None
    return pair


def current_claim(durable: Durable, ready: Proof) -> Proof:
    """Require the ready requestor's marked claim to be the exchange's current requestor claim."""
    exchange, marker, host = cast("ExchangeSnapshot", durable.exchange), cast("Marker", ready.marker), cast("Host", ready.host)
    binding, generation = exchange.marked_claim, exchange.ownership_generation
    if binding is None or generation is None:
        return Proof(ProofState.WAITING, "claim-absent")
    claim = binding.evidence
    if binding.issued_generation != generation or exchange.owner is not Actor.REQUESTOR:
        return Proof(ProofState.BLOCKED, "claim-superseded")
    if (claim.launch_id, claim.pane_id, claim.host, claim.assignment_binding) != (marker.launch_id, marker.pane_id, host.value, marker.binding):
        return Proof(ProofState.BLOCKED, "claim-other-launch")
    if claim.occurrence != exchange.occurrence:
        return Proof(ProofState.BLOCKED, "claim-occurrence-changed")
    return _counterpart(durable, ready, claim, generation)


def _counterpart(durable: Durable, ready: Proof, claim: MarkedClaimEvidence, generation: int) -> Proof:
    """Prove the receipt is the requestor's at the claimed round and name its counterpart, whose nature must agree."""
    exchange, marker = cast("ExchangeSnapshot", durable.exchange), cast("Marker", ready.marker)
    pair = _pair(durable, marker, claim)
    if pair is None or pair[0].host is not ready.host:
        return Proof(ProofState.BLOCKED, "receipt-not-requestor")
    if exchange.reviewer_nature not in {None, pair[1].host.value}:
        return Proof(ProofState.BLOCKED, "role-nature-mismatch")
    return replace(ready, generation=generation, counterpart=pair[1].pane_id)


def takeover(durable: Durable, marker: Marker | None = None, host: Host | None = None, intended: PromptDigest | None = None) -> Proof:
    """Prove the requestor's whole takeover of the intended prompt: readiness, then its current marked claim."""
    ready = takeover_ready(durable, marker, host, intended)
    return ready if ready.state is not ProofState.PROVED else current_claim(durable, ready)


__all__ = [
    "MARKED_SCHEMA",
    "Durable",
    "Proof",
    "ProofState",
    "consumption",
    "current_claim",
    "read_durable",
    "read_exchange",
    "read_pause",
    "requestor_marker",
    "takeover",
    "takeover_ready",
]


# eof
