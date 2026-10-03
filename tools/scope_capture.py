"""Independent scope values and strict captures shared across workflow tools.

Fingerprints cover normalized patterns and exact file membership. Captures
are validated from their own content, never by resolving a group again.
Canonical ordering uses linear radix buckets, including for unordered input.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Final, cast

from tools.linear_order import ordered_strings

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

_NAME: Final = re.compile(r"[a-z][a-z0-9_-]*")
_FIELDS: Final = frozenset(("kind", "name", "test_patterns", "source_patterns",
                           "test_files", "source_files", "fingerprint", "provenance"))


class ScopeKind(StrEnum):
    """The two supported scope kinds."""

    WHOLE = "whole"
    GROUP = "group"


class CaptureError(ValueError):
    """An unusable capture, with the diagnostic every caller must preserve."""

    def __init__(self, reason: str) -> None:
        """Attach the shared diagnostic prefix to a concrete failure reason."""
        super().__init__(f"bound scope unusable: {reason}")


@dataclass(frozen=True)
class ResolvedScope:
    """A complete scope resolution, including provenance separate from identity."""

    kind: ScopeKind
    name: str
    test_patterns: tuple[str, ...]
    source_patterns: tuple[str, ...]
    test_files: tuple[str, ...]
    source_files: tuple[str, ...]
    fingerprint: str
    provenance: Mapping[str, str]

    def key(self) -> str:
        """Return the proof marker's stable scope key."""
        return "whole" if self.kind is ScopeKind.WHOLE else f"group:{self.name}"

    def selector(self) -> str:
        """Return the explicit selector for a future resolution."""
        return "--whole-suite" if self.kind is ScopeKind.WHOLE else f"--group={self.name}"

    def label(self) -> str:
        """Return a human-readable scope label."""
        return "the whole suite" if self.kind is ScopeKind.WHOLE else f"group {self.name}"

    def to_json(self) -> str:
        """Serialize every capture field as UTF-8-compatible JSON."""
        return json.dumps(asdict(self), ensure_ascii=True, indent=2) + "\n"


WHOLE_SCOPE: Final = ResolvedScope(
    ScopeKind.WHOLE, "", (), (), (), (), hashlib.sha256(b"scope=whole").hexdigest(), {},
)


def scope_fingerprint(
    name: str, test_patterns: Sequence[str], source_patterns: Sequence[str],
    test_files: Sequence[str], source_files: Sequence[str],
) -> str:
    """Hash group identity, preserving pattern order and canonicalizing file order.

    Args:
        name: The validated group name.
        test_patterns: Normalized test rules in precedence order.
        source_patterns: Normalized source rules in precedence order.
        test_files: Resolved test membership.
        source_files: Resolved source membership.

    Returns:
        A SHA-256 fingerprint independent of the incoming file order.
    """
    payload = ("group", name, test_patterns, source_patterns,
               ordered_strings(test_files), ordered_strings(source_files))
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode("utf-8")).hexdigest()


def _strings(data: Mapping[str, object], field: str) -> tuple[str, ...]:
    """Read a string list from a capture, refusing coercion."""
    value = data[field]
    if not isinstance(value, list) or any(not isinstance(item, str) for item in cast("list[object]", value)):
        reason = f"invalid {field}"
        raise CaptureError(reason)
    return tuple(cast("list[str]", value))


