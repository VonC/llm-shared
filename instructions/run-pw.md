# Running a pw command from a non-interactive shell

The workflow handoffs call `pw` commands: `pw skill`, `pw skill --after-write
<role>`, `pw skill --after-commit <x>`, `pw skill --after-merge
<umbrella-draft>`, and `pw handoff <mode> <x>`. This note gives the one reliable
way to run them, so each instruction can point here instead of repeating the
call.

## Why the bare pw alias fails in a tool shell

`pw` is a doskey macro set up by the project environment. A doskey macro only lives inside an interactive `cmd` prompt; it does not resolve under `cmd /c`, under PowerShell, or in any other non-interactive shell — the call just fails to find `pw`. Calling the bare `pw` from a tool shell is the trap to avoid.

The macro only stands in for the launcher `<LLM_SHARED_DIR>\bin\prompt_workflow.bat`. Call that launcher by its full path and the alias is no longer needed.

## The launcher needs no environment setup

`prompt_workflow.bat` self-locates: it derives `LLM_SHARED_DIR` from its own `bin\` path and runs the project `llm-shared` virtual-environment Python by absolute path, with no `PATH` lookup. So it does not need `senv.bat` or any prior activation — the full path to the `.bat` is enough, from any shell or repository.

## How to run a pw command

Follow the command rules in [`../rules/run_commands.md`](../rules/run_commands.md): get the call right on the first attempt, one shell per command, no nested quoting.

Resolve `<LLM_SHARED_DIR>` as the absolute parent of the `instructions` folder
that contains this canonical file. Substitute that path directly in every
command below; do not pass the placeholder literally, guess a relative
checkout, or rely on an environment variable.

From a PowerShell shell, use the call operator `&` — one shell, no nesting:

```text
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill
```

Replace `skill` with the actual sub-command and its arguments.

| pw command | PowerShell call |
| --- | --- |
| `pw skill` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill` |
| `pw skill --after-write <role>` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-write <role>` |
| `pw skill --after-commit <x>` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-commit <x>` |
| `pw skill --after-merge <umbrella-draft>` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-merge <umbrella-draft>` |
| `pw handoff check <x>` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" handoff check <x>` |
| `pw handoff after-check <x>` | `& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" handoff after-check <x>` |

From a `cmd` shell, drop the call operator and quote only the path:

```text
"<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill
```

## Do not add an environment wrapper

Do not replace the direct call with a nested
`PowerShell(cmd /c "senv.bat && ...")` chain. `senv.bat` is redundant for this
self-locating launcher, and the extra shell and quoting can turn the handoff
into a parse failure or silent no-op.

For a `pw handoff` command, which writes `a.prompt.txt`, `a.prompt_memory`, and the clipboard, do not wrap the launcher in a nested `cmd /d /c "..."` from Git Bash or another POSIX shell: the nested `cmd` can swallow the launcher's output and its file writes, so the handoff does nothing while still returning `0` — a silent no-op. Run it directly in PowerShell and confirm the launcher's `... ready` line before moving on.

## What the command prints

Before using or showing a host-prefixed workflow command printed by `pw`, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md).

A pw command prints one line to stdout, such as
`<command-prefix>review-ask-questions on <requirement-path>`, with the actual
selected effort directory and the prefix for the active host. Read that line
verbatim and act on it as the calling handoff describes; the not-applicable case
prints nothing and exits non-zero.
