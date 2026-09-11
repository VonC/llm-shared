# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/markdown-check
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-24T11:07:14+02:00
- Exchange: specification/plan/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for plan markdown-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.markdown-check.md
Review round: 1

### Requestor assessment for plan markdown-check (round 1)

#### Writer assessment before the markdown-check plan review for plan markdown-check (round 1)

The plan translates the consolidated design into three test-first slices:
shared parsing and rules, policy and direct execution, then repository rollout.
It names every production, test, gate, repair, baseline, and documentation file;
records physical-line baselines and the 650-line ceiling; and creates a matching
three-step validation skeleton.

Three implementation questions remain and have materially different execution
effects: the stable public Python command, the source of truth for the first
baseline records, and the checkpoint for the human-only transcript repair. The
reviewer should also check step ordering, file responsibility, test package
placement, line-budget coverage, acceptance breadth, and whether any task
reopens a settled design choice.

No reviewer wording exists yet for round 1.

### Change summary for plan markdown-check (round 1)

#### Initial markdown-check implementation-plan changes for plan markdown-check (round 1)

This first plan request contains the following new artifacts and aligned source
clarifications.

- Created `docs/v0.11.0/plan.v0.11.0.markdown-check.md` with three numbered,
  file-based implementation steps and shared execution commands.
- Created `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` with matching
  not-started review sections and literal empty-check placeholders.
- Added the required file-based IO cost clarification to the draft, requirement,
  design, plan, and validation skeleton.
- Added three implementation-level open questions with recommended answers.

### Writer response for plan markdown-check (round 1)

Writer response: #### Writer response at the start of markdown-check plan review for plan markdown-check (round 1)

This is the initial plan-review request. There is no earlier reviewer feedback
or disagreement. Please review all three steps, the validation alignment, and
the three implementation questions, and identify every missing task that must be
settled before Step 1 can start.

### Reviewer focus for plan markdown-check (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-24T11:34:50+02:00
- Exchange: specification/plan/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for plan markdown-check round 1

The plan is well structured. Three test-first slices with a clean dependency
order, every production and test file named, a matching validation skeleton, an
explicit complexity bound, and an IO-cost clarification that keeps one parse per
file. The three questions are genuine implementation choices rather than design
matters reopened, and the reviewer agrees with all three recommended answers.

Two blocking gaps sit in Step 1, which matters because Step 1 is the next action.
Two smaller corrections follow from checking the plan's stated facts against the
repository.

### Step 1 cannot classify adapters as currently specified (round 1)

Step 1 owns `LS001` and `LS002`, and its tests are required to cover "adapter
exemption", so adapter classification is Step 1 work. The plan never says where
that classification lives. Step 1's classes and behavior list names only
`MarkdownSource`, `Finding`, the rule functions, and `qualify_round_headings`,
and no production file anywhere in the plan is a classifier.

The larger problem is the data it would need. The consolidated design requires
the bounded pointer classifier to find "a resolvable repository-relative
Markdown link to a canonical instruction or rule". The design's source model
records frontmatter bounds, fenced-code bounds, ATX headings with line and
level, list-block boundaries, raw HTML elements, and non-blank body lines. There
is no link token in that list, and the design also states that rule evaluators
"receive the source model and never rescan raw text independently". Step 1's
source-model tests mirror the same token list and likewise omit links.

So the pointer classifier has no supported way to see the one signal it is
defined by. `source.py` needs a Markdown-link token, Step 1's source-model tests
need to cover it, and the plan needs to name the classifier's home.

### The resolvable-link requirement crosses a step boundary (round 1)

Step 1 states that rule functions perform "pure source-model evaluation with no
filesystem access". Resolvability cannot be established under that constraint
without deciding what the word means.

Read as an existence check, classification must consult either the filesystem,
which Step 1 forbids, or the tracked inventory, which Step 2 builds. Step 2 is
the step that adds the Git inventory, so a Step 1 classifier cannot reach it.
Read syntactically, as a repository-relative path ending in `.md`, Step 1 stays
self-contained and pure.

The plan must choose. The reviewer recommends the syntactic reading in Step 1,
which keeps the purity constraint and lets `LS001` and `LS002` complete in their
own step, and an optional inventory-backed existence check in Step 2 if the
writer wants the stronger guarantee. What the plan cannot do is leave Step 1
holding a requirement that its own constraints forbid it from meeting.

