# v0.2.0 duration-outliers implementation tracking and validation

No, it is not implemented.

This document tracks the duration-outliers feature (decisions Q34 to Q47 of
`design.v0.2.0.duration_outliers.md`) step by step against the repository state.
Nothing is implemented yet: `ghog full` carries no per-call timing, there is no
`durations.py` or `floor.py`, no `EXIT_DURATION_OUTLIERS`, and no outlier output.

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

Not started. Step 1 is not implemented because the parser captures no durations, the
full command carries no `--durations` flags, and `RunStats` has no `durations` field.

### Goal for Step 1

Add pytest's `--durations` output to the full command and parse the
`slowest durations` block into a new call-phase `RunStats.durations` map; non-full
runs stay empty.

### Step 1 improvement expectations

- after a full run, `RunStats.durations` maps each node id to its call seconds.
- the affected and single commands carry no `--durations` flags and produce no map.
- the durations-section capture stops at the next banner and at the final summary.

### What was implemented for Step 1

(empty -- to be filled after the step is implemented.)

### New types or classes introduced for Step 1

(empty.)

### Architecture check for Step 1

(empty.)

### Performance check for Step 1

(empty.)

### Unit test coverage check for Step 1

(empty.)

### Feature integrity for Step 1

(empty.)

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
