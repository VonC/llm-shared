# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-01T13:48:19+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for feature-request review-resume-command (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
Review round: 1

### Requestor assessment for feature-request review-resume-command (round 1)

The feature request captures the user-visible behavior, compatibility rules,
role-specific continuation boundaries, migration safety, and cross-cutting test
impact. Its eleven open questions expose the remaining scope and edge-case
decisions I found; I did not identify an additional unanswered requirement
question during this pass. Each question provides distinct options, tradeoffs,
and a recommended answer sufficient for independent review. There are no
earlier reviewer wording suggestions in round 1, so none have yet been applied.

### Change summary for feature-request review-resume-command (round 1)

Round 1 introduces the feature request from the approved canonical draft. It
defines configurable review-artifact storage and migration, LLM-nature tracing
and legacy backfill, role resolution, reviewer and requestor resume behavior,
recovery safeguards, acceptance criteria, dependencies, and eleven open
questions for unresolved product behavior.

### Writer response for feature-request review-resume-command (round 1)

Writer response: Please independently assess whether the feature request captures every stated
resume, migration, identity, compatibility, waiting, and workflow-continuation
rule. Please also evaluate whether the eleven questions cover the remaining
ambiguities and whether their options and recommended answers are precise
enough to consolidate without adding design choices.

### Reviewer focus for feature-request review-resume-command (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-01T14:13:54+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for feature-request review-resume-command round 1

Round 1 assesses `docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md`
and its eleven open questions. The body states the resume behavior, the
migration preflight, the LLM-nature trace, the legacy artifact policy, both
role continuations, fifteen acceptance criteria, and the dependency set. The
questions are well formed: each names a real decision, offers three materially
distinct options with consequences on both sides, and records a reasoned
recommendation. I agree with all eleven recommended options and would answer
each the same way.

Two problems keep this round from converging, and neither is about the answers.

First, the requirement changes two rules the umbrella states for items already
marked completed, and never says the umbrella is amended. The umbrella's first
item states that transient `a.review-requested.*` and `a.review-answer.*` files
stay at the project root and rely on the existing `a.*` ignore rule; this
feature moves them below a configured home. The umbrella's tenth item regroups
"a repository-root `rvw_resume` command, its launcher and shared
implementation"; this feature forbids exactly that command. The reasoning given
for the second change is sound, since a shell command cannot continue an LLM
session, but a requirement that contradicts its own umbrella without saying so
leaves two live documents disagreeing about the deliverable.

Second, three decisions the body already depends on are not asked anywhere. The
configured home has no stated ignore coverage, and the shared core refuses to
activate an exchange whose transient paths are not effectively ignored, so this
one is blocking rather than theoretical. The durable artifact-home setting has
no named carrier, and the carrier decides whether Q03's own rationale holds. The
migration outcome has no place in the typed status result that the tenth
umbrella item promises resume can consume without scraping prose.

The eleven existing questions need no change beyond four small precision fixes
noted per question. The requested work is the two supersession statements and
three added questions, which is more than a wording pass.

### Question verdicts for feature-request review-resume-command round 1

**Agreement on the eleven existing questions.** My answer matches the plan's
recommendation for every one: Q01-A, Q02-B, Q03-A, Q04-A, Q05-A, Q06-A, Q07-A,
Q08-A, Q09-A, Q10-A, Q11-A. Notes below cover only the four that need a
precision fix; Q02, Q05, Q06, Q07, Q09, Q10, and Q11 need nothing.

- Q01, artifact home membership. Option Q01-A is right: transcripts are
  documentation with a stable location and no reason to move. The answer states
  the boundary against a rule the umbrella writes for a completed item, that
  transient files stay at the project root under the `a.*` ignore rule. Say in
  the answer that this feature supersedes that placement rule for runtime
  artifacts, so the two documents stop disagreeing.
- Q03, per-session override. Option Q03-A is right, and its rationale is the
  reason the carrier matters: every participant must derive the same location
  across sessions and machines. The setting's file is never named, and the
  choice is not neutral. The opt-in marker `a.review-mode` is itself ignored, so
  a setting placed there is per-clone and cannot give two machines the same
  location, while the validation declaration `.review-validation` is versioned
  precisely so every contributor reads the same obligation. Q13 below asks for
  that decision; Q03 itself needs only a pointer to it.
