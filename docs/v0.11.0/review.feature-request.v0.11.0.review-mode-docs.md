# Specification review transcript for v0.11.0

- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-18T23:16:54+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: request

### Review identity for feature-request review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
Review round: 1

### Requestor assessment for feature-request review-mode-docs round 1

The feature request is ready for independent question review. It keeps the requirement at feature scope: user-facing documentation coverage, expected workflow behavior, acceptance boundaries, and exclusions. It does not choose implementation files beyond the documentation surfaces already named by the umbrella, and it does not reopen protocol behavior settled by prerequisite items 1 through 5.

Nine questions cover the remaining material choices: Diataxis page boundaries, separate tutorials for both review families, command depth, complete recovery-state coverage, artifact naming authority, host-adapter presentation, coexistence with the established self-review loop, required navigation and inventory entry points, and validation while the umbrella's Markdown-check item remains pending.

Every question has three distinct options with pros and cons, a recommended option, an explicit answer, and a BBQ analogy whose concrete mapping is stated. No question absorbs the repository-wide Markdown checker from item 7 or the read-only commit-plan launcher from item 8.

### Change summary for feature-request review-mode-docs round 1

Created the focused `review-mode-docs` draft from ordered umbrella item 6, preserving its settled type, title, slug, version, inherited documentation layout, dependencies, operational constraints, and Diataxis ordering.

Created `docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md` with the user story, current documentation gap, required workflow coverage, authority and recovery boundaries, artifact examples, repository references, eleven acceptance criteria, and the dependency boundary.

Appended nine open questions through the `oqm` companion workflow. The umbrella draft remains unchanged, and the new draft and requirement are the only untracked project files on the `review-mode-docs` branch.

### Writer response for feature-request review-mode-docs round 1

Writer response: This is the first review round, so there is no earlier reviewer feedback or disagreement to carry forward. The writer asks the reviewer to identify missing feature-scope questions, weak or overlapping options, unsupported recommendations, and wording that could let documentation redefine settled protocol behavior.

The writer recommends keeping the nine proposed answers unless the reviewer finds a concrete gap against umbrella item 6. Suggestions that belong to the implementation design, file-by-file plan, Markdown-check item 7, or commit-plan-check item 8 should be returned as boundary observations rather than inserted into this feature request.

### Reviewer focus for feature-request review-mode-docs round 1

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-19T08:52:50+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: answer

### Reviewer assessment for feature-request review-mode-docs round 1

The feature request holds its boundary well. It documents settled behavior
from umbrella items 1 through 5, keeps protocol authority with those
requirements, and explicitly excludes the item 7 Markdown checker and the item
8 commit-plan launcher. The user story, gap list, workflow coverage, Diataxis
boundaries, and dependency statement are consistent with umbrella item 6, and
every repository path named in the reference list resolves in the working
tree.

Three defects block convergence.

First, acceptance criterion 10 and the recommended answer to Q09 both require
running "the project Markdown checks", and no such gate exists. The repository
declares its rule set in `.markdownlint.json` (MD013 off, MD033 limited to
`img`), but no launcher under `bin/` runs it, `ghog` has no Markdown step, and
building one is exactly the deferred item 7. Option Q09.3 therefore collapses
into option Q09.2 the moment implementation starts, and the effort would either
pass on evidence it cannot produce or silently pull item 7 forward. The
requirement must name the executable gates that do exist and state how the
declared Markdown rules are verified until item 7 ships.

Second, the reference list is materially incomplete and asymmetric between the
two review families, while acceptance criterion 5 and the accepted answer to
Q03 both put the complete launcher contract in reference documentation. The
list names `bin/code_review_request.bat`, `bin/code_review_evidence.bat`, and
`bin/code_review_answer.bat` but omits the shipped specification counterparts
`bin/spec_review_request.bat` and `bin/spec_review_answer.bat`. It names two of
the eight shipped review templates and omits `review-answer.template.md`,
`spec-review-request.template.md`, `spec-review-answer.template.md`,
`code-review-request.template.md`, `review-specification-transcript.template.md`,
and `review-code-transcript.template.md`. It also never names `pw`, although
the accepted answer to Q03 routes every normal journey through it.

Third, two accepted answers depend on artifacts that no acceptance criterion
requires. Q01.3 justifies itself with a coverage map proving which page
satisfies each criterion, and Q08.3 depends on an explicit affected-page
inventory. Neither is a deliverable anywhere in the requirement, so criteria 1
through 9 have no objective completion test.

Four material decisions are also missing as questions: the user-facing
terminology that separates the existing self-review loop from independent
review mode, whether the coverage map is a deliverable, whether wiki reference
pages may restate canonical instruction policy, and how the human-only forced
recovery operations are presented so documentation cannot be executed as an
ordinary automated procedure.

The nine existing questions are otherwise well built. Each has a stated
description, a BBQ analogy with a concrete mapping, three materially distinct
options with real consequences, a recommended option, and an explicit answer.
Eight of the nine recommended answers follow from the confirmed requirements
and from the implemented behavior; only Q09 does not.

### Question verdicts for feature-request review-mode-docs round 1

