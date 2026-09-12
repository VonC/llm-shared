# v0.12.0 docs_layout_hardening implementation plan

Implement content-based effort recognition and canonical-parent selection in
four independently verifiable steps.

## Plan goal and scope for v0.12.0 docs_layout_hardening

Implement the settled [issue](issue.v0.12.0.docs_layout_hardening.md) and
[design](design.v0.12.0.docs_layout_hardening.md), beside the
[canonical draft](draft.v0.12.0.docs_layout_hardening.md). All effort documents
remain in `docs/v0.12.0/`; this is a standalone effort without an umbrella.

1. Extract document lookup without changing behavior or caller imports.
2. Share content-based eligibility across both directory listings.
3. Implement scoped candidate discovery and fallback selection.
4. Verify CLI and post-commit acceptance, then document the shipped contract.

Preserve exact general resolution, workflow role/subtopic matching, existing
layout spellings, local timestamp ties, missing-draft post-commit topics and the
optional-slug interface. Do not introduce migration, indexing, caching, retry
machinery, new layout choices or changes to unrelated review-resume behavior.

## Confirmed code and test facts for v0.12.0 planning

`prompt_workflow_docs.py` owns Git-derived topic discovery, collection parsing,
layout enumeration, document lookup and settled-marker inspection. The lookup
block can depend on `prompt_workflow_models.py` and the standard library without
importing the docs facade or any caller. Keep topic/collection/marker work in
the facade. `COLLECTION_SLUG_RE` remains owned by collection validation.

The CLI imports `docs.DOCUMENT_TYPES`; `open_questions_md.py` imports
`docs_dirs` from the facade; post-commit discovery uses `docs.VERSION_RE`,
`docs.docs_dirs` and `docs.select_document`. Preserve these names and all public
lookup signatures through explicit re-exports. Existing tests also exercise
`docs._doc_matches`, `docs._exact_doc_matches` and `docs.most_recent`; retain
those access paths.
Two suites patch selectors through facade attributes: the main suite replaces
`prompt_workflow.docs.resolve_document`, and the steps suite replaces
`steps.docs.select_document`. Both callers read these attributes at call time.
Keep module-level re-exported names and keep callers importing the facade;
switching callers to the lookup module would bypass these patches.

Three existing docs-suite cases require Step 2 fixture repairs.
`test_docs_dirs_supports_all_layouts` and
`test_docs_dirs_includes_version_slug_layout` create empty slug directories
and expect recognition. `test_resolve_document_uses_only_version_slug_and_type`
includes `docs/v9.8.0/topic` with only
`plan.v9.8.0.git-history-report.md`, so its directory and document slugs disagree.

Two existing docs selection cases use `_ISO` with `draft_path=Path("d.md")`:
`test_find_matching_documents_per_role` and
`test_most_recent_and_select_document`. That topic's parent resolves against the
process working directory, outside the temporary root's recognized directories. Step 3
must give these valid-selection fixtures draft paths under `tmp_path / "docs"`.
A topic sent through real candidate discovery against a temporary root needs
a recognized parent under that root, unless the test expects invalid-parent
failure. Relative topics also appear in the main, plan, models and steps suites;
their stubbed-selector, constructed-state or field-only tests need no blanket
rewrite, but any reuse through real discovery must follow this fixture rule.

Other large suites remain regression inputs; new cases belong in the dedicated
packages below. Hypothesis is already
configured. The tools and parent test packages already contain `__init__.py`
and need no registration change for these modules.

Physical line counts, including blank lines, were measured at `9f39af3`.
`check.bat` counts physical lines and `senv.bat` sets its limit to 650.
The same ceiling applies to each new Python file. There is no involved file
above the ceiling at this baseline.

