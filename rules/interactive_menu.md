# Interactive choices

When a workflow needs an explicit user decision, prefer a host-native choice
mechanism if one is available: a menu picker, `request_user_input`, an IDE
picker, a Codex-provided interactive UI, or another tool that returns the
selected value to the agent.

Read this rule before presenting any workflow menu, and before ending a turn on
any question the user must answer, whether a choice or a plain-text question.
The workflow instruction specifies the
concrete choices for that decision. Add the standard final entries only when
the current host can actually present them as part of an interactive choice:

1. `Type something else`
   - This lets the user provide a custom value or instruction.
2. `Let's Chat about it`
   - This stops the workflow and waits for discussion.

## Present the choices with the best interface available

A blocking picker holds the turn until the user selects: Claude Code's
`AskUserQuestion`, Codex's `request_user_input`, or an IDE picker whose tool
returns the selection. Use it whenever it is listed in the current turn's
tools; the host then shows the agent as waiting by itself. Codex lists
`request_user_input` in Plan mode, and in Default mode only with its
`default_mode_request_user_input` feature. Codex's `request_user_input_async`
returns before the user answers: it is an asynchronous picker, not a blocking
one. A blocking picker that returns no answer leaves the decision open: never
continue on your own judgment, as a host's default guidance may suggest.

If the current host has no native menu or input tool, use a normal chat fallback
instead of stopping. Present the concrete workflow choices as a clear numbered
list and ask the user to reply with the number or label. Do not add the two
standard final entries in the chat fallback; the user can always type something
else or start a discussion in chat.

Do not assume that shell commands have a live interactive TTY. Do not run raw
terminal UI commands such as `gum choose`, `fzf`, `Read-Host`, or similar tools
unless the current host explicitly supports interactive command sessions where
the user can provide input after the command starts.

## Signal a decision that no blocking picker holds

A turn that ends on a question no blocking picker holds looks finished: a chat
list, an asynchronous picker, or a plain-text question in the final message.
The host, tuios and Windows Terminal show the agent as done or idle. Codex in
Default mode is the usual case. Before such a turn ends, report the wait to
the terminal with OSC 7501, the
[Program Status Protocol](https://www.superlogical.com/rex/docs/build/program-status):

1. Present the choices, or the question: the chat list or the picker stays
   visible.
2. Run this as the turn's last command, then end the turn with the final
   message that shows the question:

   ```powershell
   & "<LLM_SHARED_DIR>\bin\program_status.bat" blocked --kind question --id question --app <app> --msg "<pending question, one line>"
   ```

3. Do not wait inside the turn: no sleep, no polling, no watcher. The user's
   next message resumes the work.

Resolve `<LLM_SHARED_DIR>` as
[run_commands.md](run_commands.md#llm-shared-launchers-run-by-resolved-full-path-no-environment-setup)
describes. Outside Windows, run `python <LLM_SHARED_DIR>/tools/program_status.py`
with the same arguments. `<app>` names the host, the same in every report:

| Host | `--app` |
| --- | --- |
| Codex | `codex` |
| Claude Code | `claude` |
| GitHub Copilot | `copilot` |
| Gemini CLI | `gemini` |
| Grok | `grok` |

Another host uses its lowercase product name: letters, digits, `-`, `_`, `.`
or `+`, at most 32 characters.

`--id question` keeps the wait in a record of its own. A host such as Codex
reports its turns on the terminal's main record, `working` and then `done`
once the turn ends, which would replace a `blocked` report sent there. A
terminal shows the agent as waiting while any of its records is `blocked`.

The helper writes the bytes to the console of the agent's own terminal, not to
the captured command output, and prints where they went. Exit 0 means the
terminal took the report. Exit 3 means no terminal could be reached, as in an
IDE chat panel: say in the final message that the waiting status was not sent.
Exit 2 names an invalid argument to fix. Never print the escape sequence
yourself instead: text in the chat or in captured output reaches no terminal.

Codex sessions that share the background app-server daemon (the
`daemon_auto_start` feature, on by default) run their commands under that
daemon, outside their own terminal. The helper then exits 3 rather than
signal the pane of the session that started the daemon.

## Keep the decision open until the user answers

- Only an explicit selection or reply decides. Never infer a decision from
  silence, select the recommended option on the user's behalf, or record an
  unanswered question as decided.
- Do not continue work that depends on the answer. Finish only independent
  work, before the `blocked` report.
- A typed reply counts: read it as a choice, an amendment, a request for more
  explanation, or a change of direction.

## Report the end of the wait

A report replaces its record, and the terminal keeps the last one: a stale
`blocked` or `working` record hides the host's own status. After a `blocked`
report, keep the same `--app` and `--id question`, and report each step:

| When | Report |
| --- | --- |
| The user answers and the work resumes | `working`, as the turn's first command |
| The user cancels or postpones the decision | `idle` |
| The turn ends on another pending decision | `blocked --kind question` |
| The turn ends with the work finished | `done` |
| The turn ends on a failure that stops the work | `error` |
| The turn ends after a cancellation, with nothing to report | `clear` |

The terminal drops `working` and `blocked` when the agent exits or a shell
prompt returns. tuios keeps `done` and `error` until the user types in the
pane.

## Go-ahead menus

For go-ahead menus, the default concrete choice is usually `Go ahead`. If the
workflow has a contextual next action, include that contextual action as a
concrete choice. A `Go ahead and do this` entry is only appropriate when the host
can collect the follow-up text as part of an interactive choice; otherwise omit
it from the concrete choices and let the user type a follow-up in chat.