**Q01 Required Diataxis page boundaries — agree with Q01.3, with one added
obligation.** The three options are materially distinct and their consequences
are real. Dedicated pages for the complete journeys plus concise links from
existing entry points is the only option that satisfies both "complete
coverage" and "one Diataxis purpose per page" without rewriting correct older
material. The reviewer would choose Q01.3. The defect is that the answer text
leans on a coverage map ("A coverage map can prove which dedicated page
satisfies each acceptance criterion") that the requirement never asks anyone to
produce. Either promote it to a deliverable through new Q11 below, or delete
the claim from the answer.

**Q02 Separate first-use tutorials by review family — agree with Q02.2.**
The families differ in reviewed inputs, reviewer permissions, evidence, the
convergence signal (`consolidation-ready` against `commit-ready`) and the human
choices (`Consolidate` / `Revise and review again` against `Commit` / `Rework
and review again`), so a single branching tutorial would fail the linear
first-use property. Q02.3 is correctly rejected because it contradicts the gap
list. One inconsistency to repair: acceptance criterion 3 says "at least one
tutorial" for each family, which is weaker than the accepted answer. Tighten
criterion 3 to exactly one first-use tutorial per family, cross-linked.

**Q03 Command depth by documentation purpose — agree with Q03.3, wording
incomplete.** Layering is right: skill-level commands in tutorials and ordinary
how-to pages, the complete launcher contract in reference and recovery pages.
The recommended answer says normal journeys "should use the role commands
returned by `pw`", yet `pw` appears nowhere else in the requirement and is
absent from the reference list, so the accepted answer depends on an
unintroduced tool. Name `bin/prompt_workflow.bat` and the existing
`wiki/reference/pw-launcher.md` in the reference list, and state in the answer
that the complete contract means the operation, required context arguments,
final standard-output JSON object, `outcome`, `state`, and the exit `0` / `3` /
`2` meaning.

**Q04 Recovery state reference completeness — agree with Q04.3, add a source
rule.** The matrix-plus-procedures pairing is correct, because recovery is both
an inventory problem and a sequence problem. Add one constraint to the answer:
the matrix rows are derived from the shipped typed states and outcomes rather
than authored independently, so the reference cannot drift into a second and
conflicting policy source. This constraint also has to survive the new Q12
below.

**Q05 Artifact naming and returned-path authority — agree with Q05.3, sharpen
the authority wording.** Grammar for orientation plus returned-path authority
is the right rule, and Q05.1 is correctly rejected because nearby-name
discovery breaks as identity shapes grow. Make the authority statement exact:
the authoritative value is the `paths` object inside the single final JSON
object the launcher writes to standard output, and progress diagnostics on
standard error are never a path source. Also state that documented filenames
use repository-relative placeholders and are illustrative only.

**Q06 Host adapter documentation model — agree with Q06.3, and the adapter
table must be allowed to record gaps.** One canonical workflow plus a mapping
table matches the implemented thin-wrapper rule. The question assumes the three
hosts expose the same surface, and they do not: `.agents/llm-shared/skills/` and
`.agent/workflows/` both carry a `review-requestor` wrapper, while
`.claude/skills/` has `spec-review-requestor`, `spec-reviewer`,
`code-review-requestor`, and `code-reviewer` but no `review-requestor` entry.
Extend the answer so the adapter table records wrapper location, command
prefix, delegation boundary, and per-host coverage, including an absent
wrapper, rather than implying uniform coverage.

**Q07 Coexistence with the established self-review loop — agree with Q07.3, but
it is incomplete without terminology.** Preserving the self-review material and
adding an explicit comparison is right, because the no-marker path stays
supported behavior. The question does not settle what each concept is called,
and the collision is already in the tree: `wiki/how-to/answer-a-review-round.md`
and `wiki/explanation/why-the-llm-reviews-its-own-work.md` use "review" for the
human-answered self-review loop, which is a different thing from a second LLM
answering a durable exchange. Name those two pages in the question, and settle
the vocabulary through new Q10 below.

**Q08 Required project and wiki entry points — agree with Q08.3, make the
inventory concrete now.** Bounded inventory updates are correct, and Q08.2 is
rightly rejected as scope creep into correct self-review content. The stated
con, that the affected-page inventory is deferred to implementation, is
avoidable at feature scope: the candidate pages already exist and can be named,
namely `wiki/reference/skills-catalog.md`,
`wiki/reference/artifact-files.md`, `wiki/reference/aliases-and-launchers.md`,
`wiki/reference/templates.md`,
`wiki/reference/automation-and-direct-invocation.md`, and
`wiki/reference/repository-layout.md`. Listing them as the candidate set, with
implementation free to drop a page it proves unaffected, converts an open
implementation risk into a checkable acceptance boundary.

**Q09 Markdown validation before umbrella item 7 — disagree with the answer as
written; the recommended option is not executable.** The question frames the
right trade-off and correctly refuses to pull item 7 forward, but option Q09.3
says to run "the current project documentation and Markdown gates" and no
Markdown gate exists. `.markdownlint.json` declares the rule set, no `bin/`
launcher applies it, `ghog` has no Markdown step, and the only current rule
checker in the tree is a git-ignored provisional root helper that cannot serve
as acceptance evidence for a versioned requirement. As written, Q09.3 degrades
into Q09.2 during implementation while still claiming executable evidence.

The reviewer would keep option Q09.3 and repair its content so it is true:
name the executable gates that do exist and that this effort must keep green;
require link and path resolution for every documentation reference this effort
adds or changes; require explicit manual verification of the declared
`.markdownlint.json` rules with MD024 and MD025 called out, since
`instructions/review-requestor.md` forbids disabling them; and state that no
repository-wide Markdown checker is created here. Acceptance criterion 10 must
be rewritten in the same terms, because "the project Markdown checks report no
new finding" currently asserts a gate the repository does not have.

**Q10 missing: user-facing terminology for the two review concepts.** Q07
settles that both stay and are compared, but not what they are called. Without
settled names, the comparison cannot be written and criterion 9's one-purpose
rule does not prevent a reader from landing on the wrong page. This is feature
scope, because it fixes page titles, navigation labels, and the wording of
criteria 1, 2, and 6. Suggested options: keep both under "review" and
distinguish only in body text; rename the older pages; or fix two stable names,
such as the self-review loop for the human-answered open-question cycle and
independent review mode for the marker-gated two-agent exchange, use them
consistently in every new and touched page, and retain existing page filenames
so no external link breaks. The reviewer would choose the third option.

**Q11 missing: is the acceptance-to-page coverage map a deliverable.** Both
Q01.3 and Q08.3 rely on it and no criterion demands it. Suggested options: no
map, and implementation demonstrates coverage in the plan only; a transient
implementation-time note; or a small versioned coverage table in the effort
documentation that maps each acceptance criterion to the exact page that
satisfies it. The reviewer would choose the versioned table, because criteria 1
through 9 otherwise have no objective completion test and a later reader cannot
tell a link-only edit from complete coverage.

**Q12 missing: may wiki reference pages restate canonical instruction policy.**
Criterion 8 forbids duplicating policy bodies, but binds only adapter
documentation, while criterion 5 requires reference pages to define the marker,
paths, identity fields, roles, states, commands, outcomes, and exit behavior.
That is the same material `instructions/review-requestor.md` already owns, so
the requirement contains a latent duplication contradiction and no rule for
which source wins when they diverge. Suggested options: reference pages restate
the contract in full; reference pages carry only links; or reference pages
define the user-facing contract in their own words, name the canonical
instruction as authoritative for agent policy, and never restate a rule the
instruction owns without pointing at it. The reviewer would choose the third
option, and would extend criterion 8 to cover every new page rather than
adapters alone.

**Q13 missing: how are human-only forced recovery operations presented.**
Criteria 4 and 7 require documenting reclaim, forced recovery, repair,
resolution, archival, cancellation, and authorized resumption.
`instructions/review-requestor.md` restricts `reclaim --force`,
`complete --force`, `repair-request-transcript`, `resolve`, and `archive` to an
explicit human decision, and states that no automated role may substitute one
for another. A how-to page that lists them as ordinary numbered steps is
directly executable by an agent reading the wiki. Suggested options: document
them exactly like ordinary operations; omit them from how-to pages and leave
them in reference; or document them in how-to pages inside a clearly marked
human-decision section that states the precondition, the required human
decision, and the evidence each operation destroys or preserves. The reviewer
would choose the third option, since criteria 4 and 7 require the coverage and
only an explicit marking keeps the docs from widening automated authority.

### Requested changes for feature-request review-mode-docs round 1

Requested changes:

1. Repair Q09 and acceptance criterion 10 together, since both currently
   assert a Markdown gate the repository does not have. Keep option Q09.3 as
   the answer but rewrite its text so it names the executable gates that exist
   at implementation time, requires link and path resolution for every
   reference this effort adds or changes, requires explicit manual verification
   against the declared `.markdownlint.json` rules with MD024 and MD025 named,
   and states that no repository-wide Markdown checker is created here. Rewrite
   criterion 10 in the same terms. Do not cite the git-ignored provisional root
   helper as acceptance evidence.

2. Complete the "Code and documentation references" list so it covers both
   review families symmetrically. Add `bin/spec_review_request.bat`,
   `bin/spec_review_answer.bat`, and `bin/prompt_workflow.bat`. Add the missing
   shipped templates `review-answer.template.md`,
   `spec-review-request.template.md`, `spec-review-answer.template.md`,
   `code-review-request.template.md`,
   `review-specification-transcript.template.md`, and
   `review-code-transcript.template.md`. Add `wiki/reference/pw-launcher.md`,
   `wiki/how-to/answer-a-review-round.md`, and
   `wiki/explanation/why-the-llm-reviews-its-own-work.md` as the existing pages
   this effort must reconcile with.

3. Append Q10 on user-facing terminology for the two review concepts, with the
   three options and the recommended answer given in the verdicts, and make the
   settled names the ones used in criteria 1, 2, and 6.

4. Append Q11 on whether the acceptance-to-page coverage map is a deliverable,
   with the three options given in the verdicts. If the versioned table is
   accepted, add it as a new acceptance criterion and remove the unsupported
   coverage-map claim from the Q01 answer text.

5. Append Q12 on whether wiki reference pages may restate canonical
   instruction policy, with the three options given in the verdicts, and widen
   acceptance criterion 8 from adapter documentation to every new or changed
   page once the answer is settled.

6. Append Q13 on how the human-only forced recovery operations are presented,
   with the three options given in the verdicts, and make criteria 4 and 7
   consistent with the accepted answer.

7. Tighten acceptance criterion 3 from "at least one tutorial" per family to
   exactly one first-use tutorial per family, cross-linked, so it matches the
   accepted answer Q02.2.

8. Extend the Q03 answer text so "complete launcher contract" is defined as the
   operation, required context arguments, the single final standard-output JSON
   object, its `outcome` and `state`, and the meaning of exits `0`, `3`, and
   `2`.

9. Extend the Q04 answer text so the state matrix is stated to be derived from
   the shipped typed states and outcomes rather than authored independently.

10. Sharpen the Q05 answer text so the authoritative value is named exactly as
    the `paths` object inside the single final JSON object written to standard
    output, note that standard-error progress diagnostics are never a path
    source, and state that documented filenames are repository-relative
    placeholders.

11. Extend the Q06 answer text so the adapter table records wrapper location,
    command prefix, delegation boundary, and per-host coverage including an
    absent wrapper, and note the concrete case that `.agents` and `.agent`
    carry a `review-requestor` wrapper while `.claude/skills` does not.

12. Replace the abstract phrase "affected inventories" in the Q08 answer with
    the concrete candidate set `wiki/reference/skills-catalog.md`,
    `wiki/reference/artifact-files.md`,
    `wiki/reference/aliases-and-launchers.md`,
    `wiki/reference/templates.md`,
    `wiki/reference/automation-and-direct-invocation.md`, and
    `wiki/reference/repository-layout.md`, stating that implementation may drop
    a page it proves unaffected.

13. Name the two colliding existing pages inside the Q07 question description
    so the required comparison has concrete targets rather than a general
    reference to README and wiki pages.

### Writer instructions for feature-request review-mode-docs round 1

Apply the requested changes to
`docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md` only. The umbrella
draft `docs/v0.11.0/draft.v0.11.0.review-mode.md` and the focused draft stay
unchanged, and no protocol artifact is edited by hand.

Take the three blocking items first, in this order. Repair Q09 and acceptance
criterion 10, because they are the only place where the requirement claims
evidence the repository cannot produce. Complete the reference list, because
acceptance criterion 5 and the accepted answer to Q03 both depend on it.
Then append Q10 through Q13 through the `oqm` companion workflow, keeping the
established block shape: description, BBQ analogy closed by an explicit "In
this picture" mapping, three materially distinct options with pros and cons, a
recommended option with arguments, and an explicit answer with the reason it
must be accepted. The verdicts file supplies the options and the reviewer's
recommended answer for each of the four.

The remaining items are wording and consistency repairs inside existing blocks.
Do not renumber or reorder Q01 through Q09 while applying them, so the round-1
verdicts stay traceable.

Two boundary notes, returned as observations rather than as content to insert.
The wiki tutorials use an ordered `01` through `08` filename prefix, so two new
tutorials need positions in that sequence; that is a design or plan decision,
not feature scope, unless the answer to Q11 makes the coverage table depend on
it. Drift detection between documented commands and shipped launcher behavior
is likewise out of scope here; if the writer wants it, it belongs to a later
umbrella item, not to item 6.

Keep every answer that this review did not contest. Q01 through Q08 are
accepted as recommended, subject only to the listed wording repairs, and Q09
keeps option Q09.3 with corrected content rather than a different option.

After the edits, publish another automated review round. Do not consolidate:
four questions are newly open and one accepted answer changed its factual
basis, so this round is well past word polishing.

### Final reviewer decision for feature-request review-mode-docs round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-19T09:18:28+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: request

### Review identity for feature-request review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
Review round: 2

### Requestor assessment for feature-request review-mode-docs round 2

Round 1's three blocking defects are closed.

- The requirement no longer claims that a repository Markdown launcher or
  `ghog` Markdown phase exists. Its validation criterion now requires
  `ghog day`, `git diff --check`, local-link and repository-path resolution,
  and a manual check against `.markdownlint.json` with MD024 and MD025 active.
- The reference inventory now names the request and answer launchers for both
  review families, the prompt-workflow launcher, all eight shipped review
  templates, and the existing wiki pages whose terminology or launcher
  contract is affected.
- The acceptance-to-page coverage map and affected-page inventory are explicit
  versioned deliverables, giving criteria 1 through 11 objective completion
  evidence.

Q01 through Q09 retain their accepted choices with the requested wording
repairs. Q10 through Q13 settle stable terminology, coverage-table ownership,
the wiki-versus-instruction authority boundary, and presentation of human-only
forced recovery. Each question retains the required options, trade-offs,
recommendation, and explicit answer. No further requirement-level question or
scope leak is known.

### Change summary for feature-request review-mode-docs round 2

Only the reviewed feature request changed in response to round 1.

- Its references are now symmetric across specification and code review and
  include the prompt-workflow entry point, all shipped review templates, and
  the affected wiki entry points.
- Its acceptance criteria now use evidence available in the repository and
  require a versioned acceptance-to-page coverage table with concrete page
  dispositions.
- Its open-question section now contains the repaired Q01 through Q09 answers
  and the accepted Q10 through Q13 decisions.

The umbrella draft and focused draft are unchanged. The review transcript is
modified only by protocol-owned append operations.

### Writer response for feature-request review-mode-docs round 2

Writer response: All round-1 requested changes were accepted without disagreement.

The Q09 answer and criterion now describe factual validation evidence instead
of an unavailable Markdown gate. The incomplete reference surface is filled
in symmetrically. The coverage map and affected-page inventory are required
deliverables rather than supporting assumptions. The four proposed questions
were added with their recommended answers, and the wording repairs requested
for Q01 through Q09 were applied.

The tutorial filename-numbering and documentation-versus-launcher drift ideas
remain outside this requirement, as the reviewer classified them as boundary
observations for design or a later umbrella item.

### Reviewer focus for feature-request review-mode-docs round 2

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-19T10:09:59+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: answer

### Reviewer assessment for feature-request review-mode-docs round 2

All three round-1 blockers are genuinely closed, and the reviewer verified each
against the working tree rather than accepting the change summary.

The Markdown-gate defect is repaired honestly. `ghog day` exists and does what
criterion 10 now relies on: it walks check, then affected without coverage,
then full, stopping at the first non-green step. The requirement no longer
claims a Markdown launcher, no longer cites the ignored root helper, and states
plainly that the declared `.markdownlint.json` rules stay manually verified
with MD024 and MD025 active until item 7 ships. The reference surface is now
symmetric: `bin/spec_review_request.bat`, `bin/spec_review_answer.bat`,
`bin/prompt_workflow.bat`, all eight shipped review templates,
`wiki/reference/pw-launcher.md`, and the two colliding self-review pages all
exist and resolve. The coverage table is a required deliverable through
criterion 12 and question Q11, so criteria that were previously unverifiable
now have a completion test.

No question is missing from this round, and no accepted answer is contested.
Q01 through Q13 each carry a description, a BBQ analogy with an explicit
mapping, three materially distinct options, a recommendation, and an answer
that follows from confirmed requirements and implemented behavior. The four
questions added in round 2 settle exactly the decisions round 1 identified, and
the wording repairs requested for Q01 through Q09 were applied accurately. The
two boundary observations were correctly kept out of the requirement.

Three defects remain, and all three sit in the acceptance criteria rather than
in a decision.

Criterion 8 contradicts the accepted answers to Q01 and Q08. Round 1 asked to
widen the non-duplication rule beyond adapter documentation, and the widening
overshot: as written, every new or changed page must define the user-facing
contract in its own words and name the canonical instruction as authoritative.
Criterion 1 requires `README.md` to gain a pointer, and Q08.3 requires
inventory pages to gain a row or a link. Under criterion 8 those link-only
edits would each have to carry a contract definition and a policy-authority
statement. The operative rule in Q12.3 is narrower and correct: the obligation
attaches whenever a page summarizes a policy-owned rule, not to every touched
file.

Criterion 12 asks for a mapping that cannot exist for part of its range. It
requires the table to map criteria 1 through 11 to the exact pages that satisfy
them, but criterion 10 is validation evidence, criterion 11 is a scope
exclusion satisfied by adding nothing, and criterion 12 is the table itself.
Only criteria 1 through 9 are page-satisfiable. The criterion also never says
where the versioned table lives, which matters because criterion 9 governs
wiki pages and a coverage table serves no Diataxis purpose.

Criterion 10 names `git diff --check`, which inspects the working tree against
the index and therefore reports nothing about changes that are already staged.
A documentation effort that stages its work before validating would record a
clean result from a command that examined nothing.

These are narrow, mechanical repairs to the testable contract, not reopened
decisions. The requirement is one round from convergence.

### Question verdicts for feature-request review-mode-docs round 2

No question is missing in this round, and the reviewer contests no answer. The
verdicts below confirm each accepted choice and record what the round-1 repair
actually changed.

**Q01 Required Diataxis page boundaries — accepted, repair confirmed.** The
answer no longer asserts an undelivered coverage map; it now names the Q11
table as a separate deliverable that proves completeness. Option Q01.3 remains
the right choice for the same reason as round 1. Note that criterion 8 as
currently written works against this answer, which item 1 of the requested
changes repairs.

**Q02 Separate first-use tutorials by review family — accepted, repair
confirmed.** Criterion 3 now reads "exactly one" per family and cross-linked,
so the criterion and the accepted option agree.

**Q03 Command depth by documentation purpose — accepted, repair confirmed.**
The recommended option now defines the complete launcher contract as the
operation, its required context arguments, the single final standard-output
JSON object, its `outcome` and `state`, the meaning of exits `0`, `3`, and `2`,
and the authority boundary. That matches the shipped result and exit contract.
The answer names `bin/prompt_workflow.bat` as the routing entry point, and the
reviewer confirmed it is the launcher aliased `pw`.

**Q04 Recovery state reference completeness — accepted, repair confirmed.**
The added sentence requiring matrix rows to be derived from the shipped typed
states and outcomes closes the drift risk, and it is consistent with the Q12
source-of-truth rule.

**Q05 Artifact naming and returned-path authority — accepted, repair
confirmed.** The authority is now named exactly: the `paths` object inside the
launcher's single final standard-output JSON object, with standard-error
progress diagnostics excluded as a path source. This matches the documented
behavior that a wait writes periodic diagnostics to standard error and nothing
to standard output before the final object.

**Q06 Host adapter documentation model — accepted, repair confirmed.** The
question description now records the real asymmetry, and the answer requires
the adapter table to show per-host coverage including an absent wrapper. The
reviewer reconfirmed the underlying fact: `.agents/llm-shared/skills/` and
`.agent/workflows/` both carry a `review-requestor` wrapper and
`.claude/skills/` does not.

**Q07 Coexistence with the established self-review loop — accepted, repair
confirmed.** The description now names `wiki/how-to/answer-a-review-round.md`
and `wiki/explanation/why-the-llm-reviews-its-own-work.md`, so the required
comparison has concrete targets, and Q10 supplies the vocabulary the comparison
needs.

**Q08 Required project and wiki entry points — accepted, repair confirmed.**
The abstract phrase is replaced by the concrete candidate set, and the
disposition of each candidate is recorded in the Q11 table. The stated con is
now an honest cost rather than a deferred unknown.

**Q09 Markdown validation before umbrella item 7 — accepted; the round-1
disagreement is resolved.** Option Q09.3 now describes evidence this repository
can actually produce. The reviewer verified that `ghog day` is a real
subcommand that walks check, then affected without coverage, then full,
stopping at the first non-green step, and that no `bin/` launcher applies
`.markdownlint.json`. Refusing to cite the ignored helper is correct. One
precision point remains, carried as item 3 of the requested changes: the
`git diff --check` half of the evidence does not see staged changes. A second,
optional point: criterion 10 says `ghog day` passes, which is the right gate,
but a pre-existing red chain unrelated to this effort is a stop-and-report
condition rather than work item 6 absorbs; saying so would keep the criterion
from being read as a repair obligation.

**Q10 Stable names for the two review concepts — accepted as recommended.**
`self-review loop` and `independent review mode`, with existing filenames
retained, is the option the reviewer would choose. It gives criteria 1, 2, and
6 unambiguous vocabulary, and it avoids Q10.2's link breakage across correct
established pages. The stated con is accurate: some existing pages will show a
display name that intentionally differs from their filename.

**Q11 Versioned acceptance-to-page coverage table — accepted as recommended,
with a definitional repair.** Option Q11.3 is right, and it is what makes
criteria 1 through 9 objectively checkable. Two defects belong to criterion 12
rather than to the answer. The range "criteria 1 through 11" over-reaches,
because criterion 10 is validation evidence, criterion 11 is satisfied by
adding nothing, and criterion 12 is the table itself; only criteria 1 through 9
map to pages. The location of the versioned table is also unstated, and since
criterion 9 governs every new or changed wiki page while a coverage table
serves no Diataxis purpose, the requirement should place the table in the
effort documentation rather than the wiki tree.

**Q12 Boundary between wiki contract and instruction policy — accepted as
recommended.** Option Q12.3 is the correct rule, and its wording is precise:
define the user-facing contract in the wiki's own words, name canonical
instructions as authoritative for agent policy, and point to an instruction
whenever a reference summarizes a policy-owned rule. The defect is that
criterion 8 restates this rule unconditionally, which the answer itself does
not do. The criterion, not the answer, needs the repair.

**Q13 Human-only forced recovery presentation — accepted as recommended.**
Option Q13.3 is the option the reviewer would choose. Marked human-decision
sections keep criteria 4 and 7 satisfiable without letting an agent reading the
wiki treat `reclaim --force`, `complete --force`, `repair-request-transcript`,
`resolve`, or `archive` as ordinary automated steps. The requirement now
carries that constraint in criteria 4 and 7 as well as in the answer, which is
the right redundancy for a safety boundary.

### Requested changes for feature-request review-mode-docs round 2

Requested changes: Three repairs, all inside the acceptance criteria. No question is reopened and
no answer changes.

1. Rewrite acceptance criterion 8 so its obligation is conditional, because as
   written it contradicts the accepted answers to Q01 and Q08. Criterion 1
   requires `README.md` to gain a pointer and Q08.3 requires inventory pages to
   gain a row or a link, yet criterion 8 currently demands that every new or
   changed page define the user-facing contract in its own words and name the
   canonical instruction as authoritative. Restate it in the narrower form
   Q12.3 already uses, for example:

   > A new or changed page that summarizes a policy-owned rule states that rule
   > in its own words, names the canonical instruction that owns it as
   > authoritative for agent policy, and does not copy that policy body. A page
   > that only gains a cross-link or an inventory row carries no such
   > obligation. The adapter table records wrapper location, command prefix,
   > delegation boundary, and per-host coverage, including an absent wrapper.

2. Repair acceptance criterion 12 on two points. First, narrow the mapped range
   from "criteria 1 through 11" to the criteria a page can satisfy, and record
   the rest as evidence rather than as page mappings: criterion 10 is
   validation evidence, criterion 11 is satisfied by adding nothing, and
   criterion 12 is the table itself. Second, state where the versioned table
   lives, since criterion 9 governs every new or changed wiki page and a
   coverage table serves no Diataxis purpose. For example:

   > A versioned acceptance-to-page coverage table maps criteria 1 through 9 to
   > the exact pages that satisfy them and records criteria 10 through 12 as
   > evidence entries rather than page mappings. It also records the
   > disposition of the candidate inventory pages: [keep the existing list].
   > Implementation may omit a candidate only when the table records why that
   > page is unaffected. The table is effort documentation under
   > `docs/v0.11.0/` rather than a wiki Diataxis page, so criterion 9 does not
   > apply to it.

3. Repair the `git diff --check` evidence in acceptance criterion 10 and in the
   Q09 option and answer text. That command compares the working tree against
   the index and reports nothing about changes that are already staged, so an
   effort that stages its work before validating would record a clean result
   from a command that examined nothing. Require both forms, for example
   "`git diff --check` and `git diff --cached --check` report nothing", or
   state explicitly that the check runs before staging.

Optional polish, at the writer's discretion and not required for convergence.

- In criterion 10, note that a pre-existing red `ghog day` chain unrelated to
  this effort is a stop-and-report condition rather than work item 6 absorbs,
  so the criterion is not read as an obligation to repair unrelated failures.
- The requirement's own prose still alternates between `review mode`,
  `review-mode`, and `independent review mode`. Criterion 6 fixes the two
  user-facing names for the documentation; applying them consistently in the
  requirement body would remove the last ambiguity for the design phase.

### Writer instructions for feature-request review-mode-docs round 2

Apply the three requested repairs to
`docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md` only. The umbrella
draft and the focused draft stay unchanged, and no protocol artifact is edited
by hand.

All thirteen answers stand. Do not reopen, renumber, or restate any question,
and do not change any recommended option. Every edit in this round lands in
acceptance criteria 8, 10, and 12, plus the Q09 option and answer text where it
repeats the `git diff --check` evidence. Criterion 8 is the one that matters
most: it currently contradicts the accepted answers to Q01 and Q08, so an
implementer following it literally would owe a contract definition on a page
that gained only a cross-link.

Round 1 caused the criterion 8 defect. The reviewer asked for the
non-duplication rule to be widened beyond adapter documentation, and the
widening was applied more broadly than the accepted Q12.3 rule supports. Take
the narrower conditional form from Q12.3 rather than inventing new wording, so
the criterion and the answer say the same thing.

The two optional polish items may be applied or skipped without affecting the
next disposition.

Publish another automated review round after the edits. The reviewer expects
that round to be convergence-ready: no question is missing, no answer is
contested, and the remaining scope is three mechanical criteria repairs. If the
three repairs land as described and nothing else changes, the next round should
reach the human consolidation gate.

### Final reviewer decision for feature-request review-mode-docs round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-19T10:18:50+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: request

### Review identity for feature-request review-mode-docs round 3

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
Review round: 3

### Requestor assessment for feature-request review-mode-docs round 3

The three round-2 blocking defects are closed without reopening any decision.

- Criterion 8 now applies the policy-authority and no-copy obligation only to
  pages that summarize a policy-owned rule; link-only and inventory-row edits
  are explicitly exempt.
- Criterion 12 maps page-satisfiable criteria 1 through 9, records criteria 10
  through 12 as evidence entries, and places the versioned coverage table in
  effort documentation under `docs/v0.11.0/` outside the wiki Diataxis set.
- Criterion 10 and Q09 now require both `git diff --check` and
  `git diff --cached --check`, covering unstaged and staged changes.

No question is missing. Q01 through Q13 remain sufficient, their recommended
options and answers are unchanged, and every required round-2 wording repair
is present. The requirement is ready for convergence review.

### Change summary for feature-request review-mode-docs round 3

Only the reviewed feature request changed since round 2.

- Acceptance criteria 8, 10, and 12 received the three requested mechanical
  repairs.
- Q09's option and recommended-answer text now names both unstaged and staged
  whitespace checks.

The umbrella draft, focused draft, all other questions, and all recommended
answers are unchanged. The transcript remains protocol-owned.

### Writer response for feature-request review-mode-docs round 3

Writer response: All three requested changes were accepted without disagreement and applied in
the exact scope identified by the reviewer.

The two optional polish items were intentionally deferred. They were explicitly
non-blocking, and changing additional prose would expand a round the reviewer
expected to contain only the three mechanical contract repairs. No question
was reopened, renumbered, or given a different recommended option.

### Reviewer focus for feature-request review-mode-docs round 3

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-19T10:26:40+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: answer

### Reviewer assessment for feature-request review-mode-docs round 3

The three round-2 defects are closed, and the repairs are surgical. The
reviewer verified the current document rather than accepting the change
summary.

Criterion 8 now carries the conditional obligation. It applies to a new or
changed page that summarizes a policy-owned rule, exempts a page that only
gains a cross-link or an inventory row, and keeps the adapter-table clause
intact. The contradiction with criterion 1 and with the accepted answer to Q08
is gone: a `README.md` pointer or a single inventory row no longer drags a
contract definition and a policy-authority statement behind it. The wording
matches the accepted Q12.3 rule rather than inventing a new formulation, which
is what round 2 asked for.

Criterion 12 now maps only the page-satisfiable criteria 1 through 9 to exact
pages and records criteria 10 through 12 as evidence entries. It also places
the versioned table in effort documentation under `docs/v0.11.0/` rather than
in the wiki Diataxis set, and states that criterion 9 does not apply to it. The
candidate inventory list and the omission rule survive unchanged. Both round-2
defects in this criterion are addressed.

Criterion 10 now requires `ghog day`, `git diff --check`, and
`git diff --cached --check`, and the same triple appears in the Q09 option text
and in the recommended-answer text, so the criterion and the answer state the
same evidence. That pair covers both unstaged and staged changes, which matters
here because the effort's new pages are untracked until they are staged.

Nothing else moved. All thirteen questions keep their titles, positions, and
numbering, and every recommended option and answer is unchanged: Q01.3, Q02.2,
Q03.3, Q04.3, Q05.3, Q06.3, Q07.3, Q08.3, Q09.3, Q10.3, Q11.3, Q12.3, Q13.3.
The umbrella draft and focused draft are untouched.

The writer deferred the two optional polish items and explained the reason.
That is a sound call. Both were explicitly non-blocking, one concerns the
requirement's own prose rather than the documentation this effort delivers, and
widening a round that was scoped to three mechanical contract repairs would
have added review surface for no acceptance benefit. The reviewer does not
re-raise them as changes.

Every in-scope decision is now settled. The thirteen questions cover the
material feature-scope choices for a documentation requirement: page
boundaries, one first-use tutorial per review family, layered command depth,
recovery-reference shape, returned-path authority, host-adapter presentation,
coexistence with the self-review loop, required entry points and inventories,
validation evidence available before umbrella item 7, stable terminology,
the versioned coverage table, the wiki-versus-instruction authority boundary,
and the presentation of human-only forced recovery. Every path the requirement
names resolves in the working tree, every executable gate it names exists, and
the acceptance criteria are internally consistent with the answers they
implement.

No question is missing, no answer is contested, and no substantive change
remains. Only wording-level polish is left, and none of it blocks
implementation. The reviewer recommends convergence.

### Question verdicts for feature-request review-mode-docs round 3

No question is missing, and the reviewer contests no answer. Every recommended
option is the one the reviewer would choose. The verdicts below close each
question for this exchange.

**Q01 Required Diataxis page boundaries — settled at Q01.3.** Dedicated pages
for the complete journeys and contracts, with concise links from existing entry
points, is the only option that satisfies both complete coverage and one
Diataxis purpose per page. The answer correctly defers proof of completeness to
the Q11 table instead of asserting an undelivered artifact, and the round-2
conflict with criterion 8 is now resolved in the criterion.

**Q02 Separate first-use tutorials by review family — settled at Q02.2.** Two
cross-linked tutorials. The families differ in reviewed inputs, evidence,
reviewer permissions, convergence signal, and human choices, so a branching
single tutorial would lose the linear first-use property. Criterion 3 states
"exactly one" per family and agrees with the answer.

**Q03 Command depth by documentation purpose — settled at Q03.3.** Skill-level
commands in tutorials and ordinary how-to pages, complete launcher contract in
reference and recovery pages. The contract is defined precisely as the
operation, required context arguments, the single final standard-output JSON
object, its `outcome` and `state`, the meaning of exits `0`, `3`, and `2`, and
the authority boundary. `bin/prompt_workflow.bat` is correctly named as the
routing entry point.

**Q04 Recovery state reference completeness — settled at Q04.3.** A complete
state, owner, action, and result matrix plus focused procedures for the
multi-step cases. Deriving matrix rows from the shipped typed states and
outcomes keeps the reference from becoming a second policy source, which is
consistent with the Q12 rule.

**Q05 Artifact naming and returned-path authority — settled at Q05.3.** Naming
grammar for orientation, with authority resting on the `paths` object inside
the launcher's single final standard-output JSON object. Excluding
standard-error progress diagnostics as a path source is correct and matches the
documented wait behavior.

**Q06 Host adapter documentation model — settled at Q06.3.** One canonical
workflow plus an adapter table that records wrapper location, command prefix,
delegation boundary, and per-host coverage including an absent wrapper. The
question description carries the real asymmetry, which the reviewer verified
again: `.agents/llm-shared/skills/` and `.agent/workflows/` carry a
`review-requestor` wrapper and `.claude/skills/` does not.

**Q07 Coexistence with the established self-review loop — settled at Q07.3.**
Keep both, compare them explicitly, and link each from the points where opt-in
and human stops differ. The two colliding pages are named, and Q10 supplies the
vocabulary that makes the comparison writable.

**Q08 Required project and wiki entry points — settled at Q08.3.** The two
named top-level entry points plus the concrete candidate inventory set, with
each candidate's disposition recorded in the Q11 table. Criterion 8's new
exemption for a page that only gains a cross-link or inventory row makes this
answer executable as written.

**Q09 Markdown validation before umbrella item 7 — settled at Q09.3.** The
option, the recommendation, and criterion 10 now name the same triple of
`ghog day`, `git diff --check`, and `git diff --cached --check`, so the answer
and the criterion cannot drift. The reviewer reconfirmed that `ghog day` is a
real subcommand and that no `bin/` launcher applies `.markdownlint.json`.
Refusing to cite the ignored root helper and explicitly deferring the
repository-wide checker to item 7 keeps the umbrella order intact.

**Q10 Stable names for the two review concepts — settled at Q10.3.**
`self-review loop` for the human-answered open-question cycle and
`independent review mode` for the marker-gated two-agent exchange, with
existing filenames retained so no external link breaks. Criteria 1, 2, and 6
use the settled names.

**Q11 Versioned acceptance-to-page coverage table — settled at Q11.3.** The
table is a versioned deliverable. Criterion 12's repaired range and stated
location remove the two round-2 defects: only criteria 1 through 9 map to
pages, criteria 10 through 12 are recorded as evidence, and the table lives in
effort documentation rather than the wiki, so criterion 9 does not reach it.

**Q12 Boundary between wiki contract and instruction policy — settled at
Q12.3.** Define the user-facing contract in the wiki's own words, name the
canonical instruction as authoritative for agent policy, and point to an
instruction whenever a reference summarizes a policy-owned rule. Criterion 8
now restates this conditionally rather than universally, so the criterion and
the answer finally agree.

**Q13 Human-only forced recovery presentation — settled at Q13.3.** Forced
operations appear only inside marked human-decision sections stating the
precondition, the required authority, and the evidence each operation preserves
or removes. Criteria 4 and 7 carry the same constraint, which is the right
redundancy for a boundary that keeps an agent reading the wiki from treating
`reclaim --force`, `complete --force`, `repair-request-transcript`, `resolve`,
or `archive` as ordinary automated steps.

### Convergence evidence for feature-request review-mode-docs round 3

Covered wording: The reviewer read the complete current specification and confirmed the
following wording as covered and accurate.

Acceptance criterion 8 reads: a new or changed page that summarizes a
policy-owned rule states that rule in its own words, names the canonical
instruction that owns it as authoritative for agent policy, and does not copy
that policy body; a page that only gains a cross-link or an inventory row
carries no such obligation; and the adapter table records wrapper location,
command prefix, delegation boundary, and per-host coverage, including an absent
wrapper. This matches the accepted answer to Q12 and no longer conflicts with
criterion 1 or with the accepted answer to Q08.

Acceptance criterion 10 reads that `ghog day`, `git diff --check`, and
`git diff --cached --check` pass, that every added or changed local link and
named repository path resolves, and that changed Markdown is manually checked
against `.markdownlint.json` with MD024 and MD025 explicitly kept active, with
no repository-wide Markdown checker created by this effort. The same three
commands appear in the Q09 option text and in the Q09 recommended-answer text.

Acceptance criterion 12 reads that a versioned acceptance-to-page coverage
table maps criteria 1 through 9 to the exact pages that satisfy them, records
criteria 10 through 12 as evidence entries rather than page mappings, records
the disposition of the six named candidate inventory pages, permits omitting a
candidate only when the table records why that page is unaffected, and is
effort documentation under `docs/v0.11.0/` rather than a wiki Diataxis page, so
criterion 9 does not apply to it.

All thirteen question titles, positions, options, recommendations, and answers
are covered as they currently stand, with the answers remaining Q01.3, Q02.2,
Q03.3, Q04.3, Q05.3, Q06.3, Q07.3, Q08.3, Q09.3, Q10.3, Q11.3, Q12.3, and
Q13.3.

The reference inventory is covered as accurate. Every instruction, template,
launcher, and wiki path it names resolves in the working tree, both review
families are represented symmetrically, and the eight shipped review templates
are all listed.

Two wording-level observations remain, and neither blocks consolidation. They
are recorded here so the human choosing at the gate sees the complete picture,
and either may be folded in during consolidation or left alone.

First, criterion 10 says changed Markdown is checked against
`.markdownlint.json`. That file sets only MD013 off and MD033 to `img`, so the
operative rule set is the markdownlint defaults as modified by it. Naming MD024
and MD025 explicitly already carries the point that matters, so this is
precision rather than correction.

Second, the requirement's own prose still alternates between `review mode`,
`review-mode`, and `independent review mode`. Criterion 6 fixes the two names
for the delivered documentation, which is the binding scope, so the
requirement's internal phrasing does not affect acceptance. The writer deferred
this deliberately in round 3 and the reviewer agrees with that call.

Convergence rationale: This exchange reaches the convergence bar because every in-scope decision is
settled and no more than wording-only edits remain.

The three rounds each closed a distinct class of defect and the trend is
monotone. Round 1 found three blockers: an acceptance criterion and an answer
that both required a Markdown gate the repository does not have, a reference
inventory that was incomplete and asymmetric across the two review families,
and two accepted answers that leaned on deliverables the requirement never
demanded. It also identified four missing feature-scope decisions. Round 2
verified all three blockers closed against the working tree, accepted the four
new questions, and found three narrower defects, all inside the acceptance
criteria rather than in any decision. Round 3 verified those three repairs and
found nothing further.

Each round's remaining work was strictly smaller and more mechanical than the
round before it, and this round found no new defect at all. That is the shape
of a converged specification rather than a stalled one.

The requirement is implementable as written. Thirteen questions cover the
material feature-scope choices for a documentation effort, each with three
materially distinct options, stated consequences, a recommendation, and an
explicit answer. The acceptance criteria are internally consistent with those
answers, which was the exact thing round 2 found broken and round 3 fixed:
criterion 8 no longer contradicts criteria 1 and the Q08 answer, criterion 12
no longer asks for a mapping that cannot exist, and criterion 10's evidence now
covers both staged and unstaged changes.

The requirement is also factually grounded. Every instruction, template,
launcher, and wiki page it names resolves in the working tree. Every executable
gate it requires exists, `ghog day` included. The one place where the
repository lacks a tool, the Markdown checker, is stated honestly as a manual
verification with the automation explicitly deferred to umbrella item 7, which
respects the umbrella's declared dependency order.

The scope boundary holds. The requirement documents settled behavior from
umbrella items 1 through 5, keeps protocol authority with those completed
efforts, and adds neither the item 7 Markdown checker nor the item 8
commit-plan launcher. The two boundary observations raised in round 1, tutorial
filename numbering and documentation-versus-launcher drift detection, were
correctly kept out as design-phase or later-umbrella concerns.

Only two wording-level observations remain, both recorded in the covered
wording and neither affecting acceptance or implementation.

This recommendation is advisory. It does not authorize consolidation. The
choice between `Consolidate` and `Revise and review again` belongs to the human
at the durable gate, and the reviewer takes no part in it.

### Writer instructions for feature-request review-mode-docs round 3

No changes are requested. Do not edit
`docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md` in response to this
answer, and do not reopen, renumber, or restate any question.

Present this recommendation to the human at the durable convergence gate,
together with the requestor's own assessment and the identity summary, and
offer the registered choices `Consolidate` and `Revise and review again`. This
reviewer recommendation is advisory and authorizes nothing on its own.

If the human chooses `Consolidate`, fold the thirteen answers into the
requirement through the owning consolidation workflow. The two wording-level
observations in the covered wording may be applied during that consolidation or
left alone; neither is required and neither changes any decision. If either is
applied, keep criterion 6's settled names, `self-review loop` and
`independent review mode`, exactly as they stand.

If the human chooses `Revise and review again`, treat their guidance as the
scope of the next round. Nothing in this review contributes work to such a
round: the reviewer found no missing question, contested no answer, and
requested no change.

Two notes for the phases that follow, carried forward rather than inserted into
the requirement. The wiki tutorials use an ordered `01` through `08` filename
prefix, so the two new first-use tutorials need positions in that sequence;
that is a design or plan decision. Drift detection between documented commands
and shipped launcher behavior remains out of scope for umbrella item 6.

### Final reviewer decision for feature-request review-mode-docs round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-08-19T10:54:45+02:00
- Exchange: specification/feature-request/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/feature-request.v0.11.0.review-mode-docs.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
