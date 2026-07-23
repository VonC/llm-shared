# v0.3.0 design -- per-test duration exclusions in a.ghog.outliers

This design builds on the v0.2.0 duration gate ([`design.v0.2.0.duration_outliers.md`](design.v0.2.0.duration_outliers.md)): a `ghog full` run times each call, the rule flags a call far out by the modified z-score and at or above the floor, and the floor lives in `a.ghog.outliers` -- line 1 the auto `k * median` reference, line 2 the active floor (one second by default). This feature adds a way to accept one call as slow without moving that floor, answering the need in [`feature-request.v0.3.0.duration_outliers_exclusion.md`](feature-request.v0.3.0.duration_outliers_exclusion.md).

## Why the floor cannot accept one call

The floor is one number for the whole suite. Raising line 2 to `12s` to accept an 11.4s integration test means no call under twelve seconds can ever be flagged again, so a test that regresses from 0.2s to 4s sails through. The floor answers "where does an outlier begin for this project"; it cannot also answer "this one call is allowed to be slow" without losing the first meaning. The two needs are separate, so they get separate state: the floor stays global, and an exclusion list names the individual calls that are allowed over it.

## The exclusion section in a.ghog.outliers

`a.ghog.outliers` keeps its first two lines unchanged (Q53): line 1 the auto floor, line 2 the active floor. An optional `[exclusion]` header may follow, and every line after it is one accepted call:

```ini
0.0
1.0
[exclusion]
src/pkg/tests/.../test_auth_setup_tdd.py::TestAuthSetup::test_init_all_writes_hashes = 11.41
src/pkg/tests/.../test_auth_pbt.py::TestAuthPBT::test_only_the_exact_session_cookie = 6.80
```

Each entry is `<node id> = <recorded seconds>`. The node id is the full pytest id, kept whole so a parametrized id with spaces survives, as the durations parser already does. The recorded seconds is the call time at the moment of exclusion -- the baseline the call is later held to.

A reader tolerant of mistakes: the floor lines are read exactly as before (the `[exclusion]` header and everything after it are ignored by the floor reader), and the exclusion reader takes only well-formed `node = number` lines after the header, skipping blank lines, comments and malformed entries without raising. A missing section means no exclusions. So a hand-edit can never crash a run, matching the v0.2.0 floor file's safe-fallback rule.

## Sparing an excluded call

After the v0.2.0 rule computes the outliers of a run, any flagged call whose node id is in the exclusion set is removed from the outlier list (Q54): it was accepted on purpose, so it is spared whatever the floor. Sparing happens after the rule, not before, so the median, the MAD and the floor are still computed over the whole run -- excluding a call changes what is flagged, never the scale the rest of the suite is judged against. An excluded call is also left out of the run average (Q64), the same as an outlier, so one accepted slow call does not lift the suite-wide `avg` the v0.2.0 rule keeps over the non-outlier calls.

The recorded baseline is tool-managed and ratchets only downward (Q55, Q60). When a run times the call more than two seconds faster than its baseline (a real improvement, Q69), the tool lowers the recorded value to that time; once the call drops below the floor the tool removes the entry, handing the call back to the normal rule. A baseline only ever moves back up by re-running the `ghog` add-exclusion command, the escape if a transient fast run lowered it too far. The baseline is never raised -- a call more than two seconds slower is a regression to flag (Q57), not a new baseline -- so a creeping-slower call can never re-baseline away its own drift. The tool also removes a stale entry whose test did not run on the full suite (Q61), and entries are added by a `ghog` command rather than hand-edited (Q62), so the `[exclusion]` section stays accurate without hand upkeep while the floor lines (1 and 2) stay user-owned.

## The two-second baseline tolerance

An excluded call is accepted as slow, not accepted as unbounded, and not accepted as permanent. Each run compares the call's current time to its recorded baseline (Q56), and the comparison is slower-only (Q63): a call within two seconds of its baseline either way is accepted and reads `ok`; a call more than two seconds slower has drifted from the baseline the project agreed to, and the run drives a restore; a call more than two seconds faster than its baseline has the tool lower the recorded value to that time (the baseline ratchets down only, and only on a real improvement, Q60, Q69), removing the entry once the call is below the floor; a faster reading within two seconds leaves the baseline alone. A symmetric `abs` compare was rejected: it would tell the loop to make a faster call slow again, the opposite of what is wanted.

One case escapes the band (Q70, a v0.10.0 refinement): a call back under half the floor has its entry removed whatever the band says. An entry recorded near the floor -- 1.2s against a one-second floor, say -- can never improve by two seconds, so without this mark it would read `ok` forever even at 0.1s; half the floor, rather than the floor itself, keeps a call hovering just under the floor from flip-flopping in and out of the section.

