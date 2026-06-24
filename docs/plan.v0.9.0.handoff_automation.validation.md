# v0.9.0 handoff_automation implementation tracking and validation

No, it is not implemented.

This document tracks the v0.9.0 handoff automation: the `pw skill` subcommand and the handoff, hint, and multi-choice edits in the instruction bodies. Nothing is implemented yet; the work is the six steps of `docs/plan.v0.9.0.handoff_automation.md`, from the skill module foundation through the acceptance tests.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038) -- write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.9.0 handoff_automation (implementation)

All implementation work must respect the IO classification of `docs/plan.v0.9.0.handoff_automation.md`. The key constraints carried forward are:

- The next-step derivation lists the `docs/` directory once, the existing `docs_dirs` scan.
- It reads only the marker lines it needs (open-questions and decisions-table) on matched documents, never a full parse.
- Host detection reads two environment values and never touches the filesystem.
- `pw skill` writes nothing: no `a.prompt.txt`, no clipboard, no `a.prompt_memory`; it prints to stdout only.

---

## Complexity Bound Clarification for v0.9.0 (implementation)

The scaling target for all v0.9.0 code paths is:

- **O(1) amortized per call event**: host detection is one environment read; command rendering is constant string work.
- **O(n) total per phase**: the next-step derivation scans the `docs/` listing once and reads a few marker lines, the same bounded scan the interactive `pw` already performs.

Every implemented step is reviewed against this bound in its Performance check section.

---

## Step 1. The skill module foundation: host prefix and command rendering

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The skill module foundation is in place: `tools/prompt_workflow_skill.py` holds `detect_host`, `host_prefix`, and `render_command` as pure functions, and the nested unit test leaf covers every branch. The ghog walk's check, focused tests, and full coverage pass are green (`check exit=0`, all tests pass, `cov=100`, `outliers=0`); the lone exit-8 was an unrelated load-driven excluded integration test, accepted as out of this step's scope.

### Goal for Step 1

Create `tools/prompt_workflow_skill.py` with pure functions: `host_prefix` (read `CLAUDECODE` and `CODEX_THREAD_ID`, honor an override that short-circuits detection) and `render_command` (turn an instruction name and a document into a bare `<prefix><name> on <doc>` command with no backticks).

### Step 1 improvement expectations

- `host_prefix` returns `/` for Claude, `$` for Codex, the override when given, and a documented default otherwise.
- `render_command` produces one bare command line, the `.md` suffix dropped, no backticks.
- The new module reaches 100% unit coverage and ends with `# eof`.

### What was implemented for Step 1

- **Host detection**: `detect_host` reads `CLAUDECODE` then `CODEX_THREAD_ID` from the env mapping (Claude wins when both are set) and falls back to the Claude default; `host_prefix` maps the host to `/` or `$`, and an override short-circuits the environment read (Q04).
- **Command rendering**: `render_command` drops the `.md` suffix and formats `<prefix><name> on <document>` with no backticks, the bare command form (design area 2).
- **Tests**: `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`, with its package `__init__.py`, covers the marker precedence, the empty-marker case, the override short-circuit, both suffix branches, and a property loop over the render invariants.
- **Validation evidence**: the ghog walk reported `check exit=0`, all 964 tests pass (up from 957, the 7 new skill tests included), `cov=100`, and `outliers=0`. The lone `exit=8` was an unrelated load-driven excluded integration test, not a Step 1 file.

### New types or classes introduced for Step 1

No new production class. Step 1 is three module-level pure functions (`detect_host`, `host_prefix`, `render_command`) plus the module constants, in the new `tools/prompt_workflow_skill.py`. The nested test leaf is support code, not a production type.

### Architecture check for Step 1

