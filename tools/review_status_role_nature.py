"""Linear schema-2 projection for role-nature snapshots.

Step 4 keeps role identity diagnosis outside the main status service and
retains every already-parsed artifact path as typed evidence.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_status_models import (
    RoleNatureEvidenceStatus,
    RoleNatureState,
    RoleNatureStatus,
)

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tools.llm_nature import LlmNature
    from tools.review_role_nature import RoleNatureSnapshot


class ReviewStatusRoleNatureProjection:
    """Reconcile each role in stable input order without rereading artifacts."""

    @classmethod
    def project(
        cls,
        root: Path,
        snapshots: Sequence[tuple[Path, RoleNatureSnapshot]],
    ) -> tuple[RoleNatureStatus, RoleNatureStatus]:
        """Return requestor and reviewer status from one bounded snapshot set."""
        return (
            cls._project_role(root, snapshots, ReviewRole.REQUESTOR),
            cls._project_role(root, snapshots, ReviewRole.REVIEWER),
        )

    @staticmethod
    def _project_role(
        root: Path,
        snapshots: Sequence[tuple[Path, RoleNatureSnapshot]],
        role: ReviewRole,
    ) -> RoleNatureStatus:
        """Project one role in a linear pass and preserve diagnostic evidence."""
        evidence: list[RoleNatureEvidenceStatus] = []
        recorded: set[LlmNature] = set()
        repository_root = root.resolve()
        for path, snapshot in snapshots:
            try:
                relative = path.resolve().relative_to(repository_root).as_posix()
            except ValueError as error:
                message = f"role-nature evidence is outside repository root: {path}"
                raise ReviewExchangeError(message) from error
            nature = snapshot.for_role(role)
            evidence.append(RoleNatureEvidenceStatus(relative, nature))
            if nature is not None:
                recorded.add(nature)
        if not recorded:
            value = RoleNatureState.UNRECORDED
        elif len(recorded) == 1:
            value = next(iter(recorded))
        else:
            value = RoleNatureState.CONFLICTING
        return RoleNatureStatus(value, tuple(evidence))


__all__ = ["ReviewStatusRoleNatureProjection"]


# eof
