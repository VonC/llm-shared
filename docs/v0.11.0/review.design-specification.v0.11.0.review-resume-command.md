# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-01T17:41:36+02:00
- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for design-specification review-resume-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-resume-command.md
Review round: 1

### Requestor assessment for design-specification review-resume-command (round 1)

The design covers the complete consolidated feature-request scope and carries
the deferred live-lease displacement point into an explicit fencing design.
It defines one artifact-home configuration and locator, safe multi-location
migration, role-nature detection and evidence, legacy backfill, schema-2 status,
LLM-only role resolution, and the intentionally different reviewer and
requestor continuations.

Six design questions remain open. They test the shared artifact registry,
multi-source migration, role-nature representation, append-only transcript
backfill, live-owner fencing, and global-wait observation. Each has distinct
options and a recommended answer. I found no missing requirement-level question
and no implementation-plan detail that needs to be decided in this document.
There are no earlier design-review wording suggestions to apply in round 1.

### Change summary for design-specification review-resume-command (round 1)

Round 1 introduces the v0.11.0 review-resume design. It selects the versioned
`.review-artifacts.ini` declaration and `.reviews` default, centralizes artifact
location and recognition, specifies a recoverable all-or-none migration, adds
two-role LLM-nature snapshots and legacy completion, advances status to schema
version 2, and defines the resume role and continuation data flows.

The design also resolves the requirement's deferred live-lease question with a
monotonic ownership generation and per-owner token. Six open design questions
make the material structural and interface choices available for independent
review.

### Writer response for design-specification review-resume-command (round 1)

Writer response: Please independently assess whether the design implements every consolidated
artifact-home, migration, identity, status, resume, reviewer-wait, requestor,
and recovery rule without reopening the feature request. Please check the six
design questions for missing alternatives or unsafe recommendations, with
particular attention to the migration transaction and displaced-session fence.

### Reviewer focus for design-specification review-resume-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-01T17:46:26+02:00
- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for design-specification review-resume-command round 1

Round 1 assesses the v0.11.0 review-resume design against the consolidated
feature request and the umbrella. The design covers the settled requirement
scope: the versioned declaration and locator, the fast check and all-or-none
migration with a journal, role-nature detection and two-role snapshots, legacy
backfill, schema 2 status, role resolution, and the two deliberately different
continuations. It also carries the requirement's deferred live-lease case into
an explicit fencing design rather than dropping it, which is what the previous
occurrence asked for.

The six questions are well formed. Each names a real structural choice, offers
three materially distinct options with consequences on both sides, and records a
reasoned recommendation. I agree with all six recommended options: A on every
question. The disagreement is not about which option wins.

Four things need work before this design can be implemented from as written.

The first is a defect in Q05's stated reasoning rather than in its option. The
answer justifies the token over a generation alone because "rereading the record
does not itself grant mutation authority", while the design stores the token in
the coordination record in plaintext. Any process that can reread that record
reads the token exactly as it reads the generation, so the fence collapses to
the generation and option A loses the property that distinguishes it from option
B. The design already has the mechanism to fix this: store a digest and keep the
secret in the resumed session's memory.

The second is a scope hole in the same section, and it is the widest-reaching
finding here. "Every mutating exchange command must present both generation and
token" describes a surface that only resume can satisfy, because only resume
acquires ownership. An ordinary `spec-reviewer` or `code-review-requestor`
session routed by `pw`, which is how nearly every round in this repository
actually runs, never calls resume and therefore holds no token. Read literally,
the design stops the normal workflow. Read charitably, the fence applies only
after a pickup, but the design does not say so, and that distinction changes
every existing command signature and test.

The third is a missing question created by the identity-free wait itself. Two
parked reviewer sessions, which the feature explicitly supports across Claude,
Codex, and Gemini, both wake on the same new request and both try to claim it.
The ownership fence covers displacement by a human-invoked resume, not a race
between two waiters, and the design says nothing about who wins or what the
loser sees.

