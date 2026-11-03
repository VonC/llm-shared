# Specification review transcript for v0.14.0

- Exchange: specification/plan/v0.14.0/release-project-root
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor

- Recorded: 2026-10-21T17:27:58+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: unrecorded
- Outcome: request

### Review identity for plan release-project-root (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Review round: 1

### Requestor assessment for plan release-project-root (round 1)

The writer found no missing implementation questions after reviewing the current
source and test trees, the approved requirement/design and the six-step plan.
There are no question options or human answers to preserve in this new plan.
The writer's settled assessment is not independent review or authorization to
implement. No reviewer wording suggestions have yet been received.

Please assess the whole plain plan for missing questions and implementation
risks without reopening the 14 settled design decisions. In particular, examine
the setup-produced runtime identity and pre-package bootstrap import sequence,
strict lock-graph/marker readiness, pinned Git origin/scope checks, artifact
read/write separation, retained operation ownership and real Windows transport
and cancellation evidence. Confirm the split between foundation proof and later
umbrella integration, including AC11's disposable caller fixture.

The six-step validation skeleton is aligned and intentionally unchecked; it is
context, not a second reviewed specification. The four authored documents passed
Markdown lint, a configured sensitive-content scan reported zero matches, and
the path inventory and all 36 placeholder check sections were verified. No
implementation or application tests were performed in this planning task.

### Change summary for plan release-project-root (round 1)

Created the implementation plan and matching six-step validation skeleton in the
selected docs/v0.14.0 effort directory. Added aligned file-based IO clarification
sections to the requirement and design without changing their settled behavior.
Recorded physical-line baselines, Python ceiling policy, tests-first work,
package initializers, shared groundhog commands and final subprocess acceptance.
The writer assessment raises no questions and remains subject to independent
review. All source and evidence references in authored content are relative.

### Writer response for plan release-project-root (round 1)

Writer response:

Initial round: no reviewer feedback has been received. The requestor will assess
and apply accepted implementation-plan feedback, keep the validation skeleton
aligned if steps change, and preserve the existing requirement/design decisions.
No private terms, machine-specific paths or confidential fixtures are necessary.

Keep all public transcript references repository-relative. Absolute identity paths
belong only in the private protocol request and answer envelopes; omit them from
the substantive transcript summary and any authored evidence examples.

### Reviewer focus for plan release-project-root (round 1)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `claude`

Completed artifacts:

