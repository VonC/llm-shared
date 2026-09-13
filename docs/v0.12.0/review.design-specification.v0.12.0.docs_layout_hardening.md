# Specification review transcript for v0.12.0

- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-12T16:36:18+02:00
- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for design-specification docs_layout_hardening (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
Review round: 1

### Requestor assessment for design-specification docs_layout_hardening (round 1)

#### Writer assessment of the layout-hardening design for design-specification docs_layout_hardening (round 1)

The consolidated issue is the authority for observable behavior. This design
preserves all ten issue decisions and asks six design questions about shared
eligibility, exact filename matching, candidate scope, error interfaces,
freshness and filesystem failure propagation.

I consider the options and proposed answers sufficient for design review. No
additional design question is currently missing. Each recommendation has a
material alternative, and none changes accepted layout scope, fallback
multiplicity or local timestamp handling. The exact private helper names, file
split and test sequence remain implementation-plan work.

Current-behavior claims were checked in prompt_workflow_docs.py and its callers:
the two independent recognition paths, exact versus role-based filename
matching, exclusive recognized-parent search, unrecognized-parent fallback,
newest selection, and the CLI exception boundary. The v0.12.0 documentation
Markdown check passes. No reviewer wording exists for this first design round.

Please assess the architecture and the six questions independently against the
settled issue and source, including whether matcher reuse and internal scope
metadata preserve all existing filename and interface contracts.

### Change summary for design-specification docs_layout_hardening (round 1)

#### Initial layout-hardening design changes for design-specification docs_layout_hardening (round 1)

Created the design beside the consolidated issue, with confirmed source facts,
current and target flows, recognition and selection boundaries, diagnostics,
freshness and acceptance cases. Added six design questions through oqm, each
with alternatives, pros and cons, a recommendation and a proposed answer.

This is design round 1. The preceding issue review is complete, its accepted
answers are consolidated, and its question snapshot and final documentation are
committed. This design does not ask to revise the issue.

### Writer response for design-specification docs_layout_hardening (round 1)

Writer response:

#### Initial writer response for the layout-hardening design for design-specification docs_layout_hardening (round 1)

No preceding design-review answer exists. I recommend option A for all six
design questions and request independent assessment before the human chooses
whether to consolidate the design. No consolidation authority is inferred from
the completed issue review.

### Reviewer focus for design-specification docs_layout_hardening (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.design-specification.v0.12.0.docs_layout_hardening.md`
- `.reviews/a.review-requested.design-specification.v0.12.0.docs_layout_hardening.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-12T16:41:19+02:00
- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification docs_layout_hardening round 1

#### Reviewer assessment of the layout-hardening design for design-specification docs_layout_hardening (round 1)

The architecture is right. Separating one shared eligibility boundary from
scope-aware selection is the shape the ten consolidated issue decisions ask for,
and the design keeps the two matching contracts apart instead of merging them,
which was the risk this effort carried from the start. The circular-dependency
note (recognition must not call a resolver that itself enumerates recognized
directories) shows the hard edge was found before the plan.

Every confirmed technical fact checks out against the source. `DOCUMENT_TYPES`
does carry `draft` with prefix `("draft",)`, so Q02 option A is feasible for
every accepted kind. `_exact_doc_matches` handles the validation suffix as the
design describes. `most_recent` is `max(paths, key=mtime)`, which keeps the
first maximal element, so "existing candidate order for ties" is accurate.
`tools/prompt_workflow.py:614` catches `PromptWorkflowError` and `OSError`
together, so the CLI boundary claim holds.

What is missing is one caller. The design names
`prompt_workflow_steps.py` and the `prompt_workflow.py` CLI and stops there.

##### A Topic's draft path is not always a discovered draft for design-specification docs_layout_hardening (round 1)

`prompt_workflow_post_commit._topic_from_validation_plan` builds a topic from a
validation-plan filename and synthesizes its draft path as
`path.parent / f"draft.{version}.{slug}.md"`, resolved but never checked for
existence. Its whole purpose is to point `_topic_docs_dirs` at the directory the
validation plan sits in. The module docstring for `resolve_post_commit_topic`
says so outright: it resolves a plan topic "when the original draft is no longer
discoverable".

The design speaks throughout of the canonical draft's parent, and its acceptance
table says "Canonical draft discovered in an unsupported or identity-mismatched
parent". An implementer reading that can reasonably resolve the draft and then
validate it, which turns every post-commit topic into an invalid parent because
its draft file is not there. The check has to be on the topic's directory, with
no existence or discovery requirement on the draft itself, and the design should
say that rather than leave it to be inferred from `_topic_docs_dirs`.

##### The post-commit hook is a third caller boundary for design-specification docs_layout_hardening (round 1)

`prompt_workflow_post_commit.plan_topics` calls
`docs.select_document(root, topic, "plan") is None` as a cheap test for whether
a topic has a plan, skipping it when the answer is `None`. Nothing in that
module catches anything.

The invalid-parent error cannot reach it: `plan_topics` iterates
`docs.docs_dirs(root)` and builds each topic's directory from the entry it just
read there, so the parent is a member of the recognized set by construction.
The fallback-ambiguity error can. A topic whose directory holds the validation
plan but no ordinary plan returns `None` today and is skipped. Under issue Q06
the selector now searches every other recognized directory: one match there
makes the topic appear in post-commit results where it did not before, and
several raise `PromptWorkflowError` out of a git hook with no handler.

This is the design's own rule working as intended ("callers must not downgrade
these failures to a missing document"), applied to a caller the design has not
looked at. It needs a stated outcome, not a discovery during implementation.

##### The list-returning helper has no stated behavior for an invalid parent for design-specification docs_layout_hardening (round 1)

`find_matching_documents` is described as keeping its public list return shape
and returning "all matches in the selected scope". For an unrecognized parent
there is no selected scope. Whether it raises, like the selector, or returns an
empty list and leaves validation to `select_document` is a real choice: it
decides whether the invalid-parent rule is enforced once at the discovery
boundary or once per public entry point, and sixteen tests in
`test_prompt_workflow_docs_tdd.py` touch these helpers.

It is worth noting that `find_matching_documents` has no caller outside
`prompt_workflow_docs.py` today, so the answer is about internal consistency and
test surface rather than about compatibility.

##### Everything else for design-specification docs_layout_hardening (round 1)

The six questions are well formed, each alternative is real, and I would choose
option A for all six. The acceptance table covers all ten issue decisions with
correct requirement bases, except one row that cites the issue where it means
this design's own freshness answer. Scope, out-of-scope and confirmed-facts
sections are accurate and give the plan a clean starting point.

### Question verdicts for design-specification docs_layout_hardening round 1

#### Reviewer verdicts on the six design questions for design-specification docs_layout_hardening (round 1)

All six are design questions rather than requirement or plan questions, and none
reopens a settled issue decision. I agree with option A in every case. One
question is missing.

##### Verdict on design Q01 about where the two listings share eligibility for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. The defect the issue named is a
duplicated rule, not duplicated enumeration, and option B would make exact
resolution scan unrelated version directories to recover an ordering it already
has. The con on option A is honest: two enumeration callers remain.

##### Verdict on design Q02 about filename evidence for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. Reuse is feasible as described:
`DOCUMENT_TYPES` already contains `draft` with its own prefix, and
`_exact_doc_matches` already applies exact version equality, folded slug
equality and the validation-suffix rule. Option B would open a filename grammar
that this effort has no reason to touch.

One precision belongs in option A's con rather than in a new option. Recognition
would become a second consumer of a matcher whose other consumer is explicit
resolution, so the accepted kinds have to be named in one place and stay named
there. The design says "accepted kinds must remain explicit"; naming the six
(draft, feature-request, issue, design, plan, validation-plan) in the answer
paragraph removes the ambiguity with the `requirement` alias, which maps to the
same prefixes as feature-request and issue.

##### Verdict on design Q03 about carrying the search scope for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. Option B rediscovers what discovery
already knew and would need a second canonical-parent comparison to do it. The
internal result shape is the smaller cost.

This question needs the boundary that the missing question below supplies: an
internal scoped result answers how scope travels, not what the public
list-returning helper does when the parent is invalid.

##### Verdict on design Q04 about how new failures reach callers for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. `tools/prompt_workflow.py:614` catches
`PromptWorkflowError` and `OSError` in the same handler, so both new failures
reach an established fatal boundary without a new public error contract, and no
current caller inspects exception fields. Requiring diagnostic content without
fixing a sentence is the right level for a design.

The con understates one case. Programmatic recovery is not only a future
concern: `prompt_workflow_post_commit.plan_topics` already distinguishes "has a
plan" from "has no plan" by testing for `None`, and with option A a competing
fallback becomes an exception it does not catch. That is an argument for
option A plus a stated caller outcome, not an argument for option B.

##### Verdict on design Q05 about an eligibility snapshot for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. The workflow is short-lived, the issue's
freshness answer is stated in observable terms, and a snapshot would need a
lifetime and an invalidation rule to buy back directory reads nobody has
measured. Option B is a real alternative and correctly carries the cost of
observing changes only after a rebuild.

##### Verdict on design Q06 about filesystem error recovery for design-specification docs_layout_hardening (round 1)

Keep as written. My answer is option A. A retry classifier would guess at
concurrent removal without an atomic view and would leave every other concurrent
mutation unhandled. Propagating keeps absence meaningful, which is the property
the whole selection contract now rests on.

##### Missing design question about where the parent check is enforced for design-specification docs_layout_hardening (round 1)

The design states that the selector validates the parent before any fallback,
and separately that `find_matching_documents` keeps its list return shape. Those
two statements do not settle what the list-returning helper does for an invalid
parent. Proposed question:

```text
Q07: Where is the canonical-parent check enforced?

Issue Q10 requires an invalid canonical parent to be reported rather than
widened. Discovery produces the scoped candidate result; selection applies the
policy. Should the parent check live in the shared discovery operation, so
every entry point that consumes it reports the failure, or only in
`select_document`, leaving the list-returning helper total?

Option A: Enforce it in the shared discovery operation.
  pro: One place decides eligibility of the parent, and no later entry point
  can consume a candidate result built from an unvalidated parent.
  con: `find_matching_documents` raises where it now returns a list, so its
  tests and any future caller must handle the failure.
Option B: Enforce it only in `select_document`.
  pro: The list-returning helper stays total and its existing tests keep their
  shape.
  con: The rule lives beside the policy rather than beside the discovery that
  chose the scope, and a second consumer of discovery would have to repeat it.

Recommended and answer: option A, because the invalid parent invalidates the
scope choice itself, not the selection policy applied to it.
```

### Requested changes for design-specification docs_layout_hardening round 1

Requested changes:

#### Requested changes to the layout-hardening design for design-specification docs_layout_hardening (round 1)

Five edits. Nothing in the architecture, the scope sections or the six answers
needs to change.

##### Change 1 in the confirmed technical facts for design-specification docs_layout_hardening (round 1)

Add the third caller and the synthesized topic, both checked in the source:

```text
- [prompt_workflow_post_commit.py](../../tools/prompt_workflow_post_commit.py)
  builds a topic from a `plan.<version>.<slug>.validation.md` filename and sets
  its draft path to `<that directory>/draft.<version>.<slug>.md` without
  requiring that file to exist. `plan_topics` then treats
  `select_document(root, topic, "plan") is None` as "this topic has no plan"
  and skips it. The module catches nothing.
```

##### Change 2 in the shared directory eligibility section for design-specification docs_layout_hardening (round 1)

The parent check must not become a draft-existence check. Add to the
candidate-discovery paragraph, or to the invalid-parent rule in the error
section:

```text
The canonical parent is the directory holding the topic's draft path. It is
validated as a directory against the recognized set; the draft file itself need
not exist and is never resolved for this check. A topic can carry a draft path
to a file that was removed or never written, which post-commit topic resolution
relies on.
```

##### Change 3 in the error information and caller boundaries section for design-specification docs_layout_hardening (round 1)

Name the third boundary and state its outcome, rather than leaving it to the
plan:

```text
`plan_topics` in post-commit topic resolution is the third caller. Its topic
directory is always a member of the recognized set, so the invalid-parent
failure cannot reach it. Fallback ambiguity can: a topic whose directory holds
only the validation plan currently yields `None` and is skipped, and a
fallback that finds one plan elsewhere now includes that topic while competing
fallback plans raise. That error propagates like any other; post-commit topic
resolution does not downgrade it to a missing plan.
```

If the intended outcome is instead that `plan_topics` keeps its current skip
semantics, say that and say how, because it cannot both propagate and skip.

##### Change 4 in the open questions section for design-specification docs_layout_hardening (round 1)

Add Q07 from the reviewer verdicts, on where the canonical-parent check is
enforced, with the same question shape as the six existing ones. Its answer
determines whether `find_matching_documents` still returns a list for an
invalid parent, which the scope-aware selection section currently leaves open.

##### Change 5 in the acceptance cases table for design-specification docs_layout_hardening (round 1)

Two rows. Correct the requirement basis on the freshness row, and add the
post-commit case:

```text
| Qualifying file added, renamed or removed between discovery calls | The next call observes the resulting eligibility. | Design Q05 |
| Topic built from a validation plan whose draft file does not exist | Its directory is the canonical parent; recognition and selection proceed without resolving the draft. | Issue Q10 |
```

### Writer instructions for design-specification docs_layout_hardening round 1

#### Writer instructions for the next layout-hardening design round for design-specification docs_layout_hardening (round 1)

1. Apply the five requested changes. Three add facts and consequences about
   `tools/prompt_workflow_post_commit.py`, one adds design Q07, one repairs two
   acceptance rows.
2. Change no existing answer. All six recommended directions are accepted, and
   the architecture, scope and out-of-scope sections stand as written.
3. Do not reopen the consolidated issue. Everything raised here is about how
   this design reaches its callers, not about what the behavior should be.
4. When adding Q07, keep `find_matching_documents` consistent with whichever
   answer it settles: the scope-aware selection section currently promises a
   list return shape while the error section promises validation before any
   fallback, and those two cannot both hold for an invalid parent.

The post-commit caller is the substance of this round. Two of its properties
matter and neither is visible from the functions this design already names: its
topic carries a draft path that need not exist, and its "has a plan" test reads
`None` from a selector that is about to gain a new way to fail.

Publish a replacement request for another automated round. With these edits and
nothing else changed, I expect that round to be convergence-ready. Consolidation
stays with the human at the convergence gate, and this answer does not
recommend it.

### Final reviewer decision for design-specification docs_layout_hardening round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-12T17:08:25+02:00
- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for design-specification docs_layout_hardening (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
Review round: 2

### Requestor assessment for design-specification docs_layout_hardening (round 2)

The design now addresses all five requested changes from round 1. The seven
questions cover the shared eligibility boundary, exact filename matching,
scope provenance, error reporting, freshness, filesystem failures and placement
of parent validation. No further missing design question was identified.

Existing options remain sufficient, and the recommended option A for Q01-Q06
is unchanged. New Q07 also recommends A: validate the parent in shared
candidate discovery so both public entry points report an invalid scope.
The body states this exception behavior explicitly while preserving each
operation's successful return shape.

The reviewer wording suggestions are applied, including the six accepted kinds
in Q02 and the post-commit consequence in Q04. The confirmed source facts now
include synthesized draft paths and the post-commit caller's unhandled errors.
The design distinguishes directory validation from draft-file existence and
states the outcomes for zero, one and multiple fallback plans.

The acceptance table covers freshness, missing synthesized draft files and
post-commit fallback. Its freshness basis names both Issue Q01, which requires
observable content updates, and Design Q05, which chooses uncached discovery.
The recognized-parent statement is qualified by an unchanged tree because
uncached calls do not provide an atomic filesystem snapshot.

The previously duplicated open-questions section has been replaced through
oqm with one section containing Q01-Q07 and their proposed answers. The design
remains unconsolidated and ready for independent review of this replacement.

### Change summary for design-specification docs_layout_hardening (round 2)

- Added the verified post-commit caller facts: validation-plan topic discovery
  synthesizes a draft path without requiring its file, skips a missing ordinary
  plan and has no exception handler.
- Clarified that canonical-parent validation checks the directory against the
  recognized set, retaining path normalization without resolving a draft
  document or requiring it to exist.
- Stated post-commit fallback outcomes: one ordinary plan elsewhere includes
  the topic, none preserves the skip, and competing plans propagate an error.
- Added Q07 with two alternatives and recommended answer A, enforcing the
  parent check in shared discovery for both public entry points.
- Added missing-draft and post-commit fallback acceptance rows and corrected
  the freshness basis to include Design Q05.
- Named the six accepted document kinds in Q02 and expanded Q04's option A con
  to describe the current post-commit caller's fallback-ambiguity consequence.
- Removed the duplicate question section and preserved the six existing
  recommended answers. No consolidated issue decision was changed.

### Writer response for design-specification docs_layout_hardening (round 2)

Writer response:

Accepted all five requested changes and the two wording refinements. There is
no substantive disagreement with round 1.

The source check of tools/prompt_workflow_post_commit.py confirms that
_topic_from_validation_plan constructs and normalizes a draft path without
checking existence. plan_topics enumerates recognized directories and skips
a topic when select_document returns None; it does not catch selection errors.
The design now makes these facts and their target consequences explicit.

Q07 selects validation in shared discovery. Both find_matching_documents and
select_document raise PromptWorkflowError for an invalid parent; an empty
list or None remains meaningful absence after valid scope selection. A draft
file that does not exist is not itself an invalid parent.

Two qualifications preserve the agreed behavior. The post-commit parent's
recognition is guaranteed with an unchanged tree, since Q05 and Q06 do not
promise atomic discovery. The freshness row cites Design Q05 as requested and
retains Issue Q01 for its observable content-change requirement.

The six existing answers remain option A. Please assess the added caller
contract, Q07 and their consistency with the acceptance cases. The issue is
settled, and this replacement does not reopen its decisions or consolidate
the design ahead of the human convergence choice.

### Reviewer focus for design-specification docs_layout_hardening (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-12T17:11:51+02:00
- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for design-specification docs_layout_hardening round 2

#### Reviewer assessment of the revised layout-hardening design for design-specification docs_layout_hardening (round 2)

All five requested changes are applied, both wording refinements landed, and the
contradiction that made round one necessary is gone. The document is ready for
the human's choice.

##### The three round-one findings are closed for design-specification docs_layout_hardening (round 2)

The confirmed-facts list now carries `prompt_workflow_post_commit.py` with the
two properties that made it matter: topics built from validation-plan filenames
assign a draft path in the same directory without requiring that draft to exist,
and `plan_topics` reads `None` as a reason to skip a topic with no exception
handler anywhere in the module.

Canonical-parent validation is now defined as a directory check. The
candidate-discovery section states it twice over, in the rule itself and in
Q07's body, and says why: post-commit topics rely on paths to drafts that were
removed or never written. An implementer can no longer read "the canonical
draft's parent" as an instruction to resolve a draft first.

The scope-aware selection section no longer promises a total list-returning
helper while the error section promises validation before any fallback. It
states that an unrecognized parent raises from both entry points and is not
represented by an empty list, and it points at Q07 for the placement decision.

##### The post-commit consequence is stated correctly, including its limit for design-specification docs_layout_hardening (round 2)

The caller-boundaries section says the post-commit parents are recognized "with
an unchanged tree". That qualification is right and is the kind of thing that
usually goes missing. `plan_topics` enumerates `docs_dirs` once and then calls
the selector per topic, each call re-deriving recognition; design Q05 chose
uncached discovery, so nothing promises those two observations agree. The
guarantee is about construction, not about atomicity, and the document now says
so rather than overclaiming.

The three outcomes are also right: a sole fallback plan includes a topic that
was previously skipped, no fallback plan preserves the skip, and competing
fallback plans raise through a caller that does not catch. That is the accepted
issue Q06 behavior reaching an existing caller, which is what the design says.

##### Independent check of what changed for design-specification docs_layout_hardening (round 2)

I reread the changed sections against the source rather than against the change
summary. The new facts hold: `_topic_from_validation_plan` builds
`path.parent / f"draft.{version}.{slug}.md"` and resolves it without an
existence test, and `plan_topics` skips on `None` with no handler in the module.
The six accepted kinds named in Q02 are correct, and the `requirement` selector
does map to the same prefixes as feature-request and issue, so calling it an
alias rather than a seventh kind is accurate.

The acceptance table is now sixteen rows and covers every settled issue decision
plus the three cases this design adds. Its bases are correct, including the
freshness row that cites the issue for the observable requirement and design
Q05 for the uncached choice.

##### Questions and answers for design-specification docs_layout_hardening (round 2)

Seven questions, each a design question rather than a requirement or plan
question, each with a material alternative. I would choose option A for all
seven. Q07 asks what I proposed and answers it the way the scope argument
points: an unrecognized parent invalidates the scope choice itself, so the check
belongs where scope is formed.

Nothing is left implicit that the plan would have to invent. Private helper
names, the file split and the test sequence are explicitly plan work, which is
the correct boundary.

### Question verdicts for design-specification docs_layout_hardening round 2

#### Reviewer verdicts on the seven design questions for design-specification docs_layout_hardening (round 2)

All seven are accepted as written. None is missing, redundant or outside design
scope, and none reopens a consolidated issue decision. No eighth question is
needed.

##### Design answers this reviewer would choose in round two for design-specification docs_layout_hardening (round 2)

| Question | Answer | Reason in one line |
| --- | --- | --- |
| Q01 | A | The duplicated rule is the defect, not the duplicated enumeration. |
| Q02 | A | The exact matcher already expresses the identity rule for all six accepted kinds. |
| Q03 | A | Scope should travel from where it was chosen, not be rediscovered. |
| Q04 | A | Both failures reach an established fatal boundary with no new public error contract. |
| Q05 | A | A cache would need a lifetime and an invalidation rule to buy back unmeasured reads. |
| Q06 | A | A retry classifier guesses at one concurrent mutation and ignores the rest. |
| Q07 | A | An unrecognized parent invalidates the scope choice, so the check belongs where scope is formed. |

##### Verdict on the two refined questions for design-specification docs_layout_hardening (round 2)

Q02's answer now names draft, feature-request, issue, design, plan and
validation-plan, and says the `requirement` selector is an alias rather than a
seventh kind. That removes the only ambiguity the reuse proposal carried.

Q04's option A con now names the post-commit consequence first and keeps the
typed-interface point second. That ordering is right: the caller that changes is
live, and programmatic recovery is hypothetical.

##### Verdict on the new Q07 for design-specification docs_layout_hardening (round 2)

Accepted as written, with answer A. The options are materially distinct and each
con is the real one. Option A's con is accurate rather than softened: the
list-returning helper does gain an exception its tests must account for, and the
sixteen tests touching these helpers are where that lands. Option B's con
correctly identifies the conflation of an invalid scope with absence, which is
the property the whole selection contract now depends on staying separate.

The body's closing sentence, that the check concerns the topic's directory
rather than the existence of its draft file, is the round-one finding folded
into the question that decides it. That is the right place for it.

##### Questions considered and not proposed for design-specification docs_layout_hardening (round 2)

Whether the fallback should be version-scoped rather than spanning every
recognized directory is settled by the consolidated issue, which chose every
other recognized directory across supported layouts. Filename matching still
requires the requested version, so the design faithfully implements it.

Repeated `docs_dirs` walks across successive role lookups are named in Q05's
option A con and accepted there. Symbolic-link policy is explicitly retained
rather than introduced. Private helper names, the file split and the test order
are plan work by the design's own scope statement.

### Convergence evidence for design-specification docs_layout_hardening round 2

Covered wording:

#### Covered wording for the layout-hardening design for design-specification docs_layout_hardening (round 2)

Two optional items. Neither changes an answer, an option or an acceptance
outcome, and the design is convergence-ready with or without them. Apply them
during consolidation if the human keeps this recommendation, or leave them.

##### Optional polish in the acceptance table for design-specification docs_layout_hardening (round 2)

One row still says "Canonical draft discovered in an unsupported or
identity-mismatched parent", which is the phrasing the rest of the document
moved away from once the check became a directory check. Suggested replacement:

```text
| Topic whose parent directory is unsupported or identity-mismatched | Selection reports the parent and never widens its search. | Issue Q10 |
```

The outcome and the basis are unchanged; only "canonical draft discovered"
becomes the directory the check actually reads.

##### Optional polish in the candidate discovery section for design-specification docs_layout_hardening (round 2)

The sentence "The exact private type and helper names remain plan details."
follows "reconstruct provenance." without a blank line, so it joins that
paragraph instead of standing as the scope boundary it states. A blank line
before it separates the two.

##### Wording confirmed as correct in round two for design-specification docs_layout_hardening (round 2)

The following read correctly and need no change: the post-commit entry in the
confirmed facts, the canonical-parent definition in the candidate-discovery
section, the invalid-parent raise in the list-returning helper paragraph, the
caller-boundaries paragraph including its unchanged-tree qualification and its
three fallback outcomes, the six accepted kinds in Q02, the reordered Q04 con,
all of Q07, and the three added or corrected acceptance rows.

Convergence rationale:

#### Convergence rationale for the layout-hardening design for design-specification docs_layout_hardening (round 2)

Round one accepted the architecture and found three gaps, all in one caller the
design had not opened. A topic's draft path is synthesized by post-commit topic
resolution and need not exist, so a parent check written as "resolve the draft,
then validate it" would have failed every post-commit topic. `plan_topics` uses
`None` from the selector as a plan-absence test and catches nothing, so the new
fallback and its ambiguity error change what that caller sees. And the document
promised both a total list-returning helper and validation before any fallback,
which cannot both hold.

Round two closes all three with facts I rechecked in the source rather than in
the change summary, and adds Q07 to decide where the parent check lives. The
answer places it in shared discovery, which is the placement the scope argument
supports and which makes the list-returning helper's new exception a stated
consequence instead of an accident.

Every design decision is settled. One eligibility boundary with independent
enumeration, exact-matcher reuse across six named document kinds, an internal
scoped candidate result, the existing error type carrying both new failures to
the existing fatal boundary, uncached discovery, propagated filesystem errors,
and parent validation at the discovery boundary. Sixteen acceptance rows carry
every consolidated issue decision plus the three cases this design adds, with
correct requirement bases.

The boundaries that stay out are declared rather than forgotten: private helper
names, the file split and the test sequence belong to the plan; layout
migration, body-based classification, local timestamp ties and role matching
breadth are out of scope; the optional-slug interface and its `NewDraftError`
are unchanged.

What remains is two cosmetic items recorded in the covered wording, one phrase
in an acceptance row and one missing blank line. Neither changes behavior and
neither justifies another automated round.

This recommendation is advisory and authorizes nothing. The consolidation
choice, and the labels offered for it, belong to the human at the convergence
gate.

### Writer instructions for design-specification docs_layout_hardening round 2

#### Writer instructions at the layout-hardening design convergence gate for design-specification docs_layout_hardening (round 2)

No change is requested. All five round-one edits are applied correctly, both
wording refinements landed, and Q07 asks and answers the missing question.

1. Present the seven questions, their recommended options and their answers to
   the human with the two registered labels, and make no edit before that
   choice.
2. If the human selects consolidation, the two cosmetic items in the covered
   wording may be applied with it. Skipping them changes nothing.
3. If the human selects another round instead, that round needs a reason from
   the human: this reviewer has none to supply.

Do not treat this recommendation as authorization. Consolidation, the design
decisions table and the removal of the open-questions section stay with the
owning workflow after the human confirms.

### Final reviewer decision for design-specification docs_layout_hardening round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-12T17:28:20+02:00
- Exchange: specification/design-specification/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/design.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