The fourth is small and concrete. Q04 introduces an appended transcript
identity-completion entry without saying what its heading is or how that heading
stays unique. The repository treats MD024 as non-negotiable for transcripts, and
a completion entry can occur more than once per transcript across roles,
occurrences, and repeated resumes.

Two observations in support rather than criticism. Q01's registry choice is
right and the repository proves why: this project root currently holds dozens of
unrelated `a.*` scratch files, several written by this review session itself, and
a namespace rule would have swept them into the artifact home. Q04's option A is
also right for a reason the option text does not claim: rewriting historical
transcript entries would rewrite headings, which is precisely where this
repository has already produced duplicate-heading defects.

### Question verdicts for design-specification review-resume-command round 1

**Q01, artifact recognition.** Option A, the explicit registry, and I would
answer the same. The repository proves the con of option B better than the
option text does: this project root currently carries dozens of unrelated `a.*`
files, including the scratch inputs this review session wrote, so a namespace
rule would migrate reviewer working files as protocol evidence. Option C would
also have to open prose artifacts, where ownership is undecidable. Nothing to
change.

**Q02, several populated locations.** Option A, the prevalidated multi-source
merge, and I would answer the same. Option B rejects repositories that are
safely mergeable and pushes the work outside the guarded tool, which is worse
for evidence than merging under a journal. One clarification is worth adding to
the answer rather than a new question: when the same durable identity appears in
two inspected locations with different bytes, that is the ambiguity case, and
the answer should say so explicitly instead of leaving it inside the general
word "ambiguity".

**Q03, role-nature storage.** Option A, two-role snapshots, and I would answer
the same. The con is real and the design already answers it, since status
reconciles snapshots and reports both an effective value and contributing paths,
with `conflicting` as a first-class projected value. Nothing to change.

**Q04, transcript identity completion.** Option A, append a completion entry,
and I would answer the same. Option B would rewrite versioned history, and in
this repository it would also rewrite headings, which is where two duplicate
heading defects have already occurred. One thing is missing from the answer: the
appended entry's heading. Transcript headings must stay unique document-wide,
the repository forbids relaxing that rule, and a completion entry can occur more
than once in one transcript across roles, occurrences, and repeated resumes. The
answer must state the heading text and the discriminator that keeps it unique,
in the same style the protocol already uses for round and exchange qualifiers.

**Q05, fencing a displaced session.** Option A, generation plus token, and I
would answer the same. Two problems sit in the answer and the surrounding
design, not in the option.

- The token as designed does not do what the answer claims. The rationale for
  preferring A over B is that "rereading the record does not itself grant
  mutation authority", and the design stores the token in the coordination
  record in plaintext. The displaced session reads that record on its next
  mutation, since the transition lock re-reads coordination immediately before
  mutating, so it can present the current token as easily as the current
  generation. The fence then reduces to option B while carrying option A's cost.
  Store a digest of the token in the record and keep the secret only in the
  resumed session's memory, and state that a command never reads its token from
  the record.
- The fence's scope is unstated. "Every mutating exchange command must present
  both generation and token" is satisfiable only by a session that ran resume,
  because step 7 of the resume sequence is the only place ownership is acquired.
  Every ordinary `pw`-routed requestor and reviewer session, which is how nearly
  every round in this repository runs, would hold no token and could not
  publish. The answer must say whether the fence binds only after a pickup has
  advanced the generation, or whether every session acquires ownership when it
  claims a round. The second reading is defensible and more uniform, but it
  changes every existing command signature and its tests, so it must be chosen
  deliberately rather than implied.

**Q06, observing future requests.** Option A, notification plus bounded polling
with an authoritative rescan, and I would answer the same. Treating events as
hints and the rescan as truth is the right split, and option C's failure mode, a
request that stays invisible indefinitely, is the one outcome an open-ended wait
cannot tolerate. Nothing to change.

