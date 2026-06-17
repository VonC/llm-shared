# v0.2.0 duration-outliers design -- timing ghog full and gating on true outliers

This design extends [`Pytest reset specs.md`](../tools/Pytest%20reset%20specs.md) with a new
concern for `ghog full`: timing every test call, naming the calls that sit
outside the norm, and folding "no outliers" into the green objective. It keeps
the Q-numbering of the parent spec, so the design questions run from Q34. Q34 to
Q47 are all decided below and folded into the decision table; the design is complete
and ready for the implementation plan.

## Purpose of the duration-outliers feature

A full suite that passes and meets the coverage gate can still hide a handful of
test calls that run far longer than the rest. They slow every later `ghog full`,
and they usually point at a test doing real I/O, a missing fake, or a fixture
built per call instead of once. The feature gives `ghog full` three new jobs:

- time each test call, not just each file, from data pytest already produces.
- at the end of the run, show the average call time (slow calls left out) and how
  many calls are outliers, on the same progress line and bar the run already prints.
- treat outliers as part of the goal: a clean bill is 0 fail, coverage at the
  gate, and 0 outliers. A green-but-slow run is not done.

The aim is the call truly outside the norm, not the merely slower test. A test that
takes two or three times the typical call is slower, not a freak, and must pass
unflagged; the rule and its floor leave that room (Q46).

The fixing loop mirrors the failure loop: the report names each outlier with its
current call time, the caller shortens it (testing it alone with `ghog single` to
confirm the new time), then a fresh `ghog full` re-measures and the call drops off
the list.

## What ghog full measures today

`ghog full` streams the pytest child output and parses it in `parser.py`
(`PytestOutputParser`). The per-test line it reads is the `-v` result line,
`tests/test_a.py::test_one PASSED [ 10%]`, which carries the node id and the
status but no time. The accumulated `RunStats` holds counts (total, done,
failed, warnings, xfailed) and the coverage percentage, never a duration. So
there is no per-call timing anywhere in the tool today; this feature adds it.

## Capturing per-call durations

pytest already times setup, call and teardown for every test. The numbers are
printed only at the very end of the run, in the `slowest durations` block, when
the run is given `--durations`. The block reads:

```text
========================= slowest durations =========================
1.83s call     tests/test_a.py::test_one
0.40s setup    tests/test_a.py::test_one
0.02s call     tests/test_b.py::test_two
```

The capture is confined to `ghog full` (Q39): the full run is the only one that
sees every test, so its average and outlier set are over the whole suite and stay
comparable between runs — the property the fix-and-re-measure loop needs. The
covered `affected` run and the focused steps see only a shifting subset, so they
carry no timing.

The capture plan:

- `runner.pytest_command` adds `--durations=0 --durations-min=0` to the `full`
  branch only. `--durations=0` lists every test, not just the slowest few;
  `--durations-min=0` keeps even sub-5ms calls, so the average covers the whole
  suite, not only the slow tail.
- `parser.py` gains a `slowest durations` section capture, parallel to the
  coverage-table capture: a banner opens it, each `<secs>s <phase> <node>` line
  records the seconds for its phase and node, and the next banner or the final
  summary closes it.
- `RunStats` gains a `durations` map, node id to call-phase seconds (Q36). The
  call phase is the test body, the part an author shortens directly; setup is
  fixture cost shared across tests, kept out of the headline number (a separate
  slow-fixture list can come later). Non-full runs never set `--durations`, so the
  map stays empty and nothing downstream changes for them.

The block arrives at the end of the stream, after the last `-v` line, so the
durations are known by the time the run finishes parsing — in time for the final
report, but not during the live progress lines (Q37).

## Average and outliers in the progress output

The average and the outlier count are end-of-run values (Q37): the precise
durations are free at the end of a stream the tool already parses, and the final
line and closed bar are where the reader looks for the verdict. A live proxy
(timing the gap between result lines) would measure something different from
pytest's own number and show two disagreeing averages in one run, so it is not
done.

The LLM progress line keeps its live shape during the run; the average and the
outlier count are appended only to the final line, once the durations block has
been parsed:

```text
ghog full: 50% (125/250) fail=0 warn=0 xfail=0
ghog full: 100% (250/250) fail=0 warn=0 xfail=0 avg=0.012s outliers=2
```

