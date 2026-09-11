# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-19T11:15:04+02:00
- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
- Outcome: request

### Review identity for design-specification review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
Review round: 1

### Requestor assessment for design-specification review-mode-docs round 1

The design stays at information-architecture and contract-presentation level.
It does not assign implementation steps or reopen the settled requirement.

The proposed structure uses one explanation, two family-specific tutorials, a
bounded how-to set, one central reference contract, focused entry-point edits,
and a versioned coverage document. It derives state and command facts from
shipped models, launchers, templates, and canonical instructions while keeping
wiki prose user-facing.

Thirteen design questions cover every material choice found during review:
page granularity, tutorial numbering and scenario relationship, family versus
shared how-to boundaries, forced-recovery placement, state-matrix grouping,
missing-host representation, JSON example depth, coverage-file shape,
inventory dispositions, self-review cross-links, source attribution, and the
visual human-decision contract. No additional design-level question is known;
each option set and recommended answer is ready for independent challenge.

### Change summary for design-specification review-mode-docs round 1

This is the first design review round.

- Added the v0.11.0 review-mode-docs design beside the settled requirement.
- Defined scope, confirmed repository facts, current and target documentation
  flows, information architecture, policy ownership, command examples,
  discovery, coverage evidence, and acceptance cases.
- Added thirteen design-only open questions through the managed `oqm` flow.

The committed umbrella, focused draft, feature request, and requirement review
transcript are unchanged by design authoring.

### Writer response for design-specification review-mode-docs round 1

Writer response: There is no earlier reviewer response for this design exchange.

The writer asks the reviewer to verify that the proposed page topology remains
Diataxis-correct, that every exact contract claim has a shipped source, that
family-specific evidence is not flattened into the shared exchange, and that
human-only recovery stays visibly outside ordinary automated procedures.

The two carried notes from requirement review are addressed as design choices:
the tutorials append as `09` and `10` rather than renaming existing files, and
automatic documentation-versus-launcher drift detection remains explicitly
deferred beyond umbrella item 6.

### Reviewer focus for design-specification review-mode-docs round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-19T11:30:20+02:00
- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
- Outcome: answer

### Reviewer assessment for design-specification review-mode-docs round 1

The design holds the right altitude. It arranges settled behavior into a page
topology, decides presentation contracts, and assigns source ownership without
reopening the requirement or assigning implementation steps. Its confirmed-facts
section is unusually disciplined: the reviewer checked each claim against the
working tree and found the host-adapter asymmetry, the `01` through `08`
tutorial prefixes, the absent Markdown launcher, and the launcher result
authority all stated accurately.

One class of defect runs through the design, and it is the same class the
requirement rounds kept surfacing: a contract claim that the shipped code does
not support.

The state vocabulary is incomplete as specified. The design derives the state
matrix from every shipped `ArtifactState` member, Q06 repeats that framing, and
Q06.3 makes "one row per enum member" the objective completeness rule. But
`tools/review_exchange_cli.py` builds its final payload with
`state = "disabled"` when the `a.review-mode` marker is absent, and `disabled`
is not an `ArtifactState` member. That path also returns a null round and no
coordination record. So the first state a reader meets, the one the opt-in
how-to lands on, would be missing from a matrix built to the stated rule, and
the designed completeness check that compares grouped rows back to the source
enum would flag the correct row as an extra. The enum has fifteen members; the
user-visible state vocabulary has sixteen values.

The source-derivation list has the same problem in smaller form. It says
dispositions and outcomes come from their typed models. `ReviewDisposition` and
`ConfirmationOutcome` are typed enums, so dispositions and confirmation
outcomes are fine. Operation outcomes are not: `observed`, `activated`,
`started`, `continued`, `published`, `consumed`, `reclaimed`, `force-reclaimed`,
`repaired`, `escalated`, `cancelled`, `disabled`, and `found` are inline string
literals constructed at roughly fifteen sites in `tools/review_exchange_cli.py`,
with only the confirmation path carrying a typed value. An implementer told to
derive the outcome column from a typed model will look for an enum that does
not exist. That is worth stating plainly, because the outcome column is then
the one contract section with no typed backing and the highest drift risk,
which is exactly the exception Q12.3 reserves row-level notes for.

The third defect is internal rather than factual. The how-to page set is
described three different ways. The information-architecture section lists
seven user goals. Q04.3 enumerates family start and resume guides plus shared
result, ordinary reclaim, and stopped-state recovery guides, which covers five
of the seven and silently drops opt-in and authorized continuation. Q05.3 then
merges ordinary reclaim and stopped-state recovery into one guide, contradicting
the body's treatment of them as separate goals. An implementer cannot tell from
this design how many how-to pages to create or which goals share a page.

