# The Review Relay

- Type: collection (feature-requests and issues)
- Draft role: umbrella

I need to introduce in the workflow a review mode which makes the LLM write instruction for its work to be reviewed, and another llm to take those instructions and provide feedback or suggestions for improvement.

It is a dialogue-based workflow where the first LLM generates a set of instructions for a specific task, and the second LLM evaluates those instructions, providing constructive feedback and suggestions for improvement.

## Cross-cutting convergence gate and review-summary identity

Ordinary review rounds remain automated. When a reviewer requests changes, the requestor consumes the answer, applies the feedback, and starts another round without waiting for a human. The consolidated no-progress and disagreement rules bound that automated dialogue.

A convergence point occurs only when the reviewer recommends the continuing action for the review family: consolidation for specification review or commit-readiness for implementation-code review. At convergence, the requestor enters `awaiting-human-confirmation`. Reviewer recommendations are advisory and never authorize consolidation or commit.

The human reviews the identity-bearing summary, reviewer recommendation, resulting specification or staged changes, and requestor assessment. The available choices are:

- Specification review: `Consolidate` or `Revise and review again`.
- Implementation-code review: `Commit` or `Rework and review again`.

Choosing another round at convergence overrides the reviewer recommendation and resets the no-progress counters. The human may add guidance, which is recorded with the override and included in the replacement request summary. The confirmation and any override are recorded in the versioned transcript. `awaiting-human-confirmation` is distinct from the `escalated` state used for timeout, abandonment, no-progress, disagreement, and inconsistent artifacts.

Every reviewee-to-reviewer summary identifies its context in human-readable form. It names the umbrella draft when one exists, or states `Umbrella draft: none`; specification summaries name the exact reviewed specification and round; code summaries name the exact implementation plan, implementation step, and round. Those fields must agree with the machine-readable exchange identity.

## Cross-cutting artifact home and LLM identity extension

The final `review-resume-command` item owns two cross-cutting changes to the
integrated review-mode behavior. These changes supersede the earlier
project-root runtime-artifact convention in the final implementation without
reopening or rewriting completed items 1 through 9.

They also supersede the earlier regrouping of a repository-root `rvw_resume`
command: resume is delivered only as an LLM skill because continuation requires
an active LLM session. Completed requirement, design, plan, validation, and
status documents remain closed; this umbrella and the final item record both
cross-cutting revisions.

First, every protocol-owned runtime review artifact must resolve below one
configurable repository-local directory whose default is
`<PRJ_DIR>/.reviews`. The final item also provides a migration tool that moves
recognized existing review artifacts from `PRJ_DIR` into the configured or
default directory without overwriting ambiguous evidence. Shared code and all
affected tests from the earlier exchange, requestor, reviewer, status, and
documentation topics must adopt that resolver as part of item 10.

A fast `migration_check` tool runs before every resume and can be invoked by
review status, including `rvw_status`. It distinguishes an already-correct artifact
home, legacy traces or artifacts requiring migration, and a collision or
damaged layout that prevents a safe move. Resume must migrate recognized
misplaced evidence and repeat the check before continuing. Review status must
also be able to run that check and migration. This bounded preflight write
supersedes the earlier strict read-only guarantee only for artifact migration;
normal status discovery remains read-only once the check passes.

Second, every exchange must trace which supported LLM acts as requestor and
which acts as reviewer. The shared host detector identifies Claude, Codex, or
Gemini from session evidence when possible and records an explicit unknown
state otherwise. Review status, including `rvw_status`, reports those role-specific
LLM identities. Legacy evidence may retain a missing trace; migration does not
invent one.

Readers must accept both legacy artifacts without LLM nature and newer traced
artifacts. Before continuing a role, inspect every artifact in the selected
exchange attributed to that role. When none records a different nature,
backfill the detected current LLM into all missing-nature artifacts for that
role. When any records a different nature, stop before backfill, list all
conflicts, and ask for `Override` or `Stop`. Override preserves the conflicting
recorded values while allowing the role-wide missing-nature backfill and
continuation; Stop changes nothing. For artifacts authored by the other role,
a missing nature is ignored and the artifact remains readable and unchanged.