### The 650-line ceiling is not the repository ceiling (round 1)

The plan calls 650 the "repository ceiling" in its confirmed technical facts and
repeats it in every Step 1 line-budget entry, and the shared execution checklist
makes it commit-blocking: "Split a responsibility before commit if any Python
file exceeds 650 lines."

The enforced gate is 700. `check.bat` line 106, `bin/check_big_files.bat` line
15, and `bin/python_check.bat` line 105 all default to 700, and no
`PYTHON_BIG_FILE_LINE_LIMIT` override exists anywhere in the repository. The
figure 650 survives only in `CHANGELOG.md` and v0.1.0-era design and plan
documents, which describe an earlier gate.

A stricter plan-local budget is a perfectly good choice and the reviewer has no
objection to 650 as a target. It should be labelled as one rather than asserted
as a repository fact, because an implementer who reads the confirmed-facts
section will believe a 660-line file fails a gate that would in fact pass it.

Every other stated figure checks out exactly: `tools/review_markdown_headings.py`
at 87 lines, its test file at 104, `check.bat` at 215, and
`.claude/skills/humanizer/SKILL.md` at 412 with the `MD032` repair at line 260.

### The Q03 checkpoint has already been overtaken (round 1)

Q03 assumes the human transcript repair happens before the effort is committed.
That moment has passed. `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md`
is tracked as of `a0b6cc6`, the working tree is clean against `HEAD`, and the
committed content still carries the `MD032` defect at line 264, where a list item
follows a non-blank continuation line with no blank line between them.

Current measured `MD032` state is two findings across 378 tracked and pending
Markdown files: `.claude/skills/humanizer/SKILL.md` line 260, which Step 3
repairs, and the committed design transcript line 264, which only a human may
repair.

C1 is still the right answer. Its checkpoint simply needs restating against
reality: the repair is now an edit to an already-committed tracked file that must
land before Step 3 finalizes the baseline and wires the gate, not a pre-commit
action.

### Question verdicts for plan markdown-check round 1

### Q01 verdict for plan markdown-check: agree with A1 (round 1)

Publishing repository-root `markdown-check.bat` and
`python -m tools.markdown_check.cli` satisfies both halves of the settled design
answer J2, and routing them through one `cli.main` keeps the single policy
authority the design insists on. A2 drops the repository-root Windows launcher
the feature request requires, and A3 satisfies neither obligation. The stated
con, two documented commands, is real but small, and the plan already covers
both with identical fixtures.

One wording note. The option says `python -m tools.markdown_check.cli`, which
requires `cli.py` to carry a `__main__` guard, while the plan's Step 2 names
`cli.main` as the shared boundary. Stating that the module is executable with
`-m` and that `main` is its entry point removes any ambiguity for the
acceptance test.

### Q02 verdict for plan markdown-check: agree with B1, and the caution is well founded (round 1)

Bootstrapping the first baseline from the completed checker's empty-baseline run
and hand-authoring only reviewed residual records is clearly right. B2 would
turn estimates into accepted debt and B3 conflicts with the settled boundary that
checker execution never edits its own baseline.

The reviewer confirms the concern behind the question. The `MD033` figure of 61
carried through the requirement came from an approximation that stripped inline
code spans with a single-line pattern, so a code span opened on one line and
closed on another is not removed and its angle-bracket content can be counted as
raw HTML. That approximation was adequate for sizing the adoption problem and is
not adequate for authoring debt. Treating the implemented checker as the sole
authority for baseline records is the correct conclusion, and the same caution
applies to every figure this review supplied, including the `LS002` count of 17.

### Q03 verdict for plan markdown-check: agree with C1, restate its timing (round 1)

Making the human repair a precondition for baseline finalization and gate wiring
is right. C2 books a knowingly red gate and C3 contradicts the settled zero-start
by granting an allowance to an append-only protocol artifact.

The question's framing needs correcting rather than its answer. It presents the
repair as something to be present before the effort is committed, and the design
transcript carrying that finding is already committed at `a0b6cc6` with the
defect intact at line 264. The precondition is therefore a pending edit to a
tracked file, not a pre-commit gate. Say so, so that Step 3 checks the right
condition, and name the actor as the human maintainer since no agent may perform
it.

### Missing decision in the plan markdown-check question set (round 1)

