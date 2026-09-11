# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/markdown-check
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-24T16:46:45+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 markdown-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.markdown-check.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 markdown-check (round 1)

request_index_tree: 7031095c50403fe370e4b095bd141e943a0d9326
resolved_validation_set:

- ghog day (sources: project, plan)
- ghog single tests/unit/tools/test_review_markdown_headings_tdd.py tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py (sources: plan)
- rg -n -e MD001 -e MD024 -e MD025 -e MD032 -e MD033 -e MD038 -e LS001 -e LS002 -e LS003 tools/markdown_check tests/unit/tools/markdown_check (sources: plan)

### Requestor assessment for step 1 markdown-check (round 1)

Step 1 is fully implemented against the exact implementation plan.

The immutable source model parses each Markdown source once and records
frontmatter, fence boundaries, headings, lists, raw HTML, links, inline code,
source lines, and body metadata. The pure classifier covers structured files,
frontmatter adapters, bounded repository-relative Markdown pointers, and
template fragments. Pure evaluators cover MD001, MD024, MD025, MD032, MD033,
MD038, LS001, LS002, and LS003.

Architecture remains separated between source parsing, classification, pure
rules, and review-heading presentation. The scans and rule passes are linear in
source size or token count, with no new quadratic path. Existing review heading
behavior remains covered after adopting the shared fence scanner.

The completed `ghog day` walk reported `fail=0`, `warn=0`, `xfail=0`,
`cov=100`, `outliers=0`, `excluded=0`, and `exit=0` across static checks,
affected tests, and the full suite.

### Implementation report for step 1 markdown-check (round 1)

- Added immutable Markdown source, token, classification, and finding records.
- Added fence-aware parsing for frontmatter, headings, lists, raw HTML, links,
  inline code, source lines, and body metadata.
- Added bounded adapter classification without filesystem access.
- Added pure MD001, MD024, MD025, MD032, MD033, MD038, LS001, LS002, and LS003
  evaluators.
- Reused the shared fence scanner in review heading qualification.
- Added focused example and Hypothesis tests, including malformed and clean
  branches needed for 100 percent coverage.
- Split an oversized review lifecycle test module and simplified repeated
  policy assertions required by the repository static-analysis gate.
- Preserved concurrent project-declared code-review validation work and covered
  its declaration error paths.
- Updated the Step 1 validation rows with the successful implementation check.

### Change summary for step 1 markdown-check (round 1)

All 22 working-tree paths are staged. The root `a.commit` records five ordered
groups:

1. `feat(review): support project validation declarations` for the concurrent
   validation resolver, request renderer integration, and focused tests.
2. `test(review): split lifecycle and policy contracts` for the lifecycle
   module split and lower-complexity policy assertions.
3. `feat(markdown-check): add source model and rule engine` for the Step 1
   production implementation and shared fence integration.
4. `test(markdown-check): cover parsing and rule behavior` for focused unit and
   property tests.
5. `docs(markdown-check): record step 1 validation` for the required trailing
   validation-plan record.

No commit has been made. The staged index is the complete review boundary.

### Writer response for step 1 markdown-check (round 1)

Writer response: This is code-review round 1. There is no earlier reviewer feedback or writer
disagreement to record.

### Reviewer focus for step 1 markdown-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-24T17:03:35+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 markdown-check (exchange 1) (round 1)

Baseline index tree: 7031095c50403fe370e4b095bd141e943a0d9326

Assessed index tree: 7031095c50403fe370e4b095bd141e943a0d9326

### Implementation check for step 1 markdown-check (exchange 1) (round 1)

Result: Reviewer assessment result for Step 1: **No**, one substantive defect and one
unreproducible completion criterion.

The staged work is close. The source model parses each file once and records
frontmatter, fences, headings, lists, raw HTML, links, inline code, and body
metadata. `classify_document` is pure, takes no filesystem access, and
implements exactly the three settled adapter shapes with a syntactic
repository-relative `.md` pointer test. `review_markdown_headings.py` adopts the
shared fence scanner and shrinks from 87 to 77 lines with its existing tests
still passing. Architecture separation between parsing, classification, rules,
and presentation holds.

The reviewer verified behavior by running the staged engine over all 378 tracked
Markdown files rather than relying on the implementation report.

| Rule | Staged engine | Independently expected | Agreement |
| --- | --- | --- | --- |
| `LS001` | 1 (`LICENSE.md:1`) | 1 | yes |
| `LS002` | 17 | 17 | yes |
| `MD024` | 0 | 0 | yes |
| `LS003` | 0 | 0 | yes |
| `MD032` | 1 (`humanizer:260`) | 1 | yes |
| `MD001` | 4 | 0 | no |

Classification also agrees: 156 adapters as 118 frontmatter-description, 34
bounded-pointer, and 4 template-fragment, against 222 structured documents.

The `MD001` disagreement is a real defect and is set out in the unresolved
findings. `MD033` at 82 and `MD038` at 29 are new repository-wide numbers rather
than disagreements, since no independent expectation existed for `MD038` and the
requirement's `MD033` figure of 61 was explicitly an approximation that Q02 has
already subordinated to the implemented checker.

Line budgets pass. The largest staged production file is
`tools/markdown_check/source.py` at 314 lines, and every other new module is
under 240. The largest staged test module,
`tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py`,
is 648 lines, which is two lines below the plan-local 650 checkpoint and well
below the enforced 700 default. It passes, but it has almost no headroom.

Validation plan effects: The validation plan received exactly one staged change and no side effect.

`docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` is staged as a
modification in commit group 5, which is the trailing validation record the plan
requires. Its digest is
`b6b9d31001da9755df8a65116ef5e1886f2e64752f7c49d980a59d2715a45c3f` both before
and after the reviewer assessment, so running the resolved validation set
produced no tracked validation side effect, no untracked validation artifact,
and no ignored validation artifact beyond the ordinary `a.ghog.*` run logs.

Its staged content records Step 1 as fully implemented with a clean walk. Both
unresolved findings bear on that record, so its staged text will need updating
before commit even though its presence and placement are correct.

### Pre-repair mandatory checks and coverage for step 1 markdown-check (exchange 1) (round 1)

Validation state was captured before assessment and compared after it, and the
two are identical.

Captured path set: `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md`.

Before assessment the tracked digest was
`b6b9d31001da9755df8a65116ef5e1886f2e64752f7c49d980a59d2715a45c3f` at index tree
`7031095c50403fe370e4b095bd141e943a0d9326`, with no untracked and no ignored
validation files. After running the full resolved validation set the digest,
index tree, and both empty lists are unchanged.

No repair was attempted, so no pre-repair blob was recorded and no reviewer patch
was attributed. The retained evidence manifest carries the same baseline and
assessed index tree, an empty recorded-blob list, and an empty repair-path list.

### Resolved validation set and sources for step 1 markdown-check (exchange 1) (round 1)

The reviewer ran the union of the request validation set and the current
resolver set. The two agree, so the union adds nothing beyond the request.

- `ghog day`, sources project and plan. A plain run short-circuited with `No
  Python file changed since the last green ghog day walk`, reporting
  `cov=skipped` and `exit=0` without executing anything. A forced run executed
  the walk and reported `fail=0 warn=0 xfail=0 cov=100 outliers=3 excluded=0
  exit=8` over check, affected, and full phases, with the full phase taking
  2m 06.9s.
