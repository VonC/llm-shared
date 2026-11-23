"""Test-only receiver harness for marked resume-paused workflows.

Step 4 of v0.15.0 resume-paused (plan Q02=A) shares one harness between the
receiver unit tests and the later acceptance tests. ``ReceiverCheckout``
declares a checkout with a prepared review exchange, a routed pause prompt and
the markers bound to it. ``ReceiverHarness`` runs the marked receiving
sequence against temporary files with the real validator and the real locked
claim: validate, write the schema 3 receipt, validate, write the session
journal entry, validate, claim. A hook may change the evidence before each
protected step; the sequence stops at the first refusal and reports what was
written. It is not a production receipt or journal writer and proves only its
executed sequence, not arbitrary live-agent compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    checkout,
    prompt_text,
    receipt_text,
    write,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
    part,
    routing_mapping,
)
from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tests.unit.tools.test_review_resume.prepared_phase import prepare_phase
from tools.llm_nature import LlmNature
from tools.resume_paused_artifacts import render_routing_section
from tools.resume_paused_claim import marked_claim_verifier
from tools.resume_paused_input import CarriedIdentity, InputEvidence, PaneRecord
from tools.resume_paused_marker import (
    MARKER_FLAG,
    LiveExchange,
    Marker,
    resolve_assignment,
)
from tools.resume_paused_models import (
    PROMPT_NAME,
    RECEIPT_NAME,
    PromptDigest,
    SessionRole,
)
from tools.resume_paused_profiles import Host, ReadAccount
from tools.resume_paused_routing import SavedRouting
from tools.resume_paused_validation import (
    ReceiverValidator,
    ValidationRequest,
    ValidationResult,
)
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import datetime
    from pathlib import Path

    from tools.resume_paused_input import InputProver

PLAN = "docs/plan.v0.11.0.review-exchange-core.md"
UMBRELLA = "docs/draft.v0.11.0.review-mode.md"
CODEX_SESSION_ID = "019a0000-0000-7000-8000-000000000000"
NATURES = {Host.CLAUDE: LlmNature.CLAUDE, Host.CODEX: LlmNature.CODEX}
FIRST_ROUND = LiveExchange(1, 1)


def scenario_routing(root: Path, change: Callable[[dict[str, object]], None] | None = None) -> SavedRouting:
    """Route a Codex requestor and a Claude reviewer to the lifecycle exchange."""
    mapping = routing_mapping(root)
    targets = part(mapping, "targets")
    for name in ("resumed", "requestor"):
        part(targets, name)["host"] = "codex"
    part(targets, "reviewer")["host"] = "claude"
    mapping["exchange"] = {"family": "code", "document": PLAN, "implementation_step": "3", "umbrella": UMBRELLA, "occurrence": 1, "round": 1}
    if change is not None:
        change(mapping)
    return SavedRouting.from_mapping(mapping)


class ReceiverCheckout:
    """One checkout with a prepared exchange, a routed prompt and its markers."""

    def __init__(self, tmp_path: Path, phase: str) -> None:
        """Prepare the exchange phase and write the routed prompt."""
        self.root = checkout(tmp_path)
        self.core, self.store, context, clock = lifecycle._harness(self.root)
        self.clock = clock
        prepare_phase(self.core, context, clock, phase)
        self.routing = scenario_routing(self.root)
        self.prompt = b""
        self.publish(self.routing)

    def publish(self, routing: SavedRouting, role: str = "requestor") -> None:
        """Write the prompt carrying one routing as a pause writes it, with its session role."""
        self.routing = routing
        section = "\n".join(render_routing_section(routing)) + "\n"
        self.prompt = write(self.root, PROMPT_NAME, prompt_text(self.root, section, role=role))

    def marker(self, pane: str, role: SessionRole, launch: str, live: LiveExchange | None = FIRST_ROUND) -> Marker:
        """Bind a marker to the current prompt bytes and live exchange, or none for a single agent."""
        assignment = resolve_assignment(self.routing, PromptDigest.of(self.prompt), pane, role, live)
        return Marker(launch, pane, role, assignment.digest())

    def consume(self, marker: Marker, changes: dict[str, str | None] | None = None) -> bytes:
        """Write the schema 3 receipt a marked resume-session writes for this marker."""
        fields: dict[str, str | None] = {"Launch id": marker.launch_id, "Receiving pane": marker.pane_id, "Assignment binding": marker.binding}
        return write(self.root, RECEIPT_NAME, receipt_text(3, PromptDigest.of(self.prompt).value, self.root, fields | (changes or {})))

    def evidence(self) -> dict[str, bytes]:
        """Return the bytes every refusal must leave unchanged."""
        paths = self.store.paths
        home = self.root / ".reviews"
        return {
            str(path): path.read_bytes()
            for path in (paths.coordination, paths.transcript, home / PROMPT_NAME, home / RECEIPT_NAME)
            if path.exists()
        }

    def pane(self, pane: str, host: Host, *, session: str = SESSION, cwd: str | None = None) -> PaneRecord:
        """Declare the live agent record of one routed pane."""
        harness, apps = ("claude-code", ()) if host is Host.CLAUDE else ("", ("codex",))
        return PaneRecord(pane, session, "pane", cwd or str(self.root), harness, apps, "claude-session" if host is Host.CLAUDE else None)


def command(marker: Marker) -> str:
    """Return the complete marked native command a bulk launch delivers."""
    return f"/resume-session {MARKER_FLAG} {marker.render()}"


@dataclass
class FakeDiscovery:
    """Declared live agent records; ``None`` models failed discovery."""

    records: tuple[PaneRecord, ...] | None

    def agents(self) -> tuple[PaneRecord, ...] | None:
        """Return the declared listing."""
        return self.records


@dataclass
class FakeProver:
    """Declared complete-input proof, recording each call's carried identity."""

    proved: bool = True
    reason: str = "marked-input-not-latest"
    session_id: str | None = CODEX_SESSION_ID
    carried: list[CarriedIdentity | None] = field(default_factory=list[CarriedIdentity | None])

    def prove(self, pane: PaneRecord, command: str, not_before: datetime, carried: CarriedIdentity | None) -> InputEvidence:
        """Return the declared proof."""
        del pane, command, not_before
        self.carried.append(carried)
        if not self.proved:
            reasons = (self.reason,) if self.reason else ()
            return InputEvidence(proved=False, session_id=None, reasons=reasons, account=ReadAccount())
        return InputEvidence(proved=True, session_id=self.session_id, reasons=(), account=ReadAccount().plus(10))


