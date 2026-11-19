"""Compact resume marker, canonical assignment binding and compact result.

Step 4 of v0.14.0 resume-paused defines the consent a bulk launch delivers to
one receiving pane: the native command followed by ``--resume-paused`` and one
marker ``<launch_id>.rp1.<pane_uuid>.<role>.<binding>``. The random launch id
leads, so a host's truncated logged prefix keeps it; ``rp1`` is the version;
the pane is the full TUIOS pane UUID; the role is one of the five session role
tokens; the binding is the SHA-256 of the canonical UTF-8 JSON assignment.

The assignment, schema ``resume-paused-assignment`` version 1, holds the
checkout key, the prompt SHA-256, the receiver (host, TUIOS session, pane and
role), the resolved pair and the exact exchange with its occurrence and
selected round, or ``null`` for a single-agent pause. ``resolve_assignment``
rebuilds it deterministically from the saved routing, the receiver's pane and
role and the live exchange; a pair pane given the other pair role is a role
swap, allowed only for a saved requestor pause. The digest is a scope binding,
not encryption or an ownership capability.

``ResultLine`` is the compact non-secret outcome a receiver emits:
``resume-paused <launch_id> <outcome>[ g<generation>]``, at most 100
characters, never a token or digest. The module performs no IO.
"""

# ruff: noqa: EM101

from __future__ import annotations

import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

from tools.resume_paused_models import (
    ArtifactError,
    CanonicalRoot,
    PromptDigest,
    SessionRole,
)
from tools.resume_paused_routing import (
    NotApplicable,
    RoutingTarget,
    SavedRouting,
)

if TYPE_CHECKING:
    from tools.resume_paused_profiles import Host
    from tools.resume_paused_routing import SavedExchange

MARKER_FLAG: Final = "--resume-paused"
MARKER_VERSION: Final = "rp1"
ASSIGNMENT_SCHEMA: Final = "resume-paused-assignment"
ASSIGNMENT_VERSION: Final = 1
RESULT_PREFIX: Final = "resume-paused"
RESULT_LIMIT: Final = 100
_UUID: Final = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
_ROLE_TOKENS: Final = tuple(role.value for role in SessionRole)
_MARKER_RE: Final = re.compile(
    rf"(?P<launch>[0-9a-f]{{32}})\.{MARKER_VERSION}\.(?P<pane>{_UUID})\.(?P<role>{'|'.join(_ROLE_TOKENS)})\.(?P<binding>[0-9a-f]{{64}})",
)
_VERSION_RE: Final = re.compile(r"[0-9a-f]{32}\.(?P<version>rp\d+)\.")
MARKER_LIMIT: Final = 32 + 1 + len(MARKER_VERSION) + 1 + 36 + 1 + max(map(len, _ROLE_TOKENS)) + 1 + 64
_RESULT_RE: Final = re.compile(
    rf"{RESULT_PREFIX} (?P<launch>[0-9a-f]{{32}}) (?P<outcome>[a-z][a-z0-9-]{{0,31}})(?: g(?P<generation>[1-9][0-9]{{0,9}}))?",
)
_PAIR_ROLES: Final = frozenset({SessionRole.REQUESTOR, SessionRole.REVIEWER})


def new_launch_id() -> str:
    """Draw one fresh 128-bit launch id as 32 lowercase hexadecimal characters."""
    return secrets.token_hex(16)


@dataclass(frozen=True)
class Marker:
    """One parsed marker: launch id, receiving pane UUID, resolved role and binding."""

    launch_id: str
    pane_id: str
    role: SessionRole
    binding: str

    @classmethod
    def parse(cls, text: str) -> Marker:
        """Parse one marker strictly; another version, length or spelling is refused."""
        if len(text) > MARKER_LIMIT:
            raise ArtifactError("marker-too-long")
        match = _MARKER_RE.fullmatch(text)
        if match is None:
            version = _VERSION_RE.match(text)
            unsupported = version is not None and version["version"] != MARKER_VERSION
            raise ArtifactError("marker-version-unsupported" if unsupported else "marker-malformed")
        return cls(match["launch"], match["pane"], SessionRole(match["role"]), match["binding"])

    def render(self) -> str:
        """Return the marker text, launch id first."""
        text = f"{self.launch_id}.{MARKER_VERSION}.{self.pane_id}.{self.role.value}.{self.binding}"
        Marker.parse(text)
        return text


