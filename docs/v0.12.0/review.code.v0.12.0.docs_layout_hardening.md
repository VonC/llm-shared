# Code review transcript for v0.12.0

- Exchange: code/code/v0.12.0/docs_layout_hardening
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-09-12T19:40:47+02:00
- Exchange: code/code/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 docs_layout_hardening (round 1)

Umbrella draft: none
Implementation plan: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 docs_layout_hardening (round 1)

request_index_tree: d2dfc0c90e663997a08d28454fde63393f76a283
resolved_validation_set:

- ghog day (sources: project, plan)
- rg -n 'prompt_workflow_docs|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py (sources: plan)
- rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(workflow): characterize document lookup
group 1 path: tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
group 1 path: tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
group 2: refactor(workflow): extract document lookup
group 2 path: tools/prompt_workflow_docs.py
group 2 path: tools/prompt_workflow_document_lookup.py
group 3: docs(docs_layout_hardening): record step 1 validation
group 3 path: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md
staged path: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md
staged path: tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
staged path: tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
staged path: tools/prompt_workflow_docs.py
staged path: tools/prompt_workflow_document_lookup.py
```

### Requestor assessment for step 1 docs_layout_hardening (round 1)

Step 1 is fully implemented. The validation plan records the exact Yes verdict;
Steps 2 through 4 remain pending. This round covers only the behavior-preserving
lookup extraction, its characterization tests and its validation record.

The groundhog walk finished on 2026-09-12 at 19:33:26 +02:00 with state=done
and exit=0. Ty, Pyright, Ruff, complexity, dead-code, line-budget, Markdown,
ShellCheck and EOF checks passed. The affected phase ran 221 tests; the full
phase ran 2,714 tests, with no failures, warnings or xfails and cov=100.
Coverage is configured for tools, including both changed production modules.
The full phase took 3m 58.6s and reported outliers and exclusions as skipped.
This does not establish a duration threshold.

Static inspection found no facade or collection-regex dependency in lookup.
CLI and steps still call facade attributes; existing monkeypatch seams remain.
There is no new class, traversal, sort, body read, cache or candidate comparison.
The moved lookup body is unchanged apart from the independent equivalent slug
expression. File counts are 501, 274, 87 and 6, all below 650.
The first walk failed import-policy checks; explicit exports and the
annotation-only Path import corrected them before the successful walk.
Afterward, only equivalent CRLF-to-LF normalization was applied to source
for a readable diff, followed by the writer-owned validation document update.

### Implementation report for step 1 docs_layout_hardening (round 1)

Extracted docs_dirs through select_document and associated filename/layout
constants from tools/prompt_workflow_docs.py into
tools/prompt_workflow_document_lookup.py. Lookup depends on standard-library
modules and workflow models, never the docs facade or collection validator.

The facade explicitly re-exports all lookup names and retains VERSION_RE,
Git-derived topic discovery, collection parsing and body-marker readers.
Explicit __all__ lists preserve the supported import surface under the
repository's lint and type-checking policies. The lookup directory-slug
expression has the same accepted language as COLLECTION_SLUG_RE.

The new unit-test package supplies four cases using real temporary files.
They check ambiguity path diagnostics, canonical-parent preference over a newer
external match, plan versus validation-plan lookup, separator folding,
subtopic matching, equal timestamp ordering and later timestamp changes.
The old shape-only effort recognition and fallback remain for Steps 2 and 3.

### Change summary for step 1 docs_layout_hardening (round 1)

Five staged paths are covered by the mechanically valid root a.commit:

1. test(workflow): characterize document lookup
   - tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
   - tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
2. refactor(workflow): extract document lookup
   - tools/prompt_workflow_docs.py
   - tools/prompt_workflow_document_lookup.py
3. docs(docs_layout_hardening): record step 1 validation
   - docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md

The characterization tests use the pre-existing facade and can precede the
extraction. The completed validation record is the final documentation group.
No caller imports or unrelated files were changed.

### Writer response for step 1 docs_layout_hardening (round 1)

Writer response:

This is the first implementation review round for Step 1. There is no earlier
code-review feedback to accept or dispute. The settled specification and plan
decisions are implemented only to the extent assigned to Step 1.

### Reviewer focus for step 1 docs_layout_hardening (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `C:/Users/vonc/git/llm-shared/.reviews/a.review-active.code.code.v0.12.0.docs_layout_hardening.md`
- `C:/Users/vonc/git/llm-shared/.reviews/a.review-requested.code.v0.12.0.docs_layout_hardening.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-09-12T19:57:32+02:00
- Exchange: code/code/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 docs_layout_hardening (exchange 1) (round 1)

Baseline index tree: d2dfc0c90e663997a08d28454fde63393f76a283

Assessed index tree: d2dfc0c90e663997a08d28454fde63393f76a283

### Implementation check for step 1 docs_layout_hardening (exchange 1) (round 1)

Result:

#### Reviewer implementation check for the lookup extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

Yes. Step 1 has been fully implemented.

The contiguous lookup block moved into `tools/prompt_workflow_document_lookup.py`
with its behavior intact, the facade re-exports every moved name, and the four
characterization cases the step asks for are present. The writer's validation
record states the same verdict and I agree with it, so this check leaves those
rows unchanged.

##### What the reviewer verified in the moved code for step 1 docs_layout_hardening (exchange 1) (round 1)

I compared every moved function against the pre-extraction facade body:
`docs_dirs`, `docs_dirs_for_version`, `_is_supported_docs_dir`,
`_topic_docs_dirs`, `_slug_key`, `_doc_matches`, `_exact_doc_matches`,
`find_documents`, `resolve_document`, `find_matching_documents`, `most_recent`
and `select_document`. The only difference is the substitution the step
requires: `COLLECTION_SLUG_RE` becomes the lookup-owned `DIRECTORY_SLUG_RE`,
whose pattern `^[a-z0-9][a-z0-9_-]*$` is the same accepted language. Recognition
stays shape-only and `_topic_docs_dirs` keeps the old fallback, which is what
Steps 2 and 3 are for.

`VERSION_RE`, `COLLECTION_SLUG_RE`, `COLLECTION_ITEM_RE`, `DRAFT_PREFIX`,
collection parsing, Git-derived topic discovery and the body-marker readers stay
in the facade. The lookup module imports only `re`, `typing` and
`prompt_workflow_models`, never the facade or the collection validator.

