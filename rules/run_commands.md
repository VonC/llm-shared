# Run commands right on the first attempt

Every shell command costs tokens twice: once for the call, once for its output landing in the context window. A broken or oversized command spends that budget without producing anything usable, and a retry of the same broken command spends it again. These rules exist so the first attempt is the one that works.

## File reads never go through an environment wrapper

An environment wrapper such as `senv.bat` — always at the project root (`%PRJ_DIR%\senv.bat` when `PRJ_DIR` is set, never a copy under `bin\`) — is a contract for toolchain commands only: build, check, test, and dependency tooling (`check.bat`, `ghog`, `pytest`, `python`, `uv`). Reading or searching files never needs the project environment:

- Use the harness file tools (file read, grep/rg search) when the harness has them.
- Otherwise run a plain direct command (`rg`, `type`, `Get-Content`) with no wrapper.
- Never chain `senv.bat && <file read>`: the wrapper adds its whole setup output, its own failure modes (sandbox blocks, missing tools), and an extra quoting layer, for a task that needs none of it.

## Activate the project senv.bat, never another one

Call the project environment as `.\senv.bat` from the project root (or by its
full path, `"%PRJ_DIR%\senv.bat"`), never as a bare `senv.bat`. Only the
project's own `senv.bat` sets that project's paths and variables: its
`PRJ_DIR`, its virtual environment and Python, its `bin` on `PATH`, its
package index and certificate settings, and its aliases. Another `senv.bat`
knows none of them.

A bare name is not guaranteed to reach the project file. Some agent hosts run
their shells with `NoDefaultCurrentDirectoryInExePath` set, as Claude Code
does, and then `cmd` skips the current directory and resolves `senv.bat`
through `PATH`: typically a user-level home `senv.bat`, which prints its own
activation line and stops. The chained command then runs without the project
environment, and it can even appear to work, because the shell inherited
variables from the console that started the session. `where senv.bat` does not
reveal this, since it always lists the current directory first. The `.\`
prefix removes the ambiguity on every host.

## One shell per command, no nested quoting

Never embed a quoted shell inside another quoted shell. A form like `cmd /c ".\senv.bat && powershell -Command "<script>""` cannot work: `cmd.exe` has no `\"` escaping, so the inner double quotes split the command line, and `$`, `;`, `&&` inside the script are parsed by the wrong shell. The visible symptom is a parse error such as `The term '\' is not recognized` or `'X' is not recognized as an internal or external command`.

- When a `.bat` wrapper is the toolchain entrypoint, try the wrapper first from
  the project root: `cmd /d /v:on /c "<one-executable> <plain arguments>"`.
  Several wrappers load `senv.bat` themselves and need to own that setup.
- If the wrapper-first command fails because project tools are not exposed on
  `PATH`, check whether the inherited environment defines the project-specific
  guard `NO_MORE_SENV_%PRJ_DIR_NAME%`.
- When the project environment is required and the guard is not defined, chain
  exactly one simple command from the project root, where `senv.bat` sits
  (`%PRJ_DIR%\senv.bat` when `PRJ_DIR` is set, never `bin\senv.bat`), and
  call it as `.\senv.bat` so the project file runs, not another `senv.bat`
  found on `PATH` (see *Activate the project senv.bat, never another one*):
  `cmd /d /v:on /c ".\senv.bat && <one-executable> <plain arguments>"` -- no
  other inner double quotes, no `$`, no multi-statement script in the chained
  part.
- When `NO_MORE_SENV_%PRJ_DIR_NAME%` is defined, clear it in the same `cmd`
  process before calling the project `.\senv.bat`:
  `cmd /d /v:on /c "set NO_MORE_SENV_%PRJ_DIR_NAME%=& .\senv.bat && <one-executable> <plain arguments>"`.
- Issue any `cmd /c` form (and `.bat` toolchain scripts such as `ghog`, `check.bat`, `build.bat`/`brel`, `update-changelog.bat`) from PowerShell or cmd.exe, never from Git Bash or another MSYS/POSIX shell. A POSIX shell rewrites the `/c`, `/d`, and `/v:on` switches into Windows paths, so `cmd.exe` never sees `/c`: it opens an interactive session, prints its banner, and exits 0 without running anything. The command silently does nothing, and a redirect like `> a.out.log 2>&1` is left empty or stale — which a careless read takes for a fresh, successful result. Run these from the PowerShell tool (or have the user run them in a real console).
- When a multi-statement PowerShell script is genuinely needed, write it to a temporary `.ps1` file first and run `powershell -ExecutionPolicy Bypass -File <script.ps1>` as the single chained command.
- When neither form fits, split the work: one command for the environment-bound step, harness file tools for everything else.

## Python scripts use wrappers or a guard-clearing project environment

Prefer the shipped `bin\*.bat` wrapper for a shared Python tool. A wrapper can
load the project environment, choose the right Python, and keep the command line
simple. For example, use `bin\oqm.bat` for open-question management instead of
calling `tools\open_questions_md.py` directly.

When no wrapper exists and a Python script must run in the consuming project's
environment, clear the project-specific `NO_MORE_SENV_%PRJ_DIR_NAME%` guard in
the same `cmd` process before calling the project `.\senv.bat`. Do this
unconditionally; there is no need to check whether the variable is currently
defined. The `.\` prefix is what makes `python` the project's own interpreter:
a home `senv.bat` reached through `PATH` would leave whichever Python the shell
inherited.

Use this first-attempt shape from the project root:

```bat
cmd /d /v:on /c "set NO_MORE_SENV_%PRJ_DIR_NAME%=& .\senv.bat && python path\to\<a_script.py> <plain args>"
```

Keep the chained part to one Python executable plus plain arguments. Do not add
an inner shell, command substitution, or a multi-statement script inside the
quoted `cmd /c` body.

## llm-shared launchers run by resolved full path, no environment setup

In every llm-shared instruction, `<LLM_SHARED_DIR>` means the absolute
directory that contains the canonical `instructions`, `rules`, `bin`, and
`tools` folders. Resolve it from the absolute path of the canonical Markdown
file you loaded: for example, an instruction loaded from
`C:\src\llm-shared\instructions\spec-reviewer.md` gives
`<LLM_SHARED_DIR> = C:\src\llm-shared`. Substitute that resolved directory in
the command itself. The angle-bracket name is documentation notation, not a
literal argument or a requirement for an environment variable.

Never reinterpret a shared launcher relative to the consuming repository:
do not shorten it to `.\bin\...`, guess `..\llm-shared\...`, or rely on
`$env:LLM_SHARED_DIR` / `%LLM_SHARED_DIR%`. A consuming repository may have a
different parent, and a non-interactive tool shell may have no inherited
llm-shared variables.

The `llm-shared` `bin\*.bat` launchers (`wac.bat`, `gcba.bat`, `ghog.bat`,
`oqm.bat`, `prompt_workflow.bat`, ...) self-locate: each derives
`LLM_SHARED_DIR` from its own `bin\` path when the caller did not set it, and
resolves its Python from the llm-shared `venvs\` folder. The first-attempt
shape is a plain full-path call, from PowerShell:

```text
& "<LLM_SHARED_DIR>\bin\wac.bat" <plain arguments>
```

- Do not rely on the `LLM_SHARED_DIR` environment variable, on a doskey alias
  (`pw`, `wac`), or on a prior `senv.bat` call: none of them exists in a
  non-interactive tool shell.
- The error `ERROR: No python_3* directory found in "\venvs"` (note the empty
  path root) is the signature of an outdated launcher copy that still requires
  `LLM_SHARED_DIR`. The one-off workaround is to set the variable in the same
  process, `$env:LLM_SHARED_DIR = "<path>"; & "$env:LLM_SHARED_DIR\bin\wac.bat"`,
  then update llm-shared so the next call self-locates.

The root-level `commit-plan-check.bat` launcher follows the same rule but is
not under `bin`: call it as
`& "<LLM_SHARED_DIR>\commit-plan-check.bat" --format json`.

## Quiet waits preserve model quota

A quiet long-running command must also be quiet at the tool transport layer.
Starting one watcher process is not enough if the host resumes the model every
minute to receive "still running" and issue another wait. Those resumptions
spend quota even when the command emits no output and no `status` call runs.

`review_exchange.bat wait-any-request` must resume reviewer work on detection
without requiring another user message. Request detection and model resumption
are separate: a process can keep watching after an assistant turn ends without
being able to start the next turn. Select the transport by host.

### Codex uses an attached wait

Codex must keep the assistant turn active and await the watcher through an
attached tool execution. Do not send a final response while waiting, leave only
a background process running, or defer processing its result to the next user
turn. A live watcher alone does not satisfy active waiting in Codex.

If the tool yields a process or session handle before completion, retain it
and continue awaiting that same execution with the host's continuation tool
(`functions.wait`, `write_stdin`, or equivalent). A tool transport yield does
not end the reviewer task. When final JSON reports `found`, immediately follow
the identity and ownership gates in `instructions/review-resume.md`, then
review the selected request in the same active session. After publishing an
answer, enter the attached global wait again.

Use the longest supported transport interval permitted by higher-priority
instructions at every tool layer. Awaiting the existing process is transport
continuation, not a new protocol poll. Do not add repeated `status` calls,
filesystem scans, watcher restarts, or idle progress messages merely to check
whether a request appeared. Follow higher-priority progress requirements when
they apply. Handle user messages as steering, retaining the wait handle and
any completed result; resume waiting unless the user stops or replaces the task.

When the user asks for review status during an attached wait, follow the
[Codex status-check isolation rule](../instructions/review-status-command.md#codex-status-check-isolation).
Use a fresh, status-only helper with no active conversation context; the
waiting reviewer retains its execution handle and ownership capability.
A status check neither replaces nor restarts the attached watcher, and must
not become recurring polling.

### Claude uses background completion

Claude may run the watcher in a host-managed background execution session and
return control of the chat. Retain the handle and use the supported completion
notification to resume automatically, retrieve final JSON, and dispatch the
selected request. Do not require a new user message. This background transport
must not monopolize the chat with an outer tool wait.

Do not apply Claude's return-control rule to Codex. Other hosts retain their
supported execution and completion mechanisms; report unavailable automatic
resumption instead of inventing a callback.

### Shared wait safeguards

Start the watcher once and reuse its live handle instead of launching another
for each user message or transport yield. The command remains a blocking
watcher inside its execution session; it needs no daemon, service, or detached
agent. Keep its result, including any ownership capability, in the tool session
or session memory. Never redirect it to a persistent log or save the capability
to files or environment variables.

The watcher owns filesystem observation and protocol deadlines. A tool
transport timeout is not a protocol outcome: it does not authorize restarting
the process, resetting its deadline, or interpreting silence as completion.

For bounded `wait-request` and `wait-answer` operations and watcher
continuations, use the longest supported transport interval
permitted by higher-priority instructions. Prefer several minutes (for example,
600000 ms when supported) to recurring 60000 ms model wake-ups. A short default
yield is not a mandatory maximum. Check every outer tool layer too: a long
inner wait does not help if its wrapper needlessly resumes the model every
minute. Respect the host-specific attached or background transport above.

If the host or a higher-priority instruction prevents the required transport,
explain the limitation once. Do not claim automatic review will resume when
only request detection remains possible. Preserve role isolation.

## Targeted reads instead of whole-document dumps

Never concatenate several whole documents in one command "to gather context": that output is huge, mostly unread, and already wasted when the next action needs a specific section.

- Read each document with the file tool, one document or one section at a time for large files.
- Search with `rg` using a narrow pattern and bounded context (`-C 10`, not `-C 80`).
- Run a command only when its output feeds the very next action.

## A marker check is a command at its own moment, never a recalled listing

An instruction that says to sample a marker, a flag file, or any state file names *when* to sample it as much as *what* to sample. A directory listing taken earlier for another purpose is not that sample, and treating it as one turns a scheduled branch into a coin flip decided by whatever the listing happened to show.

- Test the exact resolved path at the moment the instruction schedules the test, with `Test-Path` in PowerShell or `test -f` in a POSIX shell, or better, run the command that resolves the state and answers.
- Prefer the command over the path whenever a launcher exists. A path written in prose drifts from the path the tooling resolves; a launcher cannot.
- Never read absence from a plain `ls`, from `git status`, or from memory of either. A marker in a dotted directory is invisible to the first, an ignored marker is invisible to the second, and a stale recollection is invisible to review.
- A failed or unavailable check is not a negative answer. Report the diagnostic and stop; do not let "the command did not run" become "the state is off".
- State the sampled result in one line before acting on it. A check whose result is never stated reads exactly like a check that never happened.

## Diagnose before re-running or escalating

A failed command falls into one of two cases, and they have opposite fixes:

- A parse or quoting error (`The term '\' is not recognized`, `'X' is not recognized as an internal or external command`): the command string itself is broken. Rewrite it simpler — fewer layers, fewer quotes — and never re-run it verbatim, never escalate it: approval does not fix quoting.
- A sandbox block (`Access is denied`, `Unable to create virtual env`, `Failed to export ... environment variables`) on a command that parsed and started: re-run that exact command once with escalated or approved execution, as the project instructions describe.

When both kinds of error appear in the same output, fix the quoting first: a command line that breaks apart mid-parse produces misleading downstream errors, and escalating it only replays the same broken string.
