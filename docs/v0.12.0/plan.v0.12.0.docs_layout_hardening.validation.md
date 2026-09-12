# v0.12.0 docs_layout_hardening implementation tracking and validation

No, it is not implemented.

This document tracks the four steps in the
[implementation plan](plan.v0.12.0.docs_layout_hardening.md). Steps 1 through 3
have passed their implementation checks and shared groundhog walks. Step 4
remains pending: CLI/post-commit acceptance and published layout guidance.

## File-based IO cost clarification for v0.12.0 validation

Verify current immediate filename and file-type checks without recognition-time
body reads. Preserve the accepted uncached freshness behavior, existing
recursive/version-scoped enumeration and sorting, and downstream body/mtime
reads. A selector must consume one scoped discovery result. Local success can
avoid fallback document matching while eligibility discovery still inspects
other directories. No index, transactional snapshot or latency target is promised.

## Complexity and timing clarification for v0.12.0 validation

Assess each step against the plan's existing enumeration and sort costs plus
at most one immediate-entry qualification traversal per candidate directory per
listing invocation. Six document kinds are fixed; directory and filename counts
are variable. Verify no repeated discovery solely to reconstruct selection scope.
Use deterministic IO/freshness evidence and the normal full-run duration gate;
there is no Step 0 timeout or xfail gate to remove.

## Step 1. Extract the document lookup responsibility

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

Layout enumeration, filename matching and selection now live in
`tools/prompt_workflow_document_lookup.py`. The docs facade retains the existing
imports and selector patch points. Characterization tests and the shared walk
confirm the existing behavior before Steps 2 and 3 change its policy.

### Goal for Step 1

Move layout, filename matching and selection into a cohesive lower-level module while preserving the docs facade.

### Step 1 improvement expectations

Existing lookup outcomes, imports, ordering and IO behavior remain intact; the 650-line facade gains room for the accepted changes.

### What was implemented for Step 1

Moved the contiguous `docs_dirs` through `select_document` block, its layout
constants and filename selectors into the lookup module. Its independent
`DIRECTORY_SLUG_RE` accepts the same language as the collection expression.
The facade explicitly re-exports lookup names, including the tested private
matchers, and retains Git/topic discovery, collection parsing, `VERSION_RE`
and document-body marker readers. Explicit export lists satisfy the import
lint and type-checking rules without changing caller imports.

Added the dedicated unit-test package and four parametrized cases covering
exact ambiguity diagnostics, canonical-parent preference, ordinary versus
validation plans, slug folding, subtopic matching and deterministic mtime ties.
Existing docs and caller suites remain regression inputs.

Physical counts after extraction are 501 for the facade, 274 for lookup, 87 for
the new test file and 6 for its initializer. The facade and lookup exceed the
advisory projections of about 440 and 270, because compatibility exports are
explicit; every involved file stays below the hard 650-line ceiling.

### New types or classes introduced for Step 1

No new type or class was introduced. The lookup module uses the existing
`Topic` and `PromptWorkflowError` models.

### Architecture check for Step 1

The lookup module depends only on the standard library and workflow models.
The required dependency search found no facade import or `COLLECTION_SLUG_RE`
reference there. The facade imports lookup, and CLI and steps callers still
resolve selectors through facade attributes. Git and collection responsibilities
remain outside lookup. This tooling adapter split introduces no domain-layer
dependency or responsibility violation, and all files meet the line budget.
Nothing needs to be addressed.

### Performance check for Step 1

The moved function bodies preserve the recursive and version-scoped directory
walks, sorted entry order, local-parent preference, fallback and mtime reads.
The slug expression has the same grammar. No additional traversal, sort,
all-candidate comparison, body read or cache was introduced. Existing sort
costs remain as accepted by the plan. The successful full phase took 3m 58.6s;
groundhog reported duration outliers and exclusions as skipped, so this is
execution evidence rather than a new timing guarantee.
No performance issue needs to be addressed.

### Unit test coverage check for Step 1

