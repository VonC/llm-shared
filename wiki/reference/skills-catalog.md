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
| `/process-draft` | a new draft and `version.txt`, or one canonical umbrella row selected by `pw` | named draft and effort branch; an umbrella continuation preserves the umbrella, creates a focused child, and waits for explicit approval before requirement writing |
| `/split-and-define` | a multi-topic collection draft | explicit umbrella marker, ordered pending/completed table, and requirement-detail subsections |
| `/write-requirement` | type, `vX.Y.Z`, topic | `<effort-dir>/feature-request.vX.Y.Z.<topic>.md` or `<effort-dir>/issue.vX.Y.Z.<topic>.md` |
| `/review-ask-questions` | a requirement, design or plan | `## Open questions` section, `Q0x` summary table |
| `/consolidate-then-review-ask-questions` | the doc with answers | scoped one-file question snapshot, then a decision table and stripped questions; a settled fold groups every remaining change and requires a clean tree before handoff |
| `/write-design` | the settled requirement | `<effort-dir>/design.vX.Y.Z.<topic>.md` |
| `/write-plans` | the settled design | `<effort-dir>/plan.vX.Y.Z.<topic>.md` + `.validation.md` skeleton |
| `/implement-step N` | plan, design, requirement | code and tests, green `ghog day` |
| `/implementation-check N` | the plan, the diff, and an associated umbrella when present | verdict in `<effort-dir>/plan...validation.md`; the final successful step also completes the matching umbrella row with evidence paths |
| `/implement-missing-step N` | the `Missing work` list | code and tests filling the gaps |
| `/group-commits-msg` | the staged diff | `a.commit`, one message per group |
| `/update-merge-commit-msg` | the current no-fast-forward merge | `a.docs`, `a.commit`, current merge reworded before push |
| `/prepare_release_notes` | `version.txt`, git history | `a.md`, `version.txt` summary, `CHANGELOG.md` |
| `/prepare-release` | `main`, integration, or an isolated effort branch | collection feature returned to its umbrella-slug integration branch plus the next handoff, or standalone/full release artifacts and one `chore(release): prepare` commit |

`/update-merge-commit-msg` runs immediately after a feature merge into its
integration branch or any no-fast-forward merge into `main`. The merge must still be the
current commit, and the target branch must not be pushed or used for later
integration work first. Rewording a historical merge requires a separate
history-repair plan.

## 🛠️ Support skills

| Skill | Purpose |
| --- | --- |
| `/groundhog` | the ghog fixing loop: walk, fix what the report names, walk again |
| `/split-large-file` | split an over-budget file into single-responsibility files |
| `/audit-application` | audit source code for performance, security, readability, and maintainability findings |
| `/review-and-update-project-docs` | re-align README, architecture docs, and existing `wiki/` or `docs/wiki/` Diataxis roots with code or a Git range |
| `/write-release-notes-summary` | draft release notes from conventional commit subjects |
| `git-history-report` | build the standalone commit-history dashboard |
| `activity-report` | French activity report from commit messages and md diffs |
| `/isolate-logos` | split an AI-generated logo sheet into named opaque and transparent PNG assets |
| `/install-sensitive-git-hooks` | install, repair, or verify shared/local sensitive pre-commit and commit-msg protection in the current repository |
| `/sanitize-git-history` | automatically run the contextual history scanner, settle confidential-term rules, then optionally rewrite with git filter-repo |
| `prepare_release_plan.bat` | internal read-only single-source tool called automatically by `/prepare-release`; its standalone interface supports diagnostics, while the skill guards empty integration ranges and explains unsupported revert, multi-topic, and non-contiguous paths |

Independent review mode adds a shared `review-requestor` coordinator plus
family-specific specification and code requestors and reviewers. The
`review-status-command` skill reports all active exchanges after bounded
migration preflight without resuming one. Their host locations, command
prefixes, delegation targets, and coverage gaps are listed in the
[independent review mode contract](independent-review-mode-contract.md#host-adapter-matrix).

## 🔗 Chaining behavior of the writing skills

`/write-requirement`, `/write-design` and `/write-plans` each end by
running `pw skill --after-write requirement`, `--after-write design`, or
`--after-write plan`, respectively, then running the
`/review-ask-questions` it prints. This explicit writer event prevents
settled-looking text from skipping review; pass `stop here` in the argument to
hold the chain and read the document first.
`/consolidate-then-review-ask-questions` first resets the index, commits only
the answered document with the group-commit template, and verifies an empty
index. It then performs the fold. When the document settles, it stages every
remaining path, runs the authorized `group-commits-msg` continuation without a
second menu, and requires an empty porcelain status before bare `pw skill`.
`/implement-step`, `/implementation-check` and
`/implement-missing-step` chain through `pw handoff` instead, and
`/group-commits-msg` closes the chain at the commit gate with
`pw skill --after-commit <x>`. `/split-and-define` and feature-mode
`/prepare-release` use `pw skill --after-merge <umbrella-draft>` as the ordered
collection checkpoint.

## 📌 Fixed sentences and stops worth knowing

- `/implementation-check` opens with exactly
  `Yes. Step N has been fully implemented.` or
  `No. Step N has NOT been fully implemented.` — `pw` routes on that line. The
  final successful check also changes an associated umbrella row from
  `pending` to `completed` and records its requirement and validation paths.
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