| Existing path | Lines | Policy band and planned treatment |
| --- | --- | --- |
| `tools/prompt_workflow_docs.py` | 650 | At risk; extract lookup before adding behavior. |
| `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` | 611 | At risk; repair three recognition fixtures in Step 2 and two selection fixtures in Step 3. |
| `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_document_lookup_tdd.py` | 59 | Safe; retain as regression input. |
| `tools/prompt_workflow_post_commit.py` | 91 | Safe; update its caller-contract docstring in Step 4. |
| `tools/prompt_workflow_models.py` | 149 | Safe; inspected dependency, no planned edit. |
| `tools/prompt_workflow_steps.py` | 266 | Safe; inspected caller, no planned edit. |
| `tools/prompt_workflow_skill_continuation.py` | 138 | Safe; inspected caller, no planned edit. |
| `tools/prompt_workflow.py` | 618 | At risk; use existing CLI handling without growth. |
| `tools/open_questions_md.py` | 414 | Safe; retain facade import. |
| `tools/new_draft_workflow.py` | 467 | Safe; retain optional-slug behavior. |
| `tests/unit/tools/test_prompt_workflow_skill/test_prompt_workflow_skill_tdd.py` | 650 | At risk; add post-commit cases to the new acceptance package. |
| `tests/unit/tools/test_prompt_workflow_acceptance/test_prompt_workflow_acceptance_tdd.py` | 585 | At risk; retain as regression input. |
| `tests/unit/tools/test_prompt_workflow_main.py` | 614 | At risk; retain as regression input. |
| `tests/unit/tools/test_prompt_workflow_integration.py` | 164 | Safe; retain as regression input. |
| `tests/unit/tools/test_prompt_workflow_steps.py` | 231 | Safe; retain as regression input. |
| `tests/unit/tools/test_prompt_workflow_plan.py` | 329 | Safe; relative-topic audit, no planned edit. |
| `tests/unit/tools/test_prompt_workflow_models.py` | 64 | Safe; field-only relative-topic fixture, no planned edit. |
| `tests/unit/tools/test_open_questions_md.py` | 520 | Safe; retain as regression input. |
| `tests/unit/tools/test_new_draft_workflow.py` | 308 | Safe; retain as regression input. |
| `tools/__init__.py` | 93 | Safe; no planned edit. |
| `tests/unit/tools/__init__.py` | 6 | Safe; no planned edit. |
| `tests/unit/tools/test_prompt_workflow_docs/__init__.py` | 7 | Safe; no planned edit. |
| `rules/docs_layout.md` | 43 | Markdown; update shipped discovery guidance in Step 4. |

Every new file listed in the steps has a baseline of zero. Projected counts
are advisory. Exceeding a projection while staying at or below 650 is evidence
to record, not missing work. If an unforeseen caller fix would grow a file past
650, extract its relevant CLI/routing or test-scenario responsibility first;
do not widen this plan by reorganizing unrelated code preemptively.

## File-based IO cost clarification for v0.12.0 planning

Recognition reads current immediate filenames and uses existing file-type
checks; it does not read document bodies. General discovery retains its current
recursive enumeration and ordering. Version-scoped discovery retains its narrow
enumeration. Qualification stops at the first exact qualifying filename and
does not recurse into a child to find evidence.

Candidate discovery inventories recognized directories once per invocation,
then scans local entries before other directories. Local success avoids fallback
document matching, although building the recognized set can already inspect
other effort directories. The selector consumes the scoped result directly;
there is no second discovery pass merely to recover scope.

Uncached calls may repeat filesystem reads. Existing downstream document-body
reads and modification-time reads remain. No index, constant-time lookup,
atomic snapshot or wall-clock latency promise is part of the accepted design.

## Complexity and timing clarification for v0.12.0 planning

Retain existing sort costs for directory and matching-file order. For each
candidate effort directory with E immediate entries, qualification examines at
most E entries and six fixed document kinds, in addition to existing enumeration
work. Directory trees and filenames are not assumed to have constant size.
Do not add nested all-candidate comparisons, duplicate scope discovery or retries.

No Step 0 or timeout/xfail gate is warranted: the settled contract specifies
freshness and allowed IO, not a quantitative speed target. Use deterministic
access guards and call-count assertions tied to those contracts, plus the
normal groundhog full-run duration check. No timing baseline has been measured
or acceptance test executed while writing this plan.

## Shared execution command checklist for every implementation step

1. Count physical lines before editing every step file, including its tests and
   package initializers. Missing files start at zero.
2. Write or adjust the step's observable regression cases first, then implement
   the step. Preserve independent expected results rather than duplicating the
   predicate in a test oracle.
