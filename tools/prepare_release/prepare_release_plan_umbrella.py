"""Resolve umbrella drafts to their topic-integration branches."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tools.prepare_release.prepare_release_plan_models import ReleasePlanError

if TYPE_CHECKING:
    from pathlib import Path

    from tools.prepare_release.prepare_release_plan_git import GitRepository

_DRAFT_NAME_RE = re.compile(
    r"^draft\.v\d+\.\d+(?:\.\d+)?\.([a-z0-9][a-z0-9_-]*)\.md$",
)
_UMBRELLA_ROLE = "- Draft role: umbrella"


def resolve_umbrella_integration(
    repository: GitRepository,
    umbrella: Path | None,
) -> str | None:
    """Resolve one marked umbrella draft to its slug-matched local branch."""
    if umbrella is None:
        return None
    resolved = _resolve_draft_path(repository, umbrella)
    slug = _umbrella_slug(resolved, umbrella)
    return _matching_integration_branch(repository, slug)


def slug_key(value: str) -> str:
    """Fold the branch-name spelling accepted across prompt workflow tools."""
    return value.replace("-", "_")


def _resolve_draft_path(repository: GitRepository, umbrella: Path) -> Path:
    """Return a repository-local umbrella path that exists on disk."""
    path = umbrella if umbrella.is_absolute() else repository.root / umbrella
    resolved = path.resolve()
    try:
        resolved.relative_to(repository.root.resolve())
    except ValueError as error:
        message = f"Umbrella draft is outside the repository: {umbrella}."
        raise ReleasePlanError(message) from error
    if not resolved.is_file():
        message = f"Umbrella draft does not exist: {umbrella}."
        raise ReleasePlanError(message)
    return resolved


def _umbrella_slug(resolved: Path, umbrella: Path) -> str:
    """Validate the draft role and return its canonical filename slug."""
    lines = {line.strip() for line in resolved.read_text(encoding="utf-8").splitlines()}
    if _UMBRELLA_ROLE not in lines:
        message = f"Draft is not marked as an umbrella: {umbrella}."
        raise ReleasePlanError(message)
    match = _DRAFT_NAME_RE.fullmatch(resolved.name)
    if match is None:
        message = f"Umbrella draft has no canonical slug: {umbrella}."
        raise ReleasePlanError(message)
    return match.group(1)


def _matching_integration_branch(repository: GitRepository, slug: str) -> str:
    """Require exactly one local branch matching the folded umbrella slug."""
    key = slug_key(slug)
    branches = tuple(
        branch
        for branch in repository.local_branches()
        if slug_key(branch.rsplit("/", maxsplit=1)[-1]) == key
    )
    if len(branches) == 1:
        return branches[0]
    detail = ", ".join(branches) if branches else "none"
    message = (
        f"Umbrella slug {slug!r} must name exactly one local integration branch "
        f"after hyphen/underscore folding; found {detail}."
    )
    raise ReleasePlanError(message)


# eof
