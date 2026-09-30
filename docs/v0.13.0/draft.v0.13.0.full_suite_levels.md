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
  affected tests, and stop there, saying the skip is on purpose.
- The full suite runs only when asked for, through a parameter or an
  environment variable, with one of three levels:
  - `pass`: the full suite runs, only test failures and crashes count;
  - `cov`: failures, crashes, and the coverage gate count;
  - `speed`: failures, crashes, the coverage gate, and duration outliers count
    (today's objective; in a parallel project it needs the sequential timing
    pass, since the parallel run does not measure call times).
- The final report only asks for the work its level covers, and every restart
  line it prints keeps the level, so an LLM following it never falls back to
  the default walk.
- A walk reuses what is still proven for unchanged sources, and never keeps a
  proof that a newer result contradicts.

## Intent for the phases that ask for the full suite

- Development skills (implement-step, implement-missing-step, split-large-file,
  and the groundhog loop they start) use the default walk.
- Under the default validation, the code-review requestor proves `speed`
  before it publishes each review request, from round 1, so every change made
  for speed (a duration exclusion included) is reviewed like the rest of the
  step. A project that declares its own validation commands keeps them, and
  gets a notice when they no longer prove `speed`.
- When the code-review requestor receives a commit-ready answer, no `speed`
  walk runs: the last request was already validated at `speed`.
- Without review mode, the `speed` pass runs between implementation-check and
  the commit menu; any change it makes goes back through implementation-check.
- The prepare-release green gate proves `cov` on the whole suite.

## Intent for test groups

- An effort can declare a test group (for example every test file under a
  `tests` folder whose name contains `sentinel`, with the source files it
  owns). Development walks, the validation before each review request, the
  review-off `speed` pass, and the affected checks of implementation-check and
  the reviewer then run only that group, and the 100% coverage gate applies to
  the group's own sources, covered by the group's tests only.
- The whole suite can always be selected explicitly, so a group left in the
  shell never narrows prepare-release or an effort without a group.
- A group that matches no test or no source file is an error, never an empty
  success or a silent whole-suite run.
- A proof counts only for the exact group it was earned on (same patterns,
  same files), and a group run never changes the project's slow-test
  threshold.
- The trade-off is accepted: a breakage outside the group surfaces only at the
  prepare-release gate, which runs every test at `cov`.

## Revisions of the full suite levels intent

Revised on 2026-09-30: an earlier intent ran the `speed` walk after review, at
the commit-ready answer, sending production-code speed repairs to another
round and letting test-only repairs skip review. Moving `speed` before review
keeps every speed change under review and removes that post-review exception.
A recheck of `speed` at the commit-ready answer was considered and dropped.

Revised on 2026-09-30, test groups: the full suite of an effort can be
narrowed to a declared test group, with prepare-release as the only
whole-suite gate for grouped efforts.
