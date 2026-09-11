"""Stable transcript and LLM-nature completion identities.

Step 2 adds an append-only completion form whose role and exchange occurrence
keep both its heading and idempotency marker unique.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.review_exchange_models import ReviewRole

if TYPE_CHECKING:
    from pathlib import Path

    from tools.llm_nature import LlmNature
    from tools.review_exchange_models import ReviewContext
    from tools.review_exchange_store import ReviewExchangeStore


def transcript_entry_base(
    context: ReviewContext,
    role: ReviewRole,
    round_number: int,
) -> str:
    """Return one stable role identity scoped by code-review step when present."""
    prefix = "request" if role is ReviewRole.REQUESTOR else "answer"
    if context.implementation_step is not None:
        return f"{prefix}-step-{context.implementation_step}-round-{round_number}"
    return f"{prefix}-round-{round_number}"


def current_request_occurrence(
    store: ReviewExchangeStore,
    context: ReviewContext,
    round_number: int,
    *,
    before_offset: int | None = None,
) -> int:
    """Return the current restarted-exchange number from request entries."""
    base = transcript_entry_base(context, ReviewRole.REQUESTOR, round_number)
    next_occurrence = store.entry_occurrence(
        base,
        discriminator="exchange",
        before_offset=before_offset,
    )
    return max(1, next_occurrence - 1)


@dataclass(frozen=True)
class NatureCompletionEntry:
    """One append-only identity-completion transcript fragment."""

    entry_id: str
    markdown: str


def render_nature_completion_entry(
    role: ReviewRole,
    exchange_occurrence: int,
    nature: LlmNature,
    artifact_paths: tuple[Path, ...],
) -> NatureCompletionEntry:
    """Render one unique, repeat-safe role identity completion entry."""
    if role is ReviewRole.HUMAN:
        message = "human role has no LLM nature completion"
        raise ValueError(message)
    if exchange_occurrence < 1:
        message = "exchange occurrence must be positive"
        raise ValueError(message)
    entry_id = f"llm-nature-completion-{role.value}-exchange-{exchange_occurrence}"
    paths = "\n".join(f"- `{path.as_posix()}`" for path in artifact_paths)
    markdown = (
        f"\n\n### LLM nature completion for {role.value} "
        f"(exchange {exchange_occurrence})\n\n"
        f"Recorded nature: `{nature.value}`\n\n"
        f"Completed artifacts:\n\n{paths}\n\n"
        f"<!-- review-entry-id: {entry_id} -->\n"
    )
    return NatureCompletionEntry(entry_id, markdown)


__all__ = [
    "NatureCompletionEntry",
    "current_request_occurrence",
    "render_nature_completion_entry",
    "transcript_entry_base",
]


# eof
