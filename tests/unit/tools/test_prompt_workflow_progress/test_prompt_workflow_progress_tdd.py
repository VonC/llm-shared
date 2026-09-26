"""Contracts for `pw progress`: where the current topic stands, and how far along.

Positions are counted from document order, never read from ids: a step `3.2`
fourth in the validation plan renders `3.2 (4/7)`, while an id equal to its
position renders compactly. Umbrella membership comes from the child draft
marker, the umbrella draft a topic resolved through, or one same-version
umbrella listing the slug; anything else is a standalone topic. A known
requestor, from an active exchange or else the topic's transcripts, renders the
`next` command for its host and labels it, except for a reviewer handoff.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tools import prompt_workflow
from tools import prompt_workflow_progress as progress
from tools import prompt_workflow_progress_review as progress_review
from tools import prompt_workflow_render as rendering
from tools.llm_nature import LlmNature
from tools.prompt_workflow_models import Topic
from tools.prompt_workflow_plan import PlanStep

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

_CLAUDE = {"CLAUDECODE": "1"}
_VERSION = "v10.0.0"
_STEP_IDS = ("0", "1", "2", "3.1", "3.2", "4A", "4B")
_VERIFIED_STEPS = 4


@pytest.fixture(autouse=True)
def stub_review_status(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the `rwst` collection with one line naming the topic slug.

    No requestor is known, from an active exchange or a transcript.
    """
    monkeypatch.setattr(
        progress.progress_review,
        "review_report",
        lambda _root, slug, *_a: progress_review.ReviewReport((f"review of {slug}",), None),
    )
    monkeypatch.setattr(progress.review_history, "last_requestor_nature", lambda *_a: None)


def _steps(verified: int) -> list[PlanStep]:
    """Return the sample plan steps with the first `verified` ones marked Yes."""
    return [
        PlanStep(number=number, verified=index < verified)
        for index, number in enumerate(_STEP_IDS)
    ]


def _umbrella(docs_dir: Path, statuses: tuple[str, str, str] = ("completed", "pending", "pending")) -> Path:
    """Write a three-row umbrella draft and return its path."""
    rows = "".join(
        f"| {order} | Feature-request | Title {slug} | `{slug}` | {status} | "
        + (
            f"`docs/feature-request.{_VERSION}.{slug}.md` | "
            f"`docs/plan.{_VERSION}.{slug}.validation.md` |\n"
            if status == "completed"
            else "- | - |\n"
        )
        for order, (slug, status) in enumerate(
            zip(("alpha", "beta-one", "gamma"), statuses, strict=True), start=1,
        )
    )
    umbrella = docs_dir / f"draft.{_VERSION}.family.md"
    umbrella.write_text(
        "# Family\n\n"
        "- Type: collection (feature-requests and issues)\n"
        "- Draft role: umbrella\n\n"
        "## List of feature-requests and issues to create\n\n"
        "| Order | Type | Key title | Slug | Status | Requirement | Validation plan |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
        f"{rows}\n",
        encoding="utf-8",
    )
    return umbrella


def _docs(tmp_path: Path) -> Path:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    return docs_dir


def _topic(docs_dir: Path, slug: str, body: str = "# Draft\n") -> Topic:
    draft = docs_dir / f"draft.{_VERSION}.{slug}.md"
    draft.write_text(body, encoding="utf-8")
    return Topic(version=_VERSION, slug=slug, draft_path=draft.resolve())


def test_format_position_is_compact_only_when_the_id_is_the_position() -> None:
    """`3/4` for a matching id, `3.2 (4/11)` or `A (3/4)` otherwise."""
    assert progress.format_position("3", 3, 4) == "3/4"
    assert progress.format_position("3.2", 4, 11) == "3.2 (4/11)"
    assert progress.format_position("A", 3, 4) == "A (3/4)"
    assert progress.format_position("0", 1, 5) == "0 (1/5)"


