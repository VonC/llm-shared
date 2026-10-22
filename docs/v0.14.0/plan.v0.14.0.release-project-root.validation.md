# v0.14.0 release-project-root implementation tracking and validation

No, it is not implemented

This initial skeleton tracks the six steps of the [implementation plan](plan.v0.14.0.release-project-root.md).
No implementation check has taken place. The foundation, caller matrix and rollout
remain to be implemented and validated.

## File-based IO cost clarification for v0.14.0 release-project-root implementation

The synchronous CLI reads tooling dependency metadata and project declarations
once per invocation and retains validated data in memory. The launcher reads the
runtime record to find Python; bootstrap rereads it for validation, once per component.
It does not scan old environments or unrelated consumer files, nor prepare artifacts
on readiness, preflight or read-only paths. Necessary Git probes and path-ancestor
checks remain; managed destinations are revalidated immediately before mutation,
with same-parent temporary files and atomic replacement. There is no document-index
or event-loop requirement. Check actual read/probe counts and real filesystem
behavior; no check or performance result is asserted by this skeleton.

## Complexity and evidence expectations for v0.14.0 release-project-root

Follow the plan's linear metadata/lock-graph and declaration processing, path-depth
checks and avoidance of repeated whole-file reads. No wall-clock SLA or Step 0
xfail gate was approved. Subprocess timeouts detect hangs; groundhog owns duration
evidence. Run the current command from `pw scope day` through the shared launcher,
and the final coverage level as assigned by the plan, without freezing a selector.
All code budgets use physical lines including blanks and the 650-line Python
ceiling. Advisory estimates do not become additional completion gates.

In-process tests provide full production Python coverage; child processes provide
behavior evidence, not pytest-cov 7 coverage. Restore interpreter import state in
bootstrap tests. Reuse session repository templates, a manifest-verified tooling
copy with only the generated handler/registry source delta, and batched caller
matrices. Report fixture/setup durations as well as sub-second test-call results;
no exclusions hide slow calls. Directory junctions provide ordinary link coverage;
unavailable real file-symlink cases remain missing evidence until run on a capable
host. Steps 5/6 require the named pseudo-console and cancellation evidence.

## Step 1. Authoritative runtime production and readiness

### Analysis of Step 1 implementation state

Not started. Step 1 is not implemented because the runtime record producer, release dependency group and readiness bootstrap have not been implemented.

### Goal for Step 1

Publish a measured setup-owned environment identity and validate platform, interpreter, locked release dependencies and engine imports before dispatch.

### Step 1 improvement expectations

- Failed setup publishes no new identity; missing or unusable identity fails without fallback or repair.
- Applicable direct/transitive release packages and markers are checked independently of unrelated dev dependencies.
- Readiness uses isolated imports and creates no consumer artifacts.
- The setup entry receives saved activation status, uses the prepared absolute interpreter, and has fake-environment tests plus one recorded fresh-setup run.
- Explicit file-based helper loading keeps `tools` absent before readiness; the complete post-gate import closure stays within stdlib and locked release dependencies.
- Lock format 1, marker variables/operators, source-kind ambiguity, extra rejection and pyproject/lock agreement follow the plan's closed contract; registry rewriting changes no readiness result.
- Root-package identification and required release metadata accept uv's absent-edge/table empty-group shapes; nonempty metadata without locked edges fails.
- Only plain data crosses the readiness gate; typed helper interfaces pass strict checking without private/package class-identity assumptions or suppressions.
- Interpreter requirements accept the enumerated release-version clauses with padded tuple comparison; unsupported specifiers fail with status 2 and identifying diagnostics.

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

## Step 2. Controlled Git and physical project boundaries

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because the pinned Git adapter, environment policy and physical path validator have not been implemented.

### Goal for Step 2

Keep every operation on the validated worktree using one eligible Git executable, controlled routing and physical containment.

### Step 2 improvement expectations

- Stale inherited routing cannot redirect explicit project selection or index operations.
- Equivalent roots and linked-worktree metadata are handled correctly; managed paths reject external or nested repositories.
- Compatible identity, signing, credentials and parent-shell settings are preserved.
- Every listed routing key permits only local/worktree scope; surviving command-scope entries fail, with key/origin/scope evidence.

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

