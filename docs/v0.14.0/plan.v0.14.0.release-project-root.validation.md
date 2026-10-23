# v0.14.0 release-project-root implementation tracking and validation

No, it is not implemented

This document tracks the six steps of the [implementation plan](plan.v0.14.0.release-project-root.md).
Step 1's round 7 boundary repair passes the full speed day, final static checks
and strict duration assessment with the human's two named live-UV exceptions.
The one-second total-duration audit remains separate from
groundhog's call-only speed gate. Steps 2 through 6, including the public caller
matrix and rollout, remain pending.

## File-based IO cost clarification for v0.14.0 release-project-root implementation

The synchronous CLI reads tooling dependency metadata and project declarations
once per invocation and retains validated data in memory. The launcher reads the
runtime record to find Python; bootstrap rereads it for validation, once per component.
It does not scan old environments or unrelated consumer files, nor prepare artifacts
on readiness, preflight or read-only paths. Necessary Git probes and path-ancestor
checks remain; managed destinations are revalidated immediately before mutation,
with same-parent temporary files and atomic replacement. There is no document-index
or event-loop requirement. Check actual read/probe counts and real filesystem
behavior; the per-step sections below record the available evidence.

## Complexity and evidence expectations for v0.14.0 release-project-root

Follow the plan's linear metadata/lock-graph and declaration processing, path-depth
checks and avoidance of repeated whole-file reads. No production wall-clock SLA
or Step 0 xfail gate was approved. The later test ceiling is 1.0 seconds for
setup + call + teardown, recorded by a separate strict audit; groundhog's
built-in speed gate measures calls only. Subprocess timeouts detect hangs.
Groundhog owns suite execution and coverage
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

Yes. Step 1 has been fully implemented.

The round 1 gaps R1 to R5 remain fixed. R6 now compares the checkout root and
interpreter prefix in the same lexical form before physical containment
validation; producer tests cover alias success and physical escape failure.
R7 process scenarios each own their measured fixture and real launch, keeping
every assertion. All process scenarios now fall below one second in the full
audit, including missing engine at 0.5580s. Both real UV lock tests still
exceed the ceiling. Additional startup experiments did not clear this gap.
After round 3, the human chose to retain live UV generation and publish round 4;
the two measured costs are now named exceptions in the performance check. The
general ceiling and all integration assertions remain unchanged.

R8 now synchronizes parent mutations with the independent waiter's first
notification wait, after its startup status scan and initial discovery. The
round 4 review found that boundary correct for the gate, concluded and
competing-reviewer journeys, and the reviewer's `ghog affected --no-cov` run
passed them. The post-R8 full run reached 100% coverage but failed in
sequential timings on the Gemini identity fixture. Round 7 now has a completed
whole-suite speed proof after the human-authorized R9 boundary repair; the
round 5 review accepted the R10 cleanup repair.

On 2026-10-23 the human instructed that R9 remain unresolved but not block
any review for now, and explicitly requested round 6 publication. This standing
review guidance permits publication with the gap disclosed; it does not resolve
R9, establish complete validation, or authorize a commit or Step 2.

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

- `senv.bat` saves preparation and producer statuses before cleanup.
  `bin/release_runtime_record.bat` invokes the prepared absolute interpreter
  with `-I -X utf8`; failed preparation preserves the previous designation.
  Successful no-environment/global setup warns without publication, and both
  temporary status variables are cleared while failure exit codes survive.
- `runtime_identity.py` measures executable and prefix, validates the versioned
  record and lexical/physical containment, and publishes atomically under ignored
  `venvs/release-runtime.v1.txt`. Its two UTF-8 lines contain version `1` and
  the checkout-relative environment directory; one parse/serialize contract
  covers literal Unicode, CRLF input, line counts and unsupported versions.
  Readiness rejects missing, moved, broken and foreign environments without fallback.
- `pyproject.toml` declares an empty stdlib-only `release` group included by
  `dev`; the regenerated `uv.lock` retains matching release metadata.
- `bootstrap.py` loads exact sibling helpers under private module names,
  disables bytecode writes and delays search-path insertion and engine import
  until readiness succeeds. Failures produce status 2 and a repair diagnostic.
  The production CLI remains assigned to Step 5; Step 1 tests supply a disposable
  engine probe and exercise the missing-engine failure.
- `readiness.py` checks format-1 locks, the unique virtual root, empty uv lock
  shapes, source/version disambiguation, transitive cycles, installed versions,
  extra rejection and dev isolation. `markers.py` implements the approved closed
  grammar and padded release-version comparisons without evaluating Python.
- Separate unit folders cover runtime identity, readiness, markers and bootstrap.
  Acceptance fixtures cover the batch producer, actual junction escape, isolated
  imports, unchanged consumer files, the eager stdlib import closure and two
  offline uv-generated empty-release lock shapes. Fresh setup produced the
  measured identity and successful isolated readiness evidence in private notes.