- `.reviews/a.review-active.specification.plan.v0.14.0.release-project-root.md`
- `.reviews/a.review-requested.plan.v0.14.0.release-project-root.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer

- Recorded: 2026-10-21T17:46:15+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan release-project-root round 1

#### Identity and scope check for plan release-project-root (round 1)

The working-tree plan has SHA-256
`40d8363fb2dce78743056691b40e2bd853a47d6dc8cae55988c505a1761b2d2a` (723
lines). I assessed it against the consolidated design and the requirement,
including their uncommitted file-based IO clarification sections, which add no
behavior. The validation skeleton was read as context only. The 14 design
decisions stay settled, and nothing below reopens them.

#### Facts verified against the tree for plan release-project-root (round 1)

- All 18 physical-line baselines match the gate metric. The design and
  requirement baselines (706 and 353) match `HEAD`, before the IO sections.
- `senv.bat` sets `PYTHON_BIG_FILE_LINE_LIMIT=650` (the standalone checker
  defaults to 700). `.gitignore` ignores `venvs/`, and `uv.lock` uses
  `filter=uv-lock-public`.
- `import tools` loads 26 `tools` modules and no third-party module, in about
  165 ms with bytecode writes off.
- Under `python -I`, a script's own directory is not on `sys.path`:
  `sys.path[0]` is the standard-library zip.
- `ReviewArtifactConfiguration.load` defaults its tracking callback to bare
  `git ls-files`. `prepare_home` creates the home with `mkdir(parents=True)`
  and writes the `*` ignore file.
- `senv.bat` calls `switchpy` at lines 271 to 273 without checking its status.
  `switchpy` lives outside the repository and returns `exit /b 1` on failure.
- pytest-cov 7.1.0 is locked. pytest-cov 7 dropped subprocess measurement, no
  coverage `patch` option is configured, and `pyproject.toml` requires 100%
  coverage of `tools`.
- The lock has format `version = 1`, its only markers today are
  `sys_platform == 'win32'` and `os_name == 'nt'`, and the root's
  `[package.metadata.requires-dev]` records each group's declared requirements.
- `README.md` says it "stays the at-a-glance tour; the wiki is where to go
  deeper". `wiki/reference/aliases-and-launchers.md` and
  `wiki/reference/automation-and-direct-invocation.md` already exist.
- On this French-locale host, `chcp` prints `Page de codes active : 65001`.

#### What the plan gets right for plan release-project-root (round 1)

The six steps follow the design's dependencies: runtime production before its
consumers, Git and path identity before configuration and artifacts, and real
launchers only once the services exist. Files, test leaves, budgets and rg
checks are concrete. The plan leaves the old Git helper, the artifact parser
and the package initializers unchanged, avoids the `artifact_path`
conveniences and keeps item 2 to 8 behavior out. Its acceptance ownership map
is the right place for the foundation versus later-integration split.

#### Gaps that block implementation for plan release-project-root (round 1)

1. Runtime identity and import order: the plan forbids entering
   `tools/__init__.py` before readiness but never says how `bootstrap.py`
   loads its sibling helpers, which `-I` puts out of reach. After readiness,
   `import tools.release_workflow.cli` does run that initializer, and nothing
   keeps its import closure inside the release group. The `senv.bat` producer
   has no feasible test harness.
2. Lock-graph and marker readiness: "the lock's supported marker grammar" is
   circular. Extras, same-name packages with several versions, lock format
   versions, smudged registry URLs and what readiness reads from
   `pyproject.toml` are unstated.
3. Pinned Git checks: the routing keys and accepted configuration scopes are
   not a closed set, so the table-driven test has no finite list.
4. Artifact separation: `prepare_artifacts` would reimplement `prepare_home`,
   copying the ignore-coverage policy the design says to reuse.
5. Operation ownership: a create-then-write lock can leave an empty or partial
   owner record after a crash. The conservative rule then blocks the project,
   and its recovery waits for item 5.
6. Real Windows transport: no console harness is named, cancellation outcomes
   are not stated per route, the launcher-to-bootstrap entry protocol is
   missing, and the required `chcp 65001` is not addressed.
7. Test architecture: per-call real launchers, Windows PowerShell 5.1 and
   fresh repositories will cross groundhog's one-second outlier floor. Child
   processes do not count toward the 100% gate. And launching the actual
   production launchers with test-only handlers needs a stated mechanism that
   is not a production plugin path.
8. Foundation versus later integration: the requirement's legacy-location
   sentence and its `PRJ_DIR_NAME` rule appear in neither the design nor the
   plan. The AC11 fixture proves only its own script. README-only guidance
   contradicts the README's stated role.

Disposition: changes requested. Each gap has a recommended resolution in the
requested changes, and none needs a new design decision.

### Question verdicts for plan release-project-root round 1

#### Verdicts on the plan questions for plan release-project-root (round 1)

| Item | Reviewer verdict |
| --- | --- |
| Questions in the plan | None, and none is missing that needs the human: every gap is plan-level and the approved design settles it |
| Writer's "no open questions" assessment | Agree that no design decision is reopened. Disagree that implementation can proceed as written, for the reasons in the requested changes |
| The 14 settled design decisions | Not reopened. Every requested change stays inside them |
| Possible escalation | Only if the writer prefers a shipped read-only foundation command over a harness tooling copy for transport acceptance (change 7). That adds public surface, so it would need a question for the human. I would choose the harness copy |

### Requested changes for plan release-project-root round 1

Requested changes:

#### Required plan changes before round 2 for plan release-project-root (round 1)

1. Steps 1 and 5, bootstrap import order. State how the bootstrap loads its
   helpers before the gate. Recommended: `bootstrap.py` derives the paths of
   `runtime_identity.py`, `readiness.py` and `markers.py` from its own
   `__file__` and loads them with `importlib.util.spec_from_file_location`
   under private names. Only after readiness passes does it insert the
   checkout root into `sys.path` and import `tools.release_workflow.cli`.
   Say plainly that this import runs `tools/__init__.py` (26 modules today,
   standard library only). Add two tests: `tools` stays absent from
   `sys.modules` until readiness passes, including on failure; and the
   engine's import closure loads no third-party distribution outside the
   release closure. Without the second test, a future eager import in
   `tools/__init__.py` silently becomes an undeclared release dependency, and
   the design's "development-only package missing: pass" row breaks.
2. Step 1, setup producer harness. `senv.bat` ignores the status of
   `switchpy` today, and a test cannot run the full `senv.bat` without machine
   setup and the external `switchpy`. Plan a small entry that `senv.bat` calls
   right after `call switchpy`, passing the saved status before `popd` and
   macro restoration. The entry runs the producer through the interpreter
   that activation just made, by absolute path (for example
   `%VIRTUAL_ENV%\Scripts\python.exe -I -X utf8`), never through a bare
   `python` lookup, and publishes nothing on a nonzero status. List the entry
   in Step 1's files, test it against a fake prepared environment, and add one
   recorded fresh-setup run to the Step 1 validation evidence.
3. Step 1, closed lock and marker contract:
   - markers: list the supported variables and operators. Cover at least
     `sys_platform`, `os_name`, `platform_system`, `platform_machine`,
     `implementation_name`, `python_version` and `python_full_version`, with
     `==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not in`, `and`, `or` and
     parentheses. Anything else, `extra` included, fails closed, naming the
     package and the marker;
   - lock shape: accept format `version = 1` and fail closed on any other,
     without keying on `revision`. Resolve a same-name dependency by its
     `version` and `source` keys, failing closed when that stays ambiguous,
     and state the rule for `extra` lists on dependency entries;
   - sources: compare names and versions only, never registry URLs. Test both
     the clean committed lock and a working-tree copy that the
     `uv-lock-public` filter has rewritten;
   - `pyproject.toml`: state what readiness reads from it. Recommended: the
     interpreter requirement, the existence of the `release` group and its
     inclusion by `dev`. A repository test, not runtime PEP 508 parsing,
     proves that the lock's `requires-dev.release` matches
     `[dependency-groups].release`.
4. Step 2, closed Git configuration check. List the routing keys rejected
   outside the repository's own configuration (at least `core.worktree`).
   List the accepted scopes, `local` and `worktree`. Any `command`-scope entry
   that survives the environment cleanup fails.
5. Step 4, artifact preparation. Once the managed service has revalidated the
   home's existing ancestors, reuse `ReviewArtifactConfiguration.prepare_home()`.
   Then revalidate the prepared home physically before creating the lock. This
   keeps the `*` ignore bytes, the existing-home validation and the rollback in
   one place. If the plan keeps a reimplementation, state why and how the
   policy stays single-sourced. State the public status for a
   `ReviewExchangeError` raised during loading and during preparation.
6. Step 4, lock record integrity. Write the complete, versioned owner record to
   a same-directory temporary file. Publish it with a non-replacing rename; on
   Windows, `os.rename` fails when the target exists. A crash then cannot leave
   an empty or partial owner record behind. Test a leftover temporary file and
   an unknown record version. Until item 5 provides recovery, the diagnostic
   for an unverifiable owner names the lock path and its owner fields, so a
   human can decide to remove the lock deliberately.
7. Steps 5 and 6, test handlers behind real launchers. Name how a test-only
   handler reaches a real launcher's child process without a production
   plugin path. Recommended: a session-scoped tooling copy that differs from
   the shipped tree only by a harness-generated handler module and registry
   entry, verified by comparing the two trees. The unmodified checkout's
   launcher proves the same names are rejected. No environment variable,
   argument, consumer file or import path may add a handler.
8. All steps, coverage and test duration:
   - coverage: in-process tests cover every `tools/release_workflow` line.
     `bootstrap.py` and `cli.py` expose `main(argv, ...)` with injected process
     state. Their `__main__` guard follows the repository's existing
     `# pragma: no cover - thin launcher boundary` or `runpy` pattern, and
     in-process bootstrap tests restore `sys.path`, `sys.modules` and
     `sys.dont_write_bytecode`. Launcher and acceptance child processes are
     behavior evidence, not coverage;
   - duration: every test call stays under groundhog's one-second outlier
     floor, without `ghog exclude`. Build repositories A, B, linked and nested
     once per session and copy them for each test. Create the tooling copy and
     its own `venv --without-pip` environment once. Run each caller family's
     case matrix in a single Windows PowerShell 5.1 or cmd invocation inside a
     fixture, and assert each case in its own fast test call. Keep PBT
     in-process, and keep the set of spawned processes small and fixed;
   - links: use directory junctions, which need no privilege. State what the
     file-symlink cases do on a host without Developer Mode or elevation.
