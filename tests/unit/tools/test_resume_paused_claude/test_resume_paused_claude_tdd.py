"""Claude transcript parsing tests.

Step 1 of v0.14.0 resume-paused: parsing keeps structure and never content,
distinguishes typed input from notifications, and classifies review-exchange
commands and the marked resume input in memory.

Fix (code review round 1, R4 and R5): the ledger tests moved to
``test_resume_paused_claude_ledger``. These tests add the requestor-operation
classification, the marked-input match, and the rejection of missing or
non-string linkage identifiers, timestamps without a timezone and repeated
JSON keys; a record with both text and tool results stays input-bearing.

Fix (code review round 2, R2-4 to R2-6): a command holding a line break or
naming a longer file that ends in the launcher's name is a watcher; every
message block type is kept for classification without its content; a message,
content, block or ``cwd`` of an unexpected JSON type rejects the transcript.

Fix (code review round 4, R4-2): a malformed or empty background task id, task
id, queue status or ``is_error`` flag rejects the transcript; a result container
that is not an object is kept as plain and an all-error result as failed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.resume_paused_test_support import (
    CREATED,
    HOST_PID,
    SHELL_PID,
    FakeWindowsApi,
    at,
    closed_turn,
    jsonl,
    record,
    task_ended,
    tool_call,
    typed,
)
from tools.resume_paused_claude import (
    DirectoryTranscriptSource,
    ExchangeCall,
    ParseScope,
    RecordFact,
    TranscriptRejectedError,
    classify_exchange_command,
    claude_generation,
    latest_typed_input,
    parse_transcript,
    record_shape,
)
from tools.resume_paused_profiles import ProcessIdentity
from tools.resume_paused_windows import ProcessRecord

CLAUDE_CHILD = (ProcessRecord(SHELL_PID, 1, "cmd.exe"), ProcessRecord(HOST_PID, SHELL_PID, "claude.exe"))
REQUESTOR_OPERATIONS = frozenset({"wait-answer"})
LAUNCHER = '& "C:\\tools\\llm shared\\bin\\review_exchange.bat"'
WAIT_ANSWER = f'{LAUNCHER} wait-answer --family code --document docs/plan.md --another-round-label "Rework and review again"'
RESULT = {"type": "tool_result", "tool_use_id": "c1"}


def test_latest_typed_input_ignores_notifications_and_slash_commands() -> None:
    """Only a human-typed prompt is the latest typed input."""
    notification = record("user", "n1", "t1-end", 50, promptSource="system", origin={"kind": "task-notification"}, message={"content": "done"})
    slash = record("user", "s1", "t1-end", 51, origin={"kind": "human"}, message={"content": "/tasks"})
    facts = parse_transcript(jsonl([*closed_turn(), notification, slash]))

    assert latest_typed_input(facts) == 2  # noqa: PLR2004
    assert latest_typed_input(parse_transcript(jsonl([notification, slash]))) is None


def test_queue_terminal_is_read_from_fields_or_tags_only_on_enqueue() -> None:
    """Task id and status come from an enqueue; other queue records carry none."""
    facts = parse_transcript(jsonl([
        record("queue-operation", operation="enqueue", taskId="t1", status="killed"),
        task_ended(20, "t2", "failed"),
        record("queue-operation", operation="dequeue", taskId="t1", status="killed"),
        record("queue-operation", operation="enqueue", content="plain prompt"),
        record("queue-operation", operation="enqueue", content=["not", "text"]),
    ]))

    assert [fact.terminal for fact in facts] == [("t1", "killed"), ("t2", "failed"), None, None, None]


def test_record_facts_keep_structure_without_content() -> None:
    """A parsed record keeps linkage and classification, never its text or command."""
    call = parse_transcript(jsonl([tool_call("a", "p", 10, "c1", command="Get-Content secret.txt")]))[0]
    answer = parse_transcript(jsonl([record("user", "u", "a", 11, message={"content": [{"type": "tool_result", "tool_use_id": "c1", "content": "secret"}]}, toolUseResult="text")]))[0]

    assert (call.calls, call.uuid, call.parent, call.timestamp) == ((("c1", "PowerShell"),), "a", "p", at(10))
    assert call.exchange_calls == ()
    assert (answer.results, answer.text_input, answer.started, answer.result_id) == (("c1",), False, None, None)
    assert "secret" not in repr(answer) + repr(call)


def test_result_shape_and_error_flag_are_kept() -> None:
    """A result container that is not an object is plain, an all-error result failed; other records carry neither."""
    facts = parse_transcript(jsonl([
        record("user", "u1", "a", 11, message={"content": [RESULT]}, toolUseResult={"backgroundTaskId": "t1"}),
        record("user", "u2", "a", 12, message={"content": [RESULT]}, toolUseResult="text"),
        record("user", "u3", "a", 13, message={"content": [{**RESULT, "is_error": True}]}),
        record("user", "u4", "a", 14, message={"content": [RESULT, {**RESULT, "tool_use_id": "c2", "is_error": True}]}, toolUseResult=[]),
        record("mode", toolUseResult="text"),
    ]))

    assert [(fact.started, fact.plain_result, fact.failed) for fact in facts] == [
        ("t1", False, False), (None, True, False), (None, True, True), (None, True, False), (None, False, False),
    ]


def test_record_with_text_and_tool_result_stays_input_bearing() -> None:
    """A user record carrying both a tool result and text is still an input."""
    content = [{"type": "tool_result", "tool_use_id": "c1"}, {"type": "text", "text": "and also do this"}]
    fact = parse_transcript(jsonl([record("user", "u", "a", 11, message={"content": content})]))[0]

    assert (fact.results, fact.text_input, record_shape(fact)) == (("c1",), True, "input")


def test_marked_input_is_matched_exactly_and_only_when_requested() -> None:
    """The complete marked command is compared in memory; only the match is kept."""
    data = jsonl([typed("in", "start", 10, "/resume rp1:launch-1"), typed("other", "in", 11, "/resume rp1:launch-1 extra")])

    marked = parse_transcript(data, ParseScope(marked_input="/resume rp1:launch-1"))

    assert [fact.marked for fact in marked] == [True, False]
    assert [fact.marked for fact in parse_transcript(data)] == [False, False]
    assert "launch-1" not in repr(marked)


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        (WAIT_ANSWER, ExchangeCall.REQUESTOR),
        ("C:/tools/bin/review_exchange.bat wait-answer --family code", ExchangeCall.REQUESTOR),
        (f"{LAUNCHER} wait-any-request", ExchangeCall.WATCHER),
        (f"{LAUNCHER} status --family code", ExchangeCall.WATCHER),
        (f'{WAIT_ANSWER}; "wait=$LASTEXITCODE"', ExchangeCall.WATCHER),
        (f"{WAIT_ANSWER} | Out-File a.log", ExchangeCall.WATCHER),
        (f"{WAIT_ANSWER} && {LAUNCHER} wait-any-request", ExchangeCall.WATCHER),
        (f"{WAIT_ANSWER} > a.log", ExchangeCall.WATCHER),
        ('cmd /c "C:\\bin\\review_exchange.bat wait-answer"', ExchangeCall.WATCHER),
        (f"powershell -Command {{ {WAIT_ANSWER} }}", ExchangeCall.WATCHER),
        (f"$(Get-Item x); {WAIT_ANSWER}", ExchangeCall.WATCHER),
        ("Get-Content docs/review_exchange notes.md", ExchangeCall.WATCHER),
        ("review_exchange.bat wait-answer", ExchangeCall.REQUESTOR),
        (f"{LAUNCHER}\twait-answer\t--family code", ExchangeCall.REQUESTOR),
        (f"{WAIT_ANSWER}\nStart-Sleep 600", ExchangeCall.WATCHER),
        (f"{WAIT_ANSWER}\r\nStart-Sleep 600", ExchangeCall.WATCHER),
        (f"{LAUNCHER}\nwait-answer", ExchangeCall.WATCHER),
        (f'{LAUNCHER} wait-answer --guidance "two\r\nlines"', ExchangeCall.WATCHER),
        ('& "C:\\tools\\bin\\not_review_exchange.bat" wait-answer', ExchangeCall.WATCHER),
        ("C:/tools/bin/not_review_exchange.bat wait-answer", ExchangeCall.WATCHER),
        ("Start-Sleep 120", None),
        ("", None),
    ],
)
def test_exchange_command_classification(command: str, expected: ExchangeCall | None) -> None:
    """Only one plain one-line requestor-only invocation qualifies; any other launcher use is a watcher."""
    assert classify_exchange_command(command, REQUESTOR_OPERATIONS) is expected


def test_message_block_types_are_kept_without_their_content() -> None:
    """Every block type reaches the profile's classification; an unknown one is not erased."""
    content = [{"type": "text", "text": "hello"}, {"type": "future_input", "text": "later work"}]
    fact = parse_transcript(jsonl([record("user", "u", "p", 10, message={"content": content})]))[0]

    assert fact.blocks == ("text", "future_input")
    assert fact.text_input
    assert "later work" not in repr(fact)