- The user-requested fixture optimization reuses CLI imports with restored host
  state and the existing Git double for identity and parent exchange operations.
  Lifecycle ownership takeover, status/workflow launchers and independent waiters
  retain real processes; migration retains real Git. Commit-plan scenarios copy
  a session-owned real Git baseline and keep real adapters and Git snapshots.
  Synthetic fixture commits disable signing locally. Shared ENV test data lives
  in the support module, and historical review headings keep their round suffix.

Pre-R8 validation on 2026-10-22: `ghog day --full=speed --whole-suite` completed with
`proof=speed`, zero failures, warnings, xfails, duration outliers or exclusions.
The full stage reported `cov=100`; the sequential timing stage ran 3,699 tests
at 17:50:24 +02:00, with `reused=none`. This evidence includes the R6 producer
regressions, per-scenario fixture split and interpreter hard-link change.
The source scan finds the
intended post-gate `import_module` call and the word `global` in a setup comment;
neither match is ambient runtime selection or an environment-directory scan.
Reviewer evidence for round 2: `ghog check` and `ghog affected --no-cov` over
the bound whole scope both exited 0, the latter with 3,696 tests and no
failures, warnings or xfails.

After the R8 repair, `ghog day --full=speed --whole-suite` on 2026-10-22
passed check, all 3,699 affected tests, and full coverage at 100%. Sequential
timings ended at 21:35:19 +02:00 with two setup errors sharing the Gemini
identity fixture, so the walk exited 2 without speed proof. The first resume
did not provide an ownership capability; the fixture then hid its diagnostic
behind `KeyError: ownership_generation`. An added assertion now checks that
resume result before using the capability and reports only operation, outcome
and diagnostic. Both the identity module and surrounding review-resume tests
pass in focused groundhog runs. A bounded 80-journey diagnostic did not
reproduce the failure; those passes do not resolve the failed full walk.
Reviewer evidence for round 4: `ghog check` and `ghog affected --no-cov` over
the bound whole scope both exited 0, the latter with 3,699 tests and no
failures, warnings or xfails. That run passed the identity module as well;
it does not replace the failed timing walk. A subsequent sequential diagnostic
ran the 63 acceptance tests preceding and including the identity module in
suite order; all passed without reproducing R9. Inspection of the in-process
runner and transition path has not established a cause. Testmon sorts the
affected stage by recorded test duration, so only the failing timings stage
and these prefix runs used collection order. Reviewer evidence for round 5:
`ghog check` exited 0, and `ghog affected --no-cov` over the bound whole scope
exited 0 with the one test testmon selected after the R10 change.

Both additional diagnostic paths suggested in round 5 passed without
reproducing R9. The focused review-resume run reported no ResourceWarning,
including final garbage collection. The uninstrumented, collection-order
whole-suite `ghog timings` diagnostic completed on 2026-10-23 at
09:18:14 +02:00 with exit 0, no failures, warnings, xfails, outliers or
exclusions; coverage was skipped. Its slowest call was 0.95 seconds.
These diagnostics establish no cause or repair, do not replace the failed
full walk, and do not prove setup + call + teardown compliance.

Reviewer evidence for round 6: `ghog affected --no-cov` over the bound whole
scope exited 0 with no test selected, because only this document changed after
round 5, and `ghog check` exited 0. The review accepts both diagnostics: the
timings pass reproduced the failing stage's sequential, uninstrumented shape.
The clean ResourceWarning probe makes a leaked in-process file object a less
likely R9 holder. It excludes neither a handle held only while the claim runs
nor an external scanner.

For round 7 the human explicitly authorized the writer prompt's diagnostic
and bounded production repair as Step 1 boundary work. The plan's Step 1 file
list is unchanged. Before the repair, the private 5,000-iteration probe in each
folder recorded 86 wrapped `PermissionError` failures in TEMP and 119 under
`.reviews`, all with WinError 5, and no other errors or sleep calls. Evidence:
`.reviews/a.release-project-root.step1.tmp.r7.diag-before.log`.
This reproduces the backfill replacement failure on the current host; it does
not identify the historical R9 file holder or establish its exact exception.

