# Specification review transcript for v0.14.0

- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-13T11:32:02+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
Review round: 1

### Requestor assessment for feature-request git-cliff-provisioning (round 1)

Writer assessment of the git-cliff-provisioning feature request, round 1.

The requirement is the first written form of umbrella item 3, built from the
focused child draft the human approved on 2026-11-13. It keeps the six item 3
acceptance criteria of the umbrella and groups the supporting umbrella
contracts by topic: the pin and its notation, the internal versioned cache,
direct invocation through `GIT_CLIFF` and the `gcliff` launcher, the
provisioning sequence and per-asset integrity data, the operations that need
the binary, the Windows x64 scope (Q1 A), the failure contract (decision 21),
the 2.7.0 to 2.14.2 comparison with the pinning policy, and the consumer inputs.
Its current-behavior section was checked against the repository: the release
engine has no git-cliff code, the shipped schemas are `tooling` and `version`
only, `.gitignore` has no `.tools/git-cliff/` entry, and dev_workflow's
`update-changelog.sh` calls `${PRGS}/git-cliffs/current/git-cliff.exe` (2.7.0).

Open questions: fourteen are proposed (Q01 to Q14), all with a recommended
option and a pending user decision. They target behavior the umbrella leaves
unstated for this item:

- the pin: which exact versions a project may declare (Q01) and an omitted pin
  when the llm-shared default changes (Q02);
- the cache: what makes a cached binary valid (Q03), its scope across
  llm-shared checkouts and unwritable checkouts (Q04), the item owning the
  ignore rule (Q05) and entries for pins no longer used (Q14);
- provisioning behavior: lock waits and stale locks (Q06), supported network
  environments (Q07), messages and output channels (Q08) and provisioning
  ahead of time (Q09);
- `gcliff`: which project's pin it uses (Q10), an invalid `.release.ini`
  (Q11) and when the alias joins llm-shared's alias set given the existing
  global-senv `gcliff` (Q12);
- the compatibility evidence this item delivers, given that items 4 and 8 own
  the configuration and the parity rehearsals (Q13).

The writer considers the question set sufficient for a feature request, with
no design-level question: the cache layout below the fixed path, the lock
mechanism, the download client, extraction, the digest source, output formats
and exit-code numbers are left to the design, as the scope section states.

Please assess the whole specification independently: completeness against
umbrella item 3 and decisions 17 to 21, 31 and Q1 A; consistency with the
ownership boundaries of items 1, 2 and 4 to 8; any missing question; and
whether each question's options and recommended answer are sound.

### Change summary for feature-request git-cliff-provisioning (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md` was written
  by `write-requirement` from the approved child draft
  `docs/v0.14.0/draft.v0.14.0.git-cliff-provisioning.md`, with type
  feature-request, version v0.14.0, slug git-cliff-provisioning and test group
  whole suite.
- `review-ask-questions` then appended the open-questions section with Q01 to
  Q14 through `oqm`.
- Both files are untracked on branch `git-cliff-provisioning`; the umbrella
  draft is unchanged. markdownlint reports 0 issues and cSpell finds no
  unknown word.

### Writer response for feature-request git-cliff-provisioning (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Writer notes for this first
round:

- Two inconsistencies inherited from the umbrella are raised as questions
  rather than fixed in the body before a human decision. The gap list makes
  this item ignore `.tools/git-cliff/`, while the llm-shared consumer input
  says the item 8 cutover does it (Q05). The body says llm-shared supplies the
  `gcliff` alias in its alias set, while the umbrella item 3 entry says
  "setup/cutover expose the alias" (Q12).
- Q12 relies on an observation outside the repository: the user's global senv
  defines `gcliff` as the `PRGS` 2.7.0 binary, and a consumer that loads
  llm-shared's `senv.doskey` would see that alias overridden.
- The supported-platform sentence keeps the umbrella wording "The v0.14.0
  release tooling", although main already released v0.14.0 without this
  tooling. The writer offered "This release tooling" at the draft review gate;
  the human approved the draft unchanged, so the requirement keeps the
  approved wording.
- The scope section lists the digest source among the design topics, so no
  question asks where the expected digest comes from; Q01 and Q03 bound only
  the observable outcome (accepted pins, and what a valid cached copy means).

