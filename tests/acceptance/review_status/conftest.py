"""Real repository and durable exchange fixtures for review-status acceptance.

The builders write protocol evidence through the production models and store.
Only deliberately damaged candidates bypass those boundaries, so command-level
tests exercise the same files a returning review role would inspect.
"""

# ruff: noqa: PLR0913, S105, S603, S607

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from tools.review_artifact_configuration import ReviewArtifactConfiguration
from tools.review_exchange_models import (
    Actor,
    ConfirmationOutcome,
    CoordinationStatus,
    ExchangeIdentity,
    FamilyPolicy,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
    format_local_timestamp,
)
from tools.review_exchange_models_coordination import CoordinationRecord
from tools.review_exchange_models_envelope import (
    Envelope,
    render_envelope_markdown,
    render_json_markdown,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from collections.abc import Mapping

_SHARED_ROOT = Path(__file__).resolve().parents[3]
_LAUNCHER = _SHARED_ROOT / "rvw_status.bat"
_POLICY = FamilyPolicy("commit-ready", "Rework and review again", "Commit")
_WAIT_SECONDS = 300


@dataclass(frozen=True)
class ProcessResult:
    """One public command result with its parsed JSON payload."""

    returncode: int
    stdout: str
    stderr: str
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class RepositorySnapshot:
    """Review bytes and Git facts that status is forbidden to change."""

    protocol_hashes: Mapping[str, str]
    coordination_bytes: Mapping[str, bytes]
    marker_bytes: bytes
    git_status: str
    index_tree: str
    current_ref: str


@dataclass(frozen=True)
class CommandMatrix:
    """Process observations for populated and empty caller repositories."""

    populated_root: Path
    direct: ProcessResult
    launcher: ProcessResult
    repeated_launcher: ProcessResult
    human_launcher: subprocess.CompletedProcess[str]
    empty_direct: ProcessResult
    empty_launcher: ProcessResult
    before: RepositorySnapshot
    after: RepositorySnapshot


def _git(root: Path, *arguments: str) -> str:
    """Run one deterministic Git fixture command and return stripped output."""
    completed = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return completed.stdout.strip()


def _initialize_repository(root: Path) -> None:
    """Create one committed Git repository with realistic review ignores."""
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "--quiet")
    _git(root, "config", "user.email", "review-status@example.invalid")
    _git(root, "config", "user.name", "Review Status Acceptance")
    (root / ".gitignore").write_text(
        "a.*\ndocs/**/review.*.md\n",
        encoding="utf-8",
    )


def _commit_fixture_documents(root: Path) -> None:
    """Commit ordinary fixture documents while protocol artifacts stay ignored."""
    _git(root, "add", "-A")
    _git(root, "commit", "--quiet", "-m", "test: seed review status fixture")


def _context(
    root: Path,
    slug: str,
    *,
    family: ReviewFamily = ReviewFamily.CODE,
    with_umbrella: bool = True,
) -> ReviewContext:
    """Create one exact reviewed document and optional umbrella context."""
    docs = root / "docs" / "v0.11.0"
    docs.mkdir(parents=True, exist_ok=True)
    if family is ReviewFamily.CODE:
        type_token = "code"
        prefix = "plan"
        step = "4"
    else:
        type_token = "feature-request"
        prefix = "feature-request"
        step = None
    document = docs / f"{prefix}.v0.11.0.{slug}.md"
    document.write_text(f"# Reviewed {slug}\n", encoding="utf-8")
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    if with_umbrella:
        umbrella.write_text("# Review mode umbrella\n", encoding="utf-8")
    return ReviewContext(
        ExchangeIdentity(family, type_token, "v0.11.0", slug),
        document,
        umbrella if with_umbrella else None,
        step,
    )


def _artifact(
    context: ReviewContext,
    role: ReviewRole,
    *,
    disposition: ReviewDisposition | None = None,
) -> str:
    """Render one valid request or answer for the supplied durable identity."""
    return render_envelope_markdown(
        Envelope(
            context.identity,
            context.umbrella_path,
            context.document_path,
            context.implementation_step,
            role,
            1,
            format_local_timestamp(),
            disposition,
        ),
        "Acceptance evidence.\n",
    )


