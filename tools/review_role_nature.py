"""Strict role-nature snapshots, reconciliation, and atomic legacy backfill.

Step 2 keeps pure selected-role classification separate from file mutation.
Backfill renders and validates every replacement before exposing any of them.
"""

# ruff: noqa: EM101, TRY003

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from tools.llm_nature import LlmNature
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_exchange_transcript_identity import render_nature_completion_entry

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from typing import Any

_BACKFILL_TEMP_PREFIX = ".tmp-review-nature-"


@dataclass(frozen=True)
class RoleNatureSnapshot:
    """Best-known requestor and reviewer LLM natures for one occurrence."""

    requestor: LlmNature | None = None
    reviewer: LlmNature | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return the strict two-key JSON representation."""
        return {
            "requestor": self.requestor.value if self.requestor is not None else None,
            "reviewer": self.reviewer.value if self.reviewer is not None else None,
        }

    @classmethod
    def from_optional_dict(
        cls,
        data: Mapping[str, Any] | None,
    ) -> RoleNatureSnapshot:
        """Parse a strict snapshot, treating field absence as legacy evidence."""
        if data is None:
            return cls()
        if set(data) != {"requestor", "reviewer"}:
            raise ReviewExchangeError("invalid role-nature snapshot fields")
        return cls(
            requestor=cls._nature(data["requestor"]),
            reviewer=cls._nature(data["reviewer"]),
        )

    @staticmethod
    def _nature(value: object) -> LlmNature | None:
        """Parse one nullable closed-enum value."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ReviewExchangeError("invalid role-nature snapshot value")
        try:
            return LlmNature(value)
        except ValueError as error:
            raise ReviewExchangeError("invalid role-nature snapshot value") from error

    def for_role(self, role: ReviewRole) -> LlmNature | None:
        """Return the nature attributed to one protocol role."""
        if role is ReviewRole.REQUESTOR:
            return self.requestor
        if role is ReviewRole.REVIEWER:
            return self.reviewer
        raise ReviewExchangeError("human role has no LLM nature")

    def record(self, role: ReviewRole, nature: LlmNature) -> RoleNatureSnapshot:
        """Fill or improve one role without replacing known conflicting evidence."""
        current = self.for_role(role)
        if (
            current is not None
            and current not in {LlmNature.UNKNOWN, nature}
            and nature is not LlmNature.UNKNOWN
        ):
            message = f"cannot replace known {role.value} LLM nature {current.value}"
            raise ReviewExchangeError(message)
        chosen = current if nature is LlmNature.UNKNOWN and current is not None else nature
        if role is ReviewRole.REQUESTOR:
            return replace(self, requestor=chosen)
        return replace(self, reviewer=chosen)

    def merge(self, other: RoleNatureSnapshot) -> RoleNatureSnapshot:
        """Combine compatible evidence while retaining the strongest value."""
        merged = self
        for role in (ReviewRole.REQUESTOR, ReviewRole.REVIEWER):
            nature = other.for_role(role)
            if nature is not None:
                merged = merged.record(role, nature)
        return merged


@dataclass(frozen=True)
class RoleNatureEvidence:
    """One artifact's role attribution and observed nature."""

    path: Path
    authored_role: ReviewRole
    nature: LlmNature | None


@dataclass(frozen=True)
class RoleNatureReconciliation:
    """Complete stable partition for one selected role and current nature."""

    role: ReviewRole
    current_nature: LlmNature
    missing: tuple[RoleNatureEvidence, ...]
    matching: tuple[RoleNatureEvidence, ...]
    conflicts: tuple[RoleNatureEvidence, ...]

    @property
    def backfill_allowed(self) -> bool:
        """Return whether known current evidence may fill missing artifacts."""
        return self.current_nature is not LlmNature.UNKNOWN and not self.conflicts


class RoleNatureReconciler:
    """Partition selected-role evidence in one stable linear pass."""

    def reconcile(
        self,
        evidence: Sequence[RoleNatureEvidence],
        role: ReviewRole,
        current_nature: LlmNature,
    ) -> RoleNatureReconciliation:
        """Classify missing, matching, and conflicting selected-role artifacts."""
        missing: list[RoleNatureEvidence] = []
        matching: list[RoleNatureEvidence] = []
        conflicts: list[RoleNatureEvidence] = []
        for item in evidence:
            if item.authored_role is not role:
                continue
            if item.nature is None:
                missing.append(item)
            elif current_nature is LlmNature.UNKNOWN or item.nature in {current_nature, LlmNature.UNKNOWN}:
                matching.append(item)
            else:
                conflicts.append(item)
        return RoleNatureReconciliation(
            role,
            current_nature,
            tuple(missing),
            tuple(matching),
            tuple(conflicts),
        )