- **Layer placement**: the new module sits beside the other `prompt_workflow_*` tool modules and holds only pure functions (env mapping in, string out); it imports nothing from the hub or the other pw modules, so there is no layer breach.
- **Dependency direction**: no technical library is pulled in; `Mapping` is a typing-only import under `TYPE_CHECKING`, so the module stays business-only string logic.
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: all three functions are `O(1)` -- two dict lookups and one string format, with no loop over input size.
- **Hot-path bound**: one environment read and a constant-time format per call.
- **Plan-bound alignment**: matches the plan's `O(1)`-per-call target.
- Conclusion: no performance issue. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 1

- **`tools/prompt_workflow_skill.py`**: covered at 100% by `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` -- every branch of `detect_host` (Claude, Codex, default, empty marker), `host_prefix` (override and detect paths), and `render_command` (suffix present and absent) is exercised; the ghog full pass reported `cov=100`.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the module is new and imported by nothing yet, so no existing route, service, or workflow is touched; the interactive `pw` and the `pw handoff` cycle are unchanged.
- **Reporting or diagnostics**: no logging or status payload changed.
- **Compatibility**: no alias or behavior change; the module stays dormant until Steps 2 and 3 wire it in.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 2. Disk-derived next-step routing and the decisions-table detector

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

`has_decisions_table` reads the three consolidated section titles in `tools/prompt_workflow_docs.py`, and `tools/prompt_workflow_skill.py` gains `next_command` and its helpers, deriving the next step from disk by reusing `compute_state` and `next_step_numbers` with the decisions-table override (Q02) and mapping it to an instruction and a document. The walk is green: `check exit=0`, 975 tests pass (up from 964), `cov=100`, `outliers=0`. The lone `exit=8` is the recurring unrelated load drift on excluded integration tests, not a Step 2 file.

### Goal for Step 2

Add `has_decisions_table` to `tools/prompt_workflow_docs.py`, and in the skill module derive the next step from disk with `compute_state` and `next_step_numbers` (no memory step), mapping the step to its instruction and target document, so a new draft routes to `process-draft`, an open-questions document to `review-ask-questions`, and a document with a decisions table to the next phase.

### Step 2 improvement expectations

- `has_decisions_table` detects the three consolidated section titles and is absent otherwise.
- The next command is derived from disk only, with no read of `a.prompt_memory`.
- The most-advanced artifact sets the reported step.

### What was implemented for Step 2

- **Decisions-table detector**: `has_decisions_table` in `prompt_workflow_docs.py` matches `## Requirement clarifications`, `## Design decisions`, or `## Implementation decisions`, beside `has_open_questions`.
- **Disk-derived routing**: `next_command` reads `compute_state(root, topic, None)` with no memory step, takes the first `next_step_numbers` step, and advances past a review step (2, 5, 8) when the document it reads carries a decisions table (Q02); the resolved step maps to an instruction and a target document, host-prefixed by `render_command`. An open-questions document routes to consolidate, a fresh document to review, a settled document advances (Q03).
- **Test move (Q08)**: `test_prompt_workflow_docs.py` moved to `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` with its `__init__.py`, gaining a `has_decisions_table` case; the skill test gained the routing cases.
- **Validation evidence**: the walk reported `check exit=0`, 975 tests pass (964 plus 11 new), `cov=100`, and `outliers=0`.

### New types or classes introduced for Step 2

No new class. Step 2 adds module-level functions: `has_decisions_table` in `prompt_workflow_docs.py`, and `next_command` with its helpers `_resolve_step`, `_instruction_and_document`, `_document`, and `_relpath` (plus the `STEP_INSTRUCTION`, `STEP_ROLE`, `ADVANCE_PAST_REVIEW`, and `PRODUCED_TYPE` maps) in `prompt_workflow_skill.py`.

### Architecture check for Step 2

