# Implement step instructions

Include "Step XXXX" in the title of this conversation (replace XXXX with the step mentioned in the prompt, for example '2', for "Step 2 of the CDC gap feature").

Read carefully the markdown files in your context to understand the context. Read them with your file tools, one document at a time — never by chaining an environment wrapper (such as `senv.bat`, the project-root environment file — `%PRJ_DIR%\senv.bat` when `PRJ_DIR` is set, never under `bin\`) with a file-dump command: the project environment is only for toolchain commands like `ghog`. For every shell command of this step, follow [`run_commands.md`](../rules/run_commands.md), so the first attempt is the one that works: one shell per command, no nested quoting, targeted reads, and no verbatim retry of a command that failed with a quoting or parse error.

Based on the design markdown and the plan markdown, implement step XXXX (see your prompt). Once the implementation is done, verify it with one groundhog walk — `ghog day`, always the redirected call `cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"` from the project root — which runs check.bat, the focused tests, and the full coverage pass in order and stops at the first non-green step with the fix to apply. Do not call `check.bat` or `pytest` directly: groundhog is in charge of check and tests. See [Verify the step with groundhog](#verify-the-step-with-groundhog) below.

Make sure no new computation would introduce any O(n^2) or O(n log(n)) process.

Make sure DDD-Hexagonal architecture is strictly respected: no violation, no smell.

Make sure no existing feature or reporting capability is impaired.

Do not update the validation plan (`<effort-dir>/plan.vX.Y.Z.<topic>.validation.md`): recording the step's state there is the separate implementation-check step. This step writes code and tests only. Use the exact path supplied by `pw`; `<effort-dir>` is the canonical draft's parent directory.

Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py`, and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Before writing code, write a short analysis of the issue and a brief description of the implementation. Only then write the code, following the project instructions in `CLAUDE.md` (and `copilot-instructions.md` for Copilot users), which means write the class in full (no "`# ...existing code...`" comment).

Always update the docstring at the very top of the modified classes to explain the fix. That applies to test classes as well.

Preserve existing code and docstrings and comments; only update them to explain and accommodate your implementation. Check if any comment is obsolete considering the current code and remove them. Do not remove comments like `# Act` unless the whole section has been removed as part of your fix. Read and follow instructions from [`preserve_code.md`](../rules/preserve_code.md).

When writing an answer in markdown, follow instructions from [`markdown.md`](../rules/markdown.md).

## Verify the step with groundhog

At the end of the step, run `ghog day` once — the groundhog walk (manual in [`GROUNDHOG.md`](../GROUNDHOG.md), fixing loop in [`groundhog.md`](groundhog.md)). Every ghog call is one redirected shell call from the project root:

```bat
cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"
```

Issue that call from **PowerShell or cmd.exe**, never from Git Bash or another MSYS/POSIX shell: a POSIX shell rewrites the `/d` and `/c` arguments into paths, so `cmd` starts interactively and exits 0 without running the tool, leaving a stale `a.ghog.log` that reads as a fresh green result. Prove the run happened with a freshness flag before trusting the log — stamp `a.ghog.started`, run the walk, confirm `a.ghog.log` is newer than the flag, delete it; an untouched log means the walk did not run, so fix the invocation and retry rather than reading old content (the per-step `started`/`ended` timestamp headers in the log make staleness obvious too). From PowerShell:

```powershell
ni a.ghog.started -Force | Out-Null; $t = (gi a.ghog.started).LastWriteTime
cmd /d /c "<llm-shared>\bin\ghog.bat day > a.ghog.log 2>&1"; $code = $LASTEXITCODE
if (-not ((Test-Path a.ghog.log) -and (gi a.ghog.log).LastWriteTime -gt $t)) {
    "STALE: a.ghog.log not refreshed - the walk did not run; fix the invocation before reading"
}
ri a.ghog.started -Force; "exit=$code"
```

`<llm-shared>` is the resolved absolute llm-shared directory that contains
this canonical instruction, as described in
[`run_commands.md`](../rules/run_commands.md). Do not substitute a guessed
sibling path or environment variable. Branch on the exit code first, then read
only the tail of `a.ghog.log` — the last 5 lines on exit 0, the last 100
otherwise; never load the whole log, never delete it. The walk is finished only
when `a.ghog.status` reads `state=done` — a verdict to read through `ghog
status`, never with a direct read of that file (only the command probes the
pid); a growing log proves nothing. When the harness can kill long calls — or
already killed one walk — run the walk detached instead, `cmd /d /c
"<llm-shared>\bin\ghog.bat day --detach"` with no redirect, then poll `cmd /d
/c "<llm-shared>\bin\ghog.bat status"` (never redirected) until its exit code
is no longer 6: exit 7 means the run was lost (relaunch), any other code is the
walk's own. The walk runs, in order, stopping at the first non-green step:

- check.bat: the compile and lint gate;
- `ghog affected --no-cov` (the old ptanc): the focused tests — created, modified, or impacted by this step — selected by testmon, coverage off;
- `ghog full` (the old ptr): the full suite with a fresh coverage measure against the gate.

Apply the fix named by the final report, then run `ghog day` again, until it reports the objective (`exit=0`). When the full run lists failing files, run `ghog single <those files>` first, as the report says: it separates the tests still failing in focus (fix first) from the ones failing only in the full suite (test interaction, fix second). On an exit-8 duration-outlier verdict, the named fix is to shorten the flagged slow calls (or `ghog exclude` a truly irreducible one): you MUST modify at least one flagged call before the next walk — re-running `ghog day` with no change is forbidden, even when you are certain the slowness was load-induced, because a borderline call only stops flapping once it is given margin, never by re-measuring it. Lower the flagged calls first; a bare re-run is never the fix. If a call you already lowered is still above the floor on the next walk, judge whether real headroom remains: lower it again only when it does, and otherwise `ghog exclude <node id> <measured seconds>` it at its measured time rather than re-walking — lower while you have headroom, exclude when you do not, and never loop on a call you cannot lower further.

Never run `check.bat` or a plain `pytest` yourself: groundhog owns check and tests, budgets their output for the token window, and protects the recorded coverage (a plain `pytest` would erase it through the `--cov` defaults of `pyproject.toml`). The historical aliases (`ptr`, `pta`, `ptanc`, `pts`) route to groundhog subcommands, so the report's next-step instructions are the only commands you need — and after a fix they name `ghog day` itself: never chain a standalone `ghog check` before the walk, that would run check.bat twice.

## Reach 100% coverage on each unit-tested class

This rule is for unit tests only, the ones under the project's unit-test root such as `src\<package>\tests\unit`. It does not apply to integration, smoke, regression, or acceptance tests.

- One unit test file, or a set of unit test files inside a test folder named after the class under test, must reach 100% coverage of that one Python class file. Each unit-tested class file gets to 100% on its own, in one test file or several.
- Design the class file to be easy to test first: small methods, injected dependencies, no hidden side effects. Then write the unit tests so they both exercise the behaviour and reach 100% of that class file.
- A unit test folder targets a single class file. Other test types may cover several classes at once; they carry no coverage target and answer only to what they represent (integration, smoke, regression, or acceptance).
- If a legacy unit test exists, is impacted by this step, and its run does not reach 100% of the class it tests, take the chance to complete it (unit tests only) so that class file is back at 100%.

## Handoff

When the step is implemented and the `ghog day` walk reports the objective (`exit=0`), hand the cycle on to the implementation check, with no menu. From the project root, run:

- `pw handoff check <x>`

`<x>` is the plan step you just implemented — the "Step XXXX" of this conversation, a number such as `2` or a sub-step id such as `4A`. `pw` is run through its launcher (see [`run-pw.md`](run-pw.md) for the non-interactive invocation), the same tool the interactive cycle uses.

Run `pw` from a PowerShell shell — the `pw` alias when the project environment
is loaded, otherwise
`& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" handoff check <x>`. Resolve
`<LLM_SHARED_DIR>` from this canonical instruction as described in
[`run_commands.md`](../rules/run_commands.md); do not rely on an environment
variable. Do not wrap the launcher in a `cmd /d /c "..."` call from a Git Bash
or other POSIX shell: that nested `cmd` swallows the launcher's output and its
rewrite of `a.prompt.txt` and `a.prompt_memory`, so the handoff does nothing
while still returning `0` — a silent no-op. The launcher must print `Prompt for
step <x> (check) ready`; if you do not see that line, the handoff did not run,
so re-run it in PowerShell before going on.

The call writes the `implementation-check.md` prompt for step `<x>` to `a.prompt.txt` at the project root, copies it to the clipboard, and records the step in `a.prompt_memory`. Confirm it took — the first line of `a.prompt.txt` now names `instructions/implementation-check.md` — then read `a.prompt.txt` and run the instructions of that returned prompt straight away to check what you just implemented. A handoff is the go-ahead to perform the next workflow step now: do not stop to ask the user whether to proceed, and do not compose the next prompt yourself. `pw` builds the prompt and the handoff authorises it, so every step the cycle reaches is executed without further confirmation — the commit-message step (`group-commits-msg.md`) included, where you write the commit messages rather than waiting to be told to.

**Hard rule — run the chain straight through to a reviewable `a.commit`, then take the branch the review-mode sampling names.** After `pw handoff check <x>` you run the implementation check immediately, then its `pw handoff after-check <x>`, then the `group-commits-msg.md` run, all without pausing: the chain is implement -> check -> after-check -> group-commits -> `a.commit` -> sample review mode -> either the code-review round or the commit gate. Do not stop between these to ask whether to run the next step, whether to proceed, or to let the user review mid-chain, and do not stop because the session has been long or the work large — those are not reasons to pause. Sampling `a.review-mode` is a step of this chain and not a preference: when it reports review mode on, the code-review round replaces the commit gate, and presenting the commit gate instead is the same defect as skipping a step. When it reports off, the single stop is the commit gate at the end, where `a.commit` is prepared and presented and `group-commits-msg.md` shows its go-ahead choices before the actual commit. Pausing anywhere earlier is the mistake this rule forbids.

### Branch after group-commits: review mode or the commit gate

Immediately after `group-commits-msg` has successfully produced the reviewable
root `a.commit`, sample review mode exactly once. This is a deliberate act
performed at this point in the chain, never a conclusion carried over from a
directory listing taken earlier for another purpose: the marker lives in a
dotted directory that a plain `ls` does not show, and it is covered by the
`a.*` ignore rule so `git status` never reports it either. An earlier listing
that did not mention it is not evidence of its absence.

Sample it with the command rather than by testing a path, so no instruction has
to name a location the tooling may resolve differently. From the project root:

```powershell
& "<LLM_SHARED_DIR>\rvw_status.bat"
```

Resolve `<LLM_SHARED_DIR>` as described in
[`run_commands.md`](../rules/run_commands.md). The command reports its artifact
home and every active exchange, and its exit code carries the trust level:
status `0` is a complete trustworthy result, including one with zero active
exchanges; status `3` returned evidence with an untrustworthy candidate; status
`2` means no trustworthy answer, so report the diagnostic rather than inferring
that review mode is off. Absence is a conclusion the command reaches, never one
a failed command implies.

When the command cannot be run, fall back to a file test in the order the
tooling itself resolves the marker: first `<artifact-home>/a.review-mode`,
where `<artifact-home>` is `.reviews` unless a versioned
`.review-artifacts.ini` declares another `home` under `[review-artifacts]`, and
only then the project-root `a.review-mode`, which the loader keeps as its
legacy fallback. The home marker wins whenever both exist. Test the exact paths
at this point in the chain; do not conclude from a listing.

State the result before doing anything with it, in one line naming the verdict
and where it came from, such as `review-mode: on (home .reviews)`. A sampling
whose result is never stated is indistinguishable from a sampling that never
happened.

When review mode is off, preserve the ordinary commit gate above. When it is
on, the review path replaces that immediate human-review stop: run
`pw skill code-review-requestor`, which prints a self-contained command carrying
the exact plan and implementation step, then run the printed command verbatim.

Read and follow `instructions/code-review-requestor.md`; do not reproduce that
role's exchange lifecycle here. Its requestor feedback is appended to the
versioned review transcript, but the transcript is never reread as working
context. After activation, durable coordination governs resumption even when
the marker later changes. The handoff never authorizes this implementation
session to initiate the counterpart: after publication it remains the
requestor, starts no reviewer agent or session, and immediately waits for the
answer through the shared protocol.
