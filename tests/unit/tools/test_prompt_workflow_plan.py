"""Tests for the implement-validate-group cycle of prompt_workflow.

Fix: Cover validation-plan parsing, the plan-step x derivation (keep, advance and
terminal), the working-tree classification, the cycle menu options, and the
per-step prompt building with the validation-commit requirement. Also cover the
staged-file listing, the group-commits body completion with the count and the
porcelain file list, and the a.commit reset (Q22-Q25). Also cover the plan step
title read for the check prompt, with the separator tolerance and the number-only
fallback (Q26, Q30-Q32). Also cover the implement body and the menu introduction
carrying the title and the plan document, with the title and plan-document drops
(Q33-Q37), and the commit body naming the step with its check-document Context
(Q38-Q40). Also cover lettered sub-step ids: parsing keeps the full id, the
derivation keeps a verified parent step from being hidden by a sub-step ``Not
started``, the menu labels carry the id, and the title read tells a parent from
its sub-step (Q41-Q45).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import Topic, WorkflowState
from tools.prompt_workflow_plan import PlanStep

if TYPE_CHECKING:
    import pytest

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_TOPIC = Topic(version="v9.8.0", slug="iso", draft_path=Path("docs/draft.v9.8.0.iso.md"))
_IMPLEMENT_STEP = 8
_CHECK_STEP = 9
_COMMIT_STEP = 10
_RELEASE_STEP = 11

_VALIDATION = """# Plan validation

## Step 0. Setup

### Analysis of Step 0 implementation state

Yes. Step 0 has been fully implemented.

## Step 1. Core

### Analysis of Step 1 implementation state

No. Step 1 is still incomplete.

## Step 2. Final

## Analysis of Step 2 Implementation

{Start with Yes. or No.}
"""


def _state(**overrides: object) -> WorkflowState:
    base: dict[str, object] = {
        "requirement": Path("docs/feature-request.v9.8.0.iso.md"),
        "design": Path("docs/design.v9.8.0.iso.md"),
        "plan": Path("docs/plan.v9.8.0.iso.md"),
        "validation_plan": Path("docs/plan.v9.8.0.iso.validation.md"),
        "requirement_has_open_questions": False,
        "design_has_open_questions": False,
        "memory_step": None,
    }
    base.update(overrides)
    return WorkflowState(**base)  # type: ignore[arg-type]


def test_parse_validation_steps() -> None:
    """Headings match loosely; the next non-empty line decides verified."""
    steps_found = plan.parse_validation_steps(_VALIDATION)
    assert steps_found == [
        PlanStep(number="0", verified=True),
        PlanStep(number="1", verified=False),
        PlanStep(number="2", verified=False),
    ]


def test_parse_validation_steps_keeps_substep_ids() -> None:
    """Lettered sub-steps keep their full id and never collapse to the number (Q42)."""
    text = (
        "# Plan validation\n\n"
        "### Analysis of Step 4 implementation state\n\nYes. Step 4 is done.\n\n"
        "### Analysis of Step 4A implementation state\n\nNot started.\n\n"
        "### Analysis of Step 4B implementation state\n\nNot started.\n"
    )
    assert plan.parse_validation_steps(text) == [
        PlanStep(number="4", verified=True),
        PlanStep(number="4A", verified=False),
        PlanStep(number="4B", verified=False),
    ]


def test_status_is_yes_at_end_of_file() -> None:
    """A heading with no following non-empty line is not verified."""
    text = "### Analysis of Step 5 implementation state\n\n"
    assert plan.parse_validation_steps(text) == [PlanStep(number="5", verified=False)]


def test_derive_x_keeps_base_without_commit() -> None:
    """With no commit, x is the last verified step (or the first when none)."""
    none_yes = [PlanStep("0", verified=False), PlanStep("1", verified=False)]
    assert plan.derive_x(none_yes, lambda _n: False) == ("0", False, False)

    some_yes = [PlanStep("0", verified=True), PlanStep("1", verified=True), PlanStep("2", verified=False)]
    assert plan.derive_x(some_yes, lambda _n: False) == ("1", True, False)


def test_derive_x_advances_and_terminates() -> None:
    """A recorded commit advances x, or marks the cycle terminal at the last step."""
    steps_mid = [PlanStep("0", verified=True), PlanStep("1", verified=True), PlanStep("2", verified=False)]
    assert plan.derive_x(steps_mid, lambda n: n == "1") == ("2", False, False)

    steps_last = [PlanStep("0", verified=True), PlanStep("1", verified=True)]
    assert plan.derive_x(steps_last, lambda n: n == "1") == ("1", True, True)


def test_derive_x_substep_collision_keeps_parent_verified() -> None:
    """A sub-step 'Not started' must not hide the parent step's 'Yes' (Q45)."""
    plan_steps = [
        PlanStep("3", verified=True),
        PlanStep("4", verified=True),
        PlanStep("4A", verified=False),
        PlanStep("4B", verified=False),
    ]
    # With no validation commit yet, the cycle sits on the verified parent step 4,
    # so the group-commits prompt is offered (verified stays True).
    assert plan.derive_x(plan_steps, lambda _id: False) == ("4", True, False)
    # Once step 4 is committed, the cycle advances to the empty sub-step 4A.
    assert plan.derive_x(plan_steps, lambda step_id: step_id == "4") == ("4A", False, False)


