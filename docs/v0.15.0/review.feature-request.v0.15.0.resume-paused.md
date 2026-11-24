# Specification review transcript for v0.14.0

- Exchange: specification/feature-request/v0.14.0/resume-paused
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-11-07T17:13:32+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for feature-request resume-paused (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 1

### Requestor assessment for feature-request resume-paused (round 1)

The reviewed requirement is docs/v0.14.0/feature-request.v0.14.0.resume-paused.md,
derived from the sibling draft.v0.14.0.resume-paused.md. There is no umbrella.

The requirement covers discovery across TUIOS sessions, the existing prompt
and receipt state rules, checkout-wide duplicate-resume protection, protected
panes, agent-specific commands, optional clearing, acceptance evidence,
preview output, and exit status. Its test scope is whole suite.

Please independently assess the whole specification against the source draft,
including omissions, conflicting requirements, unsafe acceptance behavior,
and any missing questions. Keep this feature-request review focused on scope,
expected behavior, edge cases and acceptance criteria rather than design or
implementation choices.

There are thirteen open questions, Q01 through Q13. Each has options, pros
and cons, a recommendation, and a proposed answer. Every User decision is
pending. The recommendations are not human decisions. I consider these a
useful initial set but request independent assessment of their sufficiency,
wording, proposed answers, and whether further questions are needed.

Specific points for scrutiny include reviewer-role isolation, stale Codex
readiness, attributing screen evidence to the current pause, selecting a
protected first pane, surviving background shells, and the draft's example
that says SKIP for an already-cleared pane although its rule skips only the
clear. These ambiguities are represented as questions rather than resolved
by the writer. Some normative body wording may need clarification so it does
not appear to preempt those pending decisions.

No independent reviewer wording suggestions have yet been received or applied.

### Change summary for feature-request resume-paused (round 1)

Initial round: created the v0.14.0 resume-paused feature-request from the
canonical draft, retained whole suite as the explicit test scope, and added
Q01 through Q13 through the open-question manager. All human decisions remain
pending. No source implementation changes are included.

### Writer response for feature-request resume-paused (round 1)

Writer response:

This is the first independent specification review request. No reviewer
feedback has yet been received. Please assess the complete requirement and
its proposed answers, preserving the distinction between reviewer convergence
and explicit human choices. Review does not authorize consolidation or
starting the question-explanation workflow before convergence.

### Reviewer focus for feature-request resume-paused (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared_resume-paused/.reviews/a.review-active.specification.feature-request.v0.14.0.resume-paused.md`
- `C:/Users/vonc/git/llm-shared_resume-paused/.reviews/a.review-requested.feature-request.v0.14.0.resume-paused.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-11-07T17:26:08+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 1

The specification restates the draft faithfully: every draft rule appears in
the body, the five draft notes became Q01 to Q05, and Q06 to Q13 are sound
additions for gaps the draft leaves open. Most proposed answers are the ones I
would choose. It is not ready for convergence, for four reasons:

1. Three questions are missing (proposed Q14 to Q16): which post-pause commands
   count as already resuming, which panes get a report line, and whose action a
   delivery is when an agent runs the command. Q14 and Q16 bear on the
   reviewer-role isolation point the requestor asked me to scrutinize; without
   Q14, the tool never resumes the paused requestor of a checkout whose
   reviewer was restarted by hand.
2. Q06 lacks a materially distinct option for a checkout with several panes of
   the pausing agent, and "first" has no defined order.
3. Q08 Option A treats evidence shown to predate the pause like evidence that
   cannot be dated. Both A and B then skip the checkout, so as written the
   options differ only in the reported reason and exit status.
4. Body rules state answers that pending questions still decide, the pause time
   has no defined source, and three proposed answers are ungrammatical.

Cross-document facts I checked, read-only:

- `instructions/resume-session.md`: the receipt is written only after the
  prompt is read and reconciled, so a typed resume command and its receipt are
  separated by a real window that the agent-log and screen signal covers. A
  declined agent override, or a resume that stops on a blocker, leaves the
  prompt waiting and writes no receipt.
- `instructions/pause-session.md` and `templates/pause-session.template.md`:
  agent ids also include `gemini`, `copilot`, `grok` and any other host's
  lowercase name. `Session role` takes `implementation`, `requestor`,
  `reviewer`, `documentation` or `other`, so a reviewer can pause too. The
  prompt always carries a `Snapshot:` timestamp with offset. The journal keeps
  only the latest pause and resume entry per checkout, and a journal write
  failure does not undo a published prompt or receipt.
- `rules/interactive_menu.md`: a plain-text question shows as a program-status
  `blocked --kind question` record on its own `question` id. That record stays
  until the agent reports another status or exits, so it can outlive an
  answered question, exactly as a `working` record can.
- `instructions/review-requestor.md`, role-session isolation: a reviewer must
  never "message a requestor agent or requestor session", and a requestor must
  never start or message a reviewer. That binds any agent that runs this tool,
  not only Q01's companion wake-up.

Duplicate-resume signals. The third signal counts any post-pause
`review-resume`. In the usual layout, a requestor in one agent and a reviewer
in the other, the person often restarts the reviewer with
`review-resume as reviewer`; this very review started that way. That command
does not consume the requestor's pause prompt, yet the checkout would be
reported as already resuming and the paused requestor never resumed. The first
signal, a receipt matching the prompt, is the state table's "latest prompt
already used": the prompt is not waiting at all, and its report can name the
receipt's `Resumed by` and `Used at` but no resuming pane.

Pause time. "After the pause time" decides the second and third signals, the
redundant clear and the preview line, but the spec never says where that time
comes from. The journal is an index that can miss an entry. The prompt's
`Snapshot:` field is present wherever the prompt is.

Target selection. "The first pane" has no defined order: `list-agents` output
order, and across sessions? When a checkout holds two panes of the same agent,
the first can be another conversation, such as a helper pane or a same-agent
reviewer kept after an approved role override. With `--clear`, the tool would
then clear that unrelated conversation. Q06 Option A also yields contradictory
output when the caller's own pane matches first: `SKIP ...: this pane, run
resume-session here` for the caller's pane, plus a `RESUME` of the same
checkout in another pane.

Redundant clear. "Skip the clear when the log already records one after the
pause time" also skips it when the person cleared, then worked on in the fresh
conversation. The earlier clear makes a new one redundant only when no `prompt`
line follows it.

Exclusions. The spec does not say whether `--except` stops only input or also
stops reading a pane's already-resuming evidence. Excluded panes and the
caller's own pane must still count as evidence, or excluding a pane that is
resuming lets another pane of its checkout receive a duplicate command. A
mistyped `--except` value protects nothing, silently; with `--clear`, the
pane the person meant to protect is cleared.

Codex readiness. Q03 settles a stale `working` record but not a stale
`blocked` question record. Since typing into a question-blocked pane is
forbidden without exception, a `blocked` record must prevent input even when
the screen looks idle.

Report scope. Discovery reads every pane in every session, and both preview and
run promise "one line per pane", yet the listed reasons cover only checkouts
holding a prompt. Nothing says whether panes without a waiting prompt,
non-target panes beside the target, or checkouts whose prompt was already used
get a line.

Scope boundary. The body otherwise stays on behavior. The Codex new-conversation
command (`/new` or `/clear`) is correctly left as a fact to verify during
implementation rather than a human decision.

### Question verdicts for feature-request resume-paused round 1

Every `User decision` stays pending. The answers below are my independent
choices as reviewer, not human decisions.

| Question | Verdict | My answer | Change needed |
| --- | --- | --- | --- |
| Q01 | Agree | A | Correct the isolation reason; cover reviewer pauses; fix grammar |
| Q02 | Agree | A | Mark the body skip reason as pending Q02 |
| Q03 | Agree with addition | A | A `blocked` record always prevents input |
| Q04 | Agree | A | Say what "visible" means; fix grammar |
| Q05 | Agree | A | None |
| Q06 | Disagree with recommendation | C (new) | Define "first"; add Option C; fix grammar |
| Q07 | Agree | A | Include an unresolved delivery selector |
| Q08 | Agree with refinement | A (reworded) | Separate evidence shown to be old from undatable evidence |
| Q09 | Agree with additions | A | Evidence still read from excluded panes; unmatched values |
| Q10 | Agree | A | Classify the caller's-pane skip |
| Q11 | Agree | A | None |
| Q12 | Agree with refinement | A | A clear counts only with no later prompt |
| Q13 | Agree | A | Mention a concurrent `resume_paused` run |
| Q14 (new) | Missing | A | Add the question |
| Q15 (new) | Missing | A | Add the question |
| Q16 (new) | Missing | A | Add the question |

#### Verdict on Q01 reviewer companion panes for feature-request resume-paused (round 1)

I choose Option A. Two parts of the wording need correcting. First, the
isolation sentence binds the wrong party: role isolation constrains the agent
that runs this tool, whoever it targets (see proposed Q16). The direct reasons
against B and C are that the person did not choose that counterpart restart and
that an uncleared reviewer may already hold a live watcher, which a second
`review-resume` would duplicate. Second, a reviewer can pause too
(`Session role: reviewer`), so the question should cover either review role.
Replacement question text:

```md
When the paused session held a review role (its `Session role` is `requestor` or `reviewer`), should this command also send a review-resume command to the counterpart agent's pane, such as `review-resume as reviewer` after a requestor pause? The draft lists conditional, unconditional and absent companion wake-ups. A counterpart that was not cleared keeps its context and may already be waiting for requests.
```

Replacement recommendation and answer rationale; the current "because keep
this feature ..." does not parse:

```md
Option A: The person decides when to restart the counterpart; an unsolicited review-resume can duplicate a live reviewer's watcher, and it would add another cross-role delivery beside the one Q16 settles.
```

#### Verdict on Q02 busy panes for feature-request resume-paused (round 1)

I choose Option A. Waiting would also rarely help: a Codex reviewer in its
attached wait shows `• Working` for as long as it waits, and Q13's recheck
already covers a pane that becomes eligible during a run. The body's skip
reason "a turn in progress" should be marked as pending Q02.

#### Verdict on Q03 Codex readiness for feature-request resume-paused (round 1)

I choose Option A, with one addition. A stale record can also be `blocked`:
`rules/interactive_menu.md` shows a question record that stays until the
agent reports again. Because typing into a question-blocked pane is
forbidden without exception, screen evidence may outweigh a `working`,
`idle` or `done` record, never a `blocked` one. Replacement Option A:

```md
- Option A: Decide Codex readiness from the current screen: an empty `›` prompt line, no `• Working` and no question. A stale `working` record does not prevent input, but any `blocked` program-status record does, whatever the screen shows.
```

#### Verdict on Q04 background shells for feature-request resume-paused (round 1)

I choose Option A. "Visible" should say where the count comes from: the
pane's own background-shell indicator, such as Claude's `N shells` status
line; when a pane shows none, report nothing. Replacement rationale:

```md
Option A: Showing the shell count exposes the duplicate-watcher risk of a clear, while ending a shell remains the person's call.
```

#### Verdict on Q05 senv integration for feature-request resume-paused (round 1)

I choose Option A. No change needed.

#### Verdict on Q06 several panes of the pausing agent for feature-request resume-paused (round 1)

I disagree with Option B as the recommendation and would add Option C.
"First" needs a defined order, and the question should name the real risk:
the first pane of the pausing agent can be a different conversation, and with
`--clear` the tool would clear it. Option A has a further defect: when the
caller's pane matches first, the report says "run resume-session here" for
that pane and `RESUME` for another pane of the same checkout. Option C applies
the spec's own rule of not typing on uncertain evidence and costs little,
because the draft's usual layout has at most one pane per agent per checkout.
Replacement question text and new option:

```md
### Q06: Choosing among several panes of the pausing agent

When a checkout has several panes of the agent that paused it, which pane receives the command, and what happens when that pane is excluded, busy, question-blocked, holds draft input or is the caller's own pane? "First" means first in `tuios list-agents --all-sessions --json` order.

- Option C: Resume only when the checkout has exactly one pane of the pausing agent; with several, skip the checkout as ambiguous and list the candidate panes.
  - Pro: Never resumes or clears an unrelated conversation, matching the rule of not typing on uncertain evidence.
  - Con: A checkout with two panes of the same agent always needs a manual resume.
```

Add to Option A's cons: "When the caller's pane matches first, the report
would both send the person to that pane and resume the checkout elsewhere."
Add to Option B's cons: "The first pane may hold another conversation, which
`--clear` would clear." Replacement recommendation; the current "because
preserve ..." does not parse:

```md
Option C: An ambiguous target is uncertain evidence, and the spec does not type on uncertain evidence; the usual one-pane-per-agent layout is unaffected.
```

#### Verdict on Q07 unreadable state for feature-request resume-paused (round 1)

I choose Option A. Its scope should also name a delivery selector that matches
zero or several panes, which the body requires verifying but never says what
follows from. A failure of `tuios list-agents` itself leaves nothing to
classify: Option A then reports it and exits non-zero without typing.

#### Verdict on Q08 current-pause evidence for feature-request resume-paused (round 1)

I choose Option A, reworded. As written, A treats a resume command shown to
predate the pause, which should simply be ignored, like one that cannot be
dated. A Codex pane that was resumed and later paused would then be reported
uncertain at every run. Replacement Option A:

```md
- Option A: Count screen evidence only when it is attributable to the current pause, ignore evidence shown to predate it (such as a resume command followed on the same screen by a later command or by the current pause), and report uncertainty without typing when attribution cannot be established. Without a resuming pane, report what is known: the receipt's `Resumed by` and `Used at`, or `unknown`.
```

Example report line for a receipt with no pane evidence:
`SKIP api: already resumed by chatgpt at 2026-11-07 08:12 (receipt), paused by claude`.

#### Verdict on Q09 exclusion matching for feature-request resume-paused (round 1)

I choose Option A, with three additions to its text:

```md
Exclusion stops clearing and typing only: excluded panes, like the caller's own pane, still provide already-resuming evidence. Pane names are compared whole, spaces included, and a folder match uses the checkout folder's base name. A value that matches no session, pane or folder is reported, and a normal run then types nothing.
```

The last sentence is my proposal: a mistyped exclusion would otherwise leave
the pane the person meant to protect open to typing, and to clearing with
`--clear`.

#### Verdict on Q10 exit status for feature-request resume-paused (round 1)

I choose Option A. Name the caller's-pane skip ("run resume-session here") as
an expected skip, and, if Q09's addition is accepted, an unmatched `--except`
value as a failure. Optionally align the non-zero codes with other llm-shared
launchers: 2 for invalid input or an unexpected fatal error, 3 for an expected
stop such as an unconfirmed delivery.

#### Verdict on Q11 unconfirmed acceptance for feature-request resume-paused (round 1)

I choose Option A. No change needed.

#### Verdict on Q12 already-cleared preview for feature-request resume-paused (round 1)

I choose Option A, refined: an earlier clear makes a new one redundant only
when no `prompt` line follows it in the agent log; otherwise the person worked
on in the cleared conversation. Replacement Option A and preview line:

```md
- Option A: Skip only the clear, still resume, and report RESUME with an already-cleared note. A logged clear counts only when no `prompt` line follows it.
```

```text
RESUME docs/Claude docs: already cleared at 00:42, /resume-session for 'Update the guide', paused by claude at 2026-11-07 00:30
```

#### Verdict on Q13 eligibility changes for feature-request resume-paused (round 1)

I choose Option A. Add "including a concurrent `resume_paused` run" to the
changes rechecked before input: its delivery shows up as a resume command in
the target pane.

#### Proposed Q14 commands that count as already resuming for feature-request resume-paused (round 1)

Missing. I choose Option A. Proposed text:

```md
### Q14: Commands that count as already resuming

The duplicate-resume rule counts any post-pause `resume-session` or `review-resume` in any pane of the checkout. A reviewer restarted with `review-resume as reviewer` does not consume a requestor's pause prompt, and a resume that stopped on a blocker or a declined agent override leaves the prompt waiting. Which post-pause commands suppress delivery?

#### BBQ for Q14

At a barbecue, the inspector arriving does not mean the cook's order was picked up. In this picture: the inspector is a restarted reviewer, the cook's order is the paused requestor's prompt, and picking it up is resuming it.

#### Options for Q14

- Option A: Count `resume-session` in any pane. Count `review-resume` too, except `review-resume as reviewer` when the paused session's role is not `reviewer`. A counted command still counts when its resume then stopped or its override was declined.
  - Pro: Restarting a reviewer no longer hides a paused requestor, and any real attempt at the paused session still blocks a duplicate.
  - Con: Reads command arguments from the agent log or screen; a stopped attempt needs a manual resume.
- Option B: Count every `resume-session` and `review-resume`, as the draft lists.
  - Pro: Simplest and most conservative.
  - Con: In a requestor-plus-reviewer checkout, restarting the reviewer prevents the tool from resuming the requestor.
- Option C: Count only `resume-session`.
  - Pro: Only the command that consumes the prompt counts.
  - Con: A requestor resumed directly through `review-resume` can receive a duplicate `resume-session`.

#### Recommended option for Q14

Option A: It keeps the draft's protection against duplicate resumes without treating a reviewer restart as a resume of the paused session.
```

#### Proposed Q15 report scope for feature-request resume-paused (round 1)

Missing. I choose Option A. Proposed text:

```md
### Q15: Panes and checkouts that get a report line

Discovery reads every pane of every session, and both preview and run promise one line per pane, but the listed reasons cover only checkouts holding a prompt. Should the report also list panes whose checkout has no prompt, non-target panes beside the target, and checkouts whose prompt was already used?

#### BBQ for Q15

At a barbecue, the host's list can name every guest or only those still waiting for food. In this picture: guests are panes, waiting for food is a waiting prompt, and the list is the report.

#### Options for Q15

- Option A: One line per checkout holding a prompt: `RESUME` naming its target pane, or `SKIP` with the checkout or pane reason, an already-used prompt included. Omit checkouts without a prompt and non-target panes, and end with one line counting the omitted panes.
  - Pro: Output grows with paused work only and matches the draft examples, which mix pane and checkout lines.
  - Con: An omitted pane is explained only by the closing count.
- Option B: One line for every discovered Claude or Codex pane, including `SKIP <pane>: no waiting prompt` and non-target panes.
  - Pro: Every pane is accounted for.
  - Con: Long output across many sessions, mostly lines that need no action.

#### Recommended option for Q15

Option A: The report should show what needs or received action; panes with nothing waiting add length without a decision.
```

#### Proposed Q16 running the command from an agent pane for feature-request resume-paused (round 1)

Missing. I choose Option A. Proposed text:

```md
### Q16: Running the command from an agent pane

The draft's proven run was made by an agent from its own pane, and the caller-pane rule presumes an agent caller. Review-role isolation forbids a requestor from starting or messaging a reviewer session, and a reviewer from starting or messaging a requestor session. When an agent runs `resume_paused` and it types a resume command into another agent's pane, whose action is that?

#### BBQ for Q16

At a barbecue, a cook asked by the host to ring the dinner bell passes on the host's call; it is not one cook ordering another. In this picture: the host is the person, the cook is the calling agent, and the bell is the typed resume command.

#### Options for Q16

- Option A: The command acts for the person: an agent runs it only at the person's explicit request in its current conversation, never on its own initiative or as a step of a review or resume workflow, and the role-isolation text names this exception.
  - Pro: Keeps the proven agent-run usage and records why it is not a role-to-role start.
  - Con: Changes the shared role-isolation wording in another instruction.
- Option B: Only a person runs it, from a terminal or shell pane; an agent never does.
  - Pro: Needs no change to role isolation.
  - Con: Contradicts the draft's agent-run scenario and makes the caller-pane rule pointless.
- Option C: An agent may run it, but checkouts paused in a review role are skipped when the caller is an agent pane.
  - Pro: No cross-role delivery from an agent.
  - Con: Skips the review checkouts the person most wants resumed, and the tool cannot know the caller's own role.

#### Recommended option for Q16

Option A: The typed command is the person's own request relayed by a tool, which isolation should state rather than forbid.
```

### Requested changes for feature-request resume-paused round 1

Requested changes:

Questions:

1. Add Q14 (commands that count as already resuming), Q15 (panes and
   checkouts that get a report line) and Q16 (running the command from an agent
   pane), as proposed.
2. Q06: define "first" as `tuios list-agents --all-sessions --json` order, add
   Option C (skip a checkout with several panes of the pausing agent as
   ambiguous), add the stated cons to A and B, and recommend C.
3. Q08: replace Option A so that evidence shown to predate the pause is ignored
   and only undatable evidence is reported as uncertain; say what a receipt-only
   skip reports.
4. Q01: correct the role-isolation sentence, cover a reviewer pause, fix the
   rationale grammar. Q03: a `blocked` record always prevents input. Q04: say
   where the shell count comes from, fix the rationale grammar. Q09: excluded
   panes still provide evidence, names compared whole, unmatched values
   reported and stop typing. Q12: a logged clear counts only with no later
   `prompt` line, and use the corrected preview line. Q13: include a concurrent
   `resume_paused` run.

Body:

1. Pane discovery: define the pause time as the prompt's `Snapshot:`
   timestamp; the journal's pause entry only indexes it. Compare pane folders
   and receipt project roots using the filesystem's rules, so case and
   separator differences on Windows group panes into one checkout.
2. State that a prompt's `Session role` is `implementation`, `requestor`,
   `reviewer`, `documentation` or `other`, not only a requestor marker.
3. Under the pausing-agent mapping, say that other ids (`gemini`, `copilot`,
   `grok` or any other host name) and `unknown` are reported as unrecognized
   until supported.
4. Duplicate-resume protection: describe the first signal as the state table's
   "latest prompt already used", and mark the `review-resume` signal as pending
   Q14.
5. Mark the rules that pending questions decide, rather than stating them as
   settled: "first pane" (Q06), "a turn in progress" (Q02), the redundant clear
   and the draft's `SKIP docs` example (Q12), "one line per pane" (Q15), the
   selector-uniqueness consequence (Q07), and the exit status (Q10).
6. Acceptance criterion 5: append "with no later prompt", pending Q12.

### Writer instructions for feature-request resume-paused round 1

Apply the requested changes, then publish round 2 for review. Keep every
`User decision: pending`: none of my answers is a human decision, and this
round does not authorize consolidation or the question-explanation workflow.

1. Add Q14, Q15 and Q16 through the open-question manager
   (`bin\oqm.bat`), using the proposed text in the question verdicts. Generate
   their proposed answers from the recommendations as for Q01 to Q13.
2. Update Q01, Q03, Q06, Q08, Q09, Q12 and Q13 with the replacement wording in
   the question verdicts. For Q06, add Option C and change the recommendation to
   C. If you keep B, say why in your writer response; the user then decides
   between them.
3. Rewrite the recommendation rationales of Q01, Q04 and Q06 as full clauses,
   so that their generated "Option X is proposed because ..." answers parse.
4. Apply the body changes listed under the requested changes. Where a body rule
   depends on a pending question, name that question rather than rewording the
   rule as settled.
5. In the change summary, map each requested change to the edit made, or to the
   reason it was not made.

### Final reviewer decision for feature-request resume-paused round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-11-07T17:34:25+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 2

### Requestor assessment for feature-request resume-paused (round 2)

The reviewed requirement is docs/v0.14.0/feature-request.v0.14.0.resume-paused.md,
derived from the sibling draft.v0.14.0.resume-paused.md. There is no umbrella.

The requirement covers discovery across TUIOS sessions, the existing prompt
and receipt state rules, checkout-wide duplicate-resume protection, protected
panes, agent-specific commands, optional clearing, acceptance evidence,
preview output, and exit status. Its test scope is whole suite.

Please independently assess the whole specification against the source draft,
including omissions, conflicting requirements, unsafe acceptance behavior,
and any missing questions. Keep this feature-request review focused on scope,
expected behavior, edge cases and acceptance criteria rather than design or
implementation choices.

There are thirteen open questions, Q01 through Q13. Each has options, pros
and cons, a recommendation, and a proposed answer. Every User decision is
pending. The recommendations are not human decisions. I consider these a
useful initial set but request independent assessment of their sufficiency,
wording, proposed answers, and whether further questions are needed.

Specific points for scrutiny include reviewer-role isolation, stale Codex
readiness, attributing screen evidence to the current pause, selecting a
protected first pane, surviving background shells, and the draft's example
that says SKIP for an already-cleared pane although its rule skips only the
clear. These ambiguities are represented as questions rather than resolved
by the writer. Some normative body wording may need clarification so it does
not appear to preempt those pending decisions.

Round 1 feedback has now been applied. Q14 through Q16 cover counted resume
commands, report scope and agent-run authority. Q06 now proposes skipping
ambiguous multiple-pane checkouts rather than choosing an unrelated conversation.
Q08 distinguishes demonstrably old evidence from undatable evidence. The body
labels pending decisions rather than presenting their outcomes as settled.

All sixteen User decision records remain pending. Q16's proposed exception is
only a requirement question, and current review-role isolation still applies.
Please check the revised document for sufficiency, consistency, remaining
omissions and any further questions. Reviewer convergence will assess the
proposals, not approve them on the person's behalf.

### Change summary for feature-request resume-paused (round 2)

Changes since round 1, mapped to the reviewer's requests:

1. Added Q14, Q15 and Q16 with options, trade-offs, proposed answers and pending
   user decisions through the open-question manager.
2. Q06 defines first as discovery order for Options A and B, adds the risks to
   both options, and adds and recommends Option C. Its prior writer proposal
   is retained as history, without implying a human decision.
3. Q08 ignores evidence shown to predate the current pause, treats undatable
   evidence as uncertainty, and includes receipt-only identity and output.
4. Q01 now covers either review role and separates companion wake-ups from
   caller authority under Q16. Q03 preserves a blocked record as a veto. Q04
   names the pane's background-shell indicator as the source. Q09 specifies
   full names, folder base names, continued evidence reading from excluded
   panes, and a no-input result for unmatched exclusions. Q12 requires no
   prompt after a clear. Q13 includes concurrent invocations. Q07 includes
   selector failure and discovery failure. Q10 classifies caller skips and
   unmatched exclusions. Grammar in Q01, Q04 and Q06 is corrected.
5. The body defines pause time from Snapshot with offset, uses filesystem
   path comparison rules, lists session roles and unsupported pausing ids,
   distinguishes already-used prompts, and marks counted review-resume
   commands as pending Q14.
6. The body labels selection, busy-pane handling, redundant clearing, report
   scope, selector-failure handling and exit classification with their pending
   question IDs. Acceptance criterion 5 includes no later prompt, pending Q12.

No human answers were recorded and no questions were consolidated. No source
implementation or role-isolation instruction was changed.

### Writer response for feature-request resume-paused (round 2)

Writer response:

I accept the round 1 findings and applied the requested clarifications and
missing questions. I also accept the recommendation to propose Q06 Option C;
the earlier Option B recommendation remains visible as writer history.

Q16 now expressly says the existing role-isolation prohibition remains in
effect until any exception is explicitly decided and implemented. Its proposed
Option A is not authorization to invoke another role in this review.

The preview now shows the corrected RESUME line proposed by Q12 and identifies
both its pending status and the draft's prior SKIP wording. The body labels
other pending outcomes for the same reason. No proposed answer is a human
decision.

There is no substantive disagreement with the reviewer's findings. Please
assess the revised whole specification and questions for convergence.

The installed open-question manager's append operation retained the prior
section rather than replacing it as the instruction describes. Markdown
validation caught the duplicate. I removed only that stale duplicate, leaving
the complete sixteen-question section emitted by the manager. All original
question IDs and pending decisions remain present; nothing was consolidated.

### Reviewer focus for feature-request resume-paused (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-11-07T17:39:51+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 2

I re-read the whole revised specification against the draft and the round 1
findings. Every requested change is in place:

- Q14, Q15 and Q16 were added with distinct options, consequences and pending
  decisions.
- Q06 defines "first", carries the unrelated-conversation risk in both of the
  original options, and recommends the new Option C.
- Q08 separates evidence shown to predate the pause, which is ignored, from
  undatable evidence, which is reported as uncertain.
- Q03 makes a `blocked` record a veto on input.
- Q09 keeps reading evidence from excluded panes and the caller's pane.
- Q12 counts a clear only when no prompt follows it.
- Q07, Q10 and Q13 have the added scope.
- The recommendation clauses of Q01, Q04 and Q06 now parse.
- The body defines the pause time from `Snapshot:`, compares paths using the
  filesystem's rules, lists every session role and the unsupported pausing ids,
  and names the pending question wherever a rule is still open.

The questions are complete for this feature request's scope. Every proposed
answer follows from the draft, the cross-document rules checked in round 1 or
the safety principle the spec applies throughout: no input on uncertain
evidence. I found no new missing decision. The body no longer presents a
pending outcome as settled.

Only wording-level edits remain:

1. The second duplicate-resume signal compares the journal's resume entry with
   "its pause entry". The body now defines the pause time as the prompt's
   `Snapshot:` and calls the journal's pause entry an index only. That phrase
   should therefore read "later than the pause time"; it then also works when a
   journal write failure left no pause entry.
2. Q06 has a stray blank line before Option C, which turns its options into a
   loose list unlike the other questions. The writer-history sentence in its
   recommendation belongs in the transcript, which already records it.
3. Q01 now covers either review role, but Options B and C still say
   "reviewer"; "counterpart" matches the question.
4. Q16's recommendation states a condition rather than a reason to prefer A
   over B and C. Option A should also tell the person that choosing it brings
   the role-isolation text change into this delivery, or leaves it to a
   separate one.

The round 2 request text still says "thirteen open questions, Q01 through Q13".
That is a stale line in the request rather than the specification; the next
request should say sixteen.

### Question verdicts for feature-request resume-paused round 2

Every `User decision` remains pending. My answers below are reviewer choices,
not human decisions.

| Question | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- |
| Q01 | Agree | A | Options B and C: "reviewer" to "counterpart" |
| Q02 | Agree | A | None |
| Q03 | Agree | A | None |
| Q04 | Agree | A | None |
| Q05 | Agree | A | None |
| Q06 | Agree | C | Remove the blank line before Option C and the history sentence |
| Q07 | Agree | A | None |
| Q08 | Agree | A | None |
| Q09 | Agree | A | None |
| Q10 | Agree | A | None |
| Q11 | Agree | A | None |
| Q12 | Agree | A | None |
| Q13 | Agree | A | None |
| Q14 | Agree | A | None |
| Q15 | Agree | A | None |
| Q16 | Agree | A | Rationale and delivery scope wording |

#### Questions whose proposed answers depart from the draft for feature-request resume-paused (round 2)

Five proposed answers change or extend the draft's literal wording. Reviewer
agreement does not settle them; the person should weigh them knowingly:

- Q06 Option C replaces the draft's "first pane" rule with a skip when a
  checkout has several panes of the pausing agent.
- Q09 Option A goes beyond the draft: an unmatched `--except` value stops a
  normal run before any input.
- Q12 Option A corrects the draft's `SKIP docs` example into a `RESUME` line.
- Q14 Option A narrows the draft's "any `review-resume`" signal.
- Q16 Option A asks for an exception in the shared role-isolation text,
  another instruction outside this feature's tool.

#### Suggested counterpart wording for Q01 options for feature-request resume-paused (round 2)

```md
- Option B: Also resume the counterpart only when this run cleared its pane.
- Option C: Always resume the counterpart.
```

#### Suggested wording for Q16 option A and its recommendation for feature-request resume-paused (round 2)

```md
- Option A: Let the command act for the person: an agent runs it only at the person's explicit request in its current conversation, never on its own initiative or as a step of a review or resume workflow. The shared role-isolation text gains that exception, in this delivery unless the person defers it.
```

```md
Option A: The typed command relays the person's own explicit request, which the isolation policy can name as an exception without letting either review role start the other; until that exception exists, the current prohibition applies.
```

### Convergence evidence for feature-request resume-paused round 2

Covered wording:

This convergence recommendation covers the current formulation with these
wording-only edits:

1. Duplicate-resume protection, second signal: "The session journal has a
   resume entry for the checkout later than the pause time."
2. Q06: no blank line between Option B's last sub-item and Option C; the
   recommendation section ends after its first paragraph.
3. Q01 Options B and C name the "counterpart" rather than the reviewer.
4. Q16 Option A and its recommendation as suggested in the question verdicts,
   or the current text if the person states the delivery scope when deciding.

None of these edits changes a question's options or a proposed answer.

Convergence rationale:

The sixteen questions cover every open behavior the draft leaves to decide
and every gap the round 1 review found. Their options are materially distinct
and state their consequences, and each proposed answer follows from the draft
or from the existing `resume-session`, `pause-session`, program-status and
role-isolation rules. The body states the settled rules and names the pending
question wherever an outcome is open. What remains is wording only.

This recommendation is advisory. It does not authorize consolidation, and it
records no human decision. The outstanding human choices are all sixteen
`User decision` entries, Q01 to Q16. Five of them deserve the person's direct
attention because their proposed answers depart from the draft's literal text:
Q06 (skip ambiguous checkouts instead of using the first pane), Q09 (an
unmatched exclusion stops the run), Q12 (correct the `SKIP docs` example), Q14
(narrow which `review-resume` commands count) and Q16 (a role-isolation
exception in another instruction, and whether it ships in v0.14.0).

### Writer instructions for feature-request resume-paused round 2

No further automated review round is needed. When the person next revises the
document, or at consolidation, apply the wording edits listed as covered
wording. Do not consolidate or record any decision on the strength of this
recommendation: consolidation and every `User decision` belong to the person.

1. Second duplicate-resume signal: replace "later than its pause entry" with
   "later than the pause time".
2. Q06: delete the blank line before Option C, and delete the sentence "The
   writer recommended Option B in round 1 ...", which the transcript keeps.
3. Q01: use "counterpart" in Options B and C, as suggested.
4. Q16: use the suggested Option A text and recommendation, or keep the current
   text and let the person state the delivery scope when deciding Q16.
5. In the next request text, if any, say sixteen questions, Q01 to Q16.

### Final reviewer decision for feature-request resume-paused round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-11-08T01:33:57+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: # Human guidance for resume-paused follow-up

Latest human authorization:

> Go ahead for independent review

Earlier role-switch guidance, preserved verbatim:

> D: once the requestor has been identified and resumed, check if there is a counterpart (sometime, you just have a CMD, not another llm + CMD). If there is, send a "/review-resume as reviewer, claim the role if you have to, since the requestor just resume their session": that should cover the case when the user wants the reviewer and requestor llms to switch. Make sure your questions cover that case (resume, but for a given tab, switch llm roles)

Earlier Codex submission observation, preserved verbatim:

```text
The missing Codex part is about one or two sentences. When Codex shows  <command> with no Ask Codex to do anything line below it, the command was typed but not submitted. The tool should then press Enter once and check for  Working again, instead of only reporting the command as unconfirmed.
```

The explicit recorded decisions, including Q16=B human shell launch only, remain authoritative. Preserve all question blocks and human answers. Independently review their consistency and identify missing/new questions; consolidation is not authorized.

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 3 by requestor

- Recorded: 2026-11-08T01:34:10+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 3)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 3

### Requestor assessment for feature-request resume-paused (round 3)

#### Assessment of resume-paused human decisions for feature-request resume-paused (round 3)

The full feature request and its related draft need fresh independent review after the human discussion. There are nineteen question blocks, Q01 through Q19, and every one has an explicit user decision. The full decision scanner succeeds with zero undecided questions and no diagnostics; reviewed-document SHA-256 is aa495095058e7bc582b79b3f677e572cb7137bf999a9e2c2bcf13cbb056f6123.

The round 2 convergence covered the earlier document and proposed answers, before the subsequent human choices and comments. It is not evidence that these changes have been independently reviewed. Both the original Q01-Q16 discussion and the expressly requested Q17-Q19 role-switch extension are in scope.

The recorded choices are Q01=D, Q02=A, Q03=A, Q04=A, Q05=A with a tracked follow-up reminder, Q06=C, Q07=A, Q08=A, Q09=A, Q10=A, Q11=C, Q12=A, Q13=A, Q14=A, Q15=A, Q16=B, Q17=A, Q18=A and Q19=A. Human decisions take precedence over preserved historical recommendations. The original options, explanations and recommendations remain for review; do not treat a retained proposed answer as a pending human choice.

I assess these choices as a coherent intended flow: human shell launch, explicit per-tab assignments when needed, fresh evidence and target protections, selected requestor resumption and proven ownership, then actual LLM reviewer activation, followed by separate outcomes and verified reviewer-only recovery. No plain shell can be a reviewer. An accepted command does not itself establish requestor takeover or grant override consent.

The existing options and recorded answers address the known decisions, but the expanded role-switch flow and Codex submission recovery need independent challenge for missing cases and contradictions. Review the entire specification, its retained baseline body and historical proposal wording against the confirmed answers. Identify any additional question rather than silently resolving a new human choice. Confirm whether non-review pauses, absent counterparts, multiple panes, repeated runs, consent conflicts and partial delivery are consistently covered without guessing.

Round 2 covered wording edits were applied: journal evidence compares with the prompt pause time, Q06 list/history wording was cleaned up, Q01 uses counterpart, and Q16's original A recommendation explains the proposed exception's delivery scope. The user subsequently selected Q16=B, so the requirement now records human-only shell invocation and no isolation exception. Assess any residual conflict with historical agent-run evidence and caller-pane protection.

Review input includes docs/v0.14.0/draft.v0.14.0.resume-paused.md and docs/v0.14.0/feature-request.v0.14.0.resume-paused.md. No design or plan has been created. No consolidation, staging or commit is authorized by this request.

### Change summary for feature-request resume-paused (round 3)

#### Changes after resume-paused round 2 for feature-request resume-paused (round 3)

Since round 2, the writer recorded all nineteen explicit user decisions while retaining the question blocks and historical options/recommendations. The private question companion mirrors the requirement's complete question section.

- Q01=D adds actual counterpart LLM reviewer activation after the requestor resumes, including a person-selected switch of requestor/reviewer LLMs for one tab. CMD and other plain shells never qualify. The draft Goal and requirement Target selection introduce the distinction between the selected assignment and the pause's historical author.
- Q02=A immediately skips active targets. Q03=A permits current idle-screen evidence to override stale Codex working status, with any blocked/question/person-draft evidence vetoing input. Q04=A reports only the pane-provided background-shell indicator and leaves shells running.
- Q05=A defers senv integration. The draft and requirement have an explicit unchecked follow-up checklist to revisit it after shared command implementation/validation and carry its link through design, plans and completion. No calendar reminder or separate external issue was created.
- Q06=C skips ambiguous multiple panes and lists candidates. Q17 separately permits explicit assignments. Q07=A prevents input to uncertain checkouts, reports errors, continues independent valid checkouts and fails overall; failed global discovery permits no input anywhere.
- Q08=A attributes evidence to the current pause, ignores proven older evidence and treats uncertain attribution as no-input uncertainty, reporting known identity/time or unknown. Q09=A uses case-insensitive exact complete names with scope-specific exclusions; excluded/caller panes still provide evidence; unmatched values prevent all input in a normal run.
- Q10=A distinguishes expected successful skips from classification errors, unmatched exclusions and unconfirmed planned actions. Q12=A skips only a redundant clear, still resumes an eligible pane, and requires no prompt after a logged post-pause clear. Q13=A rechecks before every input, including concurrent changes and competing resumption.
- Q11 adds C without removing A/B or their original recommendation, then records the user's C decision: at most one Enter for fresh proof of this run's exact unsubmitted Codex command, empty input before typing, and still-valid protections; never retype, never repeat Enter, then check again for command followed by Working. Uncertain ownership/submission/eligibility means no further input; unconfirmed acceptance remains a failure.
- The draft and requirement explain readiness before typing versus submission afterward. A reported command on the Codex input line without Ask Codex to do anything beneath it is context for the submission finding, not sufficient evidence on its own. Review the queued reviewer finding in .reviews/a.spec-review.pending-finding.resume-paused.md against Q11=C's actual coverage.
- Q14=A counts resume-session anywhere and review-resume except reviewer-only continuation when the saved pause role is not reviewer. Counted stopped or declined-override attempts suppress automatic repeats without proving completed resumption.
- Q15=A reports one line per prompt-bearing checkout, including already-used prompts, with separate requestor/reviewer targets and outcomes, an omitted-pane count, and no CMD-as-reviewer report.
- Q16=B requires human shell launch only; agents never launch the command even when asked. No shared isolation exception is introduced. This differs from the historical A recommendation and demonstrated agent-run draft scenario.
- New Q17=A accepts explicit per-tab role assignments and otherwise retains the known requestor; the pause author supplies a default only when the pause belonged to the requestor. A unique other supported LLM may be counterpart; absent/ambiguous requestor evidence or several counterparts require selection. Syntax is deferred to design.
- New Q18=A requires intended-pause consumption and restored requestor ownership for the exact exchange before reviewer activation. Working or a receipt alone is insufficient. Existing post-notice author-override and review-role Override consent gates remain; pending reconciliation leaves the reviewer untouched.
- New Q19=A permits verified reviewer-only continuation after partial completion without clearing or resuming the requestor twice, with fresh protections and no automatic retry of uncertain reviewer delivery. An already-claimed or waiting reviewer is left alone.

The user requested a hold after recording Q19, then explicitly released it for independent review. No review-role instruction was amended and no counterpart session was started or contacted.

### Human guidance and writer response for feature-request resume-paused (round 3)

Human guidance:

#### Human guidance for resume-paused follow-up for feature-request resume-paused (round 3)

Latest human authorization:

> Go ahead for independent review

Earlier role-switch guidance, preserved verbatim:

> D: once the requestor has been identified and resumed, check if there is a counterpart (sometime, you just have a CMD, not another llm + CMD). If there is, send a "/review-resume as reviewer, claim the role if you have to, since the requestor just resume their session": that should cover the case when the user wants the reviewer and requestor llms to switch. Make sure your questions cover that case (resume, but for a given tab, switch llm roles)

Earlier Codex submission observation, preserved verbatim:

```text
The missing Codex part is about one or two sentences. When Codex shows  <command> with no Ask Codex to do anything line below it, the command was typed but not submitted. The tool should then press Enter once and check for  Working again, instead of only reporting the command as unconfirmed.
```

The explicit recorded decisions, including Q16=B human shell launch only, remain authoritative. Preserve all question blocks and human answers. Independently review their consistency and identify missing/new questions; consolidation is not authorized.

Writer response:

#### Writer response for resume-paused human discussion for feature-request resume-paused (round 3)

The writer accepted and applied round 2's covered wording suggestions before the human discussion. All choices are now explicit user decisions rather than reviewer or writer recommendations. This replacement round is the follow-up required after that discussion, authorized again when the user released the temporary hold.

Please independently assess the full requirement and related draft, including all recorded comments and notion introductions. In particular:

1. Check Q01=D with Q16=B: the person launches the bulk command from a shell; an automated review requestor/reviewer never launches it. No role-isolation exception is authorized. Check that the historical agent-run evidence and caller-pane rule cannot be mistaken for permission to launch from an agent.
2. Check per-tab switched LLM roles end to end through Q06, Q17, Q18 and Q19: author identity, explicit assignments, exact exchange ownership, post-notice consent, counterpart qualification, missing or ambiguous LLM panes, successful takeover and partial continuation. No pane-order guess, implicit override or CMD reviewer is allowed.
3. Evaluate the queued Codex typed-but-unsubmitted finding against Q11=C. This draft already records a guarded one-Enter recovery and a subsequent Working check. Determine whether the evidence and protection requirements are sufficient; raise any remaining substantive gap. The requestor does not prescribe your disposition from the queued note.
4. Reconcile Q03 readiness, Q08 current-pause attribution, Q11 submission, Q13 fresh checks, Q14 duplicate suppression, Q18 actual takeover and Q19 repeat-run recovery. A suppressed resume attempt is not proof of successful requestor resumption, and a completed requestor action must not suppress a separately verified missing reviewer action.
5. Check preview/report/exit-status consistency, exclusions, already-used prompts, protected panes, background shells and no-counterpart outcomes. Verify that the deferred senv checklist remains explicit and survives future consolidation.
6. State whether the existing question options and confirmed answers are sufficient. Identify missing questions or conflicts with confirmed choices explicitly; do not overwrite those choices with recommendations. Assess the retained baseline body as pre-consolidation text, and identify any clarification needed to avoid misleading settled behavior without deleting question history.

There is no disagreement with the round 2 assessment of its earlier document. New human choices supersede historical recommendations, especially Q01=D, Q11=C and Q16=B. A new full-specification assessment is needed; no consolidation or implementation is requested.

### Reviewer focus for feature-request resume-paused (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-11-08T01:46:37+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 3

I read the full revised specification (SHA-256 `aa495095...6123`, matching
the request), its source draft, the queued finding and its evidence
(`a.resume-paused.codex-submit-evidence.local.md`). I checked the decisions
against `resume-session.md`, `review-resume.md`, `pause-session.md` and
`tuios send-keys --help`.

The nineteen recorded decisions are explicit, and I keep every one of them.
Q02, Q03, Q07 to Q10 and Q12 to Q15 fit together without contradiction. Q14's
counted attempts do not stand in for Q18's takeover evidence, so a suppressed
resume never activates a reviewer. The deferred senv checklist is explicit in
both documents and has a preservation rule for consolidation.

The role-switch flow (Q01=D) and the human-only launch (Q16=B) leave decisions
open that the current questions do not settle. The body and acceptance
criteria still describe the single-delivery tool. That is more than wording,
so I request changes and another round.

#### Codex typed-but-unsubmitted command for feature-request resume-paused (round 3)

Q11=C settles the policy the queued finding asked for:

- recognize the command on the input line with no `Ask Codex to do anything`
  line below it;
- press Enter once, then check again for `Working`;
- never press Enter over the person's draft.

Four parts of the requirement are still missing:

1. **The body and acceptance criteria do not carry it.** "Delivery and
   command-acceptance evidence" still says the reviewer queued a finding and
   that recovery is pending Q11, and acceptance criterion 7 has no recovery.
   An implementer reading the requirement sections would not build it.
2. **The input being empty before typing has no defined evidence.** The
   evidence shows that Codex draws its empty input line with the placeholder
   `Ask Codex to do anything`: that line reappears below a command once it is
   submitted. Q03's readiness check, "an empty `›` prompt line", should be
   defined the same way. The capture that passed it before typing is then the
   proof Q11=C needs. Read literally as a bare `›`, Q03 would never find a
   Codex pane ready.
3. **The Enter has no defined delivery.** The evidence used
   `tuios send-keys -s S -w NAME Enter`. According to `tuios send-keys --help`,
   without `-w` the keys go to the window the attached client has focused, and
   `-w` accepts a full id, an index, an exact name or a unique id prefix. A
   run the person starts (Q16=B) may start outside any pane. The Enter should
   go through `send-keys` with `-w` set to the full id of the pane that
   received the command, after the Q13 recheck.
4. **Scope and screen stability are open.** The requirement should say whether
   the recovery covers every command the tool types into Codex:
   - the new-conversation clear;
   - `resume-session`;
   - the reviewer instruction from Q01=D.

   It should also require the unsubmitted signature to be read after the
   delivery call has returned, and to be unchanged across two captures. That
   keeps a submission still in progress from being taken for an unsubmitted
   command. Claude has no such recovery: an unconfirmed Claude delivery stays
   under Option A.

#### Human-only launch for feature-request resume-paused (round 3)

Q16=B says an agent never launches the command, even at the person's request,
and makes no change to any instruction. Nothing in the requirement makes that
hold: no rule tells agents so, and the tool does not check its caller. An agent
the person asks to run it would therefore run it. Enforcement needs a decision,
which I suggest as Q20.

The body still describes an agent caller in three places:

- the caller-pane rule reports `run resume-session here`;
- the preview example shows
  `SKIP senv/Claude senv: this pane, run resume-session here`;
- Q10's answer counts a caller's-pane skip.

Under Q16=B the caller is a shell pane, or no pane at all. "Never type into the
caller's pane" can stay as a safeguard, but the agent-caller example and report
text should go or be recast. The draft's agent-run session remains evidence of
how TUIOS behaves, not an authorized way to launch the tool. The tool must also
work when started outside TUIOS, where `TUIOS_PANE_ID` is unset.

#### Role-switch flow for feature-request resume-paused (round 3)

1. **Which pauses lead to reviewer activation (suggested Q21).** Q01 asked
   about review-role pauses, but its answer and the body do not say whether D
   applies to `implementation`, `documentation` or `other` pauses.
   - A checkout has one prompt slot. `pause-session` keeps "the last
     successfully produced resume prompt for this checkout", so the prompt in
     a review tab can be the reviewer's.
   - For a `reviewer` pause, Q17 makes the author the default requestor only
     when the pause was the requestor's. No question says which pane receives
     `resume-session`, or whether the requestor is woken.
   - A requestor pause with no identifiable live exchange, or with several
     exchanges in the checkout, has no defined outcome under Q18's "exact
     review exchange".
2. **The counterpart pane (suggested Q22).**
   - Whether `--clear` also clears the counterpart is undecided. Q04 shows
     that a cleared pane keeps its background shells, so a cleared reviewer
     restarted through review-resume would run a second watcher.
   - Q19 leaves an already claimed or waiting reviewer untouched on a later
     run. Q01=D's answer sends the instruction "not limited to a counterpart
     cleared by the current run". On a first run, that counterpart is often a
     reviewer still waiting with its watcher. The same leave-alone rule, with
     the same evidence, should apply on every run.
3. **Same-run sequencing and outcome (suggested Q23).** Q18 requires the pause
   to be consumed and the exact exchange's requestor ownership to agree before
   activation. `resume-session` writes its receipt only after reconciliation,
   and review-resume restores ownership after that. This takes at least a whole
   turn, and it can stop on a consent question. The requirement does not say:
   - whether a run waits for that evidence, and for how long;
   - what `--dry-run` shows;
   - whether a pending reviewer step fails the run under Q10.

   Reading exchange state is also outside acceptance criterion 9's read list
   (prompts, receipts and journal).
4. **Conflict between Q01=D's typed text and Q18=A.**
   - Q01=D quotes the typed instruction "claim the role if you have to".
   - Q18=A says that "a selected destination does not preauthorize author or
     review-role overrides".
   - In `review-resume.md`, only an explicit `Override` from the person
     permits `--override`.

   A receiving agent can read the typed text as that consent. I propose that
   Q01's answer state that the typed instruction only gives context: on an
   LLM-nature conflict the reviewer asks `Override` or `Stop`, and the tool
   reports the reviewer step as awaiting consent. The person must confirm this;
   I have not changed the recorded choice.
5. **Conflict between Q17=A and Q06=C.** Q17=A names the requestor by LLM only.
   When a tab holds two panes of that LLM, Q06=C skips the checkout as
   ambiguous, and an assignment cannot resolve the ambiguity. I propose that an
   assignment may also name the requestor pane, for the person to confirm.
   Q17 also leaves the source of the "known requestor assignment" undefined. It
   can only come from the exact exchange's coordination record, or from the
   pause author when the pause was the requestor's.

#### Body and acceptance criteria for feature-request resume-paused (round 3)

The retained body still marks as pending what these questions now decide: Q02,
Q06, Q07, Q09, Q10, Q11, Q12, Q14, Q15, Q16 and Q19. Acceptance criterion 3
("Select the pausing agent's pane") contradicts Q17. The command contract shows
no assignment input, although Q17 adds one with its syntax deferred to design.
No acceptance criterion covers Q01=D, Q11=C, Q17, Q18 or Q19.

This does not require consolidation. It is enough to mark each decided rule
with its question and option and to add those acceptance criteria, so the body
stops presenting superseded behavior as current.

### Question verdicts for feature-request resume-paused round 3

The nineteen user decisions are recorded and preserved. "My answer" gives the
option I would choose. Where it differs from the decision, the decision stands,
and I review it for consistency only.

| Question | Decision | Verdict | My answer | Remaining issue |
| --- | --- | --- | --- | --- |
| Q01 | D | Accept, conflict reported | A originally; D reviewed as decided | Typed "claim the role" text against Q18; pause scope (Q21); counterpart pane (Q22) |
| Q02 | A | Agree | A | None |
| Q03 | A | Agree | A | Define the empty Codex input line with its placeholder |
| Q04 | A | Agree | A | Applies to the counterpart only if Q22 clears it |
| Q05 | A | Agree | A | None; keep the checklist |
| Q06 | C | Agree | C | Requestor pane naming in Q17 |
| Q07 | A | Agree | A | Also covers unreadable exchange state under Q18 |
| Q08 | A | Agree | A | None |
| Q09 | A | Agree | A | None |
| Q10 | A | Agree | A | Caller's-pane skip under Q16=B; pending reviewer step (Q23) |
| Q11 | C | Agree | C | Body, acceptance criteria, empty-input evidence, Enter delivery, scope |
| Q12 | A | Agree | A | None |
| Q13 | A | Agree | A | Also covers the recovery Enter and the reviewer instruction |
| Q14 | A | Agree | A | Match the reviewer role argument, not the literal text |
| Q15 | A | Agree | A | Report a reviewer step pending or awaiting consent (Q23) |
| Q16 | B | Accept, gap reported | A originally; B reviewed as decided | Enforcement (Q20); agent-caller text |
| Q17 | A | Accept, conflict reported | A | Let an assignment name the requestor pane; source of the known requestor |
| Q18 | A | Agree | A | Evidence source, waiting and outcome (Q23) |
| Q19 | A | Agree | A | Same leave-alone rule on a first run (Q22) |

#### Proposed corrections for the person to confirm for feature-request resume-paused (round 3)

These change no recorded option. Record each beside the decision it qualifies,
as a proposed clarification awaiting the person's confirmation:

- Q01: "The typed reviewer instruction gives context only and grants no review-role `Override`. When the reviewer's recorded LLM nature differs, the reviewer asks `Override` or `Stop` as `review-resume` requires, and the tool reports the reviewer step as awaiting consent."
- Q17: "An assignment names the requestor's LLM, or its pane when the tab holds several panes of that LLM. Without an assignment, the known requestor is the one the exact exchange's coordination record names, or the pause author when the pause was the requestor's."
- Q14 body signal: "Count a `review-resume` invocation that selects the reviewer role as the exception, whatever text follows the role", because Q01=D's instruction carries more text.

#### Suggested new question on enforcing the human-only launch for feature-request resume-paused (round 3)

```md
### Q20: Enforcing the human-only launch

Q16=B says that only the person launches `resume_paused`, and that an agent
never does, even when asked. No instruction change is made, so an agent asked
to run it would comply. How does the requirement make Q16=B hold?

- Option A: Refuse to run, including `--dry-run`, when the caller pane
  (`TUIOS_PANE_ID`) is a recognized Claude or Codex pane: exit non-zero
  without input. The command's help says agents must not run it.
  - Pro: Follows Q16=B literally without relying on an agent reading a rule.
  - Con: No preview from an agent pane; an agent outside TUIOS is not detected.
- Option B: Refuse normal runs from a recognized agent pane, but allow
  `--dry-run` there.
  - Pro: An agent can show the person the plan without typing anything.
  - Con: Narrows Q16=B's "never launches it".
- Option C: Document the rule only; keep the caller-pane skip as a safeguard.
  - Pro: No caller detection.
  - Con: An agent asked to run it will, contrary to Q16=B.

Recommended: Option A, because it matches the confirmed answer and reuses the
pane classification that discovery already performs.
```

#### Suggested new question on pauses that lead to reviewer activation for feature-request resume-paused (round 3)

```md
### Q21: Pauses that lead to reviewer activation

A checkout holds one resume prompt, whichever role wrote it last. Q01=D wakes
a reviewer after the requestor resumes, but does not say which saved
`Session role` values lead there, what happens to a `reviewer` pause, or what
happens when the checkout's live review exchange cannot be identified.

- Option A: Only a `requestor` pause leads to reviewer activation, and only
  with exactly one live review exchange identifiable for the checkout. A
  `reviewer` pause resumes in its assigned reviewer, by default its author,
  and wakes no requestor. `implementation`, `documentation` and `other` pauses
  resume one agent. With no live exchange, or several, the requestor still
  resumes and the reviewer step is reported as not applicable or ambiguous.
  - Pro: Follows Q01's review-role scope and Q18's exact-exchange evidence;
    no input on an unidentified exchange.
  - Con: An `implementation` pause that requests code review does not wake its
    reviewer.
- Option B: Decide from exchange state instead of `Session role`: activate
  when, after resumption, exactly one live exchange names the selected
  requestor.
  - Pro: Covers implementation sessions that request code review.
  - Con: A `documentation` or `other` pause can wake a reviewer unexpectedly.
- Option C: Any pause activates an LLM counterpart when one exists.
  - Pro: One rule.
  - Con: Sends review-resume where no review is in progress.

Recommended: Option A, because it keeps D within the review-role pauses it was
asked for and never guesses the exchange.
```

#### Suggested new question on the counterpart pane for feature-request resume-paused (round 3)

```md
### Q22: The counterpart pane before reviewer activation

Q01=D sends the reviewer instruction to a counterpart whether or not this run
cleared it, while Q19 leaves an already active reviewer alone on a later run.
Does `--clear` apply to the counterpart, and when is a counterpart left
untouched?

- Option A: Never clear the counterpart. On every run, leave it untouched when
  the exact exchange's coordination record already names its LLM as reviewer
  and the pane shows that reviewer still active, such as a `review-resume`
  prompt after the pause with no later prompt, or a background-shell
  indicator. Otherwise send the instruction under the usual protections.
  - Pro: One rule for first and later runs, consistent with Q19; no second
    watcher.
  - Con: A switched reviewer keeps its former requestor conversation unless
    the person clears it.
- Option B: Never clear; always send the instruction to an eligible
  counterpart and rely on review-resume to keep an existing watcher.
  - Pro: Simple.
  - Con: A counterpart the person cleared earlier no longer knows its old
    watcher and starts a second one.
- Option C: Under `--clear`, clear the counterpart too, then send the
  instruction, with Q04's shell warning.
  - Pro: A switched reviewer starts without its authoring context.
  - Con: Its old watcher survives the clear (Q04) and is duplicated; erases
    context the person may want.

Recommended: Option A, because it applies Q19's rule consistently and avoids
the duplicate-watcher risk that Q04 documents.
```

#### Suggested new question on waiting for the requestor takeover for feature-request resume-paused (round 3)

```md
### Q23: Waiting for requestor takeover and reporting a pending reviewer step

Q18 requires the pause to be consumed and the exact exchange's requestor
ownership to agree before reviewer activation. That takes at least one full
turn of the resumed agent and can stop on a consent question. Does a run wait
for it, and what does a pending reviewer step mean for the report and exit
status?

- Option A: After the requestor's command is accepted, wait for Q18's evidence
  up to a bounded time set in design, reading exchange state read-only and
  never claiming. If the evidence does not arrive, report the reviewer step as
  pending with its reason (consent, reconciliation or timeout). A pending
  reviewer step does not fail the run; an unconfirmed requestor delivery
  still does. `--dry-run` shows the reviewer step as conditional on takeover.
  - Pro: Restores the pair in one run when the requestor resumes promptly; a
    question awaiting the person is not a tool failure; Q19 finishes later.
  - Con: Runs last longer, and a pending step is visible only in the report.
- Option B: Do not wait: activate the reviewer only when takeover evidence
  already exists, normally on a later run under Q19.
  - Pro: Short runs with no in-run polling.
  - Con: Restoring a pair always takes two runs.
- Option C: As Option A, but a pending reviewer step fails the run.
  - Pro: Automation sees incomplete pairs from the exit status.
  - Con: A run fails because the person has not yet answered a question.

Recommended: Option A, because it keeps Q10's split between expected outcomes
and failed deliveries and leaves later completion to Q19.
```

### Requested changes for feature-request resume-paused round 3

Requested changes:

Questions:

1. Add Q20 to Q23 as suggested in the question verdicts, in the document's
   question format with BBQ sections, each with `User decision: pending`.
2. Record the proposed Q01, Q17 and Q14 clarifications beside their decisions,
   as clarifications awaiting the person's confirmation. Do not change any
   recorded option.

Body:

1. Delivery and command-acceptance evidence: replace the queued-finding
   paragraph with Q11=C as a requirement.
   - The unsubmitted signature: the tool's exact command on the Codex input
     line, no `Ask Codex to do anything` line below it, and no `Working`. Read
     it after the delivery call has returned, unchanged across two captures.
   - Proof that the input was empty: the pre-typing capture that passed Q03's
     readiness check.
   - Delivery of the single Enter: `tuios send-keys` with `-s` and with `-w`
     set to the full id of the pane that received the command, after a Q13
     recheck, never without `-w`.
   - Scope: every command the tool types into Codex, namely the
     new-conversation clear, `resume-session` and the Q01=D reviewer
     instruction.
   - Claude has no Enter recovery; an unconfirmed Claude delivery stays under
     Q11's Option A.
   - The result line says when the recovery Enter was used.
2. Define Q03's empty Codex input line as `›` followed only by the placeholder
   `Ask Codex to do anything`, to be confirmed on the Codex version in use, as
   the new-conversation command already is.
3. Caller pane under Q16=B: the caller is a shell pane, or no pane when the
   tool starts outside TUIOS with `TUIOS_PANE_ID` unset. Keep "never type into
   the caller's pane" as a safeguard. Remove the `run resume-session here`
   report and the `SKIP senv/Claude senv` example, or mark them historical.
   Describe the draft's agent-run session as evidence of TUIOS behavior only.
4. Replace each "pending" reference with the decided question and option:
   - duplicate-resume signals (Q14);
   - reviewer-only completion (Q19);
   - target selection (Q06, Q17);
   - companion wake-ups and launch authority (Q01, Q16);
   - busy panes and exclusions (Q02, Q09);
   - the redundant clear (Q12);
   - selector uniqueness (Q07);
   - report scope (Q15);
   - exit status (Q10).
5. Command contract: state that Q17 adds a per-tab assignment input, with its
   syntax left to design.
6. Acceptance criteria:
   - Criterion 3: selection follows Q06=C and Q17.
   - Criterion 7: add the Q11=C recovery.
   - Criterion 9: add a read-only view of review-exchange state for Q17 and
     Q18, with no claim or fenced operation.
   - Add criteria for the Q01=D order: requestor first, Q18 takeover evidence,
     then reviewer activation, and never a CMD reviewer.
   - Add criteria for Q19 reviewer-only continuation, and for Q20 to Q23 once
     they are decided.
7. Optional, in the draft: point the Codex observation paragraph to Q11=C
   instead of the queued finding.

### Human guidance response for feature-request resume-paused round 3

Human guidance:

Latest human authorization:

> Go ahead for independent review

Earlier role-switch guidance, preserved verbatim:

> D: once the requestor has been identified and resumed, check if there is a counterpart (sometime, you just have a CMD, not another llm + CMD). If there is, send a "/review-resume as reviewer, claim the role if you have to, since the requestor just resume their session": that should cover the case when the user wants the reviewer and requestor llms to switch. Make sure your questions cover that case (resume, but for a given tab, switch llm roles)

Earlier Codex submission observation, preserved verbatim:

```text
The missing Codex part is about one or two sentences. When Codex shows  <command> with no Ask Codex to do anything line below it, the command was typed but not submitted. The tool should then press Enter once and check for  Working again, instead of only reporting the command as unconfirmed.
```

Guidance response:

- **"Go ahead for independent review":** this answer is that review. It
  covers the whole feature request and the draft, against the current
  `resume-session`, `review-resume` and `pause-session` instructions.
- **Role-switch guidance (Q01=D):** the per-tab switch is covered by Q17, Q18
  and Q19, and "no CMD reviewer" is stated throughout. Three parts of the
  person's description still need decisions: which pauses lead to activation
  (Q21), how the counterpart pane is treated (Q22), and waiting for the
  requestor (Q23). One phrase, "claim the role if you have to", conflicts with
  Q18 and with `review-resume`'s explicit `Override` rule. I propose a
  clarification for the person to confirm and have not overridden the choice.
- **Codex submission observation:** Q11=C records the recovery the person
  described. It is not yet a requirement in the body or acceptance criteria,
  and three parts are still undefined:
  - the evidence that the input was empty before typing;
  - how the single Enter is addressed to the pane;
  - which typed commands the recovery covers.

  The person also asked, through a relayed note, that this point be raised as
  a requested change. This answer raises it on its merits as a requested
  change, so the next round can check it.
- **Q16=B:** preserved as decided. The requirement still needs a way to make
  it hold (Q20), and the agent-caller text left in the body should be recast.

### Writer instructions for feature-request resume-paused round 3

Apply the requested changes, then request another automated review round.

1. Keep all nineteen recorded user decisions and their history as they are.
   The proposed Q01, Q17 and Q14 clarifications are additions that await the
   person's confirmation; they do not replace any decision.
2. Add Q20 to Q23 with pending user decisions. Have the person decide them, and
   confirm or reject the three clarifications, before the next request. Then
   reflect the outcomes in the body.
3. Carry Q11=C into the body and acceptance criteria with the evidence, Enter
   delivery and scope listed in the requested changes. The next round checks
   this specifically.
4. Update the body as listed: decided rules marked with their question, the
   caller pane recast for Q16=B, the Q17 assignment input, and acceptance
   criteria covering Q01=D, Q11=C, Q17, Q18 and Q19.
5. Do not consolidate. In the next request, list the questions as Q01 to Q23
   and summarize which decisions the person made since this round.

### Final reviewer decision for feature-request resume-paused round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-11-08T01:56:04+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 4)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 4

### Requestor assessment for feature-request resume-paused (round 4)

#### Writer assessment for resume-paused replacement review for feature-request resume-paused (round 4)

The full specification retains Q01-Q19 and every confirmed human answer,
option, historical recommendation and explanation. The main body now states
the settled rules instead of presenting them as pending. No consolidation,
staging, commit, design or implementation has occurred.

Q11=C is now an operative requirement and acceptance criterion. Its recovery
requires empty pre-typing evidence, two stable post-delivery captures of the
tool-owned unsubmitted command, fresh protections, a single Enter addressed
to the full pane id, and fresh acceptance evidence. It covers every command
this tool types into Codex and never retries uncertain Claude input.

Seven explicit questions remain undecided: Q20-Q23 cover the four gaps raised
by the reviewer; Q24-Q26 track the three proposed clarifications separately
so the decision scanner cannot overlook them beside confirmed answers.
All recommendations are proposals. The three clarifications are also linked
beside Q01, Q17 and Q14 without changing their confirmed decisions.

Please assess whether the options are sufficient and identify any remaining
missing question. In particular check role-switch scope, same-LLM pane
ambiguity, consent, exact-exchange evidence and expected pending outcomes.

### Change summary for feature-request resume-paused (round 4)

#### Changes for resume-paused replacement review for feature-request resume-paused (round 4)

Since round 3:

- Promoted confirmed Q02, Q03, Q06-Q15 and Q19 rules into the body without
  removing question history. Added criteria for Q01, Q11 and Q17-Q19.
- Recast the caller as a human shell launch under Q16=B, supported an unset
  TUIOS_PANE_ID, and marked the draft's agent-run experiment as historical
  evidence. Removed the agent-caller preview example from the requirement.
- Added the Q17 assignment-input contract with syntax reserved for design.
- Defined Codex empty-input evidence and safe pane-addressed submission
  recovery in the body, including clear, resume and reviewer commands.
- Added read-only observation of exact-exchange role state, with no tool
  claim or fenced exchange mutation.
- Preserved the deferred senv checklist and its consolidation preservation rule.
- Added Q20-Q23 with BBQ, options, tradeoffs and pending decisions. Q22's
  recommended activity proof requires exact role state plus current pane
  evidence; a generic shell indicator alone never proves reviewer activity.
- Added Q24-Q26 for explicit confirmation of the proposed Q01/Q17/Q14
  clarifications. Q25 explains that an LLM role record does not by itself
  identify a unique pane when two panes share that LLM.

### Writer response for feature-request resume-paused (round 4)

Writer response:

#### Writer response for resume-paused replacement review for feature-request resume-paused (round 4)

Accepted the round-3 findings on stale body wording, acceptance criteria,
Codex submission evidence and delivery, human-only launch wording, role
assignment input and reviewer-only continuation. The draft now points to
Q11=C and labels the prior agent-run demonstration as evidence only.

The four suggested questions are Q20-Q23. The proposed clarifications beside
Q01, Q17 and Q14 are cross-referenced to Q24-Q26 so that pending confirmation
is machine-visible and cannot be mistaken for another confirmed answer.
No human decision is inferred from reviewer agreement or writer acceptance.

The reviewer's request to obtain human answers before the next request is
handled through the canonical requestor sequence: intermediate changes are
assessed and reviewed automatically; the human discussion is offered at
convergence. Therefore this round reviews the amended document and proposed
questions while Q20-Q26 remain pending. It does not claim those proposals are
settled behavior or authorize consolidation. After human decisions, the
explanation workflow requires another fresh independent review.

Please check the whole document and question set for consistency, including
the retained nineteen decisions. Converge on the adequacy of the pending
questions if no further substantive correction is needed; convergence does
not decide them. Otherwise identify the specific remaining gaps.

### Reviewer focus for feature-request resume-paused (round 4)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-11-08T02:02:14+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 4

I read the whole revised specification (SHA-256 `37067ec0...44f2`) and the
draft. I re-checked the review exchange's role-nature rules
(`tools/review_role_nature.py`, `tools/review_resume_identity.py`) and the
fields the coordination record exposes.

Every change requested in round 3 is in place:

- **Q11=C is now a requirement.** The delivery section and acceptance
  criterion 7 cover:
  - proof that the input was empty, from the capture that passed Q03;
  - two unchanged captures after delivery;
  - a single `tuios send-keys -s S -w <full pane id> Enter` after a Q13
    recheck;
  - the clear, `resume-session` and the reviewer instruction;
  - a report of whether the recovery Enter was used;
  - no recovery for Claude.

  This closes the queued Codex finding. What an implementer needs is now in
  the requirement sections, not only in the decision.
- **Q03** defines the empty Codex input line by its placeholder, to be checked
  on the Codex version in use.
- **The caller** is recast for Q16=B, and the tool must work outside TUIOS. The
  agent-caller example is gone from the requirement.
- **Decided rules** are stated as settled and cite their question. The command
  contract names the Q17 assignment input. Acceptance criteria 3, 7 and 9 are
  updated, and 11 to 13 are new.
- **Pending questions:** Q20 to Q23 are added as suggested, and Q24 to Q26 make
  the three proposed clarifications pending questions. That is better than my
  suggested side notes, because the decision scanner now sees them.

I checked whether the exchange would block the requestor-first order of a role
switch. Role-nature conflicts are checked one selected role at a time ("role-nature
conflicts require Override"), and no rule stops one LLM from briefly holding
both roles. The new requestor's Override claim can therefore come before the
new reviewer's. The reviewer-side Override question under Q24=A is then the
expected path, not a dead end.

Q18 can be observed. The coordination record exposes `role_natures`, `owner`
and `lease_renewed_at`.

- Without a switch, `role_natures.requestor` already names the requestor's LLM
  before it resumes. Takeover evidence is then the receipt for the current
  prompt, with the selected LLM in `Resumed by`, together with that record
  entry.
- With a switch, the entry changes only after the new requestor's Override
  claim.

Saying this in the body would help the design, but the decision can be
implemented as written.

I found no missing question. Q20 to Q26 have distinct options with stated
consequences. Their recommendations follow from Q16=B, Q18=A, Q19=A, Q06=C and
Q14=A, and none overrides a confirmed decision.

Only wording edits remain:

1. **Acceptance criterion 13** says "Enforce Q16=B's human-only launch
   contract". That assumes the tool enforces the rule at run time, which Q20's
   Option C would not do.
2. **Q20's Option A** should also tell the person that a command they type
   through an agent's shell escape, such as Claude Code's `!` prefix, runs in
   the agent's pane and would be refused.
3. **Q18 in the body:** a sentence naming the observable evidence described
   above would help.
4. **The draft** still shows `run resume-session here` for the caller's pane,
   in its "Choose the pane and the command" bullets and its preview example.
   Those should be marked historical, as the agent-run paragraph already is.

### Question verdicts for feature-request resume-paused round 4

The nineteen confirmed decisions stand as recorded. Q20 to Q26 are pending;
my answers are reviewer choices, not human decisions.

| Question | Status | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- | --- |
| Q01 to Q19 | Confirmed | Consistent with the body and with each other | As decided | None |
| Q20 | Pending | Agree | A | Option A's con: an agent's shell escape is refused too |
| Q21 | Pending | Agree | A | None |
| Q22 | Pending | Agree | A | None |
| Q23 | Pending | Agree | A | None |
| Q24 | Pending | Agree | A | None |
| Q25 | Pending | Agree | A | None |
| Q26 | Pending | Agree | A | None |

#### Reasons for the answers to the pending questions for feature-request resume-paused (round 4)

- Q20 A: it enforces Q16=B wherever the caller can be detected, and states the
  limit outside TUIOS.
- Q21 A: it keeps Q01=D to review-requestor pauses and never guesses an
  exchange.
- Q22 A: it applies Q19's leave-alone rule on every run, and needs evidence
  stronger than a shell indicator.
- Q23 A: a question still waiting for the person is not a delivery failure, and
  Q19 completes the step later.
- Q24 A: it keeps the explicit `Override` boundary that Q18=A and
  `review-resume` require.
- Q25 A: only a pane assignment can resolve two panes of one LLM.
- Q26 A: the selected role decides, whatever text Q01=D adds after it.

#### Suggested wording for Q20 option A for feature-request resume-paused (round 4)

```md
  - Con: Blocks previews from agent panes, including a command the person types through an agent's shell escape such as Claude Code's `!` prefix, and cannot detect every caller outside TUIOS.
```

#### Suggested wording for acceptance criterion 13 for feature-request resume-paused (round 4)

```md
13. Apply Q16=B's human-only launch contract; Q20 decides its runtime
    enforcement. Q20 to Q26 are unresolved refinements; their recommended
    options do not become acceptance criteria until the person decides them.
```

#### Suggested body sentence for Q18 evidence for feature-request resume-paused (round 4)

```md
Observable takeover evidence is a receipt for the current prompt naming the
selected LLM in `Resumed by`, and the exact exchange's recorded requestor
nature naming that LLM. After a role switch, that record changes only when the
new requestor's Override claim succeeds.
```

### Convergence evidence for feature-request resume-paused round 4

Covered wording:

This convergence recommendation covers the current formulation with these
wording-only edits:

1. Acceptance criterion 13 says "Apply" instead of "Enforce", and says that
   Q20 decides runtime enforcement.
2. Q20 Option A's con mentions a command the person types through an agent's
   shell escape.
3. Optionally, a body sentence under the Q18 rule names the observable
   takeover evidence, as suggested in the question verdicts.
4. In the draft, the caller-pane "run resume-session here" bullet and preview
   line are marked historical.

None of these edits changes a question's options, a recommendation or a
recorded decision.

Convergence rationale:

The nineteen confirmed decisions are consistent with each other and with the
body, which now states them as settled rules. Q20 to Q26 cover every gap that
the round 3 review found. Each of them offers distinct options with stated
consequences, and their recommendations follow from the confirmed decisions.
Q11=C's Codex submission recovery is now a requirement and an acceptance
criterion. The role switch is feasible under the exchange's per-role Override
rule. What remains is wording only.

This recommendation is advisory. It authorizes no consolidation and records no
human decision. Seven human decisions are outstanding: Q20, Q21, Q22, Q23, Q24,
Q25 and Q26, all marked `User decision: pending`. This convergence covers the
current formulation only. Once the person decides those questions, the
explanation workflow requires a fresh independent review of the decisions.

### Writer instructions for feature-request resume-paused round 4

No further automated review round is needed for this formulation.

1. At the next revision, apply the covered wording edits: acceptance criterion
   13, Q20 Option A's con, the optional Q18 evidence sentence and the draft's
   caller-pane lines.
2. Present Q20 to Q26 to the person for decision. Do not record a decision on
   the strength of this recommendation.
3. After the person decides, request the fresh independent review that the
   explanation workflow requires. Consolidation remains the person's separate
   choice.

### Final reviewer decision for feature-request resume-paused round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - human-confirmation

- Recorded: 2026-11-08T17:56:17+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: # Human guidance for the fresh resume-paused review

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 5 by requestor

- Recorded: 2026-11-08T17:59:10+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 5)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 5

### Requestor assessment for feature-request resume-paused (round 5)

#### Writer assessment of the decided resume-paused requirement for feature-request resume-paused (round 5)

The full decision scan now reports 26 questions, 26 explicit decisions,
zero undecided and no diagnostics. The reviewed requirement SHA-256 is
`c5ed8ea6862ff87a06d6e4052db2eac31045194eca1de3971d3a1b103ea36186`.
This is a fresh review of post-convergence human decisions and comments, not
a request to reuse round 4 convergence or consolidate the document.

The chosen rules appear sufficient for the requirement stage. Independently
check the whole specification for inconsistencies, missing questions and
options, rather than reviewing only the newest answer blocks. Human choices
are authoritative; recommendations must not silently replace them.

Q20-Q23=A, Q24=B with a broader command-wide automation amendment, Q25=custom
Option C requiring handoff-driven automatic target selection, and Q26=A.
Q01-Q19 retain their decisions, with explicit amendments to the author/role
consent qualifications and to Q06/Q17 target selection. Historical options
and recommendations are preserved as history.

One human invocation must authorize consuming the resolved pause and
establishing intended roles, including necessary pause-author, requestor and
reviewer overrides. Neither the tool nor receiving agents may ask again.
Q18 still requires actual intended-pause consumption and exact-exchange
requestor ownership before reviewer activation. Q23 processing observation
must not turn a repeated consent prompt into an acceptable pending outcome.

Q25 now requires the pause handoff to supply target identities and intended
roles automatically, including several panes of the same LLM. No required
pane-selection argument, routing question or interactive legacy migration
is permitted. Validate saved identities against live evidence; unresolved
targets receive no input and a report under the existing rules. Check whether
those rules distinguish ordinary absence from unreadable or uncertain evidence
adequately without contradicting the user's automation requirement.

Independently assess the actual documentation changes in
`instructions/pause-session.md`, `templates/pause-session.template.md` and
`wiki/how-to/pause-and-resume-a-session.md`, together with the draft and full
requirement. They add automatic routing capture, distinguish historical and
intended roles, and prohibit counterpart contact during capture. The bulk
command and shared resume authorization changes remain unimplemented.

Round 4 covered wording was applied before this discussion: the Q20 caller
shell-escape limitation and historical draft caller examples. Its optional
Q18 evidence sentence was not adopted because the requirement retains actual
consumption and ownership proof rather than relying on a pre-existing nature
entry alone. Reassess any remaining stale proposal wording or dependencies in
light of all now-confirmed choices.

### Change summary for feature-request resume-paused (round 5)

#### Changes since round 4 convergence for resume-paused for feature-request resume-paused (round 5)

- Recorded Q20=A: recognized agent caller panes are refused for normal and
  dry runs, including human shell escapes, with nonzero exit and no input.
- Recorded Q21=A: paired restoration is limited to saved requestor pauses
  with one identifiable live exchange; reviewer and other pauses resume one
  assigned agent, with no requestor activation from a reviewer pause.
- Recorded Q22=A: never clear the counterpart; leave a proved established
  exact-exchange reviewer untouched on every run. Otherwise deliver its native
  reviewer instruction when eligible after Q18 proof, claiming if required.
- Recorded Q23=A: bounded read-only takeover observation after accepted
  requestor delivery; expected processing pending alone is not failure.
- Recorded Q24=B plus the user's broader one-command amendment: the human
  invocation authorizes required pause-author and both role overrides without
  repeated confirmation, for resolved explicit or saved assignments. Changed
  the draft goal, command contract, target text, acceptance criterion and
  active Q01/Q17/Q18/Q22/Q23 qualifications. Shared resume-session/review-resume
  authorization changes are prerequisites to implementation.
- Recorded Q25=custom Option C after explicit rejection of launch-time pane
  selection. The handoff supplies intended resumed-agent and requestor/reviewer
  roles, observed TUIOS session/pane identity, checkout, time, exact exchange
  and assignment evidence. Amended Q06/Q17, command contract, selection rules,
  acceptance criteria and draft. Saved routing is checked against live evidence;
  no pane-selection argument or runtime selection/migration question is required.
- Updated the canonical pause instruction and template in this working tree
  to capture that routing through read-only observation, record explicit
  unknowns without losing the checkpoint, preserve historical versus intended
  roles, and never contact the counterpart or invoke the bulk command. Updated
  the pause/resume wiki how-to and stated the runtime implementation limit.
- Recorded Q26=A: identify reviewer-only continuation by selected role across
  native prefixes and trailing context. Applied the Q14 clarification,
  duplicate-detection text and acceptance criterion. Uncertain evidence still
  prevents input under Q07/Q08.
- Preserved question IDs, original options, historical recommendations and
  recorded user rationales. The private question companion mirrors the entire
  question section. No consolidation, staging, commits or command implementation.

### Human guidance and writer response for feature-request resume-paused (round 5)

Human guidance:

#### Human guidance for the fresh resume-paused review for feature-request resume-paused (round 5)

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Writer response:

#### Writer response for the post-decision resume-paused review for feature-request resume-paused (round 5)

The human completed the explanation batch and authorized this fresh review.
Round 4 convergence covered the earlier formulation, whose Q20-Q26 were still
pending; it cannot settle these subsequent decisions and comments.

Please review the complete requirement and related draft, plus the changed
pause instruction, handoff template and wiki how-to. Check effects on earlier
decisions, role switching, exact-exchange identity, duplicate protection,
requestor-before-reviewer ordering, bounded takeover observation, protected
panes, result classification and verified reviewer-only continuation.

Pay particular attention to the intentional Q24 and Q25 contract changes.
Existing shared resume instructions still requiring author/role confirmation
are dependencies to amend before implementation, not grounds to ask the user
for the same confirmation in the planned automated route. The actual pause
instruction/template edits should capture enough identifying evidence to
avoid selecting a same-LLM pane by order, guessing a role, or trusting a reused
id. Assess missing, conflicting, stale and legacy routing explicitly.

Q16/Q20's human-only launch and review role isolation remain unchanged. No
agent ran `resume_paused`, contacted a counterpart, or started a reviewer.

If the decisions expose another substantive question, identify it and explain
why the recorded choices do not answer it. Preserve user choices and historical
recommendations separately. Do not infer consolidation authority from either
the completed decision scan or the review request.

### Reviewer focus for feature-request resume-paused (round 5)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-5 -->

## Round 5 by reviewer

- Recorded: 2026-11-08T18:14:15+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 5

I read the whole requirement (SHA-256 `c5ed8ea6...6186`) and the draft. I also
read the new routing section of `instructions/pause-session.md`, the routing
block of `templates/pause-session.template.md` and the wiki how-to diff. To
check the dependencies, I read the consent rules in
`instructions/resume-session.md`, the decision reader
`tools/question_decisions.py`, and how `tools/program_status.py` treats
commands that the shared Codex app-server daemon runs.

#### What holds after the decisions for feature-request resume-paused (round 5)

- All 26 questions carry a `User decision: confirmed` record. The decisions
  agree on the core rules:
  - human-only launch (Q16=B, Q20=A);
  - requestor first, with takeover proof (Q01=D, Q18=A);
  - leave an active reviewer alone and never clear it (Q19=A, Q22=A);
  - a bounded, read-only takeover wait (Q23=A);
  - one-command authorization (Q24=B);
  - selection from the handoff (Q25=C);
  - matching reviewer continuation by role (Q26=A).
- The Q24=B amendment is applied in the command contract, the target
  selection section, acceptance criterion 11 and the Q01, Q17, Q18, Q22 and
  Q23 answers. Amending `resume-session` and `review-resume` is stated as a
  prerequisite. That is the right place for it: today `resume-session`
  accepts as consent only "an explicit yes from the user in this
  conversation, after the notice".
- The pause instruction gathers routing read-only. It never contacts the
  counterpart and never runs the bulk command. It records unknowns without
  asking, and it keeps historical authorship apart from intended roles. This
  matches Q25=C and role-session isolation.

#### What does not hold yet, by impact for feature-request resume-paused (round 5)

1. **Saved routing versus the earlier uniqueness rules (new Q27).** The
   requirement sends "no input to unresolved targets" when routing is
   missing, stale or legacy. It never says whether Q06=C's exactly-one-pane
   rule still resolves a target when there is no routing. Read literally, the
   first run after delivery resumes nothing:
   - every existing prompt lacks a routing section;
   - so does every pause where TUIOS could not identify the pane, including
     the common checkout with one Claude pane that Q06=C resumed safely.

   Exchanges have the same gap. The handoff now records the exact exchange,
   yet Q21=A still treats several live exchanges as ambiguous. The recorded
   choices do not say how saved routing combines with these earlier rules.
2. **A role switch decided after the pause (new Q28).** Q17=A originally
   accepted an explicit per-tab assignment at launch, naming the requestor
   LLM. Q25=C removed pane-selection arguments, and the command contract now
   has no role input at all. The draft's main example is Codex taking over as
   requestor from Claude. That switch is often decided at resume time, for
   example when one LLM's quota ran out overnight. Under the current text, a
   switch must be stated to the pausing agent before it pauses. Afterwards no
   one-command path exists.

   Q25's user text rejects choosing panes at launch. It says nothing about
   naming roles at launch. The person's own Q24 comment, "if I specify a
   role, I do not want to have to confirm", suggests they expect to name one.
3. **How the typed command carries the launch authorization (new Q29).** The
   requirement says saved assignments are "carried into the target workflows
   as sufficient authorization". It does not say how a receiving
   `resume-session` or `review-resume` tells this delivered command apart from
   the same command typed by hand, which today must still ask. The answer
   decides three things:
   - whether manual resumes change behavior;
   - whether the tool writes anything, although acceptance criterion 9 says
     it only reads;
   - whether a replaced prompt can be consumed on stale authority.

   It also conflicts with the template's statement that the file "does not
   grant new permissions", unless the requirement says where the authority
   comes from.
4. **Same-host pauses replace each other's checkpoint (new Q30).**
   `pause-session` asks before replacing an unused prompt only when the agent
   id differs or is missing. Take a tab with two Claude panes, the layout
   Q25=C now supports. The reviewer's pause silently replaces the requestor's
   unused prompt and its routing, and Q21=A then resumes only the reviewer.
   This requirement now owns the pause instruction, so the case belongs in
   scope or needs an explicit exclusion.
5. **Pause capture can record the wrong Codex pane.** The new instruction
   checks `TUIOS_PANE_ID` against the listing and the checkout. But
   `tools/program_status.py` documents that a command run by the shared Codex
   app-server daemon "descends from another session". Its inherited pane
   variables can belong to the pane that started the daemon. When that pane
   is another Codex pane of the same checkout, host and folder both match, and
   the wrong pane is recorded silently. That is the same-LLM case Q25=C is
   meant to solve.
6. **Stale and contradictory text.**
   - Five sentences in the body still describe Q20 to Q23 as open.
   - The Q24 answer heading says `option A`, but its decision is B. The
     decision reader uses only the `User decision:` line, so the scan is
     correct, but a person or a consolidation step reading the heading gets
     the wrong answer.
   - The skip list and the result section lack the routing outcomes and the
     Q23=A rule that a repeated confirmation prompt is a failure.
   - The draft still shows a `SKIP ... already cleared` example that Q12=A
     replaced, and says "one line per pane" where Q15=A chose one line per
     checkout. Its open-questions notes are all decided now.

Items 1 to 4 need decisions from the person, so this formulation is not ready
for convergence. Items 5 and 6 are corrections the writer can make directly.

### Question verdicts for feature-request resume-paused round 5

The 26 decisions stand as recorded; I do not reopen any of them. The table
notes where a decision interacts with Q25=C or has a text defect. My answers
to the proposed Q27 to Q30 are reviewer choices, not human decisions.

| Question | Status | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- | --- |
| Q01 to Q05 | Confirmed | Consistent | As decided | None |
| Q06 | Confirmed C, amended by Q25 | Consistent, but the fallback when routing is absent is undecided | As decided | Settle through Q27 |
| Q07 to Q16 | Confirmed | Consistent | As decided | None |
| Q17 | Confirmed A, amended by Q25 | Consistent, but no path is left for a switch decided after the pause | As decided | Settle through Q28 |
| Q18 to Q20 | Confirmed | Consistent | As decided | None |
| Q21 | Confirmed A | A saved exact exchange should count as the one identifiable exchange | As decided | Settle through Q27 |
| Q22, Q23 | Confirmed | Consistent | As decided | Body text still calls them open |
| Q24 | Confirmed B | The heading says `option A` | As decided | Heading and historical label |
| Q25 | Confirmed C | Its consequences are open in Q27 and Q28 | As decided | None in Q25 itself |
| Q26 | Confirmed A | Consistent | As decided | None |
| Q27 (new) | Proposed | Missing decision | A | Add the question |
| Q28 (new) | Proposed | Missing decision | B | Add the question |
| Q29 (new) | Proposed | Missing decision | A | Add the question |
| Q30 (new) | Proposed | Missing decision | A | Add the question |

#### Reasons for the reviewer answers to the proposed questions for feature-request resume-paused (round 5)

- Q27 A: it keeps one-command resumption in every case Q06=C already handled
  safely. Saved routing then adds coverage only where Q06=C would have
  skipped. A saved id that now points elsewhere stays a conflict, so a reused
  id is never trusted.
- Q28 B: it lets the person switch roles at resume time while every pane
  still comes from the handoff, which Q25's user text requires.
- Q29 A: the authority applies only to the bulk path. It is tied to prompt
  bytes and a pane that the tool has just rechecked under Q13, and manual
  resumes keep their current questions.
- Q30 A: it extends the pause workflow's existing replacement guard to the
  same-LLM layout that Q25 now supports. The question comes at pause time,
  never during the one-command resume.

### Requested changes for feature-request resume-paused round 5

Requested changes:

#### Proposed new questions after the post-convergence decisions for feature-request resume-paused (round 5)

Add these four questions after Q26, without a `User decision` line. Their
answers are proposals until the person decides.

```md
### Q27: Combining saved routing with the earlier uniqueness rules

Q25=C makes the saved handoff the source of targets. Missing, stale,
conflicting or legacy routing sends no input to unresolved targets. The
requirement does not say whether Q06=C's exactly-one-pane rule, or Q21=A's
exactly-one-exchange rule, can still resolve a target when routing is absent,
unknown, or names a pane that no longer exists. No prompt saved before this
change has routing. Neither does a pause where TUIOS could not identify the
pane. In every option, a target that nothing resolves is an expected Q06 skip
under Q10. A saved id whose live pane shows another checkout, host or session
is a Q07 conflict error. Guessing stays forbidden.

#### BBQ for Q27

At a barbecue, a seating card names a guest's chair; without a card, a table
with a single chair still has only one place to serve. In this picture: the
card is saved routing, the chair is a pane, and the single chair is Q06=C's
one matching pane.

#### Options for Q27

- Option A: Use saved routing first, checked against live state. When it is
  absent or unknown, or names a pane id missing from live discovery, fall back
  to the earlier rules: exactly one live pane of the resumed host in the
  checkout (Q06=C), the pause author as requestor only for a requestor pause,
  a unique other LLM in the same session and checkout as counterpart (Q01=D),
  and exactly one live exchange (Q21=A). A saved exchange that is live, with
  natures matching the intended targets, is the one identifiable exchange even
  when others are live. Never fall back for a role switch. Report the routing
  source on each line.
  - Pro: Existing prompts, and pauses without pane evidence, still resume in
    the usual one-pane-per-host layout, with Q06=C's no-guessing protection.
  - Con: A fallback target is matched only by host and checkout, so a pane
    replaced since the pause can receive the resume, as before Q25.
- Option B: Use saved routing only. Absent, unknown, stale or legacy routing
  gets no input and a skip report. A saved exchange still resolves Q21's
  several-exchange case.
  - Pro: One selection source, applied the same way everywhere.
  - Con: The first runs after delivery resume no existing prompt. A pause
    that could not see its pane needs a manual resume, even in a checkout
    with one pane.
- Option C: Fall back as in Option A only for legacy prompts without a routing
  section. A new prompt whose routing records an unknown gets no input.
  - Pro: Existing prompts keep resuming, while new pauses must carry routing.
  - Con: A new pause that could not identify its pane is skipped even when its
    checkout has one matching pane. Codex under the shared daemon is one
    such case.

#### Recommended option for Q27

Option A: It keeps one-command resumption wherever Q06=C was already safe,
and saved routing adds coverage only where Q06=C would have skipped.

#### Answer to Q27: option A

Option A is proposed because it keeps every earlier safe resumption, and a
conflicting saved id still blocks input.

### Q28: Stating a role switch after the pause

Q17=A accepted an explicit per-tab role assignment at launch, naming the
requestor LLM. Q25=C removed pane-selection arguments, and the command now has
no role input. A switch must therefore be stated to the pausing agent before
the handoff is saved. The draft's own example, Codex taking over as requestor
from Claude, is often decided at resume time, for example when one LLM's
quota ran out overnight. Q25's user text rejects choosing panes at launch. It
does not say whether a role switch can still be named at launch.

#### BBQ for Q28

At a barbecue, the host can swap the cook and the inspector at serving time
without pointing at chairs, because the seating plan already says who sits
where. In this picture: the seating plan is saved routing, the swap is a role
switch, and pointing at chairs is pane selection.

#### Options for Q28

- Option A: Record role switches only at pause time. A later switch needs a
  fresh pause or a manual resume.
  - Pro: Assignments have one source, and the command needs no new argument.
  - Con: A switch decided after pausing has no one-command path, and a
    cleared conversation cannot pause again.
- Option B: Add an optional `--switch-roles NAME[,NAME...]` argument. Names
  are matched like `--except`, against session and checkout folder names. The
  argument swaps the saved requestor and reviewer targets of a saved requestor
  pause with a recorded pair. It names no pane: both panes come from the
  validated handoff. The launch authorizes the switch under Q24=B. An
  unmatched name prevents all input, like a Q09 unmatched exclusion. A matched
  checkout without a recorded pair gets no input, and the run fails.
  - Pro: Covers a late decision in one command, with no pane selection and no
    question.
  - Con: Adds an argument, which can only swap a pair the handoff already
    recorded.
- Option C: The person edits the handoff's intended assignment by hand before
  launching.
  - Pro: No new argument.
  - Con: Hand edits to a private prompt are easy to get wrong, and nothing
    checks them before input.

#### Recommended option for Q28

Option B: The person can still switch roles at resume time, while every pane
comes from the handoff as Q25 requires.

#### Answer to Q28: option B

Option B is proposed because it covers the draft's role-switch example in one
command without reintroducing pane selection.

### Q29: How the typed command carries the launch authorization

Q24=B makes the human launch sufficient authorization for author and role
overrides. Today `resume-session` accepts consent only as an explicit yes in
its own conversation, and `review-resume` only as an explicit `Override`. The
requirement asks both workflows to accept the launch instead. It does not say
how a receiving workflow tells a bulk-delivered command apart from the same
command typed by hand. Unless that also changes, the hand-typed command keeps
today's questions. Any process that can type into a pane can produce the same
text. That is already true of typed input today.

#### BBQ for Q29

At a barbecue, a host's note saying "seat this guest at table 4" is useful only
if the waiter can tell it from any scribbled note, and only for table 4. In
this picture: the note is the typed command, table 4 is the target pane and
prompt, and the waiter is the receiving workflow.

#### Options for Q29

- Option A: The typed command carries an explicit bulk-resume marker bound to
  its target: the prompt SHA-256, the receiving pane id, the intended role and,
  for a reviewer, the exact exchange. A marker that matches the receiving
  pane, host, current prompt digest and exchange counts as the person's
  consent, with no question. A mismatched marker grants nothing: the workflow
  reports the mismatch and stops without consuming the prompt. A command typed
  by hand without a marker keeps today's consent questions.
  - Pro: The authority covers only this launch, these prompt bytes and this
    pane. A replaced prompt or another pane cannot reuse it, and manual
    resumes are unchanged.
  - Con: Typed commands get longer, and both shared workflows need marker
    parsing and matching rules.
- Option B: In the pane named by the saved routing, any `resume-session` or
  `review-resume` skips the consent question, whoever typed it.
  - Pro: No marker, and manual resumes in that pane stop asking too.
  - Con: A saved prompt becomes consent. That contradicts the template's
    statement that the file grants no permissions, and today's rule that a
    saved prompt is not consent. An old handoff keeps authorizing later
    invocations.
- Option C: The tool writes a single-use authorization record in the artifact
  home, and the typed command refers to it.
  - Pro: The authority lives in a checked file rather than in typed text.
  - Con: Contradicts acceptance criterion 9's read-only tool and adds an
    artifact to create, expire and clean up. Any local process can still
    write it.

#### Recommended option for Q29

Option A: It meets the one-command contract on the bulk path only, and ties
the authority to exact bytes and to a pane the tool has just rechecked under
Q13.

#### Answer to Q29: option A

Option A is proposed because it limits the authorization to the launch that
granted it, without changing manual resumes.

### Q30: Pauses from two panes running the same host

`pause-session` asks before replacing an unused prompt only when the agent id
differs or is missing. Q25=C now supports several panes of one LLM in a
checkout. When a requestor and a reviewer both run Claude and both pause, the
second pause silently replaces the first unused prompt and its routing. Q21=A
then resumes only the role saved last. Should the replacement check also
compare the pausing pane and saved role?

#### BBQ for Q30

At a barbecue, two cooks in the same apron can each leave a note on the one
hook; the second note should not silently take the first note's place. In this
picture: the apron is the agent id, the hook is the checkout's single prompt
slot, and the notes are pause prompts.

#### Options for Q30

- Option A: Treat a different recorded pausing pane or saved role like a
  different agent id. Before replacing an unused prompt, name its pane and
  role, and ask, as a choice under `interactive_menu.md`.
  - Pro: Protects an unresumed checkpoint as the existing guard does. The
    question comes at pause time, never during the one-command resume.
  - Con: Adds a pause-time question for same-host pairs. Legacy prompts can be
    compared only by agent id.
- Option B: Keep the agent-id check. The last pause in a checkout wins, and
  the requirement documents the limitation.
  - Pro: The pause workflow does not change.
  - Con: A same-host pair loses the requestor's checkpoint and routing
    whenever its reviewer pauses last.
- Option C: Never replace an unused prompt saved by another pane or role. The
  second pause reports it and stops until that prompt is resumed or discarded.
  - Pro: No checkpoint is lost and no question is asked.
  - Con: The second pane cannot save its context until the first prompt is
    handled.

#### Recommended option for Q30

Option A: It extends a protection the pause workflow already has to the
same-LLM layout that Q25 supports.

#### Answer to Q30: option A

Option A is proposed because the pause workflow already asks before
discarding another agent's unresumed checkpoint.
```

#### Corrections to stale decision text for feature-request resume-paused (round 5)

Replace these sentences in the requirement:

- Line 25, "Enforcement is an open choice in Q20.":

  ```md
  Q20=A enforces it by refusing every invocation, including `--dry-run`, from
  a recognized agent caller pane.
  ```

- Lines 178-179, "Q22 asks how the leave-alone rule applies ...":

  ```md
  Q22=A applies the leave-alone rule on every run and never clears the
  counterpart.
  ```

- Lines 213-214, "Q21 asks which pause roles lead to activation; Q23 asks ...":

  ```md
  Q21=A limits activation to a saved requestor pause with one identifiable
  live exchange. Q23=A waits a bounded time for takeover and reports a pending
  reviewer step without failing the run.
  ```

- Lines 260-261, "Counterpart clearing remains open in Q22.":

  ```md
  Under Q22=A, `--clear` never clears the counterpart.
  ```

- Lines 325-326, "Q23 separately asks how a reviewer step pending Q18 takeover
  affects reporting and exit status.":

  ```md
  Under Q23=A, a reviewer step still waiting for Q18 takeover after the
  bounded wait is reported as pending and does not fail the run. A target that
  stops on an author, role or routing confirmation question fails the run,
  because the one-command contract forbids that question.
  ```

- Line 1278, `#### Answer to Q24: option A`: change it to
  `#### Answer to Q24: option B`. Start the paragraph below it with
  "Historical proposal:", as the Q11, Q18 and Q25 answers do.

#### Routing outcomes missing from the report rules for feature-request resume-paused (round 5)

- In the skip list (lines 217-221), after "an already-resuming checkout", add:
  "unresolved, stale or conflicting saved routing, or a legacy handoff that
  Q27 does not resolve".
- In the dry-run and result rules, report each target's routing source: saved,
  fallback under Q27, or unresolved.

#### Authorization source wording for feature-request resume-paused (round 5)

In the command contract (line 48), replace "Saved intended assignments must be
carried into the target workflows as sufficient authorization" with:

```md
The launch is the authorization. The saved intended assignments set its scope
and are carried into the target workflows with it, as Q29 decides. The saved
file alone grants nothing, as the pause template states.
```

#### Pause instruction and template corrections for feature-request resume-paused (round 5)

- In `instructions/pause-session.md`, after the sentence that reconciles
  `TUIOS_PANE_ID`, add:

  ```md
  A command run by a process without its own console, such as the shared Codex
  app-server daemon, can inherit the pane variables of another session. Record
  the pausing pane only when other read-only evidence agrees, such as the pane
  screen showing this pause request. Otherwise record it as unknown with that
  reason.
  ```

- In the same section, name the exact exchange fields to save: family,
  reviewed document or implementation plan, umbrella or none, implementation
  step for code review, and exchange occurrence. These are the values
  `resume-inspect` and `claim` take. Add that exchange role state names host
  natures, not panes. For a same-host counterpart, list the read-only evidence
  used, such as its agent log or screen showing its last `review-resume` role.
- In the template's `Review pairing` line, list those same exchange fields.

#### Draft alignment with the decisions for feature-request resume-paused (round 5)

- Line 194: replace "one line per pane" with "one line per checkout holding a
  prompt (Q15=A)".
- Line 199: replace the `SKIP docs/Claude docs` example with the requirement's
  Q12=A line,
  `RESUME docs/Claude docs: already cleared at 00:42, /resume-session for 'Update the guide', paused by claude at 2026-11-07 00:30`.
- Line 214: replace the exit sentence with "Exit status follows the
  requirement's Q10=A and Q23=A rules."
- Lines 235-249: mark the notes as resolved in the requirement (Q01=D, Q02=A,
  Q03=A, Q04=A, Q05=A), or remove them.

### Human guidance response for feature-request resume-paused round 5

Human guidance:

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Guidance response:

I treated every quoted comment as binding and reopened none of the decisions.

- "One command and it is done": none of the four new questions adds a question
  at resume time.
  - Q27 lets more targets resolve without asking.
  - Q28 gives a role switch decided after the pause a one-command path.
  - Q29 only decides how the launch authority reaches the two workflows.
  - Q30's question, under its recommended option, comes at pause time.
- "If I specify a role, I do not want to have to confirm": the requirement
  currently leaves no place to specify a role after the pause. Q28 asks
  whether to add one.
- The Q25 comment: every option in Q27 and Q28 still takes panes from the
  saved handoff. None adds pane selection at launch or a routing question.
  The pause instruction change carries out the requested documentation
  update; my corrections to it are about recording the right pane.
- The scope limits are respected: this answer requests no consolidation,
  implementation, staging or commit.

### Writer instructions for feature-request resume-paused round 5

Another automated review round is needed.

1. Add Q27 to Q30 from the requested changes as pending questions, with no
   `User decision` line. Do not record my recommendations as decisions.
2. Fix the Q24 answer heading to `option B`, and label the paragraph below it
   as a historical proposal.
3. Replace the five sentences that still describe Q20 to Q23 as open, using
   the wording supplied. Add the routing outcomes to the skip list and to the
   result rules. State that a target stopping on a confirmation question fails
   the run.
4. Reword the command contract's authorization sentence so the launch is the
   authority and the saved assignments set its scope.
5. In `instructions/pause-session.md`, add the rule about pane variables
   inherited from a console-less process. Name the exact exchange fields to
   save, and the evidence for a same-host counterpart. List the same exchange
   fields in the template's `Review pairing` line.
6. Align the draft's preview example, line wording, exit sentence and notes
   with Q10, Q12, Q15 and Q23, or mark them as superseded by the requirement.
7. The wiki how-to paragraph is accurate today. Have the plan revisit it when
   the bulk command ships.
8. Present Q27 to Q30 to the person through the explanation workflow. After
   their decisions, request a fresh independent review. Consolidation,
   implementation, staging and commits stay unauthorized.

### Final reviewer decision for feature-request resume-paused round 5

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-5 -->

## Round 6 by requestor

- Recorded: 2026-11-08T18:22:27+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 6)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 6