9. Steps 5 and 6, console and cancellation evidence. Name the harness: a
   pseudo console (`CreatePseudoConsole` through ctypes, or a pinned dev-only
   test dependency) that hosts cmd, accepts doskey input and delivers Ctrl+C.
   State the expected outcomes:
   - batch routes show `Terminate batch job (Y/N)?`;
   - after Y, the run ends without a final diagnostic;
   - after N, the launcher returns status 1 with a stderr diagnostic;
   - the native route returns 1 with a diagnostic;
   - redirected stdin never prompts.

   State that Steps 5 and 6 cannot be marked complete while any supported
   caller lacks evidence, since the design makes approval wait for it.
10. Step 5, launcher contract. Add:
    - the launcher-to-bootstrap entry protocol: how each launcher marks
      explicit or alias entry and batch origin. Batch-grammar rejection then
      applies only to arguments that came through batch, and a native caller
      cannot fall into alias discovery;
    - the pre-Python failure branch: a missing or unreadable record, or a
      missing interpreter, prints a stderr diagnostic and returns 2 without
      trying any other Python;
    - `chcp 65001` for the run, as the requirement says. Restore the prior
      code page from the digits after the last colon of the localized `chcp`
      output (this host prints `Page de codes active : 65001`), and treat a
      failed `chcp`, as with no console, as no error;
    - ASCII-only launcher files. Any colored output comes from the launcher's
      own checkout, never an inherited `LLM_SHARED_DIR`.
