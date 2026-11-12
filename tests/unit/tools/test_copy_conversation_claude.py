"""Tests for the Claude transcript renderer of `tools.copy_conversation_claude`.

Every case renders a few hand-written transcript lines, so the tests read no
file and start no process.
"""

from __future__ import annotations

import json
from datetime import UTC

import pytest

from tools import copy_conversation_claude as claude

# ruff: noqa: RUF001

_HUMAN = {"kind": "human"}


def _line(**entry: object) -> str:
    """Encode one transcript entry as a `.jsonl` line."""
    return json.dumps(entry)


def _prompt(content: object, **extra: object) -> str:
    return _line(
        type="user",
        origin=_HUMAN,
        message={"role": "user", "content": content},
        **extra,
    )


def _assistant(*blocks: dict[str, object], **extra: object) -> str:
    return _line(
        type="assistant",
        message={"role": "assistant", "content": list(blocks)},
        **extra,
    )


def _text(text: str) -> dict[str, object]:
    return {"type": "text", "text": text}


def _render(*lines: str) -> str:
    return claude.render_claude_transcript(lines, UTC)


def test_one_turn_renders_prompt_answers_closing_and_recap() -> None:
    """A turn keeps its prompt, its text blocks, its closing line and its recap."""
    text = _render(
        _prompt("fix the bug\nplease"),
        _assistant({"type": "thinking", "thinking": "hidden"}),
        _assistant(_text("Looking.")),
        _assistant({"type": "tool_use", "id": "t1", "name": "Bash", "input": {}}),
        _line(
            type="user",
            message={
                "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "ok"},
                ],
            },
        ),
        _assistant(_text("Fixed it.\n\nDetails:\n- one")),
        _line(type="system", subtype="stop_hook_summary"),
        _line(
            type="system",
            subtype="turn_duration",
            durationMs=775011,
            timestamp="2026-11-03T06:58:12.000Z",
        ),
        _line(type="system", subtype="away_summary", content="The bug is fixed."),
    )

    assert text == (
        "❯ fix the bug\n  please\n\n"
        "● Looking.\n\n"
        "● Fixed it.\n\n  Details:\n  - one\n\n"
        "✻ Worked for 12m 55s · done 6:58\n\n"
        "※ recap: The bug is fixed."
    )


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        (
            "<command-message>resume-session</command-message>\n<command-name>/resume-session</command-name>",
            "/resume-session",
        ),
        (
            "<command-name>/x</command-name><command-args> --force </command-args>",
            "/x --force",
        ),
        (
            'look:\n<pasted_content id="7">\nOK line\n</pasted_content id="7">\nend',
            "look:\nOK line\nend",
        ),
        (
            [_text("see [Image #1]"), {"type": "image"}, _text("and this")],
            "see [Image #1]\nand this",
        ),
    ],
)
def test_prompt_text_reads_commands_pastes_and_blocks(
    content: object,
    expected: str,
) -> None:
    """A command prompt reads as typed; pasted text loses its tags only."""
    assert claude.prompt_text(content) == expected


def test_question_answers_and_a_refusal_become_prompts() -> None:
    """The user's answers survive as a prompt, notes included, and so does a refusal."""
    ask: dict[str, object] = {
        "type": "tool_use",
        "id": "q1",
        "name": "AskUserQuestion",
        "input": {},
    }
    result = {
        "answers": {"Which home?": "llm-shared", "Which name?": "copy-conversation"},
        "annotations": {"Which name?": {"notes": "short"}},
    }
    text = _render(
        _prompt("go"),
        _assistant(ask),
        _line(
            type="user",
            message={"content": [{"type": "tool_result", "tool_use_id": "q1"}]},
            toolUseResult=result,
        ),
        _assistant(
            {"type": "tool_use", "id": "q2", "name": "AskUserQuestion", "input": {}},
        ),
        _line(
            type="user",
            message={
                "content": [
                    {"type": "tool_result", "tool_use_id": "q2", "is_error": True},
                ],
            },
        ),
        _assistant(
            {"type": "tool_use", "id": "q3", "name": "AskUserQuestion", "input": {}},
        ),
        _line(
            type="user",
            message={"content": [{"type": "tool_result", "tool_use_id": "q3"}]},
            toolUseResult="text",
        ),
    )

    assert text == (
        "❯ go\n\n"
        "❯ User answered Claude's questions:\n"
        "  · Which home? → llm-shared\n"
        "  · Which name? → copy-conversation; notes: short\n\n"
        "❯ User declined to answer Claude's questions."
    )


def test_entries_outside_the_visible_conversation_are_left_out() -> None:
    """Subagents, injected text, summaries, local commands and bad lines render nothing."""
    text = _render(
        "",
        "{not json",
        "[1, 2]",
        _prompt("from a subagent", isSidechain=True),
        _assistant(_text("subagent answer"), isSidechain=True),
        _prompt("skill body", isMeta=True),
        _prompt("summary", isCompactSummary=True),
        _line(
            type="user",
            message={"content": "<local-command-stdout>copied</local-command-stdout>"},
        ),
        _assistant(_text("  ")),
        _line(type="file-history-snapshot"),
        _prompt("kept"),
    )

    assert text == "❯ kept"


def test_a_trailing_copy_request_is_cut_with_its_turn() -> None:
    """The copy ends on the conversation, not on the request that made it."""
    text = _render(
        _prompt("hello"),
        _assistant(_text("hi")),
        _prompt("<command-name>/copy-conversation</command-name>"),
        _assistant(_text("Copying.")),
    )

    assert text == "❯ hello\n\n● hi"


def test_an_earlier_copy_request_is_kept() -> None:
    """Only the last prompt is checked, so an older copy request stays."""
    text = _render(_prompt("/copy-conversation"), _prompt("next"))

    assert text == "❯ /copy-conversation\n\n❯ next"


@pytest.mark.parametrize(
    ("milliseconds", "expected"),
    [(45_000, "45s"), (775_011, "12m 55s"), (3_725_000, "1h 2m 5s"), (0, "0s")],
)
def test_format_duration_follows_claude_code(milliseconds: int, expected: str) -> None:
    """Durations print in hours, minutes and seconds, the largest unit first."""
    assert claude.format_duration(milliseconds) == expected


def test_closing_line_without_a_usable_time_or_duration() -> None:
    """A missing time drops the end time; a missing duration counts as zero."""
    assert claude.closing_line(45_000, "", UTC) == "✻ Worked for 45s"
    assert (
        _render(_line(type="system", subtype="turn_duration", durationMs="x"))
        == "✻ Worked for 0s"
    )


def test_render_block_keeps_blank_lines_empty() -> None:
    """Indentation never turns a blank line into trailing spaces."""
    assert claude.render_block("● ", "\nfirst\n\n  second\n") == [
        "● first",
        "",
        "    second",
    ]
    assert claude.render_block("● ", "") == ["● "]


# eof
