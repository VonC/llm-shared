# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-14T17:55:46+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for design-specification code-reviewer round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
Review round: 1

### Requestor assessment for design-specification code-reviewer round 1

## Writer assessment for design round 1

The design carries the consolidated code-reviewer requirement into an independent responder architecture. It covers exact routing, shared exchange orchestration, staged-state validation, bounded repair ownership, reviewer-safe `implementation-check`, mandatory validation, readiness classification, paired answer production, human guidance, and stopped-round recovery.

Seven design questions cover the remaining architectural choices:

1. request-time staged snapshot authority;
2. reviewer-authored delta isolation and staging;
3. enforcement of the `implementation-check` write boundary;
4. mandatory validation-set resolution;
5. retained evidence manifest identity and lifecycle;
6. shared versus specialized answer-renderer composition; and
7. the authoritative `a.commit` parser and validator interface.

No additional design-level question is presently known. Each question has three materially distinct options, explicit pros and cons, a recommended answer, and an acceptance reason. The reviewer should identify any missing structural, data-flow, interface, trust-boundary, or recovery decision without reopening the settled feature behavior or descending into file-by-file implementation planning.

No reviewer wording suggestions exist yet because this is design review round 1.

### Change summary for design-specification code-reviewer round 1

## Design changes for round 1

- Created `docs/v0.11.0/design.v0.11.0.code-reviewer.md` beside the settled requirement.
- Defined the responder's routing, authority boundary, assessment flow, repair model, validation floor, paired answer, guidance handling, and recovery evidence.
- Recorded confirmed facts from the existing review exchange, code-review requestor, specification reviewer, workflow routing, and currently absent code-reviewer surfaces.
- Added seven design questions through `oqm` for the unresolved architectural contracts.

### Writer response for design-specification code-reviewer round 1

Writer response: ## Writer response for design round 1

This is the initial design-review round, so there is no earlier reviewer feedback to accept, reject, or dispute. Please review the full current design and its seven questions for missing design choices, weak interface boundaries, inconsistent state flow, insufficient recovery evidence, or recommendations that conflict with the settled requirement and existing review architecture. Do not consolidate the design.

### Reviewer focus for design-specification code-reviewer round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-14T19:30:31+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification code-reviewer round 1

The design carries the consolidated requirement faithfully. Routing, the allowed
operation list, the baseline and repair model, the readiness classifier, the
paired renderer, the guidance boundary, and the recovery evidence all match the
nine settled answers, and the acceptance-case table is the strongest part of the
document: twelve scenarios, each with the outcome and the reason. The seven
questions are the right seven areas, each with three materially distinct options
and honest cons. I would choose A2, B2, C2, D3, E1, F2, and G3, the same
recommendations the writer recorded.

Four problems keep this round short of consolidation. Three are collisions
between decisions that are individually sound, and one is a decision the design
does not make at all.

The largest is a scope contradiction. Option A2 puts the request-time Git index
tree inside the request, and option D3 embeds the resolved mandatory validation
set inside the request. Both are requestor-side payload changes to
`tools/code_review_request.py`, its template, and the `code-review-requestor`
instruction, all completed surfaces that this design lists under confirmed facts
rather than under its own scope. The in-scope list covers reviewer surfaces
only. As written, the plan phase inherits two changes with no stated owner. The
design should name the request-payload extension as in-scope for this effort and
list the two fields it adds, or drop back to options that need no requestor
change. My recommendation is to keep A2 and D3 and widen the scope statement,
because the value of both options is exactly the shared request evidence.

The second is a state-flow collision between A2 and the recovery section. The
A2 gate rejects assessment when the live index differs from the request-time
tree. The reviewer stages its own repairs during the round under B2 and J1, so
the index no longer matches that tree. The recovery section then says a
reclaimed round compares the retained assessed tree with the current index,
which is right, but nothing says the A2 gate does not run again. An implementer
following both sections applies the request-time gate on the reclaimed round and
rejects every reclaim it was supposed to support. The design has to state that
the request-time gate runs once, at the start of a fresh assessment, and that
the retained assessed tree governs afterwards.

The third is that A2 has no outcome. "Reject assessment when the live index
differs" names no state, and the reviewer cannot cancel, continue, or consume.
Leaving the round pending burns the lease and produces the abandoned state this
exchange already handles badly. The natural outcome is a published
`changes-requested` carrying both tree identities, which returns control to the
writer through the path that already exists.

The fourth is the decision the design does not make: what happens when running
the mandatory validation set changes the tree. Coverage runs, formatters, and
generated reports write files. Under the substantive-change rule any resulting
change to a tracked file is substantive and forces another round, and under the
stopped-round rule the tree must be left untouched. Neither rule was written
with validation side effects in mind, and the design never separates them. This
needs a question of its own.

Three interface claims also need evidence or a mechanism. Option C2 calls a
reviewer mode an "enforceable interface contract", but `implementation-check` is
a prompt instruction, so a mode flag is still convention: enforcement needs a
machine post-condition. Option B2 requires a reviewer-only patch, but the
baseline the design captures is the index tree plus a list of overlapping paths,
and a patch cannot be derived from path names. Option G3 names a shared parser
and validation API; the parser exists, the validator does not.

### Question verdicts for design-specification code-reviewer round 1

Verdicts on the seven design questions, then the decision the design does not
make. Every recommended option is the one I would choose; the changes below are
about what each option still leaves undefined.

- **Q01, authoritative snapshot: keep A2, three additions.** One round should
  describe one staged tree, and A2 is the only option that keeps the round
  identity and the reviewed snapshot immutable together. A3's second
  contamination decision would collide with the settled Q03 staged-scope rule.
  What A2 still needs:

  1. A scope statement. The request-time tree is produced by the requestor, so
     `tools/code_review_request.py`, its template, and the requestor instruction
     gain a field. The design lists those as confirmed facts, not as its own
     scope.
  2. A gate lifetime. Add to the answer and to the assessment-context section:

     > The request-time gate runs once, before the fresh assessment begins.
     > Once the reviewer stages its own repairs, the retained assessed index
     > tree is the only snapshot a reclaimed or resumed round compares against.

  3. An outcome. Replace "reject assessment when the live index differs" with a
     disposition the reviewer can actually produce:

     > When the live index tree differs from the request-time tree, the reviewer
     > publishes `changes-requested` naming both tree objects and the paths that
     > differ, because the reviewer cannot cancel or replace a round and a
     > pending round left unpublished expires into the abandoned state.

  Also state what a request without the field means. Requiring an exact match
  makes every request published before this change invalid, so say that the
  field is mandatory for the code family from this version.

