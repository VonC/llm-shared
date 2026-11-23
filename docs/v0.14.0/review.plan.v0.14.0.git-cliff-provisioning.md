# Specification review transcript for v0.14.0

- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-15T13:28:41+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Review round: 1

### Requestor assessment for plan git-cliff-provisioning (round 1)

Writer assessment of the git-cliff-provisioning implementation plan, round 1.

The plan implements the consolidated design (Q01 to Q18 decided on
2026-11-14, committed in `5431b6a4`) and the consolidated feature request
(Q01 to Q16). It has eight steps: the tested-pin manifest, the `[git-cliff]`
domain and the budget policy (Step 1); the contained Windows child lifecycle and
the use guard (Step 2); the cache layout, entry record, reuse check and cache
lock with owner-aware recovery, plus the root `.gitignore` entry (Step 3); the
network client, the download worker entry kind and single-member extraction
(Step 4); the provisioning service, invocation object and failure contract
(Step 5); the `gcliff` launcher, its entry kind and alias fragment (Step 6); the
evidence harness (Step 7); and the evidence run, admission of 2.14.2,
integrated acceptance, native checks and documentation (Step 8).

Its confirmed-facts section was checked against the code on 2026-11-15 at
`2b2cbab1`: line counts with the gate metric, the `configuration._value`
default path, the single set literal that `test_codepage_tdd.py` reads in
`bootstrap.main`, the process audit and memory filesystem, the Git environment
policy and the missing input stream of `GitExecutionContext.run`. Every file
involved is below 550 lines except the unchanged `version_support.py` (552).
No Step 0 gate is planned; the stage budgets are asserted with a fake clock.

Open questions: eighteen plan questions (Q01 to Q18), each with a recommended
option and a pending user decision:

- step placement and order: the `.gitignore` entry (Q01), admission timing and
  the launcher's position (Q03, where the writer recommends swapping the
  harness and evidence steps before the launcher);
- module and helper splits: the shared record decoder (Q02), the native layer
  modules (Q04, recommending a separate `windows_native.py` from the start), the
  shared test fakes (Q12, recommending three helper modules);
- test strategy: native coverage through an injected fake kernel (Q05), when
  the native checks run (Q06, recommending incremental runs in Steps 2, 4 and
  5), the recorder's location (Q07), and test leaf naming (Q11, recommending
  one leaf per production module with prefixed topic files);
- evidence handling: the bundle location (Q08), the fixture mechanism (Q09),
  recording the user's review in the bundle (Q16) and the exit-path audit
  procedure (Q17);
- implementation details: the digest recomputation (Q10), the launcher's
  codepage handling (Q13), the Ctrl+C filter (Q14), the bootstrap entry kinds
  (Q15) and the guard reopen failure (Q18).

Recommendations for Q03, Q04, Q06, Q11, Q12 and Q16 would change the written
plan if accepted; the body still states the original choice until
consolidation.

Please assess the plan independently: completeness and faithfulness against
the design's delivered scope, foundation changes and acceptance cases, without
new design choices; feasibility of each step against the current code and test
tree; the line budgets and split guidance; the test-first and process-free
strategy; whether any question belongs to the design or the requirement
instead of the plan; any missing plan question; and whether each question's
options and recommended answer are sound. The plan's "Readings of
design-silent cases" list is the writer's interpretation where the design is
silent; please flag any reading that is in fact a design choice.