def from_json(text: str) -> ResolvedScope:
    """Decode and verify a complete capture without consulting project files.

    Args:
        text: The JSON capture text.

    Returns:
        The validated resolution.

    Raises:
        CaptureError: For missing fields, invalid types or altered content.
    """
    try:
        raw: object = json.loads(text)
    except ValueError as error:
        reason = "invalid JSON"
        raise CaptureError(reason) from error
    if not isinstance(raw, dict) or raw.keys() != _FIELDS:
        reason = "missing or unknown capture fields"
        raise CaptureError(reason)
    data = cast("dict[str, object]", raw)
    provenance = _provenance(data["provenance"])
    if data["kind"] not in ("whole", "group") or not isinstance(data["name"], str):
        reason = "invalid kind or name"
        raise CaptureError(reason)
    if not isinstance(data["fingerprint"], str):
        reason = "invalid fingerprint"
        raise CaptureError(reason)
    scope = ResolvedScope(
        ScopeKind(cast("str", data["kind"])), data["name"],
        _strings(data, "test_patterns"), _strings(data, "source_patterns"),
        _strings(data, "test_files"), _strings(data, "source_files"),
        data["fingerprint"], provenance,
    )
    _validate_content(scope)
    return scope


def _provenance(value: object) -> dict[str, str]:
    """Require string provenance keys and values without coercion."""
    if not isinstance(value, dict) or any(
        not isinstance(key, str) or not isinstance(item, str)
        for key, item in cast("dict[object, object]", value).items()
    ):
        reason = "invalid provenance"
        raise CaptureError(reason)
    return cast("dict[str, str]", value)


def _validate_content(scope: ResolvedScope) -> None:
    """Verify canonical content before trusting its fingerprint."""
    if scope.kind is ScopeKind.WHOLE:
        if any((scope.name, scope.test_patterns, scope.source_patterns, scope.test_files, scope.source_files)):
            reason = "whole scope carries group content"
            raise CaptureError(reason)
        expected = WHOLE_SCOPE.fingerprint
    else:
        _validate_group(scope)
        expected = scope_fingerprint(scope.name, scope.test_patterns, scope.source_patterns,
                                     scope.test_files, scope.source_files)
    if scope.fingerprint != expected:
        reason = "fingerprint mismatch"
        raise CaptureError(reason)


def _validate_group(scope: ResolvedScope) -> None:
    """Check the name and each normalized membership or pattern sequence."""
    if not _NAME.fullmatch(scope.name):
        reason = "invalid group name"
        raise CaptureError(reason)
    for field in (scope.test_patterns, scope.source_patterns, scope.test_files, scope.source_files):
        if not field or any(not value or value != value.strip() or "\\" in value for value in field):
            reason = "empty or non-normalized group content"
            raise CaptureError(reason)
    for files in (scope.test_files, scope.source_files):
        _validate_files(files)


def _validate_files(files: tuple[str, ...]) -> None:
    """Require sorted unique canonical paths relative to the owning project."""
    if len(set(files)) != len(files) or files != ordered_strings(files):
        reason = "file list is not sorted and unique"
        raise CaptureError(reason)
    for name in files:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or ":" in name or str(path) != name:
            reason = f"invalid project-relative file: {name}"
            raise CaptureError(reason)


def validate_capture(root: Path, text: str) -> ResolvedScope:
    """Validate capture content and check each listed file once.

    Args:
        root: Project root owning the capture's relative paths.
        text: The JSON capture text.

    Returns:
        The exact captured resolution, without matching any patterns.

    Raises:
        CaptureError: When content or any captured file is unusable.
    """
    scope = from_json(text)
    for name in dict.fromkeys((*scope.test_files, *scope.source_files)):
        if not (root / name).is_file():
            reason = f"missing file: {name}"
            raise CaptureError(reason)
    return scope


def write_capture(path: Path, scope: ResolvedScope) -> None:
    """Publish a complete capture through an atomic side-file replace.

    Args:
        path: Destination chosen by the caller.
        scope: The resolved scope to serialize.

    Raises:
        CaptureError: When the capture cannot be written or replaced.
    """
    side = path.with_name(f"{path.name}.tmp")
    try:
        side.write_text(scope.to_json(), encoding="utf-8")
        side.replace(path)
    except OSError as error:
        reason = f"cannot write capture: {error}"
        raise CaptureError(reason) from error
    finally:
        with contextlib.suppress(OSError):
            side.unlink(missing_ok=True)


# eof
