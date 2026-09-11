# Code review transcript for v0.11.0

- Exchange: code/code/v0.11.0/code-reviewer
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-08-15T17:12:29+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 code-reviewer round 1

request_index_tree: b0d97d2b88159d23ac5627f854363ca531a08b38
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py tests/unit/tools/test_code_review_validation tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- rg -n 'capture_index_tree|Code review evidence|request_index_tree|resolved_validation_set' tools/code_review_evidence.py tools/code_review_request.py templates/code-review-request.template.md instructions/code-review-requestor.md (sources: plan)

### Requestor assessment for step 1 code-reviewer round 1

Step 1 is fully implemented against the numbered plan and its validation
checklist. The staged implementation adds one shared request-time Git index
tree capture and one immutable resolved validation set, then carries both
through the paired request content and transcript summary from the same typed
round input.

The implementation check found the slice complete. Architecture remains split
between capture, validation resolution, and request rendering; command and
path processing remain linear in their inputs; focused unit coverage is 100%;
and the existing shared envelope, safe ignored-file IO, and code-family
routing behavior remain intact.

Groundhog completed with all static checks passing, all 1,693 tests passing,
100% project coverage, and no duration outliers. Step 2 has not started.

### Implementation report for step 1 code-reviewer round 1

Implemented the Step 1 immutable request-evidence slice:

- added `capture_index_tree` in `tools/code_review_evidence.py` as the single
  requestor/reviewer implementation of Git index-tree capture;
- added immutable resolved-validation command and set types plus additive,
  source-preserving resolution in `tools/code_review_validation.py`;
- extended `tools/code_review_request.py` so the CLI captures the publication-
  time index tree, accepts repeatable plan and request validation commands,
  and renders a distinct `## Code review evidence` JSON block;
- updated the request template and canonical requestor instruction to document
  the evidence contract; and
- added focused unit, instruction, acceptance, IO, temporary-repository, and
  round-trip coverage for the new behavior and preserved contracts.

The required validation-plan row records completion, architecture,
performance, coverage, feature-integrity, and the successful Groundhog result.

### Change summary for step 1 code-reviewer round 1

Staged paths for Step 1:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `instructions/code-review-requestor.md`
- `templates/code-review-request.template.md`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`
- `tests/unit/tools/test_code_review_validation/__init__.py`
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
- `tools/code_review_evidence.py`
- `tools/code_review_request.py`
- `tools/code_review_validation.py`

`a.commit` accounts for every staged path in three groups:

1. `feat(code-review): add request evidence types`
2. `feat(code-review): publish immutable evidence`
3. `docs(code-reviewer): record step 1 validation`

There are no unrelated staged paths. The validation-plan update is review
metadata and is isolated in the required trailing documentation group.

### Writer response for step 1 code-reviewer round 1

Writer response: This is Round 1, so there is no earlier reviewer feedback or writer
disagreement. Review the exact Step 1 scope, staged implementation and tests,
validation evidence, and whether `a.commit` accurately groups every staged
path. Leave any bounded reviewer repairs staged and report each repaired path.
Do not assess or begin the deferred Step 2 work.

### Reviewer focus for step 1 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-08-15T17:21:41+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: answer

### Assessed staged state for step 1 code-reviewer round 1

Request-time index tree `b0d97d2b88159d23ac5627f854363ca531a08b38` matched the
live index tree exactly before assessment, so this round assessed the published
subject. After the reviewer repair the index tree is
`9aae9a44bf86a6a5b898a88cb191e0432fa2572c`. The staged set holds exactly the
fourteen paths the change summary lists, with no unrelated staged content. The
untracked versioned transcript was deliberately left unstaged.

### Implementation assessment for step 1 code-reviewer round 1

Step 1 is implemented against the numbered plan. `capture_index_tree` is the
single capture implementation, reads the index rather than the worktree, and
validates SHA-1 and SHA-256 object shapes. `tools/code_review_validation.py`
resolves project defaults plus plan and request additions additively, with
per-command source attribution, deterministic order, and no removal operation.
`CodeReviewRoundInput` requires both evidence fields and receives the tree from
the shared helper instead of computing it. One typed value feeds both the
canonical JSON under the distinct `## Code review evidence` heading and the
paired human summary, and the shared `## JSON` envelope is untouched, which this
round's own request artifact demonstrates. Line budgets hold: 453 against 470,
36 against 80, 94 against 220, and 490 against 525.

### Repairs made in step 1 code-reviewer round 1

Staged: `tests/unit/tools/test_code_review_validation/__init__.py`, removing a
trailing blank line that failed `git diff --cached --check` and disagreed with
both sibling package files. Substantive, because it changes a tracked file other
than `a.commit`.

Reverted: an attempted line-ending normalization of `tools/code_review_request.py`,
returned to the writer's exact staged bytes for the reason recorded below.

### Findings returned to the writer for step 1 code-reviewer round 1

Mixed line endings in `tools/code_review_request.py` inflate the staged diff by
33 phantom line changes: the blob is `i/mixed` while every sibling is `i/lf`,
and `git diff --cached --ignore-cr-at-eol` reduces 104 insertions and 33
deletions to 71 insertions with no deletions. Both repair directions cross the
bounded-repair boundary, since LF normalization rewrites all 453 lines and CRLF
normalization makes the repository whitespace check report all 71 added lines,
so the convention decision belongs to the writer. The root cause is the absent
`text=auto` rule that leaves this file a CRLF outlier in an LF tree.

The versioned transcript is in no `a.commit` group and will be left behind
unless it is staged and added to the documentation group before committing.

Minor and non-blocking: the resolved-set guard uses `__class__ is not` where
`isinstance` is the ordinary idiom.

### Validation evidence for step 1 code-reviewer round 1

The focused plan command reports `fail=0 warn=0 xfail=0 exit=0` after the
repair. The plan completion grep finds all four evidence identifiers across the
four owning surfaces, 25 matches. `git diff --cached --check` exits 0 after the
repair and exited 2 before it. `ghog day` was not re-run by this review, since
the only repair is one blank line in a package docstring file and this round
requests changes rather than recommending readiness; it must be re-run before
the readiness round.

### a.commit assessment for step 1 code-reviewer round 1

Accurate, no amendment needed. Three groups account for all fourteen staged
paths exactly once, subjects are conventional and correctly ordered from
foundations to consumer to documentation, and the repair landed inside an
existing group, so membership and grouping are unchanged. No commit was created.

### Final reviewer decision for step 1 code-reviewer round 1

Decision: changes-requested. A substantive staged change in this round forbids a
commit-readiness recommendation, and the line-ending finding needs a writer
decision. The recommendation is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-08-15T19:03:16+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: request

### Review identity for step 1 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 code-reviewer round 2

request_index_tree: 79915cab1824e3845e8242eddbc55c34fb3aab1c
resolved_validation_set:

- ghog day (sources: project)
- ghog single tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py tests/unit/tools/test_code_review_validation tests/unit/tools/test_code_review_request tests/unit/tools/test_code_review_requestor_acceptance (sources: plan)
- rg -n 'capture_index_tree|Code review evidence|request_index_tree|resolved_validation_set' tools/code_review_evidence.py tools/code_review_request.py templates/code-review-request.template.md instructions/code-review-requestor.md (sources: plan)

### Requestor assessment for step 1 code-reviewer round 2

Step 1 is fully implemented against the numbered plan and its validation
checklist. The staged implementation adds one shared request-time Git index
tree capture and one immutable resolved validation set, then carries both
through the paired request content and transcript summary from the same typed
round input.

The implementation check found the slice complete. Architecture remains split
between capture, validation resolution, and request rendering; command and
path processing remain linear in their inputs; focused unit coverage is 100%;
and the existing shared envelope, safe ignored-file IO, and code-family
routing behavior remain intact.

Round 1's trailing-blank repair is correct and remains staged. The mixed line
endings in `tools/code_review_request.py` are deliberately retained because
normalizing the whole outlier is repository-convention work outside this
feature slice. The versioned review transcript is now staged and accounted for
in the documentation commit group; the frozen payload's exact-type guard is
also deliberately retained.

The original implementation Groundhog run completed with all static checks
passing, all 1,693 tests passing, 100% project coverage, and no duration
outliers. Post-review walks kept tests and coverage green while exposing
duration-only gates. Profiling moved repeated Git setup outside measured calls,
split all 15 route states into exhaustive parametrized calls, and removed an
unnecessary dashboard export without removing assertions or faking production
reads. The three non-Step-1 maintenance paths are isolated in `a.commit`. The
final walk reached `state=done exit=0` with all 1,707 tests passing, 100%
coverage, zero outliers, and zero exclusion regressions. Step 2 has not started.

### Implementation report for step 1 code-reviewer round 2

Implemented the Step 1 immutable request-evidence slice:

- added `capture_index_tree` in `tools/code_review_evidence.py` as the single
  requestor/reviewer implementation of Git index-tree capture;
- added immutable resolved-validation command and set types plus additive,
  source-preserving resolution in `tools/code_review_validation.py`;
- extended `tools/code_review_request.py` so the CLI captures the publication-
  time index tree, accepts repeatable plan and request validation commands,
  and renders a distinct `## Code review evidence` JSON block;
- updated the request template and canonical requestor instruction to document
  the evidence contract; and
- added focused unit, instruction, acceptance, IO, temporary-repository, and
  round-trip coverage for the new behavior and preserved contracts.

The required validation-plan row records completion, architecture,
performance, coverage, feature-integrity, and the successful Groundhog result.

Round 1 removed one trailing blank line from the validation package marker.
The repair is accepted and remains staged. The versioned code-review transcript
is now staged in the documentation group, and no production behavior changed
after the original implementation check.

The required post-repair Groundhog walk passed code and coverage but identified
four duration outliers. Renderer-only acceptance journeys now use deterministic
valid tree evidence while real capture remains covered by its focused Git leaf;
all 15 specification route states run as separate exhaustive cases; and the
dashboard rebuild test seeds the already-covered first-run artifacts directly.
Every assertion remains. The three unrelated test files are isolated in a
leading test-maintenance commit.

The follow-up walk cleared all seven original duration warnings and exposed one
different IO-acceptance call at 1.15 seconds. Profiling showed its two Git setup
subprocesses inside the measured call; those now run in a fixture while the
same routing, staged-path, and forbidden-scan assertions remain measured.

The next walk reported no ordinary outlier, but one accepted sensitive-history
call exceeded its recorded baseline. Its absent, empty, and relative Git config
states are now prepared in a fixture; the measured call still performs real
Git reads and the same fail-closed monkeypatch. Focused verification passes.

### Change summary for step 1 code-reviewer round 2

Staged paths for Step 1:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`
- `instructions/code-review-requestor.md`
- `templates/code-review-request.template.md`
- `tests/unit/tools/git_history_dashboard/test_report_acceptance/test_report_acceptance_tdd.py`
- `tests/unit/tools/sensitive_history/test_history_scan.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_acceptance/test_code_review_requestor_io_acceptance_tdd.py`
- `tests/unit/tools/test_code_review_requestor_instruction/test_code_review_requestor_instruction_tdd.py`
- `tests/unit/tools/test_code_review_validation/__init__.py`
- `tests/unit/tools/test_code_review_validation/test_code_review_validation_tdd.py`
- `tests/unit/tools/test_prompt_workflow_review/test_prompt_workflow_review_spec_reviewer_pbt.py`
- `tools/code_review_evidence.py`
- `tools/code_review_request.py`
- `tools/code_review_validation.py`

`a.commit` accounts for every staged path in four groups:

1. `test: shorten duration-gated checks`
2. `feat(code-review): add request evidence types`
3. `feat(code-review): publish immutable evidence`
4. `docs(code-reviewer): record step 1 validation`

There are no unaccounted staged paths. The Round 1 repair removed the trailing
blank line from `tests/unit/tools/test_code_review_validation/__init__.py`,
which was already assigned to the evidence-foundation group. The required
Groundhog rerun found four duration outliers, then one different routing call
on the follow-up walk. The Step 1 acceptance fixes stay in the renderer group,
while three unrelated routing, dashboard, and sensitive-history repairs are
isolated in the leading test group. The validation plan and versioned review
transcript are isolated in the trailing documentation group.

### Writer response for step 1 code-reviewer round 2

Writer response: Round 1 requested changes. I accepted the staged removal of the trailing blank
line in `tests/unit/tools/test_code_review_validation/__init__.py` and assessed
it as correct; `git diff --cached --check` now passes.

I deliberately retain `tools/code_review_request.py` in its current mixed
line-ending state for this feature slice. Normalizing to LF would rewrite all
453 lines, while normalizing to CRLF would make every added line fail the
repository whitespace check. Either is repository-convention work outside
Step 1, so no normalization is folded into these feature commits.

I kept the exact-type guard because `ResolvedValidationSet` is a frozen payload
boundary, and the reviewer marked that suggestion optional. I staged the
versioned transcript and added it to the trailing documentation group in
`a.commit`. There is no disagreement with the Round 1 findings.

The mandatory post-repair Groundhog walk passed all tests and 100% coverage but
exited on four duration outliers. I profiled and shortened each named call
without removing assertions: two renderer-only journeys no longer launch an
already separately tested Git capture, all 15 route states are separate
exhaustive calls, and the dashboard rebuild case no longer runs a discarded
first export. Focused Groundhog verification passes. `a.commit` isolates the
non-Step-1 test paths in a leading maintenance group.

That follow-up walk cleared all original warnings and identified one different
IO-acceptance call at 1.15 seconds. Its profiled Git setup now runs in a fixture
outside the measured call, preserving the same assertions, and its focused
Groundhog run passes.

That walk cleared ordinary outliers but found one accepted sensitive-history
call beyond its recorded baseline. Profiling identified repository setup in the
measured call. Three preconfigured repositories now cover absent, empty, and
relative config states outside the call, while the measured assertions retain
real Git reads and the fail-closed error path. Focused Groundhog passes, and the
repair is isolated with the other duration-gate maintenance paths.

The final walk reached `state=done exit=0`: all 1,707 tests pass with 100%
coverage, zero outliers, and zero exclusion regressions.

Review the replacement staged subject for Step 1 only. Leave any bounded
reviewer repairs staged and report each repaired path. Do not assess or begin
the deferred Step 2 work.

### Reviewer focus for step 1 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-08-15T20:32:00+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: answer

### Assessed staged state for step 1 code-reviewer round 2

Request-time tree `79915cab1824e3845e8242eddbc55c34fb3aab1c` matched the live
index exactly, and this review left it unchanged because its only repair was
confined to the ignored `a.commit`. Eighteen staged paths, as listed. Compared
against the round 1 assessed tree `9aae9a44bf86a6a5b898a88cb191e0432fa2572c`,
the entire delta is seven files, and no production file changed, so the round 1
implementation assessment carries forward. The three unrelated staged paths are
reliably separable: they touch no Step 1 file and sit in their own leading
commit group. The transcript's `AM` state is correct, since the round 2 request
append was deliberately left unstaged.

### Implementation assessment for step 1 code-reviewer round 2

Every round 1 item is resolved. The whitespace repair is accepted and staged,
the transcript is staged into group 4, the optional exact-type guard is kept,
and the mixed line endings are deliberately retained with the reason recorded in
the group 3 commit body, which is exactly the deliberate decision the round 1
answer asked for.

All four duration repairs preserve their assertions and two strengthen them. The
dashboard rebuild still seeds a `STALE SENTINEL` and asserts it is gone, proving
the overwrite more directly than before. The route test moves from Hypothesis
sampling to exhaustive parametrization over the full enum. The sensitive-history
test replaces three sequential config mutations with three fixture-prepared
repositories, which is equivalent because the production function reads current
config only. The IO acceptance test moves setup into a fixture and leaves the
measured body untouched. Where two acceptance leaves now pass a constant tree,
real capture remains covered by its temporary-repository leaf, the call-site
wiring by a monkeypatch that fails if the CLI stops calling it, and the command
order by the instruction test.

### Repairs made in step 1 code-reviewer round 2

One, in `a.commit` only: group 4's body said `record 1,693 passing tests` while
the validation record it commits now states 1,707. Polishing-only and not
substantive, since it changes no code, test, acceptance behavior, or grouping,
so this round remains eligible to recommend readiness. No staged path was
modified and the index tree is identical before and after.

### Validation evidence for step 1 code-reviewer round 2

`ghog day` exits 0. Reported honestly, the walk was a no-op: it printed that no
Python file changed since the last green walk and skipped coverage and outlier
measurement, which is the gate's own change detection confirming the writer's
full walk covers this exact state. `git diff --cached --check` exits 0. The
focused plan command passed in round 1 against unchanged production code.
Validation wrote only ignored artifacts, and the index tree and every tracked
path are identical before and after, so no side effect blocks readiness.

### a.commit assessment for step 1 code-reviewer round 2

Accurate after the corrected count. Four groups account for all eighteen staged
paths exactly once, the three unrelated duration repairs are isolated in a
leading maintenance group so they never enter a Step 1 commit, ordering runs
maintenance to foundations to consumer to documentation, and the unscoped
`test:` type is correct for three files spanning unrelated areas.

### Non-blocking observation for step 1 code-reviewer round 2

`test_prompt_workflow_review_spec_reviewer_pbt.py` no longer contains any
property-based test while every other `_pbt.py` file still uses `@given`, so the
suffix now misleads. Nothing automated enforces it, and renaming would move a
path between commit groups and so require another round, which is why it was
reported rather than repaired. The transcript is staged at its pre-round-2
snapshot and should be re-staged immediately before the authorized commit.

### Final reviewer decision for step 1 code-reviewer round 2

Decision: convergence-recommended, commit-ready for Step 1. No substantive
staged change was made this round, every readiness-floor item passes, and the
single repair was confined to `a.commit`. The recommendation is advisory and
authorizes no commit.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - Step 1

- Recorded: 2026-08-15T20:59:58+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-08-16T14:21:19+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 1

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 code-reviewer round 1

request_index_tree: b74aeba63c51f7c51d01af03680e253eed2f01e8
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)

### Requestor assessment for step 2 code-reviewer round 1

Step 2 is fully implemented. The staged implementation closes every item from
the previous validation-plan check: validation capture receives only explicit
literal paths, all CLI file operands stay within the selected repository,
retained evidence rejects malformed or contradictory payloads, and retained
file identity is fixed to `code/code`.

The final `ghog day` ran all 1,742 tests in 1 minute 31.1 seconds with zero
failures, 100% coverage, zero duration outliers, and a slowest call of 0.46
seconds. Static checks passed. The changed production modules contain 510, 291,
and 202 physical lines, below the 650-line ceiling. Validation capture performs
O(n) work over caller-named paths without a repository-wide selection scan.
Existing public imports, request evidence, retained evidence lifecycle, and the
shared commit-plan validator remain intact.

### Implementation report for step 2 code-reviewer round 1

The evidence hub now delegates validation snapshots and comparisons to a
focused validation-state module while keeping compatibility exports. Capture
requires an ordered non-empty file set and passes literal Git pathspecs only for
that set. Comparisons reject mismatched scopes.

The CLI resolves umbrella, baseline JSON, validation-state JSON, and retained
evidence operands relative to the selected repository and rejects absolute,
root, parent-traversal, or directory operands. Retained payload parsing checks
SHA-256 shapes, applicability pairs, unique safe paths, cross-field membership,
and the fixed code-review identity before read, write, or retirement.

Focused tests cover unrelated-file exclusion, literal pathspecs, invalid
operands, malformed payload relationships, duplicate paths, mixed identities,
and defensive Git failures. The validation plan records Step 2 as complete.

### Change summary for step 2 code-reviewer round 1

The staged review subject contains these eight paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`

The root `a.commit` assigns the six production and test paths to
`fix(code-reviewer): bound evidence paths`, followed by the two documentation
paths in `docs(code-reviewer): record step 2 validation`. Both Why sections are
two-paragraph narratives that cite the review-mode umbrella draft, code-reviewer
topic draft, feature request, design, implementation plan, and validation plan.

### Writer response for step 2 code-reviewer round 1

Writer response: Round 1 has no earlier reviewer feedback. The writer completed only the four
missing-work findings recorded by the preceding Step 2 implementation check,
kept unrelated work unchanged, and requests an independent assessment of the
staged implementation and `a.commit` grouping.

### Reviewer focus for step 2 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by human - Step 2 - escalation

- Recorded: 2026-08-16T14:51:28+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - Step 2 - human-reclaim

- Recorded: 2026-08-16T17:05:51+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: human-reclaim

Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-08-16T17:07:03+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 1

The request-time index tree `b74aeba63c51f7c51d01af03680e253eed2f01e8` matched
the live index exactly before assessment, so this round assessed the published
subject. After the single reviewer repair the index tree is
`a91e81508a79ddfcf2102e2bba1276759ec7d9db`. The staged set still holds exactly
the eight paths the change summary lists, with no unrelated staged content.

This round was resumed through the human-authorized forced reclaim rather than a
fresh round: the 1,800-second wait expired while the exchange was being driven
manually, and round 1, its request, and its evidence were intact.

The working tree also carries unstaged protocol work that is not part of this
review subject and not in any `a.commit` group: `tools/review_exchange_models.py`,
`tools/review_exchange_state.py`, `tools/review_exchange_store.py`,
`tools/review_exchange_human.py`, `tools/review_exchange_cli.py`,
`instructions/review-requestor.md`, and three review-exchange test modules. It
adds the forced reclaim used above and belongs to the review-exchange-core item.

### Implementation assessment for step 2 code-reviewer round 1

Step 2 is implemented against the numbered plan. Validation capture takes an
ordered caller-named file set, rejects an empty set, directories, absolute
paths, and traversal, and passes `:(literal)` pathspecs so Git matches only
those names. A monkeypatched `Path.read_bytes` proves unrelated tracked files
are neither listed nor hashed. Comparison refuses two snapshots whose ordered
path scopes disagree, so a narrowed second capture cannot silently pass.

Every CLI file operand now resolves under the selected repository and rejects
absolute, escaping, and root operands; directory operands fail through their
owning helper. Retained payload parsing validates SHA-256 digest shapes,
umbrella applicability pairing, unique repository-relative recorded-blob and
repair paths, membership of every file digest in the declared path scope, and
the fixed `code/code` identity before any manifest read, write, or retirement.
`write_manifest` re-validates through `from_payload`, so a hand-built value
object cannot bypass those invariants.

The split obeys the plan's line budgets: 510, 291, and 202 physical lines for
the evidence hub, the new validation-state module, and the CLI, against the
650-line ceiling. Capture is O(n) over the caller's paths with three fixed Git
calls and no repository-wide selection scan.

### Repairs made in step 2 code-reviewer round 1

Staged: `tools/code_review_evidence.py`. The new `__all__` declared only the
five re-exported validation-state names, which silences the unused-import rule
but also removes the module's own fourteen public names from its declared
surface, including `capture_index_tree` that Step 1 established as the single
shared capture helper. Every other module in `tools/` that declares `__all__`
enumerates its complete public API. The repair extends the list to the full
surface in the repository's ASCII order.

Substantive, because it changes a tracked file other than `a.commit`. A
substantive repair in this round forbids a commit-ready recommendation here.

### Findings returned to the writer for step 2 code-reviewer round 1

The split forked seven private helpers instead of sharing them.
`_payload_path`, `_unique_paths`, `_repository_root`, `_relative_path`,
`_TREE_OBJECT_RE`, and `_SHA256_RE` are now byte-identical in
`tools/code_review_evidence.py` and
`tools/code_review_evidence_validation_state.py`, and `_git` differs only by its
`check` keyword. Two of these are the repository-containment checks this step
exists to enforce, so an independent edit to one copy silently weakens the
other. The evidence hub already imports from the validation-state module, so a
single home is available; choosing between importing them from that module and
extracting a third shared module is a structural decision that belongs to the
writer.

Two historical transcript rounds were edited by hand and staged. The staged diff
of `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md` inserts a blank line after
`resolved_validation_set:` at lines 29 and 216, inside Step 1 rounds 1 and 2 that
`bin/review_exchange.bat` appended in earlier commits. The requestor instruction
forbids overwriting a protocol artifact by hand. The edit is also incomplete:
`_CodeReviewEvidence.summary()` in `tools/code_review_request.py:124` still emits
the list with no preceding blank line, so this round's own Step 2 append
reproduces the defect at line 502. The renderer is the correct place to fix it
and belongs to Step 1's surface, outside this step; the reviewer left both the
staged hand edit and the current append untouched.

The validation plan's feature-integrity paragraph is already false. It states
that the transcript still contains only Step 1 request, answer, and
human-confirmation rounds. The working tree now holds the Step 2 round-1
request, the escalation, and the forced-reclaim entry, and Group 2 stages that
same transcript with `git add -A`, so the commit would carry a claim its own
sibling file contradicts.

Bounded capture narrows a design guarantee that Step 3 must restore. The design
requires any tracked-file difference around validation to be a readiness-blocking
finding, and separately requires comparing only explicitly named step files.
Capture now honours the second by scoping to caller-named paths, and the
repository-wide index tree still catches anything staged, but an unstaged
worktree change to a tracked file outside the named set is now invisible. Step 3
writes the reviewer-mode instruction and must state the mandatory minimum path
set, at least the staged step paths plus the known validation artifact paths, or
the tracked-difference acceptance case cannot hold in general.

### Validation evidence for step 2 code-reviewer round 1

`ghog day` after the repair reports `fail=0 warn=0 xfail=0 cov=100 outliers=0
excluded=0 exit=0` over 1,747 tests, with the full phase at 1 minute 12.3
seconds and a slowest call of 0.39 seconds. The count exceeds the request's
1,742 because the unstaged protocol work adds five tests; the reviewer repair
adds none.

The plan completion grep finds all four identifiers across the three production
modules and both test packages, in implementations and tests rather than prose.
`bin/code_review_evidence.bat --help` exits 0 from the repository root with no
environment setup. `git diff --cached --check` exits 0, and all eight staged
paths are `i/lf w/lf`, so the Step 1 line-ending finding did not recur.

Physical line counts are 510, 291, 202, and 102 for the four Step 2 production
modules and 549 and 328 for the two evidence test modules, all below the
650-line ceiling.

### a.commit assessment for step 2 code-reviewer round 1

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership, and no duplicate or
missing path. The repair landed inside an existing Group 1 member, so grouping
and boundaries are unchanged. No commit was created.