Two design-level decisions are missing as questions.

The tutorials never settle how the two-agent boundary is shown. Independent
review mode needs a requestor and a separate reviewer, the tutorial rhythm says
only "run the correct independent reviewer", and criterion 3 requires the
journey to run from opt-in to the human gate, which necessarily crosses that
boundary. Whether the reader opens a second session, a second host window, or
switches skills in place changes what the tutorial shows and how the reviewer's
bounded wait behaves.

The new pages have no visual-identity decision. Every one of the fifty-nine
existing wiki pages carries a topical logo image, and MD033 is configured to
allow `img` precisely for that convention, so roughly eleven new pages need an
answer. The tension is concrete:
`wiki/assets/logo-llm-shared-review-transparent.png` currently marks seven
self-review pages, so reusing it on the independent review-mode set recreates
the vocabulary collision that Q11 and requirement criterion 6 exist to remove.

The thirteen existing questions are otherwise strong. Each is design-scope, each
has three materially distinct options with real consequences, each BBQ analogy
closes with a concrete mapping, and the reviewer would choose every recommended
option as written.

### Question verdicts for design-specification review-mode-docs round 1

**Q01 Page granularity — agree with Q01.3.** One central reference, one
explanation, two tutorials, and a bounded goal-organized how-to set is the
smallest topology that keeps the four Diataxis purposes apart while presenting
one connected protocol. Q01.1 fails requirement criterion 9 outright and Q01.2
forces readers to reassemble one exchange from fragments. The reviewer would
choose Q01.3. The word "bounded" is doing real work here and is undefined; see
the how-to page-set inconsistency in item 3 of the requested changes.

**Q02 Tutorial numeric positions — agree with Q02.3.** Append as `09` and `10`,
specification first. Existing URL stability outweighs encoding chronology in
filenames, and wiki navigation already carries reader-facing order. This also
closes the boundary note the reviewer carried forward from requirement round 3,
and it closes it the right way.

**Q03 Tutorial scenario relationship — agree with Q03.3.** Two stages of one
fictional effort, each tutorial independently completable. Q03.2 is correctly
rejected because swapping command names would hide the genuinely different
identity fields, evidence, and gates. The stated con is honest: each tutorial
must restate enough setup to stand alone.

**Q04 How-to boundaries — agree with the split axis, but the answer's page list
is incomplete.** Splitting where the protocol splits is right: family guides own
identity and reviewer invocation, shared guides own result interpretation and
recovery. That mirrors the canonical instruction architecture without copying
policy. The defect is enumeration, not principle. The answer names family
start and resume plus shared result, ordinary reclaim, and stopped-state
recovery, which accounts for five of the seven goals in the
information-architecture list; opt-in and authorized continuation are dropped
without a stated home.

**Q05 Forced-recovery placement — agree with Q05.3, with the same enumeration
problem.** One recovery guide with an ordinary section and a clearly separated
human-decision section is the right call: Q05.2 would force a human to jump
between diagnosis and action during an incident, and Q05.1 invites exactly the
misreading requirement criterion 7 forbids. But this answer merges ordinary
reclaim and stopped-state recovery into one guide, while the body lists them as
two separate goals and Q04.3 names them as two separate shared guides. The
three statements need to describe one page set.

**Q06 State matrix organization — agree with grouping, but the completeness
rule is wrong as stated.** Grouping by lifecycle phase is clearly better than
enum order for incident use, and keeping the exact typed token in every row is
the right discipline. Q06.2 is correctly rejected. The defect is the
completeness rule itself. The question description says the reference must
include every `ArtifactState` member, and Q06.3 makes one row per enum member
the objective check. That check omits `disabled`, which
`tools/review_exchange_cli.py` reports as the `state` value when the
`a.review-mode` marker is absent, and which is not an `ArtifactState` member.
The same branch returns a null round and no coordination record, so the row also
carries information no other row carries. As written, the designed validation
would reject the correct table. The reviewer would keep option Q06.3 and repair
its rule to read: every `ArtifactState` member appears exactly once, plus one
documented launcher-only `disabled` row.

**Q07 Missing host wrappers — agree with Q07.3.** An explicit `absent` cell
naming the existing family route is the only option that records shipped
reality without either hiding a gap or changing adapter behavior outside scope.
Q07.2 is correctly rejected as an implementation change. The reviewer
reconfirmed the underlying fact against the tree.

