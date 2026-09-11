"""Transient journal replacement retries preserve atomic migration evidence."""

# ruff: noqa: PLR2004, SLF001

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools import review_artifact_journal as journal_module
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_artifact_migration import ReviewArtifactMigration
from tools.review_exchange_models import ReviewExchangeError


@pytest.mark.parametrize("denials", [1, 4, 5])
def test_journal_replace_retries_only_within_its_bound(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, denials: int,
) -> None:
    """Retry the same complete snapshot; exhaustion preserves the previous journal."""
    target = tmp_path / "a.review-artifact-migration.json"
    previous = b'{"phase": "previous"}\n'
    target.write_bytes(previous)
    payload: dict[str, object] = {"version": 1, "phase": "prepared", "moves": []}
    replace = Path.replace
    prepared_paths: list[Path] = []
    delays: list[float] = []

    def deny_then_replace(prepared: Path, destination: Path) -> Path:
        prepared_paths.append(prepared)
        assert destination.read_bytes() == previous
        assert json.loads(prepared.read_bytes()) == payload
        if len(prepared_paths) <= denials:
            message = "journal temporarily busy"
            raise PermissionError(message)
        return replace(prepared, destination)

    monkeypatch.setattr(Path, "replace", deny_then_replace)
    monkeypatch.setattr(journal_module.time, "sleep", delays.append)
    if denials == 5:
        with pytest.raises(PermissionError, match="journal temporarily busy"):
            journal_module.write_journal(target, payload)
        assert target.read_bytes() == previous
    else:
        journal_module.write_journal(target, payload)
        assert json.loads(target.read_bytes()) == payload
    assert len(prepared_paths) == min(denials + 1, 5)
    assert len(set(prepared_paths)) == 1
    assert delays == [0.01, 0.02, 0.04, 0.08][:min(denials, 4)]
    assert not tuple(tmp_path.glob("*.tmp"))


def test_persistent_journal_denial_rolls_back_moved_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exhausted retries restore sources and remove a newly prepared destination."""
    source = tmp_path / "a.review-requested.plan.v0.11.0.topic.md"
    source.write_bytes(b"request evidence")
    configuration = ReviewArtifactConfiguration.load(tmp_path)
    service = ReviewArtifactMigration(
        project_root=tmp_path, load_configuration=lambda: configuration,
        ignore_checker=lambda _home, _paths: True,
    )
    replace = Path.replace
    attempts: list[Path] = []
    delays: list[float] = []

    def deny_moving_snapshot(prepared: Path, target: Path) -> Path:
        if prepared.name.startswith(".review-artifact-migration-"):
            payload: dict[str, Any] = json.loads(prepared.read_bytes())
            if payload["phase"] == "moving":
                attempts.append(prepared)
                assert not source.exists()
                message = "persistent journal denial"
                raise PermissionError(message)
        return replace(prepared, target)

    monkeypatch.setattr(Path, "replace", deny_moving_snapshot)
    monkeypatch.setattr(journal_module.time, "sleep", delays.append)
    with pytest.raises(ReviewExchangeError, match=r"rolled back.*persistent journal denial"):
        service.migrate()
    assert len(attempts) == 5
    assert delays == [0.01, 0.02, 0.04, 0.08]
    assert source.read_bytes() == b"request evidence"
    assert not configuration.home.exists()
    assert not (tmp_path / "review-artifact-migration.lock").exists()


# eof
