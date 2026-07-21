"""Tests for the pw skill module: host prefix, rendering, routing, and the CLI.

Step 1 covers the pure functions of tools/prompt_workflow_skill.py: detect_host
(host markers, Claude-wins, Claude default), host_prefix (an override
short-circuits the environment read), and render_command (a bare
``<prefix><name> on <document>`` line, ``.md`` dropped, no backticks). A small
property loop guards the render invariants.

Step 2 covers next_command: the next step read from disk (compute_state with no
memory step, next_step_numbers, the decisions-table override), mapped to an
instruction and a target document and rendered with the host prefix. When the
route reaches implementation, an available validation plan supplies the plan
step id appended to the rendered command.

Step 3 covers the pw skill subcommand: run_skill (topic resolution, the
not-applicable exit), forced_command (a forced skill emitted only when its
document exists), and the hub dispatch of the skill subparser.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tools import prompt_workflow
from tools import prompt_workflow_memory as memory
from tools import prompt_workflow_skill as skill
from tools.prompt_workflow_models import MemoryRecord, Topic

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false


def test_detect_host_reads_the_markers_with_claude_first() -> None:
    """The Claude marker wins, then Codex, then the default host."""
    # Act and Assert: each marker, then both, then neither.
    assert skill.detect_host({"CLAUDECODE": "1"}) == skill.HOST_CLAUDE
    assert skill.detect_host({"CODEX_THREAD_ID": "abc"}) == skill.HOST_CODEX
    assert skill.detect_host({"CLAUDECODE": "1", "CODEX_THREAD_ID": "abc"}) == skill.HOST_CLAUDE
    assert skill.detect_host({}) == skill.DEFAULT_HOST


def test_detect_host_ignores_an_empty_marker() -> None:
    """An empty marker value is not a present host (truthiness, not membership)."""
    assert skill.detect_host({"CLAUDECODE": ""}) == skill.DEFAULT_HOST


def test_host_prefix_detects_from_the_environment() -> None:
    """With no override the prefix follows the detected host."""
    assert skill.host_prefix({"CLAUDECODE": "1"}) == "/"
    assert skill.host_prefix({"CODEX_THREAD_ID": "abc"}) == "$"
    assert skill.host_prefix({}) == "/"


def test_host_prefix_override_short_circuits_detection() -> None:
    """An override sets the prefix and the environment is not consulted."""
    # A Codex override wins even with the Claude marker set in the environment.
    assert skill.host_prefix({"CLAUDECODE": "1"}, override=skill.HOST_CODEX) == "$"
    assert skill.host_prefix({"CODEX_THREAD_ID": "abc"}, override=skill.HOST_CLAUDE) == "/"


def test_render_command_drops_the_md_suffix() -> None:
    """A bare command drops the ``.md`` suffix and uses no backticks."""
    command = skill.render_command(
        "/", "write-design.md", "docs/design.v0.9.0.handoff_automation.md",
    )
    assert command == "/write-design on docs/design.v0.9.0.handoff_automation.md"
    assert "`" not in command


def test_render_command_keeps_a_name_without_the_md_suffix() -> None:
    """An instruction name without a ``.md`` suffix is rendered unchanged."""
    assert skill.render_command("$", "write-plans", "docs/x.md") == "$write-plans on docs/x.md"


def test_render_command_property_invariants() -> None:
    """Every rendered command starts with the prefix, has no backtick, ends on the doc."""
    instructions = ["write-design.md", "review-ask-questions.md", "process-draft.md"]
    # Act: render across both prefixes and a spread of versions and slugs.
    for prefix in ("/", "$"):
        for version in ("v0.9.0", "v1.2.3", "v10.0"):
            for slug in ("handoff_automation", "duration_outliers", "x"):
                for instruction in instructions:
                    document = f"docs/design.{version}.{slug}.md"
                    command = skill.render_command(prefix, instruction, document)
                    # Assert: the render invariants hold for every combination.
                    assert command.startswith(prefix)
                    assert "`" not in command
                    assert " on " in command
                    assert command.endswith(document)


def _topic(tmp_path: Path) -> Topic:
    """Build a scratch docs tree with a draft and return its topic."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    draft = docs_dir / "draft.v0.9.0.handoff_automation.md"
    draft.write_text("draft", encoding="utf-8")
    return Topic(version="v0.9.0", slug="handoff_automation", draft_path=draft)


