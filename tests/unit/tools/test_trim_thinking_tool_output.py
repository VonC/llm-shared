"""Tests for the tool passes of the exported-conversation trimmer.

Cover the two passes of `tools.trim_thinking` that drop tool traffic from a
Claude export before its regions are marked: the tool-block drop, and the cut
of the indented tool-output runs left in any block, a prompt included, with
the order between them.
"""

from __future__ import annotations

import pytest

from tools import trim_thinking as trimmer

# ruff: noqa: RUF001


def test_drop_tool_blocks_replaces_a_block_with_one_blank_line() -> None:
    """A block holding tool output anywhere goes whole, and a blank line stays."""
    lines = [
        "● the plan",
        "● Update(tools/a.py)",
        "  a line before the output",
        "  ⎿ Added 2 lines",
        "  a line after the output",
        "● the answer",
    ]

    assert trimmer.drop_tool_blocks(lines) == ["● the plan", "", "● the answer"]


@pytest.mark.parametrize("line", ["⎿ unindented", "      ⎿ deeply indented"])
def test_drop_tool_blocks_matches_the_output_marker_at_any_indent(line: str) -> None:
    """Zero or more spaces may precede the tool-output marker."""
    assert trimmer.drop_tool_blocks(["● Bash(ls)", line]) == [""]


def test_drop_tool_blocks_keeps_a_block_without_tool_output() -> None:
    """A marker that is not at the start of a line leaves the block in place."""
    lines = ["● the answer mentions ⎿ in passing", "  and x ⎿ too"]

    assert trimmer.drop_tool_blocks(lines) == lines


@pytest.mark.parametrize(
    "closing",
    ["❯ next ask", "✻ done", "※ recap: summary", "  ※ indented recap", "⏺ next"],
)
def test_drop_tool_blocks_ends_a_block_on_the_next_marker(closing: str) -> None:
    """The marker that follows a tool block is not part of it."""
    assert trimmer.drop_tool_blocks(["● Bash(ls)", "  ⎿ output", closing]) == [
        "",
        closing,
    ]


def test_drop_tool_blocks_never_leaves_two_blank_lines() -> None:
    """Blank lines around a dropped block collapse into one."""
    lines = [
        "● the plan",
        "",
        "● Bash(ls)",
        "  ⎿ output",
        "",
        "● Read(a.py)",
        "  ⎿ read 3 lines",
        "",
        "",
        "● the answer",
    ]

    assert trimmer.drop_tool_blocks(lines) == ["● the plan", "", "● the answer"]


def test_drop_tool_blocks_keeps_blank_runs_away_from_a_dropped_block() -> None:
    """Only a replacement collapses blank lines; the ask keeps its own."""
    lines = ["❯ ask", "", "", "  second paragraph", "● the answer"]

    assert trimmer.drop_tool_blocks(lines) == lines


def test_cut_tool_output_runs_drops_the_output_under_an_ask() -> None:
    """Hook output printed under a prompt goes, and one blank line stays."""
    lines = [
        "❯ /resume-session",
        "  ⎿  SessionStart hook ran",
        "     more hook output",
        "",
        "● The tree is clean.",
    ]

    assert trimmer.cut_tool_output_runs(lines) == [
        "❯ /resume-session",
        "",
        "● The tree is clean.",
    ]


@pytest.mark.parametrize("closing", ["● next", "❯ next ask", "✻ done", "plain text"])
def test_cut_tool_output_runs_ends_before_the_next_unindented_line(
    closing: str,
) -> None:
    """Indented and blank lines belong to the run; the first unindented line ends it."""
    lines = [
        "❯ ask",
        "  ⎿  output",
        "      deeper",
        "  indented prose",
        "",
        "   ",
        closing,
    ]

    assert trimmer.cut_tool_output_runs(lines) == ["❯ ask", "", closing]


def test_cut_tool_output_runs_accepts_any_whitespace_indent() -> None:
    """A tab before the marker opens a run as spaces do."""
    assert trimmer.cut_tool_output_runs(["❯ ask", "\t⎿  output", "● next"]) == [
        "❯ ask",
        "",
        "● next",
    ]


@pytest.mark.parametrize(
    "line",
    ["⎿  unindented", "  ⎿ one space after", "  ⎿", "  text then ⎿  marker"],
)
def test_cut_tool_output_runs_needs_an_indent_and_two_spaces(line: str) -> None:
    """Only an indented marker followed by two spaces opens a run."""
    lines = ["❯ ask", line, "  continuation", "● next"]

    assert trimmer.cut_tool_output_runs(lines) == lines


def test_cut_tool_output_runs_never_leaves_two_blank_lines() -> None:
    """A run after a blank line leaves no second blank line."""
    lines = ["❯ ask", "", "  ⎿  output", "", "● the answer"]

    assert trimmer.cut_tool_output_runs(lines) == ["❯ ask", "", "● the answer"]


def test_cut_tool_output_runs_reaches_the_end_of_the_text() -> None:
    """A run with no unindented line under it lasts to the end."""
    lines = ["❯ ask", "  ⎿  output", "  more output"]

    assert trimmer.cut_tool_output_runs(lines) == ["❯ ask", ""]


def test_trim_claude_cuts_output_runs_after_dropping_tool_blocks() -> None:
    """A tool block still goes whole, its call line included, and so does a prompt's output."""
    text = (
        "❯ /resume-session\n"
        "  ⎿  SessionStart hook ran\n"
        "     more hook output\n"
        "\n"
        "● Bash(git status)\n"
        "  ⎿  On branch master\n"
        "\n"
        "● The tree is clean.\n"
        "✻ done\n"
    )

    assert trimmer.trim_claude_transcript(text) == (
        "❯ /resume-session\n\n● The tree is clean.\n✻ done"
    )


def test_trim_claude_keeps_prose_when_a_turn_ends_on_a_tool_block() -> None:
    """A tool call can be neither the opening nor the answer of a turn."""
    text = (
        "❯ ask\n"
        "● Bash(ls)\n"
        "  ⎿ output\n"
        "● the answer so far\n"
        "  its continuation\n"
        "● Bash(pytest)\n"
        "  ⎿ Interrupted\n"
        "✻ done\n"
    )

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n\n● the answer so far\n  its continuation\n\n✻ done"
    )
