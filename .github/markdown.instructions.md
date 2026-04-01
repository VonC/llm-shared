---
applyTo: "**/*.md"
---

When writing any markdown file, always use different section titles, using the context to make them unique.
For instance, do not use as a section title "Goal", use instead "Goal for xxx" if xxx is the topic of your writing.
Each section title must be unique, not a repetition of a previous section title already used.

When writing a list element (`- xxx`), always use only one space between the list item dash marker (`-`) and its content (`xxx`): so use `- xxx`, not `-  xxx` or `-   xxx`: do not use 2 or 3 spaces, only one.

When writing an ordered list element (`1. xxx`), always use only one space between the list item number marker (`1.`) and its content (`xxx`): so use `1. xxx` or `1. **xxx**`, not `1.   xxx` or `1.   **xxx**` or `1.  xxx` or `1.  **xxx**`: do not use 2 or 3 spaces, only one.

That will avoid the markdown linter warning "`MD030/list-marker-space: Spaces after list markers [Expected: 1; Actual: 3]`"

Make sure to insert an empty line before the first item of a list (ordered or not-ordered), and after the last item of a list.

Do not use 3 or 4 spaces for sub-list before the list item, always 2 spaces more than the parent item list.

Do not use in comments/docstring `'`, always `'`
