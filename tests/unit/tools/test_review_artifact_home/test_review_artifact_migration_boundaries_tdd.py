"""Small physical-state boundary contracts for artifact migration."""

# ruff: noqa: SLF001

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import MigrationMove, ReviewArtifactMigration
from tools.review_exchange_models import ReviewExchangeError
from tools.review_status_migration import ReviewStatusMigrationPreflight

if TYPE_CHECKING:
    from pathlib import Path


def _service(root: Path) -> ReviewArtifactMigration:
    """Build migration with deterministic positive ignore verification."""
    configuration = ReviewArtifactConfiguration.load(root)
    return ReviewArtifactMigration(
        project_root=root,
        load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: True,
    )


def test_rollback_handles_duplicates_noops_and_ambiguous_paths(tmp_path: Path) -> None:
    """Rollback ignores duplicate/no-op entries and rejects ambiguous physical state."""
    service = _service(tmp_path)
    journal = tmp_path / "journal"
    journal.write_bytes(b"journal")
    source = tmp_path / "source"
    target = tmp_path / "target"
    duplicate = MigrationMove(source, target, "unused", duplicate=True)
    service._rollback((duplicate,), journal)
    assert not journal.exists()

    journal.write_bytes(b"journal")
    service._rollback((), journal)
    assert not journal.exists()

    source.write_bytes(b"source")
    target.write_bytes(b"target")
    ambiguous = MigrationMove(source, target, service._fingerprint(source))
    with pytest.raises(OSError, match="ambiguous"):
        service._rollback((ambiguous,), journal)


def test_existing_migration_lock_blocks_a_second_writer(tmp_path: Path) -> None:
    """Exclusive repository locking rejects concurrent migration writers."""
    (tmp_path / "a.review-requested.plan.v0.11.0.topic.md").write_bytes(b"request")
    lock = tmp_path / "review-artifact-migration.lock"
    lock.write_bytes(b"locked")

    with pytest.raises(ReviewExchangeError, match="already running"):
        _service(tmp_path).migrate()


@pytest.mark.parametrize("existing_home", [False, True])
@pytest.mark.parametrize("stderr", ["fatal: cannot read Git configuration", ""])
def test_git_ignore_failure_reaches_status_without_losing_its_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, existing_home: bool, stderr: str,
) -> None:
    """Git failures stay diagnostic and preserve sources during preflight or rollback."""
    configuration = ReviewArtifactConfiguration.load(tmp_path)
    if existing_home:
        configuration.prepare_home()
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"original request")
    service = ReviewArtifactMigration(project_root=tmp_path, load_configuration=lambda: configuration)

    def failed_git(command: list[str], **_options: object) -> subprocess.CompletedProcess[str]:
        assert command == ["git", "check-ignore", "-z", "--stdin"]
        return subprocess.CompletedProcess(command, 128, "", stderr)

    monkeypatch.setattr(subprocess, "run", failed_git)
    result = ReviewStatusMigrationPreflight(tmp_path, migration=service).run()
    assert not result.ready
    diagnostic = " ".join(result.status.diagnostics)
    assert "git check-ignore failed (exit=128)" in diagnostic
    assert stderr in diagnostic
    assert "ignore coverage is ineffective" not in diagnostic
    assert ("rolled back" in diagnostic) is not existing_home
    assert source.read_bytes() == b"original request"
    assert configuration.home.exists() is existing_home


# eof