- Q04, automatic status migration. Option Q04-A is right, and the body already
  records it as the single accepted exception to the read-only contract. Two
  delivered surfaces state the old contract in words that become false:
  `instructions/review-status-command.md` opens with "This workflow is strictly
  read-only", and the published skill description says it reports exchanges
  "without resuming or mutating them". Acceptance criterion 15 lists tests and
  documentation topics but neither of those. Name them.
- Q08, backfill breadth. Option Q08-A is right. The body's legacy policy says
  the update "is role-wide: it is not limited to the first legacy artifact",
  with no scope bound, while the answer limits it to the selected exchange
  occurrence. Add the occurrence bound to the body sentence so the two agree.

**Missing question, ignore coverage for the configured artifact home.** This one
blocks implementation rather than merely leaving it undecided. What makes the
current transient artifacts invisible to Git is the root `a.*` rule, and the
shared core enforces that: activation submits every transient path through one
`git check-ignore` query and fails with "review transient paths are not
effectively ignored" when any path is not covered. A file moved to
`.reviews/a.review-requested.*` is not matched by a root `a.*` rule, so with no
further decision the first `activate` after migration fails, and a repository
that ignores the failure starts tracking protocol artifacts. Options worth
stating: ship a repository `.gitignore` entry for the configured home; have the
home created with its own `.gitignore` inside it; or extend the ignore-coverage
validation to accept the resolved home without a Git rule. My recommendation is
the second, a `.gitignore` written inside the directory when it is created,
because it travels with a configured home wherever it points and keeps the
existing validation honest instead of teaching it an exception. Migration must
create that file before it moves anything, and the preflight must treat its
absence as a blocking layout rather than a safe move.

**Missing question, where the durable artifact-home setting lives.** Q03 settles
that one durable repository setting wins over session overrides, and the body
never says which file holds it or in what format. The repository already has two
patterns with opposite properties: the ignored root marker `a.review-mode`,
which carries `wait_timeout_seconds` per clone, and the versioned
`.review-validation`, which states a repository-wide obligation every
contributor reads. Options: extend the ignored marker; add a versioned
declaration; or reuse an existing versioned project settings file. My
recommendation is a versioned declaration, because Q03-A's stated reason is that
every participant derives the same location without shared shell state, and an
ignored file cannot deliver that across clones. The answer should also say what
happens when the setting names a path outside the repository or an existing
tracked directory.

**Missing question, how the typed status result reports migration.** The tenth
umbrella item promises a stable result that resume consumes without scraping
prose, and the shipped result is a versioned schema whose outcome takes exactly
three values mapped to process status 0, 3, and 2, with validated invariants
between outcome, entries, and the error flag. The body says status reports
whether migration was unnecessary, completed, or blocked, without saying where
that lands in the result or what a blocked migration returns as an exit status.
Options: add a typed migration section to the result and bump the schema
version; represent a blocked migration as the existing operational-failure
outcome with a diagnostic; or keep migration reporting in human output only. My
recommendation is the first plus the second together: a typed migration record
for the unnecessary and completed cases, and the existing operational-failure
outcome for a blocked one, since a blocked layout genuinely prevented a
trustworthy query. Whichever is chosen, the answer should say whether the schema
version changes, because resume and the status renderers read it.

**Optional question the writer may prefer to defer.** Recovery safety authorizes
lease-independent pickup while the recorded lease is still current, and the body
does not say what happens to a session that is still holding it. Two sessions
can then act in the same role, and the transition lock bounds the damage without
resolving the ownership. If the writer wants it settled here rather than in
design, the useful options are recording the pickup so the displaced session
fails its next transition with a clear diagnostic, leaving the collision to the
transition lock, or requiring the human to confirm that the previous session has
stopped. My recommendation is the first. I am not requesting this one; it is the
weakest of the four and the umbrella already grants the pickup authority.

### Requested changes for feature-request review-resume-command round 1

Requested changes: apply two supersession statements, three added questions, and four precision
fixes to `docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md`.

1. State both umbrella supersessions in "Scope boundaries and dependencies",
   which currently says only what this effort does not reopen:

   > This effort supersedes two rules the umbrella draft states for earlier
   > items: runtime protocol artifacts no longer stay directly at the project
   > root under the `a.*` ignore rule, and the resume entry point is an LLM
   > skill rather than the repository-root `rvw_resume` command the umbrella
   > regroups for this item, because continuation requires an active LLM
   > session. The umbrella draft is updated with both revisions; no completed
   > requirement, design, plan, or validation document is reopened.

   Update the matching umbrella text in `docs/v0.11.0/draft.v0.11.0.review-mode.md`
   in the same pass, so the two documents stop disagreeing about the
   deliverable.

