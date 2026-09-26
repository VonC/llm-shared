"""Condense the repository review status (`rwst`) into `pw progress` lines.

`rvw_status` (alias `rwst`) reports every active review exchange in full. This
module runs the same collection and keeps one line per exchange: the round,
what is reviewed (a plan step, or the specification document type), and whose
move it is, with that role's recorded LLM nature, for instance
`round 2 for step 3: wait for code reviewer (codex) response`.

Fix: the same collection also names the current topic's requestor, the code or
document writer, when its active exchanges agree on one Claude or Codex nature,
so `pw progress` can render its `next` command for that host.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Final

from tools.llm_nature import LlmNature
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
_HOST_NATURES: Final[frozenset[LlmNature]] = frozenset({LlmNature.CLAUDE, LlmNature.CODEX})


@dataclass(frozen=True)
class ReviewReport:
    """The condensed review lines and the current topic's requestor nature.

    Attributes:
        lines: The condensed lines of `condense`.
        requestor: The one Claude or Codex requestor of the topic's active
            exchanges, or None when there is none or it is not clear.
    """

    lines: tuple[str, ...]
    requestor: LlmNature | None


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


def requestor_nature(result: ReviewStatusResult, topic_slug: str | None) -> LlmNature | None:
    """Return the requestor nature the current topic's active exchanges agree on.

    Args:
        result: The collected repository review status.
        topic_slug: The current topic slug; exchanges of other topics are ignored.

    Returns:
        `claude` or `codex` when every active exchange of the topic records that
        same requestor, otherwise None: no exchange, no resolved topic, an
        unrecorded, conflicting, or other nature, or requestors that disagree.
    """
    natures = {
        entry.requestor_llm_nature.value
        for entry in result.exchanges
        if isinstance(entry, ExchangeStatus) and entry.identity.slug == topic_slug
    }
    if topic_slug is None or len(natures) != 1:
        return None
    (nature,) = natures
    return nature if isinstance(nature, LlmNature) and nature in _HOST_NATURES else None


def review_report(root: Path, topic_slug: str | None) -> ReviewReport:
    """Collect the review status as `rwst` does, once, and report it.

    The collection runs the same bounded migration preflight as `rwst`.

    Args:
        root: The project root.
        topic_slug: The current topic slug, or None without a resolved topic.

    Returns:
        The condensed lines and the topic's requestor nature.
    """
    result = collect_review_status(root, lambda: datetime.now().astimezone())
    return ReviewReport(
        tuple(condense(result, topic_slug)),
        requestor_nature(result, topic_slug),
    )


def review_lines(root: Path, topic_slug: str | None) -> list[str]:
    """Collect the review status as `rwst` does and return its condensed lines.

    Args:
        root: The project root.
        topic_slug: The current topic slug, or None without a resolved topic.

    Returns:
        The condensed lines of `condense`.
    """
    return list(review_report(root, topic_slug).lines)


# eof
