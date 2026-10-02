# v0.13.0 full_suite_levels implementation tracking and validation

No, it is not implemented.

This document tracks the nine steps of the
[implementation plan](plan.v0.13.0.full_suite_levels.md), from the Step 0 cost
gates to the Step 8 acceptance mapping; Step 0 is implemented and checked,
and Steps 1 to 8 are not implemented yet.

> Markdown lint note: never leave a space immediately inside an inline code span
> (MD038); write a needed space as the token `[space]`, as in `` `[space]${x}` ``.
> The empty placeholder ends in `)_.` so the line is not pure italic text (MD036).

---

## File-based IO cost clarification for v0.13.0 full_suite_levels (implementation)

All implementation work must respect the IO classification established in
[the plan](plan.v0.13.0.full_suite_levels.md). The key constraints carried
forward from the plan are:

- A noop or upgrade decision reads only the walk's own scope marker, the floor
  file for the timing fingerprint, and the existing digest walk.
- Group membership reuses the digest's single file walk; `.ghog-groups` is read
  once and only when a group is selected, never by a whole-suite run.
- A `--scope-file` run reads one capture and checks each listed file once; it
  never matches patterns or reads the declaration.
- Markers, status lines and capture copies are written through a temporary
  file and an atomic replace; `pw scope` and `pw progress` read only the
  requirement's metadata lines, never the draft.

---

## Complexity Bound Clarification for v0.13.0 (implementation)

The scaling target for all v0.13.0 code paths is:

- **O(1) amortized per hot-loop event**: one parse per streamed pytest line,
  one compiled-pattern match per project file, one existence check per
  captured file.
- **O(n) total per phase**: one project walk per invocation for digest and
  membership, one pass over the sorted lists for fingerprints and the folder
  set, one data-file analysis over the resolved sources.

Every implemented step should be reviewed against this bound in its
Performance check section.

---

## Step 0. Add the cost gates of the leveled walk

### Analysis of Step 0 implementation state

Yes. Step 0 has been fully implemented.

The new `tests/unit/tools/test_groundhog_levels_perf` package holds the five
planned gates, each bounded by `GATE_TIMEOUT_SECONDS` and marked strict
`xfail` with its owning step. They assert spawned child commands and exit
codes through `cli.main`, and the fresh `ghog day` walk reports them as the
five xfails of both the affected and the full phase.

Independent reviewer assessment (round 1) confirms that the staged tests match
Step 0 and that `a.commit` passes the mechanical checker with both groups in
dependency order. The reviewer assessed coverage statically and relied on the
requestor's recorded green walk; no validation command was repeated.

### Goal for Step 0

Add five time-bound, spawn-counting gates for the default walk, the upgrade,
the stronger-proof noop and the grouped walk, each a strict `xfail` owned by
Step 2 or Step 4.

### Step 0 improvement expectations

- The five gates xfail on the pre-change walk without erroring.
- Each gate carries `pytest.mark.timeout(GATE_TIMEOUT_SECONDS)` and asserts
  spawned commands, not wall-clock time.
- No production file changes.

### What was implemented for Step 0

- **Gate package**: `tests/unit/tools/test_groundhog_levels_perf/__init__.py`
  carries the package docstring and `# eof`;
  `test_groundhog_levels_perf_tdd.py` holds the gates, with
  `GATE_TIMEOUT_SECONDS: Final = 5` on each.
- **Step 2 gates**: `test_default_walk_spawns_no_full_run` expects exactly the
  check.bat and `--no-cov` affected children of a green default walk;
  `test_upgrade_spawns_only_the_full_run` expects one covered full child
  (`--cov-report`, no `--cov-append`, no `--durations=0`) from
  `ghog day --full=cov` after a green default walk;
  `test_stronger_saved_proof_spawns_nothing` expects a sequential
  `--full=speed` walk to make the following `--full=cov` walk spawn nothing.
