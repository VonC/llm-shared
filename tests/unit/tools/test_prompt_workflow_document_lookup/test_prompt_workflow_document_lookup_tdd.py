"""Preserve lookup behavior and require exact immediate effort evidence.

Exercise the docs facade with real files so callers retain exact ambiguity,
canonical-parent preference, plan distinctions and deterministic timestamp ties.
Both listings recognize slug directories from filenames without reading bodies,
retain older layouts, observe filesystem changes and surface enumeration errors.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow_docs as docs
from tools.prompt_workflow_models import PromptWorkflowError, Topic

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


@pytest.fixture(params=["all", "version"])
def listing(request: pytest.FixtureRequest) -> Callable[[Path], list[Path]]:
    """Exercise the same eligibility contract through both public listings."""
    if request.param == "all":
        return docs.docs_dirs
    return lambda root: docs.docs_dirs_for_version(root, "v1.2.3")


def _document(directory: Path, name: str, timestamp: int = 1_000) -> Path:
    """Create a real document with a controlled modification timestamp."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text("document", encoding="utf-8")
    os.utime(path, (timestamp, timestamp))
    return path


def test_exact_ambiguity_and_local_preference_share_the_facade(tmp_path: Path) -> None:
    """General resolution reports both duplicates while a topic selects its parent."""
    root_docs = tmp_path / "docs"
    parent = root_docs / "v0.12.0"
    name = "design.v0.12.0.lookup-topic.md"
    elsewhere = _document(root_docs, name, 2_000)
    local = _document(parent, name)
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")

    assert docs.find_documents(tmp_path, topic.version, topic.slug, "design") == [
        elsewhere, local,
    ]
    with pytest.raises(PromptWorkflowError, match="Ambiguous design document") as error:
        docs.resolve_document(tmp_path, topic.version, topic.slug, "design")
    assert elsewhere.relative_to(tmp_path).as_posix() in str(error.value)
    assert local.relative_to(tmp_path).as_posix() in str(error.value)
    assert docs.find_matching_documents(tmp_path, topic, "design") == [local]
    assert docs.select_document(tmp_path, topic, "design") == local


@pytest.mark.parametrize(
    ("document_type", "role", "suffix"),
    [("plan", "plan", ".md"), ("validation-plan", "validation_plan", ".validation.md")],
)
def test_exact_and_workflow_plan_kinds_remain_distinct(
    tmp_path: Path,
    document_type: str,
    role: str,
    suffix: str,
) -> None:
    """Each lookup entry point selects its own plan kind despite a sibling plan."""
    parent = tmp_path / "docs"
    _document(parent, "plan.v0.12.0.lookup-topic.md")
    _document(parent, "plan.v0.12.0.lookup-topic.validation.md")
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")
    expected = parent / f"plan.v0.12.0.lookup-topic{suffix}"

    assert docs.resolve_document(tmp_path, topic.version, topic.slug, document_type) == expected
    assert docs.find_matching_documents(tmp_path, topic, role) == [expected]
    assert docs.select_document(tmp_path, topic, role) == expected


def test_local_timestamp_ties_preserve_sorted_candidate_order(tmp_path: Path) -> None:
    """Equal mtimes retain the first sorted path; a newer subtopic still wins."""
    parent = tmp_path / "docs" / "v0.12.0"
    subtopic = _document(parent, "design.v0.12.0.lookup_topic_extra.md")
    exact = _document(parent, "design.v0.12.0.lookup-topic.md")
    topic = Topic("v0.12.0", "lookup_topic", parent / "draft.v0.12.0.lookup_topic.md")

    assert docs.find_matching_documents(tmp_path, topic, "design") == [exact, subtopic]
    assert docs.select_document(tmp_path, topic, "design") == exact
    assert docs.most_recent([subtopic, exact]) == subtopic
    os.utime(subtopic, (2_000, 2_000))
    assert docs.select_document(tmp_path, topic, "design") == subtopic
    assert docs.most_recent([]) is None


@pytest.mark.parametrize(
    "name",
    [
        "draft.v1.2.3.my_effort.md",
        "feature-request.v1.2.3.my_effort.md",
        "issue.v1.2.3.my_effort.md",
        "design.v1.2.3.my_effort.md",
        "plan.v1.2.3.my_effort.md",
        "plan.v1.2.3.my_effort.validation.md",
    ],
)
def test_each_concrete_document_qualifies_without_other_evidence(
    tmp_path: Path, listing: Callable[[Path], list[Path]], name: str,
) -> None:
    """Any of the six concrete kinds suffices, including a lone validation plan."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    _document(parent, name)

    assert parent in listing(tmp_path)


@pytest.mark.parametrize(
    "name",
    [
        "", "picture.png", "notes.md", "review.code.v1.2.3.my-effort.md",
        "a.issue.v1.2.3.my-effort.md", "requirement.v1.2.3.my-effort.md",
        "issue.v1.2.4.my-effort.md", "issue.v1.2.my-effort.md",
        "issue.v1.2.3.other.md", "issue.v1.2.3.my-effort-sub.md",
        "issue.v1.2.3.my_effort_sub.md", "issue.v1.2.3.my.md",
        "plan.v1.2.3.my-effort-sub.validation.md", "issue.v1.2.3.my-effort.txt",
        "design.v1.2.3.my-effort.validation.md", "draft.v1.2.3.my-effort.MD",
        "nested/issue.v1.2.3.my-effort.md",
    ],
)
def test_empty_or_unrelated_content_does_not_qualify(
    tmp_path: Path, listing: Callable[[Path], list[Path]], name: str,
) -> None:
    """Shape, body content, subtopic prefixes and nested evidence are insufficient."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    parent.mkdir(parents=True)
    if name:
        entry = parent / name
        _document(entry.parent, entry.name)

    assert parent not in listing(tmp_path)