##### The monkeypatch seams survive the extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

This is the part of a facade extraction that usually breaks, so I checked it
rather than accepting the report. Two suites replace selectors through the
facade attribute: `test_prompt_workflow_main.py` sets
`prompt_workflow.docs.resolve_document` and `test_prompt_workflow_steps.py` sets
`steps.docs.select_document`. Both callers read those attributes at call time
and both still import the facade, so both patches still intercept.

No suite patches `docs_dirs`, `docs_dirs_for_version`, `_topic_docs_dirs`,
`most_recent`, `find_matching_documents` or either matcher, which matters
because those names now resolve inside the lookup module's own globals and a
facade-attribute patch would no longer reach them. `relevant_drafts` and
`docs.git`, the two seams several suites do patch, stayed in the facade.

##### Architecture check for the extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

The split is adapter-level tooling, not a domain boundary: lookup reads
directory entries and file metadata, the facade keeps Git signals and document
bodies. The dependency runs one way, facade to lookup, with no back reference
and no import cycle. Vulture, radon, ty, pyright and ruff all pass on the result.
Every involved file is below the 650-line ceiling at 501, 274, 87 and 6.
Nothing needs to be addressed.

##### Performance check for the extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

No traversal, sort, comparison, body read or cache was added or removed. The
recursive `rglob` walk, the version-scoped candidate list, the sorted
`iterdir` order, the canonical-parent preference and the `most_recent` stat read
are the same calls in the same order. My independent full walk took 3m 32.4s
against the writer's 3m 58.6s, which is execution evidence rather than a
threshold. No performance issue needs to be addressed.

##### Unit test coverage check for the extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

The coverage gate's source is `tools` in `pyproject.toml`, so both changed
production modules are measured, and my own walk reported `cov=100` over 2,714
tests with no failures, warnings or xfails.

The four new cases characterize what the step names: exact ambiguity with both
competing paths in the diagnostic, canonical-parent preference over a newer
outside match, the ordinary and validation plan kinds staying distinct through
both entry points, and tie behavior where equal timestamps keep the first sorted
candidate and a newer subtopic then wins. The tie case is the one worth having,
because `max` returning its first maximal element is the behavior Step 3 must
preserve and nothing else pins it.

One property of these fixtures is worth recording for Step 3: the topic's draft
file is never created, only its parent directory, so they already exercise the
missing-draft path the settled design relies on. No unit-tested class is below
100%, and no staged file sits outside the coverage gate.

##### Feature integrity for the extraction for step 1 docs_layout_hardening (exchange 1) (round 1)

General resolution still fails closed on duplicates, workflow selection still
prefers the canonical parent and still admits `<slug>_<sub>` subtopics, the two
plan kinds stay separate, and the CLI, steps, open-questions and post-commit
consumers keep their existing import paths. Nothing regressed.

Validation plan effects:

#### Validation plan effects of this reviewer round for step 1 docs_layout_hardening (exchange 1) (round 1)

None. This reviewer wrote no row in
`docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md`.

Reviewer mode may write the reviewed step's rows, and here it did not need to.
The writer's Step 1 section already opens with the exact
`Yes. Step 1 has been fully implemented.` sentence, and its analysis,
architecture, performance, coverage and feature-integrity subsections match what
I found independently, including the coverage gate's `tools` scope, the
501, 274, 87 and 6 line counts, and the advisory-projection variance.

The document-level status line correctly stays at `No, it is not implemented.`,
because Steps 2 through 4 are still pending. No umbrella row applies: this is a
standalone effort and reviewer mode never completes one in any case.

The validation plan's staged content is therefore the writer's, unamended, and
the validation-state comparison confirms no tracked difference arose during
this round.

### Pre-repair mandatory checks and coverage for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Pre-repair validation evidence for the step 1 round for step 1 docs_layout_hardening (exchange 1) (round 1)

The validation state was captured before any assessment could mutate the
repository, and no repair followed, so this capture is also the state the round
was judged against.

The ordered `validation_path_set` was the five staged step paths, the validation
plan among them, followed by the known groundhog and coverage artifacts
`a.ghog.log`, `a.ghog.status`, `a.ghog.day.ok` and `.coverage`.

At capture time the index tree was
`d2dfc0c90e663997a08d28454fde63393f76a283`, matching the request's
`request_index_tree`, with five tracked files digested, four ignored artifacts
digested and no untracked file in the set.

The retained manifest carrying this evidence, the exchange identity, the step
and both index trees was written through the shared launcher before assessment
began, so a stopped round keeps its recovery evidence.

No pre-repair blob was recorded for any path, because no permitted repair path
was opened in this round and the reviewer authored no tracked change.

### Resolved validation set and sources for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Resolved validation set and what the reviewer could run for step 1 docs_layout_hardening (exchange 1) (round 1)

Three commands were resolved for this round. One ran and passed. Two could not
run in this environment, which is missing mandatory evidence rather than a pass.

| Command | Sources | Reviewer result |
| --- | --- | --- |
| `ghog day` | project, plan | Ran. `exit=0`, `fail=0 warn=0 xfail=0 cov=100`, 2,714 tests, 3m 32.4s. |
| `rg -n 'prompt_workflow_docs\|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py` | plan | Could not run. `rg` is not installed. |
| `rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py` | plan | Could not run. `rg` is not installed. |

##### Result of the walk this reviewer ran for step 1 docs_layout_hardening (exchange 1) (round 1)

The check phase passed ty, pyright, ruff, radon cyclomatic complexity, vulture
dead code, the `PYTHON_BIG_FILE_LINE_LIMIT=650` file-size gate, markdown-check
and ShellCheck. The affected phase passed with `exit=0`. The full phase reported
`fail=0 warn=0 xfail=0 cov=100 exit=0` across 2,714 tests.

This is an independent run finished at 19:51:44 +02:00, not a reading of the
writer's recorded walk.

##### Why the two inspections could not run for step 1 docs_layout_hardening (exchange 1) (round 1)

`rg` resolves in neither PowerShell nor Git Bash on this machine, and no
ripgrep binary exists under the usual install locations, the project venvs or
the plugin directories. Nothing in `senv.bat` puts one on `PATH`.

