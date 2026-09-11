# Specification review transcript for v0.11.0

- Exchange: specification/design-specification/v0.11.0/markdown-check
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-24T09:18:42+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for design-specification markdown-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.markdown-check.md
Review round: 1

### Requestor assessment for design-specification markdown-check (round 1)

#### Writer assessment before the markdown-check design review for design-specification markdown-check (round 1)

The design is grounded in the consolidated feature request and current
repository facts. It defines the checker boundary, data flow, supported catalog,
document classification, baseline comparison, diagnostics, launcher behavior,
shared-gate integration, and reference documentation contract without turning
those areas into a file-by-file implementation plan.

Six genuine design questions remain. Their options and recommended answers are
sufficient for review: overlapping `MD024` and `LS003` findings, invalid
mandatory-rule disables, canonical pointer recognition, reduced baseline debt,
the tracked baseline representation, and the diagnostic channel and line
syntax. The reviewer should identify any missing design choice, any feature
requirement that the design accidentally reopens or weakens, and any proposed
contract that is not implementable with the repository's no-Node constraint.

No reviewer wording exists yet for round 1, so no reviewer suggestion has been
applied.

### Change summary for design-specification markdown-check (round 1)

#### Initial markdown-check design changes for design-specification markdown-check (round 1)

- Created `docs/v0.11.0/design.v0.11.0.markdown-check.md` beside the consolidated
  feature request.
- Translated the approved requirement into a bounded checker architecture and
  explicit policy, document, baseline, runtime, and documentation contracts.
- Recorded current codebase facts from `.markdownlint.json`, `check.bat`, and
  `tools/review_markdown_headings.py`.
- Added six design-level open questions with options, trade-offs, and recommended
  answers through the canonical open-question workflow.

### Writer response for design-specification markdown-check (round 1)

Writer response: #### Writer response at the start of markdown-check design review for design-specification markdown-check (round 1)

This is the initial request. There is no earlier reviewer feedback or writer
disagreement. Please review the complete design and its six open questions,
including whether each recommended answer preserves the consolidated feature
request and whether further design questions are genuinely required before
consolidation.

### Reviewer focus for design-specification markdown-check (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-24T09:49:59+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for design-specification markdown-check round 1

The design translates the consolidated feature request into a coherent
architecture without drifting into implementation sequencing. The policy,
document, baseline, runtime, and documentation contracts are each stated at the
right altitude, the two flow diagrams are accurate, and the confirmed technical
facts match the repository. The separation between checker failures and Markdown
findings is a good call that the feature request did not make explicit.

Five of the six questions are well formed with materially distinct options and
recommendations the reviewer would choose. One blocking gap remains, and it
concerns the rule the requestor specifically asked about.

### MD032 adoption status is undefined in the markdown-check design (round 1)

`MD032` is correctly added to the catalog, given accurate blanks-around-lists
semantics, given an acceptance row, and named in the documentation contract. Its
adoption disposition is missing, which is the one thing the baseline model needs
from it.

The confirmed-facts section states the position in two lists. Residual findings
are `LS001`, `LS002`, and `MD033`. Rules measured at zero are `MD001`, `MD024`,
and `LS003`, which "must remain at zero and must not receive baseline entries".
`MD032` is in neither list, so the baseline contract does not determine what
happens to an `MD032` finding. The baseline model then states that a new key has
an implicit allowance of zero, which decides the outcome by omission rather than
by design.

The reviewer measured `MD032` over the 373 tracked Markdown files with a
fence-aware approximation that keeps loose lists and indented fenced blocks
inside their list. The population is one finding:
`.claude/skills/humanizer/SKILL.md` line 260, where the prose line
`**Before -> After:**` is immediately followed by a `-` list item with no blank
line between them. Review transcripts contain no `MD032` findings.

Two earlier iterations of that measurement returned 8 and then 64 findings. Both
were artifacts of the approximation rather than real defects: the first split
loose lists at continuation paragraphs, and the second treated a fenced block
indented inside a list item as a list terminator, which is the dominant shape in
`wiki/how-to/*`. Only the corrected count of one is reported here, and the single
finding was confirmed by reading its source lines.

One finding with an implicit zero allowance fails the first shared-gate run. The
design must say which remedy applies. Because the population is exactly one and
the repair is inserting a single blank line, the reviewer recommends fixing that
file inside this effort so `MD032` joins `MD001`, `MD024`, and `LS003` at zero
and opens no baseline dimension at all. Recording a baseline entry instead is
defensible but strictly worse, because it accepts permanent debt for a
one-character fix.

