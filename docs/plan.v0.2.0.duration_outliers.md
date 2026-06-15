# v0.2.0 duration-outliers implementation plan -- timing ghog full and gating on true outliers

This plan turns the decisions Q34 to Q47 of `design.v0.2.0.duration_outliers.md`
into ordered, test-first slices, each one a green `ghog day` walk.

- **Capture then judge**: parse pytest's own `slowest durations` block into the run
  stats, then judge it with a pure rule and a self-managed floor file.
- **One floor, generous by default**: a call is a true outlier only when it is far
  out and at least `k` times the median, so a slower test is spared.
- **Report and gate**: the final line and bar carry `avg=`/`outliers=`, exit 8
  keeps the loop fixing, and the report lists the above-floor calls to fix.

## Plan goal for the duration-outliers feature

Implement the full feature described in `design.v0.2.0.duration_outliers.md`
(decisions Q34 to Q47), in ordered slices that each leave the suite green.

- **Step 1 goal**: capture per-call durations from `ghog full` into `RunStats`.
- **Step 2 goal**: the pure true-outlier rule, the average, and the report window.
- **Step 3 goal**: the two-line `a.ghog.outliers` floor file and its resolution.
- **Step 4 goal**: classification (exit 8), the `avg=`/`outliers=` output, and the
  windowed report wiring.
- **Step 5 goal**: the skill instruction exit-8 branch and the LLM fix playbook.
- **Step 6 goal**: acceptance tests for the green-but-slow run and its variants.

---

## Scope anchors for the duration-outliers plan

This plan implements the spec, targeting these outcomes:

1. `ghog full` times every test call and judges only true outliers (Q35, Q46).
2. The final progress line and the closed bar carry `avg=` and `outliers=` (Q37).
3. A true outlier on an otherwise-green run returns exit 8 and drives the fix loop
   (Q34, Q41, Q44).
4. The floor is the two-line `a.ghog.outliers`, auto value and user override (Q38,
   Q40, Q43, Q45).
5. The report shows a bounded window around the floor; the fix instruction names
   only the above-floor calls (Q47).

The following are explicitly **in scope**:

- duration capture on the `full` subcommand only (Q39).
- the call-phase metric (Q36); the average excludes outliers.
- the LLM fix instructions in `instructions/groundhog.md` (Q44).

The following are explicitly **deferred**:

- a separate slow-fixture (setup-phase) list (Q36 notes it as a later add).
- duration capture on `affected` or `single` runs (Q39).

---

## Complexity bound clarification for the duration-outliers plan

The scaling target for every new code path:

- **O(1) per streamed line**: the parser's duration-line capture is a constant-cost
  branch per output line, like the coverage-table capture beside it.
- **O(n) to O(n log n) once per full run**: `n` is the collected test count; the
  median, the MAD and the outlier scan run once at end of run. A single sort is the
  only `n log n`; no path is `O(n^2)`.

The floor file read and write are two-line operations, not scans.

---

## File-based IO cost clarification for the duration-outliers plan

The feature adds one small runtime file, read once and written once per full run:

- `a.ghog.outliers` is two lines; reading it at run start is a tiny index-read, not
  a metadata-loading delay.
- the write at run end uses the atomic side-file replace already used by
  `snapshot.py` (`a.ghog.day.ok`) and `status.py` (`a.ghog.status`).
- no directory scan is added on any path; the durations come from the stream the
  parent already reads (Q37), not from a second pytest or coverage invocation.

---

## Confirmed technical facts for the duration-outliers plan viability

Drawn from direct inspection of the current tree.

**Files at or approaching the 550-line risk threshold** (must not grow much):

- `tools/groundhog/commands.py`: **499 lines** -- the one real budget risk. New
  full-run post-processing must live in the new pure modules; `commands.py` only
  calls them. Target after edits <= 545; if exceeded, a follow-up split phase.

**Files safe to extend** (current lines, expected additions):