A slower-drifted excluded call keeps an otherwise-green full run on exit 8 (Q57), the same exit a new outlier raises, so the loop does not stop at a call that has crept away from its baseline. The instruction differs from a new outlier's: a new outlier above the floor is shortened under the floor; a slower-drifted exclusion is brought back to within two seconds of its recorded time -- it is a regression against an accepted baseline, not a call to push below the floor. Two seconds is a fixed tolerance, wide enough to absorb run-to-run noise on a multi-second call, narrow enough to catch a real regression. A faster call (Q60) and a stale entry (Q61) are handled by the tool itself -- the baseline ratchets down, or the entry is removed -- so neither blocks a green run; only a slower-drift drives exit 8. The tool lowers a baseline only when a run is more than two seconds below it (Q69), the same band that flags a slower-drift, so noise within two seconds moves the baseline in neither direction and cannot fake a regression.

## Reporting excluded calls

The bounded report window of v0.2.0 -- flagged outliers, the marked floor, the runners-up -- gains an exclusion block after it (Q58). Every excluded call present in the run is listed with its recorded and current time:

```text
Excluded (accepted slow; slower by 2s+ restores; the tool ratchets down or removes the rest):
  ...::test_init_all_writes_hashes  recorded=11.41s  current=11.33s  ok
  ...::test_only_the_exact_session_cookie  recorded=6.80s  current=9.42s  restore to within 2s of 6.80s
  ...::test_assembly_always_called  recorded=3.92s  current=1.30s  baseline lowered to 1.30s
  ...::test_archive_over_1000  recorded=2.54s  current=0.30s  removed (now under the floor)
  ...::test_renamed_or_removed  recorded=4.10s  current=(not run)  removed (stale)
```

A call within tolerance reads `ok`; a slower-drifted call reads the restore instruction with its recorded baseline (Q57); a call more than two seconds faster shows the baseline the tool lowered it to (Q69), or `removed` when it fell under the floor (Q60); an entry whose test did not run shows `removed (stale)` (Q61). The closing key=value line carries an `excluded=<count>` field beside `outliers=` (Q58); the count is the number of slower-drifted calls -- the ones that drive a fix (Q65) -- so `excluded=0` reads as a clean exclusion list, parallel to `outliers=0`.

## Excluding a call only when it must stay slow

An exclusion is the last resort, not a shortcut around a slow test (Q59). A call is added to `[exclusion]` only when the fix-slow-test investigation ([`fix_slow_test.md`](../instructions/fix_slow_test.md)) has profiled it and concluded the time is irreducible without dropping what the test exercises -- a genuine integration path. The recorded seconds is the call's current time at that point, written by a `ghog` add-exclusion command (Q62), not by hand. This replaces the v0.2.0 "raise line 2" advice for one slow call: line 2 is for moving the floor for the whole project, the exclusion list is for accepting one call, and the fix-slow-test instruction and the exit-8 playbook are updated to say so.

## Implementation touch points for exclusions

- `exclusions.py` (new): read the `[exclusion]` section of `a.ghog.outliers` into a `node -> recorded seconds` map, and write it back -- adding an entry, lowering a baseline, removing a below-floor or stale entry -- with the same safe fallbacks as `floor.py`; a function-style module beside `floor.py` and `gate.py`, so `floor.py` keeps its two-line read unchanged.
- `durations.py`: the rule spares any flagged excluded call, leaves excluded calls out of the average, and classifies each excluded node against its baseline (ok, slower-drift, faster, or stale when absent from the run); `DurationSummary` gains an excluded-call list (node, recorded, current, status).
- `durations_summary.py`: read the exclusion map alongside the floor, apply it to the summary, then write the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section. Like the v0.2.0 verdict, this whole exclusion pass forms only on a full run already green on tests and coverage (Q34), so the list is never managed while the suite is failing.
- `durations_report.py`: render the exclusion block after the floor window, each call `ok`, restore (slower), the lowered baseline, or removed (below floor or stale).
- `reporting.py`: a slower-drifted excluded call counts toward the exit-8 verdict; the next-step hint names the exclusion mechanism, not raising the floor; the closing line gains `excluded=<count>` of slower-drifted calls.
- `cli.py` / `commands.py`: a `ghog` add-exclusion subcommand taking the node id and its measured time, writing the entry through `exclusions.py`.
- `instructions/fix_slow_test.md` and `instructions/groundhog.md`: the "when a call must stay slow" guidance becomes "run the `ghog` add-exclusion command with the call's measured time", not "raise line 2".

## Decision log for the exclusion feature

