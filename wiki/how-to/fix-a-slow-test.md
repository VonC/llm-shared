# How to fix a slow test flagged as an outlier

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The Groundhog loop normally hands an exit-8 outlier to the AI's
`fix-slow-test` skill, which profiles, improves, and rechecks it. Use this guide
directly when optimizing a known slow call without running the whole chain.

🧪 Goal: bring a test call flagged by the exit-8 duration gate back under
the one-second target, without weakening any assertion.

## 🐢 What exit 8 means

The sequential full run at `speed`, or `ghog timings`, times every test call.
A robust outlier score at or above a
one-second floor stops an otherwise-green walk on exit 8, with the slow
calls named. The verdict is judged last, so it never masks a failure or a
coverage gap.

## 📋 Steps to shorten the call

1. Read the project's `TESTING.md` first, if it has a
   `## Tests Execution Time Optimization Techniques` section: it lists the
   fixes already accepted in that codebase.

2. Profile the one call, not the suite:

   ```cmd
   pyinstrument -r html -o a.profile.html -m pytest "<NODE ID>" --no-cov -p no:testmon -p no:cacheprovider -q
   ```

3. Name the hotspot, then apply the smallest fix that removes it:

   - lower a KDF or hashing cost factor in the test configuration,
   - cap Hypothesis examples,
   - fake the slow resource (I/O, network) or the clock,
   - shrink the input data,
   - move heavy construction into a session fixture.

   Keep every assertion: the goal is a shorter road to the same checks.

4. Re-measure the call; aim under one second.

5. Restart with `ghog day --full=speed` and the original explicit scope.
   Use `pw scope day --full=speed` to print the effort's command; execute the
   printed command through the resolved ghog launcher.

## 🤝 Accepting a genuinely slow call

Some tests are legitimately slow. As a last resort, record the exclusion
at its measured time so the gate stops flagging it:

```cmd
ghog exclude "<NODE ID>" <measured seconds>
```

The entry lands in the `[exclusion]` section of `a.ghog.outliers` in the
artifact home (`.reviews` unless `.review-artifacts.ini` declares another
home; the confirmation line prints the path), with the measured time as
its baseline. The call stays timed on every later
run and is classified against that baseline — `ok`, `slower`, `faster` or
`stale` — so an excluded test that drifts even slower does not go
unnoticed.

## 🎚️ Tuning the gate floor for the whole suite

The floor is line 2 of that same artifact-home `a.ghog.outliers`, default
`1.0` second (line 1 is
a per-run record of `10 x median`, for reference only). Edit line 2 to
move the bar for every test at once:

- raise it when the project accepts slower tests as normal,
- lower it to hunt calls faster than one second (the report's under-floor
  runners-up show the next candidates),
- set it to `0` to switch the gate off entirely,
- delete the file to re-seed the default on the next run.

Prefer a per-call `ghog exclude` over raising the floor: the floor moves
the bar for the whole suite, an exclusion accepts one known call.

## ✅ Check after the fix

The scoped `ghog day --full=speed` reaches exit 0 with matching `proof=speed`.
Report the hotspot and before/after timing. For an accepted exclusion, also
report its node id, measured baseline, attempted improvement, and reason.
Changing the floor or exclusions caps saved speed proof at coverage until
the speed gate is proved again.

Related: [Fix a red groundhog walk](fix-a-red-groundhog-walk.md),
[ghog commands and exit codes](../reference/ghog-commands-and-exit-codes.md).
