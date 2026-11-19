"""Marked claims under the transition lock: binding recomputation and refusals.

Step 4 of v0.14.0 resume-paused threads the raw marker through the locked
selected claim. Under the transition lock, the verifier parses the marker,
rebuilds the assignment from the current prompt, saved routing and locked
exchange round and occurrence, compares the binding and the claimant host,
and requires the receipt that consumed the prompt: the requestor's own schema
3 receipt for this launch, or for a reviewer the requestor's receipt. A Codex
claimant must carry the session identity and launch id of its first
validation. Every refusal happens before any write: coordination, transcript,
prompt and receipt keep their bytes, and no generation is issued. The claim
reads no host session file and needs no TUIOS.
"""

from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.resume_paused_receiver_test_support import (
    CODEX_SESSION_ID as SESSION_ID,
)
from tests.unit.tools.resume_paused_receiver_test_support import (
    PLAN,
    command,
    receiver_validator,
    scenario_routing,
)
from tests.unit.tools.resume_paused_receiver_test_support import (
    ReceiverCheckout as Scenario,
)
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
    receipt_text,
    write,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    part,
)
from tools.llm_nature import LlmNature
from tools.resume_paused_artifacts import render_routing_section
from tools.resume_paused_claim import marked_claim_verifier, verifier_from_arguments
from tools.resume_paused_input import CarriedIdentity
from tools.resume_paused_marker import LiveExchange, Marker
from tools.resume_paused_models import (
    PROMPT_NAME,
    RECEIPT_NAME,
    PromptDigest,
    SessionRole,
)
from tools.resume_paused_profiles import Host
from tools.resume_paused_validation import ValidationRequest
from tools.review_exchange_cli_parser import parser_for
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_exchange_models_coordination import MarkedClaimEvidence
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from tools.review_exchange_store import ReviewExchangeStore
    from tools.review_resume_identity import MarkedClaimVerifier

REQUESTOR_LAUNCH = "0123456789abcdef0123456789abcdef"
REVIEWER_LAUNCH = "fedcba9876543210fedcba9876543210"


def requestor_scenario(tmp_path: Path) -> tuple[Scenario, Marker]:
    """Return an answer-pending exchange whose requestor prompt was consumed by its marker."""
    scenario = Scenario(tmp_path, "answer")
    marker = scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH)
    scenario.consume(marker)
    return scenario, marker


def claim(scenario: Scenario, role: ReviewRole, nature: LlmNature, verifier: MarkedClaimVerifier) -> int:
    """Run the real locked selected claim and return the issued generation."""
    capability = claim_selected(scenario.core, role, nature, round_number=1, occurrence=1, override=False, marked=verifier)
    return capability.generation


def stored_binding(store: ReviewExchangeStore) -> object:
    """Read the marked claim binding back from durable coordination."""
    record = store.read_coordination(required=True)
    assert record is not None
    return record.marked_claim


def test_codex_requestor_claim_records_its_binding_with_the_new_generation(tmp_path: Path) -> None:
    """The verified marked requestor claim records launch, pane, host, binding, round and occurrence."""
    scenario, marker = requestor_scenario(tmp_path)
    verifier = marked_claim_verifier(scenario.root, marker.render(), ReviewRole.REQUESTOR, Host.CODEX, CarriedIdentity(SESSION_ID, REQUESTOR_LAUNCH))
    generation = claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)
    expected = MarkedClaimEvidence(REQUESTOR_LAUNCH, REQUESTOR_PANE, "codex", marker.binding, 1, 1)
    assert stored_binding(scenario.store) == expected.issued(generation)


def test_claude_reviewer_claim_needs_the_requestor_receipt(tmp_path: Path) -> None:
    """A reviewer claims only after the requestor's marked resume consumed the prompt."""
    scenario = Scenario(tmp_path, "request")
    requestor = scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH)
    reviewer = scenario.marker(REVIEWER_PANE, SessionRole.REVIEWER, REVIEWER_LAUNCH)
    scenario.consume(requestor)
    verifier = marked_claim_verifier(scenario.root, reviewer.render(), ReviewRole.REVIEWER, Host.CLAUDE, None)
    generation = claim(scenario, ReviewRole.REVIEWER, LlmNature.CLAUDE, verifier)
    expected = MarkedClaimEvidence(REVIEWER_LAUNCH, REVIEWER_PANE, "claude", reviewer.binding, 1, 1)
    assert stored_binding(scenario.store) == expected.issued(generation)


