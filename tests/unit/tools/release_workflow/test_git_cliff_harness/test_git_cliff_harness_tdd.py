"""The developer entry point acquires both candidates, freezes the inputs, runs the comparison and writes the bundle.

Step 6 of v0.14.0 git-cliff-provisioning (design "The harness", "Frozen
inputs and the coverage matrix" and "Outputs and classification"; design
decisions Q13, Q14 and Q15; plan decisions Q03, Q16 and Q19). No process,
socket or real Git: candidates go through the children fake in the evidence
namespace, Git through a recording `subprocess.run`, and the temporary
directory, the date and both output streams are injected.

- A first run resolves the budget once, acquires the baseline then the pin,
  builds the fixture, freezes the llm-shared commit, the committed
  `cliff.toml` bytes of the dev_workflow submodule commit and the ranges of
  both repositories, runs the comparison and writes a bundle whose listed
  files are verified on read. It writes nothing else: no manifest, no
  production cache.
- A rerun from the bundle keeps its classification, audit, observed statuses
  and review; a byte-identical projection keeps an approval. A changed rerun
  digest, fixture hash or range list fails with status 2 and leaves the
  bundle as it was, as does a bundle of another pin or baseline. Since code
  review round 1, a changed candidate executable, even with identical
  outputs, or changed `cliff.toml` bytes fail before any git-cliff run.
  Round 2: the inputs record llm-shared's tags with their commits, and a
  cleanup problem noted on a comparison failure is printed after it.
- `--review approved` or `rejected` with `--bundle` only records the user's
  decision over the current projection with today's local date.
- A refused budget value fails before any child or Git call; arguments are
  checked by the parser; `production_context` binds the real environment, the
  Windows layer, the evidence Git and a temporary directory.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import sys
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.unit.tools.release_workflow.git_cliff_children_fake import (
    Child,
    ProvisionWorld,
)
from tests.unit.tools.release_workflow.git_cliff_harness_fake import (
    BASELINE,
    COMMIT,
    DEV_WORKFLOW,
    PIN,
    FakeGit,
    GitCall,
    git_context,
    metadata,
    refs_listing,
    tag_listing,
)
from tests.unit.tools.release_workflow.git_cliff_support import (
    STAND_IN_EXECUTABLE,
    synthetic_pin,
)
from tools.release_workflow.git_cliff import harness
from tools.release_workflow.git_cliff.budget import DOWNLOAD_BUDGET_VARIABLE
from tools.release_workflow.git_cliff.bundle import (
    BUNDLE_FILE,
    CLIFF_TOML,
    Audit,
    Classification,
    canonical_projection,
    file_digests,
    read,
    trust_name,
    with_review,
    write,
)
from tools.release_workflow.git_cliff.cache import CacheLayout, EntryRecord
from tools.release_workflow.git_cliff.comparison import RangeCase
from tools.release_workflow.git_cliff.fixture_history import TAGS, FixtureHashes
from tools.release_workflow.git_cliff.harness import (
    HarnessContext,
    evidence_git,
    main,
    production_context,
)

if TYPE_CHECKING:
    from collections.abc import Generator

    from tools.release_workflow.windows_child import ChildRequest

_BUNDLE = "tools/release_workflow/git_cliff/bundles/2.14.2"
_CLIFF = '[changelog]\nbody = "🚀 {{ version }}"\n'.encode()
_CHECKOUT_COMMITS = [f"{index:040x}" for index in range(1, 9)]
_FIXTURE_COMMITS = [f"{index:040x}" for index in range(100, 116)]
_FIXTURE = FixtureHashes("f" * 40, tuple((name, f"{index:x}" * 40) for index, name in enumerate(TAGS, start=1)))
_DAY = date(2026, 11, 21)
_FAILED = 2


def _lines(commits: list[str]) -> bytes:
    """List commits one per line."""
    return "".join(f"{commit}\n" for commit in commits).encode()


class _Scene:
    """One harness run: an evidence world, a checkout with its submodule directory, a recording Git and outputs."""

    def __init__(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Bind every seam of the harness context to fakes."""
        self.world = ProvisionWorld.build(tmp_path, monkeypatch, namespace="evidence")
        self.world.pin = synthetic_pin(PIN)
        self.root = self.world.layout.tooling_root
        (self.root / "tools" / "dev_workflow").mkdir(parents=True)
        self.checkout_tags = [("v0.1.0", _CHECKOUT_COMMITS[2]), ("v0.2.0", _CHECKOUT_COMMITS[5])]
        self.fixture = _FIXTURE
        self.fake = FakeGit({"rev-parse": self._rev_parse, "cat-file": _CLIFF, "rev-list": self._rev_list, "for-each-ref": self._refs,
                             "worktree": self._worktree})
        git_context(tmp_path, monkeypatch, self.fake)
        self.source = {"PATH": str(tmp_path / "installed"), "SystemRoot": "C:\\Windows", "TEMP": "C:\\Temp", "TMP": "C:\\Tmp"}
        self.runs: dict[tuple[str, str], bytes] = {}
        self.world.run_output = self._run
        self.out: list[str] = []
        self.err: list[str] = []
        self.temporaries = 0
        self.stuck = False
        self.worktree = tmp_path / "no-worktree-yet"
        self.tmp_path = tmp_path

    def _rev_parse(self, call: GitCall) -> bytes:
        """The checkout's HEAD commit, or the submodule commit recorded in it."""
        return f"{COMMIT if call.arguments[-1] == 'HEAD^{commit}' else DEV_WORKFLOW}\n".encode()

    def _rev_list(self, call: GitCall) -> bytes:
        """The history of the fixture or of the checkout."""
        return _lines(_FIXTURE_COMMITS if call.cwd.name == "fixture" else _CHECKOUT_COMMITS)

    def _refs(self, call: GitCall) -> bytes:
        """The fixture's refs, or the reachable tags of either repository."""
        if call.cwd.name == "fixture":
            if "refs/heads/main" in call.arguments:
                return refs_listing(self.fixture)
            return tag_listing([(name, _FIXTURE_COMMITS[2 * index + 1]) for index, name in enumerate(TAGS)])
        return tag_listing(self.checkout_tags)

    def _worktree(self, call: GitCall) -> bytes:
        """Create the worktree on `worktree add`; while `stuck`, list it as still registered after its removal."""
        if "add" in call.arguments:
            self.worktree = Path(call.arguments[-2])
            self.worktree.mkdir()
        if "list" in call.arguments and self.stuck:
            return f"worktree {self.worktree.as_posix()}\ndetached\n".encode()
        return b""

    def _run(self, request: ChildRequest) -> tuple[int, bytes]:
        """Answer a git-cliff run by version and case; identical outputs unless declared."""
        version = request.executable.parent.parent.name
        repository = "fixture" if request.cwd is not None and request.cwd.name == "fixture" else "llm-shared"
        after = request.arguments[request.arguments.index("--") + 1:]
        return 0, self.runs.get((version, f"{repository} {after[0] if after else 'full history'}"), b"## [unreleased]\n")

    @contextmanager
    def _temporary(self) -> Generator[Path]:
        """Give each run its own temporary directory."""
        self.temporaries += 1
        directory = self.tmp_path / f"run{self.temporaries}"
        directory.mkdir()
        yield directory

    def context(self) -> HarnessContext:
        """The injected harness context."""
        return HarnessContext(
            tooling_root=self.root, environment=self.source, seams=self.world.seams(),
            git=lambda temporary: evidence_git(self.source, checkout=self.root, temporary=temporary),
            temporary=self._temporary, today=lambda: _DAY, stdout=self.out.append, stderr=self.err.append,
        )

    def run(self, *arguments: str) -> int:
        """Run the harness on the 2.14.2 bundle."""
        return main(["--bundle", _BUNDLE, *arguments], context=self.context())

    def compare(self) -> int:
        """Run the comparison of 2.14.2 against 2.7.0."""
        self.world.children.script("metadata", metadata(BASELINE, digest=False), metadata(PIN))
        return self.run("--pin", PIN, "--baseline", BASELINE)

    @property
    def bundle(self) -> Path:
        """The bundle directory."""
        return self.root / _BUNDLE