One decision is missing and it blocks Step 1: where adapter classification lives
and what the resolvable-link test means under Step 1's no-filesystem constraint.
Both facets are set out in the assessment.

The writer may settle this in the confirmed Step 1 text or add it as a fourth
question. The reviewer's answer either way is a syntactic repository-relative
`.md` test inside Step 1, keeping rule evaluation pure, with any inventory-backed
existence check deferred to Step 2 and stated as such.

### Plan structure accepted for markdown-check (round 1)

Step ordering is correct: parsing and rules, then policy, baseline, and
execution, then rollout. Nothing in Step 2 or Step 3 reopens a settled design
choice, the validation skeleton mirrors the three steps, the complexity bound and
IO-cost clarification are consistent with one parse per file, and the test
package roots follow the repository's existing layout. Property-based coverage on
heading normalization, hierarchy streams, and baseline comparison is well chosen,
since those are the three places where an approximation would otherwise hide.

### Requested changes for plan markdown-check round 1

Requested changes: Four changes are requested, and the first two block Step 1. This summary opens
with prose rather than a list because the renderer inlines it behind the
`Requested changes:` label followed by a space, per the authoring contract the consolidated design
now documents.

- Blocking. Adapter classification has no home and no data. Step 1 owns `LS001`
  and `LS002` and must cover adapter exemption, but no plan file is a classifier
  and Step 1's classes-and-behavior list omits one. The design defines the
  bounded pointer classifier by "a resolvable repository-relative Markdown link",
  yet the source-model token list records frontmatter, fences, headings, list
  boundaries, raw HTML, and non-blank lines with no link token, and evaluators
  may not rescan raw text. Name the classifier and add a link token to
  `source.py` and the Step 1 source-model tests.
- Blocking. The resolvable-link test crosses a step boundary. Step 1 requires
  pure evaluation with no filesystem access, while an existence check needs the
  filesystem or the Step 2 inventory. Adopt the syntactic reading, a
  repository-relative path ending in `.md`, inside Step 1, and defer any
  inventory-backed existence check to Step 2 with an explicit statement that
  classification is refined there.
- The 650-line ceiling is not the repository ceiling. The enforced default is
  700 in `check.bat` line 106, `bin/check_big_files.bat` line 15, and
  `bin/python_check.bat` line 105, with no override anywhere; 650 survives only
  in `CHANGELOG.md` and v0.1.0-era documents. Either label 650 as a deliberate
  plan-local budget wherever it appears, including the commit-blocking checklist
  rule, or use 700. The four verified counts of 87, 104, 215, and 412 are exact
  and need no change.
- Q03's checkpoint has been overtaken. The design transcript is committed at
  `a0b6cc6` with its `MD032` finding intact at line 264 and a clean working tree,
  so the human repair is a pending edit to a tracked file rather than a
  pre-commit action. Restate the question description and the Step 3 precondition
  accordingly and name the human maintainer as the actor.
- Optional wording on Q01: state that `cli.py` is executable with `-m` and that
  `main` is its entry point.
- Accepted without change: Q01 A1, Q02 B1, and Q03 C1, the three-step ordering,
  the validation skeleton, the complexity bound, the IO-cost clarification, and
  the property-based coverage choices.

### Writer instructions for plan markdown-check round 1

Four changes. Items 1 and 2 block Step 1 and should land together, because they
are two halves of the same gap.

1. Give adapter classification a home and the data it needs. Name the module or
   function that performs classification and add it to Step 1's files and to its
   classes-and-behavior list. Add a Markdown-link token to
   `tools/markdown_check/source.py` and to the Step 1 source-model tests, because
   the consolidated design defines the bounded pointer classifier by "a
   resolvable repository-relative Markdown link" while the source-model token
   list records no links and rule evaluators may not rescan raw text.

2. Define what resolvable means and keep it inside Step 1's constraints. Step 1
   requires pure source-model evaluation with no filesystem access, and an
   existence check would need either the filesystem or the tracked inventory that
   Step 2 builds. State the syntactic reading, a repository-relative path ending
   in `.md`, so `LS001` and `LS002` complete within Step 1. If a stronger
   existence check is wanted, add it in Step 2 against the inventory and say
   explicitly that classification is refined there.

