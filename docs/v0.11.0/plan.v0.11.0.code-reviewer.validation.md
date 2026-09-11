# v0.11.0 code-reviewer implementation tracking and validation

Yes, it is implemented.

All six responder slices are implemented and validated through the project gate, focused boundary tests, and temporary-repository acceptance journeys.

---

## File-based IO cost clarification for v0.11.0 code-reviewer implementation

- Resolve review artifacts and retained evidence from exact identity-derived paths.
- Read explicit request, plan, manifest, and answer inputs once per owning phase.
- Compare Git state only for the staged set and named repair or validation paths.
- Write paired outputs and the stable ignored manifest through their atomic boundaries.

---

## Complexity bound for v0.11.0 code-reviewer implementation

- Path derivation remains O(1) per round.
- Assessment remains O(n) over explicit staged paths, repair paths, commands, and commit groups.
- No implementation step may add directory enumeration for artifact selection.
- Every step's performance check must confirm the absence of a repository-wide nested comparison.

---

## Step 1. Publish immutable request evidence

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The requestor now captures the exact Git index tree, resolves the mandatory
default-plus-addition validation set with source attribution, and renders both
values from one typed evidence object in the paired request artifacts. Focused
checks and the final post-review Groundhog walk pass with 1,707 tests, 100%
coverage, and no duration outliers or exclusion regressions.

### Goal for Step 1

Publish the request-time Git index tree and the resolved validation set with sources through the existing paired code-review request renderer.

### Step 1 improvement expectations

- Project defaults cannot be removed by plan or request additions.
- Request and transcript summary identify the same tree and validation set.
- Existing requestor publication behavior remains intact.

### What was implemented for Step 1

- Added `capture_index_tree` as the single capture-only Git index-tree helper.
- Added deterministic, additive validation resolution that preserves project
  defaults and merges project, plan, and request source labels.
- Extended `CodeReviewRoundInput` and its CLI boundary with mandatory request
  evidence, repeatable additive validation flags, and publication-time capture.
- Added one canonical fenced JSON object under `## Code review evidence` and a
  human-readable transcript section derived from the same typed evidence.
- Updated the canonical requestor instruction and template without changing the
  shared exchange envelope or paired publication lifecycle.
- Added real temporary-repository, resolver, renderer, instruction, IO, and
  requestor acceptance coverage for the completed surface.

### New types or classes introduced for Step 1

- `ResolvedValidationCommand`: one immutable command with ordered source labels.
- `ResolvedValidationSet`: one immutable, unique, deterministically ordered set
  of mandatory commands.
- `_CodeReviewEvidence`: the renderer-internal typed source for canonical JSON
  and its paired human-readable summary.

### Architecture check for Step 1

The capture-only Git adapter delegates subprocess portability to the existing
Git command helper. Validation resolution remains side-effect free, while the
request renderer composes those two boundaries and retains exchange-envelope
ownership in the existing shared model. Dependencies point from the request
adapter toward focused evidence and validation modules; no business-only layer
imports a new technical concern, and no DDD-Hexagonal boundary is inverted.

No architecture smell or violation needs to be addressed.

### Performance check for Step 1

Index capture delegates one `git write-tree` operation. Validation resolution is
O(n) over explicit command inputs with insertion-ordered dictionary lookup, and
rendering is O(n) over the resolved commands. No directory enumeration,
repository-wide nested comparison, O(n log n), or O(n^2) computation was added.
The real-Git tests moved process setup outside measured calls and the final full
suite reported zero duration outliers.

No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The dedicated `test_code_review_evidence` and `test_code_review_validation`
leaves exercise every branch in the two new production modules. The existing
request renderer, requestor instruction, and requestor acceptance leaves cover
mandatory evidence validation, canonical dual-JSON rendering, envelope
round-trip behavior, source summaries, publication-time capture, additive CLI
inputs, read-once IO, and unchanged exchange transitions. The final Groundhog
walk reports 100% project coverage across 1,707 passing tests.

No unit-tested class or module is below 100% coverage or needs completing.

### Feature integrity for Step 1

