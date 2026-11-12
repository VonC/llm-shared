"""Classify bounded Markdown adapters without filesystem access.

Fix: the Codex package redirects under ``.agents/llm-shared`` now link
relative to their place in the clone, so they are ordinary bounded pointers.
The cache-relative pointer shape, which exempted a short adapter linking out
of the repository through ``/git/llm-shared/``, is gone: such a link escapes
the repository and the document is structured again.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import PurePosixPath
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from tools.markdown_check.models import MarkdownSource

_POINTER_ROOTS = (
    ".agents/llm-shared/instructions/",
    ".agents/llm-shared/rules/",
    ".claude/",
    ".github/",
    "templates/",
)
_MAX_POINTER_LINES = 5
_FRAGMENT_MIN_LEVEL = 2


class DocumentKind(Enum):
    """The two structural policy classes used by local rules."""

    STRUCTURED = "structured"
    ADAPTER = "adapter"


@dataclass(frozen=True, slots=True)
class DocumentClassification:
    """One deterministic classification and its stable explanatory reason."""

    kind: DocumentKind
    reason: str


def _in_pointer_root(path: PurePosixPath) -> bool:
    """Return whether a path belongs to one approved bounded adapter root."""
    normalized = path.as_posix()
    normalized = normalized.removeprefix("./")
    return any(normalized.startswith(root) for root in _POINTER_ROOTS)


def resolve_markdown_target(
    source_path: PurePosixPath,
    target: str,
) -> PurePosixPath | None:
    """Resolve one syntactic repository-relative Markdown link target."""
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith("/"):
        return None
    if PurePosixPath(parsed.path).suffix.lower() != ".md":
        return None
    parts = list(source_path.parent.parts)
    for part in PurePosixPath(parsed.path).parts:
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return PurePosixPath(*parts) if parts else None


def _is_bounded_pointer(source: MarkdownSource) -> bool:
    """Return whether a short adapter-root document points to canonical Markdown."""
    return (
        _in_pointer_root(source.path)
        and len(source.body_lines) <= _MAX_POINTER_LINES
        and any(
            resolve_markdown_target(source.path, link.target) is not None
            for link in source.links
        )
    )


def classify_document(source: MarkdownSource) -> DocumentClassification:
    """Classify one source while exempting only the three confirmed adapter shapes."""
    if source.frontmatter is not None and source.frontmatter.description:
        return DocumentClassification(DocumentKind.ADAPTER, "frontmatter-description")
    normalized = source.path.as_posix()
    normalized = normalized.removeprefix("./")
    if (
        normalized.startswith("templates/")
        and source.headings
        and source.headings[0].level >= _FRAGMENT_MIN_LEVEL
    ):
        return DocumentClassification(DocumentKind.ADAPTER, "template-fragment")
    if _is_bounded_pointer(source):
        return DocumentClassification(DocumentKind.ADAPTER, "bounded-pointer")
    return DocumentClassification(DocumentKind.STRUCTURED, "default")


__all__ = [
    "DocumentClassification",
    "DocumentKind",
    "classify_document",
    "resolve_markdown_target",
]


# eof
