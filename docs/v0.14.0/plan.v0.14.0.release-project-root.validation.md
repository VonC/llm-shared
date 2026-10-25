# v0.14.0 release-project-root implementation tracking and validation

No, it is not implemented.

This document tracks the six steps of the [implementation plan](plan.v0.14.0.release-project-root.md).
Step 1's round 7 boundary repair passes the full speed day, final static checks
and strict duration assessment with the human's two named live-UV exceptions.
The one-second total-duration audit remains separate from
groundhog's call-only speed gate. Step 2's controlled Git and physical-path
services, including the Round 1 boundary repairs, pass the replacement full
speed day and static implementation check. Step 3's strict configuration and
schema registration pass the full speed gate after the family-instance repair.
Step 4's managed writes, artifact capabilities and operation ownership pass the
repaired full speed gate. Steps 5 and 6, including the public caller matrix and
rollout, remain pending.

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

Yes. Step 2 has been fully implemented.

The pinned Git adapter, copied environment policy, configuration origin/scope
checks and physical project/path validation are in place, with dedicated unit
suites and real Windows repository/junction cases. Round 2 repairs all three
boundary gaps found in Round 1: binary capture with explicit decoding retains
every configuration record, Windows stream redirects are removed, and the own
`.git` entry is rejected by filesystem identity, including linked gitfiles.
Regression-first evidence reproduced the defects; the repaired whole-suite
speed day passes 3,866 tests with 100% coverage and no outliers or exclusions.
The static implementation check confirms the planned Step 2 boundaries.

### Goal for Step 2

Keep every operation on the validated worktree using one eligible Git executable, controlled routing and physical containment.

### Step 2 improvement expectations

- Stale inherited routing cannot redirect explicit project selection or index operations.
- Equivalent roots and linked-worktree metadata are handled correctly; managed paths reject external or nested repositories.
- Compatible identity, signing, credentials and parent-shell settings are preserved.
- Every listed routing key permits only local/worktree scope; surviving command-scope entries fail, with key/origin/scope evidence.

### What was implemented for Step 2

- `tools/release_workflow/git_environment.py` copies the caller environment
  into a read-only mapping, removes the enumerated routing/injection/execution
  inputs, sets explicit output/interaction policy and retains compatible user
  settings. NUL-delimited configuration records retain their scope and origin;
  all surviving command-scope entries and externally scoped routing keys fail.
- `tools/release_workflow/git.py` pins the first eligible absolute `git.exe`
  outside the original physical cwd, verifies Git 2.31.0 or newer and retains
  the selected executable without fallback. Every child uses native arguments,
  an explicit absolute cwd and the copied environment. Original child status,
  stdout and stderr remain attached to failures. Configuration is inspected
  before internal output overrides; even an empty `GIT_CONFIG` selector is
  rejected because it hides the effective configuration chain. Binary streams
  are decoded on the caller thread; missing streams fail with the command.
  Configuration, diagnostics and failed-command output decode losslessly;
  successful ordinary output must be valid UTF-8.
- `tools/release_workflow/paths.py` separates worktree, per-worktree Git and
  common directory identities. Explicit and discovered roots share physical
  validation. Managed destinations check both original and resolved ancestor
  chains, including future paths, nested repositories, gitfiles, bare metadata,
  external junctions and non-directory ancestors. No sibling scan or Git call
  per ancestor is introduced. The worktree's own `.git` entry is rejected by
  filesystem identity as a target or ancestor, for directories and gitfiles.
- Dedicated `test_git`, `test_git_environment` and `test_paths` suites cover
  selection, environment/configuration matrices, retained failures, malformed
  metadata and filesystem faults. Real A/B, linked/nested repository and
  directory-junction fixtures complement in-process normalization properties.
- Test support reuses minimal real repositories and a verified native Git
  executable. Read-only matrices share setup; mutation cases stay isolated.
  Automatic xdist selection is capped at four while explicit overrides remain.
  Existing scope/documentation tests reuse only stable paths or read-only
  contents. Named property tests retain their strategies/assertions with
  bounded example counts and explicit boundary cases.
- The immediate-discovery expiry fixture injects notifications and asserts
  that no wait occurs, avoiding its native shutdown hang while preserving real
  publication, discovery, expiry and ownership. Native watcher acceptance is
  retained. Historical transcript formatting is mechanical; protocol publication
  also appends the Step 2 requests, findings and writer responses.
- Real cp1252 tests retain benign values and reject external routing despite a
  legacy byte. Unit tests cover missing streams, strict metadata decoding and
  lossless failure output. All three `GIT_REDIRECT_*` controls are removed,
  including case variants, without changing the parent environment. Linked
  worktree tests reject `.git` targets and descendants.

