# v0.1.0 pw handoff implementation tracking and validation

Steps 1 to 4 are implemented and verified.

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

Yes. Step 2 has been fully implemented.

`tools/prompt_workflow.py` now carries the `handoff` subcommand and a lean `run_handoff` orchestration. A shared parent parser puts `--root`/`--debug` on both the top-level parser and the `handoff` subparser (Q01), the `step` positional stays a plain string so a sub-step id such as `4A` reaches the resolver (Q04), and `run_handoff` resolves the topic without a menu, validates the named step, warns on a derived-step mismatch, maps the task to a cycle action, stages `git add -A` only for a commit, then delivers and records the prompt the same way the interactive cycle does (Q58 to Q61). `tests/unit/tools/test_prompt_workflow_handoff.py` and `tests/unit/tools/test_prompt_workflow_main.py` cover the orchestration and the dispatch, and the last full `ghog day` walk passed with the suite at 100% coverage.

### Goal for Step 2

Add the `pw handoff <task> <x>` subcommand to `tools/prompt_workflow.py` and a lean `run_handoff` that resolves the topic non-interactively, builds the cycle state for the named step, selects the action, stages `git add -A` for the commit task, builds the prompt with `build_cycle_prompt`, delivers it like an interactive run, and records `a.prompt_memory`.

### Step 2 improvement expectations

- `pw handoff check 2` writes the check prompt and records the step with no `stage_all` call.
- `pw handoff commit 2` stages all once and records step 10.
- `pw handoff after-check 2` writes implement-missing or commit by the status line.
- A refused topic exits non-zero with a message naming `pw --pick`; a handed/derived step mismatch logs a warning.
- The no-subcommand and `--pick` paths still route to the interactive `run`.

### What was implemented for Step 2

- **The `handoff` subparser (Q01, Q04, Q56)**: `_get_arg_parser` builds a shared `add_help=False` parent parser carrying `--root` and `--debug`, passed to both the top-level parser (which keeps `--pick`) and a `handoff` subparser; the subparser adds a `task` and a plain-string `step` positional, so a sub-step id such as `4A` reaches the resolver unparsed and is validated there, not by the grammar.
- **Dispatch (Q56)**: `main` reads `args.command` and routes the `handoff` command to `run_handoff(root, args.task, args.step)`, otherwise to the interactive `run(root, pick=args.pick)`.
- **The `run_handoff` orchestration (Q58 to Q61)**: it resolves the branch and topics, calls `handoff.resolve_topic` (raising a `PromptWorkflowError` that names `pw --pick` when None, Q63), `compute_state`, `git.fork_point`, `handoff.find_plan_step`, logs a warning when `handoff.derived_mismatch` differs from the handed step (Q59), maps the task with `handoff.action_for_task`, builds the carrier state with `handoff.cycle_state_for_step`, runs `git.stage_all` only when `action.stage_all`, then `plan.build_cycle_prompt`, `deliver_prompt` and `memory.write_memory` with the returned workflow step and `plan_step=cycle.x`.
- **Refusal contract (Q03)**: every refusal raises `PromptWorkflowError`, which the `__main__` guard turns into `EXIT_FATAL` (2), so the calling instruction branches on the non-zero code.
- **Validation evidence**: the unit tests assert the delivered `a.prompt.txt` and the recorded `a.prompt_memory` for each transition with the clipboard monkeypatched, and the last full `ghog day` walk reached the objective with the suite at 100% coverage.

### New types or classes introduced for Step 2

The step introduced no new production type. It adds the module-level `run_handoff` function and the `handoff` subparser wiring inside `_get_arg_parser`, and reuses the Step-1 `prompt_workflow_handoff` resolution functions, the `prompt_workflow_plan` builders and dataclasses, and the existing `MemoryRecord`. `run_handoff` lives in `prompt_workflow.py` beside `deliver_prompt` (Q02), so the file gains a function and a parser, not a class.

### Architecture check for Step 2

- **CLI and orchestration layer**: the subparser wiring and `run_handoff` sit in the `prompt_workflow.py` entry point, the right place for argument dispatch and orchestration; `run_handoff` delegates resolution to `prompt_workflow_handoff`, document and topic work to `prompt_workflow_docs` and `prompt_workflow_steps`, git reads and the stage write to `prompt_workflow_git`, prompt building to `prompt_workflow_plan`, and the memory write to `prompt_workflow_memory`.
- **Dependency direction (Q02)**: `prompt_workflow` imports `prompt_workflow_handoff`, but the handoff module never imports `prompt_workflow`, so there is no circular import and `run_handoff` stays in the entry point without a callback seam.
- **No technical leak**: the clipboard and git side effects stay behind `deliver_prompt`/`set_clipboard_text` and the git helpers; `run_handoff` only orchestrates and writes no IO of its own.
- **Girth**: `tools/prompt_workflow.py` is 489 lines, under the plan's 520 split trigger and the repo's 650 big-file gate, so no split is triggered.

