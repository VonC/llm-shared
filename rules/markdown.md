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

That will avoid the markdown linter warning "`MD030/list-marker-space: Spaces after list markers [Expected: 1; Actual: 3]`"

Make sure to insert an empty line before the first item of a list (ordered or not-ordered), and after the last item of a list.

That avoids "`MD032/blanks-around-lists: Lists should be surrounded by blank lines`".

Do not use 3 or 4 spaces for sub-list before the list item, always 2 spaces more than the parent item list.

Do not use in comments/docstring `'`, always `'`

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
