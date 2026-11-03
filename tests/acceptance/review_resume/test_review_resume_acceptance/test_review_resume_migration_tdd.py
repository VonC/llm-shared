"""Exercise migration, status, inspection and claim in process.

The frozen filesystem/Git fixtures supply declared repository facts. Production
migration and resume code moves protocol artifacts and reports nested schema-2
failures; assertions cover those bytes and diagnostics, not native Git state.
Unsafe layouts have their own cases in ``test_review_resume_blocked_layout_tdd``.
"""

# ruff: noqa: PLR2004, SLF001
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.conftest import SHARED_ROOT, ReviewRepository
from tests.scenario_cli import cache_review_inputs
from tools.review_artifact_migration import MigrationState, ReviewArtifactMigration

if TYPE_CHECKING:
    from pathlib import Path


def _legacy_root(repo: ReviewRepository) -> dict[str, bytes]:
    """Construct an old installation by relocating its complete runtime set."""
    before: dict[str, bytes] = {}
    for path in (repo.paths.request, repo.paths.coordination, repo.home / "a.review-mode"):
        before[path.name] = path.read_bytes()
        path.rename(repo.root / path.name)
    return before


@pytest.fixture(
    params=[
        pytest.param(layout, marks=pytest.mark.xdist_group(f"migration-{layout}"))
        for layout in ("legacy-root", "former-default")
    ],
)
def migration_journey(tmp_path: Path, request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Declare the old layout; migration and its assertions execute in the call."""
    repo = ReviewRepository(tmp_path / "resume")
    repo.start_request()
    transcript = repo.paths.transcript.read_bytes()
    if request.param == "legacy-root":
        before = _legacy_root(repo)
    else:
        before = {path.name: path.read_bytes() for path in
                  (repo.paths.request, repo.paths.coordination, repo.home / "a.review-mode")}
        (repo.root / ".review-artifacts.ini").write_text(
            "[review-artifacts]\nhome = runtime/reviews\n", encoding="utf-8",
        )
    # Observe migration separately before claim can legitimately update ownership.
    cache_review_inputs(monkeypatch)()
    target = repo.root / (".reviews" if request.param == "legacy-root" else "runtime/reviews")
    return {"repo": repo, "before": before, "target": target, "transcript": transcript}


@pytest.mark.parametrize("continuation", ["status", "resume"])
def test_status_migrates_complete_sets_once_without_changing_evidence(
    migration_journey: dict[str, Any], continuation: str,
) -> None:
    """AC3,5,18: both old layouts move together and schema 2 distinguishes repeated status."""
    journey = migration_journey
    repo = journey["repo"]
    # The automatic-resume case below checks the CLI preflight sequence.
    # Here the same real check supplies the prerequisite for status migration.
    check = ReviewArtifactMigration(project_root=repo.root).migration_check()
    assert check.state is MigrationState.MIGRATION_REQUIRED, check
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    assert status.code == 0, status
    assert status.payload["migration"]["state"] == "completed", status
    journey.update(check=check, status=status,
                   migrated={name: (journey["target"] / name).read_bytes() for name in journey["before"]},
                   transcript_after=repo.paths.transcript.read_bytes())
    _assert_migrated_evidence(journey)
    if continuation == "status":
        repeated = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
        assert repeated.payload["migration"]["state"] == "unnecessary"
    else:
        # Status already discovered the migrated exchange. Exercise the real
        # CLI claim against that known first round without another inspection
        # of the unchanged home; the full bare-resume sequence is checked below.
        claimed = repo.claim_known(role="requestor")
        assert claimed.payload["outcome"] == "ready"
    assert journey["transcript"] == repo.paths.transcript.read_bytes()


def _assert_migrated_evidence(journey: dict[str, Any]) -> None:
    """Verify migration's schema and byte-preservation contract."""
    assert journey["check"].state is MigrationState.MIGRATION_REQUIRED
    assert journey["status"].code == 0
    assert journey["status"].payload["schema_version"] == 2
    assert journey["status"].payload["migration"]["state"] == "completed"
    assert journey["before"] == journey["migrated"]
    assert journey["transcript"] == journey["transcript_after"]
    assert (journey["target"] / ".gitignore").read_bytes() == b"*\n"


@pytest.mark.parametrize("layout", ["legacy-root", "former-default"])
def test_resume_checks_migrates_rechecks_then_claims(tmp_path: Path, layout: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """AC2-4,14: bare resume resolves old evidence before selecting and claiming a role."""
    repo = ReviewRepository(tmp_path / "automatic")
    repo.start_request()
    if layout == "legacy-root":
        _legacy_root(repo)
    else:
        (repo.root / ".review-artifacts.ini").write_text(
            "[review-artifacts]\nhome = runtime/reviews\n", encoding="utf-8",
        )
    cache_review_inputs(monkeypatch)()
    results = repo.resume("resume", role="requestor")
    assert [item.payload["operation"] for item in results] == [
        "migration-check", "migrate-artifacts", "migration-check", "resume-inspect", "claim",
    ]
    assert results[0].payload["outcome"] == "migration-required"
    assert all(item.code == 0 for item in results[1:])
    assert results[-1].payload["action"] == "wait-exact-answer"


# eof