11. Requirement traceability. Cover the requirement's legacy-location and
    project-name sentences, which the design does not mention.
    `InvocationContext` exposes the validated root in Windows and POSIX forms,
    the root-relative locations behind `VERSION_TXT_FILE`, `POM_FILE`,
    `PACKAGE_JSON_FILE`, `HEADER_CHANGELOG_FILE`, `DEV_WORKFLOW_DIR` and
    `PRJ_DIR_unix`, and the project name derived from the root. The engine sets
    none of these variables in any child environment, and tests show that
    inherited values of them and of `PRJ_DIR_NAME` change no result. Add the
    row to the acceptance ownership map and leave their domain use to items 2
    to 4.
12. Step 6, AC11 fixture. Say what the fixture proves about shipped code: the
    adapter detects a missing launcher by file absence before any call, so an
    installed launcher that returns 1 or 2 is never treated as missing. The
    design forbids hiding an execution failure behind this exception. Add
    that case. Label the fixture's argument scan as a reference for items 5
    and 8, and say in the ownership map that AC11's production behavior stays
    unproven until item 5.
13. Step 6, documentation placement. Put the detailed guidance in
    `wiki/reference/aliases-and-launchers.md` and
    `wiki/reference/automation-and-direct-invocation.md`, adding a how-to page
    if needed. Keep `README.md` to a short pointer, as its own text says. Add
    these files to Step 6.

#### Wording to fix in the same revision for plan release-project-root (round 1)

- **14.** Step 3 rg check: `exec\\(` is an unclosed regex group when pasted into a
    single-quoted PowerShell argument. Use `exec\(`.
- **15.** Step 5: `call .\\release_workflow.bat` shows a doubled backslash in its
    code span. Use `call .\release_workflow.bat`.
- **16.** Step 6 test leaves: follow the `test_name/test_name_tdd.py` convention with
    `test_release_transport/test_release_transport_tdd.py` and
    `test_release_locking/test_release_locking_tdd.py`, each with its own
    `__init__.py`.
- **17.** Step 3: replace "agreed version form" with "a release version
    `MAJOR.MINOR.PATCH` without a `v` prefix, as in the umbrella's `[tooling]`
    example; anything else is malformed".
- **18.** Runtime files: name the lock like the other home files, for example
    `a.release-operation.lock`. Say that the launcher reads the runtime record
    to find Python and the bootstrap reads it again to validate it, so "once
    per invocation" holds per component.
- **19.** Step 1 tests: replace "never use evaluation of marker text" with "never
    evaluate marker text as Python code".
- **20.** Command templates: write launcher paths with backslashes, as `run-pw.md`
    does.

### Writer instructions for plan release-project-root round 1

#### Next steps for the plan writer for plan release-project-root (round 1)

1. Apply changes 1 to 13 in the plan and keep the six-step order. Add each new
   file to its step's file list and line-budget checkpoint.
2. Mirror the changed expectations in the validation skeleton, mainly for
   Steps 1, 4, 5 and 6, and leave it unchecked.
3. Apply wording items 14 to 20.
4. Leave the requirement and the design unchanged. Change 11 only adds plan
   coverage for requirement text that already exists. If a change seems to
   need a new design decision, add it to the plan as an open question with
   options and a recommendation instead of deciding it in place.
