"""Verify canonical-parent validation and role-scoped workflow fallback.

Both facade entry points preserve ordered local matches and missing draft paths.
Selection keeps local timestamp ties, rejects competing fallback documents, and
uses one discovery inventory without matching fallback files after local success.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_docs as docs
from tools import prompt_workflow_document_lookup as lookup
from tools.prompt_workflow_models import PromptWorkflowError, Topic

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

# pyright: reportPrivateUsage=false
# ruff: noqa: SLF001


@pytest.fixture(params=[
    ("requirement", "issue", ".md"),
    ("requirement", "feature-request", ".md"),
    ("design", "design", ".md"),
    ("plan", "plan", ".md"),
    ("validation_plan", "plan", ".validation.md"),
])
def role_case(request: pytest.FixtureRequest) -> tuple[str, str, str]:
    """Supply each role and both concrete requirement kinds independently."""
    role, kind, suffix = request.param
    return str(role), str(kind), str(suffix)


@pytest.fixture(params=[docs.find_matching_documents, docs.select_document])
def discover(request: pytest.FixtureRequest) -> Callable[[Path, Topic, str], object]:
    """Apply common validation and IO requirements to both facade entry points."""
    return request.param


def _document(directory: Path, name: str, timestamp: int = 1_000) -> Path:
    """Write a small document with a deterministic mtime."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text("document", encoding="utf-8")
    os.utime(path, (timestamp, timestamp))
    return path


def _topic(parent: Path) -> Topic:
    """Construct a topic without requiring its draft file to exist."""
    parent.mkdir(parents=True, exist_ok=True)
    return Topic("v1.2.3", "my_effort", parent / "draft.v1.2.3.my_effort.md")


def test_local_matches_keep_order_ties_and_newest_policy(
    tmp_path: Path, role_case: tuple[str, str, str],
) -> None:
    """Local scope wins over newer copies for every role and folded subtopic."""
    role, kind, suffix = role_case
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    topic = _topic(parent)
    subtopic = _document(parent, f"{kind}.v1.2.3.my_effort_extra{suffix}")
    exact = _document(parent, f"{kind}.v1.2.3.my-effort{suffix}")
    _document(tmp_path / "docs", exact.name, 3_000)

    assert not topic.draft_path.exists()
    assert docs.find_matching_documents(tmp_path, topic, role) == [exact, subtopic]
    assert docs.select_document(tmp_path, topic, role) == exact
    os.utime(subtopic, (2_000, 2_000))
    assert docs.select_document(tmp_path, topic, role) == subtopic


@pytest.mark.parametrize("count", [0, 1, 2, 3])
def test_fallback_cardinality_and_stable_diagnostics(
    tmp_path: Path, role_case: tuple[str, str, str], count: int,
) -> None:
    """Fallback lists all candidates but selection requires exactly one match."""
    role, kind, suffix = role_case
    topic = _topic(tmp_path / "docs" / "v1.2.3")
    directories = [tmp_path / "docs", tmp_path / "docs" / "v8.0", tmp_path / "docs" / "v9.0.0"]
    expected = [
        _document(directory, f"{kind}.v1.2.3.my-effort_extra{suffix}", 1_000 + index)
        for index, directory in enumerate(directories[:count])
    ]
    _document(topic.draft_path.parent, f"{kind}.v1.2.4.my-effort{suffix}")
    _document(topic.draft_path.parent, f"{kind}.v1.2.3.other{suffix}")

    assert not topic.draft_path.exists()
    assert docs.find_matching_documents(tmp_path, topic, role) == expected
    if count <= 1:
        assert docs.select_document(tmp_path, topic, role) == (expected[0] if expected else None)
        return
    _assert_fallback_ambiguity(tmp_path, topic, role, expected)


def _assert_fallback_ambiguity(root: Path, topic: Topic, role: str, expected: list[Path]) -> None:
    """Check contextual ambiguity details and candidate order without fixing prose."""
    with pytest.raises(PromptWorkflowError) as error:
        docs.select_document(root, topic, role)
    message = str(error.value)
    for value in (role, topic.version, topic.slug, "docs/v1.2.3"):
        assert value in message
    rendered = [path.relative_to(root).as_posix() for path in expected]
    positions = [message.index(path) for path in rendered]
    assert positions == sorted(positions)


@pytest.mark.parametrize("layout", [
    "docs", "docs/v1.2", "docs/v8.0.0", "docs/v8.0/v8.0.0", "docs/v8.0.0/elsewhere",
])
def test_fallback_searches_all_recognized_layouts(tmp_path: Path, layout: str) -> None:
    """Same-version filenames in other versions remain eligible for workflow lookup."""
    topic = _topic(tmp_path / "docs" / "v1.2.3" / "my-effort")
    _document(topic.draft_path.parent, "plan.v1.2.3.my-effort.validation.md")
    parent = tmp_path / layout
    _document(parent, "issue.v8.0.0.elsewhere.md")
    fallback = _document(parent, "plan.v1.2.3.my-effort_extra.md")

    assert docs.find_matching_documents(tmp_path, topic, "plan") == [fallback]
    assert docs.select_document(tmp_path, topic, "plan") == fallback


