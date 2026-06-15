# v0.1.0 pw handoff implementation tracking and validation

Not started. No step is implemented yet, since this is the initial skeleton.

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

Not started. Step 1 is not implemented because no `tools/prompt_workflow_handoff.py` module exists yet.

This status is updated by the implementation-check once the resolution core is written.

### Goal for Step 1

Add `tools/prompt_workflow_handoff.py` with the pure resolution core: the task-to-action map for `check`, `after-check`, `implement-missing` and `commit`, the `after-check` routing from the validation status, the handed-step build with existence validation and a derived-`x` mismatch report, and the non-interactive topic resolution.

### Step 1 improvement expectations

- `action_for_task` returns the correct `CycleAction` for each direct token and routes `after-check` to implement-missing on a `No` step and commit on a `Yes` step.
- `cycle_state_for_step` builds a state for an existing step id (including a `4A` sub-step) and raises for an unknown id.
- `resolve_topic` returns the lone or branch-locked topic and None when several drafts and no lock.

### What was implemented for Step 1

Not started -- filled by the implementation-check step.

### New types or classes introduced for Step 1

Not started -- filled by the implementation-check step.

### Architecture check for Step 1

Not started -- filled by the implementation-check step.

### Performance check for Step 1

Not started -- filled by the implementation-check step.

### Unit test coverage check for Step 1

Not started -- filled by the implementation-check step.

### Feature integrity for Step 1

Not started -- filled by the implementation-check step.

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
