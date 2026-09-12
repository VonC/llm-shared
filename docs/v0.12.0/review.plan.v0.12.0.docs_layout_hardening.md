# Specification review transcript for v0.12.0

- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-09-12T17:50:31+02:00
- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan docs_layout_hardening (round 1)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
Review round: 1

### Requestor assessment for plan docs_layout_hardening (round 1)

The four-step plan implements the settled issue and design without reopening
their contracts. All six proposed answers are option A. The questions cover
the extraction boundary, step sequence, property-test scope, IO/error test
instrumentation, real Git acceptance, and bounded selection coverage.

No additional implementation question is currently identified. Each question
has two options with pros and cons, an explicit BBQ mapping, a recommendation
and an answered proposal. The validation skeleton matches all four steps and
contains no claimed implementation evidence. Review only the plain plan's
questions; inspect the skeleton for alignment as supporting context.

The 650-line source baseline and existing test sizes were checked in the tree.
The plan preserves the docs facade, exact versus role matching, uncached
eligibility, local timestamp ties, contextual failures and missing-draft
post-commit behavior. It uses one shared groundhog walk and deterministic IO
checks rather than introducing a performance target absent from the design.

Please verify practical extraction dependencies, the tests-first step boundaries,
coverage of all sixteen acceptance rows, the invalid-parent CLI fixture, and
the policy-band/split guidance. No reviewer wording has yet been received.

### Change summary for plan docs_layout_hardening (round 1)

Initial implementation plan and aligned validation skeleton written beside the
settled effort documents. Four steps cover behavior-preserving lookup extraction,
content eligibility, scoped selection, and CLI/post-commit acceptance plus
layout guidance. Six implementation-only questions were placed using oqm.

Short IO clarification sections were added to the issue and design, repeating
their accepted uncached filename-only recognition and unchanged downstream IO;
no settled decision changed. No implementation code or tests were edited.

### Writer response for plan docs_layout_hardening (round 1)

Writer response:

First plan round. The writer recommends the six option A proposals, subject to
independent review, and will apply substantive corrections before another
round. The design's prior consolidation authorization does not authorize this
plan's consolidation. Keep the plan questions and validation placeholders
intact until this exchange reaches its own human decision.

