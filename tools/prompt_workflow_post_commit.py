"""Resolve post-commit workflow topics without coupling command rendering.

The workflow skill delegates only plan-topic discovery here. Keeping
``post_commit_command`` in the caller preserves one-way imports because command
rendering and document selection remain owned by ``prompt_workflow_skill``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import VALIDATION_SUFFIX, MemoryRecord, Topic

if TYPE_CHECKING:
    from pathlib import Path

MD_SUFFIX = ".md"


def resolve_post_commit_topic(
    root: Path,
    record: MemoryRecord | None,
    branch: str,
) -> Topic | None:
    """Resolve a plan topic when the original draft is no longer discoverable."""
    candidates = plan_topics(root)
    if not candidates:
        return None
    if record is not None:
        matching = [
            topic
            for topic in candidates
            if topic.version == record.version and topic.slug == record.topic
        ]
        if len(matching) == 1:
            return matching[0]
    branch_key = slug_key(branch.rsplit("/", maxsplit=1)[-1])
    branch_matches = [
        topic for topic in candidates if branch_key.endswith(slug_key(topic.slug))
    ]
    if len(branch_matches) == 1:
        return branch_matches[0]
    return None


def plan_topics(root: Path) -> list[Topic]:
    """Return unique topics that have both a plan and a validation plan."""
    topics: list[Topic] = []
    seen: set[tuple[str, str]] = set()
    for directory in docs.docs_dirs(root):
        for entry in sorted(directory.iterdir()):
            topic = _topic_from_validation_plan(entry)
            if topic is None:
                continue
            key = (topic.version, topic.slug)
            if key in seen or docs.select_document(root, topic, "plan") is None:
                continue
            seen.add(key)
            topics.append(topic)
    return topics


def _topic_from_validation_plan(path: Path) -> Topic | None:
    """Parse a Topic from ``plan.<version>.<slug>.validation.md``."""
    name = path.name
    if (
        not path.is_file()
        or not name.startswith("plan.")
        or not name.endswith(VALIDATION_SUFFIX)
    ):
        return None
    core = name[len("plan.") : -len(VALIDATION_SUFFIX)]
    match = docs.VERSION_RE.match(core)
    if match is None:
        return None
    version = match.group(0)
    rest = core[len(version) :]
    if not rest.startswith(".") or not rest[1:]:
        return None
    slug = rest[1:]
    draft = path.parent / f"draft.{version}.{slug}{MD_SUFFIX}"
    return Topic(version=version, slug=slug, draft_path=draft.resolve())


def slug_key(value: str) -> str:
    """Canonicalize branch and topic slugs for fallback matching."""
    return value.replace("-", "_")


# eof