**Q08 Launcher JSON example depth — agree with Q08.3, sharpen the field list.**
One minimal complete final-result example in reference plus smaller linked
excerpts is right, and separating standard-error progress from the final object
is exactly the distinction the requirement's Q05 settled. The phrase
"applicable authority flags" is guesswork as written. Pin the example to
`_success_payload` in `tools/review_exchange_cli.py`: `diagnostic`, `identity`,
`operation`, `outcome`, `paths`, `round`, and `state` are the mandatory fields,
and anything else the reader may observe, such as `exchange_occurrence` or an
owning-action authorization flag, should be shown as conditional rather than
implied to be always present.

**Q09 Coverage document format and name — agree with Q09.3.**
`coverage.v0.11.0.review-mode-docs.md` beside the effort documents follows the
established artifact grammar and satisfies the requirement's placement rule.
Q09.1 would bury durable page mapping inside step instructions and Q09.2 would
leave scope and omission reasoning with no single view. The stated con, that
the plan must keep it current, is real and correctly accepted.

**Q10 Inventory disposition model — agree with Q10.3.** The three dispositions
`update`, `already covered`, and `unaffected` make the requirement's omission
rule objectively reviewable and distinguish adequate existing coverage from a
true scope mismatch. That third value is the one that prevents Q10.1's
redundant-link outcome.

**Q11 Self-review cross-link pattern — agree with Q11.3.** Short reciprocal
comparison callouts on the two existing pages, with the full distinction living
on the new explanation page, closes the vocabulary collision where readers
actually meet it without expanding self-review pages into protocol guides. This
answer interacts with the missing visual-identity question below: a callout
that separates the two concepts in prose is undercut if both page sets carry
the same logo.

**Q12 Source attribution — agree with Q12.3.** Section-level attribution with
row-level notes only for exceptions is the right balance; per-row links would
make the lookup tables unreadable and a single bottom list would not identify
the owner of a disputed rule. One correction belongs to the design body rather
than to this answer: the derivation list claims outcomes come from typed
models, and operation outcomes are inline string literals in
`tools/review_exchange_cli.py`. The outcome column is therefore precisely the
kind of exception Q12.3 reserves a row-level or section-level note for, and it
should be named as such.

**Q13 Human-decision visual contract — agree with Q13.3.** A fixed
`Human decision required` heading plus a blockquote stating authority,
precondition, and evidence effect is the right choice. Q13.1 is correctly
rejected: the repository serves its wiki locally and renders it in several
hosts, so a warning that depends on color or custom HTML is a warning that can
vanish. Semantic Markdown survives every renderer and stays checkable.

**Q14 missing: how the tutorials depict the two-agent boundary.** The tutorial
rhythm says "run the correct independent reviewer" without settling where that
reviewer runs. Independent review mode exists to put a second agent opposite
the writer, requirement criterion 3 requires the journey to run from opt-in to
the human gate, and the reviewer's bounded wait reads differently depending on
the answer. Suggested options: teach one session that switches skills between
requestor and reviewer roles; teach two explicitly labelled sessions with the
handoff shown at each publish and wait; or abstract the actor entirely and show
only commands with a note that the reviewer runs wherever the user runs it. The
reviewer would choose two explicitly labelled sessions, because the separation
of actors is the feature being taught and a single-session depiction makes the
independence look cosmetic.

**Q15 missing: visual identity for the new pages.** All fifty-nine existing
wiki pages carry a topical logo image, and `.markdownlint.json` allows `img`
under MD033 precisely to support that convention, so roughly eleven new pages
need a decision. The tension is concrete:
`wiki/assets/logo-llm-shared-review-transparent.png` currently marks the seven
self-review pages, so reusing it for independent review mode reintroduces the
collision Q11 and requirement criterion 6 exist to remove. Suggested options:
reuse the existing review logo; use the generic
`logo-llm-shared-transparent.png` for the new set and leave the review logo as
the self-review marker; or add one new asset for independent review mode. The
reviewer would choose the generic logo, because it costs no new asset, keeps
the visual distinction the terminology decision depends on, and leaves the
dedicated-asset option open without blocking this effort.

### Requested changes for design-specification review-mode-docs round 1

Requested changes: 1. Repair the state vocabulary in three places, because the design currently
   equates it with `ArtifactState` and the launcher reports one value that the
   enum does not contain. In the confirmed-technical-facts section, in the
   central-reference contract bullet, and in Q06, state that the user-visible
   state vocabulary is the fifteen `ArtifactState` members plus the
   launcher-only `disabled` value that `tools/review_exchange_cli.py` reports
   when the `a.review-mode` marker is absent, together with its null round and
   absent coordination record. Restate the Q06.3 completeness rule so it does
   not reject the correct table, for example:

   > Every `ArtifactState` member appears in exactly one row, plus one
   > documented launcher-only `disabled` row. Validation compares the typed
   > rows against the source enum and accounts for the `disabled` row
   > separately.

