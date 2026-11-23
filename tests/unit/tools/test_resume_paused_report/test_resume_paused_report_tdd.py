"""Unit tests of the compact result reporting of resume_paused (Step 8 of v0.14.0 resume-paused).

Plans and deliveries are declared as plain values: preview lines carry the
exact marked command, clear and takeover condition, notes and the Claude
``limits=claude-wait-scope`` code; run lines separate the requestor and
reviewer outcomes with their clear, receiver observation, reason and recovery
use; statuses map to the exit decision; used prompts report their known
resumer and time or ``unknown``; checkouts sharing a folder name are named by
their full paths; run-wide refusals replace every checkout line.

Fix (Step 8 code review round 1): every target names its saved routing and
validation result, a shell slot reads as no LLM counterpart or target, and a
checkout stopped on its routing says no target was validated.

Fix (Step 8 code review round 2): a send refused on a changed identity loses
its validated status in the run line, a target that became a shell before the
send reads as no LLM, and an unrelated refusal keeps the validated identity.

Fix (Step 8 code review round 3): the takeover's pending absent-reviewer
report, produced by its own test case, renders not validated; an unrelated
pending wait keeps the validated identity.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from tests.unit.tools.test_resume_paused_artifacts.test_resume_paused_artifacts_tdd import (
    TITLE,
)
from tests.unit.tools.test_resume_paused_cli.test_resume_paused_cli_tdd import (
    HEAD,
    REQUESTOR,
    REVIEWER,
    ROOT,
    plan,
    planned,
)
from tests.unit.tools.test_resume_paused_routing.test_resume_paused_routing_tdd import (
    REQUESTOR_PANE,
    REVIEWER_PANE,
    SESSION,
)
from tests.unit.tools.test_resume_paused_takeover.takeover_world import (
    TakeoverWorld,
    listing,
)
from tests.unit.tools.test_resume_paused_takeover.test_resume_paused_takeover_tdd import (
    initial,
)
from tools import resume_paused_report as reporting
from tools.resume_paused_artifacts import PromptState
from tools.resume_paused_delivery_model import (
    CLAUDE_WAIT_SCOPE,
    ActionReport,
    CheckoutDelivery,
    ClearOutcome,
    DeliveryOutcome,
    GuardState,
    Phase,
    ReceiverState,
)
from tools.resume_paused_evidence import (
    DuplicateEvidence,
    DuplicateSignal,
    PaneObservation,
)
from tools.resume_paused_models import CanonicalRoot
from tools.resume_paused_plan_model import (
    ActionKind,
    CheckoutOutcome,
    ErrorReason,
    GlobalFailure,
    GlobalReason,
    RunPlan,
    SkipReason,
)


def test_preview_lines_show_clear_takeover_condition_skips_notes_and_claude_limits() -> None:
    """A conditional Claude reviewer carries ``limits=claude-wait-scope``; notes and skips are reported."""
    actions = (
        planned(clear=True, notes=("label-changed",)),
        planned(ActionKind.REVIEWER),
    )
    assert reporting.checkout_line(plan(*actions), None, preview=True) == (
        f"PLAN api: {HEAD}; {REQUESTOR}: clear, then /cmd requestor [label-changed]; "
        f"{REVIEWER}: after takeover, /cmd reviewer [{CLAUDE_WAIT_SCOPE}]"
    )
    skipped = plan(planned(command=None, skip=SkipReason.PANE_BUSY), outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.PANE_BUSY, detail="busy")
    assert reporting.checkout_line(skipped, None, preview=True) == f"SKIP api: {HEAD}; skip pane-busy: busy; {REQUESTOR}: skip pane-busy"
    unknown = plan(planned(command=None), title=None, author=None, paused_at=None, switched=True)
    assert reporting.checkout_line(unknown, None, preview=True) == (
        f"PLAN api: untitled paused by unknown at unknown, prompt unused; roles switched; {REQUESTOR}: skip not-planned"
    )


def test_a_shell_in_a_saved_slot_is_no_llm_and_each_target_names_its_routing_validation() -> None:
    """A non-agent pane is never named by its saved role and host; unvalidated targets give their reason (review round 1)."""
    shell = planned(ActionKind.REVIEWER, command=None, skip=SkipReason.TARGET_NOT_AGENT)
    absent = planned(command=None, skip=SkipReason.TARGET_ABSENT)
    line = reporting.checkout_line(plan(absent, shell, outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.TARGET_ABSENT), None, preview=True)
    assert line == (
        f"SKIP api: {HEAD}; skip target-absent; "
        f"requestor claude {SESSION}/requestor | pane {REQUESTOR_PANE[:8]} (saved routing, not validated: target-absent): skip target-absent; "
        f"no LLM counterpart {SESSION}/reviewer | pane {REVIEWER_PANE[:8]} (saved routing, not validated: target-not-agent): skip target-not-agent"
    )
    assert "reviewer claude" not in line
    report = ActionReport(shell, DeliveryOutcome.REFUSED, "target-not-agent")
    delivered = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(planned(), shell),)), (_delivered(report),))[0][0]
    assert f"no LLM counterpart {SESSION}/reviewer | pane {REVIEWER_PANE[:8]}" in delivered
    alone = planned(command=None, skip=SkipReason.TARGET_NOT_AGENT)
    assert reporting.checkout_line(plan(alone), None, preview=True).endswith(
        f"no LLM target {SESSION}/requestor | pane {REQUESTOR_PANE[:8]} (saved routing, not validated: target-not-agent): skip target-not-agent",
    )


@pytest.mark.parametrize(
    ("reason", "failed"),
    [
        ("target-absent", False),
        ("target-identity-unavailable", False),
        ("target-session-changed", True),
        ("target-host-changed", True),
        ("target-checkout-changed", True),
        ("pane-ambiguous", True),
        ("host-contradictory", True),
    ],
)
def test_a_send_refused_on_a_changed_identity_loses_its_validated_status(reason: str, *, failed: bool) -> None:
    """The delivery's fresh identity verdict outranks the planned one in the run line (review round 2)."""
    report = ActionReport(planned(), DeliveryOutcome.REFUSED, reason, failed=failed)
    line = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(report.action),)), (_delivered(report),))[0][0]
    word = "failed" if failed else "skipped"
    assert line.endswith(f"requestor claude {SESSION}/requestor | pane {REQUESTOR_PANE[:8]} (saved routing, not validated: {reason}): {word}: {reason}")


