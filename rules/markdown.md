# Markdown writing rules

When writing any markdown file, always use different section titles, using the context to make them unique.
For instance, do not use as a section title "Goal", use instead "Goal for xxx" if xxx is the topic of your writing.
Each section title must be unique, not a repetition of a previous section title already used.

Make sure to insert an empty line before every heading and an empty line after every heading.
The first level-one document title is the only exception: because it starts the file, it needs only the empty line after it.
This prevents `MD022/blanks-around-headings` warnings and applies whenever an existing Markdown document is edited, not only when a new document is created.

Never leave trailing whitespace at the end of a line. The one exception is the Markdown hard line break, which is exactly two trailing spaces; one space, three spaces, or a trailing tab are all warnings.

That avoids "`MD009/no-trailing-spaces: Trailing spaces [Expected: 0 or 2; Actual: 1]`". It usually arrives with pasted text, so strip the ends of every line you paste in from a terminal, a web page or an issue tracker. When a hard line break is genuinely wanted, prefer ending the sentence and starting a new paragraph, because two invisible spaces are a fragile way to say it.

Never write a bare URL in prose: wrap it as an autolink in angle brackets, `<https://example.com>`, or give it a label, `[the page](https://example.com)`.

That avoids "`MD034/no-bare-urls: Bare URL used`". A URL inside backticks, a fenced block, or an indented block is code rather than a link and needs no wrapping. A prefix does not exempt it either: `view-source:https://example.com` is still a bare URL, and the whole thing wraps as one autolink, `<view-source:https://example.com>`.

Always give a fenced code block a language on its opening fence. When the content is not a language, output, a transcript, a diagnostic, a directory listing, use `text`.

That avoids "`MD040/fenced-code-language: Fenced code blocks should have a language specified`". Only the opening fence carries the language; the closing fence stays bare.

Never leave two or more consecutive blank lines anywhere in a markdown file: exactly one blank line separates any two blocks, whatever they are (a paragraph and a heading, a table and the sentence after it, two sections).

That avoids the markdown linter warning "`MD012/no-multiple-blanks: Multiple consecutive blank lines [Expected: 1; Actual: 2]`", which the `markdown-check` catalog enforces as a mandatory rule: no repository policy can switch it off and no baseline can allow it, so the only repair is fixing the file.

This one is rarely typed on purpose: it appears when a document is assembled from parts, when a section is appended to a file that already ends with a newline, or when a block is deleted and its surrounding blank lines are both kept. So check it after any concatenation, append or removal, not only after writing prose. Blank lines inside a fenced code block are exempt, because the fence content is data.

When writing a list element (`- xxx`), always use only one space between the list item dash marker (`-`) and its content (`xxx`): so use `- xxx`, not `-  xxx` or `-   xxx`: do not use 2 or 3 spaces, only one.

When writing an ordered list element (`1. xxx`), always use only one space between the list item number marker (`1.`) and its content (`xxx`): so use `1. xxx` or `1. **xxx**`, not `1.   xxx` or `1.   **xxx**` or `1.  xxx` or `1.  **xxx**`: do not use 2 or 3 spaces, only one.

Add a list marker only at the start of a new list item. If the item already starts
with a dash or ordered-list marker (for example, `- item` or `1. item`), do not
prepend another dash marker. A wrapped line is part of the same item: indent
it under the item's text
without adding a new marker. For example:

```md
1. The first finding continues onto
   this line.
2. The second finding.

- One changed file has a long explanation
  that continues here.
```

Never turn those examples into `- 1. ...`, `- - ...`, or `- this line.`.

That will avoid the markdown linter warning "`MD030/list-marker-space: Spaces after list markers [Expected: 1; Actual: 3]`"

Surround every bulleted or numbered list with one empty line: put an empty line
before its first item and another after its last item when other content follows.
This applies after any preceding paragraph or label (including one ending in a
colon) and before any following paragraph, heading, or separate list. A list at
the start or end of a document needs a blank line only on the side with content.

For example:

```md
Group 1:

- First path
- Second path

Group 2:

1. First item
2. Second item

### Next section
```

That avoids "`MD032/blanks-around-lists: Lists should be surrounded by blank lines`".
The usual slip is a generated report or review answer where a sentence such as
`The commands agree:` is followed on the very next line by `- first command`:
insert the empty line between them.

Do not use 3 or 4 spaces for sub-list before the list item, always 2 spaces more than the parent item list.

Do not use in comments/docstring `'`, always `'`

## Code-like names and bold text

Wrap every file name, path, identifier, option or command fragment that
contains `_` or `*` in backticks, in prose, list items, table cells and
headings alike: `__init__.py`, `src/pkg/__init__.py`, `_load_state`,
`store_reader.py`, `--max_items`. Markdown otherwise reads those characters as
emphasis markers, and the resulting warnings surface far from their cause:

- "`MD037/no-space-in-emphasis: Spaces inside emphasis markers`": two bare
  names such as `_load_state` and `_save_state` on one line open and close an
  emphasis whose text starts or ends with a space.
- "`MD050/strong-style: Strong style [Expected: underscore; Actual: asterisk]`":
  a bare `__init__` is read as bold text written with underscores. The
  default `consistent` style takes the first bold marker of the document as
  its norm, so that hidden underscore turns every later `**bold**` into a
  warning, even thousands of lines away.

Write bold text with `**`, never with `__`, and never use `_` or `*` for
emphasis around a code-like name. `**` is the bold style of every document, so
an MD050 warning reading `Expected: underscore; Actual: asterisk` is never
fixed by switching the bold to `__`. It means a bare Python-style name, such as
`__init__.py`, `__main__` or `__name__`, sits earlier in the document and set
the underscore style. Search the document for it (`rg -n "__[A-Za-z]" <file>`
lists the candidates), wrap it in backticks, and lint again until the warning
is gone.

