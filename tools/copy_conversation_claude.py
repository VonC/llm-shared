"""copy_conversation_claude.py.

Render one Claude Code session transcript as an unwrapped export.

Claude Code's `/export` command wraps prose near 80 columns, and no setting
turns that off. The session transcript, the `.jsonl` file Claude Code keeps
under `~/.claude/projects/<folder>/<session id>.jsonl`, holds every message
unwrapped. This module renders it with the markers the Claude trimmer of
`tools.trim_thinking` reads:

- a typed prompt opens on U+276F, and its other lines are indented by two
  spaces, as in an export;
- each assistant text block opens on U+25CF, its other lines indented;
- each finished turn closes on a U+273B line giving its duration and the
  local time it ended;
- the recap Claude Code writes under a turn follows on a U+203B line.

Tool calls, tool output and thinking are left out, since the trimmer drops
them anyway. The answers given to Claude's questions are kept, as a prompt of
their own: the user typed them, and a tool block would be trimmed away.

When the last prompt invokes the copy itself, that unfinished turn is left
out, so the copy ends on the conversation rather than on its own request.

The rendering is pure: callers pass the transcript lines and get the text.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, tzinfo
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

# The prompt prefix is a heavy right-pointing angle ornament, U+276F, which
# ruff reports as confusable with the plain greater-than sign.
PROMPT_MARKER = "❯ "  # noqa: RUF001
ANSWER_MARKER = "● "
CLOSING_MARKER = "✻ "
RECAP_MARKER = "※ recap: "
CONTINUATION_INDENT = "  "
SELF_INVOCATION = "copy-conversation"

_QUESTION_TOOL = "AskUserQuestion"
_ANSWERED_HEADER = "User answered Claude's questions:"
_DECLINED_HEADER = "User declined to answer Claude's questions."
_COMMAND_NAME_PATTERN = re.compile(
    r"<command-name>(?P<value>.*?)</command-name>",
    re.DOTALL,
)
_COMMAND_ARGS_PATTERN = re.compile(
    r"<command-args>(?P<value>.*?)</command-args>",
    re.DOTALL,
)
_PASTED_TAG_PATTERN = re.compile(r"</?pasted_content\b[^>]*>\n?")
_SECONDS_PER_HOUR = 3600
_SECONDS_PER_MINUTE = 60
_MILLISECONDS = 1000


def as_mapping(value: object) -> dict[str, object]:
    """Return a JSON object as a mapping, or an empty one for anything else."""
    if isinstance(value, dict):
        return cast("dict[str, object]", value)
    return {}


def as_list(value: object) -> list[object]:
    """Return a JSON array as a list, or an empty one for anything else."""
    if isinstance(value, list):
        return cast("list[object]", value)
    return []


def as_text(value: object) -> str:
    """Return a JSON string, or an empty string for anything else."""
    return value if isinstance(value, str) else ""


def parse_entries(lines: Iterable[str]) -> list[dict[str, object]]:
    """Parse the JSON objects of a transcript, one per line.

    A transcript being written can end on a partial line, and a blank line
    carries nothing, so a line that is not a JSON object is skipped.

    Args:
        lines: Lines of a `.jsonl` transcript.

    Returns:
        The entries, in file order.
    """
    entries: list[dict[str, object]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            value: object = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            entries.append(cast("dict[str, object]", value))
    return entries


def render_block(marker: str, text: str) -> list[str]:
    """Render one message behind its marker, its other lines indented.

    Args:
        marker: Prefix of the first line.
        text: Message text, kept unwrapped.

    Returns:
        The block lines; a blank line inside the message stays empty.
    """
    lines = text.strip("\n").splitlines() or [""]
    rest = [CONTINUATION_INDENT + line if line.strip() else "" for line in lines[1:]]
    return [marker + lines[0], *rest]


def format_duration(milliseconds: float) -> str:
    """Format a turn duration the way Claude Code prints it."""
    seconds = round(milliseconds / _MILLISECONDS)
    hours, rest = divmod(seconds, _SECONDS_PER_HOUR)
    minutes, seconds = divmod(rest, _SECONDS_PER_MINUTE)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def closing_line(milliseconds: float, timestamp: str, zone: tzinfo | None) -> str:
    """Build the line that closes a turn, with its end time when known.

    Args:
        milliseconds: Duration of the turn.
        timestamp: ISO 8601 time the turn ended, possibly empty.
        zone: Time zone of the printed end time; None for the local one.

    Returns:
        The closing line.
    """
    line = f"{CLOSING_MARKER}Worked for {format_duration(milliseconds)}"
    try:
        ended = datetime.fromisoformat(timestamp).astimezone(zone)
    except ValueError:
        return line
    return f"{line} · done {ended.hour}:{ended.minute:02d}"


def prompt_text(content: object) -> str:
    """Return what the user typed, from the content of a prompt entry.

    A slash command is stored as tags; it becomes the command line the user
    typed. Pasted text keeps its body and loses the tags around it.

    Args:
        content: The `message.content` of the entry, a string or blocks.

    Returns:
        The prompt text.
    """
    if isinstance(content, str):
        text = content
    else:
        parts = [as_mapping(block) for block in as_list(content)]
        text = "\n".join(
            as_text(part.get("text")) for part in parts if part.get("type") == "text"
        )
    command = _COMMAND_NAME_PATTERN.search(text)
    if command is not None:
        arguments = _COMMAND_ARGS_PATTERN.search(text)
        suffix = arguments.group("value").strip() if arguments is not None else ""
        return f"{command.group('value').strip()} {suffix}".rstrip()
    return _PASTED_TAG_PATTERN.sub("", text)


def answers_text(result: dict[str, object]) -> str:
    """Render the answers given to Claude's questions, one per line.

    Args:
        result: The `toolUseResult` of the question tool.

    Returns:
        The header line, then one `· question → answer` line per question.
    """
    notes = as_mapping(result.get("annotations"))
    lines = [_ANSWERED_HEADER]
    for question, answer in as_mapping(result.get("answers")).items():
        line = f"· {question} → {as_text(answer)}"
        note = as_text(as_mapping(notes.get(question)).get("notes"))
        lines.append(f"{line}; notes: {note}" if note else line)
    return "\n".join(lines)


class ClaudeRenderer:
    """Collect the blocks of one Claude transcript, in order."""

    def __init__(self, zone: tzinfo | None = None) -> None:
        """Start empty; ``zone`` sets the time zone of the closing lines."""
        self._zone = zone
        self._blocks: list[list[str]] = []
        self._prompt_starts: list[int] = []
        self._question_ids: set[str] = set()

    def add(self, entry: dict[str, object]) -> None:
        """Add one transcript entry; entries of a subagent are left out."""
        if entry.get("isSidechain"):
            return
        kind = entry.get("type")
        if kind == "user":
            self._add_user(entry)
        elif kind == "assistant":
            self._add_assistant(entry)
        elif kind == "system":
            self._add_system(entry)

    def text(self) -> str:
        """Return the export, without a trailing copy request."""
        blocks = self._blocks
        if self._prompt_starts:
            last = self._prompt_starts[-1]
            if SELF_INVOCATION in blocks[last][0]:
                blocks = blocks[:last]
        return "\n\n".join("\n".join(block) for block in blocks)

    def _add_prompt(self, text: str) -> None:
        self._prompt_starts.append(len(self._blocks))
        self._blocks.append(render_block(PROMPT_MARKER, text))

    def _add_user(self, entry: dict[str, object]) -> None:
        if entry.get("isMeta") or entry.get("isCompactSummary"):
            return
        content = as_mapping(entry.get("message")).get("content")
        for block in (as_mapping(item) for item in as_list(content)):
            if (
                block.get("type") == "tool_result"
                and block.get("tool_use_id") in self._question_ids
            ):
                self._add_answers(entry, block)
        if as_mapping(entry.get("origin")).get("kind") == "human":
            self._add_prompt(prompt_text(content))

    def _add_answers(self, entry: dict[str, object], block: dict[str, object]) -> None:
        if block.get("is_error"):
            self._add_prompt(_DECLINED_HEADER)
            return
        result = as_mapping(entry.get("toolUseResult"))
        if result.get("answers"):
            self._add_prompt(answers_text(result))

    def _add_assistant(self, entry: dict[str, object]) -> None:
        content = as_mapping(entry.get("message")).get("content")
        for block in (as_mapping(item) for item in as_list(content)):
            kind = block.get("type")
            if kind == "text" and as_text(block.get("text")).strip():
                self._blocks.append(
                    render_block(ANSWER_MARKER, as_text(block.get("text"))),
                )
            elif kind == "tool_use" and block.get("name") == _QUESTION_TOOL:
                self._question_ids.add(as_text(block.get("id")))

    def _add_system(self, entry: dict[str, object]) -> None:
        subtype = entry.get("subtype")
        if subtype == "turn_duration":
            duration = entry.get("durationMs")
            milliseconds = duration if isinstance(duration, int | float) else 0
            timestamp = as_text(entry.get("timestamp"))
            self._blocks.append([closing_line(milliseconds, timestamp, self._zone)])
        elif subtype == "away_summary":
            self._blocks.append(
                render_block(RECAP_MARKER, as_text(entry.get("content"))),
            )


def render_claude_transcript(lines: Iterable[str], zone: tzinfo | None = None) -> str:
    """Render the lines of one Claude transcript as an unwrapped export.

    Args:
        lines: Lines of the `.jsonl` transcript.
        zone: Time zone of the closing lines; None for the local one.

    Returns:
        The export text, ready for the Claude trimmer.
    """
    renderer = ClaudeRenderer(zone)
    for entry in parse_entries(lines):
        renderer.add(entry)
    return renderer.text()


# eof
