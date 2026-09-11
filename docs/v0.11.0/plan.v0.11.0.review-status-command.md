# v0.11.0 review-status-command implementation plan -- durable state diagnosis

Implement one read-only status pipeline over the existing review-exchange
protocol, with a typed result shared by human and JSON output.

- **Typed status records**: represent healthy exchanges and damaged candidates
  without guessing missing identity.
- **Bounded discovery**: scan the reserved coordination prefix once and reuse
  the existing observer and canonical path derivation.
- **One command surface**: expose the same result through the root launcher,
  direct Python entry point, and final acceptance suite.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); when a snippet starts or ends with a space, write that space as the
> literal token `[space]`, as in `` `[space]${x}` ``. End any line that would be
> only italic text with a period after the closing underscore (MD036).

## Plan goal for v0.11.0 review status

Implement the full v0.11.0 review-status command described by
`docs/v0.11.0/feature-request.v0.11.0.review-status-command.md` and
`docs/v0.11.0/design.v0.11.0.review-status-command.md` in four ordered slices.

- **Step 1 goal**: define the strict machine result and its closed vocabularies.
- **Step 2 goal**: discover, validate, observe, normalize, and order every active
  coordination candidate without mutation.
- **Step 3 goal**: render one result for humans and machines and expose both
  forms through `rvw_status`.
- **Step 4 goal**: prove launcher parity, full-state reporting, damaged-entry
  isolation, and the read-only contract with acceptance tests.

---

## Scope anchors for the v0.11.0 review-status plan

This plan implements these settled outcomes:

1. Discover all nonterminal specification and code-review exchanges from
   protocol-owned coordination candidates.
2. Report identity, role, umbrella, lease, artifacts, state, and next action in
   one normalized result.
3. Preserve independent healthy and damaged evidence while leaving protocol and
   Git state untouched.

The following are in scope:

- caller-root resolution with an explicit test override;
- tagged healthy and damaged result records;
- state-aware continuing-role, lease, artifact, and next-action projection;
- deterministic human and versioned JSON rendering; and
- root-launcher, direct-entry, and read-only acceptance coverage.

The following remain deferred to `review-resume-command`:

- choosing one exchange when several are active;
- renewing, reclaiming, repairing, cancelling, or completing an exchange;
- executing the reported next action; and
- emitting or installing continuation instructions.

---

## Complexity bound clarification for v0.11.0 review status

Let `r` be the number of entries at the repository root and `n` the number of
reserved active-coordination candidates.

- **O(r) root discovery**: enumerate the reserved prefix once without scanning
  the documentation tree.
- **O(1) work per candidate artifact kind**: the protocol has exactly six fixed
  artifact paths, so presence and applicability projection remains constant per
  exchange.
- **O(n) observation and normalization**: each candidate receives bounded
  parsing, fingerprint, observer, lease, role, action, and artifact work.
- **O(n log n) final ordering**: the design requires deterministic identity and
  damaged-candidate ordering; this is the single intentional sorting cost.

No status path may add nested candidate scans, per-artifact directory scans, or
an `O(n^2)` comparison. Rendering walks the already ordered in-memory result
once.

---

## File-based IO cost clarification for v0.11.0 review status

- Resolve the caller root once and load `ReviewConfiguration` once.
- Enumerate only the root `a.review-active.*` prefix; do not load documentation
  metadata or walk the repository.
- Read each coordination candidate before observation and once afterward for
  the changed-during-read fingerprint; the existing observer inspects only the
  six derived canonical paths.
- Reuse one normalized result for human output, JSON output, status mapping, and
  later `rvw_resume` consumption.
- Do not enter `transition_lock` or call any store publication, lease, recovery,
  confirmation, completion, marker, index, ref, or working-tree mutation API.

The loading phase is a bounded protocol-index read proportional to active
coordination candidates rather than a broad repository metadata pass.

---

## Confirmed technical facts for v0.11.0 plan viability

Physical line counts include blank lines and use the same per-line iteration
metric as the repository big-file scan.

**Files over the 650-line repository limit**:

- None of the Python files planned for creation or modification is currently
  over the limit.

**Files in the 550-through-650 risk band**:

- `tools/review_exchange_models.py`: **555 lines**. The status implementation
  imports its public identity, configuration, state, context, and path types but
  does not add code to this file.