The resume entry point is an LLM skill rather than a CMD command. It selects
requestor or reviewer by comparing the current LLM identity with the exchange
trace. When a legacy trace contains no LLM nature and no role argument was
passed, it asks which role to resume. An explicit role argument supplies that
missing choice, while a conflict with known trace evidence requires human
confirmation. Resume means starting or restarting a wait, reclaiming the exact
round and acting, or continuing beyond review through `pw skill`. Once the role
is resolved, no further confirmation is requested except for the stated forced
role mismatch.

A reviewer resume has only two outcomes: answer an existing request, or wait
for any future review-request artifact without knowing its identity in advance.
That wait is entered from an idle exchange, from an exchange that has
concluded, and from a live exchange whose next action belongs to the requestor
or to the human convergence gate, and it wakes on the next request whether that
request resumes the same exchange at a later round or occurrence or opens one
that did not exist when the wait started.
A requestor resume waits for an in-progress review answer, performs the next
owned review action, or, when no review and no further request remain, runs and
follows `pw skill` so writing, implementation, later review, or another durable
workflow task continues.

## Spec review

### Spec review requestor -- the writer

Whenever a LLM stops at the end of review-ask-question or consolidate-then-review-ask-questions (assuming new questions are asked), meaning open questions just got added to:

- a requirement (feature-request or issue)
- a design specification
- an implementation plan

If the file `(project root/)a.review-mode` is detected, then the LLM, through `pw` (`prompt-workflow`) must not wait for the user review of said open questions but instead

- check if `(docs/vX.Y/vX.Y.Z/)review.type.vX.Y.Z.slug.md` exists, and if not, write an intro based on a template for the review type and version, and then create the file with the generated content: it must be at the same path as the original document `type.vX.Y.Z.slug.md`.

  Here "type" is the type of the document being reviewed (feature-request, issue, design-specification, plan which is the "implementation plan"), "vX.Y" is the possible parent folder (could be docs directly), "vX.Y.Z" is the version of the document being reviewed, and "slug" is the slug of the document being reviewed.

- check if `(project root/)a.review-answer.type.vX.Y.Z.slug.md` exists (always at the root folder of the project, taking advantage of the `.gitignore` rule which ignore any `a.*` files), and if it does, delete it
- create or overwrite `(project root/)a.review-requested.type.vX.Y.Z.slug.md` with the LLM's generated feedback and the following conclusion:

> Let me know if questions are missing in the plan, if you agree with the existing questions, what answer would you chose for said existing questions. No consolidation for now, but if you have a better way to phrase the questions or answers, please suggest it.
> At the end of your review, write a review-answer.type.vX.Y.Z.slug.md leave instructions for the writer to make the recommended changes, and make a decision:
>
> - if there are very few edits (just word polishing), recommend convergence and consolidation
> - if there are more than word-polishing edits, request the recommended changes and another automated review round.

The LLM general feedback from the review requestor must also be appended to the `(docs/vX.Y/vX.Y.Z/)review.type.vX.Y.Z.slug.md` file (which will be versioned alongside the `(docs/vX.Y/vX.Y.Z/)type.vX.Y.Z.slug.md` original document being reviewed).

The requestor must then wait for `(project root/)a.review-answer.type.vX.Y.Z.slug.md`, read it, and distinguish an intermediate change request from a convergence recommendation.

For an intermediate round, the requestor applies the recommended changes to `(docs/vX.Y/vX.Y.Z/)type.vX.Y.Z.slug.md`, deletes the consumed answer, and creates a new request with the updated identity-bearing summary and the same conclusion as above. The automated dialogue continues without a human wait, and both roles append their feedback to the versioned transcript.

For a convergence recommendation, the requestor retains the answer as decision evidence, enters `awaiting-human-confirmation`, and presents the human with the identity-bearing summary, reviewer recommendation, and its own assessment. Only the human may choose `Consolidate` or `Revise and review again`. The answer is deleted after the confirmed action is applied. `Consolidate` authorizes consolidation and continuation; `Revise and review again` records the override, resets no-progress counters, and starts another automated round.