@pytest.mark.parametrize("slot", [ActionKind.RESUME, ActionKind.REVIEWER])
def test_a_target_that_became_a_shell_before_the_send_is_no_llm(slot: ActionKind) -> None:
    """A planned agent found to be a shell at the send is reported as no LLM target or counterpart, never by its saved role."""
    report = ActionReport(planned(slot), DeliveryOutcome.REFUSED, "target-not-agent")
    line = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(report.action),)), (_delivered(report),))[0][0]
    kind, label, pane = ("target", "requestor", REQUESTOR_PANE) if slot is ActionKind.RESUME else ("counterpart", "reviewer", REVIEWER_PANE)
    assert line.endswith(f"no LLM {kind} {SESSION}/{label} | pane {pane[:8]} (saved routing, not validated: target-not-agent): skipped: target-not-agent")
    assert "claude" not in line.split("; ", 1)[1]


def test_the_takeovers_pending_absent_reviewer_is_not_validated() -> None:
    """The exact report of the takeover's absent-reviewer case renders pending and not validated (review round 3)."""
    world = TakeoverWorld()
    world.transport.observations = [PaneObservation(listing().panes[:1], listing().activity)]
    report, _ = initial(world)
    assert (report.outcome, report.reason) == (DeliveryOutcome.PENDING, "target-absent")
    line = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(report.action),)), (_delivered(report),))[0][0]
    assert line.endswith(f"reviewer codex {report.action.session}/{report.action.label} {REVIEWER_PANE[:8]} (saved routing, not validated: target-absent): pending: target-absent")
    waiting = ActionReport(planned(ActionKind.REVIEWER), DeliveryOutcome.PENDING, "claude-ledger-unavailable")
    unrelated = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(waiting.action),)), (_delivered(waiting),))[0][0]
    assert unrelated.endswith(f"{REVIEWER}: pending: claude-ledger-unavailable")


def test_an_unrelated_refusal_keeps_the_validated_identity() -> None:
    """A busy or excluded pane at the send is no identity failure: the target stays validated."""
    busy = ActionReport(planned(), DeliveryOutcome.REFUSED, "pane-busy")
    line = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(busy.action),)), (_delivered(busy),))[0][0]
    assert line.endswith(f"{REQUESTOR}: skipped: pane-busy")