2. Correct the source-derivation list in the authority and content-reuse
   section. Dispositions and confirmation outcomes do come from typed models,
   `ReviewDisposition` and `ConfirmationOutcome`. Operation outcomes do not:
   `observed`, `activated`, `started`, `continued`, `published`, `consumed`,
   `reclaimed`, `force-reclaimed`, `repaired`, `escalated`, `cancelled`,
   `disabled`, and `found` are inline string literals in
   `tools/review_exchange_cli.py`. Name that module as the source for the
   outcome column and record it as the one contract section with no typed
   backing, which is the exception Q12.3 already reserves a note for.

3. Make the how-to page set consistent across the three places that describe
   it. The information-architecture list names seven goals, Q04.3 accounts for
   five and drops opt-in and authorized continuation, and Q05.3 merges ordinary
   reclaim with stopped-state recovery that the body lists separately. Choose
   one page set and use it in all three places, stating for each of the seven
   goals whether it is its own page or a section of a named page.

4. Append Q14 on how the tutorials depict the two-agent boundary, with the
   three options and the recommended answer given in the verdicts. The chosen
   answer should also say what the tutorial shows while the reviewer's bounded
   wait is running, since that is the moment the depiction becomes visible.

5. Append Q15 on the visual identity of the new pages, with the three options
   and the recommended answer given in the verdicts. Whichever option is
   accepted, state it as a design constraint so the eleven new pages do not
   each decide independently.

6. Pin the Q08 canonical example to `_success_payload` in
   `tools/review_exchange_cli.py` rather than to the phrase "applicable
   authority flags". Name `diagnostic`, `identity`, `operation`, `outcome`,
   `paths`, `round`, and `state` as the mandatory fields, and show any other
   observable field, such as `exchange_occurrence` or an owning-action
   authorization flag, as conditional.

Optional polish, at the writer's discretion and not required for convergence.

- The acceptance-case table row for an expiring lease says the how-to
  "preserves the round and artifacts". Adding that ordinary reclaim renews the
  lease in place and is idempotent while the round stays live would make the
  row match the shipped guarantee rather than a weaker paraphrase of it.

### Writer instructions for design-specification review-mode-docs round 1

Apply the requested changes to
`docs/v0.11.0/design.v0.11.0.review-mode-docs.md` only. The umbrella draft, the
focused draft, the settled feature request, and every review transcript stay
unchanged, and no protocol artifact is edited by hand.

Take the state-vocabulary repair first. It is the one defect that would produce
wrong delivered documentation rather than an ambiguous instruction: a reference
built to the current completeness rule would omit the state a reader meets when
review mode is off, and the designed validation would then flag the corrected
table as containing an extra row. Repair the confirmed-facts section, the
central-reference bullet, and Q06 together so the three cannot drift apart
again.

Take the how-to page-set inconsistency second. It is the defect an implementer
hits earliest, because the first planning decision is how many pages to create.
Do not resolve it by adding a new question; the split axis is already settled by
Q04.3 and the placement rule by Q05.3, so this is an enumeration repair inside
the existing answers and the body list.

Then append Q14 and Q15 through the `oqm` companion workflow, keeping the
established block shape: description, BBQ analogy closed by an explicit "In
this picture" mapping, three materially distinct options with pros and cons, a
recommended option with arguments, and an explicit answer with the reason it
must be accepted. The verdicts file supplies the options and the reviewer's
recommended answer for both.

Do not renumber or reorder Q01 through Q13 while applying these changes, so the
round-1 verdicts stay traceable. Every recommended option in Q01 through Q13 is
accepted as written; only the Q06 completeness rule, the Q04 and Q05
enumerations, and the Q08 field list change, and none of those changes the
chosen option.

Two notes on scope. Adding a wrapper to a host adapter remains out of scope, as
Q07 already states, so Q15 must not be answered by changing adapter files.
Automatic drift detection between documented commands and shipped launcher
behavior remains deferred beyond umbrella item 6, so the outcome-column source
correction in item 2 is a stated attribution and drift risk, not a new check.

After the edits, publish another automated review round. Two new questions and
three contract repairs are well past word polishing, so this round does not
reach convergence.

### Final reviewer decision for design-specification review-mode-docs round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-19T15:01:44+02:00
- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
- Outcome: request

### Review identity for design-specification review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
Review round: 2

