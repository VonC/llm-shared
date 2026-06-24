# v0.9.0 handoff_automation implementation plan -- chain the workflow with pw skill

Implement the `pw skill` subcommand and wire the automated handoffs, the review hint, and the multi-choice lists into the instruction bodies, so the workflow chains itself from the documents on disk.

- **A new skill mode, isolated in its own module**: host prefix, bare-command rendering, and disk-derived routing live in `tools/prompt_workflow_skill.py`, so the 489-line `tools/prompt_workflow.py` only gains a subparser and a thin dispatch.
- **Disk is the single source of truth**: the next step is derived from the documents present (`compute_state`, `next_step_numbers`, the open-questions marker, and a new decisions-table detector), never from a stale memory file.
- **Instruction bodies call the mode**: the writing and consolidation instructions gain a `## Handoff` that runs `pw skill`; the review and splitting instructions gain a hint or a multi-choice list.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing underscore (MD036).

## Plan goal for v0.9.0 handoff_automation

Implement the full v0.9.0 handoff automation described in `docs/design.v0.9.0.handoff_automation.md` and `docs/feature-request.v0.9.0.handoff_automation.md`, in ordered steps that land the code before the instruction edits that call it.

- **Step 0 goal**: none needed. This is a CLI string and document feature with no hot loop; the perf-gate pass below records why no Step 0 timeout gate is added.
- **Step 1 goal**: the skill module foundation -- host prefix detection and bare-command rendering as pure functions.
- **Step 2 goal**: disk-derived next-step routing, reusing the existing state machine, plus a decisions-table detector for the settled-versus-review fork.
- **Step 3 goal**: the `pw skill` subcommand on the hub, with the optional skill-name argument (emit a valid earlier skill, or `-1`) and the host override.
- **Step 4 goal**: the automated `## Handoff` sections in `write-requirement`, `write-design`, `write-plans`, and `consolidate-then-review-ask-questions`, with the "stop here" gate.
- **Step 5 goal**: the review hint plus the no-question decisions-table behavior, and the multi-choice lists in `process-draft` and `split-and-define`.
- **Step 6 goal**: acceptance tests that drive `pw skill` across every document state and the instruction bodies through a scratch tree.
- **Step 7 goal**: the commit-gate multi-choice in `group-commits-msg`, with `pw skill` deriving the post-commit next action (next plan step, prepare-release, or none).

---

## Scope anchors for v0.9.0 handoff_automation plan

This plan implements the design from `docs/design.v0.9.0.handoff_automation.md` and the requirement from `docs/feature-request.v0.9.0.handoff_automation.md`, targeting the following outcomes:

1. `pw skill` prints the bare next-step command (or commands) from disk, host-prefixed, with an optional forced skill and a host override.
2. The writing and consolidation instructions chain automatically by running `pw skill`; the review and splitting instructions present a hint or a multi-choice list.
3. The settled-versus-review fork is read from disk, and `review-ask-questions` writes a one-row decisions table on a no-question round so that fork is always unambiguous.

The following are explicitly **in scope** for this plan:

- The new `tools/prompt_workflow_skill.py` module and its unit tests.
- The `skill` subparser and `run_skill` dispatch on `tools/prompt_workflow.py`, kept minimal.
- The `has_decisions_table` detector in `tools/prompt_workflow_docs.py`.
- The handoff, hint, and multi-choice edits in the seven instruction bodies.
- Acceptance tests covering the document states and the force-skill and override paths.
- The commit-gate multi-choice in `instructions/group-commits-msg.md`, with `pw skill` deriving the post-commit next action.

The following are explicitly **deferred** to v0.10.0 and beyond:

- The gray, Tab-completable rendering of the review hint on Claude and Codex (plain text is the committed baseline).
- Any change to the interactive `pw` menu or the existing `pw handoff` implement cycle beyond what `pw skill` reuses.
- The full migration of the remaining pw test files into the nested form, and the split of the already-over-budget `tests/unit/tools/test_prompt_workflow_main.py` (599 lines): a separate restructuring effort (Q08). This plan moves only the two files it edits and does not grow the main test.

---

## Complexity Bound Clarification for v0.9.0

The scaling target for all v0.9.0 code paths is:

- **O(1) amortized per call event**: host detection is one environment read; command rendering is constant string work.
- **O(n) total per phase**: the next-step derivation scans the `docs/` listing once and reads the marker lines of at most a few matched documents, the same bounded scan the interactive `pw` already performs.