@pytest.fixture
def scene(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Scene:
    """Give each case its own harness scene."""
    return _Scene(tmp_path, monkeypatch)


def test_a_first_run_freezes_the_commit_and_the_committed_cliff_toml_of_the_submodule(scene: _Scene) -> None:
    """HEAD's commit, the fixture hashes, and the `cliff.toml` bytes of the submodule commit, copied beside the bundle."""
    assert scene.compare() == 0
    inputs = read(scene.bundle).inputs
    assert (inputs.pin, inputs.baseline, inputs.llm_shared_commit, inputs.fixture) == (PIN, BASELINE, COMMIT, _FIXTURE)
    assert (inputs.cliff_toml.source, inputs.cliff_toml.sha256, inputs.cliff_toml.dev_workflow_commit) == (
        "tools/dev_workflow/cliff.toml", hashlib.sha256(_CLIFF).hexdigest(), DEV_WORKFLOW)
    assert (scene.bundle / CLIFF_TOML).read_bytes() == _CLIFF
    (cat_file,) = scene.fake.of("cat-file")
    assert (cat_file.arguments[-1], cat_file.cwd) == (f"{DEV_WORKFLOW}:cliff.toml", scene.root / "tools" / "dev_workflow")


def test_a_first_run_records_both_candidates_every_range_and_its_outputs(scene: _Scene) -> None:
    """The baseline then the pin with their trust and executable digest; the ranges of both repositories; no review yet."""
    assert scene.compare() == 0
    bundle = read(scene.bundle)
    inputs = bundle.inputs
    assert [(case.repository, case.range) for case in inputs.ranges] == [
        ("llm-shared", None), ("llm-shared", "v0.1.0..v0.2.0"), ("llm-shared", "v0.2.0..HEAD"),
        ("fixture", None), ("fixture", "v0.1.0..v0.2.0-SNAPSHOT"), ("fixture", "v0.2.0-SNAPSHOT..v0.2.0"),
        ("fixture", "v0.2.0..v0.3.0-SNAPSHOT"), ("fixture", "v0.3.0-SNAPSHOT..HEAD")]
    assert [(candidate.version, candidate.trust) for candidate in inputs.candidates] == [(BASELINE, "evidence-only-https"), (PIN, "upstream-digest")]
    assert inputs.llm_shared_tags == (("v0.1.0", _CHECKOUT_COMMITS[2]), ("v0.2.0", _CHECKOUT_COMMITS[5]))
    assert {candidate.executable_sha256 for candidate in inputs.candidates} == {hashlib.sha256(STAND_IN_EXECUTABLE).hexdigest()}
    assert [case.case for case in bundle.outputs.cases] == list(inputs.ranges)
    assert bundle.review is None
    assert scene.out == [f"git-cliff evidence harness: {PIN} against {BASELINE}, 8 cases, 0 with differences, bundle {scene.bundle / BUNDLE_FILE}"]


def test_a_first_run_writes_nothing_but_the_bundle_and_the_evidence_cache(scene: _Scene) -> None:
    """No manifest or other engine file, no production cache entry, the temporary worktree gone."""
    assert scene.compare() == 0
    written = sorted(path.relative_to(scene.root).as_posix() for path in (scene.root / "tools").rglob("*") if path.is_file())
    assert written == [f"{_BUNDLE}/{name}" for name in sorted((BUNDLE_FILE, CLIFF_TOML, trust_name(PIN), trust_name(BASELINE)))]
    assert not CacheLayout(scene.root).version_dir(synthetic_pin(PIN)).exists()
    assert not (scene.tmp_path / "run1" / "worktree").exists()


def test_the_budget_is_resolved_once_and_a_refused_value_fails_before_any_work(scene: _Scene, monkeypatch: pytest.MonkeyPatch) -> None:
    """One resolution per run; a refused value is status 2 with no child and no Git call."""
    calls: list[object] = []
    resolve = harness.resolve_budget

    def counted(environment: dict[str, str]) -> object:
        calls.append(environment)
        return resolve(environment)

    monkeypatch.setattr(harness, "resolve_budget", counted)
    assert scene.compare() == 0
    assert len(calls) == 1
    scene.source[DOWNLOAD_BUDGET_VARIABLE] = "fast"
    launched, called = len(scene.world.children.launched), len(scene.fake.calls)
    assert scene.run("--pin", PIN, "--baseline", BASELINE) == _FAILED
    assert DOWNLOAD_BUDGET_VARIABLE in scene.err[-1]
    assert (len(scene.world.children.launched), len(scene.fake.calls)) == (launched, called)


def test_a_differing_range_keeps_its_hunks(scene: _Scene) -> None:
    """The pin's output of one fixture range differs from the baseline's."""
    scene.runs[(PIN, "fixture v0.2.0-SNAPSHOT..v0.2.0")] = b"## [unreleased]\n### Security\n"
    assert scene.compare() == 0
    differing = [case for case in read(scene.bundle).outputs.cases if case.hunks]
    assert [case.case for case in differing] == [RangeCase("fixture", "v0.2.0-SNAPSHOT..v0.2.0")]
    assert "1 with differences" in scene.out[-1]


def _complete(scene: _Scene) -> None:
    """Add the user's classification, an audit and an approved review to the written bundle."""
    bundle = read(scene.bundle)
    bundle = dataclasses.replace(bundle, classification=(Classification("x #1", "intentional", "reason"),),
                                 audit=Audit(revision="d" * 40, excludes_69=True))
    write(scene.bundle, with_review(bundle, "approved", _DAY))


def test_a_rerun_keeps_the_hand_entries_and_an_approval_over_a_byte_identical_projection(scene: _Scene) -> None:
    """Classification, audit and review survive; the review still covers the projection."""
    assert scene.compare() == 0
    _complete(scene)
    before = read(scene.bundle)
    assert scene.compare() == 0
    after = read(scene.bundle)
    assert after == before
    assert after.review is not None
    assert after.review.covered_sha256 == hashlib.sha256(canonical_projection(after)).hexdigest()
    assert scene.world.children.of("metadata")[2:] == []


@pytest.mark.parametrize(("change", "reason"), [
    pytest.param("output", "rerun of llm-shared full history with git-cliff 2.14.2", id="digest"),
    pytest.param("fixture", "refs/heads/main", id="fixture"),
    pytest.param("ranges", "ranges", id="ranges"),
])
def test_a_rerun_that_does_not_reproduce_the_bundle_fails_and_leaves_it(change: str, reason: str, scene: _Scene) -> None:
    """A changed digest, fixture hash or range list is status 2, and the bundle keeps its bytes."""
    assert scene.compare() == 0
    content = (scene.bundle / BUNDLE_FILE).read_bytes()
    if change == "output":
        scene.runs[(PIN, "llm-shared full history")] = b"changed\n"
    elif change == "fixture":
        scene.fixture = FixtureHashes("e" * 40, _FIXTURE.tags)
    else:
        scene.checkout_tags.append(("v0.3.0", _CHECKOUT_COMMITS[7]))
    assert scene.run("--pin", PIN, "--baseline", BASELINE) == _FAILED
    assert reason in scene.err[-1]
    assert scene.err[-1].startswith("git-cliff evidence harness: ")
    assert (scene.bundle / BUNDLE_FILE).read_bytes() == content


def test_a_rerun_whose_candidate_executable_changed_fails_before_any_run_even_with_identical_outputs(scene: _Scene) -> None:
    """Code review round 1: the pin's entry now holds other bytes, recorded consistently; the frozen identity differs."""
    assert scene.compare() == 0
    content = (scene.bundle / BUNDLE_FILE).read_bytes()
    layout = CacheLayout(scene.root, "evidence")
    changed = b"MZ another build"
    layout.executable(scene.world.pin).write_bytes(changed)
    record = EntryRecord.decode(layout.record(scene.world.pin).read_bytes())
    layout.record(scene.world.pin).write_bytes(dataclasses.replace(
        record, executable_sha256=hashlib.sha256(changed).hexdigest(), executable_size=len(changed)).encode())
    runs = len(scene.world.children.of("run"))
    assert scene.run("--pin", PIN, "--baseline", BASELINE) == _FAILED
    assert "the frozen inputs changed since the bundle was written: candidates" in scene.err[-1]
    assert len(scene.world.children.of("run")) == runs
    assert (scene.bundle / BUNDLE_FILE).read_bytes() == content


def test_a_rerun_whose_copied_configuration_changed_fails(scene: _Scene) -> None:
    """The bundle copy of `cliff.toml` changed with its listed digest, so the bundle still reads; the frozen digest differs."""
    assert scene.compare() == 0
    bundle = read(scene.bundle)
    (scene.bundle / CLIFF_TOML).write_bytes(b'[changelog]\nbody = "changed"\n')
    write(scene.bundle, dataclasses.replace(bundle, files=file_digests(scene.bundle, PIN, BASELINE)))
    assert scene.run("--pin", PIN, "--baseline", BASELINE) == _FAILED
    assert scene.err[-1].endswith(f"changed since the bundle was written: {CLIFF_TOML}; nothing was run or written")


def test_a_cleanup_problem_is_printed_after_the_comparison_failure_it_rides_on(scene: _Scene) -> None:
    """Code review round 2: a git-cliff run that does not end and a worktree still registered: both reach standard error."""
    scene.world.children.script("run", Child(hang=True))
    scene.stuck = True
    assert scene.compare() == _FAILED
    assert scene.err[0].startswith("git-cliff evidence harness: git-cliff 2.7.0 did not end within 120 s")
    assert scene.err[1].startswith(f"git-cliff evidence harness: the temporary worktree {scene.worktree} may still be registered")
    assert len(scene.err) == len(["comparison failure", "cleanup note"])
    assert not (scene.bundle / BUNDLE_FILE).exists()


def test_a_bundle_of_another_pair_is_not_rerun(scene: _Scene) -> None:
    """The bundle's own pin and baseline are the only pair it can hold."""
    assert scene.compare() == 0
    assert scene.run("--pin", PIN, "--baseline", "2.8.0") == _FAILED
    assert "2.7.0" in scene.err[-1]


@pytest.mark.parametrize("decision", ["approved", "rejected"])
def test_the_review_mode_records_only_the_users_decision_over_the_current_projection(decision: str, scene: _Scene) -> None:
    """Today's date, reviewer `user`, the covered digest; nothing else changes."""
    assert scene.compare() == 0
    before = read(scene.bundle)
    launched = len(scene.world.children.launched)
    assert scene.run("--review", decision) == 0
    after = read(scene.bundle)
    assert after == with_review(before, decision, _DAY)
    assert dataclasses.replace(after, review=None) == before
    assert len(scene.world.children.launched) == launched
    assert scene.out[-1].endswith(f"recorded the user's {decision} review of {scene.bundle / BUNDLE_FILE}")


def test_the_review_of_a_missing_bundle_fails(scene: _Scene) -> None:
    """There is no projection to cover."""
    assert scene.run("--review", "approved") == _FAILED
    assert BUNDLE_FILE in scene.err[-1]


@pytest.mark.parametrize("arguments", [
    pytest.param(["--bundle", _BUNDLE, "--review", "approved", "--pin", PIN], id="review-with-pin"),
    pytest.param(["--bundle", _BUNDLE, "--pin", PIN], id="no-baseline"),
    pytest.param(["--bundle", _BUNDLE, "--review", "maybe"], id="decision"),
    pytest.param(["--pin", PIN, "--baseline", BASELINE], id="no-bundle"),
])
def test_arguments_are_checked_by_the_parser(arguments: list[str], scene: _Scene, capsys: pytest.CaptureFixture[str]) -> None:
    """A comparison needs `--pin` and `--baseline`; a review takes neither and only approved or rejected."""
    with pytest.raises(SystemExit) as raised:
        main(arguments, context=scene.context())
    assert raised.value.code == _FAILED
    assert "usage" in capsys.readouterr().err


def test_an_absolute_bundle_directory_is_used_as_given(scene: _Scene) -> None:
    """A relative directory is placed under the tooling root; an absolute one is kept."""
    scene.world.children.script("metadata", metadata(BASELINE, digest=False), metadata(PIN))
    elsewhere = scene.tmp_path / "elsewhere"
    assert main(["--bundle", str(elsewhere), "--pin", PIN, "--baseline", BASELINE], context=scene.context()) == 0
    assert (elsewhere / BUNDLE_FILE).is_file()


def test_the_production_context_binds_the_real_environment_and_layer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The checkout of this module, the process environment and interpreter, the evidence Git and a temporary directory."""
    context = production_context()
    assert context.tooling_root == Path(harness.__file__).resolve().parents[3]
    assert dict(context.environment) == dict(os.environ)
    assert context.seams.runtime == Path(sys.executable)
    assert context.today() == date.today()  # noqa: DTZ011 - the harness records the local date
    with context.temporary() as temporary:
        assert temporary.is_dir()
    assert not temporary.exists()
    fake = FakeGit()
    git_context(tmp_path, monkeypatch, fake)
    monkeypatch.setenv("PATH", str(tmp_path / "installed"))
    git = production_context().git(tmp_path)
    assert git.environment.values["GIT_CONFIG_NOSYSTEM"] == "1"
    assert (tmp_path / "empty.gitconfig").read_bytes() == b""


def test_the_writers_of_the_production_context_end_each_line(capsys: pytest.CaptureFixture[str]) -> None:
    """One line on standard output, one on standard error."""
    context = production_context()
    context.stdout("done")
    context.stderr("failed")
    captured = capsys.readouterr()
    assert (captured.out, captured.err) == ("done\n", "failed\n")


# eof