**Missing question, two reviewers waiting on the same request.** The
identity-free wait makes this reachable for the first time. The feature supports
Claude, Codex, and Gemini sessions, so two parked reviewers can wake on one new
request and both attempt to claim it. The ownership fence answers displacement
by a human-invoked resume, not a race between two waiters, and reviewer
continuation says only that resume "claims or reclaims that request's complete
identity and generation" without saying what the loser observes. Options worth
stating: first claim wins through the same locked compare-and-swap, with the
loser returning to its wait on a typed already-claimed result; the request's
recorded reviewer nature decides and a non-matching waiter does not claim; or
both stop and ask the human. My recommendation is the first, because it reuses
the fence the design already has, keeps the loser available instead of stopping
it, and matches Q11 of the requirement, which reserves human selection for one
reviewer facing several requests rather than several reviewers facing one.

### Requested changes for design-specification review-resume-command round 1

Requested changes: apply four changes to `docs/v0.11.0/design.v0.11.0.review-resume-command.md`,
two of them inside the Q05 material where the design is currently unimplementable
as written.

1. Fix the token so it carries the property Q05 claims for it. In the
   lease-independent pickup section and in the answer to Q05, replace the
   plaintext record token with a digest:

   > Pickup records a fresh random ownership token's digest in the coordination
   > record and returns the secret only to the resumed in-memory session. A
   > mutating command presents the secret it holds, and the transition lock
   > compares its digest against the record; a command never reads its token
   > from the record. A displaced session that rereads coordination therefore
   > learns the current generation but cannot present the current token.

   Without this, a displaced session reading coordination before its next
   mutation, which the transition lock already does, can present the current
   token, and the two-part fence degrades to option B's generation-only fence
   while keeping option A's cost.

2. State the fence's scope, which is currently unbounded. "Every mutating
   exchange command must present both generation and token" can be satisfied
   only by a session that ran resume, because ownership is acquired at step 7 of
   the resume sequence and nowhere else. Every `pw`-routed requestor and reviewer
   session holds no token. Decide and record one of:

   - the fence binds only for an exchange whose generation has been advanced by
     a pickup, and ordinary sessions keep today's signatures; or
   - every session acquires ownership when it claims a round, which is more
     uniform and changes every existing mutating command and its tests.

   Name the chosen rule in the failure and idempotency boundaries, and add the
   matching acceptance case, since case 14 covers only the displaced session.

3. Add a design question on two reviewers waiting for the same request, with
   these options: first claim wins through the existing locked compare-and-swap,
   with the loser returning to its wait on a typed already-claimed result; the
   request's recorded reviewer nature decides which waiter may claim; or both
   stop and ask the human. Recommended answer, the first, because it reuses the
   fence the design already defines, keeps the losing reviewer available rather
   than stopping it, and stays consistent with the requirement's Q11, which
   reserves human selection for one reviewer facing several requests rather than
   several reviewers facing one. Add an acceptance case for the losing waiter.

4. Give the appended transcript identity-completion entry a heading rule in the
   answer to Q04 and in the legacy backfill section:

   > The completion entry is appended with a heading qualified by the role and
   > the exchange occurrence it completes, so repeated completions across roles,
   > occurrences, and later resumes remain unique within one transcript.

   Transcript heading uniqueness is enforced document-wide in this repository
   and may not be relaxed, and a completion entry is reachable more than once
   per transcript.

Wording-only, worth applying in the same pass: in the answer to Q02, name the
same durable identity appearing in two inspected locations with different bytes
as the ambiguity case, rather than leaving it inside the general word
"ambiguity".

### Writer instructions for design-specification review-resume-command round 1

Apply the four requested changes and publish round 2. Do not consolidate: two of
them decide behavior the design currently leaves unimplementable, so this is
more than a wording pass.

Order of work:

1. Settle the fence scope first, change 2. It is the widest-reaching decision in
   the document, because the uniform reading changes every mutating command
   signature and every existing exchange test, while the pickup-only reading
   leaves today's surfaces intact. Changes 1 and 3 both read more clearly once
   that scope is fixed.
2. Apply the token digest, change 1. Keep the generation exactly as it is: it is
   the part that gives ordering and typed stale-session diagnostics, and only
   the token's storage is wrong.