This gap originates upstream. `MD032` entered the feature request during
consolidation, after specification review had already converged, so it never
passed through a review round. The feature request's measured-adoption paragraph
likewise omits it. The design is the right place to close it, because the design
owns the baseline model.

### MD032 exposure on generated review artifacts (round 1)

The design states that `MD032` applies "including lists inside review artifacts".
Transcripts measure zero today, so nothing is broken. The forward risk is worth
recording rather than fixing here.

Review transcripts are generated by the exchange renderers from caller-authored
assessment files, and those renderers do not normalize blank lines around
caller lists. A reviewer or requestor who writes a prose line immediately
followed by a list produces a transcript that fails the gate, and neither role
may edit a transcript afterwards because it is protocol-owned and append-only.
`MD024` and `MD025` are mandatory precisely because transcripts are protocol
artifacts, and `MD032` now reaches the same artifacts.

Changing the renderers belongs to the review-exchange effort and is outside this
design's stated boundary. The proportionate response is to record the exposure
and place the authoring obligation in the reference page.

### Question verdicts for design-specification markdown-check round 1

### Q01 verdict for design markdown-check: agree with A1 (round 1)

Independent evaluation of `MD024` and `LS003` is right. Suppressing a mandatory
rule's result because a stronger local rule also fired would make `MD024`
enforcement unobservable, which is exactly what the feature request refused when
it declined to report the stronger comparison under the `MD024` identifier. A2
and A3 both trade that away for terser output, and terser output is not worth an
invisible mandatory control.

The overlap costs nothing today: both rules measure zero across the tracked set,
so neither opens a baseline key.

One concrete addition. The acceptance table covers a normalized repeat under
another parent producing `LS003`, but not the overlapping case A1 exists to
settle. Add a row for an exact repeated heading producing both `MD024` and
`LS003` at the same occurrence, so the chosen answer has a test.

### Q02 verdict for design markdown-check: agree with B1 (round 1)

Rejecting an attempted mandatory disable before any file is scanned is
consistent with the settled decision that an unknown configuration key stops the
checker, and it keeps the committed configuration an honest description of
effective policy. B2 and B3 both create a silent override layer where the file
says one thing and the checker does another.

The current `.markdownlint.json` raises no conflict: `MD013` is an optional
catalog rule, so its explicit `false` stays valid under B1.

### Q03 verdict for design markdown-check: agree with C1, and it is free (round 1)

Requiring a resolvable repository-relative Markdown link is the right test,
because adapter status should be proved by content rather than by location and
size alone. C3 would reduce the classifier to a path exemption and C2 would let
path-like prose classify an ordinary short document.

C1's stated con is that existing pointer adapters using a different link form may
need repair. The reviewer measured that cost and it is zero. Of the 35 bounded
pointer candidates, 34 carry a repository-relative Markdown link, all of the form
`[...](../../../instructions/<name>.md)`. The one that does not,
`templates/code-review-answer.template.md`, is independently an adapter under the
`templates/` fragment condition because its first heading is level two.

Recommend recording that measurement in the question, since it converts a con
that reads like a migration risk into a confirmed no-op for the current
repository.

### Q04 verdict for design markdown-check: agree with D1 (round 1)

A no-growth baseline must never punish cleanup, so failing on a shrink is wrong
and D2 is correctly rejected. A silent pass under D3 lets an overstated allowance
persist unseen. The passing advisory is the right middle, and it composes
correctly with Q06: the advisory lands on standard error and therefore cannot
contaminate the finding stream.

### Q05 verdict for design markdown-check: agree with E1, but name the file (round 1)

Versioned JSON with explicit path, rule, and count records is the right choice.
Keeping measured debt out of `.markdownlint.json` also keeps the unknown-key
validation from Q02 simple, which E3 would compromise.

The question calls the representation "the public maintenance contract", and one
part of that contract is missing: the design never says where the baseline file
lives. The baseline is tracked, hand-maintained, documented in the reference
page, and read on every run, so its path is a public interface rather than an
internal module name that the design may defer to the plan. State it, for which
a repository-root `.markdownlint-baseline.json` is the natural form alongside
`.markdownlint.json`.

### Q06 verdict for design markdown-check: agree with F1 (round 1)

`path:line: RULE: reason` on standard output with operational errors and debt
advisories on standard error is the right contract. It is editor-navigable,
matches the source-locator convention the repository's other tools follow, and
keeps checker-health messages out of the finding stream, which F2 would not. F3
would be better for automation but worse for the primary interactive use, and
nothing in the feature request asks for a machine-readable stream today.

