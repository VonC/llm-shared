# v0.1.0 pw-handoff design -- the prompt-workflow (pw) tool and its handoff subcommand

This is the design for the `pw` prompt-workflow tool. Decisions Q01 to Q55 cover the base tool -- draft detection, the workflow steps, and the interactive implement cycle -- and decisions Q56 to Q64 cover the v0.1.0 handoff that lets the cycle advance without the menu (see [Handoff prompts to continue the implement cycle without the menu](#handoff-prompts-to-continue-the-implement-cycle-without-the-menu)). The draft naming the need is [`draft.v0.1.0.pw_handoff.md`](draft.v0.1.0.pw_handoff.md).

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

If you have several drafts, you should propose to choose one of them as the general topic for the prompt. If there is only one draft, you should use it as the general topic for the prompt. Once a choice is done, persist it in a (project root folder)/a.prompt_memory file, so that the next time the tool is used on the same branch it reuses the same general topic without asking again, the branch lock of [Locking the topic to the branch](#locking-the-topic-to-the-branch) (Q53).

### Locking the topic to the branch

Once a general topic is recorded in `a.prompt_memory`, the next run on the same branch reuses it without showing the topic menu, as long as the memory still matches one detected draft by branch, version and slug (Q53). The tool prints a one-line notice naming the locked topic, so the skipped menu is never silent:

```text
Topic v9.9.0 cleanup_fixes locked to branch cleanup_fixes; run pw --pick to choose another.
```

A single detected draft is still used directly, since there is nothing to lock against. The lock releases on its own when the memorized draft no longer matches the detected ones — a different branch, a removed draft, or a new version — and the menu comes back. To switch topics while the lock holds, run `pw --pick`: it reopens the menu with the locked topic listed first and pre-highlighted, and the new choice becomes the next lock. The flag has no effect when a single draft leaves nothing to choose.

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
| 8 (missing) | implement-missing-step.md | Implement the missing work of step {x} "{title}" of the plan "{plan_doc}", focusing on the "Missing work for Step {x}" section of the validation plan, based on the design, the plan and the validation plan. (plus the line-budget sentence; see [Implementing missing work when a step validation reads No](#implementing-missing-work-when-a-step-validation-reads-no)) | draft, requirement, design, plan, validation plan |
| 9 | implementation-check.md | Check step {x} "{title}" implementation, based on the plan "{plan_doc}" and the validation plan. | draft, requirement, design, plan, validation plan |
| 10 | group-commits-msg.md | Group the changed files and write one conventional commit message per group for those {n} files, per step {x} ("{title}") evolutions of the implementation plan "{plan_doc}": | draft, requirement, design, plan, validation plan |
| 11 | implement-step.md | Implement step {x} "{title}" of the plan "{plan_doc}", based on the design and the plan. | draft, requirement, design, plan |
| 11 | prepare-release-notes.md | Prepare the release notes for this version, based on the plan and the git history since the last tag. | draft, requirement, design, plan |

## Per-step interaction

For each step, the tool shows an interactive menu with arrow-key selection and ESC to exit (Q08), using the `questionary` library (Q12), offering:

- to choose the next step among the possible ones (if any)
- to repeat the prompt of the current step

The rows are listed higher step number first (Q54): after finishing a step the usual move is forward, so the likeliest choice is the pre-highlighted top row, and repeating the current step stays one arrow press away. The same rule orders the implement cycle menu, with one exception for the implement-missing entry (Q55; see [Proposing the prompts for step x](#proposing-the-prompts-for-step-x)). When there is no current step yet (start of the workflow), only the next steps are shown; ESC exits the tool at any point. The `questionary` call is isolated in a thin wrapper so the rest of the logic stays unit-testable and the wrapper can be excluded from coverage like `tools/uv_run.py`.

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

If a.prompt_memory file already exists, the tool should check if the branch memorized in it is still the current branch, and if the general topic is still relevant (the draft file still exists and is still modified or created since the start of the branch). If not, it should propose to choose another general topic among the relevant ones, or to exit saying that no general topic is relevant anymore or detected. If the branch and general topic are still relevant, the tool reuses the memorized topic without asking, the branch lock of [Locking the topic to the branch](#locking-the-topic-to-the-branch), and prints the lock notice (Q53); `pw --pick` reopens the menu to continue with another relevant topic or to exit (ESC to exit).

## Design decisions

The table summarizes the choices made from the answered questions Q01 to Q64, the section that carries each one, and the alternatives that were dropped.

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
| Q24 | Drop the `git_status` Context role from step 10; the document Context is later expanded by Q40 | Embedding the staged file list in the prompt body | The body already carries the file list, so a git-status entry would only restate it | Keep `git_status`; put the list under Context |
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
| Q37 | One introduction before the whole cycle menu (implement, check, commit); title and plan in the implement and check bodies; the commit body is named by Q38; release prompt unchanged | Proposing the prompts for step x | Follows the examples; release has no step `x` to name | An introduction for the release prompt |
| Q38 | Reverse Q37 for the commit body: name the step number, title and plan after the file count, reusing the shared read (Q33) | Completing the group-commits prompt with the staged file list and a.commit reset | The requested wording; the read is shared, so it costs nothing | Keep the commit body a bare file list |
| Q39 | Commit-body fallback: granular drops of the `("{title}")` and `of the implementation plan "{plan_doc}"` segments, like Q34 and Q35 | Completing the group-commits prompt with the staged file list and a.commit reset | One drop rule across every cycle prompt; the no-plan case is rare | Drop the whole clause back to the file list |
| Q40 | The step-10 Context lists the five check documents: draft, requirement, design, plan and the validation plan | Embedding the staged file list in the prompt body | The validation plan is relevant to the commit that records its step | The four implement documents; keep `["plan"]` |
| Q41 | Carry the plan step id as a `\d+[A-Za-z]*` string across the models and memory | Sub-step id representation and grammar | The id is text at every stage and round-trips to the `record step <id> validation` commit and grep | `int` plus a `suffix` field; a derived fractional number |
| Q42 | Read the id token as `\d+[A-Za-z]*` from the validation and plan headings | Sub-step id representation and grammar | Smallest pattern that matches `4` and `4A` and stops at the separator | `\d\S+` (skips a lonely `4`, swallows separators); `\d+[A-Za-z0-9]*` |
| Q43 | Order steps and sub-steps by document order | Sub-step ordering and granularity | `derive_x` already walks the parsed list in order; the plan is authored in running order | Sort by numeric part then suffix |
| Q44 | Treat each sub-step as first-class with its own `record step <id> validation` commit | Sub-step ordering and granularity | The validation plan analyses each sub-step on its own; the space-delimited grep keeps ids apart | Parent-covers-children single commit |
| Q45 | Key the parsed status by full id; current id is the last `Yes` in document order, advanced only past its validation commit | Detecting the current step among its sub-steps | Stops a sub-step `Not started` from hiding the parent `Yes`; keeps sub-steps addressable | Int-keyed OR-merge of same-number statuses |
| Q46 | Trigger the implement-missing body on the `Analysis of Step x` status line starting with `No` | Trigger and menu entry for the implement-missing body | Reuses the status line `derive_x` already reads; fires when the check has marked the step incomplete | `No` plus a non-empty missing-work section; offer both prompts |
| Q47 | Replace the implement entry with one relabelled `Implement missing for step <id>` | Trigger and menu entry for the implement-missing body | Matches "replace implement with implement missing"; one implement action per menu state | Add a second entry next to the plain implement |
| Q48 | Point the variant header at a new `implement-missing-step.md` that references `implement-step.md` and `split-large-file.md` | The implement-missing instruction file | A dedicated page names the implement-or-split (never reduce) choice by gap nature; body and Context still carry the per-step focus | Reuse `implement-step.md`, body and Context only |
| Q49 | Body names the `Missing work for Step {x}` section of the validation plan | The implement-missing body and its line-budget sentence | Points the LLM at the gap the check recorded; reuses the implement placeholders and drops | Generic "what is missing" phrasing |
| Q50 | Carry the split-large-file reminder as a standing conditional sentence in the body | The implement-missing body and its line-budget sentence | Matches the prompt need; no file scan, no second copy of the 650 threshold | Tool scans for over-650 files and adds it only then |
| Q51 | Context `draft, requirement, design, plan, validation_plan` for the variant | Context documents for the implement-missing body | The body points at the validation plan, so that file joins the reading list; reuses the check and commit set | Keep the four implement documents |
| Q52 | Apply the variant at workflow steps 8 and 11, keyed by the step status | Trigger and menu entry for the implement-missing body | A `No` step surfaces at either row; both share the implement body and title read | Only step 8 |
| Q53 | Auto-select the memorized topic on the same branch, `pw --pick` to reopen the menu | Locking the topic to the branch | Once chosen, the topic sticks per branch so the menu stops asking; the flag and the self-release on mismatch keep an escape hatch | Keep proposing the menu every run; a `locked=true` memory flag |
| Q54 | List menu rows higher step first: commit, check, implement in the cycle; next-step rows above the repeat row | Per-step interaction | After an implementation the usual next action is the check, then the commit, so the likeliest choice is the pre-highlighted top row | Workflow order with implement first; move the default cursor on an unchanged list |
| Q55 | Exception to Q54: the `Implement missing for step <id>` entry tops the menu when offered | Proposing the prompts for step x | Moving forward is best served when what was missing is no longer missing; a `No` step is never verified, so no commit row competes | Keep the strict descending order; drop the check row on a `No` status |
| Q56 | `handoff` subcommand `pw handoff <task> <x>` with the task and step as positionals | The handoff subcommand | Keeps the task and step together and leaves room for handoff options with no new flags on the main command | A1 `--handoff`/`--step` flag pair (two flags only meaningful together); A3 packed `task:step` token (buries the step in a string) |
| Q57 | Readable-word tokens, not step numbers or file names; `check` and the neutral `after-check` (full set in Q62) | The handoff subcommand | The caller names what it wants in plain words, not the hidden step counter (Q17) or a file name | B2 instruction stems (verbose, leak file names); B3 step numbers (the internal counter) |
| Q58 | pw auto-routes after the check: the caller hands off `after-check`, pw reads the status line and emits implement-missing on `No` or commit on `Yes` | Resolving the target and the step for a handoff; The three handoff transitions | One source of truth, the validation plan; the caller cannot mis-branch | C1 caller names the target with a pw guard (branch rule in two places); C3 no guard (a wrong call passes silently) |
| Q59 | Trust the handed step, validate it is a real `Analysis of Step <id>`, warn on a mismatch with the derived `x` | Resolving the target and the step for a handoff | The caller knows the step it just worked on; the check stops a typo, the warning surfaces drift | D2 always use the derived `x` (argument decorative); D3 no validation (empty prompt on a typo) |
| Q60 | Same delivery as the interactive run: `a.prompt.txt`, clipboard, then stdout fallback | Delivering and recording a handoff prompt | One path serves the calling LLM (reads `a.prompt.txt`) and a human at the terminal (clipboard) | E1 stdout plus file, no clipboard (drops the human convenience); E3 file only (an extra read step) |
| Q61 | Mirror the menu: the commit handoff stages `git add -A` and empties `a.commit`, every handoff writes `a.prompt_memory` | Delivering and recording a handoff prompt | The staged list and the empty `a.commit` are part of the commit prompt's contract; a consistent memory costs one write | F2 prompt-only (breaks the staged-list contract); F3 stage but skip memory (stale step until re-derived) |
| Q62 | Four handoff tokens, `check`, `after-check`, `implement-missing` and `commit`; the chain uses only `check` and `after-check`, the two direct words are a manual convenience | The handoff subcommand | Keeps the readable direct targets for a human at the terminal (Q60) while the chain stays mis-branch-proof on the two neutral words | S1 two tokens only (no direct manual call); S3 one post-check token (S1 renamed) |
| Q63 | Resolve the topic from the single draft or the branch lock; refuse with a `pw --pick` pointer when several drafts exist and none is locked | Resolving the topic without a menu | The per-branch lock covers the common case with no argument; a refusal beats a silent wrong-topic guess | P2 `--topic` argument (redundant with the lock); P3 auto-pick most recent draft (silent wrong topic) |
| Q64 | Ship the `handoff` subcommand plus a clear, detailed `## Handoff` section in each of the three cycle instructions (T1) | Wiring the handoff into the calling instructions | The automatic handoff happens only when the three instructions run the subcommand; the section names the call, its purpose, and to follow the returned prompt | T2 subcommand alone, wiring deferred; T3 spec guidance only (model must recall an unwritten step) |

## Implement-validate-group commit message

Once the plan and its validation plan exist (write-plans done, step 7), the implement, check and commit cycle (workflow steps 8 to 10) is driven by a plan step `x` re-derived from git and the validation plan, not by the persisted workflow step (Q21 supersedes Q11 for steps 8 to 10). The workflow step number stays internal; the user only ever sees the plan step `x` (Q17).

### Deriving the plan step x

The plan step `x` is recomputed at startup on every run:

1. Read the validation plan `docs/plan.vX.Y.Z.<topic>.validation.md`. Each plan step carries an `Analysis of Step N` heading whose next non-empty line starts with `Yes` (step N is implemented and verified) or `No` (Q15). The exact heading wording differs between sources — `### Analysis of Step N implementation state` from [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md) and `## Analysis of Step x Implementation` from [`implementation-check.md`](../instructions/implementation-check.md) — so the tool matches the heading loosely on `Analysis of Step <N>` and the status line on a leading `Yes`/`No`, both case-insensitive.
2. `x` is the id of the last `Analysis of Step N` section whose status line starts with `Yes`. When no section is `Yes` yet, `x` is the id of the first such section, so the plan owns its own numbering (it may start at 0 or 1) (Q19). An id is the `\d+[A-Za-z]*` token of the heading, so it may carry a letter suffix such as `4A` (Q41, Q42), and the status is keyed by the full id so a sub-step never overwrites its parent (Q45, see [Sub-steps of a plan step in the implement cycle](#sub-steps-of-a-plan-step-in-the-implement-cycle)).
3. Compute the branch start fresh each run as the fork point (the single `git rev-list`, not stored in the memory file) (Q18). Run `git log --grep "record step x validation"` between the branch start and HEAD. When that per-step validation commit exists, step `x` is already committed, so move `x` to the next plan step; otherwise keep `x` (Q16).

### Proposing the prompts for step x

Once `x` is fixed, the menu offers, labelled by the plan step `x`:

- `implement-step.md` for step `x` (always); on a `No` status its header, body and menu label switch to the `implement-missing-step.md` variant (see [Implementing missing work when a step validation reads No](#implementing-missing-work-when-a-step-validation-reads-no), Q46, Q47, Q48).
- `implementation-check.md` for step `x` as well, when any tracked file outside `docs/` is changed in `git status` (Q20).
- `group-commits-msg.md` as well, when the `Analysis of Step x` status line starts with `Yes` (step `x` is verified and ready to commit). The commit prompt is offered in a cached and a git-add-A variant chosen from the working-tree state:
  - cached files only: a `group-commits-msg.md (cached)` prompt.
  - both cached and non-cached files: both a `(cached)` and a `(git add -A)` prompt.
  - non-cached files only: only the `(git add -A)` prompt.
- The `(git add -A)` prompt makes the tool run `git add -A` before generating the prompt, so the prompt reads every change as staged; the `(cached)` prompt stages nothing and the prompt reads only the already-staged files.

The cycle menu lists these options higher workflow step first (Q54): the commit variants (step 10), then the check (step 9), then the implement entry (step 8). After an implementation the usual next action is the check, and after a verified check the commit, so the likeliest follow-up is the pre-highlighted top row; going back to more implementation stays an arrow press away. One exception (Q55): when a `No` status offers the `Implement missing for step <id>` entry, that entry tops the menu — moving forward is best served when what was missing is no longer missing, and a `No` step is never verified, so no commit row competes with it. An example, on a step with code changes and no `Yes` status yet:

```text
? Choose the prompt for step 6: (Use arrow keys)
 » Check step 6
   Implement step 6
```

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

Since the body now carries the list, the `git_status` Context role is dropped from the step-10 alternative (Q24); the remaining Context lists the same documents as the check prompt, `draft, requirement, design, plan, validation_plan` (Q40), even though the plan is then named both in the body and the Context. The validation-commit appendix of [Proposing the prompts for step x](#proposing-the-prompts-for-step-x) (the `docs(<topic>): record step x validation` requirement) is unchanged.

The commit body also names the plan step it groups (Q38): after the file count it reads `... for those {n} files, per step {x} ("{title}") evolutions of the implementation plan "{plan_doc}":`, reusing the step title and plan path already read for the menu and the implement and check prompts (Q33). The `("{title}")` and `of the implementation plan "{plan_doc}"` segments drop when the title or the plan is missing, the same granular drop as the implement body (Q34, Q35), so a missing plan degrades to `... for those {n} files, per step {x} evolutions:` (Q39).

The body stays in `tools/prompt_workflow.steps.json` as a static template with `{n}`, `{x}`, `{title}`, `{plan_doc}` and `{files}` placeholders, interpolated when the prompt is built (Q14), so the wording keeps living in the JSON file rather than in code.

### Emptying a.commit before delivering the commit prompt

The `group-commits-msg.md` instruction writes the grouped commit messages into `a.commit` at the project root. To start each grouping from an empty file, the tool empties `a.commit` when, and only when, a group-commits prompt is generated, for either variant (Q25): it truncates the file to size 0, creating it empty when it does not exist and clearing its content when it does, and never deletes it. This is the same write-empty step `oqm --create` uses for its companion file (`Path.write_text("", encoding="utf-8")`). No other prompt touches `a.commit`.

## Naming the implement and check steps by their plan number

The cycle prompts (workflow steps 8, 9 and 11) name the plan step by its number, its title and the plan document, so each prompt reads on its own. The title and the plan path are read once per run with `read_step_title` (the `### Step <x>` heading of the plan, Q30, Q32) and reused by the menu introduction, the implement body and the check body (Q33). This amends the number-only implement body of Q27 and the "implement never reads the plan" rule of Q29: the implement prompt now reads the same plan heading the check prompt already reads.

The implement body (steps 8 and 11) reads `Implement step {x} "{title}" of the plan "{plan_doc}", based on the design and the plan.` (Q33). The check body (step 9) reads `Check step {x} "{title}" implementation, based on the plan "{plan_doc}" and the validation plan.` (Q26). Here `{x}` is the plan step the menu shows (see [Proposing the prompts for step x](#proposing-the-prompts-for-step-x)), `{title}` is the trailing text of the matched `### Step <x>` heading in the `## Numbered steps for vX.Y.Z <topic>` section of `docs/plan.vX.Y.Z.<topic>.md` (loose match, a `.`, `:` or `-` separator tolerated, Q30, Q32), and `{plan_doc}` is the repo-relative path of the plan document, the same path the `Context:` section resolves. The plan document is repeated between the body and the `Context:` section on purpose, for clarity.

Both bodies stay in `tools/prompt_workflow.steps.json` as static templates carrying `{x}`, `{title}` and `{plan_doc}`, interpolated when the prompt is built the same way `{n}` and `{files}` already are (Q14). Two segment-drop fallbacks keep the text clean when a value is missing:

- No `### Step <x>` heading matches, so `{title}` is missing: the `"{title}"` segment and its leading space are dropped (Q31 for the check body, Q34 for the implement body and the menu introduction). The check body then reads `Check step {x} implementation, based on the plan "{plan_doc}" and the validation plan.` and the implement body `Implement step {x} of the plan "{plan_doc}", based on the design and the plan.`, with no empty quotes left behind.
- No plan document is resolved, so `{plan_doc}` is missing (and `{title}` with it): the `"{plan_doc}"` segment and its leading space are dropped too (Q35), degrading to `Implement step {x} of the plan, based on the design and the plan.` and `Check step {x} implementation, based on the plan and the validation plan.`. In practice the plan and the validation plan are matched together, so this is an edge guard.

This matches the `implement-step.md` and `implementation-check.md` instructions, which already expect prompts shaped like "implement step 2 of the ..." and "check step 2 implementation of ...".

## Sub-steps of a plan step in the implement cycle

A plan may split one numbered step into lettered sub-steps. `docs/plan.vX.Y.Z.<topic>.md` then carries `### Step 4.` followed by `### Step 4A.` and `### Step 4B.`, and the validation plan mirrors them with `### Analysis of Step 4`, `### Analysis of Step 4A` and `### Analysis of Step 4B`. The implement cycle of [Deriving the plan step x](#deriving-the-plan-step-x) was written for whole-number steps, so a sub-step id is mis-read at every stage that handles a step number. The decisions below (Q41 to Q45) settle how a sub-step id is represented, parsed, ordered, committed and detected.

### The sub-step collision today

[`parse_validation_steps`](../tools/prompt_workflow_plan.py#L107) matches the heading on `Analysis of Step <N>` with `ANALYSIS_RE` capturing only `\d+` ([prompt_workflow_plan.py:39](../tools/prompt_workflow_plan.py#L39)), so `Step 4A` and `Step 4B` are both read as the number `4`. [`derive_x`](../tools/prompt_workflow_plan.py#L127) then keys its `verified` map by that number, and the dict comprehension keeps the last entry, so the `Not started` status of `Step 4B` overwrites the `Yes` of the real `Step 4`. Step 4 reads as not verified, and the `group-commits-msg.md` choice (the commit prompt) is withheld, even though step 4 is implemented and analyzed while 4A and 4B are still empty.

### Stages a step id flows through

A step id is read, stored, compared or printed at these stages; each must accept a sub-step id such as `4A`:

- validation parse: [`parse_validation_steps`](../tools/prompt_workflow_plan.py#L107) and `ANALYSIS_RE` read the id from the `Analysis of Step <id>` heading.
- cycle derivation: [`derive_x`](../tools/prompt_workflow_plan.py#L127) builds the id list and the verified map, picks the current id, and advances past a committed id.
- cycle state: [`CycleState.x`](../tools/prompt_workflow_plan.py#L66) carries the current id.
- commit detection: [`has_step_commit`](../tools/prompt_workflow_git.py#L165) greps `record step <id> validation`.
- menu labels: [`build_cycle_options`](../tools/prompt_workflow_plan.py#L188) prints `Commit`, `Check` and `Implement step <id>`, in that order (Q54).
- prompt bodies: [`build_cycle_prompt`](../tools/prompt_workflow_plan.py#L319) interpolates `{x}` into the implement, check and commit bodies, and appends the `record step <id> validation` requirement.
- title read: [`read_step_title`](../tools/prompt_workflow_plan.py#L252) matches the plan `### Step <id>.` heading.
- intro line: [`cycle_intro`](../tools/prompt_workflow_plan.py#L307) prints `Regarding step <id> ...`.
- memory: [`MemoryRecord.plan_step`](../tools/prompt_workflow_models.py#L121) with [`_parse_step`](../tools/prompt_workflow_memory.py#L33) store and re-read the id.

### Sub-step id representation and grammar

Q41 asked how to carry a step id that can hold a letter suffix, weighing a string id, a `number` plus `suffix` pair, and a derived fractional number. The decision is to carry `x` as a string id at every stage, in `PlanStep.number`, `CycleState.x` and `MemoryRecord.plan_step`, because the id is used as text at the heading match, the menu label, the commit subject, the grep and the memory, and the cycle never sorts by numeric value (it orders by document order, Q43). The `int`-plus-`suffix` pair and the fractional encoding were dropped: the pair re-joins two fields at every stage, and the fraction cannot rebuild `4A` for the commit subject or the heading match.

Q42 asked for the id token grammar, after the proposed `\d\S+` was found to skip a lonely `4` (it needs a trailing non-space) and to swallow the `.` or `,` separator. The decision is `\d+[A-Za-z]*`, one or more digits then zero or more ASCII letters, read from both the validation `Analysis of Step <id>` heading and the plan `### Step <id>.` heading. It matches `4`, `4A` and `4B`, stops at the first non-letter, and its digit-then-letter shape lets `read_step_title` keep `4` apart from `4A` with a `\b` boundary, since there is no word boundary between a digit and a letter. The `\d+\S*` and `\d+[A-Za-z0-9]*` variants were dropped as still-greedy or wider than the plans need.

### Sub-step ordering and granularity

Q43 asked how to order `4`, `4A`, `4B`, `5` once integer order no longer applies. The decision is document order: `derive_x` already walks the parsed list in the order the `Analysis of Step` sections appear, and the plan and the validation plan are authored in the running order, so only the key type changes, not the traversal. A numeric-then-suffix sort was dropped as code to rebuild an order the document already states.

Q44 asked whether a sub-step is a first-class cycle step or part of its parent. The decision is first-class: each sub-step gets its own implement, check and commit, and its own `record step 4A validation` commit, so after step 4 is committed the cycle moves to 4A, then 4B, then 5. The space-delimited grep keeps the ids apart, since `record step 4 validation` never matches `record step 4A validation`, so `has_step_commit` tracks each id on its own. The parent-covers-children option was dropped because it would record empty sub-steps as done with step 4 and never let the cycle land on 4A.

### Detecting the current step among its sub-steps

Q45 asked how to read step 4 as current and offer its commit while 4A and 4B are empty. The decision is to key the parsed status by the full id, the fix for [The sub-step collision today](#the-sub-step-collision-today): `derive_x` reads the current id as the last id whose status is `Yes` in document order, offers implement, check and commit for it, and advances to the next id only once its `record step <id> validation` commit exists. Keyed by id, `Step 4B`'s `Not started` no longer overwrites `Step 4`'s `Yes`, so the group-commits prompt is offered for the finished step 4 while 4A and 4B stay pending. The int-keyed OR-merge was dropped because it still collapses 4, 4A and 4B into one step and would commit empty sub-steps.

## Implementing missing work when a step validation reads No

The implement cycle offers `implement-step.md` for step `x` on every run (see [Proposing the prompts for step x](#proposing-the-prompts-for-step-x)), with the body of [Naming the implement and check steps by their plan number](#naming-the-implement-and-check-steps-by-their-plan-number). That one body restates the whole step, even after [`implementation-check.md`](../instructions/implementation-check.md) has run, written "No, it is not implemented" on the `Analysis of Step x` status line, and filled a `### Missing work for Step x` section in the validation plan. A second implement body, the "implement missing" variant, points the LLM at that recorded gap instead of restating the whole step.

### Trigger and menu entry for the implement-missing body

The variant is selected by the `Analysis of Step x` status line, the same line `parse_validation_steps` already reads for `derive_x` (Q15, Q46): when that line starts with `No`, the implement entry becomes the implement-missing body; on any other status — the template placeholder of a never-checked step, or `Yes` — the plain implement body of [Naming the implement and check steps by their plan number](#naming-the-implement-and-check-steps-by-their-plan-number) stays. So `parse_validation_steps` records the `No` state of a step, not only its `Yes` state, keeping the placeholder and the `No` cases apart.

The variant replaces the implement entry rather than adding a second one (Q47): on a `No` status the single implement choice `build_cycle_options` shows is relabelled `Implement missing for step <id>`, so the cycle keeps one implement action per menu state. The full-step prompt is still reached on a placeholder or `Yes` status, and the implement-missing body still covers a wide gap when the missing-work section is broad. The relabelled entry also moves to the top of the menu, ahead of the check row, as the exception to the higher-step-first order (Q55): the step moves forward by filling its recorded gap first.

The variant fires wherever the implement body is built for a step whose status reads `No`: the cycle implement (workflow step 8) and the post-commit implement of the next plan step (workflow step 11), since both rows share the same implement body and the same `read_step_title` read (Q33, Q52). The step status, not the workflow row, picks the body.

### The implement-missing instruction file

The variant points its header at a new instruction file, `instructions/implement-missing-step.md` (Q48), not at `implement-step.md`. That new file is short and references both [`implement-step.md`](../instructions/implement-step.md) and [`split-large-file.md`](../instructions/split-large-file.md): it tells the LLM to implement and/or split — never reduce — the missing work, the choice depending on the nature of the gap (write the missing code by the implement-step flow, or split an over-budget file by the split-large-file flow). The body and the Context still carry the per-step focus (the step name and the missing-work section), so the instruction file stays a thin pointer to the two flows rather than a copy of `implement-step.md`.

### The implement-missing body and its line-budget sentence

Only the body and the Context change from the plain implement step; they are stored as a second alternative for step 8 in `tools/prompt_workflow.steps.json`, next to the plain implement body, and chosen in code by the `No` status (Q14). The cycle routes every implement action — the first-pass step-8 implement and the post-commit next-step implement — through that one step-8 config, so both pick the missing body on a `No` status (Q52). The body names the step the way the plain implement body does and points at the recorded gap (Q49):

`Implement the missing work of step {x} "{title}" of the plan "{plan_doc}", focusing on the "Missing work for Step {x}" section of the validation plan, based on the design, the plan and the validation plan.`

It keeps the `{x}`, `{title}` and `{plan_doc}` placeholders and the same segment-drop fallbacks as the plain implement body (Q34, Q35); the validation plan is always present for this variant, since the `No` status that triggers it is read from that plan.

The body also carries a standing line-budget sentence (Q50), kept in the same body block after the line above, as an inline reminder of the split flow the instruction file describes:

`If the missing work is a line-budget overflow, follow <prefix>/split-large-file.md and split the over-budget files line-wise; do not reduce or compress them.`

The sentence is always present, not gated on a file scan: it does no harm when no file is over budget, the LLM acts on it only when a file passes the limit, and it reuses the header `<prefix>` (Q10), which already ends with the instructions directory, so the `split-large-file.md` path opens in both the llm-shared and the submodule layout. "Split, not reduce" keeps every responsibility of the over-budget file rather than trimming code to fit the 650-line limit.

### Context documents for the implement-missing body

The variant's Context lists the five documents the check and commit bodies already resolve, `draft, requirement, design, plan, validation_plan` (Q40, Q51), one more than the four of the plain implement body, because the body points at the validation plan's missing-work section and that file must be on the reading list. The plan is named in both the body and the Context, the same repetition the commit body already carries (Q40).

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

## Handoff prompts to continue the implement cycle without the menu

The implement cycle of [Implement-validate-group commit message](#implement-validate-group-commit-message) is driven by the interactive menu of [Per-step interaction](#per-step-interaction): a human picks implement, check or commit for the plan step `x`. The handoff need is that same cycle without a human picking. When an LLM finishes one cycle step, it asks pw for the prompt of the next step and continues on its own. pw stays the one place that builds a cycle prompt; the handoff only adds a way to name the target step and skip the menu.

### The three handoff transitions

The handoff covers the three forward moves inside the implement cycle, each naming a target task and the plan step `x` it applies to:

- after `implement-step.md` for step `x`: hand off with `check` to `implementation-check.md` for step `x`, to check what was just implemented.
- after `implementation-check.md` for step `x`: hand off with the neutral `after-check` task for step `x`; pw reads the `Analysis of Step x` status line and produces the implement-missing prompt when it starts with `No`, or the commit prompt (the `group-commits-msg.md (git add -A)` variant) when it starts with `Yes` (Q58).
- after the implement-missing variant for step `x`: hand off with `check` to `implementation-check.md` for step `x`, to re-check after the gap is filled.

Each transition is one `pw handoff` call. The targets are the cycle actions [`build_cycle_prompt`](#proposing-the-prompts-for-step-x) already builds: the check body (step 9), the implement-missing body (step 8 variant), and the commit body in its `(git add -A)` form (step 10). The handoff adds no new prompt body; it picks an existing one instead of showing the menu.

### The handoff subcommand

pw gains a `handoff` subcommand, `pw handoff <task> <x>`, that names a target task and a plan step and writes that task's prompt, bypassing the `questionary` menu of [Per-step interaction](#per-step-interaction) (Q56). The subcommand keeps the task and the step together as positionals and leaves room for later handoff options without adding flags to the main command; a `--handoff`/`--step` flag pair was dropped as two flags that only make sense together, and a packed `task:step` token as a grammar that buries the step in a string. The global `--root` and `--debug` still apply.

The `<task>` is a readable word, not a step number or an instruction file name (Q57). pw accepts four tokens (Q62): `check` for the check prompt and the neutral `after-check` for the post-check routing above are the two the handoff chain uses, while the direct `implement-missing` and `commit` words stay for a manual call from the terminal (the Q60 case). The chain never types the direct words, so it cannot mis-branch; a manual `commit` on a `No` step carries no guard, the accepted cost of that convenience. The subcommand reuses the cycle machinery: it computes the cycle state for the named step, picks the cycle action, and runs the same [`build_cycle_prompt`](#proposing-the-prompts-for-step-x) and `deliver_prompt` path as the interactive cycle. The prefix, the document matching and the per-step bodies stay unchanged, except for the topic resolution of [Resolving the topic without a menu](#resolving-the-topic-without-a-menu).

### Resolving the target and the step for a handoff

After a check, pw decides the Yes/No branch itself rather than the caller (Q58): the check instruction writes the `Analysis of Step x` status line and hands off with the neutral `after-check` task, and pw reads that line and emits the implement-missing prompt on `No` or the commit prompt on `Yes`. The caller never names the branch, so it cannot mis-branch, and the validation plan stays the one source of truth. Naming the target in the caller with a pw guard was dropped because the branch rule would then live in two places, and a no-guard producer because a wrong call would pass silently — both moot once pw owns the branch.

The step the handoff applies to is the plan step `x` the caller names. pw uses that number, after checking it is a real `Analysis of Step <id>` id, and warns when it differs from the git-and-validation-derived `x` of [Deriving the plan step x](#deriving-the-plan-step-x) (Q59). The caller knows the step it just implemented or checked, so the named step is the intent; always overriding it with the derived `x` would make the argument decorative, and skipping the existence check would build an empty prompt on a typo. The warning keeps the derived `x` visible without overriding the explicit request.

### Resolving the topic without a menu

The interactive run resolves the topic with `choose_topic`, which falls back to the `questionary` menu when several drafts exist and no branch lock matches ([Locking the topic to the branch](#locking-the-topic-to-the-branch), Q53). The `handoff` subcommand is non-interactive and cannot show that menu, so it resolves the topic from the single draft or the branch lock only (Q63). By the implement cycle the topic is almost always locked to the branch, so the common handoff resolves with no extra input; when several drafts exist and none is locked, the handoff refuses with a message pointing at `pw --pick` to lock one first, rather than guess the topic or block on a menu it cannot draw.

### Delivering and recording a handoff prompt

A handoff delivers the prompt the same way an interactive run does (Q60): it writes `a.prompt.txt`, copies it to the clipboard, and falls back to stdout when the clipboard is unavailable ([Prompt output and clipboard fallback](#prompt-output-and-clipboard-fallback), Q05). The next reader is usually the calling LLM, which reads `a.prompt.txt`, the stable copy every run writes; the clipboard stays a convenience for a human driving the handoff from the terminal, and stdout covers a headless host. A stdout-and-file-only channel and a file-only delivery were dropped, since the one interactive path already serves both the program and the human.

The commit handoff, reached through `after-check` on a `Yes` step, resolves to the `(git add -A)` variant, so, like the interactive commit, it runs `git add -A` and empties `a.commit` before building the prompt (Q23, Q25); every handoff writes `a.prompt_memory` the way the menu does, so a later interactive run sees a consistent step (Q61). A prompt-only handoff was dropped for breaking the staged-list contract, and a stage-but-skip-memory handoff for leaving the memory stale against a cache the next run rebuilds anyway.

### Wiring the handoff into the calling instructions

The `handoff` subcommand produces the next prompt, but the chain only fires when the calling instruction runs it. This feature therefore adds a `## Handoff` section to each of the three cycle instructions (Q64): `implement-step.md` and `implement-missing-step.md` for `pw handoff check <x>`, and `implementation-check.md` for `pw handoff after-check <x>` (the tokens of Q62, with `<x>` the step the instruction just worked on). The section is not a one-line directive but a clear, detailed block that names the exact `pw handoff` call to make, states the purpose of that call, and tells the LLM to then follow the instructions of the prompt the call returns (written to `a.prompt.txt`, Q60). So each finished step hands the next prompt back to the model and the cycle advances on its own. Shipping the subcommand without the three sections, or leaving the wiring as spec guidance only, was dropped: the feature reaches its automatic-handoff goal only when each of the three instructions carries the `## Handoff` section.