def test_step_progress_counts_positions_across_sub_steps() -> None:
    """Step `3.2` is the fifth of seven ids once `3.1` carries its commit."""
    committed = {"3.1"}
    result = progress.step_progress(
        _steps(verified=4),
        committed.__contains__,
        active=True,
        title_for=lambda number: f"Title {number}",
    )

    assert result == progress.StepProgress(
        current="3.2", index=5, total=7, verified=4, title="Title 3.2",
    )
    assert result is not None
    assert result.render() == "3.2 (5/7): Title 3.2 (4/7 verified)"


def test_step_progress_reports_the_first_step_and_the_terminal_cycle() -> None:
    """No verified step starts at step 0; a committed last step ends the cycle."""
    first = progress.step_progress(_steps(verified=0), lambda _n: False, active=True)
    done = progress.step_progress(_steps(verified=7), lambda _n: True, active=True)

    assert first is not None
    assert first.render() == "0 (1/7) (0/7 verified)"
    assert done is not None
    assert done.render() == "all 7 steps done (7/7 verified)"


def test_step_progress_only_counts_before_implementation_and_skips_empty_plans() -> None:
    """A plan still in review reports its planned steps; no step means no line."""
    planned = progress.step_progress(_steps(verified=0), lambda _n: False, active=False)

    assert planned is not None
    assert planned.render() == "7 steps planned (0/7 verified)"
    assert progress.step_progress([], lambda _n: False, active=True) is None


def test_phase_of_maps_workflow_steps_to_ordered_phases() -> None:
    """Step 1 off the slug branch is the draft; step 10 is the implementation."""
    assert progress.phase_of(1, draft_pending=True) == "draft"
    assert progress.phase_of(1, draft_pending=False) == "requirement"
    assert progress.phase_of(5, draft_pending=True) == "design"
    assert progress.phase_of(9, draft_pending=False) == "plan"
    assert progress.phase_of(10, draft_pending=False) == "implementation"
    assert progress.render_phase("design") == "design (3/5)"


def test_umbrella_path_prefers_the_child_draft_marker(tmp_path: Path) -> None:
    """An explicit `- Umbrella:` line names the umbrella."""
    docs_dir = _docs(tmp_path)
    umbrella = _umbrella(docs_dir)
    topic = _topic(docs_dir, "beta-one", f"# Beta\n\n- Umbrella: docs/{umbrella.name}\n")

    assert progress.umbrella_path(tmp_path, topic) == umbrella.resolve()


def test_umbrella_path_uses_the_umbrella_a_topic_resolved_through(tmp_path: Path) -> None:
    """A requirement resolved through its umbrella draft belongs to that umbrella."""
    docs_dir = _docs(tmp_path)
    umbrella = _umbrella(docs_dir).resolve()
    topic = Topic(version=_VERSION, slug="beta_one", draft_path=umbrella)

    assert progress.umbrella_path(tmp_path, topic) == umbrella


def test_umbrella_path_falls_back_to_one_same_version_umbrella(tmp_path: Path) -> None:
    """Without a marker, the one umbrella listing the slug is used."""
    docs_dir = _docs(tmp_path)
    umbrella = _umbrella(docs_dir)
    topic = _topic(docs_dir, "gamma", "# Gamma\n\n- Umbrella: docs/missing.md\n")

    assert progress.umbrella_path(tmp_path, topic) == umbrella.resolve()


def test_umbrella_path_is_none_for_a_standalone_topic(tmp_path: Path) -> None:
    """No marker and no listing umbrella means standalone, even for a synthetic draft."""
    docs_dir = _docs(tmp_path)
    _umbrella(docs_dir)
    listed_elsewhere = _topic(docs_dir, "solo")
    synthetic = Topic(
        version=_VERSION, slug="ghost", draft_path=(docs_dir / "draft.v10.0.0.ghost.md"),
    )
    unparsed = Topic(
        version=_VERSION, slug="alpha", draft_path=_umbrella(docs_dir).with_name("notes.md"),
    )
    unparsed.draft_path.write_text("# Notes\n", encoding="utf-8")

    assert progress.umbrella_path(tmp_path, listed_elsewhere) is None
    assert progress.umbrella_path(tmp_path, synthetic) is None
    assert progress.umbrella_path(tmp_path, unparsed) == (docs_dir / "draft.v10.0.0.family.md").resolve()


