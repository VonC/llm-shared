# Code review transcript for v0.14.0

- Exchange: code/code/v0.14.0/resume-paused
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-11-15T17:31:02+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 resume-paused (round 1)

request_index_tree: 7c4e4ceeb69383822d5cf47607b59aa1941100a1
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 1)

Step 1 is implemented as a code deliverable, as plan Q05=A scopes it. It is not a support claim: the shipped profile registry pins nothing, every real pane classifies as unsupported or pending, and the live validation checklist in the validation plan has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-15T17:29:08+01:00, 5983 tests, no failure, no outlier, no exclusion.
- Static checks: the same walk's `check.bat` passes pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check.
- Coverage: 100% over `tools`, including the four new modules. Two failure branches of the Win32 binding that need a failing kernel call carry a coverage exclusion comment.
- Architecture: policy and both host modules depend on injected protocols; only the Win32 binding touches `ctypes`. No module writes a file, sends input or starts a process.
- Performance: single passes with set and map lookups; read cost follows the files actually read and is accounted.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 1)

Four read-only modules implement the Step 1 contracts of the consolidated design behind injected protocols.

- `tools/resume_paused_profiles.py`: verdicts, counted reasons, byte accounting, an empty pinned-profile registry, caller classification, the boot comparison and five disclosed limits.
- `tools/resume_paused_windows.py`: the query-only Win32 binding (process listing, creation time, native image name, allocation walk, class 44 identity, same-handle hashing, shared reads) and a complete JSONL directory listing that follows no link or junction.
- `tools/resume_paused_codex.py`: release layout and manifest checks, the loaded-image prover with recheck, the session-file input proof with a carried launch id, the pane-tie proof and a directory session store.
- `tools/resume_paused_claude.py`: allowlisted transcript parsing and a lifecycle ledger that reports absence or pending with counted reasons, plus a directory transcript source. Its closed-world sets come from a profile object; none is shipped.
- Tests: pure shared builders and four test packages. The Win32 tests observe the test process itself with query rights only and start no process.

Points for the reviewer's attention:

- The user confirmed five decisions on 2026-11-15, recorded as unconsolidated question blocks: design Q27=B and Q28=A, plan Q05=A, Q06=A and Q07=A. They have had no independent specification review. The fifth disclosed limit in code follows Q27=B, while the design body still describes four limits.
- Plan Q06 records two corrections: its baseline option could not be applied. Under the user's exceptions, the two v0.14.0 review transcripts were repaired instead: 26 headings of the design transcript gained an exchange qualifier, 10 list blocks gained a preceding empty line, and one token moved across a line break in the plan transcript. The baseline file is unchanged.
- `instructions/pause-session.md` regains one word that commit d2227928 of this branch had changed against an existing structure test.
- The first cold covered run of the suite stopped once with a pytest internal error naming a rejected process launch during a Markdown property test. It did not recur in later runs and its cause was not found.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 1)

Twenty staged paths in five `a.commit` groups, in this order:

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: `docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md`, `docs/v0.14.0/review.plan.v0.14.0.resume-paused.md`.
3. `docs(resume-paused): record Step 1 decisions`: `docs/v0.14.0/design.v0.14.0.resume-paused.md`, `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
4. `feat(resume-paused): add host evidence adapters`: `tools/resume_paused_profiles.py`, `tools/resume_paused_windows.py`, `tools/resume_paused_codex.py`, `tools/resume_paused_claude.py`, `tests/unit/tools/resume_paused_test_support.py`, the four `tests/unit/tools/test_resume_paused_*` packages (one package file and one test file each), and `docs/v0.14.0/resume-paused.profile-evidence.md`.
5. `docs(resume-paused): record step 1 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 1)

Writer response:

First round: no earlier feedback to answer and no disagreement.

### Reviewer focus for step 1 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.14.0.resume-paused.md`
- `.reviews/a.review-requested.code.v0.14.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-11-15T20:09:58+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 1)

Baseline index tree: 7c4e4ceeb69383822d5cf47607b59aa1941100a1

Assessed index tree: 536f3caa2c7e0d85f91d1bce701722793d29f5b4

### Implementation check for step 1 resume-paused (exchange 1) (round 1)

Result:

No. Step 1 has NOT been fully implemented.

The Step 1 adapter code and tests exist, but eight completeness/rejection findings remain. This assessment applies plan Q05=A: live profiles may remain unpinned while code is delivered, Steps 2 through 5 may proceed, and Steps 6 through 8 remain blocked. The empty shipped registry is correct; none of these findings claims that delivery is currently enabled. Findings R1 through R8 concern the adapter code contract and its synthetic tests. No DDD/ports-and-adapters layering violation, new superlinear computation or regression in an existing caller was identified; the modules have no caller yet.

Validation plan effects:

Updated only Step 1 in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: the exact No verdict, the immediately following missing-work inventory after implemented work, and the unit-test assessment. Preserved the live-validation deferral, every other step and the document-level status. The metadata patch was attributed and staged; no implementation or test was changed.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 1)

Requestor evidence: `ghog day --full=speed --whole-suite`, exit 0 at 2026-11-15T17:29:08+01:00, 5983 tests, no reported failures/outliers/exclusions; earlier covered full run at 17:22:29 reported 100% over `tools`. The four production modules are within `[tool.coverage.run].source = ["tools"]`. Tests reference the production symbols and shared builders, but omit the adverse cases in R1 through R8; two Win32 kernel-failure branches are excluded. This is a static coverage assessment, not a new percentage measurement. No reviewer test/coverage walk was run or needed to establish the cited code paths. The writer's single earlier cold-run pytest internal error remains reported as unreproduced with unknown cause; it is not promoted into a separate blocker after the reported green runs. The edited validation Markdown passed markdownlint with 0 issues.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 1)

`ghog day --full=speed --whole-suite` (source: `project`). No plan/request additions are declared in the request set. No `.review-validation` file exists, so the built-in default applies. The current read-only `pw scope day --full=speed` result is the identical command; the bound scope is whole-suite, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 1)

None. Request-time and current resolved command and scope agree; no addition, removal or source change was found. The command was resolved only, not executed.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 1)

Baseline/request index: `7c4e4ceeb69383822d5cf47607b59aa1941100a1`. Assessed index: `536f3caa2c7e0d85f91d1bce701722793d29f5b4`. The before/after evidence launcher reports only the reviewed validation plan changed among the same 20 tracked paths, with no untracked differences. Its generic `acceptable: false` flags that tracked change; manual classification confirms it is the expressly permitted Step 1 review metadata. No umbrella applies and its comparison is unchanged/not applicable. Attribution returned true. The baseline validation blob also matched its original index blob, so staging that exact path included only the attributed metadata change. The ignored `a.commit` group 5 body was corrected from the stale Yes claim to the current review result; membership, ordering and subjects are unchanged. No other working-tree diff remains.

### Repair inventory for step 1 resume-paused (exchange 1) (round 1)

Repairs made:

- Review metadata only: Step 1 validation-plan rows, attributed and staged. No substantive code/test repair.
- Review metadata only: ignored `a.commit` group 5 explanatory body aligned with the No verdict. No grouping, ordering, membership or subject change.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: only reviewer-staged path; all 20 requestor-staged paths remain present.

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 1)

Independent checker before assessment and after metadata staging: exit 0, state `valid`, ready `true`, diagnostics empty. All 20 staged paths are accounted for. Ordered groups remain:

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: `docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md`, `docs/v0.14.0/review.plan.v0.14.0.resume-paused.md`.
3. `docs(resume-paused): record Step 1 decisions`: `docs/v0.14.0/design.v0.14.0.resume-paused.md`, `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
4. `feat(resume-paused): add host evidence adapters`: `tools/resume_paused_profiles.py`, `tools/resume_paused_windows.py`, `tools/resume_paused_codex.py`, `tools/resume_paused_claude.py`, `tests/unit/tools/resume_paused_test_support.py`, `tests/unit/tools/test_resume_paused_profiles/__init__.py`, `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`, `tests/unit/tools/test_resume_paused_windows/__init__.py`, `tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py`, `tests/unit/tools/test_resume_paused_codex/__init__.py`, `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`, `tests/unit/tools/test_resume_paused_claude/__init__.py`, `tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py`, `docs/v0.14.0/resume-paused.profile-evidence.md`.
5. `docs(resume-paused): record step 1 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The ordering places the authorized documentation fixes and recorded decisions before the adapter delivery, then the validation record. The user-authorized transcript lint repair is assessed as declared metadata scope, without using transcript content as review context. The group 5 body now describes the reviewer verdict accurately. Mechanical readiness does not settle completeness or authorize a commit.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 1)

Unresolved findings:

- [P1] R1: Enforce closure for every input and chain tip (`tools/resume_paused_claude.py:426`, `:451`). `_closure` drops all sidechain records and records without UUIDs; `_inputs` silently skips missing parents, and duplicate UUIDs overwrite earlier facts. Appending `dict(typed('nested', 't1-end', 20), isSidechain=True)` to the existing `closed_turn()` fixture leaves every check unchanged and permits `PROVED` for an open recorded input. An input without a UUID is likewise omitted. Validate graph identity, parent completeness and every in-scope input/tip, including nested work; allow only explicitly profile-validated non-input leaves. Add regression cases for sidechain input, absent/duplicate UUIDs and broken parent links. The existing sidechain test must not authorize blanket exclusion.
- [P1] R2: Classify every contributing transcript under its own pinned version (`tools/resume_paused_claude.py:339`, `:375`). Version checking exists only in `_linkage`, called only for the bound file. A second recent `closed_turn()` with every version changed to an unknown release is accepted under the bound file's profile. Pre-boot durable-schedule files bypass `_classify` and `_calls` entirely; an unknown record/tool encoding a durable schedule can therefore disappear from the proof. Require validated version/schema coverage for every contributing generation and schedule read; unknown/missing coverage must remain pending. Test unknown-version nonbound files and pre-boot unknown/incomplete schedule records, while preserving the approved ordinary-process boot cutoff.
- [P1] R3: Correlate individual task and schedule lifecycles, preserving ordering and ambiguity (`tools/resume_paused_claude.py:304`, `:312`, `:365`, `:375`). Global ID sets erase start multiplicity, chronology and originating scope. In the existing completed-watcher fixture, move `task_ended` after the startup marker but before the watcher start, with an earlier timestamp: the same terminal ID still clears the later start. `CronDelete(job1)` followed by `CronCreate(job1)` also resolves to absence. Distinct starts with a reused ID collapse, and unrelated files can close each other's IDs without proved continuity. Match each start to its own validated later terminal/cancellation, retain ambiguous duplicates as pending, and preserve proved cross-file matching after clear. Add regressions for preceding terminals, delete-before-create, duplicate/reused IDs and unrelated-session collisions.
- [P1] R4: Implement the planned Claude requestor-operation and marked-file evidence contract (`tools/resume_paused_claude.py:198`, `:257`, `:375`). `LedgerScope` has no proved marked input, creation-order boundary, report-source identity or operation classifier; parsing discards command semantics, and all starts enter one unconditional set. The approved Q22/Q24 exception for a recognized post-marker requestor `wait-answer` can never apply, so the intended requestor/reviewer continuation remains pending even with otherwise valid synthetic evidence. Q23 also lacks full marked-input proof and a fresh process/session binding across the read; the bound transcript's `cwd` is not checked. Add the Step 1 read-only evidence interfaces and bounded operation classification, with full input comparison performed in memory and no retained payloads. Test eligible requestor starts, reviewer watchers, wrapped/chained/shared operations, uncertain ordering, earlier starts completed after clear, wrong checkout and changed binding. Keep Step 4 instruction/receiver wiring outside this repair.
- [P2] R5: Reject malformed Claude structural fields without inventing identity or throwing (`tools/resume_paused_claude.py:139`, `:170`, `:398`). Missing tool-call `id` and tool-result `tool_use_id` both become the string `None`, allowing an invalid pair to match in `_calls`. A timezone-free ISO startup timestamp parses successfully and then raises `TypeError` when compared with the aware process creation time. Validate required identifier types/nonempty values and timestamp timezone semantics under the profile; classify malformed evidence as pending with counted reasons. Add tests for missing/non-string linkage IDs, naive timestamps and mixed text/tool-result input records, which currently lose their input-bearing classification.
- [P1] R6: Reject incomplete Win32 process enumeration (`tools/resume_paused_windows.py:253`). After any false `Process32FirstW`/`Process32NextW`, `processes()` returns the accumulated tuple without checking the Win32 error. A failure after the first matching child can conceal another child and feed a false unique-child result to both host adapters. Distinguish normal `ERROR_NO_MORE_FILES` termination from every other failure, return unavailable evidence on failure, and retain handle cleanup. Exercise first/next-call failures with an injected native binding seam; a successful live self-observation does not cover this failure path.
- [P2] R7: Validate the full Codex session/input record shape before issuing a proof (`tools/resume_paused_codex.py:336`). Removing `session_meta.payload.id` from the matching fixture still returns `SUPPORTED` with `session_id='None'`. The latest-input matcher also accepts any `response_item` with role `user` and one block containing the expected text, without requiring the validated message and input-text block types. Require well-typed nonempty session identity and the supported complete user-input schema; reject malformed, missing or ambiguous structural evidence. Add cases for absent/null/wrong-type IDs, unsupported message/block types and duplicate structural keys. Retain the exact text, checkout, time, version and uniqueness checks.
- [P1] R8: Match the validated Codex pane signature, not arbitrary substrings (`tools/resume_paused_codex.py:359`). `prove_codex_pane(['quoted launch-1', 'documentation about Working'], 'launch-1', 'Working')` returns no reason, although neither line proves an accepted command or host busy state. An empty working signature accepts any later line, and a longer launch token containing the queried token also matches. Require the profile's attributable submitted-command/launch-prefix structure and actual Working-state line, reject empty/unsupported signatures and ambiguous token boundaries, and add negative fixtures for quoted output, prose, placeholders and longer IDs. Keep later delivery orchestration in its assigned step.

Boundary-crossing work:

- Preserve plan Q05=A's separate live matrix and empty registry; no request to pin either host in this code-repair round. Both pinned hosts remain a prerequisite for Steps 6 through 8.
- Do not implement Step 4 receiver/instruction transport wiring or Step 6 delivery orchestration as part of R4/R8. Add only the Step 1 read-only evidence contracts and tests.
- Design Q27=B and Q28=A and plan Q05/Q06/Q07 are confirmed user decisions recorded in unconsolidated blocks. Their consolidation/specification-review status remains disclosed; the reviewer has not performed that separate workflow.

### Writer instructions for step 1 resume-paused (exchange 1) (round 1)

Address R1 through R8 in the Step 1 adapters and focused synthetic unit tests. Preserve the fail-closed empty supported-profile registry and the deferred live checklist. For each finding, show the regression case and the corrected rejection or matching result, including valid cross-file clear continuation. Reassess the exact Step 1 validation rows, update `a.commit` to the resulting staged state, run the requestor-owned resolved validation command and coverage gate, then publish a new exact review request with fresh index and bound-scope evidence. If a finding needs a new design choice, return that specific point rather than inventing a policy. No reviewer implementation repairs were authorized by a literal `Human guidance:` block; the request's generic repair prose did not change that boundary.

### Decision rationale for step 1 resume-paused (exchange 1) (round 1)

Changes requested. Six readiness-floor results:

1. Exact identity: PASS. Correct code family, plan, Step 1, round 1, occurrence 1, request index and retained evidence.
2. Implementation completeness: FAIL. R1 through R8 remain; Q05's live-validation deferral does not waive code correctness.
3. Validation and coverage: INCOMPLETE. Writer's green evidence is recorded and resolver agrees; static assessment identifies missing adverse test cases. No full or focused test walk was repeated by the reviewer.
4. Staged attribution: PASS. Only the attributable Step 1 metadata patch was staged; no implementation repair or boundary violation.
5. Unresolved findings: FAIL. Eight current findings remain, with concrete writer actions.
6. Commit plan: PASS mechanically and semantically for the current staged scope after correcting the group 5 description. This is advisory and grants no commit authority.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-11-15T20:42:03+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 resume-paused (round 2)

request_index_tree: 888b598fae9c8d413e15a63e4c4c8ec567303d55
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tools/resume_paused_claude_ledger.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 2)

Step 1 is implemented as a code deliverable under plan Q05=A, with the eight round 1 findings repaired. It remains no support claim: the shipped registry pins nothing and the live validation checklist has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-15T20:40:18+01:00 on the staged index, proof speed, no failure, no outlier, no exclusion.
- Static checks: the walk's `check.bat` passes pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check.
- Coverage: 100% over `tools`, including the five new modules.
- Architecture: the ledger moved to its own module and imports the parsing module; only the Win32 binding touches `ctypes`; no module writes a file, sends input or starts a process.
- Performance: single passes with set and map lookups; start and end matching indexes ends by identifier, and descendants of the marked input are computed once.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 2)

Round 1 findings and their repairs, each with regression cases in the named test package:

- R1 (`tools/resume_paused_claude_ledger.py`, `test_resume_paused_claude_ledger`): closure covers every identified record, sidechains included. A sidechain input appended to the closed fixture, an input without an identifier, a repeated identifier and a broken parent link are each pending. A sidechain or fan-out leaf proves nothing unless the profile lists its shape.
- R2 (same): every transcript read must carry the pinned version and pass closed-world classification, including a schedule-only read before boot. Cases: nonbound file of another version; pre-boot file of another version, with an unknown record, with an unknown tool, and truncated. The boot cutoff for ordinary task starts is kept.
- R3 (same): each start is matched to its own later end by identifier and instant. Cases: terminal before its start, terminal without an instant, deletion before creation, reused task and schedule identifiers, and a terminal in an unrelated session file all leave the start open; a file that begins with a clear marker still closes an earlier file's start.
- R4 (`tools/resume_paused_claude.py`, both Claude test packages): parsing matches the complete marked input in memory and classifies each recorded command that names the launcher as a requestor operation or a watcher, keeping only the class. The ledger scope carries the marked input, the identity source and the process generation; it requires the bound transcript to record the checkout, a report-sourced identity, and the same process after the read. Only a start whose single answered call descends from the proved marked input and is a recognized requestor operation is excluded. Cases: eligible `wait-answer`; reviewer watcher; chained, piped, redirected and wrapped commands; shared-role operation; other work; start before the marked input; missing, repeated and untyped marked input; wrong checkout; changed binding; unreported identity. Step 4 receiver wiring is not included.
- R5 (`tools/resume_paused_claude.py`, `test_resume_paused_claude`): a tool call or result without a nonempty string identifier, a timestamp without a timezone or of another type, and a repeated JSON key reject the transcript. A record with text and a tool result stays input-bearing.
- R6 (`tools/resume_paused_windows.py`, `test_resume_paused_windows`): the process listing is returned only when the walk ends with `ERROR_NO_MORE_FILES`. Cases replace the first and the next native call with a failing one.
- R7 (`tools/resume_paused_codex.py`, `test_resume_paused_codex`): the session metadata needs nonempty string identity, checkout and version; the latest user record must be one message with exactly one `input_text` block holding string text; a repeated key and a second metadata record are rejected.
- R8 (same): the pane proof takes a profile with the submitted-command prefix and a working-line pattern. The launch id must appear as a whole token on exactly one line, that line must start with the prefix, and a later whole line must match the pattern. Cases: quoted output, prose, placeholder, longer id, repeated id, indented prompt, trailing text, and empty or invalid signatures.

Other points:

- The ledger was split from the parsing module by responsibility; both stay below 400 lines.
- In one walk during this round, three unrelated tests of `test_groundhog_acceptance_group_args_file_tdd.py` exceeded their CPU budget by one to four timer ticks. They passed in focus and in the next walk; none touches the changed files.
- No accepted duration exclusion exists.
- The points disclosed in round 1 are unchanged: unconsolidated question blocks with confirmed user decisions, the transcript repairs made under the user's exceptions, the unchanged baseline file, and the single unexplained internal error of the first cold run.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 2)

Twenty-three staged paths in five `a.commit` groups; order, subjects and groups 1 to 3 are unchanged from round 1.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: the two v0.14.0 specification review transcripts.
3. `docs(resume-paused): record Step 1 decisions`: the design and the plan.
4. `feat(resume-paused): add host evidence adapters`: adds `tools/resume_paused_claude_ledger.py` and the `tests/unit/tools/test_resume_paused_claude_ledger` package (two files) to the round 1 members; its body now names five modules.
5. `docs(resume-paused): record step 1 validation`: the validation plan, whose Step 1 rows the writer reassessed after the repairs.

Changed since round 1: the four earlier `tools/resume_paused_*.py` modules, the new ledger module, the shared builders, the Codex, Windows and Claude test files, and the validation plan. The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 2)

Writer response:

All eight round 1 findings, R1 through R8, are accepted and repaired; there is no disagreement. The reviewer's two metadata repairs are kept in substance: the validation plan's Step 1 rows were then reassessed by the writer after the code repairs, and the group 5 body of `a.commit` was updated to that state. No finding needed a new design choice.

### Reviewer focus for step 1 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-11-15T20:50:12+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 2)

Baseline index tree: 888b598fae9c8d413e15a63e4c4c8ec567303d55

Assessed index tree: a8cd1338ebac364684702cb9eefa960324c38e6e

### Implementation check for step 1 resume-paused (exchange 1) (round 2)

Result:

No. Step 1 has NOT been fully implemented.

Round 2, occurrence 1: the Claude evidence ledger still admits unproved absence through six cases detailed below. The original Windows process enumeration, Codex schema, malformed scalar/duplicate JSON, and pane-signature findings have been addressed. Claude version scope was strengthened, but nested content classification remains incomplete.

Plan Q05=A permits Step 1 code completion before live profile pinning. The empty shipped registry is appropriate and is not a Step 1 code blocker. Steps 2–5 may proceed under that decision; Steps 6–8 remain blocked until both hosts are pinned.

Validation plan effects:

Updated only Step 1 in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: retained the No verdict, replaced missing work with six round 2 findings, updated writer validation evidence, and clarified the coverage limits. Other steps and live evidence requirements are unchanged. No umbrella applies.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 2)

The request reports successful `ghog day --full=speed --whole-suite` at 2026-11-15T20:40:18+01:00, 100% tools coverage, and no duration exclusion or outstanding outlier. Earlier unrelated CPU duration outliers passed subsequently. This is writer-owned evidence; the reviewer ran no tests, coverage commands, or executable counterexample probes.

Coverage source is `tools` in `pyproject.toml`; all five new implementation modules are measured. Two Win32 failure branches retain exclusions and Windows-only tests limit portability of the reported evidence. Green measured coverage does not exercise the six adverse cases established by static reasoning.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 2)

The request binds whole-suite speed validation with scope fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The reviewer inspected the bound scope and sampled `.review-validation` absent. Independent `prompt_workflow.bat scope day --full=speed` resolved `ghog day --full=speed --whole-suite`, matching the request. The requestor owns execution of this validation set.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 2)

None. Request-bound and current resolver command/scope agree.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 2)

Request index tree and captured baseline both equal `888b598fae9c8d413e15a63e4c4c8ec567303d55`. Assessed index tree is `a8cd1338ebac364684702cb9eefa960324c38e6e` after staging the attributed Step 1 validation metadata only.

The validation-state comparison reports `acceptable:false` with exactly the validation-plan path and `<index>` changed. These are the explicitly permitted reviewer metadata edit and its staging, not test side effects. No other tracked digest changed; no untracked path appeared. No tests were run. Umbrella comparison reports `applicable:false`, `changed:false`. The original unstaged diff was empty; attribution returned `attributable:true` before exact-path staging.

### Repair inventory for step 1 resume-paused (exchange 1) (round 2)

Repairs made:

- Metadata only: updated and staged the attributed Step 1 validation assessment; adjusted ignored `a.commit` group 5 prose to match the No verdict. No implementation or test repair was performed.

Paths staged:

- `docs/v0.14.0/design.v0.14.0.resume-paused.md`
- `docs/v0.14.0/plan.v0.14.0.resume-paused.md`
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`
- `docs/v0.14.0/resume-paused.profile-evidence.md`
- `docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md`
- `docs/v0.14.0/review.plan.v0.14.0.resume-paused.md`
- `instructions/pause-session.md`
- `tests/unit/tools/resume_paused_test_support.py`
- `tests/unit/tools/test_resume_paused_claude/__init__.py`
- `tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/__init__.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py`
- `tests/unit/tools/test_resume_paused_codex/__init__.py`
- `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`
- `tests/unit/tools/test_resume_paused_profiles/__init__.py`
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`
- `tests/unit/tools/test_resume_paused_windows/__init__.py`
- `tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py`
- `tools/resume_paused_claude.py`
- `tools/resume_paused_claude_ledger.py`
- `tools/resume_paused_codex.py`
- `tools/resume_paused_profiles.py`
- `tools/resume_paused_windows.py`

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json` passed before assessment and again after metadata changes: exit 0, `state:valid`, `ready:true`, 23 staged paths, five groups, diagnostics empty. Ordered groups and membership are retained in the caller evidence JSON.