- `tools/groundhog/reporting.py`: 325 -- about +50 to +70 for `avg=`/`outliers=`,
  the exit-8 next-step and the override hint; heavy window rendering stays in the
  new `durations.py`, so it lands well under 550.
- `tools/groundhog/parser.py`: 146 -- about +25 for the durations-section capture.
- `tools/groundhog/runner.py`: 137 -- about +4 for the `--durations` flags.
- `tools/groundhog/models.py`: 78 -- about +6 for the field and the exit code.
- `tools/groundhog/__init__.py`: 42 -- one export line.

**Files unchanged** (clarifying the spec's touch list):

- `tools/groundhog/render.py`: 42 -- the tqdm wrapper and `ProgressBar` protocol are
  untouched; the bar postfix and the final LLM line are built in `commands.py`
  (`_Progress`, `postfix`) and `reporting.py` (`progress_line`), which is where the
  progress changes land.

**What does not exist yet (all new)**:

- `tools/groundhog/durations.py`.
- `tools/groundhog/floor.py`.
- `tests/unit/tools/test_groundhog_durations.py`.
- `tests/unit/tools/test_groundhog_floor.py`.
- `tests/unit/tools/test_groundhog_acceptance_durations.py`.

**Other confirmed technical facts**:

- **hypothesis is installed** in the project venv, but the repo uses no
  property-based test today; a bounded PBT for the rule is optional (Step 2), the
  100% gate is met by deterministic vectors.
- **no `pytest.mark.timeout` convention** exists in the repo; no perf-gate Step 0 is
  added (see the perf-gates pass below).
- **the groundhog test suite is flat**: `tests/unit/tools/test_groundhog_*.py`, with
  `tests/unit/tools/__init__.py` already present; new tests follow that layout, not
  the generic nested `test_*/test_*_tdd.py` form.

---

## Current test-tree validation snapshot for the duration-outliers plan

Existing test modules this plan must not break:

- `tests/unit/tools/test_groundhog_parser.py` (172) -- gains durations-block cases.
- `tests/unit/tools/test_groundhog_runner.py` (145) -- gains the `--durations` flag
  assertion for the full command.
- `tests/unit/tools/test_groundhog_reporting.py` (200) -- gains `avg=`/`outliers=`,
  closing-line and next-step cases.
- `tests/unit/tools/test_groundhog_acceptance.py` (346) -- left untouched; the new
  acceptance scenarios go in their own module, mirroring the existing split of
  `test_groundhog_acceptance_day.py`.

New test modules to create:

- `tests/unit/tools/test_groundhog_durations.py` (and an optional
  `test_groundhog_durations_pbt.py`).
- `tests/unit/tools/test_groundhog_floor.py`.
- `tests/unit/tools/test_groundhog_acceptance_durations.py`.

No new `__init__.py` is needed: `tests/unit/tools/__init__.py` and
`tools/groundhog/__init__.py` already exist; the latter is updated, not created.

---

## Runtime file note for the duration-outliers plan

- `a.ghog.outliers` -- the floor file, written at the project root, same `a.ghog.*`
  family and `.gitignore` coverage as `a.ghog.failures`, `a.ghog.day.ok` and
  `a.ghog.status` (Q38). Confirm the ignore pattern covers it before Step 3 closes.

---

## Shared execution command checklist for all duration-outliers steps

Apply this for every numbered step, filling in the step-specific paths.

1. Count lines before edits on every file the step touches (line-count command
   below).
2. Apply the tests-first changes described under the step's implementation section.
3. Run the step-targeted tests through groundhog (ready-to-run command below).
4. Run the step grep checks.
5. Run the shared gate loop (`ghog day`) until it reports the objective in one walk.
6. Count lines after edits and compare with the step's line-budget checkpoint.
7. If any Python file is over the line-limit rule after edits, stop and apply the
   step's split guidance before moving on.

---

## Ready-to-run command templates for all duration-outliers steps

Substitute actual paths per step.

- Line count before/after: `(Get-Content <file> | Measure-Object -Line).Lines`.
- Targeted tests: `ghog single <step test files>` (groundhog runs them; never a
  direct `pytest`).
- Grep checks: `rg <pattern> tools/groundhog tests/unit/tools`.
- Shared gate loop: `ghog day`, repeated fix-and-walk until `exit=0` -- it runs
  check.bat, the affected tests, then the full coverage pass, stopping at the first
  non-green step (see `GROUNDHOG.md`). Do not plan direct `check.bat` or `pytest`
  calls; groundhog owns check and tests.

---

## Shared timeout target policy: Step 0 perf-gates pass for the duration-outliers plan

No `pytest.mark.timeout` Step 0 is added. The feature's new work is an end-of-run,
once-per-walk computation over the collected test count (Q37), not a response-path
or event-loop hot path, so a time-bound xfail gate guards nothing real; the repo
also has no such convention to extend. The ironic risk that the rule's own tests
become slow is handled by keeping them deterministic and tiny, and by bounding the
optional PBT's example count and deadline.

---

## Numbered steps for the duration-outliers feature

### Step 1. Capture per-call durations into RunStats

#### Step 1 -- analysis and intent for duration capture

Issues to address:

- `ghog full` carries no per-call timing; the `-v` result line has no time (spec,
  What ghog full measures today).

Fix intent:

- give the full command pytest's `--durations` output, and parse the
  `slowest durations` block into a new `RunStats.durations` map, call phase only.

Expected outcome:

- after a full run, `RunStats.durations` maps each node id to its call seconds;
  non-full runs leave it empty (Q39).

Step framing:

- Design link: Capturing per-call durations (Q36, Q39).
- Execution checklist reference: Shared execution command checklist.

#### Step 1 -- implementation for duration capture

**Files involved**:

- `tools/groundhog/models.py` (update).
- `tools/groundhog/runner.py` (update).
- `tools/groundhog/parser.py` (update).
- `tests/unit/tools/test_groundhog_parser.py` (update).
- `tests/unit/tools/test_groundhog_runner.py` (update).

**Tests first**:

- parser: feed a transcript whose tail holds a `slowest durations` block with
  `setup`, `call` and `teardown` lines; assert `stats.durations` holds only the
  call-phase seconds keyed by node, and that the block stops at the next banner and
  at the final summary line.
- parser: a transcript with no durations block leaves `stats.durations` empty.
- parser: a `call` line whose node id holds a space (a parametrized id) is captured
  whole, not chopped at the space (Q49).
- runner: `pytest_command(..., SUB_FULL, no_cov=False, ...)` contains
  `--durations=0` and `--durations-min=0`; the affected and single commands do not.

**Classes and behavior**:

- `RunStats.durations: dict[str, float]` (default empty) -- node id to call seconds.
- `runner.pytest_command`: the full branch appends `--durations=0 --durations-min=0`.
- `parser.PytestOutputParser`: a `slowest durations` banner opens a capture;
  `^\s*(?P<secs>\d+\.\d+)s\s+(?P<phase>setup|call|teardown)\s+(?P<node>.+\S)` records
  the seconds of `call` lines into `stats.durations`; the node group is `.+` so a
  parametrized id with spaces (`test_x[a b]`) is kept whole (Q49); the next banner or
  the summary line closes the capture.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "durations" tools/groundhog/parser.py tools/groundhog/runner.py`.
- a full-run transcript fixture yields a populated `durations` map.

#### Step 1 -- addendums for duration capture

Line-budget checkpoint:

- `tools/groundhog/parser.py`: before 146 -> target <= 175.
- `tools/groundhog/runner.py`: before 137 -> target <= 145.
- `tools/groundhog/models.py`: before 78 -> target <= 86.

Split guidance:

- none expected; if the parser capture grows past ~190, move the durations-section
  state into a small helper method, not a new file.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_groundhog_parser.py tests/unit/tools/test_groundhog_runner.py`; then `ghog day`.

Time-gated status for Step 1:

- no perf gates affected.

### Step 2. The true-outlier rule, the average and the report window

#### Step 2 -- analysis and intent for the rule

Issues to address:

- the durations map needs judging into true outliers, an average, and a printable
  window, with no floor logic leaking into other modules.

Fix intent:

- a pure `durations.py`: median, MAD, modified z-score, the `k * median` floor, the
  two-condition rule (Q46), the average excluding outliers, and the bounded window
  line builders (Q47), with the MAD-zero fallback.

Expected outcome:

- given a durations map and an active floor, `durations.py` returns a summary: the
  outliers (node, seconds, multiple of median), the runners-up under the floor, the
  average, the median and the floor used.

Step framing:

- Design link: Outlier criteria for a full run; Tuning the detection by hand (Q35,
  Q46, Q47).
- Execution checklist reference: Shared execution command checklist.

#### Step 2 -- implementation for the rule

**Files involved**:

- `tools/groundhog/durations.py` (new).
- `tests/unit/tools/test_groundhog_durations.py` (new).
- `tests/unit/tools/test_groundhog_durations_pbt.py` (new, optional PBT).

**Tests first**:

- a tidy suite (all calls near the median) yields zero outliers.
- one freak an order of magnitude above the median, far out by the z-score, is the
  single outlier; a call only two to three times the median is not.
- the average excludes the outliers.
- MAD zero (more than half the calls tie): the z-condition is dropped and only the
  floor decides, so a near-median call is not flagged (Q50).
- the window holds the flagged outliers (uncapped), the marked floor, then up to 3
  runners-up under it (Q51); an empty/whitespace map is handled.
- optional PBT (hypothesis, bounded examples and deadline): scaling all durations by
  a positive constant scales the floor proportionally and preserves the outlier set;
  adding a faster-than-median call never creates an outlier.

**Classes and behavior**:

- `K_DEFAULT` (about 10) and `MODZ_CUTOFF` (3.5) module constants.
- `auto_floor(durations) -> float`: `k * median` (Q46).
- `summarize(durations, floor) -> DurationSummary`: applies the two-condition rule
  (z-score and floor; floor only when the MAD is zero, Q50), builds the outlier list
  (node, seconds, ratio), up to 3 runners-up under the floor (Q51), the average.
- `DurationSummary`: `average`, `outliers`, `runners_up`, `floor`, `median`.
- `window_lines(summary) -> list[str]`: the bounded report window -- the uncapped
  outliers, the marked floor, then up to 3 runners-up (Q51); pure string building,
  kept here to protect the `reporting.py` budget.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "K_DEFAULT|MODZ_CUTOFF|def summarize|def auto_floor" tools/groundhog/durations.py`.
- `durations.py` carries no IO and no import from `commands`/`reporting`/`floor`.

#### Step 2 -- addendums for the rule

Line-budget checkpoint:

- `tools/groundhog/durations.py`: new -> target <= 230.
- `tests/unit/tools/test_groundhog_durations.py`: new -> target <= 260.

Split guidance:

- if `durations.py` passes ~230, move `window_lines` into a `durations_report.py`
  (new), keeping the stats in `durations.py`.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_groundhog_durations.py`; then `ghog day`.

Time-gated status for Step 2:

- the optional PBT must set a bounded deadline and example count so it never becomes
  a duration outlier itself.

### Step 3. The two-line floor file

#### Step 3 -- analysis and intent for the floor file

Issues to address:

- the floor must persist across runs as the two-line `a.ghog.outliers`, with the
  auto value, the user override, the active-floor resolution and the atomic write
  (Q38, Q40, Q43, Q45).

Fix intent:

- a `floor.py` beside `gate.py` and `snapshot.py`: read the override (line 2),
  resolve the active floor (the override when set, else this run's freshly computed
  auto -- line 1 is write-only and never read for gating, Q48), write line 1 from
  the run and reset line 2 to `-1` when the file is absent.

Expected outcome:

- the active floor is the override (line 2) when positive, else this run's auto
  `k * median` (Q48); a missing file means auto floor with override `-1`; the write
  is atomic.

Step framing:

- Design link: The floor file (Q38, Q40, Q43, Q45).
- Execution checklist reference: Shared execution command checklist.

#### Step 3 -- implementation for the floor file

**Files involved**:

- `tools/groundhog/floor.py` (new).
- `tests/unit/tools/test_groundhog_floor.py` (new).
- `.gitignore` (verify, update only if `a.ghog.*` is not already covered).

**Tests first**:

- a missing file resolves to the given auto value with override `-1`.
- a file with override `-1` resolves to the freshly computed auto -- line 1 is not
  read for gating (Q48); a positive override resolves to the override.
- `write_floor` writes both lines atomically (a side-file replace) and round-trips.
- a malformed or partial file falls back to the auto value, never crashing the run.

**Classes and behavior**:

- `FLOOR_FILE = "a.ghog.outliers"`.
- `read_floor(root) -> float | None`: the override (line 2), `None` when absent or
  `-1` (Q48).
- `active_floor(override, auto) -> float`: the override when set (>= 0), else the
  freshly computed `auto` (Q48).
- `write_floor(root, auto, override) -> None`: atomic two-line write; line 1 = `auto`
  (this run's `k * median`, a write-only record), line 2 = the preserved override.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "a.ghog.outliers" tools/groundhog/floor.py .gitignore`.
- a round-trip test proves read after write returns the same two numbers.

#### Step 3 -- addendums for the floor file

Line-budget checkpoint:

- `tools/groundhog/floor.py`: new -> target <= 130.
- `tests/unit/tools/test_groundhog_floor.py`: new -> target <= 150.

Split guidance:

- none expected; the module is small and self-contained.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_groundhog_floor.py`; then `ghog day`.

Time-gated status for Step 3:

- no perf gates affected.

### Step 4. Classification, progress output and report wiring

#### Step 4 -- analysis and intent for gating and report

Issues to address:

- the durations summary and floor must reach the exit code, the progress line, the
  bar and the report, without growing `commands.py` past its budget.

Fix intent:

- add `EXIT_DURATION_OUTLIERS` (8); compute the summary for full runs in
  `run_tests`; classify exit 8 when green, coverage-clear and outliers remain (Q34,
  Q41); add `avg=`/`outliers=` to the final progress line, the bar postfix and the
  closing line (Q37); emit the windowed report and the next-step on exit 8 (Q47);
  write the auto floor after the run (Q42).

Expected outcome:

- a green-but-slow full run exits 8, the final line and closing line carry `avg=`
  and `outliers=`, and the report lists the above-floor calls with the fix; a tidy
  run exits 0 with `outliers=0`.

Step framing:

- Design link: Clean bill with zero outliers; Average and outliers in the progress
  output; Report and next step for outliers (Q34, Q37, Q41, Q42, Q44, Q47).
- Execution checklist reference: Shared execution command checklist.

#### Step 4 -- implementation for gating and report

**Files involved**:

- `tools/groundhog/models.py` (update: the exit code).
- `tools/groundhog/__init__.py` (update: export the exit code).
- `tools/groundhog/commands.py` (update: summary wiring, classify, `_Progress`,
  `postfix`).
- `tools/groundhog/reporting.py` (update: `progress_line`, `closing_line`,
  `next_after_full`, the messages and the override hint).
- `tests/unit/tools/test_groundhog_reporting.py` (update).

**Tests first**:

- reporting: `progress_line` with a summary appends `avg=` and `outliers=`; without
  one it is unchanged. `closing_line` carries `outliers=<n>` for full and
  `outliers=skipped` otherwise. `next_after_full` returns the outlier next-step and
  override hint on exit 8.
- reporting/commands: a green run with outliers classifies exit 8; the same run with
  a raised override classifies exit 0; a failing or coverage-gap run keeps its own
  exit code (outliers judged last).
- commands: `_Progress.finish` emits the final LLM line and the bar postfix with
  `avg=`/`outliers=` only for full runs.

**Classes and behavior**:

- `models.EXIT_DURATION_OUTLIERS = 8`.
- `commands.run_tests`: for full, read the override (`floor.py`), compute
  `auto = k * median` from this run (`durations.py`), resolve the active floor
  (override else auto, Q48), summarize, count outliers, write line 1 = `auto` and
  line 2 = override, pass the count to `classify`.
- `commands.classify(..., outlier_count=0)`: exit 8 only when not crashed, not
  failing, coverage clear and `outlier_count > 0`.
- `commands._Progress.finish`: emits exactly one final summary line carrying
  `avg=`/`outliers=` for full runs (the authoritative last line; a preceding governor
  100% line is left as ordinary progress, Q52); `commands.postfix` carries the same
  values on the bar.
- `reporting.progress_line(sub_label, stats, summary=None)`,
  `reporting.closing_line(..., outliers_value)`, `reporting.next_after_full(exit_code,
  failing_files, summary)`, plus `MSG_OUTLIERS_*` and the override hint;
  `durations.window_lines` builds the body.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "EXIT_DURATION_OUTLIERS|outliers=" tools/groundhog`.
- a green-but-slow acceptance-style fixture returns exit 8 with the windowed list.

#### Step 4 -- addendums for gating and report

Line-budget checkpoint:

- `tools/groundhog/commands.py`: before 499 -> target <= 545 (hard watch).
- `tools/groundhog/reporting.py`: before 325 -> target <= 395.
- `tools/groundhog/models.py`: before 84 (after Step 1) -> target <= 90.

Split guidance:

- if `commands.py` crosses 545, extract the full-run post-processing (read floor,
  summarize, classify-with-outliers, write floor) into a `durations_summary(...)`
  helper in `durations.py`, leaving `commands.run_tests` a thin call; keep the
  window rendering in `durations.py`, not `reporting.py`.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_groundhog_reporting.py`; then `ghog day`.

Time-gated status for Step 4:

- no perf gates affected.

### Step 5. The skill instruction exit-8 branch and LLM fix playbook

#### Step 5 -- analysis and intent for the fix instructions

Issues to address:

- the loop and the instruction file must route exit 8 to the outlier fix playbook,
  above-floor calls only (Q44, Q47).

Fix intent:

- add an exit-8 branch and the LLM fix steps to `instructions/groundhog.md`, beside
  the exit-2 and exit-3 guidance.

Expected outcome:

- on exit 8 the loop reads: fix only above-floor outliers; per-cause techniques;
  the override escape for a legitimately slow call; confirm with `ghog single`;
  restart with `ghog day`.

Step framing:

- Design link: Fixing an outlier: instructions for the LLM (Q44, Q47).
- Execution checklist reference: Shared execution command checklist.

#### Step 5 -- implementation for the fix instructions

**Files involved**:

- `instructions/groundhog.md` (update).

**Tests first**:

- no unit test (documentation); the completion grep below is the check. If an init
  or acceptance test already asserts instruction-file contents, extend it to mention
  the exit-8 branch.

**Classes and behavior**:

- the instruction file gains an exit-8 loop branch and the five-step fix playbook
  (fix above-floor only; fake I/O; fake the clock; shrink data; move per-call
  construction to a fixture; override if legitimately slow; confirm; `ghog day`).

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "exit 8|outlier" instructions/groundhog.md`.

#### Step 5 -- addendums for the fix instructions

Line-budget checkpoint:

- `instructions/groundhog.md`: documentation; keep the new branch concise.

Split guidance:

- none.

Full workflow timing run readiness:

- `ghog day`.

Time-gated status for Step 5:

- no perf gates affected.

### Step 6. Acceptance tests for the green-but-slow run

#### Step 6 -- analysis and intent for acceptance

Issues to address:

- the slices need an end-to-end proof driving `cli.main` with a canned transcript,
  the spec's final-step requirement.

Fix intent:

- a new acceptance module exercising the green-but-slow run and its variants through
  the real parser, rule, floor, classification and report.

Expected outcome:

- a green transcript with a `slowest durations` block holding one freak exits 8,
  prints the windowed list and the fix, writes `a.ghog.outliers`, and shows
  `avg=`/`outliers=`; a tidy transcript exits 0; a raised override exits 0; a missing
  file seeds the floor and still reports.

Step framing:

- Design link: the whole spec; the final-step acceptance requirement.
- Execution checklist reference: Shared execution command checklist.

#### Step 6 -- implementation for acceptance

**Files involved**:

- `tests/unit/tools/test_groundhog_acceptance_durations.py` (new).

**Tests first**:

- AT-D1 green-but-slow: exit 8, windowed list with node/time/ratio, `outliers>=1`,
  `a.ghog.outliers` written, `avg=` present.
- AT-D2 tidy green: a durations block with no freak exits 0, `outliers=0`.
- AT-D3 override: a pre-written `a.ghog.outliers` with line 2 above the freak exits
  0.
- AT-D4 first run / no file: the file is absent, the run seeds line 1, resets line 2
  to `-1`, and still reports the outliers.
- AT-D5 precedence: a failing transcript with a durations block keeps exit 2 and
  withholds the timing verdict (outliers judged last).

**Classes and behavior**:

- the new module reuses the acceptance harness style (canned transcript and exit
  code through the runner's process factory), asserting parsing, rule, floor,
  classification and report together.

**Completion criteria**:

- `ghog day` reports the objective (`exit=0`).
- `rg "AT-D|durations" tests/unit/tools/test_groundhog_acceptance_durations.py`.
- the five scenarios pass and the repo coverage gate holds.

#### Step 6 -- addendums for acceptance

Line-budget checkpoint:

- `tests/unit/tools/test_groundhog_acceptance_durations.py`: new -> target <= 320.

Split guidance:

- keep these out of `test_groundhog_acceptance.py` (346) so neither file nears the
  limit; mirror the `test_groundhog_acceptance_day.py` split already in the suite.

Full workflow timing run readiness:

- `ghog single tests/unit/tools/test_groundhog_acceptance_durations.py`; then
  `ghog day`.

Time-gated status for Step 6:

- no perf gates affected; the acceptance transcripts are canned, so they add no real
  runtime.

---

## Implementation decisions for the v0.2.0 duration-outliers plan

The table folds in the answered plan questions Q48 to Q52, the step that carries
each, and the alternatives dropped. The design decisions are Q34 to Q47 in
`design.v0.2.0.duration_outliers.md`.

| Question | Decision | Step | Main argument | Rejected alternatives |
| --- | --- | --- | --- | --- |
| Q48 | Gate on this run's freshly computed `k * median` when the override is `-1`; line 1 is write-only, only line 2 (override) is read for gating | Step 3, Step 4 | The convergence of Q43 rests on each run judging itself; a stale line 1 reintroduces a one-run lag and leaves the first run with nothing to read | Q48-b read the persisted line 1 (one-run lag, no first-run value) |
| Q49 | Capture the durations node id as `.+`, so parametrized ids with spaces enter the median, average and outlier set | Step 1 | A slow parametrized test must not be invisible to the rule; the `done`/durations count gap is harmless | Q49-b `\S+` (drops or chops space-containing params) |
| Q50 | When the MAD is zero, drop the z-condition and require only the floor | Step 2 | An epsilon flags every above-median call on a zero-spread suite; floor-only keeps the order-of-magnitude meaning | Q50-b epsilon MAD (flags slower tests); Q50-c another spread measure (machinery for a corner case) |
| Q51 | Up to 3 runners-up under the floor; the flagged-outlier list is uncapped | Step 2, Step 4 | The flagged list is a work list (every call must be fixed); three runners-up suffice to judge "too few" | Q51-b cap the flagged list (hides fix targets); Q51-c five runners-up (more quiet-run noise) |
| Q52 | `_Progress.finish` emits exactly one final summary line for full runs; the governor's prior 100% line stays as ordinary progress | Step 4 | The summary always appears once with no governor coupling; the bare-then-summary pair is cosmetic and self-explaining | Q52-b suppress the governor at 100% (governor coupling); Q52-c overwrite the last line (not possible with line logging) |
