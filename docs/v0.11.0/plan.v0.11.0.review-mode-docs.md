# v0.11.0 review-mode documentation implementation plan -- connected independent-review guide

This plan delivers the settled independent review-mode contract as a compact
Diataxis set backed by repository-level acceptance evidence.

- **Discovery and distinction**: connect project entry points to a dedicated
  explanation while preserving the established self-review loop.
- **Executable journeys**: add two tutorials and five bounded how-to guides.
- **Exact lookup and evidence**: add one central reference, inventory links,
  and a versioned acceptance-to-page table.

## Plan goal for v0.11.0 review-mode documentation

Implement the set described by
`docs/v0.11.0/design.v0.11.0.review-mode-docs.md` and its requirement in five
ordered slices.

- **Step 1 goal**: establish discovery, terminology, and authority explanation.
- **Step 2 goal**: deliver two explicitly two-agent first-use tutorials.
- **Step 3 goal**: deliver five task-focused how-to guides.
- **Step 4 goal**: deliver the central contract and inventory links.
- **Step 5 goal**: complete coverage and repository-level acceptance evidence.

## Scope anchors for v0.11.0 review-mode documentation plan

This plan targets three outcomes:

1. A reader can complete either family from opt-in to the human gate.
2. A reader can identify owner, safe action, artifact, and stop condition for
   every observable exchange state.
3. Every claim traces to a shipped instruction, launcher, template, or model
   without copying agent policy into the wiki.

In scope are the pages, entry points, inventories, coverage file, and acceptance
tests named below. Markdown-checker automation, read-only commit-plan inspection,
protocol changes, adapters, and drift automation remain deferred.

## Complexity bound clarification for v0.11.0 documentation

- **O(1) per navigation decision**: explicit links replace repository lookup.
- **O(n) per validation phase**: checks traverse the finite delivered pages,
  declared paths, links, states, and coverage rows once.

No response path gains `O(n^2)` or `O(n log n)` work.

## File-based IO cost clarification for v0.11.0 review-mode documentation

- Normal use reads only the selected page and followed links.
- Documentation adds no metadata loader or directory scan to `pw` or the
  exchange launcher.
- Acceptance checks read each declared page and local target at most once.
- Typed-state and launcher sources are bounded authoring inputs, not a new
  production response path.

## Confirmed technical facts for v0.11.0 plan viability

**Python files above the 650-line repository ceiling**:

- None are modified.

**Python files in the 550-through-650 risk band**:

- `tools/review_exchange_cli.py`: 558 lines, read-only source; no growth.

**Python files below 550 and safe to extend**:

- `tools/review_exchange_models.py`: 486 lines, read-only source.
- `tests/unit/tools/serve_docs/test_serve_docs.py`: 144 lines, unchanged.
- New acceptance `conftest.py`: 0 lines, advisory final below 200.
- New `test_review_mode_docs_acceptance_tdd.py`: 0 lines, advisory final below
  500.

**What does not exist yet**:

- the explanation, tutorials `09` and `10`, five how-to guides, and reference;
- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`;
- `tests/unit/tools/test_review_mode_docs_acceptance/`.

**Other confirmed technical facts**:

- `ArtifactState` supplies fifteen states. Launcher-only `disabled` and
  `fatal` are separate sixteenth and seventeenth user-visible states, from
  the absent-marker branch and the exit-2 fatal payload respectively.
- `_success_payload` supplies seven mandatory fields.
- `.agents` and `.agent` ship the shared wrapper; `.claude` does not.
- Tutorials end at `08`; navigation order is explanation, tutorials, how-to
  guides, then reference.
- `.markdownlint.json` configures rules, but no versioned launcher applies it.

## Current test-tree validation snapshot for v0.11.0 review-mode documentation

- Existing serve-docs tests pin Diataxis order and root-mounted link behavior.
- Review-exchange tests prove protocol behavior; this effort does not duplicate
  lifecycle simulations.
- New acceptance tests inspect real pages, links, the state enum, terminology,
  navigation, and coverage. No PBT is needed for this finite enumerated contract.

## Shared execution command checklist for all v0.11.0 documentation steps

1. Count physical lines of every step file.
2. Add step-owned acceptance assertions before page content.
3. Run `ghog single tests/unit/tools/test_review_mode_docs_acceptance`.
4. Run the step-specific `rg` checks.
5. Run `ghog day` until it reports `exit=0`.
6. Run `git diff --check` and `git diff --cached --check` after staging.
7. Split any Python file over 650 lines; record advisory variance below it.
8. Resolve changed links and paths, then review Markdown with MD024 and MD025
   active.

## Ready-to-run command templates for all v0.11.0 documentation steps

- Line count: `[System.IO.File]::ReadAllLines((Resolve-Path PATH)).Count`
- Targeted tests: `ghog single tests/unit/tools/test_review_mode_docs_acceptance`
- Shared gate: `ghog day`, repeated until `exit=0`
- Whitespace: `git diff --check`; `git diff --cached --check`

No Step 0 performance gate is needed. This work adds no production code or
latency-bearing response path; bounded repository-read assertions belong in the
final acceptance slice without an `xfail`.

## Implementation decisions for v0.11.0 review-mode documentation

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Assess all six inventory candidates and update only pages whose existing subject supports the link. Record every disposition in the coverage table. | Step 4 files, intent, tests, and evidence | Updating all six forces irrelevant links. Updating none loses valid discovery paths. |
| Q02 | Add one bounded repository-local helper that ignores external URLs, resolves relative files, validates fragments against target headings, and checks declared paths. | Step 1 test support and shared acceptance checks | Serve-docs snapshots inspect rewritten copies. Manual-only checks weaken repeatable evidence. |
| Q03 | Pin the explicit 24-value v0.11.0 outcome snapshot and its four source shapes without AST extraction. | Step 4 tests-first contract | AST extraction takes ownership of deferred drift automation. A source note alone cannot prove completeness. |
| Q04 | Create the coverage table with pending rows in Step 1, update it through Steps 2 to 4, and finalize it in Step 5. | All five implementation steps | Final-only reconstruction invites drift. Temporary maps add disposable merge work. |

---

## Numbered steps for v0.11.0 review-mode documentation

### Step 1. Connect discovery and explain independent authority

#### Step 1 -- analysis and intent for discovery and terminology

Issues to address:

- Entry points do not lead to a connected independent review-mode set.
- Existing self-review pages use overlapping review vocabulary.
- No explanation owns the separate authorities and durable-evidence rationale.

Fix intent:

- Add concise entry-point links and one explanation using the generic logo.
- Add comparison-only links to two self-review pages without changing purpose.
- Start acceptance coverage with navigation, logo, terminology, and link checks.

Expected outcome:

- Readers distinguish the self-review loop from independent review mode and
  reach the set in mandated category order.
- Policy summaries cite canonical instructions without copying policy bodies.

Step framing:

- Design links: Explanation and comparison boundary; Entry points and category
  navigation; Visual identity boundary.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 1 -- implementation for discovery and terminology

**Files involved**:

- `README.md` (existing, to be updated).
- `wiki/README.md` (existing, to be updated).
- `wiki/explanation/independent-review-mode-and-human-authority.md` (new, to be created).
- `wiki/explanation/why-the-llm-reviews-its-own-work.md` (existing, to be updated).
- `wiki/how-to/answer-a-review-round.md` (existing, to be updated).
- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` (new, to be created).
- `tests/unit/tools/test_review_mode_docs_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py` (new, to be created).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` (new, to be created).

**Tests first**:

- Assert both entry points link the explanation and preserve Diataxis order.
- Assert independent pages use the generic logo and self-review pages retain
  their review logo and gain comparison links.
- Assert the new explanation cites `review-requestor.md`, `spec-reviewer.md`,
  and `code-reviewer.md`, while the two self-review comparison pages retain
  their existing policy owners and only add the independent-review link.
- Create pending coverage rows for AC01 through AC12 and the six inventory
  candidates, then fill the Step 1 discovery and explanation evidence.

**Classes and behavior**:

- A bounded helper reads only the declared page set, ignores external URLs,
  resolves relative files, validates fragments against target headings, and
  checks named repository paths from the coverage fixture.
- The explanation defines authority and evidence. Old pages remain comparison
  surfaces.
- The coverage table starts as versioned effort evidence and carries pending
  rows forward instead of reconstructing them in Step 5.

**Completion criteria**:

- `ghog day` reports `exit=0`.
- `rg -n independent README.md wiki/README.md wiki/explanation/independent-review-mode-and-human-authority.md` finds the discovery path.
- Focused tests prove navigation, links, logos, and reciprocal comparison.

#### Step 1 -- addendums for discovery and terminology

Line-budget checkpoint:

- Markdown baselines: `README.md` 1037, `wiki/README.md` 197, self-review
  explanation 91, self-review how-to 101. Python ceiling not applicable.
- `conftest.py`: before 0, below-550 safe, ceiling 650, advisory below 180.
- Acceptance test: before 0, below-550 safe, ceiling 650, advisory below 120.

Split guidance:

- Keep link helpers in `conftest.py`. Split tests by category at 550 lines.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_review_mode_docs_acceptance` and
  `ghog day`.

