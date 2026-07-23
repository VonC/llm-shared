# ghog commands and exit codes

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🧪 The groundhog contract: every subcommand, every exit code, and the
closing line. Single entry point `bin\ghog.bat`; each wrapper loads
`senv.bat` itself, so a call is self-contained from any shell.

## Invocation model

The AI normally drives these commands as a reset loop after implementation and
keeps going until the recorded state is done or a safety stop needs human input.
Run them directly to learn the stages, diagnose a failed walk, or integrate the
same contract into local automation.

## ⌨️ Subcommands

| Alias | Subcommand | Behavior |
| --- | --- | --- |
| — | `ghog day` | walk check, then `affected --no-cov`, then `full`, stopping at the first non-green step; a noop when nothing changed since the last green walk (`--force` overrides); `--detach` runs a survivor process polled through `ghog status` |
| — | `ghog status` | replay the run lifecycle from `a.ghog.status` without starting anything |
| — | `ghog check` | run `check.bat` from the project root, exit code passed through |
| `ptr` | `ghog full` | delete `.testmondata`, full suite with `--testmon` and coverage |
| `pta` | `ghog affected` | testmon-selected tests, `--cov-append`, coverage report |
| `ptanc` | `ghog affected --no-cov` | testmon-selected tests, no coverage |
| `pts` | `ghog single <test files>` | named test files in focus, no coverage, compared with the last full-run baseline |
| — | `ghog init` | register the skill pointers in the project |
| — | `ghog exclude "<node id>" <seconds>` | accept a genuinely slow call at its measured time |

`ghog full` stays on a single worker: testmon does not cooperate with
xdist, and the rebuilt database keeps every later `ghog affected` cheap.

## 🚦 Exit codes

| Exit | Meaning | Next move |
| --- | --- | --- |
| 0 | objective met, or this step green | continue the walk, or stop on the full run |
| 2 | test failures | fix them; from a full run, `ghog single <failing files>` first |
| 3 | coverage gap | covg on the replayed Missing rows, add tests, `ghog affected` to the gate, `ghog check`, then `ghog day` |
| 4 | suite crash | make the suite robust against that exception |
| 5 | environment or setup error | read the printed reason; looping cannot fix it |
| 6 | a run is live | poll `ghog status` until `state=done`, start nothing |
| 7 | the last run is lost | only from `ghog status`: killed or never recorded; relaunch `ghog day` |
| 8 | duration outlier on a green run | shorten the named slow calls, or `ghog exclude`, then `ghog day` |
| other | `ghog check` passthrough | fix compile or lint errors; split a file over the line limit |

## 🏁 The closing line

```txt
myproject: ghog full done fail=0 warn=0 xfail=11 cov=100 exit=0
```

`cov=` reads `skipped` (not measured), `withheld` (failures hide it),
`unread` (TOTAL line missing — a loud setup error), or the percentage. The
exit code, not the text, is the branching signal. A `check.bat` printing
`ERROR :` lines while exiting 0 is treated as failed anyway (ANSI colors
stripped before matching).

## 🖥️ Output modes

TTY auto-detection, forced with `--user` or `--llm`. User mode shows a
progress bar with live counters; LLM mode prints one plain line per 10% of
collected tests plus one per 60 silent seconds, for example
`ghog full: 50% (125/250) fail=2 warn=1 xfail=0`. Both end with the same
next-step message and closing line.

## 🔄 Run lifecycle

Every run brackets itself atomically in `a.ghog.status`:

```txt
myproject: ghog day state=running pid=18244 started=2026-06-12T20:40:12+02:00
myproject: ghog day state=done exit=3 ended=2026-06-12T21:02:41+02:00
```

| ghog status sees | Exit | Meaning |
| --- | --- | --- |
| `state=done exit=N` | N | finished; branch on N, read the log tail |
| `state=running`, pid alive | 6 | still working; poll again |
| `state=running`, pid dead | 7 | killed mid-walk; relaunch `ghog day` |
| no status file | 7 | nothing recorded; run `ghog day` |

Only `ghog status` can probe the pid; a direct read of the file cannot
tell a live run from a killed one. Exit 6 also protects the walk: a second
run refuses to start while one is alive. A recycled pid can keep a killed
run reading as live — break that verdict by deleting `a.ghog.status`.

## 🐢 The duration gate in detail

The full run times the call phase of every test. A call is flagged as an
outlier — exit 8 on an otherwise-green run — only when two conditions
hold at once:

- its Iglewicz-Hoaglin modified z-score (median and MAD based, cutoff
  3.5) says it sits far outside the norm of this run,
- its call time is at or above the gate floor in seconds.

When more than half the calls tie and the MAD collapses to zero, the
z-score is undefined and the rule falls back to the floor alone. The
report also names up to three under-floor runners-up, the data for tuning
the floor.

The gate is configured through `a.ghog.outliers` at the project root:

```txt
0.0                                   line 1: auto floor, 10 x median (record only)
1.0                                   line 2: the gate floor the rule uses
[exclusion]
tests/unit/pkg/test_mod.py::test_x = 11.41
```

- line 1 is a write-only record of `10 x median` for this run — the gate
  never reads it back,
- line 2 is the knob: default `1.0` second, seeded on a fresh run; raise
  it to tolerate slower calls, lower it to catch faster ones, set it to
  `0` to switch the gate off; a missing, malformed or negative value
  falls back to the default, and deleting the file re-seeds it,
- each `[exclusion]` entry (written by `ghog exclude`) spares one node id
  at its recorded baseline; excluded calls are left out of the average
  and classified against that baseline on every run: `ok`, `slower`,
  `faster` or `stale`; an entry whose call drops back under half the
  floor is removed by the tool, returning the test to the normal rule.

## ⚙️ Configuration read by ghog

The coverage gate is `fail_under` (default 100) from `pyproject.toml`,
`.coveragerc` or `setup.cfg`. The duration gate reads its floor and
exclusions from `a.ghog.outliers` (see above). The full spec, decision
table and acceptance tests, lives in `tools/Pytest reset specs.md`.

Related: [Fix a red groundhog walk](../how-to/fix-a-red-groundhog-walk.md),
[Groundhog as a reset loop](../explanation/groundhog-as-a-reset-loop.md).