- `tools/review_exchange_store.py`: **633 lines**. Discovery constructs the
  existing store and observer but does not grow the persistence class.

**Files below 550 and safe to extend**:

- No existing Python file needs modification. All production and focused test
  files are new and begin at zero lines.

**What does not exist yet**:

- `tools/review_status_models.py`.
- `tools/review_status.py`.
- `tools/review_status_render.py`.
- `tools/review_status_cli.py`.
- `rvw_status.bat`.
- Focused unit leaves for status models, discovery, rendering, and CLI behavior.
- The review-status acceptance package and test leaf.

**Other confirmed facts affecting implementation**:

- `tools/review_exchange_observer.py` is 139 lines and already provides the
  read-only `ReviewExchangeObserver.classify()` boundary.
- `tools/review_exchange_paths.py` is 231 lines and already derives all six
  canonical paths and parses transient identities.
- `tools/review_exchange_models_coordination.py` is 238 lines and strictly
  parses `CoordinationRecord`, including owner, next actor, round, lease,
  confirmation, and transition evidence.
- `tools/review_exchange_models_envelope.py` is 220 lines and exposes
  `parse_json_markdown` for reading coordination content without using a private
  store method.
- `tools/review_exchange_state.py` is 277 lines and owns the complete
  `ArtifactState` classifier, including idle, abandoned, interrupted,
  convergence, authorization, escalation, repair, and inconsistency outcomes.
- `tools/review_exchange_transcript_identity.py` is 46 lines and exposes
  `current_request_occurrence` for restarted exchanges.
- `tools._models.find_project_root` already resolves `PRJ_DIR` or walks upward
  from the caller, and `commit-plan-check.bat` demonstrates a root launcher
  that preserves the caller's current directory.

---

## Current test-tree validation snapshot for v0.11.0 review status

Existing test areas that must remain green:

- `tests/unit/tools/test_review_exchange_models/` covers strict exchange,
  context, configuration, artifact-path, and coordination model validation.
- `tests/unit/tools/test_review_exchange_state/` covers every observable state
  and property-based classifier invariants.
- `tests/unit/tools/test_review_exchange_paths/` covers filename identity,
  canonical derivation, Git-root validation, and ignore behavior.
- `tests/unit/tools/test_review_exchange_lifecycle/` covers observer-driven
  transitions and restarted transcript occurrence.
- `tests/unit/tools/test_review_exchange_store/` covers strict coordination and
  artifact reads; its 528-line validation test is not modified.

New unit test leaf directories:

- `tests/unit/tools/test_review_status_models/`.
- `tests/unit/tools/test_review_status/`.
- `tests/unit/tools/test_review_status_render/`.
- `tests/unit/tools/test_review_status_cli/`.

New acceptance test leaf:

- `tests/acceptance/review_status/test_review_status_acceptance/`.

Property-based coverage is required for candidate enumeration order and result
ordering. Arbitrary valid identities and malformed reserved-prefix names must
produce the same ordered result regardless of source enumeration order;
parameterized examples remain the clearer coverage for the finite state, role,
lease, artifact, action, renderer, and process-status tables.

---

## Step 0 perf-gate assessment for v0.11.0 review status

No Step 0 wall-clock gate is added. The settled design defines bounded reads and
complexity but no duration threshold, and a filesystem timing assertion would
measure host load rather than the contract. Step 2 instead adds deterministic
read-count, fixed-artifact, configuration-load, changed-during-read, and
no-write tests. Step 4 repeats the no-mutation proof through the real launcher.

---

## Implementation constraints carried from the settled design

- Healthy and damaged entries share one ordered tagged-union collection.
- The absolute repository root appears once; all subordinate paths are
  repository-relative.
- `expected_next_actor` controls ordinary continuation, while convergence and
  escalation use the two confirmed state-aware mappings and owner stays
  separate.
- Lease evidence uses fixed timestamps and the four `current`, `expired`,
  `not-held`, and `missing` categories; no changing elapsed counter is stored.
- Artifact kind is a six-key object whose applicability and presence remain
  separate.
- Exit status is `0` for trustworthy results, `3` for results containing
  untrustworthy exchange evidence, and `2` for invocation or operational
  failure.
- Coordination changes during observation become an explicit diagnostic; the
  status path never acquires the transition lock.

---

