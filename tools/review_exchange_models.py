"""Typed protocol models for the v0.11.0 review-exchange core.

Step 1 introduces immutable identities, review context, family policy,
machine-readable envelopes, durable coordination state, marker configuration,
and the shared validation helpers used before any artifact mutation.
"""

# ruff: noqa: EM101, EM102, FLY002, S105, TRY003

from __future__ import annotations

import configparser
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, cast

_VERSION_RE: Final[re.Pattern[str]] = re.compile(r"^v\d+\.\d+\.\d+$")
_SLUG_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_SIGNAL_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_OFFSET_RE: Final[re.Pattern[str]] = re.compile(r"[+-]\d{2}:\d{2}$")
_MARKER_NAME: Final[str] = "a.review-mode"
_SETTINGS_NAME: Final[str] = ".review-exchange.ini"
_SETTINGS_SECTION: Final[str] = "review-exchange"
_SETTINGS_KEY: Final[str] = "wait_timeout_seconds"
# Last resort only. The value that governs is the one in the shipped
# .review-exchange.ini beside this package; this constant answers the single
# case that file cannot: it having been deleted from an installation. The two
# are asserted equal by the test suite so they cannot drift apart.
_FALLBACK_WAIT_SECONDS: Final[int] = 10800
_PACKAGE_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
_SPECIFICATION_TYPES: Final[frozenset[str]] = frozenset(
    {"feature-request", "issue", "design-specification", "plan"},
)
_DOCUMENT_PREFIXES: Final[dict[str, str]] = {
    "feature-request": "feature-request", "issue": "issue",
    "design-specification": "design", "plan": "plan", "code": "plan",
}


class ReviewExchangeError(ValueError):
    """Raised when review-exchange input cannot be handled safely."""


class ReviewFamily(StrEnum):
    """Supported review protocol families."""

    SPECIFICATION = "specification"
    CODE = "code"


class ReviewRole(StrEnum):
    """Roles that author protocol content."""

    REQUESTOR = "requestor"
    REVIEWER = "reviewer"
    HUMAN = "human"


class CoordinationStatus(StrEnum):
    """Durable coordination statuses."""

    ACTIVE = "active"
    AWAITING_HUMAN_CONFIRMATION = "awaiting-human-confirmation"
    ESCALATED = "escalated"


class ReviewDisposition(StrEnum):
    """Machine-readable reviewer answer dispositions."""

    CHANGES_REQUESTED = "changes-requested"
    CONVERGENCE_RECOMMENDED = "convergence-recommended"


class ConfirmationOutcome(StrEnum):
    """Role-neutral human confirmation outcomes."""

    ANOTHER_ROUND = "another-round"
    CONTINUE_OWNING_WORKFLOW = "continue-owning-workflow"


class Actor(StrEnum):
    """Actors that may own or receive a protocol transition."""

    REQUESTOR = "requestor"
    REVIEWER = "reviewer"
    HUMAN = "human"


class IncompleteTransitionKind(StrEnum):
    """Transcript-appending transitions that may require repair."""

    PUBLISH_REQUEST = "publish-request"
    PUBLISH_ANSWER = "publish-answer"
    ESCALATION = "escalation"
    HUMAN_CONFIRMATION = "human-confirmation"
    HUMAN_COMPLETION = "human-completion"
    HUMAN_RECLAIM = "human-reclaim"
    HUMAN_RESOLUTION = "human-resolution"


class ArtifactState(StrEnum):
    """Observable artifact states from the approved state table."""

    IDLE = "idle"
    ROUND_IN_PROGRESS = "round-in-progress"
    REQUEST_PENDING = "request-pending"
    ANSWER_PUBLICATION_IN_PROGRESS = "answer-publication-in-progress"
    TRANSCRIPT_REPAIR_PENDING = "transcript-repair-pending"
    ANSWER_PENDING = "answer-pending"
    CONVERGENCE_GATE = "convergence-gate"
    OWNING_ACTION_PENDING = "owning-action-pending"
    ESCALATED = "escalated"
    ABANDONED_MID_ROUND = "abandoned-mid-round"
    INTERRUPTED_ANSWER_PUBLICATION = "interrupted-answer-publication"
    INTERRUPTED_TRANSCRIPT_APPEND = "interrupted-transcript-append"
    ABANDONED_REQUEST = "abandoned-request"
    ABANDONED_ANSWER = "abandoned-answer"
    INCONSISTENT = "inconsistent"