- **Layer placement**: the routing lives in the skill module and reuses `prompt_workflow_steps` (`compute_state`, `next_step_numbers`) and `prompt_workflow_docs` (`has_decisions_table`); it adds no second state machine, honoring Q02. `has_decisions_table` sits beside `has_open_questions` as a read-only marker check.
- **Dependency direction**: the skill module imports steps and docs; steps imports docs; no cycle, and nothing imports the skill module yet (the CLI wiring is Step 3).
- **Statelessness**: `next_command` never reads `a.prompt_memory`, so it is a pure function of the tree.
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: `next_command` runs one bounded docs scan via `compute_state` and a constant number of marker reads; `next_step_numbers` and the maps are `O(1)`.
- **Hot-path bound**: one directory listing plus a few marker-line reads per call, the same bound the interactive flow already pays.
- **Plan-bound alignment**: matches the plan's `O(n)`-per-phase, `O(1)`-per-call target.
- Conclusion: no performance issue. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 2

- **`tools/prompt_workflow_skill.py`**: covered at 100% by `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` -- the routing tests exercise every branch of `_resolve_step` (review-doc absent, present-and-unsettled, present-and-settled), `_instruction_and_document` (the process-draft branch and the role path), and `_document` (existing path and produced name).
- **`tools/prompt_workflow_docs.py`**: `has_decisions_table` is covered at 100% by the moved docs test (the three titles and the absent case); the full pass reported `cov=100`.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: `next_command` and `has_decisions_table` are new and called by nothing in production yet (the CLI wiring is Step 3), so the interactive `pw` and the `pw handoff` cycle are unchanged.
- **Reporting or diagnostics**: no logging or status payload changed.
- **Compatibility**: the docs test moved into the nested form (Q08), tracked as a delete plus an add; no import path changed, since the tests use absolute imports.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 3. The pw skill subcommand, the forced skill, and the host override

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

`tools/prompt_workflow.py` gains a `skill` subparser (an optional skill-name positional and a `--host` override) on the shared parent parser, with `main` dispatching to `skill.run_skill`; the body lives in `tools/prompt_workflow_skill.py` (Q05). `run_skill` resolves the topic without a menu and prints the disk-derived next command, or a forced skill's command via `forced_command` when its document exists, otherwise an empty stdout, a stderr note, and a dedicated non-zero exit (Q03, Q04). The walk reached the objective: `check exit=0`, `cov=100`, `outliers=0`, exit=0.

### Goal for Step 3

Add a `skill` subparser on the shared parent parser of `tools/prompt_workflow.py`, with an optional skill-name positional and a host-override option, and a thin `run_skill` that delegates to the skill module; add `forced_command` so a named skill emits its command when its document exists, or `run_skill` exits `-1` when the skill is not yet applicable.

### Step 3 improvement expectations

- `pw skill` prints the disk-derived next command; `pw skill <name>` prints that skill's command or exits `-1`; the host override sets the prefix and skips detection.
- `tools/prompt_workflow.py` stays under 550 lines.
- The CLI tests live in `test_prompt_workflow_skill.py`, not in the 599-line `test_prompt_workflow_main.py`.

### What was implemented for Step 3

- **The skill subcommand**: `prompt_workflow.py` adds a `skill` subparser (optional `skill_name`, a `--host` choice) on the shared parent and dispatches `main` to `skill.run_skill`; the hub stays well under 550 lines (Q05).
- **run_skill**: resolves the topic without a menu (reusing `handoff.resolve_topic`), then prints the disk-derived next command, or a forced skill's command; on nothing-to-emit it writes a one-line stderr note, leaves stdout empty, and returns `EXIT_NOT_APPLICABLE` (Q03).
- **forced_command**: maps a skill name to its document role through the static `FORCED_ROLE` map (Q04) and emits the command only when that document exists, else None.
- **Validation evidence**: the walk reached the objective with `check exit=0`, `cov=100`, `outliers=0`, and exit=0; the new CLI, run_skill, and forced_command tests live in the skill test, not the 599-line main test.

### New types or classes introduced for Step 3

No new class. Step 3 adds the module-level `run_skill` and `forced_command` functions plus the `FORCED_ROLE` map and the `EXIT_NOT_APPLICABLE` constant in `prompt_workflow_skill.py`, and the `skill` subparser and its dispatch in `prompt_workflow.py`.

### Architecture check for Step 3

