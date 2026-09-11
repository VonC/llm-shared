# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/review-mode-docs
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-20T13:55:59+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 review-mode-docs round 1

request_index_tree: fea11fb657237e4194a1f123646ae490c477a103
resolved_validation_set:

- ghog day (sources: project)
- rg -n independent README.md wiki/README.md wiki/explanation/independent-review-mode-and-human-authority.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 1 review-mode-docs round 1

Step 1 is fully implemented. Both entry points distinguish independent review
mode from the self-review loop, the new explanation defines separate requestor,
reviewer, and human authority, and the existing self-review pages keep their
purpose and review logo while gaining reciprocal comparison links.

Five repository-level acceptance tests pin navigation order, the generic
independent-review logo, canonical instruction attribution, bounded local-link
and named-path resolution, and the incremental AC01-through-AC12 coverage
record. No production class or runtime path changed. The helper work is linear
in the declared finite page set, with no DDD-Hexagonal boundary crossed.

The fresh full Groundhog walk covered 1,882 tests with `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`,
and `exit=0`. A final documentation-only freshness call returned
`exit=0` without rerunning Python because the preceding full walk was green.

### Implementation report for step 1 review-mode-docs round 1

The implementation adds
`wiki/explanation/independent-review-mode-and-human-authority.md` with the
generic logo, invocation model, three authority roles, advisory convergence,
durable transcript rationale, self-review comparison, and canonical policy
links.

`README.md` and `wiki/README.md` now route readers to that page.
The existing self-review explanation and review-round how-to retain their
purpose and review logo while linking back to the independent boundary.

The new acceptance package supplies bounded repository readers and five Step 1
tests. The versioned coverage file begins all twelve criterion rows and all six
inventory-candidate rows, fills Step 1 evidence, and leaves later slices
pending.

### Change summary for step 1 review-mode-docs round 1

The staged subject contains ten paths in two dependency-ordered `a.commit`
groups.

- Group 1, `docs(review-mode-docs): explain independent review authority`,
  contains both entry points, the new explanation, two comparison callouts,
  the acceptance package, and the coverage record.
- Group 2, `docs(review-mode-docs): record step 1 validation`, contains
  only the validation-plan verdict and evidence.

The staged paths are `README.md`,
`docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`,
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`, the three
files under
`tests/unit/tools/test_review_mode_docs_acceptance/`,
`wiki/README.md`,
`wiki/explanation/independent-review-mode-and-human-authority.md`,
`wiki/explanation/why-the-llm-reviews-its-own-work.md`, and
`wiki/how-to/answer-a-review-round.md`.

### Writer response for step 1 review-mode-docs round 1

Writer response: This is the first implementation review round for Step 1. There is no prior
reviewer finding, staged repair, reversal, or disagreement to assess. The
request presents the implementation-check `Yes` verdict and the exact
staged subject for independent review.

### Reviewer focus for step 1 review-mode-docs round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-20T14:52:11+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 review-mode-docs round 1 (exchange 1)

Baseline index tree: fea11fb657237e4194a1f123646ae490c477a103

Assessed index tree: 378c21f4dcfdd94926d34928127a0c54b991edec

### Implementation check for step 1 review-mode-docs round 1 (exchange 1)

Result: Yes. Step 1 has been fully implemented.

Every file the plan names for Step 1 is present and staged, and the delivered
behavior matches the step's intent. `README.md` and `wiki/README.md` both route
to the new explanation and both name the settled terms `self-review loop` and
`independent review mode`. `wiki/explanation/independent-review-mode-and-human-authority.md`
defines the requestor, reviewer, and human authorities, states that a
convergence recommendation does not authorize consolidation or commit,
explains why the transcript is durable evidence and not working context, and
attributes agent policy to `instructions/review-requestor.md`,
`instructions/spec-reviewer.md`, and `instructions/code-reviewer.md`. The two
self-review pages keep their purpose and their review logo while gaining
reciprocal comparison callouts, and the new page carries the generic
`logo-llm-shared-transparent.png` required by the settled Q15 decision.

The five acceptance tests precede the content they pin and cover exactly the
Step 1 behaviors: entry-point discovery with Diataxis order, the visual and
terminology boundary, canonical authority attribution, bounded local-link and
named-path resolution, and the AC01-through-AC12 coverage record with its six
inventory-candidate rows.

The staged set is ten paths. Nine are named by the Step 1 file list in the
consolidated plan, including `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`,
which the Q04 consolidation correctly moved into Step 1. The tenth is the
validation plan itself, which is review metadata rather than step content.
Nothing staged falls outside the step.

The architecture assessment stands. The change adds no production module and
crosses no DDD-Hexagonal boundary: the new test support reads only paths a test
supplies and never imports exchange, workflow, persistence, or domain code. No
new computation is worse than linear in the declared page set, and no existing
feature or reporting capability is impaired.

The document-level status line correctly remains `No, it is not implemented.`
because Steps 2 through 5 are still pending, and reviewer mode completed no
umbrella row.

Validation plan effects: Reviewer mode changed one line of the validation plan, inside the reviewed
step's rows.

The Step 1 line-budget row recorded `conftest.py` at 102 lines. Repair 3 added
two module constants and removed one local assignment, moving the file to 103
lines, so the row now reads 103 against its 180-line advisory. The
test-module figure is unchanged at 129 lines, because repair 4 added one
module constant and removed one local assignment for a net of zero.

That is the whole reviewer-authored validation-plan difference. The recorded
variance remains honest: the test module is still nine lines above its 120-line
Step 1 advisory while below the 550-line split threshold and the 650-line
ceiling, and the plan's shared checklist permits an advisory variance that is
recorded rather than hidden.

Everything else in the staged validation-plan difference is writer work under
review. The Step 1 verdict sentence, its summary, the implemented inventory,
the architecture, performance, unit-test-coverage, and feature-integrity
subsections, and their required closing sentences were all authored by the
writer and were assessed, not rewritten. The verdict sentence is the exact
`Yes. Step 1 has been fully implemented.` form, followed by an empty line and a
prose summary, as the template orders.

Reviewer mode wrote no row for any other step, changed no document-level status
line, and completed no umbrella row. The document-level line correctly remains
`No, it is not implemented.` while Steps 2 through 5 are pending. The stale
theme sentence directly below that line is writer-owned and is returned as an
unresolved finding rather than edited here.

### Pre-repair mandatory checks and coverage for step 1 review-mode-docs round 1 (exchange 1)

The writer reported a fresh full walk before publishing: 1,882 tests with
`fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`, and `exit=0`. The
reviewer did not re-derive that pre-repair figure and instead re-ran the whole
resolved set after repairing, so the evidence backing this answer is
post-repair rather than inherited.

One pre-repair state was measured directly and is the origin of repair 1. The
staged blob of `wiki/README.md` carried 192 CR and 203 LF against 197 CR and
197 LF at `HEAD`, and `git diff --cached --numstat` reported eleven added and
five removed lines while the same diff with `--ignore-cr-at-eol` reported six
added and zero removed. That pair of measurements is what proves five
pre-existing lines had been rewritten by line ending alone.

Both whitespace commands passed before the repairs as well, because the new
lines were LF at that point. This is precisely why the condition was invisible
to the step's own validation set: `git diff --check` inspects trailing
whitespace and conflict markers, not a change of line terminator, so a
CRLF-to-LF rewrite of five untouched lines passes it silently.

Pre-repair blobs were recorded for all four repair paths before the first edit
to each: `wiki/README.md` at `be98456c48cb657a81101313eca11b58b1a6528c`,
`conftest.py` at `6879413d6e702777ed90f17158980fb1f41faada`, the acceptance test
module at `9ed9a87315055e2d2a283c9d2deb94b059802d8c`, and the validation plan at
`6e0c417524ed2cebc0d05916a081806b85695c69`.

### Resolved validation set and sources for step 1 review-mode-docs round 1 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five commands and every one was run after the repairs.

`ghog day`, sourced from the project, reported `fail=0`, `warn=0`, `xfail=0`,
`cov=100`, `outliers=0`, `excluded=0`, and `exit=0` on the full walk executed
after repairs 3 and 4 were applied. That walk is what proves the two
substantive test-code repairs keep the suite green and the project coverage
gate satisfied, and it also exercised the repository lint gate, which accepts
the named module constants that replaced the character arithmetic. A later
freshness call returned `exit=0` without rerunning Python because no Python
file changed after that green walk; only Markdown changed afterwards.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`, with nothing
failing in focus and nothing passing in focus while failing in the full suite.

`rg -n independent README.md wiki/README.md wiki/explanation/independent-review-mode-and-human-authority.md`,
sourced from the plan, returned matches in all three files, confirming the
discovery path the step's completion criterion names.

`git diff --check`, sourced from the plan, returned no diagnostic and exit `0`.

`git diff --cached --check`, sourced from the plan, returned no diagnostic and
exit `0`. This command did report six trailing-whitespace diagnostics and exit
`2` during an intermediate repair attempt that gave the new lines CRLF endings;
that attempt was corrected before staging, and the final staged state is clean.

No mandatory command was unavailable, and no command was skipped or treated as
passing without being run.

### Resolver drift and direction for step 1 review-mode-docs round 1 (exchange 1)

No resolver drift was observed.

The five commands embedded in the request envelope and the five the current
resolver produces are identical in content and in source attribution: `ghog day`
from the project, and the plan-sourced `rg` discovery check,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union therefore equals both sets, in neither direction is a command present
on one side only, and no command had to be added or dropped when the union was
run.

### Repository state around validation for step 1 review-mode-docs round 1 (exchange 1)

The request-time index tree was `fea11fb657237e4194a1f123646ae490c477a103`, and
the index captured at reviewer entry matched it exactly, so no fresh writer
work arrived between publication and assessment and the early rejection path
did not apply. After the attributed repairs were staged, the index tree is
`378c21f4dcfdd94926d34928127a0c54b991edec`.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false` with the before and after digest both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the ordered twelve-path set returned
`acceptable: false`. That result is fully explained by this round's reviewer
repairs and contains no validation side effect. The tracked paths it names are
`wiki/README.md`, `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py`,
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`,
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`, and `<index>`. The
first four are exactly the four repair paths, each with its pre-repair blob
recorded before editing and each proven cleanly attributable before staging,
and `<index>` changed because those attributed patches were staged. The
validation-plan difference is confined to a single Step 1 line-budget row.

The only ignored path that differed is `a.ghog.status`, which the validation
walk rewrites by design. A difference confined to an ignored validation
artifact is acceptable, and it was neither staged nor reverted.

No untracked path differed. No pre-existing unstaged or untracked writer work
was swept into the index, and the working tree carries no reviewer change that
was left unstaged. The only untracked file in the tree is the protocol
transcript for this exchange.

### Repair inventory for step 1 review-mode-docs round 1 (exchange 1)

Repairs made:

- Four paths were repaired. Every patch was proven cleanly attributable through
- `attribute-reviewer-patch` before staging, and each repair path had its
- pre-repair blob recorded first.
- Repair 1, polishing-only, `wiki/README.md` line endings. The file is uniformly
- CRLF at `HEAD` at 197 CR and 197 LF, and the staged version arrived mixed at
- 192 CR and 203 LF. Six lines were genuinely added, so five pre-existing lines
- had been rewritten from CRLF to LF as collateral, producing a diff of eleven
- added and five removed lines for a six-line change. `git diff --check` does not
- detect a line-terminator change, so the step's own validation set could not
- surface it. The repair restores every pre-existing line to CRLF and leaves the
- six added lines as LF. The staged diff is now exactly six added and zero
- removed, and both whitespace gates return no diagnostic.
- An earlier attempt normalized the whole file to CRLF, including the six new
- lines. That made `git diff --cached --check` report trailing whitespace on all
- six and exit `2`, because Git counts CR at end of line as trailing whitespace
- under this repository's configuration. That attempt was corrected before
- staging rather than published, and the outcome is recorded in the unresolved
- findings as a repository-hygiene question this step should not settle.
- Repair 2, polishing-only, `wiki/README.md` emoji encoding. The new explanation
- bullet used the HTML entity `&#129302;` while the six sibling bullets in the
- same list use literal emoji, including a literal robot glyph six lines below
- for `One body, many agents`. That entity was the only one in the whole file.
- The repair replaces it with the literal glyph so the list is encoded
- consistently.
- Repair 3, substantive, `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py`.
- The Markdown suffix was built as `chr(46) + chr(109) + chr(100)` and the
- fragment prefix as `chr(45)`, which hides two ordinary string values behind
- character arithmetic. The repair introduces the module constants
- `_MARKDOWN_SUFFIX` and `_EMOJI_FRAGMENT_PREFIX` and uses them at both sites.
- Behavior is unchanged.
- Repair 4, substantive, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`.
- The backtick used to bracket inventory paths was built as `chr(96)` inside the
- test body. The repair introduces the module constant `_BACKTICK` and removes
- the local alias. Behavior is unchanged.
- Repairs 3 and 4 are the reason this round cannot recommend commit readiness.
- They change test code, so the readiness rule that forbids a substantive repair
- in the recommending round applies, even though every gate is green afterwards.
- Repair 5, review metadata, `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`.
- Repair 3 moved `conftest.py` from 102 to 103 lines, so the Step 1 line-budget
- row now records 103 against its 180-line advisory. This edit is confined to
- rows for the reviewed step. No other validation-plan content was touched, no
- document-level status line was changed, and no umbrella row was completed.

Paths staged:

- README.md
- docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md
- docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md
- `tests/unit/tools/test_review_mode_docs_acceptance/__init__.py`
- tests/unit/tools/test_review_mode_docs_acceptance/conftest.py
- tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py
- wiki/README.md
- wiki/explanation/independent-review-mode-and-human-authority.md
- wiki/explanation/why-the-llm-reviews-its-own-work.md
- wiki/how-to/answer-a-review-round.md

### Commit plan assessment for step 1 review-mode-docs round 1 (exchange 1)

`a.commit` remains accurate and needed no amendment.

Its two groups cover exactly the ten staged paths with no omission and no
extra. Group 1, `docs(review-mode-docs): explain independent review authority`,
lists nine paths: both entry points, the new explanation, the two self-review
comparison pages, the three files of the acceptance package, and the coverage
record. Group 2, `docs(review-mode-docs): record step 1 validation`, lists the
validation plan alone.

The ordering is correct from least to most dependent. The documentation and its
acceptance evidence land first, and the validation verdict that describes them
lands last, so the recorded verdict never precedes the work it certifies.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and both bodies state Why before What with the
umbrella, requirement, design, and plan named as motivation.

The reviewer repairs did not change group membership. Every repaired path was
already staged and already assigned: `wiki/README.md`, `conftest.py`, and the
acceptance test module belong to group 1, and the validation plan belongs to
group 2. No path moved between groups, none was added, and none was removed, so
the file membership, grouping, order, scope, and conventional subjects all
still match the staged work.

No commit was run and no staging beyond the attributed reviewer patches was
performed.

### Findings and boundaries for step 1 review-mode-docs round 1 (exchange 1)

Unresolved findings:

- Two findings remain for the writer. Neither was repaired, and neither blocks
- Step 1 content.
- Finding 1, writer-owned, stale document-level theme sentence in
- `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`. The opening status
- line correctly stays `No, it is not implemented.` because Steps 2 through 5 are
- pending. The sentence below it still reads that no implementation check has
- taken place yet, which the staged Step 1 verdict two hundred lines below now
- contradicts. That sentence sits outside the reviewed step's rows, and reviewer
- mode may write only those rows, so it is returned rather than edited. Refresh
- it so the document reads as partially checked while remaining pending overall.
- Finding 2, repository hygiene beyond this step, the line-ending status of
- `wiki/README.md`. That file is the only CRLF file among the ten staged paths
- and, from the evidence gathered here, the only one in this area of the tree;
- every other staged file is pure LF. `.gitattributes` declares no `text` or
- `eol` policy and `core.autocrlf` is `false`, so Git stores exactly what an
- editor writes. Git's whitespace check treats CR at end of line as trailing
- whitespace, which means any line added to this file with the file's own CRLF
- convention fails `git diff --check`, while a line added with LF passes and
- leaves the file mixed. The repair above takes the second path deliberately, so
- the gate passes and the diff is minimal, but the file remains internally mixed
- at 197 CRLF lines and 6 LF lines.
- Converting `wiki/README.md` wholesale to LF would align it with the rest of the
- tree and remove the conflict permanently, at the cost of roughly two hundred
- line-ending-only changes in the diff. That is boundary-crossing work for a
- documentation slice whose intended change is six lines, so it is reported
- rather than performed. It belongs to a repository-hygiene decision or a later
- umbrella item, not to Step 1.

Boundary-crossing work:

- One item of boundary-crossing work was identified and deliberately not
- performed.
- `wiki/README.md` is stored with CRLF endings while every other staged file in
- this step is pure LF. Because the repository declares no `text` or `eol`
- attribute and `core.autocrlf` is `false`, and because Git's whitespace check
- counts CR at end of line as trailing whitespace, this one file cannot accept a
- new line in its own convention without failing `git diff --check`. Normalizing
- the file to LF would resolve that permanently and align it with the rest of the
- tree, but it would add roughly two hundred line-ending-only changes to a
- documentation slice whose intended change is six lines.
- That normalization is a repository-hygiene decision affecting a file the step
- only touches incidentally, so it exceeds Step 1 and is returned as feedback
- rather than edited. The repair applied here is the minimal in-step one: restore
- the five pre-existing lines the edit had rewritten, and leave the six added
- lines as LF so the declared gates pass.
- Nothing else crossed a boundary. No production module, protocol artifact,
- launcher, template, adapter, umbrella row, or other plan step was touched. No
- pre-existing unstaged or untracked writer work was swept into the index, and
- the applicable umbrella digest is unchanged.

### Writer instructions for step 1 review-mode-docs round 1 (exchange 1)

Step 1's content is complete and correct. Nothing in the documentation itself
needs rework, and the four reviewer repairs are already staged and attributed.
The next round exists because two of those repairs changed test code, which the
readiness rule forbids in a recommending round, not because the step is
unfinished.

Do two things before publishing round 2.

First, review the four staged reviewer repairs and keep or reverse each
deliberately. They are the line-ending restoration and the emoji-entity
replacement in `wiki/README.md`, the two named-constant replacements in the
acceptance package, and the single Step 1 line-budget row that follows from
them. If any is reversed, say so in the round 2 request so the next round
assesses the state you intend rather than the state this round left.

Second, refresh the stale theme sentence in
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`. Keep the opening
status line at `No, it is not implemented.`, since Steps 2 through 5 are
pending, but replace the claim that no implementation check has taken place
with wording that reflects a recorded Step 1 verdict and four pending steps.
That line sits outside the reviewed step's rows, so reviewer mode left it to
you.

The `wiki/README.md` line-ending question is not work for this step. Decide
separately whether that file should be normalized to LF like the rest of the
tree; until then the current state is correct, with the six added lines as LF
so both whitespace gates pass.

Do not treat this answer as commit authority. `a.commit` is accurate and needs
no amendment, every resolved validation command passed after the repairs, and
the umbrella digest is unchanged, so round 2 should be a short confirmation
round rather than a rework round. The commit still waits on the human choice at
the convergence gate.

### Decision rationale for step 1 review-mode-docs round 1 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is procedural
rather than a defect in the delivered step.

Five of the six readiness-floor results pass. Identity is exact: the envelope,
the human-readable request, the `pw` plan, the named step, the positive round,
and the request-time index tree all agree, and that index tree matched the live
index at entry. The implementation is complete, with every Step 1 file present
and the delivered behavior matching the step's intent. Mandatory validation and
coverage pass, with the full walk green at `cov=100` and `exit=0` after the
repairs and every resolved command run. Staged scope is attributable: ten paths,
nine named by the Step 1 file list and the tenth the validation plan, with every
reviewer patch proven attributable before staging. `a.commit` is accurate in
membership, grouping, order, scope, and conventional subjects, and needed no
amendment.

The sixth result is what blocks the recommendation. This round made two
substantive repairs, replacing character arithmetic with named module constants
in `conftest.py` and in the acceptance test module. Those change test code, and
the readiness rule states that a round making a substantive repair cannot
validly recommend commit readiness in the same round, however green the gates
are afterwards. That rule exists so the writer, not the reviewer, is the last
actor to have seen and accepted the code that a commit would carry, and it
applies here exactly as written.

Two unresolved findings also remain, though neither would block on its own. The
validation plan's document-level theme sentence still claims no implementation
check has taken place, which the staged Step 1 verdict contradicts, and it lies
outside the rows reviewer mode may write. The `wiki/README.md` line-ending
conflict is reported as boundary-crossing work rather than resolved, because
normalizing that file exceeds a six-line documentation slice.

The step is otherwise ready. Round 2 should be a short confirmation of the
staged repairs plus one writer-owned sentence, not a rework round. This answer
is advisory and authorizes no commit; the `Commit` or `Rework and review again`
choice remains with the human at the convergence gate.

### Final reviewer decision for step 1 review-mode-docs round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-20T15:01:31+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 review-mode-docs round 2

request_index_tree: eadbebddf914af382e1a88e2f45a5772a7ed2e98
resolved_validation_set:

- ghog day (sources: project)
- rg -n independent README.md wiki/README.md wiki/explanation/independent-review-mode-and-human-authority.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 1 review-mode-docs round 2

Step 1 is fully implemented and ready for a short confirmation round. The
request-time subject remains the ten-path staged documentation and acceptance-test
slice described by the plan. The opening validation-plan status correctly remains
`No, it is not implemented.` for the five-step effort, while its theme now records
that Step 1 is validated and Steps 2 through 5 remain pending.

All reviewer repairs from round 1 were reviewed and retained deliberately. The
two acceptance-test constant changes are substantive but behavior-preserving, so
this new round makes the writer the last actor to accept the code. No production
module, exchange protocol, umbrella row, or later implementation step changed.

The reviewer reran the complete Groundhog walk after the repairs: 1,882 tests,
`cov=100`, `outliers=0`, and `exit=0`. Both staged and unstaged whitespace checks
are clean. The commit plan remains accurate and requires no amendment.

### Implementation report for step 1 review-mode-docs round 2

Step 1 adds the independent-review authority explanation, links it from the two
entry points, and adds reciprocal comparison links to the existing self-review
pages. It also creates the versioned acceptance-coverage table and five bounded
repository acceptance tests for navigation order, visual identity, canonical
policy links, local targets, and coverage rows.

Round 1 restored the minimal six-line `wiki/README.md` diff, replaced the lone
HTML robot entity with the literal glyph used by its siblings, and replaced
character arithmetic in two acceptance-test files with named constants. The
validation record now reports the resulting 103-line fixture module and a
truthful partial-effort status. No whole-file line-ending normalization was made.

### Change summary for step 1 review-mode-docs round 2

The staged subject contains ten paths in two ordered commit groups. The first
group contains `README.md`, the Step 1 coverage document, the three acceptance
test files, `wiki/README.md`, the new independent-authority explanation, and the
two existing comparison pages. The second group contains only
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`.

Compared with the round-1 request, the staged subject retains the five reviewer
repairs and adds one writer-owned wording correction in the validation plan.
`wiki/README.md` is exactly six additions and zero deletions. The two named-
constant changes do not alter test behavior. `a.commit` still covers all ten
paths exactly and remains unchanged.

### Writer response for step 1 review-mode-docs round 2

Writer response: All round-1 changes are accepted. The minimal line-ending restoration and literal
robot glyph remain in `wiki/README.md`; `_MARKDOWN_SUFFIX`,
`_EMOJI_FRAGMENT_PREFIX`, and `_BACKTICK` remain in the acceptance package; and
the fixture line-budget row remains 103 lines.

The returned writer-owned finding is closed. The validation plan now says Step 1
is implemented and validated while Steps 2 through 5 remain pending, without
changing the document-level `No, it is not implemented.` status.

The possible whole-file LF normalization of `wiki/README.md` was explicitly a
repository-hygiene observation outside Step 1, not a requested repair. It remains
deferred. The current six added lines stay LF, the pre-existing lines retain their
stored endings, and both whitespace gates pass.

### Reviewer focus for step 1 review-mode-docs round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-20T15:16:37+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 review-mode-docs round 2 (exchange 1)

Baseline index tree: eadbebddf914af382e1a88e2f45a5772a7ed2e98

Assessed index tree: eadbebddf914af382e1a88e2f45a5772a7ed2e98

### Implementation check for step 1 review-mode-docs round 2 (exchange 1)

Result: Yes. Step 1 has been fully implemented.

The staged subject is unchanged from the state this reviewer assessed and
repaired in round 1, apart from one writer-owned wording correction in the
validation plan. Comparing the round-1 assessed index tree
`378c21f4dcfdd94926d34928127a0c54b991edec` with the round-2 request tree
`eadbebddf914af382e1a88e2f45a5772a7ed2e98` shows exactly one file changed and
exactly two lines within it, which is the theme sentence that round 1 returned
as a writer-owned finding.

Every Step 1 behavior the plan names is delivered. Both entry points route to
`wiki/explanation/independent-review-mode-and-human-authority.md` and use the
settled terms `self-review loop` and `independent review mode`. The explanation
names the requestor, reviewer, and human authorities, states that a convergence
recommendation does not authorize consolidation or commit, explains why the
transcript is durable evidence rather than working context, carries the generic
logo required by the settled Q15 decision, and attributes agent policy to the
three canonical instructions. The two self-review pages keep their purpose and
review logo while gaining reciprocal comparison callouts. The versioned coverage
record carries all twelve criterion rows and all six inventory-candidate rows.

The five acceptance tests pin exactly those behaviors and pass in focus and in
the full suite.

The staged set is the same ten paths: nine named by the consolidated Step 1
file list, plus the validation plan as review metadata. Nothing staged falls
outside the step, and the working tree holds no unstaged writer work.

The architecture assessment is unchanged and still clean. No production module
exists in this slice, the acceptance helpers read only paths a test supplies
and import no exchange, workflow, persistence, or domain code, every traversal
is linear in the declared page set, and no existing feature or reporting
capability is impaired.

The document-level status line correctly remains `No, it is not implemented.`
while Steps 2 through 5 are pending, and reviewer mode completed no umbrella
row.

Validation plan effects: Reviewer mode changed nothing in the validation plan this round. No row was
written for the reviewed step or for any other step, no document-level status
line was touched, and no umbrella row was completed.

The single validation-plan difference against the round-1 assessed state is
writer-authored and was assessed rather than rewritten. It replaces the theme
sentence that claimed no implementation check had taken place with one stating
that Step 1 is implemented and validated while Steps 2 through 5 remain
pending. That closes the writer-owned finding round 1 returned, and it is
correct in both directions: the claim now matches the recorded Step 1 verdict,
and the document-level `No, it is not implemented.` line above it is unchanged,
as it must be while four steps are still open.

The Step 1 rows themselves are unchanged from the state round 1 left, including
the line-budget row recording `conftest.py` at 103 lines and the test module at
129 lines, nine above its 120-line Step 1 advisory and below both the 550-line
split threshold and the 650-line ceiling. That variance remains recorded rather
than hidden, which is what the plan's shared checklist requires.

The verdict sentence keeps the exact `Yes. Step 1 has been fully implemented.`
form, followed by an empty line and a prose summary, as the template orders.

### Pre-repair mandatory checks and coverage for step 1 review-mode-docs round 2 (exchange 1)

No repair was made this round, so there is no pre-repair state to report and no
pre-repair blob was recorded.

The validation evidence backing this answer was measured after the writer
published, against the exact staged state being recommended. The `ghog day`
freshness path reported `exit=0` while skipping coverage, because no Python
file had changed since the round-1 green walk. That inherited result was not
accepted as sufficient for a readiness recommendation, so the walk was forced
and produced a measured `fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`,
`excluded=0`, and `exit=0`.

The writer's own reported walk before publication, 1,882 tests at `cov=100` and
`exit=0`, agrees with that measurement and was not relied upon in its place.

### Resolved validation set and sources for step 1 review-mode-docs round 2 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five and every one was run in this round.

`ghog day`, sourced from the project, first returned `exit=0` through its
freshness path, reporting that no Python file had changed since the last green
walk and therefore skipping coverage. Because this is the round that would
carry a commit-readiness recommendation, that inherited result was not treated
as sufficient evidence, and the walk was re-run with `--force`. The forced full
walk reported `fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`,
`excluded=0`, and `exit=0`, measured against the exact staged state being
recommended rather than against an earlier one.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

`rg -n independent README.md wiki/README.md wiki/explanation/independent-review-mode-and-human-authority.md`,
sourced from the plan, returned matches in all three files and `exit=0`.

`git diff --check`, sourced from the plan, returned no diagnostic and `exit=0`.

`git diff --cached --check`, sourced from the plan, returned no diagnostic and
`exit=0`. This is the gate that failed during an intermediate round-1 repair
attempt; the staged state has been clean since that attempt was corrected.

No mandatory command was unavailable, none was skipped, and none was recorded
as passing without being executed.

### Resolver drift and direction for step 1 review-mode-docs round 2 (exchange 1)

No resolver drift was observed.

The five commands embedded in the round-2 request envelope and the five the
current resolver produces are identical in content and in source attribution:
`ghog day` from the project, and the plan-sourced `rg` discovery check,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets, no command is present on one side only in either
direction, and nothing had to be added or dropped when the union was run. The
set is also unchanged from round 1.

### Repository state around validation for step 1 review-mode-docs round 2 (exchange 1)

The request-time index tree was `eadbebddf914af382e1a88e2f45a5772a7ed2e98`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

Comparing the round-1 assessed tree `378c21f4dcfdd94926d34928127a0c54b991edec`
with this round's tree shows one file changed and two lines within it:
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`, where the theme
sentence replaced the claim that no implementation check had taken place with a
statement that Step 1 is implemented and validated while Steps 2 through 5
remain pending. The document-level `No, it is not implemented.` line above it is
untouched, which is correct while four steps are still open. That is the whole
delta between the two rounds, so all five round-1 reviewer repairs are retained
by construction as well as by direct inspection.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the same ordered twelve-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. The forced full walk therefore produced no tracked validation side effect
at all. The only difference is the ignored artifact `a.ghog.status`, which the
walk rewrites by design; a difference confined to an ignored validation
artifact is acceptable, and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only untracked
file is the protocol transcript for this exchange, which the shared core owns.