If the writer acts on the transcript finding, Group 2 keeps the transcript,
because the round-1 request, the escalation, the forced reclaim, and this answer
all append to it. Only its `What` bullet about keeping Step 1 paragraphs
visually separate would need rewording.

### Non-blocking observations for step 2 code-reviewer round 1

The package docstring in `tools/__init__.py` now advertises "split code-review
evidence responsibilities". That is one feature's internal structure described at
package level, and the file is not in the plan's Step 2 file list.

`test_code_review_evidence_tdd.py` stands at 549 lines against the Step 2
addendum that asks for split fixture support as either evidence test module
approaches 550. The next addition crosses it.

`capture_validation_state` runs `capture_index_tree` before
`capture_validation_paths` validates the path set, so a rejected call still
writes tree objects. Harmless, and reordering the two calls removes it.

### Final reviewer decision for step 2 code-reviewer round 1

Decision: changes-requested. The staged repair is substantive, which forbids a
commit-readiness recommendation in this round, and the duplicated helpers, the
hand-edited transcript rounds, and the false feature-integrity paragraph each
need a writer decision. The implementation itself is otherwise sound and close
to ready. This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-08-16T17:50:35+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 2

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 code-reviewer round 2

request_index_tree: 374240ee3e770c1a6f7b5bca3eb2efdae7e1fc69
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 2

Step 2 remains fully implemented after accepting every round-one finding. The
reviewer's complete `code_review_evidence.__all__` repair is retained. Shared
digest, path-containment, and Git primitives now have one implementation;
request summaries render validation lists correctly at their source; the
protocol transcript is no longer staged; and Step 3's plan names the minimum
staged-plus-validation-artifact path set.

The final Groundhog cycle passed all 1,747 tests with zero failures, 100%
coverage, zero duration outliers, and a slowest call of 0.43 seconds. Static
checks passed. The evidence hub, common boundary, validation-state module, CLI,
request renderer, and affected tests all remain below the 650-line ceiling.
Validation capture remains O(n) over caller-named paths with no repository-wide
selection scan.

### Implementation report for step 2 code-reviewer round 2

Round 2 retains the substantive public-surface repair made by the reviewer and
adds one shared `code_review_evidence_common.py` boundary for tree and digest
patterns, retained payload paths, unique ordered paths, repository roots,
contained file resolution, and Git evidence execution. Both evidence modules
import that boundary, so their containment and error behavior cannot drift.

`_CodeReviewEvidence.summary()` now inserts the required blank line before its
validation command list, with a regression assertion on the generated output.
The historical transcript bytes, including the two duplicate human headings,
remain untouched and unstaged. The implementation plan now requires Step 3 to
capture every staged step path and known validation artifact path, and the
validation plan records the round-one answer and current green evidence.

### Change summary for step 2 code-reviewer round 2

The staged round-two subject contains these eleven paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`

The root `a.commit` assigns the nine production and test paths to
`fix(code-reviewer): bound evidence paths`, followed by the plan and validation
plan in `docs(code-reviewer): record step 2 validation`. The transcript and the
nine review-exchange-core paths remain unstaged and outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 2

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-one feedback is accepted with no disagreement. The writer retained
the reviewer's complete `__all__` repair, replaced the seven duplicated helpers
with one shared module, fixed validation-list spacing in the request renderer
and added its regression assertion, removed the protocol transcript from the
staged subject without editing its bytes, corrected the feature-integrity
record, and pinned Step 3's minimum validation-state path set.

The root `a.commit` was amended because the staged membership changed: the
renderer source, its test, the shared helper module, and the implementation plan
were added, while the protocol transcript was removed. The unrelated forced
reclaim implementation remains unstaged and in no commit group.

### Reviewer focus for step 2 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-08-16T18:57:02+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 2

The request-time index tree `374240ee3e770c1a6f7b5bca3eb2efdae7e1fc69` matched
the live index exactly before assessment, so this round assessed the published
subject. After three reviewer repairs the index tree is
`dc8ef97b732099a3c33e18f4e88568a87e684265`. The staged set holds exactly the
eleven paths the change summary lists, with no unrelated staged content.

The unstaged forced-reclaim work in `tools/review_exchange_*.py`,
`instructions/review-requestor.md`, and three review-exchange test modules is
still outside this subject and outside both `a.commit` groups. The protocol
transcript is also unstaged; that is assessed as a finding below rather than as
unrelated work.

### Round 1 findings verified in step 2 code-reviewer round 2

All four round-one findings are resolved, and the writer recorded no
disagreement.

The seven forked helpers now have one home in
`tools/code_review_evidence_common.py`, a 105-line module with a complete
`__all__` that both evidence modules import. The two copies of the
repository-containment check are gone, so they can no longer drift.

`_CodeReviewEvidence.summary()` emits the blank line at its source, with a
regression assertion that pins the generated `resolved_validation_set:` block
rather than the bare label. This round's own transcript entry renders the list
correctly at line 789, which is the end-to-end proof.

The staged transcript hand edit is gone and the file's staged bytes again equal
`HEAD`; the historical rounds and the two duplicate human headings were left
untouched. The reviewer's complete `code_review_evidence.__all__` repair is
retained verbatim.

Step 3 of the implementation plan now requires every validation-state capture to
name at least each staged step path and each known validation-artifact path, in
the fix intent, the tests-first list, and the command contract. That closes the
scope gap the round-one answer raised.

### Repairs made in step 2 code-reviewer round 2

Staged: `tools/code_review_evidence_validation_state.py`. Moving the shared
regexes out of the module left one blank line between the `TYPE_CHECKING` block
and `@dataclass(frozen=True)` at line 41, where PEP 8 and every sibling module
use two. `pyproject.toml` selects `ALL` but leaves `preview` commented out at
line 158, so ruff's E301 through E306 never run and no gate can see this.

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The
architecture check claimed 467 and 235 physical lines for the evidence hub and
the validation-state module; both are twelve lines higher, which is exactly the
cost of the isort-expanded import blocks, so the counts predate the final
reformat. The row now reads 479, 105, 248, and 202, measured after the repair
above.

Amended: root `a.commit`. Group 2's second Why paragraph still narrated the
review transcript, which this round removed from both groups, so the message
described a file the commit does not touch. It now describes the Step 3 capture
contract that the staged plan actually adds.

The `a.commit` amendment and the validation-plan row are review metadata. The
blank line is a change to a tracked production file outside the exempt
categories, so it is substantive and forbids a commit-ready recommendation in
this round.

### Findings returned to the writer for step 2 code-reviewer round 2

The transcript left both `a.commit` groups, and that overcorrects the round-one
finding. That finding was about two hand-edited hunks inside published Step 1
rounds, not about the file's membership; reverting those hunks fixed it, and the
staged bytes already equal `HEAD`. Dropping the path as well means the entire
Step 2 review record, five appended entries, never lands with the Step 2 commit,
which is the same gap the Step 1 round-one answer raised and the writer closed
then by staging the transcript in the documentation group. Restoring it changes
staged membership, so the decision is the writer's, not a reviewer repair.

`test_code_review_evidence_tdd.py` now measures exactly 550 lines. The Step 2
addendum asks for split fixture support as either evidence test module
approaches 550, so the plan's own threshold is reached rather than approaching.
Splitting a test module is a structural decision and stays with the writer.

### Validation evidence for step 2 code-reviewer round 2

Every command in the resolved set ran after the repairs. `ghog day` reports
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,747 tests,
with the full phase at 1 minute 30.1 seconds and a slowest call of 0.43 seconds.
The plan completion grep returns 60 matches across the three production modules
and both test packages. `bin/code_review_evidence.bat --help` exits 0 from the
repository root with no environment setup. `git diff --cached --check` exits 0,
which is the addition this request contributed to the set.

No resolver drift: the request's four commands are the project default plus two
plan additions plus one request addition, and the current resolver produces the
same set.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 550, 328, and
490 for the three staged test modules. All are below the 650-line ceiling.

### a.commit assessment for step 2 code-reviewer round 2

Accurate after the wording amendment above. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set both
before and after the repairs: two ordered groups, conventional subjects, exact
membership, and no duplicate or missing path. Both repairs landed inside
existing group members, so membership, grouping, and order are unchanged. No
commit was created.

### Non-blocking observations for step 2 code-reviewer round 2

The seven single-name `from tools.code_review_evidence_common import (X as _Y)`
statements are required, not accidental: `pyproject.toml` sets no
`combine-as-imports`, so isort's default splits aliased imports. A repository-wide
`[tool.ruff.lint.isort] combine-as-imports = true` would collapse them into one
statement and reclaim the twelve lines discussed above, but that setting is
outside this step.

`capture_index_tree` still calls `run_cross_platform_git_command` directly
instead of the new `run_git_evidence`, which keeps `subprocess` and
`GitCommandOptions` imported in the evidence hub for one call site. It is the
one primitive that did not move to the common boundary, and its distinct error
message is a defensible reason to leave it.

The duplicate `## Round 1 by human - Step 2` heading pair remains in the
transcript. It was rendered before the store began qualifying human headings by
outcome, and correcting it would mean editing published protocol bytes.

### Final reviewer decision for step 2 code-reviewer round 2

Decision: changes-requested. The blank-line repair is a change to a tracked
production file outside the exempt categories, and the transcript-membership
question needs a writer decision that a reviewer cannot make. Neither concerns
the implementation itself, which is complete, correct, and green on every
resolved validation command; round two accepted and closed every round-one
finding without regression. This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor - Step 2

- Recorded: 2026-08-16T19:22:10+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 3

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 3

### Code review evidence for step 2 code-reviewer round 3

request_index_tree: 3a95958c36bb108e951c4a672339809d740a9d52
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 3

Step 2 is fully implemented after accepting all round-two repairs and returned
findings. The validation-state spacing and architecture counts are corrected,
`a.commit` describes its actual groups, the complete protocol transcript is
restored to the documentation group without changing historical bytes, and the
550-line evidence test is split into focused 221-line core and 363-line
defensive-boundary modules.

The final `ghog day` passed all 1,747 tests with zero failures, 100% coverage,
zero duration outliers, and a slowest call of 0.44 seconds. The full phase took
1 minute 17.3 seconds. Static checks passed, staged whitespace is clean, every
production and test module remains below the repository ceiling, and bounded
validation capture remains O(n) over explicit paths.

### Implementation report for step 2 code-reviewer round 3

The writer retained the reviewer's production blank-line repair, corrected
line counts of 479, 105, 248, and 202 in the validation plan, and retained the
reviewer's Group 2 narrative correction. The evidence test threshold is now
closed structurally: core capture and retained-lifecycle behavior stays in the
original module, while malformed payload, unsafe path, Git failure, and IO
boundary cases live in `test_code_review_evidence_boundaries_tdd.py`.

The writer restored `review.code.v0.11.0.code-reviewer.md` to Group 2. Its
staged content is protocol-generated, its historical Step 1 bytes and duplicate
human headings were not edited, and the exact-path group command can include
later Step 2 protocol entries. The validation plan records that decision and
the final green Groundhog evidence.

### Change summary for step 2 code-reviewer round 3

The staged round-three subject contains fourteen paths.

Group 1 contains eleven production and test paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`

Group 2 contains the implementation plan, validation plan, and protocol
transcript. The root `a.commit` uses `fix(code-reviewer): bound evidence paths`
followed by `docs(code-reviewer): record step 2 validation`. The nine
review-exchange-core paths remain unstaged and outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 3

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-two feedback is accepted with no disagreement. The writer retained
the reviewer's three staged repairs, restored the protocol transcript to Group
2 as the complete Step 2 review record, and split the 550-line evidence test by
core behavior versus defensive boundaries. The test package docstring,
validation record, and `a.commit` membership and narrative were updated to
match those decisions.

Historical transcript bytes, including the duplicate human headings rendered
before the protocol fix, remain untouched. The unrelated forced-reclaim
implementation remains unstaged and in no `a.commit` group.

### Reviewer focus for step 2 code-reviewer round 3

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer - Step 2

- Recorded: 2026-08-16T20:09:00+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 3

The request-time index tree `3a95958c36bb108e951c4a672339809d740a9d52` matched
the live index exactly before assessment, so this round assessed the published
subject. After one reviewer repair the index tree is
`4531ab6b78e3d763d3b920f2456eefb6e3cfc4cb`. The staged set holds exactly the
fourteen paths the change summary lists, with no unrelated staged content.

The transcript is correctly `MM`: its staged bytes are a pure append over
`HEAD`, with no removed line anywhere in the staged diff, and the unstaged
portion is this round's protocol-generated request. The nine forced-reclaim
paths remain unstaged and outside both groups.

### Round 2 findings verified in step 2 code-reviewer round 3

Both returned findings are closed and all three round-two repairs are retained
without disagreement.

The transcript is back in Group 2 with its historical Step 1 bytes untouched, so
the complete Step 2 review record now lands with the step. The blank line before
`@dataclass` is retained, and the corrected architecture counts of 479, 105,
248, and 202 re-measure exactly against the current files. The Group 2 narrative
kept the reviewer's correction and extends it accurately now that the transcript
is a member again.

The 550-line evidence module is split into a 221-line core module and a
363-line boundary module, both under the plan's threshold. The split is a clean
move rather than a rewrite: the union of the two modules holds the same thirteen
test functions under the same names, and every distinctive boundary message,
including `code/code`, `unsafe token`, `paths disagree`, and
`Git evidence command failed`, still appears with its assertion. The package
docstring was updated to match.

### Repairs made in step 2 code-reviewer round 3

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The feature
integrity paragraph claimed the transcript carries "both reclaim entries". It
carries one. The round-two lease reclaim appended nothing, which is the
documented contract for an ordinary reclaim: it renews the lease without
touching request, answer, or transcript bytes. The transcript holds exactly one
`human-reclaim-round-1` entry, and the paragraph now says so.

That is a reviewed-step validation record and therefore review metadata, not a
substantive change. It is the only repair in this round.

### Findings returned to the writer for step 2 code-reviewer round 3

The evidence tests do not execute Git, and the literal-pathspec guarantee is
unverified. `tests/unit/tools/test_code_review_evidence/conftest.py`, tracked
since `b592199` and unchanged by this step, installs an autouse fixture that
replaces `subprocess.run` with an in-memory Git for the whole package. Its
`_run_ls_files` handler branches on `command[1]` alone and never reads the
arguments after `--`, so the `:(literal)` pathspecs built at
`tools/code_review_evidence_validation_state.py:154` are discarded before they
reach any matcher.

The consequence is that the step's headline guarantee cannot fail. Deleting
`:(literal)` from that line and running `ghog single
tests/unit/tools/test_code_review_evidence` reports `fail=0 exit=0`; the
reviewer ran exactly that and restored the file from the index afterwards. The
`literal[1].txt` fixture exists precisely to catch glob interpretation and
cannot detect it. The captured result is bounded only because
`_selected_digests` filters in Python afterwards, so Git's own filtering is
untested for the tracked, ignored, and untracked classifications alike.

This contradicts the step's own contract. The plan's Step 2 tests-first list
requires temporary Git repositories, and design Q06 requires testing public
entry points over real temporary Git repositories. Only the module-scoped
`staged_repository` fixture in the core module is instantiated before the
function-scoped autouse patch, so it alone sees real Git.

The reviewer did not repair this. Both routes out, teaching the fake to honour
pathspecs or exempting one case from the autouse fake so it runs real Git, are
test-architecture decisions that trade directly against the runtime reduction
`b592199` deliberately bought. That trade belongs to the writer.

### Validation evidence for step 2 code-reviewer round 3

Every command in the resolved set ran after the repair. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,747
tests, with the full phase at 1 minute 30.3 seconds and a slowest call of 0.44
seconds. The force flag was needed because an unforced `ghog day` short-circuits
with "No Python file changed since the last green walk", which is evidence of an
unchanged tree rather than of a passing suite. The plan completion grep returns
60 matches. `bin/code_review_evidence.bat --help` exits 0 from the repository
root. `git diff --cached --check` exits 0.

No resolver drift: the four commands are the project default plus two plan
additions plus one request addition, and the current resolver produces the same
set.

Note that the 100% coverage figure counts lines executed against the fake Git
described above, so it does not by itself establish the real-Git behavior of
`_listed_path_set`.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 221, 363, 328,
and 490 for the four staged test modules. All are below the 650-line ceiling and
the two evidence test modules are below the plan's 550-line split threshold.

### a.commit assessment for step 2 code-reviewer round 3

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership over all fourteen paths,
and no duplicate or missing path. Both group narratives now match their
membership, including the restored transcript. The repair landed inside an
existing Group 2 member. No commit was created.

### Non-blocking observations for step 2 code-reviewer round 3

The split gives the package a third byte-identical `_git` helper. The Step 2
addendum asked for split fixture support, and Step 6 already plans a
`fixtures.py` for shared repository construction, which is its natural home.

The duplicate `## Round 1 by human - Step 2` heading pair now lands in the
commit through Group 2. It was rendered before the store began qualifying human
headings by outcome, it cannot recur, and correcting it would mean rewriting
published protocol bytes.

The seven single-name aliased imports per module remain isort's default output
because `pyproject.toml` sets no `combine-as-imports`, and `capture_index_tree`
still calls `run_cross_platform_git_command` directly rather than the new
`run_git_evidence`. Both were raised in round two and neither is a defect.

### Final reviewer decision for step 2 code-reviewer round 3

Decision: changes-requested. Everything returned in round two is closed cleanly
and the implementation is otherwise complete and green, but the step's central
bounded-capture guarantee is proven only by a Python-side filter: the test that
exists to verify it passes with the mechanism removed. That gap needs a writer
decision on test architecture, which a reviewer cannot make inside this step.
This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-3 -->

## Round 4 by requestor - Step 2

- Recorded: 2026-08-16T21:16:25+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: request

### Review identity for step 2 code-reviewer round 4

Umbrella draft: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 2
Review round: 4

### Code review evidence for step 2 code-reviewer round 4

