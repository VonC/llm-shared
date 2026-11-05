# Specification review transcript for v0.14.0

- Exchange: specification/feature-request/v0.14.0/version-sources
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-03T20:41:07+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
Review round: 1

### Requestor assessment for feature-request version-sources (round 1)

Writer assessment of the version-sources feature request, round 1.

The requirement is the first written form of umbrella item 2, built from the
focused child draft the human approved on 2026-11-03. It keeps the item 2
acceptance criteria of the umbrella as fifteen observable criteria (AC1 to
AC15) and groups the supporting umbrella contracts by topic: anchor, adapter
registration, detection, forms, supported formats, version-only writes and
internal references, the version commands, the `.release.ini` version domain,
tag classification, release-version uniqueness, callers, dev_workflow defects
and consumer inputs.

Open questions: thirteen are proposed (Q01 to Q13), all with a recommended
option and a pending user decision. They target behavior the umbrella leaves
unstated for this item:

- the direct `versions set` command: accepted targets (Q01), same-value runs
  and drift repair (Q02), locking (Q11) and restoration failure (Q12);
- the anchor's well-formedness rule (Q03) and the `release-only` refusal
  scope (Q04);
- participation: tool-only manifests (Q05), one version for all participating
  components (Q06) and undeclared nested candidates (Q07);
- the supported internal-reference boundary (Q08), which umbrella decision 39
  says the child requirement must state;
- pattern-source required keys and missing files (Q09);
- lock consistency as accepted by the ecosystem tools (Q10);
- range-selector targets beyond HEAD (Q13).

The writer considers the question set sufficient for a feature request, with
no design-level question: interfaces, module layout, detection algorithms, the
persistent tag-eligibility mechanism and output formats are left to the design,
as the umbrella intends.

Please assess the whole specification independently: completeness against
umbrella item 2 and decisions 5, 6, 13, 14, 15, 26, 33, 34 and 39; consistency
with the ownership boundaries of items 3 to 8; any missing question; and
whether each question's options and recommended answer are sound.

### Change summary for feature-request version-sources (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` was written by
  `write-requirement` from the approved child draft
  `docs/v0.14.0/draft.v0.14.0.version-sources.md`, with type feature-request,
  version v0.14.0, slug version-sources and test group whole suite.
- `review-ask-questions` then appended the open-questions section with Q01 to
  Q13 through `oqm`.
- Both files are untracked; the umbrella draft is unchanged.

### Writer response for feature-request version-sources (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Two writer notes for this
first round:

- The body's "Version-only writes, locks and internal references" section
  currently says the design states the supported internal-reference boundary.
  Umbrella decision 39 and its contract text say the child requirement states
  that boundary and the design chooses how references are identified and
  changed. The writer raised this as Q08 rather than fixing the body before a
  human decision, so consolidation can apply the chosen boundary.
- The anchor layout sentence (first token, title after `--`, notes on the
  following lines) follows the real llm-shared `version.txt` and the umbrella's
  release preflight. The umbrella's dev_workflow table says `get-version.bat`
  parses "line 1 into" version, title and notes, which reads less precisely.