### Requestor assessment for feature-request resume-paused (round 6)

#### Writer assessment for feature-request resume-paused (round 6)

All 26 existing user decisions remain recorded and unchanged. The full scanner
reports 29 questions, 3 undecided (Q27-Q29), and no diagnostics. The three added
questions preserve reviewer proposals as proposals, with no human decision.

The requirement, draft, pause instruction, template and wiki are the reviewed
scope. The bulk command and shared authorization changes remain unimplemented.
Consolidation, implementation, staging and commits remain unauthorized.

The round 5 routing-fallback question is not added. Q25 already explicitly
requires handoff-driven selection and reports unresolved, missing, stale,
conflicting and legacy routing without input to unresolved targets. Its verbatim
user direction requires that this selection question never recur. Recommending
fallback to a newly discovered unique pane would reopen that decision. The body
now explicitly says that the former one-candidate rule supplies no fallback.
A saved exact exchange validated as live is Q21's one identifiable exchange;
several other exchanges do not make that identified exchange ambiguous.

The remaining proposed questions concern distinct unresolved behavior: a role
swap decided after pausing, carrying human launch authorization to the receiving
workflows, and protecting an unused checkpoint from another same-host pane.
Their options are sufficient for review as proposed choices. None introduces
a runtime selection or confirmation question into the bulk resume path.