2. Add a question on ignore coverage for the configured artifact home, with
   these options: a repository `.gitignore` entry for the configured home; a
   `.gitignore` written inside the home when it is created; or extending the
   ignore-coverage validation to accept the resolved home with no Git rule.
   Recommended answer, the second, because it travels with a configured home
   wherever it points and leaves the existing validation unchanged. The answer
   must also say that migration writes that file before moving anything and
   that the preflight reports a missing rule as a blocking layout. This is the
   one blocking gap: the shared core submits every transient path through one
   `git check-ignore` query at activation and fails when a path is not covered,
   so without this decision the first activation after migration fails.

3. Add a question on where the durable artifact-home setting lives, with these
   options: the ignored root marker `a.review-mode`; a new versioned
   declaration beside `.review-validation`; or an existing versioned project
   settings file. Recommended answer, a versioned declaration, because Q03-A
   rests on every participant deriving the same location without shared shell
   state, which an ignored per-clone file cannot deliver. Include what happens
   when the setting names a path outside the repository or an existing tracked
   directory.

4. Add a question on how the typed status result reports migration, with these
   options: a typed migration record plus a schema version bump; reuse of the
   existing operational-failure outcome for a blocked layout; or human-readable
   reporting only. Recommended answer, the first two together, with the answer
   stating explicitly whether the schema version changes, since resume and the
   status renderers read it.

5. Four precision fixes:

   - In the legacy policy, bound the role-wide sentence to the scope Q08-A
     sets: "The update covers every missing-nature artifact attributed to that
     role in the selected exchange occurrence, not only the first legacy
     artifact the workflow happens to read."
   - In acceptance criterion 15, add the canonical status instruction and the
     published skill description to the updated surfaces. Both state the
     strictly read-only contract that Q04-A changes.
   - Replace `rwst` with `rvw_status` in the migration preflight section and in
     acceptance criterion 5. `rwst` is a local doskey alias defined in
     `senv.doskey`; the command the umbrella and the shipped launcher name is
     `rvw_status`. Mention the alias once if it is useful, rather than in a
     criterion that tests key on.
   - In the answer to Q01, add one clause naming the umbrella placement rule
     this boundary supersedes, so the answer and edit 1 agree.

Optional, not requested: the recovery-safety section authorizes
lease-independent pickup while a lease is still current and does not say what
happens to a session still holding it. If you want that settled at requirement
level rather than in design, the verdicts note carries options and a
recommendation.

### Writer instructions for feature-request review-resume-command round 1

Apply the five requested changes, then publish round 2. Do not consolidate: two
umbrella supersessions and three added questions are more than a wording pass.

Order of work:

1. Write the two supersession statements first, and amend the umbrella draft in
   the same pass. Both edits are factual records of decisions this feature has
   already made, so neither needs a new option set.
2. Add the ignore-coverage question next. It is the one gap that blocks
   implementation rather than leaving it open: activation refuses transient
   paths that are not effectively ignored, so the artifact home needs a rule
   before any migration can run. Its answer also constrains the migration order,
   since the ignore rule has to exist before artifacts move.
3. Add the setting-carrier and status-result questions. The carrier answer feeds
   the acceptance criteria, which currently say "with a configured artifact
   home" without saying where the configuration is read from.
4. Apply the four precision fixes. The `rvw_status` correction matters most in
   acceptance criterion 5, because criteria drive tests.
5. Recheck the acceptance criteria against the three new answers. Criteria 1
   through 5 describe placement and migration without covering ignore coverage
   or the setting's location, and criterion 5 describes status migration without
   covering how the result reports it. Add or amend criteria rather than leaving
   the new answers untested.

If you disagree with any of the three recommended answers, say so in the next
request with the reason. They are reviewer recommendations over live choices,
not corrections of settled facts. The eleven existing questions need no change
beyond the precision fixes; their options and answers are sufficient to
consolidate once the additions are in place.

### Final reviewer decision for feature-request review-resume-command round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-01T14:55:25+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for feature-request review-resume-command (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
Review round: 2

### Requestor assessment for feature-request review-resume-command (round 2)