3. Add the two-waiter question, change 3, with its acceptance case. Place it
   after Q06, since it follows from the identity-free wait that Q06 designs.
4. Apply the transcript heading rule, change 4, and the Q02 wording note.
5. Recheck the acceptance cases against the amended text. Case 14 covers
   displacement only, and after changes 2 and 3 there are two more behaviors to
   pin: an ordinary session mutating under the chosen fence scope, and a losing
   waiter returning to its wait.

If you disagree with the two-waiter recommendation or with the fence scope I
lean toward, say so in the next request with the reason. Both are live design
choices, not corrections of settled fact. The token digest is not in that
category: as written the design claims a property the mechanism does not have,
and that needs fixing whichever way the other choices go.

Leave the rest alone. The registry, the migration transaction, the two-role
snapshot, schema 2, role resolution, and both continuations were assessed this
round and need no change.

### Final reviewer decision for design-specification review-resume-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-01T17:55:15+02:00
- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for design-specification review-resume-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-resume-command.md
Review round: 2

### Requestor assessment for design-specification review-resume-command (round 2)

The design still covers the complete consolidated feature-request scope, and
all four round-1 change groups are applied. Ownership is now a uniform claim for
ordinary and resumed actors, coordination stores only a token digest, and the
secret stays with the claiming session. The transcript completion heading is
qualified by role and exchange occurrence, and duplicate durable identities
with different bytes are explicitly a migration ambiguity.

The reviewer-race gap now has Q07, whose recommended first-claim-wins answer is
also integrated into reviewer continuation and acceptance cases. All seven
questions have distinct options and recommended answers. I found no additional
design question after applying the reviewer feedback and no requirement or plan
scope was reopened. Every round-1 wording suggestion was applied.

### Change summary for design-specification review-resume-command (round 2)

Since round 1, the ownership fence stores a digest instead of a plaintext token
and every ordinary or resumed actor obtains a generation and secret through the
same locked claim. Failure and acceptance sections cover missing, stale, and
invalid capabilities without breaking normal workflows.

The legacy transcript completion now has a unique role-and-occurrence heading,
Q02 names different bytes for one durable identity as migration ambiguity, and
new Q07 settles simultaneous reviewer waiters through first atomic claim, typed
`already-claimed`, and return to global waiting. Matching body and acceptance
cases were added.

### Writer response for design-specification review-resume-command (round 2)

Writer response: I accept all round-1 findings. For the fence-scope choice, I selected the
uniform option: every ordinary and resumed actor claims a generation and secret,
so existing workflows gain the same enforceable transition contract instead of
a pickup-only exception. The token is now session-held with only its digest in
coordination. The reviewer-race question uses the recommended first-claim-wins
answer, and all requested transcript, migration, failure, and acceptance wording
is present. Please assess the amended seven-question design for convergence.

### Reviewer focus for design-specification review-resume-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-01T17:59:33+02:00
- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for design-specification review-resume-command round 2

Round 2 assesses the amended design. All four round-1 change groups are applied,
and applied at the level where the problem actually sat rather than as a note
elsewhere.

- The fence scope is settled, and the writer took the uniform option rather than
  the pickup-only exception: `start`, `reclaim`, an exact wait that wakes for
  its actor, and a global wait that selects a request all perform the locked
  claim, so an ordinary `pw`-routed session obtains a capability through the
  same path as a resumed one. Acceptance case 15 covers exactly that, which was
  the case round 1 said the design would otherwise stop.
- The token is now a digest in coordination with the secret returned only to the
  claiming session's machine result, and the answer to Q05 carries the same
  statement. This restores the property the option's rationale claims, since a
  displaced session that rereads coordination now learns the generation and
  cannot reproduce the secret.
- Q07 was added, its options are materially distinct, and its recommended answer
  is first-claim-wins with a typed `already-claimed` loser that returns to its
  wait. Acceptance case 18 pins the behavior.
