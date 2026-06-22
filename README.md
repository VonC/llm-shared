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
- **Plan** the implementation as a numbered list of steps, then run the
  same review loop on the plan itself (not on the validation plan). The
  first step adds gate tests that fail on purpose; the following steps make
  those tests pass one by one. The last step adds the acceptance tests
  that close the loop on the original requirement
  (`/write-plans`, the plan review loop, `/implement-step`,
  `/implementation-check`).

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
| Draft capture | Author writes free-form notes | a raw draft note |
| Process draft | `/process-draft` | the draft classified (feature-request / issue), renamed `docs\draft.vX.Y.Z.<slug>.md`, on a new effort branch |
| Split (optional) | `/split-and-define` | `List of feature-requests and issues to create` section appended to the draft |
| Define each item | `/write-requirement <type> vX.Y.Z <topic>` | `docs\feature-request.vX.Y.Z.<topic>.md` or `docs\issue.vX.Y.Z.<topic>.md` |
| Review loop | `/review-ask-questions` then `/consolidate-then-review-ask-questions` | Open questions folded into a decision table; document approved |
| Design | `/write-design` | `docs\design.vX.Y.Z.<topic>.md` with acceptance scenarios |
| Plan | `/write-plans` | `docs\plan.vX.Y.Z.<topic>.md` + `docs\plan.vX.Y.Z.<topic>.validation.md` |
| Plan review loop | `/review-ask-questions` then `/consolidate-then-review-ask-questions` on the plan | Plan open questions folded into a decision table; plan approved (the validation plan is left untouched) |
| Implement and check | `/implement-step N`, then `pw handoff` chains `/implementation-check N` | Code, tests, and updates to the validation document |
| Group commits | `pw handoff after-check` routes a `Yes` step to `/group-commits-msg`; `gcba` replays | `a.commit` with one conventional commit per group, replayed by `gcba` |
| Merge and reword | `git merge --no-ff` then `/update-merge-commit-msg` then `grmc` | Merge commit with a conventional message tied to the merged docs |
| Prepare release notes | `/prepare_release_notes` | `a.md`, a release-notes summary in `version.txt`, an updated `CHANGELOG.md` |
| Prepare release (automated) | `/prepare-release` | Rebases the branch onto the latest main when behind (with a `ghog day` gate), does the merge and reword, the `version.txt` snapshot, `/prepare_release_notes`, and the pyproject and uv steps, then one `chore(release): prepare for vX.Y.Z release` commit; stops before `brel` |
| Release | `brel` | Version tag `vX.Y.Z` on `main`, marked `[valid]` after a green build |

