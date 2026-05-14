# copilot-shared

A shared collection of GitHub Copilot prompts, skills, and instructions.

> **Work in progress.** These are drafts. Content is being extracted from
> project-specific repositories and generalized for reuse across projects.
> Expect rough edges, missing pieces, and instructions that still reference
> their origin project.

---

## Main focus: shared Copilot workflows

The first goal of this repository is still to pin down a reliable workflow for
writing good conventional commit messages and grouping staged changes into
coherent commits. It now also carries reusable prompts, skills, an agent, and
local helper scripts for analysis, implementation checks, refactors, and
`a.commit` replay.

- `.github/prompts/write-commit-message.prompt.md` — write a single commit
  message from a diff in context.
- `.github/skills/group-commits-msg/SKILL.md` — group staged files by topic
  and produce one commit message per group, saved to `a.commit`.
- `.github/skills/implement-step/SKILL.md` — implement one step from a design
  or plan document.
- `.github/skills/implementation-check/SKILL.md` — check whether a plan step
  is fully implemented.
- `tools/git_batch_commit.py` — validate and replay grouped commits from
  `a.commit`.

---

## Contents

```txt
.github/
├─ agents/
│  └─ split-large-file.agent.md         split a large file or class
├─ copilot-instructions.md               shared chat and code-writing rules (Copilot)
├─ prompts/
│  ├─ analyse.prompt.md                  guide read-only analysis
│  ├─ check-api*.prompt.md               review API dumps for architecture smells
│  ├─ continue-analyse.prompt.md         continue a prior analysis thread
│  ├─ discuss.prompt.md                  answer and challenge without code
│  ├─ extend-test-coverage.prompt.md     extend tests around selected code
│  ├─ fix-issue.prompt.md                fix a selected issue in context
│  ├─ lower-cyclomatic-complexity.prompt.md refactor complex code
│  ├─ rewrite-docstring.prompt.md        shorten docstrings without losing meaning
│  ├─ write-commit-message.prompt.md     write a conventional commit from a diff
│  ├─ write-doc-commit-message.prompt.md write a docs: commit from a markdown document
│  ├─ write-release-notes-summary.prompt.md summarize a release from commit subjects
│  └─ write-plan.prompt.md               write a numbered implementation plan
└─ skills/
   ├─ <skill>/SKILL.md                   frontmatter + reference to instructions/<skill>.md
   └─ ...                                same per-skill SKILL.md layout for every skill
.claude/
├─ CLAUDE.md                              shared chat and code-writing rules (Claude Code)
└─ skills/
   ├─ <skill>/SKILL.md                   frontmatter + reference to instructions/<skill>.md
   └─ ...                                mirrors .github/skills/ with one extra: write-release-notes-summary
instructions/                             shared skill bodies (one file per skill)
├─ consolidate-then-review-ask-questions.md
├─ group-commits-msg.md
├─ implement-step.md
├─ implementation-check.md
├─ review-and-update-project-docs.md
├─ review-ask-questions.md
├─ split-and-define.md
├─ split-large-file.md
├─ update-merge-commit-msg.md
├─ write-design.md
├─ write-plans.md
├─ write-release-notes-summary.md
└─ write-requirement.md
rules/                                    shared writing and code-style rules
├─ blacklist.md                           words to avoid in all responses
├─ markdown.md                            markdown formatting rules (lists, tables, titles)
└─ preserve_code.md                       never truncate code when rewriting
templates/                                shared markdown templates referenced by instructions/
├─ group-commits-msg.template.md          a.commit file format for grouped commits
├─ implementation-step-analysis.template.md output structure for implementation-check
├─ open-question.template.md              Qxx/BBQ/Options block for review skills
├─ write-design.template.md               design document skeleton
├─ write-plans.template.md                implementation plan skeleton
├─ write-plans.validation.template.md     validation plan skeleton
└─ write-requirement.template.md          feature-request and issue document skeletons
tools/
├─ git_batch_commit.py                    validate and replay grouped commits
└─ git_command.py                         local cross-platform Git helper
senv.bat                                  local shell aliases for the tooling
```

---

## How to use copilot-shared from another project

The intended setup is to reference this repository from an existing project's
workspace. Keep the real project as the first folder in the workspace and add
`copilot-shared` as the second folder. Do not make `copilot-shared` the main
workspace folder when the goal is to use its prompts inside another codebase.

In the existing project's `.code-workspace` file, the `folders` section should
look like this:

```json
{
  "folders": [
    {
      "path": ".."
    },
    {
      "path": "../../copilot-shared"
    }
  ]
}
```

With this layout, `..` points to the existing project and
`../../copilot-shared` points to the shared repository. VS Code will discover
the prompts under `.github/prompts/`, the skills under `.github/skills/`, and
the agent definitions under `.github/agents/` from both workspace folders.

The checked-in
[`.vscode/copilot-shared.code-workspace`](.vscode/copilot-shared.code-workspace)
file in this repository is only for working on `copilot-shared` itself. When
you want to use the shared prompts in another codebase, the other project's
workspace file should own the multi-root setup.

---

## Status of main areas

| Area | Status | Notes |
| ---- | ---- | ---- |
| Shared writing rules | draft | Includes blacklist, markdown rules, and full-file rewrite rules. |
| Commit message workflow | draft | Main focus, with `a.commit` planning and replay support. |
| Analysis and review prompts | draft | Covers API review, plan checks, discussions, and issue work. |
| Step-based skills and agent | draft | Includes step implementation, implementation checks, and file splitting. |
| Local helper scripts | draft | Includes `senv.bat`, `git_batch_commit.py`, and `git_command.py`. |
