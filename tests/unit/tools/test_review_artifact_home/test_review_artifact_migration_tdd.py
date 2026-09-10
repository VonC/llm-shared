"""TDD contracts for bounded, journaled review-artifact migration."""

# ruff: noqa: SLF001

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import cast

import pytest

from tools import review_artifact_migration as migration_module
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import (
    MigrationMove,
    MigrationState,
    ReviewArtifactMigration,
)
from tools.review_exchange_models import ReviewExchangeError

_MIGRATED_ARTIFACT_COUNT = 2
_SECOND_MOVE_CALL = 2


def _configured(root: Path, relative: str = ".reviews") -> ReviewArtifactConfiguration:
    """Return a validated configuration without requiring a Git fixture."""
    if relative != ".reviews":
        (root / ".review-artifacts.ini").write_text(
            f"[review-artifacts]\nhome={relative}\n",
            encoding="utf-8",
        )
    return ReviewArtifactConfiguration.load(root)


def _service(root: Path, relative: str = ".reviews") -> ReviewArtifactMigration:
    """Build migration with deterministic positive ignore verification."""
    configuration = _configured(root, relative)
    return ReviewArtifactMigration(
        project_root=root,
        load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: True,
    )


def test_root_and_former_home_artifacts_merge_into_configured_home(
    tmp_path: Path,
) -> None:
    """Distinct recognized sources move together and preserve exact bytes."""
    request = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    request.write_bytes(b"request\r\n")
    former = tmp_path / ".reviews"
    former.mkdir()
    (former / ".gitignore").write_bytes(b"*\n")
    answer = former / "a.review-answer.plan.v0.11.0.topic.md"
    answer.write_bytes(b"answer\n")
    service = _service(tmp_path, "runtime/reviews")

    check = service.migration_check()
    migrated = service.migrate(check)

    assert check.state is MigrationState.MIGRATION_REQUIRED
    assert len(check.moves) == _MIGRATED_ARTIFACT_COUNT
    assert migrated.state is MigrationState.READY
    assert (tmp_path / "runtime/reviews" / request.name).read_bytes() == b"request\r\n"
    assert (tmp_path / "runtime/reviews" / answer.name).read_bytes() == b"answer\n"
    assert not request.exists()
    assert not answer.exists()
    assert service.migration_check().state is MigrationState.READY
    assert service.migrate(migrated).state is MigrationState.READY


