# Explain undecided specification questions

Use this workflow to explain and record human decisions for the exact
requirement, issue, design, or implementation plan selected by the user.
It is the requestor's human discussion phase after specification convergence.
Do not take a reviewer role, consolidate, stage, or commit through this skill.
Preserve every existing question ID, option, recommendation, and explanation.

## Enter or resume the discussion

Read [the shell rules](../rules/run_commands.md). Resolve `<LLM_SHARED_DIR>`
from this canonical file's parent `instructions` directory. Resolve the exact
document from the user's path or the unambiguous active specification; never
pick between several documents by modification time.

For a live review, use [review-resume.md](review-resume.md) for identity and
ownership pickup when needed, then [spec-review-requestor.md](spec-review-requestor.md).
Only enter the discussion at its `convergence-gate`. If a round is pending,
finish that requestor round first. An already authorized owning action follows
its durable authorization; this skill does not reset it. With no live exchange,
the user may request explanations directly; retain the independent-review gate
for the later handoff and do not claim independent convergence occurred.

Selecting `Explain undecided questions`, or explicitly invoking this skill,
authorizes recording the user's answers, introducing the notions the user asks
about in the effort's documents, and a follow-up independent review after all
questions are decided. Tell the user this when starting. It does not authorize
consolidation. Honor a later hold or scope correction.

Run the read-only scanner from the consuming project:

```powershell
& "<LLM_SHARED_DIR>\bin\question_decisions.bat" <document-path>
```

Read its JSON and exit code. An `Answer to Qxx` heading or a recommendation is
not a human decision. Only explicit records in that answer section count.
Exit 2 or diagnostics require reconciliation before advancing; never treat a
failed scan as zero remaining questions. The
[scanner reference](../wiki/reference/question-decisions.md) defines the fields.

Keep a task-owned continuation note named
`a.question-explanation.<document-stem>.local.md` in the configured artifact
home, using [the state template](../templates/question-explanation-state.template.md).
Resolve that home under [artifact_files.md](../rules/artifact_files.md), or use
the validated home returned by the live exchange. This note is not protocol
coordination or a reviewer `QUESTION_STATE` capture. Never put ownership tokens
in it. Update it after each explanation, recorded answer, and review handoff;
write a complete temporary replacement and replace the old note atomically.

Read an existing note before starting a new batch. Reconcile its document,
exchange, round, digest, and question identities with current disk and protocol
state. A digest change demands reconciliation, not an automatic reset. If IDs
were removed or reordered, do not silently recalculate progress or assume a
decision. Resolve the changed scope with the user when evidence is insufficient.
If appended questions or a reopened earlier question fall outside the captured
batch, reconcile the batch scope before displaying progress. Never display a
negative percentage or one above 100%, or silently reset `I` to hide the change.

## Gather the context shown with every question

Every explanation opens with where its question sits: umbrella, item, topic,
phase, draft, document and review. Gather that context before the first
explanation of a batch and again after every resume, then save it in the
continuation note. Run, from the consuming project:

```powershell
& "<LLM_SHARED_DIR>\bin\prompt_workflow.bat" progress
```

When its `topic` line names the document's version and slug, copy its `topic`,
`umbrella` and `phase` lines; `pw progress` calls an umbrella item a topic, as
in `topic 2/8`. Otherwise read the topic's own draft,
`draft.<version>.<slug>.md` in the document's effort directory: its
`- Umbrella:` line names the umbrella draft, whose status table gives the
item's position in table order, its key title and the completed rows. A topic
outside any umbrella reads `none, standalone topic`. Add the document path and
type, the batch range and the review identity. Write `not resolved` for a value
neither source establishes; never guess it.

## Compose the big picture shown before every question

The context table says where a question sits, not what the project is for or
how the behavior being decided fits into it. A user who reads specification
questions one at a time loses that picture. So, after the context table and
the question's status, every explanation describes the project around the
question, from the widest scope down to the question, and only then explains
the question itself.

