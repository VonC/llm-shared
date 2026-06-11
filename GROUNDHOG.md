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
           |             gate, finish with ghog check
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

## Subcommands and console aliases

| Alias | Subcommand | Behavior |
| --- | --- | --- |
| (none) | `ghog day` | walk the chain: check, then `affected --no-cov`, then `full`, stopping at the first non-green step; a noop when nothing changed since the last green walk (`--force` overrides) |
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
| 3 | coverage gap | covg on the replayed Missing rows, add tests, `ghog affected` to the gate, `ghog check` |
| 4 | suite crash | act on the crash block: make the suite robust against that exception |
| 5 | environment or setup error | read the printed reason; looping cannot fix it |
| other | `ghog check` passthrough | check.bat's own exit code: fix the compile errors |

A check.bat that prints `ERROR :` lines yet exits 0 is treated as failed (exit 1) with an explicit mismatch notice, so a broken check script can never green-light the walk.

## Output modes of groundhog

The mode is picked by TTY auto-detection, with `--user` and `--llm` force flags:

- **user mode** (a console): a tqdm progress bar whose postfix carries the live counters — `fail= warn= xfail=` and `cov=` once parsed — then the final report.
- **LLM mode** (captured output): no bar; one plain progress line at every 10% of the collected tests, plus one whenever 60 seconds pass without any, such as `ghog full: 50% (125/250) fail=2 warn=1 xfail=0`; then the final report.

Both modes end with the same next-step message and closing line, so a user reading over the LLM's shoulder sees the same numbers.

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
| check.bat failing | the check.bat output | `Next: fix the compile errors above, re-run ghog check` |
| affected failing | full failure context | `Next: fix these, re-run ghog affected --no-cov until green, then ghog full` |
| full failing | full tracebacks, baseline written to `a.ghog.failures` | `Next: ghog single <failing test files>` |
| focus run (`ghog single`) | the two lists: still failing in focus (fix first), passing in focus but failing in the full suite (interaction suspects, fix second) | `Stay on ghog single until green, then restart at ghog check` |
| coverage gap | the term-missing rows under `Uncovered lines` — the covg input | `Next: covg <file> <ranges> ... add tests, verify with ghog affected` |
| affected at the gate | — | `Coverage gate reached - no ghog full needed; finish with ghog check (new tests are code too)` |
| crash | last 5 started tests, stack tail | the immediate-fix instruction: make the suite robust against that exception |
| nothing affected | — | `0 tests ran in this step (testmon: nothing affected since the last run) - treated as green` |

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
- When the harness truncates long output, redirect one run to a log and read its tail, then delete the log.

## Coverage gaps and covg

On exit 3, the report replays the pytest term-missing rows under an `Uncovered lines` header. The `Missing` column is exactly the input of the covg tool:

```txt
cmd /d /v:on /c "senv.bat && ..\llm-shared\bin\covg.bat src\pkg\mod.py 48 86-88 100"
```

covg names the enclosing functions and branches of those lines and builds a ready-to-paste test-coverage prompt. Never generate or parse a `coverage.json` export — it is huge, and everything covg needs is already in the replayed rows. Verify the new tests with `ghog affected` only (coverage appends across runs); when it reports the gate is reached, finish with one `ghog check` — new tests are code too — and the objective is met without another full run.

## Files groundhog reads and writes

| File | Role |
| --- | --- |
| `.testmondata` | the testmon database; deleted and rebuilt by `ghog full`, consumed by `ghog affected` |
| `a.ghog.failures` | the failing node ids of the last full run, the focus-comparison baseline; emptied on a green full run |
| `a.ghog.day.ok` | the source snapshot of the last green `ghog day` walk; an unchanged snapshot makes the next walk a noop |
| `pyproject.toml` / `.coveragerc` / `setup.cfg` | where the coverage gate (`fail_under`) is read from, default 100 |
| `a.ghog.log` (optional) | the redirect target suggested to sandboxed harnesses; delete it when the loop ends |

All of them are covered by the usual `a.*` and `.testmondata*` ignore patterns.

## Troubleshooting groundhog

- **The walk continued past a failing check.bat**: your check.bat exits 0 despite failing (a known template bug cleared its status variable before the final `exit /b` read it). ghog detects the `ERROR :` lines — including colored ones, since the guard matches with ANSI escape codes stripped — and fails the step anyway; still, fix the script by stashing the exit code before its cleanup.
- **`--- Logging error ---` tracebacks in a captured log**: an older ghog crashed its logging handler on characters outside the console code page (the box-drawing output of ty); the stdout logger now replaces them with placeholders instead.
- **The affected step shows no progress lines and passes instantly**: nothing was affected since the last run; the report says so explicitly. The step did run.
- **`cov=unread` with exit 5**: the coverage TOTAL line was missing from the pytest output; the gate cannot be judged, on purpose loudly.
- **First run is slow**: the first `ghog affected` after a reset starts from an empty testmon database and runs everything once; that rebuild is what makes every later affected run cheap.
- **`/groundhog` unknown in Codex**: re-run `ghog init` (it writes `~/.codex/prompts/groundhog.md` when `~/.codex` exists) and start a fresh session.

## Related groundhog documents

- [tools/Pytest reset specs.md](tools/Pytest%20reset%20specs.md) — the full specification with its decision table (Q01-Q27) and acceptance tests (AT1-AT15).
- [instructions/groundhog.md](instructions/groundhog.md) — the fixing loop both LLM harnesses follow.
- [DEVELOPMENT.md](DEVELOPMENT.md) — where the walk fits in the overall step-based workflow.