No v0.9.0 code path introduces `O(n^2)` or `O(n log n)` cost. `pw skill` reuses `relevant_drafts`, `select_document`, and `next_step_numbers`, which are already O(n) over the docs entries; the new code adds only constant-time host and render work.

---

## File-based IO cost clarification for v0.9.0 handoff_automation

The document-loading phase of `pw skill` is a small index-read, not a metadata-loading delay:

- The next-step derivation lists the `docs/` directory once (and its `docs/vX.Y.Z/` subfolder), the existing `docs_dirs` scan.
- It reads only the marker lines it needs: the `## Open questions` marker and the new decisions-table marker, on the matched documents, not a full parse.
- Host detection reads two environment values; it never touches the filesystem.
- `pw skill` writes nothing: no `a.prompt.txt`, no clipboard, no `a.prompt_memory`. It prints to stdout only.

---

## Confirmed technical facts for v0.9.0 plan viability

These facts are drawn from direct inspection of the current repository tree.

**Files at or approaching the 550-line risk threshold** (must not grow in place):

- `tests/unit/tools/test_prompt_workflow_main.py`: **599 lines** -- already over 550. Do not add to it; the `pw skill` CLI tests go to the new `test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`. A split of this file is deferred.
- `tools/prompt_workflow.py`: **489 lines** -- the largest module. Add only the subparser and a thin `run_skill` dispatch; keep the skill logic in the new module so this file stays under 550.

**Files safe to extend** (current lines, expected additions):

- `tools/prompt_workflow_docs.py`: 190 -- add a short `has_decisions_table` detector beside `has_open_questions` (about 10 to 15 lines).
- `tests/unit/tools/test_prompt_workflow_docs.py`: 224 -- add the `has_decisions_table` cases.
- `tests/unit/tools/test_prompt_workflow_acceptance.py`: 240 -- add the `pw skill` acceptance cases.

**What does not exist yet (all new for v0.9.0)**:

- `tools/prompt_workflow_skill.py`.
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`.

**Other confirmed technical facts that affect plan shape**:

- **The hub is a subcommand dispatcher**: `tools/prompt_workflow.py` has a shared parent parser (`--root`, `--debug`), a top-level `--pick`, and a `handoff` subcommand; `main()` dispatches on `args.command`. The `skill` subparser slots in beside `handoff`.
- **The state machine already derives the next step**: `steps.compute_state` plus `steps.next_step_numbers` walk requirement, design, then plan, and `docs.has_open_questions` reads the `## Open questions` marker. `pw skill` reuses these and must not duplicate them.
- **The step-to-instruction map is config-driven**: `tools/prompt_workflow.steps.json` maps each step number to its instruction file and context roles. The renderer reads this map; no config change is required.
- **The host markers are confirmed live**: Claude Code sets `CLAUDECODE` (value `1`); a Codex session sets `CODEX_THREAD_ID`. A plain terminal sets neither.

---

## Current test-tree validation snapshot for v0.9.0 handoff_automation

Existing test packages that v0.9.0 must not break:

- `tests/unit/tools/test_prompt_workflow_main.py` (599 lines) -- the CLI dispatch tests; do not grow it, add the `skill` CLI tests to the new file instead.
- `tests/unit/tools/test_prompt_workflow_steps.py` (231), `test_prompt_workflow_docs.py` (224), `test_prompt_workflow_handoff.py` (384) -- the modules `pw skill` reuses; keep green.
- `tests/unit/tools/test_prompt_workflow_acceptance.py` (240), `test_prompt_workflow_integration.py` (94) -- the end-to-end suites the acceptance step extends.

New tests use the nested form `tests/unit/tools/test_<module>/test_<module>_tdd.py` (Q01). New test leaves to create for v0.9.0:

- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`.
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`.

Existing pw tests move into the same nested form for consistency (Q01). Q08 settles the scope: only the two files this feature edits (`test_prompt_workflow_docs.py` and `test_prompt_workflow_acceptance.py`) move now, within the steps that edit them; the remaining pw test files migrate in a separate restructuring effort. Each new nested leaf needs its own `__init__.py`; confirm `tools/__init__.py` and `tests/unit/tools/__init__.py` and update them only if they enumerate modules.

---

## Shared execution command checklist for all v0.9.0 handoff_automation steps

