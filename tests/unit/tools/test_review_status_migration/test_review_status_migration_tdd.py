"""Tests for bounded migration preflight before review-status projection.

Step 4 requires check, optional migration, and a ready recheck to complete
before ordinary status discovery can read exchange evidence.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import (
    MigrationCheckResult,
    MigrationMove,
    MigrationState,
)
from tools.review_exchange_models import ReviewExchangeError
from tools.review_status_migration import ReviewStatusMigrationPreflight
from tools.review_status_models import MigrationState as StatusMigrationState

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path


class _MigrationSpy:
    """Expose deterministic placement results and record preflight ordering."""

    def __init__(
        self,
        checks: Sequence[MigrationCheckResult],
        events: list[str],
        *,
        migrate_error: Exception | None = None,
    ) -> None:
        self._checks = deque(checks)
        self._events = events
        self._migrate_error = migrate_error

    def migration_check(self) -> MigrationCheckResult:
        """Return the next bounded check result."""
        self._events.append("check")
        return self._checks.popleft()

    def migrate(self, checked: MigrationCheckResult) -> MigrationCheckResult:
        """Record the validated migration and return the required recheck."""
        self._events.append("migrate")
        if self._migrate_error is not None:
            raise self._migrate_error
        assert checked.state is MigrationState.MIGRATION_REQUIRED
        return self.migration_check()


class _FailedCheck:
    """Migration port whose initial bounded check fails operationally."""

    def migration_check(self) -> MigrationCheckResult:
        """Raise the empty-message case used to verify diagnostic fallback."""
        raise ValueError

    def migrate(self, checked: MigrationCheckResult) -> MigrationCheckResult:
        """Fail if an unavailable initial check ever authorizes migration."""
        raise AssertionError(checked)


def _configuration(root: Path) -> ReviewArtifactConfiguration:
    """Return a configured nested artifact home without filesystem discovery."""
    return ReviewArtifactConfiguration(
        root.resolve(),
        (root / "runtime" / "reviews").resolve(),
        "runtime/reviews",
        declared=True,
    )


def _check(
    root: Path,
    state: MigrationState,
    *,
    moves: tuple[MigrationMove, ...] = (),
    diagnostics: tuple[str, ...] = (),
) -> MigrationCheckResult:
    """Build one complete placement result for the preflight seam."""
    configuration = _configuration(root)
    return MigrationCheckResult(
        state,
        configuration,
        (root.resolve(), configuration.home),
        moves,
        diagnostics,
        home_exists=True,
    )


def test_ready_layout_reports_unnecessary_without_migration(tmp_path: Path) -> None:
    """An initially ready layout performs exactly one bounded check."""
    events: list[str] = []
    spy = _MigrationSpy((_check(tmp_path, MigrationState.READY),), events)

    result = ReviewStatusMigrationPreflight(tmp_path, migration=spy).run()

    assert result.ready is True
    assert result.configuration == _configuration(tmp_path)
    assert result.status.state is StatusMigrationState.UNNECESSARY
    assert result.status.artifact_home == "runtime/reviews"
    assert result.status.moved_count == 0
    assert result.status.diagnostics == ()
    assert events == ["check"]


def test_required_layout_migrates_then_requires_ready_recheck(tmp_path: Path) -> None:
    """A migration is successful only after the returned second check is ready."""
    source = tmp_path / "a.review-active.code.code.v0.11.0.topic.md"
    target = tmp_path / "runtime" / "reviews" / source.name
    required = _check(
        tmp_path,
        MigrationState.MIGRATION_REQUIRED,
        moves=(MigrationMove(source, target, "digest"),),
    )
    ready = _check(tmp_path, MigrationState.READY)
    events: list[str] = []
    spy = _MigrationSpy((required, ready), events)

    result = ReviewStatusMigrationPreflight(tmp_path, migration=spy).run()

    assert result.ready is True
    assert result.status.state is StatusMigrationState.COMPLETED
    assert result.status.moved_count == 1
    assert events == ["check", "migrate", "check"]


def test_failed_initial_check_blocks_with_exception_type(tmp_path: Path) -> None:
    """An empty exception message still yields a non-empty operational diagnostic."""
    result = ReviewStatusMigrationPreflight(tmp_path, migration=_FailedCheck()).run()

    assert result.ready is False
    assert result.status.diagnostics == ("ValueError",)


@pytest.mark.parametrize(
    ("checks", "error", "diagnostic"),
    [
        ((MigrationState.BLOCKED,), None, "collision"),
        (
            (MigrationState.MIGRATION_REQUIRED,),
            ReviewExchangeError("migration failed"),
            "migration failed",
        ),
        (
            (MigrationState.MIGRATION_REQUIRED, MigrationState.BLOCKED),
            None,
            "second check",
        ),
    ],
)
def test_blocked_or_failed_preflight_returns_typed_failure(
    tmp_path: Path,
    checks: tuple[MigrationState, ...],
    error: Exception | None,
    diagnostic: str,
) -> None:
    """No blocked or incomplete placement can authorize status projection."""
    results = tuple(
        _check(
            tmp_path,
            state,
            diagnostics=("collision",) if state is MigrationState.BLOCKED else (),
            moves=(
                MigrationMove(tmp_path / "source", tmp_path / "target", "digest"),
            )
            if state is MigrationState.MIGRATION_REQUIRED
            else (),
        )
        for state in checks
    )
    events: list[str] = []
    spy = _MigrationSpy(results, events, migrate_error=error)

    result = ReviewStatusMigrationPreflight(tmp_path, migration=spy).run()

    assert result.ready is False
    assert result.configuration is None
    assert result.status.state is StatusMigrationState.BLOCKED
    assert any(diagnostic in item for item in result.status.diagnostics)


# eof