`RoleNatureBackfill._commit_prepared` now retries only `PermissionError` for
at most five attempts, with delays of 0.01, 0.02, 0.04 and 0.08 seconds.
Exhaustion follows the unchanged rollback, error wrapping and cleanup path.
Three unit tests cover transient recovery, exhaustion after the first target
was exposed, and immediate plain `OSError` failure. Their sleep recorder avoids
real waits, and the existing rollback test remains unchanged. The focused
`ghog single` passed with no failures, warnings or xfails; evidence:
`.reviews/a.release-project-root.step1.tmp.r7.retry.log`.
The unchanged after-fix probe completed another 5,000 iterations in each
folder with zero escaped permission failures and zero other errors. TEMP
recorded 87 retry sleeps in 198.1740 seconds; `.reviews` recorded 115 in
188.3987 seconds. These sleep counts prove that the retry absorbed real
transient permission failures; they do not identify the historical R9 holder.
Evidence: `.reviews/a.release-project-root.step1.tmp.r7.diag-after.log`.
Both script-created scratch folders were removed after each run.
The round 7 `ghog day --full=speed --whole-suite` completed on 2026-10-23
at 13:49:45 +02:00 with exit 0, `proof=speed`, `reused=none`, 3,702 passing
sequential tests, and zero failures, warnings, xfails, call outliers or
exclusions. The full stage reported 100% tools coverage, including the retry
exhaustion branch. The Gemini identity journey passed in collection order.
The exact plan source scan passed with only the intended post-gate import and
the global-setup comment. Final `ghog check` passed with no failures, warnings
or xfails; evidence: `.reviews/a.release-project-root.step1.tmp.r7.check.log`.
Full-walk evidence:
`.reviews/a.release-project-root.step1.tmp.r7.timing/groundhog.log`.

Reviewer evidence for round 7: `ghog check` exited 0, and
`ghog affected --no-cov` over the bound whole scope exited 0 with all 3,702
tests selected and no failures, warnings or xfails. The review accepts the
probe as R9 closure evidence: on the claim's own write-then-replace path it
reproduced wrapped `PermissionError` before the repair and none after, while
the retry absorbed 202 real violations. R9 is resolved. Its historical
exception stays unknown; the retained identity diagnostic would report the
operation and outcome if a different cause recurred.

R10 is repaired: the competing-reviewer fixture starts with an empty process
list and appends each waiter inside `try/finally`, so failure to start the
second waiter still cleans up the first. The focused concurrency module passes
through `ghog single`, with all existing assertions and real processes retained.

### New types or classes introduced for Step 1

`RuntimeIdentity` is the immutable measured designation; `InvalidRecordError`
identifies malformed record lines. `Package` holds one lock candidate and
`Closure` indexes and traverses candidates; `InvalidMetadataError` rejects
invalid input shapes. `MarkerParser` owns the closed expression grammar.
Bootstrap's `Identity`, `IdentityFactory`, `RuntimeModule`, `MarkersModule`,
`ReadinessModule` and `Engine` protocols type the dynamically loaded interfaces
without importing package twins before the gate.

### Architecture check for Step 1

The marker parser and graph logic use standard data and injected operations.
Filesystem publication, installed-distribution lookup and engine import remain
at explicit infrastructure boundaries. Bootstrap wires standalone helpers with
typed interfaces; only paths, strings and parsed values cross the gate. No
consumer configuration or future release-domain dependency was introduced.
The authorized role-nature retry is a private static helper of the existing
backfill class, copies the established atomic-writer pattern and adds only a
standard-library import.

Physical line counts: runtime identity 162, readiness 195, markers 161 and
bootstrap 139; all new Python files are below 650, and initializers are at most
4 lines. The edited role-nature module has 312 lines. The setup batch entry has 15 lines. No architecture smell, layer
violation or file-size issue needs addressing.

### Performance check for Step 1

Readiness reads each metadata file once. Four fixed index keys per candidate
make index construction linear; a visited set bounds graph traversal by nodes
and edges. Marker parsing consumes the expression once. No new quadratic or
sorting-based processing was found, and no environment scan is performed.

The eight-test provider identity module measured 71.86 seconds before and
8.78 seconds after optimization, including fixture setup: an 87.8% reduction.
Reusing imports alone measured 47.73 seconds; profiling then identified repeated
Git subprocesses in the provider-only variants. Subsequent profiled runs,
including fixtures, measured lifecycle 90.99s to 30.17s, commit-plan parity
47.19s to 35.71s, parked waits 39.15s to 8.09s and competing reviewers 16.75s
to 6.61s. All assertions remain; the real boundaries are described above.
Lifecycle setup fell from 83.18s combined to 21.19s; commit-plan setup fell
from 38.17s to 35.44s, with real Git snapshots and adapters still dominating.

The baseline strict total-duration audit found 49 tests above 1.0s among
3,687 passing tests. Setup accounted for 375.09s of 435.46s total phase time
(86.1%). Shared fixtures are charged where setup/teardown actually executes;
collection and pytest interpreter startup are excluded; child-process startup
inside fixtures is included. The round 2 audit measured 348.52s total phases.
The final round 3 audit measured 3,699 passing tests, with 50 above the same
ceiling: 371.5959s total phases, comprising 302.4019s setup, 67.1606s calls and
2.0334s teardown. The earlier 20.0% reduction describes round 2 only.
The largest remaining totals are migration (22.1786s and 16.4098s),
review-status setup (11.2909s), code lifecycle (10.3718s) and the concurrent
request scenario (10.1323s).

