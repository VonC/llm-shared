# v0.3.0 duration_outliers_exclusion implementation tracking and validation

No, it is not implemented.

This document tracks, step by step, the build of the tool-managed `[exclusion]` section against [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). Steps 1 to 3 are built and green: `exclusions.py` reads and writes the section, `durations.py` spares and classifies excluded calls, and `durations_summary.py` and `durations_report.py` wire the read / apply / write into a run and render the exclusion block. The closing-line `excluded=` field, the `ghog` add-exclusion command and the guidance and acceptance updates remain. Each step's evidence is filled at its implementation check.

---

## File-based IO cost clarification for v0.3.0 exclusions (implementation)

The exclusion read and write must stay a tiny, bounded file operation, as the plan requires:

- the `[exclusion]` section is a handful of lines read once per `ghog full` run, beside the two floor lines.
- the write is one atomic side-file replace per run, the pattern `floor.py` already uses.
- no extra file is added: the section lives inside `a.ghog.outliers`.
- the reader and writer never scan the whole repository or any coverage export.

---

## Complexity bound clarification for v0.3.0 exclusions (implementation)

The scaling target for the exclusion code paths is:

- **O(1) amortized per excluded entry**: spare, classify and the ratchet/remove decision are a constant-cost lookup per entry.
- **O(n) total per run**: one pass over the run's call map and the exclusion map, no sort beyond the v0.2.0 rule's existing one.

Every implemented step is reviewed against this bound in its Performance check section.

---

## Step 1. Read and write the exclusion section

### Analysis of Step 1 implementation state

Yes. Step 1 has been fully implemented.

`tools/groundhog/exclusions.py` reads the `[exclusion]` section into a `node -> recorded seconds` map and writes it back through the same atomic side-file replace `floor.py` uses, preserving the two floor lines; `test_groundhog_exclusions.py` pins the read, the write and the tolerant fallbacks. One `ghog day` walk is green: `exit=0`, full suite `772/772 fail=0`, `cov=100`, `outliers=0`, so the new module sits at 100% coverage with `floor.py` untouched.

### Goal for Step 1

Add a function-style `tools/groundhog/exclusions.py` that reads the `[exclusion]` section into a `node -> recorded seconds` map and writes it back -- adding an entry, lowering a baseline, removing a below-floor or stale entry -- while leaving `floor.py`'s two-line read untouched.

### Step 1 improvement expectations

- `read_exclusions(root)` returns the `node -> recorded seconds` map, `{}` when no section; a missing, partial, malformed or binary file reads as `{}`, and a malformed entry, a blank line, or text before the `[exclusion]` header is skipped without raising.
- the write path adds an entry, lowers a baseline, and removes a below-floor or stale entry, preserving the floor lines (1 and 2), with the atomic side-file replace; a write failure is logged, not raised.
- `floor.py` is unchanged in behaviour and stays at or under its 130-line budget.
- `test_groundhog_exclusions.py` reaches 100% of `exclusions.py`.

### What was implemented for Step 1

