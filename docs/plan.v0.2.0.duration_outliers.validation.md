# v0.2.0 duration-outliers implementation tracking and validation

No, it is not implemented.

This document tracks the duration-outliers feature (decisions Q34 to Q47 of
`design.v0.2.0.duration_outliers.md`) step by step against the repository state.
Step 1 (per-call duration capture into `RunStats`) is done; steps 2 to 6 remain,
so there is still no `durations.py` or `floor.py`, no `EXIT_DURATION_OUTLIERS`,
and no outlier output.

---

## File-based IO cost clarification for the duration-outliers feature (implementation)

All implementation work must respect the IO classification from
`plan.v0.2.0.duration_outliers.md`:

- the durations come from the stream the parent already reads, not a second pytest
  or coverage invocation.
- `a.ghog.outliers` is a two-line read at run start, a tiny index-read.
- the floor write at run end uses the atomic side-file replace of `snapshot.py` and
  `status.py`.
- no directory scan is added on any path.

---

## Complexity bound clarification for the duration-outliers feature (implementation)

The scaling target for every reviewed step:

- **O(1) per streamed line**: the duration-line capture is a constant-cost branch.
- **O(n) to O(n log n) once per full run**: median, MAD and the outlier scan over
  the collected test count, one sort at most; no `O(n^2)` path.

Each implemented step is reviewed against this bound in its Performance check.

---

## Step 1. Capture per-call durations into RunStats

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

The full command now adds `--durations=0 --durations-min=0`, the parser captures the
`slowest durations` block into a new call-phase `RunStats.durations` map, and every
non-full run leaves the map empty. The capture opens on its banner and closes on the
next banner, the final summary line included; a parametrized id with spaces is kept
whole. The `ghog day` walk is green in one pass.

### Goal for Step 1

Add pytest's `--durations` output to the full command and parse the
`slowest durations` block into a new call-phase `RunStats.durations` map; non-full
runs stay empty.

### Step 1 improvement expectations

- after a full run, `RunStats.durations` maps each node id to its call seconds.
- the affected and single commands carry no `--durations` flags and produce no map.
- the durations-section capture stops at the next banner and at the final summary.

### What was implemented for Step 1

- **models.py field**: `RunStats` gains `durations: dict[str, float]`, default empty, node id to call-phase seconds; the class docstring records the call-phase-only intent and the empty-on-non-full-run rule (Q36, Q39).
- **runner.py flags**: `pytest_command` appends `--durations=0 --durations-min=0` on the full branch only, gated on `sub == SUB_FULL`; the single command returns early and the affected (covered) command skips the flags, so only the full run is timed (Q39).
- **parser.py capture**: a `_DURATION_RE` regex and a `_feed_durations` step record the call-phase seconds while a `slowest durations` banner is open; the node group is `.+\S`, so a parametrized id holding a space stays whole (Q49); any later banner — the final summary line, itself a banner, included — closes the capture.
- **Tests**: `test_groundhog_parser.py` adds four cases (call-phase-only with setup/teardown skipped and a post-banner line dropped, summary-line close, no-banner empty map, space-bearing parametrized id); `test_groundhog_runner.py` updates the full-command assertion with the two flags and adds a case proving the affected and single commands stay untimed.
- **Validation evidence**: `ghog day` reports `exit=0`, `state=done`, `cov=100`, `fail=0` over 728 tests; `rg "durations" tools/groundhog` finds the field (`models.py:81`), the flags (`runner.py:113`) and the capture (`parser.py:147`).

### New types or classes introduced for Step 1

- No new production class or type. Step 1 is a field, a parser step and a flag branch: `RunStats.durations` (a dataclass field), the `_DURATIONS_TITLE`, `_DURATION_RE` and `_CALL_PHASE` module-level constants of `parser.py`, the private method `PytestOutputParser._feed_durations`, and one `SUB_FULL` branch in `runner.pytest_command`. No new module was added — `durations.py` and `floor.py` belong to Steps 2 and 3.

### Architecture check for Step 1

- **parser layer (output adapter)**: the durations capture sits beside the existing failure-block and coverage-table captures inside `PytestOutputParser`, the streamed-output parsing adapter; it reads text only, writes to `RunStats`, and imports nothing new (`re` was already used). Correct placement.
- **models layer**: `RunStats` stays a plain counter dataclass with no behavior, its imports unchanged; the new field follows the `failed_ids`/`last_started` shape. No rule logic (median, MAD, floor) leaked in — that is held for the pure `durations.py` of Step 2.
- **runner layer**: `pytest_command` only builds an argument list; the `SUB_FULL` gate adds no IO and no computation, so the boundary between command building and the deferred rule module is kept.

No DDD-Hexagonal violation or adapter smell is visible in Step 1. No, there is nothing that needs to be addressed for Step 1.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: the capture is a constant-cost branch per streamed line — one banner match, at most one duration match, one dict insert — the same shape as the coverage-table capture next to it.
- **Hot-path bound**: `_feed_durations` runs once per output line, O(1) amortized; it never scans the accumulated map and never sorts.
- **Startup or background path**: none added; the flag wiring is a constant-time list build done once per run.
- **Plan-bound alignment**: Step 1 only captures; the `O(n log n)` median and MAD work is deferred to Step 2, so this step stays at O(1) per line.

Step 1 stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed for Step 1.

### Unit test coverage check for Step 1

