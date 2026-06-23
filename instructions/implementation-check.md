# Implementation check instructions

Your goal is to analyze if the step from the `docs\plan.vX.Y.Z.<topic>.md` plan in your context -- step indicated in your prompt -- has been fully implemented, based on the files present in your context, or based on a Git diff `a.diff` present at the root folder of the project. Write this analysis as a markdown answer, and update `docs\plan.vX.Y.Z.<topic>.validation.md` with that analysis.

Check your prompt and your context for the step to check, for example "step 2 v9.3.0 sentinels", checking if yes or no step XXXXX from `docs\plan.vX.Y.Z.<topic>.md` was fully implemented, and asserting the state of the DDD-Hexagonal architecture (is there any smell or violation?).

Read first the `docs\plan.vX.Y.Z.<topic>.md` plan in your context, and only check the step you were instructed to in the prompt.

Start with a general short confirmation in the `### Analysis of Step N implementation state` section. Its first sentence MUST be one of these two sentences, copied verbatim from [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md) (with `N` replaced by the step number):

- `Yes. Step N has been fully implemented.`
- `No. Step N has NOT been fully implemented.`

Write nothing else as that first sentence: no other introduction sentence, no `Step checked:` prefix, no restatement of the step title. Only that one Yes-or-No sentence.

After that first sentence, leave one empty line, then write a short summary of why the Yes or No status has been reached, exactly as the template orders it (first sentence, empty line, then summary). For a `No`, this summary is a short prose explanation only: keep it separate from the actual `### Missing work for Step x` sub-section, which holds the concrete bullet work list. The summary says why the step is not yet done; the `Missing work for Step x` section lists each missing element to implement.

- if it is not yet implemented, do not write code, but explain what is missing, and record it as a `### Missing work for Step x` sub-section of the validation plan, placed right after `### What was implemented for Step x` as the template orders it: one bullet per missing element (code, test, wiring, or a file over the line budget), each concrete enough to be implemented without re-deriving this analysis. Any first sentence other than the exact `Yes. Step N has been fully implemented.` counts as not implemented for this rule, and the not-implemented case is always written as the exact `No. Step N has NOT been fully implemented.` sentence: a softened wording such as "partially implemented", "mostly implemented", or "implemented except ..." is not allowed as the first sentence, and any such state is still recorded as `No. Step N has NOT been fully implemented.` followed by the detail, so it requires the section. Gaps already described in the Architecture, Performance, Unit test coverage, or Feature integrity sub-sections must be repeated here as bullets: noting them there does not replace this section. That section is the single work list the [`implement-missing-step.md`](implement-missing-step.md) instruction reads, so a not-fully-implemented status without a `Missing work for Step x` section is an incomplete check.
- if it is, do not write code, but write a `## Analysis of Step x Implementation` section in which you summarize the goal and detail the implementation changes done to implement said goal. Detail also any new type or class introduced in the context of said implementation. When a previous check left a `Missing work for Step x` section and the step is now implemented, remove that section: its work list is done and would otherwise read as still pending.

Then, in case it is fully implemented, write also a sub-section `### Architecture check for Step x`, in which you assess if you detect any DDD-Hexagonal (adapters-ports) architecture violation or smell, any layer using other layers it should not, or other internal lib it should not. In particular, is there any class which is importing another class it should not (either a layer importing another wrong layer, or importing a technical lib when it should be business-only). Is there any function whose intent should not be in a particular class or layer?

Follow the per-step section structure defined in [`write-plans.validation.template.md`](../templates/write-plans.validation.template.md), which is the template of the `docs\plan.vX.Y.Z.<topic>.validation.md` document you update.

`a.diff` in your context is updated: do you see any DDD-Hexagonal smell or violation?

Is there any new computation which could be O(n^2) or O(n log n)?

Is there any existing feature or reporting capability impaired?

At the end of the "Architecture check for Step x", add a simple short phrase stating if, yes or no, there is anything possibly needed fixing (architecture smell, or violation, or girth too big, or anything else).  
Again, if anything is mentioned, even "acceptable", even "for later", even if "minor", it counts as "yes, there is something that needs to be addressed". If nothing is mentioned, it counts as "no, there is nothing that needs to be addressed".

At the end of the "Performance check for Step x", add a simple short phrase stating if, yes or no, there is any performance issue that needs to be addressed.

