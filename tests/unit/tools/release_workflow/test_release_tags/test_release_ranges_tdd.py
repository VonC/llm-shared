"""Range selection and the release-version rule over declared histories.

Step 8 of v0.14.0 version-sources: every AC13, AC14 and AC15 row of the design
on declared histories, with the Git calls recorded and checked against the
plan's call table in every case. A snapshot at HEAD gives the previous stable
release as baseline; an unvalidated engine tag is never a baseline and is
excluded with a warning; `range v0.13.0` never selects itself; a release at
HEAD gives an empty range; no candidate gives the full history; conflicting
tags, independent tips, a version inversion and an ambiguous tag after the
baseline fail with status 2; a missing tag target is status 2 from the one
records call, a Git execution failure of that call status 1, and an oversized
tips query status 1 before it starts. Aliased boundaries follow design
decisions Q18 and Q19. The release-version rule reserves either spelling,
bounds by eligible boundaries on `main` numerically and makes two calls.
Consumer-shaped histories (twelve validated `vX.Y.Z` tags; 99 mixed tags with
one snapshot; the mixed `v0.0.20` to `v0.0.24` chain) select as expected.

Code review round 1: every invocation now asserts its complete ordered calls,
arguments included, where a test selected or checked several times without
it (`_take` checks each invocation alone; `_selection_calls` builds the call
table's sequence), and the canned failure records the query it refuses.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.repository_simulation import (
    RepositoryObservations,
)
from tests.unit.tools.release_workflow.version_support import (
    ENGINE_TRAILER,
    annotation,
    tagged_history,
)
from tools.release_workflow import tags
from tools.release_workflow.git import (
    GitCommandError,
    GitCommandLineTooLongError,
    GitRevisionNotFoundError,
)
from tools.release_workflow.sources.model import VersionError
from tools.release_workflow.tags import RangeError, RangeSelection

if TYPE_CHECKING:
    from pathlib import Path

    from tests.unit.tools.release_workflow.git_test_support import GitSandbox
    from tests.unit.tools.release_workflow.repository_simulation import ReleaseHistory

_PREFLIGHT = 2
_EXECUTION = 1
_VALID = annotation(trailer=True, valid=True)
_UNVALIDATED = annotation(trailer=True)
_AMBIGUOUS = f"Notes\n{ENGINE_TRAILER}\nMore notes\n"
_ONE = ["tag_records", "tag_names", "commit_count"]
_SEVERAL = ["tag_records", "independent_commits", "tag_names", "commit_count"]
_NONE = ["tag_records", "commit_count"]


def _calls(history: ReleaseHistory) -> list[str]:
    """Name the recorded Git calls in order."""
    return [call[0] for call in history.calls]


def _take(history: ReleaseHistory) -> list[tuple[str, ...]]:
    """Return the calls recorded since the last take, then forget them, so each invocation is checked alone."""
    calls = list(history.calls)
    history.calls.clear()
    return calls


def _selection_calls(revision: str, candidates: list[str], baseline: str) -> list[tuple[str, ...]]:
    """Build the call table's sequence for a selection with a baseline: records, tips when several candidates, tags between, count."""
    tips = [("independent_commits", *candidates)] if len(candidates) > 1 else []
    start = f"refs/tags/{baseline}"
    return [("tag_records", revision), *tips, ("tag_names", revision, start), ("commit_count", f"{start}..{revision}")]


def _fails(git: RepositoryObservations, tmp_path: Path, named: str, target: str | None = None) -> RangeError:
    """Expect a status 2 selection failure matching `named`."""
    with pytest.raises(RangeError, match=named) as caught:
        tags.select_range(git, cwd=tmp_path, target=target)
    assert caught.value.exit_code == _PREFLIGHT
    return caught.value