3. Correct the line-budget facts. The enforced ceiling is 700, not 650:
   `check.bat` line 106, `bin/check_big_files.bat` line 15, and
   `bin/python_check.bat` line 105 all default to 700, and no
   `PYTHON_BIG_FILE_LINE_LIMIT` override exists in the repository. Either adopt
   650 as a deliberate plan-local budget and label it as such wherever it appears,
   including the shared execution checklist's commit-blocking rule, or use 700.
   Leave the four verified counts as they are; 87, 104, 215, and 412 are all
   exact.

4. Restate the Q03 checkpoint against current state. The design transcript is
   committed at `a0b6cc6` and still carries its `MD032` finding at line 264, so
   the repair is now a pending edit to a tracked file rather than a pre-commit
   action. Update the question description and the Step 3 precondition to check
   that condition, and name the human maintainer as the actor.

One optional wording point on Q01: state that `tools/markdown_check/cli.py` is
executable with `-m` and that `main` is its entry point, so the published command
and the shared `cli.main` boundary cannot be read as two different things.

Nothing else is requested. Q01, Q02, and Q03 are accepted with answers A1, B1,
and C1, and the reviewer endorses the Q02 caution: the implemented checker, not
any figure supplied by this review, is the authority for baseline records.

### Final reviewer decision for plan markdown-check round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-24T11:44:13+02:00
- Exchange: specification/plan/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for plan markdown-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.markdown-check.md
Review round: 2

### Requestor assessment for plan markdown-check (round 2)

#### Writer assessment after the first markdown-check plan review for plan markdown-check (round 2)

The two Step 1 blockers are closed. `classifier.py` now owns pure adapter
classification, the source model records Markdown-link tokens, Step 1 treats a
repository-relative `.md` target syntactically, and Step 2 refines target
existence against its tracked inventory. Source and runner tests cover both
halves of that boundary.

The plan now states that the enforced repository default is 700 lines and that
650 is a deliberate stricter plan-local split checkpoint. Q03 and Step 3 reflect
the current tracked transcript at commit `a0b6cc6`, with a pending human edit
required before baseline finalization or gate wiring. Q01 also names the
`__main__` guard that calls `cli.main`. No reviewer recommendation was rejected
and no further implementation question is known.

### Change summary for plan markdown-check (round 2)

#### Changes after markdown-check plan review round 1 for plan markdown-check (round 2)

The plan and validation skeleton now contain these corrections.

- Added `tools/markdown_check/classifier.py`, link tokens, classifier behavior,
  focused source tests, and a line-budget checkpoint to Step 1.
- Defined the Step 1 syntactic repository-relative `.md` link test and Step 2
  inventory-backed target-existence refinement.
- Recorded the actual 700-line enforced default and relabelled every 650-line
  limit as a deliberate plan-local checkpoint.
- Restated Q03 and Step 3 around the already-committed transcript and its pending
  human-maintainer edit.
- Stated that `cli.py` is executable with `-m` through a `__main__` guard calling
  `main`.
- Realigned validation expectations with link-token classification and inventory
  refinement.

### Writer response for plan markdown-check (round 2)

Writer response: #### Writer response to markdown-check plan review round 1 for plan markdown-check (round 2)

Accepted all four requested corrections and the optional Q01 wording with no
disagreement. Adapter classification now has both a production home and the data
needed in Step 1, filesystem-backed existence remains in Step 2, line-limit
facts distinguish policy from the plan-local checkpoint, and the human repair
checkpoint matches the tracked repository state.

Please verify that Step 1 is executable as written, the step boundary is clean,
and the plan is ready for the durable consolidation gate.

### Reviewer focus for plan markdown-check (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-24T11:47:32+02:00
- Exchange: specification/plan/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for plan markdown-check round 2

All four round 1 corrections landed, plus the optional Q01 wording, and each was
verified against the plan and the repository rather than against the change
summary.

### Step 1 classification gap closed for plan markdown-check (round 2)

`tools/markdown_check/classifier.py` now appears in the production file list, in
Step 1's files, and in Step 1's line-budget checkpoint. `classify_document` is
named in classes and behavior as a pure classifier over source tokens, the source
model records Markdown-link tokens, and Step 1 states the test explicitly: a
bounded pointer link is syntactically repository-relative and ends in `.md`.

The cross-step half is handled cleanly. Step 2 refines bounded-pointer
classification against the tracked inventory "so a syntactically valid link whose
target is absent is not treated as resolvable". Step 1 therefore stays pure and
self-contained, and the design's full resolvable-link contract is satisfied by the
completed system rather than by an impossible Step 1 obligation.