def test_exchange_calls_keep_only_the_class_of_each_command() -> None:
    """A tool call that invokes the launcher records its class under its call id."""
    scope = ParseScope(requestor_operations=REQUESTOR_OPERATIONS)
    facts = parse_transcript(
        jsonl([tool_call("a", "p", 10, "c1", command=WAIT_ANSWER), tool_call("b", "a", 11, "c2", command=f"{LAUNCHER} wait-any-request")]),
        scope,
    )

    assert [fact.exchange_calls for fact in facts] == [(("c1", ExchangeCall.REQUESTOR),), (("c2", ExchangeCall.WATCHER),)]
    assert "review_exchange" not in repr(facts)


@pytest.mark.parametrize(
    "damaged",
    [
        record("assistant", "a", "p", 10, message={"content": [{"type": "tool_use", "name": "PowerShell"}]}),
        record("assistant", "a", "p", 10, message={"content": [{"type": "tool_use", "id": "c1"}]}),
        record("assistant", "a", "p", 10, message={"content": [{"type": "tool_use", "id": 7, "name": "PowerShell"}]}),
        record("assistant", "a", "p", 10, message={"content": [{"type": "tool_use", "name": "PowerShell", "input": {"command": WAIT_ANSWER}}]}),
        record("user", "u", "a", 11, message={"content": [{"type": "tool_result"}]}),
        record("user", "u", "a", 11, message={"content": [{"type": "tool_result", "tool_use_id": ""}]}),
        record("mode", timestamp="2026-11-14T10:00:05"),
        record("mode", timestamp=1731578405),
        record("mode", timestamp=""),
        record("user", message="text"),
        record("user", message={"content": 7}),
        record("user", message={"content": ["text"]}),
        record("user", message={"content": [{"text": "untyped"}]}),
        record("user", message={"content": [{"type": 7}]}),
        record("mode", cwd=7),
        record("user", "u", "a", 11, message={"content": [RESULT]}, toolUseResult={"backgroundTaskId": 7}),
        record("user", "u", "a", 11, message={"content": [RESULT]}, toolUseResult={"backgroundTaskId": ""}),
        record("user", "u", "a", 11, message={"content": [RESULT]}, toolUseResult={"taskId": ["t1"]}),
        record("user", "u", "a", 11, message={"content": [{**RESULT, "is_error": "yes"}]}),
        record("queue-operation", operation="enqueue", taskId=7, status="killed"),
        record("queue-operation", operation="enqueue", taskId="t1", status=""),
    ],
)
def test_malformed_structural_fields_reject_the_transcript(damaged: dict[str, Any]) -> None:
    """A missing or non-string linkage id, a timestamp without a timezone, a malformed message or cwd, and a malformed lifecycle field are invalid."""
    with pytest.raises(TranscriptRejectedError, match="record-invalid"):
        parse_transcript(jsonl([damaged]), ParseScope(requestor_operations=REQUESTOR_OPERATIONS))


