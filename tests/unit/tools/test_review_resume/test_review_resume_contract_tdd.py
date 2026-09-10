"""Verify migration-first claim contracts and exact selection failure boundaries."""
# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_resume.test_review_exchange_cli_resume_tdd import (
    FakeEntry,
)
from tools import review_exchange_cli_resume as subject
from tools.review_exchange_cli_parser import parser
from tools.review_exchange_models import ReviewExchangeError

_FATAL_EXIT = 2
_CHOICE_EXIT = 3

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize("operation", ["resume-inspect", "claim", "wait-any-request"])
def test_migration_failure_blocks_identity_detection_and_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str,
) -> None:
    """An untrusted preflight must never reach role detection or acquire ownership."""
    status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.OPERATIONAL_FAILURE, exchanges=())
    monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
    monkeypatch.setattr(subject.LlmNatureDetector, "detect", lambda *_args, **_kwargs: pytest.fail("identity ran before migration"))
    args = parser().parse_args([operation, *(
        ["--document", "docs/plan.v0.11.0.resume.md", "--role", "reviewer", "--round", "1", "--occurrence", "1"]
        if operation == "claim" else []
    )])
    if operation == "wait-any-request":
        payload, code = subject.execute_resume_operation(args, tmp_path)
        assert code == _FATAL_EXIT
        assert payload["outcome"] == "operational-failure"
    else:
        with pytest.raises(ReviewExchangeError, match="trustworthy"):
            subject.execute_resume_operation(args, tmp_path)


@pytest.mark.parametrize("selection", ["gone", "multiple", "round", "occurrence"])
def test_claim_rejects_changed_selection_before_core_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, selection: str,
) -> None:
    """A selected document, round and occurrence must still denote exactly one exchange."""
    entry = FakeEntry()
    entries = (entry, entry) if selection == "multiple" else (entry,)
    status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.TRUSTWORTHY, exchanges=entries)
    monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
    monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
    monkeypatch.setattr(subject, "ReviewExchangeCore", lambda *_: pytest.fail("invalid selection reached core"))
    args = parser().parse_args([
        "claim", "--document", "gone.md" if selection == "gone" else entry.reviewed_document,
        "--role", "reviewer", "--round", "2" if selection == "round" else "1",
        "--occurrence", "2" if selection == "occurrence" else "1",
    ])
    with pytest.raises(ReviewExchangeError, match=r"no longer active|one current|selection changed"):
        subject.execute_resume_operation(args, tmp_path)


def test_claim_requires_coordination_and_returns_conflict_without_capability(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lost coordination and a selected identity mismatch are fail-closed boundaries."""
    entry = FakeEntry()
    status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.TRUSTWORTHY, exchanges=(entry,))
    monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
    monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
    monkeypatch.setattr(subject, "_context_from_status", lambda *_: object())
    monkeypatch.setattr(subject, "load_review_configuration", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(subject, "derive_artifact_paths", lambda *_args, **_kwargs: object())
    store = SimpleNamespace(read_coordination=lambda **_: None)
    monkeypatch.setattr(subject, "ReviewExchangeStore", lambda _: store)
    args = parser().parse_args([
        "claim", "--document", entry.reviewed_document, "--role", "reviewer",
        "--round", "1", "--occurrence", "1", "--trusted-host-hint", "codex",
    ])
    with pytest.raises(ReviewExchangeError, match="requires durable coordination"):
        subject.execute_resume_operation(args, tmp_path)
    store.read_coordination = lambda **_: SimpleNamespace(policy=object())
    monkeypatch.setattr(subject, "ReviewExchangeCore", lambda *_: SimpleNamespace(present_ownership=lambda _: None))
    monkeypatch.setattr(subject, "claim_selected", lambda *_args, **_kwargs: pytest.fail("unapproved conflict claimed"))
    payload, code = subject.execute_resume_operation(args, tmp_path)
    assert code == _CHOICE_EXIT
    assert payload["outcome"] == "confirmation-required"
    assert "ownership_token" not in payload


def test_step_selection_keeps_two_code_reviews_of_one_plan_distinct(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The human can resolve two exchanges sharing a plan without filename ordering."""
    first, second = FakeEntry(), FakeEntry()
    second.implementation_step = "6"
    status = SimpleNamespace(outcome=subject.ReviewStatusOutcome.TRUSTWORTHY, exchanges=(first, second))
    monkeypatch.setattr(subject, "ExchangeStatus", FakeEntry)
    monkeypatch.setattr(subject, "collect_review_status", lambda *_: status)
    args = parser().parse_args([
        "resume-inspect", "--document", first.reviewed_document, "--implementation-step", "6",
        "--role", "reviewer", "--trusted-host-hint", "claude",
    ])
    payload, code = subject.execute_resume_operation(args, tmp_path)
    assert code == 0
    assert payload["candidates"][0]["implementation_step"] == "6"
    assert len(payload["candidates"]) == 1


# eof