## Implementation decisions for v0.11.0 review status

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Use frozen standard-library dataclasses and string-valued enums for immutable status records, matching the surrounding exchange models without adding a dependency. | Step 1 classes and behavior | `NamedTuple` validation limits; a new runtime validation library |
| Q02 | Give each public record an explicit `to_dict()` projection and compose those mappings at the result root so the versioned schema is deliberate. | Step 1 classes and behavior | One serializer coupled to every model; generic `dataclasses.asdict()` reflection |
| Q03 | Keep private pure projection helpers in `review_status.py` initially and use the named `review_status_projection.py` split only when measured size requires it. | Step 2 classes and behavior; Step 2 split guidance | Immediate module extraction; moving protocol-state interpretation onto result records |
| Q04 | Route IO through a private dependency bundle while keeping `collect_review_status(root, wall_clock)` as the small public API. | Step 2 tests first and classes and behavior | Scattered direct monkeypatches; public test-oriented collaborator parameters |
| Q05 | Run broad permutation properties over normalized entries and retain parameterized filesystem cases for discovery integration. | Test-tree validation snapshot; Step 2 tests first | A temporary repository per generated example; fixed permutations without property coverage |
| Q06 | Pin representative complete JSON and human outputs, then use focused assertions for finite variants. | Step 3 tests first | Complete goldens for every case; substring and parsed-field assertions alone |
| Q07 | Test executable launcher forwarding with a controlled target in Step 3 and reserve real nested-caller repository parity for Step 4. | Step 3 tests first; Step 4 classes and behavior | Duplicated end-to-end matrices; acceptance-only launcher coverage; batch-file text matching |
| Q08 | Create one acceptance `conftest.py` from the start for reusable repository and durable-exchange builders, leaving the scenario leaf an estimated 170 lines below the risk band. | Step 4 files, fixture behavior, budgets, and split guidance | Threshold-triggered extraction; immediate fragmentation across several helper modules |

These decisions settle every implementation-detail choice raised by the plan
review. No follow-up question is required before Step 1 can begin.

---

## Shared execution command checklist for all v0.11.0 review-status steps

Apply this checklist to every numbered step with its step-specific paths.

1. Count physical lines before edits for every Python file in the step.
2. Add the step tests before production behavior.
3. Run `ghog single` with the step's focused test files.
4. Run the step-specific `rg` checks for types, observer reuse, fields,
   renderers, arguments, statuses, or launcher wiring.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare every Python file with its
   baseline, policy band, advisory estimate, and 650-line ceiling.
7. If a Python file exceeds 650 lines, stop and apply the responsibility split
   stated in the step before committing.
8. If a file exceeds only an advisory estimate while remaining at or below 650,
   record the variance without failing the step or requiring a split.

## Ready-to-run commands for all v0.11.0 review-status steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Targeted tests: `ghog single <step-test-files>`
- Grep checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated fix-and-walk until it reports the
  objective with `exit=0`
- Physical line recount: `(Get-Content -LiteralPath '<path>').Count`

---

## Numbered implementation steps for v0.11.0 review status

### Step 1. Define the versioned review-status result model

#### Step 1 analysis and intent for typed status evidence

Issues to address:

- The exchange core exposes identity and state types but has no repository-wide
  tagged result for healthy and damaged candidates.
- Role specialization, lease category, next-action identity, artifact
  applicability, overall outcome, and schema version need closed values before
  discovery or rendering can depend on them.

Fix intent:

- Add immutable JSON-compatible status records that keep trusted exchange data
  separate from partial damaged-candidate evidence.
- Make all downstream renderers and the later resume effort consume the same
  typed fields rather than interpreting prose.

Expected outcome:

- One strict result owns schema version, repository root, outcome, active count,
  error flag, and ordered entries.
- Healthy entries can represent the complete design field set, while damaged
  entries expose only safely parsed facts, candidate path, and diagnostics.

Step framing:

- Design links: Stable machine record, Continuing-agent mapping, Lease
  freshness, Artifact completeness, and Next-action identity.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 1 implementation for typed status evidence

**Files involved**:

- `tools/review_status_models.py` (new, to be created).
- `tests/unit/tools/test_review_status_models/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  (new, to be created).

**Tests first**:

- Cover strict enum values and immutable healthy, damaged, artifact, lease, and
  repository-result construction.
- Cover repository-relative path validation, six artifact keys, positive round
  and occurrence values, nullable umbrella and implementation step, error-flag
  consistency, and stable `to_dict()` output.
- Reject guessed identity on damaged candidates and inconsistent active counts
  or trustworthy outcomes.

**Classes and behavior**:

- Use frozen standard-library dataclasses and string-valued enums for every
  public status record and closed vocabulary; add no runtime model dependency.
- `ReviewStatusOutcome`, `LeaseFreshness`, `ArtifactApplicability`, and
  `NextAction`: closed machine vocabularies from the settled design.
- `ArtifactStatus` and `LeaseStatus`: keep raw evidence, derived state, and
  fixed timestamps together.
- `ExchangeStatus` and `DamagedCandidateStatus`: form the tagged entry union.
- Give each public record an explicit `to_dict()` projection, with the top-level
  result composing those mappings so internal field names do not silently
  define the versioned wire schema.
- `ReviewStatusResult`: owns schema version, absolute root, ordered entries,
  active count, error flag, composed JSON projection, and process-status
  mapping.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`
  passes.
- `rg -n "ReviewStatusResult|ExchangeStatus|DamagedCandidateStatus|NextAction|LeaseFreshness" tools/review_status_models.py tests/unit/tools/test_review_status_models`
  shows every public result component and its tests.
- `ghog day` reports the objective with `exit=0`.

#### Step 1 addendums for typed status evidence

Line-budget checkpoint:

- `tools/review_status_models.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 280 lines (advisory).
- `tests/unit/tools/test_review_status_models/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 360
  lines (advisory).

Split guidance:

- If the model module would exceed 650, extract only JSON projection helpers to
  `tools/review_status_serialization.py`; keep the closed enums and immutable
  records together.
- If the unit file approaches 550, split serialization cases into a sibling
  conventional test leaf before adding more model cases.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status_models/test_review_status_models_tdd.py`;
  `ghog day`.

Time-gated status for Step 1:

- No wall-clock perf gate is affected; this step is pure in-memory validation
  and projection.

---

### Step 2. Discover and normalize every active coordination candidate

#### Step 2 analysis and intent for bounded repository discovery

Issues to address:

- No service enumerates the reserved active-coordination prefix or converts each
  candidate into independent healthy or damaged status evidence.
- The observer classifies one known context, while status must first validate
  filename identity and coordination content and must detect a concurrent
  coordination change without locking.

Fix intent:

- Build one read-only collection service that parses each candidate, verifies
  filename, record, context, and canonical-path agreement, then delegates valid
  exchanges to `ReviewExchangeObserver`.
- Normalize role, specialization, umbrella, occurrence, lease, artifacts, next
  action, and diagnostics with one evaluation timestamp and configuration load.

Expected outcome:

- Every non-idle valid exchange and every malformed reserved-prefix candidate
  appears independently in deterministic order.
- One damaged candidate cannot hide healthy exchanges, and a changed
  coordination fingerprint cannot produce a falsely trustworthy snapshot.

Step framing:

- Design links: Repository and discovery boundary, Normalized exchange result,
  Read-only trust boundary, and Design decisions Q01 through Q10.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 2 implementation for bounded repository discovery

**Files involved**:

- `tools/review_status.py` (new, to be created).
- `tests/unit/tools/test_review_status/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status/test_review_status_tdd.py` (new, to be
  created).
- `tests/unit/tools/test_review_status/test_review_status_pbt.py` (new, to be
  created).

**Tests first**:

- Cover empty, single, multiple, malformed-name, malformed-content,
  filename-record mismatch, missing umbrella field, canonical-path mismatch,
  idle exclusion, mixed healthy/damaged, and changed-during-read cases.
- Cover configuration loading with the review-mode marker present, where the
  result reports its configured timeout.
- Cover configuration loading with the review-mode marker absent, where loading
  returns the disabled-mode fallback timeout.
- Parameterize every `ArtifactState` through continuing-role, specialization,
  owner, action, lease, artifact applicability, and overall outcome mapping.
- Spy on configuration loading, candidate enumeration, coordination reads,
  fixed artifact probes, observer construction, store mutation methods, and
  transition-lock access.
- Add Hypothesis coverage proving enumeration-order independence and stable
  identity/candidate ordering over generated normalized entries; retain focused
  parameterized filesystem permutations for discovery integration.

**Classes and behavior**:

- `collect_review_status(root, wall_clock)`: load configuration and evaluation
  time once, collect candidates, normalize entries, sort them, and return one
  `ReviewStatusResult`.
- Keep its production signature small while routing filesystem and observer
  access through a private dependency bundle whose defaults use the real
  repository APIs and whose test doubles count reads and reject writes.
- Candidate parsing: use `parse_transient_identity`, `parse_json_markdown`, and
  `CoordinationRecord.from_dict`, then compare filename identity, record
  context, and `derive_artifact_paths` before observation.
- Valid observation: construct `ReviewExchangeStore` and
  `ReviewExchangeObserver`, reuse `classify()`, exclude only `idle`, and derive
  occurrence with `current_request_occurrence`.
- Fingerprint guard: compare exact coordination bytes before and after
  observation and convert a mismatch into changed-during-read evidence.
- Pure projection helpers: implement the settled state-aware role, lease,
  artifact, next-action, outcome, and deterministic sort tables privately in
  `review_status.py`; extract them only at the named size boundary.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status/test_review_status_tdd.py tests/unit/tools/test_review_status/test_review_status_pbt.py`
  passes.