This is not specific to Step 1. Every earlier plan in this repository that
authored an `rg -n` completion command has the same gap: no validation plan
under `docs/` records having run one.

##### What the two inspections were meant to establish for step 1 docs_layout_hardening (exchange 1) (round 1)

Both conclusions hold. I verified them with an equivalent ripgrep-based search
rather than by reading alone:

- `tools/prompt_workflow_document_lookup.py` contains no match for
  `prompt_workflow_docs` and none for `COLLECTION_SLUG_RE`.
- `tools/prompt_workflow_docs.py` matches `prompt_workflow_document_lookup` at
  line 4 in its docstring and line 22 in its import.

So the step's substance is verified. What is missing is the named command's own
evidence, and the readiness floor asks for the command.

##### The project floor is satisfied for step 1 docs_layout_hardening (exchange 1) (round 1)

The repository declares no `.review-validation` file, so the project-sourced
mandatory floor is the built-in `ghog day` alone, and that one ran and passed.
The two unavailable commands entered the set from the plan's Step 1 completion
line. Re-resolving today yields the same project default, so there is no
resolver drift to report in either direction.

### Resolver drift and direction for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Resolver drift between the request set and the current resolver for step 1 docs_layout_hardening (exchange 1) (round 1)

No drift, in either direction.

The request's `resolved_validation_set` carries `ghog day` with sources
`project` and `plan`, plus the two plan-sourced `rg` inspections. Re-resolving
against the current repository gives the same result:

- The project source resolves to the built-in `("ghog day",)` default, because
  this repository declares no `.review-validation` file.
- The plan source is the consolidated Step 1 completion line, which still names
  the same `ghog day` walk and the same two `rg` inspections.

The union this reviewer ran is therefore the request set unchanged, and no
command appeared or disappeared between the request and the assessment.

Worth recording alongside the absent drift: because there is no
`.review-validation` declaration, the whole project-sourced floor for this
repository is the single `ghog day` walk. Everything else in the resolved set
arrives from plan text, which is why a plan's phrasing decides what the
readiness floor demands.

### Repository state around validation for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Repository state comparison across the reviewer round for step 1 docs_layout_hardening (exchange 1) (round 1)

Every boundary the reviewer is required to check came back clean.

##### Index tree identity for step 1 docs_layout_hardening (exchange 1) (round 1)

The request carried `request_index_tree`
`d2dfc0c90e663997a08d28454fde63393f76a283`. The live index tree matched it
exactly before assessment and matches it again after the walk, so no early
rejection applied and nothing this reviewer did changed the staged set.

##### Umbrella digest boundary for step 1 docs_layout_hardening (exchange 1) (round 1)

The request says `Umbrella draft: none` and the envelope carries
`umbrella_path: null`. The capture returned `{"applicable": false,
"digest": null}` and the comparison after the implementation-check result
returned `{"applicable": false, "changed": false}`. No umbrella is in scope and
none was touched.

##### Validation state boundary for step 1 docs_layout_hardening (exchange 1) (round 1)

The ordered `validation_path_set` held the five staged step paths, the
validation plan among them, and the four known groundhog and coverage artifacts.
The comparison returned `acceptable: true` with empty `tracked_paths` and empty
`untracked_paths`.

The only differences are the four ignored artifacts the walk rewrites,
`a.ghog.log`, `a.ghog.status`, `a.ghog.day.ok` and `.coverage`. Ignored
validation artifacts are acceptable, and no tracked validation side effect
appeared, so nothing had to be left unstaged or reported as a boundary finding.

##### Working tree observations for step 1 docs_layout_hardening (exchange 1) (round 1)

One untracked file sits beside the effort documents,
`docs/v0.12.0/review.code.v0.12.0.docs_layout_hardening.md`, which is this
exchange's own transcript. It is protocol-created tracked documentation that the
workflow commits later, it is not part of the staged step, and this reviewer
neither staged nor altered it.

### Repair inventory for step 1 docs_layout_hardening (exchange 1) (round 1)

Repairs made:

#### Repairs made by the reviewer in this round

- None. This reviewer authored no tracked change: no source edit, no test edit, no
- validation-plan row, and no `a.commit` amendment.
- Nothing needed one. The extraction is faithful, the characterization tests cover
- what the step asks for, the validation record already states the correct verdict
- with accurate supporting detail, and `a.commit` matches the staged set. The one
- blocking result is the availability of two resolved validation commands, which
- is not something a reviewer repairs inside the step.
- No pre-repair blob was recorded, because no permitted repair path was opened. No
- reviewer patch was staged, so no attribution call was needed. Staging is exactly
- what the writer published.

Paths staged:

#### Staged paths assessed in this round

- Five paths, all inside Step 1, all authored by the writer:
- - `tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py`
- - `tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py`
- - `tools/prompt_workflow_docs.py`
- - `tools/prompt_workflow_document_lookup.py`
- - `docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md`
- Each is named by the plan's Step 1 files-involved list, and nothing outside that
- list is staged. No boundary-crossing work was swept in, and no pre-existing
- unstaged or untracked writer work was added to the index.
- Resulting physical line counts are 501 for the facade, 274 for the lookup
- module, 87 for the new test file and 6 for its package initializer. All four are
- below the 650-line ceiling the check phase enforces. The facade and the lookup
- module exceed their advisory projections of about 440 and 270 because the
- compatibility exports are explicit; the plan states that exceeding a projection
- while staying at or below 650 is evidence to record rather than missing work,
- and the writer recorded it.

### Commit plan assessment for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Commit plan assessment for the staged step for step 1 docs_layout_hardening (exchange 1) (round 1)

`a.commit` is accurate and needs no amendment. This reviewer did not change it.

The independent rerun of `commit-plan-check.bat --format json` against the
received repository state returned `state: valid`, `ready: true`, an empty
`diagnostics` array and exit `0`. Its staged path list and its three ordered
groups match the result recorded in the request byte for byte.

| Position | Subject | Paths |
| --- | --- | --- |
| 1 | `test(workflow): characterize document lookup` | the new test package initializer and its TDD module |
| 2 | `refactor(workflow): extract document lookup` | the facade and the new lookup module |
| 3 | `docs(docs_layout_hardening): record step 1 validation` | the validation plan |

