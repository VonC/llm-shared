"""Versioned saved-routing model of resume-paused pauses.

Step 2 of v0.15.0 resume-paused defines the routing JSON, schema
``resume-paused-routing`` version 1, the sole routing source of bulk launch.
Its object holds exactly these keys:

- ``schema`` and ``version``: the fixed schema name and the integer 1.
- ``pause``: ``checkout``, ``snapshot``, ``author``, ``session_role`` and
  ``pane``, the historical pause identity.
- ``observation``: ``observed_at``, ``assignment_source`` and ``evidence``.
- ``targets``: ``resumed``, ``requestor`` and ``reviewer``.
- ``exchange``: ``family``, ``document``, ``implementation_step``,
  ``umbrella``, ``occurrence`` and ``round``; live protocol state, not this
  record, selects the current round.

A target holds ``role``, ``host``, ``session``, ``pane_id``, ``label``,
``checkout``, ``agent_session_id`` and ``evidence``; the pausing pane holds
``host``, ``session``, ``pane_id`` and ``label``. A target, the pausing pane
or the exchange may instead be ``{"unknown": reason}``: an explicit unknown
that preserves the rest of the pause and leaves that part unresolved. A pair
slot or the exchange may be ``{"not_applicable": reason}``. Unrecognized keys,
wrong types, other versions and contradictions between parts are errors; the
model never guesses a missing target or exchange.
"""

# ruff: noqa: EM101, EM102, TRY003

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final, cast

from tools.resume_paused_models import (
    NAME_LIMIT,
    ROOT_LIMIT,
    ArtifactError,
    CanonicalRoot,
    SessionRole,
    agent_id,
    checked_text,
    checked_timestamp,
    pane_id,
)
from tools.resume_paused_profiles import Host
from tools.review_exchange_models import ExchangeIdentity, ReviewFamily

if TYPE_CHECKING:
    from collections.abc import Mapping

ROUTING_SCHEMA: Final = "resume-paused-routing"
ROUTING_VERSION: Final = 1
_STEP_LIMIT: Final = 32
_STEP_RE: Final = re.compile(r"[0-9A-Za-z][0-9A-Za-z.]{0,31}")
_SEGMENT_RE: Final = re.compile(r"[A-Za-z0-9._-]+")
_DOCUMENT_RE: Final = re.compile(
    r"(?P<prefix>feature-request|issue|design|plan)\.(?P<version>v\d+\.\d+\.\d+)\.(?P<slug>[a-z0-9][a-z0-9_-]*)\.md",
)
_SPECIFICATION_TOKENS: Final = {
    "feature-request": "feature-request",
    "issue": "issue",
    "design": "design-specification",
    "plan": "plan",
}
_UNKNOWN: Final = "unknown"
_NOT_APPLICABLE: Final = "not_applicable"
_ROUTING_KEYS: Final = frozenset({"schema", "version", "pause", "observation", "targets", "exchange"})
_PAUSE_KEYS: Final = frozenset({"checkout", "snapshot", "author", "session_role", "pane"})
_OBSERVATION_KEYS: Final = frozenset({"observed_at", "assignment_source", "evidence"})
_TARGETS_KEYS: Final = frozenset({"resumed", "requestor", "reviewer"})
_PANE_KEYS: Final = frozenset({"host", "session", "pane_id", "label"})
_TARGET_KEYS: Final = frozenset(
    {"role", "host", "session", "pane_id", "label", "checkout", "agent_session_id", "evidence"},
)
_EXCHANGE_KEYS: Final = frozenset(
    {"family", "document", "implementation_step", "umbrella", "occurrence", "round"},
)


def _choice[EnumType: StrEnum](enum_type: type[EnumType], value: object, label: str) -> EnumType:
    """Parse one string enumeration value with a stable diagnostic."""
    if not isinstance(value, str):
        raise ArtifactError(f"invalid {label}: expected a string")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ArtifactError(f"invalid {label}: {value}") from error