Existing request identity, staged-repair policy, optional human guidance,
caller-owned ignored-file validation, exact-path access, paired output, and
shared envelope parsing remain covered. Requests now fail closed when tree or
validation evidence is absent or malformed, while both evidence headings
round-trip without changing shared exchange mechanics. No existing reporting
or requestor capability is impaired.

---

## Step 2. Add executable Git evidence and commit validation

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

The executable evidence types, CLI, launcher, manifest lifecycle, and shared
commit-plan validator are present and covered. Validation-state capture is now
bounded to caller-supplied paths, every CLI file operand stays inside the
selected repository, retained payloads fail closed on malformed relationships,
and manifest identities are restricted to the fixed `code/code` family and
type.

### Goal for Step 2

Provide machine-checkable snapshots, repair attribution, umbrella and validation-state comparisons, stable retained evidence, and shared `a.commit` validation through public typed boundaries.

### Step 2 improvement expectations

- Reviewer patches exclude pre-existing writer hunks.
- Batch execution and review use one commit-plan validator.
- The evidence CLI captures and compares umbrella digests and validation state, and owns manifest write/read/retire operations.

### What was implemented for Step 2

- **Repair attribution**: `RecordedBlob` records pre-repair Git objects for
  existing and untracked files, identifies writer-deleted files, and
  `attribute_reviewer_patch` produces reviewer-only text patches without
  rewriting the index.
- **Executable comparisons**: umbrella digest and validation-state value
  objects expose capture and comparison operations, including explicit
  not-applicable umbrella evidence and ignored-versus-tracked validation
  differences.
- **Retained evidence**: `CodeReviewEvidence` serializes baseline and assessed
  index trees, repair evidence, and validation states; stable manifest helpers
  write, read, identity-check, and retire the ignored JSON artifact.
- **Public adapter**: `CodeReviewEvidenceCli` exposes every planned operation
  without prompts, and `bin/code_review_evidence.bat --help` succeeds from the
  repository root without environment setup.
- **Commit validation**: `validate_commit_plan` checks conventional subjects,
  safe one-path `git add` commands, duplicate membership, missing paths, and
  exact staged membership while preserving group order. The root batch
  workflow calls this public validator before changing the index.
- **Validation evidence**: the completion grep finds the planned executable
  symbols, focused tests cover the implemented models and adapters, and the
  latest Groundhog cycle completed 1,748 tests in 1 minute 23.8 seconds with
  100% coverage, zero failures, zero outliers, and a slowest call of 0.42
  seconds against the 0.50-second ceiling.
- **Bounded validation capture**: callers pass the exact validation paths; Git
  receives literal pathspecs only for those paths, unrelated repository files
  are neither enumerated nor hashed, and comparisons require the same ordered
  path set.
- **Defensive evidence boundary**: repository file operands reject absolute,
  root, and parent-traversal paths; payload parsing validates digest shapes,
  applicability pairs, unique safe paths, state membership, and fixed manifest
  identity before evidence is written or used.

### New types or classes introduced for Step 2

- `RecordedBlob` and `RepairAttribution`: immutable pre-repair content and
  reviewer-only patch evidence.
- `UmbrellaDigest` and `UmbrellaComparison`: optional protected-document
  identity and comparison results.
- `FileDigest`, `ValidationState`, and `ValidationStateComparison`: repository
  content snapshots and classified validation side effects, implemented in the
  focused `code_review_evidence_validation_state.py` module and re-exported by
  the public evidence boundary.
- `CodeReviewEvidence`: versioned retained evidence for one exchange identity
  and implementation step.
- `CodeReviewEvidenceCli`: non-interactive typed dispatcher for evidence
  capture, comparison, and manifest lifecycle operations.
- `CommitPlanGroup` and `CommitPlanValidation`: ordered public results for the
  side-effect-free batch-plan validator.

### Architecture check for Step 2