- **Q02, repair isolation: keep B2, fix the baseline.** File-level refusal (B1)
  rejects safely separable work, and a second worktree (B3) buys provenance the
  baseline already gives. B2 is right, but the baseline described in the body is
  the index tree object plus the pre-existing unstaged and untracked paths that
  overlap the step. A reviewer-only patch cannot be computed from path names.
  Suggested body correction:

  > The reviewer records the content of every file it may touch before the first
  > repair, as blobs in the object database, together with the index tree
  > object. The reviewer-only patch is the difference between that recorded
  > content and the post-repair content, so writer hunks present before the
  > repair never enter the staged delta.

  Two edge cases deserve one line each: a file the reviewer creates has no
  baseline blob and is wholly reviewer-authored, and a file the writer deletes
  while unstaged is not a repair target.

- **Q03, write boundary: keep C2, add the mechanism.** C1 leaves the critical
  boundary advisory and C3 turns this effort into an evaluator refactor, so C2
  is right. But `implementation-check` is a prompt instruction, so a reviewer
  mode is a convention in the same way C1 is, and the design claims more than
  the option delivers when it calls it "an enforceable interface contract" and
  says an attempted umbrella write "fails the review boundary". Nothing detects
  the write. Suggested addition:

  > Before applying the criteria, the reviewer records the digest of the
  > umbrella document. After the pass, a changed digest fails the review
  > boundary and is reported as a boundary violation, whatever the workflow
  > result claims.

  With that post-condition the mode becomes checkable, and C2's pro line becomes
  true rather than aspirational.

- **Q04, validation-set resolution: keep D3, define the drift response.** D1
  hides the contract from the requestor and D2 lets a stale request weaken the
  project floor, so D3 is right. Its own con names the missing rule and the
  answer stops at "a truthful request-staleness result" without saying what the
  reviewer runs. Suggested answer addition:

  > When revalidation disagrees with the embedded set, the reviewer runs the
  > union of the two sets, reports the difference and its direction, and treats
  > drift alone as a finding rather than a blocker. A default the current
  > resolver requires cannot be dropped because the request predates it.

  The union rule follows from the settled answer that project defaults may be
  added to but never removed. Without it, two conforming implementations
  disagree on which side wins. Note also that D3 is the second requestor-side
  payload change, so it belongs in the same scope statement as Q01.

- **Q05, retained manifest: keep E1, add the retirement rule.** A stable derived
  path avoids enumeration and matches the specification reviewer's single-use
  manifest, which is the right precedent. Two lifecycle facts are missing:

  > The manifest is retired only after `publish-answer` reports
  > `outcome: published`. A `commit-ready` round reaches that outcome with exit
  > `3`, since the stop is the pending human confirmation, so retirement keyed
  > on exit `0` would leak the manifest on every convergence.

  This is worth stating in the design because it is the exact trap the
  specification reviewer had to call out, and the code family hits it on every
  successful review rather than rarely.

- **Q06, renderer composition: F2 confirmed, no change.** The envelope, identity
  fields, root and ignore validation, single read of each input, and the atomic
  paired write are protocol invariants that already exist; the findings schema
  is genuinely code-specific. F1 would duplicate the invariants and F3 would
  produce a union model with role-invalid combinations. Nothing to add.

- **Q07, `a.commit` interface: keep G3, correct the interface claim.** Heuristic
  reading (G1) can recommend readiness for something `gcba` rejects, and a
  subprocess dry run (G2) returns no structured groups, so G3 is right. The
  design should record what exists, because half of the named interface does
  not. `tools/git_batch_commit_parsing.py` exposes one public function,
  `parse_clipboard_content(content, *, interactive=True)`, returning
  `CommitBlock` values from `tools/git_batch_commit_models.py` and raising
  `CommitMessageError`. There is no public validation function in those modules.
  Suggested confirmed fact and answer correction:

  > A typed batch-commit parser already exists and returns `CommitBlock` values,
  > so `a.commit` structure is machine-readable today. The validator half does
  > not exist yet: this effort adds a side-effect-free validation entry point
  > beside the parser, covering file membership against the staged set, group
  > ordering, and conventional subjects, and the reviewer calls the parser with
  > `interactive=False` so no prompt can block a non-interactive round.

  Without that correction the plan phase will look for an API that is not there.

One decision is missing.

- **Q08: what happens when running mandatory validation changes the tree?** The
  reviewer runs the project validation entry point and its coverage gate, and
  those commands write: coverage data, caches, generated reports, sometimes
  formatted sources. Two settled rules then collide with no arbiter. The
  substantive-change rule makes any resulting change to a tracked file
  substantive, which would force another round for a side effect the reviewer
  did not author. The stopped-round rule requires the tree and index to be left
  untouched, which a validation run can already have broken before the round
  stops. Options worth putting to the writer: K1, treat every post-validation
  difference as a reviewer-authored substantive change, which is simple and
  wrong often; K2, record the working-tree and index state before and after
  validation, accept differences confined to ignored paths, and report a
  tracked-file difference as a finding that blocks readiness without counting as
  a reviewer repair; K3, snapshot and restore the tree around validation, which
  risks destroying concurrent writer work for the same reason H1 was rejected.
  My recommendation is K2: a project whose own gate dirties tracked files is a
  finding worth surfacing, the reviewer did not author it, and it should not be
  laundered into a repair or silently reverted.

### Requested changes for design-specification code-reviewer round 1

Requested changes: The seven questions are the right seven and every recommended option stands, so
this round asks for no option change. Eight edits remain, three of which an
implementation cannot proceed without.

- Put the request-payload extension in scope, naming the request-time index tree
  and the resolved validation set, and the requestor surfaces they change. Both
  currently sit outside the design's own scope statement.
- Give the Q01 request-time gate a lifetime (once per fresh assessment, retained
  assessed tree afterwards) so a reclaimed round is not rejected by the
  reviewer's own staged repairs.
