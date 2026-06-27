"""Topic and document resolution for prompt_workflow.

This module turns the raw git signals into topics and resolves the documents a
prompt needs. It parses the version and slug from a draft name, detects the
relevant drafts on the current branch (Q07), matches requirement, design and
plan documents to a topic by shared version and slug prefix (Q02), picks the
most recently modified match (Q01), and detects a ``## Open questions`` section
(Q04). It reads files; it never writes.

Slug matching folds ``-`` and ``_`` together, so a draft slug such as
``git_history_report`` resolves the hyphenated ``git-history-report`` requirement,
design and plan documents that ``write-requirement`` produces, and the reverse.
"""

from __future__ import annotations

import re
from inspect import signature
from pathlib import Path

from tools import prompt_workflow_git as git
from tools.prompt_workflow_models import (
    ROLE_DOC_TYPES,
    VALIDATION_SUFFIX,
    Topic,
)

# A version token such as ``v9.8.0`` or ``v8.11`` (same shape as oqm uses).
VERSION_RE = re.compile(r"v\d+(?:\.\d+)+")
# A line opening the open-questions section, matching oqm's marker.
OPEN_QUESTIONS_RE = re.compile(r"^## Open questions")
# A line opening a consolidated decisions section (requirement, design, or plan).
DECISIONS_RE = re.compile(
    r"^## (Requirement clarifications|Design decisions|Implementation decisions)",
)
# The docs folder name and the draft prefix and markdown suffix.
DOCS_DIR_NAME = "docs"
DRAFT_PREFIX = "draft."
MD_SUFFIX = ".md"
# Compatibility arity for tests that monkeypatch git.fork_point with the old
# cwd-only callable.
_FORK_POINT_LEGACY_ARITY = 1


def parse_draft_name(name: str) -> tuple[str, str] | None:
    """Return the (version, slug) parsed from a draft file name, or None.

    Args:
        name: A file name such as ``draft.v9.8.0.resources_isolation.md``.

    Returns:
        The version token and topic slug, or None when the name is not a draft
        or carries no version token.
    """
    if not name.startswith(DRAFT_PREFIX) or not name.endswith(MD_SUFFIX):
        return None
    core = name[len(DRAFT_PREFIX) : -len(MD_SUFFIX)]
    match = VERSION_RE.match(core)
    if match is None:
        return None
    version = match.group(0)
    rest = core[len(version) :]
    if not rest.startswith(".") or not rest[1:]:
        return None
    return version, rest[1:]


def _draft_relpath_topic(relpath: Path) -> tuple[str, str] | None:
    """Return the (version, slug) for a repo-relative draft path under docs/."""
    if not relpath.parts or relpath.parts[0] != DOCS_DIR_NAME:
        return None
    return parse_draft_name(relpath.name)


def relevant_drafts(root: Path, cwd: Path, branch: str | None = None) -> list[Topic]:
    """Return the topics from drafts modified or committed on the branch (Q07).

    Args:
        root: The project root, used to resolve absolute draft paths.
        cwd: The git working directory.
        branch: The already-read current branch, when the caller has it.

    Returns:
        One Topic per relevant draft that still exists on disk, de-duplicated by
        version and slug and ordered by repo-relative path.
    """
    candidates: set[str] = set(git.working_tree_changed_files(cwd))
    base = _fork_point(cwd, branch)
    if base is not None:
        candidates.update(git.changed_files_since(cwd, base))

    topics: list[Topic] = []
    seen: set[tuple[str, str]] = set()
    for relpath_text in sorted(candidates):
        relpath = Path(relpath_text)
        parsed = _draft_relpath_topic(relpath)
        if parsed is None:
            continue
        absolute = root / relpath
        if not absolute.is_file():
            continue
        version, slug = parsed
        if (version, slug) in seen:
            continue
        seen.add((version, slug))
        topics.append(Topic(version=version, slug=slug, draft_path=absolute.resolve()))
    return topics


def _fork_point(cwd: Path, branch: str | None) -> str | None:
    """Call the real two-arg fork-point path while tolerating old test doubles."""
    if branch is None or len(signature(git.fork_point).parameters) == _FORK_POINT_LEGACY_ARITY:
        return git.fork_point(cwd)
    return git.fork_point(cwd, branch)


def docs_dirs(root: Path) -> list[Path]:
    """Return the docs directories to scan: ``docs/`` and its ``docs/vX.Y.Z/``."""
    docs = root / DOCS_DIR_NAME
    if not docs.is_dir():
        return []
    dirs = [docs]
    dirs.extend(
        sub
        for sub in sorted(docs.iterdir())
        if sub.is_dir() and VERSION_RE.fullmatch(sub.name)
    )
    return dirs


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


def find_matching_documents(root: Path, topic: Topic, role: str) -> list[Path]:
    """Return every document under docs/ matching the topic for the given role."""
    matches: list[Path] = []
    for directory in docs_dirs(root):
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


def has_open_questions(path: Path) -> bool:
    """Return whether the document carries a ``## Open questions`` section (Q04)."""
    text = path.read_text(encoding="utf-8")
    return any(OPEN_QUESTIONS_RE.match(line) for line in text.splitlines())


def has_decisions_table(path: Path) -> bool:
    """Return whether the document carries a consolidated decisions section.

    The consolidate step strips the ``## Open questions`` section and writes a
    decisions table named for the document type: ``## Requirement clarifications``
    for a feature-request or issue, ``## Design decisions`` for a design, and
    ``## Implementation decisions`` for a plan. Detecting any of those three
    headings is the on-disk "settled" signal the skill routing reads (Q03 of the
    v0.9.0 handoff_automation design).

    Args:
        path: The document to inspect.

    Returns:
        True when the document opens a consolidated decisions section.
    """
    text = path.read_text(encoding="utf-8")
    return any(DECISIONS_RE.match(line) for line in text.splitlines())


# eof