### New types or classes introduced for Step 2

- `GitEnvironment`: immutable child environment and ignored-input diagnostics.
- `ConfigEntry`: effective configuration scope, origin, key and optional value.
- `GitPolicyError`: failed selection, policy or machine-output validation.
- `GitExecutionContext`: pinned executable/version, environment, original cwd
  and interaction policy, owning the subprocess boundary.
- `GitCommandError`: policy failure retaining the unmodified child result.
- `ProjectIdentity`: physical worktree, Git and common directories plus the
  supplied root spelling.
- `ProjectPathError`: invalid project identity or managed destination.
- Test-only `GitSandbox` builds real repository/junction evidence;
  `RecordingGit` observes arguments and process policy in unit tests.

### Architecture check for Step 2

Environment/configuration policy is independent of process execution. The Git
adapter owns the sole production subprocess boundary; physical path services
consume that context and filesystem identities. The package initializer stays
dependency-free. No domain behavior or release mutation is introduced, and the
existing cross-platform Git helper and its regression test are unchanged.

Physical-line counts are 159 for `git.py`, 130 for `git_environment.py`, 160 for
`paths.py` and 8 for the package initializer. New test/support files range from
3 to 190 lines, including the 94-line Git helper, 63-line routing fixtures and
54-line path fixtures. The existing instruction-structure test shrinks to 648
lines, within its existing risk band and below the 650-line ceiling; its new
28-line fixture lives separately. Other changed Python files remain below 550,
and initializers below 30. No inappropriate layer dependency or required
responsibility split was found.

No, there is nothing that needs to be addressed in the Step 2 architecture.

### Performance check for Step 2

Environment copying and configuration parsing traverse their inputs once.
Executable selection visits eligible PATH entries in order. Root validation
uses one configuration inspection and one metadata probe; alias discovery
reuses that metadata. Path authorization makes two ancestor walks with bounded
metadata checks per ancestor, independent of unrelated worktree size. It adds
no sorting or pairwise search. Path construction/resolution still incurs the
normal platform cost for the supplied path length.

The completed `ghog day --full=speed --whole-suite` ended on
2026-10-24T18:17:42+02:00 with exit 0 and speed proof: static checks 1m23.7s,
affected tests 18.0s, full 3,866 passed with 100% coverage in 3m12.0s, zero
failures/warnings/xfails, zero call outliers and zero exclusions. Maximum call
was 0.6740s. Coverage and durations came from that same full execution; no
second timings traversal followed. The separate shared-tooling repair is not
part of this step's staged source.

The same-run setup/call/teardown inventory records 67 totals above one second.
That diagnostic does not pass a one-second total-duration ceiling and is not
substituted for the plan's call-only gate. The 36 path cases sum to 5.2901s
setup, 8.5492s call and 0.0418s teardown (13.8811s worker time, not wall time).
The largest suite total is a legacy migration case at 30.2061s, including
30.2035s setup. Private writer evidence retains the complete phase inventory.

Profiled Round 2 outliers were the explicit outside-Git call at 1.08s, then
four routing calls at 1.06s to 1.28s and the diagram check at 1.26s. Native Git
startup/capture and real file reads dominated their isolated profiles. Fixtures
now retain actual exceptions, identity/configuration results and diagram texts;
every assertion and parameter remains. Final outside-Git setup/call/total is
0.6836/0.0012/0.6858s, repository-owned routing 0.8397/0.0011/0.8419s, and the
diagram check 0.0050/0.0030/0.0087s. The three named include cases have setup
0.3180s to 0.3345s, calls about 0.001s and totals 0.3202s to 0.3369s.
The shared fixture also retains all six include-test parameters. Moving these
operations into setup does not itself demonstrate lower total runtime. The
four-worker full meets the call gate and five-minute phase bound; no causal
overall speedup is inferred from run-to-run timing differences.

No, there is no Step 2 performance issue that needs to be addressed under the
current plan's gate.

### Unit test coverage check for Step 2

`pyproject.toml` configures coverage source as `["tools"]`. The completed
whole-suite gate reports 100% for that measured source. Static inspection of
the module-named unit folders confirms selection/version/error branches,
environment and scope matrices, explicit/discovered identities, ancestor
boundaries and filesystem failures are exercised. The unchanged legacy Git
helper retains its dedicated unit test. Real subprocess evidence supplements
these tests; child-process execution is not claimed as coverage.

