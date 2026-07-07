# How to pick up skill edits without restarting

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Goal: after editing a skill — its instruction body, its `SKILL.md`, or
the Python behind a launcher — know which host picks the change up live
and which one needs a fresh session.

## ⚡ Claude Code reads the edits live

No relaunch for the common edits: Claude Code watches the skill
directories, and the workflow's moving parts are read fresh anyway.

| What changed | When it takes effect | Relaunch? |
| --- | --- | --- |
| `instructions/*.md` (a skill body) | read fresh on the next skill invocation | no |
| `tools/*.py` (the `pw` engine, ghog, ...) | fresh subprocess on the next call | no |
| `.claude/skills/*/SKILL.md` | watched live; injected fresh on the next invocation | no |

Only two cases still need a new session:

- a **brand-new skill folder** created after the session started — the
  watcher only registers it on the next launch,
- a changed **one-line description** in the available-skills list — the
  list is cached in the system prompt at session start; the `SKILL.md`
  body is fresh, the list entry is not.

## 🧵 Codex freezes the skill list per thread

Codex injects the available-skills registry when a thread is created,
and never retroactively: a resumed thread does not gain new or fixed
skills. After editing the plugin package under `.agents/llm-shared/`:

1. bump the `version` in `.codex-plugin/plugin.json`,
2. reinstall: `codex plugin add llm-shared@personal`,
3. start a **new** thread — resuming the old one is not enough.

`codex debug prompt-input` shows, outside any session, exactly which
skills the next thread will receive.

## 🧲 Antigravity follows the junction

The `.agent/workflows/` wrappers are plain files the agent reads when
the slash command runs, and the recommended wiring is a junction into
the clone — so an edit to a wrapper or to the `instructions/` body it
points at is picked up on the next invocation. Only a brand-new wrapper
file may need the `/` dropdown to refresh with a new session.

## 🧭 Copilot follows the workspace

Copilot discovers prompts and skills from the workspace roots; adding or
editing them under the llm-shared folder is picked up through the normal
VS Code file watching, with a window reload as the blunt fallback when a
new file does not appear in the chat picker.

## ✅ Check which version a session runs

Ask the session to read the skill file back (`read
instructions/<skill>.md and quote its first heading`) — what it quotes
is what it will execute. For Codex, prefer the `codex debug
prompt-input` check above, since the in-thread list can be stale by
design.

Related: [Register the skills as a Codex plugin](register-skills-as-a-codex-plugin.md),
[One body, many agents](../explanation/one-body-many-agents.md).
