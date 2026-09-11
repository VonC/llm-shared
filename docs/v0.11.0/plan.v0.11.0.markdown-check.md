# v0.11.0 Markdown checker implementation plan: one policy authority

Build the checker from a shared source model, add its policy and baseline
runner, then connect that same command to the repository gate.

- **Shared parsing**: parse each tracked Markdown file once and reuse the model
  for classification and rule evaluation.
- **Bounded policy**: load the explicit supported catalog and compare findings
  with repository-root `.markdownlint-baseline.json`.
- **One observable result**: expose a direct launcher and make `check.bat`
  record the same exit status.

> Markdown lint note: avoid unnecessary spaces immediately inside an inline code
> span (MD038), but keep spaces that genuinely belong to the parsed code value,
> space-only spans, and matching delimiter padding around literal backticks. End
> a line made only of italic text with punctuation after the closing marker
> (MD036).

## Plan goal for v0.11.0 Markdown checking

Implement the consolidated requirement and design in three ordered slices.

- **Step 1 goal**: create the fence-aware source model and supported rule
  evaluators.
- **Step 2 goal**: add configuration, inventory, baseline, diagnostics, and the
  direct repository launcher.
- **Step 3 goal**: clear zero-debt findings, wire the shared gate, add acceptance
  coverage, and publish the reference contract.

No Step 0 timeout gate is needed. The checker is a batch repository command,
not a latency-sensitive event path; linear-scaling properties and the ordinary
groundhog timing report cover its performance risk.

## Scope anchors for the v0.11.0 Markdown-check plan

This plan targets three outcomes:

1. Every tracked Markdown file is classified and checked under the supported
   catalog without Node or network access.
2. Findings, operational errors, baseline comparisons, and exit status follow
   one documented contract.
3. The direct launcher and `check.bat` call the same implementation.

In scope are the Python checker package, root launcher, tracked baseline, shared
heading-scanner extraction, tests, historical zero-debt repairs, gate wiring,
and focused reference documentation.

Deferred are automatic fixes, changed-file-only mode, editor integration,
complete external markdownlint compatibility, and review-renderer changes.

## Complexity bound for the v0.11.0 Markdown checker

- Inventory, decoding, parsing, classification, rule evaluation, grouping, and
  sorting are bounded by the tracked Markdown population and its total text.
- Each source file is parsed once; rule evaluation over its source model remains
  linear in its recorded headings, lists, and raw-HTML tokens.
- Keyed baseline lookup is constant time on average. Deterministic final sorting
  may be `O(f log f)` for `f` findings and does not reopen files.
- No path may scan the complete repository separately for each rule or baseline
  entry.

## File-based IO cost clarification for the v0.11.0 Markdown-check plan

- Run one `git ls-files` inventory query per checker invocation.
- Read `.markdownlint.json` and `.markdownlint-baseline.json` once.
- Decode each tracked Markdown file once and share its source model.
- Keep findings and baseline groups in memory until ordered output is rendered.
- Never write the baseline or a source document during normal checker execution.

## Confirmed technical facts for v0.11.0 plan viability

**Existing Python files below 550 lines and safe to extend**:

- `tools/review_markdown_headings.py`: 87 lines; plan-local ceiling 650.
- `tests/unit/tools/test_review_markdown_headings_tdd.py`: 104 lines;
  plan-local ceiling 650.

**Existing non-Python files involved in rollout**:

- `check.bat`: 215 physical lines and an existing
  `record_failure <name> <status>` aggregation point.
- `.claude/skills/humanizer/SKILL.md`: 412 physical lines and one measured
  `MD032` repair at line 260.
- `.markdownlint.json`: the current MD013 and MD033 policy authority.

The enforced Python big-file default is 700 lines in `check.bat`,
`bin/check_big_files.bat`, and `bin/python_check.bat`, with no repository
override. This plan deliberately uses 650 as a stricter local split checkpoint,
not as a claim about the current gate.

**New production files, all starting at zero lines**:

- `tools/markdown_check/__init__.py`.
- `tools/markdown_check/models.py`.
- `tools/markdown_check/source.py`.
- `tools/markdown_check/classifier.py`.
- `tools/markdown_check/rules.py`.
- `tools/markdown_check/policy.py`.
- `tools/markdown_check/baseline.py`.
- `tools/markdown_check/runner.py`.
- `tools/markdown_check/cli.py`.
- `markdown-check.bat`.
- `.markdownlint-baseline.json`.