The feature request now contains fourteen open questions. The three questions
missing in round 1 cover effective Git ignore coverage, the durable setting
carrier and invalid paths, and typed status migration reporting. All requested
supersession and precision wording is present in the requirement and umbrella,
and the acceptance criteria cover the new decisions. The existing and added
options and answers are sufficient for independent review. Every requested
reviewer wording change was applied; the optional lease-displacement question
was explicitly not requested and remains available for design without blocking
this requirement round.

### Change summary for feature-request review-resume-command (round 2)

Since round 1, the requirement and umbrella now record both superseded rules,
bound role-wide identity updates to one exchange occurrence, use `rvw_status`
as the shipped command name, identify the status instruction and skill wording
that must change, and add three acceptance criteria. Q01, Q03, Q04, and Q08 were
made precise. Q12 through Q14 now settle ignore coverage, the versioned setting
carrier, and typed migration reporting. Reviewer idle behavior was also made
explicitly global across future specification and code requests even before an
exchange or implementation step exists.

### Writer response for feature-request review-resume-command (round 2)

Writer response: All five requested change groups are accepted and applied, with no
disagreement. The umbrella and requirement now state both supersessions; Q12,
Q13, and Q14 use the reviewer's recommended answers; the four precision fixes
and matching acceptance criteria are present. The optional live-lease
displacement question was not requested and is deferred. Please assess the
updated fourteen-question requirement and the newly explicit idle global
reviewer wait for convergence.

### Reviewer focus for feature-request review-resume-command (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-01T14:59:18+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for feature-request review-resume-command round 2

Round 2 assesses the amended requirement and the umbrella changes it carries.
All five round-1 request groups were applied, and applied where they belong
rather than as an afterthought.

- Both supersessions are recorded twice, once in the requirement's scope
  boundaries and once in the umbrella draft, which gained a cross-cutting
  section and had items 1, 6, 9, and 10 amended in place. Item 9 now says status
  stays read-only after the bounded migration preflight, and item 10 no longer
  regroups a repository-root `rvw_resume` command. The completed status rows
  were left untouched, which is the boundary the requirement claims to respect.
- Q12 settles ignore coverage with a home-local rule created before any artifact
  moves, which keeps the existing activation check unchanged rather than
  teaching it an exception.
- Q13 settles the carrier as a dedicated versioned declaration and adds the
  repository-boundary validation, so a path outside the repository or an
  existing tracked directory is rejected.
- Q14 settles typed reporting by combining a typed migration record and schema
  advance for the unnecessary and completed cases with the existing
  operational-failure outcome for a blocked one.
- The four precision fixes are present: the backfill sentence is bound to the
  selected exchange occurrence, criterion 15 names the canonical status
  instruction and the skill description, `rvw_status` replaced the alias in the
  preflight section and criterion 5 while the alias survives as one parenthetical
  mention, and the Q01 answer names the placement rule it supersedes.
- Three acceptance criteria were added, one per new question, so each new answer
  is testable rather than recorded only in prose.

Fourteen questions now cover the decisions this requirement depends on. I agree
with every recommended option and would answer each the same way. No further
question is missing: the deferred live-lease displacement case was the one I
marked optional, and deferring it to design is a reasonable call that blocks
nothing here.

Three wording clarifications remain, all inside the new material and none of
them changing an option, an answer, or a criterion's substance. They are listed
in the covered wording for consolidation.

One note for the record rather than a finding: the change summary says reviewer
idle behavior was made explicitly global this round, while that text already
stood in the round-1 document. The current wording is correct either way.

### Question verdicts for feature-request review-resume-command round 2

**Agreement on all fourteen questions.** My answer matches the document's
recommendation for each: Q01-A, Q02-B, Q03-A, Q04-A, Q05-A, Q06-A, Q07-A,
Q08-A, Q09-A, Q10-A, Q11-A, Q12-B, Q13-B, and Q14-A with Q14-B together. The
eleven original questions carried no change requests this round beyond the four
precision fixes, and those are applied.

- Q12, ignore coverage. Option Q12-B is right. A home-local rule follows a
  configured home wherever it points, and it keeps activation's existing
  `git check-ignore` validation intact instead of adding an exception that would
  weaken the same check for every other transient path. The answer also fixes
  the ordering, so coverage exists before anything moves.
- Q13, setting carrier. Option Q13-B is right, and for the reason Q03-A already
  gave: a per-clone ignored marker cannot give two machines the same location,
  while a versioned declaration can. The added repository-boundary validation
  closes the case where the setting points outside the repository or at tracked
  work.
