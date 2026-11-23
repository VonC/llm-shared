"""Run the git-cliff compatibility evidence by hand: acquire both candidates, compare them on frozen inputs, write the bundle.

Step 6 of v0.14.0 git-cliff-provisioning (design "The harness", "Frozen
inputs and the coverage matrix" and "Outputs and classification"; design
decisions Q13, Q14 and Q15; plan decisions Q03, Q16 and Q19). The developer
entry point of the internal comparison modules; it defines no engine command,
and item 6 decides its public form. It downloads and runs binaries and runs
Git, so it runs by hand, outside pytest, from the project root:

    python -m tools.release_workflow.git_cliff.harness --bundle <dir> --pin 2.14.2 --baseline 2.7.0
    python -m tools.release_workflow.git_cliff.harness --bundle <dir> --review approved

A comparison run resolves the budget once, before any work; reads an existing
bundle (which must be of the same pin and baseline); acquires the baseline
then the pin (`candidates.acquire_candidate`, which writes each trust record
once); builds the fixture history in a temporary directory and checks it
against the bundle's hashes; freezes llm-shared's HEAD commit, the committed
`cliff.toml` bytes of the dev_workflow submodule commit (copied into the
bundle) and the ranges of both repositories, or reuses the bundle's and
requires the same ranges; runs the comparison; requires a rerun to reproduce
every recorded digest; and writes the bundle, keeping its classification,
audit, observed statuses and review (a review whose projection changed is
stale). It never writes the manifest and never reaches the production cache.

`--review approved` or `--review rejected` with `--bundle` only records the
user's decision over the current projection, with today's local date.

Code review round 1 of Step 6: a rerun compares the complete frozen inputs it
observes (commit, `cliff.toml` descriptor, fixture hashes, ranges, candidate
identities with their executable digests, flags and environment names) and
the copied `cliff.toml` bytes with the bundle's before anything runs, so a
changed input fails even when the outputs would be identical, and the bundle
keeps its bytes. Round 2: the frozen inputs record llm-shared's reachable
tags with their commits, from which its ranges are chained, and every note a
failure carries, such as a worktree cleanup problem, is printed after its
diagnostic.

Every expected failure prints one diagnostic on standard error and returns 2;
a bad argument is the parser's status 2. `HarnessContext` carries every
boundary, so the flow is tested with fakes; `production_context` binds the
real ones.
"""

from __future__ import annotations

import argparse
import dataclasses
import functools
import hashlib
import os
import sys
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from tools.release_workflow.git import GitExecutionContext
from tools.release_workflow.git_cliff import fixture_history
from tools.release_workflow.git_cliff.budget import BudgetSettingError, resolve_budget
from tools.release_workflow.git_cliff.bundle import (
    BUNDLE_FILE,
    CLIFF_TOML,
    DECISIONS,
    Bundle,
    BundleError,
    file_digests,
    read,
    refreshed,
    trust_name,
    with_review,
    write,
)
from tools.release_workflow.git_cliff.cache import CacheLayout, EntryRecord
from tools.release_workflow.git_cliff.candidates import (
    CandidateError,
    TrustRecord,
    acquire_candidate,
)
from tools.release_workflow.git_cliff.comparison import (
    CandidateIdentity,
    CliffToml,
    ComparisonError,
    FrozenInputs,
    Workspace,
    chained_ranges,
    history_ranges,
    history_tags,
    run_comparison,
    run_environment,
    verify_rerun,
)
from tools.release_workflow.git_cliff.fixture_history import FixtureError
from tools.release_workflow.git_cliff.messages import ProvisioningError
from tools.release_workflow.git_cliff.provisioning import production_seams
from tools.release_workflow.git_environment import GitPolicyError

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping, Sequence
    from contextlib import AbstractContextManager

    from tools.release_workflow.git_cliff.budget import BudgetPolicy
    from tools.release_workflow.git_cliff.comparison import ComparisonResult
    from tools.release_workflow.git_cliff.fixture_history import FixtureHashes
    from tools.release_workflow.git_cliff.invocation import GitCliffInvocation
    from tools.release_workflow.git_cliff.provisioning import ProvisioningSeams

_CLIFF_SOURCE = "tools/dev_workflow/cliff.toml"
_PREFIX = "git-cliff evidence harness: "
_FAILURES = (ProvisioningError, CandidateError, BundleError, FixtureError, ComparisonError, BudgetSettingError, GitPolicyError, OSError)


@dataclass(frozen=True, kw_only=True)
class HarnessContext:
    """Every boundary of a harness run: the checkout, the environment, the Windows layer, Git, a temporary directory, the date and the streams."""

    tooling_root: Path
    environment: Mapping[str, str]
    seams: ProvisioningSeams
    git: Callable[[Path], GitExecutionContext]
    temporary: Callable[[], AbstractContextManager[Path]]
    today: Callable[[], date]
    stdout: Callable[[str], None]
    stderr: Callable[[str], None]