The ordering reads least to most dependent and the grouping is defensible on its
own terms. The characterization tests exercise the facade surface and pass
before the extraction, so group 1 standing ahead of group 2 is correct rather
than merely conventional. The facade and the lookup module belong in one group
because neither compiles against the other's absence. The validation record
describes the finished state, so it comes last.

Each subject uses a conventional type and scope and names what its group does.

A status `0` from this checker satisfies only the mechanical `a.commit` result
in the readiness floor. It says nothing about implementation completeness,
validation evidence or repair attribution, and it authorizes no commit.

### Findings and boundaries for step 1 docs_layout_hardening (exchange 1) (round 1)

Unresolved findings:

#### Unresolved findings after the reviewer round

- One finding, and it is the only reason this round is not a commit-ready
- recommendation.

##### Two resolved validation commands cannot run on this machine

- `rg` is not installed. It resolves in neither PowerShell nor Git Bash, and no
- ripgrep binary exists under the user program directories, the project venvs or
- the plugin directories; `senv.bat` puts none on `PATH`. So both of Step 1's
- completion inspections are unavailable:
- - `rg -n 'prompt_workflow_docs|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py`
- - `rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py`
- A resolved command that cannot run is missing mandatory evidence rather than a
- pass, and missing mandatory evidence blocks a commit-ready recommendation.

##### What this finding is not

- It is not a defect in the implementation. Both conclusions the commands were
- meant to reach are true, and I verified them with an equivalent ripgrep-based
- search: the lookup module contains no `prompt_workflow_docs` and no
- `COLLECTION_SLUG_RE` reference, and the facade imports the lookup module at
- line 22. The step's substance is sound.
- It is also not a Step 1 authoring slip in isolation. Steps 2, 3 and 4 each close
- with an `rg -n` completion command, and no validation plan under `docs/` records
- one ever having run, so the same result will recur at every remaining step of
- this effort unless the form changes.

##### What the requestor reported

- The round 1 assessment states "Static inspection found no facade or
- collection-regex dependency in lookup." That conclusion is correct, and it is
- reported without saying that the two named commands were not executed. The
- distinction matters for the evidence record: a conclusion reached by reading is
- not the same artifact as a command result, and the readiness floor is written
- against the command.

Boundary-crossing work:

#### Boundary-crossing work observed in this round

- None inside the staged step. Every staged path is named by the plan's Step 1
- files-involved list, nothing reaches another step or another requirement, and no
- change introduces a design decision the settled specification did not already
- make.
- Two observations sit at the edge of this step and are reported rather than
- acted on, because neither belongs to a reviewer and neither belongs to Step 1's
- staged scope.
- The `rg` availability finding spans the whole effort. Steps 2, 3 and 4 each close
- with an `rg -n` completion command, so the decision about that form reaches
- beyond this step. It is recorded as a finding and left to the writer, since
- changing three later steps of a consolidated plan is not a bounded in-step
- repair.
- The untracked transcript `docs/v0.12.0/review.code.v0.12.0.docs_layout_hardening.md`
- is this exchange's own record. It is protocol-created tracked documentation
- that the workflow commits on its own schedule, so it stays untracked and
- unstaged here. Sweeping it into the index would be exactly the pre-existing
- work a reviewer must never stage.

### Writer instructions for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Writer instructions for the next step 1 round for step 1 docs_layout_hardening (exchange 1) (round 1)

Do not change the implementation. The extraction, the characterization tests,
the validation record and `a.commit` are all correct, and nothing in the staged
code needs rework. Leave the five staged paths as they are.

One thing needs settling, and it decides every remaining step of this effort.

1. Make the Step 1 completion inspections runnable, or stop expressing them as
   commands. Either install ripgrep so `rg` resolves for the reviewer, or
   restate the two checks in a form this environment can execute. The
   repository already ships Python and the `check.bat` and `ghog` launchers,
   and `Select-String` is available in PowerShell.
2. Apply the same decision to Steps 2, 3 and 4. Each closes with an `rg -n`
   completion command, so whatever form Step 1 adopts should be the form they
   adopt, rather than leaving three more rounds to rediscover this.
3. If the inspection is meant as a reading rather than a gate, say so in the
   step. Prose in the completion criteria is not resolved into the mandatory
   validation set; a command line is. That alone would close the finding without
   installing anything.
4. Record in the round 2 assessment which commands actually ran. The current
   assessment reports the inspection conclusion without noting that the named
   commands were not executed; the conclusion is right, but the evidence record
   should distinguish a command result from a reading.

Consider whether a `.review-validation` declaration belongs in this repository
while you are there. Without one the project floor is the built-in `ghog day`,
which is what actually gates this work; declaring it would make the floor
explicit rather than implied. That is a suggestion, not a requested change.

The commit choice stays with the human at the convergence gate, and this answer
recommends nothing about committing.

### Decision rationale for step 1 docs_layout_hardening (exchange 1) (round 1)

#### Decision rationale for the step 1 disposition for step 1 docs_layout_hardening (exchange 1) (round 1)

This round publishes `changes-requested` on one result of the readiness floor,
not on the work.

##### The six readiness results for step 1 docs_layout_hardening (exchange 1) (round 1)

| Result | Outcome |
| --- | --- |
| Exact identity | Pass. Envelope, human-readable request, plan, step, round and index tree all agree. |
| Complete implementation | Pass. Step 1 is fully implemented and the validation record's Yes verdict is correct. |
| Mandatory validation and coverage | Blocked. `ghog day` ran and passed with `cov=100`; two resolved commands could not run. |
| Attributable staged scope | Pass. Five staged paths, all named by the step, none swept in, no reviewer patch. |
| Unresolved findings | Blocked by the same single finding. |
| `a.commit` accuracy | Pass. Independent rerun returned `state: valid`, `ready: true`, exit `0`. |

Four pass, and the two that do not are the same fact seen twice.

##### Why a correct step still does not reach commit-ready for step 1 docs_layout_hardening (exchange 1) (round 1)

The rule is explicit: a resolved validation command that cannot run is missing
mandatory evidence, never a pass, and unavailable evidence blocks a commit-ready
recommendation. Two of the three resolved commands cannot run here because `rg`
is not installed.