request_index_tree: 09d7b30aae95368231feeda6637d514355bf545e
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'interactive=False|umbrella_digest|validation_state|retire_manifest' tools/code_review_evidence.py tools/code_review_evidence_cli.py tools/git_batch_commit_validation.py tests/unit/tools/test_code_review_evidence tests/unit/tools/test_git_batch_commit_validation (sources: plan)
- bin/code_review_evidence.bat --help (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 2 code-reviewer round 4

Step 2 is fully implemented after accepting the round-three blocking finding.
The evidence package keeps its fast in-memory Git fixture by default, while one
explicit boundary contract opts out and uses a temporary real repository. That
contract records the arguments and output of all three production `git
ls-files` calls and proves that tracked, ignored, and untracked bracketed names
are selected literally while their glob-shaped decoys are excluded.

The final `ghog day` passed all 1,748 tests in 1 minute 23.8 seconds with zero
failures, 100% coverage, zero duration outliers, and no exclusions. The slowest
call was 0.42 seconds against the 0.50-second ceiling. Static checks passed,
`git diff --cached --check` is clean, the evidence test modules remain at 221
and 456 lines, and the staged subject contains exactly the fifteen paths named
by `a.commit`.

### Implementation report for step 2 code-reviewer round 4

The writer added an explicit `real_git_commands` opt-out to the evidence
package's autouse subprocess fixture. A module-scoped temporary repository now
contains literal-versus-glob pairs for tracked, ignored, and untracked files;
the production capture runs against real Git and returns the recorded command
arguments, Git output, and validation state to the assertion phase. The test
therefore proves Git's filtering rather than duplicating it in the in-memory
fake, while moving only costly repository and subprocess setup outside the
measured call phase.

The reviewer's round-three validation-plan repair is retained. The validation
record now includes the real-Git contract, the exact 1,748-test Groundhog
result, the 0.42-second slowest call, current test-module counts, and the
round-three protocol append. All earlier production, documentation, transcript,
and `a.commit` repairs remain intact.

Groundhog also identified two unrelated forced-reclaim tests just above the
project-wide ceiling. Their expensive journey preconditions moved into fixtures
without dropping assertions; that review-exchange-core test file remains
unstaged and outside this Step 2 review subject.

### Change summary for step 2 code-reviewer round 4

The staged round-four subject contains fifteen paths.

Group 1 contains twelve production and test paths:

- `tools/code_review_evidence.py`
- `tools/code_review_evidence_common.py`
- `tools/code_review_evidence_validation_state.py`
- `tools/code_review_evidence_cli.py`
- `tools/code_review_request.py`
- `tools/__init__.py`
- `tests/unit/tools/test_code_review_evidence/__init__.py`
- `tests/unit/tools/test_code_review_evidence/conftest.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_boundaries_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_tdd.py`
- `tests/unit/tools/test_code_review_evidence/test_code_review_evidence_cli_tdd.py`
- `tests/unit/tools/test_code_review_request/test_code_review_request_tdd.py`

Group 2 contains the implementation plan, validation plan, and protocol
transcript. The root `a.commit` uses `fix(code-reviewer): bound evidence paths`
followed by `docs(code-reviewer): record step 2 validation`. The nine
review-exchange-core paths and `.vscode/settings.json` remain unstaged and
outside both groups.

### Human guidance and writer response for step 2 code-reviewer round 4

Human guidance: Human recovery decision: resume step 2 round 1 in place.

The 1,800-second reviewer wait expired while this exchange was being driven as a
manual back-and-forth, so the recorded escalation describes a stopped handoff
rather than a failed round. The round-1 request, its immutable evidence, and the
transcript are intact and remain authoritative.

The human authorized the forced reclaim added to the shared protocol for exactly
this case, rather than `resolve` or `archive`. Both of those would have retired
the live evidence and opened a renumbered round that needs a replacement
request, which no part of this manual handoff requires.

Writer response: All round-three feedback is accepted with no disagreement. The writer chose the
real-Git route requested by the plan and design: the package fake remains the
fast default, but one explicit contract bypasses it and observes Git's actual
literal-pathspec filtering for every validation-state path class. Every prior
assertion remains, and the new command and output assertions fail if
`:(literal)` is removed.

The reviewer-authored correction about ordinary reclaim behavior is retained.
Historical transcript bytes remain untouched, the round-three request and
answer are a pure append, and the unrelated forced-reclaim implementation and
test-speed correction remain unstaged and in no `a.commit` group.

### Reviewer focus for step 2 code-reviewer round 4

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-4 -->

## Round 4 by reviewer - Step 2

- Recorded: 2026-08-16T21:32:17+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: answer

### Assessed staged state for step 2 code-reviewer round 4

The request-time index tree `09d7b30aae95368231feeda6637d514355bf545e` matched
the live index exactly before assessment, so this round assessed the published
subject. After one polishing repair the index tree is
`6c80f7db17e8f6de9fab02dfb30019a45e841357`. The staged set holds exactly the
fifteen paths the change summary lists.

The transcript remains correctly `MM`: its staged bytes are a pure append over
`HEAD` with no removed line anywhere in the staged diff, and the unstaged
portion is this round's protocol-generated request. The nine
review-exchange-core paths and `.vscode/settings.json` stay unstaged and outside
both groups, as the change summary states.

### Round 3 finding verified in step 2 code-reviewer round 4

The blocking finding is closed, and the reviewer proved it the same way it was
raised rather than accepting the writer's report.

Removing `:(literal)` from `tools/code_review_evidence_validation_state.py:154`
and running `ghog single tests/unit/tools/test_code_review_evidence` now reports
`fail=1 exit=2` on
`test_validation_pathspecs_filter_real_git_literally`. In round three the same
mutation reported `fail=0 exit=0`. The file was restored from the index
afterwards and its content re-verified.

An independent probe outside this repository confirms the behavior the contract
depends on. Against a real repository holding `literal[1].txt` beside a
`literal1.txt` decoy, `git ls-files -- 'tracked/literal[1].txt'` returns both
names, while `git ls-files -- ':(literal)tracked/literal[1].txt'` returns only
the bracketed one. The same holds for the `--others` and
`--others --ignored` forms, so all three production calls are genuinely bounded.

The opt-out is well placed. A `real_git_commands` fixture whose presence in
`request.fixturenames` makes the autouse fake return early keeps the fast
in-memory Git as the package default while one contract observes real Git, which
is what the plan's tests-first list and design Q06 require. The module-scoped
repository and capture fixtures keep process setup outside the measured call, so
the suite kept zero outliers.

### Repairs made in step 2 code-reviewer round 4

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. Two paragraphs
carried ragged wrapping where this round's inserted sentences were not reflowed,
leaving `threshold. One explicit` and `nothing, because an ordinary` as short
lines mid-sentence against the document's consistent width. Both paragraphs are
rewrapped with no wording change.

Polishing-only: this is a reviewed-step validation record, it changes no code,
test, acceptance behavior, or commit grouping, and it therefore does not forbid
the recommendation below. It is the only repair in this round.

### Findings returned to the writer for step 2 code-reviewer round 4

None. No finding from any earlier round remains open, and this round introduced
none.

### Precision note on the proven guarantee for step 2 code-reviewer round 4

Worth recording so Step 3 does not over-claim what the contract establishes. Of
the new test's three assertion groups, the pathspec-argument assertion and the
raw `git ls-files` output assertion both fail under the mutation. The
`ValidationState` assertions do not, because a bare pathspec still matches the
bracketed file exactly and `_selected_digests` discards the extra decoy in
Python afterwards.

So the contract proves the correct thing: `:(literal)` bounds what Git itself
selects, which is where the cost and the surprise live. It does not claim that
`ValidationState` would be wrong without it. Step 3 should describe the
guarantee in those terms.

### Validation evidence for step 2 code-reviewer round 4

Every command in the resolved set ran after the repair. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,748
tests, with the full phase at 1 minute 34.0 seconds and a slowest call of 0.41
seconds. The request records 1 minute 23.8 seconds and 0.42 seconds from the
writer's run; wall-clock differs between machines and runs while every reported
outcome field agrees, and the outlier count is zero in both.

The plan completion grep returns 61 matches.
`bin/code_review_evidence.bat --help` exits 0 from the repository root.
`git diff --cached --check` exits 0. No resolver drift: the four commands are
the project default plus two plan additions plus one request addition, and the
current resolver produces the same set.

Line counts are 479, 105, 248, 202, and 461 for the evidence hub, common
boundary, validation-state module, CLI, and request renderer, and 221, 456, 328,
257, and 490 for the staged test modules and package fixture. All are below the
650-line ceiling, and both evidence test modules are below the plan's 550-line
split threshold. Every number the validation plan states re-measures exactly.

### a.commit assessment for step 2 code-reviewer round 4

Accurate, no amendment needed. Running the step's own validator,
`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)`, returns zero diagnostics against the exact staged set: two
ordered groups, conventional subjects, exact membership over all fifteen paths,
and no duplicate or missing path. Both narratives match their membership, and
both `What` lists now name the real-Git contract and the 1,748-test result. The
repair landed inside an existing Group 2 member. No commit was created.

### Non-blocking observations for step 2 code-reviewer round 4

`assert real_git_commands is True` can never fail, since the fixture returns a
constant. It reads as a contract assertion but its real job is to request the
fixture so the autouse fake stands down. A short comment saying that would age
better than the assertion.

The duplicate `## Round 1 by human - Step 2` heading pair still lands through
Group 2. It was rendered before the store began qualifying human headings by
outcome, it cannot recur, and correcting it would mean rewriting published
protocol bytes.

The package now carries three byte-identical `_git` helpers, and Step 6 already
plans a `fixtures.py` that is their natural home. The isort import style and
`capture_index_tree` not routing through `run_git_evidence` remain as described
in earlier rounds. None of these is a defect.

### Final reviewer decision for step 2 code-reviewer round 4

Decision: commit-ready. Step 2 is fully implemented against its plan step; every
finding from rounds one through three is closed and independently verified, the
round-three blocking finding by mutation and by direct Git probe; `a.commit`
matches the staged set exactly; and all four resolved validation commands are
green with 100% coverage and zero outliers. The only repair in this round is
polishing-only, so it does not forbid this recommendation.

This recommendation is advisory. It authorizes no commit, and the human gate
remains the sole authority for the `Commit` choice.

<!-- review-entry-id: answer-round-4 -->

## Round 4 by human - Step 2 - human-confirmation

- Recorded: 2026-08-16T21:44:19+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: C:/Users/vonc/git/llm-shared/docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: C:/Users/vonc/git/llm-shared/docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Rework and review again
Outcome: another-round
Guidance: Rework and review again.

No Markdown file may carry a linter warning under the repository
`.markdownlint.json`, and no document may repeat a heading title. MD024 and
MD025 are not negotiable and neither rule may be disabled to make a file pass.

The `bis` suffix hand-written onto the published `human-reclaim-round-1` heading
is not acceptable: it is a counter, it edits protocol bytes by hand, and no
renderer would emit it. Restore both round-one human headings to exactly what
the current store renders, which qualifies a human entry by its outcome, and fix
every remaining duplicate or warning at its source rather than in the rendered
output.

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 5 by human - Step 2 - human-completion

- Recorded: 2026-08-17T09:59:07+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 2
- Outcome: human-completion

The human explicitly decides to close Step 2 round 5 after confirming that the requested rework and the owning commit action have already completed. This forced completion retires the abandoned artifact-free round; it does not claim that round 5 received a reviewer answer or manufacture a convergence recommendation.

Round 4 reached the convergence gate with a commit-ready recommendation, but the human selected Rework and review again. That durable choice removed the round-4 answer and advanced coordination to round 5. The rework and commits then proceeded without publishing the replacement round-5 request, so its active artifact-free lease expired and classified as abandoned-mid-round.

<!-- review-entry-id: human-completion-round-5 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-08-17T10:01:14+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 code-reviewer round 1

request_index_tree: a7b893d85630d401806f8221bfef293251d11e70
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'code_review_evidence.bat|umbrella_digest|validation_state' instructions/implementation-check.md tests/unit/tools/test_implementation_check_reviewer_mode (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 3 code-reviewer round 1

Step 3 is fully implemented against its current completion criteria. The
canonical implementation check exposes an explicit advisory reviewer mode,
delegates every Git and filesystem evidence operation to the Step 2 launcher,
uses the same post-criteria comparisons after Yes and No results, limits writes
to the reviewed validation rows, and suppresses writer-owned umbrella
completion.

The final `ghog day` passed all 1,759 tests with zero failures, 100% coverage,
zero duration outliers, and no exclusions; its full phase completed in 1 minute
39.6 seconds. The two calls previously measured above the 0.50-second ceiling
were shortened by halving the double-identity property examples and moving the
persisted convergence-gate setup outside the measured call phase. Static checks
and `git diff --cached --check` pass. Scope construction is O(n) over explicit
paths, the 187-line instruction remains canonical, and the focused test module
is 94 lines.

The implementation plan also carries Q09 through Q11 for independent
specification review. Their recommendations clarify artifact-path declaration,
post-publication manifest retirement, and the structure-versus-behavior test
boundary; the specification exchange remains separate and request-pending.

### Implementation report for step 3 code-reviewer round 1

The implementation-check instruction now enters reviewer mode only when the
caller explicitly assigns the advisory code-review role. Before criteria it
builds a first-seen ordered `validation_path_set`, captures umbrella and
validation state, records candidate repair blobs, and writes retained evidence.
Outside reviewer mode, the existing writer-owned status, umbrella, and handoff
rules are unchanged.

Both Yes and No sections repeat the exact `umbrella-digest` compare and
`validation-state` capture/compare commands over the same ordered path set. A
changed umbrella or other tracked side effect is returned as
`changes-requested` and left in place; only attributable reviewed-step
validation-row patches may be staged. `Umbrella draft: none` records typed
not-applicable evidence, and manifest retirement stays after successful answer
publication.

Five focused structure tests anchor the executable commands, both criteria
paths, minimum path scope, write restrictions, changed-file retention,
attribution, lifecycle, and absent-umbrella behavior. Existing Step 2
temporary-repository tests remain the behavior proof for the delegated CLI.

### Change summary for step 3 code-reviewer round 1

The staged Step 3 subject contains six paths.

Group 1 contains the canonical instruction and its focused test package:

- `instructions/implementation-check.md`
- `tests/unit/tools/test_implementation_check_reviewer_mode/__init__.py`
- `tests/unit/tools/test_implementation_check_reviewer_mode/test_implementation_check_reviewer_mode_tdd.py`

Group 2 contains the implementation plan with Q09 through Q11, the Step 3
validation record, and the specification-review transcript:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.plan.v0.11.0.code-reviewer.md`

The root `a.commit` uses `feat(code-reviewer): bound implementation checks`
followed by the required `docs(code-reviewer): record step 3 validation`.
Every staged path belongs to exactly one group.

### Writer response for step 3 code-reviewer round 1

Writer response: Round 1 has no earlier Step 3 code-review feedback. The writer implemented the
exact instruction and test files named by the plan, recorded the successful
implementation check, and prepared two dependency-ordered commit groups.

The three plan questions are disclosed rather than hidden from the code
reviewer. Their recommended answers match the current implementation, while
the separate specification-review exchange remains available for independent
wording and consolidation feedback.

### Reviewer focus for step 3 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-08-17T10:40:44+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 3
- Outcome: answer

### Assessed staged state for step 3 code-reviewer round 1

The request-time index tree `a7b893d85630d401806f8221bfef293251d11e70` matched
the live index exactly before assessment, so this round assessed the published
subject. After three reviewer repairs the index tree is
`312000d1249bc7274c82a01d641cfd3133ac25f7`. The staged set holds exactly the six
paths the change summary lists.

The review-exchange-core work and its test-speed corrections stay unstaged and
outside both groups, as do `instructions/code-review-requestor.md`,
`instructions/review-requestor.md`, and
`docs/v0.11.0/design.v0.11.0.review-exchange-core.md`.

### Implementation assessment for step 3 code-reviewer round 1

Step 3 is implemented against the numbered plan. The instruction gates reviewer
mode on an explicit advisory assignment, leaves every writer-owned rule outside
that branch untouched, and states plainly that reviewer mode never completes an
umbrella row, commits, or reverts a detected change. The setup section builds a
first-seen ordered `validation_path_set` over staged reviewed-step paths, the
validation plan, and known validation artifacts, then captures umbrella digest,
validation state, and pre-repair blobs before criteria run.

Both result sections repeat the same three comparison commands over the same
ordered scope, so a failing check cannot skip the boundary. An applicable
changed umbrella and any other tracked difference are `changes-requested`
findings left in place, ignored artifacts are accepted, and only attributable
reviewed-row patches may be staged. `Umbrella draft: none` records typed
not-applicable evidence, and retirement stays with the caller after publication.
Line budgets hold: the instruction is 195 lines and the focused module 97.

### Repairs made in step 3 code-reviewer round 1

Staged: `tests/unit/tools/test_implementation_check_reviewer_mode/test_implementation_check_reviewer_mode_tdd.py`.
The step exists to prove the instruction delegates to
`bin/code_review_evidence.bat` rather than describing equivalent shell
operations, and no test asserted the launcher at all. Replacing all thirteen
`bin/code_review_evidence.bat` references with a bare `git` left every one of
the five tests green. The repair asserts the launcher in the setup section and
in both result sections; the same mutation now fails two tests. The instruction
was restored from the index after each experiment.

Staged: `instructions/implementation-check.md`. Two prescribed commands were not
executable as written. Every launcher path operand must be repository-relative,
and every request in this exchange declares the umbrella as an absolute path:
`umbrella-digest capture C:/Users/.../draft.v0.11.0.review-mode.md` returns
`ERROR: umbrella path must be repository-relative` with exit `2`, while the
relative form returns a digest with exit `0`. The instruction also said to
"retain its JSON" and then passed that retained value where the CLI reads a
repository-relative file. The repair states the operand convention once: paths
are repository-relative, and each retained JSON is written to its own ignored
root `a.*` file so no retained evidence becomes a tracked side effect of the
check the instruction is running.

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The coverage
record measured the test module at 94 lines; the repair above makes it 97.

Substantive: the first two change the step's tests and its acceptance behavior,
so they forbid a commit-ready recommendation in this round. The third is review
metadata.

### Findings returned to the writer for step 3 code-reviewer round 1

`docs/v0.11.0/review.plan.v0.11.0.code-reviewer.md` is staged in Group 2 and
carries six MD024 duplicate headings. It is the only file with a duplicate
heading among the repository's 344 tracked Markdown files, and it breaks the
standing requirement recorded at the previous human gate, where MD024 and MD025
were declared non-negotiable.

The cause is a second specification exchange over the same plan. Exchange one
ran rounds one through four to a `Consolidate` confirmation at line 1025;
exchange two opens at line 1027 with round one again. Both halves of the append
repeat:

- the store-generated `## Round 1 by requestor` at lines 10 and 1027, which
  carries no exchange discriminator and, for specification review, has no
  `- Step N` suffix to separate it either; and
- five authored `###` headings, from `Review identity` to `Reviewer focus`,
  which the requestor left unqualified even though
  `instructions/review-requestor.md` names this exact case and prescribes the
  exchange as the discriminator, as in `## Round 1 by requestor (exchange 2)`.

The durable entry identity `request-round-1` is now also duplicated, at lines 44
and 1076, so its footer comment appears twice and a repair marker no longer
identifies one entry. That is the same identity-collision class the shared core already
addresses for repeated human transitions through `TranscriptEntry.occurrence`;
extending that mechanism to request and answer appends would close it, but the
right discriminator for a restarted exchange is the exchange rather than an
attempt, which is a core design decision.

The reviewer did not repair this. The generated heading and identity come from
the store and need that core discriminator, and the authored headings sit inside
published protocol bytes that a reviewer must not hand-edit.

### Validation evidence for step 3 code-reviewer round 1

Tests and coverage are green and the duration gate is not, for reasons outside
this step. `ghog day --force` reports `fail=0 warn=0 xfail=0 cov=100` over 1,759
tests with `exit=8` from `outliers=4`. All four are in files this effort has
never touched: two `git_history_dashboard` calls at 1.20 and 0.67 seconds and
two `test_code_review_requestor_io_acceptance_tdd.py` calls at 0.57 and 0.53
seconds.

The measurements are load artifacts rather than a regression. The same two
acceptance calls measured 0.41 seconds in a run 40 minutes earlier against
identical bytes, the full phase has drifted from 1m 31s to 1m 58s across
successive runs with no code change between them, and the reported outlier set
changes every run. One genuine outlier did appear and was fixed: the
double-identity property test measured 0.55 seconds, so its examples were
halved to ten, and it no longer appears.

The plan completion grep returns 21 matches, and `git diff --cached --check`
exits cleanly. No resolver drift: the three commands are the project default
plus one plan addition plus one request addition, and the current resolver
produces the same set.

Markdown, checked against the repository `.markdownlint.json` with MD013 off and
MD033 limited to `img`: `instructions/implementation-check.md`, both plan
documents, and the code transcript are clean. Only the specification transcript
above is not.

### a.commit assessment for step 3 code-reviewer round 1

Accurate, no amendment needed. `validate_commit_plan(parse_clipboard_content(
a.commit, interactive=False), staged_paths)` returns zero diagnostics against
the exact staged set: two ordered groups, conventional subjects, exact
membership over all six paths, and no duplicate or missing path. All three
repairs landed inside existing group members, so membership, grouping, and order
are unchanged. No commit was created.

### Non-blocking observations for step 3 code-reviewer round 1

The step's completion grep passes incidentally. Its three tokens produce 21
matches, every one in the instruction and none in the test package the criterion
names, and `umbrella_digest` and `validation_state` match only the JSON variable
names `umbrella_digest_before` and `validation_state_after`, because the real
CLI subcommands are hyphenated. The criterion is therefore satisfied by variable
naming rather than by the contract it was written to pin.

The clause "rather than describing equivalent shell operations" remains
unasserted. This round's repair proves the launcher is named; nothing yet proves
that raw shell prose is absent, which would need a negative assertion over the
reviewer sections.

The Yes and No sections carry byte-identical three-command lists. The plan
requires both result paths to name the commands, so the duplication is
deliberate, but the two copies can drift apart without any test noticing.

Repository-wide Markdown still holds 103 findings outside MD024, unchanged from
the previous gate: MD032 29, MD033 21, MD047 20, MD022 15, MD031 4, MD012 3,
MD009 3, and MD040 2, spread across roughly forty files unrelated to this step.

### Final reviewer decision for step 3 code-reviewer round 1

Decision: changes-requested. The staged subject contains the only duplicate
headings left in the repository and breaks the requirement the human set at the
previous gate, and that fix needs a core discriminator decision a reviewer
cannot make. Two of this round's three repairs are substantive in their own
right. The reviewer-mode instruction itself is otherwise complete and well
aimed, and its remaining gaps are now anchored by tests rather than by prose.
This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor - Step 3 (exchange 3)

- Recorded: 2026-08-17T13:17:46+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 3
- Outcome: request

### Review identity for step 3 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 code-reviewer round 2

request_index_tree: b517576809a9739c92c376e4a43c8cc1c5f781bf
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'code_review_evidence.bat|umbrella_digest|validation_state' instructions/implementation-check.md tests/unit/tools/test_implementation_check_reviewer_mode (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 3 code-reviewer round 2

Step 3 is fully implemented after round 1. Reviewer mode remains explicitly
advisory, delegates every executable comparison to
`bin/code_review_evidence.bat`, builds one ordered staged-plus-artifact scope,
and applies the same umbrella, validation-state, and tracked-difference checks
after both Yes and No criteria results.

All round-1 findings are closed. The staged tests now pin the launcher in setup
and both result paths. The instruction uses repository-relative launcher
operands and stores retained JSON in distinct ignored root `a.*` files. The
validation record measures the focused module at 97 lines and records the
current 1,767-test green walk.

The specification transcript collision was repaired through the shared core,
not by editing protocol bytes manually. Its restarted request is now headed
`Round 1 by requestor (exchange 2)`, every authored heading carries the same
discriminator, and the footer is `request-round-1-exchange-2`. The forward
renderer and guarded legacy-repair implementation remain unstaged with the
other review-exchange-core work, outside this Step 3 subject.

The exact staged tree is `b517576809a9739c92c376e4a43c8cc1c5f781bf`.
It contains six paths in the same two `a.commit` groups, with no membership or
ordering drift. `git diff --cached --check` is clean. The forced Groundhog walk
passes 1,767 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0
exit=0`; its slowest call is 0.40 seconds against the 0.50-second ceiling.

### Implementation report for step 3 code-reviewer round 2

Round 1 added three staged repairs: launcher assertions in the reviewer-mode
structure tests, executable repository-relative and retained-file wording in
the canonical implementation check, and the resulting 97-line validation
measurement. Those substantive repairs remain staged.

The blocking repeated-exchange defect was fixed at the protocol source. Request
and answer entries now derive unique `exchange N` headings and footers across
restarted exchanges. A requestor-only, marker-backed recovery operation
re-renders only the final pending legacy request while preserving its durable
request and all earlier transcript entries. That operation repaired the staged
plan transcript, eliminating all six MD024 duplicates and the duplicated entry
identity.

The protocol implementation, its focused tests, module splits, and test-speed
fixtures are deliberately unstaged because they belong to the separate
review-exchange-core effort. Only the repaired transcript byte result remains
inside Step 3 Group 2.

### Change summary for step 3 code-reviewer round 2

The staged subject contains exactly these six paths:

- `instructions/implementation-check.md`
- `tests/unit/tools/test_implementation_check_reviewer_mode/__init__.py`
- `tests/unit/tools/test_implementation_check_reviewer_mode/test_implementation_check_reviewer_mode_tdd.py`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`
- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`
- `docs/v0.11.0/review.plan.v0.11.0.code-reviewer.md`

`a.commit` assigns the first three paths to `feat(code-reviewer): bound
implementation checks` and the last three to `docs(code-reviewer): record step
3 validation`. The Why narratives still reference the umbrella draft, topic
draft, feature request, design, implementation plan, and validation plan in
their two narrative paragraphs. No group, order, subject, or membership change
was needed; only the recorded suite count advanced to 1,767.

### Writer response for step 3 code-reviewer round 2

Writer response: The writer accepts every round-1 repair and finding without disagreement.

The launcher boundary is now asserted, the two command examples are executable
with repository-relative operands and retained ignored files, and the
validation line count is current. The repeated specification exchange no
longer creates duplicate generated headings, authored headings, or entry
footers; the live legacy entry was repaired through the newly covered protocol
operation. No published transcript bytes were hand-edited.

Please verify that all round-1 findings are closed, the exact staged tree and
two `a.commit` groups remain coherent, and the full gate supports a
`commit-ready` recommendation.

### Reviewer focus for step 3 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-round-2-exchange-3 -->

## Round 2 by reviewer - Step 3 (exchange 3)

- Recorded: 2026-08-17T15:00:26+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 3
- Outcome: answer

### Assessed staged state for step 3 code-reviewer round 2

The request-time index tree `b517576809a9739c92c376e4a43c8cc1c5f781bf` matched
the live index exactly before assessment, and it is unchanged afterwards because
this round needed no repair. The staged set holds exactly the six paths the
change summary lists.

The staged subject carries no hidden edit. Five of the six paths add lines only;
the validation plan's seven deletions are its replaced skeleton placeholders and
its `Not started` sentence. The specification transcript is a pure append of 51
lines, and because that append is new relative to `HEAD` the reviewer checked it
against renderer output rather than against the absent-deletion signal that
would hide an edit inside an uncommitted block.

The review-exchange-core implementation, its module splits, its focused tests,
and its timing fixtures stay unstaged and outside both groups.

### Round 1 findings verified in step 3 code-reviewer round 2

All findings are closed, each verified independently rather than accepted from
the report.

The blocking duplicate-heading defect is fixed at the protocol source, not in
the rendered bytes. The store now appends `(exchange {occurrence})` to a request
or answer heading and the matching suffix to its footer identity, so the
restarted specification exchange renders `## Round 1 by requestor (exchange 2)`
with footer `request-round-1-exchange-2`, and all five authored headings carry
the same discriminator. The repaired block matches that renderer output exactly,
which is what distinguishes a protocol repair from a hand edit. MD024 and MD025
are now zero across all 344 tracked Markdown files, and no transcript anywhere
carries a hand-written qualifier.

The specification exchange itself remains healthy after the repair: its status
reports one intact `abandoned-request` at round 1 awaiting the specification
reviewer, so the operation preserved the durable request instead of stranding
the exchange.

The three round-1 repairs are retained verbatim: the launcher assertions, the
repository-relative and retained-file operand wording, and the 97-line
measurement. The launcher assertion still bites. Replacing all thirteen
`bin/code_review_evidence.bat` references with a bare `git` fails
`test_reviewer_mode_uses_executable_baselines_and_manifest_lifecycle` and
`test_yes_and_no_paths_apply_the_same_executable_comparisons`; the instruction
was restored from the index afterwards and re-verified.

One round-1 observation closed as a side effect. The completion grep now matches
`code_review_evidence.bat` inside the test package it names, because the repair
introduced that constant, so the criterion no longer passes on the instruction
alone.

### Repairs made in step 3 code-reviewer round 2

None. The staged subject needed no reviewer repair in this round, so nothing
here forbids the recommendation below.

### Findings returned to the writer for step 3 code-reviewer round 2

The occurrence counter ignores the implementation step that the heading already
uses as its discriminator, so a code transcript spanning several steps now
claims exchanges it never had. This round's own request is headed
`## Round 2 by requestor - Step 3 (exchange 3)` at line 1869 of
`review.code.v0.11.0.code-reviewer.md`, with footer
`request-round-2-exchange-3`, because that transcript already holds
`request-round-2` footers from Step 1 at line 382 and Step 2 at line 879. Those
are different implementation steps of one document, not a restarted exchange,
and `## Round 2 by requestor - Step 3` was already unique through its `- Step 3`
segment. This answer will carry the same false claim for the same reason, since
`answer-round-2` footers exist at lines 467 and 1026.

The root cause is that the base entry identity is round-scoped only. Including
the implementation step in the base identity for code-family entries, as in
`request-step-3-round-2`, would make identities unique by construction and leave
the occurrence suffix for a genuinely restarted exchange. That changes the
durable identity format and therefore marker-repair matching, so it is a core
design decision rather than a reviewer repair.

This finding sits entirely in the unstaged review-exchange-core work and in the
protocol transcript, which is in neither `a.commit` group. It does not make the
Step 3 staged subject wrong and is recorded here because this exchange is where
it became observable.

### Validation evidence for step 3 code-reviewer round 2

Every command in the resolved set ran on an idle machine. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,767
tests, with the full phase at 1 minute 21.3 seconds and a slowest call of 0.43
seconds. The round-1 duration flapping is gone, which confirms the load
diagnosis recorded then: the same suite and bytes now report zero outliers where
four were reported under concurrent runs.

The plan completion grep returns 22 matches, now spanning both files it names.
`git diff --cached --check` exits cleanly. No resolver drift: the three commands
are the project default plus one plan addition plus one request addition, and the
current resolver produces the same set.

Line budgets hold at 195 lines for the canonical instruction and 97 for the
focused module. The validation record's 1,767-test figure and zero-outlier
result match this run; its 0.40-second slowest call differs from the 0.43 seconds
measured here because the slowest call varies per run, while every outcome field
agrees.

Markdown, checked against the repository `.markdownlint.json` with MD013 off and
MD033 limited to `img`: all four staged Markdown files and the code transcript
are clean, and the repository has no MD024 or MD025 finding left.

### a.commit assessment for step 3 code-reviewer round 2

Accurate, no amendment needed. `validate_commit_plan(parse_clipboard_content(
a.commit, interactive=False), staged_paths)` returns zero diagnostics against
the exact staged set: two ordered groups, conventional subjects, exact membership
over all six paths, and no duplicate or missing path. Both Why narratives cite
the umbrella draft, the code-reviewer topic draft, the feature request, the
design, the implementation plan, and the validation plan, as the change summary
claims. No commit was created.

### Non-blocking observations for step 3 code-reviewer round 2

The clause "rather than describing equivalent shell operations" is still
unasserted. This round's evidence proves the launcher is named in the setup and
both result sections; nothing yet proves that raw shell prose is absent, which
needs a negative assertion over the reviewer sections and a decision about how
strict it should be.

The completion grep's other two tokens still match only variable names.
`umbrella_digest` and `validation_state` appear as `umbrella_digest_before` and
`validation_state_after`, because the real CLI subcommands are hyphenated. The
criterion works now, but through the launcher token rather than through the two
it was written around.

The Yes and No sections still carry byte-identical three-command lists. The plan
requires both result paths to name the commands, so this is deliberate, and the
two copies can still drift apart without any test noticing.

Repository-wide Markdown still holds its earlier findings outside MD024 and
MD025, in roughly forty files unrelated to this step.

### Final reviewer decision for step 3 code-reviewer round 2

Decision: commit-ready. Step 3 is fully implemented against its plan step, every
round-1 finding is closed and independently verified, the reviewer made no
repair in this round, `a.commit` matches the staged set exactly, and all three
resolved validation commands pass with 100% coverage and zero outliers on an
idle machine.

The one finding above belongs to the unstaged review-exchange-core work and to a
transcript in neither commit group, so it does not bear on this commit; it does
need fixing before that core effort is itself reviewed.

This recommendation is advisory. It authorizes no commit, and the human gate
remains the sole authority for the `Commit` choice.

<!-- review-entry-id: answer-round-2-exchange-3 -->

## Round 2 by human - Step 3 - human-confirmation

- Recorded: 2026-08-17T16:42:15+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-08-17T19:39:41+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 code-reviewer round 1

request_index_tree: 556d0ac9e9561b654602d0c0e5e4489bc0d76da0
resolved_validation_set:

- ghog day (sources: project, plan)
- bin\code_review_answer.bat --help (sources: request)

### Requestor assessment for step 4 code-reviewer round 1

Assess Step 4, "Build paired code-review answers", against the exact staged index and the v0.11.0 code-reviewer requirement, design, implementation plan, and validation plan. Verify both answer variants, the paired rendering source, the live retained-manifest and assessed-index checks, ignored-root IO, atomic rollback, advisory authority boundary, and the exact `a.commit` membership and ordering. Treat any repair to staged substantive work as requiring another round.

### Implementation report for step 4 code-reviewer round 1

Yes. Step 4 has been fully implemented.

The staged implementation adds immutable `EarlyRejectionAssessment`, `ImplementationAssessment`, and `CodeReviewAnswerRender` models; a shared-envelope answer and substantive transcript renderer; an explicit-file CLI; the answer template; and the repository-root launcher. Assessment rendering verifies the exact live evidence manifest and assessed index without retiring it. Early rejection rejects assessment fields before rendering. Both paths publish a rollback-safe pair and retain advisory-only decision semantics.

The final `ghog day` passed 1,811 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`; the full phase took 2m 14.6s and the slowest call was 0.40s. The completion grep found both typed variants and paired outputs, `bin/code_review_answer.bat --help` exited 0 from the repository root, and every new production or test file remains below the 550-line safe threshold.

### Change summary for step 4 code-reviewer round 1

- Add the typed early-rejection and implementation-assessment answer models.
- Render complete answer content and substantive transcript summary from one immutable source.
- Validate explicit ignored-root inputs, the live retained manifest, and the live assessed index.
- Publish the two outputs atomically and restore prior presence and bytes after partial failure.
- Add the answer template, repository-root launcher, and separate model and CLI unit suites.
- Record the affirmative Step 4 implementation check and global validation evidence.

### Writer response for step 4 code-reviewer round 1

Writer response: This is the initial Step 4 review request, so there are no prior reviewer findings to answer. The staged implementation follows the tests-first plan and includes the completed implementation-check record plus the grouped commit plan requested for review.

### Reviewer focus for step 4 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-08-17T20:27:23+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 4
- Outcome: answer

### Assessed staged state for step 4 code-reviewer round 1

The request-time index tree `556d0ac9e9561b654602d0c0e5e4489bc0d76da0` matched
the live index exactly before assessment, so this round assessed the published
subject. After one reviewer repair the index tree is
`c37ec5a319dadc599e8139a09991617402d6096e`. The staged set holds exactly the
eight paths the plan names for this step.

Seven of the eight paths are new files. The validation plan is the only modified
path, and its seven deletions are the replaced `Not started` sentence and the
skeleton placeholders, so nothing is hidden inside an edited region.

The review-exchange-core work remains unstaged and outside both groups.

### Implementation assessment for step 4 code-reviewer round 1

Step 4 is implemented against the numbered plan, and the reviewer exercised the
deliverable rather than only reading it. Rendering one real early-rejection pair
through `tools/code_review_answer_cli.py` returned exit 0 and produced a
well-formed answer with a single `#` title, `## JSON` as its first section, the
four identity fields once each, and authored sections starting at H2, plus a
matching transcript summary whose sections start at H3.

The discriminated union is enforced where it belongs. `EarlyRejectionAssessment`
rejects any assessment field and any assessment flag before rendering, and
requires `changes-requested`. `ImplementationAssessment` requires every evidence
field, validates both tree identities, normalizes four inventories to unique
non-empty values, and pairs repairs with staged paths. `_validate_commit_ready`
is the authority boundary in code: a convergence recommendation is refused when
the readiness floor is incomplete, when a substantive repair happened, or when
unresolved findings or boundary-crossing work remain. The final decision text
states plainly that the recommendation authorizes no commit.

The CLI validates the variant shape before reading any file, resolves every
operand to an ignored root `a.*` path, rejects collisions among all inputs and
both outputs, reads each authored input once, and publishes the pair through a
same-directory temporary file with `os.replace`, restoring prior bytes or prior
absence when either replace fails.

The identity fields render repository-relative, which matches the current
portability policy introduced by `8726245`, where transcript metadata and
authored evidence drop the workstation prefix while durable request envelopes
keep exact identity. The reviewer checked this against
`validate_summary_identity` before accepting it: the published request passes
that absolute-path check and the rendered answer does not, and that difference is
the intended split rather than a defect, since the shared check applies to
requests only and this round's transcript metadata is relative throughout.

### Repairs made in step 4 code-reviewer round 1

Staged: `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The architecture
record stated that both production modules sit below the 550-line safe threshold
and the 650-line ceiling, which is true, but omitted the advisory-estimate
variance that item 8 of the plan's shared execution checklist requires. Both
modules exceed their advisory estimate of below 380 lines, by 93 and 12 lines.
The record now states that variance and that it fails no file at or below 650.

Polishing-only: this is a reviewed-step validation record, it changes no code,
test, acceptance behavior, or commit grouping, and it is the only repair in this
round.

### Findings returned to the writer for step 4 code-reviewer round 1

The published resolved validation set omits the step's own completion grep. The
plan's Step 4 completion criteria name three checks, and the request's immutable
evidence carries only two commands: `ghog day` with project and plan sources,
and the launcher help as a request addition. The missing command is
`rg -n 'EarlyRejection|ImplementationAssessment|answer_content|transcript_summary'
tools/code_review_answer.py tools/code_review_answer_cli.py`, which the
implementation report says was run and which returns 21 matches here. The
requestor instruction requires every exact plan-step addition to be passed
through a repeatable plan-validation flag, and each earlier round in this
exchange did carry its plan grep. The evidence therefore understates the
mandatory set for this step. The reviewer did not repair it, because the resolved
set lives inside the published immutable request.

Authored answer headings carry no exchange discriminator. `_section` builds every
heading as `{title} for step {step} {slug} round {round}`, which is unique across
rounds and steps inside one exchange but not across a restarted exchange over the
same step and round. The store already solves this for its own generated heading
by appending `(exchange N)`, and the code transcript proves restarts are real.
This renderer is what will author every reviewer sub-heading from now on, so the
duplicate-heading class that was declared non-negotiable can return through it.
Closing this needs the exchange occurrence to reach the renderer, which the
assessment models do not currently carry, so it is a design decision rather than
a reviewer repair.

### Validation evidence for step 4 code-reviewer round 1

Both commands in the resolved set ran after the repair, and so did the plan
command the set omits. `ghog day --force` reports `fail=0 warn=0 xfail=0 cov=100
outliers=0 excluded=0 exit=0` over 1,811 tests, with the full phase at 1 minute
50.2 seconds. `bin/code_review_answer.bat --help` exits 0 from the repository
root with no environment setup. The omitted plan grep returns 21 matches across
both production modules, so the criterion it encodes is satisfied even though the
published evidence does not name it.

Beyond the declared set, the reviewer rendered a real answer pair end to end, and
`git diff --cached --check` exits cleanly.

Line counts are 473, 392, 293, and 469 for the two production modules and the two
test modules, plus 9 template lines and a 20-line launcher. All are below the
550-line safe threshold, with the advisory variance now recorded.

Markdown, checked against the repository `.markdownlint.json` with MD013 off and
MD033 limited to `img`: the staged validation plan, the new template, and the
code transcript are clean.

### a.commit assessment for step 4 code-reviewer round 1

Accurate, no amendment needed. `validate_commit_plan(parse_clipboard_content(
a.commit, interactive=False), staged_paths)` returns zero diagnostics against the
exact staged set: two ordered groups, conventional subjects, exact membership
over all eight paths, and no duplicate or missing path. The implementation group
`feat(code-reviewer): render paired review answers` precedes the required
`docs(code-reviewer): record step 4 validation`, which is the least-dependent
ordering. The repair landed inside the existing Group 2 member. No commit was
created.

### Non-blocking observations for step 4 code-reviewer round 1

`_validated_inventory` filters `if isinstance(value, str)` inside its
normalization comprehension, but a non-string item has already raised on the line
above, so that guard can never exclude anything.

The same helper special-cases one label to build its message, choosing
`duplicate staged paths` when the label is `staged path inventory` and
`duplicate {label}` otherwise. A message that branches on a caller-supplied
string is easy to break from the call site; passing the message with the label
would remove the coupling.

The requestor assessment, implementation report, and change summary in this
request are unwrapped single-line paragraphs, where every earlier round wrapped
near 78 columns. MD013 is disabled, so nothing fails, but the transcript now
mixes both styles.

### Final reviewer decision for step 4 code-reviewer round 1

Decision: changes-requested. The published evidence omits one of the three
commands the plan sets as Step 4 completion criteria, and the authored-heading
discriminator needs a design decision that a reviewer cannot make inside this
step. Neither concerns the implementation, which is complete, exercised end to
end, and green on every check including the omitted one; the single repair in
this round is polishing-only. This answer is advisory and authorizes no commit.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 2 by requestor - Step 4

- Recorded: 2026-08-18T08:03:06+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 4
- Outcome: request

### Review identity for step 4 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 4
Review round: 2

### Code review evidence for step 4 code-reviewer round 2

request_index_tree: 39741f8c562b685f6d5ed92b1c8eafeeebb66eae
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'EarlyRejection|ImplementationAssessment|answer_content|transcript_summary' tools/code_review_answer.py tools/code_review_answer_cli.py (sources: plan)
- bin\code_review_answer.bat --help (sources: request)

### Requestor assessment for step 4 code-reviewer round 2

Reassess Step 4 after the round-1 changes against the exact staged index. Verify that the resolved validation set now includes all three completion commands, every rendered answer and transcript heading carries the positive exchange occurrence, the reviewer polishing repair remains intact, the durable round-1 transcript is staged, and `a.commit` exactly covers and orders all nine staged paths. Treat any new substantive repair as requiring another round.

### Implementation report for step 4 code-reviewer round 2

Yes. Step 4 remains fully implemented after the round-1 changes.

The omitted completion grep is now supplied as the exact plan-validation command, alongside the project `ghog day` command and the launcher smoke command. The answer model now requires a positive `exchange_occurrence`; the CLI requires `--exchange-occurrence`; and every authored answer and substantive transcript heading ends in `(exchange N)`. A restarted-exchange regression renders occurrence 2 and asserts that every authored heading in both paired outputs carries `round 2 (exchange 2)`.

The reviewer polishing repair remains in the validation plan. Its architecture record now measures 470 and 395 lines for the production modules and records their 90-line and 15-line advisory-estimate variances; the test modules measure 315 and 470 lines. The final `ghog day` passed 1,813 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`; the full phase took 2m 25.9s and the slowest call was 0.47s. The completion grep returns 22 matches and `bin/code_review_answer.bat --help` exits 0.

### Change summary for step 4 code-reviewer round 2

- Require a positive exchange occurrence in both answer variants and the CLI contract.
- Append `(exchange N)` to every authored answer and transcript heading.
- Add a restarted-exchange regression over both paired outputs.
- Retain the reviewer repair and update measured line counts and global test evidence.
- Add the exact Step 4 completion grep to the immutable resolved validation set.
- Stage the durable round-1 transcript and add it to the final documentation group in `a.commit`.

### Writer response for step 4 code-reviewer round 2

Writer response: Both round-1 findings are closed. The missing completion grep is now an explicit plan-validation input, so the replacement request publishes all three Step 4 completion commands in its immutable resolved set. The heading collision is closed by a required positive exchange occurrence propagated through the CLI and both immutable models; every authored heading now carries `(exchange N)`, with occurrence 2 covered across both outputs.

The reviewer polishing repair was retained and updated with the post-change measurements. The round-1 transcript is staged without hand edits, and `a.commit` now covers the exact nine-path staged set in the same two-group order.

### Reviewer focus for step 4 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-2 -->

## Round 2 by reviewer - Step 4

- Recorded: 2026-08-18T08:19:53+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 4
- Outcome: answer

### Assessed staged state for step 4 code-reviewer round 2

The request-time index tree `39741f8c562b685f6d5ed92b1c8eafeeebb66eae` matched
the live index exactly before assessment, and it is unchanged afterwards because
this round needed no repair. The staged set holds nine paths, one more than
round one, since the durable round-one transcript is now a member.

The staged subject carries no hidden edit. Eight paths are new files or pure
additions, the validation plan's seven deletions are its replaced skeleton
placeholders, and the transcript adds 211 lines with zero deletions. Because a
newly added transcript region can hide an edit that a deletion count cannot see,
the reviewer compared the appended round-one answer block byte for byte against
the summary published last round: they are identical.

The review-exchange-core work remains unstaged and outside both groups.

### Round 1 findings verified in step 4 code-reviewer round 2

Both findings are closed, each verified rather than accepted from the report.

The immutable resolved validation set now carries all three Step 4 completion
commands: `ghog day` from the project, the completion grep from the plan, and
the launcher smoke command from the request. That was the whole of the first
finding.

The heading discriminator is real and asserted. Every authored heading now ends
in `(exchange N)` through `_heading_label`, and removing that suffix from the
builder fails two tests, including the dedicated restarted-exchange regression
that asserts `round 2 (exchange 2)` across both paired outputs. Rendering a real
early-rejection pair with `--exchange-occurrence 2` confirms it end to end: the
answer carries four `(exchange 2)` headings at H2 and the summary three at H3.

The Step 3 finding was closed in the same movement, which this round's own
transcript demonstrates. Durable entry identities are now step-scoped, reading
`request-step-4-round-1`, `answer-step-4-round-1`, and `request-step-4-round-2`,
so they are unique by construction. The cross-step inflation reported then is
gone: these entries render with no exchange suffix at all, because their
occurrence is genuinely one.

The reviewer's round-one polishing repair was retained and correctly updated.
Its architecture record now measures 470, 395, 315, and 470 lines, and states
advisory-estimate variances of 90 and 15 lines. All four measurements and both
variances are exact.

### Repairs made in step 4 code-reviewer round 2

None. The staged subject needed no reviewer repair in this round, so nothing
here forbids the recommendation below.

### Findings returned to the writer for step 4 code-reviewer round 2

The renderer now requires an exchange occurrence that no exposed command can
supply. `--exchange-occurrence` is mandatory and the answer must be rendered
before `publish-answer` runs, but `entry_occurrence` lives only in
`review_exchange_store.py` and its two internal callers; neither
`bin/review_exchange.bat` nor `bin/code_review_evidence.bat` exposes it. A caller
who guesses wrong produces authored sub-headings claiming one exchange inside a
generated round heading claiming another, which is the ambiguity the
discriminator exists to remove.

The step-scoped identity fix makes this low risk today, since the correct value
is one until an exchange genuinely restarts for the same step and round, and
Step 4's plan explicitly defers workflow wiring to Step 5 in the same way it
defers manifest retirement. Recording it here so Step 5 closes it deliberately:
either expose the occurrence through the protocol command surface or state in the
canonical reviewer instruction how the value is obtained.

### Validation evidence for step 4 code-reviewer round 2

All three commands in the resolved set ran on an idle machine. `ghog day --force`
reports `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,813
tests, with the full phase at 1 minute 24.3 seconds. The completion grep matches,
and `bin/code_review_answer.bat --help` exits 0 from the repository root without
environment setup.

Beyond the declared set, the reviewer rendered a real paired answer end to end,
mutated the heading builder to confirm the new assertions bite, restored the file
from the index and re-verified it, and confirmed `git diff --cached --check`
exits cleanly.

Markdown, checked against the repository `.markdownlint.json` with MD013 off and
MD033 limited to `img`: the staged validation plan, the staged transcript, and
the answer template are clean, and the repository still reports no MD024 or MD025
finding anywhere.

### a.commit assessment for step 4 code-reviewer round 2

Accurate, no amendment needed. `validate_commit_plan(parse_clipboard_content(
a.commit, interactive=False), staged_paths)` returns zero diagnostics against the
exact staged set: two ordered groups, conventional subjects, exact membership
over all nine paths, and no duplicate or missing path. The implementation group
`feat(code-reviewer): render paired review answers` precedes the required
`docs(code-reviewer): record step 4 validation`, which now correctly carries both
the validation plan and the durable transcript.

### Non-blocking observations for step 4 code-reviewer round 2

The request reports the completion grep as returning 22 matches. Here the same
command reports 21 matching lines, and 24 individual matches with `rg -o`, so the
figure matches neither measure. Nothing in the staged subject depends on it, and
the criterion itself passes; the command form used for the count is worth
rechecking before it is quoted again.

The two observations from round one are unchanged and remain harmless: the dead
`isinstance` guard inside the normalization comprehension of
`_validated_inventory`, and its duplicate-message branch on a caller-supplied
label string.

### Final reviewer decision for step 4 code-reviewer round 2

Decision: commit-ready. Step 4 is fully implemented against its plan step, both
round-one findings are closed and independently verified, the round-one repair is
retained and its measurements are exact, the reviewer made no repair in this
round, `a.commit` matches the staged set exactly, and all three resolved
validation commands pass with 100% coverage and zero outliers.

The single finding above belongs to Step 5's wiring, which this plan defers by
design, and does not bear on this commit.

This recommendation is advisory. It authorizes no commit, and the human gate
remains the sole authority for the `Commit` choice.

<!-- review-entry-id: answer-step-4-round-2 -->

## Round 2 by human - Step 4 - human-confirmation

- Recorded: 2026-08-18T08:30:15+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 5

- Recorded: 2026-08-18T09:43:29+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 code-reviewer round 1

request_index_tree: b8b7ff9c799af75c4493ef028db10d061c2f81b1
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'code-reviewer|REQUEST_PENDING|CODE_REVIEWER' tools/prompt_workflow_code_review.py tools/prompt_workflow_skill.py instructions/code-reviewer.md (sources: plan)
- rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat' instructions/code-reviewer.md (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 5 code-reviewer round 1

Step 5 is fully implemented. Exact pending code requests resolve to the typed
`CodeReviewActor.REVIEWER`; every other classified state resolves to
`CodeReviewActor.REQUESTOR`, and `CodeReviewRoute` rejects an actor/state
disagreement at construction. Ordinary and forced Codex and Claude routes name
the exact implementation plan and Step 5, while a cold abandoned request stops
with the exact requestor reclaim handoff.

The canonical reviewer instruction registers the fixed code-family policy,
reads only the exact returned request path, performs one bounded wait, and
delegates evidence, paired answer rendering, and exchange operations to their
three launchers. Direct-link adapter tests prove that provider files copy no
policy. The Step 4 returned occurrence finding is also closed: pending status
reports `exchange_occurrence`, and answer publication uses the current request
occurrence for its generated heading and durable entry identity.

Validation is green. `ghog day` ran 1,846 tests with `fail=0`, `warn=0`,
`xfail=0`, `cov=100`, `outliers=0`, and `exit=0`; the full phase took 1m 22.7s
and its slowest call was 0.27s. Ty, pyright, ruff, radon, vulture, file-size,
ShellCheck, and EOF checks passed. Both Step 5 completion greps passed, as did
`git diff --check`. All touched Python files remain below the 650-line ceiling;
`tools/prompt_workflow_skill.py` is 646 lines and its review-role dispatcher
passes the complexity gate.

### Implementation report for step 5 code-reviewer round 1

Implemented the Step 5 independent reviewer route, canonical instruction, and
host adapters tests-first. The code route now owns one immutable typed actor,
the skill dispatcher selects the reviewer only for an exact `request-pending`
exchange, and forced routing follows the same partition without activating or
recovering work.

Added launcher-only reviewer sequencing for identity checks, early rejection,
baseline and repair attribution, reviewer-mode implementation checking,
validation-state comparison, paired rendering, publication, and retained
evidence recovery. Added the protocol occurrence status field and shared
step-scoped transcript identity helper so the answer renderer never guesses a
restarted-exchange discriminator.

### Change summary for step 5 code-reviewer round 1

The staged review subject contains 18 paths in three ordered `a.commit` groups.

Group 1, `fix(review-exchange): expose request occurrence`:

- `tools/review_exchange_cli.py`
- `tools/review_exchange_publication.py`
- `tools/review_exchange_transcript_identity.py`
- `tests/unit/tools/test_review_exchange_cli/test_review_exchange_cli_tdd.py`
- `tests/unit/tools/test_review_exchange_lifecycle/test_review_exchange_transcript_identity_tdd.py`

Group 2, `feat(code-reviewer): route independent reviews`:

- `.agent/workflows/code-reviewer.md`
- `.agents/llm-shared/instructions/code-reviewer.md`
- `.agents/llm-shared/skills/code-reviewer/SKILL.md`
- `.claude/skills/code-reviewer/SKILL.md`
- `instructions/code-reviewer.md`
- `tools/prompt_workflow_code_review.py`
- `tools/prompt_workflow_skill.py`
- `tests/unit/tools/test_code_reviewer_instruction/__init__.py`
- `tests/unit/tools/test_code_reviewer_instruction/test_code_reviewer_instruction_tdd.py`
- `tests/unit/tools/test_instruction_structure/test_code_reviewer_adapters_tdd.py`
- `tests/unit/tools/test_prompt_workflow_code_review/test_prompt_workflow_code_review_tdd.py`
- `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py`

Group 3, `docs(code-reviewer): record step 5 completion`:

- `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`

Each Why section has two narrative paragraphs that cite the review-mode
umbrella draft, code-reviewer topic draft, feature request, design,
implementation plan, and validation plan. The unrelated unstaged
`commit-plan-check` and `markdown-check` drafts and their review-mode umbrella
edit are pre-existing concurrent work and are not part of this staged subject.

### Writer response for step 5 code-reviewer round 1

Writer response: This is Step 5 round 1, so there is no earlier Step 5 reviewer feedback or
disagreement. The non-blocking Step 4 finding about caller-supplied exchange
occurrence was accepted and closed in the first commit group: status now
exposes the current request occurrence, publication uses the same value, and a
restarted request-without-answer regression pins the boundary.

### Reviewer focus for step 5 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-08-18T10:07:51+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 code-reviewer round 1 (exchange 1)

Baseline index tree: b8b7ff9c799af75c4493ef028db10d061c2f81b1

Assessed index tree: 53bcee735036b77c8d85197fe215584a499d6d63

### Implementation check for step 5 code-reviewer round 1 (exchange 1)

Result: Yes. Step 5 is implemented against the numbered plan, and the reviewer verified
it by executing the deliverable rather than only reading it.

This assessment was produced through the Step 5 artifacts themselves. The
`code-reviewer` skill resolved to the canonical `instructions/code-reviewer.md`,
and that instruction's ordered sequence drove every action taken here: `status`
then one bounded `wait-request`, reading only the returned `paths.request`,
baseline capture and request-tree comparison, umbrella and validation-state
capture, a pre-repair blob before the single edit, patch attribution before
staging, manifest write, and paired rendering through
`bin/code_review_answer.bat`. Every operation used the named launcher; no
equivalent Git or filesystem command was substituted.

`CodeReviewActor` resolves one owner from the classified state, and
`CodeReviewRoute.__post_init__` rejects any actor that disagrees with it, which
is design decision Q04 implemented exactly. `command_for_route` consumes the
resolved actor through a single ternary and repeats no state partition.
`_forced_code_reviewer_command` refuses a cold `abandoned-request` with a
diagnostic naming the requestor reclaim handoff, and forced
`code-review-requestor` returns None when the route belongs to the reviewer, so
both forced roles carry the ownership check. The dispatcher change consolidates
three inline branches into one `FORCED_REVIEW_ROLES` membership test plus an
extracted helper, which reduces rather than grows the family branch cluster the
split guidance warns about.

All four host adapters are metadata-plus-redirect files pointing at the canonical
instruction, copying no policy.

The Step 4 follow-up finding is closed: `status` now reports
`exchange_occurrence`, which this round consumed as the value passed to
`--exchange-occurrence`.

Validation plan effects: None. The reviewer wrote no validation-plan row this round.

The staged Step 5 record was already complete and accurate on every claim the
reviewer re-measured: `tools/prompt_workflow_code_review.py` at 277 lines,
`tools/prompt_workflow_skill.py` at 646, the canonical instruction at 188, and
the new instruction, skill-route, adapter, and transcript-identity modules at
102, 180, 65, and 46 lines. The record also states the dispatcher variance
against the hard ceiling rather than leaving it silent, which closes the omission
raised in the Step 4 round-one answer.

Two figures in that record are imprecise and are reported as observations rather
than corrected, because neither changes a verdict and the record is otherwise
exact.

### Pre-repair mandatory checks and coverage for step 5 code-reviewer round 1 (exchange 1)

Pre-repair, one mandatory command failed.

`git diff --cached --check` returned `instructions/code-reviewer.md:188: new
blank line at EOF.` and exit 2. That command is in this round's resolved
validation set as a request-sourced addition, so its failure is missing
mandatory evidence, not a cosmetic note. An independent Markdown check over the
repository `.markdownlint.json` rules reported the same defect as MD047.

The other three commands passed before the repair. `ghog day --force` reported
`fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` across 1,846 tests
with the full phase at 1 minute 30.8 seconds. The routing completion grep
returned 10 matching lines across all three named files. The launcher-boundary
grep returned 15 matching lines in the canonical instruction.

Post-repair, every command passes. `git diff --cached --check` exits 0, the
Markdown check reports no finding, and a second `ghog day --force` reported the
same green result across 1,846 tests with the full phase at 1 minute 44.2
seconds.

### Resolved validation set and sources for step 5 code-reviewer round 1 (exchange 1)

Four commands, matching the request's immutable resolved set exactly.

- `ghog day` (sources: project)
- `rg -n 'code-reviewer|REQUEST_PENDING|CODE_REVIEWER' tools/prompt_workflow_code_review.py tools/prompt_workflow_skill.py instructions/code-reviewer.md` (sources: plan)
- `rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat' instructions/code-reviewer.md` (sources: plan)
- `git diff --cached --check` (sources: request)

Both plan-sourced commands are the exact Step 5 completion criteria, so the
published evidence names the mandatory set in full. The fourth criterion,
covering ordinary and forced host rendering, is proven by the staged routing
tests rather than by a command in this set.

### Resolver drift and direction for step 5 code-reviewer round 1 (exchange 1)

None in either direction.

The request's embedded set is the project default plus the two exact Step 5 plan
additions plus one request addition. The current resolver produces the same four
commands with the same sources, so the union the reviewer ran equals the
published set. No command was added, dropped, or relabelled.

### Repository state around validation for step 5 code-reviewer round 1 (exchange 1)

The request-time index tree `b8b7ff9c799af75c4493ef028db10d061c2f81b1` matched
the live index exactly before assessment, so this round assessed the published
subject. After the single reviewer repair the assessed index tree is
`53bcee735036b77c8d85197fe215584a499d6d63`.

The umbrella digest is unchanged across the implementation-check result:
`b08a43e7df11315ba094e2e76b5355c21160a46e71eee22b8b0acb6bd0551c03` before and
after, applicable true. No umbrella row was completed or touched from reviewer
mode.

The ordered validation-state scope covered all eighteen staged step paths. The
comparison reports `acceptable: false` with tracked differences at
`instructions/code-reviewer.md` and `<index>`, and no ignored or untracked
difference. Both are this reviewer's own attributable repair and its staging,
proven by `attribute-reviewer-patch` returning `attributable: true` for the
recorded pre-repair blob, not a validation side effect. No validation command
wrote to a tracked file.

Disclosed for completeness: `docs/v0.11.0/draft.v0.11.0.review-mode.md` and two
new draft files carry pre-existing unstaged changes from earlier umbrella work in
this session. They are outside the Step 5 subject, appear in no `a.commit` group,
and were captured in the umbrella baseline before assessment began, so the digest
comparison above is unaffected by them.

### Repair inventory for step 5 code-reviewer round 1 (exchange 1)

Repairs made:

- Removed the trailing blank line at the end of `instructions/code-reviewer.md`, which failed the mandatory `git diff --cached --check` command and MD047. Substantive: it changes a tracked production file that is not `a.commit`, ignored caller evidence, a protocol artifact, or a reviewed-step validation row.

Paths staged:

- instructions/code-reviewer.md

### Commit plan assessment for step 5 code-reviewer round 1 (exchange 1)

Accurate, no amendment needed.

`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)` returns zero diagnostics against the exact staged set both before
and after the repair: three ordered groups, conventional subjects, exact
membership over all eighteen paths, and no duplicate or missing path.

The grouping is well chosen. Group 1, `fix(review-exchange): expose request
occurrence`, isolates the five review-exchange-core paths that close the Step 4
follow-up, so core work does not ride inside the code-reviewer feature commit.
Group 2, `feat(code-reviewer): route independent reviews`, carries the routing
change, canonical instruction, four adapters, and their tests. Group 3,
`docs(code-reviewer): record step 5 completion`, carries the validation record
last. That is least-dependent-first ordering.

The repair landed inside an existing Group 2 member, so membership, grouping, and
order are unchanged. No commit was created.

### Findings and boundaries for step 5 code-reviewer round 1 (exchange 1)

Unresolved findings:

- A mandatory validation command failed and was reported as passing. `git diff --cached --check` is in this round's resolved set as a request addition, and it returned `instructions/code-reviewer.md:188: new blank line at EOF.` with exit 2 against the published index tree. The validation record states that `git diff --check` returned no diagnostics. Those are different commands: the recorded one compares the working tree against the index and is empty when everything is staged, while the resolved one compares the index against HEAD. Running the working-tree variant turned a failing mandatory check into a reported pass. The defect itself is repaired; the substitution is the finding, because the same substitution would hide any future staged-whitespace failure.
- The launcher-boundary grep is recorded as returning 14 matches. The exact command in the resolved set returns 15, whether counted as matching lines or as individual matches. Nothing depends on the figure and the criterion passes, but it is quoted as evidence.
- The dispatcher line-budget variance is described against the wrong plan number. The record says 646 is "63 lines above its advisory 583-line baseline"; 583 is the before-count and 600 is the advisory estimate, so the variance against the estimate is 46. The ceiling statement is correct and the file is 4 lines under 650, which is worth watching before Step 6 adds anything to it.

Boundary-crossing work: None.

### Writer instructions for step 5 code-reviewer round 1 (exchange 1)

Accept or reverse the staged repair to `instructions/code-reviewer.md`, and
record the reversal as explicit disagreement if you reverse it.

Re-run `git diff --cached --check`, the exact command named in the resolved
validation set, and correct the validation record that currently reports
`git diff --check`. State the result of the staged variant, since that is the
one this step's evidence is built on.

Correct the two quoted figures in the Step 5 record: the launcher-boundary grep
returns 15 matches, not 14, and the dispatcher is 46 lines above its advisory
estimate of below 600 rather than 63 above the 583-line baseline. Keeping both
numbers exact matters because the record is the durable evidence a later reader
trusts.

Before Step 6 adds anything to `tools/prompt_workflow_skill.py`, note that it now
sits 4 lines below the 650-line ceiling. The plan's split guidance names the
remedy if it would cross: move forced code-review role selection into
`tools/prompt_workflow_code_review.py`, which is at 277 lines.

No other change is requested. Everything else in this step is correct.

### Decision rationale for step 5 code-reviewer round 1 (exchange 1)

Changes-requested, for two independent reasons.

This round made a substantive repair. Removing the trailing blank line changed a
tracked production file outside the exempt categories, and the instruction under
review states that any such reviewer-authored change forces `changes-requested`
in the same round. The answer model enforces the same rule, so a commit-ready
recommendation here would be rejected before rendering.

A mandatory validation command also failed against the published index tree and
was recorded as passing because a different command was run. That is missing
mandatory evidence rather than a cosmetic note, and the substitution needs the
writer's attention independently of the one-line fix.

The implementation itself is complete and correct. Step 5 was assessed by
executing its own deliverable: the `code-reviewer` skill routed to the canonical
instruction, and that instruction's ordered sequence drove this entire
assessment through the named launchers, including the `exchange_occurrence` that
Step 4's follow-up finding asked for. Typed actor resolution, the construction
consistency check, forced-role ownership, the cold abandoned-request handoff, and
the four thin adapters all behave as the plan specifies, and `a.commit` groups
the work correctly in three ordered commits.

### Final reviewer decision for step 5 code-reviewer round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-08-18T10:38:59+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 code-reviewer round 2

request_index_tree: ea9b2cadbfe24cbeb7d1be097697850101097e37
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'code-reviewer|REQUEST_PENDING|CODE_REVIEWER' .agent .agents .claude instructions tools tests docs/v0.11.0/plan.v0.11.0.code-reviewer.md docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md (sources: plan)
- rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat' instructions/code-reviewer.md (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 5 code-reviewer round 2

## Assessment

Step 5 is ready for round 2 review. The implementation keeps the code-reviewer route independent from the writer-owned review routes, resolves the actor once, enforces the construction-time role and ownership consistency checks, and delegates the complete reviewer sequence to the named launchers.

All round 1 requested changes are closed. The reviewer repair removing the blank line at the end of `instructions/code-reviewer.md` is retained. The validation record now names the mandatory staged-tree check exactly as `git diff --cached --check`, records its successful post-repair result, corrects the launcher grep to 15 matching lines, and describes `tools/prompt_workflow_skill.py` as 646 lines: 46 above the 600-line advisory estimate and 4 below the 650-line hard ceiling.

The durable round 1 transcript is included in the documentation commit group. The staged subject contains 19 paths in three ordered groups, and the commit plan validates without diagnostics.

### Implementation report for step 5 code-reviewer round 2

## Implementation report

The Step 5 implementation is complete across the four metadata adapters, the canonical reviewer instruction, prompt-workflow actor routing, exchange occurrence exposure, and focused regression tests. `status` exposes `exchange_occurrence`, allowing the reviewer instruction to supply the store-computed value before answer publication.

Round 1 found one staged-whitespace defect and three inaccurate validation statements. The whitespace defect was repaired in the canonical instruction, and the validation plan now records the exact successful commands and measured figures. No implementation behavior was weakened or bypassed.

The forced full gate completed with 1,846 tests, `fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`, and `exit=0` in 1m 45.8s; the slowest test took 0.28s.

### Change summary for step 5 code-reviewer round 2

## Change summary

The staged subject contains 19 paths in three ordered commit groups:

1. `fix(review-exchange): expose request occurrence` centralizes and exposes the store-side occurrence needed by authored review headings, with CLI and transcript-identity regressions.
2. `feat(code-reviewer): route independent code reviews` adds the code-reviewer adapters, canonical reviewer sequence, actor-based workflow routing, and focused instruction and routing tests.
3. `docs(code-reviewer): record step 5 completion` records the corrected Step 5 validation evidence and retains the durable Step 5 round 1 transcript.

The round 1 repair is a one-line EOF cleanup in `instructions/code-reviewer.md`. The validation record additionally corrects the mandatory command name, launcher match count, line-budget comparison, instruction line count, and current full-suite timing.

Unrelated working-tree drafts remain excluded from the staged review subject.

### Writer response for step 5 code-reviewer round 2

Writer response: ## Writer response to round 1

Accepted all round 1 feedback without disagreement.

The reviewer-authored EOF repair is retained. I reran the mandatory `git diff --cached --check` against the repaired staged tree and it returned no diagnostics. I corrected the validation plan so it no longer substitutes `git diff --check`, and so it records 15 launcher-grep matches, the 646-line dispatcher as 46 above the 600-line advisory estimate and 4 below the hard ceiling, and the canonical instruction as 187 lines after the repair.

I reran the forced full gate after those changes: 1,846 tests completed in 1m 45.8s with 100% coverage, zero failures, zero warnings, zero xfails, and zero duration outliers; the slowest test took 0.28s. I also added the pure round 1 transcript to the documentation commit group and revalidated the resulting 19-path, three-group commit plan.

### Reviewer focus for step 5 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-08-18T10:51:27+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 code-reviewer round 2 (exchange 1)

Baseline index tree: ea9b2cadbfe24cbeb7d1be097697850101097e37

Assessed index tree: ea9b2cadbfe24cbeb7d1be097697850101097e37

### Implementation check for step 5 code-reviewer round 2 (exchange 1)

Result: Yes. Step 5 remains fully implemented, and every round-one finding is closed.

Each closure was re-measured rather than accepted from the report. `git diff
--cached --check`, the exact command named in the resolved set, now exits 0
against the published index tree, and the validation record names that staged
variant instead of the working-tree one it quoted before. The launcher-boundary
grep returns 15 matching lines and the record now says 15. The dispatcher
variance is stated against the right plan number: 646 lines is 46 above the
600-line advisory estimate and 4 below the hard ceiling.

The round-one repair is retained. `instructions/code-reviewer.md` ends with a
single newline, measures 187 lines, and the record reflects that count.

The implementation itself is unchanged and still correct: one typed
`CodeReviewActor` resolved from the classified state, a construction-time
consistency check on `CodeReviewRoute`, forced-role ownership checks in both
directions, the diagnostic cold abandoned-request handoff, and four
metadata-plus-redirect adapters.

The staged transcript is a pure append of 343 lines with zero deletions, and it
does not contain the heading defect reported below; the staged content ends
before the round-two request entry.

Validation plan effects: None. The reviewer wrote no validation-plan row this round; the staged Step 5 record is accurate on every figure re-measured.

### Pre-repair mandatory checks and coverage for step 5 code-reviewer round 2 (exchange 1)

Pre-repair and post-assessment are identical because this round required no repair. All four resolved commands pass: ghog day --force reported fail=0 warn=0 xfail=0 cov=100 outliers=0 exit=0 across 1,846 tests in 1m 18.9s on an idle machine; the routing grep returned 10 matching lines; the launcher-boundary grep returned 15; and git diff --cached --check exited 0.

### Resolved validation set and sources for step 5 code-reviewer round 2 (exchange 1)

Four commands, matching the request set exactly: ghog day (project), the routing grep (plan), the launcher-boundary grep (plan), and git diff --cached --check (request).

### Resolver drift and direction for step 5 code-reviewer round 2 (exchange 1)

None in either direction. The current resolver produces the same four commands with the same sources as the published set.

### Repository state around validation for step 5 code-reviewer round 2 (exchange 1)

The request-time index tree `ea9b2cadbfe24cbeb7d1be097697850101097e37` matched
the live index exactly before assessment, and it is unchanged afterwards because
this round required no repair.

The umbrella digest is unchanged across the implementation-check result:
`b08a43e7df11315ba094e2e76b5355c21160a46e71eee22b8b0acb6bd0551c03` before and
after, applicable true. No umbrella row was completed or touched.

The ordered validation-state scope covered all nineteen staged step paths. The
comparison reports `acceptable: true` with no tracked, ignored, or untracked
difference, so no validation command wrote anywhere in the reviewed scope.

The staged transcript was checked for a hidden edit rather than trusted: its
staged diff is 343 insertions with zero deletions, and because a newly added
region can hide an edit that a deletion count cannot see, its staged blob was
compared against the working tree. The staged content ends at line 2913, before
the round-two request entry, which is where the reported heading defect lives.

Disclosed for completeness: `docs/v0.11.0/draft.v0.11.0.review-mode.md` and two
new draft files carry pre-existing unstaged changes from earlier umbrella work.
They are outside the Step 5 subject, appear in no `a.commit` group, and were
captured in the umbrella baseline before assessment, so the digest comparison is
unaffected.

### Repair inventory for step 5 code-reviewer round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 code-reviewer round 2 (exchange 1)

Accurate, no amendment needed.

`validate_commit_plan(parse_clipboard_content(a.commit, interactive=False),
staged_paths)` returns zero diagnostics against the exact staged set: three
ordered groups, conventional subjects, exact membership over all nineteen paths,
and no duplicate or missing path.

The grouping still separates concerns correctly. Group 1,
`fix(review-exchange): expose request occurrence`, isolates the five
review-exchange-core paths. Group 2, `feat(code-reviewer): route independent
reviews`, carries the routing change, canonical instruction, four adapters, and
their tests. Group 3, `docs(code-reviewer): record step 5 completion`, carries
the validation record and the protocol transcript last.

The nineteenth path is the transcript, newly added to the documentation group so
the Step 5 review record lands with the step. That is the right membership, and
it is the reason the heading finding above must be fixed before the round-two
and round-three appends are staged.

### Findings and boundaries for step 5 code-reviewer round 2 (exchange 1)

Unresolved findings:

- Three authored request sections now nest a bare, unqualified `##` heading inside the section heading the renderer already generates. In the published round-two request, `## Assessment` sits at line 79 under `## Requestor assessment for step 5 code-reviewer round 2`, `## Implementation report` at line 89 under its generated parent, and `## Change summary` at line 99 under its own. The cause is the authored input files: `a.code-review-step5-round2.assessment.md`, `.implementation.md`, and `.changes.md` each now begin with their own heading, while the round-one files began with prose. The transcript append carries the same defect, with a bare `## Implementation report` at line 2953 inside content the store has already titled at `###`, which breaks the round's outline by placing an H2 beneath an H3. Because the three headings carry no step, round, or exchange discriminator, round three authoring the same three inputs produces exact MD024 duplicates in the transcript; this is not latent but fires on the next round. The staged subject is clean today, since the staged transcript ends at line 2913 and contains none of them, so the defect enters the repository only when the round-two and round-three appends are staged. The fix is in the authored inputs, not in any protocol artifact: drop the leading heading from each file and let the renderer supply the qualified title it already writes. A reviewer must not repair this, because both the request and the transcript are published protocol artifacts.

Boundary-crossing work: None.

### Writer instructions for step 5 code-reviewer round 2 (exchange 1)

Remove the leading `##` heading from each of the three authored input files
before rendering round three: `a.code-review-step5-round2.assessment.md`,
`a.code-review-step5-round2.implementation.md`, and
`a.code-review-step5-round2.changes.md`. Start each file with its prose, exactly
as the round-one inputs did. The request renderer already writes the qualified
section heading, so the file must not write one too.

Do not edit the published round-two request or the transcript to correct what is
already appended. Those are protocol artifacts, and hand-editing them is the
defect this exchange has already recorded once.

When round three is prepared, confirm that the transcript append contains no
bare `##` heading and that its authored sections start at `###`, before staging
the transcript into the documentation group.

Everything else in Step 5 is accepted. All three round-one findings are closed,
the reviewer repair is retained, and no other change is requested.

### Decision rationale for step 5 code-reviewer round 2 (exchange 1)

Changes-requested, on one unresolved finding rather than on the implementation.

The readiness floor this instruction defines requires the absence of unresolved
current findings. The nested bare headings are a current finding, they violate
the heading rules that `instructions/review-requestor.md` and
`instructions/implementation-check.md` both declare non-disableable, and they
will produce exact duplicate headings in the transcript on the next round. So
commit-ready is unavailable, and the answer model enforces the same rule.

Nothing else stands in the way. The reviewer made no repair this round, all three
round-one findings are closed and independently re-measured, the umbrella digest
is unchanged, the validation-state comparison is clean with no tracked or
untracked difference, and `a.commit` validates with zero diagnostics over
nineteen paths in three correctly ordered groups.

One gate note. The first walk reported a single duration outlier at 0.52 seconds
in a Step 4 test that is not part of this staged subject. Re-running on an idle
machine reported zero outliers in 1 minute 18.9 seconds, which matches the
writer's own result, so that reading was load and not a regression.

### Final reviewer decision for step 5 code-reviewer round 2 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 3 by requestor - Step 5

- Recorded: 2026-08-18T11:04:36+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: request

### Review identity for step 5 code-reviewer round 3

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 5
Review round: 3

### Code review evidence for step 5 code-reviewer round 3

request_index_tree: 88ef97781f340d16209936532824e6cde70bc57a
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'code-reviewer|REQUEST_PENDING|CODE_REVIEWER' .agent .agents .claude instructions tools tests docs/v0.11.0/plan.v0.11.0.code-reviewer.md docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md (sources: plan)
- rg -n 'code_review_evidence.bat|code_review_answer.bat|review_exchange.bat' instructions/code-reviewer.md (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 5 code-reviewer round 3

Step 5 remains fully implemented. The independent code-reviewer route, actor consistency checks, ownership enforcement, launcher delegation, occurrence exposure, and focused regressions are unchanged from the round-2 subject.

The sole round-2 finding is closed in the caller-owned authoring inputs. The three round-2 assessment, implementation-report, and change-summary files now begin directly with prose, and the corresponding round-3 inputs follow the same shape. The renderer therefore owns the qualified section titles. No published request or transcript byte was hand-edited.

The durable round-2 request and answer are staged in the existing documentation group before this round's index capture. The historical round-2 headings remain protocol-owned evidence; the round-3 append introduces no bare authored heading and cannot create the predicted duplicate.

Validation is green on that staged subject: `ghog day --force` completed all 1,846 tests in 1m 37.0s with `fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`, and `exit=0`; the slowest test took 0.32s. `git diff --cached --check` is clean and `a.commit` parses without diagnostics. Architecture and feature integrity remain unchanged because the authoring correction touches no staged implementation byte, and performance remains below both the per-test 0.5s ceiling and the three-minute suite objective.

### Implementation report for step 5 code-reviewer round 3

No Step 5 implementation code changed in response to round 2. The requested correction applies to ignored caller-owned renderer inputs: their redundant leading headings were removed, while published protocol artifacts were preserved unchanged.

The staged subject still contains the same 19 paths and three commit groups. Its transcript path now retains the complete round-2 exchange through the reviewer answer, so round 3 assesses the durable history that would ship with Step 5.

### Change summary for step 5 code-reviewer round 3

The staged subject contains 19 paths in three ordered groups: the five-path review-exchange occurrence repair, the twelve-path independent code-reviewer implementation and tests, and the two-path documentation record containing the validation plan plus durable transcript.

Since round 2, the only staged-byte change is the protocol-generated transcript append for the round-2 request and answer. The requested authoring fix is confined to ignored `a.*` inputs, so `a.commit` membership, ordering, subjects, and its two-paragraph narrative Why sections remain accurate without amendment. Unrelated umbrella draft work remains unstaged and outside this review subject.

### Writer response for step 5 code-reviewer round 3

Writer response: Accepted the round-2 finding without disagreement.

I removed the leading `##` heading from `a.code-review-step5-round2.assessment.md`, `a.code-review-step5-round2.implementation.md`, and `a.code-review-step5-round2.changes.md`. Each now starts directly with prose, matching the renderer contract and the round-1 input shape. The new round-3 assessment, implementation-report, and change-summary inputs also start with prose.

I did not edit the published round-2 request or the versioned transcript. I staged the protocol-generated round-2 transcript append as-is in the documentation group before rendering round 3. The replacement round should therefore add only renderer-qualified authored section headings and no bare `## Assessment`, `## Implementation report`, or `## Change summary` heading.

### Reviewer focus for step 5 code-reviewer round 3

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-3 -->

## Round 3 by reviewer - Step 5

- Recorded: 2026-08-18T11:12:47+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 code-reviewer round 3 (exchange 1)

Baseline index tree: 88ef97781f340d16209936532824e6cde70bc57a

Assessed index tree: 88ef97781f340d16209936532824e6cde70bc57a

### Implementation check for step 5 code-reviewer round 3 (exchange 1)

Result: Yes. Step 5 is fully implemented, and the round-two finding is closed at its
source without touching a published artifact.

The three authored inputs now begin with prose, so the round-three request
carries nine section headings and every one of them is qualified with step and
round. No bare heading appears anywhere in it.

The writer correctly refused the wrong remedy. The round-two bytes still hold
`## Assessment`, `## Implementation report`, and `## Change summary` at
transcript lines 2943, 2953, and 2963. Rewriting them would have been a hand
edit of an append-only protocol artifact, which this exchange has already
recorded once as a defect, so leaving them and fixing the inputs is the right
call.

The reviewer owes a correction here. The round-two finding described those
headings as breaking the outline by placing an H2 beneath an H3. That part was
wrong: `instructions/review-requestor.md` permits a round's own headings at
`##` or deeper and forbids only `#`. The half that was right, and the half that
mattered, is the uniqueness rule, which names a bare `## Evidence` as a defect
in the round that writes it because it duplicates the moment the next round
repeats the word. That is exactly what the input change prevents.

The implementation is unchanged from round one and still correct: one typed
`CodeReviewActor` resolved from the classified state, a construction-time
consistency check on `CodeReviewRoute`, ownership checks on both forced roles,
the diagnostic cold abandoned-request handoff, and four metadata-plus-redirect
adapters. The round-one reviewer repair remains in place, and the validation
record still matches every figure re-measured in round two.

Validation plan effects: None. The reviewer wrote no validation-plan row this round; the staged Step 5 record remains accurate on every figure re-measured in round two.

### Pre-repair mandatory checks and coverage for step 5 code-reviewer round 3 (exchange 1)

All four resolved commands pass, and no repair was needed so the pre-repair and post-assessment readings are the same. ghog day --force reported fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0 across 1,846 tests in 1m 29.7s. The routing grep returned 10 matching lines across its three files, the launcher-boundary grep returned 15 in the canonical instruction, and git diff --cached --check exited 0.

### Resolved validation set and sources for step 5 code-reviewer round 3 (exchange 1)

Four commands, matching the request set exactly: ghog day (project), the routing grep (plan), the launcher-boundary grep (plan), and git diff --cached --check (request). Both plan entries are the exact Step 5 completion criteria.

### Resolver drift and direction for step 5 code-reviewer round 3 (exchange 1)

None in either direction. The current resolver produces the same four commands with the same sources as the published set.

### Repository state around validation for step 5 code-reviewer round 3 (exchange 1)

The request-time index tree `88ef97781f340d16209936532824e6cde70bc57a` matched
the live index exactly before assessment, and it is unchanged afterwards because
this round required no repair.

The umbrella digest is unchanged across the implementation-check result:
`b08a43e7df11315ba094e2e76b5355c21160a46e71eee22b8b0acb6bd0551c03` before and
after, applicable true.

The ordered validation-state scope covered all nineteen staged step paths, and
the comparison reports `acceptable: true` with no tracked, ignored, or untracked
difference.

The staged transcript was checked for a hidden edit rather than trusted. Its
staged diff carries zero deletions, and because a newly added region can hide an
edit that a deletion count cannot see, the staged blob was inspected directly:
the round-two bare headings survive at their original lines, and the round-two
reviewer answer is present verbatim, including its distinctive closing sentences.
Nothing in the appended history was rewritten.

One consequence is worth stating plainly. Staging now reaches through the
round-two answer, so those three historical bare headings are inside the staged
content and will enter the repository with this commit. That is the correct
outcome of the instruction they were given: append-only integrity outranks
cosmetic purity, the headings are unique as written, and the input fix means they
cannot recur.

Disclosed for completeness: `docs/v0.11.0/draft.v0.11.0.review-mode.md` and two
new draft files carry pre-existing unstaged changes from earlier umbrella work.
They are outside the Step 5 subject, appear in no `a.commit` group, and were
captured in the umbrella baseline before assessment.

### Repair inventory for step 5 code-reviewer round 3 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 code-reviewer round 3 (exchange 1)

Accurate, no amendment needed. validate_commit_plan over the parsed a.commit and the exact staged set returns zero diagnostics: three ordered groups, conventional subjects, exact membership over all nineteen paths, no duplicate or missing path. Group 1 isolates the five review-exchange-core paths, Group 2 carries the routing change, canonical instruction, four adapters and their tests, and Group 3 carries the validation record and the protocol transcript last. That is least-dependent-first ordering.

### Findings and boundaries for step 5 code-reviewer round 3 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 5 code-reviewer round 3 (exchange 1)

No change is requested for the staged work. Step 5 is accepted as implemented,
and the remaining gate choice is the human one.

One small discoverability improvement is worth making later, recorded here rather
than as a finding because nothing in the staged subject depends on it. The
canonical instruction tells the reviewer to run `bin/code_review_answer.bat`
with a disposition but never states the two accepted tokens, and the CLI maps
reviewer-facing names rather than the envelope values: it accepts
`changes-requested` and `commit-ready`, not the `convergence-recommended` that
appears in the answer envelope. Because `--disposition` uses a converter rather
than `choices`, `--help` does not list the valid values either, and the failure
message is the bare `invalid disposition`.

The reviewer hit this first-hand while rendering this answer, passing the
envelope value and getting no hint of the accepted set. Naming both tokens in the
instruction step, or listing them in the argument help, would remove the guess
without changing behavior.

### Decision rationale for step 5 code-reviewer round 3 (exchange 1)

Commit-ready, advisory.

Every element of the readiness floor passes. Identity is exact and the live index
matched the request tree before assessment. The implementation is complete
against the numbered plan and was verified in round one by executing the
deliverable itself, through the `code-reviewer` skill, the canonical instruction,
and the three launchers it delegates to. All four resolved validation commands
pass with 100% coverage and zero outliers. The staged scope is entirely the
writer's, since this round produced no reviewer repair and the previous repair is
retained. No unresolved current or carried finding remains: the round-one trio
and the round-two heading finding are all closed and re-measured. `a.commit`
groups nineteen paths into three correctly ordered commits with zero validator
diagnostics.

This round made no substantive repair, which is the last condition the
instruction sets before a commit-ready recommendation is permitted.

The recommendation is advisory. It authorizes no commit, and the human gate
remains the sole authority for the `Commit` choice.

### Final reviewer decision for step 5 code-reviewer round 3 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-3 -->

## Round 3 by human - Step 5 - human-confirmation

- Recorded: 2026-08-18T14:18:39+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor - Step 6

- Recorded: 2026-08-18T15:12:25+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: request

### Review identity for step 6 code-reviewer round 1

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 6
Review round: 1

### Code review evidence for step 6 code-reviewer round 1

request_index_tree: 23c325b3b324dca532603b261eb4ec37fd13a5a1
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'early.rejection|commit-ready|changes-requested|outcome.*published|exit.*3' tests/unit/tools/test_code_reviewer_acceptance (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 6 code-reviewer round 1

Yes. Step 6 has been fully implemented. The staged acceptance package exercises the public request, evidence, answer, routing, exchange, recovery, and commit-plan seams over real temporary Git repositories. Every one of the design's sixteen acceptance cases has a named scenario, and an explicit mapping covers feature-request acceptance criteria 1 through 8.

Architecture remains within the existing boundaries: Step 6 adds tests only, reusable repository construction stays in the planned fixture module, and assessment, recovery, IO, and launcher responsibilities remain split. The tests use exact paths and linear bounded path sets; they grant the reviewer no requestor, human, escalation, commit, or umbrella-completion authority.

The focused 24-test package passed. Final post-fix `ghog day` completed 1,870 tests with `fail=0`, `warn=0`, `xfail=0`, `cov=100`, `outliers=0`, `excluded=0`, and `exit=0`; the full phase took 2m 37.8s and the slowest call took 0.30s. `git diff --cached --check` is clean, all new files stay below the 650-line ceiling, and the two-group `a.commit` parses without diagnostics.

### Implementation report for step 6 code-reviewer round 1

Step 6 adds the planned `test_code_reviewer_acceptance` package. Its shared fixture creates exact plans, validation plans, staged trees, review contexts, paired renderer inputs, and exchange cores in real temporary Git repositories.

The assessment module proves exact routing, early rejection, index drift, bounded repair ownership, validation-row permission, umbrella protection, failed mandatory evidence, and advisory convergence. The recovery module proves the no-progress bound, human guidance, retained manifests, interrupted publication replay, and exit-3 retirement. The IO module proves ignored and tracked validation effects, literal pathspecs, pure commit-plan validation, and forbidden authority. The launcher module starts each of the request, evidence, and answer launchers once.

Implementation checking marks Step 6 and the full six-step effort implemented, records the final performance and coverage evidence, and completes the code-reviewer umbrella row with the exact feature request and validation plan paths.

### Change summary for step 6 code-reviewer round 1

The staged subject contains eight paths in two ordered groups.

Group 1, `test(code-reviewer): prove responder acceptance`, contains the six new acceptance-package files: package marker, shared real-Git fixtures, assessment scenarios, recovery scenarios, IO and authority scenarios, and launcher smoke tests.

Group 2, `docs(code-reviewer): record step 6 validation`, contains the Step 6 validation-plan verdict and the matching completed umbrella row. Both Why sections use two narrative paragraphs and reference the review-mode umbrella draft, code-reviewer topic draft, feature request, design, implementation plan, and validation plan.

No production file changed in Step 6. The staged membership is exact, `a.commit` is ordered from tests to completion records, and no unrelated working-tree change exists.

### Writer response for step 6 code-reviewer round 1

Writer response: This is the first Step 6 review round, so there is no earlier reviewer feedback to accept or dispute.

The writer asks the reviewer to verify all sixteen design cases, all eight requirement criteria, real-Git and launcher boundaries, both answer outcomes, recovery and manifest behavior, the advisory authority limit, the final implementation-check verdict, umbrella completion, and the exact two-group commit plan.

### Reviewer focus for step 6 code-reviewer round 1

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-1 -->

## Round 1 by reviewer - Step 6

- Recorded: 2026-08-18T15:32:04+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 code-reviewer round 1 (exchange 1)

Baseline index tree: 23c325b3b324dca532603b261eb4ec37fd13a5a1

Assessed index tree: 23c325b3b324dca532603b261eb4ec37fd13a5a1

### Implementation check for step 6 code-reviewer round 1 (exchange 1)

Result: Step 6 is implemented apart from one hollow coverage claim, reported as the
single finding.

The sixteen design acceptance cases are genuinely covered. Identifiers `Design
case 01` through `Design case 16` all appear, each in the docstring of a real
journey test, so the plan's requirement that every design acceptance case has a
named test or parametrized case id is met exactly.

The journeys themselves are real. They build temporary efforts, start requests,
render answers through the Step 4 model, publish through
`ReviewExchangeCore.publish_answer`, and assert observable state. The
convergence journey renders a `CONVERGENCE_RECOMMENDED` assessment, publishes
it, asserts the exchange reaches `CONVERGENCE_GATE`, and asserts the answer text
carries "does not authorize a commit", which is the advisory boundary this
feature exists to protect. Retirement is exercised in the recovery module, and
publication appears across eleven call sites in the package. Testing through
public Python entry points rather than launcher exits is the plan's own Q06
decision, and a separate smoke module covers the launchers.

The step also closes the effort correctly at the document level. Every one of
the six per-step verdicts now reads `Yes`, and the validation plan's opening line
has been flipped to `Yes, it is implemented.`, which the canonical
implementation check requires once the last pending step turns green.

Umbrella row 5 is marked `completed` with both evidence paths, and the diff
touches that one row only. That is the writer's action to take on a final step;
reviewer mode is forbidden from completing an umbrella row and did not.

Validation plan effects: None. The reviewer wrote no validation-plan row this round.

### Pre-repair mandatory checks and coverage for step 6 code-reviewer round 1 (exchange 1)

All resolved commands pass, and no repair was needed, so the pre-repair and
post-assessment readings are the same.

`ghog day --force` reported `fail=0 warn=0 xfail=0 cov=100 outliers=0
excluded=0 exit=0` across 1,870 tests with the full phase at 2 minutes 26.2
seconds. `git diff --cached --check` exited 0.

The Step 6 completion grep returns six matching lines, and that result deserves a
caveat rather than a simple pass. Its pattern offers five alternatives, and only
two of them match anything: `early.rejection` and `changes-requested`. Neither
`commit-ready`, nor `outcome.*published`, nor `exit.*3` appears anywhere in the
acceptance package. The criterion's stated purpose is to find "both answer paths
and publication outcomes", and both are in fact covered, but by vocabulary the
pattern does not look for: the convergence path uses the
`ReviewDisposition.CONVERGENCE_RECOMMENDED` enum and asserts the
`ArtifactState.CONVERGENCE_GATE` state rather than the CLI's outcome strings or
exit codes. So the criterion passes on evidence it was not written to find, and
should not be quoted as proof that the publication outcomes are pinned.

### Resolved validation set and sources for step 6 code-reviewer round 1 (exchange 1)

Two commands, matching the request set: ghog day (project) and the Step 6 completion grep (plan), plus git diff --cached --check where the request adds it.

### Resolver drift and direction for step 6 code-reviewer round 1 (exchange 1)

None in either direction. The current resolver produces the same set as the published request.

### Repository state around validation for step 6 code-reviewer round 1 (exchange 1)

The request-time index tree `23c325b3b324dca532603b261eb4ec37fd13a5a1` matched
the live index exactly before assessment, and it is unchanged afterwards because
this round required no repair.

The umbrella digest is unchanged across the implementation-check result:
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b` before and
after, applicable true. The digest differs from earlier Step 5 rounds because the
writer legitimately marked row 5 `completed` before publishing this request; the
staged diff on that file is one line replaced by one line, touching no other row.

The ordered validation-state scope covered all eight staged step paths, and the
comparison reports `acceptable: true` with no tracked, ignored, or untracked
difference.

`git diff --cached --check` exits 0 and the staged Markdown is lint-clean under
the repository rules.

Disclosed for completeness: the two follow-up drafts and umbrella rows 7 and 8
that this reviewer authored earlier were committed in `2c37dc0` before Step 5
landed, so they are no longer working-tree changes and do not overlap this
subject. The only unstaged path is the protocol transcript carrying this round's
request append, which is expected during review.

### Repair inventory for step 6 code-reviewer round 1 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 code-reviewer round 1 (exchange 1)

Accurate, no amendment needed. validate_commit_plan over the parsed a.commit and the exact staged set returns zero diagnostics: two ordered groups, conventional subjects, exact membership over all eight paths, no duplicate or missing path. Group 1 test(code-reviewer): prove responder acceptance carries the six acceptance modules; Group 2 docs(code-reviewer): record step 6 validation carries the umbrella row completion and the validation record last. That is least-dependent-first ordering.

### Findings and boundaries for step 6 code-reviewer round 1 (exchange 1)

Unresolved findings:

- The test that claims the requirement's eight acceptance criteria are covered proves nothing. `test_requirement_acceptance_criteria_have_executable_case_coverage` builds a dict literal mapping 1 through 8 to eight short phrases and then asserts `tuple(covered) == tuple(range(1, 9))`, which compares the keys of a literal against the range that literal was written from. The function imports nothing, reads no module, names no test, and touches no file, so it cannot fail when an acceptance criterion loses its coverage, when an acceptance module is deleted, or when a journey stops asserting what its name claims. Its docstring states that AC01 through AC08 "stay mapped to executable Step 6 modules", but the code establishes no such mapping. This matters because it is the only artifact in the step that asserts the requirement's eight acceptance criteria are covered, and the plan's Step 6 requires exactly that alongside the sixteen design cases. The contrast inside the same file is instructive: the sixteen design cases are genuinely pinned, each named in the docstring of a real journey test, and all sixteen identifiers 01 through 16 are present. The same discipline applied here would make the claim real, for example by asserting that a named test exists for each criterion or by carrying AC identifiers in journey docstrings the way design case identifiers already are. The reviewer did not repair this, because choosing how to bind the criteria to tests is a test-design decision that belongs to the writer.

Boundary-crossing work: None.

### Writer instructions for step 6 code-reviewer round 1 (exchange 1)

Make `test_requirement_acceptance_criteria_have_executable_case_coverage` able to
fail. The current body asserts the keys of a dict literal against the range that
literal was written from, so it passes unconditionally. Bind each criterion to
something real instead: assert that a named test function exists for each of
AC01 through AC08, or carry `AC01` through `AC08` identifiers in the journey
docstrings exactly as `Design case 01` through `Design case 16` already are, and
assert every identifier is present. Either shape makes a lost criterion fail the
suite, which is what the plan asks Step 6 to prove.

Verify the change the way the design cases can be verified: remove one criterion
or rename one journey and confirm the suite goes red.

Separately, consider whether the Step 6 completion grep still says what you want.
Three of its five alternatives match nothing, because the acceptance journeys use
`ReviewDisposition.CONVERGENCE_RECOMMENDED` and `ArtifactState.CONVERGENCE_GATE`
rather than the CLI's outcome strings and exit codes. The behavior is covered, so
this is a criterion wording question rather than a coverage hole, but the grep
should not be quoted as proof that publication outcomes are pinned.

Nothing else is requested. The sixteen design cases, the journeys themselves, the
document-level status flip, the umbrella row completion, and `a.commit` are all
correct.

### Decision rationale for step 6 code-reviewer round 1 (exchange 1)

Changes-requested, on one unresolved finding.

The readiness floor this instruction defines requires the absence of unresolved
current findings, and the requirement-criteria coverage test is one. It is the
only artifact asserting that the requirement's eight acceptance criteria are
covered, the plan's Step 6 requires that coverage explicitly, and the test cannot
fail. Accepting it would mean recommending commit on the strength of a claim that
no execution can contradict, in the very step whose purpose is proving the
responder works.

The severity is bounded, and worth saying plainly so the fix is scoped
correctly. This is not a coverage hole in the journeys: the sixteen design cases
are genuinely pinned, the temporary-repository journeys exercise routing, early
rejection, repair attribution, umbrella mutation, validation outcomes, recovery,
and the advisory convergence gate, and the gate passes with 1,870 tests at 100%
coverage and zero outliers. What is missing is the binding between the eight
requirement criteria and those journeys, which is a small, well-understood
change.

Everything else in the step is correct. The reviewer made no repair, the umbrella
digest and validation state are unchanged, the document-level status is correctly
flipped now that all six steps read Yes, umbrella row 5 is completed by the
writer with both evidence paths, and `a.commit` validates with zero diagnostics
over eight paths in two correctly ordered groups.

### Final reviewer decision for step 6 code-reviewer round 1 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-1 -->

## Round 2 by requestor - Step 6

- Recorded: 2026-08-18T17:42:25+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: request

### Review identity for step 6 code-reviewer round 2

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 6
Review round: 2

### Code review evidence for step 6 code-reviewer round 2

request_index_tree: be0b9e01055f1fac434cc8e73e1c874972bde9ea
resolved_validation_set:

- ghog day (sources: project)
- rg -n 'early.rejection|commit-ready|changes-requested|outcome.*published|exit.*3' tests/unit/tools/test_code_reviewer_acceptance (sources: plan)
- git diff --cached --check (sources: request)

### Requestor assessment for step 6 code-reviewer round 2

Step 6 is fully implemented after the round-1 correction. The requirement-coverage test now parametrizes AC01 through AC08 with the module and function name of a real collected journey, imports each module, resolves each function, and requires the matching criterion marker in its docstring. Removing the AC08 marker made that exact mapping case fail; restoring it returned the focused module and final project walk to green.

All sixteen design cases remain attached to executable journeys. The final Groundhog walk completed 1,877 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`; the full phase took 2m 32.9s and its slowest call took 0.39s. `git diff --cached --check` exits 0, and the updated `a.commit` has two ordered groups over the exact nine staged paths.

The plan-defined completion grep remains an additive check, but this assessment does not use its unmatched alternatives as proof of publication outcomes. Publication behavior is established by the explicit disposition and durable-state assertions in the journeys, including convergence-gate publication and exit-3 manifest retirement.

### Implementation report for step 6 code-reviewer round 2

No production code changed in round 2. `test_code_reviewer_acceptance_tdd.py` replaces the self-confirming dictionary with an executable eight-case module/function map and marker assertion. The selected acceptance, IO, recovery, and launcher journeys now carry AC01 through AC08 identifiers, while their existing behavioral assertions remain unchanged.

The Step 6 validation record now names the 31-test focused package, the deliberate AC08 mutation failure, and the final 1,877-test timing and coverage evidence.

### Change summary for step 6 code-reviewer round 2

The staged subject contains nine paths in two ordered groups. `test(code-reviewer): prove responder acceptance` contains the six acceptance-package paths, including the executable AC mapping. `docs(code-reviewer): record step 6 validation` contains the umbrella completion, validation record, and durable Step 6 transcript.

The transcript contribution is a protocol-rendered pure append of 240 lines with no deletions. The test and documentation changes are staged, `git diff --cached --check` is clean, and `wac.bat` reports that `a.commit` needs no further changes.

### Writer response for step 6 code-reviewer round 2

Writer response: Accepted the round-1 finding without disagreement. The vacuous dictionary assertion is gone; every requirement criterion now names an importable test module and function and requires its AC marker on that executable journey. The requested mutation check was performed against AC08 and failed at the exact parametrized mapping case before restoration.

The completion-grep observation is also accepted as a boundary on how the evidence is described. The grep remains the implementation plan's exact command, but the round-2 assessment does not claim its unmatched tokens prove publication outcomes; the journeys' typed disposition, durable state, and retirement assertions provide that proof.

### Reviewer focus for step 6 code-reviewer round 2

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-2 -->

## Round 2 by reviewer - Step 6

- Recorded: 2026-08-18T20:00:00+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 code-reviewer round 2 (exchange 1)

Baseline index tree: be0b9e01055f1fac434cc8e73e1c874972bde9ea

Assessed index tree: be0b9e01055f1fac434cc8e73e1c874972bde9ea

### Implementation check for step 6 code-reviewer round 2 (exchange 1)

Result: Yes. Step 6 has been fully implemented.

The six planned acceptance files exist with the planned responsibilities and
stay inside their line budgets: `fixtures.py` at 259 lines, the assessment
module at 361, the recovery module at 261, the IO module at 124, and the
launcher smoke module at 41, all below the 550-line safe mark and the 650-line
ceiling. Repository construction stays in `fixtures.py`, and assessment,
recovery, IO, and launcher responsibilities remain in separate modules as the
split guidance requires.

All sixteen design acceptance cases carry a named test. Cases 01 through 09 and
13 are in `test_code_reviewer_acceptance_tdd.py`, cases 10 and 11 are in
`test_code_reviewer_io_acceptance_tdd.py`, and cases 12, 14, 15, and 16 are in
`test_code_reviewer_recovery_tdd.py`, with three unnumbered contract tests for
literal pathspec capture, side-effect-free commit-plan validation, and
convergence-publication manifest retirement.

The round-1 finding is closed. `_REQUIREMENT_CASES` no longer asserts a
dictionary against itself: each of the eight entries names a module and a
function, `importlib.import_module` and `getattr` resolve them, and the case
requires the exact `Requirement ACnn:` marker in the resolved function's
docstring. A wrong module, a renamed function, or a removed marker fails that
parametrized case rather than passing silently.

Reviewer mode found the exact Step 6 validation rows already accurate and
complete, including the required closing sentences for the architecture,
performance, and unit-test-coverage checks and the absence of a missing-work
section, so it wrote no validation-plan row in this round.

Validation plan effects: Reviewer mode wrote no validation-plan row in this round. The staged Step 6
rows already record the exact `Yes. Step 6 has been fully implemented.`
sentence, the implemented inventory, the new `Effort` type, and the
architecture, performance, unit-test-coverage, and feature-integrity
subsections with their required closing sentences, and no
`Missing work for Step 6` section remains. An idempotent reviewer rewrite would
have produced no difference, so none was made.

The document-level status line and the umbrella row 5 completion are staged
writer work under review, not reviewer edits. Reviewer mode neither wrote nor
completed either of them.

### Pre-repair mandatory checks and coverage for step 6 code-reviewer round 2 (exchange 1)

Every mandatory command in the union was run by the reviewer in this round, and
each one completed.

- `ghog day` exited `0`. The walk was a snapshot noop: no Python file changed
  since the last green walk. That green walk is evidence for this exact tree,
  because its snapshot `a.ghog.day.ok` is stamped `17:33:19` while the latest
  staged Python edit, `test_code_reviewer_acceptance_tdd.py`, is stamped
  `17:29:22`, and the only later staged edits are Markdown. That walk reported
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,877 tests
  in 2m 32.9s with a slowest call of 0.39s against a 0.50s floor.
- `rg -n 'early.rejection|commit-ready|changes-requested|outcome.*published|exit.*3' tests/unit/tools/test_code_reviewer_acceptance`
  exited `0` with six matching lines, all for `early.rejection` and one for
  `changes-requested`. The `commit-ready`, `outcome.*published`, and `exit.*3`
  alternatives matched nothing. This is recorded as boundary-crossing work
  below, not as missing behavior.
- `git diff --cached --check` exited `0` with no output.

Two additional checks were run as reviewer evidence rather than as mandatory
gate items. `ghog single tests/unit/tools/test_code_reviewer_acceptance`
collected and passed 31 tests with `fail=0 warn=0 xfail=0 exit=0`, which is
first-hand proof for this round that the eight parametrized requirement cases
resolve and that every named journey passes. `ruff check` over the acceptance
package reported `All checks passed!`.

Markdown lint over the three changed documents reported `TOTAL 0`, so the
appended round-1 transcript entry raises neither `MD024` nor `MD025`.

### Resolved validation set and sources for step 6 code-reviewer round 2 (exchange 1)

The request embeds three commands, and the union with the current resolver set
is the same three commands.

- `ghog day`, source `project`. It matches
  `DEFAULT_PROJECT_VALIDATION_COMMANDS` in `tools/code_review_validation.py`.
- `rg -n 'early.rejection|commit-ready|changes-requested|outcome.*published|exit.*3' tests/unit/tools/test_code_reviewer_acceptance`,
  source `plan`. It matches the second completion criterion of Step 6 in
  `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`.
- `git diff --cached --check`, source `request`. It is an additive request-side
  check.

The embedded set parses through the current `resolve_code_review_validation`
contract: three unique non-empty commands with unique valid source labels and a
non-empty project default.

### Resolver drift and direction for step 6 code-reviewer round 2 (exchange 1)

No resolver drift in either direction. The request-time set and the set the
current resolver produces from the same project default, plan addition, and
request addition are identical in commands, sources, and order, so the union
run adds nothing and drops nothing.

### Repository state around validation for step 6 code-reviewer round 2 (exchange 1)

The live index tree at reclaim, at capture, and after the full assessment is
`be0b9e01055f1fac434cc8e73e1c874972bde9ea`, matching the request-time tree
exactly, so no drift path exists and no early rejection applies.

The umbrella digest comparison over
`docs/v0.11.0/draft.v0.11.0.review-mode.md` reports
`changed: false`, before and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`. The staged
row 5 completion is pre-existing writer work inside the reviewed subject, not a
reviewer-authored umbrella write.

The ordered validation path set held seventeen entries: the nine staged step
paths, which already include the exact validation plan, plus the declared
`ghog day` artifacts `a.ghog.status`, `a.ghog.log`, `a.ghog.failures`,
`a.ghog.day.ok`, `a.ghog.senv.log`, `a.ghog.outliers`, `.coverage`, and
`htmlcov/index.html`. The before-and-after comparison over that same ordered
set reports `acceptable: true` with `tracked_paths` and `untracked_paths` both
empty; only the ignored paths `a.ghog.status` and `a.ghog.log` differ. No
tracked validation side effect was produced, so nothing had to be left unstaged
or unreverted.

### Repair inventory for step 6 code-reviewer round 2 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 code-reviewer round 2 (exchange 1)

`a.commit` is accurate and needed no amendment.

The typed commit-plan validator reports no diagnostics over the nine staged
paths in two groups. Group 1, `test(code-reviewer): prove responder
acceptance`, holds the six acceptance-package paths. Group 2,
`docs(code-reviewer): record step 6 validation`, holds
`docs/v0.11.0/draft.v0.11.0.review-mode.md`,
`docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`, and
`docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`. Membership matches
`git diff --cached --name-only` exactly, with no staged path missing from the
plan and no planned path absent from the index.

The order runs from least to most dependent: the tests that establish the
evidence come before the records that cite that evidence. Both subjects are
conventional, scoped to `code-reviewer`, and under the subject-length limit,
and each body states its own Why and What.

The unstaged round-2 append to
`docs/v0.11.0/review.code.v0.11.0.code-reviewer.md` is the live protocol
request and correctly stays out of the index and out of `a.commit`.

### Findings and boundaries for step 6 code-reviewer round 2 (exchange 1)

Unresolved findings: None.

Boundary-crossing work:

- Step 6 completion criterion 2 in `docs/v0.11.0/plan.v0.11.0.code-reviewer.md` states that the plan grep "finds both answer paths and publication outcomes", but three of its five alternatives match nothing: `commit-ready`, `outcome.*published`, and `exit.*3`. The command still exits 0 on the two alternatives that do match, so the criterion reads as green while its stated condition is false, and any later audit that runs the plan's own command will be misled. The behaviors themselves are proven more strongly than the grep can see, by `ArtifactState.CONVERGENCE_GATE` plus the "does not authorize a commit" assertion, by `payload["outcome"] == "published"`, and by the CLI exit code 3 assertion, so this is a defect in the plan's proxy rather than missing implementation. Correcting the plan text is a writer and human decision outside the reviewer's authority and outside the step's implementation files, so it is reported rather than changed.

### Writer instructions for step 6 code-reviewer round 2 (exchange 1)

The staged subject itself needs no rework. The acceptance package, the
validation record, the umbrella row, and `a.commit` are all correct, the
round-1 finding is closed, and every mandatory check passes. One item blocks
the advisory recommendation, and it is the plan text rather than the code.

Close Step 6 completion criterion 2 in
`docs/v0.11.0/plan.v0.11.0.code-reviewer.md`, which claims the plan grep finds
both answer paths and publication outcomes when it finds neither publication
outcome nor `commit-ready`. Take one of these two routes and publish round 3.

- Amend the criterion so it states what the journeys actually assert:
  convergence-gate state with the advisory wording, a `published` outcome, and
  CLI exit code 3. This is the recommended route, because the grep is a weaker
  check than the assertions that replaced it, and amending it leaves the tests
  untouched.
- Or make the three unmatched tokens appear on matched lines of the acceptance
  package. That needs only the convergence docstring to name `commit-ready`,
  the recovery assertion to place `outcome` and `published` on one line, and
  the exit assertion to read `exit 3`. This route is a substantive test change,
  so it needs its own round before a commit-ready recommendation.

Narrowing how the assessment describes its evidence, as round 2 did, leaves the
plan's criterion false, so it is not a third route. If the writer disagrees that
the criterion needs closing, record the disagreement through the requestor and
let the human gate decide; do not resolve it by rewording the assessment again.

Two optional polish items may ride along with either route. Neither blocks.

- `test_code_reviewer_acceptance_tdd.py` line 175 leaves one blank line before
  `def test_mismatched_identity_or_missing_tree_is_rejected_early`, where every
  other top-level definition in the file uses two. Ruff does not flag it,
  because its blank-line rules are preview-only under the current
  configuration.
- In `test_reviewer_instruction_denies_requestor_human_and_commit_authority`,
  the loop members `continue`, `confirm`, `complete`, and `escalate` also occur
  in unrelated prose in `instructions/code-reviewer.md`; `continue` matches the
  `--continue-owning-workflow-label` policy line alone. The test still binds,
  through `consume-answer`, `cancel`, and `The reviewer may call only`, but
  those four members prove nothing on their own and could assert against the
  forbidden-operations sentence instead.

### Decision rationale for step 6 code-reviewer round 2 (exchange 1)

All six readiness-floor results pass and this round made no substantive repair,
yet the disposition is `changes-requested`, because one boundary-crossing item
remains open and the answer contract forbids pairing any boundary-crossing work
with a commit-ready recommendation.

- Exact identity: the envelope, the human-readable identity block, the `pw`
  plan, step 6, round 2, and the request-time index tree all agree, and step 6
  exists in the exact plan.
- Complete implementation: the six planned files exist with the planned
  responsibilities and line budgets, all sixteen design acceptance cases carry
  a named test, and the eight requirement criteria now resolve to imported
  modules, resolved functions, and required docstring markers. The
  implementation-check result is Yes.
- Mandatory validation and coverage: all three resolved commands ran and
  completed, with `ghog day` at `exit=0` over a snapshot that postdates every
  staged Python edit, 1,877 tests, `cov=100`, and `outliers=0`.
- Attributable staged scope: the reviewer authored no tracked change, staged
  nothing, and left the index tree at
  `be0b9e01055f1fac434cc8e73e1c874972bde9ea`; the umbrella digest is unchanged
  and the validation-state comparison is acceptable with only ignored paths
  differing.
- Unresolved findings: none. The round-1 finding is closed by an executable
  mapping whose failure modes are real, and no new finding replaced it.
- `a.commit`: accurate, with no diagnostics over nine staged paths in two
  correctly ordered groups.

The open item is the Step 6 grep criterion. It is boundary-crossing work rather
than a finding, because the behaviors the criterion names are asserted by the
journeys with more force than a text search provides: the gap is in the plan's
proxy, not in the implementation, and correcting a plan criterion is a writer
and human decision the reviewer may report but not make. Round 2 answered the
same observation by narrowing how the assessment describes its evidence, which
changes the description without changing the criterion, so the item is still
open in this round.

The disposition follows the shipped contract rather than reviewer preference.
The implementation is complete, but `commit-ready` requires an empty
boundary-crossing inventory, and reporting the item in prose alone to keep that
inventory empty would route around the invariant instead of honoring it.

Two non-blocking observations remain for a later touch: a single-blank-line gap
before one top-level definition, and four non-discriminating members in the
authority test's substring loop. Neither affects behavior, the gate, or the
staged scope, and repairing either would have been a substantive tracked change
that could not validly finish this round.

This answer is advisory. It neither authorizes nor performs a commit, and
authority stays with the requestor and the human gate.

### Final reviewer decision for step 6 code-reviewer round 2 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-2 -->

## Round 3 by requestor - Step 6

- Recorded: 2026-08-18T20:53:58+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: request

### Review identity for step 6 code-reviewer round 3

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 6
Review round: 3

### Code review evidence for step 6 code-reviewer round 3

request_index_tree: 3802c3f4d2991a85e7175ca6452f6bd01c180541
resolved_validation_set:

- ghog day (sources: project)
- git diff --cached --check (sources: request)

### Requestor assessment for step 6 code-reviewer round 3

Step 6 is fully implemented after the round-2 corrections. The false grep proxy is gone from the completion criteria; the plan now requires the acceptance journeys' direct assertions for both answer paths, convergence-gate advisory state, a published outcome, and CLI exit 3. Those assertions already pass in the staged acceptance package.

The human-requested cold-session correction is inside Step 6's explicit allowance to update earlier production files for acceptance defects. `ABANDONED_REQUEST` now remains reviewer-owned in the typed route, ordinary and forced workflow entry both emit `code-reviewer`, and the canonical reviewer instruction performs one guarded reclaim before requiring the same request-pending round. Existing shared exchange tests continue to prove that reclaim preserves the request and returns `request-pending`.

The optional round-2 polish is also complete: the missing top-level blank line is restored, and the authority test asserts the exact forbidden-operation sentence instead of accepting unrelated substring matches. Final `ghog day` completed 1,877 tests with `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0`; the full phase took 2m 54.2s and its slowest call took 0.46s.

### Implementation report for step 6 code-reviewer round 3

The route owner now treats `REQUEST_PENDING` and `ABANDONED_REQUEST` as the two reviewer-owned request shapes. The forced code-reviewer dispatcher no longer rejects the abandoned shape, and its focused tests prove both ordinary and forced cold routing select `code-reviewer`.

The canonical reviewer sequence accepts an intact abandoned request at entry or later in the session, calls `reclaim` once, verifies the same identity and round returned to `request-pending`, and only then performs the bounded wait. Provider-specific adapters remain redirect-only; no adapter content was copied or forked.

The implementation plan now states the executable journey outcomes directly. The validation plan records the bounded earlier-step acceptance fix, corrected line counts, direct publication evidence, and the latest full-suite performance result.

### Change summary for step 6 code-reviewer round 3

The staged subject contains sixteen paths in three ordered groups. `fix(code-reviewer): let reviewers reclaim requests` contains the two routing modules, canonical instruction, and three focused test modules. `test(code-reviewer): prove responder acceptance` contains the six Step 6 acceptance-package paths. `docs(code-reviewer): record step 6 validation` contains the umbrella completion, implementation plan, validation record, and durable transcript.

The transcript remains a protocol-rendered pure append: 568 staged additions and zero deletions carry the completed round-1 and round-2 exchanges. `a.commit` keeps every Why section as two narrative paragraphs that cite the umbrella draft, topic draft, feature request, design, implementation plan, and validation plan. `git diff --cached --check` is clean.

### Writer response for step 6 code-reviewer round 3

Writer response: Accepted the round-2 plan-text finding without disagreement and took the recommended route. The completion criterion now names the journey assertions that actually establish publication behavior, so the non-discriminating grep is neither run nor presented as evidence in round 3.

Also accepted both optional polish observations. The top-level definition spacing is consistent, and the authority boundary is pinned to the exact `Never call` sentence plus the batch-commit and umbrella prohibitions.

The user additionally required cold reviewer sessions to reclaim an abandoned request. That acceptance defect is fixed across typed ownership, ordinary routing, forced routing, canonical reviewer instructions, and focused tests, and it is isolated in the first `a.commit` group. There is no disagreement and no reviewer-authored repair to assess.

### Reviewer focus for step 6 code-reviewer round 3

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-3 -->

## Round 3 by reviewer - Step 6

- Recorded: 2026-08-18T21:07:44+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 code-reviewer round 3 (exchange 1)

Baseline index tree: 3802c3f4d2991a85e7175ca6452f6bd01c180541

Assessed index tree: 3802c3f4d2991a85e7175ca6452f6bd01c180541

### Implementation check for step 6 code-reviewer round 3 (exchange 1)

Result: Yes. Step 6 has been fully implemented.

The round-2 finding is closed by the recommended route. Completion criterion 2
no longer runs a text search; it now reads "Acceptance journeys assert both
answer paths and the durable publication outcomes: convergence-gate advisory
state, a published outcome, and CLI exit 3." Each named outcome is asserted:
`envelope.disposition is ReviewDisposition.CHANGES_REQUESTED`, then
`ArtifactState.CONVERGENCE_GATE` paired with `does not authorize a commit`, and
finally `(code, payload["outcome"], payload["state"]) == (3, "published",
"convergence-gate")`. The false proxy is neither run nor presented as evidence.

Both optional polish items are done. The top-level definition spacing is
restored to two blank lines, and the authority test now pins the exact
`Never call ...` sentence over normalized whitespace plus `invoke batch commit`
and `never complete an umbrella row`, so no unrelated prose can satisfy it.

The cold-reclaim correction is coherent across its four surfaces.
`_actor_for_state` maps both `REQUEST_PENDING` and `ABANDONED_REQUEST` to the
reviewer, `CodeReviewRoute.__post_init__` still validates ownership against
that single partition, and `command_for_route` derives the instruction from the
actor, so ordinary and forced entry agree by construction rather than by a
second rule. The forced dispatcher's cold rejection is gone, and forced
`code-review-requestor` now returns `None` for that shape, which fails closed
instead of emitting the wrong role. No symbol was orphaned:
`CodeReviewRoutingError`, `CODE_REVIEW_REQUESTOR`, and the `ArtifactState`
import all remain in use. The specification reviewer's own cold-reclaim
diagnosis is deliberately untouched, which is correct for a different family.

Line budgets hold. `tools/prompt_workflow_skill.py` is 640,
`tools/prompt_workflow_code_review.py` is 277, and `instructions/code-reviewer.md`
is 190, matching the counts the validation record claims. The six acceptance
files keep their planned responsibilities, and all sixteen design acceptance
cases still carry a named test.

Reviewer mode found the exact Step 6 validation rows already accurate and
complete, including the required closing sentences and the absence of a
missing-work section, so it wrote no validation-plan row in this round.

Validation plan effects: Reviewer mode wrote no validation-plan row in this round. The staged Step 6
rows already record the exact `Yes. Step 6 has been fully implemented.`
sentence, the implemented inventory including the permitted earlier-step fix,
the `Effort` type, and the architecture, performance, unit-test-coverage, and
feature-integrity subsections with their required closing sentences. No
`Missing work for Step 6` section remains. An idempotent reviewer rewrite would
have produced no difference, so none was made.

The writer also refreshed the Step 5 rows so they describe the corrected
routing and the new line counts. Those counts check out: 640, 277, and 190
lines. That is writer-owned work under review, not a reviewer edit; reviewer
mode may write only the reviewed step's rows and wrote none.

The document-level status line and the umbrella row 5 completion are staged
writer work under review. Reviewer mode neither wrote nor completed either.

### Pre-repair mandatory checks and coverage for step 6 code-reviewer round 3 (exchange 1)

Both mandatory commands in the union were run by the reviewer in this round,
and each one completed.

- `ghog day` exited `0`. The walk was a snapshot noop: no Python file changed
  since the last green walk. That walk is evidence for this exact tree, because
  its snapshot `a.ghog.day.ok` is stamped `20:41:12` while the latest staged
  Python edit, `test_code_reviewer_io_acceptance_tdd.py`, is stamped `20:33:22`,
  and every later staged edit is Markdown. It reported `fail=0 warn=0 xfail=0
  cov=100 outliers=0 excluded=0 exit=0` over 1,877 tests in 2m 54.2s with a
  slowest call of 0.46s against the 0.50s floor.
- `git diff --cached --check` exited `0` with no output.

Additional reviewer evidence, beyond the mandatory set. A focused
`ghog single` over the acceptance package and the three changed routing and
instruction test packages passed with `fail=0 warn=0 xfail=0 exit=0` and no
focus or interaction failures, which is first-hand proof for this round that
the corrected cold-routing cases collect and pass. `ruff check` over the two
changed production modules and all four test packages reported
`All checks passed!`.

Markdown lint over the five changed or reviewed documents reported `TOTAL 0`,
so the appended round-1 and round-2 transcript entries raise neither `MD024`
nor `MD025`.

The round-2 plan grep is absent from the resolved set, as expected: it is no
longer a completion criterion, so it was neither resolved nor run.

### Resolved validation set and sources for step 6 code-reviewer round 3 (exchange 1)

The request embeds two commands, and the union with the current resolver set is
the same two commands.

- `ghog day`, source `project`. It matches
  `DEFAULT_PROJECT_VALIDATION_COMMANDS` in `tools/code_review_validation.py`.
- `git diff --cached --check`, source `request`. It is an additive
  request-side check.

There is no `plan` source in round 3. Step 6's rewritten completion criterion
now names journey assertions rather than a runnable command, so the plan
contributes no validation command. That is the intended consequence of the
round-2 correction, not an omission.

The embedded set parses through the current `resolve_code_review_validation`
contract: two unique non-empty commands with unique valid source labels and a
non-empty project default.

### Resolver drift and direction for step 6 code-reviewer round 3 (exchange 1)

No resolver drift in either direction. The request-time set and the set the
current resolver produces from the same project default and request addition
are identical in commands, sources, and order, so the union run adds nothing
and drops nothing.

The round-2 set carried a third `plan`-sourced command. Its removal is a
deliberate plan change accepted in this round rather than drift between the
request and the resolver, which agree exactly as they stand.

### Repository state around validation for step 6 code-reviewer round 3 (exchange 1)

The live index tree at `status`, at capture, and after the full assessment is
`3802c3f4d2991a85e7175ca6452f6bd01c180541`, matching the request-time tree
exactly, so no drift path exists and no early rejection applies.

The umbrella digest comparison over
`docs/v0.11.0/draft.v0.11.0.review-mode.md` reports `changed: false`, before
and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`. The staged
row 5 completion is pre-existing writer work inside the reviewed subject, not a
reviewer-authored umbrella write.

The ordered validation path set held twenty-four entries: the sixteen staged
paths, which already include the exact validation plan, plus the declared
`ghog day` artifacts `a.ghog.status`, `a.ghog.log`, `a.ghog.failures`,
`a.ghog.day.ok`, `a.ghog.senv.log`, `a.ghog.outliers`, `.coverage`, and
`htmlcov/index.html`. The before-and-after comparison over that same ordered
set reports `acceptable: true` with `tracked_paths` and `untracked_paths` both
empty; only the ignored paths `a.ghog.status` and `a.ghog.log` differ. No
tracked validation side effect was produced, so nothing had to be left unstaged
or unreverted.

The only unstaged tracked difference in the working tree is the protocol append
to `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`, which is the live
round-3 request and correctly stays out of the index.

### Repair inventory for step 6 code-reviewer round 3 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 code-reviewer round 3 (exchange 1)

`a.commit` is accurate and needed no amendment.

The typed commit-plan validator reports no diagnostics over the sixteen staged
paths in three groups. Group 1, `fix(code-reviewer): let reviewers reclaim
requests`, holds the two routing modules, the canonical instruction, and the
three focused test modules that pin the corrected behavior. Group 2,
`test(code-reviewer): prove responder acceptance`, holds the six Step 6
acceptance-package paths. Group 3, `docs(code-reviewer): record step 6
validation`, holds the umbrella draft, the implementation plan, the validation
record, and the durable transcript. Membership matches
`git diff --cached --name-only` exactly, with no staged path missing from the
plan and no planned path absent from the index.

The order runs from least to most dependent: the routing correction the
acceptance journeys exercise comes first, the acceptance package that proves it
comes second, and the records that cite both come last. All three subjects are
conventional, scoped to `code-reviewer`, and under the subject-length limit,
and each body states its own Why and What.

One grouping note that does not change the verdict. Group 3 carries the
implementation plan, whose only staged edit is the Step 6 completion criterion,
alongside the validation record. That is a defensible pairing, since the
criterion and the record it governs move together. If the writer resolves the
plan finding below by also correcting Step 5's stale text, the plan edit will
span two steps and would sit at least as well in group 1 with the behavior it
describes; either placement stays consistent, so this is a note rather than a
required change.

The unstaged round-3 append to
`docs/v0.11.0/review.code.v0.11.0.code-reviewer.md` is the live protocol
request and correctly stays out of the index and out of `a.commit`.

### Findings and boundaries for step 6 code-reviewer round 3 (exchange 1)

Unresolved findings: None.

Boundary-crossing work:

- `docs/v0.11.0/design.v0.11.0.code-reviewer.md` still specifies the routing rule this round reversed, in three places, and is not staged. Line 99 states that routing "adds a reviewer role only for a sole `request-pending` code-family exchange" and that "abandoned cold-route" states "continue to route to `code-review-requestor`". Line 101 states the forced route "cannot ... recover an abandoned request on behalf of a cold reviewer session". Line 114 states that "a cold route returns the state to the requestor reclaim path". The staged `_actor_for_state`, the staged forced dispatcher, and the staged canonical instruction now do the opposite of all three. Committing as staged ships an effort whose design of record contradicts its own code, and the design is the artifact the next reader implements from. Updating it is a design-surface decision outside Step 6's named files, so it is reported rather than changed.
- The staged `docs/v0.11.0/plan.v0.11.0.code-reviewer.md` carries the same stale rule in Step 5, two sections above the Step 6 criterion this round rewrote. The fix intent still reads "Route only one exact `request-pending` code exchange to `code-reviewer`; keep all other live states requestor-owned", and the tests-first bullet still requires "cold abandoned request refusal", while the staged test is now `test_forced_reviewer_accepts_a_cold_abandoned_request`. The writer updated Step 5's validation rows to describe the corrected routing but left Step 5's plan text describing the refusal, so the plan and its own validation record disagree. The file is already staged and in scope for the round, but the text belongs to another step, so the reviewer reports it instead of editing it.

### Writer instructions for step 6 code-reviewer round 3 (exchange 1)

Everything raised in round 2 is closed, and the staged code, tests, validation
record, and `a.commit` are correct. Two documents still describe the routing
rule this round reversed, and both must agree with the code before the effort
is committed. Fix both, then publish round 4.

- In `docs/v0.11.0/plan.v0.11.0.code-reviewer.md`, correct Step 5. The fix
  intent must stop saying that only an exact `request-pending` exchange routes
  to `code-reviewer` and that all other live states stay requestor-owned; it
  now also routes `abandoned-request`. The tests-first bullet must name cold
  abandoned request acceptance with one guarded reclaim instead of "cold
  abandoned request refusal". The file is already staged, so this is a text
  edit inside the existing group.
- In `docs/v0.11.0/design.v0.11.0.code-reviewer.md`, correct the three
  statements at the state-aware routing and fixed-policy sections: the reviewer
  role now covers `request-pending` and an intact `abandoned-request`; the
  forced route may enter a cold abandoned request; and the reviewer reclaims
  once at entry or in session rather than handing a cold route to the requestor
  reclaim path. Say why both shapes are reviewer-owned, namely that each
  retains the reviewer-owned request artifact and the reclaim transition is
  already shared, so the rule stays a single state partition.

Decide explicitly whether that design edit re-enters the specification review
exchange or is recorded as a human-directed amendment, and say which in the
next request. The reviewer cannot make that call.

Leave `instructions/code-review-requestor.md` alone. Its `abandoned-request`
row stays correct: a requestor whose own published request expires mid-session
still reclaims and resumes waiting, and only cold routing changed.

One optional grouping note, which blocks nothing. If the Step 5 plan correction
lands, the implementation-plan edit will span two steps, and the plan path may
fit `a.commit` group 1 better than group 3. Either placement is consistent;
keep whichever reads better once the edit exists.

### Decision rationale for step 6 code-reviewer round 3 (exchange 1)

All six readiness-floor results pass and this round made no substantive repair,
yet the disposition is `changes-requested`, because two boundary-crossing items
remain open and the answer contract forbids pairing any boundary-crossing work
with a commit-ready recommendation.

- Exact identity: the envelope, the human-readable identity block, the `pw`
  plan, step 6, round 3, and the request-time index tree all agree, and step 6
  exists in the exact plan.
- Complete implementation: the round-2 finding is closed through the
  recommended route, both polish items are done, and the cold-reclaim
  correction is coherent across the typed actor, ordinary routing, forced
  routing, the canonical instruction, and three focused test modules. The
  implementation-check result is Yes.
- Mandatory validation and coverage: both resolved commands ran and completed,
  with `ghog day` at `exit=0` over a snapshot that postdates every staged
  Python edit, 1,877 tests, `cov=100`, and `outliers=0`.
- Attributable staged scope: the reviewer authored no tracked change, staged
  nothing, and left the index tree at
  `3802c3f4d2991a85e7175ca6452f6bd01c180541`; the umbrella digest is unchanged
  and the validation-state comparison is acceptable with only ignored paths
  differing.
- Unresolved findings: none. Nothing carried from round 2 remains open, and no
  defect was found in the staged code or tests.
- `a.commit`: accurate, with no diagnostics over sixteen staged paths in three
  correctly ordered groups.

The two open items are the same defect in two documents: the design and the
plan's Step 5 still specify that a cold `abandoned-request` belongs to
`code-review-requestor`, which is exactly what this round's production change
reversed. They are boundary-crossing rather than findings, because the code is
right and the prose is stale: one lives in a design surface outside the step's
named files, and the other belongs to a different step of the same staged plan.
Neither is repairable under the reviewer's ownership rules.

They are also not cosmetic. The change was human-directed and correct, but the
design is the artifact the next implementer reads, and the plan now disagrees
with the validation record the writer updated beside it. Committing as staged
would freeze that contradiction into the effort's own history at the moment it
is marked complete.

The disposition follows the shipped contract rather than reviewer preference.
The implementation is complete, but `commit-ready` requires an empty
boundary-crossing inventory, and reporting these items in prose alone to keep
that inventory empty would route around the invariant instead of honoring it.

This answer is advisory. It neither authorizes nor performs a commit, and
authority stays with the requestor and the human gate.

### Final reviewer decision for step 6 code-reviewer round 3 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-3 -->

## Round 4 by requestor - Step 6

- Recorded: 2026-08-18T21:33:21+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: request

### Review identity for step 6 code-reviewer round 4

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 6
Review round: 4

### Code review evidence for step 6 code-reviewer round 4

request_index_tree: 7d53c647d83c8e9be6a507b48c5fcb43702e44fc
resolved_validation_set:

- ghog day (sources: project)
- git diff --cached --check (sources: request)

### Requestor assessment for step 6 code-reviewer round 4

Step 6 remains fully implemented, and both round-3 boundary items are closed. The design now assigns `request-pending` and intact `abandoned-request` shapes to one reviewer actor because both retain the reviewer-owned request artifact; ordinary and forced entry therefore share one state partition, and the canonical sequence performs the existing guarded reclaim.

Step 5 of the implementation plan now states the same rule in its fix intent, tests-first coverage, `CODE_REVIEWER` responsibility, and routing grep. The validation plan, code, tests, design, and plan are therefore consistent. `instructions/code-review-requestor.md` is intentionally unchanged because a requestor whose own published request expires still reclaims it legitimately.

This design correction is recorded as a human-directed amendment, not a restarted specification-review exchange. The user explicitly required cold reviewer sessions to reclaim abandoned requests and then explicitly instructed the requestor to apply round 3 and prepare round 4. Final Python evidence remains the 1,877-test green walk with 100% coverage, zero outliers, 2m 54.2s total, and a 0.46s slowest call; the post-documentation `ghog day` re-entry exits 0 by snapshot noop.

### Implementation report for step 6 code-reviewer round 4

The design's three stale routing statements now describe reviewer ownership for pending and intact abandoned requests, cold or in-session guarded reclaim, and the shared request artifact that makes the single partition correct.

The Step 5 plan no longer says pending-only, requestor-owned cold abandonment, or refusal. It now requires abandoned-request reviewer routing, guarded cold reclaim coverage, the expanded role responsibility, and a completion grep that includes `ABANDONED_REQUEST`.

No production or test code changed after round 3. The validation record notes the human-directed design amendment, and `a.commit` moves the design and implementation plan into the cold-reclaim fix group beside the behavior they specify.

### Change summary for step 6 code-reviewer round 4

The staged subject contains seventeen paths in three ordered groups. `fix(code-reviewer): let reviewers reclaim requests` now contains the two routing modules, canonical instruction, design, implementation plan, and three focused test modules. `test(code-reviewer): prove responder acceptance` contains the six acceptance-package paths. `docs(code-reviewer): record step 6 validation` contains the umbrella completion, validation record, and durable transcript.

The transcript is a protocol-rendered pure append of 926 staged lines with zero deletions through round 3. Every `a.commit` Why section remains exactly two narrative paragraphs citing the umbrella draft, topic draft, feature request, design, implementation plan, and validation plan. `wac.bat` reports no changes needed, and `git diff --cached --check` exits 0.

### Writer response for step 6 code-reviewer round 4

Writer response: Accepted both round-3 boundary items without disagreement. The design and all stale Step 5 plan statements now agree with the cold-reclaim implementation. The implementation-plan path moved from the final documentation group to the cold-reclaim fix group, and the newly staged design path joins that same group.

The design edit is a human-directed amendment and does not re-enter specification review. The user authorized the behavioral reversal and explicitly directed these round-3 changes; round 4 records that authority rather than opening a second specification exchange over an already decided rule.

As instructed, `instructions/code-review-requestor.md` remains unchanged. No reviewer repair was made, and no other finding or disagreement is carried forward.

### Reviewer focus for step 6 code-reviewer round 4

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-4 -->

## Round 4 by reviewer - Step 6

- Recorded: 2026-08-18T21:54:01+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 code-reviewer round 4 (exchange 1)

Baseline index tree: 7d53c647d83c8e9be6a507b48c5fcb43702e44fc

Assessed index tree: 7d53c647d83c8e9be6a507b48c5fcb43702e44fc

### Implementation check for step 6 code-reviewer round 4 (exchange 1)

Result: Yes. Step 6 has been fully implemented.

Both round-3 boundary items are closed, and the writer went past what was asked.

The design corrects all three stale statements and adds the reason the single
partition is sound: routing "assigns the reviewer role to a sole
`request-pending` code-family exchange or its intact `abandoned-request` form"
because "both shapes retain the reviewer-owned request artifact"; the forced
route "enters the same reviewer role so that the canonical sequence can perform
the shared guarded reclaim"; and the sequence "reclaims once ... then requires
the same round to return to `request-pending` before one bounded
`wait-request`", cold or in session.

The Step 5 plan corrects the two statements named in round 3 and two more the
reviewer had not flagged: the `CODE_REVIEWER` role constant is no longer
described as pending-only, and the Step 5 completion grep now includes
`ABANDONED_REQUEST`. Both Step 5 completion greps were run and still hold: the
routing grep returns ten lines and finds `ABANDONED_REQUEST` in
`prompt_workflow_code_review.py`, and the delegation grep returns fifteen.

Comparing the round-3 and round-4 index trees confirms the writer's claim that
no production or test code changed: only
`design.v0.11.0.code-reviewer.md`, `plan.v0.11.0.code-reviewer.md`,
`plan.v0.11.0.code-reviewer.validation.md`, and the transcript differ. The
Step 6 subject assessed and passed in round 3 is therefore unchanged, and its
`ghog day` snapshot still covers it.

An exhaustive sweep of every non-transcript document in this effort, the
canonical instruction, and all four host adapters found the routing rule stated
consistently everywhere except three Step 5 lines in the validation plan, which
are reported as boundary-crossing work below. The spec-reviewer family's own
cold-route statements are correctly untouched, since that family's behavior did
not change.

Reviewer mode found the exact Step 6 validation rows accurate and complete,
including the required closing sentences and the absence of a missing-work
section, so it wrote no validation-plan row in this round.

Validation plan effects: Reviewer mode wrote no validation-plan row in this round. The staged Step 6
rows already record the exact `Yes. Step 6 has been fully implemented.`
sentence, the implemented inventory including the permitted earlier-step fix,
the `Effort` type, and the architecture, performance, unit-test-coverage, and
feature-integrity subsections with their required closing sentences. No
`Missing work for Step 6` section remains, and an idempotent reviewer rewrite
would have produced no difference.

The writer refreshed the Step 5 `What was implemented` and `Architecture check`
subsections to describe the corrected routing and to record the human-directed
amendment. Three other Step 5 subsections were missed and still state the old
rule; they are reported as boundary-crossing work rather than repaired, because
reviewer mode may write only the reviewed step's rows.

The document-level status line and the umbrella row 5 completion are staged
writer work under review. Reviewer mode neither wrote nor completed either.

### Pre-repair mandatory checks and coverage for step 6 code-reviewer round 4 (exchange 1)

Both mandatory commands in the union were run by the reviewer in this round,
and each one completed.

- `ghog day` exited `0`. The walk was a snapshot noop: no Python file changed
  since the last green walk. The snapshot still covers this tree, because
  comparing the round-3 and round-4 index trees shows that only four
  documentation paths differ and no Python file among them. That walk reported
  `fail=0 warn=0 xfail=0 cov=100 outliers=0 excluded=0 exit=0` over 1,877 tests
  in 2m 54.2s with a slowest call of 0.46s against the 0.50s floor.
- `git diff --cached --check` exited `0` with no output.

Additional reviewer evidence, beyond the mandatory set. Both Step 5 completion
greps were run because this round edited one of them: the routing grep returns
ten lines and matches `ABANDONED_REQUEST` at
`tools/prompt_workflow_code_review.py:61`, and the delegation grep over the
canonical instruction returns fifteen lines. Markdown lint over the six changed
or reviewed documents, including the newly staged design, reported `TOTAL 0`,
so the appended round-1 through round-3 transcript entries raise neither
`MD024` nor `MD025`.

The focused acceptance and routing suites were not re-run this round. They
passed first-hand in round 3, and the index-tree comparison proves no test or
production file changed since, so a re-run would exercise identical bytes.

### Resolved validation set and sources for step 6 code-reviewer round 4 (exchange 1)

The request embeds two commands, and the union with the current resolver set is
the same two commands.

- `ghog day`, source `project`. It matches
  `DEFAULT_PROJECT_VALIDATION_COMMANDS` in `tools/code_review_validation.py`.
- `git diff --cached --check`, source `request`. It is an additive
  request-side check.

There is no `plan` source, because Step 6's completion criterion names journey
assertions rather than a runnable command. That remains the intended
consequence of the round-2 correction.

The embedded set parses through the current `resolve_code_review_validation`
contract: two unique non-empty commands with unique valid source labels and a
non-empty project default.

### Resolver drift and direction for step 6 code-reviewer round 4 (exchange 1)

No resolver drift in either direction. The request-time set and the set the
current resolver produces from the same project default and request addition
are identical in commands, sources, and order, so the union run adds nothing
and drops nothing. The set is unchanged from round 3.

### Repository state around validation for step 6 code-reviewer round 4 (exchange 1)

The live index tree at `status`, at capture, and after the full assessment is
`7d53c647d83c8e9be6a507b48c5fcb43702e44fc`, matching the request-time tree
exactly, so no drift path exists and no early rejection applies.

The umbrella digest comparison over
`docs/v0.11.0/draft.v0.11.0.review-mode.md` reports `changed: false`, before
and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`. The staged
row 5 completion is pre-existing writer work inside the reviewed subject, not a
reviewer-authored umbrella write.

The ordered validation path set held twenty-five entries: the seventeen staged
paths, which already include the exact validation plan and the newly staged
design, plus the declared `ghog day` artifacts `a.ghog.status`, `a.ghog.log`,
`a.ghog.failures`, `a.ghog.day.ok`, `a.ghog.senv.log`, `a.ghog.outliers`,
`.coverage`, and `htmlcov/index.html`. The before-and-after comparison over
that same ordered set reports `acceptable: true` with `tracked_paths` and
`untracked_paths` both empty; only the ignored paths `a.ghog.status` and
`a.ghog.log` differ. No tracked validation side effect was produced, so nothing
had to be left unstaged or unreverted.

The only unstaged tracked difference in the working tree is the protocol append
to `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`, which is the live
round-4 request and correctly stays out of the index.

### Repair inventory for step 6 code-reviewer round 4 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 code-reviewer round 4 (exchange 1)

`a.commit` is accurate and needed no amendment.

The typed commit-plan validator reports no diagnostics over the seventeen
staged paths in three groups. Group 1, `fix(code-reviewer): let reviewers
reclaim requests`, now holds the two routing modules, the canonical
instruction, the design, the implementation plan, and the three focused test
modules. Group 2, `test(code-reviewer): prove responder acceptance`, holds the
six acceptance-package paths. Group 3, `docs(code-reviewer): record step 6
validation`, holds the umbrella draft, the validation record, and the durable
transcript. Membership matches `git diff --cached --name-only` exactly, with no
staged path missing from the plan and no planned path absent from the index.

The regrouping is right. Round 3 noted that a plan edit spanning two steps
would sit better beside the behavior it specifies; the implementation plan
moved from group 3 to group 1, and the newly staged design joined it there, so
each specification now travels with the code and tests it governs.

The order still runs from least to most dependent: the routing correction with
its specification and tests, then the acceptance package that exercises it,
then the records that cite both. All three subjects are conventional, scoped to
`code-reviewer`, and under the subject-length limit, and each body states its
own Why and What.

The unstaged round-4 append to
`docs/v0.11.0/review.code.v0.11.0.code-reviewer.md` is the live protocol
request and correctly stays out of the index and out of `a.commit`.

### Findings and boundaries for step 6 code-reviewer round 4 (exchange 1)

Unresolved findings: None.

Boundary-crossing work:

- Three Step 5 subsections of the staged `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md` still assert the routing rule this effort reversed, and each is now false against the staged code. Line 413, under `### Step 5 improvement expectations`, reads "Every non-pending live state remains requestor-owned", but `abandoned-request` is a non-pending live state that `_actor_for_state` now assigns to the reviewer. Line 443, under `### Unit test coverage check for Step 5`, reads "reviewer ownership only for `request-pending`, requestor ownership for every other live or recovery state" and describes "cold-abandoned forced reviewer routes" as if the staged test still proved a refusal, when it is `test_forced_reviewer_accepts_a_cold_abandoned_request`. Line 449, under `### Feature integrity for Step 5`, reads "Every writer-owned, human-owned, abandoned cold-route, escalation, and repair-required state remains requestor-owned". The writer corrected the Step 5 `What was implemented` and `Architecture check` subsections in this round and missed these three, so the document now contradicts itself as well as the code, in the record that certifies the effort complete. The text belongs to another step, so the reviewer reports it rather than editing it.
- The reviewer should have found these three lines in round 3, when it found the design and Step 5 plan statements; it swept the plan and the design but read only the validation plan's diff instead of its full text. That miss is the reason this item spans a second round, and the sweep behind this round's report is exhaustive: every non-transcript document in the effort, the canonical instruction, and all four host adapters were searched, and these three lines are the complete remainder. The spec-reviewer family's cold-route statements are correctly untouched, because that family's behavior did not change.

### Writer instructions for step 6 code-reviewer round 4 (exchange 1)

Both round-3 items are closed, and the code, tests, design, Step 5 plan, Step 6
rows, and `a.commit` are all correct. Three sentences remain in the staged
validation plan, and they are the last of this defect. Fix them, then publish
round 5.

In `docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`, all in Step 5:

- Line 413, under `### Step 5 improvement expectations`: replace "Every
  non-pending live state remains requestor-owned" with the single-partition
  rule, that pending and intact abandoned requests are reviewer-owned and every
  writer-owned or stopped state stays requestor-owned.
- Line 443, under `### Unit test coverage check for Step 5`: replace "reviewer
  ownership only for `request-pending`, requestor ownership for every other
  live or recovery state" with the corrected partition, and restate
  "cold-abandoned forced reviewer routes" as forced cold abandoned-request
  acceptance, which is what `test_forced_reviewer_accepts_a_cold_abandoned_request`
  now proves.
- Line 449, under `### Feature integrity for Step 5`: drop "abandoned
  cold-route" from the list of states that remain requestor-owned, and say
  instead that an intact abandoned request stays reviewer-owned for one guarded
  reclaim.

The file is already staged and already edited this round, so this is a text
edit inside the existing group 3 with no regrouping needed.

Nothing else is outstanding. The reviewer swept every non-transcript document
in this effort, the canonical instruction, and all four host adapters; these
three lines are the complete remainder. Leave
`instructions/code-review-requestor.md` and every spec-reviewer document
unchanged, as before.

One optional idea, which blocks nothing and needs no round of its own. The
design's acceptance-case table still has sixteen rows and none of them names
the cold abandoned-request route, even though the design body now specifies it
and the routing tests prove it. A seventeenth row would keep the table a
complete inventory of reviewer-facing scenarios. It is a judgment call about
table completeness, not a correctness gap, so take it or leave it.

### Decision rationale for step 6 code-reviewer round 4 (exchange 1)

All six readiness-floor results pass and this round made no substantive repair,
yet the disposition is `changes-requested`, because one boundary-crossing item
remains open and the answer contract forbids pairing any boundary-crossing work
with a commit-ready recommendation.

- Exact identity: the envelope, the human-readable identity block, the `pw`
  plan, step 6, round 4, and the request-time index tree all agree, and step 6
  exists in the exact plan. The lease was live, so no reclaim was needed or
  performed.
- Complete implementation: both round-3 items are closed, the design records
  the rule and the reason behind it, and the Step 5 plan fixed two statements
  beyond those named. The Step 6 subject is byte-identical to the one assessed
  in round 3. The implementation-check result is Yes.
- Mandatory validation and coverage: both resolved commands ran and completed,
  with `ghog day` at `exit=0` over a snapshot that still covers this tree,
  1,877 tests, `cov=100`, and `outliers=0`.
- Attributable staged scope: the reviewer authored no tracked change, staged
  nothing, and left the index tree at
  `7d53c647d83c8e9be6a507b48c5fcb43702e44fc`; the umbrella digest is unchanged
  and the validation-state comparison is acceptable with only ignored paths
  differing.
- Unresolved findings: none. No defect was found in the staged code or tests.
- `a.commit`: accurate, with no diagnostics over seventeen staged paths in
  three correctly ordered groups, and the round-3 grouping note is applied.

The open item is the last remnant of the round-3 defect: three Step 5
subsections of the validation plan still state the pre-reversal routing rule.
It is boundary-crossing rather than a finding, because the code is right and
the prose is stale, and it belongs to a different step of the same staged
document, so it is not repairable under the reviewer's ownership rules.

It is also not cosmetic. The validation plan is what marks this effort
implemented and what `prepare-release` reads. Three of its sentences now
contradict both the shipped behavior and the two Step 5 subsections corrected
beside them, and committing as staged would freeze that contradiction into the
completion record.

This round would have been avoidable. The reviewer found the design and Step 5
plan statements in round 3 but read only the validation plan's diff instead of
its full text, so these three lines survived a round they should not have. The
sweep behind this answer is exhaustive across every non-transcript document,
the canonical instruction, and all four adapters, so round 5 can close this.

The disposition follows the shipped contract rather than reviewer preference.
The implementation is complete, but `commit-ready` requires an empty
boundary-crossing inventory, and reporting the item in prose alone to keep that
inventory empty would route around the invariant instead of honoring it.

This answer is advisory. It neither authorizes nor performs a commit, and
authority stays with the requestor and the human gate.

### Final reviewer decision for step 6 code-reviewer round 4 (exchange 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-4 -->

## Round 5 by requestor - Step 6

- Recorded: 2026-08-18T22:07:51+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: request

### Review identity for step 6 code-reviewer round 5

Umbrella draft: docs/v0.11.0/draft.v0.11.0.review-mode.md
Implementation plan: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
Implementation step: 6
Review round: 5

### Code review evidence for step 6 code-reviewer round 5

request_index_tree: 7ccce4e6d836ffc6f84b9c237e4f1b2c4f28800d
resolved_validation_set:

- ghog day (sources: project)
- git diff --cached --check (sources: request)

### Requestor assessment for step 6 code-reviewer round 5

Step 6 remains fully implemented, and the sole round-4 boundary-crossing item is closed. The three stale Step 5 validation subsections now use the same state partition as the implementation, design, implementation plan, and tests: `request-pending` and its intact `abandoned-request` recovery form are reviewer-owned, while writer-owned and stopped states remain requestor-owned.

The unit-test record now names forced cold abandoned-request acceptance through `test_forced_reviewer_accepts_a_cold_abandoned_request`, and the feature-integrity record reserves one guarded reclaim for the reviewer-owned intact abandoned request. A fixed-string sweep finds none of the three superseded formulations in non-transcript effort documents.

No production or test code changed after round 3. The existing full Python evidence therefore remains the 1,877-test green walk with 100% coverage, zero outliers, 2m 54.2s total, and a 0.46s slowest call; the current `ghog day` re-entry validates the documentation-only boundary against that snapshot.

### Implementation report for step 6 code-reviewer round 5

The Step 5 improvement expectations now assign pending requests and their intact abandoned form to the reviewer while retaining every writer-owned or stopped state with the requestor.

The Step 5 unit-test coverage subsection now describes the corrected partition and names the executable forced cold abandoned-request acceptance test. The feature-integrity subsection now records one guarded reviewer reclaim for the intact abandoned request and no longer classifies that state as requestor-owned.

No optional seventeenth design case was added. The design body already specifies the route and the focused tests execute it, so expanding the acceptance-case inventory is not necessary to close the correctness finding.

### Change summary for step 6 code-reviewer round 5

The staged subject still contains seventeen paths in three ordered groups. `fix(code-reviewer): let reviewers reclaim requests` contains the routing implementation, canonical instruction, design, implementation plan, and focused tests. `test(code-reviewer): prove responder acceptance` contains the six acceptance-package paths. `docs(code-reviewer): record step 6 validation` contains the umbrella completion, corrected validation record, and durable transcript.

The accepted wording corrections stay within the already staged validation-plan path and existing documentation group, so `a.commit` membership, grouping, order, and subjects remain accurate. Every Why section remains exactly two narrative paragraphs carrying the required umbrella draft, topic draft, feature request, design, implementation plan, and validation-plan references.

The protocol-rendered round-4 request and answer append remains unstaged. It is durable review history, not part of the immutable round-5 request index.

### Writer response for step 6 code-reviewer round 5

Writer response: Accepted the complete round-4 boundary item without disagreement. All three named Step 5 validation-plan statements now match the cold-reclaim implementation and the corrections already present in the design and implementation plan.

The optional seventeenth design-table row was not added because it was explicitly non-blocking and would duplicate behavior already stated in the design body and proved by focused tests. No reviewer repair was made, no requested correction was reversed, and no finding or boundary item is carried forward.

### Reviewer focus for step 6 code-reviewer round 5

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-5 -->

## Round 5 by reviewer - Step 6

- Recorded: 2026-08-18T22:16:07+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 code-reviewer round 5 (exchange 1)

Baseline index tree: 7ccce4e6d836ffc6f84b9c237e4f1b2c4f28800d

Assessed index tree: 7ccce4e6d836ffc6f84b9c237e4f1b2c4f28800d

### Implementation check for step 6 code-reviewer round 5 (exchange 1)

Result: Yes. Step 6 has been fully implemented.

The sole round-4 boundary item is closed. All three Step 5 validation
subsections now state the same partition as the code: the improvement
expectation reads "Pending requests and their intact abandoned form are
reviewer-owned; every writer-owned or stopped state remains requestor-owned";
the unit-test subsection describes that partition and names
`test_forced_reviewer_accepts_a_cold_abandoned_request`, which exists at
`tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_code_reviewer_tdd.py:158`;
and the feature-integrity subsection reserves one guarded reclaim for the
intact abandoned request instead of classifying it as requestor-owned.

The reviewer repeated the exhaustive sweep behind round 4. No superseded
formulation survives in any non-transcript effort document, the canonical
instruction, or the four host adapters, and every remaining ownership statement
across the design, implementation plan, validation plan, and instruction was
read individually and agrees with `_actor_for_state`. The transcript keeps the
earlier wording as durable history, which is correct.

Comparing the round-4 and round-5 index trees shows exactly one changed path,
`docs/v0.11.0/plan.v0.11.0.code-reviewer.validation.md`. The requested
correction was made and nothing else moved, so the Step 6 subject is
byte-identical to the one this reviewer assessed and ran in earlier rounds.

Step 6's three completion criteria all hold. `ghog day` exits 0 with the
project coverage gate. The acceptance journeys assert both answer paths and the
durable publication outcomes, through `ReviewDisposition.CHANGES_REQUESTED`,
`ArtifactState.CONVERGENCE_GATE` with "does not authorize a commit", and
`(code, payload["outcome"], payload["state"]) == (3, "published",
"convergence-gate")`. Every one of the sixteen design acceptance cases has a
named test, and all eight requirement criteria resolve through imported
modules, resolved functions, and required docstring markers.

The Step 6 validation rows are accurate and complete, with the exact Yes
sentence, all three required closing sentences, and no missing-work section, so
reviewer mode wrote no validation-plan row.

The declined seventeenth design case was offered as explicitly optional and
take-it-or-leave-it. The writer declined it with a reason, that the design body
already specifies the route and focused tests execute it. That reasoning is
sound and the decline is accepted; it is not an open item.

Validation plan effects: Reviewer mode wrote no validation-plan row in this round, so it produced no
validation-plan difference at all.

The staged Step 6 rows already record the exact `Yes. Step 6 has been fully
implemented.` sentence, the implemented inventory, the `Effort` type, and the
architecture, performance, unit-test-coverage, and feature-integrity
subsections with their required closing sentences. No `Missing work for Step 6`
section remains, and an idempotent reviewer rewrite would have produced no
difference.

The three corrected Step 5 subsections are writer work under review, not
reviewer edits. Reviewer mode may write only the reviewed step's rows and wrote
none, so the whole staged validation-plan difference in this round is
writer-authored.

The document-level `Yes, it is implemented.` line and the umbrella row 5
completion, with both evidence paths present, are staged writer work. Reviewer
mode neither wrote nor completed either.

### Pre-repair mandatory checks and coverage for step 6 code-reviewer round 5 (exchange 1)

Both mandatory commands in the union were run by the reviewer in this round,
and each one completed.

- `ghog day` exited `0`. The walk was a snapshot noop: no Python file changed
  since the last green walk. The snapshot still covers this tree, because the
  round-4 to round-5 index-tree comparison shows exactly one changed path and
  it is Markdown. That walk reported `fail=0 warn=0 xfail=0 cov=100
  outliers=0 excluded=0 exit=0` over 1,877 tests in 2m 54.2s with a slowest
  call of 0.46s against the 0.50s floor.
- `git diff --cached --check` exited `0` with no output.

Because this round recommends convergence, the reviewer did not rely on the
snapshot alone. A focused `ghog single` over the acceptance package and the
three routing and instruction packages collected and passed 141 tests with
`fail=0 warn=0 xfail=0 exit=0`, with no focus failures and no interaction or
ordering suspects. That is direct evidence in this round that every journey and
routing case behind the recommendation passes against the exact staged tree.

Markdown lint over the six changed or reviewed documents reported `TOTAL 0`, so
the accumulated transcript raises neither `MD024` nor `MD025`.

No mandatory evidence was unavailable, deferred, or substituted at any point in
this round.

### Resolved validation set and sources for step 6 code-reviewer round 5 (exchange 1)

The request embeds two commands, and the union with the current resolver set is
the same two commands.

- `ghog day`, source `project`. It matches
  `DEFAULT_PROJECT_VALIDATION_COMMANDS` in `tools/code_review_validation.py`.
- `git diff --cached --check`, source `request`. It is an additive
  request-side check.

There is no `plan` source, because Step 6's completion criterion names journey
assertions rather than a runnable command. That remains the intended
consequence of the round-2 correction.

The embedded set parses through the current `resolve_code_review_validation`
contract: two unique non-empty commands with unique valid source labels and a
non-empty project default.

### Resolver drift and direction for step 6 code-reviewer round 5 (exchange 1)

No resolver drift in either direction. The request-time set and the set the
current resolver produces from the same project default and request addition
are identical in commands, sources, and order, so the union run adds nothing
and drops nothing. The set is unchanged from rounds 3 and 4.

### Repository state around validation for step 6 code-reviewer round 5 (exchange 1)

The live index tree at `status`, at capture, and after the full assessment is
`7ccce4e6d836ffc6f84b9c237e4f1b2c4f28800d`, matching the request-time tree
exactly, so no drift path exists and no early rejection applies.

The umbrella digest comparison over
`docs/v0.11.0/draft.v0.11.0.review-mode.md` reports `changed: false`, before
and after both
`23c41ad3a750ffa604ccea4a8ccf36e1ed9eae265931cd0eb101378c5be9181b`. The staged
row 5 completion, carrying both evidence paths, is pre-existing writer work
inside the reviewed subject, not a reviewer-authored umbrella write.

The ordered validation path set held twenty-five entries: the seventeen staged
paths, which already include the exact validation plan and the design, plus the
declared `ghog day` artifacts `a.ghog.status`, `a.ghog.log`, `a.ghog.failures`,
`a.ghog.day.ok`, `a.ghog.senv.log`, `a.ghog.outliers`, `.coverage`, and
`htmlcov/index.html`. The before-and-after comparison over that same ordered
set reports `acceptable: true` with `tracked_paths` and `untracked_paths` both
empty; only the ignored paths `a.ghog.status` and `a.ghog.log` differ, from the
reviewer's own gate and focused runs. No tracked validation side effect was
produced, so nothing had to be left unstaged or unreverted.

The only unstaged tracked difference in the working tree is the protocol append
to `docs/v0.11.0/review.code.v0.11.0.code-reviewer.md`, holding the round-4
exchange and the live round-5 request. It is durable review history and
correctly stays out of the immutable round-5 index.

### Repair inventory for step 6 code-reviewer round 5 (exchange 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 code-reviewer round 5 (exchange 1)

`a.commit` is accurate and needed no amendment.

The typed commit-plan validator reports no diagnostics over the seventeen
staged paths in three groups. Group 1, `fix(code-reviewer): let reviewers
reclaim requests`, holds the two routing modules, the canonical instruction,
the design, the implementation plan, and the three focused test modules.
Group 2, `test(code-reviewer): prove responder acceptance`, holds the six
acceptance-package paths. Group 3, `docs(code-reviewer): record step 6
validation`, holds the umbrella draft, the corrected validation record, and the
durable transcript. Membership matches `git diff --cached --name-only` exactly,
with no staged path missing from the plan and no planned path absent from the
index.

This round's correction landed inside the already staged validation-plan path,
so membership, grouping, order, and subjects are unchanged and still correct.
No regrouping was needed and none was made.

The order runs from least to most dependent: the routing correction with the
specification and tests that define it, then the acceptance package that
exercises it, then the records that cite both. All three subjects are
conventional, scoped to `code-reviewer`, and under the subject-length limit,
and each body carries its own Why and What.

The unstaged transcript append is the round-4 exchange plus the live round-5
request. It is protocol history rather than staged implementation, so its
absence from `a.commit` is correct.

### Findings and boundaries for step 6 code-reviewer round 5 (exchange 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 6 code-reviewer round 5 (exchange 1)

No further writer action is required on the staged subject. The round-4 item is
closed, no finding or boundary item is carried forward, and the reviewer
requests no change.

The staged seventeen paths, the three commit groups, the Step 5 and Step 6
validation rows, the document-level status line, and the completed umbrella row
are all consistent with the code and with each other. Leave them as they stand
and take the exchange to the human gate.

The declined seventeenth design case needs no revisiting. It was offered as
optional, the decline was reasoned, and the reviewer accepts it.

`instructions/code-review-requestor.md` and every spec-reviewer document remain
correctly unchanged, since that family's cold-route behavior did not change.

Present the recommendation, the identity summary, and both registered labels to
the human. `Commit` continues the owning workflow; `Rework and review again`
returns authority for a replacement request. This recommendation does not
authorize a commit, and the reviewer performs none.

### Decision rationale for step 6 code-reviewer round 5 (exchange 1)

All six readiness-floor results pass, the boundary-crossing inventory is empty,
and this round made no substantive repair, so the disposition is an advisory
`commit-ready` recommendation.

- Exact identity: the envelope, the human-readable identity block, the `pw`
  plan, step 6, round 5, and the request-time index tree all agree, and step 6
  exists in the exact plan. `status` reported `request-pending` with a positive
  `exchange_occurrence`, so no reclaim was needed or performed, and the round-4
  `continue` typo the requestor reported left no trace in the exchange state.
- Complete implementation: all three Step 6 completion criteria hold, all
  sixteen design acceptance cases have a named test, and all eight requirement
  criteria resolve to executable journeys. The implementation-check result is
  Yes.
- Mandatory validation and coverage: both resolved commands ran and completed,
  and a focused 141-test run passed in this round as direct evidence rather
  than a carried-forward result.
- Attributable staged scope: the reviewer authored no tracked change, staged
  nothing, and left the index tree at
  `7ccce4e6d836ffc6f84b9c237e4f1b2c4f28800d`; the umbrella digest is unchanged
  and the validation-state comparison is acceptable with only ignored paths
  differing.
- Unresolved findings: none, current or carried. The round-4 item is closed at
  all three named lines, and an exhaustive re-sweep across every non-transcript
  effort document, the canonical instruction, and all four adapters found no
  remaining superseded formulation.
- `a.commit`: accurate, with no diagnostics over seventeen staged paths in
  three correctly ordered groups.

The four earlier rounds each closed on evidence rather than on wording. Round 1
replaced a self-confirming requirement map with imported modules, resolved
functions, and asserted markers. Round 2 replaced a false grep proxy with the
journey assertions that actually establish publication behavior. Rounds 3 and 4
brought the design, the Step 5 plan, and finally three Step 5 validation
subsections into agreement with the human-directed routing reversal. Nothing
was closed by narrowing a claim.

One process note, recorded for accuracy rather than as an open item: the
round-4 report existed because this reviewer read only the validation plan's
diff in round 3 instead of its full text, so three stale lines survived a round
they should not have. The sweep behind rounds 4 and 5 is exhaustive, and this
recommendation rests on it.

The recommendation is advisory and does not authorize a commit. Authority stays
with the requestor and the durable human gate, where `Commit` and
`Rework and review again` remain the human's choice. The reviewer performs no
commit, consumes no answer, and continues no round.

### Final reviewer decision for step 6 code-reviewer round 5 (exchange 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-5 -->

## Round 5 by human - Step 6 - human-confirmation

- Recorded: 2026-08-18T22:25:11+02:00
- Exchange: code/code/v0.11.0/code-reviewer
- Umbrella: docs/v0.11.0/draft.v0.11.0.review-mode.md
- Reviewed document: docs/v0.11.0/plan.v0.11.0.code-reviewer.md
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-5 -->