- Q14, typed migration reporting. Accepting Q14-A and Q14-B together is right.
  A blocked layout genuinely prevented a trustworthy projection, so the existing
  operational-failure outcome already carries the correct meaning and needs only
  a migration diagnostic, while the unnecessary and completed cases are new
  information that resume must read rather than infer. Recording the schema
  advance in the answer matters, since both renderers and resume key on it.
- Q01, Q03, Q04, and Q08 verdicts from round 1 stand, with their precision fixes
  now in place: Q01 names the superseded placement rule, Q03 points at Q13 for
  the carrier, Q04 uses the shipped command name, and the legacy policy bounds
  the backfill to the selected exchange occurrence.
- Q02, Q05, Q06, Q07, Q09, Q10, and Q11 are unchanged and need nothing.

**No missing question.** The three gaps from round 1 are closed, and the new
answers open no further requirement-level choice. The live-lease displacement
case stays deferred, which I marked optional and do not request: the umbrella
already grants the pickup authority, and the transition lock bounds the
collision until design settles it.

**Three wording clarifications for consolidation.** Each restates a decision
already made.

- The Q12 answer and criterion 16 read as two rules that could look opposed:
  migration creates the coverage before moving anything, and a missing rule
  blocks. They agree once the two paths are separated, so say it directly: when
  the home does not yet exist, creation establishes coverage; when a home
  already exists without it, the preflight blocks instead of adding it silently.
- Q13-B names "a dedicated versioned repository declaration beside
  `.review-validation`" without naming the file. This document names `.reviews`,
  `a.review-mode`, and `.review-validation` elsewhere, so either name it too or
  say the exact name is left to design.
- The Q12 answer does not say whether the home-local `.gitignore` is itself
  tracked or ignored by its own rule. That decides whether a fresh clone starts
  with coverage or establishes it on first use. One clause settles it, and
  design can pick the mechanism.

### Convergence evidence for feature-request review-resume-command round 2

Covered wording: three clarifications, all inside the new Q12 through Q14 material, to apply
during consolidation.

1. Separate the create path from the repair path in the answer to Q12, so the
   creation rule and the blocking rule cannot read as opposed:

   > Migration creates the home and its ignore rule before moving anything. A
   > home that already exists without effective coverage is a blocking layout:
   > `migration_check` reports it rather than adding the rule on its behalf.

   Criterion 16 already states both halves and needs no change once the answer
   says which path each one governs.

2. In the answer to Q13, either name the versioned declaration file as this
   document names `.reviews`, `a.review-mode`, and `.review-validation`, or add
   one clause saying the exact name is left to design. Either is fine; silence
   is what leaves a reader guessing whether it was decided.

3. In the answer to Q12, add one clause saying whether the home-local
   `.gitignore` is itself tracked or covered by its own rule. That decides
   whether a fresh clone starts with coverage or establishes it on first use.

None of the three changes an option, an answer, an acceptance criterion, or a
dependency. The requirement can be consolidated with them applied in the same
pass.

For consolidation itself, the fourteen answers become the decision record for
this requirement: the artifact home and its default, the bounded three-location
preflight, one durable setting with no session override, automatic safe
migration from status, atomic migration, the role question when both traces
match, no unknown backfill, occurrence-scoped backfill, attempt-scoped override,
the open-ended reviewer wait, explicit selection among concurrent requests, the
home-local ignore rule, the versioned setting carrier, and the typed migration
result with its schema advance.

Convergence rationale: every decision this requirement depends on is now settled, and what remains is
wording.

Round 1 found two problems: the requirement changed two umbrella rules without
saying so, and three decisions the body already depended on were asked nowhere.
Round 2 closed both. The supersessions are recorded in the requirement and in
the umbrella draft, with items 1, 6, 9, and 10 amended in place and no completed
row reopened. The three gaps became Q12, Q13, and Q14, each with three distinct
options, a reasoned recommendation, and a matching acceptance criterion, so the
new answers are testable rather than recorded only in prose.

Ignore coverage was the one blocking gap, because activation refuses transient
paths that are not effectively ignored and the root `a.*` rule does not reach a
subdirectory. Q12 closes it with a home-local rule created before any artifact
moves, which keeps the existing validation unchanged.

