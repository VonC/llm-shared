"""Exact path derivation and activation checks for review exchanges.

Step 1 derives the fixed artifact set from validated context, parses artifact
names back to their complete identity, and verifies all transient probes with
one effective Git-ignore call before protocol mutation. Step 5 uses NUL
delimiters so Windows text-mode newline conversion cannot alter probe paths.
"""

# ruff: noqa: EM101, EM102, S105, TRY003

from __future__ import annotations

import re
import subprocess
from typing import TYPE_CHECKING, Final

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_registry import (
    RegisteredArtifactKind,
    ReviewArtifactLocator,
    ReviewArtifactRegistry,
)
from tools.review_exchange_models import (
    ArchiveKind,
    ArtifactPaths,
    ExchangeIdentity,
    ReviewConfiguration,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
)

if TYPE_CHECKING:
    from pathlib import Path

_COMPACT_TIMESTAMP_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d{8}-\d{6}$",
)
_VERSION_PART: Final[str] = r"(?P<version>v\d+\.\d+\.\d+)"
_SLUG_PART: Final[str] = r"(?P<slug>[a-z0-9][a-z0-9_-]*)"
_TYPE_PART: Final[str] = (
    r"(?P<type_token>feature-request|issue|design-specification|plan|code)"
)
_TRANSCRIPT_RE: Final[re.Pattern[str]] = re.compile(
    rf"^review\.{_TYPE_PART}\.{_VERSION_PART}\.{_SLUG_PART}\.md$",
)
_IGNORE_PROBE_TIMESTAMP: Final[str] = "20000101-000000"


def load_review_configuration(
    project_root: Path,
    *,
    configuration: ReviewArtifactConfiguration | None = None,
) -> ReviewConfiguration:
    """Load review mode through one repository-bound artifact locator."""
    root = project_root.resolve()
    artifacts = configuration or ReviewArtifactConfiguration.load(root)
    if artifacts.project_root != root:
        raise ReviewExchangeError(
            "artifact configuration belongs to another repository",
        )
    marker = ReviewArtifactLocator(artifacts).fixed_path(
        RegisteredArtifactKind.REVIEW_MODE,
    )
    return ReviewConfiguration.load(root, review_mode_path=marker)


def derive_artifact_paths(
    project_root: Path,
    context: ReviewContext,
    *,
    configuration: ReviewArtifactConfiguration | None = None,
) -> ArtifactPaths:
    """Derive fixed paths while accepting one invocation-bound configuration."""
    root = project_root.resolve()
    artifacts = configuration or ReviewArtifactConfiguration.load(root)
    if artifacts.project_root != root:
        raise ReviewExchangeError(
            "artifact configuration belongs to another repository",
        )
    return ReviewArtifactLocator(artifacts).exchange_paths(context)


def archive_path(
    paths: ArtifactPaths,
    compact_timestamp: str,
    kind: ArchiveKind,
) -> Path:
    """Derive one exact evidence archive path for a selected artifact kind."""
    if _COMPACT_TIMESTAMP_RE.fullmatch(compact_timestamp) is None:
        raise ReviewExchangeError(
            "archive name requires compact local timestamp YYYYMMDD-HHMMSS",
        )
    configuration = ReviewArtifactConfiguration(
        paths.project_root,
        paths.request.parent,
        paths.request.parent.relative_to(paths.project_root).as_posix(),
        declared=False,
    )
    return ReviewArtifactLocator(configuration).archive_path(
        paths.identity,
        compact_timestamp,
        kind,
    )


def transient_paths_for_ignore(paths: ArtifactPaths) -> tuple[Path, ...]:
    """Return every transient kind represented by one exact ignored probe."""
    archives = tuple(
        archive_path(paths, _IGNORE_PROBE_TIMESTAMP, kind)
        for kind in ArchiveKind
    )
    return (
        paths.request,
        paths.answer,
        paths.coordination,
        paths.tombstone,
        paths.transition_lock,
        *archives,
    )


def _identity_from_match(match: re.Match[str]) -> ExchangeIdentity:
    """Build and validate an identity from a parsed artifact filename."""
    values = match.groupdict()
    type_token = values["type_token"]
    family_value = values.get("family")
    family = (
        ReviewFamily(family_value)
        if family_value is not None
        else (
            ReviewFamily.CODE
            if type_token == "code"
            else ReviewFamily.SPECIFICATION
        )
    )
    return ExchangeIdentity(
        family=family,
        type_token=type_token,
        version=values["version"],
        slug=values["slug"],
    )


def parse_transient_identity(path: Path) -> ExchangeIdentity:
    """Parse complete identity from any supported transient artifact name."""
    parsed = ReviewArtifactRegistry().parse_name(path.name)
    if parsed is not None and parsed.identity is not None:
        return parsed.identity
    raise ReviewExchangeError(f"unrecognized review transient path: {path.name}")


def parse_transcript_identity(path: Path) -> ExchangeIdentity:
    """Parse complete identity from a supported transcript filename."""
    match = _TRANSCRIPT_RE.fullmatch(path.name)
    if match is None:
        raise ReviewExchangeError(f"unrecognized review transcript path: {path.name}")
    return _identity_from_match(match)


def _run_git(
    command: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run one bounded Git query without a command shell."""
    return subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def validate_activation(project_root: Path, paths: ArtifactPaths) -> None:
    """Fail outside Git or when any derived transient is not ignored."""
    root = project_root.resolve()
    if root != paths.project_root:
        raise ReviewExchangeError("activation project root differs from derived paths")
    _require_git_repository(root)
    configuration = ReviewArtifactConfiguration.load(root)
    if configuration.home != paths.request.parent:
        raise ReviewExchangeError("activation artifact home differs from derived paths")
    created = configuration.prepare_home()
    relative = tuple(
        path.relative_to(root).as_posix()
        for path in (configuration.ignore_path, *transient_paths_for_ignore(paths))
    )
    try:
        _require_ignored_transients(root, relative)
    except ReviewExchangeError:
        if created:
            configuration.rollback_prepared_home()
        raise


def _require_git_repository(root: Path) -> None:
    """Fail when Git cannot verify the selected project root."""
    repository = _run_git(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
    )
    if repository.returncode != 0 or repository.stdout.strip() != "true":
        raise ReviewExchangeError("review mode requires a Git repository")


def _require_ignored_transients(root: Path, relative: tuple[str, ...]) -> None:
    """Submit the exact transient set through one effective ignore query."""
    input_text = "".join(f"{path}\0" for path in relative)
    ignored = _run_git(
        ["git", "check-ignore", "-z", "--stdin"],
        cwd=root,
        input_text=input_text,
    )
    if ignored.returncode not in {0, 1}:
        diagnostic = ignored.stderr.strip() or "git check-ignore failed"
        raise ReviewExchangeError(f"cannot verify transient ignore coverage: {diagnostic}")
    matched = frozenset(path for path in ignored.stdout.split("\0") if path)
    missing = tuple(path for path in relative if path not in matched)
    if missing:
        raise ReviewExchangeError(
            "review transient paths are not effectively ignored: " + ", ".join(missing),
        )


# eof
