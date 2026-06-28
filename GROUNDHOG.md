# Groundhog: the pytest reset tool

groundhog (alias `ghog`) drives a project to one objective: **every test passes on the full suite, and coverage reaches the project gate** (`fail_under`, default 100). Like the movie, it relives the same day — compile check, affected tests, full suite with a freshly reset coverage measure — until the result is flawless.

It replaces the old `ptr` / `pta` / `pts` doskey aliases with one Python tool whose output is mastered for two audiences at once: small enough for an LLM token budget, alive enough for a user terminal. The full specification lives in [tools/Pytest reset specs.md](tools/Pytest%20reset%20specs.md); this document is the user manual.

## What groundhog does

- One entry point, `bin\ghog.bat`, with subcommands for each workflow step and thin `ptr`/`pta`/`ptanc`/`pts` wrappers for muscle memory.
- A single walk command, `ghog day`, that runs the whole chain in order and stops at the first non-green step — the one command that answers "where am I?".
- A registration command, `ghog init`, that wires the fixing loop into a project for both Claude Code and ChatGPT Codex.
- A fixing loop for LLMs, [instructions/groundhog.md](instructions/groundhog.md): run the walk, apply the fix its report names, run the walk again, until the objective is reached.

Every wrapper loads `senv.bat` itself, inside its own cmd process, so a single call is self-contained from any shell — a user console, Claude Code, or the Codex sandbox (where environment changes never survive between tool calls).

## The groundhog walk at a glance

`ghog day` executes the steps below in order. Each step only runs when the previous one passed; the walk stops at the first non-green step, and the last report on screen always names the fix to apply.

```txt
   +------------------------------------------+
   |  ghog day   (one self-contained call;    |
   |  the wrapper loads senv.bat itself)      |
   +-------+----------------------------------+
           |
           v
   +------------------------------------------+
   |  1. check          check.bat             |
   |     pass: exit 0 and no ERROR lines      |
   |     missing check.bat: skip with notice  |
   +-------+----------------------------------+
           |  non-zero -> STOP
           |  (fix the compile errors, restart)
           v
   +------------------------------------------+
   |  2. affected --no-cov        (ptanc)     |
   |     testmon-selected tests, fast         |
   |     0 tests selected = green, says so    |
   +-------+----------------------------------+
           |  exit 2 -> STOP
           |  (fix, re-run this step to green,
           |   then restart the walk)
           v
   +------------------------------------------+
   |  3. full                     (ptr)       |
   |     del .testmondata, full suite,        |
   |     coverage measured against the gate   |
   +-------+----------------------------------+
           |
           +-- exit 2 -> STOP: ghog single <failing files>,
           |             fix the two lists, restart
           +-- exit 3 -> STOP: covg on the Missing rows,
           |             add tests, ghog affected to the
           |             gate, ghog check, then ghog day
           +-- exit 4 -> STOP: crash block, harden the suite
           +-- exit 5 -> STOP: setup error, not loopable
           v
   +------------------------------------------+
   |  exit 0: Objective reached               |
   |  fail=0, coverage at the gate (+ nag)    |
   +------------------------------------------+
```

## The day snapshot: duplicate walks are free

A fully green `ghog day` records a source snapshot, `a.ghog.day.ok`: a digest over the path, size and mtime of every Python file plus the gate configuration files (pyproject.toml, .coveragerc, setup.cfg, check.bat). The next `ghog day` checks it first — when nothing changed, the walk is a noop:

```txt
No Python file changed since the last green ghog day walk - nothing to do (use --force to walk anyway)
pdfsplitter: ghog day done fail=0 warn=0 xfail=0 cov=skipped exit=0
```

So instructions that each end with a walk (a split flow inside an implement flow, for example) can both call `ghog day` without paying twice. Any file change, addition or removal re-arms the walk; `ghog day --force` walks regardless; only the day walk writes the marker (a standalone green `ptr` proves the suite but not the compile check, so it records nothing).

## The fixing loop around the walk

The walk never fixes anything: it walks, gates, and reports. The fixing belongs to the caller — you, or an LLM following [instructions/groundhog.md](instructions/groundhog.md):

```txt
   +------------+     non-zero exit     +------------------------+
   |  ghog day  | --------------------> |  apply the fix named   |
   +-----+------+                       |  by the final report   |
         ^                              +-----------+------------+
         |                                          |
         +------------------------------------------+
          restart the walk after every fix; stop when an
          iteration makes no progress (failures not lower,
          coverage not higher), and never beyond 10 iterations
```

