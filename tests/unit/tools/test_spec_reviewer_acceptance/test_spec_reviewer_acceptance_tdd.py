"""Lifecycle and routing acceptance for the specification reviewer."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from tools import prompt_workflow_skill
from tools.review_exchange_models import ReviewDisposition
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths

from .fixtures import (
    Effort,
    make_effort,
    publish_answer,
    publish_request,
    render_answer,
)

_IDENTITIES = (
    ("feature-request", "feature-request"),
    ("issue", "issue"),
    ("design", "design-specification"),
    ("plan", "plan"),
)


@pytest.fixture(params=_IDENTITIES, ids=lambda value: value[0])
def published_identity(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> tuple[Effort, str]:
    """Publish every registered specification identity outside call timing."""
    prefix, type_token = cast("tuple[str, str]", request.param)
    effort = make_effort(tmp_path / prefix, prefix, f"reviewer-{prefix}")
    assert publish_request(effort).code == 0
    return effort, type_token


def test_every_specification_type_routes_to_reviewer_with_exact_identity(
    published_identity: tuple[Effort, str],
) -> None:
    """All specification requests use the registered identity and reviewer role."""
    effort, type_token = published_identity
    paths = derive_artifact_paths(effort.root, effort.context)
    envelope, _ = parse_envelope_markdown(paths.request.read_text(encoding="utf-8"))

    ordinary = prompt_workflow_skill.next_command(
        effort.root,
        effort.topic,
        effort.topic.slug,
        {"CODEX_THREAD_ID": "acceptance"},
    )
    explicit = prompt_workflow_skill.forced_command(
        effort.root,
        effort.topic,
        "spec-reviewer",
        {"CODEX_THREAD_ID": "acceptance"},
    )

    document = effort.document.relative_to(effort.root).as_posix()
    assert effort.context.umbrella_path is not None
    umbrella = effort.context.umbrella_path.relative_to(effort.root).as_posix()
    expected = f"$llm-shared:spec-reviewer on {document} with umbrella {umbrella}"
    assert (ordinary, explicit, envelope.identity.type_token) == (
        expected,
        expected,
        type_token,
    )
    assert paths.request.name.startswith(f"a.review-requested.{type_token}.")


@pytest.fixture(
    params=[
        ReviewDisposition.CHANGES_REQUESTED,
        ReviewDisposition.CONVERGENCE_RECOMMENDED,
    ],
    ids=lambda disposition: disposition.value,
)
def answer_publication_journey(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """Run paired answer publication outside the measured call phase."""
    disposition = cast("ReviewDisposition", request.param)
    effort = make_effort(tmp_path / disposition.value, "plan", disposition.value)
    assert publish_request(effort).code == 0
    paths = derive_artifact_paths(effort.root, effort.context)
    before = paths.transcript.read_text(encoding="utf-8")

    result = publish_answer(effort, disposition)

    transcript = paths.transcript.read_text(encoding="utf-8")
    envelope, authored = parse_envelope_markdown(
        paths.answer.read_text(encoding="utf-8"),
    )
    expected_code = 3 if disposition is ReviewDisposition.CONVERGENCE_RECOMMENDED else 0
    assert result.code == expected_code
    assert result.payload["state"] in {"answer-pending", "convergence-gate"}
    assert not paths.request.exists()
    assert envelope.disposition is disposition
    assert transcript.startswith(before)
    assert transcript.count("review-entry-id: answer-round-1") == 1
    assert "The wording was checked." in authored


def test_both_dispositions_publish_paired_content_and_one_transcript_entry(
    answer_publication_journey: None,
) -> None:
    """A reviewer publication atomically swaps request for answer and appends once."""
    assert answer_publication_journey is None


@pytest.fixture
def guided_answer_journey(tmp_path: Path) -> None:
    """Render literal guidance and its response outside the measured call phase."""
    effort = make_effort(tmp_path / "guidance", "issue", "guidance")
    assert publish_request(effort, guidance="Keep Q01 settled.").code == 0

    answer, summary = render_answer(
        effort,
        ReviewDisposition.CHANGES_REQUESTED,
        guidance=True,
    )

    answer_text = answer.read_text(encoding="utf-8")
    summary_text = summary.read_text(encoding="utf-8")
    assert "Human guidance:\n\nKeep Q01 settled." in answer_text
    assert "Guidance response:\n\nQ01 remains settled." in answer_text
    assert "Q01 remains settled." in summary_text


def test_human_guidance_receives_a_dedicated_reviewer_response(
    guided_answer_journey: None,
) -> None:
    """Literal guidance is preserved and answered in both paired outputs."""
    assert guided_answer_journey is None


def test_marker_suspends_and_restores_reviewer_routing(tmp_path: Path) -> None:
    """Review routing remains an opt-in capability with no artifact side effects."""
    effort = make_effort(
        tmp_path / "marker",
        "feature-request",
        "marker",
        marker=False,
    )
    paths = derive_artifact_paths(effort.root, effort.context)

    disabled = prompt_workflow_skill.forced_command(
        effort.root,
        effort.topic,
        "spec-reviewer",
        {"CODEX_THREAD_ID": "acceptance"},
    )
    (effort.root / "a.review-mode").write_text("", encoding="utf-8")
    requestor = prompt_workflow_skill.forced_command(
        effort.root,
        effort.topic,
        "spec-review-requestor",
        {"CODEX_THREAD_ID": "acceptance"},
    )

    assert disabled is None
    assert requestor is not None
    assert "spec-review-requestor" in requestor
    assert not paths.coordination.exists()


def test_reviewer_instruction_orders_exact_request_before_assessment() -> None:
    """The canonical workflow pins the no-search assessment sequence."""
    content = Path("instructions/spec-reviewer.md").read_text(encoding="utf-8")
    wait = content.index("wait-request")
    exact = content.index("paths.request", wait)
    assess = content.index("Read the full exact reviewed specification", exact)

    assert wait < exact < assess
    assert "Do not search documentation folders" in content
    assert "Human guidance" in content
    assert "SHA-256" in content