The evidence domain records immutable shared values in
`code_review_evidence.py`, delegates validation snapshots and comparisons to
`code_review_evidence_validation_state.py`, and shares digest, containment, and
Git error handling through `code_review_evidence_common.py`. Argument and
repository path validation remain in `code_review_evidence_cli.py`, while the
batch workflow depends on the pure public validator in
`git_batch_commit_validation.py`. These dependency directions are sound, the
compatibility exports are explicit, and the changed evidence files remain
below the 650-line ceiling: 479, 105, 248, and 202 physical lines for the
evidence hub, common boundary, validation-state module, and CLI respectively.

No architecture issues need to be addressed for Step 2.

### Performance check for Step 2

Blob recording and repair attribution use constant Git operations per named
path. Commit-plan validation is linear over explicit groups and paths, apart
from bounded diagnostic ordering. Manifest lifecycle reads or writes one
identity-derived file. Validation-state capture preserves caller order and
performs O(n) work over only the explicit staged, repair, and validation
artifact paths, using literal Git pathspecs and no repository-wide enumeration
or sorting.

No performance issue needs to be addressed for Step 2.

### Unit test coverage check for Step 2

The dedicated evidence, evidence-CLI, commit-validation, root-workflow, and
batch-process tests reach every production branch. They cover existing files,
created files, writer deletions, patch attribution, umbrella changes,
ignored-versus-tracked effects, bounded literal-path capture, unrelated-file
exclusion, repository path escapes, malformed digest and path relationships,
duplicate and inconsistent validation payloads, fixed manifest identity,
manifest lifecycle, conventional subjects, membership mismatches, unsafe `git
add` paths, and shared-validator wiring. The latest full run reports 100%
project coverage across 1,748 passing tests.

The evidence tests are split by responsibility: core capture and lifecycle
contracts occupy 221 lines, while defensive payload, path, and Git boundary
contracts occupy 456 lines. Both remain below the plan's 550-line split
threshold. One explicit boundary contract opts out of the package's autouse
in-memory Git fixture and records real `git ls-files` output for tracked,
ignored, and untracked bracketed names, proving that each `:(literal)` pathspec
excludes its glob-matching decoy.

No unit-tested class is below 100% coverage for Step 2.

### Feature integrity for Step 2

The root batch workflow rejects an inaccurate `a.commit` before reset or
commit, and the approved earlier Step 2 batch commits demonstrated that shared
path in practice. Request rendering still reads authored inputs before
capturing the index, existing Step 1 request evidence remains intact, and the
new validation-state split preserves the complete public import surface.

The protocol-owned transcript now contains the Step 2 round-one through
round-three requests and answers, the timeout escalation, and the authorized
forced-reclaim entry. The round-two and round-three lease reclaims appended
nothing, because an ordinary reclaim renews the lease without touching request,
answer, or transcript bytes. Historical Step 1 bytes and the duplicate human
headings remain untouched. The transcript is restored to the trailing
documentation group so the complete Step 2 review record lands with the step,
while later protocol appends remain eligible through that group's exact-path
staging command.

Existing behavior is not impaired, and Step 2 is ready for round-four reviewer
assessment after the accepted repairs passed the project gate.

---

## Step 3. Enforce reviewer-mode implementation checks

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The canonical implementation check now has an explicit advisory reviewer mode
that delegates repository evidence to the Step 2 launcher, applies the same
post-criteria comparisons after Yes and No results, restricts writes to the
reviewed step's validation rows, and suppresses umbrella completion.

### Goal for Step 3

Bound advisory implementation checks to reviewed-step validation rows and require executable umbrella and validation-state comparisons on both criteria outcomes.

### Step 3 improvement expectations

- Reviewer mode never marks an umbrella row completed.
- Pass and fail paths both call the evidence boundary by named operation.
- `Umbrella draft: none` records digest comparison as not applicable.

### What was implemented for Step 3

- Added an explicit reviewer assessment branch while leaving writer-owned
  implementation-check behavior unchanged outside that mode.
- Defined `validation_path_set` as the first-seen ordered union of every staged
  reviewed-step path, the validation plan, and known validation artifacts.
- Required `umbrella-digest` and `validation-state` capture before criteria and
  comparison after both Yes and No results.
- Required pre-repair blob capture, patch attribution, retained-manifest
  writing and resumption, and publication-bound manifest retirement.