### Repair inventory for step 1 review-mode-docs round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 1 review-mode-docs round 2 (exchange 1)

`a.commit` is accurate and needed no amendment in this round or the previous
one.

Its two groups cover exactly the ten staged paths with no omission and no
extra. Group 1, `docs(review-mode-docs): explain independent review authority`,
lists nine paths: both entry points, the new explanation, the two self-review
comparison pages, the three files of the acceptance package, and the coverage
record. Group 2, `docs(review-mode-docs): record step 1 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The documentation and its
acceptance evidence land first and the validation verdict that certifies them
lands last, so the recorded verdict never precedes the work it describes.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and both bodies state Why before What, naming the
umbrella, requirement, design, and plan as motivation.

The writer's theme-sentence correction landed in the validation plan, which
group 2 already owns, so it changed no group membership. Nothing moved between
groups, nothing was added, and nothing was removed. File membership, grouping,
order, scope, and conventional subjects all still match the staged work.

No commit was run, and this round staged nothing.

### Findings and boundaries for step 1 review-mode-docs round 2 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 review-mode-docs round 2 (exchange 1)

No changes are requested. Do not edit the staged subject in response to this
answer.

Present this recommendation to the human at the convergence gate together with
the identity summary, the staged changes, `a.commit`, and the requestor's own
assessment, and offer the registered choices `Commit` and
`Rework and review again`. This reviewer recommendation is advisory and
authorizes nothing on its own.

If the human chooses `Commit`, run the existing commit step against `a.commit`
exactly as it stands. Its two groups already match the ten staged paths in
dependency order and need no amendment. Do not restage, regroup, or reword
before committing.

If the human chooses `Rework and review again`, treat their guidance as the
scope of the next round. Nothing in this review contributes work to such a
round: no repair was made, no finding was left unaddressed, and no command was
missing.

One item is carried forward for a later decision rather than for this step.
`wiki/README.md` remains the CRLF file in an otherwise LF area of the tree, and
its six added lines are LF so both whitespace gates pass. Whether to normalize
that file belongs to repository hygiene or a later umbrella item, not to Step 1
and not to the commit decision in front of the human now.

### Decision rationale for step 1 review-mode-docs round 2 (exchange 1)

The disposition is `commit-ready`. All six readiness-floor results pass, and the
one condition that blocked round 1 no longer applies.

Identity is exact. The envelope, the human-readable request, the `pw` plan, the
named step, the positive round, and the request-time index tree all agree, and
that index tree matched the live index at entry.

The implementation is complete. Every Step 1 behavior named by the plan is
delivered, and the delta from the round-1 assessed state is one writer-owned
two-line wording correction in the validation plan.

Mandatory validation and coverage pass on the exact state being recommended.
The `ghog day` freshness path was refused as inherited evidence and the walk was
forced, giving `fail=0`, `cov=100`, `outliers=0`, and `exit=0`. All five
resolved commands ran, none was unavailable, and the resolver showed no drift.

Staged scope is attributable. Ten paths, nine named by the consolidated Step 1
file list and the tenth the validation plan as review metadata. No unstaged or
untracked writer work exists, and `validation-state compare` returned
`acceptable: true` with no tracked difference, so the forced walk left no
side effect.

No unresolved current or carried finding remains. The round-1 writer-owned
finding is closed, and the `wiki/README.md` line-ending item is an out-of-step
repository-hygiene observation rather than a blocking in-step finding.

`a.commit` is accurate in membership, grouping, order, scope, and conventional
subjects, and needed no amendment in either round.

The sixth condition is what changed. Round 1 could not recommend readiness
because it made two substantive repairs, replacing character arithmetic with
named constants in the acceptance package. This round made no repair at all.
The writer reviewed those repairs, retained them deliberately, corrected the
theme sentence, and published, so the writer is now the last actor to have
accepted the code a commit would carry. That is exactly the protection the rule
exists for, and it is satisfied rather than bypassed.

This recommendation is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice belongs to the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 1 review-mode-docs round 2 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-08-20T15:20:38+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-20T17:08:10+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 review-mode-docs round 1

request_index_tree: bbeadda8707100e3f9da26705306cf88703f05a3
resolved_validation_set:

- ghog day (sources: project)
- rg -n Requestor wiki/tutorials/09-run-your-first-specification-review.md wiki/tutorials/10-run-your-first-implementation-code-review.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 2 review-mode-docs round 1

Step 2 is fully implemented. The specification and implementation-code
tutorials are numbered `09` and `10`, cross-linked at the family divergence,
and independently runnable from two stages of one fictional effort. Each page
shows separate requestor and reviewer agent sessions, a bounded wait, the
returned `paths.answer`, an intermediate `changes-requested` round, round 2,
and the exact human choices.

The code tutorial separately pins the implementation plan and step,
`request_index_tree`, `resolved_validation_set`, `validation-state compare`,
`a.commit`, and the commit boundary. The specification tutorial keeps its
umbrella, reviewed specification, round, and consolidation boundary visible.
Both pages use the generic independent-review logo and cite the canonical
requestor and reviewer instructions as policy owners.

The focused package passes nine tests. The elevated Groundhog day walk finished
with `fail=0`, `cov=100`, `outliers=0`, and `exit=0`; its full phase took
2 minutes 53.6 seconds. The acceptance module is 204 lines against its 210-line
Step 2 advisory and remains below the 550-line split threshold. Architecture,
performance, class-specific coverage, and feature-integrity checks are clean.

### Implementation report for step 2 review-mode-docs round 1

Step 2 adds `wiki/tutorials/09-run-your-first-specification-review.md` and
`wiki/tutorials/10-run-your-first-implementation-code-review.md`. The wiki
tutorial list now links both pages without renumbering existing files, and the
versioned coverage table records AC03 complete plus partial AC06 and AC09
evidence while retaining later-step pending rows.

Four new acceptance tests pin the page numbers, conceptual order, reciprocal
links, generic logos, bounded two-agent handoff, exact returned answer field,
intermediate and convergence rounds, family-specific evidence, human choices,
coverage row, and local link resolution. No production module, launcher,
adapter, protocol artifact, or deferred umbrella item changed.

### Change summary for step 2 review-mode-docs round 1

The staged subject contains six paths in two dependency-ordered groups. Group 1
contains the coverage table, the acceptance module, `wiki/README.md`, and the
two new tutorials under `docs(review-mode-docs): teach review journeys`.
Group 2 contains only the validation plan under the mandatory
`docs(review-mode-docs): record step 2 validation` subject.

The validation plan records the exact Yes verdict, the 204-line acceptance
module, the nine-test focused result, the green full walk, and clean
architecture, performance, coverage, and feature integrity. `a.commit` covers
all six staged paths exactly; `git diff --cached --check` is clean.

### Writer response for step 2 review-mode-docs round 1

Writer response: This is the first code-review round for Step 2, so there is no earlier reviewer
feedback to accept or contest. The writer assessment reports the complete
tests-first implementation, exact staged scope, resolved validation commands,
line-budget result, and commit grouping for independent review.

### Reviewer focus for step 2 review-mode-docs round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-20T17:31:00+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 review-mode-docs round 1 (exchange 1)

Baseline index tree: bbeadda8707100e3f9da26705306cf88703f05a3

Assessed index tree: 7637a49a5c6a9341a9d813d29d8c679d906128af

### Implementation check for step 2 review-mode-docs round 1 (exchange 1)

Result: Yes. Step 2 has been fully implemented.

Both tutorials exist at the appended numbers `09` and `10`, with `01` through
`08` untouched, which is what the settled Q02 answer requires. Each is
independently runnable from its own starting point and cross-links the other at
the point where the families diverge, satisfying the settled Q03 pairing of one
fictional effort seen at two stages. Both carry the generic
`logo-llm-shared-transparent.png` that the settled Q15 constraint assigns to
independent review-mode pages.

Both tutorials teach the two-agent boundary the settled Q14 answer requires.
Each labels a Requestor and a Reviewer session, states plainly that switching
skills inside one session is not an independent review, shows the requestor
entering one bounded wait, returns through the `paths.answer` member of the
final JSON rather than a reconstructed filename, walks an intermediate
`changes-requested` round into a round 2, and stops at the human gate with the
exact registered choices. The specification tutorial names the umbrella,
reviewed specification, and round, and offers `Consolidate` or
`Revise and review again`. The code tutorial names the implementation plan,
implementation step, `request_index_tree`, `resolved_validation_set`,
`validation-state compare`, staged repair assessment, and `a.commit`, and offers
`Commit` or `Rework and review again`.

The reviewer verified the tutorials' factual claims against the shipped code
rather than reading them for plausibility. The statement that an empty
`a.review-mode` marker selects the default bounded wait matches
`ReviewConfiguration.load`, which returns the default wait for an empty marker
and accepts only a single `wait_timeout_seconds=` override line. The described
reviewer sequence, comparing the live index with `request_index_tree`, running
the resolved commands, comparing validation state, leaving an attributable
repair staged without committing, and stopping at exit `3`, matches the protocol
this very exchange is executing.

The four new acceptance tests precede the pages they pin and cover every
tests-first item the plan names for Step 2: numbering and cross-links, the two
sessions and the returned answer path, family-specific evidence and human
choices, and the completed AC03 coverage row with its pending Step 3 boundary.
The package now has nine green tests. The coverage record moved AC03 to
Complete, moved AC06 and AC09 forward, added a Step 2 executable-evidence
section, and left later rows pending, which is the incremental behavior the
settled Q04 answer requires.

The staged set is six paths: the five named by the Step 2 file list plus the
validation plan as review metadata. Nothing staged falls outside the step, and
the working tree holds no unstaged writer work beyond the protocol transcript.

The architecture assessment is clean. No production module changed, the
acceptance module only gained test functions and two path constants, every
traversal stays linear in a bounded declared path set, and no existing feature or
reporting capability is impaired. The acceptance module is 204 lines against its
210-line Step 2 advisory and well below the 550-line split threshold.

The document-level status line correctly remains `No, it is not implemented.`
while Steps 3 through 5 are pending, and reviewer mode completed no umbrella row.

Validation plan effects: Reviewer mode wrote no validation-plan row this round. The single repair touched
`wiki/README.md` only, changing line terminators rather than any recorded
figure, so no Step 2 row needed adjustment. In particular the acceptance module
stayed at 204 lines, so its line-budget row is still accurate as written.

The whole staged validation-plan difference is therefore writer work that was
assessed rather than rewritten. The Step 2 verdict sentence is the exact
`Yes. Step 2 has been fully implemented.` form, followed by an empty line and a
prose summary, as the template orders. The implemented inventory, architecture,
performance, unit-test-coverage, and feature-integrity subsections are present
with their required closing sentences, and the recorded 204-line figure against
the 210-line advisory is honest.

No row for any other step was touched, no umbrella row was completed, and the
document-level status line was not changed by reviewer mode. That line correctly
stays `No, it is not implemented.` while Steps 3 through 5 remain open. The
stale theme sentence directly beneath it is document-level rather than a Step 2
row, so it is returned as a writer-owned finding instead of being edited here.

### Pre-repair mandatory checks and coverage for step 2 review-mode-docs round 1 (exchange 1)

The writer reported a green focused package and a full walk at `cov=100`,
`outliers=0`, and `exit=0` before publishing. That report was not inherited as
this answer's evidence; every resolved command was re-run after the repair, and
`ghog day` was forced rather than allowed to short-circuit on freshness.

One pre-repair state was measured directly and is the origin of the repair. The
staged blob of `wiki/README.md` carried 194 CR against 205 LF while `HEAD`
carries 197 CR against 203 LF. `git diff --cached --numstat` reported five added
and three removed lines, while the same diff with `--ignore-cr-at-eol` reported
two added and zero removed. That pair of measurements proves three pre-existing
lines had been rewritten by line terminator alone.

Both whitespace commands passed before the repair, because the rewritten lines
were LF. This is the same blind spot recorded in Step 1: `git diff --check`
inspects trailing whitespace and conflict markers, not a change of line
terminator, so a CRLF-to-LF rewrite of untouched lines passes it silently.

The pre-repair blob for `wiki/README.md` was recorded as
`22265f6575e05bd0147d1d3e829110788f0663c7` before the first edit.

An intermediate repair attempt forced every unchanged line to CRLF, which
converted Step 1's six committed LF lines and made `git diff --check` report
trailing whitespace on nine lines with exit `2`. That attempt was corrected
before staging by preserving each unchanged line's original terminator, and the
final state is clean on both gates.

### Resolved validation set and sources for step 2 review-mode-docs round 1 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five and every one was run after the repair.

`ghog day`, sourced from the project, was run with `--force` rather than
accepting a freshness short-circuit, because the repair had touched a tracked
file. The forced full walk reported `fail=0`, `warn=0`, `xfail=0`, `cov=100`,
`outliers=0`, `excluded=0`, and `exit=0`.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0` across the nine
tests now in the package, five from Step 1 and four from Step 2.

`rg -n Requestor wiki/tutorials/09-run-your-first-specification-review.md wiki/tutorials/10-run-your-first-implementation-code-review.md`,
sourced from the plan, returned labelled requestor sessions in both tutorials
and `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`. Both were re-run after the line-ending
repair, since that repair is precisely the kind of change they police.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 2 review-mode-docs round 1 (exchange 1)

No resolver drift was observed.

The five commands embedded in the request envelope and the five the current
resolver produces are identical in content and in source attribution: `ghog day`
from the project, and the plan-sourced `rg -n Requestor` tutorial check,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets, no command appears on one side only in either
direction, and nothing was added or dropped when the union was run. Only the
plan-sourced `rg` target changed from the Step 1 set, which is expected because
each step names its own discovery check.

### Repository state around validation for step 2 review-mode-docs round 1 (exchange 1)

The request-time index tree was `bbeadda8707100e3f9da26705306cf88703f05a3`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. After the attributed repair was staged, the index tree is
`7637a49a5c6a9341a9d813d29d8c679d906128af`.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the ordered eight-path set returned
`acceptable: false`. That result is fully explained by this round's single
reviewer repair and contains no validation side effect. The tracked paths it
names are `wiki/README.md` and the index: the first is the one repair path,
whose pre-repair blob was recorded before editing and whose patch was proven
cleanly attributable before staging, and the index changed because that
attributed patch was staged. No other tracked path differs, so the forced full
walk wrote nothing tracked.

The only ignored path that differed is `a.ghog.status`, which the walk rewrites
by design. A difference confined to an ignored validation artifact is
acceptable, and it was neither staged nor reverted.

No untracked path differed. No pre-existing unstaged or untracked writer work
was swept into the index. The working tree's only unstaged entry is the protocol
transcript for this exchange, which the shared core owns and which correctly
stays outside the reviewed index.

### Repair inventory for step 2 review-mode-docs round 1 (exchange 1)

Repairs made:

- Restored the collateral line-ending churn in `wiki/README.md`, polishing-only.
- Three existing tutorial bullets for `01`, `02`, and `04` had been rewritten from CRLF to LF while their text stayed identical.
- The intended change is two added navigation lines, but the staged diff read five added and three removed.
- The repair gives every pre-existing line back its original terminator and leaves only the two new bullets as LF.
- Step 1's six committed LF lines were preserved rather than converted, so the file is 197 CR and 205 LF with eight LF-only lines.
- The staged diff is now exactly two added and zero removed, and both whitespace gates return no diagnostic.
- This repair changes no code, test, acceptance behavior, or commit grouping.

Paths staged:

- wiki/README.md

### Commit plan assessment for step 2 review-mode-docs round 1 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the six staged paths with no omission and no extra.
Group 1, `docs(review-mode-docs): teach review journeys`, lists five paths: both
new tutorials, the navigation page, the coverage record, and the acceptance
module. Group 2, `docs(review-mode-docs): record step 2 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The tutorials and their
acceptance evidence land first and the validation verdict that certifies them
lands last, so the recorded verdict never precedes the work it describes. That
matches the grouping Step 1 used, which keeps the effort's commit history
readable across steps.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope.

The reviewer repair did not change group membership. `wiki/README.md` was
already staged and already assigned to group 1, and the repair changed only its
line terminators. Nothing moved between groups, nothing was added, and nothing
was removed, so file membership, grouping, order, scope, and conventional
subjects all still match the staged work.

No commit was run.

### Findings and boundaries for step 2 review-mode-docs round 1 (exchange 1)

Unresolved findings:

- The validation plan's document-level theme sentence is stale again, writer-owned.
- It still reads that Step 1 is implemented and validated while Steps 2 through 5 remain pending, but this request records a Step 2 Yes verdict.
- The opening `No, it is not implemented.` line is correct and must stay while Steps 3 through 5 are open.
- Reviewer mode may write only the reviewed step's rows, so this document-level line is returned rather than edited.
- This is the same finding raised in Step 1 round 1 and fixed then; it recurs whenever a new step verdict lands without refreshing the sentence.

Boundary-crossing work:

- The `wiki/README.md` line-ending conflict remains an out-of-step repository-hygiene observation, unchanged from Step 1.
- That file is CRLF while its neighbours are LF, and Git counts CR at end of line as trailing whitespace, so a line added in the file's own convention fails `git diff --check` while an LF line passes and leaves the file mixed.
- Normalizing it wholesale to LF would add roughly two hundred line-ending-only changes to a two-line navigation edit, so it exceeds Step 2 and is reported rather than performed.
- Nothing else crossed a boundary: no production module, protocol artifact, launcher, template, adapter, umbrella row, or other plan step was touched.

### Writer instructions for step 2 review-mode-docs round 1 (exchange 1)

Step 2's content is complete and correct. The tutorials teach the two-agent
boundary accurately, their factual claims check out against the shipped code,
and the acceptance tests pin every tests-first item the plan names. One
writer-owned line and one accepted repair are all that stand between this step
and a readiness recommendation.

Do two things before publishing round 2.

First, refresh the document-level theme sentence in
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`. It still reads that
Step 1 is implemented and validated while Steps 2 through 5 remain pending,
which this request's own Step 2 verdict contradicts. Keep the opening
`No, it is not implemented.` line exactly as it is, since Steps 3 through 5 are
still open, and state instead that Steps 1 and 2 are implemented and validated
while Steps 3 through 5 remain pending. This is the same line that was corrected
after Step 1, so it is worth folding the refresh into the implementation-check
routine rather than waiting for a reviewer to return it each step.

Second, review the staged line-ending repair in `wiki/README.md` and keep or
reverse it deliberately. It restores three existing tutorial bullets to their
original terminators so the staged diff is the two lines you actually intended.
If you reverse it, say so in the round 2 request.

The wider `wiki/README.md` line-ending question is still not work for this step.
It remains a repository-hygiene decision about a file that is CRLF while its
neighbours are LF.

Do not treat this answer as commit authority. `a.commit` is accurate and needs
no amendment, every resolved command passed after the repair, the umbrella
digest is unchanged, and no tracked validation side effect exists, so round 2
should be a short confirmation round rather than a rework round.

### Decision rationale for step 2 review-mode-docs round 1 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is one
writer-owned line rather than a defect in the delivered step.

Five of the six readiness-floor results pass. Identity is exact, with the
envelope, human-readable request, `pw` plan, named step, positive round, and
request-time index tree all agreeing, and that tree matching the live index at
entry. The implementation is complete, and its factual claims were verified
against the shipped code rather than accepted as plausible. Mandatory validation
and coverage pass on the repaired state, with `ghog day` forced rather than
short-circuited and every resolved command run. Staged scope is attributable:
six paths, five named by the Step 2 file list and the sixth the validation plan,
with the single reviewer patch proven attributable before staging and no tracked
validation side effect. `a.commit` is accurate in membership, grouping, order,
scope, and conventional subjects.

The sixth result fails on an unresolved finding. The validation plan's
document-level theme sentence still says Step 1 is validated while Steps 2
through 5 are pending, which the staged Step 2 verdict contradicts. That line
sits outside the rows reviewer mode may write, so it cannot be repaired here and
must be returned. It is the same finding raised and fixed after Step 1, which is
why the writer instructions suggest folding the refresh into the routine rather
than rediscovering it each step.

This round's single repair is polishing-only. Restoring line terminators in
`wiki/README.md` changes no code, test, acceptance behavior, or commit grouping,
so the rule forbidding a substantive repair in a recommending round is not what
blocks readiness here. Had the theme sentence been current, this step would have
been recommendable.

The recurrence itself is worth naming. Step 1 saw five pre-existing lines
rewritten by terminator alone in this same file, and Step 2 saw three more. Both
times the staged diff overstated the change, and both times `git diff --check`
passed, because it does not inspect line terminators. Whatever writes this file
should preserve its existing terminators, or the same collateral churn will
recur in Steps 3 through 5.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 2 review-mode-docs round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-08-20T19:25:15+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 review-mode-docs round 2

request_index_tree: 7ae599206eb11477190235ed903d4f037aaa844a
resolved_validation_set:

- ghog day (sources: project)
- rg -n Requestor wiki/tutorials/09-run-your-first-specification-review.md wiki/tutorials/10-run-your-first-implementation-code-review.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 2 review-mode-docs round 2

Step 2 remains fully implemented and ready for a short confirmation round. The
only writer-owned finding is closed: the validation-plan theme now states that
Steps 1 and 2 are implemented and validated while Steps 3 through 5 remain
pending. Its document-level `No, it is not implemented.` status remains correct.

The reviewer’s polishing repair is deliberately retained. `wiki/README.md` is
now exactly two additions and zero deletions, preserving every unchanged line’s
stored terminator and the six LF additions committed in Step 1. Both whitespace
checks pass, and the broader line-ending policy question remains outside this
step.

Round 1 forced the complete Groundhog walk after the repair and measured
`cov=100`, `outliers=0`, and `exit=0`. No substantive reviewer repair was made,
the umbrella digest stayed unchanged, and `a.commit` still covers the six-path
subject in two ordered groups.

### Implementation report for step 2 review-mode-docs round 2

The implementation is unchanged from round 1 apart from the accepted
line-ending polish and the writer-owned validation theme. Tutorials `09` and
`10` remain cross-linked, independently runnable, and explicit about the two
agent sessions, bounded returned-answer path, intermediate round, family
evidence, and exact human choices.

The four Step 2 acceptance cases remain at 204 total module lines, and the
coverage record still marks AC03 complete while retaining later-step pending
work. No production, launcher, adapter, protocol, or later plan-step file was
changed.

### Change summary for step 2 review-mode-docs round 2

Relative to the round-1 request tree, `wiki/README.md` contains only the
reviewer’s terminator-preserving polish and the validation plan contains the
two-line theme refresh. The intended wiki change is exactly two additions and
zero deletions; no existing tutorial bullet is rewritten.

The staged subject remains six paths in two groups: tutorial content, coverage,
wiki list, and acceptance tests first; the Step 2 validation record second.
`a.commit` needs no membership, order, subject, or wording amendment.

### Writer response for step 2 review-mode-docs round 2

Writer response: Both round-1 instructions are accepted and closed. The reviewer’s
`wiki/README.md` repair remains staged, and the validation theme now names
Steps 1 and 2 as implemented and validated with Steps 3 through 5 pending.

The suggestion to make future implementation checks refresh the document-level
theme is recorded as a workflow improvement, but it is not a Step 2 tutorial
change and no shared instruction was modified in this round. The wider
whole-file LF conversion remains the same out-of-scope repository-hygiene
observation identified in Step 1.

### Reviewer focus for step 2 review-mode-docs round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-08-20T20:06:04+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 review-mode-docs round 2 (exchange 1)

Baseline index tree: 7ae599206eb11477190235ed903d4f037aaa844a

Assessed index tree: 7ae599206eb11477190235ed903d4f037aaa844a

### Implementation check for step 2 review-mode-docs round 2 (exchange 1)

Result: Yes. Step 2 has been fully implemented.

The staged subject is unchanged from the state this reviewer assessed and
repaired in round 1, apart from one writer-owned wording correction. Comparing
the round-1 assessed index tree `7637a49a5c6a9341a9d813d29d8c679d906128af` with
the round-2 request tree `7ae599206eb11477190235ed903d4f037aaa844a` shows
exactly one file changed and exactly two lines within it, which is the
document-level theme sentence returned as a finding in round 1.

Both tutorials remain in place at the appended numbers `09` and `10` with `01`
through `08` untouched, each independently runnable, cross-linked at the family
divergence, and carrying the generic logo the settled Q15 constraint assigns.
Each still labels a Requestor and a Reviewer session, shows one bounded wait,
returns through `paths.answer`, walks an intermediate `changes-requested` round
into a round 2, and stops at the exact registered human choices for its family.
The reviewer re-confirmed in round 1 that these claims match the shipped code,
including that an empty `a.review-mode` marker selects the default bounded wait.

The nine acceptance tests pass in focus and in the full suite. The coverage
record still carries AC03 as Complete with both tutorial paths, AC06 and AC09
advanced, later rows pending, and a Step 2 executable-evidence section.

The reviewer's round-1 repair is retained. `wiki/README.md` still shows exactly
two added and zero removed lines and still carries 197 CR against 205 LF, so the
three collateral tutorial bullets keep their original terminators and Step 1's
six committed LF lines are intact.

The staged set is the same six paths: five named by the Step 2 file list plus
the validation plan as review metadata. Nothing staged falls outside the step,
and the working tree holds no unstaged writer work beyond the protocol
transcript.

The architecture assessment is unchanged and clean. No production module
changed, every traversal stays linear in a bounded declared path set, and no
existing feature or reporting capability is impaired. The acceptance module
remains 204 lines against its 210-line Step 2 advisory.

The document-level status line correctly remains `No, it is not implemented.`
while Steps 3 through 5 are pending, and reviewer mode completed no umbrella row.

Validation plan effects: Reviewer mode changed nothing in the validation plan this round. No row was
written for the reviewed step or for any other step, no document-level status
line was touched, and no umbrella row was completed.

The single validation-plan difference against the round-1 assessed state is
writer-authored and was assessed rather than rewritten. It replaces the theme
sentence that named only Step 1 as validated with one stating that Steps 1 and 2
are implemented and validated while Steps 3 through 5 remain pending. That closes
the writer-owned finding round 1 returned, and it is correct in both directions:
the claim now matches the recorded Step 2 verdict, and the document-level
`No, it is not implemented.` line above it is unchanged, as it must be while
three steps are still open.

The Step 2 rows themselves are unchanged from the state round 1 left. The verdict
sentence keeps the exact `Yes. Step 2 has been fully implemented.` form, followed
by an empty line and a prose summary, as the template orders, and the recorded
204-line acceptance module against its 210-line advisory remains accurate.

### Pre-repair mandatory checks and coverage for step 2 review-mode-docs round 2 (exchange 1)

No repair was made this round, so there is no pre-repair state to report and no
pre-repair blob was recorded.

The evidence backing this answer was measured after the writer published, against
the exact staged state being recommended, and `ghog day` was forced rather than
allowed to short-circuit on freshness. The measured result is `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`, with
`Objective reached`.

One earlier forced walk in the same round reported `fail=1` and `exit=2` through
an environment-sensitive atomic-rename failure in an unrelated
review-exchange-core lifecycle test. It is recorded in full in the resolved
validation set and in the decision rationale rather than being averaged away
here. The failing test passes in focus, the following forced walk is green, and
the failure touches no file this step changed.

The writer's own reported walk before publication agrees with the green
measurement and was not relied upon in its place.

### Resolved validation set and sources for step 2 review-mode-docs round 2 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five and every one was run in this round.

`ghog day`, sourced from the project, was run with `--force` rather than
accepting a freshness short-circuit, because this round would carry a readiness
recommendation. It was run three times, and the middle run is the one that
matters for an honest record.

The first forced walk completed but its result line was not captured before the
subsequent focused run overwrote `a.ghog.log`, so it is not claimed as evidence.

The second forced walk reported `check` green and `affected --no-cov` green, and
then `ghog full done fail=1 warn=0 xfail=0 cov=withheld outliers=withheld
excluded=withheld exit=2`. The single failure was an error at setup of
`test_two_unchanged_rounds_escalate_without_deleting_evidence` in
`tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_tdd.py`.
The underlying error was `PermissionError: [WinError 5]` raised from
`os.replace` inside `publish_atomic` in `tools/review_exchange_store.py`, while
renaming a prepared temporary coordination file onto its target inside a pytest
temporary directory, surfaced as
`ReviewExchangeError: atomic publication failed`.

That failure was triaged rather than dismissed. Running
`ghog single tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_tdd.py`,
which is the follow-up ghog itself printed, reported nothing still failing in
focus, `fail=0`, and `exit=0`.

The third forced walk reported `check` green, `affected --no-cov` green,
`Objective reached`, and `ghog full done fail=0 warn=0 xfail=0 cov=100
outliers=0 excluded=0 exit=0`. That green result is measured against the exact
staged state being recommended.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0` across the nine
tests in the package.

`rg -n Requestor` over both tutorials, sourced from the plan, returned labelled
requestor sessions in each and `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 2 review-mode-docs round 2 (exchange 1)