I could have called the evidence satisfied on the grounds that I verified both
conclusions by other means. That would be the wrong call twice over: it would
quietly convert a reading into a command result in the durable record, and it
would leave the same gap waiting at Steps 2, 3 and 4, which all close the same
way. Catching it once at Step 1 costs one short round; catching it at Step 4
costs the same round four times.

##### What this answer is not saying for step 1 docs_layout_hardening (exchange 1) (round 1)

It is not saying the code is wrong. The extraction is faithful to the
pre-extraction bodies, the monkeypatch seams the plan worried about all survive,
the new tests characterize the behaviors Steps 2 and 3 will change, and my own
full walk passed every check with 2,714 tests and complete coverage. If the
validation form is settled, I expect the next round to be commit-ready.

This round made no substantive repair and no repair of any kind, so nothing
here prevents the next round from reaching the convergence gate. A commit-ready
recommendation, when it comes, remains advisory and will not authorize a commit.

### Final reviewer decision for step 1 docs_layout_hardening (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-09-12T20:00:23+02:00
- Exchange: code/code/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: request

### Review identity for step 1 docs_layout_hardening (round 2)

Umbrella draft: none
Implementation plan: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 docs_layout_hardening (round 2)

request_index_tree: d2dfc0c90e663997a08d28454fde63393f76a283
resolved_validation_set:

- ghog day (sources: project, plan)
- rg -n 'prompt_workflow_docs|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py (sources: plan)
- rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py (sources: plan)

commit_plan_result:

```text
state: valid
ready: true
group 1: test(workflow): characterize document lookup
group 1 path: tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
group 1 path: tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
group 2: refactor(workflow): extract document lookup
group 2 path: tools/prompt_workflow_docs.py
group 2 path: tools/prompt_workflow_document_lookup.py
group 3: docs(docs_layout_hardening): record step 1 validation
group 3 path: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md
staged path: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md
staged path: tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
staged path: tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
staged path: tools/prompt_workflow_docs.py
staged path: tools/prompt_workflow_document_lookup.py
```

### Requestor assessment for step 1 docs_layout_hardening (round 2)

Step 1 remains fully implemented, with the same five staged paths and the same
valid three-group a.commit. The round 1 reviewer independently agreed with the
implementation, architecture, performance, feature integrity, validation record,
coverage and grouping, made no repairs, and ran all 2,714 tests with cov=100
and no failures, warnings or xfails. Their walk ended at 19:51:44 +02:00.

The only blocker was that rg did not resolve in the reviewer's shell. It is
available here as ripgrep 15.2.0, from the Codex standalone distribution.
The original round 1 writer did execute both named commands, and this session
has executed them again after the answer:

- rg -n 'prompt_workflow_docs|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py
  returned exit 1 with empty output, the required absence of dependencies.
- rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py
  returned exit 0 with the docstring reference at line 4 and import at line 22.

The verified .reviews/a.code-docs-layout-step1-r2.rg-checks.ps1 helper exposes
that existing executable to a child PowerShell process, runs both exact rg
commands and checks those expected exit codes. Running it returned exit 0.
It neither installs software nor changes persistent environment configuration.
It is ignored review support material, not an implementation change.

The writer's groundhog evidence remains the successful walk ending at
19:33:26 +02:00; no new code or test changes require another writer walk.
The reviewer independently ran a later successful walk. No validation gate
was removed, replaced by prose or weakened.

### Implementation report for step 1 docs_layout_hardening (round 2)

Extracted docs_dirs through select_document and associated filename/layout
constants from tools/prompt_workflow_docs.py into
tools/prompt_workflow_document_lookup.py. Lookup depends on standard-library
modules and workflow models, never the docs facade or collection validator.

The facade explicitly re-exports all lookup names and retains VERSION_RE,
Git-derived topic discovery, collection parsing and body-marker readers.
Explicit __all__ lists preserve the supported import surface under the
repository's lint and type-checking policies. The lookup directory-slug
expression has the same accepted language as COLLECTION_SLUG_RE.

The new unit-test package supplies four cases using real temporary files.
They check ambiguity path diagnostics, canonical-parent preference over a newer
external match, plan versus validation-plan lookup, separator folding,
subtopic matching, equal timestamp ordering and later timestamp changes.
The old shape-only effort recognition and fallback remain for Steps 2 and 3.

### Change summary for step 1 docs_layout_hardening (round 2)

Five staged paths are covered by the mechanically valid root a.commit:

1. test(workflow): characterize document lookup
   - tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py
   - tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py
2. refactor(workflow): extract document lookup
   - tools/prompt_workflow_docs.py
   - tools/prompt_workflow_document_lookup.py
3. docs(docs_layout_hardening): record step 1 validation
   - docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md

The characterization tests use the pre-existing facade and can precede the
extraction. The completed validation record is the final documentation group.
No caller imports or unrelated files were changed.

### Writer response for step 1 docs_layout_hardening (round 2)

Writer response:

Accepted: the reviewer needs executable command evidence from their own shell.
The environment bridge is prepared and verified. Both named inspections stay
in the resolved validation set, and the same process-local PATH setup makes
the remaining plan steps' rg commands available as well.

Explicit disagreement: the statements that ripgrep is not installed on this
machine and that the writer did not execute the named commands are incorrect.
Get-Command rg locates rg.exe in the Codex standalone release's codex-path
directory. Both commands ran before the first request and ran again after the
answer, with exit 1/no matches for the dependency-absence check and exit 0/two
matches for the facade check. The difference is shell PATH visibility.

To run the exact two checks with the executable now located, from the
repository root execute:

```powershell
powershell -ExecutionPolicy Bypass -File .reviews/a.code-docs-layout-step1-r2.rg-checks.ps1
```

The helper adds the existing codex-path directory to PATH inside its child
process, runs rg --version, then executes both unchanged plan commands.
Exit 1 is the expected ripgrep no-match outcome for the first command;
exit 2 or any other unexpected result is rejected, not treated as success.

No repair was reversed because the reviewer made none. No production source,
test, validation row, plan, grouping or subject changed after round 1.
The reviewer's independent assessment supports retaining the completed Step 1
record. No .review-validation declaration is added: the suggestion is optional,
and the current project floor remains mandatory and explicit in this request.

