"""Review scope capture IO outside the fixed exchange artifact set.

Publication validates before mutation, status shares groundhog's validator,
and the capture follows coordination through completion and archival.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import scope_capture
from tools.review_exchange_models import ArchiveKind, ReviewExchangeError
from tools.review_exchange_paths import archive_path

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_models import ArtifactPaths
    from tools.review_exchange_models_coordination import CoordinationRecord
    from tools.scope_capture import ResolvedScope


def validate_scope_capture(paths: ArtifactPaths, text: str, expected_fingerprint: str) -> ResolvedScope:
    """Check a complete capture against project files and the request envelope."""
    try:
        scope = scope_capture.validate_capture(paths.project_root, text)
    except scope_capture.CaptureError as error:
        raise ReviewExchangeError(str(error)) from error
    if scope.fingerprint != expected_fingerprint:
        message = "scope capture fingerprint differs from request test_scope"
        raise ReviewExchangeError(message)
    return scope


def publish_scope_capture(paths: ArtifactPaths, text: str, expected_fingerprint: str) -> None:
    """Validate and atomically replace the core-owned capture under the caller lock."""
    scope = validate_scope_capture(paths, text, expected_fingerprint)
    try:
        scope_capture.write_capture(paths.scope, scope)
    except scope_capture.CaptureError as error:
        raise ReviewExchangeError(str(error)) from error


def remove_scope_capture(paths: ArtifactPaths) -> None:
    """Remove only the exact live capture, allowing interrupted cleanup retries."""
    paths.scope.unlink(missing_ok=True)


def archive_scope_capture(paths: ArtifactPaths, compact: str) -> Path | None:
    """Move the live capture beside other archived evidence without overwriting."""
    if not paths.scope.exists():
        return None
    destination = archive_path(paths, compact, ArchiveKind.SCOPE)
    if destination.exists():
        message = "scope capture archive already exists"
        raise ReviewExchangeError(message)
    paths.scope.rename(destination)
    return destination


def bound_scope_payload(
    paths: ArtifactPaths, record: CoordinationRecord | None,
) -> dict[str, str | None] | str:
    """Return exact validated bound identity or explicit missing evidence."""
    if record is None or record.bound_scope_fingerprint is None:
        return "missing"
    try:
        scope = validate_scope_capture(
            paths, paths.scope.read_text(encoding="utf-8"), record.bound_scope_fingerprint,
        )
    except (OSError, UnicodeError, ReviewExchangeError):
        return "missing"
    return {"scope": scope.key(), "group": scope.name or None, "fingerprint": scope.fingerprint}


# eof