1. `docs(pause): restore the pinned choice wording` (1 paths).
2. `docs(resume-paused): repair review transcript lint` (2 paths).
3. `docs(resume-paused): record Step 1 decisions` (2 paths).
4. `feat(resume-paused): add host evidence adapters` (17 paths).
5. `docs(resume-paused): record step 1 validation` (1 paths).

Grouping remains coherent: pinned pause wording, authorized transcript lint repairs, recorded decisions, adapters/tests/profile evidence, then validation. Group 5 now accurately records incomplete implementation. Mechanical validity does not authorize commit while findings remain.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 2)

Unresolved findings:

- **[P1] R2-1: Prove closure per input and reject cyclic record graphs** — `tools/resume_paused_claude_ledger.py:352-389`. The graph checks missing parents but not cycles, and `_tips` accepts a profile-listed leaf shape without proving that its input's turn closed. Starting from `closed_turn()`, append the sidechain typed-input/reply pair already used by `test_every_input_and_chain_tip_is_checked`, then use `leaf_shapes=frozenset({'assistant'})`: the main turn remains closed, the sidechain tip is allowed, and `_inputs` skips its parentless input, so the ledger reports PROVED while that recorded turn has no Stop/final pair. An appended sidechain assistant whose parent is its own UUID also has no tip and passes. This leaves round 1 R1 incomplete. Require an acyclic graph and positive closure for every input-bearing component; permit fan-out leaves only within a proved closed turn. Add regressions combining the allowed-leaf profile with an open sidechain, plus self/multi-node cycles.
- **[P1] R2-2: Preserve call/result multiplicity and causal linkage** — `tools/resume_paused_claude_ledger.py:283-288`. `_calls` still reduces call and result IDs to sets. Two distinct call records sharing `c0` are satisfied by one result, and an earlier result satisfies a later call. For a concrete static counterexample, take `closed_turn(('PowerShell', {}), ('PowerShell', {}))`, make the second tool-use ID `c0`, remove `res1`, and parent the final reply to `call1`: both calls collapse to one set entry, the existing `c0` result closes them, and the graph/turn checks remain satisfied. The second call has no own result and could have started work whose outcome is not recorded. The same collision can misattribute a result/start to an exempt requestor operation. Match each call to its own validated later result in its graph/session context, rejecting duplicate IDs, contradictory linkage and uncertain ordering. Cover these cases independently of background-task ID reuse.
- **[P1] R2-3: Require a proved continuation for cross-file lifecycle completion** — `tools/resume_paused_claude_ledger.py:150-154 and 313-317`. `_ends` accepts any same-ID terminal from any file whose first timestamped record is `SessionStart:clear`; `_Event` carries no predecessor-session or process-generation relationship. A different Claude root in this checkout can clear its own session and produce such a file, which then closes an unrelated root's task or schedule with the same identifier. The regression called `test_terminal_in_an_unrelated_session_file_closes_nothing` exercises only a startup-marked unrelated file, leaving this case open. Equal timestamps also count as 'later' without another ordering proof. This leaves round 1 R3 incomplete. Carry validated scope/continuation and creation-order evidence through start/end matching; a clear marker alone or equal timestamps without causal evidence must stay pending. Preserve legitimate clear continuation with explicit linkage and test unrelated clear-marked files for both tasks and schedules.
- **[P1] R2-4: Require positive checkout evidence for the bound Claude file** — `tools/resume_paused_claude_ledger.py:116-120 and 246-251`. `_elsewhere` returns false when no valid cwd is recorded, and the bound-file path never separately requires one. Remove every `cwd` from `closed_turn()` (or replace them with non-string values): the session/version/marker/closure checks still pass and absence is PROVED. The existing foreign-checkout test covers only a definite mismatch. This leaves round 1 R4's bound-checkout requirement incomplete. Require positive, valid checkout linkage for the bound transcript before proving absence or applying the requestor exception; absent, malformed or contradictory binding must remain pending. Keep the conservative retain-in-scope behavior for nonbound files whose checkout cannot be excluded.
- **[P1] R2-5: Reject multiline and wrong-launcher requestor exemptions** — `tools/resume_paused_claude.py:54-57 and 139-156`. The invocation regex uses `\s+` between arguments, so `WAIT_ANSWER + '\nStart-Sleep 600'` matches as one requestor invocation although PowerShell executes two commands. Feeding that command through `wait_started(...), MARKED_SCOPE` excludes its unmatched background task. CRLF has the same issue. The executable pattern also accepts `not_review_exchange.bat` because it matches a filename suffix rather than the exact launcher name. This leaves round 1 R4's complete-command classification incomplete. Reject command-separating line breaks and require the exact validated launcher/invocation grammar before granting an exemption; keep uncertain commands in scope. Add newline, CRLF and prefixed-basename tests alongside the existing semicolon/pipe/wrapper tests.
- **[P2] R2-6: Reject unclassified nested message shapes instead of erasing them** — `tools/resume_paused_claude.py:177-188 and 216-245`. `_blocks` silently filters unknown message block types, while `_texts` treats unsupported content as no text. Append `record('user', message={'content': [{'type': 'future_input', 'text': 'later work'}]})` to `closed_turn()`: the known top-level user type passes classification; its unknown block disappears, so it has no input flag or UUID obligation and does not enter closure. The ledger reports PROVED from evidence whose new input shape is unclassified. Malformed non-string/non-list message content is similarly erased. Closed-world classification must validate nested message/content schemas (or retain an explicit unknown-shape fact) and keep unsupported evidence pending, including no-UUID records and schedule-only reads. Add those regressions; top-level record and tool-name allowlists alone do not establish complete classification.

Boundary-crossing work: None.

### Writer instructions for step 1 resume-paused (exchange 1) (round 2)

Address R2-1 through R2-6 in Claude parser/ledger code with focused adverse-case regressions. These are static counterexamples, not executed reproductions; verify them while implementing the corrections. Preserve conservative treatment of uncertain evidence, legitimate closed fan-out and explicitly linked clear continuations. Re-run the requestor-owned resolver-selected whole-suite validation, refresh Step 1 evidence and `a.commit`, and publish a new exact-index review request.

Do not add fabricated live profile evidence. Preserve Q05=A: missing live pins alone do not block Step 1 code completion. Q27=B and Q28=A continue to govern disclosed limitations and impractical live scenarios.

### Decision rationale for step 1 resume-paused (exchange 1) (round 2)

Disposition: changes-requested. Six readiness floors:

- Identity: pass; exact Step 1, round 2, occurrence 1 and request tree matched.
- Completeness: fail; six Claude proof gaps remain.
- Validation and coverage: incomplete; writer's reported run is green, but the missing adverse-case behavior is not established by measured coverage.
- Staged attribution: pass; only attributable Step 1 metadata was staged by the reviewer.
- Unresolved findings: fail; five P1 findings and one P2 finding remain.
- Commit plan: pass; independent checker is valid and ready with no diagnostics.

No substantive repair was performed. Generic repair prose is not literal Human guidance authorization. The false-proof cases must be resolved before commit-ready.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 3 by requestor - Step 1

- Recorded: 2026-11-16T10:10:01+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 3

### Code review evidence for step 1 resume-paused (round 3)

request_index_tree: 1fd2ce4985fe22fcbb698433c2f9a1853774a7e2
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tools/resume_paused_claude_graph.py
group 4 path: tools/resume_paused_claude_ledger.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_claude_graph.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 3)

Step 1 is implemented as a code deliverable under plan Q05=A, with the eight round 1 findings and the six round 2 findings repaired. It remains no support claim: the shipped registry pins nothing and the live validation checklist has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-16T10:07:41+01:00 on the staged index, proof speed, 6116 tests, no failure, no outlier, no exclusion.
- Static checks: the walk's `check.bat` passes its type, lint, complexity, dead-code, file-size, Markdown, ShellCheck and end-of-file steps.
- Coverage: 100% over `tools`, including the six new modules.
- Architecture: the record graph moved to its own module; the graph imports the parsing module and the ledger imports both; only the Win32 binding touches `ctypes`; no module writes a file, sends input or starts a process.
- Performance: single passes with set and map lookups; one depth-first numbering per transcript answers every ordering question, and each record is walked at most once to find its turn.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 3)

Round 2 findings and their repairs, each with regression cases in the named test package:

- R2-1 (`tools/resume_paused_claude_graph.py`, `tools/resume_paused_claude_ledger.py`; `test_resume_paused_claude_graph`, `test_resume_paused_claude_ledger`): the graph numbers the rooted records in one depth-first walk; a record on a parent loop, or below one, gets no number and is counted as `parent-cycle`. A final record that follows the pinned Stop summary closes the nearest input above it. Every input without such a final record is `input-turn-open`, and a pinned leaf whose nearest input is absent or not closed is `leaf-outside-closed-turn`. Cases with the leaf shape pinned: the answer's open sidechain pair, a leaf under no input, a self loop, a two-record loop, and a leaf below a loop. The earlier closure cases gained the new reason where an input lost its closing.
- R2-2 (same modules and packages): call and result identifiers keep their multiplicity. An identifier naming two calls is `tool-call-duplicate`, two results `tool-result-duplicate`, and a single pair whose result is not below its call in the parent chain is `tool-result-unlinked`. Cases: the answer's two calls sharing `c0` with one result, a result recorded above its call, one call answered twice, and a call and result on records without identifiers. The requestor exception now takes "after the marked input" from the same graph.
- R2-3 (`tools/resume_paused_claude_ledger.py`, `test_resume_paused_claude_ledger`): an end closes a start only when strictly later, and in another file only over a continuation pair supplied in `LedgerScope.continuations` into a file that begins with a clear marker. Pairs chain across successive clears. Cases: another root's clear-marked file, a reversed pair and a pair into a startup-marked file close nothing; a proved pair closes a task and a schedule; two proved clears in a row close the first file's start; an end at the start's own instant closes nothing.
- R2-4 (`tools/resume_paused_claude_ledger.py`, `tools/resume_paused_claude.py`; both test packages): the bound transcript needs at least one recorded `cwd` and none outside the checkout, else `bound-transcript-checkout-unproved`; all outside stays `bound-transcript-other-checkout`. A `cwd` that is not a string rejects the transcript. Another file without a `cwd` stays in scope. Cases: no `cwd`, one foreign `cwd` among valid ones, a numeric `cwd`, and that other file.
- R2-5 (`tools/resume_paused_claude.py`; both test packages): the invocation pattern separates arguments by spaces and tabs only, rejects a carriage return or line feed anywhere, quoted arguments included, and names `review_exchange.bat` alone or right after a directory separator. Cases: line feed and carriage-return line feed before a second command, a line break before the operation, a line break inside a quoted argument, quoted and bare `not_review_exchange.bat`, and through the ledger the same three commands keep their start in scope.
- R2-6 (`tools/resume_paused_claude.py`, `tools/resume_paused_claude_ledger.py`; both test packages): each record keeps the type of every message content block, without content. `ClaudeLedgerProfile.block_types` pins the allowed types and the ledger counts any other as `content-unclassified` in every transcript read. A message that is not an object, a content that is neither a string nor an array, and a block that is not an object with a string type reject the transcript. Cases: the answer's `future_input` record without an identifier in the bound file and in a schedule-only read before boot, and five malformed message shapes.

Other points:

- The record graph was split from the ledger by responsibility. Lines: parsing 384, graph 147, ledger 466, ledger tests 574; the ceiling is 650.
- Ordering questions are answered from one numbering per transcript, so a damaged file costs no more than a healthy one.
- No accepted duration exclusion exists.
- No live host validation ran in this round; no pane received input. The synthetic test profile pins `text`, `tool_use` and `tool_result` blocks; the real block types of a release belong to its pinning.
- The points disclosed in rounds 1 and 2 are unchanged: unconsolidated question blocks with confirmed user decisions, the transcript repairs made under the user's exceptions, the unchanged baseline file, and the single unexplained internal error of the first cold run.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 3)

