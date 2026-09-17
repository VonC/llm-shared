"""Immutable wait identities and bounded records shared by the service ports.

UTC values are Unix seconds; persisted records never contain monotonic deadlines.
Physical identities and canonical locations are verified by boundary adapters.
"""

# ruff: noqa: EM101 - WaitError's first argument is a typed machine code.

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import StrEnum
from hashlib import sha256
from json import dumps

MAX_TEXT = 4096
MAX_IDENTITY = 2048


class WaitError(Exception):
    """Typed failure that never substitutes a success acknowledgement."""

    def __init__(self, code: str, detail: str = "", wait_id: str | None = None) -> None:
        """Keep the existing wait identity available on idempotency conflicts."""
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.wait_id = wait_id


def require(condition: bool, detail: str) -> None:  # noqa: FBT001 - Predicate assertion, not a mode flag.
    """Reject invalid domain values before opening a write transaction."""
    if not condition:
        raise WaitError("validation-error", detail)


def utc(value: float | None) -> None:
    """Accept absent or finite UTC evidence, excluding booleans and NaN."""
    require(value is None or (not isinstance(value, bool) and math.isfinite(value)), "UTC must be finite")


class Continuation(StrEnum):
    """Fixed semantic continuations, never caller-authored executable text."""

    RESUME = "resume"
    INSPECT = "inspect"


class Capability(StrEnum):
    """Separate measured functional wake from proven request accounting."""

    STRICT = "strict-idle-supported"
    FUNCTIONAL = "functional-wake-coverage-inconclusive"
    RETAINED = "retained-result-only"
    PENDING = "direct-pending-tool-fallback"
    UNAVAILABLE = "unsupported-or-misconfigured"


class NormalEnd(StrEnum):
    """Only verified direct or host-gated evidence supports automatic arming."""

    DIRECT = "direct-turn-evidence"
    HOST_GATED = "host-gated-turn-end"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class SourceIdentity:
    """Exact physical worktree, artifact generation and applied source policy."""

    kind: str
    repository_id: str
    worktree_id: str
    artifact_home: str
    run_id: str
    round_id: str
    generation: str
    policy_version: str


@dataclass(frozen=True)
class Recipient:
    """Exact host/session and verified physical storage identity."""

    host: str
    host_version: str
    thread_id: str
    profile_id: str


@dataclass(frozen=True)
class DeadlinePolicy:
    """A finite absolute UTC deadline or an explicitly indefinite lifetime."""

    deadline_utc: float | None = None
    indefinite: bool = False

    def __post_init__(self) -> None:
        """Reject omitted, contradictory and nonfinite lifetime policies."""
        require((self.deadline_utc is not None) != self.indefinite, "choose finite or indefinite")
        utc(self.deadline_utc)
        if self.deadline_utc is not None:
            object.__setattr__(self, "deadline_utc", float(self.deadline_utc) or 0.0)


