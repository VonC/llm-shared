# Skills catalog

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Every skill, its trigger, its inputs and what it writes. Each skill
resolves to the same-named body under `instructions/`; see the
[repository layout](repository-layout.md#shared-bodies-and-rules). GitHub Copilot and Claude Code delegate
through `.github/skills/` and `.claude/skills/`; OpenAI ChatGPT Codex uses the
self-contained `.agents/llm-shared/` plugin; Google Gemini Antigravity uses
`.agent/workflows/`. These are the four officially supported environments.

## Invocation model

Users normally invoke a top-level skill in natural language and let the AI chain
the required support skills and commands. Invoke a lower-level skill directly
when deliberately entering, repeating, or resuming that one phase with its
prerequisites already satisfied.

## 🗺️ Workflow skills in phase order

| Skill | Inputs | Writes |
| --- | --- | --- |
| `/process-draft` | a named draft, `version.txt` | draft renamed `docs\draft.vX.Y.Z.<slug>.md`, effort branch or worktree |
| `/split-and-define` | a multi-topic draft | list section appended to the draft |
| `/write-requirement` | type, `vX.Y.Z`, topic | `docs\feature-request.vX.Y.Z.<topic>.md` or `docs\issue.vX.Y.Z.<topic>.md` |
| `/review-ask-questions` | a requirement, design or plan | `## Open questions` section, `Q0x` summary table |
| `/consolidate-then-review-ask-questions` | the doc with answers | decision table, stripped questions, or a new round |
| `/write-design` | the settled requirement | `docs\design.vX.Y.Z.<topic>.md` |
| `/write-plans` | the settled design | `docs\plan.vX.Y.Z.<topic>.md` + `.validation.md` skeleton |
| `/implement-step N` | plan, design, requirement | code and tests, green `ghog day` |
| `/implementation-check N` | the plan, the diff | verdict in `docs\plan...validation.md` |
| `/implement-missing-step N` | the `Missing work` list | code and tests filling the gaps |
| `/group-commits-msg` | the staged diff | `a.commit`, one message per group |
| `/update-merge-commit-msg` | the merge commit | `a.docs`, `a.commit`, reworded merge |
| `/prepare_release_notes` | `version.txt`, git history | `a.md`, `version.txt` summary, `CHANGELOG.md` |
| `/prepare-release` | `main`, integration, or an isolated effort branch | one `chore(release): prepare` commit on `main`, or an evidence-backed manual runbook when the requested selection is unsupported |

## 🛠️ Support skills

| Skill | Purpose |
| --- | --- |
| `/groundhog` | the ghog fixing loop: walk, fix what the report names, walk again |
| `/split-large-file` | split an over-budget file into single-responsibility files |
| `/review-and-update-project-docs` | re-align README, ARCHITECTURE and docs/architecture with the code |
| `/write-release-notes-summary` | draft release notes from conventional commit subjects |
| `git-history-report` | build the standalone commit-history dashboard |
| `activity-report` | French activity report from commit messages and md diffs |
| `/sanitize-git-history` | automatically run the contextual history scanner, settle confidential-term rules, then optionally rewrite with git filter-repo |
| `prepare_release_plan.bat` | internal read-only single-source tool called automatically by `/prepare-release`; its standalone interface supports diagnostics, while the skill guards empty integration ranges and explains unsupported revert, multi-topic, and non-contiguous paths |

## 🔗 Chaining behavior of the writing skills

`/write-requirement`, `/write-design` and `/write-plans` each end by
running `pw skill` and running the `/review-ask-questions` it prints —
pass `stop here` in the argument to hold the chain and read the document
first. `/consolidate-then-review-ask-questions` runs `pw skill` when the
document settles. `/implement-step`, `/implementation-check` and
`/implement-missing-step` chain through `pw handoff` instead, and
`/group-commits-msg` closes the chain at the commit gate with
`pw skill --after-commit <x>`.

## 📌 Fixed sentences and stops worth knowing

- `/implementation-check` opens with exactly
  `Yes. Step N has been fully implemented.` or
  `No. Step N has NOT been fully implemented.` — `pw` routes on that line.
- `/review-ask-questions` always ends on the
  `Q0x | Title | Recommended Answer` table and never runs the next skill
  itself.
- `/prepare-release` and `/update-merge-commit-msg` coordinate through the
  git-ignored flag file `a.prepare-release.active`.
- `/write-requirement` refuses to infer the version: type, `vX.Y.Z` and
  topic label are validated one by one, and the run stops for correction
  on each invalid field.

Related: [pw launcher](pw-launcher.md),
[Artifact files and naming conventions](artifact-files.md), and
[Prepare-release scenarios](prepare-release-scenarios.md).
