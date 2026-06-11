"""Tests for the per-step prompts of the prompt_workflow plan cycle.

Covered here, carried over from the ``test_prompt_workflow_plan.py`` Fix
history: the per-step prompt building with the validation-commit
requirement; the staged-file listing, the group-commits body completion
with the count and the porcelain file list, and the a.commit reset
(Q22-Q25); the plan step title read for the check prompt, with the
separator tolerance and the number-only fallback (Q26, Q30-Q32); the
implement body and the menu introduction carrying the title and the plan
document, with the title and plan-document drops (Q33-Q37); the commit
body naming the step with its check-document Context (Q38-Q40); the
title read telling a parent from its lettered sub-step (Q42); and the
implement-missing prompt built from the ``implement-missing-step.md``
step-8 alternative with the missing-work focus and the split-large-file
line-budget reminder (Q48-Q52).

Fix: split out of ``test_prompt_workflow_plan.py`` for the repo line
budget — the parsing, derivation, working-tree classification and menu
scenarios stay there, and the shared state builder lives in
``prompt_workflow_plan_test_support.py``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.unit.tools.prompt_workflow_plan_test_support import make_state
from tools import prompt_workflow_plan as plan
from tools import prompt_workflow_steps as steps
from tools.prompt_workflow_models import Topic

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

    from tools.prompt_workflow_models import WorkflowState

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_IMPLEMENT_STEP = 8
_CHECK_STEP = 9
_COMMIT_STEP = 10
_RELEASE_STEP = 11


def _cycle() -> plan.CycleState:
    return plan.CycleState(
        x="2",
        verified=True,
        terminal=False,
        has_code_changes=True,
        cached=True,
        non_cached=False,
    )


def _plan_path(state: WorkflowState) -> Path:
    plan_path = state.plan
    assert plan_path is not None
    return plan_path


def _prompt_state(tmp_path: Path) -> WorkflowState:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    return make_state(
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
    _plan_path(state).write_text("### Step 2. Reporter routing\n", encoding="utf-8")
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
    _plan_path(state).write_text("### Step 2. Reporter routing\n", encoding="utf-8")
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
    _plan_path(state).write_text("# Plan with no numbered step heading\n", encoding="utf-8")
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
    _plan_path(state).write_text("# Plan with no numbered step heading\n", encoding="utf-8")
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
    state = make_state(
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


def test_build_cycle_prompt_implement_missing(tmp_path: Path) -> None:
    """The implement-missing prompt focuses on the missing work and carries the split reminder (Q48-Q51)."""
    config = steps.load_steps()
    topic = Topic(version="v9.8.0", slug="iso", draft_path=tmp_path / "docs" / "draft.v9.8.0.iso.md")
    state = _prompt_state(tmp_path)
    _plan_path(state).write_text("### Step 2. Reporter routing\n", encoding="utf-8")
    action = plan.CycleAction(kind="implement", stage_all=False, missing=True)

    prompt, workflow_step, instruction = plan.build_cycle_prompt(
        "llm-shared/instructions", config, tmp_path, topic, state, _cycle(), action,
    )

    assert instruction == "implement-missing-step.md"
    assert "llm-shared/instructions/implement-missing-step.md" in prompt
    assert (
        'Implement the missing work of step 2 "Reporter routing" of the plan '
        '"docs/plan.v9.8.0.iso.md", focusing on the "Missing work for Step 2" section '
        "of the validation plan, based on the design, the plan and the validation plan."
    ) in prompt
    assert (
        "follow llm-shared/instructions/split-large-file.md and split the over-budget "
        "files line-wise; do not reduce or compress them."
    ) in prompt
    assert "docs/plan.v9.8.0.iso.validation.md" in prompt
    assert workflow_step == _IMPLEMENT_STEP


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
    _plan_path(state).write_text("### Step 2. Reporter routing\n", encoding="utf-8")

    assert (
        plan.cycle_intro(tmp_path, state, _cycle())
        == 'Regarding step 2 ("Reporter routing") from docs/plan.v9.8.0.iso.md:'
    )


def test_cycle_intro_without_title(tmp_path: Path) -> None:
    """The introduction drops the title parenthesis when no heading matches (Q34)."""
    state = _prompt_state(tmp_path)
    _plan_path(state).write_text("# Plan with no numbered step heading\n", encoding="utf-8")

    assert (
        plan.cycle_intro(tmp_path, state, _cycle())
        == "Regarding step 2 from docs/plan.v9.8.0.iso.md:"
    )


def test_cycle_intro_without_plan(tmp_path: Path) -> None:
    """The introduction drops the plan segment when no plan is resolved (Q35)."""
    assert plan.cycle_intro(tmp_path, make_state(plan=None), _cycle()) == "Regarding step 2:"


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
    _plan_path(state).write_text("### Step 2. Reporter routing\n", encoding="utf-8")
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
    state = make_state(
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
