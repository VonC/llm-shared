# llm-shared wiki

<!-- markdownlint-disable MD013 -->

<img src="assets/logo-llm-shared-transparent.png" alt="llm-shared logo: a chat window containing the four llm-shared themes" width="200">

## The main purpose: AI-assisted development with review and reset loops

llm-shared is first a structured development workflow assisted by AI, from a
rough idea to a tagged release. It turns natural-language intent into a
requirement, design, implementation plan, code, validation evidence, grouped
commits, and release artifacts. Each phase leaves a durable file that the next
human or model can inspect.

Its defining feature goes beyond the usual "spec-driven workflow": **the AI
must review what it has just generated, and a human validates the resulting
decisions**.

- After generating a requirement, design, or plan, the AI challenges it with
  a fixed question template: options, pros and cons, a recommended answer with
  rationale, and a place for the human answer. The decisions are consolidated
  and reviewed again until no material question remains.
- After generating code, the AI checks that implementation against the exact
  requirement, design, and numbered plan step. It also applies the project's
  standing directives for architecture, performance, line budget, security,
  observability, tests, and any additional quality criteria the team defines.
  Missing work produces an explicit `No` verdict, is implemented, and is
  checked again. A human reviews the evidence before the workflow advances.
- The AI then drives the [groundhog reset loop](explanation/groundhog-as-a-reset-loop.md):
  linters and structural checks, affected tests, then the complete test suite
  with a fresh coverage measurement. The objective is the project coverage
  gate—100% by default—and a duration gate stops an otherwise-green run when a
  test call is both a statistical outlier and above the configured time floor.
  The AI fixes failures, coverage gaps, and actionable slow tests, then starts
  the day again until the objective is green or a safety stop needs human
  judgment. Follow [your first groundhog walk](tutorials/03-your-first-groundhog-walk.md)
  to see the three stations in action.
- Every completed implementation step ends at the grouped-commit gate. The AI
  reconstructs coherent, least-dependent-first commits and writes informative
  multi-line Conventional Commit messages: a comprehensive `Why:` section for
  intent and resulting state, and a `What:` section for the concrete changes.
  The human validates the groups before replay. See
  [why grouped commits carry that history](explanation/why-grouped-commits.md)
  and [how to review and replay them](how-to/group-commits-into-conventional-messages.md).
- The release phase is equally complete: AI-assisted scope detection from
  `main`, a feature, or `develop`; conflict preview; safe rebase or `--no-ff`
  merge selection; release notes, versions, changelog, and a final preparation
  commit—without silently tagging or pushing. The human approves the topology
  and later runs the final build/tag action. Start with
  [why release branch roles matter](explanation/why-release-branch-roles-matter.md)
  or [prepare a release from any branch](how-to/prepare-a-release.md).