Apply this checklist for every numbered step, filling in the step-specific paths.

1. Count lines before edits on all step files (see the ready-to-run command templates).
2. Apply tests-first changes as described under the step implementation section.
3. Run the step-targeted test command.
4. Run the step grep checks.
5. Run the shared gate loop until both the focused tests and the repo gate pass in the same cycle.
6. Count lines after edits and compare them with the step line-budget checkpoint.
7. If any Python file exceeds the 650-line "big file" rule after edits, stop and apply the split guidance before committing.

---

## Ready-to-run command templates for all v0.9.0 handoff_automation steps

Use these template forms in each step, substituting actual paths.

- Line count before or after: `[System.IO.File]::ReadAllLines('<path>').Count` from PowerShell.
- Targeted tests: `ghog single <step test files>` (groundhog runs the tests; never a direct `pytest`).
- Grep checks: a ripgrep over the step files for the new symbol or instruction phrase.
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the objective (`exit=0`): check.bat, the affected tests, then the full suite with coverage, in order.

---

## Numbered steps for v0.9.0 handoff_automation

### Step 1. The skill module foundation: host prefix and command rendering

#### Step 1 -- analysis and intent for the skill module

Issues to address:

- `pw skill` must prefix commands per host, but there is no host detection in `pw` today.
- The command string must be bare (no header, no Context wrapper, no backticks), unlike the three-part prompt `build_prompt` produces.

Fix intent:

- Create `tools/prompt_workflow_skill.py` with pure functions: `host_prefix` (read `CLAUDECODE` and `CODEX_THREAD_ID`, honor an override that short-circuits detection) and `render_command` (turn an instruction name and a document path into `<prefix><name> on <doc>`).
- Drop the `.md` suffix from the instruction file name for the emitted skill name.

Expected outcome:

- `host_prefix` returns `/` for Claude, `$` for Codex, the override when given, and a documented default when neither marker is present.
- `render_command` produces a single bare command line with no backticks.

Step framing:

- Design link: design area 2 (command surface and output channel) and design area 4 (host-aware command prefix).
- Execution checklist reference: the shared execution command checklist above.

#### Step 1 -- implementation for the skill module

**Files involved**:

- `tools/prompt_workflow_skill.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` (new, to be created).
- `tests/unit/tools/__init__.py` (existing, to be updated only if it enumerates test modules).

**Tests first**:

- `host_prefix`: Claude marker present gives `/`; Codex marker present gives `$`; override given wins and the environment is not read; neither marker present falls to the default.
- `render_command`: an instruction name and a document path render to `<prefix><name> on <doc>` with no backticks and exactly one prefix character.
- A small property check: for arbitrary version and slug, the rendered command holds no backtick and starts with the chosen prefix.

**Classes and behavior**:

- `host_prefix(env, override=None) -> str`: pure host-to-prefix resolution; the override short-circuits the environment read.
- `render_command(prefix, instruction, document) -> str`: bare command rendering, suffix dropped.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- A grep shows `CLAUDECODE` and `CODEX_THREAD_ID` only in the new module, not scattered.
- The new module ends with `# eof`, matching the repo convention.

#### Step 1 -- addendums for the skill module

Line-budget checkpoint:

- `tools/prompt_workflow_skill.py`: before 0 -> target <= 550.
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`: before 0 -> target <= 550.

Split guidance:

- If the module later grows past about 400 lines, split host detection and rendering from the routing added in Step 2 into a `prompt_workflow_skill_render.py` helper.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`; then `ghog day`.

Time-gated status for Step 1:

- No perf gate is affected; see the Step 0 perf-gate pass note in the plan goal.

### Step 2. Disk-derived next-step routing and the decisions-table detector

#### Step 2 -- analysis and intent for the routing

Issues to address:

- `pw skill` must name the next step from disk, never from `a.prompt_memory`, which the automated flow does not refresh.
- The settled-versus-review fork needs an on-disk signal: a consolidated document has its open-questions section stripped and a decisions table added.

Fix intent:

- Add `has_decisions_table` to `tools/prompt_workflow_docs.py`, detecting the consolidated section (`## Requirement clarifications`, `## Design decisions`, or `## Implementation decisions`), beside `has_open_questions`.
- In the skill module, derive the next step with `compute_state` and `next_step_numbers` (passing no memory step), map the step to its instruction through `load_steps`, and resolve the target document through `select_document`. A new draft alone routes to `process-draft`; an open-questions document routes to `review-ask-questions`; a document with a decisions table advances to the next phase.
- Reuse `next_step_numbers` as the base, then post-process its answer: when the current document carries a decisions table, override its review-or-consolidate result to the advance step. Do not change `next_step_numbers` itself, so the interactive flow stays untouched (Q02).

Expected outcome:

- `pw skill` returns the right single command for each document state, read from disk.
- The fork uses no LLM-passed parameter.

Step framing:

- Design link: design area 3 (deriving the next step from on-disk state) and the Q02 and Q03 decisions.
- Execution checklist reference: the shared execution command checklist above.

#### Step 2 -- implementation for the routing

**Files involved**:

- `tools/prompt_workflow_docs.py` (existing, to be updated).
- `tools/prompt_workflow_skill.py` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_docs.py` -> `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` (existing, moved into the nested form and updated here; Q08).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` (existing, to be updated).

**Tests first**:

- `has_decisions_table`: present for each of the three section titles; absent otherwise.
- Routing: new draft alone gives the `process-draft` command; a requirement with `## Open questions` gives `review-ask-questions`; a requirement with a decisions table gives `write-design`; a design with a decisions table gives `write-plans`; with requirement, design, and plan present, the step after the plan is named.

**Classes and behavior**:

- `has_decisions_table(path) -> bool`: marker read, mirroring `has_open_questions`.
- `next_command(root, ...) -> str`: derive the step from disk and render its command; stateless (no memory step).

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- A grep shows the three decisions-section titles handled in one place.
- No read of `a.prompt_memory` appears in the skill module.

#### Step 2 -- addendums for the routing

Line-budget checkpoint:

- `tools/prompt_workflow_docs.py`: before 190 -> target <= 550.
- `tools/prompt_workflow_skill.py`: before Step 1 size -> target <= 550.
- `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` (moved from `test_prompt_workflow_docs.py`): before 224 -> target <= 550.

Split guidance:

- If `prompt_workflow_skill.py` approaches 400 lines, apply the Step 1 split guidance.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py tests/unit/tools/test_prompt_workflow_docs.py`; then `ghog day`.

Time-gated status for Step 2:

- No perf gate is affected.

### Step 3. The pw skill subcommand, the forced skill, and the host override

#### Step 3 -- analysis and intent for the subcommand

Issues to address:

- `pw skill` needs a command surface that takes an optional skill name and a host override, without growing the 489-line hub.
- A forced skill must emit its command when its document exists, even when it is not the next step, and return `-1` when the skill is not yet applicable.

Fix intent:

- Add a `skill` subparser on the shared parent parser of `tools/prompt_workflow.py`, with an optional skill-name positional and a host-override option. The hub holds only the subparser and a one-line call; the `run_skill` body lives in the skill module from the start, so the 489-line hub barely grows (Q05).
- In the skill module, add `forced_command` resolving a skill name to its target document role through a small static map kept in the skill module (Q04), and returning the command when the document exists. When the skill is not yet applicable, the path returns the internal `-1`, which `run_skill` maps to a dedicated non-zero exit code while printing nothing on stdout and a one-line note on stderr, so the caller never mistakes the signal for a command (Q03).

Expected outcome:

- `pw skill` prints the disk-derived next command; `pw skill <name>` prints that skill's command or exits `-1`; the host override sets the prefix and skips detection.

Step framing:

- Design link: design area 2 (forcing a specific skill, and the host override) and the Q01 decision.
- Execution checklist reference: the shared execution command checklist above.

#### Step 3 -- implementation for the subcommand

**Files involved**:

- `tools/prompt_workflow.py` (existing, to be updated).
- `tools/prompt_workflow_skill.py` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` (existing, to be updated).

**Tests first**:

- The CLI parses `skill`, `skill <name>`, and the host-override option, on either side of the subcommand (the shared parent parser).
- `run_skill` with no argument prints the next command; with a forced name whose document exists prints that command; with a not-applicable name returns the `-1` exit; the override sets the prefix.

**Classes and behavior**:

- `run_skill(root, skill_name, host_override) -> int`: thin dispatch in the hub; returns the process exit code.
- `forced_command(...) -> str | None`: resolve a forced skill to a command, or None when its document does not exist.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- The `pw skill` CLI tests live in `test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`, not in the 599-line `test_prompt_workflow_main.py`.
- `tools/prompt_workflow.py` stays under 550 lines after the edit.

