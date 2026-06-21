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
its sub-step (Q41-Q45). Also cover the implement-missing variant: parsing records
the ``No`` status apart from ``Not started`` (Q46), the cycle state carries it, the
menu relabels the implement entry ``Implement missing for step <id>`` (Q47), and the
prompt is built from the ``implement-missing-step.md`` step-10 alternative with the
missing-work focus and the split-large-file line-budget reminder (Q48-Q52).

Fix: clear the ty and pyright findings that failed check.bat — the unused
``_cycle(**overrides)`` dict indirection became a typed constructor (every
call site passed no override), and the eight ``state.plan.write_text`` sites
narrow the optional plan path through the ``_plan_path`` helper.

Fix: split for the repo line budget — the per-step prompt building, the
step-title reads, the cycle introductions and the commit-body scenarios
moved to ``test_prompt_workflow_plan_prompts.py``, and the shared state
builder to ``prompt_workflow_plan_test_support.py``. This file keeps the
parsing, derivation, working-tree classification and menu scenarios.

Fix (menu order): the cycle menu lists its options higher workflow step first —
commit, then check, then implement — so the full and sub-step scenarios assert
the reversed label order (Q54). The implement-missing entry is the exception
and tops the menu when a ``No`` status offers it (Q55).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tests.unit.tools.prompt_workflow_plan_test_support import make_state
from tools import prompt_workflow_plan as plan
from tools.prompt_workflow_models import Topic
from tools.prompt_workflow_plan import PlanStep

if TYPE_CHECKING:
    import pytest

# pyright: reportPrivateUsage=false, reportUnknownLambdaType=false
# pyright: reportUnknownArgumentType=false
# ruff: noqa: SLF001

_TOPIC = Topic(version="v9.8.0", slug="iso", draft_path=Path("docs/draft.v9.8.0.iso.md"))

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


def test_parse_validation_steps() -> None:
    """Headings match loosely; the next non-empty line decides verified."""
    steps_found = plan.parse_validation_steps(_VALIDATION)
    assert steps_found == [
        PlanStep(number="0", verified=True),
        PlanStep(number="1", verified=False, not_implemented=True),
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


def test_parse_validation_steps_records_not_implemented() -> None:
    """A 'No' status sets not_implemented; 'Not started' and a placeholder do not (Q46)."""
    text = (
        "### Analysis of Step 1 implementation state\n\nNo, it is not implemented.\n\n"
        "### Analysis of Step 2 implementation state\n\nNot started.\n\n"
        "### Analysis of Step 3 implementation state\n\n{placeholder}\n"
    )
    assert plan.parse_validation_steps(text) == [
        PlanStep(number="1", verified=False, not_implemented=True),
        PlanStep(number="2", verified=False, not_implemented=False),
        PlanStep(number="3", verified=False, not_implemented=False),
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
    assert plan.compute_cycle(tmp_path, make_state(validation_plan=None), None) is None

    empty = tmp_path / "empty.validation.md"
    empty.write_text("# nothing here\n", encoding="utf-8")
    assert plan.compute_cycle(tmp_path, make_state(validation_plan=empty), None) is None


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

    cycle = plan.compute_cycle(tmp_path, make_state(validation_plan=validation), "base")

    assert cycle is not None
    assert cycle.x == "0"
    assert cycle.verified is True
    assert cycle.terminal is False
    assert cycle.has_code_changes is True
    assert cycle.cached is True
    assert cycle.non_cached is True
    assert cycle.not_implemented is False


def test_compute_cycle_not_implemented(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The cycle flags not_implemented when step x's status line starts with No (Q46)."""
    validation = tmp_path / "plan.v9.8.0.iso.validation.md"
    validation.write_text(
        "### Analysis of Step 1 implementation state\n\nNo, it is not implemented.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(plan.git, "has_step_commit", lambda _root, _n, _base: False)
    monkeypatch.setattr(plan.git, "status_entries", lambda _root: [])

    cycle = plan.compute_cycle(tmp_path, make_state(validation_plan=validation), "base")

    assert cycle is not None
    assert cycle.x == "1"
    assert cycle.verified is False
    assert cycle.not_implemented is True


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
    """Code changes add a check; a verified step adds both commit variants.

    The options come higher workflow step first: commit, check, implement (Q54).
    """
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
        "Commit step 3 (cached)",
        "Commit step 3 (git add -A)",
        "Check step 3",
        "Implement step 3",
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
    """The menu labels carry the full sub-step id (Q41), check before implement (Q54)."""
    cycle = plan.CycleState(
        x="4A",
        verified=False,
        terminal=False,
        has_code_changes=True,
        cached=False,
        non_cached=False,
    )
    assert [label for label, _ in plan.build_cycle_options(cycle)] == [
        "Check step 4A",
        "Implement step 4A",
    ]


def test_build_cycle_options_implement_missing() -> None:
    """A 'No' status relabels the implement entry and flags the missing action (Q47)."""
    cycle = plan.CycleState(
        x="2",
        verified=False,
        terminal=False,
        has_code_changes=False,
        cached=False,
        non_cached=False,
        not_implemented=True,
    )
    options = plan.build_cycle_options(cycle)
    assert [label for label, _ in options] == ["Implement missing for step 2"]
    action = options[0][1]
    assert action.kind == "implement"
    assert action.missing is True


def test_build_cycle_options_implement_missing_tops_menu() -> None:
    """The implement-missing entry comes before the check when offered (Q55)."""
    cycle = plan.CycleState(
        x="2",
        verified=False,
        terminal=False,
        has_code_changes=True,
        cached=False,
        non_cached=False,
        not_implemented=True,
    )
    assert [label for label, _ in plan.build_cycle_options(cycle)] == [
        "Implement missing for step 2",
        "Check step 2",
    ]


# eof
