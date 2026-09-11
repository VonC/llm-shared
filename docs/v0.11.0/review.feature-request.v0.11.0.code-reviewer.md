# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-14T10:02:34+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for feature-request code-reviewer round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
Review round: 1

### Requestor assessment for feature-request code-reviewer round 1

## Writer assessment for round 1

The feature request defines the independent code-reviewer role, its advisory boundary, exact exchange identity, permitted repair behavior, review artifacts, convergence meaning, escalation boundary, and acceptance criteria.

Five open questions cover the remaining feature-level ambiguities:

1. the boundary between bounded reviewer repairs and work returned to the writer;
2. whether substantive reviewer-authored implementation changes require another automated round;
3. how unrelated staged changes affect a plan-step-scoped review;
4. the minimum evidence required for commit-readiness; and
5. how unavailable mandatory verification transitions from recoverable rework to escalation.

No additional feature-level question is presently known. Each question has three materially distinct options, explicit pros and cons, a recommended answer, and an acceptance reason. The reviewer should identify any missing scope, expected-behavior, acceptance-criteria, or edge-case question and should suggest clearer wording where the current options overlap or leave a behavioral gap.

No reviewer wording suggestions exist yet because this is round 1.

### Change summary for feature-request code-reviewer round 1

## Specification changes for round 1

- Created `docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md` from the canonical focused draft and umbrella context.
- Recorded the user story, current behavior, responder gap, expected behavior, artifact rules, acceptance criteria, dependencies, and ownership boundary.
- Added five open questions through `oqm` covering repair scope, post-repair outcomes, unrelated staged work, readiness evidence, and unavailable verification.

### Writer response for feature-request code-reviewer round 1

Writer response: ## Writer response for round 1

This is the initial specification-review round, so there is no earlier reviewer feedback to accept, reject, or dispute. Please review the feature request and its five open questions for missing feature-level decisions, insufficient option separation, unclear acceptance behavior, and wording that could be made more precise. Do not consolidate the document.

### Reviewer focus for feature-request code-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-14T10:13:41+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for feature-request code-reviewer round 1

The feature request states the code-reviewer role in usable terms: advisory
boundary, exact identity validation before any assessment, bounded repairs,
artifact rules, and a commit-readiness floor meant to carry the same meaning in
every session. The five open questions are well formed. Each carries three
materially distinct options with real consequences, and each recommendation
follows from the umbrella and from the completed `review-exchange-core` and
`code-review-requestor` efforts. I would choose A3, B3, C3, D3, and E3, the same
answers the writer recorded. No question is redundant, and none reaches outside
the selected scope.

Two problems keep this round short of consolidation.

The first is measurability. Three accepted answers turn on a term the document
never defines: "substantive staged implementation change" in Q02, "reliable
attribution" in Q03, and "required" or "mandatory" verification in Q04 and Q05.
Each option's own con line names the judgement call, and none of the answers
supplies the test. Q04 exists to give commit-readiness one stable meaning across
reviewer sessions, so leaving its threshold terms to per-session judgement
undoes the decision it just made. These are answer-body corrections rather than
new questions.

The second is coverage. This reviewer differs from the specification reviewer in
one way that drives several unanswered behaviors: it writes to shared working
state. Four decisions follow from that, and the document asks none of them.

- Acceptance criterion 3 sends the reviewer through `implementation-check`, and
  that workflow writes. It updates the validation plan and, when the final step
  completes a collected effort, marks the matching umbrella status row
  completed. Running it whole would record effort completion before any human
  authorized the commit, and would have the advisory role perform part of the
  writer's owning workflow. The feature request has to state what that check may
  write.
- Q04 requires "acceptable required checks" and Q05 turns on "mandatory"
  evidence, but nothing says where that set comes from. Without a source, one
  session escalates over a missing check that another session never treated as
  mandatory, and E3's escalation trigger cannot be tested.
- Nothing says what becomes of reviewer-authored repairs when a round stops
  without publishing: bounded-wait expiry, abandonment, escalation, or an
  in-session reclaim. The staged tree already carries those repairs at that
  point, and the writer inherits them with no record of who made them.
- Nothing says whether the reviewer stages its repairs, or whether it may stage
  pre-existing unstaged work. Criterion 3 assesses "the staged changes", so an
  unstaged repair would leave a readiness recommendation describing a set that
  does not contain the fix, and Q03's contamination rule depends on who may add
  to the index.

Two smaller corrections are cross-document rather than local. The artifacts
section says the answer and the transcript entry "contain the same substantive
reviewer feedback", while the shared exchange takes the complete answer through
`--content-file` and the substantive summary to append through `--summary-file`:
those are two renderings of one set of findings, not the same bytes. The same
section restates artifact names that `review-exchange-core` already derives from
the exchange identity; repeating the pattern in this document invites drift, so
require agreement with the derived names instead.

Nothing here reopens a settled earlier-phase choice. The scope, dependencies,
and ownership boundary sections are accurate and need no change.

### Question verdicts for feature-request code-reviewer round 1

Verdicts on the five existing questions, then the four decisions the document
does not yet ask.

