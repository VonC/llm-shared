# Full Suite on Demand

- Type: feature-request

## Why the full suite should wait for the final phases

Every `ghog day` walk ends with `ghog full`: the whole suite, a fresh coverage
measure against the gate, and a duration-outlier verdict. A green run is not
enough: a coverage gap stops the walk with a request to add tests, and once
coverage is at 100%, a slow test call stops it with a request to shorten that
call.

That walk closes every implementation step, every split, and every repair
loop. During development this costs time twice: the full run itself, and the
coverage and test-speed work it demands before the code has even settled.

## Intent for the ghog day walk

- By default, `ghog day` no longer runs the full suite: check, then the
  affected tests, and stop there.
- The full suite runs only when asked for, through a parameter or an
  environment variable, with one of three levels:
  - `pass`: the full suite runs, only test failures and crashes count;
  - `cov`: failures, crashes, and the coverage gate count;
  - `speed`: failures, crashes, the coverage gate, and duration outliers count
    (today's behavior).
- The final report only asks for the work its level covers: no coverage
  request at `pass`, no slow-test request below `speed`.

## Intent for the phases that ask for the full suite

- Development skills (implement-step, implement-missing-step, split-large-file,
  and the groundhog loop they start) use the default walk.
- The code-review requestor proves `speed` before it publishes a review
  request, from round 1, so every change made for speed is reviewed like the
  rest of the step.
- The prepare-release green gate proves `cov`.
- When the code-review requestor receives a commit-ready answer, no `speed`
  walk runs: the last request was already validated at `speed`.
- Without review mode, the `speed` pass runs between implementation-check and
  the commit menu.

Revised on 2026-09-30: an earlier intent ran the `speed` walk after review, at
the commit-ready answer, sending production-code speed repairs to another
round and letting test-only repairs skip review. Moving `speed` before review
keeps every speed change under review and removes that post-review exception.