So for that part, you need to update the instructions of two existing skills: review-ask-question and consolidate-then-review-ask-questions, to add a new skill "spec-reviewer" for the reviewer mode workflow described above, able to wait for a `(project root/)a.review-requested.type.vX.Y.Z.slug.md` file. And the first two skills, in review mode, needs to be able to update a review `(docs/vX.Y/vX.Y.Z/)review.type.vX.Y.Z.slug.md` which is there just to document and record the review dialog (back and forth) between the requestor and the reviewer. That particular document does not have to be read by the LLM (only appended), it is just for documentation purposes.

### Spec review responder -- the reviewer

I need a skill "spec-reviewer" able to take the name of the document returned by `pw`, wait for a `(project root/)a.review-requested.type.vX.Y.Z.slug.md` file to be created, and then read the content of that file, and provide feedback or suggestions for improvement.

That skill will be able to read the review-requested file, analyze the instructions, and provide constructive feedback in a `(project root/)a.review-answer.type.vX.Y.Z.slug.md` file.

The LLM feedback must also append the same constructive feedback to the `(docs/vX.Y/vX.Y.Z/)review.type.vX.Y.Z.slug.md` file, in addition of the `(project root/)a.review-answer.type.vX.Y.Z.slug.md` file.

At the same time, when it is ready to create the `(project root/)a.review-answer.type.vX.Y.Z.slug.md` file, it must also delete the `(project root/)a.review-requested.type.vX.Y.Z.slug.md` file, so that the requestor can continue with the workflow without having to manage his (now deleted) request, focusing only on the new answer just provided by the reviewer.

## Implementation Code review

The same back and forth review workflow can be applied to the implementation phase, where the LLM generates code based on an implementation plan, and another LLM reviews that code.

### Implementation Code review requestor -- the writer

You need to update the existing skill `implement-step` (the one in `instructions\implement-step.md`) to trigger the review request workflow right after the `group-commits-msg` skill call, where you are supposed to stop for human review.

If the file `(project root/)a.review-mode` is detected, then the LLM, through pw (prompt-workflow) must not wait for the user review of said grouped commit message in `a.commit`, but instead:

- check if `(docs/vX.Y/vX.Y.Z/)review.code.vX.Y.Z.slug.md` exists, and if not, write an intro based on a template for the review type and version, and then create the file with the generated content: it must be at the same path as the original document `plan.vX.Y.Z.slug.md`.

  Note that in this "Implementation Code review" section, we are no longer speaking about "type" documents, but about "plan" documents, which are the implementation plans generated by the LLM. The review file will be named `review.code.vX.Y.Z.slug.md` to differentiate it from the review of the type documents.

- check if `(project root/)a.review-answer.code.vX.Y.Z.slug.md` exists (always at the root folder of the project, taking advantage of the `.gitignore` rule which ignore any `a.*` files), and if it does, delete it
- create or overwrite `(project root/)a.review-requested.code.vX.Y.Z.slug.md` with the LLM's generated report done at the end of the `implement-step` and the following conclusion:

> Step x of `docs\plan.v10.0.0.root-routing.md` has been implemented: look at the staged changes and see, following $llm-shared:implementation-check , if that is the case. `a.commit` is ready for commit, but do not commit anything yet, only review and fix what might be missing, amending `a.commit` accordingly if fixes are needed. Then summarize your fixes if any, and write a review-answer.code.vX.Y.Z.slug.md file with your feedback for the writer to review your changes.

The LLM general feedback from the review requestor must also be appended to the `(docs/vX.Y/vX.Y.Z/)review.code.vX.Y.Z.slug.md` file (which will be versioned alongside the `(docs/vX.Y/vX.Y.Z/)plan.vX.Y.Z.slug.md` original document being reviewed).

The requestor must then wait for `(project root/)a.review-answer.code.vX.Y.Z.slug.md`, read it, inspect the staged changes and `a.commit`, and distinguish an intermediate rework request from a commit-readiness recommendation.

For an intermediate round, the requestor applies or assesses the reviewer changes, makes any additional changes, deletes the consumed answer, and creates a new request with the updated identity-bearing summary. The automated review continues without a human wait.

