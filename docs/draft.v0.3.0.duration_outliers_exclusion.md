# v0.3.0 duration-outlier exclusions draft -- accept one must-stay-slow call without raising the floor for the rest

## The need for per-test exclusions

The v0.2.0 duration gate judges every call against one floor: a fixed one second by default, or the line-2 override of `a.ghog.outliers`. That floor is global. When one call is legitimately slow -- a real integration test against a slow path that cannot be shortened without dropping what it exercises -- the only way the tool offers to accept it is to raise line 2 above that call.

Raising line 2 to accept one call lifts the bar for the whole suite at once, so a genuine regression in another test lands under the raised floor and is never flagged. One call's exception should not move the line for the rest. The need is a per-test exception: a call proven to belong over the floor is accepted on its own, recorded against a baseline, while the floor stays where it is for everything else.

## Desired outcome for per-test exclusions

- `a.ghog.outliers` gains a tool-managed `[exclusion]` section listing the test node ids accepted as slow, each with the call time recorded as its baseline.
- a call is added by a `ghog` command after the fix-slow-test investigation proves it must stay slow; raising line 2 is no longer the way to accept one call.
- an excluded call is spared from the outlier rule and from the run average, so accepting it changes nothing for the rest of the suite.
- the tool keeps the list accurate without manual upkeep: it ratchets a baseline down only on a more-than-two-second improvement, and removes an entry once the call drops below the floor or its test no longer runs; a baseline is never raised except by re-running the command.
- a call more than two seconds slower than its baseline keeps the loop working on exit 8, the fix being to bring it back within two seconds of the recorded time, not to shorten it below the floor.
- the report lists each excluded call with its recorded and current time, and the closing line carries `excluded=` of the drifted calls.
- the floor lines (1 and 2) of `a.ghog.outliers` stay user-owned.

The detailed design and the decisions (Q53 to Q65 and Q69) that answer this need are in [`design.v0.3.0.duration_outliers_exclusion.md`](design.v0.3.0.duration_outliers_exclusion.md). The implementation steps are in [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). This feature builds on the v0.2.0 floor and rule in [`design.v0.2.0.duration_outliers.md`](design.v0.2.0.duration_outliers.md).