- **Layer placement**: the hub keeps only the subparser and a one-line dispatch; the orchestration lives in the skill module (Q05), which reuses `git`, `docs`, `memory`, and `handoff` for the resolution and `steps` for the state.
- **Dependency direction**: `prompt_workflow.py` imports the skill module (the hub depends on the mode, not the reverse); the skill module imports the lower modules with no cycle.
- **Output discipline**: the command goes to stdout, the not-applicable note to stderr, so the two channels stay separate (Q03).
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: `run_skill` is one branch resolution and one `next_command` or `forced_command` call; `forced_command` adds one bounded `compute_state` scan and `O(1)` map lookups.
- **Hot-path bound**: one command per invocation, the same bounded docs scan the interactive flow pays.
- **Plan-bound alignment**: matches the plan's `O(n)`-per-phase, `O(1)`-per-call target.
- Conclusion: no performance issue. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 3

- **`tools/prompt_workflow_skill.py`**: covered at 100% by the skill test -- the run_skill tests cover the no-topic, no-argument, forced-applicable, and forced-not-applicable branches, and the forced_command tests cover the unknown-skill, draft-role, and document-present-or-absent branches.
- **`tools/prompt_workflow.py`**: the `skill` subparser and its dispatch are covered by the hub dispatch test and the existing main tests; the full pass reported `cov=100`.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing feature behavior**: the new subcommand is additive; the interactive `pw` run and the `pw handoff` cycle keep their paths, with `main` only gaining a `skill` branch.
- **Reporting or diagnostics**: the skill mode prints the bare command to stdout and its note to stderr; no existing logging changed.
- **Compatibility**: `--root` and `--debug` still parse on either side of the new subcommand via the shared parent.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 4. Automated handoff sections in the writing and consolidation instructions

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

`write-requirement.md`, `write-design.md`, and `write-plans.md` each gained a `## Handoff` that runs `pw skill` and runs the returned `/review-ask-questions` on the document just written, with the `stop here` argument phrase to hold the chain; `write-plans` notes the review is the plain plan only. `consolidate-then-review-ask-questions.md` gained a `## Handoff` that, on a settled document, runs `pw skill` to advance to the next phase. A grep confirms each section is present. The walk regressed nothing (`fail=0`, `cov=100`); the `exit=8` was severe load drift on pre-existing excluded and floor-borderline tests, none of them Step 4 files, since Step 4 changed no code.

### Goal for Step 4

Add a `## Handoff` section to the four instructions in the `implement-step.md` shape (run `pw skill`, read the bare command, run it straight away, no pause), and document the "stop here" phrase that holds the chain at a writing step.

### Step 4 improvement expectations

- Each of the four instructions ends on a `## Handoff` naming `pw skill` and the document just written.
- `write-plans` hands off the plain plan only, never the validation plan.
- The three writing instructions document the "stop here" phrase.

### What was implemented for Step 4

- **Writing-step handoffs**: `write-requirement.md`, `write-design.md`, and `write-plans.md` each end on a `## Handoff` that runs `pw skill` and runs the printed `/review-ask-questions` on the produced document straight away, with no go-ahead; `write-plans` names the plain plan only.
- **The stop-here gate**: the three writing instructions document the `stop here` argument phrase that holds the chain at the writing step instead of firing the handoff (Q01, Q06).
- **Consolidate handoff**: `consolidate-then-review-ask-questions.md` ends on a `## Handoff` that, once the document is settled, runs `pw skill` to advance to `/write-design`, `/write-plans`, or `/implement-step`; when questions remain it stops for another round.
- **Validation evidence**: a grep over the four files confirms each carries `## Handoff` and `pw skill`, and the three writing instructions carry `stop here`; the walk reported `fail=0` and `cov=100`.

### New types or classes introduced for Step 4

No new type or class. Step 4 is markdown-only: a `## Handoff` section added to four instruction bodies, with no code or test files touched.

### Architecture check for Step 4

