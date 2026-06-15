# v0.1.0 pw handoff implementation tracking and validation

Step 1 is implemented and verified; steps 2 to 4 are not started yet.

This document tracks the implementation of the pw handoff feature step by step. Each step's status is filled by the separate implementation-check, against the current diff and repository state.

---

## File-based IO cost clarification for v0.1.0 pw handoff (implementation)

All implementation work must respect the IO classification of [`plan.v0.1.0.pw_handoff.md`](plan.v0.1.0.pw_handoff.md). The constraints carried forward:

- One read of the validation plan and one read of the plan heading per handoff call.
- Only the bounded git reads the interactive cycle already makes.
- Writes limited to `a.prompt.txt`, `a.prompt_memory`, and, for the commit task, `a.commit` plus the `git add -A` stage.
- No directory scan added beyond the existing draft detection.

---

## Complexity Bound Clarification for v0.1.0 (implementation)

The scaling target for all v0.1.0 handoff code paths is:

- **O(1) per handoff call** for the task-to-action mapping and the status routing.
- **O(n) per call** over the validation-plan lines and the plan-heading scan, the same scan the cycle already performs.

Every implemented step is reviewed against this bound in its Performance check section.

---

## Step 1. Handoff resolution core in a new module

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The new `tools/prompt_workflow_handoff.py` module carries the pure resolution core the plan asked for -- `find_plan_step`, `action_for_task`, `cycle_state_for_step`, `derived_mismatch`, `resolve_topic` and the `TASK_TOKENS` set -- and `tests/unit/tools/test_prompt_workflow_handoff.py` exercises every branch. The module owns no terminal IO and reuses the parsing, derivation and dataclasses of `prompt_workflow_plan` and the read-only git helpers, matching the design and the plan's step 1.

### Goal for Step 1

Add `tools/prompt_workflow_handoff.py` with the pure resolution core: the task-to-action map for `check`, `after-check`, `implement-missing` and `commit`, the `after-check` routing from the validation status, the handed-step build with existence validation and a derived-`x` mismatch report, and the non-interactive topic resolution.

### Step 1 improvement expectations

- `action_for_task` returns the correct `CycleAction` for each direct token and routes `after-check` to implement-missing on a `No` step and commit on a `Yes` step.
- `cycle_state_for_step` builds a state for an existing step id (including a `4A` sub-step) and raises for an unknown id.
- `resolve_topic` returns the lone or branch-locked topic and None when several drafts and no lock.

### What was implemented for Step 1

- **The resolution module**: `tools/prompt_workflow_handoff.py` adds the four task tokens and the `find_plan_step`, `action_for_task`, `cycle_state_for_step`, `derived_mismatch` and `resolve_topic` functions.
- **Task-to-action mapping (Q57, Q58, Q62)**: `action_for_task` maps `check`, `implement-missing` and `commit` to their `CycleAction`, and routes `after-check` to implement-missing on a `No` step and commit on a `Yes` step, raising on an unknown task or a placeholder status.
- **Named-step build (Q59)**: `find_plan_step` reads the named step from the validation plan and raises on a missing plan or unknown id; `cycle_state_for_step` builds the carrier `CycleState`, with only `x`, `verified` and `not_implemented` populated and the working-tree flags left False; `derived_mismatch` reports the `derive_x` step when it differs.
- **Non-interactive topic resolution (Q63)**: `resolve_topic` returns the single draft or the branch-locked topic, and None for the caller to refuse; the module-private `_topic_matches` mirrors `prompt_workflow._memory_matches` so the module never imports the interactive entry point.
- **Validation evidence**: `tests/unit/tools/test_prompt_workflow_handoff.py` covers every function and branch, and the last full `ghog day` walk passed with the suite at 100% coverage.

### New types or classes introduced for Step 1

The step introduced no new production type. The module is a set of module-level functions plus the module-private `_topic_matches` helper, and it reuses the `CycleState`, `CycleAction` and `PlanStep` dataclasses of `prompt_workflow_plan` rather than defining its own. The `TASK_TOKENS` tuple names the four accepted task words.

### Architecture check for Step 1

- **Resolution layer**: `prompt_workflow_handoff` sits beside `prompt_workflow_plan` as a pure resolution module; it reuses the plan parsing, derivation and dataclasses and the read-only git helpers, writes no files and touches no terminal, so the menu-less path stays unit-testable.
- **Dependency direction**: the module imports `prompt_workflow_plan`, `prompt_workflow_git` and the shared models, but never `prompt_workflow`, the interactive entry point, so there is no circular import; the small `_topic_matches` helper is the deliberate mirror that keeps that direction clean (design Q02).
- **No technical leak**: the module holds only resolution logic, while the git and clipboard side effects stay in the git helpers and the entry point.

No DDD-Hexagonal violation or adapter smell is visible in this step; there is nothing that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: the task-to-action mapping and the topic resolution are constant-time; `find_plan_step` and `derived_mismatch` scan the validation-plan lines once through `parse_validation_steps`, which is `O(n)` in the document line count.
- **Hot-path bound**: there is no hot path -- the module runs once per handoff call, not in a loop.
- **Plan-bound alignment**: the step stays inside the plan's bound, `O(1)` per call for the mapping and `O(n)` for the single document scan the cycle already performs.

