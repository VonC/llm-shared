# Groundhog pytest reset specs

## Purpose of groundhog

groundhog (alias `ghog`, Q01) is one Python tool plus one skill that drive a project to its global objective: every test passes in the full suite, and coverage reaches the project gate (default 100%, Q14). Like the movie, it relives the same day — compile check, affected tests, full suite with a freshly reset coverage measure — until the result is flawless.

It re-implements three doskey aliases (ptr, pta, pts) as subcommands of one entry point (Q02). The point of the rewrite is to master their output: small enough for an LLM token budget, alive enough for a user terminal. The aliases themselves stay available as thin wrappers, so daily commands keep working as typed today.

## Historical aliases replaced by groundhog

The doskey lines being replaced, kept here as the behavior reference (`pdfss` stands for `%PRJ_DIR_NAME%`, the consuming project folder name):

- ptr: `del .testmondata & pytest --testmon --no-header --cov-report term-missing:skip-covered $* & echo pdfss: pytest reset done` — full suite, fresh testmon data, coverage re-computed from scratch.
- pta: `pytest --testmon --cov-append --no-header --cov-report term-missing:skip-covered $* & echo pdfss: pytest affected done` — affected tests only, coverage appended; ptanc is the same without coverage.
- pts: `pytest --no-header --no-cov -rxX $* & echo pdfss: pytest no-cov single done` — focused run of named test files, no coverage.
- covg (kept as is, not replaced): `"%LLM_SHARED_DIR%\bin\covg.bat" $*` — names the uncovered lines and functions after a coverage run.

## The ghog command and its subcommands

One Python entry point with subcommands; thin bat wrappers keep the daily names (Q02):

| Wrapper | Subcommand | Behavior |
| --- | --- | --- |
| (none) | `ghog check` | run check.bat from the project root |
| ptr | `ghog full` | delete `.testmondata`, full suite with `--testmon` and coverage |
| pta | `ghog affected` | testmon-selected tests, `--cov-append`, coverage report |
| ptanc | `ghog affected --no-cov` | testmon-selected tests, no coverage |
| pts | `ghog single <test files>` | named test files (files, not functions), no coverage, `-rxX` |
| (none) | `ghog day` | walk the chain: check, then `affected --no-cov`, then `full`, stopping at the first non-green step (Q22); `--detach` spawns the walk as a survivor process wired to `a.ghog.log` and returns exit 6 at once (Q32) |
| (none) | `ghog init` | register the skill pointers in the consuming repo: `.claude\skills\groundhog\SKILL.md` and an `AGENTS.md` section, both referencing `instructions\groundhog.md` (Q23) |
| (none) | `ghog status` | replay the `a.ghog.status` line of the last run without starting anything: the recorded exit code passes through once done, 6 while the run is live, 7 when it is lost (Q32) |

The descriptive subcommand names are the settled contract (Q15): they live mostly in the skill instruction and in LLM transcripts, where self-description beats brevity, while the wrappers keep the short console forms, so nothing is lost on either side.

