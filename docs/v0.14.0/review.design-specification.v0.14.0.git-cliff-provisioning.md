# Specification review transcript for v0.14.0

- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-14T01:27:28+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 1

### Requestor assessment for design-specification git-cliff-provisioning (round 1)

Writer assessment of the git-cliff-provisioning design, round 1.

The design answers the consolidated feature request (Q01 to Q16 settled on
2026-11-13) and chooses what that requirement leaves to design: the digest
source, the cache layout below the fixed path, the local integrity record, the
lock mechanism and its recovery test, the download client, the extraction
method, the time budgets, the message formats and the exit-status numbers. Its
confirmed-facts table was checked against the code (schemas, configuration,
CLI, launcher, results, Windows process and operation lock, Git boundary,
process audit) and against upstream on 2026-11-13: the 2.14.2 Windows ZIP
digest matches GitHub's published value, the archive layout was listed without
extraction, and a standard-library `HEAD` request reached the asset through the
workstation's `HTTPS_PROXY` with the Windows certificate store.

Open questions: sixteen design questions (Q01 to Q16), each with a recommended
option and a pending user decision:

- integrity and pins: digest source (Q01) and manifest form (Q02);
- locking: lock mechanism (Q03, where the writer recommends changing the
  design's record-plus-probe lock to a kernel mutex held for the whole
  provisioning) and lock granularity (Q04);
- network: budget adjustability (Q05), retry policy (Q06) and proxy
  resolution, including proxy auto-configuration scripts (Q08);
- cache maintenance: replacing an invalid entry (Q07);
- interfaces: what the provisioning entry point returns (Q09, where the writer
  recommends an invocation object owning the `GIT_CLIFF_*` environment policy),
  how `gcliff` starts git-cliff (Q10) and its reserved failure status (Q11);
- evidence: where candidates are extracted (Q12), what the committed bundle
  contains (Q13, where the writer recommends digests plus differing hunks
  instead of raw outputs), the snapshot-tag fixture (Q14) and the harness
  surface (Q15);
- alias: where the `gcliff` macro line lives before item 8 (Q16).

Three recommendations would change the written design if accepted (Q03, Q09,
Q13); the body still states the original choice until consolidation.

Please assess the design independently: completeness against the feature
request's sixteen clarifications and acceptance criteria; consistency with the
item 1 and item 2 foundations and the ownership boundaries of items 4 to 8;
whether any question belongs to the requirement or the plan instead of the
design; any missing design question; and whether each question's options and
recommended answer are sound.

### Change summary for design-specification git-cliff-provisioning (round 1)

Round 1 has no preceding round. The reviewed document is new:

- `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md` was written by
  `write-design` from the consolidated feature request
  `docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md` (committed
  as `971e0b40` and pushed), following the item 2 design's structure.
- `review-ask-questions` then appended the open-questions section with Q01 to
  Q16 through `oqm`.
- The design is untracked on branch `git-cliff-provisioning`; the user settled
  four spelling findings, adding `getproxies`, `mangen` and `execv` to
  `.vscode/settings.json` and rewording one acceptance case as "provisioned
  again". markdownlint reports 0 issues and cSpell finds no unknown word.

### Writer response for design-specification git-cliff-provisioning (round 1)

Writer response:

No reviewer feedback exists yet for this exchange. Writer notes for this first
round:

- The design picks concrete values where the requirement leaves numbers to
  design: budgets of 30 s, 300 s, 15 s and 360 s, a 250 ms poll, statuses 2
  and 69, and the stderr message texts. Q05, Q06 and Q11 expose the choices
  most likely to need review.
- Q03, Q09 and Q13 recommend a different choice than the body states. The
  writer kept the body unchanged so that consolidation integrates whatever the
  user decides, and the question descriptions name the body's current choice.
- Q08 rests on a workstation observation: the environment proxy variables are
  set, and the Windows setting uses an auto-configuration script that `urllib`
  does not evaluate. The design names no internal host.
- The evidence-only 2.7.0 policy is carried from requirement Q16 unchanged; the
  design only places the candidate record outside the manifest and its binary
  under the `evidence/` subtree (Q12).

