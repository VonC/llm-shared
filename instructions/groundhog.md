# Groundhog loop: drive the test suite to its objective

Goal of this instruction: reach the global objective of the project under work — every test passes on the full suite, and coverage reaches the project gate (`fail_under`, default 100) — by looping the groundhog tool and code fixes until done. The tool walks and reports; you fix and loop.

## Invocation contract for the groundhog loop

- `<llm-shared>` below stands for the llm-shared folder of this workspace (for example `../llm-shared` or `llm-shared`); the file that pointed you here names the exact path.
- Every command must be one self-contained shell call from the project root: environment changes never survive between tool calls, sandboxed or not. Never run senv.bat as its own step; the ghog wrapper loads it itself, inside the same cmd process.
- Run every ghog subcommand with its output redirected to a project-root log: `cmd /d /c "<llm-shared>\bin\ghog.bat <subcommand> > a.ghog.log 2>&1"` from a CMD shell (no PowerShell needed). The exit code passes through the redirect, and the short forms below (`ghog day`, `ghog affected`, ...) all stand for that redirected call. The redirect belongs to LLM runs only: it keeps run output out of your context and lets the user follow the loop live through the log; a human calling ghog.bat directly keeps the usual stdout, nothing changes for them.
- Each run overwrites `a.ghog.log`, so its tail is always the current run. Never delete the file, not even when the loop ends.
- Branch on the exit code first, without reading anything. Then read only the log tail: the last 5 lines on exit 0 (closing line and nag line), the last 100 lines on any other code; pull further back only when the block you need is visibly cut. Never load the whole log with a plain file read.
- When a non-wrapped command needs the project environment (covg, for example), chain it in one call: `cmd /d /v:on /c "senv.bat && <command>"`, without redirection — covg output is the data you need, in full. Never run `check.bat` or `pytest` directly: groundhog is in charge of check and tests.
- Without a TTY the tool picks LLM mode on its own: progress lines, a final report ending with a next-step message, a closing key=value line (`fail= warn= xfail= cov= exit=`), and an exit code: `0` objective met, `2` test failures, `3` coverage gap, `4` suite crash, `5` setup error; `ghog check` passes the check.bat exit code through. The walk's full-suite step closes with `ghog full done` — that line is the ptr step of the old aliases.

## Sandboxed harness rules (Codex and similar)

- These commands need real filesystem access: senv.bat reads user-profile paths and activates the project venv. In a sandboxed harness, run every ghog/covg call with escalated (elevated, approved) execution from the start.
- Output containing `Access is denied`, `gum choose`, `Unable to create virtual env` or `Failed to export ... environment variables` means the sandbox blocked senv.bat. Do not debug it, do not create any virtual environment, do not pick a Python version yourself: re-run the exact same single command escalated, and it will pass.
- Harness output truncation is already covered by the standard redirected form: whatever the harness showed you, the full report sits intact in `a.ghog.log`; read its tail as stated in the contract above.

## Loop sequence to follow

`ghog day` is the loop's spine and its only entry and re-entry point: the same day is relived — one walk, the fix it names, one walk again — until everything is perfect at once (check, affected tests, full suite at the coverage gate). The subcommands named below live only inside their branch, as verifiers cheaper than a walk while fixing that one branch; never run one as a preflight or a confirmation around a walk. In particular, a standalone `ghog check` right before a `ghog day` runs check.bat twice for nothing: after a fix, the report itself names `ghog day` as the restart, and that is the one command to type.

1. Run `ghog day` — that is, `cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"`: it walks check.bat, then the affected tests without coverage, then the full suite with a fresh coverage measure, and stops at the first non-green step. When nothing changed since the last green walk, it answers with a noop notice and exit 0 — calling it twice costs nothing, so always prefer running it over wondering whether it already ran.
2. Branch on the exit code of that walk:
   - `0`: objective reached. Read the last 5 log lines, relay the closing line and the nag line (warnings and xfails) when present, then stop.
   - check.bat failure (its own non-zero code): read the log tail, fix the compile errors shown, then go back to step 1 directly — the walk opens with that same check, so a separate `ghog check` run first would only pay check.bat twice.
   - `2` with failures from the affected step: fix them from the failure context in the log tail, re-run `ghog affected --no-cov` until green, then go back to step 1 — not straight to `ghog full`: the fixes made the earlier check verdict stale, and the walk re-checks first.
   - `2` with failures from the full suite: the next-step line names the failing files. Run `ghog single <those files>` once; its report splits the failures into two lists. Fix the "still failing in focus" tests first, then the "passing in focus but failing in the full suite" ones (test interaction or ordering issues, harder to fix). Stay on `ghog single` while fixing — do not re-run the full suite per fix. Once the focus run is green, go back to step 1, as the report says: one `ghog day`, not a standalone `ghog check`.
   - `3` (coverage gap): the report replays the term-missing table under "Uncovered lines"; its Missing column is the covg input. For each listed file run `cmd /d /v:on /c "senv.bat && <llm-shared>\bin\covg.bat <file> <ranges>"` (for example `covg.bat src\pkg\mod.py 48 86-88 100`) to name the uncovered functions and branches. Never generate, read or parse a coverage.json export: it is huge, and everything covg needs is in the report's Missing lines. Write the tests covg points at, verify with `ghog affected` only, and repeat covg/tests while it stays below the gate. When it reports the gate is reached, run `ghog check` — the new tests are code too (ruff and the other checks gate them) — and the objective is met when that check is green, without another full run. On a check failure, fix what it names and go back to step 1 directly, without re-running `ghog check` on its own first; same when production code (not only tests) changed.
   - `4` (suite crash): the crash block lists the last started tests, the call-stack tail and an instruction; act on it immediately — make the test suite robust against that exception, so it cannot break the suite again — then go back to step 1.
   - `5` (setup error): relay the printed reason from the log tail and stop; looping cannot fix it.
3. Stop conditions: stop and report the stuck state when an iteration makes no progress (failure count not lower and coverage not higher than the previous iteration); never exceed 10 iterations.

The objective is only reached when nothing changed after the last green signals: any fix or new test applied after a step ran means that step's verdict is stale. One single situation closes the loop without a walk: the coverage branch above, where `ghog affected` proved the gate and one `ghog check` seals the new tests. Everywhere else, the fresh verdict comes from one more `ghog day` — never from a hand-built chain of subcommands, and never from a `ghog check` run as a preflight to a walk.

## Reporting back during the loop

The progress lines live in `a.ghog.log`; the user follows them there while the loop runs, so do not replay them. After each run, relay the closing line verbatim, naming the loop iteration you are in; do not paraphrase the numbers. At the end, report the final closing line and, on success, the nag line.
