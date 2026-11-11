"""Typed Git release observations: exact arguments, parsing and the tips guard.

Step 1 of v0.14.0 version-sources. Each observation is checked against canned
``run`` output, with no Git process: tag records with their peeled commit and
own annotation (a tag of a tag included: Git 2.44, the floor, peels it
fully, also when the inner ref was deleted), independent tips, tag names
between two revisions, a commit count and the candidate listing. A reachability filter naming no object
becomes ``GitRevisionNotFoundError`` from the one call (plan decision Q13 keeps
the selection at four calls), and the tips query refuses, before any call, a
command line longer than Windows accepts. The release history simulation
answers the same observations by reachability over declared parents.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tools.release_workflow.git import (
    GitCommandError,
    GitCommandLineTooLongError,
    GitExecutionContext,
    GitRevisionNotFoundError,
    TagRecord,
)
from tools.release_workflow.git_environment import (
    GitPolicyError,
    controlled_environment,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tests.unit.tools.release_workflow.repository_simulation import (
        GitSandbox,
        ReleaseHistory,
        RepositoryObservations,
    )

_FORMAT = "--format=%(refname:strip=2)%00%(objecttype)%00%(objectname)%00%(*objecttype)%00%(*objectname)%00%(contents)%00"
_OPTIONS = "--no-pager --literal-pathspecs -c color.ui=false -c core.quotepath=false merge-base --independent"
_LIMIT = 32_767
_USAGE = 129
_FATAL = 128
_PREFLIGHT = 2
_EXECUTION = 1
_TAG, _COMMIT, _OTHER, _INNER = "1" * 40, "2" * 40, "3" * 64, "4" * 40


@dataclass
class CannedRun:
    """Record each call's domain arguments and answer with canned output."""

    stdout: str = ""
    returncode: int = 0
    stderr: str = ""
    calls: list[tuple[tuple[str, ...], bool]] = field(default_factory=list[tuple[tuple[str, ...], bool]])

    def __call__(self, arguments: Sequence[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
        """Behave like ``run``: a checked nonzero status raises the command error."""
        del cwd
        self.calls.append((tuple(arguments), check))
        result = subprocess.CompletedProcess(list(arguments), self.returncode, self.stdout, self.stderr)
        if check and self.returncode:
            raise GitCommandError(result)
        return result


@pytest.fixture
def canned(monkeypatch: pytest.MonkeyPatch) -> CannedRun:
    """Replace the trusted command boundary; no process can start."""
    run = CannedRun()
    monkeypatch.setattr(GitExecutionContext, "run", run)
    return run


def _context(executable: str = "C:\\Git\\cmd\\git.exe") -> GitExecutionContext:
    """Build a selected context without executable discovery or a version probe."""
    environment = controlled_environment({"PATH": "C:\\Git\\cmd"}, non_interactive=True)
    return GitExecutionContext(Path(executable), (2, 45, 0), environment, Path("C:\\"), non_interactive=True)


def _record(*fields: str) -> str:
    """Render one ``for-each-ref`` record: NUL-terminated fields, then a newline."""
    return "\0".join(fields) + "\0\n"


@pytest.mark.parametrize(("merged", "selected"), [(None, ()), ("refs/tags/v0.14.0", ("--merged=refs/tags/v0.14.0",))])
def test_tag_records_arguments(merged: str | None, selected: tuple[str, ...], canned: CannedRun, tmp_path: Path) -> None:
    """One call lists every tag ref, optionally only those reachable from a revision."""
    assert _context().tag_records(cwd=tmp_path, merged=merged) == ()
    assert canned.calls == [(("for-each-ref", _FORMAT, *selected, "refs/tags"), False)]


def test_tag_records_parse_one_annotated_tag(canned: CannedRun, tmp_path: Path) -> None:
    """An annotation keeps its blank lines and trailing newline; the commit is peeled."""
    annotation = "Release 0.13.0\n\nKey changes\n\nRelease tooling: llm-shared v0.13.0-4-gabc1234\n[valid]\n"
    canned.stdout = _record("v0.13.0", "tag", _TAG, "commit", _COMMIT, annotation)
    assert _context().tag_records(cwd=tmp_path) == (TagRecord("v0.13.0", "tag", _COMMIT, annotation),)


def test_tag_records_parse_several_tags(canned: CannedRun, tmp_path: Path) -> None:
    """A lightweight tag has no annotation, even though Git prints its commit message."""
    canned.stdout = (_record("v0.13.0", "tag", _TAG, "commit", _COMMIT, "Release\n")
                     + _record("0.12.0", "commit", _OTHER, "", "", "commit subject\n")
                     + _record("v0.14.0-SNAPSHOT", "commit", _COMMIT, "", "", ""))
    assert _context().tag_records(cwd=tmp_path) == (
        TagRecord("v0.13.0", "tag", _COMMIT, "Release\n"), TagRecord("0.12.0", "commit", _OTHER, None),
        TagRecord("v0.14.0-SNAPSHOT", "commit", _COMMIT, None),
    )


@pytest.mark.parametrize("merged", [None, "HEAD"])
@pytest.mark.parametrize("inner_listed", [True, False])
def test_tag_records_peel_a_tag_of_a_tag(*, merged: str | None, inner_listed: bool, canned: CannedRun, tmp_path: Path) -> None:
    """Git 2.44 peels an outer tag to the commit, even after the inner ref is deleted."""
    inner = _record("1.0.0", "tag", _INNER, "commit", _COMMIT, "Inner release\n") if inner_listed else ""
    canned.stdout = _record("v1.0.0", "tag", _TAG, "commit", _COMMIT, "Outer release\n") + inner
    expected = (TagRecord("v1.0.0", "tag", _COMMIT, "Outer release\n"),
                *((TagRecord("1.0.0", "tag", _COMMIT, "Inner release\n"),) if inner_listed else ()))
    assert _context().tag_records(cwd=tmp_path, merged=merged) == expected
    selected = () if merged is None else (f"--merged={merged}",)
    assert canned.calls == [(("for-each-ref", _FORMAT, *selected, "refs/tags"), False)]


def test_tag_records_reject_a_one_level_dereference(canned: CannedRun, tmp_path: Path) -> None:
    """A dereferenced type `tag` means Git stopped at the inner tag: before 2.44, refused."""
    canned.stdout = _record("v1.0.0", "tag", _TAG, "tag", _INNER, "Outer release\n")
    with pytest.raises(GitPolicyError, match=r"did not peel tag v1\.0\.0 to its commit.*Git 2\.44 or later"):
        _context().tag_records(cwd=tmp_path)


@pytest.mark.parametrize("stdout", ["v0.13.0\0tag\0", _record("v0.13.0", "tag", _TAG, "commit", _COMMIT, "x").removesuffix("\n"), "unexpected\n"])
def test_tag_records_reject_malformed_output(stdout: str, canned: CannedRun, tmp_path: Path) -> None:
    """Records that are not five NUL-terminated fields are untrusted output."""
    canned.stdout = stdout
    with pytest.raises(GitPolicyError, match="tag records"):
        _context().tag_records(cwd=tmp_path)


@pytest.mark.parametrize(("merged", "status", "stderr", "missing"), [
    ("refs/tags/v9.9.9", _USAGE, "error: malformed object name refs/tags/v9.9.9\n", True),
    ("refs/tags/v9.9.9", _USAGE, "error: unknown option `merged'\n", False),
    ("refs/tags/v9.9.9", _FATAL, "fatal: malformed object name refs/tags/v9.9.9\n", False),
    (None, _USAGE, "error: malformed object name refs/tags/v9.9.9\n", False),
])
def test_tag_records_missing_revision(*, merged: str | None, status: int, stderr: str, missing: bool,  # noqa: PLR0913 - failure matrix
                                      canned: CannedRun, tmp_path: Path) -> None:
    """Only exit 129 naming the supplied filter means a missing target; the rest stays a command error."""
    canned.returncode, canned.stderr = status, stderr
    with pytest.raises(GitCommandError) as caught:
        _context().tag_records(cwd=tmp_path, merged=merged)
    assert isinstance(caught.value, GitRevisionNotFoundError) is missing
    if isinstance(caught.value, GitRevisionNotFoundError):
        assert (caught.value.revision, caught.value.exit_code) == (merged, _PREFLIGHT)
    assert len(canned.calls) == 1


def test_independent_commits(canned: CannedRun, tmp_path: Path) -> None:
    """One merge-base call returns the tips that are not ancestors of another candidate."""
    canned.stdout = f"{_COMMIT}\n{_OTHER}\n"
    assert _context().independent_commits([_TAG, _COMMIT, _OTHER], cwd=tmp_path) == (_COMMIT, _OTHER)
    assert canned.calls == [(("merge-base", "--independent", _TAG, _COMMIT, _OTHER), True)]


def _units(text: str) -> int:
    """Count UTF-16 code units: a character outside the BMP counts twice."""
    return len(text.encode("utf-16-le")) // 2


def _guard_case(id_length: int, offset: int) -> tuple[GitExecutionContext, list[str]]:
    """Build an executable and candidates whose command line is the limit plus offset."""
    count = 30_000 // (id_length + 1)
    candidates = [f"{index:0{id_length}x}" for index in range(count)]
    stem, tail = "C:\\Programs\\Git-\u00e9-\U0001f40d\\", "\\cmd\\git.exe"
    # Executable, one space, options, one space and id per candidate, then the NUL.
    fixed = 1 + len(_OPTIONS) + count * (id_length + 1) + 1
    padding = _LIMIT + offset - fixed - _units(stem) - _units(tail)
    return _context(stem + "x" * padding + tail), candidates


@pytest.mark.parametrize("id_length", [40, 64])
@pytest.mark.parametrize("offset", [-1, 0, 1])
def test_independent_commits_command_line_guard(id_length: int, offset: int, canned: CannedRun, tmp_path: Path) -> None:
    """At and below 32,767 UTF-16 units Git runs; above, nothing starts (plan decision Q13)."""
    context, candidates = _guard_case(id_length, offset)
    canned.stdout = candidates[0] + "\n"
    if offset <= 0:
        assert context.independent_commits(candidates, cwd=tmp_path) == (candidates[0],)
        assert len(canned.calls) == 1
        return
    with pytest.raises(GitCommandLineTooLongError) as caught:
        context.independent_commits(candidates, cwd=tmp_path)
    error = caught.value
    assert (error.units, error.candidates, error.exit_code) == (_LIMIT + 1, len(candidates), _EXECUTION)
    assert f"limit of {_LIMIT}" in str(error)
    assert f"{len(candidates)} candidate commits" in str(error)
    assert canned.calls == []


def test_tag_names_between_two_revisions(canned: CannedRun, tmp_path: Path) -> None:
    """One call names the tags reachable from the target and not from the baseline."""
    canned.stdout = "v0.14.0\n0.13.1\n"
    assert _context().tag_names(cwd=tmp_path, merged="HEAD", not_merged="refs/tags/v0.13.0") == ("v0.14.0", "0.13.1")
    assert canned.calls == [(("for-each-ref", "--format=%(refname:strip=2)", "--merged=HEAD",
                              "--no-merged=refs/tags/v0.13.0", "refs/tags"), True)]


def test_commit_count(canned: CannedRun, tmp_path: Path) -> None:
    """The count is asked for explicitly, never derived from describe output."""
    canned.stdout = "12\n"
    assert _context().commit_count("refs/tags/v0.13.0..HEAD", cwd=tmp_path) == 12  # noqa: PLR2004 - canned count
    assert canned.calls == [(("rev-list", "--count", "refs/tags/v0.13.0..HEAD"), True)]
    canned.stdout = "twelve\n"
    with pytest.raises(GitPolicyError, match="commit count"):
        _context().commit_count("HEAD", cwd=tmp_path)


def test_listing_drops_embedded_repositories(canned: CannedRun, tmp_path: Path) -> None:
    """An untracked nested repository is dropped; a tracked gitlink stays a name."""
    canned.stdout = "version.txt\0nested/\0vendor/module\0pkg/package.json\0"
    assert _context().listing(cwd=tmp_path) == ("version.txt", "vendor/module", "pkg/package.json")
    assert canned.calls == [(("ls-files", "-z", "--cached", "--others", "--exclude-standard"), True)]


def _history(sandbox: GitSandbox) -> tuple[RepositoryObservations, ReleaseHistory]:
    """Declare c1 <- c2 <- c3 (HEAD and main) and a side commit s1 from c1."""
    git = sandbox.context()
    history = git.facts.history
    first = history.commit("c1")
    second = history.commit("c2", first)
    side = history.commit("s1", first)
    history.head = history.main = history.commit("c3", second)
    history.tag("v0.1.0", first, "Release 0.1.0\n")
    history.tag("0.2.0", second)
    history.tag("v0.1.1", side)
    history.names = ("version.txt", "pkg/package.json")
    return git, history


def test_release_history_answers_by_reachability(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """The simulation answers the five observations from declared parents and records each call."""
    git, history = _history(git_sandbox)
    first, second, side = history.tags
    assert first == TagRecord("v0.1.0", "tag", "c1", "Release 0.1.0\n")
    assert git.tag_records(cwd=tmp_path) == (first, second, side)
    assert git.tag_records(cwd=tmp_path, merged="refs/tags/0.2.0") == (first, second)
    assert git.independent_commits(["c1", "c2", "s1"], cwd=tmp_path) == ("c2", "s1")
    assert git.tag_names(cwd=tmp_path, merged="HEAD", not_merged="refs/tags/v0.1.0") == ("0.2.0",)
    assert (git.commit_count("refs/tags/v0.1.0..main", cwd=tmp_path), git.commit_count("HEAD", cwd=tmp_path)) == (2, 3)
    assert git.listing(cwd=tmp_path) == ("version.txt", "pkg/package.json")
    assert [call[0] for call in history.calls] == [
        "tag_records", "tag_records", "independent_commits", "tag_names", "commit_count", "commit_count", "listing",
    ]


def test_release_history_nested_and_direct_tags_share_a_commit(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A tag of a tag and its inner tag name one commit, each with its own annotation."""
    git, history = _history(git_sandbox)
    inner = history.tag("1.0.0", "c3", "Inner release\n")
    outer = history.nested_tag("v1.0.0", "1.0.0", "Outer release\n")
    assert (outer.commit, outer.annotation, inner.annotation) == ("c3", "Outer release\n", "Inner release\n")
    assert git.tag_records(cwd=tmp_path, merged="HEAD")[-2:] == (inner, outer)
    assert git.tag_names(cwd=tmp_path, merged="HEAD", not_merged="refs/tags/0.2.0") == ("1.0.0", "v1.0.0")
    # Deleting only the inner ref leaves the outer tag on the same commit.
    history.tags.remove(inner)
    assert git.tag_records(cwd=tmp_path)[-1] == outer
    assert git.tag_records(cwd=tmp_path, merged="HEAD")[-1] == outer
    assert git.tag_names(cwd=tmp_path, merged="HEAD", not_merged="refs/tags/0.2.0") == ("v1.0.0",)


def test_release_history_missing_revision_and_guard(git_sandbox: GitSandbox, tmp_path: Path) -> None:
    """A missing filter fails like Git; an oversized tips query starts nothing."""
    git, history = _history(git_sandbox)
    with pytest.raises(GitRevisionNotFoundError) as caught:
        git.tag_records(cwd=tmp_path, merged="refs/tags/v9.9.9")
    assert caught.value.revision == "refs/tags/v9.9.9"
    recorded = len(history.calls)
    with pytest.raises(GitCommandLineTooLongError):
        git.independent_commits([f"{index:064x}" for index in range(600)], cwd=tmp_path)
    assert len(history.calls) == recorded


# eof