def _write(tmp_path: Path, name: str, body: str) -> None:
    """Write a document under the scratch docs folder."""
    (tmp_path / "docs" / name).write_text(body, encoding="utf-8")


# Bodies that put a document in a given state for the routing tests. A settled
# body carries a question-referenced row (| Qxx), the mark of a consolidated
# review; a seeded body carries only the decisions heading a writer may add.
_OPEN = "# x\n\n## Open questions\n\n### Q1\n"
_FRESH = "# x\n\nbody only\n"
_SETTLED_REQ = "# x\n\n## Requirement clarifications\n\n| Q01 | a |\n"
_SETTLED_DESIGN = "# x\n\n## Design decisions\n\n| Q16 | a |\n"
_SETTLED_PLAN = "# x\n\n## Implementation decisions\n\n| Q22 | a |\n"
_SEEDED_REQ = "# x\n\n## Requirement clarifications\n\n| a | b |\n"
_SEEDED_PLAN = "# x\n\n## Implementation decisions\n\n| a | b |\n"
_NO_QUESTIONS_PLAN = (
    "# x\n\n## Implementation decisions\n\n| No open questions, all decisions made |\n"
)
_REQ = "feature-request.v0.9.0.handoff_automation.md"
_DESIGN = "design.v0.9.0.handoff_automation.md"
_PLAN = "plan.v0.9.0.handoff_automation.md"
_CLAUDE = {"CLAUDECODE": "1"}


def test_next_command_off_slug_branch_processes_the_draft(tmp_path: Path) -> None:
    """Off the slug branch a lone draft routes to process-draft."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "main", _CLAUDE)
    assert command == "/process-draft on docs/draft.v0.9.0.handoff_automation.md"


def test_next_command_on_slug_branch_writes_the_requirement(tmp_path: Path) -> None:
    """On the slug branch a lone draft routes to write-requirement."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/write-requirement on docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_open_questions_requirement_consolidates(tmp_path: Path) -> None:
    """A requirement still carrying open questions routes to consolidate."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _OPEN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/consolidate-then-review-ask-questions on "
        "docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_fresh_requirement_reviews(tmp_path: Path) -> None:
    """A fresh requirement (no markers) routes to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/review-ask-questions on docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_settled_requirement_writes_the_design(tmp_path: Path) -> None:
    """A requirement carrying a decisions table advances to write-design."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/write-design on docs/design.v0.9.0.handoff_automation.md"


def test_next_command_fresh_design_reviews(tmp_path: Path) -> None:
    """A settled requirement and a fresh design route to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/review-ask-questions on docs/design.v0.9.0.handoff_automation.md"


def test_next_command_settled_design_writes_the_plans(tmp_path: Path) -> None:
    """A settled requirement and a settled design advance to write-plans."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/write-plans on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_fresh_plan_reviews(tmp_path: Path) -> None:
    """A fresh plan, the earlier docs settled, routes to review-ask-questions."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _FRESH)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/review-ask-questions on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_settled_plan_implements(tmp_path: Path) -> None:
    """A settled plan, the earlier docs settled, advances to implement-step."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SETTLED_PLAN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_seeded_plan_decisions_still_reviews(tmp_path: Path) -> None:
    """A fresh plan seeding a decisions heading without Qxx rows still reviews.

    This pins the v9.14.0 regression: a writer-seeded ``## Implementation
    decisions`` section made the routing skip the plan review and jump to
    implement-step before any review round had run.
    """
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SEEDED_PLAN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/review-ask-questions on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_seeded_requirement_decisions_still_reviews(tmp_path: Path) -> None:
    """A fresh requirement seeding a decisions heading without Qxx rows still reviews."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SEEDED_REQ)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == (
        "/review-ask-questions on docs/feature-request.v0.9.0.handoff_automation.md"
    )


