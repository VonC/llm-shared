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

Not started. Step 2 is not implemented because `has_decisions_table` does not exist in `tools/prompt_workflow_docs.py` and no disk-derived routing has been written.

The settled-versus-review fork and the next-command derivation are absent.

### Goal for Step 2

Add `has_decisions_table` to `tools/prompt_workflow_docs.py`, and in the skill module derive the next step from disk with `compute_state` and `next_step_numbers` (no memory step), mapping the step to its instruction and target document, so a new draft routes to `process-draft`, an open-questions document to `review-ask-questions`, and a document with a decisions table to the next phase.

### Step 2 improvement expectations

- `has_decisions_table` detects the three consolidated section titles and is absent otherwise.
- The next command is derived from disk only, with no read of `a.prompt_memory`.
- The most-advanced artifact sets the reported step.

### What was implemented for Step 2

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

---

## Step 3. The pw skill subcommand, the forced skill, and the host override

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because `tools/prompt_workflow.py` has no `skill` subparser and no `run_skill` dispatch.

The forced-skill argument and the host override are not wired.

### Goal for Step 3

Add a `skill` subparser on the shared parent parser of `tools/prompt_workflow.py`, with an optional skill-name positional and a host-override option, and a thin `run_skill` that delegates to the skill module; add `forced_command` so a named skill emits its command when its document exists, or `run_skill` exits `-1` when the skill is not yet applicable.

### Step 3 improvement expectations

- `pw skill` prints the disk-derived next command; `pw skill <name>` prints that skill's command or exits `-1`; the host override sets the prefix and skips detection.
- `tools/prompt_workflow.py` stays under 550 lines.
- The CLI tests live in `test_prompt_workflow_skill.py`, not in the 599-line `test_prompt_workflow_main.py`.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

---

## Step 4. Automated handoff sections in the writing and consolidation instructions

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because none of `write-requirement.md`, `write-design.md`, `write-plans.md`, or `consolidate-then-review-ask-questions.md` carries a `## Handoff` section yet.

The automatic chaining and the "stop here" gate are absent.

### Goal for Step 4

Add a `## Handoff` section to the four instructions in the `implement-step.md` shape (run `pw skill`, read the bare command, run it straight away, no pause), and document the "stop here" phrase that holds the chain at a writing step.

### Step 4 improvement expectations

- Each of the four instructions ends on a `## Handoff` naming `pw skill` and the document just written.
- `write-plans` hands off the plain plan only, never the validation plan.
- The three writing instructions document the "stop here" phrase.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.

---

## Step 5. The review hint, the no-question decisions table, and the multi-choice lists

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because `review-ask-questions.md` has no consolidation hint and no no-question rule, and the splitting instructions present no selectable list.

The hint, the no-question decisions table, and the multi-choice lists are absent.

### Goal for Step 5

Add the consolidation hint and the no-question one-row decisions-table rule to `review-ask-questions.md`, and the multi-choice lists to `process-draft.md` and `split-and-define.md`, each closing with a "Type something else" entry the instruction owns.

### Step 5 improvement expectations

- `review-ask-questions` always leaves an unambiguous on-disk state, even on a no-question round.
- `process-draft` lists `/write-requirement` and `/split-and-define` on the produced draft.
- `split-and-define` lists one `/write-requirement` per slug it defined.

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

---

## Step 6. Acceptance tests for the chained workflow

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because no acceptance test drives `pw skill` across the document states.

The end-to-end coverage of the routing, the host prefix, the forced skill, and the no-question table is absent.

### Goal for Step 6

Add acceptance tests that build a scratch `docs/` tree in each state and assert the `pw skill` command and prefix, cover the forced-skill and `-1` paths and the host override, and check that each edited instruction carries its `## Handoff`, hint, or multi-choice list.

### Step 6 improvement expectations

- One acceptance suite proves the chain end to end, with both `/` and `$` prefixes asserted through the override.
- The consolidated and no-question states route to the next phase.
- The instruction-structure checks pass for all seven edited instructions.

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.