@pytest.mark.parametrize("layout", [
    "outside", "docs/assets", "docs/v1.2.3/wrong-slug", "docs/v1.2/v1.2.3/my-effort",
])
def test_invalid_parent_rejects_tempting_alternatives(
    tmp_path: Path, discover: Callable[[Path, Topic, str], object], layout: str,
) -> None:
    """Unsupported or identity-mismatched parents raise before broader matching."""
    parent = tmp_path / layout
    topic = _topic(parent)
    _document(parent, topic.draft_path.name)
    _document(tmp_path / "docs", "design.v1.2.3.my-effort.md")

    with pytest.raises(PromptWorkflowError) as error:
        discover(tmp_path, topic, "design")
    for value in ("design", topic.version, topic.slug, layout):
        assert value in str(error.value)


def test_parent_outside_repository_has_absolute_diagnostic(
    tmp_path: Path, discover: Callable[[Path, Topic, str], object],
) -> None:
    """A parent outside the lookup root is reported without a relative-path failure."""
    root = tmp_path / "repository"
    topic = _topic(tmp_path / "elsewhere")
    with pytest.raises(PromptWorkflowError) as error:
        discover(root, topic, "plan")
    assert topic.draft_path.parent.as_posix() in str(error.value)


def test_resolved_parent_identity_preserves_returned_paths(tmp_path: Path) -> None:
    """Normalized parent comparison accepts a draft path containing dot-dot."""
    parent = tmp_path / "docs" / "v1.2.3"
    topic = _topic(parent / ".." / "v1.2.3")
    local = _document(parent, "design.v1.2.3.my-effort.md")
    assert docs.find_matching_documents(tmp_path, topic, "design") == [local]
    assert docs.select_document(tmp_path, topic, "design") == local


def test_general_duplicates_remain_ambiguous_with_canonical_slug_parent(tmp_path: Path) -> None:
    """General exact lookup stays strict while workflow lookup prefers its parent."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    topic = _topic(parent)
    local = _document(parent, "design.v1.2.3.my-effort.md")
    _document(parent.parent, local.name, 2_000)
    with pytest.raises(PromptWorkflowError, match="Ambiguous"):
        docs.resolve_document(tmp_path, topic.version, topic.slug, "design")
    assert docs.find_matching_documents(tmp_path, topic, "design") == [local]
    assert docs.select_document(tmp_path, topic, "design") == local


@pytest.mark.parametrize("scope", ["local", "fallback"])
def test_selection_inventories_once_and_matches_only_necessary_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scope: str,
) -> None:
    """Count discovery separately from permitted eligibility reads in other efforts."""
    parent = tmp_path / "docs" / "v1.2.3"
    topic = _topic(parent)
    fallback_parent = parent / "elsewhere"
    _document(fallback_parent, "issue.v1.2.3.elsewhere.md")
    fallback = _document(fallback_parent, "design.v1.2.3.my-effort_sub.md")
    expected = _document(parent, "design.v1.2.3.my-effort.md") if scope == "local" else fallback
    inventories: list[Path] = []
    matched: list[str] = []
    original_dirs, original_match = lookup.docs_dirs, lookup._doc_matches

    def inventory(root: Path) -> list[Path]:
        inventories.append(root)
        return original_dirs(root)

    def match(name: str, role: str, version: str, slug: str) -> bool:
        matched.append(name)
        return original_match(name, role, version, slug)

    monkeypatch.setattr(lookup, "docs_dirs", inventory)
    monkeypatch.setattr(lookup, "_doc_matches", match)
    assert docs.select_document(tmp_path, topic, "design") == expected
    assert inventories == [tmp_path]
    assert matched.count(expected.name) == 1
    assert (fallback.name in matched) == (scope == "fallback")


def test_matching_enumeration_errors_propagate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    discover: Callable[[Path, Topic, str], object],
) -> None:
    """A recognized parent's entry failure stays an OSError for both callers."""
    topic = _topic(tmp_path / "docs")
    failure = OSError("matching entries unavailable")

    def denied(_path: Path) -> Iterator[Path]:
        raise failure

    monkeypatch.setattr(Path, "iterdir", denied)
    with pytest.raises(OSError, match="matching entries unavailable") as error:
        discover(tmp_path, topic, "design")
    assert error.value is failure


def test_local_mtime_errors_propagate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A stat failure after matching is surfaced instead of becoming absence."""
    topic = _topic(tmp_path / "docs")
    local = _document(topic.draft_path.parent, "design.v1.2.3.my-effort.md")
    original_match, original_stat = lookup._doc_matches, Path.stat
    matched = False
    failure = OSError("mtime unavailable")

    def match(name: str, role: str, version: str, slug: str) -> bool:
        nonlocal matched
        result = original_match(name, role, version, slug)
        matched = matched or result
        return result

    def stat(path: Path, *, follow_symlinks: bool = True) -> os.stat_result:
        if matched and path == local:
            raise failure
        return original_stat(path, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(lookup, "_doc_matches", match)
    monkeypatch.setattr(Path, "stat", stat)
    with pytest.raises(OSError, match="mtime unavailable") as error:
        docs.select_document(tmp_path, topic, "design")
    assert error.value is failure


# eof
