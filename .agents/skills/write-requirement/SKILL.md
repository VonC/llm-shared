---
name: write-requirement
description: 'Write a feature-request or an issue document (common term for "feature-request" and "issue" is here "requirement") in markdown from a user story, a bug report, or a feature request expressed in the prompt and associated documents in your context. Before writing, confirm that the required inputs are valid. After validation, write the file as `docs\<type>.vX.Y.Z.<topic>.md`. The document must include the user story or bug summary, the expected behavior or gap, and acceptance criteria or confirmed rules. Add concrete examples, code references, and technical constraints only when they are directly mentioned in the user input or in associated documents.'
user-invocable: true
metadata:
  - "This skill writes a requirement document from the prompt and associated documents in your context."
  - "The argument hint for this skill is 'Provide all three inputs: the type (feature-request or issue), the product version as vX.Y.Z, and a topic label for the specific feature or area of concern using only lowercase letters, digits, and hyphens, for example "issue v9.3.0 sentinels".'."
argument-hint: 'Provide all three inputs: the type (feature-request or issue), the product version as vX.Y.Z, and a topic label for the specific feature or area of concern using only lowercase letters, digits, and hyphens, for example "issue v9.3.0 sentinels".'
---

[Instruction](../../../instructions/write-requirement.md)