- The transcript completion entry now has a heading,
  `### LLM nature completion for <role> (exchange <occurrence>)`. The two
  qualifiers are the right ones: role and occurrence are what can repeat within
  one transcript, and the idempotency boundary prevents a second completion for
  the same pair, so uniqueness holds rather than merely being asserted.
- The Q02 ambiguity case now names the same durable identity in two locations
  with different bytes.

Seven questions now cover the structural choices, and I agree with every
recommended option. No question is missing.

One consequence of the uniform fence is unstated, and it is the only thing this
round asks for. The design lists where a capability is acquired but never says
how a session that holds none acquires one on a live exchange. Two reachable
situations need that path. A later requestor session arriving at the durable
convergence gate holds no capability, because it never ran the wait that would
have claimed one, and the gate is explicitly designed to outlive the session
that reached it. Separately, a session whose capability is lost mid-round, which
for an LLM session means its context no longer carries the secret, cannot
mutate. In both cases `reclaim` does not apply, since it is reserved for a round
abandoned through lease expiry, so the only path is a direct resume pickup.

That path already exists and is already authorized to claim while the previous
lease is fresh, so this is naming a designed mechanism for two cases the text
does not mention, not adding a new one. Without it a reader concludes the human
gate is unreachable from a fresh session and that a lost secret means waiting
out a five-hour lease, and both conclusions would be wrong.

### Question verdicts for design-specification review-resume-command round 2

**Agreement on all seven questions.** My answer matches the design's
recommendation for each: Q01-A, Q02-A, Q03-A, Q04-A, Q05-A, Q06-A, and the new
Q07-A. The round-1 verdicts on Q01, Q02, Q03, and Q06 stand unchanged, and the
three questions touched this round are covered below.

- Q04, transcript identity completion. The added heading,
  `### LLM nature completion for <role> (exchange <occurrence>)`, is correct and
  its qualifiers are the right pair. Role and occurrence are the two dimensions
  that can repeat within one transcript, and the idempotency boundary already
  prevents a second completion for the same role and occurrence, so uniqueness
  follows from the design rather than from a promise. It also matches the
  qualifier style the protocol already uses for rounds and exchanges, which
  matters because a reader of the transcript should not have to learn a second
  convention.
- Q05, fencing a displaced session. Both round-1 problems are fixed. The digest
  restores the property the answer claims, and the uniform claim removes the
  reading under which no ordinary session could publish. I agree with the
  writer's choice of the uniform option over the pickup-only exception: it costs
  more in existing command signatures and tests, and it buys one transition
  contract instead of two behaviors that would diverge under maintenance. The
  one thing it leaves unstated is the re-claim path, covered below.
- Q07, competing reviewer waits. Option A is right and is the answer I
  recommended. The options are materially distinct and each con is honest,
  including A's admission that the winner depends on scheduling. That is the
  correct trade: the alternative that looks fairer, reserving a request for a
  recorded reviewer nature, fails exactly when it matters, because a new request
  has no reviewer recorded yet and a recorded one may name a session that is no
  longer running. Returning the loser to its wait rather than stopping it keeps
  the reviewer pool available, which is the point of an identity-free wait.

**No missing question.** Q07 closed the gap round 1 raised, and the amendments
open no further structural choice. The remaining item is a path that already
exists in the design rather than a decision between alternatives, so it belongs
in the covered wording and not in an eighth question.

**One unstated path, carried as covered wording.** The design names four claim
points and never says how a session holding no capability acquires one on a live
exchange. Two situations reach that state. A later requestor session at the
durable convergence gate never ran the wait that claims, and that gate is
designed to outlive the session that reached it; the shared requestor contract
even anticipates a later session finding the pending authorization again.
Separately, a session that loses its secret mid-round, which for an LLM session
means the value is no longer in its context, cannot present it. `reclaim` covers
neither, since it applies to a round abandoned through lease expiry rather than
to a live one. Direct resume already claims on a live exchange, so it is the
answer in both cases and only needs saying.

### Convergence evidence for design-specification review-resume-command round 2

