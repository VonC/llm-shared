"""Real Git repositories and public CLI scenarios for resume acceptance.

Scenario setup and teardown are included in the total-duration audit. Tests
retain assertions over process results, protocol bytes, Git state and fenced capabilities,
including status failure JSON delivered on the error stream.

Fix: the independent-waiter helpers moved here from the concurrency module.
That module was split so its scenarios run on separate xdist workers, and both
halves need the same process start, idle-silence and terminal-result helpers.

Fix: every real subprocess bound shares ``PROCESS_TIMEOUT_SECONDS``. The bounds
are hang guards, not performance assertions: under the parallel full run, a
``publish-request`` of a fixture's setup (Python start plus its few ``git``
calls, with no lock wait) once took longer than the former 30 seconds while
every worker was spawning processes, and the same file passed in focus.

Fix: a ``ReviewRepository`` copies a seed repository built once per test
process and per home and family, under pytest's temporary root, instead of
running ``git init``, two configuration writes, an add and a commit for every
scenario. The copy is byte for byte the seeded repository, so every scenario
still starts from a real committed Git history.

Fix: scenario variants reuse imported CLI modules with a fresh runtime and
restored host state per invocation. Lifecycle ownership pickup, status and
workflow launchers, and independent waiters still cross real process boundaries.
This removes repeated interpreter startup from total setup time.

Independent waiters signal their first notification boundary before returning
to the parent. Silence alone cannot distinguish startup from a parked waiter;
the signal prevents fast parent mutations racing the initial real-Git scan.

Fix: a waiter started from a Windows virtual environment runs behind the
``python`` launcher stub, and ``process.kill()`` ended only the stub: one real
interpreter kept polling every 0.05s for an hour after its test process died.
:func:`stop_waiter` ends the exact interpreter the driver reported and then
the started process, the driver exits once its test process or its direct
parent is gone, and a session finalizer fails the run when any reported
interpreter survives.

Fix: the seed's identity travels as ``-c`` options of its one commit instead of
two ``git config`` processes.
"""

# ruff: noqa: S603, S607, PLR0913
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from time import monotonic, sleep
from typing import TYPE_CHECKING, Any, Final
from uuid import uuid4

import pytest

from tests.acceptance.review_resume.cli_support import run_inline
from tests.acceptance.review_resume.waiter_driver import PARENT_VARIABLE
from tests.acceptance.review_resume.waiter_processes import TrackedProcess
from tests.unit.tools.git_test_double import GitTestDouble
from tests.unit.tools.review_exchange_test_support import (
    capability_arguments,
    common_arguments,
    configured_home,
    review_artifact,
    review_context,
    session_environment,
)
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import (
    parse_json_markdown,
    render_json_markdown,
)
from tools.review_exchange_paths import derive_artifact_paths

if TYPE_CHECKING:
    from collections.abc import Iterator

    from tools.review_exchange_models import ReviewContext

SHARED_ROOT = Path(__file__).resolve().parents[3]
# The real interpreter of each started waiter, by the pid of the process started.
_WAITERS: dict[int, TrackedProcess] = {}
EXCHANGE_LAUNCHER = SHARED_ROOT / "bin" / "review_exchange.bat"
EXCHANGE_MODULE = ("-m", "tools.review_exchange_cli")
# Hang guard for every real child process and for a waiter's wake-up: long
# enough to absorb process creation while all xdist workers spawn children at
# once, short enough that a genuinely stuck command still fails the test.
PROCESS_TIMEOUT_SECONDS: Final = 120


def module_session_environment(nature: str) -> dict[str, str]:
    """Isolate the simulated host and expose the project modules to a child run.

    The batch launchers self-locate their package; a ``python -m`` child needs
    the repository on ``PYTHONPATH`` instead.
    """
    environment = session_environment(os.environ, nature)
    previous = environment.get("PYTHONPATH")
    root = str(SHARED_ROOT)
    environment["PYTHONPATH"] = f"{root}{os.pathsep}{previous}" if previous else root
    return environment


