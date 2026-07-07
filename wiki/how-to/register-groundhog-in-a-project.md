# How to register groundhog in a project

<img src="../assets/logo-llm-shared-groundhog-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🧪 Goal: make the groundhog fixing loop triggerable from Claude Code and
ChatGPT Codex in a given project, with one command.

## 📋 One command writes three pointers

From the project root:

```cmd
ghog init
```

All three pointers reference the single `instructions/groundhog.md` body:

- `.claude\skills\groundhog\SKILL.md` — the Claude Code skill, with the
  trigger phrases in its description and a relative link computed from the
  actual layout (a sibling `..\llm-shared` and a `llm-shared` submodule
  both work),
- a `## groundhog` section appended to the project's `AGENTS.md` — the
  Codex channel; an existing file is never rewritten, the section is
  appended once and recognized on later runs,
- `~/.codex/prompts/groundhog.md` — a user-level Codex custom prompt that
  makes `/groundhog` deterministic; written only when `~/.codex` exists,
  and project-agnostic, so one copy serves every repo.

Re-running `ghog init` is idempotent.

## 🤖 Triggering the loop from Claude Code

Type `/groundhog`, or ask in plain words: "run groundhog", "fix tests and
coverage", "reach 100% coverage". Claude Code then follows
`instructions/groundhog.md`.

## 💻 Triggering the loop from Codex

Start a fresh session (a newly written `AGENTS.md` is only seen by
sessions started after it exists), then type `/groundhog` or ask "run
groundhog". Sandbox notes:

- ghog and covg need real filesystem access; run them escalated from the
  start,
- output containing `Access is denied`, `gum choose` or
  `Unable to create virtual env` means the sandbox blocked `senv.bat`:
  re-run the same command escalated, never debug `senv.bat` or create a
  venv yourself,
- harness tool timeouts are covered by `ghog day --detach` plus
  `ghog status` polling.

## ♻️ Refreshing a stale registration

An already-registered `AGENTS.md` section is never updated in place:
delete the `## groundhog` section and re-run `ghog init`. If `/groundhog`
is unknown in Codex, re-run `ghog init` and start a fresh session.

## ✅ Check the registration

The three files above exist (the Codex prompt only if `~/.codex` does),
and "run groundhog" in a fresh agent session starts a `ghog day` walk
redirected to `a.ghog.log`.

Related: [Your first groundhog walk](../tutorials/03-your-first-groundhog-walk.md),
[One body, many agents](../explanation/one-body-many-agents.md).
