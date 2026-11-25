"""Typed host-profile observations and fail-closed profile policy for resume-paused.

Step 1 of v0.15.0 resume-paused defines the shared vocabulary of the read-only
host evidence adapters: verdicts, classified reasons, byte accounting, process
identity, the pinned-profile registry, caller classification and the Q21 boot
comparison. The shipped registry pins no profile: until disposable validation
records a supported host version, every pane classifies as unsupported and no
input can be justified by this module.

Fix (code review round 1, R5 and R7): ``loads_strict`` decodes host evidence
and rejects an object that repeats a key.

Fix (design Q28=A follow-up): a boot decision has an explicit
``BootBoundary`` state. It is resolved only from the ``BootSemantics`` a
pinned ``HostProfile`` records as validated: a true boot, uptime that counts
sleep and hibernation, and a fixed tolerance with its basis and the clock
uncertainty it accepts. Without all of them the boundary stays unresolved with
a classified reason, whatever the clock comparison says, and bounds no
history. The shipped registry records no semantics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final, Protocol, cast

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence
    from datetime import datetime, timedelta


class Host(StrEnum):
    """Agent hosts whose panes the bulk resume workflow may address."""

    CLAUDE = "claude"
    CODEX = "codex"


class Verdict(StrEnum):
    """Outcome of one evidence question; only ``SUPPORTED`` permits a next gate."""

    SUPPORTED = "supported"
    PENDING = "pending"
    UNSUPPORTED = "unsupported"


class CallerOrigin(StrEnum):
    """Whether the launching process is a recognized agent or of unproved origin."""

    AGENT = "agent"
    UNPROVED = "unproved"


@dataclass(frozen=True)
class Reason:
    """One classified, non-secret reason with the number of records behind it."""

    code: str
    count: int = 1


@dataclass(frozen=True)
class ReadAccount:
    """Files and bytes actually read to reach a decision."""

    files: int = 0
    bytes_read: int = 0

    def plus(self, bytes_read: int) -> ReadAccount:
        """Return the account after one more complete file read."""
        return ReadAccount(self.files + 1, self.bytes_read + bytes_read)


@dataclass(frozen=True)
class ProcessIdentity:
    """A process generation: its identifier and creation time in FILETIME ticks."""

    pid: int
    created_at: int


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Build one decoded JSON object, refusing a repeated key."""
    decoded = dict(pairs)
    if len(decoded) != len(pairs):
        message = "duplicate JSON key"
        raise ValueError(message)
    return decoded


def loads_strict(text: bytes | str) -> object:
    """Decode JSON evidence; an object that repeats a key is invalid.

    Raises:
        ValueError: The text is not JSON, or an object repeats a key, which
            would let two readers see different structural values.
    """
    return json.loads(text, object_pairs_hook=_unique_object)


def as_mapping(value: object) -> dict[str, object]:
    """Return a decoded JSON object, or an empty one for any other value."""
    return cast("dict[str, object]", value) if isinstance(value, dict) else {}


def as_items(value: object) -> list[object]:
    """Return a decoded JSON array, or an empty one for any other value."""
    return cast("list[object]", value) if isinstance(value, list) else []


def as_text(value: object) -> str | None:
    """Return a decoded JSON string, or ``None`` for any other value."""
    return value if isinstance(value, str) else None


@dataclass(frozen=True)
class CommandResult:
    """Exit code and captured standard output of one injected command."""

    exit_code: int
    stdout: str


class Clock(Protocol):
    """Injected time source; tests never read the system clock."""

    def now(self) -> datetime:
        """Return the current timezone-aware instant."""
        ...