@dataclass(frozen=True)
class MutableRoleNatureArtifact:
    """One mutable artifact with pure snapshot rendering and validation seams."""

    evidence: RoleNatureEvidence
    snapshot: RoleNatureSnapshot
    render: Callable[[RoleNatureSnapshot], str]
    validate: Callable[[str], None]


@dataclass(frozen=True)
class RoleNatureBackfillResult:
    """Paths changed by one completed or no-op backfill attempt."""

    reconciliation: RoleNatureReconciliation
    changed_paths: tuple[Path, ...] = ()


@dataclass(frozen=True)
class RoleNatureBackfillContext:
    """Selected role, current nature, occurrence, and conflict authority."""

    role: ReviewRole
    current_nature: LlmNature
    transcript_path: Path
    exchange_occurrence: int
    override: bool = False


class RoleNatureBackfill:
    """Apply missing-only upgrades and transcript completion as one file set."""

    def apply(
        self,
        artifacts: Sequence[MutableRoleNatureArtifact],
        context: RoleNatureBackfillContext,
    ) -> RoleNatureBackfillResult:
        """Validate all content, then atomically expose missing-only replacements."""
        evidence = [artifact.evidence for artifact in artifacts]
        reconciliation = RoleNatureReconciler().reconcile(
            evidence,
            context.role,
            context.current_nature,
        )
        if context.current_nature is LlmNature.UNKNOWN or not reconciliation.missing:
            return RoleNatureBackfillResult(reconciliation)
        self._require_conflict_authority(
            reconciliation,
            override=context.override,
        )

        missing_paths = {item.path.resolve() for item in reconciliation.missing}
        rendered: list[tuple[Path, str]] = []
        for artifact in artifacts:
            if artifact.evidence.path.resolve() not in missing_paths:
                continue
            snapshot = artifact.snapshot.record(context.role, context.current_nature)
            content = artifact.render(snapshot)
            artifact.validate(content)
            rendered.append((artifact.evidence.path.resolve(), content))
        transcript = context.transcript_path.resolve()
        transcript_content = transcript.read_text(encoding="utf-8")
        completion = render_nature_completion_entry(
            context.role,
            context.exchange_occurrence,
            context.current_nature,
            tuple(path for path, _content in rendered),
        )
        marker = f"<!-- review-entry-id: {completion.entry_id} -->"
        if marker not in transcript_content:
            rendered.append((transcript, transcript_content.rstrip("\n") + completion.markdown))
        self._replace_all(rendered)
        return RoleNatureBackfillResult(
            reconciliation,
            tuple(path for path, _content in rendered),
        )

    @staticmethod
    def _require_conflict_authority(
        reconciliation: RoleNatureReconciliation,
        *,
        override: bool,
    ) -> None:
        """Reject a complete conflict set unless this attempt has Override."""
        if not reconciliation.conflicts or override:
            return
        details = ", ".join(
            f"{item.path}:{item.nature.value}"
            for item in reconciliation.conflicts
            if item.nature is not None
        )
        message = f"role-nature conflicts require Override: {details}"
        raise ReviewExchangeError(message)

    @staticmethod
    def _replace_all(rendered: Sequence[tuple[Path, str]]) -> None:
        """Prepare all replacements and restore originals after a commit failure."""
        prepared: list[tuple[Path, Path, bytes]] = []
        committed: list[tuple[Path, bytes]] = []
        try:
            for target, content in rendered:
                original = target.read_bytes()
                descriptor, name = tempfile.mkstemp(
                    prefix=_BACKFILL_TEMP_PREFIX,
                    suffix=".tmp",
                    dir=target.parent,
                )
                replacement = Path(name)
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(content.encode("utf-8"))
                    stream.flush()
                    os.fsync(stream.fileno())
                prepared.append((target, replacement, original))
            for target, replacement, original in prepared:
                replacement.replace(target)
                committed.append((target, original))
        except (OSError, UnicodeError) as error:
            for target, original in reversed(committed):
                target.write_bytes(original)
            message = f"atomic role-nature backfill failed: {error}"
            raise ReviewExchangeError(message) from error
        finally:
            for _target, replacement, _original in prepared:
                replacement.unlink(missing_ok=True)


__all__ = [
    "MutableRoleNatureArtifact",
    "RoleNatureBackfill",
    "RoleNatureBackfillContext",
    "RoleNatureBackfillResult",
    "RoleNatureEvidence",
    "RoleNatureReconciler",
    "RoleNatureReconciliation",
    "RoleNatureSnapshot",
]


# eof