For the interactive console, `senv.doskey` maps each short name (ghog, ptr, pta, ptanc, pts) to its bat in `bin\`: an assignment in that macrofile replaces any older doskey macro of the same name, and the aliases carry no echo suffix since the closing done line (Q16) already plays that role. senv.bat only puts the consuming project's own `bin` on the PATH, so these macrofile entries are what make the short names reach the llm-shared wrappers; any leftover ptr/pta/pts doskey definitions in a project's own senv files load after the macrofile and must be removed there.

Beyond pytest, the tool also chains the environment and compile steps (Q02): its bat wrappers call `call <NUL "%PRJ_DIR%\senv.bat"` first, the pattern of `bin\python_check.bat` — senv.bat is idempotent (`NO_MORE_SENV_%PRJ_DIR_NAME%` guard), so a user who already loaded the shell pays nothing, while an LLM launching from a fresh CMD (plain CMD, no PowerShell needed) gets the project environment set up within that same call. `ghog check` then runs check.bat from the project root and passes its exit code through — in the loop, any non-zero there means fixing compile errors before any test step. When check.bat is missing, the step is skipped with a printed notice, since pytest collection still catches compile errors a moment later (Q10). One guard backs the passthrough (Q26): when check.bat prints echos-style `ERROR :` lines yet exits 0 — a real check.bat template did exactly that, its cleanup clearing the status variable before the final `exit /b` read it — ghog reports the mismatch and treats the check as failed with exit 1, so a lying check script can never green-light the walk. The guard matches and re-emits check lines with their ANSI escape sequences stripped (Q29): a real colored check.bat hid its `ERROR :` lines from the guard behind color codes, and the stripped lines also keep the LLM logs free of escape noise. The stdout logger replaces unencodable characters instead of crashing (Q29): a child line carrying characters outside the console code page (the box-drawing output of ty) used to kill the logging handler and drop the line.

`ghog full` stays on a single worker with `--testmon`: pytest-testmon does not cooperate with pytest-xdist, and the rebuilt testmon database is the point of the reset — it is what keeps every later `ghog affected` run cheap (Q05). Test selection through testmon is the parallelization budget this workflow spends on.

## Process architecture for groundhog

groundhog itself runs from the llm-shared venv, launched by its bin wrappers (the `bin\covg.bat` pattern), and installs nothing into any project venv. The pytest run is a child process spawned in the project environment prepared by senv.bat, its output streams read live by the parent (Q17). A hard crash of the suite (access violation, `os._exit`) therefore kills only the child: the parent always survives to print the crash block of Q06 and to set the exit code. If live output parsing ever proves brittle, a small pytest plugin injected into the child (via `-p` and PYTHONPATH) can emit machine-readable progress events inside this same parent-child shape; that refinement was weighed and kept as a later option, not an upfront cost (Q17).

## Invoking groundhog from LLM shells

Every LLM tool call runs in a fresh shell process, and sandboxed harnesses (the OpenAI Codex sandbox among them) confirm it the hard way: environment variables set by a separate `senv.bat` call are gone before the next call, and the senv doskey macros never exist in a non-interactive shell (Q21). The invocation contract for any LLM is therefore:

- never run senv.bat as its own step; its effect cannot survive to the next command.
- always go through the ghog bat wrappers, which chain senv.bat and the tool inside one cmd process (see [The ghog command and its subcommands](#the-ghog-command-and-its-subcommands)), so a single tool call is self-contained.
- when a non-wrapped command needs the project environment (check.bat alone, plain pytest, coverage), chain it in one invocation: `cmd /d /v:on /c ""%PRJ_DIR%\senv.bat" && <command>"` — `/c` makes cmd run the line and exit (without it the call hangs waiting for an interactive session), `/d` skips AutoRun scripts, and `/v:on` turns on the delayed variable expansion some of these scripts use.

The skill instruction file (Q13) must spell out this contract, so Claude and Codex both invoke the tool the self-contained way; when a sandbox blocks senv.bat side effects entirely, the run surfaces as exit code 5, the environment error (Q12), to be reported rather than looped on.

The `a.ghog.log` redirect of the instruction file is part of that contract, and a real my-project session showed a docs-only contract does not survive a consumer project whose own instructions predate it: the agent ran `ghog day` unredirected five times, paying the full report per walk into its context and losing one run to a harness timeout. The tool therefore guards itself (Q31). When stdout is a harness capture — a pipe, or a regular file other than the project's `a.ghog.log` (some harnesses capture into a temp file) — the run writes its full report to `a.ghog.log` at the project root and hands the capture only an envelope: a notice naming the log, then the next-step, setup-reason, nag and closing lines, so exit-code branching and the next step never need a log read. A stdout that already is the project's `a.ghog.log` streams as before, the caller redirect and the guard landing in the same file; a terminal stays user mode (Q03). The senv.bat preamble of ghog.bat streams before the tool starts, so the wrapper parks it in a side file, `a.ghog.senv.log`, that cli.py replays into the report stream and deletes; a side file surviving the python call means the tool never ran, and the wrapper types it itself so the sandbox-block markers (`Access is denied`, `gum choose`) stay visible for the escalation rule.

The redirect alone still left one hole, seen in another real my-project session: a harness tool timeout killed a foreground `ghog day` mid-suite, the orphaned pytest child kept feeding `a.ghog.log` — the affected step, then the full suite up to its 90% progress line — and the report, the coverage step and the exit code never came. With the log moving and no completion proof, the agent improvised sleeps, tail reads and process listings, then replayed the whole walk. The run lifecycle is therefore a file contract (Q32): every run subcommand (check, full, affected, single, day — not init, not status) brackets itself in `a.ghog.status` at the project root, writing `state=running pid=<pid>` at start and `state=done exit=<code>` at the end of every exit path (a crashing dispatch included), both atomically through a side-file replace. A hard kill is exactly the case that leaves `state=running` behind with a dead pid. The read-only `ghog status` reporter turns that file into exit codes: the recorded code passes through on `state=done` (branch on it like on a foreground walk), 6 means the run is live (wait, poll again, start nothing), 7 means the last run is lost — killed mid-walk, or never recorded — and `ghog day` is the relaunch. The same exit 6 backs a refusal: a run command started while another run is alive stops before the Q31 guard or any child could touch the live walk's log or testmon state. For harnesses that kill long calls, `ghog day --detach` spawns the walk as a survivor process — a hidden console (CREATE_NO_WINDOW, Q33: a console-free DETACHED_PROCESS survivor made its console children pop a visible window), broken away from the harness job object when the job allows it — wired by the tool itself to `a.ghog.log` (the parked senv preamble folded in first, so no caller redirect exists at all), and acknowledges with exit 6 once the child has written its first status line, the start handshake. No per-call timeout is documented anywhere: a portable upper bound for a walk does not exist across projects, and the status file answers the question a timeout pretends to answer. Accepted edges, all visible in the replayed status line: `ghog status` must never be redirected to `a.ghog.log` (the shell would truncate the live walk's log before the tool can refuse; its two-line envelope needs no redirect), a recycled pid keeps a killed run reading as live (the conservative direction, broken by deleting `a.ghog.status`), and a check.bat passthrough code of 6 or 7 would shadow the lifecycle codes on a later poll (theoretical for the check scripts in use).

## Constraints inherited from the tools package

The tool follows the house style of the other `tools/` scripts: Python 3.13, `from tools import find_project_root` to locate the project root (with a `--root` override), `argparse` for arguments, message-only logging to stdout, a `# eof` final line, and unit tests reaching the repo 100% coverage gate. Its one runtime dependency is tqdm for the user-mode bar (Q20), isolated in a thin rendering wrapper excluded from coverage like `tools/uv_run.py`.