- Give index drift an outcome: publish `changes-requested` with both tree
  objects, since the reviewer cannot cancel, continue, or consume.
- Record pre-repair file content in the baseline, not only overlapping paths, so
  option B2's reviewer-only patch is computable.
- Add an umbrella-digest post-condition around the `implementation-check` pass,
  so the write boundary is detected rather than trusted.
- Define the Q04 revalidation result as the union of the embedded and current
  sets, with the difference reported and drift alone not blocking.
- Add the manifest retirement rule, including that a `commit-ready` publication
  reports `published` with exit `3`.
- Correct the Q07 interface: the typed parser exists, the validation entry point
  does not and this effort adds it, and the parser must be called
  non-interactively.
- Add Q08 for validation side effects on the tree, recommended option K2.

### Writer instructions for design-specification code-reviewer round 1

Apply these changes to `docs/v0.11.0/design.v0.11.0.code-reviewer.md`, then
publish another automated round. Do not consolidate. All seven selected options
stand; nothing below changes an option.

1. Widen the scope statement. Add the code-family request-payload extension to
   the in-scope list, naming both fields it adds (the request-time Git index
   tree from Q01 and the resolved mandatory validation set from Q04) and the
   surfaces they touch: `tools/code_review_request.py`, the code-review request
   template, and the `code-review-requestor` instruction. Both fields are
   requestor-side work that the current scope section does not claim, and the
   plan phase cannot assign an owner without this.
2. Give the Q01 gate a lifetime and an outcome, using the two quoted passages.
   The gate runs once before a fresh assessment; the retained assessed tree
   governs afterwards, otherwise every reclaimed round rejects itself on the
   reviewer's own staged repairs. Drift publishes `changes-requested` with both
   tree objects, since the reviewer owns no other way to end a round. State that
   the field is mandatory for code-family requests from this version.
3. Correct the baseline in "Baseline and reviewer-authored change model" so it
   records pre-repair file content, not only overlapping paths. Option B2 needs
   a reviewer-only patch, and a patch cannot be derived from a path list. Add
   the created-file and writer-deleted-file cases.
4. Add the umbrella-digest post-condition to the reviewer-safe
   `implementation-check` boundary. Without a machine check, "fails the review
   boundary" and "enforceable interface contract" describe an intention rather
   than a mechanism, and option C1 was rejected for exactly that weakness.
5. Add the union rule and drift reporting to the Q04 answer, so revalidation has
   a defined result instead of an adjective.
6. Add the retained-manifest retirement rule to the recovery section, including
   the exit `3` note for a `commit-ready` publication. The code family reaches
   that outcome on every successful review, so a retirement keyed on exit `0`
   leaks the manifest routinely.
7. Correct the Q07 interface claim and add a confirmed fact for the batch-commit
   parser. The parser exists and returns typed `CommitBlock` values; the
   validation entry point does not exist and this effort adds it. Record the
   non-interactive call requirement.
8. Add Q08 through `oqm` for validation side effects, following the existing BBQ
   and options shape, with K2 recommended. This is the one decision the design
   does not make, and it sits between two settled rules that currently give
   opposite answers.

Items 1, 2, and 8 are the ones an implementation cannot proceed without: the
first has no owner, the second rejects its own recovery path, and the third has
no rule at all. Items 3 to 7 close the gap between what an option promises and
what the design describes. With all eight applied, round 2 can converge.

### Final reviewer decision for design-specification code-reviewer round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-14T21:00:00+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for design-specification code-reviewer round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
Review round: 2

### Requestor assessment for design-specification code-reviewer round 2

The design now resolves every round-1 finding while preserving the selected answers A2, B2, C2, D3, E1, F2, and G3. Q08 adds the missing validation-side-effect decision with K2 selected. All eight questions have three materially distinct options, honest pros and cons, a recommendation, and an answer.

The requestor-side payload extension is explicitly in scope and names the request-time Git index tree, resolved validation set, renderer, template, and requestor instruction. Q01 makes the request-time tree mandatory from this version, runs its gate once before a fresh assessment, publishes `changes-requested` with both trees and differing paths on drift, and uses the retained assessed tree for recovery. Q02 records pre-repair file content as blobs and covers created and writer-deleted files. Q03 adds the umbrella-digest post-condition. Q04 runs the union of embedded and current validation sets and reports drift direction. Q05 retires its manifest on `outcome: published`, including exit 3. Q07 distinguishes the existing typed parser from the new validator and requires non-interactive parsing. Q08 records validation state, accepts ignored artifacts, and reports tracked changes without staging or reverting them.

No further design question is currently missing. The body, decision table, acceptance cases, and open-question answers express the same contracts.

### Change summary for design-specification code-reviewer round 2

Since round 1, the design scope now owns both code-family request-payload fields and their requestor surfaces. Assessment context defines the one-time request-tree gate, its `changes-requested` drift outcome, and assessed-tree recovery. Repair isolation now stores pre-repair blobs. The implementation-check boundary verifies an umbrella digest. Validation-set revalidation uses the union rule, and validation side effects have the K2 state-comparison rule. Manifest retirement handles published answers at exits 0 and 3. The batch-commit section names the existing parser, adds the missing validator, and requires `interactive=False`. Q01-Q07 answers were sharpened without changing selections, and Q08 was added with K2 selected.

### Writer response for design-specification code-reviewer round 2

Writer response: All round-1 requested changes are accepted and applied. The writer agrees that request-time tree and validation-set payloads require explicit requestor-side scope; that the request-tree gate must run only before fresh assessment and publish a normal `changes-requested` result on drift; that repair isolation requires pre-repair content; that reviewer mode needs an umbrella-digest post-condition; that validation resolver drift needs the union rule; that manifest retirement follows the published outcome rather than exit 0; and that the typed parser exists while the validator must be added. The missing validation-side-effect decision is now Q08 with K2 recommended and answered. There is no disagreement.

### Reviewer focus for design-specification code-reviewer round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-14T21:19:51+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification code-reviewer round 2

