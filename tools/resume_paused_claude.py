"""Allowlisted Claude transcript parsing for the resume-paused lifecycle ledger.

Step 1 of v0.15.0 resume-paused reads Claude transcripts into classified
structural facts only: record and attachment types, tool names, call/result
linkage, task ids and statuses, origin kinds, timestamps, recorded ``cwd`` and
typed matches for the marked resume input and review-exchange operations. It
never retains conversation content or tool payloads. No profile is shipped: a
supported ``ClaudeLedgerProfile`` must come from recorded validation.

Fix (Step 1 missing work): ``DirectoryTranscriptSource`` lists a real Claude
project directory completely or reports the enumeration incomplete.

Fix (code review round 1, R4 and R5): parsing compares the marked resume input
in memory and classifies each recorded review-exchange command as a requestor
operation or a watcher, keeping only that class. A tool call or result without
a string identifier, a timestamp without a timezone and a repeated JSON key
are invalid records, and a record carrying text stays input-bearing even when
it also carries tool results. The ledger itself moved to
``tools.resume_paused_claude_ledger``.

Fix (code review round 2, R2-4 to R2-6): a recognized invocation is one line
naming the launcher by its exact file name, so a line break or a longer file
name ending in the launcher's name is never a requestor operation. Each record
keeps the type of every message content block for the profile to classify,
and a message, a content value, a block or a ``cwd`` of an unexpected JSON
type is an invalid record instead of an empty one.

Fix (code review round 4, R4-2): a supplied background task id, task id,
queue status or ``is_error`` flag of the wrong JSON type, or an empty one, is
an invalid record: reading it as absent would erase recorded work. A tool
result whose ``toolUseResult`` is not an object is kept as plain, and a result
whose every block is flagged ``is_error`` as failed, so the ledger can tell a
validated error or non-start outcome from unknown evidence.
"""

# ruff: noqa: EM101

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Final, Protocol

from tools.resume_paused_profiles import (
    ProcessIdentity,
    as_items,
    as_mapping,
    as_text,
    loads_strict,
)
from tools.resume_paused_windows import direct_children, list_jsonl_files

if TYPE_CHECKING:
    from collections.abc import Callable

    from tools.resume_paused_windows import WindowsApi

CLAUDE_IMAGE: Final = "claude.exe"
STARTUP_MARKERS: Final = frozenset({"SessionStart:startup"})
REQUESTOR_MARKERS: Final = frozenset({"SessionStart:startup", "SessionStart:clear"})
_TASK_ID: Final = re.compile(r"<task-id>([A-Za-z0-9_-]+)</task-id>")
_STATUS: Final = re.compile(r"<status>([a-z_]+)</status>")
_LAUNCHER: Final = "review_exchange"
# One launcher call on one line, with one operation and plain or quoted
# arguments. The launcher is named by its exact file name, alone or after a
# directory. A chain, pipe, redirection, substitution, wrapper or line break
# never matches: only spaces and tabs separate the arguments.
_INVOCATION: Final = re.compile(
    r'[ \t]*(?:&[ \t]*)?'
    r'(?:"(?:[^"`$|;&<>\r\n]*[\\/])?review_exchange\.bat"|(?:[^\s"`$|;&<>()]*[\\/])?review_exchange\.bat)'
    r'[ \t]+(?P<operation>[a-z][a-z-]*)(?:[ \t]+(?:"[^"`$\r\n]*"|[^\s"`$|;&<>()]+))*[ \t]*',
)


class TranscriptRejectedError(Exception):
    """One classified reason that keeps a transcript out of an absence proof."""


class ExchangeCall(StrEnum):
    """Class of a recorded command that invokes the review-exchange launcher."""

    REQUESTOR = "requestor"
    WATCHER = "watcher"


