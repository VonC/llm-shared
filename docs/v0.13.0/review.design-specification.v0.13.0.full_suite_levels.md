# Specification review transcript for v0.13.0

- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-30T12:21:02+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification full_suite_levels (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
Review round: 1

### Requestor assessment for design-specification full_suite_levels (round 1)

This design answers the consolidated and reopened feature request `docs/v0.13.0/feature-request.v0.13.0.full_suite_levels.md`, where `speed` is proven before every code-review request under the default validation policy, never at the commit-ready answer, and, without review mode, between implementation-check and the commit menu. It replaces an earlier design dropped before its third round; it reuses that design's reviewed level model, run shapes, snapshot rules (with the proof cap applied to earned and saved proof), reporting, status keys, selector errors and repair-command propagation, and removes every post-review mechanism (test-only declaration, classifier, baseline and candidate evidence, reopen transition).

New design areas: requestor validation at `speed` through the default tuple, exclusion evidence in the implementation report, the migration notice for declared validation sets, and the review-off `speed` pass with a staged-tree comparison. Eleven questions: Q01 to Q08 carry the choices accepted in the earlier design review, renumbered; Q09 to Q11 cover the new areas.

Please check that nothing assumes the dropped post-review pass, that the review-off pass and its return path are sound, and whether a design question is missing.

### Change summary for design-specification full_suite_levels (round 1)

Round 1: the design document is new. Sections: context and scope; confirmed facts (including the step chain branching on review mode after `a.commit`, and the unchanged convergence path); current and target behavior; level model; level-shaped full runs and direct `ghog full`; snapshot evidence with atomic marker, proof cap and upgrade reuse; walk reporting with closing and status keys and restart lines; requestor validation at `speed`; review-off `speed` pass; workflow instructions; acceptance cases. Eleven open questions appended through `oqm`.

### Writer response for design-specification full_suite_levels (round 1)

Writer response:

No earlier feedback on this document: it is a fresh design. The earlier design on this topic was dropped with the post-review `speed` pass; the reusable parts carry the corrections its review asked for (proof cap on earned and saved proof, `unproven`, atomic marker, direct-run earned proof, status keys, selector errors mapped to exit 5, repair commands carrying the level, `none` never printed as a selector). The feature request's settled decisions should not be reopened.

### Reviewer focus for design-specification full_suite_levels (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.design-specification.v0.13.0.full_suite_levels.md`
- `.reviews/a.review-requested.design-specification.v0.13.0.full_suite_levels.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-30T14:02:07+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification full_suite_levels round 1

Changes requested for the replacement design, occurrence 1, round 1.

The design consistently removes the dropped post-review speed work. The commit-ready path presents the existing human gate without a speed walk or a new exchange transition. The default requestor validation occurs before each request, project-declared commands remain authoritative, and the direct parallel full run reports cov rather than claiming speed. The level model, proof cap on both earned and saved evidence, and level-carrying repair commands form a coherent design.

One substantive issue prevents convergence: the review-off change detector treats an exclusion-only speed repair as no change. The document itself states that exclusions live in ignored state (line 137), then explicitly sends that case directly to the commit menu (lines 511-514 and acceptance row 582). The settled requirement, also referenced in Q09, requires any speed repair, including a duration exclusion, to return through implementation-check. Showing an exclusion to the human at the commit menu does not perform that check.

The missing aspect belongs inside Q09: how the detector covers ignored duration-exclusion changes as well as the staged tree. No separate policy question is needed, and the earlier post-review classifier, repair baseline, and convergence transition should remain dropped. I agree with A for the other ten questions and with the staged-tree part of Q09 A, subject to the concrete extension below.

### Question verdicts for design-specification full_suite_levels round 1

| Question | Assessment and answer I would choose |
| --- | --- |
| Q01: parallel speed proof | A. The alternatives are distinct, and A provides uncontended timing in day walks while preserving the settled direct-full single-run boundary. Reporting cov for direct parallel full is essential and is present. |
| Q02: cycle default | A. Once day owns its selected timing step, a default day-only cycle avoids both an unsolicited timing run and a duplicate one. Explicit sequences remain available. |
| Q03: durations below speed | A. Omitting measurement below speed is allowed by the requirement and keeps those runs from changing timing floors. Informational durations are optional, so B is unnecessary and C changes timing state for an unenforced gate. |
| Q04: atomic marker | A. One atomic digest/proof record supports default-walk reuse and avoids mismatched files. Keep the separately stated proof updates after failures as well as writes after green walks. Unreadable and legacy markers correctly establish no proof. |
| Q05: evidence keys | A. Appending the selected objective, source, valid proof, and reuse information retains the existing key-based format. Distinguishing none from unproven and exposing the same completion evidence through status are clear. |
| Q06: detached level and source | A. Forward explicit selectors and inherit the environment otherwise. Under the documented spawn contract this preserves both level and source, including a valid parameter overriding an invalid environment value. |
| Q07: restart helper and repair commands | A. Carrying the objective on check, affected, and single preserves it through side runs without changing what those commands measure. The alternatives rely on memory or unrelated lifecycle state. |
| Q08: surviving proof | A. Capping accumulated earned and saved proof below the lowest contradicted gate prevents a later timing failure from retaining an earlier cov result. Gate-neutral operational outcomes and stale digests are distinguished. Correct the forced-run acceptance example below. |
| Q09: review-off change detection | Amend A before accepting it. The staged tree is a good exact detector for Git content, but it cannot detect ignored duration exclusions. B misses additional file types, while C loses verifiability. Extend A with a comparison of effective exclusion entries and route a change in either input through implementation-check. The current option's claim to cover every kind of change is false. |
| Q10: exclusion evidence for the reviewer | A. A required implementation-report entry can carry the call, measured time, attempted improvement, and reason, while the local exclusion file provides corroboration. The reliance on requestor completeness is explicitly stated; the alternatives add automatic listing but cannot supply the explanation. This review-enabled disclosure mechanism does not replace implementation-check on the review-disabled path. |
| Q11: migration notice producer | A. The renderer is the appropriate place to guarantee the notice on every applicable request. Keep the notice conditional about what plain day establishes: the selected environment level, other commands, or valid saved evidence may supply stronger proof. |

The questions have materially distinct alternatives. Q09 is incomplete rather than redundant or outside scope: broaden it to "How does the review-off speed pass detect changes to the step or its duration exclusions?" No other missing decision is apparent from the reviewed specification.

### Requested changes for design-specification full_suite_levels round 1

Requested changes:

R1 — Detect and recheck exclusion-only repairs in review-off mode.

Location: Review-Off Speed Pass / Change detection (lines 498-515), Q09 (lines 834-863), the workflow summary, and the exclusion-only acceptance row (line 582).

The current rule compares only git write-tree. It then expressly exempts a duration exclusion because that file is ignored. This contradicts the required return through implementation-check for every speed repair. Listing it at the final menu is useful disclosure, but is not the required return path.

Extend Q09 A and the design as follows:

- Before the speed pass, retain the staged-tree identifier and the effective entries of the [exclusion] section used by that pass. After the green walk and staging, compare both.
- A changed tree OR changed exclusion entries sends the step through implementation-check. Include the changed call, measured time, attempted improvement, and reason in that handoff so the checker can assess ignored policy changes.
- Compare exclusion semantics, not the entire a.ghog.outliers file: a normal timing run can rewrite floor or observation data without accepting a new duration exception. Pre-existing unchanged exclusions must not cause a repeated recheck. State how absent exclusion data is represented and how an unreadable comparison is handled; it must not count as verified unchanged.
- After implementation-check, follow the ordinary chain to refreshed commit material and another green speed pass, using valid saved evidence when applicable. The commit menu is reached only when the required recheck has completed and the final pass makes no additional relevant change.

Suggested replacement for the exclusion paragraph: "Duration exclusions are ignored Git state, so the staged-tree comparison is supplemented by comparison of effective exclusion entries. A change to either sends the step back through implementation-check. The handoff and final commit summary identify each accepted exclusion with its measured time, attempted improvement, and reason."

Replace the current exclusion-only acceptance outcome with return through implementation-check and then the final green speed pass before the menu. Add cases for unchanged exclusions and floor-only rewrites avoiding a spurious loop, and for an unverifiable exclusion comparison not bypassing the check. The implementation can reuse existing exclusion parsing; this does not require the discarded post-review machinery.

R2 — Correct acceptance preconditions and align short wording with the chosen design.

- Line 575: "replacement round changed no Python file" does not establish a valid speed snapshot. Gate-configuration changes, a stale or damaged marker, or a marker proving a lower level also matter. Specify an unchanged validated digest, a readable marker, and recorded speed proof for the noop case; retain invalidation/upgrade cases separately.
- Line 570: saved speed on unchanged sources makes a speed walk a noop. Add --force to the scenario that is intended to exercise a later timing failure capping saved speed proof.
- In the declared-validation notice, qualify "plain ghog day now proves only check and affected" with "when no full level is selected"; retain the existing distinction between fresh work and stronger valid saved proof. The notice must not make a claim that the next sentence retracts for GHOG_FULL.
- In Q04, state that failure outcomes also update or remove the marker according to Q08; "written by every green walk" must not be implemented as "written only on success."
- Correct the Q03 typo "unjuNdged" to "unjudged."

R1 is the substantive reason for another review round. R2 follows rules already present in the design and adds no new policy choice.

### Writer instructions for design-specification full_suite_levels round 1

Revise Q09, the Review-Off Speed Pass section, the workflow-instruction summary, and the matching acceptance cases together. Preserve the settled placement of speed before review and before the review-disabled commit menu, and preserve the absence of a commit-ready speed recheck.

Use the requested changes below to make every review-off speed repair reach implementation-check, including repairs that affect only ignored exclusion state. Keep the staged-tree comparison for tracked content and carry the exclusion explanation into the recheck, then refresh the commit material through the ordinary chain and require a green speed pass before the menu.

Apply the small consistency corrections in the same revision. Publish another automated design-review round. Do not consolidate this design yet.

### Final reviewer decision for design-specification full_suite_levels round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->