For a commit-readiness recommendation, the requestor retains the answer as decision evidence, enters `awaiting-human-confirmation`, and presents the human with the umbrella, exact plan and step, reviewer recommendation, staged changes, `a.commit`, and its own assessment. Only the human may choose `Commit` or `Rework and review again`. `Commit` explicitly authorizes the owning workflow to run its existing commit step. `Rework and review again` records the override, resets no-progress counters, and starts another automated round. The answer is deleted after the confirmed action is applied.

So for that part, you need to update the instructions of one existing skills: implement-step, and to add a new skill "code-reviewer" for the reviewer mode workflow described above, able to wait for a `(project root/)a.review-requested.code.vX.Y.Z.slug.md` file. And the first two skills, in review mode, needs to be able to update a review `(docs/vX.Y/vX.Y.Z/)review.code.vX.Y.Z.slug.md` which is there just to document and record the review dialog (back and forth) between the requestor and the reviewer. That particular document does not have to be read by the LLM (only appended), it is just for documentation purposes.

### Implementation Code responder -- the reviewer

You need a skill "code-reviewer" able to take the name of the document returned by `pw`, wait for a `(project root/)a.review-requested.code.vX.Y.Z.slug.md` file to be created, and then read the content of that file, and provide feedback or suggestions for improvement based on instructions left in that review request.

The LLM feedback must also append the same constructive feedback to the `(docs/vX.Y/vX.Y.Z/)review.code.vX.Y.Z.slug.md` file, in addition of the `(project root/)a.review-answer.code.vX.Y.Z.slug.md` file.

At the same time, when it is ready to create the `(project root/)a.review-answer.code.vX.Y.Z.slug.md` file, it must also delete the `(project root/)a.review-requested.code.vX.Y.Z.slug.md` file, so that the requestor can continue with the workflow without having to manage his (now deleted) request, focusing only on the new answer just provided by the reviewer.

## Tasks

### Complete existing skills by referencing and creating new ones for review requestor

When you complete existing skills, you must do so in a way a simple reference to the complementary role of review requestor is made, and that the LLM is aware of the review mode workflow, and that it must append its feedback to the review file in the docs folder.

The review requestor process (skill, template, script) must be specified in its own role/skill.

The reviewer process are two new skills (one for spec, one for code)

Make sure those new skills are documented, but also referenced by specific llm skill wrappers such as the ones you see in .agents and which on include "Locate the shared instruction body `instructions/process-draft.md`" or "Read and follow the canonical instruction at [`instructions/process-draft.md`](../../../instructions/process-draft.md)."

### Adding templates and scripts

In each of those skills (complementary role of review requestor, and the two new skills for the reviewer), you must add a template and a script to generate the content of the review-requested file, and the review-answer file.

Define as many utility tools as you need to better support the review mode workflow, and make sure to document them in the `docs` folder and appropriate diataxis wiki pages.

### Termination criteria

The feature request and design will need to insist on termination criteria for the review mode workflow, and how to handle cases where the review process is not completed in a timely manner, or if there are disagreements between the requestor and reviewer. Define clear guidelines for when to stop and request human intervention.

## List of feature-requests and issues to create

| Order | Type | Key title | Slug | Status | Requirement | Validation plan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Feature-request | Build the review exchange core | `review-exchange-core` | completed | `docs/v0.11.0/feature-request.v0.11.0.review-exchange-core.md` | `docs/v0.11.0/plan.v0.11.0.review-exchange-core.validation.md` |
| 2 | Feature-request | Request specification reviews | `spec-review-requestor` | completed | `docs/v0.11.0/feature-request.v0.11.0.spec-review-requestor.md` | `docs/v0.11.0/plan.v0.11.0.spec-review-requestor.validation.md` |
| 3 | Feature-request | Respond to specification reviews | `spec-reviewer` | completed | `docs/v0.11.0/feature-request.v0.11.0.spec-reviewer.md` | `docs/v0.11.0/plan.v0.11.0.spec-reviewer.validation.md` |
| 4 | Feature-request | Request implementation code reviews | `code-review-requestor` | completed | `docs/v0.11.0/feature-request.v0.11.0.code-review-requestor.md` | `docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md` |
| 5 | Feature-request | Respond to implementation code reviews | `code-reviewer` | completed | `docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md` | `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md` |
| 6 | Feature-request | Document the review-mode workflows | `review-mode-docs` | completed | `docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md` | `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md` |
| 7 | Feature-request | Check Markdown against the repository rules | `markdown-check` | completed | `docs/v0.11.0/feature-request.v0.11.0.markdown-check.md` | `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` |
| 8 | Feature-request | Expose commit-plan validation without committing | `commit-plan-check` | completed | `docs/v0.11.0/feature-request.v0.11.0.commit-plan-check.md` | `docs/v0.11.0/plan.v0.11.0.commit-plan-check.validation.md` |
| 9 | Feature-request | Report active review status through a skill | `review-status-command` | completed | `docs/v0.11.0/feature-request.v0.11.0.review-status-command.md` | `docs/v0.11.0/plan.v0.11.0.review-status-command.validation.md` |
| 10 | Feature-request | Resume interrupted reviews | `review-resume-command` | completed | `docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md` | `docs/v0.11.0/plan.v0.11.0.review-resume-command.validation.md` |