The walk is also the loop's only re-entry point. After a fix, the next command is `ghog day` itself — never a standalone subcommand run first as a confirmation: a `ghog check` right before a walk pays check.bat twice, since the walk opens with that same check. The subcommands the branches name (`ghog single`, `ghog affected --no-cov`, covg plus `ghog affected`, and the coverage branch's final `ghog check`) are inner verifiers, cheaper than a walk while one branch is being fixed, and each inner loop ends by handing back to `ghog day`.

## Subcommands and console aliases

| Alias | Subcommand | Behavior |
| --- | --- | --- |
| (none) | `ghog day` | walk the chain: check, then `affected --no-cov`, then `full`, stopping at the first non-green step; a noop when nothing changed since the last green walk (`--force` overrides); `--detach` runs the walk as a survivor process polled through `ghog status` |
| (none) | `ghog status` | replay the run lifecycle recorded in `a.ghog.status` without starting anything: the recorded exit code once done, 6 while a run is live, 7 when the last run is lost |
| (none) | `ghog check` | run check.bat from the project root, exit code passed through |
| ptr | `ghog full` | delete `.testmondata`, full suite with `--testmon` and coverage |
| pta | `ghog affected` | testmon-selected tests, `--cov-append`, coverage report |
| ptanc | `ghog affected --no-cov` | testmon-selected tests, no coverage |
| pts | `ghog single <test files>` | named test files (files, not functions), no coverage, `-rxX` |
| (none) | `ghog init` | register the skill pointers in the project (see below) |

The aliases are doskey macros from `senv.doskey`, available after `senv.bat`; the `bin\*.bat` wrappers behind them work from any shell, loaded or not. `ghog full` stays on a single worker on purpose: pytest-testmon does not cooperate with pytest-xdist, and the rebuilt testmon database is what keeps every later `ghog affected` run cheap.

## Exit codes and the closing line

Every run ends with a closing key=value line merging the old alias echo with the final numbers:

```txt
pdfsplitter: ghog full done fail=0 warn=0 xfail=11 cov=100 exit=0
```

The keys are the contract; `cov=` reads `skipped` (not measured), `withheld` (failures hide it), `unread` (TOTAL line missing, a loud setup error) or the percentage. The exit code is the branching signal:

| Exit | Meaning | Next move |
| --- | --- | --- |
| 0 | objective met (or this step green) | continue the walk, or stop on the full run |
| 2 | test failures | fix them; from a full run, `ghog single <failing files>` first |
| 3 | coverage gap | covg on the replayed Missing rows, add tests, `ghog affected` to the gate, `ghog check`, then `ghog day` |
| 4 | suite crash | act on the crash block: make the suite robust against that exception |
| 5 | environment or setup error | read the printed reason; looping cannot fix it |
| 6 | a run is live (Q32) | wait; poll `ghog status` until `state=done`, start nothing |
| 7 | the last run is lost (Q32) | only from `ghog status`: the run was killed or never recorded; relaunch `ghog day` |
| 8 | a duration outlier on an otherwise-green run (Q34) | the full suite passed and met the coverage gate, but a test call ran far outside the norm; shorten the named slow calls (see [`instructions/fix_slow_test.md`](instructions/fix_slow_test.md)), or `ghog exclude` a genuinely slow one, then re-run `ghog day` |
| other | `ghog check` passthrough | check.bat's own exit code: fix what it names — compile/lint errors in place, or a file over the line limit ("Big files found") by splitting it with `/split-large-file` (ghog reports the over-limit files, it never splits) |

A check.bat that prints `ERROR :` lines yet exits 0 is treated as failed (exit 1) with an explicit mismatch notice, so a broken check script can never green-light the walk.

Beyond pass/fail and coverage, the full run also times every test call, so `ghog day` trims test execution time: a call running far outside the norm (a robust outlier score, at or above a one-second floor) keeps the walk on exit 8 with the slow calls named, judged last so it never masks a failure or a coverage gap. The named calls are shortened (`instructions/fix_slow_test.md`: fake the slow resource, the clock, or shrink the data) or, when a call is legitimately slow, accepted at its measured time with `ghog exclude`. That is how the suite stays fast, the project target being under one second per test.

## Output modes of groundhog

The mode is picked by TTY auto-detection, with `--user` and `--llm` force flags:

- **user mode** (a console): a tqdm progress bar whose postfix carries the live counters — `fail= warn= xfail=` and `cov=` once parsed — then the final report.
- **LLM mode** (captured output): no bar; one plain progress line at every 10% of the collected tests, plus one whenever 60 seconds pass without any, such as `ghog full: 50% (125/250) fail=2 warn=1 xfail=0`; then the final report.