- **Step 4 gates**: on a `tmp_path` project whose `.ghog-groups` declares
  `sentinel`, `test_grouped_walk_passes_only_group_test_files` expects the
  affected and full children of `ghog day --full=pass --group=sentinel` to
  carry exactly `tests/sentinel/test_core.py` as their `.py` positional paths
  (the group's `conftest.py` and the outside `tests/test_mod.py` excluded);
  `test_grouped_walk_walks_the_tree_once` expects the same walk to exit 0
  with its two group children and one `pathlib.Path.rglob` call, counted
  through `monkeypatch`.
- **Assertion-only failure before the owner**: `_run(argv, deps)` returns
  argparse's `SystemExit` code, every spawn queue holds the children the
  pre-change walk pops, and an autouse fixture clears `GHOG_FULL` and
  `GHOG_GROUP`, so each gate fails on an exit-code or spawn-count assertion
  today, never on an error or an ambient selector.
- **Validation evidence**: the `ghog day` walk ended on 2026-10-02 at
  09:26:28 +02:00 with `exit=0`: check green, `ghog affected --no-cov` with
  `xfail=5`, and `ghog full` with `fail=0 xfail=5 cov=100`. Both plan `rg`
  patterns (`xfail\(strict=True` and `timeout\(GATE_TIMEOUT_SECONDS\)`) list
  five gates. Physical counts are 7 for the initializer and 265 for the gate
  file; the gate file exceeds the advisory 190 because of its documented
  project builders, which is variance below the 550 band, not missing work.

### New types or classes introduced for Step 0

No new type or class was introduced. The step is test-only: module-level
project builders, the `_run` exit-code helper, the `_count_rglob` counter and
the five gate functions reuse `QueueSpawns`, `make_deps` and
`passing_transcript` from `tests/unit/tools/groundhog_acceptance_support.py`.

### Architecture check for Step 0

- **Test boundary**: the gates drive the public `tools.groundhog.cli.main`
  entry point and read only `EXIT_OBJECTIVE_MET` from
  `tools.groundhog.models`; the single faked element is the process factory,
  as in the existing groundhog acceptance tests.
- **Production code**: no file under `tools/` changed, so no layer gained an
  import or a responsibility.
- **Global patch scope**: the `Path.rglob` counter and the environment
  clearing go through `monkeypatch`, restored after each gate.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing
that needs to be addressed.

### Performance check for Step 0

- **No new `O(n^2)` or `O(n log n)` path**: no production computation was
  added; each gate builds a project of at most eight files.
- **Hot-path bound**: the rglob counter appends one entry per call and
  delegates the walk unchanged; the spawn assertions read the recorded
  command lists once.
- **Startup or background path**: none; the gates spawn no real process.
- **Plan-bound alignment**: the gates encode the plan's bounds as counts
  (no full child by default, one child on upgrade, none on noop, one tree
  walk per grouped invocation), so a later regression fails on work done,
  not on wall-clock time.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 0

The coverage gate measures `source = ["tools"]` and omits `*/tests/*` in
`pyproject.toml`, so both staged files sit outside it and the walk's
`cov=100` says nothing about them. No class file under `tools/` is impacted.
Statically, every top-level helper of the gate file is referenced by a gate
or another helper: `_write`, `_project`, `_grouped_project`, `_green_walk`,
`_green_group_walk`, `_day`,
`_run`, `_python_paths`, `_group_spawn_count` and `_count_rglob`;
`clear_ambient_selectors` is an autouse fixture that pytest applies to every
gate. Until the owning steps land, the code after each gate's first failing
assertion does not execute, by design of a strict `xfail` gate.

No, there is no unit-tested class below 100% that needs completing for Step 0.
No, no top-level symbol of the staged files outside the coverage gate is
unreferenced.

### Feature integrity for Step 0

- **Existing feature behavior**: no production file changed; the full suite
  passed with no failure and only the five new xfails.
- **Reporting or diagnostics**: the groundhog closing lines now count five
  xfails in a walk that runs the gates; no report format changed.
- **Compatibility or rollout note**: Step 2 removes `xfail` from the three
  Step 2 gates and Step 4 from the two Step 4 gates; a strict `xfail` that
  passes earlier fails the suite, which surfaces any premature behavior
  change.

No existing feature or reporting capability appears impaired.

---

## Step 1. Free commands.py and add the pure level, proof and marker models

### Analysis of Step 1 implementation state

Not started. Step 1 is not implemented because no implementation has begun.

`commands.py` is still at 637 lines and the level, proof and marker models do
not exist yet.

### Goal for Step 1

Move the verdicts and the progress sink out of `commands.py` without behavior
change, and add the pure `levels`, `proof` and marker models with their unit
and property tests.

### Step 1 improvement expectations

- `commands.py` at most 500 lines, every existing test green with updated
  references.
- Level resolution, proof accumulation and cap, noop and upgrade decisions and
  the key=value marker covered by TDD and PBT tests.
- The walk itself unchanged.

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

---

## Step 2. Run the walk and the full run by level, with saved proof

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because Step 1 has not landed yet.

The CLI still has no `--full`, the walk still runs three steps, and the
marker still holds one digest.

### Goal for Step 2

Wire levels and saved proof through the CLI, the walk, the full run, the
reports, the status file and the detached walk, and move the requestor
default, the prepare-release operations and the no-argument cycle to their
explicit levels.

### Step 2 improvement expectations

- Plain `ghog day` stops after the affected tests with the skip line; each
  level runs its own full-run shape and verdict; restart lines carry the level
  and never `--full=none`.
- The proof marker drives noops and upgrades, is capped by any contradicted
  gate, and is rewritten or removed after every walk that judged a gate.
- The closing and status lines carry `full=`, `src=`, `proof=`, `reused=` and
  `scope=`; the three Step 2 gates pass without `xfail`.

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

---

## Step 3. Declare groups, capture scopes, and list exclusions

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because Step 2 has not landed yet.

No group declaration, matcher, capture model, `ghog groups` or exclusion
listing exists yet.

### Goal for Step 3

Add the `.ghog-groups` reader, the gitignore-style matcher, the group resolver
and fingerprint, the tools-level captured-scope model, and the read-only
`ghog groups` and `ghog exclude --list [--since]` listings.

### Step 3 improvement expectations

- `ghog groups <name>` applies the exit-5 rules a run will apply, each message
  naming the cause or the empty side.
- Captures round-trip and refuse an incomplete, tampered or stale capture.
- The exclusion listing and comparison print `exclusions=<count>`, `changed`,
  `unchanged`, `unreadable` or `unverified` as the design states.

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

---

## Step 4. Select a scope and run, gate and prove inside a group

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because Step 3 has not landed yet.

Run commands accept no scope selector and every run still covers the whole
suite.

### Goal for Step 4

Resolve one scope per invocation, narrow the affected, full and timing runs to
the group's test files, judge the group coverage gate and grouped durations,
keep one marker per scope, and carry the scope through restart lines,
evidence keys, the detached walk and the prepare-release operations.

### Step 4 improvement expectations

- A grouped walk passes only the group's test files, judges 100% over the
  group's sources from a scope-owned data file, and leaves `a.ghog.outliers`
  untouched.
- Proof is valid only for the exact scope, fingerprint and digest; a timing
  change caps it at `cov`.
- The two Step 4 gates pass without `xfail`; no gate remains `xfail`.

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

---

## Step 5. Read the effort scope and print it through pw

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because Step 4 has not landed yet.

No effort-scope reader, `pw scope` command or `scope` progress line exists
yet.

### Goal for Step 5

Add `tools/effort_scope.py`, `pw scope [ghog arguments]` and the `scope` line
of `pw progress`, reading only the requirement's `- Test group:` line.

### Step 5 improvement expectations

- `pw scope day` prints the completed command with `--group=<name>` or
  `--whole-suite`, whatever `GHOG_GROUP` holds.
- An invalid or duplicated group line is an error naming the requirement and
  the cause, never a fallback; the draft is never read.
- `pw progress` shows the scope and its source.

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

---

## Step 6. Validate requests in the effort scope and bind the round scope

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because Step 5 has not landed yet.

The renderer still renders the default without a selector and the exchange
keeps no scope for a published round.

### Goal for Step 6

Complete the requestor's default validation with the effort scope, render the
scope evidence, the migration notice, the group statement and the scope-change
block, bind each published code round to a core-owned capture that follows the
coordination record through every removal or archival, and ship the minimum
requestor and reviewer invocation instructions with the new required
arguments.

### Step 6 improvement expectations

- The project default renders as `ghog day --full=speed` plus the effort
  selector; declared sets stay unchanged and never claim a group proof they do
  not establish.
- `test_scope` proof comes from `snapshot.effective_proof`, the walk's own
  rule: a timing-only change shows at most `cov` until a new `speed` walk,
  for the whole suite and for a group.
- `publish-request --scope-capture-file` validates and copies the capture to
  `paths.scope`; `status` reports `bound_scope`, or `missing` for a legacy
  request; `complete`, `complete --force` and `resolve` remove the capture,
  `archive` archives it.
- The requestor, review-requestor, reviewer and implementation-check
  instructions name the new arguments and the `--scope-file=<paths.scope>`
  evidence; every renderer caller test passes the required output; a
  round-trip test renders, publishes and consumes the bound scope.
- A replacement whose scope changed requires `--scope-change-file`;
  `pw progress` shows the `bound` line and any `pending change`;
  `code_review_request.py` ends at or below 590 lines.

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

---

## Step 7. Update the workflow instructions, templates and groundhog manuals

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because Step 6 has not landed yet.

The instructions still describe one walk objective and no scope.

### Goal for Step 7

Apply the rest of the design's workflow instruction list on top of Step 6's
invocation contracts: development walks through `pw scope day`, the review-off
`speed` pass, the groundhog loop by level and scope, the requestor's `speed`
validation policy, the prepare-release gate at `cov` on the whole suite, the
scope menu of process-draft and write-requirement, and the groundhog manuals
and specification.

### Step 7 improvement expectations

- Each instruction names the command, level and scope the design gives its
  phase; adapters remain redirects.
- Pinned instruction tests follow the new wording; new contracts live in their
  own package; `groundhog.md` keeps exactly two `.\senv.bat &&` calls.
- Every edited Markdown file passes markdownlint.

### What was implemented for Step 7

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 7

_(empty — no check has taken place yet.)_.

### Architecture check for Step 7

_(empty — no check has taken place yet.)_.

### Performance check for Step 7

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 7

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 7

_(empty — no check has taken place yet.)_.

---

## Step 8. Prove every design acceptance case

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because Step 7 has not landed yet.

The cross-component acceptance package and the row-to-test mapping do not
exist yet.

### Goal for Step 8

Add an acceptance package that drives groundhog, `pw`, the request renderer and
the review exchange together on `tmp_path` repositories, and map every design
acceptance row to its passing tests.

### Step 8 improvement expectations

- Review flows (captured scope after a same-name edit, refused capture, legacy
  request, replacement with and without a scope-change reason, migration
  notice, no false group claim) pass end to end.
- Workflow flows (`pw scope` precedence over `GHOG_GROUP`, stale draft,
  prepare-release on the whole suite, the review-off exclusion comparison)
  pass end to end.
- This section gains a table mapping every design acceptance row to its test
  node ids.

### What was implemented for Step 8

_(empty — no check has taken place yet.)_.

### New types or classes introduced for Step 8

_(empty — no check has taken place yet.)_.

### Architecture check for Step 8

_(empty — no check has taken place yet.)_.

### Performance check for Step 8

_(empty — no check has taken place yet.)_.

### Unit test coverage check for Step 8

_(empty — no check has taken place yet.)_.

### Feature integrity for Step 8

_(empty — no check has taken place yet.)_.