#### Step 3 -- addendums for the subcommand

Line-budget checkpoint:

- `tools/prompt_workflow.py`: before 489 -> target <= 550 (add only the subparser and the thin dispatch).
- `tools/prompt_workflow_skill.py`: before Step 2 size -> target <= 550.

Split guidance:

- If the hub would cross 550, move the body of `run_skill` into the skill module and keep only a one-line call in the hub.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`; then `ghog day`.

Time-gated status for Step 3:

- No perf gate is affected.

### Step 4. Automated handoff sections in the writing and consolidation instructions

#### Step 4 -- analysis and intent for the handoffs

Issues to address:

- `write-requirement`, `write-design`, `write-plans`, and `consolidate-then-review-ask-questions` stop on a prose note; they must chain by running `pw skill`.
- The author needs a way to hold the chain at a writing step.

Fix intent:

- Add a `## Handoff` section to each of the four instructions, in the `implement-step.md` shape: run `pw skill`, read the bare command, run it straight away, with the go-ahead statement and no pause for confirmation.
- Document the "stop here" phrase: when the writing skill's argument carries the literal phrase `stop here`, the skill writes its document and skips the handoff.

Expected outcome:

- Each of the four instructions ends on a `## Handoff` that names `pw skill` and the document just written; `write-plans` hands off the plain plan only.

Step framing:

- Design link: design area 1 (the automated handoff contract) and the Q06 decision.
- Execution checklist reference: the shared execution command checklist above.

#### Step 4 -- implementation for the handoffs

**Files involved**:

- `instructions/write-requirement.md` (existing, to be updated).
- `instructions/write-design.md` (existing, to be updated).
- `instructions/write-plans.md` (existing, to be updated).
- `instructions/consolidate-then-review-ask-questions.md` (existing, to be updated).

**Tests first**:

- No unit test: these are instruction bodies. The grep checks below and the Step 6 acceptance test stand in for tests.

**Classes and behavior**:

- Each `## Handoff` section: the `pw skill` call, the confirm-and-run wording, and the "stop here" gate sentence for the three writing instructions.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`) -- unchanged, since no code is touched.
- A grep shows a `## Handoff` heading and a `pw skill` mention in each of the four files.
- A grep shows the `stop here` phrase documented in the three writing instructions.

#### Step 4 -- addendums for the handoffs

Line-budget checkpoint:

- The four instruction files gain a short section each; none is near the line limit. Record before and after counts but no split is expected.

Split guidance:

- None expected for these instruction files.

Full workflow timing run readiness:

- `ghog day` (the code gate is unaffected; this confirms nothing regressed).

Time-gated status for Step 4:

- No perf gate is affected.

### Step 5. The review hint, the no-question decisions table, and the multi-choice lists

#### Step 5 -- analysis and intent for the hint and lists

Issues to address:

- `review-ask-questions` gives no hint of the consolidation step, and leaves no on-disk signal when it raises no question.
- `process-draft` and `split-and-define` give prose guidance, not a selectable list.

Fix intent:

- Add the consolidation hint to `review-ask-questions`, carrying the reviewed document name, as plain text.
- Add the no-question behavior: when the review round raises no question, `review-ask-questions` writes a one-row decisions table ("No open questions, all decisions made") so `pw skill` advances straight to the next phase.
- Add the multi-choice lists: `process-draft` lists `/write-requirement` and `/split-and-define` on the produced draft; `split-and-define` lists one `/write-requirement` per slug it defined; each list closes with a "Type something else" entry the instruction adds.

Expected outcome:

- `review-ask-questions` always leaves an unambiguous on-disk state; the two splitting instructions present a selectable next-step list.

Step framing:

- Design link: design area 1 (the review hint, multi-choice lists) and design area 3 (the no-question decisions table, Q03), plus the Q05 split-fork-ownership decision.
- Execution checklist reference: the shared execution command checklist above.

#### Step 5 -- implementation for the hint and lists

**Files involved**:

- `instructions/review-ask-questions.md` (existing, to be updated).
- `instructions/process-draft.md` (existing, to be updated).
- `instructions/split-and-define.md` (existing, to be updated).
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py` (new, to be created).

**Tests first**:

- A structural unit test that asserts each of the seven edited instructions (the four from Step 4 and the three here) carries its `## Handoff`, consolidation hint, or multi-choice list. It runs on every `ghog day`, so a later edit that drops one fails fast (Q06).

