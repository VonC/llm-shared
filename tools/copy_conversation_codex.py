"""copy_conversation_codex.py.

Render one Codex rollout as the Markdown export the Codex trimmer reads.

Codex keeps every thread in a rollout,
`~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-<time>-<thread id>.jsonl`. Its
messages are unwrapped already; they only need the `## User` and
`## Assistant` headings that `tools.trim_thinking` detects as a Codex export.

Two rollout generations are read. Up to Codex 0.152, a message is an
`event_msg` entry of type `user_message` or `agent_message`. From 0.155, it is
an `item_completed` event whose item is a `UserMessage` or an `AgentMessage`.
When a rollout holds the newer items, only they are used, so a message is
never rendered twice.

The answers given to Codex's questions (`request_user_input`) are kept as a
user section, matched to their questions by call id. Tool calls, their output
and reasoning are left out, since the trimmer drops them anyway.

When the last user message invokes the copy itself, that unfinished turn is
left out, so the copy ends on the conversation rather than on its own request.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tools.copy_conversation_claude import (
    SELF_INVOCATION,
    as_list,
    as_mapping,
    as_text,
    parse_entries,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

USER_HEADING = "User"
ASSISTANT_HEADING = "Assistant"

_QUESTION_TOOL = "request_user_input"
_ANSWERED_HEADER = "User answered Codex's questions:"
_ITEM = "item"
_EVENT = "event"
_ANSWER = "answer"
_EVENT_HEADINGS = {"user_message": USER_HEADING, "agent_message": ASSISTANT_HEADING}
_ITEM_HEADINGS = {"UserMessage": USER_HEADING, "AgentMessage": ASSISTANT_HEADING}


@dataclass(frozen=True)
class Section:
    """One rendered section and the kind of entry it came from.

    Attributes:
        source: `item`, `event` or `answer`.
        heading: `User` or `Assistant`.
        text: The section body.
    """

    source: str
    heading: str
    text: str


def item_text(content: object) -> str:
    """Join the text parts of one message item."""
    parts = (as_mapping(part) for part in as_list(content))
    return "\n".join(text for part in parts if (text := as_text(part.get("text"))))


def parse_json_text(value: object) -> dict[str, object]:
    """Parse a JSON object stored as a string, or return an empty mapping."""
    try:
        return as_mapping(json.loads(as_text(value)))
    except json.JSONDecodeError:
        return {}


def question_texts(arguments: object) -> dict[str, str]:
    """Map each question id of a `request_user_input` call to its text."""
    questions = (
        as_mapping(item)
        for item in as_list(parse_json_text(arguments).get("questions"))
    )
    return {
        as_text(item.get("id")): as_text(item.get("question")) for item in questions
    }


def answers_text(output: object, questions: dict[str, str]) -> str:
    """Render the answers of one `request_user_input` call, one per line.

    Args:
        output: The call output, a JSON string with an `answers` object.
        questions: Question texts by id, from the call itself.

    Returns:
        The header line, then one `· question → answers` line per question,
        or an empty string when the output holds no answer.
    """
    answers = as_mapping(parse_json_text(output).get("answers"))
    lines = [_ANSWERED_HEADER]
    for question_id, value in answers.items():
        chosen = "; ".join(
            as_text(item) for item in as_list(as_mapping(value).get("answers"))
        )
        lines.append(f"· {questions.get(question_id) or question_id} → {chosen}")
    return "\n".join(lines) if answers else ""


class CodexRenderer:
    """Collect the sections of one Codex rollout, in order."""

    def __init__(self) -> None:
        """Start with no section and no pending question."""
        self._sections: list[Section] = []
        self._questions: dict[str, dict[str, str]] = {}

    def add(self, entry: dict[str, object]) -> None:
        """Add one rollout entry."""
        payload = as_mapping(entry.get("payload"))
        kind = entry.get("type")
        if kind == "event_msg":
            self._add_event(payload)
        elif kind == "response_item":
            self._add_response_item(payload)

    def sections(self) -> list[Section]:
        """Return the kept sections, without a trailing copy request."""
        newest = (
            _ITEM
            if any(section.source == _ITEM for section in self._sections)
            else _EVENT
        )
        kept = [
            section for section in self._sections if section.source in {newest, _ANSWER}
        ]
        asks = [
            index
            for index, section in enumerate(kept)
            if section.source != _ANSWER and section.heading == USER_HEADING
        ]
        if asks and SELF_INVOCATION in kept[asks[-1]].text:
            return kept[: asks[-1]]
        return kept

    def text(self) -> str:
        """Return the Markdown export."""
        return "\n\n".join(
            f"## {section.heading}\n\n{section.text.strip()}"
            for section in self.sections()
        )

    def _add(self, source: str, heading: str, text: str) -> None:
        if text.strip():
            self._sections.append(Section(source, heading, text))

    def _add_event(self, payload: dict[str, object]) -> None:
        kind = as_text(payload.get("type"))
        if kind in _EVENT_HEADINGS:
            self._add(_EVENT, _EVENT_HEADINGS[kind], as_text(payload.get("message")))
            return
        item = as_mapping(payload.get("item"))
        heading = _ITEM_HEADINGS.get(as_text(item.get("type")))
        if kind == "item_completed" and heading is not None:
            self._add(_ITEM, heading, item_text(item.get("content")))

    def _add_response_item(self, payload: dict[str, object]) -> None:
        kind = payload.get("type")
        call_id = as_text(payload.get("call_id"))
        if kind == "function_call" and payload.get("name") == _QUESTION_TOOL:
            self._questions[call_id] = question_texts(payload.get("arguments"))
        elif kind == "function_call_output" and call_id in self._questions:
            questions = self._questions.pop(call_id)
            self._add(
                _ANSWER,
                USER_HEADING,
                answers_text(payload.get("output"), questions),
            )


def render_codex_rollout(lines: Iterable[str]) -> str:
    """Render the lines of one Codex rollout as a Markdown export.

    Args:
        lines: Lines of the `.jsonl` rollout.

    Returns:
        The export text, ready for the Codex trimmer.
    """
    renderer = CodexRenderer()
    for entry in parse_entries(lines):
        renderer.add(entry)
    return renderer.text()


# eof
