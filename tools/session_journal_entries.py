"""Entries of the llm-shared session journal: parse, merge and check, no I/O.

Split from ``tools/session_journal.py``, which keeps the files, the plan and
apply commands and the command line. This module only turns text into entries
and back, and refuses any candidate that would lose an entry: per checkout and
per kind (Pause, Resume), only the entry with the latest timestamp survives,
every surviving entry keeps its exact text, and the entry count must equal
``before - removed + added``.
"""

from __future__ import annotations

import datetime as dt
import os
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

HEADING = re.compile(r"^## (Pause|Resume) by ([a-z0-9][a-z0-9-]*) at (\S+) in `([^`]+)`[ \t]*$")
TITLE = "# Session journal"
FRACTION = re.compile(r"\.(\d+)")
MICROSECOND_DIGITS = 6
CONTROL_LIMIT = 32


class JournalRefusedError(Exception):
    """A check failed before the journal was replaced: the journal is unchanged."""


@dataclass(frozen=True)
class Entry:
    """One journal entry: its exact text and the fields that order it."""

    text: str
    kind: str
    when: dt.datetime
    checkout: str
    origin: str

    @property
    def heading(self) -> str:
        """Return the entry's heading line."""
        return self.text.split("\n", 1)[0]

    @property
    def key(self) -> tuple[str, str]:
        """Return the kind and checkout pair of which only the latest entry survives."""
        return (self.kind, self.checkout)


@dataclass(frozen=True)
class Journal:
    """A parsed journal: the text before its first entry, then its entries."""

    preamble: str
    entries: tuple[Entry, ...]


@dataclass(frozen=True)
class Sources:
    """The entries a plan merges with the live journal, oldest source first."""

    base: Journal
    recovered: tuple[Entry, ...]
    added: tuple[Entry, ...]

    @property
    def requested(self) -> tuple[Entry, ...]:
        """Return every entry the caller asked to keep or add."""
        return (*self.base.entries, *self.recovered, *self.added)


@dataclass(frozen=True)
class Report:
    """What a candidate changes compared with the live journal."""

    before_count: int
    after_count: int
    removed: tuple[str, ...]
    added: tuple[str, ...]
    superseded: tuple[str, ...]

    def summary(self) -> dict[str, object]:
        """Return the fields a manifest records and apply checks again."""
        return {
            "before_count": self.before_count,
            "after_count": self.after_count,
            "removed": list(self.removed),
            "added": list(self.added),
        }


def checkout_key(path: str) -> str:
    """Return a checkout path in the form the filesystem compares (case-folded on Windows)."""
    return os.path.normcase(os.path.normpath(path))


def decode(data: bytes, origin: str, *, entry_file: bool = False) -> str:
    """Decode strict UTF-8 journal text, refusing carriage returns and control characters.

    An entry file may start with a byte order mark and use CRLF line ends, as
    some Windows editors and shells write them: both are dropped. A journal
    copy must already be LF-only.

    Fix: the byte order mark is dropped by the ``utf-8-sig`` codec, so the
    source holds no invisible character.
    """
    try:
        text = data.decode("utf-8-sig" if entry_file else "utf-8")
    except UnicodeDecodeError as error:
        msg = f"{origin}: not UTF-8 ({error})"
        raise JournalRefusedError(msg) from error
    if entry_file:
        text = text.replace("\r\n", "\n")
    if "\r" in text:
        msg = f"{origin}: carriage return found; the journal is LF-only"
        raise JournalRefusedError(msg)
    control = sorted({repr(char) for char in text if ord(char) < CONTROL_LIMIT and char not in "\n\t"})
    if control:
        msg = f"{origin}: control characters {', '.join(control)}"
        raise JournalRefusedError(msg)
    return text


def _parse_when(stamp: str, origin: str) -> dt.datetime:
    """Parse an ISO 8601 timestamp with an offset, cutting fractions to microseconds."""
    normalized = FRACTION.sub(
        lambda match: "." + match[1][:MICROSECOND_DIGITS].ljust(MICROSECOND_DIGITS, "0"),
        stamp,
        count=1,
    )
    try:
        when = dt.datetime.fromisoformat(normalized)
    except ValueError as error:
        msg = f"{origin}: bad timestamp {stamp!r}"
        raise JournalRefusedError(msg) from error
    if when.tzinfo is None:
        msg = f"{origin}: timestamp without offset {stamp!r}"
        raise JournalRefusedError(msg)
    return when


def _blocks(text: str, origin: str) -> tuple[list[str], list[tuple[re.Match[str], list[str]]]]:
    """Split journal text into its preamble lines and one block per entry heading."""
    preamble: list[str] = []
    blocks: list[tuple[re.Match[str], list[str]]] = []
    for line in text.split("\n"):
        if line.startswith("## "):
            heading = HEADING.match(line)
            if heading is None:
                msg = f"{origin}: unrecognized heading {line!r}"
                raise JournalRefusedError(msg)
            blocks.append((heading, [line]))
        elif blocks:
            blocks[-1][1].append(line)
        else:
            preamble.append(line)
    return preamble, blocks