`avg=` is the mean call time over the non-outlier tests (the outliers left out so
one slug does not drag the average up). `outliers=` is the count of true outliers:
calls that are both far out and above the floor (Q46), so `outliers=0` is a clean
timing bill. The count is the headline; the named list of those outliers and their
times is the report body (Report and next step for outliers).

The closing key=value line gains an `outliers=` key, beside `cov=`:

```text
proj: ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=2 exit=8
```

For a run that does not measure durations (any subcommand other than `full`),
`outliers=` reads `skipped`, the same way `cov=` reads `skipped` when coverage
is not measured.

## Clean bill with zero outliers

The green objective grows a third condition. A `ghog full` run is a clean bill
only when all three hold: 0 failing tests, coverage at the project gate, and 0
duration outliers. Failures and coverage keep their priority — outliers are
judged last, only on a run that is already green on tests and coverage, so an
outlier verdict never hides a real failure or a coverage gap.

A leftover outlier is carried into the orchestration layer by a new exit code,
`8` (`EXIT_DURATION_OUTLIERS`), returned when the run is green on tests and
coverage and at least one true outlier remains (Q34). This reuses every existing
mechanism for free: `ghog day` already records its green snapshot only on exit 0,
so outliers keep the walk re-entering until the slow calls are trimmed, and the
skill loop treats a slow test like any other gap. The caller branches on the code,
never on the report wording, the Q12 rule. Every full run, the first one a project
makes included, reports its true outliers and triggers the fix instruction (Q44);
because only true outliers are flagged (Q46), a tidy suite is green from the start.
A project that accepts a legitimately slow call raises its floor override above it
(The floor file) rather than leaving the loop red.

## Outlier criteria for a full run

The aim is the call truly outside the norm, not the merely slower test. A call is a
true outlier only when both conditions hold (Q46), so a test that is just a few
times the typical call passes unflagged:

- far out by a robust score: the modified z-score on the median and the MAD
  (`0.6745 * (d - median) / MAD`) is at least 3.5, the Iglewicz-Hoaglin cutoff.
  Test call times are heavily right-skewed, so a mean-and-standard-deviation rule
  reads the shape badly — the slow calls inflate both the mean and the deviation
  and so lift their own threshold and hide. The median and the MAD read the center
  from the bulk and are not fooled. When more than half the calls tie and the MAD
  collapses to zero, the score is undefined; the rule falls back so it stays
  defined (Implementation touch points).
- at or above the floor: the floor is the line-2 value, a fixed `1.0s` by default
  (revised post-v0.2.0: the floor was `k * median` with a default `k` of about ten in
  the original design; it is now the line-2 value, default `1.0s`, and `k * median`
  is a recorded reference on line 1 only, Q48). A call has to run at least a second
  before it counts, so a call under the floor is slower, never an outlier, whatever
  its z-score. The line-2 value (The floor file) is the per-project adjustment, and
  line 1's `k * median` is a reference for sizing it.

Requiring both means a call must be statistically separated from the pack and a
large multiple of the typical test. A multiple of the median states the user's aim
directly — the aim is about ratio ("ten times the typical test"), and only a
multiplicative floor states ratio; a log-space z-score and a high percentile were
weighed and dropped (Q46). The first draft's share trigger — flag a call eating a
large slice of total time — is dropped too: in a small suite every call is a large
share by arithmetic, so it flagged normal tests, the opposite of the aim, and a
genuine time-eater already clears the floor.

Detection runs on every full run with no precondition: it always fills the
slow-calls list, the `outliers=` count, and the fix instruction. `avg=` is the
mean over the calls that are not outliers.

## The floor file

There is one floor — an absolute time in seconds — not a separate gate: a call is a
true outlier when it is far out and at or above that floor, and exit 8 is the
consequence of one remaining. The floor lives in a project-root file (Q38), not the
project config, a fixed constant, or an environment variable. The file holds two
lines (Q40):

- name `a.ghog.outliers`, at the project root, following the `a.ghog.*` family
  the tool already writes (`a.ghog.failures`, `a.ghog.day.ok`, `a.ghog.status`)
  and ignored by Git the same way. The user's proposed `a.groundhog.outliers` is
  renamed to match that family.