### Requirement details for the umbrella

#### 1. Build the review exchange core

- Type: Feature-request
- Key title: Build the review exchange core
- Slug: `review-exchange-core`
- Regroups: the project-root `a.review-mode` opt-in marker; the request, answer, and versioned review-transcript artifact conventions; the shared requestor role or skill; reusable templates, scripts, and utility tools; safe create, overwrite, append, wait, and delete operations; the convergence-only human-confirmation state; the mandatory review-summary identity; and the termination and human-intervention rules shared by specification and code review.
- Boundary rationale: the transport, naming, lifecycle, and safety policy must be settled once so every requestor and reviewer role can exchange files consistently without duplicating the protocol.
- Concrete rules and constraints: transient `a.review-requested.*` and `a.review-answer.*` files originally stay at the project root and rely on the existing `a.*` ignore rule, but item 10 supersedes that runtime placement through the configured artifact home; the versioned `review.*` transcript lives beside the reviewed document, is initialized from a type-and-version template when absent, is append-only for agents, and is not reread as working context; producing an answer deletes the matching request; requestors delete stale or consumed intermediate answers but retain convergence answers until confirmation; intermediate rounds stay automated; convergence enters durable `awaiting-human-confirmation`; escalation remains separate; every requestor summary names its umbrella or `none` and its exact specification or plan context; review waits must terminate or escalate when they are not completed in time or when the two roles disagree; and the workflow must define explicit criteria for stopping and requesting human intervention.
- Depends on: none.

#### 2. Request specification reviews

- Type: Feature-request
- Key title: Request specification reviews
- Slug: `spec-review-requestor`
- Regroups: the review-requestor behavior triggered after `review-ask-questions` or `consolidate-then-review-ask-questions` adds open questions to a feature request, issue, design specification, or implementation plan; the references from those existing skills to the complementary requestor role; and the repeated revise-or-consolidate loop.
- Boundary rationale: specification authorship owns deciding whether reviewer feedback requires another review round or permits consolidation, while the shared exchange mechanics belong to the core requirement.
- Concrete rules and constraints: only activate when `a.review-mode` exists; create or reuse `review.type.vX.Y.Z.slug.md` beside the reviewed document; remove a stale root `a.review-answer.type.vX.Y.Z.slug.md`; create or overwrite `a.review-requested.type.vX.Y.Z.slug.md` with the mandatory umbrella, reviewed-specification, and round identity plus the generated feedback and prescribed conclusion; append requestor feedback to the transcript; automatically apply intermediate change requests and repeat; treat a reviewer consolidation recommendation as advisory; enter `awaiting-human-confirmation` only at convergence; and consolidate only after the human explicitly selects `Consolidate`.
- Depends on: `review-exchange-core`.

#### 3. Respond to specification reviews