The configured coverage source is `tools` in `pyproject.toml`; both changed
production modules are inside that scope. Package initializers and tests are
excluded by the gate. The dedicated lookup test package exercises the facade
with real temporary files; existing docs tests cover the moved matchers and
layout cases, and main/steps tests retain their facade selector patches.

The fresh `ghog day` walk finished on 2026-09-12 at 19:33:26 +02:00 with
`state=done exit=0`. Check, 221 affected tests and all 2,714 full-run tests passed
without failures, warnings or xfails; the full gate reported `cov=100`.
The implementation check used that completed evidence and inspected code and
tests without starting another test run. There are no impacted class files.
No unit-tested class below 100% needs completing. No executable top-level
symbol in an impacted file outside the coverage gate is unreferenced.

### Feature integrity for Step 1

General resolution still matches an exact topic and reports ambiguous layouts;
workflow lookup still admits subtopics and prefers the canonical parent.
Ordinary and validation plans stay distinct, and equal mtimes retain the first
candidate in existing order. CLI, steps, open-question and post-commit consumers
retain their facade access paths. Shape-only effort recognition and the old
fallback behavior remain intentionally unchanged until Steps 2 and 3.

## Step 2. Require exact immediate document evidence for effort directories

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

Both directory listings now use one eligibility predicate. Full-version slug
children require an immediate file with an exact supported kind, version and
folded slug. Regression and property cases cover the accepted boundary, and
the corrected groundhog walk reached the configured coverage objective.

### Goal for Step 2

Make both directory listings require exact qualifying immediate filenames for full-version slug directories.

### Step 2 improvement expectations

The six accepted kinds qualify without a draft, false positives are rejected, older layouts remain valid, and subsequent calls observe content changes without body reads or a cache.

### What was implemented for Step 2

`docs_dirs` and `docs_dirs_for_version` retain their respective enumeration and
ordering while filtering through `_is_supported_docs_dir`. The predicate
accepts the four older layouts by shape and delegates slug-child evidence to
`_has_effort_document`. That helper checks immediate `is_file()` entries using
`_exact_doc_matches` and six explicit kinds, without the `requirement` alias.
It stops after the first match, reads no bodies, caches nothing and propagates
surfaced enumeration errors.

The dedicated TDD suite runs both listings against all six kinds, empty and
unrelated content, wrong identities, subtopics, nested-only evidence, matching
directory names, common asset names, separator spelling, older empty layouts,
unsupported shapes, ordering and version scope. It exercises add/rename/remove
freshness, forbids body reads, injects enumeration failure and guards early exit.
Two bounded Hypothesis properties generate explicit identities and check folded
spelling plus rejection of changed versions, topics and subtopics.

The three planned legacy fixtures now contain matching immediate evidence or
use the correct `git-history-report` directory identity. The package initializer
describes its expanded coverage. Six inline-code spans in the review transcript
were repaired after Markdown check failures: four existing spans and two paths
in the Step 2 round 1 request. Future request inputs quote those paths too; no
review assessment content changed. The independent round 1 review confirmed
the implementation and requested only the two request-formatting repairs.

Physical counts before and after are: lookup 274 to 294, dedicated TDD 87 to
289, PBT 0 to 68, legacy docs TDD 611 to 615, and initializer 6 to 6. All are
below 650 and the post-step advisory estimates; the legacy suite remains in
the at-risk band. No file split is required.

### New types or classes introduced for Step 2

No production type or class was introduced. `_has_effort_document` isolates
the filename scan from layout classification to meet the complexity gate.
`EFFORT_DOCUMENT_TYPES` names the six concrete evidence kinds explicitly.

### Architecture check for Step 2

The lookup adapter still imports only the standard library and workflow
models. Its directory pattern is independent of collection validation, both
listing paths share classification, and evidence reuses the exact matcher
without resolver recursion. Public facade exports and caller patch points
remain intact. The dependency/body-read/cache inspection found only the
existing resolver definition/export and the docstring describing no cache.
No DDD-Hexagonal violation or responsibility smell is present.
Nothing needs to be addressed.

### Performance check for Step 2

