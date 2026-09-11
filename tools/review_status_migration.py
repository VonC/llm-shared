"""Migration-aware preflight for schema-2 review status.

Step 4 isolates the status command's one bounded mutation exception from the
ordinary read-only discovery and projection service.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from tools.review_artifact_migration import (
    MigrationState as ArtifactMigrationState,
)
from tools.review_artifact_migration import (
    ReviewArtifactMigration,
)
from tools.review_exchange_models import ReviewExchangeError
from tools.review_status_models import MigrationStatus

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_artifact_configuration import ReviewArtifactConfiguration
    from tools.review_artifact_migration import MigrationCheckResult


class _MigrationPort(Protocol):
    """Minimal placement API consumed by the status preflight."""

    def migration_check(self) -> MigrationCheckResult:
        """Return one bounded placement check."""
        ...

    def migrate(self, checked: MigrationCheckResult) -> MigrationCheckResult:
        """Migrate one fresh required layout and return its ready recheck."""
        ...


@dataclass(frozen=True)
class ReviewStatusMigrationResult:
    """Preflight status and the ready configuration authorized for projection."""

    status: MigrationStatus
    configuration: ReviewArtifactConfiguration | None

    @property
    def ready(self) -> bool:
        """Return whether ordinary projection may read the configured home."""
        return self.configuration is not None


class ReviewStatusMigrationPreflight:
    """Perform check, optional migration, and mandatory ready recheck once."""

    def __init__(
        self,
        project_root: Path,
        *,
        migration: _MigrationPort | None = None,
    ) -> None:
        """Bind one repository and an injectable bounded migration adapter."""
        self._project_root = project_root.resolve()
        self._migration = migration or ReviewArtifactMigration(
            project_root=self._project_root,
        )

    def run(self) -> ReviewStatusMigrationResult:
        """Authorize projection only for an initially or subsequently ready layout."""
        try:
            checked = self._migration.migration_check()
        except (OSError, UnicodeError, ReviewExchangeError, ValueError) as error:
            return self._blocked(".reviews", (self._diagnostic(error),))
        home = checked.configuration.relative_home
        if checked.state is ArtifactMigrationState.READY:
            return ReviewStatusMigrationResult(
                MigrationStatus.unnecessary(home),
                checked.configuration,
            )
        if checked.state is ArtifactMigrationState.BLOCKED:
            diagnostics = checked.diagnostics or ("migration check is blocked",)
            return self._blocked(home, diagnostics)

        moved_count = len(checked.moves)
        try:
            rechecked = self._migration.migrate(checked)
        except (OSError, UnicodeError, ReviewExchangeError, ValueError) as error:
            return self._blocked(home, (self._diagnostic(error),))
        if rechecked.state is not ArtifactMigrationState.READY:
            details = rechecked.diagnostics or (rechecked.state.value,)
            diagnostics = tuple(f"second check: {detail}" for detail in details)
            return self._blocked(home, diagnostics)
        return ReviewStatusMigrationResult(
            MigrationStatus.completed(home, moved_count),
            rechecked.configuration,
        )

    @staticmethod
    def _diagnostic(error: Exception) -> str:
        """Return nonempty stable text for a caught operational exception."""
        return str(error).strip() or type(error).__name__

    @staticmethod
    def _blocked(
        artifact_home: str,
        diagnostics: tuple[str, ...],
    ) -> ReviewStatusMigrationResult:
        """Return a typed failure with no configuration authorized for reads."""
        return ReviewStatusMigrationResult(
            MigrationStatus.blocked(artifact_home, diagnostics),
            None,
        )


__all__ = ["ReviewStatusMigrationPreflight", "ReviewStatusMigrationResult"]


# eof