def _changed_prompt(scenario: Scenario, _marker: Marker) -> None:
    """Edit the prompt after the marker was bound."""
    write(scenario.root, PROMPT_NAME, scenario.prompt + b"\nLater note.\n")


def _changed_routing(scenario: Scenario, _marker: Marker) -> None:
    """Re-route the reviewer to another pane after the marker was bound."""
    other = scenario_routing(scenario.root, lambda m: part(part(m, "targets"), "reviewer").update(pane_id="5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3"))
    write(scenario.root, PROMPT_NAME, prompt_text(scenario.root, "\n".join(render_routing_section(other)) + "\n"))


def _unbound_receipt(scenario: Scenario, marker: Marker) -> None:
    """Replace the receipt with one bound to another launch."""
    scenario.consume(marker, {"Launch id": REVIEWER_LAUNCH})


def _manual_receipt(scenario: Scenario, _marker: Marker) -> None:
    """Replace the receipt with a manual schema 2 receipt for the same prompt."""
    write(scenario.root, RECEIPT_NAME, receipt_text(2, PromptDigest.of(scenario.prompt).value, scenario.root))


def _other_exchange(scenario: Scenario, _marker: Marker) -> None:
    """Point the saved exchange at another plan, rebinding a fresh marker to it."""
    scenario.publish(scenario_routing(scenario.root, lambda m: part(m, "exchange").update(document="docs/plan.v0.11.0.other-topic.md")))
    scenario.consume(scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH))


REFUSALS: dict[str, tuple[Callable[[Scenario, Marker], None] | None, str]] = {
    "changed prompt": (_changed_prompt, "binding-mismatch"),
    "changed routing": (_changed_routing, "binding-mismatch"),
    "receipt of another launch": (_unbound_receipt, "receipt-not-bound"),
    "manual receipt": (_manual_receipt, "receipt-not-bound"),
    "other exchange": (_other_exchange, "exchange-mismatch"),
}


@pytest.mark.parametrize("name", list(REFUSALS))
def test_changed_evidence_refuses_the_claim_before_any_write(tmp_path: Path, name: str) -> None:
    """Prompt, routing, receipt and exchange changes stop the claim with nothing written."""
    scenario, marker = requestor_scenario(tmp_path)
    change, code = REFUSALS[name]
    if change is not None:
        change(scenario, marker)
    text = marker.render() if name != "other exchange" else scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH).render()
    before = scenario.evidence()
    verifier = marked_claim_verifier(scenario.root, text, ReviewRole.REQUESTOR, Host.CODEX, CarriedIdentity(SESSION_ID, REQUESTOR_LAUNCH))
    with pytest.raises(ReviewExchangeError, match=rf"marked claim refused: {code}$"):
        claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)
    assert scenario.evidence() == before


@dataclass(frozen=True)
class Mismatch:
    """One marked claim whose marker, host or carried identity does not match."""

    marker_of: Callable[[Scenario], str]
    host: Host
    carried: CarriedIdentity | None
    code: str


def _requestor_marker(scenario: Scenario) -> str:
    """Render the requestor's marker for the current prompt and first round."""
    return scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH).render()


CARRIED = CarriedIdentity(SESSION_ID, REQUESTOR_LAUNCH)
MISMATCHES: dict[str, Mismatch] = {
    "round advanced": Mismatch(lambda s: s.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH, LiveExchange(1, 2)).render(), Host.CODEX, CARRIED, "binding-mismatch"),
    "codex without identity": Mismatch(_requestor_marker, Host.CODEX, None, "carried-identity-missing"),
    "carried launch differs": Mismatch(_requestor_marker, Host.CODEX, CarriedIdentity(SESSION_ID, REVIEWER_LAUNCH), "carried-launch-id-mismatch"),
    "empty session identity": Mismatch(_requestor_marker, Host.CODEX, CarriedIdentity("", REQUESTOR_LAUNCH), "carried-identity-missing"),
    "host differs": Mismatch(_requestor_marker, Host.CLAUDE, None, "host-mismatch"),
    "marker role differs": Mismatch(lambda s: s.marker(REQUESTOR_PANE, SessionRole.REVIEWER, REQUESTOR_LAUNCH).render(), Host.CODEX, CARRIED, "marker-role-mismatch"),
    "malformed marker": Mismatch(lambda _s: "not-a-marker", Host.CODEX, CARRIED, "marker-malformed"),
}