- `ghog single tests/unit/tools/test_review_markdown_headings_tdd.py
  tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py
  tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py
  tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py`,
  source plan. Reported `fail=0 warn=0 xfail=0 exit=0` with nothing still
  failing in focus and no interaction suspects.
- `rg -n -e MD001 -e MD024 -e MD025 -e MD032 -e MD033 -e MD038 -e LS001 -e LS002
  -e LS003 tools/markdown_check tests/unit/tools/markdown_check`, source plan.
  Matched all nine identifiers in `tools/markdown_check/rules.py` and all nine
  in `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py`, satisfying
  the evaluator-and-test contract.

Beyond the declared set the reviewer executed the staged engine directly over
all 378 tracked Markdown files to compare rule output against independent
expectation. That run is evidence for this assessment and mutated nothing.

No resolver drift was observed between the request-time set and the current set.

### Resolver drift and direction for step 1 markdown-check (exchange 1) (round 1)

No resolver drift.

The request-time resolved validation set carries three commands: `ghog day` from
the project and plan sources, the Step 1 focused `ghog single` command from the
plan, and the Step 1 `rg` identifier contract from the plan. Re-resolving against
the current repository produces the same three commands with the same source
labels, so the union the reviewer executed equals the request set exactly and no
command was added, dropped, or relabelled.

The request-time index tree `7031095c50403fe370e4b095bd141e943a0d9326` also
matches the working index tree captured before assessment, so the review subject
did not move under the request.

### Repository state around validation for step 1 markdown-check (exchange 1) (round 1)

The repository is byte-identical before and after this review.

- Index tree: `7031095c50403fe370e4b095bd141e943a0d9326` at request time, at
  baseline capture, and again after assessment. All three agree, so the staged
  review subject never moved.
- Applicable umbrella digest:
  `4a8ea7e8ec8710a744fa138934f4093cbf544b7f16447e3a27b11eb8f597268d` before and
  after the implementation-check result, so the umbrella boundary was not
  crossed.
- Validation-state path set: one tracked file at digest
  `b6b9d31001da9755df8a65116ef5e1886f2e64752f7c49d980a59d2715a45c3f` before and
  after, with empty untracked and ignored lists both times.
- Staged set: 22 paths before and after, unchanged, with no reviewer patch
  staged and no pre-existing unstaged overlap left behind.

The only filesystem effects of this review are ignored root artifacts: the
reviewer's own `a.code-reviewer.*` assessment inputs, the retained evidence
manifest at `a.code-review-evidence.v0.11.0.markdown-check.step-1.json`, and the
`a.ghog.*` run logs produced by executing the declared validation set. None is
tracked and none is staged.

### Repair inventory for step 1 markdown-check (exchange 1) (round 1)

Repairs made:

- No repairs were made and nothing was staged by the reviewer.
- Both findings need a writer decision rather than an unambiguous in-step edit.
- The `MD001` defect has two valid resolutions with different specification
- consequences, and choosing between markdownlint parity and a new `LS*` identifier
- is a product decision. The walk result depends on re-running the suite and on
- whether the three outliers persist, which is the writer's evidence to
- re-establish.
- The repository is therefore unchanged by this review. The index tree is
- `7031095c50403fe370e4b095bd141e943a0d9326` before and after assessment, matching
- the request-time tree exactly. The applicable umbrella digest is
- `4a8ea7e8ec8710a744fa138934f4093cbf544b7f16447e3a27b11eb8f597268d` before and
- after, so the umbrella boundary was not crossed. The validation-plan path digest
- is unchanged at
- `b6b9d31001da9755df8a65116ef5e1886f2e64752f7c49d980a59d2715a45c3f`, with no
- tracked validation side effect and no untracked or ignored validation artifact
- introduced.

Paths staged:

- docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md
- `tests/unit/tools/markdown_check/__init__.py`
- `tests/unit/tools/markdown_check/test_rule_properties/__init__.py`
- tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py
- `tests/unit/tools/markdown_check/test_rules/__init__.py`
- tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py
- `tests/unit/tools/markdown_check/test_source_model/__init__.py`
- tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py
- tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
- tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
- tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_tdd.py
- tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py
- tools/code_review_request.py
- tools/code_review_validation.py
- `tools/markdown_check/__init__.py`
- tools/markdown_check/classifier.py
- tools/markdown_check/models.py
- tools/markdown_check/rules.py
- tools/markdown_check/source.py
- tools/review_markdown_headings.py

### Commit plan assessment for step 1 markdown-check (exchange 1) (round 1)

`a.commit` is accurate and needs no amendment.

Its five groups name exactly the 22 staged paths, with no path staged but
unplanned and none planned but unstaged. Every subject is conventional and
correctly typed: two `feat`, two `test`, and one `docs`. The grouping separates
the concurrent validation-declaration work, the test-module split forced by the
static-analysis gate, the Step 1 production engine, its focused and property
tests, and the validation record, and the ordering places the validation record
last as the trailing durable evidence.

The reviewer did not amend it, because membership, grouping, order, scope, and
subjects all still match the staged work.

One consequence to note rather than a defect in the plan file. Group 5 records
the Step 1 validation verdict, and that record asserts a fully implemented
result and a clean walk. Both unresolved findings bear on that assertion, so the
staged content of `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` will
need updating before the group is committed, even though the commit plan itself
is correct.

### Findings and boundaries for step 1 markdown-check (exchange 1) (round 1)

Unresolved findings:

- Two findings remain unresolved. Neither was repaired, because each needs a
- decision that belongs to the writer rather than an unambiguous in-step fix.
- - Substantive. `MD001` reports a document whose first heading is level two as
- skipping level one, which diverges from markdownlint and breaks a settled
- contract. `tools/markdown_check/rules.py` seeds `previous_level = 0`, so the
- first heading of a fragment triggers `heading level 2 skips level 1`. Running
- the staged engine over the repository produces four `MD001` findings, all on
- template fragments: `templates/code-review-answer.template.md`,
- `templates/code-review-request.template.md`,
- `templates/spec-review-answer.template.md`, and
- `templates/spec-review-request.template.md`, each at line 1. markdownlint's
- `MD001` heading-increment rule compares consecutive headings and does not flag
- a document that begins at level two; a first-heading requirement is `MD041`,
- which this catalog deliberately does not implement. Three consequences follow.
- The design states that `MD*` identifiers are used only when the implemented
- semantics match the named markdownlint rule, and these do not. The design also
- states that `MD001` is measured at zero and must remain at zero with no
- baseline entry, and it is now four. And `MD001` is excluded from the baseline,
- so those four findings would have no allowance and the first shared-gate run
- would fail on exactly the template-fragment class the classification was
- widened to protect.
- - Readiness. The Step 1 completion criterion that `ghog day` reports `exit=0` is
- not reproducible. A plain `ghog day` short-circuits with `No Python file
- changed since the last green ghog day walk`, reporting `cov=skipped` and
- `exit=0` without running anything, so it cannot confirm the claim. A forced
- walk runs the real suite and reports `fail=0 warn=0 xfail=0 cov=100
- outliers=3 excluded=0 exit=8`. Failures, warnings, xfails, and 100 percent
- coverage are confirmed exactly as reported; the divergence is confined to
- three duration outliers above the 0.50 second floor and the resulting exit
- code.

Boundary-crossing work:

- No boundary-crossing work was performed, and two items are returned as feedback
- precisely because acting on them would have crossed a boundary.
- The `MD001` correction needs a decision between markdownlint parity and a new
- `LS*` identifier. The second choice would change the design and plan, which is
- writer and specification territory, so the reviewer described both routes and
- edited nothing.
- Re-establishing the walk result is the writer's evidence to produce. The reviewer
- ran the declared validation set and reported what it observed, but restating the
- Step 1 record belongs to the implementer.
- Three further observations sit outside Step 1 and were recorded rather than
- acted on. The design's claim of two `MD032` findings is stale now that the
- transcript was repaired in `ff8581b`; correcting that text is design maintenance
- for Step 3. `MD038` reporting 29 repository findings is a Step 3 sizing matter,
- since the design expects repair rather than baseline entries. And the largest
- staged test module at 648 lines sits two lines under the plan-local checkpoint,
- which is worth watching but breaches nothing today.
- The staged work itself contains one concurrent effort, the project validation
- declaration feature in commit group 1 and its test-module split in group 2. That
- work is outside the Step 1 Markdown-check scope but is legitimately staged
- alongside it, is correctly separated into its own conventional groups, and the
- reviewer raises no objection to its inclusion.

### Writer instructions for step 1 markdown-check (exchange 1) (round 1)

Two changes are required before this step can reach commit readiness.

1. Settle `MD001`. Two readings are open and the reviewer cannot choose between
   them without taking a product decision, which is why no repair was made.

   The preferred fix is markdownlint parity: seed the level baseline from the
   first heading instead of from zero, so only a genuine increment of more than
   one between consecutive headings is reported. That restores `MD001` to zero,
   honors the design rule that `MD*` names carry markdownlint semantics, keeps
   the settled baseline exclusion true, and needs no specification change. The
   design sentence about a heading with "no preceding immediate parent" then
   reads as applying to headings after the first, which is how markdownlint
   behaves.

   If instead the stricter behavior is intended, then the identifier must move
   out of the `MD*` namespace to a new `LS*` rule, and both the design and plan
   must drop `MD001` from the measured-zero exclusion list and record its
   population of four so those findings get a baseline home. Whichever is
   chosen, add a rule test covering a document whose first heading is level two,
   because the current suite passes with the defect present.

2. Re-establish the walk result. Run `ghog day --force`, since a plain `ghog day`
   short-circuits and reports `cov=skipped` without executing the suite. If the
   three outliers persist, resolve them per `instructions/fix_slow_test.md` or
   accept them with `ghog exclude`, then restate the Step 1 evidence. The three
   are `test_spec_reviewer_acceptance_tdd.py::test_every_specification_type_routes_to_reviewer_with_exact_identity[design]`
   at 0.99s, and two cases in `test_spec_review_answer_cli_tdd.py` at 0.65s and
   0.56s. None is a Step 1 staged file, and the two marginal ones sit within
   0.15s of the floor, which the tool itself flags as flap-prone, so a re-run on
   a quieter machine may settle them without any change.

Also update the Step 1 validation record once both are resolved, because it
currently asserts a fully implemented verdict and a clean walk that the reviewer
could not reproduce.

Two accuracy notes that need no code change. The design still says two `MD032`
findings exist, naming the design-review transcript at line 264; that transcript
was repaired in `ff8581b` and the staged engine now finds only
`.claude/skills/humanizer/SKILL.md:260`, so Step 3's remediation list should drop
the transcript entry. And `MD038` currently reports 29 findings across the
repository, which the design expects Step 3 to repair rather than baseline; that
is a materially larger Step 3 task than "starts without a baseline entry"
suggests and is worth sizing now.

### Decision rationale for step 1 markdown-check (exchange 1) (round 1)

The disposition is changes-requested because one substantive defect remains and
one completion criterion could not be reproduced.

`MD001` is substantive by the request's own definition: correcting it changes
rule behavior and, on one of the two available readings, changes a rule
identifier and two specification documents. A substantive repair cannot validly
finish the workflow in the same round, and the reviewer did not repair it
because choosing between markdownlint parity and a new local identifier is a
product decision rather than an unambiguous in-step fix.

The readiness floor classifies as follows. Identity passes: the envelope,
umbrella, plan, step, round, and exchange occurrence all agree, and the
request-time index tree matched the working index exactly. Completeness is
partial: every planned file exists with the intended responsibilities, but the
rule engine does not yet satisfy the settled `MD001` contract. Validation and
coverage is unconfirmed: `fail=0`, `warn=0`, `xfail=0`, and `cov=100` are all
reproduced, while `outliers=3` and `exit=8` contradict the reported `outliers=0`
and `exit=0`. Staged attribution passes: 22 of 22 paths staged, no unstaged
overlap, and no reviewer patch to attribute. Unresolved findings stand at one
substantive and one readiness item. `a.commit` passes unamended.

The work is close and the engine is largely correct, which the independent
repository run supports: `LS001`, `LS002`, `MD024`, `LS003`, and `MD032` all
match expectation exactly, and classification reproduces the settled adapter
shapes. One rule and one piece of evidence separate this step from commit
readiness.

A commit-ready recommendation would never authorize a commit in any case; the
human commit choice remains the only authority for that.

### Final reviewer decision for step 1 markdown-check (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-24T17:19:03+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 markdown-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.markdown-check.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 markdown-check (round 2)

request_index_tree: 95c5368a33479a6bfdb66c09fb82cb7ace2c5662
resolved_validation_set:

- ghog day (sources: project, plan)
- ghog single tests/unit/tools/test_review_markdown_headings_tdd.py tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py (sources: plan)
- rg -n -e MD001 -e MD024 -e MD025 -e MD032 -e MD033 -e MD038 -e LS001 -e LS002 -e LS003 tools/markdown_check tests/unit/tools/markdown_check (sources: plan)

### Requestor assessment for step 1 markdown-check (round 2)

Step 1 remains fully implemented after accepting every round-1 finding.

MD001 now compares consecutive headings with `pairwise` and no longer invents a
level-0 predecessor for the first heading. A document or template fragment may
start at `##`; first-heading policy remains MD041 and is outside this catalog.
The existing hierarchy property oracle now uses the same consecutive-pair
contract, and a focused regression test covers a fragment beginning at level
two.

The reviewer-requested forced `ghog day` rerun completed without a testmon
short-circuit and reported `fail=0`, `warn=0`, `xfail=0`, `cov=100`,
`outliers=0`, `excluded=0`, and `exit=0`. No slow-test exclusion or repair was
needed.

Architecture and performance boundaries are unchanged. The validation record
now names the corrected MD001 semantics and the forced-run evidence.

### Implementation report for step 1 markdown-check (round 2)

- Replaced MD001's synthetic level-0 baseline with consecutive-heading
  comparison through `itertools.pairwise`.
- Added a focused rule test proving that a fragment may begin at level two.
- Updated the Hypothesis oracle to count only jumps between adjacent headings.
- Ran a forced full Groundhog day with 100 percent coverage and no failures,
  warnings, xfails, outliers, or exclusions.
- Refreshed the Step 1 validation record with the corrected semantics and
  reproducible forced-run result.
- Left all other Step 1 behavior and the five `a.commit` groups unchanged.

### Change summary for step 1 markdown-check (round 2)