Two measured breaches belong to Step 1. The human accepted both as named
live-integration timing exceptions with "Keep live UV generation, publish
round 4", after stored lock fixtures were offered as the alternative:
`tests/acceptance/release_workflow/test_uv_readiness_tdd.py::test_uv_generated_empty_shapes[no-dev-edges]`
at 1.8040s and the same test's `[with-dev-edges]` case at 1.9385s. These are
setup + call + teardown totals from the final round 3 audit. Both keep
their live offline UV invocation and every shape and readiness assertion.
Splitting the old 2.69s combined fixture gave 1.33s and 1.39s in isolation.
Tracing places nearly all their time in Windows creation of the native UV
process, about 0.91s even for `uv --version`; resolution takes 5-11ms.
Explicit interpreter selection, reduced worker pools, removing inherited UV
settings, disabling the console, linking the executable and launching through
cmd did not clear the ceiling. An isolated-environment real lock still took
1.7952s.
The round 3 successful producer totaled 0.5741s.
The missing-engine profile attributes most time to the real isolated launch;
linking the existing interpreter redirector reduced isolated setup from 0.86s
to 0.77s. The round 3 full-audit total was 0.5580s, versus the preceding 5.5625s
measurement. All real process scenarios were below 0.630s in that audit.
The other 48 breaches remain separately inventoried,
as authorized by the human. Raw inventory retains every measured cost; the
two documented UV exceptions do not change the general ceiling or configure
call-only groundhog exclusions. A green call-only speed gate does not prove
total-duration compliance.

Round 7's strict audit measured all 3,702 tests: 319.3208 seconds total,
comprising 270.8953 setup, 47.3753 call and 1.0502 teardown. It retains 45
breaches and the raw global verdict 8. Only the two named live-UV cases breach
Step 1's ceiling: no-dev-edges at 1.1758 seconds and with-dev-edges at 1.1285.
Release process scenarios peak at 0.6166 seconds; role-nature unit tests peak
at 0.0622. All identity tests pass, with the Gemini fixture total at 0.9982.
Evidence: `.reviews/a.release-project-root.step1.tmp.r7.timing/durations.json`
and its `above-one-second.md` inventory.

The other 43 breaches belong to the separately deferred topics. Compared with
round 3, six formerly slow cases are now below the ceiling and one launcher
smoke case is newly above it:
`tests/unit/tools/test_code_reviewer_acceptance/test_code_reviewer_launcher_smoke_tdd.py::test_each_code_review_launcher_reaches_its_public_entry_point[code_review_answer.bat]`
at 1.0092 seconds (1.0083 setup). This remains explicitly inventoried outside
Step 1. The one-second ceiling is not universally met; Step 1 meets its
authorized timing conditions without altering the ceiling or exclusions.
The production retry's maximum total delay is 0.15 seconds per replacement.
No performance issue needs to be addressed for Step 1; the two live-UV totals
are the human's named exceptions.

### Unit test coverage check for Step 1

The configured coverage source is `tools`, with initializers and the existing
listed thin adapters omitted. All four new behavior modules are within that
scope; the round 7 full gate reported 100% coverage, including the authorized
role-nature retry and exhaustion branch. Their dedicated unit
folders exercise publication/failure paths, schema validation, graph traversal,
marker parsing, helper loading and engine dispatch. Property tests cover graph
reachability and version/marker invariants. In-process tests restore import
paths, private modules and bytecode policy after bootstrap checks.

The acceptance processes provide additional behavior evidence, not coverage
credit for child interpreters. Test support lies outside the measured source
scope; its top-level helpers/classes are referenced by fixtures or tests, and
the setup batch adapter is exercised by the process matrix. No unit-tested
production class is below 100% and needs completing. No top-level support
symbol outside the coverage gate is unreferenced.

### Feature integrity for Step 1

Existing metadata regressions and the round 7 whole suite pass. The authorized
boundary repair has fresh full-speed proof, including the identity fixture
that failed after R8. Its historical file holder remains unknown.
With a checkout-local
environment, setup still installs development dependencies and preserves public
tools exports. Readiness leaves consumer files unchanged, does not repair
environments and does not import handlers on failure. The fixture changes
preserve assertions, durable protocol evidence and the explicit process/Git
boundary scenarios. Successful no-environment and global setup again finish
without publishing an unusable release identity; local producer failures still
fail. Checkout-local classification now uses matching lexical forms, with
physical containment still checked before publication. Producer regressions
cover alias success and physical escape failure. Steps 2 through 6 remain
pending.

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
