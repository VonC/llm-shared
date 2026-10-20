# Write implementation plan and validation plan

ultrathink: To write the two plan documents, I will first need to gather information from the design and requirement documents named in the prompt or context. I will analyze them to extract the necessary implementation details, file modifications, and rollout steps.

Check your prompt for version vX.Y.Z and topic (for instance "v9.3.0 sentinels").

Write two plan documents:

- a plan document named `plan.vX.Y.Z.<topic>.md`, in markdown format, from the design document included in your context;
- an implementation validation plan document named `plan.vX.Y.Z.<topic>.validation.md`, in markdown format, from the same design document.

Read [`../rules/docs_layout.md`](../rules/docs_layout.md). Resolve the effort
directory as the design document's parent, confirm that the related requirement
and canonical draft use that directory, and write both plans beside them. Do not
add a topic subdirectory. The plan describes implementation file by file and
the rollout steps. The validation plan records the later implementation review.
Neither document introduces design choices.

For the first plan document, follow the template from [`write-plans.template.md`](../templates/write-plans.template.md) to write the plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

For the second implementation validation plan document, follow the template from [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md) to write the implementation validation plan document, and adapt it as needed if some sections are not relevant for the specific design you are writing.

Notes for the writer:

- Keep section titles specific to the topic and version; do not reuse generic repeated titles.
- Do not seed question-referenced rows (a table row opening with `| Qxx`) or a "No open questions" row into any decisions section you write: the `pw` routing reads those rows as the mark of a consolidated review, and a fresh plan carrying them would skip its review round.
- Use the current-behavior and target-behavior sections only when the design depends on comparing flows.
- Put facts already confirmed from the codebase in the confirmed-facts section.
- Put implementation steps, file-by-file task lists, and rollout steps in the later implementation plan, not in the design.
- Do not add the open-questions section in this skill output; use the `review-ask-questions` skill (see [`review-ask-questions.md`](review-ask-questions.md)) for that follow-up review step. That review round runs on the plain plan only, not on the validation plan: it is wired as steps 8 and 9 of the `pw` workflow, between `write-plans` and the first `implement-step`.
- If that plan review later changes the numbered step list (steps added, removed, or renumbered), re-align the validation skeleton you write here so each `Analysis of Step N` section still matches a plan step, since the implement cycle reads those sections.

Based on the requirement and design beside each other in `<effort-dir>`, write
`<effort-dir>\plan.vX.Y.Z.{topic}.md`, which will include, in each step, an
"Step x analysis and intent" (with issues, fix intent, expected outcome, step
framings, complexity impact, feature preservation) before another subsection
"Step x implementation" with step files involved, test first, class and
behavior, completion criteria, and a third subsection "Step x addendums" with
line-budget checkpoint, full workflow timing run readiness, time-gated status
for this step.

Each step must include the list of files to modify or to create (each name followed by a `(new, to be created)` to mark those to create, and `(existing, to be updated)` for the existing files).
Each new test must follow the convention `...\tests\unit\xxx\yyy\...\test_filename\test_filename_tdd.py`, and you must check if a pbt is needed as well. And do not forget the `__init__.py` to create or to update, for test and non-test code.

Do review the plan against the current test tree, but also against the current code tree as a whole, to validate both code files and test files.

Focus on massive gain tending to avoid writing and reading too many files in your proposed changes.

Run your second pass focused only on implementation risk gaps, and count the current physical lines of every file involved, including blank lines, with the same metric used by the repository big-file gate. Classify each Python file by the following policy:

- below 550 lines: safe to extend. Record the baseline and the repository ceiling of 650 lines. An expected post-step count may be written as an advisory estimate, but do not invent a tighter mandatory target and do not require a split merely because the estimate is exceeded.
- from 550 through 650 lines: at risk. Avoid growth where practical and give concrete split guidance, especially for tests, but an in-place change that remains at or below 650 is not by itself incomplete and does not require a split.
- above 650 lines: over the repository limit. The plan must include a responsibility split; do not plan further growth in place.

A tighter numeric target is mandatory only when shrinking or extracting that file is an explicit goal of the step. State that reason next to the target. Otherwise the only enforceable line-budget checkpoint is the 650-line repository ceiling. If implementation exceeds an advisory estimate but remains at or below 650, record the variance as evidence without marking the step incomplete or adding mandatory split work. When an existing non-test function must be amended and a clean extraction is not yet possible, do not force an artificial split: document the risk and split only if the repository limit is exceeded or a later responsibility-focused step calls for it.

Add to the plan a compact "line budget checkpoint" checklist to each step so it is ready for execution tracking. Each checkpoint must state the baseline, policy band, 650-line ceiling, and any advisory estimate or justified mandatory shrink target. Also leave clear split guidance for files at risk or over the limit, so an implementation request for step 'x' has the applicable constraint without turning ordinary estimation variance into missing work.