@dataclass(frozen=True)
class ProcessResult:
    """One real command's exit code, streams and sole decoded machine result."""

    code: int
    stdout: str
    stderr: str
    payload: dict[str, Any]


def _run_git(root: Path, *arguments: str) -> str:
    """Run one bounded real ``git`` command in a repository."""
    result = subprocess.run(["git", *arguments], cwd=root, check=True,
                            capture_output=True, text=True, timeout=PROCESS_TIMEOUT_SECONDS)
    return result.stdout.strip()


@dataclass(frozen=True)
class _Seed:
    """One real seeded repository, the template every scenario copies."""

    root: Path
    context: ReviewContext
    tracked: dict[str, bytes]

    @classmethod
    def build(cls, root: Path, home: str, family: ReviewFamily) -> _Seed:
        """Seed ordinary Git documents and an ignored runtime home with real Git."""
        root.mkdir(parents=True)
        _run_git(root, "init", "-q", "-b", "resume-acceptance")
        (root / ".gitignore").write_text("a.*\ndocs/**/review.*.md\n", encoding="utf-8")
        home_path = configured_home(root, home)
        (home_path / "a.review-mode").write_text("wait_timeout_seconds=300\n", encoding="utf-8")
        context = review_context(root, family, "resume-acceptance", step="6" if family is ReviewFamily.CODE else None)
        docs = context.document_path.parent
        (docs / "draft.v0.11.0.resume-acceptance.md").write_text("# Resume acceptance draft\n", encoding="utf-8")
        (docs / "feature-request.v0.11.0.resume-acceptance.md").write_text("# Resume acceptance requirement\n", encoding="utf-8")
        _run_git(root, "add", "-A")
        _run_git(root, "-c", "user.name=Resume Acceptance", "-c", "user.email=resume@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "test: seed resume acceptance")
        tracked = {name: (root / name).read_bytes() for name in _run_git(root, "ls-files", "-z").split("\0") if name}
        return cls(root, context, tracked)


# The seeded templates of this test process, one per home and family, kept
# under pytest's temporary root by the session fixture below.
_SEEDS: dict[tuple[str, ReviewFamily], _Seed] = {}
_SEED_BASE: list[Path] = []


@pytest.fixture(scope="session", autouse=True)
def seeded_repository_base(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Hold this session's seeded repositories under pytest's temporary root."""
    _SEED_BASE[:] = [tmp_path_factory.mktemp("seeded-repositories")]
    _SEEDS.clear()


def _seeded(home: str, family: ReviewFamily) -> _Seed:
    """Return the seed of one home and family, building it with real Git once."""
    key = (home, family)
    if key not in _SEEDS:
        _SEEDS[key] = _Seed.build(_SEED_BASE[0] / f"seed-{len(_SEEDS)}" / "caller", home, family)
    return _SEEDS[key]


class ReviewRepository:
    """Build real repositories while every transition uses the public CLI.

    Fix: each repository is a copy of a seed built once per test process with
    real Git, instead of a fresh ``git init``, configuration, add and commit
    per scenario. The copy carries the same commit, index, ignore files and
    home byte for byte, and loads its configuration once, so a fixture now
    spawns one ``git`` process instead of about seven.
    Scenario variants reuse CLI imports; lifecycle ownership takeover explicitly
    selects a separate process to retain restart and host-isolation coverage.
    """

    def __init__(self, root: Path, *, home: str = ".reviews", family: ReviewFamily = ReviewFamily.CODE,
                 processes: bool = False, fast_git: bool = False) -> None:
        """Copy the seeded Git documents and the ignored runtime home of this family."""
        seed = _seeded(home, family)
        shutil.copytree(seed.root, root)
        self.root = root
        self.processes = processes
        self.git_queries = GitTestDouble(subprocess.run) if fast_git else None
        if self.git_queries is not None:
            self.git_queries.register(root, staged=seed.tracked)
        configuration = ReviewArtifactConfiguration.load(root)
        self.home = configuration.home
        document = root.resolve() / seed.context.document_path.relative_to(seed.root.resolve())
        self.context = replace(seed.context, document_path=document)
        self.paths = derive_artifact_paths(root, self.context, configuration=configuration)

    def git(self, *arguments: str) -> str:
        """Keep setup and Git observations on bounded real subprocesses."""
        return _run_git(self.root, *arguments)

    def run(self, *arguments: str, nature: str = "codex", launcher: Path | None = None,
            separate_process: bool = False) -> ProcessResult:
        """Execute the public entry point with a fresh host environment.

        Process-bound exchange operations use ``python -m tools.review_exchange_cli``.
        The batch form also spawns ``cmd.exe``, doubling process creation on
        the hottest path of the suite. ``rvw_status.bat`` and
        ``prompt_workflow.bat`` are still driven through their batch launchers,
        so the shipped shims keep their acceptance coverage.
        Scenario variants invoke the same main function directly, restoring the
        caller's directory, environment and streams even if an invocation fails.
        """
        command = ([str(launcher), *arguments] if launcher is not None
                   else [sys.executable, *EXCHANGE_MODULE, *arguments])
        environment = module_session_environment(nature)
        if self.processes or separate_process or launcher is not None:
            result = subprocess.run(command, cwd=self.root, env=environment, check=False,
                                    capture_output=True, text=True, timeout=PROCESS_TIMEOUT_SECONDS)
        else:
            result = run_inline(arguments, self.root, environment, self.git_queries)
        lines = (result.stdout or result.stderr).splitlines()
        assert len(lines) == 1, (result.returncode, result.stdout, result.stderr)
        return ProcessResult(result.returncode, result.stdout, result.stderr, json.loads(lines[0]))

    def exchange(self, operation: str, *arguments: str, nature: str = "codex",
                 capability: dict[str, Any] | None = None) -> ProcessResult:
        """Send unchanged exact context and only the invoking session's capability."""
        ownership = [] if capability is None else capability_arguments(capability)
        return self.run(operation, *common_arguments(self.context), *ownership, *arguments, nature=nature)

    def publish(self, role: ReviewRole, capability: dict[str, Any], *, round_number: int = 1,
                ready: bool = False, nature: str = "codex") -> ProcessResult:
        """Publish caller-owned content through the shared core, never onto protocol paths."""
        disposition = None if role is ReviewRole.REQUESTOR else (
            ReviewDisposition.CONVERGENCE_RECOMMENDED if ready else ReviewDisposition.CHANGES_REQUESTED
        )
        content = self.home / f"a.input-{role.value}-{round_number}.md"
        summary = self.home / f"a.summary-{role.value}-{round_number}.md"
        content.write_text(review_artifact(self.context, role, round_number, disposition=disposition), encoding="utf-8")
        summary.write_text(f"## {role.value} evidence (round {round_number})\n\n"
                           f"Acceptance evidence for {self.context.identity.slug}.\n", encoding="utf-8")
        operation = "publish-request" if role is ReviewRole.REQUESTOR else "publish-answer"
        return self.exchange(operation, "--content-file", str(content), "--summary-file", str(summary),
                             nature=nature, capability=capability)

    def start_request(self, *, nature: str = "codex") -> dict[str, Any]:
        """Create an ordinary request using the start-issued capability."""
        started = self.exchange("start", nature=nature)
        assert started.code == 0, started
        published = self.publish(ReviewRole.REQUESTOR, started.payload, nature=nature)
        assert published.code == 0, published
        return started.payload

    def resume(self, prompt: str, *, role: str | None = None, nature: str = "codex",
               capability: dict[str, Any] | None = None, override: bool = False,
               separate_process: bool = False) -> list[ProcessResult]:
        """Simulate bare-text orchestration; instruction tests separately bind this driver."""
        assert prompt == "resume"
        results = self._migration_preflight(nature)
        if results[-1].payload["outcome"] != "ready":
            return results
        selection = self._resume_selection(role, nature, override=override)
        inspected = self.run("resume-inspect", *selection, nature=nature)
        results.append(inspected)
        if inspected.payload["outcome"] != "ready" or not inspected.payload["candidates"]:
            return results
        candidate = inspected.payload["candidates"][0]
        if role is None:
            selection.extend(("--role", inspected.payload["role"]))
        ownership = [] if capability is None else capability_arguments(capability)
        results.append(self.run("claim", *selection, "--round", str(candidate["round"]),
                                "--occurrence", str(candidate["occurrence"]), *ownership, nature=nature,
                                separate_process=separate_process))
        return results

    def _migration_preflight(self, nature: str) -> list[ProcessResult]:
        """Require a ready post-migration check before any role inspection."""
        results = [self.run("migration-check", nature=nature)]
        if results[-1].payload["outcome"] == "migration-required":
            results.append(self.run("migrate-artifacts", nature=nature))
            results.append(self.run("migration-check", nature=nature))
        return results

    def _resume_selection(self, role: str | None, nature: str, *, override: bool) -> list[str]:
        """Carry only document, step, supplied role and trusted provider evidence."""
        selection = ["--document", str(self.context.document_path)]
        if self.context.implementation_step is not None:
            selection.extend(("--implementation-step", self.context.implementation_step))
        if role:
            selection.extend(("--role", role))
        if nature == "gemini":
            selection.extend(("--trusted-host-hint", nature))
        if override:
            selection.append("--override")
        return selection

    def evidence(self) -> dict[str, bytes]:
        """Capture only runtime protocol evidence and its versioned transcript."""
        paths = (self.paths.request, self.paths.answer, self.paths.coordination,
                 self.paths.tombstone, self.paths.transcript)
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in paths if path.is_file()}

    def natures(self, path: Path) -> dict[str, Any]:
        """Read the exact strict envelope or coordination snapshot for assertions."""
        return parse_json_markdown(path.read_text(encoding="utf-8"))[0].get("role_natures", {})


@pytest.fixture
def repository(tmp_path: Path) -> ReviewRepository:
    """Provide an independent real repository before the scenario's measured call."""
    return ReviewRepository(tmp_path / "caller")


@pytest.fixture(
    scope="module",
    params=[
        pytest.param(family, marks=pytest.mark.xdist_group(f"lifecycle-{family.value}"))
        for family in (ReviewFamily.CODE, ReviewFamily.SPECIFICATION)
    ],
)
def lifecycle_journey(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> dict[str, Any]:
    """Run both families through fresh-lease displacement and human-authorized release."""
    tmp_path = tmp_path_factory.mktemp("resume-lifecycle")
    family = request.param
    repo = ReviewRepository(tmp_path / "caller", family=family,
                            home=".reviews" if family is ReviewFamily.CODE else "runtime/reviews",
                            fast_git=True)
    writer = repo.start_request()
    pending = repo.resume("resume")
    first = repo.resume("resume", role="reviewer", nature="claude")
    # A fresh interpreter must recover ownership from disk without the first
    # session's capability. Surrounding orchestration reuses imports and the
    # bounded Git double; status/workflow launchers and this pickup stay real.
    lost = repo.resume("resume", nature="claude", separate_process=True)
    stale = repo.publish(ReviewRole.REVIEWER, first[-1].payload, nature="claude")
    answer = repo.publish(ReviewRole.REVIEWER, lost[-1].payload, ready=True, nature="claude")
    before = repo.evidence()
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    human = subprocess.run([str(SHARED_ROOT / "rvw_status.bat")], cwd=repo.root,
                           env=session_environment(os.environ, "codex"), check=False,
                           capture_output=True, text=True, timeout=PROCESS_TIMEOUT_SECONDS)
    after_status = repo.evidence()
    gate = repo.resume("resume")
    label = "Commit" if family is ReviewFamily.CODE else "Consolidate"
    confirmed = repo.exchange("confirm", "--choice-label", label, capability=gate[-1].payload)
    owning = repo.resume("resume")
    completion = repo.exchange("complete", capability=owning[-1].payload)
    released = repo.run("resume-inspect", "--role", "requestor")
    final_status = repo.exchange("status")
    workflow = subprocess.run([str(SHARED_ROOT / "bin" / "prompt_workflow.bat"), "skill"],
                              cwd=repo.root, env=session_environment(os.environ, "codex"),
                              check=False, capture_output=True, text=True,
                              timeout=PROCESS_TIMEOUT_SECONDS)
    return {"repo": repo, "writer": writer, "pending": pending, "first": first, "lost": lost,
                "stale": stale, "answer": answer, "before": before, "after_status": after_status,
                "status": status, "human": human, "gate": gate, "confirmed": confirmed, "owning": owning,
                "completion": completion, "released": released, "final_status": final_status, "workflow": workflow,
                "git_status": repo.git("status", "--porcelain"), "final_evidence": repo.evidence()}


def legacy_natures(path: Path, snapshot: dict[str, str | None] | None) -> None:
    """Seed an old or conflicting installation while preserving authored content."""
    text = path.read_text(encoding="utf-8")
    original, body = parse_json_markdown(text)
    data = dict(original)
    data.pop("role_natures", None)
    if snapshot is not None:
        data["role_natures"] = snapshot
    path.write_text(render_json_markdown(text.splitlines()[0][2:], data, body), encoding="utf-8")


def start_wait(repo: ReviewRepository, parent_pid: int | None = None) -> subprocess.Popen[str]:
    """Start the real public wait and observe completion of its startup scan.

    The waiter exits once ``parent_pid`` is gone: this test process by default.
    """
    ready = repo.root.parent / f"waiter-{uuid4().hex}.ready"
    watched = os.getpid() if parent_pid is None else parent_pid
    environment = {**module_session_environment("claude"), PARENT_VARIABLE: str(watched)}
    process = subprocess.Popen(
        [sys.executable, "-m", "tests.acceptance.review_resume.waiter_driver", str(ready),
         "wait-any-request", "--poll-interval", "0.05"],
        cwd=repo.root, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        deadline = monotonic() + PROCESS_TIMEOUT_SECONDS
        while not ready.is_file():
            assert process.poll() is None, process.communicate(timeout=5)
            remaining = deadline - monotonic()
            assert remaining > 0, "Reviewer did not reach its notification wait"
            sleep(min(0.01, remaining))
        _WAITERS[process.pid] = TrackedProcess(int(ready.read_text(encoding="utf-8")))
    except BaseException:
        stop_waiter(process)
        raise
    else:
        return process
    finally:
        ready.unlink(missing_ok=True)


def waiter_interpreter(process: subprocess.Popen[str]) -> TrackedProcess:
    """Return the real interpreter a started waiter reported."""
    return _WAITERS[process.pid]


def stop_waiter(process: subprocess.Popen[str]) -> None:
    """End a waiter's real interpreter, then its started process, then reap it.

    A waiter that never reported its interpreter exits by itself once the
    started process, its direct parent, is gone.
    """
    interpreter = _WAITERS.get(process.pid)
    if interpreter is not None:
        interpreter.kill()
    if process.poll() is None:
        process.kill()
    process.communicate(timeout=5)


@pytest.fixture(scope="session", autouse=True)
def no_surviving_waiters() -> Iterator[None]:
    """Fail the session when any started waiter interpreter is still running."""
    yield
    survivors = [interpreter.pid for interpreter in _WAITERS.values() if interpreter.alive()]
    for interpreter in _WAITERS.values():
        interpreter.kill()
        interpreter.close()
    _WAITERS.clear()
    assert not survivors, f"waiter_driver interpreters survived their tests: {survivors}"


def assert_still_quiet(process: subprocess.Popen[str]) -> None:
    """Observe bounded idle silence without sending an interrupt or consuming a claim."""
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        process.communicate(timeout=0.15)
    assert not caught.value.stdout
    assert not caught.value.stderr


def terminal_result(process: subprocess.Popen[str], streams: tuple[str, str]) -> dict[str, Any]:
    """Validate the real process and decode its one terminal result."""
    stdout, stderr = streams
    assert process.returncode == 0, (stdout, stderr)
    assert stderr == ""
    assert len(stdout.splitlines()) == 1
    return json.loads(stdout)


# eof
