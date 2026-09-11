# Why a trimmed export keeps three regions

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

The trimmer behind this reasoning is a human-run command, `tth`, invoked after
a session is exported. No skill and no workflow phase calls it implicitly, so
nothing here describes an automatic step: it explains what a person gets back
when they run it deliberately.

🤖 An exported session is written for the terminal, not for a reader. Reducing
it to something worth pasting into a report is not a matter of deleting the
reasoning: it is a matter of deciding what a turn actually said.

## The first attempt: drop the reasoning

The obvious rule is to remove the thinking blocks and keep everything else. It
is also the rule that fails, and it fails quietly.

A modern export already collapses reasoning. What is left under a prompt is one
answer block per command the session ran, each with its output stacked
underneath: file writes, diffs, test runs, shell results. On a long working
session that traffic is most of the transcript. Dropping only the reasoning
removes a handful of lines out of hundreds and returns a transcript that is
still unreadable, while looking like the tool did its job.

The trimmer therefore does not ask which lines are reasoning. It asks which
lines are the conversation.

## What a turn is made of

A turn has a recognizable shape, and the same shape in both supported exports:

- someone asks something;
- the session says what it is about to do;
- it works, sometimes for a long time;
- it says what it did.

Three of those four are worth keeping, and they are the three regions:

- **the ask**, from the prompt line to the first answer marker, blank lines and
  all, because a question has to be read the way it was written;
- **the opening**, the run of lines under that first marker, which is the plan
  the turn announced before it started working;
- **the answer**, the last block of the turn, which is the part a future reader
  came for.

Everything between the opening and the answer is the work. It was necessary to
produce the answer and it is evidence of nothing once the answer exists.

## Why the last block wins

The answer region is not chosen by content. It is chosen by position: the last
answer block of the turn, whatever it holds. Every earlier block resets the
region as the scan advances.

This is deliberate. Deciding by content would mean guessing which block "looks
like an answer", and a tool that guesses on a transcript is a tool that
silently drops the paragraph you needed. Position is not a heuristic: a turn
ends when the next turn opens, and the block that closes it is the one the
session finished on. A turn cut short, with no closing line at all, still keeps
its last block for exactly the same reason.

The cost is honest and bounded: a turn whose real answer came in two blocks
separated by a tool call keeps only the second. The alternative, keeping every
block, is the failure this design exists to avoid.

## Why the reflection line stays

The reflection line that closes a Claude turn is kept even though its body is
dropped, and the recap line under it comes back with it.

A trimmed transcript that hides its own edits is a transcript nobody can trust.
Keeping the marker line says, in one line and in the export's own vocabulary,
that reasoning stood here and was removed. The reader knows the answer did not
arrive out of nowhere, and knows where to look in the original if it matters.
The recap, when the export wrote one, is the session's own summary of that
removed work, so it is the cheapest possible replacement for it.

## What this buys

Blank lines never end a region, because a question written in paragraphs is
still one question. Text before the first prompt is dropped, because a region
belongs to a turn and a turn opens on a prompt. And a run that would keep
nothing at all stops with an error rather than handing back an empty clipboard.

The result reads as a conversation: what was asked, what was promised, what was
delivered. That is the artifact worth keeping in a report, and the one worth
handing to the next model as context.

Related: [Trim an exported conversation](../how-to/trim-an-exported-conversation.md)
and [the trim-thinking command reference](../reference/trim-thinking-command.md).
