# Why the LLM reviews its own work

<img src="../assets/logo-llm-shared-review-transparent.png" alt="" height="90" align="right">

<!-- markdownlint-disable MD013 -->

🔁 The key insight of the workflow: never ship the first pass. Blindly
trusting what the model generates — even documentation — throws away the
cheapest quality gate available: the model itself, asked to challenge
what it was given and what it produced.

## 🔁 Two review loops, same principle

The workflow runs the loop twice, once per kind of output:

- **Documentary review** — `/review-ask-questions` challenges a
  requirement, design or plan the moment it is written. The questions it
  raises are a signal of depth: a model that truly parsed the requirement
  asks about edge cases and contradictions; one that skimmed it asks
  nothing. `/consolidate-then-review-ask-questions` folds the human
  answers back and loops until the document settles.
- **Implementation check** — `/implementation-check` confronts the code
  just written with the plan step it claims to implement, and writes an
  explicit `Yes.` or `No.` verdict into the validation document, backed
  by architecture, performance, coverage and feature-integrity checks.

## 🎣 What each loop actually catches

The documentary loop catches ambiguity while it is still cheap. A real
example from the presentation deck: a requirement said dates could be
"invalid" without saying what invalid meant; the review turned that word
into a question with three options, the human picked a fourth, and the
decision table kept the choice — before a line of code depended on a
guess.

The implementation check catches the plausible-but-incomplete. Another
real example: a plan step was reported done, tests passed, but the check
found the progress-log wire was never actually written — verdict `No`,
with the missing work listed; `/implement-missing-step` filled the gap
and the second check said `Yes`. Code that compiles and passes its own
tests can still not match the plan.

## 📏 Why the verdict is a fixed sentence

The check's first sentence is exactly
`Yes. Step N has been fully implemented.` or
`No. Step N has NOT been fully implemented.` because a machine routes on
it: `pw handoff after-check` lets `pw` read that line and pick the branch
— fill the gaps, or move to the commit. A free-form verdict would put a
human back in a loop that runs fine without one.

## 🙋 The human answers, the model asks

Note the inversion: in both loops the model asks and the human decides.
The review table (`Q0x | Title | Recommended Answer`) is the only stop of
the document phase — everything else chains. The model is good at
spotting what is unclear; the human is the only one who knows what was
meant.

## 👉 Where to read the mechanics

- [Answer a review round](../how-to/answer-a-review-round.md) for the
  documentary loop step by step.
- [Run the implement chain on one plan step](../tutorials/04-run-the-implement-chain.md)
  for the check inside the chain.
