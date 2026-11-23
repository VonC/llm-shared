"""Both candidates run on the same frozen inputs in a temporary worktree; only digests, statuses and differing hunks are kept.

Step 6 of v0.14.0 git-cliff-provisioning (design "Frozen inputs and the
coverage matrix" and "Outputs and classification"; design decisions Q13 and
Q15; requirement clarification Q13). No process: Git is a recording
`subprocess.run` behind a real `GitExecutionContext`, and git-cliff runs go
through real invocation objects over a scripted launcher.

- The ranges are the full history, each consecutive `vA..vB` of the tags
  reachable from the revision in history order (one pass, no sort), and
  `<last tag>..HEAD`.
- Both candidates receive the same working directory, range, `cliff.toml`
  copy, flags (`-c <copy> -w <worktree> -s footer`) and environment
  (`SystemRoot`, `TEMP`, `TMP`, `HOME` and `USERPROFILE` on an empty
  directory, no `GIT_*`), under the engine policy and a bounded run.
- Identical outputs keep only their digest and status; a differing range
  keeps its hunks with three lines of context.
- The temporary worktree is added at the frozen commit without hooks, then
  removed and pruned on success and on failure.
- Code review round 1: the cleanup removes the registered worktree through
  Git, deletes what is left, prunes and verifies through the listing; a
  partial creation is cleaned up and keeps its own failure; a cleanup problem
  fails a successful comparison, or is noted on a failure already raised.
- A rerun whose digest or status differs from the recorded one fails.
"""

from __future__ import annotations

import dataclasses
import errno
import hashlib
import shutil
from types import SimpleNamespace
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    COMMIT,
    PIN,
    SAME_OUTPUT,
    CliffRuns,
    FakeGit,
    GitCall,
    git_context,
    sample_inputs,
    tag_listing,
)
from tools.release_workflow.git import GitCommandError
from tools.release_workflow.git_cliff import comparison
from tools.release_workflow.git_cliff.comparison import (
    ENVIRONMENT,
    FLAGS,
    RUN_SECONDS,
    CaseResult,
    ComparisonError,
    ComparisonResult,
    RangeCase,
    RunDigest,
    Workspace,
    differing_hunks,
    history_ranges,
    history_tags,
    run_comparison,
    run_environment,
    verify_rerun,
)

if TYPE_CHECKING:
    from pathlib import Path

    from tools.release_workflow.git import GitExecutionContext

_COMMITS = [f"{index:040x}" for index in range(1, 7)]
_SOURCE = {"SystemRoot": "C:\\Windows", "temp": "C:\\Temp", "TMP": "C:\\Tmp", "PATH": "C:\\bin", "GIT_DIR": "C:\\repo"}
_FIXTURE_CASE = "fixture v0.1.0..v0.2.0-SNAPSHOT"
_INPUTS = dataclasses.replace(sample_inputs(), ranges=(RangeCase("llm-shared"), RangeCase("fixture", "v0.1.0..v0.2.0-SNAPSHOT")))


def _ranges(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tags: list[tuple[str, str]]) -> tuple[FakeGit, tuple[RangeCase, ...]]:
    """Compute the ranges of a history of six commits with the given tags."""
    fake = FakeGit({"rev-list": "".join(f"{commit}\n" for commit in _COMMITS).encode(), "for-each-ref": tag_listing(tags)})
    git = git_context(tmp_path, monkeypatch, fake)
    return fake, history_ranges(git, cwd=tmp_path, revision=COMMIT, repository="llm-shared")


def test_the_ranges_are_the_full_history_each_consecutive_pair_and_the_last_tag_to_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Tags are ordered by their commit's place in history, whatever order Git lists them in."""
    tags = [("v0.2.0", _COMMITS[3]), ("v0.1.0", _COMMITS[1]), ("v0.2.0-SNAPSHOT", _COMMITS[2])]
    fake, ranges = _ranges(tmp_path, monkeypatch, tags)
    assert ranges == (
        RangeCase("llm-shared"), RangeCase("llm-shared", "v0.1.0..v0.2.0-SNAPSHOT"),
        RangeCase("llm-shared", "v0.2.0-SNAPSHOT..v0.2.0"), RangeCase("llm-shared", "v0.2.0..HEAD"),
    )
    rev_list, for_each_ref = fake.calls
    assert rev_list.arguments[-3:] == ["--topo-order", "--reverse", COMMIT]
    assert f"--merged={COMMIT}" in for_each_ref.arguments
    git = git_context(tmp_path, monkeypatch, fake)
    assert history_tags(git, cwd=tmp_path, revision=COMMIT) == (
        ("v0.1.0", _COMMITS[1]), ("v0.2.0-SNAPSHOT", _COMMITS[2]), ("v0.2.0", _COMMITS[3]))