def test_next_command_no_open_questions_row_advances(tmp_path: Path) -> None:
    """The settled row a no-question review writes advances past the review."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _NO_QUESTIONS_PLAN)
    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)
    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_settled_plan_implements_the_validation_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A settled plan with validation context names the current plan step."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SETTLED_PLAN)
    _write(tmp_path, "plan.v0.9.0.handoff_automation.validation.md", _VALIDATION_TWO_STEPS)
    monkeypatch.setattr(skill.git, "fork_point", lambda _root: "base")
    monkeypatch.setattr(
        skill.git,
        "has_step_commit",
        lambda _root, number, _base: number == "1",
    )

    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)

    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md step 2"


def test_next_command_settled_plan_prepares_release_when_terminal(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A committed last validation step routes to the release command."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SETTLED_PLAN)
    _write(tmp_path, "plan.v0.9.0.handoff_automation.validation.md", _VALIDATION_TWO_STEPS_DONE)
    monkeypatch.setattr(skill.git, "fork_point", lambda _root: "base")
    monkeypatch.setattr(
        skill.git,
        "has_step_commit",
        lambda _root, number, _base: number == "2",
    )

    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)

    assert command == "/prepare-release"


def test_next_command_settled_plan_ignores_empty_validation_plan(tmp_path: Path) -> None:
    """A validation plan with no parsed steps leaves the implement command bare."""
    topic = _topic(tmp_path)
    _write(tmp_path, _REQ, _SETTLED_REQ)
    _write(tmp_path, _DESIGN, _SETTLED_DESIGN)
    _write(tmp_path, _PLAN, _SETTLED_PLAN)
    _write(tmp_path, "plan.v0.9.0.handoff_automation.validation.md", "# no steps\n")

    command = skill.next_command(tmp_path, topic, "handoff_automation", _CLAUDE)

    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md"


def test_next_command_uses_the_codex_prefix(tmp_path: Path) -> None:
    """The host prefix follows the environment, here Codex."""
    topic = _topic(tmp_path)
    command = skill.next_command(tmp_path, topic, "main", {"CODEX_THREAD_ID": "x"})
    assert command == "$process-draft on docs/draft.v0.9.0.handoff_automation.md"


def test_forced_command_unknown_skill_returns_none(tmp_path: Path) -> None:
    """An unknown forced skill name yields None."""
    assert skill.forced_command(tmp_path, _topic(tmp_path), "nope", _CLAUDE) is None


def test_forced_command_draft_role_names_the_draft(tmp_path: Path) -> None:
    """The process-draft forced skill names the draft (the draft role)."""
    command = skill.forced_command(tmp_path, _topic(tmp_path), "process-draft", _CLAUDE)
    assert command == "/process-draft on docs/draft.v0.9.0.handoff_automation.md"


def _patch_resolution(
    monkeypatch: pytest.MonkeyPatch,
    topics: list[Topic],
    branch: str,
) -> None:
    """Patch the topic resolution so run_skill resolves off the given topics."""
    def resolve(candidates: list[Topic], _record: object, _branch: str) -> Topic | None:
        return candidates[0] if candidates else None

    monkeypatch.setattr(skill.git, "current_branch", lambda _root: branch)
    monkeypatch.setattr(skill.docs, "relevant_drafts", lambda _root, _cwd: topics)
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: None)
    monkeypatch.setattr(skill.handoff, "resolve_topic", resolve)


def test_run_skill_prints_the_next_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With no skill name, run_skill prints the disk-derived next command."""
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    _patch_resolution(monkeypatch, [_topic(tmp_path)], "main")
    code = skill.run_skill(tmp_path, None, None)
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "/process-draft on docs/draft.v0.9.0.handoff_automation.md"


def test_run_skill_with_no_topic_is_not_applicable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No resolvable topic leaves stdout empty and returns the not-applicable code."""
    _patch_resolution(monkeypatch, [], "main")
    code = skill.run_skill(tmp_path, None, None)
    captured = capsys.readouterr()
    assert code == skill.EXIT_NOT_APPLICABLE
    assert captured.out == ""
    assert "no topic" in captured.err


def test_run_skill_forced_skill_emits_when_the_document_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A forced skill prints its command when the target document exists."""
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    topic = _topic(tmp_path)
    _write(tmp_path, _DESIGN, _FRESH)
    _patch_resolution(monkeypatch, [topic], "handoff_automation")
    code = skill.run_skill(tmp_path, "write-design", None)
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "/write-design on docs/design.v0.9.0.handoff_automation.md"