def test_compute_cycle_none_cases(tmp_path: Path) -> None:
    """No validation plan, or no steps in it, yields no cycle state."""
    assert plan.compute_cycle(tmp_path, _state(validation_plan=None), None) is None

    empty = tmp_path / "empty.validation.md"
    empty.write_text("# nothing here\n", encoding="utf-8")
    assert plan.compute_cycle(tmp_path, _state(validation_plan=empty), None) is None


def test_compute_cycle_classifies_working_tree(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The cycle state reflects the parsed steps and the git status classes."""
    validation = tmp_path / "plan.v9.8.0.iso.validation.md"
    validation.write_text(_VALIDATION, encoding="utf-8")
    monkeypatch.setattr(plan.git, "has_step_commit", lambda _root, _n, _base: False)
    monkeypatch.setattr(
        plan.git,
        "status_entries",
        lambda _root: [("M ", "tools/a.py"), (" M", "docs/x.md"), ("??", "tools/b.py")],
    )

    cycle = plan.compute_cycle(tmp_path, _state(validation_plan=validation), "base")

    assert cycle is not None
    assert cycle.x == "0"
    assert cycle.verified is True
    assert cycle.terminal is False
    assert cycle.has_code_changes is True
    assert cycle.cached is True
    assert cycle.non_cached is True


def test_build_cycle_options_terminal() -> None:
    """A terminal cycle offers only the release-notes prompt."""
    cycle = plan.CycleState(
        x="2",
        verified=True,
        terminal=True,
        has_code_changes=False,
        cached=False,
        non_cached=False,
    )
    options = plan.build_cycle_options(cycle)
    assert [label for label, _ in options] == ["Prepare release notes"]
    assert options[0][1].kind == "release"


def test_build_cycle_options_full() -> None:
    """Code changes add a check; a verified step adds both commit variants."""
    cycle = plan.CycleState(
        x="3",
        verified=True,
        terminal=False,
        has_code_changes=True,
        cached=True,
        non_cached=True,
    )
    labels = [label for label, _ in plan.build_cycle_options(cycle)]
    assert labels == [
        "Implement step 3",
        "Check step 3",
        "Commit step 3 (cached)",
        "Commit step 3 (git add -A)",
    ]


def test_build_cycle_options_minimal() -> None:
    """No code change drops the check; an unverified step drops the commit."""
    cycle = plan.CycleState(
        x="1",
        verified=False,
        terminal=False,
        has_code_changes=False,
        cached=True,
        non_cached=True,
    )
    assert [label for label, _ in plan.build_cycle_options(cycle)] == ["Implement step 1"]


def test_build_cycle_options_substep_label() -> None:
    """The menu labels carry the full sub-step id (Q41)."""
    cycle = plan.CycleState(
        x="4A",
        verified=False,
        terminal=False,
        has_code_changes=True,
        cached=False,
        non_cached=False,
    )
    assert [label for label, _ in plan.build_cycle_options(cycle)] == [
        "Implement step 4A",
        "Check step 4A",
    ]


def _cycle(**overrides: object) -> plan.CycleState:
    base: dict[str, object] = {
        "x": "2",
        "verified": True,
        "terminal": False,
        "has_code_changes": True,
        "cached": True,
        "non_cached": False,
    }
    base.update(overrides)
    return plan.CycleState(**base)  # type: ignore[arg-type]


def _prompt_state(tmp_path: Path) -> WorkflowState:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    return _state(
        requirement=docs_dir / "feature-request.v9.8.0.iso.md",
        design=docs_dir / "design.v9.8.0.iso.md",
        plan=docs_dir / "plan.v9.8.0.iso.md",
        validation_plan=docs_dir / "plan.v9.8.0.iso.validation.md",
    )


def test_build_cycle_prompt_implement(tmp_path: Path) -> None:
    """The implement prompt inlines the step title and the plan document (Q33)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    state.plan.write_text("### Step 2. Reporter routing\n", encoding="utf-8")
    action = plan.CycleAction(kind="implement", stage_all=False)

    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert (
        'Implement step 2 "Reporter routing" of the plan '
        '"docs/plan.v9.8.0.iso.md", based on the design and the plan.'
    ) in prompt
    assert "implement-step.md" in prompt
    assert workflow_step == _IMPLEMENT_STEP
    assert instruction == "implement-step.md"


def test_build_cycle_prompt_check_with_title(tmp_path: Path) -> None:
    """The check prompt names the step number and inlines the plan title (Q26, Q30)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    state.plan.write_text("### Step 2. Reporter routing\n", encoding="utf-8")
    action = plan.CycleAction(kind="check", stage_all=False)

    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert (
        'Check step 2 "Reporter routing" implementation, '
        'based on the plan "docs/plan.v9.8.0.iso.md" and the validation plan.'
    ) in prompt
    assert instruction == "implementation-check.md"
    assert workflow_step == _CHECK_STEP


def test_build_cycle_prompt_check_without_title(tmp_path: Path) -> None:
    """The check body falls back to the number only when no plan heading matches (Q31)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    state.plan.write_text("# Plan with no numbered step heading\n", encoding="utf-8")
    action = plan.CycleAction(kind="check", stage_all=False)

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert (
        "Check step 2 implementation, based on the plan "
        '"docs/plan.v9.8.0.iso.md" and the validation plan.'
    ) in prompt
    assert '""' not in prompt


def test_build_cycle_prompt_implement_without_title(tmp_path: Path) -> None:
    """The implement body drops the title but keeps the plan document (Q34)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    state.plan.write_text("# Plan with no numbered step heading\n", encoding="utf-8")
    action = plan.CycleAction(kind="implement", stage_all=False)

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert (
        'Implement step 2 of the plan "docs/plan.v9.8.0.iso.md", '
        "based on the design and the plan."
    ) in prompt
    assert '""' not in prompt


def test_build_cycle_prompt_without_plan_document(tmp_path: Path) -> None:
    """With no plan document, both the title and the plan segments drop (Q35)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _state(
        requirement=tmp_path / "docs" / "feature-request.v9.8.0.iso.md",
        design=tmp_path / "docs" / "design.v9.8.0.iso.md",
        plan=None,
        validation_plan=tmp_path / "docs" / "plan.v9.8.0.iso.validation.md",
    )
    implement = plan.CycleAction(kind="implement", stage_all=False)
    check = plan.CycleAction(kind="check", stage_all=False)

    implement_prompt, _ws, _i = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), implement,
    )
    check_prompt, _ws2, _i2 = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), check,
    )

    assert "Implement step 2 of the plan, based on the design and the plan." in implement_prompt
    assert "Check step 2 implementation, based on the plan and the validation plan." in check_prompt


