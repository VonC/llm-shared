"""Tests for the Codex rollout renderer of `tools.copy_conversation_codex`.

Every case renders a few hand-written rollout lines, so the tests read no file
and start no process.
"""

from __future__ import annotations

import json

from tools import copy_conversation_codex as codex

# ruff: noqa: RUF001


def _line(kind: str, **payload: object) -> str:
    """Encode one rollout entry as a `.jsonl` line."""
    return json.dumps({"type": kind, "payload": payload})


def _item(kind: str, *texts: str) -> str:
    part = "text" if kind == "UserMessage" else "Text"
    content = [{"type": part, "text": text} for text in texts]
    return _line(
        "event_msg",
        type="item_completed",
        item={"type": kind, "content": content},
    )


def _ask(call_id: str, questions: object) -> str:
    return _line(
        "response_item",
        type="function_call",
        name="request_user_input",
        call_id=call_id,
        arguments=json.dumps({"questions": questions}),
    )


def _answer(call_id: str, output: str) -> str:
    return _line(
        "response_item",
        type="function_call_output",
        call_id=call_id,
        output=output,
    )


def test_newer_items_render_as_user_and_assistant_sections() -> None:
    """Item messages win over the older events, so nothing renders twice."""
    text = codex.render_codex_rollout(
        [
            _line("session_meta", id="t1"),
            _item("UserMessage", "Where are my skills?"),
            _line("event_msg", type="agent_message", message="older duplicate"),
            _item("AgentMessage", "Checking.", ""),
            _line(
                "event_msg",
                type="item_completed",
                item={"type": "Reasoning", "summary_text": ["x"]},
            ),
            _line("response_item", type="message", role="assistant", content=[]),
            _item("AgentMessage", "They are in the plugin cache."),
        ],
    )

    assert text == (
        "## User\n\nWhere are my skills?\n\n"
        "## Assistant\n\nChecking.\n\n"
        "## Assistant\n\nThey are in the plugin cache."
    )


def test_older_events_render_when_no_item_exists() -> None:
    """A rollout written before message items still renders from its events."""
    text = codex.render_codex_rollout(
        [
            _line("event_msg", type="user_message", message="hello"),
            _line("event_msg", type="agent_message", message="  "),
            _line("event_msg", type="agent_message", message="hi"),
            _line("turn_context", cwd="C:/x"),
        ],
    )

    assert text == "## User\n\nhello\n\n## Assistant\n\nhi"


def test_question_answers_become_a_user_section() -> None:
    """Answers are matched to their questions by call id, and kept as user text."""
    output = json.dumps(
        {
            "answers": {
                "q1": {"answers": ["A: Bounded (Recommended)", "user_note: explain"]},
                "q9": {"answers": ["B"]},
            },
        },
    )
    text = codex.render_codex_rollout(
        [
            _line("event_msg", type="user_message", message="decide"),
            _ask("c1", [{"id": "q1", "question": "Which checks?"}]),
            _answer("c1", output),
            _ask("c2", [{"id": "q2", "question": "Unanswered?"}]),
            _answer("c2", json.dumps({"other": 1})),
            _answer("c3", output),
            _line(
                "response_item",
                type="function_call",
                name="exec",
                call_id="c4",
                arguments="{}",
            ),
        ],
    )

    assert text == (
        "## User\n\ndecide\n\n"
        "## User\n\nUser answered Codex's questions:\n"
        "· Which checks? → A: Bounded (Recommended); user_note: explain\n"
        "· q9 → B"
    )


def test_unreadable_call_payloads_render_nothing() -> None:
    """Arguments or output that are not JSON objects leave no section."""
    assert codex.question_texts("not json") == {}
    assert codex.answers_text("[1]", {}) == ""


def test_a_trailing_copy_request_is_cut_with_its_turn() -> None:
    """The copy ends on the conversation, not on the request that made it."""
    text = codex.render_codex_rollout(
        [
            _item("UserMessage", "hello"),
            _item("AgentMessage", "hi"),
            _item("UserMessage", "$llm-shared:copy-conversation"),
            _item("AgentMessage", "Copying."),
        ],
    )

    assert text == "## User\n\nhello\n\n## Assistant\n\nhi"


def test_an_earlier_copy_request_is_kept() -> None:
    """Only the last typed user message is checked, so an older request stays."""
    renderer = codex.CodexRenderer()
    renderer.add(
        {
            "type": "event_msg",
            "payload": {"type": "user_message", "message": "copy-conversation please"},
        },
    )
    renderer.add(
        {"type": "event_msg", "payload": {"type": "user_message", "message": "next"}},
    )

    assert [section.text for section in renderer.sections()] == [
        "copy-conversation please",
        "next",
    ]


def test_an_answer_section_is_not_taken_for_the_copy_request() -> None:
    """An answer naming the skill is the user's choice, not a request to cut."""
    output = json.dumps({"answers": {"q1": {"answers": ["yes"]}}})
    text = codex.render_codex_rollout(
        [
            _line("event_msg", type="user_message", message="hello"),
            _ask("c1", [{"id": "q1", "question": "Run copy-conversation?"}]),
            _answer("c1", output),
        ],
    )

    assert text == (
        "## User\n\nhello\n\n"
        "## User\n\nUser answered Codex's questions:\n· Run copy-conversation? → yes"
    )


# eof
