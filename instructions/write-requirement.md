# Write requirement document (feature-request or issue)

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

## Requirement document templates

Use the matching template in [`write-requirement.template.md`](../templates/write-requirement.template.md) as the starting shape for the generated markdown file. That template file contains two sections:

- a feature-request template, to use when the CDC adds or changes a requested behavior with options and a recommended direction.
- an issue template, to use when the current behavior, the target rule, and the implementation-facing decisions are already concrete enough to describe the gap as an issue to fix.

Replace every placeholder with topic-specific content and keep section titles specific to the topic instead of reusing generic headings.

Do not include open questions yet: they will be added later by a separate skill (the `review-ask-questions` skill — see [`review-ask-questions.md`](review-ask-questions.md)), in a separate step, in that same document, after the requirement is written.

## Handoff

When the `feature-request.vX.Y.Z.<slug>.md` or `issue.vX.Y.Z.<slug>.md` is written, hand the cycle on to its review, with no menu and no go-ahead. From the project root, in a PowerShell shell, run `pw skill` through its launcher (see [`run-pw.md`](run-pw.md) for the non-interactive invocation; the bare `pw` alias does not resolve in a tool shell):

- `pw skill`

`pw skill` prints one bare next-step command, derived from the documents on disk — here `/review-ask-questions on docs/feature-request.vX.Y.Z.<slug>.md` (a `/` prefix in a Claude session, a `$` prefix in a Codex session). Read that line and run it straight away: a handoff is the go-ahead to perform the next step now, so do not stop to ask whether to proceed, and do not compose the next prompt yourself.

To hold the chain here instead — to read the requirement before the review runs — pass the literal phrase `stop here` in this skill's argument when you invoke it. With `stop here` in the argument, write the requirement and skip this handoff.