- Type: Feature-request
- Key title: Respond to specification reviews
- Slug: `spec-reviewer`
- Regroups: the new `spec-reviewer` skill, its LLM-specific wrapper or adapter, and its request-reading and answer-generation template and script.
- Boundary rationale: the independent reviewer must have a focused role that evaluates open-question instructions without inheriting the writer's responsibility to edit or consolidate the reviewed specification.
- Concrete rules and constraints: accept the document name returned by `pw`; wait for the matching project-root `a.review-requested.type.vX.Y.Z.slug.md`; validate its umbrella, reviewed-specification, and round identity; provide constructive feedback and either request changes or recommend convergence in `a.review-answer.type.vX.Y.Z.slug.md`; keep that recommendation advisory; append the same feedback to the sibling transcript; and delete the consumed request when the answer becomes ready.
- Depends on: `review-exchange-core`, `spec-review-requestor`.

#### 4. Request implementation code reviews

- Type: Feature-request
- Key title: Request implementation code reviews
- Slug: `code-review-requestor`
- Regroups: the `implement-step` integration immediately after `group-commits-msg`, where the workflow currently stops for human review, plus the requestor-side revise-and-rereview loop for staged implementation changes and `a.commit`.
- Boundary rationale: the implementation writer owns its staged changes, report, and decision after review, while the exchange lifecycle remains shared and the code reviewer remains a separate role.
- Concrete rules and constraints: only activate when `a.review-mode` exists; create or reuse `review.code.vX.Y.Z.slug.md` beside the plan; delete a stale root `a.review-answer.code.vX.Y.Z.slug.md`; create or overwrite `a.review-requested.code.vX.Y.Z.slug.md` with the mandatory umbrella, plan, step, and round identity plus the end-of-step implementation report; direct the reviewer to use `implementation-check`, inspect staged changes, avoid committing, repair missing work, amend `a.commit` when needed, and either request rework or recommend commit-readiness; automatically continue intermediate rework rounds; enter `awaiting-human-confirmation` only at convergence; and run the existing commit step only after the human explicitly selects `Commit`.
- Depends on: `review-exchange-core`.

#### 5. Respond to implementation code reviews

- Type: Feature-request
- Key title: Respond to implementation code reviews
- Slug: `code-reviewer`
- Regroups: the new `code-reviewer` skill, its LLM-specific wrapper or adapter, and its request-reading and answer-generation template and script.
- Boundary rationale: code review needs a focused responder that can validate and repair implementation work while leaving commit authority and continuation decisions with the writer.
- Concrete rules and constraints: accept the plan document name returned by `pw`; wait for the matching project-root `a.review-requested.code.vX.Y.Z.slug.md`; validate its umbrella, plan, step, and round identity; follow the request and `implementation-check` to assess staged implementation; do not commit; fix missing work and amend `a.commit` when needed; either request rework or recommend commit-readiness in `a.review-answer.code.vX.Y.Z.slug.md`; keep that recommendation advisory; append the same feedback to the sibling transcript; and delete the consumed request when the answer becomes ready.
- Depends on: `review-exchange-core`, `code-review-requestor`.

#### 6. Document the review-mode workflows

- Type: Feature-request
- Key title: Document the review-mode workflows
- Slug: `review-mode-docs`
- Regroups: documentation for the shared requestor role, the `spec-reviewer` and `code-reviewer` skills, their templates and scripts, the opt-in marker, artifacts, automated intermediate rounds, the convergence-only human gate, mandatory summary identity, dialogue lifecycle, timeouts, disagreement handling, and utility tools in the project docs and appropriate Diataxis wiki pages.
- Boundary rationale: documentation follows the settled behavior of every role and gives users one coherent operational view without making the functional requirements depend on prose that is still changing.
- Concrete rules and constraints: document the LLM-specific wrappers that locate the canonical shared instructions; cover how to enable review mode, run each reviewer, interpret and recover the transient files, and escalate to a human; keep review transcripts beside their source documents, while item 10 supersedes the root placement of transient coordination files with the configured artifact home; and keep each Diataxis page focused on one purpose, presented in the order explanation, tutorials, how-to guides, then reference.
- Depends on: `review-exchange-core`, `spec-review-requestor`, `spec-reviewer`, `code-review-requestor`, `code-reviewer`.

#### 7. Check Markdown against the repository rules

