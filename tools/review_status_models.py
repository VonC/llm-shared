"""Immutable typed records for repository-wide review status evidence."""

# pyright: reportUnnecessaryIsInstance=false
# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from types import MappingProxyType
from typing import TYPE_CHECKING

from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    ArtifactState,
    ExchangeIdentity,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
    validate_local_timestamp,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


SCHEMA_VERSION = 2
_CONFLICTING_VALUE_COUNT = 2


class ReviewStatusModelError(ValueError):
    """Raised when normalized review-status evidence is internally inconsistent."""


class ReviewStatusOutcome(StrEnum):
    """Repository-level trust outcome and process-status source."""

    TRUSTWORTHY = "trustworthy"
    UNTRUSTWORTHY = "untrustworthy"
    OPERATIONAL_FAILURE = "operational-failure"


class MigrationState(StrEnum):
    """Status-visible outcome of the bounded artifact-placement preflight."""

    UNNECESSARY = "unnecessary"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class RoleNatureState(StrEnum):
    """Status-only states used when role nature is absent or contradictory."""

    UNRECORDED = "unrecorded"
    CONFLICTING = "conflicting"


class LeaseFreshness(StrEnum):
    """Derived lease state at one fixed evaluation timestamp."""

    CURRENT = "current"
    EXPIRED = "expired"
    NOT_HELD = "not-held"
    MISSING = "missing"


class ArtifactApplicability(StrEnum):
    """Whether one canonical artifact is expected for the observed state."""

    EXPECTED = "expected"
    NOT_APPLICABLE = "not-applicable"


class NextAction(StrEnum):
    """Stable protocol intent independent of human display text."""

    WAIT_FOR_COUNTERPART = "wait-for-counterpart"
    REQUESTOR_WORK = "requestor-work"
    REVIEWER_WORK = "reviewer-work"
    HUMAN_CONFIRMATION = "human-confirmation"
    AUTHORIZED_OWNING_WORK = "authorized-owning-work"
    RECLAIM = "reclaim"
    REPAIR = "repair"
    RESOLVE_ESCALATION = "resolve-escalation"
    NO_SAFE_ACTION = "no-safe-action"


class ArtifactKind(StrEnum):
    """The six canonical review-exchange artifact kinds."""

    REQUEST = "request"
    ANSWER = "answer"
    TRANSCRIPT = "transcript"
    COORDINATION = "coordination"
    TOMBSTONE = "tombstone"
    TRANSITION_LOCK = "transition-lock"


class RoleSpecialization(StrEnum):
    """Family-specific form of a continuing requestor or reviewer role."""

    SPECIFICATION_REQUESTOR = "specification-requestor"
    SPECIFICATION_REVIEWER = "specification-reviewer"
    CODE_REQUESTOR = "code-requestor"
    CODE_REVIEWER = "code-reviewer"


def _nonempty(value: str, label: str) -> str:
    """Return stripped nonempty text or reject it with a stable diagnostic."""
    if not isinstance(value, str) or not value.strip():
        raise ReviewStatusModelError(f"{label} must be nonempty text")
    return value


