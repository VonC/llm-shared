# v0.3.0 duration_outliers_exclusion implementation tracking and validation

No, it is not implemented.

This document tracks, step by step, the build of the tool-managed `[exclusion]` section against [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). Nothing is built yet: the `exclusions.py` module, the rule post-step, the report block, the closing-line field, the `ghog` add-exclusion command and the guidance updates are all absent. Each step's evidence is filled at its implementation check.

---

## File-based IO cost clarification for v0.3.0 exclusions (implementation)

The exclusion read and write must stay a tiny, bounded file operation, as the plan requires:

- the `[exclusion]` section is a handful of lines read once per `ghog full` run, beside the two floor lines.
- the write is one atomic side-file replace per run, the pattern `floor.py` already uses.
- no extra file is added: the section lives inside `a.ghog.outliers`.
- the reader and writer never scan the whole repository or any coverage export.

---

## Complexity bound clarification for v0.3.0 exclusions (implementation)

The scaling target for the exclusion code paths is:

- **O(1) amortized per excluded entry**: spare, classify and the ratchet/remove decision are a constant-cost lookup per entry.
- **O(n) total per run**: one pass over the run's call map and the exclusion map, no sort beyond the v0.2.0 rule's existing one.

Every implemented step is reviewed against this bound in its Performance check section.

---

## Step 1. Read and write the exclusion section

### Analysis of Step 1 implementation state

Not started. Step 1 is not implemented because `tools/groundhog/exclusions.py` does not exist yet.

The reader and writer of the `[exclusion]` section are absent; `a.ghog.outliers` carries only its two floor lines.

### Goal for Step 1

Add a function-style `tools/groundhog/exclusions.py` that reads the `[exclusion]` section into a `node -> recorded seconds` map and writes it back -- adding an entry, lowering a baseline, removing a below-floor or stale entry -- while leaving `floor.py`'s two-line read untouched.

### Step 1 improvement expectations

- `read_exclusions(root)` returns the `node -> recorded seconds` map, `{}` when no section; a missing, partial, malformed or binary file reads as `{}`, and a malformed entry, a blank line, or text before the `[exclusion]` header is skipped without raising.
- the write path adds an entry, lowers a baseline, and removes a below-floor or stale entry, preserving the floor lines (1 and 2), with the atomic side-file replace; a write failure is logged, not raised.
- `floor.py` is unchanged in behaviour and stays at or under its 130-line budget.
- `test_groundhog_exclusions.py` reaches 100% of `exclusions.py`.

### What was implemented for Step 1

To be filled at the implementation check for Step 1.

### New types or classes introduced for Step 1

To be filled at the implementation check for Step 1.

### Architecture check for Step 1

To be filled at the implementation check for Step 1.

### Performance check for Step 1

To be filled at the implementation check for Step 1.

### Unit test coverage check for Step 1

To be filled at the implementation check for Step 1.

### Feature integrity for Step 1

To be filled at the implementation check for Step 1.

---

## Step 2. Spare excluded calls and measure drift

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because the rule post-step does not exist yet.

`durations.summarize` still has no exclusion handling, and `DurationSummary` carries no excluded-call list.

### Goal for Step 2

Add a post-step over `DurationSummary` that spares excluded calls from the outliers and the average and classifies each excluded node against its baseline, leaving `summarize` and its test vectors unchanged.

### Step 2 improvement expectations

- the post-step spares any flagged call whose node is excluded and leaves excluded calls out of the average; the median, MAD and floor are computed over the whole run, unchanged by exclusion; `summarize` is unchanged.
- each excluded entry carries node, recorded, current and a status: `ok` within two seconds, `slower` when `current - recorded > 2s`, `faster` when `recorded - current > 2s`, `stale` when the node ran no call this run.
- the section update lowers a baseline only on a more-than-two-second improvement (Q69) and marks a below-floor or stale entry for removal; a faster reading within two seconds leaves the baseline alone.
- `durations.py` stays pure and under its line budget; the rule reaches 100% coverage.

### What was implemented for Step 2

To be filled at the implementation check for Step 2.

### New types or classes introduced for Step 2

To be filled at the implementation check for Step 2.

### Architecture check for Step 2

To be filled at the implementation check for Step 2.

### Performance check for Step 2

To be filled at the implementation check for Step 2.

### Unit test coverage check for Step 2

To be filled at the implementation check for Step 2.

### Feature integrity for Step 2

To be filled at the implementation check for Step 2.

---

## Step 3. Wire exclusions into the run and the report

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because `durations_summary.py` does not read or write the exclusion section and `durations_report.py` renders no exclusion block.

### Goal for Step 3

Have `durations_summary` read the exclusion map, apply the post-step, and write the section back through `exclusions.py`; have `durations_report` render the exclusion block after the floor window.

### Step 3 improvement expectations