Time-gated status for Step 1:

- No production performance gate is affected.

### Step 2. Teach the two first independent-review journeys

#### Step 2 -- analysis and intent for the tutorial pair

Issues to address:

- No first-use path demonstrates either exchange from opt-in to human gate.
- A single-session presentation would misrepresent actor independence.

Fix intent:

- Append tutorials `09` and `10` without renumbering current pages.
- Use one fictional effort and label requestor and reviewer sessions.
- Cross-link the family divergence and return points.

Expected outcome:

- A user completes either journey and understands that convergence stays
  advisory until the human chooses.

Step framing:

- Design links: First-use tutorial pair and Command and path examples.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 2 -- implementation for the tutorial pair

**Files involved**:

- `wiki/tutorials/09-run-your-first-specification-review.md` (new, to be created).
- `wiki/tutorials/10-run-your-first-implementation-code-review.md` (new, to be created).
- `wiki/README.md` (existing, to be updated).
- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` (existing, to be updated).

**Tests first**:

- Pin numbering, cross-links, two labelled sessions, bounded wait, returned
  answer path, intermediate changes, and exact human choices.
- Pin code-only immutable evidence, validation comparison, step, and commit
  boundary.
- Replace the tutorial-related pending coverage rows with their page and test
  evidence.

**Classes and behavior**:

- Tutorials use skill commands for ordinary flow and repository-relative paths.
- Examples share one fictional effort but remain independently runnable.
- The coverage table retains pending rows for later steps while Step 2 records
  its completed tutorial evidence.

**Completion criteria**:

- `ghog day` reports `exit=0`.
- `rg -n Requestor wiki/tutorials/09-run-your-first-specification-review.md wiki/tutorials/10-run-your-first-implementation-code-review.md` finds labelled sessions.
- Focused tests prove order, cross-links, and family-specific evidence.

#### Step 2 -- addendums for the tutorial pair

Line-budget checkpoint:

- Both tutorials start at 0 lines and are outside the Python ceiling.
- Acceptance test: prior advisory below 120, below-550 safe, ceiling 650,
  advisory post-step below 210.

Split guidance:

- At 550 lines, extract tutorial assertions to a sibling TDD module.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_review_mode_docs_acceptance` and
  `ghog day`.

Time-gated status for Step 2:

- No production performance gate is affected.

### Step 3. Add bounded task guides and human-marked recovery

#### Step 3 -- analysis and intent for task procedures

Issues to address:

- Users lack bounded procedures for opt-in, invocation, artifacts, continuation,
  reclaim, and stopped-state recovery.
- Forced operations must not look like ordinary automated steps.

Fix intent:

- Create the settled five-page how-to topology.
- Put forced operations under `Human decision required` with authority,
  precondition, and evidence effect.
- Prefer skill routes for ordinary work and launchers for direct recovery.

Expected outcome:

- Each operational goal has a short procedure with a clear owner and stop rule.

Step framing:

- Design links: Task-focused how-to set and User contract versus agent policy.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 3 -- implementation for task procedures

**Files involved**:

- `wiki/how-to/enable-independent-review-mode.md` (new, to be created).
- `wiki/how-to/run-specification-review.md` (new, to be created).
- `wiki/how-to/run-implementation-code-review.md` (new, to be created).
- `wiki/how-to/read-independent-review-results-and-continue.md` (new, to be created).
- `wiki/how-to/recover-an-independent-review.md` (new, to be created).
- `wiki/README.md` (existing, to be updated).
- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` (existing, to be updated).

**Tests first**:

- Assert five pages cover all seven goals without mixing Diataxis purposes.
- Assert recovery separates ordinary reclaim from stopped-state operations.
- Assert forced commands sit below the human-decision heading and name
  authority, precondition, and evidence effect.
- Replace the how-to and recovery pending coverage rows with their page and
  test evidence.

**Classes and behavior**:

- Procedures follow final JSON `paths` and never reconstruct filenames or edit
  artifacts.
- Results distinguish exits `0`, `3`, and `2`; owning authorization controls
  continuation.
- The coverage table records completed task-guide evidence without finalizing
  the reference and release-gate rows.

**Completion criteria**:

- `ghog day` reports `exit=0`.
- `rg -n Human wiki/how-to/recover-an-independent-review.md` finds the marked
  authority boundary.
- Focused tests prove task assignment, forced-operation marking, and stops.

#### Step 3 -- addendums for task procedures

Line-budget checkpoint:

- Five guides start at 0 lines and are outside the Python ceiling.
- Acceptance test: prior advisory below 210, below-550 safe, ceiling 650,
  advisory post-step below 320.

Split guidance:

- Extract how-to assertions to a sibling TDD module at 550 lines.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_review_mode_docs_acceptance` and
  `ghog day`.

Time-gated status for Step 3:

- No production performance gate is affected.

### Step 4. Publish the exact contract and focused inventories

#### Step 4 -- analysis and intent for lookup and inventory

Issues to address:

- No central page defines marker, identity, artifacts, states, operations,
  outcomes, exits, adapters, and policy ownership together.
- Inventory pages do not lead from their subjects to that contract.

Fix intent:

- Build one reference from shipped sources with fifteen enum states plus
  `disabled` and `fatal`, seven mandatory result fields, and the asymmetric
  adapters.
- Assess all six candidate inventory pages, add links only where the existing
  subject supports one, and record every disposition.
- Record the inline-string origin and drift risk of operation outcomes.

Expected outcome:

- Readers gain one exact lookup while inventories stay focused and canonical
  instructions remain policy owners.

Step framing:

- Design links: Central reference contract, Authority and content reuse, and
  Versioned acceptance-to-page table.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 4 -- implementation for lookup and inventory

**Files involved**:

- `wiki/reference/independent-review-mode-contract.md` (new, to be created).
- `wiki/README.md` (existing, to be updated).
- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` (existing, to be updated).

**Candidate inventory paths**:

- `wiki/reference/skills-catalog.md` (existing, to be assessed).
- `wiki/reference/artifact-files.md` (existing, to be assessed).
- `wiki/reference/aliases-and-launchers.md` (existing, to be assessed).
- `wiki/reference/templates.md` (existing, to be assessed).
- `wiki/reference/automation-and-direct-invocation.md` (existing, to be assessed).
- `wiki/reference/repository-layout.md` (existing, to be assessed).

**Tests first**:

- Derive fifteen state names from `ArtifactState`, add the launcher-only
  `disabled` and `fatal` states, and assert seventeen reference rows with
  owner and next action.
- Pin `fatal` to the exit-2 payload shape: null `identity`, empty `paths`,
  null round, `fatal-input` outcome, caller ownership, and a next action to
  correct the input and re-run instead of opening an artifact.
- Pin seven result fields, exits, human choices, artifacts, and path authority.
- Pin this reviewed v0.11.0 outcome snapshot:
  `disabled`, `activated`, `observed`, `started`, `continued`,
  `reclaimed`, `force-reclaimed`, `completed`, `force-completed`,
  `published`, `repaired`, `found`, `timed-out`, `abandoned`,
  `escalated`, `inconsistent`, `repair-required`, `consumed`,
  `cancelled`, `archived`, `resolved`, `another-round`,
  `continue-owning-workflow`, and `fatal-input`.
- Record that the snapshot comes from plain and conditional `OperationResult`
  construction in `review_exchange_cli.py`, all `WaitOutcome` values, both
  `ConfirmationOutcome` values, and the CLI fatal payload. Future launcher
  changes must update this explicit snapshot deliberately without AST
  extraction.
- Pin every host row, wrapper or `absent`, prefix, delegation, and inventory
  link without copied policy tables.
- Assert the coverage table records a disposition for every candidate inventory
  path, including candidates that do not receive a link.

**Classes and behavior**:

- The reference groups `disabled` and `idle` as not-yet-started, assigns
  `fatal` to an invalid-input or refused-operation group, and preserves one row
  per typed state.
- The consolidated design calls `disabled` the sixteenth state and therefore
  undercounts the shipped fatal payload. Step 4 treats seventeen rows as the
  corrected source-derived enumeration, not as implementation drift.
- Subject-matched inventories add narrow discovery entries; unrelated
  candidates remain unchanged. The central page owns the contract.
- The coverage table replaces the reference and inventory pending rows with
  exact page, test, or no-change disposition evidence.

**Completion criteria**:

- `ghog day` reports `exit=0`.
- `rg -n disabled wiki/reference/independent-review-mode-contract.md` finds
  the launcher-only row.
- `rg -n fatal wiki/reference/independent-review-mode-contract.md` finds the
  exit-2 row and its null identity, empty paths, null round, and retry action.
- Focused tests prove state, payload, adapter, artifact, outcome, and inventory
  coverage against shipped sources.

#### Step 4 -- addendums for lookup and inventory

Line-budget checkpoint:

- Inventory Markdown baselines: skills 95, artifacts 148, aliases 89, templates
  98, automation 62, repository layout 102. Python ceiling not applicable.
- `review_exchange_cli.py`: 558, risk band, read-only and no growth.
- `review_exchange_models.py`: 486, below-550 safe, read-only.
- Acceptance test: prior advisory below 320, below-550 safe, ceiling 650,
  advisory post-step below 420.

Split guidance:

- Any CLI edit is out of scope. Split reference tests at the 550-line risk band.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_review_mode_docs_acceptance` and
  `ghog day`.

