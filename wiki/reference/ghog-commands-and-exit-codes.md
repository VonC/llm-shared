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
| — | `ghog day` | check, then `affected --no-cov`, with an optional full step at the selected level; stops at the first non-green step; valid saved proof can make it a noop (`--force` overrides); `--detach` runs a survivor process observed through `ghog status` |
| — | `ghog status` | replay the run lifecycle from `a.ghog.status` without starting anything |
| — | `ghog check` | run `check.bat` from the project root, exit code passed through |
| `ptr` | `ghog full` | selected suite at `speed` by default; the default sequential mode rebuilds `.testmondata` with `--testmon` for the whole suite, and keeps it with `--testmon-noselect` for a group |
| `pta` | `ghog affected` | testmon-selected tests, `--cov-append`, coverage report |
| `ptanc` | `ghog affected --no-cov` | testmon-selected tests, no coverage |
| `pts` | `ghog single <test files>` | named test files in focus, no coverage, compared with the last full-run baseline |
| — | `ghog timings` | sequential, uninstrumented whole-suite pass that judges the duration gate |
| — | `ghog init` | register the skill pointers in the project |
| — | `ghog exclude "<node id>" <seconds>` | accept a genuinely slow call at its measured time |
| — | `ghog groups [name]` | validate group declarations and print patterns and resolved test/source counts |
| — | `ghog exclude --list [--since=<saved-list>]` | list effective exclusions, or compare them with saved evidence |

## Full-suite levels

`check`, `full`, `affected`, `single`, and `day` accept `--full=pass|cov|speed`.
Selection is the explicit parameter, then nonempty `GHOG_FULL`, then the command
default. `full` defaults to `speed`; the others default to internal `none`.
An explicit `none`, empty value, or unknown level fails with exit 5.
`timings`, `status`, `init`, `groups`, and `exclude` do not read `GHOG_FULL`.

| Level | Full-step gates |
| --- | --- |
| `pass` | All selected tests pass; no coverage or duration verdict |
| `cov` | Passing tests and the coverage gate |
| `speed` | Passing tests, coverage, and the duration gate |

Plain `ghog day` runs check and affected tests only unless `GHOG_FULL` selects
a full step. `--full` selects the walk objective; it does not turn a direct
`check`, `affected`, or `single` call into a full-suite run.

## Test groups and explicit scopes

The level-capable commands accept exactly one of `--group=<name>`,
`--whole-suite`, or `--scope-file=<capture>`. An explicit selector overrides
`GHOG_GROUP`; otherwise nonempty `GHOG_GROUP` selects a group, and the default
is the whole suite. `timings` remains a whole-suite command.

Declare groups in the project-root `.ghog-groups`:

```ini
[parser]
tests =
    /tests/unit/parser/
sources =
    /src/parser/
```

Names match `[a-z][a-z0-9_-]*`. Each section requires both `tests` and `sources`,
with nonempty resolved membership; `DEFAULT` patterns are forbidden. Inventory
is Python files only. Test membership follows pytest's configured `python_files`
and excludes `conftest.py`; coverage omit rules apply to source membership.

Patterns use `/` after backslash normalization. Blank lines and `#` comments
are ignored. A slash-free pattern matches basenames at any depth; a leading
`/` anchors at the root. Directory patterns include descendants, `**` recurses,
`!` excludes, and the last matching pattern wins. Grouped coverage measures
the group's resolved sources. Group proof never proves the whole suite.

A scope capture records patterns, ordered membership, and fingerprint.
`--scope-file` validates that capture instead of selecting today's declaration
or environment. `ghog groups` is read-only: exit 0 means valid declarations,
and exit 5 means invalid input or membership. Exclusion listings also leave
proof and run lifecycle untouched. A `--since` comparison reports `changed`,
`unchanged`, or `unverified`; invalid evidence exits 5.

## Saved day proof

A green day stores proof in the artifact home: `a.ghog.day.ok` for the whole
suite, or `a.ghog.day.<group>.ok` for a group. Each marker contains five
`key=value` lines: `scope`, `fingerprint`, `timing`, `digest`, and `proof`.
The digest covers Python files and gate configuration; the scope fingerprint
must match too. Legacy one-line snapshots provide no valid proof.