@pytest.mark.parametrize(
    ("outcome", "reason", "word"),
    [
        (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_UNRESOLVED, "skip"),
        (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_MISSING, "skip"),
        (CheckoutOutcome.SKIPPED, SkipReason.ROUTING_TABLE_ONLY, "skip"),
        (CheckoutOutcome.SKIPPED, SkipReason.PAIRING_AMBIGUOUS, "skip"),
        (CheckoutOutcome.ERROR, ErrorReason.ROUTING_INVALID, "error"),
    ],
)
def test_an_unresolved_routing_names_no_validated_target(outcome: CheckoutOutcome, reason: SkipReason | ErrorReason, word: str) -> None:
    """A checkout stopped on its routing says the routing is unresolved and that no target was validated or typed into."""
    unresolved = plan(outcome=outcome, reason=reason, detail="targets.reviewer: unknown: no pane")
    assert reporting.checkout_line(unresolved, None, preview=True) == (
        f"{'ERROR' if word == 'error' else 'SKIP'} api: {HEAD}; {word} {reason.value}: targets.reviewer: unknown: no pane; "
        "routing unresolved: no target validated or typed into"
    )


def test_used_prompt_evidence_names_the_known_resumer_and_time_or_unknown() -> None:
    """Duplicate evidence reports its signal, detail, short pane and minute, or ``unknown`` (Q08=A)."""
    receipt = DuplicateEvidence(DuplicateSignal.RECEIPT, REQUESTOR_PANE, "chatgpt", datetime.fromisoformat("2026-11-18T07:25:09+01:00"))
    override = DuplicateEvidence(DuplicateSignal.OVERRIDE, None, "author-override question", None)
    used = plan(
        prompt_state=PromptState.USED, outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.ALREADY_USED, duplicates=(receipt, override),
    )
    assert reporting.checkout_line(used, None, preview=False) == (
        f"SKIP api: '{TITLE}' paused by claude at 2026-11-17 17:37, prompt used; skip already-used; "
        f"evidence receipt: chatgpt, pane {REQUESTOR_PANE[:8]}, at 2026-11-18 07:25; "
        "evidence override-pending: author-override question, pane unknown, at unknown"
    )


def test_an_error_checkout_fails_the_run_and_independent_checkouts_still_report() -> None:
    """A classification error is reported with its detail; the run fails while a skip beside it succeeds."""
    error = plan(outcome=CheckoutOutcome.ERROR, reason=ErrorReason.DUPLICATE_UNCERTAIN, detail="command-history-unreadable p")
    skip = plan(root=CanonicalRoot.parse("C:\\work\\web"), outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.EXCLUDED)
    lines, failed = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(error, skip), omitted_panes=3), ())
    assert failed
    assert lines == [
        f"ERROR api: {HEAD}; error duplicate-uncertain: command-history-unreadable p",
        f"SKIP web: {HEAD}; skip excluded",
        "omitted 3 pane(s) without a prompt-bearing target",
    ]


def test_checkouts_sharing_a_folder_name_are_named_by_their_full_paths() -> None:
    """Two reported checkouts named alike in different parents stay distinguishable; a unique folder keeps its short name."""
    first, second = CanonicalRoot.parse("C:\\a\\api"), CanonicalRoot.parse("C:\\b\\API")
    plans = tuple(plan(outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.EXCLUDED, root=root) for root in (first, second, ROOT))
    lines, _ = reporting.render_run(RunPlan(dry_run=True, failures=(), checkouts=plans), ())
    assert [line.split(": ", 1)[0] for line in lines[:3]] == ["SKIP C:\\a\\api", "SKIP C:\\b\\API", "SKIP C:\\work\\api"]
    unique = plan(outcome=CheckoutOutcome.SKIPPED, reason=SkipReason.EXCLUDED, root=CanonicalRoot.parse("C:\\work\\web"))
    assert reporting.render_run(RunPlan(dry_run=True, failures=(), checkouts=(unique,)), ())[0][0].startswith("SKIP web: ")


def _delivered(*reports: ActionReport, guard: GuardState = GuardState.ACQUIRED) -> CheckoutDelivery:
    """Declare the delivery of the default checkout."""
    return CheckoutDelivery(ROOT, guard, reports)