No DDD-Hexagonal violation or adapter smell is visible, and the file stays within its line budget; there is nothing that needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: `run_handoff` is a constant-time dispatch over the chosen action; the task-to-action mapping, the `stage_all` gate, and the deliver and record steps are all `O(1)`.
- **Per-call cost**: the validation plan is parsed twice per call -- once by `find_plan_step` and once by `derived_mismatch` -- each `O(n)` in the document line count, and `build_cycle_prompt` reads the plan heading once; these are the same linear scans the interactive cycle pays, and the two parses are exactly the two Step-1 calls the plan's orchestration prescribes.
- **Plan-bound alignment**: the path stays inside the plan's `O(1)` mapping plus `O(n)` document-scan bound; `run_handoff` runs once per invocation with no loop and no hot path.

No, there is no performance issue that needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **`tools/prompt_workflow.py` (Step-2 additions)**: covered at 100% across `tests/unit/tools/test_prompt_workflow_handoff.py` and `tests/unit/tools/test_prompt_workflow_main.py`. The handoff tests drive `run_handoff` end to end -- the check path (no stage, records step 9), the commit path (stage once, records step 10), the `after-check` No and Yes routing, the `pw --pick` refusal when `resolve_topic` returns None, and the derived-step-mismatch warning -- so the `topic is None`, `derived is not None`, and `action.stage_all` true and false branches are all exercised. `test_main_dispatches_handoff` covers the `handoff` branch of `main` and the subparser build, while the existing `test_main_*` and the `run`/cycle tests cover the no-subcommand branch and the rest of the file.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: the interactive `run` path is unchanged; the switch to an argparse subparser keeps `--root`, `--debug` and `--pick`, and the no-subcommand and `--pick` invocations still route to `run`, asserted by `test_main_uses_root_argument`, `test_main_pick_flag` and `test_main_defaults_to_found_root`.
- **Reporting or diagnostics**: `run_handoff` reports through the existing `LOGGER` (the ready line and the mismatch warning) and raises `PromptWorkflowError` for refusals, the same error type and `EXIT_FATAL` exit contract the tool already uses.
- **Compatibility note**: the change is additive -- a new subcommand and a new orchestration function; the menu cycle, topic resolution and per-step prompt builders are untouched.

No existing feature or reporting capability appears impaired by Step 2.

---

## Step 3. The Handoff section in the three cycle instructions

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The three cycle instructions each carry one `## Handoff` section as their final section: `instructions/implement-step.md` and `instructions/implement-missing-step.md` name `pw handoff check <x>`, and `instructions/implementation-check.md` names `pw handoff after-check <x>` (Q58, Q62, Q64). Each section gives the call, the `<x>` it uses, its purpose, and the order to read `a.prompt.txt` and follow the returned prompt, matching the design wiring. The files stay well under their markdown budgets and, since no Python changed, the last full `ghog day` walk passed at 100% coverage.

### Goal for Step 3

Add a clear, detailed `## Handoff` section to `instructions/implement-step.md`, `instructions/implement-missing-step.md` and `instructions/implementation-check.md`, each naming the exact `pw handoff` call (`check` for the two implement instructions, `after-check` for the check instruction), its purpose, and the order to read `a.prompt.txt` and follow the returned prompt.

### Step 3 improvement expectations

- Each of the three instructions has one `## Handoff` section.
- The two implement instructions name `pw handoff check <x>`; the check instruction names `pw handoff after-check <x>`.
- Each section tells the model to follow the instructions of the prompt the call returns.

### What was implemented for Step 3

