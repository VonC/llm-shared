"""Immutable source tokens and findings for repository Markdown evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import PurePosixPath


@dataclass(frozen=True, slots=True)
class SourceLine:
    """One source line retained for bounded document classification."""

    line: int
    text: str


@dataclass(frozen=True, slots=True)
class Frontmatter:
    """Leading YAML frontmatter bounds and its optional description value."""

    start_line: int
    end_line: int
    description: str | None


@dataclass(frozen=True, slots=True)
class Heading:
    """One ATX heading outside fenced code."""

    line: int
    level: int
    title: str


@dataclass(frozen=True, slots=True)
class FenceOpener:
    """One fenced code block opening marker and its declared info string."""

    line: int
    info: str


@dataclass(frozen=True, slots=True)
class ListBlock:
    """One list block and the blank-line state at its outer boundaries."""

    start_line: int
    end_line: int
    blank_before: bool
    blank_after: bool


@dataclass(frozen=True, slots=True)
class RawHtml:
    """One raw HTML element outside fenced and inline code."""

    line: int
    name: str


@dataclass(frozen=True, slots=True)
class MarkdownLink:
    """One Markdown link target outside fenced and inline code."""

    line: int
    target: str


@dataclass(frozen=True, slots=True)
class InlineCode:
    """One code span with both source content and its parsed Markdown value."""

    line: int
    delimiter_length: int
    raw_content: str
    value: str


@dataclass(frozen=True, slots=True)
class MarkdownSource:
    """The shared immutable representation produced by one Markdown parse."""

    path: PurePosixPath
    lines: tuple[str, ...]
    frontmatter: Frontmatter | None
    headings: tuple[Heading, ...]
    list_blocks: tuple[ListBlock, ...]
    raw_html: tuple[RawHtml, ...]
    links: tuple[MarkdownLink, ...]
    inline_code: tuple[InlineCode, ...]
    prose_lines: tuple[str, ...]
    body_lines: tuple[SourceLine, ...]
    fenced_lines: frozenset[int]
    fenced_content_lines: frozenset[int]
    indented_code_lines: frozenset[int]
    fence_openers: tuple[FenceOpener, ...]


@dataclass(frozen=True, slots=True)
class Finding:
    """One pure rule result with a stable positive source location."""

    path: str
    line: int
    rule: str
    reason: str


__all__ = [
    "FenceOpener",
    "Finding",
    "Frontmatter",
    "Heading",
    "InlineCode",
    "ListBlock",
    "MarkdownLink",
    "MarkdownSource",
    "RawHtml",
    "SourceLine",
]


# eof