- **Q01, repair boundary: keep option A3, correct the wording.** The question is
  needed, the three options are materially distinct (report-only, unbounded,
  bounded), and A3 follows from the umbrella's "fix missing work and amend
  `a.commit`" rule combined with the writer's ownership of continuation. My
  answer is A3 for the same reason the writer gives. What is missing is a test
  for "clearly in-scope", which the con line admits. Replacement wording for the
  Q01 answer:

  > Option A3: Accept bounded, clearly in-scope repairs. A repair is in scope
  > when every file it touches is already named by the reviewed plan step or
  > already present in that step's staged set, it introduces no new design
  > decision, and it changes no work belonging to another step or another
  > requirement. Anything else returns to the writer with the reason it crossed
  > the boundary. The reviewer lists every repair it made in its answer, so the
  > writer assesses reviewer-authored work rather than discovering it in the
  > diff.

- **Q02, outcome after reviewer changes: keep option B3, define "substantive".**
  The question is needed and the options are distinct. B3 follows from the
  advisory boundary: the actor that writes code cannot be the actor that finally
  clears it. My answer is B3. The con line concedes that B3 needs a distinction
  the document never draws, and "substantive" cannot stay a judgement call when
  it decides the disposition. Replacement wording for the Q02 answer:

  > Option B3: Accept another round after any substantive staged change. A
  > staged change is substantive when it alters the content of a tracked file
  > other than `a.commit`. Corrections confined to `a.commit`, to ignored root
  > `a.*` caller files, or to the answer and transcript are not substantive.
  > When the reviewer made any substantive change in a round, that round
  > publishes `changes-requested` whatever the reviewer thinks of the result,
  > because the writer owns reassessment and continuation.

  This rule also has to reach the body. The "Expected review behavior and
  boundaries" section and acceptance criteria 4 and 5 do not carry it today, and
  criterion 5 currently reads as though a reviewer that just completed the work
  itself may recommend commit-readiness in the same round.

- **Q03, unrelated staged changes: keep option C3, define "reliable
  attribution".** The question is needed, the options are distinct, and C3
  follows from the exact plan-step identity: expanding the review would make the
  identity untrue, and rejecting outright would stall on harmless content. My
  answer is C3. The undefined term is the one the con line names. Replacement
  wording for the Q03 answer:

  > Option C3: Accept scoped review with explicit contamination reporting.
  > Unrelated staged content is reliably separable when it touches no file named
  > by the reviewed plan step and `a.commit` places it in a commit group
  > distinct from the reviewed step's groups. When either condition fails, the
  > reviewer reports the contamination and withholds commit-readiness, because
  > the commit the human would authorize covers work this review did not
  > assess.

- **Q04, readiness evidence: keep option D3, make the floor countable and name
  its source.** The question is needed, D2 is correctly rejected, and D3 follows
  from the human gate depending on one stable meaning of readiness. My answer is
  D3. Two corrections. First, the six evidence items live inside an option
  bullet, where an acceptance criterion cannot reference them: lift them into
  the body as a numbered readiness floor (exact identity, full plan-step
  implementation, acceptable required checks, staged-diff scope, no unresolved
  findings, accurate `a.commit`) and have criterion 5 require all of them, so
  the criterion becomes testable. Second, "required checks" has no source, which
  is the new Q06 below.

- **Q05, unavailable verification: keep option E3, bound it by the shared
  counter rather than by reviewer feel.** The question is needed and covers a
  real edge case that the shared core does not own. E3 follows from the
  no-progress and disagreement rules already settled in
  `review-exchange-core`. My answer is E3. As written, "plausibly recoverable
  within the shared bounds" leaves the transition to reviewer judgement, and a
  transition that decides escalation has to be observable. Replacement wording
  for the Q05 answer:

  > Option E3: Accept bounded recovery followed by escalation. The reviewer
  > reports the missing evidence and requests rework the first time mandatory
  > evidence is unavailable. It escalates when the same mandatory evidence is
  > still unavailable in the next round, when the writer disputes that the
  > evidence is mandatory, or when the shared no-progress bound is reached.
  > Commit-readiness is never recommended while mandatory evidence is missing or
  > disputed.

Four decisions are missing. Q06 and Q07 block a correct implementation; Q08 and
Q09 are needed for the reviewer to behave the same way twice.

- **Q06: where does the mandatory verification set come from?** Q04 requires
  "acceptable required checks" and Q05 escalates over "mandatory" evidence, yet
  neither says who declares a check mandatory. Options: F1, the reviewed plan
  step declares its own required checks, so review follows the plan and nothing
  else; F2, the project's own validation entry point and its coverage gate
  supply a default set, the plan step or the request may add to it, and neither
  may remove from it; F3, each review request declares its own set.
  Recommended F2, because Q04 already rejected the per-request threshold in D2
  while keeping "the request may add stricter evidence", and F2 is the only
  option consistent with both halves of that answer. F1 leaves a plan step that
  forgot to name its checks with no floor at all.

