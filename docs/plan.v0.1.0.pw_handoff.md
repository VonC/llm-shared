# v0.1.0 pw handoff implementation plan -- the handoff subcommand and its instruction sections

This version turns the manual menu cycle of `pw` into an automatic chain: a `pw handoff <task> <x>` subcommand that produces the next cycle prompt with no menu, plus a `## Handoff` section in the three cycle instructions that runs it.

- **Resolution core**: a new `tools/prompt_workflow_handoff.py` maps a task word to a cycle action, routes `after-check` from the validation status, and resolves the topic without a menu.
- **CLI wiring**: `tools/prompt_workflow.py` gains a `handoff` subcommand that reuses `build_cycle_prompt`, `deliver_prompt`, `stage_all` and `write_memory`.
- **Instruction sections**: `implement-step.md`, `implement-missing-step.md` and `implementation-check.md` each gain a `## Handoff` section that names the call and tells the model to follow the returned prompt.

## Plan goal for v0.1.0 pw handoff

Implement the handoff feature described in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md), decisions Q56 to Q64, in ordered steps that keep every file inside the line budget and reach the repo coverage gate.

- **Step 1 goal**: the pure resolution core in a new module — task-to-action mapping (Q57, Q62), `after-check` routing (Q58), the handed-step build with validation and mismatch warning (Q59), and the non-interactive topic resolution (Q63).
- **Step 2 goal**: the `handoff` subcommand and its orchestration in `prompt_workflow.py` — argparse dispatch, then build, deliver (Q60) and record (Q61).
- **Step 3 goal**: the `## Handoff` section in the three cycle instructions (Q64).
- **Step 4 goal**: an acceptance scenario exercising the three transitions end to end.

---

## Scope anchors for v0.1.0 pw handoff plan

This plan implements the handoff design from [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md), targeting these outcomes:

1. `pw handoff check <x>` writes the check prompt for step `x`; `pw handoff after-check <x>` writes the implement-missing prompt on a `No` step and the commit prompt on a `Yes` step; `pw handoff implement-missing <x>` and `pw handoff commit <x>` write those prompts directly for a manual call.
2. A handoff delivers the prompt the way an interactive run does (`a.prompt.txt`, clipboard, stdout fallback) and records `a.prompt_memory`, and the commit handoff stages `git add -A` and empties `a.commit`.
3. The three cycle instructions carry a `## Handoff` section so a finished step runs the subcommand and follows the returned prompt with no human menu.

The following are explicitly **in scope**:

- The `handoff` subcommand and the four task tokens `check`, `after-check`, `implement-missing`, `commit` (Q57, Q62).
- pw-side branch routing from the `Analysis of Step x` status line (Q58).
- The handed-step build with existence validation and a derived-`x` mismatch warning (Q59).
- Topic resolution from a single draft or the branch lock, with a `pw --pick` refusal otherwise (Q63).
- The `## Handoff` instruction sections (Q64).

The following are explicitly **deferred** to a later version:

- Any change to the interactive menu cycle (steps 8 to 11) beyond reusing its prompt builders.
- A guard that refuses a manual `commit` on a `No` step: Q62 accepted that manual call as unguarded.

---

## File-based IO cost clarification for v0.1.0 pw handoff

`pw` is a one-shot CLI, not a service, so there is no response path to bound. The handoff path keeps the same tiny IO the interactive cycle already pays:

- One read of the validation plan (`parse_validation_steps`) and one read of the plan heading (`read_step_title`) per call.
- A bounded set of git reads (`status_entries`, `fork_point`, `has_step_commit`, `staged_files`) already used by `compute_cycle`.
- Writes limited to `a.prompt.txt`, `a.prompt_memory`, and, for the commit task, `a.commit` plus the `git add -A` stage — the same writes the menu cycle makes (Q61).
- No directory scan is added on the handoff path beyond the draft detection the interactive run already runs.

---

## Complexity Bound Clarification for v0.1.0

The handoff path is linear in small inputs and adds no quadratic cost:

- **O(1) per handoff call** for the task-to-action mapping and the status routing.
- **O(n) per call** over the validation-plan lines (`parse_validation_steps`) and the plan-heading scan (`read_step_title`), where `n` is the document line count — the same scan the cycle already performs.

