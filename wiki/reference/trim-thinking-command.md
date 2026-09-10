# Trim-thinking command

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Exact interface and trimming contract of `tools/trim_thinking.py` and its
command line `tools/trim_thinking_cli.py`, which reduce an exported LLM
conversation to what was asked and what was answered.

## Invocation model

Normally run directly by a human after exporting a session, or by the AI when
it is explicitly asked to shorten a transcript. No skill and no workflow phase
calls it implicitly.

## Entry points

| Entry point | Meaning |
| --- | --- |
| `tth` | Interactive Doskey alias loaded by `senv.bat` |
| `bin\tth.bat` | Self-locating launcher; preferred from scripts and agents |
| `tools\trim_thinking_cli.py` | Python entry point; use for development, not from consuming projects |
| `tools\trim_thinking.py` | Parsing only, importable with no clipboard dependency |

## Arguments

| Argument | Meaning |
| --- | --- |
| `source` | Export file to trim. Omitted, the clipboard is the source |
| `date` | Extra `YYYYMMDD` date for the dated-prompt pass. A lone eight-digit argument is read as this date, so `tth 20260903` still trims the clipboard |
| `--date YYYYMMDD` | The same date, spelled out. Use it when the value could be mistaken for a file name |
| `--format {auto,claude,codex}` | Export format. `auto` detects it from the markers, and is the default |
| `--debug` | Raise the log level to `DEBUG` |

## Claude markers

Every prefix below is the character followed by one space, and a line matches
only when it starts with both.

| Marker | Code point | Opens |
| --- | --- | --- |
| `❯` | U+276F | The prompt line of a turn |
| `●` | U+25CF | An answer or tool block |
| `⏺` | U+23FA | The same, in other Claude Code versions |
| `✻` | U+273B | The reflection line closing a turn |
| `※` | U+203B | The recap line under a reflection line, matched indented or not |

## Codex headings

| Heading | Meaning |
| --- | --- |
| `## User` | Opens a turn |
| `## Assistant` | Opens a step or the answer of that turn |
| `## Activity` | Tool activity, always dropped |

Heading names are matched case-insensitively, and a deeper heading such as
`### Files` is body text, not a section boundary.

## Kept regions

Each turn keeps three regions and drops the rest.

| Region | Claude | Codex |
| --- | --- | --- |
| Ask | Prompt line through the first answer marker, blank lines included | `## User` section up to the first `## Assistant` heading |
| Opening | Non-blank run under that first answer marker | That first `## Assistant` section, to the next heading |
| Answer | Last answer block of the turn, with the reflection line closing it and the recap line under that | Last `## Assistant` section of the turn |

Every answer block, or assistant section, between the opening and the last one
is treated as work rather than answer, and resets the answer region. A turn cut
short with no closing line still keeps its last block. Text before the first
prompt line, or the first `## User` heading, belongs to no turn and is dropped.

## Dated-prompt pass

Once the three regions are kept, one pass runs over the trimmed text. A line is
a dated prompt when it opens with an optional one-character marker and its
space, then a date, then a space, which is the shape a Claude prompt line takes
when the ask is stamped with a day:

```text
❯ 20260903 the ask this session opens with
```

Today is always one of the matched dates, so a bare `tth` still removes every
line before a prompt stamped with today. The `date` argument adds a second date
rather than replacing today. Dates are matched only in the eight-digit
`YYYYMMDD` rendering. The first recognized dated prompt becomes the first line
of the result. A dated prompt already on the first line changes nothing, and a
leading number that is not one of the requested dates leaves the transcript
unchanged.

The pass never removes the dated line itself, and the removed lines count
towards the summary line's total.

## Format detection

`auto` counts the Claude marker lines against the known Codex section headings
and picks the higher count, Codex winning a tie. A text carrying neither stops
with `UnknownTranscriptFormatError`, which names both marker families and
suggests `--format`.

## Output and exit codes

Standard output carries exactly one line:

```text
trim-thinking (<format>): <source> -> <kept> lines, <removed> reflection lines removed (<share>%). Ready to paste from clipboard.
```

| Exit code | Meaning |
| --- | --- |
| `0` | The clipboard holds the trimmed conversation |
| `2` | Missing file, empty source, unrecognized format, a trim that keeps nothing, or a clipboard failure |

On any error the clipboard is left untouched, so a failed run never destroys
the export it was given.

## Encoding contract

| Direction | Mechanism |
| --- | --- |
| File read | `utf-8-sig`, so a byte-order mark cannot hide the first prompt line |
| Clipboard read | PowerShell `Get-Clipboard -Raw` with `[Console]::OutputEncoding` set to UTF-8 |
| Clipboard write | PowerShell `Set-Clipboard` reading a UTF-8 temporary file |

The clipboard write goes through a file on purpose. PowerShell decodes a
redirected standard input with the console code page, which turns every marker
into mojibake, so the payload is handed over as UTF-8 on disk instead.

Related: [Trim an exported conversation](../how-to/trim-an-exported-conversation.md),
[Why a trimmed export keeps three regions](../explanation/why-a-trimmed-export-keeps-three-regions.md),
and [Aliases and bin launchers](aliases-and-launchers.md).