class ArchiveKind(StrEnum):
    """Evidence kinds allowed in human-recovery archive names."""

    REQUEST = "request"
    ANSWER = "answer"
    CONSUMED = "consumed"
    COORDINATION = "coordination"


def strict_fields(
    data: Mapping[str, Any],
    expected: set[str],
    label: str,
) -> None:
    """Reject missing and unknown keys in one serialized model mapping."""
    actual = set(data)
    unknown = sorted(actual - expected)
    missing = sorted(expected - actual)
    if unknown:
        raise ReviewExchangeError(f"unexpected {label} fields: {', '.join(unknown)}")
    if missing:
        raise ReviewExchangeError(f"missing {label} fields: {', '.join(missing)}")


def enum_value[EnumType: StrEnum](
    enum_type: type[EnumType],
    value: object,
    label: str,
) -> EnumType:
    """Parse one string enum with a stable diagnostic."""
    if not isinstance(value, str):
        raise ReviewExchangeError(f"invalid {label}: expected a string")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ReviewExchangeError(f"invalid {label}: {value}") from error


def optional_string(value: object, label: str) -> str | None:
    """Validate an optional string value."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ReviewExchangeError(f"invalid {label}: expected a string or null")
    return value


def positive_integer(value: object, label: str) -> int:
    """Validate a positive integer while excluding bool values."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ReviewExchangeError(f"invalid {label}: expected a positive integer")
    return value


def non_negative_integer(value: object, label: str) -> int:
    """Validate a non-negative integer while excluding bool values."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ReviewExchangeError(f"invalid {label}: expected a non-negative integer")
    return value


def optional_boolean(value: object, label: str) -> bool | None:
    """Validate an optional boolean value."""
    if value is not None and not isinstance(value, bool):
        raise ReviewExchangeError(f"invalid {label}: expected a boolean or null")
    return value


def path_value(value: object, label: str) -> Path:
    """Parse a serialized path string."""
    if not isinstance(value, str) or not value:
        raise ReviewExchangeError(f"invalid {label}: expected a path string")
    return Path(value)


def optional_path_value(value: object, label: str) -> Path | None:
    """Parse a serialized optional path string."""
    if value is None:
        return None
    return path_value(value, label)


def mapping_value(value: object, label: str) -> Mapping[str, Any]:
    """Return one JSON object mapping with known string keys."""
    if not isinstance(value, Mapping):
        raise ReviewExchangeError(f"invalid {label}: expected an object")
    return cast("Mapping[str, Any]", value)


def validate_local_timestamp(timestamp: str) -> str:
    """Return a valid ISO timestamp carrying an explicit numeric UTC offset."""
    if _OFFSET_RE.search(timestamp) is None:
        raise ReviewExchangeError("timestamp must use ISO-8601 with a numeric UTC offset")
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError as error:
        raise ReviewExchangeError("timestamp must be valid ISO-8601") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ReviewExchangeError("timestamp must use ISO-8601 with a numeric UTC offset")
    return timestamp


def format_local_timestamp() -> str:
    """Return current local system time with a numeric UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


