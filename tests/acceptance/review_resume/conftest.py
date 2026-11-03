"""Public review CLI scenarios with declared repository data and virtual notifications.

Each invocation creates fresh production CLI state and restores caller globals.
Setup, calls and teardown all count toward the lifecycle duration gate.
Repository instances write immutable declared seed bytes directly, avoiding
repeated tree walks and metadata copies while retaining independent real files.
"""

# ruff: noqa: S603, S607, PLR0913
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.acceptance.review_resume.cli_support import run_inline
from tests.acceptance.review_resume.notification_simulation import NotificationSchedule
from tests.acceptance.review_resume.prepared_request import prepare_request
from tests.review_repository_observations import ReviewRepositories
from tests.unit.tools.review_exchange_test_support import (
    capability_arguments,
    common_arguments,
    review_artifact,
    review_policy,
    session_environment,
)
from tools import review_exchange_cli_resume
from tools.llm_nature import LlmNature
from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ExchangeIdentity,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_models_envelope import (
    parse_json_markdown,
    render_json_markdown,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.review_resume_identity import claim_selected

if TYPE_CHECKING:
    from collections.abc import Iterator

SHARED_ROOT = Path(__file__).resolve().parents[3]
EXCHANGE_LAUNCHER = SHARED_ROOT / "bin" / "review_exchange.bat"
REPOSITORIES = ReviewRepositories()


def module_session_environment(nature: str) -> dict[str, str]:
    """Isolate the declared host environment for one CLI invocation."""
    environment = session_environment(os.environ, nature)
    # Argparse queries terminal dimensions for every argument formatter.
    # These JSON scenarios have no interactive terminal; use its supported
    # environment configuration instead of repeated native console queries.
    environment.update(COLUMNS="80", LINES="24")
    previous = environment.get("PYTHONPATH")
    root = str(SHARED_ROOT)
    environment["PYTHONPATH"] = f"{root}{os.pathsep}{previous}" if previous else root
    return environment


@dataclass(frozen=True)
class ProcessResult:
    """One CLI invocation's exit code, streams and sole decoded machine result."""

    code: int
    stdout: str
    stderr: str
    payload: dict[str, Any]


@pytest.fixture(scope="package", autouse=True)
def declared_repositories() -> Iterator[None]:
    """Provide read-only repository observations during all acceptance fixtures."""
    REPOSITORIES.repositories.clear()
    _SEEDS.clear()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(os, "environ", dict(os.environ))
        REPOSITORIES.install(patch)
        patch.setattr(review_exchange_cli_resume, "WatchdogNotificationAdapter", NotificationSchedule().adapter)
        yield
    REPOSITORIES.repositories.clear()


@dataclass(frozen=True)
class _Seed:
    """Immutable file bytes declared once for independent repository scenarios."""

    document: str
    tracked: dict[str, bytes]
    files: dict[str, bytes]
    parents: tuple[Path, ...]

    @classmethod
    def build(cls, home: str, family: ReviewFamily) -> _Seed:
        """Declare bytes without writing, traversing and rereading a template tree."""
        stem = "docs/v0.11.0/"
        prefix = "plan" if family is ReviewFamily.CODE else "feature-request"
        document = f"{stem}{prefix}.v0.11.0.resume-acceptance.md"
        tracked = {
            ".gitignore": b"a.*\ndocs/**/review.*.md\n",
            ".review-exchange.ini": b"[review-exchange]\nwait_timeout_seconds = 300\n",
            document: b"# resume-acceptance\n",
            f"{stem}draft.v0.11.0.resume-acceptance.md": b"# Resume acceptance draft\n",
            f"{stem}feature-request.v0.11.0.resume-acceptance.md": b"# Resume acceptance requirement\n",
        }
        if home != ".reviews":
            tracked[".review-artifacts.ini"] = f"[review-artifacts]\nhome = {home}\n".encode()
        files = {**tracked, f"{home}/.gitignore": b"*\n",
                 f"{home}/a.review-mode": b"wait_timeout_seconds=300\n"}
        return cls(document, tracked, files, tuple({Path(relative).parent for relative in files}))


# Lazy immutable bytes, initialized inside the first requesting test.
_SEEDS: dict[tuple[str, ReviewFamily], _Seed] = {}


def _seeded(home: str, family: ReviewFamily) -> _Seed:
    """Return the declared template for one artifact home and review family."""
    key = (home, family)
    if key not in _SEEDS:
        _SEEDS[key] = _Seed.build(home, family)
    return _SEEDS[key]


class ReviewRepository:
    """Prepare core prerequisites and exercise resume through the public CLI."""

    def __init__(self, root: Path, *, home: str = ".reviews", family: ReviewFamily = ReviewFamily.CODE) -> None:
        """Write declared seed bytes without traversing or copying a repository tree."""
        seed = _seeded(home, family)
        root.mkdir(parents=True)
        for parent in seed.parents:
            (root / parent).mkdir(parents=True, exist_ok=True)
        for relative, content in seed.files.items():
            target = root / relative
            target.write_bytes(content)
        self.root = root
        self.facts = REPOSITORIES.register(root, seed.tracked)
        configuration = ReviewArtifactConfiguration.load(root)
        self.home = configuration.home
        token = "code" if family is ReviewFamily.CODE else "feature-request"
        self.context = ReviewContext(
            ExchangeIdentity(family, token, "v0.11.0", "resume-acceptance"),
            root / seed.document, None, "6" if family is ReviewFamily.CODE else None,
        )
        self.paths = derive_artifact_paths(root, self.context, configuration=configuration)

    def run(self, *arguments: str, nature: str = "codex", launcher: Path | None = None) -> ProcessResult:
        """Call the selected public Python entry with restored caller state."""
        environment = module_session_environment(nature)
        entry = "status" if launcher is not None and launcher.name == "rvw_status.bat" else "exchange"
        result = run_inline(arguments, self.root, environment, entry=entry)
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
        """Declare a pending request without replaying protocol prerequisites."""
        return prepare_request(self, nature)

    def resume(self, prompt: str, *, role: str | None = None, nature: str = "codex",
               capability: dict[str, Any] | None = None, override: bool = False) -> list[ProcessResult]:
        """Simulate bare-text orchestration; instruction tests separately bind this driver."""
        assert prompt == "resume"
        results = self._migration_preflight(nature)
        if results[-1].payload["outcome"] != "ready":
            return results
        return results + self.resume_selected(role=role, nature=nature, capability=capability, override=override)

    def resume_selected(self, *, role: str | None = None, nature: str = "codex",
                        capability: dict[str, Any] | None = None, override: bool = False) -> list[ProcessResult]:
        """Inspect and claim an explicitly current layout without migration preflight."""
        selection = self._resume_selection(role, nature, override=override)
        inspected = self.run("resume-inspect", *selection, nature=nature)
        results = [inspected]
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

    def claim_known(self, *, role: str = "requestor", nature: str = "codex",
                    capability: dict[str, Any] | None = None, override: bool = False) -> ProcessResult:
        """Claim a declared first round prerequisite without rediscovering it."""
        selection = self._resume_selection(role, nature, override=override)
        ownership = [] if capability is None else capability_arguments(capability)
        return self.run("claim", *selection, "--round", "1", "--occurrence", "1", *ownership, nature=nature)

    def prepare_reviewer(self) -> dict[str, Any]:
        """Acquire a prerequisite through the same identity transaction as CLI claim."""
        core = ReviewExchangeCore(ReviewExchangeStore(self.paths), self.context,
                                  review_policy(self.context), ReviewConfiguration(enabled=True))
        capability = claim_selected(core, ReviewRole.REVIEWER, LlmNature.CLAUDE,
                                    round_number=1, occurrence=1, override=False)
        return {"ownership_generation": capability.generation, "ownership_token": capability.token}

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
    """Provide independent repository data inside the measured lifecycle."""
    return ReviewRepository(tmp_path / "caller")


def legacy_natures(path: Path, snapshot: dict[str, str | None] | None) -> None:
    """Seed an old or conflicting installation while preserving authored content."""
    text = path.read_text(encoding="utf-8")
    original, body = parse_json_markdown(text)
    data = dict(original)
    data.pop("role_natures", None)
    if snapshot is not None:
        data["role_natures"] = snapshot
    path.write_text(render_json_markdown(text.splitlines()[0][2:], data, body), encoding="utf-8")


# eof