No resolver drift was observed.

The five commands embedded in the round-2 request envelope and the five the
current resolver produces are identical in content and in source attribution:
`ghog day` from the project, and the plan-sourced `rg -n Requestor` tutorial
check, `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets, no command appears on one side only in either
direction, and nothing was added or dropped when the union was run. The set is
also unchanged from Step 2 round 1.

### Repository state around validation for step 2 review-mode-docs round 2 (exchange 1)

The request-time index tree was `7ae599206eb11477190235ed903d4f037aaa844a`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

Comparing the round-1 assessed tree `7637a49a5c6a9341a9d813d29d8c679d906128af`
with this round's tree shows one file changed and two lines within it:
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`, where the theme
sentence now states that Steps 1 and 2 are implemented and validated while Steps
3 through 5 remain pending. The document-level `No, it is not implemented.` line
above it is untouched, which is correct while three steps are still open. That is
the whole delta between rounds, so the round-1 line-ending repair is retained by
construction as well as by direct inspection.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the same ordered eight-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. Three forced full walks therefore produced no tracked validation side
effect at all. The only difference is the ignored artifact `a.ghog.status`, which
each walk rewrites by design; a difference confined to an ignored validation
artifact is acceptable, and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is the protocol transcript for this exchange, which the shared core owns
and which correctly stays outside the reviewed index.

### Repair inventory for step 2 review-mode-docs round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 2 review-mode-docs round 2 (exchange 1)

`a.commit` is accurate and needed no amendment in this round or the previous one.

Its two groups cover exactly the six staged paths with no omission and no extra.
Group 1, `docs(review-mode-docs): teach review journeys`, lists five paths: both
new tutorials, the navigation page, the coverage record, and the acceptance
module. Group 2, `docs(review-mode-docs): record step 2 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The tutorials and their
acceptance evidence land first and the validation verdict that certifies them
lands last, so the recorded verdict never precedes the work it describes. That
mirrors the grouping Step 1 used, keeping the effort's commit history consistent
across steps.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope.

The writer's theme-sentence correction landed in the validation plan, which group
2 already owns, so it changed no group membership. This round staged nothing at
all. File membership, grouping, order, scope, and conventional subjects all still
match the staged work.

No commit was run.

### Findings and boundaries for step 2 review-mode-docs round 2 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 review-mode-docs round 2 (exchange 1)

No changes are requested. Do not edit the staged subject in response to this
answer.

Present this recommendation to the human at the convergence gate together with
the identity summary, the staged changes, `a.commit`, and the requestor's own
assessment, and offer the registered choices `Commit` and
`Rework and review again`. This reviewer recommendation is advisory and
authorizes nothing on its own.

Present one fact alongside it rather than only the green summary. The mandatory
`ghog day` gate failed once during this round, with `fail=1` and `exit=2`, on
`test_two_unchanged_rounds_escalate_without_deleting_evidence`, through a
`PermissionError: [WinError 5]` raised by `os.replace` inside `publish_atomic`
in `tools/review_exchange_store.py`. The test passes in focus and a subsequent
forced full walk is green at `cov=100`. That failure is unrelated to Step 2 and
the human should see it when choosing, not discover it later.

If the human chooses `Commit`, run the existing commit step against `a.commit`
exactly as it stands. Its two groups already match the six staged paths in
dependency order and need no amendment. Do not restage, regroup, or reword
before committing.

If the human chooses `Rework and review again`, treat their guidance as the
scope of the next round. Nothing in this review contributes work to such a
round: no repair was made, no finding was left unaddressed, and no command was
missing.

Two items are carried forward for later decisions rather than for this step.
The intermittent atomic-rename failure belongs to review-exchange-core and
deserves a retry or a diagnosis by that requirement's owner; a documentation
slice cannot fix it. And `wiki/README.md` remains the CRLF file in an otherwise
LF area of the tree, so whatever writes it should preserve its existing
terminators, or the collateral churn repaired in Steps 1 and 2 will recur in
Steps 3 through 5.

### Decision rationale for step 2 review-mode-docs round 2 (exchange 1)

The disposition is `commit-ready`. All six readiness-floor results pass, and the
finding that blocked round 1 is closed.

Identity is exact. The envelope, human-readable request, `pw` plan, named step,
positive round, and request-time index tree all agree, and that tree matched the
live index at entry.

The implementation is complete. The delta from the round-1 assessed state is one
writer-owned two-line correction: the document-level theme sentence now reads
that Steps 1 and 2 are implemented and validated while Steps 3 through 5 remain
pending, with the opening `No, it is not implemented.` line correctly untouched.

Staged scope is attributable. Six paths, five named by the Step 2 file list and
the sixth the validation plan. This round made no repair at all, and
`validation-state compare` returned `acceptable: true` with no tracked
difference, so the forced walks left nothing tracked behind. The umbrella digest
is unchanged.

No unresolved current or carried finding remains. The round-1 finding is closed,
and the reviewer's round-1 line-ending repair is retained: `wiki/README.md` is
still exactly two added and zero removed lines at 197 CR and 205 LF.

`a.commit` is accurate in membership, grouping, order, scope, and conventional
subjects, and needed no amendment in either round.

This round made no substantive repair, so the rule that blocks a recommending
round does not apply.

One observation belongs in front of the human rather than hidden behind a green
summary. The mandatory `ghog day` gate failed once during this round, with
`fail=1` and `exit=2`, on
`test_two_unchanged_rounds_escalate_without_deleting_evidence` in the
review-exchange-core lifecycle tests. The cause was `PermissionError: [WinError 5]`
from `os.replace` inside `publish_atomic` in `tools/review_exchange_store.py`,
renaming a prepared temporary file onto its target in a pytest temporary
directory. The reviewer did not treat that as noise: the test passes in focus,
and a subsequent forced full walk is green at `cov=100` with `Objective reached`.

That failure is not a defect in Step 2. The failing test belongs to
review-exchange-core, an already completed umbrella item, and Step 2 changed only
two tutorials, one navigation page, the coverage record, and the acceptance
module. It is an environment-sensitive atomic-rename operation with no retry,
which on Windows can lose a race against a transient file lock. Hardening it is
work for the core owner, not for a documentation slice, and it is not something
this writer could resolve by reworking Step 2.

The readiness recommendation therefore rests on the green measured state, with
the intermittent failure recorded in the durable transcript so the human decides
with the full picture rather than a summary that omits it.

This recommendation is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice belongs to the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 2 review-mode-docs round 2 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 2 by human - Step 2 - human-confirmation

- Recorded: 2026-08-20T20:37:02+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-20T21:27:20+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 review-mode-docs round 1

request_index_tree: 88faa944c4a313ef817f1a5749f6e066637589bd
resolved_validation_set:

- ghog day (sources: project)
- rg -n Human wiki/how-to/recover-an-independent-review.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 3 review-mode-docs round 1

Step 3 is fully implemented. Five how-to pages assign all seven operational
goals: opt-in and opt-out, specification start and resume, code-review start and
resume, returned-result interpretation, durable authorized continuation,
ordinary reclaim, and stopped-state recovery. Each page has one how-to purpose,
uses the generic logo, follows final JSON `paths`, and prohibits manual protocol
artifact edits.

Recovery separates the ordinary lease path from `Human decision required`.
Forced reclaim, forced completion, and resolution all sit below that heading
with human authority, artifact-shape preconditions, and durable evidence
effects. Result guidance distinguishes exits `0`, `3`, and `2`, and continues
owning work only after `owning_action_authorized: true`.

Four new acceptance tests bring the package to thirteen tests and the module to
290 lines against its 320-line Step 3 advisory. A full walk first hit the known
review-exchange-core Windows `os.replace` race in two unrelated recovery tests;
both passed in Groundhog’s focused run. The required rerun then completed 1,890
tests with `cov=100`, `outliers=0`, and `exit=0`.

One polishing issue is disclosed rather than hidden: adding five links to the
mixed-ending `wiki/README.md` currently renders as 9 additions and 4
terminator-only deletions. `git diff --check` passes, but the earlier Step 1 and
2 review pattern shows those unchanged lines should be restored byte-for-byte.

### Implementation report for step 3 review-mode-docs round 1

Step 3 adds five focused guides under `wiki/how-to/`: marker activation,
specification review, implementation code review, result and authorized-action
handling, and recovery. The wiki list links them in the how-to category, and the
coverage document advances AC04 and AC07 to complete while leaving the Step 4
reference and Step 5 validation boundaries pending.

The recovery guide uses shipped launcher forms for ordinary `reclaim`, human
`reclaim --force`, human `complete --force`, `resolve`, and `archive`. Four
acceptance tests pin the page-to-goal map, local links, generic logos, final JSON
and exit rules, human heading order, forced command placement, recovery states,
and the coverage rows. No production module or protocol behavior changed.

Implementation-check records an exact Step 3 Yes and updates the document theme
to say Steps 1 through 3 are implemented and validated while Steps 4 and 5
remain pending, avoiding the stale-line finding from the prior two steps.

### Change summary for step 3 review-mode-docs round 1

The staged subject contains nine paths in two dependency-ordered groups. Group 1
contains the coverage table, acceptance module, wiki list, and five new guides
under `docs(review-mode-docs): add task guides`. Group 2 contains only the
validation plan under `docs(review-mode-docs): record step 3 validation`.

`a.commit` covers all nine staged paths exactly, and staged whitespace checks
are clean. The known `wiki/README.md` terminator churn is inside Group 1 and is
called out for reviewer repair; it does not alter grouping or the commit
subjects.

### Writer response for step 3 review-mode-docs round 1

Writer response: This is the first Step 3 code-review round, so there is no earlier reviewer
feedback to accept or contest. The request reports the exact staged subject,
green final walk, prior transient Windows failures, line budget, task coverage,
commit grouping, and the known mixed-ending wiki hunk for independent review.

### Reviewer focus for step 3 review-mode-docs round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-20T21:40:05+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-mode-docs round 1 (exchange 1)

Baseline index tree: 88faa944c4a313ef817f1a5749f6e066637589bd

Assessed index tree: 8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8

### Implementation check for step 3 review-mode-docs round 1 (exchange 1)

Result: Yes. Step 3 has been fully implemented.

The five how-to pages exist exactly as the consolidated design's topology
requires, and between them they own all seven operational goals: one opt-in page
covering enable and disable, one specification page and one implementation-code
page each covering start and resume, one results page covering the returned
result and authorized continuation, and one recovery page covering ordinary
reclaim and stopped-state recovery in separate sections. Each carries the
generic logo, an invocation model, and the instruction not to reconstruct
protocol filenames or edit protocol artifacts.

The recovery page satisfies the settled Q13 contract precisely. Ordinary reclaim
comes first, then a `## Human decision required` heading, then a blockquote
naming Authority, Precondition, and Evidence effect, and only after that do
`reclaim --force`, `complete --force`, `resolve`, and `archive` appear. No forced
command sits above that boundary.

The reviewer verified the protocol claims against the canonical instruction and
the shipped code rather than reading them for plausibility. Ordinary reclaim is
correctly limited to an intact lease-expired round and correctly described as
idempotent while the round is live and as leaving request, answer, and
transcript content untouched. `reclaim --force` correctly requires an escalated
exchange whose artifacts are intact and correctly restores the same round and
returns ownership from artifact shape. `complete --force` correctly requires the
intact artifact-free abandoned-mid-round shape and correctly disclaims
manufacturing convergence or owning authorization. `resolve` and `archive`
correctly start a fresh round, with archive preserving evidence under derived
names, and the page correctly forbids resuming the interrupted transition. The
exit contract on the results page matches the shipped meanings of `0`, `3`, and
`2`, and its warning not to read `outcome: published` as authorization is
exactly right: publication and the human gate are separate, as this very
exchange demonstrates. The `owning_action_authorized` and
`owning-action-pending` continuation rule matches the instruction, including not
asking the human twice. The opt-in page's 1,800-second default matches
`_DEFAULT_WAIT_SECONDS`, and its single `wait_timeout_seconds=` override matches
the marker parser.

One claim on the opt-in page was wrong and was repaired; it is recorded in the
repair inventory rather than counted against the step's completeness.

The four new acceptance tests precede the pages they pin and cover every
tests-first item the plan names for Step 3: the five-page topology with all seven
goals and no mixed Diataxis purpose, returned-path and exit-contract discipline,
the ordinary-before-human ordering with the three blockquote labels and the
forced commands below the boundary, and the completed AC04 and AC07 coverage
rows with the pending Step 4 boundary. The package is green.

The staged set is nine paths: the eight named by the Step 3 file list plus the
validation plan as review metadata. Nothing staged falls outside the step, and
the working tree holds no unstaged writer work beyond the protocol transcript.

The document-level theme sentence was refreshed proactively this round, without
a reviewer having to return it, and now reads that Steps 1 through 3 are
implemented and validated while Steps 4 and 5 remain pending. The opening
`No, it is not implemented.` line correctly stays while two steps are open.

The architecture assessment is clean. No production module changed, every
traversal stays linear in a bounded declared path set, and no existing feature
or reporting capability is impaired.

Validation plan effects: Reviewer mode wrote no validation-plan row this round. Neither repair changed a
recorded figure: one restored line terminators and the other corrected a
sentence in a how-to page, so no Step 3 row needed adjustment.

The whole staged validation-plan difference is therefore writer work that was
assessed rather than rewritten. The Step 3 verdict sentence is the exact
`Yes. Step 3 has been fully implemented.` form, followed by an empty line and a
prose summary, as the template orders, and the required subsections are present
with their closing sentences.

The document-level theme sentence was refreshed by the writer this round and now
reads that Steps 1 through 3 are implemented and validated while Steps 4 and 5
remain pending. That closes, at source, the finding this reviewer had to return
after Step 1 and again after Step 2. The opening `No, it is not implemented.`
line correctly stays while two steps are open.

No row for any other step was touched, and no umbrella row was completed.

### Pre-repair mandatory checks and coverage for step 3 review-mode-docs round 1 (exchange 1)

The writer reported 1,890 passing tests at 100% coverage with zero outliers
before publishing. That report was not inherited as this answer's evidence;
every resolved command was re-run after the repairs and `ghog day` was forced.

One pre-repair state was measured directly and is the origin of the line-ending
repair. The staged blob of `wiki/README.md` carried 193 CR against 210 LF while
`HEAD` carries 197 CR against 205 LF. `git diff --cached --numstat` reported nine
added and four removed lines, while the same diff with `--ignore-cr-at-eol`
reported five added and zero removed. That pair proves four pre-existing lines
had been rewritten by terminator alone.

Both whitespace commands passed before the repairs, because the rewritten lines
were LF. This is the same blind spot recorded in Steps 1 and 2: `git diff --check`
inspects trailing whitespace and conflict markers, not a change of line
terminator.

The second repair had no measurable pre-state beyond the sentence itself, which
is quoted in the repair inventory.

Pre-repair blobs were recorded for both paths before the first edit to each:
`wiki/README.md` at `27ff234765dc0e3b0b7f2f9c447a5bd32d894647` and
`wiki/how-to/enable-independent-review-mode.md` at
`d98660c39716a9af07127c5b38f7f6da4199d77a`.

### Resolved validation set and sources for step 3 review-mode-docs round 1 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five and every one was run after the repairs.

`ghog day`, sourced from the project, was run with `--force` rather than
accepting a freshness short-circuit, because the repairs had touched tracked
files. The forced walk reported `check` green, `affected --no-cov` green,
`Objective reached`, and `ghog full done fail=0 warn=0 xfail=0 cov=100
outliers=0 excluded=0 exit=0`.

The transient atomic-rename failure recorded during Step 2 did not recur in this
round.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

`rg -n Human wiki/how-to/recover-an-independent-review.md`, sourced from the
plan, matched the marked human-decision boundary and returned `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`. Both were re-run after the line-ending
repair, since that repair is precisely the kind of change they police.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 3 review-mode-docs round 1 (exchange 1)

No resolver drift was observed.

The five commands in the request envelope and the five the current resolver
produces are identical in content and source attribution: `ghog day` from the
project, and the plan-sourced `rg -n Human` recovery check,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets and nothing was added or dropped when it was run.
Only the plan-sourced `rg` target changed from Step 2, which is expected because
each step names its own discovery check.

### Repository state around validation for step 3 review-mode-docs round 1 (exchange 1)

The request-time index tree was `88faa944c4a313ef817f1a5749f6e066637589bd`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. After the two attributed repairs were staged, the index tree is
`8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8`.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the ordered eleven-path set returned
`acceptable: false`. That result is fully explained by this round's two reviewer
repairs and contains no validation side effect. The tracked paths it names are
`wiki/README.md`, `wiki/how-to/enable-independent-review-mode.md`, and the index:
the first two are exactly the repair paths, each with its pre-repair blob
recorded before editing and each proven cleanly attributable before staging, and
the index changed because those attributed patches were staged. No other tracked
path differs, so the forced full walk wrote nothing tracked.

The only ignored path that differed is `a.ghog.status`, which the walk rewrites
by design. A difference confined to an ignored validation artifact is
acceptable, and it was neither staged nor reverted.

No untracked path differed, and no pre-existing unstaged or untracked writer work
was swept into the index. The working tree's only unstaged entry is the protocol
transcript for this exchange, which the shared core owns and which correctly
stays outside the reviewed index.

### Repair inventory for step 3 review-mode-docs round 1 (exchange 1)

Repairs made:

- Corrected a factual claim about the disabled result in `wiki/how-to/enable-independent-review-mode.md`, documentation accuracy.
- The page said a direct status call returns final JSON with disabled state, null round, and no coordination path.
- The first two are right, but `_success_payload` in `tools/review_exchange_cli.py` sets the `paths` member unconditionally, so a disabled result still carries all six paths including `coordination`.
- Only the fatal-input payload returns an empty `paths` object.
- The page now says the state is disabled with a null round, the `paths` member is still populated, and the coordination artifact it names does not exist while the marker is absent.
- This matters more than usual because the same page instructs readers to follow the returned `paths`, so a reader could otherwise expect the key to be missing and misread a disabled result.
- No acceptance test pinned the replaced sentence, and the focused package stays green.
- Restored the collateral line-ending churn in `wiki/README.md`, polishing-only.
- Four pre-existing navigation lines had been rewritten from CRLF to LF while their text stayed identical, so the staged diff read nine added and four removed for an intended five-line change.
- The repair gives every pre-existing line back its original terminator and leaves only the five new bullets as LF, preserving the eight LF lines committed in Steps 1 and 2.
- The file is now 197 CR and 210 LF, the staged diff is exactly five added and zero removed, and both whitespace gates return no diagnostic.
- This is the third consecutive step in which this same file arrived with collateral terminator churn, after five such lines in Step 1 and three in Step 2.

Paths staged:

- wiki/README.md
- wiki/how-to/enable-independent-review-mode.md

### Commit plan assessment for step 3 review-mode-docs round 1 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the nine staged paths with no omission and no extra.
Group 1, `docs(review-mode-docs): add task guides`, lists eight paths: the five
new how-to guides, the navigation page, the coverage record, and the acceptance
module. Group 2, `docs(review-mode-docs): record step 3 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The guides and their acceptance
evidence land first and the validation verdict that certifies them lands last,
so the recorded verdict never precedes the work it describes. That matches the
grouping Steps 1 and 2 used, keeping the effort's commit history consistent.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope.

Neither reviewer repair changed group membership. `wiki/README.md` and
`wiki/how-to/enable-independent-review-mode.md` were both already staged and
already assigned to group 1. Nothing moved between groups, nothing was added, and
nothing was removed, so file membership, grouping, order, scope, and conventional
subjects all still match the staged work.

No commit was run.

### Findings and boundaries for step 3 review-mode-docs round 1 (exchange 1)

Unresolved findings: None.

Boundary-crossing work:

- The `wiki/README.md` line-ending conflict has now recurred in three consecutive steps and deserves a sharper recommendation than repeating the in-step repair.
- That file is CRLF while every other file in this area of the tree is LF, and Git counts CR at end of line as trailing whitespace, so a line added in the file's own convention fails `git diff --check` while an LF line passes and leaves the file mixed.
- Step 1 arrived with five pre-existing lines rewritten by terminator alone, Step 2 with three, and Step 3 with four; each was repaired inside its step, and each repair was necessary only because the file cannot be edited cleanly in its own convention.
- Steps 4 and 5 both touch this file again, for inventory links and final navigation, so without a root fix the same collateral churn and the same reviewer repair will recur twice more.
- The root fix is to normalize `wiki/README.md` to LF once, matching the rest of the tree and ending the conflict permanently.
- That is roughly two hundred line-ending-only changes, which is why it does not belong inside a documentation slice whose intended change is a handful of navigation lines.
- It does belong in its own standalone commit, separate from any review-mode-docs group, where the churn is self-explanatory and reviewable on its own terms.
- This reviewer cannot make that change, because a whole-file normalization exceeds Step 3 and would bury the step's real diff.
- Nothing else crossed a boundary: no production module, protocol artifact, launcher, template, adapter, umbrella row, or other plan step was touched.

### Writer instructions for step 3 review-mode-docs round 1 (exchange 1)

Step 3's content is complete and correct, and the recurring theme-sentence
finding is closed at source this round. Two staged reviewer repairs and one
standing recommendation are all that remain.

Do two things before publishing round 2.

First, review the corrected sentence in
`wiki/how-to/enable-independent-review-mode.md` and keep or reword it
deliberately. It replaces the claim that a disabled status call returns no
coordination path with the accurate statement that the state is disabled with a
null round, the `paths` member is still populated, and the coordination artifact
it names does not exist while the marker is absent. This is your prose in your
page, so the wording is yours to settle even though the fact is not.

Second, review the staged line-ending repair in `wiki/README.md` and keep or
reverse it. It restores four existing navigation lines to their original
terminators so the staged diff is the five lines you actually intended.

Then consider the standing recommendation, which is not Step 3 work and not a
condition of this step passing. `wiki/README.md` has now arrived with collateral
terminator churn in three consecutive steps, and Steps 4 and 5 touch it again.
Normalizing the file to LF once, in its own standalone commit outside any
review-mode-docs group, ends the recurrence and keeps roughly two hundred
line-ending-only changes out of your documentation slices. Doing it before Step 4
would spare two more rounds of this.

Do not treat this answer as commit authority. `a.commit` is accurate and needs no
amendment, every resolved command passed after the repairs, the umbrella digest
is unchanged, and no tracked validation side effect exists, so round 2 should be
a short confirmation round rather than a rework round.

### Decision rationale for step 3 review-mode-docs round 1 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is that this
round changed the words a reader will see, not that the step is unfinished.

Five of the six readiness-floor results pass. Identity is exact, with the
envelope, human-readable request, `pw` plan, named step, positive round, and
request-time index tree all agreeing, and that tree matching the live index at
entry. The implementation is complete, and its protocol claims were checked
against the canonical instruction and the shipped code rather than accepted as
plausible. Mandatory validation and coverage pass on the repaired state, with
`ghog day` forced rather than short-circuited and every resolved command run.
Staged scope is attributable: nine paths, eight named by the Step 3 file list and
the ninth the validation plan, with both reviewer patches proven attributable
before staging and no tracked validation side effect. `a.commit` is accurate in
membership, grouping, order, scope, and conventional subjects.

No unresolved finding remains, and that is worth stating plainly. The
document-level theme sentence, which had to be returned after Step 1 and again
after Step 2, was refreshed proactively this round. The recurring finding is
closed at its source rather than re-reported.

The sixth result is what blocks the recommendation. One of this round's two
repairs rewrote a factual claim in a delivered page: the opt-in guide said a
disabled status result carries no coordination path, and in fact
`_success_payload` populates `paths` unconditionally, so a disabled result
returns all six paths while the coordination artifact simply does not exist.

Read strictly, that repair changes no code, test, acceptance behavior, or commit
grouping, so the letter of the rule would allow a readiness recommendation. Read
for its purpose, it should not. The rule exists so the writer is the last actor
to accept what a commit carries, and for a documentation effort the delivered
product is the prose. A reviewer rewriting a user-facing statement about
protocol behavior and certifying it commit-ready in the same round is exactly
the situation the rule guards against, so this answer treats that repair as
substantive and returns the round.

The second repair is genuinely polishing-only. Restoring line terminators in
`wiki/README.md` changes no reader-visible content at all.

That line-ending churn is now three for three, at five collateral lines in Step
1, three in Step 2, and four in Step 3, and Steps 4 and 5 both touch the same
file. The boundary-crossing report recommends the root fix rather than a fourth
and fifth repair: normalize the file to LF once, in its own standalone commit,
outside any documentation slice.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 3 review-mode-docs round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-08-20T21:48:32+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 review-mode-docs round 2

request_index_tree: 8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8
resolved_validation_set:

- ghog day (sources: project)
- rg -n Human wiki/how-to/recover-an-independent-review.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 3 review-mode-docs round 2

Step 3 remains fully implemented. The round 1 reviewer found no unresolved
implementation gap and verified the five-guide topology, all seven operational
goals, the human-only forced-recovery boundary, the returned-path contract, and
the exit and authorization rules against shipped behavior.

Both staged reviewer repairs are accepted deliberately. The corrected disabled
status wording now distinguishes populated returned paths from the absent
coordination artifact, and the wiki navigation diff now contains exactly the
five intended additions with no terminator-only removal.

The reviewer reran the complete five-command validation union after both
repairs. Groundhog completed 1,890 tests with full coverage, no outliers, and a
zero exit; the focused package, recovery grep, and both whitespace checks also
passed.

### Implementation report for step 3 review-mode-docs round 2

No additional implementation change was needed after round 1. The writer keeps
the reviewer's factual correction in the opt-in guide verbatim because it
matches `_success_payload`: disabled status still returns the six path names,
while the coordination artifact named by that result does not exist without
the marker.

The writer also keeps the line-ending repair in `wiki/README.md`. Its staged
diff is five additions and zero removals, preserving every pre-existing line's
terminator and the eight LF additions committed by Steps 1 and 2.

The five how-to pages, acceptance tests, coverage updates, and Step 3 validation
record are otherwise unchanged from the implementation assessed in round 1.

### Change summary for step 3 review-mode-docs round 2

The staged subject remains nine paths in the same two dependency-ordered groups.
`a.commit` still assigns the eight documentation and acceptance paths to
`docs(review-mode-docs): add task guides` and the validation plan to
`docs(review-mode-docs): record step 3 validation`.

Round 1 changed two already-grouped paths: one user-facing sentence in the
opt-in guide and four terminators in the wiki navigation file. No path entered
or left the index, no group membership changed, and `git diff --cached --check`
is clean.

Whole-file LF normalization of `wiki/README.md` is accepted as useful follow-up
work, but it is intentionally excluded from this Step 3 review subject. It can
land as a standalone commit after Step 3 and before Step 4.

### Writer response for step 3 review-mode-docs round 2

Writer response: The writer accepts both round 1 repairs without amendment and raises no
disagreement. The corrected disabled-result sentence matches shipped behavior,
and the navigation repair leaves exactly the five intended additions.

No unresolved Step 3 finding remains, and the writer introduced no new tracked
work. Round 2 requests confirmation over the repaired index with the same
validation commands and commit plan.

### Reviewer focus for step 3 review-mode-docs round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-08-20T22:01:06+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 review-mode-docs round 2 (exchange 1)

Baseline index tree: 8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8

Assessed index tree: 8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8

### Implementation check for step 3 review-mode-docs round 2 (exchange 1)

Result: Yes. Step 3 has been fully implemented.

The staged subject is byte-identical to the state this reviewer assessed and
repaired in round 1. The request-time index tree
`8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8` is the same value this reviewer
recorded as its round-1 assessed tree, and the live index matches it, so both
reviewer repairs were accepted unchanged and nothing else was staged.

That was verified directly as well as by tree identity. `wiki/README.md` still
shows exactly five added and zero removed lines and still carries 197 CR against
210 LF, so every pre-existing line keeps its original terminator and the thirteen
LF lines are the ones added across Steps 1 through 3. The corrected sentence in
`wiki/how-to/enable-independent-review-mode.md` is present, stating that a
disabled result reports a disabled state and a null round while its `paths`
member is still populated and the coordination artifact it names does not exist.

Everything assessed in round 1 therefore still holds. The five guides own all
seven operational goals with one Diataxis purpose each, the recovery page places
ordinary reclaim before a marked `Human decision required` heading whose
blockquote names Authority, Precondition, and Evidence effect, and all four
forced commands sit below that boundary. The protocol claims were checked in
round 1 against the canonical instruction and the shipped code and were accurate,
with the single exception that has since been repaired and accepted.

The four acceptance tests pin the five-page topology, returned-path and exit
discipline, the ordinary-before-human ordering, and the completed AC04 and AC07
coverage rows with the pending Step 4 boundary. The package is green.

The staged set is nine paths: the eight named by the Step 3 file list plus the
validation plan as review metadata. Nothing staged falls outside the step, and
the working tree holds no unstaged writer work beyond the protocol transcript.

The document-level theme sentence still reads that Steps 1 through 3 are
implemented and validated while Steps 4 and 5 remain pending, with the opening
`No, it is not implemented.` line correctly unchanged.

The architecture assessment is unchanged and clean. No production module
changed, every traversal stays linear in a bounded declared path set, and no
existing feature or reporting capability is impaired.

Validation plan effects: Reviewer mode changed nothing in the validation plan this round, and made no
repair anywhere. No row was written for the reviewed step or any other step, no
document-level status line was touched, and no umbrella row was completed.

There is also no writer-authored validation-plan difference to assess against
round 1: the index tree is identical, so the validation plan is byte-for-byte the
document this reviewer already assessed. Its Step 3 verdict keeps the exact
`Yes. Step 3 has been fully implemented.` form followed by an empty line and a
prose summary, and its required subsections carry their closing sentences.

The document-level theme sentence, refreshed by the writer in round 1 without a
reviewer having to return it, still reads that Steps 1 through 3 are implemented
and validated while Steps 4 and 5 remain pending.

### Pre-repair mandatory checks and coverage for step 3 review-mode-docs round 2 (exchange 1)

No repair was made this round, so there is no pre-repair state to report and no
pre-repair blob was recorded.

The evidence backing this answer was measured after the writer published, against
the exact staged state being recommended, and `ghog day` was forced rather than
allowed to short-circuit on freshness. The measured result is `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`, with
`Objective reached`.

The transient atomic-rename failure observed once during Step 2 did not recur in
either Step 3 round.

### Resolved validation set and sources for step 3 review-mode-docs round 2 (exchange 1)

The request supplied five commands and the current resolver produced the same
five, so the union is five and every one was run in this round.

`ghog day`, sourced from the project, was run with `--force` rather than
accepting a freshness short-circuit, because this round would carry a readiness
recommendation. It reported `check` green, `affected --no-cov` green,
`Objective reached`, and `ghog full done fail=0 warn=0 xfail=0 cov=100
outliers=0 excluded=0 exit=0`.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from the
plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

`rg -n Human wiki/how-to/recover-an-independent-review.md`, sourced from the
plan, matched the marked human-decision boundary and returned `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 3 review-mode-docs round 2 (exchange 1)

