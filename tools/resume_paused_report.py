"""Compact result reporting of the human-only bulk resume.

Step 8 of v0.14.0 resume-paused renders one launch's plan and deliveries
(design, "Reporting and exit semantics") as text, kept apart from argument
parsing and composition (``tools.resume_paused``):

- one compact line per prompt-bearing checkout, used prompts included,
  starting with its status: ``PLAN`` (dry run), ``DONE``, ``PENDING`` (a
  reviewer waits), ``SKIP`` (expected skip, a guard held elsewhere
  included), ``ERROR`` (classification failure) or ``FAIL`` (execution
  failure); a checkout is named by its folder, or by its full path when
  another reported checkout has the same folder name;
- then its title, pausing agent and time, prompt state, the reason of a skip
  or error, a switch, and the duplicate-resume evidence with its known
  resumer and time or ``unknown`` (Q08=A);
- then each target's role, host, TUIOS session, label and short pane id, with
  the intended marked command, clear and takeover condition in a preview, or
  its clear, outcome, receiver observation, reason and recovery use after a
  delivery, so the requestor and reviewer outcomes stay separate; report-only
  notes, ``limits=claude-wait-scope`` of every Claude reviewer outcome and
  conditional Claude preview included, follow in brackets;
- a run-wide refusal replaces every checkout line; otherwise a last line
  counts the panes that no reported checkout targets.

``render_run`` also returns whether the run failed: a run-wide refusal, a
checkout classification error or a failed delivery. Nothing here reads or
writes anything.

Fix (Step 8 code review round 1): each target also names its routing source
and validation result, ``(saved routing, validated)`` or ``(saved routing, not
validated: <reason>)``, and a checkout skipped or failed on its routing says
that its routing is unresolved and no target was validated or typed into. A
saved slot whose live pane runs no agent reads ``no LLM counterpart`` (or
``no LLM target``), never as the saved role and host: a shell is never
reported as a reviewer.

Fix (Step 8 code review round 2): after a delivery, a send refused because
the fresh listing no longer validated the target's identity (absent, a shell,
another session, host or checkout, ambiguous or contradictory) reports that
failure instead of the planned ``validated``, and a target that became a
shell reads as no LLM counterpart or target; other refusals, such as a busy
pane, keep the validated identity.

Fix (Step 8 code review round 3): a reviewer the takeover leaves pending
because its fresh listing lacks the pane (``pending: target-absent``) loses
its validated status the same way; a pending wait unrelated to the target's
identity keeps it.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Final

from tools.resume_paused_delivery_model import (
    ClearOutcome,
    DeliveryOutcome,
    ReceiverState,
)
from tools.resume_paused_models import timestamp_instant
from tools.resume_paused_plan_model import (
    CheckoutOutcome,
    ErrorReason,
    GlobalReason,
    SkipReason,
)
from tools.resume_paused_takeover import preview_notes

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from tools.resume_paused_delivery_model import ActionReport, CheckoutDelivery
    from tools.resume_paused_models import CanonicalRoot
    from tools.resume_paused_plan_model import (
        CheckoutPlan,
        GlobalFailure,
        PlannedAction,
        RunPlan,
    )

_SHORT_ID: Final = 8
_OUTCOME_STATUS: Final = {CheckoutOutcome.SKIPPED: "SKIP", CheckoutOutcome.ERROR: "ERROR"}
_DELIVERED_STATUS: Final = ((DeliveryOutcome.PENDING, "PENDING"), (DeliveryOutcome.ACCEPTED, "DONE"))
_CLEAR_WORDS: Final = {
    ClearOutcome.NONE: "",
    ClearOutcome.REDUNDANT: "already cleared, ",
    ClearOutcome.CONFIRMED: "cleared, ",
    ClearOutcome.UNCONFIRMED: "clear unconfirmed, ",
}
_RECEIVER_WORDS: Final = {
    ReceiverState.UNOBSERVED: "",
    ReceiverState.CONSUMED: ", prompt consumed",
    ReceiverState.CLAIMED: ", claimed",
    ReceiverState.COMPLETION_UNCONFIRMED: ", completion unconfirmed",
    ReceiverState.FAILED: ", receiver failed",
}
_OUTCOME_WORDS: Final = {
    DeliveryOutcome.ACCEPTED: "accepted",
    DeliveryOutcome.PENDING: "pending",
    DeliveryOutcome.UNCONFIRMED: "unconfirmed",
    DeliveryOutcome.REFUSED: "skipped",
}
_UNVALIDATED: Final = frozenset({SkipReason.TARGET_ABSENT, SkipReason.TARGET_NOT_AGENT, SkipReason.TARGET_IDENTITY_UNAVAILABLE})
# Outcomes whose reason may be the target's live identity failure: a refused send, or a reviewer the takeover left pending.
_UNSENT: Final = frozenset({DeliveryOutcome.REFUSED, DeliveryOutcome.PENDING})
# The identity refusals of the delivery's fresh pre-send check (``tools.resume_paused_delivery_checks``) and the
# takeover's pending ``target-absent`` gate (``tools.resume_paused_takeover``).
_IDENTITY_REFUSALS: Final = frozenset({
    "target-absent", "pane-ambiguous", "target-session-changed", "host-contradictory", "target-not-agent",
    "target-host-changed", "target-identity-unavailable", "target-checkout-changed",
})
_ROUTING_REASONS: Final = frozenset({
    SkipReason.ROUTING_MISSING, SkipReason.ROUTING_TABLE_ONLY, SkipReason.ROUTING_UNRESOLVED, SkipReason.PAIRING_AMBIGUOUS,
    ErrorReason.ROUTING_INVALID,
})


def _moment(moment: datetime | None) -> str:
    """Render a known instant to the minute in its own offset, or ``unknown``."""
    return "unknown" if moment is None else moment.strftime("%Y-%m-%d %H:%M")


def _folder(root: CanonicalRoot) -> str:
    """Return the checkout folder name as discovered."""
    return root.display.rsplit("\\", 1)[-1]


def _with_notes(text: str, notes: Sequence[str]) -> str:
    """Append report-only notes, ``limits=claude-wait-scope`` included, in brackets."""
    return f"{text} [{', '.join(notes)}]" if notes else text


def _identity_failure(action: PlannedAction, live: str | None) -> str | None:
    """Return why the target's identity failed validation: at planning, else at the send, ``None`` when it held."""
    skip = action.skip
    if skip is not None and skip in _UNVALIDATED:
        return skip.value
    return live if live in _IDENTITY_REFUSALS else None


