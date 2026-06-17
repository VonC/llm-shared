# v0.3.0 implementation plan -- per-test duration exclusions

This plan turns the design in [`design.v0.3.0.duration_outliers_exclusion.md`](design.v0.3.0.duration_outliers_exclusion.md) into file-by-file implementation steps. It carries no design choices -- those are settled in the design (Q53 to Q65 and Q69) -- only what to build and in what order.

## Plan goal for the exclusion feature

Add an `[exclusion]` section to `a.ghog.outliers` so a `ghog full` run spares a named call from the outlier rule whatever the floor, holds each excluded call to its recorded baseline within two seconds, reports the excluded calls, drives a fix when one drifts, and points the fix-slow-test guidance at exclusion instead of raising the floor. The objective is reached when `ghog day` is green (every test passing, coverage at the gate, no outliers and no drifted exclusion) with the feature in place and the new and changed code at 100% coverage.

## Scope anchors for the exclusion plan

- the v0.2.0 floor and rule stay as they are: line 1 the auto reference, line 2 the active floor, the modified-z-and-floor rule. This feature reads more of the file and spares calls after the rule; it does not change the rule's scale.
- the tool manages the exclusion section: it adds an entry on command, ratchets a baseline down on a real improvement, and removes a below-floor or stale entry; only the floor lines (1 and 2) of `a.ghog.outliers` stay user-owned.
- no new exit code: a drifted exclusion reuses exit 8, the otherwise-green duration verdict.
- the instruction guidance moves from "raise line 2" to "run the `ghog` add-exclusion command" only in this feature; until these steps land, the v0.2.0 "raise line 2" wording stands.

## Confirmed technical facts for the exclusion plan

- `a.ghog.outliers` is git-ignored by the existing `a.*` pattern, so the `[exclusion]` section needs no `.gitignore` change.
- the durations parser already keeps a full pytest node id whole (including a parametrized id with spaces), so an exclusion key matches a run's node id directly.
- `floor.py` is at its 130-line budget, so the exclusion reader goes in a new module rather than growing `floor.py`.
- `DurationSummary` is the value object the report renders, so excluded-call data rides on it, keeping the rule pure and the report IO-free.

## Shared execution command for all exclusion steps

Each step is verified by one redirected `ghog day` walk from the project root, as the groundhog loop ([`../instructions/groundhog.md`](../instructions/groundhog.md)) prescribes:

```bat
cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"
```

Never call `check.bat` or `pytest` directly; groundhog owns check and tests.

## Numbered steps for the exclusion feature

### Step 1. Read and write the exclusion section

- `tools/groundhog/exclusions.py` (new): a function-style module beside `floor.py`. `read_exclusions(root) -> dict[str, float]` returns the `node -> recorded seconds` map parsed from the `[exclusion]` section of `a.ghog.outliers`, `{}` when the section is absent. Read the file in `exclusions.py` itself -- its own tolerant read, or importing `floor`'s read helper -- leaving `floor.py` untouched (Q66); a missing, partial or binary file reads as no exclusions. Skip blank lines, lines before the `[exclusion]` header, and any line that is not `node = number`, without raising. Add a write path -- `write_exclusions` (or an update that adds an entry, lowers a baseline to a new time, and removes a below-floor or stale entry) -- preserving the floor lines and using the atomic side-file replace `floor.py` uses, so a write failure is logged not raised.
- `tests/unit/tools/test_groundhog_exclusions.py` (new): the empty map for a file with no section, a parsed map for a well-formed section, a malformed entry skipped, a blank-line and comment skipped, a binary file read as empty; the write path adds, lowers and removes entries, preserves the floor lines, and survives a write failure. Reach 100% of `exclusions.py`.
- update `tools/groundhog/__init__.py` if the package re-exports modules.

### Step 2. Spare excluded calls and measure drift

- `tools/groundhog/durations.py`: leave `summarize` unchanged and add a post-step function (Q67) that takes its `DurationSummary` and the exclusion map and returns a summary with the excluded calls dropped from the outliers and from the average (Q64), plus an excluded-call list. Each entry carries node, recorded, current and a status -- `ok` within two seconds, `slower` when `current - recorded > 2s` (Q63), `faster` (more than two seconds below), `stale` when the node ran no call this run (Q61). The post-step also yields the section update the tool will write: lower a baseline only when the call is more than two seconds below it (Q69), and mark a below-floor or stale entry for removal. Add a `DurationExclusion` value object (node, recorded, current, status) beside the other records in `durations.py` (Q68). Keep the module pure and under its line budget; split a helper out if the budget is at risk.
- `tests/unit/tools/test_groundhog_durations.py`: an excluded call above the floor is spared from `outliers` and left out of the average; the statuses cover `ok`, `slower`, `faster` and `stale`; the update lowers a baseline only on a beyond-two-second improvement and marks below-floor and stale entries for removal; the median, MAD and floor are unchanged by exclusion. Keep `floor.py`-style determinism.

