"""IO and failure acceptance for the specification review requestor.

Step 4 keeps failure instrumentation separate from lifecycle journeys. These
tests reject identity and repository-boundary errors, prove escalation remains
stopped, and guard the router against documentation scans or transcript reads.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

from tools import prompt_workflow_review as review_routing
from tools import spec_review_request as request_renderer
from tools.prompt_workflow_models import Topic, WorkflowState
from tools.review_exchange_core import ReviewExchangeCore
from tools.review_exchange_models import (
    ArtifactState,
    FamilyPolicy,
    ReviewConfiguration,
    ReviewExchangeError,
)
from tools.review_exchange_paths import derive_artifact_paths
from tools.review_exchange_store import ReviewExchangeStore
from tools.spec_review_request import SpecificationRoundInput

if TYPE_CHECKING:
    from collections.abc import Callable

_POLICY = FamilyPolicy(
    "consolidation-ready",
    "Revise and review again",
    "Consolidate",
)
_FATAL = 2
_CANDIDATE_COUNT = 3


def _git(root: Path, *arguments: str) -> None:
    """Record the small repository protocol used by these acceptance tests."""
    operation = arguments[0]
    if operation == "init":
        (root / ".git").mkdir()
        return
    if operation == "add":
        tracked = root / ".unit-git-index"
        tracked.write_text(arguments[-1] + "\n", encoding="utf-8")
        return
    raise AssertionError(arguments)


def _root(tmp_path: Path, name: str) -> Path:
    """Create one opted-in Git repository with ignored root scratch files."""
    root = tmp_path / name
    root.mkdir()
    _git(root, "init", "-q")
    (root / ".gitignore").write_text("a.*\n", encoding="utf-8")
    (root / "a.review-mode").write_text("", encoding="utf-8")
    return root


def _document(root: Path, prefix: str, slug: str) -> Path:
    """Create one exact supported specification document."""
    docs = root / "docs"
    docs.mkdir(exist_ok=True)
    path = docs / f"{prefix}.v1.2.3.{slug}.md"
    path.write_text(f"# {slug}\n\n## Open questions\n", encoding="utf-8")
    return path


def _core(root: Path, document: Path) -> ReviewExchangeCore:
    """Build one public shared core for an exact specification identity."""
    context = request_renderer.specification_context(document, None)
    return ReviewExchangeCore(
        ReviewExchangeStore(derive_artifact_paths(root, context)),
        context,
        _POLICY,
        ReviewConfiguration(enabled=True, wait_timeout_seconds=60),
    )


def _render(document: Path) -> request_renderer.SpecificationRequestRender:
    """Render one valid round 1 request for an exact document."""
    context = request_renderer.specification_context(document, None)
    return request_renderer.render_specification_request(
        SpecificationRoundInput(
            context,
            1,
            "2026-08-09T10:00:00+02:00",
            "Assess the remaining question.",
            "Prepared one question.",
            "The writer requests feedback.",
        ),
    )


def test_identity_mismatch_duplicate_exchange_and_unsupported_type_fail_closed(
    tmp_path: Path,
) -> None:
    """No nearby identity or duplicate live exchange can take authority."""
    root = _root(tmp_path, "identity-failures")
    first = _document(root, "feature-request", "first")
    second = _document(root, "issue", "second")
    core = _core(root, first)
    core.start()

    with pytest.raises(ReviewExchangeError, match="already active"):
        core.start()
    wrong = _render(second)
    with pytest.raises(ReviewExchangeError, match="artifact envelope differs"):
        core.publish_request(wrong.request_content, wrong.transcript_summary)
    unsupported = root / "docs/reference.v1.2.3.first.md"
    unsupported.write_text("# Unsupported\n", encoding="utf-8")
    with pytest.raises(ReviewExchangeError, match="unsupported file name"):
        request_renderer.specification_context(unsupported, None)

    paths = core.store.paths
    assert not paths.request.exists()
    assert core.classify().state is ArtifactState.ROUND_IN_PROGRESS


@pytest.fixture
def tracked_input_journey(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Run the tracked-input rejection through the recorded Git boundary."""
    root = _root(tmp_path, "tracked-input")
    document = _document(root, "feature-request", "tracked")
    home = root / ".reviews"
    home.mkdir(exist_ok=True)
    (home / ".gitignore").write_bytes(b"*\n")
    assessment = home / "a.assessment.md"
    changes = home / "a.changes.md"
    response = home / "a.response.md"
    assessment.write_text("Assess.\n", encoding="utf-8")
    changes.write_text("Changed.\n", encoding="utf-8")
    response.write_text("Responded.\n", encoding="utf-8")
    _git(root, "add", "-f", ".reviews/a.assessment.md")
    request_output = home / "a.request-output.md"
    summary_output = home / "a.summary-output.md"

    code = request_renderer.main(
        [
            "--document",
            str(document),
            "--round-number",
            "1",
            "--assessment-file",
            str(assessment),
            "--change-summary-file",
            str(changes),
            "--writer-response-file",
            str(response),
            "--request-content-output",
            str(request_output),
            "--transcript-summary-output",
            str(summary_output),
        ],
        project_root=root,
    )

    assert code == _FATAL
    assert "assessment file is not effectively ignored" in capsys.readouterr().err
    assert not request_output.exists()
    assert not summary_output.exists()