- **Q07: what may `implementation-check` write when the reviewer runs it?**
  Criterion 3 requires the reviewer to assess the step "through
  `implementation-check`", and that workflow updates the validation plan and
  marks the umbrella status row completed when the final step lands. The
  advisory reviewer must not record effort completion before a human authorizes
  the commit. Options: G1, run it whole, including the umbrella status update;
  G2, apply its criteria read-only and write nothing outside the reviewer's own
  ignored evidence files and the answer; G3, apply its criteria and let
  validation-plan rows for the reviewed step count as an in-scope repair under
  Q01, staged and described in `a.commit`, while the umbrella status table stays
  writer-owned in every case. Recommended G3, because the step's validation
  record is part of the step's deliverable and falls inside the Q01 boundary,
  while the umbrella row asserts that a whole effort is finished, which no
  advisory round and no unauthorized commit can support. G2 is the safe fallback
  if the writer prefers a reviewer that writes no versioned document at all.

- **Q08: what happens to reviewer repairs when a round stops without
  publishing?** Bounded-wait expiry, abandonment, escalation, and in-session
  reclaim all leave the staged tree already carrying reviewer-authored work.
  Options: H1, revert the reviewer's changes before stopping, so the writer
  always resumes from its own tree; H2, leave the working tree and index
  untouched and record every repair, plus the identifier of the staged tree as
  assessed, in an ignored root evidence file that a reclaimed or fresh round
  reuses; H3, leave the changes and require the next request to state whether
  the writer accepted them. Recommended H2, which is the code-family counterpart
  of the retained assessment manifest the specification reviewer already keeps.
  H1 would destroy work nobody asked to destroy and could drop writer edits made
  in parallel. H3 places an obligation on the requestor, which this requirement
  does not own, though the writer may add it to `code-review-requestor` later.

- **Q09: does the reviewer stage its repairs, and may it stage anything else?**
  Criterion 3 assesses "the staged changes", so this decides whether a readiness
  recommendation describes the same set the human would commit. Options: J1, the
  reviewer stages its own repairs and stages nothing else, reporting
  pre-existing unstaged work instead of adding it; J2, the reviewer stages
  whatever it judges in scope for the step, including pre-existing unstaged
  work; J3, the reviewer leaves all staging to the writer and reports its
  repairs as unstaged. Recommended J1. J3 puts criteria 3 and 4 in conflict,
  since the repair would sit outside the assessed set. J2 lets
  the reviewer pull in work the writer deliberately kept out of the index, which
  is the contamination Q03 set out to report rather than create.

### Requested changes for feature-request code-reviewer round 1

Requested changes: The five recorded answers stand as chosen, but three of them rest on undefined
terms and four decisions are missing, so this round requests changes rather than
consolidation.

- Define "substantive staged change" inside the Q02 answer, "reliable
  attribution" inside the Q03 answer, and the escalation trigger inside the Q05
  answer, using the quoted replacement wording.
- Add the in-scope repair test and the repair-disclosure duty to the Q01 answer.
- Move the D3 evidence list into the body as a numbered commit-readiness floor
  and make acceptance criterion 5 require it.
- Add Q06 on the source of the mandatory verification set, Q07 on what
  `implementation-check` may write during a review, Q08 on reviewer repairs left
  behind by a stopped round, and Q09 on staging obligations.
- Carry the accepted rules into "Expected review behavior and boundaries" so
  they do not live only inside answers.
- Correct the artifacts section: answer content and transcript summary are two
  renderings of one set of findings, and artifact names come from the shared
  exchange identity rather than from this requirement.
- Name the reviewer deliverables in acceptance criterion 8 precisely enough to
  check them.

### Writer instructions for feature-request code-reviewer round 1

Apply these changes to
`docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md`, then publish another
automated round. Do not consolidate.

1. Replace the answer bodies of Q02, Q03, and Q05 with the wording quoted in the
   question verdicts, so the substantive-change test, the separability test, and
   the escalation trigger stop depending on per-session judgement. Keep the
   selected options B3, C3, and E3 unchanged.
2. Replace the Q01 answer body with the quoted wording, which states the
   in-scope test and adds the obligation to list every reviewer repair in the
   answer. Keep option A3.
3. Lift the six D3 evidence items into the body as a numbered commit-readiness
   floor, and rewrite acceptance criterion 5 to require every applicable item of
   that floor. An acceptance criterion cannot reference an item that only exists
   inside an option bullet.
4. Add four open questions through `oqm`, following the existing BBQ, options,
   recommendation, and answer shape: Q06 on the source of the mandatory
   verification set (recommended F2), Q07 on what `implementation-check` may
   write during a review (recommended G3), Q08 on the fate of reviewer repairs
   when a round stops without publishing (recommended H2), and Q09 on staging
   obligations (recommended J1). The verdict file carries the description,
   three options, and recommendation argument for each.
5. Add these bullets to "Expected review behavior and boundaries", so the
   accepted answers are visible outside the question section: a substantive
   reviewer repair forces an intermediate outcome in that same round; reviewer
   repairs are staged and listed in the answer; `implementation-check` never
   writes the umbrella status table during a review; and a round that stops
   without publishing leaves the index untouched and records its repairs as
   caller-owned evidence.
