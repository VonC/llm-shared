# Implement the missing work of a step

Your goal is to finish the missing work of the plan step named in your prompt, not to redo the whole step. The validation plan `docs\plan.vX.Y.Z.<topic>.validation.md` in your context has marked that step "No, it is not implemented" and listed what is left in its `### Missing work for Step N` section. Read that section first and treat it as the work list for this step.

Include "Step XXXX" in the title of this conversation (replace XXXX with the step mentioned in the prompt).

## Two kinds of missing work for the step

The missing work falls into two kinds, and one step may need both. Decide, for each item of the `Missing work for Step N` list, which kind it is, then apply the matching flow:

- missing code or tests: follow [`implement-step.md`](implement-step.md) and write only what the `Missing work for Step N` section reports as absent. Run `check.bat` (or `c`) until it is clean, then run the focused `pta` tests as that instruction describes.
- a file over the line budget: follow [`split-large-file.md`](split-large-file.md) and split the over-budget file by responsibility. Split it, do not reduce it: never trim code, docstrings or comments to fit the 650-line limit. Splitting keeps every responsibility in its own smaller file; reducing would drop behaviour the step still needs.

When a step is incomplete only because a file grew too big, the split alone closes the gap. When code or tests are genuinely absent, write them. When both are true, split first so the new code lands in a file that is already under budget.

## Project rules for the missing-work step

Read first your project instructions (`CLAUDE.md`; `copilot-instructions.md` for Copilot users).

Then, if you have files under the `src\` or `tools\` folder or subfolders in your context, check that those Python files end with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on.

Preserve existing code, comments and docstrings, and follow [`preserve_code.md`](../rules/preserve_code.md): write each changed file in full, with no `# ...existing code...` placeholder, and update the top docstring of any class you change to explain the fix.

When writing an answer in markdown, follow [`markdown.md`](../rules/markdown.md).