The three remaining clarifications sit inside the new material and restate
decisions already made: which path the create rule and the blocking rule each
govern, whether the versioned declaration is named here or in design, and
whether the home-local ignore file is tracked. None of them changes an option,
an answer, a criterion, or a dependency, which is what separates a wording pass
from another review round.

This recommendation is advisory. It does not authorize consolidation, and the
choice between consolidating and running another round stays with the human at
the convergence gate.

### Writer instructions for feature-request review-resume-command round 2

Stop at the convergence gate and present the human with the identity summary,
this recommendation, the amended requirement and umbrella, and your own
assessment. The reviewer recommendation is advisory: only the human chooses
`Consolidate` or `Revise and review again`.

If the human selects `Consolidate`:

1. Apply the three covered-wording clarifications first, so the consolidated
   decision record does not carry the create-versus-repair ambiguity into
   design.
2. Fold the fourteen answers into the requirement body and its decision record,
   keeping each acceptance criterion beside the answer it tests. Criteria 16
   through 18 already pair with Q12 through Q14; check that the eleven earlier
   answers have the same pairing before closing the section.
3. Keep the umbrella and the requirement in step. Both now carry the two
   supersessions, so a later edit to one without the other reopens the
   disagreement this round closed.
4. Carry the deferred live-lease displacement case into the design phase as a
   named open point rather than dropping it. It is not a requirement-level
   blocker, and it should not disappear because it was deferred here.

If the human selects `Revise and review again`, the three clarifications are the
only outstanding reviewer findings; any further change is the human's or your
own, not this round's.

### Final reviewer decision for feature-request review-resume-command round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-01T15:22:45+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor (exchange 2)

- Recorded: 2026-09-01T16:56:45+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: request

### Review identity for feature-request review-resume-command (round 1, exchange 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
Review round: 1

### Requestor assessment for feature-request review-resume-command (round 1, exchange 2)

The reopened requirement remains settled at fourteen clarifications and has no
new open question. The human override identifies one missing scope statement:
the global reviewer wait must be enterable not only before an exchange exists,
but also after an exchange concludes and while a live exchange belongs to the
requestor or the human convergence gate. The requirement, canonical child
draft, and umbrella now name all three entry situations and both wake cases.
Acceptance criterion 12 and the Q10 clarification row cover the same behavior.
The existing options and answers remain sufficient. All reviewer-authored
wording was accepted; trailing whitespace was removed and the decision record
was aligned before publication.

### Change summary for feature-request review-resume-command (round 1, exchange 2)

Since occurrence 1 was consolidated, the reviewer continuation text was
reopened by explicit human guidance. Three documents now state that the global
wait can begin before an exchange exists, after the reviewer's exchange has
concluded, or while the live exchange belongs to the requestor or human gate.
They also state that the wait wakes for a later request in the same exchange or
for a request opening a new exchange. Acceptance criterion 12 and the Q10
clarification row were updated to match. No design document was created.

### Human guidance and writer response for feature-request review-resume-command (round 1, exchange 2)

Human guidance:

The human chose `Revise and review again`, overriding the reviewer's
convergence recommendation. Round 3 must close one gap in the reviewer wait
scope, in addition to the three clarifications already listed in the round-2
covered wording.

The intended workflow is that a reviewer can wait for the next request whether
or not one is pending: after its exchange has concluded, and while the current
exchange is live but its next action belongs to the requestor or to the human
convergence gate. All three documents state a rule broad enough to cover that,
in the draft's role-specific waiting section, in the requirement's reviewer
continuation, and in umbrella item 10. What none of them does is name those two
situations, while all three name exactly one state as a valid entry point, the
idle exchange. Naming one state invites the narrow reading that only that state
qualifies.

Requested change for the reviewer continuation bullet in
`docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md`, with the same
correction applied to the matching draft line and to umbrella item 10:

> An idle exchange, an exchange that has concluded, and a live exchange whose
> next action belongs to the requestor or to the human convergence gate are all
> valid wait entry points. The wait wakes on the next request artifact whether
> it belongs to the same exchange resuming at a later round or occurrence, or to
> an exchange that did not exist when the wait started.

Acceptance criterion 12 must cover the two cases it does not test today: a
reviewer that keeps waiting after its own exchange concludes, and a reviewer
parked at a convergence gate that wakes on the replacement request when the
human chooses another round.

This override resets the no-progress counters. The reviewer's round-2 findings
stand and are not withdrawn: the three covered-wording clarifications should be
applied in the same round.

