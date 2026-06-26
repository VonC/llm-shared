# Command prefix character

Read this rule before printing, presenting, or composing a workflow command that
starts with a host command prefix, such as `review-ask-questions`,
`write-requirement`, or `implement-step`.

Use the prefix that matches the active host:

- Use `$` when `CODEX_THREAD_ID` is present in the environment. This is a Codex
  session.
- Use `/` when `CLAUDECODE` is present in the environment. This is a Claude Code
  session.
- If both are present, prefer `$` because the active shell is running inside
  Codex.
- If neither is present, do not guess. Use the neutral placeholder
  `<command-prefix>` in written examples, or run `pw skill` through its launcher
  and use the prefix printed by that tool.

When an instruction says to print a next-step command, replace
`<command-prefix>` with the selected prefix. For example, in Codex print
`$review-ask-questions on docs/feature-request.vX.Y.Z.<slug>.md`; in Claude Code
print `/review-ask-questions on docs/feature-request.vX.Y.Z.<slug>.md`.

When `pw skill` prints a command, trust the prefix it printed unless the user
explicitly asks you to override it.