### Reviewer focus for step 1 docs_layout_hardening (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-09-12T20:13:52+02:00
- Exchange: code/code/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 docs_layout_hardening (exchange 1) (round 2)

Baseline index tree: d2dfc0c90e663997a08d28454fde63393f76a283

Assessed index tree: d2dfc0c90e663997a08d28454fde63393f76a283

### Implementation check for step 1 docs_layout_hardening (exchange 1) (round 2)

Result:

#### Reviewer implementation check for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

Yes. Step 1 has been fully implemented.

Nothing changed between rounds. The index tree is the same
`d2dfc0c90e663997a08d28454fde63393f76a283`, the same five paths are staged with
the same digests, and no source, test or validation-plan byte differs from what
round 1 assessed and agreed with.

##### What the round 1 check established and this round re-confirms for step 1 docs_layout_hardening (exchange 1) (round 2)

Every moved function matches its pre-extraction body: `docs_dirs`,
`docs_dirs_for_version`, `_is_supported_docs_dir`, `_topic_docs_dirs`,
`_slug_key`, `_doc_matches`, `_exact_doc_matches`, `find_documents`,
`resolve_document`, `find_matching_documents`, `most_recent` and
`select_document`. The single intended difference is the lookup-owned
`DIRECTORY_SLUG_RE`, whose `^[a-z0-9][a-z0-9_-]*$` is the same accepted language
as the collection expression it replaces. Shape-only recognition and the old
fallback stay in place for Steps 2 and 3.

The two inspections that could not run in the previous round have now run and
confirm both boundaries: no facade or collection-regex reference inside the
lookup module, and the facade importing the lookup module.

##### Architecture check for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

One-way dependency, facade to lookup, with no cycle and no back reference. The
lookup module imports `re`, `typing` and the workflow models only. Git signals,
collection parsing and document-body readers stay in the facade. This is a
tooling adapter split rather than a domain boundary, and it introduces no layer
violation. All four files sit below the 650-line ceiling at 501, 274, 87 and 6.
Nothing needs to be addressed.

##### Performance check for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

No traversal, sort, comparison, body read or cache was added or removed; the
recursive walk, version-scoped candidate list, sorted entry order,
canonical-parent preference and single `stat` per candidate are unchanged calls
in unchanged order. This round's full phase took 4m 08.7s against the previous
3m 32.4s, which is run-to-run variance on the same tree rather than a threshold
or a regression. No performance issue needs to be addressed.

##### Unit test coverage check for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

The coverage gate's source is `tools` in `pyproject.toml`, so both changed
production modules are measured, and this round's walk reported `cov=100` across
2,714 tests with no failure, warning or xfail.

The four characterization cases still cover what the step names: exact ambiguity
carrying both competing paths in its diagnostic, canonical-parent preference
over a newer outside match, the ordinary and validation plan kinds staying
distinct through both entry points, and the tie rule where equal timestamps keep
the first sorted candidate until a newer subtopic wins. That tie case is the one
Step 3 will need, because nothing else pins `max` returning its first maximal
element.

No unit-tested class is below 100%, and no staged file sits outside the coverage
gate.

##### Feature integrity for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

General resolution still fails closed on duplicates, workflow selection still
prefers the canonical parent and still admits `<slug>_<sub>` subtopics, the two
plan kinds stay separate, and the CLI, steps, open-questions and post-commit
consumers keep their existing import paths. The two selector monkeypatch seams
still intercept, because both callers read facade attributes at call time.
Nothing regressed.

Validation plan effects:

#### Validation plan effects of the round 2 reviewer round for step 1 docs_layout_hardening (exchange 1) (round 2)

None. This reviewer wrote no row in
`docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md`, in this round
or the previous one.

The writer's Step 1 section already opens with the exact
`Yes. Step 1 has been fully implemented.` sentence, and its analysis,
architecture, performance, coverage and feature-integrity subsections match what
I verified independently. The document-level status line correctly stays at
`No, it is not implemented.`, because Steps 2 through 4 are pending. No umbrella
row applies: this is a standalone effort, and reviewer mode never completes one.

The validation-state comparison confirms no tracked difference arose during this
round, so the staged validation plan is the writer's content unamended.

### Pre-repair mandatory checks and coverage for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Pre-repair validation evidence for the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

Captured before assessment could mutate anything, and no repair followed, so
this capture is also the state the round was judged against.

The ordered `validation_path_set` was the five staged step paths, the validation
plan among them, followed by the known groundhog and coverage artifacts
`a.ghog.log`, `a.ghog.status`, `a.ghog.day.ok` and `.coverage`.

At capture time the index tree was
`d2dfc0c90e663997a08d28454fde63393f76a283`, matching the request's
`request_index_tree`, with five tracked files digested, four ignored artifacts
digested and no untracked file in the set. The five tracked digests are the same
ones round 1 captured, which is how this round establishes that the staged work
did not move between rounds.

A fresh retained manifest was written through the shared launcher before
assessment began; the round 1 manifest was retired after that round published.

No pre-repair blob was recorded, because no permitted repair path was opened and
this reviewer authored no tracked change.

### Resolved validation set and sources for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Resolved validation set executed in the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

All three resolved commands ran in this reviewer's own shell this round. The
readiness floor's validation result is complete.

| Command | Sources | Reviewer result |
| --- | --- | --- |
| `ghog day` | project, plan | Ran. `exit=0`, `fail=0 warn=0 xfail=0 cov=100`, 2,714 tests, 4m 08.7s, ended 20:08:44 +02:00. |
| `rg -n 'prompt_workflow_docs\|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py` | plan | Ran. `exit=1`, no matches, which is the required absence. |
| `rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py` | plan | Ran. `exit=0`, matches at lines 4 and 22. |

##### How the two inspections were executed for step 1 docs_layout_hardening (exchange 1) (round 2)

Ripgrep 15.2.0 resolved from the Codex standalone release's `codex-path`
directory once that directory was prepended to a process-local `PATH`. I ran
both commands exactly as the plan writes them, then ran the writer's
`.reviews/a.code-docs-layout-step1-r2.rg-checks.ps1` helper as they asked. The
helper reported `exit=1, no matches as required` for the absence check and
`exit=0` for the facade check, and returned `exit 0` overall.