All 22 reviewed working-tree paths remain staged. Round 1 changed only paths
already assigned to existing groups:

- `tools/markdown_check/rules.py` remains in the Markdown source model and rule
  engine feature group.
- `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py` and
  `tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py`
  remain in the Markdown engine test group.
- `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` remains in the final
  Step 1 validation-record group.

The root `a.commit` still names exactly the staged paths in dependency order;
its membership, grouping, conventional subjects, and descriptions remain
accurate. No commit has been made.

### Writer response for step 1 markdown-check (round 2)

Writer response: Accepted the round-1 recommendation without disagreement.

MD001 now follows markdownlint parity by comparing only consecutive headings.
The first-heading rule remains MD041 and is not implemented by this catalog. A
focused `##` fragment regression test and the property oracle both record that
decision.

The forced Groundhog rerun completed with `fail=0`, `warn=0`, `xfail=0`,
`cov=100`, `outliers=0`, `excluded=0`, and `exit=0`, so the earlier timing
outliers did not reproduce. The Step 1 validation record has been refreshed.

### Reviewer focus for step 1 markdown-check (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-24T17:26:38+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 markdown-check (exchange 1) (round 2)

Baseline index tree: 95c5368a33479a6bfdb66c09fb82cb7ace2c5662

Assessed index tree: 95c5368a33479a6bfdb66c09fb82cb7ace2c5662

### Implementation check for step 1 markdown-check (exchange 1) (round 2)

Result: Reviewer assessment result for Step 1: **Yes**. Both round 1 findings are
resolved, and each was verified by re-running the evidence rather than by
reading the report.

`MD001` now compares consecutive headings through `itertools.pairwise` and no
longer invents a level-zero predecessor, so a document may begin at any level and
first-heading policy stays with `MD041`, which this catalog deliberately does not
implement. The reviewer confirmed `MD041` appears nowhere under
`tools/markdown_check/`.

Re-running the staged engine over all 378 tracked Markdown files gives the
result the settled contract requires.

| Rule | Round 1 | Round 2 | Expected |
| --- | --- | --- | --- |
| `MD001` | 4 | 0 | 0 |
| `LS001` | 1 | 1 | 1 |
| `LS002` | 17 | 17 | 17 |
| `MD024` | 0 | 0 | 0 |
| `LS003` | 0 | 0 | 0 |
| `MD032` | 1 | 1 | 1 |

`MD001` is back to zero, so the settled baseline exclusion that names it
alongside `MD024` and `LS003` is true again, and the four template fragments no
longer produce findings that would have had no allowance. Every other rule is
unchanged, so the correction was surgical rather than broad. Classification also
holds at 156 adapters, as 118 frontmatter-description, 34 bounded-pointer, and
4 template-fragment, against 222 structured documents.

The fix is properly covered.
`test_md001_allows_a_fragment_to_start_below_level_one` asserts an empty result
for a fragment beginning at level two, and the Hypothesis oracle now derives its
expected count from `pairwise(levels)` instead of a synthetic predecessor, so the
property test would fail if the old behavior returned.

The walk claim is also reproduced. A forced `ghog day --force` completed in
1m 43.9s and reported `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0
exit=0`. The three duration outliers seen in round 1 did not recur, which
matches their profile at the time: none belonged to a Step 1 staged file and two
sat within 0.15 seconds of the 0.50 second floor.

Line budgets remain comfortable. `tools/markdown_check/rules.py` is 232 lines and
the two touched test modules are 130 and 45, all far below both the plan-local
650 checkpoint and the enforced 700 default.

Validation plan effects: The validation plan received exactly one staged change and no side effect.

`docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` is staged as a
modification in commit group 5, the trailing validation record the plan requires.
Its digest is `8a6cfc41a32ec0047f6740050ed700371ecfc3627a42b7b0e6738ed983003891`
both before and after the reviewer assessment, so executing the resolved
validation set produced no tracked validation side effect, no untracked
validation artifact, and no ignored artifact beyond the `a.ghog.*` run logs.

The writer refreshed its content this round to name the corrected `MD001`
semantics and the forced-run evidence. The reviewer reproduced both claims, so
the record now matches verifiable reality and needs no further change.

### Pre-repair mandatory checks and coverage for step 1 markdown-check (exchange 1) (round 2)

Validation state was captured before assessment and compared after it, and the
two are identical.

Captured path set: `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md`.

Before assessment the tracked digest was
`8a6cfc41a32ec0047f6740050ed700371ecfc3627a42b7b0e6738ed983003891` at index tree
`95c5368a33479a6bfdb66c09fb82cb7ace2c5662`, with no untracked and no ignored
validation files. After running the full resolved validation set, including the
forced walk, the digest, index tree, and both empty lists are unchanged.

No repair was attempted, so no pre-repair blob was recorded and no reviewer patch
was attributed. The retained manifest carries identical baseline and assessed
index trees with empty recorded-blob and repair-path lists.

### Resolved validation set and sources for step 1 markdown-check (exchange 1) (round 2)

The reviewer ran the union of the request validation set and the current
resolver set. The two agree, so the union adds nothing beyond the request.

- `ghog day`, sources project and plan. Run forced to avoid the testmon
  short-circuit that made round 1 unverifiable. Completed in 1m 43.9s and
  reported `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` across
  the check, affected and full phases. The three duration outliers observed in
  round 1 did not recur.
- The Step 1 focused `ghog single` command over the review-heading, source-model,
  rules and rule-property modules, source plan. Reported no failures and no
  interaction suspects.
- The Step 1 `rg` identifier contract, source plan. Matched all nine identifiers
  in `tools/markdown_check/rules.py` and ten occurrences in the rules test
  module, satisfying the evaluator-and-test contract.

Beyond the declared set the reviewer executed the staged engine directly over
all 378 tracked Markdown files to compare rule output against the settled
contract, and ran it once against the new code-review transcript. Both runs are
evidence for this assessment and mutated nothing.

No resolver drift was observed between the request-time set and the current set.

### Resolver drift and direction for step 1 markdown-check (exchange 1) (round 2)

No resolver drift.

The request-time resolved validation set carries the same three commands as the
current resolution, with the same source labels: `ghog day` from project and
plan, the Step 1 focused `ghog single` command from the plan, and the Step 1
`rg` identifier contract from the plan. Nothing was added, dropped or
relabelled.

The request-time index tree `95c5368a33479a6bfdb66c09fb82cb7ace2c5662` also
matches the working index tree captured before assessment, so the review subject
did not move under the request.

### Repository state around validation for step 1 markdown-check (exchange 1) (round 2)

The repository is byte-identical before and after this review.

- Index tree: `95c5368a33479a6bfdb66c09fb82cb7ace2c5662` at request time, at
  baseline capture, and again after assessment.
- Applicable umbrella digest:
  `4a8ea7e8ec8710a744fa138934f4093cbf544b7f16447e3a27b11eb8f597268d` before and
  after the implementation-check result, so the umbrella boundary was not
  crossed.
- Validation-state path set: one tracked file at digest
  `8a6cfc41a32ec0047f6740050ed700371ecfc3627a42b7b0e6738ed983003891` before and
  after, with empty untracked and ignored lists both times.
- Staged set: 22 paths before and after, with no reviewer patch staged and no
  pre-existing unstaged overlap left behind.

