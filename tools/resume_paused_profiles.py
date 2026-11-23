"""Typed host-profile observations and fail-closed profile policy for resume-paused.

Step 1 of v0.15.0 resume-paused defines the shared vocabulary of the read-only
host evidence adapters: verdicts, classified reasons, byte accounting, process
identity, the pinned-profile registry, caller classification and the Q21 boot
comparison. The shipped registry pins no profile: until disposable validation
records a supported host version, every pane classifies as unsupported and no
input can be justified by this module.

Fix (code review round 1, R5 and R7): ``loads_strict`` decodes host evidence
and rejects an object that repeats a key.
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
class HostProfile:
    """One validated host version with the evidence that pins it.

    ``image_sha256`` is the loaded-image digest of a Codex release; Claude
    profiles leave it ``None``. ``evidence`` names the section of the profile
    evidence document recording the validation.
    """

    host: Host
    version: str
    os_builds: frozenset[int]
    evidence: str
    image_sha256: str | None = None


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


@dataclass(frozen=True)
class BootObservation:
    """Fixed boot-process creation instant with the current time and uptime."""

    boot_created_at: datetime
    now: datetime
    uptime: timedelta


@dataclass(frozen=True)
class BootDecision:
    """History boundary, or pending when the clock moved backward since boot."""

    verdict: Verdict
    boundary: datetime | None
    reasons: tuple[Reason, ...]


def boot_boundary(observation: BootObservation, tolerance: timedelta) -> BootDecision:
    """Select history from the fixed boot instant, never from now minus uptime.

    The computed instant only detects a net backward clock movement (Q21=A): a
    computed boot earlier than the fixed one beyond ``tolerance`` stays pending.
    """
    if observation.uptime.total_seconds() < 0 or tolerance.total_seconds() < 0:
        return BootDecision(Verdict.PENDING, None, (Reason("boot-evidence-invalid"),))
    computed = observation.now - observation.uptime
    if computed < observation.boot_created_at - tolerance:
        return BootDecision(Verdict.PENDING, None, (Reason("clock-backward-beyond-tolerance"),))
    return BootDecision(Verdict.SUPPORTED, observation.boot_created_at, ())


# eof