@dataclass(frozen=True)
class ClaudeLedgerProfile:
    """Version-pinned closed-world classification of one Claude release.

    Shapes are the strings ``record_shape`` returns. ``block_types`` lists the
    message content block types the release writes; a record holding any other
    block is unclassified. ``leaf_shapes`` lists the
    non-final chain tips a healthy transcript may hold, such as validated
    fan-out leaves. ``input_parents`` lists the shapes, besides the final
    record, that an input may attach to. ``durable_schedules`` stays true until
    validation proves schedules never survive the host process.
    ``requestor_operations`` lists the launcher operations only a requestor
    runs; every other launcher call is a watcher. ``plain_result_tools``
    lists the tools whose validated result is not an object and starts no
    lifecycle work; any other plain result that is not a recorded error is
    unclassified.
    """

    version: str
    record_types: frozenset[str]
    attachment_types: frozenset[str]
    tool_names: frozenset[str]
    stop_handlers: frozenset[str]
    block_types: frozenset[str]
    leaf_shapes: frozenset[str] = frozenset()
    input_parents: frozenset[str] = frozenset()
    terminal_statuses: frozenset[str] = frozenset({"completed", "failed", "killed"})
    requestor_operations: frozenset[str] = frozenset({"wait-answer"})
    plain_result_tools: frozenset[str] = frozenset()
    closing_shape: str = "system:stop_hook_summary"
    final_shape: str = "system:turn_duration"
    schedule_create: str = "CronCreate"
    schedule_delete: str = "CronDelete"
    durable_schedules: bool = True


@dataclass(frozen=True)
class ParseScope:
    """What one parse recognizes in memory without retaining it.

    ``marked_input`` is the complete marked resume command to find, when the
    transcript is the proved requestor's; ``requestor_operations`` comes from
    the pinned profile.
    """

    marked_input: str | None = None
    requestor_operations: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RecordFact:
    """Structural facts of one transcript record; no content is kept.

    ``plain_result`` tells that the record answers a tool call without an
    object ``toolUseResult``; ``failed`` that every result block it holds is
    flagged ``is_error``.
    """

    kind: str
    subtype: str | None = None
    uuid: str | None = None
    parent: str | None = None
    timestamp: datetime | None = None
    sidechain: bool = False
    session: str | None = None
    version: str | None = None
    cwd: str | None = None
    attachment: str | None = None
    hook: str | None = None
    origin: str | None = None
    prompt_source: str | None = None
    text_input: bool = False
    marked: bool = False
    blocks: tuple[str, ...] = ()
    calls: tuple[tuple[str, str], ...] = ()
    exchange_calls: tuple[tuple[str, ExchangeCall], ...] = ()
    results: tuple[str, ...] = ()
    started: str | None = None
    result_id: str | None = None
    plain_result: bool = False
    failed: bool = False
    terminal: tuple[str, str] | None = None
    handlers: frozenset[str] = frozenset()


def classify_exchange_command(command: str, requestor_operations: frozenset[str]) -> ExchangeCall | None:
    """Classify a recorded command by its review-exchange use.

    Returns:
        ``None`` when the command does not name the launcher. ``REQUESTOR``
        only when the complete command is exactly one recognized invocation
        with a requestor-only operation. ``WATCHER`` for every other command
        naming the launcher: chained, piped, wrapped, multi-operation, or an
        operation either role may run.
    """
    if _LAUNCHER not in command:
        return None
    match = _INVOCATION.fullmatch(command)
    if match is not None and match.group("operation") in requestor_operations:
        return ExchangeCall.REQUESTOR
    return ExchangeCall.WATCHER


def _identifier(value: object) -> str:
    """Return a required nonempty string identifier, or reject the record."""
    text = as_text(value)
    if not text:
        raise ValueError("identifier")
    return text


def _instant(value: object) -> datetime | None:
    """Return a timezone-aware instant, ``None`` when absent, or reject the record."""
    if value is None:
        return None
    moment = datetime.fromisoformat(_identifier(value))
    if moment.tzinfo is None:
        raise ValueError("timestamp")
    return moment


def _optional(value: object) -> str | None:
    """Return an optional string field, ``None`` when absent, or reject the record."""
    if value is not None and not isinstance(value, str):
        raise ValueError("field")
    return value


def _lifecycle_field(value: object) -> str | None:
    """Return a supplied lifecycle identifier or status, ``None`` when absent, or reject the record.

    A supplied value that is not a nonempty string is invalid: reading it as
    absent would erase the work it records.
    """
    return None if value is None else _identifier(value)


def _flag(value: object) -> bool:
    """Return an optional boolean flag, false when absent, or reject the record."""
    if value is not None and not isinstance(value, bool):
        raise ValueError("flag")
    return value is True


