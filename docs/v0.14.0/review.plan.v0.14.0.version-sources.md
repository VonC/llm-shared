# Specification review transcript for v0.14.0

- Exchange: specification/plan/v0.14.0/version-sources
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-07T10:01:36+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan version-sources (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.version-sources.md
Review round: 1

### Requestor assessment for plan version-sources (round 1)

Writer assessment of the version-sources implementation plan, round 1.

The plan implements the consolidated design
`docs/v0.14.0/design.v0.14.0.version-sources.md` (decisions Q01 to Q17,
reviewed in three rounds) and its requirement. It does not reopen any design
or requirement decision. It turns them into nine sequential steps, each with
files marked new or existing, tests first, classes and behavior, completion
criteria with `rg` checks, a line-budget checkpoint, split guidance and the
shared groundhog gate resolved through `pw scope day`. The validation plan is
a skeleton with goals and expectations only.

Facts were gathered from the current tree at `f053c2f` before writing: the
CLI parser and empty handler table, the four status normalization sites
(renderer, bootstrap, two batch launchers), the schema registry and the import
cycle a version schema would create, the private lock ownership check and its
definition-time probe default, the Git adapter's typed methods and how their
tests replace `run`, the repository and launcher simulations, the memory
scratch filesystem, the process audit, the 0.1-second CPU lifecycle limit and
coverage rules. Every Python file involved is below 550 lines.

The design's round 3 writer instruction asked the plans to name exact tool
versions, schemas, commands and fixtures for the lock compatibility evidence.
A planning probe outside the repository, recorded in the plan's "Lock
compatibility facts from the planning probe", ran uv 0.13.4 (the version both
consumer revisions come from) and npm 10.8.3 on Node 22.9.0: uv's locked mode
accepts the before and edited pairs for revisions 3 and 5 and for virtual and
editable roots, and rejects a manifest-only edit; `npm ci` accepts formats 2
and 3 but ignores the root version. The plan registers support only together
with recorded evidence (Steps 4 and 5).

Open questions: fifteen are proposed (Q01 to Q15), each with a recommended
option and a pending user decision, all implementation-level:

- step order: the transition before the adapters (Q01), evidence timing (Q06);
- file placement: the version schema and its import cycle (Q02), up-front
  splits of the largest adapters (Q10), test leaf layout (Q11);
- lock evidence: storage and recorder (Q03), the revision 3 fixture's
  provenance (Q04), a sensitive npm check (Q05);
- test strategy: transition seams (Q07), the declared release history (Q08),
  the transport of the acceptance matrix (Q09), cross-site status consistency
  (Q12);
- failure handling and rollout: the command-line limit of the independent-tips
  query (Q13), documentation timing (Q14).

Q15 is a routing question: of the five design-silent cases the plan's risk
pass names, four follow from the requirement or are mechanisms, but the tag
boundary eligibility rule decides which tag becomes a baseline, so the writer
recommends settling it in a short design amendment before Step 8 rather than
in the plan. Q15 does not decide that rule.

Several recommendations change the written plan (Q01, Q05, Q07, Q09, Q10, Q12,
Q13, Q15); the plan body still shows the original choice until the user
decides and the plan is consolidated. Please assess the whole plan: whether a
step misses a file, test or acceptance case of the design, whether an
implementation question is missing, whether the options and recommendations
are sound, and whether any plan text introduces a design choice.

### Change summary for plan version-sources (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/plan.v0.14.0.version-sources.md` was written by `write-plans`
  from the consolidated design (committed in `06080c8`), the feature request,
  the child draft and the umbrella; `review-ask-questions` then placed the
  open-questions section with Q01 to Q15 through `oqm`.
- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md` was written as
  its skeleton (goals and expectations filled, every check section holding the
  empty placeholder).
- As `write-plans` requires, a short "File-based IO cost clarification for
  version sources" section was added to the feature request (before its
  requirement clarifications) and to the design (before its decision table).
  Both restate existing read and write bounds; no decision, acceptance
  criterion or rule changed.
- Both plans are untracked; the draft and the umbrella are unchanged.

### Writer response for plan version-sources (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Writer notes for this first
round:

- The planning probe's scratch projects lived in a temporary directory
  outside the repository; nothing from them is committed. The recorded
  evidence itself is produced in Steps 4 and 5 by the planned recorder.
- The plan's risk pass names the five design-silent readings it implements;
  Q15 proposes where each is settled. Please say whether any other plan
  sentence reads as a design choice rather than an implementation detail.
- The plan file has CRLF line endings because `oqm` rewrites every line ending
  when it places the questions section, as for the design; the validation
  plan keeps LF. This is a tooling matter, not reviewed content.

### Reviewer focus for plan version-sources (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.version-sources.md`
- `.reviews/a.review-requested.plan.v0.14.0.version-sources.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-07T10:09:28+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan version-sources round 1

The current plan needs substantive revisions before convergence. Its overall scope, standard-library adapters, source ownership, completion boundary, and separation from later umbrella items agree with the consolidated design. The six requested changes below concern executable step boundaries, verifiable observations, recovery evidence preservation, and two gaps in the implementation instructions.

I assessed the complete current plan and validated round-1 request against the consolidated design, the requirement's acceptance criteria, the validation skeleton's initial expectations, and the existing Git, managed-file, artifact and operation-lock boundaries. The exact assessed plan SHA-256 is `c71299a8e15ad38121f6a365c83081356d5ed08ffab8202f2f613362b73ce4fe`.

All fifteen `User decision: pending` entries remain proposed answers. None is an explicit human decision. I agree with the proposed letters, with the qualifications in the question verdicts. In particular, Q15 B is an appropriate routing proposal, but does not settle the alias policy or authorize a design amendment.

Two implementation questions are missing: where the early shared input/edit types live, and how evidence allocation preserves earlier lifecycle captures when clock and process identifiers coincide. The existing Q15 also needs a precise design dependency and concrete alias examples. The other requested repairs implement already confirmed behavior and need no new product-policy decision.

The planning probe is stated as feasibility evidence. I did not reproduce its uv/npm runs or validate a supported combination in this review. Recorded evidence and adapter-output comparison remain deliverables of the respective implementation steps. No source code or specification was edited by the reviewer, and no tests were run for this specification assessment.

### Question verdicts for plan version-sources round 1

| Question | Assessment and reviewer choice |
| --- | --- |
| Q01 | **B**, useful and in scope. Put the transition immediately after configuration/claims, then extend its restoration matrix in each adapter step. Correct R1 first: moving the transition does not by itself supply types that Step 3 already needs. Renumber both plans and every ownership map together only upon authorized consolidation. |
| Q02 | **A**, sound. A small deferred validator keeps the schema registry independent of adapter initialization. B has a genuine import-order hazard; C is a larger foundation refactor without a demonstrated need. Test absence of newly imported adapter modules without depending on which modules earlier tests already loaded. |
| Q03 | **A**, sound with a clear limitation. Keep recorded JSON beside its consuming test and the manually invoked recorder outside the shipped engine. Recomputed hashes and edits check internal consistency; they do not independently prove that the real commands ran. Retain command outcomes and honest provenance for review. |
| Q04 | **A**, acceptable for the stated narrow guarantee. A header-substituted revision-3 fixture accepted unchanged by the pinned tool proves acceptance of that fixture, not coverage of all historical revision-3 syntax or older tools. Keep the provenance and claim explicit; no older uv download is required. |
| Q05 | **B**, worthwhile. Preserve `npm ci` as the frozen-mode evidence and add the lock-only currentness/control observations. Give the added command the same isolation and safety flags as lock generation (`--offline --ignore-scripts --no-audit --no-fund`), preserve the selected lock format, and record actual exit codes and before/after hashes. The manifest-only control must actually change the relevant lock fields. |
| Q06 | **A**, correct. Support registration and its recorded evidence should enter the same reviewed adapter change. A separate late evidence step would leave an unsupported intermediate claim. |
| Q07 | **B**, good. A small `TransitionPorts` value can carry replacement, process probe, clock and PID with production defaults. It remains an implementation seam rather than a new lifecycle policy. Add the evidence-allocation protection in R3; clock/PID injection alone does not make directory names unique. |
| Q08 | **A**, good. A small declared ancestry model gives mutually consistent typed observations without becoming a Git argument interpreter. Continue checking the real adapter's argument vectors separately. Move support to its own file if size or responsibility warrants it. |
| Q09 | **B**, good. Keep every acceptance row through production parsing/preflight/dispatch/rendering and whole-tree assertions, with representative launcher cases covering each command and all public statuses. Do not weaken restoration or no-write assertions when changing transport. |
| Q10 | **C**, reasonable. Separate Maven discovery from reference/inheritance rules now, and keep Python's stated split guidance. The responsibility boundary is a better reason than predicting an imminent 650-line violation from a 470-line estimate. |
| Q11 | **A**, sound. The existing leaf convention and direct groundhog targets outweigh the small initializer cost. This is a layout preference, not a release behavior decision. |
| Q12 | **B**, reasonable. Keep each boundary's behavioral proof and add a small consistency contract for the four sites. Use the established launcher source-contract mechanism; avoid a fragile check that merely searches for the same textual spelling. No shared runtime loader is needed. |
| Q13 | **B**, reasonable with corrected measurement. Measure the actual Windows command line, including the selected executable, existing Git prefix/options, quoting and UTF-16 units, rather than enforcing the rough 41-characters-per-SHA estimate. Include SHA-256 object IDs. Refuse before starting Git, report status 1 and candidate count, and preserve the four-call ceiling. |
| Q14 | **A**, correct. Update the reference pages when the commands ship; retain the final umbrella audit. Keep the new page focused on reference material and preserve the repository's Diataxis category order in navigation. |
| Q15 | **B**, with R6. The existing requirement supports rejecting unsupported internal Maven arrangements, matching npm workspace package names, failing a missing declared root, and releasing a standalone lock after incomplete restoration. Alias eligibility and the printed representative need design clarification. An eligible historical alias and an unvalidated engine alias on the same commit do not, by themselves, prove that the whole boundary must be excluded: distinguish boundary eligibility from eligibility of the actual tag printed. Present alternatives without claiming that the stricter choice is already mandated. |

Missing question proposal Q16: **Where do the shared inputs and per-file edit types live before the transition exists?** A: define them in the Step 2 source model, adding context conversion later (recommended: minimal new surface, dependencies point toward the model). B: put them in a small dependency-neutral inputs module in Step 2 (cleaner separation, one extra module). C: keep them in the transition module and rely on late imports/forward references (retains the current dependency and independently completed-step problem). State the selected owner, creation step and imports for `VersionInputs`, `FileEdit`, `Inventory` and `Plan`. The invariant is that Steps 2 and 3 do not import a future transition implementation.

Missing question proposal Q17: **How does a transition reserve a fresh evidence directory without touching an earlier capture?** A: atomically reserve a fresh authorized directory and retry collisions with an explicit unique suffix/sequence (recommended: preserves earlier handles and supports repeated calls). B: stop before any write on a name collision (safe but makes repeated lifecycle calls depend on clock timing or caller retries). C: assume second/microsecond timestamp plus PID is unique (insufficient without collision detection). Specify the mechanism and deterministic same-clock/PID tests; never reuse an existing evidence directory.

These are reviewer recommendations. All existing and newly proposed choices still require the user's decisions through the owning workflow; this answer does not consolidate them.

### Requested changes for plan version-sources round 1

Requested changes:

1. **R1 — supply the shared types before their first consumer.** The shared builders refer to `VersionInputs` at plan line 406, Step 3 accepts `inputs` and returns `Inventory`/`FileEdit` at lines 871–875, but the only declared owner of `VersionInputs` is `version_transition` at line 1414 in Step 7. `FileEdit`, `Inventory` and `Plan` have no explicit type owner/definition contract. Moving Step 7 after Step 3 under Q01 still leaves Step 3 depending on a future module, and importing detection back from that transition invites a cycle. Add Q16, define a dependency-neutral owner and creation step, and describe the minimum fields needed for per-file originals, planned bytes, source changes and captures. Ensure every numbered step can pass its stated gate without later-step placeholder modules. Keep context conversion at the later integration boundary if needed.

2. **R2 — correct the selector's observable Git-call expectations.** Step 8 line 1523 requires one Git call for a selection with a single candidate and “no count change.” A tag record contains neither the distance from that candidate to an arbitrary target nor a reusable commit count. At least the records query and the explicit `rev-list --count` observation are needed for the ordinary single-candidate case. Replace the undefined count-change shortcut with a case-by-case call table consistent with the four-call design bound; assert a nonzero count for one baseline several commits behind HEAD, zero for a release at HEAD, and full-history count with no eligible boundary. A syntactically valid missing tag must still become status 2, while a genuine Git execution failure remains status 1; describe how the typed observation distinguishes those outcomes without silently adding a fifth query. This is not permission to use `git describe` or infer distance from a tag name.

3. **R3 — preserve prior lifecycle evidence on name collisions.** The runtime note fixes names to second-resolution timestamp plus PID (line 312), the lifecycle contract accepts its owner's earlier evidence, and `prepare_directory` currently uses `exist_ok=True`. Two calls under one lifecycle lock in the same second can therefore address the same directory; replacing `original.<n>` or `manifest.json` would destroy the first restore handle's captured state. Add Q17 and an explicit no-reuse allocation mechanism through authorized targets. Test two calls with identical injected clock/PID, retained first evidence, disjoint originals, and a still-valid first handle. Test that pre-existing or partially created directories are never overwritten during collision handling. Merely adding clock/PID seams or higher timestamp precision is insufficient.

4. **R4 — cover cleanup and lock-release faults at the completion boundary.** Step 7 tests only deletion of original copies after completion. Add deterministic cases for manifest deletion/directory removal failure and for standalone `OperationLock.release()` failure after durable completion, asserting status 1, applied source bytes, no restoration, and diagnostics naming the actual residue or lock record. Also cover incomplete restoration followed by a release failure: status 3 and every unrestored path/original must survive the secondary cleanup error. The source-restoration and lock-release obligations already come from the approved design; do not introduce a new status or allow a `finally` error to replace the primary result.

5. **R5 — state and verify character-to-byte offset conversion.** Step 2 defines byte spans, but the TOML and JSON scanners take decoded text and pattern captures are character offsets. BOM length alone does not account for multibyte UTF-8 before a field. Specify one linear offset mapping or equivalent byte-aware scan, avoiding repeated prefix encoding per field. Add fixed fixtures with accented text and a non-BMP character before the owned field, and multiple fields in one file, for TOML, JSON and pattern sources; preserve every unowned byte through composition and restoration. Keep the cheap ASCII property generators if desired. Expat's existing byte indexes should remain byte indexes. No encoding or acceptance-policy change is needed.

6. **R6 — make Q15's unresolved design rule an explicit Step 8 prerequisite.** The risk pass currently commits to “one eligible tag, none ambiguous” and always prefers the `v` spelling, while Q15 proposes settling the rule later. Put that assumption behind an explicit unresolved dependency, with affected Step 8 tests blocked until a separately authorized design clarification is reviewed. Supply the design question with at least: same-version/same-commit historical unprefixed alias plus unvalidated `v` alias; validated plus unvalidated aliases; and an ambiguous alias. Decide boundary eligibility and which *eligible actual spelling* may be printed separately. Preserve the existing same-version/different-commit and different-version/same-commit conflict rules. Do not claim a particular stricter choice is already entailed by “missing evidence never promotes a tag.” Correct Q15's “no implementation step waits” sentence: earlier independent steps can proceed, while Step 8 waits. This review does not authorize amending or consolidating the design.

For the next automated review, repair the formulation and add the missing questions without recording reviewer preferences as user decisions. If an answer remains pending, retain it as pending and explain the resulting conditional plan. Do not consolidate either plan in this round.

### Writer instructions for plan version-sources round 1

Disposition: changes-requested. Address R1 through R6 and return the exact plan for another automated review round.

Keep the existing requirement and consolidated design authoritative. Add the two missing implementation questions with distinct options, consequences, a recommendation and a pending user decision. Revise Q13's measurement and Q15's framing as described. Retain the current proposed answer letters; do not turn any reviewer agreement into a human decision.

Where questions propose a later body change, make the affected assumption and prerequisite explicit so the plan does not simultaneously promise unconditional implementation and an unresolved design choice. Reserve renumbering/consolidation of the nine-step body and validation skeleton for the separately authorized owning action, and list all cross-references that action must update.

Keep recorded uv/npm evidence, support registration and current adapter-output checks in their adapter steps. The review makes no claim that those tools or fixtures have already been validated. Leave lifecycle commits/tags, range-reader adoption and legacy cutover with their assigned umbrella items.

Publish a replacement request after the formulation repairs. Do not start or contact a reviewer; the independently waiting reviewer will receive it through the shared exchange.

### Final reviewer decision for plan version-sources round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-07T10:22:13+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan version-sources (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.version-sources.md
Review round: 2

### Requestor assessment for plan version-sources (round 2)

Writer assessment of the version-sources implementation plan, round 2.

All six round 1 requests (R1 to R6) are accepted and applied to the plan
body, and the two proposed missing questions are added as Q16 and Q17 with
options, a recommendation and a pending user decision. No reviewer preference
was recorded as a user decision: all seventeen questions remain
`User decision: pending`, and the proposed answer letters of Q01 to Q15 are
unchanged.

Where a pending question proposes a body change, the body keeps the written
choice and a new section, "Conditional plan changes awaiting the open
questions", lists the change and every cross-reference the authorized
consolidation must update (notably all step numbers under Q01 B). Where a
request repaired a defect rather than a choice (R1 to R5), the body now shows
the repair directly, written as the recommended option of its question when
one exists (Q16 A for the type owner, Q17 A for evidence allocation).

The design and requirement stay authoritative and unchanged in this round.
The plan still makes no claim that uv, npm or their fixtures are validated:
recorded evidence remains a deliverable of the adapter steps.

The writer considers the question set complete for a plan. The remaining
open design point, aliased-boundary eligibility and its printed spelling, is
now an explicit Step 8 prerequisite routed by Q15 to a separately authorized
design clarification, not a plan decision. Please check that each repair
answers its request, that the conditional-change table is complete, and
whether a further implementation question is missing.

### Change summary for plan version-sources (round 2)

Changes to `docs/v0.14.0/plan.v0.14.0.version-sources.md` since round 1:

- R1: Step 2's model now owns `VersionInputs` (with `from_context`),
  `FileCapture`, `SourceChange`, `FileEdit`, `Inventory` and `Plan`, with
  their fields and tests; Step 3's detection signatures use them; Step 7 no
  longer defines `VersionInputs`. The risk pass states that every step passes
  its gate without a later-step module.
- R2: Step 1's `tag_records` raises `GitRevisionNotFound` for an exit 129
  `malformed object name` on its `--merged` revision, tested with canned
  output; Step 8 replaces the "single candidate, no count change" shortcut with
  a case-by-case call table (0 to 4 calls), and its tests assert nonzero,
  zero and full-history counts and the status 2 versus status 1 split.
- R3: Step 7 adds `version_evidence.allocate` (exclusive creation, `-2`,
  `-3` suffixes up to a fixed limit, never entering an existing directory,
  `managed_files` unchanged) with same-clock and same-pid tests, declared
  complete and partial pre-existing directories, and a lifecycle test keeping
  the first restore handle valid; the runtime note names the suffix.
- R4: Step 7 adds completion-boundary fault tests (original copy, manifest
  and directory removal, standalone lock release) and an incomplete
  restoration followed by a release failure keeping status 3; the primary
  outcome is fixed before cleanup. The fault seams now list removal, the lock
  factory, the clock and the process id.
- R5: Step 2 adds `model.to_byte_spans`, one linear walk shared by the TOML
  and JSON scanners and pattern sources, with accented and non-BMP fixtures
  and several fields per file in Steps 2, 3, 4 and 5; expat keeps its byte
  indexes.
- R6: Step 8 gains a "Prerequisite for aliased boundaries" naming the blocked
  cases, a completion criterion tied to the reviewed design clarification and
  boundary rules limited to single-tag boundaries; the risk pass replaces the
  committed alias reading with an unresolved design dependency.
- Questions: Q13 measures the real command line in UTF-16 units with both
  object id lengths; Q15 adds the four alias examples, separates boundary
  eligibility from the printed spelling and now says Step 8 waits; Q16 and Q17
  are new; reviewer qualifications are added to the answers of Q01 to Q05,
  Q07 to Q09, Q12 and Q14.
- New section "Conditional plan changes awaiting the open questions".
- The validation skeleton's expectations for Steps 1, 2, 7 and 8 follow the
  repairs. The requirement, design, draft and umbrella are unchanged since
  round 1.

### Writer response for plan version-sources (round 2)

Writer response:

Response to the round 1 review:

- R1 to R6 are accepted without disagreement; the change summary maps each to
  its plan edits.
- Q16 and Q17 are added as proposed, with option A recommended for both, the
  reviewer's recommendation, and pending user decisions. The body is written
  as those options so that the repaired dependency and the protected
  allocation are visible now; the conditional-change table names what changes
  if the user picks option B instead.
- Evidence allocation is implemented in `version_evidence` with exclusive
  `Path.mkdir` on a revalidated authorized target rather than a new
  `managed_files` function, so the design's list of five foundation changes
  stays exact.
- The Step 8 call table keeps the design's four-call ceiling; the missing-tag
  case is distinguished from a Git execution failure by the one records call's
  exit status and stderr, with no extra query.
- Renumbering under Q01 B is not applied; it is listed for the authorized
  consolidation, as requested.

### Reviewer focus for plan version-sources (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-07T10:25:55+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan version-sources round 2

The current plan and complete round 2 request were assessed against the consolidated requirement and design, the validation skeleton, and the existing Git environment, Git adapter and managed-write boundary. The current document is authoritative. No specification or source was edited, no transcript was used as assessment context, and no tests or compatibility recorder were run.

All six round 1 requests are addressed:

- R1: Step 2 now owns the shared input, capture, change, inventory, edit and plan contracts. Steps 3 and 7 point toward that model, and Q16 covers the alternative dependency-neutral owner. Moving the transition does not require an unimplemented later module.
- R2: the selector now records an explicit commit count, the one- and several-candidate paths stay within four calls, and missing tag targets are distinguished from execution failures without adding a query. The existing Git child environment pins LC_ALL, LANG and LANGUAGE to C, consistent with the specific missing-revision diagnostic classification. Other failures remain execution failures.
- R3: evidence directories are reserved exclusively, collisions never enter an existing directory, retries are bounded, and fixed-clock/PID and lifecycle-handle cases protect earlier originals. Q17 exposes the allocation choice.
- R4: the completion-marker boundary has removal and lock-release fault cases, preserves applied bytes after completion, and preserves status 3 and original-path diagnostics when release also fails after incomplete restoration.
- R5: the common character-to-byte mapping and fixed accented/non-BMP cases cover TOML, JSON and pattern sources, multiple fields, byte-order marks and line endings, while expat retains its byte-index boundary. The restoration matrix continues to cover each adapter's fixture set.
- R6: Step 8 explicitly depends on a separately authorized reviewed design clarification for aliased-boundary eligibility and printed spelling. It does not equate an ineligible alias with an ineligible boundary. Unaffected work can proceed, but Step 8 cannot be declared complete before that dependency is resolved.

The question set is complete at this level. No additional implementation or design question is required for this plan review. The newly added Q16 and Q17 are useful, distinct decisions. All seventeen proposed answers remain pending human choices; reviewer agreement does not decide them.

Only wording synchronization remains: Q07 still describes the earlier two-keyword interface and lists only four members of TransitionPorts, whereas Step 7 already specifies six injectable inputs. The existing lock-probe technical-fact paragraph also describes module-global replacement rather than the revised explicit ports. The writer can align these passages mechanically with the existing Step 7 contract using the replacement wording below. This changes no interface decision or test requirement.

### Question verdicts for plan version-sources round 2

Every entry below is reviewer preference, not a user decision. All seventeen User decision fields remain pending. The questions and their materially distinct options are sufficient; the exceptions needing wording synchronization are identified explicitly.

| Question | Reviewer choice | Assessment and reason |
| --- | --- | --- |
| Q01 | B | Put the transition after the dependency-neutral Step 2 model and Step 3 edit planner; add each later adapter's fixture set to restoration coverage. The conditional-change table correctly reserves complete renumbering of both plans and all cross-references for authorized consolidation. |
| Q02 | A | A schema declaration with a deferred validator avoids the import cycle and keeps unused version-domain imports off configuration loads. Check newly imported modules independently of earlier tests. |
| Q03 | A | Committed JSON beside its test and a manually run recorder keep production standard-library-only and leave coverage policy intact. Hashes prove internal consistency; actual recorded runs and provenance support the compatibility claim. |
| Q04 | A | Header-derived revision 3 fixtures are acceptable with explicit provenance and demonstrated acceptance by uv 0.13.4. They make no claim about older uv versions or all historical revision 3 layouts. |
| Q05 | B | Keep npm ci and add the isolated lock-only consistency check and sensitive manifest-only control. Record actual outcomes, root-field changes and hashes; preserve the selected lock format. Historical planning-probe facts must remain descriptions of actual probes, not claims of later completed evidence. |
| Q06 | A | Each adapter registers support only when its recorded compatibility evidence and reproducibility test land with it. |
| Q07 | B | Bundle all six inputs already specified by Step 7: replacement, file/directory removal, lock factory, process probe, clock and PID. Align the stale two-keyword description and four-member list; individual explicit keywords remain the safe alternative. Deterministic inputs do not replace Q17's collision protection. |
| Q08 | A | Declared commit ancestry supplies consistent typed observations without a Git argument interpreter or a process start; real argument vectors are checked at the adapter boundary. |
| Q09 | B | Keep every matrix assertion at cli.main with whole-tree snapshots and retain representative launcher coverage for each command and public status. Restoration and no-write assertions are preserved. |
| Q10 | C | Separate Maven discovery from its extensive reference/inheritance rules up front, keeping Python's on-demand split and the actual 650-line ceiling. |
| Q11 | A | Preserve the existing test-leaf convention; initializers are a small cost and targeted failures remain easy to locate. |
| Q12 | B | A cross-site accepted-status comparison covers renderer, bootstrap and both launchers without a new runtime dependency. Compare accepted values using the existing source-contract mechanism. |
| Q13 | B | Measure the exact serialized Windows command in UTF-16 units, including the terminating NUL in the OS limit, with both object-id lengths and boundary tests. Refusal stays status 1 and adds no Git call. |
| Q14 | A | Ship matching reference documentation with the new commands and statuses, keeping each page within one Diataxis purpose and the required navigation order. |
| Q15 | B | Preserve the four supported implementation readings and resolve aliased-boundary eligibility and actual output spelling in a separately authorized reviewed design clarification. Agreement here authorizes neither that amendment nor its substantive rule. |
| Q16 | A | Step 2's model is an adequate dependency-neutral owner for the specified contracts. Option B is also viable if its module is created in Step 2 and registered as support for the completeness test. |
| Q17 | A | Exclusive reservation with bounded suffix retries preserves earlier evidence and restore handles while allowing repeated lifecycle calls under an identical clock/PID. Never reuse an existing directory. |

No questions should be consolidated, removed as decided, or recorded as confirmed by this reviewer.

### Convergence evidence for plan version-sources round 2

Covered wording:

Q07 description: "Step 7 exposes six injectable inputs: the replacement function, file and directory removal, the lock factory, the process probe, the clock and the process id. The choice is whether to keep them as explicit keywords or bundle the same inputs in one TransitionPorts value. Both forms keep evidence names and failure injection deterministic."

Q07 option A: "Keep the six explicit keyword seams with production defaults, as in the revised Step 7 body. Pro: no extra type. Con: a wider keyword interface for callers and tests."

Q07 option B: "One TransitionPorts dataclass bundles replacement, file/directory removal, the lock factory, the process probe, the clock and the process id, with production defaults, passed as one keyword. Pro: one stable parameter and a single home for all external inputs. Con: one more small type."

Apply the same six-member description to Q07's metaphor mapping and recommendation; retain B as a proposal and User decision: pending. Remove the obsolete two-keyword/real-clock assertions, rather than changing Step 7's already specified seams.

Lock-probe technical fact: "OperationLock binds its probe default at definition time, so the transition passes its explicit process-probe input to the chosen lock factory; tests supply declared process states through that seam." Existing foundation identity fixtures may still replace current_identity.

Q13 measurement: "measure the exact serialized command line in UTF-16 code units including the terminating NUL"; keep the existing limit, status 1 refusal, call bound and boundary tests.

Convergence rationale:

Disposition: convergence-recommended.

The six substantive round 1 findings are addressed by concrete contracts, tests, bounded observations and an explicit design dependency. Q16 and Q17 cover the two missing implementation decisions. Existing questions remain sufficient and their proposed choices are consistent with the requirement and design, subject to their recorded pending status and the separate alias-design prerequisite.

The remaining Q07 and lock-probe text predates the six explicit seams now present in Step 7; the covered replacements synchronize wording without changing the planned contract. The Q13 terminating-NUL clarification is a measurement-boundary wording correction within its already required exact-length tests. No substantive rework or further automated round is needed for those edits alone.

This recommendation is advisory. It does not decide any question, authorize consolidation, authorize the design clarification, complete Step 8, or claim implementation/tests/lock-tool evidence passed. The requestor and human retain their respective workflow and decision authority.

### Writer instructions for plan version-sources round 2

Recommend convergence of the current plan formulation. Only the following wording synchronization remains, covered by this recommendation:

1. Replace Q07's description with: "Step 7 exposes six injectable inputs: the replacement function, file and directory removal, the lock factory, the process probe, the clock and the process id. The choice is whether to keep them as explicit keywords or bundle the same inputs in one TransitionPorts value. Both forms keep evidence names and failure injection deterministic."
2. In Q07 option A, write: "Keep the six explicit keyword seams with production defaults, as in the revised Step 7 body." Its advantage is no extra type; its disadvantage is a wider keyword interface for callers and tests. Remove the obsolete real-clock and test-directory-search consequences.
3. In Q07 option B and its metaphor mapping, enumerate the same six inputs, including removal and the lock factory. Keep B as the proposed answer and retain its pending user decision. In the conditional-change table, spell out the same membership if useful; the table already says six seams.
4. In the earlier lock-probe technical fact, replace the module-global patch description with: "OperationLock binds its probe default at definition time, so the transition passes its explicit process-probe input to the chosen lock factory; tests supply declared process states through that seam." Existing foundation identity fixtures may still replace current_identity.
5. Clarify Q13's exact measurement wording as "UTF-16 code units including the terminating NUL", retaining its existing status, call bound and boundary tests.

These edits align wording with mechanisms and tests already present; they introduce no new design choice. Keep the conditional-change table for all pending options, apply no selected option or renumbering before the authorized consolidation, and update both plans and the registry support-module set if Q16 B is later selected. Do not rewrite historical planning-probe facts as if future recorder runs had happened.

All seventeen human choices remain outstanding. Q15's separate design-clarification authorization and reviewed outcome are prerequisites for completing the affected Step 8 cases. Convergence of this plan formulation does not resolve that design dependency or validate any implementation or tool evidence.

### Final reviewer decision for plan version-sources round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-08T01:19:01+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: User comments recorded during the explanation of the plan questions, quoted
as given:

- At Q03 (2026-11-07): "What is this "before" state you keep mentioning?",
  then "Choice A, but do update all docs to explain that "before" business,
  and do clarify it whenever you mention it in future question you explain.
  This is quite confusing (update all -- umbrella - draft - etc)".
- At Q12 (2026-11-08): "What is "site"? Don't forget applicative test must be
  kept to a minimum (failing tests only, of which there should be only one):
  a brel is not when you re-test 10K applicative tests, those are supposed to
  be done before. What are we talking about here?"
- During Q13 (2026-11-08): "Again, make sure brel does not trigger the
  application test".
- After Q17 (2026-11-08): "go ahead with the round 3 review".

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-08T01:19:54+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan version-sources (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.version-sources.md
Review round: 3

### Requestor assessment for plan version-sources (round 3)

Writer assessment of the version-sources implementation plan, round 3.

This is the follow-up review after the user's explicit decisions. Round 2
recommended convergence; at that gate the user chose to discuss the
undecided questions. All seventeen are now explicitly decided by the user
(`User decision: confirmed`), each through a host-native choice after an
explanation, with no deferral:

- Q01 B, Q02 A, Q03 A (with a comment), Q04 A, Q05 B, Q06 A, Q07 B, Q08 A,
  Q09 B, Q10 C, Q11 A, Q12 B (after a clarification request), Q13 B, Q14 A,
  Q15 B, Q16 A and Q17 A.

Every choice matches the recommended option and the reviewer's round 2
preference. The choices whose body changes are listed in "Conditional plan
changes awaiting the open questions" (Q01 B, Q05 B, Q07 B, Q09 B, Q10 C,
Q12 B, Q13 B, Q15 B) are not applied yet; consolidation applies them,
including the step renumbering of Q01 B. The options confirming the written
body (Q02 A, Q03 A, Q04 A, Q06 A, Q08 A, Q11 A, Q14 A, Q16 A, Q17 A) need no
body change.

The user's comments led to three additions across the effort's documents,
introduced at each document's level without changing any decision, question
ID, option or acceptance criterion:

- the "before" pair of the lock evidence, defined in the umbrella draft, the
  topic draft, the feature request, the design, the plan and the validation
  plan;
- "site" (status normalization site), defined in the plan, the only document
  that uses it;
- where this item's tests run (llm-shared's own development suite, never run
  by a version command, `brel` or a consumer release), stated at the first
  mention of tests in all six documents.

A further user rule, recorded in the umbrella draft only because it belongs
to item 5: `brel` never triggers the application test suite; the release gate
builds the release and re-runs at most the last failed tests, normally none or
one, as llm-shared's current dummy/last-failed pytest gate does. It appears in
the build.bat contract, lifecycle step 4, item 5's acceptance criteria and
decision 23.

Please check: the consistency of the seventeen decisions with each other,
with the conditional-change table and with the requirement, design and
drafts; whether the notion text added to the feature request, design and
drafts changes any settled behavior; whether the umbrella's new `brel` rule
conflicts with item 5's existing gate wording ("The project's build/test gate
runs against the release-form files", decision 23, and the llm-shared cutover
note on its dummy/last-failed gate); and whether any new question is needed.
The writer sees no missing question; the separate design clarification of
Q15 B and the item 5 gate content are outside this plan's decisions.

### Change summary for plan version-sources (round 3)

Changes since the round 2 convergence answer:

- `docs/v0.14.0/plan.v0.14.0.version-sources.md`:
  - Q01 to Q17: each answer section now holds a `User decision: confirmed`
    record with the choice, its qualifications, the date and any user
    comment; no option, recommendation or question ID changed.
  - "Lock compatibility facts from the planning probe" opens with a
    definition of the "before" pair, the edited pair, tool acceptance and the
    manifest-only control; Q03, Q04 and Q05 define the terms inline.
  - "Confirmed technical facts" defines a status normalization site; the Q12
    block defines it again and states that its tests run only in llm-shared's
    development suite.
  - "Shared test architecture" gains "Where these tests run".
- `docs/v0.14.0/plan.v0.14.0.version-sources.validation.md`: Step 4 goal and
  expectations and Step 5 expectations define the "before" and edited pairs;
  the opening note states where the tests run.
- `docs/v0.14.0/feature-request.v0.14.0.version-sources.md`: a paragraph
  defining the "before" pair after the lock-consistency paragraph of
  "Version-only writes, locks and internal references"; one sentence after
  the acceptance table on where the validation suite runs.
- `docs/v0.14.0/design.v0.14.0.version-sources.md`: a paragraph defining the
  "before" and edited pairs at the start of the evidence list in "Lock
  compatibility evidence for supported tools"; one sentence in "The explicit
  adapter tuple" on where its tests run.
- `docs/v0.14.0/draft.v0.14.0.version-sources.md` (topic draft): a paragraph
  on the "before" and edited pairs in "Writing only the version, including
  locks"; one sentence on test scope in its acceptance list.
- `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md` (umbrella): in item
  2's acceptance, the "before" pair sentence and the test-scope sentence; for
  item 5, the `brel` rule in "Project build.bat contract", lifecycle step 4,
  item 5's acceptance criteria (new first bullet) and decision 23 (appended
  sentence).
- The requestor's question-explanation instruction changed mid-batch (big
  picture before each question, re-explained notions); explanations from Q05
  on follow it. This affects the conversation, not the documents.

### Human guidance and writer response for plan version-sources (round 3)

Human guidance:

User comments recorded during the explanation of the plan questions, quoted
as given:

- At Q03 (2026-11-07): "What is this "before" state you keep mentioning?",
  then "Choice A, but do update all docs to explain that "before" business,
  and do clarify it whenever you mention it in future question you explain.
  This is quite confusing (update all -- umbrella - draft - etc)".
- At Q12 (2026-11-08): "What is "site"? Don't forget applicative test must be
  kept to a minimum (failing tests only, of which there should be only one):
  a brel is not when you re-test 10K applicative tests, those are supposed to
  be done before. What are we talking about here?"
- During Q13 (2026-11-08): "Again, make sure brel does not trigger the
  application test".
- After Q17 (2026-11-08): "go ahead with the round 3 review".

Writer response:

Response after the round 2 convergence and the user's decisions:

- The round 2 covered wording (Q07 six seams, the lock-probe fact, Q13
  terminating NUL, the Q16 B registry row) was applied before the gate, as
  reported then.
- No user choice departs from a recommendation, so no conditional-change row
  needs rewording; the table stays the consolidation work list.
- The notion definitions were added because the user asked for them in every
  effort document; they restate existing behavior in plainer terms. If any of
  them reads as a new requirement or a changed decision, please say so, since
  the user wants such cases raised as questions rather than edited silently.
- The `brel` rule is recorded in the umbrella as the user stated it; item 5's
  own requirement and design will refine its gate. This plan changes no step
  for it, since no version command runs tests.
- Q15 B leaves one separately authorized design clarification (aliased
  boundaries and their printed spelling) before Step 8's alias tests; it is
  not part of this round.

### Reviewer focus for plan version-sources (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-08T01:24:46+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan version-sources (round 3)

Independently reviewed the complete current plan and the validated round 3 request, including all seventeen recorded user decisions and the literal Human guidance block. Checked the related requirement, design, focused draft, umbrella and validation-plan passages concerning lock evidence, test scope, release gates and alias boundaries. No versioned review transcript was used as assessment context.

Disposition: convergence-recommended. No additional question is needed. All seventeen choices are explicit user decisions; none remains awaiting an answer. The options are materially distinct, their consequences are adequate, and the recorded choices are mutually compatible. The table below gives my independent choices and reasons. Agreement with those decisions does not authorize consolidation.

The body deliberately retains its pre-consolidation choices. Its differences from Q01 B, Q05 B, Q07 B, Q09 B, Q10 C, Q12 B and Q13 B are listed consolidation work, rather than undocumented disagreement. Apply their consequences to both plans when consolidation is authorized. Q16 A and Q17 A confirm the present body; their unselected B rows must not become implementation instructions.

The added before/edited-pair definitions restate the existing relative compatibility guarantee. They neither add runtime tool execution nor promise to repair stale dependencies. The example moves both files from a release core to another release core; the adapter form rules still govern snapshot targets. Q05 B supplements npm's frozen-mode acceptance with a sensitive lock-only check; it does not replace the design's required frozen run. Recorded command outcomes remain actual observations.

The status-site definition identifies four existing normalization boundaries without adding a runtime component. Development-test explanations consistently place this item's tests in llm-shared's development suite. They do not add tests to version commands or release execution.

The umbrella's Project build.bat contract, lifecycle step 4, item 5 acceptance and decision 23 now consistently limit release testing to the last failed tests, normally none or one. The earlier phrase "build/test gate" identifies the consuming gate and its execution against release-form files; the adjacent rule limits its contents. The item 8 cutover instruction to preserve the current dummy/last-failed gate agrees. Retaining project ownership of the gate does not authorize a full application-suite rerun during brel. Item 5 must implement the recorded rule; this item needs no new release-gate step or question.

Q15 B correctly leaves aliased-boundary eligibility and printed actual tag spelling to a separately authorized, reviewed design clarification. The current design defines tag eligibility and groups same-version/same-commit aliases but still does not decide those two boundary rules. Step 8 and its validation expectations explicitly remain incomplete until the dependent cases pass. Plan convergence neither authorizes that clarification nor validates implementation or tool evidence. No source changes, tests, or compatibility recordings were performed in this specification review.

### Question verdicts for plan version-sources (round 3)

All seventeen questions are relevant to implementation planning and have confirmed human answers. No question is missing, redundant or materially unclear after the supplied explanations. No recorded choice conflicts with another choice or requires reopening a settled requirement. My independent choices match the recorded decisions:

| Question | User / reviewer | Reason and consequence |
| --- | --- | --- |
| Q01 | B / B | The transition consumes Step 2 types and Step 3 edits, so moving it to Step 4 lets each later adapter complete its restoration contract. Renumber both plans and propagate fixture ownership. |
| Q02 | A / A | Schema data stays in schemas.py, with the established deferred validator import avoiding the import cycle and unnecessary adapter loading. |
| Q03 | A / A | Committed JSON plus a hand-run test-tree recorder preserves process-free tests and unchanged coverage rules. Recomputed hashes establish record consistency, not proof of execution. |
| Q04 | A / A | Header-substituted revision 3 bytes accepted by uv 0.13.4 support the stated narrow compatibility claim with explicit provenance. |
| Q05 | B / B | Keep npm ci and add the lock-only unchanged-pair/control checks, preserving format and recording actual hashes, exit codes and changed root fields. |
| Q06 | A / A | Register uv/npm support with its evidence in the corresponding adapter step. Moving the transition earlier does not delay that evidence. |
| Q07 | B / B | TransitionPorts groups the same six external inputs with production defaults; deterministic naming still relies on Q17's exclusive allocation. |
| Q08 | A / A | Declared ancestry answers typed observations consistently without extending the frozen Git argument emulator. |
| Q09 | B / B | cli.main covers the complete acceptance matrix with whole-tree snapshots; representative launcher cases retain each command and status contract. |
| Q10 | C / C | Separate Maven references from discovery at creation; keep Python's on-demand split guidance and register the Maven support module. |
| Q11 | A / A | The existing test-leaf convention supports focused execution and bounded file sizes. |
| Q12 | B / B | Existing per-boundary tests plus one semantic consistency comparison cover all four status lists without a new runtime module. These are development tests. |
| Q13 | B / B | Measure the exact serialized Windows command line in UTF-16 units including NUL; reject oversize input with status 1 without another Git call. |
| Q14 | A / A | Ship reference corrections with the commands, preserving explanation, tutorials, how-to guides, reference navigation order. |
| Q15 | B / B | Four constrained mechanism readings remain in the plan. Alias eligibility and printed spelling need their separately authorized design review; that authorization is still absent. |
| Q16 | A / A | Step 2 model ownership gives detection and transition their shared types without a dependency on a later step. Do not create inputs.py under the unselected B option. |
| Q17 | A / A | Exclusive creation with bounded suffix retries preserves all existing originals and restore handles, including repeated lifecycle calls with identical clock/PID inputs. |

The user's Q03 comment asks for definitions, not a new lock guarantee. The Q12 clarification and Q13 reminder constrain release-time testing and agree with the development-only test explanations. No conditional choice creates another unanswered plan decision.

### Convergence evidence for plan version-sources (round 3)

Covered wording:

Only wording corrections remain in the reviewed formulation:

- Replace the conditional-table introduction's "When the user decides" with "The user decisions below are confirmed; separately authorized consolidation applies the selected options and updates their cross-references." Until consolidation, the body is deliberately the written baseline.
- In the Q15 B conditional row, use "A separately authorized design clarification must be reviewed before Step 8's aliased-boundary tests; selecting B does not authorize it." This matches the explicit answer and user decision already present.
- In the Q05 B conditional row, identify "The npm adapter step's records add ..." rather than "Steps 4 and 5 records add ..."; retain the uv evidence unchanged and use the final step number after Q01 renumbering. Preserve the planning-probe table as historical facts and describe the supplemental npm check separately.
- In the design's new explanation, "without it, a success afterwards would prove nothing" can be narrowed to "without the starting-pair acceptance, success afterwards would not establish preservation from an accepted starting pair." This improves precision without changing the evidence requirement.
- If clarifying the umbrella's illustrative build comment, use "the project's release build and at most its last failed tests" for the release path. The adjacent prose already makes that limit binding; no gate behavior choice is missing.

Convergence rationale:

Recommend convergence: all seventeen human decisions are recorded, compatible and adequately explained. The complete plan accounts for dependency ordering, shared types, lock evidence, failure/restoration boundaries, byte mapping, bounded Git calls and the deferred alias-design rule. The new definitions clarify existing behavior, and the user's release-testing constraint is recorded consistently in the umbrella.

No additional plan question or substantive formulation revision is required. The unapplied body changes are explicit consequences of confirmed choices reserved for authorized consolidation. The remaining wording corrections do not change any option, decision, acceptance criterion or scope. No human answer to Q01-Q17 remains pending. Consolidation authorization and the separate alias-design authorization remain outside this recommendation; implementation validation and recorded compatibility evidence remain future work.

### Human guidance response for plan version-sources (round 3)

Human guidance:

User comments recorded during the explanation of the plan questions, quoted as given:

- At Q03 (2026-11-07): "What is this "before" state you keep mentioning?", then "Choice A, but do update all docs to explain that "before" business, and do clarify it whenever you mention it in future question you explain. This is quite confusing (update all -- umbrella - draft - etc)".
- At Q12 (2026-11-08): "What is "site"? Don't forget applicative test must be kept to a minimum (failing tests only, of which there should be only one): a brel is not when you re-test 10K applicative tests, those are supposed to be done before. What are we talking about here?"
- During Q13 (2026-11-08): "Again, make sure brel does not trigger the application test".
- After Q17 (2026-11-08): "go ahead with the round 3 review".

Guidance response:

Q03's request to explain "before": checked the definition in all six effort documents. It denotes the manifest/lock pair at its old version before the adapter edit, with acceptance established by the real tool; the edited pair changes only owned version bytes. The definitions preserve the existing relative guarantee and the exclusion of already stale dependencies. The minor precision correction is supplied in the wording input.

Q12's "site" and minimum-test concern: a site is one existing status-normalization boundary. The plan names all four and says its consistency test belongs only to llm-shared's development suite. The corresponding test-scope explanation is also present in the validation plan, design, requirement and drafts. No version command or consumer release runs this suite.

Q13's reminder about brel: the umbrella's build contract, lifecycle step 4, item 5 acceptance and decision 23 record the prohibition on running the application suite and limit release tests to the last failed ones, normally none or one. "Build/test gate" and the item 8 dummy/last-failed cutover note are consistent with that rule. Item 5 must retain it when defining and implementing its gate; it does not require another question in this plan.

The final instruction to proceed authorizes this review. It does not constitute consolidation authorization, authorize the separate Q15 design clarification, or permit overriding any recorded choice. All choices were preserved and assessed as recorded.

### Writer instructions for plan version-sources (round 3)

Recommend convergence of this reviewed formulation. Leave consolidation to the human gate; do not infer authorization from this recommendation or the seventeen confirmed choices.

At authorized consolidation, apply the selected options consistently to implementation and validation plans, including the validation expectations for the added npm evidence, TransitionPorts, Maven split, status consistency test, command-line guard and the cli.main/representative-launcher acceptance arrangement. Renumber the transition and adapter steps everywhere listed by Q01 and make each adapter step own its restoration fixtures. Preserve Q16 A model ownership and Q17 A suffix allocation. Remove question blocks and obsolete alternatives through the authorized consolidation workflow.

Keep the Q15 dependency explicit. Its conditional table row must say that the design clarification requires separate authorization, not that selecting B grants it. Do not amend that design or mark Step 8 complete from this plan decision. The existing conflict rules remain testable while alias-dependent eligibility/spelling cases wait.

Preserve the development-versus-release test scope and the umbrella's last-failed release gate rule. Item 5's later documents must carry that constraint forward. Do not add a full application-suite run to brel or a version command.

Preserve historical planning-probe outcomes. Q05 B's extra recorded command belongs to the future recorder/evidence work; do not relabel an earlier npm ci observation as a successful sensitivity check. The manifest-only control must actually change lock root version fields for that additional check to count.

### Final reviewer decision for plan version-sources (round 3)

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-08T01:31:00+01:00
- Exchange: specification/plan/v0.14.0/version-sources
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.version-sources.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
