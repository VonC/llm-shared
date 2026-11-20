"""Run two git-cliff candidates on identical frozen inputs and keep only digests, statuses and the hunks that differ.

Step 6 of v0.14.0 git-cliff-provisioning (design "Frozen inputs and the
coverage matrix" and "Outputs and classification"; design decisions Q13 and
Q15; requirement clarification Q13).

- `FrozenInputs` records everything a rerun needs: the pin and the baseline,
  llm-shared's commit, the `cliff.toml` source path, digest and dev_workflow
  submodule commit, the fixture hashes, the ranges, both candidate identities
  with their executable digests, the flags (`-c <bundle copy> -w <worktree>
  -s footer`, the form `update-changelog.sh` uses, with placeholders) and the
  names of the one explicit environment.
- `history_ranges` lists a repository's cases from Git in two calls: the full
  history, each consecutive `vA..vB` of the tags reachable from the revision,
  ordered by their commit's place in history in one pass (tags of one commit
  keep Git's name order), and `<last tag>..HEAD`.
- `run_environment` is that environment: `SystemRoot`, `TEMP` and `TMP` from
  the caller, `HOME` and `USERPROFILE` on an empty directory, nothing else, so
  no global Git configuration and no `GIT_*` reaches git-cliff.
- `run_comparison` adds a temporary worktree of the frozen commit without
  hooks, runs the baseline then the pin on every case through fresh
  invocation objects under the engine policy, each within `RUN_SECONDS`, and
  always removes and prunes the worktree. Identical outputs keep their digest
  and status only; a differing case keeps its unified-diff hunks with three
  lines of context, the one path above linear (`difflib`), run by hand only.
- `verify_rerun` fails a rerun whose digest or status differs from the
  bundle's.

Code review round 2: `FrozenInputs.llm_shared_tags` records llm-shared's
reachable tags with their commits in history order (`history_tags`), so the
bundle checks its ranges against them and a rerun against Git.

Code review round 1 of Step 6: the worktree is added inside the guarded
block, so a partial creation is cleaned up too; the cleanup removes the
registered worktree through Git, deletes what is left on disk, prunes, and
lists the worktrees to verify it is gone. A cleanup problem fails a
successful comparison, or is added as a note to the failure already raised,
which keeps propagating. `chained_ranges` is the pure rule behind
`history_ranges`, which the bundle's completeness check applies too.
"""

from __future__ import annotations

import difflib
import hashlib
import itertools
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git_cliff.invocation import Policy
from tools.release_workflow.git_environment import GitPolicyError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from tools.release_workflow.git import GitExecutionContext
    from tools.release_workflow.git_cliff.fixture_history import FixtureHashes
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation

FLAGS = ("-c", "<cliff.toml>", "-w", "<worktree>", "-s", "footer")
ENVIRONMENT = ("HOME", "SystemRoot", "TEMP", "TMP", "USERPROFILE")
REPOSITORIES = ("llm-shared", "fixture")
RUN_SECONDS = 120
_SYSTEM = ("SystemRoot", "TEMP", "TMP")
_CONTEXT_LINES = 3


class ComparisonError(ValueError):
    """The comparison cannot run on its frozen inputs, or a rerun does not reproduce the bundle."""

    exit_code = 2


@dataclass(frozen=True)
class RangeCase:
    """One case: a repository and a git-cliff range, or None for the full history."""

    repository: str
    range: str | None = None

    @property
    def key(self) -> str:
        """Name the case in messages and hunk identifiers."""
        return f"{self.repository} {self.range or 'full history'}"


@dataclass(frozen=True, kw_only=True)
class CliffToml:
    """The configuration both versions read: its source path, the SHA-256 of its bytes and the dev_workflow commit."""

    source: str
    sha256: str
    dev_workflow_commit: str


@dataclass(frozen=True, kw_only=True)
class CandidateIdentity:
    """One candidate as the bundle records it: its asset identity, its trust kind and its executable's SHA-256."""

    version: str
    asset: str
    size: int
    sha256: str
    trust: str
    executable_sha256: str


@dataclass(frozen=True, kw_only=True)
class FrozenInputs:
    """Every input of the comparison, recorded so anyone can repeat the run."""

    pin: str
    baseline: str
    llm_shared_commit: str
    llm_shared_tags: tuple[tuple[str, str], ...]
    cliff_toml: CliffToml
    fixture: FixtureHashes
    ranges: tuple[RangeCase, ...]
    candidates: tuple[CandidateIdentity, ...]
    flags: tuple[str, ...] = FLAGS
    environment: tuple[str, ...] = ENVIRONMENT


@dataclass(frozen=True)
class RunDigest:
    """What a run leaves in the bundle: the SHA-256 of its raw output and its exit status."""

    sha256: str
    status: int