I read the helper before running it. It resolves the existing executable, checks
it is there, prepends its directory to `$env:PATH` inside its own process, runs
the two commands, asserts exit `1` and exit `0`, and exits. It installs nothing,
writes nothing and changes no persistent configuration.

##### What the two results establish for step 1 docs_layout_hardening (exchange 1) (round 2)

`tools/prompt_workflow_document_lookup.py` has no reference to the docs facade
and none to `COLLECTION_SLUG_RE`, so the extracted module carries neither the
dependency the step forbids nor the collection coupling this effort exists to
break. `tools/prompt_workflow_docs.py` references the lookup module at line 4 in
its docstring and line 22 in its import, so the facade is the re-export point
the step requires.

##### The walk this reviewer ran in this round for step 1 docs_layout_hardening (exchange 1) (round 2)

The check phase passed ty, pyright, ruff, radon, vulture, the
`PYTHON_BIG_FILE_LINE_LIMIT=650` gate, markdown-check and ShellCheck. The
affected phase passed. The full phase reported `cov=100` with no failure,
warning or xfail across 2,714 tests.

This is a second independent walk against a byte-identical staged tree. The
index tree is the same `d2dfc0c90e663997a08d28454fde63393f76a283` the request
carries, so the walk re-establishes the same evidence under this round rather
than reusing the round 1 result.

### Resolver drift and direction for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Resolver drift observed in the round 2 assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

No drift, in either direction, and none between rounds.

The request's `resolved_validation_set` carries `ghog day` with sources
`project` and `plan`, plus the two plan-sourced `rg` inspections. That is the
same set round 1 carried, and re-resolving against the current repository
reproduces it:

- The project source resolves to the built-in `("ghog day",)` default, because
  this repository still declares no `.review-validation` file.
- The plan source is the consolidated Step 1 completion line, unchanged, which
  still names the same walk and the same two inspections.

The set did not shrink between rounds, which is the point worth recording. The
round 1 finding was closed by making the commands executable for the reviewer,
not by removing them, weakening them or restating them as prose. No validation
gate was dropped.

### Repository state around validation for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Repository state comparison across the round 2 round for step 1 docs_layout_hardening (exchange 1) (round 2)

Every boundary came back clean, and the staged work is provably the same one
round 1 assessed.

##### Index tree identity in round 2 for step 1 docs_layout_hardening (exchange 1) (round 2)

The request carries `request_index_tree`
`d2dfc0c90e663997a08d28454fde63393f76a283`, which is the value round 1 carried.
The live index tree matched it before assessment and matches it again after the
walk, so no early rejection applied, nothing moved between rounds, and nothing
this reviewer did changed the staged set.

##### Umbrella digest boundary in round 2 for step 1 docs_layout_hardening (exchange 1) (round 2)

The request says `Umbrella draft: none` and the envelope carries
`umbrella_path: null`. Capture returned `{"applicable": false, "digest": null}`
and the comparison after the implementation-check result returned
`{"applicable": false, "changed": false}`. No umbrella is in scope and none was
touched.

##### Validation state boundary in round 2 for step 1 docs_layout_hardening (exchange 1) (round 2)

The ordered `validation_path_set` held the five staged step paths, the
validation plan among them, and the four known groundhog and coverage
artifacts. The comparison returned `acceptable: true` with empty `tracked_paths`
and empty `untracked_paths`.

The only differences are the four ignored artifacts the walk rewrites,
`a.ghog.log`, `a.ghog.status`, `a.ghog.day.ok` and `.coverage`. Ignored
validation artifacts are acceptable. No tracked validation side effect appeared,
so nothing had to be left unstaged or reported as a boundary finding.

##### Working tree observations in round 2 for step 1 docs_layout_hardening (exchange 1) (round 2)

Two untracked items sit outside the staged set and were left untouched: this
exchange's transcript beside the effort documents, and the writer's ignored
`rg` bridge helper under the artifact home. Neither is staged, and a reviewer
never stages pre-existing work it did not author for the step.

### Repair inventory for step 1 docs_layout_hardening (exchange 1) (round 2)

Repairs made:

#### Repairs made by the reviewer in the round 2 round

- None. This reviewer authored no tracked change in this round: no source edit, no
- test edit, no validation-plan row, and no `a.commit` amendment. The same was
- true of round 1, so no reviewer-authored change exists anywhere in this
- exchange.
- Nothing needed one. The staged work is byte-identical to what round 1 assessed
- and agreed with, and the round 1 blocker was about evidence availability rather
- than about anything a reviewer edits inside the step.
- No pre-repair blob was recorded and no reviewer patch was staged, so no
- attribution call was needed. The index is exactly what the writer published.
- Because this round made no substantive repair, nothing prevents it from reaching
- the convergence gate.

Paths staged:

#### Staged paths assessed in the round 2 round

- The same five paths as round 1, with the same digests, all inside Step 1 and all
- authored by the writer:
- - `tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py`
- - `tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py`
- - `tools/prompt_workflow_docs.py`
- - `tools/prompt_workflow_document_lookup.py`
- - `docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.validation.md`
- Each is named by the plan's Step 1 files-involved list, nothing outside that
- list is staged, and no pre-existing unstaged or untracked work was swept in.
- Physical line counts remain 501 for the facade, 274 for the lookup module, 87
- for the new test file and 6 for its package initializer, all below the 650-line
- ceiling the check phase enforces. The facade and lookup module exceed their
- advisory projections of about 440 and 270 because the compatibility exports are
- explicit, which the plan classifies as evidence to record rather than missing
- work, and the writer recorded it.

### Commit plan assessment for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Commit plan assessment for the round 2 round for step 1 docs_layout_hardening (exchange 1) (round 2)

`a.commit` is accurate and needs no amendment. This reviewer did not change it,
in this round or the previous one.

The independent rerun of `commit-plan-check.bat --format json` against the
received repository state returned `state: valid`, `ready: true`, an empty
`diagnostics` array and exit `0`. Its staged path list and three ordered groups
match the result recorded in the request and match the round 1 rerun.

| Position | Subject | Paths |
| --- | --- | --- |
| 1 | `test(workflow): characterize document lookup` | the new test package initializer and its TDD module |
| 2 | `refactor(workflow): extract document lookup` | the facade and the new lookup module |
| 3 | `docs(docs_layout_hardening): record step 1 validation` | the validation plan |