def _positive(value: int, label: str) -> int:
    """Return a positive integer while rejecting booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReviewStatusModelError(f"{label} must be a positive integer")
    return value


def _relative_path(value: str, label: str) -> str:
    """Validate one canonical repository-relative POSIX path."""
    _nonempty(value, label)
    path = PurePosixPath(value)
    invalid = (
        "\\" in value
        or value == "."
        or path.is_absolute()
        or PureWindowsPath(value).is_absolute()
        or ".." in path.parts
        or path.as_posix() != value
    )
    if invalid:
        raise ReviewStatusModelError(f"{label} must be a canonical repository-relative path")
    return value


def _absolute_root(value: str) -> str:
    """Validate one absolute POSIX or Windows repository-root spelling."""
    _nonempty(value, "repository root")
    if "\\" in value or not (
        PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()
    ):
        raise ReviewStatusModelError("repository root must be an absolute POSIX path")
    return value


def _timestamp(value: str, label: str) -> datetime:
    """Parse one timezone-aware exchange timestamp into a comparable value."""
    try:
        validated = validate_local_timestamp(value)
    except ReviewExchangeError as error:
        raise ReviewStatusModelError(f"invalid {label}: {error}") from error
    return datetime.fromisoformat(validated)


@dataclass(frozen=True)
class MigrationStatus:
    """Typed result of the only bounded mutation allowed before status projection."""

    state: MigrationState
    artifact_home: str
    moved_count: int
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Reject migration facts that disagree with the preflight state."""
        if not isinstance(self.state, MigrationState):
            raise ReviewStatusModelError("invalid migration state")
        _relative_path(self.artifact_home, "artifact home")
        self._validate_count()
        self._validate_diagnostics()
        self._validate_relationships()

    def _validate_count(self) -> None:
        """Require one non-boolean non-negative moved-artifact count."""
        if (
            isinstance(self.moved_count, bool)
            or not isinstance(self.moved_count, int)
            or self.moved_count < 0
        ):
            raise ReviewStatusModelError("moved count must be a non-negative integer")

    def _validate_diagnostics(self) -> None:
        """Require an immutable tuple of nonempty diagnostic messages."""
        if not isinstance(self.diagnostics, tuple) or any(
            not isinstance(item, str) or not item.strip() for item in self.diagnostics
        ):
            raise ReviewStatusModelError("migration diagnostics must be nonempty text")

    def _validate_relationships(self) -> None:
        """Require counts and diagnostics to agree with the migration state."""
        if self.state is MigrationState.UNNECESSARY and self.moved_count != 0:
            raise ReviewStatusModelError("unnecessary migration cannot report moved artifacts")
        if self.state is MigrationState.COMPLETED and self.moved_count == 0:
            raise ReviewStatusModelError("completed migration must report moved artifacts")
        if self.state is MigrationState.BLOCKED and not self.diagnostics:
            raise ReviewStatusModelError("blocked migration requires diagnostics")
        if self.state is not MigrationState.BLOCKED and self.diagnostics:
            raise ReviewStatusModelError("successful migration cannot carry diagnostics")

    @classmethod
    def unnecessary(cls, artifact_home: str) -> MigrationStatus:
        """Build an initially-ready placement result."""
        return cls(MigrationState.UNNECESSARY, artifact_home, 0)

    @classmethod
    def completed(cls, artifact_home: str, moved_count: int) -> MigrationStatus:
        """Build a migrated and rechecked-ready placement result."""
        return cls(MigrationState.COMPLETED, artifact_home, moved_count)

    @classmethod
    def blocked(
        cls,
        artifact_home: str,
        diagnostics: tuple[str, ...],
    ) -> MigrationStatus:
        """Build a typed placement failure without claiming projected evidence."""
        return cls(MigrationState.BLOCKED, artifact_home, 0, diagnostics)

    def to_dict(self) -> dict[str, object]:
        """Return the explicit schema-2 migration record."""
        return {
            "state": self.state.value,
            "artifact_home": self.artifact_home,
            "moved_count": self.moved_count,
            "diagnostics": list(self.diagnostics),
        }


@dataclass(frozen=True)
class RoleNatureEvidenceStatus:
    """One repository-relative artifact path and its recorded role nature."""

    path: str
    nature: LlmNature | None

    def __post_init__(self) -> None:
        """Require canonical paths and closed nullable LLM-nature values."""
        _relative_path(self.path, "role-nature evidence path")
        if self.nature is not None and not isinstance(self.nature, LlmNature):
            raise ReviewStatusModelError("invalid role-nature evidence value")

    def to_dict(self) -> dict[str, str | None]:
        """Return one stable machine-readable evidence record."""
        return {
            "path": self.path,
            "nature": None if self.nature is None else self.nature.value,
        }


