# Trim an exported conversation

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Turn a raw Claude Code or OpenAI Codex export into something a human can
read: keep what was asked and what was answered, drop the reasoning and the
tool traffic in between. The trimmed text goes back to the clipboard, ready to
paste into a report, an issue, or a document.

## Invocation model

This is a human-run command. Export a session, run `tth`, paste the result.
The AI may run it when explicitly asked to shorten a transcript it was handed,
but no skill calls it as a hidden step, so direct invocation is the normal
path.

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

## Force the export format

The format is detected from the markers in the text: the Claude prompt, answer,
reflection, and recap prefixes against the Codex `## User`, `## Assistant`, and
`## Activity` headings. Override the detection when a transcript mixes both,
for instance a Codex export that quotes a Claude session:

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

A Codex export keeps the same three regions, read from its headings: the
`## User` section, the first `## Assistant` section, and the last
`## Assistant` section of the turn. `## Activity` is dropped.

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