The channel split composes correctly with the shared gate, which captures only
the exit status and lets both streams reach the console.

### Missing decision in the design markdown-check question set (round 1)

The six questions cover the genuine design choices with one exception: the
`MD032` adoption disposition set out in the assessment. Whether the single
measured finding is repaired inside this effort or granted a baseline entry is a
real choice with a real consequence for the first gate run, and it is currently
settled only by the implicit-zero-allowance default.

The writer may record it as a stated decision in the baseline section or add it
as a seventh question. The reviewer's answer either way is to repair the file and
keep `MD032` at zero.

No other question is missing, and none of the six is redundant, unclear, or
outside the design's stated scope.

### Requested changes for design-specification markdown-check round 1

Requested changes: - Blocking. `MD032` adoption disposition is undefined. It appears in neither the
  residual list nor the measured-zero list in the confirmed facts, so the
  baseline contract does not determine its outcome and the implicit zero
  allowance decides by omission. Measured population is one finding, at
  `.claude/skills/humanizer/SKILL.md` line 260, with zero in review transcripts.
  State the remedy; the reviewer recommends repairing that one file so `MD032`
  stays at zero with no baseline entry. Note that `MD032` entered the feature
  request during consolidation, after specification review converged, so it has
  never been reviewed.

- Name the tracked baseline file. Q05 chooses versioned JSON and calls it the
  public maintenance contract, but the design gives no path;
  `.markdownlint-baseline.json` at the repository root is the natural form.
- Record the `MD032` exposure on generated review transcripts, which are built
  from caller-authored content without blank-line normalization and cannot be
  edited afterwards, and place the authoring obligation in the reference page.
  Do not change the renderers.
- Q01: add an acceptance row for an exact repeated heading producing both
  `MD024` and `LS003`, so option A1 has a test.
- Q03: record that C1 reclassifies no current file. 34 of 35 bounded pointer
  candidates already carry a repository-relative Markdown link, and
  `templates/code-review-answer.template.md` is independently a `templates/`
  fragment adapter.
- Accepted without change: Q01 A1, Q02 B1, Q03 C1, Q04 D1, Q05 E1, and Q06 F1,
  together with the policy, document, runtime, gate-integration, and
  documentation contracts.

### Writer instructions for design-specification markdown-check round 1

Four changes. Item 1 blocks; the rest close concrete gaps that would otherwise
surface during implementation.

1. Settle the `MD032` adoption disposition. Add it to the confirmed-facts
   position statement so it sits in one of the two lists rather than neither,
   and state the remedy for its measured population. The reviewer measured one
   finding across 373 tracked files, at `.claude/skills/humanizer/SKILL.md` line
   260, where `**Before -> After:**` is immediately followed by a list item with
   no blank line. Record that this effort repairs that single file so `MD032`
   joins `MD001`, `MD024`, and `LS003` at zero with no baseline entry. If the
   writer prefers a baseline entry instead, say so explicitly and give the
   reason, because the current text decides the outcome only through the
   implicit zero allowance for a new key. Adding this as a seventh question is
   equally acceptable.

2. Name the baseline file. Q05 selects versioned JSON and calls it the public
   maintenance contract, but no path is given anywhere in the design. State it,
   for which a repository-root `.markdownlint-baseline.json` is the natural form
   beside `.markdownlint.json`, and reference that name in the baseline model and
   the documentation contract.

3. Record the `MD032` exposure on generated review artifacts. The design already
   states that `MD032` applies to lists inside review artifacts, and transcripts
   measure zero today. Add that transcripts are generated from caller-authored
   content without blank-line normalization, that neither role may edit a
   transcript afterwards, and that the reference page therefore carries the
   authoring obligation to leave a blank line before and after a list in review
   content. Do not change the renderers; that belongs to the review-exchange
   effort and outside this design's boundary.

4. Add two evidence-backed details to existing questions. In Q01, add an
   acceptance row for an exact repeated heading producing both `MD024` and
   `LS003` at the same occurrence, so the chosen answer is testable. In Q03,
   record that the migration con is empirically empty: 34 of the 35 bounded
   pointer candidates already carry a repository-relative Markdown link, and the
   remaining `templates/code-review-answer.template.md` is independently an
   adapter under the `templates/` fragment condition, so C1 reclassifies no file
   in the current repository.

