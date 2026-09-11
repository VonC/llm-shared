"""trim_thinking.py.

Trim the reflection blocks out of one exported LLM conversation.

Two export shapes are supported, and the format is detected from the markers
present in the source text unless the caller forces one:

- A Claude export keeps three regions of every turn, and drops the rest. A
  turn opens on a prompt line (U+276F prefix) and its regions are: the ask,
  running to the first answer marker (U+25CF or U+23FA) with its blank lines
  intact; the opening, the non-blank run under that marker; and the answer,
  the last answer block of every section of the turn, each through the
  reflection line (U+273B) that closes it and the recap line (U+203B) under
  that. A turn holds one section per closing line, since a background
  command that completes speaks again under the same prompt. Every earlier
  answer block of a section is tool traffic and resets the answer region,
  which is what makes a working session shrink rather than merely lose its
  reasoning.
- A Codex export keeps the same three regions of every turn: the `## User`
  section up to the first `## Assistant` heading, that first assistant
  section, and the last assistant section of the turn. Every assistant
  heading in between is a step the turn took, not its answer, so it resets
  the region. `## Activity` and anything else is dropped.

The module holds the parsing only. Clipboard access and the command line live
in `tools.trim_thinking_cli`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence
    from datetime import date

# Answer and tool blocks are rendered with a black circle. Both code points
# appear across Claude Code versions, and they are visually identical.
ANSWER_MARKERS = ("● ", "⏺ ")
REFLECTION_MARKER = "✻ "
# The prompt prefix is a heavy right-pointing angle ornament, U+276F, which
# ruff reports as confusable with the plain greater-than sign.
PROMPT_MARKER = "❯ "  # noqa: RUF001
# The recap prefix is a reference mark, U+203B, opening the recap line that
# Claude Code prints under the reflection line of a turn.
RECAP_MARKER = "※ "

CODEX_SECTION_HEADINGS = frozenset({"user", "assistant", "activity"})

_CODEX_HEADING_PATTERN = re.compile(r"^##\s+(?P<name>\S.*?)\s*$")
_BLANK_LINE_PATTERN = re.compile(r"^\s*$")
# A dated prompt opens with an optional one-character marker and its space,
# then an eight-digit YYYYMMDD date followed by a space.
_DATED_LINE_PATTERN = re.compile(r"^(?:.\s)?(?P<date>\d{8})\s")

_PERCENT = 100


class TrimThinkingError(Exception):
    """Base exception for the transcript trimming tool."""


class UnknownTranscriptFormatError(TrimThinkingError):
    """Raised when the source text carries no Claude and no Codex marker."""


class EmptyTrimResultError(TrimThinkingError):
    """Raised when trimming keeps nothing, so no result can be published."""


class TranscriptFormat(StrEnum):
    """Export format of the conversation being trimmed."""

    CLAUDE = "claude"
    CODEX = "codex"


@dataclass(frozen=True)
class TrimResult:
    """Outcome of one trimming run.

    Attributes:
        transcript_format: Format the source text was trimmed as.
        text: Trimmed conversation, ready to publish.
        source_lines: Line count of the source text.
        kept_lines: Line count of the trimmed text.
    """

    transcript_format: TranscriptFormat
    text: str
    source_lines: int
    kept_lines: int


def _is_blank(line: str) -> bool:
    """Report whether one line is empty or holds whitespace only."""
    return _BLANK_LINE_PATTERN.match(line) is not None


def _starts_answer(line: str) -> bool:
    """Report whether one line opens an answer or tool block."""
    return line.startswith(ANSWER_MARKERS)


def _starts_recap(line: str) -> bool:
    """Report whether one line is a recap line, indented or not."""
    return line.lstrip().startswith(RECAP_MARKER)


def _closes_answer(line: str) -> bool:
    """Report whether one line closes a turn, as a reflection or a recap."""
    return line.startswith(REFLECTION_MARKER) or _starts_recap(line)


def _codex_heading_name(line: str) -> str | None:
    """Return the heading text of one `## ` line, or None when there is none."""
    match = _CODEX_HEADING_PATTERN.match(line)
    if match is None:
        return None
    return match.group("name")


def count_claude_markers(lines: Sequence[str]) -> int:
    """Count the lines carrying one of the Claude export markers."""
    return sum(
        1
        for line in lines
        if line.startswith(
            (*ANSWER_MARKERS, REFLECTION_MARKER, PROMPT_MARKER, RECAP_MARKER),
        )
    )


def count_codex_headings(lines: Sequence[str]) -> int:
    """Count the lines opening one of the known Codex export sections."""
    return sum(
        1
        for line in lines
        if (name := _codex_heading_name(line)) is not None
        and name.casefold() in CODEX_SECTION_HEADINGS
    )


def detect_format(text: str) -> TranscriptFormat:
    """Detect the export format of one conversation.

    Args:
        text: Full exported conversation.

    Returns:
        The format whose markers are the most present in the text.

    Raises:
        UnknownTranscriptFormatError: When neither format leaves a marker.
    """
    lines = text.splitlines()
    codex_score = count_codex_headings(lines)
    claude_score = count_claude_markers(lines)

    if codex_score == 0 and claude_score == 0:
        msg = (
            "Unrecognized export: no Claude marker (U+25CF, U+23FA, U+273B, "
            "U+276F) and no Codex section heading (## User, ## Assistant, "
            "## Activity) was found. Force one with --format."
        )
        raise UnknownTranscriptFormatError(msg)

    if codex_score >= claude_score:
        return TranscriptFormat.CODEX
    return TranscriptFormat.CLAUDE


class _ClaudeTrimmer:
    """Scan Claude export lines, keeping the ask, the opening, and the answer.

    A working turn is mostly tool traffic: one answer block per command run,
    each with its output under it. None of that is the answer, and keeping it
    was why trimming a long session removed barely a line. Three regions
    survive a turn, and the trimmer marks their line numbers rather than
    copying text, so regions that overlap are emitted once:

    - the ask: from the prompt marker through the first answer marker,
      blank lines included, since the question is read as it was written;
    - the opening: the non-blank run under that first answer marker, which is
      what the turn said before it started working;
    - the answer: the last answer block of every section of the turn, each
      through the reflection line that closes it and the recap line under
      that. A turn holds as many sections as it has closing lines, because a
      background command that completes speaks again under the same prompt,
      so the scan runs to the last closing line and not to the first. Every
      earlier answer block of a section resets the region, so one block per
      section survives.
    """

    def __init__(self, lines: Sequence[str]) -> None:
        """Store the source lines and start with nothing marked."""
        self._lines = list(lines)
        self._kept: set[int] = set()

    def trim(self) -> list[str]:
        """Return the kept lines, in source order."""
        index = 0
        while index < len(self._lines):
            if self._lines[index].startswith(PROMPT_MARKER):
                index = self._keep_turn(index)
            else:
                index += 1
        return [self._lines[i] for i in sorted(self._kept)]

    def _keep_turn(self, start: int) -> int:
        """Mark the three kept regions of one turn, and report where it ends.

        Args:
            start: Index of the prompt marker opening the turn.

        Returns:
            The index to resume scanning from.
        """
        index = self._keep_ask(start)
        if index >= len(self._lines):
            return index
        first_answer = index
        index = self._keep_opening(first_answer + 1)
        return self._keep_answer(first_answer)

    def _keep_ask(self, start: int) -> int:
        """Mark the prompt through the first answer marker, blanks included.

        Args:
            start: Index of the prompt marker.

        Returns:
            Index of that first answer marker, or the line count when the
            turn holds none.
        """
        index = start
        while index < len(self._lines) and not _starts_answer(self._lines[index]):
            self._kept.add(index)
            index += 1
        if index < len(self._lines):
            self._kept.add(index)
        return index

    def _keep_opening(self, start: int) -> int:
        """Mark the non-blank run under the first answer marker.

        Args:
            start: Index of the line after that answer marker.

        Returns:
            The index of the blank line that closed the run.
        """
        index = start
        while index < len(self._lines):
            line = self._lines[index]
            if _is_blank(line) or _starts_answer(line) or _closes_answer(line):
                break
            self._kept.add(index)
            index += 1
        return index

    def _keep_answer(self, first_answer: int) -> int:
        """Mark the last answer block of every section, and the lines closing it.

        A turn is not one section. A background command that completes speaks
        again under the same prompt, and that block closes with a reflection
        line of its own, so a turn carries as many sections as it has closing
        lines. Scanning therefore runs to the last of them: stopping at the
        first dropped every later section whole.

        Args:
            first_answer: Index of the first answer marker of the turn.

        Returns:
            The index to resume scanning from.
        """
        region = [first_answer]
        index = first_answer + 1
        while index < len(self._lines):
            line = self._lines[index]
            if line.startswith(PROMPT_MARKER):
                break
            if _starts_answer(line):
                # A new answer block: everything gathered so far was tool
                # traffic, so it is dropped and the region restarts here.
                region = [index]
                index += 1
                continue
            if _closes_answer(line):
                region.append(index)
                index = self._extend_with_recap(line, index, region)
                self._kept.update(region)
                # The section is closed, but the turn may open another one,
                # so the scan carries on with nothing gathered. What follows
                # a closing line belongs to no answer until a marker opens
                # the next block.
                region = []
                continue
            if region:
                region.append(index)
            index += 1
        # A turn or a section cut short carries no closing line; its last
        # block still is the answer, so it is kept rather than lost.
        self._kept.update(region)
        return index

    def _extend_with_recap(self, line: str, index: int, region: list[int]) -> int:
        """Add the recap line under a reflection line, when there is one.

        Args:
            line: The closing line already added to the region.
            index: Index of that closing line.
            region: Indices of the region being built, extended in place.

        Returns:
            The index to resume scanning from.
        """
        if not line.startswith(REFLECTION_MARKER):
            return index + 1
        lookahead = index + 1
        while lookahead < len(self._lines) and _is_blank(self._lines[lookahead]):
            lookahead += 1
        if lookahead >= len(self._lines) or not _starts_recap(self._lines[lookahead]):
            return index + 1
        region.append(lookahead)
        lookahead += 1
        while lookahead < len(self._lines):
            following = self._lines[lookahead]
            if (
                _is_blank(following)
                or _starts_answer(following)
                or following.startswith(PROMPT_MARKER)
            ):
                break
            region.append(lookahead)
            lookahead += 1
        return lookahead


def trim_claude_transcript(text: str) -> str:
    """Drop the reflection bodies of one Claude export."""
    return "\n".join(_ClaudeTrimmer(text.splitlines()).trim())


def _is_codex_assistant(line: str) -> bool:
    """Report whether one line opens a Codex assistant section."""
    name = _codex_heading_name(line)
    return name is not None and name.casefold() == "assistant"


def _is_codex_user(line: str) -> bool:
    """Report whether one line opens a Codex user section."""
    name = _codex_heading_name(line)
    return name is not None and name.casefold() == "user"


class _CodexTrimmer:
    """Scan Codex export lines, keeping the ask, the opening, and the answer.

    A Codex turn opens one assistant section per step it takes, so a working
    session carries hundreds of them and keeping every one trimmed nothing.
    The three regions mirror the Claude side, and are marked by line number
    so that a turn holding a single assistant section emits it once:

    - the ask: the user section, up to the first assistant heading;
    - the opening: that first assistant heading and its body, to the next
      heading of any kind;
    - the answer: the last assistant heading of the turn and its body. Every
      earlier assistant heading resets the region, so the steps in between
      are dropped and only the section that closes the turn survives.
    """

    def __init__(self, lines: Sequence[str]) -> None:
        """Store the source lines and start with nothing marked."""
        self._lines = list(lines)
        self._kept: set[int] = set()

    def trim(self) -> list[str]:
        """Return the kept lines, in source order."""
        index = 0
        while index < len(self._lines):
            if _is_codex_user(self._lines[index]):
                index = self._keep_turn(index)
            else:
                index += 1
        return [self._lines[i] for i in sorted(self._kept)]

    def _keep_turn(self, start: int) -> int:
        """Mark the three regions of one turn, and report where it ends.

        Args:
            start: Index of the user heading opening the turn.

        Returns:
            Index of the heading that closes the turn, or the line count.
        """
        first_assistant = self._keep_ask(start)
        if first_assistant >= len(self._lines):
            return first_assistant
        self._keep_opening(first_assistant)
        return self._keep_answer(start, first_assistant)

    def _keep_ask(self, start: int) -> int:
        """Mark the user section, up to the first assistant heading.

        Args:
            start: Index of the user heading.

        Returns:
            Index of that first assistant heading, or the line count when the
            turn holds none.
        """
        index = start
        while index < len(self._lines) and not _is_codex_assistant(
            self._lines[index],
        ):
            if index > start and _is_codex_user(self._lines[index]):
                break
            self._kept.add(index)
            index += 1
        return index

    def _keep_opening(self, first_assistant: int) -> None:
        """Mark the first assistant section, to the next heading of any kind.

        Args:
            first_assistant: Index of that first assistant heading.
        """
        self._kept.add(first_assistant)
        index = first_assistant + 1
        while (
            index < len(self._lines) and _codex_heading_name(self._lines[index]) is None
        ):
            self._kept.add(index)
            index += 1

    def _keep_answer(self, start: int, first_assistant: int) -> int:
        """Mark the last assistant section of the turn.

        Args:
            start: Index of the user heading opening the turn.
            first_assistant: Index of the first assistant heading.

        Returns:
            Index of the heading that closes the turn, or the line count.
        """
        last_assistant = first_assistant
        index = first_assistant
        while index < len(self._lines):
            line = self._lines[index]
            if index > start and _is_codex_user(line):
                break
            if _is_codex_assistant(line):
                # Another step of the same turn: what came before it was
                # working, not answering, so the region restarts here.
                last_assistant = index
            index += 1
        turn_end = index

        self._kept.add(last_assistant)
        index = last_assistant + 1
        while index < turn_end:
            # No assistant heading can remain, so any heading here opens a
            # section that is neither the ask nor the answer, `## Activity`
            # among them, and it closes the region.
            if _codex_heading_name(self._lines[index]) is not None:
                break
            self._kept.add(index)
            index += 1
        return turn_end


def trim_codex_transcript(text: str) -> str:
    """Keep the ask, the opening, and the closing answer of each Codex turn."""
    return "\n".join(_CodexTrimmer(text.splitlines()).trim())


_TRIMMERS: dict[TranscriptFormat, Callable[[str], str]] = {
    TranscriptFormat.CLAUDE: trim_claude_transcript,
    TranscriptFormat.CODEX: trim_codex_transcript,
}


def date_forms(day: date) -> frozenset[str]:
    """Return the digit string one date is recognized as.

    Args:
        day: The date a dated prompt line may carry.

    Returns:
        Its `YYYYMMDD` rendering.
    """
    return frozenset({day.strftime("%Y%m%d")})


def drop_lines_before_dated_prompts(
    lines: Sequence[str],
    dates: Iterable[date],
) -> list[str]:
    """Drop every line before the first prompt bearing one of these dates.

    A dated prompt is a line whose first token, after an optional one-character
    marker such as the Claude prompt ornament, is a date followed by a space.
    Only the dates given are recognized, so an unrelated number opening a line
    keeps the transcript unchanged.

    Args:
        lines: Lines of the already trimmed conversation.
        dates: Dates a prompt line may be stamped with.

    Returns:
        The lines from the first matching dated prompt onward, or all lines
        when no dated prompt matches.
    """
    wanted: set[str] = set()
    for day in dates:
        wanted |= date_forms(day)
    if not wanted:
        return list(lines)
    for index, line in enumerate(lines):
        match = _DATED_LINE_PATTERN.match(line)
        if match is not None and match.group("date") in wanted:
            return list(lines[index:])
    return list(lines)


def trim_transcript(
    text: str,
    transcript_format: TranscriptFormat | None = None,
    dates: Iterable[date] = (),
) -> TrimResult:
    """Trim one exported conversation.

    Args:
        text: Full exported conversation.
        transcript_format: Format to apply. Detected from the text when None.
        dates: Dates whose first matching prompt drops everything before it,
            applied once the ordinary trimming is done.

    Returns:
        The trimmed text with the line counts of both sides.

    Raises:
        EmptyTrimResultError: When trimming keeps no line at all.
    """
    resolved = transcript_format or detect_format(text)
    trimmed = _TRIMMERS[resolved](text)
    # split("\n"), not splitlines(): the pass must round-trip the text exactly,
    # and splitlines() would swallow the trailing newline a kept blank line
    # leaves behind.
    trimmed = "\n".join(
        drop_lines_before_dated_prompts(trimmed.split("\n"), dates),
    )

    if not trimmed.strip():
        msg = (
            f"Trimming this text as a {resolved.value} export kept no line. "
            "The source is left untouched."
        )
        raise EmptyTrimResultError(msg)

    return TrimResult(
        transcript_format=resolved,
        text=trimmed,
        source_lines=len(text.splitlines()),
        kept_lines=len(trimmed.splitlines()),
    )


def build_summary_line(result: TrimResult) -> str:
    """Build the single stdout line printed once the clipboard is set."""
    removed = result.source_lines - result.kept_lines
    share = (
        round(removed * _PERCENT / result.source_lines) if result.source_lines else 0
    )
    return (
        f"trim-thinking ({result.transcript_format.value}): "
        f"{result.source_lines} -> {result.kept_lines} lines, "
        f"{removed} reflection lines removed ({share}%). "
        "Ready to paste from clipboard."
    )


# eof