@dataclass(frozen=True)
class _Content:
    """The validated message content of one record: its text or its typed blocks."""

    text: str | None = None
    blocks: tuple[dict[str, object], ...] = ()

    def of_type(self, block_type: str) -> list[dict[str, object]]:
        """Return the content blocks of one type."""
        return [block for block in self.blocks if block.get("type") == block_type]

    def texts(self) -> list[str]:
        """Return the message text, as its string content or its text blocks."""
        if self.text is not None:
            return [self.text]
        return [as_text(block.get("text")) or "" for block in self.of_type("text")]


def _content(record: dict[str, object]) -> _Content:
    """Read a record's message content, or reject a shape that cannot be classified.

    An absent message or content is empty. A message that is not an object, a
    content that is neither a string nor an array, and a block that is not an
    object with a string type are invalid: none of them is read as "no input".
    """
    message = record.get("message")
    if message is not None and not isinstance(message, dict):
        raise ValueError("message")
    content = as_mapping(record.get("message")).get("content")
    if content is None or isinstance(content, str):
        return _Content(text=content)
    blocks = tuple(as_mapping(block) for block in as_items(content))
    if not isinstance(content, list) or not all(as_text(block.get("type")) for block in blocks):
        raise ValueError("content")
    return _Content(blocks=blocks)


def _terminal(record: dict[str, object]) -> tuple[str, str] | None:
    """Read the task id and status of a queue enqueue, from fields or its tags."""
    if record.get("type") != "queue-operation" or record.get("operation") != "enqueue":
        return None
    content = as_text(record.get("content")) or ""
    task = _lifecycle_field(record.get("taskId")) or next(iter(_TASK_ID.findall(content)), None)
    status = _lifecycle_field(record.get("status")) or next(iter(_STATUS.findall(content)), None)
    return (task, status) if task and status else None


@dataclass(frozen=True)
class _Outcome:
    """The lifecycle facts of one record's tool result."""

    started: str | None = None
    result_id: str | None = None
    plain: bool = False
    failed: bool = False


def _outcome(record: dict[str, object], content: _Content) -> _Outcome:
    """Read the started task, result identifier and shape of a record's tool result.

    A supplied background task id or task id must be a nonempty string, and an
    ``is_error`` flag a boolean, or the record is invalid. A result container
    that is not an object is kept as plain: it may hide a start, so only the
    profile can classify it.
    """
    value = record.get("toolUseResult")
    result = as_mapping(value)
    errors = [_flag(block.get("is_error")) for block in content.of_type("tool_result")]
    background, task = _lifecycle_field(result.get("backgroundTaskId")), _lifecycle_field(result.get("taskId"))
    return _Outcome(
        started=background or task,
        result_id=as_text(result.get("id")) or None,
        plain=bool(errors) and not isinstance(value, dict),
        failed=bool(errors) and all(errors),
    )


def _exchange_calls(content: _Content, scope: ParseScope) -> tuple[tuple[str, ExchangeCall], ...]:
    """Classify each tool call's command; only the class is kept."""
    classes: list[tuple[str, ExchangeCall]] = []
    for block in content.of_type("tool_use"):
        command = as_text(as_mapping(block.get("input")).get("command")) or ""
        call = classify_exchange_command(command, scope.requestor_operations)
        if call is not None:
            classes.append((_identifier(block.get("id")), call))
    return tuple(classes)


def _fact(record: dict[str, object], scope: ParseScope) -> RecordFact:
    """Reduce one decoded record to its allowlisted structural facts."""
    kind = as_text(record.get("type")) or ""
    attachment = as_mapping(record.get("attachment"))
    content = _content(record)
    outcome = _outcome(record, content)
    texts = content.texts() if kind == "user" else []
    return RecordFact(
        kind=kind,
        subtype=as_text(record.get("subtype")),
        uuid=as_text(record.get("uuid")),
        parent=as_text(record.get("parentUuid")),
        timestamp=_instant(record.get("timestamp")),
        sidechain=record.get("isSidechain") is True,
        session=as_text(record.get("sessionId")),
        version=as_text(record.get("version")),
        cwd=_optional(record.get("cwd")),
        attachment=as_text(attachment.get("type")),
        hook=as_text(attachment.get("hookName")),
        origin=as_text(as_mapping(record.get("origin")).get("kind")),
        prompt_source=as_text(record.get("promptSource")),
        text_input=bool(texts),
        marked=scope.marked_input is not None and texts == [scope.marked_input],
        blocks=tuple(str(block.get("type")) for block in content.blocks),
        calls=tuple((_identifier(block.get("id")), _identifier(block.get("name"))) for block in content.of_type("tool_use")),
        exchange_calls=_exchange_calls(content, scope),
        results=tuple(_identifier(block.get("tool_use_id")) for block in content.of_type("tool_result")),
        started=outcome.started,
        result_id=outcome.result_id,
        plain_result=outcome.plain,
        failed=outcome.failed,
        terminal=_terminal(record),
        handlers=frozenset(str(as_mapping(info).get("command")) for info in as_items(record.get("hookInfos"))),
    )


