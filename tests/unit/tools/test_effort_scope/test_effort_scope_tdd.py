"""Prove header-only scope selection, provenance and fail-closed validation.

The reader never consults a draft or environment and only inventories files
for a named group. Resolver pattern properties are covered in its own package.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.groundhog_group_support import group_project
from tools import effort_scope
from tools.scope_capture import WHOLE_SCOPE

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator


def _requirement(root: Path, body: str) -> Path:
    """Write an effort header at a relative document path."""
    path = root / "docs" / "issue.v1.0.0.topic.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_no_requirement_never_reads_the_draft_or_inventory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An uncreated requirement is explicitly whole suite, even with a stale draft."""
    (tmp_path / "draft.v1.0.0.topic.md").write_text("- Test group: sentinel\n", encoding="utf-8")

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("no requirement must not read files")

    monkeypatch.setattr(Path, "open", forbidden)
    monkeypatch.setattr(effort_scope.snapshot, "source_files", forbidden)
    result = effort_scope.read_effort_scope(tmp_path, None)
    assert result.scope == WHOLE_SCOPE
    assert result.source_path is None
    assert result.reason == "no requirement yet"


@pytest.mark.parametrize(("body", "reason"), [
    ("# Requirement\n\n## Behavior\n- Test group: unknown\n", "no Test group line in docs/issue.v1.0.0.topic.md"),
    ("- Test group: whole suite\n", "docs/issue.v1.0.0.topic.md"),
])
def test_whole_suite_sources_need_no_inventory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str, reason: str,
) -> None:
    """Absence and an explicit whole-suite value retain their distinct source reasons."""
    path = _requirement(tmp_path, body)

    def forbidden(_root: Path) -> list[Path]:
        pytest.fail("whole suite needs no group inventory")

    monkeypatch.setattr(effort_scope.snapshot, "source_files", forbidden)
    monkeypatch.setenv("GHOG_GROUP", "sentinel")
    result = effort_scope.read_effort_scope(tmp_path, path.relative_to(tmp_path))
    assert result.scope == WHOLE_SCOPE
    assert result.source_path == path
    assert result.reason == reason


def test_group_returns_exact_membership_fingerprint_and_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One inventory provides the same resolution as groundhog, with source provenance."""
    group_project(tmp_path)
    path = _requirement(tmp_path, "# Requirement\n- Test group: sentinel\n\n## Body\n- Test group: other\n")
    inventories: list[Path] = []
    source_files = effort_scope.snapshot.source_files

    def inventory(root: Path) -> list[Path]:
        inventories.append(root)
        return source_files(root)

    monkeypatch.setattr(effort_scope.snapshot, "source_files", inventory)
    result = effort_scope.read_effort_scope(tmp_path, path)
    expected = effort_scope.groups.resolve_group(tmp_path, "sentinel", source_files(tmp_path))
    assert result.scope == expected
    assert result.scope.selector() == "--group=sentinel"
    assert result.scope.fingerprint
    assert result.source_path == path
    assert result.reason == "docs/issue.v1.0.0.topic.md"
    assert inventories == [tmp_path]


@pytest.mark.parametrize(("body", "cause"), [
    ("- Test group: unknown\n", "unknown group: unknown"),
    ("- Test group:\n", "empty Test group"),
    ("- Test group:   \n", "empty Test group"),
    ("- Test group: sentinel\n- Test group: other\n", "two Test group lines"),
    ("- Test group: whole suite\n- Test group: whole suite\n", "two Test group lines"),
])
def test_invalid_metadata_names_the_requirement_and_cause(tmp_path: Path, body: str, cause: str) -> None:
    """No malformed declaration silently falls back to the whole suite."""
    group_project(tmp_path)
    path = _requirement(tmp_path, body)
    with pytest.raises(effort_scope.EffortScopeError, match=cause) as caught:
        effort_scope.read_effort_scope(tmp_path, path)
    assert "docs/issue.v1.0.0.topic.md" in str(caught.value)


def test_empty_group_membership_is_a_requirement_error(tmp_path: Path) -> None:
    """A declared group with no effective tests is refused with its source."""
    group_project(tmp_path)
    (tmp_path / "tests/sentinel/test_core.py").unlink()
    path = _requirement(tmp_path, "- Test group: sentinel\n")
    with pytest.raises(effort_scope.EffortScopeError, match=r"issue.*empty test side"):
        effort_scope.read_effort_scope(tmp_path, path)


@pytest.mark.parametrize("content", [None, b"\xff"])
def test_unreadable_requirement_is_not_treated_as_absent(tmp_path: Path, content: bytes | None) -> None:
    """Missing files and invalid UTF-8 are errors rather than whole-suite defaults."""
    path = tmp_path / "issue.md"
    if content is not None:
        path.write_bytes(content)
    with pytest.raises(effort_scope.EffortScopeError, match=r"issue\.md:.*read"):
        effort_scope.read_effort_scope(tmp_path, path)


def test_header_reader_stops_iteration_at_the_first_level_two_heading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The body is not iterated, even when it contains metadata examples."""
    path = _requirement(tmp_path, "- Test group: whole suite\n## Behavior\n")

    def header() -> Iterator[str]:
        yield "- Test group: whole suite\n"
        yield "## Behavior\n"
        pytest.fail("requirement body was read")

    @contextmanager
    def open_header(*_args: object, **_kwargs: object) -> Generator[Iterator[str]]:
        yield header()

    monkeypatch.setattr(Path, "open", open_header)
    assert effort_scope.read_effort_scope(tmp_path, path).scope == WHOLE_SCOPE


# eof
