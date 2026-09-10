"""Closed registry and locator for review runtime artifact names.

Step 1 replaces broad root-prefix discovery with explicit kinds, reversible
identity parsing, role attribution, and one locator that keeps transcripts in
documentation while placing every transient below the configured home.
"""

# ruff: noqa: EM101, EM102, S105, TC003, TRY003

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import (
    ArchiveKind,
    ArtifactPaths,
    ExchangeIdentity,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)

if TYPE_CHECKING:
    from tools.review_artifact_configuration import ReviewArtifactConfiguration
    from tools.review_exchange_models import ReviewContext

_VERSION: Final = r"(?P<version>v\d+\.\d+\.\d+)"
_SLUG: Final = r"(?P<slug>[a-z0-9][a-z0-9_-]*)"
_TYPE: Final = r"(?P<type_token>feature-request|issue|design-specification|plan|code)"
_FAMILY: Final = r"(?P<family>specification|code)"
_STEP: Final = r"[A-Za-z0-9][A-Za-z0-9._-]*"
_REQUEST_RE: Final = re.compile(rf"^a\.review-requested\.{_TYPE}\.{_VERSION}\.{_SLUG}\.md$")
_ANSWER_RE: Final = re.compile(rf"^a\.review-answer\.{_TYPE}\.{_VERSION}\.{_SLUG}\.md$")
_COORDINATION_RE: Final = re.compile(rf"^a\.review-active\.{_FAMILY}\.{_TYPE}\.{_VERSION}\.{_SLUG}\.md$")
_TOMBSTONE_RE: Final = re.compile(rf"^a\.review-consumed\.{_FAMILY}\.{_TYPE}\.{_VERSION}\.{_SLUG}\.md$")
_LOCK_RE: Final = re.compile(rf"^a\.review-lock\.{_FAMILY}\.{_TYPE}\.{_VERSION}\.{_SLUG}\.lock$")
_ARCHIVE_RE: Final = re.compile(
    rf"^a\.review-archive\.{_FAMILY}\.{_TYPE}\.{_VERSION}\.{_SLUG}\."
    r"\d{8}-\d{6}\.(?P<archive_kind>request|answer|consumed|coordination)\.md$",
)
_GUIDANCE_RE: Final = re.compile(r"^a\.review-guidance\.[a-z0-9][a-z0-9_-]*\.md$")
_RETAINED_RE: Final = re.compile(
    rf"^a\.code-review-evidence\.{_VERSION}\.{_SLUG}\.step-{_STEP}\.json$",
)


class RegisteredArtifactKind(StrEnum):
    """Protocol-owned runtime artifact kinds accepted by migration."""

    REQUEST = "request"
    ANSWER = "answer"
    COORDINATION = "coordination"
    TOMBSTONE = "tombstone"
    TRANSITION_LOCK = "transition-lock"
    ARCHIVE = "archive"
    REVIEW_MODE = "review-mode"
    RETAINED_MANIFEST = "retained-manifest"
    REVIEW_GUIDANCE = "review-guidance"
    QUESTION_STATE = "question-state"
    MIGRATION_JOURNAL = "migration-journal"


@dataclass(frozen=True)
class RegisteredArtifact:
    """One recognized filename with optional identity and role attribution."""

    kind: RegisteredArtifactKind
    name: str
    identity: ExchangeIdentity | None
    authored_role: ReviewRole | None
    carries_role_nature: bool


def _identity(match: re.Match[str]) -> ExchangeIdentity:
    """Build one validated identity from a registered filename match."""
    values = match.groupdict()
    family_value = values.get("family")
    type_token = values["type_token"]
    family = (
        ReviewFamily(family_value)
        if family_value is not None
        else ReviewFamily.CODE if type_token == "code" else ReviewFamily.SPECIFICATION
    )
    return ExchangeIdentity(family, type_token, values["version"], values["slug"])