def _record(
    context: ReviewContext,
    *,
    status: CoordinationStatus = CoordinationStatus.ACTIVE,
    owner: Actor = Actor.REQUESTOR,
    expected: Actor = Actor.REVIEWER,
    renewed_at: str | None = None,
    convergence: bool | None = None,
    confirmed: bool = False,
    escalation_reason: str | None = None,
) -> CoordinationRecord:
    """Build one strict coordination record for an acceptance state."""
    confirmation_time = format_local_timestamp() if confirmed else None
    return CoordinationRecord(
        context=context,
        policy=_POLICY,
        status=status,
        owner=owner,
        expected_next_actor=expected,
        round_number=1,
        lease_renewed_at=renewed_at,
        convergence_recommended=convergence,
        escalation_reason=escalation_reason,
        confirmation_label="Commit" if confirmed else None,
        confirmed_outcome=(
            ConfirmationOutcome.CONTINUE_OWNING_WORKFLOW if confirmed else None
        ),
        confirmation_timestamp=confirmation_time,
    )


def _store(root: Path, context: ReviewContext) -> ReviewExchangeStore:
    """Create a bound store and its canonical transcript."""
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    store.initialize_transcript(context)
    return store


def _write_exchange(root: Path, slug: str, shape: str) -> Path:
    """Write one production-model exchange and return its coordination path."""
    family = ReviewFamily.SPECIFICATION if shape == "request" else ReviewFamily.CODE
    context = _context(
        root,
        slug,
        family=family,
        with_umbrella=shape != "standalone",
    )
    store = _store(root, context)
    now = format_local_timestamp()
    if shape in {"request", "standalone"}:
        store.publish_atomic(store.paths.request, _artifact(context, ReviewRole.REQUESTOR))
        record = _record(context, renewed_at=now)
    elif shape == "expired-request":
        store.publish_atomic(store.paths.request, _artifact(context, ReviewRole.REQUESTOR))
        renewed = (datetime.now().astimezone() - timedelta(hours=2)).isoformat(
            timespec="seconds",
        )
        record = _record(context, renewed_at=renewed)
    elif shape == "convergence":
        store.publish_atomic(
            store.paths.answer,
            _artifact(
                context,
                ReviewRole.REVIEWER,
                disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
            ),
        )
        record = _record(
            context,
            status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
            owner=Actor.REVIEWER,
            expected=Actor.HUMAN,
            convergence=True,
        )
    elif shape == "owning":
        record = _record(
            context,
            status=CoordinationStatus.AWAITING_HUMAN_CONFIRMATION,
            owner=Actor.REVIEWER,
            expected=Actor.HUMAN,
            convergence=True,
            confirmed=True,
        )
    elif shape == "escalated":
        store.publish_atomic(store.paths.request, _artifact(context, ReviewRole.REQUESTOR))
        record = _record(
            context,
            status=CoordinationStatus.ESCALATED,
            expected=Actor.HUMAN,
            escalation_reason="reviewer wait timed out",
        )
    elif shape == "inconsistent":
        store.publish_atomic(store.paths.request, _artifact(context, ReviewRole.REQUESTOR))
        store.publish_atomic(
            store.paths.answer,
            _artifact(
                context,
                ReviewRole.REVIEWER,
                disposition=ReviewDisposition.CHANGES_REQUESTED,
            ),
        )
        record = _record(context, renewed_at=now)
    else:  # pragma: no cover - fixture programming guard
        message = f"unknown exchange shape: {shape}"
        raise AssertionError(message)
    store.write_coordination(record)
    return store.paths.coordination


def _write_legacy_candidate(root: Path) -> None:
    """Write a coordination payload whose durable umbrella field is absent."""
    context = _context(root, "legacy-umbrella")
    store = _store(root, context)
    record = _record(context, renewed_at=format_local_timestamp())
    payload = record.to_dict()
    context_payload = cast("dict[str, object]", payload["context"])
    del context_payload["umbrella_path"]
    store.paths.coordination.write_text(
        render_json_markdown("Legacy coordination", payload, ""),
        encoding="utf-8",
    )


def _populate_repository(root: Path) -> None:
    """Create the complete healthy and damaged acceptance scenario matrix."""
    artifacts = ReviewArtifactConfiguration.load(root)
    artifacts.prepare_home()
    (artifacts.home / "a.review-mode").write_text(
        f"wait_timeout_seconds={_WAIT_SECONDS}\n",
        encoding="utf-8",
    )
    _write_exchange(root, "spec-request", "request")
    _write_exchange(root, "standalone", "standalone")
    _write_exchange(root, "convergence", "convergence")
    _write_exchange(root, "authorized", "owning")
    _write_exchange(root, "wait-timeout", "escalated")
    _write_exchange(root, "expired", "expired-request")
    _write_exchange(root, "inconsistent", "inconsistent")
    _write_legacy_candidate(root)
    (root / "a.review-active.malformed.md").write_text(
        "not coordination markdown\n",
        encoding="utf-8",
    )