### Reviewer focus for plan docs_layout_hardening (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.12.0.docs_layout_hardening.md`
- `.reviews/a.review-requested.plan.v0.12.0.docs_layout_hardening.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-09-12T17:55:45+02:00
- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan docs_layout_hardening round 1

#### Reviewer assessment of the layout-hardening implementation plan for plan docs_layout_hardening (round 1)

The four-step sequence is right. A behavior-preserving extraction before either
behavior change is the correct order for a module sitting exactly on its
ceiling, and splitting recognition from scoped selection keeps each step with a
narrow observable contract. The validation skeleton matches all four steps and
claims no evidence. The six questions are implementation questions, and I would
answer option A to all six.

Every measurable fact I checked holds. `tools/prompt_workflow_docs.py` is 650
lines, `prompt_workflow.py` 618, post-commit 91, models 149, steps 266, the docs
TDD suite 611, the lookup TDD suite 59, the skill suite 650 and
`test_prompt_workflow_main.py` 614. `senv.bat` sets
`PYTHON_BIG_FILE_LINE_LIMIT=650`. The CLI does use `docs.DOCUMENT_TYPES`,
post-commit does use `docs.VERSION_RE`, and tests do reach `docs._doc_matches`,
`docs._exact_doc_matches` and `docs.most_recent`.

What does not hold is the plan's account of which existing tests change. That
matters more here than anywhere else, because the plan's own rule is that each
step ends on a green shared walk, and two steps would go red on tests they never
planned to open.

##### Step 2 breaks three existing tests, not one for plan docs_layout_hardening (round 1)

The confirmed-facts section says "The current docs test has one empty
version-and-slug fixture that must acquire a qualifying file in Step 2", and
Step 2 repeats it as "Update the old empty positive fixture". In
`tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py`:

- `test_docs_dirs_supports_all_layouts` (line 314) creates an empty
  `docs/v9.8.0/topic` and asserts `docs_dirs` returns it.
- `test_docs_dirs_includes_version_slug_layout` (line 598) creates an empty
  `docs/v1.2.3/my_effort` and asserts both `docs_dirs` and
  `docs_dirs_for_version` return it.

That is two empty fixtures, and the consolidated issue's acceptance criterion 5
named both. The third case is not empty and is the interesting one:
`test_resolve_document_uses_only_version_slug_and_type` (line 336) is
parameterized over five layouts including `docs/v9.8.0/topic`, and writes
`plan.v9.8.0.git-history-report.md` into it. The directory is named `topic`
while its only document carries the slug `git_history_report`, so under the
settled identity rule that directory stops qualifying and
`resolve_document` returns `None` where the test expects the path. Adding a file
does not fix it; the fixture needs a directory name and a document slug that
agree.

The Step 2 addendum estimates the suite at 611 going to 613. Three fixtures,
one of which needs its parameter or its filename changed, is not a two-line
edit.

##### Step 3 breaks two more, and lists no existing test file for plan docs_layout_hardening (round 1)

Step 3's files involved are the lookup module and two new selection test files.
No existing suite appears. But `_ISO`, defined at line 26 of the same docs TDD
file as
`Topic(version="v9.8.0", slug="iso", draft_path=Path("d.md"))`, carries a
relative draft path. `d.md` resolves against the test process working directory,
so its parent is never a member of `docs_dirs(tmp_path)`, and both tests using
it exercise precisely the unrecognized-parent fallback that Step 3 replaces with
an error:

- `test_find_matching_documents_per_role` (line 423) calls
  `find_matching_documents(tmp_path, _ISO, role)` four times and expects lists.
- `test_most_recent_and_select_document` (line 500) calls
  `select_document(tmp_path, _ISO, "design")` and expects the newer file.

Under design Q07 option A both entry points raise `PromptWorkflowError` for an
unrecognized parent, so both tests fail. Step 3 has no entry for repairing them
and no line budget for the suite that holds them.

##### The relative draft path is an idiom, not one fixture for plan docs_layout_hardening (round 1)

`_ISO` is not alone. `test_prompt_workflow_main.py` line 54 and
`test_prompt_workflow_plan.py` line 55 both define topics as
`draft_path=Path("docs/draft.v9.8.0.iso.md")`, and
`test_prompt_workflow_models.py` line 32 uses `Path("d.md")`. Any of those used
against a `tmp_path` root has a parent outside that root.

The plan should state the fixture rule that follows from the settled contract
rather than leave the implementer to rediscover it one red test at a time: a
topic exercised against a temporary root needs a draft path under that root,
because the parent check is a directory-membership check and a path resolved
against the process working directory can never satisfy it.

##### The extraction-safety claim is the wrong way round for plan docs_layout_hardening (round 1)

The confirmed-facts section states "No caller currently patches the extracted
directory or selector functions." Two tests do:

- `tests/unit/tools/test_prompt_workflow_main.py:544`,
  `monkeypatch.setattr(prompt_workflow.docs, "resolve_document", ...)`.
- `tests/unit/tools/test_prompt_workflow_steps.py:79`,
  `monkeypatch.setattr(steps.docs, "select_document", ...)`.

Both patch the attribute on the facade module, and both callers read that
attribute at call time, so a re-export that binds module-level names in the
facade keeps them working. The conclusion the plan drew survives; the fact it
rests on does not. Recording the two sites converts an assumption into the
constraint it actually is: the facade must re-export as module-level names, and
Step 1 must not switch `prompt_workflow.py` or `prompt_workflow_steps.py` to
import the lookup module directly, which would silently strip both patches.

##### Everything else in the plan for plan docs_layout_hardening (round 1)

The line-budget table, the policy bands, the shared walk contract, the IO and
complexity clarifications, the refusal to add a timing gate the design never
promised, and the instruction to keep new cases out of the 611-line suite are
all sound. The IO clarification sections added to the issue and design restate
accepted decisions without changing any of them.

### Question verdicts for plan docs_layout_hardening round 1

#### Reviewer verdicts on the six plan questions for plan docs_layout_hardening (round 1)

All six are implementation questions rather than requirement or design
questions, each has two materially distinct options, and none reopens a settled
contract. I would answer option A to all six. No seventh question is needed: the
findings in this round are corrections to stated facts and step contents, not
decisions the plan failed to put to the human.

##### Plan answers this reviewer would choose for plan docs_layout_hardening (round 1)

| Question | Answer | Reason in one line |
| --- | --- | --- |
| Q01 | A | The lookup block is contiguous, depends only on models, and is the responsibility this effort extends. |
| Q02 | A | A module at its ceiling with several callers earns a behavior-preserving checkpoint before two behavior changes. |
| Q03 | A | Properties fit the filename grammar; an uncached predicate has too few states to repay a stateful harness. |
| Q04 | A | Only scoped instrumentation matches the accepted IO contracts; broad guards reject legitimate downstream reads. |
| Q05 | A | Stubbed Git cannot establish that the invalid-parent path is reachable from real topic discovery. |
| Q06 | A | A role-by-outcome matrix plus focused edge cases covers every policy branch without a Cartesian product. |

##### Verdict on Q01 about the extraction boundary for plan docs_layout_hardening (round 1)

Keep as written. Option B is a genuine alternative rather than a straw
alternative: collection parsing really is a separable block. Option A wins
because the lookup block is what Steps 2 and 3 grow, and leaving it in place
would mean adding behavior to a file with no headroom.

The answer's instruction to give the extracted module its own directory-slug
expression, never importing `COLLECTION_SLUG_RE`, is the plan-level expression
of the issue's independence requirement, and the Step 1 `rg` check inspects for
exactly that. Good.

One addition belongs in this question's answer rather than in a new question:
the facade must re-export module-level names, because two suites patch
`docs.resolve_document` and `docs.select_document` through the facade attribute.

##### Verdict on Q02 about the step sequence for plan docs_layout_hardening (round 1)

Keep as written. My answer is option A. The con is honest about the cost, that
the old selection policy persists between Steps 2 and 3, and that transient
state is fine because Step 2's contract is recognition alone.

This question's premise is where the missing test work shows: keeping four steps
is only a real checkpoint if each step lists the tests it must repair. Step 2
names one fixture where three change, and Step 3 names none where two change.

##### Verdict on Q03 about property-based testing scope for plan docs_layout_hardening (round 1)

Keep as written. My answer is option A. Generating filesystem mutation sequences
would buy ordering coverage for a predicate whose whole contract is that it
holds no state between calls. The instruction to use explicit generated expected
identities rather than `_exact_doc_matches` as the oracle is the right call and
is the part most often skipped.

##### Verdict on Q04 about IO guards and failure injection for plan docs_layout_hardening (round 1)

Keep as written. My answer is option A. The con names the real difficulty, that
eligibility access has to be distinguished from fallback matching, and Step 3
already writes the honest version of that limit: prove selection does not
rediscover scope, but do not claim it avoids the eligibility inventory's reads.

##### Verdict on Q05 about real temporary Git repositories for plan docs_layout_hardening (round 1)

Keep as written. My answer is option A. Option B cannot establish what Step 4
exists to establish. A stubbed topic is chosen, not discovered, so it cannot
show that a branch-relevant draft under an unsupported parent reaches the
invalid-parent boundary through the real path.

##### Verdict on Q06 about bounding the selection matrix for plan docs_layout_hardening (round 1)

Keep as written. My answer is option A, with the evidence map its con calls for.
Requiring same-version fallback filenames in other recognized version
directories is a good detail: it is what catches an implementation that
quietly makes the fallback version-scoped when the settled contract spans every
recognized directory.

### Requested changes for plan docs_layout_hardening round 1

Requested changes:

#### Requested changes to the layout-hardening implementation plan for plan docs_layout_hardening (round 1)

Five edits, all in the confirmed facts and in Steps 2 and 3. No question, answer
or step boundary changes.

##### Change 1 in the confirmed code and test facts for plan docs_layout_hardening (round 1)

Replace the single-fixture sentence with what the suite actually holds:

```text
Three cases in the current docs suite depend on version-and-slug recognition.
`test_docs_dirs_supports_all_layouts` and
`test_docs_dirs_includes_version_slug_layout` each create an empty slug
directory and assert discovery returns it.
`test_resolve_document_uses_only_version_slug_and_type` is parameterized over
`docs/v9.8.0/topic` and writes `plan.v9.8.0.git-history-report.md` there, so its
directory name and document slug disagree. All three change in Step 2.
```

##### Change 2 in the confirmed code and test facts for plan docs_layout_hardening (round 1)

Correct the patching claim and state the constraint it carries:

```text
Two suites patch selectors through the facade attribute:
`tests/unit/tools/test_prompt_workflow_main.py` replaces `docs.resolve_document`
and `tests/unit/tools/test_prompt_workflow_steps.py` replaces
`docs.select_document`. Both callers read those attributes at call time, so the
facade must re-export module-level names and no caller may switch to importing
the lookup module directly; either change would strip both patches silently.
```

##### Change 3 in the confirmed code and test facts for plan docs_layout_hardening (round 1)

Add the fixture rule the settled parent check imposes, since relative draft
paths are used across several suites:

```text
Topic fixtures carrying a relative draft path, such as `Path("d.md")` in the
docs suite and `Path("docs/draft.v9.8.0.iso.md")` in the main and plan suites,
resolve against the process working directory. Their parent is never a member of
`docs_dirs(tmp_path)`, so after Step 3 they reach the invalid-parent error. A
topic exercised against a temporary root needs a draft path under that root.
```

##### Change 4 in Step 2 for plan docs_layout_hardening (round 1)

In the tests-first paragraph, replace "Update the old empty positive fixture
with one qualifying immediate document" with the three repairs:

```text
Repair the three existing recognition cases: give each empty slug-directory
fixture one qualifying immediate document, and make the parameterized
`docs/v9.8.0/topic` resolution case agree with itself, either by naming the
directory for the document slug it contains or by writing a document whose slug
matches the directory.
```

Update the Step 2 addendum's estimate for the 611-line suite accordingly; 613 is
the estimate for the single-fixture reading being replaced.

##### Change 5 in Step 3 for plan docs_layout_hardening (round 1)

Add the existing suite to the files involved and to the tests-first paragraph:

```text
- `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py`
  (existing, to be updated).