No handoff code path may introduce `O(n^2)` or `O(n log n)` cost. Any such path must be called out as a defect before merge.

---

## Confirmed technical facts for v0.1.0 plan viability

These facts come from direct inspection of the current `tools/` tree.

**Files at or approaching the 550-line risk threshold** (must not grow in place):

- `tools/prompt_workflow_plan.py`: **470 lines** -- the handoff resolution must NOT be added here; it goes in the new `tools/prompt_workflow_handoff.py` so this file stays well under 650.
- `tests/unit/tools/test_prompt_workflow_main.py`: **574 lines** -- already over 550; handoff tests must NOT be added here. They go in the new `tests/unit/tools/test_prompt_workflow_handoff.py`.

**Files safe to extend** (current lines, expected additions):

- `tools/prompt_workflow.py`: 370 -- adds the `handoff` subparser and a lean `run_handoff` that delegates resolution to the new module; expected end size around 450, under budget.
- `tools/prompt_workflow.steps.json`: 130 -- unchanged; the handoff reuses the existing step-8, step-9 and step-10 alternatives.

**What does not exist yet (all new for v0.1.0)**:

- `tools/prompt_workflow_handoff.py`.
- `tests/unit/tools/test_prompt_workflow_handoff.py`.

**Other confirmed technical facts that affect plan shape**:

- **Reused builders**: `prompt_workflow_plan.build_cycle_prompt`, `parse_validation_steps`, `derive_x`, `CycleState`, `CycleAction`, and `prompt_workflow_git.stage_all`/`status_entries`/`has_step_commit`/`fork_point` already do the work the handoff needs; the new module orchestrates them, it does not reimplement them.
- **Topic helpers live in `prompt_workflow.py`**: `_memory_matches` and `_locked_topic` resolve the branch lock today; the non-interactive resolver reuses that logic, so it takes `(topics, record, branch)` and returns a `Topic` or None to avoid a circular import.
- **The three cycle instructions exist**: `instructions/implement-step.md` (52 lines), `instructions/implementation-check.md` (46), `instructions/implement-missing-step.md` (28); each gets one new `## Handoff` section.

---

## Current test-tree validation snapshot for v0.1.0 pw handoff

Existing test packages this version must not break:

- `tests/unit/tools/test_prompt_workflow_main.py` (574 lines) -- holds the `run`/`main` orchestration tests; only minimal edits (the subcommand still routes the no-subcommand path to `run`). Keep additions out of this file.
- `tests/unit/tools/test_prompt_workflow_plan.py` (314) and `test_prompt_workflow_plan_prompts.py` (442) -- cover the cycle builders the handoff reuses; no change expected.
- `tests/unit/tools/test_prompt_workflow_acceptance.py` -- holds the end-to-end scenario; the Step 4 acceptance case is added here only if it stays under budget, otherwise in the new handoff test file.

New test leaf files to create for v0.1.0:

- `tests/unit/tools/test_prompt_workflow_handoff.py` -- unit tests for the new module and the `run_handoff` orchestration.

`__init__.py` note: confirm `tools/__init__.py` and `tests/unit/tools/__init__.py` and update them only if they enumerate modules; an empty-package layout needs no edit for a new module.

---

## Shared execution command checklist for all v0.1.0 pw handoff steps

Apply this checklist for every numbered step, filling in the step-specific paths.

1. Count lines before edits on all step files: `wc -l <step files>`.
2. Apply the tests-first changes described under the step implementation section.
3. Run the step-targeted tests through groundhog (see the ready-to-run command).
4. Run the step grep checks.
5. Run the shared gate loop until both the focused tests and the repo gate pass in the same cycle.
6. Count lines after edits and compare with the step line-budget checkpoint.
7. If any Python file exceeds the repo line limit after edits, stop and apply the split guidance before committing.

---

## Ready-to-run command templates for all v0.1.0 pw handoff steps

Use these forms in each step, substituting actual paths.

- Line count before: `wc -l <step files>`
- Targeted tests: `ghog single <step test files>` (groundhog runs the tests; never a direct `pytest`)
- Grep checks: `rg <pattern> tools tests instructions`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the objective (`exit=0`): check.bat, affected tests, full suite with coverage, in order
- Line count after: `wc -l <step files>`

---

## Step 0 readiness note for v0.1.0 pw handoff