The reviewer measured whether that staging creates churn between the two steps.
All 34 bounded pointer adapters carrying a link resolve both on disk and in the
Git index, so Step 2's refinement reclassifies nothing in the current repository
and no `LS001` or `LS002` result changes between Step 1 and Step 2. The staging
is safe as well as sound.

### Line-budget facts corrected for plan markdown-check (round 2)

The confirmed-facts section now states that the enforced Python big-file default
is 700 lines in `check.bat`, `bin/check_big_files.bat`, and
`bin/python_check.bat` with no repository override, and that the plan
"deliberately uses 650 as a stricter local split checkpoint, not as a claim about
the current gate". Every remaining 650 reference is relabelled plan-local,
including the shared execution checklist, which now distinguishes the plan-local
650 checkpoint from the enforced 700 default. That is exactly the distinction
requested, and the four verified counts are unchanged and still exact.

### Q03 checkpoint realigned for plan markdown-check (round 2)

The question description now records that the transcript "is already committed at
`a0b6cc6` with the finding intact, so the repair is now a pending human edit to a
tracked file", and asks for the Step 3 checkpoint on that basis. The framing
matches the repository state the reviewer verified, and the answer C1 is
unchanged and still correct.

### Whole-plan verification for plan markdown-check (round 2)

All three questions carry exactly one recommendation and one answer, the three
numbered steps are intact, and the validation skeleton mirrors them with
per-step analysis, goal, implementation, architecture, performance, coverage, and
integrity sections. No confirmed text is left conditional on an unanswered
question.

Judged against the catalog this effort will enforce, both the plan and its
validation skeleton pass every rule: one level-one title each, ten and five
level-two sections, no duplicate headings under exact or normalized comparison,
no skipped levels, and no `MD032` finding.

Every implementation decision is settled and evidenced, and no substantive work
remains. The reviewer recommends consolidation. The recommendation is advisory
and authorizes nothing; the choice belongs to the human at the convergence gate.

### Question verdicts for plan markdown-check round 2

### Q01 verdict for plan markdown-check: accepted, A1 (round 2)

Publishing repository-root `markdown-check.bat` alongside
`python -m tools.markdown_check.cli` satisfies both halves of the settled design
answer, and the plan now states that `cli.py` carries a `__main__` guard calling
`main`, so the published command and the shared `cli.main` boundary cannot be
read as two different entry points. Nothing further is needed.

### Q02 verdict for plan markdown-check: accepted, B1 (round 2)

Bootstrapping the first baseline from the completed checker's empty-baseline run
and hand-authoring only reviewed residual records remains right, and the reasoning
behind it is now on the record. The reviewer reaffirms that no figure supplied by
this review, including the `MD033` count of 61 and the `LS002` count of 17, is
authoritative for baseline records; only the implemented checker is.

### Q03 verdict for plan markdown-check: accepted, C1 (round 2)

The answer was always right and the framing is now correct. Making the human
repair a precondition for baseline finalization and gate wiring keeps protocol
ownership intact and gives Step 3 a green first authoritative run, and the
question now describes the repair as a pending edit to the tracked transcript
committed at `a0b6cc6` rather than a pre-commit action.

One operational note for whoever runs Step 3, not a requested change: that repair
is the single external dependency in the whole plan, and it is the only task no
agent can perform. It is worth raising with the human maintainer before Step 3
begins rather than at its checkpoint.

### Step and validation alignment for plan markdown-check (round 2)

Step ordering remains correct and nothing in any step reopens a settled design
choice. Step 1 builds the pure source model, classifier, and rule engine; Step 2
adds inventory, policy, baseline, diagnostics, and both launch surfaces, and
refines classification against the inventory; Step 3 wires the shared gate,
finalizes the baseline from authoritative output, and publishes the reference
page. The validation skeleton mirrors all three with not-started placeholders.

### Missing decisions in the plan markdown-check question set (round 2)

None. The round 1 gap was adapter classification having neither a home nor its
defining data, together with a resolvable-link test that crossed a step boundary;
both are closed and verified. No further implementation choice is exposed, and
the plan correctly leaves module-internal structure and test-case detail to the
implementation itself.

### Convergence evidence for plan markdown-check round 2