@dataclass(frozen=True)
class CaseResult:
    """One case: each version's digest, the baseline's first, and the hunks when the outputs differ."""

    case: RangeCase
    results: tuple[tuple[str, RunDigest], ...]
    hunks: tuple[str, ...] = ()

    @property
    def hunk_ids(self) -> tuple[str, ...]:
        """Name each hunk for its classification: `<case> #<n>`."""
        return tuple(f"{self.case.key} #{number}" for number in range(1, len(self.hunks) + 1))


@dataclass(frozen=True)
class ComparisonResult:
    """Every case, in the order of the frozen ranges."""

    cases: tuple[CaseResult, ...]

    @property
    def hunk_ids(self) -> tuple[str, ...]:
        """Name every hunk of every case."""
        return tuple(identifier for case in self.cases for identifier in case.hunk_ids)


@dataclass(frozen=True, kw_only=True)
class Workspace:
    """Where the comparison runs: the checkout, a temporary directory, the bundle copy of `cliff.toml`, the fixture and the environment."""

    checkout: Path
    temporary: Path
    cliff_toml: Path
    fixture: Path
    environment: Mapping[str, str]


def history_tags(git: GitExecutionContext, *, cwd: Path, revision: str) -> tuple[tuple[str, str], ...]:
    """Give the tags reachable from a revision with their commits, ordered by the commit's place in its history, in one pass.

    Tags of one commit keep the order of Git's tag listing, which is by name; nothing is sorted here.
    """
    commits = git.run(["rev-list", "--topo-order", "--reverse", revision], cwd=cwd).stdout.split()
    by_commit: dict[str, list[str]] = {}
    for record in git.tag_records(cwd=cwd, merged=revision):
        by_commit.setdefault(record.commit, []).append(record.name)
    ordered = tuple((name, commit) for commit in commits for name in by_commit.pop(commit, []))
    if by_commit:
        commit, names = next(iter(by_commit.items()))
        msg = f"tag {names[0]} names commit {commit}, outside the history of {revision}"
        raise ComparisonError(msg)
    return ordered


def chained_ranges(repository: str, tags: Sequence[str]) -> tuple[RangeCase, ...]:
    """Give the cases of tags in history order: the full history, each consecutive tag range and the last tag to HEAD."""
    pairs = [f"{earlier}..{later}" for earlier, later in itertools.pairwise(tags)]
    tail = [f"{tags[-1]}..HEAD"] if tags else []
    return (RangeCase(repository), *(RangeCase(repository, span) for span in (*pairs, *tail)))


def history_ranges(git: GitExecutionContext, *, cwd: Path, revision: str, repository: str) -> tuple[RangeCase, ...]:
    """List the cases of a repository from Git: the chained ranges of the tags reachable from the revision."""
    return chained_ranges(repository, [name for name, _commit in history_tags(git, cwd=cwd, revision=revision)])


def run_environment(source: Mapping[str, str], home: Path) -> dict[str, str]:
    """Give the one explicit git-cliff environment: three system names from the caller and an empty home."""
    chosen: dict[str, str] = {}
    for name in _SYSTEM:
        value = next((value for key, value in source.items() if key.upper() == name.upper()), None)
        if value is None:
            msg = f"the environment has no {name} to give git-cliff"
            raise ComparisonError(msg)
        chosen[name] = value
    return {**chosen, "HOME": str(home), "USERPROFILE": str(home)}


def _lines(output: bytes) -> list[str]:
    """Split raw output into lines that keep their endings; bytes that are not UTF-8 stay visible as escapes."""
    return output.decode("utf-8", errors="backslashreplace").splitlines(keepends=True)


def _shown(line: str) -> str:
    """Show one diff line without its line feed, marking a last line that has none, as `diff` does."""
    if line.startswith("@@") or line.endswith("\n"):
        return line.removesuffix("\n")
    return f"{line}\n\\ No newline at end of file"


def differing_hunks(before: bytes, after: bytes) -> tuple[str, ...]:
    """Give the unified-diff hunks from one output to the other, three lines of context each, without file headers.

    Lines keep their endings, so a carriage return or a missing last line feed is a difference that shows.
    """
    hunks: list[list[str]] = []
    for line in list(difflib.unified_diff(_lines(before), _lines(after), n=_CONTEXT_LINES, lineterm=""))[2:]:
        if line.startswith("@@"):
            hunks.append([])
        hunks[-1].append(_shown(line))
    return tuple("\n".join(hunk) for hunk in hunks)