Both modes end with the same next-step message and closing line, so a user reading over the LLM's shoulder sees the same numbers.

## The LLM redirect: a.ghog.log

The redirect starts in the invocation. [instructions/groundhog.md](instructions/groundhog.md) makes every LLM-driven ghog call one redirected shell call — `cmd /d /c "<llm-shared>\bin\ghog.bat <subcommand> > a.ghog.log 2>&1"` — while ghog itself keeps writing to stdout: a user typing `ghog day` in a console sees the usual bar and report, with no log file involved.

The redirected form buys three things at once:

- **A small token bill.** Whatever a harness captures from a command lands in the LLM context and stays there for every later turn of the loop. Redirected, a run hands back only its exit code; the model branches on it and reads just the log tail — the last 5 lines on a green run (closing and nag lines), the last 100 on a stop. Ten loop iterations cost ten bounded tail reads instead of ten full reports sitting in the conversation.
- **Live following.** A harness shows a command's output only once the call returns; the log fills while the run progresses. Watching `a.ghog.log` from a second console shows the LLM-mode progress lines in real time — the same numbers the model itself skips.
- **Truncation immunity.** When a sandboxed harness cuts long output, the full report still sits on disk; the tail read never loses the verdict lines at the end of the report.

Lifecycle of the file: each run overwrites it (`>`, not append), so its tail is always the current run; it is never deleted, so the last report stays readable after the loop ends; the `a.*` ignore pattern keeps it out of git; and the day snapshot never digests it (Python files and gate configuration only), so writing it cannot re-arm a walk.

The tool also backstops a forgotten redirect (Q31): when stdout turns out to be a harness capture — a pipe, or a regular file other than the project's own `a.ghog.log` — the run writes its full report to `a.ghog.log` anyway and hands the capture only an envelope: one notice naming the log, then the next-step and closing lines, so the caller still branches on the exit code without one unbounded line landing in its context. The senv.bat preamble of ghog.bat is parked in a side file, `a.ghog.senv.log`, that the tool replays into the report stream and deletes; ghog.bat types a leftover side file itself when the tool never ran, keeping the sandbox-block markers visible. The redirected call above stays the form to type — the guard is the safety net, not the contract.

covg runs are the one exception: their output is exactly the data the model needs in full, so they are never redirected. `ghog status` is the other one: its two-line envelope needs no redirect, and a redirect to `a.ghog.log` would truncate the live walk's log before the tool could refuse.

## The run lifecycle: a.ghog.status and ghog status

A growing `a.ghog.log` does not prove a walk is alive, and a quiet one does not prove it finished: a real session lost a walk to a harness tool timeout while the orphaned pytest child kept feeding the log, and the agent — left guessing from tail reads and process listings — replayed the whole walk. Completion is a file contract instead (Q32). Every run subcommand (check, full, affected, single, day) brackets itself in `a.ghog.status` at the project root, atomically:

```txt
pdfsplitter: ghog day state=running pid=18244 started=2026-06-12T20:40:12+02:00
pdfsplitter: ghog day state=done exit=3 ended=2026-06-12T21:02:41+02:00
```

The `done` line lands on every exit path, a crashing run included; a hard kill is the one event that leaves `state=running` behind with a dead pid. `ghog status` reads that file — and nothing else — without starting anything:

| ghog status sees | Exit | Meaning and next move |
| --- | --- | --- |
| `state=done exit=N` | N | the run finished; branch on N exactly like on a foreground walk, read the log tail |
| `state=running`, pid alive | 6 | the run is still working; poll again, start nothing |
| `state=running`, pid dead | 7 | the run was killed mid-walk; relaunch `ghog day` |
| no status file | 7 | nothing recorded; run `ghog day` |

The command is also the only reader: a direct read of `a.ghog.status` cannot probe the pid, so a killed run keeps reading `state=running` forever — the exit-7 verdict exists only through `ghog status`.

The same exit 6 protects the walk itself: any run command started while another run is alive refuses before spawning anything, so a second walk can never truncate the first one's log or corrupt its testmon state.

When the harness kills long calls (tool timeouts you do not control), run the walk detached:

```txt
cmd /d /c "..\llm-shared\bin\ghog.bat day --detach"
```

No redirect: the tool opens `a.ghog.log` itself for a survivor process — a hidden console (its console children inherit it instead of popping a visible window), broken away from the harness job object when allowed — folds the senv preamble in, waits for the child's first status write, and returns exit 6 at once. From there the loop is: poll `ghog status`, branch on its exit code — no closer than 60 seconds apart, preferring minutes on a full walk: the progress cadence is one line per 10% with a 60-second silence floor, so a tighter poll cannot show anything new, and a progress report needs at most the last 5 lines of `a.ghog.log`. No timeout to pick, no upper bound to guess — across projects, a portable one does not exist.