Nothing else is requested. Q02, Q04, Q05, and Q06 are accepted with answers B1,
D1, E1, and F1, Q01 with A1, and Q03 with C1. The policy, document, runtime,
gate-integration, and documentation contracts are sound as written, and the
choice to treat configuration, inventory, decoding, and baseline errors as
checker failures rather than Markdown findings is a good one that the feature
request left implicit.

### Final reviewer decision for design-specification markdown-check round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-24T09:56:32+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for design-specification markdown-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.markdown-check.md
Review round: 2

### Requestor assessment for design-specification markdown-check (round 2)

#### Writer assessment after the first markdown-check design review for design-specification markdown-check (round 2)

Round 1 confirmed that the six open questions are genuine, sufficient, and at
the correct design altitude. The reviewer identified one additional adoption
gap rather than a choice needing another question: `MD032` had entered the
catalog without an explicit initial-baseline disposition. The design now records
the measured one-finding population and settles its repair within this effort,
leaving `MD032` at zero with no baseline entry.

All requested wording is present. The public baseline contract now names
repository-root `.markdownlint-baseline.json`; review-artifact exposure and the
caller blank-line obligation are explicit; Q01 has an overlapping-rule
acceptance case; and Q03 records that its recommended classifier reclassifies no
current file. No reviewer recommendation was rejected and no further design
question is known.

### Change summary for design-specification markdown-check (round 2)

#### Changes after markdown-check design review round 1 for design-specification markdown-check (round 2)

- Added the measured `MD032` population and the decision to repair its single
  current finding so the rule starts at zero without a baseline allowance.
- Named repository-root `.markdownlint-baseline.json` as the separate versioned
  JSON maintenance contract.
- Documented that caller-authored review lists must already satisfy `MD032`
  because generated transcripts are append-only and renderer changes are out of
  scope.
- Added an acceptance case where one exact repeated heading reports both
  mandatory `MD024` and normalized `LS003` findings.
- Added the current pointer-adapter measurement to Q03 and clarified that the
  explicit-link contract reclassifies no current file.
- Updated Q05's recommended answer to name `.markdownlint-baseline.json`.

### Writer response for design-specification markdown-check (round 2)

Writer response: #### Writer response to markdown-check design review round 1 for design-specification markdown-check (round 2)

Accepted every requested change with no disagreement. The `MD032` adoption gap
is settled by repairing `.claude/skills/humanizer/SKILL.md` within this effort,
not by adding baseline debt. The design now names `.markdownlint-baseline.json`,
records the generated-transcript exposure and authoring obligation, adds the
Q01 overlap acceptance case, and incorporates the Q03 population evidence.

Please verify that these edits close the round 1 findings and that the design is
ready for the durable consolidation gate.

### Reviewer focus for design-specification markdown-check (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-24T10:00:39+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for design-specification markdown-check round 2

All five round 1 items were applied, accurately and without disagreement. The
baseline file is named as repository-root `.markdownlint-baseline.json` in the
baseline model, the documentation contract, and Q05's answer. Q01 gained the
overlap acceptance row. Q03 records the pointer measurement and states that the
explicit-link contract reclassifies no current file. The review-artifact
exposure is recorded, with the authoring obligation placed in the reference page
and renderer changes explicitly left out of scope. The design document itself
passes every rule it defines, including `MD032`.

The `MD032` adoption decision is where the remaining problem is, and verifying
it turned up something the round 1 answer did not anticipate.

### MD032 does not start at zero once this exchange is committed (round 2)

The design now states that this effort repairs the single
`.claude/skills/humanizer/SKILL.md` finding so that `MD032` "also starts at zero
and receives no baseline entry". That is true of the currently tracked set. It
stops being true the moment this design review is committed.

The transcript for this very exchange,
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md`, already
carries an `MD032` finding at line 264. Scanning tracked and untracked Markdown
together gives two findings across 375 files rather than one: the humanizer
skill and this transcript. The transcript is untracked today only because the
effort has not been committed yet, and it is versioned beside the design by
design.

The cause is not careless authoring, which matters for the remedy. The answer
renderer inlines caller content behind a literal label at
`tools/spec_review_answer.py` line 188, as
`f"Requested changes: {source.requested_changes.strip()}"`. The round 1 changes
file began with a list item, so the first item was absorbed into the label line
and rendered as prose:

```text
Requested changes: - Blocking. `MD032` adoption disposition is undefined. ...
  ... never been reviewed.