No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **`tools/prompt_workflow_handoff.py`**: covered at 100% by `tests/unit/tools/test_prompt_workflow_handoff.py`, which exercises each function and branch -- the three direct task tokens, the `after-check` Yes/No routing and its placeholder raise, the unknown-task raise, the missing-plan and unknown-id raises of `find_plan_step`, the carrier state, the `derived_mismatch` match, difference and empty-plan cases, and the `resolve_topic` single, lock and refusal paths.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the step adds a new module and its tests; the only change to an existing file is the `prompt_workflow.py` module docstring repointed to the moved design, so no route, service or workflow behaviour changed.
- **Reporting or diagnostics**: unchanged; the module raises `PromptWorkflowError` for its refusals, the same error type the tool already uses.
- **Compatibility note**: the interactive menu cycle is untouched; the resolution core stays dormant until the step-2 subcommand calls it.

No existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. The handoff subcommand and its orchestration

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because `tools/prompt_workflow.py` has no `handoff` subcommand or `run_handoff` orchestration yet.

This status is updated by the implementation-check once the subcommand is wired.

### Goal for Step 2

Add the `pw handoff <task> <x>` subcommand to `tools/prompt_workflow.py` and a lean `run_handoff` that resolves the topic non-interactively, builds the cycle state for the named step, selects the action, stages `git add -A` for the commit task, builds the prompt with `build_cycle_prompt`, delivers it like an interactive run, and records `a.prompt_memory`.

### Step 2 improvement expectations

- `pw handoff check 2` writes the check prompt and records the step with no `stage_all` call.
- `pw handoff commit 2` stages all once and records step 10.
- `pw handoff after-check 2` writes implement-missing or commit by the status line.
- A refused topic exits non-zero with a message naming `pw --pick`; a handed/derived step mismatch logs a warning.
- The no-subcommand and `--pick` paths still route to the interactive `run`.

### What was implemented for Step 2

Not started -- filled by the implementation-check step.

### New types or classes introduced for Step 2

Not started -- filled by the implementation-check step.

### Architecture check for Step 2

Not started -- filled by the implementation-check step.

### Performance check for Step 2

Not started -- filled by the implementation-check step.

### Unit test coverage check for Step 2

Not started -- filled by the implementation-check step.

### Feature integrity for Step 2

Not started -- filled by the implementation-check step.

---

## Step 3. The Handoff section in the three cycle instructions

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the three cycle instructions carry no `## Handoff` section yet.

This status is updated by the implementation-check once the sections are added.

### Goal for Step 3

Add a clear, detailed `## Handoff` section to `instructions/implement-step.md`, `instructions/implement-missing-step.md` and `instructions/implementation-check.md`, each naming the exact `pw handoff` call (`check` for the two implement instructions, `after-check` for the check instruction), its purpose, and the order to read `a.prompt.txt` and follow the returned prompt.

### Step 3 improvement expectations

- Each of the three instructions has one `## Handoff` section.
- The two implement instructions name `pw handoff check <x>`; the check instruction names `pw handoff after-check <x>`.
- Each section tells the model to follow the instructions of the prompt the call returns.

### What was implemented for Step 3

Not started -- filled by the implementation-check step.

### New types or classes introduced for Step 3

Not started -- filled by the implementation-check step.

### Architecture check for Step 3

Not started -- filled by the implementation-check step.

### Performance check for Step 3

Not started -- filled by the implementation-check step.

### Unit test coverage check for Step 3

Not started -- filled by the implementation-check step.

### Feature integrity for Step 3

Not started -- filled by the implementation-check step.

---

## Step 4. Acceptance test for the handoff chain

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because no end-to-end handoff acceptance scenario exists yet.

This status is updated by the implementation-check once the acceptance scenario is written.

### Goal for Step 4

Add an acceptance scenario that drives `main(["handoff", ...])` for the three transitions against a temp project with a validation plan, asserting the delivered `a.prompt.txt` names the expected instruction and the memory records the expected step.

### Step 4 improvement expectations

- `check` writes the `implementation-check.md` prompt for the step.
- `after-check` writes the commit prompt on a `Yes` step and the implement-missing prompt on a `No` step.
- `commit` writes the commit prompt and empties `a.commit`.
- The full suite stays green and at the coverage gate.

### What was implemented for Step 4

Not started -- filled by the implementation-check step.

### New types or classes introduced for Step 4

Not started -- filled by the implementation-check step.

### Architecture check for Step 4

Not started -- filled by the implementation-check step.

### Performance check for Step 4

Not started -- filled by the implementation-check step.

### Unit test coverage check for Step 4

Not started -- filled by the implementation-check step.

### Feature integrity for Step 4

Not started -- filled by the implementation-check step.

---

Keep this document review-only: compare the current state to the plan, record evidence, and call out incomplete work. The design rationale stays in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md).