- **`tools/groundhog/exclusions.py` (new)**: a function-style module beside `floor.py` and `gate.py`. `read_exclusions(root)` returns the `node -> recorded seconds` map parsed from after the `[exclusion]` header, `{}` when the section, the file, or readable text is absent; `write_exclusions(root, exclusions)` keeps the two floor lines verbatim, then writes the header and one `node = seconds` line per entry through the side-file replace `floor.py` uses, logging an `OSError` rather than raising it. Private helpers `_floor_head`, `_parse_entry` and `_read_text` keep each function at radon grade A.
- **Tolerant read**: lines before the header (the floor lines), blank lines, comment lines and any line that is not `node = number` are skipped without raising; the value is split off the last `=` (`rpartition`), so a parametrized node id carrying its own `=` or spaces survives whole. A missing or binary file reads as `{}` (the `OSError`/`UnicodeDecodeError` suppression of `_read_text`).
- **Tool-managed write surface**: `write_exclusions` is the whole-map writer; the add / lower-baseline / remove decisions stay caller policy (Step 2's rule post-step and Step 4's command), mirroring how `floor.py` keeps the override choice in `durations_summary`. An empty map drops the header, returning the file to a clean two-line floor file; a file with fewer than two lines yet is seeded with the default floor head so the section is always well-formed.
- **`floor.py` reuse, not change**: the new module imports `floor.floor_path`, `floor.FLOOR_FILE` and `floor.DEFAULT_FLOOR` (Q66 sanctions importing floor's helpers); `floor.py` itself is byte-for-byte unchanged and stays at its 130-line budget.
- **`tests/unit/tools/test_groundhog_exclusions.py` (new)**: 16 example-based tests covering the read (no section, well-formed map, parametrized-`=` node kept whole, malformed/blank/comment/no-`=`/empty-node lines skipped, pre-header text skipped, missing and binary file) and the write (adds and preserves floor lines, lowers a baseline, removes an entry, empty-map header drop, default-head seeding, write failure logged not raised).
- **`__init__.py`**: no change needed. `tools/groundhog/__init__.py` re-exports only `models`, not sibling modules (`floor` and `durations` are not re-exported), so the new sibling needs no entry; `tests/unit/tools/__init__.py` already exists.
- **Validation evidence**: one `ghog day` walk reported `exit=0` with the full suite at `100% (772/772) fail=0 warn=0 xfail=0 cov=100 outliers=0`. The `check.bat` static gate (ty, pyright, ruff `select=["ALL"]`, radon, vulture, the 700-line big-file scan, shellcheck, enforce_eof) passed, since the walk would have stopped at check otherwise.

### New types or classes introduced for Step 1

- `tools/groundhog/exclusions.py`: introduces no new production class or dataclass; Step 1 is completed with functions only (`read_exclusions`, `write_exclusions`) plus the private helpers `_floor_head`, `_parse_entry`, `_read_text`, matching the function-style of `floor.py`. The `DurationExclusion` record named in the plan belongs to Step 2 (`durations.py`), not here.
- `tests/unit/tools/test_groundhog_exclusions.py`: a new test module with one shared `_write_section` helper that seeds the floor lines, the header and given raw entry lines.

### Architecture check for Step 1

- **Tool package placement**: `exclusions.py` is a function-style IO seam beside `floor.py` and `gate.py`, the same layer; the read/write of `a.ghog.outliers` lives here, off `floor.py` (untouched) and off `durations.py` (which stays pure), so the rule remains IO-free and unit-testable in isolation.
- **Import direction**: `exclusions` imports `floor`'s public surface (`floor_path`, `FLOOR_FILE`, `DEFAULT_FLOOR`) only; `floor` does not import `exclusions`, so there is no cycle and no reverse dependency. The single source of truth for the file path and the default floor stays in `floor.py`, as Q66 directs.
- **Technical-lib use**: only `contextlib`, `logging` and `typing` are used, the same standard set `floor.py` uses for a tolerant read and an atomic write; no business rule and no report concern leaked into this IO module, and no report or rule module imports it yet (Step 3 wires it).

No DDD-Hexagonal violation or adapter smell is visible, the module is small and self-contained, and no, there is nothing that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: `read_exclusions` is one linear pass over the file lines; `write_exclusions` builds the body with one `join` over the entries and does one atomic replace. No sort is added, so nothing beyond the v0.2.0 rule's existing one is introduced.
- **Hot-path bound**: O(1) amortized per excluded entry — each line is a constant-cost strip, header test and `rpartition` parse; each write entry is a constant-cost format.
- **Startup or background path**: the read is a single file read and the write a single side-file replace per `ghog full` run, beside the two floor lines; no repository scan and no coverage export are touched, as the plan's IO cost clarification requires.
- **Plan-bound alignment**: O(n) total per run over the file lines and the entry map, inside the plan's O(1)-per-entry / O(n)-per-run target.

The step stays inside the plan's complexity target, and no, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

- **`tools/groundhog/exclusions.py`**: covered at 100%. `test_groundhog_exclusions.py` exercises every function and branch: `read_exclusions` (the `text is None` return, the in-section toggle, the blank/comment skip, the parse success and the `_parse_entry` `None` paths), `write_exclusions` (the non-empty header-and-body branch, the empty-map head-only branch and the `OSError` log branch), `_floor_head` (the two-line preserve and the default-head pad), and `_read_text` (success, missing and binary). The `ghog day` walk reported `cov=100`, so the one class file in this step sits at 100%.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: unchanged. `floor.py`'s two-line read and write, the pure duration rule in `durations.py`, and the v0.2.0 floor/outlier gate are untouched; the new module is not yet wired into a run (Step 3), so no `ghog full` path changes behaviour. The 772-test suite stays green at `fail=0`.
- **Reporting or diagnostics**: preserved. No report line or closing key=value field changed in Step 1; a write failure is logged at INFO (`ghog: could not write ... exclusions: ...`), matching `floor.py`'s safe-fallback logging, so a hand-edit or a blocked write cannot crash a run.
- **Compatibility or rollout note**: `a.ghog.outliers` stays git-ignored under the `a.*` pattern, so the `[exclusion]` section needs no `.gitignore` change; the floor lines (1 and 2) stay user-owned and read exactly as before.

No existing feature or reporting capability appears impaired.

---

## Step 2. Spare excluded calls and measure drift

### Analysis of Step 2 implementation state

Yes. Step 2 has been fully implemented.

`durations.py` gains the pure exclusion post-step `apply_exclusions` and the `DurationExclusion` value object, and `DurationSummary` carries the excluded-call list through a new `exclusions` field defaulting to `()`, so `summarize` and every existing constructor stay unchanged. The post-step spares flagged excluded calls from the outliers (Q54) and from the average (Q64), classifies each excluded node against its baseline (Q63), and yields the `node -> seconds` section the tool will write -- the median, MAD and floor still cover the whole run (Q54). The `ghog day` walk is green: 797 tests, `fail=0`, `cov=100`, `outliers=0`, `exit=0`.

### Goal for Step 2

Add a post-step over `DurationSummary` that spares excluded calls from the outliers and the average and classifies each excluded node against its baseline, leaving `summarize` and its test vectors unchanged.

### Step 2 improvement expectations

- the post-step spares any flagged call whose node is excluded and leaves excluded calls out of the average; the median, MAD and floor are computed over the whole run, unchanged by exclusion; `summarize` is unchanged.
- each excluded entry carries node, recorded, current and a status: `ok` within two seconds, `slower` when `current - recorded > 2s`, `faster` when `recorded - current > 2s`, `stale` when the node ran no call this run.
- the section update lowers a baseline only on a more-than-two-second improvement (Q69) and marks a below-floor or stale entry for removal; a faster reading within two seconds leaves the baseline alone.
- `durations.py` stays pure and under its line budget; the rule reaches 100% coverage.

### What was implemented for Step 2

- **`apply_exclusions` post-step (`durations.py`)**: a pure function `apply_exclusions(summary, durations, exclusions)` that runs after `summarize` and returns a pair -- the spared `DurationSummary` and the `node -> seconds` section the tool will write (Q67). Every flagged call whose node is excluded is dropped from `outliers` (Q54), and every excluded call is left out of the recomputed average (Q64); `runners_up`, `floor` and `median` pass through untouched, so the scale the rest is judged against does not move.
- **`_classify` baseline drift (`durations.py`)**: a slower-only compare (Q63) -- `current - recorded > 2s` reads `slower` and keeps the recorded baseline (never raised, Q57); `recorded - current > 2s` reads `faster` and ratchets the baseline down to `current` (Q69), dropped when `current` is under the floor (Q60); within two seconds reads `ok` and leaves the baseline alone; a node absent from the run reads `stale` with a `None` current and is dropped (Q61). The fixed `_BASELINE_TOLERANCE = 2.0` is the single band that gates both the slower-restore and the faster-ratchet.
- **`DurationSummary.exclusions` field**: a new `tuple[DurationExclusion, ...]` field defaulting to `()`, so the two `summarize` constructors and the two test-helper constructors (`test_groundhog_commands.py`, `test_groundhog_reporting.py`) keep working with no edit (Q67); `summarize`, `auto_floor`, `_is_outlier`, `_call` and `_median` are byte-for-byte unchanged.
- **Tests**: `test_groundhog_durations.py` adds the `_EXCL` run and seven `apply_exclusions` cases (a flagged call spared, the scale preserved, a non-outlier dropped from the average, the four statuses, the section ratchet-and-prune, a slower baseline never raised, a small improvement left alone); `test_groundhog_durations_pbt.py` adds two invariants (excluding every node leaves no outlier, a written baseline never rises above the recorded one, Q55).
- **Validation evidence**: the `ghog day` walk reported `exit=0`, `state=done`, `cov=100`, `fail=0`, `outliers=0` over 797 tests; `durations.py` is 341 lines, well under the 700-line big-file gate; ty, pyright, ruff, radon, vulture and the eof gate all green.

### New types or classes introduced for Step 2

- `DurationExclusion`: a frozen dataclass value object beside `DurationCall` and `DurationSummary` (Q68) -- `node`, `recorded`, `current` (`float | None`, `None` for a stale entry that ran no call), and `status`.
- `apply_exclusions`: the public post-step function returning `(DurationSummary, dict[str, float])` -- the spared summary and the section to write.
- `_classify`, `_average_without`: private helpers of the post-step (per-node drift verdict; mean over the kept calls).
- `DurationSummary.exclusions`: a new tuple field carrying the excluded-call list (default `()`).
- module constants `STATUS_OK`, `STATUS_SLOWER`, `STATUS_FASTER`, `STATUS_STALE` and `_BASELINE_TOLERANCE`.
- test support: the `_excl_summary` helper and `_EXCL` fixture in the TDD file, and two new property checks in the PBT file.

### Architecture check for Step 2

- **Pure rule layer (`durations.py`)**: `apply_exclusions` keeps the rule IO-free -- it takes plain `Mapping` inputs and returns value objects, importing only `dataclasses` and `typing`. It does not import `exclusions.py`, `floor.py`, the report or any IO module, so the rule stays unit-testable in isolation, the same contract `summarize` already holds.
- **Boundary direction**: the post-step receives the already-read exclusion map and hands back the section to write; the application seam (`durations_summary.py`, Step 3) will call `apply_exclusions` and own the read/write through `exclusions.py`, never the reverse. No layer reaches into the rule's internals.
- **Split or maintainability note**: the drift classification and the average recomputation are extracted as small private helpers (`_classify`, `_average_without`), each low-complexity, so `durations.py` stays at 341 lines, well inside the line budget; no split was needed.

No DDD-Hexagonal violation or adapter smell is visible; nothing needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: `apply_exclusions` is one linear pass over `summary.outliers`, one over `exclusions.items()`, and `_average_without` one pass over `durations.items()` after building the flagged-node set; all membership tests are `O(1)` set/dict lookups. No sort is added (the only sort, in `summarize`, is unchanged).
- **Hot-path bound**: the post-step runs once per `ghog full` run, `O(n)` in the number of timed calls plus excluded entries -- inside the plan's per-phase `O(n)` target.
- **Startup or background path**: not applicable; the rule has no startup or background work.
- **Plan-bound alignment**: the step stays inside the `O(n)`-per-phase bound the plan promised.

No performance issue needs to be addressed for Step 2.

### Unit test coverage check for Step 2

- **`durations.py`**: covered at 100% by `test_groundhog_durations.py` (TDD) and `test_groundhog_durations_pbt.py` (PBT), the test files named for the rule class. Every new branch has a covering case: `_classify`'s stale, slower, faster-above-floor, faster-below-floor and ok paths; `apply_exclusions`'s kept and dropped baselines; and `_average_without`'s empty-kept fallback (the PBT excludes every node, leaving no kept call). The `ghog full` coverage pass reported `cov=100`, consistent with this reasoning.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: unchanged. `summarize` and the v0.2.0 floor/outlier rule are byte-for-byte the same; the post-step is not yet wired into a run (`durations_summary.py` and `durations_report.py` are untouched -- that is Step 3), so no `ghog full` path changes behaviour. The 797-test suite stays green at `fail=0`.
- **Reporting or diagnostics**: preserved. No report line or closing key=value field changed in Step 2; the new `exclusions` field defaults to `()`, so a `DurationSummary` from the existing `summarize` reads as "no exclusions" and `durations_report.window_lines` (which does not read the field) is unaffected.
- **Compatibility or rollout note**: the `DurationExclusion` record and the section update produced by `apply_exclusions` are consumed only once Step 3 wires them in; until then the post-step is dead-code-free because its tests exercise it directly.

No existing feature or reporting capability appears impaired.

---

## Step 3. Wire exclusions into the run and the report

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

`durations_summary.py` reads the `[exclusion]` section before the floor rewrite, applies the rule post-step to the summary, and writes the managed section back through `exclusions.py` -- the only place the tool writes it; `durations_report.py` renders the exclusion block after the floor window, and `commands.py` emits it. One `ghog day` walk is green: `exit=0`, full suite `801/801 fail=0`, `cov=100`, `outliers=0`, so the wiring sits at 100% coverage with the floor window and the v0.2.0 gate unchanged.

### Goal for Step 3

Have `durations_summary` read the exclusion map, apply the post-step, and write the section back through `exclusions.py`; have `durations_report` render the exclusion block after the floor window.

### Step 3 improvement expectations

- `durations_summary.py` reads the exclusion map, applies the post-step, then writes the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section.
- the whole exclusion pass forms only on a full run already green on tests and coverage (Q34), so the list is never managed while the suite is failing.
- `durations_report.py` renders, per excluded call, `ok`, the restore instruction when slower, the lowered baseline on a real improvement, or `removed` (below floor or stale), and no block on an empty list.
- `test_groundhog_durations_report.py` covers the four lines and the no-block case.

### What was implemented for Step 3

- **`durations_summary.py` wiring (`_judge_map`)**: the seam now reads the `[exclusion]` section with `exclusions.read_exclusions(root)` before `floor.write_floor`, which keeps only the two floor lines and so drops the section -- the read is taken first on purpose. After `durations.summarize`, when the read map holds entries the rule post-step `durations.apply_exclusions` spares each excluded call and classifies it, and the managed `node -> seconds` map is written back through `exclusions.write_exclusions(root, updated)` after the floor rewrite, so the two floor lines are kept verbatim above the section. The write is guarded on a non-empty read map: a run with no section is not rewritten a second time, while a section whose entries are all removed still writes (the read map was non-empty) to drop the section. The whole pass sits inside `judge`'s green-full gate (Q34), so the list is never managed while the suite is failing.
- **`durations_report.py` exclusion block (`exclusion_block`)**: a named function behind `window_lines` (Q68), not folded into it. It returns `[]` when the run has no exclusions, so no block prints; otherwise a header then one line per excluded call through `_exclusion_line`. The faster-removed versus faster-lowered split reads `summary.floor` against the record's `current` (mirroring the rule's `_classify`, Q60), and `ok`, the slower-restore (Q57) and `stale` (Q61) read from the record status; `_current_text` renders `(not run)` for a stale entry.
- **`commands.py` report wiring (`_report_run_context`)**: emits `durations_report.exclusion_block(summary)` right after `window_lines(summary)` on a non-`None` summary, so the block follows the floor window (Q58); the docstring notes the added block.
- **Tests**: `test_groundhog_durations_report.py` adds the block cases -- the `ok` and slower-restore line, the lowered-baseline and below-floor-removed and stale-removed lines (split across two functions to stay under the radon `cc_min=C` gate), and the empty-list no-block case; `test_groundhog_commands.py` adds an integration run with a seeded `[exclusion]` freak within tolerance that exits 0, prints no outlier window, renders the block, and keeps the section.
- **Validation evidence**: one `ghog day` walk reported `exit=0` with the full suite at `100% (801/801) fail=0 warn=0 xfail=0 cov=100 outliers=0` (797 -> 801 with the four new tests). `check.bat` passed -- ty, pyright, ruff `select=["ALL"]`, radon (`cc_min=C`), vulture, the 700-line big-file scan and enforce_eof -- since the walk would have stopped at check otherwise.

