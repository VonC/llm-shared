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

## Round 1 by requestor - Step 3

- Recorded: 2026-11-19T09:10:12+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 3
- Outcome: request

### Review identity for step 3 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 resume-paused (round 1)

request_index_tree: 23f75e4aabf2eb923115c6e56a6d765eb06e85f0
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(pause): write saved routing as one JSON block
group 1 path: instructions/pause-session.md
group 1 path: templates/pause-session.template.md
group 2: feat(session): accept schema 3 resume receipts
group 2 path: templates/resume-session.template.md
group 2 path: instructions/status-session.md
group 2 path: templates/status-session.template.md
group 2 path: instructions/list-session.md
group 2 path: templates/list-session.template.md
group 3: test(resume-paused): check the pause routing contract
group 3 path: tests/unit/tools/test_resume_paused_pause_contract/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py
group 4: docs(resume-paused): record step 3 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: instructions/list-session.md
staged path: instructions/pause-session.md
staged path: instructions/status-session.md
staged path: templates/list-session.template.md
staged path: templates/pause-session.template.md
staged path: templates/resume-session.template.md
staged path: templates/status-session.template.md
staged path: tests/unit/tools/test_resume_paused_pause_contract/__init__.py
staged path: tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py
```

### Validation scope for step 3 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 3 resume-paused (round 1)

Step 3 is fully implemented: new pauses write routing as one `resume-paused-routing` JSON block followed by the table rendered from it, the replacement guard follows requirement Q29=A, and the receipt template, status-session and list-session read receipt schemas 1 to 3. The implementation check recorded `Yes. Step 3 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-19T09:09:21+01:00, 6531 tests, no failure, no outlier, no exclusion; slowest call 0.74 s. The new contract leaf failed first (50 failures before the documents changed), then passed with the Step 2 artifact and routing leaves and the interactive-menu pointer test (347 tests in focus).
- Static checks: the same walk's `check.bat` passes ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `markdown-check.bat --root .` exits 0 and `spellcheck.bat check` reports no unknown word on the eight changed Markdown files.
- Coverage: 100% over `tools`; no `tools` file changes in this step, and every top-level helper of the new test module is referenced.
- Architecture: workflow policy stays in the canonical instructions and templates, provider adapters stay redirects, and no schema rule is duplicated in code: the tests derive keys, rows and cells from the Step 2 renderer and parsers.
- Performance: no production code changes; the test helpers read each shipped document once per session and scan it linearly.
- Feature integrity: legacy prompts with a prose table or no routing still parse, schema 1 and 2 receipts still classify, manual resumes still write schema 2, and the prompt heading, `Session role` and the three receipt lines the installed launcher reads are preserved.

### Implementation report for step 3 resume-paused (round 1)

Step 3 changes seven canonical session documents and adds one contract-test leaf. No production Python module changes; the Step 2 parsers and renderer are the executable contract the documents are tested against.

- `instructions/pause-session.md`, routing capture: identities come from the `tuios list-agents --all-sessions --json` records. The full 36-character `window_id` is the pane UUID (the table view prints 8 characters), the `session` string is the TUIOS session, `name` is a supplementary label and a non-empty `agent_session_id` is supporting evidence. Historical authorship and the saved role stay apart from intended assignments, and a session holding a live exchange role saves `requestor` or `reviewer`. Missing evidence is an explicit `{"unknown": "<reason>"}`, and the instruction forbids a routing question, contacting the counterpart and launching `resume_paused`.
- `instructions/pause-session.md`, new subsections "Write the routing JSON block" and "Render the readable routing table": the exact fence line, every key of schema `resume-paused-routing` version 1, the single-agent `{"not_applicable": "<reason>"}` rule (both pair slots and the exchange, all or none), the pairing rule (the resumed target written identically in its pair slot), the checkout spelling and single-line rules. The thirteen table rows follow, with one code span per accepted cell form and the `none` and `not applicable` substitutions. A worked paired code-review example, generated by the Step 2 `render_routing_section`, is embedded verbatim. A second block or table, or a differing cell, is documented as a bulk routing error that leaves manual resume intact.
- `instructions/pause-session.md`, replacement guard (requirement Q29=A): a decision table asks before replacing an unused or new prompt when its agent id differs or is missing, or when its known pausing pane or saved role differs even with the same agent id. The old prompt's pane and role come from its routing block (`pause.pane`, `pause.session_role`), or for a legacy prompt from a `Session role` line holding exactly one role token. Panes compare by full UUID and session string, never label; unknown values alone are no difference; legacy prompts keep the agent-id comparison; declining preserves the old checkpoint; the guard is pause-time only.
- `instructions/pause-session.md`, publishing: the `- Session role:` line holds the routing's `pause.session_role` token alone (Step 2 refuses a contradicting role token), and the read-back checks the block and every cell.
- `templates/pause-session.template.md`: the prose routing bullets and the six-column table become the JSON skeleton (every schema key) and the thirteen-row table skeleton; the `Session role` placeholder asks for one token.
- `templates/resume-session.template.md`: every schema 2 line stays; `Schema` reads 2 for a manual resume or 3 for a marked resume, and `Launch id`, `Receiving pane` and `Assignment binding` follow as marked-resume-only lines a manual resume omits. The meaning section states that schema 3 only adds non-secret bindings.
- `instructions/status-session.md` and its template: receipts of schemas 1 to 3 with exactly their own lines, classified by `Prompt`, `SHA-256` and `Project root`; an unprocessed prompt's saved routing state (resolved, unresolved, error, table only or none) is reported from the JSON block only, without checking live panes; a schema 3 receipt's receiving pane is named.
- `instructions/list-session.md` and its template: the same receipt schemas, the receiving pane of a schema 3 receipt in the disk check result, and an invalid receipt reported as `cannot check`.
- `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py` (new, 439 lines) and its package file: the example equals the rendering of its own JSON; every rendered cell of five routing variants matches a documented row form, in order; the template skeleton names every schema key and the rendered rows; prompts filled from the template parse under Step 2 (resolved, unresolved and single-agent routing), a contradicting header role is an error, and prose-table and routing-free legacy prompts stay readable; receipts of schemas 1 to 3 filled from the template parse and consume the prompt; the launcher's heading, `Session role`, `Prompt`, `SHA-256` and `Project root` readers are replayed from local fixtures; the capture, guard and reader rules are pinned; the six adapters of each session command stay canonical redirects.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: Step 3 recorded as fully implemented; the document status stays not implemented for Steps 4 to 8.

Points for the reviewer's attention:

- `instructions/resume-session.md` is unchanged, as the plan assigns its schema 3 reader and writer to Step 4. Until then a schema 3 receipt stops the worktree's resume-session, the documented fail-closed mixed-install behavior; manual resumes keep writing schema 2.
- No routing rendering tool is added: the plan's file list has none and keeps schema parsing in the Step 2 modules. The pausing agent writes the table by the documented grammar, and the contract test ties that grammar to the renderer.
- status-session reporting the saved routing state is an alignment of the manual reader beyond receipt schemas; it reads the saved record only.
- The worktree's `pause-session.md` predates main's session-journal tool section; this step leaves that section as it is in the worktree.
- `rg` is not available in the shell used, so the contract inspection used the equivalent Grep search over the seven documents.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step3.journal.md` and `.reviews/a.resume-paused.step3.handoff.md`.

### Change summary for step 3 resume-paused (round 1)

Ten staged paths in four `a.commit` groups, in this order:

1. `feat(pause): write saved routing as one JSON block`: `instructions/pause-session.md`, `templates/pause-session.template.md`.
2. `feat(session): accept schema 3 resume receipts`: `templates/resume-session.template.md`, `instructions/status-session.md`, `templates/status-session.template.md`, `instructions/list-session.md`, `templates/list-session.template.md`.
3. `test(resume-paused): check the pause routing contract`: the `tests/unit/tools/test_resume_paused_pause_contract` package (package file and tdd file).
4. `docs(resume-paused): record step 3 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and stays out of `a.commit`; it goes to the residual commit.

### Writer response for step 3 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement.

### Reviewer focus for step 3 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-11-19T09:17:27+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 resume-paused (exchange 1) (round 1)

Baseline index tree: 23f75e4aabf2eb923115c6e56a6d765eb06e85f0

Assessed index tree: 6be37d4e37289c37913a4ddaeb5c506b7b084b09

### Implementation check for step 3 resume-paused (exchange 1) (round 1)

Result:

No. Step 3 has NOT been fully implemented.

Routing capture, JSON/table agreement, replacement guarding, additive receipts and status/list readers match the step. Pause's own schema 3 receipt check is missing. The explicit completion criterion at plan line 353 requires this in Step 3, independently of the resume command deferred to Step 4. No production code changes or DDD/Hexagonal violations were identified; no new runtime performance issue was found. Static coverage inspection finds the pause receipt contract untested.

Validation plan effects:

Updated only Step 3 in docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md: exact No verdict, explanation, two concrete Missing work bullets, coverage limitation and feature-integrity consequence. Other steps and document-level status are unchanged. This is review metadata, not an implementation repair. Evidence attribution reported attributable=true; the exact reviewed patch was staged.

### Pre-repair mandatory checks and coverage for step 3 resume-paused (exchange 1) (round 1)

Requestor evidence: ghog day --full=speed --whole-suite exited 0 at 2026-11-19T09:09:21+01:00, 6531 tests, 100% tools coverage, no duration exclusion, slowest call 0.74 seconds. The request also reports 347 focused tests, static checks, Markdown and spelling checks green. These are requestor results, not independently repeated tests. Reviewer used staged-document and test inspection; no ghog check, affected test run, full walk or coverage execution was needed. The tools coverage gate does not measure Markdown behavior or test code; the new test module's helpers are referenced, but the pause receipt contract is absent.

### Resolved validation set and sources for step 3 resume-paused (exchange 1) (round 1)

Current resolver contract was inspected in tools/code_review_validation.py. The exact .review-validation path is absent, so the built-in project command ghog day --full=speed is completed with the bound whole-suite selector. No plan or request additions are declared. Resolved command: ghog day --full=speed --whole-suite; sources: project. This matches the request's parsed resolved_validation_set and scope fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6. The reviewer did not execute the requestor validation set.

### Resolver drift and direction for step 3 resume-paused (exchange 1) (round 1)

None. No added, removed or changed command/source was found between the request and current resolver contract.

### Repository state around validation for step 3 resume-paused (exchange 1) (round 1)

Baseline index 23f75e4aabf2eb923115c6e56a6d765eb06e85f0 matched the request. Assessed index after staging review metadata: 6be37d4e37289c37913a4ddaeb5c506b7b084b09. Umbrella comparison: applicable=false, changed=false. The validation-state comparator returned acceptable=false solely because the tracked validation plan changed. Diff inspection confines that change to Step 3, the explicitly permitted metadata exception; all nine other captured paths are unchanged, with no untracked or ignored differences. Attribute-reviewer-patch returned attributable=true. No implementation/test repair or validation-command side effect occurred.

### Repair inventory for step 3 resume-paused (exchange 1) (round 1)

Repairs made:

- Review metadata only: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md. Classified as polishing-only for repair accounting; it records the No assessment and concrete missing work, without changing implementation, tests or commit grouping.
- No substantive repair. No literal Human guidance block authorizes implementation repair, so the request's generic repair wording was not applied.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
- instructions/list-session.md
- instructions/pause-session.md
- instructions/status-session.md
- templates/list-session.template.md
- templates/pause-session.template.md
- templates/resume-session.template.md
- templates/status-session.template.md
- `tests/unit/tools/test_resume_paused_pause_contract/__init__.py`
- tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py

### Commit plan assessment for step 3 resume-paused (exchange 1) (round 1)

Independent commit-plan-check.bat --format json exited 0: state=valid, ready=true, diagnostics=[]. All ten staged paths are covered exactly once in four ordered groups: feat(pause): write saved routing as one JSON block; feat(session): accept schema 3 resume receipts; test(resume-paused): check the pause routing contract; docs(resume-paused): record step 3 validation. The group order and conventional subjects match the staged work. The metadata update adds no path and changes no grouping. a.commit remains accurate and unchanged. Mechanical readiness does not establish step completeness or authorize a commit. Full checker JSON is retained in .reviews/a.resume-paused.step3.tmp.r1.commit-plan.json.

### Findings and boundaries for step 3 resume-paused (exchange 1) (round 1)

Unresolved findings:

- P2: Make pause's existing-prompt receipt check schema 3 aware. instructions/pause-session.md:77-79 delegates receipt classification to resume-session.md's state table; the linked rules at instructions/resume-session.md:21-29 explicitly accept only schemas 1 and 2. With an otherwise valid schema 3 receipt from a marked resume, that route can reject the receipt and stop a subsequent pause instead of classifying the checkpoint as used or new. The plan at line 353 explicitly includes pause-session among Step 3's schema 3 readers, so Step 4's intentional resume deferral does not cover this gap. Point pause at the schema-aware status reader or state equivalent receipt validation/classification locally, preserving malformed-receipt diagnostics and the unused/new replacement guard. Extend tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py:405-437: its pause entries only assert routing publication, while schema assertions cover status/list. Pin pause's schema 3 matching, different-digest and malformed-receipt behavior in a contract test that fails against the current instruction.

Boundary-crossing work:

- None. Keep the resume command's schema 3 reader/writer in Step 4. No umbrella change, implementation repair, counterpart contact or commit was made.

### Writer instructions for step 3 resume-paused (exchange 1) (round 1)

Address the pause reader and its contract test within Step 3, following Missing work for Step 3 in the validation plan. Preserve schemas 1/2, classify schema 3 by Prompt/SHA-256/Project root, reject malformed receipts and retain the existing replacement guard. Validate through the writer-owned required checks, refresh the implementation-check and request evidence, and submit a new review round. No product decision or Step 4 implementation is required.

### Decision rationale for step 3 resume-paused (exchange 1) (round 1)

Changes requested. Readiness floor: exact identity PASS; implementation completeness FAIL (pause reader); validation/coverage FAIL (missing behavioral contract, despite reported green suite); staged attribution PASS; unresolved findings FAIL (one); commit plan PASS. The reviewer made no substantive repair. This answer is advisory and authorizes no commit.

### Final reviewer decision for step 3 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-11-19T15:29:07+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: request

### Review identity for step 3 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 resume-paused (round 2)

request_index_tree: 229f65878584b25bd7186666c64a24abcaae8d4f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(pause): write saved routing as one JSON block
group 1 path: instructions/pause-session.md
group 1 path: templates/pause-session.template.md
group 2: feat(session): accept schema 3 resume receipts
group 2 path: templates/resume-session.template.md
group 2 path: instructions/status-session.md
group 2 path: templates/status-session.template.md
group 2 path: instructions/list-session.md
group 2 path: templates/list-session.template.md
group 3: test(resume-paused): check the pause routing contract
group 3 path: tests/unit/tools/test_resume_paused_pause_contract/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py
group 4: docs(resume-paused): record step 3 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: instructions/list-session.md
staged path: instructions/pause-session.md
staged path: instructions/status-session.md
staged path: templates/list-session.template.md
staged path: templates/pause-session.template.md
staged path: templates/resume-session.template.md
staged path: templates/status-session.template.md
staged path: tests/unit/tools/test_resume_paused_pause_contract/__init__.py
staged path: tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py
```

### Validation scope for step 3 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 3 resume-paused (round 2)

Step 3 is fully implemented after the round 1 repair: new pauses write routing as one `resume-paused-routing` JSON block followed by the table rendered from it, the replacement guard follows requirement Q29=A, and the receipt template, pause's existing-prompt receipt check, status-session and list-session all read receipt schemas 1 to 3. The implementation check again records `Yes. Step 3 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-19T15:28:09+01:00, 6540 tests, no failure, no outlier, no exclusion; slowest call 0.31 s. The four new pause receipt guard rules failed against the earlier instruction (`ghog single` fail=4) and pass after the repair; the executable schema 3 cases (used, new since previous use, three malformed forms) pass.
- Static checks: the same walk's `check.bat` passes ty, pyright, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check. The first round 2 walk stopped on `MD050` at transcript line 2807 (the round 1 answer's bare `__init__.py` path); that single line was repaired under the user's explicit exception before the green walk. `spellcheck.bat check` reports no unknown word on the repaired files.
- Coverage: 100% over `tools`; no `tools` file changes in this step, and every top-level helper of the test module is referenced.
- Architecture: workflow policy stays in the canonical instructions and templates, provider adapters stay redirects, and the tests derive keys, rows, cells and receipt outcomes from the Step 2 renderer and parsers.
- Performance: no production code changes; the test helpers read each shipped document once per session and scan it linearly.
- Feature integrity: legacy prompts and schema 1 and 2 receipts stay readable, a schema 3 receipt no longer stops a later pause, manual resumes still write schema 2, and the launcher's prompt and receipt lines are preserved. `resume-session.md` keeps its Step 4 assignment.

### Implementation report for step 3 resume-paused (round 2)

Step 3 changes seven canonical session documents and adds one contract-test leaf. No production Python module changes; the Step 2 parsers and renderer are the executable contract the documents are tested against.

- `instructions/pause-session.md`, routing capture: identities come from the `tuios list-agents --all-sessions --json` records. The full 36-character `window_id` is the pane UUID (the table view prints 8 characters), the `session` string is the TUIOS session, `name` is a supplementary label and a non-empty `agent_session_id` is supporting evidence. Historical authorship and the saved role stay apart from intended assignments, and a session holding a live exchange role saves `requestor` or `reviewer`. Missing evidence is an explicit `{"unknown": "<reason>"}`, and the instruction forbids a routing question, contacting the counterpart and launching `resume_paused`.
- `instructions/pause-session.md`, new subsections "Write the routing JSON block" and "Render the readable routing table": the exact fence line, every key of schema `resume-paused-routing` version 1, the single-agent `{"not_applicable": "<reason>"}` rule (both pair slots and the exchange, all or none), the pairing rule (the resumed target written identically in its pair slot), the checkout spelling and single-line rules. The thirteen table rows follow, with one code span per accepted cell form and the `none` and `not applicable` substitutions. A worked paired code-review example, generated by the Step 2 `render_routing_section`, is embedded verbatim. A second block or table, or a differing cell, is documented as a bulk routing error that leaves manual resume intact.
- `instructions/pause-session.md`, replacement guard (requirement Q29=A): a decision table asks before replacing an unused or new prompt when its agent id differs or is missing, or when its known pausing pane or saved role differs even with the same agent id. The old prompt's pane and role come from its routing block (`pause.pane`, `pause.session_role`), or for a legacy prompt from a `Session role` line holding exactly one role token. Panes compare by full UUID and session string, never label; unknown values alone are no difference; legacy prompts keep the agent-id comparison; declining preserves the old checkpoint; the guard is pause-time only.
- `instructions/pause-session.md`, existing-prompt receipt check (round 1 repair): before the guard, pause accepts the old prompt's receipt in schema 1, 2 or 3, as status-session does, and classifies it by its `Prompt`, `SHA-256` and `Project root` lines, never by its schema. A valid receipt for the prompt's exact bytes makes it used, one for other bytes makes it new since previous use, and a receipt that misses a line of its schema, carries another one or names another schema is malformed: the pause reports the diagnostic and stops without replacing the prompt. The link to the resume state table stays for the other states; `resume-session.md` itself still waits for Step 4.
- `instructions/pause-session.md`, publishing: the `- Session role:` line holds the routing's `pause.session_role` token alone (Step 2 refuses a contradicting role token), and the read-back checks the block and every cell.
- `templates/pause-session.template.md`: the prose routing bullets and the six-column table become the JSON skeleton (every schema key) and the thirteen-row table skeleton; the `Session role` placeholder asks for one token.
- `templates/resume-session.template.md`: every schema 2 line stays; `Schema` reads 2 for a manual resume or 3 for a marked resume, and `Launch id`, `Receiving pane` and `Assignment binding` follow as marked-resume-only lines a manual resume omits. The meaning section states that schema 3 only adds non-secret bindings.
- `instructions/status-session.md` and its template: receipts of schemas 1 to 3 with exactly their own lines, classified by `Prompt`, `SHA-256` and `Project root`; an unprocessed prompt's saved routing state (resolved, unresolved, error, table only or none) is reported from the JSON block only, without checking live panes; a schema 3 receipt's receiving pane is named.
- `instructions/list-session.md` and its template: the same receipt schemas, the receiving pane of a schema 3 receipt in the disk check result, and an invalid receipt reported as `cannot check`.
- `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py` (new) and its package file: round 1 adds four guard rules pinning pause's schema 1 to 3 receipt reader (they failed against the earlier instruction) and executable cases where a schema 3 receipt filled from the template makes the old prompt used for the same bytes and new for other bytes, while a missing `Launch id`, schema 2 carrying the marked lines, and schema 4 are malformed. Earlier checks: the example equals the rendering of its own JSON; every rendered cell of five routing variants matches a documented row form, in order; the template skeleton names every schema key and the rendered rows; prompts filled from the template parse under Step 2 (resolved, unresolved and single-agent routing), a contradicting header role is an error, and prose-table and routing-free legacy prompts stay readable; receipts of schemas 1 to 3 filled from the template parse and consume the prompt; the launcher's heading, `Session role`, `Prompt`, `SHA-256` and `Project root` readers are replayed from local fixtures; the capture, guard and reader rules are pinned; the six adapters of each session command stay canonical redirects.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: Step 3 recorded as fully implemented; the document status stays not implemented for Steps 4 to 8.

Points for the reviewer's attention:

- `instructions/resume-session.md` is unchanged, as the plan assigns its schema 3 reader and writer to Step 4. Until then a schema 3 receipt stops the worktree's resume-session, the documented fail-closed mixed-install behavior; manual resumes keep writing schema 2.
- No routing rendering tool is added: the plan's file list has none and keeps schema parsing in the Step 2 modules. The pausing agent writes the table by the documented grammar, and the contract test ties that grammar to the renderer.
- status-session reporting the saved routing state is an alignment of the manual reader beyond receipt schemas; it reads the saved record only.
- The worktree's `pause-session.md` predates main's session-journal tool section; this step leaves that section as it is in the worktree.
- `rg` is not available in the shell used, so the contract inspection used the equivalent Grep search over the seven documents.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step3.journal.md` and `.reviews/a.resume-paused.step3.handoff.md`.

### Change summary for step 3 resume-paused (round 2)

Ten staged paths in four `a.commit` groups, in this order:

1. `feat(pause): write saved routing as one JSON block`: `instructions/pause-session.md`, `templates/pause-session.template.md`.
2. `feat(session): accept schema 3 resume receipts`: `templates/resume-session.template.md`, `instructions/status-session.md`, `templates/status-session.template.md`, `instructions/list-session.md`, `templates/list-session.template.md`.
3. `test(resume-paused): check the pause routing contract`: the `tests/unit/tools/test_resume_paused_pause_contract` package (package file and tdd file).
4. `docs(resume-paused): record step 3 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and stays out of `a.commit`; it goes to the residual commit.

### Writer response for step 3 resume-paused (round 2)

Writer response:

Round 1 finding P2 (pause's existing-prompt receipt check followed the schema 1/2-only resume state table): accepted and repaired as the reviewer directed.

- `instructions/pause-session.md`: the replacement guard's receipt check now accepts schemas 1, 2 and 3 as status-session does, classifies by `Prompt`, `SHA-256` and `Project root`, and reports a malformed receipt and stops without replacing the prompt. The resume state table link stays; the resume command's own schema 3 reader and writer remain in Step 4.
- `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py`: four guard rules pin the new reader and failed against the earlier instruction (`ghog single` fail=4) before passing; executable cases cover a schema 3 receipt for the same bytes (used), other bytes (new since previous use) and three malformed forms.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: the reviewer's staged No verdict and its two Missing work bullets are resolved; the writer's implementation check restores `Yes. Step 3 has been fully implemented.`, removes the Missing work section and keeps the reviewer's coverage and feature-integrity points as resolved statements. This follows the repair, not a disagreement.
- `a.commit`: membership, order and subjects are unchanged; groups 1 and 3 each gain one What bullet for the repair. The checker reports valid and ready.

- Transcript: the round 1 answer's "Paths staged" bullet with the bare `__init__.py` path made markdownlint report `MD050` at transcript line 2807 and failed the round 2 speed walk. Under the user's explicit exception for that one line, the path is now wrapped in a code span; no other transcript line changed, and the transcript stays out of `a.commit` for the residual commit. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis.

No disagreement.

### Reviewer focus for step 3 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-11-19T15:34:24+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 resume-paused (exchange 1) (round 2)

Baseline index tree: 229f65878584b25bd7186666c64a24abcaae8d4f

Assessed index tree: 229f65878584b25bd7186666c64a24abcaae8d4f

### Implementation check for step 3 resume-paused (exchange 1) (round 2)

Result:

Yes. Step 3 has been fully implemented.

Independent review confirms the routing JSON/table contract, replacement guard, manual reader compatibility and contract tests meet the named step. The carried P2 finding is resolved: pause explicitly accepts schema 1, 2 and 3 receipts independently of the deferred resume reader, classifies by prompt identity and digest, and stops on malformed receipts. Four instruction guards and executable matching/different-digest and malformed-schema cases cover that gap. Architecture, performance, static coverage and feature-integrity checks reveal no further issue. Step 4's resume command remains outside this step.

Validation plan effects:

The existing Step 3 Yes verdict and removal of its missing-work section are accurate after the writer's repair. No reviewer edit was needed. No other step or umbrella row changed.

### Pre-repair mandatory checks and coverage for step 3 resume-paused (exchange 1) (round 2)

No reviewer repair or test command was performed in round 2. Requestor evidence reports `ghog day --full=speed --whole-suite` exit 0 at 2026-11-19T15:28:09+01:00: 6540 tests, no failures, outliers or exclusions, 100% coverage over `tools`, and green static/Markdown checks. The four receipt guards reportedly failed before the instruction repair. This is requestor execution evidence, not an independent reviewer rerun. Static review found no coverage gap; this step changes no production Python.

### Resolved validation set and sources for step 3 resume-paused (exchange 1) (round 2)

Request and current resolver agree on `ghog day --full=speed --whole-suite`. The project default in `tools/code_review_validation.py` supplies `ghog day --full=speed`; the captured whole-suite scope adds `--whole-suite`. The `.review-validation` marker was sampled absent. No plan or request additions apply. Bound scope fingerprint: `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 3 resume-paused (exchange 1) (round 2)

None. No command, source or scope drift from the request's resolved validation set.

### Repository state around validation for step 3 resume-paused (exchange 1) (round 2)

Baseline and assessed index trees both equal the request-time tree `229f65878584b25bd7186666c64a24abcaae8d4f`. The evidence launcher compared before/after snapshots of all ten ordered staged paths: acceptable true; no tracked, untracked or ignored differences. Umbrella comparison is not applicable and unchanged. No staging operation or repository repair occurred.

### Repair inventory for step 3 resume-paused (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 resume-paused (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json` returned exit 0, state `valid`, ready `true`, with no diagnostics. All ten staged paths are covered exactly once. The four ordered groups remain accurate:

1. `feat(pause): write saved routing as one JSON block`: `instructions/pause-session.md`, `templates/pause-session.template.md`.
2. `feat(session): accept schema 3 resume receipts`: `templates/resume-session.template.md`, `instructions/status-session.md`, `templates/status-session.template.md`, `instructions/list-session.md`, `templates/list-session.template.md`.
3. `test(resume-paused): check the pause routing contract`: `tests/unit/tools/test_resume_paused_pause_contract/__init__.py`, `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py`.
4. `docs(resume-paused): record step 3 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Ordering separates pause publication, reader alignment, contract tests and step validation metadata. No amendment to `a.commit` is needed.

### Findings and boundaries for step 3 resume-paused (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 resume-paused (exchange 1) (round 2)

No further implementation change is requested for Step 3. The requestor may continue its owning workflow at the human convergence gate; this recommendation does not authorize a commit.

### Decision rationale for step 3 resume-paused (exchange 1) (round 2)

All six readiness results pass: exact identity and round; complete Step 3 implementation; requestor validation evidence and static coverage assessment; unchanged attributable staged scope; no unresolved current or carried findings; and independently checked accurate commit grouping. No substantive repair occurred in this round. Recommend `commit-ready` as advisory review feedback.

### Final reviewer decision for step 3 resume-paused (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 2 by human - Step 3 - human-confirmation

- Recorded: 2026-11-19T19:03:24+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-11-19T22:20:17+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 4
- Outcome: request

### Review identity for step 4 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 resume-paused (round 1)

request_index_tree: 89ddfc58db9efce3f42945c3d6add981202374f6
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review): require Claude background answer waits
group 1 path: rules/run_commands.md
group 1 path: instructions/review-requestor.md
group 1 path: instructions/spec-review-requestor.md
group 1 path: instructions/code-review-requestor.md
group 1 path: tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py
group 2: feat(resume-paused): bind markers to one assignment
group 2 path: tools/resume_paused_marker.py
group 2 path: tests/unit/tools/test_resume_paused_marker/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py
group 3: feat(resume-paused): prove a receiving pane's input
group 3 path: tools/resume_paused_input.py
group 3 path: tests/unit/tools/test_resume_paused_input/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 4: feat(review): record marked claims under the lock
group 4 path: tools/review_exchange_models_coordination.py
group 4 path: tools/review_exchange_ownership.py
group 4 path: tools/review_exchange_ownership_store.py
group 4 path: tools/review_exchange_store.py
group 4 path: tools/review_resume_identity.py
group 4 path: tools/review_exchange_cli_parser.py
group 4 path: tools/review_exchange_cli_resume.py
group 4 path: tools/resume_paused_claim.py
group 4 path: tests/memory_filesystem.py
group 4 path: tests/unit/tools/test_resume_paused_claims/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py
group 5: feat(resume-paused): validate marked receivers
group 5 path: tools/resume_paused_validation.py
group 5 path: bin/resume_paused_validate.bat
group 5 path: tests/unit/tools/resume_paused_receiver_test_support.py
group 5 path: tests/unit/tools/test_resume_paused_validation/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py
group 6: feat(session): resume from marked bulk launches
group 6 path: instructions/resume-session.md
group 6 path: instructions/review-resume.md
group 6 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py
group 7: docs(resume-paused): record step 4 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
group 7 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: bin/resume_paused_validate.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: instructions/code-review-requestor.md
staged path: instructions/resume-session.md
staged path: instructions/review-requestor.md
staged path: instructions/review-resume.md
staged path: instructions/spec-review-requestor.md
staged path: rules/run_commands.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/resume_paused_receiver_test_support.py
staged path: tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py
staged path: tests/unit/tools/test_resume_paused_claims/__init__.py
staged path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py
staged path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/__init__.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_marker/__init__.py
staged path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py
staged path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/__init__.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py
staged path: tools/resume_paused_claim.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_marker.py
staged path: tools/resume_paused_validation.py
staged path: tools/review_exchange_cli_parser.py
staged path: tools/review_exchange_cli_resume.py
staged path: tools/review_exchange_models_coordination.py
staged path: tools/review_exchange_ownership.py
staged path: tools/review_exchange_ownership_store.py
staged path: tools/review_exchange_store.py
staged path: tools/review_resume_identity.py
```

### Validation scope for step 4 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 4 resume-paused (round 1)

Step 4 is fully implemented under plan Q05=A. The compact marker binds one receiving pane to the canonical assignment. The read-only validator and its launcher run before each protected write. A marked claim is verified under the transition lock and records its non-secret binding with the generation it issues. Both receiving instructions follow the marked route without a fallback consent question, and the Claude requestor answer wait is a required background start. The implementation check recorded `Yes. Step 4 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-19T22:12+01:00 with 6768 tests, 100% coverage, no outlier and no exclusion, slowest call 0.81 s; re-run on the final staged tree at 2026-11-19T22:19:18+01:00 with `proof=speed reused=all` (only Markdown and JSON changed since). Each new leaf passed in focus; the review resume, lifecycle, acceptance, ownership and CLI regressions pass.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the seven changed Markdown files after adding `unrouted`.
- Coverage: 100% over `tools`; one unit leaf per new module; the validator's `__main__` guard carries the repository's thin-launcher exclusion.
- Architecture: the marker module is pure; the validator depends on discovery, prover and evidence-source protocols composed by `default_validator`; the review core gains only a generic evidence value and a verifier callable and imports nothing from resume-paused.
- Performance: single passes over markers, records, the transcript enumeration and candidate session files; no cache; every validation and claim rereads fresh evidence.
- Feature integrity: manual claims, manual consent and schema 2 receipts are unchanged; role conflict, fencing and isolation regressions pass; records without a marked binding parse as before.

### Implementation report for step 4 resume-paused (round 1)

Step 4 binds marked resume consent to a fresh read-only validator and to the locked selected claim, and makes the Claude requestor answer wait a required background start.

- `rules/run_commands.md` (Q25=A): new subsection "Claude requestors wait for answers in the background". Every Claude requestor starts each `wait-answer` through a host background mechanism on every requestor route, as one recognized invocation form, ends its turn and resumes from the completion notification. A foreground or moved wait leaves the reviewer pending, and Codex keeps its attached wait. `review-requestor.md`, `spec-review-requestor.md` and `code-review-requestor.md` link to it.
- `tools/resume_paused_marker.py`: the marker `<launch_id>.rp1.<pane_uuid>.<role>.<binding>` (launch id first, version `rp1`, full pane UUID, one of the five role tokens, 64 hexadecimal binding; ASCII, at most 153 characters), extracted from exactly one `--resume-paused` token. The binding hashes the canonical UTF-8 JSON (sorted keys, compact separators) of schema `resume-paused-assignment` version 1: checkout key, prompt SHA-256, receiver host, session, pane and role, the pair after any swap, and the exact exchange with occurrence and selected round, or null. `resolve_assignment` rebuilds it from saved routing and the live exchange; a swap is a pair pane given the other pair role, only for a saved requestor pause. `ResultLine`: `resume-paused <launch_id> <outcome>[ g<generation>]`, at most 100 characters.
- `tools/resume_paused_input.py`: `TuiosDiscovery` runs `tuios list-agents --all-sessions --json` and `tuios capture-pane` as argument lists through `SubprocessRunner` (never a shell). `PaneRecord` keeps the full `window_id`, `session`, `name`, `cwd`, harness, program-status apps and agent session id, and `pane_host` uses strong evidence first. `ClaudeInputProver` proves the marked command as the latest typed input of the transcript named by the pane's agent session id, at or after the pause snapshot, in the checkout, under a pinned profile. `CodexInputProver` ties the pane through `prove_codex_pane`, proves the unique session file with `prove_codex_input`, and re-proves the same session with the carried identity and launch id. `UnpinnedCodexVersions` reports the pre-input version unavailable until a release is pinned.
- `tools/resume_paused_validation.py` and `bin/resume_paused_validate.bat`: the validator checks the marker, the saved pause, the resolved routing, the live exchange (Step 2 observer), the binding and host, the consumption stage (unconsumed, consumed by this launch's schema 3 receipt, or for a reviewer the requestor's schema 3 receipt), the live pane (never an inherited `TUIOS_PANE_ID`) and the complete input. It returns typed non-secret JSON with reasons, the compact failure line, the carried Codex session and the bytes read, and exits 0 valid, 3 refused, 2 invalid. It writes and caches nothing.
- Marked claim (Q03, Q04, Q11): `CoordinationRecord.marked_claim` is a `MarkedClaimBinding` (launch id, pane, host, assignment binding, round, occurrence, issued generation) that must equal the ownership generation. `OwnershipService.claim(marked=...)` always issues a generation with it; any other new claim clears it; current-owner transitions keep it. The ownership store and exchange store forward it. `claim_selected(marked=...)` runs `tools/resume_paused_claim.py`'s verifier under the transition lock before backfill. The verifier re-parses the marker and requires the claimed role, the Codex carried identity and launch id, the current prompt, routing and locked round and occurrence, the same exact exchange, the claimant host, the binding and the consuming receipt. Every refusal writes nothing, and the claim reads no host session file and needs no TUIOS. `claim` takes `--resume-paused-marker`, `--carried-session` and `--carried-launch-id`; callers without them keep the manual path (read by `getattr`, after the first regression run showed existing callers building the arguments without them).
- `instructions/resume-session.md`: `--resume-paused <marker>`, a schema 1 to 3 flag reader keyed on `Prompt`, `SHA-256` and `Project root`, an accepted marker as consent for the author override, new section "Resume from a marked bulk launch" (validate before the receipt, journal and claim, keep a written receipt on later refusal, schema 3 receipt, compact result first, no fallback question), and schema 2 versus schema 3 receipt writing. `instructions/review-resume.md`: appended section "Continue a marked review role".
- `tests/unit/tools/resume_paused_receiver_test_support.py` (Q02=A): `ReceiverCheckout`, `FakeDiscovery`, `FakeProver` and `ReceiverHarness`, which runs validate, receipt, validate, journal, validate, claim with the real validator and locked claim and an evidence hook before each step.
- Tests: leaves `test_resume_paused_marker` (tdd, pbt), `test_resume_paused_input`, `test_resume_paused_claims` (binding, claim), `test_resume_paused_validation` (validator and sequences, launcher smoke, receiver instruction contract) and `test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: Step 4 recorded Yes, with deviations and a "Live host dependencies of Step 4" list left open under Q05=A. `.vscode/settings.json`: project word `unrouted`.

Points for the reviewer's attention:

- Implementation decisions the design leaves open: the marker and result grammars and the assignment schema above. The receiver does not know the delivery instant, so "recorded after delivery" uses the prompt's snapshot instant as the lower bound, with exact whole-command equality of the latest typed input and the fresh launch id.
- Real host proof stays unsupported under plan Q05=A: the shipped registry is empty, and the Codex pre-input version source for a pane is not wired until a release is pinned. The three live dependencies are listed in the validation plan.
- Deviations from the planned file list: `tools/resume_paused_input.py` (pane and input evidence, split from the validator by responsibility), test leaves for the marker and input modules, `test_resume_paused_claims_binding_tdd.py`, `test_resume_paused_receiver_contract_tdd.py`, and the scratch filesystem registrations in `tests/memory_filesystem.py`.
- `tools/review_exchange_store.py` is at 611 lines in the risk band and changed only by forwarding; the two forwarding claim signatures carry a PLR0913 waiver.
- `rg` is not available in the shell used; contract inspection used the equivalent Grep search.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step4.journal.md` and `.reviews/a.resume-paused.step4.handoff.md`.

### Change summary for step 4 resume-paused (round 1)

Thirty-five staged paths in seven `a.commit` groups, in this order:

1. `feat(review): require Claude background answer waits`: `rules/run_commands.md`, `instructions/review-requestor.md`, `instructions/spec-review-requestor.md`, `instructions/code-review-requestor.md`, `tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
2. `feat(resume-paused): bind markers to one assignment`: `tools/resume_paused_marker.py` and the `tests/unit/tools/test_resume_paused_marker` package (package file, tdd and pbt files).
3. `feat(resume-paused): prove a receiving pane's input`: `tools/resume_paused_input.py` and the `tests/unit/tools/test_resume_paused_input` package (package file and tdd file).
4. `feat(review): record marked claims under the lock`: `tools/review_exchange_models_coordination.py`, `tools/review_exchange_ownership.py`, `tools/review_exchange_ownership_store.py`, `tools/review_exchange_store.py`, `tools/review_resume_identity.py`, `tools/review_exchange_cli_parser.py`, `tools/review_exchange_cli_resume.py`, `tools/resume_paused_claim.py`, `tests/memory_filesystem.py`, and the claims package file with `test_resume_paused_claims_binding_tdd.py`.
5. `feat(resume-paused): validate marked receivers`: `tools/resume_paused_validation.py`, `bin/resume_paused_validate.bat`, `tests/unit/tools/resume_paused_receiver_test_support.py`, the `tests/unit/tools/test_resume_paused_validation` package file with its validation and launcher smoke files, and `test_resume_paused_claims_tdd.py`, which needs the harness.
6. `feat(session): resume from marked bulk launches`: `instructions/resume-session.md`, `instructions/review-resume.md`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py`.
7. `docs(resume-paused): record step 4 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, `.vscode/settings.json`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 4 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis in the transcript.

### Reviewer focus for step 4 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-11-19T22:28:19+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 resume-paused (exchange 1) (round 1)

Baseline index tree: 89ddfc58db9efce3f42945c3d6add981202374f6

Assessed index tree: c00d40a73233f532e6eaf26b37fd614820d74b8e

### Implementation check for step 4 resume-paused (exchange 1) (round 1)

Result:

No. Step 4 has NOT been fully implemented.

The marker, canonical binding, pane/input adapters, read-only validator, locked claim plumbing and receiving instructions implement the planned structure. One current finding blocks completion: the locked claim uses parsed fields from an error checkout snapshot. Ports/adapters and dependency direction are appropriate; the store adds forwarding only and remains below the 650-line ceiling. No new superlinear computation was identified. Manual paths appear preserved. Plan Q05=A explicitly defers live host support; the empty registry and unavailable Codex pre-input version are recorded limitations, not an additional code-completion finding.

Validation plan effects:

Updated only Step 4 in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: exact No verdict, missing-work bullets, behavioral test-gap assessment and feature-integrity qualification. Preserved other steps, document status and deferred live host rows. The recorded pre-edit blob was `09aca7bbbf6b07800325c3540aa0e0681ff09a56`; the evidence launcher reported the patch attributable before staging.

### Pre-repair mandatory checks and coverage for step 4 resume-paused (exchange 1) (round 1)

Writer evidence: 6768 tests, 100% line coverage over `tools`, no duration outlier or exclusion, slowest call 0.81 seconds; full speed walk green at 2026-11-19T22:12+01:00 and final staged rerun at 2026-11-19T22:19:18+01:00 with `proof=speed reused=all`. Static test review found the invalid-root error-snapshot scenario missing despite reported line coverage. No reviewer test or coverage command ran; the defect follows directly from the snapshot reader and claim verifier. No implementation/test repair was made.

### Resolved validation set and sources for step 4 resume-paused (exchange 1) (round 1)

Fresh sample: `.review-validation` is absent. `tools/code_review_validation.py` supplies `ghog day --full=speed`; `complete_project_default` adds the bound whole-suite selector. The current set is `ghog day --full=speed --whole-suite`, source `project`, matching the request. No plan/request additions were declared. Bound scope fingerprint: `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 4 resume-paused (exchange 1) (round 1)

None. The request and current resolver require the same command and source.

### Repository state around validation for step 4 resume-paused (exchange 1) (round 1)

Baseline/request tree: `89ddfc58db9efce3f42945c3d6add981202374f6`; assessed tree after attributable metadata staging: `c00d40a73233f532e6eaf26b37fd614820d74b8e`. The ordered 35-path validation-state comparison reports only `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` and the index changed, with no untracked or ignored changes in that set. These are the reviewed-step metadata update and its staging, not validation side effects. Umbrella comparison: not applicable, unchanged. No implementation or test changes by reviewer.

### Repair inventory for step 4 resume-paused (exchange 1) (round 1)

Repairs made:

- Metadata only: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` records Step 4 as incomplete and specifies the missing claim check and regression cases.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 4 resume-paused (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json` returned exit 0, `state: valid`, `ready: true`, no diagnostics, both before assessment and after metadata staging. All 35 staged paths remain assigned exactly once. Group order and conventional subjects follow the feature dependencies. Group 7's body still describes the writer's previous Yes verdict; reconcile it with the final validation result after the requested correction.

Ordered groups and their complete staged inventories:

1. `feat(review): require Claude background answer waits`: `rules/run_commands.md`, `instructions/review-requestor.md`, `instructions/spec-review-requestor.md`, `instructions/code-review-requestor.md`, `tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
2. `feat(resume-paused): bind markers to one assignment`: `tools/resume_paused_marker.py`, `tests/unit/tools/test_resume_paused_marker/__init__.py`, `tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py`, `tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py`.
3. `feat(resume-paused): prove a receiving pane's input`: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/__init__.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`.
4. `feat(review): record marked claims under the lock`: `tools/review_exchange_models_coordination.py`, `tools/review_exchange_ownership.py`, `tools/review_exchange_ownership_store.py`, `tools/review_exchange_store.py`, `tools/review_resume_identity.py`, `tools/review_exchange_cli_parser.py`, `tools/review_exchange_cli_resume.py`, `tools/resume_paused_claim.py`, `tests/memory_filesystem.py`, `tests/unit/tools/test_resume_paused_claims/__init__.py`, `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py`.
5. `feat(resume-paused): validate marked receivers`: `tools/resume_paused_validation.py`, `bin/resume_paused_validate.bat`, `tests/unit/tools/resume_paused_receiver_test_support.py`, `tests/unit/tools/test_resume_paused_validation/__init__.py`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py`, `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py`.
6. `feat(session): resume from marked bulk launches`: `instructions/resume-session.md`, `instructions/review-resume.md`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py`.
7. `docs(resume-paused): record step 4 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, `.vscode/settings.json`.

### Findings and boundaries for step 4 resume-paused (exchange 1) (round 1)

Unresolved findings:

- [P2] Reject error snapshots in the locked marked-claim verifier (`tools/resume_paused_claim.py:75`, `tools/resume_paused_claim.py:105`). After valid pre-claim validation, change only the schema-3 receipt's `Project root` to another checkout, keeping its prompt digest, launch, pane and assignment binding intact. `classify_usage` rejects that root, but `read_checkout_snapshot` returns `PromptState.ERROR` with the parsed prompt, routing and receipt retained (`tools/resume_paused_artifacts.py:469`, `tools/resume_paused_artifacts.py:550`). `_assignment` ignores the error state and `_marked_receipt` checks only schema/digest, so both requestor and reviewer claims can still reach backfill and issue ownership. The standalone validator rejects this snapshot, which makes the missing locked recheck observable precisely when the receipt changes after that validator call. Reject the error snapshot before deriving evidence and add regression cases asserting no artifacts or generation change.

Boundary-crossing work: None.

### Writer instructions for step 4 resume-paused (exchange 1) (round 1)

Reject an error checkout snapshot in the marked-claim path before any backfill or ownership write. Add requestor and reviewer regression cases which validate a good receipt, then change only its root before the real locked claim; require refusal and unchanged coordination, transcript, prompt, receipt and generation relative to the changed-input baseline. Also retain a validator assertion for the invalid-root receipt. Rerun the writer-owned scope-resolved validation and update Step 4 metadata and `a.commit` truthfully before publishing the next exact round. No literal `Human guidance:` block authorized reviewer implementation repairs.

### Decision rationale for step 4 resume-paused (exchange 1) (round 1)

Changes requested. Readiness floor: exact identity passes; implementation completeness fails on the error-snapshot claim check; writer validation evidence is present but the static behavioral test gap remains; staged attribution passes for the metadata-only patch; unresolved-findings floor fails; mechanical commit-plan validation passes, with the final body to be reconciled after correction. This advisory answer neither authorizes a commit nor changes the human convergence gate.

### Final reviewer decision for step 4 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 2 by requestor - Step 4

- Recorded: 2026-11-19T22:42:14+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: request

### Review identity for step 4 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 4
Review round: 2

### Code review evidence for step 4 resume-paused (round 2)

request_index_tree: ac186188e8c01bd1063ca765ff1c7bfb61febb30
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(review): require Claude background answer waits
group 1 path: rules/run_commands.md
group 1 path: instructions/review-requestor.md
group 1 path: instructions/spec-review-requestor.md
group 1 path: instructions/code-review-requestor.md
group 1 path: tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py
group 2: feat(resume-paused): bind markers to one assignment
group 2 path: tools/resume_paused_marker.py
group 2 path: tests/unit/tools/test_resume_paused_marker/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py
group 3: feat(resume-paused): prove a receiving pane's input
group 3 path: tools/resume_paused_input.py
group 3 path: tests/unit/tools/test_resume_paused_input/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 4: feat(review): record marked claims under the lock
group 4 path: tools/review_exchange_models_coordination.py
group 4 path: tools/review_exchange_ownership.py
group 4 path: tools/review_exchange_ownership_store.py
group 4 path: tools/review_exchange_store.py
group 4 path: tools/review_resume_identity.py
group 4 path: tools/review_exchange_cli_parser.py
group 4 path: tools/review_exchange_cli_resume.py
group 4 path: tools/resume_paused_claim.py
group 4 path: tests/memory_filesystem.py
group 4 path: tests/unit/tools/test_resume_paused_claims/__init__.py
group 4 path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py
group 5: feat(resume-paused): validate marked receivers
group 5 path: tools/resume_paused_validation.py
group 5 path: bin/resume_paused_validate.bat
group 5 path: tests/unit/tools/resume_paused_receiver_test_support.py
group 5 path: tests/unit/tools/test_resume_paused_validation/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py
group 6: feat(session): resume from marked bulk launches
group 6 path: instructions/resume-session.md
group 6 path: instructions/review-resume.md
group 6 path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py
group 7: docs(resume-paused): record step 4 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
group 7 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: bin/resume_paused_validate.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: instructions/code-review-requestor.md
staged path: instructions/resume-session.md
staged path: instructions/review-requestor.md
staged path: instructions/review-resume.md
staged path: instructions/spec-review-requestor.md
staged path: rules/run_commands.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/resume_paused_receiver_test_support.py
staged path: tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py
staged path: tests/unit/tools/test_resume_paused_claims/__init__.py
staged path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py
staged path: tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/__init__.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_marker/__init__.py
staged path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py
staged path: tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/__init__.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py
staged path: tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py
staged path: tools/resume_paused_claim.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_marker.py
staged path: tools/resume_paused_validation.py
staged path: tools/review_exchange_cli_parser.py
staged path: tools/review_exchange_cli_resume.py
staged path: tools/review_exchange_models_coordination.py
staged path: tools/review_exchange_ownership.py
staged path: tools/review_exchange_ownership_store.py
staged path: tools/review_exchange_store.py
staged path: tools/review_resume_identity.py
```

### Validation scope for step 4 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 4 resume-paused (round 2)

Step 4 is fully implemented under plan Q05=A after the round 1 repair. The locked marked-claim verifier now refuses an error checkout snapshot before using any parsed field, as the validator already did. The implementation check again records `Yes. Step 4 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-19T22:39:58+01:00 with 6771 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s. A rerun after re-staging two files that `check.bat`'s formatter had reordered (imports only) reused that proof (`proof=speed reused=all`) on index tree `ac186188e8c01bd1063ca765ff1c7bfb61febb30`. Both new claim regressions failed with `DID NOT RAISE` before the fix and pass after it.
- Static checks: the walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan.
- Coverage: 100% over `tools`; the new refusal is covered by the requestor and reviewer regressions.
- Architecture, performance and feature integrity: unchanged from round 1; the repair adds one state check in the claim adapter and one in the shared receipt helper.

### Implementation report for step 4 resume-paused (round 2)

Step 4 binds marked resume consent to a fresh read-only validator and to the locked selected claim, and makes the Claude requestor answer wait a required background start.

- `rules/run_commands.md` (Q25=A): new subsection "Claude requestors wait for answers in the background". Every Claude requestor starts each `wait-answer` through a host background mechanism on every requestor route, as one recognized invocation form, ends its turn and resumes from the completion notification. A foreground or moved wait leaves the reviewer pending, and Codex keeps its attached wait. `review-requestor.md`, `spec-review-requestor.md` and `code-review-requestor.md` link to it.
- `tools/resume_paused_marker.py`: the marker `<launch_id>.rp1.<pane_uuid>.<role>.<binding>` (launch id first, version `rp1`, full pane UUID, one of the five role tokens, 64 hexadecimal binding; ASCII, at most 153 characters), extracted from exactly one `--resume-paused` token. The binding hashes the canonical UTF-8 JSON (sorted keys, compact separators) of schema `resume-paused-assignment` version 1: checkout key, prompt SHA-256, receiver host, session, pane and role, the pair after any swap, and the exact exchange with occurrence and selected round, or null. `resolve_assignment` rebuilds it from saved routing and the live exchange; a swap is a pair pane given the other pair role, only for a saved requestor pause. `ResultLine`: `resume-paused <launch_id> <outcome>[ g<generation>]`, at most 100 characters.
- `tools/resume_paused_input.py`: `TuiosDiscovery` runs `tuios list-agents --all-sessions --json` and `tuios capture-pane` as argument lists through `SubprocessRunner` (never a shell). `PaneRecord` keeps the full `window_id`, `session`, `name`, `cwd`, harness, program-status apps and agent session id, and `pane_host` uses strong evidence first. `ClaudeInputProver` proves the marked command as the latest typed input of the transcript named by the pane's agent session id, at or after the pause snapshot, in the checkout, under a pinned profile. `CodexInputProver` ties the pane through `prove_codex_pane`, proves the unique session file with `prove_codex_input`, and re-proves the same session with the carried identity and launch id. `UnpinnedCodexVersions` reports the pre-input version unavailable until a release is pinned.
- `tools/resume_paused_validation.py` and `bin/resume_paused_validate.bat`: the validator checks the marker, the saved pause, the resolved routing, the live exchange (Step 2 observer), the binding and host, the consumption stage (unconsumed, consumed by this launch's schema 3 receipt, or for a reviewer the requestor's schema 3 receipt), the live pane (never an inherited `TUIOS_PANE_ID`) and the complete input. It returns typed non-secret JSON with reasons, the compact failure line, the carried Codex session and the bytes read, and exits 0 valid, 3 refused, 2 invalid. It writes and caches nothing.
- Marked claim (Q03, Q04, Q11): `CoordinationRecord.marked_claim` is a `MarkedClaimBinding` (launch id, pane, host, assignment binding, round, occurrence, issued generation) that must equal the ownership generation. `OwnershipService.claim(marked=...)` always issues a generation with it; any other new claim clears it; current-owner transitions keep it. The ownership store and exchange store forward it. `claim_selected(marked=...)` runs `tools/resume_paused_claim.py`'s verifier under the transition lock before backfill. The verifier re-parses the marker and requires the claimed role, the Codex carried identity and launch id, the current prompt, routing and locked round and occurrence, the same exact exchange, the claimant host, the binding and the consuming receipt. Every refusal writes nothing, and the claim reads no host session file and needs no TUIOS. `claim` takes `--resume-paused-marker`, `--carried-session` and `--carried-launch-id`; callers without them keep the manual path (read by `getattr`, after the first regression run showed existing callers building the arguments without them).
- Round 1 repair: `read_checkout_snapshot` keeps the prompt, routing and receipt it parsed when it rejects a receipt's `Project root`, returning an error snapshot. `_assignment` in `tools/resume_paused_claim.py` now refuses an error snapshot as `checkout-unreadable` before rebuilding the assignment. The shared `_marked_receipt` (used by `consumed_by` and `requestor_consumed`, and so by the validator) never returns a receipt from an error snapshot.
- `instructions/resume-session.md`: `--resume-paused <marker>`, a schema 1 to 3 flag reader keyed on `Prompt`, `SHA-256` and `Project root`, an accepted marker as consent for the author override, new section "Resume from a marked bulk launch" (validate before the receipt, journal and claim, keep a written receipt on later refusal, schema 3 receipt, compact result first, no fallback question), and schema 2 versus schema 3 receipt writing. `instructions/review-resume.md`: appended section "Continue a marked review role".
- `tests/unit/tools/resume_paused_receiver_test_support.py` (Q02=A): `ReceiverCheckout`, `FakeDiscovery`, `FakeProver` and `ReceiverHarness`, which runs validate, receipt, validate, journal, validate, claim with the real validator and locked claim and an evidence hook before each step.
- Round 1 regressions: `test_receipt_moved_to_another_checkout_after_validation_refuses_the_claim` (requestor and reviewer) validates a good receipt with the real validator (new harness helper `receiver_validator`), changes only the receipt's root, and asserts the locked claim is refused with coordination, transcript, prompt, receipt and generation unchanged; both cases failed (`DID NOT RAISE`) before the fix. The validator's refusal table gains "receipt of another checkout" (`checkout-unreadable`).
- Tests: leaves `test_resume_paused_marker` (tdd, pbt), `test_resume_paused_input`, `test_resume_paused_claims` (binding, claim), `test_resume_paused_validation` (validator and sequences, launcher smoke, receiver instruction contract) and `test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: Step 4 recorded Yes, with deviations and a "Live host dependencies of Step 4" list left open under Q05=A. `.vscode/settings.json`: project word `unrouted`.

Points for the reviewer's attention:

- Implementation decisions the design leaves open: the marker and result grammars and the assignment schema above. The receiver does not know the delivery instant, so "recorded after delivery" uses the prompt's snapshot instant as the lower bound, with exact whole-command equality of the latest typed input and the fresh launch id.
- Real host proof stays unsupported under plan Q05=A: the shipped registry is empty, and the Codex pre-input version source for a pane is not wired until a release is pinned. The three live dependencies are listed in the validation plan.
- Deviations from the planned file list: `tools/resume_paused_input.py` (pane and input evidence, split from the validator by responsibility), test leaves for the marker and input modules, `test_resume_paused_claims_binding_tdd.py`, `test_resume_paused_receiver_contract_tdd.py`, and the scratch filesystem registrations in `tests/memory_filesystem.py`.
- `tools/review_exchange_store.py` is at 611 lines in the risk band and changed only by forwarding; the two forwarding claim signatures carry a PLR0913 waiver.
- `rg` is not available in the shell used; contract inspection used the equivalent Grep search.
- No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step4.journal.md` and `.reviews/a.resume-paused.step4.handoff.md`.

### Change summary for step 4 resume-paused (round 2)

Thirty-five staged paths in seven `a.commit` groups, in this order:

1. `feat(review): require Claude background answer waits`: `rules/run_commands.md`, `instructions/review-requestor.md`, `instructions/spec-review-requestor.md`, `instructions/code-review-requestor.md`, `tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
2. `feat(resume-paused): bind markers to one assignment`: `tools/resume_paused_marker.py` and the `tests/unit/tools/test_resume_paused_marker` package (package file, tdd and pbt files).
3. `feat(resume-paused): prove a receiving pane's input`: `tools/resume_paused_input.py` and the `tests/unit/tools/test_resume_paused_input` package (package file and tdd file).
4. `feat(review): record marked claims under the lock`: `tools/review_exchange_models_coordination.py`, `tools/review_exchange_ownership.py`, `tools/review_exchange_ownership_store.py`, `tools/review_exchange_store.py`, `tools/review_resume_identity.py`, `tools/review_exchange_cli_parser.py`, `tools/review_exchange_cli_resume.py`, `tools/resume_paused_claim.py`, `tests/memory_filesystem.py`, and the claims package file with `test_resume_paused_claims_binding_tdd.py`.
5. `feat(resume-paused): validate marked receivers`: `tools/resume_paused_validation.py`, `bin/resume_paused_validate.bat`, `tests/unit/tools/resume_paused_receiver_test_support.py`, the `tests/unit/tools/test_resume_paused_validation` package file with its validation and launcher smoke files, and `test_resume_paused_claims_tdd.py`, which needs the harness.
6. `feat(session): resume from marked bulk launches`: `instructions/resume-session.md`, `instructions/review-resume.md`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py`.
7. `docs(resume-paused): record step 4 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, `.vscode/settings.json`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 4 resume-paused (round 2)

Writer response:

Round 1 finding P2 (the locked marked-claim verifier used parsed fields from an error checkout snapshot): accepted and repaired as the reviewer directed.

- `tools/resume_paused_claim.py`: `_assignment` refuses `PromptState.ERROR` as `checkout-unreadable` before using the prompt, routing or receipt, and `_marked_receipt` never returns a receipt from an error snapshot, so the shared consumption checks used by the claim and the validator cannot read one.
- `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py`: requestor and reviewer regressions validate a good receipt with the real validator, change only its `Project root`, keep its digest and marked fields, and require the real locked claim to refuse with coordination, transcript, prompt, receipt and generation unchanged relative to the changed-input baseline. Both failed with `DID NOT RAISE` before the fix.
- `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py`: the refusal table keeps a validator assertion for the same receipt (`checkout-unreadable`).
- `tests/unit/tools/resume_paused_receiver_test_support.py`: new `receiver_validator` helper used by the claims regression.
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`: the reviewer's staged No verdict and its two Missing work bullets are resolved; the writer's implementation check restores Yes, removes the Missing work section and records the repair in the implementation, coverage and feature-integrity sections. This follows the repair, not a disagreement.
- `a.commit`: membership, order and subjects unchanged; groups 4 and 5 each gain one What bullet for the repair and its regressions, and group 7 now describes the final Yes result truthfully. The checker reports valid and ready.

No disagreement.

### Reviewer focus for step 4 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-2 -->

## Round 2 by reviewer - Step 4

- Recorded: 2026-11-19T22:46:23+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 resume-paused (exchange 1) (round 2)

Baseline index tree: ac186188e8c01bd1063ca765ff1c7bfb61febb30

Assessed index tree: ac186188e8c01bd1063ca765ff1c7bfb61febb30

### Implementation check for step 4 resume-paused (exchange 1) (round 2)

Result:

Yes. Step 4 has been fully implemented.

The round 1 P2 finding is resolved. The fresh locked verifier rejects PromptState.ERROR in _assignment before rebuilding an assignment, backfill or ownership issuance; `_marked_receipt` also refuses error snapshots. The requestor/reviewer regression validates a good receipt with the real validator, changes only Project root, then invokes the real locked claim and checks the unchanged coordination, transcript, prompt and receipt bytes (including the stored generation). The validator refusal table independently covers the invalid root.

The unchanged marker, pane/input proof, marked ownership threading, receiving instructions and Claude background answer-wait rule retain the prior round's assessment. The narrow state guards add constant work and preserve the adapter boundaries and manual path. No architecture, performance or feature-integrity defect remains identified. Under plan Q05=A, the empty profile registry and live-host dependencies remain open for the Step 1 live matrix and Steps 6–8; this verdict covers Step 4's code deliverable.

Coverage is assessed statically: the new cases close the previously missing behavioral scenario; the helper receiver_validator is called by those tests and the invalid-root fixture is referenced in REFUSALS. The measured source scope is tools, with the exclusions in pyproject.toml, not tests or Markdown. No additional unit-test gap or unreferenced added top-level symbol was identified.

Validation plan effects:

The writer restored the exact Step 4 Yes verdict, removed the completed Missing work section and recorded the error-snapshot repair and regression coverage. These rows agree with this assessment. No reviewer edit was needed; other steps and live-host dependencies remain unchanged.

### Pre-repair mandatory checks and coverage for step 4 resume-paused (exchange 1) (round 2)

The received tree ac186188e8c01bd1063ca765ff1c7bfb61febb30 matches the request. No reviewer repair or test command was run. The requestor reports ghog day --full=speed --whole-suite exit 0 at 2026-11-19T22:39:58+01:00: 6771 tests, 100% coverage over tools, no outlier/exclusion, slowest 0.31 s; the post-formatting rerun reused the speed proof on this exact index. Both new locked-claim cases reportedly failed before the fix. The reviewer inspected the code/test delta and gate scope without repeating the suite or measuring coverage.

### Resolved validation set and sources for step 4 resume-paused (exchange 1) (round 2)

ghog day --full=speed --whole-suite — source: project. The request binds the whole-suite speed scope with fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6. This is requestor validation evidence.

### Resolver drift and direction for step 4 resume-paused (exchange 1) (round 2)

None. A fresh Test-Path .review-validation returned False. tools/code_review_validation.py supplies ghog day --full=speed and complete_project_default appends the explicit --whole-suite selector. This matches the published command and project source.

### Repository state around validation for step 4 resume-paused (exchange 1) (round 2)

Baseline and assessed index are both ac186188e8c01bd1063ca765ff1c7bfb61febb30. The ordered validation path set includes all 35 staged paths and the validation plan. The evidence launcher's before/after comparison reports acceptable=true with no tracked, untracked or ignored path changes. Umbrella digest is not applicable and unchanged. No reviewer staging occurred.

### Repair inventory for step 4 resume-paused (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 resume-paused (exchange 1) (round 2)

The independent commit-plan-check.bat --format json exited 0: state=valid, ready=true, diagnostics=[]. All 35 staged paths are covered exactly. The seven groups remain coherent in their declared order; subjects describe the staged work, and groups 4/5 now describe the repair and regressions. Group 7 accurately records the final Step 4 verdict. No amendment is needed.

1. feat(review): require Claude background answer waits
   Paths: `rules/run_commands.md`, `instructions/review-requestor.md`, `instructions/spec-review-requestor.md`, `instructions/code-review-requestor.md`, `tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.

2. feat(resume-paused): bind markers to one assignment
   Paths: `tools/resume_paused_marker.py`, `tests/unit/tools/test_resume_paused_marker/__init__.py`, `tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_tdd.py`, `tests/unit/tools/test_resume_paused_marker/test_resume_paused_marker_pbt.py`.

3. feat(resume-paused): prove a receiving pane's input
   Paths: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/__init__.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`.

4. feat(review): record marked claims under the lock
   Paths: `tools/review_exchange_models_coordination.py`, `tools/review_exchange_ownership.py`, `tools/review_exchange_ownership_store.py`, `tools/review_exchange_store.py`, `tools/review_resume_identity.py`, `tools/review_exchange_cli_parser.py`, `tools/review_exchange_cli_resume.py`, `tools/resume_paused_claim.py`, `tests/memory_filesystem.py`, `tests/unit/tools/test_resume_paused_claims/__init__.py`, `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_binding_tdd.py`.

5. feat(resume-paused): validate marked receivers
   Paths: `tools/resume_paused_validation.py`, `bin/resume_paused_validate.bat`, `tests/unit/tools/resume_paused_receiver_test_support.py`, `tests/unit/tools/test_resume_paused_validation/__init__.py`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py`, `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py`.

6. feat(session): resume from marked bulk launches
   Paths: `instructions/resume-session.md`, `instructions/review-resume.md`, `tests/unit/tools/test_resume_paused_validation/test_resume_paused_receiver_contract_tdd.py`.

7. docs(resume-paused): record step 4 validation
   Paths: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, `.vscode/settings.json`.

### Findings and boundaries for step 4 resume-paused (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 resume-paused (exchange 1) (round 2)

No further Step 4 repair is requested. Preserve the deferred live-host checklist. Continue through the existing convergence gate; this advisory recommendation does not authorize a commit.

### Decision rationale for step 4 resume-paused (exchange 1) (round 2)

Commit-ready. All six readiness-floor checks pass: exact identity/index agreement; Step 4 completeness under Q05=A; consistent requestor validation evidence plus static coverage assessment; no reviewer changes or attribution issue; no unresolved finding; and independently valid/ready a.commit. The round 1 receipt-root defect is closed by an early error-state guard and concrete regressions for both claim roles.

### Final reviewer decision for step 4 resume-paused (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-2 -->

## Round 2 by human - Step 4 - human-confirmation

- Recorded: 2026-11-19T22:59:05+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 5

- Recorded: 2026-11-20T11:11:12+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 5
- Outcome: request

### Review identity for step 5 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 resume-paused (round 1)

request_index_tree: 3c2fed75d8ded2ea1ab2338d1733d5489c8ee257
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): classify duplicate evidence
group 1 path: tools/resume_paused_evidence.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/__init__.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
group 1 path: tests/memory_filesystem.py
group 2: feat(resume-paused): add the checkout plan model
group 2 path: tools/resume_paused_plan_model.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
group 3: feat(resume-paused): plan each paused checkout
group 3 path: tools/resume_paused_planner.py
group 3 path: tests/unit/tools/test_resume_paused_planner/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_planner/planner_world.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
group 4: docs(resume-paused): record step 5 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_evidence/__init__.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/__init__.py
staged path: tests/unit/tools/test_resume_paused_planner/planner_world.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tools/resume_paused_evidence.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
```

### Validation scope for step 5 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 5 resume-paused (round 1)

Step 5 is fully implemented. The read-only planner refuses a recognized agent caller (dry run included), failed discovery and unmatched `--except` or `--switch-roles` names before reading any checkout. It indexes panes once by full UUID and canonical root and gives each prompt-bearing checkout one typed result. Duplicate evidence comes from every pane of the checkout, excluded and caller panes included; certain evidence skips and uncertainty alone fails. Saved targets are validated by UUID, session, host and checkout, the resumed target is protected, and the conditional counterpart is protected statically. Each planned marker is bound to the assignment rebuilt from the observed exchange. The implementation check recorded `Yes. Step 5 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T11:10:05+01:00 with 6910 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `3c2fed75d8ded2ea1ab2338d1733d5489c8ee257`. The previous speed walk found one uncovered line (the default journal reader), now covered by a scratch-tree test. Each new leaf passed in focus.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan, the only changed Markdown file.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_evidence`, `test_resume_paused_planner`, `test_resume_paused_plan_model`).
- Architecture: the plan model holds values only; the planner depends on injected ports for snapshots, exchanges, command histories, captures, the journal and launch ids; the only concrete readers are the argument-list listing runner and the journal reader, both read-only; no module writes, starts a process of its own, claims or sends input.
- Performance: one pass builds the UUID and root maps; target lookups and name matches are map and set lookups; sorting the checkout roots and one checkout's panes keeps output deterministic over small per-run sets; plans are rebuilt from fresh evidence on every run.
- Feature integrity: no existing module changes; manual resume, review, validator and claim paths are untouched; the plan is a new in-memory result.
- Open composition rows (validation plan): the production command history, Codex screen probe, exchange observer and snapshot reader adapters are composed by Step 8; under plan Q05=A the screen probe stays unsupported.

### Implementation report for step 5 resume-paused (round 1)

Step 5 builds the read-only checkout planner and its duplicate protections. It adds three modules and three test leaves and changes no existing module.

- `tools/resume_paused_evidence.py`, discovery and activity: `observe_panes` runs `tuios list-agents --all-sessions --json` once through the injected argument-list runner and parses, from the same output, the strict `PaneRecord` list (Step 4's `parse_agents`) and each pane's activity (`state`, `blocked_by`, `draft_held`, waiting `message`). A failed or malformed listing returns `None`, never an empty observation; a pane id listed twice gets no activity.
- Same module, input eligibility: `input_eligibility` returns blocked for `needs_input`, `blocked` or any `blocked_by`, draft for a held draft, eligible for `idle` or `done`, unknown for any other state. For `working` it returns busy on Claude without any capture; on Codex it takes one injected `ScreenProbe` verdict, and only `IDLE_EMPTY` overrides (note `stale-working-overridden`), as requirement Q03 allows.
- Same module, counted commands: `classify_command` accepts `resume-session` or `review-resume` after an optional `/`, `$` or `$llm-shared:` prefix and any trailing context. A `review-resume` selects its role from its `--resume-paused` marker or from a single standalone `requestor` or `reviewer` word; two different role words, or a malformed marker, are uncertain. `counted` implements Q14/Q26: `resume-session` always counts, any `review-resume` counts for a saved reviewer pause, a reviewer-only one never counts for another pause, and an unknown role is uncertain (`None`).
- Same module, session journal: `read_session_journal` (injected reader, `journal_path` from `USERPROFILE`) parses the journal strictly: UTF-8, every `##` heading line must be a `Pause` or `Resume` heading, timestamps need an offset and are cut to microseconds as the journal tool does, and paths are canonical Windows roots. It indexes resume entries by `CanonicalRoot`. A missing file is an empty index; an unreadable or malformed one carries an error and answers no checkout.
- Same module, duplicate verdict: `classify_duplicates` takes the pause facts (root, snapshot instant, saved reviewer role), every pane of the checkout, the injected `CommandHistory`, the activity map and the journal. It returns certain evidence (journal resume at or after the pause; counted command at or after the pause; pane blocked on the author-override question) and, separately, uncertain observations (unreadable history, unattributed counted command, uncertain role, unreadable journal), in pane id order.
- `tools/resume_paused_plan_model.py`: the typed vocabulary, values only. `PlanRequest`, `GlobalReason` and `GlobalFailure`, `SkipReason` (expected), `ErrorReason` (checkout failure), `CheckoutOutcome`, `ActionKind` (`resume`, conditional `reviewer`, conditional `continue-reviewer`), `PlannedAction`, `CheckoutPlan` and `RunPlan`, whose `failed` is a run-wide refusal or any checkout error, and whose `input_allowed` is false in a dry run or after a run-wide refusal.
- `tools/resume_paused_planner.py`, run-wide gates: `plan_run` refuses a recognized agent caller (`CallerDecision`, dry run included) and failed discovery before reading anything. It indexes panes once by full UUID and canonical root, then refuses unmatched names: an `--except` name must equal, case-insensitively, a session, a complete pane label or a checkout folder name; a `--switch-roles` name only a session or folder name.
- Same module, per checkout in root order: `NO_PROMPT` is omitted; an `ArtifactError` from the reader or the evidence fails only that checkout (`evidence-invalid`); an `ERROR` snapshot fails it (`checkout-unreadable`); an excluded folder skips it; a switch naming a checkout without a resolved saved requestor pair fails it (`switch-not-applicable`).
- Same module, used prompts: a `USED` prompt carries the receipt as evidence with the known resumer. Only a schema 3 receipt from the resolved requestor of a saved requestor pair plans a conditional `continue-reviewer` action. A receipt from the other pair pane is `switch-required` without the switch and `switch-mismatch` with it; any other receipt is `already-used`.
- Same module, fresh prompts: an unsupported pausing agent skips; routing `error` fails, `unresolved` skips (`pairing-ambiguous` when the exchange itself is unknown), absent and table-only skip. Duplicate evidence skips (first signal decides the reason); uncertainty without evidence fails (`duplicate-uncertain`).
- Same module, targets: each saved target is located by full UUID. Absent skips; listed twice fails (`pane-ambiguous`); in another session it skips when the saved session has no live pane and fails when it still has one (`target-session-changed`). Then host (contradictory fails, none is a shell skip, another host fails), checkout (unusable path skips, another checkout fails), exclusion (session or pane label) and caller pane are checked, plus activity for the resumed target. A changed label or agent session id is a note. The counterpart reviewer of a saved requestor pair is checked statically only and stays conditional; a skipped counterpart never blocks the requestor's resume, an error fails the checkout.
- Same module, commands: the saved exchange is observed through the injected `ExchangeObserver`; only `observed` with round and occurrence binds markers (not-live and busy skip, selection-changed and damaged fail). Each command is `/resume-session`, `$llm-shared:resume-session`, `/review-resume` or `$llm-shared:review-resume` with `--resume-paused` and a marker built from a fresh launch id and the `resolve_assignment` digest; the resume comes first and alone carries `clear`. The run plan counts omitted panes: every listed pane that no reported action targets.
- Ports: snapshot reader, exchange observer, command history, screen probe, journal index and launch id factory are injected (`PlannerPorts`). Step 8 composes the production adapters with the Step 1 and Step 2 readers; the validation plan lists these composition dependencies as open rows.
- Tests: `tests/unit/tools/test_resume_paused_evidence/` (tdd: listing, activity strictness, eligibility table, command classification, counting rule, journal parsing and reading, duplicate verdict; pbt: role selection over prefixes, case and trailing context, and `resume-session` always counting). `tests/unit/tools/test_resume_paused_planner/` (tdd: refusals, baseline pair with exact markers, dry run, single and reviewer pauses, switch, inapplicable switch, used prompts and continuation, routing states, unsupported pauser, isolated errors and folder exclusion, duplicate evidence incl. excluded and caller panes and other root spellings, override question, target identity table, Codex name fallback and notes, protections, stale-working override, counterpart protections, continuation skip, exchange kinds, omitted panes; pbt: discovery-order invariance of the whole plan and exclusions never lifting duplicate protection; `planner_world.py`: declared snapshots parsed from bytes, fakes and typed world-change builders). `tests/unit/tools/test_resume_paused_plan_model/` (run verdict, request defaults). No test touches a process, a pane or a file.
- Deviations from the plan's file list: the plan model was split out of the planner when formatting took the planner to 654 lines; the evidence and plan model modules got their own test leaves (one leaf per module), and the planner leaf adds `planner_world.py`.
- Design reading recorded in the step notes: a moved UUID is an absent target when its saved session no longer has any live pane ("a saved pane UUID or session name that no longer matches a live pane is an absent target") and a session-change error when that session still has one ("a known ... TUIOS session reassignment remains a classification error").
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step5.journal.md` and `.reviews/a.resume-paused.step5.handoff.md`.

### Change summary for step 5 resume-paused (round 1)

Thirteen staged paths in four `a.commit` groups, in this order:

1. `feat(resume-paused): classify duplicate evidence`: `tools/resume_paused_evidence.py` and the `tests/unit/tools/test_resume_paused_evidence` package (package file, tdd and pbt files).
2. `feat(resume-paused): add the checkout plan model`: `tools/resume_paused_plan_model.py` and the `tests/unit/tools/test_resume_paused_plan_model` package (package file and tdd file).
3. `feat(resume-paused): plan each paused checkout`: `tools/resume_paused_planner.py` and the `tests/unit/tools/test_resume_paused_planner` package (package file, `planner_world.py`, tdd and pbt files).
4. `docs(resume-paused): record step 5 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 5 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis in the transcript.

### Reviewer focus for step 5 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-11-20T11:25:38+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 resume-paused (exchange 1) (round 1)

Baseline index tree: 3c2fed75d8ded2ea1ab2338d1733d5489c8ee257

Assessed index tree: a1e638571cc66f23f39f6d0e7ea7ea59b23fff83

### Implementation check for step 5 resume-paused (exchange 1) (round 1)

Result:

No. Step 5 has NOT been fully implemented. The planner can duplicate or suppress resumes and can select an unready pane.

Validation plan effects:

Updated the step 5 verdict, missing work and supporting checks in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Markdown lint reported zero issues.

### Pre-repair mandatory checks and coverage for step 5 resume-paused (exchange 1) (round 1)

The requestor reported 6,910 passing tests and 100% line coverage over `tools`. Static review identified gaps in behavior coverage for role selection, timing and pane readiness. The reviewer did not repeat the suite or measure coverage.

### Resolved validation set and sources for step 5 resume-paused (exchange 1) (round 1)

Project validation resolves to `ghog day --full=speed --whole-suite`. The exchange binds whole-suite scope.

### Resolver drift and direction for step 5 resume-paused (exchange 1) (round 1)

The command, source and scope agree with the request.

### Repository state around validation for step 5 resume-paused (exchange 1) (round 1)

The comparison flagged `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` and the index. The entire index delta from the request tree consists of the attributable validation edit. Its working copy matches the index. The comparison reported no untracked effects. The umbrella comparison reported inapplicable and unchanged.

### Repair inventory for step 5 resume-paused (exchange 1) (round 1)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (polishing-only reviewer metadata). No substantive reviewer repairs.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (reviewer-staged assessment).

### Commit plan assessment for step 5 resume-paused (exchange 1) (round 1)

The independent checker returned `valid`, `ready: true`, and zero diagnostics for 14 staged paths in four ordered groups. Group membership and order are accurate. The request summary omitted `tests/memory_filesystem.py` from group 1. Refresh the completion wording in group 4 after rework.

1. `feat(resume-paused): classify duplicate evidence` includes `tools/resume_paused_evidence.py`, `tests/unit/tools/test_resume_paused_evidence/__init__.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py`, `tests/memory_filesystem.py`.
2. `feat(resume-paused): add the checkout plan model` includes `tools/resume_paused_plan_model.py`, `tests/unit/tools/test_resume_paused_plan_model/__init__.py`, `tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py`.
3. `feat(resume-paused): plan each paused checkout` includes `tools/resume_paused_planner.py`, `tests/unit/tools/test_resume_paused_planner/__init__.py`, `tests/unit/tools/test_resume_paused_planner/planner_world.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py`.
4. `docs(resume-paused): record step 5 validation` includes `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Findings and boundaries for step 5 resume-paused (exchange 1) (round 1)

Unresolved findings:

- In `_selected_role`, distinguish a selected role from a word in explanatory text. For a non-reviewer pause, `/review-resume after the reviewer replies` must remain uncertain, while `/review-resume as reviewer; the requestor is busy` has an explicit reviewer selection. Cover both in the unit and property tests.
- In `_command_evidence`, exclude a proved reviewer-only command for a non-reviewer pause even when its time is unknown. Keep a missing timestamp uncertain for commands that could count. Test the same undated reviewer command with each pause role.
- Apply the requirement's strictly later boundary to journal and command evidence. An equal timestamp alone cannot prove a later resume. Cover earlier, equal and later timestamps for both sources and preserve uncertainty when ordering cannot be established.
- Read the TUIOS `ready` field in `_activity` and carry it through input eligibility. Handle an idle or done record with negative or unavailable readiness conservatively. Cover these records through discovery and planning and retain the specified fresh Codex screen override for stale working status.
- Normalize exclusion and switch names once per run and share the sets across checkouts. With C checkouts and N selector names, the current constructor repeats O(N) work C times.

Boundary-crossing work: None.

### Writer instructions for step 5 resume-paused (exchange 1) (round 1)

Address each finding, exercise the listed regression cases, and rerun the bound validation set. Update the validation verdict and the wording for group 4. Reconcile the path count in the replacement request.

### Decision rationale for step 5 resume-paused (exchange 1) (round 1)

Identity, staged attribution and mechanical commit-plan checks passed. The implementation and behavior coverage have open findings in duplicate detection and input eligibility.

### Final reviewer decision for step 5 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-11-20T13:50:31+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 resume-paused (round 2)

request_index_tree: 85653d22329c74ead335eb4399e04654b0aa9da2
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): classify duplicate evidence
group 1 path: tools/resume_paused_evidence.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/__init__.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
group 1 path: tests/memory_filesystem.py
group 2: feat(resume-paused): add the checkout plan model
group 2 path: tools/resume_paused_plan_model.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
group 3: feat(resume-paused): plan each paused checkout
group 3 path: tools/resume_paused_planner.py
group 3 path: tests/unit/tools/test_resume_paused_planner/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_planner/planner_world.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
group 4: docs(resume-paused): record step 5 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_evidence/__init__.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/__init__.py
staged path: tests/unit/tools/test_resume_paused_planner/planner_world.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tools/resume_paused_evidence.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
```

### Validation scope for step 5 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 5 resume-paused (round 2)

Step 5 is fully implemented after the round 1 repairs. The read-only planner refuses a recognized agent caller (dry run included), failed discovery and unmatched `--except` or `--switch-roles` names before reading any checkout. It indexes panes once by full UUID and canonical root, with selector names case-folded once per run, and gives each prompt-bearing checkout one typed result. Duplicate evidence comes from every pane of the checkout, excluded and caller panes included. Only a strictly later time proves a resume, an equal time stays uncertain, only an explicit selection gives a `review-resume` its role, and a reviewer-only command never counts for a non-reviewer pause. Saved targets are validated by UUID, session, host and checkout; the resumed target is protected, including TUIOS readiness, and the conditional counterpart is protected statically. Each planned marker is bound to the assignment rebuilt from the observed exchange. The validation plan records `Yes. Step 5 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T13:49:56+01:00 with 6928 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `85653d22329c74ead335eb4399e04654b0aa9da2`. The three Step 5 leaves passed in focus with the new cases.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown (transcript included after the authorized one-line repair), ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan and the transcript.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_evidence`, `test_resume_paused_planner`, `test_resume_paused_plan_model`).
- Architecture: the plan model holds values only; the planner depends on injected ports for snapshots, exchanges, command histories, captures, the journal and launch ids; the only concrete readers are the argument-list listing runner and the journal reader, both read-only; no module writes, starts a process of its own, claims or sends input.
- Performance: one pass builds the UUID and root maps; selector names are folded once per run; target lookups and name matches are map and set lookups; sorting the checkout roots and one checkout's panes keeps output deterministic over small per-run sets.
- Feature integrity: no existing production module changes; manual resume, review, validator and claim paths are untouched; the plan is a new in-memory result.
- Open composition rows (validation plan): the production command history, Codex screen probe, exchange observer and snapshot reader adapters are composed by Step 8; under plan Q05=A the screen probe stays unsupported.

### Implementation report for step 5 resume-paused (round 2)

Step 5 builds the read-only checkout planner and its duplicate protections. It adds three modules and three test leaves, registers the evidence leaf in `tests/memory_filesystem.py`, and changes no existing production module. Round 2 repairs the five round 1 findings.

- `tools/resume_paused_evidence.py`, discovery and activity: `observe_panes` runs `tuios list-agents --all-sessions --json` once through the injected argument-list runner and parses, from the same output, the strict `PaneRecord` list (Step 4's `parse_agents`) and each pane's activity (`state`, `blocked_by`, `draft_held`, `ready`, waiting `message`). `ready` must be a boolean or absent (`None`). A failed or malformed listing returns `None`, never an empty observation; a pane id listed twice gets no activity.
- Same module, input eligibility: `input_eligibility` returns blocked for `needs_input`, `blocked` or any `blocked_by`, draft for a held draft, eligible for `idle` or `done` only when `ready` is true and `not-ready` otherwise, unknown for any other state. For `working` it returns busy on Claude without any capture; on Codex it takes one injected `ScreenProbe` verdict, and only `IDLE_EMPTY` overrides (note `stale-working-overridden`), as requirement Q03 allows.
- Same module, counted commands: `classify_command` accepts `resume-session` or `review-resume` after an optional `/`, `$` or `$llm-shared:` prefix and any trailing context. A `review-resume` selects a role only through its `--resume-paused` marker, a first role word, `--role <role>` or `as <role>`; a role word elsewhere is explanatory text, and two different selections, or a malformed marker, are uncertain. `counted` implements Q14/Q26: `resume-session` always counts, any `review-resume` counts for a saved reviewer pause, a reviewer-only one never counts for another pause, and an unknown role is uncertain (`None`).
- Same module, session journal: `read_session_journal` (injected reader, `journal_path` from `USERPROFILE`) parses the journal strictly: UTF-8, every level-two heading must be a `Pause` or `Resume` entry heading, timestamps need an offset and are cut to microseconds as the journal tool does, and paths are canonical Windows roots. It indexes resume entries by `CanonicalRoot`. A missing file is an empty index; an unreadable or malformed one carries an error and answers no checkout.
- Same module, duplicate verdict: `classify_duplicates` takes the pause facts (root, snapshot instant, saved reviewer role), every pane of the checkout, the injected `CommandHistory`, the activity map and the journal. `_order` places each time as older, unordered (equal), later or unattributed. Certain evidence is a journal resume or a counted command strictly later than the pause, or a pane blocked on the author-override question. A command that can never count for this pause (a proved reviewer-only continuation of a non-reviewer pause) is ignored whatever its time. Uncertain observations are an equal time, an unreadable history, an undated command that could count, an uncertain role and an unreadable journal, in pane id order.
- `tools/resume_paused_plan_model.py`: the typed vocabulary, values only. `PlanRequest`, `GlobalReason` and `GlobalFailure`, `SkipReason` (expected, now including `pane-not-ready`), `ErrorReason` (checkout failure), `CheckoutOutcome`, `ActionKind` (`resume`, conditional `reviewer`, conditional `continue-reviewer`), `PlannedAction`, `CheckoutPlan` and `RunPlan`, whose `failed` is a run-wide refusal or any checkout error, and whose `input_allowed` is false in a dry run or after a run-wide refusal.
- `tools/resume_paused_planner.py`, run-wide gates: `plan_run` refuses a recognized agent caller (`CallerDecision`, dry run included) and failed discovery before reading anything. It indexes panes once by full UUID and canonical root, then refuses unmatched names: an `--except` name must equal, case-insensitively, a session, a complete pane label or a checkout folder name; a `--switch-roles` name only a session or folder name. `_RunContext.of` case-folds both name lists once and every checkout planner shares them.
- Same module, per checkout in root order: `NO_PROMPT` is omitted; an `ArtifactError` from the reader or the evidence fails only that checkout (`evidence-invalid`); an `ERROR` snapshot fails it (`checkout-unreadable`); an excluded folder skips it; a switch naming a checkout without a resolved saved requestor pair fails it (`switch-not-applicable`).
- Same module, used prompts: a `USED` prompt carries the receipt as evidence with the known resumer. Only a schema 3 receipt from the resolved requestor of a saved requestor pair plans a conditional `continue-reviewer` action. A receipt from the other pair pane is `switch-required` without the switch and `switch-mismatch` with it; any other receipt is `already-used`.
- Same module, fresh prompts: an unsupported pausing agent skips; routing `error` fails, `unresolved` skips (`pairing-ambiguous` when the exchange itself is unknown), absent and table-only skip. Duplicate evidence skips (first signal decides the reason); uncertainty without evidence fails (`duplicate-uncertain`).
- Same module, targets: each saved target is located by full UUID. Absent skips; listed twice fails (`pane-ambiguous`); in another session it skips when the saved session has no live pane and fails when it still has one (`target-session-changed`). Then host (contradictory fails, none is a shell skip, another host fails), checkout (unusable path skips, another checkout fails), exclusion (session or pane label) and caller pane are checked, plus activity for the resumed target, including `pane-not-ready`. A changed label or agent session id is a note. The counterpart reviewer of a saved requestor pair is checked statically only and stays conditional; a skipped counterpart never blocks the requestor's resume, an error fails the checkout.
- Same module, commands: the saved exchange is observed through the injected `ExchangeObserver`; only `observed` with round and occurrence binds markers (not-live and busy skip, selection-changed and damaged fail). Each command is `/resume-session`, `$llm-shared:resume-session`, `/review-resume` or `$llm-shared:review-resume` with `--resume-paused` and a marker built from a fresh launch id and the `resolve_assignment` digest; the resume comes first and alone carries `clear`. The run plan counts omitted panes: every listed pane that no reported action targets.
- Ports: snapshot reader, exchange observer, command history, screen probe, journal index and launch id factory are injected (`PlannerPorts`). Step 8 composes the production adapters with the Step 1 and Step 2 readers; the validation plan lists these composition dependencies as open rows.
- Tests: `tests/unit/tools/test_resume_paused_evidence/` (tdd: listing, activity and readiness strictness, eligibility table with negative and absent readiness, command classification with explicit selections beside explanatory role words, counting rule, journal parsing and reading through the default reader, earlier, equal and later times for journal entries and commands, the same undated reviewer command for each pause role, override question; pbt: explicit selection over prefixes, case and explanatory context, conflicting selections, and `resume-session` always counting, each drawn as one sampled product per example). `tests/unit/tools/test_resume_paused_planner/` (tdd: refusals, baseline pair with exact markers, dry run, single and reviewer pauses, switch, inapplicable switch, used prompts and continuation, routing states, unsupported pauser, isolated errors and folder exclusion, duplicate evidence incl. excluded and caller panes and other root spellings, override question, target identity table, Codex name fallback and notes, protections incl. not-ready panes, stale-working override, counterpart protections, continuation skip, exchange kinds, omitted panes; pbt: discovery-order invariance and exclusions never lifting duplicate protection). `tests/unit/tools/test_resume_paused_plan_model/` (run verdict, request defaults). Only the default journal reader test reads a file, from the memory-backed scratch tree.
- Deviations from the plan's file list: the plan model was split out of the planner when formatting took the planner to 654 lines; the evidence and plan model modules got their own test leaves (one leaf per module), the planner leaf adds `planner_world.py`, and `tests/memory_filesystem.py` registers the evidence leaf.
- Design reading recorded in the step notes: a moved UUID is an absent target when its saved session no longer has any live pane and a session-change error when that session still has one.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step5.journal.md` and `.reviews/a.resume-paused.step5.handoff.md`.

### Change summary for step 5 resume-paused (round 2)

Fourteen staged paths in four `a.commit` groups, in this order:

1. `feat(resume-paused): classify duplicate evidence`: `tools/resume_paused_evidence.py`, the `tests/unit/tools/test_resume_paused_evidence` package (package file, tdd and pbt files) and `tests/memory_filesystem.py`, which registers that leaf for its scratch-file journal read.
2. `feat(resume-paused): add the checkout plan model`: `tools/resume_paused_plan_model.py` and the `tests/unit/tools/test_resume_paused_plan_model` package (package file and tdd file).
3. `feat(resume-paused): plan each paused checkout`: `tools/resume_paused_planner.py` and the `tests/unit/tools/test_resume_paused_planner` package (package file, `planner_world.py`, tdd and pbt files).
4. `docs(resume-paused): record step 5 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 2 changes the evidence module and its tests, the plan model (one skip reason), the planner and its tests, the validation plan and the wording of groups 1, 3 and 4; membership and order are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 5 resume-paused (round 2)

Writer response:

All five round 1 findings are accepted and repaired; there is no disagreement. Your staged validation-plan assessment was the starting point of the updated Step 5 rows, which now read Yes again with the repairs recorded and the missing-work list removed.

- **Role selection**: `_selected_role` now takes a role only from the marker, a first role word, `--role <role>` (or `--role=<role>`) or `as <role>` (optionally `as the` or `as a`). A role word anywhere else is explanatory text, and two different selections are uncertain. `/review-resume after the reviewer replies` selects nothing, so it stays uncertain for a non-reviewer pause, and `/review-resume as reviewer; the requestor is busy` selects the reviewer. Unit cases cover both, plus a leading role word followed by the other role in prose, a `--role=` form and two conflicting selections; the property test now composes explicit selections with explanatory phrases that name either role.
- **Undated reviewer-only commands**: `_command_evidence` decides countability first, so a proved reviewer-only `review-resume` is ignored for a non-reviewer pause whatever its time. A missing time stays uncertain only for a command that could count. The same undated reviewer command is tested with each pause role (ignored for a requestor pause, unattributed for a reviewer pause).
- **Strictly later boundary**: a new `_order` helper places an observation as older, unordered (equal), later or unattributed. Journal entries and commands count only when strictly later; an equal time is reported as uncertain (`journal-resume-unordered`, `command-unordered`). Earlier, equal and later times are covered for both sources.
- **TUIOS readiness**: `PaneActivity` carries `ready`, parsed strictly (boolean or absent, any other type is malformed discovery). An idle or done pane is eligible only when `ready` is true; otherwise it is `not-ready` and the planner skips it as `pane-not-ready`. The fresh Codex override of a stale working status is unchanged. Discovery, eligibility and planner cases cover negative and absent readiness.
- **Selector normalization**: `_RunContext.of` case-folds the exclusion and switch names once per run, and every checkout planner shares those sets.
- **Commit plan**: the change summary now lists `tests/memory_filesystem.py` in group 1, and groups 1, 3 and 4 describe the repaired behavior; group 4 records the round 1 repairs.

One transcript repair was made under an explicit user exception: line 3731 of the code review transcript (my round 1 implementation report) had an inline code span with a trailing space (MD038); it now reads "every `##` heading line". No other transcript line changed.

### Reviewer focus for step 5 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-11-20T13:54:40+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 resume-paused (exchange 1) (round 2)

Baseline index tree: 85653d22329c74ead335eb4399e04654b0aa9da2

Assessed index tree: 789fa202742e88d31a86b97a98513e25bb44abd0

### Implementation check for step 5 resume-paused (exchange 1) (round 2)

Result:

No. Step 5 has NOT been fully implemented. Four carried findings are resolved. Role selection remains unsafe for a non-reviewer pause.

Validation plan effects:

Updated the step 5 verdict, missing work and behavioral coverage in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Markdown lint reported zero issues.

### Pre-repair mandatory checks and coverage for step 5 resume-paused (exchange 1) (round 2)

The requestor reported 6,928 passing tests and 100% line coverage over `tools` on the matching request tree. The reviewer inspected the staged changes and regression tests without rerunning the suite.

### Resolved validation set and sources for step 5 resume-paused (exchange 1) (round 2)

The project resolver printed `ghog day --full=speed --whole-suite`. The exchange bound the whole suite.

### Resolver drift and direction for step 5 resume-paused (exchange 1) (round 2)

The request and current speed-proof resolver agree.

### Repository state around validation for step 5 resume-paused (exchange 1) (round 2)

The comparison flagged `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` and the index. The attributable review metadata accounts for the delta. Its working copy matches the index, and the whitespace check passed. No untracked effects were reported. The umbrella was inapplicable and unchanged.

### Repair inventory for step 5 resume-paused (exchange 1) (round 2)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (polishing-only review metadata). No substantive reviewer repairs.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (reviewer-staged assessment).

### Commit plan assessment for step 5 resume-paused (exchange 1) (round 2)

Independent checker result `valid`, `ready: true`, 14 paths, zero diagnostics. Membership, ordering and subjects match the change. Group 4's completion wording depends on resolving the remaining finding.

1. `feat(resume-paused): classify duplicate evidence` includes `tools/resume_paused_evidence.py`, `tests/unit/tools/test_resume_paused_evidence/__init__.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py`, `tests/memory_filesystem.py`.
2. `feat(resume-paused): add the checkout plan model` includes `tools/resume_paused_plan_model.py`, `tests/unit/tools/test_resume_paused_plan_model/__init__.py`, `tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py`.
3. `feat(resume-paused): plan each paused checkout` includes `tools/resume_paused_planner.py`, `tests/unit/tools/test_resume_paused_planner/__init__.py`, `tests/unit/tools/test_resume_paused_planner/planner_world.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py`.
4. `docs(resume-paused): record step 5 validation` includes `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Findings and boundaries for step 5 resume-paused (exchange 1) (round 2)

Unresolved findings:

- `_selected_role` still guesses reviewer-only continuation from ambiguous text. `/review-resume reviewer or requestor` used to be tested as uncertain. The replacement matcher accepts its leading word and discards the alternative. `/review-resume after Alex signs in as reviewer` also selects reviewer because the `as` matcher scans all trailing prose. In both cases `counted` ignores the command for a non-reviewer pause, so a duplicate resume can be planned.

Boundary-crossing work: None.

### Writer instructions for step 5 resume-paused (exchange 1) (round 2)

Preserve uncertainty for explicit alternatives and for role phrases embedded in explanatory clauses. Restore the removed `reviewer or requestor` regression and check both examples through duplicate classification, including their effect on input for a non-reviewer pause. Keep the explicit reviewer selection with unrelated trailing prose working. Rerun the bound validation and refresh the step 5 verdict.

### Decision rationale for step 5 resume-paused (exchange 1) (round 2)

Timestamp ordering, undated reviewer-only commands, pane readiness and shared selector normalization pass static review. The matching request identity, mechanical commit plan, and attributed staging pass. A remaining Q26 role-classification defect and the missing regression prevent a commit-ready recommendation.

### Final reviewer decision for step 5 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 3 by requestor - Step 5

- Recorded: 2026-11-20T14:07:54+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 5
Review round: 3

### Code review evidence for step 5 resume-paused (round 3)

request_index_tree: 2e82deb70d827677d3ef291182023fd82391fb04
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): classify duplicate evidence
group 1 path: tools/resume_paused_evidence.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/__init__.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
group 1 path: tests/memory_filesystem.py
group 2: feat(resume-paused): add the checkout plan model
group 2 path: tools/resume_paused_plan_model.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
group 3: feat(resume-paused): plan each paused checkout
group 3 path: tools/resume_paused_planner.py
group 3 path: tests/unit/tools/test_resume_paused_planner/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_planner/planner_world.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
group 4: docs(resume-paused): record step 5 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_evidence/__init__.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/__init__.py
staged path: tests/unit/tools/test_resume_paused_planner/planner_world.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tools/resume_paused_evidence.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
```

### Validation scope for step 5 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 5 resume-paused (round 3)

Step 5 is fully implemented after the round 1 and 2 repairs. The read-only planner refuses a recognized agent caller (dry run included), failed discovery and unmatched `--except` or `--switch-roles` names before reading any checkout. It indexes panes once by full UUID and canonical root, with selector names case-folded once per run, and gives each prompt-bearing checkout one typed result. Duplicate evidence comes from every pane of the checkout, excluded and caller panes included. Only a strictly later time proves a resume, an equal time stays uncertain, only a selection heading its arguments gives a `review-resume` its role, an alternative or a second selection of the other role keeps it uncertain, and a reviewer-only command never counts for a non-reviewer pause. Saved targets are validated by UUID, session, host and checkout; the resumed target is protected, including TUIOS readiness, and the conditional counterpart is protected statically. Each planned marker is bound to the assignment rebuilt from the observed exchange. The validation plan records `Yes. Step 5 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T14:07:05+01:00 with 6942 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `2e82deb70d827677d3ef291182023fd82391fb04`. The three Step 5 leaves passed in focus with the new cases.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown (transcript included after the authorized one-line repair), ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan and the transcript.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_evidence`, `test_resume_paused_planner`, `test_resume_paused_plan_model`).
- Architecture: the plan model holds values only; the planner depends on injected ports for snapshots, exchanges, command histories, captures, the journal and launch ids; the only concrete readers are the argument-list listing runner and the journal reader, both read-only; no module writes, starts a process of its own, claims or sends input.
- Performance: one pass builds the UUID and root maps; selector names are folded once per run; target lookups and name matches are map and set lookups; sorting the checkout roots and one checkout's panes keeps output deterministic over small per-run sets.
- Feature integrity: no existing production module changes; manual resume, review, validator and claim paths are untouched; the plan is a new in-memory result.
- Open composition rows (validation plan): the production command history, Codex screen probe, exchange observer and snapshot reader adapters are composed by Step 8; under plan Q05=A the screen probe stays unsupported.

### Implementation report for step 5 resume-paused (round 3)

Step 5 builds the read-only checkout planner and its duplicate protections. It adds three modules and three test leaves, registers the evidence leaf in `tests/memory_filesystem.py`, and changes no existing production module. Round 2 repaired the five round 1 findings; round 3 repairs the remaining role-classification finding of round 2.

- `tools/resume_paused_evidence.py`, discovery and activity: `observe_panes` runs `tuios list-agents --all-sessions --json` once through the injected argument-list runner and parses, from the same output, the strict `PaneRecord` list (Step 4's `parse_agents`) and each pane's activity (`state`, `blocked_by`, `draft_held`, `ready`, waiting `message`). `ready` must be a boolean or absent (`None`). A failed or malformed listing returns `None`, never an empty observation; a pane id listed twice gets no activity.
- Same module, input eligibility: `input_eligibility` returns blocked for `needs_input`, `blocked` or any `blocked_by`, draft for a held draft, eligible for `idle` or `done` only when `ready` is true and `not-ready` otherwise, unknown for any other state. For `working` it returns busy on Claude without any capture; on Codex it takes one injected `ScreenProbe` verdict, and only `IDLE_EMPTY` overrides (note `stale-working-overridden`), as requirement Q03 allows.
- Same module, counted commands: `classify_command` accepts `resume-session` or `review-resume` after an optional `/`, `$` or `$llm-shared:` prefix, followed by any non-word character or the end, then any trailing context. A `review-resume` selects a role only through its `--resume-paused` marker, or through a role word, `--role <role>` or `as <role>` heading its arguments on the command's own line (`_HEAD_SELECTION_RE`). The role is uncertain when the other role appears in the head's own clause, which ends at a semicolon, a newline, a period followed by whitespace or an opening parenthesis, such as `reviewer or requestor` or `reviewer/requestor`, or in another selection form anywhere, such as `requestor; later as reviewer`, or when the marker is malformed. A role phrase inside prose, such as `after Alex signs in as reviewer`, selects nothing, and a role word in a later clause, such as `as reviewer; the requestor is busy`, is explanatory. `counted` implements Q14/Q26: `resume-session` always counts, any `review-resume` counts for a saved reviewer pause, a reviewer-only one never counts for another pause, and an unknown role is uncertain (`None`).
- Same module, session journal: `read_session_journal` (injected reader, `journal_path` from `USERPROFILE`) parses the journal strictly: UTF-8, every level-two heading must be a `Pause` or `Resume` entry heading, timestamps need an offset and are cut to microseconds as the journal tool does, and paths are canonical Windows roots. It indexes resume entries by `CanonicalRoot`. A missing file is an empty index; an unreadable or malformed one carries an error and answers no checkout.
- Same module, duplicate verdict: `classify_duplicates` takes the pause facts (root, snapshot instant, saved reviewer role), every pane of the checkout, the injected `CommandHistory`, the activity map and the journal. `_order` places each time as older, unordered (equal), later or unattributed. Certain evidence is a journal resume or a counted command strictly later than the pause, or a pane blocked on the author-override question. A command that can never count for this pause (a proved reviewer-only continuation of a non-reviewer pause) is ignored whatever its time. Uncertain observations are an equal time, an unreadable history, an undated command that could count, an uncertain role and an unreadable journal, in pane id order.
- `tools/resume_paused_plan_model.py`: the typed vocabulary, values only. `PlanRequest`, `GlobalReason` and `GlobalFailure`, `SkipReason` (expected, now including `pane-not-ready`), `ErrorReason` (checkout failure), `CheckoutOutcome`, `ActionKind` (`resume`, conditional `reviewer`, conditional `continue-reviewer`), `PlannedAction`, `CheckoutPlan` and `RunPlan`, whose `failed` is a run-wide refusal or any checkout error, and whose `input_allowed` is false in a dry run or after a run-wide refusal.
- `tools/resume_paused_planner.py`, run-wide gates: `plan_run` refuses a recognized agent caller (`CallerDecision`, dry run included) and failed discovery before reading anything. It indexes panes once by full UUID and canonical root, then refuses unmatched names: an `--except` name must equal, case-insensitively, a session, a complete pane label or a checkout folder name; a `--switch-roles` name only a session or folder name. `_RunContext.of` case-folds both name lists once and every checkout planner shares them.
- Same module, per checkout in root order: `NO_PROMPT` is omitted; an `ArtifactError` from the reader or the evidence fails only that checkout (`evidence-invalid`); an `ERROR` snapshot fails it (`checkout-unreadable`); an excluded folder skips it; a switch naming a checkout without a resolved saved requestor pair fails it (`switch-not-applicable`).
- Same module, used prompts: a `USED` prompt carries the receipt as evidence with the known resumer. Only a schema 3 receipt from the resolved requestor of a saved requestor pair plans a conditional `continue-reviewer` action. A receipt from the other pair pane is `switch-required` without the switch and `switch-mismatch` with it; any other receipt is `already-used`.
- Same module, fresh prompts: an unsupported pausing agent skips; routing `error` fails, `unresolved` skips (`pairing-ambiguous` when the exchange itself is unknown), absent and table-only skip. Duplicate evidence skips (first signal decides the reason); uncertainty without evidence fails (`duplicate-uncertain`).
- Same module, targets: each saved target is located by full UUID. Absent skips; listed twice fails (`pane-ambiguous`); in another session it skips when the saved session has no live pane and fails when it still has one (`target-session-changed`). Then host (contradictory fails, none is a shell skip, another host fails), checkout (unusable path skips, another checkout fails), exclusion (session or pane label) and caller pane are checked, plus activity for the resumed target, including `pane-not-ready`. A changed label or agent session id is a note. The counterpart reviewer of a saved requestor pair is checked statically only and stays conditional; a skipped counterpart never blocks the requestor's resume, an error fails the checkout.
- Same module, commands: the saved exchange is observed through the injected `ExchangeObserver`; only `observed` with round and occurrence binds markers (not-live and busy skip, selection-changed and damaged fail). Each command is `/resume-session`, `$llm-shared:resume-session`, `/review-resume` or `$llm-shared:review-resume` with `--resume-paused` and a marker built from a fresh launch id and the `resolve_assignment` digest; the resume comes first and alone carries `clear`. The run plan counts omitted panes: every listed pane that no reported action targets.
- Ports: snapshot reader, exchange observer, command history, screen probe, journal index and launch id factory are injected (`PlannerPorts`). Step 8 composes the production adapters with the Step 1 and Step 2 readers; the validation plan lists these composition dependencies as open rows.
- Tests: `tests/unit/tools/test_resume_paused_evidence/` (tdd: listing, activity and readiness strictness, eligibility table with negative and absent readiness, command classification with head selections beside explanatory later clauses, the restored `reviewer or requestor` regression with its slash variant, an embedded `after Alex signs in as reviewer`, a second selection of the other role and punctuation after the command name, counting rule, the two ambiguous texts through the duplicate verdict, journal parsing and reading through the default reader, earlier, equal and later times for journal entries and commands, the same undated reviewer command for each pause role, override question; pbt: the head selection decides whatever later clauses say, any same-clause alternative of the other role is uncertain, a second selection form of the other role is uncertain, and `resume-session` always counts, each drawn as one sampled product per example). `tests/unit/tools/test_resume_paused_planner/` (tdd: refusals, baseline pair with exact markers, dry run, single and reviewer pauses, switch, inapplicable switch, used prompts and continuation, routing states, unsupported pauser, isolated errors and folder exclusion, duplicate evidence incl. excluded and caller panes and other root spellings, ambiguous reviewer continuation on a requestor pause (both texts fail the checkout without any command, an explicit reviewer selection with ordinary prose stays planned), override question, target identity table, Codex name fallback and notes, protections incl. not-ready panes, stale-working override, counterpart protections, continuation skip, exchange kinds, omitted panes; pbt: discovery-order invariance and exclusions never lifting duplicate protection). `tests/unit/tools/test_resume_paused_plan_model/` (run verdict, request defaults). Only the default journal reader test reads a file, from the memory-backed scratch tree.
- Deviations from the plan's file list: the plan model was split out of the planner when formatting took the planner to 654 lines; the evidence and plan model modules got their own test leaves (one leaf per module), the planner leaf adds `planner_world.py`, and `tests/memory_filesystem.py` registers the evidence leaf.
- Design reading recorded in the step notes: a moved UUID is an absent target when its saved session no longer has any live pane and a session-change error when that session still has one.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step5.journal.md` and `.reviews/a.resume-paused.step5.handoff.md`.

### Change summary for step 5 resume-paused (round 3)

Fourteen staged paths in four `a.commit` groups, in this order:

1. `feat(resume-paused): classify duplicate evidence`: `tools/resume_paused_evidence.py`, the `tests/unit/tools/test_resume_paused_evidence` package (package file, tdd and pbt files) and `tests/memory_filesystem.py`, which registers that leaf for its scratch-file journal read.
2. `feat(resume-paused): add the checkout plan model`: `tools/resume_paused_plan_model.py` and the `tests/unit/tools/test_resume_paused_plan_model` package (package file and tdd file).
3. `feat(resume-paused): plan each paused checkout`: `tools/resume_paused_planner.py` and the `tests/unit/tools/test_resume_paused_planner` package (package file, `planner_world.py`, tdd and pbt files).
4. `docs(resume-paused): record step 5 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 3 changes the evidence module and its tests, the planner tests, the validation plan and the wording of groups 1 and 4; membership and order are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 5 resume-paused (round 3)

Writer response:

The round 2 finding is accepted and repaired; there is no disagreement. Your staged Step 5 assessment was the starting point of the updated rows, which read Yes again with the round 2 repair recorded and the missing-work list removed.

- **Head-only selection**: `_selected_role` now takes a role only from the marker or from a role word, `--role <role>` or `as <role>` heading the arguments on the command's own line. An `as <role>` phrase inside prose no longer selects, so `/review-resume after Alex signs in as reviewer` has no selected role and stays uncertain for a non-reviewer pause.
- **Alternatives and second selections**: after a head selection, the other role inside the head's own clause (up to a semicolon, a newline, a period followed by whitespace or an opening parenthesis) or in another selection form anywhere makes the role uncertain. `/review-resume reviewer or requestor` and `reviewer/requestor` are uncertain again, as is `requestor; later as reviewer`. An explicit selection followed by ordinary explanatory text, such as `as reviewer; the requestor is busy` or `as reviewer, then continue the review`, keeps its role.
- **Regressions through duplicate classification and planning**: the restored `reviewer or requestor` case and the embedded `as reviewer` case are classified, counted (`None` for a non-reviewer pause), reported as `review-role-uncertain` by `classify_duplicates`, and fail a requestor pause's checkout as `duplicate-uncertain` with no planned command; the explicit reviewer selection with ordinary prose leaves the checkout planned.
- **Property tests**: rebuilt on the head rule: the head selection decides whatever later clauses say, a same-clause alternative of the other role is uncertain, and a second selection form of the other role is uncertain.
- **Command name boundary**: building those properties showed that `review-resume;` was not recognized as a command at all; a resume command name may now be followed by any non-word character, the safer reading for duplicate protection, while longer names such as `resume-sessions` stay excluded.
- **Commit plan**: groups 1 and 4 describe the head-only selection; membership and order are unchanged.

### Reviewer focus for step 5 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-3 -->

## Round 3 by reviewer - Step 5

- Recorded: 2026-11-20T14:13:51+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 resume-paused (exchange 1) (round 3)

Baseline index tree: 2e82deb70d827677d3ef291182023fd82391fb04

Assessed index tree: 5093b2d0e6d1a26abbeb9e621f64a571be8f07d2

### Implementation check for step 5 resume-paused (exchange 1) (round 3)

Result:

No. Step 5 has NOT been fully implemented. The two round 2 examples now pass through the planner, but clause punctuation still changes the meaning of alternative roles.

Validation plan effects:

Updated the verdict, remaining work and behavioral coverage in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Markdown lint passed.

### Pre-repair mandatory checks and coverage for step 5 resume-paused (exchange 1) (round 3)

The requestor reported 6,942 passing tests and 100% coverage over `tools` on the matching request tree. The reviewer checked the staged classifier, duplicate transformation and planner regression tests statically.

### Resolved validation set and sources for step 5 resume-paused (exchange 1) (round 3)

The project resolver printed `ghog day --full=speed --whole-suite` for the bound whole-suite scope.

### Resolver drift and direction for step 5 resume-paused (exchange 1) (round 3)

The request and current resolver match.

### Repository state around validation for step 5 resume-paused (exchange 1) (round 3)

The validation-state comparison flagged only `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` and the index. The attributable reviewer edit accounts for both. No untracked effects were reported. The umbrella comparison reported inapplicable and unchanged.

### Repair inventory for step 5 resume-paused (exchange 1) (round 3)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (polishing-only review metadata). No substantive reviewer repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` (reviewer-staged assessment).

### Commit plan assessment for step 5 resume-paused (exchange 1) (round 3)

Independent checker returned `valid`, `ready: true` with 14 paths, four ordered groups and no diagnostics. The group 4 completion claim needs refreshing after rework.

1. `feat(resume-paused): classify duplicate evidence` includes `tools/resume_paused_evidence.py`, `tests/unit/tools/test_resume_paused_evidence/__init__.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py`, `tests/memory_filesystem.py`.
2. `feat(resume-paused): add the checkout plan model` includes `tools/resume_paused_plan_model.py`, `tests/unit/tools/test_resume_paused_plan_model/__init__.py`, `tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py`.
3. `feat(resume-paused): plan each paused checkout` includes `tools/resume_paused_planner.py`, `tests/unit/tools/test_resume_paused_planner/__init__.py`, `tests/unit/tools/test_resume_paused_planner/planner_world.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py`.
4. `docs(resume-paused): record step 5 validation` includes `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Findings and boundaries for step 5 resume-paused (exchange 1) (round 3)

Unresolved findings:

- `_selected_role` uses punctuation as proof that the other role is merely explanatory. `/review-resume reviewer (or requestor)` loses the alternative at `(`, so `counted` returns false and a requestor checkout can be resumed twice. In the opposite direction, `/review-resume as reviewer while the requestor is busy` has an explicit role, but the other role word makes it uncertain and suppresses a legitimate resume. The same words split by a semicolon work. Preserve the meaning of the role choice across these punctuation variants.

Boundary-crossing work: None.

### Writer instructions for step 5 resume-paused (exchange 1) (round 3)

Keep an explicit alternative uncertain even when parenthesized. Retain an explicit reviewer selection when a trailing explanatory clause mentions the requestor. Exercise these contrasting cases through the requestor checkout, rerun the bound validation, and update the verdict.

### Decision rationale for step 5 resume-paused (exchange 1) (round 3)

Identity, attribution, mechanical grouping and the previously repaired readiness and timestamp cases pass. The remaining Q26 behavior permits a duplicate resume and lacks regression coverage.

### Final reviewer decision for step 5 resume-paused (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-3 -->

## Round 4 by requestor - Step 5

- Recorded: 2026-11-20T14:22:44+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 resume-paused (round 4)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 5
Review round: 4

### Code review evidence for step 5 resume-paused (round 4)

request_index_tree: 0d5deac0e39c709bba252000bb04b92d0ba85cb3
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): classify duplicate evidence
group 1 path: tools/resume_paused_evidence.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/__init__.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
group 1 path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
group 1 path: tests/memory_filesystem.py
group 2: feat(resume-paused): add the checkout plan model
group 2 path: tools/resume_paused_plan_model.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
group 3: feat(resume-paused): plan each paused checkout
group 3 path: tools/resume_paused_planner.py
group 3 path: tests/unit/tools/test_resume_paused_planner/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_planner/planner_world.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
group 4: docs(resume-paused): record step 5 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_evidence/__init__.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py
staged path: tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_plan_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/__init__.py
staged path: tests/unit/tools/test_resume_paused_planner/planner_world.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tools/resume_paused_evidence.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
```

### Validation scope for step 5 resume-paused (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 5 resume-paused (round 4)

Step 5 is fully implemented after the round 1 to 3 repairs. The read-only planner refuses a recognized agent caller (dry run included), failed discovery and unmatched `--except` or `--switch-roles` names before reading any checkout. It indexes panes once by full UUID and canonical root, with selector names case-folded once per run, and gives each prompt-bearing checkout one typed result. Duplicate evidence comes from every pane of the checkout, excluded and caller panes included. Only a strictly later time proves a resume, an equal time stays uncertain, only a selection heading its arguments gives a `review-resume` its role, the other role offered as an alternative keeps it uncertain whatever the punctuation while an explanatory mention does not, and a reviewer-only command never counts for a non-reviewer pause. Saved targets are validated by UUID, session, host and checkout; the resumed target is protected, including TUIOS readiness, and the conditional counterpart is protected statically. Each planned marker is bound to the assignment rebuilt from the observed exchange. The validation plan records `Yes. Step 5 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T14:22:10+01:00 with 6952 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `0d5deac0e39c709bba252000bb04b92d0ba85cb3`. The three Step 5 leaves passed in focus with the new cases.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown (transcript included after the authorized one-line repair), ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan and the transcript.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_evidence`, `test_resume_paused_planner`, `test_resume_paused_plan_model`).
- Architecture: the plan model holds values only; the planner depends on injected ports for snapshots, exchanges, command histories, captures, the journal and launch ids; the only concrete readers are the argument-list listing runner and the journal reader, both read-only; no module writes, starts a process of its own, claims or sends input.
- Performance: one pass builds the UUID and root maps; selector names are folded once per run; target lookups and name matches are map and set lookups; sorting the checkout roots and one checkout's panes keeps output deterministic over small per-run sets.
- Feature integrity: no existing production module changes; manual resume, review, validator and claim paths are untouched; the plan is a new in-memory result.
- Open composition rows (validation plan): the production command history, Codex screen probe, exchange observer and snapshot reader adapters are composed by Step 8; under plan Q05=A the screen probe stays unsupported.

### Implementation report for step 5 resume-paused (round 4)

Step 5 builds the read-only checkout planner and its duplicate protections. It adds three modules and three test leaves, registers the evidence leaf in `tests/memory_filesystem.py`, and changes no existing production module. Round 2 repaired the five round 1 findings, round 3 the role-classification finding of round 2, and round 4 the punctuation finding of round 3.

- `tools/resume_paused_evidence.py`, discovery and activity: `observe_panes` runs `tuios list-agents --all-sessions --json` once through the injected argument-list runner and parses, from the same output, the strict `PaneRecord` list (Step 4's `parse_agents`) and each pane's activity (`state`, `blocked_by`, `draft_held`, `ready`, waiting `message`). `ready` must be a boolean or absent (`None`). A failed or malformed listing returns `None`, never an empty observation; a pane id listed twice gets no activity.
- Same module, input eligibility: `input_eligibility` returns blocked for `needs_input`, `blocked` or any `blocked_by`, draft for a held draft, eligible for `idle` or `done` only when `ready` is true and `not-ready` otherwise, unknown for any other state. For `working` it returns busy on Claude without any capture; on Codex it takes one injected `ScreenProbe` verdict, and only `IDLE_EMPTY` overrides (note `stale-working-overridden`), as requirement Q03 allows.
- Same module, counted commands: `classify_command` accepts `resume-session` or `review-resume` after an optional `/`, `$` or `$llm-shared:` prefix, followed by any non-word character or the end, then any trailing context. A `review-resume` selects a role only through its `--resume-paused` marker, or through a role word, `--role <role>` or `as <role>` heading its arguments on the command's own line (`_HEAD_SELECTION_RE`). The role is uncertain when the other role is offered as an alternative, whatever the punctuation: in another selection form anywhere (`requestor; later as reviewer`), joined by `or`, `nor`, a slash or a vertical bar on either side through brackets, quotes and an article (`reviewer or requestor`, `reviewer/requestor`, `reviewer (or requestor)`), or listed bare right after the head with only punctuation, brackets or `and` between (`reviewer and requestor`); a malformed marker is uncertain too. A role phrase inside prose, such as `after Alex signs in as reviewer`, selects nothing, and any other mention of the other role, such as `as reviewer while the requestor is busy` or `as reviewer; the requestor is busy`, is explanatory. `counted` implements Q14/Q26: `resume-session` always counts, any `review-resume` counts for a saved reviewer pause, a reviewer-only one never counts for another pause, and an unknown role is uncertain (`None`).
- Same module, session journal: `read_session_journal` (injected reader, `journal_path` from `USERPROFILE`) parses the journal strictly: UTF-8, every level-two heading must be a `Pause` or `Resume` entry heading, timestamps need an offset and are cut to microseconds as the journal tool does, and paths are canonical Windows roots. It indexes resume entries by `CanonicalRoot`. A missing file is an empty index; an unreadable or malformed one carries an error and answers no checkout.
- Same module, duplicate verdict: `classify_duplicates` takes the pause facts (root, snapshot instant, saved reviewer role), every pane of the checkout, the injected `CommandHistory`, the activity map and the journal. `_order` places each time as older, unordered (equal), later or unattributed. Certain evidence is a journal resume or a counted command strictly later than the pause, or a pane blocked on the author-override question. A command that can never count for this pause (a proved reviewer-only continuation of a non-reviewer pause) is ignored whatever its time. Uncertain observations are an equal time, an unreadable history, an undated command that could count, an uncertain role and an unreadable journal, in pane id order.
- `tools/resume_paused_plan_model.py`: the typed vocabulary, values only. `PlanRequest`, `GlobalReason` and `GlobalFailure`, `SkipReason` (expected, now including `pane-not-ready`), `ErrorReason` (checkout failure), `CheckoutOutcome`, `ActionKind` (`resume`, conditional `reviewer`, conditional `continue-reviewer`), `PlannedAction`, `CheckoutPlan` and `RunPlan`, whose `failed` is a run-wide refusal or any checkout error, and whose `input_allowed` is false in a dry run or after a run-wide refusal.
- `tools/resume_paused_planner.py`, run-wide gates: `plan_run` refuses a recognized agent caller (`CallerDecision`, dry run included) and failed discovery before reading anything. It indexes panes once by full UUID and canonical root, then refuses unmatched names: an `--except` name must equal, case-insensitively, a session, a complete pane label or a checkout folder name; a `--switch-roles` name only a session or folder name. `_RunContext.of` case-folds both name lists once and every checkout planner shares them.
- Same module, per checkout in root order: `NO_PROMPT` is omitted; an `ArtifactError` from the reader or the evidence fails only that checkout (`evidence-invalid`); an `ERROR` snapshot fails it (`checkout-unreadable`); an excluded folder skips it; a switch naming a checkout without a resolved saved requestor pair fails it (`switch-not-applicable`).
- Same module, used prompts: a `USED` prompt carries the receipt as evidence with the known resumer. Only a schema 3 receipt from the resolved requestor of a saved requestor pair plans a conditional `continue-reviewer` action. A receipt from the other pair pane is `switch-required` without the switch and `switch-mismatch` with it; any other receipt is `already-used`.
- Same module, fresh prompts: an unsupported pausing agent skips; routing `error` fails, `unresolved` skips (`pairing-ambiguous` when the exchange itself is unknown), absent and table-only skip. Duplicate evidence skips (first signal decides the reason); uncertainty without evidence fails (`duplicate-uncertain`).
- Same module, targets: each saved target is located by full UUID. Absent skips; listed twice fails (`pane-ambiguous`); in another session it skips when the saved session has no live pane and fails when it still has one (`target-session-changed`). Then host (contradictory fails, none is a shell skip, another host fails), checkout (unusable path skips, another checkout fails), exclusion (session or pane label) and caller pane are checked, plus activity for the resumed target, including `pane-not-ready`. A changed label or agent session id is a note. The counterpart reviewer of a saved requestor pair is checked statically only and stays conditional; a skipped counterpart never blocks the requestor's resume, an error fails the checkout.
- Same module, commands: the saved exchange is observed through the injected `ExchangeObserver`; only `observed` with round and occurrence binds markers (not-live and busy skip, selection-changed and damaged fail). Each command is `/resume-session`, `$llm-shared:resume-session`, `/review-resume` or `$llm-shared:review-resume` with `--resume-paused` and a marker built from a fresh launch id and the `resolve_assignment` digest; the resume comes first and alone carries `clear`. The run plan counts omitted panes: every listed pane that no reported action targets.
- Ports: snapshot reader, exchange observer, command history, screen probe, journal index and launch id factory are injected (`PlannerPorts`). Step 8 composes the production adapters with the Step 1 and Step 2 readers; the validation plan lists these composition dependencies as open rows.
- Tests: `tests/unit/tools/test_resume_paused_evidence/` (tdd: listing, activity and readiness strictness, eligibility table with negative and absent readiness, command classification with head selections beside explanatory later clauses, the restored `reviewer or requestor` regression with its slash, parenthesized and `and` variants, `as reviewer while the requestor is busy` and `reviewer, the requestor is Claude` keeping the reviewer, an embedded `after Alex signs in as reviewer`, a second selection of the other role and punctuation after the command name, counting rule, the two ambiguous texts through the duplicate verdict, journal parsing and reading through the default reader, earlier, equal and later times for journal entries and commands, the same undated reviewer command for each pause role, override question; pbt: the head selection decides whatever punctuation-varied explanations follow, any punctuation-varied alternative of the other role is uncertain, a second selection form of the other role is uncertain, and `resume-session` always counts, each drawn as one sampled product per example). `tests/unit/tools/test_resume_paused_planner/` (tdd: refusals, baseline pair with exact markers, dry run, single and reviewer pauses, switch, inapplicable switch, used prompts and continuation, routing states, unsupported pauser, isolated errors and folder exclusion, duplicate evidence incl. excluded and caller panes and other root spellings, ambiguous reviewer continuation on a requestor pause (`reviewer or requestor`, the embedded `as reviewer` and the parenthesized alternative fail the checkout without any command; an explicit reviewer selection followed by ordinary prose, a `while` clause or a semicolon clause naming the requestor stays planned), override question, target identity table, Codex name fallback and notes, protections incl. not-ready panes, stale-working override, counterpart protections, continuation skip, exchange kinds, omitted panes; pbt: discovery-order invariance and exclusions never lifting duplicate protection). `tests/unit/tools/test_resume_paused_plan_model/` (run verdict, request defaults). Only the default journal reader test reads a file, from the memory-backed scratch tree.
- Deviations from the plan's file list: the plan model was split out of the planner when formatting took the planner to 654 lines; the evidence and plan model modules got their own test leaves (one leaf per module), the planner leaf adds `planner_world.py`, and `tests/memory_filesystem.py` registers the evidence leaf.
- Design reading recorded in the step notes: a moved UUID is an absent target when its saved session no longer has any live pane and a session-change error when that session still has one.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step5.journal.md` and `.reviews/a.resume-paused.step5.handoff.md`.

### Change summary for step 5 resume-paused (round 4)

Fourteen staged paths in four `a.commit` groups, in this order:

1. `feat(resume-paused): classify duplicate evidence`: `tools/resume_paused_evidence.py`, the `tests/unit/tools/test_resume_paused_evidence` package (package file, tdd and pbt files) and `tests/memory_filesystem.py`, which registers that leaf for its scratch-file journal read.
2. `feat(resume-paused): add the checkout plan model`: `tools/resume_paused_plan_model.py` and the `tests/unit/tools/test_resume_paused_plan_model` package (package file and tdd file).
3. `feat(resume-paused): plan each paused checkout`: `tools/resume_paused_planner.py` and the `tests/unit/tools/test_resume_paused_planner` package (package file, `planner_world.py`, tdd and pbt files).
4. `docs(resume-paused): record step 5 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 4 changes the evidence module and its tests, the planner tests, the validation plan and the wording of group 4; membership and order are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 5 resume-paused (round 4)

Writer response:

The round 3 finding is accepted and repaired; there is no disagreement. Your staged Step 5 assessment was the starting point of the updated rows, which read Yes again with the round 3 repair recorded and the missing-work list removed.

- **Punctuation no longer decides**: the clause split is gone. After a head selection, the other role makes it uncertain only when it is offered as an alternative: in another selection form anywhere (`as <role>`, `--role <role>`), joined by `or`, `nor`, a slash or a vertical bar on either side, through brackets, quotes and an article (`reviewer (or requestor)`, `the requestor or the reviewer`), or listed bare right after the head with only punctuation, brackets or `and` between (`reviewer and requestor`, `reviewer, requestor`, `reviewer (requestor)`). Any other mention of the other role is explanatory, whatever its punctuation: `as reviewer while the requestor is busy`, `as reviewer; the requestor is busy` and `reviewer, the requestor is Claude` all keep the reviewer selection.
- **Contrasting cases through the requestor checkout**: `/review-resume reviewer (or requestor)` is classified uncertain, counted as `None` for a non-reviewer pause, reported as `review-role-uncertain` by `classify_duplicates`, and fails the requestor pause's checkout as `duplicate-uncertain` with no planned command; `/review-resume as reviewer while the requestor is busy` and the semicolon form leave the checkout planned.
- **Property tests**: the explanatory phrases now vary their punctuation (semicolon, comma, plain clause, parenthesis) and must never select or unsettle the head role; the alternatives vary theirs (`or`, `nor`, slash, bar, parenthesized `or`, `and`, comma, semicolon, bare parenthesis) and must be uncertain exactly when they name the other role.
- **Commit plan**: group 4 records the round 3 repair; membership and order are unchanged.
- **File size**: the evidence module is 580 lines, in the 550 to 650 band and below the ceiling; the validation plan states it.

### Reviewer focus for step 5 resume-paused (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-4 -->

## Round 4 by reviewer - Step 5

- Recorded: 2026-11-20T14:25:20+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 resume-paused (exchange 1) (round 4)

Baseline index tree: 0d5deac0e39c709bba252000bb04b92d0ba85cb3

Assessed index tree: 0d5deac0e39c709bba252000bb04b92d0ba85cb3

### Implementation check for step 5 resume-paused (exchange 1) (round 4)

Result:

Yes. Step 5 has been fully implemented. The planner regression now shows that `reviewer (or requestor)` leaves the role uncertain and produces no command. An explicit reviewer selection with `while the requestor is busy` leaves the requestor checkout eligible. The earlier timestamp, pane readiness, selector normalization and role cases remain covered.

Validation plan effects:

The staged step 5 verdict and coverage rows in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md` already record the repairs. No reviewer edit was needed.

### Pre-repair mandatory checks and coverage for step 5 resume-paused (exchange 1) (round 4)

The writer reported 6,952 passing tests, 100% line coverage over `tools`, and zero duration outliers or exclusions on the exact request tree. The reviewer inspected the implementation, unit and property cases, and checkout-level assertions without repeating the suite.

### Resolved validation set and sources for step 5 resume-paused (exchange 1) (round 4)

The bound whole-suite project command is `ghog day --full=speed --whole-suite`.

### Resolver drift and direction for step 5 resume-paused (exchange 1) (round 4)

The independently resolved command and bound scope match the request.

### Repository state around validation for step 5 resume-paused (exchange 1) (round 4)

Request, baseline and assessed trees match. The validation-state comparison passed with no changed paths. The umbrella was inapplicable and unchanged.

### Repair inventory for step 5 resume-paused (exchange 1) (round 4)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 resume-paused (exchange 1) (round 4)

The independent checker returned `valid`, `ready: true`, with four ordered groups, 14 staged paths and zero diagnostics. The subjects, ordering, membership and completion wording match the staged step.

1. `feat(resume-paused): classify duplicate evidence` includes `tools/resume_paused_evidence.py`, `tests/unit/tools/test_resume_paused_evidence/__init__.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_tdd.py`, `tests/unit/tools/test_resume_paused_evidence/test_resume_paused_evidence_pbt.py`, `tests/memory_filesystem.py`.
2. `feat(resume-paused): add the checkout plan model` includes `tools/resume_paused_plan_model.py`, `tests/unit/tools/test_resume_paused_plan_model/__init__.py`, `tests/unit/tools/test_resume_paused_plan_model/test_resume_paused_plan_model_tdd.py`.
3. `feat(resume-paused): plan each paused checkout` includes `tools/resume_paused_planner.py`, `tests/unit/tools/test_resume_paused_planner/__init__.py`, `tests/unit/tools/test_resume_paused_planner/planner_world.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`, `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py`.
4. `docs(resume-paused): record step 5 validation` includes `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Findings and boundaries for step 5 resume-paused (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 5 resume-paused (exchange 1) (round 4)

The requestor may present the advisory recommendation for the human commit decision.

### Decision rationale for step 5 resume-paused (exchange 1) (round 4)

All carried findings are resolved within step 5. Exact identity, implementation completeness, validation and coverage evidence, staged attribution, absence of outstanding findings, and commit grouping pass. The reviewer made no substantive repairs.

### Final reviewer decision for step 5 resume-paused (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-4 -->

## Round 4 by human - Step 5 - human-confirmation

- Recorded: 2026-11-20T15:12:12+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 1 by requestor - Step 6

- Recorded: 2026-11-20T20:20:20+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 6
- Outcome: request

### Review identity for step 6 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 6
Review round: 1

### Code review evidence for step 6 resume-paused (round 1)

request_index_tree: b76ca70a1046540dece816512d87a14b56e20ddd
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): amend Q05 for code-first steps
group 1 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add the shell-free transport
group 2 path: tools/resume_paused_input.py
group 2 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 2 path: tools/resume_paused_transport.py
group 2 path: tests/unit/tools/test_resume_paused_transport/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
group 3: feat(resume-paused): add delivery ports and guard
group 3 path: tools/resume_paused_delivery_model.py
group 3 path: tools/resume_paused_guard.py
group 3 path: tests/unit/tools/test_resume_paused_guard/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
group 4: feat(resume-paused): replan one checkout per send
group 4 path: tools/resume_paused_planner.py
group 4 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
group 5: feat(resume-paused): deliver guarded pane actions
group 5 path: tools/resume_paused_delivery_checks.py
group 5 path: tools/resume_paused_delivery.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 6: docs(resume-paused): record step 6 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
staged path: tests/unit/tools/test_resume_paused_transport/__init__.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_checks.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_guard.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_transport.py
```

### Validation scope for step 6 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 6 resume-paused (round 1)

Step 6 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05. The guarded delivery runs each planned checkout under a nonblocking per-checkout OS guard, concurrently with independent checkouts and with at most one input operation per pane. Before every clear, resume, reviewer command and recovery Enter it rechecks one fresh listing (identity, protections, eligibility, the exact selector), every injected check and the pinned profile. Acceptance needs the supported profile plus the Step 1 full latest-input proof within a fixed 100-second fake-clock budget per send, and nothing is ever retyped. Codex gets at most one proven recovery Enter. The empty profile registry keeps every real pane refused before any input. The implementation check recorded `Yes. Step 6 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T20:18:46+01:00 with 7119 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `b76ca70a1046540dece816512d87a14b56e20ddd`. Each new leaf passed in focus first; the transport property tests initially exceeded the 0.1-second lifecycle CPU budget and now draw each word through one integer, with 40 examples.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` and `markdown-check` report nothing on the plan and the validation plan, the two changed Markdown files.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_guard`, `test_resume_paused_transport`, `test_resume_paused_delivery_model`, `test_resume_paused_delivery_checks`, `test_resume_paused_delivery`), with `plan_checkout` and the runner bound covered in the planner and input leaves.
- Architecture: the state machine depends only on the delivery model's ports, the fresh checks and the plan model; TUIOS argument lists and selector globs stay in the transport adapter behind `PaneTransport.select`, the native lock in the guard adapter, which uses the model's `GuardState`. The model imports adapters for typing only. Plan revalidation reuses the Step 5 planner through `plan_checkout`; Step 7's takeover enters through the `Takeover` and `PairDelivery` seam.
- Performance: one listing per send, single passes over panes and capture lines, bounded backoff within each budget, one checkout replanned per send; no `O(n^2)` or `O(n log n)` path.
- Feature integrity: `plan_run` and every Step 5 classification are unchanged; `SubprocessRunner` keeps its 30-second default, argument list, `shell=False` and inherited environment; manual resume, review, validator and claim paths are untouched; nothing writes an artifact beyond the empty guard file outside the checkout.
- Open rows (validation plan): composition by Step 8 (profile gate, agent-log reader, input provers, `PlanRecheck`, transport, guard, clock) and live host evidence (two-process guard, selector globs, ask results, draft reporting for a pane's own unsubmitted command, screen and log signatures).

### Implementation report for step 6 resume-paused (round 1)

Step 6 delivers guarded pane actions with bounded acceptance. The user amended plan Q05 on 2026-11-20, when Step 6 was launched, so Steps 6 to 8 proceed code-first against the empty profile registry; no real pane can receive input until both hosts are pinned. The step adds five modules and five test leaves, adds `plan_checkout` to the Step 5 planner and a process bound to the Step 4 runner, and amends the plan's Q05 row.

- `tools/resume_paused_guard.py`, the per-checkout OS guard (design Q07=A): `CheckoutGuard.acquire` names an empty file by the SHA-256 of the canonical checkout key in `<temp>\llm-shared-resume-paused\`, opens it non-inheritable and locks its first byte through `msvcrt.locking(LK_NBLCK)` without waiting. Another holder returns `held` (an expected skip, the new descriptor closed at once); an unopenable file, or a temporary folder inside the checkout (so possibly inside its artifact home) or unparsable, returns `unavailable`. `GuardLease` unlocks then closes in a `finally`, on every exit of its `with` block, and a second release does nothing. The OS drops the lock with the handle, so a killed invocation leaves no stale guard; the file carries no content.
- `tools/resume_paused_transport.py`, the shell-free transport: `ask_arguments` returns `tuios ask-agent --select <selector> --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>`; `enter_arguments` returns `tuios send-keys -s <session> -w <full pane id> Enter`. `selector_value` replaces each space of a live session or pane name with `*` (the draft's proven form) and refuses an empty name, any other glob character (`*`, `?`, `[`, `]`, `\`) and any non-printing or non-space blank. `resolve_selector` matches every listed pane more broadly than TUIOS does (case-insensitive, a wildcard crossing any character, slashes included) and requires the match set to be exactly the target UUID: a collision is `selector-ambiguous`, an unlisted target `selector-unresolved`, both failures before input. `TuiosTransport` adapts the delivery port: listing (`observe_panes`), `select`, capture and Enter on the 30-second runner, the ask on a runner whose bound `ASK_PROCESS_TIMEOUT_SECONDS` (110) exceeds the ask's 100 seconds. The caller environment, `TUIOS_*` included, is inherited unchanged; the ask's exit code is report-only.
- `tools/resume_paused_input.py`: `SubprocessRunner` takes its process bound as a constructor parameter, 30 seconds by default for every existing caller.
- `tools/resume_paused_delivery_model.py`, vocabulary and ports: `Phase` (clear, resume, reviewer, recovery), `DeliveryOutcome` (accepted, refused, unconfirmed, pending), `ClearOutcome` (none, redundant, confirmed, unconfirmed), `Refusal` with a `failed` severity, `GuardState`, `ActionReport`, `CheckoutDelivery` (fails on an unavailable guard or a failed action, never on contention or a pending reviewer), `SendStep`, `InputScreen` and `DeliveryProfile` (clear command, background-shell line, Codex input-box signatures), `LogKind` and `LogEvent`, and the ports `PreSendCheck`, `ProfileGate`, `AgentLog`, `Sleeper`, `PaneTransport` (with `select`), `GuardPort`, `PairDelivery` and `Takeover`, bundled in `DeliveryPorts`. `UnpinnedProfiles` refuses every pane; `NoTakeover` reports every conditional reviewer pending (`takeover-unobserved`) until Step 7. The model imports no adapter at run time; the guard uses and re-exports `GuardState`.
- `tools/resume_paused_delivery_checks.py`, fresh pre-send checks: `target_refusal` reads one fresh listing and requires the planned UUID listed once (`target-absent` skips, `pane-ambiguous` fails), in its planned session, with its planned host (`host-contradictory`, `target-host-changed` fail; a shell pane skips) and checkout (`target-checkout-changed` fails; an unusable path skips), not the caller's pane nor an excluded session or pane label, and eligible through Step 5's `input_eligibility` (busy, blocked, draft, not-ready and unknown skip; a stale working Codex pane needs a supported idle, empty-input probe). Before the recovery Enter only, a stale working status is tolerated, because the pane holds this run's own unsubmitted command, while a blocked or draft-holding pane, an idle pane that is not ready and an unknown state refuse it. `PlanRecheck` replans the checkout through `plan_checkout` from the same fresh observation and requires a planned action with the same role, host, session, pane, clear flag, kind family (a reviewer matches a later continuation), native command and marker pane, role and assignment binding; only the launch id may differ. A replanned skip keeps its reason as an expected refusal, a replanned error fails, a changed binding (prompt digest, routing or exchange) is `plan-changed`. Before the recovery Enter the target's own activity is read as ready, so only its unsubmitted command is discounted, never a duplicate or a routing change.
- `tools/resume_paused_planner.py`: `plan_checkout(request, observation, ports, root)` builds the pane index from the fresh observation and runs the same `_CheckoutPlanner` for one root, `None` when the root has no live pane or no saved prompt; `plan_run` is unchanged.
- `tools/resume_paused_delivery.py`, the state machine: `deliver_run` returns nothing for a dry run or a run-wide refusal, then runs one worker per planned checkout on a thread pool of at most eight, in plan order; `_PaneSlots` allows at most one input operation per pane across the run (`pane-in-use` fails). Each worker takes its guard without waiting (held: skipped, no listing read) and holds it through its sequence: the resume first, then each conditional reviewer handed to the injected takeover with the resume's report, or with none for a later continuation; the takeover may deliver it through `PairDelivery.deliver` with its own extra checks under the same guard. A reviewer after an unaccepted resume gets `requestor-not-accepted` and the takeover is not consulted. A planned skip is reported with its reason.
- Same module, each send: one fresh listing, `target_refusal`, the transport's `select` (not for the Enter, which names the full UUID), every injected check, then the pane's profile again, which must exist for the planned host, equal the profile of the action's earlier sends and have an input prover. A Claude send needs a readable agent log; a Codex send needs a pre-input capture whose input box, the last line opened by the pinned prefix, shows only the placeholder (other text skips as `pane-draft`; no input box, no capture or no screen signatures fail). Each send (the clear and the command) has its own 100-second budget from the ask, recovery included, with backoff 0.5, 1, 2, 4, then 5 seconds, capped at the remaining budget; the 60-second stall bound is the ask's own. Acceptance requires the Step 1 input prover's full proof from the send instant, and, for Claude, the command's prompt event in the agent log at or after it. Unproved acceptance at the deadline is `unconfirmed` and fails; nothing is retyped.
- Same module, clear: `--clear` applies to a resume action only, never a reviewer. A Claude clear is skipped as `redundant` when the log holds a clear strictly after the pause and no prompt after the last such clear; the resume is still sent. Otherwise the clear is a send of its own: Claude confirmation needs a clear event at or after the send and a fresh ready, unblocked idle or done pane; Codex confirmation needs a capture differing from the pre-input one, with the pinned cleared line and an empty input box. An unconfirmed clear fails the action with `clear-unconfirmed` and no resume.
- Same module, Codex recovery Enter: at most one per send. On each observation, a capture reading exactly this send's command in the input box, appearing once on screen, with no working line and no placeholder text below it, is followed after a one-second gap by a second capture that must be identical; then the fresh recovery checks run (including the injected checks and an unchanged profile) and, budget remaining, `send-keys` presses Enter once at the full UUID. Any other reading (other text, a working or placeholder line below, a repeat, a failed capture), an edit between captures, a refused check or a changed profile withholds the Enter for the rest of the send, with a `<phase>-recovery-withheld-<reason>` note; an empty input box withholds nothing. An Enter TUIOS refused is still spent and noted. A background-shell line in the pre-input capture is noted once and nothing else happens.
- Tests: `tests/unit/tools/test_resume_paused_guard/` (path spellings, policy cases with a declared lock primitive, two native handles contending, a blocked guard folder), `tests/unit/tools/test_resume_paused_transport/` (tdd: exact argument lists with shell metacharacters, every selector-value case, collisions by suffix, letter case and an empty wildcard, a duplicated target, both runners and `select`; pbt: plain names always resolve to their own pane, names with another glob character never get a selector, any command is the single last argument, each word drawn through one integer, 40 examples), `tests/unit/tools/test_resume_paused_delivery_model/`, `tests/unit/tools/test_resume_paused_delivery_checks/` (every target refusal and recovery readiness, `PlanRecheck` over the real planner world: unchanged, changed digest, later duplicate, uncertain history, removed prompt, busy target at resume and at recovery, reviewer continuation, unreadable markers), `tests/unit/tools/test_resume_paused_delivery/` (`delivery_world.py`; tdd for run, guard, concurrency through a barrier, per-pane exclusion through events, profile, prover and log refusals, Claude acceptance and deadlines, clears, pairs and the takeover seam; tdd for Codex refusals, recovery used, withheld for each condition, never repeated, budgets of 100 and 99.5 spent seconds, Codex clears and the screen readings), plus `test_resume_paused_planner_replan_tdd.py` and the runner bound in the input leaf. No test starts a process or sleeps; every deadline runs on a fake clock.
- Deviations: delivery is split into vocabulary, checks and state machine (split guidance), each module with its own leaf; `plan_checkout` joins the planner (558 lines, in the 550 to 650 band); the plan's two-process guard test uses two independent OS handles in one process, which Windows byte-range locking treats exactly as two processes, because this repository's tests never start a process (write-fast-python-tests, process audit without permissions); the cross-process run and the other host behaviors are open live rows in the validation plan, with the composition rows Step 8 owns.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step6.journal.md` and `.reviews/a.resume-paused.step6.handoff.md`.

### Change summary for step 6 resume-paused (round 1)

Twenty-four staged paths in six `a.commit` groups, in this order:

1. `docs(resume-paused): amend Q05 for code-first steps`: `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add the shell-free transport`: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`, `tools/resume_paused_transport.py` and the `tests/unit/tools/test_resume_paused_transport` package (package file, tdd and pbt files).
3. `feat(resume-paused): add delivery ports and guard`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_guard.py` and the `tests/unit/tools/test_resume_paused_guard` package (package file and tdd file).
4. `feat(resume-paused): replan one checkout per send`: `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`.
5. `feat(resume-paused): deliver guarded pane actions`: `tools/resume_paused_delivery_checks.py`, `tools/resume_paused_delivery.py`, the `tests/unit/tools/test_resume_paused_delivery` package (package file, `delivery_world.py`, two tdd files), and the `tests/unit/tools/test_resume_paused_delivery_checks` and `tests/unit/tools/test_resume_paused_delivery_model` packages (package file and tdd file each).
6. `docs(resume-paused): record step 6 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 6 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis in the transcript.

### Reviewer focus for step 6 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-1 -->

## Round 1 by reviewer - Step 6

- Recorded: 2026-11-20T20:26:16+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 resume-paused (exchange 1) (round 1)

Baseline index tree: b76ca70a1046540dece816512d87a14b56e20ddd

Assessed index tree: b76201f38949e5f053a71f02ce042f14b0982070

### Implementation check for step 6 resume-paused (exchange 1) (round 1)

Result:

No. Step 6 has NOT been fully implemented. The six outstanding findings affect safe delivery and guard handling. The November 20 Q05 amendment permits code-first work on steps 6–8 with an empty profile registry.

Validation plan effects:

Updated the step 6 verdict and recorded all six findings under “Missing work for Step 6” in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 6 resume-paused (exchange 1) (round 1)

The writer reported 7,119 passing tests and 100% line coverage over `tools`. The reviewer checked the staged tree and commit plan independently and did not rerun the suite. The guard evidence uses two handles. The two-process check and live host evidence remain open.

### Resolved validation set and sources for step 6 resume-paused (exchange 1) (round 1)

The resolved whole-suite validation command is `ghog day --full=speed --whole-suite`. The reviewer also checked the staged metadata diff for whitespace and linted the validation plan. Both passed.

### Resolver drift and direction for step 6 resume-paused (exchange 1) (round 1)

None. `prompt_workflow.bat scope day --full=speed` resolved to the command in the request.

### Repository state around validation for step 6 resume-paused (exchange 1) (round 1)

The request tree matched baseline `b76ca70a1046540dece816512d87a14b56e20ddd`. The after-state showed only the attributable validation-plan and index changes. The umbrella comparison was inapplicable and unchanged.

### Repair inventory for step 6 resume-paused (exchange 1) (round 1)

Repairs made:

- The reviewer corrected the step 6 verdict and staged the six findings in the validation plan. No implementation repair was performed.

Paths staged:

- Reviewer-staged review metadata only:
- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 6 resume-paused (exchange 1) (round 1)

The independent commit-plan checker returned `valid` and `ready: true` with zero diagnostics. The six groups account for all 24 staged paths in the requested order.

1. `docs(resume-paused): amend Q05 for code-first steps`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.md`
2. `feat(resume-paused): add the shell-free transport`
   - `tools/resume_paused_input.py`
   - `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`
   - `tools/resume_paused_transport.py`
   - `tests/unit/tools/test_resume_paused_transport/__init__.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py`
3. `feat(resume-paused): add delivery ports and guard`
   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_guard.py`
   - `tests/unit/tools/test_resume_paused_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py`
4. `feat(resume-paused): replan one checkout per send`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`
5. `feat(resume-paused): deliver guarded pane actions`
   - `tools/resume_paused_delivery_checks.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_delivery/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery/delivery_world.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
6. `docs(resume-paused): record step 6 validation`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 6 resume-paused (exchange 1) (round 1)

Unresolved findings:

- `_ActionDelivery.prepare` skips `transport.select` in `Phase.RECOVERY`. A second pane can acquire a colliding name after the ask and the code still presses Enter. Repeat selector resolution for the fresh listing, retain full-UUID targeting for Enter, and test the collision between the ask and recovery.
- `_ActionDelivery._send` can accept proof that finishes past the 100-second deadline. A proof started at 99.5 seconds can finish at 102 and still return `ACCEPTED`. Synchronous asks and observations also have independent process timeouts. Propagate the remaining bound to blocking operations and check expiry after each proof before accepting or acting. Test a slow successful proof, capture and ask using the fake clock.
- `read_input` treats an exact command line followed by arbitrary text as the complete editable input unless that text contains a placeholder or matches Working. A multiline draft beginning with the marked command can therefore receive Enter. Require the profile to account for the entire input box, reject unrecognized continuation lines, and put the last ownership capture after potentially slow fresh checks. Cover multiline input and an edit during revalidation.
- `cleared` accepts a pre-existing clear banner plus any unrelated screen change. A clock or status-line update can confirm a clear that never happened, allowing resume in the old conversation. Require a transition attributable to this clear and test an unchanged old banner with only an unrelated line changing.
- `_inside` checks descendants but misses equality. If the checkout itself is the temporary guard folder, the adapter opens its guard inside the checkout. Reject equality before opening and test with the guard folder as checkout root.
- `NativeFileLock.try_lock` maps every locking `OSError` to contention, and a seek error can escape without closing the descriptor. Distinguish a lock held by another handle from an unavailable guard, release the descriptor on acquisition errors, and report failure only for the affected checkout.

Boundary-crossing work: None.

### Writer instructions for step 6 resume-paused (exchange 1) (round 1)

Address the six findings, add the indicated regression coverage, rerun the resolved validation command and refresh group 6’s completion evidence before submitting the next round. Keep the two-process guard proof and host evidence identified as open until verified.

### Decision rationale for step 6 resume-paused (exchange 1) (round 1)

Changes requested. Recovery can submit the wrong input, observe a late proof as success, or accept a stale clear. Guard placement and error classification also need correction.

### Final reviewer decision for step 6 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-1 -->

## Round 2 by requestor - Step 6

- Recorded: 2026-11-20T20:58:43+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 6
Review round: 2

### Code review evidence for step 6 resume-paused (round 2)

request_index_tree: 9e0894376fbdc1cd390092cd67208c8a71cc210a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): amend Q05 for code-first steps
group 1 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add the shell-free transport
group 2 path: tools/resume_paused_input.py
group 2 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 2 path: tools/resume_paused_transport.py
group 2 path: tests/unit/tools/test_resume_paused_transport/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
group 3: feat(resume-paused): add delivery ports and guard
group 3 path: tools/resume_paused_delivery_model.py
group 3 path: tools/resume_paused_guard.py
group 3 path: tests/unit/tools/test_resume_paused_guard/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
group 4: feat(resume-paused): replan one checkout per send
group 4 path: tools/resume_paused_planner.py
group 4 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
group 5: feat(resume-paused): deliver guarded pane actions
group 5 path: tools/resume_paused_delivery_checks.py
group 5 path: tools/resume_paused_delivery.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 6: docs(resume-paused): record step 6 validation
group 6 path: .vscode/settings.json
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
staged path: tests/unit/tools/test_resume_paused_transport/__init__.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_checks.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_guard.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_transport.py
```

### Validation scope for step 6 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 6 resume-paused (round 2)

Step 6 is fully implemented after the round 1 repairs, code-first under the user's 2026-11-20 amendment of plan Q05. All six round 1 findings are repaired with regression tests:

- the recovery Enter's checks resolve the selector again;
- every blocking call of a send is bounded by its remaining budget, and no proof or capture completing at or after the deadline is acted on;
- the whole Codex input box is read through the pinned footer, and the last ownership capture follows the recovery checks;
- a Codex clear needs one more cleared line than before;
- the guard refuses a folder equal to the checkout and tells contention from failure.

The implementation check records `Yes. Step 6 has been fully implemented.` again, with the repairs listed.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T20:57:55+01:00 with 7137 tests, 100% coverage, no outlier and no exclusion, slowest call 0.36 s, on index tree `9e0894376fbdc1cd390092cd67208c8a71cc210a`. The repaired leaves passed in focus first (221 tests). The previous attempt of this walk stopped in check.bat on one typing error in a test fake (`try_lock` still returned `bool`), now fixed.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check. `spellcheck.bat check` reports no unknown word on the validation plan once `EACCES` joined the project words.
- Coverage: 100% over `tools`. Each new module still has its own leaf, and the repaired branches have dedicated cases: held and unavailable lock states, a raising attempt, the checkout as guard folder, a native seek error, slow proofs and captures, the granted bounds, a recovery collision, multiline input, an edit during the checks, and the old clear banner.
- Architecture: unchanged boundaries. The bound is part of the `PaneTransport` port, and the TUIOS adapter builds one bounded runner per call. The model keeps the screen signatures, the guard adapter classifies its own OS errors, and the state machine owns the deadline decisions.
- Performance: one listing per send; single passes over panes and capture lines, now including the footer and banner counts; bounded backoff; one checkout replanned per send. The module sizes stay below the 550-line mark except the planner (558, unchanged since round 1).
- Feature integrity: `plan_run`, the Step 5 classifications and `SubprocessRunner`'s 30-second default are unchanged. Manual resume, review, validator and claim paths are untouched; nothing writes an artifact beyond the empty guard file outside the checkout.
- Open rows (validation plan):
  - composition by Step 8: profile gate, agent-log reader, input provers, `PlanRecheck`, the bounded runner factory, guard and clock;
  - live host evidence: two-process guard, selector globs, ask results, draft reporting, screen and log signatures, the footer line, and whether a new conversation wipes an earlier cleared line.

### Implementation report for step 6 resume-paused (round 2)

Step 6 delivers guarded pane actions with bounded acceptance. The user amended plan Q05 on 2026-11-20, when Step 6 was launched, so Steps 6 to 8 proceed code-first against the empty profile registry; no real pane can receive input until both hosts are pinned. The step adds five modules and five test leaves, adds `plan_checkout` to the Step 5 planner and a process bound to the Step 4 runner, and amends the plan's Q05 row. Round 2 repairs the six round 1 findings.

- `tools/resume_paused_guard.py`, the per-checkout OS guard (design Q07=A): `CheckoutGuard.acquire` names an empty file by the SHA-256 of the canonical checkout key in `<temp>\llm-shared-resume-paused\`, refuses a guard folder inside or equal to the checkout (or unparsable) before opening anything, opens the file non-inheritable and asks the primitive to lock its first byte without waiting. `NativeFileLock.try_lock` returns `acquired`, `held` for `EACCES` or `EDEADLK` (another handle holds it), and `unavailable` for any other lock or seek error. Every non-acquired state, and a raising attempt, closes the descriptor; `held` is an expected skip, `unavailable` fails that checkout alone. `GuardLease` unlocks then closes in a `finally` on every exit of its `with` block, and a second release does nothing. The OS drops the lock with the handle; the file carries no content.
- `tools/resume_paused_transport.py`, the shell-free transport: `ask_arguments` returns `tuios ask-agent --select <selector> --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>`; `enter_arguments` returns `tuios send-keys -s <session> -w <full pane id> Enter`. `selector_value` replaces each space of a live session or pane name with `*` and refuses an empty name, any other glob character and any non-printing or non-space blank. `resolve_selector` matches every listed pane more broadly than TUIOS (case-insensitive, a wildcard crossing any character) and requires the match set to be exactly the target UUID. `TuiosTransport(runner_for)` runs `observe`, `capture`, `ask` and `enter`, each on a runner the factory builds for the seconds the caller grants; `select` does no IO. The caller environment is inherited unchanged; the ask's exit code is report-only.
- `tools/resume_paused_input.py`: `SubprocessRunner` takes its process bound as a constructor parameter, 30 seconds by default for every existing caller; the delivery's factory builds one per call.
- `tools/resume_paused_delivery_model.py`, vocabulary and ports: `Phase`, `DeliveryOutcome`, `ClearOutcome`, `Refusal` with a `failed` severity, `GuardState`, `ActionReport`, `CheckoutDelivery`, `SendStep`, `InputScreen` (input prefix, placeholder, working, cleared and, since round 2, footer signatures) and `DeliveryProfile`, `LogKind` and `LogEvent`, `ACTION_BUDGET` (100 s), `CALL_BOUND_SECONDS` (30 s), and the ports `PreSendCheck`, `ProfileGate`, `AgentLog`, `Sleeper`, `PaneTransport` (whose blocking calls take a `timeout`), `GuardPort`, `PairDelivery` and `Takeover`, bundled in `DeliveryPorts`. `UnpinnedProfiles` refuses every pane; `NoTakeover` reports every conditional reviewer pending until Step 7. The model imports no adapter at run time.
- `tools/resume_paused_delivery_checks.py`, fresh pre-send checks: `target_refusal` requires the planned UUID listed once, in its planned session, host and checkout, not the caller's pane nor an excluded session or pane label, and eligible through Step 5's `input_eligibility`; before the recovery Enter only, a stale working status is tolerated while a blocked or draft-holding pane, an idle pane that is not ready and an unknown state refuse it. `PlanRecheck` replans the checkout through `plan_checkout` from the same fresh observation and requires the same role, host, session, pane, clear flag, kind family, native command and marker pane, role and binding; before the Enter the target's own activity is read as ready.
- `tools/resume_paused_planner.py`: `plan_checkout(request, observation, ports, root)` runs the same checkout planner for one root from a fresh observation, `None` without a live pane or a saved prompt.
- `tools/resume_paused_delivery.py`, run and guard: `deliver_run` returns nothing for a dry run or a run-wide refusal, then runs one worker per planned checkout on a thread pool of at most eight; at most one input operation per pane. Each worker holds its guard through the resume, then each conditional reviewer handed to the injected takeover, which may deliver it under the same guard with extra checks; no reviewer after an unaccepted resume.
- Same module, each send: one fresh listing (bounded by the remaining budget during a send, 30 seconds before), `target_refusal`, the transport's `select` for every phase (round 2: the recovery Enter too, which still names the full UUID), every injected check, then the pane's profile again, unchanged within the action and with an input prover. A Claude send needs a readable agent log; a Codex send needs a pre-input capture whose input box shows only the placeholder with only the pinned footer below it (other text skips as `pane-draft`; no input box, an unrecognized line below, no capture or no screen signatures fail). Each send has its own 100-second budget from the ask; the ask's bound is the whole budget, every later call's bound is the remaining budget capped at 30 seconds. After each acceptance proof the clock is read again: a proof completing at or after the deadline is not acceptance (round 2). Unproved acceptance is `unconfirmed`; nothing is retyped.
- Same module, clear: `--clear` applies to a resume action only. A Claude clear is skipped as `redundant` when the log holds a clear strictly after the pause and no prompt after the last one; otherwise Claude confirmation needs a clear event at or after the send and a fresh ready pane, and Codex confirmation needs one more pinned cleared line than the pre-clear capture on an empty input box (round 2: an old banner with an unrelated change never confirms). An unconfirmed clear fails the action with no resume.
- Same module, Codex recovery Enter, at most one per send (round 2 order): a capture reading exactly this send's command as the whole input box (only the pinned footer below, no working line, no placeholder, the command once on screen); a one-second gap; the fresh recovery checks with the selector and the unchanged profile; a last capture that must be identical; then, budget remaining, one `send-keys` Enter bounded by the remaining budget. A capture completing at or after the deadline stops the attempt. Any other reading, an edit (including one made during the checks), a refused check or a changed profile withholds the Enter for the rest of the send, with a note; an empty input box withholds nothing. A refused Enter is still spent. A background-shell line is noted only.
- Tests: `tests/unit/tools/test_resume_paused_guard/` (path spellings, held and unavailable states, a raising attempt, the checkout as guard folder, folders in, beside or unparsable, release on errors, two native handles contending, a blocked folder, a native seek failure that is not contention), `tests/unit/tools/test_resume_paused_transport/` (argument lists with metacharacters, selector cases, the bounds granted to each call; properties as in round 1), `tests/unit/tools/test_resume_paused_delivery_model/`, `tests/unit/tools/test_resume_paused_delivery_checks/` (unchanged), `tests/unit/tools/test_resume_paused_delivery/` (`delivery_world.py` records every granted bound and lets captures and proofs spend declared time; round 2 adds the bounds of a recovered send, a proof finishing after the deadline, slow first and last ownership captures, a new selector collision at recovery, a multiline draft, an edit during the recovery checks, an unrecognized line below an empty box, an empty footer signature, the old clear banner through `cleared` and through a delivery, and a second banner confirming), plus `test_resume_paused_planner_replan_tdd.py` and the runner bound in the input leaf. No test starts a process or sleeps.
- Deviations: as in round 1 (delivery split into vocabulary, checks and state machine with one leaf per module; `plan_checkout` in the planner, 558 lines; the two-process guard test through two OS handles in one process; open composition and live rows in the validation plan). The live rows now include the Codex footer signature and whether a new conversation wipes an earlier cleared line. `.vscode/settings.json` gains `EACCES`.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step6.journal.md` and `.reviews/a.resume-paused.step6.handoff.md`.

### Change summary for step 6 resume-paused (round 2)

Twenty-five staged paths in six `a.commit` groups, in this order:

1. `docs(resume-paused): amend Q05 for code-first steps`: `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add the shell-free transport`: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`, `tools/resume_paused_transport.py` and the `tests/unit/tools/test_resume_paused_transport` package (package file, tdd and pbt files).
3. `feat(resume-paused): add delivery ports and guard`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_guard.py` and the `tests/unit/tools/test_resume_paused_guard` package (package file and tdd file).
4. `feat(resume-paused): replan one checkout per send`: `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`.
5. `feat(resume-paused): deliver guarded pane actions`: `tools/resume_paused_delivery_checks.py`, `tools/resume_paused_delivery.py`, the `tests/unit/tools/test_resume_paused_delivery` package (package file, `delivery_world.py`, two tdd files), and the `tests/unit/tools/test_resume_paused_delivery_checks` and `tests/unit/tools/test_resume_paused_delivery_model` packages (package file and tdd file each).
6. `docs(resume-paused): record step 6 validation`: `.vscode/settings.json` (the `EACCES` project word) and `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 2 changes paths in groups 2, 3, 5 and 6 and adds `.vscode/settings.json` to group 6; group membership otherwise, order and subjects are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 6 resume-paused (round 2)

Writer response:

All six round 1 findings are accepted and repaired; there is no disagreement. Your staged Step 6 rows were the starting point of the updated validation plan, which reads Yes again with the round 1 repairs recorded and the missing-work list removed.

- **Selector at recovery**: `_ActionDelivery.prepare` now resolves the transport selector for every phase, recovery included, from the same fresh listing; a refusal withholds the Enter (`resume-recovery-withheld-selector-ambiguous`), and the Enter still names the full UUID through `send-keys -w`. Regression: a second pane named `Codex-api` appearing in the recovery listing.
- **Deadline after slow calls**: every blocking transport call now takes the bound its caller grants (`PaneTransport.observe/capture/ask/enter(..., timeout)`); `TuiosTransport` takes a runner factory and builds one bounded runner per call. Inside a send the bound is the remaining budget (the ask gets the whole 100 seconds, later calls at most 30 seconds or what is left); before a send it is `CALL_BOUND_SECONDS` (30). The acceptance loop re-reads the clock after each proof and breaks when the proof completed at or after the deadline; the first and last ownership captures are followed by the same expiry check before any further step or the Enter. The input prover and the agent log are file reads behind Step 1 and Step 8 ports without a timeout parameter, so their late completion is handled by that expiry check rather than a propagated bound. Regressions: a proof finishing at 101 seconds is unconfirmed with no further read; a slow first or last ownership capture sends no Enter; the exact bounds granted to every call of a recovered send are asserted.
- **Whole input box**: `InputScreen` gains `footer_pattern`; every line below the input line must fully match it (no line may follow when it is empty), so a multiline draft, a working line or a placeholder line below the input reads as other text, for the recovery Enter, the pre-input empty check (an unrecognized line below an empty box fails as `screen-unsupported`) and the clear confirmation. The recovery order is now: first capture, gap, fresh recovery checks, last capture, which must be identical, expiry check, Enter. Regressions: a multiline draft starting with the exact command, an unrecognized line below an empty box, an empty footer signature, and an edit made while the recovery checks run (an injected check rewrites the screen) withholding the Enter as `changed`.
- **Clear banner**: `cleared` now requires one more pinned cleared line in the post-clear capture than in the pre-clear capture, on an empty input box; an old banner with only an unrelated line changing never confirms the clear. If a pinned Codex release wipes the screen on a new conversation, a pane already cleared before the run fails its clear closed; the validation plan records that as a live row. Regressions: the old banner with a clock line changing, through `cleared` and through a full delivery that then sends no resume, and a second banner confirming.
- **Guard folder equal to the checkout**: `_inside` rejects equality again, before any open. Regression: a checkout at `<temp>\llm-shared-resume-paused`.
- **Lock error classification**: `LockPrimitive.try_lock` returns a `GuardState`; `NativeFileLock` maps only `EACCES` and `EDEADLK` to `held` (measured: contention raises `EACCES` on this host) and any other lock or seek error, `EBADF` included, to `unavailable`, which fails that checkout alone; `CheckoutGuard.acquire` closes the descriptor for every non-acquired state and on a raising attempt. Regressions: both states through a declared primitive, a raising attempt, and the native primitive on a closed descriptor.
- **Commit plan**: groups, order and subjects are unchanged; the bodies of groups 2, 3, 5 and 6 describe the repairs, and `.vscode/settings.json` joins group 6 because the validation plan needed `EACCES` in the project words.

### Reviewer focus for step 6 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-2 -->

## Round 2 by reviewer - Step 6

- Recorded: 2026-11-20T21:03:53+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 resume-paused (exchange 1) (round 2)

Baseline index tree: 9e0894376fbdc1cd390092cd67208c8a71cc210a

Assessed index tree: fabe23a7d1f1e20ee739e910f2d6d22359ffe03c

### Implementation check for step 6 resume-paused (exchange 1) (round 2)

Result:

No. Step 6 has NOT been fully implemented. Source inspection confirms the selector recheck, last capture after revalidation, clear-banner transition, root equality check and guard acquisition handling. Two round 1 findings remain partially resolved.

Validation plan effects:

Updated the round 2 Step 6 verdict and entered the two outstanding cases under “Missing work for Step 6” in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 6 resume-paused (exchange 1) (round 2)

The writer reports 7,137 passing tests and 100% coverage over `tools` on the request tree. The 221 focused tests and the reported checks passed. The reviewer traced the concrete input prover, recovery reader and staged tests. Neither remaining case is covered. The reviewer did not rerun the suite.

### Resolved validation set and sources for step 6 resume-paused (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` (project source, whole scope). Reviewer metadata checks passed for staged whitespace and Markdown lint.

### Resolver drift and direction for step 6 resume-paused (exchange 1) (round 2)

None. The current scope resolver matched the request.

### Repository state around validation for step 6 resume-paused (exchange 1) (round 2)

The request tree matched `9e0894376fbdc1cd390092cd67208c8a71cc210a`. The only differences after assessment were the attributable validation-plan update and its index entry. No umbrella applies.

### Repair inventory for step 6 resume-paused (exchange 1) (round 2)

Repairs made:

- Reviewer metadata only. Recorded both findings and revised the verdict. No reviewer implementation or test repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 6 resume-paused (exchange 1) (round 2)

The independent checker returned `valid`, `ready: true`, zero diagnostics. All 25 staged paths occur in the six groups in dependency order. The group 5 claim about every blocking call and the group 6 completion claim need updating after repairs.

1. `docs(resume-paused): amend Q05 for code-first steps`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.md`
2. `feat(resume-paused): add the shell-free transport`
   - `tools/resume_paused_input.py`
   - `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`
   - `tools/resume_paused_transport.py`
   - `tests/unit/tools/test_resume_paused_transport/__init__.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py`
3. `feat(resume-paused): add delivery ports and guard`
   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_guard.py`
   - `tests/unit/tools/test_resume_paused_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py`
4. `feat(resume-paused): replan one checkout per send`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`
5. `feat(resume-paused): deliver guarded pane actions`
   - `tools/resume_paused_delivery_checks.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_delivery/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery/delivery_world.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
6. `docs(resume-paused): record step 6 validation`
   - `.vscode/settings.json`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 6 resume-paused (exchange 1) (round 2)

Unresolved findings:

- `_ActionDelivery._accepted` calls `CodexInputProver.prove` with `carried=None`. That concrete prover calls `self._capture.capture(pane)` without a remaining-time argument. A proof begun at 99.5 seconds can run a TUIOS capture with its independent 30-second timeout while holding the checkout guard. The late result is discarded, but the observation exceeds the fixed budget. Pass the deadline through the proof path and bound its nested capture. Also stop before starting downstream work when a slow log read or recovery recheck has consumed the budget. Use a fake clock with the concrete prover and a recording capture to verify the final half-second bound and zero calls after expiry.
- `_closed` accepts any number of lines matching `footer_pattern`, including zero. With the staged single-footer profile, a capture containing the command, a draft continuation identical to the footer, and the real footer passes `read_input` as `COMMAND`. Two identical captures can therefore authorize Enter on a multiline draft. A truncated capture ending at the command also passes despite the configured footer. Require the complete footer layout, including its expected count and order, before treating the input as empty or owned. Cover duplicated and missing footers through recovery and assert that neither sends Enter.

Boundary-crossing work: None.

### Writer instructions for step 6 resume-paused (exchange 1) (round 2)

Carry the budget through nested acceptance calls, prevent new work once the deadline expires, and require exact evidence for the configured footer layout. Add the regression cases in the findings, rerun the resolved whole-suite validation and update the validation record and affected commit bodies.

### Decision rationale for step 6 resume-paused (exchange 1) (round 2)

Changes requested. The real prover can hold the guard past 100 seconds and a footer-shaped draft continuation can receive recovery Enter. Live host and two-process verification remain open under the Q05 amendment.

### Final reviewer decision for step 6 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-2 -->

## Round 3 by requestor - Step 6

- Recorded: 2026-11-20T22:06:26+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 6
Review round: 3

### Code review evidence for step 6 resume-paused (round 3)

request_index_tree: 6aea09375a2c7e9ad56cdb525105cf6900b65d3c
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): amend Q05 for code-first steps
group 1 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add the shell-free transport
group 2 path: tools/resume_paused_input.py
group 2 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 2 path: tools/resume_paused_transport.py
group 2 path: tests/unit/tools/test_resume_paused_transport/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
group 3: feat(resume-paused): add delivery ports and guard
group 3 path: tools/resume_paused_delivery_model.py
group 3 path: tools/resume_paused_guard.py
group 3 path: tests/unit/tools/test_resume_paused_guard/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
group 4: feat(resume-paused): replan one checkout per send
group 4 path: tools/resume_paused_planner.py
group 4 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
group 5: feat(resume-paused): deliver guarded pane actions
group 5 path: tools/resume_paused_delivery_checks.py
group 5 path: tools/resume_paused_delivery.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 6: docs(resume-paused): record step 6 validation
group 6 path: .vscode/settings.json
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
staged path: tests/unit/tools/test_resume_paused_transport/__init__.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_checks.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_guard.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_transport.py
```

### Validation scope for step 6 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 6 resume-paused (round 3)

Step 6 is fully implemented after the round 2 repairs, code-first under the user's 2026-11-20 amendment of plan Q05. Both round 2 findings are repaired with regression tests:

- each acceptance proof uses a prover the per-host factory builds for the remaining budget, so the Codex prover's nested capture is bounded by it, and no step starts once the budget is spent;
- the lines below the Codex input line must be exactly the pinned footer layout, line by line, so a repeated, missing or footer-shaped extra line is never an empty or owned input box.

The implementation check records `Yes. Step 6 has been fully implemented.` again, with the round 2 repairs listed.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T22:05:45+01:00 with 7147 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s, on index tree `6aea09375a2c7e9ad56cdb525105cf6900b65d3c`. Two earlier attempts of this walk stopped first in check.bat (an untyped test lambda, a magic number, seven returns in `prepare`, now split into `_expiry` and `_selected`, and an MD032 in the review transcript caused by my round 2 assessment, repaired as one blank line under the user's explicit exception), then at 99% coverage (the stop after a slow recovery profile read, now covered).
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown (the transcript included), ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan.
- Coverage: 100% over `tools`; the round 2 cases cover the prover bound, the slow log read, the slow recovery check, the slow recovery profile read and the footer layout.
- Architecture: Step 4's `InputProver` and `PaneCapture` contracts are unchanged; the bound reaches the Codex prover through the delivery's `ProverFactory` port, which Step 8 composes with a bounded pane capture. The footer layout is profile data in the model.
- Performance: one listing per send, single passes over panes and capture lines, the footer compared line by line, bounded backoff, one checkout replanned per send.
- Feature integrity: unchanged from round 2; nothing outside the delivery modules and their tests changed in this round.
- Open rows (validation plan):

  - composition by Step 8: profile gate, agent-log reader, bounded input prover factories, `PlanRecheck`, the bounded runner factory, guard and clock;
  - live host evidence: two-process guard, selector globs, ask results, draft reporting, screen and log signatures, the exact footer layout, and whether a new conversation wipes an earlier cleared line.

### Implementation report for step 6 resume-paused (round 3)

Step 6 delivers guarded pane actions with bounded acceptance. The user amended plan Q05 on 2026-11-20, when Step 6 was launched, so Steps 6 to 8 proceed code-first against the empty profile registry; no real pane can receive input until both hosts are pinned. The step adds five modules and five test leaves, adds `plan_checkout` to the Step 5 planner and a process bound to the Step 4 runner, and amends the plan's Q05 row. Round 2 repaired the six round 1 findings; round 3 repairs the two round 2 findings.

- `tools/resume_paused_guard.py`, the per-checkout OS guard (design Q07=A): `CheckoutGuard.acquire` names an empty file by the SHA-256 of the canonical checkout key in `<temp>\llm-shared-resume-paused\`, refuses a guard folder inside or equal to the checkout (or unparsable) before opening anything, opens the file non-inheritable and asks the primitive to lock its first byte without waiting. `NativeFileLock.try_lock` returns `acquired`, `held` for `EACCES` or `EDEADLK` (another handle holds it), and `unavailable` for any other lock or seek error. Every non-acquired state, and a raising attempt, closes the descriptor; `held` is an expected skip, `unavailable` fails that checkout alone. `GuardLease` unlocks then closes in a `finally` on every exit of its `with` block, and a second release does nothing. The OS drops the lock with the handle; the file carries no content.
- `tools/resume_paused_transport.py`, the shell-free transport: `ask_arguments` returns `tuios ask-agent --select <selector> --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>`; `enter_arguments` returns `tuios send-keys -s <session> -w <full pane id> Enter`. `selector_value` replaces each space of a live session or pane name with `*` and refuses an empty name, any other glob character and any non-printing or non-space blank. `resolve_selector` matches every listed pane more broadly than TUIOS (case-insensitive, a wildcard crossing any character) and requires the match set to be exactly the target UUID. `TuiosTransport(runner_for)` runs `observe`, `capture`, `ask` and `enter`, each on a runner the factory builds for the seconds the caller grants; `select` does no IO. The caller environment is inherited unchanged; the ask's exit code is report-only.
- `tools/resume_paused_input.py`: `SubprocessRunner` takes its process bound as a constructor parameter, 30 seconds by default for every existing caller; the delivery's factory builds one per call.
- `tools/resume_paused_delivery_model.py`, vocabulary and ports: `Phase`, `DeliveryOutcome`, `ClearOutcome`, `Refusal` with a `failed` severity, `GuardState`, `ActionReport`, `CheckoutDelivery`, `SendStep`, `InputScreen` (input prefix, placeholder, working and cleared signatures and, since round 3, `footer_lines`, the exact footer layout) and `DeliveryProfile`, `LogKind` and `LogEvent`, `ACTION_BUDGET` (100 s), `CALL_BOUND_SECONDS` (30 s), and the ports `PreSendCheck`, `ProfileGate`, `AgentLog`, `Sleeper`, `PaneTransport` (whose blocking calls take a `timeout`), `GuardPort`, `PairDelivery` and `Takeover`, bundled in `DeliveryPorts`, whose `provers` hold one `ProverFactory` per host (round 3). `UnpinnedProfiles` refuses every pane; `NoTakeover` reports every conditional reviewer pending until Step 7. The model imports no adapter at run time.
- `tools/resume_paused_delivery_checks.py`, fresh pre-send checks: `target_refusal` requires the planned UUID listed once, in its planned session, host and checkout, not the caller's pane nor an excluded session or pane label, and eligible through Step 5's `input_eligibility`; before the recovery Enter only, a stale working status is tolerated while a blocked or draft-holding pane, an idle pane that is not ready and an unknown state refuse it. `PlanRecheck` replans the checkout through `plan_checkout` from the same fresh observation and requires the same role, host, session, pane, clear flag, kind family, native command and marker pane, role and binding; before the Enter the target's own activity is read as ready.
- `tools/resume_paused_planner.py`: `plan_checkout(request, observation, ports, root)` runs the same checkout planner for one root from a fresh observation, `None` without a live pane or a saved prompt.
- `tools/resume_paused_delivery.py`, run and guard: `deliver_run` returns nothing for a dry run or a run-wide refusal, then runs one worker per planned checkout on a thread pool of at most eight; at most one input operation per pane. Each worker holds its guard through the resume, then each conditional reviewer handed to the injected takeover, which may deliver it under the same guard with extra checks; no reviewer after an unaccepted resume.
- Same module, each send: one fresh listing (bounded by the remaining budget during a send, 30 seconds before), `target_refusal`, the transport's `select` for every phase (round 2: the recovery Enter too, which still names the full UUID), every injected check, then the pane's profile again, unchanged within the action and with an input prover. A Claude send needs a readable agent log; a Codex send needs a pre-input capture whose input box shows only the placeholder with exactly the pinned footer layout below it (other text skips as `pane-draft`; no input box, an unrecognized line below, no capture or no screen signatures fail). Each send has its own 100-second budget from the ask; the ask's bound is the whole budget, every later call's bound is the remaining budget capped at 30 seconds. After each acceptance proof the clock is read again: a proof completing at or after the deadline is not acceptance (round 2). Each proof uses a prover the factory builds for the remaining budget, so the Codex prover's nested capture is bounded by it, and no step starts once the budget is spent: no prover after a slow prompt read, no listing after a slow clear-event read, `deadline-passed` after a slow listing or check in `prepare`, no last capture after slow recovery checks (round 3). Unproved acceptance is `unconfirmed`; nothing is retyped.
- Same module, clear: `--clear` applies to a resume action only. A Claude clear is skipped as `redundant` when the log holds a clear strictly after the pause and no prompt after the last one; otherwise Claude confirmation needs a clear event at or after the send and a fresh ready pane, and Codex confirmation needs one more pinned cleared line than the pre-clear capture on an empty input box (round 2: an old banner with an unrelated change never confirms). An unconfirmed clear fails the action with no resume.
- Same module, Codex recovery Enter, at most one per send (round 2 order): a capture reading exactly this send's command as the whole input box (exactly the pinned footer layout below, one line per entry in order, no working line, no placeholder, the command once on screen); a one-second gap; the fresh recovery checks with the selector and the unchanged profile; a last capture that must be identical; then, budget remaining, one `send-keys` Enter bounded by the remaining budget. A capture completing at or after the deadline stops the attempt. Any other reading, an edit (including one made during the checks), a refused check or a changed profile withholds the Enter for the rest of the send, with a note; an empty input box withholds nothing. A refused Enter is still spent. A background-shell line is noted only.
- Tests: `tests/unit/tools/test_resume_paused_guard/` (path spellings, held and unavailable states, a raising attempt, the checkout as guard folder, folders in, beside or unparsable, release on errors, two native handles contending, a blocked folder, a native seek failure that is not contention), `tests/unit/tools/test_resume_paused_transport/` (argument lists with metacharacters, selector cases, the bounds granted to each call; properties as in round 1), `tests/unit/tools/test_resume_paused_delivery_model/`, `tests/unit/tools/test_resume_paused_delivery_checks/` (unchanged), `tests/unit/tools/test_resume_paused_delivery/` (`delivery_world.py` records every granted bound and lets captures and proofs spend declared time; round 2 adds the bounds of a recovered send, a proof finishing after the deadline, slow first and last ownership captures, a new selector collision at recovery, a multiline draft, an edit during the recovery checks, an unrecognized line below an empty box, an empty footer signature, the old clear banner through `cleared` and through a delivery, and a second banner confirming; round 3 adds the concrete `CodexInputProver` with a recording capture granted the last half second and no call after expiry, a slow log read building no prover, the bound granted to a prover, a recovery check and a recovery profile read spending the budget, and repeated, missing and invalid footer lines through recovery and `read_input`), plus `test_resume_paused_planner_replan_tdd.py` and the runner bound in the input leaf. No test starts a process or sleeps.
- Deviations: as in round 1 (delivery split into vocabulary, checks and state machine with one leaf per module; `plan_checkout` in the planner, 558 lines; the two-process guard test through two OS handles in one process; open composition and live rows in the validation plan). The live rows now include the Codex footer signature and whether a new conversation wipes an earlier cleared line. `.vscode/settings.json` gains `EACCES`.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step6.journal.md` and `.reviews/a.resume-paused.step6.handoff.md`.

### Change summary for step 6 resume-paused (round 3)

Twenty-five staged paths in six `a.commit` groups, in this order:

1. `docs(resume-paused): amend Q05 for code-first steps`: `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add the shell-free transport`: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`, `tools/resume_paused_transport.py` and the `tests/unit/tools/test_resume_paused_transport` package (package file, tdd and pbt files).
3. `feat(resume-paused): add delivery ports and guard`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_guard.py` and the `tests/unit/tools/test_resume_paused_guard` package (package file and tdd file).
4. `feat(resume-paused): replan one checkout per send`: `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`.
5. `feat(resume-paused): deliver guarded pane actions`: `tools/resume_paused_delivery_checks.py`, `tools/resume_paused_delivery.py`, the `tests/unit/tools/test_resume_paused_delivery` package (package file, `delivery_world.py`, two tdd files), and the `tests/unit/tools/test_resume_paused_delivery_checks` and `tests/unit/tools/test_resume_paused_delivery_model` packages (package file and tdd file each).
6. `docs(resume-paused): record step 6 validation`: `.vscode/settings.json` (the `EACCES` project word) and `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 3 changes paths in groups 3, 5 and 6 only; membership, order and subjects are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 6 resume-paused (round 3)

Writer response:

Both round 2 findings are accepted and repaired; there is no disagreement. Your staged Step 6 rows were the starting point of the updated validation plan, which reads Yes again with the round 2 repairs recorded and the missing-work list removed.

- **Deadline through the proof path**: `DeliveryPorts.provers` now holds one `ProverFactory` per host (`Callable[[float], InputProver]`). Each acceptance proof calls the factory with the send's remaining budget (at most 30 seconds) and proves through the prover it returns, so the Step 8 composition builds the Codex prover with a pane capture bounded by those seconds; Step 4's `InputProver` and `PaneCapture` contracts stay unchanged. No step starts once the budget is spent: the acceptance closure returns before building a prover when the Claude prompt read ended at or after the deadline; the Claude clear confirmation does not list panes after it; `prepare` stops with `deadline-passed` after its listing and after the injected checks; the recovery stops before its last capture when the checks or the profile read spent the budget. `bound()` never grants a negative bound. Regressions: the concrete `CodexInputProver` with a recording capture, proof started half a second before the deadline, records a 0.5-second grant and no transport call follows the ask; a slow log read builds no prover; the prover of a prompt proof gets 30 seconds; a recovery check spending 45 seconds stops before the last capture and the Enter; a recovery profile read spending 45 seconds stops before the last capture too.
- **Exact footer layout**: `InputScreen.footer_pattern` became `footer_lines: tuple[str, ...]`, one whole-line pattern per expected footer line, in order. `_closed` requires exactly that many lines below the input line, each matching its own entry; an invalid pattern or an empty layout with any line below fails. It applies to the empty pre-input box, the owned command and the clear confirmation. Regressions: a repeated footer and a missing footer through recovery (no Enter, `resume-recovery-withheld-capture`) and through `read_input`, an empty box missing its footer, and an invalid footer pattern.
- **Commit plan**: groups, order and subjects are unchanged. The bodies of group 3 (model), group 5 (the budget now bounds each prover; the footer layout; new tests) and group 6 (round 1 and round 2 repairs, prover factories) follow the repairs.

### Reviewer focus for step 6 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-3 -->

## Round 3 by reviewer - Step 6

- Recorded: 2026-11-20T22:09:07+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 resume-paused (exchange 1) (round 3)

Baseline index tree: 6aea09375a2c7e9ad56cdb525105cf6900b65d3c

Assessed index tree: 39570dd570c04b75ccbd1d0ca0fbdd0f5ca75364

### Implementation check for step 6 resume-paused (exchange 1) (round 3)

Result:

No. Step 6 has NOT been fully implemented. The footer finding is resolved. The deadline finding remains open for chained checks and nested proof operations.

Validation plan effects:

Updated the Step 6 analysis and missing-work row in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 6 resume-paused (exchange 1) (round 3)

The writer reports 7,147 tests passed and 100% line coverage over `tools` on the request tree. I reviewed the concrete prover, its factory, the ordered checks, footer matching and staged regression tests. The slow-capture test uses immediate version evidence and the slow-check test supplies one check. Neither exercises a blocking first operation followed by a second. I did not repeat the suite.

### Resolved validation set and sources for step 6 resume-paused (exchange 1) (round 3)

Project validation resolved to `ghog day --full=speed --whole-suite`, whole scope. The reviewer-staged metadata delta passed its whitespace check.

### Resolver drift and direction for step 6 resume-paused (exchange 1) (round 3)

None.

### Repository state around validation for step 6 resume-paused (exchange 1) (round 3)

Request and assessed baseline both matched `6aea09375a2c7e9ad56cdb525105cf6900b65d3c`. Only the validation plan and its index entry changed during assessment. The umbrella comparison was inapplicable and unchanged.

### Repair inventory for step 6 resume-paused (exchange 1) (round 3)

Repairs made:

- Polishing-only review metadata. Recorded the verdict and the remaining deadline finding.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 6 resume-paused (exchange 1) (round 3)

The independent checker returned `valid`, `ready: true`, and zero diagnostics. All 25 staged paths are assigned once in six ordered groups. The bodies for groups 5 and 6 should reflect the remaining work when refreshed.

1. `docs(resume-paused): amend Q05 for code-first steps`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.md`
2. `feat(resume-paused): add the shell-free transport`
   - `tools/resume_paused_input.py`
   - `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`
   - `tools/resume_paused_transport.py`
   - `tests/unit/tools/test_resume_paused_transport/__init__.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py`
3. `feat(resume-paused): add delivery ports and guard`
   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_guard.py`
   - `tests/unit/tools/test_resume_paused_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py`
4. `feat(resume-paused): replan one checkout per send`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`
5. `feat(resume-paused): deliver guarded pane actions`
   - `tools/resume_paused_delivery_checks.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_delivery/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery/delivery_world.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
6. `docs(resume-paused): record step 6 validation`
   - `.vscode/settings.json`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 6 resume-paused (exchange 1) (round 3)

Unresolved findings:

- The 100-second deadline is still checked around groups of operations. In `_selected`, if the first recovery check consumes the remaining time and returns `None`, the second check still runs. In `CodexInputProver.prove`, version evidence is read before the capture, but the timeout supplied to `ProverFactory` was calculated before that read. A proof begun at 99.5 seconds can finish the version read at 100.5 seconds and then start a capture with the stale half-second grant. The outer expiry check prevents acceptance but the guard stays held during the additional work. Use one absolute deadline or a callable that computes remaining time at each boundary. Stop before each subsequent check and before each nested capture or proof read when time is exhausted. Cover two ordered recovery checks and a concrete prover whose version read consumes part or all of its remaining time. Assert that the second check and capture are skipped on expiry and that a capture started before expiry receives only the time still available.

Boundary-crossing work: None.

### Writer instructions for step 6 resume-paused (exchange 1) (round 3)

Carry the same expiry through the chain and enforce it at each operation. Exercise both a reduced remaining duration and exhaustion before the next operation. Keep the exact-footer behavior and rerun the resolved suite after repair.

### Decision rationale for step 6 resume-paused (exchange 1) (round 3)

Changes requested. An acceptance result completed after expiry is discarded, but the current code can still start additional work after the deadline while holding the checkout guard. Q05 allows the code-first assessment with production profiles and live host evidence still open.

### Final reviewer decision for step 6 resume-paused (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-3 -->

## Round 4 by requestor - Step 6

- Recorded: 2026-11-20T22:23:26+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 resume-paused (round 4)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 6
Review round: 4

### Code review evidence for step 6 resume-paused (round 4)

request_index_tree: 6e291067218a908a73f70ddfd88487c5e7cebf7f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(resume-paused): amend Q05 for code-first steps
group 1 path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
group 2: feat(resume-paused): add the shell-free transport
group 2 path: tools/resume_paused_input.py
group 2 path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
group 2 path: tools/resume_paused_transport.py
group 2 path: tests/unit/tools/test_resume_paused_transport/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
group 3: feat(resume-paused): add delivery ports and guard
group 3 path: tools/resume_paused_delivery_model.py
group 3 path: tools/resume_paused_guard.py
group 3 path: tests/unit/tools/test_resume_paused_guard/__init__.py
group 3 path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
group 4: feat(resume-paused): replan one checkout per send
group 4 path: tools/resume_paused_planner.py
group 4 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
group 5: feat(resume-paused): deliver guarded pane actions
group 5 path: tools/resume_paused_delivery_checks.py
group 5 path: tools/resume_paused_budget.py
group 5 path: tools/resume_paused_delivery.py
group 5 path: tests/unit/tools/test_resume_paused_budget/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_budget/test_resume_paused_budget_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 6: docs(resume-paused): record step 6 validation
group 6 path: .vscode/settings.json
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_budget/__init__.py
staged path: tests/unit/tools/test_resume_paused_budget/test_resume_paused_budget_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery/delivery_world.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/__init__.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py
staged path: tests/unit/tools/test_resume_paused_transport/__init__.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py
staged path: tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py
staged path: tools/resume_paused_budget.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_checks.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_guard.py
staged path: tools/resume_paused_input.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_transport.py
```

### Validation scope for step 6 resume-paused (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 6 resume-paused (round 4)

Step 6 is fully implemented after the round 3 repair, code-first under the user's 2026-11-20 amendment of plan Q05. The round 3 finding is repaired with regression tests:

- the prover factory receives the send's remaining-time callable, and the budget-bounded readers of `tools/resume_paused_budget.py` read the time left at each nested proof read and read nothing once it is spent;
- the injected checks stop before each check once the budget is spent.

The implementation check records `Yes. Step 6 has been fully implemented.` again, with the round 3 repair listed.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-20T22:22:28+01:00 with 7157 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s. Its check.bat reflowed two import blocks of staged files, restaged unchanged otherwise; the request index tree `6e291067218a908a73f70ddfd88487c5e7cebf7f` holds exactly the validated content.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown (the transcript included), ShellCheck and the end-of-file check; `spellcheck.bat check` reports no unknown word on the validation plan.
- Coverage: 100% over `tools`; the new module has its own leaf, `tests/unit/tools/test_resume_paused_budget/`.
- Architecture: the bounded readers are adapters over the Step 1 and Step 4 reader ports, composed per proof by the Step 8 factory; Step 4's contracts are unchanged; the state machine only passes the remaining-time callable and asks the deadline before each check.
- Performance: one extra clock read per nested proof read and per injected check; no new pass over panes or captures.
- File size: `tools/resume_paused_delivery.py` is 573 lines, in the 550 to 650 band below the ceiling, disclosed in the validation plan; `tools/resume_paused_budget.py` is 106.
- Feature integrity: unchanged from round 3.
- Open rows (validation plan):

  - composition by Step 8: profile gate, agent-log reader, input prover factories built from the bounded readers, `PlanRecheck`, the bounded runner factory, guard and clock;
  - live host evidence: two-process guard, selector globs, ask results, draft reporting, screen and log signatures, the exact footer layout, and whether a new conversation wipes an earlier cleared line.

### Implementation report for step 6 resume-paused (round 4)

Step 6 delivers guarded pane actions with bounded acceptance. The user amended plan Q05 on 2026-11-20, when Step 6 was launched, so Steps 6 to 8 proceed code-first against the empty profile registry; no real pane can receive input until both hosts are pinned. The step adds five modules and five test leaves, adds `plan_checkout` to the Step 5 planner and a process bound to the Step 4 runner, and amends the plan's Q05 row. Round 2 repaired the six round 1 findings, round 3 the two round 2 findings, and round 4 repairs the round 3 finding.

- `tools/resume_paused_guard.py`, the per-checkout OS guard (design Q07=A): `CheckoutGuard.acquire` names an empty file by the SHA-256 of the canonical checkout key in `<temp>\llm-shared-resume-paused\`, refuses a guard folder inside or equal to the checkout (or unparsable) before opening anything, opens the file non-inheritable and asks the primitive to lock its first byte without waiting. `NativeFileLock.try_lock` returns `acquired`, `held` for `EACCES` or `EDEADLK` (another handle holds it), and `unavailable` for any other lock or seek error. Every non-acquired state, and a raising attempt, closes the descriptor; `held` is an expected skip, `unavailable` fails that checkout alone. `GuardLease` unlocks then closes in a `finally` on every exit of its `with` block, and a second release does nothing. The OS drops the lock with the handle; the file carries no content.
- `tools/resume_paused_transport.py`, the shell-free transport: `ask_arguments` returns `tuios ask-agent --select <selector> --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>`; `enter_arguments` returns `tuios send-keys -s <session> -w <full pane id> Enter`. `selector_value` replaces each space of a live session or pane name with `*` and refuses an empty name, any other glob character and any non-printing or non-space blank. `resolve_selector` matches every listed pane more broadly than TUIOS (case-insensitive, a wildcard crossing any character) and requires the match set to be exactly the target UUID. `TuiosTransport(runner_for)` runs `observe`, `capture`, `ask` and `enter`, each on a runner the factory builds for the seconds the caller grants; `select` does no IO. The caller environment is inherited unchanged; the ask's exit code is report-only.
- `tools/resume_paused_input.py`: `SubprocessRunner` takes its process bound as a constructor parameter, 30 seconds by default for every existing caller; the delivery's factory builds one per call.
- `tools/resume_paused_delivery_model.py`, vocabulary and ports: `Phase`, `DeliveryOutcome`, `ClearOutcome`, `Refusal` with a `failed` severity, `GuardState`, `ActionReport`, `CheckoutDelivery`, `SendStep`, `InputScreen` (input prefix, placeholder, working and cleared signatures and, since round 3, `footer_lines`, the exact footer layout) and `DeliveryProfile`, `LogKind` and `LogEvent`, `ACTION_BUDGET` (100 s), `CALL_BOUND_SECONDS` (30 s), and the ports `PreSendCheck`, `ProfileGate`, `AgentLog`, `Sleeper`, `PaneTransport` (whose blocking calls take a `timeout`), `GuardPort`, `PairDelivery` and `Takeover`, bundled in `DeliveryPorts`, whose `provers` hold one `ProverFactory` per host; since round 4 a factory receives the send's `Remaining` callable rather than a figure. `UnpinnedProfiles` refuses every pane; `NoTakeover` reports every conditional reviewer pending until Step 7. The model imports no adapter at run time.
- `tools/resume_paused_delivery_checks.py`, fresh pre-send checks: `target_refusal` requires the planned UUID listed once, in its planned session, host and checkout, not the caller's pane nor an excluded session or pane label, and eligible through Step 5's `input_eligibility`; before the recovery Enter only, a stale working status is tolerated while a blocked or draft-holding pane, an idle pane that is not ready and an unknown state refuse it. `PlanRecheck` replans the checkout through `plan_checkout` from the same fresh observation and requires the same role, host, session, pane, clear flag, kind family, native command and marker pane, role and binding; before the Enter the target's own activity is read as ready.
- `tools/resume_paused_planner.py`: `plan_checkout(request, observation, ports, root)` runs the same checkout planner for one root from a fresh observation, `None` without a live pane or a saved prompt.
- `tools/resume_paused_delivery.py`, run and guard: `deliver_run` returns nothing for a dry run or a run-wide refusal, then runs one worker per planned checkout on a thread pool of at most eight; at most one input operation per pane. Each worker holds its guard through the resume, then each conditional reviewer handed to the injected takeover, which may deliver it under the same guard with extra checks; no reviewer after an unaccepted resume.
- Same module, each send: one fresh listing (bounded by the remaining budget during a send, 30 seconds before), `target_refusal`, the transport's `select` for every phase (round 2: the recovery Enter too, which still names the full UUID), every injected check, then the pane's profile again, unchanged within the action and with an input prover. A Claude send needs a readable agent log; a Codex send needs a pre-input capture whose input box shows only the placeholder with exactly the pinned footer layout below it (other text skips as `pane-draft`; no input box, an unrecognized line below, no capture or no screen signatures fail). Each send has its own 100-second budget from the ask; the ask's bound is the whole budget, every later call's bound is the remaining budget capped at 30 seconds. After each acceptance proof the clock is read again: a proof completing at or after the deadline is not acceptance (round 2). Each proof uses a prover the factory builds from the send's remaining-time callable; the Step 8 composition builds it from the budget-bounded readers of `tools/resume_paused_budget.py` (versions, capture, session store, transcripts), each of which reads the time left at its own call and reads nothing once it is spent (round 4). No step starts once the budget is spent: no prover after a slow prompt read, no listing after a slow clear-event read, `deadline-passed` after a slow listing in `prepare` and before each injected check (round 4), no last capture after slow recovery checks (round 3). Unproved acceptance is `unconfirmed`; nothing is retyped.
- Same module, clear: `--clear` applies to a resume action only. A Claude clear is skipped as `redundant` when the log holds a clear strictly after the pause and no prompt after the last one; otherwise Claude confirmation needs a clear event at or after the send and a fresh ready pane, and Codex confirmation needs one more pinned cleared line than the pre-clear capture on an empty input box (round 2: an old banner with an unrelated change never confirms). An unconfirmed clear fails the action with no resume.
- Same module, Codex recovery Enter, at most one per send (round 2 order): a capture reading exactly this send's command as the whole input box (exactly the pinned footer layout below, one line per entry in order, no working line, no placeholder, the command once on screen); a one-second gap; the fresh recovery checks with the selector and the unchanged profile; a last capture that must be identical; then, budget remaining, one `send-keys` Enter bounded by the remaining budget. A capture completing at or after the deadline stops the attempt. Any other reading, an edit (including one made during the checks), a refused check or a changed profile withholds the Enter for the rest of the send, with a note; an empty input box withholds nothing. A refused Enter is still spent. A background-shell line is noted only.
- Tests: `tests/unit/tools/test_resume_paused_guard/` (path spellings, held and unavailable states, a raising attempt, the checkout as guard folder, folders in, beside or unparsable, release on errors, two native handles contending, a blocked folder, a native seek failure that is not contention), `tests/unit/tools/test_resume_paused_transport/` (argument lists with metacharacters, selector cases, the bounds granted to each call; properties as in round 1), `tests/unit/tools/test_resume_paused_delivery_model/`, `tests/unit/tools/test_resume_paused_delivery_checks/` (unchanged), `tests/unit/tools/test_resume_paused_delivery/` (`delivery_world.py` records every granted bound and lets captures and proofs spend declared time; round 2 adds the bounds of a recovered send, a proof finishing after the deadline, slow first and last ownership captures, a new selector collision at recovery, a multiline draft, an edit during the recovery checks, an unrecognized line below an empty box, an empty footer signature, the old clear banner through `cleared` and through a delivery, and a second banner confirming; round 3 adds the concrete `CodexInputProver` with a recording capture granted the last half second and no call after expiry, a slow log read building no prover, the bound granted to a prover, a recovery check and a recovery profile read spending the budget, and repeated, missing and invalid footer lines through recovery and `read_input`), plus `test_resume_paused_planner_replan_tdd.py` and the runner bound in the input leaf. No test starts a process or sleeps.
- `tools/resume_paused_budget.py` (round 4): `BoundedVersions`, `BoundedCapture`, `BoundedSessionStore` and `BoundedTranscriptSource` wrap the Step 1 and Step 4 reader ports; with time left they read (the capture bounded by the time left at its call, at most 30 seconds), once the budget is spent they read nothing and report the evidence unavailable. Tests: `tests/unit/tools/test_resume_paused_budget/` (each reader with time left, spent, and the bound read at the call); in the delivery leaf, the concrete Codex prover composed from them with a version read spending 0, 0.3 or 1 second of the last half second, and two ordered recovery checks where the second is never asked once the first spent the budget.
- Deviations: as in round 1 (delivery split into vocabulary, checks and state machine with one leaf per module; `plan_checkout` in the planner, 558 lines; the two-process guard test through two OS handles in one process; open composition and live rows in the validation plan). The live rows now include the Codex footer signature and whether a new conversation wipes an earlier cleared line. `.vscode/settings.json` gains `EACCES`.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step6.journal.md` and `.reviews/a.resume-paused.step6.handoff.md`.

### Change summary for step 6 resume-paused (round 4)

Twenty-eight staged paths in six `a.commit` groups, in this order:

1. `docs(resume-paused): amend Q05 for code-first steps`: `docs/v0.14.0/plan.v0.14.0.resume-paused.md`.
2. `feat(resume-paused): add the shell-free transport`: `tools/resume_paused_input.py`, `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`, `tools/resume_paused_transport.py` and the `tests/unit/tools/test_resume_paused_transport` package (package file, tdd and pbt files).
3. `feat(resume-paused): add delivery ports and guard`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_guard.py` and the `tests/unit/tools/test_resume_paused_guard` package (package file and tdd file).
4. `feat(resume-paused): replan one checkout per send`: `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`.
5. `feat(resume-paused): deliver guarded pane actions`: `tools/resume_paused_delivery_checks.py`, `tools/resume_paused_budget.py`, `tools/resume_paused_delivery.py`, the `tests/unit/tools/test_resume_paused_budget` package (package file and tdd file), the `tests/unit/tools/test_resume_paused_delivery` package (package file, `delivery_world.py`, two tdd files), and the `tests/unit/tools/test_resume_paused_delivery_checks` and `tests/unit/tools/test_resume_paused_delivery_model` packages (package file and tdd file each).
6. `docs(resume-paused): record step 6 validation`: `.vscode/settings.json` (the `EACCES` project word) and `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Round 4 changes paths in groups 3, 5 and 6 and adds the budget module and its test leaf to group 5; order and subjects are unchanged. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 6 resume-paused (round 4)

Writer response:

The round 3 finding is accepted and repaired; there is no disagreement. Your staged Step 6 rows were the starting point of the updated validation plan, which reads Yes again with the round 3 repair recorded and the missing-work list removed.

- **One remaining-time source carried through the chain**: `ProverFactory` now takes a `Remaining` callable (`Callable[[], float]`, the seconds left in the send at the moment of the call) instead of a figure computed before the proof; the delivery passes `partial(self.remaining, deadline)`. The new `tools/resume_paused_budget.py` holds the readers a factory builds each prover from: `BoundedVersions`, `BoundedCapture`, `BoundedSessionStore` and `BoundedTranscriptSource`. Each one calls `Remaining` at its own call, reads nothing and reports the evidence unavailable once the budget is spent, and the capture is bounded by the time left then, at most 30 seconds. The proof therefore fails closed before any nested read that would start after the deadline. Step 4's `InputProver`, `PaneCapture`, `CodexVersions`, `SessionStore` and `TranscriptSource` contracts stay unchanged; the Step 8 composition row in the validation plan names these readers.
- **Ordered checks**: `_selected` asks the deadline before each injected check, not only after the loop, so a second check never runs once a first one spent the budget.
- **Regressions**: the concrete `CodexInputProver` composed from the bounded readers, with the proof starting half a second before the deadline and a version read spending 0, 0.3 or 1 second. The capture is granted 0.5, then 0.2, then skipped, and nothing follows on the transport. Two ordered recovery checks, where the first spends 45 seconds, never reach the second at the recovery phase (it saw only the resume phase), and no Enter is sent. Each bounded reader has its own tests in `tests/unit/tools/test_resume_paused_budget/`: with time left, with the budget spent, and with the bound read at the call rather than at construction.
- **File size**: `tools/resume_paused_delivery.py` is 573 lines, in the 550 to 650 band below the ceiling, disclosed in the validation plan; the budget readers live in their own module.
- **Commit plan**: `tools/resume_paused_budget.py` and its test leaf join group 5, whose subject is unchanged; the bodies of groups 5 and 6 describe the repair. Groups, order and subjects are otherwise unchanged.

### Reviewer focus for step 6 resume-paused (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-4 -->

## Round 4 by reviewer - Step 6

- Recorded: 2026-11-20T22:25:08+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 resume-paused (exchange 1) (round 4)

Baseline index tree: 6e291067218a908a73f70ddfd88487c5e7cebf7f

Assessed index tree: 6e291067218a908a73f70ddfd88487c5e7cebf7f

### Implementation check for step 6 resume-paused (exchange 1) (round 4)

Result:

Yes. Step 6 has been fully implemented within amended plan Q05’s code-first scope. The round 3 deadline finding is resolved. The concrete Codex prover obtains the current capture timeout after its version read, and each injected recovery check consults the same deadline before it runs.

Validation plan effects:

The step 6 verdict and validation rows already reflect the assessed behavior. The live two-process guard check, host signatures and Step 8 composition are recorded as open.

### Pre-repair mandatory checks and coverage for step 6 resume-paused (exchange 1) (round 4)

The writer reported 7,157 passing tests, 100% coverage over `tools`, and a passing static check. I inspected the staged implementation and regression cases. With 0.5 seconds remaining, the concrete-prover cases expect a capture grant of 0.5 or 0.2 seconds, or no capture after expiry. The ordered-check test asserts that a second recovery check never runs after the first spends the budget. Synchronous file and version reads check at entry. An in-flight read can finish late, and the outer acceptance check discards that result. I did not repeat the suite.

### Resolved validation set and sources for step 6 resume-paused (exchange 1) (round 4)

`ghog day --full=speed --whole-suite` (project source, whole scope).

### Resolver drift and direction for step 6 resume-paused (exchange 1) (round 4)

None. The current resolver matched the request.

### Repository state around validation for step 6 resume-paused (exchange 1) (round 4)

The request, baseline and assessed index tree all matched `6e291067218a908a73f70ddfd88487c5e7cebf7f`. Validation-state comparison was acceptable with no differences. No umbrella applies.

### Repair inventory for step 6 resume-paused (exchange 1) (round 4)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 resume-paused (exchange 1) (round 4)

`a.commit` remains accurate. The independent checker returned `valid`, `ready: true`, zero diagnostics, six ordered groups and 28 staged paths. Group 5 contains the bounded readers and their tests. Group 6 records the scope of validation.

1. `docs(resume-paused): amend Q05 for code-first steps`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.md`
2. `feat(resume-paused): add the shell-free transport`
   - `tools/resume_paused_input.py`
   - `tests/unit/tools/test_resume_paused_input/test_resume_paused_input_tdd.py`
   - `tools/resume_paused_transport.py`
   - `tests/unit/tools/test_resume_paused_transport/__init__.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_tdd.py`
   - `tests/unit/tools/test_resume_paused_transport/test_resume_paused_transport_pbt.py`
3. `feat(resume-paused): add delivery ports and guard`
   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_guard.py`
   - `tests/unit/tools/test_resume_paused_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_guard/test_resume_paused_guard_tdd.py`
4. `feat(resume-paused): replan one checkout per send`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_replan_tdd.py`
5. `feat(resume-paused): deliver guarded pane actions`
   - `tools/resume_paused_delivery_checks.py`
   - `tools/resume_paused_budget.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_budget/__init__.py`
   - `tests/unit/tools/test_resume_paused_budget/test_resume_paused_budget_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery/delivery_world.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_recovery_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_checks/test_resume_paused_delivery_checks_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/__init__.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
6. `docs(resume-paused): record step 6 validation`
   - `.vscode/settings.json`
   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 6 resume-paused (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 6 resume-paused (exchange 1) (round 4)

Present the advisory commit-ready recommendation at the human decision gate. Keep the separate composition and live-evidence rows open.

### Decision rationale for step 6 resume-paused (exchange 1) (round 4)

Commit-ready for the staged step 6 code. All prior findings are resolved, the bound validation and coverage are reported green, and the reviewer made no repairs or staged changes. The commit decision belongs to the human.

### Final reviewer decision for step 6 resume-paused (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-4 -->

## Round 4 by human - Step 6 - human-confirmation

- Recorded: 2026-11-20T23:21:50+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 1 by requestor - Step 7

- Recorded: 2026-11-21T11:44:17+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: request

### Review identity for step 7 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 7
Review round: 1

### Code review evidence for step 7 resume-paused (round 1)

request_index_tree: 2f9916bc89be7421338ece7ff6babf30ea6a1250
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): observe each accepted receiver
group 1 path: tools/resume_paused_delivery_model.py
group 1 path: tools/resume_paused_delivery.py
group 1 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 1 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 2: feat(resume-paused): expose marked claim evidence
group 2 path: tools/resume_paused_review.py
group 2 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 2 path: tools/resume_paused_planner.py
group 3: feat(resume-paused): prove takeover and no wait
group 3 path: tools/resume_paused_takeover_proof.py
group 3 path: tools/resume_paused_reviewer_wait.py
group 4: feat(resume-paused): guard Claude reviewer sends
group 4 path: tools/resume_paused_pane_guard.py
group 5: feat(resume-paused): activate verified reviewers
group 5 path: tools/resume_paused_takeover.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
group 6: docs(resume-paused): record step 7 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_pane_guard.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_reviewer_wait.py
staged path: tools/resume_paused_takeover.py
staged path: tools/resume_paused_takeover_proof.py
```

### Validation scope for step 7 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 7 resume-paused (round 1)

Step 7 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05. `MarkedTakeover` implements the Step 6 takeover seam. It observes every accepted receiver read-only for its own 120-second fake-clock bound, and proves a requestor takeover only from durable records: the schema 3 receipt and the exchange's current marked claim agree on launch, pane, host and binding at the current generation. It decides each conditional reviewer from fresh evidence, on initial activation and later continuation alike: leave-alone first, then the current claim, then positive no-wait evidence. It delivers through the guarded worker with a refreshed decision and the design Q27=B all-pane idle guard as pre-send checks. The empty profile registry keeps every real pane unsupported. The implementation check recorded `Yes. Step 7 has been fully implemented.`

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-21T11:36:35+01:00 with 7341 tests, 100% coverage, no outlier and no exclusion, slowest call 0.75 s. The four new leaves and the changed delivery, delivery model and review leaves passed in focus first (181 tests in the four Step 7 leaves). The index tree is `2f9916bc89be7421338ece7ff6babf30ea6a1250`, the content of the walked working tree.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports nothing on the validation plan, the one changed Markdown file.
- Coverage: 100% over `tools`; one unit leaf per new module (`test_resume_paused_takeover_proof`, `test_resume_paused_reviewer_wait`, `test_resume_paused_pane_guard`, `test_resume_paused_takeover`), the seam and the marked claim field covered in the delivery, delivery model and review leaves.
- Architecture: the proofs are pure functions over one fresh durable read; the reviewer-wait classification and the Q27=B guard are separate modules, as the plan's split guidance allows; the takeover depends on the delivery model's ports and its own injected ports (`ResultSource`, `WaitAbsence`, `ClaudeScreens`), reads no file, log or process itself, and delivers only through Step 6's worker.
- Performance: single passes over listings and histories, at most about thirty bounded looks per receiver, one decision plus one pre-send refresh per activation; no `O(n^2)` or `O(n log n)` path.
- Feature integrity: with `NoTakeover`, every Step 6 outcome is unchanged; reports and exchange snapshots gain defaulted fields; `marked_command` is the planner's existing rendering moved into a function; manual resume, review, validator and claim paths are untouched; the takeover writes nothing.
- Open rows (validation plan): composition by Step 8 (result source, Claude ledger decision, Claude screen profile, reviewer-wait ports, the takeover wiring) and live host evidence (Claude idle screen signature, result line forms and question state, the Claude ledger profile).

### Implementation report for step 7 resume-paused (round 1)

Step 7 confirms takeover and activates only a verified missing reviewer. Under the amended plan Q05 it proceeds code-first against the empty profile registry, with injected ports and fake clocks. It adds four modules and four test leaves, extends the Step 6 seam, and adds one field to the Step 2 exchange snapshot and one function to the Step 5 planner.

- `tools/resume_paused_delivery_model.py` and `tools/resume_paused_delivery.py`, the seam: `ReceiverState` (`unobserved`, `consumed`, `claimed`, `completion-unconfirmed`, `failed`) and the report fields `receiver` and `generation`; `Takeover.received(pair, report)`, which `_CheckoutWorker._sequence` calls for every resume report before any conditional reviewer is decided; `PairDelivery.root`, the guarded checkout, exposed by the worker. `NoTakeover.received` returns the report unobserved.
- `tools/resume_paused_review.py`: `ExchangeSnapshot.marked_claim` carries the coordination record's marked claim binding (launch id, receiving pane, host, assignment binding, round, occurrence, issued generation); it holds no token or token digest.
- `tools/resume_paused_planner.py`: `marked_command(host, kind, marker)` renders the native command and marker, used by `_command` and by the takeover to rebuild a requestor's marked input from its receipt.
- `tools/resume_paused_takeover_proof.py`, pure proofs over one `Durable` read (saved pause, then its saved exchange; an unreadable pause fails `evidence-invalid`). `consumption` fails a removed, replaced or unreadable pause, waits without a receipt, fails another launch's receipt, an unmarked one, or a resumer other than the planned host, and rebuilds the requestor marker from the receipt when none is planned. `takeover_ready` adds a live exchange: busy waits, not live blocks, a changed selection or damage fails, and the recorded requestor nature must be the requestor's host. `current_claim` requires the marked claim of this launch, pane, host and binding at the current ownership generation, owned by the requestor in the same occurrence. It rebuilds the binding with `resolve_assignment` for the requestor role at the claimed round, so a paused reviewer's receipt, or a receipt on an unrouted pane, never proves a counterpart. It names the counterpart pane, whose recorded nature must agree; a switched pair names its switched reviewer. A missing claim waits; a superseded or foreign claim blocks, a competing pickup.
- `tools/resume_paused_reviewer_wait.py`. `reviewer_active` leaves alone a reviewer owning the current generation when its pane agrees: the current marked claim names it, or, without one, its latest typed command is a reviewer `review-resume` (histories are read oldest first). `prior_delivery` reads a marked reviewer entry to this pane since the receipt, undated or malformed, as an uncertain earlier delivery, diagnosed and never resent. `ReviewerWait.verdict` requires a resting pane (idle or done, ready, no draft, no question), a readable history and no prior delivery. A Codex reviewer then needs a supported `IDLE_EMPTY` probe, since an attached global wait is an active turn and reads busy. A Claude reviewer needs a `WaitAbsence` decision proving absence over a `WaitScope` carrying the receipt time, the proved requestor's pane and its rebuilt marked input, for the Q23=A file binding and the Q24=A exception, on both routes. Ledger reasons become `ledger-<code>` notes; `UnprovedAbsence` decides nothing while no ledger profile is pinned.
- `tools/resume_paused_pane_guard.py`, the design Q27=B guard. `AllPaneIdleGuard` is a `PreSendCheck` acting only on Claude reviewer sends. From the send's fresh listing it takes every live Claude pane whose working directory is the checkout or lies inside it, the requestor and the target included. Each must rest in TUIOS and its fresh capture must read idle under `ClaudeScreens`. A busy, blocked, draft-holding, unreadable or unknown-layout pane refuses the send, as does a Claude pane whose directory cannot be read; contradictory host evidence fails. Captures are bounded by what is left of the guard's own 30-second budget, and none starts or is acted on once it is spent. `UnpinnedClaudeScreens` reads every screen unknown.
- `tools/resume_paused_takeover.py`, `MarkedTakeover.received`: a `_Watch` starts its 120-second bound at acceptance. Each look re-reads the listing (a blocked pane or a question fails `receiver-question`), the result lines (a well-formed `failed` line for this launch fails `receiver-failed`; malformed, foreign, masked or unreadable lines prove nothing) and the durable records. Backoff runs 0.5, 1, 2, 4, then 5 seconds, capped by what is left; a remaining-time check precedes every read, and a read completed after the bound is never acted on. A requestor of a live exchange settles `claimed` with its generation on a proved takeover; any other receiver settles `consumed` on its receipt. At the bound a receipt alone stays `consumed` and nothing durable is `completion-unconfirmed`, both successes; failures set the report failed.
- Same module, `MarkedTakeover.reviewer`: after a resume that is not a requestor's, or that failed, the reviewer is refused. Otherwise one decision on a fresh listing runs the proofs, the leave-alone check (`reviewer-active`, an expected skip), the current claim, the planned reviewer as the proved counterpart (`reviewer-not-paired` fails) and the wait verdict. The planned reviewer marker keeps its launch id but is rebound to the exchange's live occurrence and round, which the reviewer's validator rebuilds; a planned marker that does not parse fails `reviewer-marker-unreadable`. The rebound command is delivered through `PairDelivery.deliver` with two pre-send checks: the decision refreshed on the send's listing, refusing `reviewer-binding-changed` when the live round moved since the decision, and the Q27=B guard. Before a Codex recovery Enter only the durable takeover is refreshed, since the pane holds the command. A refusal by either check reports the reviewer pending; an independent delivery failure stays unchanged. An accepted reviewer is watched for its own 120 seconds until its marked claim, owned by the reviewer at the current generation, is current. Every Claude reviewer outcome carries `limits=claude-wait-scope`; `preview_notes` gives it to conditional Claude reviewer previews; `CLAUDE_WAIT_LIMITS` defines the five disclosed limits for Step 8's help and reference.
- Tests: `tests/unit/tools/test_resume_paused_takeover/` holds `takeover_world.py`, the declared world shared by the four leaves: parsed receipts, exchanges with marked claims, `FakePair` running each phase's checks on a fresh listing. It also holds an observation tdd (every receiver outcome, each failure, masked lines, discovery loss, the bound exactly filled, a read or a failure read ending after it) and an activation tdd. The activation tdd covers every decision refusal, leave-alone with and without a marked claim, competing pickup, the Codex and Claude wait verdicts, ledger blockers with real reason codes, an uncertain earlier delivery, an unchanged, a switched and a log-evicted continuation, replacement, rebinding, the refresh and recovery gates, each Q27=B case on both routes, the reviewer watch, limits, previews and two runs through the real Step 6 delivery. The proof, reviewer-wait and pane-guard leaves reach their modules. The delivery, delivery model and review leaves cover the seam, `root` and the marked claim field. No test starts a process or sleeps; every bound runs on a fake clock.
- Deviations: following the plan's split guidance, the proofs, the reviewer wait and the Q27=B guard are separate modules, each with its own leaf; the Q27=B cases the plan places in `test_resume_paused_takeover_tdd.py` are there, run through the takeover with the real guard. The seam extension changes Step 6's model and worker, the marked claim joins the Step 2 snapshot and `marked_command` joins the planner (568 lines, in the 550 to 650 band); the delivery state machine is 584 lines. The Q23=A and Q24=A record classification stays in Step 1's ledger; Step 7 passes it the requestor binding and acts on its decision. The reviewer marker rebinding is a design consequence found during the step and recorded in the validation plan.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step7.journal.md` and `.reviews/a.resume-paused.step7.handoff.md`.

### Change summary for step 7 resume-paused (round 1)

Twenty-two staged paths in six `a.commit` groups, in this order:

1. `feat(resume-paused): observe each accepted receiver`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_delivery.py`, `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py` and `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`.
2. `feat(resume-paused): expose marked claim evidence`: `tools/resume_paused_review.py`, `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py` and `tools/resume_paused_planner.py`.
3. `feat(resume-paused): prove takeover and no wait`: `tools/resume_paused_takeover_proof.py` and `tools/resume_paused_reviewer_wait.py`.
4. `feat(resume-paused): guard Claude reviewer sends`: `tools/resume_paused_pane_guard.py`.
5. `feat(resume-paused): activate verified reviewers`: `tools/resume_paused_takeover.py` and the `tests/unit/tools/test_resume_paused_takeover` package (package file, `takeover_world.py`, observation and activation tdd files), with the `tests/unit/tools/test_resume_paused_takeover_proof`, `tests/unit/tools/test_resume_paused_reviewer_wait` and `tests/unit/tools/test_resume_paused_pane_guard` packages (package file and tdd file each), whose tests share the declared world of this group.
6. `docs(resume-paused): record step 7 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 7 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis in the transcript.

### Reviewer focus for step 7 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-1 -->

## Round 1 by human - Step 7 - escalation

- Recorded: 2026-11-21T14:45:02+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - Step 7 - human-reclaim

- Recorded: 2026-11-22T01:39:04+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: human-reclaim

Round 1 of the Step 7 code review escalated on 2026-11-21 at 14:45 (+01:00) when the requestor's `wait-answer` reached its full 10800-second bound. No reviewer had claimed the request: the reviewer nature was still unrecorded, the owner was the requestor, and the generation was 1. Nothing failed. The request, the bound scope (fingerprint `686958cd`), the staged index tree `2f9916bc` and `a.commit` are unchanged.

The human chose to treat the escalation as a stopped handoff and resume it. The same round 1 request goes back to the reviewer unchanged, and the requestor waits again for its answer.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer - Step 7

- Recorded: 2026-11-22T10:45:51+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 resume-paused (exchange 1) (round 1)

Baseline index tree: 2f9916bc89be7421338ece7ff6babf30ea6a1250

Assessed index tree: 2aeec1285fd784d6139208f0b027e0630384e46d

### Implementation check for step 7 resume-paused (exchange 1) (round 1)

Result:

Step 7 is incomplete. Six readiness checks give the following results.

1. Identity passes for `resume-paused` v0.14.0, step 7, round 1, occurrence 1. The request tree matched the baseline index.
2. Implementation is incomplete. Receiver identity, pane questions, two deadlines, Claude reporting and discovery cost need correction.
3. The writer reports a passing whole-suite run and 100% line coverage of `tools`. Static review found missing behavioral tests for the six findings.
4. Staged scope is attributable. The reviewer changed only the reviewed step in the validation plan.
5. Six current findings remain open. This is the first round.
6. The independent commit-plan check passed for all 22 paths and six groups.

Validation plan effects:

Recorded the No verdict, six missing-work items and their test expectations in step 7 of `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Updated its performance, coverage and feature-integrity judgments. Markdown lint passed. The umbrella comparison reported `applicable=false` and `changed=false`.

### Pre-repair mandatory checks and coverage for step 7 resume-paused (exchange 1) (round 1)

The writer reports 7,341 tests passing and 100% line coverage of `tools`. The reviewer traced the staged code and tests, verified the request tree and commit plan, and linted the validation-plan edit. Test execution evidence comes from the writer.

### Resolved validation set and sources for step 7 resume-paused (exchange 1) (round 1)

`ghog day --full=speed --whole-suite` (project). The recorded scope is `whole`, proof `speed`, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 7 resume-paused (exchange 1) (round 1)

None. The independent resolver returned the same command and source as the request.

### Repository state around validation for step 7 resume-paused (exchange 1) (round 1)

The captured comparison returned `acceptable=false` because the validation plan and index changed. The attributable step 7 edit accounts for both. A direct index comparison from `2f9916bc89be7421338ece7ff6babf30ea6a1250` to `2aeec1285fd784d6139208f0b027e0630384e46d` identified only `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. The captured comparison found no changed ignored or untracked paths.

### Repair inventory for step 7 resume-paused (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 resume-paused (exchange 1) (round 1)

The independent checker exited 0 with `state=valid`, `ready=true`, 22 staged paths and no diagnostics. Its ordered groups are

1. `feat(resume-paused): observe each accepted receiver`
2. `feat(resume-paused): expose marked claim evidence`
3. `feat(resume-paused): prove takeover and no wait`
4. `feat(resume-paused): guard Claude reviewer sends`
5. `feat(resume-paused): activate verified reviewers`
6. `docs(resume-paused): record step 7 validation`

The checked paths are

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`
- `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`
- `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
- `tests/unit/tools/test_resume_paused_pane_guard/__init__.py`
- `tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py`
- `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`
- `tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py`
- `tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py`
- `tests/unit/tools/test_resume_paused_takeover/__init__.py`
- `tests/unit/tools/test_resume_paused_takeover/takeover_world.py`
- `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py`
- `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py`
- `tests/unit/tools/test_resume_paused_takeover_proof/__init__.py`
- `tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py`
- `tools/resume_paused_delivery.py`
- `tools/resume_paused_delivery_model.py`
- `tools/resume_paused_pane_guard.py`
- `tools/resume_paused_planner.py`
- `tools/resume_paused_review.py`
- `tools/resume_paused_reviewer_wait.py`
- `tools/resume_paused_takeover.py`
- `tools/resume_paused_takeover_proof.py`

### Findings and boundaries for step 7 resume-paused (exchange 1) (round 1)

Unresolved findings:

1. Receiver observation can reject a valid second pause and miss a replacement before the first receipt exists.
2. Both idle checks can allow reviewer input while a pane reports a question.
3. A conditional Claude reviewer report can omit its wait-scope disclosure.
4. A saved-prompt read can consume the observation budget before the exchange read begins.
5. The final Claude screen classification can exhaust the guard budget and still authorize delivery.
6. Sorting matching pane UUIDs on each refresh exceeds the linear discovery bound.

Boundary-crossing work: None.

### Writer instructions for step 7 resume-paused (exchange 1) (round 1)

1. Bind observation to the prompt digest accepted for delivery. `classify_usage` returns `NEW_SINCE_USE` for a fresh prompt with an older receipt, and the planner accepts it. `consumption` currently reports `prompt-replaced` on the first look. Keep waiting when the intended prompt is present with an older receipt, and fail when the intended prompt changes, including before any receipt exists. Test both sequences through receiver observation.

2. Reject a question reported independently of `blocked_by` or pane state. Both `_resting` functions accept an idle, ready pane with a nonempty `PaneActivity.question`, unlike `_Watch.failure`. Cover a question on the target and on a non-target Claude pane. Each must keep the reviewer pending with zero sends on initial activation and continuation.

3. Apply `limits=claude-wait-scope` to the Claude reviewer report that `_CheckoutWorker._sequence` constructs when the requestor was not accepted. This path bypasses `MarkedTakeover.reviewer`. Cover a refused or unconfirmed requestor through the delivery worker.

4. Enforce the observation deadline between the saved-prompt read and the exchange read. `_Watch.durable` checks the clock around `read_durable`, which starts the exchange read even if the prompt read consumed the remaining 120 seconds. Use a fake clock and assert that the exchange observer receives zero calls in that case.

5. Recheck the idle-guard deadline after `ClaudeScreens.read` on the last pane. An idle classification that consumes the remaining budget currently passes because no next capture checks the clock. Add a final-pane fake-clock test that expects the reviewer to stay pending.

6. Keep pane discovery linear. `checkout_claude_panes` sorts the entire matching set by UUID on each refresh. The plan specifies a linear scan and does not cap the number of Claude panes. Retain discovery order and test membership and one capture per pane.

### Decision rationale for step 7 resume-paused (exchange 1) (round 1)

Changes requested. The current receiver can reject a valid pause, and the reviewer gate can authorize input with a question open or a deadline exhausted. Step 7 also requires consistent Claude limits reporting and linear pane discovery. Cover each correction in the next review request.

### Final reviewer decision for step 7 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-7-round-1 -->

## Round 2 by requestor - Step 7

- Recorded: 2026-11-22T11:36:10+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: request

### Review identity for step 7 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 7
Review round: 2

### Code review evidence for step 7 resume-paused (round 2)

request_index_tree: f36e479952f84c10f73a7b25289f0775380777a0
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): expose claim and prompt evidence
group 1 path: tools/resume_paused_review.py
group 1 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 1 path: tools/resume_paused_plan_model.py
group 1 path: tools/resume_paused_planner.py
group 1 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 2: feat(resume-paused): observe each accepted receiver
group 2 path: tools/resume_paused_delivery_model.py
group 2 path: tools/resume_paused_delivery.py
group 2 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 3: feat(resume-paused): prove takeover and no wait
group 3 path: tools/resume_paused_takeover_proof.py
group 3 path: tools/resume_paused_reviewer_wait.py
group 4: feat(resume-paused): guard Claude reviewer sends
group 4 path: tools/resume_paused_pane_guard.py
group 5: feat(resume-paused): activate verified reviewers
group 5 path: tools/resume_paused_takeover.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
group 6: docs(resume-paused): record step 7 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_pane_guard.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_reviewer_wait.py
staged path: tools/resume_paused_takeover.py
staged path: tools/resume_paused_takeover_proof.py
```

### Validation scope for step 7 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 7 resume-paused (round 2)

Step 7 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05, and round 2 repairs all six round 1 findings. `MarkedTakeover` implements the Step 6 takeover seam. It observes every accepted receiver read-only for its own 120-second fake-clock bound, bound to the saved prompt the plan accepted: an older receipt of that prompt waits, and a prompt changed since planning fails, even before any receipt exists. It proves a requestor takeover only from durable records: the schema 3 receipt and the exchange's current marked claim agree on launch, pane, host and binding at the current generation. It decides each conditional reviewer from fresh evidence, on initial activation and later continuation alike: leave-alone first, then the current claim, then positive no-wait evidence, where a question refuses a pane even without a blocking reason. It delivers through the guarded worker with a refreshed decision and the design Q27=B all-pane idle guard as pre-send checks, the guard taking the checkout's Claude panes in one linear scan and checking its budget before each pane and after the last reading. Every Claude reviewer outcome, the worker's own `requestor-not-accepted` report included, carries `limits=claude-wait-scope`. The empty profile registry keeps every real pane unsupported. The validation plan reads `Yes. Step 7 has been fully implemented.` again, with the round 1 repairs recorded.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-22T11:30:16+01:00 with 7370 tests, 100% coverage, no outlier and no exclusion, slowest call 0.32 s. Before it, the takeover, proof, reviewer-wait, pane-guard, delivery, delivery model and planner leaves passed in focus with `ghog single`. The index tree is `f36e479952f84c10f73a7b25289f0775380777a0`, the content of the walked working tree.
- Earlier walks of this round, disclosed: one stopped in `check.bat` on radon C for the planner test the digest assertions first joined (they moved to their own test), and one reached the full stage with 99% coverage because the guard's pre-capture budget check had become unreachable behind the new post-reading check (the guard now checks before each pane and once after the last reading, and every line is reached).
- Static checks: the green walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports nothing on the validation plan and the round 2 inputs.
- Coverage: 100% over `tools`; each repair has its own regression: older receipts and prompts changed since planning through receiver observation, the reviewer decision and the proofs; questions with no blocking reason on the target and a non-target Claude pane on both routes; the limits on the worker's report after a refused and an unconfirmed requestor; zero exchange reads after a saved-prompt read that spent the bound; the last pane's reading spending the guard's budget; discovery order with one capture per pane.
- Architecture: the proofs stay pure functions over one fresh durable read, now split into `read_pause` and `read_exchange` so the watch checks its bound between them; the plan's accepted digest reaches the takeover through `PairDelivery.digest`, a read-only port like `root`; `CLAUDE_WAIT_SCOPE` sits in the delivery model, which both the worker and the takeover import, with no new dependency direction.
- Performance: single passes over listings and histories; the guard's membership is one linear scan with no sort, `O(P + C)` per refreshed listing; at most about thirty bounded looks per receiver, one decision plus one pre-send refresh per activation; no `O(n^2)` or `O(n log n)` path.
- Feature integrity: with `NoTakeover`, every Step 6 outcome is unchanged, except that a Claude reviewer's `requestor-not-accepted` report gains the limits note; reports, exchange snapshots and checkout plans gain defaulted fields; every plan outcome and command spelling is unchanged; manual resume, review, validator and claim paths are untouched; the takeover writes nothing.
- Open rows (validation plan): composition by Step 8 (result source, Claude ledger decision, Claude screen profile, reviewer-wait ports, the takeover wiring) and live host evidence (Claude idle screen signature, result line forms and question state, the Claude ledger profile).

### Implementation report for step 7 resume-paused (round 2)

Step 7 confirms takeover and activates only a verified missing reviewer. Under the amended plan Q05 it proceeds code-first against the empty profile registry, with injected ports and fake clocks. It adds four modules and four test leaves, extends the Step 6 seam, and adds one field to the Step 2 exchange snapshot, one field to the Step 5 checkout plan and one function to the Step 5 planner. Round 2 repairs the six round 1 findings.

- `tools/resume_paused_plan_model.py` and `tools/resume_paused_planner.py`: `CheckoutPlan.digest` records the digest of the saved prompt the plan accepted, set once in `_classify` for every prompt-bearing checkout, so a fresh prompt behind an older receipt carries the new prompt's digest. `marked_command(host, kind, marker)` renders the native command and marker, used by `_command` and by the takeover to rebuild a requestor's marked input from its receipt.
- `tools/resume_paused_delivery_model.py` and `tools/resume_paused_delivery.py`, the seam: `ReceiverState` (`unobserved`, `consumed`, `claimed`, `completion-unconfirmed`, `failed`) and the report fields `receiver` and `generation`; `Takeover.received(pair, report)`, which `_CheckoutWorker._sequence` calls for every resume report before any conditional reviewer is decided; `PairDelivery.root`, the guarded checkout, and `PairDelivery.digest`, the plan's accepted prompt, both exposed by the worker. `NoTakeover.received` returns the report unobserved. `CLAUDE_WAIT_SCOPE` now lives in the delivery model: the worker's own `requestor-not-accepted` report of a Claude reviewer carries it, a Codex reviewer's carries no note.
- `tools/resume_paused_review.py`: `ExchangeSnapshot.marked_claim` carries the coordination record's marked claim binding (launch id, receiving pane, host, assignment binding, round, occurrence, issued generation); it holds no token or token digest.
- `tools/resume_paused_takeover_proof.py`, pure proofs over one `Durable` read. `read_pause` reads the saved pause (an unreadable pause fails `evidence-invalid`) and `read_exchange` adds its saved exchange; `read_durable` composes both. `consumption`, `takeover_ready` and `takeover` take the `intended` digest. A removed or unreadable pause fails. With an intended digest, a saved prompt whose digest differs fails `prompt-replaced`, with or without a receipt; the intended prompt waits without a receipt (`receipt-absent`) and behind an older receipt for other bytes (`receipt-earlier`). Without one, a receipt for other bytes reads as replaced, as before. Then another launch's receipt, an unmarked one, or a resumer other than the planned host fails, and the requestor marker is rebuilt from the receipt when none is planned. `takeover_ready` adds a live exchange: busy waits, not live blocks, a changed selection or damage fails, and the recorded requestor nature must be the requestor's host. `current_claim` requires the marked claim of this launch, pane, host and binding at the current ownership generation, owned by the requestor in the same occurrence. It rebuilds the binding with `resolve_assignment` for the requestor role at the claimed round, so a paused reviewer's receipt, or a receipt on an unrouted pane, never proves a counterpart. It names the counterpart pane, whose recorded nature must agree; a switched pair names its switched reviewer. A missing claim waits; a superseded or foreign claim blocks, a competing pickup.
- `tools/resume_paused_reviewer_wait.py`. `reviewer_active` leaves alone a reviewer owning the current generation when its pane agrees: the current marked claim names it, or, without one, its latest typed command is a reviewer `review-resume` (histories are read oldest first). `prior_delivery` reads a marked reviewer entry to this pane since the receipt, undated or malformed, as an uncertain earlier delivery, diagnosed and never resent. `ReviewerWait.verdict` requires a resting pane (no blocking reason, no question even when TUIOS names no blocking reason, no draft, idle or done and ready), a readable history and no prior delivery. A Codex reviewer then needs a supported `IDLE_EMPTY` probe, since an attached global wait is an active turn and reads busy. A Claude reviewer needs a `WaitAbsence` decision proving absence over a `WaitScope` carrying the receipt time, the proved requestor's pane and its rebuilt marked input, for the Q23=A file binding and the Q24=A exception, on both routes. Ledger reasons become `ledger-<code>` notes; `UnprovedAbsence` decides nothing while no ledger profile is pinned.
- `tools/resume_paused_pane_guard.py`, the design Q27=B guard. `AllPaneIdleGuard` is a `PreSendCheck` acting only on Claude reviewer sends. From the send's fresh listing, in one linear scan that keeps discovery order, it takes every live Claude pane whose working directory is the checkout or lies inside it, the requestor and the target included. Each must rest in TUIOS (a question refuses it on its own, `claude-pane-question`) and its fresh capture must read idle under `ClaudeScreens`. A busy, blocked, questioning, draft-holding, unreadable or unknown-layout pane refuses the send, as does a Claude pane whose directory cannot be read; contradictory host evidence fails. Captures are bounded by what is left of the guard's own 30-second budget; none starts once it is spent, and neither a capture nor a screen reading completed after it is acted on, the last pane's included.
- `tools/resume_paused_takeover.py`, `MarkedTakeover.received`: a `_Watch` starts its 120-second bound at acceptance. Each look re-reads the listing (a blocked pane or a question fails `receiver-question`), the result lines (a well-formed `failed` line for this launch fails `receiver-failed`; malformed, foreign, masked or unreadable lines prove nothing) and the durable records, with the bound checked before the saved-prompt read, between it and the exchange read, and after. Backoff runs 0.5, 1, 2, 4, then 5 seconds, capped by what is left; a read completed after the bound is never acted on. Consumption and takeover bind `PairDelivery.digest`. A requestor of a live exchange settles `claimed` with its generation on a proved takeover; any other receiver settles `consumed` on its receipt. At the bound a receipt alone stays `consumed` and nothing durable is `completion-unconfirmed`, both successes; failures set the report failed.
- Same module, `MarkedTakeover.reviewer`: after a resume that is not a requestor's, or that failed, the reviewer is refused. Otherwise one decision on a fresh listing, bound to the plan's prompt through `Activation.digest`, runs the proofs, the leave-alone check (`reviewer-active`, an expected skip), the current claim, the planned reviewer as the proved counterpart (`reviewer-not-paired` fails) and the wait verdict. The planned reviewer marker keeps its launch id but is rebound to the exchange's live occurrence and round, which the reviewer's validator rebuilds; a planned marker that does not parse fails `reviewer-marker-unreadable`. The rebound command is delivered through `PairDelivery.deliver` with two pre-send checks: the decision refreshed on the send's listing, refusing `reviewer-binding-changed` when the live round moved since the decision, and the Q27=B guard. Before a Codex recovery Enter only the durable takeover is refreshed, since the pane holds the command. A refusal by either check reports the reviewer pending; an independent delivery failure stays unchanged. An accepted reviewer is watched for its own 120 seconds until its marked claim, owned by the reviewer at the current generation, is current. Every Claude reviewer outcome carries `limits=claude-wait-scope`; `preview_notes` gives it to conditional Claude reviewer previews; `CLAUDE_WAIT_LIMITS` defines the five disclosed limits for Step 8's help and reference.
- Tests: `tests/unit/tools/test_resume_paused_takeover/` holds `takeover_world.py`, the declared world shared by the four leaves: parsed receipts, exchanges with marked claims, `FakePair` running each phase's checks on a fresh listing and naming the plan's prompt (the first declared pause's unless declared). It also holds an observation tdd (every receiver outcome, each failure, masked lines, discovery loss, the bound exactly filled, a read or a failure read ending after it, an older receipt then a claim, an older receipt alone at the bound, a prompt changing before any receipt or behind an older one, a plan that read other bytes, a saved-prompt read spending the bound with zero exchange reads) and an activation tdd. The activation tdd covers every decision refusal, leave-alone with and without a marked claim, competing pickup, the Codex and Claude wait verdicts, ledger blockers with real reason codes, an uncertain earlier delivery, an unchanged, a switched and a log-evicted continuation, a prompt changed since planning, an older receipt on both routes, questions with no blocking reason on the Claude target, a non-target Claude pane and a Codex target on both routes, rebinding, the refresh and recovery gates, each Q27=B case on both routes, the reviewer watch, limits, previews and two runs through the real Step 6 delivery, one carrying the plan's digest. The proof leaf covers every intended verdict and its pass-through; the reviewer-wait and pane-guard leaves add the question refusal, the guard leaf discovery order with one capture per pane and the last pane's reading spending the budget. The delivery leaf covers the digest hand-off and the limits on the worker's report after a refused and an unconfirmed requestor; the planner leaf the recorded digest. No test starts a process or sleeps; every bound runs on a fake clock.
- Deviations: following the plan's split guidance, the proofs, the reviewer wait and the Q27=B guard are separate modules, each with its own leaf; the Q27=B cases the plan places in `test_resume_paused_takeover_tdd.py` are there, run through the takeover with the real guard. The seam extension changes Step 6's model and worker, the marked claim joins the Step 2 snapshot, and `marked_command` and the plan digest join the Step 5 planner and plan model (planner 571 lines, in the 550 to 650 band); the delivery state machine is 595 lines, in the same band; the takeover is 549. The Q23=A and Q24=A record classification stays in Step 1's ledger; Step 7 passes it the requestor binding and acts on its decision. The reviewer marker rebinding is a design consequence found during the step and recorded in the validation plan.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step7.journal.md` and `.reviews/a.resume-paused.step7.handoff.md`.

### Change summary for step 7 resume-paused (round 2)

Twenty-four staged paths in six `a.commit` groups, in this order. Round 2 adds `tools/resume_paused_plan_model.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py` to the claim-evidence group, which moves first because the worker reads `CheckoutPlan.digest`:

1. `feat(resume-paused): expose claim and prompt evidence`: `tools/resume_paused_review.py`, `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`, `tools/resume_paused_plan_model.py`, `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`.
2. `feat(resume-paused): observe each accepted receiver`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_delivery.py`, `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py` and `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`.
3. `feat(resume-paused): prove takeover and no wait`: `tools/resume_paused_takeover_proof.py` and `tools/resume_paused_reviewer_wait.py`.
4. `feat(resume-paused): guard Claude reviewer sends`: `tools/resume_paused_pane_guard.py`.
5. `feat(resume-paused): activate verified reviewers`: `tools/resume_paused_takeover.py` and the `tests/unit/tools/test_resume_paused_takeover` package (package file, `takeover_world.py`, observation and activation tdd files), with the `tests/unit/tools/test_resume_paused_takeover_proof`, `tests/unit/tools/test_resume_paused_reviewer_wait` and `tests/unit/tools/test_resume_paused_pane_guard` packages (package file and tdd file each), whose tests share the declared world of this group.
6. `docs(resume-paused): record step 7 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The round 1 repairs touch every group: the plan model, planner and planner tdd (group 1); the delivery model, worker and their tdd files (group 2); the proof and reviewer wait (group 3); the guard (group 4); the takeover, the declared world and the five Step 7 tdd files (group 5); the validation plan (group 6). The code review transcript is not staged and goes to the residual commit.

### Human guidance and writer response for step 7 resume-paused (round 2)

Human guidance:

Round 1 of the Step 7 code review escalated on 2026-11-21 at 14:45 (+01:00) when the requestor's `wait-answer` reached its full 10800-second bound. No reviewer had claimed the request: the reviewer nature was still unrecorded, the owner was the requestor, and the generation was 1. Nothing failed. The request, the bound scope (fingerprint `686958cd`), the staged index tree `2f9916bc` and `a.commit` are unchanged.

The human chose to treat the escalation as a stopped handoff and resume it. The same round 1 request goes back to the reviewer unchanged, and the requestor waits again for its answer.

Writer response:

All six round 1 findings are accepted and repaired; there is no disagreement. Your staged Step 7 rows were the starting point of the updated validation plan, which reads Yes again with the round 1 repairs recorded and the missing-work list removed.

- **Prompt accepted for delivery**: `CheckoutPlan.digest` records the digest of the saved prompt the plan accepted, and the worker exposes it as `PairDelivery.digest`. `consumption`, `takeover_ready` and `takeover` take that `intended` digest. When the saved prompt is still the intended one and only an older receipt names other bytes (`NEW_SINCE_USE`), the proof waits (`receipt-earlier`). A saved prompt whose digest differs from the intended one fails as `prompt-replaced`, with or without a receipt. `MarkedTakeover.received` and every reviewer decision (`Activation.digest`) bind it. Without an intended digest, the earlier rule stays: a receipt for other bytes reads as replaced. Regressions through receiver observation: an older receipt, then this launch's receipt and claim, settles `claimed`; an older receipt alone reaches the bound `completion-unconfirmed`, not failed; a prompt changing before any receipt, or behind an older receipt, fails at the second look; a plan that read other bytes fails at the first look. The proof leaf covers every intended verdict, the activation leaf an older receipt on both routes and a continuation whose prompt changed since planning, and the planner leaf the recorded digest, the new prompt's when an older receipt exists.
- **Question with no blocking reason**: both `_resting` functions refuse a nonempty `PaneActivity.question` on its own, after the blocked check: `reviewer-question` in the reviewer wait, `claude-pane-question` in the guard. Regressions through the takeover, initial activation and continuation: a question on the Claude target, on a non-target Claude pane, and on a Codex target, each pending with zero sends; the guard and reviewer-wait leaves add the same cases.
- **Limits on the worker's own report**: `CLAUDE_WAIT_SCOPE` moved to the delivery model, which the takeover re-exports. `_CheckoutWorker._sequence` adds it to the `requestor-not-accepted` report of a Claude reviewer, while a Codex reviewer's report stays without notes. Regression through the delivery worker: a Claude reviewer after a refused requestor (a pre-send check) and after an unconfirmed one.
- **Deadline between the two reads**: `read_pause` and `read_exchange` split `read_durable`. `_Watch.durable` checks the bound before the saved-prompt read, between the two reads and after the exchange read. Regression: a saved-prompt read that spends the bound leaves the exchange observer with zero calls, and the receiver is `completion-unconfirmed`.
- **Deadline after the last screen reading**: `AllPaneIdleGuard._screen` checks its budget again after `ClaudeScreens.read`, so an idle reading of the last pane that completes after the budget refuses the send (`idle-guard-deadline`, an expected pending refusal). Regression: the second and last pane's reading spends the budget.
- **Linear discovery**: `checkout_claude_panes` returns the members in discovery order from one scan, with no sort. Regression: a listing in reverse order whose members are neither in UUID order nor sorted, checked for membership, capture order and one capture per pane; the existing tests now assert discovery order.
- **Commit plan**: membership changed. `tools/resume_paused_plan_model.py` and the planner tdd join the claim-evidence group, now named `feat(resume-paused): expose claim and prompt evidence`, which moves first because the worker reads `CheckoutPlan.digest`. The other groups keep their subjects; their bodies describe the repairs.

### Reviewer focus for step 7 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-2 -->

## Round 2 by reviewer - Step 7

- Recorded: 2026-11-22T11:42:40+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 resume-paused (exchange 1) (round 2)

Baseline index tree: f36e479952f84c10f73a7b25289f0775380777a0

Assessed index tree: 7ef0716fbafad83e70bbb58779a393b3ea01104d

### Implementation check for step 7 resume-paused (exchange 1) (round 2)

Result:

Step 7 remains incomplete after round 2.

1. Identity passed for the requested plan, step 7, round 2, occurrence 1 and request-time index.
2. All six round 1 cases have code and regression tests. The revised guard now samples its remaining time twice before a capture. Expiration between those samples can start a capture with a nonpositive timeout.
3. The writer reports 7,370 passing tests and 100% line coverage of `tools`. Static review found one behavioral test gap at this new deadline boundary.
4. Staged scope is attributable. The reviewer edited only the step 7 validation rows.
5. One current finding is open. All six carried findings are resolved.
6. The independent commit-plan check passed for six ordered groups covering 24 staged paths.

Validation plan effects:

Recorded the No verdict and the pre-capture timeout regression in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`, including a fake-clock acceptance test. Markdown lint passed. The umbrella comparison reported `applicable=false`, `changed=false`.

### Pre-repair mandatory checks and coverage for step 7 resume-paused (exchange 1) (round 2)

The writer reports a green whole-suite speed walk with 7,370 tests, 100% line coverage of `tools`, and a slowest test call of 0.32 seconds. Reviewer evidence is static inspection of the staged production and test changes, the independent resolver and grouping checks, and validation-plan lint. The tests cover older receipts and replaced prompts, question-only panes on both activation routes, reporting after an unaccepted requestor, the two round 1 deadlines and linear pane discovery.

### Resolved validation set and sources for step 7 resume-paused (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` from the project. The bound whole-suite scope has fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6` and recorded `speed` proof.

### Resolver drift and direction for step 7 resume-paused (exchange 1) (round 2)

None. The independent resolver returned the request command and project source.

### Repository state around validation for step 7 resume-paused (exchange 1) (round 2)

The validation-state comparison reported `acceptable=false` for the validation plan and index. The attributable step 7 metadata edit accounts for both. The index diff between `f36e479952f84c10f73a7b25289f0775380777a0` and `7ef0716fbafad83e70bbb58779a393b3ea01104d` contains only `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. The comparison found no changed ignored or untracked paths.

### Repair inventory for step 7 resume-paused (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 resume-paused (exchange 1) (round 2)

The independent checker exited 0 with `state=valid`, `ready=true`, six ordered groups, 24 staged paths and no diagnostics. Reviewed subjects and membership are

1. `feat(resume-paused): expose claim and prompt evidence`

   - `tools/resume_paused_review.py`
   - `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`
   - `tools/resume_paused_plan_model.py`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`

2. `feat(resume-paused): observe each accepted receiver`

   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`

3. `feat(resume-paused): prove takeover and no wait`

   - `tools/resume_paused_takeover_proof.py`
   - `tools/resume_paused_reviewer_wait.py`

4. `feat(resume-paused): guard Claude reviewer sends`

   - `tools/resume_paused_pane_guard.py`

5. `feat(resume-paused): activate verified reviewers`

   - `tools/resume_paused_takeover.py`
   - `tests/unit/tools/test_resume_paused_takeover/__init__.py`
   - `tests/unit/tools/test_resume_paused_takeover/takeover_world.py`
   - `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py`
   - `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py`
   - `tests/unit/tools/test_resume_paused_takeover_proof/__init__.py`
   - `tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py`
   - `tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py`
   - `tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py`
   - `tests/unit/tools/test_resume_paused_pane_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py`

6. `docs(resume-paused): record step 7 validation`

   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 7 resume-paused (exchange 1) (round 2)

Unresolved findings:

- `tools/resume_paused_pane_guard.py` calls `_expired(deadline)` before `_resting`, then `_screen` samples `_left(deadline)` again and passes it directly to `capture`. A positive first reading followed by a zero or negative second reading invokes the transport after the budget expires. The later check refuses the send but allows the capture to start. Existing tests advance time inside capture or screen classification and miss this ordering.

Boundary-crossing work: None.

### Writer instructions for step 7 resume-paused (exchange 1) (round 2)

In `AllPaneIdleGuard._screen`, sample the remaining time once immediately before `capture`. If it is zero or negative, return `idle-guard-deadline` without calling the transport. Pass the same positive value, capped at the per-call limit, to `capture`. Keep the post-classification check. Add a fake-clock regression where the budget expires between the pane check and capture, and assert that zero captures start on that pane.

### Decision rationale for step 7 resume-paused (exchange 1) (round 2)

Changes requested for the pre-capture deadline check and its regression test. The final-screen check, prompt identity handling, question gates, disclosure, observation read boundary and linear scan all address the previous round.

### Final reviewer decision for step 7 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-7-round-2 -->

## Round 3 by requestor - Step 7

- Recorded: 2026-11-22T11:56:58+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: request

### Review identity for step 7 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 7
Review round: 3

### Code review evidence for step 7 resume-paused (round 3)

request_index_tree: cc3fe46d511c5f74d5ed3a8e3ac36393d6823b10
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): expose claim and prompt evidence
group 1 path: tools/resume_paused_review.py
group 1 path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
group 1 path: tools/resume_paused_plan_model.py
group 1 path: tools/resume_paused_planner.py
group 1 path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
group 2: feat(resume-paused): observe each accepted receiver
group 2 path: tools/resume_paused_delivery_model.py
group 2 path: tools/resume_paused_delivery.py
group 2 path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
group 3: feat(resume-paused): prove takeover and no wait
group 3 path: tools/resume_paused_takeover_proof.py
group 3 path: tools/resume_paused_reviewer_wait.py
group 4: feat(resume-paused): guard Claude reviewer sends
group 4 path: tools/resume_paused_pane_guard.py
group 5: feat(resume-paused): activate verified reviewers
group 5 path: tools/resume_paused_takeover.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
group 5 path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
group 6: docs(resume-paused): record step 7 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py
staged path: tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/__init__.py
staged path: tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py
staged path: tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py
staged path: tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py
staged path: tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover/takeover_world.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/__init__.py
staged path: tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py
staged path: tools/resume_paused_delivery.py
staged path: tools/resume_paused_delivery_model.py
staged path: tools/resume_paused_pane_guard.py
staged path: tools/resume_paused_plan_model.py
staged path: tools/resume_paused_planner.py
staged path: tools/resume_paused_review.py
staged path: tools/resume_paused_reviewer_wait.py
staged path: tools/resume_paused_takeover.py
staged path: tools/resume_paused_takeover_proof.py
```

### Validation scope for step 7 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 7 resume-paused (round 3)

Step 7 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05; round 2 repaired all six round 1 findings, and round 3 repairs the round 2 finding: the guard samples the time left once, immediately before each capture, and bounds the capture with it. `MarkedTakeover` implements the Step 6 takeover seam. It observes every accepted receiver read-only for its own 120-second fake-clock bound, bound to the saved prompt the plan accepted: an older receipt of that prompt waits, and a prompt changed since planning fails, even before any receipt exists. It proves a requestor takeover only from durable records: the schema 3 receipt and the exchange's current marked claim agree on launch, pane, host and binding at the current generation. It decides each conditional reviewer from fresh evidence, on initial activation and later continuation alike: leave-alone first, then the current claim, then positive no-wait evidence, where a question refuses a pane even without a blocking reason. It delivers through the guarded worker with a refreshed decision and the design Q27=B all-pane idle guard as pre-send checks, the guard taking the checkout's Claude panes in one linear scan, starting no capture once its budget is spent or with a nonpositive timeout, and checking the budget again after each capture and each reading. Every Claude reviewer outcome, the worker's own `requestor-not-accepted` report included, carries `limits=claude-wait-scope`. The empty profile registry keeps every real pane unsupported. The validation plan reads `Yes. Step 7 has been fully implemented.` again, with the round 1 repairs recorded.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-22T11:53:16+01:00 with 7379 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s. Before it, the pane-guard and takeover leaves passed in focus with `ghog single` (141 tests). The index tree is `cc3fe46d511c5f74d5ed3a8e3ac36393d6823b10`, the content of the walked working tree up to the validation plan's line endings: an in-place edit after the walk had turned its CRLF endings into LF, restored before staging, so the staged plan differs from the walked one only there.
- Round 2's walks, disclosed then: one stopped on radon C in a planner test, one reached 99% coverage; the round 2 walk recorded in its request was green.
- Static checks: the green walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; `spellcheck.bat check` reports nothing on the validation plan and the round 2 inputs.
- Coverage: 100% over `tools`; each repair has its own regression: older receipts and prompts changed since planning through receiver observation, the reviewer decision and the proofs; questions with no blocking reason on the target and a non-target Claude pane on both routes; the limits on the worker's report after a refused and an unconfirmed requestor; zero exchange reads after a saved-prompt read that spent the bound; the last pane's reading spending the guard's budget; the budget expiring at a pane's pre-capture sample, with zero captures on that pane, and a sweep over every clock call of a two-pane check, with every started capture given a positive timeout (round 3); discovery order with one capture per pane.
- Architecture: the proofs stay pure functions over one fresh durable read, now split into `read_pause` and `read_exchange` so the watch checks its bound between them; the plan's accepted digest reaches the takeover through `PairDelivery.digest`, a read-only port like `root`; `CLAUDE_WAIT_SCOPE` sits in the delivery model, which both the worker and the takeover import, with no new dependency direction.
- Performance: single passes over listings and histories; the guard's membership is one linear scan with no sort, `O(P + C)` per refreshed listing; at most about thirty bounded looks per receiver, one decision plus one pre-send refresh per activation; no `O(n^2)` or `O(n log n)` path.
- Feature integrity: with `NoTakeover`, every Step 6 outcome is unchanged, except that a Claude reviewer's `requestor-not-accepted` report gains the limits note; reports, exchange snapshots and checkout plans gain defaulted fields; every plan outcome and command spelling is unchanged; manual resume, review, validator and claim paths are untouched; the takeover writes nothing.
- Open rows (validation plan): composition by Step 8 (result source, Claude ledger decision, Claude screen profile, reviewer-wait ports, the takeover wiring) and live host evidence (Claude idle screen signature, result line forms and question state, the Claude ledger profile).

### Implementation report for step 7 resume-paused (round 3)

Step 7 confirms takeover and activates only a verified missing reviewer. Under the amended plan Q05 it proceeds code-first against the empty profile registry, with injected ports and fake clocks. It adds four modules and four test leaves, extends the Step 6 seam, and adds one field to the Step 2 exchange snapshot, one field to the Step 5 checkout plan and one function to the Step 5 planner. Round 2 repaired the six round 1 findings; round 3 repairs the one round 2 finding, the guard's pre-capture budget sample.

- `tools/resume_paused_plan_model.py` and `tools/resume_paused_planner.py`: `CheckoutPlan.digest` records the digest of the saved prompt the plan accepted, set once in `_classify` for every prompt-bearing checkout, so a fresh prompt behind an older receipt carries the new prompt's digest. `marked_command(host, kind, marker)` renders the native command and marker, used by `_command` and by the takeover to rebuild a requestor's marked input from its receipt.
- `tools/resume_paused_delivery_model.py` and `tools/resume_paused_delivery.py`, the seam: `ReceiverState` (`unobserved`, `consumed`, `claimed`, `completion-unconfirmed`, `failed`) and the report fields `receiver` and `generation`; `Takeover.received(pair, report)`, which `_CheckoutWorker._sequence` calls for every resume report before any conditional reviewer is decided; `PairDelivery.root`, the guarded checkout, and `PairDelivery.digest`, the plan's accepted prompt, both exposed by the worker. `NoTakeover.received` returns the report unobserved. `CLAUDE_WAIT_SCOPE` now lives in the delivery model: the worker's own `requestor-not-accepted` report of a Claude reviewer carries it, a Codex reviewer's carries no note.
- `tools/resume_paused_review.py`: `ExchangeSnapshot.marked_claim` carries the coordination record's marked claim binding (launch id, receiving pane, host, assignment binding, round, occurrence, issued generation); it holds no token or token digest.
- `tools/resume_paused_takeover_proof.py`, pure proofs over one `Durable` read. `read_pause` reads the saved pause (an unreadable pause fails `evidence-invalid`) and `read_exchange` adds its saved exchange; `read_durable` composes both. `consumption`, `takeover_ready` and `takeover` take the `intended` digest. A removed or unreadable pause fails. With an intended digest, a saved prompt whose digest differs fails `prompt-replaced`, with or without a receipt; the intended prompt waits without a receipt (`receipt-absent`) and behind an older receipt for other bytes (`receipt-earlier`). Without one, a receipt for other bytes reads as replaced, as before. Then another launch's receipt, an unmarked one, or a resumer other than the planned host fails, and the requestor marker is rebuilt from the receipt when none is planned. `takeover_ready` adds a live exchange: busy waits, not live blocks, a changed selection or damage fails, and the recorded requestor nature must be the requestor's host. `current_claim` requires the marked claim of this launch, pane, host and binding at the current ownership generation, owned by the requestor in the same occurrence. It rebuilds the binding with `resolve_assignment` for the requestor role at the claimed round, so a paused reviewer's receipt, or a receipt on an unrouted pane, never proves a counterpart. It names the counterpart pane, whose recorded nature must agree; a switched pair names its switched reviewer. A missing claim waits; a superseded or foreign claim blocks, a competing pickup.
- `tools/resume_paused_reviewer_wait.py`. `reviewer_active` leaves alone a reviewer owning the current generation when its pane agrees: the current marked claim names it, or, without one, its latest typed command is a reviewer `review-resume` (histories are read oldest first). `prior_delivery` reads a marked reviewer entry to this pane since the receipt, undated or malformed, as an uncertain earlier delivery, diagnosed and never resent. `ReviewerWait.verdict` requires a resting pane (no blocking reason, no question even when TUIOS names no blocking reason, no draft, idle or done and ready), a readable history and no prior delivery. A Codex reviewer then needs a supported `IDLE_EMPTY` probe, since an attached global wait is an active turn and reads busy. A Claude reviewer needs a `WaitAbsence` decision proving absence over a `WaitScope` carrying the receipt time, the proved requestor's pane and its rebuilt marked input, for the Q23=A file binding and the Q24=A exception, on both routes. Ledger reasons become `ledger-<code>` notes; `UnprovedAbsence` decides nothing while no ledger profile is pinned.
- `tools/resume_paused_pane_guard.py`, the design Q27=B guard. `AllPaneIdleGuard` is a `PreSendCheck` acting only on Claude reviewer sends. From the send's fresh listing, in one linear scan that keeps discovery order, it takes every live Claude pane whose working directory is the checkout or lies inside it, the requestor and the target included. Each must rest in TUIOS (a question refuses it on its own, `claude-pane-question`) and its fresh capture must read idle under `ClaudeScreens`. A busy, blocked, questioning, draft-holding, unreadable or unknown-layout pane refuses the send, as does a Claude pane whose directory cannot be read; contradictory host evidence fails. Captures are bounded by what is left of the guard's own 30-second budget: `_screen` samples the time left once, immediately before each capture, refuses `idle-guard-deadline` without calling the transport when it is zero or negative, and passes that same positive value, capped at `CALL_BOUND_SECONDS`, to the capture. The budget is checked again after each capture and each screen reading, so neither a capture nor a screen reading completed after it is acted on, the last pane's included, and nothing samples the clock between a pane's TUIOS check and its capture.
- `tools/resume_paused_takeover.py`, `MarkedTakeover.received`: a `_Watch` starts its 120-second bound at acceptance. Each look re-reads the listing (a blocked pane or a question fails `receiver-question`), the result lines (a well-formed `failed` line for this launch fails `receiver-failed`; malformed, foreign, masked or unreadable lines prove nothing) and the durable records, with the bound checked before the saved-prompt read, between it and the exchange read, and after. Backoff runs 0.5, 1, 2, 4, then 5 seconds, capped by what is left; a read completed after the bound is never acted on. Consumption and takeover bind `PairDelivery.digest`. A requestor of a live exchange settles `claimed` with its generation on a proved takeover; any other receiver settles `consumed` on its receipt. At the bound a receipt alone stays `consumed` and nothing durable is `completion-unconfirmed`, both successes; failures set the report failed.
- Same module, `MarkedTakeover.reviewer`: after a resume that is not a requestor's, or that failed, the reviewer is refused. Otherwise one decision on a fresh listing, bound to the plan's prompt through `Activation.digest`, runs the proofs, the leave-alone check (`reviewer-active`, an expected skip), the current claim, the planned reviewer as the proved counterpart (`reviewer-not-paired` fails) and the wait verdict. The planned reviewer marker keeps its launch id but is rebound to the exchange's live occurrence and round, which the reviewer's validator rebuilds; a planned marker that does not parse fails `reviewer-marker-unreadable`. The rebound command is delivered through `PairDelivery.deliver` with two pre-send checks: the decision refreshed on the send's listing, refusing `reviewer-binding-changed` when the live round moved since the decision, and the Q27=B guard. Before a Codex recovery Enter only the durable takeover is refreshed, since the pane holds the command. A refusal by either check reports the reviewer pending; an independent delivery failure stays unchanged. An accepted reviewer is watched for its own 120 seconds until its marked claim, owned by the reviewer at the current generation, is current. Every Claude reviewer outcome carries `limits=claude-wait-scope`; `preview_notes` gives it to conditional Claude reviewer previews; `CLAUDE_WAIT_LIMITS` defines the five disclosed limits for Step 8's help and reference.
- Tests: `tests/unit/tools/test_resume_paused_takeover/` holds `takeover_world.py`, the declared world shared by the four leaves: parsed receipts, exchanges with marked claims, `FakePair` running each phase's checks on a fresh listing and naming the plan's prompt (the first declared pause's unless declared). It also holds an observation tdd (every receiver outcome, each failure, masked lines, discovery loss, the bound exactly filled, a read or a failure read ending after it, an older receipt then a claim, an older receipt alone at the bound, a prompt changing before any receipt or behind an older one, a plan that read other bytes, a saved-prompt read spending the bound with zero exchange reads) and an activation tdd. The activation tdd covers every decision refusal, leave-alone with and without a marked claim, competing pickup, the Codex and Claude wait verdicts, ledger blockers with real reason codes, an uncertain earlier delivery, an unchanged, a switched and a log-evicted continuation, a prompt changed since planning, an older receipt on both routes, questions with no blocking reason on the Claude target, a non-target Claude pane and a Codex target on both routes, rebinding, the refresh and recovery gates, each Q27=B case on both routes, the reviewer watch, limits, previews and two runs through the real Step 6 delivery, one carrying the plan's digest. The proof leaf covers every intended verdict and its pass-through; the reviewer-wait and pane-guard leaves add the question refusal, the guard leaf discovery order with one capture per pane, the last pane's reading spending the budget, the budget expiring at the second pane's pre-capture sample (zero captures on that pane) and a sweep over every clock call of a two-pane check (every capture started has a positive timeout). The delivery leaf covers the digest hand-off and the limits on the worker's report after a refused and an unconfirmed requestor; the planner leaf the recorded digest. No test starts a process or sleeps; every bound runs on a fake clock.
- Deviations: following the plan's split guidance, the proofs, the reviewer wait and the Q27=B guard are separate modules, each with its own leaf; the Q27=B cases the plan places in `test_resume_paused_takeover_tdd.py` are there, run through the takeover with the real guard. The seam extension changes Step 6's model and worker, the marked claim joins the Step 2 snapshot, and `marked_command` and the plan digest join the Step 5 planner and plan model (planner 571 lines, in the 550 to 650 band); the delivery state machine is 595 lines, in the same band; the takeover is 549. The Q23=A and Q24=A record classification stays in Step 1's ledger; Step 7 passes it the requestor binding and acts on its decision. The reviewer marker rebinding is a design consequence found during the step and recorded in the validation plan.
- `rg` is not available in this shell; contract inspection used the equivalent Grep search. No accepted duration exclusion exists.

Writer notes: `.reviews/a.resume-paused.step7.journal.md` and `.reviews/a.resume-paused.step7.handoff.md`.

### Change summary for step 7 resume-paused (round 3)

Twenty-four staged paths in six `a.commit` groups, in this order, unchanged in membership, order and subjects since round 2 (round 2 added `tools/resume_paused_plan_model.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py` to the claim-evidence group, which moved first because the worker reads `CheckoutPlan.digest`):

1. `feat(resume-paused): expose claim and prompt evidence`: `tools/resume_paused_review.py`, `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`, `tools/resume_paused_plan_model.py`, `tools/resume_paused_planner.py` and `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`.
2. `feat(resume-paused): observe each accepted receiver`: `tools/resume_paused_delivery_model.py`, `tools/resume_paused_delivery.py`, `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py` and `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`.
3. `feat(resume-paused): prove takeover and no wait`: `tools/resume_paused_takeover_proof.py` and `tools/resume_paused_reviewer_wait.py`.
4. `feat(resume-paused): guard Claude reviewer sends`: `tools/resume_paused_pane_guard.py`.
5. `feat(resume-paused): activate verified reviewers`: `tools/resume_paused_takeover.py` and the `tests/unit/tools/test_resume_paused_takeover` package (package file, `takeover_world.py`, observation and activation tdd files), with the `tests/unit/tools/test_resume_paused_takeover_proof`, `tests/unit/tools/test_resume_paused_reviewer_wait` and `tests/unit/tools/test_resume_paused_pane_guard` packages (package file and tdd file each), whose tests share the declared world of this group.
6. `docs(resume-paused): record step 7 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The round 2 repair touches `tools/resume_paused_pane_guard.py` (group 4), `tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py` (group 5) and the validation plan (group 6); the bodies of groups 4, 5 and 6 describe it. The code review transcript is not staged and goes to the residual commit.

### Human guidance and writer response for step 7 resume-paused (round 3)

Human guidance:

Round 1 of the Step 7 code review escalated on 2026-11-21 at 14:45 (+01:00) when the requestor's `wait-answer` reached its full 10800-second bound. No reviewer had claimed the request: the reviewer nature was still unrecorded, the owner was the requestor, and the generation was 1. Nothing failed. The request, the bound scope (fingerprint `686958cd`), the staged index tree `2f9916bc` and `a.commit` are unchanged.

The human chose to treat the escalation as a stopped handoff and resume it. The same round 1 request goes back to the reviewer unchanged, and the requestor waits again for its answer.

Writer response:

The round 2 finding is accepted and repaired as instructed; there is no disagreement. Your staged Step 7 rows were the starting point of the updated validation plan, which reads Yes again with the round 2 repair recorded and the missing-work list removed.

- **One sample before each capture**: `AllPaneIdleGuard._screen` samples the time left once, immediately before `capture`. When it is zero or negative it returns `idle-guard-deadline` without calling the transport; otherwise it passes that same positive value, capped at `CALL_BOUND_SECONDS`, to `capture`. The budget is checked again after the capture and after the screen reading, which keeps the post-classification check for every pane, the last included. The loop-level checks of round 2 are gone, so nothing samples the clock between the pane's TUIOS check and its capture. Regressions on a fake clock that spends the whole budget on one declared call of `now`: the budget expiring at the second pane's pre-capture sample refuses the send with zero captures on that pane; a sweep over every clock call of a two-pane check asserts that every capture started received a positive timeout and that the outcome is either a deadline refusal or a pass completed in time.
- **Commit plan**: membership, order and subjects are unchanged; the guard group's body now says the time left is sampled once before each capture and bounds it, and the takeover and validation group bodies name the new regression and the round 2 repair.

### Reviewer focus for step 7 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-3 -->

## Round 3 by reviewer - Step 7

- Recorded: 2026-11-22T12:00:37+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 resume-paused (exchange 1) (round 3)

Baseline index tree: cc3fe46d511c5f74d5ed3a8e3ac36393d6823b10

Assessed index tree: cc3fe46d511c5f74d5ed3a8e3ac36393d6823b10

### Implementation check for step 7 resume-paused (exchange 1) (round 3)

Result:

Step 7 is fully implemented under the amended plan. All six readiness checks pass.

1. Identity matches for the plan, step 7, round 3, occurrence 1 and the requested index.
2. `AllPaneIdleGuard._screen` samples the remaining time once, refuses a nonpositive value, and passes the same positive value capped at the call bound to `capture`. The checks after capture and after classification cover the final pane. The initial and continuation delivery paths use the same guard.
3. The new two-pane test expires the budget at the second pre-capture check and asserts only the first pane was captured. The parameterized test checks that all issued timeouts are positive. Prior tests still cover final-screen expiration. Static assessment found no remaining coverage gap. The writer reports passing focused and whole-suite runs.
4. Staged scope and before/after state pass. The round 3 delta consists of the guard, its tests and the step 7 validation rows.
5. The round 2 deadline finding and all six round 1 findings are resolved.
6. The independent commit-plan checker passed for six ordered groups and 24 paths.

Validation plan effects:

The writer recorded the Yes verdict, fixed deadline behavior, test coverage and deferred Step 8 integration in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. The reviewer verified those rows as staged. Umbrella digest comparison reported `applicable=false`, `changed=false`.

### Pre-repair mandatory checks and coverage for step 7 resume-paused (exchange 1) (round 3)

The writer reports 141 focused tests followed by a whole-suite speed walk with 7,379 passing tests and 100% coverage of `tools`. The slowest test call took 0.31 seconds. The writer disclosed restoring CRLF in the validation plan after that walk. The reviewer assessed the staged fix and assertions statically and checked the index, scope, resolver and grouping independently.

### Resolved validation set and sources for step 7 resume-paused (exchange 1) (round 3)

`ghog day --full=speed --whole-suite`, source `project`. The round binds the whole suite with fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6` and records `speed` proof.

### Resolver drift and direction for step 7 resume-paused (exchange 1) (round 3)

None. The independent resolver matched the request command and source.

### Repository state around validation for step 7 resume-paused (exchange 1) (round 3)

Baseline and assessed index are both `cc3fe46d511c5f74d5ed3a8e3ac36393d6823b10`. The validation-state comparison returned `acceptable=true` with empty tracked, untracked and ignored change lists.

### Repair inventory for step 7 resume-paused (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 resume-paused (exchange 1) (round 3)

Independent check exited 0, `state=valid`, `ready=true`, 24 staged paths, no diagnostics. The six groups match the staged changes in this order.

1. `feat(resume-paused): expose claim and prompt evidence`

   - `tools/resume_paused_review.py`
   - `tests/unit/tools/test_resume_paused_review/test_resume_paused_review_tdd.py`
   - `tools/resume_paused_plan_model.py`
   - `tools/resume_paused_planner.py`
   - `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`

2. `feat(resume-paused): observe each accepted receiver`

   - `tools/resume_paused_delivery_model.py`
   - `tools/resume_paused_delivery.py`
   - `tests/unit/tools/test_resume_paused_delivery_model/test_resume_paused_delivery_model_tdd.py`
   - `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`

3. `feat(resume-paused): prove takeover and no wait`

   - `tools/resume_paused_takeover_proof.py`
   - `tools/resume_paused_reviewer_wait.py`

4. `feat(resume-paused): guard Claude reviewer sends`

   - `tools/resume_paused_pane_guard.py`

5. `feat(resume-paused): activate verified reviewers`

   - `tools/resume_paused_takeover.py`
   - `tests/unit/tools/test_resume_paused_takeover/__init__.py`
   - `tests/unit/tools/test_resume_paused_takeover/takeover_world.py`
   - `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_observation_tdd.py`
   - `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py`
   - `tests/unit/tools/test_resume_paused_takeover_proof/__init__.py`
   - `tests/unit/tools/test_resume_paused_takeover_proof/test_resume_paused_takeover_proof_tdd.py`
   - `tests/unit/tools/test_resume_paused_reviewer_wait/__init__.py`
   - `tests/unit/tools/test_resume_paused_reviewer_wait/test_resume_paused_reviewer_wait_tdd.py`
   - `tests/unit/tools/test_resume_paused_pane_guard/__init__.py`
   - `tests/unit/tools/test_resume_paused_pane_guard/test_resume_paused_pane_guard_tdd.py`

6. `docs(resume-paused): record step 7 validation`

   - `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Findings and boundaries for step 7 resume-paused (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 7 resume-paused (exchange 1) (round 3)

Human guidance:

Round 1 of the Step 7 code review escalated on 2026-11-21 at 14:45 (+01:00) when the requestor's `wait-answer` reached its full 10800-second bound. No reviewer had claimed the request: the reviewer nature was still unrecorded, the owner was the requestor, and the generation was 1. Nothing failed. The request, the bound scope (fingerprint `686958cd`), the staged index tree `2f9916bc` and `a.commit` are unchanged.

The human chose to treat the escalation as a stopped handoff and resume it. The same round 1 request goes back to the reviewer unchanged, and the requestor waits again for its answer.

Guidance response:

The human resumed the earlier timed-out handoff. This review followed the live round 3 identity and independently verified its current index, scope and findings.

### Writer instructions for step 7 resume-paused (exchange 1) (round 3)

None.

### Decision rationale for step 7 resume-paused (exchange 1) (round 3)

Recommend `commit-ready` for step 7. The guard now refuses an expired capture before calling the transport. The regression tests exercise the original failure and preserve the post-classification deadline. All previous findings are closed. The validation plan identifies Step 8 composition and live host checks separately.

### Final reviewer decision for step 7 resume-paused (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-7-round-3 -->

## Round 3 by human - Step 7 - human-confirmation

- Recorded: 2026-11-22T20:49:20+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor - Step 8

- Recorded: 2026-11-23T11:06:38+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 8
- Outcome: request

### Review identity for step 8 resume-paused (round 1)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 8
Review round: 1

### Code review evidence for step 8 resume-paused (round 1)

request_index_tree: 6739d63a68afead0bee979425d4b4fa702307e00
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): render bulk resume results
group 1 path: tools/resume_paused_report.py
group 2: feat(resume-paused): ship the resume_paused command
group 2 path: tools/resume_paused.py
group 2 path: bin/resume_paused.bat
group 2 path: tests/unit/tools/test_resume_paused_cli/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_report/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
group 2 path: tests/memory_filesystem.py
group 3: test(resume-paused): accept the installed workflow
group 3 path: tests/acceptance/resume_paused/__init__.py
group 3 path: tests/acceptance/resume_paused/fakes.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
group 4: docs(resume-paused): document the bulk resume command
group 4 path: README.md
group 4 path: wiki/README.md
group 4 path: wiki/how-to/pause-and-resume-a-session.md
group 4 path: wiki/reference/resume-paused.md
group 5: docs(resume-paused): record step 8 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: README.md
staged path: bin/resume_paused.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/acceptance/resume_paused/__init__.py
staged path: tests/acceptance/resume_paused/fakes.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_cli/__init__.py
staged path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
staged path: tests/unit/tools/test_resume_paused_report/__init__.py
staged path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
staged path: tools/resume_paused.py
staged path: tools/resume_paused_report.py
staged path: wiki/README.md
staged path: wiki/how-to/pause-and-resume-a-session.md
staged path: wiki/reference/resume-paused.md
```

### Validation scope for step 8 resume-paused (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 8 resume-paused (round 1)

Step 8 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05. The human-only `resume_paused` command (`tools/resume_paused.py` behind `bin/resume_paused.bat`) parses only the documented flags, refuses a recognized agent caller before any TUIOS listing, composes the Step 1 to 7 readers, planner, guarded delivery and marked takeover, and prints the compact lines rendered by `tools/resume_paused_report.py` with exit 0, 1 or 2. Help and the new reference page state the human-only contract and define the five `limits=claude-wait-scope` limits. Forty-seven acceptance scenarios drive the production composition over a fake `tuios` at the process boundary and real temporary checkouts, the receivers calling the real validator, receipt, journal and locked marked claim. The empty profile registry keeps every real pane unsupported, so a real launch fails closed before any input. The implementation check recorded `Yes. Step 8 has been fully implemented.`, which turned the validation plan's status to implemented while naming the open follow-ups.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-23T10:53:52+01:00 with 7493 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s; the Step 8 leaves passed in focus first with `ghog single`. The walk ran on the code, tests and documentation now staged, except the validation plan, which the implementation check updated afterwards and which was linted and spell-checked on its own.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check. The first walk failed on typing, lint and complexity findings in the new test files and was repaired before the green walk; markdownlint reports 0 issues and `spellcheck.bat check` nothing on the five changed Markdown files.
- Coverage: 100% over `tools`; `test_resume_paused_cli` reaches `tools/resume_paused.py` and `test_resume_paused_report` reaches `tools/resume_paused_report.py`. The launcher is outside the gate and checked statically.
- Architecture: `tools/resume_paused.py` is the composition root and the only module binding adapters to ports; the report module is pure; host formats stay behind `HostAdapters`, TUIOS behind the transport and its runner factory, Windows behind `ProcessLister`; nothing imports the command line.
- Performance: linear parsing and rendering, one journal read per launch and none for an agent caller; the earlier steps' fresh evidence before each send is unchanged.
- Feature integrity: readers, planner, delivery, takeover, manual workflows, the validator and the Step 4 harness are unchanged; joining the memory scratch filesystem affects only the two new test trees.
- Open rows (validation plan): the Step 1 Q28=A code follow-up and live matrix, the host-dependent composition rows (command history, agent log, delivery profiles, result source, Claude ledger, Claude screens) and the deferred senv integration checklist.

### Implementation report for step 8 resume-paused (round 1)

The plan's Step 8 asks for the CLI, its launcher, the documentation, a CLI unit leaf and three acceptance modules over fake TUIOS, with the five limits defined in help and reference and no live TUIOS.

- **Command line** (`tools/resume_paused.py`): `build_parser` and `parse_arguments` accept only `--dry-run`, `--clear`, the repeatable comma-split `--except` and `--switch-roles` lists and `--help`; abbreviations are off and any other argument or an empty name raises `UsageError`, so `main` prints the usage on standard error and returns 2 before composing a runtime. The help restates the human-only contract, the statuses, the exit codes and the five `CLAUDE_WAIT_LIMITS` entries. `execute` classifies the caller (`classify_caller` over the environment markers and `process_ancestry`), so an agent caller reads neither the journal nor TUIOS; `TUIOS_PANE_ID` names the protected caller pane inside TUIOS.
- **Composition** (`tools/resume_paused.py`): `compose` binds `TuiosTransport`, the planner ports, one `PlanRecheck` of this request in `DeliveryPorts.checks`, and `MarkedTakeover` over `ReviewerWait` and `AllPaneIdleGuard`. `HostAdapters` bundles the host-profile adapters; `unpinned_hosts` returns the production bundle that proves nothing (unreadable history and log, unsupported screens, `UnpinnedProfiles`, `UnprovedAbsence`, `UnpinnedClaudeScreens`, `NoResults`, and per-proof `ClaudeInputProver` and `CodexInputProver` factories over the budget-bounded readers). `SavedExchanges` observes a saved exchange read-only, an unloadable checkout reading as damaged.
- **Reporting** (`tools/resume_paused_report.py`): one line per prompt-bearing checkout, `PLAN`, `DONE`, `PENDING`, `SKIP`, `ERROR` or `FAIL`, with the pause, reason, switch, duplicate evidence (known resumer and time or `unknown`), then each target's identity with its marked command in a preview or its clear, outcome, receiver observation, reason and recovery Enter after a delivery; bracketed notes carry `limits=claude-wait-scope`. Run-wide refusals replace the lines, and two checkouts sharing a folder name are named by their full paths, a gap the acceptance found.
- **Launcher** (`bin/resume_paused.bat`): self-locates llm-shared, selects the newest `venvs\python_3*llm-shared*` Python, forwards `%*` only to `tools\resume_paused.py`; tested statically, never executed.
- **Documentation**: `README.md`, the how-to section "Resume every waiting pane at once" (the former planned-command paragraph replaced), `wiki/reference/resume-paused.md` and its wiki index entry.
- **Unit leaves**: `tests/unit/tools/test_resume_paused_cli/` and `tests/unit/tools/test_resume_paused_report/`.
- **Acceptance** (`tests/acceptance/resume_paused/`): `fakes.py` implements the fake `tuios` runner behind the real transport and receiving agents running the Step 4 harness with the real validator over live fake discovery. Four behaviors model the real receiving workflows where the harness simplifies, without changing it: `HostedCheckout` names the receiving host's agent id as resumer (the harness always wrote `claude`, which the takeover correctly refused for a Codex requestor), `MarkedHarness` claims again with the marker's `--override` on a role conflict (review-resume, "Continue a marked review role"; the switched pair needs it), receivers act when the launch waits rather than inside the ask (the synchronous form let a receiver's later typed input defeat the delivery's own latest-input proof), and a stopped receiver prints its `resume-paused <launch_id> failed` line. The three modules own the plan's Q03 cases; later-continuation cases declare the earlier takeover instead of replaying a launch, one transition per test.
- **Deviations**: `tools/resume_paused.py` reached 665 physical lines, so the rendering moved to `tools/resume_paused_report.py` with its own leaf (command line now 501 lines). The two new test trees join `tests/memory_filesystem.py`'s scenario list, because a launch on native temporary files spent 0.19 s of CPU against the 0.1 s ceiling. `wiki/README.md` lists the reference page.

Writer notes: `.reviews/a.resume-paused.step8.journal.md` and `.reviews/a.resume-paused.step8.handoff.md`.

### Change summary for step 8 resume-paused (round 1)

Nineteen staged paths in five `a.commit` groups, in this order:

1. `feat(resume-paused): render bulk resume results`: `tools/resume_paused_report.py`.
2. `feat(resume-paused): ship the resume_paused command`: `tools/resume_paused.py`, `bin/resume_paused.bat`, the `tests/unit/tools/test_resume_paused_cli` and `tests/unit/tools/test_resume_paused_report` packages (package file and tdd file each) and `tests/memory_filesystem.py`.
3. `test(resume-paused): accept the installed workflow`: the `tests/acceptance/resume_paused` package (`__init__.py`, `fakes.py`, and the `test_resume_paused_acceptance` package with its cli_safety, delivery and continuation tdd files).
4. `docs(resume-paused): document the bulk resume command`: `README.md`, `wiki/README.md`, `wiki/how-to/pause-and-resume-a-session.md` and `wiki/reference/resume-paused.md`.
5. `docs(resume-paused): record step 8 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 8 resume-paused (round 1)

Writer response:

First round of this step: no earlier feedback to answer and no disagreement. Please write file paths in code spans in answers, so names such as `__init__.py` cannot read as emphasis in the transcript. Agents must not execute `bin/resume_paused.bat`, help and dry run included; judge it from its source and the static test.

### Reviewer focus for step 8 resume-paused (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-1 -->

## Round 1 by reviewer - Step 8

- Recorded: 2026-11-23T11:13:41+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 resume-paused (exchange 1) (round 1)

Baseline index tree: 6739d63a68afead0bee979425d4b4fa702307e00

Assessed index tree: 2ddc857ce9a6649989f00702f8a3d42399a701d8

### Implementation check for step 8 resume-paused (exchange 1) (round 1)

Result:

No. Step 8 has NOT been fully implemented.

The CLI, reporting, docs and fake-TUIOS workflow are present. Four issues affect pre-send duplicate protection, reporting and exact argument forwarding.

Validation plan effects:

Updated only the Step 8 verdict, summary and missing-work rows in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. The recorded pre-edit blob matched the index. Staged the attributable review metadata. The requestor should reconcile the overall completion line and the Step 8 commit description when applying the findings.

### Pre-repair mandatory checks and coverage for step 8 resume-paused (exchange 1) (round 1)

The requestor reports 7,493 tests passing with 100% line coverage over `tools`. I inspected the composition, report, static batch checks and acceptance assertions. The CMD assertion itself encodes the wrong result. No additional test run was needed to establish these findings. Live profiles remain unpinned under the approved code-first plan.

### Resolved validation set and sources for step 8 resume-paused (exchange 1) (round 1)

Project default `ghog day --full=speed --whole-suite`. The bound round scope is `whole`, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 8 resume-paused (exchange 1) (round 1)

No drift. The built-in speed command and the whole-suite selection match the request. No additional plan or request command was declared.

### Repository state around validation for step 8 resume-paused (exchange 1) (round 1)

The request and initial index both identified `6739d63a68afead0bee979425d4b4fa702307e00`. The before/after evidence reported only the expected Step 8 validation-plan change. The umbrella check was inapplicable.

### Repair inventory for step 8 resume-paused (exchange 1) (round 1)

Repairs made:

- Polishing-only review metadata in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Recorded the Step 8 verdict and missing work. No implementation repair.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 8 resume-paused (exchange 1) (round 1)

Independent `commit-plan-check` returned `valid`, `ready=true`, five ordered groups covering all 19 staged paths and no diagnostics. The groups are `feat(resume-paused): render bulk resume results`, `feat(resume-paused): ship the resume_paused command`, `test(resume-paused): accept the installed workflow`, `docs(resume-paused): document the bulk resume command`, `docs(resume-paused): record step 8 validation`. The last group’s body needs updating after the revised verdict.

### Findings and boundaries for step 8 resume-paused (exchange 1) (round 1)

Unresolved findings:

- `tools/resume_paused.py:349` binds `PlanRecheck` to the original `PlannerPorts`. `execute` reads `runtime.journal()` once, before planning. A resume entry appended after planning is invisible under the checkout guard, so a supported target can receive a duplicate clear or resume. An unreadable journal at that boundary also goes undetected.
- `tools/resume_paused_report.py` formats every action using its saved role and host. The CMD-counterpart acceptance case explicitly expects `reviewer claude ... skipped: target-not-agent` for a live shell. Both preview and execution must identify that slot as having no LLM counterpart. The input suppression itself is correct.
- `checkout_line` prints the prompt state and target identity, but a successful line omits each target’s saved routing source and validation result. A routing skip may also omit the affected target. The requirement’s “Preview and result reporting” section requires that information for each target.
- `bin/resume_paused.bat:2` enables delayed expansion while forwarding `%*`. A legal selection such as `--except work!` can reach Python as `work`, potentially excluding a different checkout. The static launcher test checks the forwarding line but misses the expansion mode.

Boundary-crossing work: None.

### Writer instructions for step 8 resume-paused (exchange 1) (round 1)

- Refresh the journal used by `PlanRecheck` at each pre-send safety check. Add a composition test where the journal gains a later resume entry after planning and before the first send, and another where it becomes unreadable. Verify the skip or error and zero input.
- Render a non-agent in the saved reviewer slot as no LLM counterpart in preview and execution. Update the shell-counterpart acceptance test to require that outcome and to reject the Claude reviewer label.
- Include each target’s saved or unresolved routing source and validation result or reason in the compact line. Cover a validated target and an unresolved target in reporting tests and update the reference examples.
- Disable delayed expansion when forwarding arguments in `bin/resume_paused.bat` so `--except` and `--switch-roles` preserve literal exclamation marks. Extend the static launcher test.
- Reconcile the validation plan and `a.commit` with the repaired result, rerun the required validation and publish a replacement round.

### Decision rationale for step 8 resume-paused (exchange 1) (round 1)

The exact identity and staged attribution pass. Implementation completeness and test adequacy remain open on four findings. The independent commit-plan check passed mechanically. The current findings and the stale Step 8 completion wording preclude a commit-ready recommendation.

### Final reviewer decision for step 8 resume-paused (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-1 -->

## Round 2 by requestor - Step 8

- Recorded: 2026-11-23T11:37:10+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 resume-paused (round 2)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 8
Review round: 2

### Code review evidence for step 8 resume-paused (round 2)

request_index_tree: 0b75d518c39f0f1e85acabd6cd94f100c4e82e57
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): render bulk resume results
group 1 path: tools/resume_paused_report.py
group 2: feat(resume-paused): ship the resume_paused command
group 2 path: tools/resume_paused.py
group 2 path: bin/resume_paused.bat
group 2 path: tests/unit/tools/test_resume_paused_cli/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_report/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
group 2 path: tests/memory_filesystem.py
group 3: test(resume-paused): accept the installed workflow
group 3 path: tests/acceptance/resume_paused/__init__.py
group 3 path: tests/acceptance/resume_paused/fakes.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
group 4: docs(resume-paused): document the bulk resume command
group 4 path: README.md
group 4 path: wiki/README.md
group 4 path: wiki/how-to/pause-and-resume-a-session.md
group 4 path: wiki/reference/resume-paused.md
group 5: docs(resume-paused): record step 8 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: README.md
staged path: bin/resume_paused.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/acceptance/resume_paused/__init__.py
staged path: tests/acceptance/resume_paused/fakes.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_cli/__init__.py
staged path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
staged path: tests/unit/tools/test_resume_paused_report/__init__.py
staged path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
staged path: tools/resume_paused.py
staged path: tools/resume_paused_report.py
staged path: wiki/README.md
staged path: wiki/how-to/pause-and-resume-a-session.md
staged path: wiki/reference/resume-paused.md
```

### Validation scope for step 8 resume-paused (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 8 resume-paused (round 2)

Step 8 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05, after repairing the four round 1 findings. The human-only `resume_paused` command (`tools/resume_paused.py` behind `bin/resume_paused.bat`) parses only the documented flags, refuses a recognized agent caller before any TUIOS listing, composes the Step 1 to 7 readers, planner, guarded delivery and marked takeover, re-reads the session journal at every pre-send recheck, and prints the compact lines rendered by `tools/resume_paused_report.py` with exit 0, 1 or 2; each target names its routing source and validation result, and a shell slot reads as no LLM counterpart. Help and the reference page state the human-only contract and define the five `limits=claude-wait-scope` limits. Fifty-five acceptance scenarios drive the production composition over a fake `tuios` at the process boundary and real temporary checkouts, the receivers calling the real validator, receipt, journal and locked marked claim. The empty profile registry keeps every real pane unsupported, so a real launch fails closed before any input. The implementation check reads `Yes. Step 8 has been fully implemented.` again, with the round 1 repairs recorded and the open follow-ups named.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-23T11:33:37+01:00 with 7503 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s (one pyright narrowing fix after the first post-repair walk); the Step 8 leaves passed in focus first with `ghog single`. The walk ran on the staged tree as it is now, apart from the validation plan and `a.commit` wording, updated afterwards and linted and spell-checked on their own.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; markdownlint reports 0 issues and `spellcheck.bat check` nothing on the changed Markdown files.
- Coverage: 100% over `tools`; `test_resume_paused_cli` reaches `tools/resume_paused.py` and `test_resume_paused_report` reaches `tools/resume_paused_report.py`. The launcher is outside the gate and checked statically.
- Architecture: `tools/resume_paused.py` is the composition root and the only module binding adapters to ports; the report module is pure; host formats stay behind `HostAdapters`, TUIOS behind the transport and its runner factory, Windows behind `ProcessLister`; nothing imports the command line.
- Performance: linear parsing and rendering; one journal read for planning and one per pre-send recheck, none for an agent caller; the earlier steps' fresh evidence before each send is unchanged.
- Feature integrity: readers, planner, delivery, takeover, manual workflows, the validator and the Step 4 harness are unchanged; joining the memory scratch filesystem affects only the two new test trees.
- Open rows (validation plan): the Step 1 Q28=A code follow-up and live matrix, the host-dependent composition rows (command history, agent log, delivery profiles, result source, Claude ledger, Claude screens) and the deferred senv integration checklist.

### Implementation report for step 8 resume-paused (round 2)

The plan's Step 8 asks for the CLI, its launcher, the documentation, a CLI unit leaf and three acceptance modules over fake TUIOS, with the five limits defined in help and reference and no live TUIOS.

- **Command line** (`tools/resume_paused.py`): `build_parser` and `parse_arguments` accept only `--dry-run`, `--clear`, the repeatable comma-split `--except` and `--switch-roles` lists and `--help`; abbreviations are off and any other argument or an empty name raises `UsageError`, so `main` prints the usage on standard error and returns 2 before composing a runtime. The help restates the human-only contract, the statuses, the exit codes and the five `CLAUDE_WAIT_LIMITS` entries. `execute` classifies the caller (`classify_caller` over the environment markers and `process_ancestry`), so an agent caller reads neither the journal nor TUIOS; `TUIOS_PANE_ID` names the protected caller pane inside TUIOS.
- **Composition** (`tools/resume_paused.py`): `compose` binds `TuiosTransport`, the planner ports, one `PlanRecheck` of this request in `DeliveryPorts.checks`, and `MarkedTakeover` over `ReviewerWait` and `AllPaneIdleGuard`. `HostAdapters` bundles the host-profile adapters; `unpinned_hosts` returns the production bundle that proves nothing (unreadable history and log, unsupported screens, `UnpinnedProfiles`, `UnprovedAbsence`, `UnpinnedClaudeScreens`, `NoResults`, and per-proof `ClaudeInputProver` and `CodexInputProver` factories over the budget-bounded readers). `SavedExchanges` observes a saved exchange read-only, an unloadable checkout reading as damaged.
- **Reporting** (`tools/resume_paused_report.py`): one line per prompt-bearing checkout, `PLAN`, `DONE`, `PENDING`, `SKIP`, `ERROR` or `FAIL`, with the pause, reason, switch, duplicate evidence (known resumer and time or `unknown`), then each target's identity with its marked command in a preview or its clear, outcome, receiver observation, reason and recovery Enter after a delivery; bracketed notes carry `limits=claude-wait-scope`. Run-wide refusals replace the lines, and two checkouts sharing a folder name are named by their full paths, a gap the acceptance found.
- **Launcher** (`bin/resume_paused.bat`): self-locates llm-shared, selects the newest `venvs\python_3*llm-shared*` Python, forwards `%*` only to `tools\resume_paused.py`; tested statically, never executed.
- **Documentation**: `README.md`, the how-to section "Resume every waiting pane at once" (the former planned-command paragraph replaced), `wiki/reference/resume-paused.md` and its wiki index entry.
- **Unit leaves**: `tests/unit/tools/test_resume_paused_cli/` and `tests/unit/tools/test_resume_paused_report/`.
- **Acceptance** (`tests/acceptance/resume_paused/`): `fakes.py` implements the fake `tuios` runner behind the real transport and receiving agents running the Step 4 harness with the real validator over live fake discovery. Four behaviors model the real receiving workflows where the harness simplifies, without changing it: `HostedCheckout` names the receiving host's agent id as resumer (the harness always wrote `claude`, which the takeover correctly refused for a Codex requestor), `MarkedHarness` claims again with the marker's `--override` on a role conflict (review-resume, "Continue a marked review role"; the switched pair needs it), receivers act when the launch waits rather than inside the ask (the synchronous form let a receiver's later typed input defeat the delivery's own latest-input proof), and a stopped receiver prints its `resume-paused <launch_id> failed` line. The three modules own the plan's Q03 cases; later-continuation cases declare the earlier takeover instead of replaying a launch, one transition per test.
- **Deviations**: `tools/resume_paused.py` reached 665 physical lines, so the rendering moved to `tools/resume_paused_report.py` with its own leaf (command line now 509 lines, report 241; `tests/acceptance/resume_paused/fakes.py` is 606, in the 550 to 650 band). The two new test trees join `tests/memory_filesystem.py`'s scenario list, because a launch on native temporary files spent 0.19 s of CPU against the 0.1 s ceiling. `wiki/README.md` lists the reference page.

- **Round 1 repairs**: `_replan` reads `runtime.journal()` at every recheck; `_target` adds the routing source and validation result and names a non-agent slot `no LLM counterpart` or `no LLM target`; `_verdict` adds `routing unresolved: no target validated or typed into` for the routing reasons; the launcher disables delayed expansion. Tests: two journal scenarios in the delivery module, the CMD case in preview and run, report-leaf cases for validated, unvalidated and unresolved targets, a CLI-leaf journal-read count, and the launcher's expansion mode.

Writer notes: `.reviews/a.resume-paused.step8.journal.md` and `.reviews/a.resume-paused.step8.handoff.md`.

### Change summary for step 8 resume-paused (round 2)

Nineteen staged paths in five `a.commit` groups, in this order:

1. `feat(resume-paused): render bulk resume results`: `tools/resume_paused_report.py`.
2. `feat(resume-paused): ship the resume_paused command`: `tools/resume_paused.py`, `bin/resume_paused.bat`, the `tests/unit/tools/test_resume_paused_cli` and `tests/unit/tools/test_resume_paused_report` packages (package file and tdd file each) and `tests/memory_filesystem.py`.
3. `test(resume-paused): accept the installed workflow`: the `tests/acceptance/resume_paused` package (`__init__.py`, `fakes.py`, and the `test_resume_paused_acceptance` package with its cli_safety, delivery and continuation tdd files).
4. `docs(resume-paused): document the bulk resume command`: `README.md`, `wiki/README.md`, `wiki/how-to/pause-and-resume-a-session.md` and `wiki/reference/resume-paused.md`.
5. `docs(resume-paused): record step 8 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Membership, order and subjects are unchanged since round 1; the bodies of groups 1 to 5 now mention the round 1 repairs and the corrected scenario count. The reviewer's staged validation-plan edit was reconciled into group 5. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 8 resume-paused (round 2)

Writer response:

All four round 1 findings are accepted and repaired; there is no disagreement. The reviewer's validation-plan edit (Step 8 "No" with a Missing work section) was reconciled after the repairs: Step 8 reads Yes again, its Missing work section is removed, and a round 1 paragraph records what was found and fixed.

- **Journal at each send**: `compose` binds `PlanRecheck` to `_replan`, which replans with `replace(planner, journal=runtime.journal())`, so every pre-send recheck reads the session journal again. New acceptance cases in `test_resume_paused_delivery_tdd.py`: a resume entry recorded after the planning listing skips the first send (`journal-resumed`, exit 0), and a journal unreadable at that send fails it (`duplicate-uncertain`, exit 1); neither types anything. The CLI leaf also checks that two rechecks read the journal twice.
- **Shell counterpart**: `_target` in `tools/resume_paused_report.py` names a `target-not-agent` slot `no LLM counterpart` (reviewer slot) or `no LLM target` (resumed slot), never by its saved role and host. The CMD acceptance case now requires that wording in the preview and after the run and rejects any `reviewer claude` label; the report leaf covers both slots and a delivered report.
- **Routing source and validation**: every target now carries `(saved routing, validated)` or `(saved routing, not validated: <reason>)` for the target-absent, target-not-agent and identity-unavailable skips; a checkout stopped on its routing (missing, table-only, unresolved, pairing-ambiguous or invalid) adds `routing unresolved: no target validated or typed into`. The report leaf covers a validated target, unvalidated ones and each unresolved reason; the reference page shows preview and run examples in the new form.
- **Launcher**: `bin/resume_paused.bat` uses `setlocal DisableDelayedExpansion`, so a literal `!` reaches Python; the static test requires that line and rejects `EnableDelayedExpansion`.

I also corrected my round 1 count of acceptance scenarios: it was 53 then, not forty-seven; with the two journal cases it is 55. `a.commit` keeps its membership, order and subjects; its bodies now mention the repairs.

### Reviewer focus for step 8 resume-paused (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-2 -->

## Round 2 by reviewer - Step 8

- Recorded: 2026-11-23T11:42:48+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 resume-paused (exchange 1) (round 2)

Baseline index tree: 0b75d518c39f0f1e85acabd6cd94f100c4e82e57

Assessed index tree: 8d5f9e182d7093c49464e5e16e2a9aeede218e3e

### Implementation check for step 8 resume-paused (exchange 1) (round 2)

Result:

No. Step 8 has NOT been fully implemented. Delivery refuses a target whose identity has changed. The compact result can still show the original agent as validated.

Validation plan effects:

Updated the Step 8 verdict, missing work and journal read frequency in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 8 resume-paused (exchange 1) (round 2)

The writer reports 7,503 tests passing with 100% coverage. Static review traced the run path from the live identity check to the compact result and inspected the new tests. The shell test changes the pane before planning. It misses the change between planning and delivery. No reviewer test run was needed.

### Resolved validation set and sources for step 8 resume-paused (exchange 1) (round 2)

Project default `ghog day --full=speed --whole-suite`. The bound whole-suite scope fingerprint is `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 8 resume-paused (exchange 1) (round 2)

The bound scope and resolved project command match the request.

### Repository state around validation for step 8 resume-paused (exchange 1) (round 2)

The request and initial index both identified `0b75d518c39f0f1e85acabd6cd94f100c4e82e57`. Evidence comparison found only the Step 8 validation edit. Its pre-edit blob matched the index, and the attributed metadata was staged. Assessed tree `8d5f9e182d7093c49464e5e16e2a9aeede218e3e`. No umbrella applies.

### Repair inventory for step 8 resume-paused (exchange 1) (round 2)

Repairs made:

- Polishing-only review metadata in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Recorded the remaining reporting defect and corrected the journal read description.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 8 resume-paused (exchange 1) (round 2)

The independent checker returned `valid` and `ready=true` for five groups covering all 19 staged paths, with zero diagnostics. The validation group body still describes the step as complete.

### Findings and boundaries for step 8 resume-paused (exchange 1) (round 2)

Unresolved findings:

- `tools/resume_paused_report.py:151` passes only `report.action` to `_target`. When an eligible Claude reviewer becomes a shell between the takeover decision and `pair.deliver`, the fresh `target_refusal` returns `target-not-agent` before input. `_report` keeps the planned action with `skip=None`. The compact line consequently labels the shell `reviewer claude` and `validated` alongside `skipped: target-not-agent`. A disappeared pane or changed host or checkout can also retain that validated label. The resumed-target path has the same issue.

Boundary-crossing work: None.

### Writer instructions for step 8 resume-paused (exchange 1) (round 2)

- Use the live delivery identity verdict in the run result. Show a shell as `no LLM counterpart` or `no LLM target` as appropriate, and show the actual validation failure for an absent or changed target. Preserve valid identity for unrelated refusals such as a busy pane.
- Add a fake-TUIOS acceptance case in which a valid agent becomes a shell before the protected send. Assert zero input to the changed target, its non-agent label and its failed validation reason. Cover other delivery identity refusals in renderer tests.
- Reconcile the validation document and commit-plan completion wording with the result, validate the repair and submit the next round.

### Decision rationale for step 8 resume-paused (exchange 1) (round 2)

Identity and attribution pass, the commit-plan groups cover the index, and the writer supplied green validation evidence. Journal freshness and literal argument forwarding are repaired. The shell label and routing status are correct for planning-time refusals. Incorrect delivery-time identity reporting and the missing regression case keep Step 8 incomplete.

### Final reviewer decision for step 8 resume-paused (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-2 -->

## Round 3 by requestor - Step 8

- Recorded: 2026-11-23T11:52:45+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 resume-paused (round 3)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 8
Review round: 3

### Code review evidence for step 8 resume-paused (round 3)

request_index_tree: de38d60493abe143191a4a00f4b2ce457f583e76
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): render bulk resume results
group 1 path: tools/resume_paused_report.py
group 2: feat(resume-paused): ship the resume_paused command
group 2 path: tools/resume_paused.py
group 2 path: bin/resume_paused.bat
group 2 path: tests/unit/tools/test_resume_paused_cli/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_report/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
group 2 path: tests/memory_filesystem.py
group 3: test(resume-paused): accept the installed workflow
group 3 path: tests/acceptance/resume_paused/__init__.py
group 3 path: tests/acceptance/resume_paused/fakes.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
group 4: docs(resume-paused): document the bulk resume command
group 4 path: README.md
group 4 path: wiki/README.md
group 4 path: wiki/how-to/pause-and-resume-a-session.md
group 4 path: wiki/reference/resume-paused.md
group 5: docs(resume-paused): record step 8 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: README.md
staged path: bin/resume_paused.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/acceptance/resume_paused/__init__.py
staged path: tests/acceptance/resume_paused/fakes.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_cli/__init__.py
staged path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
staged path: tests/unit/tools/test_resume_paused_report/__init__.py
staged path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
staged path: tools/resume_paused.py
staged path: tools/resume_paused_report.py
staged path: wiki/README.md
staged path: wiki/how-to/pause-and-resume-a-session.md
staged path: wiki/reference/resume-paused.md
```

### Validation scope for step 8 resume-paused (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 8 resume-paused (round 3)

Step 8 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05, after repairing the four round 1 findings and the round 2 finding. The human-only `resume_paused` command (`tools/resume_paused.py` behind `bin/resume_paused.bat`) parses only the documented flags, refuses a recognized agent caller before any TUIOS listing, composes the Step 1 to 7 readers, planner, guarded delivery and marked takeover, re-reads the session journal at every pre-send recheck, and prints the compact lines rendered by `tools/resume_paused_report.py` with exit 0, 1 or 2; each target names its routing source and validation result, a send refused on a changed live identity reports that failure, and a shell slot, at planning or at the send, reads as no LLM counterpart or target. Help and the reference page state the human-only contract and define the five `limits=claude-wait-scope` limits. Fifty-six acceptance scenarios drive the production composition over a fake `tuios` at the process boundary and real temporary checkouts, the receivers calling the real validator, receipt, journal and locked marked claim. The empty profile registry keeps every real pane unsupported, so a real launch fails closed before any input. The implementation check reads `Yes. Step 8 has been fully implemented.` again, with the round 1 and round 2 repairs recorded and the open follow-ups named.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-23T11:51:25+01:00 with 7514 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s; the Step 8 leaves passed in focus first with `ghog single`. The walk ran on the staged tree as it is now, apart from the validation plan and `a.commit` wording, updated afterwards and linted and spell-checked on their own.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; markdownlint reports 0 issues and `spellcheck.bat check` nothing on the changed Markdown files.
- Coverage: 100% over `tools`; `test_resume_paused_cli` reaches `tools/resume_paused.py` and `test_resume_paused_report` reaches `tools/resume_paused_report.py`. The launcher is outside the gate and checked statically.
- Architecture: `tools/resume_paused.py` is the composition root and the only module binding adapters to ports; the report module is pure; host formats stay behind `HostAdapters`, TUIOS behind the transport and its runner factory, Windows behind `ProcessLister`; nothing imports the command line.
- Performance: linear parsing and rendering; one journal read for planning and one per pre-send recheck, none for an agent caller; the earlier steps' fresh evidence before each send is unchanged.
- Feature integrity: readers, planner, delivery, takeover, manual workflows, the validator and the Step 4 harness are unchanged; joining the memory scratch filesystem affects only the two new test trees.
- Open rows (validation plan): the Step 1 Q28=A code follow-up and live matrix, the host-dependent composition rows (command history, agent log, delivery profiles, result source, Claude ledger, Claude screens) and the deferred senv integration checklist.

### Implementation report for step 8 resume-paused (round 3)

The plan's Step 8 asks for the CLI, its launcher, the documentation, a CLI unit leaf and three acceptance modules over fake TUIOS, with the five limits defined in help and reference and no live TUIOS.

- **Command line** (`tools/resume_paused.py`): `build_parser` and `parse_arguments` accept only `--dry-run`, `--clear`, the repeatable comma-split `--except` and `--switch-roles` lists and `--help`; abbreviations are off and any other argument or an empty name raises `UsageError`, so `main` prints the usage on standard error and returns 2 before composing a runtime. The help restates the human-only contract, the statuses, the exit codes and the five `CLAUDE_WAIT_LIMITS` entries. `execute` classifies the caller (`classify_caller` over the environment markers and `process_ancestry`), so an agent caller reads neither the journal nor TUIOS; `TUIOS_PANE_ID` names the protected caller pane inside TUIOS.
- **Composition** (`tools/resume_paused.py`): `compose` binds `TuiosTransport`, the planner ports, one `PlanRecheck` of this request in `DeliveryPorts.checks`, and `MarkedTakeover` over `ReviewerWait` and `AllPaneIdleGuard`. `HostAdapters` bundles the host-profile adapters; `unpinned_hosts` returns the production bundle that proves nothing (unreadable history and log, unsupported screens, `UnpinnedProfiles`, `UnprovedAbsence`, `UnpinnedClaudeScreens`, `NoResults`, and per-proof `ClaudeInputProver` and `CodexInputProver` factories over the budget-bounded readers). `SavedExchanges` observes a saved exchange read-only, an unloadable checkout reading as damaged.
- **Reporting** (`tools/resume_paused_report.py`): one line per prompt-bearing checkout, `PLAN`, `DONE`, `PENDING`, `SKIP`, `ERROR` or `FAIL`, with the pause, reason, switch, duplicate evidence (known resumer and time or `unknown`), then each target's identity with its marked command in a preview or its clear, outcome, receiver observation, reason and recovery Enter after a delivery; bracketed notes carry `limits=claude-wait-scope`. Run-wide refusals replace the lines, and two checkouts sharing a folder name are named by their full paths, a gap the acceptance found.
- **Launcher** (`bin/resume_paused.bat`): self-locates llm-shared, selects the newest `venvs\python_3*llm-shared*` Python, forwards `%*` only to `tools\resume_paused.py`; tested statically, never executed.
- **Documentation**: `README.md`, the how-to section "Resume every waiting pane at once" (the former planned-command paragraph replaced), `wiki/reference/resume-paused.md` and its wiki index entry.
- **Unit leaves**: `tests/unit/tools/test_resume_paused_cli/` and `tests/unit/tools/test_resume_paused_report/`.
- **Acceptance** (`tests/acceptance/resume_paused/`): `fakes.py` implements the fake `tuios` runner behind the real transport and receiving agents running the Step 4 harness with the real validator over live fake discovery. Four behaviors model the real receiving workflows where the harness simplifies, without changing it: `HostedCheckout` names the receiving host's agent id as resumer (the harness always wrote `claude`, which the takeover correctly refused for a Codex requestor), `MarkedHarness` claims again with the marker's `--override` on a role conflict (review-resume, "Continue a marked review role"; the switched pair needs it), receivers act when the launch waits rather than inside the ask (the synchronous form let a receiver's later typed input defeat the delivery's own latest-input proof), and a stopped receiver prints its `resume-paused <launch_id> failed` line. The three modules own the plan's Q03 cases; later-continuation cases declare the earlier takeover instead of replaying a launch, one transition per test.
- **Deviations**: `tools/resume_paused.py` reached 665 physical lines, so the rendering moved to `tools/resume_paused_report.py` with its own leaf (command line now 509 lines, report 241; `tests/acceptance/resume_paused/fakes.py` is 606, in the 550 to 650 band). The two new test trees join `tests/memory_filesystem.py`'s scenario list, because a launch on native temporary files spent 0.19 s of CPU against the 0.1 s ceiling. `wiki/README.md` lists the reference page.

- **Round 1 repairs**: `_replan` reads `runtime.journal()` at every recheck; `_target` adds the routing source and validation result and names a non-agent slot `no LLM counterpart` or `no LLM target`; `_verdict` adds `routing unresolved: no target validated or typed into` for the routing reasons; the launcher disables delayed expansion. Tests: two journal scenarios in the delivery module, the CMD case in preview and run, report-leaf cases for validated, unvalidated and unresolved targets, a CLI-leaf journal-read count, and the launcher's expansion mode.

- **Round 2 repair**: `_reported` passes a refused report's reason to `_target`; `_identity_failure` lets a delivery identity refusal from the fresh pre-send check outrank the planned identity, so the run line shows `not validated: <reason>` and a target that became a shell reads `no LLM counterpart` or `no LLM target`; unrelated refusals keep the validated identity. Tests: report-leaf cases for each identity refusal, both shell slots and a busy refusal; a continuation scenario where the reviewer becomes a shell between the takeover decision and the send.

Writer notes: `.reviews/a.resume-paused.step8.journal.md` and `.reviews/a.resume-paused.step8.handoff.md`.

### Change summary for step 8 resume-paused (round 3)

Nineteen staged paths in five `a.commit` groups, in this order:

1. `feat(resume-paused): render bulk resume results`: `tools/resume_paused_report.py`.
2. `feat(resume-paused): ship the resume_paused command`: `tools/resume_paused.py`, `bin/resume_paused.bat`, the `tests/unit/tools/test_resume_paused_cli` and `tests/unit/tools/test_resume_paused_report` packages (package file and tdd file each) and `tests/memory_filesystem.py`.
3. `test(resume-paused): accept the installed workflow`: the `tests/acceptance/resume_paused` package (`__init__.py`, `fakes.py`, and the `test_resume_paused_acceptance` package with its cli_safety, delivery and continuation tdd files).
4. `docs(resume-paused): document the bulk resume command`: `README.md`, `wiki/README.md`, `wiki/how-to/pause-and-resume-a-session.md` and `wiki/reference/resume-paused.md`.
5. `docs(resume-paused): record step 8 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Membership, order and subjects are unchanged since round 1; the bodies of groups 1 to 5 mention the round 1 and round 2 repairs and the scenario count, now 56. The reviewer's staged validation-plan edits of rounds 1 and 2 were reconciled into group 5. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 8 resume-paused (round 3)

Writer response:

The round 2 finding is accepted and repaired; there is no disagreement. The reviewer's validation-plan edit was reconciled after the repair: Step 8 reads Yes again, the Missing work section is removed, the round 1 paragraph is restored beside a round 2 paragraph, and the reviewer's journal-read bullet is kept under a `Reads` label.

- **Delivery-time identity in the run line**: `_reported` in `tools/resume_paused_report.py` passes a refused report's reason to `_target`. Its `_identity_failure` returns the planning-time skip first, otherwise a delivery identity refusal from the fresh pre-send check (`target-absent`, `pane-ambiguous`, `target-session-changed`, `host-contradictory`, `target-not-agent`, `target-host-changed`, `target-identity-unavailable`, `target-checkout-changed`). That failure becomes the target's validation result, and `target-not-agent` turns the identity into `no LLM counterpart` or `no LLM target`. A refusal unrelated to identity, such as `pane-busy`, keeps `(saved routing, validated)`.
- **Regression cases**: the report leaf covers each identity refusal (skipped or failed), both shell slots and a busy refusal. The continuation module adds a fake-TUIOS case where the Claude reviewer's live record becomes a plain shell inside the ledger decision, after the takeover chose to activate it and before the send: the fresh check refuses it, the reviewer pane gets no input, the requestor's claim stays current, and the line reads `no LLM counterpart ... (saved routing, not validated: target-not-agent): skipped: target-not-agent`.

`a.commit` keeps its membership, order and subjects; the bodies of groups 1, 3 and 5 mention the round 2 repair and the 56 scenarios.

### Reviewer focus for step 8 resume-paused (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-3 -->

## Round 3 by reviewer - Step 8

- Recorded: 2026-11-23T11:55:59+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 resume-paused (exchange 1) (round 3)

Baseline index tree: de38d60493abe143191a4a00f4b2ce457f583e76

Assessed index tree: 682dcb75094a1a411a32fea7e4e8e629f32d2aa7

### Implementation check for step 8 resume-paused (exchange 1) (round 3)

Result:

No. Step 8 has NOT been fully implemented. The repaired result is correct when delivery refuses the send to a changed target. A missing reviewer at the takeover check still appears validated.

Validation plan effects:

Recorded the Step 8 verdict and the missing pending-outcome case in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 8 resume-paused (exchange 1) (round 3)

The writer reports 7,514 tests passing with 100% coverage in the whole-suite speed walk. I inspected the new shell-transition acceptance case, the renderer cases and the existing takeover test for an absent reviewer. The existing test establishes the pending outcome. The renderer drops its identity reason before formatting validation. No reviewer test execution was needed.

### Resolved validation set and sources for step 8 resume-paused (exchange 1) (round 3)

The project resolves `ghog day --full=speed --whole-suite` with the bound whole-suite fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 8 resume-paused (exchange 1) (round 3)

The configured command and round scope agree with the request.

### Repository state around validation for step 8 resume-paused (exchange 1) (round 3)

The request and initial index both identified `de38d60493abe143191a4a00f4b2ce457f583e76`. The post-assessment comparison found only the attributable Step 8 validation edit. The assessed index is `682dcb75094a1a411a32fea7e4e8e629f32d2aa7`. No umbrella applies.

### Repair inventory for step 8 resume-paused (exchange 1) (round 3)

Repairs made:

- Polishing-only metadata in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Recorded the remaining result-line defect.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 8 resume-paused (exchange 1) (round 3)

Independent `commit-plan-check` returned `valid`, `ready=true`, five groups, 19 staged paths and zero diagnostics. The group membership, subjects and order fit the staged work. The validation group body needs reconciling with the revised verdict.

### Findings and boundaries for step 8 resume-paused (exchange 1) (round 3)

Unresolved findings:

- `tools/resume_paused_report.py:172` considers `report.reason` only for `REFUSED`. `MarkedTakeover.decide` explicitly returns a pending gate with `target-absent` when its fresh listing lacks the reviewer. `_refused` preserves both as `ActionReport(PENDING, target-absent)`. With a previously valid planned reviewer, the result therefore prints `(saved routing, validated): pending: target-absent`. The absent-reviewer test in `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py:344` already exercises this production outcome. The new renderer tests supply `REFUSED` for every identity failure.

Boundary-crossing work: None.

### Writer instructions for step 8 resume-paused (exchange 1) (round 3)

- Preserve a pending reviewer’s explicit target identity failure in the compact result. For `PENDING` with `target-absent`, report `not validated: target-absent` and retain `pending: target-absent`. Keep the ordinary pending label for waits unrelated to target identity.
- Assert both outcomes in the renderer, including the exact pending outcome produced by the existing absent-reviewer takeover case. Reconcile Step 8 and the commit plan with the repaired result, validate and submit the next round.

### Decision rationale for step 8 resume-paused (exchange 1) (round 3)

The shell-transition acceptance case now exercises the requested boundary and verifies the requestor remains the owner. Renderer tests cover both shell slots, the other refused identity reasons and the busy control. Exact identity, attribution, writer validation evidence and commit grouping pass. The demonstrated pending case keeps implementation completeness and regression coverage open.

### Final reviewer decision for step 8 resume-paused (exchange 1) (round 3)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-3 -->

## Round 4 by requestor - Step 8

- Recorded: 2026-11-23T12:06:34+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 resume-paused (round 4)

Umbrella draft: none
Implementation plan: docs/v0.14.0/plan.v0.14.0.resume-paused.md
Implementation step: 8
Review round: 4

### Code review evidence for step 8 resume-paused (round 4)

request_index_tree: 28b18de8229d1ae2368da36a20d5ef5fe3bb03af
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(resume-paused): render bulk resume results
group 1 path: tools/resume_paused_report.py
group 2: feat(resume-paused): ship the resume_paused command
group 2 path: tools/resume_paused.py
group 2 path: bin/resume_paused.bat
group 2 path: tests/unit/tools/test_resume_paused_cli/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_report/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
group 2 path: tests/memory_filesystem.py
group 3: test(resume-paused): accept the installed workflow
group 3 path: tests/acceptance/resume_paused/__init__.py
group 3 path: tests/acceptance/resume_paused/fakes.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
group 3 path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
group 4: docs(resume-paused): document the bulk resume command
group 4 path: README.md
group 4 path: wiki/README.md
group 4 path: wiki/how-to/pause-and-resume-a-session.md
group 4 path: wiki/reference/resume-paused.md
group 5: docs(resume-paused): record step 8 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: README.md
staged path: bin/resume_paused.bat
staged path: docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md
staged path: tests/acceptance/resume_paused/__init__.py
staged path: tests/acceptance/resume_paused/fakes.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_cli_safety_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_continuation_tdd.py
staged path: tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_delivery_tdd.py
staged path: tests/memory_filesystem.py
staged path: tests/unit/tools/test_resume_paused_cli/__init__.py
staged path: tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py
staged path: tests/unit/tools/test_resume_paused_report/__init__.py
staged path: tests/unit/tools/test_resume_paused_report/test_resume_paused_report_tdd.py
staged path: tools/resume_paused.py
staged path: tools/resume_paused_report.py
staged path: wiki/README.md
staged path: wiki/how-to/pause-and-resume-a-session.md
staged path: wiki/reference/resume-paused.md
```

### Validation scope for step 8 resume-paused (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 8 resume-paused (round 4)

Step 8 is fully implemented, code-first under the user's 2026-11-20 amendment of plan Q05, after repairing the four round 1 findings and the round 2 and round 3 findings. The human-only `resume_paused` command (`tools/resume_paused.py` behind `bin/resume_paused.bat`) parses only the documented flags, refuses a recognized agent caller before any TUIOS listing, composes the Step 1 to 7 readers, planner, guarded delivery and marked takeover, re-reads the session journal at every pre-send recheck, and prints the compact lines rendered by `tools/resume_paused_report.py` with exit 0, 1 or 2; each target names its routing source and validation result, a send refused on a changed live identity, or a reviewer the takeover left pending as `target-absent`, reports that failure, and a shell slot, at planning or at the send, reads as no LLM counterpart or target. Help and the reference page state the human-only contract and define the five `limits=claude-wait-scope` limits. Fifty-six acceptance scenarios drive the production composition over a fake `tuios` at the process boundary and real temporary checkouts, the receivers calling the real validator, receipt, journal and locked marked claim. The empty profile registry keeps every real pane unsupported, so a real launch fails closed before any input. The implementation check reads `Yes. Step 8 has been fully implemented.` again, with the round 1 to round 3 repairs recorded and the open follow-ups named.

- Tests: `ghog day --full=speed --whole-suite` exit 0 at 2026-11-23T12:03:41+01:00 with 7515 tests, 100% coverage, no outlier and no exclusion, slowest call 0.31 s; the Step 8 leaves passed in focus first with `ghog single`. The walk ran on the staged tree as it is now, apart from the validation plan and `a.commit` wording, updated afterwards and linted and spell-checked on their own.
- Static checks: the same walk's `check.bat` passes ty, pyright strict, ruff, radon, vulture, big files, Markdown, ShellCheck and the end-of-file check; markdownlint reports 0 issues and `spellcheck.bat check` nothing on the changed Markdown files.
- Coverage: 100% over `tools`; `test_resume_paused_cli` reaches `tools/resume_paused.py` and `test_resume_paused_report` reaches `tools/resume_paused_report.py`. The launcher is outside the gate and checked statically.
- Architecture: `tools/resume_paused.py` is the composition root and the only module binding adapters to ports; the report module is pure; host formats stay behind `HostAdapters`, TUIOS behind the transport and its runner factory, Windows behind `ProcessLister`; nothing imports the command line.
- Performance: linear parsing and rendering; one journal read for planning and one per pre-send recheck, none for an agent caller; the earlier steps' fresh evidence before each send is unchanged.
- Feature integrity: readers, planner, delivery, takeover, manual workflows, the validator and the Step 4 harness are unchanged; joining the memory scratch filesystem affects only the two new test trees.
- Open rows (validation plan): the Step 1 Q28=A code follow-up and live matrix, the host-dependent composition rows (command history, agent log, delivery profiles, result source, Claude ledger, Claude screens) and the deferred senv integration checklist.

### Implementation report for step 8 resume-paused (round 4)

The plan's Step 8 asks for the CLI, its launcher, the documentation, a CLI unit leaf and three acceptance modules over fake TUIOS, with the five limits defined in help and reference and no live TUIOS.

- **Command line** (`tools/resume_paused.py`): `build_parser` and `parse_arguments` accept only `--dry-run`, `--clear`, the repeatable comma-split `--except` and `--switch-roles` lists and `--help`; abbreviations are off and any other argument or an empty name raises `UsageError`, so `main` prints the usage on standard error and returns 2 before composing a runtime. The help restates the human-only contract, the statuses, the exit codes and the five `CLAUDE_WAIT_LIMITS` entries. `execute` classifies the caller (`classify_caller` over the environment markers and `process_ancestry`), so an agent caller reads neither the journal nor TUIOS; `TUIOS_PANE_ID` names the protected caller pane inside TUIOS.
- **Composition** (`tools/resume_paused.py`): `compose` binds `TuiosTransport`, the planner ports, one `PlanRecheck` of this request in `DeliveryPorts.checks`, and `MarkedTakeover` over `ReviewerWait` and `AllPaneIdleGuard`. `HostAdapters` bundles the host-profile adapters; `unpinned_hosts` returns the production bundle that proves nothing (unreadable history and log, unsupported screens, `UnpinnedProfiles`, `UnprovedAbsence`, `UnpinnedClaudeScreens`, `NoResults`, and per-proof `ClaudeInputProver` and `CodexInputProver` factories over the budget-bounded readers). `SavedExchanges` observes a saved exchange read-only, an unloadable checkout reading as damaged.
- **Reporting** (`tools/resume_paused_report.py`): one line per prompt-bearing checkout, `PLAN`, `DONE`, `PENDING`, `SKIP`, `ERROR` or `FAIL`, with the pause, reason, switch, duplicate evidence (known resumer and time or `unknown`), then each target's identity with its marked command in a preview or its clear, outcome, receiver observation, reason and recovery Enter after a delivery; bracketed notes carry `limits=claude-wait-scope`. Run-wide refusals replace the lines, and two checkouts sharing a folder name are named by their full paths, a gap the acceptance found.
- **Launcher** (`bin/resume_paused.bat`): self-locates llm-shared, selects the newest `venvs\python_3*llm-shared*` Python, forwards `%*` only to `tools\resume_paused.py`; tested statically, never executed.
- **Documentation**: `README.md`, the how-to section "Resume every waiting pane at once" (the former planned-command paragraph replaced), `wiki/reference/resume-paused.md` and its wiki index entry.
- **Unit leaves**: `tests/unit/tools/test_resume_paused_cli/` and `tests/unit/tools/test_resume_paused_report/`.
- **Acceptance** (`tests/acceptance/resume_paused/`): `fakes.py` implements the fake `tuios` runner behind the real transport and receiving agents running the Step 4 harness with the real validator over live fake discovery. Four behaviors model the real receiving workflows where the harness simplifies, without changing it: `HostedCheckout` names the receiving host's agent id as resumer (the harness always wrote `claude`, which the takeover correctly refused for a Codex requestor), `MarkedHarness` claims again with the marker's `--override` on a role conflict (review-resume, "Continue a marked review role"; the switched pair needs it), receivers act when the launch waits rather than inside the ask (the synchronous form let a receiver's later typed input defeat the delivery's own latest-input proof), and a stopped receiver prints its `resume-paused <launch_id> failed` line. The three modules own the plan's Q03 cases; later-continuation cases declare the earlier takeover instead of replaying a launch, one transition per test.
- **Deviations**: `tools/resume_paused.py` reached 665 physical lines, so the rendering moved to `tools/resume_paused_report.py` with its own leaf (command line now 509 lines, report 241; `tests/acceptance/resume_paused/fakes.py` is 606, in the 550 to 650 band). The two new test trees join `tests/memory_filesystem.py`'s scenario list, because a launch on native temporary files spent 0.19 s of CPU against the 0.1 s ceiling. `wiki/README.md` lists the reference page.

- **Round 1 repairs**: `_replan` reads `runtime.journal()` at every recheck; `_target` adds the routing source and validation result and names a non-agent slot `no LLM counterpart` or `no LLM target`; `_verdict` adds `routing unresolved: no target validated or typed into` for the routing reasons; the launcher disables delayed expansion. Tests: two journal scenarios in the delivery module, the CMD case in preview and run, report-leaf cases for validated, unvalidated and unresolved targets, a CLI-leaf journal-read count, and the launcher's expansion mode.

- **Round 2 repair**: `_reported` passes a refused report's reason to `_target`; `_identity_failure` lets a delivery identity refusal from the fresh pre-send check outrank the planned identity, so the run line shows `not validated: <reason>` and a target that became a shell reads `no LLM counterpart` or `no LLM target`; unrelated refusals keep the validated identity. Tests: report-leaf cases for each identity refusal, both shell slots and a busy refusal; a continuation scenario where the reviewer becomes a shell between the takeover decision and the send.

- **Round 3 repair**: `_reported` honors an identity reason for refused and pending reports, so the takeover's pending `target-absent` gate renders `not validated: target-absent` beside `pending: target-absent`; unrelated pending waits keep the validated identity. Test: the report leaf renders the exact report of the takeover's own absent-reviewer case and an unrelated pending wait.

Writer notes: `.reviews/a.resume-paused.step8.journal.md` and `.reviews/a.resume-paused.step8.handoff.md`.

### Change summary for step 8 resume-paused (round 4)

Nineteen staged paths in five `a.commit` groups, in this order:

1. `feat(resume-paused): render bulk resume results`: `tools/resume_paused_report.py`.
2. `feat(resume-paused): ship the resume_paused command`: `tools/resume_paused.py`, `bin/resume_paused.bat`, the `tests/unit/tools/test_resume_paused_cli` and `tests/unit/tools/test_resume_paused_report` packages (package file and tdd file each) and `tests/memory_filesystem.py`.
3. `test(resume-paused): accept the installed workflow`: the `tests/acceptance/resume_paused` package (`__init__.py`, `fakes.py`, and the `test_resume_paused_acceptance` package with its cli_safety, delivery and continuation tdd files).
4. `docs(resume-paused): document the bulk resume command`: `README.md`, `wiki/README.md`, `wiki/how-to/pause-and-resume-a-session.md` and `wiki/reference/resume-paused.md`.
5. `docs(resume-paused): record step 8 validation`: `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

Membership, order and subjects are unchanged since round 1; the bodies of groups 1 to 5 mention the round 1 to round 3 repairs and the scenario count, 56. The reviewer's staged validation-plan edits of rounds 1 to 3 were reconciled into group 5. The commit-plan checker reports the plan valid and ready. The code review transcript is not staged and goes to the residual commit.

### Writer response for step 8 resume-paused (round 4)

Writer response:

The round 3 finding is accepted and repaired; there is no disagreement. The reviewer's validation-plan edit was reconciled after the repair: Step 8 reads Yes again, the Missing work section is removed, and the round 3 paragraph now records the case as found and repaired.

- **Pending identity failure**: `_reported` in `tools/resume_paused_report.py` now passes the reason of a refused or pending report (`_UNSENT`) to `_target`, so the takeover's pending gate for a reviewer missing from its fresh listing renders `(saved routing, not validated: target-absent): pending: target-absent`; the outcome stays `pending`. A grep of the takeover, proof, reviewer-wait and pane-guard modules shows `target-absent` is the only target-identity reason their gates emit (`requestor-pane-absent` and `pane-host-contradictory` concern other panes, not the target). A pending wait unrelated to identity, such as `claude-ledger-unavailable`, keeps `(saved routing, validated)`.
- **Regression case**: the report leaf runs the existing absent-reviewer takeover case through `MarkedTakeover` (its `initial` helper and declared world), asserts the produced report is `PENDING` with `target-absent`, and renders it; it also renders an unrelated pending wait.

`a.commit` keeps its membership, order and subjects; groups 1 and 5 mention the round 3 repair.

### Reviewer focus for step 8 resume-paused (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-4 -->

## Round 4 by reviewer - Step 8

- Recorded: 2026-11-23T12:08:23+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 resume-paused (exchange 1) (round 4)

Baseline index tree: 28b18de8229d1ae2368da36a20d5ef5fe3bb03af

Assessed index tree: 46afddf0083cf6a503ad9433184749d30d419044

### Implementation check for step 8 resume-paused (exchange 1) (round 4)

Result:

Yes. Step 8 has been fully implemented. The run line now reports a missing reviewer as pending with failed target validation. Pending waits unrelated to identity retain the validated target. Previous rounds verified fresh journal checks, literal launcher arguments, and shell handling at planning and delivery.

Validation plan effects:

Confirmed the existing Step 8 verdict and recorded the round 4 regression evidence in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`.

### Pre-repair mandatory checks and coverage for step 8 resume-paused (exchange 1) (round 4)

The writer reports 7,515 tests passing with 100% coverage in the whole-suite speed walk, with no outlier or exclusion. Static review checked the staged renderer and regression assertions. The new test obtains `PENDING, target-absent` from `MarkedTakeover`, renders it, and checks the unrelated ledger-wait control. No additional reviewer test run was needed. The live host matrix and profile pinning remain external evidence under the approved code-first plan.

### Resolved validation set and sources for step 8 resume-paused (exchange 1) (round 4)

The project resolves `ghog day --full=speed --whole-suite`. The captured whole-suite scope fingerprint is `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`.

### Resolver drift and direction for step 8 resume-paused (exchange 1) (round 4)

The request and the current project validation command and scope agree.

### Repository state around validation for step 8 resume-paused (exchange 1) (round 4)

The request and initial index both identified `28b18de8229d1ae2368da36a20d5ef5fe3bb03af`. The post-assessment comparison found only the Step 8 validation note. Its original blob matched the index and the attributed edit was staged. The assessed tree is `46afddf0083cf6a503ad9433184749d30d419044`. No umbrella applies.

### Repair inventory for step 8 resume-paused (exchange 1) (round 4)

Repairs made:

- Polishing-only review metadata in `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`. Added the independent round 4 verification. The writer supplied the implementation and regression repairs before the request.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.resume-paused.validation.md`

### Commit plan assessment for step 8 resume-paused (exchange 1) (round 4)

Independent `commit-plan-check` returned `valid`, `ready=true`, with five ordered groups covering all 19 staged paths and zero diagnostics. The subjects, scope, ordering and validation group body match the assessed index.

### Findings and boundaries for step 8 resume-paused (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 8 resume-paused (exchange 1) (round 4)

None.

### Decision rationale for step 8 resume-paused (exchange 1) (round 4)

Exact identity, Step 8 completeness, validation and static coverage, staged attribution, resolution of all carried findings, and commit grouping pass. The reviewer added only the validation note. The human owns the commit decision.

### Final reviewer decision for step 8 resume-paused (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-8-round-4 -->

## Round 4 by human - Step 8 - human-confirmation

- Recorded: 2026-11-23T16:58:51+01:00
- Exchange: code/code/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/plan.v0.14.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 1 by requestor - Step 1 (exchange 2)

- Recorded: 2026-11-25T18:17:43+01:00
- Exchange: code/code/v0.15.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.15.0/plan.v0.15.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (exchange 2) (round 1)

Umbrella draft: none
Implementation plan: docs/v0.15.0/plan.v0.15.0.resume-paused.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 resume-paused (exchange 2) (round 1)

request_index_tree: cd3035f88fe46f5230d288efbd0ad1a36b9b3279
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.15.0/feature-request.v0.15.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(resume-paused): leave unproved boots unresolved
group 1 path: tools/resume_paused_profiles.py
group 1 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 1 path: tests/unit/tools/resume_paused_test_support.py
group 2: refactor(resume-paused): move generation checks
group 2 path: tools/resume_paused_claude_generation.py
group 2 path: tests/unit/tools/test_resume_paused_claude_generation/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
group 3: fix(resume-paused): limit history only on true boot
group 3 path: tools/resume_paused_claude_ledger.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py
group 4: test(resume-paused): never reuse a clean recheck
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md
group 5 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude_generation/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tools/resume_paused_claude_generation.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_profiles.py
```

### Validation scope for step 1 resume-paused (exchange 2) (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (exchange 2) (round 1)

Yes. Step 1 has been fully implemented, including its design Q28=A code
follow-up: the four "Open code follow-up for Step 1" rows of the validation
plan are implemented, tested and checked. The Step 1 live validation checklist
stays open by design (plan Q05=A): no host profile is pinned, so no real pane
receives input.

- **Tests**: `ghog single` on the profile, generation, ledger and Codex test
  targets passed (317 tests). The scope-resolved walk `ghog day --whole-suite`
  passed: check.bat green, 915 affected tests. The requestor validation set
  `ghog day --full=speed --whole-suite` passed on the staged tree: 8348
  tests, fail 0, coverage 100, duration outliers 0, exclusions 0, proof
  speed.
- **Static checks**: check.bat (pyright, ty, ruff, radon, vulture, big files,
  Markdown) is green. Its first run failed only on a pyright unknown-type
  finding in the new generation test, fixed by typing the empty set; ruff's
  automatic fixes of three style findings are kept.
- **Coverage**: the gate measures `tools`, the new generation module
  included, and reports 100% for the suite. The generation module is
  covered by its own test package; the profile and ledger changes by their
  existing packages plus the new boot test.
- **Architecture**: the boot policy stays in `resume_paused_profiles`, which
  still imports no sibling. The generation module imports the Claude parsing
  and Windows modules only. The ledger reads the decision's state and never
  decides boot semantics. No adapter or port changed.
- **Performance**: the boot decision is a fixed number of comparisons. An
  unresolved boundary adds the per-record lifecycle checks for older
  transcripts, still one pass per file. With durable schedules those files
  were already read; with session-only schedules the extra read stays
  proportional to the listed bytes. No `O(n^2)` or `O(n log n)` path is added.
- **Feature integrity**: no production code builds a `LedgerScope` or calls
  `boot_boundary`, since the composition plugs the unpinned adapters; the
  changed signatures reach tests only. `continuation_places`' only importer,
  a test, moved with it.
- **Markdown**: the validation plan passes markdown-check and cSpell after
  `markerless` was added to the project and user dictionaries.

### Implementation report for step 1 resume-paused (exchange 2) (round 1)

This exchange reviews the Step 1 code follow-up of design Q28=A, which the
earlier Step 1 exchange (converged at round 6 and committed) did not cover:
the four rows of "Open code follow-up for Step 1" in the validation plan. The
work sits on branch `integration/resume-paused`, created from `main` at the
v0.15.0 release commit.

- **`tools/resume_paused_profiles.py`** (row 1): new `BootBoundary` state
  (resolved, unresolved, pending) and `BootSemantics` (true boot,
  sleep-inclusive uptime, fixed tolerance, tolerance basis, accepted clock
  uncertainty). `HostProfile` gains an optional `boot` field. `BootDecision`
  replaces `verdict` with `state`. `boot_boundary(observation, semantics)`
  returns pending for negative uptime or a negative recorded tolerance;
  otherwise it stays unresolved, with one reason per missing predicate
  (`boot-semantics-unpinned`, `true-boot-unvalidated`,
  `uptime-sleep-unvalidated`, `tolerance-basis-unrecorded`), whatever the clock
  comparison says. With validated semantics it keeps the Q21=A backward-clock
  check (pending beyond the tolerance) and otherwise resolves at the fixed
  boot instant. The shipped registry records no semantics, so every real
  decision is unresolved.
- **`tools/resume_paused_claude_generation.py`** (row 2, new): the ledger's
  generation and continuation checks moved unchanged, renamed as public
  functions: `require_generation` (was `_generation`, with its private
  `_marker`, `_first_stamped` and `_restarts`), `writer_markers`, `clears`
  (was the ledger's `_clears`), `continuation_places` and
  `missing_predecessors`, with the three marker constants.
- **`tools/resume_paused_claude_ledger.py`** (row 3): imports those checks.
  `LedgerScope.boot_boundary` is now the `BootDecision`. `_bounding_instant`
  returns the instant only for a resolved decision, and `_read` puts every
  transcript in the lifecycle check when there is none, so an unresolved or
  pending boundary bounds nothing. `evaluate` adds a pending decision's
  reasons, or `boot-boundary-pending` when it names none. Schedule handling is
  unchanged: only the schedule's own deletion closes it. The module went from
  642 to 584 lines.
- **`tools/resume_paused_codex.py`** (row 4): unchanged.
- **Tests**: the profile tests cover resolved, unresolved (each predicate,
  alone and together, under a forward and a backward clock) and pending
  decisions and the recorded tolerance basis. The new generation test calls
  every moved function directly and holds the two `continuation_places`
  cases moved from the ordering tests. The new ledger boot test covers an
  older unmatched task under the shipped policy's unresolved boundary and its
  resolved true-boot control, complete older history with matched ends,
  unreadable, truncated and markerless older history, an incomplete
  enumeration, pending decisions with and without reasons, and a recurring
  firing, an assumed seven-day expiry and a host restart that close no
  schedule, with durable and session-only schedules. The existing ledger
  scopes use `resolved_boot(...)`. The Codex test shares its recheck cases as
  `RECHECK_CHANGES` and adds `test_clean_recheck_is_never_reused`. The shared
  builders gain `boot_semantics`, `resolved_boot` and `UNRESOLVED_BOOT`.
- **Validation plan**: the four rows are checked with the scope-resolved walk
  evidence; the Step 1 analysis, implemented-work, types, architecture,
  performance, coverage and feature-integrity sections are updated. Outside
  the Step 1 section, the document summary sentence and the Step 8 completion
  handoff sentence now say these rows closed, instead of open.
- **`.vscode/settings.json`**: adds `markerless`, the one word cSpell flagged
  in the validation plan.

During the first walk, check.bat's ruff fixed three style findings by itself
in the test builders, the ledger and the boot test; those fixes are kept and
staged.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and
`.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (exchange 2) (round 1)

Staged paths (14), all part of the reviewed scope:

- `tools/resume_paused_profiles.py`
- `tools/resume_paused_claude_generation.py` (new)
- `tools/resume_paused_claude_ledger.py`
- `tests/unit/tools/resume_paused_test_support.py`
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_generation/__init__.py` (new)
- `tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py` (new)
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py` (new)
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py`
- `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`
- `docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md`
- `.vscode/settings.json`

Root `a.commit`, five groups from least to most dependent; `commit-plan-check`
reports valid and ready with no diagnostic:

1. `fix(resume-paused): leave unproved boots unresolved`: the profile module,
   its test and the shared builders.
2. `refactor(resume-paused): move generation checks`: the new generation
   module, its test package and the ordering test that lost the moved cases.
   The ledger still holds its own copies at this commit; group 3 switches it
   to the new module.
3. `fix(resume-paused): limit history only on true boot`: the ledger and its
   three existing test files plus the new boot test.
4. `test(resume-paused): never reuse a clean recheck`: the Codex test.
5. `docs(resume-paused): record step 1 validation`: the validation plan and
   the project dictionary.

Each group was ordered so that its commit passes on its own: group 1 changes
the boot policy while the ledger still takes a bare instant, and group 3
moves the ledger and its scopes to `BootDecision` together.

### Writer response for step 1 resume-paused (exchange 2) (round 1)

Writer response:

No earlier feedback exists in this exchange. The previous Step 1 exchange
converged at round 6 with a commit-ready answer and was committed; this
exchange covers only the design Q28=A code follow-up that the round 6 verdict
explicitly left open. No disagreement is recorded.

Points the writer asks the reviewer to judge:

- An unresolved boundary makes every listed transcript of the checkout part of
  the lifecycle check, however old. On a real checkout with old killed
  sessions this keeps activation pending until a profile records validated
  boot semantics. That is the intended Q28=A consequence, not a regression.
- `boot_boundary` still reports invalid evidence as pending when no semantics
  are recorded, although the observation is then not used to bound history.
  The writer kept that as the more conservative choice.
- A schedule closes only on its own deletion. The plan also mentions a
  validated terminal record of the schedule itself; no such record shape is
  validated, so none closes a schedule. That is stricter than the plan's
  wording, never looser.
- The ledger now has 584 lines: under the 650 ceiling, above the 550
  safe-to-extend mark. Its next extension should split it first.

### Reviewer focus for step 1 resume-paused (exchange 2) (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1-exchange-2 -->

### LLM nature completion for reviewer (exchange 2)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.15.0.resume-paused.md`
- `.reviews/a.review-requested.code.v0.15.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-2 -->

## Round 1 by reviewer - Step 1 (exchange 2)

- Recorded: 2026-11-25T19:44:31+01:00
- Exchange: code/code/v0.15.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.15.0/plan.v0.15.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 2) (round 1)

Baseline index tree: cd3035f88fe46f5230d288efbd0ad1a36b9b3279

Assessed index tree: fec18e42a458692f050167318b06c8e16f10c3b9

### Implementation check for step 1 resume-paused (exchange 2) (round 1)

Result:

No. Step 1 has NOT been fully implemented.

An unresolved boot correctly brings every listed in-checkout transcript into the lifecycle check. Generation and continuation checks retain their behavior after extraction. The Codex tests recheck each changed binding after a successful recheck. The pending boot verdict and the schedule-age fixture need the two changes below.

Validation plan effects:

Updated only the Step 1 status, ledger checklist row, coverage assessment and missing-work list in `docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md`. The changes were attributable and staged.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 2) (round 1)

The requestor reported 8,348 tests passing, 100% coverage over `tools` and zero duration outliers. The reviewer inspected the implementation and tests statically. The two findings follow from the staged code and fixture timestamps.

### Resolved validation set and sources for step 1 resume-paused (exchange 2) (round 1)

`ghog day --full=speed --whole-suite` (project). The bound capture specifies the whole suite.

### Resolver drift and direction for step 1 resume-paused (exchange 2) (round 1)

The current project resolver returned the published command with the same project source. No drift.

### Repository state around validation for step 1 resume-paused (exchange 2) (round 1)

The request-time and baseline trees matched. The only path changed during assessment was the reviewed validation plan. The evidence helper attributed the Step 1 edits, and the baseline blob matched the index before staging. The umbrella comparison was inapplicable.

### Repair inventory for step 1 resume-paused (exchange 2) (round 1)

Repairs made:

- Polishing-only review metadata in `docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md`.

Paths staged:

- `.vscode/settings.json`
- `docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md`
- `tests/unit/tools/resume_paused_test_support.py`
- `tests/unit/tools/test_resume_paused_claude_generation/__init__.py`
- `tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py`
- `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`
- `tools/resume_paused_claude_generation.py`
- `tools/resume_paused_claude_ledger.py`
- `tools/resume_paused_profiles.py`

### Commit plan assessment for step 1 resume-paused (exchange 2) (round 1)

The independent checker returned `valid`, `ready=true`, five ordered groups, all 14 staged paths listed above and zero diagnostics on both runs. The groups cover boot policy, generation extraction, the ledger, Codex rechecks and validation documentation in dependency order. Refresh group 5’s description of closed rows when the ledger work is complete.

### Findings and boundaries for step 1 resume-paused (exchange 2) (round 1)

Unresolved findings:

- At `tools/resume_paused_claude_ledger.py` line 351, a pending boot carrying `Reason("boot-evidence-invalid", 0)` supplies a nonempty mapping and skips the fallback. Line 317 drops the zero count. With a clean bound transcript, the ledger returns `Absence.PROVED`. The current policy producer uses positive counts, but the typed ledger input permits zero and the pending state promises an unconditional block.
- At `test_resume_paused_claude_ledger_boot_tdd.py` lines 151–166, the expiry fixture dates the file modification eight days earlier. Its `CronCreate` result is still at `T0` plus 21 seconds and the bound turn closes at `T0` plus 41 seconds. A regression that inferred expiry from the recorded creation time could pass this test.

Boundary-crossing work: None.

### Writer instructions for step 1 resume-paused (exchange 2) (round 1)

Make the pending state sufficient to hold the ledger pending, including a regression with only a zero-count reason and otherwise clean history. Give the old transaction coherent record and file timestamps, put its `CronCreate` result more than seven days before a fixed later observation, and assert that the durable schedule still blocks absence. Refresh the Step 1 validation evidence and submit the revised staged tree.

### Decision rationale for step 1 resume-paused (exchange 2) (round 1)

Identity, staged attribution and mechanical grouping passed. Implementation completeness and behavioral test coverage remain open on the two findings. The live-host checklist remains separate under Q05=A.

### Final reviewer decision for step 1 resume-paused (exchange 2) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1-exchange-2 -->

## Round 2 by requestor - Step 1 (exchange 2)

- Recorded: 2026-11-25T20:08:06+01:00
- Exchange: code/code/v0.15.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.15.0/plan.v0.15.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 resume-paused (exchange 2) (round 2)

Umbrella draft: none
Implementation plan: docs/v0.15.0/plan.v0.15.0.resume-paused.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 resume-paused (exchange 2) (round 2)

request_index_tree: f2ce52f46b6ce5baabdb9ebb295ed5b0dd42081d
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.15.0/feature-request.v0.15.0.resume-paused.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(resume-paused): leave unproved boots unresolved
group 1 path: tools/resume_paused_profiles.py
group 1 path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
group 1 path: tests/unit/tools/resume_paused_test_support.py
group 2: refactor(resume-paused): move generation checks
group 2 path: tools/resume_paused_claude_generation.py
group 2 path: tests/unit/tools/test_resume_paused_claude_generation/__init__.py
group 2 path: tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py
group 2 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
group 3: fix(resume-paused): limit history only on true boot
group 3 path: tools/resume_paused_claude_ledger.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
group 3 path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py
group 4: test(resume-paused): never reuse a clean recheck
group 4 path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
group 5: docs(resume-paused): record step 1 validation
group 5 path: docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md
group 5 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md
staged path: tests/unit/tools/resume_paused_test_support.py
staged path: tests/unit/tools/test_resume_paused_claude_generation/__init__.py
staged path: tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py
staged path: tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py
staged path: tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py
staged path: tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
staged path: tools/resume_paused_claude_generation.py
staged path: tools/resume_paused_claude_ledger.py
staged path: tools/resume_paused_profiles.py
```

### Validation scope for step 1 resume-paused (exchange 2) (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 1 resume-paused (exchange 2) (round 2)

Yes. Step 1 has been fully implemented, including its design Q28=A code
follow-up and the two round 1 repairs: a pending boot holds the ledger
pending whatever counts its reasons carry, and the expiry fixture dates its
whole older transaction more than seven days before the bound turn. The four
"Open code follow-up for Step 1" rows of the validation plan are checked. The
Step 1 live validation checklist stays open by design (plan Q05=A): no host
profile is pinned, so no real pane receives input.

- **Tests**: `ghog single` on the ledger, profile and generation test targets
  passed (200 tests). The scope-resolved walk `ghog day --whole-suite` passed
  at 2026-11-25T19:55:47+01:00: check.bat green, 146 affected tests. The
  requestor validation set `ghog day --full=speed --whole-suite` passed on the
  staged tree at 2026-11-25T20:06:21+01:00: 8351 tests, fail 0, coverage 100,
  duration outliers 0, exclusions 0, proof speed. The three new tests are the
  zero-count and negative-count pending cases and the expiry fixture check.
- **Static checks**: check.bat (pyright, ty, ruff, radon, vulture, big files,
  Markdown) is green on the repaired code, with no automatic fix this round.
- **Coverage**: 100% over `tools`. The repaired loop in `evaluate` is reached
  with and without pending reasons and with positive, zero and negative
  counts.
- **Architecture**: unchanged since round 1. The ledger still only reads the
  boot decision's state and never decides boot semantics. It has 593 lines,
  under the 650 ceiling.
- **Performance**: the pending-reason update is one pass over a decision's
  few reasons. The dated fixtures change test data only.
- **Feature integrity**: no production caller builds a `LedgerScope`, so the
  stricter pending handling reaches tests only.
- **Markdown**: the validation plan passes markdown-check and cSpell.

### Implementation report for step 1 resume-paused (exchange 2) (round 2)

Round 2 of this exchange repairs the two round 1 findings. The rest of the
design Q28=A follow-up is unchanged since round 1: the boot policy in
`tools/resume_paused_profiles.py`, the generation module
`tools/resume_paused_claude_generation.py`, the unchanged
`tools/resume_paused_codex.py` with its never-reused clean recheck, and the
shared builders.

- **`tools/resume_paused_claude_ledger.py`** (finding 1): `evaluate` no longer
  copies a pending decision's reason counts as they are. For a pending boot it
  adds each reason with a count of at least one, or `boot-boundary-pending`
  when the decision names none. The pending state alone therefore keeps the
  decision pending: a zero or negative count can no longer produce an empty or
  dropped reason and a proved absence. The module and `evaluate` docstrings say
  so. The module now has 593 lines.
- **`test_resume_paused_claude_ledger_boot_tdd.py`** (findings 1 and 2):
  - The pending-boot case adds a zero-count and a negative-count
    `boot-evidence-invalid` reason with an otherwise clean bound transcript.
    Each expects that reason once. On the round 1 ledger, the zero-count case
    proves absence and the negative-count case reports a count of -1, so both
    fail.
  - The schedule scenarios now move their whole older transaction back with
    `aged`, so every recorded timestamp keeps its order. The file's
    modification time is its last record (`last_written`). The expiry scenario
    ends eight days before the bound turn. The recurring-firing and restart
    scenarios end one day before it, so each scenario still has a single cause.
  - `test_expiry_fixture_creates_its_schedule_more_than_seven_days_before_the_bound_turn`
    shows that the expiry case is not vacuous. Its `CronCreate` result
    predates the bound turn's close by more than seven days, and the older
    transaction ends before the resolved boot at second 30.
  - Both schedule tests, with durable and session-only schedules, run on these
    dated scenarios. A ledger that inferred expiry from the creation time would
    close the expiry scenario's schedule and fail the durable test.
- **Validation plan**: the reviewer's round 1 wording of the Step 1 analysis is
  kept. Its verdict is back to Yes, with one paragraph naming the two repairs.
  The missing-work list is removed, and the ledger row is checked again with
  the new cases. The walk evidence names the round 2 scope-resolved walk. The
  implemented-work, file-size and coverage entries are refreshed, and the
  coverage verdict is restored.
- **`a.commit`**: group 3's body names the pending-count repair and the dated
  fixtures. Group 5's body names the recorded round 1 repairs. Membership,
  order and subjects are unchanged.

Correction: round 1 gave the ledger as 584 lines. That figure was wrong: the
staged round 1 module had 589 lines. 584 is the size of the first ledger test
file.

Writer notes: `.reviews/a.resume-paused.step1.journal.md` and
`.reviews/a.resume-paused.step1.handoff.md`.

### Change summary for step 1 resume-paused (exchange 2) (round 2)

Staged paths (14), all part of the reviewed scope, unchanged in membership
since round 1:

- `tools/resume_paused_profiles.py`
- `tools/resume_paused_claude_generation.py` (new)
- `tools/resume_paused_claude_ledger.py` (changed in round 2)
- `tests/unit/tools/resume_paused_test_support.py`
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_generation/__init__.py` (new)
- `tests/unit/tools/test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py` (new)
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py`
  (new, changed in round 2)
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_evidence_tdd.py`
- `tests/unit/tools/test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_ordering_tdd.py`
- `tests/unit/tools/test_resume_paused_codex/test_resume_paused_codex_tdd.py`
- `docs/v0.15.0/plan.v0.15.0.resume-paused.validation.md` (changed by the
  reviewer in round 1 and by the writer in round 2)
- `.vscode/settings.json`

Root `a.commit` keeps its five groups, in the same order and with the same
members and subjects. `commit-plan-check` reports valid and ready with no
diagnostic:

1. `fix(resume-paused): leave unproved boots unresolved`: the profile module,
   its test and the shared builders.
2. `refactor(resume-paused): move generation checks`: the new generation
   module, its test package and the ordering test that lost the moved cases.
3. `fix(resume-paused): limit history only on true boot`: the ledger and its
   three existing test files plus the new boot test. Its body now names the
   pending-count repair and the dated schedule fixtures.
4. `test(resume-paused): never reuse a clean recheck`: the Codex test.
5. `docs(resume-paused): record step 1 validation`: the validation plan and
   the project dictionary. Its body now names the recorded round 1 repairs.

### Writer response for step 1 resume-paused (exchange 2) (round 2)

Writer response:

Both round 1 findings are accepted and repaired. No disagreement is recorded.

- Pending boot with a zero-count reason: accepted. The pending state now
  holds the ledger pending by itself. Each pending reason counts at least
  once, so neither a zero nor a negative count can prove absence. The
  regression covers both counts with an otherwise clean bound transcript.
- Expiry fixture dated only by its file: accepted. The whole older
  transaction, its `CronCreate` result included, is moved eight days back,
  and its file modification time matches its last record. A fixture check
  asserts the more-than-seven-day gap before the bound turn. The durable test
  still expects `schedule-unresolved` under both boundaries. The firing and
  restart scenarios got the same coherent dating, one day back.
- Reviewer's validation-plan edits: kept as covered wording. The writer
  reassessment then set the verdict back to Yes, removed the missing-work
  list, checked the ledger row again and restored the coverage verdict, with
  the round 2 evidence.
- Commit plan: group 3 and 5 descriptions are refreshed as asked. Grouping is
  unchanged.

Still for the reviewer to judge from round 1: an unresolved boundary keeps
activation pending on a checkout with old killed sessions until a profile
records validated boot semantics. Invalid evidence stays pending even without
recorded semantics. A schedule closes only on its own deletion. The ledger
now has 593 lines, under the 650 ceiling and above the 550 safe-to-extend
mark, so its next extension should split it first. Round 1 gave 584 lines,
which was wrong: the staged module had 589.

### Reviewer focus for step 1 resume-paused (exchange 2) (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2-exchange-2 -->

## Round 2 by reviewer - Step 1 (exchange 2)

- Recorded: 2026-11-25T20:12:12+01:00
- Exchange: code/code/v0.15.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.15.0/plan.v0.15.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 resume-paused (exchange 2) (round 2)

Baseline index tree: f2ce52f46b6ce5baabdb9ebb295ed5b0dd42081d

Assessed index tree: f2ce52f46b6ce5baabdb9ebb295ed5b0dd42081d

### Implementation check for step 1 resume-paused (exchange 2) (round 2)

Result:

Both round 1 findings are resolved. A pending boot contributes each reported reason at least once, with a fallback when the reason list is empty. The tests cover positive, zero, negative and absent counts against an otherwise clean transcript. The expiry fixture now dates the whole transaction eight days earlier and derives the modification time from its last record. An independent assertion checks that schedule creation predates the bound turn by more than seven days. The durable schedule remains unresolved under both tested boot boundaries.

Validation plan effects:

The writer updated the step 1 verdict and ledger evidence to record both repairs. Live host validation remains open and both host profiles remain unpinned.

### Pre-repair mandatory checks and coverage for step 1 resume-paused (exchange 2) (round 2)

The writer reported 8,351 passing tests, 100% coverage over tools, and zero duration outliers for the staged changes. Reviewer verification of the two fixes was static.

### Resolved validation set and sources for step 1 resume-paused (exchange 2) (round 2)

ghog day --full=speed --whole-suite (project validation command).

### Resolver drift and direction for step 1 resume-paused (exchange 2) (round 2)

The resolved validation command matches the request.

### Repository state around validation for step 1 resume-paused (exchange 2) (round 2)

The request, baseline, and assessed index all match f2ce52f46b6ce5baabdb9ebb295ed5b0dd42081d. The validation-state comparison returned acceptable=true with no changed paths.

### Repair inventory for step 1 resume-paused (exchange 2) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 resume-paused (exchange 2) (round 2)

The independent commit-plan check returned valid and ready=true for five ordered groups covering all 14 staged paths, with zero diagnostics. The updated descriptions of groups 3 and 5 cover the ledger repair, dated fixtures and validation evidence.

### Findings and boundaries for step 1 resume-paused (exchange 2) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 resume-paused (exchange 2) (round 2)

Submit the five assessed groups for the human commit decision.

### Decision rationale for step 1 resume-paused (exchange 2) (round 2)

Step 1 is commit-ready at the assessed index. Both requested regressions are covered, the validation plan records their resolution, and the staged grouping passes the independent check.

### Final reviewer decision for step 1 resume-paused (exchange 2) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2-exchange-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-11-25T20:14:45+01:00
- Exchange: code/code/v0.15.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.15.0/plan.v0.15.0.resume-paused.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