- Limited reviewer writes to the exact reviewed-step validation rows and made
  any umbrella or other tracked difference a retained `changes-requested`
  finding.
- Added five focused instruction structure tests for setup, both result paths,
  scope completeness, permission boundaries, and absent-umbrella evidence.

### New types or classes introduced for Step 3

No production type or class was introduced. The new test package contains two
small file-reading helpers that isolate canonical section assertions without
implementing a second evidence engine.

### Architecture check for Step 3

The canonical instruction remains the reviewer policy adapter and delegates all
Git, digest, filesystem, patch, and manifest behavior to
`bin/code_review_evidence.bat`. The structure tests validate that delegation
without importing production internals or duplicating Step 2 algorithms. The
writer-owned document and umbrella completion flow remains outside the reviewer
branch.

No architecture issue needs to be addressed for Step 3.

### Performance check for Step 3

Reviewer scope construction uses a first-seen ordered union and therefore
performs O(n) work over explicit paths. Each evidence operation receives that
bounded set; the instruction adds no directory scan, sort, nested comparison,
wait, or repeated repository walk.

No performance issue needs to be addressed for Step 3.

### Unit test coverage check for Step 3

The 97-line reviewer-mode test module covers every Step 3 instruction contract:
baseline evidence and manifest lifecycle, symmetric Yes and No comparisons,
the staged-plus-artifact minimum scope, reviewed-row write limits, changed-file
retention, patch attribution, and `Umbrella draft: none`. Step 2's existing
temporary-repository tests remain the executable proof for the delegated
commands. The completed implementation walk ran 1,771 tests with 100% project
coverage, zero outliers, and a slowest call of 0.38 seconds.

No unit-tested class is below 100% coverage for Step 3.

### Feature integrity for Step 3

Outside reviewer assessment mode, the original validation-plan status rules,
document-level completion check, umbrella completion, and workflow handoff are
unchanged. Inside reviewer mode, a changed umbrella or other tracked side
effect is reported and left in place instead of being staged or reverted, and
ignored validation artifacts remain acceptable. The absent-umbrella path keeps
typed not-applicable evidence without inventing a file operand.

Existing behavior and reporting remain intact for Step 3.

---

## Step 4. Build paired code-review answers

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

The implementation supplies both discriminated answer shapes, renders the durable answer and substantive transcript summary from one immutable source, and keeps the reviewer decision advisory. The assessment path validates the exact live retained manifest and assessed index tree without retiring the manifest; the early-rejection path rejects assessment-only evidence before rendering.

### Goal for Step 4

Render separately validated early-rejection and assessment answers plus their paired substantive transcript summaries.

### Step 4 improvement expectations

- Assessment-derived fields are prohibited in early rejection.
- Paired outputs share one exact identity and finding source.
- CLI IO failures do not leave a partial accepted pair.

### What was implemented for Step 4

- Added `tools/code_review_answer.py` with immutable early-rejection and full-assessment inputs, readiness-floor enforcement, explicit exchange-occurrence heading discrimination, shared-envelope composition, and paired answer/transcript rendering.
- Added `tools/code_review_answer_cli.py` with explicit ignored-root `a.*` inputs, prohibited-mixture and mandatory-field checks, strict single UTF-8 reads, exact manifest/index validation, distinct-path enforcement, and rollback-safe atomic pair publication.
- Added `templates/code-review-answer.template.md` and the repository-root `bin/code_review_answer.bat` launcher. Rendering deliberately leaves manifest retirement to the later publication workflow.
- Added separate model and CLI test modules covering both valid variants, guidance pairing, advisory decisions, failure boundaries, manifest drift, ignored-path validation, single reads, and partial-write cleanup.

### New types or classes introduced for Step 4

- `EarlyRejectionAssessment`: the narrow pre-assessment disagreement and writer-instruction shape.
- `ImplementationAssessment`: the complete evidence, repair, validation, drift, readiness, and decision shape.
- `CodeReviewAnswerRender`: the non-empty answer-content and transcript-summary pair.

### Architecture check for Step 4