Review the whole specification and related documentation for consistency,
missing questions and effects on earlier decisions. Assess the three pending
question formulations before returning to the explanation workflow. This round
does not claim that their proposed answers are human decisions.

### Change summary for feature-request resume-paused (round 6)

#### Changes since round 5 for feature-request resume-paused (round 6)

- Corrected five stale body references to Q20-Q23 and the Q24 answer heading.
- Made the human launch the authorization source; saved routing sets its scope
  and grants no permissions by itself.
- Added routing source and validation reporting, distinguished expected missing
  routing skips from contradictory-evidence errors, and stated that repeated
  confirmation prompts fail the run.
- Clarified handoff-only selection without a unique-pane fallback and the use
  of a saved, validated exact exchange under Q21.
- Required independent pane evidence because a shared Codex app-server daemon
  can inherit another session's TUIOS variables. Listed exact exchange fields
  and same-host role-to-pane evidence in the pause instruction and template.
- Aligned draft preview, reporting, exit status and original question notes
  with confirmed decisions. The wiki paragraph remains accurate and unchanged.
- Added the reviewer's proposed Q28-Q30 as document Q27-Q29, without decision
  records. Did not add the proposed fallback-routing question, which would
  reopen Q25. Refreshed the private question companion.

The original staged draft blob remains unchanged. No staging or commit occurred.