One caveat: a recycled pid can keep a killed run reading as live; that conservative verdict is broken by deleting `a.ghog.status`.

## What success looks like

A green `ghog day` walk prints one closing line per step and ends on the full run's objective report:

```txt
pdfsplitter: ghog check done fail=0 warn=0 xfail=0 cov=skipped exit=0
pdfsplitter: ghog affected --no-cov done fail=0 warn=0 xfail=0 cov=skipped exit=0
Objective reached
nag: warn=0 xfail=11 worth a look
pdfsplitter: ghog full done fail=0 warn=0 xfail=11 cov=100 exit=0
```

The nag line appears only on success, when warnings or expected failures remain worth a look; they never block the objective.

## What each stop looks like

| Stop | Report carries | Next-step message |
| --- | --- | --- |
| check.bat failing | the check.bat output | `Next: fix the compile errors above, re-run ghog day (the walk opens with this check)` |
| affected failing | full failure context | `Next: fix these, re-run ghog affected --no-cov until green, then ghog day` |
| full failing | full tracebacks, baseline written to `a.ghog.failures` | `Next: ghog single <failing test files>` |
| focus run (`ghog single`) | the two lists: still failing in focus (fix first), passing in focus but failing in the full suite (interaction suspects, fix second) | `Stay on ghog single until green, then restart the walk: ghog day` |
| coverage gap | the term-missing rows under `Uncovered lines` — the covg input | `Next: covg <file> <ranges> ... add tests, verify with ghog affected` |
| affected at the gate | — | `Coverage gate reached - run ghog check (new tests are code too), then ghog day` |
| crash | last 5 started tests, stack tail | the immediate-fix instruction: make the suite robust against that exception |
| nothing affected | — | `0 tests ran in this step (testmon: nothing affected since the last run) - treated as green` |

Every next-step message that follows a fix names `ghog day` directly (Q30): the walk is the loop's only re-entry point and its first step is the check, so no standalone `ghog check` run is ever needed before it (see [instructions/groundhog.md](instructions/groundhog.md)).

## Registering groundhog in a project: ghog init

From the project root (console or LLM shell):

```txt
ghog init
```

It writes three pointers, all referencing the single instruction file `instructions/groundhog.md` of llm-shared:

- `.claude\skills\groundhog\SKILL.md` — the Claude Code skill, discovered from the project's `.claude\skills`, with the trigger phrases in its description and a relative link computed from your actual layout (sibling `..\llm-shared` and submodule `llm-shared` both work).
- a `## groundhog` section in `AGENTS.md` at the project root — the Codex channel. An existing AGENTS.md is never rewritten: the section is appended once, recognized on later runs (detection anchored at a line start), and a non-UTF-8 file is left byte-identical with a loud exit 5.
- `~/.codex/prompts/groundhog.md` — a user-level Codex custom prompt making `/groundhog` deterministic, written only when `~/.codex` exists. It is project-agnostic: it routes through the current project's AGENTS.md section, so one copy serves every repository.

Re-running `ghog init` is safe and idempotent. Two caveats: a freshly written AGENTS.md is only seen by Codex sessions started after it exists, and an already-registered AGENTS.md section is never updated — delete the `## groundhog` section and re-run `ghog init` to refresh its wording.

## Triggering groundhog from Claude Code

After `ghog init`, either form works:

- `/groundhog` — the skill, deterministic.
- "run groundhog" (or "fix tests and coverage", "reach 100% coverage") — matched from the skill description.

Claude Code then follows [instructions/groundhog.md](instructions/groundhog.md): the `ghog day` walk, the per-exit fixes, the stop conditions.

## Triggering groundhog from ChatGPT Codex

After `ghog init` (and a fresh Codex session, so the new AGENTS.md is loaded):

- `/groundhog` — the user-level custom prompt, deterministic.
- "run groundhog" — routed by the AGENTS.md section, which states explicitly that there is no `groundhog` executable to run and that senv.bat is never a separate step (both misreadings were observed in a real session).

Codex sandbox notes, also spelled out in the instruction file:

- ghog and covg calls need real filesystem access (senv.bat reads user-profile paths); run them with escalated (approved) execution from the start.
- Output containing `Access is denied`, `gum choose` or `Unable to create virtual env` means the sandbox blocked senv.bat: re-run the exact same command escalated; never debug senv.bat, never create a virtual environment, never pick a Python version.
- Harness output truncation is a non-event: every LLM-driven run is redirected to `a.ghog.log` by the standard invocation form — and the Q31 guard writes the log even when the redirect was forgotten — so the full report is always on disk; the model reads the tail and never deletes the file.
- Harness tool timeouts on long walks are covered by `ghog day --detach` plus `ghog status` polls (Q32): the walk runs as a survivor process the timeout cannot reach, and completion is read through `ghog status`, never guessed from the log or from a direct read of `a.ghog.status`.

## Coverage gaps and covg

On exit 3, the report replays the pytest term-missing rows under an `Uncovered lines` header. The `Missing` column is exactly the input of the covg tool:

```txt
cmd /d /v:on /c "senv.bat && ..\llm-shared\bin\covg.bat src\pkg\mod.py 48 86-88 100"
```

covg names the enclosing functions and branches of those lines and builds a ready-to-paste test-coverage prompt. Never generate or parse a `coverage.json` export — it is huge, and everything covg needs is already in the replayed rows. Verify the new tests with `ghog affected` only (coverage appends across runs); when it reports the gate is reached, run one `ghog check` because new tests are code too, then restart the walk with `ghog day` so check, affected tests, full coverage, and outliers are proven together.

## Files groundhog reads and writes

| File | Role |
| --- | --- |
| `.testmondata` | the testmon database; deleted and rebuilt by `ghog full`, consumed by `ghog affected` |
| `a.ghog.failures` | the failing node ids of the last full run, the focus-comparison baseline; emptied on a green full run |
| `a.ghog.day.ok` | the source snapshot of the last green `ghog day` walk; an unchanged snapshot makes the next walk a noop |
| `pyproject.toml` / `.coveragerc` / `setup.cfg` | where the coverage gate (`fail_under`) is read from, default 100 |
| `a.ghog.log` | the redirect target of every LLM-driven run, written by the Q31 guard even when the caller forgot the redirect; overwritten per run, never deleted, so the user can follow the loop live (direct human runs keep stdout) |
| `a.ghog.senv.log` | the parked senv.bat preamble of one ghog.bat call; replayed into the report stream and deleted by the tool, typed by ghog.bat itself when the tool never ran |
| `a.ghog.status` | the run lifecycle line (Q32): `state=running pid=` while a run works, `state=done exit=` after; read by `ghog status` and by the live-run refusal; cleared by a detached launch before its spawn |

All of them are covered by the usual `a.*` and `.testmondata*` ignore patterns.

## Troubleshooting groundhog

- **The walk continued past a failing check.bat**: your check.bat exits 0 despite failing (a known template bug cleared its status variable before the final `exit /b` read it). ghog detects the `ERROR :` lines — including colored ones, since the guard matches with ANSI escape codes stripped — and fails the step anyway; still, fix the script by stashing the exit code before its cleanup.
- **`--- Logging error ---` tracebacks in a captured log**: an older ghog crashed its logging handler on characters outside the console code page (the box-drawing output of ty); the stdout logger now replaces them with placeholders instead.
- **The affected step shows no progress lines and passes instantly**: nothing was affected since the last run; the report says so explicitly. The step did run.
- **`cov=unread` with exit 5**: the coverage TOTAL line was missing from the pytest output; the gate cannot be judged, on purpose loudly.
- **First run is slow**: the first `ghog affected` after a reset starts from an empty testmon database and runs everything once; that rebuild is what makes every later affected run cheap.
- **`/groundhog` unknown in Codex**: re-run `ghog init` (it writes `~/.codex/prompts/groundhog.md` when `~/.codex` exists) and start a fresh session.
- **The log kept growing after my command timed out, then went quiet without a report**: the harness killed the walk and an orphaned test runner kept writing until it finished; the walk is over only when `a.ghog.status` reads `state=done`. Run `ghog status`: exit 7 confirms the kill, and `ghog day --detach` relaunches out of the timeout's reach (Q32).
- **Every ghog command answers `a run is already live (pid=...)` with exit 6**: a previous run is still working — poll `ghog status` instead of relaunching. If that pid is provably not a ghog run (a recycled pid), delete `a.ghog.status` and relaunch.

## Related groundhog documents

- [tools/Pytest reset specs.md](tools/Pytest%20reset%20specs.md) — the full specification with its decision table (Q01-Q32) and acceptance tests (AT1-AT19).
- [instructions/groundhog.md](instructions/groundhog.md) — the fixing loop both LLM harnesses follow.
- [DEVELOPMENT.md](DEVELOPMENT.md) — where the walk fits in the overall step-based workflow.