Covered wording: one addition to the lease-independent pickup section, naming the re-claim path
for a session that holds no capability on a live exchange:

> A session holding no capability for a live exchange acquires one through a
> direct resume pickup, which is authorized to claim while the previous lease is
> fresh. Two ordinary situations reach that state: a later session that arrives
> at the durable convergence gate without having run the wait that claims, and a
> session whose secret is no longer available to it mid-round. `reclaim` does
> not cover either, since it applies to a round abandoned through lease expiry.
> Neither situation requires waiting for the lease to lapse.

Add the matching acceptance case beside case 15:

> A session holding no capability picks up a live exchange through direct
> resume, advances the generation, and completes the mutation its role owns,
> including a human confirmation at the convergence gate.

Nothing else needs to change. The digest, the uniform claim, the transcript
completion heading, the Q02 ambiguity case, and Q07 with acceptance case 18 are
all applied as requested, and the seven questions and their answers are
sufficient to consolidate.

Two notes for consolidation rather than edits. The uniform fence changes the
signature of every mutating exchange command, so the implementation plan built
from this design should treat that as its own slice with the existing exchange,
requestor, reviewer, and status suites updated together, rather than folding it
into the artifact-home work. And acceptance case 21 already promises the
regression sweep; whoever writes the plan should keep it attached to the fence
slice, since that is the change most likely to break shipped tests.

Convergence rationale: every structural choice in this design is settled, and what remains is one
sentence naming a mechanism the design already has.

Round 1 raised four things. Two of them made the design unimplementable as
written: the token stored in plaintext did not deliver the property its own
rationale claimed, and an unbounded fence would have stopped every ordinary
`pw`-routed session from publishing. Both are fixed at the source, the digest in
the coordination record and the uniform claim shared by ordinary and resumed
actors, with acceptance case 15 pinning the ordinary path. The reviewer race
became Q07 with the recommended first-claim-wins answer and acceptance case 18,
and the transcript completion entry gained a heading whose role and occurrence
qualifiers are provably unique given the idempotency boundary.

The writer also took the more expensive of the two fence options deliberately,
choosing one transition contract over a pickup-only exception. That is the right
call for a protocol whose two behaviors would otherwise drift apart under
maintenance, and it is recorded plainly in the answer rather than left implicit.

What remains is not a decision between alternatives. Direct resume already
claims on a live exchange; the design simply does not say that this is the path
for a session holding no capability, and does not name the two situations that
reach that state. Adding it changes no option, no answer, no schema, and no
command, which is what separates a wording pass from another review round.

This recommendation is advisory. It does not authorize consolidation, and the
choice stays with the human at the convergence gate.

### Writer instructions for design-specification review-resume-command round 2

Stop at the convergence gate and present the human with the identity summary,
this recommendation, the amended design, and your own assessment. The
recommendation is advisory: only the human chooses `Consolidate` or `Revise and
review again`.

If the human selects `Consolidate`:

1. Add the re-claim paragraph and its acceptance case from the covered wording
   before folding the questions into the design body, so the ownership section
   is complete when it becomes the decision record.
2. Fold the seven answers into the design decisions table, keeping the existing
   row order and adding rows for the uniform claim and for Q07.
3. When the implementation plan is written from this design, keep the ownership
   fence as its own slice. It changes the signature of every mutating exchange
   command, and acceptance case 21's regression sweep belongs with that slice
   rather than with the artifact-home work.
4. Carry the two-observation-mechanism cost from Q06 into the plan's test
   planning. The design accepts notification plus polling, and the concurrency
   cases it implies are easy to lose between a design and a plan.

If the human selects `Revise and review again`, the re-claim paragraph is the
only outstanding reviewer finding; any further change is the human's or your
own, not this round's.

Leave the rest alone. The registry, the migration transaction, the two-role
snapshot, schema 2, role resolution, both continuations, and the seven questions
were assessed across two rounds and need no further change.

### Final reviewer decision for design-specification review-resume-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-01T19:03:16+02:00
- Exchange: specification/design-specification/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-resume-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