def test_run_skill_forced_skill_not_applicable_without_the_document(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A forced skill whose document is absent leaves stdout empty, returns the code."""
    _patch_resolution(monkeypatch, [_topic(tmp_path)], "handoff_automation")
    code = skill.run_skill(tmp_path, "write-design", None)
    captured = capsys.readouterr()
    assert code == skill.EXIT_NOT_APPLICABLE
    assert captured.out == ""
    assert "write-design" in captured.err


def test_main_dispatches_the_skill_subcommand(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The hub parses the skill subcommand with its name and host, then dispatches."""
    captured: dict[str, object] = {}

    def fake_run_skill(
        root: Path,
        skill_name: str | None,
        host_override: str | None,
        after_commit: str | None,
    ) -> int:
        captured["call"] = (root, skill_name, host_override, after_commit)
        return 0

    monkeypatch.setattr(prompt_workflow.skill, "run_skill", fake_run_skill)
    code = prompt_workflow.main(
        ["skill", "write-design", "--host", "codex", "--root", str(tmp_path)],
    )
    assert code == 0
    assert captured["call"] == (tmp_path.resolve(), "write-design", "codex", None)


_VALIDATION_TWO_STEPS = (
    "# v\n\n## Step 1.\n\n### Analysis of Step 1 implementation state\n\n"
    "Yes. Step 1 has been fully implemented.\n\n"
    "## Step 2.\n\n### Analysis of Step 2 implementation state\n\n"
    "Not started. Step 2 is not implemented because x.\n"
)
_VALIDATION_TWO_STEPS_DONE = (
    "# v\n\n## Step 1.\n\n### Analysis of Step 1 implementation state\n\n"
    "Yes. Step 1 has been fully implemented.\n\n"
    "## Step 2.\n\n### Analysis of Step 2 implementation state\n\n"
    "Yes. Step 2 has been fully implemented.\n"
)


def _setup_plan_tree(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    validation_text: str | None,
) -> None:
    """Lay down a plan (and optionally its validation plan) and wire resolution."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    (docs_dir / "draft.v0.9.0.handoff_automation.md").write_text("d", encoding="utf-8")
    (docs_dir / "plan.v0.9.0.handoff_automation.md").write_text("# plan\n", encoding="utf-8")
    if validation_text is not None:
        (docs_dir / "plan.v0.9.0.handoff_automation.validation.md").write_text(
            validation_text,
            encoding="utf-8",
        )
    _patch_resolution(monkeypatch, [_topic(tmp_path)], "handoff_automation")


def test_plan_topics_skip_invalid_and_unpaired_validation_plans(tmp_path: Path) -> None:
    """Only validation plans with a matching plan become post-commit candidates."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "plan.nope.topic.validation.md").write_text("bad version", encoding="utf-8")
    (docs_dir / "plan.v0.9.0.validation.md").write_text("missing slug", encoding="utf-8")
    (docs_dir / "plan.v0.9.0.orphan.validation.md").write_text("no plan", encoding="utf-8")
    (docs_dir / "plan.v0.9.0.handoff_automation.md").write_text("# plan\n", encoding="utf-8")
    (docs_dir / "plan.v0.9.0.handoff_automation.validation.md").write_text(
        _VALIDATION_TWO_STEPS,
        encoding="utf-8",
    )

    topics = skill._plan_topics(tmp_path)

    assert [(topic.version, topic.slug) for topic in topics] == [
        ("v0.9.0", "handoff_automation"),
    ]


def test_main_dispatches_the_skill_after_commit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The hub parses --after-commit and dispatches it to run_skill."""
    captured: dict[str, object] = {}

    def fake_run_skill(
        root: Path,
        skill_name: str | None,
        host_override: str | None,
        after_commit: str | None,
    ) -> int:
        captured["call"] = (root, skill_name, host_override, after_commit)
        return 0

    monkeypatch.setattr(prompt_workflow.skill, "run_skill", fake_run_skill)
    code = prompt_workflow.main(["skill", "--after-commit", "2", "--root", str(tmp_path)])
    assert code == 0
    assert captured["call"] == (tmp_path.resolve(), None, None, "2")


def test_post_commit_command_implements_the_next_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The step after the committed one gives an implement-step command."""
    _setup_plan_tree(monkeypatch, tmp_path, _VALIDATION_TWO_STEPS)
    command = skill.post_commit_command(tmp_path, "1", _CLAUDE)
    assert command == "/implement-step on docs/plan.v0.9.0.handoff_automation.md step 2"


def test_post_commit_command_resolves_from_plan_when_draft_was_renamed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The commit gate chains from plan files when no draft topic resolves."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "plan.v9.11.0.git_hot_path.md").write_text("# plan\n", encoding="utf-8")
    (docs_dir / "plan.v9.11.0.git_hot_path.validation.md").write_text(
        _VALIDATION_TWO_STEPS,
        encoding="utf-8",
    )
    monkeypatch.setattr(skill.git, "current_branch", lambda _root: "feature/git_hot_path")
    monkeypatch.setattr(skill.docs, "relevant_drafts", lambda _root, _cwd: [])
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: None)

    command = skill.post_commit_command(tmp_path, "1", _CLAUDE)

    assert command == "/implement-step on docs/plan.v9.11.0.git_hot_path.md step 2"


