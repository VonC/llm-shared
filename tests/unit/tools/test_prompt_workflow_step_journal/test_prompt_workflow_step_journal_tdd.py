"""Contracts for the code writer's private step notes and `pw step-journal`.

Each plan step owns `a.<slug>.step<x>.journal.md` and
`a.<slug>.step<x>.handoff.md` in the review artifact home, plus temporary
`a.<slug>.step<x>.tmp.*` files. A missing journal means the step is starting,
a present one that it is resuming. The command prepares the ignored home and
prints the state and paths; `pw progress` only reads.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_step_journal as step_journal
from tools.prompt_workflow_models import Topic
from tools.review_exchange_models import ReviewExchangeError

if TYPE_CHECKING:
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

_SLUG = "dex-navigation"


def _topic(tmp_path: Path) -> Topic:
    return Topic(version="v10.0.0", slug=_SLUG, draft_path=tmp_path / "draft.md")


def _stub_topic(monkeypatch: pytest.MonkeyPatch, topic: Topic | None) -> None:
    monkeypatch.setattr(step_journal.git, "current_branch", lambda _root: "dex-navigation")
    monkeypatch.setattr(step_journal.memory, "read_memory", lambda _root: None)
    monkeypatch.setattr(step_journal.handoff, "resolve_current_topic", lambda *_a: topic)


def test_step_notes_name_every_file_in_the_artifact_home(tmp_path: Path) -> None:
    """The default home is `.reviews`; the step id is kept as written."""
    notes = step_journal.step_notes(tmp_path, _SLUG, "3b")
    home = tmp_path.resolve() / ".reviews"

    assert notes.home == home
    assert notes.stem == f"a.{_SLUG}.step3b"
    assert notes.journal == home / f"a.{_SLUG}.step3b.journal.md"
    assert notes.handoff == home / f"a.{_SLUG}.step3b.handoff.md"
    assert notes.tmp_pattern == home / f"a.{_SLUG}.step3b.tmp.*"
    assert not notes.resuming


def test_step_notes_follow_a_declared_home_and_reject_bad_step_ids(tmp_path: Path) -> None:
    """A declared home wins; an empty or path-like step id cannot name a note."""
    (tmp_path / ".review-artifacts.ini").write_text(
        "[review-artifacts]\nhome = .private-reviews\n", encoding="utf-8",
    )

    assert step_journal.step_notes(tmp_path, _SLUG, "4.2").home == (
        tmp_path.resolve() / ".private-reviews"
    )
    for step in ("", "../3", "3 b", ".3"):
        with pytest.raises(step_journal.StepJournalError):
            step_journal.step_notes(tmp_path, _SLUG, step)


def test_existing_journal_is_read_only_and_tolerant(tmp_path: Path) -> None:
    """No journal, a bad step id, or a bad declaration all read as no journal."""
    assert step_journal.existing_journal(tmp_path, _SLUG, "3") is None
    assert not (tmp_path / ".reviews").exists()

    journal = tmp_path / ".reviews" / f"a.{_SLUG}.step3.journal.md"
    journal.parent.mkdir()
    journal.write_text("# journal\n", encoding="utf-8")

    assert step_journal.existing_journal(tmp_path, _SLUG, "3") == journal.resolve()
    assert step_journal.existing_journal(tmp_path, _SLUG, "") is None

    (tmp_path / ".review-artifacts.ini").write_text("not an ini\n", encoding="utf-8")
    assert step_journal.existing_journal(tmp_path, _SLUG, "3") is None


def test_render_notes_reports_start_then_resume(tmp_path: Path) -> None:
    """The report is aligned like `pw progress` and flips once the journal exists."""
    notes = step_journal.step_notes(tmp_path, _SLUG, "5")
    home = notes.home

    assert step_journal.render_notes(notes) == (
        "state     start\n"
        f"journal   {home / f'a.{_SLUG}.step5.journal.md'}\n"
        f"handoff   {home / f'a.{_SLUG}.step5.handoff.md'}\n"
        f"tmp       {home / f'a.{_SLUG}.step5.tmp.*'}\n"
    )

    home.mkdir()
    notes.journal.write_text("# journal\n", encoding="utf-8")
    assert step_journal.render_notes(notes).startswith("state     resume\n")


def test_run_step_journal_prepares_the_ignored_home_and_prints(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """The command creates `.reviews` with its `*` ignore file, then reports."""
    _stub_topic(monkeypatch, _topic(tmp_path))

    assert step_journal.run_step_journal(tmp_path, "2") == step_journal.EXIT_OK
    assert (tmp_path / ".reviews" / ".gitignore").read_bytes() == b"*\n"
    assert capsys.readouterr().out.startswith("state     start\njournal   ")

    assert step_journal.run_step_journal(tmp_path, "2") == step_journal.EXIT_OK
    assert "state     start" in capsys.readouterr().out


def test_run_step_journal_reports_missing_topics_and_invalid_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """No topic exits 3; a bad step id or a damaged home exits 2 with a diagnostic."""
    _stub_topic(monkeypatch, None)
    assert step_journal.run_step_journal(tmp_path, "2") == step_journal.EXIT_NOT_APPLICABLE
    assert "no workflow topic resolved" in capsys.readouterr().err

    _stub_topic(monkeypatch, _topic(tmp_path))
    assert step_journal.run_step_journal(tmp_path, "../2") == step_journal.EXIT_FATAL
    assert "invalid plan step id" in capsys.readouterr().err

    (tmp_path / ".reviews").mkdir()
    (tmp_path / ".reviews" / ".gitignore").write_text("*.log\n", encoding="utf-8")
    assert step_journal.run_step_journal(tmp_path, "2") == step_journal.EXIT_FATAL
    assert "ignore coverage is invalid" in capsys.readouterr().err


def test_main_dispatches_the_step_journal_subcommand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`pw step-journal 4A` reaches `run_step_journal` with the step id."""
    calls: list[tuple[Path, str]] = []

    def fake_run(root: Path, step: str) -> int:
        calls.append((root, step))
        return 0

    monkeypatch.setattr(prompt_workflow.step_journal, "run_step_journal", fake_run)

    assert prompt_workflow.main(["step-journal", "--root", str(tmp_path), "4A"]) == 0
    assert calls == [(tmp_path.resolve(), "4A")]


def test_step_notes_surface_an_invalid_declaration(tmp_path: Path) -> None:
    """The naming call itself does not hide a broken artifact-home declaration."""
    (tmp_path / ".review-artifacts.ini").write_text("not an ini\n", encoding="utf-8")

    with pytest.raises(ReviewExchangeError):
        step_journal.step_notes(tmp_path, _SLUG, "3")


# eof
