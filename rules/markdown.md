# Markdown writing rules

When writing any markdown file, always use different section titles, using the context to make them unique.
For instance, do not use as a section title "Goal", use instead "Goal for xxx" if xxx is the topic of your writing.
Each section title must be unique, not a repetition of a previous section title already used.

When writing a list element (`- xxx`), always use only one space between the list item dash marker (`-`) and its content (`xxx`): so use `- xxx`, not `-  xxx` or `-   xxx`: do not use 2 or 3 spaces, only one.

When writing an ordered list element (`1. xxx`), always use only one space between the list item number marker (`1.`) and its content (`xxx`): so use `1. xxx` or `1. **xxx**`, not `1.   xxx` or `1.   **xxx**` or `1.  xxx` or `1.  **xxx**`: do not use 2 or 3 spaces, only one.

That will avoid the markdown linter warning "`MD030/list-marker-space: Spaces after list markers [Expected: 1; Actual: 3]`"

Make sure to insert an empty line before the first item of a list (ordered or not-ordered), and after the last item of a list.

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