## Output modes and progress reporting

Every subcommand has two modes, picked by TTY auto-detection — stdout not a TTY means LLM mode — with `--user` and `--llm` flags to force either (Q03):

- user mode: a progress bar drawn by tqdm (Q20), whose postfix carries the runtime numbers — tests done over total, failure/warning/xfail counts, coverage when measured — up to and including the end of the run, so the user reads the same numbers the LLM grammar carries; then the final report.
- LLM mode: no progress bar; one plain progress line at every 10% of the collected tests, plus one whenever 60 seconds pass without any (Q04). Each line carries the tests done over the total, the failure/warning/xfail counts, and the coverage percentage when measured.

In LLM mode, every line follows one fixed key=value grammar (Q16): a progress line reads `ghog full: 50% (125/250) fail=2 warn=1 xfail=0`, and the closing line merges the alias echo with the final numbers, `%PRJ_DIR_NAME%: ghog full done fail=2 warn=1 xfail=0 cov=withheld exit=2` — `cov=` reads `skipped` when coverage is not measured, `withheld` while failures hide it, the percentage otherwise. The keys are the contract: the wording around them may evolve, the keys do not. The exit code (Q12) stays the branching signal; these lines are for eyes and grep, not for orchestration.

Both modes end with a final report and that closing done line, the echo of the original aliases, so the user and the LLM both know the run completed.

## Reports, gates and exit codes

- Failures come first: when any test fails, the coverage numbers are not reported at all, to keep the focus on fixing tests before looking at coverage.
- Failure report (Q08): adaptive. A failing run is fixing material, so the final report gives full context — a short traceback per failing test — even when that is long: those tokens are what the LLM needs to produce a fix. The token thrift applies to the green case, where the long pytest output stays hidden behind the compact progress lines and the final report.
- Suite crash (Q06): when the run dies mid-suite (pytest internal error, hard interpreter exit), the tool prints one final stdout block with the last 5 started tests, the tail of the call stack, and an explicit instruction the LLM must act on immediately: make the test suite robust against that exception, based on those tests and that stack, so it cannot break the suite again.
- Warnings and xfail (Q09): informational only, never blocking the objective. When the objective is otherwise reached, one final nag line counts the remaining warnings and xfails.
- Coverage gate (Q14): read from the project coverage configuration (`fail_under`), default 100 when absent.
- Coverage percentage (Q19): parsed from the TOTAL line of the pytest-cov terminal report the parent already streams (Q17). A parse miss is loud — no `cov=` value means exit 5, never a silent wrong gate decision; a second `coverage report` child invocation was rejected as a cost paid on every run for a layout change that may never come.
- Coverage-gap rows (Q24): on exit 3 the report replays the term-missing table (Name/Stmts/Miss/Cover/Missing, header to TOTAL) under an "Uncovered lines" header — the gap's fixing material, like the failure block is for exit 2. The Missing column is exactly the covg input (`covg <file> <ranges>`), so no caller ever needs a coverage.json export.
- Exit codes (Q12): `0` objective met, `2` test failures, `3` coverage gap, `4` suite crash, `5` environment or setup error. Callers branch on the code, never on the report wording. Two lifecycle codes complete the contract (Q32): `6` a run is live (returned by `ghog status` while it runs, by the refusal of a run started over it, and by the acknowledgment of a detached launch), `7` the last run is lost (killed or never recorded — relaunch `ghog day`); they are never produced by a run's own classification.

## Failure baseline between full and focus runs

`ghog full` writes the failing test node ids to a scratch file at the project root, `a.ghog.failures`, refreshed on every full run and emptied on a green one (Q18). `ghog single` reads that file to print the Q07 comparison as two named lists: the tests still failing in focus (fix these first), and the tests passing in focus but failing in the full suite (the interaction or ordering suspects, fixed second). The pytest `lastfailed` cache was rejected as the baseline because the first focus run overwrites it, while the workflow prescribes several focus runs in a row; the scratch file is the only baseline with exactly the right lifetime, and it follows the `a.*` convention the project root already carries (a.prompt.txt, a.commit).