- **`tools/groundhog/parser.py` (`PytestOutputParser`)**: the new `_feed_durations` statements are all reached by the four added parser tests — the banner-open path, the banner-close path (named banner and summary line), the not-capturing early return, the call-phase insert, and the setup/teardown skip. Covered at 100%.
- **`tools/groundhog/runner.py` (`pytest_command`)**: the new `SUB_FULL` branch is reached by the updated full-command test; the not-full path by the affected and single tests. Covered at 100%.
- **`tools/groundhog/models.py` (`RunStats`)**: the `durations` default factory runs on every `RunStats()` construction the parser tests make. Covered at 100%.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: the affected, single and check commands get no `--durations` flags, so their command lines and output parsing are unchanged; `RunStats.durations` defaults empty and nothing downstream reads it yet, so no route or workflow is impaired.
- **Reporting or diagnostics**: the progress lines, closing line, failure block and coverage capture are untouched; the full-run output gains pytest's own `slowest durations` block, captured silently into the map — no visible report yet, which is Step 4's job.
- **Compatibility or rollout note**: the full command appends the two flags after `-v`; the alias-faithful test was updated to match that order. No behavior change reaches the affected, single or check paths.

No existing feature or reporting capability appears impaired by Step 1.

---

## Step 2. The true-outlier rule, the average and the report window

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because there is no `durations.py`: no rule,
no average, no window builder.

### Goal for Step 2

A pure `durations.py` carrying the median, the MAD, the modified z-score, the
`k * median` floor, the two-condition true-outlier rule, the average excluding
outliers and the bounded window line builders, with the MAD-zero fallback.

### Step 2 improvement expectations

- a tidy suite yields zero outliers; one order-of-magnitude freak is the one
  outlier; a two-to-three-times call is not.
- the average excludes outliers; the MAD-zero case stays defined.
- the window holds the flagged outliers, the marked floor, and bounded runners-up.

### What was implemented for Step 2

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 2

(empty.)

### Architecture check for Step 2

(empty.)

### Performance check for Step 2

(empty.)

### Unit test coverage check for Step 2

(empty.)

### Feature integrity for Step 2

(empty.)

---

## Step 3. The two-line floor file

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because there is no `floor.py` and no
`a.ghog.outliers` read/write or active-floor resolution.

### Goal for Step 3

A `floor.py` beside `gate.py` and `snapshot.py` that reads the two-line
`a.ghog.outliers`, resolves the active floor (line 2 when not `-1`, else line 1),
and writes line 1 from the run with line 2 reset to `-1` when the file is absent,
using the atomic side-file replace.

### Step 3 improvement expectations

- a missing file resolves to the auto value with override `-1`.
- a positive line 2 overrides line 1; line 1 is still read.
- the write is atomic and round-trips; a malformed file falls back, never crashing.

### What was implemented for Step 3

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 3

(empty.)

### Architecture check for Step 3

(empty.)

### Performance check for Step 3

(empty.)

### Unit test coverage check for Step 3

(empty.)

### Feature integrity for Step 3

(empty.)

---

## Step 4. Classification, progress output and report wiring

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because there is no `EXIT_DURATION_OUTLIERS`,
`classify` ignores outliers, the progress and closing lines carry no `avg=` or
`outliers=`, and no outlier report is emitted.

### Goal for Step 4

Add the exit-8 code, compute the summary for full runs, classify exit 8 when green
and coverage-clear with outliers remaining, add `avg=`/`outliers=` to the final
line, the bar and the closing line, emit the windowed report on exit 8, and write
the auto floor after the run -- keeping `commands.py` under its budget.

### Step 4 improvement expectations

- a green-but-slow full run exits 8 with the windowed list and the fix instruction.
- a tidy run exits 0 with `outliers=0`; a raised override exits 0.
- a failing or coverage-gap run keeps its own exit code (outliers judged last).
- the final progress line and bar postfix carry `avg=` and `outliers=` for full.

### What was implemented for Step 4

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 4

(empty.)

### Architecture check for Step 4

(empty.)

### Performance check for Step 4

(empty.)

### Unit test coverage check for Step 4

(empty.)

### Feature integrity for Step 4

(empty.)

---

## Step 5. The skill instruction exit-8 branch and LLM fix playbook

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because `instructions/groundhog.md` has no
exit-8 branch and no outlier fix playbook.

### Goal for Step 5

Add an exit-8 branch and the LLM fix playbook to `instructions/groundhog.md`, beside
the exit-2 and exit-3 guidance: fix above-floor outliers only, the per-cause
techniques, the override escape, confirm with `ghog single`, restart with
`ghog day`.

### Step 5 improvement expectations

- on exit 8 the loop reads a concrete fix playbook scoped to above-floor calls.
- the runners-up shown for tuning are explicitly not fix targets.
- the override is named as the alternative for a legitimately slow call.

### What was implemented for Step 5

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 5

(empty.)

### Architecture check for Step 5

(empty.)

### Performance check for Step 5

(empty.)

### Unit test coverage check for Step 5

(empty.)

### Feature integrity for Step 5

(empty.)

---

## Step 6. Acceptance tests for the green-but-slow run

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because there is no end-to-end acceptance
module driving `cli.main` over a transcript with a durations block.

### Goal for Step 6

A new `test_groundhog_acceptance_durations.py` exercising the green-but-slow run and
its variants through the real parser, rule, floor, classification and report.

### Step 6 improvement expectations

- a green-but-slow transcript exits 8, prints the windowed list, writes
  `a.ghog.outliers`, and shows `avg=`/`outliers=`.
- a tidy transcript exits 0; a raised override exits 0; a missing file seeds the
  floor and still reports.
- a failing transcript with a durations block keeps exit 2 (outliers judged last).

### What was implemented for Step 6

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 6

(empty.)

### Architecture check for Step 6

(empty.)

### Performance check for Step 6

(empty.)

### Unit test coverage check for Step 6

(empty.)

### Feature integrity for Step 6

(empty.)