### Reviewer focus for feature-request git-cliff-provisioning (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.feature-request.v0.14.0.git-cliff-provisioning.md`
- `.reviews/a.review-requested.feature-request.v0.14.0.git-cliff-provisioning.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-13T12:38:37+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request git-cliff-provisioning round 1

The requirement faithfully carries item 3's six acceptance criteria and the confirmed internal-cache, exact-pin, Windows x64, invocation and preflight boundaries. It distinguishes proposed 2.14.2 compatibility from completed evidence. The fourteen questions cover the principal pin, cache, launcher and ownership decisions; none needs to be deleted simply for being outside this feature.

Disposition: changes-requested. The formulation needs substantive corrections before convergence: Q12 promises per-project alias timing that a single shared macro file does not provide; Q13 must define the comparison boundary and reconcile comparison-version admission with Q01; Q14 overstates deletion safety; and there is no bounded-failure policy for network access and executable validation. Q03 should explicitly order integrity checking before execution of an existing cache entry.

Evidence reviewed: the full current requirement and exact round-1 request; the umbrella's automatic provisioning contract and item 3 boundary; senv.doskey and senv.bat:32; and tools/dev_workflow/update-changelog.sh. The latter invokes git-cliff first and only subsequently injects notes, attaches the external header and applies cleanup/fix rules. No versioned review transcript was used as assessment context. No binary compatibility run or fresh upstream integrity lookup was performed, and neither is claimed by this review.

All Q01-Q14 user decisions remain pending. Reviewer recommendations below are advisory. Preserve the approved draft and confirmed umbrella decisions; revise the proposed questions and their reasoning without consolidating or recording a human decision. Existing questions already expose the cache-ignore and alias-ownership tension; do not silently resolve those cross-document choices in the requirement body.

### Question verdicts for feature-request git-cliff-provisioning round 1

| Question | Assessment and reviewer choice |
| --- | --- |
| Q01 | Relevant missing policy, with materially different options. Choose B: admit only explicitly tested production pins and diagnose unsupported values before mutation. This is a proposed restriction, not something already mandated by umbrella decision 19. Reconcile the 2.7.0 comparison/candidate workflow in Q13 so obtaining compatibility evidence does not require that evidence to exist already. |
| Q02 | Relevant default-lifetime question. Choose A: an omitted setting follows the executing checkout's tested default, while an explicit pin survives a tooling update. Explain that changing the checkout/default can change output on the next release; item 6 reports this through its upgrade workflow, but ordinary checkout updates are not automatically guaranteed to have passed that workflow. Avoid calling every update inherently reported. |
| Q03 | Relevant and distinct from archive verification. Choose A with explicit ordering: verify the existing executable against locally recorded integrity data before launching its version check, then require the exact pinned version. Archive integrity and the extracted executable's locally recorded digest are distinct. Missing or mismatching local verification data makes the entry invalid. Storage and hashing mechanisms remain design work. |
| Q04 | Mostly a clarification of the fixed-path contract. Choose A: use only the executing checkout's cache, with no cross-checkout or per-user fallback. Say that a required write denied by permissions fails with the setup diagnostic. Avoid promising either blanket rejection or successful use of every read-only installation without specifying which lock/validation writes are needed. |
| Q05 | Relevant cross-document ownership correction. Choose A: item 3 guarantees effective ignore coverage before its first cache write; item 8 verifies it. This preserves the existing acceptance criterion. Keep the recorded source wording and flag the corresponding umbrella consumer bullet for authorized reconciliation. |
| Q06 | Relevant concurrency/interruption policy. Choose A: bounded waiting, observable contention and safe automatic recovery after establishing that the previous owner is no longer active. Never equate elapsed lock age alone with proof that the owner died, and never clean another live caller's temporary installation. Exact ownership tests and limit values belong in design. |
| Q07 | Relevant network-support policy, with a scope-expanding mirror option. Choose A: GitHub through documented standard proxy configuration and OS-trusted certificates, retaining certificate verification and no new mirror setting. Do not claim this covers every current corporate installation without evidence. Define bounded network failure under the additional question below; exact downloader and trust-store integration remain design work. |
| Q08 | Relevant observable output policy. Choose A for concise stderr provisioning messages, silent valid-cache reuse and unchanged git-cliff stdout/exit propagation. Qualify the distinct provisioning-code promise to the admitted/tested git-cliff versions, with verification in design. Include Q06's lock-wait message as a permitted additional message so the one-or-two-line limit does not contradict contention reporting. |
| Q09 | Useful operational clarification. Choose A: first-need provisioning plus documented prewarming through bin/gcliff.bat --version. The direct launcher works before alias exposure; use the alias form once exposed. Setup can recommend this without gaining a mandatory download. |
| Q10 | Relevant project-selection ambiguity. Choose A: resolve the current directory's worktree and its configuration, including from a nested directory; pass all git-cliff arguments through. No worktree or no pin uses the default, subject to Q11's whole-file validation. A target argument pointing elsewhere does not select that other project's pin. Call this argument passthrough rather than unconditional drop-in compatibility. |
| Q11 | Mostly clarification of the existing common-reader rule. Choose A: validate the whole discovered .release.ini and report any invalid declaration without falling back. B changes the established reader contract and C undermines exact pinning; label those consequences explicitly. |
| Q12 | Necessary question, but A's stated per-project guarantee is unsupported. A shared senv.doskey entry affects every console that loads that file after the change, including consumers still using legacy uc. Choose a corrected A: item 3 ships/tests the direct launcher, setup/cutover own alias exposure, and adding the alias to the shared file at item 8 is explicitly a shared exposure affecting all loaders. Record the possible mixed-version interval. If the desired guarantee is instead per-project activation, offer it as a distinct option with explicit scope/ownership consequences rather than implying the shared file already provides it. |
| Q13 | Necessary evidence-boundary question. Choose A with a precise comparison definition: identical frozen repository/history/range and explicit legacy config/CLI inputs for both versions; compare raw git-cliff output and classify differences. Header attachment, note injection and Perl fixes are postprocessing in update-changelog.sh, so raw comparison cannot claim coverage of those stages. Item 4 rechecks its new renderer and item 8 performs final parity. State how comparison candidates are obtained/verified before admission to Q01's production tested set; do not assert unverified 2.7.0 integrity availability. |
| Q14 | Relevant retention policy. Choose A after removing “always safe.” Keep complete versions until deliberate manual deletion with no active users; deletion loses offline availability until successful reprovisioning. Clean only abandoned partial state after establishing ownership/death under Q06. This policy avoids automatic eviction; it cannot guarantee safety of arbitrary manual removal. |

Missing question: What bounded failure behavior applies to release metadata lookup, asset download and executable --version validation when a server stalls or a process never exits?

- Option A (recommended): all provisioning-controlled network operations and version probes have documented finite time budgets, with bounded retries if any. Expiry reports the pin, internal path and failed stage, leaves no accepted partial entry, and releases recoverable lock state without changing the project. Design selects values and mechanisms.
- Option B: bound lock acquisition only and let network operations/probes wait indefinitely. Simpler, but a caller holding the lock can hang all first-use releases despite Q06's bounded waiting for other callers.
- Option C: require manual cancellation/recovery for a stalled holder. Adds an operator dependency contrary to automatic first-use provisioning.

Choose A. This specifies the externally observable availability contract; it does not choose a client, timeout number or lock mechanism. Add it as a new pending question or expand Q06 explicitly to cover these stages and their separate bounds.

### Requested changes for feature-request git-cliff-provisioning round 1

Requested changes:

1. Correct Q12's exposure model. senv.bat:32 loads the single shared senv.doskey file. Delaying an entry until llm-shared's item 8 does not wait for every consuming project's migration. Replace the false promise that gcliff and uc always switch together with an explicit shared-exposure consequence; alternatively offer actual per-project activation as a separate human choice. Do not change the confirmed alias name or fixed resolver contract.
2. Tighten Q13 and its relation to Q01. Separate raw git-cliff compatibility from final legacy/new pipeline parity, identify reproducible history/config/range inputs, and explain candidate verification versus production-pin admission. The current requirement asks to test the real header/template/parser/skip/range behavior, while invoking cliff.toml alone does not exercise the separately attached header or postprocessing. State which evidence item 3 supplies and what items 4/8 still owe. If 2.7.0 cannot be verified under the required integrity policy, surface the decision needed; do not bypass verification or silently use global senv.
3. Correct Q14's manual-deletion and partial-cleanup guarantees. Explicitly preserve the no-replacement-of-in-use-binaries contract and acknowledge loss of offline availability after manual deletion. Tie orphan cleanup to Q06 ownership checks.
4. Add the bounded-failure policy for network operations and executable version probes. A finite wait for another lock holder does not bound the holder's own download or hung probe. Specify finite stage budgets and safe failure, leaving numeric limits and implementation to design.
5. Make Q03's offline validation order explicit: integrity first, then execute --version. Explain the distinct archive digest and retained executable integrity record. This is necessary for the selected validity policy to reject a changed cached executable before running it.

These are changes to behavior/evidence guarantees rather than spelling or phrasing alone. The requested next disposition is another review round, not consolidation. No compatibility outcome, new supported pin, or user choice is asserted by this answer.

### Writer instructions for feature-request git-cliff-provisioning round 1

Revise only the reviewed formulation and question set, preserving all explicit human choices and keeping user decisions pending. Do not consolidate now. Address the requested changes and publish another automated review round through the existing requestor workflow. Use the current requirement as authority and report any necessary umbrella reconciliation rather than silently changing approved scope.

Keep Q01-Q14 identifiers stable. A new question may be Q15, or the bounded-operation policy may be integrated into Q06 if its full scope is made explicit. Apply the per-question qualifications in the verdict table; they include wording improvements for Q02, Q04, Q07-Q11 in addition to the substantive changes.

The request's closing instruction names a project-root answer file. That path conflicts with the shared artifact-home contract. The answer is published only through the core-owned path returned by status under .reviews; no root answer file is created. Correct that generated request wording at its owning source when authorized, without manually editing live exchange artifacts.

### Final reviewer decision for feature-request git-cliff-provisioning round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-13T12:53:38+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
Review round: 2

### Requestor assessment for feature-request git-cliff-provisioning (round 2)

Writer assessment of the git-cliff-provisioning feature request, round 2.

The requirement body is unchanged since round 1: it keeps the approved draft,
the six item 3 acceptance criteria and the confirmed umbrella decisions. Every
round 1 change lands in the open-questions section, which now holds sixteen
questions (Q01 to Q16), all with a recommended option and a pending user
decision. Q01 to Q14 keep their identifiers; no option was removed, and every
amended option keeps its letter.

All five requested changes and every per-question qualification of the round 1
verdict table were applied:

- Q12 now describes the shared exposure of the single `senv.doskey` file,
  loaded by llm-shared's `senv.bat` and by my-project's, and records the
  mixed-version interval for consumers still on the legacy `uc`. Per-project
  activation is offered as option D, with its scope consequence on decision 17
  and item 6.
- Q13 now limits this item's evidence to raw git-cliff output on frozen,
  recorded inputs (commit, ranges, `cliff.toml`, the `update-changelog.sh`
  flags). It names the postprocessing stages the comparison does not cover and
  what items 4 and 8 still owe, and treats the compared binaries as evidence
  candidates that are not admitted as pins. A full legacy-pipeline comparison
  is option D.
- Q14 drops the "always safe" claim, keeps the no-replacement-of-in-use
  contract, states the loss of offline availability after a manual removal,
  and ties partial cleanup to Q06's ownership check.
- New Q15 asks for finite budgets on metadata lookup, asset download and the
  `--version` probe, as the reviewer proposed.
- Q03 now orders the check (local integrity record first, then `--version`)
  and separates the archive digest from the executable's local record.

The writer also checked GitHub's release API on 2026-11-13: the 2.7.0
`x86_64-pc-windows-msvc` ZIP has no asset digest, and 2.7.0 publishes `.sha512`
sidecars for its tarballs only. Under the requirement's integrity rule, the
2.7.0 comparison binary therefore cannot be verified from upstream data. As
the round 1 answer asked ("surface the decision needed"), new Q16 asks how that
binary is trusted. It recommends a digest recorded in the evidence and accepted
explicitly by the user, limited to evidence and never admitted as a pin. Q01
and Q13 refer to it.

Missing questions: none known to the writer beyond Q15 and Q16. Please assess
whether the amended Q12 and Q13 options are sound, whether Q16 is within the
nature of a feature request (it decides an evidence trust policy, not a
mechanism), and whether any recommended answer still overstates a guarantee.

### Change summary for feature-request git-cliff-provisioning (round 2)

Changes since round 1, all inside the open-questions section of
`docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md`; the body
above it is unchanged:

- Q01: records that the 2.7.0 Windows ZIP has no upstream integrity data;
  separates obtaining an evidence candidate from admitting a pin; states that
  option B is stricter than decision 19 rather than mandated by it.
- Q02: an explicit pin survives tooling updates while it stays tested; an
  ordinary checkout update is not guaranteed to pass through item 6's report.
- Q03: integrity check of the local executable record before `--version`; a
  missing or mismatching record invalidates the entry; archive digest and
  executable record distinguished.
- Q04: no cross-checkout or per-user fallback; a denied required write fails
  with the setup diagnostic; no promise either way for a read-only checkout.
- Q05: the umbrella consumer bullet is flagged for authorized reconciliation
  instead of being reworded by the requirement.
- Q06: recovery only after the holder is established to be gone, never on
  lock age alone, and never removing a live caller's temporary installation;
  points to Q15 for the holder's own bounds.
- Q07: certificate verification always kept; no claim of covering every
  installation; points to Q15.
- Q08: the Q06 lock-wait message is allowed; the distinct exit status is
  promised for admitted versions, verified in design.
- Q09: `bin\gcliff.bat --version` works before alias exposure.
- Q10: nested directories, Q11 validation before the default, a target
  argument does not select another project's pin; "argument passthrough"
  replaces "drop-in replacement".
- Q11: options B and C labeled with their contract consequences.
- Q12: rewritten around the shared `senv.doskey` exposure and its
  mixed-version interval; new option D for per-project activation.
- Q13: rewritten around a raw git-cliff comparison on frozen inputs, its
  uncovered postprocessing stages and the evidence-candidate status; new
  option D for a full legacy-pipeline comparison.
- Q14: option A rewritten without "always safe", with the in-use contract,
  offline-availability loss and Q06 ownership check.
- Q15 (new): bounded failure of network operations and version probes.
- Q16 (new): trusting the 2.7.0 comparison binary without upstream integrity
  data.

The companion `.reviews/a.feature-request.v0.14.0.git-cliff-provisioning.open.questions.md`
matches the section. markdownlint reports 0 issues for the requirement and
cSpell finds no unknown word.

### Writer response for feature-request git-cliff-provisioning (round 2)

Writer response:

Response to the round 1 answer (changes-requested). Every requested change is
accepted; there is no disagreement.

1. Q12 exposure model: accepted. `senv.bat` loads the single shared
   `senv.doskey`, and my-project's `senv.bat` loads `..\llm-shared\senv.doskey`
   (umbrella context), so the earlier promise that `gcliff` and `uc` switch
   together per project was false. Option A now states the shared exposure at
   item 8 and the mixed-version interval; option D offers per-project
   activation as a separate human choice. The alias name and the fixed
   resolver contract are unchanged.
2. Q13 boundary and relation to Q01: accepted. The comparison is raw git-cliff
   output on a recorded commit, ranges, `cliff.toml` and flags; header
   attachment, note injection, section labels and fix rules are named as not
   covered, with item 4 and item 8 owing them. Compared binaries are evidence
   candidates that are not admitted as pins. The 2.7.0 integrity gap the
   answer anticipated is real (checked on 2026-11-13), so it is surfaced as
   new Q16 rather than bypassed or resolved through global senv.
3. Q14: accepted as requested.
4. Bounded failure: accepted as new Q15 rather than folded into Q06, so Q06
   stays about the waiting caller and Q15 about the holder's own stages; each
   question points to the other.
5. Q03 ordering: accepted.

The per-question qualifications for Q01, Q02, Q04 to Q11 were applied as
listed in the change summary. No user decision was recorded; all sixteen
remain pending.

Two observations outside the reviewed document, reported to the human rather
than changed now:

- The round 1 answer notes that the generated request's closing instruction
  names a project-root answer file, which conflicts with the artifact-home
  contract. The writer has not edited the renderer; that correction needs the
  human's authorization at its owning source.
- `oqm --append` appends a second section instead of replacing the existing
  one, while the review-time question steps describe it as a replacement. The
  writer restored the single section and kept the companion identical to it.

### Reviewer focus for feature-request git-cliff-provisioning (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-13T13:00:12+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request git-cliff-provisioning round 2

The current requirement and the complete round 2 request were assessed. The request accurately describes its revisions; all sixteen user decisions remain pending. This answer neither chooses for the user nor authorizes consolidation.

Round 1 corrections are substantially addressed: Q03 verifies the local executable record before execution; Q06 distinguishes a waiting caller from the holder and recovers only established dead ownership; Q12 now states shared alias exposure and its mixed-version interval; Q13 bounds raw-renderer evidence and assigns later pipeline checks to items 4 and 8; Q14 qualifies manual removal; Q15 adds bounded network and probe stages.

One substantive correction remains, in the new Q16 and its Q01/Q13 references. A digest calculated from a just-downloaded archive identifies those bytes and permits later equality checks; it does not verify the initial archive against independent upstream integrity data. Q16 A explicitly admits HTTPS as the sole initial trust anchor, yet Q16's answer says this is instead of bypassing verification, and Q13's answer promises never to bypass integrity verification even for evidence. The wording presents an exception as satisfying the unconditional rule. Q16 also places explicit acceptance when reviewing evidence, leaving whether execution is allowed before the trust decision unresolved.

This is a valid feature-request decision about evidence trust, rather than a download-client or storage design decision. Preserve it as a question. State precisely that it proposes a narrowly scoped exception to upstream verification for the 2.7.0 evidence candidate, require an explicit user decision authorizing that policy before its first execution, and distinguish recording/rechecking a digest from independently authenticating the initial download. Keep production provisioning fail-closed and keep the candidate out of the set/cache state accepted by normal provisioning. No new numbered question is necessary; Q16 can express this decision fully.

The umbrella's automatic provisioning sequence requires published integrity information and treats missing information as setup failure. The proposed exception must be labeled as evidence-only and flagged for authorized source reconciliation if the user selects it, just as Q05 handles its umbrella wording. Do not amend the umbrella or requirement body while those choices are pending.

Assessment scope was documentary: no comparison binary was obtained or executed, and no compatibility run is claimed.

### Question verdicts for feature-request git-cliff-provisioning round 2

| Question | Verdict and reviewer choice | Reason and qualification |
| --- | --- | --- |
| Q01 | Agree; B | Tested-pin admission is explicitly proposed as stricter than decision 19. Evidence acquisition and admission are separated. Qualify the statement that candidates are verified the same way with Q16's proposed exception. |
| Q02 | Agree; A | The executing checkout supplies the inherited default; an explicit supported pin remains fixed. Ordinary checkout updates are correctly distinguished from the item 6 reporting path. |
| Q03 | Agree; A | Integrity comparison precedes executing the probe and stays offline. The archive digest and executable record have different purposes. The local record detects divergence from publication; it is not a guarantee against simultaneous malicious replacement of both record and binary. |
| Q04 | Agree; A | A checkout-local cache preserves the fixed-path contract; denied required writes fail explicitly. Read-only reuse is correctly left dependent on design. |
| Q05 | Agree; A | Ignoring state before its first write belongs to the creator. The umbrella correction awaits the human decision. |
| Q06 | Agree; A | Bounded waiting and dead-owner recovery cover separate conditions. Age alone does not justify removing live state, and Q15 bounds the holder's own stages. Success of all callers is conditional on the download completing within their wait budgets. |
| Q07 | Agree; A | GitHub with documented proxy/trust-store integration is a clear initial scope; certificate verification remains enabled and universal environment support is not claimed. |
| Q08 | Agree; A | Standard error preserves captured output, quiet reuse avoids noise, and the distinct status is restricted to admitted versions subject to design verification. |
| Q09 | Agree; A | The direct launcher gives an early warm-up path before alias exposure, without making setup network-dependent. |
| Q10 | Agree; A | The containing worktree selects the pin and the arguments remain git-cliff arguments. The consequences of targeting another repository are explicit. |
| Q11 | Agree; A | Whole-file validation follows the common-reader contract and does not silently select a different pin. |
| Q12 | Agree; A | Shared exposure and the legacy-uc interval are now explicit. D is a meaningful alternative with an acknowledged scope change. Wording polish: say gcliff uses the project's admitted pin or executing checkout default, initially proposed as 2.14.2, rather than universally stating it runs 2.14.2. |
| Q13 | Agree with raw-output boundary; A after trust wording correction | Recorded frozen inputs make the raw-renderer comparison reproducible; later postprocessing evidence remains owned by items 4 and 8. Replace the unconditional no-bypass claim and qualify candidate verification with Q16. Keep snapshot/archive histories and parser/skip-rule coverage from the existing compatibility requirement in the evidence matrix. |
| Q14 | Agree; A | No automatic complete-entry eviction, no replacement of an in-use binary, manual removal consequences, and owned partial cleanup are all stated. |
| Q15 | Agree; A | Finite stage budgets and bounded retries complete Q06 without choosing clients or timeout values. Limit the guarantee to provisioning-controlled work, as the option does, rather than promising git-cliff rendering itself can never hang. |
| Q16 | Necessary and in scope; A only after correction | Explicitly choose an evidence-only exception to independent upstream verification, with policy authorization before first execution. HTTPS and a locally calculated hash do not retroactively provide upstream verification. B is optional corroboration, not independent authentication; C changes the evidence scope and needs the corresponding Q13/acceptance reconciliation. |

No additional numbered question is needed. Q16 needs the missing timing and exception semantics before its options and proposed answer are complete. Reviewer choices above are recommendations; every User decision remains pending.

### Requested changes for feature-request git-cliff-provisioning round 2

Requested changes:

1. Correct Q16 A and its recommendation/answer to state a proposed evidence-only exception, not upstream verification. Replace the option with wording such as: "Only after the user explicitly authorizes this evidence-only trust policy, obtain the 2.7.0 Windows ZIP from the named upstream GitHub release over certificate-verified HTTPS, record its exact asset identity and SHA-256, and run it solely for the frozen-input comparison. HTTPS is the initial trust anchor; the calculated digest identifies the downloaded bytes and is rechecked for later repetitions, but does not independently authenticate the initial archive. The evidence candidate is never admitted as a project pin or published as an entry normal provisioning accepts. Missing upstream verification data remains a setup failure for every production pin. Reviewing the resulting evidence is separate from authorizing the policy before first execution." A prior explicit selection of that fully stated policy may satisfy authorization; this does not require an extra prompt for every run. Update the analogy and pros/cons so they do not imply the hash supplies a missing upstream seal. Flag any related umbrella reconciliation for the authorized post-decision workflow.

2. Make Q01 and Q13 consistent with that choice. Qualify "verified the same way" and "through this item's download and integrity verification" with the evidence-only Q16 exception. Replace Q13's answer claim "never bypasses integrity verification ... even for evidence" with: "keeps upstream verification mandatory for production pins; an evidence-only 2.7.0 run is blocked until the explicit Q16 trust-policy decision authorizes its narrowly stated exception." Q16's description/answer should likewise say it avoids an undisclosed exception, not that calculating and accepting a new digest supplies independent verification. If the human rejects the exception, keep the comparison blocked until a different evidence policy and its scope consequences are explicitly settled.

These are one connected policy correction, not requests for a new implementation mechanism or a new numbered question. Everything else is accepted for this formulation, subject to pending human choices and the stated wording polish.

### Writer instructions for feature-request git-cliff-provisioning round 2

Revise only the open-questions formulation and its companion file. Preserve Q01-Q16 identifiers and option letters, the requirement body, all explicit earlier decisions, and every pending user decision. Do not execute a binary, consolidate, or broaden the production provisioning policy on the strength of this review.

Apply the single substantive correction in the requested-changes input to Q16 and its Q01/Q13 cross-references. Keep the accepted raw-output evidence boundary, shared-alias exposure model, and bounded-stage contract. No additional question is required.

Optional wording polish: Q12's mixed interval uses the project's pin or checkout default, initially proposed as 2.14.2; Q03's local record detects divergence rather than defeating coordinated replacement; Q06's concurrent success depends on the wait budget. These points do not independently block convergence.

After the revisions, request another automated review round. Keep all sixteen choices pending for the human. If Q16 A is later selected, retain its explicit pre-execution policy authorization and reconcile source contracts through the authorized owning workflow; later review of generated evidence is a separate acceptance step.

The current request's closing project-root answer-path instruction is stale. Follow the configured artifact-home protocol and renderer outputs; do not create or overwrite a project-root protocol answer. The renderer-source issue and the reported oqm behavior are outside this reviewed requirement and do not independently block its convergence.

### Final reviewer decision for feature-request git-cliff-provisioning round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-13T13:04:44+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
Review round: 3

### Requestor assessment for feature-request git-cliff-provisioning (round 3)

Writer assessment of the git-cliff-provisioning feature request, round 3.

The requirement body is unchanged since round 1. The open-questions section
still holds sixteen questions (Q01 to Q16) with stable identifiers and option
letters, each with a recommended option and a pending user decision.

The round 2 correction is applied as one connected policy change:

- Q16 now states option A as a proposed evidence-only exception to upstream
  verification, authorized by the user's explicit selection of the fully
  stated policy before the first execution, with no extra prompt for each run.
  It distinguishes certificate-verified HTTPS as the initial trust anchor from
  the recorded SHA-256 digest, which only identifies the downloaded bytes for
  later rechecks. The candidate is never admitted as a pin or published as an
  entry normal provisioning accepts, and production pins stay fail-closed.
  Evidence review is a separate acceptance step. Selecting option A flags the
  umbrella's unconditional integrity wording for authorized reconciliation, as
  Q05 does for its wording. The analogy, option B (corroboration, not
  authentication) and option C (scope change needing reconciliation) were
  corrected to match. Its recommendation now says that rejecting the
  exception keeps the 2.7.0 comparison blocked until another evidence policy
  is explicitly settled.
- Q01 qualifies "verified the same way" with the Q16 exception.
- Q13 option A separates 2.14.2 (upstream-verified) from 2.7.0 (Q16 policy
  only), its con says the 2.7.0 run stays blocked until Q16 is decided, and its
  answer uses the reviewer's wording on mandatory upstream verification for
  production pins.

The optional polish was also applied: Q13's evidence matrix keeps the parser,
skip-rule, snapshot-tag and archive-range coverage the compatibility section
names, with a recorded fixture history for cases llm-shared lacks; Q12's
mixed-version interval names the admitted pin or checkout default, initially
proposed as 2.14.2; Q03 says the local record detects divergence but does not
defeat a coordinated replacement of record and binary; Q06's concurrent success
depends on the waiting caller's budget; Q15 leaves git-cliff's own rendering
outside its guarantee.

The writer considers the question set complete for a feature request, with no
missing question, and asks whether the formulation is now ready for the human
convergence gate.

### Change summary for feature-request git-cliff-provisioning (round 3)

Changes since round 2, all inside the open-questions section of
`docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md`; the body
above it is unchanged:

- Q16: title now "Trusting the 2.7.0 comparison binary without upstream
  integrity data"; description, analogy, all three options, recommendation and
  answer rewritten around a proposed evidence-only exception authorized before
  first execution, with HTTPS as the initial anchor and the recorded digest
  limited to identifying the downloaded bytes.
- Q01: option B qualifies candidate verification with the Q16 exception.
- Q13: option A adds the evidence matrix coverage and separates the 2.14.2
  and 2.7.0 candidates; one con and the answer now refer to Q16's
  authorization instead of an unconditional no-bypass claim.
- Q12: the mixed-version interval and analogy name the admitted pin or
  checkout default, initially proposed as 2.14.2.
- Q03, Q06, Q15: one-sentence qualifications from the optional polish.

The companion `.reviews/a.feature-request.v0.14.0.git-cliff-provisioning.open.questions.md`
matches the section. markdownlint reports 0 issues and cSpell finds no unknown
word. All sixteen user decisions remain pending.

### Writer response for feature-request git-cliff-provisioning (round 3)

Writer response:

Response to the round 2 answer (changes-requested). Both requested changes and
the optional polish are accepted; there is no disagreement.

1. Q16: accepted. Option A uses the reviewer's proposed wording almost
   verbatim, labeled as a proposed evidence-only exception. The description
   and answer now say it avoids an undisclosed exception rather than claiming
   that a computed digest supplies verification. The analogy no longer
   implies that the lot number replaces the missing seal. The umbrella
   reconciliation is flagged for the authorized post-decision workflow; the
   umbrella and the requirement body are not amended while the choice is
   pending.
2. Q01 and Q13 consistency: accepted, including the reviewer's replacement
   wording for Q13's answer and the blocked 2.7.0 comparison if the exception
   is rejected.

The evidence-matrix coverage requested in the Q13 verdict was added to option
A. No binary was obtained or executed for this round, and no new numbered
question was added.

The renderer's root answer-path wording and the `oqm --append` behavior remain
reported to the human as outside this requirement, as the round 2 answer
confirms.

### Reviewer focus for feature-request git-cliff-provisioning (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-13T13:07:59+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request git-cliff-provisioning round 3

Recommend convergence of the reviewed formulation. I read the complete current requirement and validated round 3 request. The request accurately describes the changes. No substantive correction or missing numbered question remains; the sixteen questions give materially distinct choices, relevant consequences and supportable proposed answers.

Q16 now explicitly proposes an evidence-only exception, requires the user's policy authorization before first execution, separates initial HTTPS trust from later digest equality, excludes the candidate from production pin/cache admission, and keeps production provisioning fail-closed. Q01 and Q13 consistently refer to that exception. The required umbrella reconciliation remains flagged for the authorized post-decision workflow rather than being silently performed. Rejecting the exception leaves the comparison blocked pending another explicitly settled evidence policy.

The other earlier corrections remain intact: shared-file alias exposure and its mixed-version interval; the raw-renderer comparison boundary and recorded coverage matrix; local integrity before version execution; bounded lock waiting and holder stages; owner-aware interrupted-state cleanup; and qualified manual cache removal. The requirement body is intentionally still the recorded source formulation while its questions await decisions. Its known timing, evidence and ignore-ownership reconciliations are expressed in the relevant questions, not treated as already approved changes.

All User decision fields remain pending. Reviewer agreement is advisory and cannot authorize consolidation, an evidence trust exception, executable acquisition or execution, or implementation. This was a specification review only; no compatibility run is claimed.

### Question verdicts for feature-request git-cliff-provisioning round 3

| Question | Reviewer choice | Assessment and reason |
| --- | --- | --- |
| Q01 | B | Agree. A tested-pin set is explicitly a proposed stronger policy, with untested evidence candidates distinguished from production admission and Q16's exception stated. |
| Q02 | A | Agree. Inheritance follows the executing checkout; an explicit admitted pin persists. The unreported default-change consequence of an ordinary checkout update is visible. |
| Q03 | A | Agree. Verify the local record before execution, then check the version. Archive verification and local divergence detection have distinct roles; simultaneous record/binary replacement is outside the stated guarantee. |
| Q04 | A | Agree. Each executing checkout has its own fixed cache and required denied writes produce a setup diagnostic; read-only behavior depends on design. |
| Q05 | A | Agree. Ignore coverage must exist before the first write. The umbrella's cutover wording is flagged for authorized reconciliation. |
| Q06 | A | Agree. Bounded contention waiting and established dead-owner recovery preserve live temporary installations. Concurrent success is correctly conditional on the wait budget. |
| Q07 | A | Agree. GitHub, documented proxy behavior and operating-system trust with certificate verification define a useful initial scope without a mirror feature. |
| Q08 | A | Agree. Standard-error notices leave captured output intact; valid reuse stays quiet; distinct provisioning status is constrained to admitted versions and must be verified in design. |
| Q09 | A | Agree. The direct launcher's version call warms the cache before alias exposure without making setup network-dependent. |
| Q10 | A | Agree. The containing current worktree selects configuration, including from nested directories, and target arguments do not secretly choose a different pin. |
| Q11 | A | Agree. Whole-file validation preserves the common-reader rule and avoids silent fallback. |
| Q12 | A | Agree. Item 3 delivers the launcher/definition; cutover exposes the shared alias, with the mixed-version consequence stated. Per-project activation remains an explicit scope-changing alternative. |
| Q13 | A | Agree. Frozen inputs and the parser/skip/snapshot/archive matrix establish raw-renderer evidence; postprocessing and final parity stay with items 4 and 8. The 2.7.0 run now depends explicitly on Q16. |
| Q14 | A | Agree. Complete entries are retained, in-use binaries are not replaced, manual removal loses offline availability, and only abandoned owned partial state is automatically cleaned. |
| Q15 | A | Agree. Finite provisioning-stage budgets and bounded retries complement lock acquisition limits. Rendering itself is outside this guarantee. |
| Q16 | A | Agree with the stated proposed policy. It is a disclosed evidence-only exception authorized before execution, not a claim that a freshly calculated digest authenticates the first download. Production admission remains prohibited, and rejecting the exception blocks that comparison until another policy is settled. |

No missing question identified. These are reviewer recommendations, not recorded human decisions. Q01 B and Q02-Q16 A are the choices I would make; all sixteen still await the user.

### Convergence evidence for feature-request git-cliff-provisioning round 3

Covered wording:

The covered wording is the complete open-questions section Q01-Q16 of the current requirement, assessed at SHA-256 b2750c3e7cde7ecc1f6419f2497313e5ae192043553b742fefc1be27311da59b. Agree with Q01 B and Q02-Q16 A as proposed answers, without changing their pending human status.

Specifically covered: Q16 A's certificate-verified HTTPS initial trust, digest identity/rechecks, explicit policy authorization before execution, evidence-only use, exclusion from production pin/cache admission, separate evidence acceptance, and flagged umbrella reconciliation; Q01 and Q13's matching cross-references; Q13's frozen-input raw comparison with retained coverage and later pipeline ownership; and Q12's shared exposure and admitted-pin/default mixed interval.

Only optional wording polish remains: Q16 A is the simplest raw-evidence option, rather than the only one, because B adds corroboration to A. No new question or policy change follows from that edit.

Convergence rationale:

The round 2 blocking issue is resolved in the authoritative current text: the evidence-only trust exception is disclosed, authorized before execution and separated from production verification. Cross-references no longer claim that the exception satisfies independent upstream verification. All previously accepted boundaries and operational choices remain coherent, and the optional remaining edit changes no decision.

Convergence is recommended for the reviewed question formulation, not for implementation or completed compatibility validation. All sixteen human decisions are outstanding, including the tested-pin restriction and the evidence-only trust exception. The human may choose the registered next action or discuss those choices through the requestor; the reviewer cannot confirm or consolidate.

### Writer instructions for feature-request git-cliff-provisioning round 3

Present the formulation and reviewer recommendation to the human through the requestor-owned convergence gate. Preserve every pending User decision. Do not consolidate, obtain or execute the comparison candidate, or treat reviewer agreement as authorization.

No substantive rewrite or further automatic revision round is requested. Optional wording-only polish in Q16's recommendation: replace "the only option that keeps raw 2.7.0 evidence" with "the simplest option that keeps raw 2.7.0 evidence", since B includes A and also keeps the raw comparison. This does not change any option or the convergence recommendation.

If the human later chooses different options or supplies comments, reconcile their consequences across the whole requirement and its umbrella before implementation. In particular, retain Q05's ignore-ownership correction, Q12's alias timing and shared exposure, Q13's raw-output boundary and later pipeline obligations, and Q16's explicit pre-execution trust authorization and source reconciliation if selected. No earlier confirmed decision is overridden by this answer.

Publish/consume only through the configured artifact home and shared core. The generated request's stale project-root answer wording is outside this requirement and does not justify writing a project-root protocol artifact. Consolidation and any workflow continuation remain requestor/human authority.

### Final reviewer decision for feature-request git-cliff-provisioning round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-11-13T22:59:05+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-13T22:59:51+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for feature-request git-cliff-provisioning (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
Review round: 4

### Requestor assessment for feature-request git-cliff-provisioning (round 4)

Writer assessment of the git-cliff-provisioning feature request, round 4: the
follow-up review of the user's decisions.

At the round 3 convergence gate the user selected "Explain undecided
questions". Each of Q01 to Q16 was explained one at a time and the user
recorded an explicit decision on each, on 2026-11-13. The scanner reports 16
confirmed questions and 0 undecided, with no diagnostics. Every decision
matches the recommended option, without amendment: Q01 B and Q02 to Q16 A. No
question was removed or consolidated; each answer section now ends with a
`User decision: confirmed: ...` record (colon separator, which the scanner
accepts) stating the choice and date.

User comments recorded in the document:

- Q05 was decided after the user asked for a worked example (untracked cache
  files, `git add -A` and clean-tree checks between items 3 and 8).
- Q05 and Q12 each carry a "User comment (2026-11-13)" paragraph. The writer's
  chat examples had wrongly said that item 3 "lands on main"; the user
  corrected this: umbrella items land on `sibling_release_tooling`, and main
  receives the umbrella only after all items are developed, so any change
  reaching main before then is unlikely. The user kept both decisions: the Q05
  window concerns the umbrella branch and its worktrees, and under Q12 a
  consumer such as my-project sees the shared `gcliff` when the umbrella merges
  to main, with the same mixed-version interval.
- Q16 A was selected with the explicit statement that selecting it is the
  user's authorization of the evidence-only trust policy before the 2.7.0
  binary first runs.

No notion was introduced in any document during the discussion.

Reconciliations that the decisions require at consolidation, not performed
now (the requirement body and the umbrella are unchanged):

- Q05 A: the requirement's own consumer-input bullet for llm-shared still says
  its cutover "ignores the internal `.tools/git-cliff/` cache", like the
  umbrella's llm-shared consumer bullet; both become "verifies the cache stays
  ignored".
- Q16 A: the requirement's integrity subsection ("Missing verification data is
  an explicit setup failure, never a reason to skip the check") and the
  umbrella's provisioning sequence need the evidence-only exception stated, so
  that production provisioning stays fail-closed while the authorized 2.7.0
  comparison is not mistaken for a bypass.
- Q12 A: the body's "llm-shared supplies `bin/gcliff.bat` and the `gcliff`
  alias in its alias set" stays true, but the exposure timing (item 8 shared
  exposure, item 6 for consumers, recorded mixed-version interval) is stated
  only in the question.
- Q13 A and Q01 B: the compatibility section and gap item 8 do not yet state
  the raw-output boundary, the coverage matrix, or that evidence candidates are
  not admitted as pins.

Please review the whole specification for consistency between the sixteen
decisions, the user comments and the body; the effect of these decisions on
the umbrella and on items 4 to 8; whether the reconciliation list above is
complete; and whether the decisions raise any new question.

### Change summary for feature-request git-cliff-provisioning (round 4)

Changes since the round 3 convergence, all inside the open-questions section of
`docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md`; the body
above it and the umbrella draft are unchanged:

- Q16 recommendation: the covered wording edit from the round 3 answer, "the
  only option" replaced by "the simplest option".
- Q01 to Q16: each `User decision: pending` line replaced by a
  `User decision: confirmed: ...` record of the user's choice, dated
  2026-11-13: Q01 B; Q02 to Q16 A; no amendment.
- Q05 and Q12: a "User comment (2026-11-13)" paragraph each, recording that
  main receives the umbrella only after all items are developed.

Question IDs, titles, descriptions, analogies, options, recommendations and
answers are otherwise unchanged. The companion
`.reviews/a.feature-request.v0.14.0.git-cliff-provisioning.open.questions.md`
is byte-identical to the section. markdownlint reports 0 issues and cSpell
finds no unknown word.

### Writer response for feature-request git-cliff-provisioning (round 4)

Writer response:

The round 3 answer recommended convergence; its covered wording edit is
applied. This round is not a response to requested changes: it is the
follow-up review the user's "Explain undecided questions" selection requires
after every question received an explicit user decision.

Reviewer recommendations cannot overwrite these human choices. If a decision
conflicts with another decision, the body, the umbrella or a neighboring item,
please surface the conflict and the question it raises instead of proposing a
different answer.

The two items reported in earlier rounds as outside this requirement remain
open with the human: the generated request's root answer-path wording and the
`oqm --append` behavior.

### Reviewer focus for feature-request git-cliff-provisioning (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-13T23:05:39+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for feature-request git-cliff-provisioning round 4

The sixteen recorded human decisions are complete and mutually consistent. I agree with Q01 B and Q02-Q16 A. No missing question or outstanding human answer was found. The Q05 and Q12 comments correct the integration chronology without amending those choices: items integrate into sibling_release_tooling; main receives the completed umbrella. No implementation or compatibility run is claimed by this review.

The decisions were checked against the requirement body and the relevant umbrella provisioning, pin policy, consumer inputs, decision table and item 3-8 boundaries. Q01/Q13/Q16 separate acquiring evidence candidates from admitting production pins, so there is no circular requirement for prior evidence. Q03/Q07/Q16 distinguish upstream archive verification, local executable integrity and the explicitly authorized evidence-only HTTPS trust policy. Q04/Q05/Q06/Q14/Q15 give coherent cache ownership, first-write hygiene, safe contention/recovery and bounded failure behavior. Q02/Q10/Q11 establish which project and executing checkout supply validated configuration. Q08/Q09 preserve direct launcher behavior without forcing downloads during unrelated operations. Q12/Q13 preserve the item ownership split.

The requestor's reconciliation list identifies the principal topics, but is not an exhaustive location checklist. Add the umbrella item 8 acceptance bullet that still says to add the cache ignore; both pinning-policy tables that still present retaining 2.7.0 as a runtime alternative; the umbrella's alias paragraph and item 3 acceptance language; and the relevant umbrella decision rows. All sixteen decisions must survive removal of the questions, including local integrity before execution and default inheritance. These are propagation of settled decisions during consolidation, not unresolved policy choices or a request to consolidate now.

The confirmed formulation is ready for the human consolidation gate. The substantive policies are already explicit in the answers and confirmed records. The remaining incorporation into the body and umbrella has a determinate result; the added location checklist below introduces no new behavior, changes no chosen option and needs no further question-review round.

### Question verdicts for feature-request git-cliff-provisioning round 4

All questions remain relevant; none needs removal or a new alternative. The options express material tradeoffs, and the recommended answers follow the scope and ownership constraints. Each choice below is an explicit human decision dated 2026-11-13, rather than reviewer confirmation on the user's behalf.

| Question | Human choice and reviewer choice | Assessment and reason |
| --- | --- | --- |
| Q01 | B | Agree. Only tested pins are admitted; rejection lists accepted pins before mutation. Evidence acquisition remains separate, avoiding circular admission. |
| Q02 | A | Agree. Omission follows the executing checkout's tested default. Explicit pins survive while admitted; ordinary checkout updates may change an omitted pin without an item 6 report. |
| Q03 | A | Agree. Compare the executable with its local integrity record before version execution; missing or mismatching records invalidate reuse. This does not authenticate coordinated replacement of record and binary. |
| Q04 | A | Agree. Cache scope is the executing checkout/worktree, with no fallback. Diagnose required denied writes. Read-only reuse mechanics remain design work. |
| Q05 | A | Agree. Item 3 ignores the whole cache from its first write; item 8 verifies it. The interim untracked-file risk concerns the umbrella branch/worktrees, not an assumed early merge to main. |
| Q06 | A | Agree. Report bounded lock waiting and recover only after proving the owner gone; age alone is insufficient. |
| Q07 | A | Agree. Upstream GitHub over verified HTTPS, standard proxies and OS trust provide the selected network scope without a mirror requirement. |
| Q08 | A | Agree. Provisioning and contention diagnostics use stderr, valid reuse stays silent, and git-cliff stdout and exit status pass through. Provisioning failures use a status unused by admitted versions. |
| Q09 | A | Agree. Provision lazily; the direct launcher with --version provides explicit cache warming without a mandatory setup download. |
| Q10 | A | Agree. Current-directory worktree discovery, including nested directories, chooses the pin; opaque git-cliff target arguments do not change that choice. |
| Q11 | A | Agree. Launcher use validates the whole .release.ini through the common reader and never falls back after configuration errors. |
| Q12 | A | Agree. Item 3 ships/tests the launcher and alias definition; item 8 edits the shared alias file; item 6 brings aliases to consumers not loading it. Main consumers see the shared edit when the umbrella reaches main and may retain legacy uc during their accepted mixed-version interval. |
| Q13 | A | Agree. Compare raw output at recorded frozen history, ranges, config and flags with parser, skip, snapshot-tag and archive-range coverage and fixture histories for absent cases. Item 4 rechecks its renderer; item 8 owns full parity. Candidate 2.14.2 is admitted only after evidence; 2.7.0 is restricted to Q16. |
| Q14 | A | Agree. No automatic eviction of complete entries avoids deleting an in-use binary. Manual removal while unused loses offline availability; abandoned partial cleanup follows Q06 ownership proof. |
| Q15 | A | Agree. Finite documented download/probe budgets and retries bound failures, with stage diagnostics, no accepted partial entry or project mutation, and recoverable lock state. Rendering timeouts remain outside this decision. |
| Q16 | A | Agree. The user's selection already authorizes the narrow evidence-only policy before first execution. Verified upstream HTTPS anchors the initial download; the recorded asset identity and SHA-256 support byte identity and repetition, not independent authentication. No production pin or accepted cache entry results, and production missing-integrity failure remains mandatory. |

No new question follows from the comments. The distinction between integration on sibling_release_tooling and later delivery to main is compatible with both first-write cache protection and shared alias exposure. No additional per-run authorization is required for the chosen Q16 policy. Acceptance of the resulting compatibility evidence remains future work.

### Convergence evidence for feature-request git-cliff-provisioning round 4

Covered wording:

No question or answer requires substantive revision. The round 3 edit to Q16, replacing "only option" with "simplest option", is present and accepted. No outstanding human decisions remain.

The following is the deterministic incorporation checklist for a later authorized consolidation; do not apply it as reviewer edits or reopen the confirmed policies:

1. Cache ownership and chronology: in the requirement's llm-shared consumer bullet, the umbrella's matching consumer bullet, and umbrella item 8's "add ... cache ignore" acceptance bullet, use: "Item 3 ignores the whole .tools/git-cliff/ cache before its first write; item 8 verifies that it remains ignored." Keep the item's integration into sibling_release_tooling distinct from the completed umbrella's later merge to main.
2. Production pins and evidence candidates: in both pin-resolution/pinning-policy discussions and umbrella decision 19/item 3 acceptance wording, state that only recorded tested pins are admitted. Retitle or qualify the historical "Retain exact 2.7.0 temporarily" table row: "2.7.0 is an evidence-only comparison candidate under the confirmed exception, not a supported production pin." Keep 2.14.2 proposed until its compatibility evidence is recorded. An omitted pin follows the executing checkout's tested default; no silent move during a release is promised, not stability across checkout updates.
3. Integrity and provisioning: carry Q03's local integrity check before --version into both provisioning sequences. In both integrity contracts and the relevant umbrella decision/acceptance text, distinguish verified production asset acquisition from Q16's evidence-only 2.7.0 policy. State its upstream asset identity, certificate-verified HTTPS initial trust anchor, recorded SHA-256, repeated-byte checks and exclusion from normal pin admission/cache acceptance. The digest does not authenticate the initial download. The human has already authorized this policy; acceptance of its resulting evidence is separate.
4. Alias timing: qualify the requirement's alias paragraphs, gap item 6 and acceptance text, plus the umbrella alias paragraph and item 3/6/8 ownership and acceptance references. Item 3 ships/tests bin/gcliff.bat and the alias definition without editing shared senv.doskey; item 8 exposes it there; item 6 brings it to consumers not yet loading that file. Shared-file consumers receive it on their executing checkout's update, with main consumers following the umbrella merge; legacy uc may still use 2.7.0 until that consumer's migration.
5. Compatibility evidence: qualify both compatibility discussions and umbrella item 3 acceptance/decision 19, plus requirement gap item 8 and acceptance language. Item 3 establishes raw-output evidence only, using the recorded frozen commit, ranges, dev_workflow configuration and flags, and the complete parser/skip/snapshot-tag/archive-range matrix with fixtures as needed. Item 4 checks new rendering/configuration/postprocessing; item 8 compares full pipelines. Do not remove coverage merely because it is not exercised by llm-shared's existing history.
6. Preserve the other confirmed details when folding the answers into the body: checkout-local cache with diagnosed denied writes; bounded and reported lock waiting with proven-gone recovery; GitHub/standard proxy/OS trust scope; stderr/provisioning status and pass-through behavior; lazy warming; current-directory pin discovery with opaque forwarded arguments; whole-configuration validation; no automatic complete-entry eviction; bounded network/probe failures. Extend matching umbrella summaries as needed without duplicating design detail. None of these needs a new choice.

This expands the requestor's list of locations. It does not introduce an unresolved cross-document policy correction: every replacement follows an explicit confirmed answer already included in this reviewed formulation. The unchanged pre-consolidation body is not evidence that these choices have been incorporated yet.

Convergence rationale:

Recommend convergence. All sixteen user decisions are explicit, match the reviewed options and remain coherent after whole-specification and related umbrella review. No missing decision, conflicting human instruction, conditional choice requiring another answer or new substantive question was found. The integration chronology comments refine examples without changing cache or alias policies.

The compatibility and trust distinctions are sufficiently stated to proceed to consolidation: candidates are separate from admitted pins, 2.7.0 is restricted to the authorized evidence comparison, and later rendering and complete-pipeline evidence keep their owners. Actual binary compatibility evidence is an implementation obligation, not missing evidence required to settle these specification choices.

The requestor's four-topic reconciliation list needs the additional locations identified in this answer, especially umbrella item 8's cache-ignore bullet and both historical 2.7.0 pinning rows. Their result is dictated by the confirmed choices. No substantive work remains in the reviewed question/answer formulation; the remaining body/umbrella incorporation belongs to the separately authorized consolidation action. This recommendation neither performs nor authorizes that action. There are zero outstanding human question decisions.

### Writer instructions for feature-request git-cliff-provisioning round 4

Recommend convergence of the reviewed formulation; do not initiate another automated round solely for incorporating these confirmed answers. Present the durable human gate and leave Consolidate to the human. This answer does not authorize consolidation, implementation, execution of compatibility candidates, or a commit beyond authorization already recorded by the human.

When consolidation is durably authorized, preserve Q01 B and Q02-Q16 A without changing their consequences. Incorporate the decisions into the requirement and matching umbrella contract, ownership/acceptance text and decision table before removing the questions. Use the location checklist in the covered-wording section; it supplements the four-topic requestor list rather than replacing it. Preserve each confirmed decision's meaning, including accepted limitations and item boundaries.

Keep the production integrity rule fail-closed. State Q16 as a separate, already authorized evidence-only exception, never as a fallback for normal provisioning. Do not call a locally computed digest authentication of the initial download. Do not require another authorization prompt merely to repeat the selected evidence policy.

Do not claim compatibility evidence exists, admit an untested candidate, move later rendering/parity work into item 3, or imply that items land individually on main. Storage, locking implementation, output formatting and numeric status selection remain design work within the confirmed contracts.

The request's closing project-root answer-path sentence is stale adapter wording; this answer follows the authoritative artifact-home publication contract. That adapter issue and oqm --append remain outside this specification review.

### Final reviewer decision for feature-request git-cliff-provisioning round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-13T23:07:05+01:00
- Exchange: specification/feature-request/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