All eight round-1 items landed, and each landed in every place it needed to
rather than in one. The scope section now owns both request-payload fields and
names the three requestor surfaces they touch. The Q01 gate has a lifetime and
an outcome, and the recovery section states that the gate is not repeated. The
baseline records pre-repair content as blobs, with the created-file and
writer-deleted cases. The umbrella digest post-condition is in the body, the
options, and the answer. Q04 carries the union rule and drift direction. Q05
retires the manifest on the published outcome and names the exit `3` trap. Q07
separates the parser that exists from the validator this effort adds and
requires the non-interactive call. Q08 is a well-formed question with three
distinct options, K2 answered, a body rule, a decision-table row, and two
acceptance cases.

I would choose A2, B2, C2, D3, E1, F2, G3, and K2, the same eight the writer
selected. No option needs to change and no further question is missing.

Two gaps remain, and both are the same kind: a transition with no named actor or
outcome. They are the last of the class this review has been closing since round
1, where a rule says what must not happen without saying what does happen
instead.

The first is request content the shared layer cannot validate. The exchange
validates the envelope and returns `request-pending`, so a request whose step
identifier is absent from the plan, or whose human-readable fields disagree with
the envelope, or which lacks the now-mandatory request-time tree, arrives as a
perfectly valid pending round. The acceptance table says "Review stops before
staged-state mutation" and the validated-context section lists what must agree,
but neither names the outcome. The reviewer cannot cancel or consume, so a round
that merely stops holds the lease until it expires into the abandoned state that
needs a human or a requestor reclaim. Index drift already got the right answer
last round: publish `changes-requested` with the diagnostic. The same rule fits
these cases and should be stated once for all of them.

The second is escalation. The design says the same missing mandatory evidence in
the next round, a writer dispute, or the shared no-progress bound "causes
escalation", with no actor. The allowed-operations list says the reviewer may
wait, assess, repair, render, and publish, and may not consume, continue,
confirm, complete, resolve, archive, cancel, or commit. `escalate` appears in
neither list, so an implementer can read it either way, and the two readings
produce different architectures: a reviewer that ends the automated dialogue
itself, or a reviewer that stays advisory and lets the requestor and the shared
bound do it. The advisory reading matches every other decision in this document
and needs one sentence to become explicit.

Three smaller corrections sit in the new enforcement paths. The umbrella digest
is compared "after the criteria pass", which contradicts the same paragraph's
"regardless of the workflow result" and would skip the check on the failure path
where a mistaken write is just as possible. Nothing says what the digest check
does when the request states `Umbrella draft: none`. And the reported validation
results describe the state before any repair, which the answer contract does not
say, so a writer reading a repaired round can take pre-repair results for
post-repair evidence.

Nothing else is outstanding. The routing, policy, baseline, repair isolation,
readiness classifier, renderer composition, guidance boundary, and recovery
model are internally consistent and match the consolidated requirement. With
these five edits the design is ready for a convergence recommendation.

### Question verdicts for design-specification code-reviewer round 2

Eight questions, eight confirmed answers. No option changes, and no question is
missing, redundant, unclear, or outside the design phase.

- **Q01, authoritative snapshot: A2 confirmed.** The gate now has a lifetime
  (once, before a fresh assessment), an outcome (`changes-requested` naming both
  tree objects and the differing paths), a version rule (mandatory for
  code-family requests from this version), and a recovery rule (the retained
  assessed tree governs afterwards). The body, the answer, the recovery section,
  the target-behavior flow, and a new acceptance case all agree. My answer is
  A2.
- **Q02, repair isolation: B2 confirmed.** Baseline blobs make the reviewer-only
  patch computable, which is what the option needed. Created files and
  writer-deleted unstaged files are handled. My answer is B2.
- **Q03, write boundary: C2 confirmed, two precision fixes.** The digest
  post-condition turns the reviewer mode from a convention into something
  detectable, which is exactly what C1 lacked. Two details in that paragraph
  work against each other:

  > After the criteria are applied, whether they passed or failed, the reviewer
  > compares the umbrella digest with the recorded value.

  The current text says "after the criteria pass" one sentence before saying
  "regardless of the workflow result". A mistaken umbrella write is at least as
  likely on the failure path, so the check has to run on both. Second, add the
  no-umbrella case:

  > When the request states `Umbrella draft: none`, there is no umbrella status
  > table to protect and the digest check is recorded as not applicable.

- **Q04, validation-set resolution: D3 confirmed.** The union rule, the drift
  direction report, and the rule that an older request cannot drop a current
  default make revalidation deterministic. My answer is D3. One contract gap,
  below, is about where that drift evidence lands rather than about the rule.
- **Q05, retained manifest: E1 confirmed.** The stable derived path, atomic
  replacement, published-outcome retirement, and the exit `3` note are all
  present. The exit `3` sentence is worth keeping verbatim: it is the one
  mistake that would otherwise recur on every successful code review.
- **Q06, renderer composition: F2 confirmed, no change.** Shared envelope and IO
  validation, code-specific typed model and template. Nothing to add.
- **Q07, `a.commit` interface: G3 confirmed.** The confirmed-fact entry now
  matches the tree: `parse_clipboard_content(content, *, interactive=True)`
  returning `CommitBlock` values, no public validator, one added by this effort.
  The `interactive=False` requirement is in both the body and the answer, which
  matters because the default would let a prompt block a non-interactive round.
  My answer is G3.
- **Q08, validation side effects: K2 confirmed.** The three options are
  materially distinct and the con lines are honest, including K2's own cost that
  an intended source rewrite by the gate blocks readiness. That cost is the
  right trade: a project gate that rewrites tracked sources during review is
  something the writer should see rather than something the reviewer absorbs.
  K1 misattributes command output to the reviewer and K3 repeats the data-loss
  risk that H1 was rejected for. My answer is K2.

Two contracts still lack an actor or an outcome, and both are extensions of
rules this design has already accepted.

- **Give request-content failures the outcome that index drift already has.**
  The shared exchange validates the envelope, so a request whose step is absent
  from the plan, whose human-readable fields disagree with the envelope, or
  which omits the mandatory request-time tree still arrives as a valid
  `request-pending` round. The validated-context section lists what must agree
  and the acceptance table says review "stops", but nothing says how a stopped
  review ends. The reviewer cannot cancel or consume, so stopping silently holds
  the lease until it expires into the abandoned state. Suggested addition to the
  validated-context section:

  > When request content the shared exchange cannot validate is wrong, the
  > reviewer publishes `changes-requested` naming the exact disagreement and
  > mutates nothing: a step identifier the plan does not define, a
  > human-readable field that disagrees with the envelope, or a missing
  > request-time index tree. A stopped review that publishes nothing would hold
  > the lease until it expires, so the reviewer always ends its round through
  > the answer it is allowed to publish.

  Update the "Request step absent from the plan" acceptance case to name that
  outcome, the way the drift case now does.