The only filesystem effects are ignored root artifacts: the reviewer's own
`a.code-reviewer.*` inputs, the retained manifest at
`a.code-review-evidence.v0.11.0.markdown-check.step-1.json`, and the `a.ghog.*`
logs from executing the declared validation set. None is tracked or staged.

One untracked non-ignored path exists: the protocol-created code-review
transcript `docs/v0.11.0/review.code.v0.11.0.markdown-check.md`. It is created
by the exchange rather than by the reviewer, and the staged engine finds no
catalog findings in it.

### Repair inventory for step 1 markdown-check (exchange 1) (round 2)

Repairs made:

- No repairs were made and nothing was staged by the reviewer.
- Round 1's findings were corrected by the writer, and this round verified them.
- There was nothing left that was both safe and unambiguous to repair in step.
- The repository is unchanged by this review. The index tree is
- `95c5368a33479a6bfdb66c09fb82cb7ace2c5662` at request time, at baseline capture,
- and after assessment. The applicable umbrella digest is
- `4a8ea7e8ec8710a744fa138934f4093cbf544b7f16447e3a27b11eb8f597268d` before and
- after, so the umbrella boundary was not crossed. The validation-plan digest is
- unchanged at `8a6cfc41a32ec0047f6740050ed700371ecfc3627a42b7b0e6738ed983003891`,
- with no tracked validation side effect and no untracked or ignored validation
- artifact beyond the ordinary `a.ghog.*` run logs.

Paths staged:

- docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md
- `tests/unit/tools/markdown_check/__init__.py`
- `tests/unit/tools/markdown_check/test_rule_properties/__init__.py`
- tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py
- `tests/unit/tools/markdown_check/test_rules/__init__.py`
- tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py
- `tests/unit/tools/markdown_check/test_source_model/__init__.py`
- tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py
- tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py
- tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py
- tests/unit/tools/test_instruction_structure/test_instruction_structure_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_answers_tdd.py
- tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_lifecycle_tdd.py
- tests/unit/tools/test_review_requestor_instruction/test_review_requestor_instruction_tdd.py
- tools/code_review_request.py
- tools/code_review_validation.py
- `tools/markdown_check/__init__.py`
- tools/markdown_check/classifier.py
- tools/markdown_check/models.py
- tools/markdown_check/rules.py
- tools/markdown_check/source.py
- tools/review_markdown_headings.py

### Commit plan assessment for step 1 markdown-check (exchange 1) (round 2)

`a.commit` is accurate and needs no amendment.

Its five groups name exactly the 22 staged paths, with nothing staged but
unplanned and nothing planned but unstaged. All five subjects remain
conventional and correctly typed: two `feat`, two `test`, and one `docs`.

Round 2 touched only paths already assigned to existing groups.
`tools/markdown_check/rules.py` stays in the Markdown source-model and rule
engine feature group, the two Markdown engine test modules stay in the engine
test group, and the refreshed Step 1 record stays in the trailing validation
group. Membership, grouping, dependency order, scope, and descriptions therefore
all still match the staged work.

The group 3 and group 4 descriptions remain truthful after the correction, since
they describe the rule catalog and its coverage generically rather than
restating the superseded `MD001` behavior. The group 5 record was refreshed by
the writer and now names the corrected semantics and the forced-run evidence,
which the reviewer reproduced.

The reviewer did not amend the plan and made no staged change of any kind.

### Findings and boundaries for step 1 markdown-check (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 markdown-check (exchange 1) (round 2)

No changes are requested. Step 1 is complete against the plan and verified.

Before committing, note that group 5 stages the Step 1 validation record. The
writer refreshed it this round to name the corrected `MD001` semantics and the
forced-run evidence, and the reviewer reproduced both, so it is accurate as
staged.

Three items to carry into later steps, none of which affects this commit.

1. Size the `MD038` work before Step 3 starts. The engine reports 29 findings
   across the repository and the design expects Step 3 to repair rather than
   baseline them.
2. Bootstrap the Step 3 baseline from the implemented checker, which reports
   `MD033` at 82 rather than the requirement's approximate 61. Q02 already
   settles that the checker is authoritative.
3. Drop the stale design sentence naming two `MD032` findings. The design-review
   transcript was repaired in `ff8581b` and only
   `.claude/skills/humanizer/SKILL.md:260` remains, which Step 3 repairs.

A commit-ready recommendation is advisory and authorizes nothing. The human
commit choice remains the only authority to commit.

### Decision rationale for step 1 markdown-check (exchange 1) (round 2)

The disposition is an advisory commit-ready recommendation. It does not
authorize a commit; only the human commit choice does that.

The readiness floor now passes on all six results. Identity passes: envelope,
umbrella, plan, step, round, and exchange occurrence agree, and the request-time
index tree `95c5368a33479a6bfdb66c09fb82cb7ace2c5662` matched the working index
before and after assessment. Completeness passes: every planned Step 1 file
exists with its intended responsibility, and the rule engine now satisfies the
settled `MD001` contract that round 1 found broken. Validation and coverage
passes: the forced walk reports `fail=0 warn=0 xfail=0 cov=100 outliers=0
excluded=0 exit=0`, and the focused suite and `rg` identifier contract both pass.
Staged attribution passes: 22 of 22 paths staged with no reviewer patch to
attribute and no unstaged overlap. Unresolved findings are empty for Step 1.
`a.commit` passes unamended.

No repair was made this round, so nothing finished in the same round that
changed the work. The round 1 corrections were made by the writer and verified
here, which is the intended shape: a substantive change and its verification sit
in different rounds.

The recommendation rests on reproduced evidence rather than the implementation
report. `MD001` moved from four findings to zero when the reviewer re-ran the
staged engine over all 378 tracked Markdown files, every other rule held its
previous value, the regression test and property oracle both encode the corrected
semantics, and the forced walk that failed to reproduce last round now reports a
clean result. The three earlier duration outliers did not recur and were never in
Step 1 files.

Three observations are carried into Step 3 rather than held against Step 1: the
`MD038` repair scale, the authoritative `MD033` count of 82, and the stale
two-finding `MD032` sentence in the design.

### Final reviewer decision for step 1 markdown-check (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-08-24T17:29:48+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-25T09:27:53+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 markdown-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.markdown-check.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 markdown-check (round 1)

request_index_tree: 3f6b8230c4f17d36c66bc4e1dd799c0adfd16115
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/acceptance/markdown_check/test_markdown_check_acceptance/test_markdown_check_acceptance_tdd.py tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py (sources: plan)
- rg -n -e record_failure.markdown -e markdown-check.bat check.bat (sources: plan)
- rg -n -e Markdown.checker -e MD032 -e MD033 -e MD038 -e MD050 -e LS003 -e markdownlint-baseline README.md wiki/README.md wiki/reference/markdown-checker.md (sources: plan)
- pytest tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py --no-cov -p no:testmon -q (sources: request)

### Requestor assessment for step 3 markdown-check (round 1)

Step 3 is fully implemented against its amended plan. The staged work repairs
the remaining MD032 and MD038 corpus findings, adds zero-debt MD050 enforcement,
connects the direct checker to `check.bat`, adds repository acceptance coverage,
and publishes the checker reference.

The final detached Groundhog day completed 2,001 tests with 100 percent
coverage, no duration outliers, and exit 0. The direct Markdown checker also
returns zero after the transcript repair and validation update. Production
modules remain below the plan line limits, and the rule engine continues to use
one shared source model rather than rule-specific file reads.