- Name the tracked baseline file. Q05 chooses versioned JSON and calls it the
```

Lines 255 to 263 become one prose block, and the next list item at line 264
follows it with no blank line, which is exactly what `MD032` reports.

The reference-page obligation the design just added does not prevent this. It
tells authors to "leave a blank line before and after every list in
caller-authored review content", but the renderer applies `.strip()` to that
content before prefixing the label, so a leading blank line an author adds is
removed. The author cannot satisfy the stated obligation for this field by
following it literally.

The obligation that does work is stronger and less obvious: caller content that
the renderer inlines behind a label must not begin with a list at all. Beginning
with a prose sentence, then a blank line, then the list, renders correctly. This
round's own changes file is written that way as a check on the advice.

No currently tracked transcript has the pattern, so this is a new exposure
introduced by this exchange rather than existing debt. Two remedies are
available and the design should pick one: state the precise obligation and have
the human repair this transcript before the effort is committed, or accept one
baseline allowance for the transcript path and say so. The reviewer prefers the
first, because a baseline entry for a protocol artifact that keeps growing is
harder to reason about than a one-time repair, but this is a genuine choice and
the transcript is not a file any agent may edit.

### Question verdicts for design-specification markdown-check round 2

### MD032 zero-start claim in the design markdown-check (round 2)

The claim that `MD032` starts at zero with no baseline entry is correct for the
tracked set and incorrect for the set this effort will commit. Measured over
tracked and untracked Markdown together, `MD032` has two findings across 375
files: `.claude/skills/humanizer/SKILL.md` line 260, which the design already
commits to repairing, and
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264,
which this exchange created.

Reviewer answer: keep the repair decision and correct the scope of the claim.
State that the zero-start applies to the effort's committed state, name the
transcript exposure as the second case, and record the chosen remedy for it.

### Authoring obligation wording in the design markdown-check (round 2)

The reference-page obligation as written cannot be followed for the fields the
renderers inline behind a label, because `.strip()` removes the leading blank
line before the label is prefixed. The obligation needs to name the real
constraint.

Reviewer answer: replace "leave a blank line before and after every list" with a
statement that distinguishes the two cases. Caller content rendered as its own
block keeps the blank-line rule. Caller content inlined behind a label, which is
the requested-changes, covered-wording, and writer-response fields, must not
begin with a list; it begins with a prose sentence, then a blank line, then any
list. Naming the affected fields makes the rule checkable by an author before
publication.

### Design boundary for the transcript remedy in markdown-check (round 2)

The design correctly keeps renderer changes out of scope, and the reviewer is
not asking for them here. The remedy for the existing transcript finding is
therefore either a human repair before commit or one baseline allowance, and
either is consistent with the stated boundary. What the design cannot do is
claim a zero start while a tracked-at-commit file carries a finding.

If the writer chooses the baseline allowance, the entry belongs in
`.markdownlint-baseline.json` keyed on the transcript path, `MD032`, and a count
of one, and the design should note that the allowance covers a protocol artifact
that no agent may edit.

### Accepted without change in the design markdown-check round 2

Q01 through Q06 remain accepted with answers A1, B1, C1, D1, E1, and F1. The
round 1 additions are all correct: the named baseline file, the Q01 overlap
acceptance row, the Q03 pointer measurement, and the recorded review-artifact
exposure. The policy, document, runtime, gate-integration, and documentation
contracts need no further change, and the design continues to sit at the right
altitude with implementation sequencing left to the plan.

### Requested changes for design-specification markdown-check round 2

Requested changes: Two changes are requested, both arising from one measured finding. This summary
opens with prose rather than a list because the renderer inlines it behind the
`Requested changes:` label followed by a space, which is the exact constraint item 2 asks the design
to document.

- Blocking. The `MD032` zero-start claim is scoped to the tracked set and breaks
  at commit. Measured across tracked and untracked Markdown, `MD032` has two
  findings across 375 files: `.claude/skills/humanizer/SKILL.md` line 260, which
  the design already repairs, and
  `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264,
  created by this exchange and versioned beside the design. Restate the claim
  against the effort's committed state and record the remedy for the transcript,
  either a human repair before commit or one `.markdownlint-baseline.json`
  allowance keyed on that path, `MD032`, and a count of one. Name the actor,
  because no agent may edit a published transcript.
- The reference-page authoring obligation cannot be followed as written. For
  fields the renderers inline behind a label, `tools/spec_review_answer.py` line
  188 applies `.strip()` before prefixing the `Requested changes:` label and a space, so a leading
  blank line the author adds is removed. Replace the single blank-line rule with
  the two-case rule: block-rendered caller content keeps the blank lines, while
  label-inlined content, namely the requested-changes, covered-wording, and
  writer-response fields, must not begin with a list and opens with a prose
  sentence followed by a blank line.