@pytest.mark.parametrize(
    ("data", "reason"),
    [
        (jsonl(closed_turn())[:-1], "transcript-incomplete"),
        (b"", "transcript-incomplete"),
        (b"{truncated\n", "record-invalid"),
        (b'{"type": "mode", "type": "user"}\n', "record-invalid"),
    ],
)
def test_incomplete_unparsable_or_ambiguous_bytes_reject_the_transcript(data: bytes, reason: str) -> None:
    """A truncated read, a non-JSON line and a repeated key never yield facts."""
    with pytest.raises(TranscriptRejectedError, match=reason):
        parse_transcript(data)


def test_non_object_lines_parse_as_unclassifiable_records() -> None:
    """A JSON line that is not an object yields a record of no known kind."""
    assert parse_transcript(b"3\n\n") == (RecordFact(""),)


@pytest.mark.parametrize(
    ("fact", "shape"),
    [
        (RecordFact("system", subtype="turn_duration"), "system:turn_duration"),
        (RecordFact("attachment", attachment="hook_success"), "attachment:hook_success"),
        (RecordFact("user", results=("c1",)), "tool-result"),
        (RecordFact("user", text_input=True), "input"),
        (RecordFact("assistant", calls=(("c1", "PowerShell"),)), "tool-call"),
        (RecordFact("assistant"), "assistant"),
    ],
)
def test_record_shape(fact: RecordFact, shape: str) -> None:
    """Each record kind maps to one shape used by the closure rules."""
    assert record_shape(fact) == shape


def test_claude_generation_identifies_the_single_direct_child() -> None:
    """The pane shell's only Claude child yields its process generation."""
    api = FakeWindowsApi(listing=CLAUDE_CHILD)

    assert claude_generation(api, SHELL_PID) == ProcessIdentity(HOST_PID, CREATED)
    assert api.closed == [1020]


@pytest.mark.parametrize(
    "change",
    [
        {"listing": None},
        {"listing": (*CLAUDE_CHILD, ProcessRecord(21, SHELL_PID, "claude.exe"))},
        {"listing": CLAUDE_CHILD, "process_handle": None},
        {"listing": CLAUDE_CHILD, "created": None},
    ],
)
def test_claude_generation_is_unavailable_without_one_readable_child(change: dict[str, Any]) -> None:
    """No listing, several children, a denied open or no creation time bind nothing."""
    assert claude_generation(FakeWindowsApi(**change), SHELL_PID) is None


def test_directory_source_lists_and_reads_real_transcripts(tmp_path: Path) -> None:
    """A project directory yields its nested transcripts through the injected reader."""
    (tmp_path / "subagents").mkdir()
    (tmp_path / "subagents" / "side.jsonl").write_bytes(jsonl(closed_turn()))
    (tmp_path / "bound.jsonl").write_bytes(jsonl(closed_turn()))
    source = DirectoryTranscriptSource(str(tmp_path), lambda path: Path(path).read_bytes())

    listing = source.list_files()

    assert listing is not None
    assert {Path(file.path).name for file in listing} == {"side.jsonl", "bound.jsonl"}
    assert all(file.modified.tzinfo is not None for file in listing)
    assert source.read(listing[0].path) == jsonl(closed_turn())
    assert DirectoryTranscriptSource(str(tmp_path / "absent"), lambda _path: None).list_files() is None


# eof