This makes self-review part of the workflow topology, not optional prompting
advice. The first generated answer is a draft; the reviewed, human-validated
artifact is the input to the next phase. This is the central idea presented in
[slide 4 of the project deck](../docs/llm-shared_presentation.html#solution-workflow-phases)
and developed further in [Why the LLM reviews its own work](explanation/why-the-llm-reviews-its-own-work.md).

## Four officially supported AI environments

One shared Markdown instruction body is exposed through the native discovery
mechanism of four supported environments:

- Anthropic Claude Code;
- OpenAI ChatGPT Codex;
- Google Gemini Antigravity;
- GitHub Copilot.

The wrappers differ, but the workflow, templates, review gates, and artifacts
do not. Any other agent that can read and write workspace files can also be
handed the same instruction bodies. See [One body, many agents](explanation/one-body-many-agents.md).

## Additional utilities are first-class too

The repository also ships independent tools and skills that remain useful
outside the complete document-to-release chain: the groundhog test-reset loop,
conventional commit grouping, selective release preparation, release notes,
Git-history dashboards, sensitive-history scanning and sanitization, activity
reports, presentation generation, local wiki serving, and deterministic Git
history diagrams. These are additional goodies, not hidden implementation
details; each has its own task-oriented documentation below.

Each page carries the logo and emoji of its main theme: 📝 the document
pipeline, 🔁 self-review and handoff, 🧪 the groundhog test gate, 📊 the shared
trail, or 🤖 llm-shared as a whole. The logo sources are documented in
[assets/logo-prompts.md](assets/logo-prompts.md).

The wiki follows [Diátaxis](https://diataxis.fr/) and always presents its four
purposes in this order: explanation, tutorials, how-to guides, then reference.

## 💡 Explanation

Background and reasoning: understand why the workflow and utilities make
their choices.

### AI-assisted development workflow

- 📝 [Why documents come before code](explanation/why-documents-before-code.md)
- 🔁 [Why the LLM reviews its own work](explanation/why-the-llm-reviews-its-own-work.md)
- 🔁 [Where the human stays in the loop](explanation/where-the-human-stays-in-the-loop.md)
- 🔁 [One launcher, three modes](explanation/one-launcher-three-modes.md)
- 🤖 [One body, many agents](explanation/one-body-many-agents.md)

### Additional utilities

- 🧪 [Groundhog as a reset loop](explanation/groundhog-as-a-reset-loop.md)
- 📊 [Why grouped commits, least dependent first](explanation/why-grouped-commits.md)
- 📊 [Why release branch roles matter](explanation/why-release-branch-roles-matter.md)
- 📊 [Why Git history diagrams use explicit arrows](explanation/why-git-history-diagrams-use-explicit-arrows.md)
- 📊 [Why sensitive-history replacement needs context](explanation/why-sensitive-history-needs-context.md)

## 🎓 Tutorials

Learning by doing: follow the steps in order and inspect the result.

### AI-assisted development workflow

- 🤖 [Plug llm-shared into your project](tutorials/01-plug-llm-shared-into-your-project.md)
- 📝 [From draft note to settled requirement](tutorials/02-from-draft-to-settled-requirement.md)
- 🔁 [Run the implement chain on one plan step](tutorials/04-run-the-implement-chain.md)

### Additional utilities

- 🧪 [Your first groundhog walk](tutorials/03-your-first-groundhog-walk.md)
- 📊 [Prepare your first release from develop](tutorials/05-prepare-a-release-from-develop.md)
- 📊 [Audit sensitive Git history for the first time](tutorials/06-audit-sensitive-history.md)
- 📊 [Generate the Git history diagrams](tutorials/07-generate-git-history-diagrams.md)

## 🧭 How-to guides

Recipes for a precise goal, for readers who already know the basics.

### AI-assisted development workflow

- 📝 [Split a mixed draft into requirements](how-to/split-a-mixed-draft.md)
- 🔁 [Answer a review round](how-to/answer-a-review-round.md)
- 🔁 [Run pw from any shell](how-to/run-pw-from-any-shell.md)
- 🤖 [Keep project docs in sync with the code](how-to/update-project-docs-from-code.md)

### AI-environment compatibility

- 🤖 [Register the skills as a Codex plugin](how-to/register-skills-as-a-codex-plugin.md)
- 🤖 [Use the skills from Google Antigravity](how-to/use-the-skills-from-antigravity.md)
- 🤖 [Pick up skill edits without restarting](how-to/pick-up-skill-edits-without-restarting.md)

### Additional utilities

- 🧪 [Fix a red groundhog walk](how-to/fix-a-red-groundhog-walk.md)
- 🧪 [Fix a slow test flagged as an outlier](how-to/fix-a-slow-test.md)
- 🧪 [Register groundhog in a project](how-to/register-groundhog-in-a-project.md)
- 🧪 [Split a large file](how-to/split-a-large-file.md)
- 📊 [Group a dirty tree into conventional commits](how-to/group-commits-into-conventional-messages.md)
- 📊 [Reword a merge commit from the branch docs](how-to/reword-a-merge-commit.md)
- 📊 [Prepare a release from any branch](how-to/prepare-a-release.md)
- 📊 [Build the Git-history dashboard](how-to/build-the-git-history-dashboard.md)
- 📊 [Sanitize a repository history before publishing](how-to/sanitize-history-before-publishing.md)
- 📊 [Write an activity report](how-to/write-an-activity-report.md)
- 📊 [Rebuild the presentation as PPTX and PDF](how-to/rebuild-the-presentation.md)
- 📊 [Update a Git history diagram](how-to/update-git-history-diagrams.md)
- 🤖 [Serve a Markdown folder as a local website](how-to/serve-a-docs-folder-as-a-website.md)

## 📖 Reference

Exact descriptions of commands, formats, files, and supported behavior.

### AI-assisted development workflow

- 🤖 [Skills catalog](reference/skills-catalog.md)
- 🔁 [pw launcher](reference/pw-launcher.md)
- 📝 [Artifact files and naming conventions](reference/artifact-files.md)
- 📝 [Document templates](reference/templates.md)
- 🤖 [Writing and agent rules](reference/writing-rules.md)
- 🤖 [Repository layout and AI entry points](reference/repository-layout.md)
- 🤖 [Automation and direct-invocation ownership](reference/automation-and-direct-invocation.md)

### Additional utilities

- 🤖 [Aliases and bin launchers](reference/aliases-and-launchers.md)
- 📊 [Commit message format](reference/commit-message-format.md)
- 🧪 [ghog commands and exit codes](reference/ghog-commands-and-exit-codes.md)
- 📊 [Prepare-release scenarios](reference/prepare-release-scenarios.md)
- 📊 [Prepare-release planner command](reference/prepare-release-planner.md)
- 📊 [Sensitive-history scanner command](reference/sensitive-history-scan.md)
- 📊 [Git-history diagram generator](reference/git-history-diagram-generator.md)
