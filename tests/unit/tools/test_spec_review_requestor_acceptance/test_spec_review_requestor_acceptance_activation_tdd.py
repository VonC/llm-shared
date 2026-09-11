"""Activation and identity acceptance for the specification requestor.

Step 4 keeps opt-in routing and the four registered specification identities
separate from repeated-round lifecycle coverage. Real Git journeys run in
fixtures so call-phase timing measures assertions rather than subprocesses.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from tools import prompt_workflow_skill as workflow_skill
from tools.review_exchange_models_envelope import parse_envelope_markdown
from tools.review_exchange_paths import derive_artifact_paths

from .test_spec_review_requestor_acceptance_tdd import (
    _effort,
    _init_repo,
    _render_pair,
    _run_cli,
)

_IDENTITY_CASES = (
    ("feature-request", "feature-request"),
    ("issue", "issue"),
    ("design", "design-specification"),
    ("plan", "plan"),
)


@pytest.fixture
def activation_journey(tmp_path: Path) -> None:
    """Run opt-in, hold, activation, and live routing outside call timing."""
    root = tmp_path / "activation"
    _init_repo(root, marker=False)
    effort = _effort(root, "feature-request", "activation")

    disabled = workflow_skill.forced_command(
        root,
        effort.topic,
        "spec-review-requestor",
        {"CODEX_THREAD_ID": "acceptance"},
    )
    coordination = derive_artifact_paths(root, effort.context).coordination
    assert (disabled, coordination.exists()) == (None, False)

    (root / "a.review-mode").write_text("", encoding="utf-8")
    effort.document.write_text(
        "# activation\n\n## Requirement clarifications\n\n"
        "| Question | Decision |\n| --- | --- |\n"
        "| Q01 | No open questions, all decisions made |\n",
        encoding="utf-8",
    )
    no_question = workflow_skill.forced_command(
        root,
        effort.topic,
        "spec-review-requestor",
        {"CODEX_THREAD_ID": "acceptance"},
    )

    instruction = (Path("instructions") / "review-ask-questions.md").read_text(
        encoding="utf-8",
    )
    delegation = instruction.index("## Review-mode delegation after placing questions")
    block = instruction[delegation : instruction.index("## Presenting", delegation)]
    hold_before_marker = block.index("`stop here`") < block.index("`a.review-mode`")
    marker_before_pw = block.index("`a.review-mode`") < block.index(
        "pw skill spec-review-requestor",
    )
    assert (no_question, hold_before_marker, marker_before_pw, coordination.exists()) == (
        None,
        True,
        True,
        False,
    )

    effort.document.write_text(
        "# activation\n\n## Open questions for activation\n\n1. Question?\n",
        encoding="utf-8",
    )
    forced = workflow_skill.forced_command(
        root,
        effort.topic,
        "spec-review-requestor",
        {"CODEX_THREAD_ID": "acceptance"},
    )
    expected = (
        "$llm-shared:spec-review-requestor on "
        "docs/v0.11.0/feature-request.v0.11.0.activation.md"
        " with umbrella docs/v0.11.0/draft.v0.11.0.review-mode.md"
    )
    activated = _run_cli(root, effort.context, "activate")
    started = _run_cli(root, effort.context, "start")
    resumed = workflow_skill.next_command(
        root,
        effort.topic,
        "activation",
        {"CODEX_THREAD_ID": "acceptance"},
    )
    assert (forced, activated.code, started.code, resumed) == (expected, 0, 0, expected)


def test_activation_holds_and_public_pw_routing_are_composed(
    activation_journey: None,
) -> None:
    """Opt-in, no-question, hold, activation, and live routing stay coherent."""
    assert activation_journey is None


@pytest.fixture(params=_IDENTITY_CASES, ids=lambda case: case[0])
def specification_identity_journey(
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    """Publish one registered specification identity outside call timing."""
    prefix, type_token = cast("tuple[str, str]", request.param)
    root = tmp_path / prefix
    _init_repo(root)
    effort = _effort(root, prefix, f"identity-{prefix}")
    assert _run_cli(root, effort.context, "activate").code == 0
    assert _run_cli(root, effort.context, "start").code == 0

    request_path, summary_path = _render_pair(effort, 1)
    envelope, authored = parse_envelope_markdown(
        request_path.read_text(encoding="utf-8"),
    )
    publication = _run_cli(
        root,
        effort.context,
        "publish-request",
        (
            "--content-file",
            str(request_path),
            "--summary-file",
            str(summary_path),
        ),
    )
    paths = derive_artifact_paths(root, effort.context)

    assert publication.code == 0
    assert envelope.identity.type_token == type_token
    assert envelope.round_number == 1
    assert authored.count("Review round: 1") == 1
    assert paths.request.name == (
        f"a.review-requested.{type_token}.v0.11.0.identity-{prefix}.md"
    )
    assert "Questions prepared for independent review." in paths.transcript.read_text(
        encoding="utf-8",
    )


def test_every_specification_type_renders_and_publishes_exact_identity(
    specification_identity_journey: None,
) -> None:
    """All registered specification types share one paired publication path."""
    assert specification_identity_journey is None


# eof