Twenty-six staged paths in five `a.commit` groups; order, subjects and groups 1 to 3 are unchanged from round 2.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: the two v0.14.0 specification review transcripts.
3. `docs(resume-paused): record Step 1 decisions`: the design and the plan.
4. `feat(resume-paused): add host evidence adapters`: adds `tools/resume_paused_claude_graph.py` and the `tests/unit/tools/test_resume_paused_claude_graph` package (two files) to the round 2 members; its body now names six modules and the round 2 repairs.
5. `docs(resume-paused): record step 1 validation`: the validation plan, whose Step 1 rows the writer reassessed after the round 2 repairs; its body records that verdict.

Changed since round 2: `tools/resume_paused_claude.py`, `tools/resume_paused_claude_ledger.py`, the new graph module and its test package, the shared builders (one pinned set added to the synthetic profile), the two Claude test files, and the validation plan. The Windows, Codex and profile modules and their tests are unchanged. The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 3)

Writer response:

All six round 2 findings, R2-1 through R2-6, are accepted and repaired; there is no disagreement. Each static counterexample of the answer was reproduced as a test that fails without its repair. The reviewer's metadata repair is kept in substance: the writer then reassessed the Step 1 rows of the validation plan after the code repairs and updated the group 4 and group 5 bodies of `a.commit` to that state.

One repair needed a choice inside the finding's instruction, disclosed here for assessment. R2-3 asks for a proved continuation with explicit linkage. No recorded field links a cleared session file to its earlier file in the evidence gathered so far, so the ledger takes that linkage from its caller: `LedgerScope.continuations` holds the (earlier path, later path) pairs that independent pane evidence proved, and a pair counts only into a file that begins with a clear marker. The default is no pair, so today every cross-file end leaves its start pending. The evidence source for such a pair is a new open row of the live validation checklist. This adds no evidence channel and changes no settled decision; Step 7 would supply the pairs.

### Reviewer focus for step 1 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-3 -->

## Round 3 by reviewer - Step 1

- Recorded: 2026-11-16T10:21:56+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 3)

Baseline index tree: 1fd2ce4985fe22fcbb698433c2f9a1853774a7e2

Assessed index tree: c435930b9a15dfadaf2eaa81b8c19f36caf9d26a

### Implementation check for step 1 resume-paused (exchange 1) (round 3)

Result:

No. Step 1 has NOT been fully implemented.

Round 3 finds the three concrete ledger defects below. The six round 2 repair areas are present, but R3-1 and R3-2 still allow false positive absence and R3-3 exceeds the planned computation bound. Ports and adapters remain separated, the new modules remain below the 650-line ceiling, and existing reporting is unaffected. Plan Q05=A explicitly accepts code work with an empty supported-profile registry; the deferred live matrix is not itself a rejection reason.

Validation plan effects:

Only Step 1 rows of `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` changed: exact No sentence, reviewer rationale, Missing work for Step 1 immediately after implemented work, performance and static test assessment. Other steps, the document-level status and the live checklist are unchanged. No umbrella applies. The group 5 body of ignored `a.commit` now accurately describes this verdict.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 3)

The request records the writer's successful `ghog day --full=speed --whole-suite` at 2026-11-16T10:07:41+01:00: 6116 tests, 100% of the configured tools source scope, no failures, duration outliers or accepted exclusions. This is writer evidence, not a reviewer measurement. Reviewer execution of check, affected, day, full and coverage: none; the findings are static counterexamples using existing fixtures. The reported statement coverage does not cover the missing invariants.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 3)

`ghog day --full=speed --whole-suite`, source `project`. The built-in default in `tools/code_review_validation.py` is `ghog day --full=speed`; the exact requirement declares `Test group: whole suite`, completing the selector. No project `.review-validation` declaration exists; no plan/request additions are declared. The returned scope capture is whole, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 3)

None found: the request's single project command agrees with the current resolver default, absent project override and requirement's whole-suite selector. The reviewer did not execute the resolved requestor validation set.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 3)

The request-time index and captured baseline match: `1fd2ce4985fe22fcbb698433c2f9a1853774a7e2`. The assessed index is `c435930b9a15dfadaf2eaa81b8c19f36caf9d26a`. Evidence comparison over the same 26 staged paths reports only the validation plan as changed; inspection confines that difference to Step 1 review metadata. The raw comparison's `acceptable: false` flags this tracked change, which is expressly permitted in reviewer mode. Attribution succeeded against the saved pre-edit blob; only that patch was applied to the index. Its CRLF line endings were preserved. No implementation or test edit, validation side effect, added staged path, or umbrella change occurred. The separately attributed ignored `a.commit` edit updates group 5 wording only.

### Repair inventory for step 1 resume-paused (exchange 1) (round 3)

Repairs made:

- Review metadata only: Step 1 validation verdict and missing-work rows; no substantive repair.
- Review metadata only: ignored `a.commit` group 5 body aligned to the No verdict.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 3)

Independent `commit-plan-check.bat --format json` returned exit 0, `state: valid`, `ready: true`, and no diagnostics both before assessment and after the metadata update. All 26 staged paths occur exactly in the five ordered groups below. The order runs from independent documentation repairs through decisions and implementation to validation; scope and conventional subjects are accurate. Mechanical readiness does not override the findings or authorize a commit.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: `docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md`, `docs/v0.14.0/review.plan.v0.14.0.resume-paused.md`.
3. `docs(resume-paused): record Step 1 decisions`: `docs/v0.14.0/design.v0.14.0.resume-paused.md`, `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
4. `feat(resume-paused): add host evidence adapters`: `tools/resume_paused_profiles.py`, `tools/resume_paused_windows.py`, `tools/resume_paused_codex.py`, `tools/resume_paused_claude.py`, `tools/resume_paused_claude_graph.py`, `tools/resume_paused_claude_ledger.py`, `tests/unit/tools/resume_paused_test_support.py`, `tests/unit/tools/test_resume_paused_profiles/__init__.py`, `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`, `tests/unit/tools/test_resume_paused_windows/__init__.py`, `tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py`, `tests/unit/tools/test_resume_paused_codex/__init__.py`, `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`, `tests/unit/tools/test_resume_paused_claude/__init__.py`, `tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py`, `tests/unit/tools/test_resume_paused_claude_graph/__init__.py`, `tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py`, `tests/unit/tools/test_resume_paused_claude_ledger/__init__.py`, `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py`, `docs/v0.14.0/resume-paused.profile-evidence.md`.
5. `docs(resume-paused): record step 1 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 3)

Unresolved findings:

- [P1] R3-1: Exclude requestor start records, not every start sharing their task id (`tools/resume_paused_claude_ledger.py:363-391`). `_requestor_starts` returns task ids and `_lifecycle` drops every matching id before duplicate detection. Static counterexample using the existing builders: `closed_turn(("PowerShell", {"backgroundTaskId": "wait1"}), ("PowerShell", {"backgroundTaskId": "wait1"}, WAIT_ANSWER), text=MARKED)` under `MARKED_SCOPE` has one ordinary unmatched task and one recognized requestor start; both disappear and absence is PROVED. An earlier start sharing the later excluded id is lost too. Exclude only the exact qualifying start record and its own attributable lifecycle records; detect ambiguous reuse before exclusion. Add regressions for unrelated post-marker and earlier starts sharing an excluded id, with and without terminal records. Both must remain pending.
- [P1] R3-2: Require closure ordering for pinned sidechain leaves (`tools/resume_paused_claude_ledger.py:402-453`). `_closings` retains only the input uuid; `_tips` accepts any pinned leaf under that input, while `_closure` ignores sidechains when checking the last record. Static counterexample: `decide({BOUND: [*closed_turn(), side("late", "in", 50)]}, leaf_shapes=LEAVES)` returns PROVED although the final record is at second 41 and the sidechain reply is recorded later at second 50. Sharing an input with an earlier final record does not close later recorded work. Retain the closing record and prove the profile's closing-record-last ordering for every leaf, or remain pending when that order cannot be established. Add late-sibling and late-descendant sidechain regressions while retaining the legitimate pre-final fan-out case.
- [P2] R3-3: Remove the Cartesian transitive-closure expansion (`tools/resume_paused_claude_ledger.py:172-180,244`). `_linked` materializes every reachable file pair and scans the entire pair set against itself until stable. A chain of 101 files creates 5,050 pairs and the final no-change pass alone evaluates 25,502,500 pair combinations; 1,000 files produce approximately 2.5e11 combinations. This runs even with no task or schedule events. It violates the plan's evidence-proportional bound and the validation plan's no-quadratic-work claim. Replace it with indexed continuation/reachability evaluation that avoids the all-pairs product, handles ambiguous/cyclic linkage conservatively, and accounts for its real bound. Add a deterministic structural or operation-count regression over a long continuation chain rather than a timing threshold.

Boundary-crossing work: None.

### Writer instructions for step 1 resume-paused (exchange 1) (round 3)

Repair R3-1, R3-2 and R3-3 in the ledger and its focused unit tests, keep the live-profile policy unchanged, reassess Step 1 and update the commit-plan body to the resulting state. Run the writer-owned mandatory validation before publishing another review request. The reviewer made no implementation/test repair and no literal Human guidance block was supplied.

### Decision rationale for step 1 resume-paused (exchange 1) (round 3)

Changes requested. Six readiness-floor results:

- Identity: PASS; exact code/v0.14.0/resume-paused, Step 1, round 3, occurrence 1, matching request-time baseline.
- Completeness: FAIL; R3-1 and R3-2 permit false positive absence, and R3-3 violates the complexity bound.
- Validation and coverage: FAIL; the writer's green evidence is retained, but static assessment finds missing regression cases for all three findings. No new runtime result or coverage percentage is claimed.
- Staged attribution: PASS; only attributable Step 1 review metadata was staged, with the ignored commit-plan wording amended separately.
- Unresolved findings: FAIL; R3-1 through R3-3 remain for the writer.
- Commit plan: PASS mechanically and semantically for the present staged state; valid/ready, five groups, 26 paths, no diagnostics.

The disposition is advisory and grants no commit authority.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-3 -->

## Round 4 by requestor - Step 1

- Recorded: 2026-11-17T08:55:15+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 4)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 4

### Code review evidence for step 1 resume-paused (round 4)

request_index_tree: e15245fbe009f58dba133952c67a5cfd5bd9f7da
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tools/resume_paused_claude_graph.py
group 4 path: tools/resume_paused_claude_ledger.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_claude_graph.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 4)

Step 1 is implemented as a code deliverable under plan Q05=A, with the eight round 1 findings, the six round 2 findings and the three round 3 findings repaired. It remains no support claim: the shipped registry pins nothing and the live validation checklist has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-17T08:51:53+01:00 on the staged index, proof speed, 6130 tests, no failure, no outlier, no exclusion.
- Static checks: the walk's `check.bat` passes its type, lint, complexity, dead-code, file-size, Markdown, ShellCheck and end-of-file steps.
- Coverage: 100% over `tools`, including the six new modules.
- Architecture: the graph imports the parsing module and the ledger imports both; only the Win32 binding touches `ctypes`; no module writes a file, sends input or starts a process.
- Performance: single passes with set and map lookups; one depth-first numbering per transcript answers every ordering question, each record is walked at most once to find its turn, and continuation chains are numbered in time and memory linear in the number of proved pairs.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 4)

Round 3 findings and their repairs, each with regression cases in `test_resume_paused_claude_ledger` (second file, `test_resume_paused_claude_ledger_ordering_tdd.py`):

- R3-1 (`tools/resume_paused_claude_ledger.py`): the requestor exception returns the identifiers of the qualifying start records, never task ids. Each task start enters the tally; the covered record is marked exempt. An exempt start is never counted open, yet it counts as a use of its task id, so any other start sharing that id is open and the id is reported as reused, whatever terminal record exists. Cases: the answer's two post-marker starts sharing `wait1`, and an earlier ordinary start sharing the id of a later requestor wait, each with and without a terminal record; all four stay pending with `background-start-unmatched` and `task-id-reused`.
- R3-2 (same module): the closing check keeps, for each closed input, the instant of its earliest final record. A pinned leaf under that input must carry an instant strictly before it, else `leaf-after-closing`. Cases: the answer's late sibling under the input, a late leaf under the reply, a late descendant of an early sidechain record, a leaf at the final record's own instant, a leaf without an instant, and a final record without an instant; the leaf recorded before the final record still proves absence.
- R3-3 (same module): `continuation_places` replaces the reachable-pair expansion. It keeps a pair only when its earlier file has one proved successor and its later file one proved predecessor, then walks each chain once from its head and gives every file its head and position. "File B continues file A" is two map lookups. Cases: a chain of one thousand clears yields exactly 1001 places with the expected head and positions; two successors, two predecessors, a two-file loop and a self link place nothing; through the ledger, a start file with two proved successors keeps its start open. The earlier proved-chain cases are unchanged.

Two static-check repairs followed, with no behavior change: the long-chain case builds its pairs with `itertools.pairwise` (ruff RUF007), and the requestor call set moved from `ClaudeLedger._requestor_starts` into the module helper `_requestor_calls`, keeping that method within the radon grade B budget.

Other points:

- Lines: ledger 536, first ledger test file 574, second 129; the ceiling is 650.
- The continuation index costs time and memory linear in the number of proved pairs; no pair product is formed.
- No accepted duration exclusion exists.
- No live host validation ran in this round; no pane received input.
- The points disclosed in earlier rounds are unchanged: unconsolidated question blocks with confirmed user decisions, the transcript repairs made under the user's exceptions, the unchanged baseline file, the single unexplained internal error of the first cold run, and the caller-supplied continuation pairs of round 3.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 4)

Twenty-seven staged paths in five `a.commit` groups; order, subjects and groups 1 to 3 are unchanged from round 3.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: the two v0.14.0 specification review transcripts.
3. `docs(resume-paused): record Step 1 decisions`: the design and the plan.
4. `feat(resume-paused): add host evidence adapters`: adds `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py` to the round 3 members; its body now names the repairs of rounds 1 to 3.
5. `docs(resume-paused): record step 1 validation`: the validation plan, whose Step 1 rows the writer reassessed after the round 3 repairs; its body records that verdict.

Changed since round 3: `tools/resume_paused_claude_ledger.py`, the new second ledger test file, and the validation plan. Every other staged path is unchanged. The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 4)

Writer response:

All three round 3 findings, R3-1 through R3-3, are accepted and repaired; there is no disagreement. Each static counterexample of the answer was reproduced as a test that fails without its repair. The reviewer's metadata repair is kept in substance: the writer then reassessed the Step 1 rows of the validation plan after the code repairs and updated the group 4 and group 5 bodies of `a.commit` to that state.

Two repairs made a choice inside the finding's instruction, disclosed here for assessment. For R3-2, the order between a pinned leaf and its turn's final record comes from their recorded instants, since two branches under one input share no parent order: the leaf must be strictly earlier, and an equal or unknown instant is pending. This keeps design Q21=A's disclosed clock limit and adds no source. For R3-3, a continuation counts only along a single chain: a file with two proved successors or two proved predecessors, or on a loop, is placed nowhere, so such a link closes nothing.

### Reviewer focus for step 1 resume-paused (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-4 -->

## Round 4 by reviewer - Step 1

- Recorded: 2026-11-17T09:08:07+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 4)

Baseline index tree: e15245fbe009f58dba133952c67a5cfd5bd9f7da

Assessed index tree: e15245fbe009f58dba133952c67a5cfd5bd9f7da

### Implementation check for step 1 resume-paused (exchange 1) (round 4)

Result:

No. Step 1 has NOT been fully implemented.

The three round 3 repairs are present. The Step 1 code deliverable under plan Q05=A still has the two fail-closed defects below. Empty supported-profile registration and deferred live validation remain authorized; they are not findings.

Readiness floor: identity passes; completeness fails R4-1/R4-2; writer validation evidence is green but behavioral regressions are missing; original staged scope is attributable, with the reviewer validation patch proved attributable but unstaged; unresolved findings fail; commit-plan mechanics pass and its validation narrative was corrected. No commit-ready recommendation.

Validation plan effects:

Only Step 1 rows in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` changed: exact No status, round 4 explanation, two missing-work bullets, and static coverage qualification. The umbrella is not applicable. Implementation and tests were not edited.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 4)

Request and independently captured index both equal `e15245fbe009f58dba133952c67a5cfd5bd9f7da`. The request reports the writer's `ghog day --full=speed --whole-suite` exit 0 at 2026-11-17T08:51:53+01:00: 6130 tests, 100% tools coverage, no failure, outlier or exclusion. These are writer results, not reviewer reruns. Neither permitted optional reviewer test command was run; findings are static counterexamples traced through the existing fixture builders and implementation.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 4)

The resolved command is `ghog day --full=speed --whole-suite`, source `project`. The current resolver uses the built-in speed default because `.review-validation` is absent, and the exact requirement declares `Test group: whole suite`. No plan/request additions are embedded. Bound scope fingerprint: `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 4)

No drift found by static comparison of `tools/code_review_validation.py`, the requirement selector and the request payload. The coverage source is `tools` in `pyproject.toml`; all six new implementation modules are measured. Their matching unit-test packages exercise the modules, but the reported percentage does not establish the missing behaviors in R4-1/R4-2.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 4)

Baseline and final captured index: `e15245fbe009f58dba133952c67a5cfd5bd9f7da`. Validation-state comparison reports only the Step 1 validation-plan path changed; no other tracked or untracked path differs in the captured set. The generic comparison reports acceptable=false for that tracked metadata edit; manual boundary inspection confines it to the authorized Step 1 rows. Umbrella comparison: applicable=false, changed=false. Patch attribution reports attributable=true.

The required evidence launcher only computes attribution; its CLI exposes no staging operation. Its source confirms that `attribute-reviewer-patch` does not stage. In accordance with the instruction forbidding substitute Git-index mutations, the reviewer left this attributable metadata patch unstaged and explicitly hands its staging back to the writer. The ignored `a.commit` body was corrected to describe the No verdict; membership, order and subjects are unchanged.

### Repair inventory for step 1 resume-paused (exchange 1) (round 4)

Repairs made:

- Polishing-only review metadata: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, attributable Step 1 verdict/missing-work/coverage patch, left unstaged because the mandated launcher has no staging operation.
- Polishing-only review metadata: ignored `a.commit`, group 5 body changed from Yes to No to match the current assessment; no membership, ordering or subject changes.

Paths staged:

- No reviewer-authored path was newly staged; the original 27 staged paths and five groups remain unchanged.

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 4)