def _positive(value: object, label: str) -> int:
    """Return a positive JSON integer, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ArtifactError(f"invalid {label}: expected a positive integer")
    return value


def _exact(value: object, keys: frozenset[str], label: str) -> Mapping[str, object]:
    """Return one JSON object that holds exactly the expected keys."""
    if not isinstance(value, dict):
        raise ArtifactError(f"invalid {label}: expected an object")
    mapping = cast("dict[str, object]", value)
    unknown = sorted(set(mapping) - keys)
    missing = sorted(keys - set(mapping))
    if unknown or missing:
        raise ArtifactError(
            f"invalid {label}: unexpected {', '.join(unknown) or 'none'}; missing {', '.join(missing) or 'none'}",
        )
    return mapping


def _optional_text(value: object, label: str, *, limit: int) -> str | None:
    """Return ``None`` for JSON null, otherwise checked single-line text."""
    return None if value is None else checked_text(value, label, limit=limit)


def _relative_markdown(value: object, label: str) -> str:
    """Return a checkout-relative POSIX Markdown path without dot segments."""
    text = checked_text(value, label, limit=ROOT_LIMIT)
    segments = text.split("/")
    if not text.endswith(".md") or any(
        segment in {"", ".", ".."} or _SEGMENT_RE.fullmatch(segment) is None for segment in segments
    ):
        raise ArtifactError(f"invalid {label}: expected a checkout-relative POSIX Markdown path")
    return text


@dataclass(frozen=True)
class Unresolved:
    """A routing part recorded as unknown, with the pauser's reason."""

    reason: str


@dataclass(frozen=True)
class NotApplicable:
    """A routing part that does not apply to this pause, with its reason."""

    reason: str


def _marker(value: object, label: str, *, allow_not_applicable: bool) -> Unresolved | NotApplicable | None:
    """Return an explicit unknown or not-applicable form, or ``None`` for a full object."""
    if isinstance(value, dict) and len(cast("dict[str, object]", value)) == 1:
        key, reason = next(iter(cast("dict[str, object]", value).items()))
        if key == _UNKNOWN:
            return Unresolved(checked_text(reason, f"{label} unknown reason"))
        if key == _NOT_APPLICABLE and allow_not_applicable:
            return NotApplicable(checked_text(reason, f"{label} not-applicable reason"))
    return None


def _marker_mapping(marker: Unresolved | NotApplicable) -> dict[str, object]:
    """Render one explicit unknown or not-applicable form."""
    key = _UNKNOWN if isinstance(marker, Unresolved) else _NOT_APPLICABLE
    return {key: marker.reason}