Writer response: The human reopened the feature-request scope and requested another review
occurrence. I accept the reviewer-authored amendment and widened the Q10
clarification row so the settled record matches the body and acceptance case.
Please assess whether the three entry situations, the two wake cases, and the
no-writer-work reviewer boundary now fully capture the override. Please also
check that no new requirement-level question is needed.

### Reviewer focus for feature-request review-resume-command (round 1, exchange 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1-exchange-2 -->

## Round 1 by reviewer (exchange 2)

- Recorded: 2026-09-01T16:59:47+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: answer

### Reviewer assessment for feature-request review-resume-command round 1 (exchange 2)

Independence limit for this round, stated first because it bears on how much
weight the verdict carries. The reviewer authored the wait-scope wording now
under review. The human directed that edit after the previous occurrence had
already consolidated, and the requestor accepted it unchanged, so this round's
verdict on that specific text is not an independent assessment of it. What
remains independent, and is what this answer actually checks: whether the
amendment covers the whole override, whether the three documents agree with each
other, whether the decision record and the acceptance criteria match the body,
and whether the change opens a new requirement-level question.

Coverage of the override is complete in the body text. All three documents now
name the same three entry situations, an idle exchange, a concluded exchange,
and a live exchange whose next action belongs to the requestor or to the human
convergence gate, and all three name both wake cases, a request that resumes the
same exchange at a later round or occurrence and a request that opens an
exchange which did not exist when the wait started. The requirement's reviewer
continuation, the child draft's role-specific waiting section, and umbrella item
10 agree in substance and in the order they list those cases.

The Q10 clarification row is the requestor's own work this round, so it is
assessed independently. It is accurate, and it is slightly broader than the
acceptance criterion beside it: the row names idle, concluded, requestor-owned,
and convergence-gate entry, while criterion 12 names entry before any exchange
starts, entry after the reviewer's own exchange concludes, and entry while
parked at a gate. The requestor-owned live exchange is missing from the
criterion alone.

That gap matters more than its size suggests, because the requestor-owned state
is the most frequent one: it is where every reviewer sits after publishing a
`changes-requested` answer, waiting for the replacement request. A criterion set
that tests the rare entry points and skips the common one would pass while the
behavior that runs on every intermediate round goes unverified. The fix is one
clause in criterion 12, which is why this round converges rather than requesting
another.

No new requirement-level question is needed. The entry situations and wake cases
are enumerated rather than left open, cancellation stays with Q10, and
concurrent requests stay with Q11, which already covers the case where a parked
wait sees its own exchange resume while another request also arrives. The
reviewer boundary against writer work is unchanged and still explicit.

### Question verdicts for feature-request review-resume-command round 1 (exchange 2)

**No open question remains in the reviewed specification.** The previous
occurrence consolidated all fourteen into the clarifications table, and this
occurrence adds none. My answers to those fourteen are unchanged from the
previous occurrence: Q01-A, Q02-B, Q03-A, Q04-A, Q05-A, Q06-A, Q07-A, Q08-A,
Q09-A, Q10-A, Q11-A, Q12-B, Q13-B, and Q14-A with Q14-B together. Nothing in the
amendment disturbs any of them.

**Q10's clarification row, widened this round by the writer.** I agree with it.
It now reads that the global reviewer wait stays active from idle, concluded,
requestor-owned, and convergence-gate states until a same-exchange or
new-exchange request arrives or the human cancels, and it adds idle-only entry
to the rejected alternatives. That last addition is the useful part: it records
why the narrow reading was wrong, so a later reader does not reintroduce it. The
row is the most complete statement of the rule in the document set.

**One coverage gap, in acceptance criterion 12 only.** The body and the Q10 row
name four states from which the wait may be entered. Criterion 12 names three
and omits the live exchange whose next action belongs to the requestor. The
requestor assessment for this round states that criterion 12 and the Q10 row
cover the same behavior; they do not quite, and the criterion is the half that
is short. The covered wording carries the clause that closes it.

**No missing question.** The widened scope enumerates its entry situations and
its wake cases rather than leaving either open, so it settles behavior instead
of opening a choice. Two cases that might look like new questions are already
owned elsewhere: cancelling a parked wait is Q10, and a parked wait that sees
both its own exchange resume and another request arrive is Q11, which lists them
and asks the human to select one.