5. No consolidation: convergence and consolidation remain the human's choice.
   Publish round 2 with the new plan digest.

### Final reviewer decision for plan release-project-root round 1

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-1 -->

## Round 2 by requestor

- Recorded: 2026-10-21T17:54:54+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan release-project-root (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Review round: 2

### Requestor assessment for plan release-project-root (round 2)

Round 1 found implementation gaps without reopening any of the 14 settled design
decisions. All 20 requested corrections are incorporated into the six-step plan
and the validation expectations. No missing question needs a human decision;
there are no question options or answers to preserve. The writer accepts the
reviewer's harness-copy recommendation and adds no public operation.

Please assess whether the revised execution details now close the identified
gaps, including the pre-gate helper loader, setup entry, closed lock/marker
contract, Git scopes, reused artifact preparation, non-replacing owner-record
publication, coverage and fixture architecture, exact entry/cancellation
contracts, requirement traceability and documentation placement.

The validation skeleton remains context only: six matching steps and 36 empty
check sections. No implementation or application tests have been performed.
Requirement and design were not changed by this revision. All suggested wording
corrections are applied; the writer claims no independent approval.

Reviewed plan SHA-256:
`e9fded4a5f0bfaac460e17d735bd2df078045df237a026c4bb1d2bbc475a9add`.

### Change summary for plan release-project-root (round 2)

The plan and aligned validation expectations now cover every round 1 request:

1. File-based helper loading before readiness and a checked engine import closure.
2. Saved-status setup batch entry, fake environment tests and fresh-setup evidence.
3. Explicit marker/lock/extra/source rules and pyproject-to-lock agreement checks.
4. Closed routing-key set, local/worktree scopes and command-scope rejection.
5. Reused artifact preparation with physical revalidation and public error statuses.
6. Complete versioned lock records published by non-replacing rename.
7. Manifest-verified tooling-copy handlers with no production injection surface.
8. In-process coverage, reusable fixtures, visible setup costs and link capability evidence.
9. Named pseudo-console harness and per-route cancellation completion requirements.
10. Reserved launcher entry protocol, pre-Python errors, localized chcp and ASCII launchers.
11. Root-derived project name and legacy locations with stale-environment tests.
12. AC11 file-absence detection, real launcher failure propagation and later ownership.
13. Two reference-page updates and a short README pointer.
14. Corrected literal-parenthesis rg expression.
15. Corrected relative batch call spelling.
16. Dedicated transport and locking test leaves with initializers.
17. Explicit MAJOR.MINOR.PATCH tooling minimum syntax.
18. Home-local a.* lock naming and per-component runtime record reads.
19. Precise prohibition on evaluating marker text as Python code.
20. Backslash launcher paths in command templates.

Six steps and all 36 unchecked validation sections are preserved. The file
inventory now lists 54 new paths; existing and earlier-step update targets were
verified. Requirement and design are unchanged from round 1.

### Writer response for plan release-project-root (round 2)

Writer response:

Accepted changes 1 through 20, with no disagreement or new design question.
The plan now names file-based pre-gate imports and import-closure tests; a small
saved-status setup entry with a fake-environment harness and fresh-setup evidence;
closed lock/marker inputs and source-kind ambiguity rejection without registry
URL identity; and a finite Git routing-key/scope matrix.

Artifact preparation delegates to the existing helper after ancestor validation
and rechecks the resulting home. Error statuses are explicit. Operation ownership
publishes only complete versioned records through a non-replacing rename, with
conservative diagnostics for unknown or unverifiable owners.

The shared test architecture uses a manifest-verified tooling copy, in-process
coverage, session templates and bounded caller-family matrices. Fixture/setup
cost remains visible. Missing file-symlink or console evidence remains a gap.
The named ctypes pseudo-console and entry protocol cover actual doskey,
cancellation, redirected input, localized code-page handling and pre-Python errors.

The context covers the existing legacy-location/project-name requirements without
exporting variables. AC11 distinguishes launcher absence from execution failure
and leaves production behavior to item 5. Detailed documentation targets the two
existing reference pages; README receives a pointer. All seven wording/layout
corrections are included. The requirement and design were not changed this round.

Keep all public transcript references repository-relative. Absolute identity paths
belong only in the private protocol request and answer envelopes; omit them from
the substantive transcript summary and any authored evidence examples.

The requestor normalized the two generated provenance paths in the public
transcript to repository-relative references under the user's confidentiality
instruction. Reviewer wording references 14 through 20 now use bullet labels
with their original numbers to resolve MD029 without changing review content.
Please use continuous lists or explicit bullet labels in subsequent summaries.

### Reviewer focus for plan release-project-root (round 2)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-2 -->

## Round 2 by reviewer

- Recorded: 2026-10-21T18:00:07+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan release-project-root round 2

#### Identity and scope check for plan release-project-root (round 2)

The working-tree plan has SHA-256
`e9fded4a5f0bfaac460e17d735bd2df078045df237a026c4bb1d2bbc475a9add`, the digest
the request names (889 lines). The requirement and the design are unchanged
since round 1: their only edits over `HEAD` are the same two IO clarification
sections. The validation skeleton was read as context; its six steps carry the
new expectations and stay unchecked. No design decision is reopened.

#### Round 1 changes verified for plan release-project-root (round 2)

| Round 1 item | Status | Where in the plan |
| --- | --- | --- |
| 1. Pre-gate loader and import-closure test | Applied | Step 1, lines 267 to 272 and 292 to 300 |
| 2. Setup entry with saved status | Applied | `bin/release_runtime_record.bat`; lines 267 to 268, 280 to 287 and 335 to 337 |
| 3. Closed lock and marker contract | Applied, one lock shape left open (required change 1) | Lines 309 to 330 |
| 4. Git routing keys and scopes | Applied | Lines 408 to 412 |
| 5. Reuse of `prepare_home` and error statuses | Applied | Lines 556 to 563 |
| 6. Owner-record publication | Applied | Lines 546 to 547 and 568 to 583 |
| 7. Harness tooling copy for handlers | Applied | Lines 28 to 29, 195 to 204 and 784 to 789 |
| 8. Coverage, duration and links | Applied | Lines 185 to 217 |
| 9. Console harness and cancellation | Applied, answer keys need localizing (wording) | Lines 708 to 716, 726 to 727 and 803 to 805 |
| 10. Launcher contract and entry protocol | Applied | Lines 674 to 693 |
| 11. Legacy locations and project name | Applied | Lines 657 to 663 and the ownership map |
| 12. AC11 file-absence case | Applied | Lines 806 to 812 and the ownership map |
| 13. Wiki placement and README pointer | Applied | Lines 779 to 780, 815 to 822 and 854 |
| 14 to 20. Wording items | Applied | Lines 496, 701, 774 to 777, 487 to 488, 35 to 36, 124, 264, 161 and 164 |

Baselines for the two wiki pages (130 and 69 lines) match the gate metric.

#### New findings for plan release-project-root (round 2)

- Empty release group. A uv 0.11.21 probe locked `release = []` beside a
  nonempty `dev` group. `[package.dev-dependencies]` then lists only `dev`, and
  `release = []` appears only in `[package.metadata.requires-dev]`. With both
  groups empty, no `[package.dev-dependencies]` table exists at all. The plan
  expects an empty group for the stdlib-only foundation, but its closed
  contract does not define that shape, and a fail-closed reading would reject
  the shipped lock.
- Values crossing the gate. The helpers loaded under private names are
  separate module objects from the `tools.release_workflow` modules that the
  engine imports after the gate. An object of a private class fails
  `isinstance` and equality checks against its package twin, and pyright
  strict sees a dynamically loaded module as untyped.
- Interpreter requirement grammar. Readiness reads `requires-python`
  (`>=3.13, <3.14`), but the plan closes only the marker grammar, not the
  specifier forms readiness must parse.
- Localized cancellation prompt. On this French host, cmd's prompt is
  `Terminer le programme de commandes (O/N) ?` and it expects O, not Y.

Disposition: changes requested. Three small contract rules remain, plus
wording. Each is one or two sentences, so round 3 should be short.

### Question verdicts for plan release-project-root round 2

#### Verdicts on the plan questions for plan release-project-root (round 2)

| Item | Reviewer verdict |
| --- | --- |
| Questions in the plan | None, and none is missing that needs the human. The remaining items are plan rules that the approved design settles |
| Writer's "no open questions" assessment | Agree. The harness-copy choice adds no public operation, so the possible escalation from round 1 no longer applies |
| The 14 settled design decisions | Not reopened |

### Requested changes for plan release-project-root round 2

Requested changes:

#### Required plan changes before round 3 for plan release-project-root (round 2)

1. Closed readiness contract, lock shape of an empty group. Identify the root
   package by `source = { virtual = "." }` and the normalized project name.
   Require `[package.metadata.requires-dev].release` to exist. When it is
   empty, an absent `release` key under `[package.dev-dependencies]`, or an
   absent table, means an empty closure. When it is nonempty and the root has
   no locked `release` edges, readiness fails closed with status 2. Test both
   shapes, using the lock that uv actually produces for an empty group.
2. Bootstrap, values crossing the gate. Pass only plain data (paths, strings
   and the record's parsed fields) from the pre-gate helpers to the engine.
   The engine never relies on `isinstance` or equality between private-module
   objects and their `tools.release_workflow` twins. Type the dynamically
   loaded helpers through a small typed protocol or an explicit cast, so that
   pyright strict passes without suppressions.
3. Readiness, interpreter requirement grammar. Close the `requires-python`
   forms that readiness accepts: comma-separated `==`, `!=`, `<`, `<=`, `>` and
   `>=` clauses on release versions, compared with the same release-tuple rule
   as the markers. `~=`, `===`, wildcards, prereleases and local versions fail
   readiness with status 2, naming the specifier.

#### Wording to fix in the same revision for plan release-project-root (round 2)

- Cancellation outcomes (lines 711 to 713): say "the localized yes and no
  answers" rather than Y and N. The harness reads the answer keys from the
  prompt it captured; this host shows `Terminer le programme de commandes
  (O/N) ?`.
- Closed readiness contract: add one line saying that a `release` dependency
  needing an extra cannot be declared until readiness supports extras, so
  domain owners learn the limit before they add one.
- Reflow the IO paragraph at lines 37 to 38 and the minimum-version item at
  lines 489 to 490, which have short broken lines.

### Writer instructions for plan release-project-root round 2

#### Next steps for the plan writer for plan release-project-root (round 2)

1. Add the three contract rules from the required changes to Step 1 and
   mirror them in the Step 1 validation expectations.
2. Apply the three wording items.
3. Keep the requirement and the design unchanged, and keep the six-step order.
4. No consolidation: convergence and consolidation remain the human's choice.
   Publish round 3 with the new plan digest.

### Final reviewer decision for plan release-project-root round 2

Decision: changes-requested. The writer should apply the concrete instructions and publish another automated review round.

<!-- review-entry-id: answer-round-2 -->

## Round 3 by requestor

- Recorded: 2026-10-21T18:02:16+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: request

### Review identity for plan release-project-root (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Reviewed specification: docs/v0.14.0/plan.v0.14.0.release-project-root.md
Review round: 3

### Requestor assessment for plan release-project-root (round 3)

Round 2 verified all 20 earlier corrections and identified three small contract
gaps plus wording corrections. They are now applied, and the validation skeleton
has matching expectations. No missing question needs a human decision; no design
decision, public operation or step order changed. There are no question options
or human answers to preserve. All reviewer wording suggestions are applied.

Please verify the added uv empty-group shapes, plain-data/typed boundary between
private helper modules and the engine, enumerated interpreter specifier grammar,
localized cancellation answer keys, extras limitation and paragraph reflow.
The requirement and design remain unchanged from round 1. No implementation or
application tests have been performed; the six-step skeleton remains unchecked.

Reviewed plan SHA-256: 513db01c9a0681279ebf18e725ed0b5313eb03d0b6f255cdf0eb8aedd45e78a3.

### Change summary for plan release-project-root (round 3)

Step 1 now identifies the virtual root package and requires release metadata;
it accepts uv's two empty-group shapes and rejects nonempty metadata without
locked edges. It passes plain data across the readiness boundary and types the
dynamic helper interfaces without suppressions. Its interpreter parser accepts
the six listed comma-separated release-version comparison operators and rejects
unsupported specifiers with status 2. Release tuples use trailing zero padding.

The cancellation harness reads localized yes/no keys from the captured prompt.
Domain owners are told that extras-dependent release dependencies are unsupported.
The two requested paragraphs are reflowed. Validation expectations mirror the
changes and retain six steps and all 36 empty check sections. Requirement and
design remain unchanged, and no files or public operations were added this round.

### Writer response for plan release-project-root (round 3)

Writer response:

Accepted all three required changes and all three wording changes, without
disagreement or any reopened design question. Round 2's implementation gaps are
covered by explicit Step 1 rules and matching unchecked validation expectations.

Keep public transcript references repository-relative and all authored evidence
generic. Absolute machine identity belongs only in private protocol envelopes.
Use independent numbered lists starting at 1 or explicit bullet labels so the
published transcript stays lint-clean without changing reviewer references.

### Reviewer focus for plan release-project-root (round 3)

Check for missing questions, assess the existing options and answers, and suggest any clearer wording.

<!-- review-entry-id: request-round-3 -->

## Round 3 by reviewer

- Recorded: 2026-10-21T18:05:14+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: answer

### Reviewer assessment for plan release-project-root round 3

#### Identity and scope check for plan release-project-root (round 3)

The working-tree plan has SHA-256
`513db01c9a0681279ebf18e725ed0b5313eb03d0b6f255cdf0eb8aedd45e78a3`, the digest
the request names (907 lines). The requirement and the design are unchanged
since round 1. The validation skeleton keeps six steps and 36 empty check
sections, and its Step 1 expectations mirror the new rules. No design decision
is reopened.

#### Round 2 changes verified for plan release-project-root (round 3)

| Round 2 item | Status | Where in the plan |
| --- | --- | --- |
| Empty release group lock shapes | Applied: the virtual root package, required `requires-dev.release`, both empty shapes accepted, nonempty metadata without edges fails with 2, tests use uv-generated locks | Closed readiness contract, first item |
| Plain data across the gate | Applied: no private/package class-identity assumption, typed protocols or casts, no suppressions | `bootstrap.py` behavior item |
| Interpreter specifier grammar | Applied: six comparison operators on release versions, padded release tuples, rejected forms fail with 2, the current `>=3.13, <3.14` form tested | Closed readiness contract, last item |
| Localized cancellation answers | Applied: answer keys read from the captured prompt | `console_support.py` paragraph |
| Extras limitation | Applied | Closed readiness contract, first item |
| Reflow | Partly applied (see covered wording) | IO paragraph and cancellation paragraph |

The padded comparison matches the current requirement: 3.13.9 is at least
3.13.0 and below 3.14.0. The empty-group rule matches what uv 0.11.21 wrote in
the round 2 probe, both beside a nonempty `dev` group and with both groups
empty.

#### Remaining state for plan release-project-root (round 3)

All round 1 and round 2 findings are settled in the plan text, and the
validation skeleton mirrors them. What is left is reflowing two paragraphs,
which changes no rule.

### Question verdicts for plan release-project-root round 3

#### Verdicts on the plan questions for plan release-project-root (round 3)

| Item | Reviewer verdict |
| --- | --- |
| Questions in the plan | None, and none is missing: every implementation decision is now settled in the plan from the approved design |
| Writer's "no open questions" assessment | Agree |
| The 14 settled design decisions | Not reopened |

### Convergence evidence for plan release-project-root round 3

Covered wording:

#### Wording polish left for the writer for plan release-project-root (round 3)

1. File-based IO paragraph: join "artifacts during readiness, preflight or
   read-only" with the following "work." line so the paragraph reflows
   normally.
2. Cancellation paragraph: rewrap the line "execution returns 1 with
   diagnostics. Redirected stdin must never prompt. Verify environment," to
   the paragraph's width.

Both items are readability only and change no rule.

Convergence rationale:

#### Why the plan has converged for plan release-project-root (round 3)

- Every round 1 and round 2 finding is applied where it belongs, and the
  validation skeleton carries matching unchecked expectations.
- The closed readiness contract, the gate boundary, the launcher entry
  protocol, the lock record, the harness copy and the console evidence rules
  are concrete enough to implement and test without a new decision.
- The plan has no open question, adds no public operation, keeps the six-step
  order and leaves the requirement and the design unchanged.
- Only the two reflow items in the covered wording remain.

This recommendation is advisory and does not authorize consolidation. Whether
and when to consolidate stays with the human at the gate.

### Writer instructions for plan release-project-root round 3

#### Next steps for the plan writer for plan release-project-root (round 3)

1. Apply the two covered reflow items. They need no further review round.
2. Keep the validation skeleton unchecked until implementation checks run.
3. Do not consolidate or start implementation until the human chooses at the
   gate.

### Final reviewer decision for plan release-project-root round 3

Decision: convergence-recommended. This recommendation is advisory; consolidation is not confirmed and remains at the durable human gate.

<!-- review-entry-id: answer-round-3 -->

## Round 3 by human - human-confirmation

- Recorded: 2026-10-22T09:47:45+02:00
- Exchange: specification/plan/v0.14.0/release-project-root
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.release-project-root.md
- Requestor LLM nature: codex
- Reviewer LLM nature: claude
- Outcome: human-confirmation

Human choice: Consolidate
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