def _entry(heading: re.Match[str], lines: list[str], origin: str) -> Entry:
    """Build one entry from its block, without the blank lines that follow it."""
    while not lines[-1].strip():
        lines.pop()
    kind, _agent, stamp, checkout = heading.groups()
    return Entry("\n".join(lines), kind, _parse_when(stamp, origin), checkout_key(checkout), origin)


def parse_journal(text: str, origin: str) -> Journal:
    """Parse journal text into its preamble and entries, refusing unknown headings."""
    preamble, blocks = _blocks(text, origin)
    entries = tuple(_entry(heading, lines, origin) for heading, lines in blocks)
    return Journal("\n".join(preamble).strip("\n"), entries)


def render(journal: Journal) -> str:
    """Render a journal with one blank line between its blocks and a final newline."""
    if not journal.entries:
        return journal.preamble + "\n"
    return journal.preamble + "\n\n" + "\n\n".join(entry.text for entry in journal.entries) + "\n"


def merge(sources: Iterable[Entry]) -> list[Entry]:
    """Keep the latest entry per kind and checkout, in order of first appearance.

    Identical texts count once. Two different entries of one kind for one
    checkout with the same timestamp cannot be ordered, so they are refused.
    """
    distinct: list[Entry] = []
    seen: set[str] = set()
    for entry in sources:
        if entry.text not in seen:
            seen.add(entry.text)
            distinct.append(entry)
    winners: dict[tuple[str, str], Entry] = {}
    for entry in distinct:
        best = winners.get(entry.key)
        if best is not None and entry.when == best.when:
            msg = f"two different entries share one timestamp: {entry.heading!r} ({best.origin}, {entry.origin})"
            raise JournalRefusedError(msg)
        if best is None or entry.when > best.when:
            winners[entry.key] = entry
    return [entry for entry in distinct if winners[entry.key] is entry]


def _check_kept(reference: Iterable[Entry], result: Sequence[Entry], label: str) -> list[Entry]:
    """Return the reference entries absent from the result, each one superseded.

    Raises:
        JournalRefusedError: a reference entry is absent and the result holds
            no newer entry of the same kind for the same checkout.
    """
    texts = {entry.text for entry in result}
    latest = {entry.key: entry for entry in result}
    missing: list[Entry] = []
    for entry in reference:
        if entry.text in texts:
            continue
        newer = latest.get(entry.key)
        if newer is None or newer.when <= entry.when:
            msg = f"{label} entry would be lost without a newer replacement: {entry.heading!r}"
            raise JournalRefusedError(msg)
        missing.append(entry)
    return missing


def _check_shape(live: Journal, candidate: Journal) -> None:
    """Refuse a candidate without the title, with another preamble, or with duplicate keys."""
    if not candidate.preamble.startswith(TITLE):
        msg = "candidate does not start with the journal title"
        raise JournalRefusedError(msg)
    if live.preamble and live.preamble != candidate.preamble:
        msg = "candidate changes the journal preamble"
        raise JournalRefusedError(msg)
    keys = [entry.key for entry in candidate.entries]
    if len(keys) != len(set(keys)):
        msg = "candidate holds two entries of one kind for one checkout"
        raise JournalRefusedError(msg)


def _headings(entries: Iterable[Entry]) -> tuple[str, ...]:
    """Return the heading line of each entry."""
    return tuple(entry.heading for entry in entries)


def validate(live_text: str, candidate_text: str, requested: Sequence[Entry] = ()) -> Report:
    """Check a candidate against the live journal and report what it changes.

    Every live entry and every requested entry must appear in the candidate
    with its exact text, or be superseded there by a newer entry of the same
    kind for the same checkout. The candidate must count exactly the live
    entries, minus the removed ones, plus the added ones.

    Raises:
        JournalRefusedError: any of these checks fails.
    """
    live = parse_journal(live_text, "live journal")
    candidate = parse_journal(candidate_text, "candidate")
    _check_shape(live, candidate)
    removed = _check_kept(live.entries, candidate.entries, "live")
    superseded = _check_kept(requested, candidate.entries, "requested")
    live_texts = {entry.text for entry in live.entries}
    added = [entry for entry in candidate.entries if entry.text not in live_texts]
    if len(candidate.entries) != len(live.entries) - len(removed) + len(added):
        msg = (
            f"count mismatch: the candidate holds {len(candidate.entries)} entries, not "
            f"{len(live.entries)} - {len(removed)} removed + {len(added)} added"
        )
        raise JournalRefusedError(msg)
    return Report(
        len(live.entries),
        len(candidate.entries),
        _headings(removed),
        _headings(added),
        _headings(superseded),
    )


# eof