- **`instructions/implement-step.md` (Q62, Q64)**: a `## Handoff` section naming `pw handoff check <x>` to hand the just-implemented step to the implementation check, with `<x>` the "Step XXXX" of the conversation, and the order to read `a.prompt.txt` and follow it.
- **`instructions/implement-missing-step.md` (Q62, Q64)**: a `## Handoff` section naming the same `pw handoff check <x>` to re-check after the recorded gap is filled.
- **`instructions/implementation-check.md` (Q58, Q62, Q64)**: a `## Handoff` section naming `pw handoff after-check <x>`, stating that pw reads the `Analysis of Step x` status line and routes to the `implement-missing-step.md` prompt on `No` or the commit prompt (`group-commits-msg.md`, the `git add -A` variant) on `Yes`, so the caller cannot mis-branch.
- **Validation evidence**: `grep -c "## Handoff"` returns one hit per file (three total); `pw handoff check <x>` appears in the two implement instructions and `pw handoff after-check <x>` in the check instruction; no list marker carries more than one space; the files measure 62, 38 and 56 lines, under the 80, 55 and 75 budgets; the last `ghog day` walk reached the objective with the suite at 100% coverage.

### New types or classes introduced for Step 3

The step introduced no new type, class or function. It is a documentation-only change: each of the three cycle instruction files gains one `## Handoff` section that wires the existing `pw handoff` subcommand built in Step 2, so there is no production or test code to introduce.

### Architecture check for Step 3

- **Documentation layer**: the change touches only `instructions/*.md` files, which sit outside the `tools/` code, so no module, layer or import is added or moved.
- **Boundary direction**: the sections name the existing `pw handoff` CLI surface and point at `a.prompt.txt`; they add no new dependency and no code path.
- **Markdown rule note**: each file carries the single `## Handoff` heading the plan's completion criteria require, unique within its own document, with single-space list markers and blank lines around the one-item list, per `markdown.md`.

No DDD-Hexagonal violation or adapter smell is possible in a documentation-only step; there is nothing that needs to be addressed.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: no code changed, so no computation is added; the step edits three markdown files.
- **Hot-path bound**: not applicable -- an instruction document carries no runtime path.
- **Plan-bound alignment**: the plan marks no perf gate for Step 3, and none is touched.

No, there is no performance issue that needs to be addressed for Step 3.

### Unit test coverage check for Step 3

- **No unit-tested class**: Step 3 adds no Python class or function, so it carries no unit test and no coverage target; the plan states the instruction sections are documents, verified by the grep checks and proven end to end by the Step 4 acceptance scenario.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing feature behavior**: the three instructions gain one trailing section and keep all prior content unchanged, so no existing instruction step is altered; the wired `pw handoff` subcommand already exists from Step 2.
- **Reporting or diagnostics**: unchanged -- the sections add guidance only, with no log or status output.
- **Compatibility note**: the change is additive and document-only; the `## Handoff` token routing (`check` for the implement instructions, `after-check` for the check) matches the `TASK_TOKENS` the subcommand accepts.

No existing feature or reporting capability appears impaired by Step 3.

---

## Step 4. Acceptance test for the handoff chain

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

`tests/unit/tools/test_prompt_workflow_acceptance.py` now carries four handoff acceptance scenarios that drive `main(["handoff", ...])` against a temp project (draft, plan with a `### Step 2.` heading, validation plan) for the three forward transitions: `check` to the `implementation-check.md` prompt, `after-check` to the `implement-missing-step.md` prompt on a `No` step and to the `group-commits-msg.md` commit prompt on a `Yes` step, and the direct `commit`. Each asserts the delivered `a.prompt.txt` instruction and body and the recorded `a.prompt_memory` step. The real `build_cycle_prompt` runs end to end; only the git reads and the clipboard are monkeypatched (Q05). The last full `ghog day` walk reached the objective with 718 tests passing at 100% coverage.

### Goal for Step 4

Add an acceptance scenario that drives `main(["handoff", ...])` for the three transitions against a temp project with a validation plan, asserting the delivered `a.prompt.txt` names the expected instruction and the memory records the expected step.

### Step 4 improvement expectations

- `check` writes the `implementation-check.md` prompt for the step.
- `after-check` writes the commit prompt on a `Yes` step and the implement-missing prompt on a `No` step.
- `commit` writes the commit prompt and empties `a.commit`.
- The full suite stays green and at the coverage gate.

### What was implemented for Step 4