Time-gated status for Step 4:

- No production performance gate is affected.

### Step 5. Close coverage and acceptance evidence

#### Step 5 -- analysis and intent for release evidence

Issues to address:

- Criteria 1 through 9 need page mappings while 10 through 12 need validation
  or scope evidence.
- Inventory dispositions and link integrity need one auditable record.

Fix intent:

- Finalize every pending row in the versioned coverage table outside the wiki.
- Complete repository-level acceptance tests across the connected set.
- Run project, focused, whitespace, link, path, and manual Markdown checks.

Expected outcome:

- Every criterion and candidate inventory has reviewable evidence without a new
  Markdown launcher.

Step framing:

- Design links: Versioned acceptance-to-page table and Acceptance cases.
- Execution checklist: Shared execution command checklist in this plan.

#### Step 5 -- implementation for release evidence

**Files involved**:

- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py` (existing, to be updated).

**Tests first**:

- Add acceptance cases for discovery, topology, local links, named paths, stable
  terms, logos, authority links, states, gates, and inventory dispositions.
- Assert criteria 1 through 9 map to pages and 10 through 12 are evidence rows.
- Assert no row cites an ignored helper or nonexistent Markdown launcher.
- Assert no pending row remains and every earlier step evidence entry is
  retained.
- No PBT is needed because criteria, states, pages, and candidates are closed
  enumerations.

**Classes and behavior**:

- Fixtures read only declared pages and source paths and report exact failures.
- The incrementally maintained coverage file is finalized as evidence
  documentation, not another Diataxis purpose.

**Completion criteria**:

- `ghog day` reports `exit=0`.
- `git diff --check` and `git diff --cached --check` return no diagnostics.
- `rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` begins a
  complete AC01 through AC12 evidence table.
- All changed links and paths resolve. Manual review finds no MD024 or MD025
  defect.

#### Step 5 -- addendums for release evidence

Line-budget checkpoint:

- Coverage Markdown has its Step 4 baseline measured before finalization and is
  outside the Python ceiling.
- `conftest.py`: prior advisory below 180, below-550 safe, ceiling 650,
  advisory final below 200.
- Acceptance test: prior advisory below 420, below-550 safe, ceiling 650,
  advisory final below 500.

Split guidance:

- At 550 lines, extract category assertions to a sibling TDD module. No Python
  file may exceed 650.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_review_mode_docs_acceptance`, `ghog day`,
  and both Git whitespace checks after staging.

Time-gated status for Step 5:

- Final repository-level acceptance covers the connected documentation set and
  adds no production timeout or `xfail`.