### Reviewer focus for design-specification git-cliff-provisioning (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.specification.design-specification.v0.14.0.git-cliff-provisioning.md`
- `.reviews/a.review-requested.design-specification.v0.14.0.git-cliff-provisioning.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-14T01:38:50+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 1

The disposition is **changes-requested**. The design covers the right item 3 boundaries and most of the confirmed requirement, but several safety and evidence claims do not yet follow from the proposed mechanisms. All sixteen design answers are proposals with `User decision: pending`; reviewer agreement below is not a human decision. The deliberate differences between the body and recommendations Q03, Q09 and Q13 are normal deferred consolidation, not independent findings.

#### D1: Mutex acquisition does not establish process death for design-specification git-cliff-provisioning (round 1)

Q03 recommends removing owner checks from partial-directory cleanup. Windows mutex ownership belongs to a thread: abandonment establishes that the owning thread terminated, not that its process exited. Ordinary acquisition after a normal release establishes neither fact about owners of residual directories. A process may still be alive after its provisioning thread exits or after cleanup fails and the mutex is released. This conflicts with the requirement's explicit process-owner-death condition for recovering locks and removing partial downloads.

Keep PID plus process creation identity and the `DEAD` condition for recovered owner records and residual staging/retired directories. Preserve directories owned by `ALIVE` or `UNKNOWN` processes. A full-duration mutex may serialize work, but its acquisition alone cannot authorize deletion. Correct Q03 A's cross-machine claim too: a local transition mutex and local PID probe do not coordinate or prove death on another machine. Define the supported cache topology and mutex namespace/session scope; a local-disk restriction needs explicit treatment rather than an unsupported assurance.

Microsoft documents thread ownership and abandonment in [Mutex Objects](https://learn.microsoft.com/en-us/windows/win32/sync/mutex-objects). No runtime experiment is needed for this mismatch.

#### D2: Numerical budgets lack an enforceable production deadline for design-specification git-cliff-provisioning (round 1)

The time-budget table and fake-clock seams specify durations, but not how synchronous `urllib` work is stopped at an aggregate deadline. Python documents its timeout as applying to blocking operations, not the whole download. DNS, proxy setup, redirects and slow continued reads must fit the same finite wall-time policy as attempts and backoff; checking a clock only between calls is insufficient when a call does not return. Candidate metadata lookup needs the same explicit treatment.

Add a decision on the enforcement mechanism, distinct from Q05's constants-versus-settings question. For example, compare a bounded worker process that can be terminated and reaped with a transport having a documented cancellation/deadline contract. The selected mechanism must stop and join/reap the actor before releasing its protection or removing its staging state. Specify terminate-and-reap for timed-out version probes as well. Correct the unconditional claim that 360 seconds exceeds a healthy holder's worst case: an under-lock reuse probe, download, staging probe, extraction, hashing and cleanup/publication also contribute. Bound the relevant work or describe 360 seconds as a finite contention policy, with success conditional on the holder completing in that budget.

The production contract requires a documented acceptance check for the actual deadline/cancellation adapter; fake clocks alone establish orchestration, not real cancellation. This can remain a developer-run check outside process-free pytest. See [Python urllib.request](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen).

#### D3: In-use protection relies on an unestablished directory-rename assumption for design-specification git-cliff-provisioning (round 1)

Publication and Q07 A assume moving a directory containing a running executable is refused and therefore protects the binary. The design supplies no documented primitive or acceptance evidence for that exact operation. Refusal to delete an executable after the parent directory has already moved would be too late for the stated protection. There is also an interval between lock-free validation/path return and child creation during which a repair caller could retire the entry.

Define a reader/use protocol covering validation through child start and the required execution lifetime, and a writer replacement protocol that respects it. Alternatively choose immutable generation directories with a stable selection protocol and no cleanup of in-use generations. Explain how the chosen protocol preserves valid read-only reuse. Revise Q07's options and recommendation rather than presenting automatic rename refusal as proven. If retaining an OS refusal primitive, cite its documented guarantee and require a bounded acceptance case for both an already running child and the validation-to-start race.

[MoveFileEx documentation](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexa) describes directory moves but does not establish the descendant-running-image guarantee asserted here. An isolated local rename diagnostic was rejected by automatic approval review before execution with `blocked by policy`; it created no evidence. This finding is an unsupported design guarantee, not a claimed observation that a Windows rename succeeded.

#### D4: Three observed statuses do not prove the reserved status is unused for design-specification git-cliff-provisioning (round 1)

The body samples success, usage error and failing render; Q11 additionally mentions panic and claims the admission check proves no admitted version returns 69. Those examples alone cannot establish the confirmed requirement that admitted versions never return the provisioning status.

Keep 69 as a proposed number, conditional on a per-version exit-path audit (including propagated/helper statuses and panic/termination handling where relevant), with targeted observed cases that corroborate it. Record the audit basis and artifact identity in admission evidence; if the version's behavior cannot support the guarantee, bring that conflict back explicitly rather than silently weakening the requirement. Align the body and Q11's status matrices. This is not a demand to execute every possible erroneous input.

#### D5: Candidate admission ordering and cached evidence reuse need a concrete contract for design-specification git-cliff-provisioning (round 1)

The design correctly separates evidence candidates from production pins, but calls the pre-admission 2.14.2 candidate digest 'equal to the manifest'. Make the order explicit: acquire candidate identity/digest independently, verify and compare, classify the bundle, then admit that same identity/digest with its bundle reference. No provisional production admission is necessary.

Q12 promises offline reuse, while the harness only explicitly shares fetch/extract/probe primitives. Define candidate cache reuse validation before execution, candidate-scoped locks/staging/publication, and where the durable first 2.7.0 trust record lives. Repeating a comparison must compare against the previously recorded digest, not overwrite the trust record from whatever cached executable is found. A recorded executable hash in a new report is not itself a reuse integrity check. Reusing parameterized cache primitives or re-extracting from a retained archive checked against the immutable candidate record are both viable. Keep this route incapable of admitting a production pin. The human already authorized the 2.7.0 evidence-only trust exception; do not request another authorization.

#### D6: Frozen inputs must remain recoverable and identical between candidates for design-specification git-cliff-provisioning (round 1)

The bundle records a dev_workflow config path and hash, but these do not recover the bytes after the legacy source is removed or changes. Preserve the exact config bytes or an immutable repository/commit/path reference that supplies them. State the controlled comparison cwd, flags and environment policy; use the same explicit environment for both versions, including removal of ambient `GIT_CLIFF_*` overrides. User-launcher passthrough remains a separate policy under Q09.

Retain Q14's script approach, specifying all object-producing inputs (tree, parents, messages, identities/dates and annotated tag/tagger data), object format and relevant ambient Git configuration. Require regeneration to match the recorded object hashes. These details make Q13 B's regeneration tradeoff defensible without requiring full identical raw outputs in Git.

### Question verdicts for design-specification git-cliff-provisioning round 1

All Q01–Q16 remain pending human choices. None is redundant or outside item 3 merely because a later item consumes its interface. The questions generally belong to design; file-by-file implementation and rollout sequencing remain for the plan.

| Question | Independent verdict and reviewer choice |
| --- | --- |
| Q01 digest source | Agree with A: commit the upstream asset digest at admission, avoiding release-time metadata lookup. Clarify candidate-first ordering under D5. Runtime verification still checks the downloaded bytes against that digest. |
| Q02 manifest form | Agree with A: frozen Python records fit the small shipped tested set and require no new runtime parser. Preserve a bundle reference per admitted identity and whole-set validation. |
| Q03 lock mechanism | Revise. Choose the existing A pending a requirement-compliant revised B. B's simpler waiting can be useful, but acquiring/abandoning a mutex cannot replace process-owner checks for recovery/cleanup. Correct thread-versus-process semantics, A's cross-machine claim, and the supported namespace/topology consequences (D1). |
| Q04 granularity | Agree with A: version/platform serialization matches entry publication and permits unrelated pins to proceed. Candidate and production namespaces must remain distinct. |
| Q05 budget adjustability | Agree with A: constants are sufficient and avoid a new user setting. This question does not settle deadline enforcement; add the missing enforcement decision described in D2. |
| Q06 retries | Agree with A, conditional on the D2 deadline: one transient retry and backoff share a single total budget, including 429/5xx handling. Do not retry integrity failures; do not let Retry-After extend the deadline. |
| Q07 invalid replacement | Revise; A is not justified by the current evidence. Prefer an explicit reader/use guard plus protected replacement if it can preserve read-only reuse; otherwise C with an immutable-generation lifetime contract. Present this as a revised option with tradeoffs and acceptance evidence, not automatic agreement with an unsupported OS assumption (D3). B's manual repair is not the preferred self-healing design. |
| Q08 proxies | Agree with A within the documented environment/static Windows proxy scope. State PAC-only and authenticated-proxy limitations clearly; workstation success is supporting evidence, not universal proxy coverage. |
| Q09 provisioning API | Agree with B: centralize scrubbed engine/probe and passthrough launcher policies. Include evidence comparison in the scrubbed controlled policy and incorporate any D3 lifetime guard. Item 4 keeps rendering arguments/postprocessing/timeouts; the object must not take its renderer responsibilities. |
| Q10 child execution | Agree with A: inherited streams, existing batch argument guard and unchanged child status fit the launcher contract. Retain the status path and explicit process lifecycle; do not route child statuses through release-status normalization. |
| Q11 reserved status | Conditionally A (69), but revise the admission proof before recommending it as guaranteed unused. Sampled status cases alone do not establish the requirement (D4). No human decision on the number is recorded. |
| Q12 candidate location | Agree with A: the evidence subtree and manifest-only production lookup establish the right separation. Add the concrete offline reuse/trust/locking contract in D5; location alone does not supply it. |
| Q13 evidence contents | Agree with B: frozen recoverable inputs, output digests, complete differing hunks with context, statuses and classifications retain reviewable differences. State that regenerating identical output needs the controlled harness; do not silently require full raw-output storage instead. D6 repairs reproducibility inputs. |
| Q14 fixtures | Agree with A, strengthened as D6: fix every object-producing input and verify the recorded hashes on regeneration. C would leave confirmed matrix coverage missing; a binary bundle is not necessary if the script is deterministic. |
| Q15 harness surface | Agree with C: internal reusable comparison logic plus a developer entry point serves admission now and item 6 later without prematurely creating a public command contract. |
| Q16 alias fragment | Agree with A: a tested single-line fragment beside the launcher respects the item 3/item 8 exposure boundary and keeps direct launcher warm-up usable. |

Missing decision: **How are network-stage deadlines enforced and cancelled in production?** Suggested options are (A) a bounded subprocess worker with terminate/reap semantics, (B) a transport with a documented end-to-end cancellable deadline, or (C) socket timeouts and clock checks between blocking operations. Recommend A if retaining synchronous urllib; B is viable with a supported concrete transport; reject C as insufficient for the confirmed finite-budget contract. Explain process-free unit seams and a separate bounded developer acceptance check. The writer should finalize options from actual adapter constraints, without treating this reviewer proposal as a human answer.

Q07 already provides a place for the missing reader lifetime/replacement decision; revise that question rather than adding a duplicate. Candidate lifecycle and recoverable frozen inputs can be specified as consequences of the existing Q12–Q14 choices unless their implementation reveals a material tradeoff needing a separate human choice.

### Requested changes for design-specification git-cliff-provisioning round 1

Requested changes:

1. Correct Q03's mutex/thread semantics; retain process-identity/DEAD checks for recovery and partial cleanup; define supported cache topology and naming scope, and remove the unproven cross-machine claim.
2. Add a production deadline/cancellation decision covering blocking network work, candidate metadata, all attempts/backoff and probe termination/reaping; correct the holder/wait worst-case assurance.
3. Replace Q07's assumed directory-rename protection with a specified use/replacement protocol or immutable-generation alternative, covering validation through invocation and preserving read-only reuse.
4. Make status 69 conditional on version-specific exit-path evidence with corroborating observations; remove the claim that three sampled statuses prove universal exclusion and align panic coverage.
5. Specify independent candidate acquisition before admission plus integrity-before-execution, immutable trust record, and locking/atomic publication for cached evidence reuse.
6. Preserve recoverable exact config inputs, control cwd/flags/environment identically between candidates, and define deterministic fixture object inputs with hash verification.

These are substantive design corrections, so another review round is required. Reviewer choices are advisory; all current design questions still await the human.

### Writer instructions for design-specification git-cliff-provisioning round 1

Revise the design and question formulations for D1–D6, then publish another automated specification review round. Do not consolidate pending answers or mark reviewer preferences as explicit human decisions.

Preserve the confirmed requirement decisions, including candidate-before-admission, checkout-local cache, owner-aware cleanup, no in-use replacement, distinct status, finite stage budgets and the already authorized 2.7.0 evidence-only exception. Keep the renderer/postprocessing boundary with item 4, consumer setup with item 6 and shared exposure/full parity with item 8.

Revise Q03 and Q07 with accurate alternatives and consequences. Add the deadline-enforcement question independently of Q05. Correct Q11's evidence claim and align its matrix. Add candidate lifecycle/admission ordering and recoverable comparison inputs as explicit contracts. Update affected acceptance cases and adapter seams, including process cancellation/reaping, owner still alive after a mutex thread ends, ALIVE/UNKNOWN orphan preservation, in-use and validation-to-start replacement races, cached evidence integrity and identical controlled comparison inputs.

The body may continue recording its original choices while recommendations await human decisions, provided the question text clearly states the proposed change. Do not interpret that temporary difference alone as a defect. No implementation, commits or consolidation are requested from this reviewer round.

### Final reviewer decision for design-specification git-cliff-provisioning round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-14T01:49:16+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 2

### Requestor assessment for design-specification git-cliff-provisioning (round 2)

Writer assessment of the git-cliff-provisioning design, round 2.

All six round 1 findings are accepted and applied to both the body and the
questions. The body now states:

- D1: the transition mutex only serializes record changes; mutex ownership is
  per thread, so neither a normal nor an abandoned acquisition authorizes
  recovery or cleanup, which still require a `DEAD` owner identity. The
  supported topology is a cache on a local disk of one machine, with the mutex
  in the `Global\` namespace; a network-share cache used from several machines
  is explicitly unsupported.
- D2: a new "Deadline enforcement" subsection runs each download attempt, and
  the harness's metadata lookup, in a worker process that the parent
  terminates and reaps at the deadline before removing staging or releasing
  the lock; the probe is terminated and reaped the same way; the retry and
  `Retry-After` share the deadline. The 360 s wait is described as a finite
  contention policy, with success conditional on the holder finishing within
  it.
- D3: a use guard, a `CreateFileW` read handle with `FILE_SHARE_READ` only,
  is held from validation until the git-cliff process exits; replacement first
  renames the executable, which needs delete access and fails while a guard is
  open. Read-only reuse keeps working because the guard is a read handle.
- D4: status 69 holds only with a per-version exit-path audit at the source
  tag, corroborated by observed statuses; a version that can return 69 stops
  admission and goes back to the user.
- D5: a four-step candidate lifecycle (independent identity, verification,
  classification, reviewed manifest edit), immutable candidate trust records
  committed with the bundle, and a candidate cache with its own namespace,
  locks, staging, publication, entry record, use guard and reuse check.
- D6: the exact `cliff.toml` bytes are copied into the bundle, both versions
  share one worktree, flags and explicit environment without `GIT_*`
  variables, and the fixture script fixes every object-producing input with
  regeneration checked against recorded hashes.

The confirmed-facts table gains three documented facts (mutex ownership,
`CreateFileW` sharing, `urlopen` timeout scope), and the acceptance cases add
worker and probe termination, a live owner behind an abandoned mutex,
`ALIVE`/`UNKNOWN` orphan preservation, the in-use and validation-to-start
races, cached candidate integrity, fixture regeneration and identical
comparison inputs.

Questions: Q03 is rewritten with accurate mutex semantics and now recommends
option A, the record-plus-probe lock the body states. Q07 is rewritten around
the use guard (A), manual repair (B) and immutable generations (C). Q11 makes
69 conditional on the audit. Q01, Q04 to Q06, Q08 to Q10 and Q12 to Q14 gain
the qualifications from the verdict table. New Q17 asks how stage deadlines
are enforced, recommending the worker process. All seventeen decisions remain
pending.

Please assess whether the revised mechanisms meet the requirement, whether
the use-guard sharing argument and the worker termination contract are sound,
and whether any question is missing or misstated.

### Change summary for design-specification git-cliff-provisioning (round 2)

Changes since round 1 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Scope: the delivered list names the download worker, the use guard, the
  candidate lifecycle, the immutable 2.7.0 trust record and the exit-status
  audit.
- Confirmed facts: three rows for mutex thread ownership, `CreateFileW`
  sharing and the `urlopen` timeout scope; the process-audit row names a fake
  download worker.
- Target flow: use guard first, guarded reuse check, worker download, retirement
  by renaming the executable first, guard kept until git-cliff exits.
- Cache: "Reuse check and the use guard" replaces the lock-free reuse section;
  publication retires an invalid entry by renaming its executable first and
  names the developer-run acceptance check.
- Lock: transition-mutex semantics, supported topology, and `DEAD`-only
  recovery even after an abandoned mutex; staging owners read from directory
  names.
- Budgets: the wait is a finite contention policy; new "Deadline enforcement"
  subsection.
- Statuses: 69 conditional on the exit-path audit.
- Entry point and launcher: the use guard is returned and held until the child
  exits; the worker and use-guard seams.
- Evidence: "Candidate lifecycle and admission order" and "Candidate cache"
  replace the candidate table section; frozen inputs copy the `cliff.toml`
  bytes and fix cwd, flags and environment; the fixture fixes every
  object-producing input; outputs record the audit.
- Testing, foundation changes and acceptance cases updated as listed in the
  assessment.
- Questions: Q03, Q07 and Q11 rewritten; Q01, Q04, Q05, Q06, Q08, Q09, Q10,
  Q12, Q13 and Q14 qualified; Q17 added. IDs Q01 to Q16 are unchanged.

The companion
`.reviews/a.design.v0.14.0.git-cliff-provisioning.open.questions.md` is
byte-identical to the section. markdownlint reports 0 issues and cSpell finds
no unknown word.

### Writer response for design-specification git-cliff-provisioning (round 2)

Writer response:

Response to the round 1 answer (changes-requested). All six findings and the
verdict-table qualifications are accepted; there is no disagreement.

- D1: Q03 now recommends option A, the body's record-plus-probe lock; option B
  keeps the whole-duration mutex only as a waiting improvement that still
  needs owner records and `DEAD` checks. The unsupported cross-machine claim is
  removed and the local-disk topology stated.
- D2: added as Q17 rather than folded into Q05, as the answer suggested. The
  writer chose the worker-process option as the body's proposal because the
  standard library offers no end-to-end cancellable transport and the release
  dependency group is empty.
- D3: the body no longer assumes a refused directory move. The use guard rests
  on the `CreateFileW` sharing rule: renaming needs delete access, which a
  handle opened with `FILE_SHARE_READ` only denies to every other opener. The
  guard is opened before validation, which closes the validation-to-start
  window. The writer did not run a rename experiment; the design requires a
  developer-run acceptance check instead.
- D4: the body and Q11 now make 69 conditional on the audit and align the
  observed cases, including reachable panics.
- D5 and D6: specified as contracts of the existing Q12 to Q14 choices; no new
  question was needed. The 2.7.0 trust record is committed with the bundle,
  written once and never overwritten, and no new authorization is requested.

Q09 and Q13 still recommend changes the body does not yet state (an invocation
object; digests plus hunks instead of raw outputs); the question texts say so.

### Reviewer focus for design-specification git-cliff-provisioning (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-14T01:54:42+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 2

Disposition: changes-requested.

The revision addresses the six round-1 findings in the normal and deadline-expiry paths. Record transitions no longer substitute mutex abandonment for process death; the supported topology is explicit; child workers enforce aggregate deadlines; file-sharing guards replace the unsupported directory-rename assumption; admission includes an exit-path audit; candidate trust, locking and controlled evidence inputs are specified. Q09 and Q13 deliberately propose changes to the body pending human selection; that declared difference is not a defect.

R2-D1 (substantive): specify child lifetime and guard ownership when the parent dies.

The deadline subsection (lines 394-411) guarantees terminate/reap before cleanup only while the parent remains alive. Staging names identify an owning PID and creation time (line 201), and recovery authorizes cleanup after that owner is DEAD. Windows explicitly states that terminating a process does not terminate its child processes. A parent can therefore die while its download worker survives, retains a staging file and loses its deadline enforcer. A recovering caller can observe the parent DEAD without having established that the actual writer is dead. This is the same owner-aware cleanup requirement already settled in the requirement, now applied to the newly introduced worker. The candidate metadata/download and probe paths need the same lifecycle analysis.

Likewise, the reuse and launcher contracts (lines 240-258, 467-473 and Q07/Q09/Q10) keep the use guard in the caller until its child exits. If that caller dies, Windows closes its handles while its git-cliff child can survive. The documented sharing argument then no longer proves the promised protection for the whole child lifetime. Do not substitute another unverified assumption about automatic executable-image protection.

Document a concrete lifecycle that covers parent failure and the launch/ownership-publication window. Viable approaches include Windows job containment established before a child can work, with kill-on-close and recovery that establishes actual child termination before destructive cleanup, or explicit child identities and safe ownership handoff with a bounded orphan lifecycle. Kill-on-close initiates child termination; merely seeing the parent DEAD must not be treated as proof that child termination has finished. For a git-cliff child that may survive its launcher, explicitly inheriting or duplicating the use guard into that child can preserve the sharing lifetime; otherwise define containment and termination semantics that preserve the invariant. Explain handle inheritance and job-handle ownership rather than relying on implicit defaults. Select an approach compatible with unchanged normal stdout/status passthrough and read-only reuse.

Supporting Windows contracts: [Terminating a Process](https://learn.microsoft.com/en-us/windows/win32/procthread/terminating-a-process), [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), and [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew). These are documentation-based findings; no new process/rename experiment was executed for this round.

R2-D2 (small contract clarification): give the candidate metadata stage an explicit total budget and retry policy. The deadline subsection says it uses the same worker, but the budget table enumerates download, probe and contention only. State whether metadata shares the 300-second budget or gets its own named finite budget, and whether its retry shares that deadline. This need not add a setting or another question.

No distinct Q18 is necessary if the parent-death consequences and the materially different lifecycle alternatives are incorporated into Q17 and the guard-dependent Q07/Q09/Q10. The design is not ready for implementation from the current options without that revision. All Q01-Q17 remain human-pending; reviewer preferences below do not confirm them.

### Question verdicts for design-specification git-cliff-provisioning round 2

All seventeen questions are relevant to item 3 and remain pending human choices. Their options are generally distinct and their recommendations follow the confirmed requirement, subject to the parent-death repair below. No earlier requirement decision is reopened.

| Question | Independent verdict and reviewer choice |
| --- | --- |
| Q01 digest source | Agree with A. Candidate-first acquisition and a reviewed manifest edit now remove the circular admission order; committed expected digests avoid a live production API dependency. |
| Q02 manifest form | Agree with A. Frozen Python records fit the small tested set, retain per-pin evidence and need no runtime parser. |
| Q03 lock mechanism | Agree with revised A. Record plus PID/creation identity and DEAD-only recovery preserve ALIVE/UNKNOWN owners; transition mutex acquisition is correctly separate. Extend recovery to account for surviving worker identities under R2-D1. B remains a real waiting tradeoff, not an alternative proof of owner death. |
| Q04 granularity | Agree with A. Version/platform granularity and separate candidate namespace avoid unrelated contention. Child-lifecycle records must remain scoped to the same attempt. |
| Q05 budget adjustability | Agree with A. Fixed reviewed constants meet the no-new-setting decision. Clarify the metadata stage value or shared budget under R2-D2; Q17 owns enforcement. |
| Q06 retries | Agree with A. One transient retry shares the aggregate deadline; integrity failures are not retried and Retry-After cannot extend it. |
| Q07 invalid replacement | Conditionally A. The documented read-sharing guard and executable-first rename support the normal path and read-only reuse. Revise the option to preserve the guard through an orphaned child's actual lifetime, or specify contained termination with safe recovery; a parent-only handle is insufficient after parent death (R2-D1). B's manual intervention and C's generations remain distinct costs. |
| Q08 proxies | Agree with A within the explicit environment/static-Windows scope. The PAC-only/authentication limits and workstation-evidence limit are now clear. |
| Q09 provisioning API | Prefer B. Centralized scrubbed-engine and passthrough-launcher policies prevent caller omissions, while item 4 retains rendering arguments, postprocessing and timeouts. Require lifecycle ownership beyond an invocation object's destruction or process death; returning a guard in that object alone does not protect a surviving child (R2-D1). |
| Q10 child execution | Prefer A with the revised lifecycle. Inherited streams, existing argument guard and unchanged normal child status fit the launcher contract. Add the parent-death behavior and guard transfer or containment cost to this option rather than presenting the parent wait as sufficient (R2-D1). |
| Q11 reserved status | Agree with conditional A. The per-version source-tag exit-path audit plus observations is materially stronger than sampled statuses alone. A version that can return 69 stops admission and returns the collision to the human. |
| Q12 candidate location | Agree with A. Candidate-scoped records, immutable trust inputs and production-only manifest resolution provide safe separation. Apply the revised worker/recovery/guard lifetime to this namespace too. |
| Q13 evidence contents | Agree with B. Recoverable exact config bytes, frozen inputs, digests and complete differing hunks retain reviewable evidence without requiring every identical output. The declared proposed change from the body is clear. |
| Q14 fixtures | Agree with A. Fixing object-producing inputs and checking regenerated hashes makes the missing-history fixtures reproducible; omitting those fixtures would leave confirmed coverage missing. |
| Q15 harness surface | Agree with C. Internal reusable comparison logic and a developer entry point support admission now and item 6 later without premature public command commitments. |
| Q16 alias fragment | Agree with A. A tested fragment beside the launcher supplies item 3's definition while item 8 owns exposure. |
| Q17 deadline enforcement | Prefer revised A. A stoppable worker solves blocking urllib calls while the parent lives. Add a concrete parent-crash lifecycle, safe launch/ownership handoff and actual-child-death recovery checks. Compare containment versus identity/handoff consequences explicitly; socket timeouts alone remain insufficient. |

Suggested replacement contract for Q17 A: "Each network attempt runs in a bounded worker with a specified parent-crash lifecycle established before it can write. Deadline expiry terminates and waits for that worker. Recovery removes an attempt only after every process able to write it is established DEAD; parent death alone is insufficient. The same lifecycle covers metadata and probe processes." The writer must supply the selected concrete mechanism and its tradeoffs, not leave this invariant as the entire design.

Suggested addition to Q07 A and Q09/Q10: "Protection covers the actual git-cliff child lifetime, including launcher death. The design specifies guard inheritance/duplication or contained termination, launch-failure cleanup, and recovery ordering." No separate question is needed if these alternatives and consequences are exposed in the existing options. These are reviewer proposals, not recorded human answers.

### Requested changes for design-specification git-cliff-provisioning round 2

Requested changes:

- R2-D1: replace the parent-only child/guard lifetime assumption with a concrete parent-crash protocol covering launch, ownership publication, termination completion, staging recovery and use-guard lifetime. Update the affected existing questions and acceptance cases. This is substantive and requires another review round.
- R2-D2: name the candidate metadata stage's finite aggregate budget and retry policy or explicitly allocate it to an existing shared deadline. This is a small clarification supporting the already-confirmed finite-network-budget rule.

Reviewer choices remain Q01 A, Q02 A, Q03 A, Q04 A, Q05 A, Q06 A, Q07 A conditional on R2-D1, Q08 A, Q09 B conditional on R2-D1, Q10 A conditional on R2-D1, Q11 conditional A, Q12 A, Q13 B, Q14 A, Q15 C, Q16 A and Q17 revised A. All seventeen await human decisions. No consolidation is authorized by this answer.

### Writer instructions for design-specification git-cliff-provisioning round 2

Revise the design and its matching question companion, then request another automated review round. Do not consolidate or mark Q01-Q17 decided.

1. Preserve the six accepted round-1 repairs. Add Windows parent/child termination facts and a concrete lifetime protocol for workers, probes and git-cliff invocations. Specify who owns each relevant process and handle, when that ownership becomes visible, and what happens if the parent dies at each launch/handoff boundary. Account for assignment/inheritance failures before a child can perform work.
2. Make recovery establish that every actor able to write staging has actually stopped before deleting staging or relinquishing its protection. A DEAD parent or abandoned mutex is insufficient. If using job kill-on-close, document job-handle inheritance/ownership and how recovery avoids racing pending child termination. If using child identity records, specify publication and handoff before writes plus a finite orphan lifecycle.
3. Keep the use guard effective through the actual git-cliff child lifetime. Select explicit child guard inheritance/duplication or a concrete containment/lifetime protocol; specify launch failures and parent crash as well as normal exit. Preserve normal passthrough and read-only cache reuse, and apply the same rule to evidence candidates and probes as applicable.
4. Update Q17 and the affected Q03/Q07/Q09/Q10/Q12 consequences, plus flow, public internal API contract, recovery and acceptance cases. Keep the materially different lifecycle alternatives and their costs visible to the human without duplicating them as Q18 unless a genuinely independent decision remains.
5. Add process-free acceptance scenarios for parent death during worker launch, active write, probe, the validation-to-start gap and a running child; recovery while child termination is pending; ALIVE/UNKNOWN child preservation; and assignment/handle-transfer failure. Keep real lifecycle checks in the bounded developer acceptance path outside the process-free pytest suite. Specify needed evidence without claiming those checks have already run.
6. State the metadata lookup's finite total budget and retry allocation explicitly, using an existing constant/shared deadline if that is the proposal. No new user setting is required.

The authorized evidence-only 2.7.0 exception and item boundaries remain settled. Do not request renewed authorization or move renderer/postprocessing work into item 3.

### Final reviewer decision for design-specification git-cliff-provisioning round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-14T02:03:09+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 3

### Requestor assessment for design-specification git-cliff-provisioning (round 3)

Writer assessment of the git-cliff-provisioning design, round 3.

Both round 2 findings are accepted and applied; the six round 1 repairs are
kept.

R2-D1, parent death: the body adds a "Child process lifecycle" subsection that
every child follows, the download worker, the metadata worker, the version
probe and the git-cliff run itself:

1. the parent creates one job object per attempt or run with
   `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, through a non-inheritable handle it
   alone holds;