def test_read_step_title_heading_and_separators(tmp_path: Path) -> None:
    """The title is the heading trailing text; `.`, `:` and `-` separators work (Q30, Q32)."""
    plan_doc = tmp_path / "plan.v9.8.0.iso.md"
    plan_doc.write_text(
        "## Numbered steps\n\n### Step 2. Reporter routing\n\n"
        "#### Step 2 -- analysis\n\n### Step 3: Metrics\n\n### Step 4 - Budgets\n",
        encoding="utf-8",
    )

    assert plan.read_step_title(plan_doc, "2") == "Reporter routing"
    assert plan.read_step_title(plan_doc, "3") == "Metrics"
    assert plan.read_step_title(plan_doc, "4") == "Budgets"


def test_read_step_title_distinguishes_substep(tmp_path: Path) -> None:
    """A parent id reads its own title, not a sub-step's, and the reverse (Q42)."""
    plan_doc = tmp_path / "plan.v9.8.0.iso.md"
    plan_doc.write_text(
        "## Numbered steps\n\n"
        "### Step 4. Duration breakdown\n\n### Step 4A. User log phase set\n",
        encoding="utf-8",
    )

    assert plan.read_step_title(plan_doc, "4") == "Duration breakdown"
    assert plan.read_step_title(plan_doc, "4A") == "User log phase set"


