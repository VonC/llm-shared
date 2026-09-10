"""Real Git repositories and separate public-launcher sessions for resume acceptance.

Scenario setup runs outside measured calls; the tests retain assertions over
actual process results, protocol bytes, Git state and fenced capabilities,
including status failure JSON delivered on the error stream.

Fix: the independent-waiter helpers moved here from the concurrency module.
That module was split so its scenarios run on separate xdist workers, and both
halves need the same process start, idle-silence and terminal-result helpers.
"""

# ruff: noqa: S603, S607, PLR0913
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from tests.unit.tools.review_exchange_test_support import (
    capability_arguments,
    common_arguments,
    configured_home,
    review_artifact,
    review_context,
    session_environment,
)
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

SHARED_ROOT = Path(__file__).resolve().parents[3]
EXCHANGE_LAUNCHER = SHARED_ROOT / "bin" / "review_exchange.bat"
EXCHANGE_MODULE = ("-m", "tools.review_exchange_cli")


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


class ReviewRepository:
    """Build real repositories while every scenario transition uses the public launcher."""

    def __init__(self, root: Path, *, home: str = ".reviews", family: ReviewFamily = ReviewFamily.CODE) -> None:
        """Seed ordinary Git documents and an ignored runtime home."""
        self.root = root
        root.mkdir(parents=True)
        self.git("init", "-q", "-b", "resume-acceptance")
        self.git("config", "user.name", "Resume Acceptance")
        self.git("config", "user.email", "resume@example.invalid")
        (root / ".gitignore").write_text("a.*\ndocs/**/review.*.md\n", encoding="utf-8")
        self.home = configured_home(root, home)
        (self.home / "a.review-mode").write_text("wait_timeout_seconds=300\n", encoding="utf-8")
        self.context = review_context(root, family, "resume-acceptance", step="6" if family is ReviewFamily.CODE else None)
        self.paths = derive_artifact_paths(root, self.context)
        docs = self.context.document_path.parent
        (docs / "draft.v0.11.0.resume-acceptance.md").write_text("# Resume acceptance draft\n", encoding="utf-8")
        (docs / "feature-request.v0.11.0.resume-acceptance.md").write_text("# Resume acceptance requirement\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-qm", "test: seed resume acceptance")

    def git(self, *arguments: str) -> str:
        """Keep setup and Git observations on bounded real subprocesses."""
        result = subprocess.run(["git", *arguments], cwd=self.root, check=True,
                                capture_output=True, text=True, timeout=20)
        return result.stdout.strip()

    def run(self, *arguments: str, nature: str = "codex", launcher: Path | None = None) -> ProcessResult:
        """Execute one real, isolated public entry point with a fresh host environment.

        The exchange operations run as ``python -m tools.review_exchange_cli``
        rather than through ``review_exchange.bat``. Both spawn a real separate
        process over the same CLI, but the batch form spawns ``cmd.exe`` first
        and then a second process for Python, which doubled process creation on
        the hottest path of the suite. ``rvw_status.bat`` and
        ``prompt_workflow.bat`` are still driven through their batch launchers,
        so the shipped shims keep their acceptance coverage.
        """
        command = ([str(launcher), *arguments] if launcher is not None
                   else [sys.executable, *EXCHANGE_MODULE, *arguments])
        result = subprocess.run(command, cwd=self.root,
                                env=module_session_environment(nature), check=False,
                                capture_output=True, text=True, timeout=30)
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
               capability: dict[str, Any] | None = None, override: bool = False) -> list[ProcessResult]:
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
                                "--occurrence", str(candidate["occurrence"]), *ownership, nature=nature))
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
                            home=".reviews" if family is ReviewFamily.CODE else "runtime/reviews")
    writer = repo.start_request()
    pending = repo.resume("resume")
    first = repo.resume("resume", role="reviewer", nature="claude")
    lost = repo.resume("resume", nature="claude")
    stale = repo.publish(ReviewRole.REVIEWER, first[-1].payload, nature="claude")
    answer = repo.publish(ReviewRole.REVIEWER, lost[-1].payload, ready=True, nature="claude")
    before = repo.evidence()
    status = repo.run("--format", "json", launcher=SHARED_ROOT / "rvw_status.bat")
    human = subprocess.run([str(SHARED_ROOT / "rvw_status.bat")], cwd=repo.root,
                           env=session_environment(os.environ, "codex"), check=False,
                           capture_output=True, text=True, timeout=30)
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
                              check=False, capture_output=True, text=True, timeout=30)
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


def start_wait(repo: ReviewRepository) -> subprocess.Popen[str]:
    """Start an independent reviewer process using only the identity-free public operation."""
    return subprocess.Popen([sys.executable, *EXCHANGE_MODULE, "wait-any-request", "--poll-interval", "0.05"],
                            cwd=repo.root, env=module_session_environment("claude"),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


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