- Accepted without change: Q01 through Q06 with answers A1, B1, C1, D1, E1, and
  F1, the named `.markdownlint-baseline.json` contract, the Q01 overlap
  acceptance row, the Q03 pointer measurement, and the recorded review-artifact
  exposure. The design document passes every rule it defines, including `MD032`.

### Writer instructions for design-specification markdown-check round 2

Two changes remain, and they are the same finding seen from the policy side and
the guidance side.

1. Correct the `MD032` zero-start claim and choose the transcript remedy. The
   confirmed-facts paragraph currently says the humanizer repair leaves `MD032`
   at zero with no baseline entry. Measured across tracked and untracked
   Markdown together, `MD032` has two findings across 375 files: the humanizer
   skill at line 260 and
   `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` at line
   264, created by this exchange and versioned beside the design.

   State the zero-start against the effort's committed state rather than the
   current tracked set, name the transcript case, and record which remedy
   applies: a human repair of that transcript before the effort is committed, or
   one `.markdownlint-baseline.json` allowance keyed on the transcript path,
   `MD032`, and a count of one. The reviewer prefers the repair, but either is
   consistent with the design's boundary. No agent may edit the transcript, so
   whichever is chosen must name the actor.

2. Restate the reference-page authoring obligation so it can actually be
   followed. The current wording tells authors to leave a blank line before and
   after every list in caller-authored review content. For the fields the
   renderers inline behind a literal label, that instruction has no effect,
   because `tools/spec_review_answer.py` line 188 applies `.strip()` to the
   caller content before prefixing the `Requested changes:` label and a space, removing any leading
   blank line the author added.

   Replace it with the two-case rule. Caller content rendered as its own block
   keeps the blank-line requirement. Caller content inlined behind a label, which
   is the requested-changes, covered-wording, and writer-response fields, must
   not begin with a list and instead opens with a prose sentence followed by a
   blank line. Naming those fields lets an author check compliance before
   publishing.

Nothing else is requested. Q01 through Q06 stay accepted with A1, B1, C1, D1,
E1, and F1, and every round 1 addition is correct as applied. The design
document itself passes all the rules it defines, including `MD032`, which is a
good consistency signal for the contract it specifies.

### Final reviewer decision for design-specification markdown-check round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-08-24T10:06:10+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: request

### Review identity for design-specification markdown-check (round 3)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/design.v0.11.0.markdown-check.md
Review round: 3

### Requestor assessment for design-specification markdown-check (round 3)

#### Writer assessment after the second markdown-check design review for design-specification markdown-check (round 3)

The remaining `MD032` inconsistency is now closed at design level. The committed
effort population, not only the current tracked population, is the baseline
boundary. The design names both measured findings, assigns the skill-file repair
to implementation, assigns the published-transcript repair to a human maintainer
before commit, and keeps `MD032` at zero without a baseline allowance.

The authoring contract now distinguishes block-rendered content from fields
inlined behind renderer labels. It names requested-changes, covered-wording, and
writer-response content and requires prose before any list in those fields. The
design continues to exclude renderer changes and agent edits to protocol-owned
transcripts. No disagreement or further open design choice remains.

### Change summary for design-specification markdown-check (round 3)

#### Changes after markdown-check design review round 2 for design-specification markdown-check (round 3)

The round 2 findings produced the following design changes.

- Reframed the `MD032` adoption measurement around all 375 Markdown files that
  the effort will commit.
- Named both findings and assigned the humanizer repair to implementation and
  the design-review transcript repair to a human maintainer before commit.
- Preserved the zero-start, no-baseline decision without authorizing an agent to
  edit the published transcript.
- Replaced the blanket list-spacing guidance with separate contracts for
  block-rendered and label-inlined caller content.
- Named requested-changes, covered-wording, and writer-response as fields that
  must begin with prose before any list.

### Writer response for design-specification markdown-check (round 3)

Writer response: #### Writer response to markdown-check design review round 2 for design-specification markdown-check (round 3)

Accepted both requested changes with no disagreement. The design now makes a
human pre-commit transcript repair the explicit remedy, keeps renderer changes
outside scope, and documents an authoring rule that survives the renderer's
`.strip()` and label-prefix behavior.

Please verify the corrected committed-state baseline claim and renderer-aware
authoring contract, then recommend convergence if no further design gap remains.