6. Correct the artifacts section on two points. State that the answer carries
   the complete findings and the transcript entry carries the paired substantive
   summary of the same findings, rather than "the same substantive reviewer
   feedback", which reads as identical bytes. State that the request, answer,
   and transcript names are derived by `review-exchange-core` from the exchange
   identity and must agree with it, instead of restating the file-name patterns
   this requirement does not own.
7. Name the deliverables in acceptance criterion 8 the way the completed
   efforts named theirs: the canonical shared instruction, the LLM-specific
   wrapper, the answer template beside the existing request template, and the
   answer-generation launcher that matches the existing `bin/code_review_request`
   entry point. A criterion that says "a generation script" cannot be checked.

Round 2 can converge if these edits land and the four new questions carry the
same option quality as the current five. Nothing in this feedback asks for a new
capability: every item either measures a decision already taken or asks for a
decision the current text assumes without making it.

### Final reviewer decision for feature-request code-reviewer round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-14T11:43:23+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for feature-request code-reviewer round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
Review round: 2

### Requestor assessment for feature-request code-reviewer round 2

## Writer assessment for round 2

All round-1 requested changes were applied without disagreement. The nine open questions now cover the known feature-level decisions for repair scope, substantive reviewer changes, staged contamination, readiness evidence, unavailable verification, mandatory-check authority, `implementation-check` write boundaries, interrupted-round repair evidence, and reviewer staging authority.

The existing choices A3, B3, C3, D3, and E3 remain selected. Their measurable terms are now explicit in the answer bodies and requirement body. New questions Q06 through Q09 each contain three materially distinct options with pros and cons, a recommendation, and an answered acceptance reason.

No additional feature-level question is presently known. The reviewer should verify that the new questions close the identified gaps, that the body and acceptance criteria faithfully carry the selected behavior, and that no remaining wording permits two conforming reviewer sessions to reach opposite outcomes from the same evidence.

All round-1 wording suggestions were applied or represented with equivalent wording. No suggestion was rejected.

### Change summary for feature-request code-reviewer round 2

## Specification changes since round 1

- Defined the Q01 in-scope repair test and required every reviewer repair to be listed in the answer.
- Defined substantive staged changes in Q02, reliable separation in Q03, and the observable escalation trigger in Q05.
- Added a six-item commit-readiness evidence floor and named the project's validation entry point and coverage gate as the mandatory default set.
- Added Q06 through Q09 for verification authority, `implementation-check` write boundaries, interrupted-round repair evidence, and reviewer staging authority.
- Carried reviewer repair, staging, intermediate-outcome, validation-plan, umbrella-status, and stopped-round evidence rules into the requirement body.
- Corrected the answer/transcript rendering relationship and delegated protocol artifact naming to `review-exchange-core`.
- Made acceptance criterion 8 name the canonical instruction, LLM-specific wrapper, answer template, and matching answer-generation launcher.

### Writer response for feature-request code-reviewer round 2

Writer response: ## Writer response to round 1

The writer accepts every round-1 finding and requested change without disagreement. The requirement and open questions now include the supplied measurable definitions, four missing decisions, cross-document artifact corrections, readiness floor, write boundaries, staging rules, retained repair evidence, and precise responder deliverables.

Please review the amended feature request as round 2. Confirm whether Q06 through Q09 are complete and materially distinct, whether the carried body rules match their recommended answers, and whether the specification is ready for consolidation. Do not consolidate it; any convergence recommendation remains advisory and requires the requestor's human confirmation gate.

### Reviewer focus for feature-request code-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-14T16:39:03+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for feature-request code-reviewer round 2

All seven round-1 requested changes landed, and none was applied partially
except the one noted below. The four added questions are well formed: three
materially distinct options each, honest cons, and recommendations that follow
from the answers already accepted. F2, G3, H2, and J1 are the answers I would
choose, for the reasons the document now gives. The commit-readiness floor, the
write boundary around `implementation-check`, the stopped-round evidence rule,
and the staging rule now appear in the requirement body, so the accepted
behavior no longer lives only inside answer text.

No question is missing. The remaining work is one edit pass on six points, four
of which are the defect class this review flagged in round 1: a term that
decides an outcome but carries no test, so two conforming sessions can differ on
the same evidence.

One point is a conflict between two accepted answers rather than a loose term.
Q02 defines a substantive change as any alteration of a tracked file other than
`a.commit`, and Q07 through option G3 lets the reviewer update validation-plan
rows for the reviewed step. The validation plan is a tracked file, so recording
step validation evidence is substantive, and every review that records it must
publish `changes-requested`. A clean review then costs a guaranteed extra round:
round N writes the validation rows and cannot converge, round N+1 finds them
already written, changes nothing, and converges. The document has to say which
behavior it wants. My recommendation is to exempt validation-plan rows for the
reviewed step from the substantive test inside the Q02 answer, on the same
reasoning that already exempts `a.commit`: those rows record the review's own
findings rather than implementation behavior. If the writer prefers the extra
round, Q02 has to say so, so the loop is deliberate instead of accidental.

