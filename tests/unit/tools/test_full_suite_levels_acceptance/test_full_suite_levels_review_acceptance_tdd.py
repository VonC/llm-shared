"""Prove publication and drift while reusing immutable artifact/path observations."""

from __future__ import annotations

import json
from functools import cache
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.review_exchange_test_support import common_arguments
from tools import prompt_workflow
from tools import review_exchange_cli as exchange_cli
from tools.groundhog import snapshot
from tools.groundhog.groups import resolve_group
from tools.groundhog.levels import FullLevel
from tools.groundhog.project_settings import Settings
from tools.scope_capture import validate_capture

if TYPE_CHECKING:
    from collections.abc import Callable

    from tests.unit.tools.test_full_suite_levels_acceptance.conftest import Effort


@pytest.fixture
def published_capture(
    effort: Effort, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
    stable_review_inputs: Callable[[], None],
) -> tuple[Effort, str]:
    """Start at a persisted proof boundary, then exercise real publication."""
    del stable_review_inputs  # Artifact declaration and symlink targets stay fixed.
    # Drift changes group contents, not inventory or pytest/coverage settings.
    # Group parsing, content digests and capture validation remain uncached.
    monkeypatch.setattr(snapshot, "source_files", cache(snapshot.source_files))
    monkeypatch.setattr(Settings, "load", cache(Settings.load))
    scope = resolve_group(effort.root, "sentinel", snapshot.source_files(effort.root))
    snapshot.save_proof(effort.root, scope.key(), scope.fingerprint,
                        snapshot.source_digest(effort.root), FullLevel.SPEED)
    assert effort.render() == 0
    fingerprint = _assert_grouped_request(effort)
    assert effort.publish() == 0
    capture = _published_scope(effort, capsys, fingerprint)
    return effort, capture


def test_speed_walk_produces_renderable_group_proof(
    effort: Effort, monkeypatch: pytest.MonkeyPatch, stable_review_inputs: Callable[[], None],
) -> None:
    """The producer independently establishes the proof consumed by publication."""
    del stable_review_inputs  # Keep proof, SQLite reporting and rendering live.
    # Only ignored evidence changes in this journey. Share immutable source
    # inventory and settings observations; retain real proof production, digest
    # checks, persisted SQLite coverage, and the consuming renderer.
    monkeypatch.setattr(snapshot, "source_files", cache(snapshot.source_files))
    monkeypatch.setattr(Settings, "load", cache(Settings.load))
    assert effort.walk("day", "--full=speed", "--group=sentinel")[0] == 0
    assert effort.render() == 0
    _assert_grouped_request(effort)


def test_published_capture_survives_same_name_drift(
    published_capture: tuple[Effort, str], capsys: pytest.CaptureFixture[str],
) -> None:
    """Published evidence selects old files while progress discloses the new definition."""
    effort, capture = published_capture
    groups = effort.root / ".ghog-groups"
    groups.write_text(groups.read_text(encoding="utf-8").replace("tests/old/**", "tests/new/**"), encoding="utf-8")
    _assert_bound_collection(effort, capture)
    capsys.readouterr()
    assert prompt_workflow.main(["--root", str(effort.root), "progress"]) == 0
    progress = capsys.readouterr().out
    assert "pending change" in progress
    assert "group sentinel" in progress


def _assert_bound_collection(effort: Effort, capture: str) -> None:
    """The captured affected run keeps old members despite both ambient selectors."""
    code, spawns = effort.walk("affected", "--no-cov", f"--scope-file={capture}",
                               environment={"GHOG_GROUP": "other"})
    assert code == 0
    assert "tests/old/test_core.py" in spawns.commands[-1]
    assert "tests/new/test_core.py" not in spawns.commands[-1]
    assert "tests/other/test_core.py" not in spawns.commands[-1]


def _assert_grouped_request(effort: Effort) -> str:
    """Check the renderer's concrete policy and earned proof before publication."""
    envelope, _authored, evidence = effort.request()
    assert envelope.test_scope is not None
    assert envelope.test_scope["scope"] == "group:sentinel"
    assert envelope.test_scope["proof"] == "speed"
    assert envelope.test_scope["requirement"] == "docs/v9.9.0/feature-request.v9.9.0.topic.md"
    assert evidence["resolved_validation_set"]["commands"] == [
        {"command": "ghog day --full=speed --group=sentinel", "sources": ["project"]},
    ]
    return str(envelope.test_scope["fingerprint"])


def _published_scope(effort: Effort, capsys: pytest.CaptureFixture[str], fingerprint: str) -> str:
    """Read the public status path and check the exact persisted captured members."""
    capsys.readouterr()
    assert exchange_cli.main(["status", *common_arguments(effort.context)]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["paths"]["scope"] == effort.paths.scope.as_posix()
    assert status["bound_scope"]["fingerprint"] == fingerprint
    assert effort.paths.scope.read_bytes() == effort.files["capture"].read_bytes()
    captured = validate_capture(effort.root, effort.paths.scope.read_text(encoding="utf-8"))
    assert captured.test_files == ("tests/old/test_core.py",)
    return str(status["paths"]["scope"])
