"""Strict performance gates for review migration and global reviewer waiting.

Step 0 added these contracts before the production services existed. Step 1
activated the migration gates when the artifact locator and migration service
landed. Step 5 removes the wait xfails when the notification-backed global
reviewer wait lands. The spies assert bounded calls as well as elapsed time so later code
cannot hide recursive discovery, full status projection, or busy polling behind
otherwise correct results.
"""

from __future__ import annotations

import importlib
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from pathlib import Path

MIGRATION_TIMEOUT_SECONDS: Final = 1
WAIT_TIMEOUT_SECONDS: Final = 1
SYNTHETIC_CANDIDATE_COUNT: Final = 400
MIGRATION_ELAPSED_BOUND_SECONDS: Final = 0.25
WAIT_ELAPSED_BOUND_SECONDS: Final = 0.25
QUIET_INTERVAL_COUNT: Final = 3
QUIET_RESCAN_COUNT: Final = 4
NOTIFICATION_RESCAN_COUNT: Final = 2
FALLBACK_WAIT_COUNT: Final = 2
FALLBACK_RESCAN_COUNT: Final = 3
STATUS_PROJECTION_ERROR: Final = "migration_check must not project review status"


def _path_list() -> list[Path]:
    """Return one typed empty path list for the migration spy."""
    return []


@dataclass
class MigrationSpies:
    """Count placement reads, candidate parses, and forbidden status calls."""

    project_root: Path
    configured_home: Path
    candidates_per_location: int = 0
    configuration_reads: int = 0
    directory_reads: list[Path] = field(default_factory=_path_list)
    candidate_parses: int = 0
    status_projections: int = 0

    def load_configuration(self) -> Path:
        """Return one configured home and count the declaration read."""
        self.configuration_reads += 1
        return self.configured_home

    def enumerate_directory(self, location: Path) -> tuple[str, ...]:
        """Return deterministic registered-looking names for one flat read."""
        self.directory_reads.append(location)
        prefix = location.name or "root"
        return tuple(
            f"a.review-requested.plan.v0.11.0.{prefix}-{index}.md"
            for index in range(self.candidates_per_location)
        )

    def parse_candidate(self, name: str) -> str:
        """Count one bounded parse and return the recognized candidate name."""
        self.candidate_parses += 1
        return name

    def project_status(self) -> None:
        """Record the full status projection that migration check forbids."""
        self.status_projections += 1
        raise AssertionError(STATUS_PROJECTION_ERROR)


@dataclass
class WaitSpies:
    """Count authoritative rescans, notification hints, and fallback polls."""

    request_on_rescan: int | None = None
    notify_on_wait: int | None = None
    rescans: int = 0
    notification_waits: int = 0
    fallback_polls: int = 0
    now: float = 0.0

    def rescan_candidates(self) -> tuple[str, ...]:
        """Return one request only on the configured authoritative rescan."""
        self.rescans += 1
        if self.request_on_rescan == self.rescans:
            return ("a.review-requested.plan.v0.11.0.future.md",)
        return ()

    def wait_for_notification(self, timeout_seconds: float) -> bool:
        """Advance synthetic time and optionally report a directory hint."""
        self.notification_waits += 1
        self.now += timeout_seconds
        return self.notify_on_wait == self.notification_waits

    def fallback_poll(self) -> None:
        """Record one bounded polling fallback."""
        self.fallback_polls += 1

    def monotonic(self) -> float:
        """Return deterministic synthetic monotonic time."""
        return self.now


def _migration_check(spies: MigrationSpies) -> object:
    """Call the Step 1 migration seam with explicit bounded-IO ports."""
    module = importlib.import_module("tools.review_artifact_migration")
    service = module.ReviewArtifactMigration(
        project_root=spies.project_root,
        load_configuration=spies.load_configuration,
        enumerate_directory=spies.enumerate_directory,
        parse_candidate=spies.parse_candidate,
        project_status=spies.project_status,
    )
    return service.migration_check()