Three terms still decide outcomes without a test. Floor item 3 requires every
mandatory command to complete "acceptably" without saying what acceptable means,
while Q06 already names a coverage gate that supplies the pass condition. Floor
item 5 forbids "unresolved reviewer findings" without saying whose findings or
from which round, in a role that never rereads the transcript and therefore
cannot see a prior round's findings unless the request carries them. Q08 and the
body require the reviewer to record the "assessed staged-tree identity" without
saying what computes it, which is the one piece of retained evidence a later
round has to compare against.

One round-1 correction reached a single section out of three. The artifacts
section now separates the complete answer content from the paired transcript
summary, but gap item 5 and acceptance criterion 6 still say the reviewer
appends "the same feedback" to the transcript. Criterion 6 is the testable
statement, so it is the one that has to change.

Last, criterion 2 rejects a request whose umbrella, plan, step, or round
disagrees with the exchange identity. That does not cover a step identifier that
is internally consistent but absent from the plan document. Such a request
passes the gate, and the reviewer then assesses a named step that does not
exist. One added clause closes it.

Nothing here reopens a settled choice, and none of these points needs a new
question. The selected options A3, B3, C3, D3, E3, F2, G3, H2, and J1 all stand.

### Question verdicts for feature-request code-reviewer round 2

Verdicts on the nine questions, then the six corrections this round asks for.
Every selected option stands; no question is missing, redundant, unclear, or
outside the selected scope.

- **Q01, repair boundary: A3 confirmed.** The replacement wording landed intact.
  The in-scope test is now checkable from the plan step and the staged set, and
  the duty to list every repair is present in the answer, the body, and
  acceptance criterion 4. No further change.

- **Q02, outcome after reviewer changes: B3 confirmed, one exemption to
  settle.** The substantive test is now measurable. Its interaction with Q07 is
  not: the validation plan is a tracked file other than `a.commit`, so a
  step-level validation-plan update, which G3 explicitly permits as an in-scope
  repair, is substantive and forces `changes-requested`. Every review that
  records its own validation evidence then spends an extra round doing nothing.
  Suggested addition to the Q02 answer:

  > Validation-plan rows for the reviewed step are not substantive when the
  > reviewer writes them to record the result of its own `implementation-check`
  > pass, for the same reason `a.commit` is not substantive: they describe the
  > review, not the implementation. Any other change to a tracked file remains
  > substantive.

  If the writer prefers the extra round instead, say so in the Q02 answer with
  its reason, so the loop is a decision rather than a side effect.

- **Q03, unrelated staged changes: C3 confirmed.** The separability test landed
  and reads the same way for any session. No further change.

- **Q04, readiness evidence: D3 confirmed, two floor items still soft.** The
  six-item floor is now in the body where criterion 5 can reference it, which
  was the round-1 request. Two items are not yet testable. Suggested wording:

  > 3/ Every mandatory validation command completes with a passing result under
  > the project's own gate, including its coverage threshold.
  >
  > 5/ No finding raised in this round, and no finding carried into the current
  > request, remains unresolved.

  Item 5 matters more than it looks: the transcript is not reread as working
  context, so a finding from an earlier round exists for the reviewer only if
  the request carries it. Without that clause the item is either unverifiable or
  an implicit instruction to reread the transcript, which the artifacts section
  forbids.

- **Q05, unavailable verification: E3 confirmed.** The escalation trigger is now
  observable: same mandatory evidence missing in the next round, writer dispute,
  or the shared no-progress bound. No further change.

- **Q06, source of the mandatory set: F2 confirmed.** This is the answer I
  recommended and the reasoning is correct: additive plan or request evidence,
  no removal of project defaults. The floor item 3 wording above is what makes
  F2 usable, since the coverage gate it names is exactly the pass condition
  item 3 leaves unstated.

- **Q07, `implementation-check` write boundary: G3 confirmed.** Options are
  distinct, the pro and con lines are honest, and criterion 3 carries the
  umbrella-table prohibition. The only open point is the Q02 exemption above,
  without which G3's permitted repair always costs a round.

- **Q08, repairs left by a stopped round: H2 confirmed, one term to pin.** The
  no-rollback rule is right and the provenance requirement is right. "Assessed
  staged-tree identity" is the piece a later round compares against, so it needs
  a computable definition. Suggested wording for the answer and the matching
  body bullet:

  > The assessed staged-tree identity is the Git tree object of the index at the
  > moment the reviewer completed its assessment, recorded together with the
  > list of reviewer repairs.

  With that, a reclaimed or fresh round can tell in one comparison whether the
  retained evidence still describes the current index, which is what makes H2
  deterministic rather than descriptive.

- **Q09, staging authority: J1 confirmed.** The reviewed set and the proposed
  commit set now coincide, and pre-existing unstaged work stays with the writer.
  No further change.

Two corrections sit outside the questions.

- **Carry the round-1 answer and transcript correction into the two places it
  missed.** The artifacts section is now right, but gap item 5 still reads
  "append the same feedback to the versioned sibling transcript" and acceptance
  criterion 6 still reads "appends the same feedback to the sibling versioned
  transcript". Criterion 6 is what an implementation is checked against.
  Suggested criterion 6:

  > Publishing an answer appends the paired substantive summary of the same
  > findings to the sibling versioned transcript, and removes the consumed
  > request only after the answer is ready.