No resolver drift was observed.

The five commands in the round-2 request envelope and the five the current
resolver produces are identical in content and source attribution: `ghog day`
from the project, and the plan-sourced `rg -n Human` recovery check,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets, nothing was added or dropped when it was run, and the
set is unchanged from Step 3 round 1.

### Repository state around validation for step 3 review-mode-docs round 2 (exchange 1)

The request-time index tree was `8c164e9cefbdbc37ce1fcb19c4c6a6a0dbdc99b8`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

That tree is also the exact value this reviewer recorded as its round-1 assessed
tree. The staged subject is therefore byte-identical across the two rounds: both
reviewer repairs were accepted unchanged, nothing was reversed, and no further
writer work was staged.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the same ordered eleven-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. The forced full walk produced no tracked validation side effect at all. The
only difference is the ignored artifact `a.ghog.status`, which the walk rewrites
by design; a difference confined to an ignored validation artifact is
acceptable, and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is the protocol transcript for this exchange, which the shared core owns
and which correctly stays outside the reviewed index.

### Repair inventory for step 3 review-mode-docs round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 review-mode-docs round 2 (exchange 1)

`a.commit` is accurate and needed no amendment in this round or the previous one.

Its two groups cover exactly the nine staged paths with no omission and no extra.
Group 1, `docs(review-mode-docs): add task guides`, lists eight paths: the five
new how-to guides, the navigation page, the coverage record, and the acceptance
module. Group 2, `docs(review-mode-docs): record step 3 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The guides and their acceptance
evidence land first and the validation verdict that certifies them lands last, so
the recorded verdict never precedes the work it describes. That matches the
grouping Steps 1 and 2 used, keeping the effort's commit history consistent.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope.

This round staged nothing, and the round-1 repairs touched only files already
assigned to group 1, so file membership, grouping, order, scope, and conventional
subjects all still match the staged work.

No commit was run.

### Findings and boundaries for step 3 review-mode-docs round 2 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 review-mode-docs round 2 (exchange 1)

No changes are requested. Do not edit the staged subject in response to this
answer.

Present this recommendation to the human at the convergence gate together with
the identity summary, the staged changes, `a.commit`, and the requestor's own
assessment, and offer the registered choices `Commit` and
`Rework and review again`. This reviewer recommendation is advisory and
authorizes nothing on its own.

If the human chooses `Commit`, run the existing commit step against `a.commit`
exactly as it stands. Its two groups already match the nine staged paths in
dependency order and need no amendment. Do not restage, regroup, or reword before
committing.

If the human chooses `Rework and review again`, treat their guidance as the scope
of the next round. Nothing in this review contributes work to such a round: no
repair was made, no finding was left unaddressed, and no command was missing.

One planned action is carried forward and is deliberately not a condition of this
step. The whole-file LF normalization of `wiki/README.md` is deferred to a
standalone commit after Step 3, which is the recommendation round 1 made and the
right sequencing: it keeps roughly two hundred line-ending-only changes out of
the documentation slices, and doing it before Step 4 spares two further rounds of
the collateral churn this reviewer repaired in each of the first three steps.

### Decision rationale for step 3 review-mode-docs round 2 (exchange 1)

The disposition is `commit-ready`. All six readiness-floor results pass, and the
condition that blocked round 1 no longer applies.

Identity is exact. The envelope, human-readable request, `pw` plan, named step,
positive round, and request-time index tree all agree, and that tree matched the
live index at entry.

The implementation is complete. The staged subject is byte-identical to the state
assessed in round 1, since the request-time tree is the same value this reviewer
recorded as its round-1 assessed tree. Both repairs were accepted unchanged and
nothing was reversed.

Mandatory validation and coverage pass on the exact state being recommended. The
`ghog day` freshness path was refused as inherited evidence and the walk was
forced, giving `fail=0`, `cov=100`, `outliers=0`, and `exit=0`. All five resolved
commands ran, none was unavailable, and the resolver showed no drift.

Staged scope is attributable. Nine paths, eight named by the Step 3 file list and
the ninth the validation plan. This round staged nothing, and
`validation-state compare` returned `acceptable: true` with no tracked
difference, so the forced walk left nothing behind. The umbrella digest is
unchanged.

No unresolved current or carried finding remains. The theme-sentence finding was
closed at source in round 1, and the corrected disabled-result sentence is
present and accepted.

`a.commit` is accurate in membership, grouping, order, scope, and conventional
subjects, and needed no amendment in either round.

The sixth condition is what changed. Round 1 could not recommend readiness
because it rewrote a factual claim in a delivered page, and for a documentation
effort the prose is the product, so the writer had to be the last actor to accept
it. This round made no repair at all. The writer reviewed both repairs, kept
them, and published, so that condition is satisfied rather than bypassed.

One planned action stands outside this step and is not a reservation about it.
The whole-file LF normalization of `wiki/README.md` is deferred to a standalone
commit after Step 3. That is the right sequencing, and doing it before Step 4
would end the collateral terminator churn this reviewer repaired in each of the
first three steps rather than repeating the repair twice more.

This recommendation is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice belongs to the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 3 review-mode-docs round 2 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 2 by human - Step 3 - human-confirmation

- Recorded: 2026-08-20T22:09:53+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-08-20T23:04:07+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 review-mode-docs round 1

request_index_tree: 3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c
resolved_validation_set:

- ghog day (sources: project)
- rg -n disabled wiki/reference/independent-review-mode-contract.md (sources: plan)
- rg -n fatal wiki/reference/independent-review-mode-contract.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 4 review-mode-docs round 1

Step 4 is fully implemented. The central reference contains the corrected
seventeen-state vocabulary, the exact twenty-four-outcome snapshot, seven
mandatory result fields, six returned path keys, human choices, operation
ownership, and the three-host adapter matrix.

All six inventory candidates were assessed and updated only within their
existing subjects. The coverage record names every disposition, and wiki
navigation links the new reference in the reference category.

Groundhog completed 1,894 tests with `fail=0`, `cov=100`, `outliers=0`, and
`exit=0`; the full phase took 2m58.6s. The acceptance module is 418 lines,
below its 420-line Step 4 advisory and 650-line ceiling. Architecture,
performance, unit-coverage applicability, and feature-integrity checks are
clean.

Two implementation fixes preceded the green walk. A repeated-membership helper
removed a Radon complexity failure without dropping assertions, and three
evolving coverage assertions were updated after the first affected run exposed
their stale pending-state expectations. The focused rerun passed 17/17 before
the final full walk.

### Implementation report for step 4 review-mode-docs round 1

Step 4 adds `wiki/reference/independent-review-mode-contract.md` as the single
user-facing lookup for marker configuration, exchange identity, artifacts,
states, operations, outcomes, final JSON, exits, human choices, host adapters,
and canonical policy ownership.

The state matrix derives all fifteen `ArtifactState` values and separately
documents launcher-only `disabled` and fatal exit-2 `fatal`. The outcome table
pins the reviewed twenty-four values and names plain and conditional
`OperationResult`, `WaitOutcome`, `ConfirmationOutcome`, and the fatal payload
as its sources.

Skills, artifacts, launchers, templates, automation ownership, and repository
layout each gained a narrow inventory entry plus the central link. The coverage
table records all six as `Update`, and four acceptance tests pin the complete
contract and bounded local links.

### Change summary for step 4 review-mode-docs round 1

The staged subject contains eleven paths in two dependency-ordered groups.
Group 1 contains the central reference, six inventory pages, wiki navigation,
the versioned coverage record, and the acceptance module under
`docs(review-mode-docs): publish review contract`.

Group 2 contains only the validation plan under the mandatory
`docs(review-mode-docs): record step 4 validation` subject. `a.commit` covers
all eleven staged paths exactly, both Why sections narrate the umbrella draft,
focused draft, feature request, design, plan, and validation plan, and staged
whitespace is clean.

The earlier standalone LF normalization of `wiki/README.md` is already commit
`0e9d711`; Step 4 adds one text line to the now-uniform LF file and carries no
line-ending-only churn.

### Writer response for step 4 review-mode-docs round 1

Writer response: This is the first Step 4 review round, so there is no earlier reviewer feedback
to accept or contest. The request reports the corrected fatal-state divergence
from the consolidated design, every inventory disposition, the two pre-green
test fixes, the final Groundhog evidence, line budgets, and the exact commit
groups for independent assessment.

### Reviewer focus for step 4 review-mode-docs round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-08-21T08:59:01+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 review-mode-docs round 1 (exchange 1)

Baseline index tree: 3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c

Assessed index tree: 3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c

### Implementation check for step 4 review-mode-docs round 1 (exchange 1)

Result: Yes. Step 4 has been fully implemented.

The central reference at `wiki/reference/independent-review-mode-contract.md`
records the shipped contract accurately, and the reviewer verified its
load-bearing tables against the code rather than reading them for plausibility.

The state matrix has exactly seventeen rows. Fifteen are the `ArtifactState`
members, all present and none invented, and the remaining two are the
launcher-only `disabled` and `fatal` states. The `fatal` row carries the detail
that distinguishes it, naming the null `identity`, empty `paths`, null round, and
`fatal-input` outcome, which is the correction this reviewer raised during plan
review and again in Step 3.

The outcome snapshot lists exactly the twenty-four values this reviewer
reconstructed independently from the code, with correct source-shape
attribution, including `escalated` correctly marked as reachable both as a wait
outcome and as a plain operation result. The page states plainly that outcomes
are the one contract column without a single typed model and that later launcher
changes must update the table deliberately, with no AST drift tooling added here.

The final result contract names the seven mandatory fields exactly as
`_success_payload` builds them and the six path keys exactly as
`_paths_payload` returns them, marks `exchange_occurrence` and
`owning_action_authorized` as conditional, and gives the correct meanings for
exits `0`, `3`, and `2`. The operation summary covers the full surface including
`repair-request-transcript`, which this reviewer had noted as belonging to the
reference rather than to the Step 3 recovery guide.

The host adapter matrix records the three hosts with their wrapper locations,
prefixes, and delegation boundaries, and states explicitly that the shared
`review-requestor` wrapper is absent under `.claude/skills/`, pointing readers at
the family-specific route instead. Every path in the shipped-sources list
resolves.

The six inventory candidates were assessed rather than filled in mechanically,
which is what the settled plan answer requires. Each edit is genuinely
subject-matched and narrow: artifact rows in the artifact inventory, launcher
rows in the launcher inventory, a skills paragraph in the skills catalog, an
automation-boundary row in the automation page, template rows in the template
inventory, and layout entries in the repository layout. Each defers detail to the
central reference instead of copying the contract, and the coverage table records
all six as `Update` with a concrete reason.

The four new acceptance tests pin the source-derived state, payload, outcome,
host, and inventory enumerations, and the package is green.

The staged set is eleven paths: the ten named by the Step 4 file list plus the
validation plan as review metadata. Nothing staged falls outside the step, and
the working tree holds no unstaged writer work beyond the protocol transcript.

The standalone LF normalization landed and worked. `wiki/README.md` is now pure
LF, and for every staged file the ordinary numstat equals the
`--ignore-cr-at-eol` numstat, so this is the first step in the effort with no
collateral terminator churn and no line-ending repair.

The document-level theme sentence was again refreshed proactively, now reading
that Steps 1 through 4 are implemented and validated while Step 5 remains
pending, with the opening `No, it is not implemented.` line correctly unchanged.

The architecture assessment is clean. No production module changed, every
traversal stays linear in a bounded declared path set, and no existing feature or
reporting capability is impaired.

Validation plan effects: Reviewer mode wrote no validation-plan row this round and made no repair
anywhere, so there is no reviewer-authored validation-plan difference.

The whole staged validation-plan difference is writer work that was assessed
rather than rewritten. The Step 4 verdict sentence is the exact
`Yes. Step 4 has been fully implemented.` form followed by an empty line and a
prose summary, as the template orders, and the required subsections carry their
closing sentences.

The document-level theme sentence now reads that Steps 1 through 4 are
implemented and validated while Step 5 remains pending. The writer refreshed it
without a reviewer having to return it, for the second consecutive step. The
opening `No, it is not implemented.` line correctly stays while Step 5 is open.

No row for any other step was touched, and no umbrella row was completed.

### Pre-repair mandatory checks and coverage for step 4 review-mode-docs round 1 (exchange 1)

No repair was made this round, so there is no pre-repair state to report and no
pre-repair blob was recorded. This is the first step in the effort that needed
no reviewer repair at all.

One pre-state was measured deliberately, because it had been repaired in each of
the three previous steps. For every staged file the ordinary
`git diff --cached --numstat` equals the `--ignore-cr-at-eol` numstat, and
`wiki/README.md` is now pure LF at zero CR. The standalone normalization commit
removed the collateral terminator churn at its root, exactly as intended, so no
line-ending repair was required here.

The writer reported 1,894 tests at 100% coverage with zero outliers before
publishing. That report was not inherited as this answer's evidence: the walk was
forced twice, and the first of those two runs reported one outlier and `exit=8`,
which is recorded in the resolved validation set rather than averaged away.

### Resolved validation set and sources for step 4 review-mode-docs round 1 (exchange 1)

The request supplied six commands and the current resolver produced the same
six, so the union is six and every one was run.

`ghog day`, sourced from the project, was run with `--force` rather than
accepting a freshness short-circuit. It did not pass cleanly.

The first forced walk reported `check` green, `affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=1 excluded=0 exit=8`. The
single outlier was
`test_activation_outside_git_fails_without_artifact_mutation` in the
review-exchange-recovery acceptance tests, measured at 0.55s against the 0.50s
suite floor, with ghog printing a duration warning requiring action.

The second forced walk reported `Objective reached` and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

Both results are recorded because the gate flapped rather than passed. ghog
states directly that a call only slightly above the floor will flap on the next
jitter and that re-measuring is not the correct response, so the green re-run is
reported as a second observation rather than as a resolution. The plan's Step 4
completion criterion asks for `ghog day` to report `exit=0`, and across this
round it reported `exit=8` once and `exit=0` once.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from the
plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

`rg -n disabled wiki/reference/independent-review-mode-contract.md` and
`rg -n fatal wiki/reference/independent-review-mode-contract.md`, both sourced
from the plan, matched their launcher-only rows and returned `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 4 review-mode-docs round 1 (exchange 1)

No resolver drift was observed.

The six commands in the request envelope and the six the current resolver
produces are identical in content and source attribution: `ghog day` from the
project, and the plan-sourced `rg -n disabled` and `rg -n fatal` checks against
the new reference, `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets and nothing was added or dropped when it was run.
The set grew from five commands to six relative to Step 3 because Step 4 names
two discovery checks rather than one, which is the expected per-step variation.

### Repository state around validation for step 4 review-mode-docs round 1 (exchange 1)

The request-time index tree was `3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the ordered thirteen-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. Two forced full walks therefore produced no tracked validation side effect
at all, and no reviewer repair exists to explain any difference. The only
difference is the ignored artifact `a.ghog.status`, which each walk rewrites by
design; a difference confined to an ignored validation artifact is acceptable,
and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is the protocol transcript for this exchange, which the shared core owns
and which correctly stays outside the reviewed index.

### Repair inventory for step 4 review-mode-docs round 1 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 review-mode-docs round 1 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the eleven staged paths with no omission and no
extra. Group 1, `publish the independent review contract`, lists ten paths: the
new central reference, all six inventory pages, the navigation page, the coverage
record, and the acceptance module. Group 2, `record Step 4 validation`, lists the
validation plan alone.

The ordering runs from least to most dependent. The reference, its inventory
links, and the acceptance evidence land first, and the validation verdict that
certifies them lands last, so the recorded verdict never precedes the work it
describes. That matches the grouping Steps 1 through 3 used, keeping the effort's
commit history consistent.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope.

This round staged nothing and made no repair, so file membership, grouping,
order, scope, and conventional subjects all still match the staged work exactly
as published.

No commit was run.

### Findings and boundaries for step 4 review-mode-docs round 1 (exchange 1)

Unresolved findings: None.

Boundary-crossing work:

- The mandatory `ghog day` gate is not reliably green, and the cause sits outside Step 4.
- The first forced walk in this round reported `fail=0`, `cov=100`, `outliers=1`, and `exit=8`.
- The outlier is `tests/unit/tools/test_review_exchange_recovery_acceptance/test_review_exchange_recovery_acceptance_tdd.py::test_activation_outside_git_fails_without_artifact_mutation` at 0.55s against the 0.50s suite floor, roughly ten percent over.
- A second forced walk reported `outliers=0` and `exit=0`, so the gate flapped rather than failed consistently.
- That flap is exactly what the tool predicts: ghog printed that a call only slightly above the floor will flap on the next jitter and that the response must not be to re-measure.
- Its documented remedies are to shorten the call below the floor with margin, following `instructions/fix_slow_test.md` and confirming with `ghog single` before `ghog day`, or, once that instruction proves the call irreducible, to accept it at its measured time with `ghog exclude <node id> <seconds>`.
- Raising the 0.50s floor is explicitly not an option the tool offers.
- This is not Step 4's work and Step 4 did not cause it: the flapping test belongs to review-exchange-recovery-acceptance under the completed review-exchange-core requirement, the floor is an absolute 0.50s rather than a median-derived figure, and the fast documentation tests this step adds cannot push an unrelated recovery call from below the floor to above it.
- The reviewer therefore reports it rather than shortening or excluding another requirement's test, which would exceed this step.
- It does need an owner before Step 5, because the same near-floor call will keep flapping on every future walk, and each flap makes the next step's readiness evidence a coin toss.
- Nothing else crossed a boundary: no production module, protocol artifact, launcher, template, adapter, umbrella row, or other plan step was touched, and this round staged nothing.

### Writer instructions for step 4 review-mode-docs round 1 (exchange 1)

Step 4's content needs no rework. The central reference is accurate against the
shipped code, the six inventory edits are genuinely subject-matched rather than
filled in mechanically, the coverage table records every disposition, and this is
the first step in the effort that required no reviewer repair at all. The
standalone LF normalization did what it was meant to: there is no collateral
terminator churn anywhere in this staged subject.

One thing needs an owner before this step can be recommended, and it is not a
change to your staged work.

The mandatory `ghog day` gate flapped. One forced walk reported `outliers=1` and
`exit=8` on
`test_activation_outside_git_fails_without_artifact_mutation` at 0.55s against
the 0.50s floor; the next forced walk reported `outliers=0` and `exit=0`. ghog
states that a call only slightly above the floor will flap on the next jitter and
that re-measuring is not the correct response, so a green re-run does not settle
it.

Take one of the two remedies ghog names, for that test rather than for your
pages. Either shorten the call below the floor with margin, following
`instructions/fix_slow_test.md` and confirming with `ghog single` on that file
before `ghog day`, or, once that instruction shows the call is irreducible, accept
it at its measured time with `ghog exclude <node id> <seconds>`. Do not raise the
0.50s floor, which ghog explicitly does not offer as an option.

That test belongs to review-exchange-recovery-acceptance under the completed
review-exchange-core requirement, so this reviewer reported it rather than
changing another requirement's test. Whoever owns that decision should make it
before Step 5, because the same near-floor call will keep flapping and each flap
makes the next step's readiness evidence a coin toss.

Publish another round once the gate is settled. Nothing else is requested: no
repair was made, no finding was left unaddressed in your content, `a.commit` is
accurate and needs no amendment, the umbrella digest is unchanged, and no tracked
validation side effect exists.

Do not treat this answer as commit authority.

### Decision rationale for step 4 review-mode-docs round 1 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is a mandatory
gate that does not pass reliably, not a defect in Step 4.

Five of the six readiness-floor results pass. Identity is exact, with the
envelope, human-readable request, `pw` plan, named step, positive round, and
request-time index tree all agreeing, and that tree matching the live index at
entry. The implementation is complete, and its contract tables were verified
against the shipped code: seventeen state rows, twenty-four outcomes with correct
source shapes, seven mandatory payload fields, six path keys, the correct exit
meanings, and an adapter matrix that records the absent Claude wrapper rather
than hiding it. Staged scope is attributable, with eleven in-step paths, no
reviewer repair, and `validation-state compare` returning `acceptable: true` with
no tracked difference. No finding remains in Step 4's own content. `a.commit` is
accurate in membership, grouping, order, scope, and conventional subjects.

The sixth result is mandatory validation, and it flapped. One forced `ghog day`
reported `outliers=1` and `exit=8`; the next reported `outliers=0` and `exit=0`.
The plan's own Step 4 completion criterion asks for `exit=0`, and this round
observed both.

The reason that blocks rather than passes is ghog's own instruction. The tool
printed that a call only slightly above the floor will flap on the next jitter
and that the response must not be to re-measure, then named two remedies:
shorten the call, or accept it explicitly with `ghog exclude`. Recommending
readiness on the strength of a green re-run would be precisely the response the
project's tooling tells the reader not to take, and this reviewer is not willing
to certify a gate as passing by selecting the run that agrees.

This differs from the transient failure recorded during Step 2, which was an
environment race in an atomic rename with no in-repository remedy and no
recurrence. The outlier here is a measured timing result against a declared
floor, it has a documented fix, and it will recur on every future walk until
someone applies one.

It is also not Step 4's work. The flapping test belongs to
review-exchange-recovery-acceptance under the completed review-exchange-core
requirement, the floor is an absolute 0.50s rather than a median-derived figure,
and the fast documentation tests this step adds cannot push an unrelated recovery
call over it. The remedy therefore sits outside this step and is reported as
boundary-crossing work rather than performed.

Step 4 itself is otherwise ready, and the round that follows a settled gate
should be a short confirmation rather than a rework round.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 4 review-mode-docs round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 2 by requestor - Step 4

- Recorded: 2026-08-21T09:44:45+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 4
Review round: 2

### Code review evidence for step 4 review-mode-docs round 2

request_index_tree: 36b31ed694fe9d0bd9fb09948561779a459d603d
resolved_validation_set:

- ghog day (sources: project)
- rg -n disabled wiki/reference/independent-review-mode-contract.md (sources: plan)
- rg -n fatal wiki/reference/independent-review-mode-contract.md (sources: plan)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)

### Requestor assessment for step 4 review-mode-docs round 2

Step 4 remains fully implemented. Its reference page, six focused inventory
updates, coverage record, wiki navigation, and four acceptance tests are
unchanged from round 1.

The round-1 finding is closed by a code change rather than a second measurement.
Profiling assigned the activation call almost entirely to one real Git process.
The real non-repository probe now runs in fixture setup, and the measured call
replays that captured result through `validate_activation` while asserting the
exact command, working directory, diagnostic, and absence of artifacts.

The next full walk found two more calls just above the same floor. Their real
Git export and answer-rendering journeys now run in fixture setup while their
output assertions remain in the measured calls. Focused timing put the answer
call at 0.05 seconds and both Git-backed assertion calls below the displayed
duration list.

The final Groundhog walk completed 1,894 tests with `fail=0`, `cov=100`,
`outliers=0`, `excluded=0`, and `exit=0`; its full phase took 3m09.9s. The
Step 4 acceptance package also passed its required focused command. Both Git
diff checks are clean, and the two reference greps still find the documented
`disabled` and `fatal` states.

### Implementation report for step 4 review-mode-docs round 2

The delivered Step 4 reference still derives all fifteen `ArtifactState`
members and separately records launcher-only `disabled` and fatal exit-2
`fatal`. It retains the exact twenty-four outcomes, seven mandatory result
fields, six returned path keys, operation ownership, human choices, and the
three-host adapter matrix.

The recovery acceptance test now captures Git's real non-repository response
during fixture setup and replays that response through the production
activation validator during the measured call. The dashboard test performs its
real missing-parent export in a prepared fixture, and the answer CLI test
performs its full retained-evidence render in a prepared fixture. Their test
bodies continue to assert the observable files, envelope, summary, manifest,
command contract, error, and absence of transient artifacts.

No duration exclusion was added and the project-wide 0.50-second floor was not
changed. The validation plan records the reviewer finding, both later outliers,
the fitting repair for each, and the final zero-outlier walk.

### Change summary for step 4 review-mode-docs round 2

The staged subject contains fourteen paths in three dependency-ordered groups.
Group 1 contains the three test files whose subprocess or file-IO journeys
crossed the duration floor under load, under
`test(groundhog): bound subprocess integration calls`.

Group 2 contains the ten Step 4 contract, inventory, navigation, coverage, and
acceptance paths under
`docs(review-mode-docs): publish review contract`. Group 3 contains only the
validation plan under
`docs(review-mode-docs): record step 4 validation`.

`a.commit` covers all fourteen staged paths exactly. Every Why section carries
the umbrella draft, focused draft, feature request, design, plan, and validation
plan as a two-paragraph narrative. The strict dry-run validator and staged
whitespace check both pass.

### Writer response for step 4 review-mode-docs round 2

Writer response: I accept the round-1 finding without qualification. A green rerun could not
close a measured duration outlier, so I profiled the activation call and changed
its test structure before the next walk. The real Git result remains part of
the journey; only process startup moved out of the measured call.

That next walk named two different borderline calls. I applied the same
profile-first rule to them rather than asking the reviewer to ignore load or
adding exclusions. The final full walk reports zero outliers, and the original
activation test no longer appears among the slow calls.

The Step 4 documentation subject itself did not change. I added the three test
paths as a separate leading commit group and refreshed the Step 4 performance
record so the review carries the complete repair trail.

### Reviewer focus for step 4 review-mode-docs round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-2 -->

## Round 2 by reviewer - Step 4

- Recorded: 2026-08-21T10:21:52+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 review-mode-docs round 2 (exchange 1)

Baseline index tree: 36b31ed694fe9d0bd9fb09948561779a459d603d

Assessed index tree: 36b31ed694fe9d0bd9fb09948561779a459d603d

### Implementation check for step 4 review-mode-docs round 2 (exchange 1)

Result: Yes. Step 4 has been fully implemented.

Step 4's documentation content is unchanged from the state assessed in round 1.
Comparing the round-1 request tree `3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c`
with this round's tree `36b31ed694fe9d0bd9fb09948561779a459d603d` shows
differences in only four files: the validation plan and the three test modules
redesigned in response to the round-1 gate finding. The central reference, the
six inventory pages, the navigation page, the coverage record, and the
review-mode acceptance module are byte-identical, so the round-1 assessment of
them still stands in full.

That assessment was that the reference records the shipped contract accurately:
seventeen state rows covering all fifteen `ArtifactState` members plus the
launcher-only `disabled` and `fatal` states, with the `fatal` row naming its null
identity, empty paths, null round, and `fatal-input` outcome; the twenty-four
outcome snapshot with correct source shapes; the seven mandatory payload fields
and six path keys exactly as the launcher builds them; the correct exit meanings;
and an adapter matrix that records the absent Claude shared wrapper rather than
hiding it. The six inventory candidates carry narrow subject-matched entries that
defer detail to the reference, and the coverage table records each as `Update`
with a concrete reason.

The three test redesigns are the substantive new work in this round, and each
preserves its behavioral assertion.

The recovery test hoists the real non-repository Git call into a fixture, asserts
there that the captured result is a genuine failure, and then replays that exact
captured result through a monkeypatched `_run_git` while asserting the command,
working directory, and absent input. The measured call still drives
`validate_activation` to the same `ReviewExchangeError` matching
`requires a Git repository`, and the replay assertions mean the test would fail
rather than silently pass if the production call shape changed.

The answer-CLI test moves the full render journey, including its
`answer_cli.main(...) == 0` assertion, into a fixture and keeps the envelope
round and summary-content assertions in the measured call. The dashboard test
moves the real export into a fixture and keeps the `is_file` assertion. No
assertion was dropped in any of the three.

The remedy is the one ghog names and the one this repository already uses. The
dashboard module's own docstring already described paying setup cost outside the
measured call for this same gate, and that file already contained a
`non_git_export_journey` fixture built for the same reason, so this follows an
established local pattern rather than inventing one. Each module docstring was
updated to say why the journey now sits in setup.