Before appending to a document that several authors or tools write, such as a
review transcript, read its earlier lines the same way. When the bare name sits
in generated or protocol content you must not edit, keep `**` in your own lines
and report the remaining warning at the commit gate instead of hiding it.

## Validate a Markdown document with markdownlint

After writing or editing a Markdown document, validate it with `markdownlint-cli2`. Node.js does not need to be on the `PATH` beforehand: the Node versions installed under `%PRGS%\nodes` are available, and the `switchnode` senv utility puts the chosen one first in the `PATH` for that shell. From the project root, so the repository's `.markdownlint.json` applies:

```bat
cmd /c "switchnode 22 && npx --yes markdownlint-cli2 my_markdown_document_to_validate.md"
```

Several files or a glob can follow the command name. Exit code `0` with `Summary: 0 issues` means the document is clean; any other result lists each finding as `path:line rule/name description`, to fix in the file. Run the call from PowerShell or `cmd.exe`, never from Git Bash, which rewrites `/c` into a path and runs nothing.

## Lint every new or modified Markdown file before asking to commit

Before presenting any choice that commits (the go-ahead menu of a grouped
commit plan, a review convergence gate, or any other confirmation that leads
to a commit), lint every Markdown file the commit would add or modify with the
command above, and fix every finding first. Include the modified Markdown
files that the same workflow commits later, such as a review transcript kept
unstaged for a residual commit: the person approving the commit approves those
too. List them with `git status --porcelain -- "*.md"` rather than from memory.
Then spell-check the same Markdown files as [`spelling.md`](spelling.md)
requires.

Fixing a finding is part of preparing the commit, not a later cleanup: restage
the fixed files, refresh the commit plan if its membership changed, and only
then ask. Never present the commit choice while a finding remains, and never
disable a rule or add an exception comment to make a file pass. In a document
that several authors or tools append to, fix only the lines this work added,
following the earlier section on code-like names and bold text. The only
finding that may remain is one in a line this work must not edit, such as
generated or protocol content: name it, with its file and line, in the commit
question itself.

## No em dash

Never use the em dash (`—`) in documentation text: nobody but LLMs is using it.
Replace it with whichever fits the sentence best: a `:`, a parenthesis `(...)`, or a `,`. As a last resort, use a `;`.
The only acceptable use of `—` is when the programming language or the application being coded requires that exact character (for example a test fixture or an escape sequence), never in prose.

## Compact tables

When writing a markdown table, always use compact mode as defined in [`md060`](https://github.com/DavidAnson/markdownlint/blob/v0.40.0/doc/md060.md): avoid any extra padding inside cells, use a single space around cell content, and use exactly three `-` characters in each header separator column (`| --- |`), not longer dash runs such as `| ---- |` or `| -------- |`.

Compact form to follow:

```md
| Column A | Column B |
| --- | --- |
| value 1 | value 2 |
| value 3 | value 4 |
```

Forms to avoid:

```md
|  Column A  |  Column B  |
| ---------- | ---------- |
|  value 1   |  value 2   |
```

```md
| Column A | Column B |
| -------- | -------- |
| value 1  | value 2  |
```

## Mermaid diagrams that Codex can draw

Codex draws a fenced `mermaid` block in its terminal with its own small
renderer, [`codex-rs/mermaid`](https://github.com/openai/codex/tree/main/codex-rs/mermaid),
whose limits are fixed in its code (Codex 0.167.0): no setting raises them.
Past a limit, Codex shows the diagram's source under one of these notices,
not a drawing:

- "This Mermaid diagram exceeds the terminal renderer's size limits."
- "This Mermaid diagram uses features the terminal renderer doesn't support."
- "This Mermaid diagram doesn't fit the current terminal width."

A document can end up in a Codex terminal as well as an answer, so write every
Mermaid diagram as a `flowchart` within these limits:

- Each line of a node label holds at most 40 columns. Split a longer label
  with `<br>` inside its double quotes, each part counting on its own:
  `A["Consumer senv:<br>own Python + selected checks"]`, not
  `A["Consumer senv: own Python + selected checks"]` (43 columns).
- An edge label is one line of at most 40 columns, without `<br>`:
  `A -->|reads| B` or `A -- reads --> B`. Keep it to a word or two: its width
  widens the whole diagram.
- At most 16 nodes and 24 edges. `A & B --> C & D` counts as four edges.
- Use only the node shapes `A["text"]`, `A{"text"}` and `A(["text"])`, and
  the links `-->`, `---`, `-.->`, `-.-`, `<-->` and `<-.->`. Other shapes,
  such as `A[(text)]` or `A[[text]]`, and links such as `==>`, `--o` or `--x`
  are refused.
- No `subgraph`, `style`, `classDef`, `class`, `linkStyle`, `click` or
  `%%{init: ...}%%` line, no Markdown string (``A["`text`"]``), no HTML tag
  other than `<br>`, and no entity such as `#quot;` or `&amp;`. Write a label
  holding punctuation between double quotes, and never put a `"` inside it.
- Prefer `flowchart TD`. The renderer draws every node in one column, in the
  order the nodes first appear, with each edge in its own lane beside them.
  The width is the longest node label line plus 4, plus the longest edge
  label plus 5, plus 2 per edge, minus 1: keep it under 80 columns.
  `flowchart LR` puts every node on one row, as wide as all the boxes
  together, and soon no longer fits.
- Two flows that no edge connects make two diagrams, each one shorter.

Count the widest label line, the nodes and the edges before writing the
diagram. For example, 12 nodes, 11 edges, no edge label and a widest line of
38 columns give a diagram 68 columns wide (38 + 4 + 0 + 5 + 22 - 1).