- **Close the step-resolution hole in criterion 2.** A request can be internally
  consistent and still name a step the plan does not define. As written,
  criterion 2 only rejects disagreement with the exchange identity, so that
  request passes and the reviewer assesses a step that does not exist.
  Suggested criterion 2:

  > A request whose umbrella, plan, step, or round disagrees with its exchange
  > identity, or whose step identifier is not defined by the referenced plan, is
  > rejected without reviewing or mutating the staged implementation.

Two wording nits, worth taking while the file is open. Expected-behavior line 4
says the reviewer "follows `implementation-check`", which reads as option G1;
say "applies the `implementation-check` criteria" as criterion 3 already does.
The next bullet mixes moods, "may repair it within the named step, stages only
its own repairs"; make the verbs agree.

### Requested changes for feature-request code-reviewer round 2

Requested changes: Round 2 applied every round-1 change and the four added questions are sound, so
the nine answers all stand. Six edits remain, three of which decide behavior, so
this round requests changes rather than consolidation.

- Settle the Q02 and Q07 interaction: a validation-plan row for the reviewed
  step is currently substantive under Q02, so option G3's permitted repair
  forces an extra round on every clean review. Exempt it in the Q02 answer, or
  state that the extra round is intended.
- Give commit-readiness floor item 3 a pass condition (the project's gate,
  including its coverage threshold) and floor item 5 a scope (findings from this
  round and from the current request).
- Define the assessed staged-tree identity as the Git tree object of the index
  at the end of the assessment, in the Q08 answer and the matching body bullet.
- Rewrite acceptance criterion 6 and gap item 5 with the paired-summary wording
  the artifacts section already uses.
- Reject a request whose step identifier is not defined by the referenced plan,
  in acceptance criterion 2.
- Two wording nits: "applies the `implementation-check` criteria" in the
  expected-behavior list, and consistent verb mood in the repair bullet.

### Writer instructions for feature-request code-reviewer round 2

Apply these six changes to
`docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md`, then publish round 3.
Do not consolidate. No new question is needed and no selected option changes.

1. Settle the Q02 and Q07 interaction inside the Q02 answer. Either add the
   quoted exemption for validation-plan rows the reviewer writes for the
   reviewed step, or state that recording them deliberately costs another round
   and why. Leaving it implicit makes every clean review spend one empty round.
2. Replace commit-readiness floor items 3 and 5 with the quoted wording, so
   "acceptably" becomes the project's gate result and the unresolved-finding
   rule names findings from this round and from the current request only. The
   second half matters because the transcript is not reread as working context.
3. Define the assessed staged-tree identity as the Git tree object of the index
   at the end of the assessment, in the Q08 answer and in the matching
   "Expected review behavior and boundaries" bullet.
4. Rewrite acceptance criterion 6 and gap item 5 with the paired-summary
   wording. The artifacts section already carries the round-1 correction; these
   two kept the old "same feedback" phrasing, and criterion 6 is the statement
   an implementation is checked against.
5. Add the step-resolution clause to acceptance criterion 2, so a request naming
   a step the plan does not define is rejected at the same gate as an identity
   mismatch.
6. Take the two wording nits: "applies the `implementation-check` criteria"
   instead of "follows `implementation-check`" in the expected-behavior list,
   and consistent verb mood in the repair bullet.

Items 1 to 3 change behavior an implementation would otherwise guess at. Items 4
to 6 are corrections and polish. With these applied, the specification is ready
for a convergence recommendation in round 3: the nine questions cover the
feature-level decisions, every selected option is sound, and the body and
acceptance criteria carry the accepted behavior faithfully everywhere except the
places listed above.

### Final reviewer decision for feature-request code-reviewer round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-14T16:56:07+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for feature-request code-reviewer round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
Review round: 3

### Requestor assessment for feature-request code-reviewer round 3

## Writer assessment for round 3

All round-2 requested changes were applied without disagreement. The nine selected answers remain A3, B3, C3, D3, E3, F2, G3, H2, and J1, and no new question was added.

The Q02 substantive-change rule now exempts reviewed-step validation rows written solely to record the reviewer's own `implementation-check` result, both in the answer and the requirement body. This resolves the Q02 and Q07 conflict without forcing an empty review round.

The readiness floor now defines the project gate and coverage threshold as the pass condition and limits unresolved findings to the current round or findings carried into the current request. The stopped-round rule defines the assessed staged-tree identity as the Git tree object of the index at assessment completion. The gap and acceptance criteria use paired answer-content and transcript-summary wording, the identity gate rejects steps absent from the referenced plan, and the two wording corrections are applied.

No additional feature-level ambiguity is presently known. The reviewer should verify that the six corrections are complete and internally consistent and determine whether the specification is ready for a convergence recommendation.

### Change summary for feature-request code-reviewer round 3

## Specification changes since round 2

