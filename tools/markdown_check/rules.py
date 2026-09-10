"""Pure evaluators for the bounded repository Markdown rule catalog."""

from __future__ import annotations

import re
import unicodedata
from itertools import pairwise
from typing import TYPE_CHECKING

from tools.markdown_check.classifier import DocumentClassification, DocumentKind
from tools.markdown_check.models import Finding, InlineCode, MarkdownSource

if TYPE_CHECKING:
    from collections.abc import Sequence

_LINK_LABEL_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")
_UNDERSCORE_STRONG_RE = re.compile(r"(?<![\\_])__(?=\S).+?(?<=\S)__(?!_)")
_WHITESPACE_RE = re.compile(r"\s+")
# Only http and https become autolink literals, so a bare `ftp://` is not a
# bare URL for this rule. The character before the scheme must not be an ASCII
# letter, which is what keeps `xhttps://x` out and lets `view-source:https://x`
# in.
_URL_RE = re.compile(r"https?://[^\s<>()\[\]\"'`]+")
_DEFINITION_RE = re.compile(r"^[ \t]{0,3}\[[^\]]+\]:[ \t]")
_URL_CONTEXTS = ("<", "](", '"', "'")
_AUTOLINK_SPAN_RE = re.compile(r"<[A-Za-z][A-Za-z0-9+.-]{1,31}:[^<>\s]*>")
_SECTION_LEVEL = 2
_MIN_SECTION_COUNT = 2
_BREAK_SPACES = 2


def _finding(source: MarkdownSource, line: int, rule: str, reason: str) -> Finding:
    """Build one finding with the shared stable path representation."""
    return Finding(source.path.as_posix(), line, rule, reason)


