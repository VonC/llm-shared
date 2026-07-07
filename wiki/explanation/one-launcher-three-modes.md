# One launcher, three modes

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

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

The document phase's next step is always a standard slash skill that
loads its own full instructions when it runs. So `pw skill` prints only
the bare command — `/review-ask-questions on docs\design.vX.Y.Z.<slug>.md`
— on stdout. The verbosity is not lost, only deferred to the skill it
names. Terse output also suits its callers: a `## Handoff` section that
just needs the one line to run next.

## 🎛️ Why the interactive mode still exists

`pw` with its menu is the manual override: the human picks the step when
the chain is not running, when a phase must be redone, or when the state
on disk is ambiguous. The forced form `pw skill <skill-name>` serves the
same purpose inside scripts — print a specific earlier phase's command
and re-run it by hand.

## 🔤 The host prefix, decided at print time

The same workflow drives Claude Code and Codex, whose commands differ
only by prefix: `/` versus `$`. `pw skill` reads `CLAUDECODE` or
`CODEX_THREAD_ID` and prints the right one, so the instruction bodies
never hard-code a host.

## 👉 Where the modes are specified

- [pw launcher reference](../reference/pw-launcher.md) for every form and
  flag.
- [Run pw from any shell](../how-to/run-pw-from-any-shell.md) for the
  invocation mechanics.