| Decision | Section | Why | Alternatives rejected |
| --- | --- | --- | --- |
| Q53 | The exclusion section in a.ghog.outliers | An optional `[exclusion]` section after the two floor lines, each entry `node = recorded seconds`; floor lines read unchanged, the section is ignored by the floor reader | A second file (one more `a.ghog.*` to track); a column on line 2 (overloads the floor); JSON (needs a schema, harder to hand-edit) |
| Q54 | Sparing an excluded call | Spare the call after the rule runs, so the median, MAD and floor still cover the whole run | Drop the call before the rule (would move the scale the rest is judged against); a separate "excluded" floor (a second gate, the complexity Q43 already rejected) |
| Q55 | Sparing an excluded call | The tool manages the baseline, ratcheting it only downward and removing a below-floor or stale entry; it never raises a baseline, so a creeping-slower call cannot re-baseline away its drift | refresh the baseline freely in both directions (a creeping call hides its own drift); a write-once hand-edited baseline (manual upkeep, dead entries linger) |
| Q56 | The two-second baseline tolerance | Hold an excluded call to its recorded baseline within two seconds; a fixed tolerance absorbs run noise on a multi-second call and still catches a real regression (the compare direction is set by Q63) | A percentage band (swings wide on a long call, tight on a short one); no tolerance (run-to-run noise would flag a stable call); the modified z-score (the call is already off-distribution by design) |
| Q57 | The two-second baseline tolerance | A call more than two seconds slower keeps an otherwise-green run on exit 8 with a restore-to-baseline instruction, distinct from the shorten instruction | A new exit code (exit 8 already means "a call's duration is wrong on a green run"); a report-only note (would not drive the loop to fix the regression) |
| Q58 | Reporting excluded calls | List every excluded call with recorded and current time after the floor window; `excluded=<count>` on the closing line | Hide accepted calls (the user cannot see what is excluded or whether it drifted); list only drifted ones (the accepted-ok calls are the tuning context) |
| Q59 | Excluding a call only when it must stay slow | An exclusion is added only after the fix-slow-test investigation proves the call irreducible; it replaces "raise line 2" for one slow call | Let any slow call be excluded on sight (turns the gate off test by test); keep raising line 2 (lifts the floor for the whole suite, the need this feature answers) |
| Q60 | The two-second baseline tolerance; Sparing an excluded call | A call faster than recorded has the tool lower the baseline to the new time (ratchet down only); once below the floor the tool removes the entry, returning it to the normal rule, with no manual upkeep | report-only for the user to prune (manual upkeep); raise the baseline (would hide a regression); restore it (asks for a slower test) |
| Q61 | Sparing an excluded call; Reporting excluded calls | A recorded node id absent from a full run is reported and removed by the tool, so dead entries and a typo'd node id do not accumulate | ignore it (dead entries pile up, a typo excludes nothing); report-only (manual upkeep) |
| Q62 | Excluding a call only when it must stay slow | An exclusion is added by a `ghog` command taking the node id and its measured time; the tool writes the section while the floor lines stay user-owned | hand-edit the file (mistyped baseline, manual upkeep); a no-number entry the tool stamps (an odd half-state) |
| Q63 | The two-second baseline tolerance | Drift is slower-only -- `current - recorded > 2s` drives the restore; a faster call routes to Q60; this refines Q56's compare | a symmetric `abs` compare (tells the loop to make a faster call slow again) |
| Q64 | Sparing an excluded call | An excluded call is left out of the run average, the same as an outlier, so one accepted slow call does not lift the suite-wide `avg` | count it in the average (one slug lifts the whole-suite average, the drag the v0.2.0 average was built to avoid) |
| Q65 | Reporting excluded calls | `excluded=` on the closing line counts slower-drifted exclusions only, so all-zero counters stay the all-clear, parallel to `outliers=` | count all accepted-slow calls (alarms on a green run); two fields (one more on a six-field line) |
| Q69 | The two-second baseline tolerance | The tool lowers a baseline only on a more-than-two-second improvement, the same band that flags a slower-drift, so noise moves it in neither direction; a transient over-drop is reset by re-running the add-exclusion command | lower on every faster run (noise fakes a later regression); never lower above the floor (the baseline goes stale-high) |
| Q70 | The two-second baseline tolerance | A call back under half the floor has its entry removed even inside the two-second band (v0.10.0 refinement): an entry recorded near the floor can never improve by two seconds, so the band alone would keep it `ok` forever; half the floor, not the floor itself, is the margin against flip-flopping | wait for the two-second improvement (never fires for a baseline under floor + 2s, so a fast-again test stays excluded); remove at the floor exactly (a call hovering just under the floor bounces in and out of the section) |
