"""Shared strict values of resume-paused pause artifacts.

Step 2 of v0.15.0 resume-paused defines the values that the bulk reader, the
routing schema and the later receiving validator share: canonical Windows
checkout roots, prompt digests, agent ids, full pane UUIDs, offset timestamps
and single-line text. The module performs no IO. The versioned routing schema
lives in ``tools.resume_paused_routing``; ``tools.resume_paused_artifacts``
reads the files.

A checkout root compares by Windows rules: separators, case, repeated or
trailing separators and the extended-length prefix do not change its key,
while dot segments, trailing dots or spaces and reserved characters are
refused rather than guessed.
"""

# ruff: noqa: EM102, TRY003

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Final

from tools.resume_paused_profiles import Host
from tools.review_exchange_models import ReviewExchangeError, validate_local_timestamp

if TYPE_CHECKING:
    from pathlib import Path

PROMPT_NAME: Final = "a.session-resume.local.md"
RECEIPT_NAME: Final = "a.session-resume.used.local.md"
NAME_LIMIT: Final = 200
TEXT_LIMIT: Final = 1000
ROOT_LIMIT: Final = 1024
LAUNCH_ID_RE: Final = re.compile(r"[0-9a-f]{32}")
_TIMESTAMP_LIMIT: Final = 64
_AGENT_LIMIT: Final = 64
_PANE_ID_LENGTH: Final = 36
_UNC_PARTS: Final = 2
_C0_END: Final = 0x20
_C1_START: Final = 0x7F
_C1_END: Final = 0x9F
_LINE_SEPARATORS: Final = frozenset("\N{LINE SEPARATOR}\N{PARAGRAPH SEPARATOR}")
_AGENT_ID_RE: Final = re.compile(r"[a-z0-9-]+")
_UUID_RE: Final = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
_HEX64_RE: Final = re.compile(r"[0-9a-f]{64}")
_DRIVE_RE: Final = re.compile(r"[A-Za-z]:\\")
_RECOGNIZED_AGENTS: Final = {"claude": Host.CLAUDE, "chatgpt": Host.CODEX, "codex": Host.CODEX}
_FORBIDDEN_SEGMENT_CHARACTERS: Final = frozenset('<>:"|?*')


class ArtifactError(ValueError):
    """Unreadable, malformed or contradictory pause evidence for one checkout."""


class SessionRole(StrEnum):
    """Session roles a pause records and a routing target can be assigned."""

    IMPLEMENTATION = "implementation"
    REQUESTOR = "requestor"
    REVIEWER = "reviewer"
    DOCUMENTATION = "documentation"
    OTHER = "other"


def checked_text(value: object, label: str, *, limit: int = TEXT_LIMIT, empty: bool = False) -> str:
    """Return trimmed single-line text that renders unambiguously in a table cell.

    Control characters and the Unicode line and paragraph separators are
    refused: ``str.splitlines`` breaks a JSON or table line on each of them.
    """
    if not isinstance(value, str):
        raise ArtifactError(f"invalid {label}: expected a string")
    control = any(
        ord(character) < _C0_END or _C1_START <= ord(character) <= _C1_END or character in _LINE_SEPARATORS
        for character in value
    )
    if (not value and not empty) or len(value) > limit or value != value.strip() or control:
        raise ArtifactError(f"invalid {label}: expected trimmed single-line text of at most {limit} characters")
    return value


def checked_timestamp(value: object, label: str) -> str:
    """Return an ISO-8601 timestamp that carries a numeric UTC offset."""
    text = checked_text(value, label, limit=_TIMESTAMP_LIMIT)
    try:
        return validate_local_timestamp(text)
    except ReviewExchangeError as error:
        raise ArtifactError(f"invalid {label}: {error}") from error


def timestamp_instant(text: str) -> datetime:
    """Return the instant of an already validated offset timestamp."""
    return datetime.fromisoformat(text)


def agent_id(value: object, label: str) -> str:
    """Return one agent id: lowercase letters, digits and hyphens, as pauses write it."""
    text = checked_text(value, label, limit=_AGENT_LIMIT)
    if _AGENT_ID_RE.fullmatch(text) is None:
        raise ArtifactError(f"invalid {label}: expected lowercase letters, digits and hyphens")
    return text


