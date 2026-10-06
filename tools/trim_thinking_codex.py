"""Codex side of the exported-conversation trimmer.

Split out of ``tools.trim_thinking`` so that module stays under the repository
line budget. It holds the Codex section vocabulary, which format detection
reads too, and the trimmer that keeps the ask, the opening, and the closing
answer of every Codex turn; ``trim_transcript`` dispatches to it.

Fix: a message sent while a turn is working is exported as a user section
followed by the `## Activity` and `## Reasoning` sections the turn was already
writing, before any assistant heading. The ask ran to that assistant heading
and kept them; it now stops at the first step heading, so they are dropped
like every other step.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# Sections a Codex turn writes while working rather than speaking: its tool
# activity and its reasoning summaries. A message sent mid-turn is followed
# by them before any assistant heading, so they close the ask.
CODEX_STEP_HEADINGS = frozenset({"activity", "reasoning"})
CODEX_SECTION_HEADINGS = frozenset({"user", "assistant"}) | CODEX_STEP_HEADINGS

_CODEX_HEADING_PATTERN = re.compile(r"^##\s+(?P<name>\S.*?)\s*$")


def codex_heading_name(line: str) -> str | None:
    """Return the heading text of one `## ` line, or None when there is none."""
    match = _CODEX_HEADING_PATTERN.match(line)
    if match is None:
        return None
    return match.group("name")


def _is_codex_assistant(line: str) -> bool:
    """Report whether one line opens a Codex assistant section."""
    name = codex_heading_name(line)
    return name is not None and name.casefold() == "assistant"


def _is_codex_user(line: str) -> bool:
    """Report whether one line opens a Codex user section."""
    name = codex_heading_name(line)
    return name is not None and name.casefold() == "user"


def _is_codex_step(line: str) -> bool:
    """Report whether one line opens a Codex activity or reasoning section."""
    name = codex_heading_name(line)
    return name is not None and name.casefold() in CODEX_STEP_HEADINGS


class _CodexTrimmer:
    """Scan Codex export lines, keeping the ask, the opening, and the answer.

    A Codex turn opens one assistant section per step it takes, so a working
    session carries hundreds of them and keeping every one trimmed nothing.
    The three regions mirror the Claude side, and are marked by line number
    so that a turn holding a single assistant section emits it once:

    - the ask: the user section, up to the first assistant, activity or
      reasoning heading;
    - the opening: that first assistant heading and its body, to the next
      heading of any kind;
    - the answer: the last assistant heading of the turn and its body. Every
      earlier assistant heading resets the region, so the steps in between
      are dropped and only the section that closes the turn survives.

    Fix: the ask stopped only at an assistant heading, so a message sent
    mid-turn kept the activity and reasoning sections the export writes
    under it before the assistant speaks again. It now stops at the first
    of them.
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

        A message sent while the turn is working is exported with the
        activity and reasoning sections the turn was already writing under
        it, before the first assistant heading. Marking stops at the first of
        those step headings, while the scan still runs to the assistant
        heading. Any other `## ` line is the user's own Markdown and stays in
        the ask.

        Args:
            start: Index of the user heading.

        Returns:
            Index of that first assistant heading, or the line count when the
            turn holds none.
        """
        index = start
        asking = True
        while index < len(self._lines):
            line = self._lines[index]
            if _is_codex_assistant(line) or (index > start and _is_codex_user(line)):
                break
            if _is_codex_step(line):
                # The turn was working when the message arrived: what follows
                # is its activity, not the ask.
                asking = False
            if asking:
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
            index < len(self._lines) and codex_heading_name(self._lines[index]) is None
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
            if codex_heading_name(self._lines[index]) is not None:
                break
            self._kept.add(index)
            index += 1
        return turn_end


def trim_codex_transcript(text: str) -> str:
    """Keep the ask, the opening, and the closing answer of each Codex turn."""
    return "\n".join(_CodexTrimmer(text.splitlines()).trim())


# eof
