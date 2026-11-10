"""Locate single-line TOML string assignments by table, with their spans.

Step 5 of v0.14.0 version-sources. `tomllib` gives a file's meaning; this
scanner finds where an owned value is written, so an edit replaces only those
characters. It reads the text line by line (LF or CRLF), tracking the current
table header and each `[[array]]` block, and only lines that start a statement
count: a small lexer follows strings, comments and brackets, so a line inside a
multi-line string, an open array or an inline table is never read as a header
or an assignment. A header it cannot read, such as a quoted key, ends the
current table.

The owned field is the single-line `version = "..."` assignment, in a basic or
literal string, written directly in `[project]` or directly in the one
`[[package]]` block whose `name` is the requested package; sub-tables such as
`[package.metadata]` are other tables. Dotted keys, inline tables and
multi-line strings are not located, and the caller fails as an unsupported
layout with the remedy to write the plain assignment. `byte_span` also
requires the located text to equal the parsed value, so an escape sequence
fails, and maps the span to bytes. Each line is scanned once, by regular
expressions that jump between tokens: linear in the text.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.release_workflow.sources.model import SourceError, Span, to_byte_spans

if TYPE_CHECKING:
    from collections.abc import Sequence

_KEY = "version"
_NAME = "name"
_BARE = r"[A-Za-z0-9_-]+"
_DOTTED = rf"{_BARE}(?:[ \t]*\.[ \t]*{_BARE})*"
_TAIL = r"[ \t]*(?:#.*)?"
_TABLE = re.compile(rf"[ \t]*\[[ \t]*(?P<name>{_DOTTED})[ \t]*\]{_TAIL}")
_ARRAY = re.compile(rf"[ \t]*\[\[[ \t]*(?P<name>{_DOTTED})[ \t]*\]\]{_TAIL}")
_ASSIGNMENT = re.compile(rf"""[ \t]*(?P<key>{_BARE})[ \t]*=[ \t]*(?:"(?P<basic>(?:[^"\\]|\\.)*)"|'(?P<literal>[^']*)'){_TAIL}""")
_DOT = re.compile(r"[ \t]*\.[ \t]*")
_SINGLE = ('"', "'")
_TOKENS: dict[str | None, re.Pattern[str]] = {
    None: re.compile(r"\"\"\"|'''|[\"'#\[\]{}]"),
    '"': re.compile(r'\\.|"'),
    "'": re.compile("'"),
    '"""': re.compile(r'\\.|"""'),
    "'''": re.compile("'''"),
}

type _Block = list[tuple[str, Span]]


def _advance(line: str, string: str | None, depth: int) -> tuple[str | None, int]:
    """Follow strings, comments and brackets over one line; return the state at its end.

    A single-line string cannot continue on the next line, so it is closed at
    the line end; a multi-line string and an open bracket carry over.
    """
    position = 0
    while (match := _TOKENS[string].search(line, position)) is not None:
        lexeme = match[0]
        position = match.end()
        if string is not None:
            string = None if lexeme == string else string
        elif lexeme == "#":
            break
        elif lexeme in ('"""', "'''", *_SINGLE):
            string = lexeme
        else:
            depth += 1 if lexeme in "[{" else -1
    return (None if string in _SINGLE else string), depth


def _entered(line: str, table: str, *, array: bool, blocks: list[_Block]) -> _Block | None:
    """Read a header line: start and return a new block when it opens the target table."""
    is_array = line.lstrip(" \t").startswith("[[")
    match = (_ARRAY if is_array else _TABLE).fullmatch(line)
    if match is None or is_array is not array or _DOT.sub(".", match["name"]) != table:
        return None
    block: _Block = []
    blocks.append(block)
    return block


def _record(line: str, offset: int, block: _Block) -> None:
    """Keep a `name` or `version` single-line string assignment written directly in the block."""
    match = _ASSIGNMENT.fullmatch(line)
    if match is not None and match["key"] in (_KEY, _NAME):
        group = "basic" if match["basic"] is not None else "literal"
        start, end = match.span(group)
        block.append((match["key"], Span(offset + start, offset + end)))


def _blocks(text: str, table: str, *, array: bool) -> list[_Block]:
    """Return, for each occurrence of the target table, its direct `name` and `version` assignments."""
    blocks: list[_Block] = []
    current: _Block | None = None
    string: str | None = None
    depth = 0
    offset = 0
    for raw in text.split("\n"):
        line = raw.removesuffix("\r")
        statement = string is None and depth == 0
        if statement and line.lstrip(" \t").startswith("["):
            current = _entered(line, table, array=array, blocks=blocks)
        else:
            if statement and current is not None:
                _record(line, offset, current)
            string, depth = _advance(line, string, depth)
        offset += len(raw) + 1
    return blocks


def _where(table: str, package: str | None) -> str:
    """Name the target table in a diagnostic."""
    return f"[{table}]" if package is None else f"the [[{table}]] block named {package!r}"


def _named(text: str, blocks: Sequence[_Block], table: str, package: str) -> _Block:
    """Return the one block whose only `name` is the package."""
    named = [block for block in blocks if [text[span.start:span.end] for key, span in block if key == _NAME] == [package]]
    if not named:
        msg = f"no [[{table}]] block is named {package!r}"
        raise SourceError(msg)
    if len(named) > 1:
        msg = f"{len(named)} [[{table}]] blocks are named {package!r}: the entry is ambiguous"
        raise SourceError(msg)
    return named[0]


def locate(text: str, table: str, *, package: str | None = None) -> Span:
    """Return the character span of the owned `version` string content.

    Without `package`, the field is `version` directly in `[table]`; with it,
    `version` directly in the one `[[table]]` block whose `name` is `package`.
    """
    blocks = _blocks(text, table, array=package is not None)
    if package is not None:
        blocks = [_named(text, blocks, table, package)]
    where = _where(table, package)
    versions = [span for block in blocks for key, span in block if key == _KEY]
    if not versions:
        msg = (f"no single-line version assignment directly in {where}: dotted keys, inline tables and multi-line "
               f'strings are unsupported; write version = "X.Y.Z" on its own line in {where}')
        raise SourceError(msg)
    if len(versions) > 1:
        msg = f"{where} is ambiguous: {len(versions)} single-line version assignments"
        raise SourceError(msg)
    return versions[0]


def byte_span(text: str, bom: bytes, table: str, value: str, *, package: str | None = None) -> Span:
    """Locate the owned value, require its text to equal the parsed value and return its byte span."""
    span = locate(text, table, package=package)
    located = text[span.start:span.end]
    if located != value:
        msg = (f"the version in {_where(table, package)} reads {located!r} but means {value!r}: escape sequences are "
               "unsupported; write the plain value")
        raise SourceError(msg)
    return to_byte_spans(text, len(bom), [span])[0]


# eof
