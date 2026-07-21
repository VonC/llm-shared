# pw launcher

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🔁 The prompt-workflow launcher: `bin\prompt_workflow.bat`, wrapping
`tools\prompt_workflow.py`, aliased `pw` in an interactive `cmd`. It
answers one question — what is the next step of this effort? — in three
modes.

## Invocation model

Other skills normally let the AI call this launcher as an internal handoff.
Humans call it directly to use the interactive menu, debug dispatch, or resume a
specific known phase without restarting the parent workflow.

## 🧠 Shared core of every mode

All modes resolve the topic from the branch and the `docs\` tree (locked
per branch in `a.prompt_memory`), read the same workflow state (which of
draft, requirement, design, plan, validation exist; open questions or
settled decision table; which plan steps are done), and know the host:
`CLAUDECODE` means a `/` prefix, `CODEX_THREAD_ID` means `$`.

## 🎛️ The three modes side by side

| Mode | Step chosen by | Emits | Channel |
| --- | --- | --- | --- |
| `pw` | a human, from a menu | a full next-step prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw handoff <task> <x>` | the caller (the step is given) | a full, assembled cycle prompt | `a.prompt.txt` + clipboard + `a.prompt_memory` |
| `pw skill [name]` | derived from the docs on disk | one bare command line | stdout |

## 🤝 pw handoff tasks

| Call | When | Prompt written |
| --- | --- | --- |
| `pw handoff check <x>` | after `/implement-step <x>` or `/implement-missing-step <x>` ends green | the `implementation-check.md` prompt for step `<x>` |
| `pw handoff after-check <x>` | after `/implementation-check <x>` records its verdict | routed: `implement-missing-step.md` on `No`, `group-commits-msg.md` (`git add -A` form) on `Yes` |

`after-check` is neutral on purpose: `pw` reads the `Analysis of Step x`
status line the check wrote, so the caller cannot pick the wrong branch.

## 🗂️ What pw skill derives from disk

| State on disk | Printed command |
| --- | --- |
| fresh draft, no requirement | `/process-draft on docs\draft...md` |
| doc still carrying `## Open questions` | `/consolidate-then-review-ask-questions on ...` |
| current doc fresh: no open questions, no consolidated decisions | `/review-ask-questions on ...` |
| settled requirement | `/write-design` |
| settled design | `/write-plans` |
| settled plan, uncommitted validation work | `/implement-step <x>` |
| settled plan, final step committed | `/prepare-release` |

"Settled" means consolidated, not merely titled: the document must carry a
decisions section (`Requirement clarifications`, `Design decisions`, or
`Implementation decisions`) holding at least one row opening with a question id
(`| Qxx`) or the "No open questions" row a no-question review writes. A
decisions heading seeded by the document writer does not count, so a freshly
written plan always routes to its review round before any `/implement-step`.
The `<x>` of `/implement-step` comes from the validation plan's own step list:
the last verified step, or the plan's first step when none is verified, which
is not always `1` (a plan may open on a step 0). Whether the settled-plan
command is run at once (the default) or shown and held (`stop here` in the
consolidation invocation, or an explicit human instruction) is decided by the
skill instructions, not by `pw`.

## 🚩 Flags and special forms

| Form | Effect |
| --- | --- |
| `pw skill --after-commit <x>` | told the plan step the pending commit completes, prints the contextual next action (next `/implement-step`, `/prepare-release`, or nothing) — read-only, used to build the commit-gate labels |
| `pw skill --host claude\|codex` | forces the command prefix |
| `pw skill <skill-name>` | prints a specific earlier phase's command, to re-run it by hand |
| `pw --pick` | reopens the topic menu when the branch lock is wrong |
| `--root`, `--debug` | shared flags of the underlying tool |

## 🚦 Exit and error behavior

The tool exits `2` on fatal errors (`EXIT_FATAL`). A launcher error naming
`No python_3* directory found in "\venvs"` means a stale copy of
`prompt_workflow.bat` outside the real checkout.

Related: [Run pw from any shell](../how-to/run-pw-from-any-shell.md),
[One launcher, three modes](../explanation/one-launcher-three-modes.md).
