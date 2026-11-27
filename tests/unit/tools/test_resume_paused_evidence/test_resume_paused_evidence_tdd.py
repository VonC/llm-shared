"""Duplicate-resume evidence, pane activity and session journal index tests.

Step 5 of v0.15.0 resume-paused: one ``list-agents --all-sessions --json``
call yields both the pane records and their activity; input eligibility
protects busy, blocked, question and draft panes, letting only a supported
fresh Codex idle capture override stale working status; counted commands are
classified by selected role across native prefixes and trailing context; the
private session journal is read strictly as an index; and the checkout-wide
duplicate verdict keeps certain evidence apart from uncertain attribution.
Every observation is declared: no process or pane is touched, and only the
default journal reader test reads a file, from the memory-backed scratch tree.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tools.resume_paused_evidence import (
    OVERRIDE_QUESTION,
    Activity,
    ClassifiedCommand,
    CommandKind,
    DuplicateSignal,
    JournalIndex,
    ObservedCommand,
    PaneActivity,
    PauseFacts,
    ScreenVerdict,
    classify_command,
    classify_duplicates,
    counted,
    input_eligibility,
    journal_path,
    journal_time,
    observe_panes,
    parse_activity,
    parse_session_journal,
    read_session_journal,
)
from tools.resume_paused_input import LIST_AGENTS, PaneRecord
from tools.resume_paused_models import ArtifactError, CanonicalRoot, SessionRole
from tools.resume_paused_profiles import CommandResult, Host

if TYPE_CHECKING:
    from collections.abc import Sequence

PANE = "77e5f39c-0536-4cbb-a057-f4a1f5c715b0"
OTHER = "2fd92f30-1111-4222-8333-444455556666"
ROOT = CanonicalRoot.parse("C:\\work\\api")
PAUSE = datetime(2026, 11, 17, 16, 37, 18, tzinfo=UTC)
MARKER = f"{'a' * 32}.rp1.{PANE}.requestor.{'b' * 64}"
IDLE = PaneActivity("idle", "", draft_held=False, question="", ready=True)


def agent(window: str = PANE, **changes: Any) -> dict[str, Any]:  # noqa: ANN401
    """Return one live ``list-agents`` record with its activity fields."""
    record: dict[str, Any] = {
        "window_id": window, "session": "api", "name": "Claude api", "cwd": "C:\\work\\api",
        "harness_id": "claude-code", "program_status": [], "agent_session_id": "",
        "state": "idle", "blocked_by": "", "draft_held": False, "message": "", "ready": True,
    }
    record.update(changes)
    return record


def listing(*records: dict[str, Any]) -> str:
    """Render one ``list-agents --json`` output."""
    return json.dumps({"success": True, "agents": list(records)})


def pane(window: str = PANE, host: Host | None = Host.CLAUDE) -> PaneRecord:
    """Declare one live pane record of the checkout."""
    harness, apps = {Host.CLAUDE: ("claude-code", ()), Host.CODEX: ("", ("codex",)), None: ("", ())}[host]
    return PaneRecord(window, "api", "pane", "C:\\work\\api", harness, apps, None)


@dataclass
class FakeRunner:
    """Declared command result, recording every argument list."""

    result: CommandResult
    calls: list[tuple[str, ...]] = field(default_factory=list[tuple[str, ...]])

    def run(self, arguments: Sequence[str]) -> CommandResult:
        """Return the declared result."""
        self.calls.append(tuple(arguments))
        return self.result


@dataclass
class FakeProbe:
    """Declared screen verdict, counting each probe."""

    verdict: ScreenVerdict = ScreenVerdict.UNSUPPORTED
    probed: list[str] = field(default_factory=list[str])

    def probe(self, pane: PaneRecord) -> ScreenVerdict:
        """Return the declared verdict."""
        self.probed.append(pane.pane_id)
        return self.verdict


@dataclass
class FakeHistory:
    """Declared typed commands per pane; ``None`` models an unreadable history."""

    by_pane: dict[str, tuple[ObservedCommand, ...] | None] = field(default_factory=dict[str, tuple[ObservedCommand, ...] | None])

    def commands(self, pane: PaneRecord) -> tuple[ObservedCommand, ...] | None:
        """Return the declared commands of one pane."""
        return self.by_pane.get(pane.pane_id, ())


def test_one_all_session_listing_yields_panes_and_activity() -> None:
    """Discovery runs the all-session listing once and keeps the activity of each pane."""
    runner = FakeRunner(CommandResult(0, listing(agent(), agent(OTHER, session="web", state="working", draft_held=True))))
    observation = observe_panes(runner)
    assert runner.calls == [LIST_AGENTS]
    assert observation is not None
    assert [(record.pane_id, record.session) for record in observation.panes] == [(PANE, "api"), (OTHER, "web")]
    assert observation.activity[PANE] == IDLE
    assert observation.activity[OTHER] == PaneActivity("working", "", draft_held=True, question="", ready=True)


@pytest.mark.parametrize(
    "result",
    [CommandResult(1, listing(agent())), CommandResult(0, "not json"), CommandResult(0, listing(agent(draft_held="no")))],
)
def test_failed_or_malformed_discovery_is_not_absence(result: CommandResult) -> None:
    """A failed or malformed listing is a discovery failure, never an empty one."""
    assert observe_panes(FakeRunner(result)) is None


@pytest.mark.parametrize(
    "text",
    [
        "[]", "{", json.dumps({"agents": {}}), listing(agent(state=3)), listing(agent(blocked_by=None)),
        listing(agent(message=[])), listing(agent(ready="yes")), listing(agent(needs_you=1)), listing(agent(window_id="c6a64568")),
    ],
)
def test_activity_parsing_is_strict(text: str) -> None:
    """Wrong types, short pane ids and non-listing JSON are malformed discovery."""
    with pytest.raises(ArtifactError, match="discovery-malformed"):
        parse_activity(text)


def test_activity_defaults_and_repeated_pane_ids() -> None:
    """Absent activity fields read as empty, absent readiness as unknown; a repeated pane id has no activity at all."""
    minimal = {"window_id": PANE.upper(), "session": "api"}
    assert parse_activity(listing(minimal)) == {PANE: PaneActivity("", "", draft_held=False, question="", ready=None)}
    assert parse_activity(listing(agent(state="done", ready=False))) == {PANE: PaneActivity("done", "", draft_held=False, question="", ready=False)}
    assert parse_activity(listing(agent(), agent(), agent(OTHER))) == {OTHER: IDLE}


@pytest.mark.parametrize(
    ("activity", "host", "verdict", "expected"),
    [
        (None, Host.CLAUDE, ScreenVerdict.IDLE_EMPTY, (Activity.UNKNOWN, "")),
        (IDLE, Host.CLAUDE, ScreenVerdict.UNSUPPORTED, (Activity.ELIGIBLE, "")),
        (PaneActivity("done", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.UNSUPPORTED, (Activity.ELIGIBLE, "")),
        (PaneActivity("idle", "", draft_held=False, question="", ready=False), Host.CLAUDE, ScreenVerdict.IDLE_EMPTY, (Activity.NOT_READY, "")),
        (PaneActivity("done", "", draft_held=False, question="", ready=None), Host.CODEX, ScreenVerdict.IDLE_EMPTY, (Activity.NOT_READY, "")),
        (PaneActivity("needs_input", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.IDLE_EMPTY, (Activity.BLOCKED, "")),
        (PaneActivity("working", "question", draft_held=False, question="Go?", ready=False), Host.CODEX, ScreenVerdict.IDLE_EMPTY, (Activity.BLOCKED, "")),
        (PaneActivity("idle", "", draft_held=True, question="", ready=True), Host.CLAUDE, ScreenVerdict.IDLE_EMPTY, (Activity.DRAFT, "")),
        (PaneActivity("restored", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.IDLE_EMPTY, (Activity.UNKNOWN, "")),
        (PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CLAUDE, ScreenVerdict.IDLE_EMPTY, (Activity.BUSY, "")),
        (PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.UNSUPPORTED, (Activity.BUSY, "")),
        (PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.WORKING, (Activity.BUSY, "")),
        (PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.DRAFT, (Activity.DRAFT, "")),
        (PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.QUESTION, (Activity.BLOCKED, "")),
        (
            PaneActivity("working", "", draft_held=False, question="", ready=True), Host.CODEX, ScreenVerdict.IDLE_EMPTY,
            (Activity.ELIGIBLE, "stale-working-overridden"),
        ),
    ],
)
def test_input_eligibility_protects_busy_blocked_and_draft_panes(
    activity: PaneActivity | None, host: Host, verdict: ScreenVerdict, expected: tuple[Activity, str],
) -> None:
    """Only a fresh supported Codex idle capture overrides working; nothing overrides blocked or draft."""
    probe = FakeProbe(verdict)
    eligibility = input_eligibility(pane(host=host), host, activity, probe)
    assert (eligibility.activity, eligibility.note) == expected
    working = activity is not None and activity.state == "working" and not activity.blocked_by
    assert probe.probed == ([PANE] if working and host is Host.CODEX else [])


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/resume-session", ClassifiedCommand(CommandKind.RESUME_SESSION, None, uncertain=False)),
        ("  $llm-shared:resume-session --force", ClassifiedCommand(CommandKind.RESUME_SESSION, None, uncertain=False)),
        ("resume-session\nplease", ClassifiedCommand(CommandKind.RESUME_SESSION, None, uncertain=False)),
        ("/resume-session; then wait", ClassifiedCommand(CommandKind.RESUME_SESSION, None, uncertain=False)),
        ("/REVIEW-RESUME as Reviewer", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        ("$review-resume --role requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REQUESTOR, uncertain=False)),
        ("/review-resume", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=False)),
        ("/review-resume reviewer; the requestor is Claude", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        ("/review-resume as reviewer; the requestor is busy", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        ("/review-resume after the reviewer replies", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=False)),
        ("/review-resume --role=requestor as the requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REQUESTOR, uncertain=False)),
        ("/review-resume as reviewer, then as requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume reviewer or requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume reviewer/requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume reviewer (or requestor)", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume reviewer and requestor", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume as reviewer while the requestor is busy", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        ("/review-resume reviewer, the requestor is Claude", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        ("/review-resume requestor; later as reviewer", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume after Alex signs in as reviewer", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=False)),
        ("/review-resume as reviewer, then continue the review", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REVIEWER, uncertain=False)),
        (f"/review-resume --resume-paused {MARKER}", ClassifiedCommand(CommandKind.REVIEW_RESUME, SessionRole.REQUESTOR, uncertain=False)),
        ("/review-resume --resume-paused not-a-marker", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=True)),
        ("/review-resume reviewers-only", ClassifiedCommand(CommandKind.REVIEW_RESUME, None, uncertain=False)),
    ],
)
def test_commands_are_classified_across_prefixes_and_trailing_context(text: str, expected: ClassifiedCommand) -> None:
    """Native prefixes, case and trailing context keep the command and its selected role."""
    assert classify_command(text) == expected


@pytest.mark.parametrize("text", ["please resume-session", "/resume-sessions", "/review-resumed", "", "$other:resume-session"])
def test_other_text_is_not_a_resume_command(text: str) -> None:
    """Only a leading resume command counts; prose and longer names do not."""
    assert classify_command(text) is None


@pytest.mark.parametrize(
    ("text", "reviewer_pause", "expected"),
    [
        ("/resume-session", False, True),
        ("/review-resume as reviewer", False, False),
        ("/review-resume as reviewer", True, True),
        ("/review-resume as requestor", False, True),
        ("/review-resume", False, None),
        ("/review-resume", True, True),
        ("/review-resume as reviewer, then as requestor", False, None),
        ("/review-resume after the reviewer replies", False, None),
        ("/review-resume as reviewer; the requestor is busy", False, False),
        ("/review-resume reviewer or requestor", False, None),
        ("/review-resume after Alex signs in as reviewer", False, None),
        ("/review-resume reviewer (or requestor)", False, None),
        ("/review-resume as reviewer while the requestor is busy", False, False),
    ],
)
def test_reviewer_only_continuation_counts_only_for_a_reviewer_pause(text: str, reviewer_pause: bool, expected: bool | None) -> None:  # noqa: FBT001
    """Q14/Q26: reviewer-only review-resume never suppresses a non-reviewer pause; an unknown role is uncertain."""
    command = classify_command(text)
    assert command is not None
    assert counted(command, reviewer_pause=reviewer_pause) is expected


def journal(*headings: str) -> bytes:
    """Render a session journal holding the declared entry headings."""
    body = "".join(f"{heading}\n\n- Host: Claude Code\n\n" for heading in headings)
    return f"# Session journal\n\nPrivate index.\n\n{body}".encode()


def test_session_journal_indexes_resume_entries_by_canonical_checkout() -> None:
    """Resume entries index by checkout; pause entries and other checkouts never count for it."""
    index = parse_session_journal(journal(
        "## Pause by claude at 2026-11-17T17:37:18+01:00 in `C:\\work\\api`",
        "## Resume by chatgpt at 2026-11-17T18:00:00.1234567+01:00 in `c:/WORK/api`",
        "## Resume by claude at 2026-11-17T19:00:00+01:00 in `C:\\work\\web`",
    ))
    resumes = index.resumes(ROOT)
    assert resumes is not None
    (resume,) = resumes
    assert (resume.agent, resume.at, resume.checkout) == ("chatgpt", datetime(2026, 11, 17, 17, 0, 0, 123456, tzinfo=UTC), ROOT)
    assert index.resumes(CanonicalRoot.parse("C:\\work\\docs")) == ()


@pytest.mark.parametrize(
    ("data", "diagnostic"),
    [
        (b"\xff", "not UTF-8"),
        (journal("## Notes"), "unrecognized heading"),
        (journal("## Resume by claude at yesterday in `C:\\work\\api`"), "bad timestamp"),
        (journal("## Resume by claude at 2026-11-17T18:00:00 in `C:\\work\\api`"), "without offset"),
        (journal("## Resume by claude at 2026-11-17T18:00:00+01:00 in `work\\api`"), "absolute Windows path"),
    ],
)
def test_malformed_session_journal_is_unreadable_not_empty(data: bytes, diagnostic: str) -> None:
    """A malformed journal reports its error and answers no checkout."""
    index = parse_session_journal(data)
    assert diagnostic in index.error
    assert index.resumes(ROOT) is None


def test_journal_time_keeps_the_offset_and_microseconds() -> None:
    """Fractions are cut or padded to microseconds; an offset is required."""
    assert journal_time("2026-11-17T18:00:00.5+01:00") == datetime(2026, 11, 17, 17, 0, 0, 500000, tzinfo=UTC)
    with pytest.raises(ArtifactError, match="without offset"):
        journal_time("2026-11-17T18:00:00")


def test_session_journal_read_distinguishes_missing_from_unreadable() -> None:
    """A missing journal holds no entry; an unreadable one is an error, never absence."""

    def missing(path: Path) -> bytes:
        raise FileNotFoundError(path)

    def denied(path: Path) -> bytes:
        raise PermissionError(13, "Access is denied", str(path))

    path = Path("C:\\Users\\person\\.llm-shared\\sessions.journal.md")
    assert read_session_journal(path, read=missing).resumes(ROOT) == ()
    assert read_session_journal(path, read=denied).error == "session journal is unreadable: Access is denied"
    present = read_session_journal(path, read=lambda _path: journal("## Resume by claude at 2026-11-17T18:00:00+01:00 in `C:\\work\\api`"))
    assert len(present.resumes(ROOT) or ()) == 1


def test_session_journal_default_reader_reads_the_file_bytes(tmp_path: Path) -> None:
    """The default reader reads the journal file as it is; a missing file is an empty index."""
    path = tmp_path / ".llm-shared" / "sessions.journal.md"
    assert read_session_journal(path).resumes(ROOT) == ()
    path.parent.mkdir()
    path.write_bytes(journal("## Resume by claude at 2026-11-17T18:00:00+01:00 in `C:\\work\\api`"))
    assert [resume.agent for resume in read_session_journal(path).resumes(ROOT) or ()] == ["claude"]


def test_journal_path_comes_from_the_user_profile() -> None:
    """The journal sits under USERPROFILE; without it there is no path to read."""
    assert journal_path({"USERPROFILE": "C:\\Users\\person"}) == Path("C:\\Users\\person\\.llm-shared\\sessions.journal.md")
    assert journal_path({"HOME": "C:\\Users\\person"}) is None


def facts(*, reviewer: bool = False) -> PauseFacts:
    """Return the declared pause facts of the checkout."""
    return PauseFacts(ROOT, PAUSE, reviewer=reviewer)


def at(seconds: int) -> datetime:
    """Return the pause instant shifted by whole seconds."""
    return PAUSE + timedelta(seconds=seconds)


@pytest.mark.parametrize(
    ("stamp", "evidence", "uncertain"),
    [
        ("2026-11-17T17:37:17+01:00", [], ()),
        ("2026-11-17T17:37:18+01:00", [], ("journal-resume-unordered chatgpt",)),
        ("2026-11-17T17:37:19+01:00", [(DuplicateSignal.JOURNAL, "chatgpt", at(1))], ()),
    ],
)
def test_only_a_strictly_later_journal_resume_is_evidence(stamp: str, evidence: list[object], uncertain: tuple[str, ...]) -> None:
    """An earlier entry belongs to an older pause; an equal time cannot prove a later resume and stays uncertain."""
    index = parse_session_journal(journal(f"## Resume by chatgpt at {stamp} in `C:\\work\\api`"))
    verdict = classify_duplicates(facts(), (pane(),), FakeHistory(), {}, index)
    assert [(item.signal, item.detail, item.at) for item in verdict.evidence] == evidence
    assert verdict.uncertain == uncertain


@pytest.mark.parametrize(
    ("seconds", "evidence", "uncertain"),
    [
        (-5, [], ()),
        (0, [], (f"command-unordered {PANE}",)),
        (3, [(DuplicateSignal.COMMAND, PANE, "review-resume requestor")], ()),
    ],
)
def test_only_a_strictly_later_counted_command_is_evidence(seconds: int, evidence: list[object], uncertain: tuple[str, ...]) -> None:
    """An earlier command is ignored, an equal time stays uncertain, a later one counts; other text never does."""
    history = FakeHistory({PANE: (ObservedCommand("hello", None), ObservedCommand("/review-resume as requestor", at(seconds)))})
    verdict = classify_duplicates(facts(), (pane(),), history, {}, JournalIndex())
    assert [(item.signal, item.pane_id, item.detail) for item in verdict.evidence] == evidence
    assert verdict.uncertain == uncertain


def test_counted_commands_come_from_every_pane_in_pane_order() -> None:
    """Every pane of the checkout supplies evidence, reported in pane id order."""
    history = FakeHistory({PANE: (ObservedCommand("/resume-session", at(3)),), OTHER: (ObservedCommand("$llm-shared:resume-session", at(1)),)})
    verdict = classify_duplicates(facts(), (pane(), pane(OTHER, Host.CODEX)), history, {}, JournalIndex())
    assert [(item.pane_id, item.detail) for item in verdict.evidence] == [(OTHER, "resume-session"), (PANE, "resume-session")]


@pytest.mark.parametrize("moment", [at(2), None])
def test_reviewer_continuation_follows_the_saved_pause_role(moment: datetime | None) -> None:
    """A reviewer-only review-resume never counts for a non-reviewer pause, dated or not; for a reviewer pause it needs a later time."""
    history = FakeHistory({PANE: (ObservedCommand("/review-resume as reviewer", moment),)})
    requestor = classify_duplicates(facts(), (pane(),), history, {}, JournalIndex())
    reviewer = classify_duplicates(facts(reviewer=True), (pane(),), history, {}, JournalIndex())
    assert (requestor.evidence, requestor.uncertain) == ((), ())
    if moment is None:
        assert (reviewer.evidence, reviewer.uncertain) == ((), (f"command-unattributed {PANE}",))
    else:
        assert [item.detail for item in reviewer.evidence] == ["review-resume reviewer"]


@pytest.mark.parametrize(
    ("commands", "reason"),
    [
        (None, "command-history-unreadable"),
        ((ObservedCommand("/resume-session", None),), "command-unattributed"),
        ((ObservedCommand("/review-resume", at(4)),), "review-role-uncertain"),
        ((ObservedCommand("/review-resume reviewer or requestor", at(4)),), "review-role-uncertain"),
        ((ObservedCommand("/review-resume after Alex signs in as reviewer", at(4)),), "review-role-uncertain"),
        ((ObservedCommand("/review-resume reviewer (or requestor)", at(4)),), "review-role-uncertain"),
    ],
)
def test_uncertain_attribution_and_role_are_reported_not_ignored(commands: tuple[ObservedCommand, ...] | None, reason: str) -> None:
    """An unreadable history, an unattributed counted command or an uncertain role stays uncertain, never a reviewer-only skip."""
    verdict = classify_duplicates(facts(), (pane(),), FakeHistory({PANE: commands}), {}, JournalIndex())
    assert verdict.evidence == ()
    assert verdict.uncertain == (f"{reason} {PANE}",)


def test_unreadable_journal_is_uncertain() -> None:
    """A journal that cannot be read leaves duplicate protection uncertain."""
    verdict = classify_duplicates(facts(), (), FakeHistory(), {}, JournalIndex(error="session journal is not UTF-8"))
    assert verdict.uncertain == ("session-journal-unreadable",)


def test_pending_author_override_question_is_duplicate_evidence_while_blocked() -> None:
    """A pane blocked on the override question suppresses; the same text on an idle pane does not."""
    question = f"resume-session: resume prompt `.reviews/a.session-resume.local.md` (unused) was paused by `claude`. Do you want to {OVERRIDE_QUESTION}?"
    blocked = PaneActivity("needs_input", "question", draft_held=False, question=question, ready=False)
    stale = PaneActivity("idle", "", draft_held=False, question=question, ready=False)
    verdict = classify_duplicates(facts(), (pane(), pane(OTHER)), FakeHistory(), {PANE: blocked, OTHER: stale}, JournalIndex())
    assert [(item.signal, item.pane_id) for item in verdict.evidence] == [(DuplicateSignal.OVERRIDE, PANE)]


# eof