@dataclass(frozen=True)
class WaitIntent:
    """Immutable registration intent; connection incarnations are separate."""

    idempotency_key: str
    source: SourceIdentity
    recipient: Recipient
    deadline: DeadlinePolicy
    continuation: Continuation
    provenance: str
    role: str

    def validate(self) -> None:
        """Require explicit bounded identities and an allowlisted continuation."""
        values = (*asdict(self.source).values(), *asdict(self.recipient).values(), self.idempotency_key, self.provenance, self.role)
        require(all(isinstance(value, str) and bool(value.strip()) and len(value) <= MAX_IDENTITY for value in values), "exact bounded identities required")
        require(self.continuation in tuple(Continuation), "unknown continuation")
        self.deadline.__post_init__()

    def digest(self) -> str:
        """Hash a fixed-order schema with no sorting or incarnation mutation."""
        self.validate()
        return sha256(dumps(asdict(self), ensure_ascii=True, separators=(",", ":")).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HostBinding:
    """Verified route evidence retained independently from the caller intent."""

    recipient: Recipient
    incarnation: str
    capability: Capability
    normal_end: NormalEnd
    policy_version: str
    arming_evidence: str = ""
    normal_end_evidence: str = ""

    def validate(self) -> None:
        """A usable route needs bounded arming evidence and a declared gate."""
        require(self.capability in tuple(Capability) and self.normal_end in tuple(NormalEnd), "unknown capability or gate")
        require(all(0 < len(value) <= MAX_TEXT for value in (self.incarnation, self.policy_version, self.arming_evidence)), "missing route evidence")
        require(len(self.normal_end_evidence) <= MAX_TEXT, "normal-end evidence too large")


@dataclass(frozen=True)
class Observation:
    """Authoritative source evidence with a durable access-loss recovery start."""

    state: str
    generation: str
    observed_utc: float
    completed_utc: float | None = None
    result_reference: str = ""
    result_digest: str = ""
    data: str = ""
    access_loss_utc: float | None = None

    def validate(self) -> None:
        """Bound source data and require a known observation classification."""
        require(self.state in {"pending", "ready", "unknown", "invalid"}, "unknown observation")
        require(bool(self.generation), "missing source generation")
        require(all(len(value) <= MAX_TEXT for value in (self.generation, self.result_reference, self.result_digest, self.data)), "source data too large")
        for value in (self.observed_utc, self.completed_utc, self.access_loss_utc):
            utc(value)


@dataclass(frozen=True)
class Outcome:
    """Immutable decision plus the source and clock evidence used to make it."""

    kind: str
    observation: Observation
    deadline_decision: str
    clock_uncertain: bool

    def validate(self) -> None:
        """Reject unbounded or nonterminal decisions before storing an event."""
        require(self.kind in {"ready", "expired", "monitoring-failure"}, "unknown outcome")
        require(len(self.deadline_decision) <= MAX_TEXT, "deadline evidence too large")
        self.observation.validate()


@dataclass(frozen=True)
class Registration:
    """Committed preparation or arming acknowledgement for one exact intent."""

    wait_id: str
    intent: WaitIntent
    state: str
    created_utc: float
    diagnostic: str = ""


@dataclass(frozen=True)
class Event:
    """Stable event identity committed atomically with its terminal outcome."""

    event_id: str
    wait_id: str
    outcome: Outcome
    created_utc: float


@dataclass(frozen=True)
class Delivery:
    """Restartable transport state; acceptance never means workflow consumption."""

    event_id: str
    incarnation: str
    state: str
    attempt_count: int
    epoch: int
    next_eligible_utc: float | None
    receipt: str
    diagnostic: str
    policy_version: str

    def validate(self) -> None:
        """Bound persisted retry counters and transport evidence."""
        require(self.state in {"eligible", "queued", "accepted", "retry-scheduled", "unavailable", "exhausted"}, "unknown delivery state")
        require(self.attempt_count >= 0 and self.epoch >= 0, "negative retry state")
        require(all(len(value) <= MAX_TEXT for value in (self.incarnation, self.receipt, self.diagnostic, self.policy_version)), "delivery evidence too large")
        utc(self.next_eligible_utc)


@dataclass(frozen=True)
class Cancellation:
    """Durable suppression evidence, separate from immutable source outcomes."""

    wait_id: str
    cancelled_utc: float
    origin: str
    decision: str


@dataclass(frozen=True)
class ConsumptionAttempt:
    """Attempt settlement and abandonment facts for the later consumption fence."""

    attempt_id: str
    event_id: str
    recipient: Recipient
    authority_generation: str
    decision: str
    consumption_id: str | None = None
    workflow_receipt: str = ""
    execution_state: str = ""
    settled_utc: float | None = None
    abandonment_reason: str = ""
    abandonment_utc: float | None = None
    reconciliation_pending: bool = False
    superseded: bool = False


# eof