def test_collision_or_different_duplicate_blocks_without_moving(tmp_path: Path) -> None:
    """One target collision blocks the complete transaction before mutation."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"source")
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    target = home / source.name
    target.write_bytes(b"different")
    service = _service(tmp_path)

    check = service.migration_check()

    assert check.state is MigrationState.BLOCKED
    assert "different bytes" in " ".join(check.diagnostics)
    assert source.read_bytes() == b"source"
    assert target.read_bytes() == b"different"


def test_existing_uncovered_home_blocks_without_silent_repair(tmp_path: Path) -> None:
    """An existing home with missing catch-all coverage is never repaired."""
    home = tmp_path / ".reviews"
    home.mkdir()
    service = _service(tmp_path)

    check = service.migration_check()

    assert check.state is MigrationState.BLOCKED
    assert "ignore" in " ".join(check.diagnostics)
    assert not (home / ".gitignore").exists()


def test_failed_move_rolls_back_every_completed_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An ordinary rename failure restores the complete source layout."""
    first = tmp_path / "a.review-requested.plan.v0.11.0.first.md"
    second = tmp_path / "a.review-requested.plan.v0.11.0.second.md"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    service = _service(tmp_path)
    check = service.migration_check()
    original_replace = service._replace
    calls = 0

    def fail_second(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == _SECOND_MOVE_CALL:
            message = "injected move failure"
            raise OSError(message)
        original_replace(source, target)

    monkeypatch.setattr(service, "_replace", fail_second)

    with pytest.raises(ReviewExchangeError, match="migration failed"):
        service.migrate(check)
    assert first.read_bytes() == b"first"
    assert second.read_bytes() == b"second"
    assert not (tmp_path / ".reviews" / first.name).exists()


def test_malformed_or_unsupported_journal_blocks_recovery(tmp_path: Path) -> None:
    """Recovery accepts only one strict versioned full-snapshot journal."""
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    service = _service(tmp_path)
    journal = service.journal_path
    journal.write_text("{broken", encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match="migration journal"):
        service.recover()
    journal.write_text(
        json.dumps({"version": 99, "phase": "prepared", "moves": []}),
        encoding="utf-8",
    )
    with pytest.raises(ReviewExchangeError, match="migration journal"):
        service.recover()


def test_committed_journal_recovery_finishes_duplicate_source_cleanup(
    tmp_path: Path,
) -> None:
    """A committed snapshot preserves its target and idempotently retires sources."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"same")
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    target = home / source.name
    target.write_bytes(b"same")
    service = _service(tmp_path)
    fingerprint = service._fingerprint(source)
    service.journal_path.write_text(
        json.dumps(
            {
                "version": 1,
                "phase": "committed",
                "moves": [
                    {
                        "source": source.relative_to(tmp_path).as_posix(),
                        "target": target.relative_to(tmp_path).as_posix(),
                        "fingerprint": fingerprint,
                        "duplicate": True,
                        "completed": True,
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    result = service.recover()

    assert result.state is MigrationState.READY
    assert target.read_bytes() == b"same"
    assert not source.exists()
    assert not service.journal_path.exists()


def test_recovery_restores_a_rename_before_its_completion_snapshot(
    tmp_path: Path,
) -> None:
    """Physical layout closes the crash window between rename and journal update."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"request")
    home = tmp_path / ".reviews"
    home.mkdir()
    (home / ".gitignore").write_bytes(b"*\n")
    target = home / source.name
    service = _service(tmp_path)
    fingerprint = service._fingerprint(source)
    source.replace(target)
    service.journal_path.write_text(
        json.dumps(
            {
                "version": 1,
                "phase": "moving",
                "moves": [
                    {
                        "source": source.relative_to(tmp_path).as_posix(),
                        "target": target.relative_to(tmp_path).as_posix(),
                        "fingerprint": fingerprint,
                        "duplicate": False,
                        "completed": False,
                    },
                ],
            },
        ),
        encoding="utf-8",
    )

    result = service.recover()

    assert result.state is MigrationState.MIGRATION_REQUIRED
    assert source.read_bytes() == b"request"
    assert not target.exists()


def test_each_journal_replacement_is_a_complete_transaction_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prepared, per-move, and committed journals always describe every move."""
    for slug in ("first", "second"):
        (tmp_path / f"a.review-requested.plan.v0.11.0.{slug}.md").write_bytes(
            slug.encode(),
        )
    service = _service(tmp_path)
    snapshots: list[dict[str, object]] = []
    original_write = service._write_journal

    def capture(path: Path, payload: dict[str, object]) -> None:
        snapshots.append(json.loads(json.dumps(payload)))
        original_write(path, payload)

    monkeypatch.setattr(service, "_write_journal", capture)

    service.migrate()

    assert [snapshot["phase"] for snapshot in snapshots] == [
        "prepared",
        "moving",
        "moving",
        "committed",
    ]
    assert all(
        len(cast("list[object]", snapshot["moves"])) == _MIGRATED_ARTIFACT_COUNT
        for snapshot in snapshots
    )


def test_default_ignore_checker_and_location_failures_are_bounded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The production Git port is bounded and one unreadable location is diagnostic."""
    configuration = _configured(tmp_path, "runtime/reviews")
    configuration.prepare_home()
    request = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    request.write_bytes(b"request")

    def check_ignore(
        command: list[str],
        **options: object,
    ) -> subprocess.CompletedProcess[str]:
        payload = cast("str", options["input"])
        return subprocess.CompletedProcess(command, 0, payload, "")

    def enumerate_location(location: Path) -> tuple[str, ...]:
        if location == tmp_path / ".reviews":
            message = "location denied"
            raise OSError(message)
        if not location.exists():
            return ()
        return tuple(path.name for path in location.iterdir())

    monkeypatch.setattr(migration_module.subprocess, "run", check_ignore)
    service = ReviewArtifactMigration(
        project_root=tmp_path,
        load_configuration=lambda: configuration,
        enumerate_directory=enumerate_location,
    )

    result = service.migration_check()

    assert result.state is MigrationState.BLOCKED
    assert "location denied" in " ".join(result.diagnostics)


def test_default_boundary_helpers_reject_wrong_kind_and_git_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default filesystem and Git ports fail closed at their defensive edges."""
    location = tmp_path / "not-a-directory"
    location.write_bytes(b"file")
    with pytest.raises(ReviewExchangeError, match="not a directory"):
        migration_module._enumerate_directory(location)

    def failed_git(
        command: list[str],
        **_options: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 2, "", "failure")

    monkeypatch.setattr(migration_module.subprocess, "run", failed_git)
    with pytest.raises(OSError, match=r"git check-ignore failed.*exit=2.*failure"):
        migration_module._git_ignore_checker(tmp_path, (tmp_path / "x",))


def test_damaged_candidates_and_ineffective_ignore_are_diagnostic(tmp_path: Path) -> None:
    """Non-files, unreadable files, and ineffective existing coverage fail closed."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    damaged = tmp_path / name
    damaged.mkdir()
    service = _service(tmp_path)
    result = service.migration_check()
    assert result.state is MigrationState.BLOCKED
    assert "not a regular file" in " ".join(result.diagnostics)

    damaged.rmdir()
    damaged.write_bytes(b"request")

    def unreadable(_path: Path) -> bytes:
        message = "read denied"
        raise OSError(message)

    configuration = _configured(tmp_path)
    unreadable_service = ReviewArtifactMigration(
        project_root=tmp_path,
        load_configuration=lambda: configuration,
        read_bytes=unreadable,
        ignore_checker=lambda _home, _paths: True,
    )
    result = unreadable_service.migration_check()
    assert result.state is MigrationState.BLOCKED
    assert "read denied" in " ".join(result.diagnostics)

    damaged.unlink()
    configuration.prepare_home()
    uncovered_service = ReviewArtifactMigration(
        project_root=tmp_path,
        load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: False,
    )
    result = uncovered_service.migration_check()
    assert result.state is MigrationState.BLOCKED
    assert "ineffective" in " ".join(result.diagnostics)


@pytest.mark.parametrize("second", [b"same", b"different"])
def test_planned_duplicates_are_resolved_by_exact_bytes(
    tmp_path: Path,
    second: bytes,
) -> None:
    """Two legacy sources coalesce only when their fingerprints are identical."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    (tmp_path / name).write_bytes(b"same")
    former = tmp_path / ".reviews"
    former.mkdir()
    (former / ".gitignore").write_bytes(b"*\n")
    (former / name).write_bytes(second)
    service = _service(tmp_path, "runtime/reviews")

    result = service.migration_check()

    if second == b"different":
        assert result.state is MigrationState.BLOCKED
        assert "different bytes" in " ".join(result.diagnostics)
        return
    assert result.state is MigrationState.MIGRATION_REQUIRED
    assert result.moves[1].duplicate
    service.migrate(result)
    assert (tmp_path / "runtime/reviews" / name).read_bytes() == b"same"
    assert not (former / name).exists()


def test_identical_existing_target_is_cleaned_after_commit(tmp_path: Path) -> None:
    """An exact existing target is retained while its old root copy is retired."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    source = tmp_path / name
    source.write_bytes(b"same")
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    target = configuration.home / name
    target.write_bytes(b"same")
    service = _service(tmp_path)

    result = service.migration_check()

    assert result.moves[0].duplicate
    service.migrate(result)
    assert not source.exists()
    assert target.read_bytes() == b"same"


def test_existing_target_read_failure_blocks_migration(tmp_path: Path) -> None:
    """A target that cannot be fingerprinted is never overwritten."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    source = tmp_path / name
    source.write_bytes(b"same")
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    target = configuration.home / name
    target.write_bytes(b"same")

    def read_bytes(path: Path) -> bytes:
        if path == target:
            message = "target denied"
            raise OSError(message)
        return path.read_bytes()

    service = ReviewArtifactMigration(
        project_root=tmp_path,
        load_configuration=lambda: configuration,
        read_bytes=read_bytes,
        ignore_checker=lambda _home, _paths: True,
    )

    result = service.migration_check()

    assert result.state is MigrationState.BLOCKED
    assert "cannot inspect migration target" in " ".join(result.diagnostics)


def test_blocked_and_stale_checks_cannot_start_a_transaction(tmp_path: Path) -> None:
    """Migration always refreshes preflight and rejects blocked or changed input."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    source = tmp_path / name
    source.write_bytes(b"source")
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    (configuration.home / name).write_bytes(b"different")
    service = _service(tmp_path)
    with pytest.raises(ReviewExchangeError, match="migration is blocked"):
        service.migrate()

    (configuration.home / name).unlink()
    checked = service.migration_check()
    (tmp_path / "a.review-answer.plan.v0.11.0.topic.md").write_bytes(b"answer")
    with pytest.raises(ReviewExchangeError, match="migration check is stale"):
        service.migrate(checked)


def test_new_home_ignore_failure_rolls_back_home(tmp_path: Path) -> None:
    """A newly prepared home is removed when effective ignore validation fails."""
    (tmp_path / "a.review-requested.plan.v0.11.0.topic.md").write_bytes(b"request")
    configuration = _configured(tmp_path)
    service = ReviewArtifactMigration(
        project_root=tmp_path,
        load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: False,
    )

    with pytest.raises(ReviewExchangeError, match="rolled back"):
        service.migrate()
    assert not configuration.home.exists()


def test_committed_cleanup_failure_requires_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Cleanup failure preserves the committed journal for deterministic recovery."""
    name = "a.review-requested.plan.v0.11.0.topic.md"
    source = tmp_path / name
    source.write_bytes(b"same")
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    (configuration.home / name).write_bytes(b"same")
    service = _service(tmp_path)
    original_unlink = service._unlink

    def fail_source(path: Path) -> None:
        if path == source:
            message = "cleanup denied"
            raise OSError(message)
        original_unlink(path)

    monkeypatch.setattr(service, "_unlink", fail_source)
    with pytest.raises(ReviewExchangeError, match="recovery is required"):
        service.migrate()
    assert service.journal_path.exists()
    assert service.migration_check().state is MigrationState.BLOCKED

    monkeypatch.setattr(service, "_unlink", original_unlink)
    assert service.recover().state is MigrationState.READY


def test_target_verification_failure_rolls_back_the_move(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Post-rename byte changes are detected before the transaction commits."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"request")
    service = _service(tmp_path)
    original_replace = service._replace

    def corrupt_after_move(old: Path, new: Path) -> None:
        original_replace(old, new)
        new.write_bytes(b"corrupt")

    monkeypatch.setattr(service, "_replace", corrupt_after_move)
    with pytest.raises(ReviewExchangeError, match="rolled back"):
        service.migrate()
    assert service.journal_path.exists()


def test_committed_recovery_rejects_an_invalid_target(tmp_path: Path) -> None:
    """Committed cleanup cannot proceed without its exact durable target."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"request")
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    service = _service(tmp_path)
    target = configuration.home / source.name
    fingerprint = service._fingerprint(source)
    service._write_journal(
        service.journal_path,
        service._journal_payload(
            "committed",
            (MigrationMove(source, target, fingerprint),),
            {0},
        ),
    )

    with pytest.raises(ReviewExchangeError, match="recovery failed"):
        service.recover()


def test_atomic_journal_write_cleans_a_failed_temporary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed atomic replacement removes its private temporary snapshot."""
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    service = _service(tmp_path)
    original_replace = Path.replace

    def fail_journal_replace(path: Path, target: Path) -> Path:
        if path.name.startswith(".review-artifact-migration-"):
            message = "replace denied"
            raise OSError(message)
        return original_replace(path, target)

    monkeypatch.setattr(Path, "replace", fail_journal_replace)
    with pytest.raises(OSError, match="replace denied"):
        service._write_journal(
            service.journal_path,
            {"version": 1, "phase": "prepared", "moves": []},
        )
    assert not tuple(configuration.home.glob("*.tmp"))


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"version": 1, "phase": "prepared", "moves": [], "extra": True},
        {"version": 1, "phase": "prepared", "moves": "bad"},
    ],
)
def test_journal_envelope_validation_rejects_other_shapes(
    tmp_path: Path,
    payload: object,
) -> None:
    """Only the exact versioned envelope can enter recovery."""
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    service = _service(tmp_path)
    service.journal_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ReviewExchangeError, match="migration journal"):
        service.recover()


@pytest.mark.parametrize(
    "move",
    [
        3,
        {"source": "x"},
        {
            "source": 3,
            "target": ".reviews/x",
            "fingerprint": "x",
            "duplicate": False,
            "completed": False,
        },
        {
            "source": "../outside",
            "target": ".reviews/x",
            "fingerprint": "x",
            "duplicate": False,
            "completed": False,
        },
    ],
)
def test_journal_move_validation_rejects_other_shapes(
    tmp_path: Path,
    move: object,
) -> None:
    """Malformed values and repository escapes cannot become filesystem paths."""
    configuration = _configured(tmp_path)
    configuration.prepare_home()
    service = _service(tmp_path)
    service.journal_path.write_text(
        json.dumps({"version": 1, "phase": "prepared", "moves": [move]}),
        encoding="utf-8",
    )

    with pytest.raises(ReviewExchangeError, match="migration journal"):
        service.recover()


# eof
