---
name: process-draft
description: 'Read a draft named in the prompt, run a light first-pass that classifies it as a feature-request, an issue, or a collection of both, and record that type in the draft. Propose three witty titles and three slugs, pick a target version derived from version.txt (current, or a major, minor, or patch step), rename the draft to draft.vX.Y.Z.<slug>.md, then create the effort branch in a new sibling worktree or in the current tree (git switch -C slug). Hand off to write-requirement for a single topic, or split-and-define when the draft holds more than one topic.'
user-invocable: true
argument-hint: 'Name the draft document to process, for example "process-draft docs/draft.duration_outliers.md".'
---

[Instruction](../../../instructions/process-draft.md)