- **The handoff acceptance scenarios**: four functions added to `tests/unit/tools/test_prompt_workflow_acceptance.py` -- `test_handoff_check_delivers_check_prompt`, `test_handoff_after_check_no_delivers_implement_missing`, `test_handoff_after_check_yes_delivers_commit` and `test_handoff_commit_delivers_commit_prompt` -- each calling `prompt_workflow.main(["handoff", <task>, "2", "--root", str(tmp_path)])` and asserting the return code, the delivered prompt and the recorded memory.
- **The temp-project builder (`_build_project`)**: writes `docs/draft.v0.1.0.pw_handoff.md`, a plan with the `### Step 2. The handoff subcommand and its orchestration` heading that `read_step_title` reads, and a validation plan whose `Analysis of Step 2` status line is passed in per scenario (`Not started`, `No`, or `Yes`), so the real document scans resolve the topic and the step.
- **The git-and-clipboard wiring (`_wire_handoff`)**: monkeypatches the `prompt_workflow_git` reads (`current_branch`, `working_tree_changed_files`, `fork_point`, `has_step_commit`, `status_entries`, `staged_files`) and records each `stage_all`, and stubs `set_clipboard_text` to a no-op, so no real git process or PowerShell call runs (Q05); the single draft and a None fork point resolve the topic with no menu.
- **The commit assertion helper (`_assert_commit_prompt`)**: checks the commit body fragments, the staged `log` block, the `docs(pw_handoff): record step 2 validation` final-commit line the staged validation plan triggers (Q16), the emptied `a.commit` (Q25), the single `git add -A` (Q61), and the `step=10` memory; the substrings are checked as one membership scan to keep the helper's branch count under the radon gate.
- **Validation evidence**: `rg -c "handoff"` returns 31 hits in the acceptance file, the file measures 296 lines (under the 600 budget) and ends with `# eof`; the full `ghog day` walk reached the objective (`exit=0`) with the suite at 100% coverage.

### New types or classes introduced for Step 4

The step introduced no new production type and no new test class. It is an acceptance addition built from four module-level test functions and three module-level helpers (`_build_project`, `_wire_handoff`, `_assert_commit_prompt`, plus the small `_delivered_prompt` reader) in the existing `test_prompt_workflow_acceptance.py`. It reuses the production `MemoryRecord` for the memory assertions and the real `prompt_workflow.main`, `run_handoff` and `build_cycle_prompt` paths rather than introducing any new code under `tools/`.

### Architecture check for Step 4

- **Test layer placement**: the scenario sits in `tests/unit/tools/`, the test layer, and exercises the tool through its `main` entry point; it adds no production code, so no module, layer or import is added or moved in `tools/`.
- **Boundary direction**: the test monkeypatches the shared `prompt_workflow_git` module object, which `prompt_workflow_docs`, `prompt_workflow_plan` and the entry point all import, so the stubbed git reads reach every caller without the test reaching inside any layer; the real prompt-building path runs untouched.
- **No coverage-protection breach**: the scenario runs no `pytest`/`ghog` of its own and spins no real git or clipboard process, matching the design's Q05 choice and the suite's house style.

No DDD-Hexagonal violation or adapter smell is visible in this test-only step; there is nothing that needs to be addressed.

### Performance check for Step 4

- **No new `O(n^2)` or `O(n log n)` path**: the step adds test code only; each scenario runs `run_handoff` once, which performs the same linear validation-plan and plan-heading scans the cycle already pays, with no loop and no new computation.
- **Hot-path bound**: not applicable -- an acceptance test carries no runtime hot path; the helpers build a few small files and assert substrings.
- **Plan-bound alignment**: the plan marks no perf gate for Step 4, and the exercised path stays inside the documented `O(1)` mapping plus `O(n)` document-scan bound.

No, there is no performance issue that needs to be addressed for Step 4.

### Unit test coverage check for Step 4

- **No new unit-tested class**: Step 4 adds an acceptance scenario, which the plan states is larger than a unit test and carries no 100% coverage target; it introduces no production class of its own.
- **Production classes it exercises**: `tools/prompt_workflow_handoff.py` and the `run_handoff` orchestration in `tools/prompt_workflow.py` are already at 100% from the Step-1 and Step-2 unit tests in `test_prompt_workflow_handoff.py` and `test_prompt_workflow_main.py`; the acceptance scenario adds end-to-end confidence over the real `build_cycle_prompt`, not a new per-class target.

No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **Existing feature behavior**: the change is test-only -- four scenarios and three helpers added to `test_prompt_workflow_acceptance.py`; the two existing `__main__`-guard tests are untouched, so no route, service or workflow behaviour changed.
- **Reporting or diagnostics**: unchanged; the scenarios read the tool's own `a.prompt.txt` and `a.prompt_memory` outputs and assert on them, adding no new diagnostics.
- **Compatibility note**: the addition proves the handoff chain end to end and locks the delivered prompt and recorded step for each of the three transitions, so a later change that breaks one transition is caught by these scenarios.

No existing feature or reporting capability appears impaired by Step 4.

---

Keep this document review-only: compare the current state to the plan, record evidence, and call out incomplete work. The design rationale stays in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md).
