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
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-write design
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-commit 3
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" document v10.0.0 route-cleanup plan
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
| `pw skill --after-write requirement\|design\|plan` | review of the artifact just written | stdout |
| `pw skill --after-commit <x>` | the contextual after-commit action | stdout |
| `pw document <version> <slug> <type>` | the unique repository-relative document path | stdout |
| `pw handoff check <x>` | the full implementation-check prompt | `a.prompt.txt` + clipboard |
| `pw handoff after-check <x>` | the routed next cycle prompt | `a.prompt.txt` + clipboard |

After a `handoff` call, confirm the first line of `a.prompt.txt` names the
expected instruction, then follow that prompt. The step is also recorded
in `a.prompt_memory`.

## 🔤 Forcing the host prefix

`pw skill` prints `/write-design`-style commands when `CLAUDECODE` is set
and `$llm-shared:write-design`-style commands when `CODEX_THREAD_ID` is set;
`pw skill --host claude` or `--host codex` forces the host form. The forced
form `pw skill <skill-name>` prints a specific earlier phase's command, to
re-run that phase by hand.

## 📝 Pick the right skill form

Use bare `pw skill` when asking what follows the current state on disk, such
as after review or consolidation. Use `--after-write` inside a writer handoff:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-write requirement
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-write design
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill --after-write plan
```

The explicit form deliberately ignores settled-looking decision markers and
reviews the named artifact. It exits without printing a command if that
artifact does not exist.

## 🔎 Find a document without knowing its folder

Pass only the full version, topic slug, and document type:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" document v10.0.0 route_cleanup design
```

The locator checks `docs/`, `docs/v10.0/`, `docs/v10.0.0/`, and
`docs/v10.0/v10.0.0/`. It treats `route_cleanup` and `route-cleanup` as the same
slug. Use one of `draft`, `requirement`, `feature-request`, `issue`, `design`,
`plan`, or `validation-plan` as the type.

If the same exact selector exists in more than one layout, remove or relocate
the duplicate. The command deliberately reports ambiguity instead of choosing
one copy.

On an item branch split from a collection draft, you do not need to rename the
umbrella draft. All menu-less forms — bare, post-write, and post-commit
`pw skill`, plus `pw handoff` — use the same topic resolver. If ordinary
resolution has no topic, they match the normalized branch leaf
(`route_cleanup`) to one requirement slug (`route-cleanup`) and then to its
direct draft or one same-version umbrella draft that mentions the complete
slug. More than one matching requirement or related draft is an ambiguity and
the launcher refuses to route. Do not add a temporary same-slug draft alias.

On a clean branch named for the umbrella itself, bare `pw skill` can recover
that umbrella without a changed-file candidate. It requires exactly one
branch-matched canonical umbrella with a nonempty ordered table and prints the
`process-draft ... based on <slug>` command for its first valid pending row.
An absent or ambiguous umbrella remains not applicable.

## ✅ Check the launcher works

`& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" skill` prints exactly one
command line. An error naming
`No python_3* directory found in "\venvs"` means a stale copy of the
launcher is being called: point at the launcher inside the real llm-shared
checkout.

Related: [pw launcher reference](../reference/pw-launcher.md),
[Artifact files and naming conventions](../reference/artifact-files.md), and
[run_commands rule](../reference/writing-rules.md).