### Requestor assessment for design-specification review-mode-docs round 2

All three design defects and both missing-question gaps from round 1 are closed.

- The user-visible state vocabulary is now the fifteen `ArtifactState` members
  plus the launcher-only `disabled` result with null round and no coordination
  record, and Q06 carries the same completeness rule.
- Typed dispositions and confirmation outcomes are separated from inline
  operation-outcome strings sourced from `review_exchange_cli.py`, with the
  untyped column identified as a drift-risk exception.
- The how-to topology is fixed at five pages that assign all seven user goals:
  opt-in, two family start/resume pages, shared results and continuation, and
  shared recovery with ordinary, stopped-state, and human-decision sections.
- Q08 names the seven mandatory `_success_payload` fields and labels additions
  such as occurrence or owning-action authorization as conditional.

Q14 and Q15 complete the design review surface with two labelled agent sessions
and a generic-logo constraint for new pages. No question is missing; Q01
through Q15 remain design-level, have sufficient options and answers, and keep
their original order where previously published.

### Change summary for design-specification review-mode-docs round 2

Only the reviewed design changed since round 1.

- Repaired the state vocabulary and matrix validation rule.
- Corrected typed and untyped contract-source attribution.
- Reconciled every how-to description around one five-page topology.
- Pinned launcher JSON examples to `_success_payload`.
- Added Q14 and Q15 through `oqm` without renumbering Q01 through Q13.
- Applied the optional ordinary-reclaim precision in the acceptance cases.

The umbrella, focused draft, settled requirement, and transcripts remain
untouched outside protocol-owned transcript appends.

### Writer response for design-specification review-mode-docs round 2

Writer response: All round-1 requested changes were accepted without disagreement.

The state repair uses the exact launcher exception identified by the reviewer.
The operation-outcome source note does not introduce drift automation or a new
typed model. The page-set repair keeps Q04.3's family-versus-shared split and
Q05.3's marked human-decision boundary while assigning every required goal.

Q14 adopts two explicitly labelled sessions and shows the reviewer working
while the requestor's bounded wait is active. Q15 adopts the generic llm-shared
logo for every new independent-review-mode page and reserves the existing
review logo for self-review pages. No adapter or asset implementation changed.

### Reviewer focus for design-specification review-mode-docs round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-19T16:38:40+02:00
- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
- Outcome: answer

### Reviewer assessment for design-specification review-mode-docs round 2

All three round-1 defects and both missing-question gaps are closed. The
reviewer verified each repair against the working tree and against the shipped
code the design cites, rather than accepting the change summary.

The state-vocabulary repair is correct and complete in all three places that
carried the defect. The confirmed-facts section now states fifteen
`ArtifactState` members plus the launcher-only `disabled` value emitted when
the `a.review-mode` marker is absent, together with its null round and absent
coordination record. The central-reference bullet requires one row per enum
member plus that sixteenth row. Q06 carries the same rule in its description,
its option text, and its answer, and its validation rule now compares fifteen
typed rows against the enum while accounting for `disabled` separately, so the
check no longer rejects the correct table. The reviewer reconfirmed against
`tools/review_exchange_cli.py` that the absent-marker branch sets the state
literal, leaves the record unset, and therefore reports a null round.

The source-attribution repair is precise. Dispositions are now attributed to
`ReviewDisposition` and confirmation outcomes to `ConfirmationOutcome`, both of
which are typed enums, while operation outcome strings are attributed to
`tools/review_exchange_cli.py` and explicitly recorded as the one contract
column with inline string sources rather than typed backing. Naming it a
drift-risk exception rather than adding a check respects the deferral the
umbrella already declares.

The how-to topology is now stated identically in all three places that
previously disagreed. The information-architecture section, the Q04 answer, and
the Q05 answer all describe one five-page set, and every one of the seven user
goals has a named home: opt-in, specification start and resume,
implementation-code start and resume, results with authorized continuation, and
recovery holding ordinary reclaim, stopped-state handling, and the marked
human-decision section. That set also satisfies each item requirement criterion
4 enumerates. The Q08 example is pinned to `_success_payload` with the seven
mandatory fields named exactly as the payload builds them, and observable
additions labelled conditional.

Q14 and Q15 are well built and adopt the recommended answers. Q14 chooses two
explicitly labelled sessions and, usefully, specifies what the reader sees
while the requestor's bounded wait is active, which was the part most likely to
be left implicit. Q15 states the generic logo as a design-wide constraint so
eleven new pages cannot each decide independently, and it reserves the review
logo for the self-review set, which protects the visual half of the distinction
that Q11 and requirement criterion 6 make in prose.

