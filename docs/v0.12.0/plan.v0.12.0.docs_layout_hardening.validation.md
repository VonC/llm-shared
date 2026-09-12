# v0.12.0 docs_layout_hardening implementation tracking and validation

No, it is not implemented.

This document tracks the four steps in the
[implementation plan](plan.v0.12.0.docs_layout_hardening.md). Step 1 has passed
its implementation check and shared groundhog walk. Steps 2 through 4 remain
pending; the new recognition and selection behavior is not implemented yet.

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

Not started. Step 2 is not implemented because the shared eligibility predicate and its regression/property coverage have not been implemented.

### Goal for Step 2

Make both directory listings require exact qualifying immediate filenames for full-version slug directories.

### Step 2 improvement expectations

The six accepted kinds qualify without a draft, false positives are rejected, older layouts remain valid, and subsequent calls observe content changes without body reads or a cache.

### What was implemented for Step 2

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 2

_(empty — no check has taken place yet.)_.

### Architecture check for Step 2

_(empty — no check has taken place yet.)_.

### Performance check for Step 2

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 2

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 2

_(empty — no check has taken place yet.)_.

## Step 3. Select within canonical or fallback scope

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the scoped candidate result, selection policy and diagnostics have not been implemented.

### Goal for Step 3

Validate the canonical parent, discover one scope, and preserve the distinct local and fallback selection rules.

### Step 3 improvement expectations

Local newest/tie behavior is retained; missing siblings use all other recognized directories with zero/one/ambiguous outcomes, and invalid parents and operational errors remain observable.

### What was implemented for Step 3

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 3

_(empty — no check has taken place yet.)_.

### Architecture check for Step 3

_(empty — no check has taken place yet.)_.

### Performance check for Step 3

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 3

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 3

_(empty — no check has taken place yet.)_.

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