From `/implement-step N` down to the `a.commit` group-commit-message step,
the rows no longer need a separate trigger each. One `pw handoff` call at
the end of each step writes the next prompt and the chain runs itself  --
see [Automated implement cycle with pw handoff](#automated-implement-cycle-with-pw-handoff).

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
                  |  raw draft note |
                  +--------+--------+
                           |
                           |  /process-draft  (classify feature/issue,
                           |  pick vX.Y.Z, rename draft.vX.Y.Z.<slug>.md,
                           |  create the effort branch)
                           v
                  +-----------------+
                  | named, branched |
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
                  |     plan +      |----+
                  | validation plan |    |  /review-ask-questions
                  |                 |<---+  /consolidate-then-review-ask-questions
                  +--------+--------+       (loop on the plan only, not the
                           |                 validation plan)
                           |  /implement-step N   (enters the chain)
                           v
   +=================================================================+
   |  Automated implement chain  --  pw handoff wires each box       |
   |  to the next: no menu, and no "go ahead" between the steps      |
   |  inside this box.                                               |
   |                                                                 |
   |              +-----------------+                                |
   |              | implement step  |                                |
   |              +--------+--------+                                |
   |                       |  pw handoff check <x>                   |
   |                       v                                         |
   |              +-----------------+                                |
   |              | implementation  |----+  No: implement-           |
   |              | check (Yes/No)  |    |  missing step, then       |
   |              +--------+--------+<---+  pw handoff check <x>     |
   |                       |  pw handoff after-check <x>             |
   |                       |  (Yes branch)                           |
   |                       v                                         |
   |              +-----------------+                                |
   |              | group-commits-  |                                |
   |              | msg writes      |                                |
   |              | a.commit        |                                |
   |              +--------+--------+                                |
   +======================= =========================================+
                           |  chain ends: a.commit holds the grouped
                           |  commit messages, ready for review
                           v
                  +-----------------+
                  | step N          |----+  "go ahead" -> gcba replays
                  | committed       |    |  the grouped commits, gp
                  |                 |<---+  (loop for next step)
                  +--------+--------+
                           |
                           |  last step done: effort branch ready
                           v
                  +-----------------+  one command, any branch: switch to
                  | prepare-release |  main + merge --no-ff, reword, set
                  |  stops before   |  version.txt -SNAPSHOT, run
                  |    the tag      |  /prepare_release_notes (notes +
                  +--------+--------+  CHANGELOG), pyproject + uv, then one
                           |           chore(release): prepare commit
                           |  review everything, then
                           |  brel   (build + tag)
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

The giant box around the implement, check, and group-commit steps marks
the part that now runs by itself: `pw handoff` chains those steps with no
menu and no go-ahead until `a.commit` is written. See
[Automated implement cycle with pw handoff](#automated-implement-cycle-with-pw-handoff)
for how each transition fires.

The flow opens and closes with one skill each. `/process-draft` turns a
loose draft note into a named, classified, branched effort ready to spec
(see [DEVELOPMENT.md  --  Draft capture for a feature or fix](DEVELOPMENT.md#draft-capture-for-a-feature-or-fix)).
`/prepare-release` is the box at the bottom: one command, from any branch,
that does the merge and reword, the `version.txt` snapshot,
`/prepare_release_notes`, and the pyproject and uv steps, then a single
`chore(release): prepare` commit, and stops before `brel` tags (see
[DEVELOPMENT.md  --  Automate the prep with /prepare-release](DEVELOPMENT.md#automate-the-prep-with-prepare-release)).

The `/split-and-define` phase is optional. When the draft already
describes a single, self-contained requirement, the author can call
`/write-requirement` directly and pass the type (`feature-request` or
`issue`), version, and topic  --  no split step is needed. Reach for
`/split-and-define` when the draft mixes several distinct items, when
the items differ in dependency order, or when the author wants the skill
to suggest a slug per item.

---

## Automated implement cycle with pw handoff

The giant box in the diagram above is the part of the workflow that now
runs on its own. Each step ends by calling `pw handoff`, which writes the
prompt for the next step; the model reads that prompt and keeps going,
with no menu in between and no pause to ask "should I proceed?". `pw` is
the prompt-workflow launcher (`bin\prompt_workflow.bat`, the `pw` alias);
`pw handoff <task> <x>` builds the next cycle prompt for plan step `<x>`
without showing the interactive menu.

### The three handoff calls that chain the steps

The chain covers the forward moves of the implement cycle. Each move is
one `pw handoff` call, run from the project root once the current step is
done:

- after `/implement-step <x>` (once its `ghog day` walk is green):
  `pw handoff check <x>` writes the `implementation-check.md` prompt.
- after `/implementation-check <x>` (once it records its Yes/No verdict):
  `pw handoff after-check <x>` lets `pw` pick the next step itself.
- after `/implement-missing-step <x>` (once its walk is green):
  `pw handoff check <x>` again, so the filled gap is re-checked.

### Why after-check decides the branch instead of the caller

`after-check` is neutral on purpose. `pw` reads the `Analysis of Step x`
status line the check just wrote and routes the branch, so the caller
cannot pick the wrong next step:

- a `No` status  --  the `implement-missing-step.md` prompt, to fill the
  gap the check listed, then back to the check.
- a `Yes` status  --  the `group-commits-msg.md` prompt (its `git add -A`
  form), which stages every change and writes one grouped commit message
  per group into `a.commit`.

### Where the automated chain stops

The chain stops at `a.commit`. Writing the grouped commit messages is the
last automatic step; making the real commits is not. `gcba` replays
`a.commit` only after the author reviews it and says "go ahead", the
review gate that `group-commits-msg.md` keeps. So the model writes the
messages on its own, then waits for the go-ahead before any commit lands.

### What each handoff leaves on disk

Every `pw handoff` call writes the next prompt to `a.prompt.txt` at the
project root, copies it to the clipboard, and records the step in
`a.prompt_memory`. The model confirms the first line of `a.prompt.txt`
names the expected instruction, then follows that prompt. The calls are
wired into the workflow by the `## Handoff` section of each cycle
instruction (`implement-step.md`, `implement-missing-step.md`, and
`implementation-check.md`); the same chain is drawn step by step in
[DEVELOPMENT.md  --  Step execution loop from the plan](DEVELOPMENT.md#step-execution-loop-from-the-plan).

---

## Prepare release notes before tagging a release

A release is more than a git tag. Before `main` is tagged, the
`/prepare_release_notes` skill turns the commit history since the last
tag into release notes a reader can use.

The skill runs
[`scripts/prepare_release_notes.sh`](scripts/prepare_release_notes.sh):
it reads the `X.Y.Z-SNAPSHOT` version from `version.txt`, collects every
conventional-commit title since the last tag, and writes `a.md` with
those titles grouped by type. From `a.md`, the skill writes a
release-notes summary back into `version.txt`  --  a main theme, a short
list of key changes, and three witty title / subtitle pairs for the
author to pick from. Once a title is picked, the skill calls
`update-changelog.bat` to fold the summary into `CHANGELOG.md`.

This skill stops before the tag. Creating the release is a separate
step: the author runs `brel`, which drives the project build with the
`rel` parameter. See
[DEVELOPMENT.md  --  Prepare release notes and create the release](DEVELOPMENT.md#prepare-release-notes-and-create-the-release)
for the six-step workflow and the dependency on the `senv_dev_workflow`
build tooling.

---

## Make a release with the prepare-release skill

A release is more than the tag: the effort branch is merged into `main`,
`version.txt` is set to `X.Y.Z-SNAPSHOT` with its release notes,
`CHANGELOG.md` is updated, and only then is `main` tagged `vX.Y.Z` by
`brel`. The `/prepare-release` skill drives every step except the tag, from
any branch, and stops at one `chore(release): prepare for vX.Y.Z release`
commit for the author to review.

It calls the smaller skills rather than repeating them, signalling each
through a git-ignored `a.prepare-release.active` flag file so the callee
hands control back:

- `group-commits-msg`  --  commit a dirty tree, or commit fixes a test gate
  needed.
- `update-merge-commit-msg`  --  give the merge commit the `Why:` / `What:`
  message (a free-form one is refused).
- `prepare_release_notes`  --  the `version.txt` summary and `CHANGELOG.md`.
- the `ghog day` groundhog loop  --  the green gate after a rebase or a
  stale-base merge.

The skill pauses whenever the author must decide or act, and several pauses
resume only on an explicit "go ahead": choosing rebase / merge-anyway /
abort when the branch is behind `main`, resolving a rebase conflict, picking
a release title, and the notes-review pause where the author edits the
`version.txt` summary or asks for `.changelog.fixes` rules before the
changelog is regenerated. It never tags and never pushes; the author runs
`brel` at the end. The full pause-by-pause table is in
[DEVELOPMENT.md  --  Automate the prep with /prepare-release](DEVELOPMENT.md#automate-the-prep-with-prepare-release).

---

## Groundhog: the pytest reset loop

The test side of the workflow is driven by groundhog (`ghog`), one tool replacing the old `ptr`/`pta`/`pts` aliases: `ghog day` walks compile check, affected tests, then the full suite with a fresh coverage measure, stopping at the first non-green step with the exact fix to apply; `ghog init` registers the fixing loop in a project for both Claude Code (`/groundhog`) and ChatGPT Codex (AGENTS.md section plus a `/groundhog` custom prompt). LLM-driven runs go through a project-root `a.ghog.log` (overwritten per run, never deleted): the model branches on exit codes and reads only the log tail, while the user follows the run live from a second console; direct console runs keep the usual stdout. The full manual is [GROUNDHOG.md](GROUNDHOG.md).

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
├─ groundhog.md                           the groundhog fixing loop (see GROUNDHOG.md)
├─ group-commits-msg.md
├─ implement-step.md
├─ implement-missing-step.md
├─ implementation-check.md
├─ prepare-release-notes.md
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
├─ open-question.template.md              Qxx/BBQ/Options block for review skills
├─ prepare-release-notes.version-txt.template.txt version.txt release-notes summary skeleton
├─ write-design.template.md               design document skeleton
├─ write-plans.template.md                implementation plan skeleton
├─ write-plans.validation.template.md     validation plan skeleton
└─ write-requirement.template.md          feature-request and issue document skeletons
scripts/                                  shared helper scripts grouped by skill
├─ prepare_release_notes.sh               build a.md from the git history since the last tag
└─ update-merge-commit-msg/
   ├─ git-extract-merge-docs.sh           dump the merged branch docs to a.docs
   └─ git-reword-merge.sh                 rewrite the current merge commit from a.commit
tools/
├─ git_batch_commit.py                    validate and replay grouped commits
├─ git_command.py                         local cross-platform Git helper
├─ groundhog/                             pytest reset tool behind ghog/ptr/pta/ptanc/pts (see GROUNDHOG.md)
├─ prompt_workflow.py                     build the next cycle prompt; pw handoff chains the implement cycle
└─ uv_run.py                              cert-aware uv launcher (personal/corporate networks)
senv.bat                                  local shell aliases for the tooling
```

---

## Development environment

Using the shared skills needs no Python environment — they are plain
markdown. A Python environment is only needed to **work on llm-shared
itself**: to run the helper scripts under `tools/` and the test suite
under `tests/`.

Dependencies are declared in [`pyproject.toml`](pyproject.toml) (the
`[dependency-groups]` `dev` group) and pinned in `uv.lock`. The
repository is managed with [uv](https://docs.astral.sh/uv/); there are
no longer any `requirements*.txt` files.

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux
venv\Scripts\activate           # Windows
```

`uv` is the installer. On a fresh checkout it is not yet present, but it
ships on PyPI as a wheel with the binary bundled in, so the `pip` that
comes with every `venv` can bootstrap it:

```bash
# Inside the activated virtual environment, when `uv` is not installed
python -m pip install uv

# Then install the development tooling from the lockfile
uv sync
```

That two-step replaces the former `pip install -r requirements.dev.txt`.
If `uv` is already installed system-wide, the first command can be
skipped and `uv sync` run directly.

### Dependency maintenance

```bash
uv lock              # refresh uv.lock after editing pyproject.toml
uv lock --upgrade    # bump every dependency to its newest allowed version
uv sync              # apply the lockfile to the venv
uv add --dev <package>   # add a development dependency
```

`uv` is not aliased — it runs the venv's `uv.exe` directly. That means a
plain `uv lock`, `uv lock --upgrade`, or `uv sync` uses only the
environment prepared by `senv.bat`: if a corporate PEM is found,
`SSL_CERT_FILE`, `CURL_CA_BUNDLE`, and `UV_CERT` point at it; if no PEM
is found, those variables stay unset.

The `pcomp` / `pupg` / `psync` aliases are shortcuts for the first three
commands, but they do not call `uv.exe` directly: they route through
[`tools/uv_run.py`](tools/uv_run.py), a cert-aware launcher. On a
corporate machine, `senv.bat` looks for the newest bundle-like `*.pem`
first in a local ignored `certs/` folder under the repo, then in the
parent folder of the repository, and only falls back to a generic
`*.pem` when no bundle-like PEM exists. `uv_run.py` then tries `uv`
with that explicit PEM first; if the command still fails with a
certificate error, it retries with `--system-certs`, and only after
that falls back to `uv`'s default trust roots.

The public nature of this repository is a separate concern. It does not
change how local `uv` commands trust a corporate proxy. Instead,
`senv.bat` installs a local git clean filter for `uv.lock`. That filter
rewrites any staged registry URL to `https://pypi.org/simple/` and any
staged package URL to `https://files.pythonhosted.org/packages/`, so
committed `uv.lock` content stays free of corporate mirror references
even when local `uv` commands use a corporate index. After clearing any
stale inherited value from an older activation, `senv.bat` derives
`UV_INDEX_URL` from `PYPI_HOST` when that variable is present in the
shell.

So when plain `uv` already works on a corporate machine, the usual reason
is that `senv.bat` has already populated `SSL_CERT_FILE` with the
corporate PEM and `uv.exe` can use that bundle directly, without needing
the wrapper retry path.

If you want the automatic TLS fallback path, use `pcomp`, `pupg`,
`psync`, or call `python tools/uv_run.py ...` yourself. It is
project-agnostic; any repository that loads this `senv.bat` gets the
same shortcuts.

### Checking dependency state

Three read-only commands answer "is everything in order?" without
changing anything:

```bash
uv sync --locked --check     # venv matches uv.lock, and uv.lock matches pyproject.toml
uv lock --upgrade --dry-run  # whether any locked version could move to a newer release
uv pip list --outdated       # installed packages with a newer release on PyPI
```

| Command | Network | Reports |
| --- | --- | --- |
| `uv sync --locked --check` | no | venv ↔ `uv.lock` ↔ `pyproject.toml` consistency; exits non-zero on any drift |
| `uv lock --upgrade --dry-run` | yes | which locked versions a `uv lock --upgrade` *would* move, writing nothing |
| `uv pip list --outdated` | yes | installed packages with a newer PyPI release |

`uv lock --upgrade --dry-run` honours the constraints of the whole
dependency graph; `uv pip list --outdated` does not. A package can
appear "outdated" there yet be unmovable — for example `mando` is held
below `0.8` by `radon` (`Requires-Dist: mando (<0.8,>=0.6)`), and `pip`
is the virtual environment's own seed package, not a tracked
dependency. Only what `uv lock --upgrade --dry-run` reports can be
upgraded by `pupg`.

`pip` is unmanaged by uv, so `pupg` never moves it. Upgrade the venv's
seed `pip` directly when `uv pip list --outdated` flags it — this
touches neither `pyproject.toml` nor `uv.lock`:

```bash
uv pip install --upgrade pip
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
| Groundhog pytest loop | draft | Claude Code (VS Code + CLI), ChatGPT Codex | `ghog day` walk, `ghog init` registration, LLM fixing loop; see `GROUNDHOG.md`. |
| Prompt-workflow handoff | draft | Claude Code (VS Code + CLI) | `pw handoff` chains implement-step, check, implement-missing, and the `a.commit` group-commit step with no menu. |

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
| `a.prompt.txt` | Next-step prompt written by `pw` / `pw handoff`; the model reads it to continue the cycle. |
| `a.prompt_memory` | Per-branch workflow state `pw` records: branch, locked topic, current step. |
| `c` | Doskey alias to `bin\python_check.bat`. |
| `covg` | Doskey alias that maps uncovered lines to functions and builds a clipboard prompt. |
| `gate test` | A failing test added before the implementation step that makes it pass. |
| `gcba` | Doskey alias to `git_batch_commit.py --root-a-commit`; validates and replays `a.commit`. |
| `gcmp` | Doskey alias to `group_commit_message_prompt.py`; writes `a.diff` and the clipboard prompt. |
| `ghog` | Doskey alias to `bin\ghog.bat`, the groundhog pytest reset tool; `ghog day` walks check + affected + full, `ghog init` registers the LLM fixing loop (see `GROUNDHOG.md`). |
| `gp` | Local Doskey alias to `git push`. |
| `grmc` | Local Doskey alias to `git-reword-merge.sh`; rewrites the current merge commit. |
| `pta` | Doskey alias to `ghog affected`: testmon-selected tests with appended coverage, key=value report, exit-code contract. |
| `ptanc` | Doskey alias to `ghog affected --no-cov`: the fast focused pass with coverage off. |
| `pts` | Doskey alias to `ghog single <test files>`: named test files in focus, coverage off, compared with the last full-run baseline. |
| `ptr` | Doskey alias to `ghog full`: resets `.testmondata`, reruns the suite with coverage against the gate; the objective verdict. |
| `pw` | Doskey alias to `bin\prompt_workflow.bat` (`tools\prompt_workflow.py`); builds the next cycle prompt, interactively or via `pw handoff <task> <x>`. |
| `pw handoff` | The non-interactive `pw handoff <task> <x>` subcommand; writes the next step prompt with no menu, the engine of the automated chain. |
| `Qxx` block | An open-question block appended by the review skills (options + recommended choice). |
| `ruffc` | Doskey alias to `ruff check`. |
| `vX.Y.Z` | Working version slug used in every artifact filename (draft, requirement, design, plan). |

---

## License for llm-shared

This repository is released under the MIT License. The full text is in
[LICENSE.md](LICENSE.md): use, copy, modify, and redistribute the
prompts, skills, instructions, templates, and helper scripts, in your
own projects or forks, as long as the copyright notice stays in place.

See [DEVELOPMENT.md  --  License rationale: why MIT fits llm-shared](DEVELOPMENT.md#license-rationale-why-mit-fits-llm-shared)
for why MIT was picked over a copyleft license.