def marker_in_command(command: str) -> Marker:
    """Return the marker that follows the single marker flag of one typed command."""
    tokens = command.split()
    flags = [index for index, token in enumerate(tokens) if token == MARKER_FLAG]
    if len(flags) > 1:
        raise ArtifactError("marker-repeated")
    if not flags or flags[0] + 1 >= len(tokens):
        raise ArtifactError("marker-missing")
    return Marker.parse(tokens[flags[0] + 1])


@dataclass(frozen=True)
class AssignedPane:
    """One assigned pane: its agent host, TUIOS session string and full pane UUID."""

    host: Host
    session: str
    pane_id: str

    @classmethod
    def of(cls, target: RoutingTarget) -> AssignedPane:
        """Take the identity of one routed target."""
        return cls(target.host, target.session, target.pane_id)

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {"host": self.host.value, "pane_id": self.pane_id, "session": self.session}


@dataclass(frozen=True)
class LiveExchange:
    """The verified live occurrence and round that select the exact exchange."""

    occurrence: int
    round_number: int

    def __post_init__(self) -> None:
        """Refuse a non-positive occurrence or round."""
        if self.occurrence < 1 or self.round_number < 1:
            raise ArtifactError("exchange-not-observed")


@dataclass(frozen=True)
class AssignedExchange:
    """The saved exchange identity with its live occurrence and selected round."""

    saved: SavedExchange
    occurrence: int
    round_number: int

    def to_mapping(self) -> dict[str, object]:
        """Return the canonical JSON object."""
        return {
            "document": self.saved.document,
            "family": self.saved.family.value,
            "implementation_step": self.saved.implementation_step,
            "occurrence": self.occurrence,
            "round": self.round_number,
            "umbrella": self.saved.umbrella,
        }