Every factual claim the design makes now checks out: fifteen enum members, the
launcher-only disabled branch, the seven mandatory payload fields, the typed
and untyped source split, the host-adapter asymmetry, the `01` through `08`
tutorial prefixes, the absent Markdown launcher, and the universal wiki logo
convention.

Nothing else moved. All fifteen questions keep their titles, order, and
recommended options: Q01.3, Q02.3, Q03.3, Q04.3, Q05.3, Q06.3, Q07.3, Q08.3,
Q09.3, Q10.3, Q11.3, Q12.3, Q13.3, Q14.2, and Q15.2. The optional
ordinary-reclaim precision was applied, and the acceptance case now states that
reclaim renews the lease in place and stays idempotent while the round is live,
which matches the shipped guarantee.

One wording-level observation remains, recorded in the covered wording. Q06.3
names six groups, and fourteen of the fifteen enum members map cleanly onto
them, but `idle` has no listed group: it is neither disabled, nor active, nor
convergence, abandonment, interrupted, or inconsistent. The objective
completeness rule already guarantees `idle` a row, so this cannot produce
missing documentation; it only leaves the implementer to choose a group.

No question is missing, no answer is contested, and no substantive change
remains. The reviewer recommends convergence.

### Question verdicts for design-specification review-mode-docs round 2

No question is missing, and the reviewer contests no answer. Every recommended
option is the one the reviewer would choose. The verdicts below close each
question for this exchange.

**Q01 Page granularity — settled at Q01.3.** One central reference, one
explanation, two tutorials, and a bounded goal-organized how-to set. The word
"bounded" now has a concrete meaning, because Q04 fixes the how-to set at five
named pages; that was the open edge in round 1 and it is closed.

**Q02 Tutorial numeric positions — settled at Q02.3.** Append as `09` and `10`,
specification first, with navigation carrying conceptual order. This preserves
every existing tutorial URL and keeps the numeric convention intact.

**Q03 Tutorial scenario relationship — settled at Q03.3.** Two stages of one
fictional effort, each tutorial independently completable, with comparison links
at the divergence points. This pairs well with the Q14 decision: one effort seen
from two labelled sessions is easier to follow than two unrelated efforts each
spanning two sessions.

**Q04 How-to boundaries — settled at Q04.3, enumeration repaired.** The split
axis was never in doubt; the round-1 defect was that the answer accounted for
five of seven goals. It now names all five pages and assigns every goal: the
opt-in page owns the marker, two family pages own identity and reviewer
invocation, the shared result page owns artifact interpretation and authorized
continuation, and the shared recovery page owns ordinary reclaim and
stopped-state handling. Each item requirement criterion 4 enumerates has a home.

**Q05 Forced-recovery placement — settled at Q05.3, enumeration repaired.** One
recovery guide with ordinary reclaim and stopped-state actions in separate
sections, and forced operations under a dedicated human-decision heading and
callout stating preconditions, authority, and evidence effects before any
command. The body, Q04, and Q05 now describe the same page.

**Q06 State matrix organization — settled at Q06.3, completeness rule
repaired.** Grouping by lifecycle phase with the exact typed token in every row
remains the right choice for incident use. The rule now reads that every
`ArtifactState` member appears once plus one launcher-only `disabled` row with
null round and no coordination record, and validation compares the fifteen
typed rows against the enum while accounting for `disabled` separately. That is
exactly the repair round 1 requested, and it removes the case where the designed
check would have rejected a correct table. One wording point about the group
list is recorded in the covered wording.

**Q07 Missing host wrappers — settled at Q07.3.** An explicit `absent` cell
naming the existing family route. It records shipped coverage without
manufacturing parity and without changing adapter files, which Q15 also
correctly refrains from doing.

**Q08 Launcher JSON example depth — settled at Q08.3, field list pinned.** The
canonical example is now tied to `_success_payload` in
`tools/review_exchange_cli.py` with `diagnostic`, `identity`, `operation`,
`outcome`, `paths`, `round`, and `state` as the mandatory fields, and
observable additions such as `exchange_occurrence` or an owning-action
authorization flag labelled conditional. The reviewer confirmed those seven are
exactly the keys the payload builds, so the example can no longer freeze an
incidental field into the user contract.

**Q09 Coverage document format and name — settled at Q09.3.**
`coverage.v0.11.0.review-mode-docs.md` beside the effort documents, with
criterion, evidence type, exact path or command, result, and notes. It follows
the effort artifact grammar and satisfies the requirement's placement rule.

**Q10 Inventory disposition model — settled at Q10.3.** The three dispositions
`update`, `already covered`, and `unaffected`, each with an exact target or
reason, make the requirement's omission rule objectively reviewable.

