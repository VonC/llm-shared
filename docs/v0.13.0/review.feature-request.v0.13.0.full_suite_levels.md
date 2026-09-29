# Specification review transcript for v0.13.0

- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-29T17:37:38+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request full_suite_levels (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
Review round: 1

### Requestor assessment for feature-request full_suite_levels (round 1)

The feature request `docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md` describes three full-suite levels (`pass`, `cov`, `speed`) for the `ghog day` walk, a default walk that stops after the affected tests, and the phases that ask for each level. It carries nine open questions (Q01 to Q09), each with options, pros and cons, a recommended option, and an answer line.

Questions believed complete: what `pass` runs (Q01, raised by the human, who asked whether `pass` should skip the test suite entirely), the scope of `GHOG_FULL` (Q02), level upgrades on unchanged sources (Q03), the test-only classification for the requestor speed pass (Q04), non-speed failures found by that pass (Q05), the scope of the review round it starts (Q06), `ghog exclude` at convergence (Q07), how a walk reports its level (Q08), and the speed pass without review mode (Q09).

Please check whether a question is missing, whether any option set or recommendation is weak or wrong, and whether any question drifts into design or implementation detail, which a feature request must not carry. No reviewer wording suggestion has been applied yet: this is round 1.

### Change summary for feature-request full_suite_levels (round 1)

Round 1: the document is new. It was written from the draft `docs/v0.13.0/draft.v0.13.0.full_suite_levels.md`, then nine open questions were appended through `oqm`. A tenth question (level of a direct `ghog full` call inside the groundhog loop) was dropped before publication, because the loop never calls `ghog full` directly and gap 6 already settles the human call.

### Writer response for feature-request full_suite_levels (round 1)

Writer response:

No earlier feedback to answer: this is round 1. The human already agreed to the level names, the parameter and variable names, the level-aware snapshot, the `speed` default of a direct `ghog full`, and the extension of the convergence rule for production-code speed fixes. Those points are settled and should not be reopened as questions.

### Reviewer focus for feature-request full_suite_levels (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.feature-request.v0.13.0.full_suite_levels.md`
- `.reviews/a.review-requested.feature-request.v0.13.0.full_suite_levels.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-29T17:52:15+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request full_suite_levels round 1

Changes requested. The three levels and the development/review/release split are coherent. I agree with the direction of all nine recommendations except Q04's proposed classifier, which does not provide its claimed conservative guarantee. The remaining issues concern observable behavior, not a request to choose implementation structures.

1. Q04 can bypass review for production changes. A project collection root could include application code (for example, a root of `.`), and a filename alone does not establish exclusive test use. Under option A, every file below such a root qualifies as test-side. Its claim that the only classification error triggers extra review is therefore false. Keep the test-only exception, but require positive evidence of exclusive test use and route mixed-use or uncertain changes to another review. Treat Q07's narrow exclusion exception separately from this file classification.
2. The direct command's environment behavior is missing. Gap 6 gives `ghog full` the same level and a `speed` default; Q02 consistently speaks about walks and development calls. With `GHOG_FULL=cov`, it is not explicit whether plain `ghog full` means `cov` or `speed`. Settle that case without reopening the agreed level names, parameter, variable, or unset-environment default.
3. Cached validation needs an unambiguous evidence contract. Gap 5 retains the highest proved level, Q03 reuses earlier steps, and Q08 proposes a single level key. After a successful `speed` walk, an unchanged default walk can be a noop: the requested level is none, the saved proof is speed, and no suite ran in this invocation. These are distinct facts. Also settle whether a pre-feature snapshot without a level can satisfy a new requested level. Otherwise the first walk after upgrade has no stated acceptance behavior.

The request and current document agree on scope and the nine questions. No material request/document drift was found. The request's reference to a project-root answer location is obsolete coordination wording; publication must use the artifact-home paths returned by the shared exchange, as required by the canonical workflow. This does not require a specification change.

### Question verdicts for feature-request full_suite_levels round 1

Q01 — Relevant, clear, and materially distinct options. Choose A: run the entire suite without coverage collection or a duration verdict. B duplicates the default walk; C adds optional measurement that this level does not need. Keep this as behavior, leaving measurement implementation to design. Suggested answer: "`pass` executes the entire test suite and requires its tests to pass without a suite crash. It does not collect coverage or enforce duration thresholds; any recorded durations are informational."

Q02 — Relevant and distinct options. Choose A for every `ghog day` caller, including development skills. State that the lightweight default applies only when neither a parameter nor an environment level is supplied; current gap 1's "with no level requested" should retain that meaning. Add the direct-command case described below. Reporting a selected environment level is useful; the source of selection can be described without prescribing a data structure.

Q03 — Relevant behavioral choice, not merely an implementation detail: users can observe whether expensive checks rerun. Choose A when an unchanged snapshot actually proves the preliminary checks passed. The reasoning from the existing noop guarantee is sound. Suggested answer: "An upgrade may reuse successful check and affected-test results for the same validated snapshot, runs the missing full-suite objective, and identifies the reused results in its report." Do not suggest that a green lower-level full run proves a higher level.

Q04 — Necessary question, but do not accept A as written. The options are distinct, yet none states the required conservative boundary correctly. A pytest collection root or filename is not proof that every matched file serves tests exclusively. C's unrestricted judgment also makes the bypass hard to verify. Replace A with a reproducible classification supported by explicit test-only scope, with mixed-use and unclassified paths requiring review. Choose that revised A. Suggested answer: "The post-review delta qualifies for the test-only exception only when every changed file is established to serve tests exclusively. Shared runtime code, configuration or tooling that can affect production behavior, and uncertain files require another review. Path names and collection roots alone are insufficient evidence. Preserve the narrow duration-exclusion exception in Q07 separately." Specify this boundary in the requirement; defer recognition algorithms and configuration representation to design.

Q05 — Relevant missing failure branch and distinct options. Choose A, subject to the corrected Q04 boundary. It is reasonable to use the changed content rather than the original failure category to decide whether another review is required. Suggested answer: "For repairable test, coverage, crash, or duration failures, restore the selected speed objective, preserve test coverage and assertions, and classify the complete repair delta using Q04 and Q07 before the gate. Existing operational stop and interruption rules still apply." This does not authorize weakening checks to obtain exit 0 or endlessly retrying setup failures.

Q06 — Relevant, distinct options. Choose A: ordinary review of the same implementation step, with the additional changes explicit and speed validation repeated at the next convergence. This is within scope as workflow behavior. Replace "the loop ends by itself" and "terminates naturally" with the conditional statement that an unchanged, already successful speed result can be reused; further reviewer repairs can legitimately require another validation or round.

Q07 — Relevant exceptional case and distinct options. Choose A with the existing attempted-fix requirement retained. Require the gate evidence to state the exact excluded call, measured time, attempted improvement and reason for accepting the duration. Identify this as an explicit exception to Q04, since an exclusion configuration change can be outside test-only paths. The exception must cover duration acceptance only, not unrelated configuration changes or removal of correctness/coverage checks. This makes its boundary reviewable without adding a new human gate.

Q08 — Necessary and distinct options. Choose A with clearer evidence semantics. Describe the selected objective, the strongest valid saved proof, and whether steps ran or were reused. A single ambiguous `full` value cannot describe all three. Example: after a green speed walk, an unchanged default noop must not claim a fresh full run or hide that the saved proof is stronger. Leave field names and encoding to design. Replace "existing parsers keep working" with a compatibility requirement for supported consumers; adding a key is not by itself proof of parser compatibility. Detached execution must preserve the effective level selected for that invocation.

Q09 — Relevant final-phase behavior with distinct options. Choose A. It closes the speed-validation gap without changing the agreed release `cov` gate. State explicitly that, with review mode disabled, changes outside the permitted test-only/exclusion scope return through implementation-check and speed validation before the ordinary human gate. No review exchange should be manufactured for that path. This is a scope extension proposed by the document's existing question, not a reason to reopen settled naming or levels.

Missing decision A — Does `GHOG_FULL` select the level of direct `ghog full` calls? Choose the common precedence rule: explicit parameter, then environment, then the command default. Its advantage is one predictable selector; its cost is that a shell setting changes direct calls too. The alternative is to limit the variable to day walks, preserving an unconditional direct-call speed default but giving the two commands different selection rules. Recommended wording: "Both commands resolve an explicit level before `GHOG_FULL`. When neither is set, `ghog day` has no full step and `ghog full` uses speed." Include examples for unset environment, an environment level, and an explicit override.

Missing decision B — What may an existing saved result with no level prove after this change? Choose to rerun once rather than silently assigning a level. This costs one validation but establishes explicit, inspectable evidence. An alternative may reuse a positively identified legacy all-gates-green result as speed, avoiding that run but requiring an explicit compatibility guarantee. Do not conflate a proven legacy result with arbitrary missing or invalid metadata. Recommended wording: "A saved result that cannot establish its achieved level must not satisfy a requested level. The next successful walk records explicit evidence." Settle this observable behavior now; leave format and migration mechanics to design.

### Requested changes for feature-request full_suite_levels round 1

Requested changes:

Changes requested because the current Q04 rule can incorrectly exempt production changes from review, and selector/cache behavior still has observable undecided cases. These are more than wording edits.

The next round should demonstrate:

- A collection root that includes production files does not make those files eligible for the test-only exception; ambiguous or shared files require review.
- A duration exclusion has a narrowly described exception with supporting evidence, while other configuration changes follow the conservative rule.
- `ghog full` with `GHOG_FULL=cov`, and the same call with an explicit speed override, each have one stated expected level.
- An unchanged default walk after a green speed walk reports reuse honestly, without confusing this invocation's work with the saved stronger proof.
- A snapshot without an established level has one defined reuse/revalidation outcome.

No consolidation or human convergence recommendation is warranted until these decisions and cross-question corrections are settled.

### Writer instructions for feature-request full_suite_levels round 1

Revise the open questions and their proposed answers, then publish another specification-review round. Do not consolidate yet.

1. Replace Q04's classifier and its false fail-safe rationale with the conservative test-only boundary in this answer. Apply it consistently to Q05, Q06, Q09 and gap 11. Make Q07's duration-exclusion exception explicit and narrow.
2. Add or extend a question to settle direct `ghog full` environment precedence, preserving its agreed speed default when no selector is supplied. Align gap 6 and Q02.
3. Extend Q08 to distinguish requested objective, reused proof and actual execution, including the stronger-snapshot/lower-request case and detached execution. Specify consumer compatibility as a requirement, not an unverified assertion.
4. Add the saved-result compatibility decision for existing snapshots with no level. State the chosen observable behavior without prescribing serialization or migration algorithms.
5. Apply the bounded wording corrections to Q05 and Q06. Keep implementation mechanics out of this feature request: in particular, replace Q04's parser/filename algorithm and Q08's concrete report-key prescription with acceptance behavior where they are currently normative.

Keep the accepted level names, selector names, level-aware snapshot, unset-selector direct speed default and production-change review extension. The nine existing topics are in scope; none needs removal as redundant. The two missing decisions may be folded into Q02/Q08 if that keeps the document clearer. Identify the amended answers and any disagreement in the next request.

### Final reviewer decision for feature-request full_suite_levels round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-29T17:55:52+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request full_suite_levels (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
Review round: 2

### Requestor assessment for feature-request full_suite_levels (round 2)

All five round-1 writer instructions are applied. The document now carries ten open questions (Q01 to Q10). The conservative test-only boundary of Q04 is applied consistently to Q05, Q06, Q09 and gap 11, and Q07 is an explicit, narrow exception to it. Direct `ghog full` selection is folded into Q02 with the three requested examples, Q08 separates requested objective, saved proof and actual execution, and the new Q10 settles legacy snapshots with no level.

No question is believed missing. Please confirm the revised boundaries and whether any remaining text is still normative about implementation mechanics.

### Change summary for feature-request full_suite_levels (round 2)

- Q01: answer reworded with the suggested behavior (whole suite, no coverage collection, no duration threshold, informational durations).
- Q02: retitled "Level selection for `ghog day` and direct `ghog full`"; one precedence rule (parameter, then `GHOG_FULL`, then command default) with examples for unset, environment, and explicit override; new option B limits the variable to `ghog day`.
- Q03: answer reworded; states that a green lower-level full run never proves a higher level.
- Q04: option A replaced by the positive-evidence boundary (every changed file established to serve tests exclusively; shared, configuration, tooling or uncertain files require review; path names and collection roots are insufficient); the former classifier is now option B with the collection-root bypass as its con; the false fail-safe claim is removed.
- Q05: answer reworded: restore the `speed` objective, preserve coverage and assertions, classify the complete repair delta with Q04 and Q07; operational stop rules still apply.
- Q06: "ends by itself" and "terminates naturally" replaced by the conditional reuse of an unchanged successful result.
- Q07: option A is an explicit exception to Q04, limited to duration acceptance, with evidence naming the call, measured time, attempted improvement and reason.
- Q08: retitled "What a walk reports about its objective and evidence"; covers selected objective and source, strongest saved proof, ran or reused steps, the noop after a stronger proof, and detached walks; field names left to design; parser compatibility stated as a requirement to verify.
- Q09: states that changes outside the test-only and exclusion scope return through implementation-check and `speed` validation, with no review exchange created.
- Q10 (new): a saved result that cannot establish its level satisfies no requested level.
- Gaps 1, 2, 3, 6 and 11 aligned: default walk only when neither selector is set, settled selector names no longer marked "recommended", informational durations, `ghog full` uses the same selectors, and gap 11 uses the Q04/Q05/Q07 boundary.

### Writer response for feature-request full_suite_levels (round 2)

Writer response:

All round-1 findings are accepted, with no disagreement. The Q04 fail-safe claim was indeed false: a collection root such as the project root would have exempted production code from review. Missing decision A is folded into Q02 and missing decision B is added as Q10, which keeps each question focused. The obsolete project-root answer location in the request template is noted as a coordination wording issue outside this specification.

### Reviewer focus for feature-request full_suite_levels (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-29T18:40:51+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request full_suite_levels round 2

Convergence recommended. I assessed the complete current specification against the validated round-2 request. The reported amendments are present, and no material request/document drift remains.

The substantive findings are resolved. Q04 now requires positive evidence of exclusive test use and sends shared or uncertain changes to review. Q05 applies that boundary to the complete repair delta without weakening checks; Q07 establishes a separate, narrow duration-exclusion exception. Q02 explicitly applies parameter/environment/default precedence to both commands, with examples. Q08 separates this invocation's objective and execution from the strongest valid saved proof, including detached execution and stronger-proof noops. Q10 prevents reuse of evidence whose achieved level cannot be established.

I agree with all ten proposed option-A answers. No additional in-scope decision is missing. The remaining edits below clarify statements already settled by those answers; they require no new behavioral choice or review round.

The requirement appropriately leaves test-only recognition, report fields and encoding, and snapshot compatibility mechanics to design. The retained command names, level names, precedence, exit behavior and workflow boundaries are observable requirements or already confirmed constraints, not newly imposed implementation mechanics. The code references identify affected areas without dictating their implementation.

This is a specification assessment, not implementation or test validation. The recommendation does not authorize consolidation or any commit.

### Question verdicts for feature-request full_suite_levels round 2

Q01 — Agree with A. This relevant question distinguishes a whole-suite passing objective from the affected-only default, and its options describe materially different work. The answer clearly excludes coverage collection and duration enforcement while allowing informational timings. No decision remains; align gap 3's tentative wording with the answer.

Q02 — Agree with A. The expanded question now covers both development inheritance and direct `ghog full`. Its alternatives expose the consequences of command-specific or human-only environment behavior, while the selected common precedence is explicit. The unset, environment and explicit-override examples settle the missing direct-command case. No further selector question is needed.

Q03 — Agree with A. Reusing proved preliminary checks for the same validated snapshot is consistent with the existing reuse principle. The option to rerun everything is distinct and its cost is stated. The text now explicitly denies that a lower-level full result proves a higher level and requires honest reporting of reuse. This is sufficient behavioral scope for the requirement.

Q04 — Agree with revised A. The options distinguish evidence-based classification, the unsafe path heuristic, and unrestricted judgment. The answer rejects the root/filename bypass and routes uncertainty conservatively while leaving the recognition method to design. The claim that every possible classification error is safe is still too absolute; replace it with the uncertainty rule already established by the answer, as covered in the wording input. This is a precision edit, not another decision.

Q05 — Agree with A. The alternatives materially change automation and review routing. The selected rule handles repairable failures consistently, preserves assertions and coverage, classifies the complete repair delta, and retains operational stopping rules. No additional failure-category decision remains.

Q06 — Agree with A. An ordinary replacement review of the same step retains context and avoids a separate review type. The unconditional termination claim is gone, and reuse is now conditional on a successful unchanged result. The next convergence repeats speed validation as required. Its description should mention the Q07 exception alongside Q04 so its shorthand cannot obscure the already settled boundary.

Q07 — Agree with A. Its alternatives differ on who may accept an exclusion and whether another review is required. The selected exception now requires an attempted improvement, the measured call and duration, and a reason visible at the human gate. It explicitly excludes unrelated configuration changes and removal of correctness or coverage checks. This resolves its relationship with Q04.

Q08 — Agree with A. It now states the selected objective and source, strongest valid saved proof, and execution/reuse information, including the default noop backed by speed evidence. Compatibility is a requirement to verify rather than an unsupported assertion. Field names and encoding are correctly deferred. No missing reporting decision remains.

Q09 — Agree with A. The alternatives distinguish per-commit validation, optional speed checking, and release-time validation. The selected path retains speed validation before the ordinary human gate, routes other changes back through implementation-check, and expressly creates no review exchange. It remains consistent with the agreed release cov gate.

Q10 — Agree with A. The two options state the cost of revalidation versus legacy compatibility, and the chosen conservative rule gives a defined outcome for level-less or invalid evidence. It is sufficient to require that such evidence cannot satisfy a requested objective and that successful validation records explicit evidence. Clarify that revalidation performs the selected objective, which may be the lightweight default; it does not unconditionally force a full-suite run.

All ten questions are relevant and sufficiently distinct; none needs removal as redundant or out of scope. No new open question is requested.

### Convergence evidence for feature-request full_suite_levels round 2

Covered wording:

1. In gap 3, replace "The recommended direction for pass is to skip the coverage measure, since nothing reads it" with: "At `pass`, the full suite runs without coverage collection or duration enforcement; any recorded durations are informational." This makes the main requirement agree with Q01's settled answer.

2. In Q04, replace the option-A pro "every classification error falls on the side of one more review" with: "when exclusive test use cannot be established, the change requires another review." Replace "Requiring positive evidence of exclusive test use gives that guarantee" with: "Positive evidence is required to use the exception; uncertainty must lead to another review." A conservative rule handles uncertainty without claiming that an implementation cannot misclassify evidence.

3. In Q06's description, replace "when a speed repair falls outside the test-only exception" with: "when a repair made during speed validation falls outside both the test-only boundary (Q04) and the narrow duration-exclusion exception (Q07)." This restates the existing joint boundary without changing it.

4. In Q10's cost and rationale, describe "the first requested walk after upgrade must revalidate its selected objective instead of reusing evidence with no established level." The selected objective may be the lightweight default; later level upgrades still follow Q03. Avoid implying that upgrade alone forces a speed run or that every project's total cost is exactly one full-suite run.

5. When aligning gap 1 with Q08, state: "A default invocation does not itself establish fresh coverage or speed proof; its report separately identifies any stronger valid saved proof it reuses." This preserves the intended distinction between work performed now and earlier evidence.

These edits resolve shorthand or tentative wording using decisions already present in the current document. They introduce no new acceptance behavior.

Convergence rationale:

Every substantive round-1 concern is addressed by the current specification: the review-skipping boundary is conservative, duration exclusions have a narrow explicit exception, direct-command environment precedence is defined, cached proof is distinguished from execution, and level-less evidence has a stated outcome. The complete repair and no-review workflows remain consistent with these decisions.

All ten option-A answers can be carried into a coherent requirement without an additional decision. No new question, substantive disagreement, missing evidence for specification acceptance, or cross-document correction is needed. Remaining changes are the wording-only alignments provided with this answer.

Recommend convergence and consolidation subject to the existing human choice. The reviewer leaves that choice and all document consolidation to the authorized requestor workflow.

### Writer instructions for feature-request full_suite_levels round 2

Present this convergence recommendation through the existing human gate. Do not consolidate merely because the reviewer recommends it.

If the human authorizes Consolidate, incorporate the ten agreed answers and the covered wording into the consolidated requirement. Keep the existing level names, selector names, default behavior and workflow boundaries. Carry Q09's non-review path and Q10's saved-evidence rule into the resulting requirements rather than losing them when removing the question section.

The covered wording is editorial alignment with settled answers. No further automated round is needed solely for these edits. A new substantive change or disagreement would still require the normal review route.

The request template's project-root answer wording remains a coordination issue outside this reviewed document. This answer is published through the shared exchange at its returned artifact-home path.

### Final reviewer decision for feature-request full_suite_levels round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-29T19:00:27+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: Add the LLM-facing closing instructions as requirements. Rewrite gap 4 as a table of the required closing instruction for each level (default with the full suite skipped, `pass`, `cov`, `speed`) and each outcome (green, failure, coverage gap, duration outliers). A skipped full run must say the skip is expected, that the walk objective (check plus affected tests) is met, that the full suite must not be run unless the calling instruction asks for a level, and how to ask for one (`ghog day --full=pass|cov|speed`). Add a rule that every printed restart line names the level of the walk it restarts (for example `ghog day --full=cov`), so an LLM following it literally never drops back to the default walk.

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-09-29T19:02:05+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request full_suite_levels (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
Review round: 3

### Requestor assessment for feature-request full_suite_levels (round 3)

Round 2 converged, and the human chose another round with guidance: the specification did not state what a walk tells the LLM at its end, for each level and outcome, nor what a skipped full run says. Those closing instructions are now requirements. Gap 4 points to a new section, "Closing instructions for the LLM by level", holding one required instruction per level and outcome, and adds the rule that every printed restart line names the level of the walk it restarts. Gap 13 now covers those instructions in the documentation and tests.

The ten open questions and their answers are unchanged since round 2, apart from the covered wording edits. Please check that the table is complete (levels, outcomes, noop), consistent with Q01, Q03, Q05, Q07 and Q08, and that it states behavior without fixing message wording, which is left to the design.

### Change summary for feature-request full_suite_levels (round 3)

- Gap 4 rewritten as "Closing instructions by level": the report ends with the instruction of the new table, asks only for the work its level covers, and every printed restart line names the level of the walk it restarts (`ghog day --full=<level>`); a default walk restarts with plain `ghog day`.
- New section "Closing instructions for the LLM by level": a table for default, `pass`, `cov` and `speed` against green, check or affected failure, full-suite failure, suite crash, coverage gap and duration outliers. The default green line says the skip is expected, the walk objective is met, the full suite must not be run unless the calling instruction asks for a level, and how to ask for one. A noop follows the green instruction of its requested level and states the reused proof.
- Gap 13: documentation and tests also cover the closing instruction of every level and outcome, restart lines included.
- The five round-2 covered wording edits are present (gap 3, gap 1, Q04, Q06, Q10).

### Human guidance and writer response for feature-request full_suite_levels (round 3)

Human guidance:

Add the LLM-facing closing instructions as requirements. Rewrite gap 4 as a table of the required closing instruction for each level (default with the full suite skipped, `pass`, `cov`, `speed`) and each outcome (green, failure, coverage gap, duration outliers). A skipped full run must say the skip is expected, that the walk objective (check plus affected tests) is met, that the full suite must not be run unless the calling instruction asks for a level, and how to ask for one (`ghog day --full=pass|cov|speed`). Add a rule that every printed restart line names the level of the walk it restarts (for example `ghog day --full=cov`), so an LLM following it literally never drops back to the default walk.

Writer response:

The five round-2 covered wording edits were applied before the gate and are listed in the change summary. At the gate, the human asked whether the specification defines the instructions printed at the end of a full run for each level, and whether a skipped full run tells the LLM so. It did only negatively (gap 4 listed what not to ask for) and gap 1 only stated the skip. In particular, today's restart lines name plain `ghog day`, which an LLM following them literally would run at the default level, losing the objective it was proving. The new section and the restart rule close both gaps. No disagreement with the round-2 answer.

### Reviewer focus for feature-request full_suite_levels (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-09-29T19:08:10+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request full_suite_levels round 3

Convergence recommended. The complete current specification and the validated round-3 request agree. The human-requested closing instructions are now requirements: the default success case explains the intentional skip, each full-suite level identifies its objective and corrective work, restart commands retain the selected level, and noops identify reused evidence. Gap 13 includes these instructions and restart lines in documentation and acceptance coverage.

The new table is consistent in direction with the ten settled answers. Its ordinary success, test-failure, crash, coverage and duration cases cover the requested behavior. Existing operational stop and interruption rules remain applicable through Q05; the table must not turn those stops into automatic retries.

Only wording alignment remains. In particular, the rows labelled "any level" should explicitly name the three full-suite levels to avoid overlapping the default row; exclusion wording should repeat the already required attempted fix; and green/noop wording should distinguish what the requested level requires from any stronger saved proof. The exact replacements are supplied separately. These edits restate settled behavior and introduce no new decision.

All ten option-A answers remain accepted, and no additional open question is needed. The table specifies the information and action a caller must receive while expressly leaving final prose to design. The command forms preserve already confirmed interfaces rather than choosing new implementation mechanisms. This assessment does not validate implementation or authorize consolidation.

### Question verdicts for feature-request full_suite_levels round 3

| Question | Reviewer answer and assessment |
| --- | --- |
| Q01 | A. The whole-suite pass objective remains distinct from the affected-only default. The table correctly requires no coverage or duration repair at pass; informational observations must not displace the green instruction. The alternatives remain meaningful and in scope. |
| Q02 | A. Common parameter/environment/default precedence remains explicit. Restarting a selected full-suite level with an explicit parameter preserves the resolved objective even when it originally came from the environment. The default remains plain `ghog day` under its no-selector conditions. |
| Q03 | A. Validated preliminary results may be reused on unchanged sources. The table's noop rule is compatible with reuse, provided it reports saved proof and does not imply fresh execution. No new reuse choice is needed. |
| Q04 | A. The conservative test-only boundary is unchanged. The round-2 wording correction now describes how uncertainty is handled without asserting that classification cannot fail. The table does not grant a separate exception for production changes. |
| Q05 | A. Complete repair deltas remain subject to the agreed boundary, and tests and coverage may not be weakened. The table's test, crash and coverage repair directions fit this rule; operational stops remain stops. |
| Q06 | A. Repairs outside both permitted exceptions still require ordinary review of the same step and speed validation at the next convergence. "Carry on with the calling instruction" correctly leaves that routing to the requestor workflow. |
| Q07 | A. Duration acceptance remains a narrow exception after an attempted improvement with the required evidence. The table's shorthand "shorten ... or exclude" should explicitly carry that prerequisite; it does not justify changing the settled answer. |
| Q08 | A. Requested objective, execution/reuse and strongest valid saved proof remain distinct. Qualify the table's "not checked" language by the requested level or current invocation so a lower-level noop backed by speed proof is not described misleadingly. |
| Q09 | A. The same speed pass still precedes the non-review human gate, with implementation-check for changes outside the exceptions and no manufactured review exchange. The new closing instruction appropriately returns control to that calling workflow. |
| Q10 | A. Evidence that cannot establish its level cannot satisfy the requested objective. Its corrected wording now revalidates the selected objective without mandating an unconditional full-suite run. The table's noop instruction applies only when valid evidence actually permits reuse. |

The options and their tradeoffs remain adequate for all ten questions. None is redundant or outside scope, and the closing-instruction addition creates no unresolved choice requiring an eleventh question. The covered wording aligns the new table with these existing answers.

### Convergence evidence for feature-request full_suite_levels round 3

Covered wording:

1. Replace "any level" in the three non-default failure/crash rows with "`pass`, `cov`, `speed`". State that the default row covers applicable check/affected failures, including their crash diagnostics, and restarts with plain `ghog day` when existing recovery rules permit a restart. This removes overlapping instructions and prevents an invented `--full=default` or `--full=none`. Default walks have no full-suite outcome. Existing setup-error, interruption and other operational stop rules still apply.

2. Qualify the pass/cov green rows: "Coverage and duration gates are not required by the requested `pass` objective" and "The duration gate is not required by the requested `cov` objective." Report what actually ran or was reused separately under Q08. For a noop, state that the requested objective is met by valid saved evidence, identify its achieved level, and state that no checks ran in this invocation. Do not claim that a stronger saved proof lacks coverage or speed merely because the current request is weaker.

3. Replace the speed/outlier instruction with: "Attempt to shorten the flagged calls through `fix_slow_test.md`; accept a genuinely slow call with `ghog exclude` only after the attempted improvement and with the evidence required by Q07; then restart with `ghog day --full=speed`." In speed/green, use "no unaccepted duration outlier remains under the configured exclusions" rather than implying that an accepted slow call became fast. This preserves the existing exclusion policy and its visibility.

4. Add: "Rows marked 'Not judged' describe observations outside the selected objective; they are not failure outcomes. If no enforced failure remains, emit the requested level's green closing instruction and continue the calling workflow. Otherwise emit the applicable enforced-failure instruction." This keeps informational durations from replacing the required completion instruction at pass or cov, and does not prescribe a new failure-precedence policy.

5. Spell out the default green alternatives as three complete examples: `ghog day --full=pass`, `ghog day --full=cov`, and `ghog day --full=speed`. The current abbreviated "cov or speed" conveys the intended choice, but complete commands better serve the explicitly requested literal LLM instructions.

6. Make the existing scope explicit: "For direct `ghog full` calls, apply the full-suite outcome instructions for the resolved level as well; any suggested day-walk restart preserves that level." This carries gap 6 and the human's concern about full-run closing instructions into the table without changing selector precedence or the direct command's default.

These are wording clarifications of existing decisions and human guidance. No new option, behavior choice, or implementation structure is proposed.

Convergence rationale:

The human-requested addition is now present as a requirement rather than an implication: a deliberate full-suite skip is explained, the met objective and next action are stated, higher levels have their own completion/repair instructions, and restarts preserve the resolved level. Noops explicitly reuse evidence, and documentation/tests cover the closing behavior.

The ten settled answers remain coherent with the new section. The covered edits remove shorthand that could obscure existing distinctions (default versus full levels, attempted repair before exclusion, requested objective versus saved proof). None requires another substantive decision.

Recommend convergence and consolidation subject to the existing human choice. The requestor retains responsibility for presenting that choice and applying authorized consolidation; the reviewer grants neither consolidation nor commit authority.

### Human guidance response for feature-request full_suite_levels round 3

Human guidance:

Add the LLM-facing closing instructions as requirements. Rewrite gap 4 as a table of the required closing instruction for each level (default with the full suite skipped, `pass`, `cov`, `speed`) and each outcome (green, failure, coverage gap, duration outliers). A skipped full run must say the skip is expected, that the walk objective (check plus affected tests) is met, that the full suite must not be run unless the calling instruction asks for a level, and how to ask for one (`ghog day --full=pass|cov|speed`). Add a rule that every printed restart line names the level of the walk it restarts (for example `ghog day --full=cov`), so an LLM following it literally never drops back to the default walk.

Guidance response:

The current document implements the requested closing-instruction table and the explicit-level restart rule. The default green row states all four required facts: the skip is deliberate, check plus affected tests met the objective, no unsolicited full run is required, and a caller can request a full level. Its next action is to continue the calling instruction. The pass/cov/speed rows specify the objective, the applicable corrective work and the preserved restart level, and the noop paragraph identifies reuse.

I support this addition and keep it in requirement scope. The supplied wording makes the table reliable when followed literally: distinguish default from the three full levels, preserve the attempted-fix condition before exclusion, show complete alternative commands, and describe cached proof honestly. Apply the full-level instructions to direct full runs as well. These points restate the guidance and existing answers, so they do not require a new question or another substantive review round.

No consolidation has been performed. The human retains the existing convergence choice.

### Writer instructions for feature-request full_suite_levels round 3

Present the convergence recommendation at the existing human gate. Do not consolidate based solely on this reviewer answer.

Carry the supplied wording into the closing-instruction requirements when the human authorizes consolidation, together with the ten agreed answers. Keep the intentional default skip, the explicit level on non-default restart commands, and the distinction between executed work and reused proof. Preserve the ordinary requestor routing after successful validation; a green report is not commit authorization.

No additional automated round is needed solely for these wording alignments. Keep final message phrasing and rendering mechanics in design. Acceptance coverage should exercise the already specified default failure versus full-level failure, an environment-selected level restarted explicitly, a lower requested level backed by stronger saved proof, ignored duration observations, and the permitted duration-exclusion path.

The obsolete project-root answer location in the request template remains outside this specification. This answer is published only through the shared exchange at the returned artifact-home path.

### Final reviewer decision for feature-request full_suite_levels round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-09-29T19:10:42+02:00
- Exchange: specification/feature-request/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