2. it creates the child suspended with `CreateProcessW` and an explicit
   inherited-handle list (standard handles, plus the use guard for a git-cliff
   run);
3. it assigns the suspended child to the job; a failure terminates and reaps
   the suspended child and fails the stage;
4. for a provisioning child, it records the child's PID and creation time in
   the lock record and in the staging owner file before the child can run; a
   failure terminates and reaps it;
5. it resumes the child, waits within the deadline, and terminates and reaps
   it on expiry.

A child that was never recorded never ran. If the parent dies, its job handle
closes and Windows terminates the assigned children; a terminating child stays
`ALIVE` until it ends, and recovery requires the owner and every recorded child
to be `DEAD`. The git-cliff child inherits the use guard, so the protection
lasts for its actual lifetime even if its caller dies, and the kill-on-close
job bounds that orphan; a caller that dies before the child exists leaves
nothing to protect. The launcher ignores Ctrl+C while waiting and returns the
child's status unchanged.

Three documented facts support this: terminating a process does not terminate
its children; a kill-on-close job terminates its processes when its last
handle closes; and CPython's `subprocess` closes the primary thread handle and
supports only `handle_list`, so suspended creation and job assignment need the
engine's Windows layer.

R2-D2: the budget table adds a 60 s total budget for the harness-only metadata
lookup, with one retry under the download rules inside it.

Questions: Q17 is rewritten with four lifecycle alternatives (contained
lifecycle, self-limiting workers, third-party cancellable transport, socket
timeouts only) and still recommends A. Q03, Q07, Q09, Q10 and Q12 carry the
lifecycle consequences. Acceptance cases add parent death before recording,
during a write and during a probe, children `ALIVE` or `UNKNOWN` after a `DEAD`
parent, assignment and recording failures, launcher death while a child runs
and between validation and child start. Testing names the fake Windows layer
scenarios and the developer-run checks, stating that none has run yet. All
seventeen decisions remain pending.

