# Markdown plan templates for requirement documents

Use the matching template below as the starting shape for the generated markdown file.
Replace every placeholder with topic-specific content and keep section titles specific to the topic instead of reusing generic headings.

## Feature-request template for `<topic>`

Use this template when the CDC adds or changes a requested behavior with options and a recommended direction.

Do not include open questions yet: they will be added later by a separate skill, in a separate step, in that same document, after the requirement is written. The open questions will be based on the content of the requirement, but they will be written independently from the requirement writing step, and they will be added in a separate section at the end of the document. This separation allows to keep the requirement document focused on describing the requested behavior and its rationale, while still providing a clear and structured way to capture any open questions that may arise during the requirement writing process or later during the implementation process.

```md
# <Short title for <topic>>

## CDC revision that introduces <topic>

Describe the earlier CDC state, then quote or summarize the revision that adds the requested behavior.

## Current behavior in vX.Y.Z

- <Current behavior point 1>
- <Current behavior point 2>
- <Current behavior point 3>

## Gap to close in the implementation for <topic>

1. <Requested change 1>
2. <Requested change 2>
3. <Requested change 3>

## Code references for <topic>

- `<path/to/file.ext>`: <Current responsibility>
- `<path/to/other_file.ext>`: <Current responsibility>
```

## Issue template for `<topic>`

Use this template when the current behavior, the target rule, and the implementation-facing decisions are already concrete enough to describe the gap as an issue to fix.

```md
# <Short title for <topic>>

## CDC revision history for <topic>

- <Earlier CDC behavior>
- <Newer CDC behavior>

## Current behavior in vX.Y.Z

1. <Current step 1>
2. <Current step 2>
3. <Current step 3>

## Current side effects in vX.Y.Z for <topic>

- <Current naming, storage, state, or logging side effect>
- <Current fallback or rejection side effect>

## CDC wording and gap analysis for <topic>

Explain how the CDC wording differs from the current behavior and list the concrete gaps.

## Confirmed rule for `<topic>`

- <Accepted rule 1>
- <Accepted rule 2>
- <Accepted rule 3>

## Gap to close in the implementation for `<topic>`

1. <Implementation change 1>
2. <Implementation change 2>
3. <Implementation change 3>

## Concrete examples for `<topic>`

- `<Example input>` -> <Expected result>
- `<Example input>` -> <Expected result>

## Code references for `<topic>`

- `<path/to/file.ext>`: <Current responsibility>
- `<path/to/other_file.ext>`: <Current responsibility>
```
