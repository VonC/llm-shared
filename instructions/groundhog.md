# Groundhog loop: drive the test suite to its objective

Goal of this instruction: reach the global objective of the project under work — every test passes on the full suite, and coverage reaches the project gate (`fail_under`, default 100) — by looping the groundhog tool and code fixes until done. The tool walks and reports; you fix and loop.

## Invocation contract for the groundhog loop

- `<llm-shared>` below stands for the llm-shared folder of this workspace (for example `../llm-shared` or `llm-shared`); the file that pointed you here names the exact path.
- Every command must be one self-contained shell call from the project root: environment changes never survive between tool calls, sandboxed or not. Never run senv.bat as its own step; the ghog wrapper loads it itself, inside the same cmd process.
- Run the tool as `<llm-shared>\bin\ghog.bat <subcommand>` from a CMD shell (no PowerShell needed). When a non-wrapped command needs the project environment (covg, for example), chain it in one call: `cmd /d /v:on /c "senv.bat && <command>"`. Never run `check.bat` or `pytest` directly: groundhog is in charge of check and tests.
- Without a TTY the tool picks LLM mode on its own: progress lines, a final report ending with a next-step message, a closing key=value line (`fail= warn= xfail= cov= exit=`), and an exit code: `0` objective met, `2` test failures, `3` coverage gap, `4` suite crash, `5` setup error; `ghog check` passes the check.bat exit code through. The walk's full-suite step closes with `ghog full done` — that line is the ptr step of the old aliases.

## Sandboxed harness rules (Codex and similar)

- These commands need real filesystem access: senv.bat reads user-profile paths and activates the project venv. In a sandboxed harness, run every ghog/covg call with escalated (elevated, approved) execution from the start.
- Output containing `Access is denied`, `gum choose`, `Unable to create virtual env` or `Failed to export ... environment variables` means the sandbox blocked senv.bat. Do not debug it, do not create any virtual environment, do not pick a Python version yourself: re-run the exact same single command escalated, and it will pass.
- When the harness truncates long output, redirect one run to a log and read its tail (`cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"`, then read the last 80 lines); delete the log when the loop ends.

## Loop sequence to follow

1. Run `<llm-shared>\bin\ghog.bat day`: it walks check.bat, then the affected tests without coverage, then the full suite with a fresh coverage measure, and stops at the first non-green step. When nothing changed since the last green walk, it answers with a noop notice and exit 0 — calling it twice costs nothing, so always prefer running it over wondering whether it already ran.
2. Branch on the exit code of that walk:
   - `0`: objective reached. Relay the closing line and the nag line (warnings and xfails) when present, then stop.
   - check.bat failure (its own non-zero code): fix the compile errors shown, then go back to step 1.
   - `2` with failures from the affected step: fix them from the failure context in the report, re-run `<llm-shared>\bin\ghog.bat affected --no-cov` until green, then go back to step 1.
   - `2` with failures from the full suite: the next-step line names the failing files. Run `<llm-shared>\bin\ghog.bat single <those files>` once; its report splits the failures into two lists. Fix the "still failing in focus" tests first, then the "passing in focus but failing in the full suite" ones (test interaction or ordering issues, harder to fix). Stay on `ghog.bat single` while fixing — do not re-run the full suite per fix. Once the focus run is green, go back to step 1.
   - `3` (coverage gap): the report replays the term-missing table under "Uncovered lines"; its Missing column is the covg input. For each listed file run `cmd /d /v:on /c "senv.bat && <llm-shared>\bin\covg.bat <file> <ranges>"` (for example `covg.bat src\pkg\mod.py 48 86-88 100`) to name the uncovered functions and branches. Never generate, read or parse a coverage.json export: it is huge, and everything covg needs is in the report's Missing lines. Write the tests covg points at, verify with `<llm-shared>\bin\ghog.bat affected` only, and repeat covg/tests while it stays below the gate. When it reports the gate is reached, run `<llm-shared>\bin\ghog.bat check` — the new tests are code too (ruff and the other checks gate them) — and the objective is met when that check is green, without another full run. On a check failure, or when production code (not only tests) changed, go back to step 1.
   - `4` (suite crash): the crash block lists the last started tests, the call-stack tail and an instruction; act on it immediately — make the test suite robust against that exception, so it cannot break the suite again — then go back to step 1.
   - `5` (setup error): relay the printed reason and stop; looping cannot fix it.
3. Stop conditions: stop and report the stuck state when an iteration makes no progress (failure count not lower and coverage not higher than the previous iteration); never exceed 10 iterations.

The objective is only reached when nothing changed after the last green signals: any fix or new test applied after a step ran means that step's verdict is stale — finish with `ghog check` at minimum, or a fresh `ghog day` when production code changed.

## Reporting back during the loop

Relay the groundhog progress lines and each closing line to the user as they arrive, naming the loop iteration you are in; do not paraphrase the numbers. At the end, report the final closing line and, on success, the nag line.