3. Run the step's `rg` inspection and the shared `ghog day` walk. Its affected
   phase supplies targeted testing and its full phase covers existing callers.
   Use focused groundhog commands only in the failure branch it prescribes.
4. Fix the named failure and repeat the authorized walk until check, affected
   tests, full coverage and duration policy reach the objective together.
5. Recount files. Apply the 650-line ceiling and responsibility split guidance;
   record advisory-estimate variance without failing an otherwise compliant step.
6. Record actual implementation and validation evidence in the matching
   [validation step](plan.v0.12.0.docs_layout_hardening.validation.md). Keep its
   numbered steps aligned if plan review changes this sequence.

## Ready-to-run commands shared by all four steps

Read [run commands](../../rules/run_commands.md) and the current
[groundhog lifecycle](../../instructions/groundhog.md) before execution.
Resolve the absolute shared checkout from that instruction path; substitute it
for `<LLM_SHARED_DIR>` below. Do not persist machine-specific paths in this plan.

Count each step's actual paths before and after with PowerShell:

```powershell
$stepPaths = @('tools/prompt_workflow_docs.py') # Replace with every step file.
$stepPaths | ForEach-Object {
    $lineCount = if (Test-Path -LiteralPath $_) {
        @(Get-Content -LiteralPath $_).Count
    } else { 0 }
    '{0}: {1}' -f $_, $lineCount
}
```

The shared gate is one walk, not a separately assembled check/test sequence:

```powershell
New-Item a.ghog.started -Force | Out-Null
$stepStarted = (Get-Item a.ghog.started).LastWriteTime
cmd /d /c "<LLM_SHARED_DIR>\bin\ghog.bat day > a.ghog.log 2>&1"
$stepExit = $LASTEXITCODE
$stepFresh = (Test-Path a.ghog.log) -and (Get-Item a.ghog.log).LastWriteTime -gt $stepStarted
Remove-Item -LiteralPath a.ghog.started -Force
if (-not $stepFresh) { throw 'Groundhog log was not refreshed; diagnose invocation.' }
"exit=$stepExit"
```

Branch on the exit code before reading the last five log lines on success or
last 100 on failure. Follow the groundhog failure branch for focused
`ghog affected` or `ghog single <step-test-files>` verification; each stands for
the same resolved launcher and redirected log contract. Never run tests or
checks directly. A live walk is waited on through `ghog status`, without
duplicating it. Use the documented detached lifecycle if the harness requires
it. A step completes only with a fresh `ghog day` objective after the last edit.

## Numbered implementation steps for v0.12.0 docs_layout_hardening

### Step 1. Extract the document lookup responsibility

#### Step 1 analysis and intent

The docs module has no line-budget headroom for either behavioral change.
Move its contiguous layout/matching/selection responsibility and associated
constants into one lower-level module, retaining the existing facade. This is
a behavior-preserving prerequisite to design Q01 and Q03, not a new lookup
policy. It preserves caller imports, enumeration order, matching and IO cost.
Apply the shared execution checklist and ready-to-run commands above.

#### Step 1 implementation

Files involved:

- `tools/prompt_workflow_docs.py` (existing, to be updated).
- `tools/prompt_workflow_document_lookup.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_document_lookup/__init__.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py` (new, to be created).

Tests first: characterize the facade with temporary files for general exact
ambiguity, workflow local preference, ordinary/validation plan distinction and
timestamp ties. Retain the existing docs and lookup regression suites. These
tests assert outputs and errors rather than the physical import arrangement.

Move `docs_dirs` through `select_document` and their filename/layout constants
as a cohesive block. Re-export the public selectors, `DOCUMENT_TYPES`, shared
constants used by retained code, `_slug_key` and the tested private matchers
explicitly. Keep `VERSION_RE`, collection parsing, Git/topic discovery and
body-marker readers in the facade. The extracted module imports models, never
the facade. Keep CLI and steps callers on facade module attributes so their
existing selector monkeypatches still intercept calls. Give the lookup module
its own directory-slug expression with the same accepted
language; it must not import `COLLECTION_SLUG_RE`. Keep the current shape-only
and fallback behavior until Steps 2 and 3 respectively.