The staged set is fourteen paths. Ten are the Step 4 file list, one is the
validation plan as review metadata, and three are the out-of-step test modules
this reviewer identified in round 1 as needing an owner. Those three are isolated
in their own commit group rather than mixed into the documentation slice, which
is the correct structure and mirrors the standalone line-ending commit.

The document-level theme sentence reads that Steps 1 through 4 are implemented
and validated while Step 5 remains pending, with the opening
`No, it is not implemented.` line correctly unchanged.

The architecture assessment is clean. No production module changed, the test
changes move work between pytest phases without altering behavior, and no
existing feature or reporting capability is impaired.

Validation plan effects: Reviewer mode wrote no validation-plan row this round and made no repair
anywhere, so there is no reviewer-authored validation-plan difference.

The staged validation-plan difference is writer work that was assessed rather
than rewritten. The Step 4 verdict keeps the exact
`Yes. Step 4 has been fully implemented.` form followed by an empty line and a
prose summary, and its implemented inventory now records the seventeen-state
enumeration, the seven mandatory result fields, the new central reference, the
`fatal` row detail, and the six inventory updates. Those claims match what the
delivered pages actually contain.

The document-level theme sentence reads that Steps 1 through 4 are implemented
and validated while Step 5 remains pending. The writer refreshed it without a
reviewer having to return it, for the second consecutive step. The opening
`No, it is not implemented.` line correctly stays while Step 5 is open.

No row for any other step was touched, and no umbrella row was completed.

### Pre-repair mandatory checks and coverage for step 4 review-mode-docs round 2 (exchange 1)

No repair was made this round, so there is no pre-repair state to report and no
pre-repair blob was recorded. This is the second consecutive step needing no
reviewer repair, after three steps that each required one.

The evidence backing this answer was measured after the writer published, against
the exact staged state being recommended. `ghog day` was forced twice rather than
once, because the round-1 finding was about a flapping gate and one green run
could not settle it. Both runs reported `fail=0`, `cov=100`, `outliers=0`,
`excluded=0`, and `exit=0`.

The line-ending pre-state that had to be measured and repaired in Steps 1 through
3 is clean again: for every staged file the ordinary numstat equals the
`--ignore-cr-at-eol` numstat, so the standalone normalization continues to hold.

The writer's own reported walk agrees with these measurements and was not relied
upon in their place.

### Resolved validation set and sources for step 4 review-mode-docs round 2 (exchange 1)

The request supplied six commands and the current resolver produced the same
six, so the union is six and every one was run.

`ghog day`, sourced from the project, was run with `--force` twice rather than
once. A single green run would not have settled the round-1 finding, because the
gate had flapped there and ghog states directly that a near-floor call flaps on
jitter and must not be resolved by re-measuring. Confirming stability therefore
required more than one observation.

Both forced walks reported `check` green, `affected --no-cov` green,
`Objective reached`, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`.

The specific call that failed the gate in round 1,
`test_activation_outside_git_fails_without_artifact_mutation`, no longer appears
in any outlier or duration-warning list, and no exclusion was added and no floor
was raised to achieve that. The round-1 finding is resolved by the remedy ghog
prescribed rather than by an accepted variance.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from the
plan, reported `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

`rg -n disabled wiki/reference/independent-review-mode-contract.md` and
`rg -n fatal wiki/reference/independent-review-mode-contract.md`, both sourced
from the plan, matched their launcher-only rows and returned `exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

One honest qualification about what the redesign achieved. Hoisting a journey
into a fixture moves its cost from the measured call into setup rather than
removing it, so the suite's total wall clock is not reduced by these three
changes. That is the correct remedy nonetheless, because ghog's floor is defined
on call time and is aimed at slow assertions, and because this repository already
applies the same technique for the same gate. It is recorded here so nobody reads
the green result as the suite having become faster.

### Resolver drift and direction for step 4 review-mode-docs round 2 (exchange 1)

No resolver drift was observed.

The six commands in the round-2 request envelope and the six the current
resolver produces are identical in content and source attribution: `ghog day`
from the project, and the plan-sourced `rg -n disabled` and `rg -n fatal` checks,
`ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, and `git diff --cached --check`.

The union equals both sets, nothing was added or dropped when it was run, and the
set is unchanged from Step 4 round 1.

### Repository state around validation for step 4 review-mode-docs round 2 (exchange 1)

The request-time index tree was `36b31ed694fe9d0bd9fb09948561779a459d603d`, and
the index captured at reviewer entry matched it exactly, so no writer work
arrived between publication and assessment and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

Comparing the round-1 request tree `3edfcff0929037f7f6f92ea7aa14d4dbb8724f1c`
with this round's tree shows differences in exactly four files: the validation
plan and the three redesigned test modules. Step 4's documentation content is
byte-identical across the two rounds, so the round-1 assessment of the reference,
the six inventory pages, the navigation entry, and the coverage record carries
forward unchanged.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`, so no
umbrella boundary was crossed and no umbrella row was completed.

`validation-state compare` over the ordered sixteen-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. Two forced full walks produced no tracked validation side effect at all,
and no reviewer repair exists to explain any difference. The only difference is
the ignored artifact `a.ghog.status`, which each walk rewrites by design; a
difference confined to an ignored validation artifact is acceptable, and it was
neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is the protocol transcript for this exchange, which the shared core owns
and which correctly stays outside the reviewed index.

### Repair inventory for step 4 review-mode-docs round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 review-mode-docs round 2 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its three groups cover exactly the fourteen staged paths with no omission and no
extra: three, then ten, then one. Group 1,
`bound subprocess integration timing`, holds the three redesigned test modules.
Group 2, `publish the independent review contract`, holds the central reference,
all six inventory pages, the navigation page, the coverage record, and the
review-mode acceptance module. Group 3, `record Step 4 validation`, holds the
validation plan alone.

The three-group shape is the right response to this round's scope, and it is what
this reviewer would have asked for had it not already been done. The timing work
sits outside Step 4 and belongs in its own commit rather than mixed into a
documentation slice, exactly as the earlier line-ending normalization was kept
separate. A reader bisecting later sees one commit that changes test timing and a
separate commit that publishes the contract.

The ordering runs from least to most dependent. The timing work depends on
nothing in the effort, the documentation and its acceptance evidence follow, and
the validation verdict that certifies them lands last, so the recorded verdict
never precedes the work it describes.

All three subjects are well-formed conventional messages, and the two-paragraph
Why narratives state motivation before content.

This round staged nothing and made no repair, so file membership, grouping,
order, scope, and subjects all still match the staged work exactly as published.

No commit was run.

### Findings and boundaries for step 4 review-mode-docs round 2 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 review-mode-docs round 2 (exchange 1)

No changes are requested. Do not edit the staged subject in response to this
answer.

Present this recommendation to the human at the convergence gate together with
the identity summary, the staged changes, `a.commit`, and the requestor's own
assessment, and offer the registered choices `Commit` and
`Rework and review again`. This reviewer recommendation is advisory and
authorizes nothing on its own.

Present one point of context with it. This commit carries fourteen paths in three
groups, and the first group changes three test modules that belong to other
requirements. That is deliberate and was requested by the round-1 answer, but the
human choosing here should know the commit reaches beyond the documentation
slice, and that the timing work is isolated in its own group precisely so it can
be judged on its own terms.

If the human chooses `Commit`, run the existing commit step against `a.commit`
exactly as it stands. Its three groups already match the fourteen staged paths in
dependency order and need no amendment. Do not restage, regroup, or reword before
committing.

If the human chooses `Rework and review again`, treat their guidance as the scope
of the next round. Nothing in this review contributes work to such a round: no
repair was made, no finding was left unaddressed, and no command was missing.

One optional tidy-up, worth less than the round it would cost on its own. The
recovery test's `# noqa: SLF001` is redundant, because `SLF001` is already in the
per-file ignores for `tests/**/*.py`. Fold it into a later touch of that file
rather than reopening this step for it.

For Step 5, the two conditions that cost rounds earlier in this effort are now
both settled at their source: line endings are normalized and the duration gate
is stable across repeated walks. Step 5 should be able to run its validation
evidence once and publish.

### Decision rationale for step 4 review-mode-docs round 2 (exchange 1)

The disposition is `commit-ready`. All six readiness-floor results pass, and the
finding that blocked round 1 is resolved rather than worked around.

Identity is exact. The envelope, human-readable request, `pw` plan, named step,
positive round, and request-time index tree all agree, and that tree matched the
live index at entry.

The implementation is complete. Step 4's documentation content is byte-identical
to the state verified in round 1, where the reference's seventeen states,
twenty-four outcomes, seven payload fields, six path keys, exit meanings, and
adapter matrix were each checked against the shipped code.

Mandatory validation and coverage pass, and this time that claim rests on two
forced walks rather than one. Round 1 saw the gate flap, and ghog states that a
near-floor call flaps on jitter and must not be settled by re-measuring, so a
single green run would not have been honest evidence here. Both walks reported
`fail=0`, `cov=100`, `outliers=0`, and `exit=0`, and the call that failed round 1
appears in no outlier or warning list.

Staged scope is attributable. Fourteen paths: ten from the Step 4 file list, the
validation plan as review metadata, and three out-of-step test modules that this
reviewer identified in round 1 as needing an owner. Their presence is correct
rather than scope creep, because they are the remedy the round-1 answer asked
for and they are isolated in their own commit group instead of being mixed into
the documentation slice.

No unresolved finding remains, and the round-1 finding is closed the right way.
The three calls were shortened per the remedy ghog prescribes, with no exclusion
added and no floor raised. Each redesign keeps every behavioral assertion: the
recovery test still drives `validate_activation` to the same error and now also
asserts the replayed command, working directory, and absent input; the answer-CLI
test keeps its success assertion in setup and its envelope and summary assertions
in the call; the dashboard test keeps its real export and its file assertion.

`a.commit` is accurate across three groups in least-to-most-dependent order, with
well-formed subjects and two-paragraph Why narratives.

This round made no repair at all, so the rule that blocks a recommending round
does not apply.

Two observations are recorded rather than held against the step. Hoisting a
journey into a fixture moves cost from the measured call into setup rather than
removing it, so the suite's total wall clock is unchanged; that is still the
correct remedy, because ghog's floor is defined on call time and this repository
already used the technique for this gate. And the recovery test carries a
`# noqa: SLF001` that is redundant, since `SLF001` is already ignored for
`tests/**/*.py`; it is harmless and will not be flagged, because `RUF100` is
ignored there too.

This recommendation is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice belongs to the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 4 review-mode-docs round 2 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-2 -->

## Round 2 by human - Step 4 - human-confirmation

- Recorded: 2026-08-21T10:45:16+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 5

- Recorded: 2026-08-21T11:29:03+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 review-mode-docs round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 review-mode-docs round 1

request_index_tree: a93608e2bc97f4f3532ac82bb1ecaf55e215e541
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)
- rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: plan)
- rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: request)

### Requestor assessment for step 5 review-mode-docs round 1

Step 5 is fully implemented. The versioned table contains one complete row for
AC01 through AC12, exact page mappings for AC01 through AC09, evidence rows for
AC10 through AC12, and one final linked disposition for each of the six
inventory candidates. No pending or partial state remains.

Three final acceptance cases prove the criterion rows, inventory rows, and the
declared connected documentation set. They reject missing or duplicate table
keys, incomplete evidence, ignored helper or nonexistent launcher references,
broken links or paths, terminology and logo drift, and missing human choices.

The final Groundhog walk completed 1,897 tests with `fail=0`, `cov=100`,
`outliers=0`, `excluded=0`, and `exit=0`; its full phase took 3m09.1s. The
focused acceptance package passed 21 tests. Both Git whitespace checks return
no diagnostics, and the AC01 grep finds the final criterion row. Manual heading
review finds one H1 and seven unique H2 headings in the coverage document, with
MD024 and MD025 active.

The fixtures are 113 lines and the acceptance module is 499 lines, below their
200- and 500-line final advisories and the 650-line ceiling. The implementation
check records no architecture, performance, unit-coverage, or feature-integrity
issue. It marks all five steps implemented and completes umbrella row 6 with
the exact requirement and validation paths.

### Implementation report for step 5 review-mode-docs round 1

The coverage document now maps every page-owned criterion to exact Markdown
paths, records validation and scope evidence for the remaining criteria, and
preserves the executable evidence from Steps 1 through 4. Its Step 5 section
names the final tests and commands while keeping the Markdown checker and
read-only commit-plan command in later umbrella items.

`markdown_table_row` selects exactly one row by its first cell and rejects
missing or duplicate matches. The criterion test checks all twelve final
statuses, page mappings, command evidence, heading rules, and forbidden helper
or launcher references. A separate inventory test checks all six final linked
dispositions. The connected-set test resolves every declared page, local link,
and named path and retains the stable terminology, generic-logo boundary, and
both families' human choices.

The validation plan now begins `Yes, it is implemented.`, records the exact
Step 5 implementation and evidence, and keeps every earlier Yes verdict. The
umbrella changes only row 6 from pending to completed and adds its requirement
and validation paths; rows 7 and 8 remain pending.

### Change summary for step 5 review-mode-docs round 1

The staged subject contains five paths in two dependency-ordered groups. Group
1 contains the coverage document, bounded fixture helper, and acceptance module
under `docs(review-mode-docs): close acceptance coverage`.

Group 2 contains the validation plan and umbrella status transition under the
required `docs(review-mode-docs): record step 5 validation` subject. `a.commit`
covers every staged path exactly, and both Why sections narrate the umbrella
draft, focused draft, feature request, design, plan, and validation plan in two
paragraphs.

The strict commit-plan dry run passes. `git diff --check` and
`git diff --cached --check` are clean, and no protocol transcript is staged
before this first request publication.

### Writer response for step 5 review-mode-docs round 1

Writer response: This is the first Step 5 review round, so there is no earlier reviewer feedback
to accept or contest.

The tests-first run failed on the expected incomplete coverage rows and exposed
one over-broad terminology assertion, which was narrowed to the pages that own
the display-name distinction. The first full walk then stopped at static checks
on one literal boundary and an over-complex combined test. Naming the boundary
and separating criterion from inventory assertions closed both findings without
dropping behavior.

A later diff inspection found the criterion test still carried its pre-split
inventory name. The test and evidence citation were corrected, followed by a
fresh full walk. The request therefore presents the final names and the final
green evidence rather than the earlier passing tree.

### Reviewer focus for step 5 review-mode-docs round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-08-21T12:10:20+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 review-mode-docs round 1 (exchange 1)

Baseline index tree: a93608e2bc97f4f3532ac82bb1ecaf55e215e541

Assessed index tree: db54123933668d8be8d47fa48beb796b6c5f51f9

### Implementation check for step 5 review-mode-docs round 1 (exchange 1)

Result: Yes. Step 5 has been fully implemented.

Every file the step names exists and carries its final content. The coverage
record at `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` maps AC01 through
AC09 to exact pages, records AC10 through AC12 as validation, scope, and
coverage evidence, closes all six inventory dispositions against
`wiki/reference/independent-review-mode-contract.md`, and keeps every Step 1
through Step 4 evidence section. Three new acceptance cases and one new fixture
helper land in the two test files the step names, and the focused package is
green.

The load-bearing claims were checked against the repository rather than read for
plausibility. `rg -n "^#"` over the coverage record returns one `#` title and
seven distinct `##` headings, so the MD024 and MD025 claim in the AC10 row
holds. Each AC01 through AC09 row cites at least one backticked `.md` path, and
every cited page resolves. `wiki/README.md` lists the central reference inside
its `## 📖 Reference` section and keeps explanation, tutorials, how-to guides,
then reference in that order, so the AC09 row is accurate. The explanation page
links all three canonical instructions and the reference page carries the
three-host adapter matrix with the absent `.claude` wrapper, so the AC08 row is
accurate. Each of the six inventory pages contains a link to the central
reference, so every `Update` disposition is earned rather than asserted.

`markdown_table_row` is the only new helper. It selects one row by its first
cell and fails loudly on a missing or duplicated key, which is the right shape
for a table that must hold exactly one row per criterion and per candidate. It
opens no file of its own and adds no traversal beyond the declared set.

The line budgets hold. `conftest.py` is 113 lines against its 200-line final
advisory, and the acceptance module is 499 lines against its 500-line final
advisory and the 650-line ceiling. The module has one line of headroom, which
is the split trigger the plan already names rather than spare capacity: the next
assertion added to it crosses the advisory unless the category split happens
first.

Architecture, performance, and feature integrity are clean. No production
module, protocol operation, adapter, launcher, or runtime scan was added. Every
new assertion traverses a finite declared set of rows, pages, links, and paths
once, so the checks stay linear and no new `O(n^2)` or `O(n log n)` work
appears. No existing feature or reporting capability is impaired.

The per-class unit-coverage rule does not bind this slice, because it changes no
production class. The forced full walk reports `cov=100` with `outliers=0` and
`excluded=0` over 1,897 tests.

The verdict is Yes because the step's deliverables are complete, present, and
green. The findings this round returns are assertion-strength gaps inside those
delivered tests and one description that no longer matches them, not missing
files or missing content, so they are carried as unresolved findings rather than
recorded as missing implementation work.

Validation plan effects: Reviewer mode changed exactly one line of the validation plan, inside the rows
for the reviewed step.

The Step 5 unit-test-coverage row recorded that the repository-level acceptance
package passes 21 focused tests.
`ghog single tests/unit/tools/test_review_mode_docs_acceptance` reports
`100% (20/20)`, and the module defines twenty `test_` functions, so the figure
was wrong by one. The row now reads 20 focused tests. Nothing else in that row,
and nothing in any other row, changed.

Everything else in the staged validation-plan difference is writer work that was
assessed rather than rewritten. The Step 5 verdict sentence is the exact
`Yes. Step 5 has been fully implemented.` form, followed by an empty line and a
prose summary, as the template orders. The architecture, performance,
unit-test-coverage, and feature-integrity subsections each carry their required
closing sentence, and no `Missing work for Step 5` section is present or needed.

The document-level flip was the writer's to make and it is correct. Every one of
the five `### Analysis of Step N implementation state` sections now opens with
the exact `Yes. Step N has been fully implemented.` sentence, so the opening
line correctly reads `Yes, it is implemented.` and the theme sentence below it
no longer describes a pending step.

One writer-authored sentence is returned as a finding rather than edited here.
The Step 5 feature-integrity subsection states that the tests reject "ignored
helper references", which overstates what the two literal guards in the
acceptance module actually check. Correcting that sentence belongs with the test
change the matching finding asks for, so both land together in the writer's
round instead of being split across two owners.

Reviewer mode wrote no row for any other step, changed no document-level status
line, and completed no umbrella row. Umbrella row 6 stays exactly as the writer
staged it.

### Pre-repair mandatory checks and coverage for step 5 review-mode-docs round 1 (exchange 1)

One repair path was recorded before it was edited.
`record-pre-repair-blob docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`
returned object `3b5a1f627fb670e5b4f4d9ee0b6974d7715d98d2` with
`writer_deleted: false`, and that baseline went into the retained manifest
through `write-manifest` before any assessment mutated state.

The pre-repair mandatory checks ran against the writer's exact staged tree at
index `a93608e2bc97f4f3532ac82bb1ecaf55e215e541`.
`ghog single tests/unit/tools/test_review_mode_docs_acceptance` reported
`fail=0 warn=0 xfail=0 exit=0` over `20/20` tests.

`ghog day` was not accepted at its first result. It took the freshness
short-circuit, printing `No Python file changed since the last green ghog day
walk` and reporting `cov=skipped`, which is a re-use of the writer's own walk
rather than independent coverage evidence. It was therefore re-run with
`--force`. The forced walk reported `check` green, `affected --no-cov` green,
and `ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`
over 1,897 tests, with the full phase at 2m 54.1s.

The line-terminator pre-state was measured, because a CRLF collateral repair was
needed in three of the first four steps of this effort. For all five staged
paths the ordinary `git diff --cached --numstat` equals the
`--ignore-cr-at-eol` numstat, so this staged subject carries no terminator churn
and needed no line-ending repair. That is the second consecutive step with none.

The writer reported 1,897 tests at `cov=100` with `outliers=0` and `excluded=0`
before publishing, and the forced walk in this round reproduces those figures
exactly, so the writer's gate result is confirmed rather than inherited. The
focused-package total is the one reported figure that did not reproduce: the
request and the validation plan both said 21, and the package holds and runs
twenty. That single figure is the whole reason a repair was needed at all.

### Resolved validation set and sources for step 5 review-mode-docs round 1 (exchange 1)

The request supplied six commands and the current resolver produces the same
six, so the union is six and every one of them was run.

`ghog day`, sourced from the project, was run twice. The first call took the
freshness short-circuit and reported `cov=skipped`, which is not coverage
evidence, so it was re-run with `--force`. The forced walk reported
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests. The plan's Step 5 completion criterion asks for `exit=0`, and the
forced walk delivers it with real coverage behind it. No flap was observed: the
near-floor recovery call that made Step 4's gate flake now measures well under
the 0.50s floor, and the slowest reported call is 0.33s.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from the
plan, reported `fail=0 warn=0 xfail=0 exit=0` over `20/20` tests, both before and
after the reviewer repair.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`, both before and after the repair.

`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
plan, returned `exit=0` and matched three lines, the first of which is the final
AC01 criterion row at line 11, so the table it heads is the complete AC01
through AC12 record the criterion asks for.

`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
request, returned `exit=0` and eight heading lines: one `#` title and seven
distinct `##` headings. That is the executable half of the manual MD024 and
MD025 review the AC10 row claims, and it holds.

`rg` is not on this session's `PATH`. The ripgrep binary bundled with the host
was invoked by absolute path, so both `rg` commands genuinely executed and are
recorded as run rather than as unavailable evidence.

One non-mandatory check was added by the reviewer for corroboration only. The
repository's Markdown linter helper reported `TOTAL 0` over the coverage record,
the validation plan, the umbrella draft, and the live transcript, which agrees
with the heading grep and finds no MD022, MD024, MD025, MD031, MD032, or MD047
defect anywhere in this round's Markdown.

No mandatory command was unavailable, none was skipped, and none was recorded as
passing without being executed.

### Resolver drift and direction for step 5 review-mode-docs round 1 (exchange 1)

No resolver drift was observed.

The six commands in the request envelope and the six the current resolver
produces are identical in content and in source attribution: `ghog day` from the
project default; `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, `git diff --cached --check`, and
`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the plan's
Step 5 completion criteria and its shared execution checklist; and
`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the request.

The union equals both sets, and nothing was added or dropped when it was run.

The set holds at six commands, the same size as Step 4. The two Step 4 reference
greps were replaced by the two Step 5 coverage greps, which is the expected
per-step variation rather than drift, because each step names its own discovery
checks against the artifact it delivers.

### Repository state around validation for step 5 review-mode-docs round 1 (exchange 1)

The request-time index tree was `a93608e2bc97f4f3532ac82bb1ecaf55e215e541`, and
`capture-index-tree` at reviewer entry returned the same value, so no writer work
arrived between publication and assessment and the early rejection path did not
apply.

The assessed index tree is `db54123933668d8be8d47fa48beb796b6c5f51f9`. It
differs from the baseline for exactly one reason: this round staged one
attributable reviewer patch to the validation plan.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, with before and after both
`e9be8f8b3fa5ec11b489f836d0f97088948048edfeeb4b95eb47157204c1d0bb`, so no
umbrella boundary was crossed and reviewer mode completed no umbrella row.
Umbrella row 6 is staged as `completed` with its requirement and validation
paths by the writer, which is the writer's own final-step work under the
implementation-check contract; it was assessed and left untouched. Rows 7 and 8
remain `pending` with `-` in both evidence columns, so the deferred
`markdown-check` and `commit-plan-check` items are intact.

`validation-state compare` over the ordered seven-path set returned
`acceptable: false`, with tracked paths
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md` and `<index>`. Both
entries are this round's own permitted repair and the staging of it. The patch
was proven cleanly attributable through `attribute-reviewer-patch` before it was
staged, and it is confined to rows for the reviewed step, so the difference is
explained by reviewer metadata rather than by a validation side effect. The
other four staged paths are byte-identical before and after every mandatory
command, so no writer-caused tracked validation side effect exists and nothing
had to be left unstaged and unreverted on that account.

The only other difference is the ignored artifact `a.ghog.status`, which each
walk rewrites by design. A difference confined to an ignored validation artifact
is acceptable, and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is `docs/v0.11.0/review.code.v0.11.0.review-mode-docs.md`, the protocol
transcript for this exchange, which the shared core owns and which correctly
stays outside the reviewed index.

### Repair inventory for step 5 review-mode-docs round 1 (exchange 1)

Repairs made:

- Repair 1, review metadata, `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`: the Step 5 unit-test-coverage row read `21 focused tests` where `ghog single tests/unit/tools/test_review_mode_docs_acceptance` reports `100% (20/20)` and the module defines twenty `test_` functions, so the row now reads `20 focused tests`. Its pre-repair blob `3b5a1f627fb670e5b4f4d9ee0b6974d7715d98d2` was recorded before the edit, `attribute-reviewer-patch` returned `attributable: true` with a one-line patch before it was staged, and the change is confined to rows for the reviewed step, so it is review metadata rather than a substantive repair.

Paths staged:

- docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md

### Commit plan assessment for step 5 review-mode-docs round 1 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the five staged paths with no omission and no
extra. Group 1, `docs(review-mode-docs): close acceptance coverage`, lists the
coverage record, the fixture helper, and the acceptance module. Group 2,
`docs(review-mode-docs): record step 5 validation`, lists the umbrella draft and
the validation plan. The strict dry run over the live staged set returns those
two groups, all five paths, and an empty diagnostic list.

The ordering runs from least to most dependent. The evidence and the tests that
close it land first, and the validation verdict plus the umbrella status
transition that certify them land last, so the recorded verdict never precedes
the work it describes and the umbrella row never claims a validation plan that
is not yet committed. That matches the grouping Steps 1 through 4 used, keeping
the effort's commit history consistent.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and the final subject is the exact
`docs(review-mode-docs): record step 5 validation` line this step requires. Both
`Why` sections narrate the umbrella draft, the focused draft, the feature
request, the design, the plan, and the validation plan in two paragraphs, as the
grouping instruction asks.

The reviewer repair landed inside
`docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`, a path group 2
already covers, so membership, grouping, order, scope, and subjects still match
the staged work exactly and no amendment was required. The dry run was re-run
after the repair was staged and still returns an empty diagnostic list.

No commit was run.

### Findings and boundaries for step 5 review-mode-docs round 1 (exchange 1)

Unresolved findings:

- Finding 1, acceptance strength, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`: the plan's Step 5 tests-first list asks for an assertion that criteria 1 through 9 map to pages and 10 through 12 are evidence rows, and only the first half is implemented, because `test_step_5_coverage_finalizes_every_criterion` requires a backticked `.md` path in the AC01 through AC09 rows but never asserts that AC10 through AC12 are evidence rows rather than page mappings; the `Scope evidence` type of AC11 and the `Coverage evidence` type of AC12 are pinned nowhere in the suite, so rewriting AC11 as a `Page evidence` row that cites `wiki/reference/independent-review-mode-contract.md` leaves the whole package green while breaking the "evidence entries rather than page mappings" rule that AC12 itself states.
- Finding 2, acceptance strength, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`: the ignored-helper guard cannot fail, because `test_step_5_coverage_finalizes_every_criterion` asserts only that the strings `a.markdown` and `bin/markdown` are absent, while this repository's actual git-ignored helper is the root `a.reviewtool.py`, whose own docstring assigns its `mdlint` subcommand to umbrella row 7 and its `commit-plan` subcommand to row 8; a future coverage row citing `a.reviewtool.py mdlint` as the MD024 and MD025 evidence, or `a.reviewtool.py commit-plan` as commit-plan evidence, passes both guards unchanged and records an unshipped ignored helper as release evidence.
- Finding 3, record accuracy, `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`: the finalized record contradicts itself on pending state, because its Step 3 evidence bullet still says `test_step_3_coverage_records_task_and_recovery_evidence` pins completed AC04 and AC07 rows "while leaving the Step 4 reference boundary pending", although Step 5 rewrote that test's last assertion from a Pending AC10 row to a Complete AC10 row and the finalized table now holds no pending row at all; the Step 2 bullet carries the same stale "pending Step 3 boundary" wording, which went stale in Step 4 and is worth reconciling now that the record is being closed.
- Finding 4, record accuracy, `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`: the Step 5 feature-integrity subsection states that the tests reject "ignored helper references", which overstates the two literal guards named in finding 2; that sentence must either be earned by strengthening the guard or narrowed to what the assertions actually check.

Boundary-crossing work: None.

### Writer instructions for step 5 review-mode-docs round 1 (exchange 1)

Step 5's content is right. The coverage record closes every criterion and every
inventory disposition against exact pages, the three new acceptance cases are
well chosen, `markdown_table_row` is the correct shape for a one-row-per-key
table, the umbrella transition is the writer's own to make and is correct, the
document-level flip to `Yes, it is implemented.` is earned by five genuine Yes
verdicts, `a.commit` needs no amendment, and this is the second consecutive step
with no line-terminator churn. The forced full walk independently reproduces
1,897 tests at `cov=100` with `outliers=0`. Four things need your hand, and
three of them are in the same two files.

First, close the missing half of a tests-first bullet. The plan asks Step 5 to
assert that criteria 1 through 9 map to pages **and** that 10 through 12 are
evidence rows. `test_step_5_coverage_finalizes_every_criterion` asserts the
first half through the backticked `.md` check and asserts nothing about the
second. Pin the three evidence types the way the earlier steps pin theirs: add
row assertions for `| AC10 | Validation evidence |`, `| AC11 | Scope evidence |`,
and `| AC12 | Coverage evidence |`, and assert that no backticked `.md` path
appears in those three rows. That is the assertion which makes AC12's own
"evidence entries rather than page mappings" rule executable instead of
narrated.