def evidence_git(source: Mapping[str, str], *, checkout: Path, temporary: Path) -> GitExecutionContext:
    """Select Git for the evidence run: an empty global configuration file in the temporary directory, no system file."""
    config = temporary / "empty.gitconfig"
    config.write_bytes(b"")
    return GitExecutionContext.create(fixture_history.environment(source, config), original_cwd=checkout, non_interactive=True)


@contextmanager
def _temporary_directory() -> Generator[Path]:
    """Give a temporary directory outside the repository, removed when the run ends."""
    with tempfile.TemporaryDirectory(prefix="git-cliff-evidence-") as directory:
        # The long form of the path, as Git lists the worktrees below it.
        yield Path(directory).resolve()


def _stdout(line: str) -> None:
    """Write one whole line on standard output."""
    sys.stdout.write(f"{line}\n")
    sys.stdout.flush()


def _stderr(line: str) -> None:
    """Write one whole line on standard error."""
    sys.stderr.write(f"{line}\n")
    sys.stderr.flush()


def production_context() -> HarnessContext:
    """Bind this checkout, the process environment and interpreter, the Windows layer, the evidence Git and the local date."""
    root = Path(__file__).resolve().parents[3]
    environment = dict(os.environ)
    return HarnessContext(
        tooling_root=root, environment=environment, seams=production_seams(Path(sys.executable)),
        git=lambda temporary: evidence_git(environment, checkout=root, temporary=temporary), temporary=_temporary_directory,
        today=date.today, stdout=_stdout, stderr=_stderr,
    )


class _Options(argparse.Namespace):
    """The parsed arguments."""

    bundle: str
    pin: str | None
    baseline: str | None
    review: str | None


def _options(arguments: Sequence[str]) -> _Options:
    """Parse a comparison (`--pin`, `--baseline`) or a review (`--review`), each with `--bundle`."""
    parser = argparse.ArgumentParser(prog="python -m tools.release_workflow.git_cliff.harness",
                                     description="Compare two git-cliff versions on frozen inputs, or record the user's review.")
    parser.add_argument("--bundle", required=True, help="the bundle directory, relative to the checkout or absolute")
    parser.add_argument("--pin", help="the version the bundle can admit, such as 2.14.2")
    parser.add_argument("--baseline", help="the version it is compared with, such as 2.7.0")
    parser.add_argument("--review", choices=DECISIONS, help="record the user's decision over the current bundle instead")
    options = parser.parse_args(arguments, namespace=_Options())
    if options.review is not None and (options.pin is not None or options.baseline is not None):
        parser.error("--review takes --bundle only")
    if options.review is None and (options.pin is None or options.baseline is None):
        parser.error("a comparison needs --pin and --baseline")
    return options