Completion: the existing behavior passes the shared walk and all consumers keep
their current import paths. Inspect with
`rg -n 'prompt_workflow_docs|COLLECTION_SLUG_RE' tools/prompt_workflow_document_lookup.py`
for absence of those dependencies, and inspect facade re-exports with
`rg -n 'prompt_workflow_document_lookup' tools/prompt_workflow_docs.py`.
No PBT is needed for the extraction itself; Step 2 owns filename properties.

#### Step 1 addendums

- [ ] Line budget: docs baseline 650, at risk, ceiling 650; extraction is an
  explicit step goal, with an advisory result around 440 lines. The new lookup
  module and test start at 0, safe, ceiling 650; estimates 270 and 100. The new
  initializer starts at 0, safe, ceiling 650, estimate 6.
- [ ] If lookup growth later exceeds 650, split filename matching from layout
  and scoped selection into a lower-level names module, with facade exports
  retained. Do not duplicate the filename grammar.
- [ ] Full workflow timing readiness: new characterization and existing docs
  suites are ready for the shared walk; no time gate or xfail is introduced.

### Step 2. Require exact immediate document evidence for effort directories

#### Step 2 analysis and intent

Shape-only checks accept asset directories. Implement design Q01, Q02, Q05 and
Q06 through one eligibility predicate used by both enumeration entry points.
The added cost is an uncached immediate-entry check per eligible shape; older
layouts, sort order, exact resolution and collection validation stay intact.
Apply the shared execution checklist and ready-to-run commands above.

#### Step 2 implementation

Files involved:

- `tools/prompt_workflow_document_lookup.py` (existing, to be updated after Step 1).
- `tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_tdd.py` (existing, to be updated after Step 1).
- `tests/unit/tools/test_prompt_workflow_document_lookup/test_prompt_workflow_document_lookup_pbt.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` (existing, to be updated).

Tests first: parameterize both directory listings over the six qualifying kinds,
empty/assets/review/scratch-only directories, wrong version/slug, prefix-only
subtopics, nested-only evidence, unrelated siblings, `images`/`sub` effort names,
and hyphen/underscore spelling. Cover all older empty layouts, unsupported
uppercase/dotted slugs and depth-three nesting. Repair the three existing cases:
give the empty slug directories in `test_docs_dirs_supports_all_layouts` and
`test_docs_dirs_includes_version_slug_layout` one qualifying immediate document
each. In `test_resolve_document_uses_only_version_slug_and_type`, change the
slug-directory parameter to `docs/v9.8.0/git-history-report`, retaining its
existing document and folded-slug selector. This fixes identity disagreement,
not missing content.

Add bounded Hypothesis filename cases for separator folding and exact identity
using explicit generated expected identities, not `_exact_doc_matches` as the
oracle. Keep filesystem shape/error cases deterministic. In one process add,
rename and remove the last qualifying file between listing calls. Guard against
body reads during recognition; inject surfaced `OSError` from entry enumeration
and assert propagation. Preserve `Path.is_file()` semantics without adding a
platform-dependent symlink requirement.

The shared predicate accepts the four older shapes as before. For a full-version
slug child, require the independent slug pattern and one immediate `is_file()`
entry accepted by `_exact_doc_matches` for the enclosing version and slug across
draft, feature-request, issue, design, plan and validation-plan. Keep the six
kinds explicit, excluding the `requirement` alias. Both listing functions call
this predicate while retaining their separate enumeration. Never call a document
resolver from eligibility or cache a result across calls.

Completion: all recognition cases agree between applicable listings; general
exact ambiguity remains strict. Inspect
`rg -n 'COLLECTION_SLUG_RE|read_text|read_bytes|cache|resolve_document' tools/prompt_workflow_document_lookup.py`
to verify eligibility introduces no collection dependency, body read, cache or
resolver recursion; the existing resolver definition itself is expected.

#### Step 2 addendums

- [ ] Line budget: lookup and its TDD file were 0 at planning; recount Step 1
  results before editing, safe if below 550, otherwise at risk, ceiling 650.
  Advisory post-step counts are 330 and 300. PBT starts at 0, safe, ceiling 650,
  estimate 100. Existing docs tests: 611, at risk, ceiling 650, revised advisory
  post-step estimate 625 for the three fixture repairs; recount after editing.