Please assess whether the lifecycle closes every launch and handoff boundary,
whether the guard inheritance and job ownership are specified explicitly
enough, and whether the questions now expose the alternatives the human needs.

### Change summary for design-specification git-cliff-provisioning (round 3)

Changes since round 2 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Confirmed facts: rows for process termination not reaching children, job
  objects with kill-on-close, and CPython `subprocess` thread-handle and
  attribute-list limits.
- Target flow: recovery needs the owner and every recorded child `DEAD`; the
  worker runs as a contained, recorded child; git-cliff starts as a contained
  child that inherits the guard.
- Reuse check and the use guard: the guard passes to the git-cliff child
  through the inherited-handle list; caller death before the child exists.
- Recovery: lock and staging removal require every recorded child `DEAD`; new
  "Child process lifecycle" subsection with the five-step protocol and the
  parent-death consequences.
- Budgets: the harness metadata lookup gets a 60 s total with one retry inside
  it; deadline enforcement refers to the lifecycle and to kill-on-close after
  parent death.
- Entry point and launcher: guard inheritance, closing the caller's copy,
  Ctrl+C handling and launcher death.
- Testing, foundation changes and acceptance cases: fake Windows layer
  scenarios, developer-run lifecycle checks, `CreateProcessW` creation path,
  and seven new acceptance cases.
- Questions: Q17 rewritten (four options); Q03, Q07, Q09, Q10 and Q12 extended
  with the lifecycle consequences.

The companion is byte-identical to the section. markdownlint reports 0 issues
and cSpell finds no unknown word.

### Writer response for design-specification git-cliff-provisioning (round 3)

Writer response:

Response to the round 2 answer (changes-requested). Both findings are accepted;
there is no disagreement.

- R2-D1: the writer chose job containment with recorded identities over the
  identity-and-handoff alternative because a git-cliff probe or run cannot
  carry its own watchdog, so only a job bounds every child; Q17 option B keeps
  that alternative and its unbounded-probe cost visible. Recording happens
  while the child is suspended, which removes the launch window between start
  and ownership publication. Guard inheritance is explicit, through the
  inherited-handle list, and the design does not rely on any automatic
  protection of a running executable image.
- R2-D2: the metadata lookup has its own named 60 s budget rather than sharing
  the 300 s download budget, since it runs only in the harness and transfers
  little data.

No new question was added; the lifecycle alternatives live in Q17 and their
consequences in Q03, Q07, Q09, Q10 and Q12, as the answer suggested. No
experiment was run; the developer-run checks are specified, not claimed.

### Reviewer focus for design-specification git-cliff-provisioning (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-14T02:07:39+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 3

Disposition: changes-requested.

The revised design correctly adds child identities before resume, waits for recorded children to be DEAD, gives the git-cliff child its own guard handle and names the metadata stage's 60-second aggregate budget. R2-D2 is resolved. These changes address parent failure after job assignment, but the requested launch-boundary analysis exposes one remaining substantive gap and one inconsistent lifecycle classification.

R3-D1: containment must exist at child creation, not in a later parent action.

The lifecycle creates a suspended child at lines 396-398 and assigns it to the job at lines 399-400. If the parent dies between those operations, the child belongs to no newly created kill-on-close job. Closing that job cannot terminate an unassigned process. CREATE_SUSPENDED stops execution; it does not bind the child's lifetime to its parent. The child can remain suspended indefinitely. For a git-cliff invocation, it already inherited the guard and standard handles at creation, so it can indefinitely block entry repair and keep redirected pipe handles open. The worker may not yet write staging, but that does not make the leaked process bounded or accounted for. The acceptance case at line 730 incorrectly promises job termination for the whole interval before recording, and Q17 A incorrectly says every launch boundary leaves nothing unaccounted for.

Use a concrete creation-time containment mechanism. The documented PROC_THREAD_ATTRIBUTE_JOB_LIST attribute assigns job handles during CreateProcess; it can be combined with suspended creation and the explicit inherited-handle list in the Windows layer. It is supported from Windows 10 / Windows Server 2016. Specify that supported baseline or an equally safe supported alternative, fail closed if containment cannot be established, and retain suspended identity publication before resume for cache-writing children. Do not silently fall back to a separate create-then-assign sequence. Job nesting or creation failures must produce a stage failure without an uncontained child. This is a targeted correction to the selected lifecycle proposal, not a request to redesign provisioning or add a watchdog service.

Supporting contracts: [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute) documents both HANDLE_LIST and JOB_LIST; [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject) associates an existing process only when called; [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) defines kill-on-close for associated processes. No runtime process experiment was performed for this review.

R3-D2: distinguish cache-writing attempts from lock-free executable checks and inherit the guard for probes too.

The lifecycle applies to every version probe, then requires every "provisioning child" to write its identity into the lock record and staging owner file (lines 401-404). A valid-entry reuse check runs the probe without a lock or staging directory and promises no write, including in a read-only checkout (line 270). State explicitly that a lock-free reuse probe uses contained creation and guard inheritance but writes no recovery records: it cannot write cache state. Download workers and staging probes belong to an existing writable attempt and publish identities there before resume. Harness metadata must likewise have a defined attempt context if it writes candidate state. Replace the parent-versus-provisioning label with this explicit distinction.

The inherited-handle list currently includes the use guard only "for a git-cliff run" while probes are named separately. Every execution of a guarded cached git-cliff binary, including --version during reuse, must retain the guard through its actual lifetime. Otherwise parent death closes the sole guard before the contained probe has actually terminated. Specify guard inheritance for the reuse probe and other executable checks where that protection is required, without introducing cache writes on reuse. Add acceptance cases that distinguish these paths.

No new independent Q18 is needed: correct Q17 A and propagate its costs and classification through Q03/Q07/Q09/Q10/Q12. All seventeen human choices remain pending. The earlier six repairs and the metadata clarification remain accepted; Q09 and Q13's declared proposed differences from the body remain intentional pending human selection.

### Question verdicts for design-specification git-cliff-provisioning round 3

All Q01-Q17 remain relevant and human-pending. The options generally distinguish real design costs; the lifecycle wording below must be repaired before recommending convergence. Reviewer choices are advisory.

| Question | Independent verdict and reviewer choice |
| --- | --- |
| Q01 digest source | Agree with A: independent candidate acquisition then reviewed admission permits a fixed expected digest with no live production API dependency. |
| Q02 manifest form | Agree with A: frozen engine records fit reviewed pin admission and avoid a runtime parsing surface. |
| Q03 lock mechanism | Agree with A: record transitions and DEAD-only identity checks preserve ALIVE/UNKNOWN owners. Qualify child recording as applying to cache-writing attempts, not a valid-entry reuse probe that holds no lock (R3-D2). |
| Q04 granularity | Agree with A: entry-scoped locks and separate candidate names serialize only conflicting publication. |
| Q05 budget adjustability | Agree with A: fixed reviewed constants meet the no-new-setting decision; the metadata stage now has an explicit finite budget. |
| Q06 retry policy | Agree with A: one transient retry shares the aggregate deadline; integrity failures and Retry-After cannot extend it. |
| Q07 invalid replacement | Prefer A with the lifecycle repair. Inherited guards now address parent death after assignment, but containment must exist at creation to avoid an indefinitely suspended guard holder (R3-D1). Include reuse probes in guard inheritance (R3-D2). Manual repair and immutable generations remain distinct alternatives. |
| Q08 proxy resolution | Agree with A: standard environment/static-Windows proxy scope is explicit, with PAC-only and authenticated proxies deferred and the workstation evidence correctly limited. |
| Q09 returned interface | Prefer B with R3-D1/D2 applied centrally. The invocation object can own environment policy, contained creation and guard transfer; item 4 still owns rendering arguments, postprocessing and timeouts. Its body difference is explicitly proposed, not an inconsistency to consolidate now. |
| Q10 child execution | Prefer A with creation-time containment. The stream/status path and argument guard fit the requirement; sequential create-then-assign does not meet the claimed parent-death lifecycle. |
| Q11 reserved status | Agree with conditional A: per-version source-tag exit-path audit plus observations must exclude 69 before admission; a collision goes back to the human. |
| Q12 candidate location | Agree with A: isolated resolver namespace, immutable trust records and entry checks prevent production admission. Apply the corrected creation and writer-versus-reader classification to this namespace. |
| Q13 evidence bundle | Agree with B: recoverable exact inputs, output digests, complete differing hunks and classifications keep differences reviewable and reruns verifiable. The declared body alternative awaits selection. |
| Q14 history fixtures | Agree with A: fixed object-producing inputs and recorded hash checks make the missing snapshot cases reproducible. C would defer confirmed item-3 coverage. |
| Q15 harness surface | Agree with C: internal reusable logic plus a developer entry point serves admission now and item 6 later without an early public interface. |
| Q16 alias definition | Agree with A: a tested fragment ships the definition in item 3 while item 8 owns exposure. |
| Q17 deadline and child lifecycle | Prefer corrected A. Establish kill-on-close membership during child creation, keep cache writers suspended until identity publication, and define record-free guarded reuse probes. The current "every orphan" and "any launch boundary" claims are false for the pre-assignment interval. B/C/D still show relevant costs but do not supply the same complete child-lifetime contract. |

Suggested replacement for the start of Q17 A: "Create each child suspended with an explicit inherited-handle list and creation-time membership in the parent-only kill-on-close job. A creation or containment failure yields no uncontained child. Publish cache-writing attempt identities before resume; lock-free reuse probes publish no cache records and inherit their executable's guard. Terminate and wait at the deadline; recover writable attempts only after all recorded actors are DEAD."

The writer should state the concrete Windows API support baseline and failure behavior for this proposal. Correct the existing question and affected consequences rather than adding a duplicate question. None of these preferences records a human answer.

### Requested changes for design-specification git-cliff-provisioning round 3

Requested changes:

- R3-D1 (substantive): close the interval between suspended process creation and job assignment with creation-time containment. A suspended unassigned orphan can live indefinitely while holding inherited guard/pipe handles. Correct the acceptance case and Q17's universal lifetime claims.
- R3-D2: distinguish writable-attempt identity publication from record-free valid-entry reuse probes, and explicitly inherit the use guard for those probes through actual termination. The lifecycle must preserve its promised read-only reuse contract.

R2-D2 is resolved by the named 60-second metadata budget and retry policy. The accepted earlier repairs remain intact. Reviewer choices remain Q01-Q08 A (Q07 conditional on the lifecycle repair), Q09 B, Q10 A, Q11 conditional A, Q12 A, Q13 B, Q14 A, Q15 C, Q16 A and Q17 corrected A. All Q01-Q17 await human choices; request another review and do not consolidate.

### Writer instructions for design-specification git-cliff-provisioning round 3

Revise the design and question companion, then request another automated review. Keep all seventeen human decisions pending and do not consolidate.

1. Replace the separate CreateProcessW/AssignProcessToJobObject sequence with specified creation-time containment, for example STARTUPINFOEX attributes containing both PROC_THREAD_ATTRIBUTE_JOB_LIST and HANDLE_LIST. State its supported Windows baseline, job nesting/creation failure handling and fail-closed behavior. A child must never exist outside the required containment, even if the caller dies before CreateProcess returns. Keep the primary thread suspended until necessary attempt identities are safely published.
2. Correct the lifecycle's parent-death explanation, confirmed-facts/foundation text, Q17 A and affected Q07/Q09/Q10 consequences. Remove the assertion that a never-resumed child is necessarily terminated by a job it has not yet joined. No alternate parent-only cleanup action can repair that crash interval.
3. Classify child paths explicitly: cache-writing download/metadata attempts and staging probes publish required recovery identities in their existing writable attempt; valid-entry reuse probes and git-cliff runs take no provisioning lock and write no cache records. Define metadata context only where it actually writes state. All children still receive the corrected containment and deadline/lifetime rules.
4. State explicitly that every guarded executable invocation, including a cached --version reuse probe, inherits the guard for its actual lifetime. Preserve lock-free, offline, read-only valid-entry reuse and unchanged normal launcher streams/status.
5. Add meaningful process-free cases for parent death during creation and immediately after creation before identity publication; creation-time job setup/nesting failure; and a read-only valid-entry reuse probe with no lock/staging/owner-file writes. Specify bounded developer checks of creation-time containment and probe guard lifetime outside pytest; do not claim unperformed checks as evidence.

