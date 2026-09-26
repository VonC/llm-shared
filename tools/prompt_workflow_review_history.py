"""Name the last recorded review requestor of a topic from its transcripts.

A completed review exchange removes its coordination record, so `rwst` then
reports `no review in progress` and no longer knows who wrote the reviewed
code or document. The committed transcripts keep that answer: every request
and answer entry of `review.<type>.<version>.<slug>.md`, next to the reviewed
document, records a `- Recorded:` timestamp and a `- Requestor LLM nature:`
line. The most recently recorded Claude or Codex requestor across the topic's
transcripts is the writer `pw progress` names on its `next` line.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Final

from tools import prompt_workflow_docs as docs
from tools.llm_nature import LlmNature
from tools.prompt_workflow_post_commit import slug_key
from tools.review_exchange_models import ReviewExchangeError
from tools.review_exchange_paths import parse_transcript_identity

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prompt_workflow_models import Topic

_RECORDED_PREFIX: Final[str] = "- Recorded: "
_REQUESTOR_PREFIX: Final[str] = "- Requestor LLM nature: "
_HOST_NATURES: Final[dict[str, LlmNature]] = {
    LlmNature.CLAUDE.value: LlmNature.CLAUDE,
    LlmNature.CODEX.value: LlmNature.CODEX,
}


def _aware_timestamp(value: str) -> datetime | None:
    """Return an offset-carrying timestamp, or None so entries stay comparable."""
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def recorded_requestors(text: str) -> list[tuple[datetime, LlmNature]]:
    """Return each entry's recording time and Claude or Codex requestor.

    Args:
        text: One review transcript.

    Returns:
        `(recorded_at, nature)` pairs in document order. Entries whose
        requestor is unrecorded or another nature, or whose timestamp is
        missing, unreadable, or without an offset, are skipped.
    """
    requestors: list[tuple[datetime, LlmNature]] = []
    recorded: datetime | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            recorded = None
        elif line.startswith(_RECORDED_PREFIX):
            recorded = _aware_timestamp(line.removeprefix(_RECORDED_PREFIX).strip())
        elif line.startswith(_REQUESTOR_PREFIX) and recorded is not None:
            nature = _HOST_NATURES.get(line.removeprefix(_REQUESTOR_PREFIX).strip())
            if nature is not None:
                requestors.append((recorded, nature))
    return requestors


def topic_transcripts(root: Path, topic: Topic) -> list[Path]:
    """Return the review transcripts of the topic, any reviewed document type."""
    key = slug_key(topic.slug)
    transcripts: list[Path] = []
    for directory in docs.docs_dirs_for_version(root, topic.version):
        for entry in sorted(directory.glob(f"review.*.{topic.version}.*.md")):
            try:
                identity = parse_transcript_identity(entry)
            except ReviewExchangeError:
                continue
            if identity.version == topic.version and slug_key(identity.slug) == key:
                transcripts.append(entry)
    return transcripts


def last_requestor_nature(root: Path, topic: Topic) -> LlmNature | None:
    """Return the most recently recorded Claude or Codex requestor of the topic.

    Args:
        root: The project root.
        topic: The resolved topic.

    Returns:
        The requestor nature of the latest transcript entry naming one, or None
        when no transcript of the topic records a Claude or Codex requestor.
        An unreadable transcript is skipped: this lookup only labels a command.
    """
    requestors: list[tuple[datetime, LlmNature]] = []
    for transcript in topic_transcripts(root, topic):
        try:
            requestors.extend(recorded_requestors(transcript.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
    if not requestors:
        return None
    return max(requestors, key=lambda pair: pair[0])[1]


# eof