Valid proof at or above the requested level skips the entire walk, including
`check.bat`. An upgrade from a lower valid proof reuses check and affected tests
and runs the full step at the requested level. Changing the duration floor or
exclusions caps a saved `speed` proof at `cov`. A failed judged gate lowers
proof below that gate; a setup failure or interruption without a verdict
preserves prior proof. Direct `ghog full` reports earned proof but never reads
or writes a day marker.

## Sequential and parallel full runs

`ghog full` stays on a single worker by default: testmon does not cooperate
with xdist, and the rebuilt database keeps every later `ghog affected` cheap.
A project opts its full run into workers by adding a `.ghog-parallel` marker
at its root, which runs `-n auto --dist loadgroup` so a module carrying an
`xdist_group` mark keeps its module-scoped fixtures on one worker. Parallel
mode omits `--testmon` and leaves the existing testmon database untouched;
`ghog affected` still uses that database. A parallel full run skips the
duration gate, because a contended call time measures the
scheduler rather than the test. Direct parallel `full --full=speed` earns at
most `cov` proof. A parallel `day --full=speed` follows the full step with
sequential, uninstrumented timings before earning `speed` proof.

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
| 9 | not a pytest project (no pytest marker at the root) | groundhog has no test step here; validate with the project's own test commands |
| other | `ghog check` passthrough | fix compile or lint errors; split a file over the line limit |

## 🏁 The closing line

```txt
myproject: ghog day done fail=0 warn=0 xfail=11 cov=100 exit=0 full=cov src=param proof=cov reused=none scope=whole
```

`cov=` reads `skipped` (not measured), `withheld` (failures hide it),
`unread` (TOTAL line missing — a loud setup error), or the percentage. The
exit code, not the text, is the branching signal. A `check.bat` printing
`ERROR :` lines while exiting 0 is treated as failed anyway (ANSI colors
stripped before matching).

Day evidence adds `full`, `src` (`param`, `env`, or `default`), `proof`,
`reused` (`none`, `check+affected`, or `all`), and `scope` (`whole` or
`group:<name>`). Direct full evidence adds level, source, proof, and scope;
other runs carry scope only. A running record uses `proof=pending`.

## 🖥️ Output modes

TTY auto-detection, forced with `--user` or `--llm`. User mode shows a
progress bar with live counters; LLM mode prints one plain line per 10% of
collected tests plus one per 60 silent seconds, for example
`ghog full: 50% (125/250) fail=2 warn=1 xfail=0`. Both end with the same
next-step message and closing line.

Environment activation output is parked in `a.ghog.senv.log`, in the
artifact home, and replayed by default; an LLM run keeps the raw text in
`a.ghog.senv.txt` there, behind one summary line naming its path. Defining `GHOG_SENV_LIVE` streams that setup output immediately.
The interactive `ghdy`, `gha`, `ghc`, `ghf`, and `ghs` aliases select live
setup output for `day`, `affected`, `check`, `full`, and `single` respectively.

`bin\ghog_cycle.bat` activates the project environment once, then runs each
argument as a ghog subcommand line. With no arguments it runs `day` alone,
following the normal level selection; a nonzero phase stops the sequence and
supplies its exit code. Pass `"day --full=speed"` for the complete speed gate.
The wrapper sets `GHOG_SENV_READY` for its child calls after activation.
An inherited `NO_MORE_SENV_<project>` guard alone does not bypass setup.

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

The sequential full run at `speed` and `ghog timings` measure each test's call phase.
A call is flagged as an
outlier — exit 8 on an otherwise-green run — only when two conditions
hold at once:

- its Iglewicz-Hoaglin modified z-score (median and MAD based, cutoff
  3.5) says it sits far outside the norm of this run,
- its call time is at or above the gate floor in seconds.

When more than half the calls tie and the MAD collapses to zero, the
z-score is undefined and the rule falls back to the floor alone. The
report also names up to three under-floor runners-up, the data for tuning
the floor.

The gate is configured through `a.ghog.outliers` in the artifact home
(`.reviews` unless `.review-artifacts.ini` declares another home); a copy
an older version left at the project root is moved there on first use,
its floor and exclusions kept:

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
exclusions from the artifact-home `a.ghog.outliers` (see above). The full spec, decision
table and acceptance tests, lives in `tools/Pytest reset specs.md`.

Related: [Groundhog as a reset loop](../explanation/groundhog-as-a-reset-loop.md),
[Fix a red groundhog walk](../how-to/fix-a-red-groundhog-walk.md).