### Human guidance and writer response for feature-request resume-paused (round 6)

Human guidance:

#### Human guidance for the fresh resume-paused review for feature-request resume-paused (round 6)

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Writer response:

#### Response to round 5 for feature-request resume-paused (round 6)

Accepted the concrete documentation corrections, authorization-source wording,
reporting corrections, daemon pane-identity warning, exact exchange fields,
same-host evidence rule and draft alignment. Applied them before this round.
The wiki should be revisited in the implementation plan when the command ships.

There is one explicit disagreement: the proposed Q27 fallback-routing question
is already answered by Q25's direct user amendment. The recorded answer says:

> Selection must come from information saved in the pause-session handoff.

It also explicitly requires reporting unresolved, missing, stale, conflicting
and legacy routing without input to unresolved targets or an interactive
question. The user's verbatim instruction requires Q25 never to be asked again.
Accordingly, the body now removes any residual ambiguity: no unique-live-pane
fallback substitutes for missing saved identity. Missing or unknown routing is
an expected skip; contradictory required evidence remains a Q07 error.

The exact saved exchange, when validated as live, resolves Q21's "one
identifiable" exchange; without it, the tool never chooses among multiple
exchanges. This clarifies existing handoff and exact-exchange decisions.

Accepted the other three missing-behavior proposals as pending questions.
Mapping from the round 5 answer to this document is Q28 -> Q27 (late role swap),
Q29 -> Q28 (launch authorization), Q30 -> Q29 (same-host checkpoint replacement).
All their answers remain reviewer proposals. Please assess their sufficiency
and the whole specification without requesting the person's answers before
the current automated review reaches its ordinary human discussion gate.

