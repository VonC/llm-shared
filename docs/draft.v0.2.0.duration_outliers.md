# v0.2.0 duration-outliers draft -- time ghog full and gate on the calls truly outside the norm

## The need for duration outliers

A `ghog full` run can pass every test and meet the coverage gate while a handful of
test calls run far longer than the rest. Those slow calls drag every later full run,
and they usually point at a test doing real I/O, a missing fake, or a fixture built
per call instead of once. Today the tool times nothing per call, so a green-but-slow
suite looks done when it is not.

The need is to surface the call truly outside the norm -- not the merely slower test
-- and to keep fixing it the way failures and coverage gaps are already fixed: name
it, shorten it, re-run, watch it drop off the list.

## Desired outcome for duration outliers

- `ghog full` times each test call, not just each file.
- at the end of the run, the progress line and the bar show the average call time
  (slow calls left out) and how many calls are outliers.
- a clean bill becomes 0 fail, coverage at the gate, and 0 outliers; a leftover
  outlier keeps the loop fixing.
- only a call far outside the norm is flagged, so a test that is merely two or three
  times slower than its peers is left alone.
- the report names each flagged call with its time, and an LLM is told how to shorten
  it, or to accept it when it is legitimately slow.
- a user can run `ghog full` by hand and read the detection at work, to judge whether
  it flags too many or too few and tune it.

The detailed design and the decisions (Q34 to Q47) that answer this need are in
[`design.v0.2.0.duration_outliers.md`](design.v0.2.0.duration_outliers.md).
