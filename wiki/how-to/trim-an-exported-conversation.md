# Trim an exported conversation

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Turn a raw Claude Code or OpenAI Codex export into something a human can
read: keep what was asked and what was answered, drop the reasoning and the
tool traffic in between. The trimmed text goes back to the clipboard, ready to
paste into a report, an issue, or a document.

## Invocation model

This is a human-run command. Export a session, run `tth`, paste the result.
The AI may run it when explicitly asked to shorten a transcript it was handed.
The one skill that uses the same trimmer is `copy-conversation`, which the user
invokes in the session to copy; see
[Copy the running session instead](#copy-the-running-session-instead).

## When to reach for the trimmer

- Pasting a session into an activity report, a requirement document, or a
  pull-request description, where a raw export is unreadable.
- Handing a past session to another model as context without spending the
  budget on the reasoning and the shell output it no longer needs.
- Keeping a decision trail: the question and the answer are the parts a future
  reader needs, not the fifty tool calls that produced them.

## Trim what is in the clipboard

Export the session first. In Claude Code that is `/export`, which copies the
conversation to the clipboard; Codex exports a Markdown file with `## User`
and `## Assistant` headings.

With the export on the clipboard, run the alias with no argument:

```text
tth
```

The tool reads the clipboard, trims it, writes the result back to the
clipboard, and prints one line built on this shape:

```text
trim-thinking (<format>): <source> -> <kept> lines, <removed> reflection lines removed (<share>%). Ready to paste from clipboard.
```

The clipboard now holds the trimmed conversation. Nothing else is touched: the
source file, if there was one, is left alone.

## Trim a file instead

Pass a path to read from disk rather than from the clipboard. The result still
goes to the clipboard, so the file on disk is never rewritten:

```text
tth docs\session-export.md
```

From a shell with no Doskey aliases, call the self-locating launcher:

```text
& "<LLM_SHARED_DIR>\bin\tth.bat" docs\session-export.md
```

## Copy the running session instead

`/export` wraps Claude prose near 80 columns, and no setting turns that off.
To copy the session you are in, skip the export: invoke `copy-conversation` in
that session (`/copy-conversation` in Claude Code,
`$llm-shared:copy-conversation` in Codex). The agent reads its own transcript,
renders it unwrapped, trims it with this same trimmer, and leaves this in the
clipboard:

```text
<tab title>:

<trimmed conversation>
```

The title comes from `%HOME%\bin\tuitp.list`: the tab whose expanded project
folder contains the current directory, choosing the deepest match. An inherited
`TUIOS_SESSION` only breaks ties between matching projects; it cannot select a
different checkout's title. If the layout has no unique match, the current
folder name is used. Add a `YYYYMMDD` date as for `tth`, or `--title <text>` to
name the block yourself. The request itself, the last turn, is left out of the copy.

In Claude Code the skill runs the copy while it loads, so the agent only
repeats the one result line, with no command of its own. A new or cleared chat
has nothing before the request: the copy then fails with `Nothing to copy` and
leaves the clipboard alone.

### Also append the copy to a mission journal

Set `JOURNAL_MISSION` in the agent's environment to an existing absolute
folder named `YYYYMM-NAME`, for example `C:\notes\202401-Project-A`.
The Codex instruction checks the Windows user setting before its first
invocation when the process has no entry. An existing process entry wins,
including an invalid one. Direct CLI calls and Claude's automatic invocation
still need the setting in their process environment; restart those hosts if
they have not inherited it.
Then invoke `copy-conversation` as usual. It also appends the copied block
and a `~~~~~~~~~~~~~~~~` separator line to
`<JOURNAL_MISSION>\YYYYMM\project-aYYYYMMDD.txt`.

The prefix comes from the folder name after `YYYYMM-`, always lowercase.
Before 06:00 local time, the journal day is yesterday; at 06:00 it becomes
today. Both the month subfolder and filename follow that day. The mission
root stays as configured, and a supplied trimming date does not change the
journal day. The command creates the month subfolder and file as needed.
Only a newly created file starts with its journal date in French, for example
`Mardi 17 novembre 2026`, an underline of `=` characters of the same length,
then a blank line. The heading uses the filename's journal day. Existing
files, including empty ones, receive only the new conversation entry.

Use UTF-8 for existing journal files. Each append holds exclusive access to
the daily file on Windows (a cooperative lock on POSIX), then flushes and
closes it. The result names the destination. If it reports that the clipboard
is ready but the append failed, inspect that destination before retrying.
Remove `JOURNAL_MISSION` from both the process and Windows user settings to
return to clipboard-only copying through the Codex instruction. The underlying
CLI's `--no-clipboard` also skips journaling. This option does not change `tth`.

## Force the export format

The format is detected from the markers in the text: the Claude prompt, answer,
reflection, and recap prefixes against the Codex `## User`, `## Assistant`,
`## Activity`, and `## Reasoning` headings. Override the detection when a
transcript mixes both, for instance a Codex export that quotes a Claude
session:

```text
tth docs\session-export.md --format codex
```

## What survives the trim

Each turn keeps three regions, and everything else is dropped. In a Claude
export:

- the ask: the prompt line and its continuation, blank lines included, up to
  the first answer marker;
- the opening: the run of non-blank lines under that first answer marker, what
  the turn said before it started working;
- the answer: the last answer block of the turn, plus the reflection line that
  closes it and the recap line under that.

Tool calls never survive: a block holding `⎿` tool output goes whole, and the
`⎿` output left under a prompt, such as hook output, goes too, each replaced by
one blank line.

A Codex export keeps the same three regions, read from its headings: the
`## User` section, the first `## Assistant` section, and the last
`## Assistant` section of the turn. `## Activity` and `## Reasoning` are
dropped, including those written under a message you sent while the turn was
still working.

The reflection line itself is kept on purpose. It marks where reasoning was
removed, so a reader can see that something was elided instead of wondering
whether the answer arrived out of nowhere.

## What to check when the result looks wrong

- **Nothing was removed.** The export may already be trimmed, or it may hold
  one answer block per turn, in which case there is nothing between the opening
  and the answer to drop. Both are correct outcomes.
- **A turn is missing entirely.** Every kept region belongs to a turn, and a
  turn opens on a prompt line or a `## User` heading. Text before the first one
  is banner noise and never survives.
- **The command refuses to run.** An unrecognized export, an empty source, or a
  trim that would keep nothing all stop with an error on exit code 2, and the
  clipboard is left as it was rather than emptied.

Related: [Why a trimmed export keeps three regions](../explanation/why-a-trimmed-export-keeps-three-regions.md),
[the trim-thinking command reference](../reference/trim-thinking-command.md),
and [Aliases and bin launchers](../reference/aliases-and-launchers.md).