Preserve every existing human decision, the handoff-only target source and
the one-command authorization requirement. No consolidation or implementation
is requested or authorized.

### Reviewer focus for feature-request resume-paused (round 6)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-6 -->

## Round 6 by reviewer

- Recorded: 2026-11-08T18:28:39+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 6

I read the whole revised requirement (SHA-256 `eef42231...f241`), the draft, the
routing section of `instructions/pause-session.md` and the routing block of
`templates/pause-session.template.md`. The wiki how-to is unchanged since
round 5.

#### Round 5 corrections now in place for feature-request resume-paused (round 6)

- The five body sentences that called Q20 to Q23 open now state the decided
  outcomes. The Q24 answer heading says `option B`, and its Option A text is
  labeled as a historical proposal.
- The command contract makes the human launch the authority. The saved
  assignments set its scope and grant nothing alone, which now agrees with the
  template's "does not grant new permissions" line.
- The skip and result rules cover routing:
  - missing or unknown routing is an expected skip under Q06 and Q10;
  - contradictory or unreadable identity evidence is a Q07 error;
  - each target reports its routing source;
  - a target that stops on a confirmation question fails the run.
- The pause instruction warns that the shared Codex daemon can carry another
  session's pane variables, and it requires independent evidence in that
  case. It names the exact exchange fields and the evidence for a same-host
  counterpart, and the template's `Review pairing` line lists the same fields.