def host_for_agent(agent: str | None) -> Host | None:
    """Return the host a recognized pausing agent id names, or ``None``."""
    return None if agent is None else _RECOGNIZED_AGENTS.get(agent)


def pane_id(value: object, label: str) -> str:
    """Return one full TUIOS pane UUID in its lowercase canonical spelling."""
    text = checked_text(value, label, limit=_PANE_ID_LENGTH).lower()
    if _UUID_RE.fullmatch(text) is None:
        raise ArtifactError(f"invalid {label}: expected a full pane UUID")
    return text


def sha256_hex(value: object, label: str) -> str:
    """Return one SHA-256 digest as 64 lowercase hexadecimal characters."""
    text = checked_text(value, label, limit=64).lower()
    if _HEX64_RE.fullmatch(text) is None:
        raise ArtifactError(f"invalid {label}: expected 64 hexadecimal characters")
    return text


def _strip_extended_prefix(text: str) -> str:
    """Drop the extended-length prefixes, keeping a UNC share's leading separators."""
    if text.startswith("\\\\?\\UNC\\"):
        return "\\\\" + text[8:]
    return text.removeprefix("\\\\?\\")


def _segments(text: str) -> list[str]:
    """Split backslash-separated segments, dropping repeated separators."""
    return [part for part in text.split("\\") if part]


def _split_root(text: str, label: str) -> tuple[str, list[str], list[str]]:
    """Return the root prefix, the segments below it and every segment to check."""
    if text.startswith("\\\\"):
        parts = _segments(text[2:])
        if len(parts) < _UNC_PARTS:
            raise ArtifactError(f"invalid {label}: incomplete UNC share")
        return "\\\\" + "\\".join(parts[:2]), parts[2:], parts
    if _DRIVE_RE.match(text) is None:
        raise ArtifactError(f"invalid {label}: expected an absolute Windows path")
    segments = _segments(text[3:])
    return text[0].upper() + ":\\", segments, segments


def _require_plain_segments(parts: list[str], label: str) -> None:
    """Reject dot segments, trailing dots or spaces, and reserved characters."""
    for part in parts:
        if part in {".", ".."} or part != part.rstrip(". ") or not _FORBIDDEN_SEGMENT_CHARACTERS.isdisjoint(part):
            raise ArtifactError(f"invalid {label}: unsupported path segment {part!r}")


@dataclass(frozen=True)
class CanonicalRoot:
    """One absolute Windows checkout path, equal across case and separator spellings."""

    key: str
    display: str = field(compare=False)

    @classmethod
    def parse(cls, value: object, label: str = "checkout root") -> CanonicalRoot:
        """Normalize separators, case and extended prefixes; reject ambiguous segments."""
        text = _strip_extended_prefix(checked_text(value, label, limit=ROOT_LIMIT).replace("/", "\\"))
        prefix, segments, checked = _split_root(text, label)
        _require_plain_segments(checked, label)
        display = "\\".join((prefix, *segments)) if prefix.startswith("\\\\") else prefix + "\\".join(segments)
        return cls(display.lower(), display)

    @classmethod
    def from_path(cls, path: Path) -> CanonicalRoot:
        """Canonicalize one filesystem path as a checkout root."""
        return cls.parse(str(path))


@dataclass(frozen=True)
class PromptDigest:
    """SHA-256 of a prompt's exact bytes, as 64 lowercase hexadecimal characters."""

    value: str

    @classmethod
    def of(cls, data: bytes) -> PromptDigest:
        """Hash exact prompt bytes."""
        return cls(hashlib.sha256(data).hexdigest())

    @classmethod
    def parse(cls, value: object, label: str = "SHA-256") -> PromptDigest:
        """Parse a recorded digest, normalizing its hexadecimal case."""
        return cls(sha256_hex(value, label))


__all__ = [
    "LAUNCH_ID_RE",
    "NAME_LIMIT",
    "PROMPT_NAME",
    "RECEIPT_NAME",
    "ROOT_LIMIT",
    "TEXT_LIMIT",
    "ArtifactError",
    "CanonicalRoot",
    "PromptDigest",
    "SessionRole",
    "agent_id",
    "checked_text",
    "checked_timestamp",
    "host_for_agent",
    "pane_id",
    "sha256_hex",
    "timestamp_instant",
]


# eof