def _environment() -> dict[str, str]:
    """Return an environment that imports this checkout from any caller root."""
    environment = os.environ.copy()
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(_SHARED_ROOT)
        if not existing
        else f"{_SHARED_ROOT}{os.pathsep}{existing}"
    )
    return environment


def _run_json(command: list[str], cwd: Path) -> ProcessResult:
    """Run one public JSON command without requiring a zero process status."""
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    payload = cast("Mapping[str, Any]", json.loads(completed.stdout))
    return ProcessResult(
        completed.returncode,
        completed.stdout,
        completed.stderr,
        payload,
    )


def _direct_command() -> list[str]:
    """Return the direct shared-module command using the active test runtime."""
    return [sys.executable, "-P", "-m", "tools.review_status_cli", "--format", "json"]


def _launcher_command(*arguments: str) -> list[str]:
    """Return the real root launcher command."""
    return [str(_LAUNCHER), *arguments]


def _protocol_hashes(root: Path) -> dict[str, str]:
    """Hash every review marker, transient, and versioned transcript."""
    selected = (
        path
        for path in root.rglob("*")
        if path.is_file()
        and (path.name.startswith("a.review") or path.name.startswith("review."))
    )
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(selected)
    }


def _snapshot(root: Path) -> RepositorySnapshot:
    """Capture the complete read-only acceptance boundary."""
    artifacts = ReviewArtifactConfiguration.load(root)
    coordination = {
        path.name: path.read_bytes()
        for path in sorted(artifacts.home.glob("a.review-active*"))
    }
    return RepositorySnapshot(
        protocol_hashes=_protocol_hashes(root),
        coordination_bytes=coordination,
        marker_bytes=(artifacts.home / "a.review-mode").read_bytes(),
        git_status=_git(root, "status", "--porcelain"),
        index_tree=_git(root, "write-tree"),
        current_ref=_git(root, "rev-parse", "HEAD"),
    )


@pytest.fixture(scope="module")
def command_matrix(tmp_path_factory: pytest.TempPathFactory) -> CommandMatrix:
    """Run both public entry points over populated and empty repositories."""
    populated = tmp_path_factory.mktemp("review-status-populated")
    empty = tmp_path_factory.mktemp("review-status-empty")
    _initialize_repository(populated)
    _populate_repository(populated)
    _commit_fixture_documents(populated)
    nested = populated / "nested" / "caller"
    nested.mkdir(parents=True)
    before = _snapshot(populated)
    direct = _run_json(_direct_command(), nested)
    launcher = _run_json(_launcher_command("--format", "json"), nested)
    repeated = _run_json(_launcher_command("--format", "json"), nested)
    human = subprocess.run(
        _launcher_command(),
        cwd=nested,
        env=_environment(),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    after = _snapshot(populated)

    _initialize_repository(empty)
    _commit_fixture_documents(empty)
    empty_nested = empty / "nested"
    empty_nested.mkdir()
    empty_direct = _run_json(_direct_command(), empty_nested)
    empty_launcher = _run_json(_launcher_command("--format", "json"), empty_nested)
    return CommandMatrix(
        populated,
        direct,
        launcher,
        repeated,
        human,
        empty_direct,
        empty_launcher,
        before,
        after,
    )


@pytest.fixture
def migration_repositories(tmp_path: Path) -> tuple[Path, Path, bytes]:
    """Create safe-required and collision-blocked root artifact layouts."""
    completed = tmp_path / "completed"
    blocked = tmp_path / "blocked"
    expected = f"wait_timeout_seconds={_WAIT_SECONDS}\n".encode()
    for root in (completed, blocked):
        _initialize_repository(root)
        artifacts = ReviewArtifactConfiguration.load(root)
        artifacts.prepare_home()
        (artifacts.home / "a.review-mode").write_bytes(expected)
        _commit_fixture_documents(root)
    completed_target = completed / ".reviews" / "a.review-mode"
    completed_target.replace(completed / "a.review-mode")
    (blocked / "a.review-mode").write_text(
        "wait_timeout_seconds=999\n",
        encoding="utf-8",
    )
    return completed, blocked, expected


@pytest.fixture
def changing_repository(tmp_path: Path) -> tuple[Path, Path, bytes]:
    """Create one candidate for deterministic changed-during-read simulation."""
    root = tmp_path / "changing"
    _initialize_repository(root)
    ReviewArtifactConfiguration.load(root).prepare_home()
    candidate = _write_exchange(root, "changing", "request")
    _commit_fixture_documents(root)
    return root, candidate, candidate.read_bytes()