Preserve the accepted six original repairs and 60-second metadata stage budget. The 2.7.0 evidence exception and item boundaries stay settled. A separate Q18 is unnecessary if these consequences are expressed in the existing lifecycle choices.

### Final reviewer decision for design-specification git-cliff-provisioning round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-14T16:16:38+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 4

### Requestor assessment for design-specification git-cliff-provisioning (round 4)

Writer assessment of the git-cliff-provisioning design, round 4.

Both round 3 findings are accepted and applied; the six round 1 repairs and
the 60 s metadata budget are kept.

R3-D1, creation-time containment: the "Child process lifecycle" subsection no
longer creates a child and assigns it to the job afterwards. Each child is
created with `CreateProcessW`, `CREATE_SUSPENDED` and
`EXTENDED_STARTUPINFO_PRESENT`, through a `STARTUPINFOEX` whose attribute list
carries `PROC_THREAD_ATTRIBUTE_JOB_LIST` (the parent-only kill-on-close job)
and `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` (standard handles, plus the use guard
for a child that executes a cached entry). Job membership is therefore part
of the creation call: if the parent dies during or after creation, either no
child exists or it is already a member that the job's closure ends. The
supported baseline is Windows 10 or Windows Server 2016, x64, the first
releases that document the job-list attribute; the platform check rejects an
older Windows before any download or child. A job creation, attribute or
creation-time association failure, including a nesting refused under a host
job with UI limits, returns no child and fails the stage with a containment
diagnostic (status 69 for `gcliff`, 2 for engine operations). There is no
create-then-assign fallback and no `subprocess` fallback. The parent-death
paragraph, the confirmed facts (new rows for `AssignProcessToJobObject`,
`UpdateProcThreadAttribute` and nested jobs), the foundation changes, Q17 A
and the Q07, Q09 and Q10 consequences now say this; the false claim that a
never-assigned child is ended by a job it has not joined is gone.

R3-D2, child classes: a table classifies every child.

- Cache-writing: the download worker and the staging probe of a provisioning
  or candidate attempt, recorded in the lock record and staging owner file
  before resume.
- Record-free: the valid-entry reuse probe (entry or candidate), the harness
  metadata worker, which returns the metadata on its standard output and
  writes nothing, and every git-cliff run. They take no lock and write no
  cache record.

Every child that executes a cached entry's executable, the reuse probe as
well as each git-cliff run, inherits that entry's use guard for its actual
lifetime. Reuse stays lock-free, offline and read-only, and the normal
launcher streams and status are unchanged.

Acceptance cases add: parent death during creation; parent death after
creation before recording, reworded around membership from creation;
creation-time containment failures; a Windows release below the baseline;
recording failure of a cache-writing child; valid-entry reuse with no lock,
staging or owner-file write; caller death during a reuse probe; harness death
during the metadata worker. Testing adds a fake Windows layer that models
creation as one step (no child, or a child already in its job), a read-only
reuse scenario that rejects every write, and bounded developer-run checks:
`IsProcessInJob` before resume, parent killed while the child is suspended,
creation refused under a UI-limited job with no child left, and the reuse
probe's guard after its caller is killed. None of these checks has run.

No question was added. Q17 A starts with the suggested replacement wording
plus the baseline; its pros no longer claim that nothing is unaccounted for at
every launch boundary, and its con names the baseline and the nesting failure.
Q03, Q07, Q09, Q10 and Q12 carry the corrected classification and containment.
All seventeen decisions remain pending.

Please assess whether creation-time containment and the fail-closed rules
close the crash interval R3-D1 identified, whether the child classes and guard
inheritance preserve the read-only reuse contract, and whether the questions
still expose the alternatives the human needs.

### Change summary for design-specification git-cliff-provisioning (round 4)

Changes since round 3 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Confirmed facts: the job-objects implication covers children associated
  with the job; new rows for `AssignProcessToJobObject` (association only when
  called), `UpdateProcThreadAttribute` (`PROC_THREAD_ATTRIBUTE_JOB_LIST` from
  Windows 10 and Windows Server 2016, `PROC_THREAD_ATTRIBUTE_HANDLE_LIST`) and
  nested jobs (refused under UI limits); the CPython row no longer mentions a
  later assignment.
- Target flow and reuse check: the reuse probe is a contained, record-free
  child that inherits the guard; every execution of a cached executable
  inherits the guard; reuse, its probe included, takes no lock and writes
  nothing.
- Version probe: reuse probe and staging probe roles distinguished.
- Child process lifecycle: a class table (cache-writing versus record-free);
  creation through `STARTUPINFOEX` with the job list and handle list; fail
  closed on job, attribute, association or nesting failure, with no
  create-then-assign or `subprocess` fallback; Windows 10 or Windows Server
  2016 baseline; the parent-death explanation rewritten around membership from
  creation.
- Deadline enforcement: the metadata worker is record-free and writes nothing;
  developer checks include a parent killed while its child is still suspended.
- Failure diagnostics and statuses: platform remedy names the baseline; a new
  containment remedy; status 69 lists child containment.
- Candidate lifecycle: metadata read through the record-free metadata worker.
- Testing, foundation changes and acceptance cases: creation modeled as one
  step, read-only reuse scenario, bounded developer checks (`IsProcessInJob`,
  suspended-child kill, refused nesting, reuse-probe guard); the Windows layer
  has no create-then-assign path; the platform check requires the baseline;
  five new acceptance cases, the assignment-failure case split into a
  containment-failure case and a recording-failure case, and the
  suspended-worker case reworded.
- Questions: Q17 description, BBQ, option A, recommendation and answer
  corrected; Q03, Q07, Q09, Q10 and Q12 carry the classification and
  creation-time containment. No question added; all seventeen pending.
- One overlong line in "The harness" rewrapped (no wording change).

The companion is byte-identical to the section. markdownlint reports 0
issues. cSpell reported `STARTUPINFOEX`; the user chose to add it to the
project's `.vscode/settings.json`, and the check is now clean.

### Writer response for design-specification git-cliff-provisioning (round 4)

Writer response:

Response to the round 3 answer (changes-requested). Both findings are accepted;
there is no disagreement.

- R3-D1: the writer took the job-list attribute the answer named. The
  Microsoft documentation lists `PROC_THREAD_ATTRIBUTE_JOB_LIST` as supported
  in Windows 10 and newer and Windows Server 2016 and newer, so that is the
  stated baseline; the nested-jobs page documents that nesting is refused when
  a job sets UI limits, which the design turns into a containment failure
  rather than a fallback. The documentation does not spell out what
  `CreateProcessW` leaves behind when the job association fails; the design
  requires that no child exist, models it in the process-free suite and adds a
  bounded developer check (creation under a UI-limited job, no child left)
  instead of asserting it as observed. Suspended creation and identity
  publication before resume are kept for cache-writing children.
- R3-D2: the metadata worker is classified record-free by making it write
  nothing (it returns the metadata on standard output), which is simpler than
  giving it an attempt context. The reuse probe inherits the guard through the
  same creation path as a git-cliff run, so a contained probe cannot outlive
  the only guard; no cache write was added to reuse.

No new question; the corrections live in Q17 and its consequences in Q03, Q07,
Q09, Q10 and Q12. No runtime experiment was performed; the developer-run
checks are specified, not claimed.

### Reviewer focus for design-specification git-cliff-provisioning (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-14T16:20:15+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 4

The current specification and round 4 request agree on the two repaired lifecycle rules. R3-D1 is addressed: job membership is supplied in the creation attributes, not assigned in a later parent action; suspended creation still prevents an unrecorded cache-writing child from executing. Failure is closed, with an explicit Windows baseline and no uncontained fallback. R3-D2 is addressed: download workers and staging probes belong to writable attempts, while reuse probes, metadata workers and git-cliff runs publish no cache records. Every execution of a cached executable inherits its guard, covering parent death until the child actually exits.

The current text preserves separate guarantees: the job triggers termination, the inherited handle prevents replacement during termination, and recorded process identities prevent premature recovery. Parent death and mutex abandonment are not substituted for a recorded child's death. Read-only reuse remains possible.

I reviewed the whole current design and all seventeen questions, including the candidate lifecycle, deadlines, launcher and evidence proposals. The linked requirement's clarification table and evidence scope support the proposed choices. No missing decision requires an additional question. Q17 now exposes the additional Windows baseline and failure under incompatible host jobs as real costs, rather than hiding them.

This is design convergence, not runtime validation. Real creation-time association, failure cleanup, job nesting, termination and guard inheritance remain implementation acceptance obligations. The request correctly says that the developer checks have not run. Fakes alone cannot establish these operating-system properties.

### Question verdicts for design-specification git-cliff-provisioning round 4

All seventeen questions are relevant, sufficiently distinct and understandable. None is redundant or outside this design's scope. I agree with the proposed answers below; all remain pending human choices.

| Question | Reviewer choice | Reason |
| --- | --- | --- |
| Q01 | A | Recording the published digest at reviewed admission binds subsequent downloads to the tested bytes without a release-time API dependency. |
| Q02 | A | Frozen Python records fit the existing shipped registries and retain reviewed admission. |
| Q03 | A | The existing record and short-mutex pattern preserves DEAD-only recovery, including recorded children; a whole-operation mutex does not remove that requirement. |
| Q04 | A | Per-version/platform locks serialize shared writes while candidate namespace separation permits independent work. |
| Q05 | A | Fixed finite budgets keep the confirmed configuration surface small and can be revisited at admission. The harness-only metadata budget is also finite. |
| Q06 | A | One transient retry inside the original deadline balances recovery and predictable failure; integrity failures remain non-retryable. |
| Q07 | A | A deny-write/delete read handle covers validation through actual child lifetime, including reuse probes; replacement tests that protection by renaming the executable first. |
| Q08 | A | Standard proxy resolution meets the stated network scope with explicit limits for PAC-only and authenticated proxies. |
| Q09 | B | An invocation object centralizes environment policy, containment and guard transfer while leaving rendering arguments and timeouts to item 4. |
| Q10 | A | A Python parent preserves one status path and the existing batch argument guard, with explicit containment and Ctrl+C handling. |
| Q11 | A | 69 distinguishes pre-start failure, conditional on the required admission audit; sampled successes are not proof of exclusivity. |
| Q12 | A | An isolated evidence namespace reuses safe lifecycle primitives without allowing candidates into production resolution. |
| Q13 | B | Recorded inputs, output digests, contextual differences and classifications retain reviewability and reproducibility without committing every identical output. |
| Q14 | A | A deterministic script is reviewable; recorded object hashes detect regeneration drift. |
| Q15 | C | An internal comparison module serves current evidence and later upgrade work without prematurely exposing a public interface. |
| Q16 | A | A tested alias fragment supplies exactly what the later shared exposure needs while respecting its scope boundary. |
| Q17 | A | Creation-time job membership closes the create-then-assign interval; suspended starts, child classification, guard inheritance and DEAD-only recovery cover the separate execution and cleanup hazards. |

Q09 B and Q13 B are proposed changes to the current body's path-return and full-output formulations, not already confirmed decisions. Their eventual integration belongs to human-authorized consolidation. Likewise, Q17 A's baseline and incompatible-job failure behavior remain choices for the user, not approvals granted by this review.

### Convergence evidence for design-specification git-cliff-provisioning round 4

Covered wording:

Suggested wording for the provisioning seams: "Production supplies the download worker, contained Windows child launcher, process-state probe and use-guard implementation; tests supply fakes."

Suggested wording for the child-class paragraph: "A cache-writing child belongs to an attempt that already holds the lock and owns staging. A record-free child needs no attempt record and makes no cache writes; it may also be used by the entry recheck after a provisioning caller acquires the lock."

These edits clarify the already specified creation path and under-lock recheck. They add no behavior or new decision.

Convergence rationale:

The current round resolves the two requested substantive defects and propagates the repairs through the lifecycle, questions and acceptance cases. The remaining alternatives are exposed as explicit pending human decisions. No additional question or behavioral revision is required before that discussion; the residual edits are wording only. Recommend convergence, with no authority to consolidate and no claim that implementation acceptance has run.

### Writer instructions for design-specification git-cliff-provisioning round 4

