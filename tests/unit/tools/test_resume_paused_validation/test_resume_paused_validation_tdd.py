"""Read-only receiver validation and the fenced marked receiving sequence.

Step 4 of v0.14.0 resume-paused: the validator parses the marker, reads the
saved pause, observes the live exchange, rebuilds the assignment, checks the
consumption stage, proves the receiving pane from live discovery and its
complete typed input through the host prover, and returns typed non-secret
JSON. Each refusal names its reason and the compact failure line; nothing is
written. The shared receiver harness runs the real validator and the real
locked claim before each protected write, receipt, journal and claim, with the
evidence changed in between: a refusal stops the sequence, keeps any truthful
earlier write and never claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.resume_paused_receiver_test_support import (
    CODEX_SESSION_ID,
    FakeDiscovery,
    FakeProver,
    ReceiverCheckout,
    ReceiverHarness,
    Step,
    command,
    scenario_routing,
)
from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    prompt_text,
    tree,
    write,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    part,
    single_agent,
)
from tools.resume_paused_input import CarriedIdentity, InputProver, PaneRecord
from tools.resume_paused_marker import MARKER_FLAG, LiveExchange
from tools.resume_paused_models import PROMPT_NAME, SessionRole
from tools.resume_paused_profiles import Host
from tools.resume_paused_validation import (
    OPERATION,
    ReceiverValidator,
    ValidationRequest,
)
from tools.review_exchange_models import ReviewRole

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

LAUNCH = "0123456789abcdef0123456789abcdef"
OTHER_LAUNCH = "fedcba9876543210fedcba9876543210"


def validator(receiver: ReceiverCheckout, *, discovery: FakeDiscovery | None = None, codex: FakeProver | None = None) -> ReceiverValidator:
    """Return the real validator over declared panes and provers."""
    panes = (receiver.pane(REQUESTOR_PANE, Host.CODEX), receiver.pane(REVIEWER_PANE, Host.CLAUDE))
    provers: dict[Host, InputProver] = {Host.CODEX: codex or FakeProver(), Host.CLAUDE: FakeProver(session_id=None)}
    return ReceiverValidator(discovery or FakeDiscovery(panes), provers, receiver.clock.now)


def test_unconsumed_requestor_is_valid_and_carries_its_codex_session(tmp_path: Path) -> None:
    """A fresh marked requestor validates and returns the session identity to carry."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    result = validator(receiver).validate(ValidationRequest(receiver.root, command(marker), Host.CODEX))
    assert (result.valid, result.reasons, result.consumed, result.live) == (True, (), False, LiveExchange(1, 1))
    data = result.to_json()
    assert data["carried"] == {"session_id": CODEX_SESSION_ID, "launch_id": LAUNCH}
    assert (data["operation"], data["result"], data["role"], data["pane_id"]) == (OPERATION, None, "requestor", REQUESTOR_PANE)
    assert data["exchange"] == {"round": 1, "occurrence": 1}


def test_prompt_consumed_by_this_launch_stays_valid(tmp_path: Path) -> None:
    """After its own receipt, the same launch still validates for later protected writes."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    receiver.consume(marker)
    carried = CarriedIdentity(CODEX_SESSION_ID, LAUNCH)
    result = validator(receiver).validate(ValidationRequest(receiver.root, command(marker), Host.CODEX, carried))
    assert (result.valid, result.consumed) == (True, True)


def test_reviewer_needs_the_requestor_receipt(tmp_path: Path) -> None:
    """A reviewer validates only after the requestor's marked resume consumed the prompt."""
    receiver = ReceiverCheckout(tmp_path, "request")
    reviewer = receiver.marker(REVIEWER_PANE, SessionRole.REVIEWER, OTHER_LAUNCH)
    request = ValidationRequest(receiver.root, command(reviewer), Host.CLAUDE)
    assert validator(receiver).validate(request).reasons == ("requestor-receipt-missing",)
    receiver.consume(receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH))
    result = validator(receiver).validate(request)
    assert (result.valid, result.consumed, result.carried_session) == (True, False, None)


def test_single_agent_validates_without_an_exchange(tmp_path: Path) -> None:
    """A single implementation pause binds no pair and observes no exchange."""
    receiver = ReceiverCheckout(tmp_path, "answer")

    def single(mapping: dict[str, object]) -> None:
        """Make the pause a single implementation pause."""
        single_agent(mapping)
        part(mapping, "pause")["session_role"] = "implementation"

    receiver.publish(scenario_routing(receiver.root, single), role="implementation")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.IMPLEMENTATION, LAUNCH, None)
    result = validator(receiver).validate(ValidationRequest(receiver.root, command(marker), Host.CODEX))
    assert (result.valid, result.live) == (True, None)


@dataclass(frozen=True)
class Overrides:
    """What one refusal case changes in the request or the declared evidence."""

    text: str | None = None
    host: Host = Host.CODEX
    carried: CarriedIdentity | None = None
    discovery: FakeDiscovery | None = None
    codex: FakeProver | None = None