Review MD050 closely: underscore-delimited strong prose must fail, while
asterisk strong style, escaped delimiters, inline code, fenced code, and every
code-delimited `__init__.py` path must pass.

### Implementation report for step 3 markdown-check (round 1)

The implementation adds `MD050` to the closed policy catalog and runner. The
source model now retains prose lines after fence and inline-code masking, and
the pure MD050 evaluator reports underscore-delimited strong style without
interpreting code content as prose. The fence classifier also recognizes
list-indented fenced blocks.

The tracked Step 1 review transcript now wraps all ten `__init__.py` list paths
in backticks. MD032 and genuine MD038 defects are repaired without baseline
entries. The baseline remains limited to reviewed LS001, LS002, and MD033 debt.

`check.bat` invokes `markdown-check.bat` once and records failures under the
`markdown` component. Acceptance tests cover the public launcher, shared gate,
adapters, overlapping rules, configuration errors, baseline growth and shrink,
zero-debt policy, MD038 exceptions, asterisk strong style, and a code-delimited
`__init__.py` example. Root and wiki navigation link the new reference page.

### Change summary for step 3 markdown-check (round 1)

The staged index contains these 41 paths:

- `.claude/skills/humanizer/SKILL.md`
- `.vscode/settings.json`
- `README.md`
- `check.bat`
- `docs/design.v0.1.0.pw_handoff.md`
- `docs/v0.11.0/design.v0.11.0.markdown-check.md`
- `docs/v0.11.0/draft.v0.11.0.markdown-check.md`
- `docs/v0.11.0/draft.v0.11.0.review-mode.md`
- `docs/v0.11.0/feature-request.v0.11.0.markdown-check.md`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md`
- `docs/v0.11.0/plan.v0.11.0.markdown-check.md`
- `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md`
- `docs/v0.11.0/plan.v0.11.0.review-exchange-core.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.code.v0.11.0.markdown-check.md`
- `docs/v0.11.0/review.code.v0.11.0.review-exchange-core.md`
- `docs/v0.11.0/review.design-specification.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md`
- `docs/v0.11.0/review.plan.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.plan.v0.11.0.markdown-check.md`
- `instructions/group-commits-msg.md`
- `instructions/prepare-release-notes.md`
- `instructions/prepare-release.md`
- `tests/acceptance/__init__.py`
- `tests/acceptance/markdown_check/__init__.py`
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/__init__.py`
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/test_markdown_check_acceptance_tdd.py`
- `tests/acceptance/markdown_check/test_shared_gate/__init__.py`
- `tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py`
- `tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py`
- `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py`
- `tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py`
- `tools/markdown_check/models.py`
- `tools/markdown_check/policy.py`
- `tools/markdown_check/rules.py`
- `tools/markdown_check/runner.py`
- `tools/markdown_check/source.py`
- `wiki/README.md`
- `wiki/reference/markdown-checker.md`
- `wiki/reference/templates.md`

The root `a.commit` contains six groups in dependency order:

1. `feat(markdown-check): enforce strong style`
2. `fix(markdown-check): clear Markdown debt`
3. `feat(markdown-check): wire shared gate`
4. `test(markdown-check): cover gate rollout`
5. `docs(markdown-check): publish checker reference`
6. `docs(markdown-check): record step 3 validation`

### Human guidance and writer response for step 3 markdown-check (round 1)

Human guidance:

Pay particular attention to MD050 parity and the repaired Step 1 transcript.
Every `__init__.py` list path must be code-delimited, underscore strong prose
must report MD050, and inline or fenced code must remain exempt. Also verify
that the request and transcript describe Step 3 only and do not claim a Step 2
review occurred.

Writer response: There is no earlier Step 3 reviewer answer. After the premature commit gate, the
human identified two omissions: the existing transcript had unquoted
`__init__.py` paths that trigger MD050, and Step 3 had not entered code review.
Both issues are addressed before this round: MD050 is now implemented and the
transcript paths are repaired.

The missing Step 2 pre-commit review is not represented as completed or repaired
by this Step 3 request. Step 2 was already committed, so its original staged
review subject no longer exists. This request covers only the exact staged Step
3 implementation.

### Reviewer focus for step 3 markdown-check (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-25T09:40:39+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 markdown-check (exchange 1) (round 1)

Baseline index tree: 3f6b8230c4f17d36c66bc4e1dd799c0adfd16115

Assessed index tree: 3f6b8230c4f17d36c66bc4e1dd799c0adfd16115

### Implementation check for step 3 markdown-check (exchange 1) (round 1)

Result: Reviewer assessment result for Step 3: **Yes**. Every claim was reproduced
rather than accepted, and the effort's final step is complete.

The decisive check is the baseline itself. Running the shipped checker against
an empty baseline gives the repository's true residual set, and it matches the
tracked baseline exactly.

| Rule | Empty-baseline run | Tracked allowance |
| --- | --- | --- |
| `LS001` | 1 | 1 |
| `LS002` | 17 | 17 |
| `MD033` | 7 | 7 |
| `MD001`, `MD024`, `MD025`, `MD032`, `MD038`, `MD050`, `LS003` | 0 | none |

Twenty-five findings measured, twenty-five allowed, nothing more. That is
exactly the Q02 contract: the baseline records reviewed checker output rather
than an estimate, and every zero-debt rule was repaired instead of grandfathered.
`test_zero_debt_markdown_rules_have_no_baseline_entries` locks that in by
asserting the `MD*` allowance set equals `{"MD033"}`.

Both public entry points work. `markdown-check.bat` and
`python -m tools.markdown_check.cli` each exit 0 against the current repository.
The shared gate wires the launcher through the same `record_failure markdown
<status>` pattern every other check uses, with `markdown_status` initialised at
line 17 and cleared in `:check_unset` at line 208, so the new step follows the
established gate lifecycle rather than inventing one.

The forced walk reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0
exit=0` and prints `Objective reached`, completing in 1m 56.7s. The plan's two
`rg` contracts both match: the gate wiring in `check.bat`, and the catalog and
baseline terms across `README.md`, `wiki/README.md`, and
`wiki/reference/markdown-checker.md`.

The reference page carries the full catalog with per-rule sections for `MD032`,
`MD038`, and `MD050`, states that `MD024` and `MD025` are mandatory and that a
configuration attempting to disable either fails before inventory evaluation,
and documents the invocation model, finding and stream contract, and versioned
baseline. `MD041` is absent, consistent with first-heading policy staying out of
this catalog.

The umbrella change is one line: row 7 flips from `pending` to `completed` with
its requirement and validation-plan paths, matching rows 1 to 6. That is the
writer-owned final-step action `implementation-check` mandates once the
validation plan reads `Yes, it is implemented.`, which it now does with all
three steps at Yes. It is not a boundary violation, and the reviewer confirmed
the applicable umbrella digest did not move during this assessment.

Validation plan effects: The validation plan received exactly one staged change and no side effect.

`docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md` is staged as a
modification in the trailing commit group. Its digest is
`bb1ace1f2d861726b8023a0befeb3ca0c5d71bba266dda6203371bd12cc6827a` both before
and after the reviewer assessment, so executing the resolved validation set
produced no tracked validation side effect, no untracked validation artifact,
and no ignored artifact beyond the `a.ghog.*` run logs.

