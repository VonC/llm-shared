"""Fail-closed resume and status across every unsafe physical artifact layout.

Fix: split out of ``test_review_resume_migration_tdd``. Its six layouts and
the two migration journeys were the longest-running module of the suite, and
``--dist loadscope`` keeps a whole module on one worker, so they ran back to
back. The scenarios and their assertions are unchanged.
"""

# ruff: noqa: PLR2004
from __future__ import annotations

from typing import Any

import pytest

from tests.acceptance.review_resume.conftest import SHARED_ROOT, ReviewRepository
from tools.review_artifact_migration import ReviewArtifactMigration


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(layout, marks=pytest.mark.xdist_group(f"blocked-{layout}"))
        for layout in ("collision", "journal", "uncovered", "outside", "tracked", "root")
    ],
)
def blocked_layout(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Seed each unsafe physical layout before observing the fail-closed commands."""
    repo = ReviewRepository(tmp_path_factory.mktemp("resume-blocked") / "caller")
    repo.start_request()
    if request.param == "collision":
        (repo.root / repo.paths.request.name).write_bytes(b"conflicting legacy request")
    elif request.param == "journal":
        ReviewArtifactMigration(project_root=repo.root).journal_path.write_bytes(b"broken journal")
    elif request.param == "uncovered":
        (repo.home / ".gitignore").write_bytes(b"!a.*\n")
        (repo.root / ".gitignore").write_text("docs/**/review.*.md\n", encoding="utf-8")
    else:
        location = {"outside": "../outside", "tracked": "docs", "root": "."}[request.param]
        (repo.root / ".review-artifacts.ini").write_text(
            f"[review-artifacts]\nhome = {location}\n", encoding="utf-8",
        )
    before = repo.evidence()
    trace = repo.resume("resume", role="requestor")
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    return {"before": before, "after": repo.evidence(), "trace": trace, "status": status}


def test_unsafe_layout_stops_before_identity_or_ownership_changes(blocked_layout: dict[str, Any]) -> None:
    """AC3-4,16-18: unsafe configuration, collisions and incomplete recovery block resume."""
    journey = blocked_layout
    assert journey["before"] == journey["after"]
    assert all(item.payload["operation"] in {"migration-check", "migrate-artifacts"}
               for item in journey["trace"])
    assert journey["trace"][-1].code != 0
    assert journey["status"].code == 2
    assert "ownership_token" not in journey["status"].payload
    assert journey["status"].payload["migration"]["diagnostics"]


# eof