@pytest.mark.parametrize("name", list(MISMATCHES))
def test_marker_and_carried_identity_mismatches_refuse_the_claim(tmp_path: Path, name: str) -> None:
    """A stale round, missing or wrong carried identity, other host or role, or bad marker writes nothing."""
    case = MISMATCHES[name]
    scenario, _marker = requestor_scenario(tmp_path)
    before = scenario.evidence()
    verifier = marked_claim_verifier(scenario.root, case.marker_of(scenario), ReviewRole.REQUESTOR, case.host, case.carried)
    with pytest.raises(ReviewExchangeError, match=rf"marked claim refused: {case.code}$"):
        claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)
    assert scenario.evidence() == before


def _republished(scenario: Scenario, change: Callable[[dict[str, object]], None], live: LiveExchange | None) -> str:
    """Publish changed routing, consume it with a fresh requestor marker and return that marker."""
    scenario.publish(scenario_routing(scenario.root, change))
    marker = scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH, live)
    scenario.consume(marker)
    return marker.render()


def _no_umbrella(mapping: dict[str, object]) -> None:
    """Save the exchange without its umbrella."""
    part(mapping, "exchange")["umbrella"] = None


def _single_requestor(mapping: dict[str, object]) -> None:
    """Save a single requestor pause with no pair and no exchange."""
    absent = {"not_applicable": "single-agent pause"}
    part(mapping, "targets").update(requestor=absent, reviewer=absent)
    mapping["exchange"] = absent


def _unresolved(scenario: Scenario) -> str:
    """Keep the bound marker but publish routing with an unknown reviewer."""
    marker = _requestor_marker(scenario)
    scenario.publish(scenario_routing(scenario.root, lambda m: part(m, "targets").update(reviewer={"unknown": "closed"})))
    return marker


ROUTING_REFUSALS: dict[str, tuple[Callable[[Scenario], str], str]] = {
    "umbrella differs": (lambda s: _republished(s, _no_umbrella, LiveExchange(1, 1)), "exchange-mismatch"),
    "no exchange to claim": (lambda s: _republished(s, _single_requestor, None), "exchange-not-applicable"),
    "unresolved routing": (_unresolved, "routing-unresolved"),
}


@pytest.mark.parametrize("name", list(ROUTING_REFUSALS))
def test_routing_that_names_no_exact_exchange_refuses_the_claim(tmp_path: Path, name: str) -> None:
    """Another umbrella, a single-agent pause or unknown routing never claims the locked exchange."""
    setup, code = ROUTING_REFUSALS[name]
    scenario = Scenario(tmp_path, "answer")
    text = setup(scenario)
    verifier = marked_claim_verifier(scenario.root, text, ReviewRole.REQUESTOR, Host.CODEX, CARRIED)
    with pytest.raises(ReviewExchangeError, match=rf"marked claim refused: {code}$"):
        claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)


@pytest.mark.parametrize("role", [ReviewRole.REQUESTOR, ReviewRole.REVIEWER])
def test_receipt_moved_to_another_checkout_after_validation_refuses_the_claim(tmp_path: Path, role: ReviewRole) -> None:
    """Fix (code review round 1): an error snapshot never reaches backfill or ownership.

    The receiver validates a good receipt; then only the receipt's project
    root changes, keeping its digest and marked fields. The checkout snapshot
    becomes an error that still carries the parsed prompt and receipt, and the
    locked claim must refuse it with nothing written and no generation issued.
    """
    requestor = role is ReviewRole.REQUESTOR
    scenario = Scenario(tmp_path, "answer" if requestor else "request")
    consumed = scenario.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, REQUESTOR_LAUNCH)
    scenario.consume(consumed)
    marker = consumed if requestor else scenario.marker(REVIEWER_PANE, SessionRole.REVIEWER, REVIEWER_LAUNCH)
    host, carried = (Host.CODEX, CARRIED) if requestor else (Host.CLAUDE, None)
    assert receiver_validator(scenario).validate(ValidationRequest(scenario.root, command(marker), host)).valid
    scenario.consume(consumed, {"Project root": str(scenario.root.parent / "other")})
    before = scenario.evidence()
    verifier = marked_claim_verifier(scenario.root, marker.render(), role, host, carried)
    with pytest.raises(ReviewExchangeError, match=r"marked claim refused: checkout-unreadable$"):
        claim(scenario, role, LlmNature.CODEX if requestor else LlmNature.CLAUDE, verifier)
    assert scenario.evidence() == before