**Q11 Self-review cross-link pattern — settled at Q11.3.** Short reciprocal
comparison callouts on the two existing pages with the full distinction on the
new explanation page. Q15 now protects the visual half of this separation, which
was the gap the reviewer flagged against this answer in round 1.

**Q12 Source attribution — settled at Q12.3.** Section-level attribution with
row-level notes for exceptions. The design body now supplies an accurate source
map for that scheme to attribute against, including the honest statement that
operation outcomes have no typed backing and therefore carry an explicit source
and drift-risk note.

**Q13 Human-decision visual contract — settled at Q13.3.** A fixed
`Human decision required` heading plus a blockquote stating authority,
precondition, and evidence effect. Semantic Markdown survives every renderer
this repository serves, which color-dependent HTML would not.

**Q14 Two-agent tutorial boundary — settled at Q14.2, as recommended.** Two
explicitly labelled sessions, with the requestor publishing and entering its
bounded wait, the reviewer receiving the request and publishing the answer, and
the tutorial returning to the requestor when the wait reports the authoritative
answer path. This is the option the reviewer would choose: actor separation is
the feature being taught, and a single session switching skills would make that
independence look cosmetic. Specifying what the reader sees during the bounded
wait closes the part most likely to be left implicit. The stated con, that the
reader keeps two sessions visible, is the honest cost of teaching the real
boundary.

**Q15 Visual identity — settled at Q15.2, as recommended.** The generic
`logo-llm-shared-transparent.png` for every new independent-review-mode page,
with `logo-llm-shared-review-transparent.png` retained as the self-review
marker. This is the option the reviewer would choose: it costs no new asset,
keeps the two concepts visually distinct where the terminology decision needs
support, changes no shipped adapter or asset, and leaves a dedicated asset
possible later. Stating it as a design-wide constraint is the right move, since
eleven pages deciding independently is exactly how a convention erodes.

### Convergence evidence for design-specification review-mode-docs round 2

Covered wording: The reviewer read the complete current design and confirmed the following
wording as covered and accurate.

The confirmed-facts section states that `tools/review_exchange_models.py`
defines fifteen `ArtifactState` members and that the user-visible vocabulary
also includes the launcher-only `disabled` value emitted by
`tools/review_exchange_cli.py` when the `a.review-mode` marker is absent, with a
null round and no coordination record. The central-reference contract requires
one row per enum member plus that launcher-only row. Q06 repeats the same rule
in its description, option, recommendation, and answer. All of this matches the
shipped code.

The source map states that fifteen states come from `ArtifactState` and the
`disabled` state from the absent-marker branch of the CLI; dispositions from
`ReviewDisposition` and confirmation outcomes from `ConfirmationOutcome`;
operation outcome strings from `tools/review_exchange_cli.py`, recorded as the
one contract column with inline string sources rather than typed backing and
given an explicit source and drift-risk note; operations and arguments from
launcher help and adapters; ownership from canonical instructions; and artifact
shapes from templates and store models.

The how-to set is five pages: opt-in, specification start and resume,
implementation-code start and resume, results with authorized continuation, and
recovery holding ordinary reclaim, stopped-state handling, and the marked
human-decision section. The information-architecture section, the Q04 answer,
and the Q05 answer state this identically.

The canonical launcher example is pinned to `_success_payload` with
`diagnostic`, `identity`, `operation`, `outcome`, `paths`, `round`, and `state`
mandatory, and additions such as `exchange_occurrence` or an owning-action
authorization flag labelled conditional.

The visual identity boundary assigns `wiki/assets/logo-llm-shared-transparent.png`
to new independent-review-mode pages and retains
`wiki/assets/logo-llm-shared-review-transparent.png` for the self-review set.

The acceptance case for an expiring lease now states that ordinary reclaim
renews the lease in place, preserves the round and artifacts, and remains
idempotent while the round is live, which matches the shipped guarantee.

All fifteen question titles, positions, options, recommendations, and answers
are covered as they currently stand, with the answers remaining Q01.3, Q02.3,
Q03.3, Q04.3, Q05.3, Q06.3, Q07.3, Q08.3, Q09.3, Q10.3, Q11.3, Q12.3, Q13.3,
Q14.2, and Q15.2.

One wording-level observation remains, and it does not block consolidation. It
is recorded here so the human choosing at the gate sees the complete picture,
and it may be folded in during consolidation or left alone.

