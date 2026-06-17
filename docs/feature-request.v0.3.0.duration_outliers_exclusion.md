# v0.3.0 duration-outlier exclusions -- accept one must-stay-slow call without raising the floor for the rest

## The need for per-test exclusions

The v0.2.0 duration gate judges every call against one floor: a fixed one second by default, or the line-2 override of `a.ghog.outliers`. That floor is global. When one call is legitimately slow -- a real integration test against a slow path that cannot be shortened without dropping what it exercises -- the only way the tool offers to accept it is to raise line 2 above that call.

Raising line 2 to accept one call lifts the bar for all 5000-plus tests at once. A genuine three-second regression in another test then lands under the raised floor and is never flagged, so accepting one slow call blinds the gate to every test slower than the floor but faster than the accepted one. That is the wrong trade: one call's exception should not move the line for the rest.

The need is a per-test exception. A call proven to belong over the floor is named and accepted on its own, with the time it ran at recorded as its baseline, while the floor stays where it is for everything else.

## Desired outcome for per-test exclusions

- `a.ghog.outliers` gains an `[exclusion]` section listing the test node ids accepted as slow, each with the call time recorded when it was excluded.
- a call is added to that section only after the fix-slow-test investigation concludes it genuinely must stay slow; raising the global floor (line 2) is no longer the way to accept one call.
- an excluded call is spared from the outlier rule whatever the floor, so accepting it changes nothing for the rest of the suite.
- the floor (line 2) goes back to its real job: project-wide tuning of where "an outlier" begins, not a place to park one slow test.
- each excluded call is held to its own recorded baseline: the report lists it with its recorded and current call time, marked accepted when they are within two seconds.
- a call more than two seconds slower than its baseline keeps the loop working the same way a new outlier does, but the fix is to bring it back within two seconds of the recorded time, not to shorten it below the floor; the baseline is never raised, so a regression can never hide behind it.
- a call faster than its baseline has the tool lower the recorded time to the new faster value -- the baseline only ever ratchets down -- and once the call drops below the floor the tool removes the entry, returning the call to the normal floor rule.
- an entry whose test no longer runs on a full suite is reported as stale and removed by the tool, so dead entries and a mistyped node id do not accumulate.
- an exclusion is added by a `ghog` command (the node id and its measured time), so the tool writes the entry after the fix-slow-test investigation rather than the user editing it by hand.
- the tool keeps the `[exclusion]` section accurate without manual upkeep -- it adds on command, ratchets baselines down, and removes stale or now-fast entries -- while the floor lines (1 and 2) of `a.ghog.outliers` stay user-owned.
- a user can read the excluded list at the end of a `ghog full` run and see, at a glance, which calls are accepted-slow and which have drifted.

The detailed design and the decisions (Q53 to Q65) that answer this need are in [`design.v0.3.0.duration_outliers_exclusion.md`](design.v0.3.0.duration_outliers_exclusion.md). The implementation steps are in [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). This feature builds on the v0.2.0 floor and rule in [`design.v0.2.0.duration_outliers.md`](design.v0.2.0.duration_outliers.md).

## Feature decisions for the exclusion request

These decisions answer the review's feature questions; the matching design choices are recorded in the design's decision log.

| Decision | Section | Why | Alternatives rejected |
| --- | --- | --- | --- |
| Q60 | Desired outcome (faster call) | A call faster than its baseline has the tool lower the recorded time to the new value -- the baseline only ratchets down, never up, so a regression cannot hide -- and once the call is below the floor the tool removes the entry, returning it to the normal rule; no manual upkeep | report-only for the user to prune (manual upkeep, dead entries linger); raise the baseline on a slower call (would hide a regression) |
| Q61 | Desired outcome (stale entry) | An entry whose test does not run on a full suite is reported and removed by the tool, so dead entries and a typo'd node id do not accumulate | ignore it silently (dead entries pile up, a typo'd exclusion fails quietly); report-only (leaves manual upkeep) |
| Q62 | Desired outcome (adding an exclusion) | An exclusion is added by a `ghog` command taking the node id and its measured time; the tool writes the entry after the fix-slow-test investigation, so the baseline is the real measured value | hand-edit the file (a mistyped baseline, manual upkeep); a no-number entry the tool later stamps (an odd half-state) |