- **Name the escalation actor.** The readiness section says repeated missing
  evidence, a writer dispute, or the shared bound "causes escalation" without
  saying who performs the transition, and `escalate` appears in neither the
  allowed nor the forbidden operation list. Both readings are architecturally
  coherent, so the design has to choose. Suggested wording, matching the
  advisory role every other decision in this document takes:

  > The reviewer does not call `escalate`. It publishes the finding that
  > mandatory evidence is still unavailable or disputed, and the requestor and
  > the shared no-progress bound perform the escalation transition.

  Add `escalate` to the forbidden list in the allowed-operations paragraph so
  the two statements cannot drift apart.

One contract completeness item and one accuracy item close the round.

- **The renderer input list and answer sections predate Q04 drift and Q08.** The
  typed model receives a "validation report" and the answer covers
  "mandatory-check and coverage results", neither of which mentions the resolved
  set and its sources, the resolver drift and its direction, or the
  pre-validation and post-validation state comparison. Say once that the
  validation report carries all four, so the typed model is complete and the two
  new evidence classes reach the writer instead of being folded into prose.
- **Say which state the reported validation results describe.** Validation runs
  before repairs in the target-behavior flow. A round with substantive repairs
  publishes `changes-requested` anyway, so re-running is not required, but the
  answer should label the results as covering the pre-repair staged state.
  Otherwise a writer reading a repaired round can take them for evidence about
  the state the reviewer left behind.

### Requested changes for design-specification code-reviewer round 2

Requested changes: All eight round-1 items landed and all eight answers stand, so this round asks
for no option change and no new question. Five edits remain, two of which decide
behavior.

- Give request-content failures the outcome index drift already has: publish
  `changes-requested` naming the disagreement when the step is absent from the
  plan, a human-readable field disagrees with the envelope, or the mandatory
  request-time tree is missing. A review that stops without publishing holds the
  lease until it expires.
- Name the escalation actor: the reviewer publishes the finding and does not
  call `escalate`, and `escalate` joins the forbidden operations list.
- Compare the umbrella digest after the criteria are applied whether they passed
  or failed, and record it as not applicable when the umbrella is `none`.
- Carry the resolved validation set, its sources, resolver drift and direction,
  and the pre-validation and post-validation state comparison in the renderer
  input list and the answer sections.
- Label the reported validation results as covering the pre-repair staged state.

### Writer instructions for design-specification code-reviewer round 2

Apply these five changes to
`docs/v0.11.0/design.v0.11.0.code-reviewer.md`, then publish round 3. Do not
consolidate. No option changes and no question is added.

1. Add the quoted request-content failure rule to the validated-context section,
   covering a step the plan does not define, a human-readable field that
   disagrees with the envelope, and a missing request-time index tree. Update
   the "Request step absent from the plan" acceptance case to name
   `changes-requested` as its outcome, the way the drift case already does. This
   is the rule you accepted last round for index drift, applied to its siblings.
2. Name the escalation actor in the readiness section with the quoted sentence,
   and add `escalate` to the forbidden operations list. Leaving it out of both
   lists lets two implementations build different architectures from the same
   design.
3. Fix the umbrella-digest paragraph: compare the digest after the criteria are
   applied whether they passed or failed, and record the check as not applicable
   when the request states `Umbrella draft: none`. As written, the paragraph
   contradicts itself one sentence apart and skips the failure path.
4. Extend the renderer input list and the answer sections so the validation
   report carries the resolved set and its sources, the resolver drift and its
   direction, and the pre-validation and post-validation state comparison. Q04
   and Q08 added two evidence classes that the typed model never picked up.
5. Label the reported validation results as covering the pre-repair staged
   state, since validation runs before repairs in the target-behavior flow.

Items 1 and 2 decide behavior an implementation would otherwise invent. Items 3
to 5 close the gap between a rule and the evidence that carries it. With these
applied, round 3 can converge: the eight questions cover the design-phase
decisions, every selected option is sound, and the body, decision table, and
acceptance cases carry the same contracts everywhere else.

### Final reviewer decision for design-specification code-reviewer round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-14T21:26:02+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for design-specification code-reviewer round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
Review round: 3

### Requestor assessment for design-specification code-reviewer round 3

The design now applies all five round-2 corrections while preserving answers A2, B2, C2, D3, E1, F2, G3, and K2. All eight questions remain sufficient, their options remain materially distinct, and no new design question is missing.

Invalid specialized request content now produces `changes-requested` without mutation for an undefined step, human-readable identity disagreement, or missing request-time tree, so the reviewer ends through its allowed publication operation. Escalation is explicitly requestor and shared-bound owned; `escalate` is forbidden to the advisory reviewer. The umbrella digest is checked after both successful and failed criteria application, with `Umbrella draft: none` recorded as not applicable. The typed validation report now carries the resolved set and sources, drift and direction, and repository state around validation. Validation results are explicitly labeled as evidence for the pre-repair staged state. The acceptance cases and answer contract match these rules.

Every round-2 wording suggestion was applied. The body, decision table, acceptance cases, renderer model, and open-question answers are internally consistent, with no known remaining gap.

### Change summary for design-specification code-reviewer round 3

Since round 2, the design gives invalid request content a normal `changes-requested` outcome and adds matching acceptance cases. It forbids reviewer escalation and assigns that transition to the requestor and shared no-progress bound. Umbrella digest verification now runs after criteria on both pass and fail and records the no-umbrella case as not applicable. The renderer's typed validation report now includes resolved-set provenance, resolver drift, and repository state around validation. Reported command results are labeled as covering the pre-repair staged state. No option or answer changed, and no question was added.

### Writer response for design-specification code-reviewer round 3

Writer response: All round-2 requested changes are accepted and applied. The writer agrees that specialized request-content failures must publish `changes-requested`, that the advisory reviewer must not call `escalate`, that the umbrella digest must be checked after both pass and fail with a not-applicable result for no umbrella, and that Q04 and Q08 evidence must be present in the typed renderer model. Validation results now identify the pre-repair staged state they cover. There is no disagreement and no proposed option change.