- `rg -n "ReviewExchangeObserver|parse_transient_identity|parse_json_markdown|current_request_occurrence|changed-during-read" tools/review_status.py tests/unit/tools/test_review_status`
  shows reuse of every required authority and the race guard.
- Read-count tests show one configuration load, one prefix enumeration, bounded
  per-candidate reads, no documentation walk, no transition lock, and no write.
- `ghog day` reports the objective with `exit=0`.

#### Step 2 addendums for bounded repository discovery

Line-budget checkpoint:

- `tools/review_status.py`: before 0; below-550 safe; repository ceiling 650;
  expected at or below 450 lines (advisory).
- `tests/unit/tools/test_review_status/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status/test_review_status_tdd.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 500 lines
  (advisory).
- `tests/unit/tools/test_review_status/test_review_status_pbt.py`: before 0;
  below-550 safe; repository ceiling 650; expected at or below 180 lines
  (advisory).

Split guidance:

- If `tools/review_status.py` would exceed 650, extract only pure state-to-role,
  lease, artifact, action, and ordering projection into
  `tools/review_status_projection.py`; keep root enumeration and observer
  orchestration in the service.
- If the example test approaches 550, move read-boundary spies into a sibling
  `test_review_status_io` leaf rather than weakening coverage.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status/test_review_status_tdd.py` and
  `tests/unit/tools/test_review_status/test_review_status_pbt.py`; `ghog day`.

Time-gated status for Step 2:

- No wall-clock timeout is added. Deterministic IO-count and complexity tests
  own the bounded-loading requirement.

---

### Step 3. Render and expose the `rvw_status` command

#### Step 3 analysis and intent for command and output parity

Issues to address:

- The normalized result needs concise human output and stable versioned JSON
  without separate data gathering or status logic.
- The repository has no caller-preserving `rvw_status` launcher or direct CLI
  with human/JSON selection and explicit root override.
- The installed llm-shared plugin has no discoverable
  `$llm-shared:review-status-command` skill that delegates to the launcher.

Fix intent:

- Add two renderers over the same immutable result and one thin CLI that maps
  result outcome to process status.
- Follow the root-launcher precedent so installed runtime location never
  replaces the caller repository.
- Add one canonical skill instruction and thin provider adapters; keep all
  status discovery and classification in `rvw_status`.

Expected outcome:

- Human output visibly separates Role, Specialization, Owner, and Umbrella for
  each exchange and retains candidate diagnostics when identity is damaged.
- JSON and human forms agree, direct and batch entry points select the same
  repository, and fatal invocation errors return status `2` without a partial
  trustworthy payload.
- The installed plugin exposes `$llm-shared:review-status-command`, and every
  provider adapter points directly to the same canonical read-only workflow.

Step framing:

- Design links: Human report and command outcome, Stable machine record, and
  Caller repository resolution.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 3 implementation for command and output parity

**Files involved**:

- `tools/review_status_render.py` (new, to be created).
- `tools/review_status_cli.py` (new, to be created).
- `rvw_status.bat` (new, to be created).
- `instructions/review-status-command.md` (new, to be created).
- `.agent/workflows/review-status-command.md` (new, to be created).
- `.agents/llm-shared/instructions/review-status-command.md` (new, to be
  created).
- `.agents/llm-shared/skills/review-status-command/SKILL.md` (new, to be
  created).