@dataclass(frozen=True)
class RoleNatureStatus:
    """Reconciled role nature plus all artifact evidence supporting the result."""

    value: LlmNature | RoleNatureState
    evidence: tuple[RoleNatureEvidenceStatus, ...] = ()

    def __post_init__(self) -> None:
        """Reject evidence that contradicts the normalized role-nature value."""
        if not isinstance(self.value, (LlmNature, RoleNatureState)):
            raise ReviewStatusModelError("invalid role-nature status value")
        recorded = self._recorded_values()
        self._validate_relationship(recorded)

    def _recorded_values(self) -> set[LlmNature]:
        """Validate the evidence tuple and return its known values."""
        if not isinstance(self.evidence, tuple) or any(
            not isinstance(item, RoleNatureEvidenceStatus) for item in self.evidence
        ):
            raise ReviewStatusModelError("role-nature evidence must be a typed tuple")
        return {item.nature for item in self.evidence if item.nature is not None}

    def _validate_relationship(self, recorded: set[LlmNature]) -> None:
        """Require the normalized value to agree with all recorded evidence."""
        if self.value is RoleNatureState.UNRECORDED and recorded:
            raise ReviewStatusModelError("unrecorded role nature cannot have recorded evidence")
        if (
            self.value is RoleNatureState.CONFLICTING
            and len(recorded) < _CONFLICTING_VALUE_COUNT
        ):
            raise ReviewStatusModelError("conflicting role nature requires different evidence")
        if isinstance(self.value, LlmNature) and recorded != {self.value}:
            raise ReviewStatusModelError("role nature disagrees with recorded evidence")

    @classmethod
    def unrecorded(cls) -> RoleNatureStatus:
        """Build the legacy-compatible absence used by constructor defaults."""
        return cls(RoleNatureState.UNRECORDED)

    def evidence_dicts(self) -> list[dict[str, str | None]]:
        """Return stable evidence records for the exchange schema."""
        return [item.to_dict() for item in self.evidence]


@dataclass(frozen=True)
class ArtifactStatus:
    """Canonical artifact path with separate applicability and presence facts."""

    path: str
    applicability: ArtifactApplicability
    present: bool

    def __post_init__(self) -> None:
        """Reject noncanonical paths and non-boolean observations."""
        _relative_path(self.path, "artifact path")
        if not isinstance(self.applicability, ArtifactApplicability):
            raise ReviewStatusModelError("invalid artifact applicability")
        if not isinstance(self.present, bool):
            raise ReviewStatusModelError("artifact presence must be boolean")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable artifact schema."""
        return {
            "path": self.path,
            "applicability": self.applicability.value,
            "present": self.present,
        }


@dataclass(frozen=True)
class LeaseStatus:
    """Raw and derived lease evidence fixed at one evaluation timestamp."""

    renewed_at: str | None
    expires_at: str | None
    evaluated_at: str
    timeout_seconds: int
    freshness: LeaseFreshness

    def __post_init__(self) -> None:
        """Reject lease categories that disagree with their fixed timestamps."""
        timeout = _positive(self.timeout_seconds, "lease timeout")
        evaluated = _timestamp(self.evaluated_at, "lease evaluation timestamp")
        if not isinstance(self.freshness, LeaseFreshness):
            raise ReviewStatusModelError("invalid lease freshness")
        if self.freshness in (LeaseFreshness.NOT_HELD, LeaseFreshness.MISSING):
            if self.renewed_at is not None or self.expires_at is not None:
                raise ReviewStatusModelError("lease-free state must not carry lease timestamps")
            return
        if self.renewed_at is None or self.expires_at is None:
            raise ReviewStatusModelError("current or expired lease requires both timestamps")
        renewed = _timestamp(self.renewed_at, "lease renewal timestamp")
        expires = _timestamp(self.expires_at, "lease expiry timestamp")
        if expires != renewed + timedelta(seconds=timeout):
            raise ReviewStatusModelError("lease expiry must equal renewal plus timeout")
        is_current = evaluated < expires
        if is_current is not (self.freshness is LeaseFreshness.CURRENT):
            raise ReviewStatusModelError("lease freshness disagrees with evaluation timestamp")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable lease schema."""
        return {
            "renewed_at": self.renewed_at,
            "expires_at": self.expires_at,
            "evaluated_at": self.evaluated_at,
            "timeout_seconds": self.timeout_seconds,
            "freshness": self.freshness.value,
        }