Existing recursive and version-scoped enumeration and sorting remain. Added
qualification visits at most E immediate entries per eligible shape and tests
six fixed kinds, with filename length included in matching cost. There is no
new sort, all-candidate comparison, resolver call, body read or retry. The early
exit test proves scanning stops on the first qualifying file. Freshness tests
prove subsequent calls re-evaluate content. The latest successful full phase took
2m 44.7s; duration outlier and exclusion checks were reported as skipped, so
the run supplies no separate duration-policy measurement.
No performance issue needs to be addressed.

### Unit test coverage check for Step 2

The coverage source is `tools` with `fail_under = 100` in `pyproject.toml`;
lookup is measured, while tests and package initializers are excluded. The
dedicated lookup package exercises both facade listings and the exact matcher;
existing docs suites cover remaining resolution and role-selection branches.
The new evidence helper is reached through the shared predicate from both
public listings. Every production top-level function remains referenced by
tests or another function in the package, and no class file is impacted.

The fresh `ghog day` walk after the round 1 formatting repairs finished on
2026-09-12 at 21:27:26 +02:00 with
`state=done exit=0`. The log freshness check passed. Check, affected tests and
the full suite passed; the closing result was `fail=0 warn=0 xfail=0 cov=100`.
This implementation check used that completed evidence and static inspection
without running tests again.
No unit-tested class below 100% needs completing. No executable top-level
symbol in an impacted file outside the coverage gate is unreferenced.

### Feature integrity for Step 2

Only full-version slug-child recognition becomes stricter. Older empty layouts,
directory order, exact ambiguity, requirement aliases for document selection,
validation-plan distinction, workflow subtopic matching and timestamp ties
remain supported. Collection validation and optional-slug creation are
unchanged. Surfaced filesystem errors remain observable. Canonical-parent
validation and missing-sibling fallback are still the separate Step 3 work.
No existing feature or reporting capability appears impaired.

## Step 3. Select within canonical or fallback scope

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

Workflow discovery validates the canonical parent, returns its ordered matches
when present, and otherwise searches every other recognized directory.
Selection retains local newest/tie behavior and requires a unique fallback.
The fresh groundhog walk passed check, affected tests and full coverage.

### Goal for Step 3

Validate the canonical parent, discover one scope, and preserve the distinct local and fallback selection rules.

### Step 3 improvement expectations

Local newest/tie behavior is retained; missing siblings use all other recognized directories with zero/one/ambiguous outcomes, and invalid parents and operational errors remain observable.

### What was implemented for Step 3

`_discover_candidates` inventories `docs_dirs(root)` once and compares resolved
directory paths with the draft's parent without requiring the draft to exist.
It scans local entries first and returns immediately on a match. Only local
absence permits scanning other recognized directories, retaining role, exact
version, folded subtopic matching and existing ordering.

`find_matching_documents` adapts the scoped tuple to its public list result.
`select_document` consumes discovery directly, using `most_recent` locally and
zero/one/ambiguous cardinality for fallback. Invalid-parent errors include the
role, version, slug and canonical directory; fallback ambiguity also lists every
competing path in stable order. Repository-relative diagnostics are used where
applicable, and matching/stat errors propagate unchanged.

The new selection package adds 47 parameterized cases across all four roles,
both requirement kinds, local timestamps and ties, fallback cardinalities,
cross-version directory searches, qualifying slug children, invalid parents,
missing drafts, normalized paths, exact-resolution ambiguity and IO failures.
Access counters prove a single inventory and no fallback role matching after
local success. The two planned legacy selection fixtures now use temporary
recognized parents. The affected run identified one additional real-discovery
fixture in `test_find_matching_documents_folds_hyphen_and_underscore`; its draft
path was repaired while preserving all role assertions. Relative-topic fixtures
in main, plan, models and steps remain appropriate for stubbed or field-only use.

The obsolete `_topic_docs_dirs` helper and its facade import/export were removed;
the facade docstring now describes scoped selection. This small additional
facade edit is required by replacing the private helper; public selector
signatures and caller monkeypatch points are retained.