class _Runs:
    """The runs of one comparison: both versions on every case, in a worktree that is always removed."""

    def __init__(self, inputs: FrozenInputs, invocations: Mapping[str, Callable[[], GitCliffInvocation]], workspace: Workspace) -> None:
        """Bind the inputs, the invocation providers and the directories."""
        self._inputs = inputs
        self._invocations = invocations
        self._workspace = workspace
        self.worktree = workspace.temporary / "worktree"

    def _run(self, version: str, case: RangeCase) -> tuple[bytes, int]:
        """Run one version on one case and return its output and status."""
        workspace = self._workspace
        directory = workspace.fixture if case.repository == "fixture" else self.worktree
        arguments = ["-c", str(workspace.cliff_toml), "-w", str(directory), "-s", "footer", "--", *([] if case.range is None else [case.range])]
        with self._invocations[version]() as invocation:
            outcome = invocation.run(arguments, policy=Policy.ENGINE, cwd=directory, environment=workspace.environment, output="capture",
                                     deadline=RUN_SECONDS)
        if outcome.timed_out:
            msg = f"git-cliff {version} did not end within {RUN_SECONDS} s for {case.key}"
            raise ComparisonError(msg)
        return outcome.stdout, outcome.status

    def case(self, case: RangeCase) -> CaseResult:
        """Run the baseline, then the pin, and keep the hunks only when their outputs differ."""
        (before, before_status), (after, after_status) = (self._run(version, case) for version in (self._inputs.baseline, self._inputs.pin))
        results = ((self._inputs.baseline, RunDigest(hashlib.sha256(before).hexdigest(), before_status)),
                   (self._inputs.pin, RunDigest(hashlib.sha256(after).hexdigest(), after_status)))
        return CaseResult(case, results, () if before == after else differing_hunks(before, after))


def run_comparison(inputs: FrozenInputs, invocations: Mapping[str, Callable[[], GitCliffInvocation]], git: GitExecutionContext,
                   workspace: Workspace) -> ComparisonResult:
    """Run both candidates on every frozen case, in a temporary worktree of the frozen commit removed afterwards.

    Args:
        inputs: The frozen inputs: the commit, the versions and the ranges.
        invocations: For each version, a provider of a fresh invocation object (each starts one run).
        git: The evidence Git, which adds and prunes the worktree in the checkout.
        workspace: The checkout, the temporary directory, the bundle copy of `cliff.toml`, the fixture and the environment.

    Returns:
        Each case's digests and statuses, with hunks where the outputs differ.

    Raises:
        ComparisonError: A run did not end within its bound.
    """
    runs = _Runs(inputs, invocations, workspace)
    hooks = workspace.temporary / "hooks"
    hooks.mkdir(exist_ok=True)
    failure: BaseException | None = None
    try:
        git.run(["-c", f"core.hooksPath={hooks}", "worktree", "add", "--detach", str(runs.worktree), inputs.llm_shared_commit],
                cwd=workspace.checkout)
        return ComparisonResult(tuple(runs.case(case) for case in inputs.ranges))
    except BaseException as error:
        failure = error
        raise
    finally:
        _clean(git, workspace.checkout, runs.worktree, failure)


def _removal_problems(git: GitExecutionContext, checkout: Path, worktree: Path) -> list[str]:
    """Remove the temporary worktree through Git, then from disk, prune, and verify it is gone; return what remains."""
    removed = git.run(["worktree", "remove", "--force", str(worktree)], cwd=checkout, check=False)
    problems: list[str] = []
    if worktree.exists():
        try:
            shutil.rmtree(worktree)
        except OSError as error:
            problems.append(f"{worktree} could not be deleted: {error}")
    pruned = git.run(["worktree", "prune"], cwd=checkout, check=False)
    if pruned.returncode:
        problems.append(f"`git worktree prune` exited {pruned.returncode}: {pruned.stderr.strip()}")
    listing = git.run(["worktree", "list", "--porcelain"], cwd=checkout, check=False)
    registered = [Path(line.removeprefix("worktree ")) for line in listing.stdout.splitlines() if line.startswith("worktree ")]
    if listing.returncode or worktree in registered:
        problems.append(f"the temporary worktree {worktree} may still be registered in {checkout}"
                        f" (`git worktree remove` exited {removed.returncode}: {removed.stderr.strip()})")
    return problems


def _clean(git: GitExecutionContext, checkout: Path, worktree: Path, failure: BaseException | None) -> None:
    """Remove the worktree; a cleanup problem fails a successful comparison, or is noted on the failure already raised."""
    try:
        problems = _removal_problems(git, checkout, worktree)
    except GitPolicyError as error:
        problems = [f"the temporary worktree {worktree} could not be removed: {error}"]
    if not problems:
        return
    message = "; ".join(problems)
    if failure is None:
        raise ComparisonError(message)
    failure.add_note(message)


def verify_rerun(recorded: ComparisonResult, observed: ComparisonResult) -> None:
    """Require a rerun to reproduce every recorded digest and status, naming the first case and version that differ."""
    if [case.case for case in observed.cases] != [case.case for case in recorded.cases]:
        msg = "the rerun covers other cases than the bundle records"
        raise ComparisonError(msg)
    for before, after in zip(recorded.cases, observed.cases, strict=True):
        for (version, expected), (_version, found) in zip(before.results, after.results, strict=True):
            if found != expected:
                msg = (f"the rerun of {before.case.key} with git-cliff {version} produced {found.sha256} (status {found.status});"
                       f" the bundle records {expected.sha256} (status {expected.status})")
                raise ComparisonError(msg)


# eof
