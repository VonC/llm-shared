"""Stable transcript and LLM-nature completion identities.

Step 2 adds an append-only completion form whose role and exchange occurrence
keep both its heading and idempotency marker unique.

Fix: given the project root, the completion entry lists each completed artifact
relative to it, so the tracked transcript never records the host's absolute
folder; an artifact outside the root is rejected.
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


def _artifact_path(path: Path, project_root: Path | None) -> str:
    """Render one completed artifact path, relative to the project root when it is known."""
    if project_root is None:
        return path.as_posix()
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as error:
        message = "completed artifact is outside the project root"
        raise ValueError(message) from error


def render_nature_completion_entry(
    role: ReviewRole,
    exchange_occurrence: int,
    nature: LlmNature,
    artifact_paths: tuple[Path, ...],
    *,
    project_root: Path | None = None,
) -> NatureCompletionEntry:
    """Render one unique, repeat-safe role identity completion entry.

    Args:
        role: The LLM role whose nature the entry completes.
        exchange_occurrence: The positive exchange occurrence of the entry.
        nature: The recorded LLM nature.
        artifact_paths: The artifacts the completion changed.
        project_root: When given, each artifact path is written relative to it.
    """
    if role is ReviewRole.HUMAN:
        message = "human role has no LLM nature completion"
        raise ValueError(message)
    if exchange_occurrence < 1:
        message = "exchange occurrence must be positive"
        raise ValueError(message)
    entry_id = f"llm-nature-completion-{role.value}-exchange-{exchange_occurrence}"
    paths = "\n".join(f"- `{_artifact_path(path, project_root)}`" for path in artifact_paths)
    markdown = (
        f"\n\n### LLM nature completion for {role.value} "
        f"(exchange {exchange_occurrence})\n\n"
        f"Recorded nature: `{nature.value}`\n\n"
        f"Completed artifacts:\n\n{paths}\n\n"
        f"<!-- review-entry-id: {entry_id} -->\n"
    )
    return NatureCompletionEntry(entry_id, markdown)


def render_nature_override_entry(
    role: ReviewRole,
    exchange_occurrence: int,
    previous: LlmNature,
    nature: LlmNature,
) -> NatureCompletionEntry:
    """Render one repeat-safe entry for a human-approved role nature replacement.

    The entry keeps the replaced nature visible: earlier rounds stay credited
    to it, and only the coordination record names the new nature.
    """
    if role is ReviewRole.HUMAN:
        message = "human role has no LLM nature override"
        raise ValueError(message)
    if exchange_occurrence < 1:
        message = "exchange occurrence must be positive"
        raise ValueError(message)
    entry_id = (
        f"llm-nature-override-{role.value}-exchange-{exchange_occurrence}"
        f"-{previous.value}-to-{nature.value}"
    )
    markdown = (
        f"\n\n### LLM nature override for {role.value} "
        f"(exchange {exchange_occurrence})\n\n"
        f"Human-approved Override: the {role.value} continues as "
        f"`{nature.value}` instead of `{previous.value}`.\n\n"
        f"Previous nature: `{previous.value}`\n\n"
        f"Recorded nature: `{nature.value}`\n\n"
        f"<!-- review-entry-id: {entry_id} -->\n"
    )
    return NatureCompletionEntry(entry_id, markdown)


__all__ = [
    "NatureCompletionEntry",
    "current_request_occurrence",
    "render_nature_completion_entry",
    "render_nature_override_entry",
    "transcript_entry_base",
]


# eof