Q06.3 names six groups: disabled opt-in, active exchange, convergence and
owning action, lease abandonment, interrupted or repair-required, and stopped
or inconsistent. Fourteen of the fifteen enum members map cleanly onto those
groups, but `idle` fits none of them: it is not the disabled state, since the
marker is present, and it is not an active, converging, abandoned, interrupted,
or inconsistent exchange. The objective completeness rule already guarantees
`idle` a row, so no state can go missing; the implementer simply has to choose
its group. Widening the first group to cover both not-yet-started cases, for
example naming it disabled or idle, would remove the hesitation. This is
precision rather than correction, and the reviewer does not request it as a
change.

Convergence rationale: This exchange reaches the convergence bar because every in-scope design
decision is settled and no more than wording-only edits remain.

Round 1 found three defects and two gaps. The defects shared one shape: a
contract claim the shipped code did not support. The state matrix was defined
as the `ArtifactState` enum when the launcher also reports a `disabled` state
outside it, the source map claimed typed models for operation outcomes that are
inline string literals, and the how-to page set was described three
incompatible ways. The gaps were the two-agent tutorial depiction and the visual
identity of the new pages. Round 2 closed all five, and the reviewer verified
each against the working tree and the cited modules rather than against the
change summary. This round found no new defect.

The design is implementable as written. Fifteen questions cover the material
design-level choices for a documentation effort: page topology, tutorial
numbering, tutorial scenario relationship, how-to boundaries, forced-recovery
placement, state-matrix organization, missing host wrappers, launcher example
depth, coverage document shape and name, inventory dispositions, self-review
cross-links, source attribution, human-decision styling, the two-agent
depiction, and visual identity. Each has three materially distinct options with
stated consequences, a recommendation, and an explicit answer, and the internal
descriptions now agree with the answers they implement.

The design is factually grounded, which matters more here than usual because
this effort's whole product is claims about shipped behavior. Every technical
statement was checked: fifteen enum members, the absent-marker branch that
yields `disabled` with a null round and no coordination record, the seven
mandatory `_success_payload` fields, the split between typed dispositions and
untyped operation outcomes, the host-adapter asymmetry, the `01` through `08`
tutorial prefixes, the absent Markdown launcher, and the logo convention across
every existing wiki page. All hold.

The design also stays inside its altitude and its scope. It arranges settled
behavior into a page topology and presentation contracts without reopening the
requirement, assigning implementation steps, or changing any protocol,
launcher, template, adapter, or asset. Q07 refuses to add a missing wrapper and
Q15 refuses to commission an asset, both for the same correct reason. The
deferred items stay deferred: the item 7 Markdown checker, the item 8
commit-plan launcher, and automatic drift detection between wiki command text
and launcher behavior, which the outcome-column note records as a risk rather
than converting into a check.

One wording-level observation remains, recorded in the covered wording, and it
cannot cause missing or wrong documentation because the objective completeness
rule already governs the case.

This recommendation is advisory. It does not authorize consolidation. The
choice between `Consolidate` and `Revise and review again` belongs to the human
at the durable gate, and the reviewer takes no part in it.

### Writer instructions for design-specification review-mode-docs round 2

No changes are requested. Do not edit
`docs/v0.11.0/design.v0.11.0.review-mode-docs.md` in response to this answer,
and do not reopen, renumber, or restate any question.

Present this recommendation to the human at the durable convergence gate,
together with the requestor's own assessment and the identity summary, and
offer the registered choices `Consolidate` and `Revise and review again`. This
reviewer recommendation is advisory and authorizes nothing on its own.

If the human chooses `Consolidate`, fold the fifteen answers into the design
through the owning consolidation workflow. The single wording-level observation
in the covered wording, about `idle` having no listed group among Q06.3's six
groups, may be applied during that consolidation or left alone. If it is
applied, keep the objective completeness rule exactly as it stands: every
`ArtifactState` member appears once, plus one launcher-only `disabled` row.

If the human chooses `Revise and review again`, treat their guidance as the
scope of the next round. Nothing in this review contributes work to such a
round: the reviewer found no missing question, contested no answer, and
requested no change.

Two notes for the phases that follow, carried forward rather than inserted into
the design. The five how-to pages, two tutorials, one explanation, one central
reference, and the coverage document give the implementation plan its natural
units, and the versioned coverage document is the deliverable most likely to
drift during implementation because it must be updated whenever the page set
changes. The operation-outcome column is the one contract section with no typed
source, so it is the section most exposed to future launcher changes; the plan
should keep its source note visible rather than folding it into general
attribution.

### Final reviewer decision for design-specification review-mode-docs round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-20T07:49:56+02:00
- Exchange: specification/design-specification/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.review-mode-docs.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