- The draft's preview, exit sentence and notes now follow Q10, Q12, Q15 and
  Q23.

#### The writer's disagreement on the fallback question for feature-request resume-paused (round 6)

I accept it. The recorded Q25 decision says selection "must come from
information saved in the pause-session handoff". It explicitly reports legacy
routing "without input to unresolved targets". The option the person chose
also names, as its cost, that "legacy or unresolved routing must be reported
rather than guessed". Asking again whether a live single candidate may stand
in for missing routing would put that settled point back in front of the
person.

The practical cost is also smaller than I estimated in round 5. The pause
instruction change ships with this effort, before the bulk command, so most
prompts the command meets will carry routing.

Two answer blocks still read as they did before this clarification, though:

- **Q06** still says "Resume only when the checkout has exactly one pane of
  the pausing agent". Its Q25 note says only that the one-candidate rule "no
  longer forces a skip" when routing exists. The body now goes further: a
  single live candidate never replaces missing saved identity. For a legacy
  prompt in a one-pane checkout, the recorded Q06 text and the body give
  opposite outcomes.
- **Q21** still says that several live exchanges make the reviewer step
  ambiguous. The body now lets a saved exchange that is validated as live
  resolve that case.

Both changes follow from Q25, but a person reading only the decision blocks
would not see them. A short consequence note in each block keeps the decision
record consistent with the body. When the explanation workflow presents Q27
to Q29, the writer should also say plainly that, after delivery, prompts
saved without routing are not bulk-resumed.