The independent checker passed before assessment and again after metadata edits: state=valid, ready=true, diagnostics=[]. The retained final checker JSON contains all 27 staged paths and five ordered groups: pause wording; authorized specification-transcript lint repairs; confirmed Step 1 decisions; host evidence adapters and tests; Step 1 validation. These groups match the request and scope. The group 5 body now describes the No verdict. Mechanical readiness does not remove R4-1/R4-2 or stage the metadata patch.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 4)

Unresolved findings:

- R4-1 (high): Generation completeness is enforced only for the bound transcript (`tools/resume_paused_claude_ledger.py:407-432`). With BOUND holding a normal `closed_turn()`, add a recent in-checkout nonbound `closed_turn()` and change its startup hook to `SessionStart:resume`. The graph, inputs, calls and closure remain valid; `_bound` is skipped, so neither `_marker` nor `_restarts` can block it and the ledger returns `Absence.PROVED`. Removing its startup record and rooting its input at null also passes. Plan Step 1 requires complete generation ranges and marker coverage for every contributing writer, with detected missing history pending. Apply a completeness check to every in-scope transcript, without treating the bound process identity as the identity of other writers. Keep the narrow requestor marker/continuation exception scoped to proved evidence. Add nonbound missing/resume marker and restart regressions plus a complete positive case.
- R4-2 (high): Malformed lifecycle fields are erased (`tools/resume_paused_claude.py:259-290`, `tools/resume_paused_claude_ledger.py:395-405`). Existing fixture constructions `closed_turn(("PowerShell", {"backgroundTaskId": 7}))` and `closed_turn(("CronCreate", {"id": 7}))`, each as the bound transcript, pass call/result/turn checks. `as_text` maps the supplied identifier to None; no task or schedule start enters the tally, so absence is proved. Empty identifiers and malformed result containers have the same information-loss risk. Reject malformed supplied lifecycle fields and require recognized schedule-create result shapes; distinguish validated non-start/error outcomes explicitly. Add parser and end-to-end ledger regressions showing malformed or unknown evidence is pending, never absence. This follows the plan's closed-world and partially recorded work requirements.

Boundary-crossing work:

- No implementation or test repairs were performed. The request has no literal `Human guidance:` block authorizing them.
- No live host profile was enabled, no pane received input, and no other step or umbrella row was changed.

### Writer instructions for step 1 resume-paused (exchange 1) (round 4)

Repair R4-1 and R4-2 within the Step 1 parser/ledger and add the specified behavioral regressions. Reassess the Step 1 validation rows, stage the attributable reviewer metadata together with the resulting writer assessment, and keep `a.commit` accurate. Run the writer-owned resolved validation gate on the repaired state and publish a new review request. Preserve the empty supported registry and the existing live-validation limits. No commit is authorized by this answer.

### Decision rationale for step 1 resume-paused (exchange 1) (round 4)

Changes requested: two static counterexamples still allow absence to be proved from incomplete or malformed evidence. R3-1 through R3-3 are accepted as repaired. This round changed review metadata only; no substantive reviewer repair occurred. The writer owns implementation repair, validation, staging and the next request.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 4)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-4 -->

## Round 5 by requestor - Step 1

- Recorded: 2026-11-17T09:40:25+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 5)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 5

### Code review evidence for step 1 resume-paused (round 5)

request_index_tree: a41ca65ed705e97056b1dbf914938bf2c546ce63
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tools/resume_paused_claude_graph.py
group 4 path: tools/resume_paused_claude_ledger.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_claude_graph.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 5)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 5)

Step 1 is implemented as a code deliverable under plan Q05=A, with the eight round 1 findings, the six round 2 findings, the three round 3 findings and the two round 4 findings repaired. It remains no support claim: the shipped registry pins nothing and the live validation checklist has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-17T09:37:58+01:00 on the staged index, proof speed, 6160 tests, no failure, no outlier, no exclusion. After the walk, only two inline lines of the Step 1 validation rows changed (the ledger's line count and one performance sentence); no Python source changed, and that file's spelling check is clean.
- Static checks: the walk's `check.bat` passes its type, lint, complexity, dead-code, file-size, Markdown, ShellCheck and end-of-file steps.
- Coverage: 100% over `tools`, including the six new modules.
- Architecture: the graph imports the parsing module and the ledger imports both; only the Win32 binding touches `ctypes`; no module writes a file, sends input or starts a process.
- Performance: single passes with set and map lookups; one depth-first numbering per transcript answers every ordering question, each record is walked at most once to find its turn, continuation chains are numbered in time and memory linear in the number of proved pairs, and the files a continuation leads into are indexed once per decision.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 5)

Round 4 findings and their repairs. The ledger regressions sit in a third file of `test_resume_paused_claude_ledger`, `test_resume_paused_claude_ledger_evidence_tdd.py`; the parser regressions extend `test_resume_paused_claude_tdd.py`.

- R4-1 (`tools/resume_paused_claude_ledger.py`): the generation check now runs for every transcript read since boot, not only the bound one. `_generation` requires the first timestamped record to be an accepted `hook_success` marker and counts every later SessionStart other than a compaction. The bound transcript keeps the scope's markers and the check against the pane's process creation. Any other transcript is checked against `_writer_markers` with no process: the startup marker, plus the clear marker only when `LedgerScope.continuations` proves the file is the later end of a continuation. Cases: the answer's resume-marked other writer and its writer with no marker and an input without a parent, an other writer opened by an unproved clear, and later resume and startup restarts are pending; a startup-opened writer, a compacted one and one whose marker predates the bound process prove absence; a clear-opened writer proves only with its continuation pair.
- R4-2 (`tools/resume_paused_claude.py`, then the ledger): a supplied `backgroundTaskId`, `taskId`, queue `taskId` or `status`, or tool result `is_error`, of the wrong JSON type or empty, rejects the transcript (`record-invalid`). Each result record keeps two new facts: `plain_result`, when its `toolUseResult` is absent or not an object, and `failed`, when every result block is flagged `is_error`. The ledger counts `result-unclassified` for a plain result that is neither failed nor answering only tools listed in the new profile field `plain_result_tools` (default empty). A schedule creation result that is not failed and has no nonempty string `id` counts `schedule-result-unrecognized`. A failed result creates and deletes no schedule. Cases: the answer's `{"backgroundTaskId": 7}` and `{"id": 7}`, plus empty and list task ids, empty, null and missing schedule ids, string, list, number and absent containers; a failed plain result and a validated plain tool prove absence, a plain tool listed for another tool does not; a failed creation leaves nothing to resolve and a failed deletion resolves nothing.

Each of the 27 new cases fails on the pre-repair modules: they were run once against the index versions of the two modules before the repaired files were restored byte for byte. One existing case changed: the unlinked call and result case in the first ledger test file gives its result an object container, so it keeps its single linkage reason under the new container rule.

Other points:

- Lines: parser 451, ledger 611, first ledger test file 578, second 129, third 138, parser test file 293. The ledger is past the plan's advisory 550 mark of the parsing module it was split from and below the 650 ceiling.
- The added checks are single passes over records already parsed. The files a proved continuation leads into are indexed once per decision, so choosing a writer's accepted markers is one set lookup per transcript.
- No accepted duration exclusion exists.
- No live host validation ran in this round; no pane received input.
- The points disclosed in earlier rounds are unchanged: unconsolidated question blocks with confirmed user decisions, the transcript repairs made under the user's exceptions, the unchanged baseline file, the single unexplained internal error of the first cold run, and the caller-supplied continuation pairs of round 3.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 5)

Twenty-eight staged paths in five `a.commit` groups; order, subjects and groups 1 to 3 are unchanged from round 4.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: the two v0.14.0 specification review transcripts.
3. `docs(resume-paused): record Step 1 decisions`: the design and the plan.
4. `feat(resume-paused): add host evidence adapters`: adds `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py` to the round 4 members; its body now names the parser's lifecycle-field rejection, the ledger's generation and result checks, and the repairs of rounds 1 to 4.
5. `docs(resume-paused): record step 1 validation`: the validation plan, whose Step 1 rows the writer reassessed after the round 4 repairs; its body records that verdict.

Changed since round 4: `tools/resume_paused_claude.py`, `tools/resume_paused_claude_ledger.py`, the parser test file, the first ledger test file, the new third ledger test file, and the validation plan. Every other staged path is unchanged. The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 5)

Writer response:

Both round 4 findings, R4-1 and R4-2, are accepted and repaired; there is no disagreement. Each static counterexample of the answer was reproduced as a test that fails without its repair. The reviewer's metadata repair is kept in substance: the reviewer left it unstaged, and the writer then reassessed the Step 1 rows of the validation plan after the code repairs, staged that result, and updated the group 4 and group 5 bodies of `a.commit` to that state. The "Missing work for Step 1" section the reviewer added is replaced by the round 4 repairs entry, and a new open live-checklist row covers the tool result containers.

Several repairs made a choice inside the finding's instruction, disclosed here for assessment:

- R4-1: another writer's transcript opened by a clear marker counts as complete only when the caller proved it continues an earlier file; without that pair it is pending. This keeps the requestor's acceptance of a clear, design Q23=A, confined to the bound file.
- R4-2: a recorded error is read from the tool result block's `is_error` flag. A failed result creates and deletes no schedule, yet a task id it carries still counts as a start. A JSON `null` lifecycle field reads as absent; a wrong type or an empty string rejects. A result's `id` stays lenient for other tools, so an unrelated tool's numeric `id` does not reject the transcript; only a schedule creation requires it. An absent `toolUseResult` on a result record counts as a plain container, like a string, list or number. Validated plain tools come from the new profile field `plain_result_tools`, empty by default, so no plain result is classified until validation lists it.

### Reviewer focus for step 1 resume-paused (round 5)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-5 -->

## Round 5 by reviewer - Step 1

- Recorded: 2026-11-17T09:50:37+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 5)

Baseline index tree: a41ca65ed705e97056b1dbf914938bf2c546ce63

Assessed index tree: a41ca65ed705e97056b1dbf914938bf2c546ce63

### Implementation check for step 1 resume-paused (exchange 1) (round 5)

Result:

No. Step 1 has NOT been fully implemented.

Plan Q05=A permits the code deliverable with an empty supported registry. The round 4 malformed-result counterexamples are repaired, and the generation check now covers nonbound writers. R5-1 remains: an absent known predecessor can be silently excluded while its cleared successor passes generation completeness. This is a code defect under the existing detected-history-loss rule, not a demand to finish the deferred live matrix.

Architecture and file boundaries remain appropriate; no new performance regression was found in the round 5 changes. The static coverage review confirms all six modules are within the tools coverage source, but the missing-predecessor behavior lacks a regression. Existing features have no new callers of these adapters.

Validation plan effects:

Updated only Step 1 in docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md: exact No verdict, missing-work bullets immediately after What was implemented, and behavioral-test gap. Other steps and the document-level status are unchanged. No umbrella applies. The metadata patch is attributable but remains unstaged: the mandated evidence launcher reports attribution and exposes no staging operation; no substitute index command was used. The writer must stage/reassess it with the repair.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 5)

No reviewer test, check or coverage command ran in round 5. Static control-flow and fixture assessment suffice for R5-1. The request reports the writer's ghog day --full=speed --whole-suite exit 0 at 2026-11-17T09:37:58+01:00: 6160 tests, 100% tools coverage, no failures, outliers or exclusions. It discloses two subsequent validation-Markdown line edits and no Python changes. Coverage is writer evidence, not a reviewer measurement.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 5)

ghog day --full=speed --whole-suite; source: project. The built-in project speed default is completed with the requirement's explicit whole-suite scope. Bound scope fingerprint: 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6. No plan or request additions are declared.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 5)

None. The current .review-validation path is absent; the canonical resolver default remains ghog day --full=speed, and the requirement still declares Test group: whole suite. This agrees with the request's project-sourced command and bound scope.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 5)

Request, retained baseline and assessed index trees agree: a41ca65ed705e97056b1dbf914938bf2c546ce63. The before/after comparison across all 28 staged paths reports only the intentionally edited Step 1 validation plan; no untracked or other tracked side effect. Its generic acceptable=false denotes that tracked metadata difference, inspected and confined to the permitted Step 1 rows. Umbrella comparison: applicable=false, changed=false. Attribution: attributable=true. Index unchanged; reviewer metadata left unstaged as disclosed.

### Repair inventory for step 1 resume-paused (exchange 1) (round 5)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md: review metadata only; polishing-only classification, no code or test repair; attributable and left unstaged.
- a.commit: review metadata only; group 5 body distinguishes the staged writer Yes from the reviewer's unstaged No and pending writer reassessment. Membership, ordering and subjects unchanged.

Paths staged:

- docs/v0.14.0/design.v0.14.0.resume-paused.md
- docs/v0.14.0/plan.v0.14.0.resume-paused.md
- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
- docs/v0.14.0/resume-paused.profile-evidence.md
- docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
- docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
- instructions/pause-session.md
- tests/unit/tools/resume_paused_test_support.py
- `tests/unit/tools/test_resume_paused_claude/__init__.py`
- tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
- `tests/unit/tools/test_resume_paused_claude_graph/__init__.py`
- tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
- `tests/unit/tools/test_resume_paused_claude_ledger/__init__.py`
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
- `tests/unit/tools/test_resume_paused_codex/__init__.py`
- tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
- `tests/unit/tools/test_resume_paused_profiles/__init__.py`
- tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
- `tests/unit/tools/test_resume_paused_windows/__init__.py`
- tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
- tools/resume_paused_claude.py
- tools/resume_paused_claude_graph.py
- tools/resume_paused_claude_ledger.py
- tools/resume_paused_codex.py
- tools/resume_paused_profiles.py
- tools/resume_paused_windows.py

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 5)

The independent checker on the received state exited 0: state=valid, ready=true, diagnostics=[]. It records 28 staged paths in five ordered groups: docs(pause): restore the pinned choice wording; docs(resume-paused): repair review transcript lint; docs(resume-paused): record Step 1 decisions; feat(resume-paused): add host evidence adapters; docs(resume-paused): record step 1 validation. Scope, ordering and conventional subjects remain accurate. Only the group 5 narrative was updated to disclose the reviewer No and unstaged metadata; the writer must refresh it after reassessment. Mechanical validity is not implementation completeness or commit authorization.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 5)

Unresolved findings:

- R5-1 (high), tools/resume_paused_claude_ledger.py:333, 383, 502: a continuation destination is accepted without requiring its known predecessor to be present. Static counterexample using the existing evidence test fixtures: linked = replace(SCOPE, continuations=frozenset({(OLD, OTHER)})); decide({BOUND: closed_turn(), OTHER: CLEARED}, scope=linked). The current control flow returns PROVED with no reasons: only the bound path is checked for presence, OLD is never read, and OTHER receives the allowed clear marker from the raw destination set. The terminal in CLEARED does not prove that OLD contained no other unfinished work. This is detectable missing history because the supplied pair names OLD; it is outside Q26's allowance for roots whose loss leaves no evidence. Require complete relevant predecessor history through the continuation chain before using a clear marker to prove a complete generation, and add the missing-predecessor and missing-ancestor regressions alongside the complete-history control.

Boundary-crossing work:

- None. No implementation or test repair was made. The request contains generic repair wording but no literal Human guidance: block authorizing such repairs. Deferred live validation and the empty registry remain accepted under Q05=A.

### Writer instructions for step 1 resume-paused (exchange 1) (round 5)

Repair R5-1 in the ledger and add regression cases for an absent known predecessor, a missing ancestor through successive clears, and unreadable/incomplete predecessor history, preserving a complete-history positive control and the boot/schedule scope rules. Keep reason counts explicit. Reassess and stage the Step 1 validation metadata, refresh a.commit, run the writer-owned required validation, and publish a new exact request. No commit is authorized.

### Decision rationale for step 1 resume-paused (exchange 1) (round 5)

changes-requested. Six readiness results: identity passes; implementation completeness fails R5-1; reported validation and measured coverage pass but behavioral coverage misses R5-1; staged implementation attribution passes while the attributable metadata update remains unstaged; unresolved-findings floor fails R5-1; a.commit mechanical grouping and subjects pass. R4-2 is closed for its stated counterexamples; the R4-1 completeness obligation remains open through R5-1. No substantive reviewer repair occurred.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 5)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-5 -->

## Round 6 by requestor - Step 1

- Recorded: 2026-11-17T10:01:57+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (round 6)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 1
Review round: 6

### Code review evidence for step 1 resume-paused (round 6)

