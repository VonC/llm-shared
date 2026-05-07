---
name: write-requirement
description: 'Write a feature-request or an issue document (common term for "feature-request" and "issue" is here "requirement") in markdown from a user story, a bug report, or a feature request expressed in the prompt and associated documents in your context. Before writing, confirm that the required inputs are valid. After validation, write the file as `docs\<type>.vX.Y.Z.<topic>.md`. The document must include the user story or bug summary, the expected behavior or gap, and acceptance criteria or confirmed rules. Add concrete examples, code references, and technical constraints only when they are directly mentioned in the user input or in associated documents.'
user-invocable: true
metadata:
  - "This skill writes a requirement document from the prompt and associated documents in your context."
  - "The argument hint for this skill is 'Provide all three inputs: the type (feature-request or issue), the product version as vX.Y.Z, and a topic label for the specific feature or area of concern using only lowercase letters, digits, and hyphens, for example "issue v9.3.0 sentinels".'."
argument-hint: 'Provide all three inputs: the type (feature-request or issue), the product version as vX.Y.Z, and a topic label for the specific feature or area of concern using only lowercase letters, digits, and hyphens, for example "issue v9.3.0 sentinels".'
---

1. Read the prompt and identify three mandatory inputs: the requirement type (`feature-request` or `issue`), the product version written as `vX.Y.Z`, and the topic label.
2. First, validate the type.
3. Accept the type only if it is exactly `feature-request` or `issue` and it aligns with the user's stated intent.
4. If the type is missing, invalid, or irrelevant to the request, ask the user for a corrected type and stop.
5. Next, validate the version.
6. Accept the version only if it is explicitly provided in the user's input in `vX.Y.Z` form.
7. Do not infer the version from associated documents or other context.
8. If the version is missing or not in `vX.Y.Z` form, ask the user for a corrected version and stop.
9. If the version format is valid but the version appears inconsistent with the prompt or associated documents, ask the user to confirm or correct the version and stop.
10. Last, validate the topic label.
11. Accept the topic label only if it identifies the specific feature or area of concern and uses only lowercase letters, digits, and hyphens.
12. If the topic label is missing, irrelevant to the request, or contains other characters, ask the user for a corrected topic label and stop.
13. When asking for a correction, keep any earlier fields that were already confirmed as valid and ask only for the current field.
14. If the user does not answer the clarification request, or answers again with an invalid value, stop and explain which field still needs a valid value.
15. If associated documents are missing, invalid, or not useful for the requested requirement, notify the user and ask for additional context before writing the document body.
16. After validation succeeds, write the file as `docs\<type>.vX.Y.Z.<topic>.md` in markdown format.
17. Fill the document body from the user story, bug report, feature request, and associated documents in your context. Use only the user-provided version that you confirmed as valid for the file name and version references.
18. Include these core items in the document: the user story or bug summary, the current behavior, the expected behavior or gap, and acceptance criteria or confirmed rules.
19. Add concrete examples, code references, and technical constraints only when they are directly mentioned in the user input or in associated documents.

## Markdown plan templates for requirement documents

Use the matching template below as the starting shape for the generated markdown file.
Replace every placeholder with topic-specific content and keep section titles specific to the topic instead of reusing generic headings.

### Feature-request template for `<topic>`

Use this template when the CDC adds or changes a requested behavior and the document still needs open questions with options and a recommended direction.

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

### Issue template for `<topic>`

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