- [ ] Keep new cases out of the 611-line suite. If its fixture repair cannot
  remain within 650, move its layout-test responsibility to the new package.
  Split a growing new suite by filename versus directory eligibility if needed.
- [ ] Full workflow timing readiness: deterministic IO and freshness cases plus
  existing resolution regressions run through the shared walk. No time gate.

### Step 3. Select within canonical or fallback scope

#### Step 3 analysis and intent

Current directory-first selection loses missing-sibling fallback and applies
newest-file selection too broadly. Implement design Q03, Q04 and Q07 using one
scoped discovery result. Preserve exact lookup separately, local timestamp
ties, role/subtopic matching and synthetic draft paths. One discovery pass
supplies both paths and provenance. Apply the shared checklist and commands.

#### Step 3 implementation

Files involved:

- `tools/prompt_workflow_document_lookup.py` (existing, to be updated after Step 2).
- `tests/unit/tools/test_prompt_workflow_docs/test_prompt_workflow_docs_tdd.py` (existing, to be updated).
- `tests/unit/tools/test_prompt_workflow_document_selection/__init__.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_document_selection/test_prompt_workflow_document_selection_tdd.py` (new, to be created).

Tests first: cover both public workflow entry points with a recognized canonical
parent, multiple local matches including tied mtimes, zero/one/multiple fallback
matches, invalid parents with tempting valid alternatives, and missing draft
files. Cover all four workflow roles and existing folded subtopic matching.
Place same-version fallback filenames in other recognized version directories
as well as the ordinary layouts to detect accidental version-scoped enumeration.
For slug-directory fixtures, add independently qualifying identity evidence
where necessary. Verify duplicate general resolution still raises while a
workflow topic prefers its own parent.

Repair `test_find_matching_documents_per_role` and
`test_most_recent_and_select_document` in the existing docs suite: replace their
uses of the relative `_ISO` topic with per-test topics whose draft paths are
under the temporary root's recognized `docs` directory. A draft file need not
exist. Keep their role and newest-file expectations; put the newly required
invalid-parent error cases in the new selection package. Inspect relative-topic
fixtures across the caller suites for actual discovery use before changing them;
do not modify field-only or intentionally stubbed-selector tests merely because
their paths are relative.

Use an internal frozen `_DocumentCandidates` dataclass carrying ordered paths
and a `Literal["canonical-parent", "fallback"]` scope. `_discover_candidates`
validates the resolved parent against `docs_dirs(root)`, scans the parent and
returns local matches immediately; only local absence scans every other
recognized directory using the existing role matcher and ordering. Replace the
old `_topic_docs_dirs` behavior. `find_matching_documents` returns a list adapter;
`select_document` consumes the internal result once. Keep `most_recent` for
local matches and enforce zero/one/ambiguous fallback selection.

Raise `PromptWorkflowError` with the accepted contextual information. Assert
role/topic/parent and every competing path, including stable path ordering,
without freezing the whole sentence. Invalid-parent errors come from discovery
for both public functions. Surface `OSError` from matching/stat work unchanged.
Use controlled access counters to prove selection does not rediscover scope and
local success does not inspect fallback documents for the requested role; do
not claim it avoids the eligibility inventory's reads. No new PBT is needed:
the finite scope/cardinality/role matrix is explicit and Step 2 covers folding.

Completion: every scoped result and error matches the design, and the shared
walk covers caller regressions. Inspect
`rg -n '_DocumentCandidates|_discover_candidates|most_recent|PromptWorkflowError' tools/prompt_workflow_document_lookup.py`
and verify no workflow caller catches these failures as absence.

#### Step 3 addendums

- [ ] Line budget: lookup baseline 0 at planning, recount actual Step 2 size;
  ceiling 650, advisory post-step 420, classify the measured band. New selection
  test and initializer: 0, safe, ceiling 650, estimates 300 and 6.
- [ ] Existing docs suite: baseline 611 at planning, at risk, ceiling 650;
  recount its actual Step 2 result before the two topic-fixture repairs.
  Advisory post-Step 3 estimate 640, including the Step 2 changes. If it would
  exceed 650, extract its selection-test responsibility into the new package;
  an estimate variance within 650 alone does not require a split.