### New types or classes introduced for Step 3

- `tools/groundhog/durations_report.py`: introduces no new production class. `exclusion_block` is a new public function with the private helpers `_exclusion_line`, `_current_text` and `_status_text`, function-style like the existing `window_lines` and its helpers; it reuses the `DurationExclusion` record and the `STATUS_*` constants from Step 2's `durations.py`.
- `tools/groundhog/durations_summary.py`: no new type; `_judge_map` gains the read / apply / write wiring only.
- Test support: `_excluded_summary` and the five `DurationExclusion` fixtures in `test_groundhog_durations_report.py`, and the seeded-section `test_full_run_spares_an_excluded_call` run in `test_groundhog_commands.py`.

### Architecture check for Step 3

- **Report layer (`durations_report.py`)**: now imports `durations` at runtime for the `STATUS_*` constants and the value-object annotations, still a one-way report-over-rule dependency -- `durations` imports no report or IO module, so there is no cycle. The block is pure string building, no IO, kept out of `reporting.py` so that module holds its budget.
- **Application seam (`durations_summary.py`)**: owns the read / apply / write across `exclusions.py` (the IO seam), `durations.py` (the pure rule) and `floor.py`, the correct orchestration-over-rule-and-IO direction; the rule stays IO-free and `exclusions.py` only persists the map handed to it. The read-before-`write_floor`, write-after ordering keeps the floor lines user-owned and the section intact across the floor rewrite.
- **Command wiring (`commands.py`)**: emits the block through `durations_report`, with no rule or IO logic added; the file is 551 lines, under the 700-line big-file gate, and `durations_report.py` (142) and `durations_summary.py` (100) stay well under it.