def test_umbrella_progress_renders_child_and_own_positions(tmp_path: Path) -> None:
    """A child shows its row; the umbrella branch shows the next pending row."""
    umbrella = _umbrella(_docs(tmp_path))

    child = progress.umbrella_progress(umbrella, "beta_one")
    missing = progress.umbrella_progress(umbrella, "zeta")
    own = progress.umbrella_progress(umbrella, None)

    assert child.render_child() == "family, topic 2/3: Title beta-one (1/3 topics completed)"
    assert missing.render_child() == "family, topic not listed (1/3 topics completed)"
    assert own.render_own() == (
        "1/3 topics completed, next topic 2/3: Title beta-one (`beta-one`)"
    )


def test_umbrella_progress_reports_an_exhausted_umbrella(tmp_path: Path) -> None:
    """Every completed row leaves no next topic; a non-draft name keeps its stem."""
    umbrella = _umbrella(_docs(tmp_path), ("completed", "completed", "completed"))
    renamed = umbrella.rename(umbrella.with_name("family-notes.md"))

    own = progress.umbrella_progress(renamed, None)

    assert own.slug == "family-notes"
    assert own.render_own() == "3/3 topics completed, every topic done"


def test_progress_lines_for_an_umbrella_child_in_implementation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A child in its implementation cycle reports umbrella, phase, and step."""
    docs_dir = _docs(tmp_path)
    umbrella = _umbrella(docs_dir)
    topic = _topic(docs_dir, "beta-one", f"# Beta\n\n- Umbrella: docs/{umbrella.name}\n")
    (docs_dir / f"feature-request.{_VERSION}.beta-one.md").write_text("# FR\n", encoding="utf-8")
    (docs_dir / f"plan.{_VERSION}.beta-one.md").write_text(
        "# Plan\n\n### Step 3.2. Wire the parser\n", encoding="utf-8",
    )
    (docs_dir / f"plan.{_VERSION}.beta-one.validation.md").write_text(
        "# Validation\n\n"
        + "".join(
            f"### Analysis of Step {number} implementation state\n\n"
            f"{'Yes' if index < _VERIFIED_STEPS else 'No'}. Step {number}.\n\n"
            for index, number in enumerate(_STEP_IDS)
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: ("/next", ""))
    monkeypatch.setattr(progress.skill, "resolved_workflow_step", lambda _state: 10)
    monkeypatch.setattr(progress.git, "fork_point", lambda _root: "base")
    monkeypatch.setattr(
        progress.git, "has_step_commit", lambda _root, number, _base: number == "3.1",
    )

    lines = progress.progress_lines(tmp_path, topic, "feat/beta-one", _CLAUDE)

    assert lines == [
        ("branch", "feat/beta-one"),
        ("topic", f"{_VERSION} beta-one"),
        ("umbrella", "family, topic 2/3: Title beta-one (1/3 topics completed)"),
        ("phase", "implementation (5/5)"),
        ("step", "3.2 (5/7): Wire the parser (4/7 verified)"),
        ("review", "review of beta-one"),
        ("next", "/next"),
    ]


def test_progress_lines_for_a_standalone_draft_and_an_empty_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A new standalone draft routes to its draft phase with its real next command."""
    topic = _topic(_docs(tmp_path), "solo")

    lines = progress.progress_lines(tmp_path, topic, "main", _CLAUDE)

    assert lines == [
        ("branch", "main"),
        ("topic", f"{_VERSION} solo"),
        ("umbrella", "none, standalone topic"),
        ("phase", "draft (1/5)"),
        ("review", "review of solo"),
        ("next", "/process-draft on docs/draft.v10.0.0.solo.md"),
    ]

    (tmp_path / "docs" / f"plan.{_VERSION}.solo.validation.md").write_text(
        "# Validation\n", encoding="utf-8",
    )
    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: (None, "note"))
    monkeypatch.setattr(progress.git, "fork_point", lambda _root: None)

    assert progress.progress_lines(tmp_path, topic, "main", _CLAUDE)[-1] == (
        "next", "none resolved",
    )


