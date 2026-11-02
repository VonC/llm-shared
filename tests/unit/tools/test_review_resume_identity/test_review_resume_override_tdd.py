"""An approved Override lets another LLM take over a requestor or reviewer role.

Both rounds are published by Codex before the measured takeover; the Claude
session then claims with Override, its replacement is recorded once in the
transcript, and its next publication records Claude for that role.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_review_exchange_lifecycle import (
    test_review_exchange_lifecycle_tdd as lifecycle,
)
from tools.llm_nature import LlmNature
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import ReviewExchangeError, ReviewRole
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_transcript_identity import render_nature_override_entry
from tools.review_resume_identity import claim_selected
from tools.review_role_nature import (
    MutableRoleNatureArtifact,
    RoleNatureBackfill,
    RoleNatureBackfillContext,
    RoleNatureEvidence,
    RoleNatureSnapshot,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.review_exchange_store import ReviewExchangeStore

_REQUESTOR_OVERRIDE = "llm-nature-override-requestor-exchange-1-codex-to-claude"
_REVIEWER_OVERRIDE = "llm-nature-override-reviewer-exchange-1-codex-to-claude"
Harness = tuple[ReviewExchangeCore, "ReviewExchangeStore", lifecycle.ReviewContext, lifecycle.FakeTime]


def _host(monkeypatch: pytest.MonkeyPatch, nature: LlmNature) -> None:
    """Declare exactly one host signal for the publications that follow."""
    signals = {LlmNature.CLAUDE: "CLAUDECODE", LlmNature.CODEX: "CODEX_THREAD_ID"}
    for name in signals.values():
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv(signals[nature], "1")


@pytest.fixture
def codex_answered(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Harness:
    """Codex published round one's request and its intermediate answer."""
    _host(monkeypatch, LlmNature.CODEX)
    core, store, context, clock = lifecycle._harness(tmp_path)
    lifecycle._start_and_request(core, context, clock)
    core.publish_answer(lifecycle._answer(context, clock, 1), "Changes requested.")
    return core, store, context, clock


def _resumed(harness: Harness) -> ReviewExchangeCore:
    """Open the same exchange from a new session."""
    old, store, context, clock = harness
    return ReviewExchangeCore(store, context, old.policy, old.configuration, wall_clock=clock.now)


def _transcript(store: ReviewExchangeStore) -> str:
    return store.paths.transcript.read_text(encoding="utf-8")


def test_claude_requestor_takes_over_with_override_and_publishes(
    codex_answered: Harness, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Override replaces the recorded requestor, once, and the next request records Claude."""
    _old, store, context, clock = codex_answered
    _host(monkeypatch, LlmNature.CLAUDE)
    resumed = _resumed(codex_answered)
    with pytest.raises(ReviewExchangeError, match="conflicts require Override"):
        claim_selected(resumed, ReviewRole.REQUESTOR, LlmNature.CLAUDE, round_number=1, occurrence=1, override=False)
    capability = claim_selected(resumed, ReviewRole.REQUESTOR, LlmNature.CLAUDE, round_number=1, occurrence=1, override=True)
    record = store.read_coordination(required=True)
    assert record is not None
    assert record.role_natures == RoleNatureSnapshot(LlmNature.CLAUDE, LlmNature.CODEX)
    assert _transcript(store).count(f"<!-- review-entry-id: {_REQUESTOR_OVERRIDE} -->") == 1
    resumed.present_ownership(capability)
    assert claim_selected(resumed, ReviewRole.REQUESTOR, LlmNature.CLAUDE, round_number=1, occurrence=1, override=True) == capability
    assert _transcript(store).count(_REQUESTOR_OVERRIDE) == 1
    resumed.consume_answer(reviewed_work_changed=True)
    resumed.continue_round()
    published = resumed.publish_request(lifecycle._request(context, clock, 2), "Requestor report for round 2.")
    assert published.role_natures.requestor is LlmNature.CLAUDE
    envelope, _ = parse_envelope_markdown(store.paths.request.read_text(encoding="utf-8"))
    assert envelope.role_natures == RoleNatureSnapshot(LlmNature.CLAUDE, LlmNature.CODEX)


def test_claude_reviewer_takes_over_with_override_and_answers(
    codex_answered: Harness, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The reviewer gets the same rule: Override replaces it, the answer records Claude."""
    old, store, context, clock = codex_answered
    old.consume_answer(reviewed_work_changed=True)
    old.continue_round()
    old.publish_request(lifecycle._request(context, clock, 2), "Requestor report for round 2.")
    _host(monkeypatch, LlmNature.CLAUDE)
    resumed = _resumed(codex_answered)
    capability = claim_selected(resumed, ReviewRole.REVIEWER, LlmNature.CLAUDE, round_number=2, occurrence=1, override=True)
    resumed.present_ownership(capability)
    record = store.read_coordination(required=True)
    assert record is not None
    assert record.role_natures == RoleNatureSnapshot(LlmNature.CODEX, LlmNature.CLAUDE)
    assert _transcript(store).count(f"<!-- review-entry-id: {_REVIEWER_OVERRIDE} -->") == 1
    answered = resumed.publish_answer(lifecycle._answer(context, clock, 2), "Claude reviewer feedback.")
    assert answered.role_natures.reviewer is LlmNature.CLAUDE
    envelope, _ = parse_envelope_markdown(store.paths.answer.read_text(encoding="utf-8"))
    assert envelope.role_natures == RoleNatureSnapshot(LlmNature.CODEX, LlmNature.CLAUDE)


def test_override_replacement_rejects_what_it_cannot_record(tmp_path: Path) -> None:
    """No unknown replacement, no human nature, no entry without Override."""
    snapshot = RoleNatureSnapshot(LlmNature.CODEX, None)
    assert snapshot.replace_role(ReviewRole.REQUESTOR, LlmNature.CLAUDE).requestor is LlmNature.CLAUDE
    with pytest.raises(ReviewExchangeError, match="needs a known"):
        snapshot.replace_role(ReviewRole.REQUESTOR, LlmNature.UNKNOWN)
    with pytest.raises(ReviewExchangeError, match="human role"):
        snapshot.replace_role(ReviewRole.HUMAN, LlmNature.CLAUDE)
    with pytest.raises(ValueError, match="human role"):
        render_nature_override_entry(ReviewRole.HUMAN, 1, LlmNature.CODEX, LlmNature.CLAUDE)
    with pytest.raises(ValueError, match="positive"):
        render_nature_override_entry(ReviewRole.REVIEWER, 0, LlmNature.CODEX, LlmNature.CLAUDE)
    transcript = tmp_path / "transcript.md"
    transcript.write_text("# Transcript\n", encoding="utf-8")
    coordination = MutableRoleNatureArtifact(
        RoleNatureEvidence(tmp_path / "coordination.md", ReviewRole.REVIEWER, LlmNature.CODEX),
        RoleNatureSnapshot(None, LlmNature.CODEX), str, _never_valid,
    )
    context = RoleNatureBackfillContext(ReviewRole.REVIEWER, LlmNature.CLAUDE, transcript, 1)
    with pytest.raises(ReviewExchangeError, match="requires Override"):
        RoleNatureBackfill().record_override(coordination, context, LlmNature.CODEX)
    assert transcript.read_text(encoding="utf-8") == "# Transcript\n"


def _never_valid(content: str) -> None:
    """Fail if a refused replacement ever reached validation."""
    raise AssertionError(content)


# eof