**On the previous occurrence's deferred item.** The live-lease displacement case
was deferred to design at the end of the last occurrence, and this reopen did
not revive it. That remains the right call: it is a design-level safety question
and it blocks nothing in this requirement. It should reach the design document
rather than quietly disappear with the consolidated questions.

### Convergence evidence for feature-request review-resume-command round 1 (exchange 2)

Covered wording: one clause in acceptance criterion 12, so the criterion covers the same four
entry states as the body and the Q10 clarification row:

> Criterion 12:  A reviewer with a request reclaims and answers it; a reviewer without one
> waits globally for any future specification- or code-review request
> artifact without requiring its identity. That wait is entered before any
> exchange or implementation step starts, after the reviewer's own exchange
> has concluded, while the exchange's next action belongs to the requestor,
> and while the reviewer is parked at a convergence gate; in the last two
> cases it wakes on the replacement request when the requestor publishes it
> or when the human chooses another round.

The added state is the one every reviewer occupies after publishing a
`changes-requested` answer, so the criterion currently skips the entry point
that runs on every intermediate round while testing the rarer ones.

Nothing else needs to change. The reviewer continuation bullet, the child
draft's role-specific waiting section, umbrella item 10, and the Q10 row already
state the rule consistently, and no acceptance criterion other than 12 touches
the wait scope.

For the record this occurrence leaves behind: the working tree carries the
amendment across three documents, `feature-request.v0.11.0.review-resume-command.md`,
`draft.v0.11.0.review-resume-command.md`, and `draft.v0.11.0.review-mode.md`,
none of which is committed yet. Whoever consolidates should commit them together
with the criterion clause, since a partial commit would leave the umbrella and
the requirement disagreeing again, which is the condition the previous
occurrence closed.

Convergence rationale: the override is fully carried and what remains is one clause.

The human reopened this requirement for one reason: the global reviewer wait was
stated broadly enough to cover waiting after an exchange concludes and while a
live exchange belongs to the requestor or the human gate, but named only the
idle exchange as a valid entry point, which invited the narrow reading. The
amendment names all four states and both wake cases in the requirement, the
child draft, and umbrella item 10, and the Q10 clarification row records
idle-only entry as a rejected alternative so the narrow reading cannot return
through the decision table.

What is left is acceptance criterion 12, which lists three of the four states.
That is a coverage clause, not a decision: the rule it tests is already settled
and stated in three documents plus the decision row. No option changes, no
answer changes, no dependency changes, and no new question is opened.

This convergence carries one limitation the human should weigh: the reviewer
authored the wait-scope wording at the human's direction, so the verdict on that
text is not independent. The verdict on the surrounding work is: the requestor's
Q10 row, the cross-document agreement, the criterion coverage, and the absence
of a new question were all assessed normally. If the human wants an independent
reading of the amendment itself, another round with a different reviewer session
is the way to get it, and that is a stronger reason to choose another round here
than anything found in the text.

This recommendation is advisory. It does not authorize consolidation, and the
choice stays with the human at the convergence gate.

### Writer instructions for feature-request review-resume-command round 1 (exchange 2)

Stop at the convergence gate and present the human with the identity summary,
this recommendation, the amended documents, and your own assessment. Include the
independence limit stated in the convergence rationale: the reviewer wrote the
wait-scope wording it has just reviewed, so the human is choosing with that on
the record rather than discovering it later.

If the human selects `Consolidate`:

1. Apply the criterion 12 clause from the covered wording.
2. Commit the three amended documents together with that clause. A partial
   commit would leave the umbrella and the requirement disagreeing about the
   wait scope, which is the condition the previous occurrence closed.
3. Carry the deferred live-lease displacement case into the design document as a
   named open point. It survived one consolidation already and will disappear
   quietly if the design phase does not pick it up.

If the human selects `Revise and review again`, the criterion 12 clause is the
only outstanding reviewer finding, and the strongest use of that round is an
independent reviewer session reading the wait-scope amendment for the first
time.

Either way, do not treat the reopened occurrence as a reason to revisit the
fourteen consolidated clarifications. They were settled in the previous
occurrence, the amendment disturbs none of them, and only the Q10 row needed the
widening you already applied.

### Final reviewer decision for feature-request review-resume-command round 1 (exchange 2)

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-1-exchange-2 -->

## Round 1 by human - human-confirmation

- Recorded: 2026-09-01T17:07:29+02:00
- Exchange: specification/feature-request/v0.11.0/review-resume-command
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-resume-command.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