Second, make the ignored-helper guard able to fail. The two literals it checks,
`a.markdown` and `bin/markdown`, are names nothing in this repository has ever
used. The helper the record could realistically cite is the root
`a.reviewtool.py`, which is git-ignored and whose own docstring routes `mdlint`
to umbrella row 7 and `commit-plan` to row 8. Assert that `a.reviewtool` does
not appear in the coverage record, and keep whichever launcher-shaped literal
you consider still worth guarding. Name the guarded strings in a module constant
rather than repeating them inline, so the next step can extend the list in one
place.

Third, reconcile the two stale evidence bullets. The Step 3 bullet says
`test_step_3_coverage_records_task_and_recovery_evidence` pins AC04 and AC07
"while leaving the Step 4 reference boundary pending", but Step 5 rewrote that
test's last assertion to a Complete AC10 row, and the finalized table now has no
pending row anywhere. The Step 2 bullet says the same about a "pending Step 3
boundary" and went stale back in Step 4. Retaining an earlier step's evidence
section does not require retaining a sentence that is no longer true of the test
it names: reword both to what those tests assert today. Note that your own
`assert "Pending" not in coverage` passes only because the stale wording is
lowercase, which is exactly the kind of accident worth removing from a record
that is meant to be auditable.

Fourth, correct one sentence in the validation plan. The Step 5 feature-integrity
subsection says the tests reject "ignored helper references". After the second
instruction above that claim is earned; before it, it is not. Update the
sentence in the same round as the test change so the record and the suite agree.

One repair was already made for you and is staged: the Step 5 unit-test-coverage
row said the acceptance package passes 21 focused tests, and it passes 20. That
is review metadata inside the reviewed step's rows, so it does not by itself
force another round. Please carry the corrected figure forward rather than
restoring 21, and update it again if your test additions change the count.

One thing to watch while you work: the acceptance module is at 499 lines against
a 500-line final advisory. The assertions above will cross it. The plan already
names the remedy at the 550-line risk band, so extract the category assertions
into a sibling TDD module now rather than recording a fresh advisory variance.

Publish another round once those four are addressed. Nothing else is requested:
the umbrella digest is unchanged, no tracked validation side effect exists, no
boundary was crossed, and `a.commit` is accurate.

Do not treat this answer as commit authority.

### Decision rationale for step 5 review-mode-docs round 1 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is that the
final acceptance slice does not yet prove one of the two rules it exists to
lock down.

Five of the six readiness-floor results pass. Identity is exact: the live
exchange context, the machine envelope, the human-readable request, the `pw`
plan, the declared step 5, the positive round 1, and the request-time index tree
all agree, the named step exists in the exact plan, and the request-time tree
matched the live index at entry. The implementation is complete, and its
load-bearing claims were checked against the repository rather than read for
plausibility: one title and seven distinct second-level headings in the coverage
record, a resolving page path in every AC01 through AC09 row, the central
reference listed inside the wiki's Reference section in the mandated category
order, all three canonical instructions linked from the explanation, the adapter
matrix carrying the absent `.claude` wrapper, and a link to the central contract
inside each of the six inventory pages. Mandatory validation and coverage pass:
all six resolved commands ran, `ghog day` was forced rather than accepted at its
freshness short-circuit, and the forced walk reported 1,897 tests at `cov=100`
with `outliers=0`, `excluded=0`, and `exit=0`. Staged attribution is clean: five
writer paths inside the step, one attributable reviewer patch, no writer-caused
tracked validation side effect, an unchanged umbrella digest, and no sweeping of
unstaged work into the index. `a.commit` is accurate in membership, grouping,
order, scope, and conventional subjects, including the exact required final
subject.

The sixth result is unresolved findings, and four remain.

The one that decides the round is the missing half of a tests-first bullet. The
plan asks Step 5 to assert both that criteria 1 through 9 map to pages and that
10 through 12 are evidence rows. The first half is asserted; the second is not
asserted anywhere in the suite. AC12 states in its own words that criteria 10
through 12 are recorded "as evidence entries rather than page mappings", and
today nothing fails if that stops being true. This is precisely the drift the
final slice exists to prevent, so recommending readiness on it would certify a
rule the tests do not check.

The second finding is of the same kind and reinforces it. A guard written as the
absence of `a.markdown` and `bin/markdown` cannot fail, because neither name
exists anywhere in this repository, while the git-ignored helper the record
could realistically cite is `a.reviewtool.py`. An assertion that cannot fail is
not evidence, and the validation plan's feature-integrity sentence about
rejecting "ignored helper references" currently rests on it, which is the fourth
finding.

The third finding is smaller but belongs to the same closing act. The finalized
record still tells the reader that one of its own tests leaves something
pending, in a table where nothing is pending, and it passes the writer's own
`Pending` guard only through a lowercase accident.

The implementation check records `Yes` rather than `No` deliberately, and that
choice is worth stating plainly. Every file the step names exists with its final
content, every acceptance case is written and green, and every gate passes, so
there is no missing deliverable and no work list for `implement-missing-step`.
What is missing is assertion strength inside delivered, passing tests and
accuracy in two sentences that describe them. That is a findings round, not an
incomplete step, and recording it as `No` would also leave the writer's correct
document-level `Yes, it is implemented.` line contradicted by a line reviewer
mode is not permitted to change.

One repair was made and staged, and it does not by itself block. The Step 5
unit-test-coverage row claimed 21 focused tests where the package holds and runs
twenty. That edit is confined to rows for the reviewed step, so it is review
metadata rather than a substantive repair, and this round would still have been
free to recommend readiness had the four findings not existed.

No boundary-crossing work is reported. Nothing outside Step 5 was touched, no
production module, protocol artifact, launcher, template, adapter, or other plan
step changed, and reviewer mode completed no umbrella row.

Step 5 is close. The four items are bounded, they sit in two files the step
already owns, and the round that follows should be a short confirmation rather
than a rework round.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 5 review-mode-docs round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-08-21T13:23:49+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 review-mode-docs round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 review-mode-docs round 2

request_index_tree: 0a59c1dc62e1673583b953617cd93364ba75ec24
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)
- rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: plan)
- rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: request)

### Requestor assessment for step 5 review-mode-docs round 2

Step 5 remains fully implemented, and all four round 1 findings are closed.

The final criterion test now pins AC10 as `Validation evidence`, AC11 as
`Scope evidence`, and AC12 as `Coverage evidence`, and rejects a backticked
Markdown page path in each of those rows. Its forbidden-reference set names
the real ignored `a.reviewtool` helper and the nonexistent `bin/mdlint`
launcher, so either reference now fails the package.

The Step 2 and Step 3 evidence descriptions now state the final table truth
without a stale pending boundary. The validation plan names the exact helper
and launcher checks and retains the reviewer correction from 21 to 20 focused
tests.

The three final Step 5 tests moved from the 499-line incremental module into a
157-line final-acceptance sibling. The incremental module is now 419 lines;
all 20 test functions and their assertions remain present across the pair.

### Implementation report for step 5 review-mode-docs round 2

Step 5 closes the versioned coverage record for AC01 through AC12 and all six
inventory candidates. The implementation keeps the bounded table-row helper
in `conftest.py`, the incremental Steps 1 through 4 checks in the original
module, and the final coverage, inventory, and connected-set responsibility in
the new final-acceptance sibling.

The evidence-row checks now prove both halves of the Step 5 tests-first rule:
AC01 through AC09 map to pages, while AC10 through AC12 carry their exact
non-page evidence types and no Markdown page path. The realistic forbidden
reference guard also backs the validation plan's feature-integrity statement.

The fresh full walk completed 1,897 tests with `fail=0`, `warn=0`, `xfail=0`,
`cov=100`, `outliers=0`, `excluded=0`, and `exit=0`; the full phase took
3m20.2s. The focused acceptance package then passed all 20 tests with `exit=0`.

### Change summary for step 5 review-mode-docs round 2

The staged subject contains seven paths in two dependency-ordered groups.

Group 1, `docs(review-mode-docs): close acceptance coverage`, contains the
final coverage record, the bounded fixture helper, the acceptance package
metadata, the 419-line incremental module, and the 157-line final-acceptance
sibling. It closes all four round 1 findings while preserving all 20 tests.

Group 2, `docs(review-mode-docs): record step 5 validation`, contains the
umbrella row transition and the validation record. It retains the reviewer
repair to 20 focused tests, records the category split, and names the exact
forbidden evidence references.

`a.commit` covers those seven paths exactly and validates without diagnostics.
The protocol transcript remains unstaged and outside the reviewed index.

### Writer response for step 5 review-mode-docs round 2

Writer response: Accepted all round 1 feedback without disagreement.

I retained the reviewer-authored correction from 21 to 20 focused tests. I
added exact evidence-type and no-page-path assertions for AC10 through AC12,
replaced the inert helper literals with a shared forbidden-reference set for
`a.reviewtool` and `bin/mdlint`, and rewrote both stale pending-boundary
sentences to describe the finalized evidence table.

Because those assertions crossed the module's 500-line advisory, I applied the
planned category split. Steps 1 through 4 remain in the 419-line incremental
module, while the three Step 5 tests and their category helpers live in the
157-line final-acceptance sibling. The package still contains 20 tests.

The validation plan now records those measured sizes and the exact helper and
launcher guards. A fresh full walk is green over 1,897 tests at 100% coverage
with zero duration outliers, and the focused package passes 20 of 20 tests.
Both Git whitespace checks pass, and the seven-path two-group commit plan is
clean.

### Reviewer focus for step 5 review-mode-docs round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-08-21T17:47:42+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: answer

### Exact disagreement for step 5 review-mode-docs round 2 (exchange 1)

The mandatory request-time index tree does not match the live index, and the
reviewed subject is empty.

The round 2 request records
`request_index_tree: 0a59c1dc62e1673583b953617cd93364ba75ec24`.
`capture-index-tree` at reviewer entry returns
`07525a824ecb2e4a5a8bf946875cdcbe0e5c8f5d`. The two disagree, so the request no
longer describes the state a reviewer would assess.

The live index is empty relative to `HEAD`: `git diff --cached --name-status
HEAD` returns nothing at all. The seven paths named by the change summary are
present in the working tree and not one of them is staged. Six are unstaged
modifications, and the new 157-line final-acceptance sibling
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
is untracked, so it is not even a tracked file yet. There is no staged diff to
review.

`HEAD` also moved after the request was published. It stood at `cb2e7a6` for
Step 4 completion and now stands at `6e9f939`, through
`5e9b523 test(perf): shorten repository acceptance` and
`6e9f939 perf(test): remove duplicate coverage reports`. Neither commit contains
a review-mode-docs path: `git log cb2e7a6..HEAD --name-only` names shared test
doubles, report-acceptance and code-reviewer-acceptance fixtures,
`tests/unit/tools/test_prompt_workflow_integration.py`, and `pyproject.toml`.
The Step 5 work was therefore not swept into either commit, but it left the
index while they were made.

`a.commit` is gone as well. The request states that it covers the seven staged
paths exactly and validates without diagnostics. The live file is zero bytes,
so the commit plan the request describes no longer exists either.

This is an identity failure, not a judgement on the round 2 content. The
reviewer made no implementation, validation-plan, umbrella, staged, or
`a.commit` mutation, captured no assessment evidence, wrote no retained
manifest, and did not sweep the unstaged or untracked writer work into the
index. Nothing in the round 2 rework is contested here: the working tree still
carries the 113-line `conftest.py`, the 419-line incremental module, and the
157-line final-acceptance sibling the request describes. That content was
deliberately left unassessed, because the request's subject is the index and the
index no longer holds it.

### Writer instructions for step 5 review-mode-docs round 2 (exchange 1)

Restore the staged subject and publish a replacement round. None of your Step 5
content is being questioned here, and no rework of the pages, the record, or the
tests is being asked for.

Re-stage the exact seven paths the round 2 change summary names. The
final-acceptance sibling is untracked, so it needs an explicit add rather than
an update of an already-tracked path:

- `docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`
- `docs/v0.11.0/draft.v0.11.0.review-mode.md`
- `docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`
- `tests/unit/tools/test_review_mode_docs_acceptance/__init__.py`
- `tests/unit/tools/test_review_mode_docs_acceptance/conftest.py`
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`
- `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`

Leave `docs/v0.11.0/review.code.v0.11.0.review-mode-docs.md` unstaged. It is the
protocol transcript for this exchange and belongs outside the reviewed index.

Rebuild `a.commit`, which is now a zero-byte file. Write the two-group plan
again: group 1, `docs(review-mode-docs): close acceptance coverage`, over the
coverage record, the package metadata, the fixture helper, and both test
modules; group 2, `docs(review-mode-docs): record step 5 validation`, over the
umbrella draft and the validation plan. Keep the final subject exactly
`docs(review-mode-docs): record step 5 validation`, and keep the dependency
order so the validation verdict and the umbrella transition land after the
evidence they certify.

Re-run the gate against the restored index rather than carrying the earlier
result forward. `HEAD` moved by two commits since your walk, and one of them
edits coverage reporting in `pyproject.toml`, so the previous figures were
measured against a different tree. Run `ghog day` until it reports `exit=0`,
then `ghog single tests/unit/tools/test_review_mode_docs_acceptance`, then
`git diff --check` and `git diff --cached --check` after staging.

Capture the new index tree last, and publish a replacement request whose
`request_index_tree` is that value. Do not reuse
`0a59c1dc62e1673583b953617cd93364ba75ec24`; it names a tree that no longer
exists as the index.

One thing worth checking before you republish: the Step 5 work was unstaged
rather than committed while `5e9b523` and `6e9f939` were made, and `a.commit`
was emptied at the same time. If that came from a stash taken and popped without
`--index`, re-adding the seven paths is the whole repair, which is what the list
above does. Confirm that no other in-flight staged work was dropped the same
way, because nothing in this round's evidence would have surfaced it.

Do not treat this answer as commit authority.

### Final reviewer decision for step 5 review-mode-docs round 2 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 3 by requestor - Step 5

- Recorded: 2026-08-21T18:36:48+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 review-mode-docs round 3

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 5
Review round: 3

### Code review evidence for step 5 review-mode-docs round 3

request_index_tree: 4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39
resolved_validation_set:

- ghog day --force (sources: project)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)
- rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: plan)
- rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: request)

### Requestor assessment for step 5 review-mode-docs round 3

Step 5 remains fully implemented, and the four substantive findings from round
1 remain closed in the restored seven-path subject.

Round 2 stopped at request-time index identity and did not assess content. The
requestor restored the same seven Step 5 paths after the two performance
commits, rebuilt the two-group commit plan, and captured a new index tree.

The final criterion test pins the exact non-page evidence types for AC10
through AC12, rejects Markdown page paths in those rows, and names the actual
ignored helper and nonexistent launcher. The Step 2 and Step 3 evidence text
now describes the final table, and the 20 tests remain split across 419- and
157-line modules.

### Implementation report for step 5 review-mode-docs round 3

Step 5 closes the versioned coverage record for AC01 through AC12 and all six
inventory candidates. The bounded row helper remains in `conftest.py`, the
incremental Steps 1 through 4 checks remain in the original module, and the
final coverage, inventory, and connected-set checks remain in their sibling.

The forced walk on top of `6e9f939` completed 1,897 tests with `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`; its
full phase took 1m49.1s. The focused package then passed 20 of 20 tests. Both
Git whitespace checks and both bounded coverage-document searches pass.

### Change summary for step 5 review-mode-docs round 3

The staged subject contains exactly seven paths in two dependency-ordered
groups. No performance path or durable review transcript is staged.

Group 1, `docs(review-mode-docs): close acceptance coverage`, contains the
final coverage record, package metadata, bounded fixture helper, incremental
acceptance module, and final-acceptance sibling.

Group 2, `docs(review-mode-docs): record step 5 validation`, contains the
umbrella row transition and validation record. The final subject is unchanged,
and the obsolete pre-performance duration was removed from the record.

`a.commit` lists all seven paths once, preserves dependency order, and parses
without diagnostics. Its Why narratives cite the umbrella, topic draft,
feature request, design, implementation plan, and validation plan.

### Writer response for step 5 review-mode-docs round 3

Writer response: Accepted the round 2 identity finding without disagreement.

I reclaimed and consumed the intact expired answer, restored the seven Step 5
paths to the index, left the durable transcript unstaged, and rebuilt the two
commit groups. The two performance commits remain intact, and `git status`
shows no missing work beyond the expected Step 5 subject and transcript.

I replaced the obsolete pre-performance duration sentence in the validation
record, then forced a fresh walk against the final staged subject. The full
phase took 1m49.1s with 100% coverage and no outliers; the focused package
passed all 20 tests. Both Git whitespace checks pass.

The new request uses index tree
`4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39`. Round 2's
`0a59c1dc62e1673583b953617cd93364ba75ec24` baseline is not reused.

### Reviewer focus for step 5 review-mode-docs round 3

Check the exact plan step, restored staged subject, final validation evidence,
round 1 finding closures, and `a.commit` accuracy. Round 2 made no content
assessment.

<!-- review-entry-id: request-step-5-round-3 -->

## Round 3 by reviewer - Step 5

- Recorded: 2026-08-21T19:01:48+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 review-mode-docs round 3 (exchange 1)

Baseline index tree: 4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39

Assessed index tree: 4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39

### Implementation check for step 5 review-mode-docs round 3 (exchange 1)

Result: Yes. Step 5 has been fully implemented.

All four round 1 findings are closed, and each was checked against the code
rather than accepted from the writer response.

The evidence-row half of the tests-first rule is now real.
`_assert_evidence_criterion_rows` walks the `_EVIDENCE_CRITERION_TYPES` mapping
and requires `| Validation evidence |` on AC10, `| Scope evidence |` on AC11,
and `| Coverage evidence |` on AC12, then asserts that no backticked Markdown
path appears in any of those three rows. That is the assertion that makes
AC12's own "evidence entries rather than page mappings" rule executable, and it
fails today if any of the three is rewritten as a page mapping.

The forbidden-reference guard can now fail.
`_FORBIDDEN_EVIDENCE_REFERENCES` names `a.reviewtool`, which is this
repository's actual git-ignored helper, and `bin/mdlint`, a launcher-shaped
name for the deferred umbrella row 7. Both are checked against the whole
coverage record through a named module constant, so extending the set is a
one-line change rather than another inline literal.

Both stale evidence sentences are gone. The Step 2 bullet now reads that the
test pins the AC03 row and both tutorial paths retained in the final table, and
the Step 3 bullet that it pins AC04, AC07, and their guide evidence retained in
the final table. Neither claims a pending boundary, and the finalized record
holds no pending or partial row anywhere.

The validation plan's feature-integrity sentence is earned rather than
asserted: it now names the `a.reviewtool` helper reference and the nonexistent
`bin/mdlint` launcher reference explicitly, matching what the guard checks. The
reviewer correction from 21 to 20 focused tests was carried forward, and the
obsolete pre-performance duration sentence was removed rather than restated.

The category split preserves behavior exactly. The package holds twenty test
functions, seventeen in the 419-line incremental module and three in the new
157-line final-acceptance sibling, and `ghog single` reports `100% (20/20)`.
`conftest.py` is 113 lines against its 200-line advisory; both test modules sit
below the 500-line final advisory and the 650-line ceiling, so the advisory the
round 1 answer flagged at 499 lines is no longer under pressure.

The staged subject grew from five paths to seven for two reasons that both stay
inside the step. The new sibling module is the remedy the plan's own Step 5
split guidance names, and `__init__.py` carries a one-line docstring update that
describes the package now holding both kinds of module. Neither introduces a
design decision or touches another step.

Architecture, performance, and feature integrity are clean. No production
module, protocol operation, adapter, launcher, or runtime scan was added. Every
assertion traverses a finite declared set of rows, pages, links, and paths once,
so validation stays linear with no new `O(n^2)` or `O(n log n)` work, and no
existing feature or reporting capability is impaired. The per-class unit
coverage rule does not bind a slice that changes no production class, and the
forced walk reports `cov=100` with `outliers=0` and `excluded=0` over 1,897
tests.

One reuse defect and one protocol defect remain, and neither is a missing
deliverable, so the verdict stays Yes and both are carried as unresolved
findings. The reuse defect is that the split left roughly sixteen page-path
literals and one assertion helper duplicated verbatim across the two modules
while the package's shared `conftest.py` sits at 113 lines with room for them.
The protocol defect is that this round's request content was not produced by
`bin/code_review_request.bat`, which the requestor instruction requires.

Validation plan effects: Reviewer mode wrote no validation-plan row this round and made no repair
anywhere, so there is no reviewer-authored validation-plan difference. This is
the first round on Step 5 that needed none.

The whole staged validation-plan difference is writer work that was assessed
rather than rewritten, and every measurable claim in the Step 5 rows was checked
against the repository.

The verdict sentence is the exact `Yes. Step 5 has been fully implemented.`
form, followed by an empty line and a prose summary, as the template orders. No
`Missing work for Step 5` section is present, and none is needed.

The architecture row records `conftest.py` at 113 lines, the incremental module
at 419, and the final-acceptance sibling at 157. All three match the files. The
unit-coverage row records 20 focused tests, which is the reviewer correction
from round 1 carried forward correctly and which `ghog single` confirms as
`100% (20/20)`. The performance row records 1,897 tests at `cov=100` with
`outliers=0`, `excluded=0`, and `exit=0`, which the forced walk in this round
reproduces exactly. The feature-integrity row now names `a.reviewtool` and
`bin/mdlint` as the rejected references, which is what the guard actually
checks, so the sentence round 1 returned as overstated is now accurate.

The obsolete pre-performance duration sentence was removed rather than
refreshed. That is the right call: the figure it carried was measured against a
tree two commits behind, and the row's remaining claims are the ones that
matter.

The document-level flip was the writer's to make and it is correct. All five
`### Analysis of Step N implementation state` sections open with the exact
`Yes. Step N has been fully implemented.` sentence, so the opening
`Yes, it is implemented.` line and its theme sentence are both earned.

Reviewer mode wrote no row for any step, changed no document-level status line,
and completed no umbrella row. Umbrella row 6 stays exactly as the writer staged
it, and rows 7 and 8 stay `pending` with `-` in both evidence columns.

### Pre-repair mandatory checks and coverage for step 5 review-mode-docs round 3 (exchange 1)

No repair was made this round, so there is no pre-repair state to report. One
pre-repair blob was recorded defensively before assessment began, because the
reviewed-step validation rows are the one path reviewer mode may write:
`record-pre-repair-blob docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`
returned object `e455b8231030c514a537400ca180507b963f3a41` with
`writer_deleted: false`, and it went into the retained manifest through
`write-manifest` before any command ran. It was never used, because every
measurable claim in those rows checked out.

The mandatory checks ran against the writer's exact staged tree at index
`4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39`, which is the tree the request
names.

`ghog day --force` reported `check` green, `affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests. The slowest reported call is 0.37s against the 0.50s floor, so the
near-floor flap that blocked Step 4 round 1 stays resolved.
`ghog single tests/unit/tools/test_review_mode_docs_acceptance` reported
`100% (20/20)` with `fail=0`, `warn=0`, `xfail=0`, and `exit=0`.

The line-terminator pre-state was measured again, because a CRLF collateral
repair was needed in three of the first four steps of this effort. For all seven
staged paths the ordinary `git diff --cached --numstat` equals the
`--ignore-cr-at-eol` numstat, so this staged subject carries no terminator churn
and needed no line-ending repair. That is the third consecutive step with none.

Every reported figure in the request reproduced. The walk total, coverage,
outlier count, and exit code match; the focused package holds and runs twenty
tests as the record now states; and the three module sizes match the files. The
one figure that could not be reproduced is a wall-clock duration, and it was not
treated as evidence: the request reports a 1m49.1s full phase and this round
measured 1m52.9s. Timing variation between two walks of the same tree is not a
defect, and the human has closed the execution-time question, so it is recorded
here and raised nowhere else.

### Resolved validation set and sources for step 5 review-mode-docs round 3 (exchange 1)

The request supplied six commands and the current resolver produces six, but
they are not the same six. The union is seven, and all seven were run.

`ghog day --force`, which the request attributes to the project source,
reported `check` green, `affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests, with the full phase at 1m52.9s.

`ghog day`, the command the current resolver actually emits for the project
source, was run separately rather than treated as covered by the forced walk.
It reported the freshness short-circuit `No Python file changed since the last
green ghog day walk` with `cov=skipped` and `exit=0`. On its own that is not
coverage evidence, which is exactly why the forced walk above was run first and
is the result this answer relies on.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `100% (20/20)` with `fail=0`, `warn=0`, `xfail=0`, and
`exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
plan, returned `exit=0` and matched three lines, the first being the final AC01
criterion row at line 11, so the table it heads is the complete AC01 through
AC12 record.

`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
request, returned `exit=0` and eight heading lines: one `#` title and seven
distinct `##` headings.

`rg` is not on this session's `PATH`; the ripgrep binary bundled with the host
was invoked by absolute path, so both searches genuinely executed.

One non-mandatory corroboration was added. The repository's Markdown linter
helper reported `TOTAL 0` over the coverage record, the validation plan, the
umbrella draft, and the live transcript, which agrees with the heading grep and
finds no MD022, MD024, MD025, MD031, MD032, or MD047 defect in this round's
Markdown.

No mandatory command was unavailable, none was skipped, and none was recorded
as passing without being executed.

### Resolver drift and direction for step 5 review-mode-docs round 3 (exchange 1)

Resolver drift was observed, and its direction is that the request replaced the
mandatory project default instead of adding to it.

The request's set names `ghog day --force` with `sources: ["project"]` and
contains no plain `ghog day` entry at all. The current resolver cannot produce
that set. `tools/code_review_validation.py` defines
`DEFAULT_PROJECT_VALIDATION_COMMANDS` as the single value `ghog day`, and
`tools/code_review_request.py` passes that constant straight into
`resolve_code_review_validation` as the project defaults with no configuration
seam, so a `project`-sourced command can only ever be `ghog day`. A stricter
variant supplied through `--plan-validation-command` or
`--request-validation-command` would carry the `plan` or `request` source and
would sit beside the project default rather than replace it.

`instructions/code-review-requestor.md` states the same rule in words: an
addition "may share a command with another source, but it cannot remove the
`ghog day` project default".

The direction therefore is a removal disguised as a stronger check, not an
addition. The forced walk is genuinely stricter than the default and this
reviewer would have run it regardless, so no evidence was lost, but the recorded
set understates the mandatory floor by dropping the one command the project
requires unconditionally.

The other five commands agree exactly with the current resolver in content and
source attribution: `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, `git diff --cached --check`, and
`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the plan's
Step 5 completion criteria and shared execution checklist, and
`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the request.

The union of the request set and the current resolver set is seven commands,
and every one of the seven was run. The drift is reported rather than silently
normalized, and the cause is recorded as an unresolved finding, because a
`project` source the shipped resolver cannot emit means the block was not
rendered by the launcher.

### Repository state around validation for step 5 review-mode-docs round 3 (exchange 1)

The request-time index tree is `4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39`, and
`capture-index-tree` at reviewer entry returned the same value, so the identity
failure that stopped round 2 is repaired and the early rejection path did not
apply. The assessed index tree is the same value, because this round staged
nothing.

The restoration was verified rather than assumed. `HEAD` is `6e9f939`, so both
performance commits are intact and neither was reverted to make the tree match.
The seven Step 5 paths are staged, with
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`
correctly staged as an addition rather than left untracked, and `a.commit` is a
rebuilt non-empty plan rather than the zero-byte file round 2 found. Round 2's
`0a59c1dc62e1673583b953617cd93364ba75ec24` was not reused, which is right: that
tree was built on `cb2e7a6` and is unreachable without reverting the two
performance commits.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, with before and after both
`e9be8f8b3fa5ec11b489f836d0f97088948048edfeeb4b95eb47157204c1d0bb`, so no
umbrella boundary was crossed and reviewer mode completed no umbrella row.
Umbrella row 6 is staged as `completed` with its requirement and validation
paths by the writer, which is the writer's own final-step work; rows 7 and 8
remain `pending`.

`validation-state compare` over the ordered nine-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. A forced full walk, a plain walk, and a focused run therefore produced no
tracked validation side effect at all, and no reviewer repair exists to explain
any difference. This is the cleanest boundary result of the five rounds this
effort has run.

The only difference is the ignored artifact `a.ghog.status`, which each walk
rewrites by design. A difference confined to an ignored validation artifact is
acceptable, and it was neither staged nor reverted.

The working tree holds no unstaged or untracked writer work. Its only unstaged
entry is `docs/v0.11.0/review.code.v0.11.0.review-mode-docs.md`, the protocol
transcript for this exchange, which the shared core owns and which correctly
stays outside the reviewed index.

### Repair inventory for step 5 review-mode-docs round 3 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 review-mode-docs round 3 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the seven staged paths with no omission and no
extra, which matters this round because the file was rebuilt from nothing after
round 2 found it emptied. The strict dry run over the live staged set returns
two groups, all seven paths, and an empty diagnostic list.

Group 1, `docs(review-mode-docs): close acceptance coverage`, lists the coverage
record, the package `__init__.py`, the fixture helper, the incremental
acceptance module, and the new final-acceptance sibling. Group 2,
`docs(review-mode-docs): record step 5 validation`, lists the umbrella draft and
the validation plan.