No DDD-Hexagonal violation or adapter smell is visible, and no, there is nothing that needs to be addressed.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: the wiring adds one section read, one `apply_exclusions` pass (Step 2, one pass over the outliers, the exclusion map and the call map with `O(1)` lookups) and one guarded write; the report block is one pass over the records. No sort is added beyond the v0.2.0 rule's existing one.
- **Hot-path bound**: `O(1)` amortized per excluded entry -- spare, classify and render are each a constant-cost step per entry.
- **Startup or background path**: the read is a single file read and the write a single atomic side-file replace, beside the floor write; the non-empty-section guard skips the extra write on a run with no exclusions, so a clean run keeps its one floor write.
- **Plan-bound alignment**: `O(n)` total per run over the call map and the entry map, inside the plan's `O(1)`-per-entry / `O(n)`-per-run target.

The step stays inside the plan's complexity target, and no, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

- **`tools/groundhog/durations_report.py`**: covered at 100% by `test_groundhog_durations_report.py`. The three `window_lines` shapes are unchanged, and `exclusion_block` is reached for every verdict -- `ok`, slower-restore, faster-lowered (above the floor), faster-removed (below the floor) and stale -- plus the empty-list no-block case, so `_exclusion_line`, `_current_text` (the seconds and the `(not run)` branch) and every branch of `_status_text` are hit.
- **`tools/groundhog/durations_summary.py`**: covered at 100% through the `test_groundhog_commands.py` integration runs, the same way the seam was covered in v0.2.0. The empty-section branch (`if not exclusion_map: return summary`) is reached by the existing full-run tests on a fresh root, and the non-empty read / apply / write branch by the new `test_full_run_spares_an_excluded_call` run.
- **`tools/groundhog/commands.py`**: the added emit line runs on every full-run report (a non-`None` summary); the block is empty on a run with no exclusions, so the line is covered by the existing tidy and slow runs and exercised with content by the new excluded-freak run.