request_index_tree: 11a6bbb0bee2efeec57b6e581496efede465fe5c
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(pause): restore the pinned choice wording
group 1 path: instructions/pause-session.md
group 2: docs(resume-paused): repair review transcript lint
group 2 path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
group 2 path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
group 3: docs(resume-paused): record Step 1 decisions
group 3 path: docs/v0.14.0/design.v0.14.0.resume-paused.md
group 3 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 4: feat(resume-paused): add host evidence adapters
group 4 path: tools/resume_paused_profiles.py
group 4 path: tools/resume_paused_windows.py
group 4 path: tools/resume_paused_codex.py
group 4 path: tools/resume_paused_claude.py
group 4 path: tools/resume_paused_claude_graph.py
group 4 path: tools/resume_paused_claude_ledger.py
group 4 path: tests/unit/tools/resume_paused_test_support.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_windows/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_codex/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
group 4 path: docs/v0.14.0/resume-paused.profile-evidence.md
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/design.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.profile-evidence.md
staged path: docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
staged path: instructions/pause-session.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/__init__.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/__init__.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tests/unit/tools/test_resume_paused_windows/__init__.py
staged path: tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
staged path: tools/resume_paused_claude.py
staged path: tools/resume_paused_claude_graph.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_codex.py
staged path: tools/resume_paused_profiles.py
staged path: tools/resume_paused_windows.py
```

### Validation scope for step 1 resume-paused (round 6)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (round 6)

Step 1 is implemented as a code deliverable under plan Q05=A, with the eight round 1 findings, the six round 2 findings, the three round 3 findings, the two round 4 findings and the round 5 finding repaired. It remains no support claim: the shipped registry pins nothing and the live validation checklist has every row open.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-17T10:01:00+01:00 on the staged index, proof speed, 6166 tests, no failure, no outlier, no exclusion. Nothing changed after the walk.
- Static checks: the walk's `check.bat` passes its type, lint, complexity, dead-code, file-size, Markdown, ShellCheck and end-of-file steps.
- Coverage: 100% over `tools`, including the six new modules.
- Architecture: the graph imports the parsing module and the ledger imports both; only the Win32 binding touches `ctypes`; no module writes a file, sends input or starts a process. The ledger is at 642 of 650 lines.
- Performance: single passes with set and map lookups; one depth-first numbering per transcript answers every ordering question, each record is walked at most once to find its turn, continuation chains are numbered in time and memory linear in the number of proved pairs, and the continued files and the enumerated paths are indexed once per decision.
- Feature integrity: no existing module changes behavior; the new modules have no caller yet.

### Implementation report for step 1 resume-paused (round 6)

Round 5 finding and its repair, with regression cases in the third ledger test file, `test_resume_paused_claude_ledger_evidence_tdd.py`:

- R5-1 (`tools/resume_paused_claude_ledger.py`): a proved continuation pair whose later file is listed now needs its earlier file in the scope. The tally keeps the enumerated paths (`listed`) and the read transcripts the checkout rule excluded (`outside`); `_missing_predecessors` counts `continuation-predecessor-missing` once per pair whose earlier file is unlisted or excluded. Each link of a chain is checked, so a missing ancestor behind successive clears is counted too. An unreadable or incomplete earlier file is already pending under `read-failed` or `transcript-incomplete` and is not counted twice; an earlier file older than the boot boundary stays under the boot rule. Cases: the answer's counterexample (`LINKED` with `OLD` absent) and a two-link chain with its first file absent are pending; the same chain with every file present proves absence; an unreadable, an incomplete and another checkout's earlier file are pending with their explicit reason; a pre-boot earlier file holding an unmatched start proves absence under the boot rule.

The three missing-history cases fail on the pre-repair ledger: they were run once against the index version of the module before the repaired file was restored byte for byte. The unreadable, incomplete and pre-boot cases pass on both versions; they pin the existing behavior the repair keeps.

Other points:

- Lines: ledger 642, below the 650 ceiling and past the plan's advisory 550 mark of the parsing module it was split from; a further addition would move the generation and continuation checks into a module of their own. Third ledger test file 188.
- The predecessor check is one pass over the proved pairs with set lookups.
- No accepted duration exclusion exists.
- No live host validation ran in this round; no pane received input.
- The points disclosed in earlier rounds are unchanged: unconsolidated question blocks with confirmed user decisions, the transcript repairs made under the user's exceptions, the unchanged baseline file, the single unexplained internal error of the first cold run, the caller-supplied continuation pairs of round 3, and the round 4 choices listed in that round's writer response.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and `.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (round 6)

Twenty-eight staged paths in five `a.commit` groups; membership, order and subjects are unchanged from round 5.

1. `docs(pause): restore the pinned choice wording`: `instructions/pause-session.md`.
2. `docs(resume-paused): repair review transcript lint`: the two v0.14.0 specification review transcripts.
3. `docs(resume-paused): record Step 1 decisions`: the design and the plan.
4. `feat(resume-paused): add host evidence adapters`: unchanged members; its body now names the predecessor requirement of proved continuations and the repairs of rounds 1 to 5.
5. `docs(resume-paused): record step 1 validation`: the validation plan, whose Step 1 rows the writer reassessed after the round 5 repair; its body records that verdict in place of the reviewer's interim wording.

Changed since round 5: `tools/resume_paused_claude_ledger.py`, the third ledger test file, and the validation plan. Every other staged path is unchanged. The commit-plan checker reports the plan valid and ready.

### Writer response for step 1 resume-paused (round 6)

Writer response:

The round 5 finding, R5-1, is accepted and repaired; there is no disagreement. Its static counterexample was reproduced as a test that fails without the repair, together with the missing-ancestor case the instructions name. The reviewer's metadata repair is kept in substance: the reviewer left it unstaged, and the writer then reassessed the Step 1 rows of the validation plan after the code repair, staged that result, and replaced the interim group 5 wording of `a.commit` with the reassessed verdict.

Two choices inside the finding's instruction, disclosed for assessment:

- The requirement applies to every proved pair whose later file is listed, not only to pairs used to accept a clear marker: a pair names its earlier file whichever file it leads into, the bound transcript included, so that file's absence is detected missing history in every case.
- An earlier file that is listed but unreadable or incomplete keeps only its own read reason, and one excluded as another checkout's transcript counts as missing, so each cause is reported once and explicitly.

### Reviewer focus for step 1 resume-paused (round 6)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-6 -->

## Round 6 by reviewer - Step 1

- Recorded: 2026-11-17T10:10:56+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 1) (round 6)

Baseline index tree: 11a6bbb0bee2efeec57b6e581496efede465fe5c

Assessed index tree: 11a6bbb0bee2efeec57b6e581496efede465fe5c

### Implementation check for step 1 resume-paused (exchange 1) (round 6)

Result:

Yes. Step 1 has been fully implemented.

#### Analysis of Step 1 Implementation for resume-paused exchange 1 round 6 for step 1 resume-paused (exchange 1) (round 6)

The read-only code deliverable is complete under confirmed plan Q05=A. R5-1 is closed: _missing_predecessors checks every continuation into a listed file for an absent or excluded predecessor. Successive clears cannot hide a missing ancestor; read failures and incomplete transcripts retain their existing pending reasons, and the ordinary-process boot boundary is preserved. The new regression cases cover each failure and the complete-history control. Earlier round repairs remain present.

The six modules provide profile policy, Windows observations, Codex evidence, Claude parsing, record graphs and lifecycle absence decisions behind injected protocols. Existing type and architecture inventories in the validation plan remain accurate. No architecture violation, performance regression or existing-feature impairment was found. The ledger remains below the 650-line ceiling; the plan explicitly makes advisory estimates nonblocking. All six modules are measured by the tools coverage source, and static test inspection found no outstanding coverage gap.

The supported registry remains empty and live host checks remain open by the agreed scope. Steps 6 through 8 remain blocked until both hosts have pinned profiles.

Validation plan effects:

Updated only the Step 1 assessment paragraph and its file-size explanation in docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md. The exact Yes verdict was already staged and is unchanged; this polishing records the independent review and removes a speculative future refactor statement. No missing-work section remains. Other steps, document-level status and live checklist are unchanged. The evidence launcher proves attribution but exposes no staging operation, so this review-metadata patch remains unstaged. It changes no reviewed behavior and must be accounted for by the owning workflow before committing.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 1) (round 6)

The request reports ghog day --full=speed --whole-suite exit 0 at 2026-11-17T10:01:00+01:00, 6166 tests, 100% tools coverage, no failures, outliers or exclusions, and nothing changed after that walk. Its check stage passed type, lint, complexity, dead-code, file-size, Markdown, ShellCheck and end-of-file checks. No reviewer test, check or coverage command was needed or run: the round 6 change and regression cases were assessed statically. These measured results remain attributed to the writer.

### Resolved validation set and sources for step 1 resume-paused (exchange 1) (round 6)

ghog day --full=speed --whole-suite; source: project. The built-in speed default is completed by the requirement's whole-suite selector. Bound scope fingerprint: 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6. No plan or request additions are declared.

### Resolver drift and direction for step 1 resume-paused (exchange 1) (round 6)

None. The current .review-validation path remains absent, the resolver default remains ghog day --full=speed and the requirement still declares Test group: whole suite. The request and core-owned scope agree.

### Repository state around validation for step 1 resume-paused (exchange 1) (round 6)

Request, baseline and assessed index trees agree: 11a6bbb0bee2efeec57b6e581496efede465fe5c. The ordered 28-path before/after comparison reports only the deliberate Step 1 validation metadata edit; no other tracked or untracked side effect. Its generic acceptable=false denotes that permitted tracked metadata difference. The attribution check reports attributable=true, and the patch is confined to Step 1. Umbrella: applicable=false, changed=false. The staged implementation is unchanged; no reviewer code or test repair and no index mutation occurred.

### Repair inventory for step 1 resume-paused (exchange 1) (round 6)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md: polishing-only review metadata; independent Yes assessment and factual line-budget explanation, attributable and left unstaged because the required evidence launcher has no staging operation. No substantive repair.

Paths staged:

- docs/v0.14.0/design.v0.14.0.resume-paused.md
- docs/v0.14.0/plan.v0.14.0.resume-paused.md
- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
- docs/v0.14.0/resume-paused.profile-evidence.md
- docs/v0.14.0/review.design-specification.v0.14.0.resume-paused.md
- docs/v0.14.0/review.plan.v0.14.0.resume-paused.md
- instructions/pause-session.md
- tests/unit/tools/resume_paused_test_support.py
- `tests/unit/tools/test_resume_paused_claude/__init__.py`
- tests/unit/tools/test_resume_paused_claude/test_resume_paused_claude_tdd.py
- `tests/unit/tools/test_resume_paused_claude_graph/__init__.py`
- tests/unit/tools/test_resume_paused_claude_graph/test_resume_paused_claude_graph_tdd.py
- `tests/unit/tools/test_resume_paused_claude_ledger/__init__.py`
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
- tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
- `tests/unit/tools/test_resume_paused_codex/__init__.py`
- tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
- `tests/unit/tools/test_resume_paused_profiles/__init__.py`
- tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
- `tests/unit/tools/test_resume_paused_windows/__init__.py`
- tests/unit/tools/test_resume_paused_windows/test_resume_paused_windows_tdd.py
- tools/resume_paused_claude.py
- tools/resume_paused_claude_graph.py
- tools/resume_paused_claude_ledger.py
- tools/resume_paused_codex.py
- tools/resume_paused_profiles.py
- tools/resume_paused_windows.py

### Commit plan assessment for step 1 resume-paused (exchange 1) (round 6)

Independent commit-plan checker exit 0 on the received round 6 state: state=valid, ready=true, diagnostics=[]. All 28 staged paths belong to the same five ordered groups: docs(pause): restore the pinned choice wording; docs(resume-paused): repair review transcript lint; docs(resume-paused): record Step 1 decisions; feat(resume-paused): add host evidence adapters; docs(resume-paused): record step 1 validation. Membership, ordering, scope and conventional subjects are accurate. Group 4 describes the predecessor repair; group 5 accurately records the Yes code-deliverable verdict and open live matrix. a.commit was not changed this round.

### Findings and boundaries for step 1 resume-paused (exchange 1) (round 6)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 resume-paused (exchange 1) (round 6)

The advisory review is commit-ready for the assessed staged code deliverable. The owning workflow must account for the disclosed unstaged validation-metadata polish and preserve the open live host checklist. Follow the human commit gate; this recommendation does not authorize a commit.

### Decision rationale for step 1 resume-paused (exchange 1) (round 6)

commit-ready. All six readiness results pass for the assessed staged code: exact identity and index match; implementation completeness under Q05=A; writer validation and static coverage assessment; attributable staged implementation with only a disclosed, attributable unstaged metadata polish; no unresolved findings; accurate mechanically valid a.commit grouping. No substantive reviewer repair occurred. This is advisory and does not authorize a commit or establish supported host profiles.

### Final reviewer decision for step 1 resume-paused (exchange 1) (round 6)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-6 -->

## Round 6 by human - Step 1 - human-confirmation

- Recorded: 2026-11-17T10:43:53+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-6 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-11-18T09:20:02+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 resume-paused (round 1)

request_index_tree: 85cc988c0563b7773d2f8ce671dc87d702d67057
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): repair code transcript lint
group 1 path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add pause routing models
group 2 path: tools/resume_paused_models.py
group 2 path: tools/resume_paused_routing.py
group 2 path: tests/unit/tools/test_resume_paused_models/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
group 2 path: tests/unit/tools/test_resume_paused_routing/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
group 3: feat(resume-paused): read pause prompts and receipts
group 3 path: tools/resume_paused_artifacts.py
group 3 path: tests/memory_filesystem.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
group 4: feat(resume-paused): observe the saved exchange
group 4 path: tools/resume_paused_review.py
group 4 path: tests/unit/tools/test_resume_paused_review/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 5: docs(resume-paused): add legacy routing study
group 5 path: docs/v0.14.0/resume-paused.legacy-routing-study.md
group 6: docs(resume-paused): record step 2 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.legacy-routing-study.md
staged path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
staged path: tests/unit/tools/test_resume_paused_models/__init__.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/__init__.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_routing/__init__.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
staged path: tools/resume_paused_artifacts.py
staged path: tools/resume_paused_models.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_routing.py
```

### Validation scope for step 2 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 2 resume-paused (round 1)

Step 2 is fully implemented: the strict pause prompt, receipt and versioned routing readers and the exact-exchange observation boundary exist, and tests prove that reading writes nothing and prepares, migrates or claims nothing. The implementation check recorded `Yes. Step 2 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T09:18:05+01:00, 6456 tests, no failure, no outlier, no exclusion; slowest call 0.31 s.
- Static checks: the same walk's `check.bat` passes ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check.
- Coverage: 100% over `tools`, the four new modules included.
- Architecture: the values and routing modules perform no IO; the artifact reader is the filesystem adapter over them; the observer follows the existing read-only status pattern of exact paths, the observation lock and the observer. No module writes a file, claims a role, starts a process or calls TUIOS.
- Performance: single passes over prompt and receipt lines, one fence scan, linear table comparison, one map of panes; each checkout reads at most four exact files once, and the observer reads the exact exchange paths and the transcript once.
- Feature integrity: no existing production module changes; the new modules have no caller yet. Prompts and receipts keep the grammar the installed launcher parses.

### Implementation report for step 2 resume-paused (round 1)

Four read-only modules implement the Step 2 contracts of the consolidated design, beside the legacy routing study.

