# copilot-shared

A shared collection of GitHub Copilot prompts, skills, and instructions.

> **Work in progress.** These are drafts. Content is being extracted from
> project-specific repositories and generalized for reuse across projects.
> Expect rough edges, missing pieces, and instructions that still reference
> their origin project.

---

## Main focus: commit message prompts and skills

The central goal of this repository is to nail down a reliable, reusable
workflow for writing good conventional commit messages and grouping staged
changes into coherent commits. The two key files are:

- `.github/prompts/write-commit-message.prompt.md` — write a single commit
  message from a diff in context.
- `.github/skills/group-commits-msg/SKILL.md` — group staged files by topic
  and produce one commit message per group, saved to `a.commit`.

These two work together: the skill invokes the same commit message conventions
defined in the prompt.

---

## Contents

```
.github/
├─ blacklist.md                          instruction: words to avoid in all responses
├─ markdown.instructions.md              instruction: markdown formatting rules
├─ preserve_code.md                      instruction: never truncate code when rewriting
├─ prompts/
│  ├─ write-commit-message.prompt.md     write a conventional commit from a diff
│  ├─ write-doc-commit-message.prompt.md write a docs: commit from a markdown document
│  ├─ write-release-notes-summary.prompt.md  summarize a release from commit subjects
│  └─ write-plan.prompt.md               write a numbered implementation plan
└─ skills/
   └─ group-commits-msg/
      ├─ SKILL.md                        group staged files and write one commit each
      └─ TEMPLATE.md                     template for the a.commit file format
```

---

## How to use this repository

Add it as a folder in a VS Code multi-root workspace alongside the project you
are working on:

```json
{
  "folders": [
    { "path": "C:/Users/vonc/prog/git/copilot-trackers/copilot-shared" },
    { "path": "C:/Users/vonc/prog/git/copilot-trackers/copilot-pacer" }
  ]
}
```

VS Code will discover the prompts under `.github/prompts/` and the skills
under `.github/skills/` from all workspace folders.

---

## Status of each file

| File | Status | Notes |
| ---- | ---- | ---- |
| `blacklist.md` | draft | Generic. Ready to use. |
| `markdown.instructions.md` | draft | Generic. Ready to use. |
| `preserve_code.md` | draft | Generic. Ready to use. |
| `write-commit-message.prompt.md` | draft | Main focus. Usable. |
| `write-doc-commit-message.prompt.md` | draft | Usable. |
| `write-release-notes-summary.prompt.md` | draft | Usable. |
| `write-plan.prompt.md` | draft | Generalized from Python project. May need tuning per project type. |
| `group-commits-msg` skill | draft | Main focus. Validation step is project-specific — see SKILL.md notes. |