def test_tags_on_one_commit_are_ordered_by_name_and_no_tag_gives_the_full_history_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Two tags of the same commit keep the order of Git's listing, by name; a history without tags has one case."""
    _fake, ranges = _ranges(tmp_path, monkeypatch, [("v1.0.0", _COMMITS[4]), ("v1.0.0-SNAPSHOT", _COMMITS[4])])
    assert [case.range for case in ranges] == [None, "v1.0.0..v1.0.0-SNAPSHOT", "v1.0.0-SNAPSHOT..HEAD"]
    _fake, ranges = _ranges(tmp_path, monkeypatch, [])
    assert ranges == (RangeCase("llm-shared"),)


def test_a_tag_outside_the_listed_history_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A reachable tag whose commit Git did not list cannot be placed."""
    with pytest.raises(ComparisonError, match=r"v9\.9\.9"):
        _ranges(tmp_path, monkeypatch, [("v9.9.9", "f" * 40)])


def test_the_run_environment_keeps_three_system_names_and_points_home_at_an_empty_directory(tmp_path: Path) -> None:
    """`SystemRoot`, `TEMP` and `TMP` whatever their case, `HOME` and `USERPROFILE` on the empty home, nothing else."""
    home = tmp_path / "home"
    assert run_environment(_SOURCE, home) == {
        "SystemRoot": "C:\\Windows", "TEMP": "C:\\Temp", "TMP": "C:\\Tmp", "HOME": str(home), "USERPROFILE": str(home)}
    assert tuple(sorted(run_environment(_SOURCE, home))) == ENVIRONMENT


def test_a_run_environment_without_a_system_name_fails(tmp_path: Path) -> None:
    """A missing `SystemRoot` is named instead of starting git-cliff without it."""
    with pytest.raises(ComparisonError, match="SystemRoot"):
        run_environment({"TEMP": "C:\\Temp", "TMP": "C:\\Tmp"}, tmp_path)


class _Scene:
    """One comparison: a checkout, a run directory with its fixture and empty home, and the recording Git."""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lay out the directories and bind Git; `worktree add` creates the worktree as Git would."""
        self.checkout, self.temporary = tmp_path / "checkout", tmp_path / "run"
        for directory in (self.checkout, self.temporary / "fixture", self.temporary / "home"):
            directory.mkdir(parents=True)
        self.fake = FakeGit({"worktree": self._worktree})
        self.git: GitExecutionContext = git_context(tmp_path, monkeypatch, self.fake)
        self.workspace = Workspace(checkout=self.checkout, temporary=self.temporary, cliff_toml=tmp_path / "bundle" / "cliff.toml",
                                   fixture=self.temporary / "fixture", environment=run_environment(_SOURCE, self.temporary / "home"))
        self.runs = CliffRuns()

        self.registered = False

    def _worktree(self, call: GitCall) -> bytes:
        """Play `worktree add`, `remove`, `prune` and `list` over one registration, as Git would, honoring declared failures."""
        worktree, failed = self.temporary / "worktree", call.action in self.fake.failures
        if call.action == "worktree add":
            worktree.mkdir()
            (worktree / "README.md").write_bytes(b"checked out\n")
            self.registered = not failed
        elif call.action == "worktree remove" and not failed and worktree.exists():
            shutil.rmtree(worktree)
            self.registered = False
        elif call.action == "worktree prune" and not failed and not worktree.exists():
            self.registered = False
        elif call.action == "worktree list":
            listed = f"worktree {worktree.as_posix()}\nHEAD {COMMIT}\ndetached\n\n" if self.registered else ""
            return f"worktree {self.checkout.as_posix()}\nHEAD {COMMIT}\n\n{listed}".encode()
        return b""

    def compare(self) -> ComparisonResult:
        """Run both candidates on two cases of the sample inputs."""
        return run_comparison(_INPUTS, self.runs.invocations(BASELINE, PIN), self.git, self.workspace)


