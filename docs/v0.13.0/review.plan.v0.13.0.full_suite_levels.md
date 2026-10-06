# Specification review transcript for v0.13.0

- Exchange: specification/plan/v0.13.0/full_suite_levels
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-10-01T10:58:58+02:00
- Exchange: specification/plan/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan full_suite_levels (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Review round: 1

### Requestor assessment for plan full_suite_levels (round 1)

The implementation plan for v0.13.0 full_suite_levels is new: it turns the consolidated design into nine ordered steps (Step 0 cost gates, Step 1 pure models and the `commands.py` extraction, Step 2 the leveled walk and saved proof, Step 3 group declaration and listings, Step 4 group-scoped runs, Step 5 the effort scope and `pw scope`, Step 6 the bound review scope, Step 7 instructions and manuals, Step 8 the acceptance mapping). Each step lists its files as new or existing, its tests first, its classes and behavior, its completion checks, and a line-budget checkpoint against the 650-line ceiling.

Nineteen open questions (Q01 to Q19) cover the implementation choices that remain: step boundaries, the extraction target in `commands.py`, the timing of the rollout guard for full-suite callers, this effort's own gate walk, the evidence channel to `a.ghog.status`, the child environment for `COVERAGE_FILE`, the `Invocation.level` default, the placement of the capture model and of `paths.scope`, the source of the `pw progress` bound line, the coverage data reader, the test layout, the Step 0 gate strategy, the `status.py` split trigger, the instruction update timing, the acceptance placement, `pw scope` argument conflicts, capture removal paths, and whether the renderer's capture output is required.

I do not see a missing question for now. Each question offers two or three options with pros and cons and a recommended option A. No question re-opens a design decision; questions whose alternatives would depart from the design (for example, a capture stored inside the coordination record) were left out on purpose.

Please check in particular whether the plan carries every design acceptance case to a step (the round-3 design reviewer asked that the capture, evidence-error and coverage cases reach the relevant components), whether the line-budget figures and mandatory targets are justified, and whether any step mixes responsibilities in a way that would make a failing walk hard to attribute.

### Change summary for plan full_suite_levels (round 1)

Round 1 publishes the first version of the plan, `docs/v0.13.0/plan.v0.13.0.full_suite_levels.md`, with its validation skeleton `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`, and its open-questions section Q01 to Q19 placed through `oqm`.

The same write-plans pass added a short "File-based IO cost clarification" section to the feature request (before its requirement clarifications) and to the design (before its design decisions). Those sections restate IO bounds the design already implies (one marker read beside the digest walk, no group-file read for whole-suite runs, one capture read for `--scope-file`, atomic writes, metadata-only requirement reads) and add no decision.

### Writer response for plan full_suite_levels (round 1)

Writer response:

No earlier round exists, so there is no reviewer feedback to answer yet. The recommended answers are option A throughout; I am ready to revise any recommendation, add questions you find missing, or reword unclear options in the next round.

### Reviewer focus for plan full_suite_levels (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.13.0.full_suite_levels.md`
- `.reviews/a.review-requested.plan.v0.13.0.full_suite_levels.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-10-01T14:52:57+02:00
- Exchange: specification/plan/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan full_suite_levels round 1

The nine-step structure is workable, and the plan carries the important capture, coverage-data error, outside-source coverage, branch, and proof-cap cases into the responsible components. The pure-model step before the behavior switch is useful. The mandatory extraction targets have a stated purpose; the other line counts are appropriately advisory and must be recounted during implementation.

Three implementation gaps need another round. They concern rollout and evidence handling, not the settled level or group design.

- R1: Step 6 makes `--scope-capture-output` required and publishes `test_scope`, but the instructions that supply the output and pass it into publication are deferred to Step 7. Unlike the Step 2 change to a rendered default command, a new mandatory renderer argument cannot be discovered from a request that fails to render. Step 6's own code-review handoff therefore needs the minimum caller instruction changes in the same step. Step 6 also says to keep `test_code_review_request_tdd.py` unchanged, while Q19 explicitly says its existing calls must change.
- R2: Q18 names live-evidence resolution as a path that removes or archives the coordination record, but Step 6 covers only `complete` and `force_complete`. Since the capture is deliberately outside `fixed_paths`, its lifecycle cannot be assumed to follow existing record cleanup automatically. The plan needs an explicit treatment and test for that resolution path.
- R3: Step 6 describes marker evidence as valid for the current scope fingerprint and source digest, without applying the timing-fingerprint rule used by the walk. A saved `speed` marker can retain those two matches after only the floor or exclusions change. Rendering its raw proof would overstate the currently valid evidence. Carry the same effective-proof calculation into request evidence and test this case.

The capture boundary, exact-scope evidence, and group coverage behavior are otherwise represented well. The requested changes below make these remaining contracts executable and reviewable before implementation proceeds.

### Question verdicts for plan full_suite_levels round 1

All nineteen questions are relevant to implementation. Their options generally describe distinct costs and responsibilities. No settled design choice needs reopening. Q15 needs a rollout exception, Q18 needs its stated lifecycle completed, and the Step 6 text must agree with Q19. Add the missing evidence-validation question described after the table.

| Question | Reviewer choice and assessment |
| --- | --- |
| Q01 | A. Pure models followed by one behavior switch isolate proof errors without temporary marker semantics. B enlarges the change; C introduces disposable compatibility logic. |
| Q02 | A. Verdicts and progress have useful independent responsibilities and create headroom where later changes occur. B's dependency issue and C's broader churn justify retaining report extraction as a fallback. |
| Q03 | A. Move operational defaults with the behavior change. B weakens intermediate verification; C is optional for explanatory wording. This does not justify delaying the new required Step 6 invocation arguments. |
| Q04 | A. Preserving a whole-suite coverage gate is reasonable while changing the gate itself. B reduces this effort's verification; C adds the timing cost to each development walk. |
| Q05 | A. Typed outcomes with thin integer wrappers preserve existing callers and avoid parsing report text. B is a wider interface migration; C couples evidence to presentation. |
| Q06 | A. A narrowly scoped override is adequate under the stated single-threaded spawn model. Require restoration in `finally`, including factory exceptions, and tests for both an existing and an absent variable. B is explicit but broader; C needlessly complicates configuration. |
| Q07 | A. `None` plus one effective-level helper preserves command-specific defaults. B changes other commands; C expands call-site churn. |
| Q08 | A. One shared capture schema allows complete validation without a dependency from the protocol core to groundhog. B couples the layers; C cannot enforce completeness. |
| Q09 | A, with R2. A dedicated registered artifact module is reasonable; its removal and archival paths must be explicit because it is outside `fixed_paths`. B offers uniformity at a larger refactoring cost. |
| Q10 | A. A focused read for the bound line is acceptable under the stated existing routing precedent. Use the shared capture reader and error behavior so this does not become a second interpretation of validity. B adds projection work without a required behavior gain. |
| Q11 | A. The coverage API can assess resolved sources without another child. The stated exit-5 failure for incompatible data preserves correctness; B and C add process or report dependencies. |
| Q12 | A. New packages can follow the stated convention without moving existing tests. B divides the test roots; C continues a layout the plan says is no longer the convention. |
| Q13 | A. Spawn and traversal counts directly guard avoided work, with timeouts as a ceiling. B adds timing noise; C delays these contracts. |
| Q14 | A. Keep a concrete extraction available when growth reaches the chosen threshold. Clarify that 550 is this plan's extraction trigger, while 650 is the repository ceiling; neither advisory end counts nor the risk band alone are a repository hard failure. |
| Q15 | Amend A. Keep the broad manuals pass in Step 7, but move the minimum new renderer/publication/reviewer invocation instructions and their contract tests into Step 6. The current claim that all lag is harmless is false for required arguments. Full option B is unnecessary. |
| Q16 | A. A final cross-component package complements component tests and the explicit acceptance mapping. B adds environment-dependent subprocesses; C makes the completed workflow harder to assess as one flow. |
| Q17 | A. Refuse conflicting selectors early and name them. Cover both separated and equals forms. B produces an unusable command; C hides caller input. |
| Q18 | A, completed by R2. Match the capture's lifetime to its record, including the live-evidence resolution mentioned in the question. B knowingly leaves stale evidence; the present A enumeration is incomplete. |
| Q19 | A, completed by R1. Require a capture from new renderer calls, update all affected caller tests in Step 6, and supply the required arguments in that step's live workflow. B permits missing evidence by construction. |

Suggested replacement for Q15 option A: "Keep broad instruction and manual updates in Step 7; update the minimum invocation contracts in the step that introduces a required argument or required artifact, including renderer capture output, publication input, and reviewer scope consumption in Step 6."

Suggested completion of Q18 option A: "Handle the capture on every transition that removes or archives its coordination record, explicitly covering normal completion, forced completion, and live-evidence resolution; test the resulting artifact set."

Missing question: "How does request rendering determine the currently valid marker proof?" Choose the shared effective-proof rules: validate the marker's scope, membership fingerprint and source digest, and cap saved `speed` to `cov` on a timing mismatch. The alternative of checking only membership and source digest is simpler but can advertise stale duration evidence. This applies an existing proof rule; it does not add a new design choice.

### Requested changes for plan full_suite_levels round 1

Requested changes:

- R1 -- Make Step 6 usable before Step 7. Add the minimum updates to `instructions/code-review-requestor.md` and the shared publication instructions so the renderer receives `--scope-capture-output` and publication receives that output through `--scope-capture-file`. Bring the reviewer capture-consumption contract and affected instruction tests forward as needed for the same step's review. List the existing renderer test callers that must supply the newly required argument; remove the contradictory promise that `test_code_review_request_tdd.py` stays unchanged. Add a completion check demonstrating that the Step 6 request can render, publish its capture, and supply the bound scope to review using the instructions available at that step. Update Q15 and Q19 accordingly.
- R2 -- Complete capture lifecycle coverage. Q18 explicitly names live-evidence resolution, but Step 6 supplies no capture behavior or test for it. Identify that transition's owning file and decide its capture handling consistently with the record: remove a discarded live capture or archive it with retained record evidence, as appropriate to the existing resolution contract. Include it in Step 6's file list, behavior and tests, alongside normal and forced completion. If it delegates to one of those existing cleanup paths, document that call path and test it rather than assuming it. Expand Q18's enumeration; keeping the capture outside `fixed_paths` must not strand it.
- R3 -- Apply timing validity to rendered proof. Make `scope_evidence` use the same marker-validity and timing-cap rules as the walk instead of reporting the raw marker proof after only scope-fingerprint and digest checks. Add Step 6 tests in which a saved `speed` marker retains the same source digest and group fingerprint but the timing floor or exclusions change: rendered evidence must show at most `cov`, and a subsequent successful `speed` walk can restore `speed`. Cover both whole-suite and grouped evidence through the shared rule. Keep the validation plan and final acceptance mapping aligned with these tests.

### Writer instructions for plan full_suite_levels round 1

Revise the implementation plan and keep its validation skeleton aligned with the same step ownership. Do not consolidate yet.

Keep the nine-step structure and the accepted choices. Address R1 through R3 with named files, tests, and completion checks. Update the affected question answers and add the missing marker-evidence question. Retain Step 7 for the broad documentation pass while moving only the invocation contracts required for a functioning Step 6 review into Step 6.

In the next request, identify where each finding is covered. Minor wording follow-ups: make the plan-specific 550-line extraction trigger distinct from the 650-line ceiling, state exception-safe restoration for Q06, and cover both selector syntaxes for Q17.

### Final reviewer decision for plan full_suite_levels round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-10-01T20:43:53+02:00
- Exchange: specification/plan/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan full_suite_levels (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
Review round: 2

### Requestor assessment for plan full_suite_levels (round 2)

All three requested changes are accepted and applied; no disagreement remains. The nine-step structure and every accepted option A are kept. The open-questions section now holds Q01 to Q20: Q06, Q14, Q15, Q17, Q18 and Q19 were revised as requested, and Q20 is the missing question on how request rendering determines the currently valid marker proof.

I do not see another missing question. Q20 applies the existing exact-scope and timing-cap rule to request evidence; it adds no design choice. Q15 now states the rollout exception (minimum invocation contracts ship with the step that requires them), Q18 enumerates every transition that removes or archives the coordination record, and Q19 names every renderer caller that must pass the new argument.

Please check that the Step 6 instruction scope is the minimum needed for a working review of Step 6 itself, and that archiving the capture on `archive` (rather than removing it) matches the existing resolution contract.

### Change summary for plan full_suite_levels (round 2)

Changes since round 1, all in `docs/v0.13.0/plan.v0.13.0.full_suite_levels.md` unless named otherwise:

- R1 (Step 6 usable before Step 7): Step 6 now lists and updates `instructions/code-review-requestor.md` (renderer `--scope-capture-output` and `--scope-change-file`, publication `--scope-capture-file`), `instructions/review-requestor.md` (code-only `--scope-capture-file` input and `paths.scope`), `instructions/code-reviewer.md` and the reviewer evidence setup of `instructions/implementation-check.md` (`ghog affected --no-cov --scope-file=<paths.scope>`, missing, legacy or refused capture as missing evidence), with their four pinned instruction tests. It lists the renderer caller tests that must pass the new required argument (`test_code_review_request_tdd.py`, `test_code_review_request_commit_plan_tdd.py`, both requestor acceptance files, and `tests/acceptance/commit_plan_check/.../test_commit_plan_check_contracts_tdd.py`); the contradictory "keep `test_code_review_request_tdd.py` unchanged" promise is replaced by "argument edits only". `CodeReviewRoundInput.test_scope` defaults to `None` for direct constructions, so `test_code_reviewer_acceptance_tdd.py` stays unchanged. A Step 6 round-trip test (render, publish, `status`, then `ghog affected --no-cov --scope-file=<paths.scope>` running only the captured files) and matching completion checks were added. Step 7 now keeps only the broad pass (requestor `speed` policy wording and the rest of the design's list) and no longer lists the moved files and tests. Q15 and Q19 were updated.
- R2 (capture lifecycle): Step 6 names the three transitions of `tools/review_exchange_human.py` that remove or archive the coordination record: `complete` and `force_complete` remove the capture; `_resolve_live_evidence`, shared by `resolve` and `archive` through `resolve_escalation`, removes it when clearing and archives it (new `ArchiveKind.SCOPE`, registry archive name and regex accepting `scope.json`) when archiving, returning the archived path. `tools/review_exchange_store.py` stays unedited. Tests assert the artifact set after `complete`, `complete --force`, `resolve` and `archive`, and that the fresh round reports `bound_scope: missing`. Q18 now enumerates all of them.
- R3 (timing validity): Step 1 adds `proof.effective_saved` (scope, fingerprint and digest must match, then a timing mismatch caps saved `speed` at `cov`); Step 2 adds `snapshot.effective_proof`, used by the walk; Step 6's `scope_evidence` calls that same function. Step 6 tests cover a timing-only change rendering at most `cov` and a later `speed` walk restoring `speed`, for the whole suite and for a group. Step 8's review flows and the validation skeleton were aligned. New Q20 records the choice.
- Wording follow-ups: Step 2 and Step 4 split guidance and Q14 distinguish this plan's 550-line extraction trigger for `status.py` from the 650-line ceiling; Step 4 and Q06 state `finally` restoration of the spawn environment, tested for an existing and an absent variable and for a raising factory; Step 5 and Q17 cover both the equals and the separated selector forms.
- `docs/v0.13.0/plan.v0.13.0.full_suite_levels.validation.md`: Step 6 goal and expectations now include the shared proof rule, the capture lifecycle, the instruction contracts and the round trip; Step 7 goal now sits on top of Step 6's contracts.

### Writer response for plan full_suite_levels (round 2)

Writer response:

R1 is accepted: you are right that a required argument cannot lag its callers, and that the "keep `test_code_review_request_tdd.py` unchanged" promise contradicted Q19. I adopted your suggested wording for Q15 option A, moved only the invocation contracts (renderer, publication, reviewer evidence) into Step 6, and kept the requestor's policy wording for Step 7.

R2 is accepted. I checked the code: `resolve_escalation` calls `_resolve_live_evidence(archive=...)`, which archives or removes request, answer, tombstone and coordination. Since the existing contract archives every live evidence file on `archive` and clears them on `resolve`, the capture follows the same split: archived beside the others on `archive`, removed on `resolve`. Archiving needs one new archive kind, which the registry gains in Step 6; the store is not edited.

R3 is accepted. The timing cap now lives in one function shared by the walk and the renderer, so request evidence cannot claim more than the walk would accept.

The three wording follow-ups are applied (550 trigger versus 650 ceiling, `finally` restoration with both variable states, both selector syntaxes).

### Reviewer focus for plan full_suite_levels (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-10-01T20:48:58+02:00
- Exchange: specification/plan/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan full_suite_levels round 2

Convergence recommended for round 2 of the v0.13.0 full_suite_levels implementation plan. I read the complete current plan and its exact round 2 request. The three substantive round 1 findings are addressed, and I found no missing in-scope decision.

R1 is closed. Step 6 supplies the minimum live invocation contracts: the renderer capture output, the publication capture input, replacement scope-change input, and the reviewer's bound-capture evidence command. It updates their instruction contracts and affected renderer callers, preserves direct-construction compatibility, and includes a render/publish/status/affected round-trip test. This is sufficient to review Step 6 before the broader Step 7 documentation pass.

R2 is closed. Step 6 explicitly removes the capture on complete, forced completion and resolve, and archives it with the other evidence on archive. Inspection of tools/review_exchange_human.py confirms that resolve_escalation delegates the clear/archive split to `_resolve_live_evidence` before creating a fresh coordination record. Preserving the capture with archived evidence therefore follows the existing resolution contract. The planned dedicated helper, archive kind and registry naming changes fit that contract without editing the store. Artifact-set tests cover all four commands and the fresh round's missing bound scope.

R3 is closed. Steps 1, 2 and 6 share the effective-proof rule through proof.effective_saved and snapshot.effective_proof. The renderer cannot retain speed after a timing-only change when the walk would cap it at cov. Tests cover floor and exclusion changes for whole-suite and group scopes, then a successful speed walk restoring the evidence.

The environment restoration, extraction-trigger wording and both selector syntaxes are explicit. All twenty questions are relevant and sufficiently clear; their options distinguish implementation tradeoffs without reopening settled design choices. The only remaining edit is a summary sentence whose Step 7 attribution has not caught up with the detailed Step 6 text. This is wording-only. This assessment concerns the plan; it does not claim implementation validation or an independent review of the companion validation plan.

### Question verdicts for plan full_suite_levels round 2

All Q01-Q20 are in scope, present and sufficiently clear. None needs removal as redundant or replacement for missing consequences. I choose option A for each, for the following reasons.

- Q01: A. Separate pure-model proof from one behavior switch. B combines refactoring and behavior in a much larger step; C introduces temporary marker semantics.
- Q02: A. Extract verdicts and progress where later work grows them, preserving dependency direction. B requires further moves to avoid a cycle; C expands the preliminary refactor unnecessarily.
- Q03: A. Move executable full-suite callers with the Step 2 switch. B weakens intermediate review and release validation; C also removes harmless prose lag but requires additional document churn. The rendered command supplies the operative validation contract.
- Q04: A. Keep this effort's coverage gate consistent through the CLI transition. B reduces the evidence for a runner rewrite; C imposes the additional timing pass on every step.
- Q05: A. Typed outcome functions with integer wrappers preserve callers and provide status evidence. B changes many callers; C couples status to display text.
- Q06: A. Under the stated single-threaded execution model, the spawn-local environment override keeps the factory seam stable. Finally restoration and tests for present/absent variables and raising factories bound the side effect. B changes every factory; C adds a generated configuration that must preserve project settings.
- Q07: A. None resolves to the subcommand default for existing direct constructions. B changes check/affected/single restart behavior; C requires unnecessary caller edits.
- Q08: A. A shared tools-level capture schema gives every producer and consumer one validator. B couples the exchange to groundhog; C cannot enforce capture completeness.
- Q09: A. Register the capture outside fixed_paths with dedicated IO. B broadens the artifact-model refactor. A is complete because Q18 now explicitly handles lifecycle transitions.
- Q10: A. Read the record and capture in the scope helper, following the existing pw routing approach and using the shared validator. B expands an at-limit status projection without changing the required behavior.
- Q11: A. The coverage API provides exact file and branch evidence, and incompatible or unreadable data fails as an evidence error. B adds a process and text parsing; C adds a report-generation dependency. The compatibility consequence is explicit.
- Q12: A. New one-level packages satisfy the naming convention while retaining discoverability beside existing tests. B creates another root; C disregards the convention.
- Q13: A. Spawn and walk counts directly test avoided work, with bounded execution and strict expected failures until the owning step. B is less deterministic; C leaves the cost contract unguarded initially.
- Q14: A. Use the plan's chosen 550-line extraction trigger while retaining 650 as the repository ceiling. B extracts before the need is known; C retains the mixed responsibilities until the ceiling.
- Q15: A. Ship required invocation contracts with their owning step and leave the broad manual pass to Step 7. B is a viable but more repetitive rollout. Step 6 now contains the complete minimum requestor/reviewer invocation chain.
- Q16: A. A final in-process cross-component package and explicit design-row mapping complement the per-step tests. B adds launcher/environment cost; C lacks a final check after all components and instruction contracts exist.
- Q17: A. Reject preexisting selectors in both syntaxes before printing a workflow command. B defers a predictable failure; C silently replaces the caller's argument.
- Q18: A. Remove captures on complete, forced completion and resolve; archive them with retained evidence on archive. B and C omit actual record-exit paths. The selected behavior matches the current _resolve_live_evidence contract.
- Q19: A. Require the capture output for new renderer CLI calls and update every affected caller and live instruction in Step 6. B permits new requests with missing scope evidence. Optional model defaults correctly preserve direct-construction and legacy compatibility.
- Q20: A. Use the walk's shared effective-proof function, including the timing cap. B overstates speed after timing changes; C delegates a mechanical validity rule to reviewers. Whole-suite and grouped regression tests establish the intended behavior.

No additional question is needed. Keep the current option A answers; apply only the covered wording correction.

### Convergence evidence for plan full_suite_levels round 2

Covered wording:

At plan lines 321-323, replace the test-tree bullet ending "pinned phrases follow the Step 7 edits" with:

- Instruction tests: Step 6 updates the invocation-contract pins in test_code_review_requestor_instruction, test_code_reviewer_instruction, test_implementation_check_reviewer_mode and test_review_requestor_instruction. Step 7 updates the broader requestor policy pins; test_instruction_structure stays green without edits.

The detailed step files, tests and completion criteria already establish this sequence. This replacement only aligns the earlier summary with them.

Convergence rationale:

Every substantive round 1 finding is resolved in the current plan. The minimum Step 6 invocation contracts make its own review operational; every coordination-record exit handles the bound capture consistently with the existing clear/archive semantics; and request proof uses the same timing-aware validity rule as the walk. Q01-Q20 provide clear, distinct alternatives and justified answers, with no missing in-scope decision. One stale overview sentence needs wording alignment only. Recommend convergence and submission to the human consolidation gate.

### Writer instructions for plan full_suite_levels round 2

Apply the covered wording correction to the earlier test-tree summary so it agrees with Steps 6 and 7. Keep the nine-step structure, Q01-Q20 answers, Step 6 invocation-contract updates, capture lifecycle, shared proof rule and regression cases as written. No new substantive revision or automatic review round is requested. Convergence is advisory; consolidation remains subject to the exchange's human decision.

### Final reviewer decision for plan full_suite_levels round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-10-01T21:59:40+02:00
- Exchange: specification/plan/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/plan.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