def test_reviewer_without_the_requestor_receipt_is_refused(tmp_path: Path) -> None:
    """The reviewer cannot claim while the requestor has not consumed the prompt."""
    scenario = Scenario(tmp_path, "request")
    reviewer = scenario.marker(REVIEWER_PANE, SessionRole.REVIEWER, REVIEWER_LAUNCH)
    before = scenario.evidence()
    verifier = marked_claim_verifier(scenario.root, reviewer.render(), ReviewRole.REVIEWER, Host.CLAUDE, None)
    with pytest.raises(ReviewExchangeError, match=r"marked claim refused: requestor-receipt-missing$"):
        claim(scenario, ReviewRole.REVIEWER, LlmNature.CLAUDE, verifier)
    assert scenario.evidence() == before


def test_unreadable_saved_pause_refuses_the_claim(tmp_path: Path) -> None:
    """A missing prompt is not routing: the claim stops with the snapshot diagnostic."""
    scenario, marker = requestor_scenario(tmp_path)
    (scenario.root / ".reviews" / PROMPT_NAME).unlink()
    verifier = marked_claim_verifier(scenario.root, marker.render(), ReviewRole.REQUESTOR, Host.CODEX, CarriedIdentity(SESSION_ID, REQUESTOR_LAUNCH))
    with pytest.raises(ReviewExchangeError, match=r"marked claim refused: prompt-unavailable$"):
        claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)


def test_claim_arguments_carry_the_marker_and_codex_identity(tmp_path: Path) -> None:
    """The claim command accepts the raw marker and both carried values and builds the verifier."""
    scenario, marker = requestor_scenario(tmp_path)
    args = parser_for("claim").parse_args([
        "claim", "--document", PLAN, "--role", "requestor", "--round", "1", "--occurrence", "1",
        "--resume-paused-marker", marker.render(), "--carried-session", SESSION_ID, "--carried-launch-id", REQUESTOR_LAUNCH,
    ])
    verifier = verifier_from_arguments(args, scenario.root, ReviewRole.REQUESTOR, LlmNature.CODEX)
    assert verifier is not None
    generation = claim(scenario, ReviewRole.REQUESTOR, LlmNature.CODEX, verifier)
    assert stored_binding(scenario.store) == MarkedClaimEvidence(REQUESTOR_LAUNCH, REQUESTOR_PANE, "codex", marker.binding, 1, 1).issued(generation)


@pytest.mark.parametrize(
    "args",
    [Namespace(resume_paused_marker=None, carried_session=None, carried_launch_id=None), Namespace(document=PLAN)],
    ids=["parsed without a marker", "caller predating the marker"],
)
def test_unmarked_claim_arguments_build_no_verifier(tmp_path: Path, args: Namespace) -> None:
    """Manual claims, including callers that predate the marked arguments, keep their consent path."""
    assert verifier_from_arguments(args, tmp_path, ReviewRole.REQUESTOR, LlmNature.CODEX) is None


def test_marked_claim_needs_a_known_host(tmp_path: Path) -> None:
    """A marked claim from an unrecognized host is refused before any lock."""
    args = Namespace(resume_paused_marker="m", carried_session=None, carried_launch_id=None)
    with pytest.raises(ReviewExchangeError, match=r"marked claim refused: host-unsupported$"):
        verifier_from_arguments(args, tmp_path, ReviewRole.REQUESTOR, LlmNature.GEMINI)


# eof