### Reviewer focus for design-specification code-reviewer round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-14T21:33:07+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification code-reviewer round 3

All five round-2 corrections landed, and each reached both the body and the
places that have to agree with it. Request-content failures now publish
`changes-requested` and mutate nothing, with two matching acceptance cases.
`escalate` joined the forbidden operations list and the readiness paragraph
names the requestor and the shared bound as the actors. The umbrella digest is
compared after the criteria are applied whether they passed or failed, and the
`Umbrella draft: none` case is recorded as not applicable. The typed validation
report carries the resolved set and sources, resolver drift and direction, and
the repository state around validation, in both the renderer input list and the
answer sections. Command results are labeled as pre-repair evidence.

The eight questions are unchanged and remain sound. A2, B2, C2, D3, E1, F2, G3,
and K2 are the answers I would choose. No question is missing.

One item is left, and it is a consequence of the rules added in the last two
rounds rather than an old oversight. The design now has two kinds of answer. The
full one reports an assessment. The early-rejection one ends a round before any
assessment happens: a step the plan does not define, a human-readable field that
disagrees with the envelope, a missing request-time tree, or a live index that
differs from the request-time tree. Three acceptance cases require that second
kind. The typed renderer model describes only the first: it receives the
baseline and assessed index identities, the repair report, the validation
report, the `a.commit` assessment, and the unresolved findings, with only human
guidance marked optional, and the answer sections assume every one of them
exists.

An implementation cannot render the three early-rejection cases against that
model. It would have to invent empty reports, or quietly drop the validation the
model exists to provide, and the two choices produce different artifacts for the
same situation. The specification renderer already solves this shape of problem
by requiring different authored evidence per disposition; the same approach
works here, with the difference keyed on whether an assessment occurred rather
than on the disposition alone.

Two wording items are worth taking while the file is open, both listed in the
requested changes. Neither changes behavior.

Everything else holds. Routing, the allowed-operation list, the request-time
gate and its lifetime, baseline blobs and hunk attribution, the reviewer-safe
check boundary and its digest post-condition, resolver union and drift, the
six-item classifier, validation side effects, guidance, publication, and
stopped-round recovery are internally consistent and match the consolidated
requirement. With the answer contract split, round 4 converges.

### Question verdicts for design-specification code-reviewer round 3

Eight questions, eight confirmed answers, no option change and no question
missing. The single remaining item belongs to the answer contract in the body,
not to any question.

- **Q01, authoritative snapshot: A2 confirmed.** Gate lifetime, drift outcome,
  version rule, and recovery rule agree across the body, the answer, the
  recovery section, the target-behavior flow, and the acceptance cases.
- **Q02, repair isolation: B2 confirmed.** Baseline blobs make the reviewer-only
  patch computable; created and writer-deleted files are handled.
- **Q03, write boundary: C2 confirmed.** The body now checks the digest after
  the criteria are applied on both paths and records the no-umbrella case as not
  applicable. One leftover: option C2 still reads "verify an umbrella digest
  before and after the criteria pass", which can be read as the success path
  only. The body is unambiguous, so this is wording. Suggested option text:

  > Option C2: Add reviewer assessment mode and verify an umbrella digest before
  > and after the criteria are applied, whether they passed or failed.

- **Q04, validation-set resolution: D3 confirmed.** Union, drift direction, and
  the rule that an older request cannot drop a current default are stated, and
  the evidence now reaches the typed model.
- **Q05, retained manifest: E1 confirmed.** Stable derived path, atomic
  replacement, published-outcome retirement, exit `3` note.
- **Q06, renderer composition: F2 confirmed.** Shared envelope and IO
  validation, code-specific typed model and template. The item below is about
  what that typed model must accept, not about the composition choice.
- **Q07, `a.commit` interface: G3 confirmed.** Existing parser, new validator,
  `interactive=False`.
- **Q08, validation side effects: K2 confirmed.** Body rule, decision-table row,
  and two acceptance cases agree.

One contract gap remains.

- **The typed answer model has no shape for a round that ends before
  assessment.** Rounds 2 and 3 added four situations where the reviewer publishes
  `changes-requested` without assessing anything: a step the plan does not
  define, a human-readable field disagreeing with the envelope, a missing
  request-time index tree, and a live index differing from the request-time
  tree. Three acceptance cases require exactly that. The renderer input list
  requires the baseline and assessed index identities, the repair report, the
  validation report, the `a.commit` assessment, and the unresolved findings,
  marking only human guidance optional, and the eight answer sections assume an
  assessment produced each one. Rendering an early rejection against that model
  forces the implementation either to fabricate empty reports or to relax the
  validation the model exists to provide, and those two choices produce
  different artifacts for the same case. Suggested addition to the renderer
  section:

  > A code-review answer takes one of two shapes. An assessment answer carries
  > the baseline and assessed index identities, repair report, validation
  > report, `a.commit` assessment, and unresolved findings. An early-rejection
  > answer ends a round before assessment and carries the validated context,
  > round, `changes-requested` disposition, the exact identity or snapshot
  > disagreement, and the writer instructions that would resolve it;
  > assessment-derived fields are absent rather than empty. The renderer
  > validates each shape separately and rejects a mixture, in the same way the
  > shared renderer already requires different authored evidence for each
  > disposition.

  Add one line to the answer-sections list saying an early-rejection answer
  renders only the identity, disagreement, and instruction sections, so the
  section contract and the input model stay aligned.

One more wording item. The acceptance case for an attempted umbrella status
update says "Review stops that write", while the mechanism is a digest compared
after the criteria ran, so a write that happened is detected rather than
prevented. The row's own reason already says "reports the boundary failure".
Suggested outcome text, which also settles what happens to the modified file:

> Reviewer fails the boundary, reports the violation, and leaves the changed
> umbrella in place; the change is substantive, so the round is
> `changes-requested`.

Optionally, the "same mandatory evidence unavailable" acceptance case could name
the reviewer's part the way the readiness paragraph now does: the reviewer
publishes the finding, and the requestor and the shared bound escalate.

### Requested changes for design-specification code-reviewer round 3