Recommend convergence of the reviewed formulation. Preserve all seventeen pending user decisions. Do not consolidate or mark the Windows checks passed on the strength of this answer.

Only wording polish remains: qualify the remaining generic references to production "subprocess" implementations as the contained Windows child launcher (the standard library may still provide command-line quoting helpers). In the child-class explanation, say that record-free children do not require an attempt or publish their own cache records, rather than saying they can never run while an attempt holds a lock: the target flow deliberately rechecks an entry after acquiring the provisioning lock. This clarification changes neither reuse behavior nor locking policy.

When consolidation is separately authorized, integrate the selected Q09 interface and Q13 bundle format consistently into the body and retain the bounded real-Windows acceptance checks. Failure of those checks during implementation must be resolved before claiming the lifecycle validated.

### Final reviewer decision for design-specification git-cliff-provisioning round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-14T21:21:37+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-14T21:22:31+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 5)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 5

### Requestor assessment for design-specification git-cliff-provisioning (round 5)

Writer assessment of the git-cliff-provisioning design, round 5: follow-up
review of the user's decisions after the round 4 convergence.

At the round 4 gate the user chose "Explain undecided questions". Each of the
seventeen questions was explained in turn and the user recorded an explicit
decision for every one on 2026-11-14 (scanner: 17 questions, 0 undecided, no
diagnostics). The decisions are written under each question as
`User decision: confirmed: ...`; the recommendations and question blocks are
kept unchanged.

| Question | User decision | Same as the recommendation |
| --- | --- | --- |
| Q01 digest source | A, manifest digest recorded at admission, no API call at release time | Yes |
| Q02 manifest form | A, frozen Python records | Yes |
| Q03 lock mechanism | A, record, short transition mutex, liveness probe, 250 ms polling | Yes |
| Q04 lock granularity | A, one lock per version and platform | Yes |
| Q05 budgets | B, fixed constants plus one documented environment variable that raises the download and wait budgets | No (recommended A) |
| Q06 retries | A, one retry after 5 s inside the budget | Yes |
| Q07 invalid entry | A, use guard and rename-first replacement | Yes |
| Q08 proxy | A, `urllib.request.getproxies()` | Yes |
| Q09 entry point | B, invocation object | Yes |
| Q10 gcliff start | A, Python launcher with a contained child | Yes |
| Q11 reserved status | A, 69 with the per-version audit | Yes |
| Q12 candidate location | A, `evidence/` subtree | Yes |
| Q13 evidence bundle | B, digests, differing hunks and classification | Yes |
| Q14 fixture history | A, deterministic script with recorded hashes | Yes |
| Q15 harness surface | C, internal module with a developer entry point | Yes |
| Q16 alias definition | A, tested fragment beside the launcher | Yes |
| Q17 child lifecycle | A, creation-time job containment, Windows 10 or Windows Server 2016 baseline | Yes |

Points the writer sees for this review, none of them yet applied to the body
(consolidation integrates decisions only after a human `Consolidate`):

1. Q05 B departs from the recommendation. The body still says the budgets are
   engine constants, "not configuration, in line with Q07's no-new-setting
   decision", and the Q05 description says requirement Q07 rejected a new
   network setting. The consolidated requirement excludes a mirror setting
   ("no mirror setting"; rejected alternative "a mirror base URL"), not a
   budget override, so the writer reads no conflict with requirement Q07.
   Requirement Q15 still requires every budget, raised or not, to be
   documented and finite. The decision record lists what consolidation must
   define: the variable's name, form, accepted range and refusal of an invalid
   value; a wait budget kept above the raised holder budgets (download plus
   probes); the variable named in the expiry remedies; the body sentence
   replaced. Whether the override also covers the probe budget, and whether
   it is read by the harness's 60 s metadata budget, is not decided.
2. Q09 B and Q13 B replace the body's path-return and raw-output
   formulations at consolidation, as the round 4 answer noted.
3. Q07 A depends on Q17 A for its parent-death guarantee; both are chosen.

No notion was introduced into any document during the discussion. At Q14 the
user said they were lost; the question was restated in plain language (a tiny
scripted repository with `-SNAPSHOT` tags for the comparison) and the user
then confirmed A. No other document changed since round 4 apart from the
round 4 covered wording edits, which the change summary lists.

Please review the decisions and comments for consistency with the whole
design, the consolidated requirement and the umbrella; assess whether Q05 B
needs further constraints or a new question (for example the override's form,
range and scope) before consolidation; and identify any missing or new
question the decisions raise. Reviewer recommendations cannot overwrite the
user's choices; please surface any conflict instead.

### Change summary for design-specification git-cliff-provisioning (round 5)

Changes since round 4 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Covered wording edits from the round 4 answer, applied before the gate:
  the child-class table and paragraph say a record-free child needs no
  attempt record and makes no cache writes, and may also serve the entry
  recheck after a caller acquires the lock; the provisioning seams name the
  download worker, contained Windows child launcher, process-state probe and
  use-guard implementation; the standard-library row names `ctypes` for the
  contained child launcher and `subprocess` only for its command-line quoting
  helper.
- Q01 to Q17: each answer section's `User decision: pending` replaced by a
  `User decision: confirmed: ...` record dated 2026-11-14, with the choice and
  its stated consequences. Q05 records option B instead of the recommended A,
  first picked as A and corrected to B by the user, with the consolidation
  obligations listed above. No question ID, option, recommendation or
  explanation was changed; no question was added or removed.

The companion is byte-identical to the section. markdownlint reports 0
issues and cSpell finds no unknown word. The question scanner reports 17
questions, 0 undecided, no diagnostics.

### Writer response for design-specification git-cliff-provisioning (round 5)

Writer response:

Response to the round 4 answer (convergence-recommended). The two covered
wording edits were applied before the human gate, with no behavior change.
The user then selected "Explain undecided questions"; this round is the
follow-up review that selection requires, published through "Revise and
review again" after all seventeen decisions were recorded.

The writer agrees with sixteen decisions as recommended. For Q05 the user
chose B over the recommended A; the writer accepts it as the user's decision
and records the constraints it creates rather than arguing for A. The writer
asks the reviewer to say whether those constraints are complete enough for
consolidation, or whether the override's form, range or scope needs its own
question.

No experiment was run. The developer-run Windows checks remain specified,
not performed.

### Reviewer focus for design-specification git-cliff-provisioning (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-14T21:28:16+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 5

Disposition: changes-requested.

I reviewed the current request and the full current design, including all 17
recorded user decisions, against the requirement's network, contention,
finite-budget and evidence contracts and the umbrella's item 3 boundary.
All 17 decisions are explicit human choices. Preserve them, including Q05 B;
the earlier recommendation of A is not authority to reverse that choice.

The choices are mutually compatible. Requirement Q07 excludes a mirror URL,
not a time-budget override: see the requirement's provisioning sequence and
its Q07 clarification. Requirement Q15 requires documented finite budgets,
not fixed constants. Q09 B encapsulates the Q07/Q17 guard and containment
rules without taking item 4's rendering choices. Q13 B still compares raw
outputs and records every difference; the requirement does not demand that
every identical raw output be committed. Q14 A's recorded hashes check the
deterministic fixture. No new conflict with the umbrella was found.

One substantive decision is missing. At design lines 1094-1103, Q05 B defers
the variable's form and accepted range to consolidation, but does not define
which budgets it affects beyond download and waiting, or how concurrent
callers with different environment values interact. The request itself
identifies the probe and metadata scope as undecided. Naming the variable can
be editorial; choosing whether a hung probe or metadata lookup may run longer,
how long users may wait, and whether one caller extends another's deadline
changes behavior. Those rules must be reviewable before consolidation.

For example, a holder using a 1,800 s download budget and a default waiter
using 360 s cannot both satisfy an unconditional promise that the wait exceeds
the holder's budget. The requirement expressly allows the waiter to fail when
the holder does not finish within that waiter's budget (requirement lines
246-249). Keep that finite per-caller policy, or explicitly propose a different
bounded policy; do not silently extend a wait whenever the holder changes.

Add one focused follow-up question for Q05 B's concrete override contract.
The recommended package and alternatives are in the requested changes. Its
new answer is a reviewer proposal, not a human decision. This is more than
word polishing, so the current formulation is not convergence-ready.

The stale path-return and raw-output body formulations are known deferred
consolidation work for Q09 B and Q13 B, not reasons to reopen those choices.
The fixed-only budget body and the broad claim that requirement Q07 forbids a
new setting likewise need replacement when the choices are consolidated.
No design or companion document was edited by this reviewer. No experiment,
binary comparison or Windows acceptance check was run; the specified runtime
evidence remains an implementation obligation.

### Question verdicts for design-specification git-cliff-provisioning round 5

All existing questions are in scope, distinct and useful. Their alternatives
describe materially different choices. None should be removed or reopened
merely because the human has now answered it. The following assessment treats
the recorded user decision as authoritative.

| Question | Recorded choice | Reviewer verdict and reason |
| --- | --- | --- |
| Q01 | A | Agree: admission records the published digest and release-time provisioning avoids metadata availability and rate limits. |
| Q02 | A | Agree: frozen records fit the shipped registry model and keep pin admission reviewed. |
| Q03 | A | Agree: brief transition serialization and process identities preserve DEAD-only recovery; a mutex's abandonment alone is insufficient. |
| Q04 | A | Agree: independent version/platform entries and candidate namespaces need not serialize each other. |
| Q05 | B | Accept and support the human's adjustable-budget choice. Its motivation is valid and requirement Q07 does not prohibit it. The concrete override contract needs the focused follow-up below; do not restore A. |
| Q06 | A | Agree: one retry and its 5 s delay consume the same deadline, including an overridden one. Clarify that the non-retried 4xx cases exclude the expressly retryable 429. |
| Q07 | A | Agree: the inherited guard protects validation through actual child exit, with Q17 A supplying creation-time containment. |
| Q08 | A | Agree: standard proxy resolution matches the selected network scope; authenticated proxies and PAC support remain excluded. |
| Q09 | B | Agree: the invocation object centralizes environment policy, containment and guard transfer while item 4 retains rendering arguments and deadlines. |
| Q10 | A | Agree: a contained Python-launched child preserves streams and status under the existing batch guard. |
| Q11 | A | Agree conditionally on the already required per-version exit-path audit; the choice does not prove status 69 is excluded. |
| Q12 | A | Agree: a separate evidence namespace with immutable trust records provides offline candidate reuse without production admission. |
| Q13 | B | Agree: controlled inputs, output digests, differing hunks and classification retain reproducibility and reviewable differences without storing identical outputs. Preserve per-run statuses and the exit-path audit too. |
| Q14 | A | Agree: fixed object-producing inputs plus recorded commit and tag hashes make fixture regeneration checkable. The user's request for a simpler explanation adds no technical conflict. |
| Q15 | C | Agree: reusable internal comparison logic serves this item without defining item 6's public interface prematurely. |
| Q16 | A | Agree: a tested alias fragment preserves item 8's ownership of shared exposure. |
| Q17 | A | Agree: creation-time job membership and inherited guards address parent death without writable reuse records; real Windows evidence remains required. |

The Q05 options incorrectly attribute a general ban on network settings to
requirement Q07. Correct that description without altering the recorded
decision. The main missing question is the concrete contract of the chosen
override, not whether to allow an override at all.

### Requested changes for design-specification git-cliff-provisioning round 5

Requested changes:

Required change: add Q18, "What contract does the Q05 budget override expose?"
Keep Q05 B confirmed. Explain that one environment variable has already been
chosen; this question defines its meaning and scope. Include distinct options,
their consequences, a recommendation and an explicitly pending human decision.

Recommended option A, as a concrete reviewer proposal:

- Name: `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS`, outside the upstream
  `GIT_CLIFF_*` namespace scrubbed by the invocation object.
- Unset means the existing 300 s aggregate archive-download deadline. A set
  value is an ASCII decimal integer in seconds from 300 through 3600 inclusive.
  Reject empty strings, signs, fractions, units, whitespace and out-of-range
  values; never silently clamp or fall back. The upper limit is a proposed
  operational policy, not a bound derived from the requirements.
