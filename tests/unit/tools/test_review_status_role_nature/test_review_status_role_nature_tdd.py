"""Tests for schema-2 role-nature reconciliation and evidence paths."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.llm_nature import LlmNature
from tools.review_exchange_models import ReviewExchangeError
from tools.review_role_nature import RoleNatureSnapshot
from tools.review_status_models import RoleNatureState
from tools.review_status_role_nature import ReviewStatusRoleNatureProjection

if TYPE_CHECKING:
    from pathlib import Path


def test_matching_snapshots_project_one_typed_nature_with_evidence(tmp_path: Path) -> None:
    """Matching artifact snapshots retain their paths for machine diagnosis."""
    snapshots = (
        (
            tmp_path / ".reviews" / "coordination.md",
            RoleNatureSnapshot(requestor=LlmNature.CODEX),
        ),
        (
            tmp_path / ".reviews" / "request.md",
            RoleNatureSnapshot(requestor=LlmNature.CODEX),
        ),
    )

    requestor, reviewer = ReviewStatusRoleNatureProjection.project(tmp_path, snapshots)

    assert requestor.value is LlmNature.CODEX
    assert [item.path for item in requestor.evidence] == [
        ".reviews/coordination.md",
        ".reviews/request.md",
    ]
    assert reviewer.value is RoleNatureState.UNRECORDED
    assert all(item.nature is None for item in reviewer.evidence)


def test_conflicting_snapshots_report_all_stable_evidence(tmp_path: Path) -> None:
    """Different known values produce a conflict and preserve bounded input order."""
    snapshots = (
        (
            tmp_path / ".reviews" / "request.md",
            RoleNatureSnapshot(reviewer=LlmNature.CLAUDE),
        ),
        (
            tmp_path / ".reviews" / "coordination.md",
            RoleNatureSnapshot(reviewer=LlmNature.GEMINI),
        ),
        (tmp_path / ".reviews" / "answer.md", RoleNatureSnapshot()),
    )

    _requestor, reviewer = ReviewStatusRoleNatureProjection.project(tmp_path, snapshots)

    assert reviewer.value is RoleNatureState.CONFLICTING
    assert [(item.path, item.nature) for item in reviewer.evidence] == [
        (".reviews/request.md", LlmNature.CLAUDE),
        (".reviews/coordination.md", LlmNature.GEMINI),
        (".reviews/answer.md", None),
    ]


def test_evidence_outside_repository_is_rejected(tmp_path: Path) -> None:
    """Evidence paths cannot escape the repository-relative status contract."""
    outside = tmp_path.parent / "outside-coordination.md"

    with pytest.raises(ReviewExchangeError, match="outside repository root"):
        ReviewStatusRoleNatureProjection.project(
            tmp_path,
            ((outside, RoleNatureSnapshot(requestor=LlmNature.CODEX)),),
        )


# eof