@dataclass(frozen=True)
class ExchangeIdentity:
    """Complete collision-resistant identity for one review exchange."""

    family: ReviewFamily
    type_token: str
    version: str
    slug: str

    def __post_init__(self) -> None:
        """Validate family-specific tokens and filename-safe version data."""
        if self.family is ReviewFamily.CODE and self.type_token != "code":
            raise ReviewExchangeError("code family requires the fixed code type token")
        if (
            self.family is ReviewFamily.SPECIFICATION
            and self.type_token not in _SPECIFICATION_TYPES
        ):
            raise ReviewExchangeError(
                f"unsupported specification type token: {self.type_token}",
            )
        if _VERSION_RE.fullmatch(self.version) is None:
            raise ReviewExchangeError(f"invalid version: {self.version}")
        if _SLUG_RE.fullmatch(self.slug) is None:
            raise ReviewExchangeError(f"invalid slug: {self.slug}")

    @property
    def key(self) -> str:
        """Return the readable complete identity key."""
        return "/".join(
            (self.family.value, self.type_token, self.version, self.slug),
        )

    def to_dict(self) -> dict[str, str]:
        """Return strict JSON-compatible identity data."""
        return {
            "family": self.family.value,
            "type_token": self.type_token,
            "version": self.version,
            "slug": self.slug,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ExchangeIdentity:
        """Construct an identity from strict JSON-compatible data."""
        expected = {"family", "type_token", "version", "slug"}
        strict_fields(data, expected, "identity")
        family = enum_value(ReviewFamily, data["family"], "review family")
        for field in ("type_token", "version", "slug"):
            if not isinstance(data[field], str):
                raise ReviewExchangeError(f"invalid identity {field}")
        return cls(
            family=family,
            type_token=data["type_token"],
            version=data["version"],
            slug=data["slug"],
        )


@dataclass(frozen=True)
class ReviewContext:
    """Validated exact document, umbrella, and implementation-step context."""

    identity: ExchangeIdentity
    document_path: Path
    umbrella_path: Path | None
    implementation_step: str | None

    def __post_init__(self) -> None:
        """Resolve paths and reject context that disagrees with its identity."""
        document = self.document_path.resolve()
        if not document.is_file():
            raise ReviewExchangeError(f"reviewed document does not exist: {document}")
        object.__setattr__(self, "document_path", document)
        if self.identity.family is ReviewFamily.CODE:
            if not self.implementation_step or not self.implementation_step.strip():
                raise ReviewExchangeError("code review requires an implementation step")
        elif self.implementation_step is not None:
            raise ReviewExchangeError(
                "implementation step is only valid for code review",
            )
        prefix = _DOCUMENT_PREFIXES[self.identity.type_token]
        expected_name = (
            f"{prefix}.{self.identity.version}.{self.identity.slug}.md"
        )
        if document.name != expected_name:
            raise ReviewExchangeError(
                "reviewed document does not match exchange identity: "
                f"expected {expected_name}, got {document.name}",
            )
        if self.umbrella_path is not None:
            umbrella = self.umbrella_path.resolve()
            if not umbrella.is_file():
                raise ReviewExchangeError(f"umbrella draft does not exist: {umbrella}")
            object.__setattr__(self, "umbrella_path", umbrella)

    def to_dict(self) -> dict[str, Any]:
        """Return strict JSON-compatible context data."""
        return {
            "identity": self.identity.to_dict(),
            "document_path": self.document_path.as_posix(),
            "umbrella_path": (
                self.umbrella_path.as_posix() if self.umbrella_path is not None else None
            ),
            "implementation_step": self.implementation_step,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ReviewContext:
        """Construct context from strict JSON-compatible data."""
        expected = {
            "identity",
            "document_path",
            "umbrella_path",
            "implementation_step",
        }
        strict_fields(data, expected, "context")
        identity_data = mapping_value(data["identity"], "context identity")
        return cls(
            identity=ExchangeIdentity.from_dict(identity_data),
            document_path=path_value(data["document_path"], "document path"),
            umbrella_path=optional_path_value(data["umbrella_path"], "umbrella path"),
            implementation_step=optional_string(
                data["implementation_step"],
                "implementation step",
            ),
        )


@dataclass(frozen=True)
class FamilyPolicy:
    """Immutable family convergence signal and human display choices."""

    convergence_signal: str
    another_round_label: str
    continue_owning_workflow_label: str

    def __post_init__(self) -> None:
        """Reject empty, ambiguous, or non-machine-readable registration."""
        if _SIGNAL_RE.fullmatch(self.convergence_signal) is None:
            raise ReviewExchangeError(
                "convergence signal must be a non-empty lowercase token",
            )
        labels = (
            self.another_round_label.strip(),
            self.continue_owning_workflow_label.strip(),
        )
        if not all(labels):
            raise ReviewExchangeError("choice labels must be non-empty")
        if labels[0] == labels[1]:
            raise ReviewExchangeError("choice labels must be distinct")
        object.__setattr__(self, "another_round_label", labels[0])
        object.__setattr__(self, "continue_owning_workflow_label", labels[1])

    def label_for(self, outcome: ConfirmationOutcome) -> str:
        """Return the family display label for one role-neutral outcome."""
        if outcome is ConfirmationOutcome.ANOTHER_ROUND:
            return self.another_round_label
        if outcome is ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW:
            return self.continue_owning_workflow_label
        raise ReviewExchangeError(f"unsupported confirmation outcome: {outcome}")

    def outcome_for(self, label: str) -> ConfirmationOutcome:
        """Return the role-neutral outcome registered for a display label."""
        if label == self.another_round_label:
            return ConfirmationOutcome.ANOTHER_ROUND
        if label == self.continue_owning_workflow_label:
            return ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW
        raise ReviewExchangeError(f"unregistered confirmation label: {label}")

    def to_dict(self) -> dict[str, str]:
        """Return strict JSON-compatible policy data."""
        return {
            "convergence_signal": self.convergence_signal,
            "another_round_label": self.another_round_label,
            "continue_owning_workflow_label": self.continue_owning_workflow_label,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> FamilyPolicy:
        """Construct a policy from strict JSON-compatible data."""
        expected = {
            "convergence_signal",
            "another_round_label",
            "continue_owning_workflow_label",
        }
        strict_fields(data, expected, "family policy")
        if not all(isinstance(data[field], str) for field in expected):
            raise ReviewExchangeError("family policy fields must be strings")
        return cls(
            data["convergence_signal"],
            data["another_round_label"],
            data["continue_owning_workflow_label"],
        )


def _wait_setting_of(settings: Path) -> int | None:
    """Read one wait value from a settings file, or None when unusable.

    Every failure returns None rather than raising: a missing file, an
    unreadable one, a malformed one, a missing section or key, and a value that
    is not a positive integer. The caller then falls back to the next source.
    That is deliberate for this file and only for this file, since it may belong
    to a repository that never meant to configure a review.

    Args:
        settings: Path of the candidate settings file.

    Returns:
        The positive wait in seconds, or None when the file does not supply one.
    """
    try:
        content = settings.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(content)
    except configparser.Error:
        return None
    raw = parser.get(_SETTINGS_SECTION, _SETTINGS_KEY, fallback="").strip()
    if not raw.isdecimal() or int(raw) <= 0:
        return None
    return int(raw)


def _default_wait_seconds(project_root: Path) -> int:
    """Resolve the wait that applies when the marker states none.

    The reviewed repository wins over the shipped default, so a project sets its
    own pace by adding one file at its root. The shipped default wins over the
    constant, which exists only for an installation missing its own file.

    Args:
        project_root: Root of the repository the review runs in.

    Returns:
        The wait in seconds.
    """
    for candidate in (project_root / _SETTINGS_NAME, _PACKAGE_ROOT / _SETTINGS_NAME):
        found = _wait_setting_of(candidate)
        if found is not None:
            return found
    return _FALLBACK_WAIT_SECONDS


@dataclass(frozen=True)
class ReviewConfiguration:
    """Review-mode activation loaded against one reusable artifact context."""

    enabled: bool
    wait_timeout_seconds: int = _FALLBACK_WAIT_SECONDS

    def __post_init__(self) -> None:
        """Validate the typed configuration values."""
        positive_integer(self.wait_timeout_seconds, "wait timeout")

    @classmethod
    def load(
        cls,
        project_root: Path,
        *,
        review_mode_path: Path | None = None,
    ) -> ReviewConfiguration:
        """Read the review marker selected by the artifact locator."""
        root = project_root.resolve()
        default_wait = _default_wait_seconds(root)
        legacy_marker = root / _MARKER_NAME
        selected = review_mode_path.resolve() if review_mode_path is not None else None
        marker = selected if selected is not None and selected.exists() else legacy_marker
        if not marker.exists():
            return cls(enabled=False, wait_timeout_seconds=default_wait)
        if not marker.is_file():
            raise ReviewExchangeError("invalid a.review-mode: marker is not a file")
        try:
            content = marker.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ReviewExchangeError(f"invalid a.review-mode: {error}") from error
        timeout = _wait_timeout_from_marker(content, default_wait)
        return cls(enabled=True, wait_timeout_seconds=timeout)


def _wait_timeout_from_marker(content: str, default_wait: int) -> int:
    """Parse the marker's optional single positive wait override.

    Args:
        content: Exact marker text.
        default_wait: Wait to use when the marker states none.

    Returns:
        The wait in seconds.
    """
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return default_wait
    if len(lines) != 1 or not lines[0].startswith("wait_timeout_seconds="):
        raise ReviewExchangeError("invalid a.review-mode: expected one wait override")
    value = lines[0].partition("=")[2]
    if not value.isdecimal() or int(value) <= 0:
        raise ReviewExchangeError(
            "invalid a.review-mode: wait timeout must be a positive integer",
        )
    return int(value)


@dataclass(frozen=True)
class ArtifactPaths:
    """All fixed exact paths derived for one exchange identity."""

    identity: ExchangeIdentity
    project_root: Path
    transcript: Path
    request: Path
    answer: Path
    coordination: Path
    tombstone: Path
    transition_lock: Path

    @property
    def fixed_paths(self) -> tuple[Path, ...]:
        """Return the constant transcript and transient path set."""
        return (
            self.transcript,
            self.request,
            self.answer,
            self.coordination,
            self.tombstone,
            self.transition_lock,
        )


# eof
