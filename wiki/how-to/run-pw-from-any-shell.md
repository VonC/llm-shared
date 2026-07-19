# How to run pw from any shell

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🔁 Goal: call the prompt-workflow launcher from a tool shell (Claude Code,
Codex, a script) where the bare `pw` Doskey alias does not exist.

## Invocation model

The AI normally calls the full `prompt_workflow.bat` launcher when another skill
needs `pw`; the interactive alias is a human convenience. Call the launcher
directly to open its menu, diagnose host-shell behavior, or resume a known
handoff without repeating the whole parent workflow.

## 🐚 Why the bare alias fails outside cmd

`pw` is a Doskey macro loaded by `senv.bat` in an interactive `cmd`
session. A tool shell (PowerShell, a sandboxed bash) never loads it. The
launcher itself, `bin\prompt_workflow.bat`, works from anywhere: it
self-locates the llm-shared folder and its bundled Python from its own
path — no `senv.bat` needed first.

## 📋 Invocation forms

From PowerShell:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-commit 3
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" handoff check 3
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" handoff after-check 3
```

From `cmd`, drop the `&` call operator. Never wrap the call in a nested
`cmd /d /c` from Git Bash: the POSIX shell mangles the `/c` and `/d`
switches and the call becomes a silent no-op.

## 🖨️ What each form prints or writes

| Form | Emits | Where |
| --- | --- | --- |
| `pw skill` | the bare next-step command | stdout |
| `pw skill --after-commit <x>` | the contextual after-commit action | stdout |
| `pw handoff check <x>` | the full implementation-check prompt | `a.prompt.txt` + clipboard |
| `pw handoff after-check <x>` | the routed next cycle prompt | `a.prompt.txt` + clipboard |

After a `handoff` call, confirm the first line of `a.prompt.txt` names the
expected instruction, then follow that prompt. The step is also recorded
in `a.prompt_memory`.

## 🔤 Forcing the host prefix

`pw skill` prints `/` when `CLAUDECODE` is set and `$` when
`CODEX_THREAD_ID` is set; `pw skill --host claude` or `--host codex`
forces it. The forced form `pw skill <skill-name>` prints a specific
earlier phase's command, to re-run that phase by hand.

## ✅ Check the launcher works

`& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill` prints exactly one
command line. An error naming
`No python_3* directory found in "\venvs"` means a stale copy of the
launcher is being called: point at the launcher inside the real llm-shared
checkout.

Related: [pw launcher reference](../reference/pw-launcher.md),
[run_commands rule](../reference/writing-rules.md).