- [ ] Apply Step 1's filename-responsibility split only if lookup exceeds 650.
  Split selection tests into local/invalid-parent and fallback modules within
  their package if needed; preserve the public behavior matrix.
- [ ] Full workflow timing readiness: local, fallback, error and single-discovery
  cases are ready for the shared walk. No timeout or xfail status changes.

### Step 4. Verify workflow acceptance and publish discovery guidance

#### Step 4 analysis and intent

Helper tests alone do not prove CLI routing and post-commit propagation. Drive
the accepted flows across the real modules and temporary filesystem, then update
the canonical layout guidance. Cover the design's sixteen acceptance rows,
reusing unit evidence for the exhaustive filename matrix. This adds integration
coverage without changing caller policy, IO complexity or optional-slug defaults.
Apply the shared execution checklist and ready-to-run commands above.

#### Step 4 implementation

Files involved:

- `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/__init__.py` (new, to be created).
- `tests/unit/tools/test_prompt_workflow_docs_layout_acceptance/test_prompt_workflow_docs_layout_acceptance_tdd.py` (new, to be created).
- `tools/prompt_workflow_post_commit.py` (existing, to be updated).
- `rules/docs_layout.md` (existing, to be updated).

Tests first: call `prompt_workflow.main` against small temporary Git repositories
and real effort files. Use the existing CLI arguments and host override; isolate
clipboard/host delivery only where necessary. Do not stub layout recognition,
selection, state computation or post-commit resolution. Verify document-mode
ambiguity, workflow local preference, unique fallback routing, and fatal exit 2
for invalid parents and ambiguous fallback without a success prompt. Include a
branch-relevant draft under an unsupported parent so the public invalid-parent
path is actually reached. Inspect emitted diagnostics and selected paths.

Exercise `plan_topics` and `skill --after-commit` with a validation-plan-only
canonical parent and a nonexistent draft: one fallback plan includes the topic
and routes by its validation state, none skips it, and multiple plans propagate
failure through the CLI. Re-run each relevant scenario after filesystem content
changes in the same process to guard against stale recognition. Existing
new-draft tests prove the optional slug default and missing-slug `NewDraftError`;
add a focused case in this acceptance package only if inspection finds a gap.

Update the `plan_topics` docstring to describe local-or-unique-fallback plans;
retain its exception propagation and synthesized draft path. Update
`rules/docs_layout.md` with the qualifying-content condition, exact identity,
canonical preference, unique missing-sibling fallback and invalid-parent error.
Do not change instruction adapters or add a migration command.

Completion: record an acceptance-to-evidence mapping for all sixteen design
rows, the actual CLI/post-commit results and the final fresh groundhog objective.
Inspect `rg -n 'content|fallback|canonical|version-slug' rules/docs_layout.md`
and the post-commit call path for accidental swallowing of errors. No acceptance
PBT is needed beyond the lower-level filename properties. Roll out the four
steps in order through normal reviewed commits; no deployment or push is planned.

#### Step 4 addendums

- [ ] Line budget: post-commit baseline 91, safe, ceiling 650, estimate 95. New
  acceptance test and initializer: 0, safe, ceiling 650, estimates 350 and 6.
  Layout rules baseline 43 Markdown lines; no Python ceiling applies.
- [ ] Keep the existing 585-line acceptance and 650-line skill suites unchanged.
  If the new acceptance suite exceeds 650, separate CLI and post-commit scenarios
  within its package; keep fixtures local until actual sharing warrants a helper.
- [ ] Full workflow timing readiness: temporary Git/CLI integration is ready
  for the final shared walk, including coverage and duration checks. No pending
  perf gate or xfail may be claimed as acceptance evidence.

## Open questions for the v0.12.0 docs_layout_hardening implementation plan

### Q01: Which responsibility should be extracted before lookup changes?

Question description: The docs facade is at 650 physical lines. Step 1 proposes moving layout enumeration, filename matching and document selection together into prompt_workflow_document_lookup.py while retaining caller access through explicit re-exports. Confirm that file boundary before implementing the split.

#### BBQ for Q01