Covered wording: No substantive change is requested, and only ordinary consolidation work remains.
This summary opens with prose because the renderer inlines it behind the
`Covered wording:` label followed by a space, per the authoring contract the design documents.

- Fold the three answered questions into the confirmed step text. No confirmed
  clause is conditional on an unanswered question, so nothing else needs
  rewording.
- Optionally record in Step 3 that all 34 bounded pointer links currently resolve
  on disk and in the Git index, so the Step 2 inventory refinement is expected to
  reclassify no file. It gives the implementer a concrete expectation to check
  the refinement against.
- Optionally raise the human transcript repair with the maintainer before Step 3
  starts rather than at its checkpoint, since it is the plan's only task no agent
  can perform.

Everything else is settled: the three-step ordering, the file inventory, the
classifier and its Step 1 syntactic contract, the Step 2 inventory refinement,
the enforced 700-line default against the deliberate plan-local 650 checkpoint,
the baseline bootstrap from authoritative checker output, both launch surfaces
and the `__main__` guard, the shared-gate wiring, the complexity bound, the
IO-cost clarification, the property-based coverage choices, and the validation
skeleton.

Convergence rationale: The plan is ready for consolidation, and the reviewer reaches that position by
verification rather than by round count.

Every implementation choice the consolidated design left open is settled with a
stated answer and a reason: the public invocation surfaces, the authoritative
source for the first baseline records, and the checkpoint for the one repair no
agent may perform. The reviewer independently agrees with A1, B1, and C1.

The round 1 blockers are closed and confirmed against the repository. Adapter
classification now has a named production home in
`tools/markdown_check/classifier.py`, the source model carries the Markdown-link
tokens the bounded-pointer contract is defined by, and the resolvable-link test
is split so Step 1 stays pure and syntactic while Step 2 refines target existence
against its tracked inventory. That staging was measured rather than assumed: all
34 bounded pointer adapters carrying a link resolve both on disk and in the Git
index, so the refinement reclassifies nothing and no `LS001` or `LS002` result
moves between the two steps.

The two factual corrections also hold. The plan now states the enforced 700-line
default in all three launchers with no repository override and labels 650 as a
deliberate stricter local checkpoint wherever it appears, so an implementer can
no longer mistake a plan target for a gate. Q03 now describes the transcript
repair as a pending edit to the file committed at `a0b6cc6`, which is the state
the reviewer verified at `HEAD` with a clean working tree.

The plan is executable as written. A reader can determine which files each step
creates or updates, which tests come first, what each completion criterion checks,
which commands to run, what the line budget means, where classification happens
and what it consumes, how the baseline is bootstrapped and what makes it
authoritative, and which single task waits on a human. Step ordering carries no
backward dependency, and the validation skeleton mirrors all three steps.

As a final consistency signal, both the plan and its validation skeleton satisfy
the catalog this effort will enforce: one level-one title each, no duplicate
headings under exact or normalized comparison, no skipped levels, and no `MD032`
finding.

Only consolidation remains, and the reviewer recommends it. That recommendation
is advisory and does not authorize consolidation; the decision belongs to the
human at the convergence gate, who may equally choose another round.

### Writer instructions for plan markdown-check round 2

No substantive change is requested. The plan is complete, internally consistent,
verified against the repository, and executable as written.

At consolidation, fold the three answered questions into the confirmed step text.
No confirmed clause is conditional on an unanswered question, so nothing else
needs rewording.

Two optional additions the implementer would benefit from, neither of which
blocks consolidation. Record in Step 3 that all 34 bounded pointer links
currently resolve on disk and in the Git index, so the Step 2 inventory
refinement is expected to reclassify no file and any reclassification is a signal
worth investigating. And raise the human transcript repair with the maintainer
before Step 3 begins rather than at its checkpoint, since it is the only task in
the plan that no agent can perform and the only external dependency in the
critical path.

One note for whoever runs Step 1. Its completion criteria are unit-level and
fixture-based, so they remain valid regardless of the Step 2 refinement. The
first repository-wide numbers appear only in Step 3, and Q02 already establishes
that those numbers, not any figure carried through the requirement or this
review, are what the baseline records.

The reviewer recommends consolidation. The recommendation is advisory; the human
at the convergence gate may choose `Consolidate` or `Revise and review again`.

### Final reviewer decision for plan markdown-check round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-24T12:00:51+02:00
- Exchange: specification/plan/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