- Exempted reviewed-step validation rows that record the reviewer's own `implementation-check` result from the Q02 substantive-change rule, in both the answer and requirement body.
- Defined readiness floor item 3 by the project's passing gate and coverage threshold.
- Scoped readiness floor item 5 to findings raised in the current round or carried into the current request.
- Defined the assessed staged-tree identity as the Git tree object of the index at assessment completion in Q08 and the matching body rule.
- Replaced the remaining same-feedback wording with complete answer content and its paired substantive transcript summary.
- Rejected step identifiers absent from the referenced plan and corrected the `implementation-check` and repair-bullet wording.

### Writer response for feature-request code-reviewer round 3

Writer response: ## Writer response to round 2

The writer accepts all round-2 findings and applies all six requested corrections without disagreement. The recommended Q02 exemption was chosen because reviewed-step validation rows describe the review result rather than implementation behavior, matching the existing `a.commit` exemption and avoiding a guaranteed empty round.

Please review the amended feature request as round 3 and determine whether the nine questions, answers, requirement body, and acceptance criteria are ready for consolidation. Do not consolidate the document. Any convergence recommendation remains advisory and must enter the requestor's human confirmation gate.

### Reviewer focus for feature-request code-reviewer round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-14T17:12:54+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for feature-request code-reviewer round 3

All six round-2 corrections landed, and each one landed where it was asked for
rather than in a paraphrase.

- The Q02 answer now exempts reviewed-step validation rows written to record the
  reviewer's own `implementation-check` result, with the reason that matches the
  existing `a.commit` exemption. This closes the conflict with option G3, so a
  clean review no longer spends a guaranteed empty round.
- Floor item 3 names the project gate and its coverage threshold as the pass
  condition, and floor item 5 limits unresolved findings to this round and to
  findings the current request carries. Both are now checkable by a reviewer
  that never rereads the transcript.
- The assessed staged-tree identity is defined as the Git tree object of the
  index at assessment completion, in the Q08 answer and in the matching body
  rule, so retained evidence can be compared in one operation.
- Gap item 5 and acceptance criterion 6 both carry the paired answer-content and
  transcript-summary wording, matching the artifacts section.
- Acceptance criterion 2 rejects a step identifier the referenced plan does not
  define, at the same gate as an identity mismatch.
- Both wording corrections are applied, and gap item 3 picked up the same
  `implementation-check` criteria phrasing without being asked.

Every in-scope decision is settled. The nine questions cover the feature-level
choices: repair boundary, outcome after reviewer changes, staged contamination,
readiness evidence, unavailable verification, the source of the mandatory set,
the `implementation-check` write boundary, stopped-round evidence, and staging
authority. A3, B3, C3, D3, E3, F2, G3, H2, and J1 are the answers I would
choose, each option set is materially distinct, and the requirement body and
acceptance criteria now carry the selected behavior rather than leaving it
inside answer text. No question is missing, redundant, unclear, or outside the
selected scope. I found no remaining wording that lets two conforming reviewer
sessions reach opposite outcomes from the same evidence.

Three wording-only edits remain, listed in the covered wording. None changes
behavior and none needs another automated round: the sentence structure of one
body rule, one leftover literal artifact name in the current-behavior section,
and a missing pointer from the Q04 answer to the floor it accepts.

One observation for the design phase rather than for this requirement. The
human may override convergence with `Rework and review again` plus guidance, and
that guidance reaches the reviewer inside the replacement request. This
requirement already directs review against the request, so the guidance is not
lost, but it never states the boundary: guidance informs the assessment and
cannot override identity, the current staged state, or the reviewed step's
scope, and the answer should show how it was addressed. That boundary belongs in
the canonical `code-reviewer` instruction required by acceptance criterion 8,
which is design and plan territory. It does not block consolidation.

This is a convergence recommendation and nothing more. It is advisory, it
authorizes no consolidation, and the choice between `Consolidate` and `Revise
and review again` stays with the human at the requestor's gate.

### Question verdicts for feature-request code-reviewer round 3

Nine questions, nine confirmed answers. None is missing, redundant, unclear, or
outside the selected scope, and no answer needs a substantive change.

- **Q01, repair boundary: A3.** The in-scope test reads off the plan step and
  the staged set, so a second session applies it the same way. The duty to list
  every repair appears in the answer, the body, and acceptance criterion 4. My
  answer is A3, for the reason the document gives.
- **Q02, outcome after reviewer changes: B3.** The substantive test is
  measurable and its exemption list is now complete: `a.commit`, reviewed-step
  validation rows recording the reviewer's own check result, ignored root `a.*`
  files, and the answer and transcript. The exemption reason is the right one:
  those rows describe the review, not the implementation. My answer is B3.
- **Q03, unrelated staged changes: C3.** Separability has two conditions that
  can both be evaluated against the index and `a.commit`, and the consequence,
  withholding commit-readiness, is stated. My answer is C3.
- **Q04, readiness evidence: D3.** The floor is now six numbered items in the
  body where acceptance criterion 5 can require them, and each item states a
  pass condition. My answer is D3. One pointer is missing, noted in the covered
  wording: the answer never sends the reader to the floor it accepts.
- **Q05, unavailable verification: E3.** The escalation trigger is observable
  from three facts: the same mandatory evidence missing in the next round, a
  writer dispute, or the shared no-progress bound. My answer is E3.
