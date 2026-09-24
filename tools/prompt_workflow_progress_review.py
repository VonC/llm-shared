"""Condense the repository review status (`rwst`) into `pw progress` lines.

`rvw_status` (alias `rwst`) reports every active review exchange in full. This
module runs the same collection and keeps one line per exchange: the round,
what is reviewed (a plan step, or the specification document type), and whose
move it is, with that role's recorded LLM nature, for instance
`round 2 for step 3: wait for code reviewer (codex) response`.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Final

from tools.review_exchange_models import ReviewFamily, ReviewRole
from tools.review_status import collect_review_status
from tools.review_status_models import (
    ExchangeStatus,
    NextAction,
    ReviewStatusOutcome,
    ReviewStatusResult,
)

if TYPE_CHECKING:
    from pathlib import Path

NO_REVIEW: Final[str] = "no review in progress"
_FAMILY_WORD: Final[dict[ReviewFamily, str]] = {
    ReviewFamily.CODE: "code",
    ReviewFamily.SPECIFICATION: "spec",
}
_OWNING_LABEL: Final[dict[ReviewFamily, str]] = {
    ReviewFamily.CODE: "Commit",
    ReviewFamily.SPECIFICATION: "Consolidate",
}
_ANOTHER_ROUND_LABEL: Final[dict[ReviewFamily, str]] = {
    ReviewFamily.CODE: "Rework and review again",
    ReviewFamily.SPECIFICATION: "Revise and review again",
}
_COUNTERPART_ACTIONS: Final[frozenset[NextAction]] = frozenset(
    {NextAction.WAIT_FOR_COUNTERPART, NextAction.REQUESTOR_WORK, NextAction.REVIEWER_WORK},
)


def _subject(exchange: ExchangeStatus, topic_slug: str | None) -> str:
    """Return `round N for <step or document type>`, naming another topic's slug."""
    identity = exchange.identity
    if identity.family is ReviewFamily.CODE and exchange.implementation_step:
        reviewed = f"step {exchange.implementation_step}"
    else:
        reviewed = identity.type_token
    other = "" if identity.slug == topic_slug else f" of {identity.slug}"
    return f"round {exchange.round_number} for {reviewed}{other}"


def _wait(exchange: ExchangeStatus) -> str:
    """Return whose move the exchange waits for, or the action it needs."""
    family = _FAMILY_WORD[exchange.identity.family]
    requestor = f"{family} requestor ({exchange.requestor_llm_nature.value.value})"
    reviewer = f"{family} reviewer ({exchange.reviewer_llm_nature.value.value})"
    action = exchange.next_action
    owning = _OWNING_LABEL[exchange.identity.family]
    if action is NextAction.HUMAN_CONFIRMATION:
        another = _ANOTHER_ROUND_LABEL[exchange.identity.family]
        return f"wait for the human choice: {owning}, or {another}"
    if action is NextAction.AUTHORIZED_OWNING_WORK:
        return f"wait for {requestor} to finish the authorized {owning}"
    if action in _COUNTERPART_ACTIONS:
        if exchange.continuing_role is ReviewRole.REVIEWER:
            return f"wait for {reviewer} response"
        return f"wait for {requestor} update"
    return f"{action.value}: {exchange.next_action_text}"


def condense(result: ReviewStatusResult, topic_slug: str | None) -> list[str]:
    """Return one condensed line per active exchange, or one status line.

    Args:
        result: The collected repository review status.
        topic_slug: The current topic slug; exchanges of other topics name theirs.

    Returns:
        `no review in progress`, one line per exchange, a damaged-candidate
        count, or the unavailable status with its migration diagnostics.
    """
    if result.outcome is ReviewStatusOutcome.OPERATIONAL_FAILURE:
        details = "; ".join(result.migration.diagnostics) or "no diagnostic"
        return [f"review status unavailable (run rwst): {details}"]
    exchanges = [entry for entry in result.exchanges if isinstance(entry, ExchangeStatus)]
    lines = [f"{_subject(entry, topic_slug)}: {_wait(entry)}" for entry in exchanges]
    damaged = len(result.exchanges) - len(exchanges)
    if damaged:
        lines.append(f"{damaged} damaged review candidate(s), run rwst for details")
    return lines or [NO_REVIEW]


def review_lines(root: Path, topic_slug: str | None) -> list[str]:
    """Collect the review status as `rwst` does and return its condensed lines.

    The collection runs the same bounded migration preflight as `rwst`.

    Args:
        root: The project root.
        topic_slug: The current topic slug, or None without a resolved topic.

    Returns:
        The condensed lines of `condense`.
    """
    result = collect_review_status(root, lambda: datetime.now().astimezone())
    return condense(result, topic_slug)


# eof
