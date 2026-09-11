"""Tests for the exported-conversation trimmer.

Cover format detection, the Claude line state machine, the Codex section
filter, the trimming entry point, and the summary line of
`tools.trim_thinking`.
"""

from __future__ import annotations

from datetime import date

import pytest

from tools import trim_thinking as trimmer

# pyright: reportPrivateUsage=false
# ruff: noqa: RUF001, RUF002, SLF001

_CLAUDE_EXPORT = """banner noise before the conversation

❯ add the trimming tool
  and keep it small

  a separate paragraph

● I will add the tool now.
  reading the source first

  a plan paragraph, dropped because a blank line closed the opening

● Bash(pytest -q)
  ⎿ 3 passed

● Read(tools/trim_thinking.py)
  ⎿ read 240 lines

● Done: the trimmer keeps three regions.

  and a second paragraph of the answer

✻ Cogitated for 21m 7s · done 16:16

※ recap: added the trimmer and its tests
  wrapped recap continuation
"""

_TRIMMED_CLAUDE_EXPORT = """❯ add the trimming tool
  and keep it small

  a separate paragraph

● I will add the tool now.
  reading the source first
● Done: the trimmer keeps three regions.

  and a second paragraph of the answer

✻ Cogitated for 21m 7s · done 16:16
※ recap: added the trimmer and its tests
  wrapped recap continuation"""

_CODEX_EXPORT = """# Codex export

preamble metadata

## User

add the trimming tool

## Assistant

I will read the sources first.

## Assistant

**Shell** `rg trim tools/`

## Assistant

**Shell** `pytest -q`

## Assistant

I added the tool and its tests.

## Activity

- ran ruff
"""

_TRIMMED_CODEX_EXPORT = """## User

add the trimming tool

## Assistant

I will read the sources first.

## Assistant

I added the tool and its tests.
"""


def test_detect_format_reads_the_markers_of_each_export() -> None:
    """Detection should follow the marker family present in the source text."""
    assert trimmer.detect_format(_CLAUDE_EXPORT) is trimmer.TranscriptFormat.CLAUDE
    assert trimmer.detect_format(_CODEX_EXPORT) is trimmer.TranscriptFormat.CODEX


def test_detect_format_ignores_headings_that_open_no_codex_section() -> None:
    """A plain Markdown heading should not turn a Claude export into a Codex one."""
    text = "## Notes\n\n● an answer line\n"

    assert trimmer.count_codex_headings(text.splitlines()) == 0
    assert trimmer.detect_format(text) is trimmer.TranscriptFormat.CLAUDE


def test_detect_format_rejects_a_text_without_any_marker() -> None:
    """A text with no marker at all should name both marker families."""
    with pytest.raises(
        trimmer.UnknownTranscriptFormatError,
        match="Unrecognized export",
    ):
        trimmer.detect_format("just some prose\nover two lines\n")


def test_trim_claude_keeps_the_ask_the_opening_and_the_last_answer() -> None:
    """A Claude export should keep the three regions of every turn."""
    assert trimmer.trim_claude_transcript(_CLAUDE_EXPORT) == _TRIMMED_CLAUDE_EXPORT


def test_trim_claude_accepts_the_record_circle_answer_marker() -> None:
    """Both black-circle code points should open an answer block."""
    text = f"❯ ask\n{trimmer.ANSWER_MARKERS[1]}an answer\n  its continuation\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_drops_every_answer_block_but_the_last() -> None:
    """Tool traffic is answer blocks too, and only the closing one is kept."""
    text = (
        "❯ ask\n"
        "● first\n"
        "● Bash(ls)\n"
        "  ⎿ output\n"
        "● Read(file)\n"
        "  ⎿ more output\n"
        "● the real answer\n"
        "✻ done\n"
    )

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n● first\n● the real answer\n✻ done"
    )


def test_trim_claude_stops_the_opening_at_the_first_blank_line() -> None:
    """What the turn said before working is one run, not the whole block."""
    text = "❯ ask\n● opening line\n  still the opening\n\n  dropped\n● answer\n✻ done\n"

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n● opening line\n  still the opening\n● answer\n✻ done"
    )


def test_trim_claude_keeps_a_prompt_block_across_its_blank_lines() -> None:
    """A prompt block runs to the answer that follows it, blank lines included."""
    text = "❯ the question\n   \n  its second paragraph\n● the answer\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_closes_a_turn_on_a_recap_without_a_reflection() -> None:
    """A recap line closes the answer region on its own."""
    text = "❯ ask\n● the answer\n※ recap: the summary\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_rescues_an_indented_recap_line() -> None:
    """A recap line keeps its rescue whether the export indents it or not."""
    text = "❯ ask\n● the answer\n✻ Thinking…\n\n  ※ recap: the summary\n"

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n● the answer\n✻ Thinking…\n  ※ recap: the summary"
    )