- line 1: the tool's auto floor, in seconds, rewritten after every full run as
  `k * median` of the run's call times (Q46). It is a recorded reference value only:
  a project can read it to size its own floor, but it no longer gates anything
  (revised post-v0.2.0: line 1 was the default floor in the original design; it is
  now a write-only record, Q48).
- line 2: the active floor in seconds, default a fixed `1.0` — one second. A fresh
  run seeds line 2 with `1.0`, so every project flags any call at or above a second
  out of the box; a positive line 2 is the floor the rule gates against, so a project
  accepts a legitimately slow call by raising line 2 above that call, or tightens
  detection by lowering it. A line-2 value of `0` switches the gate off (it spares
  every call); a value below zero, or a missing, partial, malformed or binary file,
  all fall back to the one-second default (revised post-v0.2.0: line 2 was the user
  override defaulting to `-1` in the original design, with `-1` falling back to the
  line-1 auto floor; it now defaults to a fixed `1.0s` and line 1 no longer gates,
  Q48). Editing line 2 changes the active floor.

Deleting the whole file drops any tuning: the next full run rewrites line 1 and
seeds line 2 again with the one-second default, and still reports and triggers fixes
(Q45). So "no file" and "the first run ever" are the same state, and deleting the
file does what it says, remove the project's tuning and fall back to the
one-second default floor.

The auto floor on line 1 is still recomputed every run as a reference (Q43): the
median is robust, so trimming a slow call barely moves `k * median`. A call that must
stay slow — an unavoidable integration test — is exactly the case for raising the
line-2 floor above it.

## Report and next step for outliers

When a full run has true outliers, the fix instruction lists every one of them, the
slowest first, each with its current call time and its multiple of the median
(`tests/test_a.py::test_one  1.83s  18x median`), under a header — the same shape
as the coverage gap replaying its term-missing rows. The exact call time is part of
the instruction, so the size of each problem is on screen. The next-step message
names the fix: shorten each listed call, confirm the new time by running it alone
with `ghog single <file>`, then re-run `ghog full` so the whole suite is
re-measured. `prompt_workflow` surfaces "fix the slowest call" the way it already
surfaces a failure or a coverage gap, so the fix is triggered from the first run on
(Q44). This reuses the existing loop shape (fix, then `ghog day`), so the caller —
user or skill — needs no new habit. The one alternative to fixing is the line-2
override, when the call is legitimately slow.

The fix instruction names only the calls above the floor — the flagged outliers
(Q47). The slowest few calls the report shows under the floor are tuning context,
not fix targets: an LLM must leave them alone and shorten only the outliers above
the floor.

## Tuning the detection by hand

The list is printed on every full run, looped or run by hand, so a user can call
`ghog full` and read the detection at work. The report shows a bounded window
around the floor (Q47): the flagged outliers, then the floor line marked, then the
few next-slowest calls under it, each with its call time and multiple of the
median; on a run that flags nothing, a single slowest-call line with the floor. The
full sorted list is never printed — that would break the token thrift the tool is
built on.

From that window the user judges whether the cutoff (the factor `k` and the active
floor) flags too many or too few: "too many" reads off the flagged list above the
floor (are normal tests in it), "too few" reads off the runners-up under the floor
(did a real freak slip through). The user then tunes the line-2 override — raise it
to flag fewer, lower it to flag more — and re-runs `ghog full` to see the window
shift. The runners-up are shown for this judgment only; they are never fix targets
(Report and next step for outliers).

## Fixing an outlier: instructions for the LLM

A flagged outlier is a fix target like a failing test or a coverage gap, and the
loop drives it the same way. The detailed how-to lives in the skill instruction
file `instructions/groundhog.md` (wired by `ghog init`, Q13, Q23), beside the
exit-2 and exit-3 guidance; the report itself carries only the concise list, the
floor and the action, so the in-context pointer stays short and the detail is
loaded once. The skill loop gains an exit-8 branch (parent spec, Loop sequence)
that routes here.

On an exit 8, the instructions for the LLM are:

1. fix only the calls listed above the floor — the named outliers. The slowest few
   shown under the floor are tuning context (Q47), not fix targets; leave them.