def check_md001(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report level skips between consecutive headings."""
    findings: list[Finding] = []
    for previous, heading in pairwise(source.headings):
        if heading.level > previous.level + 1:
            findings.append(
                _finding(
                    source,
                    heading.line,
                    "MD001",
                    f"heading level {heading.level} skips level {previous.level + 1}",
                ),
            )
    return tuple(findings)


def check_md009(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report trailing whitespace other than the hard-break pair."""
    findings: list[Finding] = []
    for line_number, line in enumerate(source.lines, start=1):
        trailing = len(line) - len(line.rstrip())
        if not trailing or trailing == _BREAK_SPACES:
            continue
        if line_number in source.fenced_content_lines | source.indented_code_lines:
            continue
        findings.append(
            _finding(
                source,
                line_number,
                "MD009",
                f"trailing spaces [Expected: 0 or {_BREAK_SPACES}; Actual: {trailing}]",
            ),
        )
    return tuple(findings)


def _linked_url(
    line: str,
    start: int,
    autolinks: Sequence[tuple[int, int]],
) -> bool:
    """Report whether one URL occurrence already sits inside link or tag syntax."""
    if any(open_at < start < close_at for open_at, close_at in autolinks):
        return True
    before = line[:start]
    preceding = before[-1:]
    return before.endswith(_URL_CONTEXTS) or (
        preceding.isascii() and preceding.isalpha()
    )


def _bare_url_spans(line: str) -> tuple[int, ...]:
    """Locate absolute URLs that carry no autolink, link, or definition context."""
    if _DEFINITION_RE.match(line) is not None:
        return ()
    # A nested scheme, `<view-source:https://host>`, puts one URL inside another
    # autolink. Checking only the character before the match would report it.
    autolinks = [span.span() for span in _AUTOLINK_SPAN_RE.finditer(line)]
    return tuple(
        match.start() + 1
        for match in _URL_RE.finditer(line)
        if not _linked_url(line, match.start(), autolinks)
    )


def check_md034(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report bare absolute URLs that are neither autolinks nor link targets."""
    return tuple(
        _finding(source, line_number, "MD034", f"bare URL at column {column}")
        for line_number, line in enumerate(source.prose_lines, start=1)
        for column in _bare_url_spans(line)
    )


def _hidden_from_blank_runs(source: MarkdownSource, line_number: int) -> bool:
    """Report whether one line belongs to code or to leading frontmatter."""
    frontmatter = source.frontmatter
    return line_number in source.fenced_lines | source.indented_code_lines or (
        frontmatter is not None
        and frontmatter.start_line <= line_number <= frontmatter.end_line
    )


def _blank_run_finding(
    source: MarkdownSource,
    end: int,
    length: int,
) -> Finding | None:
    """Build one finding for a closed blank run longer than a single line."""
    if length <= 1:
        return None
    return _finding(
        source,
        end,
        "MD012",
        f"multiple consecutive blank lines [Expected: 1; Actual: {length}]",
    )


def check_md012(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every run of two or more blank lines outside fenced code."""
    candidates: list[Finding | None] = []
    end = 0
    length = 0
    for line_number, line in enumerate(source.lines, start=1):
        if not _hidden_from_blank_runs(source, line_number) and not line.strip():
            end = line_number
            length += 1
            continue
        candidates.append(_blank_run_finding(source, end, length))
        length = 0
    candidates.append(_blank_run_finding(source, end, length))
    return tuple(finding for finding in candidates if finding is not None)


def check_md024(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every exact heading title occurrence after the first."""
    seen: set[str] = set()
    findings: list[Finding] = []
    for heading in source.headings:
        if heading.title in seen:
            findings.append(
                _finding(source, heading.line, "MD024", "duplicate heading content"),
            )
        else:
            seen.add(heading.title)
    return tuple(findings)


def check_md025(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every level-one heading after the document's first title."""
    seen_title = False
    findings: list[Finding] = []
    for heading in source.headings:
        if heading.level != 1:
            continue
        if seen_title:
            findings.append(
                _finding(source, heading.line, "MD025", "multiple level-one headings"),
            )
        seen_title = True
    return tuple(findings)


def check_md032(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report list blocks that touch adjacent non-blank content."""
    findings: list[Finding] = []
    for block in source.list_blocks:
        if block.blank_before and block.blank_after:
            continue
        boundaries: list[str] = []
        if not block.blank_before:
            boundaries.append("before")
        if not block.blank_after:
            boundaries.append("after")
        findings.append(
            _finding(
                source,
                block.start_line,
                "MD032",
                f"list block needs a blank line {' and '.join(boundaries)} it",
            ),
        )
    return tuple(findings)


def check_md033(
    source: MarkdownSource,
    *,
    allowed_elements: frozenset[str] = frozenset(),
) -> tuple[Finding, ...]:
    """Report raw HTML elements not present in the configured allowance."""
    allowed = frozenset(element.lower() for element in allowed_elements)
    return tuple(
        _finding(source, element.line, "MD033", f"raw HTML element <{element.name}>")
        for element in source.raw_html
        if element.name not in allowed
    )


def check_md040(source: MarkdownSource) -> tuple[Finding, ...]:
    """Require every fenced code block to declare a language on its opener."""
    return tuple(
        _finding(source, opener.line, "MD040", "fenced code block has no language")
        for opener in source.fence_openers
        if not opener.info
    )


def _allowed_md038_space(span: InlineCode) -> bool:
    """Recognize genuine code whitespace and required literal-backtick padding."""
    raw = span.raw_content.replace("\n", " ")
    leading = raw.startswith(" ")
    trailing = raw.endswith(" ")
    if not leading and not trailing:
        return True
    if not raw.strip(" "):
        return True
    if not leading or not trailing:
        return False
    if span.value.startswith(" ") or span.value.endswith(" "):
        return True
    core = raw[1:-1]
    return core.startswith("`") or core.endswith("`")


def check_md038(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report unnecessary spaces immediately inside inline-code delimiters."""
    return tuple(
        _finding(
            source,
            span.line,
            "MD038",
            "unnecessary space inside inline-code delimiters",
        )
        for span in source.inline_code
        if not _allowed_md038_space(span)
    )


def check_md050(source: MarkdownSource) -> tuple[Finding, ...]:
    """Require asterisks rather than underscores for strong emphasis."""
    return tuple(
        _finding(
            source,
            line_number,
            "MD050",
            "strong style [Expected: asterisk; Actual: underscore]",
        )
        for line_number, line in enumerate(source.prose_lines, start=1)
        if _UNDERSCORE_STRONG_RE.search(line) is not None
    )


def check_ls001(
    source: MarkdownSource,
    classification: DocumentClassification,
) -> tuple[Finding, ...]:
    """Require one level-one title only for structured documents."""
    if classification.kind is DocumentKind.ADAPTER or any(
        heading.level == 1 for heading in source.headings
    ):
        return ()
    return (_finding(source, 1, "LS001", "structured document needs a title"),)


def check_ls002(
    source: MarkdownSource,
    classification: DocumentClassification,
) -> tuple[Finding, ...]:
    """Require multiple level-two sections only for structured documents."""
    if classification.kind is DocumentKind.ADAPTER:
        return ()
    section_count = sum(heading.level == _SECTION_LEVEL for heading in source.headings)
    if section_count >= _MIN_SECTION_COUNT:
        return ()
    return (
        _finding(source, 1, "LS002", "structured document needs multiple sections"),
    )


def _normalized_title(title: str) -> str:
    """Apply the repository's anchor-style heading normalization."""
    rendered = _LINK_LABEL_RE.sub(r"\1", title)
    rendered = _HTML_TAG_RE.sub("", rendered)
    rendered = rendered.replace("`", "").replace("*", "").replace("_", "").replace("~", "")
    kept = "".join(
        character
        for character in rendered.casefold()
        if character == "-"
        or character.isspace()
        or unicodedata.category(character)[0] in {"L", "N"}
    )
    return _WHITESPACE_RE.sub("-", kept.strip())


def check_ls003(source: MarkdownSource) -> tuple[Finding, ...]:
    """Report every anchor-normalized heading title occurrence after the first."""
    seen: set[str] = set()
    findings: list[Finding] = []
    for heading in source.headings:
        normalized = _normalized_title(heading.title)
        if normalized in seen:
            findings.append(
                _finding(
                    source,
                    heading.line,
                    "LS003",
                    "heading title is not globally unique",
                ),
            )
        else:
            seen.add(normalized)
    return tuple(findings)


def evaluate_rules(
    source: MarkdownSource,
    classification: DocumentClassification,
    *,
    allowed_html: frozenset[str] = frozenset(),
) -> tuple[Finding, ...]:
    """Evaluate every Step 1 rule against one already-parsed source."""
    return (
        *check_md001(source),
        *check_md009(source),
        *check_md012(source),
        *check_md024(source),
        *check_md025(source),
        *check_md032(source),
        *check_md033(source, allowed_elements=allowed_html),
        *check_md034(source),
        *check_md038(source),
        *check_md040(source),
        *check_md050(source),
        *check_ls001(source, classification),
        *check_ls002(source, classification),
        *check_ls003(source),
    )


__all__ = [
    "check_ls001",
    "check_ls002",
    "check_ls003",
    "check_md001",
    "check_md009",
    "check_md012",
    "check_md024",
    "check_md025",
    "check_md032",
    "check_md033",
    "check_md034",
    "check_md038",
    "check_md040",
    "check_md050",
    "evaluate_rules",
]


# eof