Requested changes: All five round-2 corrections landed and all eight answers stand, so this round
asks for no option change and no new question. Three edits remain, one of which
decides what an implementation builds.

- Split the answer contract into an assessment answer and an early-rejection
  answer, and say that assessment-derived fields are absent rather than empty in
  the second. Three acceptance cases require a `changes-requested` answer
  published before any assessment, and the typed renderer model currently
  requires the repair report, validation report, `a.commit` assessment, assessed
  index identity, and unresolved findings for every answer.
- Rewrite the umbrella-status acceptance outcome so it describes detection
  rather than prevention, and say the changed umbrella is left in place and
  makes the round `changes-requested`.
- Align the Q03 option wording with the body's "whether they passed or failed",
  and optionally name the reviewer's part in the escalation acceptance case.

### Writer instructions for design-specification code-reviewer round 3

Apply these three changes to
`docs/v0.11.0/design.v0.11.0.code-reviewer.md`, then publish round 4. Do not
consolidate. No option changes and no question is added.

1. Split the answer contract into its two shapes, using the quoted paragraph in
   the renderer section, and add the matching line to the answer-sections list.
   This is the only item that changes what an implementation builds: three
   acceptance cases already require an answer that carries no assessment, and
   the current typed model cannot express one.
2. Replace the outcome text of the umbrella-status acceptance case with the
   quoted wording, so the row describes detection rather than prevention and
   states that the changed file stays in place and makes the round
   `changes-requested`.
3. Take the Q03 option wording, and optionally the escalation acceptance case,
   so the questions read the same way the body now does.

Item 1 is the last substantive gap I can find. Items 2 and 3 are wording. With
item 1 applied, the design is ready for a convergence recommendation in round 4:
the eight questions cover the design-phase decisions, every selected option is
sound, and the body, decision table, acceptance cases, renderer model, and
answers agree everywhere else.

### Final reviewer decision for design-specification code-reviewer round 3

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor

- Recorded: 2026-08-14T21:44:08+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: request

### Review identity for design-specification code-reviewer round 4

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
Review round: 4

### Requestor assessment for design-specification code-reviewer round 4

The design now resolves the round-3 answer-contract gap while preserving A2, B2, C2, D3, E1, F2, G3, and K2. All eight questions remain sufficient, their options remain materially distinct, and no new question is missing.

The answer renderer now accepts a discriminated union. Both shapes share only protocol-valid exchange identity and round metadata. An assessment answer requires fully validated context and all assessment evidence. An early-rejection answer carries the exact identity or snapshot disagreement and writer instructions; fully validated context, index assessment identities, repair report, validation report, `a.commit` assessment, and unresolved findings are prohibited rather than fabricated as empty reports. Each shape is validated separately and mixtures are rejected. The answer-section contract renders only identity, disagreement, and instructions for early rejection.

The umbrella acceptance case now describes post-criteria detection, leaves the changed umbrella in place, and makes the substantive result `changes-requested`. Q03 option C2 now says digest verification occurs after criteria are applied whether they pass or fail. The repeated-evidence acceptance case also names the reviewer's publication role and the requestor/shared-bound escalation role. Every round-3 wording suggestion was applied, with no disagreement and no known remaining design gap.

### Change summary for design-specification code-reviewer round 4

Since round 3, the paired answer design now defines separately validated assessment and early-rejection input shapes. Assessment-derived fields are absent rather than empty in early rejection, and the rendered section set is correspondingly limited. The umbrella-status acceptance case now describes digest detection, retained file state, and the resulting `changes-requested` disposition. Q03 option C2 now covers both successful and failed criteria application. The repeated mandatory-evidence case now names reviewer publication and requestor/shared-bound escalation. No answer selection changed and no question was added.

### Writer response for design-specification code-reviewer round 4

Writer response: All round-3 requested changes are accepted and applied. The writer agrees that early rejection must be a separately validated typed shape whose assessment-derived fields are absent, that the umbrella digest mechanism detects rather than prevents a changed file and leaves it in place for `changes-requested`, and that Q03 must state the pass-and-fail behavior. The optional escalation acceptance wording was also aligned with the body. There is no disagreement, no option change, and no missing question.

### Reviewer focus for design-specification code-reviewer round 4

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer

- Recorded: 2026-08-14T21:59:13+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: answer

### Reviewer assessment for design-specification code-reviewer round 4

The three round-3 items landed, and the first one landed better than the change
I asked for. I suggested that assessment-derived fields be absent in an
early-rejection answer; the design makes the renderer a discriminated union that
prohibits them and rejects any mixture, so a malformed answer fails at the type
boundary rather than at review time. The answer-section contract matches, the
umbrella acceptance case now describes detection rather than prevention and says
the changed file stays in place, Q03 option C2 covers the pass and fail paths,
and the repeated-evidence case names both actors.

Every design-phase decision is settled. The eight questions cover routing and
snapshot authority, repair isolation, the check write boundary, validation-set
resolution, retained evidence, renderer composition, the `a.commit` interface,
and validation side effects. A2, B2, C2, D3, E1, F2, G3, and K2 are the answers
I would choose, each option set is materially distinct, and each answer names
the observable fact that decides it. No question is missing, redundant, unclear,
or outside the design phase.

I traced the contracts that cross section boundaries and they hold. The
request-time gate has a lifetime that does not collide with reclaim, because
recovery compares the retained assessed tree instead. Every path that ends a
round names its outcome: assessment answers, early rejections, index drift,
boundary violations, and repeated missing evidence. Every transition names its
actor: the reviewer publishes, and the requestor and the shared bound escalate.
The substantive-change rule, its four exemptions, the readiness floor, and the
validation side-effect rule partition the ways a file can differ, so no
difference is both a reviewer repair and a command artifact. The retained
manifest has a path, a replacement rule, and a retirement rule that survives the
exit `3` a successful code review always produces. The two answer shapes carry
exactly the evidence their situation can produce.

Two wording edits remain, listed in the covered wording. The decision table
still describes answer production as rendering "from one typed assessment",
which predates the union, and the target-behavior flow shows only the path where
assessment proceeds. Neither changes behavior and both can be applied during
consolidation.

