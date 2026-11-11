"""Tag names, annotation eligibility and release boundaries.

Step 8 of v0.14.0 version-sources: `vX.Y.Z` and `X.Y.Z` are stable release
names; `-SNAPSHOT` in any case marks a development marker; every other name,
other prereleases included, is ignored. Eligibility follows every row of the
design's table, by whole lines: a lightweight tag, or an annotation without a
trailer line, is historical (with or without `[valid]`); a trailer as the last
nonempty line is an unvalidated engine release, and before a final `[valid]`
a validated one; a trailer elsewhere, two trailers or `[valid]` before the
trailer are ambiguous. A trailer inside a notes line, or `Release tooling:`
without a value, is no trailer. Tags of one version on one commit form one
boundary, which takes the most restrictive class of its aliases (design
decision Q18) and is named by its `vX.Y.Z` alias when it has one (Q19); one
version on two commits, or two versions on one commit, fail naming the tags.
"""

from __future__ import annotations

import pytest

from tests.unit.tools.release_workflow.version_support import ENGINE_TRAILER, annotation
from tools.release_workflow import tags
from tools.release_workflow.git import TagRecord
from tools.release_workflow.sources.model import VersionToken
from tools.release_workflow.tags import BoundaryClass, Eligibility, RangeError

_PREFLIGHT = 2


def _tag(name: str, commit: str = "c1", text: str | None = None) -> tags.ClassifiedTag:
    """Classify a stable tag record, which must classify."""
    classified = tags.classify(TagRecord(name, "commit" if text is None else "tag", commit, text))
    assert classified is not None
    return classified


@pytest.mark.parametrize(("name", "kind", "token", "prefixed"), [
    ("v0.13.0", tags.StableName, "0.13.0", True),
    ("0.13.0", tags.StableName, "0.13.0", False),
    ("v10.0.25", tags.StableName, "10.0.25", True),
    ("v0.14.0-SNAPSHOT", tags.SnapshotName, "0.14.0", True),
    ("0.14.0-snapshot", tags.SnapshotName, "0.14.0", False),
    ("v0.14.0-Snapshot", tags.SnapshotName, "0.14.0", True),
])
def test_release_and_snapshot_names(name: str, kind: type, token: str, *, prefixed: bool) -> None:
    """Stable names in both spellings and snapshot markers in every suffix case."""
    parsed = tags.parse_name(name)
    assert parsed is not None
    assert isinstance(parsed, kind)
    assert (parsed.name, str(parsed.token), parsed.prefixed) == (name, token, prefixed)


@pytest.mark.parametrize("name", ["v0.14.0-rc1", "0.14.0-beta.1", "V0.13.0", "v01.13.0", "v0.13", "release-0.13.0", "v0.13.0.1", ""])
def test_other_names_are_not_releases(name: str) -> None:
    """Other prereleases, other spellings and other names are ignored."""
    assert tags.parse_name(name) is None


@pytest.mark.parametrize(("text", "expected"), [
    (None, Eligibility.HISTORICAL),
    (annotation(), Eligibility.HISTORICAL),
    (annotation(valid=True), Eligibility.HISTORICAL),
    (annotation(trailer=True, valid=True), Eligibility.VALIDATED),
    (annotation(trailer=True), Eligibility.UNVALIDATED),
    (annotation(trailer=True) + "\n\n", Eligibility.UNVALIDATED),
    (annotation(trailer=True, valid=True).replace("\n", "\r\n") + "\r\n", Eligibility.VALIDATED),
    (f"Notes\n{ENGINE_TRAILER}\nMore notes\n", Eligibility.AMBIGUOUS),
    (f"Notes\n{ENGINE_TRAILER}\n{ENGINE_TRAILER}\n[valid]\n", Eligibility.AMBIGUOUS),
    (f"Notes\n[valid]\n{ENGINE_TRAILER}\n", Eligibility.AMBIGUOUS),
    (f"Notes\n{ENGINE_TRAILER}\n[valid]\n[valid]\n", Eligibility.AMBIGUOUS),
    (f"Notes\n{ENGINE_TRAILER}\n[valid] \n", Eligibility.AMBIGUOUS),
    (f"See {ENGINE_TRAILER} for details\n", Eligibility.HISTORICAL),
    ("Notes\nRelease tooling:\n[valid]\n", Eligibility.HISTORICAL),
    ("Notes\nRelease tooling:   \n", Eligibility.HISTORICAL),
    ("Notes\nRelease tooling:x\n", Eligibility.HISTORICAL),
])
def test_eligibility_follows_the_design_table(text: str | None, expected: Eligibility) -> None:
    """Whole lines decide: the trailer's place, its count and the `[valid]` line after it."""
    assert tags.eligibility(text) is expected