#### The three pending questions for feature-request resume-paused (round 6)

Q27 to Q29 match my round 5 proposals. Each has materially distinct options
with real consequences and a recommendation that follows from the confirmed
decisions. None adds a question at resume time. Two option texts can be
sharpened:

- Q27 Option B does not say how a later run interacts with Q19's
  reviewer-only continuation once a switch has been applied.
- Q28 Option A says a mismatched marker stops without consuming the prompt.
  It should also say that no role is claimed.

I found no other missing decision, and no contradiction elsewhere in the
whole specification.

### Question verdicts for feature-request resume-paused round 6

The 26 decisions stand as recorded. Q27 to Q29 are pending; my answers below
are reviewer choices, not human decisions.

| Question | Status | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- | --- |
| Q01 to Q05 | Confirmed | Consistent | As decided | None |
| Q06 | Confirmed C, amended by Q25 | The body's no-fallback rule is not visible in the answer block | As decided | Q25 consequence note |
| Q07 to Q20 | Confirmed | Consistent | As decided | None |
| Q21 | Confirmed A | The body's saved-exchange rule is not visible in the answer block | As decided | Q25 clarification note |
| Q22 to Q26 | Confirmed | Consistent; the Q24 heading is fixed | As decided | None |
| Q27 | Proposed | Agree | B | Option B: later-run sentence |
| Q28 | Proposed | Agree | A | Option A: no role claimed on mismatch |
| Q29 | Proposed | Agree | A | None |

#### Reasons for the reviewer answers to the pending questions for feature-request resume-paused (round 6)

- Q27 B: it gives a role switch decided after the pause a one-command path,
  while every pane still comes from the saved handoff, as Q25 requires.
- Q28 A: the authority applies only to the bulk path. It is tied to the prompt
  bytes, the pane and the role that the tool has just rechecked under Q13, and
  commands typed by hand keep today's questions.
- Q29 A: it extends the existing replacement guard to the same-LLM layout
  that Q25 supports, and its question comes at pause time, never during the
  one-command resume.

### Convergence evidence for feature-request resume-paused round 6

Covered wording:

#### Q06 answer block: consequence of the Q25 decision for feature-request resume-paused (round 6)

Append after the existing "User amendment on 2026-11-08 (Q25)" paragraph. It
records a consequence and is not a new user decision:

```md
Consequence of the Q25 decision, recorded on 2026-11-08: when the handoff
cannot identify a target, including a legacy prompt without routing, a single
live candidate does not replace the missing saved identity. That target gets
no input and an expected skip; the person can still resume it with ordinary
`resume-session`.
```

#### Q21 answer block: clarification from the Q25 decision for feature-request resume-paused (round 6)

Append after the Q21 decision-date paragraph:

```md
Clarification from the Q25 decision, recorded on 2026-11-08: a saved exact
exchange validated as live is the one identifiable exchange, even when other
exchanges are live. Without a valid saved exchange, several live exchanges
remain ambiguous. For a reviewer pause, the author default means the pausing
pane recorded in the handoff.
```

#### Q27 Option B: a later run after the switch for feature-request resume-paused (round 6)

After "A matched checkout without a recorded pair gets no input, and the run
fails.", add:

```md
On a later run, Q19's reviewer-only continuation checks the resumed requestor
against the assignment this invocation resolves, with or without the switch;
a mismatch sends no input and is reported.
```

#### Q28 Option A: a mismatched marker for feature-request resume-paused (round 6)

Replace "stops without consuming the prompt" with "stops without consuming the
prompt or claiming a role".

#### Optional polish for the pause instruction for feature-request resume-paused (round 6)

In `instructions/pause-session.md`, replace "such as its screen showing this
pause request" with "such as that pane's screen or agent log showing this
pause request".

Convergence rationale:

No further automated review round is needed for this formulation.

- Every substantive round 5 correction is applied in the requirement, the
  pause instruction, the template and the draft.
- The writer's disagreement on the fallback question is supported by the
  recorded Q25 decision and the cost the person accepted with it.
- Q27 to Q29 are complete, with distinct options and recommendations that
  follow from the confirmed decisions.
- What remains is wording:
  - two consequence notes that copy rules already in the body into the Q06
    and Q21 answer blocks;
  - one sentence each sharpening an option of Q27 and of Q28;
  - an optional phrase in the pause instruction.

Outstanding human decisions: Q27, Q28 and Q29, whose proposed answers (B, A,
A) are not confirmed. The person should also hear, when Q27 to Q29 are
presented, that prompts saved without routing are not bulk-resumed under Q25.

This recommendation is advisory. It does not authorize consolidation,
implementation, staging or commits.

### Human guidance response for feature-request resume-paused round 6

Human guidance:

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Guidance response:

I applied the quoted comments as binding.

- "Q25 to never be asked ever again": I withdrew my round 5 fallback question,
  which would have asked the person to reconsider part of Q25. The covered
  wording only records that consequence in the Q06 and Q21 answer blocks.
- "One command and it is done": Q27 to Q29 add no question at resume time.
  Q29's recommended question comes at pause time, to protect an unresumed
  checkpoint.
- "If I specify a role, I do not want to have to confirm": Q27 Option B is the
  only place where the person names a role at launch, and the launch
  authorizes that switch under Q24=B.
- The scope limits are respected: this answer requests no consolidation,
  implementation, staging or commit.

### Writer instructions for feature-request resume-paused round 6

No further automated review round is needed for this formulation.

1. Apply the covered wording at the next revision: the Q06 and Q21 notes, the
   sentence for Q27 Option B and the phrase for Q28 Option A. The phrase for
   the pause instruction is optional.
2. Present Q27, Q28 and Q29 to the person for decision. Do not record a
   decision on the strength of my recommendation.
3. When presenting them, also tell the person that after delivery, prompts
   saved without routing, and targets that the handoff cannot identify, are
   skipped and need ordinary `resume-session`. This follows from Q25. If the
   person objects, that is new guidance for a later round, not something to
   apply silently.
4. If Q27=B is chosen, add `--switch-roles` to the command synopsis and the
   acceptance criteria during consolidation.
5. After the decisions, request the fresh independent review that the
   explanation workflow requires. Consolidation stays the person's separate
   choice.

### Final reviewer decision for feature-request resume-paused round 6

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-6 -->

## Round 6 by human - human-confirmation

- Recorded: 2026-11-08T20:49:19+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Revise and review again
Outcome: another-round
Guidance: # Human guidance for the fresh resume-paused review

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

<!-- review-entry-id: human-confirmation-round-6 -->

## Round 7 by requestor

- Recorded: 2026-11-08T20:50:42+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 7)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 7

### Requestor assessment for feature-request resume-paused (round 7)

#### Writer assessment after all 29 decisions for feature-request resume-paused (round 7)

All Q01-Q29 have explicit human decisions. The full scanner reports 29
questions, zero undecided and no diagnostics. Preserve all question blocks,
options, recommendations, explanations and recorded decisions. Consolidation
is not authorized.

Q27=B adds an optional late swap of a saved requestor/reviewer pair using
`--switch-roles NAME[,NAME...]`, with handoff-derived targets and no extra
confirmation. Q28=A carries human launch authorization in a command marker
bound to prompt SHA-256, receiving pane and host, resolved role and exact
reviewer exchange. A mismatch stops without consuming the prompt or claiming
a role and does not fall back to a consent question. Q29=A extends the
pause-time replacement guard to a different recorded pausing pane or saved
session role, including the same host. Legacy prompts retain the host-id
comparison. The user selected these answers after the round 6 convergence.

Review the whole requirement, draft, pause instruction, template and wiki,
including all earlier decisions and user comments. The existing options and
answers appear sufficient; assess consistency and any missing questions
independently. Check command syntax, role switching and later reviewer-only
continuation, marker binding, pause replacement and the distinction between
historical pausing identities and future role assignments.

Q24 and Q25 are settled: one human launch authorizes required author and role
overrides without repeated consent; saved handoff routing determines panes,
validated against live evidence without selection questions or a unique-pane
fallback. Do not reopen those decisions. The saved handoff alone grants no
permissions, and the bulk tool writes no authorization artifact.

The pause instruction/template/wiki changes document capture and replacement
behavior. The bulk command and receiving-workflow marker implementation remain
future prerequisites for design and plans. No implementation, staging, commit
or consolidation is requested. Round 6 covered wording is retained; this is
the required fresh independent review of the newly confirmed decisions.

### Change summary for feature-request resume-paused (round 7)

#### Changes since the round 6 convergence for feature-request resume-paused (round 7)

- Recorded explicit Q27=B, Q28=A and Q29=A decisions, preserving their full
  question history and earlier human decisions.
- Added optional `--switch-roles NAME[,NAME...]` to the command syntax, target
  selection and acceptance criteria. Names match session/checkout folder names
  exactly and case-insensitively. Unmatched names prevent all input; a matched
  checkout without a saved pair gets none and fails the run.
- Required later reviewer-only continuation to match the assignment resolved
  by that invocation. A switched continuation repeats the switch argument;
  mismatch sends no input and is reported.
- Added the target-bound launch marker to the operative command contract and
  criterion 11. Matching proceeds without confirmation; mismatch consumes
  nothing and claims no role. Manual unmarked commands retain existing consent
  behavior; saved routing grants no permissions and no artifact is written.
- Added the Q29 pause-time guard to the requirement, pause instruction and
  wiki. Different recorded pausing pane or saved role triggers the existing
  replacement choice even on the same host. Declining preserves the old
  checkpoint and stops the new pause. Legacy prompts retain host-id comparison;
  one checkpoint per checkout remains and bulk resume gains no question.
- Mirrored the complete question section into its private companion. The
  scanner confirms all 29 decisions with no diagnostics; the four edited
  requirement/capture documents pass Markdown lint. Whitespace checks pass and
  the original staged draft blob is unchanged.

The confirmed round 5 guidance is reused verbatim. These later decisions are
described separately here and in the assessment and response.

### Human guidance and writer response for feature-request resume-paused (round 7)

Human guidance:

#### Human guidance for the fresh resume-paused review for feature-request resume-paused (round 7)

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Writer response:

#### Response following the Q27-Q29 discussion for feature-request resume-paused (round 7)

The human selected Q27=B, Q28=A and Q29=A after all three explanations.
The full scanner now reports zero undecided questions. Please independently
review those decisions, the whole specification, earlier comments and related
pause documentation for consistency and missing requirements.

Q27 resolves late role switches through a named swap of the recorded pair;
it introduces neither pane selection nor repeated confirmation. Q28 resolves
authorization transport with the explicit marker; its exact syntax, parsing
and validation belong in design, plans and receiving-workflow implementation.
Q29 resolves same-host checkpoint replacement at pause time only. Its guard
compares historical pausing identities rather than future assignments. The
existing template already records those identities, so no new field was
needed for this last answer.

The one-command authorization and handoff-only target source remain binding.
Missing/legacy routing is reported without input or an interactive migration
question. Required unreadable/conflicting evidence remains an error. The saved
exact exchange, validated live, resolves the identifiable-exchange condition
even if other exchanges exist. Do not revive the withdrawn fallback question.

Assess substantive gaps through the ordinary automated review loop. At
convergence, retain the answer for the human workflow gate. This request
authorizes no consolidation, code implementation, staging or commits.

### Reviewer focus for feature-request resume-paused (round 7)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-7 -->

## Round 7 by reviewer

- Recorded: 2026-11-08T21:13:30+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 7

I read the whole requirement (SHA-256 `02b29ba9...6fc6`), the draft, and the
working-tree changes to `instructions/pause-session.md`,
`templates/pause-session.template.md` and
`wiki/how-to/pause-and-resume-a-session.md`. The decision scanner reports 29
confirmed decisions and none undecided.

#### Round 6 wording and the three new decisions in place for feature-request resume-paused (round 7)

- The round 6 covered wording is applied: the Q06 and Q21 notes, the sentence
  for Q27 Option B, the phrase for Q28 Option A, and the optional phrase in
  the pause instruction.
- Q27=B, Q28=A and Q29=A are recorded as decided, and their option history is
  kept. The synopsis, target selection, reviewer-only continuation and
  criteria 3, 11 and 12 carry them.
- The requirement, the pause instruction and the wiki state the Q29 guard the
  same way. All three compare historical pausing identities, not intended
  assignments or the Q27 swap.

#### Gaps left by applying Q27 to Q29 for feature-request resume-paused (round 7)

I agree with all three decisions. Applying them left four contract gaps and
three smaller ones. None needs a new human decision: each follows from a
recorded decision, and the requested changes give wording for each.

1. **Codex cannot prove its own pane from its environment.** Q28 has the
   receiving workflow validate the marker against "its current prompt, pane,
   host". The pause instruction now warns that a command run under the shared
   Codex app-server daemon can inherit another session's pane variables. A
   Codex workflow comparing the marker with `TUIOS_PANE_ID` would see the pane
   of whichever session started the daemon. Every other Codex target would
   report a mismatch and stop, so the bulk path would fail for Codex. The
   receiving pane needs the same independent-evidence rule as pause capture.
2. **A marker mismatch has no run outcome.** The result rules fail a target
   that stops on a confirmation question. Under Q28 that question should no
   longer appear, and the authorization path now fails through a marker
   mismatch, which asks nothing. A requestor's mismatch would read as a Q23
   pending takeover, which succeeds. A single-agent target has already shown
   its acceptance evidence, so the run would report RESUME although nothing
   resumed. The requirement also never says how long a single-agent target is
   observed after acceptance. Q23 bounds that wait for takeover only.
3. **The Q27 failures are missing from the exit rules.** The result section
   lists what fails a normal run and a dry run. It omits an unmatched
   `--switch-roles` name and a matched checkout the switch cannot apply to,
   although Q27 makes both prevent input and the second fail the invocation.
   It also leaves Q27's later-run mismatch unclassified, and two existing
   rules point different ways: an already-resuming checkout is an expected
   skip, while contradictory identity evidence is a Q07 error. Classify it by
   the argument:
   - when `--switch-roles` names the checkout, the argument cannot apply, and
     the run fails, as for a checkout without a recorded pair;
   - without the argument, all evidence agrees on who resumed. It is the
     expected already-resuming skip, and its report says that continuing the
     switched pair needs `--switch-roles`.
4. **A switch can match a checkout that neither sentence covers.** The text
   covers a saved requestor pause with a recorded pair, and a matched checkout
   without a recorded pair. A reviewer pause whose handoff records both
   targets fits neither. The decision lets the switch swap only a recorded
   requestor pair, so any other matched checkout gets no input and fails.

Smaller gaps:

5. **The Q29 guard with an unknown pane.** The guard compares recorded pausing
   panes. Codex under the daemon will often record its pane as unknown, and
   the guard does not say whether unknown counts as different. For a missing
   field, the legacy rule falls back to the agent-id comparison. An unknown
   value should be read the same way: alone it is not a difference, and the
   remaining recorded fields are still compared.
6. **What the resumed agent's marker authorizes.** The marker names the
   exchange only for reviewer activation. A switched requestor also needs a
   requestor-role override. The digest fixes the saved prompt, and with it
   the exchange its routing records; the requirement should say the override
   covers only that exchange. For reviewer activation, it should say which
   prompt the digest names: the checkout's pause prompt that the requestor
   consumed, checked against its receipt.
7. **Q29 has no acceptance criterion.** Criterion 14 covers routing capture
   only. The Q29 guard appears in the body and the instruction, but no
   criterion carries it into design and validation.

Polish:

- The Q29 decision line reads `confirmed:` where every other block uses
  `confirmed —`. The scanner accepts both.
- The body says `--switch-roles` matches "checkout folder names". `--except`
  says folder base names.
- The draft's synopsis still lacks `--switch-roles`.

I found no other missing decision, and no conflict with the settled Q24 and
Q25 decisions. None of the changes adds a question at resume time.

### Question verdicts for feature-request resume-paused round 7

All 29 decisions stand as recorded. My answers match them; the remaining
edits apply the decisions and change none.

| Question | Status | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- | --- |
| Q01 to Q05 | Confirmed | Consistent | As decided | None |
| Q06 | Confirmed C, amended by Q25 | Consistent; the round 6 note is applied | As decided | None |
| Q07 to Q20 | Confirmed | Consistent | As decided | None |
| Q21 | Confirmed A | Consistent; the round 6 note is applied | As decided | None |
| Q22 to Q26 | Confirmed | Consistent | As decided | None |
| Q27 | Confirmed B | Agree; two cases have no outcome | As decided | Applicability and later-run note; exit rules |
| Q28 | Confirmed A | Agree; receiving-pane proof, override scope and mismatch outcome missing | As decided | Pane-evidence and scope sentences; mismatch outcome |
| Q29 | Confirmed A | Agree; unknown pane and criterion missing | As decided | Unknown-value sentence; criterion 14; decision-line dash |

#### Why the three new decisions hold for feature-request resume-paused (round 7)

- Q27 B: a role switch decided after the pause gets a one-command path, while
  every pane still comes from the saved handoff, as Q25 requires.
- Q28 A: the authority applies only to the bulk path. It is tied to the prompt
  bytes, the pane and the role that the tool has just rechecked under Q13, and
  commands typed by hand keep today's questions.
- Q29 A: the existing replacement guard now covers the same-LLM layout that
  Q25 supports. Its question comes at pause time, never during the
  one-command resume.

