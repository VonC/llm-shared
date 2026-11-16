"""Clipboard and optional journal coordination, with no real clipboard access."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from tools import copy_conversation as cli
from tools import copy_conversation_journal as journal

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def mission_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], Path, list[str]]:
    """Prepare one synthetic conversation and a temporary configured mission."""
    root = tmp_path / "202401-MiXeD"
    root.mkdir()
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(json.dumps({"type": "event_msg", "payload": {
        "type": "user_message", "message": "20261115 hello",
    }}) + "\n", encoding="utf-8")
    monkeypatch.setenv("JOURNAL_MISSION", str(root))
    monkeypatch.setattr(journal, "local_now", lambda: datetime(2026, 11, 16, 5, 59, tzinfo=UTC))
    copied: list[str] = []
    monkeypatch.setattr(cli, "set_clipboard_text", copied.append)
    args = ["codex", "20261115", "--transcript", str(transcript), "--title", "Example"]
    return args, root / "202611/mixed20261115.txt", copied


def test_cli_appends_exact_copied_text_and_reports_path(
    mission_copy: tuple[list[str], Path, list[str]], capsys: pytest.CaptureFixture[str],
) -> None:
    """One invocation copies once and journals the same text with its separator."""
    args, path, copied = mission_copy
    assert cli.main(args) == 0
    assert copied == ["Example:\n\n20261115 hello"]
    assert path.read_bytes() == copied[0].encode() + b"\n~~~~~~~~~~~~~~~~\n"
    summary = capsys.readouterr().out
    assert f"Mission folder: {path.parent.parent}." in summary
    assert f"Appended to: {path}." in summary


def test_no_clipboard_also_disables_journaling(
    mission_copy: tuple[list[str], Path, list[str]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Export-only calls ignore even an invalid mission setting."""
    args, path, copied = mission_copy
    monkeypatch.setenv("JOURNAL_MISSION", "invalid")
    output = path.parent.parent / "export.txt"
    assert cli.main([*args, "--no-clipboard", "--output", str(output)]) == 0
    assert output.read_text(encoding="utf-8") == "Example:\n\n20261115 hello"
    assert not copied
    assert not path.parent.exists()


def test_clipboard_failure_never_appends(
    mission_copy: tuple[list[str], Path, list[str]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The daily file is untouched if publishing the clipboard fails."""
    args, path, _ = mission_copy

    def fail(_text: str) -> None:
        msg = "clipboard busy"
        raise cli.CopyConversationError(msg)

    monkeypatch.setattr(cli, "set_clipboard_text", fail)
    with pytest.raises(cli.CopyConversationError, match="clipboard busy"):
        cli.main(args)
    assert not path.parent.exists()


@pytest.mark.parametrize("failure", [OSError("disk full"), journal.JournalError("lock timeout")])
def test_append_failure_reports_clipboard_success(
    mission_copy: tuple[list[str], Path, list[str]], monkeypatch: pytest.MonkeyPatch, failure: Exception,
) -> None:
    """A partial operation is reported explicitly and never retried."""
    args, path, copied = mission_copy
    attempts: list[Path] = []

    def fail(destination: Path, _text: str) -> None:
        attempts.append(destination)
        raise failure

    monkeypatch.setattr(cli, "append_journal", fail)
    with pytest.raises(cli.CopyConversationError, match="Clipboard ready; mission journal append failed"):
        cli.main(args)
    assert len(copied) == 1
    assert attempts == [path]


def test_export_alias_is_refused_before_any_publication(
    mission_copy: tuple[list[str], Path, list[str]],
) -> None:
    """--output cannot truncate an existing journal, even before append starts."""
    args, path, copied = mission_copy
    path.parent.mkdir()
    path.write_bytes(b"old")
    with pytest.raises(journal.JournalError, match="must not overwrite"):
        cli.main([*args, "--output", str(path)])
    assert not copied
    assert path.read_bytes() == b"old"


# eof