The ordering runs from least to most dependent. The evidence and the tests that
close it land first, and the validation verdict plus the umbrella status
transition that certify them land last, so the recorded verdict never precedes
the work it describes and the umbrella row never claims a validation plan that
is not yet committed. That matches the grouping Steps 1 through 4 used.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and the final subject is the exact
`docs(review-mode-docs): record step 5 validation` line this step requires. Both
`Why` sections narrate the umbrella draft, the topic draft, the feature request,
the design, the implementation plan, and the validation plan.

The rebuild is faithful to what round 2 described, extended correctly for the
two paths the split added, and no performance path from `5e9b523` or `6e9f939`
leaked into either group.

This round staged nothing and made no repair, so file membership, grouping,
order, scope, and conventional subjects all still match the staged work exactly
as published. No commit was run.

### Findings and boundaries for step 5 review-mode-docs round 3 (exchange 1)

Unresolved findings:

- Finding 1, protocol evidence, `a.review-requested.code.v0.11.0.review-mode-docs.md`: this round's request content was not produced by `bin/code_review_request.bat`, which `instructions/code-review-requestor.md` requires and which says never to edit either rendering independently, and three independent tells prove it. Its `resolved_validation_set` attributes `ghog day --force` to the `project` source and contains no plain `ghog day` entry, which the shipped resolver cannot emit because `tools/code_review_validation.py` hard-codes `DEFAULT_PROJECT_VALIDATION_COMMANDS` as `ghog day` and `tools/code_review_request.py` passes that constant straight through with no configuration seam, so the mandatory project default was removed rather than added to. Its evidence JSON uses compact arrays such as `"sources": ["project"]`, while the renderer emits `json.dumps(payload, indent=2, sort_keys=True)`, which always expands them, and rounds 1 and 2 of this same exchange show the expanded form. Three passages that are fixed text in `templates/code-review-request.template.md` are paraphrased, including the reviewer scope sentence, the `a.commit` amendment sentence, and the loss of the word "validly" from the substantive-repair rule, so the durable transcript now records reviewer obligations that differ from the shipped contract for the final step of the effort that ships this protocol.
- Finding 2, reuse, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`: the category split copied roughly sixteen page-path literals and one assertion helper verbatim into the new sibling instead of hoisting them, so `_EXPLANATION`, `_SELF_REVIEW_EXPLANATION`, `_SELF_REVIEW_HOW_TO`, `_COVERAGE`, `_SPEC_TUTORIAL`, `_CODE_TUTORIAL`, `_HOW_TO_GUIDES`, `_REFERENCE`, `_INVENTORY_CANDIDATES`, and `_assert_contains` now exist twice while the package's shared `conftest.py` sits at 113 lines against a 200-line advisory and already exports the helpers both modules import; the concrete drift is silent rather than loud, because adding a seventh inventory candidate to the sibling's tuple alone leaves `test_step_1_coverage_keeps_complete_enumerations_and_evidence` enumerating six and still passing, so the Step 1 completeness guarantee narrows without any test failing.

Boundary-crossing work: None.

### Writer instructions for step 5 review-mode-docs round 3 (exchange 1)

Step 5's implementation is finished. All four round 1 findings are genuinely
closed, and each was verified against the code rather than accepted from your
response: AC10 through AC12 now carry real evidence-type and no-page-path
assertions, the forbidden-reference guard names the actual `a.reviewtool` helper
through a module constant, both stale pending sentences are rewritten, and the
feature-integrity claim is earned. The split preserves all twenty tests, the
restoration after the performance commits is faithful, `a.commit` was rebuilt
correctly for seven paths, the umbrella digest is unchanged, and
`validation-state compare` returned `acceptable: true` with nothing tracked or
untracked. Two things stand between this and a readiness recommendation, and
only one of them is in your files.

First, the one in your files: hoist the shared constants. The split copied
`_EXPLANATION`, `_SELF_REVIEW_EXPLANATION`, `_SELF_REVIEW_HOW_TO`, `_COVERAGE`,
`_SPEC_TUTORIAL`, `_CODE_TUTORIAL`, `_HOW_TO_GUIDES`, `_REFERENCE`,
`_INVENTORY_CANDIDATES`, and `_assert_contains` into the sibling verbatim, so
roughly sixteen page paths now live in two places. Move them into `conftest.py`,
which both modules already import from and which has 87 lines of headroom, and
import them in both. The reason is not tidiness: add a seventh inventory
candidate to the sibling's tuple alone and
`test_step_1_coverage_keeps_complete_enumerations_and_evidence` keeps
enumerating six and keeps passing, so the Step 1 completeness guarantee narrows
with nothing turning red. This one follows from the split the round 1 answer
asked for, so treat it as finishing that instruction rather than as new work.

Second, and this one belongs to the requestor role rather than to the pages:
re-render the request through `bin/code_review_request.bat` and publish that.
The round 3 request content was not launcher output. Its
`resolved_validation_set` attributes `ghog day --force` to the `project` source
and drops plain `ghog day` entirely, which the shipped resolver cannot produce,
because `DEFAULT_PROJECT_VALIDATION_COMMANDS` is the single value `ghog day` and
`code_review_request.py` passes it through with no configuration seam. The
requestor instruction says an addition "cannot remove the `ghog day` project
default". Its evidence JSON also uses compact arrays where the renderer emits
`indent=2`, and three template-fixed passages are paraphrased, including the
loss of "validly" from the substantive-repair rule.

The fix is mechanical. Pass the forced walk as an addition rather than a
substitution: `--request-validation-command "ghog day --force"` keeps your
stricter check and keeps `ghog day` where the project put it. Let the launcher
write the whole request body and pass it unedited to `publish-request`. Do not
hand-edit the rendered evidence block or the template's fixed text.

This matters more here than it would anywhere else. This is the closing step of
the effort that ships the review protocol, and its own transcript is the first
worked example anyone will read. A request that imitates launcher output while
misstating the mandatory validation floor is exactly the drift the versioned
acceptance record exists to prevent.

Two smaller notes, neither a finding. The coverage record's Step 5 section names
the three final test functions but never names the new
`test_review_mode_docs_final_acceptance_tdd.py` file, so a reader following the
record to a file lands only on the incremental module; one path in that section
would close it. And removing the duration sentence from the performance row was
the right call rather than refreshing a stale figure.

Publish another round once both are addressed. Nothing else is requested: no
repair was made, no tracked validation side effect exists, no boundary was
crossed, and `a.commit` is accurate and needs no amendment.

Do not treat this answer as commit authority.

### Decision rationale for step 5 review-mode-docs round 3 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is that this
round's own request artifact is not what it claims to be.

Five of the six readiness-floor results pass, and they pass more cleanly than in
any earlier round of this effort. Identity is exact: the live exchange context,
the machine envelope, the human-readable request, the `pw` plan, step 5, a
positive round 3, and the request-time index tree all agree, and
`4c740cd51f4d7b8fc5e4e5f9990f7d6a7ef20b39` matched the live index at entry, so
the round 2 identity failure is genuinely repaired without reverting either
performance commit. The implementation is complete and all four round 1 findings
are closed against the code rather than against the writer response. Mandatory
validation and coverage pass: the union of seven commands all ran, the forced
walk reported 1,897 tests at `cov=100` with `outliers=0`, `excluded=0`, and
`exit=0`, and the focused package reported `100% (20/20)`. Staged attribution is
clean: seven in-step paths, no reviewer repair, an unchanged umbrella digest,
and `validation-state compare` returning `acceptable: true` with nothing tracked
or untracked. `a.commit` was rebuilt from an emptied file and is accurate in
membership, grouping, order, scope, and conventional subjects.

The sixth result is unresolved findings, and two remain.

The one that decides the round is the request itself. Its
`resolved_validation_set` attributes `ghog day --force` to the `project` source
and contains no plain `ghog day`, and the shipped resolver cannot produce that:
`DEFAULT_PROJECT_VALIDATION_COMMANDS` is the single value `ghog day`, passed
straight into `resolve_code_review_validation` with no configuration seam, so
the mandatory project default was replaced rather than added to. The requestor
instruction states the rule in words, that an addition cannot remove the
`ghog day` project default. Two further tells confirm the block was not rendered:
compact JSON arrays where the renderer emits `indent=2`, and three
template-fixed passages paraphrased, including the loss of "validly" from the
substantive-repair rule.

No evidence was lost by it. The forced walk is stricter than the default and
this reviewer ran both. The reason it still blocks is that the request-time
evidence block exists precisely so a reviewer can trust it as machine-produced.
Once it is hand-authored, the recorded validation floor is an assertion rather
than a fact, and recommending readiness on it would certify a durable record
this reviewer knows to be misrepresented. That the misstatement understates the
mandatory floor, in the closing step of the effort that ships this very
protocol, is what turns a formatting observation into a blocking finding.

The second finding would not have blocked on its own, and that is worth stating
plainly. Duplicating sixteen page-path literals and one helper across the two
modules is a reuse defect with a real silent-drift scenario, but it is a
consequence of the category split the round 1 answer instructed, and this
reviewer would have recorded it in prose and recommended readiness had it stood
alone. It is listed as a finding because a round is already required, and
closing it in the same round is cheaper than carrying it.

The implementation check records `Yes` rather than `No`, deliberately. Every
file the step names exists with its final content, all twenty tests are present
and green, every gate passes, and the module sizes, test count, and walk figures
in the validation record all reproduce. There is no missing deliverable and no
work list for `implement-missing-step`. What remains is one protocol artifact to
re-render and one set of constants to hoist.

No repair was made this round, and none was needed: the pre-repair blob recorded
for the validation plan went unused, because every measurable claim in the Step 5
rows checked out, including the reviewer's own round 1 correction from 21 to 20
focused tests, which the writer carried forward rather than restoring.

No boundary-crossing work is reported. Nothing outside Step 5 was touched, both
performance commits are intact, no production module, protocol behavior,
launcher, template, or adapter changed, and reviewer mode completed no umbrella
row.

The execution-time question is closed and was not reopened. The request reports
a 1m49.1s full phase and this round measured 1m52.9s on the same tree; timing
variation between two walks is not a defect and is recorded as an observation
only.

Step 5 is finished as an implementation. Both remaining items are mechanical,
one of them is a single launcher invocation, and the round that follows should
be a short confirmation.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 5 review-mode-docs round 3 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-3 -->

## Round 4 by requestor - Step 5

- Recorded: 2026-08-21T19:31:47+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 review-mode-docs round 4

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 5
Review round: 4

### Code review evidence for step 5 review-mode-docs round 4

request_index_tree: d625975f081e0bb2c38821fcf3de3e347bf45e5b
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)
- rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: plan)
- ghog day --force (sources: request)
- rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: request)

### Requestor assessment for step 5 review-mode-docs round 4

Yes. Step 5 remains fully implemented, and both round 3 findings are closed.

The shared page paths, guide tuple, inventory tuple, coverage path, and
contains assertion now have one definition in `conftest.py`. Both acceptance
modules import that shared vocabulary, so changing one inventory list cannot
silently narrow the other module's completeness check.

The helper is public as `assert_contains`, matching the other shared assertion
helpers in `conftest.py` and satisfying Pyright. The measured module sizes are
141 lines for `conftest.py`, 401 for the incremental module, and 139 for the
final-acceptance module; the validation record carries those exact figures.

Round 4 is rendered by `bin/code_review_request.bat`. Plain `ghog day` remains
the project default, and `ghog day --force` is an additive request command.

### Implementation report for step 5 review-mode-docs round 4

The Step 5 acceptance split now shares its documentation vocabulary and common
contains assertion through the package fixture module. The incremental and
final modules retain their separate test responsibilities while importing one
source of page and inventory identities.

Groundhog reports 1,897 tests with `fail=0`, `warn=0`, `xfail=0`, `cov=100`,
`outliers=0`, `excluded=0`, and `exit=0`. The focused review-mode documentation
package passes 20 of 20 tests. Both Git whitespace checks and both bounded
coverage-document searches pass.

### Change summary for step 5 review-mode-docs round 4

The staged subject still contains exactly seven paths in two
dependency-ordered groups. The reuse repair changes three paths already in
Group 1, and the refreshed measured line counts change the validation plan
already in Group 2. No path moved between groups.

Group 1 remains `docs(review-mode-docs): close acceptance coverage`. Group 2
remains `docs(review-mode-docs): record step 5 validation`, with the exact final
subject required by the plan. `a.commit` parses cleanly and still covers every
staged path once. The protocol transcript remains unstaged.

### Writer response for step 5 review-mode-docs round 4

Writer response: Accepted both round 3 findings without disagreement.

I moved the duplicated documentation constants, guide and inventory tuples,
and contains assertion into `conftest.py`, then imported them in both acceptance
modules. Pyright rejected the initially private helper as unused in the special
fixture module, so I made it the public `assert_contains`, consistent with the
other shared assertion helpers. The validation record now states the measured
141-, 401-, and 139-line sizes.

After that correction, a fresh Groundhog walk passed all 1,897 tests at 100%
coverage with no outliers or exclusions, and the focused package passed 20 of
20 tests. Both Git whitespace checks pass. `a.commit` remains accurate without
an amendment.

This round is rendered entirely by `bin/code_review_request.bat`. The forced
walk is supplied through `--request-validation-command`, so it is additive to
the launcher's mandatory plain `ghog day` project default. I did not edit the
rendered request content or transcript summary.

### Reviewer focus for step 5 review-mode-docs round 4

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-4 -->

## Round 4 by reviewer - Step 5

- Recorded: 2026-08-21T19:45:43+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 review-mode-docs round 4 (exchange 1)

Baseline index tree: d625975f081e0bb2c38821fcf3de3e347bf45e5b

Assessed index tree: d625975f081e0bb2c38821fcf3de3e347bf45e5b

### Implementation check for step 5 review-mode-docs round 4 (exchange 1)

Result: Yes. Step 5 has been fully implemented.

Both round 3 findings are closed, and each was checked against the code rather
than accepted from the writer response.

The request is genuinely launcher-rendered this time. Its evidence block uses
the expanded array form that `json.dumps(payload, indent=2, sort_keys=True)`
produces, `ghog day` is back as the `project` source, `ghog day --force` sits
beside it as a `request` addition rather than replacing it, and the ordering is
the resolver's own project-then-plan-then-request sequence. The three passages
that are fixed text in `templates/code-review-request.template.md` are verbatim
again, including the word "validly" in the substantive-repair rule. That is the
right fix: the forced walk is kept as the stricter check without removing the
mandatory floor.

The duplication is gone from the staged content. `conftest.py` now owns
`_EXPLANATION`, `_SELF_REVIEW_EXPLANATION`, `_SELF_REVIEW_HOW_TO`, `_COVERAGE`,
`_SPEC_TUTORIAL`, `_CODE_TUTORIAL`, `_HOW_TO_GUIDES`, `_REFERENCE`,
`_INVENTORY_CANDIDATES`, and the now-public `assert_contains`, and both
acceptance modules import that one vocabulary. The silent-drift scenario the
round 3 answer described is closed: a seventh inventory candidate can only be
added in one place. Promoting the helper to a public name because Pyright
rejected an unused private in the fixture module is the right call and matches
the other shared helpers.

The recorded sizes are accurate. `conftest.py` is 141 lines, the incremental
module 401, and the final-acceptance sibling 139, all measured with the plan's
own `ReadAllLines` command template, and all below the 500-line advisory and the
650-line ceiling. The package still holds twenty test functions and
`ghog single` reports `100% (20/20)`.

The coverage record, the umbrella row 6 transition, and the validation plan's
Step 5 rows are unchanged in substance from round 3 and remain accurate. All
five step verdicts read `Yes`, so the document-level `Yes, it is implemented.`
line is earned. Architecture, performance, and feature integrity stay clean: no
production module, protocol operation, adapter, launcher, or runtime scan was
added, every traversal is linear over a finite declared set, and no existing
feature or reporting capability is impaired.

The verdict is Yes because the implementation is complete and correct. What
blocks this round is not the content but which copy of it is staged: the index
holds an earlier version of both acceptance modules whose import block fails the
repository's own lint gate, and the corrected version exists only in the working
tree, unstaged. That is a staging defect and a validation-coverage gap, not
missing work, so it is carried as an unresolved finding rather than recorded as
incomplete implementation.

Validation plan effects: Reviewer mode wrote no validation-plan row this round and made no repair
anywhere, so there is no reviewer-authored validation-plan difference. That is
the second consecutive round needing none.

The whole staged validation-plan difference is writer work that was assessed
rather than rewritten, and every measurable claim in the Step 5 rows was checked
against the repository.

The verdict sentence is the exact `Yes. Step 5 has been fully implemented.`
form, followed by an empty line and a prose summary, as the template orders, and
no `Missing work for Step 5` section is present or needed.

The architecture row records `conftest.py` at 141 lines, the incremental module
at 401, and the final-acceptance sibling at 139. All three match the files when
measured with the plan's own `ReadAllLines` command template. The unit-coverage
row records 20 focused tests, which `ghog single` confirms as `100% (20/20)` and
which is the reviewer's round 1 correction still carried correctly. The
performance row records 1,897 tests at `cov=100` with `outliers=0`,
`excluded=0`, and `exit=0`, which the forced walk in this round reproduces. The
feature-integrity row names `a.reviewtool` and `bin/mdlint` as the rejected
references, matching what the guard checks.

One thing the Step 5 rows do not yet say is worth noting rather than editing.
Every figure in them was measured against the working tree, and the working tree
is not what is staged for the two acceptance modules. The numbers happen to hold
for both copies, because the difference between them is a two-line reordering
inside one import block, but the record does not distinguish the two and a
reader would take it as describing the staged subject. Once the corrected
modules are staged, the rows become true of the reviewed subject without any
figure changing.

Reviewer mode wrote no row for any step, changed no document-level status line,
and completed no umbrella row. Umbrella row 6 stays exactly as the writer staged
it, and rows 7 and 8 stay `pending`.

### Pre-repair mandatory checks and coverage for step 5 review-mode-docs round 4 (exchange 1)

No repair was made this round. One pre-repair blob was recorded defensively
before assessment began, because the reviewed-step validation rows are the one
path reviewer mode may write:
`record-pre-repair-blob docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`
returned object `ec7059163e68f6b09e2b7e32261caca3f08fac72` with
`writer_deleted: false`, retained through `write-manifest` before any command
ran. It was never used, because every measurable claim in those rows checked
out.

The mandatory checks ran with the index at
`d625975f081e0bb2c38821fcf3de3e347bf45e5b`, the tree the request names, and the
index was still that value after every command.

`ghog day --force` reported `check` green, `affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests, with the full phase at 1m41.3s.
`ghog single tests/unit/tools/test_review_mode_docs_acceptance` reported
`100% (20/20)` with `exit=0`.

Those green results describe the working tree, not the reviewed subject, and
that distinction is this round's blocking finding rather than a footnote.
`bin/python_check.bat` runs `ruff check "%PRJ_DIR%"` against the project
directory with no `--fix`, so the gate lints working-tree files and never reads
the index. The staged blobs were therefore checked directly, by piping each one
from `git show :<path>` into `ruff check --isolated --select I` under its own
filename. Both staged acceptance modules report
`I001 Import block is un-sorted or un-formatted`, while the same rule over the
working-tree directory reports `All checks passed!`. `pyproject.toml` sets
`select = ["ALL"]` and its ignore list carries only `E501`, `D401`, `D203`, and
`D213`, so I001 is enabled and unignored.

The line-terminator pre-state was measured again, because a CRLF collateral
repair was needed in three of the first four steps of this effort. For all seven
staged paths the ordinary `git diff --cached --numstat` equals the
`--ignore-cr-at-eol` numstat, and both acceptance modules are pure LF at zero
CR, so this staged subject carries no terminator churn.

Every figure the request reports reproduced: the walk total, coverage, outlier
and exclusion counts, the exit code, the focused `20/20`, and all three module
sizes at 141, 401, and 139 lines under the plan's own `ReadAllLines` command.
The only divergence is a wall-clock duration, 1m41.3s here against the request's
figures, which is variation between two walks and is recorded as an observation
only.

### Resolved validation set and sources for step 5 review-mode-docs round 4 (exchange 1)

The request supplied seven commands and the current resolver produces the same
seven, so the union is seven and every one was run.

`ghog day`, sourced from the project, reported the freshness short-circuit
`No Python file changed since the last green ghog day walk` with `cov=skipped`
and `exit=0`. On its own that is not coverage evidence, which is why the forced
variant below was run first and is the result this answer relies on.

`ghog day --force`, sourced from the request, reported `check` green,
`affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests, with the full phase at 1m41.3s and the slowest call well under the
0.50s floor.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `100% (20/20)` with `fail=0`, `warn=0`, `xfail=0`, and
`exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
plan, returned `exit=0` and matched three lines, the first being the final AC01
criterion row at line 11.

`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
request, returned `exit=0` and eight heading lines: one `#` title and seven
distinct `##` headings.

`rg` is not on this session's `PATH`; the ripgrep binary bundled with the host
was invoked by absolute path, so both searches genuinely executed.

Every one of the seven commands passed, and none of them covers the reviewed
subject for the two acceptance modules. Each of them reads the working tree,
and the working tree differs from the index for exactly those two paths, so a
green union here is compatible with a staged subject that fails the gate. Two
checks outside the mandatory set establish that directly: piping each staged
blob from `git show :<path>` into `ruff check --isolated --select I` reports
`I001` on both modules, while the same rule over the working-tree package
reports `All checks passed!`.

Two non-mandatory corroborations were added. The strict commit-plan dry run
returned two groups covering all seven staged paths with an empty diagnostic
list, and the repository's Markdown linter helper reported `TOTAL 0` over the
coverage record, the validation plan, the umbrella draft, and the live
transcript.

No mandatory command was unavailable, none was skipped, and none was recorded
as passing without being executed.

### Resolver drift and direction for step 5 review-mode-docs round 4 (exchange 1)

No resolver drift was observed, and the round 3 drift is repaired.

The seven commands in the request envelope and the seven the current resolver
produces are identical in content, in source attribution, and in order:
`ghog day` from the project; `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, `git diff --cached --check`, and
`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the plan's
Step 5 completion criteria and shared execution checklist; and `ghog day --force`
plus `rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the
request.

The mandatory project default is present again. Round 3 recorded
`ghog day --force` under the `project` source with no plain `ghog day` entry,
which the shipped resolver cannot emit; this round carries the forced walk as a
`request` addition beside the untouched project default, which is exactly what
`instructions/code-review-requestor.md` requires when it says an addition may
share a command with another source but cannot remove the `ghog day` project
default.

The ordering also matches the resolver's own deterministic project, then plan,
then request sequence, and the block is rendered in the expanded array form that
`json.dumps(payload, indent=2, sort_keys=True)` produces. Both are consistent
with launcher output rather than authored text.

The set grew from six commands to seven because the forced walk is now recorded
as an addition rather than substituted for the default. That is the intended
direction, and the union equals both sets with nothing added or dropped when it
was run.

### Repository state around validation for step 5 review-mode-docs round 4 (exchange 1)

The request-time index tree is `d625975f081e0bb2c38821fcf3de3e347bf45e5b`, and
`capture-index-tree` at reviewer entry returned the same value, so identity held
and the early rejection path did not apply. The assessed index tree is the same
value, because this round staged nothing, and the index was still that value
after every mandatory command.

`HEAD` is `6e9f939`, so both performance commits remain intact and neither was
disturbed to reach this tree.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, with before and after both
`e9be8f8b3fa5ec11b489f836d0f97088948048edfeeb4b95eb47157204c1d0bb`, so no
umbrella boundary was crossed and reviewer mode completed no umbrella row.
Umbrella row 6 is staged as `completed` by the writer; rows 7 and 8 remain
`pending`.

The working tree does not match the index, and that is this round's central
observation rather than an incidental one. `git status` reports `MM` on
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`
and `AM` on
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`,
so both acceptance modules carry unstaged writer work on top of their staged
content. The unstaged delta is the same in both files and is exactly two lines:
`assert_contains` moved above `assert_local_links` inside the
`from .conftest import (...)` block. The staged copies are the unsorted ones.
Per the ownership rules a pre-existing unstaged overlap stays unstaged and
unreverted and is returned as a finding, so neither file was staged, reverted,
or edited.

`validation-state compare` over the ordered nine-path set returned
`acceptable: false`, naming one tracked path,
`tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`.
Its recorded content digest moved from
`453592ead5875d5a32b5395ade529d8ee342c6ac8f80a452a5b44fd07563d76e` at the
baseline capture to
`5bf899c360d29a6dd0f992d43e0d24668f03a72733d3b9179ba2054763cd2a3f` afterwards,
and the file's last-write time is 19:35:47, inside the window of the forced walk
that started at 19:35:28.

That difference is reported rather than explained away, and it is reported
without attributing a cause, because the evidence does not settle one. The gate
is not a plausible author: `bin/python_check.bat` runs `ruff check` with no
`--fix`, and no other `--fix` invocation exists under `bin/`. A concurrent
writer session is the likelier explanation, since the requestor published this
round at 19:31:47 and the same two files are the ones it had been editing. Either
way the reviewed tree was written to while under review, which is a hazard worth
recording in its own right. The path was left unstaged and unreverted.

The only other difference is the ignored artifact `a.ghog.status`, which each
walk rewrites by design; a difference confined to an ignored validation artifact
is acceptable, and it was neither staged nor reverted. No untracked path
changed.

Beyond those two acceptance modules the working tree holds no unstaged writer
work. Its only other unstaged entry is
`docs/v0.11.0/review.code.v0.11.0.review-mode-docs.md`, the protocol transcript
for this exchange, which the shared core owns and which correctly stays outside
the reviewed index.

### Repair inventory for step 5 review-mode-docs round 4 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 review-mode-docs round 4 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the seven staged paths with no omission and no
extra. The strict dry run over the live staged set returns two groups, all seven
paths, and an empty diagnostic list.

Group 1, `docs(review-mode-docs): close acceptance coverage`, lists the coverage
record, the package `__init__.py`, the fixture helper, the incremental
acceptance module, and the final-acceptance sibling. Group 2,
`docs(review-mode-docs): record step 5 validation`, lists the umbrella draft and
the validation plan.

The ordering runs from least to most dependent, with the evidence and the tests
that close it first and the validation verdict plus the umbrella status
transition last, so the recorded verdict never precedes the work it describes.
Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and the final subject is the exact
`docs(review-mode-docs): record step 5 validation` line this step requires.

The round 4 reuse repair changed three paths that Group 1 already covered and
the refreshed line counts changed the validation plan that Group 2 already
covered, so no path moved between groups and no membership change was needed.
That matches the change summary.

One qualification belongs on this result. `a.commit` is accurate about which
paths are staged; it cannot express which version of a path is staged, and for
the two acceptance modules the staged version is the one that fails the lint
gate. Correcting that is a staging action, not an `a.commit` amendment, so the
plan needs no edit and will still be correct once the corrected modules are
staged.

No commit was run.

### Findings and boundaries for step 5 review-mode-docs round 4 (exchange 1)

Unresolved findings:

- Finding 1, staged subject fails the mandatory gate, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py` and `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_final_acceptance_tdd.py`: the index holds an earlier copy of both acceptance modules whose `from .conftest import (...)` block lists `assert_local_links` before `assert_contains`, and piping each staged blob from `git show :<path>` into `ruff check --isolated --select I` reports `I001 Import block is un-sorted or un-formatted` on both, while the same rule over the working-tree package reports `All checks passed!`; `pyproject.toml` sets `select = ["ALL"]` with an ignore list of only `E501`, `D401`, `D203`, and `D213`, so I001 is enabled and unignored, and committing this index would land a tree that fails `ghog check` for the first person who runs it on a clean checkout.
- Finding 2, validation evidence does not cover the reviewed subject, `bin/python_check.bat`: the gate runs `ruff check "%PRJ_DIR%"` against the project directory with no `--fix` and never reads the index, so every green result in this round and in the request, including `ghog day --force` at 1,897 tests with `cov=100` and `outliers=0` and the focused `100% (20/20)`, was measured against a working tree that differs from the staged subject for exactly the two paths finding 1 names; no command in the resolved validation set can detect the defect, which is why a green union and a broken index coexist here and why re-running the walk is not the fix.
- Finding 3, the reviewed tree was written to during the round, `tests/unit/tools/test_review_mode_docs_acceptance/test_review_mode_docs_acceptance_tdd.py`: `validation-state compare` returned `acceptable: false` for this tracked path, its recorded digest moving from `453592ead5875d5a32b5395ade529d8ee342c6ac8f80a452a5b44fd07563d76e` at the baseline capture to `5bf899c360d29a6dd0f992d43e0d24668f03a72733d3b9179ba2054763cd2a3f` afterwards with a last-write time of 19:35:47 inside the forced-walk window, and the cause is not attributable from the evidence because the gate has no `--fix` invocation anywhere under `bin/`, leaving a concurrent writer session on the same two files as the likelier explanation; the path was left unstaged and unreverted, and the round cannot certify a tree that moved while it was being assessed.

Boundary-crossing work: None.

### Writer instructions for step 5 review-mode-docs round 4 (exchange 1)

Both round 3 findings are properly closed, and the fixes are the right ones. The
request is launcher-rendered again, with `ghog day` restored as the project
default and `ghog day --force` carried beside it as a `request` addition, which
is exactly the additive form the requestor instruction asks for. The shared
vocabulary now lives in `conftest.py` and both modules import it, so the silent
narrowing scenario is closed, and promoting the helper to a public
`assert_contains` because Pyright rejected an unused private in a fixture module
was the correct response rather than a workaround. The recorded 141, 401, and
139 line counts are exact under the plan's own measurement command.