## The groundhog skill loop

A skill loops the tool until the global objective is reached: zero failures on the full suite, coverage at the gate. It is packaged as one instruction file, `instructions\groundhog.md`, with thin per-harness pointers — a Claude skill referencing it, and a Codex AGENTS.md section naming the same file — so Anthropic Claude and OpenAI GPT Codex run the same words (Q13). That instruction file carries the self-contained invocation contract of [Invoking groundhog from LLM shells](#invoking-groundhog-from-llm-shells) (Q21), and the loop is built on `ghog day` (Q22): run the walk, apply the fix its report names, run the walk again.

`ghog init` writes those per-harness pointers into a consuming repository (Q23): `.claude\skills\groundhog\SKILL.md` (frontmatter naming the skill and its triggers, body pointing at the instruction file by relative path) and a `## groundhog` section in `AGENTS.md` (created with a title when absent, appended otherwise, and left untouched when the section already exists). The relative paths are computed from the actual layout, so the sibling (`..\llm-shared`) and submodule (`llm-shared`) layouts both work. After init, the loop is triggered from Claude Code with `/groundhog` (or "run groundhog"), and from Codex with "run groundhog", which AGENTS.md routes to the same instruction file.

A real Codex session showed the bare phrase is not enough (Q25): AGENTS.md is passive context, only loaded at session start, and `groundhog` reads like a command name — Codex ran a `groundhog` shell command through senv.bat instead of opening the file. Two counters: the AGENTS.md section is worded trigger-first and names the misreadings (no `groundhog` executable exists; senv.bat is never a separate step), and `ghog init` also writes a user-level Codex custom prompt, `~/.codex/prompts/groundhog.md` (when `~/.codex` exists), so `/groundhog` triggers deterministically in Codex like in Claude Code. That prompt is project-agnostic: it routes through the project's own AGENTS.md section. A freshly written AGENTS.md is only seen by Codex sessions started after it exists.

### Loop sequence for the skill

1. senv.bat: never a separate step — the ghog bat wrappers chain it inside each call (Q21); a user launching from their console has it loaded already.
2. `ghog check`: compile check (skipped with a notice when check.bat is absent, Q10).
3. `ghog affected --no-cov`: confirm the recently modified files pass, the fast feedback step.
4. `ghog full`: full suite, fresh testmon data, coverage measured against the gate, failure baseline written to `a.ghog.failures` (Q18).
5. Branch on the exit code (Q12):
   - `4` (crash): act on the crash block immediately — fix the suite robustness based on the last started tests and the call stack (Q06), then restart the walk (`ghog day`, Q30).
   - `2` (failures): run one `ghog single test_file1.py test_file2.py ...` call with every failing test file (files, not functions). The tool prints the comparison against the `a.ghog.failures` baseline per test node id (Q07, Q18). Fix first the tests failing in focus; then the ones passing in focus but failing in the full suite, which point at test interaction or ordering issues, harder to fix. While fixing, stay on `ghog single` until the focus run is green — do not re-run `ghog full` per fix — then restart the walk (`ghog day`, Q30).
   - `3` (coverage gap): the report replays the term-missing rows (Q24); feed each file and its Missing ranges to covg (never a coverage.json export), write the tests covg points at, and verify with `ghog affected` only (coverage appends across runs). When `ghog affected` reports the gate is reached, finish with `ghog check` — new tests are code too, and ruff gates them (Q24) — and the objective is met without another `ghog full` once that check is green. On a check failure, fix what it names and restart the walk directly — no standalone `ghog check` re-run first (Q30); same when production code (not only tests) changed.
   - `5` (environment or setup error): report it; this is not a test problem to loop on.
   - `0`: objective reached; final report, including the warnings and xfail nag line (Q09).
6. Stop conditions (Q11): besides exit code 0, the loop stops when an iteration makes no progress — failure count not lower and coverage not higher than the previous iteration — and reports the stuck state; a hard cap of 10 iterations backs that rule as a safety net.

After any applied fix, the sequence restarts with one `ghog day` walk (check, then affected without coverage, then full), so every fix is re-proven by the whole chain — never through a standalone subcommand run first as a confirmation, which would pay the same step twice (Q30).

### CLI use without the loop

From the CLI, the user runs one subcommand at a time, typically starting at `ptr` (`ghog full`) or `pta` (`ghog affected`); the tool does not loop, but its final report and exit code name the step the run ended in (fix failures, fix coverage, or objective reached). The skill is the looping caller; both consume the same reports and exit codes.

`ghog day` is the single user entry point that walks the chain in one command (Q22): check (a missing check.bat skips with its notice, Q10), then `affected --no-cov`, then `full`, each step printing its own report and closing line. The walk stops at the first non-green step and exits with that step's code, so the last report on screen is always the one naming the fix to apply; the fixing itself, and the loop around it, stay with the caller (the user or the skill). With everything green, the walk ends on the full run's objective report.

A fully green walk records a source snapshot, `a.ghog.day.ok` at the project root: a digest over the path, size and mtime of every Python file (excluded folders aside) plus the gate configuration files (pyproject.toml, .coveragerc, setup.cfg, check.bat). The next `ghog day` recomputes the digest first: when it matches, the walk is a noop — one notice, the closing line, exit 0, no child spawned — so chained instructions that each end with a walk (implement-missing-step routing through split-large-file, for example) pay for it once (Q28). Any file change, addition or removal moves the digest; `ghog day --force` overrides the marker; unreadable files are skipped from the digest, which biases toward re-walking, never toward a wrong noop. Only the day walk writes the marker: a standalone green `ghog full` proves the suite but not the compile check, so it records nothing.

## Next-step messages per run state

The final report of every run closes with a next-step message naming the workflow state the run landed in, before the key=value done line (Q16). A user entering the workflow at any point, and the skill looping over it, both read the same contract. Every message that follows a fix names `ghog day` as the restart (Q30): the walk is the loop's only re-entry point, and its first step is the compile check, so the older `re-run ghog check` wording made a real session pay check.bat twice — once standalone, once again inside the walk it resumed.

| Run state | Exit code | Next-step message |
| --- | --- | --- |
| `ghog check` green | 0 | `Next: ghog affected --no-cov` |
| `ghog check` failing | check.bat code | `Next: fix the compile errors above, re-run ghog day (the walk opens with this check)` (Q30) |
| `ghog check`, check.bat absent | 0 | `check.bat not found - skipped; pytest collection will catch compile errors` (Q10) |
| `ghog affected --no-cov` green | 0 | `Next: ghog full` |
| `ghog affected` green with 0 tests | 0 | `0 tests ran in this step (testmon: nothing affected since the last run) - treated as green`, then the green next step (Q27) |
| `ghog affected --no-cov` failing | 2 | `Next: fix these, re-run ghog affected --no-cov until green, then ghog day` (Q30) |
| `ghog full` crash | 4 | the crash block: last 5 started tests, stack tail, immediate-fix instruction (Q06) |
| `ghog full` failures | 2 | `Next: ghog single <failing test files>`, baseline written (Q18), coverage withheld |
| `ghog full` coverage gap | 3 | the term-missing rows under `Uncovered lines` (Q24), then the covg message naming the Missing column as its input |
| `ghog full` objective met | 0 | `Objective reached`, plus the nag line when warnings or xfails remain (Q09) |
| `ghog affected` (coverage) at gate | 0 | `Coverage gate reached - no ghog full needed; finish with ghog check (new tests are code too)` (Q24) |
| `ghog affected` (coverage) below gate | 3 | the same covg message as the full coverage gap |
| `ghog single`, baseline present, failing | 2 | the two Q07 lists, then `Stay on ghog single until green, then restart the walk: ghog day` (Q30) |
| `ghog single`, baseline present, green | 0 | `Next: ghog day (the walk re-proves check, affected and full)` (Q30) |
| `ghog single`, no baseline | 0 or 2 | `no full-run baseline, comparison skipped; run ghog full for suite-level truth` |
| any subcommand, setup error | 5 | the failing precondition (pytest not found, unreadable TOTAL line, blocked senv.bat) |

## Implementation layout under tools

The tool is a package, `tools/groundhog/`, following the house constraints already stated:

- `models.py`: exit-code contract (Q12), pytest exit-code names, run statistics, the error type.
- `parser.py`: streaming pytest output parser — collected count, per-test results and node ids (`-v`), warnings summary, TOTAL coverage line (Q19), FAILURES/ERRORS block capture (Q08), last started tests and INTERNALERROR detection (Q06).
- `baseline.py`: `a.ghog.failures` read/write and the focus comparison lists (Q07, Q18).
- `gate.py`: coverage gate from `fail_under` in pyproject.toml, .coveragerc or setup.cfg, default 100 (Q14).
- `reporting.py`: key=value progress and closing lines (Q16), progress cadence governor (Q04), next-step messages, crash block, nag line.
- `redirect.py`: the Q31 self-redirect guard — capture detection (pipe or non-log file), the `a.ghog.log` file-handler swap, the envelope mirror behind `commands.emit_summary`, and the senv side-log consumption and replay.
- `status.py`: the Q32 run lifecycle — the `a.ghog.status` read/write mechanics, the pid liveness probe, the read-only status reporter, the live-run refusal, the running/done bracket around every run, and the detached day walk (hidden-console survivor spawn (Q33), senv preamble hand-off, start handshake).
- `runner.py`: child-process spawning and live streaming (Q17), pytest command per subcommand, `.testmondata` reset for full runs.
- `render.py`: the tqdm thin wrapper for user mode (Q20), excluded from coverage like `tools/uv_run.py`.
- `cli.py`: argparse subcommands, TTY mode pick (Q03), orchestration and exit-code classification; runnable as a script via the sys.path bootstrap the other tools use.

The bat wrappers live in `bin\`: `ghog.bat` (senv.bat call, llm-shared venv python by absolute path so the project PATH stays first for the pytest child, Q17, Q21), and `ptr.bat`, `pta.bat`, `ptanc.bat`, `pts.bat` as one-line delegates to `ghog.bat`. Unit tests live in `tests\unit\tools\test_groundhog_*.py`, acceptance tests in `tests\unit\tools\test_groundhog_acceptance.py`.

## Acceptance tests for groundhog

The acceptance tests drive `cli.main` end to end; the one faked element is the process boundary (a canned pytest transcript and exit code injected through the runner's process factory), so every scenario asserts the real parsing, classification, reporting and baseline behavior. Scenarios:

- AT1 green full run: a passing transcript with `TOTAL ... 100%` exits 0; the report carries the objective message and the closing line keys `fail=0`, `cov=100`, `exit=0`.
- AT2 full run with failures: exits 2, prints the FAILURES block in full (Q08), withholds coverage (`cov=withheld`), writes the failing node ids to `a.ghog.failures` (Q18), and names the failing files in the `Next: ghog single ...` message.
- AT3 focus run with a baseline: a `ghog single` transcript where one baseline test still fails and one passes exits 2 and prints both Q07 lists (still failing in focus; passing in focus but failing in the full suite).
- AT4 focus run green with a baseline: exits 0 and instructs to restart the walk with `ghog day` (Q30).
- AT5 coverage gap: a passing transcript with `TOTAL ... 97%` against a gate of 100 exits 3, replays the term-missing rows under the `Uncovered lines` header (Q24) and points at covg; an `ghog affected` transcript reaching the gate exits 0 with the no-full-needed message ending on the final `ghog check` (Q24).
- AT6 crash: a transcript cut mid-run with an INTERNALERROR (or a crash exit code) exits 4 and prints the crash block with the last started tests and the immediate-fix instruction (Q06).
- AT7 setup errors: pytest missing from PATH exits 5; a covered run whose transcript lacks a readable TOTAL line exits 5 (Q19).
- AT8 check step: a missing check.bat prints the skip notice and exits 0 (Q10); a failing check.bat passes its exit code through.
- AT9 LLM cadence: a long transcript emits one progress line per 10% step, and the 60-second silence floor emits a line when the injected clock jumps (Q04).
- AT10 grammar: every scenario's closing line carries the `fail=`, `warn=`, `xfail=`, `cov=` and `exit=` keys (Q16).
- AT11 day walk: `ghog day` spawns the three children in order (check.bat, the uncovered affected run, the covered full run) when everything is green; it stops at the first non-green step with that step's exit code and message; a missing check.bat skips to the test steps (Q10, Q22).
- AT12 init: `ghog init` writes a SKILL.md whose relative link resolves to the real `instructions\groundhog.md`, creates AGENTS.md with the groundhog section (or appends it to an existing AGENTS.md without touching its content), reports the already-registered case without rewriting AGENTS.md (detection anchored at a line start, so a mid-line mention does not count), leaves a non-UTF-8 AGENTS.md byte-identical with the exit-5 setup error, and exits 5 when the instruction file is missing (Q23).
- AT13 Codex prompt: with a `~/.codex` folder, init writes the `/groundhog` prompt under `~/.codex/prompts/` and reports it; without one, the prompt is skipped with a notice (Q25).
- AT14 lying check.bat: a check transcript carrying `ERROR :` lines with exit code 0 is reported as a mismatch and fails with exit 1, stopping a day walk at the check step (Q26).
- AT15 nothing affected: an affected transcript running no tests (pytest exit 5) stays green, prints the explicit zero-test note (Q27), and the day walk continues to the full step.
- AT16 day noop: a green day walk writes `a.ghog.day.ok`; an immediately repeated walk spawns no child and exits 0 with the noop notice; `--force` walks again; touching a Python file walks again; a failing walk records no snapshot (Q28).
- AT17 colored check and encoding: a check transcript whose `ERROR :` lines are wrapped in ANSI color codes still trips the Q26 mismatch guard, the re-emitted lines carry no escape sequences, and a line with characters outside an ascii stdout stream is logged with placeholders instead of crashing the handler (Q29).
- AT18 self-redirect guard: an LLM run whose stdout is a pipe or a capture file writes its full report to `a.ghog.log` and hands the captured stdout only the notice, next-step and closing lines; a stdout that already is the project log, a user-mode run, and an unwritable log all keep streaming as before, and the parked senv side log is replayed into the report stream then deleted (Q31).
- AT19 run lifecycle: every run brackets itself in `a.ghog.status` (running with the pid while the child works, done with the exit code after, even when the dispatch raises); `ghog status` passes a recorded done code through, exits 6 on a live run and 7 on a killed, missing or exit-free one, never arming the Q31 guard; a run command started over a live run refuses with exit 6, spawning nothing and writing nothing; `ghog day --detach` clears the stale status, hands the senv preamble and the day command to the survivor spawn (breakaway first, the same hidden-console flags when the job refuses, a new session off Windows; CREATE_NO_WINDOW and never DETACHED_PROCESS, Q33), acknowledges with exit 6 after the child's first status write, and reports the setup error on a spawn failure or a silent child (Q32).

## Design decisions for groundhog

The table summarizes the choices made from the answered questions Q01 to Q33, the section that carries each one, and the alternatives that were dropped.

| Question | Decision | Integrated in section | Main argument | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | Name the tool groundhog, alias `ghog` | Purpose of groundhog | Names the loop-until-perfect behavior; no clash with Python tooling | phoenix (collides, names only the reset); mulligan (suggests discarding a run) |
| Q02 | One entry point with subcommands, bat aliases kept; the tool also chains senv.bat and check.bat | The ghog command and its subcommands | One place for the output contract; aliases keep muscle memory; pytest is not the only step | Three separate scripts; retiring the alias names |
| Q03 | TTY auto-detection with `--user`/`--llm` force flags | Output modes and progress reporting | Right mode with zero ceremony; avoids progress-bar floods in LLM context | Explicit flag only; environment variable |
| Q04 | Hybrid cadence: a line every 10%, plus a 60-second silence floor | Output modes and progress reporting | Bounded line count and never more than a minute of silence | Percent only; fixed time span only |
| Q05 | `ghog full` keeps `--testmon` on a single worker | The ghog command and its subcommands | The rebuilt testmon database is the point of the reset and keeps pta cheap | xdist without testmon; a `--par` flag |
| Q06 | Crash block on stdout: last 5 started tests, stack tail, and an instruction the LLM consumes immediately to produce a fix | Reports, gates and exit codes | The LLM reads stdout in the moment; a re-run regenerates the block | Scratch file; file plus printed block |
| Q07 | Compare focus and full-suite failures per test node id | The groundhog skill loop | Only an id-level comparison produces the two named fix lists the workflow needs | Per-file counts; global count |
| Q08 | Adaptive report: full failure context (short traceback per failing test), compact output for green runs | Reports, gates and exit codes | A failing run is fixing material worth its tokens; thrift targets the long green output | One line per failure beyond a cap; always-minimal output |
| Q09 | Warnings and xfail informational, with a final nag line on success | Reports, gates and exit codes | A noisy dependency can never wedge the loop; rot stays visible | Warnings block the objective; no visibility at all |
| Q10 | Missing check.bat: skip with a printed notice | The ghog command and its subcommands | check.bat is an accelerator; collection catches the breakage anyway | Hard stop; per-project configuration |
| Q11 | Stop on no progress between iterations, hard cap of 10 as backstop | The groundhog skill loop | Stops on the symptom, not on an arbitrary count | Fixed iteration cap alone; unbounded loop |
| Q12 | Exit codes 0/2/3/4/5 as the orchestration signal | Reports, gates and exit codes | Branching without text parsing, stable across wording changes | 0/1 with text parsing; machine-readable last line |
| Q13 | One instruction file with thin Claude and Codex pointers | The groundhog skill loop | Single source of truth, the existing repository pattern | Two full copies; Claude-only |
| Q14 | Coverage gate from `fail_under`, default 100 | Reports, gates and exit codes | The tool never demands more than the project's own declared gate | Hardcoded 100; per-run flag |
| Q15 | Descriptive subcommand names: `check`, `full`, `affected`, `single` | The ghog command and its subcommands | The names live in LLM-facing instructions, where self-description beats brevity | Alias names as subcommands; both vocabularies registered |
| Q16 | Fixed key=value grammar for the LLM progress and closing lines | Output modes and progress reporting | One stream serves the user and grep alike; the keys give the stability sentences lose | Human sentences; one JSON object per line |
| Q17 | groundhog as parent in the llm-shared venv, pytest as a child in the project venv | Process architecture for groundhog | The parent survives any suite crash (Q06) and project venvs stay untouched | In-process `pytest.main`; upfront event-plugin injection |
| Q18 | `ghog full` writes the failing node ids to `a.ghog.failures`; `ghog single` reads it for the comparison | Failure baseline between full and focus runs | The only baseline surviving the repeated focus runs the workflow prescribes | pytest `lastfailed` cache; comparison left to the LLM |
| Q19 | Coverage percent parsed from the streamed TOTAL line, loud exit 5 on a parse miss | Reports, gates and exit codes | Zero extra cost on a stream already parsed; the failure mode is visible | Second `coverage report` child; parse-then-fallback |
| Q20 | tqdm draws the user-mode bar, counters in the postfix to the end, wrapper excluded from coverage | Output modes and progress reporting | Smallest footprint for one bar; the user reads the same numbers as the LLM | rich; hand-rolled `\r` bar |
| Q21 | Self-contained invocations for LLM shells: the wrappers chain senv.bat per call; non-wrapped commands use `cmd /d /v:on /c "senv.bat && <command>"` | Invoking groundhog from LLM shells | Environment changes never survive between LLM tool calls, sandboxed or not | A separate senv.bat step; per-harness invocation notes duplicated outside the instruction file |
| Q22 | `ghog day` as the single user entry point walking check, `affected --no-cov`, `full`, stopping at the first non-green step | CLI use without the loop | One command answers "where am I" without looping or fixing | Single-step subcommands only; a fixing loop inside the CLI |
| Q23 | `ghog init` writes the per-harness skill pointers (Claude SKILL.md, AGENTS.md section) into the consuming repo | The groundhog skill loop | One command registers the Q13 pointers with layout-correct relative paths, idempotent on AGENTS.md | Hand-written pointers per project; pointers kept only in llm-shared |
| Q24 | Exit 3 replays the term-missing rows as the covg input, and the gate-reached shortcut ends with one `ghog check` | Reports, gates and exit codes | Without the rows the LLM mines coverage.json; without the final check, new tests dodge ruff (both seen in a real Codex run) | Keep the table hidden; treat test-only changes as not needing check.bat |
| Q25 | Trigger-first AGENTS.md wording naming the misreadings, plus a user-level `~/.codex/prompts/groundhog.md` for a deterministic `/groundhog` | The groundhog skill loop | A real Codex session ran `groundhog` as a shell command instead of reading the passive AGENTS.md context | Descriptive wording with the trigger last; AGENTS.md as the only Codex channel |
| Q26 | A check.bat that prints `ERROR :` lines yet exits 0 is treated as failed (exit 1) with a mismatch notice | The ghog command and its subcommands | A real check.bat template cleared its status variable before `exit /b` read it, green-lighting a failed walk | Trust the exit code alone; parse nothing |
| Q27 | A green affected step that ran 0 tests says so explicitly | Next-step messages per run state | An invisible no-op step reads as a skipped step in a day walk (seen in a real log) | Stay silent and let the closing line carry the zeros |
| Q28 | A green `ghog day` records a source snapshot (`a.ghog.day.ok`); an unchanged snapshot makes the next walk a noop, `--force` overrides | CLI use without the loop | Chained instructions may each end with a walk; duplicates become free instead of a second full run | Always re-walk; rely on testmon selection alone (the full step resets it) |
| Q29 | The check guard matches and re-emits ANSI-stripped lines; the stdout logger replaces unencodable characters | The ghog command and its subcommands | A colored check.bat hid its ERROR lines from the Q26 guard, and ty's box-drawing output crashed the cp1252 logging stream (both seen in one real run) | Match the raw colored lines; let encoding errors drop lines |
| Q30 | Every post-fix next-step message names `ghog day`, the loop's only re-entry point | Next-step messages per run state | A real session obeyed `re-run ghog check`, then resumed the walk, paying check.bat twice; the walk opens with that same check | Keep the subcommand wording and translate it in the instruction files alone |
| Q31 | An unredirected LLM run self-redirects: full report to `a.ghog.log`, envelope (notice, next-step, closing lines) to the captured stdout; ghog.bat parks the senv preamble in `a.ghog.senv.log` for the CLI to replay | Invoking groundhog from LLM shells | A real session ran the walk unredirected five times — the redirect contract lived in docs a stale consumer AGENTS.md overrode; a tool-side guard cannot be skipped | Docs-only contract; failing hard on a missing redirect |
| Q32 | Run lifecycle in `a.ghog.status` (running pid / done exit, atomic), a read-only `ghog status` reporter (done code passthrough, 6 live, 7 lost), a live-run refusal (exit 6), and `ghog day --detach` spawning a survivor walk wired to `a.ghog.log` | Invoking groundhog from LLM shells | A harness timeout killed a real walk mid-suite while the orphaned runner kept feeding the log: with no completion proof the agent guessed from tails and process listings, then replayed the whole walk; no portable per-call timeout exists across projects | A documented timeout per harness; completion inferred from log tails, file mtimes or process listings; a watchdog process around the walk |
| Q33 | The survivor spawn hides its console with CREATE_NO_WINDOW instead of dropping it with DETACHED_PROCESS | Invoking groundhog from LLM shells | A console-free survivor made its console children (check.bat, pytest) allocate a fresh visible console window on the user's desktop for the whole detached walk; a hidden console is inherited silently | DETACHED_PROCESS (console-free survivor, the window source); a minimized but visible window; a pythonw.exe relaunch |

## Questions

If there is no open questions and decision table, follow instructions from `instructions\review-ask-questions.md`, and ask feature questions, then pause for review.

If you see open questions, follow instructions from `instructions\consolidate-then-review-ask-questions.md`, and, after consolidation, rewrite the first section of this document to better reflect the features to implement, and then ask new questions if needed (either feature or design), then pause for review.

If, after consolidation (and first section updates or rewrite, to specify feature and define design), you think you have enough information to start the implementation, say so, and do not ask any new question. Otherwise, ask new questions as needed, then pause for review.