def test_matching_directory_name_is_not_a_regular_file(
    tmp_path: Path, listing: Callable[[Path], list[Path]],
) -> None:
    """A directory with a qualifying filename cannot stand in for a file."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    (parent / "issue.v1.2.3.my-effort.md").mkdir(parents=True)

    assert parent not in listing(tmp_path)


@pytest.mark.parametrize("slug", ["images", "sub", "my_effort", "my-effort"])
def test_effort_names_and_unrelated_siblings_do_not_disqualify(
    tmp_path: Path, listing: Callable[[Path], list[Path]], slug: str,
) -> None:
    """Common asset names and both separator spellings qualify with exact evidence."""
    parent = tmp_path / "docs" / "v1.2.3" / slug
    _document(parent, f"issue.v1.2.3.{slug.replace('_', '-')}.md")
    _document(parent, "picture.png")
    _document(parent, "review.code.v1.2.3.other.md")
    unrelated = parent.parent / "unrelated"
    _document(unrelated, f"issue.v1.2.3.{slug}.md")

    found = listing(tmp_path)
    assert parent in found
    assert unrelated not in found


@pytest.mark.parametrize("relative", ["docs", "docs/v1.2", "docs/v1.2.3", "docs/v1.2/v1.2.3"])
def test_older_empty_layouts_remain_recognized(
    tmp_path: Path, listing: Callable[[Path], list[Path]], relative: str,
) -> None:
    """The content restriction leaves all four older empty layouts supported."""
    parent = tmp_path / relative
    parent.mkdir(parents=True)

    assert parent in listing(tmp_path)


@pytest.mark.parametrize(
    "relative", ["v1.2.3/My-effort", "v1.2.3/my.effort", "v1.2/v1.2.3/my-effort"],
)
def test_unsupported_shapes_stay_rejected_despite_matching_content(
    tmp_path: Path, listing: Callable[[Path], list[Path]], relative: str,
) -> None:
    """Content does not extend slug spelling or supported nesting depth."""
    parent = tmp_path / "docs" / relative
    _document(parent, f"issue.v1.2.3.{parent.name}.md")

    assert parent not in listing(tmp_path)


def test_listings_keep_their_existing_order_and_version_scope(tmp_path: Path) -> None:
    """General ordering and narrow version enumeration remain distinct."""
    root_docs = tmp_path / "docs"
    minor = root_docs / "v1.2"
    full = root_docs / "v1.2.3"
    nested = minor / "v1.2.3"
    nested.mkdir(parents=True)
    for slug in ("zeta", "alpha"):
        _document(full / slug, f"issue.v1.2.3.{slug}.md")
    other = root_docs / "v2.0.0"
    _document(other / "other", "issue.v2.0.0.other.md")

    assert docs.docs_dirs(tmp_path) == [
        root_docs, minor, nested, full, full / "alpha", full / "zeta", other, other / "other",
    ]
    assert docs.docs_dirs_for_version(tmp_path, "v1.2.3") == [
        root_docs, minor, full, nested, full / "alpha", full / "zeta",
    ]
    assert docs.docs_dirs_for_version(tmp_path, "v1.2") == [root_docs, minor]


def test_content_changes_are_visible_without_restarting(
    tmp_path: Path, listing: Callable[[Path], list[Path]],
) -> None:
    """Add, rename away, restore and remove the last qualifying file in one process."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    parent.mkdir(parents=True)
    assert parent not in listing(tmp_path)
    document = _document(parent, "plan.v1.2.3.my_effort.validation.md")
    assert parent in listing(tmp_path)
    renamed = document.rename(parent / "plan.v1.2.3.other.validation.md")
    assert parent not in listing(tmp_path)
    renamed.rename(document)
    assert parent in listing(tmp_path)
    document.unlink()
    assert parent not in listing(tmp_path)


def test_recognition_does_not_read_document_bodies(
    tmp_path: Path, listing: Callable[[Path], list[Path]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Even invalid UTF-8 content qualifies solely through its immediate filename."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    parent.mkdir(parents=True)
    (parent / "issue.v1.2.3.my-effort.md").write_bytes(b"\xff\x00")

    def forbid_read(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Recognition must not open a document body")

    monkeypatch.setattr(Path, "read_text", forbid_read)
    monkeypatch.setattr(Path, "read_bytes", forbid_read)
    monkeypatch.setattr(Path, "open", forbid_read)
    assert parent in listing(tmp_path)


def test_entry_enumeration_errors_propagate(
    tmp_path: Path, listing: Callable[[Path], list[Path]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A surfaced failure while inspecting evidence is never reported as absence."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    parent.mkdir(parents=True)
    original = Path.iterdir

    def fail_entries(path: Path) -> Iterator[Path]:
        if path == parent:
            msg = "Cannot enumerate effort evidence"
            raise OSError(msg)
        return original(path)

    monkeypatch.setattr(Path, "iterdir", fail_entries)
    with pytest.raises(OSError, match="Cannot enumerate effort evidence"):
        listing(tmp_path)


def test_eligibility_stops_after_first_exact_file(
    tmp_path: Path, listing: Callable[[Path], list[Path]], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Qualification does not enumerate further evidence after its first match."""
    parent = tmp_path / "docs" / "v1.2.3" / "my-effort"
    document = _document(parent, "issue.v1.2.3.my-effort.md")
    original = Path.iterdir

    def limited_entries(path: Path) -> Iterator[Path]:
        if path == parent:
            yield document
            pytest.fail("Eligibility continued past qualifying evidence")
        else:
            yield from original(path)

    monkeypatch.setattr(Path, "iterdir", limited_entries)
    assert parent in listing(tmp_path)


# eof