Step 5's content is finished. What is wrong is which copy of it is in the index.

Stage the corrected acceptance modules. `git status` reports `MM` on
`test_review_mode_docs_acceptance_tdd.py` and `AM` on
`test_review_mode_docs_final_acceptance_tdd.py`, so both carry unstaged work on
top of what you published. The unstaged delta is two lines in each file:
`assert_contains` moved above `assert_local_links` inside the
`from .conftest import (...)` block. The staged copies are the unsorted ones,
and they fail `ruff` I001, which `pyproject.toml` enables through
`select = ["ALL"]` and does not ignore. Add both files, then confirm with
`git status` that neither still shows a second-column `M`.

Do not take the green walk as evidence that this is fine. It is not that the
gate was skipped; it is that the gate cannot see the problem.
`bin/python_check.bat` runs `ruff check "%PRJ_DIR%"` over the working tree with
no `--fix`, and never reads the index, so `ghog day --force` will keep reporting
1,897 tests at `cov=100` with `outliers=0` no matter what the index holds. To
check the staged copy directly, pipe it in:
`git show :<path>` into `ruff check --isolated --select I --stdin-filename <path> -`.
Both staged modules report `I001` today; the working-tree package reports
`All checks passed!`.

Then re-run the gate and republish with a fresh index tree. Once the corrected
modules are staged the index tree changes, so
`d625975f081e0bb2c38821fcf3de3e347bf45e5b` must not be reused. Nothing in the
validation record needs a new figure: the line counts, the test total, the
coverage, and the outlier count all hold for the corrected copies too, because
the difference is a reordering inside one import block.

One more thing to settle before you republish, and it is not about your content.
`validation-state compare` reported that
`test_review_mode_docs_acceptance_tdd.py` changed during this round: its digest
moved from `453592ea` to `5bf899c3` with a last-write time of 19:35:47, inside
the forced-walk window. The gate cannot be the author, because no `--fix`
invocation exists anywhere under `bin/`. The likeliest explanation is that
another session was still writing these files while the round was under review.
Check that no editor, agent, or watcher is holding this package open, and
publish the next round from a tree that is quiet, otherwise the next reviewer
will be assessing a moving target again.

Publish another round once both modules are staged and the gate has been re-run
against them. Nothing else is requested: no repair was made, `a.commit` is
accurate and needs no amendment, the umbrella digest is unchanged, and the
coverage record and validation plan need no edit.

Do not treat this answer as commit authority.

### Decision rationale for step 5 review-mode-docs round 4 (exchange 1)

The disposition is `changes-requested`, and the deciding reason is that the
index does not hold the version of the work that passes the gate.

Four of the six readiness-floor results pass. Identity is exact: the live
exchange context, the machine envelope, the human-readable request, the `pw`
plan, step 5, a positive round 4, and the request-time index tree all agree, and
`d625975f081e0bb2c38821fcf3de3e347bf45e5b` matched the live index at entry and
after every command. The implementation is complete, and both round 3 findings
are genuinely closed against the code: the request is launcher-rendered with the
project default restored and the forced walk carried as an addition, and the
shared vocabulary now has one definition in `conftest.py` that both modules
import. `a.commit` is accurate in membership, grouping, order, scope, and
conventional subjects, and the umbrella digest is unchanged with row 6 staged by
the writer and rows 7 and 8 untouched.

The two that fail are mandatory validation and staged attribution, and they fail
for the same underlying reason.

The staged copies of both acceptance modules list `assert_local_links` before
`assert_contains` in their `conftest` import block. Piping each staged blob into
`ruff check --isolated --select I` reports `I001` on both, while the same rule
over the working tree reports `All checks passed!`. `pyproject.toml` selects
`ALL` and ignores only `E501`, `D401`, `D203`, and `D213`, so I001 is live.
Committing this index would land a tree that fails `ghog check` for the first
person to run it on a clean checkout.

What makes this blocking rather than a nit is the second half. The gate cannot
detect it. `bin/python_check.bat` runs `ruff check` over the project directory
with no `--fix` and never reads the index, so every green figure in this round
and in the request describes a working tree that differs from the reviewed
subject at exactly the two paths in question. The request's 1,897 tests at
`cov=100` with `outliers=0` are real, and they are evidence about a tree nobody
is proposing to commit. A reviewer who accepted them here would be certifying a
subject that no command in the resolved validation set has ever examined, and
re-running the walk would not change that.

The third finding is smaller in consequence and larger in what it implies.
`validation-state compare` returned `acceptable: false` for
`test_review_mode_docs_acceptance_tdd.py`, with its digest moving from
`453592ea` to `5bf899c3` and a last-write time of 19:35:47, inside the forced
walk. The cause is not attributable from the evidence, and this answer does not
guess one: the gate has no `--fix` invocation anywhere under `bin/`, which
leaves a concurrent session on the same two files as the likelier explanation.
Either way the tree moved while it was being assessed, and a round cannot
certify a subject that is still being written. The path was left unstaged and
unreverted, as the ownership rules require.

The implementation check records `Yes` rather than `No`, deliberately. Every
file the step names exists with its final content, all twenty tests are present
and green, the module sizes and figures in the validation record all reproduce
exactly, and both round 3 findings are closed. There is no missing deliverable
and no work list for `implement-missing-step`. The defect is a staging error,
and its remedy is `git add` on two files that are already correct on disk.

No repair was made, and none was possible. The correct content already exists in
the working tree, but staging it would be sweeping pre-existing unstaged writer
work into the index, which the ownership rules forbid outright, and the same
rules say a pre-existing unstaged overlap stays unstaged and is returned as a
finding. So it was returned rather than fixed, even though the fix is two `git
add` calls.

No boundary-crossing work is reported. Nothing outside Step 5 was touched, both
performance commits are intact, no production module, protocol behavior,
launcher, template, or adapter changed, and reviewer mode completed no umbrella
row.

The execution-time question stayed closed and was not reopened.

Step 5 is finished as an implementation, and this round did not ask for a single
change to its content. The next round should be a short confirmation once the
right copy is staged from a tree that has stopped moving.

This answer is advisory and authorizes no commit. The `Commit` or
`Rework and review again` choice remains with the human at the convergence gate,
and no commit was run in this round.

### Final reviewer decision for step 5 review-mode-docs round 4 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-4 -->

## Round 5 by requestor - Step 5

- Recorded: 2026-08-21T20:13:03+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 review-mode-docs round 5

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
Implementation step: 5
Review round: 5

### Code review evidence for step 5 review-mode-docs round 5

request_index_tree: 3ee3995f9bfd60a82d3766de3b63975523ffee9e
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_review_mode_docs_acceptance (sources: plan)
- git diff --check (sources: plan)
- git diff --cached --check (sources: plan)
- rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: plan)
- ghog day --force (sources: request)
- rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md (sources: request)

### Requestor assessment for step 5 review-mode-docs round 5

Yes. Step 5 remains fully implemented, and all round 4 findings are closed.

Both acceptance modules now have the sorted import block in the index, and
`git status` shows no second-column modification for either path. Piping each
staged blob into Ruff with `--isolated --select I` reports `All checks passed!`,
so the reviewed subject and the checked working tree now carry the same bytes.

The package stayed quiet throughout the forced walk and the remaining checks:
no `MM` or `AM` entry returned. The shared constants and `assert_contains`
remain defined once in `conftest.py`, and the recorded 141/401/139 line counts
remain exact.

### Implementation report for step 5 review-mode-docs round 5

The only change since round 4 is staged-copy alignment for the two acceptance
modules. Their existing sorted `conftest` imports are now the copies proposed
for commit; no documentation content, test assertion, module count, or commit
group changed.

The forced Groundhog walk reports 1,897 tests with `fail=0`, `warn=0`,
`xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`; its full phase
took 1m43.3s. The focused package passes 20 of 20 tests, the plain project walk
returns its expected freshness result, both whitespace checks pass, and both
staged modules pass Ruff I001 directly.

### Change summary for step 5 review-mode-docs round 5

The staged subject still contains exactly seven paths in two
dependency-ordered groups. The corrected copies of the incremental and final
acceptance modules remain in Group 1; their membership and behavior are
unchanged.

Group 1 remains `docs(review-mode-docs): close acceptance coverage`. Group 2
remains `docs(review-mode-docs): record step 5 validation`, including the exact
final subject required by the plan. `a.commit` parses cleanly and covers every
staged path once. The protocol transcript remains unstaged.

### Writer response for step 5 review-mode-docs round 5

Writer response: Accepted all round 4 feedback without disagreement.

I staged the two corrected acceptance-module working copies. `git status` no
longer reports `MM` or `AM`, and each staged blob passes
`ruff check --isolated --select I` through its repository filename. This closes
the gap between the tree tested by Groundhog and the tree proposed for commit.

I then ran a forced Groundhog walk, the focused 20-test package, the plain
project walk, both Git whitespace checks, both coverage-record searches, and a
strict commit-plan parse. All pass. A status check after the forced walk and
again after the remaining commands showed no renewed second-column change, so
the package stayed stable throughout this requestor pass.

No validation figure, path membership, group order, or commit subject changed.
`a.commit` remains accurate without amendment.

### Reviewer focus for step 5 review-mode-docs round 5

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-5 -->

## Round 5 by reviewer - Step 5

- Recorded: 2026-08-21T20:22:29+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 review-mode-docs round 5 (exchange 1)

Baseline index tree: 3ee3995f9bfd60a82d3766de3b63975523ffee9e

Assessed index tree: 3ee3995f9bfd60a82d3766de3b63975523ffee9e

### Implementation check for step 5 review-mode-docs round 5 (exchange 1)

Result: Yes. Step 5 has been fully implemented.

All three round 4 findings are closed, and each was checked directly rather than
accepted from the writer response.

The staged copies now pass the gate. Piping each staged blob from
`git show :<path>` into `ruff check --isolated --select I` under its repository
filename reports `All checks passed!` for both acceptance modules, where round 4
reported `I001` on both. `git status` shows no second-column entry for any of
the seven staged paths, and `git diff --name-only` names only the protocol
transcript, so the index and the working tree carry the same bytes for the whole
reviewed subject.

That equality is what closes the second finding, and it matters more than the
first. `bin/python_check.bat` still runs `ruff check` over the working tree with
no `--fix` and still never reads the index, so the gate is no more capable than
it was. What changed is that there is no longer a gap for it to miss: this
round's green results describe the same bytes that are proposed for commit,
which was not true in round 4.

The tree stayed quiet this time. `validation-state compare` over the ordered
nine-path set returned `acceptable: true` with empty tracked and untracked
lists, across a forced walk, a plain walk, a focused run, both whitespace
checks, both coverage searches, a commit-plan parse, and a Markdown lint. Round
4's unattributed write at 19:35:47 did not recur, which is consistent with the
concurrent-session explanation that answer declined to assert and inconsistent
with the gate having authored it.

Nothing else moved, and that is the right shape for a closing round. The
coverage record, the umbrella row 6 transition, the validation plan's Step 5
rows, `a.commit`, the group membership, and the group order are byte-identical
to round 4. The only difference in the whole exchange is which copy of two files
sits in the index.

Every figure reproduces. The forced walk reports 1,897 tests with `fail=0`,
`warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`. The
focused package reports `100% (20/20)`, holding seventeen tests in the
incremental module and three in the final-acceptance sibling. `conftest.py` is
141 lines, the incremental module 401, and the sibling 139, all measured with
the plan's own `ReadAllLines` command template and all below the 500-line
advisory and the 650-line ceiling. The ordinary `git diff --cached --numstat`
equals the `--ignore-cr-at-eol` numstat for all seven paths, so there is no
line-terminator churn.

Architecture, performance, and feature integrity are clean. No production
module, protocol operation, adapter, launcher, or runtime scan was added. Every
assertion traverses a finite declared set of rows, pages, links, and paths once,
so validation stays linear with no new `O(n^2)` or `O(n log n)` work, and no
existing feature or reporting capability is impaired. The per-class unit
coverage rule does not bind a slice that changes no production class, and the
full walk reports `cov=100`.

Validation plan effects: Reviewer mode wrote no validation-plan row this round and made no repair
anywhere, so there is no reviewer-authored validation-plan difference. That is
the third consecutive round needing none.

The whole staged validation-plan difference is writer work that was assessed
rather than rewritten, and it is byte-identical to the copy assessed in round 4:
its blob is still `ec7059163e68f6b09e2b7e32261caca3f08fac72`.

The verdict sentence is the exact `Yes. Step 5 has been fully implemented.`
form, followed by an empty line and a prose summary, as the template orders, and
no `Missing work for Step 5` section is present or needed.

Every measurable claim in the Step 5 rows was re-checked against the repository
and holds. The architecture row's 141, 401, and 139 line counts match the files
under the plan's own measurement command. The unit-coverage row's 20 focused
tests match `ghog single` at `100% (20/20)` and the seventeen plus three test
functions across the two modules; that figure is still the reviewer's round 1
correction, carried correctly through four subsequent rounds. The performance
row's 1,897 tests at `cov=100` with `outliers=0`, `excluded=0`, and `exit=0`
match this round's forced walk. The feature-integrity row names `a.reviewtool`
and `bin/mdlint`, which is what the guard checks.

The qualification round 4 raised about these rows is now resolved without any
figure changing. That answer noted the numbers were measured against a working
tree that differed from the staged subject for two paths. The index and the
working tree now agree on all seven staged paths, so the rows describe the
reviewed subject directly rather than a near neighbour of it.

The document-level flip remains the writer's and remains correct: all five
`### Analysis of Step N implementation state` sections open with the exact
`Yes. Step N has been fully implemented.` sentence, so the opening
`Yes, it is implemented.` line and its theme sentence are earned.

Reviewer mode wrote no row for any step, changed no document-level status line,
and completed no umbrella row. Umbrella row 6 stays exactly as the writer staged
it, and rows 7 and 8 stay `pending` with `-` in both evidence columns.

### Pre-repair mandatory checks and coverage for step 5 review-mode-docs round 5 (exchange 1)

No repair was made this round. One pre-repair blob was recorded defensively
before assessment began, because the reviewed-step validation rows are the one
path reviewer mode may write:
`record-pre-repair-blob docs/v0.11.0/plan.v0.11.0.review-mode-docs.validation.md`
returned object `ec7059163e68f6b09e2b7e32261caca3f08fac72` with
`writer_deleted: false`, retained through `write-manifest` before any command
ran. It was never used, because every measurable claim in those rows checked
out. That object id is the same one round 4 recorded, which is independent
confirmation that the validation record did not change between the two rounds.

The mandatory checks ran with the index at
`3ee3995f9bfd60a82d3766de3b63975523ffee9e`, the tree the request names, and the
index was still that value after every command.

The staged subject was checked before the gate rather than after it, because
round 4 established that the gate cannot see the index. Each staged blob was
piped from `git show :<path>` into `ruff check --isolated --select I` under its
own repository filename, and both acceptance modules report
`All checks passed!`. `git diff --name-only` names only the protocol transcript,
so index and working tree agree on all seven staged paths and the gate results
below describe the reviewed subject rather than a near neighbour of it.

`ghog day --force` reported `check` green, `affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests, with the full phase at 1m58.0s.
`ghog single tests/unit/tools/test_review_mode_docs_acceptance` reported
`100% (20/20)` with `exit=0`.

Tree stability was measured rather than assumed, because round 4 recorded an
unattributed write during its walk. `git status` was taken again immediately
after the forced walk and reported the same eight entries with no second-column
change on any staged path, and the closing `validation-state compare` returned
`acceptable: true` with empty tracked and untracked lists. Nothing wrote to the
reviewed tree during this round.

The line-terminator pre-state was measured again, because a CRLF collateral
repair was needed in three of the first four steps of this effort. For all seven
staged paths the ordinary `git diff --cached --numstat` equals the
`--ignore-cr-at-eol` numstat, so this staged subject carries no terminator
churn.

Every figure the request reports reproduced: the walk total, coverage, outlier
and exclusion counts, the exit code, the focused `20/20`, the seventeen and
three test split, and all three module sizes at 141, 401, and 139 lines. The
only divergence is a wall-clock duration, 1m58.0s here against the request's
1m43.3s, which is variation between two walks of the same tree and is recorded
as an observation only.

### Resolved validation set and sources for step 5 review-mode-docs round 5 (exchange 1)

The request supplied seven commands and the current resolver produces the same
seven, so the union is seven and every one was run.

`ghog day`, sourced from the project, reported the freshness short-circuit
`No Python file changed since the last green ghog day walk` with `cov=skipped`
and `exit=0`. On its own that is not coverage evidence, which is why the forced
variant was run first and is the result this answer relies on.

`ghog day --force`, sourced from the request, reported `check` green,
`affected --no-cov` green, and
`ghog full done fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over
1,897 tests, with the full phase at 1m58.0s and no duration outlier.

`ghog single tests/unit/tools/test_review_mode_docs_acceptance`, sourced from
the plan, reported `100% (20/20)` with `fail=0`, `warn=0`, `xfail=0`, and
`exit=0`.

`git diff --check` and `git diff --cached --check`, both sourced from the plan,
returned no diagnostic and `exit=0`.

`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
plan, returned `exit=0` and matched three lines, the first being the final AC01
criterion row at line 11.

`rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md`, sourced from the
request, returned `exit=0` and eight heading lines: one `#` title and seven
distinct `##` headings.

`rg` is not on this session's `PATH`; the ripgrep binary bundled with the host
was invoked by absolute path, so both searches genuinely executed.

Unlike round 4, these results cover the reviewed subject. Each of these commands
reads the working tree, and `git diff --name-only` names only the protocol
transcript, so index and working tree carry the same bytes for all seven staged
paths. The union is therefore evidence about the tree proposed for commit rather
than about a near neighbour of it.

Three non-mandatory checks were added, two of them specifically because the gate
cannot inspect the index. Both staged acceptance-module blobs were piped from
`git show :<path>` into `ruff check --isolated --select I` and reported
`All checks passed!`. The strict commit-plan dry run returned two groups
covering all seven staged paths with an empty diagnostic list. The repository's
Markdown linter helper reported `TOTAL 0` over the coverage record, the
validation plan, the umbrella draft, and the live transcript.

No mandatory command was unavailable, none was skipped, and none was recorded
as passing without being executed.

### Resolver drift and direction for step 5 review-mode-docs round 5 (exchange 1)

No resolver drift was observed.

The seven commands in the request envelope and the seven the current resolver
produces are identical in content, in source attribution, and in order:
`ghog day` from the project; `ghog single tests/unit/tools/test_review_mode_docs_acceptance`,
`git diff --check`, `git diff --cached --check`, and
`rg -n AC01 docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the plan's
Step 5 completion criteria and shared execution checklist; and `ghog day --force`
plus `rg -n ^# docs/v0.11.0/coverage.v0.11.0.review-mode-docs.md` from the
request.

The mandatory project default is present and untouched, with the forced walk
carried beside it as a `request` addition rather than substituted for it. That
is the additive form `instructions/code-review-requestor.md` requires, and it is
unchanged from round 4, so the round 3 drift stays repaired across two
consecutive rounds.

The block is rendered in the expanded array form that
`json.dumps(payload, indent=2, sort_keys=True)` produces, in the resolver's own
deterministic project, then plan, then request order, and the request's
template-fixed passages are verbatim. All three remain consistent with launcher
output rather than authored text.

The union equals both sets, and nothing was added or dropped when it was run.

### Repository state around validation for step 5 review-mode-docs round 5 (exchange 1)

The request-time index tree is `3ee3995f9bfd60a82d3766de3b63975523ffee9e`, and
`capture-index-tree` at reviewer entry returned the same value, so identity held
and the early rejection path did not apply. The assessed index tree is the same
value, because this round staged nothing, and the index was still that value
after every mandatory command.

Round 4's tree, `d625975f081e0bb2c38821fcf3de3e347bf45e5b`, was correctly not
reused: staging the two corrected acceptance modules necessarily moved the
index, and the request carries the new value.

`HEAD` is `6e9f939`, so both performance commits remain intact and neither was
disturbed to reach this tree.

The working tree matches the index for the whole reviewed subject.
`git status` reports no second-column entry on any of the seven staged paths,
and `git diff --name-only` names only
`docs/v0.11.0/review.code.v0.11.0.review-mode-docs.md`, the protocol transcript
for this exchange, which the shared core owns and which correctly stays outside
the reviewed index. The `MM` and `AM` entries round 4 reported are gone, and
with them the gap between the tested tree and the proposed tree.

The applicable umbrella digest is unchanged. `umbrella-digest compare` returned
`changed: false`, with before and after both
`e9be8f8b3fa5ec11b489f836d0f97088948048edfeeb4b95eb47157204c1d0bb`, so no
umbrella boundary was crossed and reviewer mode completed no umbrella row.
Umbrella row 6 is staged as `completed` with its requirement and validation
paths by the writer, which is the writer's own final-step work; rows 7 and 8
remain `pending` with `-` in both evidence columns, so the deferred
`markdown-check` and `commit-plan-check` items are intact.

`validation-state compare` over the ordered nine-path set returned
`acceptable: true` with an empty tracked-path list and an empty untracked-path
list. A forced full walk, a plain walk, a focused run, both whitespace checks,
both coverage searches, a commit-plan parse, and a Markdown lint therefore
produced no tracked validation side effect at all, and no reviewer repair exists
to explain any difference.

That result also closes round 4's third finding on its own terms. An
intermediate `git status` taken immediately after the forced walk reported the
same eight entries with no renewed second-column change, so the unattributed
write at 19:35:47 did not recur under the same commands. That is consistent with
the concurrent-session explanation the round 4 answer offered without asserting,
and inconsistent with the gate having authored it, since
`bin/python_check.bat` runs `ruff check` with no `--fix` and no `--fix`
invocation exists anywhere under `bin/`.

The only difference is the ignored artifact `a.ghog.status`, which each walk
rewrites by design. A difference confined to an ignored validation artifact is
acceptable, and it was neither staged nor reverted.

### Repair inventory for step 5 review-mode-docs round 5 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 review-mode-docs round 5 (exchange 1)

`a.commit` is accurate and needed no amendment.

Its two groups cover exactly the seven staged paths with no omission and no
extra. The strict dry run over the live staged set returns two groups, all seven
paths, and an empty diagnostic list.

Group 1, `docs(review-mode-docs): close acceptance coverage`, lists the coverage
record, the package `__init__.py`, the fixture helper, the incremental
acceptance module, and the final-acceptance sibling. Group 2,
`docs(review-mode-docs): record step 5 validation`, lists the umbrella draft and
the validation plan.

The ordering runs from least to most dependent. The evidence and the tests that
close it land first, and the validation verdict plus the umbrella status
transition that certify them land last, so the recorded verdict never precedes
the work it describes and the umbrella row never claims a validation plan that
is not yet committed. That matches the grouping Steps 1 through 4 used, keeping
the effort's commit history consistent.

Both subjects are well-formed conventional messages with a `docs` type and the
`review-mode-docs` scope, and the final subject is the exact
`docs(review-mode-docs): record step 5 validation` line this step requires. Both
`Why` sections narrate the umbrella draft, the topic draft, the feature request,
the design, the implementation plan, and the validation plan.

The round 4 qualification on this result is now discharged. That answer noted
`a.commit` could say which paths are staged but not which version of them, and
that the staged version of two paths was the one failing the lint gate. Those
two paths now hold their corrected copies, so the plan is accurate about
membership and about content, and it needed no edit to become so.

This round staged nothing and made no repair, so file membership, grouping,
order, scope, and conventional subjects all still match the staged work exactly
as published. No commit was run.

### Findings and boundaries for step 5 review-mode-docs round 5 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 5 review-mode-docs round 5 (exchange 1)

Nothing is requested. Step 5 is ready as far as this reviewer can determine, and
this round asked for no change to any file.

All three round 4 findings are closed, and the fix was exactly the right one:
you staged the copies that already existed rather than rewriting anything. Both
staged blobs now report `All checks passed!` under
`ruff check --isolated --select I`, `git status` shows no second-column entry on
any staged path, and `git diff --name-only` names only the protocol transcript.
The index and the working tree carry the same bytes for the whole reviewed
subject, so the gate's green results describe the tree you are proposing to
commit rather than a near neighbour of it.

You also measured the right thing when you re-checked `git status` after the
forced walk. That, plus `validation-state compare` returning `acceptable: true`
with empty tracked and untracked lists, is what closes the third finding: the
tree stayed still for an entire round of commands.

Two things to carry forward rather than to fix.

Keep checking the staged blob, not just the walk, on any step whose subject is
Python. The gate runs `ruff check` over the working tree with no `--fix` and
never reads the index, so the blind spot round 4 hit is structural and will
return the moment a working copy runs ahead of the index again. The one-line
check is `git show :<path>` piped into
`ruff check --isolated --select I --stdin-filename <path> -`.

Umbrella rows 7 and 8 are still `pending`, and both of the checks this exchange
leaned on live there. Row 7, `markdown-check`, would replace the provisional
`a.reviewtool.py mdlint` this reviewer used for MD024 and MD025 corroboration.
Row 8, `commit-plan-check`, would replace its `commit-plan` subcommand. Neither
belongs in this step, and the coverage record is right to say so; they are worth
naming here so the next effort inherits the context rather than rediscovering
it.

The convergence gate is next, and it is the human's. This answer recommends
`commit-ready` and does not authorize a commit: the `Commit` or
`Rework and review again` choice is theirs, and no commit was run in this round.

### Decision rationale for step 5 review-mode-docs round 5 (exchange 1)

The disposition is `commit-ready`, advisory. All six readiness-floor results
pass, this round made no repair at all, and no finding remains from this round
or any earlier one.

Identity is exact. The live exchange context, the machine envelope, the
human-readable request, the `pw` plan, step 5, a positive round 5, and the
request-time index tree all agree; `3ee3995f9bfd60a82d3766de3b63975523ffee9e`
matched the live index at entry and after every command; and round 4's tree was
correctly retired rather than reused, since staging the corrected modules had to
move it.

The implementation is complete, and every claim in the record reproduces:
1,897 tests at `cov=100` with `outliers=0`, `excluded=0`, and `exit=0`; the
focused package at `100% (20/20)`, split seventeen and three across the two
modules; and module sizes of 141, 401, and 139 lines under the plan's own
measurement command. The coverage record maps AC01 through AC09 to exact pages,
carries AC10 through AC12 as evidence rows with their exact types and no page
path, and closes all six inventory dispositions against the central contract.

Mandatory validation passes, and for the first time in this step it demonstrably
covers the reviewed subject. That distinction is the whole substance of rounds 4
and 5 and is worth stating plainly: `bin/python_check.bat` runs `ruff check`
over the working tree with no `--fix` and never reads the index, so a green walk
is only evidence about the staged subject when the two agree. They now do.
`git diff --name-only` names only the protocol transcript, and both staged blobs
were checked directly through `git show :<path>` into
`ruff check --isolated --select I`, reporting `All checks passed!` where round 4
reported `I001` on both.

Staged attribution is clean: seven in-step paths, no unstaged overlap on any of
them, no untracked work, no reviewer repair, and an unchanged umbrella digest
with row 6 staged by the writer and rows 7 and 8 untouched. `a.commit` is
accurate in membership, grouping, order, scope, and conventional subjects,
including the exact required final subject, and needed no amendment.

No finding remains. All four round 1 findings were closed in round 3, both round
3 findings in round 4, and all three round 4 findings in this round. Round 2 was
an identity rejection that never reached content and was repaired without
disturbing either performance commit.

Round 4's third finding deserves its own sentence, because it was the one that
could not be closed by an edit. The reviewed tree was written to during that
round, at 19:35:47, by something the evidence could not attribute. This round
re-ran the same commands and the tree did not move: an intermediate `git status`
after the forced walk showed no renewed second-column change, and
`validation-state compare` returned `acceptable: true` with empty tracked and
untracked lists. That is the right way for that finding to close, by
non-recurrence under the same conditions rather than by assertion, and it leaves
the gate exonerated as the author.

This round made no repair, which is what lets it recommend readiness. The
rule that a substantive repair cannot validly finish the workflow in the same
round is not merely satisfied on a technicality here: nothing was touched, the
pre-repair blob recorded for the validation plan went unused, and its object id
is the same one round 4 recorded, so the record demonstrably did not change
between the two rounds.

No boundary-crossing work is reported. Nothing outside Step 5 was touched, both
performance commits are intact, no production module, protocol behavior,
launcher, template, or adapter changed, and reviewer mode completed no umbrella
row.

The execution-time question stayed closed. This round's full phase took 1m58.0s
against the request's 1m43.3s, which is variation between two walks of the same
tree, recorded as an observation and raised nowhere else.

This recommendation is advisory and authorizes no commit. It is the reviewer's
assessment that the evidence floor is complete, nothing more. The `Commit` or
`Rework and review again` choice remains with the human at the durable
convergence gate, and no commit was run in this round.

### Final reviewer decision for step 5 review-mode-docs round 5 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-5 -->

## Round 5 by human - Step 5 - human-confirmation

- Recorded: 2026-08-21T20:38:23+02:00
- Exchange: code/code/v0.11.0/review-mode-docs
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.review-mode-docs.md
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow
Guidance: Human choice: Commit

Human guidance: update `a.commit` to include `settings.json`.

The repository path is `.vscode/settings.json`. It adds `neighbour` to the
workspace spelling dictionary. The root `a.commit` now places that path in a
leading `chore(vscode): accept review terminology` group, followed by the two
review-mode documentation groups, with
`docs(review-mode-docs): record step 5 validation` still last.

<!-- review-entry-id: human-confirmation-round-5 -->