def _remove(receiver: ReceiverCheckout, *names: str) -> Overrides:
    """Remove artifacts from the artifact home."""
    for name in names:
        (receiver.root / ".reviews" / name).unlink()
    return Overrides()


def _unusable_home(receiver: ReceiverCheckout) -> Overrides:
    """Break the artifact home's ignore file."""
    write(receiver.root, ".gitignore", b"#" + bytes([10]))
    return Overrides()


def _table_only(receiver: ReceiverCheckout) -> Overrides:
    """Replace the prompt with one carrying only an earlier prose routing table."""
    write(receiver.root, PROMPT_NAME, prompt_text(receiver.root, "| Target | Agent host and intended role | x |" + chr(10)))
    return Overrides()


def _unknown_reviewer(mapping: dict[str, object]) -> None:
    """Record the reviewer target as unknown."""
    part(mapping, "targets").update(reviewer={"unknown": "closed"})


def _receipt_of_another_checkout(receiver: ReceiverCheckout) -> Overrides:
    """Consume the prompt by this launch, but with a receipt naming another checkout."""
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    receiver.consume(marker, {"Project root": str(receiver.root.parent / "other")})
    return Overrides()


def _unreadable_review_mode(receiver: ReceiverCheckout) -> Overrides:
    """Break the review-mode marker the exchange observation loads."""
    write(receiver.root, "a.review-mode", "not a wait override")
    return Overrides()


def _unresolved(receiver: ReceiverCheckout) -> Overrides:
    """Publish routing whose reviewer is unknown."""
    receiver.publish(scenario_routing(receiver.root, _unknown_reviewer))
    return Overrides()


def _used_by_another_launch(receiver: ReceiverCheckout) -> Overrides:
    """Consume the prompt by another launch's marker."""
    receiver.consume(receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, OTHER_LAUNCH))
    return Overrides()


def _panes(*panes: PaneRecord) -> Overrides:
    """Declare the live discovery of one refusal case."""
    return Overrides(discovery=FakeDiscovery(panes))


REFUSALS: dict[str, tuple[Callable[[ReceiverCheckout], Overrides], str]] = {
    "malformed marker": (lambda _r: Overrides(text=f"/resume-session {MARKER_FLAG} nope"), "marker-malformed"),
    "carried launch differs": (lambda _r: Overrides(carried=CarriedIdentity(CODEX_SESSION_ID, OTHER_LAUNCH)), "carried-launch-id-mismatch"),
    "no prompt": (lambda r: _remove(r, PROMPT_NAME), "prompt-unavailable"),
    "unusable home": (_unusable_home, "checkout-unreadable"),
    "receipt of another checkout": (_receipt_of_another_checkout, "checkout-unreadable"),
    "table-only routing": (_table_only, "routing-table-only"),
    "unresolved routing": (_unresolved, "routing-unresolved"),
    "exchange not live": (lambda r: _remove(r, r.store.paths.coordination.name, r.store.paths.answer.name), "exchange-not-live"),
    "unreadable review mode": (_unreadable_review_mode, "exchange-unreadable"),
    "other round bound": (lambda r: Overrides(text=command(r.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH, LiveExchange(1, 2)))), "binding-mismatch"),
    "other host": (lambda _r: Overrides(host=Host.CLAUDE), "host-mismatch"),
    "used by another launch": (_used_by_another_launch, "prompt-already-used"),
    "discovery failed": (lambda _r: Overrides(discovery=FakeDiscovery(None)), "discovery-failed"),
    "pane absent": (lambda r: _panes(r.pane(REVIEWER_PANE, Host.CLAUDE)), "pane-absent"),
    "pane ambiguous": (lambda r: _panes(r.pane(REQUESTOR_PANE, Host.CODEX), r.pane(REQUESTOR_PANE, Host.CODEX)), "pane-ambiguous"),
    "other session": (lambda r: _panes(r.pane(REQUESTOR_PANE, Host.CODEX, session="other")), "session-mismatch"),
    "other checkout": (lambda r: _panes(r.pane(REQUESTOR_PANE, Host.CODEX, cwd=r"C:\elsewhere")), "checkout-mismatch"),
    "unparsable checkout": (lambda r: _panes(r.pane(REQUESTOR_PANE, Host.CODEX, cwd="relative")), "checkout-mismatch"),
    "pane runs claude": (lambda r: _panes(r.pane(REQUESTOR_PANE, Host.CLAUDE)), "pane-host-mismatch"),
    "input unproved": (lambda _r: Overrides(codex=FakeProver(proved=False)), "marked-input-not-latest"),
    "input unproved without reason": (lambda _r: Overrides(codex=FakeProver(proved=False, reason="")), "input-unproved"),
}