Rendering and typed model validation remain in `tools/code_review_answer.py` at 470 physical lines, while filesystem, Git, manifest, and CLI validation remain in `tools/code_review_answer_cli.py` at 395 lines. The model and CLI tests remain separate at 315 and 470 lines. Every file is below the plan's 550-line safe threshold and 650-line ceiling; no split is required. Both production modules exceed their advisory estimate of below 380 lines, by 90 and 15 lines respectively; the shared checklist records that variance without failing a file at or below 650 lines. The shared envelope and Step 2 evidence APIs are composed rather than forked, and the launcher contains no policy.

### Performance check for Step 4

The deterministic local implementation adds no timeout gate. The final `ghog day` full phase completed 1,813 tests in 2m 25.9s with the slowest call at 0.47s, zero duration outliers, and exit 0. Exact caller paths and linear inventories bound the renderer's work without directory enumeration.

### Unit test coverage check for Step 4

`ghog single tests/unit/tools/test_code_review_answer` passed before the final walk. The final `ghog day` reported `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` across 1,813 tests. Coverage includes invalid families and roots, non-tuple and mismatched inventories, restarted-exchange heading discrimination, parser and ignored-path failures, live-manifest/index drift, failed temporary output, and restoration of both existing and previously absent paired outputs.

### Feature integrity for Step 4

Step 4 preserves the feature's authority boundary: `commit-ready` is rendered only as an advisory convergence recommendation, `changes-requested` carries concrete writer instructions, and neither result commits, consumes, confirms, completes, or retires protocol evidence. Every authored answer and transcript heading includes the caller-supplied positive exchange occurrence, so a restarted step-round remains unique without transcript scanning. The completion grep finds both typed variants and paired fields, and `bin/code_review_answer.bat --help` succeeds from the repository root without prior environment setup.

---

## Step 5. Route and instruct the independent reviewer

### Analysis of Step 5 implementation state

Yes. Step 5 has been fully implemented.

### Goal for Step 5

Route only an exact pending code request to the advisory reviewer and expose the same bounded workflow through every supported host adapter.

### Step 5 improvement expectations

- Ordinary and forced routing agree on actor and identity.
- `CodeReviewRoute.actor` is resolved once and cannot disagree with the classified state.
- Pending requests and their intact abandoned form are reviewer-owned; every writer-owned or stopped state remains requestor-owned.
- Canonical prose forbids owner, escalation, and commit operations.

### What was implemented for Step 5

- `tools/prompt_workflow_code_review.py` now resolves one typed `CodeReviewActor` from the classified state, assigns both active and reclaimable requests to the reviewer, rejects an actor/state mismatch at `CodeReviewRoute` construction, and renders the route's resolved reviewer or requestor role without a second state partition.
- `tools/prompt_workflow_skill.py` routes exact `request-pending` and `abandoned-request` code exchanges to `code-reviewer`, retains every other state in `code-review-requestor`, and applies the same ownership rule to forced roles.
- `instructions/code-reviewer.md` defines the fixed code-family policy and one bounded reviewer sequence, including one cold or in-session reclaim of an intact abandoned request, while delegating evidence, paired rendering, and protocol mutation to `bin/code_review_evidence.bat`, `bin/code_review_answer.bat`, and `bin/review_exchange.bat`.
- `docs/v0.11.0/design.v0.11.0.code-reviewer.md` and the Step 5 plan text record the human-directed amendment: pending and intact abandoned requests stay with one reviewer actor because both retain the reviewer-owned request artifact.
- The `.agent`, `.agents`, and `.claude` adapters link directly to the canonical root instruction and contain no copied reviewer or exchange policy.
- The Step 4 follow-up is closed by exposing `exchange_occurrence` in exact `request-pending` status output and deriving the generated answer occurrence from the current request entry; `tools/review_exchange_transcript_identity.py` keeps that identity rule out of the already large store and publication modules.

### New types or classes introduced for Step 5

