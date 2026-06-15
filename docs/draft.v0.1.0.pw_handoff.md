# v0.1.0 pw-handoff draft -- automatic handoff between the implement, check and commit steps

## The need for the pw handoff

The `pw` (prompt-workflow) tool generates, for each stage of the document-and-implement workflow, the next prompt to give an LLM, and copies it to the clipboard. During the implement cycle -- implement a step, check it, then commit, or fix the missing work -- the tool resolves the next prompt from an interactive menu: a human picks implement, check or commit for the current plan step.

The need is to take the human out of that loop, so a finished step hands off to the next on its own:

- after an implement-step, hand off to the implementation-check for the same step;
- after the check, hand off to the commit when the step is verified ("Yes"), or to the implement-missing work when it is not ("No");
- after the implement-missing work, hand off back to the check.

## Desired outcome for the pw handoff

- A non-interactive way to ask `pw` for one named step's prompt, so the chain runs without the menu.
- Each cycle instruction (implement-step, implementation-check, implement-missing-step) tells the LLM which `pw` call to make next and to follow the prompt it returns.
- The handoff reuses the existing cycle prompts and leaves the repository in the same state the menu would, so an interactive run after a handoff stays consistent.

The detailed design and the decisions (Q56 to Q64) that answer this need are in [`design.v0.1.0.pw_handoff.md`](design.v0.1.0.pw_handoff.md).
