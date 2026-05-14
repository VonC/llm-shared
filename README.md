# llm-shared

A shared development workflow that takes a draft note from "raw idea" to
"tagged release" without skipping the requirement, design, plan, and
acceptance-test phases. The repository ships the prompts, skills,
instructions, templates, and helper scripts that drive that workflow.

The skills are tested with GitHub Copilot in VS Code and with Claude Code
in both the VS Code extension and the CLI. They are designed to work with
any LLM that can read files in the workspace and write files back: every
slash command resolves to a plain markdown body in [`instructions/`](instructions/)
that another model can be handed directly as context.

> **Work in progress.** These are drafts. Content is being extracted from
> project-specific repositories and generalized for reuse across projects.
> Expect rough edges, missing pieces, and instructions that still reference
> their origin project.

---

## Goal: avoid vibe-coding

The point of this workflow is to keep the creative expression of an idea
while refusing to short-circuit it into code. Vibe-coding  --  "I got an
idea, here it is, now generate me some code for it, I will figure out the
details later"  --  is what these skills are built to prevent.

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

See [DEVELOPMENT.md  --  Goal: avoid vibe-coding](DEVELOPMENT.md#goal-avoid-vibe-coding)
for the full rationale, what each phase costs up front, and the short
path when the draft is genuinely one self-contained requirement.

A side benefit: the workflow leaves a written trail. Each phase produces
artifacts  --  the draft, the requirement, the design with its acceptance
scenarios, the plan and validation plan, the per-step grouped commits  --
and each merge keeps a conventional commit message that ties them
together. That trail is read later by humans returning to old code, and
it is also the context an LLM needs when asked to extend, debug, or
explain that code in a future session. The history carries not just the
code, but the reasoning that produced it.

### Key insight: Always make the LLM review its own work

- review to ask questions about your requirement or design;
- review to confirm (or infirm) the code generated does indeed match what was planned.

If your blindly trust what the LLM generates as a first pass (even in terms of documentation), you are missing out.

The review loop is where the LLM gets to challenge the inputs it was given and the outputs it produced, and to ask for clarifications or point out contradictions. It is also where you get to see if the LLM actually understands the requirement and design, or if it just generated something that superficially looks like it.

The "implementation check" phase is where the LLM gets to confirm that the code it just generated actually implements the plan and meets the acceptance criteria. If it does not, you get to iterate on the implementation until it does.

---

## At a glance: phases, skills, artifacts

One row per phase, in execution order. The "Trigger" column is what the
author types or runs; the "Output artifact" column is what lands on disk
after the trigger completes.

| Phase | Trigger | Output artifact |
| --- | --- | --- |
| Draft capture | Author writes free-form notes | `docs\draft.vX.Y.Z.<topic>.md` |
| Split (optional) | `/split-and-define` | `List of feature-requests and issues to create` section appended to the draft |
| Define each item | `/write-requirement <type> vX.Y.Z <topic>` | `docs\feature-request.vX.Y.Z.<topic>.md` or `docs\issue.vX.Y.Z.<topic>.md` |
| Review loop | `/review-ask-questions` then `/consolidate-then-review-ask-questions` | Open questions folded into a decision table; document approved |
| Design | `/write-design` | `docs\design.vX.Y.Z.<topic>.md` with acceptance scenarios |
| Plan | `/write-plans` | `docs\plan.vX.Y.Z.<topic>.md` + `docs\plan.vX.Y.Z.<topic>.validation.md` |
| Implement and check | `/implement-step N` then `/implementation-check N` | Code, tests, and updates to the validation document |
| Group commits | `gcmp` then `/group-commits-msg` then `gcba` | One conventional commit per logical group |
| Merge and reword | `git merge --no-ff` then `/update-merge-commit-msg` then `grmc` | Merge commit with a conventional message tied to the merged docs |
| Release | `/write-release-notes-summary` then `git tag` | Release notes + version tag on `main` |

---

## Conventional commits with a why/what body

Every commit in this workflow follows the
[Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
spec for the title line (`type(scope): subject`, 52 characters max).
That title is what tools read to generate changelogs and release
notes.

The spec stops at the title. The body is freeform. This repository
extends the spec with a fixed body template,
[`templates/group-commits-msg.template.md`](templates/group-commits-msg.template.md),
that adds two structured sections under the title:

- `Why:`  --  two short paragraphs separated by an empty line. The
  first paragraph states why the commit is needed (what was broken,
  missing, or unclear). The second paragraph states how the code is
  better after the commit lands.
- `What:`  --  a dash-prefixed list of the actual modifications, one
  line per change.

The reason for the extension: the title alone feeds a changelog
generator, but it does not help the next reader  --  human or LLM  --
understand *why* the code looks the way it does. The body template
fills that gap.

The matching skill, `/group-commits-msg`, automates the harder half.
By the time a developer is ready to commit, they often no longer
remember every change they made in the working tree, nor which
changes depend on which others. The skill reads the staged diff,
groups files from the least dependent group to the most dependent
one, and writes one commit message per group into `a.commit` for the
author to review and edit. `gcba` then replays `a.commit` as a
sequence of real commits.

See [DEVELOPMENT.md  --  Conventional commit message template](DEVELOPMENT.md#conventional-commit-message-template-why-and-what-beyond-changelog)
for the template fields in detail, the 52/80 character rules, and
the rationale behind the least-to-most-dependent grouping pass.

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

Each looping box in the diagram above has its own zoomed-in diagram in
[DEVELOPMENT.md](DEVELOPMENT.md), under the section named after the phase
(draft capture, requirement breakdown, review loop, design and planning,
grouped commit loop, step execution, and merge). Read the top-level
diagram for the route, then jump to the per-phase diagram for the
detail.

The `/split-and-define` phase is optional. When the draft already
describes a single, self-contained requirement, the author can call
`/write-requirement` directly and pass the type (`feature-request` or
`issue`), version, and topic  --  no split step is needed. Reach for
`/split-and-define` when the draft mixes several distinct items, when
the items differ in dependency order, or when the author wants the skill
to suggest a slug per item.

---

## Contents

### Agent entry points

Two folders, one per agent  --  same skills, same instruction bodies, two
discovery mechanisms. Pick the one your agent reads.

```txt
.github/                                  GitHub Copilot picks up prompts, skills, and agents from here
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
.claude/                                  Claude Code picks up project rules and skills from here
├─ CLAUDE.md                              shared chat and code-writing rules (Claude Code)
└─ skills/
   ├─ <skill>/SKILL.md                   frontmatter + reference to instructions/<skill>.md
   └─ ...                                mirrors .github/skills/ with one extra: write-release-notes-summary
```

### Shared bodies referenced by both agents

Both `.github/skills/<skill>/SKILL.md` and `.claude/skills/<skill>/SKILL.md`
delegate to the same markdown body under `instructions/`. A third LLM
that does not read either folder can still run the same skill by being
handed the matching `instructions/<skill>.md` file as part of its
context.

```txt
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

## How to use llm-shared from another project

The intended setup is to reference this repository from an existing
project's workspace or `~/.claude/` directory. The three subsections
below cover the three common entry points: VS Code (Copilot Chat or
Claude Code extension), Claude Code CLI, and any other LLM that reads
files in a workspace.

### From VS Code (Copilot Chat or Claude Code extension)

Keep the real project as the first folder in the workspace and add
`llm-shared` as the second folder. Do not make `llm-shared` the main
workspace folder when the goal is to use its prompts inside another
codebase.

In the existing project's `.code-workspace` file, the `folders` section
should look like this:

```json
{
  "folders": [
    {
      "path": ".."
    },
    {
      "path": "../../llm-shared"
    }
  ]
}
```

With this layout, `..` points to the existing project and
`../../llm-shared` points to the shared repository. Copilot Chat
discovers the prompts under `.github/prompts/`, the skills under
`.github/skills/`, and the agent definitions under `.github/agents/`
from both workspace folders. The Claude Code VS Code extension, opened
on the same multi-root workspace, picks up `.claude/skills/` from the
shared folder.

The checked-in
[`.vscode/llm-shared.code-workspace`](.vscode/llm-shared.code-workspace)
file in this repository is only for working on `llm-shared` itself.
When you want to use the shared prompts in another codebase, the other
project's workspace file should own the multi-root setup.

### From Claude Code (CLI)

Claude Code reads `.claude/` from the current working directory. To run
the shared skills inside a project that does not have its own
`.claude/` folder, point Claude at the shared one with `--add-dir`:

```bash
claude --add-dir=../llm-shared
```

Adjust the path so it points to where the repository sits on disk
(`..\llm-shared` from Windows `cmd.exe`, `../../llm-shared` from a
deeper subfolder, etc.).

To make the shared skills available in every project on the machine
without `--add-dir`, copy or symlink `.claude/skills/` into
`~/.claude/skills/`:

```bash
ln -s "$(pwd)/.claude/skills" ~/.claude/skills
```

After that, the same slash commands resolve in any directory.

### From another LLM (any model that reads files)

Every slash command resolves to a plain markdown body under
[`instructions/`](instructions/) (for example,
`instructions/write-design.md`). When an agent that does not understand
`.github/skills/` or `.claude/skills/` is used, hand it the matching
file in `instructions/` as context together with the inputs the body
expects (a draft, a requirement document, a plan, etc.). The slash
command name and the instruction file name are always the same.

---

## Status of main areas

| Area | Status | Tested with | Notes |
| --- | --- | --- | --- |
| Shared writing rules | draft | Copilot (VS Code), Claude Code (VS Code + CLI) | Includes blacklist, markdown rules, and full-file rewrite rules. |
| Commit message workflow | draft | Copilot (VS Code), Claude Code (VS Code + CLI) | Main focus, with `a.commit` planning and replay support. |
| Analysis and review prompts | draft | Copilot (VS Code), Claude Code (VS Code + CLI) | Covers API review, plan checks, discussions, and issue work. |
| Step-based skills and agent | draft | Copilot (VS Code), Claude Code (VS Code + CLI) | Includes step implementation, implementation checks, and file splitting. |
| Local helper scripts | draft | Windows (`cmd.exe` with Doskey) | Includes `senv.bat`, `git_batch_commit.py`, and `git_command.py`. |

---

## Glossary

Shorthand used across this README, [DEVELOPMENT.md](DEVELOPMENT.md), and
the shared skill bodies. The Doskey aliases are documented in detail in
[DEVELOPMENT.md  --  Local command reference for this workflow](DEVELOPMENT.md#local-command-reference-for-this-workflow).

| Term | Stands for |
| --- | --- |
| `a.commit` | Grouped-commit plan file, one block per logical group, replayed by `gcba`. |
| `a.diff` | Snapshot of the staged diff written by `gcmp` so the agent can justify the grouping. |
| `a.docs` | Dump of the merged branch documents, written by the merge-doc extraction script. |
| `c` | Doskey alias to `bin\python_check.bat`. |
| `covg` | Doskey alias that maps uncovered lines to functions and builds a clipboard prompt. |
| `gate test` | A failing test added before the implementation step that makes it pass. |
| `gcba` | Doskey alias to `git_batch_commit.py --root-a-commit`; validates and replays `a.commit`. |
| `gcmp` | Doskey alias to `group_commit_message_prompt.py`; writes `a.diff` and the clipboard prompt. |
| `gp` | Local Doskey alias to `git push`. |
| `grmc` | Local Doskey alias to `git-reword-merge.sh`; rewrites the current merge commit. |
| `pta` | Doskey alias to `pytest --testmon --cov-append ...`; reruns affected tests. |
| `ptr` | Doskey alias that resets `.testmondata` then reruns the suite with coverage. |
| `Qxx` block | An open-question block appended by the review skills (options + recommended choice). |
| `ruffc` | Doskey alias to `ruff check`. |
| `vX.Y.Z` | Working version slug used in every artifact filename (draft, requirement, design, plan). |
