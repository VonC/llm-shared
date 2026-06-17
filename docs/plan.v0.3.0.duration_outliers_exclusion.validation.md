# v0.3.0 validation plan -- per-test duration exclusions

This is the review checklist for the exclusion feature built from [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). It records, step by step, what to confirm once the work lands. The evidence fields are filled during the implementation-check, not now -- this feature is specified, not yet built.

## Validation goal for the exclusion feature

Confirm, file by file, that `a.ghog.outliers` carries a tool-managed `[exclusion]` section: an excluded call is spared from the outlier rule and the average without moving the floor; a slower-drifted call (more than two seconds over its baseline) drives a fix on exit 8; a faster call has its baseline ratcheted down only on a more-than-two-second improvement and is removed once below the floor; a stale entry is removed; entries are added by a `ghog` command; and the fix-slow-test guidance points at that command instead of the floor. The whole feature must leave `ghog day` green with the new and changed code at 100% coverage. 

## Step 1 validation -- read and write the exclusion section

- `tools/groundhog/exclusions.py` exists, function-style, and `read_exclusions(root)` returns the `node -> recorded seconds` map, `{}` when no section.
- a missing, partial, malformed or binary file reads as `{}`; a malformed entry, a blank line, and any text before the `[exclusion]` header are skipped without raising.
- the write path adds an entry, lowers a baseline, and removes a below-floor or stale entry, preserving the floor lines (1 and 2), with the atomic side-file replace; a write failure is logged not raised.
- `floor.py` is unchanged in behaviour and still at or under its 130-line budget (the reader did not grow it).
- `test_groundhog_exclusions.py` reaches 100% of `exclusions.py`.
- evidence: <ghog day exit, cov, exclusions.py line count, test count -- fill at check>.

## Step 2 validation -- spare excluded calls and classify them

- the post-step spares any flagged call whose node is excluded and leaves excluded calls out of the average; the median, MAD and floor are computed over the whole run, unchanged by exclusion; `summarize` is unchanged.
- each excluded entry carries node, recorded, current and a status: `ok` within two seconds, `slower` when `current - recorded > 2s`, `faster` when `recorded - current > 2s`, `stale` when the node ran no call this run.
- the section update lowers a baseline only on a more-than-two-second improvement (Q69) and marks a below-floor or stale entry for removal; a faster reading within two seconds leaves the baseline alone.
- `durations.py` stays pure (no IO, no floor or report import) and under its line budget.
- `test_groundhog_durations.py` covers spared-above-floor, the four statuses, the beyond-two-second ratchet-down, and the below-floor/stale removals; 100% of the rule.
- evidence: <ghog day exit, cov, durations.py line count -- fill at check>.

## Step 3 validation -- wire exclusions into the run and the report

- `durations_summary.py` reads the exclusion map, applies the post-step, then writes the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section.
- `durations_report.py` renders the exclusion block after the floor window: recorded and current per call, `ok` within tolerance, the restore instruction when slower, the lowered baseline on a real improvement, `removed` when below floor or stale, and no block on an empty list.
- `test_groundhog_durations_report.py` covers the `ok`, slower-restore, lowered-baseline, and removed lines, and the no-block case.
- evidence: <ghog day exit, cov -- fill at check>.

## Step 4 validation -- classify drift, add the command, reword the hint

- a slower-drifted excluded call keeps an otherwise-green run on exit 8; a faster or stale entry is auto-managed (baseline lowered or entry removed) and leaves the exit unchanged; an excluded-ok run stays exit 0.
- the closing key=value line carries `excluded=<count>` of slower-drifted calls; `excluded=0` on a clean exclusion list.
- the exit-8 next-step hint names the `ghog` add-exclusion command and `fix_slow_test.md` for a must-stay-slow call, not raising line 2.
- a `ghog` add-exclusion subcommand takes the node id and its measured time and writes the entry through `exclusions.py`.
- `test_groundhog_reporting.py` and `test_groundhog_cli.py` cover the closing-line field, the reworded hint, the slower-drift-only exit-8 verdict, and the add-exclusion subcommand write.
- evidence: <ghog day exit, cov -- fill at check>.

## Step 5 validation -- update the fix-slow-test guidance

- `instructions/fix_slow_test.md` "when a call has to stay slow" tells the LLM to run the `ghog` add-exclusion command with the call's measured time and states the two-second baseline rule, and no longer says raise line 2 or hand-edit the file for one call.
- `instructions/groundhog.md` exit-8 section points a must-stay-slow call at the `ghog` add-exclusion command and describes line 2 as project-wide floor tuning.
- both files follow the markdown rules and carry no blacklisted word.
- evidence: <links checked, wording confirmed -- fill at check>.

## Step 6 validation -- acceptance tests for the exclusion states

- an excluded-call acceptance run (the freak listed in `[exclusion]` within tolerance) exits 0, reports the call `ok`, and prints no outlier window.
- a slower-drift acceptance run (the freak more than two seconds over its recorded baseline) exits 8 with the restore instruction and `excluded=1` on the closing line.
- a faster acceptance run shows the tool lower the baseline on a more-than-two-second improvement, or remove the entry once below the floor, and stays exit 0; a stale-entry run shows the entry removed and stays exit 0.
- the add-exclusion subcommand writes a new entry, with its measured time as the baseline.
- `test_groundhog_acceptance_durations.py` stays under its line budget after the new scenarios.
- evidence: <ghog day exit, cov, acceptance file line count -- fill at check>.

## Rollout validation for the exclusion feature

- the steps landed in order (read and write, rule, wire and report, classify and command, guidance, acceptance), each followed by a green `ghog day`.
- the final `ghog day` is green: every test passing, coverage at the gate, no outliers and no slower-drifted exclusion.
- the tool wrote only the `[exclusion]` section (added on command, baselines ratcheted down, below-floor and stale entries removed) and left the floor lines (1 and 2) user-owned; a baseline moved up only by re-running the add-exclusion command, never automatically.
- evidence: <final ghog day closing line -- fill at check>.