Files under `tests/` are outside that percentage. Static reference inspection
confirms `GitSandbox`, `create_template` and `copy_template` feed the real Git
fixtures; `RecordingGit` is used by adapter tests. New path/index fixtures,
the proven-scope and published-capture fixtures, and existing expiry helpers
are requested by tests. New routing fixtures feed the config assertions;
`explicit_outside_git` and `diagram_file_texts` feed their named tests. The
worker-count function is a registered pytest hook;
test functions and fixtures are discovered by pytest. All other changed
top-level helpers are referenced within their test package. The reduced PBT
budgets retain assertions and add explicit shortest/deepest, dense/cyclic,
Unicode, duplicate and maximum-size cases.

No, no unit-tested class below 100% needs completing.
No, no top-level symbol outside the coverage gate is unreferenced.

### Feature integrity for Step 2

Explicit B remains B under stale A routing, including a distinct inherited
index. Compatible identity/signing/credential settings and selected benign
configuration files survive; the parent mapping is unchanged. Linked metadata
may live outside the worktree while managed destinations cannot cross foreign
repository or physical boundaries. Original inputs and child failures remain
available for diagnostics. Legacy configuration bytes cannot empty the scope
check; missing streams fail explicitly, stream redirects cannot hide output,
and linked `.git` gitfiles are not authorized managed destinations.

The fixture repair does not claim to fix the production Windows watchdog
shutdown race. Timing data and gate/reporting information remain available,
but covered parallel measurements are not numerically equivalent to the old
uninstrumented sequential timings. No Step 2 commit has been made.

Real directory-junction evidence is present. The file-symlink capability probe
failed with Windows privilege error 1314; real configuration-file symlink
evidence remains pending for Step 4 and whole-topic acceptance. Steps 3 through
6 retain their configuration, write-boundary, caller and rollout work. R9 stays
unresolved and nonblocking for review as directed by the user.

## Step 3. Strict configuration and domain schema registration

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The strict loader, explicit shipped registry, value provenance, managed-path
checks and fail-closed tooling minimum are implemented and tested. The round 1
family-instance gap is repaired: empty, blank and whitespace-padded instances
fail with file and section context, including duplicate-looking declarations.
Internal whitespace and exact fixed-section lookup remain valid.

### Goal for Step 3

Parse optional project configuration strictly with domain-owned schemas and a fail-closed tooling minimum gate.

### Step 3 improvement expectations

- Missing configuration uses defaults; invalid declarations never do.
- All declarations are checked without importing consumer code or scanning schema files.
- Any declared minimum tooling version fails until the later comparator exists; malformed syntax is diagnosed.
- The interim minimum syntax is exactly a release `MAJOR.MINOR.PATCH` without a `v` prefix.

### What was implemented for Step 3

- `configuration.py` reads only the selected project's `.release.ini`, once,
  using UTF-8 with one optional leading BOM. Strict INI rejects malformed and
  duplicate declarations, disables interpolation and DEFAULT inheritance, and
  preserves literal regex, percent, dollar, quotes and inline comment text.
- Missing files permit schema defaults. Read/encoding errors, dangling or
  disappearing targets, unknown sections/keys, invalid values and required
  values without defaults raise status-2 errors. Supplied/defaulted values keep
  their file, section, key and original text in immutable mappings.
- Family instances reject leading and trailing whitespace without normalizing
  names. Regression cases cover empty, space-only and tab-only instances,
  padding on either end, and each spelling beside an existing declaration.
  They verify status 2, source/section diagnostics, no new files and unchanged
  input. Positive controls preserve internal spaces and exact fixed names.
- `schemas.py` composes explicit domain declarations, indexes fixed and
  prefix-family ownership, rejects overlaps and missing/substituted shipped
  schemas, and invokes every owner's cross-section validator. Production ships
  only `tooling`; tests supply synthetic domains without filesystem discovery
  or consumer imports.
- Managed paths use Step 2's physical authorization boundary without creating
  targets. Any declared `minimum-version` is checked before domain validation:
  ASCII release `MAJOR.MINOR.PATCH` is required, and valid declarations fail
  with compatibility-unavailable status 2 until item 6 supplies comparison.
- TDD and PBT cover strict input, literal preservation, defaults/provenance,
  ownership/completeness, families, all-owner validation and read-only failure.
  Separate `test_configuration` and `test_schemas` leaves keep each unit-test
  folder aligned with one production module. The package initializer remains
  lazy and changes only its description.
- The first replacement full run lost a worker in the existing physical-root
  alias test. A focused run passed; profiling found unrelated shared setup
  dominated its cost. That case now creates its own single real junction,
  retaining real Git, both filesystem assertions and its ten-second timeout.
  Setup plus call fell from 1.85 to 0.47 seconds in the focused measurement.
  The shared path fixture no longer creates the alias it does not use.