def test_trim_claude_keeps_a_turn_that_never_closes() -> None:
    """A transcript cut mid-turn still carries its last answer block."""
    text = "❯ ask\n● first\n● the last answer\n  its continuation\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_keeps_a_prompt_that_never_got_an_answer() -> None:
    """An export ending on the ask still carries that ask."""
    text = "❯ ask\n  its continuation\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_closes_a_turn_on_the_prompt_of_the_next_one() -> None:
    """A turn with no closing line ends where the following turn opens."""
    text = "❯ ask one\n● answer one\n❯ ask two\n● answer two\n✻ done\n"

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_ends_a_recap_at_the_blank_line_under_it() -> None:
    """What follows the recap belongs to no region and is dropped."""
    text = "❯ ask\n● the answer\n✻ done\n\n※ recap: the summary\n\n  dropped tail\n"

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n● the answer\n✻ done\n※ recap: the summary"
    )


def test_trim_claude_keeps_every_section_of_a_turn() -> None:
    """A background command that completes speaks again under the same prompt."""
    text = (
        "❯ ask\n"
        "● opening\n"
        "● the first answer\n"
        "✻ done 9:52\n"
        "※ recap: the first summary\n"
        "● Background command completed\n"
        "● Bash(ls)\n"
        "  ⎿ output\n"
        "● the second answer\n"
        "✻ done 9:55\n"
        "※ recap: the second summary\n"
    )

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n"
        "● opening\n"
        "● the first answer\n"
        "✻ done 9:52\n"
        "※ recap: the first summary\n"
        "● the second answer\n"
        "✻ done 9:55\n"
        "※ recap: the second summary"
    )


def test_trim_claude_opens_a_new_section_after_a_bare_recap() -> None:
    """A recap closes its section on its own, and the turn may hold more."""
    text = (
        "❯ ask\n"
        "● the first answer\n"
        "※ recap: the first summary\n"
        "● the second answer\n"
        "✻ done\n"
    )

    assert trimmer.trim_claude_transcript(text) == text.rstrip("\n")


def test_trim_claude_keeps_a_last_section_that_never_closes() -> None:
    """A turn whose last section is cut short still carries its answer."""
    text = (
        "❯ ask\n"
        "● the first answer\n"
        "✻ done\n"
        "  traffic belonging to no answer\n"
        "● the last answer\n"
        "  its continuation\n"
    )

    assert trimmer.trim_claude_transcript(text) == (
        "❯ ask\n● the first answer\n✻ done\n● the last answer\n  its continuation"
    )


def test_trim_claude_keeps_nothing_before_the_first_prompt() -> None:
    """Every kept region belongs to a turn, and a turn opens on a prompt."""
    text = "banner noise\n● an answer with no question\n✻ done\n"

    assert trimmer.trim_claude_transcript(text) == ""


def test_trim_codex_keeps_the_user_and_assistant_sections() -> None:
    """A Codex export should keep only what the two sides actually said."""
    assert trimmer.trim_codex_transcript(_CODEX_EXPORT) == _TRIMMED_CODEX_EXPORT


def test_trim_codex_keeps_a_user_section_that_never_got_an_answer() -> None:
    """An export ending on the ask still carries that ask."""
    text = "## User\n\nask\n"

    assert trimmer.trim_codex_transcript(text) == text.rstrip("\n")


def test_trim_codex_keeps_two_asks_that_follow_each_other() -> None:
    """A user section closes on the next one, with no assistant in between."""
    text = "## User\n\nask one\n\n## User\n\nask two\n\n## Assistant\n\nthe answer\n"

    assert trimmer.trim_codex_transcript(text) == text.rstrip("\n")


def test_trim_codex_closes_a_turn_on_the_ask_of_the_next_one() -> None:
    """Each turn keeps its own three regions, and turns do not bleed."""
    text = (
        "## User\n\nask one\n\n## Assistant\n\nanswer one\n\n"
        "## User\n\nask two\n\n## Assistant\n\nanswer two\n"
    )

    assert trimmer.trim_codex_transcript(text) == text.rstrip("\n")


