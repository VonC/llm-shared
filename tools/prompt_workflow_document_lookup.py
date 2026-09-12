"""Layout enumeration, filename matching and document selection.

Extracted from the docs facade without changing lookup behavior. This module
reads directory entries and file metadata; Git topic discovery and document-body
markers remain with its caller. Directory-slug syntax belongs to lookup and has
no dependency on collection validation.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.prompt_workflow_models import (
    ROLE_DOC_TYPES,
    VALIDATION_SUFFIX,
    PromptWorkflowError,
    Topic,
)

if TYPE_CHECKING:
    from pathlib import Path

MINOR_DIR_RE = re.compile(r"v\d+\.\d+")
FULL_VERSION_DIR_RE = re.compile(r"v\d+\.\d+\.\d+")
NESTED_LAYOUT_DEPTH = 2
FULL_VERSION_PARTS = 3
DOCUMENT_TYPES = (
    "draft",
    "requirement",
    "feature-request",
    "issue",
    "design",
    "plan",
    "validation-plan",
)
DOCUMENT_TYPE_PREFIXES = {
    "draft": ("draft",),
    "requirement": ROLE_DOC_TYPES["requirement"],
    "feature-request": ("feature-request",),
    "issue": ("issue",),
    "design": ("design",),
    "plan": ("plan",),
    "validation-plan": ("plan",),
}

# Lookup owns layout slug syntax independently of collection validation.
DIRECTORY_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
DOCS_DIR_NAME = "docs"
MD_SUFFIX = ".md"


def docs_dirs(root: Path) -> list[Path]:
    """Return directories from the supported documentation layouts."""
    docs = root / DOCS_DIR_NAME
    if not docs.is_dir():
        return []
    dirs = [docs]
    dirs.extend(
        sub
        for sub in sorted(docs.rglob("*"))
        if sub.is_dir() and _is_supported_docs_dir(docs, sub)
    )
    return dirs


def docs_dirs_for_version(root: Path, version: str) -> list[Path]:
    """Return existing supported documentation directories for ``version``.

    A full ``vX.Y.Z`` version maps to ``docs/``, ``docs/vX.Y/``,
    ``docs/vX.Y.Z/``, ``docs/vX.Y/vX.Y.Z/``, and any ``docs/vX.Y.Z/<slug>/``.
    A legacy ``vX.Y`` version maps to the first two layouts only.
    """
    is_minor = MINOR_DIR_RE.fullmatch(version) is not None
    is_full = FULL_VERSION_DIR_RE.fullmatch(version) is not None
    if not (is_minor or is_full):
        msg = f"Invalid document version: {version!r}."
        raise PromptWorkflowError(msg)
    docs = root / DOCS_DIR_NAME
    parts = version.removeprefix("v").split(".")
    minor = f"v{parts[0]}.{parts[1]}"
    candidates = [docs, docs / minor]
    if len(parts) == FULL_VERSION_PARTS:
        full_dir = docs / version
        candidates.extend((full_dir, docs / minor / version))
        if full_dir.is_dir():
            candidates.extend(
                sub
                for sub in sorted(full_dir.iterdir())
                if sub.is_dir() and DIRECTORY_SLUG_RE.fullmatch(sub.name) is not None
            )
    return [candidate for candidate in candidates if candidate.is_dir()]


def _is_supported_docs_dir(docs: Path, candidate: Path) -> bool:
    """Return whether ``candidate`` is one of the supported version paths."""
    parts = candidate.relative_to(docs).parts
    if len(parts) == 1:
        return bool(
            MINOR_DIR_RE.fullmatch(parts[0])
            or FULL_VERSION_DIR_RE.fullmatch(parts[0]),
        )
    if len(parts) == NESTED_LAYOUT_DEPTH:
        if MINOR_DIR_RE.fullmatch(parts[0]) and FULL_VERSION_DIR_RE.fullmatch(parts[1]):
            return True
        if FULL_VERSION_DIR_RE.fullmatch(parts[0]) and DIRECTORY_SLUG_RE.fullmatch(parts[1]):
            return True
    return False


def _topic_docs_dirs(root: Path, topic: Topic) -> list[Path]:
    """Prefer the canonical draft's directory, falling back to every layout."""
    directories = docs_dirs(root)
    draft_parent = topic.draft_path.resolve().parent
    matching = [directory for directory in directories if directory.resolve() == draft_parent]
    return matching or directories


def _slug_key(value: str) -> str:
    """Canonicalize a slug so ``-`` and ``_`` separators compare equal.

    A draft slug uses ``_`` (for example ``git_history_report``) while the
    requirement, design and plan documents carry the hyphenated topic
    ``write-requirement`` enforces (``git-history-report``). Folding ``-`` onto
    ``_`` lets either form resolve the other.

    Args:
        value: A slug or a file-name topic part.

    Returns:
        The value with every ``-`` rewritten as ``_``.
    """
    return value.replace("-", "_")


