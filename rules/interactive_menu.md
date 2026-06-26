# Interactive choices

When a workflow needs an explicit user decision, prefer a host-native choice
mechanism if one is available: a menu picker, `request_user_input`, an IDE
picker, a Codex-provided interactive UI, or another tool that returns the
selected value to the agent.

Read this rule before presenting any workflow menu. The workflow instruction
specifies the concrete choices for that decision. Add the standard final entries
only when the current host can actually present them as part of an interactive
choice:

1. `Type something else`
   - This lets the user provide a custom value or instruction.
2. `Let's Chat about it`
   - This stops the workflow and waits for discussion.

If the current host has no native menu or input tool, use a normal chat fallback
instead of stopping. Present the concrete workflow choices as a clear numbered
list and ask the user to reply with the number or label. Do not add the two
standard final entries in the chat fallback; the user can always type something
else or start a discussion in chat.

Do not assume that shell commands have a live interactive TTY. Do not run raw
terminal UI commands such as `gum choose`, `fzf`, `Read-Host`, or similar tools
unless the current host explicitly supports interactive command sessions where
the user can provide input after the command starts.

For go-ahead menus, the default concrete choice is usually `Go ahead`. If the
workflow has a contextual next action, include that contextual action as a
concrete choice. A `Go ahead and do this` entry is only appropriate when the host
can collect the follow-up text as part of an interactive choice; otherwise omit
it from the concrete choices and let the user type a follow-up in chat.