@dataclass(frozen=True)
class Assignment:
    """The bound scope of one marked resume: checkout, prompt, receiver, pair and exchange."""

    checkout: CanonicalRoot
    prompt: PromptDigest
    receiver: AssignedPane
    role: SessionRole
    pair: tuple[AssignedPane, AssignedPane] | None
    exchange: AssignedExchange | None

    def to_mapping(self) -> dict[str, object]:
        """Return the assignment object that the binding hashes."""
        pair = None if self.pair is None else {"requestor": self.pair[0].to_mapping(), "reviewer": self.pair[1].to_mapping()}
        return {
            "checkout": self.checkout.key,
            "exchange": None if self.exchange is None else self.exchange.to_mapping(),
            "pair": pair,
            "prompt_sha256": self.prompt.value,
            "receiver": {**self.receiver.to_mapping(), "role": self.role.value},
            "schema": ASSIGNMENT_SCHEMA,
            "version": ASSIGNMENT_VERSION,
        }

    def canonical_json(self) -> bytes:
        """Serialize with sorted keys, compact separators and UTF-8 text."""
        return json.dumps(self.to_mapping(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

    def digest(self) -> str:
        """Return the binding: SHA-256 of the canonical JSON."""
        return hashlib.sha256(self.canonical_json()).hexdigest()


def _single(resumed: RoutingTarget, pane_id: str, role: SessionRole) -> AssignedPane:
    """Bind the resumed pane in its saved role only."""
    if resumed.pane_id != pane_id:
        raise ArtifactError("marker-pane-not-routed")
    if role is not resumed.role:
        raise ArtifactError("marker-role-mismatch")
    return AssignedPane.of(resumed)


def _paired(routing: SavedRouting, resumed: RoutingTarget, pane_id: str, role: SessionRole) -> tuple[AssignedPane, tuple[AssignedPane, AssignedPane]]:
    """Bind a paired pause, swapping the pair when the marker gives a pair pane the other role.

    The caller refused every unknown part, and the routing model requires both
    pair slots to be targets whenever its exchange applies.
    """
    requestor, reviewer = cast("RoutingTarget", routing.requestor), cast("RoutingTarget", routing.reviewer)
    order = (AssignedPane.of(requestor), AssignedPane.of(reviewer))
    slot = {requestor.pane_id: requestor, reviewer.pane_id: reviewer}.get(pane_id)
    if slot is None:
        return _single(resumed, pane_id, role), order
    if role not in _PAIR_ROLES:
        raise ArtifactError("marker-role-mismatch")
    if role is slot.role:
        return AssignedPane.of(slot), order
    if routing.pause.session_role is not SessionRole.REQUESTOR:
        raise ArtifactError("marker-switch-not-applicable")
    return AssignedPane.of(slot), (order[1], order[0])


def resolve_assignment(
    routing: SavedRouting, prompt: PromptDigest, pane_id: str, role: SessionRole, live: LiveExchange | None,
) -> Assignment:
    """Rebuild the assignment a marker binds from saved routing and live evidence.

    Args:
        routing: The prompt's parsed saved routing.
        prompt: The SHA-256 of the prompt's exact bytes.
        pane_id: The receiving pane UUID the marker names.
        role: The resolved role the marker names.
        live: The verified live occurrence and round of the saved exchange, or
            ``None`` when no exchange applies.

    Raises:
        ArtifactError: The routing records an unknown part, the pane is not a
            routed target, the role is not its saved role or a legal swap, or the
            live exchange is missing for a pair or present for a single agent.
    """
    resumed = routing.resumed
    if routing.unresolved or not isinstance(resumed, RoutingTarget):
        raise ArtifactError("routing-unresolved")
    if isinstance(routing.exchange, NotApplicable):
        if live is not None:
            raise ArtifactError("exchange-not-applicable")
        return Assignment(routing.pause.checkout, prompt, _single(resumed, pane_id, role), role, None, None)
    exchange = cast("SavedExchange", routing.exchange)
    if live is None:
        raise ArtifactError("exchange-not-observed")
    receiver, ordered = _paired(routing, resumed, pane_id, role)
    assigned = AssignedExchange(exchange, live.occurrence, live.round_number)
    return Assignment(routing.pause.checkout, prompt, receiver, role, ordered, assigned)


@dataclass(frozen=True)
class ResultLine:
    """The compact result one receiver emits: launch id, outcome, optional generation."""

    launch_id: str
    outcome: str
    generation: int | None = None

    @classmethod
    def parse(cls, line: str) -> ResultLine:
        """Parse one result line; any other shape or length is refused."""
        match = _RESULT_RE.fullmatch(line) if len(line) <= RESULT_LIMIT else None
        if match is None:
            raise ArtifactError("result-malformed")
        generation = match["generation"]
        return cls(match["launch"], match["outcome"], None if generation is None else int(generation))

    def render(self) -> str:
        """Return the result line after checking it against the parser's grammar."""
        suffix = "" if self.generation is None else f" g{self.generation}"
        line = f"{RESULT_PREFIX} {self.launch_id} {self.outcome}{suffix}"
        ResultLine.parse(line)
        return line


__all__ = [
    "ASSIGNMENT_SCHEMA",
    "ASSIGNMENT_VERSION",
    "MARKER_FLAG",
    "MARKER_LIMIT",
    "MARKER_VERSION",
    "RESULT_LIMIT",
    "AssignedExchange",
    "AssignedPane",
    "Assignment",
    "LiveExchange",
    "Marker",
    "ResultLine",
    "marker_in_command",
    "new_launch_id",
    "resolve_assignment",
]


# eof