### Change summary for plan git-cliff-provisioning (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md` and its validation
  skeleton `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
  were written by `write-plans` from the consolidated design (committed in
  `5431b6a4`) and the feature request, following the item 2 plan's structure.
- As `write-plans` requires, a short "File-based IO cost clarification for
  git-cliff provisioning" section was added to the feature request (before its
  requirement clarifications) and to the design (before its decisions table).
  Both restate existing read and write bounds; no decision, acceptance
  criterion or rule changed.
- `review-ask-questions` then appended the open-questions section with Q01 to
  Q18 through `oqm`.
- The plans, the two edited documents and `.vscode/settings.json` are
  uncommitted on branch `git-cliff-provisioning`. The user settled seven
  spelling findings: `extractall`, `getmtime`, `isascii`, `JOBOBJECT`,
  `STARTUPINFOEXW` and `mktree` were added to the project dictionary, and the
  coined `fakeable` was replaced by "replaceable in tests". markdownlint
  reports 0 issues and cSpell finds no unknown word on the four documents.

### Writer response for plan git-cliff-provisioning (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Writer notes for this first
round:

- The manifest admits no pin from Step 1 to the admission step: the design
  admits a pin only by the reviewed manifest edit that follows its evidence, so
  every earlier test uses synthetic pin tables. Q03 asks whether the admission
  should move before the launcher step.
- Several plan choices protect existing contracts rather than add behavior: the
  new bootstrap entry kinds keep the single set literal of `bootstrap.main`
  that the cross-site status test parses, and the launcher's Ctrl+C filter is a
  handler routine because the null routine is inherited by git-cliff (Q14,
  Q15).
- The test leaf names in the step file lists do not all follow the
  `test_<module>` convention; Q11 proposes the renaming, and the file lists stay
  as written until the user decides.
- The developer-run native checks and the evidence harness run outside pytest.
  The 2.7.0 download in the evidence run relies on the evidence-only exception
  the user authorized on 2026-11-13, carried unchanged from requirement Q16.
- The plan names no private path or consumer; "my-project" is not needed.

### Reviewer focus for plan git-cliff-provisioning (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.git-cliff-provisioning.md`
- `.reviews/a.review-requested.plan.v0.14.0.git-cliff-provisioning.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-15T13:36:58+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan git-cliff-provisioning round 1

Disposition: changes-requested. The implementation structure broadly follows the approved design, but the formulation has unresolved lifecycle, acquisition, discovery and evidence-validation contracts. These are more than wording changes.

The eight-step decomposition, empty manifest until reviewed admission, independent cache lock, creation-time job membership, inherited use guard, record-free reuse, finite D/W policy and process-free pytest strategy are sound. The proposed module splits in Q04 and Q12 reduce credible line-budget pressure. The existing Git adapter really has one subprocess boundary and no input argument; the existing paths adapter wraps discovery errors, so the proposed typed errors need changes at both boundaries. The shared lock decoder is a small, feasible extraction. No implementation or test run is being claimed by this specification review.

The body deliberately retains the original choices while Q03/Q04/Q06/Q11/Q12/Q16 propose alternatives. That is acknowledged pending-decision structure, not accidental drift. All eighteen user decisions remain pending. Reviewer agreement below neither decides them nor authorizes consolidation.

1. **R1 — High: contained-child cleanup can deadlock before the job closes.** Plan lines 688–691 join captured-output reader threads before return; lines 716–719 close the job only when the call returns; lines 1780–1782 explicitly allow unbounded reap. A child can create a descendant that inherits a pipe write handle. After the direct child exits normally or is terminated, the reader still cannot see EOF while that descendant lives, and the job that would end it is not closed until after the join. This defeats the stage deadline. The plan also specifies faults before creation and in the recording callback, but not failed ResumeThread, process-time lookup, waits or termination after a child exists. Define job-wide teardown before blocking pipe joins on every completion/failure path, preserving direct-child status and proving actors have ended before writable-state cleanup. Add fake descendant/pipe scenarios and explicit post-creation API failures; add a bounded native descendant check. Do not justify a failed termination call with the assertion that the kernel will end a successfully terminated process. The approved design's containment/reap ordering stays authoritative; do not invent permission to delete staging while death is unconfirmed.

2. **R2 — Medium: first acquisition of 2.7.0 has no implementable input contract.** Step 4 (lines 979–1012) requires expected_size before streaming. Step 7 (lines 1463–1468 and 1496–1500) obtains the first size and digest from that download, yet Candidate and provision_candidate already require both. No acquisition input type, pre-download size source, first-download cap or transition into the immutable trust record is specified. A fake returning a ready-made Candidate hides this gap. Define the evidence-only acquisition path separately from ordinary verified provisioning, including where its size bound comes from, how the parent computes the first identity, retry/deadline/recording behavior, when write_once occurs and how incomplete acquisitions are discarded. Keep the existing HTTPS exception confined to 2.7.0 evidence. This needs an additional question if the writer must choose a new size/trust policy; see the proposed question in the writer instructions.

3. **R3 — Medium: outside-worktree fallback excludes bare repositories.** Lines 1332–1335 and 1796–1798 define no-worktree exclusively as exit 128 plus `fatal: not a git repository`. A bare repository is not a worktree, but `rev-parse --show-toplevel` diagnoses `fatal: this operation must be run in a work tree`. The requirement says the default applies outside a worktree; the plan instead returns 69. A read-only Git invocation in bare mode reproduced the different diagnostic. Use a typed worktree-presence check (or an equivalently complete classified discovery result), distinguish no worktree from genuine configuration/access/corruption errors, and test plain directory, bare repository, nested worktree and genuine discovery failure. Preserve configuration validation and the unchanged error behavior of other callers. This corrects the implementation mapping of an existing requirement; it does not reopen pin selection.

4. **R4 — Medium: retirement's partial state and retry path are unspecified.** Lines 1147–1149 rename the executable and then its directory; lines 1764–1767 say directory-rename refusal leaves the entry in place. Its directory may remain, but its executable has already moved. A subsequent attempt must cope with that canonical directory lacking `git-cliff.exe`, including parent death between the renames, a pre-existing missing executable and a failed publication after retirement. A naive repetition of the first rename permanently fails with missing-file error. State the exact residual files and next-attempt algorithm under the lock, with death checks for attempt cleanup; do not claim unchanged entry contents. Tests must inject failure at both renames and publication, then show the next eligible caller can repair without deleting an in-use entry. This refines the approved two-rename protocol rather than substituting a different publication design.

5. **R5 — Medium: Q16's approval binding is not defined enough to enforce.** Option B hashes “the bundle's other content,” without defining serialization, referenced-file coverage or rerun invalidation. Step 7 preserves classification/audit entries by hunk identity, so the plan also needs to state how an existing review behaves when inputs or evidence change. Define a deterministic digest projection excluding the review object, bind the copied configuration and both trust records through verified digests, require the explicit approving decision and correct role/date fields, and reject a stale review when covered content changes. A byte-identical covered projection may retain approval. Tests must reject absent, rejected and stale review, tampered referenced evidence and a content change after approval. This is an implementation detail of recording the already-required human review, not a new human gate.

6. **R6 — Medium: native evidence must prove passing checks, not just record outcomes.** Lines 1628–1630 require a structurally complete record with outcomes, while lines 1678–1680 allow a row to name a “recorded native check.” A complete record of failure, timeout or skipped checks can meet those words. Require successful outcomes and expected observations for every check due at that milestone; missing, failed, timed-out or skipped required checks block completion. For Q06's incremental records, declare the due subset explicitly and require the full set at final acceptance. Record the tested source revision or relevant source digest so final evidence can be tied to the implemented native code. Keep those checks outside pytest; pytest reads and validates their committed evidence. Add negative fixture cases for these failure states.

Wording-only repairs: links at plan lines 360–362 need `../../../instructions/...`, since the plan is under `docs/v0.14.0/`; apply the same correction to any matching links. In both plans, distinguish the constant number of reuse operations from hashing's linear byte cost instead of calling the complete reuse O(1). These do not themselves prevent convergence.

### Question verdicts for plan git-cliff-provisioning round 1

All choices below are reviewer recommendations. Every user decision remains pending.

| Question | Reviewer choice | Assessment of options, scope and needed wording |
| --- | --- | --- |
| Q01 | A | Clear implementation sequencing question; the choices differ in when the ignore rule lands. Step 3 is sufficient if it precedes every cache-writing operation, including incremental manual checks. Say this explicitly when combining with Q06. No need to reopen the requirement that the first write is ignored. |
| Q02 | A | Clear, materially distinct ownership choices. A shared strict decoder keeps both lock implementations independent and avoids duplicating parsing rules. Preserve current operation-lock diagnostics and tests. No design expansion is needed. |
| Q03 | B | The reordered harness, evidence/admission and launcher steps are feasible: the harness depends on the service, not the launcher. Update both plans, dependency maps, acceptance owners, commands and cumulative file baselines together after a human choice. Move the Git stdin change with the harness; do not retain the old Git line baseline that assumed launcher changes had landed. Q06's incremental native checks and final complete rerun still apply. C is incompatible with the approved reusable harness, so label it as requiring a design change rather than an equally compliant route. |
| Q04 | B | The alternatives have distinct module boundaries. Separate ctypes declarations/loader from lifecycle and guard from the outset. This is a justified plan-level split; add the new module and loader coverage to the step lists and line budgets. |
| Q05 | A | Explicit injection is suitable and more visible than module patching. It does not by itself cover the production default-loader path: test that path through a fake loader and test signature declarations without OS calls. Extend fault coverage to R1's post-creation cases. C contradicts the stated coverage gate and should be marked noncompliant, not just costly. |
| Q06 | B | Early native checks are useful evidence for the layers that depend on them; the options genuinely differ in when evidence is obtained and committed. Identify checks executable at each step, their prerequisites and passing gates (R6). Step 2 checks must not rely on the not-yet-created cache; Step 4's stalled worker check can use disposable recorded staging; Step 5 covers the integrated service. The final full run remains required. |
| Q07 | A | Location follows the existing native-recorder convention and avoids importing process-starting recorder code in pytest. The record must validate success and provenance, not only structure (R6). Replace the claim that A is the “only” testable option: B is also testable but adds unnecessary production coverage obligations. |
| Q08 | A | Clear location choice. Keeping a compact versioned bundle beside the engine supports manifest references and later item reuse. The proposed location does not itself admit a pin. No missing choice here. |
| Q09 | A | A deterministic fast-import stream fits the approved fixture. The optional Git input belongs at the existing subprocess boundary: use supplied input bytes without also setting stdin, and retain current stdin behavior when absent. Cover both branches process-free. All object identities and configuration controls from the design remain required. |
| Q10 | A | Parent recomputation makes the file actually consumed by extraction the verified object. Distinct from trusting the worker's report; the extra read is already documented and linear in archive bytes. No missing policy question. |
| Q11 | B | Module-based leaves plus prefixed topic files fit affected-test selection and the file ceiling. Preserve separate acceptance/evidence leaves. Rename file lists, commands and validation references consistently after the decision; this changes organization, not proof obligations. |
| Q12 | B | Three fake modules have distinct responsibilities and avoid a foreseeable late split. Keep the native kernel fake separate. With Q03 B, the harness fake appears in new Step 6, not old Step 7; update cumulative budgets and imports accordingly. |
| Q13 | A | Matches existing launcher codepage behavior and explicit restoration. The options are implementation-level, though they affect console behavior. Keep the simulation/source checks for restoration on readiness errors and normal child return. No requirement change is needed. |
| Q14 | A | A real handler routine avoids the inherited NULL-handler ignore flag and preserves the child's decision about Ctrl+C. B instead depends on C-runtime signal handling and C on repeated polling; A expresses the contract directly through the existing native seam. Keep the ctypes callback referenced and test handler removal on errors as well as success. |
| Q15 | A | One bootstrap with module-level dispatch/status tables preserves readiness and the existing unique literal contract. Worker and gcliff status passthrough must be checked independently of the release kinds. This is a feasible implementation choice, not a new command surface. |
| Q16 | B, revised | Recording the already-required user review in committed evidence is reasonable; no extra approval is being introduced. The option needs R5's exact digest projection, referenced-input binding and stale-review rules before it is implementation-ready. A standalone review document could also bind a digest, so revise C's disadvantage to the extra artifact/coordination cost rather than implying binding is inherently difficult. |
| Q17 | A | The manual audit with a recorded checklist and immutable source revision satisfies the design; observed statuses alone (C) explicitly do not. Include dependency versions/source references where they affect helper, parser or panic exits. Do not treat a grep list or a few observed statuses as proof of exclusion. No need to write harness source-discovery code now. |
| Q18 | A, wording adjusted | Failing once when the published entry cannot be guarded avoids an implicit second provisioning cycle and fits the existing error contract. Do not claim manual deletion is the only cause: a concurrent repair or external interference can also make the open fail. Report the actual cause and path; issue the ready message only after the usable invocation exists. No extra retry budget is justified. |

No existing question needs removal. Some rejected alternatives already violate confirmed constraints (notably Q03 C, Q05 C and Q17 C); state that explicitly so pending human choices are not presented as reopening settled design by accident. R2 requires a missing acquisition question if the resolution adds a policy. R1/R3/R4/R6 primarily need concrete implementation and validation contracts; do not multiply human questions for consequences already required by the design.

### Requested changes for plan git-cliff-provisioning round 1

Requested changes:

Another review round is required because:

- R1 must remove the descendant-pipe/job-close deadlock and define post-creation failure cleanup with explicit tests.
- R2 must supply an implementable, bounded first-acquisition contract for the authorized 2.7.0 evidence candidate.
- R3 must map all ordinary no-worktree cases, including bare repositories, to the required default pin while retaining genuine discovery failures.
- R4 must specify and test recovery from partial retirement/publication.
- R5 must make Q16's approval digest and invalidation rules precise enough to enforce.
- R6 must require successful, relevant native evidence rather than structurally present outcomes.

Reviewer recommendations for Q01–Q18 are A, A, B, B, A, B, A, A, A, A, B, B, A, A, A, B (revised), A, A (wording adjusted). They remain proposals awaiting the user. The reviewer has not modified the specification or its decisions, and does not authorize consolidation.

### Writer instructions for plan git-cliff-provisioning round 1

Revise the reviewed plan and its paired validation skeleton for R1–R6, then publish a new specification-review request. Do not consolidate pending Q01–Q18 or mark any reviewer recommendation as a human decision. Preserve the explicit distinction between the current body and proposed alternatives. Updates needed to make an alternative implementable can be placed in its question while the original body remains pending consolidation.

For R1, write an ordered lifecycle covering setup failure, child-created-but-not-resumed failure, normal root exit, deadline expiry, wait/termination errors, descendant-held pipes, job teardown, pipe closure/drain and guard release. Test that cleanup cannot run on unconfirmed death. Keep the design's creation-time membership, noninherited parent job handle and recording-before-resume invariants. If a finite post-termination policy requires a new budget or retained-failure behavior beyond the approved design, expose that as a design clarification rather than silently changing the contract.

For R2, add a question such as: “How does the evidence-only first acquisition of 2.7.0 obtain a bounded archive before its immutable size and digest exist?” Two viable formulations to compare are (A, recommended) obtain asset name/size from certificate-verified release metadata, then use the ordinary size-bounded contained worker, compute the digest in the parent and write the immutable HTTPS-trust record once; (B) a separate evidence-only acquisition mode with an explicitly chosen finite size cap, recording actual size/digest after completion. A reuses the metadata worker and exact-size guard but needs metadata availability; B avoids that metadata dependency but introduces a new cap and worker mode that needs design clarification. Neither authenticates the first digest independently or broadens the existing exception. State failure/retry behavior, interrupted first acquisition and the typed transition into Candidate. If an already-approved source supplies size, cite it and make the mechanism explicit instead of asking a redundant question.

For R3, keep ordinary release discovery semantics unchanged while giving gcliff an explicit no-worktree classification. Test bare repositories separately from plain directories; do not catch every GitCommandError as absence. For R4, state the on-disk state after each successful rename and each failure, and prove subsequent repair with fault-injected tests, including an executable already absent. For R5, revise Q16 B with a precise content projection and validation/invalidation rules; update bundle fields and negative tests when that option is selected. For R6, define stage-specific and final passing evidence sets, source provenance and refusal of failure/timeout/skipped evidence.

Keep real subprocess/network checks outside pytest, retain fake-clock timing tests, and update file budgets for the added lifecycle branches, evidence validator and acquisition path. If Q03/Q04/Q06/Q11/Q12 are later accepted, renumber and rename all affected step references, validation sections, test commands, ownership maps and cumulative baselines together. Correct the relative instruction links and complexity wording as minor polish. No implementation edits or native test execution are requested in this specification round.

### Final reviewer decision for plan git-cliff-provisioning round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-15T13:54:05+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Review round: 2

### Requestor assessment for plan git-cliff-provisioning (round 2)

Writer assessment of the git-cliff-provisioning implementation plan, round 2.

The six round 1 findings are accepted and applied in the plan body, the
questions and the validation skeleton. The plan now states an ordered child
lifecycle with a confirmed job-wide teardown before any pipe join (R1), a
bounded first acquisition for the 2.7.0 evidence candidate behind the new Q19
(R2), a typed worktree-presence classification covering bare repositories
(R3), the exact on-disk states of retirement and the next caller's repair
(R4), an enforceable review binding inside Q16 option B (R5), and native
evidence that must pass for the current sources (R6).

Open questions: nineteen plan questions (Q01 to Q19), all with a pending user
decision. Q19 is new, as the reviewer proposed. Question wording was adjusted
where the reviewer's verdicts asked for it (Q01, Q03, Q04, Q05, Q06, Q07, Q09,
Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18); no option, recommendation or ID was
removed, and each revision is marked "revised after review round 1". The
writer does not find another missing question: the R1, R3, R4 and R6
contracts follow from the design and are stated in the body, and the one
policy choice they raised (R2) is Q19.

One round 1 wording repair is not applied: the relative instruction links at
the cited plan lines already resolve. From `docs/v0.14.0/`,
`../../instructions/run-pw.md`, `../../rules/run_commands.md` and
`../../instructions/groundhog.md` exist, while `../../../instructions/run-pw.md`
points outside the repository (checked with `test -f` on 2026-11-15); the
item 2 plan uses the same form.

Please assess whether the R1 to R6 revisions are complete and consistent with
the approved design (in particular, that the unconfirmed-end handling uses only
states the design already defines and that no finite post-termination budget
was introduced), whether Q19's options and recommendation are sound, and
whether any further question is missing.

### Change summary for plan git-cliff-provisioning (round 2)

Changes to `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md` and its
validation skeleton since round 1:

- R1, Step 2: `run_contained` is specified as seven ordered phases (setup,
  creation, pre-resume, wait, job-wide teardown, drain, unconfirmed end). The
  teardown calls `TerminateJobObject` on every path after creation, then waits
  on the root and polls `ActiveProcesses` to 0 before the reader threads are
  joined; the parent closes its pipe write-end copies right after creation.
  Failures of the identity lookup, the recording callback and `ResumeThread`
  tear down and confirm before raising. A failing termination, wait or count
  query raises `UnconfirmedEndError`, joins no reader and keeps the job handle
  open. Tests cover a fake descendant holding stdout and every post-creation
  failure; budgets grew (windows_child 500, fake kernel 310). Step 5: on an
  unconfirmed end, installation keeps staging and the lock record and the
  invocation keeps its guard copy. A native descendant-teardown check was
  added to the Step 8 recorder and to the acceptance map.
- R2, Step 7: `AssetListing`, `EVIDENCE_ONLY_VERSIONS = {"2.7.0"}` and an
  ordered `acquire_candidate` (listing, size-bounded recorded download,
  parent digest, extraction and probe, then `write_once`), following Q19's
  recommended option while it is pending; new failure tests; candidates
  budget 260.
- R3, Step 6: `GitExecutionContext.worktree_presence` (`INSIDE`,
  `NO_WORKTREE`, `NO_REPOSITORY` from `rev-parse --is-inside-work-tree`) and
  `paths.find_worktree`, used only by `gcliff`; `discover_project` unchanged.
  Tests cover a plain directory, a bare repository, a `.git` directory, a
  nested worktree folder and genuine failures. The confirmed facts record the
  `LC_ALL=C` environment and the observed `rev-parse` outputs.
- R4, Step 5: `retire_entry` lists the states after each rename and failure,
  and the next caller's algorithm; tests inject failures at both renames,
  between them, with an executable already absent and at publication. The
  risk pass no longer says the entry is left in place.
- R5, Q16 option B: canonical-JSON projection without `review`, a `files`
  member binding `cliff.toml` and both trust records by SHA-256, the review
  fields, refusal and staleness rules, and the negative tests. Option C's
  disadvantage was reworded.
- R6, Step 8: a validator requires `passed`, expected observations, bounds,
  the commit and current source digests for every required check, with
  negative records; the acceptance map and completion criteria now name
  passing native checks. Q06 option B lists the due set of each milestone.
- Wording: the complexity bound distinguishes the constant number of reuse
  operations from the linear hash pass, in both plans. The links were kept
  (see the assessment).
- Questions: Q19 added; Q01, Q03 to Q07, Q09 and Q11 to Q18 reworded as the
  verdicts asked, each marked "revised after review round 1".
- markdownlint reports 0 issues and cSpell finds no unknown word on both
  plans; the companion was copied from the document section byte for byte.

### Writer response for plan git-cliff-provisioning (round 2)

Writer response:

Writer response to the round 1 answer:

- R1 accepted. The plan keeps the design's unbounded reap, but only after a
  successful termination call: a returned outcome now always means a
  confirmed end of every job member. The unconfirmed-end path adds no budget
  and no new state: it leaves exactly what a dead parent leaves (staging, the
  lock record with its recorded children, the child-held guard), which the
  design's recovery rule already handles, and the parent's own end still
  closes the job.
- R2 accepted through the proposed Q19, with your option A recommended: the
  asset size comes from the same certificate-verified release metadata the
  harness already reads for 2.14.2, and the trust record is written only after
  extraction and probe succeed. Option B is kept as the alternative that would
  need a design clarification.
- R3 accepted. `--is-inside-work-tree` was chosen because one call separates
  all three cases (`true`, `false`, exit 128) under the controlled `LC_ALL=C`
  environment; other callers keep `discover_project`.
- R4 accepted; the next caller starts from the state it finds, so a partial
  retirement never needs the first rename again.
- R5 accepted inside Q16 option B, since the body keeps the step journal
  until the user decides.
- R6 accepted; for Q06's incremental option the due sets are listed in the
  option itself.
- Wording: the complexity repair is applied. I disagree with the link repair:
  the links resolve from `docs/v0.14.0/` and the proposed `../../../` form would
  break them (evidence in the assessment). This is the only disagreement, and
  it concerns no finding.

### Reviewer focus for plan git-cliff-provisioning (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-15T14:00:05+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan git-cliff-provisioning round 2

The full current plan, all nineteen questions, the validated round 2 request and the revised validation skeleton have been assessed against the approved design. Disposition: changes-requested for one remaining lifecycle contract, R1 below. This is a focused continuation of round 1 R1, not a reopening of the approved containment design.

R2 is resolved: AssetListing supplies the exact size before the recorded first download, the parent hashes the bytes, and trust publication follows successful extraction and probing. Q19 makes the remaining acquisition choice explicit without extending the 2.7.0 exception. R3 is resolved by the typed worktree observation and the bare-repository and .git cases. R4 now defines recoverable partial retirement states and retries. R5 is resolved in proposed Q16 B by the canonical projection, referenced-file hashes and stale-review refusal. R6 now requires passing checks, expected observations, bounds and current source digests, including milestone due sets and the final complete rerun.

R1's normal and timeout paths are substantially repaired: job-wide termination and confirmed zero membership precede pipe-reader joins, and post-creation failures enter teardown. No finite post-termination budget was added. The retained staging and lock records can use the existing recovery rules, provided owner death is still required as well as recorded-child death. However, retaining a live job until the parent's own end is not yet a complete executable contract: reader shutdown and retained resource ownership remain unspecified. The concrete failure is detailed in the requested changes.

The writer is correct about the relative links. From docs/v0.14.0/, ../../instructions and ../../rules reach this repository's root. My round 1 suggestion to add a third parent component was incorrect and is withdrawn. Keep the existing links.

All Q01-Q19 user decisions remain pending. The alternatives proposed in questions are intentionally unconsolidated with the body. Agreement with those proposals is not approval to consolidate or implement them. No additional human policy question is needed to finish the resource-lifetime contract; it can be specified within the current containment and recovery design without a new budget or persisted process-state value.

### Question verdicts for plan git-cliff-provisioning round 2

These are reviewer recommendations only; all nineteen human decisions remain pending. Each question is in scope and materially distinct. No question needs removal. The revised questions incorporate the requested round 1 qualifications.

| Question | Choice | Current assessment and reason |
| --- | --- | --- |
| Q01 | A | Step 3 precedes the first cache write; the revised temporary-path rule also covers earlier Q06 checks. |
| Q02 | A | One neutral strict decoder avoids drift while preserving existing operation-lock behavior. |
| Q03 | B | Harness, evidence/admission, then launcher is a feasible dependency order. The option now explicitly carries both plans, commands, ownership maps and line baselines together; C correctly requires a design change. |
| Q04 | B | Separate declarations, lifecycle and guard modules give clear responsibilities and a shared fakeable loader. |
| Q05 | A | Explicit injection with default-loader and declaration coverage fits the process-free gate. Include the remaining R1 retention/shutdown cases; C is correctly identified as noncompliant. |
| Q06 | B | Incremental passing native proof detects assumptions before dependent steps; milestone due sets and a final full rerun now make the gate concrete. Use stand-in callers where the production launcher is not yet present, and verify the actual launcher in its final-step run. |
| Q07 | A | The existing tests-tree recorder convention is appropriate. Success and source provenance are now required, and B is no longer described as untestable. |
| Q08 | A | A bundle beside the shipped manifest has a stable consumer-facing reference. |
| Q09 | A | Byte-stable fast-import inputs and the existing Git boundary support reproducibility. The revised input/stdin handling is explicit. |
| Q10 | A | The publishing parent verifies the bytes extraction will consume, independently of worker reporting. |
| Q11 | B | Module-named leaves with topic files preserve affected-test mapping and manageable file sizes; the proposed coordinated rename is complete. |
| Q12 | B | Separate common, child and harness fakes avoid a predictable later split; the Q03-dependent step reference is explicit. |
| Q13 | A | Existing UTF-8 record handling and codepage restoration preserve non-ASCII paths; error and success checks are included. |
| Q14 | A | A referenced Win32 handler routine avoids passing the ignore flag to the child; cleanup on errors is specified. |
| Q15 | A | Dispatch and status tables share the readiness boundary while keeping worker and launcher passthrough separately tested. |
| Q16 | B | The exact canonical projection excludes only review, binds the three referenced files, and invalidates changed evidence. This resolves round 1 R5. |
| Q17 | A | A recorded manual audit with dependency source references satisfies the approved requirement; observations alone remain explicitly insufficient. |
| Q18 | A | One accurate failure avoids another provisioning cycle; actual cause/path and ready-line timing are now specified. |
| Q19 | A | The existing certificate-verified metadata worker supplies an exact size before the first download. The ordinary worker and D remain unchanged, trust publication follows verification, and the exception stays limited to 2.7.0. B adds a new cap/mode and correctly requires design clarification. |

Q07's introductory reference to a test that checks only structure can be polished to say success and provenance, consistent with its revised recommendation. This is wording only. No further question is missing: the remaining R1 work defines ownership and shutdown consequences of the existing fail-closed contract rather than choosing a new product policy.

### Requested changes for plan git-cliff-provisioning round 2

Requested changes:

#### R1 follow-up for plan round 2: make unconfirmed-end retention survive unwinding and interpreter shutdown for plan git-cliff-provisioning (round 2)

Priority: high. References: plan Step 2, lines 712-715 and 754-778; Step 3, lines 893-898 and check_entry; Step 5, lines 1245-1249 and 1261-1272; validation Steps 2, 3 and 5.

The new path raises UnconfirmedEndError without joining readers and leaves the job handle open until the parent ends. That alone does not establish that the parent can end. If TerminateJobObject fails while a descendant holds a captured pipe open, an ordinary non-daemon Python reader remains blocked in its read. CPython shutdown waits for non-daemon threads, so the parent cannot exit, its job handle never closes, and the descendant never receives the promised kill-on-close. The deadlock has moved from the explicit join to interpreter shutdown. The plan does not specify a reader daemon/cancellation policy that excludes this execution.

The same path needs a concrete retained-resource owner. Saying that an invocation keeps its guard is insufficient for a reuse probe inside cache.check_entry, before an invocation has been returned, especially while Step 3 still says every failure closes the guard. Specify who holds the job, process/thread and pipe handles and guard after the error is caught and local objects are discarded, and how ordinary finally/context-manager/close paths avoid releasing the retained protection. Do not make exception-object reachability the only lifetime guarantee. Also define error data when GetProcessTimes fails and teardown fails in turn: the required creation-time identity does not exist at that point, so UnconfirmedEndError cannot unconditionally require it. The child must remain suspended and must not be given a fabricated identity or recorded as safe to recover.

Requested repair: retain the chosen approach with an explicit process-lifetime resource owner and readers that cannot block interpreter exit (for example, daemon readers using native pipe handles and private capture buffers, without shutdown-time joining or closing a Python buffered object held by a blocked reader), or specify another concrete shutdown-safe mechanism consistent with the design. State the optional/unavailable identity representation, transfer the guard from check_entry on this exceptional path, and preserve owner-and-recorded-child DEAD recovery rules. This does not require a new finite reap budget, new on-disk recovery state, or new human question.

Validation: process-free fault cases cover failed termination with a live pipe-holder, failed wait/query, failed identity lookup followed by teardown failure, and a reuse-probe error before invocation construction. Assert retained ownership through caller cleanup and the reader configuration that prevents an implicit shutdown join. A bounded native helper check should inject the failing teardown call while keeping the real kill-on-close job, let the parent exit normally, and observe parent and descendant termination; the supervising recorder must bound and clean up the check if the parent hangs. The existing normal-root-exit descendant check does not cover this failure path.

R2-R6 require no further substantive changes. Another review is required because R1 affects executable lifecycle safety, not just wording.

### Writer instructions for plan git-cliff-provisioning round 2

Revise only the remaining unconfirmed-end contract described in R1 and its validation expectations, then request another review. Keep the accepted R2-R6 changes, the existing relative links, and all pending user-decision markers. Do not consolidate Q01-Q19 or renumber steps on the reviewer's authority.

Specify how the selected retained-job approach survives normal stack unwinding and Python interpreter shutdown. An explicit process-lifetime owner for unresolved native resources, with pipe readers that cannot prevent process exit, is one compatible implementation. Define the pre-identity failure case without inventing a valid PID/creation-time identity. State how reuse-check guard ownership transfers before an invocation object exists, and exempt UnconfirmedEndError from ordinary close-on-failure and release paths. No new timeout or persisted liveness state is requested.

Carry the same rules into Steps 2, 3 and 5 of the validation skeleton and process-free fault tests. Include a bounded native helper check proving that normal parent exit after injected teardown failure does not wait forever for a pipe-holding descendant. Keep the existing all-recorded-children-and-owner-DEAD recovery predicate. Where Q06 names a launcher before its implementation step, clarify that the early check uses a stand-in caller and the final run exercises the production launcher.

### Final reviewer decision for plan git-cliff-provisioning round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-15T14:07:18+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Review round: 3

### Requestor assessment for plan git-cliff-provisioning (round 3)

Writer assessment of the git-cliff-provisioning implementation plan, round 3.

The round 2 R1 follow-up is accepted and applied in Steps 2, 3, 5 and 8, the
risk pass, Q05, Q06 and Q07, and Steps 2, 3 and 5 of the validation skeleton.
The unconfirmed-end path now has an explicit process-lifetime owner,
`windows_child.RETAINED`, which only appends the job, process, thread and pipe
read handles and retained guards and never closes them; readers are daemon
threads that read the native pipe handles with `ReadFile` into private
buffers, so interpreter shutdown never waits for them, and the parent's
normal exit closes the retained job handle and lets kill-on-close end the
members. `UnconfirmedEndError` carries `pid` and an optional identity: a
failed identity lookup followed by a failed teardown yields `identity=None`,
with the child left suspended, unrecorded and never resumed. `UseGuard.retain()`
and `CacheLock.retain_record()` make the ordinary `close()` and `release()`
paths leave the guard and the record in place, and `check_entry` retains the
reuse probe's guard before any invocation exists. The recovery predicate is
unchanged: the owner and every recorded child must be `DEAD`. No timeout, no
on-disk state and no human question was added.

Open questions: nineteen (Q01 to Q19), all pending. Q05, Q06 and Q07 carry the
round 2 wording; Q06 now uses a stand-in caller in the Step 5 due set and the
production launcher in the final run.

Please assess whether the retention and shutdown contract is complete and
consistent with the design's containment and recovery rules, whether the new
process-free cases and the native teardown-failure exit check cover it, and
whether any question remains missing.

### Change summary for plan git-cliff-provisioning (round 3)

Changes to `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md` and its
validation skeleton since round 2, all for the R1 follow-up:

- Step 2: phase 3 states the pre-identity unconfirmed end (`identity=None`,
  child suspended and unrecorded); phase 4 makes the readers daemon threads
  over native handles with private buffers; phase 7 moves every unresolved
  handle into `RETAINED` and exempts it from every `finally`, context manager
  and `close()` path. New bullets define `RETAINED`, the `pid` and optional
  identity of `UnconfirmedEndError`, and `UseGuard.retain()`. The tests cover a
  failed termination with a live pipe holder, failed wait and query, a failed
  identity lookup followed by a failed teardown, reader configuration and no
  `CloseHandle` of retained handles; fake pipes release their blocked reads at
  test teardown. Budgets: `windows_child.py` 530, test files 380 and 140.
- Step 3: `check_entry` retains the guard on `UnconfirmedEndError` from the
  probe; `CacheLock.retain_record()` makes `release()` leave the record; the
  recovery rule (owner and every recorded child `DEAD`) is restated.
- Step 5: the installation calls `retain_record()` and keeps staging; the
  invocation retains its guard; the lifecycle tests cover the reuse probe
  before any invocation and the pre-identity case.
- Step 8: the recorder gains the teardown-failure exit check (injected failing
  `TerminateJobObject` over the real kernel and job, parent exits normally,
  descendant ended, bounded by the recorder's own job); the validator's
  required set, the acceptance map row and the risk pass name it.
- Questions: Q05 adds the retention and shutdown cases, Q06 adds the new check
  to the Step 2 due set and uses a stand-in caller in Step 5, with the
  production launcher in the final run; Q07's description says the test
  checks passing outcomes and provenance. Each is marked "revised after review
  round 2" where reworded.
- markdownlint reports 0 issues and cSpell finds no unknown word on both
  plans; the companion was copied from the document section byte for byte.

### Writer response for plan git-cliff-provisioning (round 3)

Writer response:

Writer response to the round 2 answer:

- R1 follow-up accepted as proposed: an explicit process-lifetime owner and
  daemon readers over native handles. The owner is a module-level registry,
  so the retained handles never depend on an exception object staying
  reachable, and nothing closes them before the process ends.
- The pre-identity case keeps the PID that `CreateProcessW` returned, for
  diagnostics only; no creation time is invented, and the child is never
  recorded, so its staging directory stays recoverable once the owner is
  `DEAD`, as the design already states for a suspended unrecorded child.
- The guard handoff before an invocation exists is done by `check_entry`
  itself, the only code holding the guard at that moment.
- Thank you for withdrawing the link correction; the links are unchanged.
- No disagreement remains.

### Reviewer focus for plan git-cliff-provisioning (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-15T14:12:47+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan git-cliff-provisioning round 3

The full current implementation plan and all nineteen open questions have been assessed against the validated round 3 request and the companion validation plan. No substantive revision remains in this formulation.

Round 2 R1 is resolved. The unconfirmed-end path now transfers native handles and guards to the module-level process-lifetime owner RETAINED, independently of exception reachability. Daemon readers use native ReadFile handles and private buffers rather than Python file wrappers. Neither ordinary cleanup nor interpreter shutdown waits for those readers; process exit closes the retained job and activates kill-on-close. UnconfirmedEndError permits identity=None after a failed creation-time lookup; that child is suspended, never resumed and never recorded with an invented identity.

Ownership is explicit at each caller boundary: check_entry retains a reuse-probe guard before any invocation exists, invocation retains its guard, and installation retains its lock record and staging. close(), context-manager exit and release() preserve retained resources. Recovery still requires the owner and every recorded child to be DEAD; no new recovery exception or timeout policy was introduced.

The tests now cover retained ownership, forbidden joins/closes, missing identity, reader configuration and caller cleanup. The native recorder injects termination failure over a real job, requires the helper parent's normal exit and consequent descendant termination, and contains the check in a separate bounded supervising job. Q05, Q06 and the validation plan carry these obligations. Q06 uses a stand-in caller before the production launcher exists and requires the final run against the actual launcher.

Earlier substantive resolutions remain intact: bounded first acquisition of 2.7.0, defaults outside a worktree, recovery from partial retirement, evidence approval binding and staleness, and native evidence proving passing outcomes against current source digests. This is specification convergence, not implementation or native-validation evidence. All steps remain unimplemented.

The two-parent relative instruction links are correct for docs/v0.14.0/ and must remain unchanged. The earlier suggestion to add a third parent was withdrawn in round 2.

### Question verdicts for plan git-cliff-provisioning round 3

These are reviewer recommendations, not human decisions. Q01-Q19 are in scope, distinct and sufficiently clear; their alternatives state relevant consequences, including options that would require design changes. No missing substantive question was identified.

| Question | Choice | Assessment and reason |
| --- | --- | --- |
| Q01 | A | Add the ignore rule before the first cache write; earlier native checks use temporary paths. |
| Q02 | A | A neutral strict decoder avoids record-parser drift and preserves existing lock behavior. |
| Q03 | B | Harness, evidence/admission, then launcher is a feasible dependency order. Both plans, commands, ownership maps and line budgets must move together after the decision. |
| Q04 | B | Separate native declarations, lifecycle and guard responsibilities with one injectable loader. |
| Q05 | A | Explicit injection covers ordering and failures without processes; the revised retention, daemon-reader and pre-identity cases complete the requested proof. |
| Q06 | B | Incremental passing native checks test assumptions before dependent steps. Stand-in callers and the final production-launcher rerun make the milestone sets feasible. |
| Q07 | A | The established tests-tree recorder convention now explicitly validates success and source provenance. |
| Q08 | A | Store shipped admission evidence beside the shipped manifest in a stable package path. |
| Q09 | A | A byte-stable fast-import stream uses the existing Git boundary with explicit input/stdin behavior. |
| Q10 | A | The publishing parent verifies the staged bytes extraction will consume. |
| Q11 | B | Module-named leaves and topic files preserve test discovery and manageable sizes; coordinate the proposed path changes. |
| Q12 | B | Separate common, child and harness fakes avoid a predictable later split, including Q03-dependent step references. |
| Q13 | A | UTF-8 runtime-record handling supports non-ASCII paths and restores the codepage on success and errors. |
| Q14 | A | A referenced Win32 handler routine handles parent interrupts without inheriting an ignore flag into the child. |
| Q15 | A | Dispatch/status tables retain one readiness boundary and independently tested passthrough behavior. |
| Q16 | B | The canonical projection excludes review, binds all three referenced files and rejects stale approval after covered changes. |
| Q17 | A | A recorded source audit with dependency references meets the approved audit requirement; observations alone do not. |
| Q18 | A | An accurate cause/path diagnostic preserves one provisioning cycle and prints readiness only for a usable invocation. |
| Q19 | A | Certificate-verified metadata supplies the first exact size; the ordinary bounded worker and parent verification precede immutable trust publication. The exception remains limited to 2.7.0. |

Every User decision remains pending. The alternatives and proposed answers may converge while those decisions remain explicitly human-owned.

### Convergence evidence for plan git-cliff-provisioning round 3

Covered wording:

The recommendation covers the complete current plan, its Q01-Q19 options and proposed answers, and their consistency with the current validation skeleton. In particular it covers Steps 2, 3 and 5 resource retention; the Step 8 native recorder and evidence validator; and Q05/Q06/Q07 revisions. It retains the approved budgets, containment baseline, recovery predicate and evidence-only 2.7.0 exception.

The plan body still describes the baseline implementation order while pending questions propose coordinated alternatives. That is an explicit pending decision, not an approval to reorder now. All nineteen User decision fields remain pending.

Convergence rationale:

The remaining round 2 finding has a concrete ownership and shutdown contract, tests for each affected boundary, and a bounded native check of normal parent exit with a pipe-holding descendant after injected termination failure. The validation plan agrees with that contract. The prior findings remain resolved, and the current questions provide complete, materially distinct options with supported recommendations.

Only optional wording polish remains. Recommend convergence of this reviewed formulation, subject to the human-owned gate and the user's outstanding Q01-Q19 decisions. This recommendation neither confirms consolidation nor claims implementation or native tests have passed.

### Writer instructions for plan git-cliff-provisioning round 3

No substantive revision is requested. Preserve the current lifecycle, retention and recovery obligations, including their process-free and native checks.

Optional wording polish: replace "the design's five lifecycle steps" before the seven implementation phases with "the design lifecycle, expanded into the following seven implementation phases." This changes no behavior.

Do not mark Q01-Q19 decided from this review. Route the convergence recommendation through the existing human gate. If the user later chooses the proposed reordering or module/test splits, propagate those choices through both plans, file lists, commands, acceptance ownership and cumulative budgets during the authorized consolidation workflow. Keep the existing two-parent instruction links.

### Final reviewer decision for plan git-cliff-provisioning round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-16T09:33:28+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-16T09:35:42+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for plan git-cliff-provisioning (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Review round: 4

### Requestor assessment for plan git-cliff-provisioning (round 4)

Writer assessment of the git-cliff-provisioning implementation plan, round 4:
the follow-up review of the user's decisions.

At the round 3 convergence gate the user selected "Explain undecided
questions". Each of Q01 to Q19 was explained one at a time and the user
recorded an explicit decision on each, on 2026-11-15. The scanner reports 19
questions and 0 undecided, with no diagnostics. Every decision matches the
recommended option: Q03 B, Q04 B, Q06 B, Q11 B, Q12 B and Q16 B (Q16 as
revised after round 1), all others A. No question was removed or consolidated;
each answer section now ends with a `User decision: confirmed: ...` record
(colon separator, which the scanner accepts) stating the choice and date.

User comments and clarifications recorded in the document:

- Q11 B carries the user's amendment: everything release related stays
  grouped inside one overall group above any module. A clarifying question
  settled that this group is the existing folder
  `tests/unit/tools/release_workflow/`: every new git-cliff leaf goes directly
  in it, beside the item 1 and item 2 leaves, with no extra `git_cliff` level
  and no groundhog named group. The writer checked the current plan: every
  planned leaf and helper (`git_cliff_support.py`, `native_kernel_fake.py`,
  `git_cliff_native_checks.py`) is already under that folder, so the amendment
  adds a placement constraint to option B's renames and moves no path.
- Q04 B carries a size clarification: after rounds 1 and 2, option C's single
  module grew to about 660 lines (over the 650 ceiling) and option A's
  `windows_child.py` to about 530. Option C's own text in Q04 still shows the
  pre-round figure of about 560; the answer section states the current figures.
- Q19 A was decided last; the user then held the follow-up review and lifted
  that hold for this round.

No notion was introduced in any document during the discussion.

Reconciliations that the decisions require at consolidation, not performed
now (the plan body and the validation skeleton are unchanged since round 3):

- Q03 B: renumber Steps 6 to 8 (6 evidence harness, 7 evidence run with the
  user's review and the admission of 2.14.2, 8 `gcliff` launcher, alias,
  integrated acceptance, native checks and documentation); the Git input
  change (Q09) moves with the harness; file lists, commands, the acceptance
  map, baselines and the validation skeleton follow.
- Q04 B: add `tools/release_workflow/windows_native.py` beside
  `windows_child.py` and `windows_guard.py` from Step 2, with its own budget.
- Q06 B: native check due sets per milestone (Steps 2, 4, 5), a stand-in
  caller in Step 5, the full rerun with the production launcher in the final
  step (Step 8 after the renumbering).
- Q11 B: rename the leaves and topic files as option B lists, inside
  `tests/unit/tools/release_workflow/`.
- Q12 B: three helper modules (`git_cliff_support.py` Step 3,
  `git_cliff_children_fake.py` Step 5, `git_cliff_harness_fake.py` in the
  harness step), native fake kept separate.
- Q16 B: the body still says the step journal alone records the user's review;
  it gains the `review` and `files` members of `bundle.json` and the
  `require_admissible` refusals.

Please review the whole plan for consistency between the nineteen decisions,
the Q11 amendment, the Q04 clarification and the body; their combined effect
(for example Q03 B renumbering against the Q06 B due sets and the Q12 B helper
steps); the effect on the design, the requirement and the umbrella; whether
the reconciliation list above is complete; and whether the decisions raise any
new question. Reviewer recommendations cannot overwrite the user's choices:
surface any conflict instead.

### Change summary for plan git-cliff-provisioning (round 4)

Changes to `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md` since the
round 3 convergence answer:

- The round 3 covered wording edit (Step 2 lifecycle lead-in) is applied, as
  reported at the gate.
- Each of the nineteen answer sections (Q01 to Q19) gained one
  `User decision: confirmed: option X, ...` record stating the choice, its
  qualifications and the date 2026-11-15. Q11 records the user's amendment
  and its clarification; Q04 records the current size figures of options A
  and C.
- No question block, option, recommendation or answer text was otherwise
  changed; the body and the validation skeleton are unchanged.
- No other document of the effort changed since round 3.
- The scanner reports 19 questions, 0 undecided, no diagnostics; markdownlint
  reports 0 issues and cSpell finds no unknown word; the private companion was
  copied from the document section byte for byte.

### Writer response for plan git-cliff-provisioning (round 4)

Writer response:

Writer response to the round 3 convergence answer:

- The convergence recommendation and the reviewer's per-question verdicts
  (Q01 to Q19: A A B B A B A A A A B B A A A B A A A) match every decision the
  user then recorded.
- The covered Step 2 wording edit stays applied.
- This round reviews the user's decisions and comments, which the round 3
  answer could not see. The body integration of the six B decisions is left
  to the authorized consolidation, as the specification review rules require.
- No disagreement remains.

### Reviewer focus for plan git-cliff-provisioning (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-16T09:45:40+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for plan git-cliff-provisioning round 4

The recorded human decisions are mutually consistent and remain within umbrella item 3. No new question or unresolved human choice is needed. I independently agree with A A B B A B A A A A B B A A A B A A A, including the Q11 folder amendment and the current Q04 size clarification.

Q03 B and Q06 B are compatible: Steps 2, 4 and 5 establish native evidence using stand-ins and the service; the harness in Step 6 depends on the Step 5 service, not the public launcher; Step 7 gathers and reviews compatibility evidence before admitting the pin; Step 8 adds the production launcher and reruns the entire native set. Q12's harness fake consequently starts in Step 6. No production admission is needed for the earlier synthetic tests or stand-in checks.

Q04 B, Q05 A, Q07 A, Q11 B and Q12 B fit together: the three native modules have an explicit fake API seam, their recorder remains outside pytest, and their tests and helpers remain directly within the existing release_workflow test folder. The module split preserves the 650-line ceiling without changing the native proof obligations.

Q16 B strengthens the existing evidence-review requirement without changing admission authority. The human approves the exact covered bundle; the harness can generate evidence without admitting a pin; require_admissible refuses missing, rejected, malformed, stale or tampered evidence. Q17's source audit, Q19's narrowly authorized baseline acquisition and Q10's parent-computed digest remain separate necessary checks. The admission test and real manifest/default edit belong with Step 7 under Q03, whereas launcher acceptance belongs with Step 8.

The requirement's raw-output compatibility scope and the umbrella's separation of item 3 from rendering, setup and cutover remain intact. The design's ignore-rule timing is satisfied by adding the rule before the earlier cache writer in Step 3; this is the already explained Q01 interpretation. The design's bundle and developer-run checks permit the selected binding and milestone implementation details. No earlier-phase decision needs reopening.

The request correctly identifies the six B decisions requiring later body integration. Its list is complete at decision level. The writer instructions below make their mechanical consequences explicit, including moving the native validator with the recorder, the admission/default tests with admission, and maintaining source-bound evidence after source changes. These are applications of confirmed choices, not additional requirements or questions. The intentionally pre-consolidation body and validation skeleton do not themselves justify another review round.

This is a specification assessment only. It establishes neither implementation completion nor a successful native run, compatibility comparison or admission.

### Question verdicts for plan git-cliff-provisioning round 4

All nineteen questions are in scope, materially distinguish their alternatives, and have explicit human decisions dated 2026-11-15. None is missing, redundant or substantively unclear after reading its recorded clarification. I would choose the following answers for the stated reasons; reviewer agreement does not replace those human decisions.

| Question | Reviewer choice and verdict |
| --- | --- |
| Q01 | A, agree. Step 3 adds the ignore rule before the first cache writer, preserving the design's purpose. |
| Q02 | A, agree. The shared strict record decoder removes divergent validation while preserving operation-lock behavior. |
| Q03 | B, agree. Harness 6, reviewed admission 7, launcher and final acceptance 8 preserve dependencies and avoid provisional pins. |
| Q04 | B, agree. Separate native bindings, child lifecycle and guard modules from Step 2 keep responsibilities and size manageable. The updated 530/660 estimates supersede the older option figures. |
| Q05 | A, agree. An explicit injected API seam permits process-free coverage of the native wrapper behavior. |
| Q06 | B, agree. Committed milestone evidence proves assumptions when introduced, with stand-ins until the final production-launcher rerun. |
| Q07 | A, agree. The manually run recorder and committed validated evidence belong in the existing test tree without importing the recorder into pytest. |
| Q08 | A, agree. The committed production-domain bundle remains available to admission and later rendering work. |
| Q09 | A, agree. A deterministic fast-import stream fixes object inputs; optional input must not be combined with stdin. |
| Q10 | A, agree. Parent hashing checks the actual staged bytes independently of the worker report. |
| Q11 | B with the user's amendment, agree. Module-based leaves and prefixed topic files retain size limits, all directly below tests/unit/tools/release_workflow/, with no extra git_cliff folder or named groundhog group. |
| Q12 | B, agree. Concern-specific helpers start in Steps 3, 5 and 6; the native kernel fake stays separate. |
| Q13 | A, agree. Save, switch and restore the console codepage across readiness errors and normal child exit, consistent with the launcher contract. |
| Q14 | A, agree. The parent's handler routine ignores console interrupts without setting the inheritable null-handler ignore flag for git-cliff. |
| Q15 | A, agree. Shared bootstrap dispatch keeps one source of behavior and preserves the existing main-body set-literal contract. |
| Q16 | B as revised, agree. The canonical digest and verified file hashes bind explicit human approval to the exact evidence admitted. |
| Q17 | A, agree. A source audit at the exact revision establishes the status-69 exclusion; observed exits alone cannot prove it. |
| Q18 | A, agree. A newly published entry that cannot be guarded fails once with its actual cause/path, without claiming readiness or provisioning again. |
| Q19 | A, agree. Verified metadata supplies the first baseline size bound, the parent records the digest after successful extraction/probe, and the exception remains limited to 2.7.0. |

The Q19 review hold was explicitly lifted. No undecided question or new human choice remains in this formulation; consolidation is still a separate human gate.

### Convergence evidence for plan git-cliff-provisioning round 4

Covered wording:

Only wording polish remains in the reviewed questions and answers:

- In Q04's option descriptions, align option A's child-module estimate with approximately 530 lines and option C's combined-module estimate with approximately 660 lines, explicitly above the 650-line ceiling. The recorded clarification already establishes these figures.
- In Q06 option B, replace "the launcher (which Step 6 delivers)" with "the launcher (delivered in Step 8 under confirmed Q03 B)". Its recorded user decision already says this.
- In Q12 option B, replace the conditional harness-helper step reference with "git_cliff_harness_fake.py (Step 6 under confirmed Q03 B)".

These edits align explanatory option text with its explicit decisions and do not change any selected behavior. Routine body integration belongs to later authorized consolidation.

Convergence rationale:

Recommend convergence of this reviewed formulation. The nineteen explicit decisions, the Q11 placement amendment and the Q04 size clarification are complete, mutually consistent and within the requirement/design/umbrella scope. The selected implementation order and milestone evidence have no unresolved dependency. The request's reconciliation list covers the substantive decisions; the writer instructions spell out their direct consequences without adding a new decision. Only stale explanatory wording in option text remains. No new question and no outstanding human answer is required. Convergence remains advisory: the human retains the separate consolidation choice and the later real compatibility-evidence approval.

### Writer instructions for plan git-cliff-provisioning round 4

Preserve every recorded user decision and the Q11 amendment. No substantive revision or additional question is requested before convergence. Apply the covered wording polish if desired; do not consolidate under reviewer authority.

When the human authorizes consolidation, carry the already selected decisions into both plans together:

- Apply Q03 to steps, dependencies, file lists, commands, ownership maps and cumulative baselines: harness and Git input in Step 6; evidence run, audit, actual user review, manifest/default edit and admission/schema/configuration tests in Step 7; launcher, alias, integrated acceptance, final native rerun and documentation in Step 8. Keep synthetic manifest fixtures before admission.
- Apply Q04 to all Step 2 files, module tests, API imports and line budgets for windows_native.py, windows_child.py and windows_guard.py. Use the current estimates; estimates remain advisory and the 650-line ceiling remains binding.
- Apply Q06 and Q07 by moving the recorder, evidence record and process-free evidence validator/tests to Step 2, then extending them in Steps 4 and 5. Preserve the exact due sets, temporary Step 2 paths, disposable Step 4 staging, Step 5 stand-in caller and final production launcher. Validate milestone-appropriate checks against current exercised-source digests; an exercised source change cannot leave a stale record accepted. Refresh affected evidence as the already selected current-source rule requires.
- Apply Q11's module-to-leaf rule throughout, including file lists, commands, validation links and maps, without changing proof obligations. Keep all leaves and helper modules directly below tests/unit/tools/release_workflow/; acceptance/evidence leaves retain their established names. Apply Q12's support/children/harness split at Steps 3/5/6, with cumulative budgets and imports updated.
- Apply Q16's review and files fields, exact canonical projection, reader checks, admission refusals and negative tests in the Step 6 bundle implementation; Step 7 obtains and records the real human decision before admission. Preserve a rerun's review while invalidating it when the covered projection changes. The step journal remains additional evidence, not the admission binding.
- Remove obsolete pending/conditional wording now settled by the user, including Q19 and the Q03-dependent step references. Keep Q01's first-write ignore guarantee and Q17/Q19's complete audit/acquisition obligations explicit. No expansion into later umbrella items is needed.

These are the concrete integration consequences of existing decisions. They do not authorize implementation, real evidence approval or consolidation in this reviewer session.

### Final reviewer decision for plan git-cliff-provisioning round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-16T10:34:26+01:00
- Exchange: specification/plan/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