No Step 0 perf gate is needed. The handoff is a one-shot CLI path with no event loop, hot loop, or async work, so there is no time-bound responsiveness check to mark `xfail` and remove later. The Complexity Bound section is enforced by code review, not by a timeout gate.

---

## Numbered steps for v0.1.0 pw handoff

### Step 1. Handoff resolution core in a new module

#### Step 1 -- analysis and intent for the resolution core

Issues to address:

- The cycle today only resolves its action from an interactive menu (`build_cycle_options`); there is no way to name a task and a step and get its action.
- `compute_cycle` derives `x` from git; the handoff must instead build the cycle state for an explicitly named step, validating that step exists (Q59).
- After a check, the next task depends on the `Analysis of Step x` status line; that routing must live in one place (Q58).
- A non-interactive call cannot show the topic menu, so topic resolution must collapse to the single-draft or branch-lock case (Q63).

Fix intent:

- Add `tools/prompt_workflow_handoff.py` with pure functions and no terminal IO.
- `TASK_TOKENS`: the accepted set `{check, after-check, implement-missing, commit}` (Q57, Q62).
- `cycle_state_for_step(root, state, step)`: parse the validation plan, find the `PlanStep` whose `number == step` (raise `PromptWorkflowError` when absent, Q59), and build a `CycleState` with that step's `verified`/`not_implemented` and the working-tree flags from `git.status_entries` (mirroring `compute_cycle`).
- `derived_mismatch(root, state, branch_start, step)`: return the derived `x` from `derive_x` when it differs from `step`, for the caller to warn (Q59), else None.
- `action_for_task(task, cycle)`: map `check` to `CycleAction(kind="check")`, `implement-missing` to `CycleAction(kind="implement", missing=True)`, `commit` to `CycleAction(kind="commit", stage_all=True)`, and `after-check` to the implement-missing action when `cycle.not_implemented`, the commit action when `cycle.verified`, else raise a clear `PromptWorkflowError` (the check left no `Yes`/`No`).
- `resolve_topic(topics, record, branch)`: return the single topic, or the branch-locked one, else None (the caller refuses with a `pw --pick` message, Q63).

Expected outcome:

- Given a parsed validation plan and a step id, the module yields the right `CycleAction` for each task with no menu and no file writes.

Step framing:

- Design link: [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md) decisions Q57, Q58, Q59, Q62, Q63; reuses `prompt_workflow_plan` (`parse_validation_steps`, `derive_x`, `CycleState`, `CycleAction`) and `prompt_workflow_git` (`status_entries`, `fork_point`).
- Execution checklist reference: Shared execution command checklist for all v0.1.0 pw handoff steps.

#### Step 1 -- implementation for the resolution core

**Files involved**:

- `tools/prompt_workflow_handoff.py` (new).
- `tools/__init__.py` (update only if it enumerates modules).
- `tests/unit/tools/test_prompt_workflow_handoff.py` (new).
- `tests/unit/tools/__init__.py` (update only if it enumerates modules).

**Tests first**:

- `action_for_task` returns the check, implement-missing and commit actions for the direct tokens, and routes `after-check` to implement-missing on a `not_implemented` cycle and to commit on a `verified` cycle.
- `action_for_task` raises on `after-check` when the step is neither verified nor not-implemented.
- `cycle_state_for_step` builds a state for an existing step id (including a `4A` sub-step) and raises `PromptWorkflowError` for an unknown id.
- `derived_mismatch` returns the derived id when it differs, None when it matches.
- `resolve_topic` returns the lone topic, the branch-locked topic, and None when several drafts and no lock.
- Property test check: not needed — inputs are a small fixed token set and parsed step lists; example-based cases cover the branches.

**Classes and behavior**:

- `action_for_task(task: str, cycle: CycleState) -> CycleAction`: the task-to-action map and the `after-check` routing.
- `cycle_state_for_step(root, state, step) -> CycleState`: the handed-step build with existence validation.
- `derived_mismatch(root, state, branch_start, step) -> str | None`: the derived-`x` comparison.
- `resolve_topic(topics, record, branch) -> Topic | None`: the non-interactive topic pick.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "def action_for_task|def cycle_state_for_step|def resolve_topic" tools/prompt_workflow_handoff.py`.
- The new module reaches 100% unit coverage in its test file.

#### Step 1 -- addendums for the resolution core

Line-budget checkpoint:

- `tools/prompt_workflow_handoff.py`: before 0 -> target <= 200.
- `tests/unit/tools/test_prompt_workflow_handoff.py`: before 0 -> target <= 300.

Split guidance:

- If the module passes 200 lines, move `resolve_topic` and the topic-lock helpers into a small `tools/prompt_workflow_handoff_topic.py`; keep the action and cycle-state resolution in the main module.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_handoff.py; ghog day`