### Requested changes for feature-request resume-paused round 7

Requested changes:

Line numbers refer to the reviewed requirement unless another file is named.
Leave the recorded user decision text unchanged. Where a decision block needs a
consequence, add a dated note beside it, as for Q06 and Q21 in round 6.

#### Receiving pane proof for the Q28 marker for feature-request resume-paused (round 7)

In "Carrying launch authorization into receiving workflows" (lines 73-86),
after the sentence ending "for required author and role overrides.", add:

```md
The receiving workflow establishes its own pane as pause capture does. An
inherited `TUIOS_PANE_ID` alone is not enough, because a command run under
the shared Codex app-server daemon can carry another session's pane
variables. Independent read-only evidence must agree, such as the marked
pane's agent log or screen showing this exact marked command as its latest
input, in the same checkout and agent host. When that evidence is unavailable
or disagrees, treat the marker as mismatched.
```

In criterion 11, after "resolved role and exact reviewer exchange.", add:
"The receiving workflow proves its pane with independent read-only evidence,
not an inherited `TUIOS_PANE_ID` alone."

#### Exchange covered by the resumed agent's marker for feature-request resume-paused (round 7)

In the same subsection, after "resolved intended role and, for reviewer
activation, the exact exchange." (lines 75-76), add:

```md
For the resumed agent's `resume-session`, the digest also fixes the exchange
saved in that prompt's routing, and a required role override covers only that
exchange. For reviewer activation, the digest names the checkout's pause
prompt that the requestor consumed, checked against its receipt.
```

#### Run outcome of a marker mismatch for feature-request resume-paused (round 7)

In the result rules, after "A target that stops on an author, role or routing
confirmation question fails the run, because the one-command contract forbids
that question." (lines 381-383), add:

```md
A target that reports a Q28 marker mismatch also fails the run; for a
requestor, it is not a pending takeover under Q23=A. Design selects how long
a single-agent target is observed after acceptance for these stops, as Q23=A
does for takeover.
```

#### Q27 outcomes in the exit rules for feature-request resume-paused (round 7)

Replace "Classification errors, unmatched exclusions and unconfirmed planned
actions fail. Dry runs fail on classification errors or unmatched exclusions."
(lines 377-379) with:

```md
Classification errors, unmatched exclusions, unmatched `--switch-roles` names,
matched checkouts that the switch cannot apply to, and unconfirmed planned
actions fail. Dry runs fail on classification errors, unmatched exclusions and
the same two `--switch-roles` errors.
```

In the duplicate-resume section (lines 222-225), replace "a mismatch sends no
input and is reported. A continuation of a switched assignment therefore
repeats the switch argument." with:

```md
A mismatch sends no input. When `--switch-roles` names that checkout, the
argument cannot apply and the invocation fails. Without the argument, the
checkout is the expected already-resuming skip, and its report names the
resumed requestor and says that continuing the switched pair needs
`--switch-roles`. A continuation of a switched assignment therefore repeats
the switch argument.
```

In criterion 12 (lines 437-439), replace "otherwise send no input and report
the mismatch" with "otherwise send no input; the mismatch fails the invocation
when `--switch-roles` names the checkout and is an expected skip otherwise".

#### Checkouts the Q27 switch cannot apply to for feature-request resume-paused (round 7)

- In the command contract (lines 66-67), replace "A matched checkout without a
  recorded pair receives no input and makes the invocation fail." with:

  ```md
  A matched checkout that does not hold a saved requestor pause with a
  recorded pair, such as a reviewer or single-agent pause, receives no input
  and makes the invocation fail.
  ```

- In criterion 3 (lines 398-399), replace "a matched checkout without a
  recorded pair receives no input and fails the invocation" with "a matched
  checkout that does not hold a saved requestor pause with a recorded pair
  receives no input and fails the invocation".
- In the Q27 answer block, after its decision-date paragraph, add:

  ```md
  Clarification from the Q27 decision, recorded on 2026-11-08: the switch
  applies only to a saved requestor pause with a recorded pair. Any other
  matched checkout, including a reviewer pause that records both targets, is
  handled as a checkout without a recorded pair. On a later run, a mismatch
  fails the invocation when `--switch-roles` names the checkout and is
  otherwise the expected already-resuming skip.
  ```

#### Unknown pane or role in the Q29 guard for feature-request resume-paused (round 7)

- In the requirement (lines 172-180), after "Legacy prompts without pane or
  role fields retain the host-id comparison.", add: "A pane or role recorded
  as unknown, for the existing checkpoint or the current pause, is not by
  itself a difference; the remaining recorded fields are still compared."
- In `instructions/pause-session.md` (lines 86-87), after "For legacy prompts
  without pane or role fields, retain the agent-id comparison.", add:

  ```md
  A pane or role recorded as unknown, for the existing checkpoint or the
  current pause, is not by itself a difference; compare the remaining
  recorded fields.
  ```

#### Q29 in the acceptance criteria for feature-request resume-paused (round 7)

In criterion 14 (lines 446-453), after "Capture must not contact the
counterpart or launch `resume_paused`.", add:

```md
Extend the pause replacement guard under Q29=A to a different recorded
pausing pane or saved role, at pause time only, with legacy prompts keeping
the agent-id comparison.
```

#### Wording polish for feature-request resume-paused (round 7)

- Line 1653: change `User decision: confirmed: Option A.` to
  `User decision: confirmed — Option A.`, as in the other 28 blocks.
- Lines 63-64: say "session names and checkout folder base names", as the
  `--except` rule does.
- In the draft, after the synopsis block at line 99, add: "Q27=B adds the
  optional `--switch-roles NAME[,NAME...]` argument; the requirement holds the
  current synopsis."

### Human guidance response for feature-request resume-paused round 7

Human guidance:

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Guidance response:

I applied the quoted comments as binding.

- "One command and it is done": no requested change adds a question at
  resume time. The receiving-pane rule and the mismatch outcome make a
  failed authorization visible in the report and the exit status, instead
  of a silent non-resume.
- "If I specify a role, I do not want to have to confirm": a switch named
  with `--switch-roles` still needs no confirmation. A switch argument that
  cannot apply is reported and fails the run, as an unmatched exclusion does,
  without a question.
- "Q25 to never be asked ever again": no change adds a selection or migration
  question. The unknown-value rule for the Q29 guard limits when that
  pause-time question, which the person chose, is asked.
- The scope limits are respected: this answer requests no consolidation,
  implementation, staging or commit.

### Writer instructions for feature-request resume-paused round 7

Another automated review round is needed for the requested changes above.

1. Apply the requested changes to the requirement, the pause instruction and
   the draft. None needs a new human decision: each applies Q27, Q28, Q29, Q10
   or Q23 as recorded.
2. Leave the recorded user decision text unchanged. Put each consequence in a
   dated note beside its decision block, as round 6 did for Q06 and Q21.
3. The later-run mismatch classification follows from Q10 and Q27: an
   argument that cannot apply fails the run, and an already-resuming checkout
   with consistent evidence is an expected skip. If you find it does not
   follow, present it to the person as a question instead of choosing. Do not
   reopen Q24 or Q25, and do not revive the withdrawn fallback question.
4. Mirror the changed question blocks into the private companion. Rerun the
   decision scanner and Markdown lint on the edited files.
5. Then request the next review round. This answer authorizes no
   consolidation, implementation, staging or commit.

### Final reviewer decision for feature-request resume-paused round 7

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-7 -->

## Round 8 by requestor

- Recorded: 2026-11-08T21:19:02+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for feature-request resume-paused (round 8)

Umbrella draft: none
Reviewed specification: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
Review round: 8

### Requestor assessment for feature-request resume-paused (round 8)

#### Writer assessment of the round 7 clarifications for feature-request resume-paused (round 8)

All 29 explicit user decisions remain recorded and unchanged. The scanner
reports zero undecided questions and no diagnostics. No missing human decision
is identified. Existing options and answers remain sufficient; all question
history is preserved and consolidation is unauthorized.

Applied the round 7 substantive requests: independent receiving-pane proof,
marker exchange scope and prompt/receipt binding, marker-mismatch failure and
bounded single-agent observation, switch applicability and exit rules, the
later-run assignment mismatch classification, unknown pane/role comparison,
and Q29 acceptance coverage. Added dated consequence notes beside Q27-Q29.

The later-run classification follows the confirmed outcomes: an explicit
switch that cannot apply fails, while consistent evidence of an already
resumed checkout without a switch is an expected skip. The report names the
resumed requestor and the required switch for continuing that pair. This adds
neither a decision nor a runtime question.

The requirement, draft, pause instruction, template and wiki pass Markdown
lint; whitespace passes. The draft's CRLF format and original staged blob are
preserved. No code, staging, commit or consolidation occurred. Review the
complete scope for consistency and any remaining missing questions.

### Change summary for feature-request resume-paused (round 8)

#### Changes responding to round 7 for feature-request resume-paused (round 8)

- Required independent read-only receiving-pane proof instead of an inherited
  `TUIOS_PANE_ID` alone; unavailable or conflicting proof mismatches the marker.
- Scoped a resumed agent's role override to the exchange fixed by the prompt
  digest and routing. Reviewer activation binds the same pause prompt to the
  requestor's consumption receipt.
- Made reported marker mismatch fail the run rather than count as pending
  takeover. Deferred the bounded single-agent observation interval to design.
- Added both switch errors to normal/dry-run outcomes; restricted applicability
  to saved requestor pauses with a recorded pair, including explicit handling
  of reviewer pauses that happen to record both targets.
- Classified later assignment mismatch by whether the invocation names the
  checkout in `--switch-roles`; explicit inapplicability fails, otherwise it is
  the expected already-resuming skip with actionable reporting.
- Defined unknown pane/role values as insufficient alone to establish a
  difference, comparing remaining recorded fields. Aligned requirement, pause
  instruction and wiki; added the pause guard to acceptance criterion 14.
- Added dated Q27-Q29 clarification notes without changing their user answers.
  Mirrored the full question section to its private companion.
- Clarified folder base-name matching and added the draft's pointer to the
  current switch synopsis while preserving CRLF and the original staged blob.

The round 5 guidance is reused verbatim. Its generated blockquote spacing is
preserved; generated/protocol artifacts are never manually edited.

### Human guidance and writer response for feature-request resume-paused (round 8)

Human guidance:

#### Human guidance for the fresh resume-paused review for feature-request resume-paused (round 8)

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Writer response:

#### Response to round 7 findings for feature-request resume-paused (round 8)

Accepted all seven substantive clarifications and the folder-name and draft
synopsis polish. They apply recorded decisions without adding a human choice,
reopening Q24/Q25, or introducing a confirmation during bulk resume. The
unknown-value rule is reflected in the wiki as well as the requested files.

The Q27 applicability and later-run outcomes now follow the explicit argument:
an inapplicable named switch fails; without it, consistent prior resumption is
an expected skip whose report identifies the resumed requestor and switch
needed for continuation. Dated consequence notes preserve the original human
answer text. All 29 decisions remain confirmed.

Retained the scanner-valid colon in the Q29 decision line. The canonical
`rules/markdown.md` prohibits em dashes in documentation, so the suggested
editorial dash would conflict with that rule. This is formatting only and
changes no decision or behavior; there is no substantive disagreement.

Please assess the whole scope and these corrections independently. Bulk
command and receiving-marker implementation remain future prerequisites.
At convergence retain the answer for the ordinary human workflow gate; no
consolidation, implementation, staging or commit is authorized.

### Reviewer focus for feature-request resume-paused (round 8)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-8 -->

## Round 8 by reviewer

- Recorded: 2026-11-08T21:24:57+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for feature-request resume-paused round 8

I read the whole requirement again (SHA-256 `8f76f325...3c79`). I also read
the guard and routing sections of `instructions/pause-session.md`, the wiki
paragraph on replacing a prompt, and the draft's synopsis pointer. The
decision scanner reports 29 confirmed decisions and none undecided.

#### Round 7 corrections now in place for feature-request resume-paused (round 8)

- **Receiving pane.** The marker subsection and criterion 11 require
  independent read-only evidence of the receiving pane, not an inherited
  `TUIOS_PANE_ID` alone. Unavailable or conflicting evidence counts as a
  mismatch.
- **Override scope.** A resumed agent's role override covers only the exchange
  that the prompt digest and its saved routing fix. For reviewer activation,
  the digest names the pause prompt the requestor consumed, checked against
  its receipt.
- **Mismatch outcome.** A reported marker mismatch fails the run and is never
  a Q23 pending takeover. Design chooses how long a single-agent target is
  observed after acceptance.
- **`--switch-roles` outcomes.** Both switch errors fail normal and dry runs.
  The switch applies only to a saved requestor pause with a recorded pair,
  including the reviewer-pause case. A later-run mismatch fails when the
  argument names the checkout. Without the argument, it is the expected skip,
  and its report says how to continue. Body, criteria 3 and 12, and the Q27
  note agree.
- **Q29 guard.** An unknown pane or role is not by itself a difference, in the
  requirement, the pause instruction and the wiki. Criterion 14 now carries
  the guard.
- **Polish.** Folder base-name matching and the draft's synopsis pointer are
  applied.

The dated notes beside Q27, Q28 and Q29 record consequences without changing
the user's answers, as round 6 did for Q06 and Q21.

#### The writer's disagreement on the Q29 dash for feature-request resume-paused (round 8)

I accept it. `rules/markdown.md` forbids the em dash in documentation text,
and the scanner accepts the colon form. My round 7 polish item was wrong. The
other 28 decision lines need no change now: consolidation removes the
question section.

#### What remains for feature-request resume-paused (round 8)

One optional placement edit. In the pause instruction, the new unknown-value
sentence comes after "Ask as a choice under interactive_menu.md". It belongs
with the other comparison rules, right after the legacy sentence.

I found no missing decision and no contradiction across the requirement, the
draft, the pause instruction, the template and the wiki. No change adds a
question at resume time, and Q24 and Q25 are respected throughout.

### Question verdicts for feature-request resume-paused round 8

All 29 decisions stand as recorded, and my answers match them. No human
decision is outstanding.

| Question | Status | Verdict | My answer | Remaining edit |
| --- | --- | --- | --- | --- |
| Q01 to Q26 | Confirmed | Consistent | As decided | None |
| Q27 | Confirmed B | Consistent; the round 7 note and exit rules are applied | As decided | None |
| Q28 | Confirmed A | Consistent; pane proof, scope and mismatch outcome are applied | As decided | None |
| Q29 | Confirmed A | Consistent; the unknown-value rule and criterion 14 are applied | As decided | Optional sentence placement in the pause instruction |

### Convergence evidence for feature-request resume-paused round 8

Covered wording:

#### Optional placement in the pause instruction for feature-request resume-paused (round 8)

In `instructions/pause-session.md` (lines 86-90), move the sentence "A pane or
role recorded as unknown, for the existing checkpoint or the current pause, is
not by itself a difference; compare the remaining recorded fields." so that it
follows "For legacy prompts without pane or role fields, retain the agent-id
comparison." and comes before "Ask as a choice under interactive_menu.md". The
comparison rules then read together, ahead of the question they lead to:

```md
pausing identities, not intended future role assignments. For legacy prompts
without pane or role fields, retain the agent-id comparison. A pane or role
recorded as unknown, for the existing checkpoint or the current pause, is not
by itself a difference; compare the remaining recorded fields. Ask as a choice
under [interactive_menu.md](../rules/interactive_menu.md). If the user
declines, preserve the existing prompt and stop without writing a new one.
```

Convergence rationale:

No further automated review round is needed for this formulation.

- Every round 7 change is applied in the requirement body, criteria 3, 11, 12
  and 14, the dated Q27 to Q29 notes, the pause instruction, the wiki and the
  draft.
- The writer's one disagreement, keeping the colon in the Q29 decision line,
  follows the repository's no-em-dash rule, and the scanner accepts it.
- All 29 questions have explicit human decisions. The consequence notes apply
  those decisions and change none of them.
- What remains is one optional sentence placement in the pause instruction.

No human decision is outstanding. Consolidation remains the person's separate
choice; this recommendation is advisory and authorizes no consolidation,
implementation, staging or commit.

### Human guidance response for feature-request resume-paused round 8

Human guidance:

The user selected Q20=A, Q21=A, Q22=A, Q23=A and Q24=B, then supplied these
explicit comments, preserved verbatim:

> Q24: seriously, if I specify a role, I do not want to have to confirm: maximum automation is required here

> Do not make myself repeat: a resume pause means: "one command and it is done", not "one command, and I still need to confirm this or that"

For Q25, the user rejected the original pane-selection alternatives:

> No the selection must be done based on what is noted in the pause session handoff, which means you MUST evolve pause instruction to add additional information in the handoff note for Q25 to never be asked ever again: update the docs to achieve this

Q26 was explained with native prefixes and trailing context included in
Option A. The user's explicit answer was:

> A

The explanation workflow and the user's earlier go-ahead authorize this
independent review after the decisions. They do not authorize consolidation,
implementation, staging or commits. The user explicitly authorized the Q25
pause instruction/template/documentation changes.

Guidance response:

I applied the quoted comments as binding.

- "One command and it is done": the revised text adds no question at resume
  time. A failed authorization now shows in the report and the exit status
  instead of passing as success.
- "If I specify a role, I do not want to have to confirm": a switch named
  with `--switch-roles` needs no confirmation. A switch argument that cannot
  apply fails the run without a question.
- "Q25 to never be asked ever again": no selection or migration question is
  added. The only question, at pause time, is the Q29 guard the person chose,
  and the unknown-value rule limits when it fires.
- The scope limits are respected: this answer requests no consolidation,
  implementation, staging or commit.

### Writer instructions for feature-request resume-paused round 8

No further automated review round is needed for this formulation.

1. Optionally apply the covered sentence placement in
   `instructions/pause-session.md` at the next revision.
2. Keep the Q29 decision line's colon, under `rules/markdown.md`.
3. No human decision is outstanding. Present the convergence gate to the
   person. Consolidation is their separate choice.
4. During consolidation, carry the routing, marker and `--switch-roles`
   prerequisites into design, plans and validation, as the requirement
   states. Keep the deferred senv follow-up section.
5. This answer authorizes no consolidation, implementation, staging or
   commit.

### Final reviewer decision for feature-request resume-paused round 8

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-8 -->

## Round 8 by human - human-confirmation

- Recorded: 2026-11-08T21:48:44+01:00
- Exchange: specification/feature-request/v0.14.0/resume-paused
- Umbrella: none
- Reviewed document: docs/v0.14.0/feature-request.v0.14.0.resume-paused.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-8 -->