- **Q06, source of the mandatory set: F2.** Project defaults that additions may
  extend and nobody may shrink. This is the only option consistent with Q04's
  rejection of a per-request threshold, and it supplies the pass condition floor
  item 3 now uses. My answer is F2.
- **Q07, `implementation-check` write boundary: G3.** Step-level validation rows
  are permitted as an in-scope repair, the umbrella status table is forbidden
  during review, and acceptance criterion 3 carries the prohibition. With the
  Q02 exemption in place, G3's permitted repair no longer costs a round. My
  answer is G3.
- **Q08, repairs left by a stopped round: H2.** No rollback, full provenance,
  and an identity for the assessed index that a later round can compare in one
  operation. My answer is H2.
- **Q09, staging authority: J1.** The reviewed set and the set presented for
  commit authorization coincide, and pre-existing unstaged work stays with the
  writer. My answer is J1.

Cross-checks that hold in the current text: acceptance criterion 5 and Q02 agree
on what blocks convergence; Q07 and Q02 no longer contradict each other; floor
item 3 and Q06 name the same gate; floor item 5 and the append-only transcript
rule agree on which findings the reviewer can see; Q09 and Q08 agree on what the
index contains when a round stops; and gap item 5, the artifacts section, and
acceptance criterion 6 now describe the answer and transcript summary the same
way.

### Convergence evidence for feature-request code-reviewer round 3

Covered wording: Three wording-only edits remain. None changes behavior, and all three can be
applied during consolidation.

- The substantive-change rule in "Expected review behavior and boundaries" packs
  its exception inside the noun phrase, so "a change to a tracked file other
  than `a.commit` or reviewed-step validation rows that record ..." can be read
  with the exception attached to the wrong clause. The Q02 answer is
  unambiguous; the body rule should read the same way. Suggested replacement:

  > A reviewer-authored change to any tracked file is substantive, except
  > `a.commit` and reviewed-step validation rows that record the reviewer's own
  > `implementation-check` result. A substantive change forces a
  > `changes-requested` intermediate outcome in that same round.

- The second bullet of "Current behavior in v0.11.0" still spells out a literal
  request file name, while the artifacts section now states that
  `review-exchange-core` derives request, answer, and transcript names from the
  exchange identity. Suggested replacement:

  > The implementation requestor can publish the derived code-family request
  > artifact with the umbrella, exact plan, implementation step, and review
  > round.

- The Q04 answer accepts a comprehensive evidence floor without pointing at it,
  so a reader who starts from the question never reaches the six items.
  Suggested addition at the end of that answer:

  > The required items are listed in the commit-readiness evidence floor.

Convergence rationale: The three review rounds closed everything they opened. Round 1 found five sound
questions resting on undefined terms and four missing decisions. Round 2 applied
every requested change, added Q06 through Q09, and left one conflict between two
accepted answers plus three soft terms. Round 3 resolved the conflict with the
exemption that matches the existing `a.commit` reasoning, and gave every
remaining term a test.

Convergence is warranted because the three conditions this review has been
measuring are met. Every feature-level decision is answered, and each answer
names the observable fact that decides it rather than leaving it to reviewer
judgement. The requirement body and the eight acceptance criteria carry the
selected behavior, so an implementation can be checked against the document
instead of against the question section. The cross-checks between answers hold:
Q02 against Q07, Q04 against Q06, floor item 5 against the append-only
transcript rule, and Q09 against Q08.

What remains is three sentences of polish that change no behavior, which is the
convergence threshold this exchange set at round 1.

This recommendation is advisory. It does not consolidate the specification, does
not authorize consolidation, and does not settle the choice between
`Consolidate` and `Revise and review again`. That choice belongs to the human at
the requestor's confirmation gate, with the option to override this
recommendation and add guidance for another round.

### Writer instructions for feature-request code-reviewer round 3

Do not consolidate on this answer. This is a convergence recommendation, it is
advisory, and consolidation stays behind the human confirmation gate.

1. Take the three wording edits in the covered wording. They change no behavior,
   so they can be applied during consolidation rather than in another review
   round.
2. Present the human with the identity, this recommendation, the current
   specification, and your own assessment, then offer `Consolidate` or `Revise
   and review again`. If the human overrides with guidance, the replacement
   request should carry that guidance so the next round can address it.
3. Carry one observation into the design and plan phase rather than into this
   requirement: the canonical `code-reviewer` instruction required by acceptance
   criterion 8 should state how the reviewer treats human guidance arriving in a
   post-override request. Guidance informs the assessment and cannot override
   the exchange identity, the current staged state, or the reviewed step's
   scope, and the answer should show how it was addressed. The requirement
   already directs review against the request, so the guidance is not lost and
   this is not a specification gap.
4. Nothing else is outstanding. All nine answers stand as selected, and no
   question needs to be added, split, or removed.

### Final reviewer decision for feature-request code-reviewer round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human

- Recorded: 2026-08-14T17:35:47+02:00
- Exchange: specification/feature-request/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/feature-request.v0.11.0.code-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