Time-gated status for Step 1:

- No perf gate is affected.

---

### Step 2. The handoff subcommand and its orchestration

#### Step 2 -- analysis and intent for the subcommand

Issues to address:

- `prompt_workflow.py` has a single flat parser (`--root`, `--debug`, `--pick`) and one `run` entry; there is no subcommand and no non-interactive path.
- The handoff must deliver and record exactly like the menu cycle (Q60, Q61), including the commit `git add -A` and the `a.commit` reset that `build_cycle_prompt` already performs.

Fix intent:

- Add a `handoff` subcommand: `pw handoff <task> <x>`, task and step as positionals (Q56). Carry `--root` and `--debug` on a shared parent parser passed to both the top-level parser and the `handoff` subparser (Q01), so they parse on either side of the subcommand; `--pick` stays top-level only. The `step` positional is a plain string, not an int, so a sub-step id such as `4A` is accepted (Q04).
- Add `run_handoff(root, task, step)`: resolve the branch and topics, call `handoff.resolve_topic` (raise `PromptWorkflowError` naming `pw --pick` when None, Q63), `compute_state`, `fork_point`, `handoff.cycle_state_for_step`, log a warning when `handoff.derived_mismatch` is not None (Q59), `handoff.action_for_task`, run `git.stage_all` when `action.stage_all`, `build_cycle_prompt`, `deliver_prompt`, and `write_memory` with the returned workflow step and `plan_step=x` (Q61).
- `run_handoff` lives in `prompt_workflow.py`, next to `deliver_prompt`, so there is no circular import (Q02); it stays lean by delegating all resolution to the new module, and `prompt_workflow.py` ends near 450, under the 550 budget.
- Every refusal -- no topic (Q63), an unknown step (Q59) or task (Q62), or an `after-check` with no `Yes`/`No` -- raises `PromptWorkflowError`, which `__main__` turns into `EXIT_FATAL` (2), so the calling instruction branches on that non-zero code (Q03).

Expected outcome:

- `pw handoff check 2` writes the check prompt to `a.prompt.txt`, copies it to the clipboard, and records the memory; `pw handoff commit 2` stages `git add -A`, empties `a.commit`, and writes the commit prompt; `pw handoff after-check 2` writes implement-missing or commit by the status line.

Step framing:

- Design link: Q56, Q58, Q59, Q60, Q61; reuses `deliver_prompt`, `prompt_workflow_plan.build_cycle_prompt`, `prompt_workflow_git.stage_all`, `prompt_workflow_memory.write_memory`.
- Execution checklist reference: Shared execution command checklist for all v0.1.0 pw handoff steps.

#### Step 2 -- implementation for the subcommand

**Files involved**:

- `tools/prompt_workflow.py` (update).
- `tools/prompt_workflow_handoff.py` (update only if a thin orchestration helper is shared).
- `tests/unit/tools/test_prompt_workflow_handoff.py` (update).
- `tests/unit/tools/test_prompt_workflow_main.py` (update: assert the parser still routes the no-subcommand path to `run`, minimal additions only).

**Tests first**:

- `run_handoff` for `check` writes the prompt and records `MemoryRecord(step=9, instruction="implementation-check.md", plan_step="2")`, with no `stage_all` call.
- `run_handoff` for `commit` calls `stage_all` once and records `step=10`.
- `run_handoff` for `after-check` on a `No` step yields the implement-missing prompt; on a `Yes` step yields the commit prompt.
- `run_handoff` refuses (non-zero, message names `pw --pick`) when `resolve_topic` returns None.
- `run_handoff` logs a warning when the handed step differs from the derived `x`.
- `main(["handoff", "check", "2", "--root", str(tmp)])` dispatches to `run_handoff`; `main(["--pick", "--root", str(tmp)])` and `main(["--root", str(tmp)])` still dispatch to `run`.