def parse_transcript(data: bytes, scope: ParseScope | None = None) -> tuple[RecordFact, ...]:
    """Parse one complete transcript read into structural facts.

    Args:
        data: The complete bytes of one transcript read.
        scope: The marked input and requestor operations to recognize.

    Raises:
        TranscriptRejectedError: The read lacks its final newline, or holds a
            line that is not JSON, repeats a key, lacks a required identifier,
            carries a timestamp without a timezone, has a message, content,
            block or ``cwd`` of an unexpected JSON type, or supplies a
            lifecycle identifier, status or error flag of the wrong type.
    """
    if not data.endswith(b"\n"):
        raise TranscriptRejectedError("transcript-incomplete")
    scope = scope or ParseScope()
    try:
        return tuple(_fact(as_mapping(loads_strict(line)), scope) for line in data.splitlines() if line.strip())
    except ValueError:
        raise TranscriptRejectedError("record-invalid") from None


def record_shape(fact: RecordFact) -> str:
    """Classify a record for leaf, closure and input-parent rules."""
    if fact.kind == "system":
        return f"system:{fact.subtype}"
    if fact.kind == "attachment":
        return f"attachment:{fact.attachment}"
    if fact.text_input:
        return "input"
    if fact.results:
        return "tool-result"
    return "tool-call" if fact.calls else fact.kind


def latest_typed_input(facts: tuple[RecordFact, ...]) -> int | None:
    """Return the index of the latest human-typed input; notifications never count."""
    typed = [i for i, fact in enumerate(facts) if fact.origin == "human" and fact.prompt_source == "typed"]
    return typed[-1] if typed else None


def claude_generation(api: WindowsApi, shell_pid: int) -> ProcessIdentity | None:
    """Identify the pane shell's single direct Claude child and its creation time."""
    children = direct_children(api.processes() or (), shell_pid, CLAUDE_IMAGE)
    process = api.open_process(children[0].pid) if len(children) == 1 else None
    if process is None:
        return None
    try:
        created = api.creation_time(process)
    finally:
        api.close(process)
    return None if created is None else ProcessIdentity(children[0].pid, created)


@dataclass(frozen=True)
class TranscriptFile:
    """Metadata of one transcript from a complete project-directory enumeration."""

    path: str
    modified: datetime


class TranscriptSource(Protocol):
    """Injected access to the checkout's Claude project transcripts."""

    def list_files(self) -> tuple[TranscriptFile, ...] | None:
        """Return every transcript, or ``None`` when enumeration is incomplete."""
        ...

    def read(self, path: str) -> bytes | None:
        """Read one transcript completely while its writer keeps it open."""
        ...


class DirectoryTranscriptSource:
    """``TranscriptSource`` over a real Claude project directory, nested files included."""

    def __init__(self, root: str, read: Callable[[str], bytes | None]) -> None:
        """Keep the project directory and the injected whole-file reader."""
        self._root = root
        self._read = read

    def list_files(self) -> tuple[TranscriptFile, ...] | None:
        """List every regular JSONL transcript, or ``None`` when incomplete."""
        files = list_jsonl_files(self._root)
        if files is None:
            return None
        return tuple(TranscriptFile(file.path, datetime.fromtimestamp(file.modified_ns / 1_000_000_000, UTC)) for file in files)

    def read(self, path: str) -> bytes | None:
        """Read one transcript completely."""
        return self._read(path)


# eof