- Type: Feature-request
- Key title: Check Markdown against the repository rules
- Slug: `markdown-check`
- Regroups: an executable check for the Markdown rules this umbrella already declares non-negotiable, its repository-root launcher, its place in the shared gate, and the Diataxis reference page that states which rules are enforced and why the two heading rules may never be disabled.
- Boundary rationale: the heading rules belong to review mode because a duplicate heading in a transcript is a protocol defect, but the check itself is a repository-wide quality gate that no review role should own; separating it keeps the reviewer roles focused on assessment rather than on carrying a linter.
- Concrete rules and constraints: apply the rule set the repository already declares in `.markdownlint.json`, where MD013 is off and MD033 allows only `img`; run from the repository root without environment setup, in an environment that has no Node runtime and no reachable package network, so the implementation is Python over the declared rules; report one finding per line with path, line, rule, and reason; treat MD024 and MD025 as failures that no configuration may disable, since `instructions/review-requestor.md` and `instructions/implementation-check.md` both forbid disabling them; decide during the requirement and design phases whether the gate fails or warns, whether it covers every tracked Markdown file or only changed ones, and how the pre-existing findings outside this effort are handled rather than folded into an unrelated commit.
- Depends on: `review-exchange-core`, `code-reviewer`, `review-mode-docs`.

#### 8. Expose commit-plan validation without committing

- Type: Feature-request
- Key title: Expose commit-plan validation without committing
- Slug: `commit-plan-check`
- Regroups: a launcher over the existing public `validate_commit_plan` API that reports groups and diagnostics for the root `a.commit` against the exact staged set without touching the index, and the reviewer-instruction wording that names it where the assessment is currently prose.
- Boundary rationale: the validator already exists and is shared with batch execution, so this requirement adds only the missing entry point and the instruction that calls it; folding it into the reviewer role would put a commit-plan tool inside an assessment skill, and folding it into batch execution would tie a read-only check to the committing path.
- Concrete rules and constraints: reuse the shipped `validate_commit_plan(blocks, staged_paths)` rather than reimplementing its rules; parse the plan with `interactive=False`; never reset, stage, or commit; report the typed groups and every diagnostic in a form the reviewer can quote as readiness-floor evidence; note that the one shipped entry point today refuses `--root-a-commit` combined with `--dry-run`, so the requirement must decide between a new launcher and lifting that restriction; and decide whether `group-commits-msg` should call the same command before a request is published so both roles judge the plan identically.
- Depends on: `review-exchange-core`, `code-reviewer`.

#### 9. Report active review status through a skill

- Type: Feature-request
- Key title: Report active review status through a skill
- Slug: `review-status-command`
- Regroups: a public `review-status-command` skill exposed by the installed llm-shared plugin as `$llm-shared:review-status-command`; its canonical instruction and thin LLM-specific adapters; a repository-root `rvw_status` command, launcher, and shared implementation; a stable machine-readable result; and a concise human-readable account of every review exchange currently in progress.
- Boundary rationale: discovering who owns a stopped review and what it concerns is read-only diagnosis; it belongs outside the requestor and reviewer roles so either role can use the same facts before acting.
- Concrete rules and constraints: make `$llm-shared:review-status-command` discoverable after installing the llm-shared plugin; keep reusable skill instructions canonical and make each LLM-specific skill file a thin adapter that refers directly to them; have the skill invoke or direct the agent to invoke `rvw_status` rather than reproduce its discovery logic; run without requiring the caller to remember a family, document, slug, step, round, or artifact path; discover live specification and code exchanges from protocol-owned coordination records; report whether a review is active, its specification or code family, the current requestor or reviewer actor, state, exact reviewed document, umbrella or `none`, implementation step when applicable, round, exchange occurrence, artifact paths, and next protocol action; distinguish zero, one, and multiple live exchanges without silently choosing among several; remain read-only after the bounded migration preflight introduced by item 10; return a stable result that the resume skill can consume without scraping prose; and work after a shell, VPN, terminal, or computer restart without relying on prompt memory.
- Depends on: `review-exchange-core`, `spec-review-requestor`, `spec-reviewer`, `code-review-requestor`, `code-reviewer`.

#### 10. Resume interrupted reviews

