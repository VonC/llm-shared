"""Layout enumeration, filename matching and document selection.

Extracted from the docs facade, this module reads directory entries and file
metadata; Git topic discovery and document-body markers remain with its caller.
Both directory listings require exact immediate document evidence for a full
version's slug child, preserving shape-only recognition for older layouts.
Eligibility is uncached and directory-slug syntax has no collection dependency.
Workflow discovery validates the canonical parent once, preferring its matches
and selecting a fallback document only when it is unique across other layouts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

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
EFFORT_DOCUMENT_TYPES = (
    "draft", "feature-request", "issue", "design", "plan", "validation-plan",
)

# Lookup owns layout slug syntax independently of collection validation.
DIRECTORY_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
DOCS_DIR_NAME = "docs"
MD_SUFFIX = ".md"


def docs_dirs(root: Path) -> list[Path]:
    """Return directories from the supported documentation layouts."""
    docs = root / DOCS_DIR_NAME
    if not docs.is_dir():
        return []
    candidates = [docs, *sorted(docs.rglob("*"))]
    return [
        candidate for candidate in candidates
        if candidate.is_dir() and _is_supported_docs_dir(docs, candidate)
    ]


def docs_dirs_for_version(root: Path, version: str) -> list[Path]:
    """Return existing supported documentation directories for ``version``.

    A full ``vX.Y.Z`` version maps to ``docs/``, ``docs/vX.Y/``,
    ``docs/vX.Y.Z/``, ``docs/vX.Y/vX.Y.Z/``, and ``docs/vX.Y.Z/<slug>/``
    children with exact immediate effort-document evidence.
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
            candidates.extend(sorted(full_dir.iterdir()))
    return [
        candidate for candidate in candidates
        if candidate.is_dir() and _is_supported_docs_dir(docs, candidate)
    ]


def _is_supported_docs_dir(docs: Path, candidate: Path) -> bool:
    """Accept older layouts by shape and slug children by exact filename evidence.

    Inspect current immediate files only, without reading bodies or resolving
    documents. Enumeration failures propagate and the first match ends the scan.
    """
    parts = candidate.relative_to(docs).parts
    if not parts:
        return True
    if len(parts) == 1:
        return bool(
            MINOR_DIR_RE.fullmatch(parts[0])
            or FULL_VERSION_DIR_RE.fullmatch(parts[0]),
        )
    if len(parts) == NESTED_LAYOUT_DEPTH:
        if MINOR_DIR_RE.fullmatch(parts[0]) and FULL_VERSION_DIR_RE.fullmatch(parts[1]):
            return True
        if FULL_VERSION_DIR_RE.fullmatch(parts[0]) and DIRECTORY_SLUG_RE.fullmatch(parts[1]):
            return _has_effort_document(candidate, parts[0], parts[1])
    return False


def _has_effort_document(directory: Path, version: str, slug: str) -> bool:
    """Stop at the first immediate file carrying the directory's exact identity."""
    return any(
        entry.is_file()
        and any(
            _exact_doc_matches(entry.name, kind, version, slug)
            for kind in EFFORT_DOCUMENT_TYPES
        )
        for entry in directory.iterdir()
    )


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


@dataclass(frozen=True)
class _DocumentCandidates:
    """Retain ordered matches and their scope so selection never rediscovers it."""

    paths: tuple[Path, ...]
    scope: Literal["canonical-parent", "fallback"]


def _render_parent(root: Path, topic: Topic) -> str:
    """Render a normalized canonical parent relative to the root when possible."""
    parent = topic.draft_path.resolve().parent
    resolved_root = root.resolve()
    if parent.is_relative_to(resolved_root):
        return parent.relative_to(resolved_root).as_posix()
    return parent.as_posix()


def _directory_matches(directory: Path, topic: Topic, role: str) -> tuple[Path, ...]:
    """Match immediate files in the existing sorted order, surfacing IO errors."""
    return tuple(
        entry
        for entry in sorted(directory.iterdir())
        if entry.is_file()
        and _doc_matches(entry.name, role, topic.version, topic.slug)
    )


def _discover_candidates(root: Path, topic: Topic, role: str) -> _DocumentCandidates:
    """Validate the draft parent and scan fallback only when local matches are absent.

    Inventory recognized directories once, allowing their eligibility reads.
    The draft itself need not exist. Preserve resolved directory comparisons
    and candidate ordering without a second scan to recover selection scope.
    """
    directories = [(directory, directory.resolve()) for directory in docs_dirs(root)]
    parent = topic.draft_path.resolve().parent
    canonical = next((directory for directory, resolved in directories if resolved == parent), None)
    if canonical is None:
        msg = (
            f"Unrecognized canonical parent {_render_parent(root, topic)} "
            f"for {role} document of {topic.version} {topic.slug}."
        )
        raise PromptWorkflowError(msg)
    local = _directory_matches(canonical, topic, role)
    if local:
        return _DocumentCandidates(local, "canonical-parent")
    fallback = tuple(
        path
        for directory, resolved in directories
        if resolved != parent
        for path in _directory_matches(directory, topic, role)
    )
    return _DocumentCandidates(fallback, "fallback")


def find_matching_documents(root: Path, topic: Topic, role: str) -> list[Path]:
    """List local matches or all fallback matches, rejecting unsupported parents."""
    return list(_discover_candidates(root, topic, role).paths)


def most_recent(paths: list[Path]) -> Path | None:
    """Return the most recently modified path, or None when the list is empty (Q01)."""
    if not paths:
        return None
    return max(paths, key=lambda path: path.stat().st_mtime)


def select_document(root: Path, topic: Topic, role: str) -> Path | None:
    """Select the newest local match or sole fallback; reject ambiguous fallback."""
    candidates = _discover_candidates(root, topic, role)
    if candidates.scope == "canonical-parent":
        return most_recent(list(candidates.paths))
    if len(candidates.paths) > 1:
        rendered = ", ".join(path.relative_to(root).as_posix() for path in candidates.paths)
        msg = (
            f"Ambiguous fallback {role} document for {topic.version} {topic.slug} "
            f"(canonical parent {_render_parent(root, topic)}): {rendered}."
        )
        raise PromptWorkflowError(msg)
    return candidates.paths[0] if candidates.paths else None


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
    "docs_dirs",
    "docs_dirs_for_version",
    "find_documents",
    "find_matching_documents",
    "most_recent",
    "resolve_document",
    "select_document",
]


# eof
