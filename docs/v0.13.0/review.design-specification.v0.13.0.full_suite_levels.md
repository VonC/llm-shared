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
   cSpell: disable-next-line
- Correct the Q03 typo "unjuNdged" to "unjudged."
   cSpell: enable

R1 is the substantive reason for another review round. R2 follows rules already present in the design and adds no new policy choice.

### Writer instructions for design-specification full_suite_levels round 1

Revise Q09, the Review-Off Speed Pass section, the workflow-instruction summary, and the matching acceptance cases together. Preserve the settled placement of speed before review and before the review-disabled commit menu, and preserve the absence of a commit-ready speed recheck.

Use the requested changes below to make every review-off speed repair reach implementation-check, including repairs that affect only ignored exclusion state. Keep the staged-tree comparison for tracked content and carry the exclusion explanation into the recheck, then refresh the commit material through the ordinary chain and require a green speed pass before the menu.

Apply the small consistency corrections in the same revision. Publish another automated design-review round. Do not consolidate this design yet.

### Final reviewer decision for design-specification full_suite_levels round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-10-01T08:14:03+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification full_suite_levels (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
Review round: 2

### Requestor assessment for design-specification full_suite_levels (round 2)

Round 2 applies the round-1 answer and adds the test-group requirement, which the human added to the feature request while round 1 was with the reviewer (gaps 18 to 25, clarifications Q15 to Q26, consolidated in two further requirement exchanges).

Round-1 feedback: R1 is applied inside Q09 as asked, with no separate policy question. The review-off pass now compares the staged tree and the effective exclusion entries, through a strict `ghog exclude --list` and its `--since` comparison: an added node or a raised baseline is a change, a lowered baseline or a removed entry is the tool's own tightening, and an unreadable side is `exclusions=unverified`, never unchanged. Any change goes back through implementation-check with the exclusion evidence in the step journal, then through the ordinary chain and a final green pass that compares against its own starting point. R2's corrections are applied; the Q03 typo was not found (the text already reads "unjudged"), but Q03's rationale was corrected, because the gate floor (line 2) is never rewritten by a run.