def test_progress_lines_on_the_umbrella_integration_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The umbrella branch reports the umbrella itself, not a phase or a step."""
    umbrella = _umbrella(_docs(tmp_path)).resolve()
    topic = Topic(version=_VERSION, slug="family", draft_path=umbrella)
    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: ("/next", ""))

    lines = progress.progress_lines(tmp_path, topic, "family", _CLAUDE)

    assert [label for label, _value in lines] == [
        "branch", "topic", "umbrella", "review", "next",
    ]
    assert lines[1] == ("topic", f"{_VERSION} family (umbrella)")
    assert lines[2][1].startswith("1/3 topics completed, next topic 2/3")


_PLAN_DOC = f"docs/plan.{_VERSION}.dex-navigation.md"


def _fake_command(role: str) -> Callable[..., tuple[str, str]]:
    """Return a `current_command` stub rendering `role` for the requested host."""

    def fake(
        _root: Path, _topic: Topic, _branch: str, env: Mapping[str, str], override: str | None = None,
    ) -> tuple[str, str]:
        prefix = rendering.host_prefix(env, override)
        return rendering.render_step_command(prefix, f"{role}.md", _PLAN_DOC, "3"), ""

    return fake


def test_next_line_renders_and_labels_the_known_requestor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Claude gets `/`, Codex gets `$llm-shared:`, and the line names the host."""
    topic = _topic(_docs(tmp_path), "dex-navigation")
    monkeypatch.setattr(progress.skill, "current_command", _fake_command("implement-step"))

    def line(requestor: LlmNature | None, env: dict[str, str] | None = None) -> str:
        return progress.next_line(tmp_path, topic, "dex-navigation", env or {}, None, requestor)

    assert line(None) == f"<command-prefix>implement-step on {_PLAN_DOC} step 3"
    assert line(LlmNature.CLAUDE) == f"/implement-step on {_PLAN_DOC} step 3 (claude)"
    assert line(LlmNature.CODEX, _CLAUDE) == (
        f"$llm-shared:implement-step on {_PLAN_DOC} step 3 (codex)"
    )


