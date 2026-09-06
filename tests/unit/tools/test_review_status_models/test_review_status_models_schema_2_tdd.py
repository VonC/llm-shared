"""Schema-2 model tests for migration and role-nature status evidence."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, cast

import pytest

from tools.llm_nature import LlmNature
from tools.review_status_models import (
    MigrationState,
    MigrationStatus,
    ReviewStatusModelError,
    RoleNatureEvidenceStatus,
    RoleNatureState,
    RoleNatureStatus,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_MOVED_COUNT = 2


def test_migration_status_factories_project_schema_2_records() -> None:
    """Ready, completed, and blocked states expose explicit typed fields."""
    assert MigrationStatus.unnecessary(".reviews").to_dict() == {
        "state": "unnecessary",
        "artifact_home": ".reviews",
        "moved_count": 0,
        "diagnostics": [],
    }
    assert (
        MigrationStatus.completed("runtime/reviews", _MOVED_COUNT).to_dict()[
            "moved_count"
        ]
        == _MOVED_COUNT
    )
    assert MigrationStatus.blocked(".reviews", ("collision",)).to_dict() == {
        "state": "blocked",
        "artifact_home": ".reviews",
        "moved_count": 0,
        "diagnostics": ["collision"],
    }


@pytest.mark.parametrize(
    "status",
    [
        MigrationStatus.unnecessary(".reviews"),
        MigrationStatus.completed(".reviews", 1),
        MigrationStatus.blocked(".reviews", ("blocked",)),
    ],
)
@pytest.mark.parametrize(
    "changes",
    [
        {"state": "unnecessary"},
        {"artifact_home": "../outside"},
        {"moved_count": True},
        {"moved_count": -1},
        {"diagnostics": ["not-a-tuple"]},
        {"diagnostics": ("",)},
    ],
)
def test_migration_status_rejects_untyped_or_noncanonical_fields(
    status: MigrationStatus,
    changes: dict[str, object],
) -> None:
    """Migration facts remain closed, relative, non-negative, and diagnostic-safe."""
    with pytest.raises(ReviewStatusModelError):
        replace(status, **changes)


@pytest.mark.parametrize(
    "factory",
    [
        lambda: MigrationStatus(MigrationState.UNNECESSARY, ".reviews", 1),
        lambda: MigrationStatus(MigrationState.COMPLETED, ".reviews", 0),
        lambda: MigrationStatus(MigrationState.BLOCKED, ".reviews", 0),
        lambda: MigrationStatus(
            MigrationState.UNNECESSARY,
            ".reviews",
            0,
            ("unexpected",),
        ),
    ],
)
def test_migration_status_rejects_cross_field_contradictions(
    factory: Callable[[], object],
) -> None:
    """Construction cannot pair a migration state with contradictory evidence."""
    with pytest.raises(ReviewStatusModelError):
        factory()


def test_role_nature_status_projects_typed_evidence() -> None:
    """One known value and one conflict keep their complete path evidence."""
    codex = RoleNatureEvidenceStatus(".reviews/request.md", LlmNature.CODEX)
    missing = RoleNatureEvidenceStatus(".reviews/answer.md", None)
    known = RoleNatureStatus(LlmNature.CODEX, (codex, missing))
    conflict = RoleNatureStatus(
        RoleNatureState.CONFLICTING,
        (
            codex,
            RoleNatureEvidenceStatus(".reviews/coordination.md", LlmNature.CLAUDE),
        ),
    )

    assert known.evidence_dicts() == [
        {"path": ".reviews/request.md", "nature": "codex"},
        {"path": ".reviews/answer.md", "nature": None},
    ]
    assert conflict.value is RoleNatureState.CONFLICTING
    assert RoleNatureStatus.unrecorded().value is RoleNatureState.UNRECORDED


@pytest.mark.parametrize(
    "factory",
    [
        lambda: RoleNatureEvidenceStatus("../outside", None),
        lambda: RoleNatureEvidenceStatus(
            ".reviews/request.md",
            cast("LlmNature", "codex"),
        ),
        lambda: RoleNatureStatus(cast("LlmNature", "codex")),
        lambda: RoleNatureStatus(
            RoleNatureState.UNRECORDED,
            cast("tuple[RoleNatureEvidenceStatus, ...]", []),
        ),
        lambda: RoleNatureStatus(
            RoleNatureState.UNRECORDED,
            cast("tuple[RoleNatureEvidenceStatus, ...]", (object(),)),
        ),
        lambda: RoleNatureStatus(
            RoleNatureState.UNRECORDED,
            (RoleNatureEvidenceStatus(".reviews/request.md", LlmNature.CODEX),),
        ),
        lambda: RoleNatureStatus(
            RoleNatureState.CONFLICTING,
            (RoleNatureEvidenceStatus(".reviews/request.md", LlmNature.CODEX),),
        ),
        lambda: RoleNatureStatus(
            LlmNature.CODEX,
            (RoleNatureEvidenceStatus(".reviews/request.md", LlmNature.CLAUDE),),
        ),
    ],
)
def test_role_nature_status_rejects_invalid_or_contradictory_evidence(
    factory: Callable[[], object],
) -> None:
    """Schema-2 role status never normalizes malformed or disagreeing facts."""
    with pytest.raises(ReviewStatusModelError):
        factory()


# eof