The `ghog day` walk reported `cov=100`, consistent with this reasoning.

No, there is no unit-tested class below 100% that needs completing for Step 3.

### Feature integrity for Step 3

- **Existing feature behavior**: unchanged. `window_lines` is byte-stable, and the floor window, the v0.2.0 outlier rule and the exit-code contract are untouched; a run with no `[exclusion]` section behaves exactly as before -- the guard returns the plain summary and the block is empty. The 801-test suite stays green at `fail=0`.
- **Reporting or diagnostics**: extended, not changed. The exclusion block prints only when the run carries exclusions, after the floor window; the closing key=value line is unchanged in this step -- the `excluded=` field is Step 4.
- **Compatibility or rollout note**: the section is read before the floor rewrite and written back after it, so the floor lines (1 and 2) stay user-owned and the section survives the rewrite; `a.ghog.outliers` stays git-ignored under the `a.*` pattern, so no `.gitignore` change is needed.

No existing feature or reporting capability appears impaired.

---

## Step 4. Classify drift, add the exclusion command, and reword the hint

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because the closing line carries no `excluded=` field, the exit-8 hint still names line 2, and there is no `ghog` add-exclusion subcommand.

### Goal for Step 4

Drive exit 8 from a slower-drifted exclusion, carry `excluded=` of the slower-drifted calls on the closing line, reword the exit-8 hint to name the `ghog` add-exclusion command, and add that subcommand.

