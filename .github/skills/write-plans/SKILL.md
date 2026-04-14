---
name: write-plans
description: 'Write two plan markdown documents. A plan to details what needs to be implemented, file by file, and the rollout steps to be followed. An implementation plan to review what has been implemented, file by file, and the rollout steps followed. Both documents should not include any design choice, but only implementation details.'
user-invocable: true
metadata:
  - "This skill is used to write two plan markdown documents. A plan to details what needs to be implemented, file by file, and the rollout steps to be followed. An implementation plan to review what has been implemented, file by file, and the rollout steps followed. Both documents should not include any design choice, but only implementation details."
  - "The argument hint for this skill is 'Provide the version vX.Y.Z and topic, for example "v9.3.0 sentinels".'"
argument-hint: 'Provide the version vX.Y.Z and topic, for example "v9.3.0 sentinels".'
---

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels")

Write two plan documents:

- a plan document named `docs\plan.vX.Y.Z.<topic>.md`, in markdown format, from a design document `docs\design.vX.Y.Z.<topic>.md` included in your context. It will describes what needs to be implemented, file by file, and the rollout steps to be followed. It should not include any design choice, but only implementation details.
- an implementation plan document named `docs\plan.vX.Y.Z.<topic>.implementation.md`, in markdown format, from the same design document `docs\design.vX.Y.Z.<topic>.md` included in your context. It will review what has been implemented, file by file, and the rollout steps followed. It should not include any design choice, but only implementation review details.

For the first plan document, follow the template from #file:./plan.template.md to write the plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

For the second implementation plan document, follow the template from #file:./plan.implementation.template.md to write the implementation plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; use `.github\skills\review-ask-questions\SKILL.md` for that follow-up review step.

Based on `docs\issue/feature_request.vX.Y.Z.{topic}.md` and `docs\design.vX.Y.Z.{topic}.md`, write a `docs\plan.vX.Y.Z.{topic}.md`, which will include, in each step, add an "Step x analysis and intent (with issues, fix intent, expected outcome, step framings, complexity impact, feature preservation) before another subsection "Step x implementation" with step files involved, test first, class and behavior, completion criteria, and a third subsection "Step x addendums" with Line-budget checkpoint, Full workflow timing run readiness, Time-gated status for this step.

Each step must include the list of files to modify or to create (each name followed by a `(new, to be created)` to mark those to create, and `(existing, to be updated)` for the existing files).
Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py` , and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Do review the plan against the current test tree, but also against the current code tree as a whole, to valide both code files and test files.

Focus on massive gain tending to avoid writing and reading too many file in your propose changes.

Run your second pass focused only on implementation risk gaps, but also check the current number of lines for each file involved: anything above 550 risks getting, after code updates and additions, to exceed the 650 line limit qualifying for "big file": in case of over 550-line files, check if you can delegate/isolate the evolutions you need to a separate file (especially for test). This is not always possible for non-test files where existing functions need to be amended: do not force a resolution then: a future split phase will be needed once the plan is implemented.

Add to the plan a compact "line budget checkpoint" checklist to each step so it is ready for execution tracking, but also leave clear guidance/instruction regarding that line budget on each step: when I will tell you to implement the step 'x', said step will have everything it needs, including line budget constraint and split guidance.

Add in each step a reference to a new section which describe how to do the "execution command checklist" per step (count lines before/after, run targeted tests, run grep check). That way, you can detail that process, while mutualizing it for all step, and reference it in each step.

Mutualize your "ready-to-run-command", and add a reference to it in each step. Said command must include `.\check.bat` and pytest on the step's tests: do both until everything passes.

Prepare also a `docs\plan.vX.Y.Z.{topic}.implementation.md` skeleton (similar to docs\plan.v8.11.perf_complexity.implementation.md), with subsections Goal for step x (you can fill out this one), "Step x improvement expectations" (you can fill out this one), "What was implemented for Step x" (leave it empty for now), "New types/classes introduced for Step x" (leave it empty), "Architecture check for Step x" (empty), "Performance check for step" (empty), "Feature integrity for step" (empty).

Follow the steps detailed in `docs\plan.vX.Y.Z.{topic}.md`

### File-based IO cost Target Clarification Pass

Do a final pass on issue-design-plan-implementation to check if each designed and planed ameliorations will result in a fast operation minimizing file-based IO: the loading doc phase must now be a tiny index-read step rather than a noticeable metadata-loading delay.

Do one quick doc patch pass to add a short "file-based IO cost Clarification" section in all 4 docs so this criterion is explicit and consistent.

### Step 0 Perf-Gates Pass for new model

Do a final pass on plan: do we need a step 0 with `pytest.mark.timeout` time-bound based tests, marked as xfail, with a clear expectation of removing that xfail in the appropriate step?

If yes, do add those patches

### Final step: Acceptance tests

Make sure the final step includes acceptance tests (larger than unit test, like integration tests) that are able to validate the features are working as expected.