def _doc_matches(name: str, role: str, version: str, slug: str) -> bool:
    """Return whether a file name matches the role, version and topic slug (Q02).

    The topic part of the file name is compared to ``slug`` with ``-`` and ``_``
    folded together (see ``_slug_key``), so a ``git_history_report`` draft slug
    resolves the hyphenated ``git-history-report`` documents and the reverse,
    including a ``<slug>_<sub>`` umbrella sub-topic written with either separator.
    """
    slug_key = _slug_key(slug)
    for doc_type in ROLE_DOC_TYPES[role]:
        prefix = f"{doc_type}.{version}."
        if not name.startswith(prefix) or not name.endswith(MD_SUFFIX):
            continue
        if role == "plan" and name.endswith(VALIDATION_SUFFIX):
            continue
        if role == "validation_plan":
            if not name.endswith(VALIDATION_SUFFIX):
                continue
            topic_part = name[len(prefix) : -len(VALIDATION_SUFFIX)]
        else:
            topic_part = name[len(prefix) : -len(MD_SUFFIX)]
        topic_key = _slug_key(topic_part)
        if topic_key == slug_key or topic_key.startswith(slug_key + "_"):
            return True
    return False


def _exact_doc_matches(name: str, document_type: str, version: str, slug: str) -> bool:
    """Return whether ``name`` exactly matches one document selector."""
    prefixes = DOCUMENT_TYPE_PREFIXES.get(document_type)
    if prefixes is None:
        choices = ", ".join(DOCUMENT_TYPES)
        msg = f"Unknown document type {document_type!r}; expected one of: {choices}."
        raise PromptWorkflowError(msg)
    validation = document_type == "validation-plan"
    suffix = VALIDATION_SUFFIX if validation else MD_SUFFIX
    slug_key = _slug_key(slug)
    for prefix in prefixes:
        start = f"{prefix}.{version}."
        if not name.startswith(start) or not name.endswith(suffix):
            continue
        if not validation and name.endswith(VALIDATION_SUFFIX):
            continue
        topic_part = name[len(start) : -len(suffix)]
        if _slug_key(topic_part) == slug_key:
            return True
    return False


def find_documents(
    root: Path,
    version: str,
    slug: str,
    document_type: str,
) -> list[Path]:
    """Find exact documents from only version, slug, and document type."""
    if document_type not in DOCUMENT_TYPE_PREFIXES:
        choices = ", ".join(DOCUMENT_TYPES)
        msg = f"Unknown document type {document_type!r}; expected one of: {choices}."
        raise PromptWorkflowError(msg)
    matches: list[Path] = []
    for directory in docs_dirs_for_version(root, version):
        matches.extend(
            entry
            for entry in sorted(directory.iterdir())
            if entry.is_file()
            and _exact_doc_matches(entry.name, document_type, version, slug)
        )
    return matches


def resolve_document(
    root: Path,
    version: str,
    slug: str,
    document_type: str,
) -> Path | None:
    """Resolve one exact document, failing closed when layouts are ambiguous."""
    matches = find_documents(root, version, slug, document_type)
    if len(matches) > 1:
        rendered = ", ".join(path.relative_to(root).as_posix() for path in matches)
        msg = (
            f"Ambiguous {document_type} document for {version} {slug}: {rendered}."
        )
        raise PromptWorkflowError(msg)
    return matches[0] if matches else None


def find_matching_documents(root: Path, topic: Topic, role: str) -> list[Path]:
    """Return every document under docs/ matching the topic for the given role."""
    matches: list[Path] = []
    for directory in _topic_docs_dirs(root, topic):
        matches.extend(
            entry
            for entry in sorted(directory.iterdir())
            if entry.is_file()
            and _doc_matches(entry.name, role, topic.version, topic.slug)
        )
    return matches


def most_recent(paths: list[Path]) -> Path | None:
    """Return the most recently modified path, or None when the list is empty (Q01)."""
    if not paths:
        return None
    return max(paths, key=lambda path: path.stat().st_mtime)


def select_document(root: Path, topic: Topic, role: str) -> Path | None:
    """Return the most recent document for a topic and role, or None."""
    return most_recent(find_matching_documents(root, topic, role))


# The private names remain explicit exports for the compatibility facade.
__all__ = [
    "DOCS_DIR_NAME",
    "DOCUMENT_TYPES",
    "DOCUMENT_TYPE_PREFIXES",
    "FULL_VERSION_DIR_RE",
    "FULL_VERSION_PARTS",
    "MD_SUFFIX",
    "MINOR_DIR_RE",
    "NESTED_LAYOUT_DEPTH",
    "_doc_matches",
    "_exact_doc_matches",
    "_is_supported_docs_dir",
    "_slug_key",
    "_topic_docs_dirs",
    "docs_dirs",
    "docs_dirs_for_version",
    "find_documents",
    "find_matching_documents",
    "most_recent",
    "resolve_document",
    "select_document",
]


# eof