def _target(action: PlannedAction, live: str | None = None) -> str:
    """Name one target: its role and host, TUIOS session, label and short pane id, then its routing source and validation.

    ``live`` is the reason a delivery refused the send, which outranks the
    planned identity when the fresh listing no longer validated the target. A
    saved slot whose live pane runs no agent is named ``no LLM counterpart``
    (or ``no LLM target`` for the resumed slot), never by its saved role and
    host, so a shell is never reported as a reviewer.
    """
    where = f"{action.session}/{action.label} {action.pane_id[:_SHORT_ID]}"
    failure = _identity_failure(action, live)
    if failure == SkipReason.TARGET_NOT_AGENT.value:
        identity = f"no LLM {'counterpart' if action.conditional else 'target'} {where}"
    else:
        identity = f"{action.role.value} {action.host.value} {where}"
    validation = "validated" if failure is None else f"not validated: {failure}"
    return f"{identity} (saved routing, {validation})"


def _planned(action: PlannedAction) -> str:
    """Render one action as a preview: its exact marked command, its clear and its takeover condition, or its skip."""
    if action.command is None:
        text = f"skip {action.skip.value if action.skip else 'not-planned'}"
    else:
        prefix = "after takeover, " if action.conditional else ("clear, then " if action.clear else "")
        text = prefix + action.command
    return _with_notes(f"{_target(action)}: {text}", (*action.notes, *preview_notes(action)))


def _reported(report: ActionReport) -> str:
    """Render one action's run outcome: clear, outcome, receiver observation, reason and recovery use."""
    word = "failed" if report.failed and report.outcome is DeliveryOutcome.REFUSED else _OUTCOME_WORDS[report.outcome]
    receiver = _RECEIVER_WORDS[report.receiver]
    if report.receiver is ReceiverState.CLAIMED and report.generation is not None:
        receiver += f" g{report.generation}"
    reason = f": {report.reason}" if report.reason else ""
    recovery = ", recovery enter" if report.recovery else ""
    text = f"{_CLEAR_WORDS[report.clear]}{word}{receiver}{reason}{recovery}"
    live = report.reason if report.outcome in _UNSENT else None
    return _with_notes(f"{_target(report.action, live)}: {text}", report.notes)


