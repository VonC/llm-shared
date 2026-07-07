# Writing rules

<img src="../assets/logo-llm-shared-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🤖 The shared rules under [`rules/`](../../rules/) that every skill body
imports. They apply to any agent using the skills, whatever the host.

## 🚫 blacklist.md

Words and expressions forbidden in every response outside code blocks —
buzzwords such as "leverage", "delve" or "seamless". The escape hatch is
the BBQ technique: say it the way two people at a barbecue would.

## ✍️ markdown.md

Formatting rules for any markdown the skills write: unique,
context-specific section titles (never a bare "Goal"); exactly one space
after list markers; an empty line before and after every list; two-space
sub-list indentation; and compact tables — single space around cell
content, exactly three dashes per header separator column.

## 🛡️ preserve_code.md

Never truncate when rewriting a file: every file is written from top to
bottom in full, with no `# ...existing code...` placeholders, and all
still-relevant comments and docstrings preserved.

## 🐚 run_commands.md

Get every shell command right on the first attempt — each one costs
tokens twice, call and output:

- file reads never go through an environment wrapper: `senv.bat` is for
  toolchain commands (build, check, test, deps), not for reading files,
- one shell per command, no nested quoting: the chain form is
  `cmd /d /v:on /c "senv.bat && <one-exe> <plain args>"`, issued from
  PowerShell or cmd, never from Git Bash,
- llm-shared launchers run by full path with no environment setup: they
  self-locate `LLM_SHARED_DIR` and their Python from their own `bin\`
  path,
- targeted reads instead of whole-document dumps: a narrow `rg` with
  bounded context,
- diagnose before re-running: a quoting or parse error means rewrite the
  command simpler, never re-run verbatim, never escalate; a sandbox block
  (`Access is denied`) means re-run once escalated.

## 🔤 command_prefix_char.md

Which prefix to print before a workflow command: `$` when
`CODEX_THREAD_ID` is set, `/` when `CLAUDECODE` is set, `$` when both
are, and the `<command-prefix>` placeholder (or the prefix `pw skill`
prints) when neither is.

## 🎛️ interactive_menu.md

Prefer the host's native choice mechanism for menus, adding the two
standard closing entries (`Type something else`, `Let's Chat about it`)
only when the host renders them interactively. Never assume a live TTY:
no `gum choose`, no `fzf`, no `Read-Host`. The default concrete choice of
a go-ahead menu is `Go ahead`.

## 💬 Chat rules from CLAUDE.md and copilot-instructions.md

Both agent rule files add the same session-level habits: treat opened
editors as context, check Python files under `src\` and `tools\` end with
`# eof`, print the relative pathname before every code block, write
impacted classes in full, and keep tests in step with the code they
cover.

Related: [One body, many agents](../explanation/one-body-many-agents.md).