def test_post_commit_command_resolves_from_memory_when_branch_is_renamed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Persisted topic memory wins when the branch no longer names the plan."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "plan.v9.11.0.git_hot_path.md").write_text("# plan\n", encoding="utf-8")
    (docs_dir / "plan.v9.11.0.git_hot_path.validation.md").write_text(
        _VALIDATION_TWO_STEPS,
        encoding="utf-8",
    )
    memory.write_memory(
        tmp_path,
        MemoryRecord(
            branch="feature/old-name",
            version="v9.11.0",
            topic="git_hot_path",
            step=12,
            instruction="group-commits-msg.md",
            plan_step="1",
        ),
    )
    monkeypatch.setattr(skill.git, "current_branch", lambda _root: "release/wrong-name")
    monkeypatch.setattr(skill.docs, "relevant_drafts", lambda _root, _cwd: [])

    command = skill.post_commit_command(tmp_path, "1", _CLAUDE)

    assert command == "/implement-step on docs/plan.v9.11.0.git_hot_path.md step 2"


def test_post_commit_command_prepares_release_after_the_last_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Once the committed step was the last, the command is prepare-release."""
    _setup_plan_tree(monkeypatch, tmp_path, _VALIDATION_TWO_STEPS)
    assert skill.post_commit_command(tmp_path, "2", _CLAUDE) == "/prepare-release"


def test_post_commit_command_none_without_a_validation_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With no validation plan (a standalone commit) there is no contextual command."""
    _setup_plan_tree(monkeypatch, tmp_path, None)
    assert skill.post_commit_command(tmp_path, "1", _CLAUDE) is None


def test_post_commit_command_none_for_an_unknown_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A committed step not in the plan yields no contextual command."""
    _setup_plan_tree(monkeypatch, tmp_path, _VALIDATION_TWO_STEPS)
    assert skill.post_commit_command(tmp_path, "9", _CLAUDE) is None


def test_post_commit_command_none_without_a_topic(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No resolvable topic yields no contextual command."""
    _patch_resolution(monkeypatch, [], "main")
    assert skill.post_commit_command(tmp_path, "1", _CLAUDE) is None


def test_post_commit_command_ignores_unmatched_single_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A lone plan is not enough on an unrelated branch."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "plan.v9.11.0.git_hot_path.md").write_text("# plan\n", encoding="utf-8")
    (docs_dir / "plan.v9.11.0.git_hot_path.validation.md").write_text(
        _VALIDATION_TWO_STEPS,
        encoding="utf-8",
    )
    monkeypatch.setattr(skill.git, "current_branch", lambda _root: "main")
    monkeypatch.setattr(skill.docs, "relevant_drafts", lambda _root, _cwd: [])
    monkeypatch.setattr(skill.memory, "read_memory", lambda _root: None)

    assert skill.post_commit_command(tmp_path, "1", _CLAUDE) is None


def test_run_skill_after_commit_emits_the_next_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """run_skill with after_commit prints the post-commit next action."""
    monkeypatch.setenv("CLAUDECODE", "1")
    monkeypatch.delenv("CODEX_THREAD_ID", raising=False)
    _setup_plan_tree(monkeypatch, tmp_path, _VALIDATION_TWO_STEPS)
    code = skill.run_skill(tmp_path, None, None, "1")
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "/implement-step on docs/plan.v0.9.0.handoff_automation.md step 2"


def test_run_skill_after_commit_not_applicable_without_a_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """run_skill with after_commit and no plan leaves stdout empty, returns the code."""
    _setup_plan_tree(monkeypatch, tmp_path, None)
    code = skill.run_skill(tmp_path, None, None, "1")
    captured = capsys.readouterr()
    assert code == skill.EXIT_NOT_APPLICABLE
    assert captured.out == ""
    assert "no next step" in captured.err


# eof