class CommandRunner(Protocol):
    """Injected argument-list process runner; no shell parsing is involved."""

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Run one command and return its exit code and standard output."""
        ...


@dataclass(frozen=True)
class BootSemantics:
    """The boot evidence one host profile records as validated (designs Q21=A, Q28=A).

    ``true_boot`` records that the boot process's creation marks a true boot,
    Windows fast startup included, and ``sleep_inclusive_uptime`` that uptime
    counts time spent in sleep and hibernation. ``tolerance`` is the fixed
    tolerance of the clock comparison, ``tolerance_basis`` what that value
    rests on and ``clock_uncertainty`` the clock movement it accepts within the
    disclosed Q21=A limit. A case recorded as not reproduced stays ``False``:
    that label is not evidence. A wider tolerance loosens the comparison; it
    never strengthens it.
    """

    true_boot: bool
    sleep_inclusive_uptime: bool
    tolerance: timedelta
    tolerance_basis: str
    clock_uncertainty: str


@dataclass(frozen=True)
class HostProfile:
    """One validated host version with the evidence that pins it.

    ``image_sha256`` is the loaded-image digest of a Codex release; Claude
    profiles leave it ``None``. ``evidence`` names the section of the profile
    evidence document recording the validation. ``boot`` holds the boot
    semantics that validation recorded (design Q28=A follow-up); without them
    no boot decision resolves.
    """

    host: Host
    version: str
    os_builds: frozenset[int]
    evidence: str
    image_sha256: str | None = None
    boot: BootSemantics | None = None


@dataclass(frozen=True)
class ProfileDecision:
    """Registry answer for one observed host, version, build and digest."""

    verdict: Verdict
    profile: HostProfile | None
    reasons: tuple[Reason, ...]


class ProfileRegistry:
    """Closed set of pinned profiles, indexed once by host and version."""

    def __init__(self, profiles: Iterable[HostProfile]) -> None:
        """Index the profiles and refuse two pins for one host version."""
        self._profiles: dict[tuple[Host, str], HostProfile] = {}
        for profile in profiles:
            key = (profile.host, profile.version)
            if key in self._profiles:
                message = f"duplicate profile for {profile.host.value} {profile.version}"
                raise ValueError(message)
            self._profiles[key] = profile

    def select(
        self, host: Host, version: str, os_build: int, image_sha256: str | None = None,
    ) -> ProfileDecision:
        """Return the pinned profile only when version, build and digest all agree."""
        profile = self._profiles.get((host, version))
        if profile is None:
            return ProfileDecision(Verdict.UNSUPPORTED, None, (Reason("profile-version-unpinned"),))
        if os_build not in profile.os_builds:
            return ProfileDecision(Verdict.UNSUPPORTED, None, (Reason("os-build-unpinned"),))
        if profile.image_sha256 != image_sha256:
            return ProfileDecision(Verdict.UNSUPPORTED, None, (Reason("image-digest-mismatch"),))
        return ProfileDecision(Verdict.SUPPORTED, profile, ())


# No host version has passed Step 1 validation: the registry stays empty.
SUPPORTED_PROFILES: Final = ProfileRegistry(())

# Residual limits every Claude activation report must disclose (Q20, Q21, Q26).
# The fifth is design Q27=B, confirmed on 2026-11-15: a local shell command
# runs before its input is recorded, so a still-running one may be missed.
DISCLOSED_LIMITS: Final = (
    "detached-foreground-or-hook-work",
    "hook-configuration-history-unavailable",
    "undetectable-backward-clock-change",
    "roots-without-records",
    "running-local-command-not-yet-recorded",
)

AGENT_ENVIRONMENT_MARKERS: Final = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CODEX_THREAD_ID")
AGENT_IMAGE_NAMES: Final = frozenset({"claude.exe", "codex.exe"})


@dataclass(frozen=True)
class CallerDecision:
    """Caller classification with the classified signals that produced it."""

    origin: CallerOrigin
    reasons: tuple[Reason, ...]


def classify_caller(environment: Mapping[str, str], ancestry: Sequence[str] | None) -> CallerDecision:
    """Reject recognized agent callers without treating missing proof as human.

    Args:
        environment: The caller's environment; only marker presence is read.
        ancestry: Image names of the caller's ancestors, or ``None`` when the
            process ancestry is unavailable.

    Returns:
        ``AGENT`` when a known marker or agent ancestor is present. Otherwise
        ``UNPROVED``: the human-only contract applies, inside or outside TUIOS.
    """
    reasons: list[Reason] = []
    markers = sum(1 for name in AGENT_ENVIRONMENT_MARKERS if environment.get(name))
    if markers:
        reasons.append(Reason("agent-environment-marker", markers))
    if ancestry is None:
        reasons.append(Reason("ancestry-unavailable"))
    else:
        ancestors = sum(1 for name in ancestry if name.casefold() in AGENT_IMAGE_NAMES)
        if ancestors:
            reasons.append(Reason("agent-ancestor", ancestors))
    agent = any(reason.code != "ancestry-unavailable" for reason in reasons)
    return CallerDecision(CallerOrigin.AGENT if agent else CallerOrigin.UNPROVED, tuple(reasons))


class BootBoundary(StrEnum):
    """How a boot decision bounds the transcript history (designs Q21=A, Q28=A).

    Only ``RESOLVED`` lets the boot instant bound ordinary work. ``UNRESOLVED``
    bounds nothing: every earlier record stays in scope. ``PENDING`` keeps
    activation pending, because the evidence is invalid or the clock moved
    backward beyond the validated tolerance.
    """

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    PENDING = "pending"


@dataclass(frozen=True)
class BootObservation:
    """Fixed boot-process creation instant with the current time and uptime."""

    boot_created_at: datetime
    now: datetime
    uptime: timedelta


@dataclass(frozen=True)
class BootDecision:
    """History boundary with its explicit state.

    Fix (design Q28=A follow-up): ``state`` replaces the former verdict, so an
    unresolved boundary is never mistaken for a resolved one. ``boundary`` is
    the fixed boot instant of a ``RESOLVED`` decision and ``None`` otherwise.
    An unresolved decision names each boot predicate no profile validated; a
    pending one names the invalid evidence or the backward clock movement.
    """

    state: BootBoundary
    boundary: datetime | None
    reasons: tuple[Reason, ...]


def _unvalidated(semantics: BootSemantics | None) -> tuple[Reason, ...]:
    """Name each boot predicate the profile does not record as validated."""
    if semantics is None:
        return (Reason("boot-semantics-unpinned"),)
    gaps = (
        (not semantics.true_boot, "true-boot-unvalidated"),
        (not semantics.sleep_inclusive_uptime, "uptime-sleep-unvalidated"),
        (not (semantics.tolerance_basis.strip() and semantics.clock_uncertainty.strip()), "tolerance-basis-unrecorded"),
    )
    return tuple(Reason(code) for missing, code in gaps if missing)


def boot_boundary(observation: BootObservation, semantics: BootSemantics | None) -> BootDecision:
    """Select history from the fixed boot instant only when a profile validated its semantics.

    Fix (design Q28=A follow-up): the boundary resolves only when the pinned
    profile records a true boot, sleep-inclusive uptime and its fixed
    tolerance with that tolerance's basis and accepted clock uncertainty.
    Otherwise it stays unresolved with a classified reason, whatever the clock
    comparison would say. With validated semantics, the computed instant only
    detects a net backward clock movement (Q21=A): a computed boot earlier than
    the fixed one beyond the tolerance stays pending. The boundary is never
    current time minus uptime.

    Args:
        observation: The fixed boot-process creation instant, current time and uptime.
        semantics: The boot semantics the pinned profile records, or ``None``
            when no profile records them.

    Returns:
        A resolved decision at the fixed boot instant, an unresolved one with
        its reasons, or a pending one for invalid evidence or a backward clock.
    """
    if observation.uptime.total_seconds() < 0 or (semantics is not None and semantics.tolerance.total_seconds() < 0):
        return BootDecision(BootBoundary.PENDING, None, (Reason("boot-evidence-invalid"),))
    unvalidated = _unvalidated(semantics)
    if semantics is None or unvalidated:
        return BootDecision(BootBoundary.UNRESOLVED, None, unvalidated)
    computed = observation.now - observation.uptime
    if computed < observation.boot_created_at - semantics.tolerance:
        return BootDecision(BootBoundary.PENDING, None, (Reason("clock-backward-beyond-tolerance"),))
    return BootDecision(BootBoundary.RESOLVED, observation.boot_created_at, ())


# eof