class ReviewArtifactRegistry:
    """Render and parse only the closed set of protocol runtime names."""

    _QUESTION_NAMES: Final = frozenset(
        {
            "a.reviewer-assessment.md",
            "a.question-verdicts.md",
            "a.writer-instructions.md",
            "a.requested-changes.md",
        },
    )

    def name_for(
        self,
        kind: RegisteredArtifactKind,
        identity: ExchangeIdentity,
    ) -> str:
        """Render one fixed exchange artifact name from complete identity."""
        suffix = f"{identity.type_token}.{identity.version}.{identity.slug}"
        family_suffix = f"{identity.family.value}.{suffix}"
        names = {
            RegisteredArtifactKind.REQUEST: f"a.review-requested.{suffix}.md",
            RegisteredArtifactKind.ANSWER: f"a.review-answer.{suffix}.md",
            RegisteredArtifactKind.COORDINATION: f"a.review-active.{family_suffix}.md",
            RegisteredArtifactKind.TOMBSTONE: f"a.review-consumed.{family_suffix}.md",
            RegisteredArtifactKind.TRANSITION_LOCK: f"a.review-lock.{family_suffix}.lock",
        }
        try:
            return names[kind]
        except KeyError as error:
            raise ReviewExchangeError(f"artifact kind has no identity name: {kind}") from error

    def parse_name(self, name: str) -> RegisteredArtifact | None:
        """Return registered metadata or reject an unrelated filename with None."""
        patterns = (
            (_REQUEST_RE, RegisteredArtifactKind.REQUEST, ReviewRole.REQUESTOR, True),
            (_ANSWER_RE, RegisteredArtifactKind.ANSWER, ReviewRole.REVIEWER, True),
            (_COORDINATION_RE, RegisteredArtifactKind.COORDINATION, None, True),
            (_TOMBSTONE_RE, RegisteredArtifactKind.TOMBSTONE, ReviewRole.REVIEWER, True),
            (_LOCK_RE, RegisteredArtifactKind.TRANSITION_LOCK, None, False),
            (_ARCHIVE_RE, RegisteredArtifactKind.ARCHIVE, None, True),
        )
        for pattern, kind, role, carries_nature in patterns:
            match = pattern.fullmatch(name)
            if match is not None:
                return RegisteredArtifact(kind, name, _identity(match), role, carries_nature)
        fixed = {
            "a.review-mode": (RegisteredArtifactKind.REVIEW_MODE, None),
            "a.review-artifact-migration.json": (
                RegisteredArtifactKind.MIGRATION_JOURNAL,
                None,
            ),
        }
        if name in fixed:
            kind, role = fixed[name]
            return RegisteredArtifact(
                kind,
                name,
                None,
                role,
                carries_role_nature=False,
            )
        if name in self._QUESTION_NAMES:
            return RegisteredArtifact(
                RegisteredArtifactKind.QUESTION_STATE,
                name,
                None,
                ReviewRole.REVIEWER,
                carries_role_nature=False,
            )
        retained = _RETAINED_RE.fullmatch(name)
        if retained is not None:
            return RegisteredArtifact(
                RegisteredArtifactKind.RETAINED_MANIFEST,
                name,
                ExchangeIdentity(
                    ReviewFamily.CODE,
                    "code",
                    retained.group("version"),
                    retained.group("slug"),
                ),
                ReviewRole.REVIEWER,
                carries_role_nature=True,
            )
        if _GUIDANCE_RE.fullmatch(name) is not None:
            return RegisteredArtifact(
                RegisteredArtifactKind.REVIEW_GUIDANCE,
                name,
                None,
                ReviewRole.HUMAN,
                carries_role_nature=False,
            )
        return None

    def archive_name(
        self,
        identity: ExchangeIdentity,
        compact_timestamp: str,
        kind: ArchiveKind,
    ) -> str:
        """Render one registered archive name from validated components."""
        name = (
            f"a.review-archive.{identity.family.value}.{identity.type_token}."
            f"{identity.version}.{identity.slug}.{compact_timestamp}.{kind.value}.md"
        )
        parsed = self.parse_name(name)
        if parsed is None or parsed.kind is not RegisteredArtifactKind.ARCHIVE:
            raise ReviewExchangeError("invalid registered review archive name")
        return name

    def retained_manifest_name(self, version: str, slug: str, step: str) -> str:
        """Render one registered retained-manifest name."""
        name = f"a.code-review-evidence.{version}.{slug}.step-{step}.json"
        parsed = self.parse_name(name)
        if parsed is None or parsed.kind is not RegisteredArtifactKind.RETAINED_MANIFEST:
            raise ReviewExchangeError("invalid registered retained-manifest name")
        return name

    @staticmethod
    def fixed_name(kind: RegisteredArtifactKind) -> str:
        """Render one unique non-identity runtime name."""
        names = {
            RegisteredArtifactKind.REVIEW_MODE: "a.review-mode",
            RegisteredArtifactKind.MIGRATION_JOURNAL: (
                "a.review-artifact-migration.json"
            ),
        }
        try:
            return names[kind]
        except KeyError as error:
            raise ReviewExchangeError("artifact kind has no unique fixed name") from error


class ReviewArtifactLocator:
    """Derive all runtime paths from one loaded artifact-home configuration."""

    def __init__(
        self,
        configuration: ReviewArtifactConfiguration,
        registry: ReviewArtifactRegistry | None = None,
    ) -> None:
        """Bind one invocation to a validated home and closed registry."""
        self.configuration = configuration
        self.registry = registry or ReviewArtifactRegistry()

    def exchange_paths(self, context: ReviewContext) -> ArtifactPaths:
        """Keep transcript history beside the document and transients in home."""
        root = self.configuration.project_root
        try:
            context.document_path.relative_to(root)
        except ValueError as error:
            raise ReviewExchangeError(
                f"reviewed document is outside project root: {context.document_path}",
            ) from error
        identity = context.identity
        transcript = context.document_path.parent / (
            f"review.{identity.type_token}.{identity.version}.{identity.slug}.md"
        )
        home = self.configuration.home
        return ArtifactPaths(
            identity=identity,
            project_root=root,
            transcript=transcript,
            request=home / self.registry.name_for(RegisteredArtifactKind.REQUEST, identity),
            answer=home / self.registry.name_for(RegisteredArtifactKind.ANSWER, identity),
            coordination=home / self.registry.name_for(
                RegisteredArtifactKind.COORDINATION,
                identity,
            ),
            tombstone=home / self.registry.name_for(RegisteredArtifactKind.TOMBSTONE, identity),
            transition_lock=home / self.registry.name_for(
                RegisteredArtifactKind.TRANSITION_LOCK,
                identity,
            ),
        )

    def archive_path(
        self,
        identity: ExchangeIdentity,
        compact_timestamp: str,
        kind: ArchiveKind,
    ) -> Path:
        """Locate one registered archive below the bound artifact home."""
        return self.configuration.home / self.registry.archive_name(
            identity,
            compact_timestamp,
            kind,
        )

    def retained_manifest_path(self, version: str, slug: str, step: str) -> Path:
        """Locate one registered retained manifest below the bound home."""
        return self.configuration.home / self.registry.retained_manifest_name(
            version,
            slug,
            step,
        )

    def fixed_path(self, kind: RegisteredArtifactKind) -> Path:
        """Locate one unique non-identity runtime artifact below the bound home."""
        return self.configuration.home / self.registry.fixed_name(kind)


__all__ = [
    "RegisteredArtifact",
    "RegisteredArtifactKind",
    "ReviewArtifactLocator",
    "ReviewArtifactRegistry",
]


# eof
