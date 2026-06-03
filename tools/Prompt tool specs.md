# Prompt tool specs

## Purpose of the prompt tool

I need a tool able to copy in the clipboard a prompt that I can use for a specific task done by a LLM.

Each call must follow a workflow and propose either to repeat the prompt of the current step, or a choice of the next steps to do, in order to generate their prompt.

## Scope and runtime constraints

That tool will be in python, like all other tools in the tools/ folder, and will be able to find back its project root (the one containing the .git folder), like the other tools are already doing.

### Implementation constraints inherited from the tools package

The tool follows the same house style as the other `tools/` scripts: Python 3.13, `from tools import find_project_root` to locate the root (with a `--root` override), git read through `subprocess` with `shutil.which("git")`, `argparse` for arguments, message-only logging to stdout, a `# eof` final line, and unit tests that reach the repo 100% coverage gate. It adds `questionary` as its one runtime dependency for the interactive menu (Q08, Q12); that interactive call is isolated in a thin wrapper so it can be excluded from coverage like `tools/uv_run.py`, keeping the rest at 100%.

### Prompt output and clipboard fallback

The generated prompt is copied to the clipboard with PowerShell `Set-Clipboard`, the same mechanism as `tools/group_commit_message_prompt.py` (Q05). The tool also always writes the prompt to `a.prompt.txt` at the project root, whatever the clipboard state, so there is a stable copy to read back. When the clipboard write fails (headless or remote session), the tool prints the prompt to stdout and warns that the clipboard was unavailable. The target host is mostly Windows, where the clipboard is normally present, so the file and stdout paths act as a safety net.

## Core concepts and glossary