def test_run_lines_separate_requestor_and_reviewer_outcomes() -> None:
    """Accepted with its clear, claim and recovery; a pending Claude reviewer keeps its limits note."""
    resume = ActionReport(
        planned(), DeliveryOutcome.ACCEPTED, clear=ClearOutcome.REDUNDANT, recovery=(Phase.RESUME,),
        notes=("background-shell",), receiver=ReceiverState.CLAIMED, generation=6,
    )
    reviewer = ActionReport(planned(ActionKind.REVIEWER), DeliveryOutcome.PENDING, "claude-ledger-unavailable", notes=(CLAUDE_WAIT_SCOPE,))
    lines, failed = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(resume.action, reviewer.action),), omitted_panes=1), (_delivered(resume, reviewer),))
    assert not failed
    assert lines[0] == (
        f"PENDING api: {HEAD}; {REQUESTOR}: already cleared, accepted, claimed g6, recovery enter [background-shell]; "
        f"{REVIEWER}: pending: claude-ledger-unavailable [{CLAUDE_WAIT_SCOPE}]"
    )


@pytest.mark.parametrize(
    ("report", "status", "text"),
    [
        (ActionReport(planned(), DeliveryOutcome.ACCEPTED, receiver=ReceiverState.CONSUMED), "DONE", "accepted, prompt consumed"),
        (
            ActionReport(planned(), DeliveryOutcome.ACCEPTED, receiver=ReceiverState.COMPLETION_UNCONFIRMED),
            "DONE", "accepted, completion unconfirmed",
        ),
        (
            ActionReport(planned(), DeliveryOutcome.ACCEPTED, "result-failed", failed=True, receiver=ReceiverState.FAILED),
            "FAIL", "accepted, receiver failed: result-failed",
        ),
        (
            ActionReport(planned(), DeliveryOutcome.UNCONFIRMED, "clear-unconfirmed", failed=True, clear=ClearOutcome.UNCONFIRMED),
            "FAIL", "clear unconfirmed, unconfirmed: clear-unconfirmed",
        ),
        (ActionReport(planned(), DeliveryOutcome.REFUSED, "discovery-failed", failed=True), "FAIL", "failed: discovery-failed"),
        (ActionReport(planned(), DeliveryOutcome.REFUSED, "pane-busy", clear=ClearOutcome.CONFIRMED), "SKIP", "cleared, skipped: pane-busy"),
        (ActionReport(planned(), DeliveryOutcome.ACCEPTED, receiver=ReceiverState.CLAIMED), "DONE", "accepted, claimed"),
    ],
)
def test_each_action_outcome_maps_to_its_status_and_words(report: ActionReport, status: str, text: str) -> None:
    """Failures fail the run; accepted work is done; refused expected skips succeed."""
    lines, failed = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(report.action),)), (_delivered(report),))
    assert lines[0] == f"{status} api: {HEAD}; {REQUESTOR}: {text}"
    assert failed is (status == "FAIL")


@pytest.mark.parametrize(("guard", "status"), [(GuardState.HELD, "SKIP"), (GuardState.UNAVAILABLE, "FAIL")])
def test_a_guard_held_elsewhere_skips_and_an_unavailable_guard_fails(guard: GuardState, status: str) -> None:
    """Contention is an expected skip; an unusable guard is a failure; nothing was sent either way."""
    lines, failed = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(planned()),)), (_delivered(guard=guard),))
    assert lines[0] == f"{status} api: {HEAD}; guard {guard.value}; {REQUESTOR}: not sent"
    assert failed is (status == "FAIL")


def test_a_planned_checkout_without_delivery_and_name_refusals_render() -> None:
    """An undelivered planned checkout is a skip; every run-wide refusal gets its own line."""
    lines, failed = reporting.render_run(RunPlan(dry_run=False, failures=(), checkouts=(plan(planned()),), omitted_panes=2), ())
    assert (lines[0], failed) == (f"SKIP api: {HEAD}; {REQUESTOR}: /cmd requestor", False)
    refusals = (GlobalFailure(GlobalReason.EXCEPT_UNMATCHED, ("x",)), GlobalFailure(GlobalReason.DISCOVERY_FAILED))
    assert reporting.render_run(RunPlan(dry_run=True, failures=refusals), ()) == (
        ["REFUSED run: except-unmatched: x; no input sent", "REFUSED run: discovery-failed; no input sent"], True,
    )


# eof
