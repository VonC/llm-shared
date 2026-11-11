# Write fast Python tests: keep the work each test asserts

Goal of this instruction: write or review a Python test so its whole lifecycle,
fixture setup, call and teardown together, stays well inside the project's time
budget without weakening what it checks. Use it when you add a test, when you
review one, and before a test can become a duration outlier. When a test is
already flagged as slow, profile it with [`fix_slow_test.md`](fix_slow_test.md)
first, then apply the practices below. The reasoning behind them is explained
in the wiki page *Why fast tests keep the work they assert*.

## Budget for one test lifecycle

- Count the whole lifecycle, not only the call: setup, call and teardown, with
  every fixture they create. Aim to keep a lifecycle under the project's CPU ceiling
  and wall reference, `test_lifecycle_limit` and `test_lifecycle_wall_limit` (0.1
  and one second by default), and setup and teardown each stay under 0.1
  second of wall time. Aim for 0.04 second of CPU so coverage, two workers and
  a busy machine leave headroom. The stability band that lets a proven test
  pass a load spike is a tolerance for the machine, never a target.
- The lifecycle gate passes timing when CPU is at or below the effective limit,
  including an eligible band or accepted exception, even when wall time exceeds
  its reference. It still measures and reports wall time. Functional failures,
  process auditing and groundhog's separate call-duration speed rule still apply.
- Keep first-use work inside the test that first needs it. Building a grammar,
  a template or a cache in worker startup, at collection, or in an unmeasured
  session fixture hides its cost; it does not remove it.
- Moving work from the call into setup, or from one test into the next, is not
  a speed-up either: the budget measures both.

## Measure before changing a test

- Profile one test before editing it, as `fix_slow_test.md` describes, and name
  the cost in one sentence: replayed setup, repeated reads, native calls,
  generation, or real waiting.
- On Windows, CPU time advances in 15.625 ms ticks: compare readings in ticks
  and never draw a conclusion from a one-tick difference.
- When a reading is far above the test's usual cost, split it into user CPU,
  kernel CPU, garbage collection and idle wall time before acting. Kernel time
  points at native operating-system work, idle wall at waiting, user time at
  Python work. CPU above the test's own wall time means another thread used it.
- Counting operations (native file opens, command invocations, child launches)
  is exact and repeatable, and confirms that a repair removed work without a
  timing run.

## Give each test only the transitions it asserts

- Assert one transition per test. When a test checks a confirmation, declare
  the prior state (records, files, ownership) directly instead of replaying the
  public journey that produces it; that journey keeps its own test.
- A declared prerequisite must equal what production would have written: the
  same policy, identity, ownership generation and invariants. If production
  validation rejects the declared state, fix the declaration; never weaken the
  validation.
- Split a module- or package-level journey fixture shared by several tests into
  independent cases. Otherwise its whole cost lands on whichever test runs
  first, and that test flips between passing and failing with execution order.
- Keep one public command-line test per contract. Check variants of the same
  decision by calling the deciding function with plain data.

## Reuse only what cannot change during the session

- Cache immutable inputs lazily for the session: command grammars, shipped
  template text, stable path and configuration observations. The first test
  that needs one still pays for it.
- Never cache mutable state: protocol records, ownership, transcripts,
  anything a test writes, or a settings file a test may rewrite at the same
  path.
- Do not cache failures: a missing or invalid input must fail again on the
  next read.
- Read immutable production inputs through one replaceable function, so the
  suite can reuse them while production still reads them on every call.

## Keep native work out of tests that do not assert it

The shared `llm_shared_lifecycle_gate` and `llm_shared_process_audit` plugins are
independent opt-ins for consumers; this repository selects both. Follow the
[lifecycle activation guide](../wiki/how-to/enable-shared-lifecycle-gate.md) and
[process permission guide](../wiki/how-to/enable-shared-process-audit.md).
Use the exact plugin-manager guard when registering the four lifecycle keys
for unselected strict runs. Register `process_allowed(reason)` independently
and declare fixture permissions by decorated object in
`LLM_SHARED_PROCESS_FIXTURES`; neither declaration needs shared imports.
Permissions authorize only their documented operation scope and never remove
timing charges. This repository's own tests and fixtures declare no process
permissions. Real executable compatibility checks run in the separate harness.

- Use the project's memory-backed scratch filesystem or virtual `tmp_path` when
  it has one, instead of creating and deleting native directories. Keep the
  path spelling that external tools report (for example an upper-case Windows
  drive), or their file keys stop matching.
- Never start a process from a test. Inject the seam instead: declare the
  executable rather than searching `PATH`, declare project detection, and
  supply recorded Git or command observations.
- Avoid native probes nobody asserts: declare a terminal size instead of
  querying the console, capture Python streams instead of native file
  descriptors when nothing spawns a child, and use a declared locale instead
  of catalog lookups.
- Count native file opens per test when kernel time appears; repeated reads of
  the same immutable file are the first candidates for a session cache.

## Isolate each test from its host and from other tests

- Remove host signals the code under test reads, such as the variables that
  identify the calling agent, so a run behaves the same from any terminal.
  Tests of that detection set the signal they assert explicitly.
- Restore every global a test changes: environment variables, the current
  directory, logging handlers and levels, monkeypatched functions.
- Stop every thread, observer or executor a test starts. A thread left running
  burns CPU and kernel time that the next test's window is charged for.
- Replace real waiting with a fake clock or an injected sleeper. A test never
  sleeps to let something happen.

## Generate property inputs cheaply without shrinking them

- Keep the domain, the example budget and the explicit examples. Lowering
  `max_examples` or narrowing a strategy to pass the budget reduces what the
  property explores and is not an acceptable fix.
- Draw the same domain through a cheaper encoding. For arbitrary Unicode text,
  map integers onto every scalar value instead of using the default text
  alphabet, which loads Unicode category tables on its first use in a process.
  Pin the mapping's edges with a deterministic test.
- Replace a small finite domain with exhaustive parametrization, so every case
  runs and fails individually.
- Disable the example database and wall-clock deadlines in the suite profile;
  the duration gate, not Hypothesis, judges slowness.

## Shortcuts that never count as a speed-up

- Deleting or loosening an assertion, marking a test `xfail`, skipping it, or
  moving it out of the default suite.
- Raising a budget, a floor or a deadline, or adding a duration exclusion to
  pass. An exclusion stays the last resort that `fix_slow_test.md` governs,
  never a way to meet this budget.
- Re-running an unchanged walk until timing looks better. Change the test,
  then walk again, as [`groundhog.md`](groundhog.md) requires.
- Building a new simulation of an external system without the project's
  agreement. Replace a transport only where the project already provides one.

## Verify a faster test

- Run the changed tests in focus with `ghog single <files>` until they pass.
- Re-measure them in the same order as the suite runs them, so first-use costs
  stay where they belong.
- Finish with the walk the task requires, for example `ghog day --full=speed`,
  and report the cost you removed with its before and after readings.