Add in each step a reference to a new section which describes how to do the "execution command checklist" per step (count lines before/after, run targeted tests, run grep check). That way, you can detail that process, while mutualizing it for all steps, and reference it in each step.

Mutualize your "ready-to-run-command", and add a reference to it in each step. Run the command printed by `pw scope day`, through [`run-pw.md`](run-pw.md), so the current requirement supplies the selector at execution time. Never freeze a group selector in the plan. The default walk runs check.bat plus affected tests and deliberately skips full; follow its printed repair and restart lines until it reports the requested objective (see `GROUNDHOG.md`). Use the same resolver in shared gate loops and completion criteria. Do not plan direct `check.bat` or `pytest` calls; groundhog is in charge of check and tests.

Prepare also an `<effort-dir>\plan.vX.Y.Z.{topic}.validation.md` skeleton, with subsections Goal for step x (you can fill out this one), "Step x improvement expectations" (you can fill out this one), "What was implemented for Step x" (leave it empty for now), "New types/classes introduced for Step x" (leave it empty), "Architecture check for Step x" (empty), "Performance check for step" (empty), "Security check for Step x" (empty), "Unit test coverage check for Step x" (empty), "Feature integrity for step" (empty). Each section left empty in this initial skeleton holds the literal placeholder `_(empty — no check has taken place yet.)_.` (note the trailing period after the closing `_`, explained under "Markdown lint workarounds" below). Do not include a "Missing work for Step x" section in the skeleton: no check has taken place yet, and only an implementation check that concludes "No, it is not implemented" adds that section.

Follow the steps detailed in `<effort-dir>\plan.vX.Y.Z.{topic}.md`.

## File-based IO cost Target Clarification Pass

Do a final pass on issue-design-plan-implementation to check if each designed and planned amelioration will result in a fast operation minimizing file-based IO: the loading doc phase must now be a tiny index-read step rather than a noticeable metadata-loading delay.

Do one quick doc patch pass to add a short "file-based IO cost Clarification" section in all 4 docs so this criterion is explicit and consistent.

## Step 0 Perf-Gates Pass for new model

Do a final pass on plan: do we need a step 0 with `pytest.mark.timeout` time-bound based tests, marked as xfail, with a clear expectation of removing that xfail in the appropriate step?

If yes, do add those patches.

## Pre-final step: Acceptance tests

Make sure the plan includes acceptance tests (larger than unit test, like integration tests) that are able to validate the features are working as expected before the security review.

## Mandatory Pre-Closure Step: Security & OWASP Top 10 Review

Every implementation plan MUST include a dedicated security review step before closing the effort (as the final step following or concluding acceptance tests). This step evaluates the cumulative diff of the entire effort against the OWASP Top 10 to ensure that no side effect of the new code introduces a vulnerability or security regression.

The security review step must:

1. Audit all modified entry points, data flows, and external integrations against the OWASP Top 10 (broken access control, injection flaws, cryptographic failures, insecure design, security misconfigurations, vulnerable components, identification/authentication, software/data integrity, logging failures, SSRF).
2. Validate that untrusted inputs are sanitized, path traversal is impossible, shell calls use safe execution, and no secrets or credentials are leaked in code, tests, or logs.
3. Verify that all automated security checks (such as pre-commit sensitive-content checks or security linters) pass cleanly.
4. Record findings in the validation plan's OWASP Top 10 audit matrix with a strict pass/fail verdict. Any Critical or High severity finding requires remediation before the effort can be marked implemented.

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
`Performance check`, `Security check`, `Unit test coverage check`, `Feature integrity`) with that
exact placeholder, `_(empty — no check has taken place yet.)_.`, and opens each
step's `Analysis of Step N implementation state` with the sentence "Not started.
Step N is not implemented because ...". An implementation check later replaces the
placeholders with real findings.

## Handoff

Before using or showing a host-prefixed workflow command, read
[`../rules/command_prefix_char.md`](../rules/command_prefix_char.md) and use its
prefix rule.

When `<effort-dir>\plan.vX.Y.Z.<slug>.md` and its validation skeleton are
written, hand the cycle on to the plan review, with no menu and no go-ahead.
From the project root, in a PowerShell shell, run the explicit post-write form
through the `pw skill` launcher (see [`run-pw.md`](run-pw.md) for the
non-interactive invocation; the bare `pw` alias does not resolve in a tool
shell):

- `pw skill --after-write plan`

The explicit post-write form prints the exact
`<command-prefix>review-ask-questions on <plan-path>` line (with the prefix
selected by `command_prefix_char.md`) regardless of settled-looking content in
the new plan. The review runs on the plain plan only, never the validation plan.
Read that line and run it straight away: a handoff is the go-ahead to perform
the next step now, so do not stop to ask whether to proceed, and do not compose
the next prompt yourself.

To hold the chain here instead — to read the plan before the review runs — pass the literal phrase `stop here` in this skill's argument when you invoke it. With `stop here` in the argument, write the plans and skip this handoff.