def test_read_step_title_missing_returns_none(tmp_path: Path) -> None:
    """A missing plan, an absent file, or a title-less heading yields None (Q31)."""
    assert plan.read_step_title(None, "2") is None
    assert plan.read_step_title(tmp_path / "absent.md", "2") is None

    present = tmp_path / "plan.md"
    present.write_text("### Step 2.\n\n# Other heading\n", encoding="utf-8")
    assert plan.read_step_title(present, "2") is None
    assert plan.read_step_title(present, "9") is None


def test_cycle_intro_full(tmp_path: Path) -> None:
    """The introduction names the step, the title and the plan document (Q33)."""
    state = _prompt_state(tmp_path)
    state.plan.write_text("### Step 2. Reporter routing\n", encoding="utf-8")

    assert (
        plan.cycle_intro(tmp_path, state, _cycle())
        == 'Regarding step 2 ("Reporter routing") from docs/plan.v9.8.0.iso.md:'
    )


def test_cycle_intro_without_title(tmp_path: Path) -> None:
    """The introduction drops the title parenthesis when no heading matches (Q34)."""
    state = _prompt_state(tmp_path)
    state.plan.write_text("# Plan with no numbered step heading\n", encoding="utf-8")

    assert (
        plan.cycle_intro(tmp_path, state, _cycle())
        == "Regarding step 2 from docs/plan.v9.8.0.iso.md:"
    )


def test_cycle_intro_without_plan(tmp_path: Path) -> None:
    """The introduction drops the plan segment when no plan is resolved (Q35)."""
    assert plan.cycle_intro(tmp_path, _state(plan=None), _cycle()) == "Regarding step 2:"


def test_build_cycle_prompt_commit_with_validation_staged(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """A commit prompt gains the validation-commit requirement when staged."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    action = plan.CycleAction(kind="commit", stage_all=False)
    monkeypatch.setattr(
        plan.git,
        "status_entries",
        lambda _root: [("M ", "docs/plan.v9.8.0.iso.validation.md")],
    )
    monkeypatch.setattr(plan.git, "staged_files", lambda _root: ["docs/plan.v9.8.0.iso.validation.md"])

    prompt, workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, _prompt_state(tmp_path), _cycle(), action,
    )

    assert "docs(iso): record step 2 validation" in prompt
    assert "M  docs/plan.v9.8.0.iso.validation.md" in prompt
    assert workflow_step == _COMMIT_STEP


def test_build_cycle_prompt_commit_without_validation_staged(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """No validation-commit requirement when the validation plan is not staged."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    action = plan.CycleAction(kind="commit", stage_all=False)
    monkeypatch.setattr(plan.git, "status_entries", lambda _root: [("M ", "tools/a.py")])
    monkeypatch.setattr(plan.git, "staged_files", lambda _root: ["tools/a.py"])

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, _prompt_state(tmp_path), _cycle(), action,
    )

    assert "record step" not in prompt