Move the utensils for one cooking station together so cooks still collect them at the same counter. In this picture: the utensils are lookup functions and constants, the station is the new lookup module, and the counter is the existing docs facade.

#### Options for Q01

- Option A: Extract the cohesive lookup block and preserve facade exports.
  - pro: Creates headroom where the new behavior belongs and keeps caller imports stable.
  - con: Requires careful constant ownership and characterization of exported helpers.

- Option B: Extract collection parsing and leave lookup in the existing module.
  - pro: Moves a smaller unrelated block and keeps lookup function locations unchanged.
  - con: Leaves the growing lookup responsibility mixed with Git/topic and marker work.

#### Recommended option for Q01 (with arguments for this choice)

Option A: The contiguous lookup block has a one-way models dependency and is the responsibility this effort will extend. Keep collection validation and VERSION_RE in the facade and characterize behavior through its existing interface.

#### Answer to Q01: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because the contiguous lookup block has a one-way models dependency and is the responsibility this effort will extend. Keep collection validation and VERSION_RE in the facade and characterize behavior through its existing interface.

### Q02: Should extraction, recognition and selection remain separate steps?

Question description: The plan has three implementation steps followed by acceptance and guidance. Extraction can pass with existing behavior, recognition can then change without workflow fallback, and the scoped selection change follows. Decide whether to retain these reviewable checkpoints or combine prerequisite work.

#### BBQ for Q02

Test the grill assembly before changing the fuel and then the cooking routine. In this picture: assembly is extraction, fuel is directory eligibility, and the cooking routine is scoped selection.

#### Options for Q02

- Option A: Retain all four numbered steps and a green walk after each.
  - pro: Separates relocation regressions from the two intentional behavior changes and keeps validation attribution clear.
  - con: Requires more full gate walks and transiently preserves the old selection policy after recognition changes.

- Option B: Combine extraction and eligibility into one step, leaving three total.
  - pro: Reduces intermediate commits and gate walks.
  - con: Makes failures harder to attribute between moving code and changing directory recognition.

#### Recommended option for Q02 (with arguments for this choice)

Option A: The file is already at its ceiling and multiple callers share it. A behavior-preserving extraction checkpoint reduces implementation risk; each later step then has a narrow observable contract.

#### Answer to Q02: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because the file is already at its ceiling and multiple callers share it. A behavior-preserving extraction checkpoint reduces implementation risk; each later step then has a narrow observable contract.

### Q03: How much property-based testing should the filename contract receive?

Question description: Step 2 proposes bounded Hypothesis tests for pure filename identities, with deterministic filesystem matrices for layout, freshness and errors. Decide whether this gives sufficient implementation coverage or whether to generate directory mutation sequences as well.

#### BBQ for Q03

Vary the seasoning combinations in small samples and test the full cooking sequence with named recipes. In this picture: seasoning combinations are generated version/slug/kind identities, samples are pure matcher calls, and named recipes are deterministic filesystem scenarios.

#### Options for Q03

- Option A: Use bounded filename properties plus explicit filesystem scenarios.
  - pro: Exercises separator and identity combinations with a small independent oracle and predictable fixture cost.
  - con: Filesystem mutation sequences are limited to deliberately selected cases.

- Option B: Add stateful property tests that generate filesystem mutations.
  - pro: Explores additional orders of qualifying-file additions, renames and removals.
  - con: Adds fixture lifecycle and shrinking complexity for an uncached contract that has few relevant states.

#### Recommended option for Q03 (with arguments for this choice)

Option A: Properties suit the filename grammar and folding equivalence. Named same-process add/rename/remove tests directly prove the accepted freshness rules without a stateful filesystem harness.

#### Answer to Q03: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because properties suit the filename grammar and folding equivalence. Named same-process add/rename/remove tests directly prove the accepted freshness rules without a stateful filesystem harness.

### Q04: Where should deterministic IO guards and failure injection be applied?

Question description: The accepted design retains body and mtime reads in downstream workflow stages and inventories eligibility before local matching. Step 2 and Step 3 guards must prove the intended boundaries without forbidding legitimate IO or depending on machine-specific permission failures.

#### BBQ for Q04