### Step 4 improvement expectations

- a slower-drifted excluded call keeps an otherwise-green run on exit 8; a faster or stale entry is auto-managed and leaves the exit unchanged; an excluded-ok run stays exit 0.
- the closing key=value line carries `excluded=<count>` of slower-drifted calls; `excluded=0` on a clean exclusion list.
- the exit-8 next-step hint names the `ghog` add-exclusion command and `fix_slow_test.md`, not raising line 2.
- a `ghog` add-exclusion subcommand takes the node id and its measured time and writes the entry through `exclusions.py`.

### What was implemented for Step 4

To be filled at the implementation check for Step 4.

### New types or classes introduced for Step 4

To be filled at the implementation check for Step 4.

### Architecture check for Step 4

To be filled at the implementation check for Step 4.

### Performance check for Step 4

To be filled at the implementation check for Step 4.

### Unit test coverage check for Step 4

To be filled at the implementation check for Step 4.

### Feature integrity for Step 4

To be filled at the implementation check for Step 4.

---

## Step 5. Update the fix-slow-test guidance

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because `fix_slow_test.md` and `groundhog.md` still tell a must-stay-slow call to raise line 2.

### Goal for Step 5

Move the must-stay-slow guidance from raising line 2 to running the `ghog` add-exclusion command, in `fix_slow_test.md` and `groundhog.md`.

