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
    CollectionItem,
    PromptWorkflowError,
    Topic,
)

# A version token such as ``v9.8.0`` or ``v8.11`` (same shape as oqm uses).
VERSION_RE = re.compile(r"v\d+(?:\.\d+)+")
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
# A line opening the open-questions section, matching oqm's marker.
OPEN_QUESTIONS_RE = re.compile(r"^## Open questions")
# A line opening a consolidated decisions section (requirement, design, or plan).
DECISIONS_RE = re.compile(
    r"^## (Requirement clarifications|Design decisions|Implementation decisions)",
)
# A table row opening with a question id: the mark of a decision a review round
# actually consolidated, as opposed to a seeded table written with the document.
CONSOLIDATED_ROW_RE = re.compile(r"^\|\s*Q\d+\b")
# The settled row a no-question review writes instead of question-referenced
# rows. Named MARK, not TOKEN, so ruff's hardcoded-password rule (S105), which
# keys on credential-like names, does not misread the phrase as a secret.
NO_OPEN_QUESTIONS_MARK = "No open questions"
# The docs folder name and the draft prefix and markdown suffix.
DOCS_DIR_NAME = "docs"
DRAFT_PREFIX = "draft."
MD_SUFFIX = ".md"
# The split-and-define section is the authoritative ordered collection backlog.
COLLECTION_HEADING = "## List of feature-requests and issues to create"
UMBRELLA_MARKER = "- Draft role: umbrella"
COLLECTION_TABLE_HEADER = (
    "order",
    "type",
    "key title",
    "slug",
    "status",
    "requirement",
    "validation plan",
)
COLLECTION_STATUSES = frozenset({"pending", "completed"})
COLLECTION_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
COLLECTION_ITEM_RE = re.compile(
    r'^-\s+(Feature-request|Issue):\s+"(.+)\s+\[([a-z0-9][a-z0-9_-]*)\]":',
    flags=re.IGNORECASE,
)
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