- `CodeReviewActor`: the typed `REVIEWER` or `REQUESTOR` owner resolved once from the classified artifact state.
- `CodeReviewRoute.actor`: a required immutable field whose post-init validation rejects any owner that disagrees with the route state.
- `transcript_entry_base(...)` and `current_request_occurrence(...)`: small shared functions that keep request, answer, status, and restarted-exchange headings on one step-scoped identity contract.

### Architecture check for Step 5

The implementation preserves the existing exact-path observer and shared exchange state machine. Routing adds no artifact scan; `ArtifactState.REQUEST_PENDING` and `ArtifactState.ABANDONED_REQUEST` map to the reviewer because both shapes retain the reviewer-owned request artifact. Forced routing reuses the same resolved route, and the canonical reviewer instruction performs one guarded reclaim before continuing. The human-directed design and Step 5 plan amendment now state the same single-partition rule. Canonical policy remains in `instructions/code-reviewer.md`; all provider files are metadata-plus-redirect adapters under `rules/llm-specific-adapters.md`.

Line budgets remain below the 650-line ceiling: `tools/prompt_workflow_code_review.py` is 277 lines, `tools/prompt_workflow_skill.py` is 640, and the existing route test is 434. The dispatcher is 40 lines above the 600-line advisory estimate and 10 lines below the hard ceiling; static complexity passes after review-role forcing was extracted into its own dispatcher. The canonical instruction is 190 lines, and the instruction, skill-route, adapter, and transcript-identity test modules are 104, 181, 65, and 46 lines respectively.

### Performance check for Step 5

No polling or timeout loop was added. State classification and actor resolution are constant-time over one exact context, and the exchange occurrence reads only the one exact transcript already named by that context. The post-repair round-two `ghog day --force` completed the 1,846-test full phase in 1m 45.8s with zero duration outliers; the slowest call was 0.28s.

### Unit test coverage check for Step 5

The new and updated tests cover reviewer ownership for `request-pending` and its intact `abandoned-request` recovery form, requestor ownership for every writer-owned or stopped state, actor/state construction rejection, ordinary and forced Codex/Claude rendering with the exact plan step, absent forced reviewer routes, forced cold abandoned-request acceptance through `test_forced_reviewer_accepts_a_cold_abandoned_request`, and exact forced requestor routing. Instruction tests pin fixed policy, exact request reads, one bounded wait, early rejection, repair attribution, validation side effects, retained-manifest recovery, both successful publication exits, forbidden authority, and launcher-only executable boundaries. Adapter tests prove every host links directly to the canonical instruction and copies no policy. The restarted request/answer regression and status payload test pin `exchange_occurrence` without reviewer transcript discovery.

The focused 93-test Step 5 slice passed before the full walk. Final `ghog day` reported `fail=0 warn=0 xfail=0 cov=100 outliers=0 exit=0` across 1,846 tests. The routing completion grep returned 10 matches, the launcher-boundary grep returned 15 matches, and the mandatory `git diff --cached --check` command returned no diagnostics after the round-one EOF repair.

### Feature integrity for Step 5

Step 5 preserves the feature's advisory boundary. The reviewer may wait, assess, make bounded attributable repairs, render, and publish, but the canonical instruction explicitly forbids answer consumption, continuation, confirmation, completion, escalation, cancellation, resolution, archival, and commits. It reads the exact request path returned by the protocol, never the transcript as working context, and retires retained evidence on the published outcome for both exit `0` and convergence exit `3`. An intact abandoned request remains reviewer-owned for one guarded reclaim, while every writer-owned, human-owned, escalation, and repair-required state remains requestor-owned.

---

## Step 6. Prove responder acceptance and recovery

### Analysis of Step 6 implementation state

Yes. Step 6 has been fully implemented.

The new acceptance package composes the completed request, evidence, answer, routing, exchange, recovery, and authority surfaces over real temporary Git repositories. Its named scenarios cover all sixteen design cases and map the feature request's eight acceptance criteria to executable tests.

### Goal for Step 6

Prove all requirement and design acceptance cases through real staged-state, exchange, publication, and recovery behavior.

### Step 6 improvement expectations