def test_a_snapshot_at_head_gives_the_previous_release(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """`v0.14.0-SNAPSHOT` on HEAD after `v0.13.0`: baseline `v0.13.0`, range `v0.13.0..HEAD`."""
    git, history = tagged_history(git_sandbox, 3, {"v0.13.0": (2, annotation()), "v0.14.0-SNAPSHOT": (3, None)})
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.13.0", "v0.13.0..HEAD", 1, ())
    assert history.calls == [("tag_records", "HEAD"), ("tag_names", "HEAD", "refs/tags/v0.13.0"),
                             ("commit_count", "refs/tags/v0.13.0..HEAD")]


def test_an_unvalidated_engine_tag_is_never_a_baseline(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """An engine tag without `[valid]` stays out, with a warning; the baseline is the previous release."""
    git, history = tagged_history(git_sandbox, 5, {"v0.13.0": (2, annotation()), "v0.14.0": (4, _UNVALIDATED)})
    selection = tags.select_range(git, cwd=tmp_path)
    assert (selection.baseline, selection.range, selection.commits) == ("v0.13.0", "v0.13.0..HEAD", 3)
    assert selection.warnings == ("excluded unvalidated engine release v0.14.0 between v0.13.0 and HEAD",)
    assert _calls(history) == _ONE


def test_a_tag_target_never_selects_itself(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """`range v0.13.0` after `v0.12.0` gives `v0.12.0..v0.13.0`, through `refs/tags` revisions."""
    git, history = tagged_history(git_sandbox, 4, {"v0.12.0": (1, None), "v0.13.0": (3, annotation())})
    assert tags.select_range(git, cwd=tmp_path, target="v0.13.0") == RangeSelection("v0.13.0", "v0.12.0", "v0.12.0..v0.13.0", 2, ())
    assert history.calls == [("tag_records", "refs/tags/v0.13.0"), ("tag_names", "refs/tags/v0.13.0", "refs/tags/v0.12.0"),
                             ("commit_count", "refs/tags/v0.12.0..refs/tags/v0.13.0")]


def test_a_release_at_head_gives_an_empty_range(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """HEAD on `v0.13.0` keeps it as candidate: zero commits after it."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), "v0.13.0": (3, _VALID)})
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.13.0", "v0.13.0..HEAD", 0, ())
    assert _calls(history) == _SEVERAL


@pytest.mark.parametrize(("declared", "expected"), [
    ({}, RangeSelection("HEAD", None, "HEAD", 4, ())),
    ({"v0.14.0-SNAPSHOT": (4, None), "nightly": (2, None)}, RangeSelection("HEAD", None, "HEAD", 4, ())),
    ({"v0.1.0": (3, None)}, RangeSelection("v0.1.0", None, "v0.1.0", 3, ())),
    ({"v0.2.0": (2, _UNVALIDATED)}, RangeSelection("HEAD", None, "HEAD", 4, ("excluded unvalidated engine release v0.2.0 before HEAD",))),
])
def test_without_a_candidate_the_range_is_the_full_history(git_sandbox: GitSandbox, tmp_path: Path, declared: dict[str, tuple[int, str | None]],
                                                           expected: RangeSelection) -> None:
    """No eligible release before the target: the whole history through it, counted in one call."""
    git, history = tagged_history(git_sandbox, 4, declared)
    target = None if expected.target == "HEAD" else expected.target
    assert tags.select_range(git, cwd=tmp_path, target=target) == expected
    assert _calls(history) == _NONE


def test_several_candidates_take_the_independent_tip(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """Older releases are ancestors of the baseline; the count is the distance to the target."""
    git, history = tagged_history(git_sandbox, 6, {"v0.1.0": (1, None), "0.2.0": (2, annotation(valid=True)), "v0.3.0": (3, _VALID)})
    selection = tags.select_range(git, cwd=tmp_path)
    assert (selection.baseline, selection.range, selection.commits) == ("v0.3.0", "v0.3.0..HEAD", 3)
    assert history.calls[1] == ("independent_commits", "c1", "c2", "c3")
    assert _calls(history) == _SEVERAL


def test_independent_tips_from_merged_parallel_histories_fail(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """Two eligible releases that are not ancestors of each other are a conflict, never guessed."""
    git = git_sandbox.context()
    history = git.facts.history
    base = history.commit("c1")
    main_line, side = history.commit("c2", base), history.commit("s1", base)
    history.head = history.main = history.commit("m1", main_line, side)
    history.tag("v0.1.0", base)
    history.tag("v0.2.0", main_line)
    history.tag("v0.1.1", side)
    _fails(git, tmp_path, r"several independent eligible releases: v0\.1\.1 and v0\.2\.0")
    assert _calls(history) == ["tag_records", "independent_commits"]


def test_a_version_inversion_fails(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A baseline lower than an earlier candidate is refused."""
    git, history = tagged_history(git_sandbox, 3, {"v0.3.0": (1, None), "v0.2.0": (2, None)})
    _fails(git, tmp_path, r"version inversion: baseline v0\.2\.0 is lower than the earlier release v0\.3\.0")
    assert _calls(history) == ["tag_records", "independent_commits"]


@pytest.mark.parametrize(("declared", "target", "named"), [
    ({"0.13.0": (2, None), "v0.13.0": (3, None)}, None, r"conflicting tags 0\.13\.0 and v0\.13\.0: version 0\.13\.0 is tagged on commits c2 and c3"),
    ({"1.0.0": (1, None), "v1.0.0": (3, None)}, "v1.0.0", r"conflicting tags 1\.0\.0 and v1\.0\.0: version 1\.0\.0 is tagged on commits c1 and c3"),
    ({"v1.0.0": (2, None), "v1.1.0": (2, None)}, "v1.1.0", r"conflicting tags v1\.0\.0 and v1\.1\.0: commit c2 carries versions 1\.0\.0 and 1\.1\.0"),
])
def test_conflicting_tags_fail_before_anything_is_excluded(git_sandbox: GitSandbox, tmp_path: Path, declared: dict[str, tuple[int, str | None]],
                                                           target: str | None, named: str) -> None:
    """The conflict check sees the target's own tags too, so A never becomes the predecessor of B."""
    git, history = tagged_history(git_sandbox, 4, declared)
    _fails(git, tmp_path, named, target)
    assert _calls(history) == ["tag_records"]


def test_an_ambiguous_tag_after_the_baseline_fails(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """An ambiguous engine tag between the baseline and HEAD stops the selection, naming it."""
    git, history = tagged_history(git_sandbox, 4, {"v0.13.0": (1, None), "v0.14.0": (3, _AMBIGUOUS)})
    _fails(git, tmp_path, r"ambiguous release v0\.14\.0 between v0\.13\.0 and HEAD; correct its annotation")
    assert _calls(history) == ["tag_records", "tag_names"]


@pytest.mark.parametrize(("target", "named"), [
    ("v0.13", r"'v0\.13' is not a stable release tag name"),
    ("v0.14.0-SNAPSHOT", r"'v0\.14\.0-SNAPSHOT' is not a stable release tag name"),
    ("v0.14.0-rc1", r"'v0\.14\.0-rc1' is not a stable release tag name"),
])
def test_targets_that_are_not_stable_names_start_no_git_call(git_sandbox: GitSandbox, tmp_path: Path, target: str, named: str) -> None:
    """Malformed names, snapshot markers and other prereleases fail before any query."""
    git, history = tagged_history(git_sandbox, 2, {})
    _fails(git, tmp_path, named, target)
    assert history.calls == []


def test_a_missing_tag_target_is_status_2_from_the_records_call(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A syntactically valid tag that does not exist fails through `GitRevisionNotFoundError`."""
    git, history = tagged_history(git_sandbox, 2, {"v0.1.0": (1, None)})
    error = _fails(git, tmp_path, r"tag v9\.9\.9 does not exist", "v9.9.9")
    assert isinstance(error.__cause__, GitRevisionNotFoundError)
    assert _calls(history) == ["tag_records"]


def test_a_git_failure_of_the_records_call_is_status_1(git_sandbox: GitSandbox, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A canned execution failure stays a Git command error, which carries no preflight status; it is the only call."""
    git, history = tagged_history(git_sandbox, 2, {"v0.1.0": (1, None)})

    def failing(self: RepositoryObservations, *, cwd: Path, merged: str | None = None) -> tuple[()]:
        del cwd
        self.facts.history.calls.append(("tag_records", *(() if merged is None else (merged,))))
        raise GitCommandError(subprocess.CompletedProcess(["for-each-ref"], 128, "", "fatal: broken repository\n"))

    monkeypatch.setattr(RepositoryObservations, "tag_records", failing)
    with pytest.raises(GitCommandError) as caught:
        tags.select_range(git, cwd=tmp_path)
    assert getattr(caught.value, "exit_code", _EXECUTION) == _EXECUTION
    assert history.calls == [("tag_records", "HEAD")]


def test_an_oversized_tips_query_is_status_1_before_it_starts(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """Six hundred candidates of 64-character ids exceed the Windows command line; only the records call ran."""
    git = git_sandbox.context()
    history = git.facts.history
    commits: list[str] = []
    for index in range(600):
        commits.append(history.commit(f"{index:064x}", *commits[-1:]))
        history.tag(f"v0.{index // 100}.{index % 100}", commits[-1])
    history.head = history.main = commits[-1]
    with pytest.raises(GitCommandLineTooLongError, match=r"for 600 candidate commits") as caught:
        tags.select_range(git, cwd=tmp_path, target=None)
    assert caught.value.exit_code == _EXECUTION
    assert _calls(history) == ["tag_records"]


@pytest.mark.parametrize(("second", "warning"), [
    ((("0.13.0", None), ("v0.13.0", _UNVALIDATED)), "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    ((("v0.13.0", _VALID), ("0.13.0", _UNVALIDATED)), "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
    ((("v0.13.0", _UNVALIDATED), ("0.13.0", _UNVALIDATED)), "excluded unvalidated engine release 0.13.0 and v0.13.0 between v0.12.0 and HEAD"),
])
def test_an_ineligible_aliased_boundary_falls_back_with_a_warning(git_sandbox: GitSandbox, tmp_path: Path,
                                                                  second: tuple[tuple[str, str | None], ...], warning: str) -> None:
    """One unvalidated alias makes the whole release ineligible; the warning names both aliases."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), **{name: (2, text) for name, text in second}})
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.12.0", "v0.12.0..HEAD", 2, (warning,))
    assert _calls(history) == _ONE


@pytest.mark.parametrize("second", [(("v0.13.0", _VALID), ("0.13.0", _AMBIGUOUS)), (("v0.13.0", _AMBIGUOUS), ("0.13.0", _AMBIGUOUS))])
def test_an_ambiguous_aliased_boundary_after_the_baseline_fails(git_sandbox: GitSandbox, tmp_path: Path,
                                                                second: tuple[tuple[str, str | None], ...]) -> None:
    """One ambiguous alias makes the whole release ambiguous; the failure names both aliases."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), **{name: (2, text) for name, text in second}})
    _fails(git, tmp_path, r"ambiguous release 0\.13\.0 and v0\.13\.0 between v0\.12\.0 and HEAD")
    assert history.calls == [("tag_records", "HEAD"), ("tag_names", "HEAD", "refs/tags/v0.12.0")]


def test_an_eligible_aliased_baseline_is_named_by_its_v_alias(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """Historical `0.13.0` with validated `v0.13.0`: baseline and left endpoint `v0.13.0`."""
    git, history = tagged_history(git_sandbox, 3, {"0.13.0": (2, None), "v0.13.0": (2, _VALID)})
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.13.0", "v0.13.0..HEAD", 1, ())
    assert history.calls == _selection_calls("HEAD", ["c2"], "v0.13.0")


@pytest.mark.parametrize("target", ["0.13.0", "v0.13.0"])
def test_a_tag_target_through_either_alias_of_an_ineligible_boundary_fails(git_sandbox: GitSandbox, tmp_path: Path, target: str) -> None:
    """The boundary decides, even when the named alias alone would be eligible."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), "0.13.0": (2, None), "v0.13.0": (2, _UNVALIDATED)})
    _fails(git, tmp_path, r"tag .*0\.13\.0 cannot be a range target: its release 0\.13\.0 and v0\.13\.0 is not eligible", target)
    assert _calls(history) == ["tag_records"]


def test_an_ambiguous_target_boundary_fails(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A tag target whose release is ambiguous fails naming its aliases."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), "v0.13.0": (2, _AMBIGUOUS)})
    _fails(git, tmp_path, r"tag v0\.13\.0 cannot be a range target: its release v0\.13\.0 is ambiguous", "v0.13.0")
    assert history.calls == [("tag_records", "refs/tags/v0.13.0")]


@pytest.mark.parametrize(("target", "expected"), [
    (None, RangeSelection("HEAD", "v0.14.0", "v0.14.0..HEAD", 0, ())),
    ("0.14.0", RangeSelection("0.14.0", "v0.13.0", "v0.13.0..0.14.0", 1, ())),
    ("v0.14.0", RangeSelection("v0.14.0", "v0.13.0", "v0.13.0..v0.14.0", 1, ())),
])
def test_an_eligible_aliased_boundary_on_head(git_sandbox: GitSandbox, tmp_path: Path, target: str | None, expected: RangeSelection) -> None:
    """HEAD keeps the boundary as candidate; a tag target through either alias removes both."""
    git, history = tagged_history(git_sandbox, 3, {"v0.13.0": (2, None), "0.14.0": (3, None), "v0.14.0": (3, _VALID)})
    assert tags.select_range(git, cwd=tmp_path, target=target) == expected
    assert _calls(history) == (_SEVERAL if target is None else _ONE)


@pytest.mark.parametrize(("declared", "version"), [
    ({"v0.13.0": (2, _UNVALIDATED)}, "0.13.0"),
    ({"0.13.0": (2, _AMBIGUOUS)}, "0.13.0"),
    ({"v0.13.0": (2, None)}, "0.13.0"),
])
def test_a_tagged_version_is_reserved_in_either_spelling(git_sandbox: GitSandbox, tmp_path: Path, declared: dict[str, tuple[int, str | None]],
                                                         version: str) -> None:
    """Any stable tag naming the version reserves it, whatever its eligibility."""
    git, history = tagged_history(git_sandbox, 3, declared)
    with pytest.raises(RangeError, match=rf"version {version} is reserved: tag .*0\.13\.0 already names it") as caught:
        tags.check_release_version(git, cwd=tmp_path, version=version)
    assert caught.value.exit_code == _PREFLIGHT
    assert history.calls == [("tag_records",), ("tag_records", "main")]


@pytest.mark.parametrize(("version", "accepted"), [("0.10.0", True), ("0.9.1", True), ("0.8.9", False), ("0.15.0", True)])
def test_a_target_must_be_higher_than_every_eligible_release_on_main(git_sandbox: GitSandbox, tmp_path: Path, version: str, *,
                                                                    accepted: bool) -> None:
    """Numeric comparison against the highest eligible boundary on `main` (`0.10.0` beats `v0.9.0`); unmerged tags do not bound."""
    git = git_sandbox.context()
    history = git.facts.history
    history.commit("c1")
    history.commit("c2", "c1")
    history.head = history.main = history.commit("c3", "c2")
    history.commit("s1", "c3")
    history.tag("v0.8.0", "c1")
    history.tag("v0.9.0", "c2", _VALID)
    history.tag("v0.20.0", "s1")
    if accepted:
        tags.check_release_version(git, cwd=tmp_path, version=version)
    else:
        with pytest.raises(RangeError, match=rf"version {version} is not higher than release v0\.9\.0, reachable from main"):
            tags.check_release_version(git, cwd=tmp_path, version=version)
    assert _calls(history) == ["tag_records", "tag_records"]


def test_the_bound_uses_boundary_classes(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """`0.12.5` passes after `v0.12.0` when the later release is ineligible; `0.13.0` stays reserved."""
    git, history = tagged_history(git_sandbox, 3, {"v0.12.0": (1, None), "0.13.0": (2, None), "v0.13.0": (2, _UNVALIDATED)})
    tags.check_release_version(git, cwd=tmp_path, version="0.12.5")
    assert _take(history) == [("tag_records",), ("tag_records", "main")]
    with pytest.raises(RangeError, match=r"version 0\.13\.0 is reserved"):
        tags.check_release_version(git, cwd=tmp_path, version="0.13.0")
    assert _take(history) == [("tag_records",), ("tag_records", "main")]


def test_without_an_eligible_release_any_target_passes(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """Only unvalidated releases on `main`: nothing bounds the target."""
    git, history = tagged_history(git_sandbox, 3, {"v0.13.0": (2, _UNVALIDATED)})
    tags.check_release_version(git, cwd=tmp_path, version="0.0.1")
    assert history.calls == [("tag_records",), ("tag_records", "main")]


@pytest.mark.parametrize(("version", "error", "named"), [
    ("0.13", VersionError, r"Invalid version '0\.13'"),
    ("0.14.0-SNAPSHOT", RangeError, r"0\.14\.0-SNAPSHOT is not a release version"),
])
def test_an_unusable_version_fails_before_any_call(git_sandbox: GitSandbox, tmp_path: Path, version: str, error: type[ValueError], named: str) -> None:
    """The release-version rule checks a well-formed release token first."""
    git, history = tagged_history(git_sandbox, 1, {})
    with pytest.raises(error, match=named):
        tags.check_release_version(git, cwd=tmp_path, version=version)
    assert history.calls == []


def test_twelve_validated_releases(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """llm-shared's shape: annotated `vX.Y.Z` tags ending with `[valid]`, no trailer."""
    declared = {f"v0.{minor}.0": (minor - 1, annotation(f"0.{minor}.0 -- Release", valid=True)) for minor in range(2, 14)}
    git, history = tagged_history(git_sandbox, 14, declared)
    commits = [f"c{position}" for position in range(1, 13)]
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.13.0", "v0.13.0..HEAD", 2, ())
    assert _take(history) == _selection_calls("HEAD", commits, "v0.13.0")
    assert tags.select_range(git, cwd=tmp_path, target="v0.13.0").range == "v0.12.0..v0.13.0"
    assert _take(history) == _selection_calls("refs/tags/v0.13.0", commits[:-1], "v0.12.0")


def test_ninety_nine_mixed_tags_with_one_snapshot(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A long history of annotated and lightweight tags; the snapshot marker is never a release."""
    declared: dict[str, tuple[int, str | None]] = {}
    for position in range(1, 100):
        name = f"v0.{position // 10}.{position % 10}" + ("-SNAPSHOT" if position == 50 else "")  # noqa: PLR2004
        declared[name] = (position, None if position % 7 == 0 else annotation(valid=position % 3 != 0))
    git, history = tagged_history(git_sandbox, 99, declared)
    stable = [f"c{position}" for position in range(1, 100) if position != 50]  # noqa: PLR2004 - c50 holds the snapshot
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.9.9", "v0.9.9..HEAD", 0, ())
    assert _take(history) == _selection_calls("HEAD", stable, "v0.9.9")
    assert tags.select_range(git, cwd=tmp_path, target="v0.5.1") == RangeSelection("v0.5.1", "v0.4.9", "v0.4.9..v0.5.1", 2, ())
    assert _take(history) == _selection_calls("refs/tags/v0.5.1", stable[:49], "v0.4.9")


def test_the_mixed_spelling_chain(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """workspace-halo's shape: `v0.0.20`, `0.0.21`, `0.0.22`, `v0.0.23`, `v0.0.24` on HEAD."""
    declared = {name: (position, annotation()) for position, name in enumerate(["v0.0.20", "0.0.21", "0.0.22", "v0.0.23", "v0.0.24"], 1)}
    git, history = tagged_history(git_sandbox, 5, declared)
    commits = ["c1", "c2", "c3", "c4", "c5"]
    assert tags.select_range(git, cwd=tmp_path) == RangeSelection("HEAD", "v0.0.24", "v0.0.24..HEAD", 0, ())
    assert _take(history) == _selection_calls("HEAD", commits, "v0.0.24")
    assert tags.select_range(git, cwd=tmp_path, target="v0.0.24") == RangeSelection("v0.0.24", "v0.0.23", "v0.0.23..v0.0.24", 1, ())
    assert _take(history) == _selection_calls("refs/tags/v0.0.24", commits[:4], "v0.0.23")
    assert tags.select_range(git, cwd=tmp_path, target="v0.0.23").baseline == "0.0.22"
    assert _take(history) == _selection_calls("refs/tags/v0.0.23", commits[:3], "0.0.22")


# eof