2. for each outlier, open the test, find what makes the call slow, and apply the
   fitting fix:
   - real I/O — a network call, a database, a file read or write, a subprocess:
     fake it (a stub, a fixture, `tmp_path`, an in-memory double), so the call
     exercises the logic without the slow resource.
   - a real wait — `time.sleep`, a poll, a retry with a backoff: fake the clock or
     inject the delay, so the test spends no real seconds waiting.
   - heavy data or iteration — a large generated input, a long loop: shrink it to a
     representative size that still proves the behavior.
   - per-call heavy construction — an object or fixture built inside the test body:
     move it to a module- or session-scoped fixture, so the cost is paid once, not
     per call, which also takes it out of the call phase the rule measures (Q36).
3. if the call is legitimately slow and cannot be shortened without dropping the
   thing it must exercise — a genuine integration test against a real slow path —
   do not fake the slowness away. Raise the line-2 override of `a.ghog.outliers`
   above that call instead (The floor file), so the suite accepts it on purpose.
4. confirm the new time by running the test alone — `ghog single <file>` reports
   the call time — and check it is under the floor the report showed.
5. restart the walk with `ghog day` (Q30), which re-proves check, affected and the
   full run, so the trimmed call is re-measured against the whole suite.

Step 1 is the boundary the user set: the report shows both sides of the floor so
the cutoff can be tuned, but the fix instruction acts only on the outliers above
it.

## Implementation touch points

The change stays inside the existing package layout of the parent spec:

- `models.py`: the `durations` map on `RunStats`, and the `EXIT_DURATION_OUTLIERS`
  (8) exit code (Q34).
- `parser.py`: the `slowest durations` section capture.
- `runner.py`: the `--durations=0 --durations-min=0` flags on the `full` command.
- `durations.py` (new): the average and the true-outlier rule, `k * median` floor
  and the modified z-score (Q46), pure and unit-tested, with the MAD-is-zero edge
  case handled (a tie-heavy suite where the MAD collapses falls back so the rule
  stays defined).
- `floor.py` (new): read and write the two-line `a.ghog.outliers`, resolve the
  active floor (line 2 when set, else the fixed `1.0s` default; line 1's auto floor
  is a recorded reference only, Q48), beside the `gate.py` and `snapshot.py` file
  helpers.
- `commands.py`: compute the summary after a full run, feed it to the progress
  finish, the classification and the report.
- `reporting.py`: the `avg=`/`outliers=` additions to the progress and closing
  lines, the windowed outlier list (node, call time, multiple of the median, the
  marked floor), the next-step message and the override hint.
- `render.py` / `_Progress`: the closing postfix and the final LLM line carrying
  the two values.
- `instructions/groundhog.md` and the skill loop: the exit-8 branch and the
  outlier fix instructions (Fixing an outlier: instructions for the LLM).