def test_build_cycle_prompt_commit_lists_staged_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The commit body lists only staged files, drops git status, and resets a.commit (Q22-Q25)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    action = plan.CycleAction(kind="commit", stage_all=False)
    monkeypatch.setattr(
        plan.git,
        "status_entries",
        lambda _root: [("M ", "docs/x.md"), ("A ", "tools/a.py"), (" M", "tools/b.py"), ("??", "tools/c.py")],
    )
    monkeypatch.setattr(plan.git, "staged_files", lambda _root: [])
    a_commit = tmp_path / "a.commit"
    a_commit.write_text("stale groups\n", encoding="utf-8")

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, _prompt_state(tmp_path), _cycle(), action,
    )

    # The body states the staged count and lists only the two staged files (Q22, Q23).
    assert "for those 2 files, per step 2 evolutions of the implementation plan" in prompt
    assert "M  docs/x.md" in prompt
    assert "A  tools/a.py" in prompt
    assert "tools/b.py" not in prompt
    assert "tools/c.py" not in prompt
    # The body carries the list, so the Context no longer mentions git status (Q24).
    assert "the current git status" not in prompt
    # a.commit is truncated to empty, not deleted (Q25).
    assert a_commit.read_text(encoding="utf-8") == ""


def test_build_cycle_prompt_commit_names_step(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The commit body names the step, title and plan after the file count (Q38, Q40)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    state.plan.write_text("### Step 2. Reporter routing\n", encoding="utf-8")
    action = plan.CycleAction(kind="commit", stage_all=False)
    monkeypatch.setattr(plan.git, "status_entries", lambda _root: [("M ", "tools/a.py")])
    monkeypatch.setattr(plan.git, "staged_files", lambda _root: ["tools/a.py"])

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert (
        'for those 1 files, per step 2 ("Reporter routing") evolutions '
        'of the implementation plan "docs/plan.v9.8.0.iso.md":'
    ) in prompt
    # The Context now lists the validation plan too (Q40).
    assert "docs/plan.v9.8.0.iso.validation.md" in prompt


def test_build_cycle_prompt_commit_without_plan(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """With no plan, the commit clause drops to per step x evolutions (Q39)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _state(
        requirement=tmp_path / "docs" / "feature-request.v9.8.0.iso.md",
        design=tmp_path / "docs" / "design.v9.8.0.iso.md",
        plan=None,
        validation_plan=tmp_path / "docs" / "plan.v9.8.0.iso.validation.md",
    )
    action = plan.CycleAction(kind="commit", stage_all=False)
    monkeypatch.setattr(plan.git, "status_entries", lambda _root: [("M ", "tools/a.py")])
    monkeypatch.setattr(plan.git, "staged_files", lambda _root: ["tools/a.py"])

    prompt, _workflow_step, _instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert "for those 1 files, per step 2 evolutions:" in prompt
    assert "implementation plan" not in prompt


def test_staged_listing_filters_to_staged(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Only staged entries are listed, formatted as porcelain XY path lines (Q22, Q23)."""
    expected_staged = 2
    monkeypatch.setattr(
        plan.git,
        "status_entries",
        lambda _root: [("M ", "a.py"), (" M", "b.py"), ("??", "c.py"), ("A ", "d.py")],
    )

    count, lines = plan.staged_listing(tmp_path)

    assert count == expected_staged
    assert lines == "M  a.py\nA  d.py"


def test_reset_a_commit_creates_and_truncates(tmp_path: Path) -> None:
    """reset_a_commit creates an empty a.commit, or truncates an existing one (Q25)."""
    target = tmp_path / "a.commit"

    plan.reset_a_commit(tmp_path)
    assert target.read_text(encoding="utf-8") == ""

    target.write_text("stale groups\n", encoding="utf-8")
    plan.reset_a_commit(tmp_path)
    assert target.read_text(encoding="utf-8") == ""


def test_build_cycle_prompt_release(tmp_path: Path) -> None:
    """The release action uses the prepare-release-notes alternative."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    action = plan.CycleAction(kind="release", stage_all=False)

    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, _prompt_state(tmp_path), _cycle(), action,
    )

    assert "prepare-release-notes.md" in prompt
    assert workflow_step == _RELEASE_STEP
    assert instruction == "prepare-release-notes.md"


# eof