Then write a sub-section `### Unit test coverage check for Step x`, focused on unit tests only, the ones under `src\pdfss\tests\unit`, not integration, smoke, regression, or acceptance tests. For each class file impacted by the step, check that its unit tests sit in a test file, or a test folder named after the class, designed to reach 100% coverage of that one class file. If a legacy unit test impacted by the step does not reach 100% of its class, say so and note it must be completed. Other test types carry no coverage target and may cover several classes at once, so do not hold them to 100%. Do not run groundhog (`ghog day`, `ptr`) or any test command to confirm this: reason from the code and the tests in your context.

At the end of the "Unit test coverage check for Step x", add a simple short phrase stating if, yes or no, there is any unit-tested class below 100% that needs completing.

When writing an answer in markdown, follow instructions from [`markdown.md`](../rules/markdown.md).

Note how each list item uses only one space between a list item marker and the list item content: `- **Change 2**: explain ...`, not `-   **Change 2**: explain ...` (3 spaces after the list item marker dash).

Check your answer: do you see list items with 3 spaces as in `-   xxx`? Change them to one space: `- xxx`.

Check your validation plan update: re-read the status sentence you wrote under `### Analysis of Step N implementation state`. It MUST be exactly `Yes. Step N has been fully implemented.` or `No. Step N has NOT been fully implemented.`, with no other introduction sentence and no `Step checked:` prefix. If it is not the exact `Yes. Step N has been fully implemented.` sentence, search the updated document for the `### Missing work for Step N` heading. If that heading is absent, the check is not finished: add the section with the gathered missing-element bullets before ending your answer.

## Handoff

When the check is written and the `Analysis of Step x` status line records the Yes-or-No verdict in the validation plan, hand the cycle on, with no menu. From the project root, run:

- `pw handoff after-check <x>`

`<x>` is the plan step you just checked — the "step XXXXX" of your prompt, a number such as `2` or a sub-step id such as `4A`. `pw` is the `<llm-shared>\bin\prompt_workflow.bat` launcher (the `pw` alias of the project environment), the same tool the interactive cycle uses.

Run `pw` from a PowerShell shell — the `pw` alias when the project environment is loaded, otherwise `& "$env:LLM_SHARED_DIR\bin\prompt_workflow.bat" handoff after-check <x>`. Do not wrap `bin\prompt_workflow.bat` in a `cmd /d /c "..."` call from a Git Bash or other POSIX shell: that nested `cmd` swallows the launcher's output and its rewrite of `a.prompt.txt` and `a.prompt_memory`, so the handoff does nothing while still returning `0` — a silent no-op. The launcher must print `Prompt for step <x> (commit) ready` on a `Yes` (or `(implement-missing) ready` on a `No`); if you do not see that line, re-run it in PowerShell before going on.

The `after-check` task is neutral on purpose: `pw` reads the `Analysis of Step x` status line you just wrote and routes the branch itself, so the caller cannot mis-branch. It writes the `implement-missing-step.md` prompt when the line starts with `No`, or the commit prompt (`group-commits-msg.md`, the `git add -A` variant) when it starts with `Yes`, to `a.prompt.txt` at the project root, copies it to the clipboard, and records the step in `a.prompt_memory`. Confirm it took — the first line of `a.prompt.txt` now names that next instruction — then read `a.prompt.txt` and run the instructions of that returned prompt straight away. A handoff is the go-ahead to perform the next workflow step now: do not pick the Yes-or-No branch yourself, do not stop to ask whether to proceed, and do not compose the next prompt yourself. When the branch is the commit step, prepare the grouped commit messages in `a.commit` right away — preparing `a.commit` is the step and does not wait on a go-ahead. Because the commit handoff stages the whole tree with `git add -A`, the `group-commits-msg.md` run must cover **every** staged change, not only the files you touched for this step: a change of outside origin already in the working tree — a concurrent edit, a tool-written file, an earlier unrelated tweak — is staged too, so it joins the same `a.commit` run and is grouped from least to most dependent like any other. Never drop or hold back a staged change because you did not author it; rank it by its own dependencies and place it in a fitting group. The actual commit is a separate action: it follows `group-commits-msg.md`'s own review-and-go-ahead gate (the user says "go ahead"), never run on your own off the back of the handoff. `pw` reads the status line and the handoff authorises the next step, so the cycle advances on its own.

**Hard rule — do not stop before the commit gate.** After this check you run `pw handoff after-check <x>` and then the `group-commits-msg.md` run straight away, with no pause to ask whether to proceed and no pause because the session has been long or the change large. The only stop in the implement-check-commit cycle is the commit gate: `a.commit` prepared and presented for the user's "go ahead". Stopping after the check, or before the grouping, to ask the user anything is the mistake this rule forbids.