@pytest.mark.parametrize("name", list(REFUSALS))
def test_every_refusal_names_its_reason_and_writes_nothing(tmp_path: Path, name: str) -> None:
    """Each changed or missing piece of evidence stops the receiver with one reason, read-only."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    setup, reason = REFUSALS[name]
    overrides = setup(receiver)
    before = tree(receiver.root)
    checker = validator(receiver, discovery=overrides.discovery, codex=overrides.codex)
    request = ValidationRequest(receiver.root, overrides.text or command(marker), overrides.host, overrides.carried)
    result = checker.validate(request)
    assert (result.valid, result.reasons) == (False, (reason,))
    assert tree(receiver.root) == before
    data = result.to_json()
    assert data["carried"] is None
    if result.marker is not None:
        assert data["result"] == f"resume-paused {LAUNCH} failed"


def test_missing_host_prover_is_unsupported(tmp_path: Path) -> None:
    """Without a host prover, the receiver's input cannot be proved."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    checker = ReceiverValidator(FakeDiscovery((receiver.pane(REQUESTOR_PANE, Host.CODEX),)), {}, receiver.clock.now)
    assert checker.validate(ValidationRequest(receiver.root, command(marker), Host.CODEX)).reasons == ("host-profile-unsupported",)


def test_inherited_pane_variable_never_proves_the_pane(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A shared daemon's inherited ``TUIOS_PANE_ID`` naming the target is not discovery evidence."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    monkeypatch.setenv("TUIOS_PANE_ID", REQUESTOR_PANE)
    checker = validator(receiver, discovery=FakeDiscovery((receiver.pane(REVIEWER_PANE, Host.CLAUDE),)))
    assert checker.validate(ValidationRequest(receiver.root, command(marker), Host.CODEX)).reasons == ("pane-absent",)


def harness(tmp_path: Path, receiver: ReceiverCheckout, codex: FakeProver) -> ReceiverHarness:
    """Return the shared harness over the real validator and a temporary journal."""
    return ReceiverHarness(receiver, validator(receiver, codex=codex), tmp_path / "sessions.journal.md")


def test_codex_requestor_sequence_writes_receipt_journal_and_claim(tmp_path: Path) -> None:
    """Every protected write follows a fresh validation, carrying the first proof's identity."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    prover = FakeProver()
    run = harness(tmp_path, receiver, prover).run(marker, Host.CODEX, ReviewRole.REQUESTOR)
    assert (run.written, run.stopped_at) == ([Step.RECEIPT, Step.JOURNAL, Step.CLAIM], None)
    carried = CarriedIdentity(CODEX_SESSION_ID, LAUNCH)
    assert prover.carried == [None, carried, carried]
    record = receiver.store.read_coordination(required=True)
    assert record is not None
    assert record.marked_claim is not None
    assert (record.marked_claim.issued_generation, record.marked_claim.evidence.launch_id) == (run.generation, LAUNCH)


def test_changed_prompt_before_the_receipt_writes_nothing(tmp_path: Path) -> None:
    """A prompt edited before consumption stops the sequence with no receipt, journal or claim."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    journal = tmp_path / "sessions.journal.md"

    def edit(step: Step) -> None:
        """Change the prompt just before the receipt."""
        if step is Step.RECEIPT:
            write(receiver.root, PROMPT_NAME, receiver.prompt + b"\nLater note.\n")

    run = ReceiverHarness(receiver, validator(receiver), journal).run(marker, Host.CODEX, ReviewRole.REQUESTOR, before=edit)
    assert (run.written, run.stopped_at, run.reason) == ([], Step.RECEIPT, "binding-mismatch")
    assert not journal.exists()


def test_new_typed_input_before_the_journal_keeps_the_truthful_receipt(tmp_path: Path) -> None:
    """Consumption already happened: the receipt stays, the journal and claim do not happen."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)
    prover = FakeProver()

    def newer_input(step: Step) -> None:
        """Make the latest typed input another command before the journal write."""
        if step is Step.JOURNAL:
            prover.proved = False

    run = harness(tmp_path, receiver, prover).run(marker, Host.CODEX, ReviewRole.REQUESTOR, before=newer_input)
    assert (run.written, run.stopped_at, run.reason) == ([Step.RECEIPT], Step.JOURNAL, "marked-input-not-latest")
    assert (receiver.root / ".reviews" / "a.session-resume.used.local.md").exists()
    record = receiver.store.read_coordination(required=True)
    assert record is not None
    assert record.marked_claim is None


def test_changed_routing_before_the_claim_claims_nothing(tmp_path: Path) -> None:
    """A routing change after consumption stops before the claim; earlier writes stay truthful."""
    receiver = ReceiverCheckout(tmp_path, "answer")
    marker = receiver.marker(REQUESTOR_PANE, SessionRole.REQUESTOR, LAUNCH)

    def reroute(step: Step) -> None:
        """Re-route the reviewer before the claim."""
        if step is Step.CLAIM:
            receiver.publish(scenario_routing(receiver.root, lambda m: part(part(m, "targets"), "reviewer").update(pane_id="5b1c0d2e-3f40-4a5b-8c6d-7e8f90a1b2c3")))

    run = harness(tmp_path, receiver, FakeProver()).run(marker, Host.CODEX, ReviewRole.REQUESTOR, before=reroute)
    assert (run.written, run.stopped_at, run.reason) == ([Step.RECEIPT, Step.JOURNAL], Step.CLAIM, "binding-mismatch")
    record = receiver.store.read_coordination(required=True)
    assert record is not None
    assert record.marked_claim is None


# eof