- `durations_summary.py` reads the exclusion map, applies the post-step, then writes the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section.
- the whole exclusion pass forms only on a full run already green on tests and coverage (Q34), so the list is never managed while the suite is failing.
- `durations_report.py` renders, per excluded call, `ok`, the restore instruction when slower, the lowered baseline on a real improvement, or `removed` (below floor or stale), and no block on an empty list.
- `test_groundhog_durations_report.py` covers the four lines and the no-block case.

### What was implemented for Step 3

To be filled at the implementation check for Step 3.

### New types or classes introduced for Step 3

To be filled at the implementation check for Step 3.

### Architecture check for Step 3

To be filled at the implementation check for Step 3.

### Performance check for Step 3

To be filled at the implementation check for Step 3.

### Unit test coverage check for Step 3

To be filled at the implementation check for Step 3.

### Feature integrity for Step 3

To be filled at the implementation check for Step 3.

---

## Step 4. Classify drift, add the exclusion command, and reword the hint

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the closing line carries no `excluded=` field, the exit-8 hint still names line 2, and there is no `ghog` add-exclusion subcommand.

### Goal for Step 4

Drive exit 8 from a slower-drifted exclusion, carry `excluded=` of the slower-drifted calls on the closing line, reword the exit-8 hint to name the `ghog` add-exclusion command, and add that subcommand.

### Step 4 improvement expectations

- a slower-drifted excluded call keeps an otherwise-green run on exit 8; a faster or stale entry is auto-managed and leaves the exit unchanged; an excluded-ok run stays exit 0.
- the closing key=value line carries `excluded=<count>` of slower-drifted calls; `excluded=0` on a clean exclusion list.
- the exit-8 next-step hint names the `ghog` add-exclusion command and `fix_slow_test.md`, not raising line 2.
- a `ghog` add-exclusion subcommand takes the node id and its measured time and writes the entry through `exclusions.py`.

### What was implemented for Step 4

To be filled at the implementation check for Step 4.

### New types or classes introduced for Step 4

To be filled at the implementation check for Step 4.

### Architecture check for Step 4

To be filled at the implementation check for Step 4.

### Performance check for Step 4

To be filled at the implementation check for Step 4.

### Unit test coverage check for Step 4

To be filled at the implementation check for Step 4.

### Feature integrity for Step 4

To be filled at the implementation check for Step 4.

---

## Step 5. Update the fix-slow-test guidance

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because `fix_slow_test.md` and `groundhog.md` still tell a must-stay-slow call to raise line 2.

### Goal for Step 5

Move the must-stay-slow guidance from raising line 2 to running the `ghog` add-exclusion command, in `fix_slow_test.md` and `groundhog.md`.

### Step 5 improvement expectations

- `instructions/fix_slow_test.md` "when a call has to stay slow" tells the LLM to run the `ghog` add-exclusion command with the call's measured time and states the two-second baseline rule, and no longer says raise line 2 or hand-edit the file for one call.
- `instructions/groundhog.md` exit-8 section points a must-stay-slow call at the `ghog` add-exclusion command and describes line 2 as project-wide floor tuning.
- both files follow the markdown rules and carry no blacklisted word.

### What was implemented for Step 5

To be filled at the implementation check for Step 5.

### New types or classes introduced for Step 5

To be filled at the implementation check for Step 5.

### Architecture check for Step 5

To be filled at the implementation check for Step 5.

### Performance check for Step 5

To be filled at the implementation check for Step 5.

### Unit test coverage check for Step 5

To be filled at the implementation check for Step 5.

### Feature integrity for Step 5

To be filled at the implementation check for Step 5.

---

## Step 6. Acceptance tests for excluded and drifted runs

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because the acceptance scenarios for the exclusion states do not exist yet.

### Goal for Step 6

Add acceptance tests that drive a `ghog full` run through the excluded-ok, slower-drift, faster and stale states, and through the `ghog` add-exclusion command.

### Step 6 improvement expectations

- an excluded-call run within tolerance exits 0, reports the call `ok`, and prints no outlier window.
- a slower-drift run exits 8 with the restore instruction and `excluded=1` on the closing line.
- a faster run shows the tool lower the baseline on a more-than-two-second improvement, or remove the entry once below the floor, and stays exit 0; a stale-entry run shows the entry removed and stays exit 0.
- the add-exclusion subcommand writes a new entry with its measured time as the baseline; `test_groundhog_acceptance_durations.py` stays under its line budget.

### What was implemented for Step 6

To be filled at the implementation check for Step 6.

### New types or classes introduced for Step 6

To be filled at the implementation check for Step 6.

### Architecture check for Step 6

To be filled at the implementation check for Step 6.

### Performance check for Step 6

To be filled at the implementation check for Step 6.

### Unit test coverage check for Step 6

To be filled at the implementation check for Step 6.

### Feature integrity for Step 6

To be filled at the implementation check for Step 6.
