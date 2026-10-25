# llm-shared

<img src="wiki/assets/logo-llm-shared-transparent.png" alt="llm-shared logo" width="160">

Shared instructions, templates, skills, and tools for AI-assisted development,
from a rough idea to a tagged release. The AI writes, reviews, implements, and
checks; **you settle the decisions, approve the commits, and release**.
Every phase leaves documents and evidence that another person or model can use.

A **skill** combines canonical instructions with the templates, supporting
files, and tools it needs. **LLM-specific scaffolding** supplies the discovery
metadata and redirects the host to those shared instructions; the workflow
body stays in one place.

| LLM / host | Current compatibility |
| --- | --- |
| OpenAI ChatGPT/Codex | Supported Codex plugin with skill adapters in `.agents/llm-shared/` |
| Anthropic Claude Code | Supported skills in `.claude/skills/` |
| Google Gemini through Antigravity | Supported workflows in `.agent/workflows/` |
| GitHub Copilot | Supported skills, prompts, and agent adapters in `.github/` |
| Grok | Portable redirects for all shared commands in `.grok/commands/`; explicit loading, native discovery unverified |
| Other LLMs, including plain ChatGPT or Gemini chat | Load the canonical files explicitly; local automation requires filesystem and tool access |

[Set up your agent](wiki/tutorials/01-plug-llm-shared-into-your-project.md),
read [how skills and scaffolding fit together](wiki/explanation/one-body-many-agents.md),
or [add scaffolding for another LLM](wiki/how-to/add-an-llm-adapter.md).
The [compatibility reference](wiki/reference/repository-layout.md#llm-compatibility)
records entry points and coverage limits.

## 1. The development workflow

Start with a draft and ask for `process-draft`. The agent chains the skills
through `pw skill` and `pw handoff`; you intervene at the decisions below.
Command names here omit the host prefix: for example, Claude uses
`/process-draft`, and the Codex plugin uses `$llm-shared:process-draft`.

| Stage | What the AI produces and checks | Your intervention |
| --- | --- | --- |
| Frame the work | `process-draft` names and branches the effort; `split-and-define` separates a collection into ordered requirements | Choose the title, slug, version, document/branch layout, and test scope where applicable. Approve each focused child draft derived from a collection. |
| Settle the requirement | `write-requirement`, review questions, then `explain-undecided-questions` for guided decisions and a fresh consistency review | Decide each question, review any new questions, then request consolidation. |
| Design and plan | `write-design` defines the solution and acceptance scenarios; `write-plans` creates numbered steps and a validation plan. Each gets the same review loop. | Settle design and plan questions. Say `stop here` when consolidating the plan if you want to hold before implementation; otherwise it starts automatically. |
| Implement and verify | `implement-step` writes code and tests, runs the Groundhog quality loop, then chains `implementation-check` and any `implement-missing-step` repairs | Resolve blockers that require your judgment. The agent handles ordinary repairs and reruns. |
| Commit each step | `group-commits-msg` prepares coherent groups and Conventional Commit messages in `a.commit` | Review the evidence and groups; approve commit replay, optionally with continuation to the next step or release preparation. |
| Integrate and release | `prepare-release` integrates the effort, reviews project docs, and prepares notes, versions, and changelog. Collections return to their next requirement until complete. | Approve the proposed Git operations, resolve conflicts, and review the release title and notes. Run `brel` for the final build/tag; pushing remains your decision. |

The two recurring loops are **write → review → explain and decide → review → consolidate**
for documents, and **implement → test → check → repair** for code. Groundhog
restarts its checks, affected tests, and full test/coverage gate after fixes.
The written requirement, plan, and validation evidence keep each loop tied to
the original objective. The [guided question phase](wiki/how-to/explain-undecided-questions.md)
preserves questions, records explicit decisions, and resumes where you paused.

Choosing consolidation also authorizes its documented snapshot and cleanup
commits; the implementation commit gate is separate. See
[where the human stays in the loop](wiki/explanation/where-the-human-stays-in-the-loop.md)
for the exact boundaries, and follow the
[draft tutorial](wiki/tutorials/02-from-draft-to-settled-requirement.md) and
[implementation tutorial](wiki/tutorials/04-run-the-implement-chain.md) to try it.

### Pause now, resume later

Use these commands in the agent session working on your project:

| Command | Result |
| --- | --- |
| `status-session` | Reports whether an unprocessed pause prompt exists, then gives three points from it or the latest notes, handoffs and journals. Leaves files and tasks unchanged. |
| `list-session` | Lists every folder with a session waiting to be resumed, the agent that should resume it and a short summary, then every session in progress (resumed and not paused since, possibly interrupted). Reads the private journal `%USERPROFILE%\.llm-shared\sessions.journal.md`; changes no files. |
| `pause-session` | Refreshes notes, saves a comprehensive resume prompt whose first line names the pausing agent (`claude`, `chatgpt`, `gemini`, `copilot`, `grok`), adds a session journal entry, confirms its relative path, and stops task work. |
| `resume-session` | Asks for consent when the prompt was paused by another agent or names none; otherwise announces the prompt's relative path and that it will use it, reads and reconciles the saved context, records its use, then continues authorized work in the same turn. Without an unprocessed prompt (reboot, already used), resumes from the latest notes. |
| `resume-session --force` | Reads that same prompt again after it has already been used, instead of the latest notes. |

The prompt is `.reviews/a.session-resume.local.md`; its usage receipt is
`a.session-resume.used.local.md` beside it. A configured review artifact home
is honored. Each pause replaces the latest prompt and clears its receipt;
journals retain the history. The snapshot carries objectives, decisions,
permissions, completed and remaining work, evidence, live jobs, and next actions.

The receipt identifies the exact prompt by SHA-256 and confirms context recovery,
not task completion. Force bypasses only the already-used check; pending human
decisions remain pending. These are LLM commands. For invocation examples,
templates, and recovery steps, see
[pause and resume a working session](wiki/how-to/pause-and-resume-a-session.md).

## 2. Goodies alongside the workflow

Use these independently or add them to the development cycle.

| Need | Tools and guidance |
| --- | --- |
| An independent second review | [Specification and code review](wiki/explanation/independent-review-mode-and-human-authority.md), with separately started requestor/reviewer sessions, automatic intermediate rounds, human convergence decisions, [status](wiki/how-to/inspect-independent-review-status.md), and [recovery](wiki/how-to/recover-an-independent-review.md). |
| Tests, coverage, and speed | [Groundhog](wiki/tutorials/03-your-first-groundhog-walk.md), [slow-test repair](wiki/how-to/fix-a-slow-test.md), and [coverage helpers](wiki/reference/aliases-and-launchers.md). |
| Code auditing and refactoring | [Application audit](instructions/audit-application.md), [large-file splitting](wiki/how-to/split-a-large-file.md), and [one-shot prompts](instructions/prompts/) for API analysis, fixes, coverage, complexity, and docstrings. |
| Clear commits and releases | [Grouped Conventional Commits](wiki/how-to/group-commits-into-conventional-messages.md), [merge rewording](wiki/how-to/reword-a-merge-commit.md), [release preparation](wiki/how-to/prepare-a-release.md), and [release-note summaries](instructions/write-release-notes-summary.md). |
| Useful project documentation | [Documentation updates from code or a Git range](wiki/how-to/update-project-docs-from-code.md), [effort-folder organization](instructions/arrange-docs-folders.md), shared [templates](wiki/reference/templates.md), and [Markdown checks](wiki/reference/markdown-checker.md). |
| Sensitive-content protection | [Commit hooks](wiki/how-to/install-sensitive-commit-hooks.md), plus [history scanning and sanitization](wiki/how-to/sanitize-history-before-publishing.md). |
| History and reporting | [Interactive Git-history dashboards](wiki/how-to/build-the-git-history-dashboard.md), [activity reports](wiki/how-to/write-an-activity-report.md), and [Git history diagrams](wiki/how-to/update-git-history-diagrams.md). |
| Presentations and visual assets | [PPTX/PDF presentation generation](wiki/how-to/rebuild-the-presentation.md), [coherent logo families](wiki/how-to/create-a-logo-family-for-a-project.md), and [logo-sheet extraction](instructions/isolate-logos.md). |
| Reading and writing aids | [Local Markdown website](wiki/how-to/serve-a-docs-folder-as-a-website.md), [conversation-export trimming](wiki/how-to/trim-an-exported-conversation.md), and [humanizer](instructions/prompts/humanizer.md). |

The full [Diátaxis wiki](wiki/README.md) is organized as
[explanation](wiki/README.md#-explanation),
[tutorials](wiki/README.md#-tutorials),
[how-to guides](wiki/README.md#-how-to-guides), then
[reference](wiki/README.md#-reference).
See the [skills catalog](wiki/reference/skills-catalog.md) and
[launcher reference](wiki/reference/aliases-and-launchers.md) for exact names,
or [set up the shared Python tools](wiki/how-to/set-up-shared-python-tools.md)
to run helpers and contribute to llm-shared.

Released under the [MIT License](LICENSE.md).