- `.claude/skills/review-status-command/SKILL.md` (new, to be created).
- `.github/skills/review-status-command/SKILL.md` (new, to be created).
- `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_status_render/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`
  (new, to be created).
- `tests/unit/tools/test_review_status_cli/__init__.py` (new, to be created).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py` (new,
  to be created).

**Tests first**:

- Cover zero, healthy, damaged, and mixed human reports; assert separate role,
  specialization, owner, umbrella, lease, artifact, next-action, and diagnostic
  labels.
- Cover deterministic compact JSON, Unicode/path handling, schema version,
  null standalone umbrella, tagged entries, and renderer no-IO behavior.
- Pin complete compact JSON strings and complete representative human blocks,
  then use focused field assertions for the remaining finite variants.
- Cover `--format human`, `--format json`, `--root`, upward caller discovery,
  invalid roots, operational failures, stdout/stderr separation, and statuses
  `0`, `3`, and `2`.
- Cover launcher self-location, newest llm-shared Python selection, caller
  directory preservation, `PYTHONPATH`, and exit-code forwarding through a
  controlled executable target rather than batch-file text matching.
- Cover the canonical skill instruction, direct adapter references, discovery
  metadata, and the absence of copied status or mutation policy.

**Classes and behavior**:

- `render_human(result)`: print repository and outcome once, then one stable
  labelled exchange or damaged-candidate block per ordered entry.
- `render_json(result)`: serialize the same typed result with no new discovery
  or path normalization.
- `review_status_cli.main(argv)`: parse arguments, resolve and validate root,
  collect once, render once, route streams, and return the typed status.
- `rvw_status.bat`: self-locate the llm-shared runtime while retaining `%CD%`
  as the default discovery origin and forwarding all arguments and exit status.
- `instructions/review-status-command.md`: direct the agent to the full-path
  `rvw_status` launcher, preserve caller-root semantics, interpret statuses
  `0`, `3`, and `2`, and stop after read-only reporting.
- Provider adapters: expose the skill name and link directly to the canonical
  instruction without copying command behavior.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
  passes.
- `rg -n "Role:|Specialization:|Owner:|Umbrella:|schema_version|--format|--root|review-status-command|rvw_status" tools/review_status_render.py tools/review_status_cli.py rvw_status.bat instructions/review-status-command.md .agents/llm-shared/skills/review-status-command tests/unit/tools/test_review_status_render tests/unit/tools/test_review_status_cli tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`
  shows the required visible fields and command contract.
- Renderer tests prove no filesystem or subprocess access after collection.
- `ghog day` reports the objective with `exit=0`.

#### Step 3 addendums for command and output parity

Line-budget checkpoint:

- `tools/review_status_render.py`: before 0; below-550 safe; repository ceiling
  650; expected at or below 220 lines (advisory).
- `tools/review_status_cli.py`: before 0; below-550 safe; repository ceiling 650;
  expected at or below 180 lines (advisory).
- `rvw_status.bat`: before 0; non-Python launcher; Python ceiling not
  applicable; expected at or below 35 physical lines (advisory).
- `instructions/review-status-command.md`: before 0; below-550 safe; repository
  ceiling 650; expected at or below 80 lines (advisory).
- Each provider adapter: before 0; below-550 safe; repository ceiling 650;
  expected at or below 12 lines (advisory).
- `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 100
  lines (advisory).
- `tests/unit/tools/test_review_status_render/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 330
  lines (advisory).
- `tests/unit/tools/test_review_status_cli/__init__.py`: before 0; below-550
  safe; repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`: before
  0; below-550 safe; repository ceiling 650; expected at or below 330 lines
  (advisory).

Split guidance:

- If the renderer module would exceed 650, separate human and JSON presentation
  while keeping both dependent only on `ReviewStatusResult`.
- If CLI or launcher tests approach 550, split launcher-process cases into a
  focused sibling leaf; keep parser and status-mapping cases together.

Full workflow timing run readiness:

- `tests/unit/tools/test_review_status_render/test_review_status_render_tdd.py`,
  `tests/unit/tools/test_review_status_cli/test_review_status_cli_tdd.py`, and
  `tests/unit/tools/test_instruction_structure/test_review_status_command_adapters_tdd.py`;
  `ghog day`.

Time-gated status for Step 3:

- No perf gate changes; renderers must remain in-memory and CLI work stays one
  collection plus one render.

