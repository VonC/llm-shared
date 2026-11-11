"""Locate wanted XML element text by element path, with byte spans, through expat.

Step 7 of v0.14.0 version-sources. The standard element tree drops formatting
and offsets, so this scanner drives `xml.parsers.expat` and reads
`CurrentByteIndex` at each event: byte offsets in the original content,
byte-order mark and raw CRLF bytes included. It keeps a stack of open
elements named by their slash-joined path (`project/parent/version`), without
namespace processing, and records each element whose path the caller's
expression fully matches.

A recorded value's text is its character data, without the XML whitespace
around it. Its span starts at its first character-data event and ends at the
byte index of its end tag, both moved inward past that whitespace. Its parent
is the start offset of the enclosing element, shared by siblings, which groups
the fields of one `<dependency>`. A comment, CDATA section, processing
instruction or child element inside a recorded element, or text whose span
bytes do not read as the parsed text (an entity or character reference), is
kept as the value's problem: the text stays readable for coordinates, and
`XmlValue.owned` refuses to hand out the span of such a field. Only well-formed
UTF-8 is scanned, declared as UTF-8 or undeclared. Each byte is parsed once and
each recorded value measured once: linear in the content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING
from xml.parsers import expat

from tools.release_workflow.sources.model import SourceError, Span, decode_utf8

if TYPE_CHECKING:
    import re

_UTF8 = frozenset({"utf-8", "utf8"})
_SPACE = " \t\r\n"
_SPACE_BYTES = _SPACE.encode()


@dataclass(frozen=True)
class XmlValue:
    """One wanted element: its path, text, the bytes holding that text and its parent's start offset."""

    path: str
    text: str
    span: Span
    parent: int
    problem: str | None = None

    def owned(self, name: str) -> Span:
        """Return the span of a field versions set will write, or fail when markup makes it unusable."""
        if self.problem is not None:
            msg = f"{name}: <{self.path}> holds {self.problem}, which versions set cannot edit; write the plain value"
            raise SourceError(msg)
        return self.span


@dataclass(frozen=True)
class PomDocument:
    """The root element name and every wanted value, in the order their elements close."""

    root: str
    values: tuple[XmlValue, ...]

    @cached_property
    def _by_path(self) -> dict[str, tuple[XmlValue, ...]]:
        """Index the values by path once."""
        index: dict[str, list[XmlValue]] = {}
        for value in self.values:
            index.setdefault(value.path, []).append(value)
        return {path: tuple(values) for path, values in index.items()}

    def every(self, path: str) -> tuple[XmlValue, ...]:
        """Return every value recorded at a path."""
        return self._by_path.get(path, ())

    def first(self, path: str) -> XmlValue | None:
        """Return the first value recorded at a path, or `None`."""
        values = self.every(path)
        return values[0] if values else None


@dataclass
class _Open:
    """One open element: its path and start offset, and, when wanted, its text so far and any problem."""

    path: str
    start: int
    wanted: bool
    text_start: int | None = None
    chars: list[str] = field(default_factory=list[str])
    problem: str | None = None


class _Scan:
    """The expat handlers of one scan and what they collect."""

    def __init__(self, content: bytes, name: str, wanted: re.Pattern[str]) -> None:
        """Create the parser and attach the handlers."""
        self.content, self.name, self.wanted = content, name, wanted
        self.stack: list[_Open] = []
        self.values: list[XmlValue] = []
        self.root = ""
        self.parser = expat.ParserCreate()
        self.parser.XmlDeclHandler = self.declaration
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.characters
        self.parser.CommentHandler = self.comment
        self.parser.StartCdataSectionHandler = self.cdata
        self.parser.ProcessingInstructionHandler = self.instruction

    def declaration(self, version: str, encoding: str | None, standalone: int) -> None:
        """Refuse a declared encoding other than UTF-8."""
        del version, standalone
        if encoding is not None and encoding.lower() not in _UTF8:
            msg = f'{self.name} declares encoding {encoding!r}: a POM must be UTF-8; save it as UTF-8 and declare encoding="UTF-8"'
            raise SourceError(msg)

    def _flag(self, problem: str) -> None:
        """Keep the first problem of the innermost open element when it is wanted."""
        top = self.stack[-1] if self.stack else None
        if top is not None and top.wanted and top.problem is None:
            top.problem = problem

    def start(self, name: str, attributes: dict[str, str]) -> None:
        """Open an element below its parent's path; markup inside a wanted element is a problem."""
        del attributes
        self._flag(f"child markup <{name}>")
        path = f"{self.stack[-1].path}/{name}" if self.stack else name
        if not self.stack:
            self.root = name
        self.stack.append(_Open(path, self.parser.CurrentByteIndex, self.wanted.fullmatch(path) is not None))

    def characters(self, data: str) -> None:
        """Collect a wanted element's text and remember where it starts."""
        top = self.stack[-1]
        if top.wanted:
            if top.text_start is None:
                top.text_start = self.parser.CurrentByteIndex
            top.chars.append(data)

    def comment(self, data: str) -> None:
        """A comment inside a wanted element is a problem."""
        del data
        self._flag("a comment")

    def cdata(self) -> None:
        """A CDATA section inside a wanted element is a problem."""
        self._flag("a CDATA section")

    def instruction(self, target: str, data: str) -> None:
        """A processing instruction inside a wanted element is a problem."""
        del target, data
        self._flag("a processing instruction")

    def end(self, name: str) -> None:
        """Close an element, recording it when wanted."""
        del name
        closing = self.stack.pop()
        if closing.wanted:
            self.values.append(self._value(closing, self.parser.CurrentByteIndex))

    def _value(self, closing: _Open, end: int) -> XmlValue:
        """Measure a closed wanted element's text without the XML whitespace around it."""
        start = end if closing.text_start is None else closing.text_start
        raw = self.content[start:end]
        lead = len(raw) - len(raw.lstrip(_SPACE_BYTES))
        span = Span(start + lead, start + lead + len(raw.strip(_SPACE_BYTES)))
        text = "".join(closing.chars).strip(_SPACE)
        problem = closing.problem
        if problem is None and self.content[span.start:span.end].decode("utf-8", errors="replace") != text:
            problem = "an entity or character reference"
        parent = self.stack[-1].start if self.stack else -1
        return XmlValue(closing.path, text, span, parent, problem)


def scan(content: bytes, name: str, wanted: re.Pattern[str]) -> PomDocument:
    """Parse well-formed UTF-8 XML once and record every element whose path `wanted` fully matches."""
    decode_utf8(content, name)
    scanner = _Scan(content, name, wanted)
    try:
        scanner.parser.Parse(content, True)  # noqa: FBT003
    except expat.ExpatError as exc:
        msg = f"{name} is not well-formed XML: {exc}; correct the file"
        raise SourceError(msg) from exc
    return PomDocument(scanner.root, tuple(scanner.values))


# eof