Watch one preparation station while allowing the rest of the kitchen to work normally. In this picture: the watched station is recognition or candidate discovery, the kitchen is the full workflow, and the observation log is the test's scoped access counter.

#### Options for Q04

- Option A: Scope guards to recognition/discovery calls and inject surfaced filesystem errors at their entry points.
  - pro: Checks body-read exclusion, freshness, error propagation and single discovery deterministically while allowing downstream reads.
  - con: Requires clear guard lifetimes and distinguishing eligibility access from fallback matching.

- Option B: Apply broad filesystem guards to complete CLI runs and use real permission failures.
  - pro: Observes a larger end-to-end surface with fewer narrowly instrumented tests.
  - con: Can reject allowed document reads and varies with OS permissions, privileges and Path behavior.

#### Recommended option for Q04 (with arguments for this choice)

Option A: Only scoped instrumentation corresponds to the accepted IO contracts. Use explicit OSError injection for surfaced failures and retain real-filesystem acceptance for the combined normal behavior.

#### Answer to Q04: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because only scoped instrumentation corresponds to the accepted IO contracts. Use explicit OSError injection for surfaced failures and retain real-filesystem acceptance for the combined normal behavior.

### Q05: Should CLI acceptance use real temporary Git repositories?

Question description: Step 4 proposes real temporary Git repositories and calls to prompt_workflow.main. Existing acceptance tests often stub Git reads. Decide which approach should establish that branch-relevant drafts, invalid canonical parents and post-commit routing reach the real selection code.

#### BBQ for Q05

Rehearse serving from an actual small table before checking the full dining room. In this picture: the small table is a temporary Git repository, serving is CLI topic resolution and routing, and the dining room is the repository-wide regression suite.

#### Options for Q05

- Option A: Use small real Git repositories for representative CLI flows, isolating host delivery only.
  - pro: Validates Git-derived topic discovery and invalid-parent reachability together with real selection and routing.
  - con: Costs subprocess setup and requires careful, small fixtures.

- Option B: Stub Git discovery in all new acceptance tests, as several existing tests do.
  - pro: Keeps setup faster and allows direct control over selected topics.
  - con: Cannot independently establish that the chosen invalid-parent and post-commit scenarios reach the expected caller boundary.

#### Recommended option for Q05 (with arguments for this choice)

Option A: These are the final tests larger than unit tests. Keep a small real Git scenario set and reuse lower-level matrix evidence rather than duplicating every filename combination through the CLI.

#### Answer to Q05: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because these are the final tests larger than unit tests. Keep a small real Git scenario set and reuse lower-level matrix evidence rather than duplicating every filename combination through the CLI.

### Q06: How should the scoped selection test matrix be bounded?

Question description: Step 3 must cover all workflow roles, local and fallback cardinality, cross-layout search, wrong-version rejection and folded subtopics. A full Cartesian product would be large. Decide how to organize the cases while retaining evidence for every distinct branch and compatibility rule.

#### BBQ for Q06

Check every burner setting with a standard pan, then use selected pans to test fit. In this picture: burner settings are scope/cardinality outcomes across roles, the standard pan is a simple recognized parent fixture, and fit tests are representative layout/version/subtopic cases.

#### Options for Q06

- Option A: Parameterize roles against selection outcomes and add focused layout/version/subtopic edge cases.
  - pro: Covers each policy branch across roles without multiplying every filesystem shape into every case.
  - con: Requires an explicit evidence map so a compatibility dimension is not accidentally omitted.

- Option B: Build the full roles-by-layouts-by-cardinalities-by-spellings product.
  - pro: Provides uniform exhaustive coverage of the selected dimensions.
  - con: Repeats equivalent behavior many times and grows setup cost and maintenance.

#### Recommended option for Q06 (with arguments for this choice)

Option A: Use a compact role/outcome matrix, including local ties, plus explicit all-other-directory fallback cases and filename-version rejection. Map these tests and Step 4 acceptance to the sixteen design rows.

#### Answer to Q06: option A (with reason why it must be accepted as the answer)

Option A: Accept this implementation approach because use a compact role/outcome matrix, including local ties, plus explicit all-other-directory fallback cases and filename-version rejection. Map these tests and Step 4 acceptance to the sixteen design rows.