- **No code changed**: Step 4 edits only instruction markdown, so there is no layer, import, or dependency to assess.
- **Handoff shape**: each section mirrors the existing `implement-step.md` handoff (run the `pw` command, run the returned prompt straight away), keeping the workflow's handoff prose consistent.
- Conclusion: no DDD-Hexagonal violation or smell, since no code changed. No, there is nothing that needs to be addressed.

### Performance check for Step 4

- **No code path added**: the change is instruction text; no runtime path is introduced.
- Conclusion: no performance concern. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 4

- **No unit-tested class touched**: Step 4 adds no production code, so no class coverage changes. The instruction sections are guarded by the structural test added in Step 5 and by the Step 6 acceptance suite.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 4.

### Feature integrity for Step 4

- **Existing feature behavior**: the handoff sections are additive prose; the writing and consolidation skills keep their bodies and only gain the trailing handoff.
- **Reporting or diagnostics**: no logging or payload changed.
- **Compatibility**: the handoff names the document by its `vX.Y.Z.<slug>` pattern, so it works for any topic.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 5. The review hint, the no-question decisions table, and the multi-choice lists

### Analysis of Step 5 implementation state

Yes. Step 5 has been fully implemented.

`review-ask-questions.md` gained a `## Handoff` that leaves the consolidation hint carrying the reviewed document name and the no-question rule (write a one-row decisions table when the round raises no question). `process-draft.md` step 7 and `split-and-define.md` now present a multi-choice next-step list, each closing with a "Type something else" entry. A new structural test asserts every edited instruction carries its handoff, hint, or list, and runs on every walk (Q06). The walk reached the objective: 985 tests (up from 982), `cov=100`, `outliers=0`, exit=0.

### Goal for Step 5

Add the consolidation hint and the no-question one-row decisions-table rule to `review-ask-questions.md`, and the multi-choice lists to `process-draft.md` and `split-and-define.md`, each closing with a "Type something else" entry the instruction owns.

### Step 5 improvement expectations

- `review-ask-questions` always leaves an unambiguous on-disk state, even on a no-question round.
- `process-draft` lists `/write-requirement` and `/split-and-define` on the produced draft.
- `split-and-define` lists one `/write-requirement` per slug it defined.

### What was implemented for Step 5

- **Review hint and no-question table**: `review-ask-questions.md` leaves a plain-text `/consolidate-then-review-ask-questions` hint with the reviewed document name, and writes a one-row decisions table when no question is raised so the on-disk state reads as settled (Q03, Q06).
- **Multi-choice lists**: `process-draft.md` presents `/write-requirement` or `/split-and-define` on the produced draft, and `split-and-define.md` presents one `/write-requirement` per defined slug (no cap, in split order); each list closes with a "Type something else" free-text entry the instruction supplies (Q05, Q07).
- **Structural guard**: `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py` asserts the four writing and consolidation instructions carry a `## Handoff` with `pw skill`, the review instruction carries the consolidation hint, and the two splitting instructions carry the multi-choice with a free-text entry (Q06).
- **Validation evidence**: the walk reached the objective with 985 tests, `cov=100`, `outliers=0`, and exit=0.

### New types or classes introduced for Step 5

No new production type or class. Step 5 edits three instruction bodies and adds one structural test module (`test_instruction_structure_tdd.py`) plus its package `__init__.py`; the test is regression support, not a production type.

### Architecture check for Step 5

- **Code vs prose**: the only code is the structural test, which reads the instruction files through `steps.llm_shared_dir()`; the rest is instruction markdown.
- **No production change**: no `tools/` module changed, so there is no layer or dependency to assess.
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 5

- **No new runtime path**: the structural test reads a handful of files once at test time; no production path is added.
- Conclusion: no performance concern. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 5

- **No production class touched**: Step 5 adds no production code, so no class coverage changes; the full pass held `cov=100`.
- **Structural test**: `test_instruction_structure_tdd.py` is a regression check over the instruction files, not a class unit test, so it carries no 100% target of its own.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 5.

### Feature integrity for Step 5

