"""Normalize caller-authored review Markdown inside one identified round.

Two normalizations run at the same input boundary, because both fix a lint
the author cannot be expected to think about while writing a review round.
Headings are nested under their generated parent and qualified with the round
identity, so an appended transcript keeps one outline and unique titles
(MD024 and MD025). Bare URLs are wrapped in angle brackets, so a reviewer who
pastes a reference on its own line does not leave the transcript failing
MD034 forever after.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.markdown_check.source import fenced_line_numbers

if TYPE_CHECKING:
    from collections.abc import Iterator

_ATX_HEADING_RE = re.compile(
    r"^(?P<indent>[ \t]{0,3})(?P<marks>#{1,6})[ \t]+"
    r"(?P<title>.*?)(?P<closing>[ \t]+#+[ \t]*)?$",
)
_ROUND_CONTEXT_RE = re.compile(
    r"\s+for step .+?(?: \(exchange \d+\))? "
    r"(?:round \d+|\(round \d+\))(?: \(exchange \d+\))?$",
)
_BARE_URL_RE = re.compile(r"(?:https?|ftp)://[^\s<>`]+")
_CODE_SPAN_RE = re.compile(r"`+")
_LINK_DEFINITION_RE = re.compile(r"^[ \t]{0,3}\[[^\]]+\]:")
# Punctuation that ends a sentence rather than the address inside it.
_TRAILING_PUNCTUATION = ".,;:!?'\")]}>"
_ADDRESS_PREFIX_LENGTH = 2


def _authored_headings(lines: list[str]) -> Iterator[tuple[int, re.Match[str]]]:
    """Yield ATX headings using the checker's shared fence boundaries."""
    fenced = fenced_line_numbers(lines)
    for index, line in enumerate(lines):
        if index + 1 in fenced:
            continue
        heading = _ATX_HEADING_RE.match(line)
        if heading is not None:
            yield index, heading


def _code_span_spans(line: str) -> list[tuple[int, int]]:
    """Return the half-open ranges of inline code spans on one line."""
    spans: list[tuple[int, int]] = []
    markers = list(_CODE_SPAN_RE.finditer(line))
    index = 0
    while index < len(markers) - 1:
        opener = markers[index]
        closer = next(
            (
                candidate
                for candidate in markers[index + 1 :]
                if candidate.group() == opener.group()
            ),
            None,
        )
        if closer is None:
            index += 1
            continue
        spans.append((opener.start(), closer.end()))
        index = markers.index(closer) + 1
    return spans


def _url_end(line: str, match: re.Match[str]) -> int:
    """Return the URL end with sentence punctuation and stray brackets left out."""
    end = match.end()
    while end > match.start() and line[end - 1] in _TRAILING_PUNCTUATION:
        if line[end - 1] == ")" and line.count("(", match.start(), end) >= line.count(
            ")", match.start(), end,
        ):
            break
        end -= 1
    return end


def _already_addressed(line: str, start: int) -> bool:
    """Report whether a URL is already inside a link, an autolink or an attribute."""
    if start == 0:
        return False
    if line[start - 1] in "<\"'":
        return True
    return (
        line[start - 1] == "("
        and start >= _ADDRESS_PREFIX_LENGTH
        and line[start - _ADDRESS_PREFIX_LENGTH] == "]"
    )


def _wrap_line_urls(line: str) -> str:
    """Wrap every bare URL on one line, leaving addressed ones alone."""
    if _LINK_DEFINITION_RE.match(line):
        return line
    spans = _code_span_spans(line)
    rendered = line
    for match in reversed(list(_BARE_URL_RE.finditer(line))):
        start = match.start()
        if _already_addressed(line, start):
            continue
        if any(opener <= start < closer for opener, closer in spans):
            continue
        end = _url_end(line, match)
        rendered = f"{rendered[:start]}<{line[start:end]}>{rendered[end:]}"
    return rendered


def wrap_bare_urls(markdown: str) -> str:
    """Wrap bare URLs in angle brackets, outside fences and code spans.

    This is markdownlint's own MD034 fix. A reviewer pasting a reference on its
    own line is writing prose, not Markdown, and the transcript that keeps the
    line forever is the artifact that fails the lint.

    Args:
        markdown: One caller-authored body.

    Returns:
        The same body with every bare URL wrapped, and every already-linked,
        fenced or code-spanned URL untouched.
    """
    lines = markdown.splitlines()
    fenced = fenced_line_numbers(lines)
    rendered = [
        line if index + 1 in fenced else _wrap_line_urls(line)
        for index, line in enumerate(lines)
    ]
    joined = "\n".join(rendered)
    return f"{joined}\n" if markdown.endswith("\n") else joined


def _qualified_title(title: str, qualifier: str, round_number: int) -> str:
    """Return one idempotent step-and-round-qualified heading title."""
    base = title.rstrip()
    current_suffix = f" for {qualifier} (round {round_number})"
    if base.endswith(current_suffix):
        base = base[: -len(current_suffix)]
    else:
        base = _ROUND_CONTEXT_RE.sub("", base)
    base = re.sub(rf"\s+\(round {round_number}\)$", "", base)
    return f"{base} for {qualifier} (round {round_number})"


def qualify_round_headings(
    markdown: str,
    *,
    minimum_level: int,
    qualifier: str,
    round_number: int,
) -> str:
    """Nest and qualify every heading, and wrap every bare URL, in one round."""
    lines = wrap_bare_urls(markdown).splitlines()
    headings = dict(_authored_headings(lines))
    shallowest = min(
        (len(match.group("marks")) for match in headings.values()),
        default=minimum_level,
    )
    shift = max(0, minimum_level - shallowest)
    for index, heading in headings.items():
        level = min(6, len(heading.group("marks")) + shift)
        lines[index] = (
            f"{heading.group('indent')}{'#' * level} "
            f"{_qualified_title(heading.group('title'), qualifier, round_number)}"
            f"{heading.group('closing') or ''}"
        )
    rendered = "\n".join(lines)
    if markdown.endswith("\n"):
        rendered += "\n"
    return rendered


__all__ = ["qualify_round_headings", "wrap_bare_urls"]


# eof
