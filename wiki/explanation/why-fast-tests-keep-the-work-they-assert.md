# Why fast tests keep the work they assert

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

## Invocation model

Nobody invokes this gate by hand. The suite's pytest policy measures every
test lifecycle on each run, and the covered full step of
`ghog day --full=speed` measures the whole suite on two workers with coverage.
The AI meets the gate while it drives the groundhog loop; a human meets it by
running `ghog day` or a focused `ghog single`.

## What this page explains about test speed

🧪 Every test in this repository has a budget for its whole lifecycle: fixture
setup, the call and teardown together. This page explains how that budget is
measured, what made tests exceed it, and why each speed-up keeps the behavior
the test asserts. For the walk that enforces it, see
[Groundhog as a reset loop](groundhog-as-a-reset-loop.md). For the practices to
apply when writing or reviewing a test, follow the dedicated instruction
[`write-fast-python-tests.md`](../../instructions/write-fast-python-tests.md).

## The lifecycle budget and its two clocks

A test passes the timing gate when its lifecycle uses at most 0.1 second of
CPU and at most one second of wall time, and when setup and teardown each stay
under 0.1 second of wall time. The preferred target is 0.04 second of CPU: it
leaves room for coverage, two workers and an ordinary busy workstation.

CPU is counted in one window, from the start of setup to the end of teardown,
including the report hooks that run in between. An earlier version summed
three separate phase readings. On Windows, CPU time advances in 15.625 ms
ticks, so three readings could overstate a test by almost three ticks; one
window overstates it by less than one.

Initialization stays inside that window. A grammar, a seed template or a
cached observation is built lazily by the first test that needs it, and that
test pays for it. Moving such work into worker startup or an unmeasured
fixture would hide it, not remove it.

## Where the time actually went

Profiling the slowest tests showed the same few causes again and again:

- **Replayed journeys.** A fixture drove several public commands to reach the
  state one test asserted, and the whole journey was charged to that test.
- **Repeated reads of things that do not change.** Templates, command
  grammars, settings and source inventories were rebuilt on every use.
- **Native work nobody asserted.** Searching every `PATH` entry for an
  executable, probing the console size, or reading a file through the
  operating system when the test only needed its text.
- **Expensive generation.** Property tests that drew arbitrary Unicode text
  made Hypothesis load its Unicode category tables in whichever test came
  first in a process.

## Declare prerequisites, run the asserted transition

A test that checks a human confirmation does not need to publish a request and
an answer first. Their publication has its own tests. The confirmation test
writes the resulting records directly, as typed coordination, envelope and
transcript data, then runs the real confirmation it asserts.

The records must match what the production code would have produced. In one
case the declared record carried a different family policy from the one the
core under test registered; the observer correctly classified that state as
inconsistent, and the real confirmation refused it. The fix was to declare the
registered policy, not to weaken the observer.

Long journeys were also split into independent cases. An activation check, a
duplicate-start check and an identity-isolation check had shared one fixture
of eight commands; as three cases, each keeps its assertions and pays only for
its own transitions. Splitting moved the first case of that batch from 0.094
second of CPU and a 0.119 second setup to under 0.04 second.

## Reuse what cannot change

Command grammars, shipped template text and stable path observations are
immutable during a test session. The suite keeps one lazy cache for each,
filled inside the first test that needs it. Template text is read through a
single function, `tools/template_text.py`, so production still reads the file
on every render while the suite reuses it. A missing template still fails,
because a failed read is never cached.

Live state is never cached: protocol records, ownership, transcripts and
anything a test mutates are read fresh every time.

## Remove native work the test does not assert

Several costs were operating-system calls that no assertion depended on:

- Simulated walks searched `PATH` for the pytest executable on every child
  launch. Declaring the executable, as other walk tests already did, took the
  slowest of them from 0.125 to 0.031 second.
- Argparse probed the native console for every formatter. A declared terminal
  size removed the probes.
- Pytest captured output through native file descriptors. Capturing Python
  streams is enough for tests that create no processes.

Tests that count native file opens show why this matters: tests that opened
real files showed kernel CPU twice as often as tests that did not.

## Generate the same domain more cheaply

A property test should explore the same inputs, not fewer. Unicode text is
generated by mapping integers onto every scalar value, skipping the surrogate
block and any excluded characters, through `tests/scalar_text.py`. The domain
equals that of Hypothesis's default text, the example budgets are unchanged,
and deterministic tests pin the mapping's edges. The first Unicode property in
a process no longer pays for the category tables: one such test went from
0.109 to 0.0625 second of CPU.

Small finite domains are enumerated exhaustively with parametrization instead
of sampled. Lowering an example budget would be a different tradeoff, because
it reduces exploration; none was lowered here.

## What a fast test still proves, and what it does not

Repository scenarios run on a memory-backed filesystem with the real
production code on top. That proves paths, bytes, ordering, records and
error handling. It does not prove Windows sharing rules, crash durability or
native lock contention, and it does not replace the launcher acceptance
checks that run real commands. Simulated scratch paths keep the canonical
spelling that tools such as coverage report; a lower-case drive once made
coverage data unmatchable and a covered walk read 0%.

Tests also stopped inheriting the agent that launched them. Production detects
the calling agent from environment signals; the suite removes those signals
so a run from one agent host behaves like a run from another.

## Why a few timing misses are confirmed, not trusted

After these changes, a full round over every group measured 5,143 test
lifecycles, all under the hard CPU gate, with 57 above the 0.04 second target
and a maximum of 0.094 second. The remaining misses were rare, about one per
thousand lifecycles, and their shape was not test work: kernel time with
little user time, or setup that waited a tenth of a second while using almost
no CPU. They hit a different test each run.

Lowering such a test further cannot help, so the gates stay unchanged and a
timing-only miss with that shape is measured again once, in the same order. If
the same test misses again, it is a real cost and gets fixed. Every
confirmation is recorded with its user, kernel and garbage-collection time.

## What the whole suite measured afterwards

The covered whole-suite walk that followed ran 5,148 tests on two workers with
coverage in 32 seconds, at 100% configured coverage and with no failure. Its
highest lifecycle used 0.094 second of CPU, 16 lifecycles exceeded the 0.04
second target, none exceeded a hard gate, and the longest setup took 0.035
second. Earlier whole-suite attempts in the same effort took five to six
minutes and failed on timing.

## Turning these reasons into practice for new tests

The reasons above become a checklist in
[`write-fast-python-tests.md`](../../instructions/write-fast-python-tests.md),
also available as the `write-fast-python-tests` skill. It covers the lifecycle
budget, measuring before changing a test, declaring prerequisites, reusing only
immutable inputs, keeping native work out, isolating each test from its host,
generating property inputs without shrinking them, and the shortcuts that never
count as a speed-up. When a test is already flagged as slow,
[`fix_slow_test.md`](../../instructions/fix_slow_test.md) profiles it first.