def test_classify_keeps_stable_tags_only() -> None:
    """A stable record keeps its record, name and class; snapshot and other tags are dropped."""
    record = TagRecord("v0.13.0", "tag", "c3", annotation(trailer=True, valid=True))
    classified = tags.classify(record)
    assert classified is not None
    assert (classified.record, classified.name.token, classified.eligibility) == (record, VersionToken.parse("0.13.0"), Eligibility.VALIDATED)
    assert tags.classify(TagRecord("v0.14.0-SNAPSHOT", "commit", "c4", None)) is None
    assert tags.classify(TagRecord("nightly", "commit", "c4", None)) is None


@pytest.mark.parametrize(("aliases", "status", "name"), [
    ((("0.13.0", None),), BoundaryClass.ELIGIBLE, "0.13.0"),
    ((("0.13.0", None), ("v0.13.0", annotation(trailer=True, valid=True))), BoundaryClass.ELIGIBLE, "v0.13.0"),
    ((("0.13.0", None), ("v0.13.0", annotation(trailer=True))), BoundaryClass.INELIGIBLE, "v0.13.0"),
    ((("v0.13.0", annotation(trailer=True, valid=True)), ("0.13.0", annotation(trailer=True))), BoundaryClass.INELIGIBLE, "v0.13.0"),
    ((("v0.13.0", annotation(trailer=True, valid=True)), ("0.13.0", f"x\n{ENGINE_TRAILER}\ny\n")), BoundaryClass.AMBIGUOUS, "v0.13.0"),
    ((("v0.13.0", annotation(trailer=True)), ("0.13.0", annotation(trailer=True))), BoundaryClass.INELIGIBLE, "v0.13.0"),
    ((("v0.13.0", f"x\n{ENGINE_TRAILER}\ny\n"), ("0.13.0", f"[valid]\n{ENGINE_TRAILER}\n")), BoundaryClass.AMBIGUOUS, "v0.13.0"),
    ((("v0.13.0", annotation(trailer=True)),), BoundaryClass.INELIGIBLE, "v0.13.0"),
])
def test_a_boundary_takes_the_most_restrictive_class_and_its_v_alias(aliases: tuple[tuple[str, str | None], ...], status: BoundaryClass, name: str) -> None:
    """Ambiguous, then not eligible, then eligible; the `vX.Y.Z` alias names the boundary."""
    boundary, = tags.boundaries([_tag(alias, "c3", text) for alias, text in aliases])
    assert (boundary.status, boundary.name, boundary.commit, str(boundary.version)) == (status, name, "c3", "0.13.0")
    assert boundary.spelled == " and ".join(sorted(alias for alias, _text in aliases))


def test_boundaries_keep_first_appearance_order() -> None:
    """Each version on its own commit is one boundary, in listing order."""
    found = tags.boundaries([_tag("v0.2.0", "c2"), _tag("0.1.0", "c1"), _tag("v0.1.0", "c1")])
    assert [(boundary.name, boundary.commit) for boundary in found] == [("v0.2.0", "c2"), ("v0.1.0", "c1")]


@pytest.mark.parametrize(("aliases", "named"), [
    ((("0.13.0", "c1"), ("v0.13.0", "c2")), r"conflicting tags 0\.13\.0 and v0\.13\.0: version 0\.13\.0 is tagged on commits c1 and c2"),
    ((("v1.0.0", "c1"), ("v1.1.0", "c1")), r"conflicting tags v1\.0\.0 and v1\.1\.0: commit c1 carries versions 1\.0\.0 and 1\.1\.0"),
])
def test_conflicting_tags_fail_naming_them(aliases: tuple[tuple[str, str], ...], named: str) -> None:
    """One version on two commits, or two versions on one commit, is never grouped."""
    with pytest.raises(RangeError, match=named) as caught:
        tags.boundaries([_tag(alias, commit) for alias, commit in aliases])
    assert caught.value.exit_code == _PREFLIGHT


# eof