def test_next_line_leaves_reviewer_handoffs_and_missing_commands(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A reviewer runs its own handoff; no command stays `none resolved`."""
    topic = _topic(_docs(tmp_path), "dex-navigation")
    monkeypatch.setattr(progress.skill, "current_command", _fake_command("code-reviewer"))

    assert progress.next_line(tmp_path, topic, "b", {}, None, LlmNature.CODEX) == (
        f"<command-prefix>code-reviewer on {_PLAN_DOC} step 3"
    )
    assert progress.addresses_reviewer("$llm-shared:spec-reviewer on docs/x.md")
    assert not progress.addresses_reviewer("/code-review-requestor on docs/x.md step 3")

    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: (None, "note"))
    assert progress.next_line(tmp_path, topic, "b", {}, None, LlmNature.CODEX) == "none resolved"
    assert progress.next_line(tmp_path, topic, "b", {}, None, None) == "none resolved"

    answers = iter([("/code-reviewer on docs/x.md", ""), (None, "note")])
    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: next(answers))
    assert progress.next_line(tmp_path, topic, "b", {}, None, LlmNature.CLAUDE) == "none resolved"


def test_progress_lines_prefer_the_live_requestor_then_the_transcripts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`rwst` names the requestor first; a finished review falls back to transcripts."""
    topic = _topic(_docs(tmp_path), "solo")
    monkeypatch.setattr(progress.skill, "current_command", _fake_command("implement-step"))
    monkeypatch.setattr(progress.review_history, "last_requestor_nature", lambda *_a: LlmNature.CODEX)

    assert progress.progress_lines(tmp_path, topic, "solo", {})[-1] == (
        "next", f"$llm-shared:implement-step on {_PLAN_DOC} step 3 (codex)",
    )

    monkeypatch.setattr(
        progress.progress_review,
        "review_report",
        lambda *_a: progress_review.ReviewReport(("live",), LlmNature.CLAUDE),
    )
    assert progress.progress_lines(tmp_path, topic, "solo", {})[-2:] == [
        ("review", "live"),
        ("next", f"/implement-step on {_PLAN_DOC} step 3 (claude)"),
    ]


def test_progress_lines_add_a_resume_line_per_abnormal_exchange(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """Resume prompts follow the review lines, with or without a resolved topic."""
    topic = _topic(_docs(tmp_path), "solo")
    prompt = f"/code-review-requestor on {_PLAN_DOC} step 3: escalated, resume it (claude)"
    seen: list[tuple[object, ...]] = []

    def fake_report(*args: object) -> progress_review.ReviewReport:
        seen.append(args[1:])
        return progress_review.ReviewReport(("round 2 for step 3: escalated",), None, (prompt,))

    monkeypatch.setattr(progress.progress_review, "review_report", fake_report)
    monkeypatch.setattr(progress.skill, "current_command", lambda *_a: ("/next", ""))

    assert progress.progress_lines(tmp_path, topic, "solo", _CLAUDE, "codex")[-3:] == [
        ("review", "round 2 for step 3: escalated"),
        ("resume", prompt),
        ("next", "/next"),
    ]
    assert seen == [("solo", _CLAUDE, "codex")]

    monkeypatch.setattr(progress.git, "current_branch", lambda _root: "main")
    monkeypatch.setattr(progress.memory, "read_memory", lambda _root: None)
    monkeypatch.setattr(progress.handoff, "resolve_current_topic", lambda *_a: None)

    assert progress.run_progress(tmp_path, "claude") == progress.skill.EXIT_NOT_APPLICABLE
    assert capsys.readouterr().out.splitlines()[-1] == f"resume    {prompt}"
    assert seen[-1][0] is None
    assert seen[-1][2] == "claude"


def test_run_progress_prints_the_report_or_notes_a_missing_topic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    """A resolved topic prints aligned lines and exits 0; none exits 3."""
    topic = _topic(_docs(tmp_path), "solo")
    resolved: list[Topic | None] = [None, topic]
    monkeypatch.setattr(progress.git, "current_branch", lambda _root: "main")
    monkeypatch.setattr(progress.memory, "read_memory", lambda _root: None)
    monkeypatch.setattr(
        progress.handoff, "resolve_current_topic", lambda *_a: resolved.pop(0),
    )
    monkeypatch.setattr(
        progress, "progress_lines", lambda *_a: [("branch", "main"), ("next", "/x")],
    )

    assert progress.run_progress(tmp_path) == progress.skill.EXIT_NOT_APPLICABLE
    assert capsys.readouterr().out == (
        "branch    main\ntopic     none resolved\nreview    review of None\n"
    )
    assert progress.run_progress(tmp_path, "claude") == 0
    assert capsys.readouterr().out == "branch    main\nnext      /x\n"


def test_main_dispatches_the_progress_subcommand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`pw progress --host codex` reaches `run_progress` with the override."""
    calls: list[tuple[Path, str | None]] = []

    def fake_run_progress(root: Path, host_override: str | None = None) -> int:
        calls.append((root, host_override))
        return 0

    monkeypatch.setattr(prompt_workflow.progress, "run_progress", fake_run_progress)

    assert prompt_workflow.main(["progress", "--root", str(tmp_path), "--host", "codex"]) == 0
    assert calls == [(tmp_path.resolve(), "codex")]


# eof