**Classes and behavior**:

- `review-ask-questions`: the consolidation hint and the no-question one-row decisions-table rule.
- `process-draft` and `split-and-define`: the multi-choice list shape, with the trailing "Type something else" entry the instruction owns.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`), including the new structural instruction test.
- A grep shows the consolidation hint and the no-question rule in `review-ask-questions.md`.
- A grep shows a multi-choice list and a "Type something else" entry in both splitting instructions.

#### Step 5 -- addendums for the hint and lists

Line-budget checkpoint:

- Three instruction files gain a short section each; none is near the line limit.
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`: before 0 -> target <= 550.

Split guidance:

- None expected for these instruction files.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`; then `ghog day`.

Time-gated status for Step 5:

- No perf gate is affected.

### Step 6. Acceptance tests for the chained workflow

#### Step 6 -- analysis and intent for the acceptance tests

Issues to address:

- The disk-derived routing, the host prefix, the forced skill, and the no-question table need an end-to-end check on a real scratch tree, larger than the unit tests.

Fix intent:

- Add acceptance tests that build a scratch `docs/` tree in each state and assert the `pw skill` command and prefix; cover the forced-skill and `-1` paths and the host override; assert the consolidated and no-question states route to the next phase.
- Add a structure check that each edited instruction carries its `## Handoff`, hint, or multi-choice list.

Expected outcome:

- One acceptance suite proves the chain end to end, host prefix included.

Step framing:

- Design link: the acceptance cases table of `docs/design.v0.9.0.handoff_automation.md`.
- Execution checklist reference: the shared execution command checklist above.

#### Step 6 -- implementation for the acceptance tests

**Files involved**:

- `tests/unit/tools/test_prompt_workflow_acceptance.py` -> `tests/unit/tools/test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py` (existing, moved into the nested form and updated here; Q08).

**Tests first**:

- The scratch-tree cases for each document state, the forced-skill and `-1` cases, and the override case (the instruction structure is now guarded by the Step 5 unit test).

**Classes and behavior**:

- Acceptance helpers that lay down a scratch tree and drive `pw skill` in-process through `main(argv)`, capturing stdout and setting the host markers in the test, matching the existing CLI-test style (Q07).

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`), full suite and coverage included.
- The acceptance suite asserts both `/` and `$` prefixes through the override, since the live host is Claude.

#### Step 6 -- addendums for the acceptance tests

Line-budget checkpoint:

- `tests/unit/tools/test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py` (moved from `test_prompt_workflow_acceptance.py`): before 240 -> target <= 550.

Split guidance:

- If the acceptance file would cross 550, move the `pw skill` cases into a sibling nested leaf `test_prompt_workflow_skill_acceptance/test_prompt_workflow_skill_acceptance_tdd.py`.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_acceptance.py`; then `ghog day`.

Time-gated status for Step 6:

- No perf gate is affected; the perf-gate pass concluded no Step 0 gate is needed.

### Step 7. The commit-gate multi-choice in group-commits-msg

#### Step 7 -- analysis and intent for the commit gate

Issues to address:

- `group-commits-msg` waits for a typed `go ahead`; it must instead present a multi-choice that, after the commit, can chain to the next plan step or to prepare-release.
- `pw skill` derives the next workflow step but not yet the post-commit next action (next plan step, prepare-release, or none).

Fix intent:

- Extend the skill module so `pw skill`, told the step the commit completes, derives the post-commit next action: the next unimplemented step after it (via `derive_x` over the validation plan) gives `go ahead, and implement step x`; when that committed step was the last, every step is committed and it gives `go ahead and prepare-release`; with no plan resolved it gives only `go ahead`.
- Edit `instructions/group-commits-msg.md` so the commit gate, with an effort in flight, presents the constant `go ahead`, the `pw skill` contextual option, and a "Type something else" entry; a standalone call shows only `go ahead`. Plain `go ahead` commits and stops; the contextual option commits and, only after the commit succeeds, chains to `/implement-step` on x or `/prepare-release` (a failed commit aborts the chain).

Expected outcome:

- The commit gate offers the right multi-choice for the branch state, and only the contextual option chains after the commit.

Step framing:

