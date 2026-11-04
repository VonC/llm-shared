# Copy the running conversation to the clipboard

Use when the user invokes `copy-conversation` or asks to copy this session's
conversation, trimmed, to paste it into their notes. One command reads the
session's own transcript, renders it as an export with no line wrapping, trims
it exactly as [`tth`](../wiki/how-to/trim-an-exported-conversation.md) does,
and leaves the result in the clipboard under a title line:

```text
<tab title>:

<trimmed conversation>
```

This is an LLM command, not a shell executable or `pw` subcommand. It accepts
two optional arguments: a `YYYYMMDD` date and `--title <text>`. Reject any
other argument instead of guessing.

## Run the launcher once

Read [run_commands.md](../rules/run_commands.md) before shell work and resolve
`<LLM_SHARED_DIR>` from this canonical file as that rule describes. Then run
the launcher once, from PowerShell, in the current checkout:

```text
& "<LLM_SHARED_DIR>\bin\copy_conversation.bat" <host> [--date YYYYMMDD] [--title "<text>"]
```

| Argument | Value |
| --- | --- |
| `<host>` | `claude` when you run in Claude Code, `codex` when you run in OpenAI Codex; always your own host |
| `--date` | the user's `YYYYMMDD` argument, if any |
| `--title` | the user's title, if any; otherwise the command finds it |

Any other host has no transcript reader yet: report that and stop. Do not
read, search or print the transcript yourself, and do not run `tth`
separately: the command already trims, and printing the copy would only add
it to the conversation.

## What the command does

| Step | Behavior |
| --- | --- |
| Transcript | The session's own file, found by the id the host exports to its shell: `CLAUDE_CODE_SESSION_ID` for `~/.claude/projects/*/<id>.jsonl`, `CODEX_THREAD_ID` for `~/.codex/sessions/**/rollout-*-<id>.jsonl` |
| Rendering | Claude: prompts, text answers, closing and recap lines with the export markers, unwrapped. Codex: `## User` and `## Assistant` sections. Tool calls, tool output and reasoning are left out. Answers to the agent's questions are kept as user text |
| Current turn | Cut when its prompt invokes `copy-conversation`, so the copy ends on the conversation before the request |
| Trimming | `tth`'s own trimmer, with today's date and the optional `--date`: a prompt starting with one of them drops every line before it |
| Title | `--title`; otherwise the tuitp tab whose `+` line names the pane's `TUIOS_SESSION`, read from `%HOME%\bin\tuitp.list`; otherwise the folder name of `TUITP_PROJECT` or of the current directory |
| Output | The clipboard, written from a UTF-8 file so the markers survive, then one summary line on stdout |

## Report the result and stop

On exit code 0, report the summary line: host, transcript file, rendered and
kept line counts, and the title. Say the copy is ready to paste, then stop.

On exit code 2, report the `ERROR:` line and stop. Do not retry with another
transcript, another host or a copy assembled by hand.

| Error | Meaning |
| --- | --- |
| `... is not set` | The host did not export its session id to the shell; the transcript cannot be identified |
| `No transcript found` | The host home holds no transcript for that id |
| `kept no line` | The transcript holds no prompt the renderer recognizes |
| `Failed to reach the clipboard` | PowerShell could not set the clipboard |
