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
- The code-review requestor proves `cov` before it publishes a review request.
- The prepare-release green gate proves `cov`.
- When the code-review requestor receives a commit-ready answer, it runs one
  `speed` walk:
  - if shortening the slow calls needs a change in production code (not only
    in tests), it requests another review round;
  - otherwise (no outlier, or test-only changes), it accepts the commit-ready
    answer and waits for the human to validate the commit.
