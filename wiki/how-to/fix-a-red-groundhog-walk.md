# How to fix a red groundhog walk

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Inside an implementation workflow the AI reads Groundhog's exit contract,
applies the named fix, and runs the day again. Use these commands directly to
reproduce or diagnose the same failure from a console.

🧪 Goal: bring a stopped `ghog day` walk back to green by applying the fix
each exit code calls for, without wasting a full run on the wrong move.

## 🔁 The loop discipline

The walk never fixes; it walks, gates, reports. The loop is always: run
`ghog day`, apply the fix the final report names, run `ghog day` again.
Never re-walk without a change, use the cheaper inner verifiers each
branch names, and stop when an iteration makes no progress — never beyond
10 iterations.

## 📋 Recipe per exit code

- **check failing (passthrough exit)** — fix the compile or lint errors in
  place. A "Big files found" report means a file is over the line limit:
  split it with [`/split-large-file`](split-a-large-file.md); ghog reports,
  it never splits.

- **exit 2 on the affected step** — fix the failures, re-run
  `ghog affected --no-cov` until green, then `ghog day`.

- **exit 2 on the full run** — the failing node ids land in
  `a.ghog.failures`. Focus first:

  ```cmd
  ghog single <failing test files>
  ```

  The focus report splits plain failures (fix first) from tests passing in
  focus but failing in the full suite (interaction suspects, fix second).
  Stay on `ghog single` until green, then restart the walk.

- **exit 3, coverage gap** — the report replays the term-missing rows
  under `Uncovered lines`. Feed each row to covg:

  ```cmd
  cmd /d /v:on /c "senv.bat && ..\llm-shared\bin\covg.bat src\pkg\mod.py 48 86-88 100"
  ```

  covg names the enclosing functions and builds a ready-to-paste
  test-writing prompt. Add the tests, verify with `ghog affected` only
  (coverage appends across runs); at the gate, run one `ghog check` (new
  tests are code too), then `ghog day`. Never generate or parse a
  `coverage.json` export.

- **exit 4, suite crash** — act on the crash block (last started tests,
  stack tail): make the suite robust against that exception.

- **exit 5, setup error** — read the printed reason; looping cannot fix
  it. `cov=unread` means the coverage TOTAL line is missing, a loud setup
  problem.

- **exit 6, a run is live** — wait; poll `ghog status` until `state=done`,
  and start nothing meanwhile.

- **exit 7, the run is lost** — the walk was killed mid-run; relaunch
  `ghog day` (or `ghog day --detach` under a harness with tool timeouts).

- **exit 8, duration outlier** — the suite is green but one call ran far
  outside the norm: see [Fix a slow test](fix-a-slow-test.md).

## 🤖 Driving the loop from an LLM

Every LLM-driven run goes through one redirected call so the model reads
only the log tail (last 5 lines on green, last 100 on a stop):

```cmd
cmd /d /c "..\llm-shared\bin\ghog.bat day > a.ghog.log 2>&1"
```

Exceptions never redirected: covg runs (their full output is the data)
and `ghog status` (a redirect would truncate the live walk's log).

## ✅ Check the objective

The green walk ends with `Objective reached` and a closing line such as
`myproject: ghog full done fail=0 warn=0 xfail=11 cov=100 exit=0`. The nag
line about warnings or xfails never blocks it.

Related: [ghog commands and exit codes](../reference/ghog-commands-and-exit-codes.md),
[Groundhog as a reset loop](../explanation/groundhog-as-a-reset-loop.md).
