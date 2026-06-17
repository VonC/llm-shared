# v0.3.0 duration_outliers_exclusion implementation tracking and validation

No, it is not implemented.

This document tracks, step by step, the build of the tool-managed `[exclusion]` section against [`plan.v0.3.0.duration_outliers_exclusion.md`](plan.v0.3.0.duration_outliers_exclusion.md). Step 1 is built and green: `exclusions.py` reads and writes the `[exclusion]` section. The rule post-step, the report block, the closing-line field, the `ghog` add-exclusion command and the guidance updates remain. Each step's evidence is filled at its implementation check.

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

Not started. Step 2 is not implemented because the rule post-step does not exist yet.

`durations.summarize` still has no exclusion handling, and `DurationSummary` carries no excluded-call list.

### Goal for Step 2

Add a post-step over `DurationSummary` that spares excluded calls from the outliers and the average and classifies each excluded node against its baseline, leaving `summarize` and its test vectors unchanged.

### Step 2 improvement expectations

- the post-step spares any flagged call whose node is excluded and leaves excluded calls out of the average; the median, MAD and floor are computed over the whole run, unchanged by exclusion; `summarize` is unchanged.
- each excluded entry carries node, recorded, current and a status: `ok` within two seconds, `slower` when `current - recorded > 2s`, `faster` when `recorded - current > 2s`, `stale` when the node ran no call this run.
- the section update lowers a baseline only on a more-than-two-second improvement (Q69) and marks a below-floor or stale entry for removal; a faster reading within two seconds leaves the baseline alone.
- `durations.py` stays pure and under its line budget; the rule reaches 100% coverage.

### What was implemented for Step 2

To be filled at the implementation check for Step 2.

### New types or classes introduced for Step 2

To be filled at the implementation check for Step 2.

### Architecture check for Step 2

To be filled at the implementation check for Step 2.

### Performance check for Step 2

To be filled at the implementation check for Step 2.

### Unit test coverage check for Step 2

To be filled at the implementation check for Step 2.

### Feature integrity for Step 2

To be filled at the implementation check for Step 2.

---

## Step 3. Wire exclusions into the run and the report

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because `durations_summary.py` does not read or write the exclusion section and `durations_report.py` renders no exclusion block.

### Goal for Step 3

Have `durations_summary` read the exclusion map, apply the post-step, and write the section back through `exclusions.py`; have `durations_report` render the exclusion block after the floor window.

### Step 3 improvement expectations

- `durations_summary.py` reads the exclusion map, applies the post-step, then writes the section back through `exclusions.py` -- baselines ratcheted down, below-floor and stale entries removed -- the only place the tool writes the section.
- the whole exclusion pass forms only on a full run already green on tests and coverage (Q34), so the list is never managed while the suite is failing.
- `durations_report.py` renders, per excluded call, `ok`, the restore instruction when slower, the lowered baseline on a real improvement, or `removed` (below floor or stale), and no block on an empty list.
- `test_groundhog_durations_report.py` covers the four lines and the no-block case.

### What was implemented for Step 3

To be filled at the implementation check for Step 3.

### New types or classes introduced for Step 3

To be filled at the implementation check for Step 3.

### Architecture check for Step 3

To be filled at the implementation check for Step 3.

### Performance check for Step 3

To be filled at the implementation check for Step 3.

### Unit test coverage check for Step 3

To be filled at the implementation check for Step 3.

### Feature integrity for Step 3

To be filled at the implementation check for Step 3.

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