- **Existing feature behavior**: the hint, no-question rule, and multi-choice lists are additive to the instruction bodies; no skill loses its existing steps.
- **Reporting or diagnostics**: no logging or payload changed.
- **Compatibility**: the structural test guards the markers, so a later edit that drops a handoff, hint, or list fails on the next walk.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 6. Acceptance tests for the chained workflow

### Analysis of Step 6 implementation state

Yes. Step 6 has been fully implemented.

`tests/unit/tools/test_prompt_workflow_acceptance.py` moved into the nested `test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py` (Q08) and gained four `pw skill` acceptance cases that drive `main(["skill", ...])` end to end against a scratch tree: process-draft on a new draft, write-design on a settled requirement, the forced-skill not-applicable-then-emit path, and the host override. The walk ran 989 tests with `fail=0`, `cov=100`, `outliers=0`; the lone `exit=8` was the recurring unrelated load drift on an excluded integration test.

### Goal for Step 6

Add acceptance tests that build a scratch `docs/` tree in each state and assert the `pw skill` command and prefix, cover the forced-skill and `-1` paths and the host override, and check that each edited instruction carries its `## Handoff`, hint, or multi-choice list.

### Step 6 improvement expectations

- One acceptance suite proves the chain end to end, with both `/` and `$` prefixes asserted through the override.
- The consolidated and no-question states route to the next phase.
- The instruction-structure checks pass for all seven edited instructions.

### What was implemented for Step 6

- **Acceptance cases**: four `pw skill` cases drive the CLI in-process through `main(argv)` (Q07) on a scratch tree with the git reads monkeypatched: process-draft on a new draft, write-design on a settled requirement, the forced skill (not applicable, then emitting once the document exists), and the host override forcing the Codex prefix.
- **Test move (Q08)**: the acceptance test moved into the nested `test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py` with its `__init__.py`; the existing handoff-cycle acceptance cases came across unchanged.
- **Validation evidence**: the walk ran 989 tests (985 plus 4) with `fail=0`, `cov=100`, and `outliers=0`.

### New types or classes introduced for Step 6

No new production type or class. Step 6 adds four acceptance test functions and a `_setup_skill_tree` helper to the moved acceptance module, plus its package `__init__.py`.

### Architecture check for Step 6

- **Test-only change**: Step 6 touches only the acceptance test (moved and extended); no `tools/` module changed.
- **Harness**: the cases drive the real `main` and `run_skill`, monkeypatching only the git reads, so they exercise the parser, the dispatch, and the routing end to end.
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 6

- **No new runtime path**: the acceptance cases are test-only; each runs `main(["skill", ...])` once on a tiny scratch tree.
- Conclusion: no performance concern. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 6

- **No production class touched**: Step 6 adds no production code, so no class coverage changes; the full pass held `cov=100`.
- **Acceptance suite**: these are end-to-end acceptance tests, not class unit tests, so they carry no 100% target of their own.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 6.

### Feature integrity for Step 6

- **Existing feature behavior**: the move preserves the handoff-cycle acceptance cases; the new cases are additive.
- **Reporting or diagnostics**: no logging or payload changed.
- **Compatibility**: the move keeps absolute imports, so nothing else changes.
- Conclusion: no existing feature or reporting capability is impaired.

---

## Step 7. The commit-gate multi-choice in group-commits-msg

### Analysis of Step 7 implementation state

Yes. Step 7 has been fully implemented.

`pw skill` gains a `--after-commit <step>` mode: `post_commit_command` derives the post-commit next action from the validation plan -- the step after the committed one for `/implement-step`, `/prepare-release` once it was the last, or none when no plan is in play (a standalone commit). `instructions/group-commits-msg.md` step 7 now presents the commit-gate multi-choice (a constant `go ahead`, the `pw skill --after-commit` contextual option, and a "Type something else" entry), and the structural test guards it. The walk reached the objective: 998 tests (up from 989), `cov=100`, `outliers=0`, exit=0.

### Goal for Step 7