class _Run:
    """One comparison run of a pin against its baseline, into one bundle directory."""

    def __init__(self, context: HarnessContext, directory: Path, pin: str, baseline: str) -> None:
        """Bind the run to its context and bundle directory."""
        self._context = context
        self._directory = directory
        self._pin = pin
        self._baseline = baseline

    def _existing(self) -> Bundle | None:
        """Read the bundle already there, which must compare the same two versions."""
        if not (self._directory / BUNDLE_FILE).is_file():
            return None
        bundle = read(self._directory)
        if (bundle.pin, bundle.baseline) != (self._pin, self._baseline):
            msg = (f"{self._directory / BUNDLE_FILE} compares {bundle.pin} with {bundle.baseline},"
                   f" not {self._pin} with {self._baseline}")
            raise BundleError(msg)
        return bundle

    def _providers(self, budget: BudgetPolicy) -> dict[str, Callable[[], GitCliffInvocation]]:
        """Give each version a provider of fresh invocation objects, baseline first."""
        context = self._context
        return {version: functools.partial(acquire_candidate, context.tooling_root, version, budget, context.seams,
                                           trust_path=self._directory / trust_name(version)) for version in (self._baseline, self._pin)}

    def _identity(self, version: str) -> CandidateIdentity:
        """Read an acquired candidate's identity from its trust record, and its executable digest from its entry."""
        candidate = TrustRecord(self._directory / trust_name(version), version).require()
        entry = EntryRecord.decode(CacheLayout(self._context.tooling_root, "evidence").record(candidate).read_bytes())
        return CandidateIdentity(version=version, asset=candidate.asset, size=candidate.size, sha256=candidate.sha256, trust=candidate.trust,
                                 executable_sha256=entry.executable_sha256)

    def _cliff_toml(self, git: GitExecutionContext, commit: str) -> CliffToml:
        """Copy the committed `cliff.toml` of the dev_workflow submodule commit recorded in the frozen commit into the bundle."""
        root = self._context.tooling_root
        submodule = git.run(["rev-parse", "--verify", f"{commit}:tools/dev_workflow"], cwd=root).stdout.strip()
        content = git.run(["cat-file", "blob", f"{submodule}:cliff.toml"], cwd=root / "tools" / "dev_workflow").stdout.encode("utf-8")
        self._directory.mkdir(parents=True, exist_ok=True)
        (self._directory / CLIFF_TOML).write_bytes(content)
        return CliffToml(source=_CLIFF_SOURCE, sha256=hashlib.sha256(content).hexdigest(), dev_workflow_commit=submodule)

    def _inputs(self, git: GitExecutionContext, existing: Bundle | None, hashes: FixtureHashes, fixture: Path) -> FrozenInputs:
        """Freeze the inputs on a first run; on a rerun, reuse the bundle's and require the same ranges."""
        root = self._context.tooling_root
        commit = git.run(["rev-parse", "--verify", "HEAD^{commit}"], cwd=root).stdout.strip() if existing is None else existing.inputs.llm_shared_commit
        cliff = self._cliff_toml(git, commit) if existing is None else existing.inputs.cliff_toml
        tags = history_tags(git, cwd=root, revision=commit)
        ranges = (*chained_ranges("llm-shared", [name for name, _commit in tags]),
                  *history_ranges(git, cwd=fixture, revision="HEAD", repository="fixture"))
        inputs = FrozenInputs(pin=self._pin, baseline=self._baseline, llm_shared_commit=commit, llm_shared_tags=tags, cliff_toml=cliff,
                              fixture=hashes, ranges=ranges, candidates=tuple(self._identity(version) for version in (self._baseline, self._pin)))
        if existing is not None:
            self._require_frozen(existing.inputs, inputs)
        return inputs

    def _require_frozen(self, recorded: FrozenInputs, observed: FrozenInputs) -> None:
        """Refuse a rerun whose inputs, or copied configuration bytes, differ from the bundle's, before anything runs."""
        changed = [field.name for field in dataclasses.fields(FrozenInputs) if getattr(recorded, field.name) != getattr(observed, field.name)]
        if hashlib.sha256((self._directory / CLIFF_TOML).read_bytes()).hexdigest() != recorded.cliff_toml.sha256:
            changed.append(CLIFF_TOML)
        if changed:
            msg = f"the frozen inputs changed since the bundle was written: {', '.join(changed)}; nothing was run or written"
            raise ComparisonError(msg)

    def _compare(self, budget: BudgetPolicy, existing: Bundle | None) -> tuple[FrozenInputs, ComparisonResult]:
        """Acquire both candidates, build and check the fixture, freeze the inputs and run the comparison."""
        context = self._context
        providers = self._providers(budget)
        for provider in providers.values():
            provider().close()
        with context.temporary() as temporary:
            git = context.git(temporary)
            fixture = temporary / "fixture"
            hashes = fixture_history.build(git, fixture)
            if existing is not None:
                fixture_history.verify(existing.inputs.fixture, hashes)
            inputs = self._inputs(git, existing, hashes, fixture)
            home = temporary / "home"
            home.mkdir()
            workspace = Workspace(checkout=context.tooling_root, temporary=temporary, cliff_toml=self._directory / CLIFF_TOML, fixture=fixture,
                                  environment=run_environment(context.environment, home))
            return inputs, run_comparison(inputs, providers, git, workspace)

    def run(self) -> None:
        """Compare the two versions and write the bundle, keeping its hand-written entries."""
        budget = resolve_budget(self._context.environment)
        existing = self._existing()
        inputs, result = self._compare(budget, existing)
        if existing is not None:
            verify_rerun(existing.outputs, result)
        fresh = Bundle(inputs=inputs, outputs=result, files=file_digests(self._directory, self._pin, self._baseline))
        write(self._directory, fresh if existing is None else refreshed(fresh, existing))
        differing = sum(1 for case in result.cases if case.hunks)
        self._context.stdout(f"{_PREFIX}{self._pin} against {self._baseline}, {len(result.cases)} cases, {differing} with differences,"
                             f" bundle {self._directory / BUNDLE_FILE}")


def _review(context: HarnessContext, directory: Path, decision: str) -> None:
    """Record only the user's decision over the bundle's current projection, with today's local date."""
    write(directory, with_review(read(directory), decision, context.today()))
    context.stdout(f"{_PREFIX}recorded the user's {decision} review of {directory / BUNDLE_FILE}")


def main(arguments: Sequence[str], *, context: HarnessContext | None = None) -> int:
    """Run a comparison or record a review; return 0, or 2 after one diagnostic on standard error.

    Args:
        arguments: The command-line arguments after the module name.
        context: The boundaries of the run; the production ones by default.

    Returns:
        0 on success, 2 when a stage failed.
    """
    options = _options(arguments)
    active = production_context() if context is None else context
    directory = active.tooling_root / options.bundle
    try:
        if options.review is not None:
            _review(active, directory, options.review)
        else:
            _Run(active, directory, str(options.pin), str(options.baseline)).run()
    except _FAILURES as error:
        active.stderr(f"{_PREFIX}{error}")
        notes: list[str] = getattr(error, "__notes__", [])
        for note in notes:
            active.stderr(f"{_PREFIX}{note}")
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))


# eof