Nothing here reopens a settled requirement-phase choice. The design carries the
nine consolidated clarifications and the design-phase observation about human
guidance that the requirement review left for this document, and it adds no
authority the requirement withheld.

This is a convergence recommendation and nothing more. It is advisory, it
authorizes no consolidation, and the choice between `Consolidate` and `Revise
and review again` stays with the human at the requestor's gate.

### Question verdicts for design-specification code-reviewer round 4

Eight questions, eight confirmed answers, no option change and no question
missing.

- **Q01, authoritative snapshot: A2.** A mandatory request-time index tree, one
  gate before a fresh assessment, `changes-requested` on mismatch naming both
  trees and the differing paths, and the retained assessed tree for recovery.
  The gate and the reclaim path no longer collide, which was the round-1
  finding.
- **Q02, repair isolation: B2.** Pre-repair content recorded as blobs makes the
  reviewer-only patch computable, hunk attribution fails closed on unsafe
  overlap, and created and writer-deleted files are covered.
- **Q03, write boundary: C2.** Reviewer assessment mode plus a digest compared
  after the criteria are applied on either path, with the no-umbrella case
  recorded as not applicable. The acceptance case now matches the mechanism: the
  digest detects a write that already happened, the changed file stays in place,
  and the round becomes `changes-requested` under the substantive rule.
- **Q04, validation-set resolution: D3.** One shared resolver at publication and
  at assessment, the union on disagreement, drift reported with its direction
  and not treated as a blocker, and no removal of a current default by an older
  request.
- **Q05, retained manifest: E1.** Stable identity-and-step path, atomic
  replacement with embedded round validation, retirement keyed to
  `outcome: published`, and the exit `3` note that a `commit-ready` publication
  always produces.
- **Q06, renderer composition: F2.** Shared envelope and IO validation with a
  code-specific typed model. The discriminated union added this round sits
  inside that boundary rather than weakening it: it is two strictly validated
  shapes, not the sparse union of optional fields that made F3 the wrong choice.
- **Q07, `a.commit` interface: G3.** The existing typed parser, a new
  side-effect-free validator for staged membership, group ordering, and
  conventional subjects, and the `interactive=False` call that keeps a
  non-interactive round from blocking on a prompt.
- **Q08, validation side effects: K2.** State compared around validation,
  ignored-path differences accepted, tracked differences reported as
  readiness-blocking findings that are neither a reviewer repair nor an
  automatic rollback.

Cross-checks that hold in the current text: the request-time gate against the
reclaim path; the four early-rejection triggers against the answer contract that
must render them; the substantive-change exemptions against the Q07 validation
rows, the Q08 command artifacts, and the ignored caller evidence; the readiness
floor against the escalation rule, so missing evidence blocks readiness without
granting the reviewer escalation authority; the retained-evidence list against
the fields an assessment answer needs to be rebuilt; and the decision table and
sixteen acceptance cases against the body rules they summarize.

Every round of this review has been closing the same class of gap: a rule that
says what must not happen without saying what does happen instead. Round 1 found
five of them, round 2 found two, round 3 found one. I found none this round.

### Convergence evidence for design-specification code-reviewer round 4

Covered wording: Two wording edits remain. Neither changes behavior, and both can be applied
during consolidation.

- The decision table still describes answer production as rendering the complete
  answer and transcript summary "from one typed assessment", which predates this
  round's discriminated union. Suggested replacement for that row's decision
  cell:

  > Render both answer shapes and their paired transcript summary from one
  > separately validated typed model.

- The target-behavior flow shows only the path where assessment proceeds, so a
  reader following it never meets the four situations that end a round early.
  Suggested insertion after the request-tree verification line:

  > -> invalid request content or index drift ends the round with an
  >    early-rejection answer

Convergence rationale: Four rounds closed everything they opened. Round 1 found a scope contradiction,
a gate that rejected its own recovery path, a drift rule with no outcome, three
interface claims that outran what exists, and one missing decision. Round 2
found two transitions with no actor or outcome and three evidence gaps. Round 3
found the answer contract that could not express the rounds it had just been
told to end early. This round found nothing.

Convergence is warranted because the three conditions this review has been
measuring are met. Every design-phase decision is answered, and each answer
names an observable fact rather than leaving the call to the implementer: a tree
object, a digest, a set union, an exit code, a path derivation, a typed shape.
Every path that ends a round has an outcome and an actor, which is what the
earlier rounds kept finding missing. The body, the decision table, the sixteen
acceptance cases, the renderer model, and the eight answers describe the same
contracts, so an implementation can be checked against any of them and get the
same result.

The design also stays inside its own boundary. It claims the requestor-side
payload extension it genuinely needs, defers requestor continuation, human
confirmation, commit execution, and shared protocol mechanics to their owning
efforts, and adds no authority the consolidated requirement withheld from the
advisory reviewer.

What remains is two sentences of polish that change no behavior, which is the
convergence threshold this exchange set at round 1.

This recommendation is advisory. It does not consolidate the design, does not
authorize consolidation, and does not settle the choice between `Consolidate`
and `Revise and review again`. That choice belongs to the human at the
requestor's confirmation gate, with the option to override this recommendation
and add guidance for another round.

### Writer instructions for design-specification code-reviewer round 4

Do not consolidate on this answer. This is a convergence recommendation, it is
advisory, and consolidation stays behind the human confirmation gate.

1. Take the two wording edits in the covered wording during consolidation. They
   change no behavior, so neither needs another review round.
2. Present the human with the identity, this recommendation, the current design,
   and your own assessment, then offer `Consolidate` or `Revise and review
   again`. If the human overrides with guidance, carry that guidance into the
   replacement request so the next round can address it.
3. Nothing else is outstanding. All eight answers stand as selected, and no
   question needs to be added, split, or removed.

One note for the plan phase rather than for this document. Three deliverables
this design commits to touch surfaces owned by completed efforts: the
code-family request payload and its renderer, the reviewer assessment mode in
`implementation-check`, and the new validator beside the batch-commit parser.
The design puts them in scope, which was the round-1 correction; the plan should
order them so each lands with the tests that cover the completed behavior it
extends.

### Final reviewer decision for design-specification code-reviewer round 4

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human

- Recorded: 2026-08-14T22:04:35+02:00
- Exchange: specification/design-specification/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/design.v0.11.0.code-reviewer.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->
