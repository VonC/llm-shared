# Write implementation plan and validation plan

ultrathink: To write the two plan documents, I will first need to gather information from the design document `docs\design.vX.Y.Z.<topic>.md` and the issue document `docs\issue/feature_request.vX.Y.Z.{topic}.md`. I will analyze the design and issue documents to extract the necessary implementation details, file modifications, and rollout steps.

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels").

Write two plan documents:

- a plan document named `docs\plan.vX.Y.Z.<topic>.md`, in markdown format, from a design document `docs\design.vX.Y.Z.<topic>.md` included in your context. It will describe what needs to be implemented, file by file, and the rollout steps to be followed. It should not include any design choice, but only implementation details.
- an implementation validation plan document named `docs\plan.vX.Y.Z.<topic>.validation.md`, in markdown format, from the same design document `docs\design.vX.Y.Z.<topic>.md` included in your context. It will review what has been implemented, file by file, and the rollout steps followed. It should not include any design choice, but only implementation review details.

For the first plan document, follow the template from [`write-plans.template.md`](../templates/write-plans.template.md) to write the plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

For the second implementation validation plan document, follow the template from [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md) to write the implementation validation plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; use the `review-ask-questions` skill (see [`review-ask-questions.md`](review-ask-questions.md)) for that follow-up review step. That review round runs on the plain plan only, not on the validation plan: it is wired as steps 8 and 9 of the `pw` workflow, between `write-plans` and the first `implement-step`.
- If that plan review later changes the numbered step list (steps added, removed, or renumbered), re-align the validation skeleton you write here so each `Analysis of Step N` section still matches a plan step, since the implement cycle reads those sections.

Based on `docs\issue/feature_request.vX.Y.Z.{topic}.md` and `docs\design.vX.Y.Z.{topic}.md`, write a `docs\plan.vX.Y.Z.{topic}.md`, which will include, in each step, an "Step x analysis and intent" (with issues, fix intent, expected outcome, step framings, complexity impact, feature preservation) before another subsection "Step x implementation" with step files involved, test first, class and behavior, completion criteria, and a third subsection "Step x addendums" with line-budget checkpoint, full workflow timing run readiness, time-gated status for this step.

Each step must include the list of files to modify or to create (each name followed by a `(new, to be created)` to mark those to create, and `(existing, to be updated)` for the existing files).
Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py`, and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Do review the plan against the current test tree, but also against the current code tree as a whole, to validate both code files and test files.

Focus on massive gain tending to avoid writing and reading too many files in your proposed changes.

Run your second pass focused only on implementation risk gaps, but also check the current number of lines for each file involved: anything above 550 risks getting, after code updates and additions, to exceed the 650 line limit qualifying for "big file": in case of over 550-line files, check if you can delegate/isolate the evolutions you need to a separate file (especially for test). This is not always possible for non-test files where existing functions need to be amended: do not force a resolution then: a future split phase will be needed once the plan is implemented.

Add to the plan a compact "line budget checkpoint" checklist to each step so it is ready for execution tracking, but also leave clear guidance/instruction regarding that line budget on each step: when I will tell you to implement the step 'x', said step will have everything it needs, including line budget constraint and split guidance.

Add in each step a reference to a new section which describes how to do the "execution command checklist" per step (count lines before/after, run targeted tests, run grep check). That way, you can detail that process, while mutualizing it for all steps, and reference it in each step.

Mutualize your "ready-to-run-command", and add a reference to it in each step. Said command is one `ghog day` walk — groundhog runs check.bat, the step's affected tests, and the full coverage pass in order, stopping at the first non-green step (see `GROUNDHOG.md`) — repeated fix-and-walk until it reports the objective. Do not plan direct `check.bat` or `pytest` calls; groundhog is in charge of check and tests.

Prepare also a `docs\plan.vX.Y.Z.{topic}.validation.md` skeleton (similar to `docs\plan.v8.11.perf_complexity.validation.md`), with subsections Goal for step x (you can fill out this one), "Step x improvement expectations" (you can fill out this one), "What was implemented for Step x" (leave it empty for now), "New types/classes introduced for Step x" (leave it empty), "Architecture check for Step x" (empty), "Performance check for step" (empty), "Feature integrity for step" (empty). Each section left empty in this initial skeleton holds the literal placeholder `_(empty — no check has taken place yet.)_.` (note the trailing period after the closing `_`, explained under "Markdown lint workarounds" below). Do not include a "Missing work for Step x" section in the skeleton: no check has taken place yet, and only an implementation check that concludes "No, it is not implemented" adds that section.

Follow the steps detailed in `docs\plan.vX.Y.Z.{topic}.md`.

## File-based IO cost Target Clarification Pass

Do a final pass on issue-design-plan-implementation to check if each designed and planned amelioration will result in a fast operation minimizing file-based IO: the loading doc phase must now be a tiny index-read step rather than a noticeable metadata-loading delay.

Do one quick doc patch pass to add a short "file-based IO cost Clarification" section in all 4 docs so this criterion is explicit and consistent.

## Step 0 Perf-Gates Pass for new model

Do a final pass on plan: do we need a step 0 with `pytest.mark.timeout` time-bound based tests, marked as xfail, with a clear expectation of removing that xfail in the appropriate step?

If yes, do add those patches.

## Final step: Acceptance tests

Make sure the final step includes acceptance tests (larger than unit test, like integration tests) that are able to validate the features are working as expected.

## Markdown lint workarounds for the plan documents

Two markdownlint rules need a deliberate workaround when writing these plan
documents:

- **MD038 (no-space-in-code)**: never leave a space immediately inside an inline
  code span. When a snippet genuinely starts or ends with a space, write that
  space as the literal token `[space]` so the span stays lint-clean while the
  reader still sees that a space is meant, as in `` `[space]${x}` ``.
- **MD036 (no-emphasis-as-heading)**: a line made only of italic text is read as an
  emphasis-used-as-heading. End such a line with a period placed after the closing
  underscore so it is no longer pure emphasis, for example
  `_(empty — no check has taken place yet.)_.`.

The initial validation skeleton fills every not-yet-checked section (`What was
implemented`, `New types or classes introduced`, `Architecture check`,
`Performance check`, `Unit test coverage check`, `Feature integrity`) with that
exact placeholder, `_(empty — no check has taken place yet.)_.`, and opens each
step's `Analysis of Step N implementation state` with the sentence "Not started.
Step N is not implemented because ...". An implementation check later replaces the
placeholders with real findings.

## Handoff

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

When the `plan.vX.Y.Z.<slug>.md` and its validation skeleton are written, hand the cycle on to the plan review, with no menu and no go-ahead. From the project root, in a PowerShell shell, run `pw skill` through its launcher (see [`run-pw.md`](run-pw.md) for the non-interactive invocation; the bare `pw` alias does not resolve in a tool shell):

- `pw skill`

`pw skill` prints one bare next-step command, derived from the documents on disk — here `<command-prefix>review-ask-questions on docs/plan.vX.Y.Z.<slug>.md` (with the prefix selected by `command_prefix_char.md`). The review runs on the plain plan only, never the validation plan. Read that line and run it straight away: a handoff is the go-ahead to perform the next step now, so do not stop to ask whether to proceed, and do not compose the next prompt yourself.

To hold the chain here instead — to read the plan before the review runs — pass the literal phrase `stop here` in this skill's argument when you invoke it. With `stop here` in the argument, write the plans and skip this handoff.
