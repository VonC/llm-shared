"""Resolve declared test groups from the snapshot's supplied file inventory.

Only the declaration is read here. Project settings are loaded once per
resolution phase, and pure pattern matchers filter the shared inventory.
No test or source file is opened and no second tree walk is performed.
"""

from __future__ import annotations

import configparser
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from coverage.files import GlobMatcher

from tools.groundhog import group_patterns
from tools.groundhog.project_settings import Settings
from tools.linear_order import ordered_strings
from tools.scope_capture import ResolvedScope, ScopeKind, scope_fingerprint

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

GROUPS_FILE: Final = ".ghog-groups"
_NAME: Final = re.compile(r"[a-z][a-z0-9_-]*")


class GroupError(ValueError):
    """A declaration or selected membership cannot support a grouped run."""


@dataclass(frozen=True)
class Declaration:
    """Ordered normalized patterns for both sides of one declared group."""

    tests: tuple[str, ...]
    sources: tuple[str, ...]


def read_declaration(root: Path) -> dict[str, Declaration]:
    """Read and validate the group declaration exactly once.

    Args:
        root: Project root containing the declaration.

    Returns:
        Groups in declaration order, with normalized patterns.

    Raises:
        GroupError: For an unreadable or malformed declaration.
    """
    parser = configparser.ConfigParser(interpolation=None)
    try:
        text = (root / GROUPS_FILE).read_text(encoding="utf-8")
    except (OSError, ValueError) as error:
        reason = f"unreadable {GROUPS_FILE}: {error}"
        raise GroupError(reason) from error
    try:
        parser.read_string(text)
    except configparser.Error as error:
        reason = f"malformed {GROUPS_FILE}: {error}"
        raise GroupError(reason) from error
    if parser.defaults():
        reason = f"malformed {GROUPS_FILE}: DEFAULT patterns are not group declarations"
        raise GroupError(reason)
    result: dict[str, Declaration] = {}
    for name in parser.sections():
        _validate_name(name)
        for side in ("tests", "sources"):
            if not parser.has_option(name, side):
                reason = f"group {name}: missing {side} key"
                raise GroupError(reason)
        result[name] = Declaration(
            group_patterns.normalized_patterns(parser.get(name, "tests").splitlines()),
            group_patterns.normalized_patterns(parser.get(name, "sources").splitlines()),
        )
    return result


def _validate_name(name: str) -> None:
    """Reject names that cannot safely identify a proof scope."""
    if not _NAME.fullmatch(name):
        reason = f"invalid group name: {name!r}"
        raise GroupError(reason)


def resolve_group(root: Path, name: str, files: Sequence[Path]) -> ResolvedScope:
    """Resolve a selected group using a supplied snapshot inventory.

    Args:
        root: The project root.
        name: The selected group.
        files: The snapshot inventory, already walked by the caller.

    Returns:
        Exact effective test and source membership.

    Raises:
        GroupError: For an invalid declaration or empty membership side.
    """
    _validate_name(name)
    declaration = read_declaration(root)
    if name not in declaration:
        reason = f"unknown group: {name}"
        raise GroupError(reason)
    return _resolve(root, name, declaration[name], files, Settings.load(root))


def list_groups(root: Path, files: Sequence[Path]) -> list[ResolvedScope]:
    """Resolve all declared groups with one declaration and settings read.

    Args:
        root: The project root.
        files: The snapshot inventory reused for every declared group.

    Returns:
        Resolved groups in declaration order.
    """
    declaration = read_declaration(root)
    settings = Settings.load(root)
    return [_resolve(root, name, entry, files, settings) for name, entry in declaration.items()]


def _resolve(root: Path, name: str, entry: Declaration, files: Sequence[Path], settings: Settings) -> ResolvedScope:
    """Match each candidate once against each fixed pattern list."""
    test_files, source_files = _membership(root, entry, files, settings)
    for side, members in (("test", test_files), ("source", source_files)):
        if not members:
            reason = f"group {name}: empty {side} side"
            raise GroupError(reason)
    resolved_tests, resolved_sources = ordered_strings(test_files), ordered_strings(source_files)
    return ResolvedScope(
        ScopeKind.GROUP, name, entry.tests, entry.sources, resolved_tests, resolved_sources,
        scope_fingerprint(name, entry.tests, entry.sources, resolved_tests, resolved_sources),
        {"declaration": GROUPS_FILE},
    )


def _membership(root: Path, entry: Declaration, files: Sequence[Path], settings: Settings) -> tuple[list[str], list[str]]:
    """Filter the supplied inventory with compiled collection and source rules."""
    tests = group_patterns.compile_patterns(entry.tests)
    sources = group_patterns.compile_patterns(entry.sources)
    python = group_patterns.compile_patterns(settings.python_files)
    omissions = _omissions(root, settings)
    test_files: list[str] = []
    source_files: list[str] = []
    for path in files:
        if path.suffix != ".py":
            continue
        relative = path.relative_to(root).as_posix()
        is_test = path.name != "conftest.py" and group_patterns.matches(python, path.name)
        if is_test and group_patterns.matches(tests, relative):
            test_files.append(relative)
        if group_patterns.matches(sources, relative) and not omissions.match(str(path)):
            source_files.append(relative)
    return test_files, source_files


def _omissions(root: Path, settings: Settings) -> GlobMatcher:
    """Anchor relative coverage omit patterns while retaining wildcard roots."""
    return GlobMatcher([
        pattern if pattern.startswith(("*", "?")) else str(root / pattern)
        for pattern in settings.omit
    ])


# eof