### Step 3. Wire exclusions into the run and the report

- `tools/groundhog/durations_summary.py`: read the exclusion map with `exclusions.read_exclusions(root)` alongside the floor, apply the exclusion post-step (Q67) to its summary, then write the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section.
- `tools/groundhog/durations_report.py`: after the floor window, render the exclusion block -- a header, then one line per excluded call with its recorded and current time, reading `ok`, the restore instruction when slower, the baseline the tool lowered it to, or `removed` (below floor or stale). No block when the run has no exclusions.
- `tests/unit/tools/test_groundhog_durations_report.py`: the block renders an `ok`, a slower-restore, a lowered-baseline and a removed line; no block on an empty exclusion list.

### Step 4. Classify drift, add the exclusion command, and reword the hint

- `tools/groundhog/reporting.py`: a slower-drifted excluded call keeps the run on exit 8 (the same green-but-duration verdict as a flagged outlier); a faster or stale entry is auto-managed by the tool (baseline lowered or entry removed) and never changes the exit; the closing key=value line gains `excluded=<count>` of slower-drifted calls (Q65); the exit-8 next-step hint names the `ghog` add-exclusion command for a must-stay-slow call instead of raising line 2, and points at `fix_slow_test.md`.
- `tools/groundhog/cli.py` and `commands.py`: a `ghog` add-exclusion subcommand taking the node id and its measured time, writing the entry through `exclusions.py` (Q62).
- `tests/unit/tools/test_groundhog_reporting.py` and `test_groundhog_cli.py`: the closing line carries `excluded=`; the exit-8 hint names the add-exclusion command; a slower-drifted exclusion alone yields exit 8; the add-exclusion subcommand writes the entry.

### Step 5. Update the fix-slow-test guidance

- `instructions/fix_slow_test.md`: the "when a call has to stay slow" section becomes "run the `ghog` add-exclusion command with the call's measured time", with the two-second baseline rule; drop the "raise line 2" wording for one call.
- `instructions/groundhog.md`: the exit-8 section's must-stay-slow line points at the `ghog` add-exclusion command, not line 2; line 2 is described as project-wide floor tuning.

### Step 6. Acceptance tests for excluded and drifted runs

- `tests/unit/tools/test_groundhog_acceptance_durations.py`: an excluded-call run where the freak is in the `[exclusion]` section within tolerance exits 0 with the call reported `ok` and no outlier window; a slower-drift run where the freak crept more than two seconds over its recorded baseline exits 8 with the restore instruction and `excluded=1` on the closing line; a faster run shows the tool lower the baseline (or remove the entry once below the floor) and stays exit 0; a stale-entry run shows the entry removed and stays exit 0; the add-exclusion subcommand writes a new entry.

## Rollout sequence for the exclusion plan

Implement the steps in order: Step 1 (read) before Step 2 (rule) before Step 3 (wire and report) before Step 4 (classify) before Step 5 (guidance) and Step 6 (acceptance). After each step, run one `ghog day` walk and fix what it names until green, then move on. The feature is done when the full walk is green with the new code at 100% coverage and the acceptance runs for the excluded-ok, slower-drift, faster and stale cases passing.

## Implementation decisions referenced by the exclusion plan

The design choices this plan carries out are recorded as Q53 to Q65 and Q69 in [`design.v0.3.0.duration_outliers_exclusion.md`](design.v0.3.0.duration_outliers_exclusion.md). The plan's own implementation choices, from the review, are:

| Decision | Step | Why | Alternatives rejected |
| --- | --- | --- | --- |
| Q66 | Step 1 | `exclusions.py` reads and writes `a.ghog.outliers` itself (its own tolerant read and atomic write, or importing `floor`'s helpers), preserving the floor lines; `floor.py` is untouched | one shared read/write through `durations_summary` (changes `floor.py`'s contract and tests for a negligible saving); a new shared IO module (over-structured for a few lines) |
| Q67 | Step 2 | exclusion handling is a post-step over the `DurationSummary`, leaving `summarize` and its many test vectors unchanged | add the exclusion map to `summarize` (touches every call site and test); add it with no default (largest churn) |
| Q68 | Step 2, Step 3 | the `DurationExclusion` record lives beside the other records in `durations.py`; the report block is a named function in `durations_report.py` behind `window_lines` | fold the block inline into `window_lines` (mixes concerns, harder to test); a separate `exclusions_report.py` (a module for a few lines) |
