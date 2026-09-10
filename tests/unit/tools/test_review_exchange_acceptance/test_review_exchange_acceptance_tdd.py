"""Integrated acceptance coverage for the public review-exchange boundaries.

Step 5 composes the command adapter, recorded Git ignore resolution, exact artifact
paths, multi-round lifecycle, convergence choices, archives, and deterministic
wait reporting in temporary consuming repositories. Public commands run
in-process while preserving their JSON and environment boundaries. Step 6 shares
the exact context and artifact builders with real public-launcher acceptance.
"""

from __future__ import annotations

import json
import os
import re
from contextlib import chdir, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

import pytest

from tests.unit.tools.review_exchange_test_support import (
    common_arguments as _common,
)
from tests.unit.tools.review_exchange_test_support import (
    review_artifact as _artifact,
)
from tests.unit.tools.review_exchange_test_support import (
    review_context as _context,
)
from tests.unit.tools.review_exchange_test_support import (
    review_policy as _policy,
)
from tools import review_exchange_cli as cli
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactPaths,
    ReviewConfiguration,
    ReviewContext,
    ReviewDisposition,
    ReviewFamily,
    ReviewRole,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Sequence

_EXPECTED_STOP = 3
_SECOND_ROUND = 2
_WAIT_LIMIT = 4
_CAPABILITIES: dict[Path, tuple[int, str]] = {}


@dataclass(frozen=True)
class CliResult:
    """One parsed CLI subprocess result."""

    code: int
    payload: dict[str, Any]


@dataclass(frozen=True)
class IsolationJourney:
    """Observable results for activation and concurrent identity acceptance."""

    disabled: CliResult
    unignored: CliResult
    specification_status: CliResult
    code_status: CliResult
    duplicate_start: CliResult
    specification: ReviewContext
    code: ReviewContext


@dataclass(frozen=True)
class CodeJourney:
    """Observable results for a complete multi-round implementation exchange."""

    gate: CliResult
    first_confirmation: CliResult
    replayed_confirmation: CliResult
    owning_status: CliResult
    completion: CliResult
    paths: Any
    transcript: str


@dataclass(frozen=True)
class ResolutionJourney:
    """Observable results for human guidance and archived fresh resumption."""

    override: CliResult
    publication: CliResult
    escalation: CliResult
    resolution: CliResult
    paths: Any
    transcript: str