- General topic: the subject a prompt works on, derived from a draft file (see [General topic resolution](#general-topic-resolution)).
- Draft: a `docs\draft.vX.Y.Z.<topic>.md` file that names a general topic.
- Prompt: the clipboard text generated for a step, with a fixed header, a body, and a `Context:` section (see [Prompt format](#prompt-format)).
- Step: one entry of the workflow, mapped to an instruction file (see [Workflow step sequence](#workflow-step-sequence)).
- Prompt memory: the `a.prompt_memory` file at the project root that persists the branch, the chosen general topic, and the current step (see [The a.prompt_memory file](#the-aprompt_memory-file)).

## Prompt format

Each generated prompt has three parts (Q09):

- a header line: `Follow the instructions from <prefix>/instructions/<instruction>.md and do the following:`, where `<instruction>` is the step instruction file and `<prefix>` is computed as described below (Q10), and the colon and the blank line that follow it are described in [Blank lines between prompt parts and the do-the-following colon](#blank-lines-between-prompt-parts-and-the-do-the-following-colon);
- a per-step body that states the step intent and reminds the LLM which previous documents the step builds on (see [Per-step prompt content](#per-step-prompt-content));
- a trailing `Context:` section.

### Header path prefix

The `<prefix>` is the path from the project root to the llm-shared directory, which is the parent of this `tools/` folder (Q10). When the project root is llm-shared itself, the prefix is `instructions/`; in the standard submodule layout it is `llm-shared/instructions/`, and `llm-shared` is the default sub-folder name when the tool runs from a consuming repository.

### Trailing context section of each prompt

Each prompt is concluded by a "Context:" section, which repeats the vX.Y.Z and general topic name, and invites the LLM to read the draft (when writing a requirement like a feature or an issue), or to read the draft and the requirement (when writing a design), or to read the draft, the requirement and the design (when writing plans, implementing or preparing release notes). The exact list of documents per step is given in [Per-step prompt content](#per-step-prompt-content).

## General topic resolution

A prompt works on a general topic, and a general topic is derived from a draft found in the docs folder (or docs/vX.Y.Z). For instance: docs\draft.v9.8.0.resources_isolation.md means the general topic is "resources isolation".

### Draft detection on the current branch

The only draft(s) that should be used are the ones currently modified (git status) or created since the start of the current branch (do not use git --since, but rather look for the first commit which does belong to more than the current branch, and use the previous one as a starting point for the current branch). Any draft file created (in docs or any docs/v.X.Y.Z) since the start of the current branch should be considered as a general topic.

A draft is relevant only when it is modified in the working tree (git status) or committed on the current branch since the branch start; drafts that are neither modified nor committed on the current branch are ignored even when they exist in the repo (Q07). On the default branch, where there is no separate branch start to anchor against, the tool falls back to the drafts modified in the working tree.

### Choosing among several drafts

If you have several drafts, you should propose to choose one of them as the general topic for the prompt. If there is only one draft, you should use it as the general topic for the prompt. Once a choice is done, persist it in a (project root folder)/a.prompt_memory file, so that the next time the tool is used, it can directly propose to continue with the same general topic, or to choose another one if there are several.

### Matching documents to the general topic

A requirement, design or plan is tied to the general topic when its file name shares the same `vX.Y.Z` version and the same `<topic>` slug prefix as the originating draft (Q02). For example, `docs\draft.v9.8.0.resources_isolation.md` matches `docs\feature-request.v9.8.0.resources_isolation.md`, `docs\design.v9.8.0.resources_isolation.md` and `docs\plan.v9.8.0.resources_isolation.md`. Because the split-and-define step can produce several requirements for one topic, a sub-topic file such as `docs\design.v9.8.0.resources_isolation_sub_topic.md` also matches, as long as it keeps the version and the topic slug as a prefix. The match applies to feature-request, issue, design and plan files; draft files are only used to derive the version and topic, never matched against.

### Selecting the most recent related document

When several files match the topic (for example two designs, or several requirements after split-and-define), the tool picks the one with the most recent filesystem modification time (Q01). The version and topic are already fixed by draft detection, so recency only breaks ties between same-topic files, and modification time is the rule that also covers files not yet committed.

## Workflow step sequence

The possible next steps that must be proposed, in sequence, and memorized in the a.prompt_memory file, are listed below. Each row carries the precondition that makes the step available.

| # | Instruction | Precondition |
| --- | --- | --- |
| 1 | `split-and-define.md` or `write-requirement.md` | start of the workflow |
| 2 | `review-ask-questions.md` | previous step was `write-requirement.md`, for the most recent feature or issue related to the general topic |
| 3 | `consolidate-then-review-ask-questions.md` | "Open questions" detected in the most recent feature or issue related to the general topic (Q06) |
| 4 | `write-design.md` | at least `review-ask-questions.md` was done, and "Open questions" is not detected in the most recent feature or issue related to the general topic (Q06) |
| 5 | `review-ask-questions.md` | previous step was `write-design.md`, for the most recent design related to the general topic |
| 6 | `consolidate-then-review-ask-questions.md` | "Open questions" detected in the most recent design related to the general topic, on the most recent design related to the general topic |
| 7 | `write-plans.md` | at least `review-ask-questions.md` was done, and "Open questions" is not detected in the most recent design related to the general topic |
| 8 | `implement-step.md` | `write-plans.md` was done |
| 9 | `implementation-check.md` | `implement-step.md` was done |
| 10 | `group-commits-msg.md` | `implementation-check.md` was done |
| 11 | `implement-step.md` or `prepare-release-notes.md` | `group-commits-msg.md` was done |

## Per-step prompt content

The body line and the Context documents for each step are fixed as below (Q13). The body names the prior documents by role; the Context section turns those roles into concrete file paths resolved for the current topic and version (see [Matching documents to the general topic](#matching-documents-to-the-general-topic)). This per-step data is static, and "git status" is a non-file role resolved from the working tree. It lives in a JSON file next to the tool, `tools/prompt_workflow.steps.json`, keyed by step number, with one or more alternatives per step (Q14).

| Step | Instruction | Body intent line | Context documents |
| --- | --- | --- | --- |
| 1 | split-and-define.md | Split and define the features and issues for this topic, based on the draft. | draft |
| 1 | write-requirement.md | Write the feature-request or issue for this topic, based on the draft. | draft |
| 2 | review-ask-questions.md | Review the most recent feature or issue and ask open questions, based on the draft and the requirement. | draft, requirement |
| 3 | consolidate-then-review-ask-questions.md | Consolidate the answers in the most recent feature or issue, then review and ask new questions, based on the draft and the requirement. | draft, requirement |
| 4 | write-design.md | Write the design for this topic, based on the draft and the requirement. | draft, requirement |
| 5 | review-ask-questions.md | Review the most recent design and ask open questions, based on the draft, the requirement and the design. | draft, requirement, design |
| 6 | consolidate-then-review-ask-questions.md | Consolidate the answers in the most recent design, then review and ask new questions, based on the draft, the requirement and the design. | draft, requirement, design |
| 7 | write-plans.md | Write the implementation plan and validation plan, based on the draft, the requirement and the design. | draft, requirement, design |
| 8 | implement-step.md | Implement step {x} "{title}" of the plan "{plan_doc}", based on the design and the plan. | draft, requirement, design, plan |
| 9 | implementation-check.md | Check step {x} "{title}" implementation, based on the plan "{plan_doc}" and the validation plan. | draft, requirement, design, plan, validation plan |
| 10 | group-commits-msg.md | Group the changed files and write one conventional commit message per group. | plan, current git status |
| 11 | implement-step.md | Implement step {x} "{title}" of the plan "{plan_doc}", based on the design and the plan. | draft, requirement, design, plan |
| 11 | prepare-release-notes.md | Prepare the release notes for this version, based on the plan and the git history since the last tag. | draft, requirement, design, plan |

## Per-step interaction

For each step, the tool shows an interactive menu with arrow-key selection and ESC to exit (Q08), using the `questionary` library (Q12), offering:

- to repeat the prompt of the current step
- to choose the next step among the possible ones (if any)

When there is no current step yet (start of the workflow), only the next steps are shown; ESC exits the tool at any point. The `questionary` call is isolated in a thin wrapper so the rest of the logic stays unit-testable and the wrapper can be excluded from coverage like `tools/uv_run.py`.

## The a.prompt_memory file

### Contents and format of the memory file

The memory file at the project root keeps the workflow context as `key=value` lines grouped in sections (Q03), which stay easy to read and to hand-edit. It records the branch, the resolved version, the topic slug, and the current step as a number plus its chosen instruction (the step number is needed because the same instruction recurs at different steps); during the implement cycle it also records the plan step `x` (Q17). The branch start is not stored: it is recomputed each run (Q18). No step history is stored: the step preconditions are re-derived from the documents on disk, from git, and from this `step` value (see below), so the file stays small. A minimal shape:

```ini
[topic]
branch=feature/resources-isolation
version=v9.8.0
topic=resources_isolation
step=4
instruction=write-design.md
```

### Step state re-derived from the documents on disk

Step preconditions are checked against two sources: the documents present on disk, and the persisted `step` value for the steps that create no new document (Q04, Q11). The mapping is:

- "previous step was write-requirement.md" / "write-design.md was done": the matching requirement (`feature-request.` or `issue.`) or `design.` document exists for the topic.
- "at least review-ask-questions.md was done": known from the persisted `step`, since review and consolidate create no new document; it is backed by the "Open questions" state of the requirement or design.
- "Open questions" gate: the relevant requirement or design document is read and checked for a `## Open questions` line.

The document-producing steps (requirement at step 1, design at step 4, plan at step 7) and the "Open questions" gates are derived from the documents on disk. The review and consolidate steps (2, 3, 5, 6) take their state from the persisted `step` value (Q04, Q11). The implement, check and commit cycle (steps 8 to 10) is re-derived from git and the validation plan as the plan step `x`, which supersedes Q11 there (Q21); see [Implement-validate-group commit message](#implement-validate-group-commit-message). When the persisted state disagrees with what the documents or git show, the tool warns and trusts the derived state.

### Startup validation logic for the memory file

If a.prompt_memory file already exists, the tool should check if the branch memorized in it is still the current branch, and if the general topic is still relevant (the draft file still exists and is still modified or created since the start of the branch). If not, it should propose to choose another general topic among the relevant ones, or to exit saying that no general topic is relevant anymore or detected. If the branch and general topic are still relevant, it should propose to continue with the same general topic, or to choose another one among the relevant ones, or to exit (ESC to exit).

## Design decisions

The table summarizes the choices made from the answered questions Q01 to Q37, the section that carries each one, and the alternatives that were dropped.

| Question | Decision | Integrated in section | Main argument | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q01 | Pick the most recent matching document by filesystem mtime | Selecting the most recent related document | Version and topic are already fixed by draft detection; mtime also covers uncommitted files | Highest version token; git commit date |
| Q02 | Match documents by shared version and topic slug prefix | Matching documents to the general topic | Groups all requirement, design and plan files of one topic, including sub-topics | Slug only; version only; explicit paths in memory |
| Q03 | Store the memory as key=value lines in sections | Contents and format of the memory file | Easy to read and hand-edit; the file stays small with no step history | JSON object; single topic line |
| Q04 | Re-derive step state from the documents on disk | Step state re-derived from the documents on disk | Always matches reality, survives a deleted memory file | Full step history; last step only |
| Q05 | Set-Clipboard, always write a.prompt.txt, stdout on failure | Prompt output and clipboard fallback | Keeps the prompt reachable in every environment | Clipboard only with error; file only |
| Q06 | Rows 3 and 4 gate on the most recent requirement, not the design | Workflow step sequence | Only a requirement exists between the requirement review and write-design | Keep the design wording; drop the early consolidate |
| Q07 | Use drafts modified or committed on the current branch; default branch falls back to working-tree drafts | Draft detection on the current branch | Keeps the focus on the current work, avoids unrelated drafts | Error on the default branch; treat all drafts |
| Q08 | Interactive TUI menu with arrow keys and ESC | Per-step interaction | Matches the "ESC to exit" affordance the spec asks for | Numbered stdin menu; non-interactive flags |
| Q09 | Three-part prompt: header, per-step intent-and-reading body, Context | Prompt format | Reminds the step intent and the documents to read | Empty body; full instruction inlined |
| Q10 | Prefix is the path from the project root to the llm-shared directory, default `llm-shared` | Header path prefix | Yields a path the LLM can open in both layouts | Literal `llm-shared/`; configurable flag |
| Q11 | Steps 8 to 11 trust the persisted `step` (8 to 10 superseded by Q21); steps 1 to 7 stay document-derived | Step state re-derived from the documents on disk | Gives the doc-less tail a notion of progress without git guessing | Git signals; track nothing |
| Q12 | Use `questionary` for the interactive menu | Per-step interaction | Smallest select API with arrow keys and a clean None-on-ESC exit, runs on Windows | prompt_toolkit directly; InquirerPy |
| Q13 | Per-step body names prior docs by role; Context resolves them to file paths | Per-step prompt content | Satisfies Q09 without duplicating the path list | Body intent only; paths inlined in the body |
| Q14 | Store the per-step body and Context roles in a JSON file keyed by step number | Per-step prompt content | Editable without code; expresses alternatives and role lists cleanly | INI; in-code dict |
| Q15 | Read the validation plan `Analysis of Step N` status line (Yes/No) for step state | Deriving the plan step x | The validation template already carries the per-step Yes/No marker | New section; non-empty heuristic; git-only |
| Q16 | Complete the group-commits prompt to require a `docs(<topic>): record step x validation` final commit | Implement-validate-group commit message | A commit subject git log can match ties each step to the log without editing the instruction | Step trailer; no grep; slug count |
| Q17 | Keep 8 to 11 as the internal instruction selector; add a plan step `x` the user sees and the body names | Implement-validate-group commit message | Names the step without overloading the menu counter; `x` stays git-reconciled | Collapse to `x` only; never store `x` |
| Q18 | Recompute the branch start each run; do not cache it | Deriving the plan step x | Sub-second rev-list avoids rebase and amend staleness | Cache with ancestor check; cache by branch name |
| Q19 | Initial `x` is the first `Analysis of Step` number; last step committed proposes release notes | Deriving the plan step x | The plan owns its step numbering and count | Hardcode `x=1`; section-presence end; read the plan step list |
| Q20 | Propose the check on any changed tracked file outside `docs/` | Proposing the prompts for step x | Works whatever the code folder is named | Hardcode `src/`; plan file list; configurable folder |
| Q21 | Re-derive steps 8 to 10 from git and the validation plan; supersede Q11; memory is a cache | Step state re-derived from the documents on disk | One consistent rule for the cycle | Warn-only cross-check; keep both counters |
| Q22 | List the staged files in the body as porcelain `XY path` lines, the `git status --short` shape, inside a fenced log block | Embedding the staged file list in the prompt body | Matches the example and the commit template; the status letter signals add, modify or delete | Paths only; `git diff --cached --name-status` tab form |
| Q23 | List the staged set read after the optional `git add -A`, every staged file whatever its folder, only the staged ones | Embedding the staged file list in the prompt body | The printed list then matches the `git diff --cached` the instruction runs, for both variants | Always all changes; only index-staged; filter by folder |
| Q24 | Drop the `git_status` Context role from step 10; its Context stays `["plan"]` | Embedding the staged file list in the prompt body | The body already carries the concrete list, so a Context entry would only restate it | Keep `git_status`; put the list under Context |
| Q25 | Empty `a.commit` for both commit variants at prompt-delivery time | Emptying a.commit before delivering the commit prompt | The grouping always rewrites `a.commit`, so one reset rule clears stale groups | Only the `(git add -A)` variant; also wrap or validate |
| Q26 | Name the check body by step number, and add the step title so the check prompt reads on its own | Naming the implement and check steps by their plan number | Matches the check instruction's "check step x" shape; the title makes the check prompt self-describing | Number only like implement; no title |
| Q27 | Implement body named the step by number only; superseded by Q33, which adds the title and the plan document | Naming the implement and check steps by their plan number | Was the first wording; the Context resolved the plan path | of the `<topic>`; inline the title in the body |
| Q28 | One blank line only between the three prompt parts; Context document lines stay grouped | Blank lines between prompt parts and the do-the-following colon | The blank lines mark the three-part boundary; spacing the context list would blur it and lengthen the prompt | A blank line between each Context line |
| Q29 | Only the check prompt read one plan heading for the title; superseded by Q33, which extends that read to the implement prompt and the menu | Naming the implement and check steps by their plan number | The check title was the single needed read; Q33 broadened it | Never read the plan at all; read it to validate step existence |
| Q30 | Read the check `{title}` from the plan `### Step N.` heading, loose-matched on `Step <x>`, check prompt only, number-only fallback | Naming the implement and check steps by their plan number | The plan step heading is the one place the title is written; reuses the `Analysis of Step N` loose match (Q15); keeps Q29 elsewhere | Read the title from the validation plan; drop the title and walk back Q26 |
| Q31 | On the check fallback, drop the `"{title}"` segment and render `Check step {x} implementation, ...`, with no empty quotes | Naming the implement and check steps by their plan number | A bare number reads cleanly; empty quotes would look like a missing value | Leave empty `""`; keep the number-only check body always |
| Q32 | The title grab tolerates a `.`, `:` or `-` separator between the step number and the title | Naming the implement and check steps by their plan number | Plans vary the separator; matches the loose `Analysis of Step N` style | Require the exact `Step N.` period form |
| Q33 | Reverse Q27 and Q29: read the title and plan once with `read_step_title` and reuse them for the menu introduction, the implement body and the check body | Naming the implement and check steps by their plan number | The requested wording; one shared plan-heading read the check already pays | Keep the implement body number-only; read per prompt |
| Q34 | Title-missing fallback for the implement body and the menu introduction: drop the `"{title}"` segment, like Q31 | Naming the implement and check steps by their plan number | One drop rule across the menu, implement and check; no empty quotes | An `(untitled)` placeholder |
| Q35 | Plan-document-missing fallback: drop the `"{plan_doc}"` segment, degrading to the number-only shape | Naming the implement and check steps by their plan number | Never renders an empty path or `None`; an edge guard | Name the validation plan instead |
| Q36 | Print the menu introduction as its own stdout line before `menu.select`; the menu message is unchanged | Proposing the prompts for step x | Matches the layout; keeps the wording unit-tested outside the `questionary` wrapper | Fold the introduction into the questionary message |
| Q37 | One introduction before the whole cycle menu (implement, check, commit); title and plan doc in the implement and check bodies only; commit body and release prompt unchanged | Proposing the prompts for step x | Follows the examples; the commit body is a file list and release has no step `x` | Title and plan in the commit body; an introduction for release |

## Implement-validate-group commit message

Once the plan and its validation plan exist (write-plans done, step 7), the implement, check and commit cycle (workflow steps 8 to 10) is driven by a plan step `x` re-derived from git and the validation plan, not by the persisted workflow step (Q21 supersedes Q11 for steps 8 to 10). The workflow step number stays internal; the user only ever sees the plan step `x` (Q17).

### Deriving the plan step x

The plan step `x` is recomputed at startup on every run:

1. Read the validation plan `docs/plan.vX.Y.Z.<topic>.validation.md`. Each plan step carries an `Analysis of Step N` heading whose next non-empty line starts with `Yes` (step N is implemented and verified) or `No` (Q15). The exact heading wording differs between sources — `### Analysis of Step N implementation state` from [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md) and `## Analysis of Step x Implementation` from [`implementation-check.md`](../instructions/implementation-check.md) — so the tool matches the heading loosely on `Analysis of Step <N>` and the status line on a leading `Yes`/`No`, both case-insensitive.
2. `x` is the number of the last `Analysis of Step N` section whose status line starts with `Yes`. When no section is `Yes` yet, `x` is the number of the first such section, so the plan owns its own numbering (it may start at 0 or 1) (Q19).
3. Compute the branch start fresh each run as the fork point (the single `git rev-list`, not stored in the memory file) (Q18). Run `git log --grep "record step x validation"` between the branch start and HEAD. When that per-step validation commit exists, step `x` is already committed, so move `x` to the next plan step; otherwise keep `x` (Q16).

### Proposing the prompts for step x

Once `x` is fixed, the menu offers, labelled by the plan step `x`:

- `implement-step.md` for step `x` (always).
- `implementation-check.md` for step `x` as well, when any tracked file outside `docs/` is changed in `git status` (Q20).
- `group-commits-msg.md` as well, when the `Analysis of Step x` status line starts with `Yes` (step `x` is verified and ready to commit). The commit prompt is offered in a cached and a git-add-A variant chosen from the working-tree state:
  - cached files only: a `group-commits-msg.md (cached)` prompt.
  - both cached and non-cached files: both a `(cached)` and a `(git add -A)` prompt.
  - non-cached files only: only the `(git add -A)` prompt.
- The `(git add -A)` prompt makes the tool run `git add -A` before generating the prompt, so the prompt reads every change as staged; the `(cached)` prompt stages nothing and the prompt reads only the already-staged files.

Before any non-terminal cycle menu (the menu that offers the implement, check and commit prompts for step `x`), the tool prints one introduction line, `Regarding step {x} ("{title}") from {plan_doc}:`, as its own stdout line above the menu, then shows the menu choices unchanged (Q33, Q36, Q37). The `{title}` and `{plan_doc}` are the values the bodies use (see [Naming the implement and check steps by their plan number](#naming-the-implement-and-check-steps-by-their-plan-number)), with the same drops when missing: `Regarding step {x} from {plan_doc}:` with no title (Q34) and `Regarding step {x}:` with no plan document (Q35). The terminal menu, which offers only the release-notes prompt, shows no introduction, since it names no plan step (Q37).

When the validation plan is among the files to be committed, the generated group-commits prompt is completed with the requirement that the final commit be `docs(<topic>): record step x validation` (the tool appends this to the prompt it generates; the `group-commits-msg.md` instruction file itself is not changed) (Q16). That commit is what the next run finds with `git log --grep "record step x validation"` to advance `x`.

After the validation commit, the next run re-derives `x` and proposes `implement-step.md` for the next plan step, or `prepare-release-notes.md` when `x` was the last plan step (Q19).

### Memory and ESC for the cycle

The memory file may still record the plan step `x` and the workflow instruction, but the state is re-derived from git and the validation plan at startup; on a mismatch the tool warns and trusts the git-derived state, overriding the memory (Q17, Q21).

ESC must exit without generating any prompt. The current `questionary` menu does not act on ESC; making ESC cancel needs a key binding on the underlying prompt, added with the code change.

## Completing the group-commits prompt with the staged file list and a.commit reset

The group-commits prompt of the implement cycle (workflow step 10, the `group-commits-msg.md` action) gets two additions on top of its [Per-step prompt content](#per-step-prompt-content) entry: the body now carries the list of files to commit, and the tool empties `a.commit` before delivering the prompt. Both apply to the `(cached)` and the `(git add -A)` variants described in [Proposing the prompts for step x](#proposing-the-prompts-for-step-x).

### Embedding the staged file list in the prompt body

The [`group-commits-msg.md`](../instructions/group-commits-msg.md) instruction groups the "files listed in the prompt", but the bare body line lists nothing. The body today is:

`Group the changed files and write one conventional commit message per group.`

The completed body states the count and lists the staged files (Q22). The delivered body reads `... per group for those 26 files:` followed by a blank line and a ```log block such as:

```log
M  docs/plan.v9.8.0.resources_isolation.validation.md
M  src/pdfss/adapters/__init__.py
A  src/pdfss/adapters/job_shm_layout.py
```

Each line is the two-character `git status --porcelain` code, a space, then the repo-relative path, the same shape the example shows and the same shape `git status --short` prints (Q22). The block is fenced with ```log to match the commit blocks of [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md), and a rename collapses to its target path, the rule `_porcelain_path` already applies.

The list is the staged set, produced by `git status --short` run at the project root that `find_project_root` resolves — the repository the tool is invoked in, not the llm-shared folder that holds the tool — and read at prompt-build time after the optional `git add -A` (Q23). It lists every staged file whatever its folder, `docs/` changes included and never restricted to a subfolder such as `src/`, and only the staged files: the `(cached)` variant lists the already-staged files, and the `(git add -A)` variant, which stages everything first, lists every change as staged. So the printed list always agrees with the `git diff --cached` the instruction tells the LLM to run. The count `N` is the length of that list; because the menu only offers a commit prompt when step `x` is verified and there is at least one staged or non-staged change, `N` is always at least 1.

Since the body now carries the list, the `git_status` Context role is dropped from the step-10 alternative, leaving its Context at `["plan"]` (Q24). The validation-commit appendix of [Proposing the prompts for step x](#proposing-the-prompts-for-step-x) (the `docs(<topic>): record step x validation` requirement) is unchanged.

The body stays in `tools/prompt_workflow.steps.json` as a static template with `{n}` and `{files}` placeholders, interpolated when the prompt is built the same way `{x}` already is (Q14), so the wording keeps living in the JSON file rather than in code.

### Emptying a.commit before delivering the commit prompt

The `group-commits-msg.md` instruction writes the grouped commit messages into `a.commit` at the project root. To start each grouping from an empty file, the tool empties `a.commit` when, and only when, a group-commits prompt is generated, for either variant (Q25): it truncates the file to size 0, creating it empty when it does not exist and clearing its content when it does, and never deletes it. This is the same write-empty step `oqm --create` uses for its companion file (`Path.write_text("", encoding="utf-8")`). No other prompt touches `a.commit`.

## Naming the implement and check steps by their plan number

The cycle prompts (workflow steps 8, 9 and 11) name the plan step by its number, its title and the plan document, so each prompt reads on its own. The title and the plan path are read once per run with `read_step_title` (the `### Step <x>` heading of the plan, Q30, Q32) and reused by the menu introduction, the implement body and the check body (Q33). This amends the number-only implement body of Q27 and the "implement never reads the plan" rule of Q29: the implement prompt now reads the same plan heading the check prompt already reads.

The implement body (steps 8 and 11) reads `Implement step {x} "{title}" of the plan "{plan_doc}", based on the design and the plan.` (Q33). The check body (step 9) reads `Check step {x} "{title}" implementation, based on the plan "{plan_doc}" and the validation plan.` (Q26). Here `{x}` is the plan step the menu shows (see [Proposing the prompts for step x](#proposing-the-prompts-for-step-x)), `{title}` is the trailing text of the matched `### Step <x>` heading in the `## Numbered steps for vX.Y.Z <topic>` section of `docs/plan.vX.Y.Z.<topic>.md` (loose match, a `.`, `:` or `-` separator tolerated, Q30, Q32), and `{plan_doc}` is the repo-relative path of the plan document, the same path the `Context:` section resolves. The plan document is repeated between the body and the `Context:` section on purpose, for clarity.

Both bodies stay in `tools/prompt_workflow.steps.json` as static templates carrying `{x}`, `{title}` and `{plan_doc}`, interpolated when the prompt is built the same way `{n}` and `{files}` already are (Q14). Two segment-drop fallbacks keep the text clean when a value is missing:

- No `### Step <x>` heading matches, so `{title}` is missing: the `"{title}"` segment and its leading space are dropped (Q31 for the check body, Q34 for the implement body and the menu introduction). The check body then reads `Check step {x} implementation, based on the plan "{plan_doc}" and the validation plan.` and the implement body `Implement step {x} of the plan "{plan_doc}", based on the design and the plan.`, with no empty quotes left behind.
- No plan document is resolved, so `{plan_doc}` is missing (and `{title}` with it): the `"{plan_doc}"` segment and its leading space are dropped too (Q35), degrading to `Implement step {x} of the plan, based on the design and the plan.` and `Check step {x} implementation, based on the plan and the validation plan.`. In practice the plan and the validation plan are matched together, so this is an edge guard.

This matches the `implement-step.md` and `implementation-check.md` instructions, which already expect prompts shaped like "implement step 2 of the ..." and "check step 2 implementation of ...".

## Blank lines between prompt parts and the do-the-following colon

The header line ends with a colon. It reads `Follow the instructions from <prefix>/instructions/<instruction>.md and do the following:`, not `... and do the following` (see [Prompt format](#prompt-format)). Any prompt that opens a block with the phrase "do the following" closes that phrase with a colon the same way.

The three prompt parts (header, body, and `Context:`) are separated by one blank line each. The blank line after the header is the extra line for readability that the colon opens, and the blank line before `Context:` keeps the body and the context apart. Inside the `Context:` section the document lines stay grouped, with no blank line between them, so the context reads as one block (Q28). A delivered prompt then reads:

```text
Follow the instructions from <prefix>/instructions/<instruction>.md and do the following:

<body>

Context:
...
```

For the step-10 body, which already carries the count, the colon and the fenced `log` block of staged files (see [Embedding the staged file list in the prompt body](#embedding-the-staged-file-list-in-the-prompt-body)), the same one-blank-line rule applies around that block: one blank line between the body line and the `log` block, and one blank line between the block and `Context:`.
