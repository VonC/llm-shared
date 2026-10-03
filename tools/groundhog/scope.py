"""Resolve one invocation scope and persist the detached walk's exact membership.

Explicit selectors never consult the environment. Group resolution requests
the caller's lazy inventory so scope and proof share one tree walk; whole
and captured scopes never request it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from tools.artifact_home import artifact_path
from tools.groundhog.groups import GroupError, resolve_group
from tools.scope_capture import (
    WHOLE_SCOPE,
    CaptureError,
    ResolvedScope,
    validate_capture,
    write_capture,
)

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Callable, Sequence
    from pathlib import Path

GHOG_GROUP_ENV: Final = "GHOG_GROUP"


class ScopeError(ValueError):
    """An explicit or ambient scope cannot safely select an execution."""


def resolve_scope(
    args: Namespace, environ: Callable[[str], str | None], root: Path,
    files: Callable[[], Sequence[Path]],
) -> ResolvedScope:
    """Select explicit scope, else a nonempty environment group, else whole.

    Raises:
        ScopeError: For conflicting selectors or unusable declarations/captures.
    """
    group = getattr(args, "group", None)
    whole = getattr(args, "whole_suite", False)
    capture = getattr(args, "scope_file", None)
    selected = [option for option, present in (
        ("--group", group is not None), ("--whole-suite", whole), ("--scope-file", capture is not None),
    ) if present]
    if len(selected) > 1:
        message = f"conflicting scope selectors: {', '.join(selected)}"
        raise ScopeError(message)
    if whole:
        return WHOLE_SCOPE
    try:
        if capture is not None:
            return _capture(root, capture)
        if group is None:
            group = environ(GHOG_GROUP_ENV) or None
        return WHOLE_SCOPE if group is None else resolve_group(root, group, files())
    except (GroupError, CaptureError) as error:
        raise ScopeError(str(error)) from error


def _capture(root: Path, name: str) -> ResolvedScope:
    """Read a capture relative to the project root without consulting declarations."""
    try:
        text = (root / name).read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        message = f"cannot read scope file {name}: {error}"
        raise CaptureError(message) from error
    return validate_capture(root, text)


def write_detach_capture(root: Path, scope: ResolvedScope) -> Path:
    """Atomically bind the detached child's membership before its spawn."""
    path = artifact_path(root, "a.ghog.day.scope.json")
    write_capture(path, scope)
    return path


# eof