Physical line counts before and after: lookup 294 to 345, facade 501 to 500,
legacy docs TDD 615 to 615, selection TDD 0 to 253, initializer 0 to 6. All stay
below 650; the legacy suite remains at risk and the other files remain safe.
The final counts stay within the advisory projections, so no split is needed.

### New types or classes introduced for Step 3

The internal frozen `_DocumentCandidates` dataclass holds an ordered
`tuple[Path, ...]` and a `Literal["canonical-parent", "fallback"]` scope.
It carries selection provenance without another discovery pass.
`_directory_matches` isolates ordered role matching, and `_render_parent`
handles relative or external canonical-parent diagnostics.

### Architecture check for Step 3

The lookup filesystem adapter depends only on standard-library facilities and
workflow models. The facade continues to own Git/topic and document-body work;
callers still select through facade attributes. No caller catches the new
errors as document absence. The internal result does not introduce an upward
dependency, collection coupling or a new public policy surface.
No DDD-Hexagonal violation or responsibility smell is present.
Nothing needs to be addressed.

### Performance check for Step 3

Existing directory and matching-entry sorts remain; no new sort or nested
all-candidate comparison was introduced. Resolved-directory inventory,
canonical selection and fallback exclusion use linear passes. Each selected
directory's entries are matched once, and local success avoids fallback role
matching while allowing the eligibility inventory's reads. There is no cache,
retry, body read or rediscovery to recover scope. Path and filename lengths
remain part of the existing filesystem and matching cost.

The successful full phase took 3m 53.9s. Duration-outlier and exclusion checks
were reported as skipped, so this result is not a separate duration-policy
measurement. Deterministic access assertions cover the promised IO boundaries.
No performance issue needs to be addressed.

### Unit test coverage check for Step 3

`pyproject.toml` measures `tools` with `fail_under = 100`; both modified
production modules are included. Tests and package initializers are excluded.
The dedicated lookup and selection packages exercise the lookup module, with
the existing docs suites covering the retained facade and legacy paths.
The new dataclass is constructed by both discovery scopes; every new helper
is reached through the public selectors. Static inspection covers local,
absent, unique, ambiguous, invalid-parent and IO-error paths. No new PBT is
needed for the finite scope/cardinality matrix; Step 2 retains folding properties.

The final detached `ghog day` run started on 2026-09-12 at 23:31:09 +02:00
and `ghog status` confirmed `state=done exit=0` at 23:35:40 +02:00.
Its fresh log contains the completed check, affected and 2,842-test full phases,
closing with `fail=0 warn=0 xfail=0 cov=100`. Earlier test lint/complexity issues
were fixed, and the extra legacy fixture repair passed the prescribed focused
rerun before this final walk. This implementation check uses that evidence and
static inspection without running tests again.
No unit-tested class below 100% needs completing. No executable top-level
symbol in an impacted file outside the coverage gate is unreferenced.

### Feature integrity for Step 3

General exact resolution remains strict about duplicate documents. Workflow
local preference, timestamp ties, four-role matching, folded subtopics and
validation-plan distinctions remain supported. Missing drafts work with a
recognized parent; unsupported parents and competing fallback matches now fail
explicitly as designed. Public return types and facade patch points remain
compatible. Optional-slug creation, collection validation and unrelated review
workflows are unchanged. Step 4 still owns CLI/post-commit acceptance and
published layout guidance.
No existing feature or reporting capability appears impaired.

## Step 4. Verify workflow acceptance and publish discovery guidance

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the CLI/post-commit acceptance coverage and shipped layout guidance have not been implemented.

### Goal for Step 4

Exercise the accepted behavior through real workflow callers and document the verified contract.

### Step 4 improvement expectations

CLI routing and fatal diagnostics, missing-draft post-commit fallback, optional-slug compatibility and all sixteen design acceptance rows have recorded evidence from a fresh groundhog objective.

### What was implemented for Step 4

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 4

_(empty — no check has taken place yet.)_.

### Architecture check for Step 4

_(empty — no check has taken place yet.)_.

### Performance check for Step 4

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 4

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 4

_(empty — no check has taken place yet.)_.
