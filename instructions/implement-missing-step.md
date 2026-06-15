# Implement the missing work of a step

Your goal is to finish the missing work of the plan step named in your prompt, not to redo the whole step. The validation plan `docs\plan.vX.Y.Z.<topic>.validation.md` in your context has marked that step "No, it is not implemented" and listed what is left in its `### Missing work for Step N` section. Read that section first and treat it as the work list for this step.

Include "Step XXXX" in the title of this conversation (replace XXXX with the step mentioned in the prompt).

## Two kinds of missing work for the step

The missing work falls into two kinds, and one step may need both. Decide, for each item of the `Missing work for Step N` list, which kind it is, then apply the matching flow:

- missing code or tests: follow [`implement-step.md`](implement-step.md) and write only what the `Missing work for Step N` section reports as absent. Verify with one `ghog day` walk as that instruction describes — do not run `check.bat` or `pytest` directly; groundhog is in charge of check and tests.
- a file over the line budget: follow [`split-large-file.md`](split-large-file.md) and split the over-budget file by responsibility. Split it, do not reduce it: never trim code, docstrings or comments to fit the 650-line limit. Splitting keeps every responsibility in its own smaller file; reducing would drop behaviour the step still needs.

When a step is incomplete only because a file grew too big, the split alone closes the gap. When code or tests are genuinely absent, write them. When both are true, split first so the new code lands in a file that is already under budget.

Both flows end with a `ghog day` walk, and that is fine: a walk right after a green one, with no file changed since, is a noop (one notice, exit 0), so duplicate groundhog calls cost nothing.

## Project rules for the missing-work step

Read first your project instructions (`CLAUDE.md`; `copilot-instructions.md` for Copilot users). Read them and the context documents with your file tools, never through an environment wrapper, and follow [`run_commands.md`](../rules/run_commands.md) for every shell command: one shell per command, no nested quoting, targeted reads, no verbatim retry after a quoting or parse error.

Do not update the validation plan itself: its `Missing work for Step N` list is this step's input, and recording the new state of the step is the separate implementation-check step.

Then, if you have files under the `src\` or `tools\` folder or subfolders in your context, check that those Python files end with `# eof`. If they do not, stop right there and list those incomplete files. If they do, go on.

Preserve existing code, comments and docstrings, and follow [`preserve_code.md`](../rules/preserve_code.md): write each changed file in full, with no `# ...existing code...` placeholder, and update the top docstring of any class you change to explain the fix.

When writing an answer in markdown, follow [`markdown.md`](../rules/markdown.md).

## Handoff

When the missing work is implemented and the `ghog day` walk reports the objective (`exit=0`), hand the cycle back to the implementation check, with no menu. From the project root, run:

- `pw handoff check <x>`

`<x>` is the plan step whose missing work you just filled — the "Step XXXX" of this conversation, a number such as `2` or a sub-step id such as `4A`. `pw` is the `<llm-shared>\bin\pw.bat` launcher (the `pw` alias of the project environment), the same tool the interactive cycle uses.

The call writes the `implementation-check.md` prompt for step `<x>` to `a.prompt.txt` at the project root, copies it to the clipboard, and records the step in `a.prompt_memory`, so the gap you just closed gets re-checked. Then read `a.prompt.txt` and follow the instructions of that returned prompt. Do not compose the next prompt yourself: `pw` builds it, so the cycle advances on its own.