def test_trim_transcript_honors_a_forced_format_and_counts_both_sides() -> None:
    """The entry point should skip detection and report the two line counts."""
    result = trimmer.trim_transcript(_CODEX_EXPORT, trimmer.TranscriptFormat.CODEX)

    assert result.transcript_format is trimmer.TranscriptFormat.CODEX
    assert result.text == _TRIMMED_CODEX_EXPORT
    assert result.source_lines == len(_CODEX_EXPORT.splitlines())
    assert result.kept_lines == len(_TRIMMED_CODEX_EXPORT.splitlines())


def test_trim_transcript_detects_the_format_when_none_is_forced() -> None:
    """With no forced format the entry point falls back to detection."""
    result = trimmer.trim_transcript(_CLAUDE_EXPORT)

    assert result.transcript_format is trimmer.TranscriptFormat.CLAUDE
    assert result.text == _TRIMMED_CLAUDE_EXPORT


def test_trim_transcript_refuses_to_publish_an_empty_result() -> None:
    """A source whose sections are all dropped must not overwrite anything."""
    with pytest.raises(trimmer.EmptyTrimResultError, match="kept no line"):
        trimmer.trim_transcript("## Activity\n\n- ran ruff\n")


def test_build_summary_line_reports_the_removed_share() -> None:
    """The summary line should carry the format, the counts, and the share."""
    result = trimmer.trim_transcript(_CLAUDE_EXPORT)
    summary = trimmer.build_summary_line(result)

    assert "trim-thinking (claude)" in summary
    assert f"{result.source_lines} -> {result.kept_lines} lines" in summary
    assert "Ready to paste from clipboard." in summary


def test_build_summary_line_reports_no_share_for_an_empty_source() -> None:
    """An empty source must not divide by zero when building the summary."""
    summary = trimmer.build_summary_line(
        trimmer.TrimResult(
            transcript_format=trimmer.TranscriptFormat.CODEX,
            text="",
            source_lines=0,
            kept_lines=0,
        ),
    )

    assert "0 -> 0 lines, 0 reflection lines removed (0%)" in summary



_DAY = date(2026, 9, 3)
_DATED_EXPORT = """❯ first ask
● opening
● the answer
✻ done

※ recap that precedes the dated turn

❯ 20260903 the dated ask
● opening two
● answer two
✻ done two
"""


def test_date_forms_covers_the_eight_digit_rendering() -> None:
    """One date is recognized only in YYYYMMDD form."""
    assert trimmer.date_forms(_DAY) == {"20260903"}


def test_dated_prompt_drops_every_line_before_it() -> None:
    """The entire prefix goes; the dated prompt and the rest stay."""
    kept = trimmer.drop_lines_before_dated_prompts(
        ["first", "second", "", "❯ 20260903 the ask", "after"],
        [_DAY],
    )

    assert kept == ["❯ 20260903 the ask", "after"]


def test_dated_prompt_is_matched_without_a_marker() -> None:
    """The one-character prompt marker is optional."""
    assert trimmer.drop_lines_before_dated_prompts(
        ["gone", "20260903 bare ask"],
        [_DAY],
    ) == ["20260903 bare ask"]


@pytest.mark.parametrize(
    "line",
    [
        "20261231 another day",
        "260903 six-digit date",
        "1234567 not a date length",
        "❯ 20260903no space after the date",
    ],
)
def test_unmatched_leading_number_keeps_its_predecessor(line: str) -> None:
    """Only a recognized eight-digit date truncates the transcript."""
    assert trimmer.drop_lines_before_dated_prompts(["before", line], [_DAY]) == [
        "before",
        line,
    ]


def test_dated_prompt_on_the_first_line_keeps_the_whole_text() -> None:
    """A dated prompt opening the text leaves no prefix to drop."""
    assert trimmer.drop_lines_before_dated_prompts(
        ["20260903 the ask", "after"],
        [_DAY],
    ) == ["20260903 the ask", "after"]


def test_no_dates_leaves_every_line_in_place() -> None:
    """With no date to match, the trimmed text is returned untouched."""
    lines = ["before", "20260903 the ask"]

    assert trimmer.drop_lines_before_dated_prompts(lines, []) == lines


def test_trim_transcript_applies_the_dated_pass_after_trimming() -> None:
    """The dated pass truncates the ordinarily trimmed text at its match."""
    plain = trimmer.trim_transcript(_DATED_EXPORT)
    dated = trimmer.trim_transcript(_DATED_EXPORT, None, [_DAY])

    assert "※ recap that precedes the dated turn" in plain.text
    assert dated.text == """❯ 20260903 the dated ask
● opening two
● answer two
✻ done two"""
    assert dated.kept_lines < plain.kept_lines


# eof