def receiver_validator(receiver: ReceiverCheckout) -> ReceiverValidator:
    """Return the real validator over the routed panes and proving fakes for both hosts."""
    panes = (receiver.pane(REQUESTOR_PANE, Host.CODEX), receiver.pane(REVIEWER_PANE, Host.CLAUDE))
    provers: dict[Host, InputProver] = {Host.CODEX: FakeProver(), Host.CLAUDE: FakeProver(session_id=None)}
    return ReceiverValidator(FakeDiscovery(panes), provers, receiver.clock.now)


class Step(StrEnum):
    """The protected steps of one marked receiving sequence."""

    RECEIPT = "receipt"
    JOURNAL = "journal"
    CLAIM = "claim"


@dataclass
class SequenceOutcome:
    """What one receiving sequence wrote, and where and why it stopped."""

    written: list[Step] = field(default_factory=list[Step])
    stopped_at: Step | None = None
    reason: str | None = None
    generation: int | None = None
    results: list[ValidationResult] = field(default_factory=list[ValidationResult])


class ReceiverHarness:
    """Run the marked receiving sequence with the real validator and locked claim."""

    def __init__(self, receiver: ReceiverCheckout, validator: ReceiverValidator, journal: Path) -> None:
        """Keep the checkout, the validator and a temporary session journal file."""
        self.receiver = receiver
        self.validator = validator
        self.journal = journal

    def run(  # noqa: PLR0913 - the receiving pane's whole identity and the evidence hook
        self, marker: Marker, host: Host, role: ReviewRole | None, *,
        steps: tuple[Step, ...] = (Step.RECEIPT, Step.JOURNAL, Step.CLAIM),
        before: Callable[[Step], None] | None = None,
    ) -> SequenceOutcome:
        """Validate before each protected step and stop at the first refusal."""
        outcome = SequenceOutcome()
        carried: CarriedIdentity | None = None
        for step in steps:
            if before is not None:
                before(step)
            result = self.validator.validate(ValidationRequest(self.receiver.root, command(marker), host, carried))
            outcome.results.append(result)
            if not result.valid:
                outcome.stopped_at, outcome.reason = step, result.reasons[0]
                return outcome
            if host is Host.CODEX and carried is None and result.carried_session is not None:
                carried = CarriedIdentity(result.carried_session, marker.launch_id)
            if not self._write(step, marker, host, role, carried, outcome):
                return outcome
            outcome.written.append(step)
        return outcome

    def _write(  # noqa: PLR0913 - one protected write with its full binding
        self, step: Step, marker: Marker, host: Host, role: ReviewRole | None, carried: CarriedIdentity | None, outcome: SequenceOutcome,
    ) -> bool:
        """Perform one protected write; a refused claim stops the sequence."""
        if step is Step.RECEIPT:
            self.receiver.consume(marker)
        elif step is Step.JOURNAL:
            self.journal.write_text(f"## Resume by {host.value} launch {marker.launch_id}\n", encoding="utf-8")
        else:
            assert role is not None
            verifier = marked_claim_verifier(self.receiver.root, marker.render(), role, host, carried)
            try:
                capability = claim_selected(self.receiver.core, role, NATURES[host], round_number=1, occurrence=1, override=False, marked=verifier)
            except ReviewExchangeError as error:
                outcome.stopped_at, outcome.reason = step, str(error)
                return False
            outcome.generation = capability.generation
        return True


__all__ = [
    "CODEX_SESSION_ID",
    "FIRST_ROUND",
    "PLAN",
    "UMBRELLA",
    "FakeDiscovery",
    "FakeProver",
    "ReceiverCheckout",
    "ReceiverHarness",
    "SequenceOutcome",
    "Step",
    "command",
    "receiver_validator",
    "scenario_routing",
]


# eof