---

### Step 4. Prove end-to-end status behavior and read-only rollout

#### Step 4 analysis and intent for acceptance and rollout

Issues to address:

- Unit tests cannot prove that the real launcher, direct module, ignored review
  files, Git state, and caller-root selection behave together.
- The final feature needs permanent coverage for every acceptance shape that
  previously required manual state reconstruction, including overnight-style
  escalation and healthy/damaged mixtures.

Fix intent:

- Exercise the public launcher and direct Python entry against temporary Git
  repositories populated through real review-exchange models and stores.
- Snapshot protocol artifacts and Git evidence before and after status calls to
  prove that repeated diagnosis is read-only.

Expected outcome:

- No, one, multiple, convergence, authorization, escalation, standalone,
  umbrella, malformed, inconsistent, missing-artifact, and changed-state cases
  produce the designed output and process status.
- The root launcher and direct entry report identical structured results from a
  nested caller directory, and repeated calls leave every observed byte and Git
  fact unchanged.

Step framing:

- Design link: Acceptance cases for v0.11.0 review status.
- Execution checklist reference: Shared execution command checklist for all
  v0.11.0 review-status steps.

#### Step 4 implementation for acceptance and rollout

**Files involved**:

- `tests/acceptance/review_status/__init__.py` (new, to be created).
- `tests/acceptance/review_status/conftest.py` (new, to be created).
- `tests/acceptance/review_status/test_review_status_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  (new, to be created).

**Tests first**:

- Build real temporary repositories with zero, one, and multiple specification
  and code exchanges, umbrella and standalone contexts, fixed timestamps, and
  every designed nonterminal category.
- Assert broad role and specialization, separate owner, exact umbrella, step,
  round, occurrence, lease, six artifacts, next action, diagnostics, ordering,
  active count, error flag, and statuses `0`, `3`, and `2`.
- Mix healthy and malformed candidates and prove healthy records remain in both
  outputs while the repository outcome becomes untrustworthy.
- Compare recursive protocol-file hashes, `git status --porcelain`, index tree,
  current ref, review marker, and coordination bytes before and after repeated
  launcher and direct-entry calls.

**Classes and behavior**:

- Acceptance fixtures in `tests/acceptance/review_status/conftest.py` use
  `ReviewContext`, `CoordinationRecord`,
  `ReviewExchangeStore`, and canonical paths to create valid durable evidence;
  they write malformed candidates directly only for damage cases.
- Subprocess coverage invokes `rvw_status.bat` from a nested caller path and the
  direct module with the same root, parses JSON, and compares full payloads.
- No production type is added in this step; it closes the feature with public
  behavior and non-mutation evidence.

**Completion criteria**:

- `ghog single tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`
  passes.
- `rg -n "rvw_status|convergence|owning-action|escalated|Umbrella|git status|index" tests/acceptance/review_status`
  shows public command, state, identity, and read-only coverage.
- The acceptance file covers every row in the design acceptance table and both
  entry points.
- `ghog day` reports the objective with `exit=0`.

#### Step 4 addendums for acceptance and rollout

Line-budget checkpoint:

- `tests/acceptance/review_status/__init__.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 5 lines (advisory).
- `tests/acceptance/review_status/conftest.py`: before 0; below-550 safe;
  repository ceiling 650; expected at or below 240 lines (advisory).
- `tests/acceptance/review_status/test_review_status_acceptance/__init__.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 5
  lines (advisory).
- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`:
  before 0; below-550 safe; repository ceiling 650; expected at or below 380
  lines (advisory).

The proactive split raises the combined advisory estimate from 520 to 620 lines
because the extracted fixture module needs its own imports, docstring, fixture
decorators, and explicit signatures; both files remain below the risk band.

Split guidance:

- Keep repository and durable-exchange builders in
  `tests/acceptance/review_status/conftest.py` from the start and keep public
  scenario assertions in the test leaf.
- If `conftest.py` itself approaches 550, split protocol-state
  construction from subprocess invocation rather than weakening scenarios.

Full workflow timing run readiness:

- `tests/acceptance/review_status/test_review_status_acceptance/test_review_status_acceptance_tdd.py`;
  `ghog day`.

Time-gated status for Step 4:

- No wall-clock threshold is introduced. Repeated-call byte equality, bounded
  read-count unit evidence, and full Git-state equality are the rollout gates.

---