- Let D be that invocation's validated download budget. Its lock wait is
  W = D + 60 s: 300/360 by default, 900/960 for a 900 s override, and
  3600/3660 at the proposed maximum. The extra 60 s retains two 15 s probe
  allowances and the existing 30 s processing allowance. This is a contention
  policy, not a promise that all filesystem work always completes in 30 s.
- Apply D and W to both production provisioning and evidence-candidate archive
  provisioning. Socket connect/inactivity stays 30 s, every version probe stays
  15 s, and the harness metadata lookup stays 60 s. Those stages are explicitly
  outside this override. Rendering deadlines remain item 4's responsibility.
- Sample and validate the policy once when a caller enters provisioning or
  starts the evidence harness, before a reuse probe, child creation, network
  access or cache mutation; pass the resolved policy to workers rather than
  rereading the environment. An invalid value is a setup/configuration failure
  (engine status 2, gcliff status 69), including with a valid cached entry.
  Operations that do not need git-cliff do not read this variable.
- Every caller owns its finite W. A 360 s waiter may time out behind a holder
  using D = 1800 s; its deadline is never reset or enlarged by a holder change.
  The relation W = D + 60 applies to the caller's own configured policy, not
  to an arbitrary holder's environment. A timeout never authorizes recovery of
  a live or UNKNOWN owner. This is consistent with requirement Q06.
- Q06's retry count, 5 s delay and shared deadline remain unchanged. The wait
  line and expiry diagnostics show the effective budgets. Download and wait
  expiry remedies name the variable and its supported range; probe and
  metadata expiry must not suggest that this variable extends their budgets.

Why A: users can request an exact duration for the slow archive transfer while
keeping the two affected budgets coupled and bounded. It adds one setting,
preserves the chosen narrow scope and avoids making a hung local probe slower
to diagnose. Its cost is that a slow metadata service or a socket inactivity
timeout is not cured by raising the archive budget, and differently configured
callers can still time out on contention.

Alternative B: one integer multiplier from 1 through 12 affecting only the
download and wait policy, D = 300*m and W = D + 60, with the same fixed other
stages and per-caller behavior. Pro: a simple relative scale with unchanged
defaults. Con: coarse 300 s steps, and the effective duration moves if base
constants later change. It is still an implementation of Q05 B.

Alternative C: one multiplier from 1 through 12 that scales the download,
socket, probe, metadata and wait constants together. Pro: one knob also helps
slow metadata and probe environments, with a finite upper bound. Con: it
extends the scope of the existing decision and delays unrelated failure
detection (at 12, a version probe may take 180 s and metadata 720 s). This
broader scope requires a new explicit human choice; Q05 B alone did not grant
it. Rendering still stays outside the setting.

The writer may propose another concrete bounded package with its rationale,
but must not leave the form, limits, affected stages or mixed-caller semantics
for an implementation-time guess. Do not make a separate question merely to
pick the spelling of a variable.

Add acceptance examples alongside the proposed contract: defaults, an exact
raised value, the maximum, invalid/empty/out-of-range input, valid-cache reuse
with an invalid value, unrelated operations ignoring the setting, retry and
Retry-After staying inside D, unchanged probe/metadata deadlines, candidate
downloads using D, and a default waiter timing out safely behind a raised
holder without recovering it. Specify fake-clock validation; do not run real
long waits or introduce tests in this specification review.

Covered wording corrections:

1. Replace the assertion that requirement Q07 rejected any new network setting
   with: "Requirement Q07 excludes a mirror setting; Q05 B permits one finite
   provisioning-budget override."
2. In Q06's description and recorded consequence, use "HTTP 429 or 5xx is
   retryable; other HTTP 4xx, size overflow and digest mismatch are not".
   This clarifies the already specified 429 exception without changing the
   confirmed retry policy.

### Writer instructions for design-specification git-cliff-provisioning round 5

Preserve all 17 explicit user decisions, especially Q05 B. Add the single
focused override-contract question described in the requested changes, with
the recommended package marked as proposed and its human decision pending.
Correct the false requirement-Q07 attribution and the HTTP-429 wording.
Keep the question companion synchronized through its owning workflow.

Do not consolidate now. Publish the revised formulation for another automated
review round. No new human choice is being made by this answer; the requestor
retains the human decision workflow after the new question has been reviewed.

When consolidation is separately authorized, integrate Q05 and its follow-up
across budgets, worker inputs, diagnostics, acceptance cases and the evidence
harness. Integrate Q09 B across the entry-point contract and callers, and
Q13 B across the bundle description while preserving output statuses,
classification and the admission audit. These known body differences do not
authorize changing the recorded choices or prematurely consolidating them.

There is no literal Human guidance block in this request. The decisions and
the writer's explicit questions have been addressed in the assessment and
question verdicts. Runtime containment and compatibility evidence remains
specified, not validated by this review.

### Final reviewer decision for design-specification git-cliff-provisioning round 5

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-5 -->

## Round 6 by requestor

- Recorded: 2026-11-14T21:32:43+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 6)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 6

### Requestor assessment for design-specification git-cliff-provisioning (round 6)

Writer assessment of the git-cliff-provisioning design, round 6.

The round 5 changes are accepted and applied; all seventeen recorded user
decisions are kept unchanged, Q05 B included.

New question Q18, "What contract does the Q05 budget override expose?",
follows Q17 with its description, BBQ, three options, recommendation, answer
and `User decision: pending`. Its description states that Q05 B is confirmed
and that Q18 defines the override's meaning and scope without reopening it.

- Option A is the reviewer's proposal, kept as proposed:
  `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS`, an ASCII decimal integer
  from 300 through 3600 seconds, refused (never clamped) when malformed or out
  of range; the caller's own wait W = D + 60 s; D and W for production and
  candidate archive downloads only, with socket 30 s, probe 15 s and metadata
  60 s unchanged; read and validated once before any reuse probe, child,
  network access or cache change, then passed to workers; an invalid value is
  status 2 for engine operations and 69 for `gcliff`, even with a valid cached
  entry; operations that need no git-cliff never read it; every caller owns
  its finite W and a timeout never recovers a live or `UNKNOWN` owner; Q06's
  retry stays inside D; diagnostics show the effective budgets and only the
  download and wait remedies name the variable.
- Option B is a 1 to 12 multiplier for the download and wait only.
- Option C is a 1 to 12 multiplier for every stage, noted as widening Q05 B's
  scope.
- An acceptance table for the chosen contract (stated for option A, checked
  with a fake clock) covers the defaults, an exact raised value, the maximum,
  invalid inputs, a valid cache with an invalid value, operations ignoring the
  variable, retry and `Retry-After` inside D, unchanged probe and metadata
  budgets, candidate downloads using D, and a default waiter timing out behind
  a raised holder without recovering it.

Covered wording corrections: the Q05 description, Q05's option A pro and
option B con, and the body's budget paragraph no longer attribute a general
ban on new settings to requirement Q07 (it excludes a mirror setting). Q06's
description, its recorded decision text and the body's budget row now say
that HTTP 429 or 5xx is retryable while other HTTP 4xx, size overflow and
digest mismatch are not; the retry policy itself is unchanged.

The body still describes fixed budgets, path return (Q09 B) and raw outputs
(Q13 B); integrating those decisions, and Q18 once decided, belongs to
consolidation. Scanner: 18 questions, Q18 undecided.

Please assess whether Q18's options and acceptance examples define the
override completely enough for a human decision, and whether the corrections
are accurate.

### Change summary for design-specification git-cliff-provisioning (round 6)

Changes since round 5 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Time budgets: the archive-download row says "none for another HTTP 4xx";
  the paragraph after the table says requirement Q07 excludes a mirror
  setting, not a budget override, and that Q05 and Q18 decide the one
  override (the fixed-budget body itself awaits consolidation).
- Q05: description and the option A pro and option B con corrected about
  requirement Q07; the recorded decision is unchanged.
- Q06: description and recorded decision text state the HTTP 429 exception
  explicitly; the decision is unchanged.
- Q18 added after Q17: description, BBQ, options A, B and C, acceptance
  examples, recommendation (A), answer, and `User decision: pending`.

The companion is byte-identical to the section. markdownlint reports 0
issues and cSpell finds no unknown word.

### Writer response for design-specification git-cliff-provisioning (round 6)

Writer response:

Response to the round 5 answer (changes-requested). The requested question
and both covered corrections are accepted; there is no disagreement.

- Q18 takes the reviewer's package as option A nearly verbatim, because it
  leaves nothing to implementation-time guessing: form, range, affected
  stages, sampling point, failure statuses and mixed-caller semantics. The
  writer added only the explicit statement that W = D + 60 s applies to the
  caller's own policy, and wrote the acceptance examples as a table inside
  Q18 rather than in the body's acceptance cases, since the contract is not
  decided yet. The leading-space input is written in words to keep the
  Markdown valid.
- The Q06 clarification touches the user's recorded decision text only to
  spell out the 429 exception the option already contained.

Q18 remains a reviewer proposal; the human decision is pending and will be
asked after this round, through the question-explanation workflow.

### Reviewer focus for design-specification git-cliff-provisioning (round 6)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-6 -->

## Round 6 by reviewer

- Recorded: 2026-11-14T21:37:20+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 6

The complete current design and round 6 request have been reviewed. The round
5 substantive gap is resolved in the formulation: Q18 presents a concrete,
bounded override contract without treating the reviewer's proposal as a human
decision. Q01-Q17 retain their recorded choices, including Q05 B.

Q18 A specifies the name, syntax, inclusive range, default, rejection behavior,
sampling point, propagation to workers, affected stages, effective diagnostics
and independent waiter deadlines. Its production and evidence-candidate scope
is explicit. Retry count and delay remain inside D; socket, probe and metadata
limits remain unchanged. Invalid configuration is rejected even on cache reuse,
while operations needing no git-cliff ignore it. The acceptance examples cover
the requested observable cases without real waits.

The requirement allows a waiter to expire when a holder exceeds that waiter's
budget. Q18 correctly avoids a promise that a default waiter outlasts a raised
holder, and never turns expiry into permission to recover ALIVE or UNKNOWN
actors. Its 3600 s ceiling is explicitly a proposed operational policy.

The requirement-Q07 correction is accurate: the requirement prohibits a mirror
setting, not a budget override. The HTTP wording now consistently retries 429
and 5xx while excluding other 4xx, size overflow and digest mismatch.

No additional missing question was found. Q18 A is sufficiently complete for
the human decision. B is a distinct coarse relative alternative; C expressly
requires a broader scope choice. Neither alternative has been selected.

The fixed-budget body, path-return API and raw-output storage text still await
authorized consolidation of Q05, Q09 and Q13, plus Q18 after its decision. That
declared deferral is not a new review blocker. Preserve the statuses and
exit-path audit when consolidating the compact evidence bundle.

This is specification review only. No implementation test, real Windows
containment/termination/guard check, or compatibility evidence run was performed;
those remain required implementation/admission evidence.

### Question verdicts for design-specification git-cliff-provisioning round 6

All eighteen questions are in scope and materially distinct. Q18 supplies the
previously missing contract; no further question is needed for the recommended
formulation. Reviewer choices below preserve explicit human authority.

| Question | Human choice | Reviewer choice and reason |
| --- | --- | --- |
| Q01 | A | A: recorded published digests avoid release-time metadata availability and quota dependencies. |
| Q02 | A | A: frozen Python records fit the shipped registries and reviewed admission. |
| Q03 | A | A: short serialization and process identities preserve DEAD-only recovery. |
| Q04 | A | A: version/platform and candidate namespaces isolate independent work. |
| Q05 | B | B: support the confirmed finite override; Q18 now supplies its concrete proposed contract. Do not restore A. |
| Q06 | A | A: one retry and 5 s delay share the deadline; the 429 exception is now clear. |
| Q07 | A | A: inherited guards protect the entry through the child's actual lifetime with Q17 containment. |
| Q08 | A | A: standard proxy resolution fits the confirmed network scope. |
| Q09 | B | B: the invocation object centralizes environment policy, containment and guard transfer. |
| Q10 | A | A: the contained Python-launched child preserves streams and status under the existing argument guard. |
| Q11 | A | A: 69 remains conditional on the required per-version exit-path audit, not merely observed sample statuses. |
| Q12 | A | A: isolated evidence namespace and immutable trust records support safe candidate reuse. |
| Q13 | B | B: controlled inputs, output digests, differing hunks and classification retain reproducibility; preserve statuses and audit. |
| Q14 | A | A: fixed object-producing inputs and recorded hashes make fixture regeneration checkable. |
| Q15 | C | C: reusable internal logic leaves item 6's public surface undecided. |
| Q16 | A | A: the tested alias fragment preserves item 8's exposure responsibility. |
| Q17 | A | A: creation-time containment and inherited guards cover parent death; real Windows checks remain required. |
| Q18 | Pending | A: exact seconds, bounded D and W, narrow stage scope and independent caller deadlines implement Q05 B with predictable failure behavior. |

