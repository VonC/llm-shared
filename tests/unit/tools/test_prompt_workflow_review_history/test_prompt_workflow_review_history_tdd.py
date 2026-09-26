"""Contracts for naming a topic's last review requestor from its transcripts.

Every transcript entry records `- Recorded:` and `- Requestor LLM nature:`.
The latest Claude or Codex requestor across the topic's `review.*` transcripts
wins; unrecorded natures, naive or unreadable timestamps, other topics, and
unparsable names are ignored.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_review_history as history
from tools.llm_nature import LlmNature
from tools.prompt_workflow_models import Topic

if TYPE_CHECKING:
    import pytest

_VERSION = "v10.0.0"
_SLUG = "dex-navigation"


def _entry(recorded: str, requestor: str, role: str = "requestor") -> str:
    """Return one transcript entry with its metadata lines."""
    return (
        f"\n## Round 1 by {role} - Step 3\n\n"
        f"- Recorded: {recorded}\n"
        f"- Exchange: code/code/{_VERSION}/{_SLUG}\n"
        f"- Requestor LLM nature: {requestor}\n"
        "- Reviewer LLM nature: claude\n"
        "- Outcome: request\n"
    )


def _topic(tmp_path: Path) -> Topic:
    docs_dir = tmp_path / "docs" / _VERSION
    docs_dir.mkdir(parents=True)
    draft = docs_dir / f"draft.{_VERSION}.{_SLUG}.md"
    draft.write_text("# Draft\n", encoding="utf-8")
    return Topic(version=_VERSION, slug=_SLUG, draft_path=draft.resolve())


def _write(tmp_path: Path, name: str, *entries: str) -> Path:
    path = tmp_path / "docs" / _VERSION / name
    path.write_text("# Code review transcript\n" + "".join(entries), encoding="utf-8")
    return path


def test_recorded_requestors_keeps_timed_host_entries_only() -> None:
    """Unrecorded natures and naive, bad, or missing timestamps are skipped."""
    text = (
        _entry("2026-09-12T19:40:47+02:00", "codex")
        + _entry("2026-09-12T20:00:00+02:00", "unrecorded")
        + _entry("2026-09-12T21:00:00", "claude")
        + _entry("not a date", "claude")
        + "\n## Round 2 by reviewer\n\n- Requestor LLM nature: claude\n"
        + _entry("2026-09-13T08:00:00+02:00", "claude", role="reviewer")
    )

    assert history.recorded_requestors(text) == [
        (datetime.fromisoformat("2026-09-12T19:40:47+02:00"), LlmNature.CODEX),
        (datetime.fromisoformat("2026-09-13T08:00:00+02:00"), LlmNature.CLAUDE),
    ]


def test_last_requestor_is_the_latest_across_the_topic_transcripts(tmp_path: Path) -> None:
    """A later code round outranks an earlier plan review of the same topic."""
    topic = _topic(tmp_path)
    _write(tmp_path, f"review.plan.{_VERSION}.{_SLUG}.md", _entry("2026-09-10T09:00:00+02:00", "claude"))
    _write(
        tmp_path,
        f"review.code.{_VERSION}.{_SLUG}.md",
        _entry("2026-09-11T09:00:00+02:00", "codex"),
        _entry("2026-09-12T09:00:00+00:00", "codex"),
    )
    _write(tmp_path, f"review.code.{_VERSION}.other.md", _entry("2026-09-20T09:00:00+02:00", "claude"))
    _write(tmp_path, f"review.notes.{_VERSION}.{_SLUG}.md", _entry("2026-09-20T09:00:00+02:00", "claude"))

    assert [path.name for path in history.topic_transcripts(tmp_path, topic)] == [
        f"review.code.{_VERSION}.{_SLUG}.md",
        f"review.plan.{_VERSION}.{_SLUG}.md",
    ]
    assert history.last_requestor_nature(tmp_path, topic) is LlmNature.CODEX


def test_last_requestor_matches_the_slug_across_hyphens_and_underscores(tmp_path: Path) -> None:
    """A transcript written with underscores still belongs to the hyphenated topic."""
    topic = _topic(tmp_path)
    _write(tmp_path, f"review.code.{_VERSION}.dex_navigation.md", _entry("2026-09-11T09:00:00+02:00", "claude"))

    assert history.last_requestor_nature(tmp_path, topic) is LlmNature.CLAUDE


def test_last_requestor_is_none_without_a_recorded_host(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No transcript, only unrecorded natures, or an unreadable file name no one."""
    topic = _topic(tmp_path)
    assert history.last_requestor_nature(tmp_path, topic) is None

    _write(tmp_path, f"review.code.{_VERSION}.{_SLUG}.md", _entry("2026-09-11T09:00:00+02:00", "unrecorded"))
    assert history.last_requestor_nature(tmp_path, topic) is None

    def unreadable(_self: Path, encoding: str = "utf-8") -> str:
        raise OSError(encoding)

    monkeypatch.setattr(Path, "read_text", unreadable)
    assert history.last_requestor_nature(tmp_path, topic) is None


# eof