Its content now records Step 3 as fully implemented and carries the
document-level status `Yes, it is implemented.` with all three step sections
reading `Yes`. That flip is the precondition `implementation-check` requires
before the matching umbrella row may be completed, and the staged umbrella diff
performs exactly that single row change.

### Pre-repair mandatory checks and coverage for step 3 markdown-check (exchange 1) (round 1)

Validation state was captured before assessment and compared after it, and the
two are identical.

Captured path set: `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md`.

Before assessment the tracked digest was
`bb1ace1f2d861726b8023a0befeb3ca0c5d71bba266dda6203371bd12cc6827a` at index tree
`3f6b8230c4f17d36c66bc4e1dd799c0adfd16115`, with no untracked and no ignored
validation files. After running the full resolved validation set, including the
forced walk and both launcher invocations, the digest, index tree, and both
empty lists are unchanged.

No repair was attempted, so no pre-repair blob was recorded and no reviewer patch
was attributed. The retained manifest carries identical baseline and assessed
index trees with empty recorded-blob and repair-path lists.

### Resolved validation set and sources for step 3 markdown-check (exchange 1) (round 1)

The reviewer ran the union of the request validation set and the current
resolver set. The two agree, so the union adds nothing beyond the request.

- `ghog day`, source project. Run forced to avoid the testmon short-circuit.
  Completed in 1m 56.7s reporting `fail=0 warn=0 xfail=0 cov=100 outliers=0
  excluded=0 exit=0` and printing `Objective reached`.
- The Step 3 acceptance `ghog single` command over the checker-acceptance and
  shared-gate modules, source plan. Covered by the forced walk, which runs the
  complete suite.
- `rg -n -e record_failure.markdown -e markdown-check.bat check.bat`, source
  plan. Matched the launcher invocation at line 125 and the
  `record_failure markdown` call at line 131.
- The documentation `rg` contract over `README.md`, `wiki/README.md`, and
  `wiki/reference/markdown-checker.md`, source plan. Matched in all three files.
- `pytest tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py
  tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py --no-cov
  -p no:testmon -q`, source request. Covered by the forced walk.

Beyond the declared set the reviewer ran `markdown-check.bat` and
`python -m tools.markdown_check.cli`, which both exit 0; ran the checker once
against an empty baseline in the scratch directory to establish the true
residual set; and exercised the `MD050` evaluator against ten constructed
boundary cases. None of those runs mutated the repository.

No resolver drift was observed between the request-time set and the current set.

### Resolver drift and direction for step 3 markdown-check (exchange 1) (round 1)

No resolver drift.

The request-time resolved validation set carries five commands and the current
resolution produces the same five with the same source labels: `ghog day` from
the project, the Step 3 acceptance `ghog single` command, the gate-wiring `rg`
contract, and the documentation `rg` contract from the plan, plus the focused
policy and rules `pytest` command from the request. Nothing was added, dropped,
or relabelled.

The request-time index tree `3f6b8230c4f17d36c66bc4e1dd799c0adfd16115` also
matches the working index tree captured before assessment, so the review subject
did not move under the request.

### Repository state around validation for step 3 markdown-check (exchange 1) (round 1)

The repository is byte-identical before and after this review.

- Index tree: `3f6b8230c4f17d36c66bc4e1dd799c0adfd16115` at request time, at
  baseline capture, and again after assessment.
- Applicable umbrella digest:
  `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and
  after the implementation-check result. The staged single-row umbrella change
  was made by the writer before the request and is the mandated final-step
  completion action; the reviewer did not move it.
- Validation-state path set: one tracked file at digest
  `bb1ace1f2d861726b8023a0befeb3ca0c5d71bba266dda6203371bd12cc6827a` before and
  after, with empty untracked and ignored lists both times.
- Staged set: 41 paths before and after, with no reviewer patch staged and no
  pre-existing unstaged overlap left behind.

The only filesystem effects are ignored root artifacts: the reviewer's own
`a.code-reviewer.*` inputs, the retained manifest at
`a.code-review-evidence.v0.11.0.markdown-check.step-3.json`, and the `a.ghog.*`
logs from executing the declared validation set. The empty baseline used to
establish the true residual set was written to the session scratch directory
outside the repository, so no tracked or ignored repository file was added for
it.

### Repair inventory for step 3 markdown-check (exchange 1) (round 1)

Repairs made:

- No repairs were made and nothing was staged by the reviewer.
- Every claim in the request reproduced on first check, so there was nothing both
- safe and unambiguous left to repair in step.
- The repository is unchanged by this review. The index tree is
- `3f6b8230c4f17d36c66bc4e1dd799c0adfd16115` at request time, at baseline capture,
- and after assessment. The applicable umbrella digest is
- `020d1d67f9a3dca50a2651e6dd7b6717b3f1a7ef5521c5eaf4a27de6e2c3b79c` before and
- after the implementation-check result, so the umbrella boundary was not crossed
- by the reviewer. The validation-plan digest is unchanged at
- `bb1ace1f2d861726b8023a0befeb3ca0c5d71bba266dda6203371bd12cc6827a`, with no
- tracked validation side effect and no untracked or ignored validation artifact
- beyond the ordinary `a.ghog.*` run logs.

Paths staged:

- `.claude/skills/humanizer/SKILL.md`
- `.vscode/settings.json`
- `README.md`
- `check.bat`
- `docs/design.v0.1.0.pw_handoff.md`
- `docs/v0.11.0/design.v0.11.0.markdown-check.md`
- `docs/v0.11.0/draft.v0.11.0.markdown-check.md`
- `docs/v0.11.0/draft.v0.11.0.review-mode.md`
- `docs/v0.11.0/feature-request.v0.11.0.markdown-check.md`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/plan.v0.11.0.code-review-requestor.validation.md`
- `docs/v0.11.0/plan.v0.11.0.markdown-check.md`
- `docs/v0.11.0/plan.v0.11.0.markdown-check.validation.md`
- `docs/v0.11.0/plan.v0.11.0.review-exchange-core.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.code.v0.11.0.markdown-check.md`
- `docs/v0.11.0/review.code.v0.11.0.review-exchange-core.md`
- `docs/v0.11.0/review.design-specification.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md`
- `docs/v0.11.0/review.plan.v0.11.0.code-review-requestor.md`
- `docs/v0.11.0/review.plan.v0.11.0.markdown-check.md`
- `instructions/group-commits-msg.md`
- `instructions/prepare-release-notes.md`
- `instructions/prepare-release.md`
- `tests/acceptance/__init__.py`
- `tests/acceptance/markdown_check/__init__.py`
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/__init__.py`
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/test_markdown_check_acceptance_tdd.py`
- `tests/acceptance/markdown_check/test_shared_gate/__init__.py`
- `tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py`
- `tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py`
- `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py`
- `tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py`
- `tools/markdown_check/models.py`
- `tools/markdown_check/policy.py`
- `tools/markdown_check/rules.py`
- `tools/markdown_check/runner.py`
- `tools/markdown_check/source.py`
- `wiki/README.md`
- `wiki/reference/markdown-checker.md`
- `wiki/reference/templates.md`

### Commit plan assessment for step 3 markdown-check (exchange 1) (round 1)

`a.commit` is accurate and needs no amendment.