### Reviewer focus for feature-request version-sources (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.feature-request.v0.14.0.version-sources.md`
- `.reviews/a.review-requested.feature-request.v0.14.0.version-sources.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-03T20:44:54+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request version-sources round 1

The formulation substantially preserves umbrella item 2 and decisions 5, 6,
13, 14, 15, 26, 33, 34 and 39. It correctly leaves orchestration, commits,
tags, consumer adoption and setup with their owning items. No implementation
review or test execution is needed for this specification-only assessment.

Disposition: changes-requested. Q01 to Q13 contain useful decisions, but Q08
does not yet completely bound unsupported workspace arrangements, Q11 needs
to accommodate an already locked lifecycle caller, and missing built-in locks
and historical range-target behavior remain unspecified. These are observable
contracts, beyond wording-only edits. The writer's own note correctly identifies
the body's and AC9's conflict with decision 39.

All thirteen User decision fields are pending. My recommended answers below
are independent reviewer proposals, not human decisions. Preserve that state.
The request's final project-root answer-path instruction is stale: publication
must use the artifact-home path returned by the exchange, via the paired
renderer and publish-answer, never a manually written project-root answer.

### Question verdicts for feature-request version-sources round 1

| Question | Reviewer verdict and preferred answer |
| --- | --- |
| Q01 | Agree, A. Keep direct set a file transition with source guards; release uniqueness and main ordering belong to releasing callers. Distinguish accepted syntax from permission to create a release. Numeric version comparison must be numeric, not string order. |
| Q02 | Agree, A. Repair only drift, succeed without source writes when synchronized, and never stage or commit. Validate the complete applicable set even for a same-target invocation. Operation-lock bookkeeping can still occur; no source writes is the meaningful no-op guarantee. |
| Q03 | Agree, A. Strict unprefixed numeric triplet with optional uppercase SNAPSHOT; optional title/notes for these commands. Historical tag tolerance is a separate input contract. Do not reinterpret this as imposing release-content checks on reads. |
| Q04 | Agree, A. An ahead release-only source makes the entire set fail before source writes; check reports actual/expected drift. A whole-set failure follows the existing atomic contract, so skipping is not a valid implementation of that contract. |
| Q05 | Agree with A's principle, clarify paired locks. A versionless npm manifest may be tool-only; missing/dynamic version under an actual Python project remains a failure. Specify that ignoring a tool-only manifest cannot leave its lock treated as a participating source independently. Malformed present manifests must not be silently reclassified as tool-only. |
| Q06 | Prefer A; largely a clarification of the settled single-anchor scope. B introduces independent releases beyond this effort. An undeclared independent package is external for synchronization, not proof that every dependency on it has a valid version. Preserve the existing external-version rule. |
| Q07 | Prefer A with an explicit eligibility limit. Candidate reporting must obey the same vendor/sample, skipped-directory and nested-repository exclusions as detection. Its con about listing many samples conflicts with that exclusion. Report status as well as path so list continues to identify precisely what set touches. |
| Q08 | Prefer revised A, not the current text unchanged. State support for unambiguous Maven reactor project/internal-parent and literal internal dependency/dependency-management version references, including recursively declared participating modules. Keep external parents and external dependencies unchanged. Explicitly reject unsupported internal property/range forms before source writes. npm/uv workspace member lock entries and local/path/workspace links must be addressed too: rejecting only references 'by version' leaves non-version links and shared workspace locks unbounded. Say whether any participating npm/uv workspace arrangement is rejected in v0.14.0 (recommended bounded A), while independently declared components with independent locks and no internal references remain supported. Identification mechanics stay design work. |
| Q09 | Agree, A. Required file/pattern/form and exactly one captured version, with actionable failures. Distinguish one capture group from exactly one successful version capture; an optional group with no value is not a valid version. Do not generate an absent declared pattern file. |
| Q10 | Prefer qualified A. For supported formats/tool versions and an initially current manifest/lock pair, a version-only transition must preserve ecosystem acceptance. Do not promise that changing root versions repairs unrelated pre-existing dependency drift, a changed resolver environment, or every future ecosystem version. Design/plans select the compatibility evidence; ordinary set must not opportunistically execute installed tools. Preserve the umbrella's explicitly supported regeneration exception rather than making 'never runs these tools' a broader new ban. |
| Q11 | Prefer revised A. Serialize standalone set across reading/capturing originals, complete validation, writes and restoration; locking only the write span allows a stale restoration baseline. A lifecycle already holding the same operation lock must be able to call the primitive under its existing ownership without self-refusal or releasing the lock. Reads create no lock/artifact, but may observe an in-progress transition; do not imply snapshot isolation or that their drift result is a release-readiness guarantee. Interfaces and ownership representation remain design work. |
| Q12 | Prefer A, with recovery evidence prerequisite. Original bytes and existence must remain recoverable before they are overwritten, and failure to prepare required evidence must stop source writes. Distinct incomplete-restoration status names unrestored paths and retained evidence; never announce complete restoration. Storage, retention and interaction with item 5's encompassing transaction are design work. Do not store consumer evidence in the tooling checkout. |
| Q13 | Prefer A, but complete the target contract. An existing release tag's range excludes that target itself as a baseline; HEAD preparation can include a release already at HEAD. Specify eligibility of an explicitly selected unvalidated stable-looking tag, an unknown/non-stable target, first-release behavior and alias handling. The deterministic ancestry algorithm can remain design work; caller-visible target validation cannot. |

Missing question: built-in manifest/lock participation when files are absent or
unsupported. A manifest without a lock, an orphan lock without its participating
manifest, or an existing unsupported lock schema currently has no promised
outcome. The rollback language about pre-existing absence does not answer
whether set creates locks, skips them or refuses.

Suggested question: "Which absent or unsupported built-in manifest/lock pairs
can list/check/set accept?" Option A (recommended): an absent optional lock
does not participate and is never generated; an existing lock must be paired
with an identifiable participating manifest and a supported unambiguous schema,
otherwise fail before source writes; tool-only manifest/lock pairs excluded
under Q05 remain excluded together. Pro: supports unlocked projects without
dependency resolution, and prevents silent omission of an existing release
lock. Con: orphan/unsupported locks need correction. Option B: require a lock
for every participating manifest. Pro: uniform lock-backed releases. Con:
rejects legitimate unlocked projects and adds an umbrella requirement. Option
C: skip any unusable lock with a warning. Pro: tolerant. Con: can report a
successful transition leaving an existing release lock stale. Keep this as a
pending human decision and reconcile the chosen answer with Q05/Q10.

Missing sub-decisions within Q13: recommend ordinary historical targets must
be eligible stable releases, missing/snapshot/other-prerelease/ineligible targets
fail with a diagnostic, no predecessor yields full history through the target,
and same-version aliases on the same commit denote one release boundary while
conflicting commits fail. An alternative allowing unvalidated explicit targets
must explicitly distinguish generation for an owned transaction from selecting
a released historical range. Present consequences and keep the human decision
pending; do not silently fold this policy into a design algorithm.

### Requested changes for feature-request version-sources round 1

Requested changes:

Substantive changes required before convergence:

- Bound supported internal references in the child requirement and in Q08,
  including unsupported workspace locks and local references; fix decision 39
  ownership drift in the body and AC9.
- Make Q11 mutation serialization cover capture/validation and already owned
  lifecycle calls, with honest read-consistency limits.
- Add absent/orphan/unsupported built-in lock participation decisions.
- Complete Q13's explicit target and predecessor contract.
- Qualify Q10 compatibility and regeneration wording; make Q12 recovery
  evidence survive before overwrite; align Q05/Q07 participation descriptions.

Evidence: the exact current specification (body, AC8/AC9/AC11/AC13/AC14 and
Q05/Q07/Q08/Q10-Q13), and umbrella sections "Version sources as plugins",
"Release readiness, lifecycle and recovery", "Snapshot tags are not releases",
"Temporary files move out of the tooling tree" and item 2 acceptance criteria.
No transcript was used as assessment context. No human choice is overridden.

### Writer instructions for feature-request version-sources round 1

Revise the question formulation and proposed answers, preserving all pending
human decisions, then publish a replacement request for independent review.
Do not consolidate this round or implement the engine.

1. Complete Q08 option A's workspace and Maven reference boundary. Correct the
   ownership wording in the body and AC9: the requirement states the boundary;
   the design chooses identification and mutation mechanisms. The proposed
   concrete boundary remains a pending user choice, so label it as proposed.
2. Amend Q11 A to cover baseline capture/validation under mutation ownership
   and primitive reuse by an already locked release caller. State the limits
   of unlocked reads without adding a reader lock requirement.
3. Add the missing manifest/lock-pair question with materially distinct options,
   pros/cons and a proposed answer. Reconcile it with Q05's tool-only exclusions
   and Q10's supported consistency guarantee.
4. Expand Q13's options/answer to settle historical-target eligibility, first
   release, exclusion of the target as its own predecessor, and aliases. Leave
   deterministic ancestry implementation and persistent eligibility evidence
   to the design, as the umbrella requires.
5. Qualify Q10's ecosystem guarantee and preserve the explicitly supported
   regeneration exception. Strengthen Q12's evidence-before-overwrite behavior.
   Resolve Q07's sample-listing inconsistency. Keep Q01-Q04/Q06/Q09's preferred
   A answers as reviewer-supported proposals, not confirmed decisions.
6. Update affected acceptance criteria or explicitly identify their pending
   proposed additions so the next reader can trace each proposed rule. Remove
   the stale project-root answer-path instruction from future authored request
   prose if its calling adapter allows that correction; protocol paths always
   come from the exchange regardless.

### Final reviewer decision for feature-request version-sources round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-03T21:00:01+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
Review round: 2

### Requestor assessment for feature-request version-sources (round 2)

Writer assessment of the version-sources feature request, round 2.

Every round 1 instruction was applied; no recommendation was declined. The
question set now holds Q01 to Q14, each with a recommended option and a
pending user decision. No decision was recorded or inferred: all fourteen
`User decision: pending` lines remain, and reviewer-supported answers are
still proposals.

- Q08 option A now states the proposed boundary in full: reactor project
  versions, internal parents, literal internal dependency and
  dependency-management versions including recursively declared modules;
  rejection of unsupported internal property and range forms; rejection of any
  participating npm or uv workspace arrangement, including workspace locks,
  member entries and local `file:`, `link:`, path or workspace links; support
  for independently declared components with their own locks and no internal
  references. It is labeled as the proposed boundary.
- The body and AC9 now say this requirement states the boundary (proposed in
  Q08) and the design chooses identification and change mechanisms.
- Q11 option A covers the whole standalone `set` span (capture, validation,
  writes, restoration), reuse by a lifecycle caller already holding the lock,
  and the limits of unlocked reads.
- Q14 is new: absent optional locks, orphan locks and unsupported lock schemas,
  reconciled with Q05 (tool-only pairs excluded together) and Q10 (guarantee
  for supported pairs only).
- Q13 option A now settles target validity, the target never being its own
  predecessor, first-release behavior and aliases; option D adds the
  owned-transaction alternative so its consequences are visible.
- Q10 option A is qualified to previously accepted pairs and supported tool
  versions, and keeps the requirement's explicit regeneration exception.
- Q12 option A requires recovery evidence before the first overwrite and
  stops before any write when it cannot be prepared.
- Q05 adds the paired-lock and malformed-manifest rules; Q07 limits
  candidates to the detection exclusions and reports status with path; Q01,
  Q02, Q03, Q06 and Q09 carry the reviewer's clarifications.
- A new traceability table after the acceptance criteria maps each pending
  question to the criteria it would refine.

The writer considers the specification ready for convergence, with the
fourteen human decisions outstanding. Please check the amended questions and
the body changes, and whether any further question is missing.

### Change summary for feature-request version-sources (round 2)

Changes to `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` since
round 1:

- Body, "Version-only writes, locks and internal references": the last
  sentences now say the requirement states the supported boundary, proposed in
  Q08 and pending a user decision, and the design chooses how references are
  identified and changed.
- AC9 now refers to the boundary this requirement states (proposed in Q08).
- After the acceptance criteria: a new table maps Q01 to Q14 to the criteria
  each would refine once decided.
- Open questions: Q01, Q02, Q03, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q12 and Q13
  amended as listed in the assessment, each with a short "after review round
  1" note in its recommendation; Q04 unchanged; Q14 added. Question IDs,
  existing options and pending decisions are preserved; Q13 keeps options A to
  C and gains option D.
- No other body section changed; the umbrella and the child draft are
  unchanged.

### Writer response for feature-request version-sources (round 2)

Writer response:

All six round 1 writer instructions were accepted and applied, with no
disagreement:

1. Q08 option A completed and labeled as the proposed boundary; body and AC9
   corrected to the decision 39 ownership split.
2. Q11 option A amended for the full capture-to-restoration span, reuse by an
   already locked lifecycle caller and the limits of unlocked reads, with no
   reader lock requirement.
3. Q14 added with three distinct options, reconciled with Q05 and Q10.
4. Q13 expanded: target eligibility, self-predecessor exclusion, first release
   and aliases in option A, plus option D for the owned-transaction
   alternative. Ancestry and persistent eligibility evidence stay with the
   design.
5. Q10 qualified with the regeneration exception preserved; Q12 requires
   evidence before overwrite; Q07's sample-listing inconsistency removed (its
   option C con was adjusted the same way). Q01 to Q04, Q06 and Q09 keep their
   A answers as proposals.
6. The new traceability table identifies which criteria each pending question
   would refine.

About the stale project-root answer path: that sentence is generated by the
paired request renderer, not authored by the writer, so this round cannot
remove it. The exchange's returned artifact-home paths remain authoritative.

Tooling note: the instruction describes `oqm --append` as replacing the
section, but the tool only appends. The first amended append duplicated the
section; the writer then ran `--strip` and `--append` once with the complete
preserved-and-amended companion, so the document holds one section with all
fourteen questions.

### Reviewer focus for feature-request version-sources (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-03T21:03:54+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request version-sources round 2

I independently reviewed the complete current feature request, its fourteen
open questions and the validated round-2 request against the umbrella's
version-source, internal-reference and release-range contracts. I did not use
the versioned review transcript as assessment context.

The six substantive round-1 instructions are addressed. Q08 now bounds the
proposed supported references and rejects participating npm/uv workspaces,
their shared locks and local links rather than allowing silent partial
updates. Requirement ownership of that boundary is explicit in the body and
AC9; identification and mutation mechanics remain design work. Q11 covers
capture through restoration under mutation ownership and reuse by an already
locked lifecycle caller. Q14 closes the absent/orphan/unsupported lock gap.
Q13 covers historical targets, eligibility, first releases, self-predecessor
exclusion and aliases. Q10 limits compatibility honestly and preserves the
explicit regeneration exception. Q12 requires recoverable originals before
overwrite. Q05/Q07 participation wording and the criterion traceability table
are consistent with these refinements.

No additional in-scope question or substantive disagreement remains. Options
and proposed answers are sufficient for the human decision phase. Agreement
with their formulation does not authorize implementation or consolidation:
all fourteen User decision fields remain pending.

The request's project-root answer sentence is a renderer defect already
identified by the requestor. Publication follows the protocol-returned
artifact-home paths. This external wording defect does not block convergence
of the reviewed specification.

### Question verdicts for feature-request version-sources round 2

All questions are relevant, sufficiently clear and within this requirement's
scope. None is missing or redundant. Their options express distinct policies
and relevant tradeoffs. I would choose option A for Q01 through Q14, as
reviewer recommendations only:

| Question | Reviewer verdict and reason |
| --- | --- |
| Q01 | A: keep the shared set primitive independent of release preflights, with numeric comparisons and source guards. B prevents legitimate corrections; C couples file transitions to release policy. |
| Q02 | A: validate the complete applicable set, repair only drift and write no version source for a true no-op; staging and commits belong to callers. B creates churn; C defeats reruns. |
| Q03 | A: a strict anchor token gives deterministic mappings while release-content validation remains with the lifecycle. B changes accepted notation; C blocks fresh projects. Historical tags retain their separate classification contract. |
| Q04 | A: a downgrade refusal stops the whole transition before writes, preserving atomicity. Skipping or overriding weakens that contract. |
| Q05 | A: exclude identifiable tool-only manifests and their locks together, visibly; malformed manifests and real Python projects without static versions fail. This avoids false failures without guessing. |
| Q06 | A: every participating component follows one anchor; independent releases remain outside participation. Exclusion leaves external references untouched without asserting validity. Multiple anchors or fixed versions expand scope. |
| Q07 | A: expose eligible undeclared candidates without adopting them or failing mutation. Applying detection exclusions removes the earlier sample contradiction. Silent exclusion hides omissions; mandatory classification adds scope. |
| Q08 | A: recursive Maven project/internal-parent references and literal internal dependency/dependency-management versions cover the stated need. Unsupported property/range forms and all participating npm/uv workspace arrangements, shared locks and local links fail before writes. Independent declared components with separate locks and no internal references remain supported. Broader workspace support is premature; parent-only support misses common reactors. |
| Q09 | A: require all declaration keys, an existing file and exactly one successful nonempty version capture. This catches moved files and empty optional captures rather than silently dropping a declared source. |
| Q10 | A: preserve tool acceptance for previously valid supported pairs and supported tool versions, without promising dependency repair or future-tool compatibility. Keep the explicitly supported regeneration exception. Field edits alone are insufficient; opportunistic live tool checks change runtime dependencies. |
| Q11 | A: hold mutation ownership from original capture through restoration, reuse an owning lifecycle caller's lock and state unlocked reads' consistency limits. Reader locking adds unnecessary contention; lifecycle-only locking leaves direct set calls unsafe. |
| Q12 | A: prepare recoverable originals before overwrite, stop if preparation fails, and distinguish incomplete restoration with retained originals and precise diagnostics. Reporting paths alone loses evidence; retries alone do not define a safe terminal result. |
| Q13 | A: share HEAD and eligible historical-target selection, exclude a historical target as its predecessor, include full history for a first release and treat same-commit aliases as one boundary while rejecting conflicts. Separate selectors duplicate policy; an unvalidated owned target has no demonstrated caller. |
| Q14 | A: absent optional locks stay absent; existing participating locks require identifiable manifests and supported unambiguous schemas; Q05 excludes tool-only pairs together. Requiring every lock exceeds scope, while skipping unusable existing release locks risks stale versions. |

Every recommended answer follows the confirmed umbrella constraints or
explicitly presents a refinement for the human to choose. Q01-Q14 all still
require explicit human decisions. A different human choice or conditional
comment may require a further consistency review.

### Convergence evidence for feature-request version-sources round 2

Covered wording:

The covered formulation is the complete current feature request, including
the revised internal-reference ownership text, AC9, the pending-question
traceability table and Q01-Q14 with their options and proposed A answers.
No replacement wording is required for convergence. The proposed support
boundary is the bounded Q08 A formulation, not an authorization for a design
to expand support implicitly. All human-decision markers remain pending.

Convergence rationale:

Recommend convergence of the reviewed formulation. The prior substantive
gaps are closed, the options and consequences support informed human
decisions, and no missing in-scope question or cross-document contradiction
requires another formulation round. Implementation mechanisms and evidence
organization are correctly reserved for design and plans.

This is advisory reviewer agreement only. Q01-Q14 remain pending human
choices, and consolidation requires the separate human choice owned by the
requestor workflow.

### Writer instructions for feature-request version-sources round 2

No substantive revision or additional automated formulation round is required.
Present Q01-Q14 for explicit human decisions and preserve their pending state
until the human answers. Do not consolidate, mark recommendations confirmed,
or begin implementation on the authority of this review.

After decisions are recorded, reconcile their consequences across the body,
acceptance criteria and related scope through the owning workflow. Changed
choices or conditional comments require the appropriate follow-up consistency
review. Publish requests using the shared exchange; its returned paths remain
authoritative despite the renderer's project-root sentence.

### Final reviewer decision for feature-request version-sources round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-05T07:47:14+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-05T07:55:32+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request version-sources (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
Review round: 3

### Requestor assessment for feature-request version-sources (round 3)

Writer assessment of the version-sources feature request, round 3: follow-up
review of the human decisions recorded after the round 2 convergence.

Round 2 converged with Q01 to Q14 pending. The user then went through every
question, one at a time, and chose option A, as recommended, for all fourteen,
with no comment (Q01 to Q04 on 2026-11-03, Q05 to Q14 on 2026-11-04). Each
choice is recorded as a `User decision: confirmed - Option A, as recommended:
...` line in that question's answer section. The decision scan reports 14
confirmed, 0 undecided and no diagnostics. The round 2 convergence covered the
document with pending decisions, not these choices, so this round reviews them.

The writer found no missing question and considers the options and recorded
answers sufficient. The writer proposes no change to a decided question. The
round 2 reviewer instructions asked only for the human decision phase; there
was no wording suggestion to apply.

Points the writer asks the reviewer to check, without reopening a choice:

- Wording that still presents a decided question as open, left for
  consolidation because the explanation phase edits only answer sections:
  the body section "Version-only writes, locks and internal references" says
  the Q08 boundary "remains a pending user decision" (around line 237); AC9
  says "(proposed in Q08)"; the sentence before the traceability table says
  the questions "remain pending user decisions" and refine the criteria "once
  decided" (around line 398). The Q08 option A label "(proposed boundary)" is
  option text and stays until consolidation. Please report any other passage
  of this kind.
- Workspace wording against Q08: the same body section says the contract
  "applies to supported participating workspace packages" and their lock
  files, while the Q08 decision rejects every participating npm or uv
  workspace arrangement in v0.14.0. The writer reads this as: no workspace
  arrangement is supported in this version, and consolidation should say so.
  The "Participation and detection of ecosystems" section also says
  independent workspace packages "need explicit configuration"; under the Q06
  decision they are simply not declared and never touched.
- Maven property forms: the body says "Supported reactor version properties
  are handled explicitly; others are rejected" (around line 217), AC6 rejects
  "unsupported Maven property indirection", and the child draft has the same
  wording. The Q08 decision supports literal versions and rejects "unsupported
  property or range forms", but names no supported property form. The writer
  reads Q08 A as supporting no property form in v0.14.0. Please say whether
  that reading conflicts with the body, AC6, the child draft or the umbrella,
  and whether it needs a new question rather than a consolidation edit.
- Scope of the Q14 lock rule against Q07: Q14 makes an existing lock without
  an identifiable participating manifest fail `list`, `check` and `set`, while
  Q07 says an undeclared nested candidate is listed as not participating and
  never fails. The writer reads Q14 as covering only the root and declared
  component roots. Please confirm, or name the case where they collide.
- Cross-question effects to confirm: Q01 (any valid target, numeric
  comparisons, uniqueness with items 5 and 7) with the uniqueness rule section
  and AC15; Q02 (same-target no-op, lock bookkeeping allowed) with Q11 and
  Q12; Q04 (whole-transition refusal) with Q02 and AC7; Q05 and Q14 (tool-only
  pairs excluded together); Q11 (read commands take no lock and create no
  artifact) with AC1 and Q12 (recovery evidence in the consuming project's
  artifact home, only for `set`); Q13 (HEAD baseline possibly at HEAD itself,
  target never its own predecessor) with the tag classification section and
  AC13 and AC14.

Reviewer recommendations cannot overwrite these human choices. Where a
decision conflicts with another decision, the body, the criteria, the umbrella
or the child draft, please name the conflict and the passages involved, and
state whether it needs a new question for the user or only a consolidation
edit.

### Change summary for feature-request version-sources (round 3)

Changes to `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` since
the round 2 convergence answer (2026-11-03T21:03:54+01:00):

- Open questions Q01 to Q14: each `User decision: pending` line now reads
  `User decision: confirmed - Option A, as recommended: ...`, restating the
  chosen option's outcome and the decision date, with no further comment.
  Every choice equals the proposed answer A.
- No other change: question descriptions, options, pros and cons,
  recommendations, proposed answers, the body, the acceptance criteria and the
  traceability table are unchanged. The stale wording listed in the assessment
  is deliberately left for consolidation.
- The umbrella `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md` and the
  child draft `docs/v0.14.0/draft.v0.14.0.version-sources.md` are unchanged.

### Writer response for feature-request version-sources (round 3)

Writer response:

Response to the round 2 writer instructions:

1. Q01 to Q14 were presented to the user one at a time, each with an
   explanation, and their pending state was kept until the user answered.
   All fourteen decisions are now recorded as explicit user choices; none was
   inferred from the proposed answers or from reviewer agreement.
2. Nothing was consolidated. No question block was removed or replaced, and
   no recommendation was marked confirmed on the authority of the review.
   Implementation has not started.
3. Reconciling the decisions across the body, the acceptance criteria and the
   related scope belongs to the owning workflow, consolidation, which needs a
   separate human choice. The passages it must update are listed in the
   assessment so this round can check them and find any others.
4. Since every choice equals its recommended option and no comment was given,
   the writer does not expect a conflict, but asks for this round because the
   round 2 convergence did not review the decisions themselves.

About the project-root answer path sentence in the generated request: it is
still produced by the paired renderer, not authored by the writer. The paths
returned by the exchange remain authoritative.

### Reviewer focus for feature-request version-sources (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-05T08:03:39+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request version-sources round 3

I read the complete current requirement and validated round-3 request, the focused draft, and the relevant umbrella contracts, including decisions 33, 34 and 39. The request accurately describes fourteen explicit Option A decisions. I preserve every one of those decisions. There is no literal Human guidance block requiring a separate response.

One substantive scope decision is still missing: the exact Maven property support boundary. Q08 A names literal dependency/dependency-management versions but says only that property and range forms "that the requirement does not support" fail. Its confirmed decision repeats "unsupported property or range forms". Neither passage defines which property forms are supported. The body at lines 217-218 says "Supported reactor version properties are handled explicitly; others are rejected"; AC6 says "unsupported Maven property indirection". These formulations do not establish that every version property is unsupported, especially for reactor project/parent versions, which Q08 does not explicitly limit to literals. A reactor using ${revision} or an internal dependency using ${project.version} therefore has no unambiguous supported/refused outcome.

The focused draft's "Handle supported reactor version properties explicitly or reject them" and umbrella lines 1008-1009 permit a bounded rejection policy; they do not choose one. Decision 39 deliberately leaves the concrete supported boundary to the child requirement. Thus rejecting all properties is compatible with the parent scope, but it cannot be silently attributed to the user's Q08 decision. This is a new question for the human, not a consolidation edit or a design mechanism. No other new question is needed.

The workspace wording is different: Q08 explicitly rejects every participating npm/uv workspace arrangement and local link between participating components. That decision supplies the missing boundary and is consistent with the umbrella's conditional promise for *supported* workspaces. The body at lines 231-237 and AC9 need to express that decided boundary during authorized consolidation. Independent components with separate locks and no internal references remain supported; independently released packages remain undeclared under Q06. An undeclared member does not make an otherwise participating shared workspace supported.

Q14 is scoped by participation. At the project root and explicitly participating component roots, an existing lock without an identifiable participating manifest fails. Tool-only manifest/lock pairs are excluded together under Q05. An orphan or unsupported lock solely inside an undeclared nested candidate does not activate Q14: Q07 excludes that candidate from validation and mutation and reports it as not participating in list. A shared workspace lock belonging to a participating root remains subject to Q08/Q14 even if some members are undeclared. This is a scope clarification following existing decisions, not a new choice.

Q01/Q04 keep numeric source guards separate from release uniqueness/order, so direct set can correct an anchor but cannot bypass release-only refusal. Q02 still validates a same-target set and Q04 still refuses a downgrade before any source write. Q11 permits lock bookkeeping for set, including a same-target operation; its read commands create no artifacts. Q12 requires recoverable originals before the first overwrite, not an overwrite on a no-op, and its evidence belongs to the consumer. Q13's HEAD baseline may equal HEAD; only a release-tag target excludes its own release boundary as predecessor, including alias spellings. These decisions are mutually consistent and retain AC1, AC7, AC11, AC13-AC15 and the umbrella's ownership boundaries.

The remaining pending/proposed wording is consolidation debt, not evidence that the fourteen human decisions are absent: requirement lines 237-238, AC9, and lines 397-398 are the stale passages identified in the request. Q08's option label is historical option text. Question descriptions/recommendations remain explanatory history until the authorized workflow removes the question section. AC10/list must also gain the decided non-participating statuses from Q05/Q07, and the other criteria must absorb their decided refinements. Those integrations need no new human choice. The property boundary must be settled first.

### Question verdicts for feature-request version-sources round 3

| Question | Verdict and reviewer answer |
| --- | --- |
| Q01 | Agree with confirmed A. Any syntactically valid target reaches source-level validation; numeric comparison prevents lexicographic mistakes. Release preflights retain uniqueness/order enforcement. Distinct options, no missing decision here. |
| Q02 | Agree with confirmed A. Same-target set validates first, repairs drift only, writes no source on a clean no-op, and never stages/commits. Operation-lock bookkeeping is consistent with Q11 and recovery evidence before actual overwrite with Q12. |
| Q03 | Agree with confirmed A. Strict bare token grammar and optional title/notes keep version commands usable; release-content checks belong to item 5. Historical tag recognition stays separate. |
| Q04 | Agree with confirmed A. Whole-set refusal preserves atomicity and remains applicable on a same-anchor drift-repair run. Check reports the ahead source as drift. No override is required. |
| Q05 | Agree with confirmed A. Tool-only pairs are visible but excluded together, while malformed manifests and invalid Python project versions fail. Q14 explicitly preserves this exception. |
| Q06 | Agree with confirmed A. Participating components share one anchor in their forms. Independently released packages and references to them retain the stated external-version rule; this grants no workspace support contrary to Q08. |
| Q07 | Agree with confirmed A. Report eligible undeclared candidates without validating or modifying their sources/locks. This participation scope resolves the apparent Q14 collision. |
| Q08 | Preserve confirmed A and agree with its explicit literal Maven dependency support, recursive reactors, external-version preservation, and npm/uv workspace/local-link rejection. The property part is incomplete: 'unsupported' never defines the supported forms. Do not change the confirmed choice or interpret it as an explicit rejection of all properties. Add the focused follow-up question below. |
| Q09 | Agree with confirmed A. Required keys, an existing file and exactly one nonempty captured version give a concrete fail-before-write rule. Design owns syntax/mechanics. |
| Q10 | Agree with confirmed A. Preserve ecosystem acceptance for previously accepted supported pairs, without promising repair of pre-existing drift or opportunistic tool execution. The qualified regeneration exception is retained. |
| Q11 | Agree with confirmed A. The mutation lock spans capture through restoration and is reused by an owning lifecycle caller. Artifact-free unlocked reads explicitly allow observation during a transition. |
| Q12 | Agree with confirmed A. Prepare recoverable originals before overwrite; distinguish incomplete restoration and retain named consumer-local originals. Storage/retention mechanisms remain design work. |
| Q13 | Agree with confirmed A. HEAD and eligible historical-tag targets share classification but differ in self-baseline treatment; aliases represent one boundary and conflicting commits fail. No new eligibility mechanism is prescribed. |
| Q14 | Agree with confirmed A. Optional absent locks stay absent, malformed participating pairs fail, and tool-only pairs remain excluded. Apply only after participation filtering, so undeclared candidate locks do not become blockers. |

All existing questions have materially distinct options and relevant consequences. None should be removed or reopened in this review. The reviewer would choose A for each existing question, but Q08's conditional property wording does not settle the missing concrete boundary. The fourteen recorded choices are human decisions; the following recommendation is not.

Suggested Q15: Which Maven version property forms are supported in v0.14.0?

Question: Q08 specifies literal internal dependency versions and rejects unsupported property/range forms, while the body promises handling of supported reactor version properties. For participating project versions, internal parent versions and internal dependency/dependency-management versions, is any property indirection supported? Keep Q08's other boundaries unchanged.

- Option A (recommended): support literal Maven version values only, retaining inherited project versions as inherited; reject property expressions in participating project versions and internal parent/dependency/dependency-management version references before any source write, naming the file, field/expression and limitation. External versions/properties stay unchanged, as already required. No Maven property or range form is added to the supported boundary in v0.14.0.
  - Pro: closes the smallest supported boundary without inventing a property-resolution model; compatible with the umbrella's explicit-reject alternative.
  - Con: common ${revision} and ${project.version} reactor layouts need manual literal conversion or a later support increment; this consequence must be explicit before the user chooses it.
- Option B: also support a precisely enumerated set of property forms, requiring the question to name each expression, its allowed locations/definition scope and expected ownership behavior; reject all others.
  - Pro: can retain common CI-friendly reactors and sibling references without literal conversion.
  - Con: expands the supported contract and needs additional boundary decisions about aliases, external property consumers and ambiguous definitions. Merely saying 'unambiguous properties' leaves this review defect unresolved.

Reviewer proposed answer: A, for the smallest explicit initial boundary. User decision: pending. Do not record the proposal as confirmed. If consumer evidence already requires a property form, describe it in B before presenting the question rather than silently excluding that consumer.

### Requested changes for feature-request version-sources round 3

Requested changes:

Required before convergence: add Q15 to close the undefined Maven property support set. Q08's phrase 'unsupported property or range forms', body lines 217-218 and AC6 allow incompatible supported/refused outcomes for ${revision} project versions and ${project.version} internal references. The requestor's proposed 'no property support' reading is a reasonable new recommendation but is not an explicit recorded human decision.

Keep all fourteen confirmed decisions. Add complete options, consequences, a reviewer/writer recommendation and a pending user decision for the new question, then request another review. This is substantive requirement scope, so changes-requested applies. Ordinary integration of already confirmed choices remains deferred to separately authorized consolidation; it is not requested as a prerequisite for the next round.

### Writer instructions for feature-request version-sources round 3

Preserve the confirmed Q01-Q14 decisions verbatim in meaning. Do not consolidate, remove the questions, or implement the feature on the authority of this answer.

Add one focused follow-up question, Q15, defining the Maven property boundary. Use the proposed wording/options in the verdicts as a starting point, retain a pending user decision, and explain the consequence for ${revision}/${project.version}. In particular, do not change Q08's recorded user choice into 'all properties rejected' without this explicit follow-up decision. Ensure the question covers project, internal parent and internal dependency/dependency-management version fields, preserves inherited project versions and external versions, and distinguishes a support policy from resolution mechanisms that belong to design.

Publish the amended specification for another automated review round. The next review can assess the new question's completeness before a separate human explanation/decision phase. No existing confirmed choice needs to be asked again.

At a later authorized consolidation, reconcile the already decided workspace boundary, participation-first lock scope, same-target validation/no-op, numeric guards, unlocked reads, recovery evidence and range targets into the body/criteria. Remove the pending/proposed claims at lines 237-238, AC9 and lines 397-398 then. The historical focused draft/umbrella permit this bounded support policy; they do not mandate an additional property form. Do not rewrite either parent as though an unmade property decision were confirmed. A substantive property expansion beyond the selected boundary would need corresponding scope reconciliation.

### Final reviewer decision for feature-request version-sources round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-05T08:13:11+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request version-sources (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
Review round: 4

### Requestor assessment for feature-request version-sources (round 4)

Writer assessment of the version-sources feature request, round 4.

The round 3 requested change is applied: Q15, "Maven version property forms
supported in v0.14.0", closes the undefined Maven property boundary. Q01 to Q14
keep their confirmed user decisions unchanged; the decision scan reports 15
questions, Q01 to Q14 confirmed, Q15 `pending-user-decision`, no diagnostics.

Q15 covers the participating project version, the internal `<parent>` version
and the internal dependency or dependency-management version. It restates
that inherited project versions stay inherited, ranges stay rejected and
external versions and properties stay unchanged, as Q08 decided, and leaves
identification to the design. It names the consequence for `${revision}` and
`${project.version}` in every option.

Consumer evidence, checked for this round: the only Maven consumer, my-project,
states a literal version in its root POM and a literal `<parent>` version in
its one module. `${project.version}` appears there only inside a plugin
configuration value, not in a version field, and its plugin versions use
properties that are external versions. No consumer requires a property form,
so option C is described with that consequence, as the reviewer asked.

The writer's recommendation differs from the reviewer's proposed answer on
one point. Option A, the reviewer's proposal, is kept as written: literal
values only. Option B adds `${project.version}` as the whole value of an
internal dependency or dependency-management version. Under the confirmed
Q06 decision every participating component takes the anchor's version, so
that expression always resolves to the transition's version: it needs no write
and cannot go stale. Rejecting it would fail reactors that are already
consistent and push users to replace a self-maintaining reference with
literals the engine must then rewrite. B still resolves and rewrites no
property, which keeps Q08's literal-write boundary. The writer recommends B
and asks the reviewer to test that argument, in particular whether
`${project.version}` in a dependency-management entry of the root POM, or in a
module whose version is inherited, can resolve to anything other than the
shared version within the participating reactor.

No other question is missing, in the writer's view. The stale wording listed
in round 3 and the integration of the confirmed decisions remain deferred to
consolidation, as the round 3 answer agreed. The Q14 participation scope the
reviewer confirmed in round 3 (lock rule applied only after participation
filtering) is likewise left for consolidation and was not edited into Q14.

Please assess Q15's completeness and options, the B recommendation against
the reviewer's A proposal, and whether Q15 conflicts with Q06, Q08, AC6, AC9,
the body's Maven sentences, the child draft or the umbrella. The fourteen
confirmed decisions stay as the user recorded them.

### Change summary for feature-request version-sources (round 4)

Changes to `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` since
round 3:

- Open questions: Q15, "Maven version property forms supported in v0.14.0",
  added after Q14 with a description, a BBQ, options A (literal versions
  only), B (literal versions plus `${project.version}` as an internal
  dependency or dependency-management version) and C (B plus root-POM
  `${revision}` CI-friendly versions), a recommendation for B, a proposed
  answer B and `User decision: pending`.
- Traceability table: new row mapping Q15 to AC6 and AC9.
- No other change: Q01 to Q14, including their confirmed decisions, the body
  and the acceptance criteria are unchanged. The umbrella and the child draft
  are unchanged.
- Markdown check after the edit: exit 0, no findings.

### Writer response for feature-request version-sources (round 4)

Writer response:

Response to the round 3 writer instructions:

1. Q15 was added to settle the Maven property boundary, with a pending user
   decision. It covers project, internal `<parent>` and internal dependency or
   dependency-management version fields; it keeps inherited project versions
   and external versions unchanged; it separates the support policy from
   identification, which stays with the design; and every option states its
   consequence for `${revision}` and `${project.version}`.
2. Q08's recorded user choice was not changed and was not read as "all
   properties rejected". Q01 to Q14 were not asked again or edited.
3. Nothing was consolidated, no question was removed and implementation has
   not started.
4. The reviewer's suggested Q15 wording was the starting point. Its option A
   is kept; its option B, an enumerated property set, became two concrete
   options: B, accepting only `${project.version}` in internal dependency and
   dependency-management versions, and C, adding root-POM CI-friendly
   versions. The consumer evidence the reviewer asked for is in the
   assessment: no consumer needs a property form.
5. The writer recommends B rather than the reviewer's proposed A, for the
   reason given in the assessment. This is a proposal for the human, not a
   rejection of a requested change; every requested change was applied, so
   the round is not flagged as a disagreement. If the reviewer finds a case
   where B's expression does not resolve to the shared version, the writer
   will change the recommendation to A.
6. The consolidation items listed in the round 3 answer (decided workspace
   boundary, participation-first lock scope, stale pending wording at the
   lines named, and the other decided refinements) remain deferred to an
   authorized consolidation.

### Reviewer focus for feature-request version-sources (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-05T08:20:03+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request version-sources round 4

The round 3 missing decision is now expressed as Q15. No additional question is required for the proposed option B boundary. The question distinguishes project versions, internal parent versions and internal dependency/dependency-management versions, preserves inherited versions and external fields, and explicitly rejects other property expressions before mutation. Q01-Q14 retain their confirmed human decisions.

I agree with the writer's option B recommendation. My round 3 option A was a proposed conservative boundary, not a human decision or a requirement to reject every property. Whole-value `${project.version}` in an internal dependency version refers to the owning Maven project's effective version. In the supported reactor, Q06 supplies one release version and AC7 supplies the Maven suffix form. A root dependency-management entry therefore follows the root's version; a module whose project version is inherited follows its internal parent's version. Whether interpolation occurs in the parent or the child does not change the result when these participating Maven versions have the same expected value. No property definition needs rewriting. A mixed-version or otherwise unsupported arrangement is not licensed by this exception: Q06 and AC9 still apply.

This reasoning concerns the supported source model, not arbitrary Maven invocations, external BOM consumers, externally supplied overrides or property-driven project coordinates. The exception does not admit `${revision}`, property-based project or parent version fields, composite expressions, or custom version properties. Existing preflight and ambiguity rules remain in force.

The distinction fits Q08's confirmed rejection of unsupported property forms, AC6's corresponding failure rule, AC9's internal-reference consistency promise, and the body/drafts' requirement to handle supported properties explicitly or reject them. No cross-document scope change is necessary. The consumer evidence reported in the request is consistent with B but does not require it; the reason for B is its bounded, self-maintaining reference behavior. No independent consumer execution or Maven integration test was performed for this specification review.

Only wording and the already deferred authorized consolidation remain. This is advisory convergence on the formulation, not a human answer to Q15 or authorization to consolidate.

### Question verdicts for feature-request version-sources round 4

| Question | Verdict and reviewer choice |
| --- | --- |
| Q01 | Preserve confirmed A: numeric downgrade guard and release uniqueness have separate owners. |
| Q02 | Preserve confirmed A: same-target transitions validate and repair drift, with no source write when already clean. |
| Q03 | Preserve confirmed A: anchor parsing and malformed-input handling remain as decided. |
| Q04 | Preserve confirmed A: a forbidden downgrade refuses the whole transition. |
| Q05 | Preserve confirmed A: tool-only Python metadata and its lock remain excluded together. |
| Q06 | Preserve confirmed A: one project version, applied in each supported source form; independent releases stay outside participation. |
| Q07 | Preserve confirmed A: report eligible undeclared candidates without synchronizing them. |
| Q08 | Preserve confirmed A: bounded recursive Maven reactor support, with participating npm/uv workspaces and local links rejected. Q15 defines the formerly unnamed property boundary. |
| Q09 | Preserve confirmed A: pattern-source declarations and required files remain validated as decided. |
| Q10 | Preserve confirmed A: supported version-only writes retain unrelated bytes and lock data. |
| Q11 | Preserve confirmed A: mutation is locked; read-only operations remain artifact-free. |
| Q12 | Preserve confirmed A: recoverable consumer-local originals precede source overwrites. |
| Q13 | Preserve confirmed A: baseline eligibility at HEAD remains distinct from release-target uniqueness, including tag aliases. |
| Q14 | Preserve confirmed A: optional absent locks are not generated; participating existing locks need supported, identifiable pairs. Apply participation filtering first, including Q05/Q07 exclusions. |
| Q15 | Complete and in scope; choose B. A is a valid conservative alternative but needlessly rejects a whole-value internal `${project.version}` reference. B names the sole accepted property expression and every covered field, without requiring property rewrites. C is a broader future direction whose additional boundary decisions are explicitly acknowledged; it is not implementation-ready on its present sketch if selected. Q15 remains pending human decision. |

The Q15 options are materially distinct and state the relevant costs. The proposed answer B is consistent with confirmed Q06/Q08. No confirmed decision is reopened or replaced.

### Convergence evidence for feature-request version-sources round 4

Covered wording:

Coverage includes the complete current feature request and round 4 request, especially Q15's description, options, recommendation and proposed B answer; its interaction with confirmed Q06/Q08 and Q14 participation filtering; AC6/AC7/AC9; and the previously reviewed focused and umbrella scope.

The accepted formulation supports literals and whole-value `${project.version}` only in internal dependency/dependency-management version fields, leaves that expression untouched, preserves inherited project versions, and rejects other property forms in the covered version fields before writes. External version fields and properties remain outside this rewrite boundary. No additional unresolved decision was identified for option B. Previously identified body/criteria integration is deferred to authorized consolidation.

Convergence rationale:

Recommend convergence of the reviewed formulation. Q15 closes the only missing requirement decision identified in round 3. Its proposed B answer is bounded, consistent with the confirmed single-version Maven reactor and internal-reference contract, and requires no new property rewrite policy. The writer's explanation resolves the earlier conservative recommendation without overriding a human choice. Remaining suggested edits clarify wording only.

Outstanding human choice: Q15, currently pending. Q01-Q14 are confirmed. Reviewer agreement neither records Q15 as decided nor authorizes consolidation. This recommendation covers B; choosing the broader C would require the follow-up decisions C itself identifies.

### Writer instructions for feature-request version-sources round 4

No substantive revision or further automated round is requested for this formulation. Leave Q15 pending until the human selects an answer. Preserve Q01-Q14 and their decision records. Do not consolidate or implement on the strength of this recommendation.

Optional wording polish for Q15 option B: "In a supported reactor, `${project.version}` is accepted only as the entire internal dependency or dependency-management version. It stays unchanged and follows the owning project's effective Maven version, which is the same expected Maven version as the participating target module. All participating project and internal parent version fields remain literal or inherited as applicable; every other expression in the covered fields is rejected before mutation."

This merely makes the shared supported-version premise explicit; it adds no new form policy. Root dependency management and inherited module versions do not require an additional question. Identification and validation mechanisms remain design work.

At a separately authorized consolidation, integrate the chosen Q15 boundary into the Maven body and AC6/AC9 alongside the already confirmed decisions. Retain the earlier consolidation reminders: state the decided workspace rejection, apply lock rules only after participation filtering, and replace stale pending/proposed wording. If the human instead selects C, its expressly deferred boundary decisions need follow-up before design proceeds.

### Final reviewer decision for feature-request version-sources round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-05T08:53:04+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-05T08:54:23+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request version-sources (round 5)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
Review round: 5

### Requestor assessment for feature-request version-sources (round 5)

Writer assessment of the version-sources feature request, round 5: follow-up
review of the human decision on Q15 recorded after the round 4 convergence.

Round 4 converged with Q15 pending. The user then received the Q15
explanation and chose option B, as recommended, with no comment
(2026-11-05T08:50). The decision is recorded as `User decision: confirmed -
Option B, as recommended: ...` in Q15's answer section. The decision scan now
reports 15 questions, all confirmed, 0 undecided and no diagnostics. Q01 to
Q14 keep the decisions the user recorded on 2026-11-03 and 2026-11-04, which
rounds 3 and 4 already reviewed.

The recorded Q15 decision states: participating project versions and internal
`<parent>` versions are literal or inherited; `${project.version}` is accepted
only as the entire internal dependency or dependency-management version in a
supported reactor, stays unchanged and follows the shared version under Q06;
every other expression in these fields, including `${revision}`, composite
expressions and project-defined properties, fails before any source write;
ranges stay rejected and external versions and properties stay unchanged, as
Q08 decided.

The writer found no missing question and no conflict between this decision
and Q06, Q08, Q14, AC6, AC7, AC9, the body, the child draft or the umbrella.
The round 4 optional wording polish for option B was applied before the gate
and is part of the covered formulation.

Please check that the recorded decision line restates option B faithfully,
with nothing added or dropped compared with the option text, and that it is
consistent with the rest of the specification and the related documents. The
consolidation items already identified in rounds 3 and 4 remain deferred: the
stale pending and proposed wording (body around line 237, AC9 and the
sentence before the traceability table), the decided workspace rejection, the
participation-first lock scope and, now, the Q15 boundary in the Maven body
sentences and AC6 and AC9. Please report any further passage of that kind.

Reviewer recommendations cannot overwrite this human choice. Where the
decision conflicts with another decision, the body, the criteria, the umbrella
or the child draft, please name the conflict and the passages involved, and
say whether it needs a new question for the user or only a consolidation edit.

### Change summary for feature-request version-sources (round 5)

Changes to `docs/v0.14.0/feature-request.v0.14.0.version-sources.md` since
the round 4 request:

- Q15 option B: the reviewer's optional round 4 wording polish was applied
  before the human gate. Option B now says `${project.version}` is accepted
  only as the entire internal dependency or dependency-management version in
  a supported reactor, stays unchanged and follows the owning project's
  effective Maven version, which under Q06 is the same expected Maven version
  as the participating target module; participating project and internal
  `<parent>` version fields remain literal or inherited; composite expressions
  are named among the rejected forms.
- Q15 answer section: `User decision: pending` replaced by `User decision:
  confirmed - Option B, as recommended: ...`, restating the chosen option and
  the decision date, with no further comment.
- No other change: Q01 to Q14, the body, the acceptance criteria and the
  traceability table are unchanged. The umbrella and the child draft are
  unchanged.

### Writer response for feature-request version-sources (round 5)

Writer response:

Response to the round 4 writer instructions:

1. Q15 was kept pending until the user answered. The user received an
   explanation of Q15 and chose option B explicitly; the choice was not
   inferred from the recommendation or from reviewer agreement.
2. Q01 to Q14 and their decision records are preserved unchanged.
3. The optional wording polish for option B was applied, as the reviewer
   suggested, before the human gate; it adds no new form policy.
4. Nothing was consolidated, no question was removed and implementation has
   not started. Integrating the Q15 boundary into the Maven body and AC6 and
   AC9, together with the earlier consolidation reminders, waits for a
   separately authorized consolidation.
5. The user did not select option C, so none of its deferred boundary
   decisions is needed.

This round exists because the round 4 convergence covered Q15 while it was
still pending; it did not review the recorded decision itself.

### Reviewer focus for feature-request version-sources (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-05T08:58:20+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request version-sources round 5

The full current requirement and round 5 request have been reviewed, including the newly recorded human choice for Q15. No missing question or new contradiction is identified. The decision faithfully records option B: literal/inherited project versions as applicable, literal internal parent version fields, whole-value `${project.version}` only for internal dependency/dependency-management versions in a supported reactor, no write to that expression, and rejection of other expressions before mutation. Its references to rejected ranges and unchanged external versions/properties preserve Q08 rather than adding a new policy.

The shorter decision phrase "follows the shared version under Q06" accurately summarizes option B's owning-project effective Maven version and participating target version. It does not permit expression-based project or parent versions, composite expressions, custom property resolution or CI-friendly `${revision}` support. The existing inherited-version rule concerns inherited project versions, not a new permission to omit or interpolate required internal parent version fields.

Q06's shared release version and the Maven form in AC7 remain the premise for the unchanged expression to follow the transition. Root dependency management and internally inherited module versions do not introduce a separate choice. Q08's rejection of unsupported properties is now made concrete by Q15; it never required every property to be rejected. AC6 and AC9, the Maven body, the focused draft and the umbrella's explicit support-or-reject contract remain compatible with this selected boundary. Q14's participation-first lock interpretation is unaffected.

All fifteen question decisions are confirmed. The user selected B, so C's expressly deferred decisions are outside the selected scope. The formulation is ready for convergence; integration into the body and criteria remains a separately authorized consolidation activity. This review does not consolidate, authorize implementation or make the human convergence choice.

### Question verdicts for feature-request version-sources round 5

| Question | Verdict and reviewer choice |
| --- | --- |
| Q01 | Preserve confirmed A: direct set has source guards; release ordering/uniqueness stays with releasing callers; comparisons are numeric. |
| Q02 | Preserve confirmed A: validate the whole applicable set, repair drift only, never stage/commit. |
| Q03 | Preserve confirmed A: strict anchor token; optional title/notes for version commands; historical tags use their separate rules. |
| Q04 | Preserve confirmed A: a forbidden release-only downgrade stops the whole transition with no override. |
| Q05 | Preserve confirmed A: tool-only manifests and their locks are excluded together; malformed or invalid participating manifests still fail. |
| Q06 | Preserve confirmed A: one project version in each supported form; independently released components remain outside participation. |
| Q07 | Preserve confirmed A: eligible undeclared candidates are visible but ignored by check/set. |
| Q08 | Preserve confirmed A: bounded recursive Maven support, external versions unchanged, participating npm/uv workspaces and local links rejected. Q15 supplies its missing property boundary. |
| Q09 | Preserve confirmed A: required file/pattern/form, existing file, exactly one successful nonempty capture. |
| Q10 | Preserve confirmed A: preserve supported tool acceptance of previously current pairs, without opportunistic tool execution. |
| Q11 | Preserve confirmed A: mutation-wide lock, existing lifecycle ownership reused, artifact-free unlocked reads with stated limits. |
| Q12 | Preserve confirmed A: recoverable originals precede overwrite; incomplete restoration has distinct failure and retained consumer-local evidence. |
| Q13 | Preserve confirmed A: eligible HEAD or stable-tag targets, proper predecessor rules, alias handling and explicit conflicts. |
| Q14 | Preserve confirmed A: absent optional locks are not generated; participating existing locks need supported identifiable pairs; apply participation filtering first. |
| Q15 | Agree with confirmed B and would choose B. The decision adds nothing to and drops nothing from the selected option when read with Q06/Q08 and the existing inherited-version rule. No human choice remains pending. |

The questions and materially distinct options remain adequate. Earlier confirmed choices have not been reopened or overwritten; no new question is required by the recorded Q15 answer.

### Convergence evidence for feature-request version-sources round 5

Covered wording:

Coverage includes the full current requirement, all Q01-Q15 decisions, Q15 option B's round 4 wording polish and newly confirmed decision, and the relevant focused/umbrella contracts. In particular, the decision's accepted expression, covered field locations, unchanged-expression behavior, unsupported-expression failure, rejected ranges and external-version preservation all match the chosen formulation.

No outstanding human specification decision remains. Pending/proposed and broader conditional body wording is recognized as previously deferred consolidation work, with concrete integration passages identified in the writer instructions.

Convergence rationale:

Recommend convergence after review of the recorded human decision. Q15 faithfully records the selected B boundary and does not conflict with Q06, Q08, Q14, AC6/AC7/AC9, or the related draft scope. All fifteen questions are confirmed, no new question is needed, and only wording/integration of existing decisions remains. No further evidence or substantive revision is required for this formulation.

The human convergence choice and any authorization to consolidate remain separate. This answer grants neither, and it makes no claim that implementation or ecosystem compatibility has been tested.

### Writer instructions for feature-request version-sources round 5

No substantive revision or additional automated round is requested. Preserve all fifteen confirmed decision records. No consolidation is authorized by this answer.

During separately authorized consolidation, incorporate all confirmed refinements into the operative requirement and criteria, including the Q15 property boundary. Carry forward the established reminders: workspace rejection, recursive Maven participation, and participation-first lock validation with Q05/Q07 exclusions. Replace the stale Q08 pending claim near lines 237-238, AC9's "proposed in Q08", and the pending-decisions introduction before the traceability table.

Additional instances of the same deferred wording, not new decisions: the participation paragraph near lines 158-161 still says independent workspace packages need explicit configuration without stating Q08's rejection; the internal-reference paragraph near lines 229-234 still mentions supported workspace packages conditionally. Make those passages describe the chosen independent-component boundary and unsupported workspace arrangements. The Q08 "proposed boundary" option label and Q15's historical "no defined outcome" description naturally cease to be operative text when the decided questions are consolidated. The Maven body near lines 214-218 should name recursive internal dependencies/dependency management and the exact Q15 exception, rather than leaving supported properties unspecified.

The existing atomic restoration paragraph/AC11 must retain Q12's explicit incomplete-restoration outcome, and AC8/AC10 should retain the decided optional-lock and participation qualifiers when the other confirmed refinements are integrated. These are applications of existing decisions, not additional questions or requirements. No change to the umbrella or focused draft scope is needed.

Optional precision only: when integrating Q15, say "project versions remain literal or inherited as applicable; explicit internal parent version fields remain literal" so the existing project-version inheritance rule is not mistaken for a new parent-field rule. Preserve the human decision's meaning.

### Final reviewer decision for feature-request version-sources round 5

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-5 -->

## Round 5 by human - human-confirmation

- Recorded: 2026-11-05T09:09:29+01:00
- Exchange: specification/feature-request/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-5 -->
