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

- a header line: `Follow the instructions from <prefix>/instructions/<instruction>.md and do the following`, where `<instruction>` is the step instruction file and `<prefix>` is computed as described below (Q10);
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
| 8 | implement-step.md | Implement the next step of the plan, based on the design and the plan. | draft, requirement, design, plan |
| 9 | implementation-check.md | Check the current step implementation, based on the plan and the validation plan. | draft, requirement, design, plan, validation plan |
| 10 | group-commits-msg.md | Group the changed files and write one conventional commit message per group. | plan, current git status |
| 11 | implement-step.md | Implement the next step of the plan, based on the design and the plan. | draft, requirement, design, plan |
| 11 | prepare-release-notes.md | Prepare the release notes for this version, based on the plan and the git history since the last tag. | draft, requirement, design, plan |

## Per-step interaction

For each step, the tool shows an interactive menu with arrow-key selection and ESC to exit (Q08), using the `questionary` library (Q12), offering:

- to repeat the prompt of the current step
- to choose the next step among the possible ones (if any)

When there is no current step yet (start of the workflow), only the next steps are shown; ESC exits the tool at any point. The `questionary` call is isolated in a thin wrapper so the rest of the logic stays unit-testable and the wrapper can be excluded from coverage like `tools/uv_run.py`.

## The a.prompt_memory file

### Contents and format of the memory file

The memory file at the project root keeps the workflow context as `key=value` lines grouped in sections (Q03), which stay easy to read and to hand-edit. It records the branch, the resolved version, the topic slug, and the current step as a number plus its chosen instruction (the step number is needed because the same instruction recurs at different steps). No step history is stored: the step preconditions are re-derived from the documents on disk and from this `step` value (see below), so the file stays small. A minimal shape:

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

The document-producing steps (requirement at step 1, design at step 4, plan at step 7) and the "Open questions" gates are derived from the documents on disk. The steps that create no new `docs\...md` file — the review and consolidate steps (2, 3, 5, 6) and the tail steps (8 to 11: implement, check, commit, release notes) — take their state from the persisted `step` value instead (Q04, Q11). When that `step` disagrees with the documents on disk, the tool warns about the mismatch and trusts the documents.

### Startup validation logic for the memory file

If a.prompt_memory file already exists, the tool should check if the branch memorized in it is still the current branch, and if the general topic is still relevant (the draft file still exists and is still modified or created since the start of the branch). If not, it should propose to choose another general topic among the relevant ones, or to exit saying that no general topic is relevant anymore or detected. If the branch and general topic are still relevant, it should propose to continue with the same general topic, or to choose another one among the relevant ones, or to exit (ESC to exit).

## Design decisions

The table summarizes the choices made from the answered questions Q01 to Q14, the section that carries each one, and the alternatives that were dropped.

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
| Q11 | Steps 8 to 11 trust the persisted `step`; steps 1 to 7 stay document-derived | Step state re-derived from the documents on disk | Gives the doc-less tail a notion of progress without git guessing | Git signals; track nothing |
| Q12 | Use `questionary` for the interactive menu | Per-step interaction | Smallest select API with arrow keys and a clean None-on-ESC exit, runs on Windows | prompt_toolkit directly; InquirerPy |
| Q13 | Per-step body names prior docs by role; Context resolves them to file paths | Per-step prompt content | Satisfies Q09 without duplicating the path list | Body intent only; paths inlined in the body |
| Q14 | Store the per-step body and Context roles in a JSON file keyed by step number | Per-step prompt content | Editable without code; expresses alternatives and role lists cleanly | INI; in-code dict |
