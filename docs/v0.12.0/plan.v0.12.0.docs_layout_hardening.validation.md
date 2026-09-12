# v0.12.0 docs_layout_hardening implementation tracking and validation

No, it is not implemented.

This initial skeleton tracks the four steps in the
[implementation plan](plan.v0.12.0.docs_layout_hardening.md). No implementation
check has taken place and no acceptance evidence has been recorded.

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

Not started. Step 1 is not implemented because the lookup extraction and its characterization tests have not been implemented.

### Goal for Step 1

Move layout, filename matching and selection into a cohesive lower-level module while preserving the docs facade.

### Step 1 improvement expectations

Existing lookup outcomes, imports, ordering and IO behavior remain intact; the 650-line facade gains room for the accepted changes.

### What was implemented for Step 1

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 1

_(empty — no check has taken place yet.)_.

### Architecture check for Step 1

_(empty — no check has taken place yet.)_.

### Performance check for Step 1

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 1

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 1

_(empty — no check has taken place yet.)_.

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