### Reviewer focus for design-specification markdown-check (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-08-24T10:09:05+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: answer

### Reviewer assessment for design-specification markdown-check round 3

Both round 2 changes are applied precisely, in the policy section and again in
the documentation contract, and the reviewer verified each against the
repository rather than against the change summary.

### Verified MD032 committed-state claim for the design markdown-check (round 3)

The adoption paragraph now measures the population the effort will commit rather
than the currently tracked set, names both findings, and assigns each a distinct
actor: implementation repairs `.claude/skills/humanizer/SKILL.md` line 260, and a
human maintainer repairs
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264
before commit. It states that no agent edits the published transcript, which
keeps the remedy inside the protocol's ownership rules.

Re-measuring across tracked and pending Markdown confirms the figures exactly:
two `MD032` findings across 375 files, at the two lines named. The claim now
matches the evidence.

### Authoring contract validated in practice for the design markdown-check (round 3)

The reference-page obligation is now split correctly. Block-rendered caller
content keeps the blank line before and after every list. Content inlined behind
a label, named as the requested-changes, covered-wording, and writer-response
fields, must open with a prose sentence and a blank line before any list. That is
the constraint that survives the renderer's `.strip()` and label prefix.

The round 2 answer was authored under the new rule as a test of it, and the
re-measurement confirms the result: appending that round to the transcript
introduced no new `MD032` finding, so the count stayed at two rather than rising
to three. The contract is not merely stated, it is demonstrated on the artifact
this exchange produces.

### Whole-document verification for the design markdown-check (round 3)

All six questions carry exactly one recommendation and one answer. The confirmed
sections contain no clause deferred to an unanswered question, so consolidation
has no conditional text to resolve beyond folding the answers in. The catalog,
mandatory-rule set, classification, baseline model, diagnostic contract, and gate
integration remain mutually consistent, and `.markdownlint-baseline.json` is
named consistently in the baseline model, the documentation contract, and Q05.

Judged against the catalog it specifies, the design passes every rule: one
level-one title, thirteen level-two sections, no duplicate headings under either
exact or normalized comparison, no skipped levels, and no `MD032` finding.

Every in-scope design decision is settled and evidenced, and no substantive work
remains. The reviewer recommends consolidation. The recommendation is advisory
and authorizes nothing; the choice belongs to the human at the convergence gate.

### Question verdicts for design-specification markdown-check round 3

### Q01 verdict for design markdown-check: accepted, A1 (round 3)

Independent `MD024` and `LS003` evaluation stands, and the overlap acceptance row
added in round 2 gives the answer a test. Both rules remain at zero, so the extra
baseline dimension costs nothing today.

### Q02 verdict for design markdown-check: accepted, B1 (round 3)

Fail-fast rejection of an attempted mandatory disable is consistent with the
unknown-key stop and keeps the committed configuration an honest description of
effective policy. The current `.markdownlint.json` raises no conflict.

### Q03 verdict for design markdown-check: accepted, C1 (round 3)

The explicit-link pointer contract is the right test, and the measurement
recorded in round 2 stands: 34 of 35 bounded pointer candidates already carry a
repository-relative Markdown link, and the remaining
`templates/code-review-answer.template.md` qualifies independently as a
`templates/` fragment, so C1 reclassifies no current file.

### Q04 verdict for design markdown-check: accepted, D1 (round 3)

Passing with a debt-reduced advisory keeps no-growth semantics from punishing
cleanup, and it composes correctly with Q06 because the advisory lands on
standard error and cannot contaminate the finding stream.

### Q05 verdict for design markdown-check: accepted, E1 (round 3)

Separate versioned JSON keeps measured debt out of rule configuration, which also
keeps Q02's unknown-key validation simple. The public contract is now complete
because repository-root `.markdownlint-baseline.json` is named in the baseline
model, the documentation contract, and the answer itself.

### Q06 verdict for design markdown-check: accepted, F1 (round 3)

The `path:line: RULE: reason` findings stream on standard output with operational
errors and advisories on standard error is editor-navigable, matches the
repository's source-locator conventions, and keeps checker-health messages out of
the finding stream. The shared gate captures only the exit status, so both
streams reach the console unchanged.

### Missing decisions in the design markdown-check question set (round 3)

None. The round 1 gap was the `MD032` adoption disposition and the round 2 gap
was the scope of its zero-start claim together with an authoring rule that could
not be followed. Both are closed and verified. No further design choice is
exposed, no question is redundant, unclear, or outside scope, and the design
leaves implementation sequencing, module names, test placement, and rollout
commands to the plan as it should.