def _global_wait(
    spies: WaitSpies,
    *,
    quiet_intervals: int = QUIET_INTERVAL_COUNT,
) -> object:
    """Call the Step 5 wait seam with deterministic notification and poll ports."""
    module = importlib.import_module("tools.review_resume_wait")
    waiter = module.GlobalReviewerWait(
        rescan_candidates=spies.rescan_candidates,
        wait_for_notification=spies.wait_for_notification,
        fallback_poll=spies.fallback_poll,
        monotonic_clock=spies.monotonic,
        poll_interval_seconds=1.0,
    )
    return waiter.wait(max_quiet_intervals=quiet_intervals)


class TestMigrationCheckPerformance:
    """Guard the Step 1 placement preflight against hidden projection and scans."""

    @pytest.mark.timeout(MIGRATION_TIMEOUT_SECONDS)
    def test_migration_check_reads_only_three_flat_locations(
        self,
        tmp_path: Path,
    ) -> None:
        """Placement reads root, default, and configured homes exactly once."""
        spies = MigrationSpies(tmp_path, tmp_path / "configured")

        _migration_check(spies)

        assert spies.configuration_reads == 1
        assert spies.directory_reads == [
            tmp_path,
            tmp_path / ".reviews",
            tmp_path / "configured",
        ]

    @pytest.mark.timeout(MIGRATION_TIMEOUT_SECONDS)
    def test_migration_check_parses_candidates_once_in_linear_time(
        self,
        tmp_path: Path,
    ) -> None:
        """Candidate work is one pass over three deterministic flat listings."""
        spies = MigrationSpies(
            tmp_path,
            tmp_path / "configured",
            candidates_per_location=SYNTHETIC_CANDIDATE_COUNT,
        )
        started = time.perf_counter()

        _migration_check(spies)

        elapsed = time.perf_counter() - started
        assert spies.candidate_parses == 3 * SYNTHETIC_CANDIDATE_COUNT
        assert elapsed < MIGRATION_ELAPSED_BOUND_SECONDS

    @pytest.mark.timeout(MIGRATION_TIMEOUT_SECONDS)
    def test_migration_check_never_projects_full_status(self, tmp_path: Path) -> None:
        """The fast placement check never enters the ordinary status projector."""
        spies = MigrationSpies(tmp_path, tmp_path / "configured")

        _migration_check(spies)

        assert spies.status_projections == 0


class TestGlobalReviewerWaitPerformance:
    """Guard the Step 5 global wait against busy loops and event-only truth."""

    @pytest.mark.timeout(WAIT_TIMEOUT_SECONDS)
    def test_quiet_wait_uses_one_rescan_and_poll_per_interval(self) -> None:
        """A quiet interval performs bounded work instead of busy-looping."""
        spies = WaitSpies()
        started = time.perf_counter()

        _global_wait(spies, quiet_intervals=QUIET_INTERVAL_COUNT)

        elapsed = time.perf_counter() - started
        assert spies.rescans == QUIET_RESCAN_COUNT
        assert spies.notification_waits == QUIET_INTERVAL_COUNT
        assert spies.fallback_polls == QUIET_INTERVAL_COUNT
        assert elapsed < WAIT_ELAPSED_BOUND_SECONDS

    @pytest.mark.timeout(WAIT_TIMEOUT_SECONDS)
    def test_notification_hint_wakes_into_authoritative_rescan(self) -> None:
        """A native event marks the wait dirty but a rescan finds the request."""
        spies = WaitSpies(request_on_rescan=2, notify_on_wait=1)

        result = _global_wait(spies)

        assert result is not None
        assert spies.notification_waits == 1
        assert spies.rescans == NOTIFICATION_RESCAN_COUNT
        assert spies.fallback_polls == 0

    @pytest.mark.timeout(WAIT_TIMEOUT_SECONDS)
    def test_polling_fallback_finds_request_without_notification(self) -> None:
        """A missed native event still reaches a complete candidate rescan."""
        spies = WaitSpies(request_on_rescan=3)

        result = _global_wait(spies)

        assert result is not None
        assert spies.notification_waits == FALLBACK_WAIT_COUNT
        assert spies.fallback_polls == FALLBACK_WAIT_COUNT
        assert spies.rescans == FALLBACK_RESCAN_COUNT


# eof
