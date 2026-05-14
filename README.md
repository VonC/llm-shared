# copilot-shared

A shared collection of GitHub Copilot prompts, skills, and instructions.

> **Work in progress.** These are drafts. Content is being extracted from
> project-specific repositories and generalized for reuse across projects.
> Expect rough edges, missing pieces, and instructions that still reference
> their origin project.

---

## Goal: avoid vibe-coding

The point of this workflow is to keep the creative expression of an idea
while refusing to short-circuit it into code. Vibe-coding — "I got an
idea, here it is, now generate me some code for it, I'll figure out the
details later" — is what these skills are built to prevent.

Each skill draws a clear line between phases:

- **Define and refine** what is actually needed, in plain text first
  (`/split-and-define`, `/write-requirement`, `/review-ask-questions`,
  `/consolidate-then-review-ask-questions`).
- **Design** a solution with explicit acceptance scenarios
  (`/write-design` and the same review loop).
- **Plan** the implementation as a numbered list of steps. The first
  step adds gate tests that fail on purpose; the following steps make
  those tests pass one by one. The last step adds the acceptance tests
  that close the loop on the original requirement
  (`/write-plans`, `/implement-step`, `/implementation-check`).

See [DEVELOPMENT.md — Goal: avoid vibe-coding](DEVELOPMENT.md#goal-avoid-vibe-coding)
for the full rationale, what each phase costs up front, and the short
path when the draft is genuinely one self-contained requirement.

A side benefit: the workflow leaves a written trail. Each phase produces
artifacts — the draft, the requirement, the design with its acceptance
scenarios, the plan and validation plan, the per-step grouped commits —
and each merge keeps a conventional commit message that ties them
together. That trail is read later by humans returning to old code, and
it is also the context an LLM needs when asked to extend, debug, or
explain that code in a future session. The history carries not just the
code, but the reasoning that produced it.

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

## Development workflow overview

The skills in this repository fit a single end-to-end workflow that takes a
raw idea from a draft note all the way to a tagged release. The diagram below
shows the main phases and which skill triggers each transition. See
[DEVELOPMENT.md](DEVELOPMENT.md) for per-phase details and helper diagrams.

```txt
                  +-----------------+
                  |   draft (EdB)   |
                  +--------+--------+
                           |
              +------------+------------+
              |                         |
       single requirement?       multiple items?
       /write-requirement        /split-and-define
       (skip the split)                  |
              |                          v
              |                  +-----------------+
              |                  | requirement     |
              |                  | items list      |
              |                  +--------+--------+
              |                           |
              |                  /write-requirement
              |                     (one per item)
              |                           |
              +------------+--------------+
                           v
                  +-----------------+
                  |                 |----+
                  | requirement doc |    |  /review-ask-questions
                  |                 |<---+  /consolidate-then-review-ask-questions
                  +--------+--------+       (loop while open questions remain)
                           |
                           |  /write-design
                           v
                  +-----------------+
                  |                 |----+
                  |   design doc    |    |  /review-ask-questions
                  |                 |<---+  /consolidate-then-review-ask-questions
                  +--------+--------+       (loop while open questions remain)
                           |
                           |  /write-plans
                           v
                  +-----------------+
                  |     plan +      |
                  | validation plan |
                  +--------+--------+
                           |
                           |  /implement-step N
                           |  /implementation-check N
                           v
                  +-----------------+
                  | step N          |----+
                  | committed       |    |  /group-commits-msg + gcba
                  |                 |<---+  (loop for next step)
                  +--------+--------+
                           |
                           |  last step done
                           |  git merge --no-ff <branch>
                           |  /update-merge-commit-msg
                           v
                  +-----------------+
                  |                 |----+
                  |  main updated   |    |  (loop for next requirement)
                  |                 |<---+
                  +--------+--------+
                           |
                           |  after several merges
                           |  /write-release-notes-summary
                           |  git tag vX.Y.Z
                           v
                  +-----------------+
                  |     release     |
                  +-----------------+
```

The `/split-and-define` phase is optional. When the draft already
describes a single, self-contained requirement, the author can call
`/write-requirement` directly and pass the type (`feature-request` or
`issue`), version, and topic — no split step is needed. Reach for
`/split-and-define` when the draft mixes several distinct items, when
the items differ in dependency order, or when the author wants the skill
to suggest a slug per item.

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
scripts/                                  shared helper scripts grouped by skill
└─ update-merge-commit-msg/
   ├─ git-extract-merge-docs.sh           dump the merged branch docs to a.docs
   └─ git-reword-merge.sh                 rewrite the current merge commit from a.commit
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