Extend `pw skill` to derive the post-commit next action (next plan step via `derive_x`, prepare-release when all are committed, or none) and edit `group-commits-msg.md` so the commit gate presents the constant `go ahead`, the contextual option, and a "Type something else" entry, with only the contextual option chaining after the commit.

### Step 7 improvement expectations

- The commit gate shows `go ahead` plus the right contextual option for the branch state, or only `go ahead` for a standalone call.
- Plain `go ahead` commits and stops; the contextual option commits then chains.
- pw skill derives the option from disk, reusing `derive_x`.

### What was implemented for Step 7

- **Post-commit derivation**: `post_commit_command` in `prompt_workflow_skill.py`, told the committed step, reads the validation plan and returns `/implement-step on <plan> step <next>` for the next step, `/prepare-release` once the committed step was the last, or None when no validation plan is resolved or the step is not in it.
- **CLI**: `pw skill --after-commit <step>` on the hub dispatches to `run_skill`, which prints the contextual command or, when None, writes a stderr note and returns `EXIT_NOT_APPLICABLE`.
- **Commit gate**: `instructions/group-commits-msg.md` step 7 presents the multi-choice -- a constant `go ahead`, the `pw skill --after-commit` option (`implement step <next>` or `prepare-release`, or only `go ahead` standalone), and a "Type something else" entry; plain `go ahead` stops, the contextual option chains only after the commit succeeds.
- **Structural guard and evidence**: the structural test asserts the gate's multi-choice; the walk ran 998 tests with `fail=0`, `cov=100`, `outliers=0`.

### New types or classes introduced for Step 7

No new class. Step 7 adds the module-level `post_commit_command` and the `_emit` helper to `prompt_workflow_skill.py`, the `--after-commit` argument and its dispatch on `prompt_workflow.py`, and the commit-gate section to `group-commits-msg.md`.

### Architecture check for Step 7

- **Layer placement**: `post_commit_command` lives in the skill module beside the other derivations and reuses `plan.parse_validation_steps` and `_document`; the hub keeps only the new argument and a one-line dispatch.
- **Dependency direction**: the skill module now imports `prompt_workflow_plan` (already in its transitive graph via `handoff`); no cycle.
- **Output discipline**: the contextual command goes to stdout, the not-applicable note to stderr (Q03).
- Conclusion: no DDD-Hexagonal violation or smell. No, there is nothing that needs to be addressed.

### Performance check for Step 7

- **No new `O(n^2)` or `O(n log n)` path**: `post_commit_command` parses the validation plan once and does an `index` lookup over the step list, `O(n)` over the steps.
- **Hot-path bound**: one command per gate invocation, the same bounded reads the cycle already pays.
- **Plan-bound alignment**: matches the plan's `O(n)`-per-phase, `O(1)`-per-call target.
- Conclusion: no performance issue. No, there is nothing that needs to be addressed.

### Unit test coverage check for Step 7

- **`tools/prompt_workflow_skill.py`**: covered at 100% by the skill test -- `post_commit_command`'s five branches (no topic, no validation plan, unknown step, next step, last step) and `run_skill`'s after-commit path are exercised; the full pass reported `cov=100`.
- **`tools/prompt_workflow.py`**: the `--after-commit` argument and its dispatch are covered by the after-commit dispatch test.
- **`group-commits-msg.md`**: the gate multi-choice is guarded by the structural test.
- Conclusion: No, there is no unit-tested class below 100% that needs completing for Step 7.

### Feature integrity for Step 7

- **Existing feature behavior**: `pw skill` keeps its no-argument and forced-skill paths; `--after-commit` is an additive mode, and `group-commits-msg` step 7 only gains the multi-choice.
- **Reporting or diagnostics**: the contextual command and the not-applicable note keep the stdout and stderr split.
- **Compatibility**: the `--after-commit` value is a plain string, so a sub-step id such as `4A` is accepted; `run_skill`'s extra parameter defaults to None, so existing callers are unaffected.
- Conclusion: no existing feature or reporting capability is impaired.