The package runs in place, matching `tool.uv.package = false`. Coverage remains
100 percent for executable code under `tools/`.

## Current test-tree validation snapshot for v0.11.0 Markdown checking

Existing coverage to preserve:

- `tests/unit/tools/test_review_markdown_headings_tdd.py`: fence-aware review
  heading transformation.
- `tests/unit/tools/test_enforce_eof.py` and branch coverage: root-tool behavior
  that gate wiring must not disturb.
- Groundhog acceptance tests under `tests/unit/tools/`: subprocess and temporary
  repository patterns for larger workflow checks.

New test package roots:

- `tests/unit/tools/markdown_check/` for source, rule, policy, baseline, runner,
  and launcher unit tests.
- `tests/acceptance/markdown_check/` for repository-fixture and shared-gate
  acceptance tests.

Property-based coverage is required for heading normalization, hierarchy
streams, and baseline count comparison. No time-bound `xfail` test is needed.

## Implementation decisions for v0.11.0 Markdown checking

| Question | Decision | Integrated in | Rejected alternatives |
| --- | --- | --- | --- |
| Q01 | Publish repository-root `markdown-check.bat` for Windows and `python -m tools.markdown_check.cli` on every platform; both call `cli.main`. | Step 2 launcher behavior, tests, and completion criteria. | A package-only Python API, and launchers outside the repository root. |
| Q02 | Bootstrap the tracked baseline from the implemented checker's complete empty-baseline output, review every finding, and hand-author only accepted residual records. | Step 3 baseline finalization and acceptance coverage. | Seeding from approximate counts, and an automatic baseline-writing mode. |
| Q03 | Repair the tracked design-review transcript before Step 3 baseline finalization or gate wiring; the documentation update has completed that repair. | Step 3 prerequisite and completion criteria. | Wiring a knowingly red gate, and baselining the transcript defect. |

## Shared execution checklist for every v0.11.0 Markdown-check step

1. Count physical lines before edits for every existing Python step file.
2. Add or update the step's tests before production behavior.
3. Run `ghog single` on the exact affected test files.
4. Run the step's `rg` checks for file presence, identifiers, and gate wiring.
5. Run `ghog day` repeatedly until it reports the objective with `exit=0`.
6. Count physical lines after edits and compare each Python file with the
   plan-local 650-line checkpoint and enforced 700-line default.
7. Split a responsibility before commit if any Python file exceeds the
   deliberate plan-local 650-line checkpoint.
8. Record an advisory-estimate variance without failing the step when the file
   remains at or below 650 lines.

## Ready-to-run commands for v0.11.0 Markdown-check steps

- Physical line count: `(Get-Content -LiteralPath '<path>').Count`
- Focused tests: `ghog single <step-test-files>`
- File and contract checks: `rg -n '<step-pattern>' <step-paths>`
- Shared gate loop: `ghog day`, repeated until `exit=0`

## Numbered implementation steps for v0.11.0 Markdown checking

### Step 1. Build the shared source model and rule engine

#### Step 1 analysis and intent for Markdown parsing

Issues to address:

- Review heading transformation understands fenced code, but its scanner is
  private and the checker must not create an incompatible parser.
- Heading, list, raw-HTML, frontmatter, and adapter rules need one immutable
  per-file representation.

Fix intent:

- Extract or reuse fence boundary logic through
  `tools/markdown_check/source.py` while keeping review output unchanged.
- Add typed records and pure evaluators for MD001, MD024, MD025, MD032, MD033,
  MD038, LS001, LS002, and LS003.
- Record Markdown links in the source model and classify frontmatter, bounded
  pointer, fragment, and structured documents in a pure classifier.
- Record inline-code delimiters and parsed values so MD038 can distinguish
  accidental inner padding from genuine code whitespace, space-only spans, and
  matching delimiter padding around literal backticks.

Expected outcome:

- Each Markdown fixture is decoded and parsed once.
- Pure evaluators return finding records without printing or reading files.

Step framing:

- Design links: fence-aware source representation, adapter classification, and
  complete heading hierarchy and uniqueness evaluation.
- Execution checklist: use the shared execution checklist in this plan.

#### Step 1 implementation for Markdown parsing

**Files involved**:

- `tools/markdown_check/__init__.py` (new, to be created).
- `tools/markdown_check/models.py` (new, to be created).
- `tools/markdown_check/source.py` (new, to be created).
- `tools/markdown_check/classifier.py` (new, to be created).
- `tools/markdown_check/rules.py` (new, to be created).
- `tools/review_markdown_headings.py` (existing, to be updated).
- `tests/unit/tools/test_review_markdown_headings_tdd.py` (existing, to be
  updated).
- `tests/unit/tools/markdown_check/__init__.py` (new, to be created).
- `tests/unit/tools/markdown_check/test_source_model/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py`
  (new, to be created).
- `tests/unit/tools/markdown_check/test_rules/__init__.py` (new, to be created).
- `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_rule_properties/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py`
  (new, to be created).

**Tests first**:

- Cover frontmatter, both fence styles, multiline code spans, ATX headings,
  Markdown links, list boundaries, raw HTML, UTF-8 headings, and line locations.
- Cover every catalog rule, adapter exemption, exact and normalized duplicate
  overlap, all six heading levels, and immediate-parent failures.
- Cover MD038 failures when delimiter-adjacent spaces neither survive in the
  parsed code value nor delimit literal backticks, and passing cases for genuine
  boundary whitespace, space-only spans, and required matching padding around
  literal backticks.
- Generate heading streams and normalized title variants with Hypothesis.

**Classes and behavior**:

- `MarkdownSource`: immutable parsed tokens and body metadata for one path.
- `classify_document`: pure classification from source tokens; a bounded pointer
  link is syntactically repository-relative and ends in `.md`.
- `Finding`: path, positive line, rule, and reason.
- Rule functions: pure source-model evaluation with no filesystem access.
- `qualify_round_headings`: preserve existing output after fence extraction.

**Completion criteria**:

- `ghog single tests/unit/tools/test_review_markdown_headings_tdd.py tests/unit/tools/markdown_check/test_source_model/test_source_model_tdd.py tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py tests/unit/tools/markdown_check/test_rule_properties/test_rule_properties_pbt.py`
  passes.
- `rg -n "MD001|MD024|MD025|MD032|MD033|MD038|LS001|LS002|LS003" tools/markdown_check tests/unit/tools/markdown_check`
  finds each evaluator and its tests.
- `ghog day` reports `exit=0`.

#### Step 1 addendums for Markdown parsing

Line-budget checkpoint:

- `tools/review_markdown_headings.py`: before 87, below-550 safe; plan-local ceiling 650;
  expected final at or below 110 (advisory).
- `tools/markdown_check/models.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 140 (advisory).
- `tools/markdown_check/source.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 320 (advisory).
- `tools/markdown_check/classifier.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 220 (advisory).
- `tools/markdown_check/rules.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 380 (advisory).
- Every new or updated Python test file starts below 550 and must remain at or
  below the plan-local 650 checkpoint; split fixtures or rule families if one
  exceeds it.

Full workflow timing readiness: the source, rule, property, and existing review
heading suites are the focused set before `ghog day`.

Time-gated status: no timeout gate is introduced or removed in Step 1.

### Step 2. Add policy loading, baseline comparison, and the direct launcher

#### Step 2 analysis and intent for checker execution

Issues to address:

- The repository needs an explicit supported-catalog interpretation of
  `.markdownlint.json` and fail-fast mandatory-rule validation.
- Inventory, baseline, diagnostics, and exit status need one runner callable
  directly without environment setup.

Fix intent:

- Add Git inventory, policy, versioned JSON baseline, deterministic grouping,
  diagnostics, and CLI composition around the Step 1 engine.
- Refine bounded-pointer classification against the tracked inventory so a
  syntactically valid link whose target is absent is not treated as resolvable.
- Add repository-root `markdown-check.bat` as the Windows direct launcher.

Expected outcome:

- A direct run checks every tracked Markdown path once without Node or network.
- Repository-root `markdown-check.bat` and
  `python -m tools.markdown_check.cli` are the stable public commands, and both
  enter the same `cli.main` boundary.
- Growth fails, unchanged debt passes, and shrink writes an advisory without
  mutating `.markdownlint-baseline.json`.

Step framing:

- Design links: policy model, baseline model, diagnostic contract, and direct
  launcher.
- Execution checklist: use the shared execution checklist in this plan.

#### Step 2 implementation for checker execution

**Files involved**:

- `tools/markdown_check/policy.py` (new, to be created).
- `tools/markdown_check/baseline.py` (new, to be created).
- `tools/markdown_check/runner.py` (new, to be created).
- `tools/markdown_check/cli.py` (new, to be created).
- `markdown-check.bat` (new, to be created).
- `.markdownlint-baseline.json` (new, to be created).
- `tests/unit/tools/markdown_check/test_policy/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_baseline/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_baseline/test_baseline_tdd.py` (new, to
  be created).
- `tests/unit/tools/markdown_check/test_runner/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_launcher/__init__.py` (new, to be
  created).
- `tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py` (new, to
  be created).

**Tests first**:

- Reject unknown keys, invalid option shapes, and attempted `MD024` or `MD025`
  disables before inventory evaluation.
- Cover inventory failure, path normalization, decoding failure, deterministic
  ordering, stdout findings, stderr health messages, and process status.
- Cover inventory-backed link existence refinement, including missing targets
  and normalized repository-relative paths.
- Cover baseline versions, duplicates, unsupported rules, positive counts, new
  debt, unchanged debt, and debt-reduced advisories.
- Exercise the root launcher from a clean subprocess environment.

**Classes and behavior**:

- `MarkdownPolicy`: validated effective catalog and per-rule options.
- `Baseline`: immutable allowance map loaded from explicit JSON records.
- `CheckerRunner`: inventory, source reads, grouping, sorting, and final status.
- `cli.main`: platform-neutral argument and stream boundary; `cli.py` carries a
  `__main__` guard so `python -m tools.markdown_check.cli` is executable.

**Completion criteria**:

- `ghog single tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py tests/unit/tools/markdown_check/test_baseline/test_baseline_tdd.py tests/unit/tools/markdown_check/test_runner/test_runner_tdd.py tests/unit/tools/markdown_check/test_launcher/test_launcher_tdd.py`
  passes.
- `rg -n "markdownlint-baseline|path:line|debt-reduced|git ls-files" tools/markdown_check markdown-check.bat tests/unit/tools/markdown_check`
  finds the settled contracts.
- `ghog day` reports `exit=0`.

#### Step 2 addendums for checker execution

Line-budget checkpoint:

- `tools/markdown_check/policy.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 240 (advisory).
- `tools/markdown_check/baseline.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 230 (advisory).
- `tools/markdown_check/runner.py`: before 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 340 (advisory).
- `tools/markdown_check/cli.py`: before 0, below-550 safe; plan-local ceiling 650; expected
  final at or below 120 (advisory).
- Every new Python test file starts below 550 and must remain at or below the
  plan-local 650 checkpoint; split reusable fixtures if a runner test leaf
  reaches the risk band.

Full workflow timing readiness: the policy, baseline, runner, and launcher suites
are the focused set before `ghog day`.

Time-gated status: no timeout gate is introduced or removed in Step 2.

### Step 3. Connect the shared gate and publish the checked contract

#### Step 3 analysis and intent for repository rollout

Issues to address:

- The direct checker is not part of `check.bat`, and zero-debt rules must be
  clean before the gate becomes authoritative.
- Maintainers need acceptance coverage and a focused reference page for rules,
  streams, baseline maintenance, and launchers.

Fix intent:

- Repair the remaining implementation-owned `MD032` source, verify the recorded
  transcript repair, clear genuine `MD038` defects while preserving its
  code-space exceptions, add zero-debt `MD050` strong-style enforcement and
  repair unquoted underscore-bearing filenames, establish the authoritative
  residual baseline, and then add the gate call.
- Produce that baseline by running the implemented checker against an empty
  baseline, reviewing its complete findings, and hand-authoring only accepted
  residual records; approximate discovery counts are not baseline input.
- Add repository-fixture acceptance tests and Diataxis reference navigation.

Expected outcome:

- `check.bat` records `markdown` failure status through its aggregator.
- A clean direct run, a failing fixture run, and `ghog day` agree on the result.

Step framing:

- Design links: Windows gate connection, acceptance cases, documentation
  contract, and verified transcript repair.
- Execution checklist: use the shared execution checklist in this plan.

#### Step 3 implementation for repository rollout

**Files involved**:

- `tools/markdown_check/models.py` (existing, to be updated).
- `tools/markdown_check/source.py` (existing, to be updated).
- `tools/markdown_check/policy.py` (existing, to be updated).
- `tools/markdown_check/rules.py` (existing, to be updated).
- `tools/markdown_check/runner.py` (existing, to be updated).
- `tests/unit/tools/markdown_check/test_policy/test_policy_tdd.py` (existing,
  to be updated).
- `tests/unit/tools/markdown_check/test_rules/test_rules_tdd.py` (existing, to
  be updated).
- `.claude/skills/humanizer/SKILL.md` (existing, to be updated).
- `docs/v0.11.0/review.code.v0.11.0.markdown-check.md` (existing, to be
  updated).
- `docs/v0.11.0/review.design-specification.v0.11.0.markdown-check.md`
  (existing, repaired during documentation consolidation; Step 3 verifies).
- `.markdownlint-baseline.json` (new from Step 2, to be updated with
  authoritative residual counts).
- `check.bat` (existing, to be updated).
- `wiki/reference/markdown-checker.md` (new, to be created).
- `wiki/README.md` (existing, to be updated).
- `README.md` (existing, to be updated).
- `tests/acceptance/__init__.py` (new, to be created).
- `tests/acceptance/markdown_check/__init__.py` (new, to be created).
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/__init__.py`
  (new, to be created).
- `tests/acceptance/markdown_check/test_markdown_check_acceptance/test_markdown_check_acceptance_tdd.py`
  (new, to be created).
- `tests/acceptance/markdown_check/test_shared_gate/__init__.py` (new, to be
  created).
- `tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py`
  (new, to be created).

**Tests first**:

- Build temporary Git repositories covering structured documents, every adapter
  class, rule overlap, configuration errors, baseline growth and shrink, and
  deterministic output.
- Verify the root launcher and `check.bat` return nonzero for an unbaselined
  finding and zero for the checked repository state.
- Verify every enabled zero-debt `MD*` rule has no baseline entry. Preserve only
  authoritative residual `MD033` entries allowed by the consolidated scope.
- Cover MD038 failures when delimiter-adjacent spaces neither survive in the
  parsed code value nor delimit literal backticks, and passing cases for genuine
  boundary whitespace, space-only spans, and required matching padding around
  literal backticks.
- Cover MD050 failure for underscore-delimited strong style and an unquoted
  `__init__.py` filename, plus passing asterisk, inline-code, fenced-code, and
  escaped cases.

**Classes and behavior**:

- `check.bat`: run `markdown-check.bat`, capture its status, and call
  `record_failure markdown <status>` on failure.
- Reference page: catalog, mandatory rules, adapter classes, `LS003`
  normalization, MD032 authoring boundaries, MD038 genuine-code-space
  exceptions, MD050 strong-style and code-span boundaries, streams, baseline
  schema, direct launcher, and shared-gate name.
- Navigation: link the page under reference while preserving explanation,
  tutorials, how-to guides, then reference.

**Completion criteria**:

- The repaired design transcript has a blank line before its list at the former
  MD032 boundary before baseline finalization or gate wiring.
- `ghog single tests/acceptance/markdown_check/test_markdown_check_acceptance/test_markdown_check_acceptance_tdd.py tests/acceptance/markdown_check/test_shared_gate/test_shared_gate_tdd.py`
  passes.
- `rg -n "record_failure markdown|markdown-check.bat" check.bat` finds one gate
  call and one failure record.
- `rg -n "Markdown checker|MD032|MD033|MD038|MD050|LS003|markdownlint-baseline" README.md wiki/README.md wiki/reference/markdown-checker.md`
  finds navigation and the reference contract.
- `ghog day` reports `exit=0`.

#### Step 3 addendums for repository rollout

Line-budget checkpoint:

- Existing production Python modules keep their earlier step counts and remain
  at or below the plan-local 650 checkpoint; Step 3 adds no production Python
  responsibility.
- Each new acceptance test file starts at 0, below-550 safe; plan-local ceiling 650;
  expected final at or below 450 (advisory).
- `check.bat`, Markdown sources, JSON policy, and navigation files are outside
  the Python plan-local 650-line classification.

Split guidance: extract one focused repository-fixture support module if an
acceptance leaf enters the 550-through-650 risk band.

Full workflow timing readiness: the acceptance suites and all checker unit
suites are the affected set before the final `ghog day`.

Time-gated status: no timeout gate is introduced or removed in Step 3; the
groundhog duration report remains the timing evidence.