- tests under `tests\unit\tools\` for each module, plus an acceptance scenario
  for a green-but-slow full run.

## Design decisions for the duration-outliers feature

The table summarizes the choices made from Q34 to Q47, the section that carries
each one, and the alternatives that were dropped.

| Question | Decision | Integrated in section | Main argument | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q34 | New exit code 8 (`EXIT_DURATION_OUTLIERS`) when an otherwise-green run has a true outlier | Clean bill with zero outliers | Only an exit code carries "0 outliers" into the orchestration that `ghog day`, the snapshot and the skill loop already key off exit 0 | A2 report-only (goal left unenforced); A3 reuse exit 3 (one code for two fixes, breaks branching) |
| Q35 | Robust detection (median, MAD, modified z-score 3.5) AND above the floor; the share trigger dropped | Outlier criteria for a full run | The two conditions together flag only a true outlier and spare the merely slower test | B2 z-score only (flags slower tests on a tight suite); B3 absolute-only (blind to "outside the norm"); the share trigger (flags normal tests in a small suite) |
| Q36 | Call phase only; a slow-fixture (setup) list deferred | Capturing per-call durations | The call phase is what an author shortens directly and the cleanest single metric | C2 setup+call+teardown total (charges a shared fixture to one node); C3 split lists (additive, deferred) |
| Q37 | End-of-run only: avg and count on the final line and the closed bar | Average and outliers in the progress output | The exact durations are free at the end of the parsed stream; a live proxy shows a second disagreeing number | D2/D3 live proxy (noisy, two sources of truth) |
| Q38 | Floor from a git-ignored project-root file `a.ghog.outliers`, user-editable and deletable | The floor file | A self-managed file keeps the floor visible and owned by the project with no config schema | E1 pyproject config; E2 fixed constant; E3 env var (lost across the fresh shells of Q21) |
| Q39 | `ghog full` only | Capturing per-call durations | Only the full run sees every test, so the average and outlier set are stable and comparable run to run | F2 plus covered affected (shifting subset); F3 every run (loads the fast focused steps) |
| Q40 | Two-line file: line 1 the auto floor, line 2 the user override (default `-1`) (revised post-v0.2.0: line 2 now defaults to a fixed `1.0s` and is the active floor; line 1's auto floor is a recorded reference only, Q48) | The floor file | One floor with a live auto value the user can override; no second concept | A single auto value with no override (no escape for a legitimately slow call); a single frozen value (loses the live auto value) |
| Q41 | Detection always runs, always reports, and always triggers fixes; the floor (auto by default) is always active (revised post-v0.2.0: the floor by default is now the fixed `1.0s` on line 2, not the auto floor; line 1's `k * median` is a recorded reference only, Q48) | Outlier criteria for a full run; Clean bill with zero outliers | The auto floor is always computable from the run, so there is no no-floor state to special-case | A report-only mode that does not trigger fixes (the user wants fixes driven from the first run) |
| Q42 | The auto floor (line 1) is a generous function of the run, set by Q46 (revised post-v0.2.0: line 1's `k * median` is now a recorded reference only and no longer gates; the active floor is the line-2 value, default a fixed `1.0s`, Q48) | The floor file; Outlier criteria for a full run | A generous floor is what leaves room for slower tests and keeps "0 outliers" reachable | I1 twice the median (too low); the median+MAD threshold (equals the z-cutoff, leaves no room); I3 percentile (a fixed fraction always near the line) |
| Q43 | One floor, not a gate: line 2 overrides line 1, `-1` uses the auto floor; exit 8 is the consequence of a true outlier above the floor (revised post-v0.2.0: line 2 now defaults to a fixed `1.0s` and is itself the active floor; line 1's auto floor no longer gates and is a recorded reference only, Q48) | The floor file | The earlier "gate" was a needless second concept; a generous auto floor (Q46) makes the auto value reachable, so no opt-in is needed | A separate opt-in gate (needless complexity); gating on a bare z-threshold floor (unreachable, fixed by the generous floor of Q46) |
| Q44 | Every full run, the first included, reports true outliers and triggers the fix via the report and `prompt_workflow`; no opt-in ceremony | Report and next step for outliers; Clean bill with zero outliers | Only true outliers are flagged, so driving the fix from run one is safe and is what the user asked | A two-phase report-then-enforce opt-in (delays the fix the user wants from the first run) |
| Q45 | Deleting the file drops the override and re-seeds the auto floor next run; outliers are still reported and still trigger fixes (revised post-v0.2.0: deleting drops the line-2 tuning and re-seeds it with the fixed `1.0s` default next run; line 1's auto floor is re-recorded but no longer gates, Q48) | The floor file | One meaning for "no file" — auto floor, fixes triggered — so first-run and post-delete match | O2 remember the override elsewhere; O3 re-seed and silently re-arm (both make delete not drop the override) |
| Q46 | Auto floor `k * median` (default `k` about ten); a true outlier is a call with modified z-score at least 3.5 AND at or above the floor (revised post-v0.2.0: the gating floor is now the line-2 value, default a fixed `1.0s`; `k * median` is still computed but recorded on line 1 as a reference only, Q48) | Outlier criteria for a full run; The floor file | A multiple of the median states the ratio aim directly, leaves room, converges, and the override tunes it | P2 log-space z-score (still needs a floor, reads less plainly); P3 percentile (never reaches a clean zero); the bare median+MAD seed (no room) |
| Q47 | The report shows a bounded window — the flagged outliers, the floor line marked, the few next-slowest under it, one slowest-call line on a green run; the fix instruction names only the calls above the floor | Tuning the detection by hand; Report and next step for outliers; Fixing an outlier: instructions for the LLM | Both sides of the floor are needed to judge too-many versus too-few, but only the above-floor calls are outliers to fix | R1 flagged-only (cannot show an under-flag); R3 full list (breaks token thrift) |