@dataclass(frozen=True)
class ExchangeStatus:
    """Complete active-exchange evidence with reconciled role natures."""

    identity: ExchangeIdentity
    reviewed_document: str
    umbrella: str | None
    implementation_step: str | None
    round_number: int
    occurrence: int
    state: ArtifactState
    diagnostic: str
    continuing_role: ReviewRole
    specialization: RoleSpecialization
    owner: Actor
    lease: LeaseStatus
    artifacts: Mapping[ArtifactKind, ArtifactStatus]
    requestor_llm_nature: RoleNatureStatus
    reviewer_llm_nature: RoleNatureStatus
    next_action: NextAction
    next_action_text: str

    def __post_init__(self) -> None:
        """Validate complete healthy evidence and freeze the six-key artifact map."""
        _validate_exchange_identity(self)
        _validate_exchange_protocol(self)
        _validate_exchange_artifacts(self)
        object.__setattr__(self, "artifacts", MappingProxyType(dict(self.artifacts)))
        if not isinstance(self.next_action, NextAction):
            raise ReviewStatusModelError("invalid next action")
        _nonempty(self.next_action_text, "next-action text")
        if not isinstance(self.requestor_llm_nature, RoleNatureStatus):
            raise ReviewStatusModelError("invalid requestor LLM-nature status")
        if not isinstance(self.reviewer_llm_nature, RoleNatureStatus):
            raise ReviewStatusModelError("invalid reviewer LLM-nature status")

    def to_dict(self) -> dict[str, object]:
        """Return the explicit stable healthy-entry schema."""
        return {
            "kind": "exchange",
            "identity": self.identity.to_dict(),
            "reviewed_document": self.reviewed_document,
            "umbrella": self.umbrella,
            "implementation_step": self.implementation_step,
            "round": self.round_number,
            "occurrence": self.occurrence,
            "state": self.state.value,
            "diagnostic": self.diagnostic,
            "continuing_role": self.continuing_role.value,
            "specialization": self.specialization.value,
            "owner": self.owner.value,
            "lease": self.lease.to_dict(),
            "artifacts": {
                kind.value: self.artifacts[kind].to_dict() for kind in ArtifactKind
            },
            "requestor_llm_nature": self.requestor_llm_nature.value.value,
            "requestor_llm_nature_evidence": (
                self.requestor_llm_nature.evidence_dicts()
            ),
            "reviewer_llm_nature": self.reviewer_llm_nature.value.value,
            "reviewer_llm_nature_evidence": self.reviewer_llm_nature.evidence_dicts(),
            "next_action": self.next_action.value,
            "next_action_text": self.next_action_text,
        }


def _validate_exchange_identity(exchange: ExchangeStatus) -> None:
    """Validate identity and repository-relative document paths."""
    if not isinstance(exchange.identity, ExchangeIdentity):
        raise ReviewStatusModelError("exchange identity must be validated")
    _relative_path(exchange.reviewed_document, "reviewed document")
    if exchange.umbrella is not None:
        _relative_path(exchange.umbrella, "umbrella")


def _validate_exchange_protocol(exchange: ExchangeStatus) -> None:
    """Validate protocol facts that depend on the exchange identity."""
    _positive(exchange.round_number, "round")
    _positive(exchange.occurrence, "occurrence")
    if not isinstance(exchange.state, ArtifactState) or exchange.state is ArtifactState.IDLE:
        raise ReviewStatusModelError("healthy exchange state must be active")
    _nonempty(exchange.diagnostic, "exchange diagnostic")
    if exchange.continuing_role not in (ReviewRole.REQUESTOR, ReviewRole.REVIEWER):
        raise ReviewStatusModelError("continuing role must name an agent")
    expected_specialization = RoleSpecialization(
        f"{exchange.identity.family.value}-{exchange.continuing_role.value}",
    )
    if exchange.specialization is not expected_specialization:
        raise ReviewStatusModelError("role specialization disagrees with identity and role")
    if exchange.owner not in (Actor.REQUESTOR, Actor.REVIEWER):
        raise ReviewStatusModelError("exchange owner must name an agent")
    if exchange.identity.family is ReviewFamily.CODE:
        _nonempty(exchange.implementation_step or "", "implementation step")
    elif exchange.implementation_step is not None:
        raise ReviewStatusModelError("specification exchange cannot carry a step")


def _validate_exchange_artifacts(exchange: ExchangeStatus) -> None:
    """Validate the complete typed artifact mapping."""
    expected_kinds = set(ArtifactKind)
    if set(exchange.artifacts) != expected_kinds or any(
        not isinstance(value, ArtifactStatus) for value in exchange.artifacts.values()
    ):
        raise ReviewStatusModelError("artifact map must contain all six typed kinds")