## Step 3. Strict configuration and domain schema registration

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because the common configuration reader and shipped schema registry have not been implemented.

### Goal for Step 3

Parse optional project configuration strictly with domain-owned schemas and a fail-closed tooling minimum gate.

### Step 3 improvement expectations

- Missing configuration uses defaults; invalid declarations never do.
- All declarations are checked without importing consumer code or scanning schema files.
- Any declared minimum tooling version fails until the later comparator exists; malformed syntax is diagnosed.
- The interim minimum syntax is exactly a release `MAJOR.MINOR.PATCH` without a `v` prefix.

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

## Step 4. Managed writes, artifact capabilities and operation ownership

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the managed-write service, read-only artifact adapter and shared operation lock have not been implemented.

### Goal for Step 4

Separate resolution from mutation, revalidate managed destinations and retain exact project operation ownership through handoffs.

### Step 4 improvement expectations

- Read-only/preflight failure paths neither prepare nor migrate artifacts.
- Managed writes use revalidated same-parent temporary files and atomic replacement.
- Live or retained owners block competing mutations; stale recovery requires exact dead-owner evidence and no retained handoff.
- Artifact preparation reuses `prepare_home` between physical validations; loading errors return 2 and preparation errors return 1 with owned rollback.
- A complete versioned temporary owner record is published by non-replacing rename; leftover temporary files confer no ownership and unknown record versions fail conservatively.
- Unverifiable-owner diagnostics show the project-relative lock path and available owner fields; no recovery CLI is claimed.

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

## Step 5. Invocation context, dispatch and actual launchers

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because the context/transport/result interfaces and real explicit-root and alias launchers have not been implemented.

### Goal for Step 5

Compose the foundation into fixed invocation context and prove supported Windows/native caller channels.

### Step 5 improvement expectations

- Explicit selectors, alias discovery and script-derived build roots preserve intended project identity.
- GetConsoleMode and explicit non-interactive policy prevent hidden prompts and assumed consent.
- UTF-8/LF streams remain separate; public 0/1/2 and original child failure details survive launcher cleanup.
- The reserved entry prefix distinguishes explicit batch, alias batch and explicit native input; missing/duplicate kinds and missing explicit roots fail.
- ASCII launchers report pre-Python record/interpreter failure with status 2, use their own checkout, parse localized code-page output and restore state wherever cleanup regains control.
- The pseudo console reads localized answer keys and proves doskey and Ctrl+C outcomes: batch yes termination, batch no status 1 with diagnostics, native status 1 with diagnostics, and no prompts for redirected stdin.
- Context derives the project name, Windows/POSIX roots and six legacy locations without exporting variables or trusting inherited values.
- Real test handlers exist only in the verified tooling copy; the unmodified checkout rejects their names.

### What was implemented for Step 5

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 5

_(empty — no check has taken place yet.)_.

### Architecture check for Step 5

_(empty — no check has taken place yet.)_.

### Performance check for Step 5

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 5

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 5

_(empty — no check has taken place yet.)_.

## Step 6. Integrated acceptance and foundation rollout

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because the subprocess acceptance matrix and invocation documentation have not been implemented.

### Goal for Step 6

Prove the assembled foundation on supported Windows x64 and document usable routes and later integration ownership.

### Step 6 improvement expectations

- Real processes/filesystems/console transport cover stale environments, isolation, locking, cancellation and failure without writes.
- Acceptance distinguishes production foundation behavior from disposable caller-contract fixtures and deferred domain integration.
- Resolved groundhog objectives, coverage, line budgets and repository-relative evidence support completion.
- Missing-launcher fixtures check file absence first and never hide an installed launcher's status 1/2; production AC11 remains unproven until item 5.
- Every supported caller has real transport/cancellation evidence; unavailable console or file-symlink evidence cannot become a passing completeness claim.
- Detailed contracts live in the two existing reference pages; README supplies a short pointer and category links retain the required order.

### What was implemented for Step 6

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 6

_(empty — no check has taken place yet.)_.

### Architecture check for Step 6

_(empty — no check has taken place yet.)_.

### Performance check for Step 6

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 6

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 6

_(empty — no check has taken place yet.)_.