- Design link: design area 6 (the commit-gate multi-choice) and its design-decision rows.
- Execution checklist reference: the shared execution command checklist above.

#### Step 7 -- implementation for the commit gate

**Files involved**:

- `tools/prompt_workflow_skill.py` (existing, to be updated).
- `instructions/group-commits-msg.md` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py` (existing, to be updated -- assert the commit-gate multi-choice in `group-commits-msg.md`).

**Tests first**:

- The post-commit derivation, given the committed step: a plan with a next unimplemented step after it yields the implement-step-x option; a plan whose committed step was the last yields the prepare-release option; no plan yields only `go ahead`.
- The structural test gains a case asserting `instructions/group-commits-msg.md` carries the commit-gate multi-choice.

**Classes and behavior**:

- A skill-module function that, given the committed step, derives the post-commit next action by reusing `parse_validation_steps` and `derive_x`: the next step after the committed one gives implement-step x; the last step gives prepare-release; no plan gives none.
- `instructions/group-commits-msg.md`: the commit-gate multi-choice wording -- the constant `go ahead`, the `pw skill` contextual option, and the "Type something else" entry when an effort is in flight (only `go ahead` when standalone); the plain-go-ahead-stops rule; and the contextual option chaining only after a successful commit.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- A grep shows the commit-gate multi-choice and `pw skill` in `instructions/group-commits-msg.md`.
- `tools/prompt_workflow_skill.py` stays under 550 lines after the edit.

#### Step 7 -- addendums for the commit gate

Line-budget checkpoint:

- `tools/prompt_workflow_skill.py`: before Step 3 size -> target <= 550.
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`: before Step 3 size -> target <= 550.

Split guidance:

- If the skill module crosses 550, split the post-commit derivation into a `prompt_workflow_skill_commit.py` helper.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py`; then `ghog day`.

Time-gated status for Step 7:

- No perf gate is affected.

## Implementation decisions for v0.9.0 handoff_automation

These rows record the implementation choices settled in the plan review (Q01 to Q08) and the follow-up commit-gate request; each names the question or request that settled it, the step or section where it is integrated, and the options that were turned down.

| Area | Decision | Question | Integrated in | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Test-file layout | New tests use the nested form `test_<module>/test_<module>_tdd.py`; existing pw tests move into it for consistency (move scope is the open question below) | Q01 | Steps 1 to 6, test-tree snapshot | The flat `test_<module>.py` form |
| Next-step derivation | Reuse `next_step_numbers`, then post-process: a decisions table on the current document overrides the review-or-consolidate answer to the advance step; `next_step_numbers` is unchanged | Q02 | Step 2 | A separate skill-side resolver; extend `next_step_numbers` itself |
| Not-applicable signal | Empty stdout, a one-line stderr note, and a dedicated non-zero exit code; the internal `-1` maps to that code | Q03 | Step 3 | Print `-1` on stdout; print nothing and exit 0 |
| Skill-to-role map | A small static map in the skill module | Q04 | Step 3 | Derive it from `prompt_workflow.steps.json` |
| run_skill placement | The body lives in the skill module from the start; the hub holds only the subparser and a one-line call | Q05 | Step 3 | Put it in the hub, move only if over 550 |
| Doc-step gate test | A small structural unit test asserts each edited instruction carries its handoff, hint, or list, run on every walk | Q06 | Step 5 | Grep plus the one-off acceptance check only |
| Acceptance harness | Drive `pw skill` in-process through `main(argv)`, capturing stdout, host markers set in-test | Q07 | Step 6 | Spawn the launcher as a subprocess; call the module functions directly |
| Existing-test move scope | Move only the two pw test files this feature edits (`_docs` in Step 2, `_acceptance` in Step 6) into the nested form, within those steps; defer the full eleven-file migration and the 599-line split to a separate effort | Q08 | Steps 2 and 6, scope anchors | Move all pw test files now; move none |
| Commit-gate multi-choice | `group-commits-msg` presents a constant `go ahead`, a `pw skill`-derived contextual option (implement the step after the one committed, or prepare-release when all are committed), and a "Type something else" entry when an effort is in flight; a standalone call shows only `go ahead`. Plain `go ahead` stops; the contextual option chains only after a successful commit | follow-up | Step 7, design area 6 | LLM infers the option; re-offer the committed step; chain regardless of the commit result; keep "Type something else" when standalone |