Q18 B is materially different because its 300 s increments are coarse and move
with the base constant. Q18 C scales unrelated stages and therefore needs an
explicit expansion of Q05 B. These are meaningful consequences, not redundant
choices. The recommended A and its acceptance examples are complete enough for
decision; a later selection or amendment must be reviewed in its own context.

### Convergence evidence for design-specification git-cliff-provisioning round 6

Covered wording:

Only clarification of already stated semantics remains advisable. In Q05's
recorded decision commentary, replace the phrase "keeps the wait budget above
the raised holder budgets" with "defines the caller's finite wait budget in
Q18; it need not outlast a differently configured holder". Preserve the user's
confirmed B and selection history. This aligns explanatory wording with Q18's
explicit per-caller rule and the requirement's bounded-wait condition; it does
not select Q18 A on the user's behalf.

Optionally make Q18's description more precise: "Q05 B names download and
wait budgets; Q18 defines their representation, bounds and caller semantics.
Option C would additionally expand the affected stages." This avoids implying
that Q05 already authorized a broader scope.

No additional automated round is needed solely for these wording corrections.

Convergence rationale:

Recommend convergence of the reviewed formulation. The missing override
question and both factual wording corrections requested in round 5 are now
present. Q18 A closes the concrete behavioral gap, preserves the existing human
choices, and is consistent with the requirement's finite budgets and caller-
bounded contention. No substantive disagreement or further missing decision
beyond Q18 itself was found.

Q18 remains a pending human decision, including its proposed upper bound.
Convergence means the question and recommendation are ready for that decision;
it does not confirm the answer, authorize consolidation, or prove implementation.

### Writer instructions for design-specification git-cliff-provisioning round 6

Preserve Q01-Q17 and their recorded human choices. Keep Q18 pending until the
human explicitly answers it. Present A as the reviewer-supported recommendation,
including its operational 3600 s ceiling and the consequence that a default
waiter can expire behind a raised holder.

Apply the covered wording clarification without changing Q05 B. Do not treat
this recommendation as authorization to consolidate. After the human decides
Q18, review that decision and any comments for new conflicts or scope changes.

When consolidation is separately authorized, integrate the decided budget
policy throughout the flow, table, diagnostics and acceptance cases; replace
the path-return API with Q09 B's invocation object; and use Q13 B's compact
evidence representation while retaining observed statuses and the exit-path
audit. Keep item 4's rendering ownership and the specified real Windows and
compatibility-evidence obligations intact.

### Final reviewer decision for design-specification git-cliff-provisioning round 6

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-6 -->

## Round 6 by human - human-confirmation

- Recorded: 2026-11-14T21:55:54+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round

<!-- review-entry-id: human-confirmation-round-6 -->

## Round 7 by requestor

- Recorded: 2026-11-14T21:56:31+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: request

### Review identity for design-specification git-cliff-provisioning (round 7)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
Review round: 7

### Requestor assessment for design-specification git-cliff-provisioning (round 7)

Writer assessment of the git-cliff-provisioning design, round 7: follow-up
review of the Q18 decision after the round 6 convergence.

At the round 6 gate the user chose "Explain undecided questions" again. Q18
was explained in plain language (what value the variable takes, which limits
it raises, how two callers with different values interact) and the user
recorded option A on 2026-11-14 without amendment:
`LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS` as an exact download budget D
from 300 through 3600 seconds, the caller's own wait W = D + 60 s, every other
stage budget unchanged, the value validated once and refused when malformed or
out of range, and each caller keeping its own finite wait. The record states
that the 3600 s ceiling is accepted as the operational limit and that a
default waiter may expire behind a raised holder without ever recovering it.

Scanner: 18 questions, 0 undecided, no diagnostics. Q01 to Q17 keep the
decisions reviewed in round 6. The only other edits since round 6 are the two
covered wording clarifications from that answer (the Q05 record's wait
sentence and Q18's scope sentence).

Consolidation, once authorized, integrates Q05 with Q18 across the budget
table, worker inputs, diagnostics, acceptance cases and the evidence harness,
Q09 B across the entry point, and Q13 B across the bundle with statuses and
the exit-path audit.

Please review the Q18 decision and record for consistency with Q05 B, Q06 A,
Q03 A, Q11 A and Q12 A, the requirement and the umbrella, and identify any new
question the decision raises. Reviewer recommendations cannot overwrite the
user's choice; please surface any conflict instead.

### Change summary for design-specification git-cliff-provisioning (round 7)

Changes since round 6 in
`docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`:

- Covered wording from the round 6 answer, applied before the gate: the Q05
  decision record says consolidation defines the caller's finite wait budget
  in Q18, which need not outlast a differently configured holder; Q18's
  description says Q05 B names the download and wait budgets, Q18 defines
  their representation, bounds and caller semantics, and option C would
  additionally expand the affected stages.
- Q18: `User decision: pending` replaced by the confirmed option A record
  dated 2026-11-14. No option, recommendation or other question changed.

The companion is byte-identical to the section. markdownlint reports 0
issues and cSpell finds no unknown word.

### Writer response for design-specification git-cliff-provisioning (round 7)

Writer response:

Response to the round 6 answer (convergence-recommended). Both covered
wording clarifications were applied before the human gate. The user then
selected "Explain undecided questions" for Q18 and chose the recommended
option A; this round is the follow-up review that selection requires,
published through "Revise and review again". The writer has no disagreement
to report.

### Reviewer focus for design-specification git-cliff-provisioning (round 7)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-7 -->

## Round 7 by reviewer

- Recorded: 2026-11-14T21:59:50+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: answer

### Reviewer assessment for design-specification git-cliff-provisioning round 7

Reviewed the full current design and round 7 request. All eighteen questions
now contain explicit human decisions. Q18 A is recorded without amendment,
including acceptance of the 3600 s operational ceiling and the possibility
that a default waiter expires behind a raised holder. The record agrees with
the complete option A contract; it does not silently select an alternative.

The new decision is consistent with the existing choices and related scope:

- Q05 B: one environment variable raises only download D and lock wait W;
  defaults remain 300/360 s, the maximum is 3600/3660 s, and W = D + 60 s.
- Q06 A: one retry and its 5 s delay remain inside D, with no extension from
  Retry-After; HTTP 429/5xx remain retryable and other 4xx are excluded.
- Q03 A and Q17 A: each caller has its own finite deadline; expiry never
  authorizes recovery of ALIVE or UNKNOWN actors. Changing a holder does not
  reset a wait, and existing containment/termination obligations remain.
- Q11 A: malformed or out-of-range values fail before execution with status
  69 for gcliff and 2 for engine operations, including on a valid-cache path.
  This does not replace the required admission audit excluding git-cliff's
  own use of 69.
- Q12 A: the resolved policy also serves candidate archive downloads and
  waits, without changing their isolated namespace, trust records or admission.
  The harness metadata lookup stays 60 s; probes stay 15 s and socket limits
  stay 30 s. The value is validated once before provisioning/harness work.
- Q09 B and umbrella decisions 17-21: the setting is outside GIT_CLIFF_*,
  requires no global senv or executable-path setting, and does not alter the
  pinned internal binary or argument/stream passthrough. Operations needing
  no git-cliff ignore it, preserving their availability.
- Requirement Q06 explicitly permits failure at the waiting caller's budget;
  Q15 requires finite documented budgets, not fixed constants; Q07 prohibits
  a mirror setting, not this override. No cross-document conflict follows.

Both round 6 wording clarifications are present. No new missing question,
substantive disagreement or further wording correction was found. The recorded
choices can support implementation planning after separately authorized
consolidation integrates the known body differences: Q05/Q18 budgets, Q09's
invocation object and Q13's compact evidence representation.

This assessment validates specification consistency, not implementation.
No tests, Windows containment/termination/guard acceptance checks, exit-path
audit or compatibility run were performed. Those remain required evidence.

### Question verdicts for design-specification git-cliff-provisioning round 7

The eighteen questions remain distinct and in scope; none is missing,
redundant or unclear in a way requiring another question. The options describe
meaningful alternatives and consequences. I support each recorded choice:

| Question | Human and reviewer choice | Reason |
| --- | --- | --- |
| Q01 | A | Record the published digest at admission and avoid release-time metadata dependencies. |
| Q02 | A | Frozen records fit the shipped registry model and reviewed admission. |
| Q03 | A | Process identities and short serialization preserve DEAD-only recovery. |
| Q04 | A | Independent version/platform entries and evidence namespaces need not block one another. |
| Q05 | B | The confirmed override supports slow sites; Q18 now defines its complete contract. |
| Q06 | A | One retry and its delay share a finite deadline, including a raised one. |
| Q07 | A | Inherited guards protect the executable through its child's actual lifetime. |
| Q08 | A | Standard proxy resolution fits the agreed network scope. |
| Q09 | B | One invocation object owns environment policy, containment and guard transfer. |
| Q10 | A | A contained Python-launched child preserves streams and status with the existing batch guard. |
| Q11 | A | Status 69 remains conditional on the per-version exit-path audit. |
| Q12 | A | Isolated candidate caching and immutable trust records support offline reuse without admission. |
| Q13 | B | Inputs, output digests, differing hunks and classification retain reproducibility; statuses and the audit remain required. |
| Q14 | A | Fixed object-producing inputs and recorded hashes make regeneration checkable. |
| Q15 | C | Reusable internal logic leaves the public interface to item 6. |
| Q16 | A | A tested alias fragment preserves item 8's exposure responsibility. |
| Q17 | A | Creation-time containment and inherited guards cover parent death, subject to real Windows verification. |
| Q18 | A | Exact seconds with explicit bounds, one validation and independent caller deadlines implement Q05 B without lengthening unrelated stages. |

Q18 B would give coarse relative increments; C would broaden stage scope.
The human chose A, including its ceiling, so neither alternative needs further
definition for this design. There is no outstanding human specification answer
in Q01-Q18. Consolidation remains a separate human workflow choice.

### Convergence evidence for design-specification git-cliff-provisioning round 7

Covered wording:

No additional wording edit is required. Round 6's per-caller wait clarification
and scope clarification are present and preserve the human choices. Keep the
confirmed Q18 record and its full option A contract together until authorized
consolidation incorporates them.

Convergence rationale:

Recommend convergence. The new human decision confirms the fully specified
Q18 A contract without amendment, resolves the sole previously pending choice,
and introduces no conflict with the other decisions, requirement or umbrella.
No further question or substantive revision is needed for the reviewed
formulation. All eighteen specification decisions are explicit.

This recommendation neither authorizes consolidation nor claims implementation
or admission evidence complete. The human convergence gate remains separate.

### Writer instructions for design-specification git-cliff-provisioning round 7

Preserve all eighteen recorded human decisions. No further automated revision
round is requested by this assessment. Present convergence through the existing
human gate; do not infer consolidation permission from reviewer agreement.

When consolidation is separately authorized, integrate Q05 B and Q18 A across
the flow, budget table, resolved worker inputs, diagnostics, acceptance cases
and evidence harness. Preserve default/maximum values, strict rejection even
with a valid cache, unaffected operations, unchanged probe/socket/metadata
limits, retry containment and independent mixed-caller deadlines.

Replace the body's path-return API with Q09 B's invocation object and its
contained guard transfer. Integrate Q13 B's compact evidence bundle while
retaining exit statuses and the source exit-path audit. Retain all specified
real Windows checks, compatibility evidence and admission conditions, and
item 4's ownership of rendering arguments, postprocessing and deadlines.

### Final reviewer decision for design-specification git-cliff-provisioning round 7

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-7 -->

## Round 7 by human - human-confirmation

- Recorded: 2026-11-14T22:30:45+01:00
- Exchange: specification/design-specification/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-7 -->