- Both answer shapes reach the correct durable exchange state.
- Request, evidence, and answer launchers each have one public-seam smoke test.
- Repair, drift, validation side effects, guidance, and reclaim preserve ownership boundaries.
- Commit-ready remains advisory and exit-3 publication retires retained evidence.

### What was implemented for Step 6

- `tests/unit/tools/test_code_reviewer_acceptance/fixtures.py` creates exact Step 6 plans, validation plans, staged files, contexts, paired renderer inputs, and shared exchange cores in real temporary Git repositories.
- `test_code_reviewer_acceptance_tdd.py` proves exact pending routing, early rejection, live-index drift, safe and unsafe repair attribution, reviewed validation-row updates, umbrella protection, mandatory-gate failure, and advisory convergence.
- `test_code_reviewer_recovery_tdd.py` proves the repeated-evidence no-progress bound, literal human-guidance handling, retained assessed-tree manifests, interrupted answer-publication replay, and manifest retirement after convergence publication returns exit 3.
- `test_code_reviewer_io_acceptance_tdd.py` proves ignored and tracked validation-side-effect classification, literal Git pathspec behavior, side-effect-free commit-plan validation, and the reviewer authority boundary.
- `test_code_reviewer_launcher_smoke_tdd.py` starts the request, evidence, and answer launchers once each and verifies that every adapter reaches its public argument parser.
- Round-2 acceptance feedback exposed and corrected one permitted earlier-step defect: cold `abandoned-request` routing now keeps the request reviewer-owned, and the canonical reviewer reclaims it once before continuing.

### New types or classes introduced for Step 6

- `Effort`: a test-local immutable bundle containing the exact repository root, workflow topic and state, memory record, review context, plan, validation plan, umbrella, and staged source used by acceptance journeys.

### Architecture check for Step 6

Step 6 primarily adds acceptance tests and uses its explicit earlier-production-file allowance for one acceptance defect in the Step 5 route and canonical instruction. The correction assigns the existing `ABANDONED_REQUEST` state to the reviewer that already owns its intact request artifact and delegates the existing reclaim transition; it introduces no production dependency or new state transition. The fixtures call the public request and answer renderers, evidence functions, `ReviewExchangeCore`, routing boundary, and shared commit-plan validator. Reusable repository construction stays in the planned fixture module, while assessment, recovery, IO, and launcher responsibilities remain split across focused modules. Each scenario names explicit paths and keeps Git work linear over its bounded path set.

There is no architecture smell, violation, oversized file, or other issue that needs to be addressed.

### Performance check for Step 6

The 31-test focused acceptance package passed before the full walk. Repository and launcher setup runs in pytest fixture setup so each measured call remains small. Final post-fix `ghog day` completed 1,877 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`; the full phase took 2m 54.2s and its slowest call took 0.46s, below the 0.5-second per-call ceiling.

There is no performance issue that needs to be addressed.

### Unit test coverage check for Step 6

Step 6 changes no production class file, so it creates no new class-specific unit-test target. The acceptance tests exercise the existing public surfaces as composed behavior and the full project gate remains at 100% coverage.

There is no unit-tested class below 100% that needs completing.

### Feature integrity for Step 6

All sixteen design acceptance cases have a named test: exact routing; undefined-step, identity, missing-tree, and index-drift rejection; bounded repair and overlap refusal; validation-row and umbrella boundaries; mandatory-gate failure; ignored and tracked validation effects; repeated missing evidence; advisory convergence; human guidance; stopped-round manifests; and interrupted publication replay. A separate parametrized mapping imports the named module and function for acceptance criteria 1 through 8 and requires the matching criterion marker on each executable journey; removing the AC08 marker made that exact mapping case fail before restoration. Launcher smoke covers all three new adapters, the cold-routing tests keep reclaimable requests reviewer-owned through ordinary and forced entry, and the authority test confirms the reviewer can publish but cannot consume, continue, confirm, complete, escalate, cancel, commit, or complete the umbrella. The human-directed design amendment and Step 5 plan now agree with that behavior, and the Step 6 completion criterion names the journeys' durable-state, published-outcome, and exit-3 assertions directly instead of treating a partial text search as proof.