def _init_repo(root: Path, *, ignored: bool = True, marker: bool = True) -> None:
    """Create the filesystem shape consumed by the recorded Git boundary."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir()
    if ignored:
        (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    if marker:
        (root / "a.review-mode").write_text("", encoding="utf-8")


def _run_cli(
    root: Path,
    context: ReviewContext,
    operation: str,
    extra: Sequence[str] = (),
) -> CliResult:
    """Invoke the public command adapter and preserve its JSON boundary."""
    stdout, stderr = StringIO(), StringIO()
    capability = _CAPABILITIES.get(context.document_path)
    capability_arguments: tuple[str, ...] = ()
    if capability is not None and operation not in {"activate", "status"}:
        generation, token = capability
        capability_arguments = (
            "--ownership-generation",
            str(generation),
            "--ownership-token",
            token,
        )
    with (
        chdir(root),
        redirect_stdout(stdout),
        redirect_stderr(stderr),
        patch.dict(os.environ, {"PRJ_DIR": str(root)}),
    ):
        code = cli.main(
            [operation, *_common(context), *capability_arguments, *extra],
        )
    stdout_lines = tuple(stdout.getvalue().splitlines())
    assert len(stdout_lines) == 1, stderr.getvalue()
    payload: dict[str, Any] = json.loads(stdout_lines[0])
    generation = payload.get("ownership_generation")
    token = payload.get("ownership_token")
    if isinstance(generation, int) and isinstance(token, str):
        _CAPABILITIES[context.document_path] = (generation, token)
    if payload.get("state") == "idle":
        _CAPABILITIES.pop(context.document_path, None)
    return CliResult(code, payload)


def _input(root: Path, name: str, content: str) -> Path:
    """Write one caller-owned ignored input file and return its exact path."""
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    path = home / f"a.{name}.md"
    path.write_text(content, encoding="utf-8")
    return path


def _publish(
    context: ReviewContext,
    role: ReviewRole,
    round_number: int,
    *,
    disposition: ReviewDisposition | None = None,
    guidance: str | None = None,
) -> CliResult:
    """Publish one role artifact through the real subprocess boundary."""
    root = context.document_path.parents[2]
    content = _input(
        root,
        "acceptance-content",
        _artifact(
            context,
            role,
            round_number,
            disposition=disposition,
            guidance=guidance,
        ),
    )
    report = _input(
        root,
        "acceptance-report",
        f"{role.value} report for round {round_number}.",
    )
    operation = "publish-request" if role is ReviewRole.REQUESTOR else "publish-answer"
    return _run_cli(
        root,
        context,
        operation,
        ("--content-file", str(content), "--summary-file", str(report)),
    )


@pytest.fixture
def isolation_journey(tmp_path: Path) -> IsolationJourney:
    """Run activation failures and two independent public exchanges."""
    disabled_root = tmp_path / "disabled"
    _init_repo(disabled_root, marker=False)
    disabled_context = _context(disabled_root, ReviewFamily.CODE, "disabled", step="5")
    disabled = _run_cli(disabled_root, disabled_context, "activate")

    unignored_root = tmp_path / "unignored"
    _init_repo(unignored_root, ignored=False)
    unignored_context = _context(unignored_root, ReviewFamily.CODE, "unignored", step="5")
    unignored = _run_cli(unignored_root, unignored_context, "activate")

    active_root = tmp_path / "active"
    _init_repo(active_root)
    specification = _context(active_root, ReviewFamily.SPECIFICATION, "specification")
    code = _context(active_root, ReviewFamily.CODE, "implementation", step="5")
    assert _run_cli(active_root, specification, "start").code == 0
    assert _run_cli(active_root, code, "start").code == 0
    duplicate_start = _run_cli(active_root, code, "start")
    assert _publish(specification, ReviewRole.REQUESTOR, 1).code == 0
    specification_status = _run_cli(active_root, specification, "status")
    code_status = _run_cli(active_root, code, "status")
    return IsolationJourney(
        disabled,
        unignored,
        specification_status,
        code_status,
        duplicate_start,
        specification,
        code,
    )


def test_opt_in_git_protocol_and_exact_identity_isolation(
    isolation_journey: IsolationJourney,
) -> None:
    """Activation is inert by default and isolates Git-backed exchanges."""
    _assert_activation_failures(isolation_journey)
    _assert_identity_isolation(isolation_journey)


def _assert_activation_failures(journey: IsolationJourney) -> None:
    """Check disabled, home-covered, and duplicate-start outcomes."""
    actual = (
        journey.disabled.code,
        journey.disabled.payload["outcome"],
        journey.unignored.code,
        journey.duplicate_start.code,
    )
    assert actual == (
        _EXPECTED_STOP,
        "disabled",
        0,
        _SECOND_ROUND,
    )
    assert journey.unignored.payload["outcome"] == "activated"


def _assert_identity_isolation(journey: IsolationJourney) -> None:
    """Check independent states and the intentional code.code identity path."""
    assert journey.specification_status.payload["state"] == "request-pending"
    assert journey.code_status.payload["state"] == "round-in-progress"
    code_paths = derive_artifact_paths(journey.code.document_path.parents[2], journey.code)
    assert ".code.code." in code_paths.coordination.name
    assert journey.specification.identity != journey.code.identity


@pytest.fixture
def code_journey(tmp_path: Path) -> CodeJourney:
    """Run two code rounds through convergence and replayed owning authorization."""
    root = tmp_path / "code-journey"
    _init_repo(root)
    context = _context(root, ReviewFamily.CODE, "multi-round", step="5")
    paths = derive_artifact_paths(root, context)
    assert _run_cli(root, context, "start").code == 0
    assert _publish(context, ReviewRole.REQUESTOR, 1).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CHANGES_REQUESTED,
    ).code == 0
    consumed = _run_cli(
        root,
        context,
        "consume-answer",
        ("--reviewed-work-changed", "true"),
    )
    assert consumed.code == 0
    assert _run_cli(root, context, "continue").payload["round"] == _SECOND_ROUND
    assert _publish(context, ReviewRole.REQUESTOR, _SECOND_ROUND).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        _SECOND_ROUND,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    ).code == _EXPECTED_STOP
    gate = _run_cli(root, context, "status")
    first_confirmation = _run_cli(root, context, "confirm", ("--choice-label", "Commit"))
    replayed_confirmation = _run_cli(
        root,
        context,
        "confirm",
        ("--choice-label", "Commit"),
    )
    owning_status = _run_cli(root, context, "status")
    completion = _run_cli(root, context, "complete")
    transcript = paths.transcript.read_text(encoding="utf-8")
    return CodeJourney(
        gate,
        first_confirmation,
        replayed_confirmation,
        owning_status,
        completion,
        paths,
        transcript,
    )


def test_multiround_convergence_and_cross_session_authorization_replay(
    code_journey: CodeJourney,
) -> None:
    """Intermediate automation ends only after replayable human authorization."""
    _assert_owning_authorization(code_journey)
    _assert_code_transcript_order(code_journey)


def _assert_owning_authorization(journey: CodeJourney) -> None:
    """Check convergence, replay, and idempotent owning completion."""
    actual = (
        journey.gate.code,
        journey.gate.payload["state"],
        journey.first_confirmation.payload["owning_action_authorized"],
        journey.replayed_confirmation.payload["owning_action_authorized"],
        journey.owning_status.payload["state"],
        journey.completion.code,
        journey.completion.payload["state"],
    )
    assert actual == (
        _EXPECTED_STOP,
        "convergence-gate",
        True,
        True,
        "owning-action-pending",
        0,
        "idle",
    )
    assert not any((journey.paths.answer.exists(), journey.paths.coordination.exists()))


def _assert_code_transcript_order(journey: CodeJourney) -> None:
    """Check round order, stable confirmation identity, and offset timestamps."""
    ordered = [
        journey.transcript.index("request-step-5-round-1"),
        journey.transcript.index("answer-step-5-round-1"),
        journey.transcript.index("request-step-5-round-2"),
        journey.transcript.index("answer-step-5-round-2"),
        journey.transcript.index("human-confirmation-round-2"),
    ]
    assert ordered == sorted(ordered)
    assert journey.transcript.count("human-confirmation-round-2") == 1
    assert re.search(r"Recorded: .*[-+]\d\d:\d\d", journey.transcript)


@pytest.fixture
def resolution_journey(tmp_path: Path) -> ResolutionJourney:
    """Run a specification override, escalation, archive, and fresh resumption."""
    root = tmp_path / "resolution-journey"
    _init_repo(root)
    context = _context(root, ReviewFamily.SPECIFICATION, "human-resolution")
    paths = derive_artifact_paths(root, context)
    assert _run_cli(root, context, "start").code == 0
    assert _publish(context, ReviewRole.REQUESTOR, 1).code == 0
    assert _publish(
        context,
        ReviewRole.REVIEWER,
        1,
        disposition=ReviewDisposition.CONVERGENCE_RECOMMENDED,
    ).code == _EXPECTED_STOP
    guidance = "Recheck the exact transcript boundary."
    guidance_file = _input(root, "acceptance-guidance", guidance)
    override = _run_cli(
        root,
        context,
        "confirm",
        (
            "--choice-label",
            "Revise and review again",
            "--guidance-file",
            str(guidance_file),
        ),
    )
    publication = _publish(
        context,
        ReviewRole.REQUESTOR,
        _SECOND_ROUND,
        guidance=guidance,
    )
    reason = _input(root, "acceptance-escalation", "Human evidence choice required.")
    escalation = _run_cli(root, context, "escalate", ("--summary-file", str(reason)))
    resolution = _input(root, "acceptance-resolution", "Archive and restart cleanly.")
    resolved = _run_cli(root, context, "archive", ("--summary-file", str(resolution)))
    transcript = paths.transcript.read_text(encoding="utf-8")
    return ResolutionJourney(override, publication, escalation, resolved, paths, transcript)


def test_human_override_guidance_archive_and_fresh_round(
    resolution_journey: ResolutionJourney,
) -> None:
    """Another-round guidance and archived human resolution remain observable."""
    _assert_resolution_state(resolution_journey)
    _assert_resolution_transcript(resolution_journey)


def _assert_resolution_state(journey: ResolutionJourney) -> None:
    """Check the override, archive paths, and authoritative fresh round."""
    archived = journey.resolution.payload["archived_paths"]
    actual = (
        journey.override.payload["outcome"],
        journey.override.payload["round"],
        journey.publication.code,
        journey.escalation.payload["state"],
        journey.resolution.payload["round"],
        len(archived),
    )
    assert actual == (
        "another-round",
        _SECOND_ROUND,
        0,
        "escalated",
        _EXPECTED_STOP,
        _SECOND_ROUND,
    )
    assert all(Path(path).is_file() for path in archived)
    assert not journey.paths.request.exists()


def _assert_resolution_transcript(journey: ResolutionJourney) -> None:
    """Check one confirmation, one resolution, and retained human guidance."""
    assert journey.transcript.count("Outcome: human-confirmation") == 1
    assert journey.transcript.count("Outcome: human-resolution") == 1
    assert "Recheck the exact transcript boundary." in journey.transcript


class FakeTime:
    """Advance one monotonic deadline and wall clock without real sleeping."""

    def __init__(self) -> None:
        """Start deterministic clocks and record every sleep interval."""
        self.wall = datetime(2026, 8, 5, 8, 0, tzinfo=UTC)
        self.monotonic = 10.0
        self.sleeps: list[float] = []

    def now(self) -> datetime:
        """Return the injected wall time."""
        return self.wall

    def monotonic_now(self) -> float:
        """Return the injected monotonic value."""
        return self.monotonic

    def sleep(self, seconds: float) -> None:
        """Advance both clocks by one requested poll interval."""
        self.sleeps.append(seconds)
        self.monotonic += seconds
        self.wall += timedelta(seconds=seconds)


def test_long_wait_has_progress_stderr_and_one_monotonic_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A long logical wait reports progress without a real-time test dependency."""
    root = tmp_path / "wait"
    root.mkdir()
    context = _context(root, ReviewFamily.CODE, "wait", step="5")
    store = ReviewExchangeStore(derive_artifact_paths(root, context))
    clock = FakeTime()
    policy = _policy(context)
    configuration = ReviewConfiguration(
        enabled=True,
        wait_timeout_seconds=_WAIT_LIMIT,
    )
    core = ReviewExchangeCore(
        store,
        context,
        policy,
        configuration,
        wall_clock=clock.now,
        monotonic_clock=clock.monotonic_now,
        sleeper=clock.sleep,
    )
    core.start()
    capability = core.ownership_capability
    assert capability is not None
    runtime = cli.Runtime(root, context, store.paths, configuration, core)
    def fixed_root(_start: Path) -> Path:
        return root

    def fixed_runtime(_args: Namespace, _root: Path) -> cli.Runtime:
        return runtime

    def valid_activation(_root: Path, _paths: ArtifactPaths) -> None:
        return None

    monkeypatch.setattr(cli, "find_project_root", fixed_root)
    monkeypatch.setattr(cli, "_build_runtime", fixed_runtime)
    monkeypatch.setattr(cli, "validate_activation", valid_activation)

    code = cli.main(
        [
            "wait-answer",
            *_common(context),
            "--ownership-generation",
            str(capability.generation),
            "--ownership-token",
            capability.token,
            "--timeout-seconds",
            str(_WAIT_LIMIT),
            "--poll-interval",
            "1",
            "--progress-interval",
            "1",
        ],
    )

    captured = capsys.readouterr()
    stdout_lines = captured.out.splitlines()
    progress = [json.loads(line)["progress"] for line in captured.err.splitlines()]
    assert code == _EXPECTED_STOP, captured.out + captured.err
    assert len(stdout_lines) == 1
    assert json.loads(stdout_lines[0])["outcome"] == "timed-out"
    assert len(progress) >= _EXPECTED_STOP
    assert [item["elapsed_seconds"] for item in progress] == sorted(
        item["elapsed_seconds"] for item in progress
    )
    assert sum(clock.sleeps) == _WAIT_LIMIT


# eof