**Classes and behavior**:

- `_get_arg_parser`: a shared parent parser defines `--root` and `--debug`; the top-level parser (with `--pick`) and the `handoff` subparser both take `parents=[common]` (Q01). The `handoff` subparser carries `task` and a plain-string `step` positional (Q04).
- `main`: dispatch to `run_handoff` when the `handoff` command is selected, else to `run`.
- `run_handoff(root, task, step) -> int`: the orchestration above; returns 0 on success and raises `PromptWorkflowError` (turned into `EXIT_FATAL` by `__main__`) on any refusal (Q03).

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "handoff" tools/prompt_workflow.py`.
- The clipboard is monkeypatched in tests (as in `test_prompt_workflow_main.py`); `a.prompt.txt` carries the expected prompt and `a.prompt_memory` the expected record.

#### Step 2 -- addendums for the subcommand

Line-budget checkpoint:

- `tools/prompt_workflow.py`: before 370 -> target <= 470 (stop and split the topic-resolution glue into the handoff module if it would pass 520).
- `tests/unit/tools/test_prompt_workflow_handoff.py`: before <Step 1 size> -> target <= 480.
- `tests/unit/tools/test_prompt_workflow_main.py`: before 574 -> target <= 600 (add at most the two dispatch assertions; if it would pass 600, move them to the handoff test file).

Split guidance:

- `run_handoff` stays in `prompt_workflow.py` (Q02); the file ends near 450, so the split is not triggered. Only if a later change pushes it past 520, move `run_handoff` to `tools/prompt_workflow_handoff.py` with `deliver_prompt` and `set_clipboard_text` passed in as callbacks to avoid a circular import.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_handoff.py tests/unit/tools/test_prompt_workflow_main.py; ghog day`

Time-gated status for Step 2:

- No perf gate is affected.

---

### Step 3. The `## Handoff` section in the three cycle instructions

#### Step 3 -- analysis and intent for the instruction sections

Issues to address:

- The subcommand exists after Step 2 but nothing runs it; the chain fires only when each cycle instruction tells the model to (Q64).
- Per the Q64 refinement, the wiring is a clear, detailed `## Handoff` section, not a one-line directive.

Fix intent:

- Add a `## Handoff` section to each of the three cycle instructions. Each section states the exact `pw handoff` call, its purpose, and that the model must then read `a.prompt.txt` and follow the instructions of the returned prompt.
- `implement-step.md` and `implement-missing-step.md`: `pw handoff check <x>` (hand to the check for the step just implemented).
- `implementation-check.md`: `pw handoff after-check <x>` (pw routes to implement-missing on `No` or commit on `Yes` from the status line just written).

Expected outcome:

- A finished cycle step ends by running its handoff call and continuing on the returned prompt, with no human menu.

Step framing:

- Design link: Q64 and the `## Handoff` refinement in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md); tokens from Q62.
- Execution checklist reference: Shared execution command checklist for all v0.1.0 pw handoff steps.

#### Step 3 -- implementation for the instruction sections

**Files involved**:

- `instructions/implement-step.md` (update).
- `instructions/implement-missing-step.md` (update).
- `instructions/implementation-check.md` (update).

**Tests first**:

- These are instruction documents, not code, so there is no unit test. The grep checks below stand in as the verification, and the Step 4 acceptance scenario proves the call shape the sections name.

**Classes and behavior**:

- Each `## Handoff` section: one short paragraph naming the call, the `<x>` it uses (the step the instruction just worked on), the purpose, and the order to read `a.prompt.txt` and follow it. Follow `markdown.md` (unique section title, single-space list markers, blank lines around lists).

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`) -- unchanged, since no code changed.
- `rg "## Handoff" instructions/implement-step.md instructions/implement-missing-step.md instructions/implementation-check.md` returns three hits.
- `rg "pw handoff (check|after-check)" instructions` shows `check` in the two implement instructions and `after-check` in the check instruction.

#### Step 3 -- addendums for the instruction sections

Line-budget checkpoint:

- `instructions/implement-step.md`: before 52 -> target <= 80 (markdown, well under the code limit).
- `instructions/implementation-check.md`: before 46 -> target <= 75.
- `instructions/implement-missing-step.md`: before 28 -> target <= 55.

Split guidance:

- Not applicable: the 650-line rule targets Python files; these short markdown files stay small.

Full workflow timing run readiness:

- `ghog day` (a no-op walk after a green Step 2, since no Python changed).

Time-gated status for Step 3:

- No perf gate is affected.

---

### Step 4. Acceptance test for the handoff chain

#### Step 4 -- analysis and intent for the acceptance scenario

Issues to address:

- The unit tests cover each function; an end-to-end scenario must prove the three transitions produce the right prompt against a temp project and validation plan.

Fix intent:

- Add an acceptance test that builds a temp project (draft, plan, validation plan with an `Analysis of Step 2` section), then drives `main(["handoff", ...])` for `check`, `after-check` on a `Yes` and on a `No` validation plan, and `commit`, asserting the delivered `a.prompt.txt` names the expected instruction and the memory records the expected step.

Expected outcome:

- The handoff chain is proven for the three transitions in one larger, integration-level test.

Step framing:

- Design link: the three transitions in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md); larger than a unit test, so it carries no 100% coverage target.
- Execution checklist reference: Shared execution command checklist for all v0.1.0 pw handoff steps.

#### Step 4 -- implementation for the acceptance scenario

**Files involved**:

- `tests/unit/tools/test_prompt_workflow_acceptance.py` (update if under budget) or `tests/unit/tools/test_prompt_workflow_handoff.py` (new acceptance case) -- choose by the budget check below.

**Tests first**:

- Acceptance: `check` writes the `implementation-check.md` prompt for step 2; `after-check` on a `Yes` step writes the `group-commits-msg.md` prompt and stages all; `after-check` on a `No` step writes the `implement-missing-step.md` prompt; `commit` writes the commit prompt and empties `a.commit`.
- The git reads are driven by monkeypatching `prompt_workflow_git` and the clipboard, the same style as `test_prompt_workflow_acceptance.py` (Q05); no real git process is spun, since the git helpers have their own tests in `test_prompt_workflow_git.py`.

**Classes and behavior**:

- One acceptance scenario function per transition, or one parametrized scenario, asserting the delivered prompt and the recorded memory.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "handoff" tests/unit/tools/test_prompt_workflow_acceptance.py` (or the handoff test file) shows the new scenario.
- The full suite stays green and at the coverage gate.

#### Step 4 -- addendums for the acceptance scenario

Line-budget checkpoint:

- `tests/unit/tools/test_prompt_workflow_acceptance.py`: before `<current>` -> target <= 600; if the additions would pass 600, put the acceptance case in `tests/unit/tools/test_prompt_workflow_handoff.py` instead.

Split guidance:

- Keep the acceptance scenario in the handoff test file when the existing acceptance file is near budget.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_acceptance.py; ghog day`

Time-gated status for Step 4:

- No perf gate is affected.

---

## Implementation decisions for v0.1.0 pw handoff

The table records the implementation choices made from Q01 to Q05, the step that carries each one, and the alternatives dropped.

| Question | Decision | Integrated in | Main argument | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | `--root`/`--debug` on a shared parent parser passed to the top-level parser and the `handoff` subparser; `--pick` stays top-level | Step 2 | The global options parse on either side of the subcommand, with one definition | A2 redefine on both (drift); A3 require them before the subcommand (order trap) |
| Q02 | `run_handoff` stays in `prompt_workflow.py` beside `deliver_prompt` | Step 2 | The file stays near 450, under budget, so no circular import and no callback seam | B2 move with callbacks; B3 new shared IO module |
| Q03 | Every handoff refusal raises `PromptWorkflowError` to `EXIT_FATAL` (2) | Step 1; Step 2 | One non-zero contract the calling instruction branches on, reusing the `__main__` handler | C2 per-cause code table; C3 soft exit 0 for a refused topic |
| Q04 | The `step` positional is a plain string; `cycle_state_for_step` is the only validator | Step 1; Step 2 | One validation point that reads the real ids and accepts `4A` | D2 parser regex too (duplicate grammar); D3 no existence check |
| Q05 | The acceptance scenario monkeypatches `prompt_workflow_git` and the clipboard | Step 4 | Fast, deterministic, uniform with the suite; real git is covered in the git tests | E2 real temp repo; E3 hybrid |

Keep the document at implementation level only: files, tests, commands, budgets, rollout order, and completion checks. The design rationale stays in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md).