def test_tracked_root_renderer_input_is_rejected_before_outputs(
    tracked_input_journey: None,
) -> None:
    """A tracked caller input cannot cross the ignored root-file boundary."""
    assert tracked_input_journey is None


@pytest.fixture
def escalated_request_journey(tmp_path: Path) -> None:
    """Escalate and inspect one request outside the measured call."""
    root = _root(tmp_path, "escalation")
    document = _document(root, "plan", "escalated")
    core = _core(root, document)
    core.start()
    rendered = _render(document)
    core.publish_request(rendered.request_content, rendered.transcript_summary)
    request_before = core.store.paths.request.read_bytes()

    record = core.escalate("Counterpart identity requires human resolution.")

    assert record.status.value == "escalated"
    assert core.classify().state is ArtifactState.ESCALATED
    assert core.store.paths.request.read_bytes() == request_before
    with pytest.raises(ReviewExchangeError, match="reclaim requires"):
        core.reclaim()


def test_escalation_preserves_evidence_and_cannot_be_reclaimed(
    escalated_request_journey: None,
) -> None:
    """An escalated request remains stopped with its exact evidence intact."""
    assert escalated_request_journey is None


def test_exact_path_routing_never_scans_docs_or_reads_transcript(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Three candidates use a fixed artifact set without history traversal."""
    root = _root(tmp_path, "bounded-io")
    docs = root / "docs"
    docs.mkdir()
    umbrella = docs / "draft.v1.2.3.umbrella.md"
    umbrella.write_text("# Umbrella\n", encoding="utf-8")
    draft = docs / "draft.v1.2.3.bounded.md"
    draft.write_text(
        "# Draft\n\n- Umbrella: docs/draft.v1.2.3.umbrella.md\n",
        encoding="utf-8",
    )
    candidates = tuple(
        _document(root, prefix, "bounded")
        for prefix in ("feature-request", "design", "plan")
    )
    topic = Topic("v1.2.3", "bounded", draft)
    state = WorkflowState(
        requirement=candidates[0],
        design=candidates[1],
        plan=candidates[2],
        validation_plan=None,
        requirement_has_open_questions=True,
        design_has_open_questions=False,
        plan_has_open_questions=False,
        memory_step=None,
    )
    original_read_text = Path.read_text
    original_exists = Path.exists
    reads: list[Path] = []
    exists_checks: list[Path] = []

    def forbidden_scan(_path: Path, *_args: object, **_kwargs: object) -> object:
        """Fail if routing tries any documentation-tree enumeration."""
        pytest.fail("documentation scan attempted")

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        """Record bounded reads and reject versioned transcript history."""
        reads.append(path)
        if path.name.startswith("review."):
            pytest.fail("transcript read attempted")
        reader = cast("Callable[..., str]", original_read_text)
        return reader(path, *args, **kwargs)

    def tracked_exists(path: Path) -> bool:
        """Record each exact existence probe used during routing."""
        exists_checks.append(path)
        return original_exists(path)

    monkeypatch.setattr(Path, "glob", forbidden_scan)
    monkeypatch.setattr(Path, "rglob", forbidden_scan)
    monkeypatch.setattr(Path, "iterdir", forbidden_scan)
    monkeypatch.setattr(Path, "read_text", guarded_read_text)
    monkeypatch.setattr(Path, "exists", tracked_exists)

    selected = review_routing.forced_specification_document(root, topic, state)
    contexts = review_routing.specification_contexts(root, topic, state)

    allowed_exists = {
        root / "a.review-mode",
        root / ".review-artifacts.ini",
        root / ".reviews",
        root / ".reviews" / "a.review-mode",
    }
    for context in contexts:
        allowed_exists.update(derive_artifact_paths(root, context).fixed_paths)
    assert selected == candidates[0].resolve()
    assert len(contexts) == _CANDIDATE_COUNT
    assert all(
        path.name in {".review-exchange.ini", "a.review-mode", draft.name}
        for path in reads
    )
    assert set(exists_checks) <= allowed_exists
    assert not any(path.name.startswith("review.") for path in reads)


# eof
