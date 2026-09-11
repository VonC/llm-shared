# Specification review transcript for v0.11.0

- Exchange: specification/plan/v0.11.0/commit-plan-check
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-08-26T09:48:53+02:00
- Exchange: specification/plan/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Outcome: request

### Review identity for plan commit-plan-check (round 1)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Review round: 1

### Requestor assessment for plan commit-plan-check (round 1)

The implementation plan is ready for an independent round-1 specification
review. No additional implementation-only question is currently missing: the
five placed questions cover checker module granularity, staged-inventory
compatibility, requestor gate placement, growth control for the existing
risk-band rendering test, and acceptance fixture extraction timing. Each
question has complete options, pros and cons, a recommended answer, and an
explicit acceptance reason. No reviewer wording suggestion exists before this
first round.

### Change summary for plan commit-plan-check (round 1)

Created the four-step implementation plan and aligned validation skeleton from
the settled requirement and design. Added explicit file-based IO cost
clarifications to the feature request, design, plan, and validation skeleton.
Recorded physical line baselines, risk-band guidance, shared groundhog command
checklists, the Step 0 decision, final acceptance coverage, and five
implementation-plan open questions.

### Writer response for plan commit-plan-check (round 1)

Writer response: This is the initial review request, so there is no earlier reviewer feedback to
accept or dispute. Please verify that the four implementation steps preserve
the settled design, that every modified or new file and test boundary is
accounted for, and that the recommended answers minimize unnecessary file
growth without weakening validation or acceptance evidence.

### Reviewer focus for plan commit-plan-check (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer

- Recorded: 2026-08-26T09:56:40+02:00
- Exchange: specification/plan/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Outcome: answer

### Reviewer assessment for plan commit-plan-check round 1

The plan is structurally sound and unusually well grounded in fact. Every
physical line baseline it records is exact, and every API claim it makes is
true as written. The four-step order is correct: inventory parity must precede
the checker, the checker must precede the requestor gate, and instruction
wiring plus real-repository acceptance evidence must come last. The step
boundaries preserve the settled design, and the deferred list matches the
design's deferral of `--root-a-commit --dry-run`.

Verification performed against the working tree rather than the plan's prose:

- Baselines confirmed exact for all fifteen named files, including the two
  that drive risk-band guidance: `tools/code_review_request.py` at 497 and
  `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
  at exactly 550.
- `validate_commit_plan(blocks, staged_paths)` is side-effect-free and accepts
  `list[str] | tuple[str, ...]`, so the shared inventory tuple passes without
  conversion.
- `_staged_paths` runs exactly `("diff", "--cached", "--name-only",
  "--no-renames", "-z")` and is absent from the module `__all__`, confirming it
  is private today.
- The workflow test both calls `_staged_paths` directly and monkeypatches it,
  which is decisive evidence for the Q02 recommendation.
- `_render_from_arguments` already calls `capture_index_tree(root)` once, so
  the Step 3 sequence is a small addition at an existing seam.
- All six `CodeReviewRoundInput(` construction sites use keyword arguments.
- The reviewer instruction really does classify "the six readiness-floor
  results" with `a.commit` as one of them, so the Step 4 wording is accurate.

Two decisions with real implementation consequence are not expressed as
questions, and one of them is actively steered toward the wrong seam by a
"confirmed technical fact". That is the substance of this round.

The first concerns plan parsing. Step 2 says the service must "parse once with
`interactive=False`" but never names the parsing boundary, while the confirmed
facts highlight `git_batch_commit_workflow._read_and_parse_content`. That
helper is a committing-workflow function that reads the clipboard when no
filename is given, emits `LOGGER.info` progress lines, and raises one
`GitBatchCommitError` for a missing file, an empty file, and an OS read
failure alike. The design requires those three conditions to become three
distinct outcomes: `missing-plan` at status three, `empty-plan` at status
three, and an operational failure at status two. Reusing that helper forces the
checker to recover the distinction by matching exception message text, and it
makes a read-only command depend on the committing module that Step 1 was
extracting away from. The public, content-in/blocks-out
`git_batch_commit_parsing.parse_clipboard_content` is exported and is the
correct seam.

The second concerns the typed request input. Step 3 adds a commit-plan result
to `CodeReviewRoundInput` without deciding whether the field is required and
whether `__post_init__` rejects a non-ready result. That choice decides
whether the public `render_code_review_request` can still emit a request
carrying non-ready evidence, which is precisely the enforcement boundary the
design assigns to this module. It also determines how much the 550-line
risk-band test file must change, so it is entangled with Q04 and should be
settled beside it.

Beyond the two missing questions, Step 4's acceptance coverage is narrower
than the design's acceptance table, and Step 2's test list does not pin the
structured payload the design fixes at `schema_version` 1. Both are concrete
and small, but they are the evidence the feature is judged by, so they belong
in the plan rather than in implementer discretion.

The five existing questions are well formed. Each has materially distinct
options, honest consequences, and a recommendation that follows from the
confirmed facts. I agree with all five recommended answers. No question is
redundant, unclear, or outside the plan's scope, and none reopens a settled
requirement or design choice.

### Question verdicts for plan commit-plan-check round 1

## Verdict on Q01 initial checker module granularity

Agree with Option 1A, keep one `tools/commit_plan_check.py`.

The question is well posed and the options are materially distinct. The
recommendation follows from the confirmed facts: the advisory estimate is 360
lines, the repository ceiling is 650, and the plan already names an exact
split destination and trigger. Option 1C would create a package for a single
focused command and multiply initializers and navigation for no present
benefit.

One caveat the writer should record rather than re-decide: if Q06 below is
answered as recommended, the checker also owns the exact plan read and the
`missing-plan` / `empty-plan` / unreadable discrimination, which the 360-line
estimate did not budget for. Keep 1A, but treat 360 as the advisory it is and
expect the measured figure to land higher. The split trigger stays 650.

## Verdict on Q02 batch inventory compatibility delegate

Agree with Option 2A, keep `_staged_paths` as a thin delegate.

This is the strongest-supported of the five, and the working tree settles it.
`tests/unit/tools/test_git_batch_commit_workflow_process.py` uses the seam in
both directions: line 287 calls `git_batch_workflow._staged_paths(tmp_path)`
directly against a temporary repository, and line 304 monkeypatches
`git_batch_workflow._staged_paths`. Option 2B would have to rewrite both
usages inside Step 1 for no parity gain, and Option 2C is excluded by the
design constraint that checking and committing call one inventory function.

The answer's requirement that tests prove the delegate calls the public
function and cannot reinterpret its result is exactly right and should be kept
verbatim.

## Verdict on Q03 requestor gate placement

Agree with Option 3A, keep compact gate sequencing in
`tools/code_review_request.py`.

The design names the specialized renderer as the enforcement boundary, and
Option 3C would contradict that by letting direct renderer use bypass the
precondition. The size argument also holds up: `_render_from_arguments`
already calls `capture_index_tree(root)`, so the addition is a second capture,
one checker call, and two rejections at an existing seam. A 497-to-545
advisory projection is credible.

This question is incomplete rather than wrong. It settles which module holds
the sequence but not whether the typed input itself enforces readiness. See
Q07 below.

## Verdict on Q04 growth control for the existing request rendering test

Agree with Option 4A, restrict the 550-line file to fixture and parity
updates.

Option 4C is clearly worse and the question says so honestly. Option 4B is
real cleanup, but it is cleanup this feature does not need, and the plan's own
rule that a split is mandatory only above 650 is the right standard.

The question would be sharper with one mechanical fact it currently omits: all
six `CodeReviewRoundInput(` construction sites use keyword arguments, so the
cost of the new field in the risk-band file is one argument per construction
unless the new evidence is supplied through the shared fixture. State that,
and 4A stops depending on judgement about "material growth". This also makes
the dependency on Q07 explicit, since a required field and an optional field
imply different edit counts in exactly this file.

## Verdict on Q05 acceptance fixture extraction timing

Agree with Option 5A, keep helpers local until the risk band is near.

Option 5C is correctly rejected: reusing unit Git fixtures would couple
acceptance evidence to isolated unit support and blur the launcher boundary
that these tests exist to prove. Option 5B adds a shared fixture surface
before a second consumer exists.

One precision point. The named destination
`tests/acceptance/commit_plan_check/conftest.py` sits at the parent package
rather than the leaf, while every existing conftest in this repository is
leaf-level, including
`tests/unit/tools/test_code_reviewer_acceptance/conftest.py`. Parent-level
placement is defensible because it would serve later sibling acceptance
leaves, but the plan should say that is deliberate so an implementer does not
"correct" it to the leaf and quietly change the sharing scope.

## Verdict on question coverage for the plan as a whole

The five placed questions are individually sound, but the set is incomplete.
Two decisions carry implementation consequence, are not derivable from the
design, and are currently left to implementer discretion. They are requested
as Q06 and Q07 in the writer instructions.

### Requested changes for plan commit-plan-check round 1

Requested changes:

1. Add Q06 deciding the checker's plan-parsing boundary, with the three
   options and the accepted Option 6A answer described in the writer
   instructions.
2. Update Step 2 "Classes and behavior" so `check_commit_plan(root)` states
   the resolve, `missing-plan`, `empty-plan`, parse, inventory, validate order
   explicitly rather than only "parse once with `interactive=False`".
3. Add a confirmed technical fact recording that
   `git_batch_commit_parsing.parse_clipboard_content` is public and exported,
   and reword the existing `_read_and_parse_content` fact so it no longer
   reads as the recommended parsing seam for a read-only command.
4. Add Q07 deciding whether the commit-plan result on `CodeReviewRoundInput`
   is required and whether `__post_init__` rejects a non-ready result, with
   the accepted Option 7B answer described in the writer instructions.
5. Record in Q04 and Q07 that all six `CodeReviewRoundInput(` construction
   sites use keyword arguments and that the new field is supplied through the
   shared fixture, so the 550-line risk-band file absorbs one fixture change.
6. Rewrite the Step 4 acceptance input list so the two empty scenarios are
   named separately as `empty-plan` and `empty-staged-set`.
7. Add the operational-failure acceptance scenario for an unreadable plan or a
   failed Git inventory at status two across both entry points.
8. Add the stdout-redirection acceptance scenario in which the caller owns the
   ignored root `a.*` evidence file and the checker stays read-only.
9. Require Step 2 tests to assert the exact structured key set from the design
   with `schema_version` 1, and to assert that structured output reaches
   stdout for expected non-readiness as well as readiness.
10. State that `tests/acceptance/commit_plan_check/conftest.py` is
    deliberately at the parent package rather than the leaf, and note the
    advisory-only nature of the 360-line Step 2 estimate once the checker owns
    plan reading and empty-state discrimination.

### Writer instructions for plan commit-plan-check round 1

## Instruction to add Q06 for the checker plan-parsing boundary

Add a sixth open question deciding which parsing boundary the read-only
checker uses, following the document's existing question template with a
description, a BBQ analogy, options with pros and cons, a recommended option,
and an accepted answer.

Suggested question description: Step 2 requires the service to parse the root
plan once with `interactive=False` but does not name the parsing function,
while the confirmed technical facts highlight
`git_batch_commit_workflow._read_and_parse_content`. Which parsing boundary
must the checker use?

Suggested options:

- Option 6A: Read `<root>/a.commit` in the checker and parse with the public
  `git_batch_commit_parsing.parse_clipboard_content(content,
  interactive=False)`.
  - pro: Lets the checker classify a missing file, an empty file, and an OS
    read failure directly, which is what the design's three distinct outcomes
    require.
  - pro: Keeps the read-only command independent of the committing workflow
    module and uses a name that module `__all__` already exports.
  - con: The checker owns a small exact-file read that the committing workflow
    implements separately.
- Option 6B: Reuse `git_batch_commit_workflow._read_and_parse_content(root,
  filename="a.commit", interactive=False)`.
  - pro: Reuses one existing read-and-parse path with no new reading code.
  - con: That helper raises a single `GitBatchCommitError` for a missing file,
    an empty file, and an OS read failure, so the checker can only recover the
    three required states by matching exception message text.
  - con: Makes the read-only checker depend on the committing module and on a
    private name, and inherits a clipboard fallback and `LOGGER.info` progress
    lines that a read-only evidence command has no use for.
- Option 6C: Move the exact plan read and parse into
  `tools/commit_plan_support.py` in Step 1 beside `staged_paths`.
  - pro: Gives checking and committing one shared read-and-parse boundary in
    the same neutral module as the shared inventory.
  - con: Widens Step 1 beyond the inventory extraction the design asked for,
    and the committing workflow still needs its clipboard path, so the two
    callers would not fully converge.

Recommended and accepted answer: Option 6A. The design fixes `missing-plan`,
`empty-plan`, and operational failure as three separate outcomes at two
different exit statuses, and only 6A produces them from control flow instead
of from error-message inspection. It also honors the design constraint that
Git inventory, not parsing, is the shared boundary, so Step 1 stays scoped.

When Q06 is answered, also update Step 2 "Classes and behavior" so
`check_commit_plan(root)` states the order explicitly: resolve
`<root>/a.commit`; return `missing-plan` when it is absent; read it and return
`empty-plan` when the content is empty or whitespace; otherwise parse once
with `interactive=False`, inventory once, validate once. Add a line to the
confirmed technical facts recording that `parse_clipboard_content` is exported
from `tools/git_batch_commit_parsing.py`, and reframe the existing
`_read_and_parse_content` fact so it is not read as the recommended seam.

## Instruction to add Q07 for typed commit-plan evidence on the request input

Add a seventh open question, in the same template, deciding how the
commit-plan result attaches to `CodeReviewRoundInput`.

Suggested question description: Step 3 requires one typed commit-plan result
on `CodeReviewRoundInput` but does not say whether the field is required and
whether `__post_init__` rejects a non-ready result, which decides whether the
public `render_code_review_request` can emit a request carrying non-ready
evidence.

Suggested options:

- Option 7A: Required field, readiness enforced only in
  `_render_from_arguments`.
  - pro: Keeps the enforced order in one place and leaves the dataclass a
    plain carrier.
  - con: The public renderer can still produce request content from a
    non-ready result.
- Option 7B: Required field, and `__post_init__` rejects a non-ready result
  alongside the existing identity, round, timestamp, and tree-shape checks.
  - pro: Makes non-ready request content unconstructible, matching how the
    class already rejects a non-code family and a malformed
    `request_index_tree`.
  - con: Tests covering non-ready rejection must assert construction failure
    rather than a render-path return.
- Option 7C: Optional field defaulting to `None`.
  - pro: Leaves every existing construction site untouched.
  - con: Makes missing checker evidence representable and weakens the binding
    between the request and the checked index state.

Recommended and accepted answer: Option 7B. `CodeReviewRoundInput.__post_init__`
already refuses a non-code family, a non-positive round, an invalid local
timestamp, and a `request_index_tree` that fails `_TREE_OBJECT_RE`, so
readiness validation is consistent with the type's established role. Option 7C
is excluded because the design requires the request to carry the full
structured checker result.

State in the answer that all six existing `CodeReviewRoundInput(` construction
sites use keyword arguments, and that the new field must be supplied through
the shared fixture so
`tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
absorbs one fixture change rather than per-test edits. That keeps the Q04
answer consistent with this one.

## Instruction to align Step 4 acceptance coverage with the design table

Step 4 currently lists acceptance inputs as "valid, missing, empty, mismatched,
and renamed", which is narrower than the design's acceptance table. Rewrite
that list so each design row has a named acceptance scenario:

- Distinguish the two empty scenarios explicitly, since they must produce
  different states: empty `a.commit` with an empty staged set yields
  `empty-plan`, and a nonempty plan with an empty staged set yields
  `empty-staged-set`. The current single word "empty" hides that the checker
  must tell them apart.
- Add the operational-failure acceptance scenario for an unreadable plan or a
  failed Git inventory returning a stable stderr diagnostic at status two.
  Step 2 covers this at unit level, but the design lists it as an acceptance
  case across both entry points.
- Add the stdout-redirection scenario in which a caller redirects checker
  output to an ignored root `a.*` file and the checker remains read-only with
  the caller owning the evidence file. The existing before/after ignored-root
  inventory snapshot proves the checker creates no file, which is a different
  claim.

## Instruction to pin the structured payload in Step 2 tests

Step 2 "Tests first" asks for "deterministic human and JSON projections",
which does not pin the contract. The design fixes the structured form at
`schema_version` 1 with keys `state`, `ready`, `staged_paths`, `groups` whose
entries carry `position`, `subject`, and `paths`, and `diagnostics`. Step 2's
own completion criteria already grep for `schema_version`, so the assertion
should exist to match.

Require an explicit assertion of that exact key set and of `schema_version`
being 1, and require the structured result to reach stdout for expected
non-readiness as well as for readiness, since the design states automation
must be able to parse the evidence before observing status three.

## Instruction to record the conftest placement rationale

In the Q05 answer or the Step 4 split guidance, state that
`tests/acceptance/commit_plan_check/conftest.py` is intentionally at the
parent package so later sibling acceptance leaves can share it, noting that
existing repository conftests are leaf-level. This prevents an implementer
from relocating it and silently narrowing the sharing scope.

## Instruction on what to leave unchanged

Do not reopen the settled requirement or design choices. In particular keep
the accepted direct-publication bypass, the exclusion of the batch
missing-file precheck from readiness, the unchanged `--root-a-commit
--dry-run` rejection in the committing launcher, and the existing answers to
Q01 through Q05, which this review accepts as written apart from the noted
precision additions.

### Final reviewer decision for plan commit-plan-check round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-08-26T10:07:17+02:00
- Exchange: specification/plan/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Outcome: request

### Review identity for plan commit-plan-check (round 2)

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Reviewed specification: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
Review round: 2

### Requestor assessment for plan commit-plan-check (round 2)

The revised implementation plan is ready for round-2 review. No additional
implementation-only question is currently missing. Q01 through Q05 remain as
accepted in round 1, and new Q06 and Q07 now settle the public content parser
and required ready evidence on `CodeReviewRoundInput`. Every question has
complete options, consequences, a recommendation, and an accepted answer. All
round-1 wording and coverage recommendations were applied without disagreement.

### Change summary for plan commit-plan-check (round 2)

Added Q06 selecting checker-owned exact plan reading through public
`parse_clipboard_content`, and Q07 requiring construction-time ready evidence
on `CodeReviewRoundInput`. Reframed the parsing facts and Step 2 call order,
pinned the schema-version-1 JSON key set and status-three stdout behavior,
recorded the six keyword-based request input sites, separated both empty
acceptance states, and added operational-failure and caller-redirection
acceptance scenarios. Clarified the advisory checker estimate and deliberate
parent-package acceptance `conftest.py` destination.

### Writer response for plan commit-plan-check (round 2)

Writer response: Accepted every round-1 recommendation. The public content parser now preserves
missing, empty, and operational outcomes without exception-message matching;
the typed request input makes non-ready evidence unconstructible; and the unit
and acceptance lists now pin every requested structured-output and repository
state case. Q01 through Q05 remain unchanged apart from the requested factual
precision. There is no disagreement with the reviewer.

### Reviewer focus for plan commit-plan-check (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-08-26T10:10:48+02:00
- Exchange: specification/plan/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Outcome: answer

### Reviewer assessment for plan commit-plan-check round 2

Every round-1 recommendation was applied, and applied correctly rather than
nominally. I verified each against the current document instead of relying on
the change summary.

Confirmed applied:

- Q06 exists at the plan's question template with three materially distinct
  options and the accepted Option 6A answer.
- Q07 exists with the accepted Option 7B answer.
- Step 2 `check_commit_plan(root)` now states the full order: resolve, return
  `missing-plan` when absent, read once and return `empty-plan` on empty or
  whitespace content, then parse through public `parse_clipboard_content`,
  inventory once, validate once.
- The confirmed facts now record `parse_clipboard_content` as public and
  exported, and explicitly mark `_read_and_parse_content` as not the read-only
  checker seam, naming its clipboard, logging, and collapsed-error behavior.
- Step 2 tests pin the exact structured key set with `schema_version` equal to
  `1` and require the complete object on stdout before status three.
- Step 4 separates `empty-plan` from `empty-staged-set` and adds both the
  operational-failure and the caller-redirection acceptance scenarios.
- Q04, Q07, and Step 3 all record that the six `CodeReviewRoundInput(` sites
  use keyword arguments and that the new field arrives through the shared
  fixture.
- Step 3 requires `__post_init__` to reject a non-ready result.
- The parent-package `conftest.py` placement is now marked deliberate, and the
  360-line Step 2 estimate is marked advisory against the added read and
  discrimination work.

I also re-derived the failure taxonomy against the real validator rather than
accepting the new ordering on its face. `validate_commit_plan([], [])` returns
no diagnostics and would therefore report a nonempty-but-zero-block plan as
ready if it were reached with an empty index. The Step 2 order forecloses that
path: empty or whitespace content becomes `empty-plan` before parsing, and a
nonempty plan against an empty index becomes `empty-staged-set` before
validation. A nonempty plan that parses to zero blocks against a nonempty
index reaches the validator and fails on membership diagnostics at status
three. The taxonomy is closed at every entry, including the case the design's
table does not name.

Cross-checking Step 4 against the design's eleven acceptance rows, all eleven
now have a named scenario: valid, missing membership, `empty-plan`,
`empty-staged-set`, `missing-plan`, operational failure, staged rename, caller
redirection, invalid requestor plan, index drift during rendering, and the
reviewer rerun recorded as mechanical evidence only.

I ran the repository Markdown gate over the working tree; it reports no
finding for the plan or its transcript, so the non-negotiable MD024 and MD025
heading rules hold across the appended rounds.

Every in-scope decision is now settled. Seven questions carry complete
options, honest consequences, a recommendation, and an accepted answer, and
none reopens a settled requirement or design choice. The four steps remain
correctly ordered, every modified and new file is accounted for with a
baseline and a budget, and the deferred list still matches the design. What
remains is optional wording polish only, listed separately and carrying no
implementation consequence.

There is no disagreement between the roles in this exchange.

### Question verdicts for plan commit-plan-check round 2

## Round two verdict on Q01 through Q05

Unchanged and agreed. The round-1 answers stand, and the precision additions I
asked for are present without altering any selected option.

Q01 keeps the single checker module and now marks the 360-line estimate
advisory against the plan read and empty-state discrimination that Q06 adds to
that file. That is the honest reading: the estimate moved, the 650-line split
trigger did not.

Q02 keeps the thin `_staged_paths` delegate. The working tree still supports
this decisively, using the seam both directly and as a monkeypatch target.

Q03 keeps gate sequencing in `tools/code_review_request.py`, and the gap I
noted is now closed by Q07 rather than by rewording Q03.

Q04 keeps the risk-band file limited to fixture and parity updates, and now
states the mechanical fact that makes that outcome verifiable rather than a
judgement call.

Q05 keeps local acceptance helpers and now records why the extraction
destination sits at the parent package.

## Round two verdict on the new Q06

Agree with Option 6A as accepted.

The question is correctly framed and its options are genuinely distinct. The
cons are accurate, not strawmen: 6B really does collapse missing, empty, and
read failures into one `GitBatchCommitError`, and 6C really would widen Step 1
while leaving the committing workflow's clipboard path unconverged.

The recommendation follows from the design's requirement that `missing-plan`,
`empty-plan`, and operational failure be three outcomes across two exit
statuses. Only 6A produces them from control flow. The accepted answer states
that reason rather than restating the option.

## Round two verdict on the new Q07

Agree with Option 7B as accepted.

The consistency argument is the right one and it is factually correct:
`CodeReviewRoundInput.__post_init__` already rejects a non-code family, a
non-positive round, an invalid local timestamp, and a `request_index_tree`
that fails its shape check, so refusing a non-ready commit-plan result is the
same kind of invariant rather than a new responsibility.

Option 7C is correctly excluded by the design requirement that the request
carry the complete structured checker result. Option 7A is a reasonable
fallback but leaves the public renderer able to emit request content from a
non-ready result, which is exactly the boundary the design assigns to this
module.

## Round two verdict on remaining question coverage

The set is now complete. I looked specifically for decisions still left to
implementer discretion and found none with implementation consequence. The
checker's state ordering, the parsing seam, the typed-input invariant, the
risk-band growth path, the acceptance extraction trigger, and both module
granularity choices are all settled with reasons recorded.

No question is missing, redundant, unclear, or outside scope.

### Convergence evidence for plan commit-plan-check round 2

Covered wording: These are optional and carry no implementation consequence. The plan is
implementable exactly as written if none is applied. I list them only because
the round asks for better phrasing where it exists.

1. Q06's description opens with "the initial plan did not name the parsing
   function". After consolidation the document no longer has an "initial"
   revision to refer to, so the clause reads as an artifact of the review. A
   present-tense framing keeps the question self-contained, for example:
   "Step 2 requires the service to parse the root plan once with
   `interactive=False`. Which parsing boundary must the read-only checker use,
   given that the committing workflow exposes its own read-and-parse helper?"

2. Q07's stated con, "Non-ready unit cases assert construction failure rather
   than a render-path return", is slightly narrower than the settled behavior.
   `_render_from_arguments` still requires a ready result before it constructs
   the typed input, so a non-ready result is rejected on the render path too
   and the construction guard covers direct public renderer use. Consider:
   "Non-ready cases are proven at two boundaries: the render path rejects
   before construction, and direct construction fails."

3. Step 3's `_render_from_arguments` bullet and the Q07 answer both describe
   the readiness rejection. Naming the division once, that the render path
   owns command order and `__post_init__` owns representability, would remove
   the appearance of a duplicated rule.

4. In the Step 2 line-budget entry, "may exceed this estimate without creating
   missing work" is accurate but dense. "May exceed this advisory estimate;
   record the variance as evidence rather than treating it as a defect"
   matches the wording already used in the shared execution checklist.

None of these changes a decision, an option, an answer, a file list, a test
boundary, or a budget.

Convergence rationale: I recommend convergence because the two substantive gaps from round 1 are
closed at their root rather than papered over, and because I could not find a
new one.

The round-1 blockers were both decisions with real consequence that had been
left to implementer discretion. Q06 now settles the parsing boundary in the
only way that preserves the design's three-outcome failure taxonomy from
control flow, and it removes the confirmed-fact hint that would have steered
implementation into a private committing helper with a clipboard fallback.
Q07 now settles the typed-input invariant so non-ready checker evidence is
unrepresentable, which restores the specialized renderer as a real enforcement
boundary rather than a documented intention.

The eight non-question items were mechanical and are all present. The
acceptance list now covers all eleven design rows, including the two empty
states the earlier wording had collapsed into one word, and Step 2 now asserts
the structured contract its own completion grep was already looking for.

I did three independent checks beyond confirming the edits. I re-derived the
failure taxonomy against the real `validate_commit_plan`, including the
nonempty-plan-that-parses-to-zero-blocks case the design table does not name,
and the Step 2 ordering closes it at every entry. I cross-checked Step 4
against the design's acceptance table row by row. I ran the repository
Markdown gate and found no finding for the plan or its transcript, so the
non-negotiable heading rules hold across appended rounds.

What remains is four optional phrasing suggestions, none of which changes a
decision, option, answer, file list, test boundary, or budget. That is
wording-only by the standard this exchange uses, so another automated round
would not improve the specification.

This recommendation is advisory. It does not authorize consolidation, and the
human remains the only party who may choose `Consolidate` or
`Revise and review again`.

### Writer instructions for plan commit-plan-check round 2

No substantive change is required. Do not open another revision cycle on my
account.

If the human selects `Consolidate`, proceed with the canonical
`consolidate-then-review-ask-questions` workflow on
`docs/v0.11.0/plan.v0.11.0.commit-plan-check.md`. When consolidating:

- Carry every accepted answer for Q01 through Q07 into the decision record
  with its reason, since several reasons rest on verified working-tree facts
  that will not be re-derivable from the consolidated prose alone. In
  particular preserve why `parse_clipboard_content` is the checker's parsing
  seam and why `_read_and_parse_content` is not, because that distinction is
  what keeps the failure taxonomy intact.
- Keep the confirmed technical facts that record `parse_clipboard_content` as
  public and exported, and that record the six keyword-based
  `CodeReviewRoundInput(` construction sites. Both are load-bearing for
  decisions rather than background.
- Keep the Step 2 call order verbatim. The sequence of resolve, `missing-plan`,
  read once, `empty-plan`, parse, inventory, validate is what closes the
  taxonomy, including for a nonempty plan that parses to zero blocks.
- Keep the deliberate parent-package `conftest.py` note and the advisory
  framing of the 360-line Step 2 estimate.

The four phrasing suggestions in the covered-wording input are optional. Apply
any, all, or none before consolidation; none of them alters a decision.

If the human instead selects `Revise and review again`, treat the covered
wording as the full scope of that round unless the human supplies guidance
that adds to it.

### Final reviewer decision for plan commit-plan-check round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-08-26T11:41:07+02:00
- Exchange: specification/plan/v0.11.0/commit-plan-check
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.commit-plan-check.md
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