def _pause(plan: CheckoutPlan) -> str:
    """Render the saved pause: title, pausing agent and time, prompt state."""
    title = "untitled" if plan.title is None else f"'{plan.title}'"
    paused = None if plan.paused_at is None else timestamp_instant(plan.paused_at)
    return f"{title} paused by {plan.author or 'unknown'} at {_moment(paused)}, prompt {plan.prompt_state.value}"


def _verdict(plan: CheckoutPlan) -> list[str]:
    """Render the checkout's skip or error reason, its switch and its duplicate-resume evidence."""
    parts: list[str] = []
    if plan.reason is not None:
        word = "error" if plan.outcome is CheckoutOutcome.ERROR else "skip"
        parts.append(f"{word} {plan.reason.value}" + (f": {plan.detail}" if plan.detail else ""))
    if plan.reason in _ROUTING_REASONS:
        parts.append("routing unresolved: no target validated or typed into")
    if plan.switched:
        parts.append("roles switched")
    for item in plan.duplicates:
        pane = item.pane_id[:_SHORT_ID] if item.pane_id else "unknown"
        parts.append(f"evidence {item.signal.value}: {item.detail}, pane {pane}, at {_moment(item.at)}")
    return parts


def _status(plan: CheckoutPlan, delivery: CheckoutDelivery | None, *, preview: bool) -> str:
    """Return the checkout's status word: PLAN, DONE, PENDING, SKIP, ERROR or FAIL."""
    if plan.outcome is not CheckoutOutcome.PLANNED:
        return _OUTCOME_STATUS[plan.outcome]
    if preview:
        return "PLAN"
    if delivery is None:
        return "SKIP"
    if delivery.failed:
        return "FAIL"
    outcomes = {report.outcome for report in delivery.reports}
    return next((status for outcome, status in _DELIVERED_STATUS if outcome in outcomes), "SKIP")


def _actions(plan: CheckoutPlan, delivery: CheckoutDelivery | None, *, preview: bool) -> list[str]:
    """Render each target: planned in a preview or a skipped checkout, reported after a delivery."""
    if preview or delivery is None or plan.outcome is not CheckoutOutcome.PLANNED:
        return [_planned(action) for action in plan.actions]
    if not delivery.reports:
        return [f"guard {delivery.guard.value}", *(f"{_target(action)}: not sent" for action in plan.actions)]
    return [_reported(report) for report in delivery.reports]


def checkout_line(plan: CheckoutPlan, delivery: CheckoutDelivery | None, *, preview: bool, name: str | None = None) -> str:
    """Render one prompt-bearing checkout's compact line, named by its folder unless another name is given."""
    status = _status(plan, delivery, preview=preview)
    parts = [_pause(plan), *_verdict(plan), *_actions(plan, delivery, preview=preview)]
    return f"{status} {name or _folder(plan.root)}: " + "; ".join(parts)


def _checkout_names(checkouts: Sequence[CheckoutPlan]) -> dict[CanonicalRoot, str]:
    """Name each reported checkout by its folder, or by its full path when another reported folder has the same name."""
    folders = Counter(_folder(checkout.root).casefold() for checkout in checkouts)
    return {
        checkout.root: checkout.root.display if folders[_folder(checkout.root).casefold()] > 1 else _folder(checkout.root)
        for checkout in checkouts
    }


def _global(failure: GlobalFailure) -> str:
    """Render one run-wide refusal: no input anywhere."""
    names = f": {', '.join(failure.names)}" if failure.names else ""
    human = " (human-only command: agents must not run it)" if failure.reason is GlobalReason.AGENT_CALLER else ""
    return f"REFUSED run: {failure.reason.value}{names}{human}; no input sent"


def render_run(plan: RunPlan, deliveries: Sequence[CheckoutDelivery]) -> tuple[list[str], bool]:
    """Render every checkout line and the omitted-pane count; return them with whether the run failed."""
    if plan.failures:
        return [_global(failure) for failure in plan.failures], True
    by_root = {delivery.root: delivery for delivery in deliveries}
    names = _checkout_names(plan.checkouts)
    lines = [
        checkout_line(checkout, by_root.get(checkout.root), preview=plan.dry_run, name=names[checkout.root]) for checkout in plan.checkouts
    ]
    omitted = f"omitted {plan.omitted_panes} pane(s) without a prompt-bearing target"
    lines.append(f"{omitted}; dry run, nothing typed" if plan.dry_run else omitted)
    return lines, plan.failed or any(delivery.failed for delivery in deliveries)


__all__ = [
    "checkout_line",
    "render_run",
]


# eof