def collection_items(path: Path) -> tuple[CollectionItem, ...]:
    """Return the ordered settled split from one umbrella draft.

    Canonical umbrella drafts carry an explicit marker and a compact ordered
    status table. Legacy top-level list entries below the same heading remain
    readable for compatibility. Earlier examples and inventory bullets are
    deliberately ignored.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        heading_index = lines.index(COLLECTION_HEADING)
    except ValueError:
        return ()
    section = _collection_section(lines, heading_index + 1)
    if UMBRELLA_MARKER in lines:
        return _collection_table_items(section)
    return _legacy_collection_items(section)


def _collection_section(lines: list[str], start: int) -> list[str]:
    """Return lines below the collection heading up to the next H2 heading."""
    section: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def _table_cells(line: str) -> tuple[str, ...]:
    """Return normalized cells from one Markdown table row."""
    if not line.startswith("|") or not line.endswith("|"):
        return ()
    return tuple(cell.strip() for cell in line[1:-1].split("|"))


def _document_cell(cell: str) -> str | None:
    """Return a document path from one canonical table cell."""
    value = cell.strip().strip("`")
    return None if value in {"", "-"} else value


def _collection_table_items(section: list[str]) -> tuple[CollectionItem, ...]:
    """Parse the canonical ordered umbrella status table."""
    header_index = _collection_header_index(section)
    if header_index is None or header_index + 1 >= len(section):
        return ()
    if not _collection_separator_valid(section[header_index + 1]):
        return ()

    items: list[CollectionItem] = []
    for line in section[header_index + 2 :]:
        cells = _table_cells(line)
        if not cells:
            break
        if len(cells) != len(COLLECTION_TABLE_HEADER):
            return ()
        item = _collection_item(cells, len(items) + 1)
        if item is None:
            return ()
        items.append(item)
    return tuple(items)


def _collection_header_index(section: list[str]) -> int | None:
    """Return the canonical status-table header offset."""
    return next(
        (
            index
            for index, line in enumerate(section)
            if tuple(cell.lower() for cell in _table_cells(line))
            == COLLECTION_TABLE_HEADER
        ),
        None,
    )


def _collection_separator_valid(line: str) -> bool:
    """Return whether a table separator matches the canonical width."""
    cells = _table_cells(line)
    return len(cells) == len(COLLECTION_TABLE_HEADER) and all(
        cell == "---" for cell in cells
    )


def _collection_item(
    cells: tuple[str, ...],
    expected_order: int,
) -> CollectionItem | None:
    """Parse and validate one canonical umbrella status row."""
    order, kind, title, slug, status, requirement, validation = cells
    kind = kind.lower()
    slug = slug.strip("`")
    status = status.lower()
    valid = (
        order.isdigit()
        and int(order) == expected_order
        and kind in {"feature-request", "issue"}
        and bool(title)
        and COLLECTION_SLUG_RE.fullmatch(slug) is not None
        and status in COLLECTION_STATUSES
    )
    if not valid:
        return None
    return CollectionItem(
        kind=kind,
        title=title,
        slug=slug,
        status=status,
        requirement_path=_document_cell(requirement),
        validation_plan_path=_document_cell(validation),
    )


def _legacy_collection_items(section: list[str]) -> tuple[CollectionItem, ...]:
    """Parse the former bullet-only split format."""
    items: list[CollectionItem] = []
    for line in section:
        match = COLLECTION_ITEM_RE.match(line)
        if match is None:
            continue
        items.append(
            CollectionItem(
                kind=match.group(1).lower(),
                title=match.group(2),
                slug=match.group(3),
            ),
        )
    return tuple(items)


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


def branch_requirement_topic(root: Path, branch: str) -> Topic | None:
    """Resolve one branch-matched requirement through its direct or umbrella draft.

    This fallback covers a development branch created for one item split from a
    collection draft. The requirement slug must exactly match the branch leaf
    after folding hyphens and underscores. The matching version must also have
    exactly one related draft: either a direct same-slug draft or an umbrella
    draft whose content mentions the requirement slug.
    """
    branch_key = _slug_key(branch.rsplit("/", maxsplit=1)[-1])
    requirements: set[tuple[str, str]] = set()
    for directory in docs_dirs(root):
        for entry in sorted(directory.iterdir()):
            parsed = _parse_requirement_name(entry.name)
            if entry.is_file() and parsed is not None:
                version, slug = parsed
                if _slug_key(slug) == branch_key:
                    requirements.add((version, slug))
    if len(requirements) != 1:
        return None
    version, slug = next(iter(requirements))
    draft = _related_draft(root, version, slug)
    if draft is None:
        return None
    return Topic(version=version, slug=slug, draft_path=draft.resolve())


def branch_umbrella_topic(root: Path, branch: str) -> Topic | None:
    """Resolve the one canonical umbrella whose slug matches the branch leaf.

    Integration branches remain clean after each feature merge, so their
    umbrella may be absent from the changed-file candidates used by ordinary
    topic resolution. A canonical branch-name match keeps bare ``pw skill``
    connected to the remaining ordered collection rows without scanning an
    unrelated umbrella.
    """
    branch_key = _slug_key(branch.rsplit("/", maxsplit=1)[-1])
    matches: list[Topic] = []
    for directory in docs_dirs(root):
        for entry in sorted(directory.iterdir()):
            parsed = parse_draft_name(entry.name)
            if not entry.is_file() or parsed is None:
                continue
            version, slug = parsed
            if _slug_key(slug) != branch_key:
                continue
            lines = entry.read_text(encoding="utf-8").splitlines()
            if "- Draft role: umbrella" not in (line.strip() for line in lines):
                continue
            if collection_items(entry):
                matches.append(
                    Topic(version=version, slug=slug, draft_path=entry.resolve()),
                )
    return matches[0] if len(matches) == 1 else None


def _parse_requirement_name(name: str) -> tuple[str, str] | None:
    """Return the version and slug from a feature-request or issue file name."""
    for doc_type in ROLE_DOC_TYPES["requirement"]:
        prefix = f"{doc_type}."
        if not name.startswith(prefix) or not name.endswith(MD_SUFFIX):
            continue
        core = name[len(prefix) : -len(MD_SUFFIX)]
        match = VERSION_RE.match(core)
        if match is None:
            continue
        version = match.group(0)
        rest = core[len(version) :]
        if rest.startswith(".") and rest[1:]:
            return version, rest[1:]
    return None


def _related_draft(root: Path, version: str, slug: str) -> Path | None:
    """Return one direct draft or one umbrella draft mentioning the topic."""
    candidates = _drafts_for_version(root, version)
    slug_key = _slug_key(slug)
    direct = [path for path, draft_slug in candidates if _slug_key(draft_slug) == slug_key]
    if len(direct) == 1:
        return direct[0]
    if direct:
        return None
    umbrella = [path for path, _draft_slug in candidates if _mentions_slug(path, slug_key)]
    return umbrella[0] if len(umbrella) == 1 else None


def _drafts_for_version(root: Path, version: str) -> list[tuple[Path, str]]:
    """Return draft paths and slugs for one version."""
    candidates: list[tuple[Path, str]] = []
    for directory in docs_dirs(root):
        for entry in sorted(directory.iterdir()):
            parsed = parse_draft_name(entry.name)
            if not entry.is_file() or parsed is None or parsed[0] != version:
                continue
            candidates.append((entry, parsed[1]))
    return candidates


def _mentions_slug(path: Path, slug_key: str) -> bool:
    """Return whether a draft mentions a normalized slug as a complete token."""
    normalized = path.read_text(encoding="utf-8").replace("-", "_")
    pattern = rf"(?<![a-z0-9_]){re.escape(slug_key)}(?![a-z0-9_])"
    return re.search(pattern, normalized, flags=re.IGNORECASE) is not None


def _fork_point(cwd: Path, branch: str | None) -> str | None:
    """Call the real two-arg fork-point path while tolerating old test doubles."""
    if branch is None or len(signature(git.fork_point).parameters) == _FORK_POINT_LEGACY_ARITY:
        return git.fork_point(cwd)
    return git.fork_point(cwd, branch)


def docs_dirs(root: Path) -> list[Path]:
    """Return directories from the four supported documentation layouts."""
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
    ``docs/vX.Y.Z/``, and ``docs/vX.Y/vX.Y.Z/``. A legacy ``vX.Y`` version maps
    to the first two layouts only.
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
        candidates.extend((docs / version, docs / minor / version))
    return [candidate for candidate in candidates if candidate.is_dir()]


def _is_supported_docs_dir(docs: Path, candidate: Path) -> bool:
    """Return whether ``candidate`` is one of the supported version paths."""
    parts = candidate.relative_to(docs).parts
    if len(parts) == 1:
        return bool(
            MINOR_DIR_RE.fullmatch(parts[0])
            or FULL_VERSION_DIR_RE.fullmatch(parts[0]),
        )
    return bool(
        len(parts) == NESTED_LAYOUT_DEPTH
        and MINOR_DIR_RE.fullmatch(parts[0])
        and FULL_VERSION_DIR_RE.fullmatch(parts[1]),
    )


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


def has_consolidated_decisions(path: Path) -> bool:
    """Return whether the document carries decisions a review round produced.

    A decisions heading alone is not enough: a freshly written document may seed
    such a section (a plan's house-style ``## Implementation decisions``, for
    instance), and reading that seed as "reviewed" made the skill routing skip
    the review step. The consolidated signal is the heading plus at least one
    row a review produces: a table row opening with a question id (``| Qxx``),
    or the ``No open questions`` settled row a no-question review writes.

    Args:
        path: The document to inspect.

    Returns:
        True when the document opens a decisions section and carries at least
        one question-referenced row or the no-open-questions settled row.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(DECISIONS_RE.match(line) for line in lines):
        return False
    return any(
        CONSOLIDATED_ROW_RE.match(line) or NO_OPEN_QUESTIONS_MARK in line
        for line in lines
    )


# eof
