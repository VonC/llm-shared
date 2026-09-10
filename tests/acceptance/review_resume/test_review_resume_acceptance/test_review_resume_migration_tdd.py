"""Migration-first launcher acceptance, including schema-2 nested failure diagnostics.

Fix: the blocked-layout scenarios moved to
``test_review_resume_blocked_layout_tdd``. This module was the longest-running
file of the suite, and ``--dist loadscope`` keeps a whole module on one worker,
so its two journeys and the six unsafe layouts ran back to back. Both journeys
and every assertion here are unchanged, including the status assertions that
make a refused migration report its own diagnostic.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import SHARED_ROOT, ReviewRepository


def _legacy_root(repo: ReviewRepository) -> dict[str, bytes]:
    """Construct an old installation by relocating its complete runtime set."""
    before: dict[str, bytes] = {}
    for path in (repo.paths.request, repo.paths.coordination, repo.home / "a.review-mode"):
        before[path.name] = path.read_bytes()
        path.rename(repo.root / path.name)
    return before


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(layout, marks=pytest.mark.xdist_group(f"migration-{layout}"))
        for layout in ("legacy-root", "former-default")
    ],
)
def migration_journey(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Exercise resume's migration sequence and its public status counterpart."""
    base = tmp_path_factory.mktemp("resume-migration")
    repo = ReviewRepository(base / "resume")
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
    check = repo.run("migration-check")
    assert check.payload["outcome"] == "migration-required", check
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    assert status.code == 0, status
    assert status.payload["migration"]["state"] == "completed", status
    target = repo.root / (".reviews" if request.param == "legacy-root" else "runtime/reviews")
    migrated = {name: (target / name).read_bytes() for name in before}
    repeated = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    trace = repo.resume("resume", role="requestor")
    second = ReviewRepository(base / "automatic")
    second.start_request()
    _legacy_root(second)
    automatic = second.resume("resume", role="requestor")
    return {"repo": repo, "before": before, "migrated": migrated, "check": check, "status": status,
                "repeated": repeated, "trace": trace, "automatic": automatic, "target": target,
                "transcript": transcript, "transcript_after": repo.paths.transcript.read_bytes()}


def test_status_migrates_complete_sets_once_without_changing_evidence(migration_journey: dict[str, Any]) -> None:
    """AC3,5,18: both old layouts move together and schema 2 distinguishes repeated status."""
    journey = migration_journey
    assert journey["check"].payload["outcome"] == "migration-required"
    assert journey["status"].code == 0
    assert journey["status"].payload["schema_version"] == 2
    assert journey["status"].payload["migration"]["state"] == "completed"
    assert journey["repeated"].payload["migration"]["state"] == "unnecessary"
    assert journey["before"] == journey["migrated"]
    assert journey["transcript"] == journey["transcript_after"]
    assert (journey["target"] / ".gitignore").read_bytes() == b"*\n"


def test_resume_checks_migrates_rechecks_then_claims(migration_journey: dict[str, Any]) -> None:
    """AC2-4,14: bare resume resolves old evidence before selecting and claiming a role."""
    results = migration_journey["automatic"]
    assert [item.payload["operation"] for item in results] == [
        "migration-check", "migrate-artifacts", "migration-check", "resume-inspect", "claim",
    ]
    assert results[0].payload["outcome"] == "migration-required"
    assert all(item.code == 0 for item in results[1:])
    assert results[-1].payload["action"] == "wait-exact-answer"
    assert migration_journey["trace"][-1].payload["outcome"] == "ready"


# eof
