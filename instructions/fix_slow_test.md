# Fix a slow test: profile it, find the cost, shorten it

Goal of this instruction: bring a slow test call under the duration floor without weakening what it checks. The groundhog full run flags a call as a duration outlier (exit 8) when it runs far outside the norm and at or above the floor (one second by default, or the line-2 override of `a.ghog.outliers`). This file is the per-call procedure the exit-8 next-step line and the [`groundhog.md`](groundhog.md) playbook point to.

## When to follow this fix-slow-test instruction

- `ghog full` exited 8 and the report listed one or more calls above the floor, or you are cutting a test you already know is slow.
- Fix only the calls listed above the floor — the named outliers. The few next-slowest calls shown under the floor are tuning context, not fix targets; leave them alone.
- One call at a time: profile it, shorten it, move to the next.

## Profile one slow test with pyinstrument

Measure first, never guess. `pyinstrument` is a sampling profiler that reads wall-clock time, so time spent waiting — a subprocess, file or network I/O, a key-derivation function running in C — shows up in the Python frame that called it. That is exactly the shape of most slow tests.

Profile the one test in isolation, with the plugins that add noise turned off. With the project environment loaded (the same `senv` the ghog wrapper uses), run one shell call from the project root:

```bash
pyinstrument -r html -o a.profile.html -m pytest "<NODE ID>" --no-cov -p no:testmon -p no:cacheprovider -q
```

Then open `a.profile.html` and read the frames with the largest self time (the `a.` prefix keeps the file git-ignored, like the `a.ghog.*` family). Drop any flag your setup does not recognise. For a quick read in the console, omit `-r html -o a.profile.html` and pyinstrument prints the call tree directly.

For a property-based test (Hypothesis, the `*_pbt.py` files), this profiles every generated example, so the hotspot aggregates across the run — the cost is usually examples times per-example work, which the profile makes plain.

## Name the hotspot, then apply the smallest fix

State in one sentence where the wall time goes, then apply the fix that fits, and nothing more:

- a key-derivation or hashing cost factor (argon2, scrypt, bcrypt) run per call: lower the cost factor through test config, not by changing production behaviour.
- Hypothesis running many examples, each doing expensive work: cap them with `@settings(max_examples=...)`, or shrink the strategy bounds to a representative size.
- real I/O — a network call, a database, a file read or write, a subprocess: fake it with a stub, a fixture, `tmp_path` or an in-memory double, so the call drives the logic without the slow resource.
- a real wait — `time.sleep`, a poll, a retry with a backoff: fake the clock or inject the delay, so the test spends no real seconds waiting.
- building or parsing real artifacts per example (PDFs, archives, images): use fewer and smaller inputs, or build one sample in a session-scoped fixture instead of one per example.
- per-call heavy construction — an object or fixture built inside the test body: move it to a module- or session-scoped fixture, so the cost is paid once, not per call, which also takes it out of the call phase the rule measures.

Keep the test honest while you cut its time:

- change only what the profile points at, and keep every assertion.
- do not delete assertions, loosen the property, mark the test `xfail`, or skip it to make the number drop. A faster test that proves less is not a fix.
- follow the project code rules: write the class in full, preserve comments and docstrings, update the top docstring to explain the change, and update the `__init__.py` files as needed (see [`preserve_code.md`](../rules/preserve_code.md)).

## Re-measure and fold the fix back into the walk

- run the test alone and check it is under one second:

  ```bash
  pytest "<NODE ID>" --no-cov -p no:testmon -q --durations=1
  ```

- confirm it still passes on its own with `ghog single <file>`. The focused run carries no timing of its own — only the full run measures durations — so the new call time is re-read by the next walk, not here.
- restart the walk with `ghog day`: its full run re-measures every call against the whole suite, so the trimmed call falls under the floor and drops off the list.

Fixing a slow call is a sub-step of the walk, not the end of it: exit 8 is one more non-green step, no different from a failure or a coverage gap. Keep looping from `ghog day` (the loop is in [`groundhog.md`](groundhog.md)) until it reports `exit=0`, then carry on with whatever instruction sent you to the walk -- the handoff, the commit, or the next step. Shortening a call never ends the work; it clears one blocker so the walk can reach the objective.

## When a call has to stay slow

If the call is legitimately slow and cannot be shortened without dropping what it must exercise — a genuine integration test against a real slow path — do not fake the slowness away. Raise line 2 of `a.ghog.outliers` above that call instead (the override the exit-8 hint names, with the floor it has to clear), so the suite accepts it on purpose. The default floor is one second; line 2 is the per-project number you raise to keep a slow call green, or lower to catch faster ones.

## Report back after the fix

Say the hotspot you found, the change you made, and the before and after call time, so the loop has a record of why the call is now under the floor.
