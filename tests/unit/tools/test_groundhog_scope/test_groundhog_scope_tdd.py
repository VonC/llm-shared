"""Resolve scope once, reject ambiguity, and trust only validated captures.

Fix (v0.13.0 full_suite_levels, Step 4): only group declarations request
the lazy source inventory.
"""

from argparse import Namespace
from pathlib import Path

import pytest

from tests.unit.tools.groundhog_group_support import group_project
from tools.groundhog import scope, snapshot
from tools.scope_capture import WHOLE_SCOPE


def args(**options: object) -> Namespace:
    """Build a free-option namespace as the parser does."""
    return Namespace(**{"group": None, "whole_suite": False, "scope_file": None, **options})


def forbidden(_name: str) -> str:
    """Detect any environment lookup after explicit selection."""
    pytest.fail("explicit scope must not read GHOG_GROUP")


def forbidden_inventory() -> tuple[Path, ...]:
    """Detect a tree scan when the selection requires no group resolution."""
    pytest.fail("scope must not request a source inventory")


@pytest.mark.parametrize("options", [{"whole_suite": True}, {"group": "sentinel"}])
def test_explicit_wins_without_environment(tmp_path: Path, options: dict[str, object]) -> None:
    """An invalid ambient value cannot affect any explicit selector."""
    group_project(tmp_path)
    actual = scope.resolve_scope(args(**options), forbidden, tmp_path, lambda: snapshot.source_files(tmp_path))
    assert actual.key() == ("whole" if "whole_suite" in options else "group:sentinel")


@pytest.mark.parametrize("value", [None, "", "sentinel", "nope", "../bad"])
def test_environment_and_default(tmp_path: Path, value: str | None) -> None:
    """Empty environment selects whole; nonempty values are validated."""
    group_project(tmp_path)
    if value in ("nope", "../bad"):
        with pytest.raises(scope.ScopeError):
            scope.resolve_scope(args(), lambda _: value, tmp_path, lambda: snapshot.source_files(tmp_path))
    else:
        actual = scope.resolve_scope(args(), lambda _: value, tmp_path, lambda: snapshot.source_files(tmp_path))
        assert actual.key() == ("group:sentinel" if value else "whole")


@pytest.mark.parametrize("options", [
    {"group": "sentinel", "whole_suite": True},
    {"group": "sentinel", "scope_file": "capture"},
    {"whole_suite": True, "scope_file": "capture"},
])
def test_conflicting_selectors(tmp_path: Path, options: dict[str, object]) -> None:
    """Report every conflicting selector before looking up environment or files."""
    with pytest.raises(scope.ScopeError) as error:
        scope.resolve_scope(args(**options), forbidden, tmp_path, forbidden_inventory)
    for option in options:
        assert "--" + option.replace("_", "-") in str(error.value)


def test_whole_never_reads_declaration(tmp_path: Path) -> None:
    """A declaration that cannot be read is irrelevant to whole scope."""
    (tmp_path / ".ghog-groups").mkdir()
    assert scope.resolve_scope(args(whole_suite=True), forbidden, tmp_path, forbidden_inventory) == WHOLE_SCOPE


def test_capture_is_bound_and_relative_to_root(tmp_path: Path) -> None:
    """A saved capture survives declaration edits without resolving its name."""
    group_project(tmp_path)
    original = scope.resolve_scope(args(group="sentinel"), forbidden, tmp_path, lambda: snapshot.source_files(tmp_path))
    capture = scope.write_detach_capture(tmp_path, original)
    (tmp_path / ".ghog-groups").unlink()
    actual = scope.resolve_scope(args(scope_file=str(capture.relative_to(tmp_path))), forbidden, tmp_path, forbidden_inventory)
    assert actual == original
    assert capture.name == "a.ghog.day.scope.json"


@pytest.mark.parametrize("content", [None, "{}", "not json", "\udcff"])
def test_unusable_capture(tmp_path: Path, content: str | None) -> None:
    """Missing, corrupt and unreadable captures never fall back."""
    path = tmp_path / "capture.json"
    if content is not None:
        path.write_bytes(content.encode("utf-8", errors="surrogateescape"))
    with pytest.raises(scope.ScopeError, match="bound scope unusable:"):
        scope.resolve_scope(args(scope_file=str(path)), forbidden, tmp_path, forbidden_inventory)
