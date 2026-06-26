# Run commands right on the first attempt

Every shell command costs tokens twice: once for the call, once for its output landing in the context window. A broken or oversized command spends that budget without producing anything usable, and a retry of the same broken command spends it again. These rules exist so the first attempt is the one that works.

## File reads never go through an environment wrapper

An environment wrapper such as `senv.bat` — always at the project root (`%PRJ_DIR%\senv.bat` when `PRJ_DIR` is set, never a copy under `bin\`) — is a contract for toolchain commands only: build, check, test, and dependency tooling (`check.bat`, `ghog`, `pytest`, `python`, `uv`). Reading or searching files never needs the project environment:

- Use the harness file tools (file read, grep/rg search) when the harness has them.
- Otherwise run a plain direct command (`rg`, `type`, `Get-Content`) with no wrapper.
- Never chain `senv.bat && <file read>`: the wrapper adds its whole setup output, its own failure modes (sandbox blocks, missing tools), and an extra quoting layer, for a task that needs none of it.

## One shell per command, no nested quoting

Never embed a quoted shell inside another quoted shell. A form like `cmd /c "senv.bat && powershell -Command "<script>""` cannot work: `cmd.exe` has no `\"` escaping, so the inner double quotes split the command line, and `$`, `;`, `&&` inside the script are parsed by the wrong shell. The visible symptom is a parse error such as `The term '\' is not recognized` or `'X' is not recognized as an internal or external command`.

- When a `.bat` wrapper is the toolchain entrypoint, try the wrapper first from
  the project root: `cmd /d /v:on /c "<one-executable> <plain arguments>"`.
  Several wrappers load `senv.bat` themselves and need to own that setup.
- If the wrapper-first command fails because project tools are not exposed on
  `PATH`, check whether the inherited environment defines the project-specific
  guard `NO_MORE_SENV_%PRJ_DIR_NAME%`.
- When the project environment is required and the guard is not defined, chain
  exactly one simple command from the project root, where `senv.bat` sits
  (`%PRJ_DIR%\senv.bat` when `PRJ_DIR` is set, never `bin\senv.bat`):
  `cmd /d /v:on /c "senv.bat && <one-executable> <plain arguments>"` -- no
  inner double quotes, no `$`, no multi-statement script in the chained part.
- When `NO_MORE_SENV_%PRJ_DIR_NAME%` is defined, clear it in the same `cmd`
  process before calling `senv.bat`:
  `cmd /d /v:on /c "set NO_MORE_SENV_%PRJ_DIR_NAME%=& senv.bat && <one-executable> <plain arguments>"`.
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
the same `cmd` process before calling `senv.bat`. Do this unconditionally; there
is no need to check whether the variable is currently defined.

Use this first-attempt shape from the project root:

```bat
cmd /d /v:on /c "set NO_MORE_SENV_%PRJ_DIR_NAME%=& senv.bat && python path\to\<a_script.py> <plain args>"
```

Keep the chained part to one Python executable plus plain arguments. Do not add
an inner shell, command substitution, or a multi-statement script inside the
quoted `cmd /c` body.

## Targeted reads instead of whole-document dumps

Never concatenate several whole documents in one command "to gather context": that output is huge, mostly unread, and already wasted when the next action needs a specific section.

- Read each document with the file tool, one document or one section at a time for large files.
- Search with `rg` using a narrow pattern and bounded context (`-C 10`, not `-C 80`).
- Run a command only when its output feeds the very next action.

## Diagnose before re-running or escalating

A failed command falls into one of two cases, and they have opposite fixes:

- A parse or quoting error (`The term '\' is not recognized`, `'X' is not recognized as an internal or external command`): the command string itself is broken. Rewrite it simpler — fewer layers, fewer quotes — and never re-run it verbatim, never escalate it: approval does not fix quoting.
- A sandbox block (`Access is denied`, `Unable to create virtual env`, `Failed to export ... environment variables`) on a command that parsed and started: re-run that exact command once with escalated or approved execution, as the project instructions describe.

When both kinds of error appear in the same output, fix the quoting first: a command line that breaks apart mid-parse produces misleading downstream errors, and escalating it only replays the same broken string.