### Step 5 improvement expectations

- `instructions/fix_slow_test.md` "when a call has to stay slow" tells the LLM to run the `ghog` add-exclusion command with the call's measured time and states the two-second baseline rule, and no longer says raise line 2 or hand-edit the file for one call.
- `instructions/groundhog.md` exit-8 section points a must-stay-slow call at the `ghog` add-exclusion command and describes line 2 as project-wide floor tuning.
- both files follow the markdown rules and carry no blacklisted word.

### What was implemented for Step 5

To be filled at the implementation check for Step 5.

### New types or classes introduced for Step 5

To be filled at the implementation check for Step 5.

### Architecture check for Step 5

To be filled at the implementation check for Step 5.

### Performance check for Step 5

To be filled at the implementation check for Step 5.

### Unit test coverage check for Step 5

To be filled at the implementation check for Step 5.

### Feature integrity for Step 5

To be filled at the implementation check for Step 5.

---

## Step 6. Acceptance tests for excluded and drifted runs

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because the acceptance scenarios for the exclusion states do not exist yet.

### Goal for Step 6

Add acceptance tests that drive a `ghog full` run through the excluded-ok, slower-drift, faster and stale states, and through the `ghog` add-exclusion command.

### Step 6 improvement expectations

- an excluded-call run within tolerance exits 0, reports the call `ok`, and prints no outlier window.
- a slower-drift run exits 8 with the restore instruction and `excluded=1` on the closing line.
- a faster run shows the tool lower the baseline on a more-than-two-second improvement, or remove the entry once below the floor, and stays exit 0; a stale-entry run shows the entry removed and stays exit 0.
- the add-exclusion subcommand writes a new entry with its measured time as the baseline; `test_groundhog_acceptance_durations.py` stays under its line budget.

### What was implemented for Step 6

To be filled at the implementation check for Step 6.

### New types or classes introduced for Step 6

To be filled at the implementation check for Step 6.

### Architecture check for Step 6

To be filled at the implementation check for Step 6.

### Performance check for Step 6

To be filled at the implementation check for Step 6.

### Unit test coverage check for Step 6

To be filled at the implementation check for Step 6.

### Feature integrity for Step 6

To be filled at the implementation check for Step 6.
