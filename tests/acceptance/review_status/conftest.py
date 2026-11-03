"""Declared repository observations and durable review-status evidence.

The builders render typed prerequisite records directly to files. Status still
reads and validates those files through production code; fixture construction
does not replay publication transactions unrelated to the read-only contract.
Repository observations replace native Git; no synthetic commit is created.
Tracked prerequisite bytes are declared while writing their documents, so setup
does not traverse and reread the complete protocol tree to create a baseline.
Transcript prerequisites render the real template without an unrelated atomic
publication transaction. Every status read and before/after snapshot stays live.
"""

# ruff: noqa: PLR0913, S105, S603, S607

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cache, cached_property
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Any, cast

import pytest

from tests.acceptance.review_resume.cli_support import run_inline
from tests.review_repository_observations import ReviewRepositories
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
    import subprocess
    from collections.abc import Callable, Iterator, Mapping

_SHARED_ROOT = Path(__file__).resolve().parents[3]
_POLICY = FamilyPolicy("commit-ready", "Rework and review again", "Commit")
_WAIT_SECONDS = 300
_REPOSITORIES = ReviewRepositories()


@pytest.fixture(scope="package", autouse=True)
def declared_repositories() -> Iterator[None]:
    """Inject repository facts for every fixture and direct service call."""
    _REPOSITORIES.repositories.clear()
    with pytest.MonkeyPatch.context() as patch:
        _REPOSITORIES.install(patch)
        yield
    _REPOSITORIES.repositories.clear()


@dataclass(frozen=True)
class ProcessResult:
    """One public command result with its parsed JSON payload."""

    returncode: int
    stdout: str
    stderr: str
    payload: Mapping[str, Any]


@dataclass(frozen=True)
class RepositorySnapshot:
    """Review bytes and tracked content that status is forbidden to change."""

    protocol_hashes: Mapping[str, str]
    coordination_bytes: Mapping[str, bytes]
    marker_bytes: bytes
    git_status: str


@dataclass(frozen=True)
class CommandMatrix:
    """Lazily execute only the status observations asserted by this test."""

    populated_root: Path

    @cached_property
    def before(self) -> RepositorySnapshot:
        """Capture the baseline only for a test asserting nonmutation."""
        return _snapshot(self.populated_root)

    @cached_property
    def direct(self) -> ProcessResult:
        """Run the JSON entry from the nested caller."""
        return _run_json(["--format", "json"], self.populated_root / "nested/caller")

    @cached_property
    def repeated(self) -> ProcessResult:
        """Repeat JSON status to prove idempotence."""
        return _run_json(["--format", "json"], self.populated_root / "nested/caller")

    @cached_property
    def human(self) -> subprocess.CompletedProcess[str]:
        """Render the same repository through the human entry point."""
        return run_inline((), self.populated_root / "nested/caller", _environment(), entry="status")

    @property
    def after(self) -> RepositorySnapshot:
        """Observe evidence after the commands actually exercised by the test."""
        return _snapshot(self.populated_root)


def _initialize_repository(root: Path) -> None:
    """Declare a repository marker and review ignore inputs."""
    root.mkdir(parents=True, exist_ok=True)
    _REPOSITORIES.register(root, {".gitignore": b"a.*\ndocs/**/review.*.md\n"})
    (root / ".gitignore").write_bytes(b"a.*\ndocs/**/review.*.md\n")


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
    content = f"# Reviewed {slug}\n".encode()
    document.write_bytes(content)
    tracked = _REPOSITORIES.repositories[root.resolve()].tracked
    tracked[document.relative_to(root).as_posix()] = content
    umbrella = docs / "draft.v0.11.0.review-mode.md"
    if with_umbrella:
        umbrella.write_bytes(b"# Review mode umbrella\n")
        tracked[umbrella.relative_to(root).as_posix()] = b"# Review mode umbrella\n"
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


@cache
def _transcript_template(family: ReviewFamily) -> Template:
    """Read immutable template bytes lazily in the first measured fixture."""
    name = "review-code-transcript.template.md" if family is ReviewFamily.CODE else "review-specification-transcript.template.md"
    return Template((_SHARED_ROOT / "templates" / name).read_text(encoding="utf-8"))


