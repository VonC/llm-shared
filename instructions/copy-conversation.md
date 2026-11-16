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

In Claude Code the skill runs the launcher itself while it loads and shows
its result line: report that line and stop, with no command of your own.

Otherwise run the launcher once, from PowerShell, in the current checkout.
`<LLM_SHARED_DIR>` is the absolute parent of the `instructions` folder that
holds this file; this one command needs no `run_commands.md` read and no
`senv.bat` call:

```text
& "<LLM_SHARED_DIR>\bin\copy_conversation.bat" <host> [YYYYMMDD] [--title "<text>"]
```

| Argument | Value |
| --- | --- |
| `<host>` | `claude` when you run in Claude Code, `codex` when you run in OpenAI Codex; always your own host |
| `YYYYMMDD` | the user's date argument, if any, as typed; `--date YYYYMMDD` is the same |
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
| Title | `--title`; otherwise the tuitp tab whose expanded project folder contains the current directory, read from `%HOME%\bin\tuitp.list`; the deepest matching folder wins. `TUIOS_SESSION` breaks ties only among those matches. If no unique title matches, use the current directory's folder name; inherited `TUITP_PROJECT` cannot override it |
| Output | The clipboard, set as Unicode text so the markers survive (on Windows through the Windows API, elsewhere through PowerShell from a UTF-8 file), then one summary line on stdout |

## Optional mission journal

When `JOURNAL_MISSION` is present in the command's environment, it names an
existing absolute `YYYYMM-NAME` folder. After setting the clipboard, the same
command appends the exact copied text to:

```text
<JOURNAL_MISSION>\YYYYMM\<name-lowercase>YYYYMMDD.txt
```

Derive the filename prefix from the folder basename by removing its leading
`YYYYMM-` and lowercasing the remaining name, including any internal hyphens.
The folder's leading month does not restrict the journal date. Capture local
time once: before 06:00 the journal day is yesterday, and from exactly 06:00
it is today. Both the month subfolder and daily filename use that journal
day, including at month/year boundaries. The optional `YYYYMMDD` argument
still controls trimming only; it does not override the journal day.

The command creates the month subfolder and daily file if needed. It takes
exclusive access to the actual daily file on Windows, waits up to ten seconds
if another writer holds it, appends and flushes, then releases the handle even
on errors. POSIX uses a cooperative file lock. New files use UTF-8 without a
BOM; existing UTF-8 files, with or without a BOM, retain their bytes. A newline
separates entries when needed. The copied text is followed by a newline when
needed and a line containing exactly `~~~~~~~~~~~~~~~~`, ending in a newline.

An absent variable preserves clipboard-only behavior; an empty or invalid
value is an error. A new Windows user environment setting must reach the
host's process environment before the command can see it. The underlying
CLI's `--no-clipboard` also disables automatic journaling, and `--output`
cannot overwrite the selected journal file. Keep private mission paths and
names in the user's environment, never hard-code them in shared sources.

The summary names both the mission folder and the appended daily file. If
journaling fails after copying, the error explicitly says the clipboard is
ready and names the failed destination. Do not repeat the command automatically:
clipboard and file updates are separate operations, and a process crash can
leave an incomplete append. Caught write failures attempt to restore the old
file size while still locked and report any rollback failure.

## Report the result and stop

On exit code 0, report the summary line: host, transcript file, rendered and
kept line counts, title, and journal destination when enabled. Say the copy
is ready to paste, then stop. Do not append again outside the command.

On exit code 2, report the `ERROR:` line and stop. Do not retry with another
transcript, another host or a copy assembled by hand.

| Error | Meaning |
| --- | --- |
| `... is not set` | The host did not export its session id to the shell; the transcript cannot be identified |
| `No transcript found` | The host home holds no transcript for that id |
| `Nothing to copy` | No turn precedes the request: a new or cleared chat starts a new transcript |
| `kept no line` | Trimming removed every rendered line |
| `Failed to reach the clipboard` | PowerShell could not set the clipboard |