@dataclass(frozen=True)
class DamagedCandidateStatus:
    """Untrusted candidate path with only safely parsed optional identity."""

    candidate_path: str
    diagnostic: str
    candidate_identity: ExchangeIdentity | None = None

    def __post_init__(self) -> None:
        """Reject escaped paths, missing diagnostics, and guessed identity text."""
        _relative_path(self.candidate_path, "candidate path")
        _nonempty(self.diagnostic, "candidate diagnostic")
        if self.candidate_identity is not None and not isinstance(
            self.candidate_identity,
            ExchangeIdentity,
        ):
            raise ReviewStatusModelError("candidate identity must be validated or absent")

    def to_dict(self) -> dict[str, object]:
        """Return the explicitly tagged damaged-candidate schema."""
        return {
            "kind": "damaged-candidate",
            "candidate_path": self.candidate_path,
            "identity": (
                None if self.candidate_identity is None else self.candidate_identity.to_dict()
            ),
            "diagnostic": self.diagnostic,
        }


StatusEntry = ExchangeStatus | DamagedCandidateStatus


@dataclass(frozen=True)
class ReviewStatusResult:
    """One immutable schema-2 result shared by all status renderers."""

    schema_version: int
    repository_root: str
    outcome: ReviewStatusOutcome
    exchanges: tuple[StatusEntry, ...]
    active_count: int
    has_errors: bool
    migration: MigrationStatus

    def __post_init__(self) -> None:
        """Reject aggregate counts, flags, and outcomes that contradict entries."""
        if self.schema_version != SCHEMA_VERSION:
            raise ReviewStatusModelError(f"schema version must be {SCHEMA_VERSION}")
        _absolute_root(self.repository_root)
        if not isinstance(self.migration, MigrationStatus):
            raise ReviewStatusModelError("invalid migration status")
        _validate_result_entries(self)
        _validate_result_outcome(self)

    @property
    def process_status(self) -> int:
        """Return the stable shell status derived only from the overall outcome."""
        return {
            ReviewStatusOutcome.TRUSTWORTHY: 0,
            ReviewStatusOutcome.UNTRUSTWORTHY: 3,
            ReviewStatusOutcome.OPERATIONAL_FAILURE: 2,
        }[self.outcome]

    def to_dict(self) -> dict[str, object]:
        """Return the explicit versioned repository-result schema."""
        return {
            "schema_version": self.schema_version,
            "repository_root": self.repository_root,
            "outcome": self.outcome.value,
            "active_count": self.active_count,
            "has_errors": self.has_errors,
            "migration": self.migration.to_dict(),
            "exchanges": [entry.to_dict() for entry in self.exchanges],
        }


def _validate_result_entries(result: ReviewStatusResult) -> None:
    """Validate result entry types, count, and error flag."""
    if not isinstance(result.outcome, ReviewStatusOutcome):
        raise ReviewStatusModelError("invalid review-status outcome")
    if not isinstance(result.exchanges, tuple) or any(
        not isinstance(entry, (ExchangeStatus, DamagedCandidateStatus))
        for entry in result.exchanges
    ):
        raise ReviewStatusModelError("exchanges must be a tuple of typed entries")
    if result.active_count != len(result.exchanges):
        raise ReviewStatusModelError("active count must equal the entry count")
    if not isinstance(result.has_errors, bool):
        raise ReviewStatusModelError("error flag must be boolean")


def _validate_result_outcome(result: ReviewStatusResult) -> None:
    """Validate relationships between overall trust and retained entries."""
    if result.has_errors is not (
        result.outcome is not ReviewStatusOutcome.TRUSTWORTHY
    ):
        raise ReviewStatusModelError("error flag disagrees with overall outcome")
    if result.outcome is ReviewStatusOutcome.TRUSTWORTHY and any(
        isinstance(entry, DamagedCandidateStatus) for entry in result.exchanges
    ):
        raise ReviewStatusModelError("trustworthy outcome cannot contain damaged entries")
    if result.outcome is ReviewStatusOutcome.UNTRUSTWORTHY and not result.exchanges:
        raise ReviewStatusModelError("untrustworthy outcome requires retained evidence")
    if result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE and result.exchanges:
        raise ReviewStatusModelError("operational failure cannot claim observed entries")


# eof