- `tools/resume_paused_models.py`: shared values. `CanonicalRoot` compares checkout roots by Windows rules (case, `/` or `\`, repeated or trailing separators, the `\\?\` and `\\?\UNC\` prefixes) and refuses dot segments, trailing dots or spaces and reserved characters. `PromptDigest`, agent ids, full pane UUIDs, offset timestamps and single-line text checks complete it; the text check also refuses U+2028 and U+2029, which `str.splitlines` treats as line breaks.
- `tools/resume_paused_routing.py`: schema `resume-paused-routing` version 1. `SavedRouting` holds the pause identity, the observation, the resumed, requestor and reviewer targets and the exact exchange, and renders back to the same canonical JSON. A part recorded as `{"unknown": reason}` stays unresolved without failing the pause; a pair slot or the exchange may be `{"not_applicable": reason}`. Unrecognized keys, wrong types, other versions and contradictions between parts are errors. `SavedExchange` derives the complete exchange identity from the reviewed document and leaves the current round to live state.
- `tools/resume_paused_artifacts.py`: `read_checkout_snapshot` loads the home through `ReviewArtifactConfiguration.load`, validates the existing ignore bytes, reads the prompt's exact bytes and the receipt, and applies the resume-session state table (no saved prompt, unused, new since use, used, error) with the exact paths read and their byte account. Receipts of schemas 1, 2 and 3 parse. Routing is read only from one top-level block fenced as `` ```json resume-paused-routing ``; the readable table headed `| Routing item | Value |` is rendered from that object and must equal the rendering when present.
- `tools/resume_paused_review.py`: `observe_saved_exchange` rebuilds the saved context, derives its exact paths, takes the nonblocking `observe_transition` lock and classifies through `ReviewExchangeObserver` and `current_request_occurrence`, reading the coordination record before and after. It reports not live, busy, selection changed, damaged or observed, with the ownership generation and role natures and never the token digest.
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`: why the prose table cannot be read as routing, the digest and used-receipt hazards of any rewrite, the manual resume and fresh pause path, and the preconditions of a separate converter. No converter is implemented.
- Tests: one leaf per module, each declaring its files in the memory-backed scratch tree or as plain data. Read-only proofs compare whole checkout trees before and after each read and make every home preparation, migration, review-core construction and filesystem mutation fail. A local replay of the installed launcher's heading and field readers, copied without importing senv, checks the prompt and receipt grammar.

Points for the reviewer's attention:

- Interpretation: the plan's "unknown routing fields" is read as fields recorded with an explicit `{"unknown": reason}` value, which give unresolved-target skips. Unrecognized keys, duplicate keys and unsupported versions remain errors, like every strict review model.
- Contracts this step fixes for later steps: the routing fence line and table header (Step 3 writes them), and the schema 3 receipt field names `Launch id` (32 lowercase hexadecimal characters), `Receiving pane` and `Assignment binding` (Step 4 writes them).
- Deviations from the planned file list: the first models module (653 lines) and test module (732) exceeded the 650-line ceiling, so the routing schema moved to the new `tools/resume_paused_routing.py`, and the tests were split into `test_resume_paused_artifacts`, `test_resume_paused_models`, `test_resume_paused_routing` and `test_resume_paused_review`. `tests/memory_filesystem.py` registers the artifact and review leaves with the memory-backed scratch filesystem. `tools/resume_paused_artifacts.py` has 562 lines.
- Under the user's exception of 2026-11-18, twelve bare `__init__.py` path lines in the Step 1 round 5 and round 6 repair inventories of the code review transcript were wrapped in code spans to clear the `MD050` findings that blocked the Markdown gate; no other transcript line changed. That repair is its own commit group.
- The first models module was written before its tests; the tests for the artifacts, review and split modules came first.
- `rg` is not available in the shell used, so the contract inspection used the equivalent Grep search over the four modules.
- The first whole-suite day walk lost its affected stage to two lifecycle overruns in untouched groundhog tests (one wall-only, one CPU at 0.3125 s); both passed in focus and the restarted walk was green.
- The validation plan states coverage as a static assessment, written before the coverage walk; the speed walk below measures it.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step2.journal.md` and `.reviews/a.resume-paused.step2.handoff.md`.

### Change summary for step 2 resume-paused (round 1)

Nineteen staged paths in six `a.commit` groups, in this order:

1. `docs(resume-paused): repair code transcript lint`: `docs/v0.14.0/review.code.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add pause routing models`: `tools/resume_paused_models.py`, `tools/resume_paused_routing.py`, and the `tests/unit/tools/test_resume_paused_models` and `tests/unit/tools/test_resume_paused_routing` packages (one package file, one tdd and one pbt file each).
3. `feat(resume-paused): read pause prompts and receipts`: `tools/resume_paused_artifacts.py`, `tests/memory_filesystem.py`, and the `tests/unit/tools/test_resume_paused_artifacts` package (package file, tdd and pbt files).
4. `feat(resume-paused): observe the saved exchange`: `tools/resume_paused_review.py` and the `tests/unit/tools/test_resume_paused_review` package (package file and tdd file).
5. `docs(resume-paused): add legacy routing study`: `docs/v0.14.0/resume-paused.legacy-routing-study.md`.
6. `docs(resume-paused): record step 2 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready.

### Writer response for step 2 resume-paused (round 1)

Writer response:

First round: no earlier feedback to answer and no disagreement.

### Reviewer focus for step 2 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-11-18T09:47:43+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 resume-paused (exchange 1) (round 1)

Baseline index tree: 85cc988c0563b7773d2f8ce671dc87d702d67057

Assessed index tree: 444c155d7be2771932347e75c31b047ac807a15b

### Implementation check for step 2 resume-paused (exchange 1) (round 1)

Result:

No. Step 2 has NOT been fully implemented.

The four modules, legacy study and no-write tests deliver most of the planned structure, but the observer can report absence for incomplete or busy evidence, lock IO failures escape the typed boundary, and read accounting omits actual IO. These are step 2 requirements; later implementation and deferred senv integration remain outside this assessment. Pure values and adapters have appropriate dependency direction, and all staged Python files remain under 650 lines.

Validation plan effects:

Updated only the Step 2 section of `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: exact No verdict, three concrete missing-work bullets, corrected read-cost and static coverage assessments. The patch was attributed from the retained pre-edit blob and staged alone. No other step, umbrella, implementation, tests or a.commit was edited.

### Pre-repair mandatory checks and coverage for step 2 resume-paused (exchange 1) (round 1)

The requestor reports `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T09:18:05+01:00, 6456 tests, 100% line coverage over `tools`, no failure, outlier or exclusion, with static checks passing. This is requestor evidence, not an independent reviewer run. Reviewer inspected source and module-specific tests statically; no ghog test/check command or coverage run was needed to establish these defects. Reported line coverage does not cover the missing combinations and IO failure behaviors.

### Resolved validation set and sources for step 2 resume-paused (exchange 1) (round 1)

Request and current resolution: `ghog day --full=speed --whole-suite`, source `project`. No `.review-validation` declaration exists; the built-in speed default applies. `prompt_workflow.bat scope day --full=speed` returned the identical command. No plan/request additions are present. Bound round scope: whole; fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The reviewer did not execute the resolved requestor command.

### Resolver drift and direction for step 2 resume-paused (exchange 1) (round 1)

None. Project default, requirement selector and request validation command agree.

### Repository state around validation for step 2 resume-paused (exchange 1) (round 1)

Baseline/request tree: `85cc988c0563b7773d2f8ce671dc87d702d67057`. Assessed tree: `444c155d7be2771932347e75c31b047ac807a15b`. The evidence launcher compared the same ordered 19-path set before and after: only the validation plan and index changed. Raw comparison reports acceptable=false because these are tracked changes; inspection and patch attribution show the difference is entirely the authorized Step 2 review metadata. Tree-to-tree comparison names only that validation plan, and its worktree matches its staged version. No implementation/test change or validation side effect occurred. Umbrella comparison: applicable=false, changed=false.

### Repair inventory for step 2 resume-paused (exchange 1) (round 1)

Repairs made:

- Review metadata only (polishing-only): `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`; recorded the No assessment and missing work. No substantive repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` — only the attributable Step 2 assessment patch was staged by the reviewer.

### Commit plan assessment for step 2 resume-paused (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json` passed before assessment and after staging review metadata: exit 0, state=valid, ready=true, diagnostics=[]. The 19 staged paths remain assigned exactly once across these ordered groups:

1. `docs(resume-paused): repair code transcript lint`: `docs/v0.14.0/review.code.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add pause routing models`: `tools/resume_paused_models.py`, `tools/resume_paused_routing.py`, `tests/unit/tools/test_resume_paused_models/__init__.py`, `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py`, `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py`, `tests/unit/tools/test_resume_paused_routing/__init__.py`, `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py`, `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py`.
3. `feat(resume-paused): read pause prompts and receipts`: `tools/resume_paused_artifacts.py`, `tests/memory_filesystem.py`, `tests/unit/tools/test_resume_paused_artifacts/__init__.py`, `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py`, `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py`.
4. `feat(resume-paused): observe the saved exchange`: `tools/resume_paused_review.py`, `tests/unit/tools/test_resume_paused_review/__init__.py`, `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`.
5. `docs(resume-paused): add legacy routing study`: `docs/v0.14.0/resume-paused.legacy-routing-study.md`.
6. `docs(resume-paused): record step 2 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Ordering is coherent: isolated human-authorized transcript lint repair, pure models/routing, artifact parser, exchange observer, legacy study, then validation. The additional routing module and test leaves are justified responsibility splits. Subjects and membership remain accurate; mechanical readiness does not overcome the findings.

### Findings and boundaries for step 2 resume-paused (exchange 1) (round 1)

Unresolved findings:

- [P1] Validate absence under the observation lock (`tools/resume_paused_review.py:181`). The early `coordination.exists()` return bypasses both the lock and `ReviewExchangeObserver`. With no coordination and an existing malformed request/answer/tombstone, it returns NOT_LIVE without reading the damaged evidence. With a publisher holding the lock before coordination appears, it also returns NOT_LIVE instead of BUSY. The existing core classifier preserves valid orphan requests/answers as abandoned and tombstones as interrupted; this adapter discards all of those distinctions. Move absence classification under the lock, validate the exact artifact set, preserve explicit orphan/incomplete states and return DAMAGED for invalid evidence. Add no-write cases for malformed and valid orphan artifacts, held lock without coordination, and genuinely absent state.
- [P2] Catch observation-lock IO failures at the public boundary (`tools/resume_paused_review.py:183`). `observe_transition` can raise PermissionError when opening the lock, unexpected OSError during native acquisition, or an unlock error on exit. `_observe_settled` catches IO only inside the with body, so these failures escape rather than returning ExchangeObservationKind.DAMAGED for this checkout. Wrap the complete lock context in the typed error boundary; test denied/unreadable locks and injected acquisition/exit IO failures while retaining BUSY for ordinary contention and zero writes.
- [P2] Account for the reads the adapters actually perform (`tools/resume_paused_artifacts.py:531`, `tools/resume_paused_review.py:118`). `ReviewArtifactConfiguration.load` reads `.review-artifacts.ini` before `_CheckoutReader` initializes its empty account, so custom-home snapshots omit that path and its bytes, including when declaration parsing fails. The observer callback counts only its before/after probes: `store.read_coordination` and `ReviewExchangeObserver._snapshot` read coordination again (four total), and delegated envelope/configuration/transcript reads have no complete returned account. This contradicts the step's deterministic exact-path IO evidence and validation claim of two coordination reads. Provide accounting across the reused readers and assert actual paths/bytes independently, including custom declarations, declaration errors and a populated exchange; update the validation claims to match.

Boundary-crossing work: None.

### Writer instructions for step 2 resume-paused (exchange 1) (round 1)

Implement the three missing-work items in the Step 2 validation section, with deterministic regression tests preserving the read-only boundary. Keep absence distinct from busy, incomplete and damaged evidence; include lock entry/exit failures and all actual evidence reads in the tests. Update only the affected step evidence and keep a.commit aligned. Run the writer-owned scope-resolved validation, including its speed/coverage gate, before publishing a replacement request for this exact plan and step. Do not treat this answer as commit authorization.

### Decision rationale for step 2 resume-paused (exchange 1) (round 1)

Changes requested. Six readiness results: exact identity PASS; completeness FAIL (three findings); validation/coverage FAIL for behavioral completeness despite the reported green requestor walk; staged attribution PASS (only review metadata added); unresolved findings FAIL (three); a.commit PASS (independently valid/ready, no diagnostics). No Human guidance block was supplied, so no implementation or test repair was made. The review is advisory and grants no commit authority.

### Final reviewer decision for step 2 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-11-18T10:40:47+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 resume-paused (round 2)

request_index_tree: 6c13d1372e3bb9c59779934bbff1896f3b4bb092
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): repair code transcript lint
group 1 path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add pause routing models
group 2 path: tools/resume_paused_models.py
group 2 path: tools/resume_paused_routing.py
group 2 path: tests/unit/tools/test_resume_paused_models/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
group 2 path: tests/unit/tools/test_resume_paused_routing/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
group 3: feat(resume-paused): read pause prompts and receipts
group 3 path: tools/resume_paused_artifacts.py
group 3 path: tests/memory_filesystem.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
group 4: feat(resume-paused): observe the saved exchange
group 4 path: tools/resume_paused_review.py
group 4 path: tests/unit/tools/test_resume_paused_review/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 5: docs(resume-paused): add legacy routing study
group 5 path: docs/v0.14.0/resume-paused.legacy-routing-study.md
group 6: docs(resume-paused): record step 2 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.legacy-routing-study.md
staged path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
staged path: tests/unit/tools/test_resume_paused_models/__init__.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/__init__.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_routing/__init__.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
staged path: tools/resume_paused_artifacts.py
staged path: tools/resume_paused_models.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_routing.py
```

### Validation scope for step 2 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 2 resume-paused (round 2)

Step 2 is fully implemented after the round 1 repairs: absence is decided under the observation lock through the observer, lock IO failures are damaged results, and both adapters account for every read they and the reused readers make. The implementation check records `Yes. Step 2 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T10:39:02+01:00, 6464 tests, no failure, no outlier, no exclusion; slowest call 0.31 s.
- Static checks: the same walk's `check.bat` passes ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check, on a working tree that holds the repaired transcript.
- Coverage: 100% over `tools`, the four new modules included.
- Architecture: the values and routing modules perform no IO; the artifact reader is the filesystem adapter over them; the observer follows the read-only status pattern of exact paths, the observation lock and the observer, with the review configuration supplied by its caller and an accounted subclass of the exchange store for its reads. No module writes a file, claims a role, starts a process or calls TUIOS.
- Performance: single passes over prompt and receipt lines, one fence scan, linear table comparison, one map of panes; a checkout reads at most four exact files once; an observation reads the coordination record four times, each present artifact once and the transcript once, all returned in its account.
- Feature integrity: no existing production module changes; the new modules have no caller yet. Prompts and receipts keep the grammar the installed launcher parses.

### Implementation report for step 2 resume-paused (round 2)

Four read-only modules implement the Step 2 contracts of the consolidated design, beside the legacy routing study; round 2 repairs the observer and both read accounts.

- `tools/resume_paused_models.py`: shared values. `CanonicalRoot` compares checkout roots by Windows rules (case, `/` or `\`, repeated or trailing separators, the `\\?\` and `\\?\UNC\` prefixes) and refuses dot segments, trailing dots or spaces and reserved characters. `PromptDigest`, agent ids, full pane UUIDs, offset timestamps and single-line text checks complete it; the text check also refuses U+2028 and U+2029, which `str.splitlines` treats as line breaks.
- `tools/resume_paused_routing.py`: schema `resume-paused-routing` version 1. `SavedRouting` holds the pause identity, the observation, the resumed, requestor and reviewer targets and the exact exchange, and renders back to the same canonical JSON. A part recorded as `{"unknown": reason}` stays unresolved without failing the pause; a pair slot or the exchange may be `{"not_applicable": reason}`. Unrecognized keys, wrong types, other versions and contradictions between parts are errors.
- `tools/resume_paused_artifacts.py`: `read_checkout_snapshot` loads the home through `ReviewArtifactConfiguration.load`, validates the existing ignore bytes, reads the prompt's exact bytes and the receipt, and applies the resume-session state table with the exact paths read and their byte account, which now starts with the `.review-artifacts.ini` declaration whenever the load reads it, including when the declaration is refused. Receipts of schemas 1, 2 and 3 parse. Routing is read only from one top-level block fenced as `` ```json resume-paused-routing ``; the readable table headed `| Routing item | Value |` is rendered from that object and must equal the rendering when present.
- `tools/resume_paused_review.py`: `observe_saved_exchange(configuration, review_configuration, exchange, wall_clock)` takes the nonblocking `observe_transition` lock first and classifies through `ReviewExchangeObserver` and `current_request_occurrence`, with or without a coordination record. Only an empty artifact set is not live; a held lock or a record changing between the two probes is busy; orphan requests and answers keep their abandoned states and a tombstone its interrupted state; another occurrence, round, document, umbrella or step is a changed selection; invalid evidence and lock entry, acquisition or exit failures are damaged. Reads go through `_AccountedStore`, a subclass of the exchange store that records each read of its read methods, and the snapshot returns the exact paths in order with their bytes. The caller supplies the review configuration, loaded once per checkout as the status collector does.
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`: unchanged since round 1.
- Tests: one leaf per module. Read-only proofs compare whole checkout trees before and after each read and make every home preparation, migration, review-core construction and filesystem mutation fail. An independent recorder of `Path.read_text` and `Path.read_bytes` checks both read accounts. A local replay of the installed launcher's heading and field readers, copied without importing senv, checks the prompt and receipt grammar.

Points for the reviewer's attention:

- The observer's signature gained the `review_configuration` argument; it has no caller yet. Its four coordination reads are now reported, not hidden: two stability probes, the adapter's read (it needs the record's policy before constructing the observer) and the observer's own.
- The neutral `FamilyPolicy` passed when no coordination record exists is never consulted by the observer, which compares a policy only against a record.
- Interpretation kept from round 1: "unknown routing fields" means fields recorded as `{"unknown": reason}`; unrecognized keys stay errors.
- Contracts this step fixes for later steps: the routing fence line and table header (Step 3), and the schema 3 receipt fields `Launch id` (32 lowercase hexadecimal characters), `Receiving pane` and `Assignment binding` (Step 4).
- Deviations from the planned file list (round 1): the routing schema module and the per-module test leaves split for the 650-line ceiling, and `tests/memory_filesystem.py` registers the artifact and review leaves. Line counts: `tools/resume_paused_artifacts.py` 578, `tools/resume_paused_review.py` 318.
- Transcript repairs, each under its own user exception of 2026-11-18: the staged group 1 wraps twelve bare `__init__.py` paths of the Step 1 entries; in the working copy, the round 1 answer's `- N.` lines 1807-1812 lost their leading `-` to clear `MD029`. The latter belongs to the residual transcript commit with the unstaged `.vscode/settings.json` word `nonbound`.
- `rg` is not available in the shell used; the contract inspection used the equivalent Grep search.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step2.journal.md` and `.reviews/a.resume-paused.step2.handoff.md`.

### Change summary for step 2 resume-paused (round 2)

Nineteen staged paths in the same six `a.commit` groups as round 1; the repairs change five of them and no membership, order or subject.

1. `docs(resume-paused): repair code transcript lint`: `docs/v0.14.0/review.code.v0.14.0.resume-paused.md` (staged copy: the twelve-line group 1 repair only).
2. `feat(resume-paused): add pause routing models`: `tools/resume_paused_models.py`, `tools/resume_paused_routing.py`, and the `tests/unit/tools/test_resume_paused_models` and `tests/unit/tools/test_resume_paused_routing` packages; unchanged in round 2.
3. `feat(resume-paused): read pause prompts and receipts`: `tools/resume_paused_artifacts.py` (declaration accounting), `tests/memory_filesystem.py`, and the `tests/unit/tools/test_resume_paused_artifacts` package (read recorder and two accounting tests).
4. `feat(resume-paused): observe the saved exchange`: `tools/resume_paused_review.py` (lock-first observation, lock failures, accounted store) and the `tests/unit/tools/test_resume_paused_review` package (orphan, held-lock, lock-failure and accounting cases).
5. `docs(resume-paused): add legacy routing study`: `docs/v0.14.0/resume-paused.legacy-routing-study.md`; unchanged.
6. `docs(resume-paused): record step 2 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (Step 2 back to Yes after the repairs).

Unstaged, for the residual commit after the review: the transcript's round entries with the approved lines 1807-1812 repair, and `.vscode/settings.json` with the project word `nonbound`. The commit-plan checker reports the plan valid and ready.

### Writer response for step 2 resume-paused (round 2)

Writer response:

All three round 1 findings are accepted and repaired, with no disagreement.

- [P1] Absence under the observation lock: `observe_saved_exchange` now takes `observe_transition` first and decides every outcome under it through `ReviewExchangeObserver`, with or without a coordination record (a neutral policy is passed when no record exists, since the observer compares a policy only against a record). Only an empty artifact set is not live. A held lock is busy before and after the record exists; a valid orphan request keeps `abandoned-request` with its envelope round and transcript occurrence, a tombstone keeps `interrupted-answer-publication`, and a malformed orphan answer is damaged. New no-write tests cover each case beside the genuinely absent one.
- [P2] Lock IO failures: the whole lock context sits inside the typed boundary, so a lock that cannot be opened (a directory at the lock path), a failing native acquisition and a failing unlock on exit each return `damaged` with an `observation lock failed` diagnostic, while ordinary contention stays busy.
- [P2] Read accounting: `read_checkout_snapshot` now starts its exact reads and bytes with the `.review-artifacts.ini` declaration whenever the configuration load reads it, on success and on refusal. The observer reads through an accounted subclass of the exchange store, so the reads the store and the observer make are recorded with the two stability probes; the snapshot returns the exact paths in order with their bytes. The review configuration is now supplied by the caller, loaded once per checkout as the status collector does, so the observer reads only exchange evidence. An independent recorder of `Path.read_text` and `Path.read_bytes` checks both accounts: a custom-home snapshot reads the declaration, ignore file and prompt; a refused declaration is still accounted; a populated exchange reads coordination four times, then the request and transcript, in the order the snapshot reports.
- The validation plan's Step 2 section returns to `Yes` with corrected read-cost and coverage statements and no missing-work section; the reviewer's No rewrite was the starting point.
- Transcript, under the user's exception of 2026-11-18: the round 1 answer's commit-group list at lines 1807-1812 used `- N.` bullets, each nesting a one-item numbered list, which fails `MD029` and therefore the Markdown gate. Only the leading `-` of those six lines was removed. A later answer can avoid this by writing the groups as a plain numbered list. The user also chose to add `nonbound`, a word of the committed Step 1 entries, to the project cSpell words; that `.vscode/settings.json` change is unstaged and joins the transcript's residual commit.

### Reviewer focus for step 2 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-11-18T10:47:29+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 resume-paused (exchange 1) (round 2)

Baseline index tree: 6c13d1372e3bb9c59779934bbff1896f3b4bb092

Assessed index tree: 5d55575e5da641c41d39cdaa307e94c35cb024cf

### Implementation check for step 2 resume-paused (exchange 1) (round 2)

Result:

No. Step 2 has NOT been fully implemented.

The first two round 1 findings are resolved: absence is classified under the lock through the existing observer, and lock entry/acquisition/release failures become damaged outcomes. Declaration and successful exchange reads are now accounted. One carried finding remains: failed parsing drops completed delegated reads. Models, routing, legacy study, read-only boundaries, architecture and file sizes remain acceptable. No implementation or test changes were made by the reviewer.

Validation plan effects:

Updated only Step 2 of `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: exact No verdict, explanation, missing-work section, read-cost qualification and unit-test gap. The attributable metadata patch alone was staged. Other steps and document-level status were unchanged. Umbrella: none.

### Pre-repair mandatory checks and coverage for step 2 resume-paused (exchange 1) (round 2)

Requestor reports `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T10:39:02+01:00: 6464 tests, 100% line coverage over `tools`, no outlier or exclusion, slowest call 0.31 s, all static checks green. These are requestor results, not a reviewer rerun. Static review compared the five-file round 2 change with the round 1 assessed tree and traced delegated error paths. No reviewer test or coverage command was needed or run. Current tests check damaged classification but omit accounting assertions for malformed evidence.

### Resolved validation set and sources for step 2 resume-paused (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` (source: project). No plan or request additions. Bound scope: whole; fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`, from `.reviews/a.review-scope.code.v0.14.0.resume-paused.json`.

### Resolver drift and direction for step 2 resume-paused (exchange 1) (round 2)

No drift in either direction. Exact marker check found `.review-validation` absent; current `prompt_workflow.bat scope day --full=speed` returned the same command as the request.

### Repository state around validation for step 2 resume-paused (exchange 1) (round 2)

Request-time and baseline index tree: `6c13d1372e3bb9c59779934bbff1896f3b4bb092`. Assessed index tree: `5d55575e5da641c41d39cdaa307e94c35cb024cf`. The same ordered set of 19 staged paths was captured before and after. Raw comparison flags only the Step 2 validation plan and index; exact attribution proves both result solely from the permitted reviewer metadata patch. No implementation/test/other-step change, unrelated staging, or validation side effect occurred. Umbrella comparison is not applicable and unchanged. Pre-existing transcript and editor-settings work remains unstaged.

### Repair inventory for step 2 resume-paused (exchange 1) (round 2)

Repairs made:

- None to implementation or tests. Review metadata only: Step 2 validation verdict and missing-work rows in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`
- `docs/v0.14.0/review.code.v0.14.0.resume-paused.md`
- `tests/memory_filesystem.py`
- `tests/unit/tools/test_resume_paused_artifacts/__init__.py`
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py`
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py`
- `tests/unit/tools/test_resume_paused_models/__init__.py`
- `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py`
- `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py`
- `tests/unit/tools/test_resume_paused_review/__init__.py`
- `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`
- `tests/unit/tools/test_resume_paused_routing/__init__.py`
- `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py`
- `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py`
- `tools/resume_paused_artifacts.py`
- `tools/resume_paused_models.py`
- `tools/resume_paused_review.py`
- `tools/resume_paused_routing.py`

### Commit plan assessment for step 2 resume-paused (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json`: exit 0, state valid, ready true, no diagnostics; all 19 staged paths assigned once. Group membership, dependency order and conventional subjects remain accurate after the metadata update. No `a.commit` amendment.

- `docs(resume-paused): repair code transcript lint` (1 path).
- `feat(resume-paused): add pause routing models` (8 paths).
- `feat(resume-paused): read pause prompts and receipts` (5 paths).
- `feat(resume-paused): observe the saved exchange` (3 paths).
- `docs(resume-paused): add legacy routing study` (1 path).
- `docs(resume-paused): record step 2 validation` (1 path).

### Findings and boundaries for step 2 resume-paused (exchange 1) (round 2)

Unresolved findings:

- [P2] Account reads before evidence parsing can reject them (`tools/resume_paused_review.py:129-148`). Each `_AccountedStore` override calls its superclass before recording the read. `ReviewExchangeStore.read_artifact` reads the bytes as text and validates the envelope before returning; malformed content therefore raises before `_reads.record`. In the existing malformed-orphan-answer fixture, the answer is read, but the damaged snapshot returns `reads=()` and zero files/bytes. Invalid coordination likewise loses its delegated read, and a transcript decode failure loses the transcript read. This leaves the exact-path/byte contract and carried round 1 accounting finding incomplete. Record actual consumed bytes at the read boundary, before parsing, retain them on failure, and extend the independent recorder tests to these cases without extra accounting reads.

Boundary-crossing work: None.

### Writer instructions for step 2 resume-paused (exchange 1) (round 2)

Complete the carried accounting repair at the underlying read boundary. Preserve consumed paths and byte counts when envelope/coordination parsing or transcript decoding fails, while keeping classification and no-write behavior. Add independent recorder assertions for malformed orphan answers, malformed coordination and invalid UTF-8 transcripts; do not reread merely to calculate accounting. Update Step 2 validation, run the requestor-owned resolved validation set, and publish a fresh request for the resulting index tree.

### Decision rationale for step 2 resume-paused (exchange 1) (round 2)

Changes requested. Readiness floor: identity passes; implementation completeness fails on the carried read-accounting defect; requestor validation is green but static test assessment finds missing failure-path accounting assertions; staged attribution passes; unresolved-findings gate fails on one P2; commit-plan assessment passes. No substantive reviewer repair occurred. This advisory answer does not authorize a commit.

### Final reviewer decision for step 2 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 3 by requestor - Step 2

- Recorded: 2026-11-18T14:10:06+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 2
Review round: 3

### Code review evidence for step 2 resume-paused (round 3)

request_index_tree: 38c0813a65e435707fd157987aface6b2b2ca510
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): repair code transcript lint
group 1 path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
group 2: test(groundhog): shorten args-file acceptance tests
group 2 path: tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py
group 3: feat(resume-paused): add pause routing models
group 3 path: tools/resume_paused_models.py
group 3 path: tools/resume_paused_routing.py
group 3 path: tests/unit/tools/test_resume_paused_models/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
group 3 path: tests/unit/tools/test_resume_paused_routing/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
group 4: feat(resume-paused): read pause prompts and receipts
group 4 path: tools/resume_paused_artifacts.py
group 4 path: tests/memory_filesystem.py
group 4 path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
group 4 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
group 5: feat(resume-paused): observe the saved exchange
group 5 path: tools/resume_paused_review.py
group 5 path: tests/unit/tools/test_resume_paused_review/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 6: docs(resume-paused): add legacy routing study
group 6 path: docs/v0.14.0/resume-paused.legacy-routing-study.md
group 7: docs(resume-paused): record step 2 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.legacy-routing-study.md
staged path: docs/v0.14.0/review.code.v0.14.0.resume-paused.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py
staged path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
staged path: tests/unit/tools/test_resume_paused_models/__init__.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/__init__.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_routing/__init__.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
staged path: tools/resume_paused_artifacts.py
staged path: tools/resume_paused_models.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_routing.py
```

### Validation scope for step 2 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 2 resume-paused (round 3)

Step 2 is fully implemented after the round 2 repair: every exchange read is accounted where its bytes are consumed, before decoding or parsing, so damaged snapshots keep their reads. The implementation check records `Yes. Step 2 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T14:08:41+01:00, 6467 tests, no failure, no outlier, no exclusion; slowest call 0.43 s.
- Static checks: the same walk's `check.bat` passes ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check, on a working tree that holds the repaired transcript.
- Coverage: 100% over `tools`, the four new modules included.
- Architecture: the values and routing modules perform no IO; the artifact reader is the filesystem adapter over them; the observer follows the read-only status pattern, with the review configuration supplied by its caller and accounted exact paths handed to the unchanged exchange store. No module writes a file, claims a role, starts a process or calls TUIOS.
- Performance: single passes over prompt and receipt lines, one fence scan, linear table comparison, one map of panes; a checkout reads at most four exact files once; an observation reads the coordination record four times, each present artifact once and the transcript once, all in its account, and decoding reuses the bytes read.
- Feature integrity: no existing production module changes; the new modules have no caller yet; the separate groundhog test group keeps every assertion of the three args-file tests. Prompts and receipts keep the grammar the installed launcher parses.

