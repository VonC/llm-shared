# Code review transcript for v0.13.0

- Exchange: code/code/v0.13.0/shared-wait-service
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-09-15T18:48:29+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 shared-wait-service (round 1)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Implementation plan: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 shared-wait-service (round 1)

request_index_tree: 45dd99f48db9e8e5879e6e630df8892cdb5b4b5c
resolved_validation_set:

- ghog day (sources: project)
- powershell -NoProfile -ExecutionPolicy Bypass -File .reviews/a.step1-gate.ps1 -Subcommand single tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py tests/unit/tools/wait_evidence/test_models/test_models_tdd.py tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py (sources: plan)
- rg -n 'CoverageAssessment|request_coverage|usage_coverage|B-prototype|B-service' tools/wait_evidence (sources: plan)
- powershell -NoProfile -ExecutionPolicy Bypass -File .reviews/a.step1-all-counts.ps1 (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(workflow): fix validation documentation
group 1 path: docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md
group 1 path: wiki/explanation/why-effort-folders-need-document-evidence.md
group 2: feat(wait): collect synthetic thread evidence
group 2 path: tools/wait_evidence/__init__.py
group 2 path: tools/wait_evidence/models.py
group 2 path: tools/wait_evidence/telemetry.py
group 2 path: tools/wait_evidence/collector.py
group 2 path: tools/wait_evidence/reports.py
group 2 path: docs/v0.13.0/collect.shared-wait-service.py
group 2 path: tests/unit/tools/wait_evidence/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_models/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_models/test_models_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_reports/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py
group 3: docs(shared-wait-service): record step 1 validation
group 3 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/collect.shared-wait-service.py
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md
staged path: tests/unit/tools/wait_evidence/__init__.py
staged path: tests/unit/tools/wait_evidence/test_collector/__init__.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py
staged path: tests/unit/tools/wait_evidence/test_models/__init__.py
staged path: tests/unit/tools/wait_evidence/test_models/test_models_tdd.py
staged path: tests/unit/tools/wait_evidence/test_reports/__init__.py
staged path: tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/__init__.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
staged path: tools/wait_evidence/__init__.py
staged path: tools/wait_evidence/collector.py
staged path: tools/wait_evidence/models.py
staged path: tools/wait_evidence/reports.py
staged path: tools/wait_evidence/telemetry.py
staged path: wiki/explanation/why-effort-folders-need-document-evidence.md
```

### Requestor assessment for step 1 shared-wait-service (round 1)

Step 1 has been fully implemented and is ready for independent code review.

- The final Groundhog day walk completed on 2026-09-15 at 18:37:55 +02:00:
  3,000/3,000 tests passed, fail=0, warn=0, xfail=0, cov=100, exit=0.
  Static checks took 22.1 seconds, affected tests 1.9 seconds, and the full
  test run 2 minutes 13.9 seconds. Duration-outlier checks were skipped;
  this is not a claim that those checks passed.
- Evidence: `.reviews/a.step1-final-ghog.log`, `a.ghog.log`, and the Step 1
  section of `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`.
  Project and launcher environment evidence is recorded separately in
  `.reviews/a.step1-environment-result.md`.
- The final focused affected run passed all 53 collector tests with 100%
  measured coverage before the final full walk. Tests exercise malformed,
  partial, delayed and duplicate input, exact identity, independent coverage,
  baseline epochs, cross-phase requests, nested tools, fake-clock drain,
  immutable reports, matched comparisons and cross-cwd CLI invocation.
- Parsing, accounting, report rendering and typed models have separate
  responsibilities. Reads use fixed snapshot budgets and bounded chunks;
  accounting and correlation scan normalized events without repository scans.
  Timeouts guard tests; contractual waits use fake clocks.
- All 19 added Python files are below 550 physical lines; the largest is
  collector.py at 543, below the mandatory 650-line ceiling.
- The standalone docs-side CLI has real subprocess smoke coverage from two
  working directories. It is outside the existing tools coverage denominator;
  no coverage exclusions or dependency declarations were changed.
- This is synthetic-v1 evidence collection only. Installed-host adapters,
  native wake feasibility, live A/B trials and service acceptance belong to
  later steps and remain unperformed. Missing evidence stays unknown or
  inconclusive; B-prototype and B-service labels remain distinct.

Writer assessment: recommend reviewing the staged Step 1 implementation and
its two separately grouped documentation repairs. No commit is authorized yet.

### Implementation report for step 1 shared-wait-service (round 1)

The implementation supplies reusable exact-thread synthetic telemetry
collection before native wake measurement.

- `models.py` validates manifest identities, explicit paths, frozen controls,
  finite timing bounds, baseline epochs and typed report fields.
- `telemetry.py` validates the synthetic host/schema envelope and incrementally
  reads JSONL using explicit offsets, partial-line state and bounded snapshots.
  Missing, rotated, truncated, malformed and oversized input creates evidence
  gaps instead of silently claiming completeness.
- `collector.py` separates phase costs, deduplicates request attempts and usage,
  reconciles compatible cumulative baselines, correlates nested tool calls and
  recognizes polling independently of literal tool names. Request and usage
  coverage remain independent. Seed, auxiliary and post-observation costs stay
  separate from primary measured costs. Drain decisions use monotonic elapsed
  time or authoritative coverage; offline timestamps alone cannot prove drain.
- `reports.py` writes exclusive immutable report versions and retains failed,
  invalid and inconclusive trials. Pairing enforces fresh identity and matching
  seed/configuration/context controls, with separate treatment arms and
  median/range summaries for eligible comparisons.
- `collect.shared-wait-service.py` bootstraps imports from its own physical
  path while requiring explicit manifest/output paths and report identity.
- Tests cover behavioral and property cases in per-module unit folders,
  including real subprocess invocation with the verified project interpreter.

The full regression gate also required an invocation-model section in the
existing effort-discovery explanation and two blank lines around an existing
list item in the planning review transcript. The transcript's published prose
is unchanged; these repairs have their own commit group.

The validation plan records Step 1 evidence and leaves Steps 2 through 8
pending. No umbrella completion, native wake or service result is claimed.

### Change summary for step 1 shared-wait-service (round 1)

The staged scope contains 22 paths in the following prepared `a.commit` groups.
The grouped commit plan has passed formatting and readiness checks.

#### Group 1: docs(workflow): fix validation documentation for step 1 shared-wait-service (round 1)

- `docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md`
- `wiki/explanation/why-effort-folders-need-document-evidence.md`

#### Group 2: feat(wait): collect synthetic thread evidence for step 1 shared-wait-service (round 1)

- `tools/wait_evidence/__init__.py`
- `tools/wait_evidence/models.py`
- `tools/wait_evidence/telemetry.py`
- `tools/wait_evidence/collector.py`
- `tools/wait_evidence/reports.py`
- `docs/v0.13.0/collect.shared-wait-service.py`
- `tests/unit/tools/wait_evidence/__init__.py`
- `tests/unit/tools/wait_evidence/test_collector/__init__.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/__init__.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_models/__init__.py`
- `tests/unit/tools/wait_evidence/test_models/test_models_tdd.py`
- `tests/unit/tools/wait_evidence/test_reports/__init__.py`
- `tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py`

#### Group 3: docs(shared-wait-service): record step 1 validation for step 1 shared-wait-service (round 1)

- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`

The final validation group records the completed full walk, implementation
scope, exact line counts and local evidence references. It also repairs code
formatting in an existing Step 4 description. Runtime review artifacts, raw
logs and helper scripts remain ignored and are not staged.

### Writer response for step 1 shared-wait-service (round 1)

Writer response:

This is the first implementation code review round for Step 1. There is no
earlier Step 1 code-review feedback to accept or dispute. The implementation
follows the consolidated plan after specification review round 2.

### Reviewer focus for step 1 shared-wait-service (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-active.code.code.v0.13.0.shared-wait-service.md`
- `C:/Users/vonc/git/llm-shared_no_polling/.reviews/a.review-requested.code.v0.13.0.shared-wait-service.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-09-15T19:00:33+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 shared-wait-service (exchange 1) (round 1)

Baseline index tree: 45dd99f48db9e8e5879e6e630df8892cdb5b4b5c

Assessed index tree: 4a12e7b49ca094ddeab598473afca7279e065425

### Implementation check for step 1 shared-wait-service (exchange 1) (round 1)

Result:

Reviewer implementation-check result: **No. Step 1 has NOT been fully implemented.**

Step 1 mostly delivers what the plan asks:

- Typed manifests with explicit absolute paths, frozen hashes and finite bounds.
- Exact-identity normalization of the synthetic schema.
- Bounded chunked reads with partial-line state.
- Deduplicated attempts and completions.
- Epoch-based cumulative reconciliation that keeps unknown values unknown.
- Nested tool correlation independent of tool names.
- Independent request and usage coverage.
- A monotonic drain that a UTC jump cannot shorten.
- Exclusive immutable report versions, and pair summaries that keep failed,
  invalid and inconclusive trials.

The 16 test leaves cover most of the plan's "tests first" list, and the forced
full walk is green at 100% coverage.

Two plan behaviors are not met:

- **Rotation must not silently erase evidence.** Detection depends on
  in-memory cursor identity, so the stream a snapshot opens first is trusted
  blindly. A stream replaced after manifest creation is parsed from the old
  offset with no gap; the reviewer probe returned `['request_attempt']`. The
  existing replacement test covers only a replacement between two reads of the
  same `Telemetry` instance, which the offline CLI never performs.
- **Cross-phase requests are flagged "rather than forcing [them] into a
  bucket".** A request with an unknown end is forced into `cross_boundary` and
  counted as a crossing, instead of staying unknown; the probe showed
  `cross_phase_attempts: 1`, `unknown: 0`.

Architecture:

- Parsing stays in `telemetry.py`, and accounting consumes normalized records
  without file I/O.
- `reports.py` combines report publication, pair summaries and the CLI
  composition root. That is acceptable at 183 lines, but the CLI is the one
  place that composes adapters.
- There are no imports of service, review or host code.

Performance:

- Accounting is linear per snapshot.
- `report()` rebuilds groups three times through `drained()` and `_status`,
  which is still linear.
- The median uses bounded five-element sorts.
- No quadratic path was found.

Coverage: the `[tool.coverage.run]` scope is `source = ["tools"]` with a 100%
gate. All four production modules are inside it and at 100% in the forced walk.
The docs-side CLI is outside the gate; its only statements delegate to
`reports.main`, which two subprocess smoke tests exercise.

The Step 1 validation rows were updated to the No result, with a `Missing work
for Step 1` section listing the three concrete fixes.

Validation plan effects:

Reviewer edits to `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`
are confined to the Step 1 rows:

- `### Analysis of Step 1 implementation state`: the status sentence changed
  from `Yes. Step 1 has been fully implemented.` to `No. Step 1 has NOT been
  fully implemented.`, and the summary now cites the forced walk and the two
  confirmed behavior gaps.
- A new `### Missing work for Step 1` section follows `### What was implemented
  for Step 1`. It has three bullets: record and verify stream identity,
  recompute the snapshot budget after a reset, and keep unknown request
  intervals out of the cross-phase count.

The document-level line stays `No, it is not implemented`. No other step's rows,
the plan, the umbrella or any requirement document was changed.
`attribute-reviewer-patch` reported the patch attributable against the recorded
pre-repair blob `3eb8acc53a037de1af190e86e1411e64bb7e9bef`, and only that path
was staged.

### Pre-repair mandatory checks and coverage for step 1 shared-wait-service (exchange 1) (round 1)

All commands ran against request index tree
`45dd99f48db9e8e5879e6e630df8892cdb5b4b5c` before any reviewer edit.

| Command | Result |
| --- | --- |
| `.reviews/a.step1-gate.ps1 -Subcommand single` (8 step test files) | exit 0; `ghog single done fail=0 warn=0 xfail=0 cov=skipped` |
| `.reviews/a.step1-gate.ps1 -Subcommand day` | exit 0, but no walk ran: "No Python file changed since the last green ghog day walk - nothing to do"; `cov=skipped` |
| `.reviews/a.step1-gate.ps1 -Subcommand day --force` (reviewer rerun) | exit 0; check phase passed ty, pyright, ruff, radon, vulture, big-file (650), Markdown, ShellCheck and EOF; `ghog full done fail=0 warn=0 xfail=0 cov=100`, 3,000 tests, ended 18:57:09 +02:00 |
| `rg -n 'CoverageAssessment\|request_coverage\|usage_coverage\|B-prototype\|B-service' tools/wait_evidence` | The `rg` binary is not on this tool shell's PATH. The same pattern ran through the harness's ripgrep search and matched `models.py`, `collector.py`, `reports.py` and `__init__.py`, including both arm labels and both coverage fields. |
| `.reviews/a.step1-all-counts.ps1` | Failed because `rg` is not on PATH. Recounted with `git ls-files` and physical line reads: collector 543, models 294, reports 183, telemetry 166, init 10, effort CLI 15; test leaves 208, 47, 249, 133, 85, 161, 76, 159; initializers 3. All are below 550. |

Validation state was compared before and after: the tracked difference is only
the reviewer's Step 1 validation-plan rows, and the ignored difference is
`a.ghog.log`. The umbrella digest is unchanged (`239b4aeb…`).

### Resolved validation set and sources for step 1 shared-wait-service (exchange 1) (round 1)

The request's resolved set and the current resolver set are identical:

1. `ghog day` (project source): run through the request's gate script. It was
   also rerun with `--force`, because the unforced run skipped the walk, so
   Markdown changes made after the writer's walk had not been re-checked.
2. The focused Groundhog `single` gate over the eight Step 1 test files (plan
   source).
3. `rg -n 'CoverageAssessment|request_coverage|usage_coverage|B-prototype|B-service' tools/wait_evidence`
   (plan source): run with the harness ripgrep search, because `rg` is not on
   the tool shell's PATH.
4. `.reviews/a.step1-all-counts.ps1` (plan source): replaced by an equivalent
   `git ls-files` physical-line count, because the script calls `rg`.

### Resolver drift and direction for step 1 shared-wait-service (exchange 1) (round 1)

None. The request's validation set and the current resolver set are the same
four commands. The `rg` executable is unavailable in the reviewer's tool shell;
equivalent searches ran, and the substitution is recorded as environment
evidence, not resolver drift.

### Repository state around validation for step 1 shared-wait-service (exchange 1) (round 1)

- The request-time index tree `45dd99f48db9e8e5879e6e630df8892cdb5b4b5c`
  matched the live index at entry, with no unstaged tracked changes.
- The assessed index tree after the reviewer's staged validation rows is
  `4a12e7b49ca094ddeab598473afca7279e065425`.
- The umbrella `docs/v0.13.0/draft.v0.13.0.no_polling.md` digest is unchanged
  before and after the check.
- Validation-state comparison: the tracked difference is only
  `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`, the reviewer's
  Step 1 rows. The ignored difference is `a.ghog.log`. There are no untracked
  differences and no tracked validation side effects.
- The reviewer's local probe ran from the session scratchpad and left no
  tracked files.

### Repair inventory for step 1 shared-wait-service (exchange 1) (round 1)

Repairs made:

- - `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`: the
- implementation-check rows for Step 1 (status sentence, summary, new `Missing
- work for Step 1` section). This is review metadata, polishing-only under the
- code-review contract; it is staged and attributable.
- No implementation, test, wiki, transcript or `a.commit` file was changed by the
- reviewer.

Paths staged:

- The 22 staged paths match the request and the independent commit-plan check:
- - `docs/v0.13.0/collect.shared-wait-service.py`
- - `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md` (includes the
- reviewer's Step 1 rows)
- - `docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md`
- - `tests/unit/tools/wait_evidence/__init__.py`
- - `tests/unit/tools/wait_evidence/test_collector/__init__.py`
- - `tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py`
- - `tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py`
- - `tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py`
- - `tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py`
- - `tests/unit/tools/wait_evidence/test_models/__init__.py`
- - `tests/unit/tools/wait_evidence/test_models/test_models_tdd.py`
- - `tests/unit/tools/wait_evidence/test_reports/__init__.py`
- - `tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py`
- - `tests/unit/tools/wait_evidence/test_telemetry/__init__.py`
- - `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py`
- - `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`
- - `tools/wait_evidence/__init__.py`
- - `tools/wait_evidence/collector.py`
- - `tools/wait_evidence/models.py`
- - `tools/wait_evidence/reports.py`
- - `tools/wait_evidence/telemetry.py`
- - `wiki/explanation/why-effort-folders-need-document-evidence.md`
- The only untracked file is the exchange transcript
- `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`, which is a protocol
- artifact and not part of the step.

### Commit plan assessment for step 1 shared-wait-service (exchange 1) (round 1)

The independent `commit-plan-check.bat --format json` rerun, both at entry and
after the reviewer's staged rows, returned status 0, `state: valid`,
`ready: true`, no diagnostics, and three groups covering all 22 staged paths:

1. `docs(workflow): fix validation documentation`: the plan-review transcript
   and the wiki explanation.
2. `feat(wait): collect synthetic thread evidence`: the package, effort CLI and
   test leaves.
3. `docs(shared-wait-service): record step 1 validation`: the validation plan.

Mechanically the plan is ready, and membership, order and subjects match the
staged work. The content is no longer accurate:

- The Group 1 body says "Add two blank lines around the existing review list
  item" and "without changing the published review's prose". The line is part
  of a wrapped sentence, not a list item, and the change turns it into a
  numbered item (finding 3).
- The Group 3 body records a completed Step 1 validation, while the validation
  rows now read No.

The reviewer did not amend `a.commit`, because the writer's rework will change
the staged content and its message. Rewrite both bodies when regrouping.

### Findings and boundaries for step 1 shared-wait-service (exchange 1) (round 1)

Unresolved findings:

1. **A telemetry stream replaced before the first snapshot read is read without
  a gap** (`tools/wait_evidence/telemetry.py`, `tools/wait_evidence/models.py`).
  `StreamSpec` records only `path` and `offset`. `_Cursor.identity` starts as
  `None`, so rotation is detected only between two reads made by the same
  `Telemetry` instance. The CLI in `reports.main` always builds a fresh
  instance. A reviewer probe replaced the stream after manifest creation with
  a different, longer file. `Telemetry(manifest).snapshot(486)` returned
  `['request_attempt']`: the replacement's bytes were parsed from the old
  offset, no gap was recorded, and the differing prefix was silently skipped.
  Plan Step 1 lists rotation among the cases that must not silently erase
  evidence, and the design requires rotation to be preserved as evidence. A
  related effect is truncation found during `snapshot()`. The remaining budget
  is computed before `_read_cursor` resets the offset to 0, so that snapshot
  records the gap but reads none of the new content.
2. **A request with an unknown end is reported as a cross-boundary attempt**
  (`tools/wait_evidence/collector.py`, `_phases`). When `end_at` is missing or
  invalid, `_request_end` returns `inf`. The phase is first set to
  `Phase.UNKNOWN`, but `any(row.at < boundary < end ...)` then matches every
  later boundary. The phase is overwritten with `Phase.CROSS_BOUNDARY` and
  `crossing` is incremented. The probe with
  `event("request_attempt", 244, attempt_id="a")` produced
  `cross_phase_attempts: 1`, `phase_attempts.cross_boundary: 1` and
  `unknown: 0`. The report thus claims an observed phase crossing, and moves
  usage into that bucket, for a request whose interval is unknown. The gap
  text is correct; the classification is not.
3. **The staged plan-review transcript repair changes published prose**
  (`docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md`). The source text
  was one wrapped sentence, "documents show the same code-complete and
  live-evidence states for Steps 2 and / 8. For change 3, verify...". A line
  beginning with `8.` looks like an ordered list item to the Markdown checker,
  and the repair added blank lines around it. The sentence now renders as a
  fragment ending in "Steps 2 and", followed by a numbered item "For change 3,
  verify ...". The Group 1 commit body calls this "the existing review list
  item" and says the published prose is unchanged; neither is true. The fix
  is a rewrap, for example ending the previous line with "Steps 2" and
  starting the next with "and 8. For change 3", with the two added blank
  lines removed.

Boundary-crossing work:

- These points fall outside Step 1's accepted scope. They were not edited and do
- not block this round, but Step 2 should settle them when it adds the real host
- schema and driver:
- - `Collector._correct` requires exactly one `consumption` event and an
- `automatic: true` useful continuation for every arm, including arm A. A real
- classic-polling trial has no service consumption, so Step 2 must define what
- arm A emits. Otherwise every real arm A trial reports `failed`.
- - `TrialManifest._bounds` rejects any `drain_bound` other than 120. The design
- says the drain is fixed per series and initially 120 seconds, so a later
- series schema must allow its declared value.
- - The report omits the manifest's `cached_input_included` and
- `reasoning_included` semantics, so a published report cannot show how its
- token fields may be combined. Step 2 reports should carry them.
- - The report does not expose the functional wake finding (automatic
- continuation, one consumption, latency within bound) separately from
- coverage. Q02 and AC-02 need "wake observed, coverage inconclusive" to be
- recorded explicitly when the probes run.

### Writer instructions for step 1 shared-wait-service (exchange 1) (round 1)

1. Implement the three bullets under `### Missing work for Step 1` in the
   validation plan, tests first:
   - Add a stream identity to `StreamSpec`: file identity plus a bounded digest
     ending at the recorded offset, or an equivalent that detects replacement
     before the first read. Verify it when `Telemetry` first opens each stream,
     and emit the rotation gap on mismatch. Test replacement between manifest
     creation and a fresh `Telemetry(...).snapshot(...)`, and the CLI path
     through `reports.main`.
   - In `Telemetry.snapshot`, recompute the remaining budget after a reset
     caused by truncation or rotation, and test that the same snapshot reads
     the replacement content present at snapshot start.
   - In `Collector._phases`, keep `Phase.UNKNOWN` and do not increment
     `crossing` when the request end is unknown. Extend
     `test_unknown_request_interval_prevents_zero` to assert
     `phase_attempts["unknown"] == 1` and `cross_phase_attempts == 0`.
2. Fix `docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md` by rewrapping
   the sentence so no line starts with `8.`, for example "...states for Steps 2"
   then "and 8. For change 3, verify the environment state yourself before
   writing it into". Remove the two blank lines the earlier repair added, then
   confirm that the Markdown check still passes.
3. Rerun `ghog single` for the affected leaves and a full `ghog day`, using
   `--force` if the walk would otherwise skip because only Markdown changed.
   Then rerun implementation-check for Step 1.
4. Regroup `a.commit`: correct the Group 1 body (rewrapped sentence, prose
   unchanged) and the Group 3 body to match the new validation result.
5. Leave the out-of-scope notes in the boundary section for Step 2; do not
   implement them in Step 1.

The line budget remains safe: `collector.py` is at 543 lines, so keep the
`_phases` fix small or split along the plan's accounting/correlation boundary
if it would approach 650.

### Decision rationale for step 1 shared-wait-service (exchange 1) (round 1)

Decision: `changes-requested`.

Readiness floor:

1. **Identity: pass.** The envelope, human-readable identity, plan, step 1,
   round 1, occurrence 1 and request index tree all agree.
2. **Completeness: fail.** Two plan behaviors are unmet: stream replacement
   before the first read is undetected, and an unknown request interval is
   classified as a boundary crossing.
3. **Validation and coverage: pass.** The focused gate passed, and the forced
   full walk passed with all checks green, 3,000 tests and 100% coverage. The
   `rg` and count commands ran through equivalent tools, recorded as such.
4. **Staged attribution: pass.** The staged set is unchanged except for the
   attributable reviewer validation rows.
5. **Unresolved findings: fail.** There are three findings: the two
   completeness gaps and the transcript rewrap.
6. **`a.commit`: pass mechanically.** The checker returned status 0, but the
   Group 1 and Group 3 bodies are inaccurate and must be rewritten when
   regrouping.

The reviewer's only edit is review metadata, the Step 1 validation rows, so no
substantive repair was made. The fixes are small and inside Step 1's files, but
they change code, tests and a published document, so they belong to the writer's
rework rather than a reviewer repair. This recommendation is advisory and
authorizes no commit.

### Final reviewer decision for step 1 shared-wait-service (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-09-15T19:21:22+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 shared-wait-service (round 2)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Implementation plan: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 shared-wait-service (round 2)

request_index_tree: 1d1e9aa0c39e1868b84fc55e8b8a67d036e7a109
resolved_validation_set:

- ghog day (sources: project)
- powershell -NoProfile -ExecutionPolicy Bypass -File .reviews/a.step1-gate.ps1 -Subcommand single tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py tests/unit/tools/wait_evidence/test_models/test_models_tdd.py tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py (sources: plan)
- rg -n 'CoverageAssessment|request_coverage|usage_coverage|B-prototype|B-service' tools/wait_evidence (sources: plan)
- powershell -NoProfile -ExecutionPolicy Bypass -File .reviews/a.step1-all-counts.ps1 (sources: plan)
- powershell -NoProfile -ExecutionPolicy Bypass -File .reviews/a.step1-gate.ps1 -Subcommand day --force (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(workflow): fix validation documentation
group 1 path: docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md
group 1 path: wiki/explanation/why-effort-folders-need-document-evidence.md
group 2: feat(wait): collect synthetic thread evidence
group 2 path: tools/wait_evidence/__init__.py
group 2 path: tools/wait_evidence/models.py
group 2 path: tools/wait_evidence/telemetry.py
group 2 path: tools/wait_evidence/collector.py
group 2 path: tools/wait_evidence/reports.py
group 2 path: docs/v0.13.0/collect.shared-wait-service.py
group 2 path: tests/unit/tools/wait_evidence/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_models/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_models/test_models_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_reports/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py
group 3: docs(shared-wait-service): record step 1 validation
group 3 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/collect.shared-wait-service.py
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md
staged path: tests/unit/tools/wait_evidence/__init__.py
staged path: tests/unit/tools/wait_evidence/test_collector/__init__.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py
staged path: tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py
staged path: tests/unit/tools/wait_evidence/test_models/__init__.py
staged path: tests/unit/tools/wait_evidence/test_models/test_models_tdd.py
staged path: tests/unit/tools/wait_evidence/test_reports/__init__.py
staged path: tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/__init__.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
staged path: tools/wait_evidence/__init__.py
staged path: tools/wait_evidence/collector.py
staged path: tools/wait_evidence/models.py
staged path: tools/wait_evidence/reports.py
staged path: tools/wait_evidence/telemetry.py
staged path: wiki/explanation/why-effort-folders-need-document-evidence.md
```

### Requestor assessment for step 1 shared-wait-service (round 2)

Yes. Step 1 has been fully implemented after addressing round 1.

- The full Groundhog walk completed at 19:12:30 +02:00 on 2026-09-15:
  3,018/3,018 tests, fail=0, warn=0, xfail=0, cov=100, exit=0.
  Static checks took 21.8s and full tests took 2m 20.4s. Groundhog status
  confirmed state=done and exit=0. Duration-outlier checks were skipped.
- Before that walk, all 125 focused tests passed. Eight new regression cases
  failed before the fixes. The full walk also passed 152 affected tests.
- Evidence is retained in `.reviews/a.step1-round2-final-ghog.log`,
  `.reviews/a.step1-round2-tests-first.log`, and the updated Step 1 validation
  section. The previously verified environment and source scope are unchanged.
- All production modules retain their responsibilities, bounded I/O and linear
  accounting. Stream baseline checks hash at most 4 KiB in bounded reads.
  The largest file is collector.py at 547 physical lines; all 19 Python files
  remain below 550 and the mandatory 650-line ceiling.
- Tests now cover pre-first-read replacement and same-file rewriting, reset
  snapshot budgets, appends after reset, legacy missing identities, CLI
  replacement evidence, independent simultaneous gaps, and unknown phase costs.
- The docs-side CLI remains outside the existing tools coverage denominator
  and is exercised through real subprocess smoke tests. No dependency or
  coverage configuration changed. Native adapters, live trials and service
  results remain later-step work.

The same 22 staged paths and three commit groups remain mechanically ready.
Commit bodies now describe the sentence rewrap and completed rework accurately.
Writer assessment: ready for independent round 2 review; no commit authorized.

### Implementation report for step 1 shared-wait-service (round 2)

Round 2 keeps the Step 1 package and CLI responsibilities and corrects the
round 1 findings.

- `StreamSpec` accepts paired device/inode identity and SHA-256 fingerprint
  fields. The fingerprint covers at most 4 KiB immediately before the recorded
  offset. Invalid identity fields fail validation; absent identity produces an
  explicit coverage gap when read.
- `Telemetry` verifies this frozen identity against its first opened stream.
  Replacement, truncation or differing pre-offset bytes produce a rotation
  gap and reset the cursor to zero. The snapshot then fixes its byte budget
  from that open file before yielding, retaining replacement records without
  chasing later appends. Subsequent reads retain in-memory continuity checks.
- Distinct evidence-gap reasons now have distinct event identities even at the
  same location and ingestion time, preventing deduplication from hiding a
  second kind of damage.
- `Collector` counts a boundary crossing only for a known finite request end.
  An unknown interval retains its coverage gap and unknown phase usage.
- The plan-review transcript sentence was rewrapped without changing its
  words; the accidental ordered-list interpretation and inserted blank lines
  are removed. The relevant commit body describes this accurately.
- The Step 1 implementation check was repeated against the repaired code,
  tests and full-gate evidence. Its status is Yes and the completed missing-work
  section is removed. Steps 2 through 8 remain pending.

The focused, full, static, coverage, line-count and contract-search evidence
supports this synthetic-only step. No installed-host or native wake claim was
added, and no later-step implementation was attempted.

### Change summary for step 1 shared-wait-service (round 2)

The staged scope contains 22 paths in the following prepared `a.commit` groups.
The grouped commit plan has passed formatting and readiness checks.

#### Group 1: docs(workflow): fix validation documentation for step 1 shared-wait-service (round 2)

- `docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md`
- `wiki/explanation/why-effort-folders-need-document-evidence.md`

#### Group 2: feat(wait): collect synthetic thread evidence for step 1 shared-wait-service (round 2)

- `tools/wait_evidence/__init__.py`
- `tools/wait_evidence/models.py`
- `tools/wait_evidence/telemetry.py`
- `tools/wait_evidence/collector.py`
- `tools/wait_evidence/reports.py`
- `docs/v0.13.0/collect.shared-wait-service.py`
- `tests/unit/tools/wait_evidence/__init__.py`
- `tests/unit/tools/wait_evidence/test_collector/__init__.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_tdd.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_pbt.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_collector/test_collector_accounting_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/__init__.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_models/__init__.py`
- `tests/unit/tools/wait_evidence/test_models/test_models_tdd.py`
- `tests/unit/tools/wait_evidence/test_reports/__init__.py`
- `tests/unit/tools/wait_evidence/test_reports/test_reports_tdd.py`

#### Group 3: docs(shared-wait-service): record step 1 validation for step 1 shared-wait-service (round 2)

- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`

The final validation group records the completed full walk, implementation
scope, exact line counts and local evidence references. It also repairs code
formatting in an existing Step 4 description. Runtime review artifacts, raw
logs and helper scripts remain ignored and are not staged.

### Writer response for step 1 shared-wait-service (round 2)

Writer response:

All round 1 findings are accepted; there is no disagreement or reversed repair.

1. Stream continuity is now checked against frozen manifest identity before
   the first read. Tests cover file replacement, same-file rewriting,
   truncation, and the fresh CLI path. Reset snapshots read the replacement
   present at snapshot start and ignore later appends.
2. Unknown request ends stay in the unknown phase and do not increment the
   cross-phase count. Regression assertions also verify their usage stays in
   that unknown bucket.
3. The planning transcript sentence is rewrapped so `8.` is not mistaken for
   a list marker. Its prose is unchanged. The Group 1 commit body is corrected.

The reviewer-owned Step 1 No result and missing-work list were accepted as the
rework baseline. After completing that work and the full validation walk, the
writer repeated implementation-check, recorded Yes and removed the completed
list. Group 3 now records the new 3,018-test result and review fixes.

The replacement tests also exposed two simultaneous gap reasons colliding at
one stream position and timestamp. Gap identities now include their reason;
the CLI test proves both missing-baseline and unfinished-tail evidence survive.

The four boundary notes remain Step 2 work: classic-arm consumption semantics,
later-series drain bounds, published token-inclusion semantics, and functional
wake findings independent of coverage. This round does not implement them.

For the reviewer environment, the physical-line helper now falls back to Git's
staged path inventory if rg is unavailable. The contract search may use the
equivalent harness ripgrep tool as in round 1. The request adds a forced full
walk so a cached Python-only no-op cannot skip the validation Markdown update.

### Reviewer focus for step 1 shared-wait-service (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-09-15T19:29:44+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 shared-wait-service (exchange 1) (round 2)

Baseline index tree: 1d1e9aa0c39e1868b84fc55e8b8a67d036e7a109

Assessed index tree: 1d1e9aa0c39e1868b84fc55e8b8a67d036e7a109

### Implementation check for step 1 shared-wait-service (exchange 1) (round 2)

Result:

Reviewer implementation-check result: **Yes. Step 1 has been fully implemented.**

The round 1 missing work is complete:

- A frozen stream identity (device/inode plus a bounded 4 KiB anchor digest) is
  verified on the first open of each stream.
- A snapshot recomputes its byte budget after a detected reset.
- An unknown request end stays in the unknown phase.

The staged tests cover each case, including the fresh CLI path, and a
scratchpad probe reproduced the corrected behavior on the staged code. Together
with the round 1 assessment, the step now delivers the plan's full list:

- typed manifests;
- exact-identity synthetic normalization;
- bounded chunked reads with partial-line state and rotation/truncation gaps;
- deduplicated accounting with epoch reconciliation;
- independent request/usage coverage;
- a monotonic drain;
- immutable report versions;
- paired summaries that keep failed and inconclusive trials.

Architecture: parsing and file access stay in `telemetry.py`, accounting
consumes normalized records only, and `reports.py` owns publication and CLI
composition. There are no imports of service, review or host code. Nothing
needs fixing.

Performance: accounting is linear per snapshot, the anchor check reads at most
4 KiB in chunk-bounded reads, and the median uses bounded five-element sorts.
No performance issue needs addressing.

Coverage: `[tool.coverage.run] source = ["tools"]` with a 100% gate. The four
production modules are inside it and at 100% in the forced walk. The docs-side
CLI is outside the gate and only delegates to `reports.main`, which two
subprocess smoke tests exercise. No unit-tested class is below 100%, and no
top-level symbol outside the gate is unreferenced.

The writer's Step 1 validation rows match this result and the measured line
counts, so the reviewer left them unchanged.

All round 1 findings are resolved, confirmed by reading the staged code and by
an independent reviewer probe run from the session scratchpad:

1. **Stream replaced before the first read.**
   - `StreamSpec` now carries a paired `file_id` (device, inode) and
     `anchor_sha256` over at most 4 KiB before the offset. Invalid pairs are
     rejected at manifest validation.
   - `Telemetry._prepare_cursor` checks identity, size and anchor on the first
     open of each stream.
   - Probe results on a fresh `Telemetry(manifest).snapshot(486)`:
     - a replacement file gives a `Telemetry rotation or truncation` gap, then
       parses from zero;
     - an in-place edit before the offset (same inode) gives a gap;
     - an unchanged prefix with an append gives only `compaction`, with no
       false gap.
   - The CLI path is covered by
     `test_cli_detects_replacement_after_manifest_publication`.
2. **Snapshot budget after a reset.** `_read_cursor` computes the remaining
   budget from the open file after `_prepare_cursor` resets the cursor, and
   before yielding. `test_first_snapshot_checks_manifest_identity` (replacement,
   rewrite, truncation) and
   `test_snapshot_recomputes_budget_after_existing_cursor_reset` show that the
   replacement records are read and later appends are not chased.
3. **Unknown request end.** `Collector._crosses` now requires a finite end. The
   probe with `event("request_attempt", 244, attempt_id="a")` gives
   `cross_phase_attempts: 0`, `cross_boundary: 0`, `unknown: 1`, and
   `test_unknown_interval_is_not_an_observed_crossing` asserts it.
4. **Transcript rewrap.** The staged diff for
   `docs/v0.13.0/review.plan.v0.13.0.shared-wait-service.md` now only moves
   "and" so that "and 8. For change 3" continues the sentence. The words are
   unchanged, and the earlier inserted blank lines are gone.

One additional writer change is accepted: gap event identities now digest
location, time and reason, so two different gap reasons at the same position
and time are no longer deduplicated into one.

The four Step 2 boundary notes from round 1 remain open for Step 2, as the
writer states, and are not Step 1 work.

Validation plan effects:

No reviewer edit in round 2. The writer's staged Step 1 rows in
`docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md` are accurate:

- the `Yes. Step 1 has been fully implemented.` status;
- removal of the completed `Missing work for Step 1` section;
- the 3,018-test walk;
- line counts that match the reviewer's recount.

The document-level line stays `No, it is not implemented` because Steps 2 to 8
are pending. Validation-state comparison shows no tracked difference.

### Pre-repair mandatory checks and coverage for step 1 shared-wait-service (exchange 1) (round 2)

All commands ran against request index tree
`1d1e9aa0c39e1868b84fc55e8b8a67d036e7a109`; the reviewer made no edits.

| Command | Result |
| --- | --- |
| `.reviews/a.step1-gate.ps1 -Subcommand single` (8 step test files) | exit 0; `ghog single done fail=0 warn=0 xfail=0` |
| `.reviews/a.step1-gate.ps1 -Subcommand day` | exit 0; skipped as "No Python file changed since the last green ghog day walk" |
| `.reviews/a.step1-gate.ps1 -Subcommand day --force` | exit 0; ty, pyright, ruff, radon, vulture, big-file (650), Markdown, ShellCheck and EOF checks passed; `ghog full done fail=0 warn=0 xfail=0 cov=100`, 3,018 tests, ended 19:26:53 +02:00 |
| `rg -n 'CoverageAssessment\|request_coverage\|usage_coverage\|B-prototype\|B-service' tools/wait_evidence` | Ran through the harness ripgrep search because `rg` is not on the tool shell's PATH: 17 matches in `__init__.py`, `models.py`, `collector.py` and `reports.py` |
| `.reviews/a.step1-all-counts.ps1` | exit 0 using its `git ls-files` fallback: collector 547, models 312, telemetry 195, reports 183, init 10, effort CLI 15; test leaves 221, 47, 259, 133, 86, 216, 89, 177; initializers 3. All are below 550. |

A reviewer scratchpad probe on the staged code confirmed the round 1 fixes: a
replaced stream gives a rotation gap, an in-place prefix edit gives a gap, an
unchanged prefix gives no false gap, and an unknown request end gives
`cross_phase_attempts 0` and `unknown 1`.

### Resolved validation set and sources for step 1 shared-wait-service (exchange 1) (round 2)

The request's resolved set (five commands) and the current resolver set agree:

1. `ghog day` (project source).
2. The focused Groundhog `single` gate over the eight Step 1 test files (plan
   source).
3. The plan's `rg` contract search (plan source), run with the harness ripgrep
   search because `rg` is not on the tool shell's PATH.
4. `.reviews/a.step1-all-counts.ps1` (plan source), which now falls back to
   `git ls-files` and ran directly.
5. `.reviews/a.step1-gate.ps1 -Subcommand day --force` (request source).

### Resolver drift and direction for step 1 shared-wait-service (exchange 1) (round 2)

None. Round 2 adds the forced walk as a request-sourced command. That matches
the reviewer's round 1 practice and is not resolver drift. The only environment
substitution is the harness ripgrep search in place of the unavailable `rg`
binary.

### Repository state around validation for step 1 shared-wait-service (exchange 1) (round 2)

- The request-time index tree `1d1e9aa0c39e1868b84fc55e8b8a67d036e7a109`
  matched the live index at entry, and the assessed tree is identical because
  the reviewer staged nothing.
- The umbrella `docs/v0.13.0/draft.v0.13.0.no_polling.md` digest `239b4aeb…` is
  unchanged.
- Validation-state comparison is `acceptable: true`: no tracked or untracked
  differences, and only the ignored `a.ghog.log` changed.
- The reviewer probe ran from the session scratchpad with bytecode writing
  disabled and left no repository files.

### Repair inventory for step 1 shared-wait-service (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 shared-wait-service (exchange 1) (round 2)

The independent `commit-plan-check.bat --format json` rerun returned status 0,
`state: valid`, `ready: true`, no diagnostics, and three groups covering all 22
staged paths:

1. `docs(workflow): fix validation documentation`: the plan-review transcript
   and the wiki explanation.
2. `feat(wait): collect synthetic thread evidence`: the package, effort CLI and
   test leaves.
3. `docs(shared-wait-service): record step 1 validation`: the validation plan.

The content is also accurate now:

- The Group 1 body describes the sentence rewrap with unchanged prose and the
  new invocation-model section.
- The Group 2 body lists stream identity verification and unknown request
  intervals.
- The Group 3 body records the 3,018-test walk and the round 1 regression fixes.

Membership, order, scope and conventional subjects match the staged work.
`a.commit` remains accurate, and the reviewer did not amend it.

### Findings and boundaries for step 1 shared-wait-service (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 shared-wait-service (exchange 1) (round 2)

No rework is required for Step 1. Present the advisory commit-ready result at
the commit gate. If the human selects Commit, run the reviewed three-group
`a.commit` through the owning workflow.

Carry the boundary notes into Step 2. In particular, the Step 2 manifest driver
must record each stream's `file_id` and `anchor_sha256`, so collection honors
the recorded offset instead of reading from zero with a gap.

Carried notes for Step 2 (not Step 1 boundary-crossing work):

- Arm A's consumption and automatic-continuation semantics in
  `Collector._correct`.
- A later series' drain bound other than 120 seconds.
- Publishing `cached_input_included` and `reasoning_included` with each report.
- An explicit functional wake finding recorded separately from coverage (Q02
  and AC-02).

A design note for Step 2: a manifest stream without an identity is now read
from offset 0 with a `Missing baseline stream identity` gap. That is
conservative for coverage, but every Step 2 driver must record `file_id` and
`anchor_sha256` so the manifest offset is honored.

### Decision rationale for step 1 shared-wait-service (exchange 1) (round 2)

Decision: `commit-ready` (advisory).

Readiness floor:

1. **Identity: pass.** The envelope, human-readable identity, plan, step 1,
   round 2, occurrence 1 and request index tree agree.
2. **Completeness: pass.** Implementation-check is Yes, and the round 1
   missing work is complete with regression tests.
3. **Validation and coverage: pass.** The focused gate passed; the forced full
   walk passed every check, 3,018 tests and 100% coverage; the contract search
   and line counts ran.
4. **Staged attribution: pass.** There are no reviewer repairs, and the staged
   set equals the request's 22 paths.
5. **Unresolved findings: pass.** None are current or carried.
6. **`a.commit`: pass.** The checker returned status 0 with no diagnostics, and
   the group bodies are accurate.

This round made no substantive repair. The recommendation never authorizes a
commit; the commit choice belongs to the human at the convergence gate.

### Final reviewer decision for step 1 shared-wait-service (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-09-15T20:13:05+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-09-17T13:18:43+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 shared-wait-service (round 1)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Implementation plan: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 shared-wait-service (round 1)

request_index_tree: 98120e08a2e01e8cea3edcdfaf9d10e8119ea7bf
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py (sources: plan)
- rg -n 'normal.end|WAIT_TEST_DONE|B-prototype|inconclusive' tools/wait_evidence docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md (sources: plan)
- git diff --cached --check (sources: request)
- ghog single tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: build(wait-evidence): add WebSocket framing
group 1 path: pyproject.toml
group 1 path: uv.lock
group 2: feat(wait-evidence): probe native idle wake
group 2 path: tools/wait_evidence/__init__.py
group 2 path: tools/wait_evidence/claude_monitor.py
group 2 path: tools/wait_evidence/claude_observer.py
group 2 path: tools/wait_evidence/codex_proxy.py
group 2 path: tools/wait_evidence/collector.py
group 2 path: tools/wait_evidence/models.py
group 2 path: tools/wait_evidence/probe_cli.py
group 2 path: tools/wait_evidence/probe_driver.py
group 2 path: tools/wait_evidence/probe_files.py
group 2 path: tools/wait_evidence/probe_observer.py
group 2 path: tools/wait_evidence/prototype.py
group 2 path: tools/wait_evidence/telemetry.py
group 2 path: tools/wait_evidence/telemetry_claude.py
group 2 path: docs/v0.13.0/probe.shared-wait-service.py
group 2 path: tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
group 3: feat(wait-probe): prepare measured TUI sessions
group 3 path: docs/v0.13.0/claude-probe-state.shared-wait-service.py
group 3 path: docs/v0.13.0/claude-probe.shared-wait-service.py
group 3 path: docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/claude-tabs.shared-wait-service.ps1
group 3 path: docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/codex-tabs.shared-wait-service.ps1
group 3 path: docs/v0.13.0/codex-tabs.shared-wait-service.py
group 3 path: docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md
group 3 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md
group 4: docs(wait-probe): retain matched trial evidence
group 4 path: docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
group 5: docs(shared-wait-service): record step 2 validation
group 5 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/claude-probe-state.shared-wait-service.py
staged path: docs/v0.13.0/claude-probe.shared-wait-service.py
staged path: docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/claude-tabs.shared-wait-service.ps1
staged path: docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/codex-tabs.shared-wait-service.ps1
staged path: docs/v0.13.0/codex-tabs.shared-wait-service.py
staged path: docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/probe.shared-wait-service.py
staged path: docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md
staged path: pyproject.toml
staged path: tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py
staged path: tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/__init__.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
staged path: tools/wait_evidence/__init__.py
staged path: tools/wait_evidence/claude_monitor.py
staged path: tools/wait_evidence/claude_observer.py
staged path: tools/wait_evidence/codex_proxy.py
staged path: tools/wait_evidence/collector.py
staged path: tools/wait_evidence/models.py
staged path: tools/wait_evidence/probe_cli.py
staged path: tools/wait_evidence/probe_driver.py
staged path: tools/wait_evidence/probe_files.py
staged path: tools/wait_evidence/probe_observer.py
staged path: tools/wait_evidence/prototype.py
staged path: tools/wait_evidence/telemetry.py
staged path: tools/wait_evidence/telemetry_claude.py
staged path: uv.lock
```

### Requestor assessment for step 2 shared-wait-service (round 1)

Writer assessment: Step 2 is fully implemented, subject to independent code review.
The matching validation section records code completion and live-evidence
completion separately. Steps 3 through 8 remain unimplemented; umbrella item 1
is not being closed by this review.

Validation evidence:

- The exact Claude B1 continuation rejection was reproduced red, then the
  repaired implementation passed 39 focused checks, 10 affected checks and
  all 3,198 full tests with 100% configured coverage, zero failures, warnings
  or xfails. The final walk ended 2026-09-17T07:47:09Z, state=done exit=0.
- Retained full log: a.shared-wait-service/ghog-claude-continuation-green.log,
  SHA-256 4d6d9429b582533b23683f2cde4b5f1805f8c34fb98397b594688bb30eac0b3b.
  Related red and focused logs share that directory and prefix.
- Groundhog owns the static-check, affected-test and coverage gates. Coverage
  is the configured tools scope, with pyproject exclusions; it is not a claim
  of measured coverage for docs-side scripts or every repository file.
- The implementation inventory counted all 30 changed Python files at or
  below 650 physical lines, including tests and initializers, and checked EOF
  markers and references. collector.py has 548 lines; claude_observer.py 388.
  Evidence: a.shared-wait-service/step2-code-inventory.json and the validation
  document's architecture, performance, coverage and feature-integrity sections.
- The isolated prototype uses durable identities, native gates, external
  observers and bounded timers. It does not replace current review/Groundhog
  workflows or implement the later shared service.
- Both hosts have retained controlled baselines and three paired trials.
  Claude B1 remains failed; B2 and B3 passed after the additive validated
  monitor-completion-01 revision. All A trials retain the initial-yield
  limitation. Codex B2's observer recovery and earlier failures remain visible.
- Claude final audit 2026-09-17T09:11:59.194Z passed all aggregate and per-run
  integrity checks. Closure at 09:12:14.715Z verified all original session
  identities, unchanged stream hashes and completed observers. All seven
  Claude tabs may close. No measured trial was retried or reseeded.
- Immediately before review rendering, git diff --cached --check passed and
  commit-plan-check reported ready=true, state=valid, diagnostics=[], with
  all 50 staged paths covered by five groups.

The current request adds the missing Claude median/range and explicit count
summary, computed from the existing exported deltas. This documentation-only
addition preserves raw evidence and production code. The full code validation
above predates that report addition; the review's resolved checks remain due.

Acceptance distinction: SW-09 and AC-15 impose no minimum net token-savings
threshold. SW-11 requires observed counts/deltas, aggregates and limitations,
and forbids inferring billing or quota savings from token counts. Functional
wake is observed; complete request coverage and strict-idle support remain
unknown. The strict no-inference and fresh A/B-service obligations belong to
umbrella item 8, not this effort's local Step 8.

### Implementation report for step 2 shared-wait-service (round 1)

The Step 2 harness now freezes full seeds, reserves exact fresh identities,
enforces READY/context/manifest gates and serial measurements, and persists
registration, source readiness, native delivery and one consumption. The
standalone probe entry point works independently of cwd.

Codex proxy framing and Claude Monitor adapters bind the exact original
conversation. Native transcript normalization keeps request-attempt coverage
unknown when the installed schema cannot establish it. Independent ordinary
processes collect evidence and enforce separate source, wake, duplicate and
drain intervals.

The Claude repair accepts the verified completed-task notification only when
its ancestry, task and Monitor call match the ready notification. It rejects
ambiguous, duplicate or unrelated notices and never rewrites native UUIDs.
Regression tests cover that boundary and lifecycle/transport/parser behavior.

Human-invoked named-tab launchers and run procedures prepare fresh measured
sessions with frozen seeds. The implementing session does not substitute for
a measured TUI. The user submitted all Claude benchmark prompts after readiness.

Versioned results and redacted selected exports retain configuration, hashes,
timings, original failures, per-pair usage and the final integrity audit. Raw
evidence remains local under a.shared-wait-service, including the immutable
claude-controlled-20260917 series and additive implementation revision.

Review focus:

- Check lifecycle suppression, exact native session/turn/task binding,
  startup/readiness races, restart behavior and duplicate consumption.
- Verify the completed Step 2 assessment against AC-02/14/15 and SW-08..11,
  including the failed B1 case and qualified A protocol observations.
- Check descriptive aggregate calculations and denominators, phase attribution,
  known gaps and explicit absence of strict-idle or quota-savings claims.
- Check public exports for appropriate redaction and consistent raw hashes.
- Assess staged scope and the five-group a.commit before recommending readiness.

Do not rerun measured conversations, reseed, alter frozen snapshots, or
overwrite original audits. Read-only audit inspection and deterministic tests
are sufficient to review retained measurements. Any proposed fresh experiment
must preserve every existing trial and its classification.

### Change summary for step 2 shared-wait-service (round 1)

The current staged inventory contains 50 paths in five reviewed commit-plan groups.

#### Staged paths for step 2 shared-wait-service (round 1)

- `docs/v0.13.0/claude-probe-state.shared-wait-service.py`
- `docs/v0.13.0/claude-probe.shared-wait-service.py`
- `docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/claude-tabs.shared-wait-service.ps1`
- `docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/codex-tabs.shared-wait-service.ps1`
- `docs/v0.13.0/codex-tabs.shared-wait-service.py`
- `docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`
- `docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/probe.shared-wait-service.py`
- `docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md`
- pyproject.toml
- `tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py`
- `tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/__init__.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`
- `tools/wait_evidence/__init__.py`
- `tools/wait_evidence/claude_monitor.py`
- `tools/wait_evidence/claude_observer.py`
- `tools/wait_evidence/codex_proxy.py`
- `tools/wait_evidence/collector.py`
- `tools/wait_evidence/models.py`
- `tools/wait_evidence/probe_cli.py`
- `tools/wait_evidence/probe_driver.py`
- `tools/wait_evidence/probe_files.py`
- `tools/wait_evidence/probe_observer.py`
- `tools/wait_evidence/prototype.py`
- `tools/wait_evidence/telemetry.py`
- `tools/wait_evidence/telemetry_claude.py`
- uv.lock

#### Prepared root a.commit for step 2 shared-wait-service (round 1)

#### Grouping commits by topic for step 2 shared-wait-service (round 1)

##### Group 1: Native proxy framing dependency for step 2 shared-wait-service (round 1)

git add -A pyproject.toml
git add -A uv.lock

```log
build(wait-evidence): add WebSocket framing

Why:

The local Codex proxy tunnel carries `WebSocket` frames. Raw JSON transport
cannot complete the native queue protocol.

The development environment now includes the framing dependency used by the
probe transport, with its resolved dependency versions recorded.

What:

- Add wsproto to the development dependencies.
- Record wsproto and its h11 dependency in the lockfile.
```

##### Group 2: Native evidence adapters and durable wake prototype for step 2 shared-wait-service (round 1)

`git add -A tools/wait_evidence/__init__.py`
`git add -A tools/wait_evidence/claude_monitor.py`
`git add -A tools/wait_evidence/claude_observer.py`
`git add -A tools/wait_evidence/codex_proxy.py`
`git add -A tools/wait_evidence/collector.py`
`git add -A tools/wait_evidence/models.py`
`git add -A tools/wait_evidence/probe_cli.py`
`git add -A tools/wait_evidence/probe_driver.py`
`git add -A tools/wait_evidence/probe_files.py`
`git add -A tools/wait_evidence/probe_observer.py`
`git add -A tools/wait_evidence/prototype.py`
`git add -A tools/wait_evidence/telemetry.py`
`git add -A tools/wait_evidence/telemetry_claude.py`
`git add -A docs/v0.13.0/probe.shared-wait-service.py`
`git add -A tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py`
`git add -A tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/__init__.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py`
`git add -A tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`

```log
feat(wait-evidence): probe native idle wake

Why:

Queue acceptance alone cannot prove that the original idle conversation resumes
usefully after normal completion. Native telemetry also needs exact session
binding without inventing complete request accounting.

The isolated prototype now measures native Codex and Claude routes through
durable identities, independent observers and fixed observation windows.

What:

- Add frozen seeds, indexed thread claims, pair ordering and context gates.
- Persist registration, readiness, delivery and single consumption state.
- Adapt Codex proxy framing and Claude Monitor startup and native gating.
- Normalize installed native schemas, ancestry and repeated response usage.
- Bind adjacent Claude notifications to the same ready event and task.
- Retain failures, unknown coverage and separate duplicate and drain windows.
- Cover lifecycle, transport, parsing and continuation regressions in tests.
- Record 39 focused checks and 3198 full tests at 100% configured coverage.
```

##### Group 3: Human-operated session preparation and probe commands for step 2 shared-wait-service (round 1)

`git add -A docs/v0.13.0/claude-probe-state.shared-wait-service.py`
`git add -A docs/v0.13.0/claude-probe.shared-wait-service.py`
`git add -A docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md`
`git add -A docs/v0.13.0/claude-tabs.shared-wait-service.ps1`
`git add -A docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md`
`git add -A docs/v0.13.0/codex-tabs.shared-wait-service.ps1`
`git add -A docs/v0.13.0/codex-tabs.shared-wait-service.py`
`git add -A docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md`
`git add -A docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md`
`git add -A docs/v0.13.0/plan.v0.13.0.shared-wait-service.md`
`git add -A docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md`

```log
feat(wait-probe): prepare measured TUI sessions

Why:

Controlled trials need fresh human-started conversations with verified full
seeds and exact identities before a benchmark prompt is delivered.

Human-invoked launchers now prepare seven named tabs per host. The documented
procedure preserves readiness and sequential measurement gates after resume.

What:

- Add Codex and Claude named-tab launchers and complete frozen seed loading.
- Provide the Claude capability and smoke commands with durable local state.
- Document supported prompt delivery and independent observation boundaries.
- Record authorized operator automation and the exact resumed trial order.
- Keep seeding and identity setup outside measured benchmark activity.
```

##### Group 4: Controlled results, failures and retained audit evidence for step 2 shared-wait-service (round 1)

`git add -A docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json`
`git add -A docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md`

```log
docs(wait-probe): retain matched trial evidence

Why:

Functional wake and observed usage need live evidence separate from unit tests.
Failed trials and protocol deviations must remain visible in matched
comparisons.

Both controlled baselines and three pairs per host now have retained audits,
with passing native routes and explicit limits on usage interpretation.

What:

- Export selected settings, seed hashes, identities, timings and usage phases.
- Preserve Codex observer recovery and all original failed preparations.
- Retain Claude B1 failure and the additive validated continuation repair.
- Record Claude B2/B3 wake at `5.623/11.906` seconds and full final windows.
- Compare all pairs while retaining the Claude A initial-yield deviation.
- Verify final stream integrity, sequential runs and seven-tab closure.
- Keep request accounting unknown and quota or billing savings unproved.
```

##### Group 5: Step 2 implementation validation for step 2 shared-wait-service (round 1)

`git add -A docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`

```log
docs(shared-wait-service): record step 2 validation

Why:

The prototype step requires both validated implementation and retained live
evidence. Prepared commands or successful wake alone cannot close that gate.

Step 2 now satisfies its code and live-evidence requirements, including the
recorded failed and qualified cases. Later service steps remain outstanding.

What:

- Mark Step 2 implemented and remove its completed missing-work list.
- Record architecture, performance, unit coverage and feature integrity.
- Link both host comparisons and the final Claude audit and closure evidence.
- Preserve unknown accounting and future production-adapter revalidation.
```

### Human guidance and writer response for step 2 shared-wait-service (round 1)

Human guidance:

The user asks: "If step 2 is complete, shouldn't you request a review? And is
'quota saving' proof part of step 2?"

Review the actual acceptance requirements and the completion assessment.
Distinguish required measured evidence from a claim of quota or billing savings.
This instruction authorizes review; it does not authorize a commit.

Writer response:

This is the first code-review round for Step 2. There is no earlier reviewer
feedback to accept or dispute.

The user correctly identified that the prepared commit plan must proceed to
review before a commit decision. The prior commit menu was premature and has
been withdrawn. No commit or next-step implementation was authorized or run.

Before publication, the writer supplied the Claude aggregate summary required
by SW-11. No raw evidence or production implementation changed in this
pre-publication documentation correction.

### Reviewer focus for step 2 shared-wait-service (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-09-17T13:25:57+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 shared-wait-service (exchange 1) (round 1)

Baseline index tree: 98120e08a2e01e8cea3edcdfaf9d10e8119ea7bf

Assessed index tree: 98120e08a2e01e8cea3edcdfaf9d10e8119ea7bf

### Implementation check for step 2 shared-wait-service (exchange 1) (round 1)

Result:

Reviewer implementation-check result: **Yes. Step 2 has been fully implemented.**

The step's own work is present and matches the plan, including the operator
automation the plan records as authorized on 2026-09-16:

- `prototype.py` keeps a durable isolated lifecycle: exact
  source/wait/event/thread identities, one delivery attempt, uncertain receipts
  without retry, and single consumption.
- `probe_driver.py` freezes both drafts from the recorded seed commit, records
  hashes, enforces indexed reservations, pair ordering and the 5% context gate.
- `probe_observer.py` and `claude_observer.py` bind native normal end to the
  exact registering turn and keep full duplicate and separate drain windows.
- `telemetry.py` and `telemetry_claude.py` accept only the inspected Codex
  0.154.0 and Claude 2.1.272/2.1.273 shapes, verify stream headers, host home
  and probe roles, and keep request completeness unknown.
- `claude_monitor.py` gates delivery behind the observer and keeps the bridge
  silent except for one stdout line.
- The new `probe_cli.py`, `probe_files.py`, `codex_proxy.py` and the docs-side
  launchers follow the step's split guidance rather than growing
  `prototype.py` beyond the ceiling.

I checked the B1 repair closely, since it decides what counts as an automatic
continuation. `ClaudeObservation._stream_end` accepts the completed-task notice
only when its `parent_uuid` is the ready notification, and the task id,
Monitor `tool-use-id` and `completed` status all match, and only one wake turn
exists. Unrelated notices are ignored rather than accepted, a second completion
notice fails the run, and native UUIDs are never merged. `_consumption` still
requires a bound turn, persisted readiness and no earlier useful continuation.

The retained evidence matches the plan's obligations: a ten-minute baseline per
host, three pairs per host in A/B, B/A, A/B order, per-host pass, fail and
deviation records, retained failures (Claude B1, Codex B2 observer recovery,
the failed smoke preparations), and explicit "request accounting unknown"
statements throughout. The report and validation rows correctly refuse
strict-idle, quota and billing conclusions.

Architecture: the probe stays out of the shared service and of review or
Groundhog workflows; host invocation lives in adapters behind `Route`. No
production workflow imports it. Nothing needs fixing.

Performance: native reads advance captured offsets, ancestry uses keyed state,
notifications select exact paths and journal replay is linear. Nothing needs
addressing.

Coverage: the gate measures `tools` at 100%, and the focused gates I reran
pass. The docs-side helpers stay outside the gate, as recorded.

Two documentation defects and one blocking validation failure are listed under
findings. The failure is not in the step's code: the repository Markdown gate
now rejects the exchange transcript, which this round's own request content
broke. Because a mandatory validation command fails in the received state, the
readiness floor cannot pass this round.

Validation plan effects:

No reviewer edit. The writer's staged Step 2 rows record the Yes status, both
completion components, the architecture, performance, coverage and
feature-integrity sections, and the retained failures and deviations. They match
what I checked, with one gap: they do not mention the added `wsproto` dependency
(finding 2).

Validation-state comparison shows no tracked difference, so the reviewer left
the validation plan and every other tracked file untouched.

### Pre-repair mandatory checks and coverage for step 2 shared-wait-service (exchange 1) (round 1)

All commands ran against request index tree
`98120e08a2e01e8cea3edcdfaf9d10e8119ea7bf`; the reviewer changed nothing.

| Command | Result |
| --- | --- |
| `ghog single` over the plan's two named leaves | exit 0; `fail=0 warn=0 xfail=0` |
| `ghog single tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py` | exit 0; `fail=0 warn=0 xfail=0` |
| `ghog day --force` | **exit 1**. The check phase failed on `markdown(1)`: MD001 and MD050 in `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`. ty, pyright, ruff, radon, vulture, big-file (650), ShellCheck and EOF passed. No test or coverage phase ran. |
| `git diff --cached --check` | exit 0 |
| `rg -n 'normal.end\|WAIT_TEST_DONE\|B-prototype\|inconclusive' tools/wait_evidence docs/...probe-results...md` | Run through the harness ripgrep search because `rg` is not on the tool shell's PATH: 51 matches across 10 `tools/wait_evidence` modules, including the observers, prototype, driver and Claude telemetry |

The plain `ghog day` was not run separately: the forced walk is the same command
without the "no Python file changed" short-circuit, and it already fails in its
first phase, which the unforced walk also runs.

Independent state checks: the umbrella digest `239b4aeb…` is unchanged, and the
validation-state comparison is `acceptable: true` with no tracked or untracked
differences and only the ignored `a.ghog.log` changed. The pre-existing unstaged
transcript modification is the protocol append described in finding 1; it was
present before the reviewer's capture and is unchanged by it.

Line-count spot check of the staged Python: every file is at or below 550
physical lines, so the 650 ceiling holds with room; `collector.py` is the
largest at 548.

### Resolved validation set and sources for step 2 shared-wait-service (exchange 1) (round 1)

The request's five resolved commands and the current resolver set agree:

1. `ghog day` (project source), run as `ghog day --force` so no short-circuit
   could skip it.
2. `ghog single` over the plan's `test_prototype_tdd.py` and
   `test_telemetry_tdd.py` (plan source).
3. The plan's `rg` contract search over `tools/wait_evidence` and the probe
   results (plan source), run with the harness ripgrep search because `rg` is
   not on the tool shell's PATH.
4. `git diff --cached --check` (request source).
5. `ghog single` over `test_claude_continuation_tdd.py`, the B1 regression
   (request source).

### Resolver drift and direction for step 2 shared-wait-service (exchange 1) (round 1)

None. The request adds two request-sourced commands to the plan's set, which the
reviewer ran. The only environment substitution is the harness ripgrep search
in place of the unavailable `rg` binary.

### Repository state around validation for step 2 shared-wait-service (exchange 1) (round 1)

- The request-time index tree `98120e08a2e01e8cea3edcdfaf9d10e8119ea7bf`
  matched the live index at entry, and the assessed tree is identical because
  the reviewer staged nothing.
- The umbrella digest `239b4aeb…` is unchanged.
- Validation-state comparison over the 50 staged paths plus the transcript and
  `a.ghog.log`: `acceptable: true`, no tracked or untracked differences, only
  the ignored Groundhog log changed.
- One pre-existing unstaged tracked change exists:
  `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`, the protocol
  transcript this exchange appends to. It is not a validation side effect, but
  its content currently fails the repository Markdown gate (finding 1), and it
  is not covered by any `a.commit` group.

### Repair inventory for step 2 shared-wait-service (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 shared-wait-service (exchange 1) (round 1)

The independent `commit-plan-check.bat --format json` rerun returned status 0,
`state: valid`, `ready: true`, no diagnostics, and five groups covering all 50
staged paths: the framing dependency, the adapters and prototype, the
human-operated session preparation, the retained trial evidence, and the Step 2
validation rows. Membership, order, scope and conventional subjects match the
staged work, and the Group 2 body correctly separates functional wake from
accounting.

Two points for the regrouping after the rework:

- The transcript `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md` is
  tracked, modified and in no group. Step 1 committed it in its own
  documentation group, so this step needs the same treatment once finding 1 is
  fixed, or the change will be swept into an unrelated later commit.
- The Group 2 body records "39 focused checks and 3198 full tests at 100%
  configured coverage". That walk predates this request's publication and the
  Markdown failure it introduced. After the rerun, keep the recorded numbers
  equal to the walk that actually covers the committed state.

`a.commit` needs no membership change for the current staged set, so the
reviewer did not amend it.

### Findings and boundaries for step 2 shared-wait-service (exchange 1) (round 1)

Unresolved findings:

1. **`ghog day` fails in the received state: the Markdown gate rejects this
exchange's transcript.** My forced walk stopped in the check phase with
`markdown(1)`, before any test ran:
`docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md:1302 MD001: heading level 5 skips level 4`,
plus `MD050` at lines 1327, 1329, 1340, 1383 and 1399.
The cause is this round's own request content, appended unstaged: the
`Staged paths for step 2` heading lands at level 5 under a level-3 section,
and path lines such as
`- tests/unit/tools/wait_evidence/test_prototype/__init__.py` are not
backticked, so `__init__` parses as strong emphasis with underscores. The
writer's green walk predates that publication, which is why it was not seen.
Fix the appended transcript text (backtick every path and author the
sub-heading one level shallower), rerun `ghog day`, and author future round
content the same way.
2. **The added `wsproto` dependency contradicts the plan and is unrecorded.**
`pyproject.toml` gains `wsproto>=1.3.2` and `uv.lock` gains `wsproto 1.3.2`
and `h11 0.16.0`, for the Codex proxy's WebSocket framing. The plan's
"Confirmed code and test facts" still says "No new dependency or coverage
exclusion is planned: use standard-library SQLite/ctypes and the existing
watchdog dependency", and the Step 2 validation rows do not mention the
dependency at all. Record the change where a later reader will find it:
update that plan fact (the plan is already being amended in this step) and
state in the Step 2 validation rows what the dependency is for, that it is
development-only, and why stdlib framing was not used.
3. **Two docs-side probe scripts lack the `# eof` sentinel.**
`docs/v0.13.0/claude-probe.shared-wait-service.py` ends with `main())` and
`docs/v0.13.0/claude-probe-state.shared-wait-service.py` ends with a dict
literal. Their siblings `probe.shared-wait-service.py`,
`codex-tabs.shared-wait-service.py` and Step 1's
`collect.shared-wait-service.py` all end with `# eof`. The repository EOF
check scans only `src` and `tools`, so the gate does not catch this.

Boundary-crossing work:

The A-arm initial-yield deviation is retained in all three Claude A trials and
in Codex A1, where the host applied a 10,000 ms minimum. That is the plan's
"otherwise its supported minimum" path, and the audits keep the limitation
visible; no further Step 2 work is implied.
Pair 1 mixes the original and repaired observer revisions across the series
while keeping both arms of each pair on one revision. The report already
labels the all-pair aggregate descriptive. If item 8 wants three pairs on one
revision, that belongs to its own comparison, not to Step 2.
The four Step 1 notes remain open for their owning items: classic-arm
consumption semantics, later-series drain bounds, published token-inclusion
semantics, and an explicit functional-wake field separate from coverage.

### Human guidance response for step 2 shared-wait-service (exchange 1) (round 1)

Human guidance:

The user asks: "If step 2 is complete, shouldn't you request a review? And is
'quota saving' proof part of step 2?"

Review the actual acceptance requirements and the completion assessment.
Distinguish required measured evidence from a claim of quota or billing savings.
This instruction authorizes review; it does not authorize a commit.

Guidance response:

The guidance asks two questions.

**"If step 2 is complete, shouldn't you request a review?"** Yes, and that is
what this exchange is. The commit gate belongs after an independent code review
of the staged step, so withdrawing the earlier commit menu and publishing this
request was the right move. This answer is advisory; the commit decision stays
with the human.

**"Is 'quota saving' proof part of step 2?"** No. The writer's reading is
correct, and the evidence follows it:

- SW-09 and AC-15 require matched A versus B-prototype trials with reported
  overhead and deltas. They set no minimum net token saving, and the
  consolidated Q04 answer states that an unfavourable end-to-end delta is a
  reported result, not a failed criterion.
- SW-11 requires exact counts, phases, coverage confidence and limitations, and
  forbids inferring billing or quota savings from token counts.
- AC-02 and the consolidated Q02 answer keep strict zero-inference separate
  from functional wake, and leave it open when request coverage is unverifiable.

What Step 2 owed was the functional native-wake evidence, the matched trials
with their failures and deviations retained, and honest coverage limits. The
retained results label every comparison descriptive, keep request-attempt
coverage unknown, and state that no quota or billing conclusion follows. That
is the correct scope. The strict no-inference proof and the A versus B-service
comparison remain umbrella item 8 obligations, not Step 2 work.

This guidance does not change the disposition: a mandatory validation command
currently fails in the received state, so the findings must be resolved first.

### Writer instructions for step 2 shared-wait-service (exchange 1) (round 1)

1. Fix the transcript content that fails the Markdown gate in
   `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`: backtick every
   path in the round 1 staged-path list and in the group listings, and author
   the `Staged paths for step 2` sub-heading one level shallower so no heading
   level is skipped. Then rerun `ghog day` and confirm the check phase passes.
   Author the next round's change summary the same way.
2. Record the `wsproto` dependency. Update the plan's "Confirmed code and test
   facts" line that still says no new dependency is planned, and add to the
   Step 2 validation rows what `wsproto` is for, that it is a development
   dependency, and why stdlib framing was not used.
3. Add the `# eof` sentinel to
   `docs/v0.13.0/claude-probe.shared-wait-service.py` and
   `docs/v0.13.0/claude-probe-state.shared-wait-service.py`, matching their
   siblings.
4. Regroup `a.commit` so the transcript change has a group, and keep the
   recorded walk numbers equal to the rerun that covers the committed state.

Do not rerun or reseed any measured conversation. Every finding is a document
or packaging fix; the retained trials, audits and frozen snapshots stay exactly
as they are.

### Decision rationale for step 2 shared-wait-service (exchange 1) (round 1)

Decision: `changes-requested`.

Readiness floor:

1. **Identity: pass.** Envelope, human-readable identity, plan, step 2, round 1,
   occurrence 1 and request index tree agree.
2. **Completeness: pass.** Implementation-check is Yes for the step's code and
   live evidence.
3. **Validation and coverage: fail.** `ghog day --force` exits 1 in the check
   phase on the Markdown gate, so no test or coverage phase ran in the received
   state. The two focused gates and `git diff --cached --check` pass.
4. **Staged attribution: pass.** The staged set equals the request's 50 paths,
   and the reviewer staged nothing.
5. **Unresolved findings: fail.** Three findings: the failing Markdown gate, the
   unrecorded `wsproto` dependency, and two missing `# eof` sentinels.
6. **`a.commit`: pass mechanically.** Status 0 with no diagnostics; membership
   and subjects match. The transcript still needs a group after the fix.

The reviewer made no repair, so nothing here is a substantive reviewer change.
All three findings are document or packaging fixes that leave every measured
trial untouched. This answer is advisory and authorizes no commit.

### Final reviewer decision for step 2 shared-wait-service (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-09-17T13:34:08+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: request

### Review identity for step 2 shared-wait-service (round 2)

Umbrella draft: docs/v0.13.0/draft.v0.13.0.no_polling.md
Implementation plan: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 shared-wait-service (round 2)

request_index_tree: 6a8f2fbb7a46e46421c5e638b6b029ad2cc862e6
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py (sources: plan)
- rg -n 'normal.end|WAIT_TEST_DONE|B-prototype|inconclusive' tools/wait_evidence docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md (sources: plan)
- git diff --cached --check (sources: request)
- ghog single tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py (sources: request)

commit_plan_result:

```text
state: valid
ready: true
group 1: build(wait-evidence): add WebSocket framing
group 1 path: pyproject.toml
group 1 path: uv.lock
group 2: feat(wait-evidence): probe native idle wake
group 2 path: tools/wait_evidence/__init__.py
group 2 path: tools/wait_evidence/claude_monitor.py
group 2 path: tools/wait_evidence/claude_observer.py
group 2 path: tools/wait_evidence/codex_proxy.py
group 2 path: tools/wait_evidence/collector.py
group 2 path: tools/wait_evidence/models.py
group 2 path: tools/wait_evidence/probe_cli.py
group 2 path: tools/wait_evidence/probe_driver.py
group 2 path: tools/wait_evidence/probe_files.py
group 2 path: tools/wait_evidence/probe_observer.py
group 2 path: tools/wait_evidence/prototype.py
group 2 path: tools/wait_evidence/telemetry.py
group 2 path: tools/wait_evidence/telemetry_claude.py
group 2 path: docs/v0.13.0/probe.shared-wait-service.py
group 2 path: tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/__init__.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py
group 2 path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
group 3: feat(wait-probe): prepare measured TUI sessions
group 3 path: docs/v0.13.0/claude-probe-state.shared-wait-service.py
group 3 path: docs/v0.13.0/claude-probe.shared-wait-service.py
group 3 path: docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/claude-tabs.shared-wait-service.ps1
group 3 path: docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/codex-tabs.shared-wait-service.ps1
group 3 path: docs/v0.13.0/codex-tabs.shared-wait-service.py
group 3 path: docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md
group 3 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
group 3 path: docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md
group 4: docs(wait-probe): retain matched trial evidence
group 4 path: docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json
group 4 path: docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
group 5: docs(shared-wait-service): record step 2 code review
group 5 path: docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md
group 6: docs(shared-wait-service): record step 2 validation
group 6 path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/claude-probe-state.shared-wait-service.py
staged path: docs/v0.13.0/claude-probe.shared-wait-service.py
staged path: docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/claude-tabs.shared-wait-service.ps1
staged path: docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/codex-tabs.shared-wait-service.ps1
staged path: docs/v0.13.0/codex-tabs.shared-wait-service.py
staged path: docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md
staged path: docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json
staged path: docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/probe.shared-wait-service.py
staged path: docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md
staged path: docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md
staged path: pyproject.toml
staged path: tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py
staged path: tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/__init__.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py
staged path: tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py
staged path: tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py
staged path: tools/wait_evidence/__init__.py
staged path: tools/wait_evidence/claude_monitor.py
staged path: tools/wait_evidence/claude_observer.py
staged path: tools/wait_evidence/codex_proxy.py
staged path: tools/wait_evidence/collector.py
staged path: tools/wait_evidence/models.py
staged path: tools/wait_evidence/probe_cli.py
staged path: tools/wait_evidence/probe_driver.py
staged path: tools/wait_evidence/probe_files.py
staged path: tools/wait_evidence/probe_observer.py
staged path: tools/wait_evidence/prototype.py
staged path: tools/wait_evidence/telemetry.py
staged path: tools/wait_evidence/telemetry_claude.py
staged path: uv.lock
```

### Requestor assessment for step 2 shared-wait-service (round 2)

Writer assessment: Step 2 is fully implemented, subject to independent code review.
The matching validation section records code completion and live-evidence
completion separately. Steps 3 through 8 remain unimplemented; umbrella item 1
is not being closed by this review.

Validation evidence:

- The exact Claude B1 continuation rejection was reproduced red, then the
  repaired implementation passed 39 focused checks, 10 affected checks and
  all 3,198 full tests with 100% configured coverage, zero failures, warnings
  or xfails. The final walk ended 2026-09-17T07:47:09Z, state=done exit=0.
- Retained full log: a.shared-wait-service/ghog-claude-continuation-green.log,
  SHA-256 4d6d9429b582533b23683f2cde4b5f1805f8c34fb98397b594688bb30eac0b3b.
  Related red and focused logs share that directory and prefix.
- Groundhog owns the static-check, affected-test and coverage gates. Coverage
  is the configured tools scope, with pyproject exclusions; it is not a claim
  of measured coverage for docs-side scripts or every repository file.
- The implementation inventory counted all 30 changed Python files at or
  below 650 physical lines, including tests and initializers, and checked EOF
  markers and references. collector.py has 548 lines; claude_observer.py 388.
  Evidence: a.shared-wait-service/step2-code-inventory.json and the validation
  document's architecture, performance, coverage and feature-integrity sections.
- The isolated prototype uses durable identities, native gates, external
  observers and bounded timers. It does not replace current review/Groundhog
  workflows or implement the later shared service.
- Both hosts have retained controlled baselines and three paired trials.
  Claude B1 remains failed; B2 and B3 passed after the additive validated
  monitor-completion-01 revision. All A trials retain the initial-yield
  limitation. Codex B2's observer recovery and earlier failures remain visible.
- Claude final audit 2026-09-17T09:11:59.194Z passed all aggregate and per-run
  integrity checks. Closure at 09:12:14.715Z verified all original session
  identities, unchanged stream hashes and completed observers. All seven
  Claude tabs may close. No measured trial was retried or reseeded.
- Immediately before review rendering, git diff --cached --check passed and
  commit-plan-check reported ready=true, state=valid, diagnostics=[], with
  all 51 staged paths covered by six groups.

Round 1 added the missing Claude median/range and explicit count
summary, computed from the existing exported deltas. This documentation-only
addition preserves raw evidence and production code. The full code validation
above predates that report addition; the review's resolved checks remain due.

Acceptance distinction: SW-09 and AC-15 impose no minimum net token-savings
threshold. SW-11 requires observed counts/deltas, aggregates and limitations,
and forbids inferring billing or quota savings from token counts. Functional
wake is observed; complete request coverage and strict-idle support remain
unknown. The strict no-inference and fresh A/B-service obligations belong to
umbrella item 8, not this effort's local Step 8.

Round 1 independently confirmed that Step 2 is fully implemented and quota savings are not an acceptance threshold. Its changes-requested disposition concerned the transcript Markdown gate, dependency documentation and two docs-side EOF sentinels. All three are accepted and repaired; the transcript has its own commit group. The new validation evidence below supersedes the pre-publication walk for current review readiness, while that earlier frozen log remains evidence for the measured implementation.

Fresh repair validation: ghog day --force passed all static checks (including
Markdown), affected tests and all 3,198 full tests, with fail=0 warn=0 xfail=0
cov=100 exit=0, ending 2026-09-17T13:32:15+02:00. Retained log:
.reviews/a.step2-r1-repair-ghog.log, SHA-256
9919dc025ad161de51f243622e5bc5666ee48b5934c8bb1f2d029f0923e45f73.
commit-plan-check passes with 51 staged paths in six groups and no diagnostics.
The validation document now records this result; round 2's resolved checks
must also validate the new protocol append and this evidence-recording update.

### Implementation report for step 2 shared-wait-service (round 2)

The Step 2 harness now freezes full seeds, reserves exact fresh identities,
enforces READY/context/manifest gates and serial measurements, and persists
registration, source readiness, native delivery and one consumption. The
standalone probe entry point works independently of cwd.

Codex proxy framing and Claude Monitor adapters bind the exact original
conversation. Native transcript normalization keeps request-attempt coverage
unknown when the installed schema cannot establish it. Independent ordinary
processes collect evidence and enforce separate source, wake, duplicate and
drain intervals.

The Claude repair accepts the verified completed-task notification only when
its ancestry, task and Monitor call match the ready notification. It rejects
ambiguous, duplicate or unrelated notices and never rewrites native UUIDs.
Regression tests cover that boundary and lifecycle/transport/parser behavior.

Human-invoked named-tab launchers and run procedures prepare fresh measured
sessions with frozen seeds. The implementing session does not substitute for
a measured TUI. The user submitted all Claude benchmark prompts after readiness.

Versioned results and redacted selected exports retain configuration, hashes,
timings, original failures, per-pair usage and the final integrity audit. Raw
evidence remains local under a.shared-wait-service, including the immutable
claude-controlled-20260917 series and additive implementation revision.

Review focus:

- Check lifecycle suppression, exact native session/turn/task binding,
  startup/readiness races, restart behavior and duplicate consumption.
- Verify the completed Step 2 assessment against AC-02/14/15 and SW-08..11,
  including the failed B1 case and qualified A protocol observations.
- Check descriptive aggregate calculations and denominators, phase attribution,
  known gaps and explicit absence of strict-idle or quota-savings claims.
- Check public exports for appropriate redaction and consistent raw hashes.
- Assess staged scope and the five-group a.commit before recommending readiness.

Do not rerun measured conversations, reseed, alter frozen snapshots, or
overwrite original audits. Read-only audit inspection and deterministic tests
are sufficient to review retained measurements. Any proposed fresh experiment
must preserve every existing trial and its classification.

### Change summary for step 2 shared-wait-service (round 2)

All 51 current staged paths are covered by root a.commit in six groups.

Staged paths:

- `docs/v0.13.0/claude-probe-state.shared-wait-service.py`
- `docs/v0.13.0/claude-probe.shared-wait-service.py`
- `docs/v0.13.0/claude-smoke.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/claude-tabs.shared-wait-service.ps1`
- `docs/v0.13.0/claude-tabs.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/codex-tabs.shared-wait-service.ps1`
- `docs/v0.13.0/codex-tabs.shared-wait-service.py`
- `docs/v0.13.0/codex-tabs.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/handoff.v0.13.0.claude-timed-tests.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`
- `docs/v0.13.0/probe-claude-capability.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-controlled.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-resume.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-seeds.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-series-audit.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-claude-smoke.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-controlled.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-manifests.v0.13.0.shared-wait-service.json`
- `docs/v0.13.0/probe-results.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/probe.shared-wait-service.py`
- `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/seed-procedure.v0.13.0.shared-wait-service.md`
- `pyproject.toml`
- `tests/unit/tools/wait_evidence/test_codex_proxy/__init__.py`
- `tests/unit/tools/wait_evidence/test_codex_proxy/test_codex_proxy_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/__init__.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_lifecycle_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_claude_observer_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_driver_edges_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_native_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_observer_tdd.py`
- `tests/unit/tools/wait_evidence/test_prototype/test_prototype_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_claude273_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_native_binding_tdd.py`
- `tests/unit/tools/wait_evidence/test_telemetry/test_telemetry_tdd.py`
- `tools/wait_evidence/__init__.py`
- `tools/wait_evidence/claude_monitor.py`
- `tools/wait_evidence/claude_observer.py`
- `tools/wait_evidence/codex_proxy.py`
- `tools/wait_evidence/collector.py`
- `tools/wait_evidence/models.py`
- `tools/wait_evidence/probe_cli.py`
- `tools/wait_evidence/probe_driver.py`
- `tools/wait_evidence/probe_files.py`
- `tools/wait_evidence/probe_observer.py`
- `tools/wait_evidence/prototype.py`
- `tools/wait_evidence/telemetry.py`
- `tools/wait_evidence/telemetry_claude.py`
- `uv.lock`

Ordered commit groups:

- `build(wait-evidence): add WebSocket framing`
- `feat(wait-evidence): probe native idle wake`
- `feat(wait-probe): prepare measured TUI sessions`
- `docs(wait-probe): retain matched trial evidence`
- `docs(shared-wait-service): record step 2 code review`
- `docs(shared-wait-service): record step 2 validation`

### Human guidance and writer response for step 2 shared-wait-service (round 2)

Human guidance:

The user asks: "If step 2 is complete, shouldn't you request a review? And is
'quota saving' proof part of step 2?"

Review the actual acceptance requirements and the completion assessment.
Distinguish required measured evidence from a claim of quota or billing savings.
This instruction authorizes review; it does not authorize a commit.

Writer response:

All three round-1 findings are accepted. No disagreement and no reviewer
repair reversal occurred; the reviewer had staged no changes.

1. Corrected the two skipped-level request headings in the versioned transcript
   and quoted all 96 authored path/command lines from that request. The
   findings, decisions and review identities are unchanged. Future change
   summaries use plain labels, quoted paths and concise commit subjects, so
   neither nested a.commit headings nor bare initializer names recur.
2. Updated the plan's stale no-new-dependency fact and the Step 2 validation
   section. They now explain development-only wsproto 1.3.2 and its locked
   h11 dependency, native Codex WebSocket framing, the absence of a standard
   library framing implementation, and avoidance of a separate frame parser.
3. Added # eof to both docs-side Claude probe Python scripts. No executable
   behavior changed; all existing measurements and frozen snapshots are intact.

Writer-repaired paths:

- `docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.md`
- `docs/v0.13.0/plan.v0.13.0.shared-wait-service.validation.md`
- `docs/v0.13.0/claude-probe.shared-wait-service.py`
- `docs/v0.13.0/claude-probe-state.shared-wait-service.py`

The root ignored a.commit now has a separate transcript group before the final
Step 2 validation group, covering 51 staged paths in six groups. Grouping
changed, so a replacement review round is required even though executable
behavior did not change. No commit has been authorized or performed.

### Reviewer focus for step 2 shared-wait-service (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-09-17T13:42:24+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 shared-wait-service (exchange 1) (round 2)

Baseline index tree: 6a8f2fbb7a46e46421c5e638b6b029ad2cc862e6

Assessed index tree: 6a8f2fbb7a46e46421c5e638b6b029ad2cc862e6

### Implementation check for step 2 shared-wait-service (exchange 1) (round 2)

Result:

Reviewer implementation-check result: **Yes. Step 2 has been fully implemented.**

Round 1's three findings are all repaired, verified against the staged state:

1. **Transcript Markdown.** The `Staged paths for step 2` sub-heading is now
   `####`, so no level is skipped, and every path in the appended round 1
   content is backticked. My forced walk's check phase now reports
   `Markdown check passed`.
2. **Dependency recorded.** The plan's "Confirmed code and test facts" no longer
   claims that no dependency is added; it names the development-only
   `wsproto>=1.3.2` and its locked `h11` for the native Codex proxy's WebSocket
   framing. The Step 2 validation rows repeat that, with the coverage scope
   unchanged.
3. **`# eof` sentinels.** Both `claude-probe.shared-wait-service.py` and
   `claude-probe-state.shared-wait-service.py` now end with the marker, like
   their siblings.

The requestor also gave the exchange transcript its own commit group, so the
tracked protocol artifact is no longer left out of the plan.

Everything I confirmed in round 1 still holds:

- The prototype keeps durable identities, one delivery attempt and single
  consumption; host I/O stays outside the write transaction.
- The driver freezes both drafts from the recorded seed commit and enforces
  ordering and the 5% context gate.
- The observers bind native normal end to the exact registering turn and keep
  full duplicate and separate drain windows.
- The telemetry adapters accept only the inspected Codex 0.154.0 and Claude
  2.1.272/2.1.273 shapes and keep request completeness unknown.
- The B1 repair accepts a completed-task notice only with matching parent,
  task, Monitor call and completed status, with a duplicate notice failing the
  run.
- The retained evidence carries a ten-minute baseline per host, three pairs per
  host in A/B, B/A, A/B order, and every failure and deviation, including the
  failed Claude B1 and the initial-yield deviations.
- No strict-idle, quota or billing conclusion is claimed anywhere.

Architecture, performance and coverage are unchanged from round 1: the probe
stays out of the shared service and existing workflows, accounting stays
linear, and the configured `tools` gate is at 100%. Nothing needs fixing, and
nothing needs addressing.

Validation plan effects:

No reviewer edit. The writer's staged Step 2 rows record the Yes status, both
completion components, the architecture, performance, coverage and
feature-integrity sections, the retained failures and deviations, and now the
added development-only dependency and the fresh repair walk. They match what I
checked. Validation-state comparison shows no tracked difference, so the
reviewer left the validation plan and every other tracked file untouched.

### Pre-repair mandatory checks and coverage for step 2 shared-wait-service (exchange 1) (round 2)

All commands ran against request index tree
`6a8f2fbb7a46e46421c5e638b6b029ad2cc862e6`; the reviewer changed nothing.

| Command | Result |
| --- | --- |
| `ghog single` over the plan's two named leaves | exit 0; `fail=0 warn=0 xfail=0` |
| `ghog single tests/unit/tools/wait_evidence/test_prototype/test_claude_continuation_tdd.py` | exit 0; `fail=0 warn=0 xfail=0` |
| `ghog day --force` | exit 0. Check phase passed ty, pyright, ruff, radon, vulture, big-file (650), **Markdown**, ShellCheck and EOF; `ghog full done fail=0 warn=0 xfail=0 cov=100`; started 13:36:02 local |
| `git diff --cached --check` | exit 0 |
| `rg -n 'normal.end\|WAIT_TEST_DONE\|B-prototype\|inconclusive' tools/wait_evidence docs/...probe-results...md` | Run through the harness ripgrep search because `rg` is not on the tool shell's PATH: 51 matches across 10 modules |

The round 1 blocking failure is gone: the Markdown gate that rejected the
transcript now passes in the received state, and the walk reached its test and
coverage phases.

Independent state checks: the umbrella digest `239b4aeb…` is unchanged, and the
validation-state comparison over the 51 staged paths plus the transcript is
`acceptable: true`, with no tracked or untracked differences and only the
ignored `a.ghog.log` changed.

### Resolved validation set and sources for step 2 shared-wait-service (exchange 1) (round 2)

The request's five resolved commands and the current resolver set agree:

1. `ghog day` (project source), run as `ghog day --force` so no short-circuit
   could skip it.
2. `ghog single` over the plan's `test_prototype_tdd.py` and
   `test_telemetry_tdd.py` (plan source).
3. The plan's `rg` contract search over `tools/wait_evidence` and the probe
   results (plan source), run with the harness ripgrep search because `rg` is
   not on the tool shell's PATH.
4. `git diff --cached --check` (request source).
5. `ghog single` over `test_claude_continuation_tdd.py`, the B1 regression
   (request source).

### Resolver drift and direction for step 2 shared-wait-service (exchange 1) (round 2)

None. The request adds two request-sourced commands to the plan's set, which the
reviewer ran. The only environment substitution is the harness ripgrep search
in place of the unavailable `rg` binary.

### Repository state around validation for step 2 shared-wait-service (exchange 1) (round 2)

- The request-time index tree `6a8f2fbb7a46e46421c5e638b6b029ad2cc862e6`
  matched the live index at entry, and the assessed tree is identical because
  the reviewer staged nothing.
- The umbrella digest `239b4aeb…` is unchanged.
- Validation-state comparison over the 51 staged paths plus the transcript:
  `acceptable: true`, no tracked or untracked differences, only the ignored
  `a.ghog.log` changed.
- The transcript's remaining unstaged content is this exchange's own protocol
  append. It is covered by the new commit group and no longer breaks the
  Markdown gate.

### Repair inventory for step 2 shared-wait-service (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 shared-wait-service (exchange 1) (round 2)

The independent `commit-plan-check.bat --format json` rerun returned status 0,
`state: valid`, `ready: true`, no diagnostics, and six groups covering all 51
staged paths: the framing dependency, the adapters and prototype, the
human-operated session preparation, the retained trial evidence, the
independent review record, and the Step 2 validation rows.

Both round 1 points are addressed. The transcript
`docs/v0.13.0/review.code.v0.13.0.shared-wait-service.md` now has its own group,
and the recorded walk evidence points at the fresh repair run rather than only
the pre-publication one. Membership, order, scope and conventional subjects
match the staged work, so `a.commit` is accurate and the reviewer did not amend
it.

### Findings and boundaries for step 2 shared-wait-service (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 shared-wait-service (exchange 1) (round 2)

No rework is required for Step 2. Present the advisory commit-ready result at
the commit gate. If the human selects Commit, run the reviewed six-group
`a.commit` through the owning workflow.

Two notes for the next steps, not for this one:

- Author every future round's change summary with backticked paths and without
  skipping heading levels, so the transcript keeps passing the Markdown gate.
- Step 3 starts the durable service core. The Step 1 notes still stand for their
  owning items: classic-arm consumption semantics, later-series drain bounds,
  published token-inclusion semantics, and an explicit functional-wake field
  separate from coverage.

### Decision rationale for step 2 shared-wait-service (exchange 1) (round 2)

Decision: `commit-ready` (advisory).

Readiness floor:

1. **Identity: pass.** Envelope, human-readable identity, plan, step 2, round 2,
   occurrence 1 and request index tree agree.
2. **Completeness: pass.** Implementation-check is Yes; all three round 1
   findings are repaired.
3. **Validation and coverage: pass.** `ghog day --force` now passes every static
   check, including Markdown, with `fail=0 warn=0 xfail=0 cov=100`. Both focused
   gates and `git diff --cached --check` pass.
4. **Staged attribution: pass.** The staged set equals the request's 51 paths,
   and the reviewer staged nothing.
5. **Unresolved findings: pass.** None are current or carried.
6. **`a.commit`: pass.** Status 0 with no diagnostics, six groups, accurate
   membership and bodies.

This round made no reviewer repair. The recommendation is advisory and never
authorizes a commit; the commit choice belongs to the human at the convergence
gate.

### Final reviewer decision for step 2 shared-wait-service (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-09-17T14:07:01+02:00
- Exchange: code/code/v0.13.0/shared-wait-service
- Umbrella: docs/v0.13.0/draft.v0.13.0.no_polling.md
- Reviewed document: docs/v0.13.0/plan.v0.13.0.shared-wait-service.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