The ordering runs least to most dependent. The characterization tests exercise
the facade surface and pass before the extraction, so group 1 ahead of group 2
is correct rather than conventional. The facade and the lookup module belong
together because neither works without the other. The validation record
describes the finished state, so it comes last. Each subject uses a conventional
type and scope and names what its group does.

A status `0` satisfies only the mechanical `a.commit` result in the readiness
floor. It proves nothing about implementation completeness, validation evidence
or repair attribution, and it authorizes no commit.

### Findings and boundaries for step 1 docs_layout_hardening (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Writer instructions at the step 1 convergence gate for step 1 docs_layout_hardening (exchange 1) (round 2)

No change is requested. The staged work is correct, the evidence is complete,
and `a.commit` is accurate.

1. Present the advisory commit-ready recommendation and the two registered
   labels to the human, and make no further edit before that choice.
2. Keep the `rg` bridge available for Steps 2, 3 and 4. Each closes with an
   `rg -n` completion command, and the same process-local `PATH` setup is what
   lets a reviewer execute them. Nothing else needs to change about those steps.
3. Leave the five staged paths exactly as they are. This reviewer authored no
   tracked change in either round, so the index is entirely the writer's.

Consider declaring a `.review-validation` file at some point. Without one the
project-sourced floor is the built-in `ghog day`, and every other mandatory
command arrives from plan text. Making the floor explicit would put it where a
reader looks for it rather than leaving it implied. That is a suggestion for
later, not a requested change, and it does not belong inside this step.

This recommendation is advisory and authorizes nothing. The commit choice, and
the labels offered for it, belong to the human at the convergence gate. Do not
commit on the strength of this answer.

### Decision rationale for step 1 docs_layout_hardening (exchange 1) (round 2)

#### Decision rationale for the step 1 round 2 disposition for step 1 docs_layout_hardening (exchange 1) (round 2)

This round publishes an advisory `commit-ready` recommendation. Every result in
the readiness floor now passes, no finding is carried or open, and this round
made no repair of any kind.

##### The six readiness results in round 2 for step 1 docs_layout_hardening (exchange 1) (round 2)

| Result | Outcome |
| --- | --- |
| Exact identity | Pass. Envelope, human-readable request, plan, step, round, occurrence and index tree all agree. |
| Complete implementation | Pass. Step 1 is fully implemented and the validation record's Yes verdict is correct. |
| Mandatory validation and coverage | Pass. All three resolved commands ran this round; the walk reported `cov=100` over 2,714 tests. |
| Attributable staged scope | Pass. Five staged paths, all named by the step, none swept in, no reviewer patch in either round. |
| Unresolved findings | Pass. The single round 1 finding is closed and none replaced it. |
| `a.commit` accuracy | Pass. Independent rerun returned `state: valid`, `ready: true`, exit `0`. |

##### What changed since round 1 for step 1 docs_layout_hardening (exchange 1) (round 2)

Only the evidence, not the code. The index tree is the same
`d2dfc0c90e663997a08d28454fde63393f76a283` and the five staged digests are
unchanged, so the implementation this round recommends is the one round 1
already agreed with on every substantive point.

Round 1 blocked because two resolved validation commands could not run in this
reviewer's shell. They ran this round, exactly as the plan writes them: exit `1`
with no matches for the dependency-absence inspection, and exit `0` with matches
at lines 4 and 22 for the facade inspection.

##### Corrections this reviewer owes from round 1 for step 1 docs_layout_hardening (exchange 1) (round 2)

The writer disagreed with two statements in the round 1 answer and is right on
both.

Ripgrep is installed on this machine. It ships inside the Codex standalone
release directory, and `rg.exe` exists under
`~/.codex/packages/standalone/releases/<release>/codex-path/` for several
releases including `0.154.0`. Round 1 checked `PATH` in both shells, the user
program directories, the project venvs and `Program Files`, found nothing, and
wrote "not installed" when the accurate statement was "does not resolve in
either of this reviewer's shells". That was a PATH visibility difference rather
than a missing tool.

The round 1 answer also observed that the requestor had reported the inspection
conclusion without saying the commands had not been executed. The writer had
executed them, so that observation does not apply and is withdrawn with the
first. What survives from round 1 is the narrower point, now satisfied: the
reviewer needs the command evidence from its own shell, and it has it.

##### The bridge this reviewer verified before using for step 1 docs_layout_hardening (exchange 1) (round 2)

I read `.reviews/a.code-docs-layout-step1-r2.rg-checks.ps1` before running it.
It resolves the existing executable, checks it is present, prepends its
directory to `$env:PATH` inside its own process, runs the two commands, asserts
their expected exit codes and exits. It installs nothing, writes nothing and
changes no persistent configuration. Running it returned `exit 0` with both
expected results.

The important property of that fix is what it did not do. The two commands are
still in the resolved validation set, still worded exactly as the plan writes
them, still asserting their exit codes. The blocker closed by making the
evidence obtainable rather than by lowering the floor, which is the difference
between a gate satisfied and a gate quietly removed.

One note for the remaining steps, as information rather than a request: the
executable lives inside the Codex runtime's bundled `codex-path`, so it resolves
for a Codex-hosted process and for anything sourcing the same bridge, not for an
arbitrary shell. Steps 2, 3 and 4 each close with an `rg -n` command and will
need the same bridge, which the writer has already said the setup covers.

##### What this recommendation is and is not for step 1 docs_layout_hardening (exchange 1) (round 2)

It is advisory. It does not authorize a commit and it is not a commit. The
choice belongs to the human at the convergence gate, along with the option of
another round.

It rests on evidence this reviewer produced in its own shell: two full groundhog
walks across the two rounds, both green with complete coverage, both resolved
inspections executed as written, two independent `commit-plan-check` reruns, and
clean umbrella and validation-state boundaries with no tracked side effect in
either round.

### Final reviewer decision for step 1 docs_layout_hardening (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-09-12T20:44:27+02:00
- Exchange: code/code/v0.12.0/docs_layout_hardening
- Umbrella: none
- Reviewed document: docs/v0.12.0/plan.v0.12.0.docs_layout_hardening.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->
