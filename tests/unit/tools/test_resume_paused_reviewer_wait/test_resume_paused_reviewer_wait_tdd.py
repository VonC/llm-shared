"""Reviewer-wait classification tests over declared panes, histories, screens and ledger decisions.

Step 7 of v0.15.0 resume-paused: the leave-alone check needs the reviewer to
own the current claim generation and the reviewer pane to agree; a marked
reviewer entry since the receipt, undated or malformed is an uncertain prior
delivery; positive no-wait evidence needs a resting pane, a readable
history and, for Codex, a supported idle empty-input capture or, for Claude,
a ledger decision proving absence over the scope that binds the requestor.
Code review round 1: a question the pane reports refuses it on its own, even
idle, ready and with no blocking reason.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.test_resume_paused_planner.planner_world import (
    FakeHistory,
    FakeProbe,
)
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    ASKING,
    CLAIMED_GENERATION,
    IDLE,
    PROVED,
    QUESTION,
    REQUESTOR_PANE,
    REVIEWER_LAUNCH,
    REVIEWER_PANE,
    ROOT,
    THIRD_PANE,
    WORKING,
    FakeAbsence,
    exchange,
    marker,
    pane,
    taken,
)
from tools.resume_paused_claude_ledger import Absence, LedgerDecision
from tools.resume_paused_evidence import ObservedCommand, PaneActivity, ScreenVerdict
from tools.resume_paused_marker import MARKER_FLAG, Marker
from tools.resume_paused_models import SessionRole, timestamp_instant
from tools.resume_paused_plan_model import ActionKind
from tools.resume_paused_planner import marked_command
from tools.resume_paused_profiles import Host, ReadAccount, Reason
from tools.resume_paused_reviewer_wait import (
    ReviewerWait,
    UnprovedAbsence,
    WaitScope,
    prior_delivery,
    reviewer_active,
)
from tools.review_exchange_models import Actor

if TYPE_CHECKING:
    from tools.resume_paused_review import ExchangeSnapshot

SINCE = timestamp_instant("2026-11-18T07:25:09+01:00")
REVIEWER = pane(REVIEWER_PANE, Host.CODEX)
ELSEWHERE = Marker(REVIEWER_LAUNCH, THIRD_PANE, SessionRole.REVIEWER, "d" * 64)
ENTRY = "$llm-shared:review-resume as reviewer"
MARKED = marked_command(Host.CODEX, ActionKind.REVIEWER, marker(SessionRole.REVIEWER))
DRAFT = PaneActivity("idle", "", draft_held=True, question="", ready=True)
NOT_READY = PaneActivity("idle", "", draft_held=False, question="", ready=False)
PENDING = LedgerDecision(Absence.PENDING, (Reason("background-start-unmatched", 2), Reason("turn-open")), ReadAccount())


def typed(text: str, offset: int | None = 1) -> ObservedCommand:
    """Return one typed command, dated seconds after the receipt, or undated."""
    return ObservedCommand(text, None if offset is None else SINCE + timedelta(seconds=offset))


def scope(reviewer: Host = Host.CODEX) -> WaitScope:
    """Return the decision scope of the reviewer, binding the Claude requestor."""
    return WaitScope(ROOT, pane(REVIEWER_PANE, reviewer), SINCE, pane(REQUESTOR_PANE, Host.CLAUDE), "/resume-session --resume-paused x")


def wait(probe: ScreenVerdict = ScreenVerdict.IDLE_EMPTY, decision: LedgerDecision | None = PROVED) -> tuple[ReviewerWait, FakeAbsence]:
    """Return the classification over a declared probe verdict and ledger decision."""
    absence = FakeAbsence(decision)
    return ReviewerWait(FakeHistory(), FakeProbe({REVIEWER_PANE: probe}), absence), absence


@pytest.mark.parametrize(
    ("observed", "commands", "active"),
    [
        (exchange(marker(SessionRole.REVIEWER), owner=Actor.REVIEWER, generation=CLAIMED_GENERATION), (), True),
        (exchange(ELSEWHERE, owner=Actor.REVIEWER), (typed(ENTRY),), False),
        (exchange(None, owner=Actor.REVIEWER), (typed("/clear"), typed(ENTRY)), True),
        (exchange(None, owner=Actor.REVIEWER), (typed(ENTRY), typed("/clear")), False),
        (exchange(None, owner=Actor.REVIEWER), (typed("$llm-shared:review-resume as reviewer or requestor"),), False),
        (exchange(None, owner=Actor.REVIEWER), None, False),
        (exchange(None, owner=Actor.REVIEWER), (), False),
        (taken(), (typed(ENTRY),), False),
    ],
)
def test_only_an_agreeing_reviewer_owner_is_left_alone(observed: ExchangeSnapshot, commands: tuple[ObservedCommand, ...] | None, active: bool) -> None:  # noqa: FBT001
    """The reviewer owns the current generation and its pane agrees: the current marked claim or its latest entry."""
    assert reviewer_active(observed, REVIEWER, commands) is active


def test_an_owner_without_a_generation_is_never_active() -> None:
    """A legacy record without an ownership generation proves no active reviewer."""
    legacy = replace(exchange(None, owner=Actor.REVIEWER), ownership_generation=None)
    assert reviewer_active(legacy, REVIEWER, (typed(ENTRY),)) is False


@pytest.mark.parametrize(
    ("command", "uncertain"),
    [
        (typed(MARKED), True),
        (typed(MARKED, None), True),
        (typed(MARKED, -1), False),
        (typed(f"$llm-shared:review-resume {MARKER_FLAG} not-a-marker"), True),
        (typed(marked_command(Host.CODEX, ActionKind.REVIEWER, ELSEWHERE)), False),
        (typed(marked_command(Host.CODEX, ActionKind.REVIEWER, marker(SessionRole.REQUESTOR, pane=REVIEWER_PANE))), False),
        (typed(marked_command(Host.CLAUDE, ActionKind.RESUME, marker())), False),
        (typed(ENTRY), False),
        (typed("/clear"), False),
    ],
)
def test_a_marked_reviewer_entry_since_the_receipt_is_an_uncertain_prior_delivery(command: ObservedCommand, uncertain: bool) -> None:  # noqa: FBT001
    """A marked reviewer entry to this pane since the receipt, undated or malformed, is never resent."""
    assert prior_delivery((command,), REVIEWER, SINCE) is uncertain


@pytest.mark.parametrize(
    ("activity", "reason"),
    [
        (None, "reviewer-state-unknown"), (QUESTION, "reviewer-blocked"), (ASKING, "reviewer-question"),
        (DRAFT, "reviewer-draft"), (WORKING, "reviewer-busy"), (NOT_READY, "reviewer-busy"),
    ],
)
def test_the_reviewer_pane_must_rest(activity: PaneActivity | None, reason: str) -> None:
    """Only an idle, ready pane without a draft or question may be activated."""
    classification, _ = wait()
    verdict = classification.verdict(scope(), Host.CODEX, activity, ())
    assert (verdict.refusal.reason if verdict.refusal else None, verdict.refusal.failed if verdict.refusal else None) == (reason, False)


def test_an_unreadable_history_or_a_prior_delivery_keeps_the_reviewer_pending() -> None:
    """A history that cannot be read, or an earlier marked entry, stops the activation."""
    classification, _ = wait()
    unreadable = classification.verdict(scope(), Host.CODEX, IDLE, None)
    delivered = classification.verdict(scope(), Host.CODEX, IDLE, (typed(MARKED),))
    assert (getattr(unreadable.refusal, "reason", None), getattr(delivered.refusal, "reason", None)) == (
        "reviewer-history-unreadable", "reviewer-delivery-uncertain",
    )


@pytest.mark.parametrize(
    ("probe", "reason", "notes"),
    [
        (ScreenVerdict.IDLE_EMPTY, None, ()),
        (ScreenVerdict.WORKING, "codex-wait-unproved", ("screen-working",)),
        (ScreenVerdict.DRAFT, "codex-wait-unproved", ("screen-draft",)),
        (ScreenVerdict.UNSUPPORTED, "codex-wait-unproved", ("screen-unsupported",)),
    ],
)
def test_a_codex_reviewer_needs_a_fresh_idle_empty_capture(probe: ScreenVerdict, reason: str | None, notes: tuple[str, ...]) -> None:
    """Only a supported idle, empty-input capture with no active turn proves that no Codex wait runs."""
    classification, _ = wait(probe)
    verdict = classification.verdict(scope(), Host.CODEX, IDLE, (typed(ENTRY),))
    assert (getattr(verdict.refusal, "reason", None), verdict.notes) == (reason, notes)


@pytest.mark.parametrize(
    ("decision", "reason", "notes"),
    [
        (PROVED, None, ()),
        (PENDING, "claude-wait-unproved", ("ledger-background-start-unmatched", "ledger-turn-open")),
        (None, "claude-ledger-unavailable", ()),
    ],
)
def test_a_claude_reviewer_needs_the_ledger_to_prove_absence(decision: LedgerDecision | None, reason: str | None, notes: tuple[str, ...]) -> None:
    """A running or restarted watcher, an open turn or no pinned ledger keeps a Claude reviewer pending."""
    classification, absence = wait(decision=decision)
    verdict = classification.verdict(scope(Host.CLAUDE), Host.CLAUDE, IDLE, (typed(ENTRY),))
    assert (getattr(verdict.refusal, "reason", None), verdict.notes, absence.scopes) == (reason, notes, [scope(Host.CLAUDE)])


def test_no_pinned_ledger_never_proves_absence() -> None:
    """The default absence port answers no decision, whatever the scope."""
    assert UnprovedAbsence().decide(scope(Host.CLAUDE)) is None


def test_the_history_is_read_through_the_port() -> None:
    """The reviewer history comes from the injected command history."""
    history = FakeHistory({REVIEWER_PANE: (typed(ENTRY),)})
    classification = ReviewerWait(history, FakeProbe(), UnprovedAbsence())
    assert classification.commands(REVIEWER) == (typed(ENTRY),)