@pytest.fixture
def scene(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Scene:
    """Give each case its own directories, Git and runs."""
    return _Scene(tmp_path, monkeypatch)


def test_both_candidates_receive_the_same_directory_range_copy_flags_and_environment(scene: _Scene) -> None:
    """Per case, the baseline then the pin run with identical requests but for the executable."""
    scene.compare()
    worktree, fixture = scene.temporary / "worktree", scene.workspace.fixture
    requests = scene.runs.requests
    assert [request.executable.parent.name for request in requests] == [BASELINE, PIN, BASELINE, PIN]
    cliff = str(scene.workspace.cliff_toml)
    expected = [
        (worktree, ("-c", cliff, "-w", str(worktree), "-s", "footer", "--")),
        (fixture, ("-c", cliff, "-w", str(fixture), "-s", "footer", "--", "v0.1.0..v0.2.0-SNAPSHOT")),
    ]
    for index, (cwd, arguments) in enumerate(expected):
        for request in requests[2 * index:2 * index + 2]:
            assert (request.cwd, request.arguments, request.stdin, request.output, request.deadline) == (cwd, arguments, "closed", "capture", RUN_SECONDS)
            assert request.environment == scene.workspace.environment
    home = scene.temporary / "home"
    assert {name for request in requests for name in request.environment or {}} == set(ENVIRONMENT)
    assert {request.environment["HOME"] for request in requests if request.environment} == {str(home)}
    assert list(home.iterdir()) == []
    assert FLAGS == ("-c", "<cliff.toml>", "-w", "<worktree>", "-s", "footer")


def test_identical_outputs_keep_only_their_digest_and_status(scene: _Scene) -> None:
    """No hunk is stored for a case whose outputs are the same."""
    result = scene.compare()
    same = RunDigest(hashlib.sha256(SAME_OUTPUT).hexdigest(), 0)
    assert result.cases[0] == CaseResult(RangeCase("llm-shared"), ((BASELINE, same), (PIN, same)), ())


def test_a_differing_range_keeps_its_hunks_with_three_lines_of_context(scene: _Scene) -> None:
    """The baseline output, then the pin's, give the hunk; statuses are kept per version."""
    before = b"".join(f"line {number}\n".encode() for number in range(1, 21))
    after = before.replace(b"line 10\n", b"line ten\n")
    scene.runs.outputs = {(BASELINE, _FIXTURE_CASE): (0, before), (PIN, _FIXTURE_CASE): (1, after)}
    case = scene.compare().cases[1]
    assert case.results == ((BASELINE, RunDigest(hashlib.sha256(before).hexdigest(), 0)), (PIN, RunDigest(hashlib.sha256(after).hexdigest(), 1)))
    assert case.hunks == ("@@ -7,7 +7,7 @@\n line 7\n line 8\n line 9\n-line 10\n+line ten\n line 11\n line 12\n line 13",)
    assert case.hunk_ids == (f"{_FIXTURE_CASE} #1",)


def test_distant_changes_give_one_hunk_each() -> None:
    """Two changes more than six lines apart are two hunks."""
    before = [f"line {number}" for number in range(1, 31)]
    after = [*before[:2], "changed 3", *before[3:25], "changed 26", *before[26:]]
    hunks = differing_hunks("\n".join(before).encode(), "\n".join(after).encode())
    assert [hunk.splitlines()[0] for hunk in hunks] == ["@@ -1,6 +1,6 @@", "@@ -23,7 +23,7 @@"]


def test_line_endings_and_a_missing_last_line_feed_are_differences_that_show() -> None:
    """A carriage return stays visible; a last line without a line feed is marked as `diff` marks it."""
    assert differing_hunks(b"a\nb\n", b"a\r\nb\n") == ("@@ -1,2 +1,2 @@\n-a\n+a\r\n b",)
    marker = "\\ No newline at end of file"
    assert differing_hunks(b"a\nb", b"a\nc") == (f"@@ -1,2 +1,2 @@\n a\n-b\n{marker}\n+c\n{marker}",)


def test_the_worktree_is_added_at_the_frozen_commit_without_hooks_then_removed_pruned_and_verified(scene: _Scene) -> None:
    """`worktree add --detach` with an empty hooks directory; then `remove --force`, `prune` and a listing without it."""
    scene.compare()
    worktree = scene.temporary / "worktree"
    add, remove, prune, listing = scene.fake.of("worktree")
    assert add.arguments[-5:] == ["worktree", "add", "--detach", str(worktree), COMMIT]
    assert f"core.hooksPath={scene.temporary / 'hooks'}" in add.arguments
    assert list((scene.temporary / "hooks").iterdir()) == []
    assert (remove.arguments[-4:], prune.arguments[-2:], listing.arguments[-3:]) == (
        ["worktree", "remove", "--force", str(worktree)], ["worktree", "prune"], ["worktree", "list", "--porcelain"])
    assert {call.cwd for call in (add, remove, prune, listing)} == {scene.checkout}
    assert (worktree.exists(), scene.registered) == (False, False)


def test_a_run_that_does_not_end_fails_and_the_worktree_is_still_removed_and_verified(scene: _Scene) -> None:
    """A git-cliff run past its bound names the version and case; cleanup still happens and adds nothing to the failure."""
    scene.runs.hang = {PIN}
    with pytest.raises(ComparisonError, match=rf"git-cliff {PIN} did not end within {RUN_SECONDS} s .*llm-shared full history") as raised:
        scene.compare()
    assert [call.action for call in scene.fake.of("worktree")][1:] == ["worktree remove", "worktree prune", "worktree list"]
    assert not (scene.temporary / "worktree").exists()
    assert getattr(raised.value, "__notes__", []) == []


def test_a_partial_creation_is_cleaned_up_and_keeps_its_own_failure(scene: _Scene) -> None:
    """Code review round 1: `worktree add` failed after creating its directory; the directory goes and its error stays."""
    scene.fake.failures["worktree add"] = (128, b"fatal: could not create work tree dir")
    with pytest.raises(GitCommandError, match="could not create work tree"):
        scene.compare()
    assert [call.action for call in scene.fake.of("worktree")] == ["worktree add", "worktree remove", "worktree prune", "worktree list"]
    assert (scene.temporary / "worktree").exists() is False
    assert scene.runs.requests == []


def _refuse(path: object, **_options: object) -> None:
    """Refuse a removal, as Windows does for a file still open elsewhere."""
    raise PermissionError(errno.EACCES, "Access is denied", str(path))


def test_a_worktree_that_cannot_be_removed_fails_a_successful_comparison(scene: _Scene, monkeypatch: pytest.MonkeyPatch) -> None:
    """A refused `worktree remove` and a refused deletion leave it registered: the comparison fails, naming both."""
    scene.fake.failures["worktree remove"] = (1, b"error: failed to delete: Permission denied")
    monkeypatch.setattr(comparison, "shutil", SimpleNamespace(rmtree=_refuse))
    with pytest.raises(ComparisonError) as raised:
        scene.compare()
    message = str(raised.value)
    assert "could not be deleted: [Errno 13] Access is denied" in message
    assert f"may still be registered in {scene.checkout}" in message
    assert "failed to delete: Permission denied" in message


def test_a_cleanup_problem_after_a_failed_run_is_noted_on_the_run_failure(scene: _Scene, monkeypatch: pytest.MonkeyPatch) -> None:
    """The run's own failure propagates; the cleanup problems ride on it as a note."""
    scene.runs.hang = {PIN}
    scene.fake.failures.update({"worktree remove": (1, b"error: Permission denied"), "worktree prune": (1, b"error: prune refused")})
    monkeypatch.setattr(comparison, "shutil", SimpleNamespace(rmtree=_refuse))
    with pytest.raises(ComparisonError, match="did not end") as raised:
        scene.compare()
    notes = " ".join(raised.value.__notes__)
    assert "`git worktree prune` exited 1: error: prune refused" in notes
    assert "may still be registered" in notes


def test_a_git_failure_during_cleanup_is_reported(scene: _Scene) -> None:
    """A Git that cannot even list the worktrees is a cleanup problem of its own."""
    played = scene.fake.answers["worktree"]
    assert not isinstance(played, bytes)

    def broken(call: GitCall) -> bytes:
        if call.action == "worktree list":
            msg = "the executable is gone"
            raise OSError(msg)
        return played(call)

    scene.fake.answers["worktree"] = broken
    with pytest.raises(ComparisonError, match="could not be removed: Cannot execute selected Git"):
        scene.compare()


def test_a_rerun_with_the_recorded_digests_passes() -> None:
    """The same digests and statuses reproduce the bundle."""
    same = RunDigest("1" * 64, 0)
    recorded = ComparisonResult((CaseResult(RangeCase("llm-shared"), ((BASELINE, same), (PIN, same))),))
    verify_rerun(recorded, ComparisonResult(recorded.cases))


@pytest.mark.parametrize(("observed", "reason"), [
    pytest.param(RunDigest("2" * 64, 0), f"git-cliff {PIN} produced {'2' * 64}", id="digest"),
    pytest.param(RunDigest("1" * 64, 3), "status 3", id="status"),
])
def test_a_rerun_digest_or_status_different_from_the_bundle_fails(observed: RunDigest, reason: str) -> None:
    """The case, the version and both observations are named."""
    same = RunDigest("1" * 64, 0)
    recorded = ComparisonResult((CaseResult(RangeCase("llm-shared"), ((BASELINE, same), (PIN, same))),))
    rerun = ComparisonResult((CaseResult(RangeCase("llm-shared"), ((BASELINE, same), (PIN, observed))),))
    with pytest.raises(ComparisonError, match=reason) as raised:
        verify_rerun(recorded, rerun)
    assert "llm-shared full history" in str(raised.value)


def test_a_rerun_over_other_cases_fails() -> None:
    """A rerun must cover exactly the recorded cases."""
    same = RunDigest("1" * 64, 0)
    recorded = ComparisonResult((CaseResult(RangeCase("llm-shared"), ((BASELINE, same), (PIN, same))),))
    with pytest.raises(ComparisonError, match="cases"):
        verify_rerun(recorded, ComparisonResult(()))


# eof