- Writer gate: `ghog day --full=speed --whole-suite` completed on
  2026-10-25 at 00:28:46 +02:00 with exit 0, 3,946 full-suite tests, no failures
  or xfails, two warnings, 100% measured coverage, zero duration outliers and
  zero exclusions. Groundhog status confirmed completion and `proof=speed`.
  No exclusion was added or baseline raised. This implementation check used
  that evidence and static inspection without rerunning tests.
- The plan's `rg -n 'ConfigParser|interpolation|minimum-version|importlib|exec\(' tools/release_workflow`
  inspection finds one strict parser with interpolation disabled, the minimum
  gate and only the existing bootstrap imports. It finds no consumer import,
  schema discovery or execution of project configuration.

### New types or classes introduced for Step 3

- `ValueRule`, `SectionSchema` and `DomainSchema` declare conversions, defaults,
  managed-path roles, section ownership and whole-configuration validation.
- `RegisteredSection`, `_OwnershipNode` and `SchemaRegistry` retain indexed
  rules, detect ownership conflicts and verify the complete shipped manifest.
- `ConfigValue` and `ConfigSections` describe validated values with provenance;
  `Configuration` retains their immutable section mappings and source path.
- `SchemaError` and `ConfigurationError` identify status-2 composition and
  project-input failures respectively.

### Architecture check for Step 3

Schema declarations and ownership are separate from the INI adapter. Domain
converters and validators are shipped callables; project content selects only
data. The loader uses the existing physical-path service and neither imports
consumer code nor prepares artifacts. No future domain implementation, upgrade
comparator or command wiring is introduced by this step.

Line counts are within the 650-line ceiling: new `schemas.py` 196 and
`configuration.py` 160; configuration TDD/PBT 256/54; schema TDD/PBT 90/28;
both new test initializers 3. All have baseline 0. The existing package
initializer grows from 8 to 9 lines, below its under-30 advisory band.

No, there is nothing that needs to be addressed.

### Performance check for Step 3

The loader performs one file read, parses each declaration once and converts
each supplied or defaulted value once. A 64-rule operation-count test verifies
the read and conversion bounds. Hash maps index domain names and keys; a trie
checks section ownership and resolves families in time linear in their name
lengths. There is no pairwise prefix scan or sorting. Whole-config callbacks
run once per registered owner, and managed values reuse Step 2's path checks.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

The configured coverage source is `tools`; both new production modules are
inside it. `test_configuration` targets `configuration.py`, and `test_schemas`
targets `schemas.py`, with TDD and PBT in each leaf. Static review accounts for
every loader helper and schema type through those tests or their package
callers, including read failures, duplicate ownership in both orders, empty
or padded family instances, missing required values, immutable section access, managed
path rejection and domain validation errors. The writer's full coverage gate
reports 100% for its measured source scope.

Initializers are excluded by the coverage configuration and contain only
documentation. Test helpers are referenced by the collected tests; no new
executable production symbol lies outside the measured source scope.

No, there is no unit-tested class below 100% that needs completing.
No, there is no unreferenced top-level symbol outside the coverage gate.

### Feature integrity for Step 3

The full 3,946-test suite passes. Existing runtime readiness, Git isolation,
physical path handling and review-artifact formats remain intact. Configuration
loading and its failures create no files or directories and perform no
migration. Public dispatch wiring remains in its planned Step 5 scope.
The family-instance gap is covered by rejecting ambiguous declarations while
preserving valid names. Steps 4-6 are still pending, so the document-level
status remains No.

## Step 4. Managed writes, artifact capabilities and operation ownership

### Analysis of Step 4 implementation state

Yes. Step 4 has been fully implemented.

Managed writes, separate artifact capabilities and durable operation ownership
are implemented and pass the repaired full speed gate. The optional
`validate_home` callback runs after lexical rejection and before physical
resolution. The transition mutex waits up to one second for a brief contender
record check, preserving owner release, retention and transfer. The plan now
records the helper seam and measured line counts as a Step 4 implementation
adjustment; the requirement and design remain unchanged.

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

- `managed_files.py` retains lexical and physical destination authorization,
  revalidates at mutation boundaries and publishes flushed same-parent
  temporaries atomically. Failure cleanup checks ownership of its temporary.
- `artifacts.py` separates read-only declarations from prepared capabilities.
  The existing helper owns parsing, exact ignore bytes and rollback. Its new
  optional `validate_home` callback lets the release adapter authorize the
  original path after lexical checks, before normalization, and retain it
  through preparation. Invalid spellings cannot trigger consumer probes.
- `windows_process.py` queries native PID and creation time, distinguishing
  dead processes from unknown identity and PID reuse. `operation_lock.py`
  flushes complete versioned records before non-replacing publication, uses
  a project mutex with a bounded transition wait and retains ownership through handoffs.
  Recovery requires an exact dead owner without retained ownership; malformed
  records and unknown versions fail conservatively with diagnostic context.
- TDD covers containment, aliases, tracking, rollback, write failures, native
  process identity, contention and retained transfer. A property test checks
  ownership transitions against an independent state model. The two lexical
  alias regressions failed before the repair and pass afterward. Sixteen
  callback-ordering and mutex-contention checks also failed before repair and
  now pass. Native contention checks synchronize on actual mutex contention
  without sleeps; all three owner transitions are covered.

The resolved `ghog day --full=speed --whole-suite` passed compile, lint,
complexity, affected, full coverage and timing gates after the repairs, with
4,036 tests, `exit=0`, `fail=0`, `warn=2`, `cov=100`, `outliers=0`,
`excluded=0`, `proof=speed` and `reused=none`. `ghog status` confirmed
`state=done` and `exit=0` at `2026-10-25T20:40:22+01:00`.

### New types or classes introduced for Step 4

`ManagedTarget`, `ArtifactDeclaration`, `PreparedArtifacts`, `ProcessIdentity`,
`ProcessState`, `OperationLock`, `RetainedOwnership` and their typed errors
separate path, artifact, process and operation responsibilities.

### Architecture check for Step 4

Path authorization, artifact policy, operation state and Windows interrogation
have separate responsibilities. The artifact helper accepts an optional
consumer callback and does not import release services. Parsing, ignore policy
and rollback remain single-sourced. Domains retain transaction ordering and
must revalidate mutable state after acquiring ownership. The write-boundary
inspection finds project writes behind managed services; runtime setup writes
retain their separate tooling boundary.

The callback is the narrow helper seam that the amended Step 4 checkpoint
records: the helper grows from 184 to 197 lines and its existing test leaf from
218 to 261, preserving legacy behavior for callers that omit it. Without this seam,
the adapter loses lexical repository boundaries or must duplicate parsing.
New source files have 123/133/233/132 lines; new TDD/PBT leaves have
226/140/285/97/92 lines, and test initializers have 3 each. The package
initializer grows from 9 to 10 lines. All remain below the 650-line ceiling.

The plan's file list, implementation text, baseline table, Step 4 checkpoint
and implementation decisions now record this integration seam. The amendment
claims no separate human agreement; the human accepts or rejects it at the
Step 4 commit gate, which commits the plan change with this validation.

No, there is nothing that needs to be addressed.

### Performance check for Step 4

Checks visit affected ancestors, JSON fields and fixed native API calls without
tree scans or sorting. No new quadratic or n-log-n processing was introduced.
The first repaired speed run flagged the lock property test at 1.25 seconds.
Profiling identified repeated native filesystem checks and lock-record I/O;
bounding generated traces from 15 to 6 reduced isolated profiled time from
0.939 to 0.366 seconds. Strategy bounds, the explicit lifecycle, independent
state model and all assertions are preserved. The final full speed gate has
zero outliers and exclusions; no duration floor or baseline was raised.
No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 4

The configured source scope is `tools`, including all four new source modules
and the modified artifact helper. The full gate reports 100% line coverage.
Each new module has its own unit-test folder; the existing helper leaf adds
default/configured callback and rejection coverage. Static inspection accounts
for all executable helpers through these tests or internal callers, including
error translation, strict record decoding and owned cleanup. Initializers are
excluded from the gate and contain only documentation.

Real directory-junction regressions prove rejection of nested aliases returning
inside the project and internal aliases repointed before preparation. Native
file-symlink creation is unavailable here (Windows error 1314); its test skips
only that capability error, with a separate deterministic resolved-target
rejection test. No native file-symlink execution evidence is claimed. Native
process and mutex tests passed.

No, there is no unit-tested class below 100% that needs completing.
No, there is no unreferenced top-level symbol outside the coverage gate.

### Feature integrity for Step 4

Existing artifact-configuration regressions pass with the optional callback
omitted. Read-only resolution and rejected paths leave artifacts unchanged and
do not migrate legacy files. Tests preserve original bytes and ownership on
failed writes and transitions. No existing feature or reporting regression is
identified. An owner's cleanup or handoff now tolerates brief contention;
a mutex still busy after the bound fails visibly and conservatively. Launcher
composition and cross-process acceptance remain in their planned Steps 5 and
6, so the document-level status remains No.

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
