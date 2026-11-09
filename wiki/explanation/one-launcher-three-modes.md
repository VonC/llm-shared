# One launcher, three modes

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Workflow skills normally call `pw skill`, `pw skill --after-write <role>`, and
`pw handoff` themselves. Use the interactive `pw` menu directly to choose a
next step by hand, or call a mode directly when diagnosing or resuming a known
routing state.

🔁 `pw` answers a single question — what is the next step of this effort?
— three different ways, because three different callers need the answer:
a human at a menu, the implement chain, and the document chain. All three
read the same state; they differ in who picks the step and how much text
travels.

## 🗂️ The shared question and its state

Every mode resolves the topic from the branch and the `docs\` tree, then
reads what is on disk: which documents exist, whether they carry open
questions or a settled decision table, which plan steps are done. The
state is the filesystem — there is no hidden database, only
`a.prompt_memory` remembering the branch's locked topic and current step.

Topic identity is not always the draft filename. A collection draft can remain
`draft.v10.0.0.sentinel.md` while an item uses
`issue.v10.0.0.route-cleanup.md` on branch `route_cleanup`. If ordinary memory
and changed-draft resolution have no answer, the menu-less `pw skill` and
`pw handoff` modes use the same fallback. They connect those three facts only
when the normalized branch matches one requirement and one direct or umbrella
draft is related. Sharing the resolver prevents the document chain from
recognizing an item that the implementation chain cannot hand off. Refusing
missing or ambiguous relationships keeps a convenient fallback from becoming a
guess.

## 🗣️ Why pw handoff is verbose

The implement cycle's next prompt cannot be a bare command: it needs the
plan step number, the step title read from the plan, the staged file set,
the Yes/No branch of the check. `pw handoff <task> <x>` assembles that
context into a complete prompt in `a.prompt.txt`, because the next cycle
instruction needs it built for it.

Its `after-check` task is deliberately neutral: the caller does not say
which branch comes next, `pw` reads the `Analysis of Step x` verdict the
check just wrote and routes — so the caller cannot pick the wrong step.

## 🤫 Why pw skill is terse

The document phase's next step is always a standard skill that loads its own
full instructions when it runs. Skill mode therefore prints only the bare
command on stdout; the verbosity is deferred to the skill it names.

There are two distinct questions behind that terse answer:

- Bare `pw skill` asks **what follows the state now on disk?** Review and
  consolidation use it because their decision markers are evidence.
- `pw skill --after-write design` says **a design was just written; review that
  artifact now**. Writers use this event-aware form because their prose can
  legitimately contain words that resemble an old settled marker.

Keeping event and state separate prevents a writer from skipping review while
preserving automatic advancement after review actually settles the document.

## 🎛️ Why the interactive mode still exists

`pw` with its menu is the manual override: the human picks the step when
the chain is not running, when a phase must be redone, or when the state
on disk is ambiguous. The forced form `pw skill <skill-name>` serves the
same purpose inside scripts — print a specific earlier phase's command
and re-run it by hand.

## 🔤 The host command, decided at print time

The same workflow drives Claude Code and Codex, but Codex lists the linked
skill package under its namespace, so a command needs both its `$` prefix and
that namespace. `pw skill` reads `CLAUDECODE` or
`CODEX_THREAD_ID` and prints `/write-design` for Claude or
`$llm-shared:write-design` for Codex. Instruction bodies can therefore use a
neutral command placeholder instead of hard-coding either host form.

## 👉 Where the modes are specified

- [pw launcher reference](../reference/pw-launcher.md) for every form and
  flag.
- [Run pw from any shell](../how-to/run-pw-from-any-shell.md) for the
  invocation mechanics.