Compose the picture once per batch, after gathering the context, from these
sources read in this order:

1. The umbrella draft, when the topic belongs to one: its goal, its items in
   table order with the completed ones, and what this item adds to it.
2. The topic draft: the situation it starts from and the outcome it asks for.
3. The effort's other documents in the same effort directory: the feature
   request or issue, the design and the plan, whichever exist, with their
   settled decisions. For a plan question, read the plan's step list too.

Save the result in the continuation note's big-picture section: the purpose,
the numbered walkthrough steps, and the step or component each batch question
concerns. Write `not resolved` for a part no source establishes;
never fill a gap with a guess. Recompose it after a resume, and after a
recorded decision that changes the flow.

Render it before every question of the batch, not only the first: the user may
read each question on its own. From one question to the next, only the marked
step, the diagram's labelled node, the close-up and the question part change.
Write it in plain language, as these parts in this order:

- Purpose: one bold sentence on what the project is for, the document under
  review, and the implementation state, such as
  `Implementation has not started`. For an umbrella item, start with the
  umbrella's goal and this item's place among its items, then the topic's own
  purpose.
- Today and after: what exists now and what the project changes, with a short
  table of its main parts when it has several.
- Terms: define each tool-specific word the explanation relies on where it
  first appears, such as what pytest calls a plugin. A notion the user already
  asked about gets the fuller explanation that
  [the notions section](#explain-a-notion-the-user-asks-about) requires.
- Walkthrough: a numbered end-to-end flow of how someone uses the result, on an
  ordinary concrete case, with the step this question concerns marked by its
  ID, such as `This is the part involved in Q02`.
- Flow diagram: a small diagram of that flow and of the other routes into it,
  such as a Mermaid flowchart, with the question's node labelled with its ID.
  A Mermaid diagram follows
  [the Mermaid rules](../rules/markdown.md#mermaid-diagrams-that-codex-can-draw),
  or Codex shows its source instead of drawing it: at most 40 columns per
  label line, split with `<br>`, at most 16 nodes and 24 edges, no `subgraph`
  or `style`, and `flowchart TD` kept under 80 columns.
- Close-up: the parts next to the question's step, what they compute or check,
  and the earlier decisions that constrain them, cited by ID and choice, such
  as `Q01=A3`.
- The question: what it asks at that step, separating the behavior already
  required from what is still to choose, then the options, and where the
  choice lands in the plan or rollout, such as step 4 of 7, with the steps
  before and after it.

Keep each part short for a small topic: a few sentences, a few walkthrough
steps. The picture places the decision; it does not widen what is decided.

## Explain one question and record one decision

For a new batch, save `I` as the first undecided question's **position** and
`Total` as `question_count`. Save their question IDs and the ordered batch IDs
too. Keep `I` fixed through answers and pauses; the scanner never owns it.
Use document positions for arithmetic, so non-contiguous numeric IDs work.
For the current position `x`, display
`{question-id}/{last-question-id} {percentage}%`, where IDs include their `Q`
prefix, and:

```text
percentage = round(100 * (x - I + 1) / (Total - I + 1))
```

This is position in the explanation sequence, not a claim that the displayed
question has been decided. Q59 through Q73 yields `Q59/Q73 7%` at the start
and `Q73/Q73 100%` on the last question. A single-question batch displays 100%
but remains awaiting a decision until the user answers. An empty batch has no
percentage. Skip already decided questions without changing `I` or renumbering.

1. Select the first remaining undecided question from a fresh scan. Read its
   full block and dependencies, including any relevant earlier user comments.
2. Explain it with [question-explanation.template.md](../templates/question-explanation.template.md):
   the saved context table first, with this question's position and the
   current undecided count, then its status, then
   the big picture with this question's step marked, as
   [composed above](#compose-the-big-picture-shown-before-every-question),
   then concrete behavior, realistic example, options and tradeoffs,
   recommendation, effects on other questions, and where the choice lands.
   Keep the decision within the document's scope; its context comes from the
   umbrella, the draft and the effort's other documents too.
3. Save `awaiting-user-decision`, the question ID, and whether the explanation
   was delivered. Then end the turn with an actual choice, as
   [ask for the decision](#ask-for-the-decision-as-a-choice) describes, and
   wait for its answer. Do not answer on their behalf or advance because they
   asked for more explanation. A question about a notion follows
   [Explain a notion the user asks about](#explain-a-notion-the-user-asks-about).
4. On an explicit choice, update only that question's answer and necessary
   clarifications. Replace its active pending marker with
   `User decision: confirmed — <choice and agreed qualifications>`, with the
   rationale, relevant comments, and decision date nearby. Preserve the
   historical recommendation even when the user chooses differently. Existing
   `Confirmed by the user: ...` records remain valid and need no conversion.
   Move superseded status prose into a clearly quoted historical note if it is
   needed; do not leave both pending and confirmed as active records.
5. An explicit user decision that a conditional question is inapplicable can
   be recorded as confirmed with its condition and reason. A dependent question
   is not automatically decided by another answer. Record a deferred choice as
   `User decision: deferred`; it remains undecided.
6. Rescan the whole document without `--after` before choosing the next item.
   `--after Qxx` is a navigation aid only; earlier unresolved questions still
   count. Persist `explaining` with the next question, or the final phase below.

Targeted answer/clarification edits, and the notion introductions below, are
authorized here; do not run `oqm --strip` or regenerate the entire question
section merely to record an answer. Keep decision comments in the document,
with a concise change list in the private note for the next review request. If an answer reopens an earlier decision,
record that explicitly rather than retaining a misleading confirmed status.

## Explain a notion the user asks about

While a question awaits a decision, the user may ask what a notion means: a
term, a component or a mechanism the explanation relies on. An answer given
only in the chat leaves the documents with the same gap for their next reader.
So answer it in the chat, then:

1. Introduce and explain the notion in every document of the effort that
   relies on it, from the widest to the narrowest: the umbrella draft when
   there is one, the topic draft, then the requirement, the design and the
   plan, up to and including the document under review. Do not create a
   document the effort has not reached yet. Place the explanation where the
   notion first appears in each document, at that document's level: what it
   is and why it matters in a draft, how it behaves in the requirement, how it
   is built in the design, where it is built in the plan.
2. Change only how the notion is introduced and explained. Keep every
   decision, question ID, option, recommendation and recorded answer as they
   are. When an explanation would change a decision, raise that with the user
   as a question instead.
3. Record the notion in the continuation note's notions section: its name, a
   short definition, the question that raised it, and each document and
   section updated. Refresh the note's document digest after the edit, and
   add the edits to the change list, so the follow-up review examines them
   with the decisions.
4. Return to the pending question and ask its choice again, as
   [ask for the decision](#ask-for-the-decision-as-a-choice) describes.

Every later question of the batch, or of a later batch on the same document,
that involves a recorded notion explains it again where it first appears in
that explanation, in more detail than the previous time: what it is, how it
applies to this question, and where the documents now introduce it. Never
treat one explanation as having made a notion familiar.

## Ask for the decision as a choice

Every explanation ends with a choice the user can act on, and the agent shows
as waiting for it, never with the options written as text only. A turn that
ends in prose looks finished: the host and pane monitors such as tuios show
the agent as done or idle.

Read [interactive_menu.md](../rules/interactive_menu.md) and use the host's
blocking choice when the current turn lists one: `AskUserQuestion` in Claude
Code, `request_user_input` in Codex (Plan mode, or Default mode with its
feature on), or an IDE picker.

- Offer this question's options as entries, the recommended one first with
  `(Recommended)` after its label. Each description names the resulting
  behavior in a few words.
- Add an entry to explain more when the host has room for it. Amendments go
  through the host's free-text entry, such as `Type something else`. When the
  host caps the entry count, keep the question's options and drop the
  explain-more entry first. With more options than fit, keep the recommended
  one and the most distinct others, and name the rest in the question text.
- Make the question text stand alone, since the dialog can hide the
  explanation: repeat the progress line and question title, such as
  `Q60/Q73 13%: <title>`, and the decision asked.
- Without a blocking choice, as in Codex Default mode, end with the numbered
  chat list of the same entries, and report the question as `blocked` first,
  as interactive_menu.md describes for a decision no picker holds. Its `--msg`
  is the question text's first line, such as `Q60/Q73 13%: <title>`.

A typed reply, in the free-text entry or in chat, still counts. Read it as a
choice, an amendment or a request for more explanation. Never take the
recommended option as chosen unless the user selected or wrote it. After a
`blocked` report, report `working` before recording the answer, as
interactive_menu.md's "Report the end of the wait" describes.

## Finish with a fresh independent review

When a successful full scan shows zero undecided questions, save
`follow-up-review-required` **before** any review command, and tell the user:

> All questions now have recorded user decisions. A new review round must
> examine those decisions and your comments for inconsistencies and identify
> any additional questions they raise.

The retained convergence answer describes the earlier document. It does not
review the subsequent human decisions and comments. Keep all question blocks.
If the skill starts with zero undecided questions and no saved discussion or
post-convergence changes, report that fact and return to the ordinary gate;
do not invent an explanation batch or a required duplicate review.

Unless the user has placed a hold, use the already recorded follow-up authority:

- At the same live `convergence-gate`, the specification requestor calls
  `confirm` with the existing exact label `Revise and review again`, including
  the user's guidance. Never send `Explain undecided questions` to `confirm`.
- If there is no live exchange, apply
  [specification-review-gate.md](../rules/specification-review-gate.md) and enter
  the specification requestor for this exact document. This skill's explicit
  invocation authorizes the independent review setup, but does not create or
  contact a reviewer session; role isolation still applies.

The replacement request must identify the decided questions, recorded comments,
and changes since convergence, including the notion introductions in each
document, and ask for full-specification consistency,
effects on earlier decisions and related documents, and missing/new questions.
Reviewer recommendations cannot overwrite human choices; surface conflicts.
Use the ordinary requestor publication and exact-answer wait. Before publishing
after an interruption, inspect the existing exchange: resume an advanced or
already-published round, never confirm or publish it twice.

After successful publication, record `follow-up-review-in-progress`, the round
and publication evidence in the note. At subsequent convergence, mark this
batch `reviewed` with the new round and reviewed-document evidence. New
undecided questions receive a new batch and starting `I` when the human selects
explanation again. With none remaining, present the ordinary consolidation or
another-review choices. All decisions plus review never auto-consolidate.

## Pause and resume

[pause-session.md](pause-session.md) copies the phase, fixed `I` and endpoint,
current/next IDs, decision status, follow-up authority, and exact next action
into its snapshot, linking the continuation note. Resume rescans, gathers the
question context again, recomposes the big picture from its sources, and
reconciles:

- `explaining`: explain the first still-undecided question using saved `I`.
- `awaiting-user-decision`: restore the pending question; retain any delivered
  explanation and continue its clarification or answer rather than skipping it.
  The previous session's choice died with it: ask the choice again, with the
  `blocked` report when no blocking choice holds it.
- `follow-up-review-required`: initiate the authorized replacement review.
- `follow-up-review-in-progress`: resume that round through review ownership.
- `reviewed`: use the current convergence gate, without launching a duplicate.

A saved phase never restores review ownership or grants missing permission.
If a user's answer was durably recorded just before interruption, the scan may
advance the stale note. If zero remain, move to the required-review phase even
when the pause occurred between recording the last answer and updating the note.
