"""Locate owned JSON values by key path, with their spans.

Step 6 of v0.14.0 version-sources. `json` gives a file's meaning; this scanner
finds where an owned value is written, so an edit replaces only those
characters. One pass of a token expression over the decoded text keeps a
stack of open objects and arrays, each object remembering the key path that
reaches it and its last key. A value whose key path is owned is recorded with
its span: the content between a string's quotes, or the whole text of any
other value, so the caller checks the parsed type. Keys are compared after
their escapes are decoded, as `json` reads them.

`json` keeps the last of duplicate keys silently, so a second value on an
owned path fails as ambiguous; duplicates elsewhere are ignored. The caller
parses the text with `json` first, so the scanner only rejects what it relies
on: a root that is not one object. `byte_spans` also requires each located
string to equal its parsed value, so an escape inside an owned value fails,
and maps every span to bytes in one walk, so several edits of one file
compose from one original. Each character is matched once: linear in the
text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from tools.release_workflow.sources.model import SourceError, Span, to_byte_spans

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

type JsonPath = tuple[str, ...]

_SPACE = " \t\r\n"
_TOKEN = re.compile(r'[ \t\r\n]*(?:"(?P<string>[^"\\]*(?:\\.[^"\\]*)*)"|(?P<open>[{\[])|(?P<close>[}\]])|(?P<comma>,)|(?P<colon>:)'
                    r'|(?P<scalar>[^ \t\r\n{}\[\]:,"]+))')
_NOT_ONE_OBJECT = "is not one JSON object"


def spell(path: JsonPath) -> str:
    """Spell a key path as JSON accessors, such as `packages[""].version`."""
    return "".join(f".{key}" if key.isidentifier() else f"[{json.dumps(key)}]" for key in path).removeprefix(".")


@dataclass
class _Frame:
    """One open object or array: the owned-path prefix reaching it, its last key, and the owned value it is."""

    path: JsonPath | None
    is_object: bool
    owned: JsonPath | None
    start: int
    key: str = ""
    expect_key: bool = True


@dataclass
class _Scanner:
    """The key-path stack of one pass and the spans recorded on owned paths."""

    owned: frozenset[JsonPath]
    prefixes: frozenset[JsonPath]
    found: dict[JsonPath, Span] = field(default_factory=dict[JsonPath, Span])
    stack: list[_Frame] = field(default_factory=list[_Frame])
    closed: bool = False

    def _value_path(self) -> JsonPath | None:
        """Return the key path of the value about to be read, or `None` below an array or an unowned prefix."""
        if not self.stack:
            return ()
        frame = self.stack[-1]
        return None if frame.path is None or not frame.is_object else (*frame.path, frame.key)

    def accepts(self, match: re.Match[str]) -> bool:
        """Tell whether a token may come now: inside the root object, or as the `{` opening it."""
        return bool(self.stack) or (not self.closed and match["open"] == "{")

    def _record(self, path: JsonPath | None, span: Span) -> None:
        """Keep the span of an owned value; a second value on the same path is ambiguous."""
        if path is None or path not in self.owned:
            return
        if path in self.found:
            msg = f"{spell(path)} is ambiguous: the key appears more than once and json keeps only the last; remove the duplicate"
            raise SourceError(msg)
        self.found[path] = span

    def string(self, match: re.Match[str]) -> None:
        """Read a key, or a string value with the span of its content."""
        frame = self.stack[-1]
        if frame.is_object and frame.expect_key:
            raw = match["string"]
            frame.key = json.loads(f'"{raw}"') if "\\" in raw else raw
            frame.expect_key = False
            return
        self._record(self._value_path(), Span(*match.span("string")))

    def scalar(self, match: re.Match[str]) -> None:
        """Read a number or literal value with the span of its text."""
        self._record(self._value_path(), Span(*match.span("scalar")))

    def open(self, match: re.Match[str]) -> None:
        """Enter an object or array, tracking its path only while it can lead to an owned path."""
        path = self._value_path()
        tracked = path if path in self.prefixes else None
        owned = path if path in self.owned else None
        self.stack.append(_Frame(tracked, match["open"] == "{", owned, match.start("open")))

    def close(self, match: re.Match[str]) -> None:
        """Leave an object or array, recording its whole text when it is an owned value."""
        frame = self.stack.pop()
        self._record(frame.owned, Span(frame.start, match.end("close")))
        self.closed = not self.stack

    def comma(self, match: re.Match[str]) -> None:
        """Expect the next key of an object; an array needs nothing."""
        del match
        self.stack[-1].expect_key = True


# A colon needs no action: the key read before it already waits for its value.
_HANDLERS: dict[str | None, Callable[[_Scanner, re.Match[str]], None]] = {
    "string": _Scanner.string, "scalar": _Scanner.scalar, "open": _Scanner.open, "close": _Scanner.close, "comma": _Scanner.comma,
}


def locate(text: str, paths: Iterable[JsonPath]) -> dict[JsonPath, Span]:
    """Return the character span of each owned path's value present in one JSON object.

    A string's span is its content between the quotes; any other value's is
    its whole text. A duplicate key on an owned path fails as ambiguous.
    """
    owned = frozenset(paths)
    scanner = _Scanner(owned, frozenset(path[:index] for path in owned for index in range(len(path) + 1)))
    end = len(text.rstrip(_SPACE))
    position = 0
    while position < end:
        match = _TOKEN.match(text, position, end)
        if match is None or not scanner.accepts(match):
            msg = f"the text {_NOT_ONE_OBJECT}: unexpected text at character {position}"
            raise SourceError(msg)
        position = match.end()
        handler = _HANDLERS.get(match.lastgroup)
        if handler is not None:
            handler(scanner, match)
    if not scanner.closed:
        msg = f"the text {_NOT_ONE_OBJECT}: it ends before its root object closes"
        raise SourceError(msg)
    return scanner.found


def byte_spans(text: str, bom: bytes, paths: Iterable[JsonPath], values: Mapping[JsonPath, str]) -> dict[JsonPath, Span]:
    """Locate the owned paths, require each string in `values` to read as written and return their byte spans.

    `paths` are every owned path whose duplicates must fail; `values` maps the
    paths to edit to their parsed strings. The byte spans are measured in one
    walk over the text, in the order of `values`.
    """
    spans = locate(text, paths)
    for path, value in values.items():
        span = spans.get(path)
        located = None if span is None else text[span.start:span.end]
        if located != value:
            msg = (f"the {spell(path)} value reads {located!r} but means {value!r}: escape sequences are unsupported; "
                   "write the plain value")
            raise SourceError(msg)
    edited = list(values)
    return dict(zip(edited, to_byte_spans(text, len(bom), [spans[path] for path in edited]), strict=True))


# eof
