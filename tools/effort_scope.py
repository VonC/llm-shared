"""Read requirement-owned scope without consulting draft or environment state.

Only metadata before the first level-two heading participates. Whole-suite
selection needs no project inventory; a named group shares groundhog's resolver
and its linear inventory pass instead of introducing another matching policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from tools.groundhog import groups, snapshot
from tools.scope_capture import WHOLE_SCOPE

if TYPE_CHECKING:
    from pathlib import Path

    from tools.scope_capture import ResolvedScope

TEST_GROUP_PREFIX: Final = "- Test group: "
WHOLE_SUITE_VALUE: Final = "whole suite"


class EffortScopeError(ValueError):
    """A requirement cannot supply an unambiguous, valid workflow scope."""


@dataclass(frozen=True)
class EffortScope:
    """Resolved membership and the requirement or absence that selected it."""

    scope: ResolvedScope
    source_path: Path | None
    reason: str


def read_effort_scope(root: Path, requirement: Path | None) -> EffortScope:
    """Resolve the requirement header into an explicit scope and provenance.

    Args:
        root: Project root used for relative paths and group validation.
        requirement: Selected requirement path, or None before its creation.

    Returns:
        Validated scope with its source path and display reason.

    Raises:
        EffortScopeError: For unreadable metadata, duplicate or empty values,
            or a group that groundhog cannot resolve.
    """
    if requirement is None:
        return EffortScope(WHOLE_SCOPE, None, "no requirement yet")
    path = root / requirement
    source = path.relative_to(root).as_posix()
    try:
        value = _header_value(path)
        if value is None:
            return EffortScope(WHOLE_SCOPE, path, f"no Test group line in {source}")
        if value == WHOLE_SUITE_VALUE:
            return EffortScope(WHOLE_SCOPE, path, source)
        resolved = groups.resolve_group(root, value, snapshot.source_files(root))
    except (EffortScopeError, groups.GroupError) as error:
        message = f"{source}: {error}"
        raise EffortScopeError(message) from error
    return EffortScope(resolved, path, source)


def _header_value(path: Path) -> str | None:
    """Read only header lines and reject ambiguous or empty metadata."""
    value: str | None = None
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if line.startswith("## "):
                    break
                if not (line.startswith(TEST_GROUP_PREFIX) or line.rstrip() == TEST_GROUP_PREFIX.rstrip()):
                    continue
                if value is not None:
                    message = "two Test group lines"
                    raise EffortScopeError(message)
                value = line[len(TEST_GROUP_PREFIX.rstrip()):].strip()
                if not value:
                    message = "empty Test group value"
                    raise EffortScopeError(message)
    except (OSError, UnicodeError) as error:
        message = f"cannot read requirement: {error}"
        raise EffortScopeError(message) from error
    return value


# eof