```

```text
Repair the two existing selection cases that rely on the replaced fallback.
`test_find_matching_documents_per_role` and `test_most_recent_and_select_document`
both use the module-level `_ISO` topic, whose relative draft path leaves its
parent outside the temporary root, so both currently exercise the
unrecognized-parent fallback. Give that fixture a draft path inside the
temporary root, and cover the invalid-parent error in the new selection package
instead.
```

Add the resulting count to the Step 3 addendum's line budget, which currently
lists no existing file.

### Writer instructions for plan docs_layout_hardening round 1

#### Writer instructions for the next layout-hardening plan round for plan docs_layout_hardening (round 1)

1. Apply the five requested changes. Three correct the confirmed facts, one
   rewrites a sentence in Step 2, one adds the existing suite to Step 3.
2. Change no question, no answer and no step boundary. All six directions are
   accepted and the four-step sequence is right.
3. Do not reopen the issue or the design. Everything raised here is about what
   the plan says the existing tests do.
4. Recount the two line-budget entries the corrections touch: the docs suite in
   Step 2, where the estimate assumes a single fixture edit, and Step 3, which
   currently budgets no existing file at all.

Verify the three Step 2 cases and the two Step 3 cases in the tree before
rewriting the sentences, rather than copying the line numbers from this answer.
The one that repays a second look is the parameterized resolution case: it is
not an empty directory, and it fails for a different reason from the other two,
because the directory is named `topic` while its document carries the slug
`git_history_report`.

Publish a replacement request for another automated round. With these five edits
and nothing else changed, I expect that round to be convergence-ready.
Consolidation stays with the human at the convergence gate, and this answer does
not recommend it.

### Final reviewer decision for plan docs_layout_hardening round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-09-12T17:58:18+02:00
- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan docs_layout_hardening (round 2)

Umbrella draft: none
Reviewed specification: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
Review round: 2

### Requestor assessment for plan docs_layout_hardening (round 2)

All six option A proposals remain sufficient. No new implementation question
is identified, and no question, answer or numbered step changed. The four-step
validation skeleton remains aligned and unimplemented.

All five requested corrections were checked against the current source/tests
and applied. The three recognition fixtures include two empty positive cases
and one directory/document identity mismatch. The two selection cases really
use a relative _ISO topic outside tmp_path; their repairs now belong to Step 3.
The facade-patching claim is corrected, and Step 1 explicitly preserves callers'
module-attribute lookup. The docs suite remains 611 physical lines before any
implementation; advisory post-step estimates now allow the five repairs.

The broader relative-topic audit distinguishes actual discovery from stubbed
selectors and constructed-state or field-only tests. Main/steps monkeypatches
and plan/models field use do not require blanket fixture rewrites. The rule
is explicit for any topic sent through real candidate discovery.

Markdown checking and git diff whitespace checking pass after the corrections.
No source implementation or test execution is claimed. The plan is ready for
another independent assessment of the corrected facts and step contents.

### Change summary for plan docs_layout_hardening (round 2)

Applied round 1's five requested changes:

1. Replaced the one-fixture claim with the two empty discovery cases and the
   nonempty mismatched-slug resolution case.
2. Recorded the main and steps facade selector patches and retained their
   module-attribute access in the extraction instructions.
3. Added the temporary-root canonical-parent fixture rule and the verified
   distinction between real discovery and isolated caller/model tests.
4. Listed all three Step 2 repairs, choosing a matching git-history-report
   directory parameter for the existing resolver case; revised its advisory
   docs-suite estimate to 625 while retaining the measured 611 baseline.
5. Added the existing docs suite and both relative-topic repairs to Step 3,
   with a measured-before-step checkpoint, 650 ceiling, advisory total 640,
   and a selection-responsibility split only if the ceiling is exceeded.

Also recorded the inspected 329-line plan and 64-line models test modules in
the baseline table. Questions Q01-Q06, answers A, the four step boundaries,
validation skeleton, issue and design are unchanged from round 1.

### Writer response for plan docs_layout_hardening (round 2)

Writer response:

The writer accepts all requested corrections. Direct inspection confirmed
each named recognition/selection fixture and the facade monkeypatch sites.
The single-fixture and no-patching claims were wrong and are now corrected.

The plan now schedules the five required fixture repairs in their owning
steps, without changing accepted options or step boundaries. The relative-path
rule is qualified to real discovery because the inspected main/steps tests
stub that boundary, and plan/models tests construct state or inspect fields.
This qualification preserves the requested fixture rule without predicting
failures in tests that never invoke the new parent check.

No disagreement is raised. Please review the corrected plan for convergence;
the questions remain intact for the human's plan-consolidation decision.

### Reviewer focus for plan docs_layout_hardening (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-09-12T18:02:09+02:00
- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan docs_layout_hardening round 2

#### Reviewer assessment of the corrected implementation plan for plan docs_layout_hardening (round 2)

All five requested changes are applied, and the one place where the writer went
past the request improved the result. The plan is ready for the human's choice.

##### The test-impact audit is now correct and complete for plan docs_layout_hardening (round 2)

I rechecked each corrected fact in the tree rather than against the change
summary. The three Step 2 cases are the three that exist, the two Step 3 cases
are the two that exist, and both facade patch sites are recorded with the
constraint they impose.

I also looked for affected fixtures the corrections might still have missed.
Only the docs suite builds version-and-slug directory fixtures anywhere in
`tests/`. The one other place that writes into that layout,
`test_run_from_draft_places_draft_in_selected_docs_layout`, puts
`draft.v0.5.0.topic.md` into `docs/v0.5.0/topic/`, where the directory name and
the document slug already agree, and it asserts a written path rather than
discovery. Nothing outside the docs suite changes, which is what the plan now
says.

##### The Step 2 repair choice is the right one and it works for plan docs_layout_hardening (round 2)

Changing the parameterized case to `docs/v9.8.0/git-history-report` while
keeping `plan.v9.8.0.git-history-report.md` and the folded `git_history_report`
selector is better than adding a second document. The directory name satisfies
the accepted slug language, `_exact_doc_matches` folds both sides to
`git_history_report`, so the directory qualifies and the resolver finds the
file. It also preserves what that test is for, one document resolved the same
way in every supported layout, instead of turning one parameter into a special
case. The plan's own sentence, that this fixes identity disagreement rather than
missing content, is the distinction that matters.

The Step 3 repair is equally sound. Giving those two tests per-test topics whose
draft paths sit under the temporary root's `docs` directory keeps their role and
newest-file expectations intact, and putting the new invalid-parent cases in the
new selection package keeps the 611-line suite from growing into its ceiling.
The note that the draft file need not exist is consistent with the design's
directory-only parent check.

##### The relative-topic qualification is better than what I asked for for plan docs_layout_hardening (round 2)

Round one asked for a fixture rule and observed that relative draft paths appear
in several suites. The plan states the rule for topics sent through real
candidate discovery, then distinguishes tests that stub the boundary, construct
state, or only read fields. I verified that distinction:
`test_prompt_workflow_plan.py` never calls `select_document`,
`find_matching_documents` or `docs_dirs`, and the models suite builds a
`WorkflowState` whose document fields are already resolved. Neither reaches the
new parent check, so neither needs a rewrite.

That is the correct scope. A blanket rule would have sent the implementer to
edit fixtures in four suites to prevent failures that cannot occur.

##### Line budgets and remaining facts for plan docs_layout_hardening (round 2)

The two added baseline rows measure correctly at 329 and 64 lines. The docs
suite is still 611 before implementation, Step 2's advisory estimate moved to
625 for three fixture repairs, and Step 3 now carries the suite with an advisory
640 including the Step 2 changes and a split instruction if the ceiling is
threatened. Every earlier count I verified in round one is unchanged.

##### Questions, steps and the validation skeleton for plan docs_layout_hardening (round 2)

Six questions, all answered option A, all implementation questions. Four step
boundaries unchanged. The validation skeleton still matches all four steps and
claims no evidence. Nothing was consolidated ahead of the human's decision, and
the issue and design were not reopened.

### Question verdicts for plan docs_layout_hardening round 2

#### Reviewer verdicts on the six plan questions after correction for plan docs_layout_hardening (round 2)

All six are accepted as written with answer option A. No question changed in
round two, none needs to, and no seventh is missing.

##### Plan answers this reviewer would choose in round two for plan docs_layout_hardening (round 2)

| Question | Answer | Reason in one line |
| --- | --- | --- |
| Q01 | A | The lookup block is contiguous, depends only on models, and is what Steps 2 and 3 grow. |
| Q02 | A | A file at its ceiling with several callers earns a behavior-preserving checkpoint first. |
| Q03 | A | Properties fit the filename grammar; an uncached predicate has too few states for a stateful harness. |
| Q04 | A | Only scoped instrumentation matches the accepted IO contracts. |
| Q05 | A | A stubbed topic is chosen rather than discovered, so it cannot prove the invalid-parent path is reachable. |
| Q06 | A | A role-by-outcome matrix with focused edge cases covers every branch without a Cartesian product. |

##### What the corrections did to Q01 and Q02 for plan docs_layout_hardening (round 2)

Neither question changed, and both are better supported now. Q01's answer rests
on the extraction preserving callers, and the facts section now records the two
facade patch sites and the constraint that keeps them working: module-level
re-exports, callers still importing the facade. That converts the option A con,
"requires careful constant ownership and characterization of exported helpers",
from a general caution into something the implementer can check.

Q02's premise is that each step is a reviewable checkpoint with a green walk.
That premise only held once each step listed the tests it must repair. Step 2
now names three and Step 3 names two, so the checkpoints are real.

##### No question is missing for plan docs_layout_hardening (round 2)

The five fixture repairs are determined by the settled contract rather than
chosen, so they belong in step contents rather than in a question. The choice
between renaming the parameterized directory and adding a second document is an
implementation detail inside Q01's and Q02's accepted approach, and the plan
picked the option that preserves what the test exists to prove.

Nothing else in the plan asks the human to decide something it has not already
put in front of them.

### Convergence evidence for plan docs_layout_hardening round 2

Covered wording:

#### Covered wording for the implementation plan for plan docs_layout_hardening (round 2)

Two optional items. Neither changes a fact, a step, a question or an answer, and
the plan is convergence-ready with or without them. Apply them during
consolidation if the human keeps this recommendation, or leave them.

##### Optional polish in the selection-fixture paragraph for plan docs_layout_hardening (round 2)

The sentence beginning "Its parent resolves against the process working
directory" follows two test names, so "Its" reads as belonging to the second
test rather than to the topic. Suggested replacement:

```text
That topic's parent resolves against the process working directory, outside the
temporary root's recognized directories.
```

##### Optional polish in the re-export paragraph for plan docs_layout_hardening (round 2)

The paragraph names `docs._doc_matches` and `docs._exact_doc_matches` as tested
access paths to retain. `docs.most_recent` is exercised directly as well, in the
same suite. It is public, so "all public lookup signatures through explicit
re-exports" already covers it, and naming it would make the list complete for a
reader checking the re-export against the tests:

```text
Existing tests also exercise `docs._doc_matches`, `docs._exact_doc_matches` and
`docs.most_recent`; retain those access paths.
```

##### Wording confirmed as correct in round two for plan docs_layout_hardening (round 2)

The following read correctly and need no change: the facade-patching paragraph
and its constraint, the three Step 2 repairs including the identity-disagreement
sentence, the Step 3 repairs and their placement of new invalid-parent cases,
the temporary-root fixture rule with its real-discovery qualification, the two
added baseline rows, and the revised Step 2 and Step 3 line budgets.

Convergence rationale:

#### Convergence rationale for the implementation plan for plan docs_layout_hardening (round 2)

Round one accepted the four-step sequence and all six answers, and found that
the plan's account of the existing tests was wrong in four places: one
version-and-slug fixture where three cases change, no existing test file listed
in the step that breaks two more, a claim that no caller patches the functions
being extracted when two suites do, and a line estimate following the
single-fixture reading.

Round two corrects all four, and the correction is verified rather than
asserted. The three Step 2 cases and the two Step 3 cases are the ones in the
tree, the two patch sites are recorded with the constraint that keeps them
working, and the budgets moved to 625 and 640. I also searched for fixtures the
corrections could still have missed and found none: no suite outside the docs
tests builds a version-and-slug directory, and the one test that writes into
that layout already has a directory name and document slug that agree.

The writer went past the request in one place and was right to. Round one said
relative draft paths appear in several suites; the plan states the rule for
topics sent through real candidate discovery and then separates the tests that
stub that boundary or only read fields. I confirmed the plan suite never calls
the selectors and the models suite builds already-resolved state. A blanket rule
would have sent the implementer editing four suites against failures that cannot
happen.

Every implementation decision is settled. The extraction boundary with facade
re-exports, four steps each ending on a green shared walk, bounded filename
properties with an independent oracle, scoped IO guards with injected errors,
real temporary Git repositories for the acceptance flows, and a role-by-outcome
matrix mapped to the design's sixteen rows. The line-budget policy, the shared
walk contract, and the refusal to add a timing gate the design never promised
are unchanged and correct.

What remains is two cosmetic items recorded in the covered wording, an ambiguous
pronoun and one function name that would complete a list. Neither changes what
gets built, and neither justifies another automated round.

This recommendation is advisory and authorizes nothing. The consolidation
choice, and the labels offered for it, belong to the human at the convergence
gate.

### Writer instructions for plan docs_layout_hardening round 2

#### Writer instructions at the implementation-plan convergence gate for plan docs_layout_hardening (round 2)

No change is requested. All five round-one corrections are applied and verified,
and the relative-topic qualification the writer added is correct.

1. Present the six questions, their recommended options and their answers to the
   human with the two registered labels, and make no edit before that choice.
2. If the human selects consolidation, the two cosmetic items in the covered
   wording may be applied with it. Skipping them changes nothing.
3. If the human selects another round instead, that round needs a reason from
   the human: this reviewer has none to supply.
4. Keep the validation skeleton's four steps aligned with the plan's, as the
   shared checklist already requires. Nothing in this round changed the
   sequence, so no realignment is due.

Do not treat this recommendation as authorization. Consolidation, the
implementation decisions table and the removal of the open-questions section
stay with the owning workflow after the human confirms. Implementation itself
begins only after that, one step at a time, through the reviewed commits the
plan describes.

### Final reviewer decision for plan docs_layout_hardening round 2

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-2 -->

## Round 2 by human - human-confirmation

- Recorded: 2026-09-12T19:14:53+02:00
- Exchange: specification/plan/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