def _store(root: Path, context: ReviewContext) -> ReviewExchangeStore:
    """Declare the canonical transcript consumed by the real status service."""
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    store.paths.transcript.write_text(_transcript_template(context.identity.family).substitute(
        version=context.identity.version, exchange_identity=context.identity.key,
        reviewed_document=context.document_path.relative_to(root).as_posix(),
    ), encoding="utf-8")
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
        store.paths.request.write_text(_artifact(context, ReviewRole.REQUESTOR), encoding="utf-8")
        record = _record(context, renewed_at=now)
    elif shape == "expired-request":
        store.paths.request.write_text(_artifact(context, ReviewRole.REQUESTOR), encoding="utf-8")
        renewed = (datetime.now().astimezone() - timedelta(hours=2)).isoformat(
            timespec="seconds",
        )
        record = _record(context, renewed_at=renewed)
    elif shape == "convergence":
        store.paths.answer.write_text(
            _artifact(
                context,
                ReviewRole.REVIEWER,
                disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
            ),
            encoding="utf-8",
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
        store.paths.request.write_text(_artifact(context, ReviewRole.REQUESTOR), encoding="utf-8")
        record = _record(
            context,
            status=CoordinationStatus.ESCALATED,
            expected=Actor.HUMAN,
            escalation_reason="reviewer wait timed out",
        )
    elif shape == "inconsistent":
        store.paths.request.write_text(_artifact(context, ReviewRole.REQUESTOR), encoding="utf-8")
        store.paths.answer.write_text(
            _artifact(
                context,
                ReviewRole.REVIEWER,
                disposition=ReviewDisposition.CHANGES_REQUESTED,
            ),
            encoding="utf-8",
        )
        record = _record(context, renewed_at=now)
    else:  # pragma: no cover - fixture programming guard
        message = f"unknown exchange shape: {shape}"
        raise AssertionError(message)
    title = f"Review exchange coordination for {context.identity.key}"
    store.paths.coordination.write_text(render_json_markdown(title, record.to_dict(), ""), encoding="utf-8")
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


def _populate_repository(root: Path, slugs: tuple[str, ...] | None = None) -> None:
    """Create the selected independent states plus neighboring damaged evidence."""
    artifacts = ReviewArtifactConfiguration.load(root)
    artifacts.prepare_home()
    (artifacts.home / "a.review-mode").write_text(
        f"wait_timeout_seconds={_WAIT_SECONDS}\n",
        encoding="utf-8",
    )
    shapes = {"spec-request": "request", "standalone": "standalone", "convergence": "convergence",
              "authorized": "owning", "wait-timeout": "escalated", "expired": "expired-request",
              "inconsistent": "inconsistent"}
    for slug in shapes if slugs is None else slugs:
        _write_exchange(root, slug, shapes[slug])
    _write_legacy_candidate(root)
    (root / "a.review-active.malformed.md").write_text(
        "not coordination markdown\n",
        encoding="utf-8",
    )


def _environment() -> dict[str, str]:
    """Return an environment that imports this checkout from any caller root."""
    environment = os.environ.copy()
    environment.update(COLUMNS="80", LINES="24")
    existing = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        str(_SHARED_ROOT)
        if not existing
        else f"{_SHARED_ROOT}{os.pathsep}{existing}"
    )
    return environment


def _run_json(command: list[str], cwd: Path) -> ProcessResult:
    """Run one public JSON command without requiring a zero process status."""
    completed = run_inline(tuple(command), cwd, _environment(), entry="status")
    payload = cast("Mapping[str, Any]", json.loads(completed.stdout))
    return ProcessResult(
        completed.returncode,
        completed.stdout,
        completed.stderr,
        payload,
    )


def _protocol_hashes(root: Path) -> dict[str, str]:
    """Hash every review marker, transient, and versioned transcript."""
    hashes: dict[str, str] = {}
    for directory, _subdirectories, filenames in os.walk(root):
        parent = Path(directory)
        relative = parent.relative_to(root)
        for filename in filenames:
            if filename.startswith(("a.review", "review.")):
                hashes[(relative / filename).as_posix()] = hashlib.sha256((parent / filename).read_bytes()).hexdigest()
    return hashes


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
        git_status=str(_REPOSITORIES.repositories[root.resolve()].changes() or ""),
    )


def _populated_commands(populated: Path, slugs: tuple[str, ...] | None = None) -> CommandMatrix:
    """Prepare independent state; each test pays for its own asserted commands."""
    _initialize_repository(populated)
    _populate_repository(populated, slugs)
    nested = populated / "nested" / "caller"
    nested.mkdir(parents=True)
    return CommandMatrix(populated)


def _empty_command(empty: Path) -> ProcessResult:
    """Run the production Python entry with an empty repository."""
    _initialize_repository(empty)
    empty_nested = empty / "nested"
    empty_nested.mkdir()
    return _run_json(["--format", "json"], empty_nested)


@pytest.fixture
def command_matrix(
    tmp_path: Path, request: pytest.FixtureRequest,
    stable_review_inputs: Callable[[], None],
) -> CommandMatrix:
    """Cache fixed configuration; every protocol read and snapshot stays live."""
    matrix = _populated_commands(tmp_path / "populated", getattr(request, "param", None))
    stable_review_inputs()
    return matrix


@pytest.fixture
def empty_command(tmp_path: Path) -> ProcessResult:
    """Empty status has no dependency on the populated matrix."""
    return _empty_command(tmp_path / "empty")


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
    return root, candidate, candidate.read_bytes()