- Type: Feature-request
- Key title: Resume interrupted reviews
- Slug: `review-resume-command`
- Regroups: a public LLM resume skill and its shared implementation; configurable review-artifact path resolution with a `<PRJ_DIR>/.reviews` default; a fast `migration_check` preflight; a migration tool for recognized runtime review artifacts currently stored in `PRJ_DIR`; review-status check and migration support; Claude, Codex, and Gemini host detection; durable requestor and reviewer LLM traces; legacy missing-nature compatibility, role-wide identity backfill, and recorded-identity override-or-stop handling; review-status identity reporting; trace-based resume-role routing with a confirmed explicit override; reviewer-only wait-or-answer behavior with a quiet script-managed foreground wait; requestor answer-waiting, review work, and `pw skill` continuation; and self-contained host-specific instructions for the current session.
- Boundary rationale: interruption recovery is a human-invoked orchestration action over an existing exchange, not reviewer judgment or requestor authorship; keeping it separate prevents either role instruction from guessing identity or reconstructing protocol context. This final item also owns the shared artifact-location and participant-identity retrofit needed across the already integrated review-mode code and tests, without reopening the completed umbrella rows.
- Concrete rules and constraints: expose resume only as an LLM skill, with no CMD, batch, or repository-root `rvw_resume` command; route every protocol-owned runtime artifact through one configurable repository-local directory that defaults to `<PRJ_DIR>/.reviews`; run a fast `migration_check` before every resume and make review status and `rvw_status` able to run the same check; migrate recognized misplaced root traces and artifacts, repeat the check, and stop rather than invent identity or overwrite ambiguous evidence; treat that bounded migration as the only exception to status's read-only observation contract; update all affected shared code and tests from earlier topics; detect Claude, Codex, or Gemini from host evidence when possible and record an explicit unknown result otherwise; durably trace the LLM acting as requestor and reviewer in every exchange; process both legacy missing-nature artifacts and newer traced artifacts; before continuing a role, scan every artifact in the selected exchange occurrence attributed to that role; when none records a different nature, backfill the detected nature into all missing-nature artifacts for that role as one operation; read counterpart-role artifacts without mutation when their nature is absent; when any current-role artifact records a different nature, stop before backfill, list every conflict, and ask for `Override` or `Stop`; preserve conflicting recorded values on Override and make no identity change on Stop; make review status and `rvw_status` report role identities and migration outcome; use the typed status result to select specification requestor, specification reviewer, code requestor, or code reviewer by matching the current LLM to the trace; when legacy trace evidence contains no LLM nature and no role argument was passed, ask which role to resume; accept a forced requestor or reviewer argument without that question when no LLM nature exists, but require human confirmation when the argument conflicts with a known LLM-role trace; once role and artifact identities are resolved, continue without another confirmation; for a reviewer, renew or reclaim and answer an existing request, otherwise enter a global wait for any new specification- or code-review request, entered from an idle exchange, from a concluded exchange, or from a live exchange whose next action belongs to the requestor or to the human convergence gate, even when no exchange or implementation step has started and no live request artifact or identity exists, and waking on a request that resumes the same exchange at a later round or occurrence as well as on one that opens a new exchange, and never run `pw skill` or writer work; for a requestor, wait for an in-progress answer, renew or reclaim and perform the next owned review action, or, when no review and no further request remain, run and immediately follow `pw skill` so writing, implementation, later review, or another selected task continues; preserve the exact identity, round, occurrence, artifacts, expected actor, and next action even when the lease has not expired and without waiting for `wait_timeout_seconds`; preserve all durable evidence; continue through the applicable human convergence gate; refuse malformed, repair-required, escalated, artifact-inconsistent, or ambiguous multiple-exchange states with typed status evidence instead of guessing; and remain idempotent when repeated against the same durable state.
- Foreground wait contract: `wait-any-request` is the only identity-free global reviewer wait. A graceful host or console cancellation is a terminal `cancelled` result. The command writes no idle progress and emits one machine object with `operation`, `outcome`, `identity`, `candidates`, and `diagnostic`; a `found` result additionally contains the session-only ownership capability. It exits 0 for `found`, 3 for `ambiguous` or `cancelled`, and 2 for invalid input or an operational failure.
- Depends on: `review-exchange-core`, `review-status-command`, `spec-review-requestor`, `spec-reviewer`, `code-review-requestor`, `code-reviewer`, `review-mode-docs`.