### Convergence evidence for design-specification markdown-check round 3

Covered wording: No substantive change is requested, and only ordinary consolidation work
remains. This summary opens with prose because the renderer inlines it behind
the `Covered wording:` label followed by a space, which is the contract the design now documents.

- Fold the six answered questions into the confirmed text. The design's confirmed
  sections contain no clause conditional on an unanswered question, so there is
  no deferred wording to resolve beyond removing the question block itself.
- Optionally carry the two `MD032` prerequisites into the implementation plan as
  explicit tasks, since they have different actors: the implementation repairs
  the skill file, and a human maintainer repairs the design-review transcript
  before commit. The design states both correctly; the plan is where they become
  trackable work items.
- Optionally note in the plan that the transcript repair must happen before the
  effort is committed, because the `MD032` zero-start claim depends on it and a
  published transcript cannot be edited by an agent.

Everything else is settled: the catalog and mandatory-rule set, configuration
precedence, the finding model and ordering, the tracked inventory boundary, the
fence-aware source model, adapter classification, hierarchy and uniqueness
evaluation, the `.markdownlint-baseline.json` contract and integrity rules, both
runtime entry points, the shared-gate connection, the acceptance table, and the
documentation contract.

Convergence rationale: The design is ready for consolidation, and the reviewer reaches that position by
verification rather than by round count.

Every design decision the consolidated feature request left open is settled with
a stated answer and a reason: duplicate-heading overlap, mandatory-rule
configuration conflict, pointer-adapter recognition, reduced-debt behavior,
baseline representation, and the diagnostic channel and syntax. The reviewer
independently agrees with A1, B1, C1, D1, E1, and F1.

The two defects raised in earlier rounds are closed and confirmed against the
repository rather than accepted on assertion. `MD032` had entered the catalog
without an adoption disposition, sitting in neither the residual list nor the
measured-zero list; it now carries a measured population, a named remedy, and a
distinct actor for each of its two findings. The zero-start claim had been scoped
to the tracked set and would have been false at commit; it is now scoped to the
committed state, and re-measurement confirms the exact figures, two findings
across 375 tracked and pending files at the two lines named.

The authoring contract that supports that claim is not merely written down, it is
demonstrated. Round 2's answer was authored under the new label-inlined rule, and
appending it to the transcript produced no new `MD032` finding, holding the count
at two. A rule that survives its own artifact is a rule an implementer can trust.

The design is implementable as written. A reader can determine which files are
inventoried, how each is classified, which rules apply, what each finding
carries, how findings are ordered, which stream carries them, what the baseline
file is called and how it is validated, what happens when debt shrinks, how the
Windows gate and the platform-neutral entry point share one policy authority, and
what the reference page must document. Operational failures are correctly
separated from Markdown findings, which the feature request left implicit.

As a final consistency signal, the design satisfies the catalog it specifies: one
level-one title, thirteen level-two sections, no duplicate headings under exact
or normalized comparison, no skipped levels, and no `MD032` finding.

Only consolidation remains, and the reviewer recommends it. That recommendation
is advisory and does not authorize consolidation; the decision belongs to the
human at the convergence gate, who may equally choose another round.

### Writer instructions for design-specification markdown-check round 3

No substantive change is requested. The design is complete, internally
consistent, verified against the repository, and implementable as written.

At consolidation, fold the six answered questions into the confirmed text. No
confirmed clause is conditional on an unanswered question, so nothing else needs
rewording.

Carry the two `MD032` prerequisites into the implementation plan as separate
tracked items, because they have different actors and different timing. The
implementation repairs `.claude/skills/humanizer/SKILL.md` line 260. A human
maintainer repairs
`docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md` line 264
before the effort is committed, since the zero-start claim depends on it and no
agent may edit a published transcript.

One note for the plan rather than the design. The `MD032` obligation on
label-inlined caller content is currently a documentation contract enforced by
author discipline. If a later effort revisits the review-exchange renderers, the
durable fix is for the renderers to place caller content on its own line below
the label, which would remove the constraint rather than document it. That is
outside this effort's boundary and correctly excluded here.

The reviewer recommends consolidation. The recommendation is advisory; the human
at the convergence gate may choose `Consolidate` or `Revise and review again`.

### Final reviewer decision for design-specification markdown-check round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-08-24T10:40:01+02:00
- Exchange: specification/design-specification/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/design.v0.11.0.markdown-check.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
