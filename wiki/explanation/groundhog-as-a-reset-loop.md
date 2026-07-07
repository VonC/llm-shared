# Groundhog as a reset loop

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🧪 Like the movie, groundhog relives the same day — compile check,
affected tests, full suite with a freshly reset coverage measure — until
the day is flawless. The design choices all follow from one split: the
walk never fixes, and the fixer never walks.

## ⚖️ Why walk and fix are separate

`ghog day` walks, gates and reports; fixing belongs to the caller, human
or LLM, following `instructions/groundhog.md`. That split makes the loop
auditable: every iteration is one walk with one verdict, the fix applied
between two walks is visible in the diff, and the loop has a stopping
rule — no progress, or ten iterations — instead of a model quietly
thrashing.

The walk is also the only re-entry point. After a fix, the next command
is `ghog day` itself, never a standalone subcommand as confirmation: the
cheaper inner verifiers (`ghog single`, `ghog affected`) exist inside a
branch, and each branch hands back to the walk.

## ♻️ Why the full run resets testmon

`ghog full` deletes `.testmondata` and rebuilds it on a single worker.
The fresh database is what makes every later `ghog affected` cheap and
truthful — stale test-impact data would let a change slip through the
fast pass. The full run is slow on purpose: it is the objective verdict,
and the day snapshot (`a.ghog.day.ok`) makes repeating a green one free.

## 👥 One output, two audiences

The output is mastered for a token budget and a terminal at once. A human
gets a live progress bar; a captured run gets one plain line per 10% and
a 60-second silence floor. LLM-driven runs are redirected to `a.ghog.log`
so the model reads only the tail — last 5 lines on green, last 100 on a
stop — while the user follows the same file live from a second console.
The guard even rewrites a forgotten redirect: a harness capture receives
an envelope naming the log, never the full report.

## 🚦 Why exit codes, not prose

The model branches on `exit=N`, not on wording: 2 failures, 3 coverage,
8 outlier, 6 live, 7 lost. Prose can drift; the contract cannot. The
lifecycle file `a.ghog.status` extends the contract across processes — a
walk killed by a harness timeout is detectable (`ghog status` probes the
pid), and a second walk refuses to start while one is alive, protecting
both the log and the testmon state.

## 🐢 Why slow tests stop a green run

Exit 8 flags a duration outlier even when everything passes, judged last
so it never masks a failure. A suite that creeps past one second per test
stops being run willingly; the gate keeps the feedback loop fast enough
that running it stays the default.

The rule deliberately separates slower from outlier: a call two or three
times the median is merely slower, and flagging it would turn the gate
into noise. A call is stopped only when a robust statistic (the modified
z-score, immune to the outlier inflating a plain average) says it sits
far outside this run's norm, AND it crosses an absolute floor in seconds
— relative oddity alone never flags a uniformly fast suite, and absolute
slowness alone never flags a uniformly slow one the project has accepted.
The floor is the project's one knob, and `ghog exclude` records the
deliberate exceptions at their measured time, each held to that baseline
afterwards.

## 👉 Where the contract is written

- [ghog commands and exit codes](../reference/ghog-commands-and-exit-codes.md)
  for the full tables.
- [Fix a red groundhog walk](../how-to/fix-a-red-groundhog-walk.md) for
  the per-branch recipes.