@dataclass(frozen=True)
class PaneIdentity:
    """The historical pausing pane: its agent, TUIOS session, pane UUID and label."""

    host: str
    session: str
    pane_id: str
    label: str

    @classmethod
    def from_mapping(cls, value: object, label: str) -> PaneIdentity:
        """Parse one strict pausing-pane object."""
        data = _exact(value, _PANE_KEYS, label)
        return cls(
            agent_id(data["host"], f"{label} host"),
            checked_text(data["session"], f"{label} session", limit=NAME_LIMIT),
            pane_id(data["pane_id"], f"{label} pane id"),
            checked_text(data["label"], f"{label} label", limit=NAME_LIMIT, empty=True),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {"host": self.host, "session": self.session, "pane_id": self.pane_id, "label": self.label}


@dataclass(frozen=True)
class RoutingTarget:
    """One intended receiver: role, host, TUIOS session, full pane UUID and checkout."""

    role: SessionRole
    host: Host
    session: str
    pane_id: str
    label: str
    checkout: CanonicalRoot
    agent_session_id: str | None
    evidence: str

    @classmethod
    def from_mapping(cls, value: object, label: str) -> RoutingTarget:
        """Parse one strict full target object."""
        data = _exact(value, _TARGET_KEYS, label)
        return cls(
            _choice(SessionRole, data["role"], f"{label} role"),
            _choice(Host, data["host"], f"{label} host"),
            checked_text(data["session"], f"{label} session", limit=NAME_LIMIT),
            pane_id(data["pane_id"], f"{label} pane id"),
            checked_text(data["label"], f"{label} label", limit=NAME_LIMIT, empty=True),
            CanonicalRoot.parse(data["checkout"], f"{label} checkout"),
            _optional_text(data["agent_session_id"], f"{label} agent session id", limit=NAME_LIMIT),
            checked_text(data["evidence"], f"{label} evidence"),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {
            "role": self.role.value,
            "host": self.host.value,
            "session": self.session,
            "pane_id": self.pane_id,
            "label": self.label,
            "checkout": self.checkout.display,
            "agent_session_id": self.agent_session_id,
            "evidence": self.evidence,
        }


@dataclass(frozen=True)
class SavedExchange:
    """The exact review exchange a pair resumes; its current round comes from live state."""

    family: ReviewFamily
    document: str
    implementation_step: str | None
    umbrella: str | None
    occurrence: int
    round_number: int | None

    def __post_init__(self) -> None:
        """Reject a document, step or umbrella that cannot name one exact exchange."""
        _relative_markdown(self.document, "exchange document")
        if self.umbrella is not None:
            _relative_markdown(self.umbrella, "exchange umbrella")
        _positive(self.occurrence, "exchange occurrence")
        if self.round_number is not None:
            _positive(self.round_number, "exchange round")
        prefix = self._name()["prefix"]
        if self.family is ReviewFamily.CODE:
            step = self.implementation_step
            if prefix != "plan" or step is None or _STEP_RE.fullmatch(step) is None:
                raise ArtifactError("invalid code exchange: expected an implementation plan and step")
        elif self.implementation_step is not None:
            raise ArtifactError("invalid specification exchange: an implementation step applies to code review only")

    def _name(self) -> re.Match[str]:
        """Return the parsed reviewed-document file name."""
        match = _DOCUMENT_RE.fullmatch(self.document.rsplit("/", 1)[-1])
        if match is None:
            raise ArtifactError("invalid exchange document: expected <type>.vX.Y.Z.<slug>.md")
        return match

    def identity(self) -> ExchangeIdentity:
        """Derive the complete exchange identity from the reviewed document."""
        match = self._name()
        token = "code" if self.family is ReviewFamily.CODE else _SPECIFICATION_TOKENS[match["prefix"]]
        return ExchangeIdentity(self.family, token, match["version"], match["slug"])

    @classmethod
    def from_mapping(cls, value: object) -> SavedExchange:
        """Parse one strict exchange object."""
        data = _exact(value, _EXCHANGE_KEYS, "routing exchange")
        umbrella, round_number = data["umbrella"], data["round"]
        return cls(
            _choice(ReviewFamily, data["family"], "exchange family"),
            _relative_markdown(data["document"], "exchange document"),
            _optional_text(data["implementation_step"], "exchange implementation step", limit=_STEP_LIMIT),
            None if umbrella is None else _relative_markdown(umbrella, "exchange umbrella"),
            _positive(data["occurrence"], "exchange occurrence"),
            None if round_number is None else _positive(round_number, "exchange round"),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {
            "family": self.family.value,
            "document": self.document,
            "implementation_step": self.implementation_step,
            "umbrella": self.umbrella,
            "occurrence": self.occurrence,
            "round": self.round_number,
        }


@dataclass(frozen=True)
class PauseIdentity:
    """Historical pause identity: checkout, snapshot, author, saved role and pane."""

    checkout: CanonicalRoot
    snapshot: str
    author: str
    session_role: SessionRole
    pane: PaneIdentity | Unresolved

    @classmethod
    def from_mapping(cls, value: object) -> PauseIdentity:
        """Parse one strict pause object."""
        data = _exact(value, _PAUSE_KEYS, "routing pause")
        pane = _marker(data["pane"], "pausing pane", allow_not_applicable=False)
        return cls(
            CanonicalRoot.parse(data["checkout"], "pause checkout"),
            checked_timestamp(data["snapshot"], "pause snapshot"),
            agent_id(data["author"], "pause author"),
            _choice(SessionRole, data["session_role"], "pause session role"),
            pane if isinstance(pane, Unresolved) else PaneIdentity.from_mapping(data["pane"], "pausing pane"),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        pane = _marker_mapping(self.pane) if isinstance(self.pane, Unresolved) else self.pane.to_mapping()
        return {
            "checkout": self.checkout.display,
            "snapshot": self.snapshot,
            "author": self.author,
            "session_role": self.session_role.value,
            "pane": pane,
        }


@dataclass(frozen=True)
class RoutingObservation:
    """When and from which independent evidence the assignments were observed."""

    observed_at: str
    assignment_source: str
    evidence: str

    @classmethod
    def from_mapping(cls, value: object) -> RoutingObservation:
        """Parse one strict observation object."""
        data = _exact(value, _OBSERVATION_KEYS, "routing observation")
        return cls(
            checked_timestamp(data["observed_at"], "observation time"),
            checked_text(data["assignment_source"], "assignment source"),
            checked_text(data["evidence"], "observation evidence"),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {
            "observed_at": self.observed_at,
            "assignment_source": self.assignment_source,
            "evidence": self.evidence,
        }


type PairSlot = RoutingTarget | Unresolved | NotApplicable


def _slot(value: object, label: str) -> PairSlot:
    """Parse one pair slot: a full target, an explicit unknown, or not applicable."""
    marker = _marker(value, label, allow_not_applicable=True)
    return marker if marker is not None else RoutingTarget.from_mapping(value, label)


def _slot_mapping(slot: PairSlot | SavedExchange) -> dict[str, object]:
    """Render one slot or exchange as its canonical JSON object."""
    if isinstance(slot, Unresolved | NotApplicable):
        return _marker_mapping(slot)
    return slot.to_mapping()


def _require_pair_shape(requestor: PairSlot, reviewer: PairSlot, *, pair_absent: bool) -> None:
    """Require both pair slots to apply exactly when the exchange applies, in their roles."""
    slots_absent = [isinstance(slot, NotApplicable) for slot in (requestor, reviewer)]
    if pair_absent != all(slots_absent) or (not pair_absent and any(slots_absent)):
        raise ArtifactError("routing pair contradicts its exchange applicability")
    for slot, role in ((requestor, SessionRole.REQUESTOR), (reviewer, SessionRole.REVIEWER)):
        if isinstance(slot, RoutingTarget) and slot.role is not role:
            raise ArtifactError(f"routing {role.value} slot names a {slot.role.value} target")


def _require_consistent_targets(targets: list[RoutingTarget], checkout: CanonicalRoot) -> None:
    """Require every target in the pause checkout and one target per pane."""
    if any(target.checkout != checkout for target in targets):
        raise ArtifactError("routing target checkout contradicts the pause checkout")
    by_pane = {target.pane_id: target for target in targets}
    if any(by_pane[target.pane_id] != target for target in targets):
        raise ArtifactError("routing assigns one pane to different targets")


@dataclass(frozen=True)
class SavedRouting:
    """Pause identity, observation, intended targets and the exact exchange of one pause."""

    pause: PauseIdentity
    observation: RoutingObservation
    resumed: RoutingTarget | Unresolved
    requestor: PairSlot
    reviewer: PairSlot
    exchange: SavedExchange | Unresolved | NotApplicable

    def __post_init__(self) -> None:
        """Reject routing whose parts contradict each other."""
        pair_absent = isinstance(self.exchange, NotApplicable)
        _require_pair_shape(self.requestor, self.reviewer, pair_absent=pair_absent)
        targets = [slot for slot in (self.resumed, self.requestor, self.reviewer) if isinstance(slot, RoutingTarget)]
        _require_consistent_targets(targets, self.pause.checkout)
        if isinstance(self.resumed, RoutingTarget) and not pair_absent:
            matching = {SessionRole.REQUESTOR: self.requestor, SessionRole.REVIEWER: self.reviewer}.get(self.resumed.role)
            if matching is not None and matching != self.resumed:
                raise ArtifactError("resumed target contradicts its pair slot")

    @property
    def unresolved(self) -> tuple[str, ...]:
        """Return the reason of every target or exchange recorded as unknown."""
        named = (
            ("resumed target", self.resumed),
            ("requestor target", self.requestor),
            ("reviewer target", self.reviewer),
            ("review exchange", self.exchange),
        )
        return tuple(f"{name} unknown: {slot.reason}" for name, slot in named if isinstance(slot, Unresolved))

    @classmethod
    def from_mapping(cls, value: object) -> SavedRouting:
        """Parse one strict routing object of the supported schema version."""
        data = _exact(value, _ROUTING_KEYS, "routing")
        version = data["version"]
        if data["schema"] != ROUTING_SCHEMA or isinstance(version, bool) or version != ROUTING_VERSION:
            raise ArtifactError(f"unsupported routing schema or version: {data['schema']!r} {version!r}")
        targets = _exact(data["targets"], _TARGETS_KEYS, "routing targets")
        resumed = _marker(targets["resumed"], "resumed target", allow_not_applicable=False)
        exchange = _marker(data["exchange"], "routing exchange", allow_not_applicable=True)
        return cls(
            PauseIdentity.from_mapping(data["pause"]),
            RoutingObservation.from_mapping(data["observation"]),
            resumed if isinstance(resumed, Unresolved) else RoutingTarget.from_mapping(targets["resumed"], "resumed target"),
            _slot(targets["requestor"], "requestor target"),
            _slot(targets["reviewer"], "reviewer target"),
            exchange if exchange is not None else SavedExchange.from_mapping(data["exchange"]),
        )

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object, which parses back to an equal routing."""
        return {
            "schema": ROUTING_SCHEMA,
            "version": ROUTING_VERSION,
            "pause": self.pause.to_mapping(),
            "observation": self.observation.to_mapping(),
            "targets": {
                "resumed": _slot_mapping(self.resumed),
                "requestor": _slot_mapping(self.requestor),
                "reviewer": _slot_mapping(self.reviewer),
            },
            "exchange": _slot_mapping(self.exchange),
        }


__all__ = [
    "ROUTING_SCHEMA",
    "ROUTING_VERSION",
    "NotApplicable",
    "PairSlot",
    "PaneIdentity",
    "PauseIdentity",
    "RoutingObservation",
    "RoutingTarget",
    "SavedExchange",
    "SavedRouting",
    "Unresolved",
]


# eof