### Implementation report for step 2 resume-paused (round 3)

Four read-only modules implement the Step 2 contracts of the consolidated design, beside the legacy routing study; round 3 moves the observer's read accounting to the read boundary.

- `tools/resume_paused_models.py`: shared values. `CanonicalRoot` compares checkout roots by Windows rules (case, `/` or `\`, repeated or trailing separators, the `\\?\` and `\\?\UNC\` prefixes) and refuses dot segments, trailing dots or spaces and reserved characters. `PromptDigest`, agent ids, full pane UUIDs, offset timestamps and single-line text checks complete it; the text check also refuses U+2028 and U+2029, which `str.splitlines` treats as line breaks.
- `tools/resume_paused_routing.py`: schema `resume-paused-routing` version 1. `SavedRouting` holds the pause identity, the observation, the resumed, requestor and reviewer targets and the exact exchange, and renders back to the same canonical JSON. A part recorded as `{"unknown": reason}` stays unresolved without failing the pause; a pair slot or the exchange may be `{"not_applicable": reason}`. Unrecognized keys, wrong types, other versions and contradictions between parts are errors.
- `tools/resume_paused_artifacts.py`: `read_checkout_snapshot` loads the home through `ReviewArtifactConfiguration.load`, validates the existing ignore bytes, reads the prompt's exact bytes and the receipt, and applies the resume-session state table with the exact paths read and their byte account, which now starts with the `.review-artifacts.ini` declaration whenever the load reads it, including when the declaration is refused. Receipts of schemas 1, 2 and 3 parse. Routing is read only from one top-level block fenced as `` ```json resume-paused-routing ``; the readable table headed `| Routing item | Value |` is rendered from that object and must equal the rendering when present.
- `tools/resume_paused_review.py`: `observe_saved_exchange(configuration, review_configuration, exchange, wall_clock)` takes the nonblocking `observe_transition` lock first and classifies through `ReviewExchangeObserver` and `current_request_occurrence`, with or without a coordination record. Only an empty artifact set is not live; a held lock or a record changing between the two probes is busy; orphan requests and answers keep their abandoned states and a tombstone its interrupted state; another occurrence, round, document, umbrella or step is a changed selection; invalid evidence and lock entry, acquisition or exit failures are damaged. The unchanged `ReviewExchangeStore` reads through `_AccountedPath` objects, a `Path` subclass that records each consumed byte count where the bytes are read and decodes text from those bytes, so the snapshot returns every exact path in order with its bytes, including reads that parsing or decoding then rejects. The caller supplies the review configuration, loaded once per checkout as the status collector does.
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`: unchanged since round 1.
- Tests: one leaf per module. Read-only proofs compare whole checkout trees before and after each read and make every home preparation, migration, review-core construction and filesystem mutation fail. An independent recorder of `Path.read_text` and `Path.read_bytes` checks both read accounts, on success and on rejected evidence. A local replay of the installed launcher's heading and field readers, copied without importing senv, checks the prompt and receipt grammar.

Points for the reviewer's attention:

- The observer's signature gained the `review_configuration` argument in round 2; it has no caller yet. Its four coordination reads are reported: two stability probes, the adapter's read (it needs the record's policy before constructing the observer) and the observer's own.
- `_AccountedPath.read_text` reproduces `Path.read_text` through `io.TextIOWrapper` over the accounted bytes, with the same encoding, errors and newline arguments; `resolve` is overridden as well as `with_segments` so a resolved path stays accounted under any `resolve` implementation.
- The neutral `FamilyPolicy` passed when no coordination record exists is never consulted by the observer, which compares a policy only against a record.
- Interpretation kept from round 1: "unknown routing fields" means fields recorded as `{"unknown": reason}`; unrecognized keys stay errors.
- Contracts this step fixes for later steps: the routing fence line and table header (Step 3), and the schema 3 receipt fields `Launch id` (32 lowercase hexadecimal characters), `Receiving pane` and `Assignment binding` (Step 4).
- Deviations from the planned file list (round 1): the routing schema module and the per-module test leaves split for the 650-line ceiling, and `tests/memory_filesystem.py` registers the artifact and review leaves. Line counts: `tools/resume_paused_artifacts.py` 578, `tools/resume_paused_review.py` 346.
- Transcript repairs, each under its own user exception of 2026-11-18: the staged group 1 wraps twelve bare `__init__.py` paths of the Step 1 entries; in the working copy, the round 1 answer's numbered lines 1807-1812 lost their leading bullet to clear `MD029`, and my round 2 lines 1952, 1978 and 1981 were corrected for `MD038` and one cSpell word. The working-copy edits belong to the residual transcript commit with the unstaged `.vscode/settings.json` word `nonbound`.
- Outside the Step 2 plan, at the user's direction on 2026-11-18: the round 3 speed walk failed only on the CPU lifecycle budget of the three tests in `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py`, untouched by this step (0.11 to 0.16 s against the 0.1 s ceiling, band tolerance lost after three runs above it, reproduced in focus). A pyinstrument profile put most of the call in resolving the 61-file sentinel group. The tests now lower `args_file.COMMAND_LINE_BUDGET` to 100 and use three short files; a new precondition asserts that the expanded command exceeds the lowered budget, and every earlier assertion is kept. This is its own commit group, `test(groundhog): shorten args-file acceptance tests`.
- `rg` is not available in the shell used; the contract inspection used the equivalent Grep search.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step2.journal.md` and `.reviews/a.resume-paused.step2.handoff.md`.

### Change summary for step 2 resume-paused (round 3)

Twenty staged paths in seven `a.commit` groups; round 3 adds group 2 and changes three Step 2 paths, with no other membership, order or subject change.

1. `docs(resume-paused): repair code transcript lint`: `docs/v0.14.0/review.code.v0.14.0.resume-paused.md` (staged copy: the twelve-line group 1 repair only).
2. `test(groundhog): shorten args-file acceptance tests`: `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py` (new in round 3, outside the Step 2 plan, at the user's direction).
3. `feat(resume-paused): add pause routing models`: `tools/resume_paused_models.py`, `tools/resume_paused_routing.py`, and the `tests/unit/tools/test_resume_paused_models` and `tests/unit/tools/test_resume_paused_routing` packages; unchanged.
4. `feat(resume-paused): read pause prompts and receipts`: `tools/resume_paused_artifacts.py`, `tests/memory_filesystem.py`, and the `tests/unit/tools/test_resume_paused_artifacts` package; unchanged since round 2.
5. `feat(resume-paused): observe the saved exchange`: `tools/resume_paused_review.py` (accounted paths at the read boundary) and the `tests/unit/tools/test_resume_paused_review` package (rejected-read accounting test).
6. `docs(resume-paused): add legacy routing study`: `docs/v0.14.0/resume-paused.legacy-routing-study.md`; unchanged.
7. `docs(resume-paused): record step 2 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (Step 2 back to Yes after the round 2 repair).

Unstaged, for the residual commit after the review: the transcript's round entries with the approved working-copy repairs, and `.vscode/settings.json` with the project word `nonbound`. The commit-plan checker reports the plan valid and ready.

### Writer response for step 2 resume-paused (round 3)

Writer response:

The round 2 finding is accepted and repaired, with no disagreement.

- [P2] Reads accounted before parsing: the accounting moved from the store's methods to the exact paths the store reads. `_accounted_paths` hands the unchanged `ReviewExchangeStore` an `ArtifactPaths` whose request, answer, tombstone, coordination and transcript entries are `_AccountedPath` objects, a `Path` subclass bound to the observation's read record. `read_bytes` records the path and the bytes it consumed before returning them; `read_text` decodes those same bytes through `io.TextIOWrapper` with the caller's encoding, errors and newline, the text-mode semantics of `open`, so no file is read twice. `with_segments` and `resolve` keep derived paths accounted, because `read_artifact` reads through the resolved path. A malformed envelope, a malformed coordination record or an undecodable transcript is therefore recorded before the parser or decoder rejects it.
- New regression test `test_rejected_reads_stay_accounted`, parametrized over a malformed orphan answer, a malformed coordination record and an invalid UTF-8 transcript: each snapshot is damaged, its exact reads equal the independent recorder's (answer; coordination twice; coordination three times then transcript), and its bytes equal the sizes of those files.
- Validation-only change outside the plan: three untouched groundhog args-file acceptance tests lost their CPU band tolerance and failed the round 3 speed walk; at the user's direction they were shortened in a separate commit group (lowered command-line budget, three short files, all assertions kept, one added precondition, its assertions moved into one helper to stay within the complexity limit). Please review that group as well.
- The validation plan's Step 2 section returns to `Yes` from the reviewer's round 2 rewrite, with the corrected accounting description and checks.
- Transcript, under the user's exceptions of 2026-11-18: my own round 2 request text wrote a code span with a trailing space on lines 1952 and 1981, which fails `MD038`, and the word "unopenable" on line 1978, which cSpell refuses. Only the inner space of those two spans was removed, and line 1978 now reads "a lock that cannot be opened". These working-copy edits join the transcript's residual commit.

### Reviewer focus for step 2 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-3 -->

## Round 3 by reviewer - Step 2

- Recorded: 2026-11-18T14:18:41+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 resume-paused (exchange 1) (round 3)

Baseline index tree: 38c0813a65e435707fd157987aface6b2b2ca510

Assessed index tree: 6dc383e4880a4f19f1fdf218ce5a9e11d3d08712

### Implementation check for step 2 resume-paused (exchange 1) (round 3)

Result:

Yes. Step 2 has been fully implemented.

The independent review confirms the four read-only modules and legacy routing study against the exact Step 2 plan. The carried round 2 finding is resolved: `_AccountedPath` records bytes before decoding or parsing, preserves accounting on resolved paths, and avoids a second content read. Independent recorder tests cover a malformed orphan answer, malformed coordination, and invalid UTF-8 transcript. The prior orphan-evidence and lock-failure repairs remain intact. No architecture, complexity, file-size or feature-integrity gap remains.

The separately disclosed groundhog test optimization preserves pass/fail cleanup, expanded-versus-inline equality and coverage-tail ordering. Its lowered budget and explicit over-budget assertion preserve the behavior under test while reducing fixture work.

Validation plan effects:

Polishing-only review metadata: added one independent round 3 confirmation paragraph within Step 2 of docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md. Retained the exact Yes sentence; no Missing work section remains. Other steps and document-level status are unchanged.

### Pre-repair mandatory checks and coverage for step 2 resume-paused (exchange 1) (round 3)

Requestor evidence: ghog day --full=speed --whole-suite exited 0 at 2026-11-18T14:08:41+01:00, with 6467 tests, 100% line coverage over tools, no failures, outliers or exclusions, and passing static checks. These are the requestor's reported results. The reviewer did not rerun the full walk, coverage, or optional focused evidence commands.

### Resolved validation set and sources for step 2 resume-paused (exchange 1) (round 3)

Current project default: ghog day --full=speed --whole-suite (source: project). Exact .review-validation marker check returned absent; prompt_workflow.bat scope day --full=speed returned this command. It matches the request's resolved validation set. Bound scope is whole, fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6.

### Resolver drift and direction for step 2 resume-paused (exchange 1) (round 3)

None. The current command and project source match the request.

### Repository state around validation for step 2 resume-paused (exchange 1) (round 3)

Baseline index 38c0813a65e435707fd157987aface6b2b2ca510 matched the request and retained manifest. Assessed index 6dc383e4880a4f19f1fdf218ce5a9e11d3d08712 differs only by the attributable two-line Step 2 validation metadata patch. The identical ordered 20-path validation-state comparison reports only that validation plan and `<index>`; both are explained by this permitted patch. Attribution returned attributable=true before staging. No other tracked or untracked change appeared in the compared set. Umbrella comparison is not applicable and unchanged. Pre-existing writer edits remain unstaged.

### Repair inventory for step 2 resume-paused (exchange 1) (round 3)

Repairs made:

- Polishing-only review metadata: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md; independent Step 2 confirmation, attributed and staged.
- No implementation or test repair; no substantive reviewer change.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`
- `docs/v0.14.0/review.code.v0.14.0.resume-paused.md`
- `tests/memory_filesystem.py`
- `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py`
- `tests/unit/tools/test_resume_paused_artifacts/__init__.py`
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py`
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py`
- `tests/unit/tools/test_resume_paused_models/__init__.py`
- `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py`
- `tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py`
- `tests/unit/tools/test_resume_paused_review/__init__.py`
- `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`
- `tests/unit/tools/test_resume_paused_routing/__init__.py`
- `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py`
- `tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py`
- `tools/resume_paused_artifacts.py`
- `tools/resume_paused_models.py`
- `tools/resume_paused_review.py`
- `tools/resume_paused_routing.py`

### Commit plan assessment for step 2 resume-paused (exchange 1) (round 3)

The independent commit-plan checker returned state=valid, ready=true, exit 0, with no diagnostics: 20 paths in seven ordered groups. Membership, dependency order and conventional subjects are accurate. Group 2 is the explicitly disclosed groundhog test optimization; group 1 is the disclosed transcript lint repair. The reviewer metadata paragraph remains within the existing final validation group. No a.commit edit is needed.

- docs(resume-paused): repair code transcript lint (1 path)
- test(groundhog): shorten args-file acceptance tests (1 path)
- feat(resume-paused): add pause routing models (8 paths)
- feat(resume-paused): read pause prompts and receipts (5 paths)
- feat(resume-paused): observe the saved exchange (3 paths)
- docs(resume-paused): add legacy routing study (1 path)
- docs(resume-paused): record step 2 validation (1 path)

### Findings and boundaries for step 2 resume-paused (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 resume-paused (exchange 1) (round 3)

No rework is requested. The advisory commit-ready recommendation leaves the human commit choice and all continuation actions with the requestor workflow.

### Decision rationale for step 2 resume-paused (exchange 1) (round 3)

All six readiness conditions pass: exact identity and request tree; complete Step 2; matching requestor validation and static coverage assessment; attributable staged scope; no unresolved findings; accurate independent commit plan. The coverage gate measures tools, including all four new production modules; the module test leaves cover the changed failure paths. No substantive repair was made. Commit-ready is advisory and does not authorize a commit.

### Final reviewer decision for step 2 resume-paused (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-3 -->

## Round 3 by human - Step 2 - human-confirmation

- Recorded: 2026-11-18T20:21:35+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Rework and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor - Step 2

- Recorded: 2026-11-18T20:26:22+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 resume-paused (round 4)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 2
Review round: 4

### Code review evidence for step 2 resume-paused (round 4)

request_index_tree: ba294f5ab976b9061df5bc0f82fe75f45d625e6b
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: test(groundhog): shorten args-file acceptance tests
group 1 path: tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py
group 2: feat(resume-paused): add pause routing models
group 2 path: tools/resume_paused_models.py
group 2 path: tools/resume_paused_routing.py
group 2 path: tests/unit/tools/test_resume_paused_models/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
group 2 path: tests/unit/tools/test_resume_paused_routing/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
group 3: feat(resume-paused): read pause prompts and receipts
group 3 path: tools/resume_paused_artifacts.py
group 3 path: tests/memory_filesystem.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
group 4: feat(resume-paused): observe the saved exchange
group 4 path: tools/resume_paused_review.py
group 4 path: tests/unit/tools/test_resume_paused_review/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 5: docs(resume-paused): add legacy routing study
group 5 path: docs/v0.14.0/resume-paused.legacy-routing-study.md
group 6: docs(resume-paused): record step 2 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/resume-paused.legacy-routing-study.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py
staged path: tests/unit/tools/test_resume_paused_artifacts/__init__.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py
staged path: tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py
staged path: tests/unit/tools/test_resume_paused_models/__init__.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_pbt.py
staged path: tests/unit/tools/test_resume_paused_models/test_resume_paused_models_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/__init__.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_routing/__init__.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_pbt.py
staged path: tests/unit/tools/test_resume_paused_routing/test_resume_paused_routing_tdd.py
staged path: tools/resume_paused_artifacts.py
staged path: tools/resume_paused_models.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_routing.py
```

### Validation scope for step 2 resume-paused (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 2 resume-paused (round 4)

Step 2 is fully implemented, as round 3 confirmed; round 4 only regroups `a.commit` so the review transcript leaves the staged groups for the residual commit. The implementation check records `Yes. Step 2 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T20:23:39+01:00 with `proof=speed reused=all`: groundhog reused the speed proof of the round 3 walk (2026-11-18T14:08:41+01:00, 6467 tests, no failure, no outlier, no exclusion), since no working-tree file changed, only the index.
- Static checks: the same proof covers `check.bat` (ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck, end-of-file).
- Coverage: 100% over `tools`, the four new modules included.
- Architecture, performance and feature integrity: unchanged since round 3, which found no gap.
- Commit plan: six groups, nineteen staged paths, no transcript; the checker reports it valid and ready.

### Implementation report for step 2 resume-paused (round 4)

Four read-only modules implement the Step 2 contracts of the consolidated design, beside the legacy routing study; round 3 moves the observer's read accounting to the read boundary.

- `tools/resume_paused_models.py`: shared values. `CanonicalRoot` compares checkout roots by Windows rules (case, `/` or `\`, repeated or trailing separators, the `\\?\` and `\\?\UNC\` prefixes) and refuses dot segments, trailing dots or spaces and reserved characters. `PromptDigest`, agent ids, full pane UUIDs, offset timestamps and single-line text checks complete it; the text check also refuses U+2028 and U+2029, which `str.splitlines` treats as line breaks.
- `tools/resume_paused_routing.py`: schema `resume-paused-routing` version 1. `SavedRouting` holds the pause identity, the observation, the resumed, requestor and reviewer targets and the exact exchange, and renders back to the same canonical JSON. A part recorded as `{"unknown": reason}` stays unresolved without failing the pause; a pair slot or the exchange may be `{"not_applicable": reason}`. Unrecognized keys, wrong types, other versions and contradictions between parts are errors.
- `tools/resume_paused_artifacts.py`: `read_checkout_snapshot` loads the home through `ReviewArtifactConfiguration.load`, validates the existing ignore bytes, reads the prompt's exact bytes and the receipt, and applies the resume-session state table with the exact paths read and their byte account, which now starts with the `.review-artifacts.ini` declaration whenever the load reads it, including when the declaration is refused. Receipts of schemas 1, 2 and 3 parse. Routing is read only from one top-level block fenced as `` ```json resume-paused-routing ``; the readable table headed `| Routing item | Value |` is rendered from that object and must equal the rendering when present.
- `tools/resume_paused_review.py`: `observe_saved_exchange(configuration, review_configuration, exchange, wall_clock)` takes the nonblocking `observe_transition` lock first and classifies through `ReviewExchangeObserver` and `current_request_occurrence`, with or without a coordination record. Only an empty artifact set is not live; a held lock or a record changing between the two probes is busy; orphan requests and answers keep their abandoned states and a tombstone its interrupted state; another occurrence, round, document, umbrella or step is a changed selection; invalid evidence and lock entry, acquisition or exit failures are damaged. The unchanged `ReviewExchangeStore` reads through `_AccountedPath` objects, a `Path` subclass that records each consumed byte count where the bytes are read and decodes text from those bytes, so the snapshot returns every exact path in order with its bytes, including reads that parsing or decoding then rejects. The caller supplies the review configuration, loaded once per checkout as the status collector does.
- `docs/v0.14.0/resume-paused.legacy-routing-study.md`: unchanged since round 1.
- Tests: one leaf per module. Read-only proofs compare whole checkout trees before and after each read and make every home preparation, migration, review-core construction and filesystem mutation fail. An independent recorder of `Path.read_text` and `Path.read_bytes` checks both read accounts, on success and on rejected evidence. A local replay of the installed launcher's heading and field readers, copied without importing senv, checks the prompt and receipt grammar.

Points for the reviewer's attention:

- The observer's signature gained the `review_configuration` argument in round 2; it has no caller yet. Its four coordination reads are reported: two stability probes, the adapter's read (it needs the record's policy before constructing the observer) and the observer's own.
- `_AccountedPath.read_text` reproduces `Path.read_text` through `io.TextIOWrapper` over the accounted bytes, with the same encoding, errors and newline arguments; `resolve` is overridden as well as `with_segments` so a resolved path stays accounted under any `resolve` implementation.
- The neutral `FamilyPolicy` passed when no coordination record exists is never consulted by the observer, which compares a policy only against a record.
- Interpretation kept from round 1: "unknown routing fields" means fields recorded as `{"unknown": reason}`; unrecognized keys stay errors.
- Contracts this step fixes for later steps: the routing fence line and table header (Step 3), and the schema 3 receipt fields `Launch id` (32 lowercase hexadecimal characters), `Receiving pane` and `Assignment binding` (Step 4).
- Deviations from the planned file list (round 1): the routing schema module and the per-module test leaves split for the 650-line ceiling, and `tests/memory_filesystem.py` registers the artifact and review leaves. Line counts: `tools/resume_paused_artifacts.py` 578, `tools/resume_paused_review.py` 346.
- Transcript repairs, each under its own user exception of 2026-11-18: twelve bare `__init__.py` paths of the Step 1 entries wrapped in code spans; the round 1 answer's numbered lines 1807-1812 lost their leading bullet to clear `MD029`; my round 2 lines 1952, 1978 and 1981 were corrected for `MD038` and one cSpell word. Since round 4 none of them is in `a.commit`: the whole transcript stays unstaged for the residual commit, with the unstaged `.vscode/settings.json` word `nonbound`, because the batch commit re-adds a listed path whole and would otherwise carry the appended rounds under the lint-repair message.
- Outside the Step 2 plan, at the user's direction on 2026-11-18: the round 3 speed walk failed only on the CPU lifecycle budget of the three tests in `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py`, untouched by this step (0.11 to 0.16 s against the 0.1 s ceiling, band tolerance lost after three runs above it, reproduced in focus). A pyinstrument profile put most of the call in resolving the 61-file sentinel group. The tests now lower `args_file.COMMAND_LINE_BUDGET` to 100 and use three short files; a new precondition asserts that the expanded command exceeds the lowered budget, and every earlier assertion is kept. This is its own commit group, `test(groundhog): shorten args-file acceptance tests`, now group 1.
- `rg` is not available in the shell used; the contract inspection used the equivalent Grep search.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step2.journal.md` and `.reviews/a.resume-paused.step2.handoff.md`.

### Change summary for step 2 resume-paused (round 4)

Nineteen staged paths in six `a.commit` groups; round 4 removes the former transcript group and changes nothing else.

1. `test(groundhog): shorten args-file acceptance tests`: `tests/unit/tools/test_groundhog_acceptance_groups/test_groundhog_acceptance_group_args_file_tdd.py` (outside the Step 2 plan, at the user's direction).
2. `feat(resume-paused): add pause routing models`: `tools/resume_paused_models.py`, `tools/resume_paused_routing.py`, and the `tests/unit/tools/test_resume_paused_models` and `tests/unit/tools/test_resume_paused_routing` packages.
3. `feat(resume-paused): read pause prompts and receipts`: `tools/resume_paused_artifacts.py`, `tests/memory_filesystem.py`, and the `tests/unit/tools/test_resume_paused_artifacts` package.
4. `feat(resume-paused): observe the saved exchange`: `tools/resume_paused_review.py` and the `tests/unit/tools/test_resume_paused_review` package.
5. `docs(resume-paused): add legacy routing study`: `docs/v0.14.0/resume-paused.legacy-routing-study.md`.
6. `docs(resume-paused): record step 2 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (with the reviewer's round 3 confirmation paragraph).

Unstaged, for the residual commit after the review: the code review transcript, with its twelve-line `MD050` repair, the approved round 1 and round 2 line repairs and every appended round, and `.vscode/settings.json` with the project word `nonbound`. The commit-plan checker reports the plan valid and ready.

### Writer response for step 2 resume-paused (round 4)

Writer response:

Round 3 recommended commit-ready with no finding, and its polishing paragraph in the Step 2 validation section is kept unchanged. The human chose "Rework and review again" at that gate for one commit-grouping change, made by the writer:

- `pw code-review-commit` re-adds each listed path whole, so the former group 1, which listed the code review transcript, would have committed all three appended review rounds under its "repair code transcript lint" message. That group is removed and the remaining groups are renumbered. The transcript is no longer staged: its working copy, with the twelve-line `MD050` repair and the approved line repairs of rounds 1 and 2, goes entirely to the residual commit that retains this exchange, together with `.vscode/settings.json` and its project word `nonbound`.
- No code, test or validation-plan content changed since round 3. The requestor-owned speed walk was rerun for the regrouped tree.

### Reviewer focus for step 2 resume-paused (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-4 -->

## Round 4 by reviewer - Step 2

- Recorded: 2026-11-18T20:31:12+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 resume-paused (exchange 1) (round 4)

Baseline index tree: ba294f5ab976b9061df5bc0f82fe75f45d625e6b

Assessed index tree: ba294f5ab976b9061df5bc0f82fe75f45d625e6b

### Implementation check for step 2 resume-paused (exchange 1) (round 4)

Result:

Yes. Step 2 has been fully implemented.

The exact plan and Step 2 validation rows remain satisfied. The four read-only modules, per-module tests, memory-filesystem registration and legacy routing study are unchanged from the independently accepted round 3 state. The staged-tree comparison reports only the transcript difference, and the retained file-digest comparison confirms unchanged implementation, tests, study and validation-plan content. The read-accounting, orphan-evidence and lock-error findings remain resolved. No new architecture, performance, coverage or feature-integrity gap is introduced by removing the transcript from the commit groups. Later steps remain outside this assessment.

Validation plan effects:

No edit was needed. The Step 2 status remains exactly `Yes. Step 2 has been fully implemented.`, with its round 3 reviewer confirmation and no Missing work section. All other step rows and the document-level status are unchanged. Umbrella: not applicable.

### Pre-repair mandatory checks and coverage for step 2 resume-paused (exchange 1) (round 4)

No reviewer repair or test command was run. The requestor reports `ghog day --full=speed --whole-suite` exit 0 at 2026-11-18T20:23:39+01:00 with `proof=speed reused=all`, reusing the round 3 result of 6467 passing tests, no failures, no duration outliers or exclusions, and 100% line coverage over `tools`. The coverage configuration still measures `tools`; the four production modules are inside that scope. Static coverage assessment from round 3 remains applicable because the code and tests are identical.

### Resolved validation set and sources for step 2 resume-paused (exchange 1) (round 4)

The `.review-validation` marker was sampled and is absent. The current project resolver, `prompt_workflow.bat scope day --full=speed`, returns `ghog day --full=speed --whole-suite`, exactly matching the request's project source. The core-bound scope is whole, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The reviewer did not repeat requestor validation or measure coverage.

### Resolver drift and direction for step 2 resume-paused (exchange 1) (round 4)

None. The command and source remain unchanged.

### Repository state around validation for step 2 resume-paused (exchange 1) (round 4)

The request-time, baseline and assessed index trees all equal `ba294f5ab976b9061df5bc0f82fe75f45d625e6b`. The round 4 before/after validation comparison is acceptable with no tracked, untracked or ignored changes. The umbrella comparison is not applicable and unchanged. Comparing round 3's assessed tree with this tree reports only the review transcript; the broader retained-file comparison reports only that transcript and `<index>`, as expected from transcript publication and the disclosed unstaging. All nineteen current staged paths retain the accepted content. The reviewer changed no tracked file and staged nothing.

### Repair inventory for step 2 resume-paused (exchange 1) (round 4)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 resume-paused (exchange 1) (round 4)

The independent `commit-plan-check.bat --format json` run exits 0: state `valid`, ready `true`, nineteen staged paths, six ordered groups, no diagnostics. Reading `a.commit` confirms these subjects and dependency order:

1. `test(groundhog): shorten args-file acceptance tests`
2. `feat(resume-paused): add pause routing models`
3. `feat(resume-paused): read pause prompts and receipts`
4. `feat(resume-paused): observe the saved exchange`
5. `docs(resume-paused): add legacy routing study`
6. `docs(resume-paused): record step 2 validation`

The requestor's removal of the transcript group addresses the human-selected regrouping: the batch commit will no longer re-add the whole transcript under a lint-repair subject. The transcript and disclosed spelling setting remain reserved for the requestor's residual commit. The independent groundhog test optimization remains in its own first group. Group membership, order, scopes and conventional subjects are accurate. The reviewer made no grouping change.

### Findings and boundaries for step 2 resume-paused (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 resume-paused (exchange 1) (round 4)

No implementation rework is requested. Present the advisory recommendation at the human convergence gate. The requestor retains responsibility for the commit choice and the disclosed residual transcript/settings commit.

### Decision rationale for step 2 resume-paused (exchange 1) (round 4)

Recommend `commit-ready` for round 4, occurrence 1. All six readiness results pass: exact identity and index, complete Step 2 implementation, matching validation evidence and static coverage assessment, attributable staged scope, no unresolved current or carried findings, and an independently valid commit plan. No literal Human guidance block is present. No substantive repair, polishing edit or staging action was made by the reviewer. This recommendation does not authorize a commit.

### Final reviewer decision for step 2 resume-paused (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-4 -->

## Round 4 by human - Step 2 - human-confirmation

- Recorded: 2026-11-18T22:01:57+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