Its six groups name exactly the 41 staged paths, with nothing staged but
unplanned and nothing planned but unstaged. All six subjects are conventional
and correctly typed: three `feat` and `fix` implementation groups, one `test`,
and two `docs`.

The dependency order is right for a rollout step. `MD050` enforcement lands
first, then the corpus debt it and the other rules require, then the shared-gate
wiring that depends on a clean corpus, then the acceptance coverage of that
wiring, then the published reference, and finally the Step 3 validation record
as the trailing durable evidence.

Group membership matches the work each subject describes. The umbrella row flip
travels with the validation record rather than with the implementation groups,
which is correct because it is the completion bookkeeping that the validation
status flip authorizes.

The reviewer did not amend the plan and made no staged change of any kind.

### Findings and boundaries for step 3 markdown-check (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 3 markdown-check (exchange 1) (round 1)

Human guidance: Pay particular attention to MD050 parity and the repaired Step 1 transcript.
Every `__init__.py` list path must be code-delimited, underscore strong prose
must report MD050, and inline or fenced code must remain exempt. Also verify
that the request and transcript describe Step 3 only and do not claim a Step 2
review occurred.

Guidance response: All three guidance items were checked directly, and all three hold.

**MD050 parity.** The reviewer exercised the evaluator against ten constructed
cases covering every boundary the guidance names, and each behaved as specified.

| Case | Expected | Result |
| --- | --- | --- |
| `__bold text__` in prose | reports | reports |
| Bare `__init__.py` in prose | reports | reports |
| Bare path in a list item | reports | reports |
| `**bold text**` asterisk strong | exempt | exempt |
| Underscore path inside inline code | exempt | exempt |
| Underscore path inside a fenced block | exempt | exempt |
| Escaped delimiters | exempt | exempt |
| Code-delimited path in a list item | exempt | exempt |
| `_italic_` single-underscore emphasis | exempt | exempt |
| `snake_case_name` intraword underscores | exempt | exempt |

The pattern `(?<![\\_])__(?=\S).+?(?<=\S)__(?!_)` earns those last two exemptions
deliberately: the lookbehind rejects an escaped or run-on delimiter and the
trailing lookahead rejects a longer underscore run, so intraword and emphasis
forms never reach the finding path. Masking happens in the source model, so
`prose_lines` excludes fenced and inline code before the rule ever sees a line,
which is why code content cannot be misread as prose.

**The repaired Step 1 transcript.** Every `__init__.py` mention in
`docs/v0.11.0/review.code.v0.11.0.markdown-check.md` is code-delimited: 19
occurrences in total, 19 wrapped in backticks, including the ten list paths
across both Step 1 rounds at lines 280 to 295 and 734 to 749. The whole-corpus
run confirms the consequence, with `MD050` reporting zero findings and holding no
baseline allowance.

**Step 3 scope and the absent Step 2 review.** The request and the transcript
describe Step 3 only. `Step 2` appears in the transcript exactly twice outside
this guidance block, both inside the writer's own response, and it states plainly
that the missing Step 2 pre-commit review "is not represented as completed or
repaired by this Step 3 request" because Step 2 was already committed and its
staged subject no longer exists. No section claims a Step 2 review occurred, and
no evidence in this round is attributed to one.

The reviewer records the gap as a fact rather than a Step 3 defect: Step 2 of
this plan was committed without passing through the code-review exchange. Nothing
in the current staged work can repair that, and the honest disclosure is the
correct handling. Whether the effort needs any retrospective action for Step 2 is
a human decision that belongs at the commit gate, not a reviewer judgment.

### Writer instructions for step 3 markdown-check (exchange 1) (round 1)

No changes are requested. Step 3 is complete against its plan and verified.

Two facts to carry to the commit gate, neither of which is a defect in the
staged work.

1. Step 2 of this plan was committed without passing through the code-review
   exchange. This request discloses that plainly and does not claim otherwise,
   and nothing in the staged Step 3 work can repair it because Step 2's staged
   subject no longer exists. Whether the effort needs any retrospective action
   is a human decision.
2. This step completes the effort. The staged umbrella row 7 flip to
   `completed` is the mandated final-step bookkeeping and depends on the
   validation plan's `Yes, it is implemented.` status, which is also staged.
   Committing the two together keeps that pair consistent.

A correction to this reviewer's earlier Step 1 round 2 notes, so the record is
accurate: the figures of 82 `MD033` findings and 29 `MD038` findings were
wrong. They came from calling the rule evaluators directly and bypassing policy
loading, so `MD033` counted the `img` elements the configuration allows. Under
the shipped runner the true values are 7 and 0. Q02's decision to make the
implemented checker the sole authority for baseline records is exactly what
guards against that class of error.

A commit-ready recommendation is advisory and authorizes nothing. The human
commit choice remains the only authority to commit.

One forward-looking note about `MD050` and the review tooling, found while
preparing this answer. The code-review answer renderer emits the caller's staged
path inventory verbatim, and the natural way to produce that inventory is
`git diff --cached --name-only`, which yields bare paths. Any step whose staged
set contains an `__init__.py` file will therefore introduce `MD050` findings
into its own review transcript unless the caller code-delimits each path first.
This reviewer hit exactly that: the first render of this answer would have added
four `MD050` findings to the transcript at the four staged `__init__.py` paths.
They were code-delimited before publication and the merged transcript now
reports no findings under any rule.

Since `MD050` carries no baseline allowance by design, that mistake turns the
shared gate red on the next run. The requestor already code-delimits paths in
its own change summary. Worth stating in the reference page's `MD050` section
that review-artifact authors must code-delimit file paths, so the obligation is
documented rather than rediscovered.

### Decision rationale for step 3 markdown-check (exchange 1) (round 1)

The disposition is an advisory commit-ready recommendation. It does not
authorize a commit; only the human commit choice does that.

All six readiness-floor results pass. Identity passes: envelope, umbrella, plan,
step, round, and exchange occurrence agree, and the request-time index tree
matched the working index before and after assessment. Completeness passes: the
catalog now carries `MD050`, the corpus debt it and the other zero-debt rules
require is repaired, the gate is wired, acceptance coverage exists, and the
reference is published. Validation and coverage passes: the forced walk reports
`cov=100` with no failures, warnings, xfails, outliers, or exclusions and exits
0, and both launcher forms exit 0. Staged attribution passes: 41 of 41 paths
staged with no reviewer patch and no unstaged overlap. Unresolved findings are
empty. `a.commit` passes unamended.

The recommendation rests on reproduced evidence. The strongest single check is
the empty-baseline run: the repository's true residual set is 1 `LS001`, 17
`LS002`, and 7 `MD033` findings, and the tracked baseline allows exactly those
25 and nothing else. Every rule the design requires to start at zero reports
zero, and an acceptance test now asserts that the `MD*` allowance set is
`{"MD033"}`, so the zero-debt contract cannot silently erode later.

The human guidance was answered on its own terms. `MD050` behaved correctly on
all ten boundary cases the reviewer constructed, the Step 1 transcript has all
19 `__init__.py` mentions code-delimited, and neither the request nor the
transcript claims a Step 2 review occurred.

No repair was made this round, so nothing finished in the same round that
changed the work.

### Final reviewer decision for step 3 markdown-check (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 1 by human - Step 3 - human-confirmation

- Recorded: 2026-08-25T09:50:16+02:00
- Exchange: code/code/v0.11.0/markdown-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.markdown-check.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->