Groups: four groundhog sections (declaration, scope selection, grouped runs, group evidence) and two workflow sections (group scope in the workflow, activation and change). Eight new questions, Q12 to Q19, cover the decisions the requirement leaves to the design: declaration format, whole-suite selector spelling, group coverage computation (with the project's `omit` entries kept), the outlier rule in a group (floor alone), per-scope markers with scope and timing fingerprints, how workflow commands receive the scope (`pw scope`), where a round's bound scope is stored (a field the exchange core keeps at publication), and how an effort's scope changes (the requirement line, validated by `pw scope`).

No question seems missing to me. One interpretation to check: the requirement's "same gate configuration, timing floor included" is read as capping a saved proof at `cov` when only the floor or the exclusions changed, since `pass` and `cov` do not depend on them (Group Evidence, Q16). Please also check that Q18's core field is the right trade against role-written notes, and that the acceptance rows cover gap 25's group and activation list.

### Change summary for design-specification full_suite_levels (round 2)

- Context and scope: a fourth outcome for test groups, new in-scope items (exclusion listing, declaration, scope selection, grouped runs, per-scope markers, effort scope and bound scope), and two deferrals (a group-narrowed digest, per-group floors).
- Confirmed facts: how measuring runs rewrite `a.ghog.outliers` (line 1, the exclusion ratchet, stale removal), the parsed `TOTAL` coverage verdict over a project-wide measure, pytest commands without paths, empty-run classification, the two-condition outlier rule, the failure baseline, Python 3.13 `glob.translate`, and the workflow facts (pw reads no requirement header and prints no ghog command, the renderer's validation set, `pw progress` lines, draft metadata lines, reviewer commands, the code-review gate labels).
- Target behavior, level propagation, snapshot, reporting: the scope selector on every restart line, `scope=` on the closing and status lines, success lines naming their scope, marker keys `scope`, `fingerprint`, `timing`, and the marker rewritten or removed after failing walks too.
- Review-off pass (R1): new "Exclusion listing and comparison" and "Outcome of the review-off pass" subsections; exclusion-only, unchanged, ratchet-only, repeated-pass and unverifiable acceptance rows replace the old exclusion row.
- R2: forced scenarios in the snapshot example and the acceptance row, precise replacement-round noop preconditions plus two invalidation rows, the qualified migration notice, and Q04's failure-outcome wording.
- New sections: Test Group Declaration, Scope Selection, Group-Scoped Runs, Group Evidence, Group Scope in the Workflow, Group Activation and Change; requestor validation completed with the effort scope and the declared-set group statement; workflow instruction list and about 40 group and activation acceptance rows.
- Questions: Q03 corrected, Q04, Q05, Q06 and Q07 extended for scope, Q09 rewritten for exclusions, Q12 to Q19 added.

### Writer response for design-specification full_suite_levels (round 2)

Writer response:

Accepted R1 in full, inside Q09: the staged-tree comparison is supplemented by a semantic comparison of effective exclusion entries; a change in either, or an unverifiable comparison, returns the step through implementation-check with the call, measured time, attempt and reason recorded for the checker; each later pass compares against its own start, so pre-existing or already rechecked exclusions cause no loop. The suggested replacement paragraph is used almost verbatim. The discarded post-review machinery stays dropped.

Accepted R2: `--force` added where saved `speed` would otherwise make the walk a noop; the replacement-round noop now requires an unchanged validated digest, a readable marker and recorded `speed` for the same scope, with invalidation and upgrade rows beside it; the migration notice is qualified with "when no full level is selected" and keeps fresh work apart from stronger saved proof; Q04 states that failing walks update or remove the marker per Q08. The Q03 typo is not in the document, which already reads "unjudged"; while checking it, Q03's description and rationale were corrected to match the code: runs rewrite the auto-floor record and the exclusion section, never the gate floor.

The test-group additions follow the consolidated feature request without reopening its decisions; the design-level choices are in Q12 to Q19.

### Reviewer focus for design-specification full_suite_levels (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-10-01T08:24:22+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification full_suite_levels round 2

The current design and all nineteen questions were read in full against the validated round-2 request. The round-1 exclusion comparison and proof-invalidation corrections are present in the current text. The request accurately describes the group additions; there is no substantive request/document drift.

Disposition: changes-requested. Two implementation decisions remain unresolved: how a published or detached scope is actually kept immutable when the group declaration changes, and how coverage collection obtains data for every source file the group resolver accepts. These affect which tests execute and whether a valid group can reach its coverage gate; they are more than wording changes.

The proposed answers are otherwise coherent. In particular, I support Q16's timing-only downgrade to cov: an edit confined to the floor or exclusions contradicts the saved duration verdict, not already established test or coverage evidence. This works provided timing inputs are separated from the ordinary digest and other scope/gate inputs still invalidate proof as specified. I also support keeping bound scope in the exchange core (Q18), rather than in role-authored notes or the transcript; its execution contract needs completing.

The acceptance table covers most group activation and switching cases, including explicit whole-suite selection, stale draft metadata, destination-scope reuse, declared validation authority and pending changes at the human gate. Add cases for same-name definition drift during actual reviewer/detached execution and for an executed source outside the original coverage source setting. Merely displaying a pending change does not verify that execution stays bound.

This is a specification assessment, not implementation validation. No specification, request, coordination record or transcript was edited by the reviewer.

### Question verdicts for design-specification full_suite_levels round 2

| Question | Verdict and selected answer |
| --- | --- |
| Q01 | Agree with A. The separate sequential timing step gives the parallel day walk its duration evidence while preserving the explicitly settled direct-full behavior. The alternatives are distinct; C crosses that settled boundary. |
| Q02 | Agree with A. A day-only cycle avoids a duplicated timing pass and follows the same level resolution as direct callers. |
| Q03 | Agree with A. Omitting durations below speed avoids unjudged exclusion ratchets. Qualify the wording about file writes for groups and direct whole-suite full runs as described in the wording corrections. |
| Q04 | Agree with A. One atomic marker containing scope, fingerprints, digest and proof supports default noops and upgrades; failing-walk handling correctly defers to Q08. The JSON alternative is valid but provides no required advantage here. |
| Q05 | Agree with A. Appended evidence keys keep the existing reporting grammar and expose selected objective separately from earned proof. |
| Q06 | Agree with A for level propagation. Inheriting the level environment preserves src. Scope propagation is a different issue: forwarding a name does not freeze its definition; address that under Q18 and the scope sections. |
| Q07 | Agree with A. Carrying the resolved objective through repair commands makes restart behavior explicit. The same-name scope-drift case still needs the bound-execution rule below. |
| Q08 | Agree with A. Capping both saved and newly earned evidence at the first contradicted gate handles the important parallel-timing failure cases without discarding unrelated lower proof. |
| Q09 | Agree with A. The strict semantic exclusion comparison closes the ignored-state gap, distinguishes ratchets from new exceptions, and treats unreadable evidence as unverified. Comparison against each pass's own starting point prevents repeated rechecks. |
| Q10 | Agree with A. The requestor must supply the attempt and rationale, which an automatic list cannot reconstruct; the reviewer can verify the local exclusion entries. |
| Q11 | Agree with A. The renderer is the reliable place for an every-request migration notice. The current qualification correctly avoids claiming that an unqualified command can never reuse stronger proof. |
| Q12 | Agree with A. A dedicated INI declaration and a fingerprint for the selected group avoid invalidating unrelated scope proof when another group is added. |
| Q13 | Agree with A. An explicit whole-suite flag is clear and leaves group names unrestricted by a reserved all value. The conflict case is explicitly defined. |
| Q14 | Agree with A's per-file analysis and project omit rules, but incomplete: specify collection as well as analysis. Reading existing data cannot supply measurements that the configured collector excluded. Prefer collecting all resolved group sources, then applying the stated gate; see R2. |
| Q15 | Agree with A. The floor-only grouped verdict is an explicit, justified choice avoiding a group-relative norm and new saved statistical state. Preserve the no-write rule and existing exclusion behavior. |
| Q16 | Agree with A and with the timing-only cap at cov. Per-scope markers prevent cross-scope reuse; floor/exclusion changes require fresh speed evidence while lower evidence remains usable. Add a timing-change-at-cov acceptance case and distinguish timing-only changes from ordinary digest changes. |
| Q17 | Agree with A. Resolve the requirement when a new workflow command begins, keep the launcher as the runner, and carry the selected scope through that invocation. A published review or already launched detached walk must use its bound resolution as addressed in R1. |
| Q18 | Agree with A's core-owned record, but incomplete: the stored selector and fingerprint detect drift without preserving the old resolved scope for execution. Complete the snapshot/validation and consumer behavior; see R1. |
| Q19 | Agree with A. Editing the requirement line is consistent with the settled control point; reopening the requirement or inventing another setter is unnecessary. |

No existing question needs removal. The missing decisions fit Q14 (coverage collection and gate inputs) and Q18 (bound scope representation and execution), with corresponding updates to scope propagation; separate new policy questions are unnecessary if those questions are completed.

For Q18, the material alternatives are: capture the validated resolution with the request/detached launch, or execute against an immutable reviewed declaration/tree. Either can preserve the published scope. Re-resolving only the name is insufficient; comparing only the fingerprint can detect drift but must stop rather than silently run a different scope. I recommend an explicit captured resolution consumed by the execution path, with a typed refusal when it can no longer be used safely.

For Q14, the material alternatives are: configure measurement to cover the accepted resolved source set, or explicitly restrict and validate group sources against the project's collector configuration. I recommend configuring collection to cover the resolved set, which matches the currently unrestricted source-pattern declaration. Silently accepting an unmeasurable source and later calling it unexecuted is not an adequate third option.

### Requested changes for design-specification full_suite_levels round 2

Requested changes:

#### R1: Preserve the resolved scope through actual execution for design-specification full_suite_levels (round 2)

Evidence: Scope propagation (lines 673-688) forwards only `--group=<name>` to a detached child. Scope-carrying workflow commands and Bound scope of a review round (lines 962-993) store a selector, fingerprint and source requirement, then tell the reviewer to run ghog affected --no-cov with that selector. When a scope change takes effect (lines 1049-1062) promises that a launched walk and a published round keep their original scope. The acceptance table explicitly allows editing the patterns of the same named group while the round is published.

Counterexample: round 2 is published for sentinel matching tests/old/**. Before reviewer evidence runs, sentinel is edited to match tests/new/**. The reviewer's printed --group=sentinel command resolves the current .ghog-groups and therefore selects tests/new/**. A stored old fingerprint can reveal the difference but cannot tell the command what old file set to use. There is also a launch-to-child-resolution window when detach forwards only the mutable name.

Requested change: define an immutable resolved-scope representation or an immutable reviewed configuration that the reviewer and detached execution actually consume. Bind it to the stored fingerprint, validate its provenance and usable paths, and explicitly reject an unusable binding before executing evidence. A current-name lookup must never silently substitute a new scope. Define the compatibility behavior for a live request lacking the newly introduced bound data. This can extend Q18 without adding a protocol transition.

Suggested wording: "A bound scope is the validated resolution used at publication or launch, not merely its group name. Reviewer evidence and the detached child consume that captured resolution (or its immutable reviewed configuration). Later changes to the current declaration are displayed as pending changes and apply only at the next eligible boundary. If the captured scope cannot be validated or executed, evidence stops with an explicit diagnostic; it never re-resolves the name to a different scope."

Acceptance additions: publish sentinel with tests/old/**, change the same group's patterns before reviewer evidence, and verify the original resolved selection or an explicit refusal before any different tests run; change the declaration between detached launch and child resolution and verify the same property; verify a missing/invalid bound payload cannot acquire a guessed scope. Include the corresponding source membership, not just the group name, in these checks.

#### R2: Define coverage collection for the accepted source set for design-specification full_suite_levels (round 2)

Evidence: Confirmed Technical Facts describes project-wide --cov=tools and configured coverage source (lines 205 onward). Resolved group membership (lines 611-627) accepts matching Python source files minus omit rules without restricting them to that collector source. Narrowed collection (lines 693-708) changes pytest's test paths. Group coverage gate (lines 710-729) changes post-run analysis and --cov-fail-under, but does not say how measurement includes every accepted group source.

Counterexample under the specified command construction: a valid group's tests exercise lib/widget.py and its sources pattern selects lib/**, while the project still collects only tools. The resolver accepts the source; the run executes it; the saved coverage data has no measurement for it. The proposed analysis then calls it entirely missed. Adding or improving the group's tests cannot repair a measurement exclusion.

Requested change: specify a collection strategy that measures the resolved group sources before applying per-file analysis, or an explicit validation restriction that refuses sources the chosen collector cannot measure. Prefer the former to match the declared general source patterns. Keep the project's relevant coverage semantics when computing 100%; do not accidentally substitute line-only success for any stronger configured coverage gate. Define missing/corrupt coverage-data handling separately from a valid measurement where one particular source was never executed.

Suggested wording: "For a grouped covered run, collection is configured to measure every resolved, non-omitted group source. The gate analyses that same resolved set under the project's applicable coverage settings. A source absent from valid run data counts as unexecuted; unavailable or invalid run data produces an explicit evidence error rather than a coverage-success claim. Changing the collector's threshold alone is not sufficient."

Acceptance additions: a fully exercised accepted source outside the original project coverage source can reach the group gate; an otherwise identical never-executed source fails at 0%; project omit rules still apply; invalid measurement data cannot establish coverage proof. If configured branch coverage is supported by the consuming project, a missing required branch must not be hidden by executed-line analysis.

#### Wording corrections alongside R1 and R2 for design-specification full_suite_levels (round 2)

- Scope resolution says standalone ghog timings is the only standalone command that rewrites the floor file, but the direct sequential ghog full speed shape also measures durations. Say that grouped runs never write it and that whole-suite duration-measuring runs retain their writes.
- Q03's "only speed walks touch that file" should distinguish whole-suite duration-measuring runs from grouped walks and include direct full/timings where applicable.
- Keep the timing-only cap at cov, but add an acceptance case proving a cov request reuses unchanged test/coverage evidence after only the floor or exclusions change. Ordinary digest and scope changes must still invalidate as documented.
- Add the missing blank line after the narrowed-collection list before the paragraph beginning "A grouped full or timing run". The repository Markdown check reports MD032 at line 704.

These wording edits alone would not prevent convergence; R1 and R2 require another assessment of substantive design changes.

### Writer instructions for design-specification full_suite_levels round 2

Keep the settled level model, review timing, review-off exclusion comparison, declared validation authority and requirement-based scope selection.

Complete Q18 and the bound-scope/propagation sections to explain how reviewer evidence and a detached child consume the exact resolved scope captured for their round or launch. Specify what is retained, how it is validated, how stale or missing legacy bound data is reported, and what happens if the old resolution cannot be executed. Keep core ownership and the existing transitions. Do not infer old scope from current mutable declarations or silently fall back to whole-suite execution.

Complete Q14 and Group coverage gate with the collection configuration that supplies data for every accepted source file. Retain configured omission and coverage semantics, the never-executed-source rule and the fresh grouped-full data rule. State how absent/unreadable measurement data is distinguished from a valid data file in which a source was not executed. If choosing to restrict source membership instead, make that a visible validation rule with its consequences, not an accidental permanent coverage failure.

Add the concrete acceptance cases in R1 and R2, plus a saved cov proof after a timing-only change to verify the intended Q16 cap. Align the small wording corrections listed with the findings. Leave consolidation for the human convergence gate; publish the amended specification for another review round.

### Final reviewer decision for design-specification full_suite_levels round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-10-01T08:32:02+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification full_suite_levels (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
Review round: 3

### Requestor assessment for design-specification full_suite_levels (round 3)

Round 3 completes Q18 and Q14 as the round-2 answer asked, without new questions and without new exchange transitions.

R1 (Q18, Scope Selection, Group Scope in the Workflow): a bound scope is now a captured resolution, not a name. A capture holds the scope kind, group name, normalized patterns, resolved test and source file lists, fingerprint and provenance. Groundhog gains a third explicit selector, `--scope-file`, which validates the capture (complete, fingerprint recomputed from content, every listed file present) and then runs exactly its lists, never re-matching patterns, reading `.ghog-groups` or looking the name up; any failure is exit 5 `bound scope unusable` before a test runs. The renderer writes the capture, `publish-request` takes it as `--scope-capture-file`, checks it against the envelope's `test_scope`, and copies it to a core-owned `paths.scope` artifact; the reviewer runs `ghog affected --no-cov --scope-file=<paths.scope>`. A detached grouped walk passes its own launch capture to the child. A legacy request without `test_scope` reports `bound_scope: missing` and is missing evidence, never a guessed scope. Q18's alternatives are now capture, immutable Git objects, and a role-written note.

R2 (Q14, Group coverage gate): collection adds one `--cov` folder per resolved source folder so sources outside the project's collected `source` are measured; data goes to a scope-owned file through `COVERAGE_FILE`; analysis covers exactly the resolved set under the project's coverage settings, omit and branch measurement included; missing, unreadable or stale data is an evidence error (exit 5, no proof). Q14's alternatives are now measure-the-resolved-set, restrict-to-the-collector, and ignore-omit.

Wording corrections are applied; the timing-only cap gains acceptance cases. The MD032 the repository check reported came from a wrapped line starting with "5)", read as a list marker; it is rewrapped.

Please check that the capture's validation and the legacy rule close the counterexamples of R1, and whether a separate question is needed for the new core artifact, or Q18 covers it as you suggested.

### Change summary for design-specification full_suite_levels (round 3)

- Scope: in-scope list names captured scopes and group coverage collection; the reviewer-side deferral mentions the captured scope.
- Scope Selection: `--scope-file` added to the resolution rule and its errors; floor-file writes restated (grouped runs never write, whole-suite measuring runs keep their writes); restart lines name the group, a restart being a new boundary; detached grouped walks pass a launch capture; new "Captured scope" subsection.
- Resolved group membership: sources outside the project's collected `source` are accepted and measured.
- Group coverage gate: rewritten in three parts (collection, analysis, data errors).
- Group Evidence: timing inputs never move the digest; digest and scope changes still invalidate.
- Group Scope in the Workflow: reviewer evidence runs `--scope-file=<paths.scope>`; "Bound scope of a review round" rewritten (capture output, `--scope-capture-file`, core-owned `paths.scope`, legacy `bound_scope: missing`); "When a scope change takes effect" ties started walks and published rounds to their captures.
- Workflow Instructions: reviewer commands, requestor capture handling, and `review-requestor.md`.
- Acceptance cases: reviewer row updated; 15 rows added for R1, R2 and the timing-only cap.
- Questions: Q03 wording, Q06 description, Q14 and Q18 rewritten.
- MD032: the paragraph line starting with "5)" rewrapped.

### Writer response for design-specification full_suite_levels (round 3)

Writer response:

Accepted R1: the chosen alternative is the explicit captured resolution consumed by the execution path, with a typed refusal, as recommended; the suggested wording is used in "Captured scope" and "Bound scope of a review round". Legacy live requests without bound data are treated as missing evidence rather than as the whole suite, so no scope is ever guessed.

Accepted R2: collection now covers the resolved set, as recommended over restricting membership; the project's omit and branch semantics are kept, and invalid data is an evidence error, separate from a valid file in which a source was never executed.

Accepted the wording corrections and the timing-only acceptance cases. On the MD032 finding: the location was right, but the cause was a wrapped line starting with "5)", which the repository check reads as an ordered-list marker; rewrapping it fixed the finding.

One observation for the reviewer's own content: the round-2 answer writes `--group=<name>` without backticks, and the transcript now fails the repository's markdown check with MD033 (raw HTML element `<name>`) at line 254. The requestor does not edit the transcript.

### Reviewer focus for design-specification full_suite_levels (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-10-01T08:37:30+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification full_suite_levels round 3

Convergence recommended. I read the complete current specification and the validated round-3 request. Both substantive findings from the preceding review are resolved in the design and acceptance cases. No additional open question is needed.

R1 is resolved: the execution path consumes the captured test and source lists through `--scope-file`; it does not look up the group name or re-match changed patterns. The capture is checked for completeness, fingerprint consistency and file existence before tests run, with exit 5 on unusable evidence. The same-name declaration change and detached launch-to-child cases now have explicit outcomes. The legacy rule reports missing bound evidence and requests replacement instead of guessing a scope. Q18 explicitly includes the new core-owned artifact and publication input, so a separate question for their existence would duplicate Q18.

R2 is resolved: collection now includes the accepted source folders, including sources outside the project's original coverage source configuration. Analysis uses the resolved source set and the project's statement, branch and omission settings. A never-executed source in valid data fails coverage; missing, unreadable or stale measurement is an evidence error. Fresh full-run data and the non-proving intermediate affected run are distinguished. The outside-source, unexecuted-source, omitted-source, invalid-data and missed-branch cases make the intended behavior testable.

The timing-only proof rule is also consistent: duration inputs remain outside the source digest; changing only them caps saved speed proof at cov while retaining lower proof. The added cases cover both a cov noop and a speed upgrade. The revised duration-writer wording covers direct sequential full runs as well as walk timing passes.

These are specification conclusions, not implementation validation. The eventual plan must carry the stated capture, evidence-error and coverage acceptance cases into the relevant components.

The request reports MD033 in the earlier reviewer transcript entry. I acknowledge the unquoted placeholder in my authored text; the intended spelling is `--group=<name>` in inline code. That historical formatting defect does not change the design verdict. This answer uses code formatting for placeholders; it does not rewrite the core-owned transcript.

### Question verdicts for design-specification full_suite_levels round 3

All nineteen questions are in scope. None is missing, redundant or substantively unclear in the current text. Their options identify materially different choices and relevant consequences. I agree with every recommended answer, option A, for the reasons below. Alternatives that depart from a confirmed requirement remain useful as rejected alternatives, not unresolved implementation choices.

| Question | Reviewer choice and reason |
| --- | --- |
| Q01 | A: a parallel speed day walk must actually measure durations; the extra sequential pass supplies that evidence while the direct full command retains its settled single-run boundary and reports cov honestly. |
| Q02 | A: once the day walk owns its timing pass, the cycle's default must be day alone to avoid duplicate or unsolicited timing work. |
| Q03 | A: dropping duration measurement below speed prevents unjudged runs from changing timing records; the revised whole-suite wording and grouped no-write rule agree. |
| Q04 | A: one atomically replaced marker binds the digest to its proof, preserves default-walk reuse and treats incomplete legacy data conservatively. |
| Q05 | A: appended evidence keys retain the established closing-line grammar and make foreground and detached outcomes equally visible. |
| Q06 | A: forwarding an explicit level and otherwise preserving the inherited environment keeps both level and provenance; captured scope is correctly handled separately. |
| Q07 | A: carrying the level through repair commands makes their printed restart lines preserve the objective without relying on conversational memory. |
| Q08 | A: accumulated proof must be capped by any later contradictory gate, including a timing-pass test failure; an outlier-only failure retains cov. |
| Q09 | A: staged-tree comparison plus semantic exclusion comparison covers both tracked edits and newly accepted ignored exceptions, without treating routine tightening as a new exception. |
| Q10 | A: the implementation report is the available source of the attempted improvement and justification; the reviewer can verify the recorded exclusion locally. |
| Q11 | A: rendering the migration notice from the resolved declared set puts it in every relevant request without rewriting the project's policy. |
| Q12 | A: the dedicated INI declaration allows comments and avoids invalidating unrelated scope proof merely because another group was declared. |
| Q13 | A: the explicit whole-suite flag is unambiguous and overrides ambient group selection without reserving a group name. |
| Q14 | A: the revised choice covers collection and analysis, so accepted sources outside the original collector can earn coverage; project exemptions and branch semantics remain in force, and unusable data is not a passing result. |
| Q15 | A: the shared floor and existing exclusions provide the settled group duration standard without allowing a uniformly slow group to define its own norm or rewrite the shared records. |
| Q16 | A: separate scope markers preserve exact-scope reuse, and the timing fingerprint invalidates only the part of proof that depends on durations. |
| Q17 | A: resolving the current requirement when producing each workflow command avoids stale selectors in plans and keeps the actual groundhog command visible. |
| Q18 | A: the captured resolution is now consumed by execution, with a refusal for unusable or missing evidence. The new protocol artifact and publication input belong to this existing decision; a separate question is unnecessary. |
| Q19 | A: one versioned requirement line remains the authority, with validation before use and explicit boundaries for applying a change. |

No replacement questions or different answers are proposed. Keep the capture and coverage cases attached to Q18 and Q14 respectively when consolidating after human authorization.

### Convergence evidence for design-specification full_suite_levels round 3

Covered wording:

In the Target Behavior fenced summary, align the abbreviated scope-resolution line with the already complete Scope resolution rule:

```txt
scope = one explicit selector (--group=G | --whole-suite | --scope-file=capture)
        else GHOG_GROUP else whole suite; invalid or unusable -> exit 5
```

This is a summary-only wording correction. It introduces no new selector, precedence, error policy or question.

Convergence rationale:

Every in-scope decision has a supported answer. The two previously missing execution contracts are now explicit: bound scopes are captured and consumed without later name resolution, and group coverage is collected for the accepted source set before its gate is analysed. Refusal behavior, legacy evidence handling and concrete acceptance cases are supplied. The timing-only proof cap and duration-file wording are consistent with those choices.

The only proposed design edit repeats an existing rule in the overview. The historical transcript placeholder is likewise a formatting defect, not a specification decision. I recommend convergence at the human gate, without consolidating or taking the requestor's next action.

### Writer instructions for design-specification full_suite_levels round 3

Present the convergence recommendation at the existing human gate. This recommendation does not authorize consolidation; the user requested no consolidation for now.

Only the covered wording alignment remains in the reviewed design. Preserve the resolved Q14 and Q18 contracts and their acceptance cases. No substantive rewrite or additional automatic review round is requested.

The prior transcript MD033 is acknowledged as reviewer-authored formatting. The intended correction wraps the existing `--group=<name>` placeholder in backticks. Neither role should hand-edit protocol-owned history under the current exchange instructions, and this answer does not authorize doing so; report that separate formatting defect through the owning review-tool maintenance path if it remains after the exchange. Do not treat it as a reason to change this design or as a missing design question.

### Final reviewer decision for design-specification full_suite_levels round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-10-01T09:40:00+02:00
- Exchange: specification/design-specification/v0.13.0/full_suite_levels
- Umbrella: none
- Reviewed document: docs/v0.13.0/design.v0.13.0.full_suite_levels.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
