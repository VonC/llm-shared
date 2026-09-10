"""Step 2 schema tests for strict and legacy role-nature snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools.llm_nature import LlmNature
from tools.review_exchange_models import (
    Actor,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewExchangeError,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import Envelope
from tools.review_role_nature import RoleNatureSnapshot

if TYPE_CHECKING:
    from pathlib import Path

_STAMP = "2026-09-03T09:00:00+02:00"


def _context(tmp_path: Path) -> ReviewContext:
    """Return one code-review context with a real plan path."""
    plan = tmp_path / "plan.v0.11.0.topic.md"
    plan.write_text("# Plan\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(ReviewFamily.CODE, "code", "v0.11.0", "topic"),
        plan,
        None,
        "2",
    )


def test_envelope_writes_two_roles_and_reads_legacy_absence(tmp_path: Path) -> None:
    """New JSON is complete while a missing field remains a valid legacy shape."""
    context = _context(tmp_path)
    envelope = Envelope(
        context.identity,
        None,
        context.document_path,
        "2",
        ReviewRole.REQUESTOR,
        1,
        _STAMP,
        role_natures=RoleNatureSnapshot(requestor=LlmNature.CODEX),
    )

    data = envelope.to_dict()
    assert data["role_natures"] == {"requestor": "codex", "reviewer": None}
    assert Envelope.from_dict(data) == envelope
    del data["role_natures"]
    assert Envelope.from_dict(data).role_natures == RoleNatureSnapshot()


def test_coordination_writes_two_roles_and_reads_legacy_absence(tmp_path: Path) -> None:
    """Coordination uses the same strict snapshot and one legacy exception."""
    context = _context(tmp_path)
    record = CoordinationRecord(
        context,
        FamilyPolicy("commit-ready", "Rework", "Commit"),
        CoordinationStatus.ACTIVE,
        Actor.REQUESTOR,
        Actor.REVIEWER,
        1,
        _STAMP,
        role_natures=RoleNatureSnapshot(requestor=LlmNature.CODEX),
    )

    data = record.to_dict()
    assert CoordinationRecord.from_dict(data) == record
    del data["role_natures"]
    assert CoordinationRecord.from_dict(data).role_natures == RoleNatureSnapshot()


def test_identity_bearing_models_reject_unsupported_natures(tmp_path: Path) -> None:
    """The compatibility parser does not accept unknown future enum strings."""
    context = _context(tmp_path)
    envelope = Envelope(
        context.identity,
        None,
        context.document_path,
        "2",
        ReviewRole.REQUESTOR,
        1,
        _STAMP,
    ).to_dict()
    envelope["role_natures"] = {"requestor": "other", "reviewer": None}

    with pytest.raises(ReviewExchangeError, match="role-nature snapshot"):
        Envelope.from_dict(envelope)
