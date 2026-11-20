# Code review transcript for v0.14.0

- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md

This append-only transcript records completed review rounds. Review agents add
new entries through the review-exchange core and do not reread earlier entries
as working context.

## Round 1 by requestor - Step 1

- Recorded: 2026-11-17T09:46:35+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 1
- Outcome: request

### Review identity for step 1 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 1
Review round: 1

### Code review evidence for step 1 git-cliff-provisioning (round 1)

request_index_tree: 281ef86db648bf57ed6df4709ec293b40deae48d
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): sample scope capture names from a pool
group 1 path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
group 2: refactor(release): share strict lock record decoding
group 2 path: tools/release_workflow/lock_records.py
group 2 path: tools/release_workflow/operation_lock.py
group 2 path: tests/unit/tools/release_workflow/test_lock_records/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py
group 3: feat(release): add git-cliff pins and budget policy
group 3 path: tools/release_workflow/git_cliff/__init__.py
group 3 path: tools/release_workflow/git_cliff/manifest.py
group 3 path: tools/release_workflow/git_cliff/budget.py
group 3 path: tools/release_workflow/schemas.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py
group 3 path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
group 4: docs(git-cliff-provisioning): record step 1 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
staged path: tests/unit/tools/release_workflow/test_lock_records/__init__.py
staged path: tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
staged path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/budget.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/lock_records.py
staged path: tools/release_workflow/operation_lock.py
staged path: tools/release_workflow/schemas.py
```

### Validation scope for step 1 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 1 git-cliff-provisioning (round 1)

Writer assessment for Step 1 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and its implementation check records
`Yes. Step 1 has been fully implemented.` in the staged validation plan,
whose document status stays `No, it is not implemented.` while Steps 2 to 8
are not started.

Evidence, all on the staged tree:

- Tests first: before the production files existed, `ghog single` on the
  seven Step 1 test files failed at collection on the missing
  `tools.release_workflow.git_cliff` and `lock_records` modules (exit 4).
  With the implementation they passed together with both operation lock
  suites (212 tests).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after three repairs: ruff `RUF043` (non-raw `match=` patterns) and
  `RUF001` (ambiguous characters written literally in two property tests,
  now built from code points) in the new tests; a lifecycle CPU overrun of
  `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py::test_fingerprint_order_independent[2]`
  (0.2656 s, band top 0.250 s), a test outside this step, shortened as the
  implementation report describes; and a pyright annotation in that rework.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7413 tests), on index tree
  `281ef86db648bf57ed6df4709ec293b40deae48d`. No budget was changed and no
  exclusion is accepted.
- `rg -n 'import' tools/release_workflow/git_cliff/manifest.py` shows only
  `__future__`, `re` and `dataclasses`;
  `rg -n 'json.loads' tools/release_workflow/operation_lock.py` finds nothing;
  `rg -n 'getenv|environ' tools/release_workflow/git_cliff` finds only the
  `environment` parameter of `budget.py`. The import-freedom test passes.
- Line counts: `manifest.py` 164 (advisory 110), `budget.py` 89,
  `lock_records.py` 71, `schemas.py` 245, `operation_lock.py` 244; the
  largest test file is `test_configuration_tdd.py` at 327. Every Python file
  stays below 550.
- Markdown check and cSpell on the staged validation plan: clean.

Architecture: the manifest and the budget policy are pure functions and data,
with standard-library imports only; the budget policy receives the
environment mapping from its caller. `schemas.py` imports only the manifest at
load time, as the plan requires for the rule's default, and the
import-freedom test proves configuration loading pulls no other `git_cliff`
module. `lock_records.py` depends on nothing in the engine. Performance: a pin
table is validated and indexed once, then each lookup is one dictionary
access; decoding is linear in the record bytes; the budget is one pass over
the caller's mapping, once per caller. Feature integrity: the operation lock
keeps its messages and its suites pass unchanged; `[git-cliff]` becomes a
known section whose declared `version` is refused with `tested: none` until
Step 7.

Please check in particular: the strict decoder's messages and exception types
against the former private helpers; the manifest's invariant list and the
per-table memo against the plan's complexity bound; the refused budget forms,
the leading-zero handling and the case-insensitive lookup; the configuration
messages; the import-freedom test's restoration of `sys.modules` and package
attributes; and the scope capture rework, which must keep every case it
checked.

### Implementation report for step 1 git-cliff-provisioning (round 1)

Step 1, "Tested-pin manifest, git-cliff domain and download budget policy",
is the first of eight steps of the git-cliff-provisioning plan. It adds no
process, network or filesystem code: only pure tables, converters and the
strict record rules that later steps build on.

Shared record decoder, `tools/release_workflow/lock_records.py` (plan
decision Q02):

- `decode_object(content, *, label)`: `json.loads` with a pairs hook that
  refuses a repeated key at every object level
  (`Duplicate <label> field: <key>`), then refuses any value that is not an
  object (`<Label> record is not an object`, `TypeError`). The returned dict
  keeps the keys of the document in order, so each record kind compares them
  with the exact key set it expects.
- `positive_integer(record, key, *, label)`: `type(value) is int` and above
  zero, so booleans, numeric strings, floats and absence are refused
  (`Invalid <label> <key>`, `ValueError`).
- `text(record, key, *, label)`: a present `str`, empty allowed
  (`Invalid <label> <key>`, `TypeError`).
- `tools/release_workflow/operation_lock.py`: `_record`, `_integer` and
  `_text` keep their names and docstrings and delegate with `label="owner"`;
  the private pairs hook and the `cast` import are gone, `json` stays for
  `json.dumps`. Its messages and exception types are unchanged.

Manifest, `tools/release_workflow/git_cliff/manifest.py`:

- `AdmittedPin` (frozen): `version`, `default`, `triple`, `asset`, `size`,
  `sha256`, `member`, `evidence`. `PLATFORM_TRIPLE` is
  `x86_64-pc-windows-msvc`.
- `validate_pins(pins)`: for each pin, the first invalid field among an
  `X.Y.Z` version, the platform triple, the asset
  `git-cliff-<version>-<triple>.zip`, the member
  `git-cliff-<version>/git-cliff.exe`, a 64-character lowercase hexadecimal
  digest, a size above zero and a nonempty evidence reference
  (`Admitted git-cliff pin '<version>': invalid <field>`); then duplicate
  versions; then exactly one default in a nonempty table. It raises
  `ManifestError` (`ValueError`, `exit_code = 2`) and returns the table, so
  `ADMITTED_PINS: tuple[AdmittedPin, ...] = validate_pins(())` is validated
  where it is defined.
- `_table(pins)`: a private memo keyed by the immutable table validates and
  indexes it on first use (`by_version`, the default version, the listing
  `2.14.2, 2.15.1` or `none`), so `default_version`, `admitted` and
  `parse_pin` make one dictionary access per call afterwards, as the plan's
  complexity section states, without importing more than `re` and
  `dataclasses`.
- `parse_pin(raw, *, pins)`: `re.fullmatch` on
  `(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)`, else
  `PinError("expected an exact git-cliff version X.Y.Z, without a v prefix, prerelease or latest")`;
  then `admitted`, which raises
  `PinError("not a tested git-cliff pin; tested: <listing>")`.
  `PinError` is a `ValueError`, so the reader wraps it with its location.
- `download_url(pin)`:
  `https://github.com/orhun/git-cliff/releases/download/v<version>/<asset>`.

Budget, `tools/release_workflow/git_cliff/budget.py`:

- `BudgetPolicy` (frozen, keyword-only): `download`, `wait`, `socket = 30`,
  `probe = 15`, `metadata = 60`, `retry_delay = 5`, `source` (`default` or
  `LLM_SHARED_GIT_CLIFF_DOWNLOAD_TIMEOUT_SECONDS=<text>`).
- `resolve_budget(environment)`: one pass over the mapping matches the
  variable name whatever its case; unset gives D 300 and W 360; a value
  passing `isascii()` and `isdigit()` is stripped of leading zeros, and at most
  four remaining digits are converted, so `0900` is 900 and a long zero-padded
  text costs no large conversion; anything outside 300 through 3600 raises
  `BudgetSettingError` (`exit_code = 2`) naming the canonical variable and the
  range. The module reads no process environment: the provisioning entry of
  Step 5 hands it the mapping.

Domain, `tools/release_workflow/schemas.py`: `git_cliff_domain(pins)` returns
`DomainSchema("git-cliff", (SectionSchema("git-cliff", (rule,)),))` with
`ValueRule("version", parse=partial(manifest.parse_pin, pins=pins),
default=manifest.default_version(pins))`; `GIT_CLIFF_SCHEMA` comes last in
`SHIPPED_SCHEMAS`. The module imports the manifest at load time, which the
plan's "Default and converter" fact requires.

Package docstrings: `tools/release_workflow/git_cliff/__init__.py` lists the
two modules and imports nothing; `tools/release_workflow/__init__.py` names
`lock_records` and the `git_cliff` package.

Tests:

- `test_lock_records/test_lock_records_tdd.py`: labels in duplicate refusals,
  nested duplicates, five non-object documents, malformed bytes, key order,
  integer and text acceptance and refusals.
- `test_git_cliff_manifest/`: TDD for admission, the default, ten refused
  forms, the tested listing, the shipped empty tuple, thirteen invariant
  cases, the single validation per table and the URL; PBT for integer triples
  against a synthetic table and inserted foreign characters.
- `test_git_cliff_budget/`: TDD for the defaults, four accepted values,
  twelve refused values (non-ASCII digits built from code points), the
  case-insensitive name and similar names; PBT for every in-range integer,
  out-of-range integers and inserted non-digit characters.
- `test_schemas_tdd.py`: the three-domain tuple, the fixed section with no
  default and no extension claim, and the synthetic default.
- `test_configuration_tdd.py`: the known section with unknown keys, the empty
  table's missing value and `tested: none`, the synthetic default with its
  source information and the exact `2.15.0` message, and the import freedom:
  configuration and schemas are imported again in a fresh `sys.modules`
  snapshot, configuration is loaded, and only the `git_cliff` package and its
  `manifest` are loaded; the test restores the package attributes the fresh
  import rebinds.

Out-of-step change, `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`:
the second whole-suite walk failed on a lifecycle CPU overrun of
`test_fingerprint_order_independent[2]` (0.2656 s, band top 0.250 s). The
property now samples names from the precomputed pool of its former domain
instead of generated unique text, and the three explicit limits run once in
`test_fingerprint_order_independent_at_the_limits`; a side-by-side
measurement over 200 calls gave 5.4 ms instead of 8.8 ms of CPU per batch
call. It is its own `perf(tests)` commit group.

Validation plan: Step 1 sections written; the document stays
`No, it is not implemented.` with Steps 2 to 8 not started, and its opening
paragraph now says Step 1 is implemented.

Writer notes: `.reviews/a.git-cliff-provisioning.step1.journal.md` and
`.reviews/a.git-cliff-provisioning.step1.handoff.md`.

### Change summary for step 1 git-cliff-provisioning (round 1)

Staged paths (19), grouped in the root `a.commit` (four groups, checker
`ready: true`):

1. `perf(tests): sample scope capture names from a pool`:
   `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`.
2. `refactor(release): share strict lock record decoding`:
   `tools/release_workflow/lock_records.py`,
   `tools/release_workflow/operation_lock.py`,
   `tests/unit/tools/release_workflow/test_lock_records/__init__.py`,
   `tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py`.
3. `feat(release): add git-cliff pins and budget policy`:
   `tools/release_workflow/git_cliff/__init__.py`,
   `tools/release_workflow/git_cliff/manifest.py`,
   `tools/release_workflow/git_cliff/budget.py`,
   `tools/release_workflow/schemas.py`,
   `tools/release_workflow/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py`,
   `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`,
   `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`.
4. `docs(git-cliff-provisioning): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

The requirement, design and plan of this item are committed and pushed
(`0ae0ee2d` is the base of this review); no earlier step of this plan exists.

### Writer response for step 1 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 1 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and, where they
outlive the step, in the validation plan:

- "Exact key sets" in the plan's decoder tests is read as the decoder
  returning exactly the keys of the document, which each record kind then
  compares with its expected set; the operation lock keeps its own combined
  check and its `Unverifiable owner record` message. No fourth helper was
  added beyond the three the plan names.
- Pin lookups go through a private per-table memo in the manifest, validated
  and indexed once, to meet the plan's "one dictionary access" bound while
  keeping the manifest's imports to `re` and `dataclasses`. A synthetic table
  is validated on its first lookup, which `git_cliff_domain` makes when it
  reads the default, so an invalid table fails at domain construction rather
  than as a configuration error.
- The invariant check also requires `triple == PLATFORM_TRIPLE`: with one
  entry per version (the duplicate rule), a pin for another platform could
  not coexist with the Windows one, and other platforms are out of scope.
- `PinError` and `ManifestError` subclass `ValueError`, so the reader's
  existing `except (ValueError, OSError, RuntimeError)` adds the location.
- The budget message always names the canonical upper-case variable, even
  when the mapping held another case; `source` records the text as given.
- Synthetic pin builders are small local helpers in each test file:
  `git_cliff_support.py` is a Step 3 file in the plan, and the Step 1 tests
  need no archive.
- The scope capture property rework is outside the step; it changes how that
  test generates and replays its cases, never what it asserts, and is its own
  commit group.

### Reviewer focus for step 1 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-1 -->

### LLM nature completion for reviewer (exchange 1)

Recorded nature: `codex`

Completed artifacts:

- `.reviews/a.review-active.code.code.v0.14.0.git-cliff-provisioning.md`
- `.reviews/a.review-requested.code.v0.14.0.git-cliff-provisioning.md`

<!-- review-entry-id: llm-nature-completion-reviewer-exchange-1 -->

## Round 1 by reviewer - Step 1

- Recorded: 2026-11-17T09:55:33+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: 281ef86db648bf57ed6df4709ec293b40deae48d

Assessed index tree: 1a3464d6c7ba27e3c372e718902de1e68c56d559

### Implementation check for step 1 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 1 has NOT been fully implemented.

The functional manifest, domain, budget and record-decoder work is present. Warm manifest lookups violate the explicit O(1) amortized bound because every tuple-key lookup hashes all pins. Existing tests miss this behavior.

Validation plan effects:

Updated only Step 1 analysis, implementation detail, missing-work, performance and static test assessment in docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md. The exact No sentence and a concrete Missing work for Step 1 section are present. Document-level status, other steps and umbrella remain unchanged. The pre-existing overview says Step 1 is implemented; the writer should reconcile that overview when updating completion status.

### Pre-repair mandatory checks and coverage for step 1 git-cliff-provisioning (exchange 1) (round 1)

Requestor evidence: ghog day --full=speed --whole-suite exited 0 with 7413 tests, 100% coverage and no duration outliers or exclusions. Reviewer ran the independent commit-plan checker (exit 0), inspected code/tests and performed evidence-boundary operations. No reviewer ghog check, affected run or coverage measurement was needed or performed. Static coverage review found no uncovered executable branch; a complexity regression is missing.

### Resolved validation set and sources for step 1 git-cliff-provisioning (exchange 1) (round 1)

{"commands":[{"command":"ghog day --full=speed --whole-suite","sources":["project"]}]}

### Resolver drift and direction for step 1 git-cliff-provisioning (exchange 1) (round 1)

No drift. The current .review-validation path is absent. load_project_validation therefore uses ghog day --full=speed, and complete_project_default appends the declared whole-suite selector. No plan/request additions appear in the request. The command and project source match the embedded resolved set. Commands were compared statically, not executed.

### Repository state around validation for step 1 git-cliff-provisioning (exchange 1) (round 1)

The retained baseline matched the live request-time index: 281ef86db648bf57ed6df4709ec293b40deae48d. The 19-path validation-state comparison reports acceptable=false solely because the reviewer intentionally updated the Step 1 validation document; no tests were executed and no validation-generated tracked/untracked side effect occurred. attribute-reviewer-patch proved that exact metadata patch attributable before staging. The assessed index is 1a3464d6c7ba27e3c372e718902de1e68c56d559. Umbrella digest comparison is unchanged (20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c).

### Repair inventory for step 1 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- Review metadata only: corrected and staged the exact Step 1 validation sections; no implementation or test repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md

### Commit plan assessment for step 1 git-cliff-provisioning (exchange 1) (round 1)

Independent commit-plan-check.bat --format json returned state=valid, ready=true, exit 0, 19 staged paths and no diagnostics. Four ordered groups are appropriate: perf(tests): sample scope capture names from a pool; refactor(release): share strict lock record decoding; feat(release): add git-cliff pins and budget policy; docs(git-cliff-provisioning): record step 1 validation. The first isolates the requestor's measured test-duration fix; shared decoding precedes the new feature and documentation follows it. Reviewer metadata stays in the existing fourth group. No membership or subject change is needed; a.commit was not edited.

### Findings and boundaries for step 1 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- [P2] Avoid hashing every pin on warm cache access (`tools/release_workflow/git_cliff/manifest.py:118`). `_TABLES.get(pins)` hashes the tuple on every call, including hits using the same tuple object; tuple hashing invokes `AdmittedPin.__hash__` once per pin. Thus `parse_pin`, `admitted` and `default_version` remain O(n) in manifest size after warm-up, contrary to the plan's O(1) amortized bound and the module/validation claims. `test_a_table_is_validated_and_indexed_once` counts only `validate_pins` calls and cannot detect the repeated work. Use a cache lookup that does not traverse or hash all pins (retaining tuple ownership if keyed by identity), and add an operation-count regression for the three warm entry points.

Boundary-crossing work: None.

### Writer instructions for step 1 git-cliff-provisioning (exchange 1) (round 1)

Fix the warm manifest cache access without weakening validation, add the operation-count regression across parse_pin/admitted/default_version, and correct the module cost claims. Follow Missing work for Step 1 in the validation plan, reconcile its overview, run the required writer validation and refresh evidence, then publish a replacement review request. No literal Human guidance block authorized reviewer implementation repairs.

### Decision rationale for step 1 git-cliff-provisioning (exchange 1) (round 1)

changes-requested. Readiness floor: identity passes; completeness fails on warm-lookup complexity; validation/coverage has reported green writer evidence and no static branch gap but lacks the required complexity regression; staged attribution passes for the metadata-only patch; unresolved findings fails on the cache defect; a.commit passes mechanical and semantic assessment. No substantive reviewer repair was made.

### Final reviewer decision for step 1 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-1-round-1 -->

## Round 2 by requestor - Step 1

- Recorded: 2026-11-17T10:30:45+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: request

### Review identity for step 1 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 1
Review round: 2

### Code review evidence for step 1 git-cliff-provisioning (round 2)

request_index_tree: 2d96299b343141add7866032ec6c6d1ecbaea573
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): sample scope capture names from a pool
group 1 path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
group 2: perf(tests): check malformed audit marks directly
group 2 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
group 3: refactor(release): share strict lock record decoding
group 3 path: tools/release_workflow/lock_records.py
group 3 path: tools/release_workflow/operation_lock.py
group 3 path: tests/unit/tools/release_workflow/test_lock_records/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py
group 4: feat(release): add git-cliff pins and budget policy
group 4 path: tools/release_workflow/git_cliff/__init__.py
group 4 path: tools/release_workflow/git_cliff/manifest.py
group 4 path: tools/release_workflow/git_cliff/budget.py
group 4 path: tools/release_workflow/schemas.py
group 4 path: tools/release_workflow/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py
group 4 path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
group 5: docs(git-cliff-provisioning): record step 1 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
staged path: tests/unit/tools/release_workflow/test_lock_records/__init__.py
staged path: tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
staged path: tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/budget.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/lock_records.py
staged path: tools/release_workflow/operation_lock.py
staged path: tools/release_workflow/schemas.py
```

### Validation scope for step 1 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 1 git-cliff-provisioning (round 2)

Writer assessment for Step 1 of the git-cliff-provisioning plan, round 2: the
round 1 finding is repaired, the implementation check again records
`Yes. Step 1 has been fully implemented.` in the staged validation plan
(document status still `No, it is not implemented.` while Steps 2 to 8 are
not started), and the step is ready for another review.

Evidence, all on the staged tree:

- Round 1 repair, red then green: the new
  `test_warm_lookups_never_hash_compare_or_visit_the_pins` failed against the
  reviewed manifest with twelve recorded tuple hashes (`ghog single`,
  exit 2); with the identity-keyed cache it passes together with the manifest
  property tests and the schema and configuration tests (exit 0).
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7414 tests) at
  2026-11-17T10:25:59+01:00. It took three walks: the first stopped at ruff
  `SLOT001` on the regression helper (now `__slots__ = ()`); the second failed
  on the lifecycle CPU ceiling for a malformed test-permission case of the
  process audit plugin, a test outside this step, reworked in its own
  `perf(tests)` group as the implementation report describes. A final call on
  the index tree `2d96299b343141add7866032ec6c6d1ecbaea573` reported the
  objective met by saved proof on unchanged sources, and `ghog check` on that
  tree passed every `check.bat` step, Markdown included, because the
  validation plan was edited during the third walk. No budget was changed and
  no exclusion is accepted.
- The step's `rg` checks are unchanged since round 1: the manifest imports
  only `__future__`, `re` and `dataclasses`; `operation_lock.py` has no
  `json.loads`; only `budget.py` names an `environment`.
- Line counts: `manifest.py` 172, `test_git_cliff_manifest_tdd.py` 188,
  `test_audit_declarations_tdd.py` 379; every Python file stays below 550.
- `commit-plan-check.bat --format json`: `ready: true`, five groups, no
  diagnostics. markdownlint and cSpell on the staged validation plan: clean.

Performance after the repair: a warm `parse_pin`, `admitted` or
`default_version` call is one dictionary access on `id(pins)`, one identity
check and one access by version, with no pin hashed, compared or visited, as
the regression asserts for hits and misses; validation stays linear once per
table.

Please check in particular: the identity-keyed cache and its retention of the
table; whether the regression's recorded operations cover every way a lookup
could touch the pins; and the audit declaration rework, which must keep every
assertion of the seven former embedded cases.

### Implementation report for step 1 git-cliff-provisioning (round 2)

Step 1, "Tested-pin manifest, git-cliff domain and download budget policy",
is unchanged since round 1 except for the repair of the round 1 finding; the
round 1 implementation report describes the rest (record decoder, manifest,
budget policy, domain, package docstrings, tests and the out-of-step scope
capture rework).

Repair in `tools/release_workflow/git_cliff/manifest.py`:

- `_TABLES` is now `dict[int, tuple[tuple[AdmittedPin, ...], _Table]]`,
  keyed by `id(pins)`. `_table(pins)` returns `entry[1]` when an entry exists
  and `entry[0] is pins`; otherwise it validates the table, builds the index,
  the default and the listing, and stores `(pins, table)`. Keeping the table
  in its entry keeps it alive, so its identity cannot name another object
  while cached.
- The module docstring explains the identity key, the retained table, why a
  warm lookup never hashes, compares or visits a pin, and that the cached
  tables are long-lived values (the shipped tuple and the table each
  git-cliff domain captures).

Repair in `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`:

- `_CountingPins`, a `tuple[AdmittedPin, ...]` subclass with
  `__slots__ = ()` (ruff `SLOT001`) that records `iter`, `hash`, `eq`, `len`
  and `contains` operations in one class-level list, which its one test
  clears before the first use and again before the warm calls.
- `test_warm_lookups_never_hash_compare_or_visit_the_pins`: with an empty
  cache, the first `default_version` call validates and indexes (it records a
  traversal); the record is cleared; three rounds of `parse_pin` hit and miss,
  `admitted` and `default_version` then record nothing.
- The module docstring names the regression and the round 1 finding.

Second out-of-step test change,
`tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`
(its own `perf(tests)` group): the first round 2 speed walk failed on the
lifecycle CPU ceiling for
`test_malformed_test_permission_prevents_setup[pytest.mark.process_allowed]`
(0.109 s against 0.100 s, not proven here: the drift guard had dropped the
proof of a case that measured 0.125 s in round 1). Each of its seven cases ran
an embedded pytest session of about 25 ms alone, mostly plugin manager and
configuration setup, and the plugin raises on the first malformed item, so
the sessions cannot be merged. Now:

- `test_malformed_test_permission_prevents_setup` keeps one embedded session
  with the bare decorator: exit `USAGE_ERROR`, the error names
  `process_allowed` and `test_case`, and the autouse fixture never runs.
- `test_malformed_test_permission_forms_are_refused` runs
  `AuditSession._test_marks` on a stand-in item for each distinct malformed
  form (no arguments, a positional reason, an empty, blank or non-string
  reason, an extra keyword) and checks that the usage error names the mark and
  the test. The bare and `()` spellings build the same mark, so the direct
  list holds it once. The marks are `SimpleNamespace` values with `name`,
  `args` and `kwargs`, because the host suite runs `--strict-markers` and does
  not register `process_allowed`.

Validation plan: the Step 1 sections record the repair, its red and green
runs, the identity-keyed cache in the implementation, architecture,
performance and coverage sections, and the new line counts (`manifest.py`
172, `test_git_cliff_manifest_tdd.py` 188, `test_audit_declarations_tdd.py`
379), the second out-of-step change, and the round 2 lint fix of the
regression helper (`__slots__ = ()` with a class-level record); the
missing-work list is removed and the status is
`Yes. Step 1 has been fully implemented.` again.

Writer notes: `.reviews/a.git-cliff-provisioning.step1.journal.md` and
`.reviews/a.git-cliff-provisioning.step1.handoff.md`.

### Change summary for step 1 git-cliff-provisioning (round 2)

Staged paths (20), grouped in the root `a.commit` (five groups, checker
`ready: true`):

1. `perf(tests): sample scope capture names from a pool`:
   `tests/unit/tools/test_scope_capture/test_scope_capture_pbt.py`.
2. `perf(tests): check malformed audit marks directly` (new in round 2):
   `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`.
3. `refactor(release): share strict lock record decoding`:
   `tools/release_workflow/lock_records.py`,
   `tools/release_workflow/operation_lock.py`,
   `tests/unit/tools/release_workflow/test_lock_records/__init__.py`,
   `tests/unit/tools/release_workflow/test_lock_records/test_lock_records_tdd.py`.
4. `feat(release): add git-cliff pins and budget policy`:
   `tools/release_workflow/git_cliff/__init__.py`,
   `tools/release_workflow/git_cliff/manifest.py`,
   `tools/release_workflow/git_cliff/budget.py`,
   `tools/release_workflow/schemas.py`,
   `tools/release_workflow/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_pbt.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_pbt.py`,
   `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`,
   `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`.
5. `docs(git-cliff-provisioning): record step 1 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Round 2 changes the staged content of
`tools/release_workflow/git_cliff/manifest.py`,
`tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`
and the validation plan, and adds the audit declaration test with its own
group 2; the other groups keep their paths and subjects, and group 5 now names
the round 1 repair and both out-of-step reworks. The review transcript stays
unstaged for its residual commit after the review.

The requirement, design and plan of this item are committed and pushed
(`0ae0ee2d` is the base of this review); no earlier step of this plan exists.

### Writer response for step 1 git-cliff-provisioning (round 2)

Writer response:

Writer response:

Round 1 finding [P2], warm manifest lookups hashing every pin: accepted, no
disagreement.

- The tuple key of `_TABLES` hashed the whole table on every lookup, cache hit
  included, so each warm call was linear in the pins, against the plan's
  "O(1) amortized per call" bound. The cache is now keyed by `id(pins)`, and
  each entry keeps the table object, so that identity cannot be reused by
  another table while the entry exists; the lookup also checks
  `entry[0] is pins`. A warm `parse_pin`, `admitted` or `default_version` call
  is one dictionary access on an integer plus one access by version in the
  cached index.
- The regression the answer asked for is
  `test_warm_lookups_never_hash_compare_or_visit_the_pins`: a tuple subclass
  records every `__iter__`, `__hash__`, `__eq__`, `__len__` and
  `__contains__` call; after the first use, three rounds of hits and misses on
  the three entry points must record nothing. Against the reviewed manifest it
  failed with twelve recorded hashes; with the repair it passes.
- The module docstring now states the identity key, the retained table and
  why a warm lookup touches no pin; the test module docstring names the
  regression.
- The reviewer's Step 1 validation edits were taken as the starting point of
  the new implementation check, which restores the `Yes` sentence, removes the
  completed missing-work list, rewrites the performance and coverage sections
  for the repaired cache, adds the repair evidence and the new line counts,
  and reflows one paragraph. The opening paragraph already said Step 1 is
  implemented, which is true again.

Accepted reviewer edits: the staged Step 1 validation metadata, superseded as
described above. Reversed reviewer edits: none beyond that update.

New in round 2, worth checking: the required speed walk failed on a second
test outside the step, the malformed test-permission cases of the process
audit plugin, at the lifecycle CPU ceiling. They are reworked in their own
`perf(tests)` group, described in the implementation report: one embedded
session keeps the before-setup proof and the six distinct malformed forms are
checked directly against the plugin's mark validation. Please confirm that no
assertion was lost in that move.

### Reviewer focus for step 1 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-1-round-2 -->

## Round 2 by reviewer - Step 1

- Recorded: 2026-11-17T10:33:50+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: answer

### Assessed index identity for step 1 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 2d96299b343141add7866032ec6c6d1ecbaea573

Assessed index tree: 512f12836470980dd9d33ec377741246d7516e00

### Implementation check for step 1 git-cliff-provisioning (exchange 1) (round 2)

Result:

Yes. Step 1 has been fully implemented.

Round 1's warm-lookup defect is resolved: _TABLES uses id(pins), retains the exact tuple and checks identity before returning the index. Warm calls do not traverse or hash the pins; cold validation remains linear. The required manifest, schema, budget policy and shared decoder remain consistent with Step 1.

Validation plan effects:

Updated only Step 1 review metadata in docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md: corrected the out-of-step test-change count to two, recorded current requestor validation evidence, distinguished the static reviewer assessment, and documented resolution of the cache finding and assessment of the audit tests. The exact Yes sentence remains; the completed missing-work section is absent. Document-level status, other steps and umbrella were preserved.

### Pre-repair mandatory checks and coverage for step 1 git-cliff-provisioning (exchange 1) (round 2)

Requestor reports ghog day --full=speed --whole-suite exited 0 with 7414 tests, coverage 100%, no outliers or exclusions and proof=speed, followed by saved proof on the unchanged submitted sources and a passing ghog check after the documentation edit. The new regression reportedly failed on the old cache with twelve tuple hashes and passed after the repair. Reviewer independently ran commit-plan-check (exit 0) and assessed code/tests and coverage configuration statically. No reviewer ghog run or coverage measurement was needed or performed. No uncovered executable path was identified.

### Resolved validation set and sources for step 1 git-cliff-provisioning (exchange 1) (round 2)

{"commands":[{"command":"ghog day --full=speed --whole-suite","sources":["project"]}]}

### Resolver drift and direction for step 1 git-cliff-provisioning (exchange 1) (round 2)

No drift. The current .review-validation path is absent; the built-in project default is ghog day --full=speed, completed with the declared --whole-suite selector. No plan/request additions are declared in the current request. The command and project provenance match the embedded resolved set.

### Repository state around validation for step 1 git-cliff-provisioning (exchange 1) (round 2)

The request-time tree and independently captured baseline agree: 2d96299b343141add7866032ec6c6d1ecbaea573. The ordered 20-path validation-state comparison reports acceptable=false solely for the intentional Step 1 validation metadata update; no test command ran and no validation-generated tracked/untracked side effect occurred. attribute-reviewer-patch proved that exact patch attributable before staging. Assessed index: 512f12836470980dd9d33ec377741246d7516e00. Umbrella digest remains 20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c.

### Repair inventory for step 1 git-cliff-provisioning (exchange 1) (round 2)

Repairs made:

- Polishing-only review metadata: refreshed the exact Step 1 validation sections. No implementation, test or commit-group repair.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md

### Commit plan assessment for step 1 git-cliff-provisioning (exchange 1) (round 2)

Independent commit-plan-check.bat --format json returned state=valid, ready=true, exit 0, 20 staged paths and no diagnostics. The five ordered groups are accurate: perf(tests): sample scope capture names from a pool; perf(tests): check malformed audit marks directly; refactor(release): share strict lock record decoding; feat(release): add git-cliff pins and budget policy; docs(git-cliff-provisioning): record step 1 validation. The two test-duration repairs are isolated, shared decoding precedes the feature, and documentation follows. The metadata update remains within the existing fifth group; a.commit needs no amendment.

### Findings and boundaries for step 1 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 1 git-cliff-provisioning (exchange 1) (round 2)

Consume this advisory commit-ready answer and continue through the existing human convergence gate. Include the attributable Step 1 validation metadata update. The reviewer has not authorized or executed a commit.

### Decision rationale for step 1 git-cliff-provisioning (exchange 1) (round 2)

commit-ready. All six readiness results pass: exact identity and request index; complete Step 1 implementation; reported green requestor validation and static coverage assessment; attributable staged metadata; no unresolved current or carried finding; accurate mechanically valid a.commit. The previous P2 is resolved. The operation-count regression detects the original tuple-hash defect across warm entry points and a refused lookup. Static inspection confirms tuple retention prevents identity reuse. Audit variants use the same mark fields as pytest; all six distinct malformed forms raise UsageError with mark/test identifiers, and one real embedded session retains the common before-setup assertion. No substantive reviewer repair occurred.

### Final reviewer decision for step 1 git-cliff-provisioning (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-1-round-2 -->

## Round 2 by human - Step 1 - human-confirmation

- Recorded: 2026-11-17T10:43:15+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 1
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 2

- Recorded: 2026-11-18T10:16:03+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 2
- Outcome: request

### Review identity for step 2 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 2
Review round: 1

### Code review evidence for step 2 git-cliff-provisioning (round 1)

request_index_tree: dd2a3f69895e31bb743a2d6982e79247266802a6
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): code-span step 1 finding identifiers
group 1 path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
group 2: docs(git-cliff-provisioning): use process-limit job
group 2 path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
group 2 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
group 3: feat(release): contain Windows children in jobs
group 3 path: tools/release_workflow/windows_native.py
group 3 path: tools/release_workflow/windows_child.py
group 3 path: tools/release_workflow/windows_guard.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/native_kernel_fake.py
group 3 path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
group 4: test(release): record step 2 native checks
group 4 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 5: docs(git-cliff-provisioning): record step 2 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 5 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/native_kernel_fake.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/windows_child.py
staged path: tools/release_workflow/windows_guard.py
staged path: tools/release_workflow/windows_native.py
```

### Validation scope for step 2 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 2 git-cliff-provisioning (round 1)

Writer assessment for Step 2 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and its implementation check records
`Yes. Step 2 has been fully implemented.` in the staged validation plan,
whose document status stays `No, it is not implemented.` while Steps 3 to 8
are not started.

Evidence, all on the staged tree:

- Tests first: before the production modules existed, `ghog single` on the
  five Step 2 test files failed at collection on the missing
  `tools.release_workflow.windows_native` module (exit 4). With the modules
  they pass together with `test_windows_process_tdd.py` (91 tests).
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after one walk that failed at check: ty and pyright (ctypes array slices
  typed as lists, now `ctypes.string_at`; the context manager's return type;
  test helpers typed `object`), ruff (`EM101` literal call names, `ANN401`
  in the fake kernel, `PLR2004` in tests), radon grade C on two tests (now
  split into helpers), and Markdown rule MD050 on a committed line of the
  Step 1 review transcript (see the change summary).
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7494 tests), on index tree
  `dd2a3f69895e31bb743a2d6982e79247266802a6`. No budget was changed and no
  exclusion is accepted.
- Native record: the recorder `git_cliff_native_checks.py --milestone step-2`
  ran on a real kernel after the last source change and passed its eight
  checks (0.08 s to 1.32 s each); `test_git_cliff_native_evidence_tdd.py`
  accepts the committed `native_checks.v1.json` for the current sources.
- `rg -n 'subprocess\.(Popen|run|call)|AssignProcessToJobObject'` on the
  three modules: no match. `rg -n 'SetConsoleCtrlHandler'
  tools/release_workflow`: the registration and removal in
  `windows_child.py` and the declaration in `windows_native.py`.
  `rg -n 'TerminateJobObject|\.join\(' tools/release_workflow/windows_child.py`:
  the termination in `_teardown`, then the two reader joins in `_drain` and
  `_end_after_failure`, both after it.
- Line counts: `windows_native.py` 286 (advisory 180), `windows_child.py`
  477 (advisory 360), `windows_guard.py` 120, `native_kernel_fake.py` 434,
  `git_cliff_native_checks.py` 524; every Python file stays below 550.
- Markdown check and cSpell on the four staged Markdown files: clean, after
  the user added `PHANDLER` and `STARTUPINFOW` to the project dictionary.

Architecture: the three modules are the Windows adapter layer beside
`windows_process.py`, with standard-library imports, `ProcessIdentity` and
each other only; `windows_guard` depends on `windows_child` for `RETAINED`,
and `windows_child` receives guard handles as integers, so there is no cycle.
Every native call goes through the `api` kernel object (plan decision Q05).
Performance: a constant number of kernel calls per child, one inheritance
query per listed handle, reads and hashing linear in bytes, and one sort of
the environment entries that `CreateProcessW` requires. Feature integrity: no
existing module changes behavior; nothing calls the layer before Step 3.

Please check in particular: that no path can run a child outside its job or
before recording; the seven-phase order on every failure path, and that an
unconfirmed end closes and joins nothing; the inheritance window and its
restoration for handles that were already inheritable; the error checks and
the sizing exception of the attribute list; the guard's duplicate-handle hash;
the fake kernel's fidelity to the error checks; and the recorder's checks,
especially the two descendant checks and the process-limit refusal that
replaced the UI-limits check by user decision.

### Implementation report for step 2 git-cliff-provisioning (round 1)

Step 2, "Contained Windows children and the use guard", is the second of
eight steps of the git-cliff-provisioning plan. It adds the engine's Windows
child layer and its first real-kernel evidence; nothing calls the layer
before Step 3.

Declarations, `tools/release_workflow/windows_native.py` (plan decisions Q04
and Q05):

- x64 structures `STARTUPINFOW` (104 bytes), `STARTUPINFOEXW` (112),
  `PROCESS_INFORMATION` (24), `JOBOBJECT_BASIC_LIMIT_INFORMATION`,
  `IO_COUNTERS`, `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` (144) and
  `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION` (48); the creation, attribute, job,
  file, wait, console and error constants; `PHANDLER_ROUTINE`.
- `NativeCallError(OSError)`: `call` and `winerror`, message
  `[WinError N] <call> failed`.
- `Kernel`: a protocol whose `__getattr__` returns a callable, met by the
  declared `WinDLL` and by the fake kernel.
- `kernel(loader=None)`: declares 23 functions (argument types, result type,
  error check) and caches the declared library per loader. Error checks:
  zero BOOL, NULL handle, NULL or `INVALID_HANDLE_VALUE` file handle,
  `WAIT_FAILED` and a failed `ResumeThread` raise `NativeCallError`;
  `InitializeProcThreadAttributeList` accepts only the sizing call's
  insufficient-buffer answer. Pointer arguments are declared as pointers to
  their type, so callers pass ctypes instances directly.

Lifecycle, `tools/release_workflow/windows_child.py`:

- `require_supported_platform(version=None, machine=None)`: major platform
  version 10 or later and an `AMD64` or `x86_64` machine, else
  `PlatformError` (`stage = "platform"`) naming Windows 10 or Windows Server
  2016 or later on x64 and what the machine runs.
- `ChildRequest` (frozen): `executable`, `arguments`, `cwd`, `environment`,
  `stdin` (`closed` or `inherit`), `output` (`capture` or `inherit`),
  `inherited` (guard handles), `deadline`, `record`; invalid stream modes,
  an empty name, `=` after the first character of a name and NUL characters
  are refused when it is built. `command_line()` is `list2cmdline`;
  `environment_block()` sorts by upper-cased name and ends with two NULs.
- `ChildOutcome` (frozen): `status`, `stdout`, `stderr`, `timed_out`,
  `identity`.
- `run_contained(request, *, api=None, sleep=time.sleep)`, in phases:
  1. Setup: `CreateJobObjectW(None, None)`, kill-on-close through
     `SetInformationJobObject`, `NUL` (`GENERIC_READ`, shared read and write)
     or `GetStdHandle`, two `CreatePipe` pairs or the parent's output handles,
     the attribute list sized, initialized and updated with the job list
     `(job,)` and the handle list (stdin, stdout, stderr deduplicated, then
     the guards).
  2. Creation: `GetHandleInformation` per listed handle and
     `SetHandleInformation` only for those not yet inheritable;
     `CreateProcessW` with `bInheritHandles` 1 and `CREATE_SUSPENDED`,
     `EXTENDED_STARTUPINFO_PRESENT` and `CREATE_UNICODE_ENVIRONMENT`; then the
     changed handles reset, the list deleted and the parent's write ends and
     `NUL` closed.
  3. Pre-resume: `GetProcessTimes` gives the `ProcessIdentity`, the callback
     receives it, then `ResumeThread`.
  4. Wait: two daemon `_Reader` threads call `ReadFile` on the native read
     handles into private chunks (`ERROR_BROKEN_PIPE` ends a reader, another
     error is kept), and `WaitForSingleObject` waits within the deadline in
     milliseconds, rounded up, or `INFINITE`.
  5. Teardown: `TerminateJobObject(job, 1)`, `WaitForSingleObject(process,
     INFINITE)`, then `QueryInformationJobObject` until `ActiveProcesses` is 0,
     sleeping 10 ms between reads.
  6. Drain: join the readers, `GetExitCodeProcess`, close job, process,
     thread and read handles; a reader error then raises `ContainmentError`.
  7. Unconfirmed end: a failing call of phase 5 appends a `RetainedChild`
     (PID, identity or `None`, call, handles, readers) to `RETAINED` and raises
     `UnconfirmedEndError`, closing and joining nothing.
  A setup or creation failure closes what exists and raises
  `ContainmentError` (`stage = "containment"`) with the call and Windows
  error. Any failure after creation runs phases 5 and 6 first; an
  `Exception` becomes `ContainmentError`, any other exception propagates.
- `is_process_in_job(process, job=None, *, api=None)` and
  `ignore_console_interrupts(*, api=None)`, a context manager registering a
  `PHANDLER_ROUTINE` that handles `CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, kept
  referenced and removed on exit, errors included.

Use guard, `tools/release_workflow/windows_guard.py`:

- `open_guard(path, *, api=None)`: `CreateFileW(path, GENERIC_READ,
  FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)`; errors 2
  and 3 raise `FileNotFoundError`, others an `OSError` with the Windows error
  and the path.
- `UseGuard`: `path`, `handle`, `sha256_and_size()` (refused once closed;
  `DuplicateHandle`, `SetFilePointerEx` to 0, 1 MiB `ReadFile` loop, closes
  only the duplicate), idempotent `close()`, `retain()` (registers in
  `RETAINED`, after which `close()` does nothing), context manager.

Tests:

- `native_kernel_fake.py`: `FakeKernel` logs `(name, args)` per call, can fail
  the n-th call of a function with a Windows error, models handles, pipes
  with write-end holders (parent, root, descendant), files with a position
  shared by duplicates, one declared `FakeChild` and its job, and records the
  `CreateProcessW` arguments with the inheritance state of the listed handles.
  A pipe read gives up after 5 s with a fake-only error, so a wrong join
  order fails instead of hanging.
- `test_windows_native_tdd.py`: layouts, constants, all 23 declarations
  through a fake loader, every error check.
- `test_windows_child_tdd.py`: platform, request validation and environment
  block, exact call order, both lists and the inheritance window, streams and
  guards, the poll, deadlines, expiry, descendants, membership, console
  filter.
- `test_windows_child_faults_tdd.py`: each setup and creation fault, a
  missing standard handle, pre-resume faults, an interrupt, failures after
  resume, the three unconfirmed ends and the identity failure with an
  unconfirmed teardown.
- `test_windows_guard_tdd.py`: open arguments, missing files, sharing
  violation, hashing through duplicates, close and retain.

Native evidence:

- `git_cliff_native_checks.py`: started by hand
  (`python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone step-2 --output ...`), helper parents started as the same
  module with `--helper`, stand-in children from the interpreter with short
  scripts, temporary paths outside the repository, each check bounded and
  every started process ended. An `api` wrapper over the real kernel keeps the
  job and process information and observes the descendant before the outer
  termination; another fails `TerminateJobObject`.
- `native_checks.v1.json`: milestone `step-2`, commit `f11c37ff` (the base;
  the sources are uncommitted, their digests are what binds), Windows build
  and architecture, eight passed checks.
- `test_git_cliff_native_evidence_tdd.py`: its own catalog of due checks,
  expected observations, bounds and sources; the committed record must pass
  for the current sources and hold no host path, user or host name; ten
  defective records are each refused for their own reason.

Documentation: the design and plan corrections and the validation plan entry
described in the change summary; the package docstring of
`tools/release_workflow/__init__.py` names the three modules.

Writer notes: `.reviews/a.git-cliff-provisioning.step2.journal.md` and
`.reviews/a.git-cliff-provisioning.step2.handoff.md`.

### Change summary for step 2 git-cliff-provisioning (round 1)

Staged paths (21), grouped in the root `a.commit` (five groups, checker
`ready: true`):

1. `docs(review): code-span step 1 finding identifiers`:
   `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`. Line 419,
   committed with Step 1, quoted `AdmittedPin.__hash__` and other identifiers
   as plain text, which fails Markdown rule MD050 on `HEAD`; the identifiers
   are now code spans and no word changed. This round's transcript entry is
   appended to the same file and stays unstaged for the residual commit.
2. `docs(git-cliff-provisioning): use process-limit job`:
   `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`,
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md`.
3. `feat(release): contain Windows children in jobs`:
   `tools/release_workflow/windows_native.py`,
   `tools/release_workflow/windows_child.py`,
   `tools/release_workflow/windows_guard.py`,
   `tools/release_workflow/__init__.py`,
   `tests/unit/tools/release_workflow/native_kernel_fake.py`,
   `tests/unit/tools/release_workflow/test_windows_native/__init__.py`,
   `tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py`,
   `tests/unit/tools/release_workflow/test_windows_child/__init__.py`,
   `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`,
   `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py`,
   `tests/unit/tools/release_workflow/test_windows_guard/__init__.py`,
   `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py`.
4. `test(release): record step 2 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
5. `docs(git-cliff-provisioning): record step 2 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`,
   `.vscode/settings.json` (cSpell words `PHANDLER` and `STARTUPINFOW`).

Step 1 of this plan is committed and pushed (`f11c37ff` is the base of this
review).

### Writer response for step 2 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 2 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and, where they
outlive the step, in the design, the plan or the validation plan:

- The planned native check "a refused creation under a job with UI limits"
  could not pass: on Windows 11 build 26200, a helper inside a job with UI
  restrictions (0x1, 0x20, 0x40 or 0xff) created the job-list child
  normally. Two real refusals were found, a job at its active-process limit
  (`CreateProcessW` error 1816) and a job list holding a query-only job
  handle (error 5). The user chose the first on 2026-11-18; the design and
  plan text now name it, and the versioned design review transcript keeps its
  history unchanged.
- Every declared kernel call carries an error check that raises
  `NativeCallError` (an `OSError` with the call name and Windows error); the
  fake kernel raises it where the real check would. Only the sizing call of
  the attribute list may answer with an insufficient buffer.
- `run_contained` takes an injected `sleep` for the accounting poll, beside
  `api`; the plan names "the injected sleep" without a parameter.
- Only listed handles that are not yet inheritable are made inheritable, and
  only those are reset after creation, so a parent's inheritable standard
  handles keep their state. Standard handles are listed once each, since the
  console often returns one handle for stdout and stderr.
- A failure after creation that is not a native call (the recording callback
  or a reader thread start) is reported with the step name as `call`; an
  interrupt (`KeyboardInterrupt`) propagates unwrapped after the same
  confirmed end.
- The final status is read after the confirmed end, in the drain, for both a
  normal exit and an expiry; termination after a normal exit does not change
  the root's status.
- The record's source digests are LF-normalized SHA-256, so a checkout that
  converts line endings validates the same record; the recorder's own file is
  a source of every check. The two descendant checks also observe the
  descendant alive at the decisive moment, so "ended" cannot be a
  coincidence.
- `is_process_in_job(process, job=None)` takes an optional job, so the
  recorder proves membership in the attempt's own job, not merely in the
  terminal's job.

### Reviewer focus for step 2 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-1 -->

## Round 1 by reviewer - Step 2

- Recorded: 2026-11-18T10:26:52+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: dd2a3f69895e31bb743a2d6982e79247266802a6

Assessed index tree: dd2a3f69895e31bb743a2d6982e79247266802a6

### Implementation check for step 2 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 2 has NOT been fully implemented. The staged Windows layer implements the normal lifecycle, but R1 and R2 violate failure cleanup/end-confirmation contracts and R3 violates the native recorder bounds. Reviewed the exact Step 2 plan, implementation and tests statically; the approved process-limit refusal case is appropriate.

Validation plan effects:

Updated only Step 2 in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`: No verdict, missing-work section R1-R3, performance and behavior-coverage conclusions. Markdown lint passed. Other steps and umbrella unchanged. The patch is attributable to the recorded baseline blob. It remains unstaged: the required evidence launcher computes attribution but exposes no staging operation, and its contract prohibits substituting direct Git index mutations. Requestor must reconcile this explicit metadata handoff.

### Pre-repair mandatory checks and coverage for step 2 git-cliff-provisioning (exchange 1) (round 1)

No implementation repairs and no reviewer test execution. Writer reports 7,494 tests, 100% coverage, zero outliers/exclusions, and eight passing Windows native checks; these are writer evidence, not independently rerun results. Static review demonstrates missing failure contracts despite line coverage. Reviewer Markdown lint of the edited validation plan passed.

### Resolved validation set and sources for step 2 git-cliff-provisioning (exchange 1) (round 1)

The request embeds `ghog day --full=speed --whole-suite`, provenance project, scope whole, proof speed, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The sampled `.review-validation` is absent. The current resolver source's built-in default plus scope completion agrees with that set. No additional validation commands. The reviewer did not run the writer's full walk.

### Resolver drift and direction for step 2 git-cliff-provisioning (exchange 1) (round 1)

No drift found in static comparison of the embedded resolved set with current resolver source and sampled project policy. The resolver executable was not independently invoked.

### Repository state around validation for step 2 git-cliff-provisioning (exchange 1) (round 1)

Baseline and assessed index tree both `dd2a3f69895e31bb743a2d6982e79247266802a6`. Ordered validation-state comparison returned acceptable=false solely for the intentional reviewer edit to the validation plan; no ignored or untracked deltas. Manual diff confines this change to Step 2 review metadata, not test side effects. Attribution returned attributable=true against blob `661278a0ffdd93b84030013271ec0a48d3a5448e`. Umbrella digest unchanged: `20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c`. No implementation or test modifications by reviewer.

### Repair inventory for step 2 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- No substantive repairs. The only reviewer change is Step 2 validation metadata, attributable and explicitly left unstaged because the mandatory evidence launcher has no staging command.

Paths staged:

- `.vscode/settings.json`
- `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
- `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py`
- `tests/unit/tools/release_workflow/native_kernel_fake.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_guard/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_native/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/windows_child.py`
- `tools/release_workflow/windows_guard.py`
- `tools/release_workflow/windows_native.py`

### Commit plan assessment for step 2 git-cliff-provisioning (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json` returned exit 0, state valid, ready=true, 21 staged paths and no diagnostics. Manual assessment agrees that membership, ordering and conventional subjects cover the staged work. Ordered groups:

- `docs(review): code-span step 1 finding identifiers`
- `docs(git-cliff-provisioning): use process-limit job`
- `feat(release): contain Windows children in jobs`
- `test(release): record step 2 native checks`
- `docs(git-cliff-provisioning): record step 2 validation`

The unstaged reviewer validation metadata must be reconciled before committing. The checker establishes commit-plan mechanics, not implementation readiness.

### Findings and boundaries for step 2 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- **R1 (P2): Preserve ownership until cleanup succeeds.** `tools/release_workflow/windows_child.py:362` pops `_restore` before `SetHandleInformation` succeeds; line 437 likewise pops before `CloseHandle`. With capture and an inherited guard, failing the fifth `SetHandleInformation` call fails the first restoration, permanently removing that guard from retry bookkeeping. Recovery can then report ordinary containment failure while the caller's guard remains inheritable. A close failure similarly loses ownership and stops remaining cleanup; the setup/create exception handler at lines 268-271 lets cleanup failures bypass later cleanup. Keep failed resources owned, attempt remaining cleanup, and preserve explicit diagnostics/recovery state. Add restoration/close faults, including create failure plus cleanup failure. This is a static failure trace, not an executed reproduction.
- **R2 (P2): Handle interrupts until end confirmation.** `tools/release_workflow/windows_child.py:391` catches only `NativeCallError` during teardown. With `FakeKernel.lingering = 1`, a sleep raising `KeyboardInterrupt` at line 403 escapes without zero-member confirmation, a retained child or `UnconfirmedEndError`. Normal teardown is outside the earlier `BaseException` handler; error recovery can also be interrupted again. Setup/create only catches `NativeCallError`, so a setup interrupt also bypasses resource cleanup. Complete teardown before propagating interruption, or retain ownership and emit the distinct unconfirmed-end contract so callers preserve guards/staging/locks. Cover setup, accounting polling and repeated interruption. This is a static failure trace, not an executed reproduction.
- **R3 (P2): Enforce native-check deadlines independently.** `tests/unit/tools/release_workflow/git_cliff_native_checks.py:480` calls each check synchronously; the elapsed-time check at line 487 runs only after return. Descendant, teardown-failure and other direct checks enter production reap/poll/join operations that intentionally have no bound. A stalled lifecycle therefore hangs the recorder instead of producing a timed-out record and cleaning its helper processes. Give the entire check an independent timeout and cleanup owner, terminate/reap its helper tree, and demonstrate timeout with a deliberately stalled helper. Keep production reap semantics unchanged and regenerate source-bound native evidence.

Boundary-crossing work:

- No implementation work crossed the reviewer boundary. No code/test repairs, umbrella edits, other-step edits, commit, convergence confirmation or requestor contact. Only authorized Step 2 validation metadata changed. The evidence-launcher staging limitation is reported for requestor reconciliation, not repaired as part of this review.

### Writer instructions for step 2 git-cliff-provisioning (exchange 1) (round 1)

- Resolve R1: preserve cleanup ownership on failure, clean remaining resources and cover inheritance-restoration/close failures.
- Resolve R2: protect setup and post-creation cleanup from interruptions; prove confirmed end or retained unconfirmed-end behavior, including repeated interruption.
- Resolve R3: enforce each native check's full timeout independently, prove stalled-helper cleanup and regenerate the eight-check native record against final sources.
- Reconcile the attributable unstaged Step 2 validation-plan review update, rerun the writer's required validation for repaired sources and publish a fresh exact staged request. Recheck `a.commit` if membership changes.

### Decision rationale for step 2 git-cliff-provisioning (exchange 1) (round 1)

Disposition: changes-requested. Six readiness-floor results: identity PASS; implementation completeness FAIL (R1-R3); validation and behavior coverage FAIL (missing cleanup/interrupt cases and unenforced native-check deadlines); staged attribution PASS for the unchanged request tree, with reviewer metadata explicitly attributable but unstaged and requiring reconciliation; unresolved findings FAIL (R1-R3); `a.commit` PASS mechanically and semantically. Green writer line coverage cannot establish these omitted failure contracts. No architecture dependency issue or file-size blocker was found; environment sorting and byte processing fit the plan.

### Final reviewer decision for step 2 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-1 -->

## Round 2 by requestor - Step 2

- Recorded: 2026-11-18T11:04:57+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 2
Review round: 2

### Code review evidence for step 2 git-cliff-provisioning (round 2)

request_index_tree: a8170531cbb60ae616124268afb7e668062a62e5
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: docs(review): code-span step 1 finding identifiers
group 1 path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
group 2: docs(git-cliff-provisioning): use process-limit job
group 2 path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
group 2 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
group 3: feat(release): contain Windows children in jobs
group 3 path: tools/release_workflow/windows_native.py
group 3 path: tools/release_workflow/windows_child.py
group 3 path: tools/release_workflow/windows_guard.py
group 3 path: tools/release_workflow/__init__.py
group 3 path: tests/unit/tools/release_workflow/native_kernel_fake.py
group 3 path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
group 4: test(release): record step 2 native checks
group 4 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 5: docs(git-cliff-provisioning): record step 2 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 5 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/native_kernel_fake.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/windows_child.py
staged path: tools/release_workflow/windows_guard.py
staged path: tools/release_workflow/windows_native.py
```

### Validation scope for step 2 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 2 git-cliff-provisioning (round 2)

Writer assessment for Step 2 of the git-cliff-provisioning plan, round 2: the
round 1 findings R1, R2 and R3 are repaired, and the step is fully
implemented. The implementation check, redone on the repaired tree over the
reviewer's attributable edit, records `Yes. Step 2 has been fully implemented.`
in the staged validation plan; the document status stays
`No, it is not implemented.` while Steps 3 to 8 are not started.

Evidence, all on the staged tree:

- Red first for the repairs: the thirteen new fault cases run against the
  reviewed `windows_child.py` (swapped in from the index, then restored and
  verified by SHA-256): `ghog single` exit 4, 10 failed. They pass with the
  repaired module (91 tests with the other kernel-based files and
  `test_windows_process_tdd.py`); every Step 2 test file passes together
  (107 tests).
- `ghog check` exit 0 after the repairs (one `FBT003` and one radon grade C on
  the recorder's `main` fixed on the way).
- Native record after the last source change: 8 of 8 checks passed through
  their bounded runners (0.46 s to 1.22 s each); the stalled runner timed out
  at its 3 s bound in 3.07 s, its helper alive at the bound and ended after
  it. The validator accepts the record.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7510 tests), on index tree
  `a8170531cbb60ae616124268afb7e668062a62e5`. No budget was changed and no
  exclusion is accepted.
- `rg -n 'subprocess\.(Popen|run|call)|AssignProcessToJobObject'` on the
  three modules: no match. `rg -n 'SetConsoleCtrlHandler'
  tools/release_workflow`: registration, removal and declaration only.
  `rg -n 'TerminateJobObject|\.join\(' tools/release_workflow/windows_child.py`:
  the termination in `_teardown`; the one reader join is in `_release`, which
  runs only after a confirmed end.
- Line counts: `windows_child.py` 547 (condensed docstrings keep it below
  550), `windows_native.py` 286, `windows_guard.py` 120,
  `native_kernel_fake.py` 446, `git_cliff_native_checks.py` 598 (in the 550 to
  650 band; the plan adds about 190 lines to it in Steps 4, 5 and 8, so Step 4
  applies the split guidance first, as the validation plan records).
- cSpell on the four Markdown files, the transcript included: clean. Markdown
  check: inside the green speed walk.

Architecture, performance and feature integrity are unchanged from round 1:
the repairs stay inside `windows_child.py`'s private `_Run` class and the
test-only recorder, add no import, and add a constant number of calls per
handle on failure paths only. `ContainmentError` gains `cleanup`, a tuple of
the failed reset or close calls whose handles `RETAINED` now owns.

Please check in particular: that no settling path can drop or double-close a
handle, that a failed reset of a caller's guard stays visible, the order of
deferred interrupts against `ContainmentError` and `UnconfirmedEndError`, the
teardown resumed after an interrupt (termination not repeated), and the
recorder's runner bound with its timeout demonstration.

### Implementation report for step 2 git-cliff-provisioning (round 2)

Step 2, "Contained Windows children and the use guard", is the second of
eight steps of the git-cliff-provisioning plan. It adds the engine's Windows
child layer and its first real-kernel evidence; nothing calls the layer
before Step 3.

Declarations, `tools/release_workflow/windows_native.py` (plan decisions Q04
and Q05):

- x64 structures `STARTUPINFOW` (104 bytes), `STARTUPINFOEXW` (112),
  `PROCESS_INFORMATION` (24), `JOBOBJECT_BASIC_LIMIT_INFORMATION`,
  `IO_COUNTERS`, `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` (144) and
  `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION` (48); the creation, attribute, job,
  file, wait, console and error constants; `PHANDLER_ROUTINE`.
- `NativeCallError(OSError)`: `call` and `winerror`, message
  `[WinError N] <call> failed`.
- `Kernel`: a protocol whose `__getattr__` returns a callable, met by the
  declared `WinDLL` and by the fake kernel.
- `kernel(loader=None)`: declares 23 functions (argument types, result type,
  error check) and caches the declared library per loader. Error checks:
  zero BOOL, NULL handle, NULL or `INVALID_HANDLE_VALUE` file handle,
  `WAIT_FAILED` and a failed `ResumeThread` raise `NativeCallError`;
  `InitializeProcThreadAttributeList` accepts only the sizing call's
  insufficient-buffer answer. Pointer arguments are declared as pointers to
  their type, so callers pass ctypes instances directly.

Lifecycle, `tools/release_workflow/windows_child.py`:

- `require_supported_platform(version=None, machine=None)`: major platform
  version 10 or later and an `AMD64` or `x86_64` machine, else
  `PlatformError` (`stage = "platform"`) naming Windows 10 or Windows Server
  2016 or later on x64 and what the machine runs.
- `ChildRequest` (frozen): `executable`, `arguments`, `cwd`, `environment`,
  `stdin` (`closed` or `inherit`), `output` (`capture` or `inherit`),
  `inherited` (guard handles), `deadline`, `record`; invalid stream modes,
  an empty name, `=` after the first character of a name and NUL characters
  are refused when it is built. `command_line()` is `list2cmdline`;
  `environment_block()` sorts by upper-cased name and ends with two NULs.
- `ChildOutcome` (frozen): `status`, `stdout`, `stderr`, `timed_out`,
  `identity`.
- `run_contained(request, *, api=None, sleep=time.sleep)`, in phases:
  1. Setup: `CreateJobObjectW(None, None)`, kill-on-close through
     `SetInformationJobObject`, `NUL` (`GENERIC_READ`, shared read and write)
     or `GetStdHandle`, two `CreatePipe` pairs or the parent's output handles,
     the attribute list sized, initialized and updated with the job list
     `(job,)` and the handle list (stdin, stdout, stderr deduplicated, then
     the guards).
  2. Creation: `GetHandleInformation` per listed handle and
     `SetHandleInformation` only for those not yet inheritable;
     `CreateProcessW` with `bInheritHandles` 1 and `CREATE_SUSPENDED`,
     `EXTENDED_STARTUPINFO_PRESENT` and `CREATE_UNICODE_ENVIRONMENT`; then the
     changed handles reset, the list deleted and the parent's write ends and
     `NUL` closed.
  3. Pre-resume: `GetProcessTimes` gives the `ProcessIdentity`, the callback
     receives it, then `ResumeThread`.
  4. Wait: two daemon `_Reader` threads call `ReadFile` on the native read
     handles into private chunks (`ERROR_BROKEN_PIPE` ends a reader, another
     error is kept), and `WaitForSingleObject` waits within the deadline in
     milliseconds, rounded up, or `INFINITE`.
  5. Teardown: `TerminateJobObject(job, 1)` once (a flag skips it when the
     teardown is rerun), `WaitForSingleObject(process, INFINITE)`, then
     `QueryInformationJobObject` until `ActiveProcesses` is 0, sleeping 10 ms
     between reads.
  6. Drain: `GetExitCodeProcess`, then `_release` (join the readers, reset
     what remains, close every owned handle: thread, process, read ends,
     job); a status, reader or close failure then raises `ContainmentError`.
  7. Unconfirmed end: a failing call of phase 5, or any other `Exception`
     while ending, appends a `RetainedChild` (PID, identity or `None`, call,
     handles, readers) to `RETAINED` and raises `UnconfirmedEndError`, closing
     and joining nothing.
  Round 1 repairs (R1, R2): phases 1 to 4 run in one `try`; any
  `BaseException` there calls `_settle`, which ends a created child through
  the shielded teardown, then runs the shielded `_release`; an `Exception`
  then becomes `ContainmentError` (`stage = "containment"`, `call`, `error`,
  `cleanup`), an interrupt propagates. `_release_creation_inputs` resets
  inheritance handle by handle and removes each only after success; `_close`
  takes a handle off its list before the call and puts it back on failure;
  both keep the failures and continue. After the creation inputs are
  released, `_raise_failed_release` fails the run on the first failure, and
  settling retries the release. `_containment` hands every handle still listed
  to `RETAINED` and names the failed calls in `cleanup`. `_shielded(action)`
  reruns the action after each `KeyboardInterrupt` and keeps the first;
  `execute` raises it after the outcome, or from a pending error, never in
  place of `UnconfirmedEndError`.
- `is_process_in_job(process, job=None, *, api=None)` and
  `ignore_console_interrupts(*, api=None)`, a context manager registering a
  `PHANDLER_ROUTINE` that handles `CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, kept
  referenced and removed on exit, errors included.

Use guard, `tools/release_workflow/windows_guard.py`:

- `open_guard(path, *, api=None)`: `CreateFileW(path, GENERIC_READ,
  FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)`; errors 2
  and 3 raise `FileNotFoundError`, others an `OSError` with the Windows error
  and the path.
- `UseGuard`: `path`, `handle`, `sha256_and_size()` (refused once closed;
  `DuplicateHandle`, `SetFilePointerEx` to 0, 1 MiB `ReadFile` loop, closes
  only the duplicate), idempotent `close()`, `retain()` (registers in
  `RETAINED`, after which `close()` does nothing), context manager.

Tests:

- `native_kernel_fake.py`: `FakeKernel` logs `(name, args)` per call, can fail
  the n-th call of a function with a Windows error or raise
  `KeyboardInterrupt` after it ran (`interrupt`), models handles, pipes
  with write-end holders (parent, root, descendant), files with a position
  shared by duplicates, one declared `FakeChild` and its job, and records the
  `CreateProcessW` arguments with the inheritance state of the listed handles.
  A pipe read gives up after 5 s with a fake-only error, so a wrong join
  order fails instead of hanging.
- `test_windows_native_tdd.py`: layouts, constants, all 23 declarations
  through a fake loader, every error check.
- `test_windows_child_tdd.py`: platform, request validation and environment
  block, exact call order, both lists and the inheritance window, streams and
  guards, the poll, deadlines, expiry, descendants, membership, console
  filter.
- `test_windows_child_faults_tdd.py`: each setup and creation fault, a
  missing standard handle, pre-resume faults, an interrupt, failures after
  resume, the three unconfirmed ends and the identity failure with an
  unconfirmed teardown; since round 1, a guard reset failing once and twice,
  a close failing twice, a refused creation with a failed reset and close, a
  failed close in the drain, interrupts during setup, right after creation,
  while polling and repeatedly, a pending interrupt over a containment error,
  an error while polling and an unconfirmed end over an interrupt.
- `test_windows_guard_tdd.py`: open arguments, missing files, sharing
  violation, hashing through duplicates, close and retain.

Native evidence:

- `git_cliff_native_checks.py`: started by hand
  (`python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone step-2 --output ...`), helper parents started as the same
  module with `--helper`, stand-in children from the interpreter with short
  scripts, temporary paths outside the repository, and every started process
  ended. Since round 1 (R3), each check runs in a runner process (the same
  module with `--run-check <id> <scratch> <result>`) started through
  `run_contained` with the check's bound as deadline; expiry ends the runner
  and its helper tree job-wide and records `timed-out`. An `api` wrapper over
  the real kernel keeps the job and process information and observes a
  descendant or helper before the outer termination; another fails
  `TerminateJobObject`.
- `native_checks.v1.json`: milestone `step-2`, commit `f11c37ff` (the base;
  the sources are uncommitted, their digests are what binds), Windows build
  and architecture, eight passed checks, and `recorder_timeout`: a stalled
  runner whose helper child is alive at the 3 s bound and ended after it.
- `test_git_cliff_native_evidence_tdd.py`: its own catalog of due checks,
  expected observations, bounds and sources, and the expected timeout
  demonstration; the committed record must pass for the current sources and
  hold no host path, user or host name; fourteen defective records are each
  refused for their own reason.

Documentation: the design and plan corrections and the validation plan entry
described in the change summary; the package docstring of
`tools/release_workflow/__init__.py` names the three modules.

Writer notes: `.reviews/a.git-cliff-provisioning.step2.journal.md` and
`.reviews/a.git-cliff-provisioning.step2.handoff.md`.

### Change summary for step 2 git-cliff-provisioning (round 2)

Staged paths (21, the same as round 1), grouped in the root `a.commit` (five
groups, checker `ready: true`):

1. `docs(review): code-span step 1 finding identifiers`:
   `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` (only the
   line 419 code spans are staged; the round entries this exchange appends
   stay unstaged for the residual commit).
2. `docs(git-cliff-provisioning): use process-limit job`:
   `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`,
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md`.
3. `feat(release): contain Windows children in jobs`:
   `tools/release_workflow/windows_native.py`,
   `tools/release_workflow/windows_child.py` (round 1 repairs R1 and R2),
   `tools/release_workflow/windows_guard.py`,
   `tools/release_workflow/__init__.py`,
   `tests/unit/tools/release_workflow/native_kernel_fake.py` (`interrupt`),
   the `test_windows_native/`, `test_windows_child/` (thirteen new fault
   cases) and `test_windows_guard/` leaves.
4. `test(release): record step 2 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py` (round 1
   repair R3: bounded runners, timeout demonstration),
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`
   (regenerated),
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`
   (timeout validation).
5. `docs(git-cliff-provisioning): record step 2 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md` (implementation
   check redone over the reviewer's edit), `.vscode/settings.json`.

Step 1 of this plan is committed and pushed (`f11c37ff` is the base of this
review).

### Writer response for step 2 git-cliff-provisioning (round 2)

Writer response:

Writer response:

All three round 1 findings are accepted and repaired; there is no
disagreement.

- **R1, cleanup ownership**: `_release_creation_inputs` removes a handle from
  `_restore` only after its reset succeeds, and keeps the failure. `_close`
  takes each handle off its list before the call (so an interrupt can leak a
  handle but never close it twice), puts it back when the close fails, keeps
  the failure and goes on. Settling retries what remains. A failed reset of a
  handle the run then closes is dropped as moot. Every failure path now runs
  the same release (`_release`: join, reset, delete the list, close the parent
  ends and every owned handle), so one cleanup failure never skips the rest.
  `_containment` hands whatever is left, a caller's guard still inheritable
  included, to `RETAINED`, and names the failed calls in the new
  `ContainmentError.cleanup`. New cases: a guard reset failing once (retried,
  restored) and twice (retained, named), a close failing twice (retained,
  every other handle closed after the end), a refused creation with a failed
  guard reset and a failed close, and a failed close in the drain.
- **R2, interrupted lifecycle**: setup and creation now run in the same
  `try` as the later phases, and any `BaseException` settles the attempt. A
  created child is ended and confirmed, then everything is released, before an
  `Exception` becomes `ContainmentError` or an interrupt propagates. The
  teardown and the release run through `_shielded`, which reruns the action to
  its end after each `KeyboardInterrupt` and keeps the first one. The
  teardown remembers a successful termination, so a rerun only reaps and
  polls. Any other exception while ending is an unconfirmed end, with the
  handles retained. `execute` then raises the deferred interrupt after the
  outcome, or chained to a pending `ContainmentError`, but never in place of
  `UnconfirmedEndError`. New cases: an interrupt during setup, right after
  creation, while polling (lingering count), and repeatedly (from the
  callback, twice in the poll, once during a close); a pending interrupt
  replacing a containment error; an error while polling; an unconfirmed end
  winning over an interrupt. The fake kernel's `interrupt(name, occurrence)`
  raises after the call ran, as Python delivers a Ctrl+C after a native call
  returns.
- **R3, native recorder bounds**: `_record` no longer runs a check in
  process. It starts the recorder module with `--run-check` through
  `run_contained` with the check's bound as deadline. On expiry, the job-wide
  termination ends the runner and its whole helper tree (nested jobs
  included) and the check is recorded `timed-out`; a runner that writes no
  result is `cannot-run` with its error output. The production reap is
  unchanged. The new `recorder_timeout` record entry comes from a deliberately
  stalled runner with a helper child: timed out at 3 s, helper alive at the
  bound, helper tree ended afterwards. The validator requires that entry
  (observation, bound and a 3 s to 15 s duration) and refuses four defective
  variants. The record was regenerated on the final sources.
- **Reviewer validation-plan edit**: the attributable unstaged update (No,
  Missing work R1 to R3) was accurate for round 1. I redid the implementation
  check over it on the repaired tree: Step 2 is back to Yes, the Missing work
  section is removed as done, and the evidence, line counts, performance and
  coverage sections describe the repairs. The result is staged.

Also changed: `windows_child.py` docstrings were condensed so the module stays
below the 550-line band (547), and the bodies of commit groups 3 and 4 now
mention the cleanup, interrupt and runner work; their subjects and membership
are unchanged.

### Reviewer focus for step 2 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-2 -->

## Round 2 by reviewer - Step 2

- Recorded: 2026-11-18T11:10:14+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: a8170531cbb60ae616124268afb7e668062a62e5

Assessed index tree: a8170531cbb60ae616124268afb7e668062a62e5

### Implementation check for step 2 git-cliff-provisioning (exchange 1) (round 2)

Result:

No. Step 2 has NOT been fully implemented. R3 is resolved by contained check runners and the stalled-runner demonstration. R1 and R2 remain incomplete at combined failure/interrupt and native-return boundaries. R4 records the newly introduced quadratic restoration traversal against the plan's linear phase bound. Reviewed the exact Step 2 plan, the round 1 to round 2 staged delta, the new tests, and the current validation-plan assessment.

Validation plan effects:

Updated only Step 2 in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`: No verdict, missing work R1/R2/R4, explicit resolution of R3, and performance/behavior-coverage conclusions. Markdown lint passed on the update; subsequent wording corrections changed no Markdown structure. Umbrella and other steps unchanged. Evidence launcher confirms attributable=true. The metadata remains unstaged because the required launcher has no staging operation and prohibits substituting direct Git index mutation; reconcile it as an explicit requestor handoff.

### Pre-repair mandatory checks and coverage for step 2 git-cliff-provisioning (exchange 1) (round 2)

No implementation repairs and no reviewer test execution. Writer reports 7,510 tests, 100% coverage, zero outliers/exclusions, 107 focused tests and eight passing native checks, plus a stalled-runner timeout in 3.07 seconds. These are writer evidence, not independently rerun results. Static traces below use the supplied fake kernel's after-call interrupt semantics. No numeric coverage shortfall is asserted. Reviewer Markdown lint of the edited validation plan passed.

### Resolved validation set and sources for step 2 git-cliff-provisioning (exchange 1) (round 2)

The request embeds `ghog day --full=speed --whole-suite`, provenance project, scope whole, proof speed, fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. `.review-validation` was sampled absent in round 2. The current resolver's built-in default plus whole-suite scope completion agrees with that set. No additions. The reviewer did not run the writer's full walk.

### Resolver drift and direction for step 2 git-cliff-provisioning (exchange 1) (round 2)

No drift found in static comparison of the embedded resolved set with the current resolver source and sampled project policy. The resolver executable was not independently invoked.

### Repository state around validation for step 2 git-cliff-provisioning (exchange 1) (round 2)

Baseline and assessed index tree: `a8170531cbb60ae616124268afb7e668062a62e5`, matching the round 2 request. Ordered validation-state comparison returned acceptable=false solely for the intentional reviewer Step 2 validation-plan metadata; no ignored or untracked deltas. The manual diff confirms no changes to other steps. Attribution returned attributable=true. Umbrella digest unchanged: `20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c`. No reviewer code/test edits.

### Repair inventory for step 2 git-cliff-provisioning (exchange 1) (round 2)

Repairs made:

- No substantive repairs. Only attributable Step 2 validation metadata changed; it is explicitly unstaged pending requestor reconciliation.

Paths staged:

- `.vscode/settings.json`
- `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
- `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py`
- `tests/unit/tools/release_workflow/native_kernel_fake.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_guard/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_native/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/windows_child.py`
- `tools/release_workflow/windows_guard.py`
- `tools/release_workflow/windows_native.py`

### Commit plan assessment for step 2 git-cliff-provisioning (exchange 1) (round 2)

Independent `commit-plan-check.bat --format json` returned exit 0, state valid, ready=true, 21 staged paths and no diagnostics. Manual inspection confirms the five groups' ordering, membership and conventional subjects remain appropriate. Updated bodies describe the intended repairs, whose completeness is challenged by R1/R2/R4. Ordered groups:

- `docs(review): code-span step 1 finding identifiers`
- `docs(git-cliff-provisioning): use process-limit job`
- `feat(release): contain Windows children in jobs`
- `test(release): record step 2 native checks`
- `docs(git-cliff-provisioning): record step 2 validation`

No grouping change needed. Reconcile the unstaged reviewer metadata and the implementation findings before committing.

### Findings and boundaries for step 2 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings:

- **R1 (P2, carried): Keep ownership and diagnostics when cleanup is interrupted.** `tools/release_workflow/windows_child.py:493` stores failed closes in a local `failed` list and only restores them at line 501. With a default captured request, `kernel.fail("CloseHandle", occurrence=1)` followed by `kernel.interrupt("CloseHandle", occurrence=2)` leaves the first write handle open: the second call interrupts after closing its own handle, discards the local failure list, and settling cannot retry or retain the first handle. Separately, an interrupted recording callback plus `kernel.fail("CloseHandle", occurrence=4)` leaves a failed handle in `_owned`, but `_phases` lines 294-298 reraises the original interrupt without `_containment`, so unresolved ownership is never transferred to `RETAINED` and diagnostics are lost. Make cleanup ownership durable across interrupted traversals and finalize unresolved-resource retention on interrupt paths too. Assert no lost or duplicate close and preserved cleanup diagnostics. These are static traces, not executed reproductions.
- **R2 (P2, carried): Close the gap between native side effects and ownership bookkeeping.** `tools/release_workflow/windows_child.py:367` enables inheritance before appending to `_restore`; with a captured request carrying a guard, `kernel.interrupt("SetHandleInformation", occurrence=4)` leaves that caller-owned guard inheritable and absent from restoration bookkeeping. `kernel.interrupt("CreateProcessW")` similarly fills `_info` but skips `_owned.extend` at line 374; settlement ends the child but never closes or retains its process/thread handles. Acquisition paths at lines 307, 330 and 344 and attribute-list initialization have the same interruption window. Ensure native-return interrupts cannot lose handles or restoration obligations, and test these boundaries explicitly. The existing test named right after creation interrupts a later reset, not `CreateProcessW`. Preserve confirmed-end and unconfirmed-end precedence while fixing ownership. These are static traces using the fake's documented after-call interrupts.
- **R4 (P3, new): Restore the planned linear cleanup traversal.** `tools/release_workflow/windows_child.py:381` walks a snapshot and calls `_restore.remove(handle)` for every successful reset at line 387. Each removal shifts the remaining list, giving quadratic work in the number of inherited handles accepted by `ChildRequest`. Use a linear pass with durable pending/failed ownership while addressing R1/R2; the current validation claim of linear phase cost is inaccurate. No timing regression was measured.

Boundary-crossing work:

- No implementation work crossed the reviewer boundary. No code/test repairs, umbrella edits, other-step edits, commit, convergence confirmation or requestor contact. Only authorized Step 2 validation metadata changed. The launcher staging limitation remains a metadata handoff, not an implementation repair.

### Writer instructions for step 2 git-cliff-provisioning (exchange 1) (round 2)

- Finish R1 with failure-plus-interrupt cases and retention even when an interrupt is the original error. Use the exact fake-kernel sequences in the findings.
- Finish R2 with interrupted native acquisition, process creation and inheritance enabling; assert every acquired handle and restoration obligation remains owned until settled.
- Address R4 during that cleanup rework using linear bookkeeping.
- Keep the R3 contained runners and timeout demonstration; regenerate their source-bound record after production changes.
- Reconcile the attributable unstaged validation-plan update, redo the implementation check and required writer validation, and publish the fresh exact staged request. Recheck `a.commit` if file membership changes.

### Decision rationale for step 2 git-cliff-provisioning (exchange 1) (round 2)

Disposition: changes-requested. R3 is resolved: check work executes inside its own contained runner, and the record/validator include a stalled-runner timeout and helper termination proof. R1/R2 are partially repaired but the explicit failure sequences above still lose resources or restoration obligations; R4 is the associated linear-bound gap. Six readiness-floor results: identity PASS; implementation completeness FAIL; validation/behavior coverage FAIL for the missing R1/R2 combinations; staged attribution PASS for the unchanged request tree, with attributable reviewer metadata explicitly unstaged; unresolved findings FAIL; `a.commit` PASS for grouping and subjects. Writer green line coverage does not establish the missing contracts. No dependency-layer violation found. Production files stay below 550 lines; the 598-line test recorder remains below the 650 ceiling and its future split checkpoint is recorded.

### Final reviewer decision for step 2 git-cliff-provisioning (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-2-round-2 -->

## Round 3 by requestor - Step 2

- Recorded: 2026-11-18T11:45:56+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: request

### Review identity for step 2 git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 2
Review round: 3

### Code review evidence for step 2 git-cliff-provisioning (round 3)

request_index_tree: f25f99705f9e1f52acb1e62abf421de3efbaf728
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: perf(tests): check module-level audit marks directly
group 1 path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
group 2: docs(review): code-span step 1 finding identifiers
group 2 path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
group 3: docs(git-cliff-provisioning): use process-limit job
group 3 path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
group 3 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
group 4: feat(release): contain Windows children in jobs
group 4 path: tools/release_workflow/windows_native.py
group 4 path: tools/release_workflow/windows_child.py
group 4 path: tools/release_workflow/windows_guard.py
group 4 path: tools/release_workflow/__init__.py
group 4 path: tests/unit/tools/release_workflow/native_kernel_fake.py
group 4 path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
group 5: test(release): record step 2 native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(git-cliff-provisioning): record step 2 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 6 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/native_kernel_fake.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_native/__init__.py
staged path: tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py
staged path: tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py
staged path: tools/release_workflow/__init__.py
staged path: tools/release_workflow/windows_child.py
staged path: tools/release_workflow/windows_guard.py
staged path: tools/release_workflow/windows_native.py
```

### Validation scope for step 2 git-cliff-provisioning (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 2 git-cliff-provisioning (round 3)

Writer assessment for Step 2 of the git-cliff-provisioning plan, round 3: the
round 2 findings R1, R2 and R4 are repaired (R3 was resolved in round 2), and
the step is fully implemented. The implementation check, redone on the
repaired tree over the reviewer's attributable edit, records
`Yes. Step 2 has been fully implemented.` in the staged validation plan; the
document status stays `No, it is not implemented.` while Steps 3 to 8 are not
started.

Evidence, all on the staged tree:

- Red first for the repairs: the nine new fault cases, the reviewer's exact
  sequences among them, run against the round 2 reviewed `windows_child.py`
  (swapped in from the index, then restored and verified by SHA-256):
  `ghog single` exit 2, 9 failed. They pass with the repaired module (100
  tests with the other kernel-based files and `test_windows_process_tdd.py`);
  every Step 2 test file passes together (116 tests).
- `ghog check` exit 0 after the repairs (one ty finding in the fake fixed).
- Native record after the last source change: 8 of 8 checks passed through
  their bounded runners (0.38 s to 1.03 s each); the stalled runner timed out
  at its 3 s bound in 3.08 s, its helper alive at the bound and ended after
  it. The validator accepts the record.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7519 tests), on index tree
  `f25f99705f9e1f52acb1e62abf421de3efbaf728`. On the way, the first walk
  measured a lifecycle CPU overrun (0.109 s) of one embedded-session test
  outside the step, now lowered (see the change summary); the second stopped
  at a ruff `RUF043` in that rework. No budget was changed and no exclusion is
  accepted.
- `rg` checks unchanged: no `subprocess` or `AssignProcessToJobObject` in the
  three modules; `SetConsoleCtrlHandler` only registered, removed and
  declared; the one reader join is in `_release`, after a confirmed end.
- Line counts: `windows_child.py` 594 (the review repairs moved it into the
  550 to 650 band; below the ceiling, recorded as variance; no later step
  plans to extend it), `native_kernel_fake.py` 456, the faults test 474, the
  recorder 598 (Step 4 splits it first, as recorded).
- cSpell on the four Markdown files, the transcript included: clean.

The repairs stay inside `windows_child.py`'s private `_Run` and the new
`_sigint_deferred` context manager around `run_contained`, plus the fake
kernel and the tests. The new import is `signal` (standard library).

Please check in particular: the Ctrl+C deferral scope (main thread with
Python's default SIGINT handler only; a launcher's console filter still wins),
the safe points (after setup, before `ResumeThread`, after the wait) and the
delivery once settled, write-ahead registration before enabling inheritance,
adoption of the process and thread handles from the process information, the
linear ordered-dict bookkeeping, and retention with a note when an interrupt
is the propagating error.

### Implementation report for step 2 git-cliff-provisioning (round 3)

Step 2, "Contained Windows children and the use guard", is the second of
eight steps of the git-cliff-provisioning plan. It adds the engine's Windows
child layer and its first real-kernel evidence; nothing calls the layer
before Step 3.

Declarations, `tools/release_workflow/windows_native.py` (plan decisions Q04
and Q05):

- x64 structures `STARTUPINFOW` (104 bytes), `STARTUPINFOEXW` (112),
  `PROCESS_INFORMATION` (24), `JOBOBJECT_BASIC_LIMIT_INFORMATION`,
  `IO_COUNTERS`, `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` (144) and
  `JOBOBJECT_BASIC_ACCOUNTING_INFORMATION` (48); the creation, attribute, job,
  file, wait, console and error constants; `PHANDLER_ROUTINE`.
- `NativeCallError(OSError)`: `call` and `winerror`, message
  `[WinError N] <call> failed`.
- `Kernel`: a protocol whose `__getattr__` returns a callable, met by the
  declared `WinDLL` and by the fake kernel.
- `kernel(loader=None)`: declares 23 functions (argument types, result type,
  error check) and caches the declared library per loader. Error checks:
  zero BOOL, NULL handle, NULL or `INVALID_HANDLE_VALUE` file handle,
  `WAIT_FAILED` and a failed `ResumeThread` raise `NativeCallError`;
  `InitializeProcThreadAttributeList` accepts only the sizing call's
  insufficient-buffer answer. Pointer arguments are declared as pointers to
  their type, so callers pass ctypes instances directly.

Lifecycle, `tools/release_workflow/windows_child.py`:

- `require_supported_platform(version=None, machine=None)`: major platform
  version 10 or later and an `AMD64` or `x86_64` machine, else
  `PlatformError` (`stage = "platform"`) naming Windows 10 or Windows Server
  2016 or later on x64 and what the machine runs.
- `ChildRequest` (frozen): `executable`, `arguments`, `cwd`, `environment`,
  `stdin` (`closed` or `inherit`), `output` (`capture` or `inherit`),
  `inherited` (guard handles), `deadline`, `record`; invalid stream modes,
  an empty name, `=` after the first character of a name and NUL characters
  are refused when it is built. `command_line()` is `list2cmdline`;
  `environment_block()` sorts by upper-cased name and ends with two NULs.
- `ChildOutcome` (frozen): `status`, `stdout`, `stderr`, `timed_out`,
  `identity`.
- `run_contained(request, *, api=None, sleep=time.sleep)`, in phases:
  1. Setup: `CreateJobObjectW(None, None)`, kill-on-close through
     `SetInformationJobObject`, `NUL` (`GENERIC_READ`, shared read and write)
     or `GetStdHandle`, two `CreatePipe` pairs or the parent's output handles,
     the attribute list sized, initialized and updated with the job list
     `(job,)` and the handle list (stdin, stdout, stderr deduplicated, then
     the guards).
  2. Creation: `GetHandleInformation` per listed handle and
     `SetHandleInformation` only for those not yet inheritable;
     `CreateProcessW` with `bInheritHandles` 1 and `CREATE_SUSPENDED`,
     `EXTENDED_STARTUPINFO_PRESENT` and `CREATE_UNICODE_ENVIRONMENT`; then the
     changed handles reset, the list deleted and the parent's write ends and
     `NUL` closed.
  3. Pre-resume: `GetProcessTimes` gives the `ProcessIdentity`, the callback
     receives it, then `ResumeThread`.
  4. Wait: two daemon `_Reader` threads call `ReadFile` on the native read
     handles into private chunks (`ERROR_BROKEN_PIPE` ends a reader, another
     error is kept), and `WaitForSingleObject` waits within the deadline in
     milliseconds, rounded up, or `INFINITE`.
  5. Teardown: `TerminateJobObject(job, 1)` once (a flag skips it when the
     teardown is rerun), `WaitForSingleObject(process, INFINITE)`, then
     `QueryInformationJobObject` until `ActiveProcesses` is 0, sleeping 10 ms
     between reads.
  6. Drain: `GetExitCodeProcess`, then `_release` (join the readers, reset
     what remains, close every owned handle: thread, process, read ends,
     job); a status, reader or close failure then raises `ContainmentError`.
  7. Unconfirmed end: a failing call of phase 5, or any other `Exception`
     while ending, appends a `RetainedChild` (PID, identity or `None`, call,
     handles, readers) to `RETAINED` and raises `UnconfirmedEndError`, closing
     and joining nothing.
  Settling (rounds 1 and 2): phases 1 to 4 run in one `try`; any
  `BaseException` there calls `_settle`, which ends a created child through
  the shielded teardown, runs the shielded `_release`, then
  `_retain_unreleased`. An `Exception` then becomes `ContainmentError`
  (`stage = "containment"`, `call`, `error`, `cleanup`); an interrupt
  propagates, with a note when handles were retained. Bookkeeping: `_owned`,
  `_parent_ends` and `_restore` are ordered dictionaries used as sets. A
  handle enters `_restore` before its inheritance is enabled, and
  `_adopt_child` owns the process and thread handles from `PROCESS_INFORMATION`
  after `CreateProcessW` and at every release. `_release_creation_inputs`
  deletes a reset handle only after success. `_close` deletes each handle
  before its call and re-adds it at once on failure. Both keep the failures and
  continue; a failed reset of a handle the run then closes is dropped.
  `_raise_failed_release` fails a created run on the first release failure, and
  settling retries the release. `_retain_unreleased` (after every settling and
  drain) hands what remains to `RETAINED` and records the failed calls.
  `_shielded(action)` reruns a settling action after each `KeyboardInterrupt`
  and keeps the first. Ctrl+C deferral (round 2): `run_contained` runs inside
  `_sigint_deferred`, which, on the main thread with Python's default SIGINT
  handler only, installs `_Run.defer_interrupt` (it records the Ctrl+C) and
  restores the default afterwards. `_interrupt_point` raises a recorded
  interrupt after setup, before `ResumeThread` and after the wait. `execute`
  raises a deferred interrupt after the outcome or from a pending error, never
  in place of `UnconfirmedEndError`.
- `is_process_in_job(process, job=None, *, api=None)` and
  `ignore_console_interrupts(*, api=None)`, a context manager registering a
  `PHANDLER_ROUTINE` that handles `CTRL_C_EVENT` and `CTRL_BREAK_EVENT`, kept
  referenced and removed on exit, errors included.

Use guard, `tools/release_workflow/windows_guard.py`:

- `open_guard(path, *, api=None)`: `CreateFileW(path, GENERIC_READ,
  FILE_SHARE_READ, None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None)`; errors 2
  and 3 raise `FileNotFoundError`, others an `OSError` with the Windows error
  and the path.
- `UseGuard`: `path`, `handle`, `sha256_and_size()` (refused once closed;
  `DuplicateHandle`, `SetFilePointerEx` to 0, 1 MiB `ReadFile` loop, closes
  only the duplicate), idempotent `close()`, `retain()` (registers in
  `RETAINED`, after which `close()` does nothing), context manager.

Tests:

- `native_kernel_fake.py`: `FakeKernel` logs `(name, args)` per call, can fail
  the n-th call of a function with a Windows error or deliver a Ctrl+C after
  it ran (`interrupt`, which calls the Python SIGINT handler then installed,
  as CPython does), models handles, pipes
  with write-end holders (parent, root, descendant), files with a position
  shared by duplicates, one declared `FakeChild` and its job, and records the
  `CreateProcessW` arguments with the inheritance state of the listed handles.
  A pipe read gives up after 5 s with a fake-only error, so a wrong join
  order fails instead of hanging.
- `test_windows_native_tdd.py`: layouts, constants, all 23 declarations
  through a fake loader, every error check.
- `test_windows_child_tdd.py`: platform, request validation and environment
  block, exact call order, both lists and the inheritance window, streams and
  guards, the poll, deadlines, expiry, descendants, membership, console
  filter.
- `test_windows_child_faults_tdd.py`: each setup and creation fault, a
  missing standard handle, pre-resume faults, an interrupt, failures after
  resume, the three unconfirmed ends and the identity failure with an
  unconfirmed teardown; since round 1, a guard reset failing once and twice,
  a close failing twice, a refused creation with a failed reset and close, a
  failed close in the drain, interrupts during setup, right after creation,
  while polling and repeatedly, a pending interrupt over a containment error,
  an error while polling and an unconfirmed end over an interrupt; since round
  2, a failed close then a Ctrl+C, a failed close behind an interrupt from the
  callback (retained and noted), a Ctrl+C at a guard's inheritance enabling,
  at `CreateProcessW` and at each acquisition, and the scope of the Ctrl+C
  deferral. An autouse fixture pins Python's default SIGINT handler, and every
  case asserts that no handle is closed twice.

Outside the step: `test_audit_declarations_tdd.py` keeps an embedded session
for the class-level inherited permission and checks the module level directly
on a module collector (a lifecycle CPU overrun of 0.109 s in the round 3
request walk).

- `test_windows_guard_tdd.py`: open arguments, missing files, sharing
  violation, hashing through duplicates, close and retain.

Native evidence:

- `git_cliff_native_checks.py`: started by hand
  (`python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone step-2 --output ...`), helper parents started as the same
  module with `--helper`, stand-in children from the interpreter with short
  scripts, temporary paths outside the repository, and every started process
  ended. Since round 1 (R3), each check runs in a runner process (the same
  module with `--run-check <id> <scratch> <result>`) started through
  `run_contained` with the check's bound as deadline; expiry ends the runner
  and its helper tree job-wide and records `timed-out`. An `api` wrapper over
  the real kernel keeps the job and process information and observes a
  descendant or helper before the outer termination; another fails
  `TerminateJobObject`.
- `native_checks.v1.json`: milestone `step-2`, commit `f11c37ff` (the base;
  the sources are uncommitted, their digests are what binds), Windows build
  and architecture, eight passed checks, and `recorder_timeout`: a stalled
  runner whose helper child is alive at the 3 s bound and ended after it.
- `test_git_cliff_native_evidence_tdd.py`: its own catalog of due checks,
  expected observations, bounds and sources, and the expected timeout
  demonstration; the committed record must pass for the current sources and
  hold no host path, user or host name; fourteen defective records are each
  refused for their own reason.

Documentation: the design and plan corrections and the validation plan entry
described in the change summary; the package docstring of
`tools/release_workflow/__init__.py` names the three modules.

Writer notes: `.reviews/a.git-cliff-provisioning.step2.journal.md` and
`.reviews/a.git-cliff-provisioning.step2.handoff.md`.

### Change summary for step 2 git-cliff-provisioning (round 3)

Staged paths (22: round 2's 21 plus one test file outside the step), grouped
in the root `a.commit` (six groups, checker `ready: true`):

0. `perf(tests): check module-level audit marks directly` (new):
   `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`.
1. `docs(review): code-span step 1 finding identifiers`:
   `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` (only the
   line 419 code spans are staged; the round entries this exchange appends
   stay unstaged for the residual commit).
2. `docs(git-cliff-provisioning): use process-limit job`: the design and the
   plan.
3. `feat(release): contain Windows children in jobs`: the three native
   modules (round 2 repairs in `windows_child.py`), the package docstring, the
   fake kernel (`interrupt` now calls the current SIGINT handler) and the
   `test_windows_native/`, `test_windows_child/` (nine new fault cases, an
   autouse default-handler fixture) and `test_windows_guard/` leaves.
4. `test(release): record step 2 native checks`: the recorder, the evidence
   test and `native_checks.v1.json` (regenerated on the final sources).
5. `docs(git-cliff-provisioning): record step 2 validation`: the validation
   plan (implementation check redone over the reviewer's round 2 edit) and
   `.vscode/settings.json`.

Step 1 of this plan is committed and pushed (`f11c37ff` is the base of this
review).

### Writer response for step 2 git-cliff-provisioning (round 3)

Writer response:

Writer response:

R1, R2 and R4 are accepted and repaired; there is no disagreement. R3 stays
as resolved in round 2: the contained runners and the stalled-runner
demonstration are unchanged, and the record was regenerated on the final
sources.

- **Root cause shared by R1 and R2**: a Ctrl+C delivered as a
  `KeyboardInterrupt` right after a native call returns can land between any
  side effect and its bookkeeping. CPython delivers it after the call
  returns. Instead of patching each window, `run_contained` now runs inside
  `_sigint_deferred`. On the main thread, when Python's default SIGINT
  handler is installed, it swaps in `_Run.defer_interrupt`, which only
  records the Ctrl+C, and restores the default handler afterwards. The run
  raises the recorded interrupt at safe points where every handle is
  accounted for (after setup, before `ResumeThread`, after the wait), so the
  ordinary settling path ends the child and releases everything. A Ctrl+C met
  while ending or releasing is raised once the run is settled, after an
  outcome or chained to a pending `ContainmentError`, never in place of
  `UnconfirmedEndError`. Other threads never receive `KeyboardInterrupt`. A
  custom or ignoring handler is left alone. A launcher's console filter
  (`ignore_console_interrupts`, registered before the run) still swallows
  Ctrl+C before Python sees it, so Step 8's passthrough contract is
  unaffected.
- The fake kernel's `interrupt(name, occurrence)` now calls the Python SIGINT
  handler then installed, as CPython does after a native call returns, rather
  than raising `KeyboardInterrupt` itself. Under the default handler it still
  raises; under a run's handler it is recorded. An autouse fixture in the
  faults file pins the default handler for each case, so the cases behave the
  same under xdist workers.
- **R1**: `_close` takes each handle out of its set before the call and puts
  it back at once when the close fails, with no local list, so neither a
  failure nor an interrupt can drop or repeat a close (every case now asserts
  no duplicate close). `_retain_unreleased` runs after every settling and
  every drain, whatever error then propagates. It hands what remains to
  `RETAINED` and records the failed calls, which become
  `ContainmentError.cleanup` or, when an interrupt propagates, a note on it.
  The reviewer's two sequences are covered: fail `CloseHandle` 1 with a Ctrl+C
  at `CloseHandle` 2, and an interrupt from the callback with a failed
  `CloseHandle` 4.
- **R2**: a handle is registered in `_restore` before `SetHandleInformation`
  enables its inheritance. `_adopt_child` owns the process and thread handles
  from the filled `PROCESS_INFORMATION`, right after `CreateProcessW` and
  again at every release. With the deferral, acquisition calls (job, `NUL`,
  pipes, attribute list) complete their bookkeeping before any interrupt is
  raised. Covered: a Ctrl+C at the guard's `SetHandleInformation` 4, at
  `CreateProcessW`, and at `CreateJobObjectW`, `CreateFileW`, the second
  `CreatePipe` and the list initialization. The scope of the deferral (main
  thread, default handler, other thread, ignoring handler) has its own case.
- **R4**: `_owned`, `_parent_ends` and `_restore` are ordered dictionaries
  used as sets: removal, re-addition and membership are constant time, so
  every release is linear in the handles; the close order is unchanged.
- **Reviewer validation-plan edit**: accurate for round 2; I redid the
  implementation check over it on the repaired tree. Step 2 is back to Yes,
  Missing work is removed as done, the reviewer's clearer "one required
  `O(n log n)` sort" wording is kept, and the repairs, evidence, line counts,
  performance and coverage sections are updated. The result is staged.

Also changed, outside the step: the first round 3 request walk measured
0.109 s of lifecycle CPU (above the 0.100 s ceiling, not proven) for
`test_audit_declarations_tdd.py::test_inherited_permissions_are_invalid[module]`.
As Step 1 did for the same file, the class-level case keeps its embedded
session, and the module-level case calls the plugin's collector check directly
on a module collector carrying the mark. It is a new first commit group,
`perf(tests): check module-level audit marks directly`, disclosed in the
validation plan.

### Reviewer focus for step 2 git-cliff-provisioning (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-2-round-3 -->

## Round 3 by reviewer - Step 2

- Recorded: 2026-11-18T11:52:24+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: answer

### Assessed index identity for step 2 git-cliff-provisioning (exchange 1) (round 3)

Baseline index tree: f25f99705f9e1f52acb1e62abf421de3efbaf728

Assessed index tree: f25f99705f9e1f52acb1e62abf421de3efbaf728

### Implementation check for step 2 git-cliff-provisioning (exchange 1) (round 3)

Result:

Yes. Step 2 has been fully implemented.

R1 is resolved: failed closes are restored immediately to durable ownership, and `_retain_unreleased` runs after settling and draining even when the original error is an interrupt. R2 is resolved for Python's default SIGINT delivery: `_sigint_deferred` records the signal across native effects and bookkeeping; safe points follow setup, precede resume and follow the wait. Inheritance restoration is registered before enabling it, and `_adopt_child` accounts for filled process information during creation and release. Custom handlers and worker threads are deliberately left untouched. Unconfirmed termination still takes precedence over an interrupt. The new cases cover the exact reported sequences and acquisition windows.

R3 remains resolved by contained per-check runners and the refreshed stalled-runner demonstration. R4 is resolved by ordered dictionaries used as sets; reset and close passes are linear in handle count. The prescribed environment sort remains O(n log n).

Static assessment found no architecture violation, missing top-level exercise, or impaired existing behavior. Coverage scope is `tools`, excluding tests and package initializers; the fake and recorder are assessed by references, not by assigning them the writer's coverage percentage. The 594-line child module remains below the ceiling; the recorder's planned split before Step 4 remains recorded.

Validation plan effects:

Only the exact Step 2 analysis and unit-coverage paragraphs were amended. The exact Yes sentence remains; no Missing work section is needed. Added the independent round 3 conclusion and clarified that the 7,519-test, 100% coverage report belongs to the writer. Other steps and document-level status were untouched. Markdown lint completed with zero issues. The patch is attributable and remains unstaged: the canonical evidence launcher exposes attribution but no staging operation; no direct Git index mutation was substituted.

### Pre-repair mandatory checks and coverage for step 2 git-cliff-provisioning (exchange 1) (round 3)

The writer reports nine new regression cases failing against round 2, then passing with the repair; 100 kernel/process tests and all 116 Step 2 tests pass. Writer `ghog check` passed. Writer whole-suite speed validation on request tree `f25f99705f9e1f52acb1e62abf421de3efbaf728` passed 7,519 tests with measured coverage 100%, zero outliers and zero exclusions. The committed native record reports eight passed checks (0.378–1.029 s), plus the stalled runner timing out at its 3 s bound in 3.084 s and ending its helper tree. These are inspected writer artifacts, not reviewer reruns. The reviewer ran no test or coverage command; independent execution was limited to the commit-plan/evidence launchers and Markdown lint.

### Resolved validation set and sources for step 2 git-cliff-provisioning (exchange 1) (round 3)

`ghog day --full=speed --whole-suite`, source `project`. The bound scope capture is whole-suite with fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. `.review-validation` was sampled absent for this round. No additive plan or request command was declared.

### Resolver drift and direction for step 2 git-cliff-provisioning (exchange 1) (round 3)

No drift found by static comparison with the current canonical resolver and sampled policy: the absent declaration selects `ghog day --full=speed`, completed with the bound whole-suite selector. The embedded command and project provenance agree. The resolver executable was not independently invoked.

### Repository state around validation for step 2 git-cliff-provisioning (exchange 1) (round 3)

Baseline and assessed index trees both equal the request tree `f25f99705f9e1f52acb1e62abf421de3efbaf728`. The ordered 22-path validation comparison detects only the reviewer's Step 2 validation-plan edit; its raw `acceptable: false` denotes that tracked difference, which the reviewer contract permits as metadata. No other tracked or untracked path changed during assessment. Umbrella digest remains `20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c`. Attribution reports `attributable: true`.

### Repair inventory for step 2 git-cliff-provisioning (exchange 1) (round 3)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`: polishing-only review metadata in Step 2, attributable and unstaged.
- No substantive reviewer repair, implementation/test edit, or `a.commit` change.

Paths staged:

- `.vscode/settings.json`
- `docs/v0.14.0/design.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md`
- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
- `docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py`
- `tests/unit/tools/release_workflow/native_kernel_fake.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_faults_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_guard/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_guard/test_windows_guard_tdd.py`
- `tests/unit/tools/release_workflow/test_windows_native/__init__.py`
- `tests/unit/tools/release_workflow/test_windows_native/test_windows_native_tdd.py`
- `tools/release_workflow/__init__.py`
- `tools/release_workflow/windows_child.py`
- `tools/release_workflow/windows_guard.py`
- `tools/release_workflow/windows_native.py`
- `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`

### Commit plan assessment for step 2 git-cliff-provisioning (exchange 1) (round 3)

Independent `commit-plan-check.bat --format json` returned exit 0, `state: valid`, `ready: true`, and no diagnostics. Its 22 staged paths and six ordered groups match the request and `a.commit`: audit-test optimization; Step 1 transcript code spans; process-limit documentation; Windows child implementation and unit tests; native recorder and evidence; Step 2 validation and spelling entries. Membership, dependency order, scopes and conventional subjects remain accurate. The transcript was not read as working context. Reviewer metadata can be reconciled into the existing validation group without changing membership.

Disclosed writer scope:

- Writer-owned `tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py` lies outside Step 2 and is disclosed as a separate first group. Its direct module-collector check retains the UsageError/message assertion, while the class case keeps a real collection session. The shared collector hook and rejection implementation were inspected; no blocker found. The reported cost removed is one redundant embedded pytest session; no new timing measurement was made by the reviewer.
- Earlier documentation, spelling and transcript-format changes remain disclosed in their existing groups. The reviewer made no boundary-crossing change.

### Findings and boundaries for step 2 git-cliff-provisioning (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 2 git-cliff-provisioning (exchange 1) (round 3)

Reconcile the attributable unstaged Step 2 review metadata into the existing validation group without sweeping unrelated work into the index. This is an advisory commit-ready recommendation; the requestor owns consumption and the human convergence gate. The reviewer grants no commit authorization.

### Decision rationale for step 2 git-cliff-provisioning (exchange 1) (round 3)

All six readiness-floor results pass: exact identity and request tree; complete Step 2 implementation; sufficient inspected writer validation and static coverage evidence; attributable staged scope with only permitted reviewer metadata outside the index; no unresolved finding; and independently valid `a.commit`. No substantive reviewer repair occurred. Recommend commit-ready.

### Final reviewer decision for step 2 git-cliff-provisioning (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-2-round-3 -->

## Round 3 by human - Step 2 - human-confirmation

- Recorded: 2026-11-18T13:52:29+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 2
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 1 by requestor - Step 3

- Recorded: 2026-11-18T21:15:09+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 3
- Outcome: request

### Review identity for step 3 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 3
Review round: 1

### Code review evidence for step 3 git-cliff-provisioning (round 1)

request_index_tree: 3efddd6aed408e84d4672d1797544b73a7dbe234
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the git-cliff cache and its lock
group 1 path: .gitignore
group 1 path: tools/release_workflow/git_cliff/__init__.py
group 1 path: tools/release_workflow/git_cliff/cache.py
group 1 path: tools/release_workflow/git_cliff/cache_lock.py
group 1 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py
group 2: docs(git-cliff-provisioning): record step 3 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: .gitignore
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
```

### Validation scope for step 3 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 3 git-cliff-provisioning (round 1)

Writer assessment for Step 3 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and its implementation check records
`Yes. Step 3 has been fully implemented.` in the staged validation plan,
whose document status stays `No, it is not implemented.` while Steps 4 to 8
are not started.

Evidence, all on the staged tree:

- Tests first: with `cache.py` and `cache_lock.py` held aside, `ghog single`
  on the four Step 3 test files failed at collection on the missing
  `tools.release_workflow.git_cliff.cache` module (exit 4). With the modules
  restored they pass.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after one walk that failed at check: ty and pyright on the test support
  (untyped default factories, `io.open` and `os.open` wrappers, a scheduled
  action returning a value), ruff (`PLR0911` on the reuse validator, now split
  into three helpers; `D301` on the lock docstring, now raw; `EM101`, `S105`,
  `PLR0913` and `PTH116` in tests). Four tests were then added for paths a
  static coverage reading found unexercised (owner file fields, default seams,
  empty caller kind, unreadable owner file).
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7636 tests, slowest call
  0.79 s, outside this step), on index tree
  `3efddd6aed408e84d4672d1797544b73a7dbe234`. No budget was changed and no
  exclusion is accepted (`ghog exclude --list`: `exclusions=0`).
- `rg -n '\.tools/git-cliff/' .gitignore`: line 124.
  `rg -n 'getmtime|st_mtime|age' tools/release_workflow/git_cliff/cache_lock.py`:
  no match. `rg -n 'subprocess|Popen'
  tests/unit/tools/release_workflow/git_cliff_support.py`: no match.
- Line counts: `cache.py` 395 (advisory 260), `cache_lock.py` 358 (290),
  `git_cliff_support.py` 318 (230), tests 289, 49, 217 and 175; every Python
  file stays below 550.
- Markdown check and cSpell on the staged validation plan: clean.
- No source file covered by the committed native check record changed, so
  `native_checks.v1.json` needs no refresh.

Architecture: `cache` defines the `Guard` and `CachePin` ports it consumes and
receives the guard opener and the probe; it imports only `lock_records`,
`windows_process.ProcessIdentity` and the `windows_child` error and outcome
types. `cache_lock` depends on `cache` and the `budget` constants, reaches the
kernel only through `LockSeams` (defaults: the unchanged `windows_process`
primitives) and stays separate from the project `OperationLock`.
Performance: reuse is one guard, one record read, one hash pass and one
probe; a poll is one mutex entry, one record read and the liveness probes;
recovery lists one version directory once without recursion. Feature
integrity: no existing module changes behavior; the ignore rule covers only
`/.tools/git-cliff/`.

Please check in particular: the reuse order and that no ordinary failure
leaves the guard open while an unconfirmed probe end leaves it retained; that
no path publishes over or removes a record whose owner or any child is not
proven `DEAD`; the deadline and polling arithmetic of the wait; ownership
checks in `record_child`, `release` and after `retain_record()`; the attempt
recovery rules, including a missing owner file meaning no child; the layout's
refusal of names that could reach `evidence/` or leave their directory; and
the interface details that differ from the plan's sketch (writer response).

### Implementation report for step 3 git-cliff-provisioning (round 1)

Step 3, "Cache layout, entry record, reuse check and the cache lock", is the
third of eight steps of the git-cliff-provisioning plan. It adds the cache of
the executing checkout, the lock-free reuse check and the provisioning lock of
one version and platform; nothing calls them before Step 5.

Cache, `tools/release_workflow/git_cliff/cache.py` (design "Cache layout and
the local integrity record" and "Reuse check and the use guard"; design
decisions Q03, Q07 and Q12):

- `CachePin` (protocol: `version`, `triple`) and `Guard` (protocol: `path`,
  `handle`, `sha256_and_size()`, `close()`, `retain()`), met by
  `manifest.AdmittedPin` and `windows_guard.UseGuard`.
- `CacheLayout(tooling_root, namespace="production")` (frozen): `root` is
  `<tooling_root>/.tools/git-cliff`, or its `evidence` folder; any other
  namespace raises `ValueError`. `version_dir`, `entry_dir`, `executable`,
  `record`, `lock_path` and `attempt_dir(pin, kind, owner, token)`. A version
  directory name must match `[0-9]+\.[0-9]+\.[0-9]+` and a triple
  `[a-z0-9_]+(-[a-z0-9_]+)+`, otherwise `ValueError` ("not a cache place"),
  so no production pin resolves into `evidence/`. Attempt names are
  `.staging-<pid>-<created>-<token>` and `.retired-...` with a positive PID
  and creation time and a lowercase hexadecimal token; `parse_attempt(name)`
  (static) returns `Attempt(kind, owner, token)` for a canonical name and
  `None` otherwise (leading zeros, suffixes, other kinds).
- `EntryRecord` (frozen, keyword-only, schema 1): `version`, `triple`,
  `asset`, `asset_sha256`, `executable_sha256`, `executable_size`,
  `provisioned`. `__post_init__` refuses another schema, an empty name, a
  digest that is not 64 lowercase hexadecimal characters, a size below 1 and
  a `provisioned` time without an offset. `encode()` writes one JSON line in
  a fixed key order; `decode()` uses `lock_records.decode_object` with the
  `entry` label and requires exactly the eight keys.
- `OwnerFile(owner, children=())` (frozen, schema 1): `with_child`, `encode`,
  `decode` with the `owner file` label and exactly four keys. The shared
  helpers `identity_fields`, `decode_children` (a list of objects holding
  exactly a positive `pid` and `created`) and `local_time` (ISO time with an
  offset) also serve the lock record.
- `check_entry(layout, pin, *, open_guard, probe) -> EntryCheck`, where
  `EntryCheck` is `ValidEntry(guard, record) | UnusableEntry(absent, reason)`:
  1. `open_guard(executable)`; `FileNotFoundError` returns the absent result,
     any other error propagates.
  2. `entry.json` read; missing, undecodable or naming another version or
     triple returns an invalid result, before any hash.
  3. `guard.sha256_and_size()`; a size or digest other than the record's
     returns an invalid result, before the probe.
  4. `probe(guard) -> ChildOutcome`; timed out, a status other than 0 or a
     first line other than `git-cliff <pin>` returns an invalid result.
  Every invalid result closes the guard. An `UnconfirmedEndError` from the
  probe calls `guard.retain()` and propagates; any other exception closes the
  guard and propagates. A valid result keeps the guard open for the caller.

Lock, `tools/release_workflow/git_cliff/cache_lock.py` (design "Provisioning
lock, contention and recovery"; design decisions Q03 and Q04):

- `LockRecord(owner, started, caller, children=())` (frozen, schema 1, six
  keys, non-empty caller, `started` with an offset).
- `LockSeams` (frozen, keyword-only): `clock` and `sleep` required; `probe`
  (`process_state`), `current` (`current_identity`), `mutex`
  (`transition_mutex`) and `now` (local time with offset) default to the
  item 1 primitives.
- `CacheLock(layout, pin, *, caller, seams)`; the first transition creates
  the version directory with its parents and names the mutex
  `Global\llm-shared-git-cliff-<dev>-<ino>-<namespace>-<version>-<triple>`
  from `stat` of `layout.root`.
- `acquire(wait_seconds, on_wait)`: deadline fixed once. Each poll enters the
  mutex and reads the record. Absent: publish this caller's record (flushed
  temporary from `tempfile.mkstemp` beside it, then `Path.rename`, which
  Windows never lets replace). Present with owner and every child `DEAD`
  (owner probed first, children only then): replace it with `Path.replace` in
  the same transition. Otherwise the holder is returned. The first holder
  gets `on_wait(holder, W)` once; then `sleep(min(0.25, remaining))` until
  the deadline, where `LockWaitError(path, holder, W)` is raised (message:
  path, PID, start time, caller kind, W and `LOCK_WAIT_REMEDY`, the design's
  lock-wait remedy). The temporary is always unlinked. An unverifiable record
  raises `LockRecordError` at once; acquiring a held lock is refused.
- `record_child(identity)`, `release()` and `retain_record()`: each change
  rereads the record under the mutex and requires it to equal the held one;
  `release` unlinks it. After `retain_record()`, `release` returns without
  touching anything and `record_child` and `recover_attempts` raise
  `LockRecordError`.
- `recover_attempts()`: refused unless held; one `os.scandir` of the version
  directory; for each directory (not following links) whose name parses as an
  attempt: probe the name owner; read `owner.json` (missing: no children;
  another read error or an invalid file: keep); require the same owner and
  every child `DEAD`; then `shutil.rmtree`, a refusal keeping the directory.
  Returns the removed names.

Ignore rule: the root `.gitignore` ends with a comment and
`/.tools/git-cliff/` (design "Ignore rule", requirement Q05, plan Q01).

Tests (no process, no native call, no real wait):

- `git_cliff_support.py`: `FakeClock` (monotonic, `now`, `sleep`, scheduled
  actions), `ProcessStates` (undeclared is `UNKNOWN`, queries recorded),
  `UncontendedMutex` (can declare entries abandoned), `LockWorld` (lock built
  on those seams, `hold`, `attempt`, `declare`, `on_wait` recording),
  `synthetic_pin()` from a generated archive with its real size and SHA-256,
  `entry_record`, `install_entry`, `FakeGuard` and `FakeGuardOpener` over
  scenario files, `FakeProbe`, and `deny_writes`.
- `test_git_cliff_cache_tdd.py`: fixed paths, evidence namespace, refused
  names and namespace, attempt names both ways, the `.gitignore` line, entry
  record round trip and thirteen invalid records, owner file round trip and
  refusals, and every reuse outcome in order, including the valid reuse under
  `deny_writes` and the retained guard on an unconfirmed probe end.
- `test_git_cliff_cache_pbt.py`: attempt names and entry records round-trip.
- `test_git_cliff_cache_lock_tdd.py`: publication and key order, mutex names
  in both namespaces, a live holder until W (4 sleeps of 0.25 s, 5 polls, one
  callback, exact message), release mid-wait, a holder change, child
  recording, release and a replaced record, retention, refused double
  acquisition and retention, the caller kind, the default seams and eleven
  unverifiable records.
- `test_git_cliff_cache_lock_recovery_tdd.py`: dead owner and children
  recovered in one transition; a live or `UNKNOWN` child, an `UNKNOWN` owner
  and an abandoned mutex keep the record; eight attempt verdicts for both
  kinds; non-attempt entries and an unreadable owner file kept; recovery
  refused without the lock; a refused removal kept.

Documentation: the validation plan entry and the `git_cliff/__init__.py`
docstring described in the change summary.

Writer notes: `.reviews/a.git-cliff-provisioning.step3.journal.md` and
`.reviews/a.git-cliff-provisioning.step3.handoff.md`.

### Change summary for step 3 git-cliff-provisioning (round 1)

Staged paths (12), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the git-cliff cache and its lock`:
   `.gitignore`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/cache_lock.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py`.
   The ignore rule travels with the first code that writes under the cache
   path (design "Ignore rule", plan decision Q01).
2. `docs(git-cliff-provisioning): record step 3 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 and 2 of this plan are committed and pushed (`644f0041` is the base
of this review). This round's transcript entry is appended to
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and stays
unstaged for the residual commit.

### Writer response for step 3 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 3 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- `CacheLock` takes its seams as one frozen `LockSeams` value instead of the
  six keywords of the plan's sketch, because the repository's lint allows
  five arguments (ruff `PLR0913`); the defaults are the item 1
  `windows_process` primitives.
- `recover_attempts()` takes no pin: a lock already serves exactly one
  version and platform, and another pin would clean a version the caller does
  not lock.
- A pin is typed as the `CachePin` protocol (`version`, `triple`), so the
  Step 6 evidence candidates fit the layout without being admitted pins. The
  layout refuses any version or triple that is not a plain name instead of
  relying on admission, which is how production can never reach `evidence/`.
- The probe seam returns the `ChildOutcome` of Step 2: beside the first line,
  a timed-out probe or a status other than 0 makes the entry invalid.
- A guard open failure other than a missing executable propagates instead of
  making the entry invalid, so its real cause reaches the diagnostic rather
  than a retirement attempt that would fail on the same handle.
- An unverifiable lock record raises `LockRecordError` at once instead of
  being waited on: it cannot prove an owner, so it is never recovered, and
  waiting W cannot change it. It stays in place.
- A missing `owner.json` in an attempt directory means no child was recorded:
  Step 5 writes it before creating any child and removes it only after every
  recorded child has exited. A present but unreadable or invalid owner file,
  or one naming another owner, keeps the directory.
- A lock record publication writes a flushed temporary beside the record;
  a crash between that write and the rename can leave a temporary, which
  confers no ownership, as for the project operation lock.
- `record_child` rewrites the complete record: the design publishes only
  complete records, and an attempt records at most three children.

### Reviewer focus for step 3 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-1 -->

## Round 1 by reviewer - Step 3

- Recorded: 2026-11-18T21:24:44+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: 3efddd6aed408e84d4672d1797544b73a7dbe234

Assessed index tree: 3efddd6aed408e84d4672d1797544b73a7dbe234

### Implementation check for step 3 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 3 has NOT been fully implemented.

The cache layout, strict persisted records, guard -> record -> hash -> probe reuse order, retention on UnconfirmedEndError, DEAD-only recovery and root ignore rule match the step. The LockSeams and CachePin interface adjustments preserve the intended boundaries. R1 blocks completeness: acquisition can succeed after the fixed wait deadline.

Architecture: no dependency-direction violation; cache owns its consumed ports, and `cache_lock` uses injected Windows primitives. All added Python files are below 550 lines. Work is linear in hashed bytes, polls or recovered files; the deadline gap is the performance-contract defect.

Static unit-test review covers all four new test files and their support module. The coverage gate measures tools, excluding tests and initializers. Every top-level test-support symbol is referenced, including default factories and module-level builders. The reported 100% line coverage does not exercise oversleep or elapsed time inside a transition. No reviewer tests or coverage measurement were run. Existing behavior is unchanged because the added modules are not wired until Step 5.

Validation plan effects:

Only Step 3 rows of docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md changed: exact No status, R1 missing-work bullets, bounded-wait assessment, static coverage evidence and correction of the construction-versus-decoding description. No other step, opening document status or umbrella row was changed.

The evidence launcher reports the patch attributable. Its attribute-reviewer-patch operation returns a patch but does not stage it; the reviewer left this metadata patch unstaged for writer reconciliation rather than substituting a direct index mutation. Markdown lint and git diff --check pass.

### Pre-repair mandatory checks and coverage for step 3 git-cliff-provisioning (exchange 1) (round 1)

Request-time and independently captured baseline index tree: 3efddd6aed408e84d4672d1797544b73a7dbe234. The requestor reports ghog day --full=speed --whole-suite green on that tree: 7636 tests, coverage 100, outliers 0, exclusions 0. These are writer-reported results. This review ran no ghog command and measured no coverage; it assessed source, tests and the exact bound scope statically.

### Resolved validation set and sources for step 3 git-cliff-provisioning (exchange 1) (round 1)

ghog day --full=speed --whole-suite (source: project). The bound scope file is .reviews/a.review-scope.code.v0.14.0.git-cliff-provisioning.json, scope whole, fingerprint 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6, proof speed. No plan or request additions were declared.

### Resolver drift and direction for step 3 git-cliff-provisioning (exchange 1) (round 1)

No drift. Test-Path sampled the exact root .review-validation during assessment and returned false. The resolver's built-in ghog day --full=speed default completed with the bound --whole-suite selector equals the request command and its project source.

### Repository state around validation for step 3 git-cliff-provisioning (exchange 1) (round 1)

Before and after index trees both equal 3efddd6aed408e84d4672d1797544b73a7dbe234. The evidence boundary reports only the exact validation-plan path changed, attributable to this review and confined to Step 3. The raw validation comparator returns acceptable:false because that tracked metadata changed; the reviewer-mode contract explicitly permits those rows. No implementation or test changed, no untracked validation side effect appeared, and the umbrella digest is unchanged: 20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c.

### Repair inventory for step 3 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md: polishing-only review metadata; Step 3 assessment and missing-work list. Attributable, left unstaged for writer reconciliation. No substantive implementation or test repair.

Paths staged:

- .gitignore
- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
- `tests/unit/tools/release_workflow/git_cliff_support.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py`
- `tools/release_workflow/git_cliff/__init__.py`
- `tools/release_workflow/git_cliff/cache.py`
- `tools/release_workflow/git_cliff/cache_lock.py`

### Commit plan assessment for step 3 git-cliff-provisioning (exchange 1) (round 1)

Independent commit-plan-check.bat --format json returned exit 0, state valid, ready true, diagnostics []. Ordered groups: (1) feat(release): add the git-cliff cache and its lock, with the 11 implementation/ignore/test paths; (2) docs(git-cliff-provisioning): record step 3 validation, with the validation plan. All 12 staged paths occur exactly once. Grouping, ordering and subjects remain appropriate; a.commit was not changed. Its prose claims Step 3 is implemented, so reconcile that claim with R1 and the revised validation rows before the next request.

### Findings and boundaries for step 3 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- R1 [P2] Enforce the wait deadline before acquiring a newly freed lock. In `tools/release_workflow/git_cliff/cache_lock.py`:283, acquire calls `_poll` before inspecting remaining time; `_poll` at lines 253-262 publishes and returns None without checking the deadline. Example traced from the code: with W=360, the last sleep starts at 359.75, resumes at 360.5 after scheduling delay, and the holder has released in between. `_poll` publishes this caller's record and acquire returns success at 360.5 instead of LockWaitError. A mutex entry or DEAD-actor probe that crosses W has the same effect. This defeats the caller's own finite wait and can start provisioning after its budget expired. Carry the original deadline into the transition, reject expiry after waiting and before publication/recovery under the mutex, and retain last-holder diagnostics. Add fake-clock regressions for oversleep plus release and for a transition/probe crossing W; assert no ownership publication or DEAD-record replacement after expiry. Existing tests use an exact FakeClock.sleep and UncontendedMutex, so the reported green suite does not cover this scenario. This is a static code trace, not a claimed executed reproduction.

Boundary-crossing work: None.

### Writer instructions for step 3 git-cliff-provisioning (exchange 1) (round 1)

Fix R1 within `cache_lock.py` and its unit tests. Preserve successful acquisition before W, one waiting callback, the unchanged deadline and DEAD-only recovery. Reconcile the attributable unstaged Step 3 validation metadata, update the implementation check and a.commit prose to the resulting state, run the writer-owned required validation set, and publish another exact staged review request with its new index tree. No Human guidance block authorized reviewer code repairs.

### Decision rationale for step 3 git-cliff-provisioning (exchange 1) (round 1)

Readiness floor:

1. Exact identity: PASS, code/code v0.14.0 git-cliff-provisioning, Step 3 round 1 occurrence 1; request tree matches the baseline.
2. Complete implementation: FAIL, R1 allows acquisition after W.
3. Validation and coverage: FAIL, writer reports a green speed/coverage walk, but static review identifies missing deadline regressions. No reviewer test failure is claimed.
4. Staged scope and attribution: implementation scope PASS; the only reviewer patch is attributable Step 3 metadata and remains unstaged for writer reconciliation.
5. Unresolved findings: FAIL, R1 remains open.
6. a.commit: mechanical PASS, state valid and ready true, no diagnostics; grouping and subjects fit. Reconcile its completed-step prose after the fix.

Disposition: changes-requested. No substantive repair was made. This answer is advisory and does not authorize a commit.

### Final reviewer decision for step 3 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-3-round-1 -->

## Round 2 by requestor - Step 3

- Recorded: 2026-11-18T21:40:37+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: request

### Review identity for step 3 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 3
Review round: 2

### Code review evidence for step 3 git-cliff-provisioning (round 2)

request_index_tree: 78c002416187a2ba1488ea1915eb4099d7b5ed3a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the git-cliff cache and its lock
group 1 path: .gitignore
group 1 path: tools/release_workflow/git_cliff/__init__.py
group 1 path: tools/release_workflow/git_cliff/cache.py
group 1 path: tools/release_workflow/git_cliff/cache_lock.py
group 1 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py
group 2: docs(git-cliff-provisioning): record step 3 validation
group 2 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: .gitignore
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
```

### Validation scope for step 3 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 3 git-cliff-provisioning (round 2)

Writer assessment for Step 3 of the git-cliff-provisioning plan, round 2: the
step is fully implemented after the round 1 repair, and the reconciled
implementation check records `Yes. Step 3 has been fully implemented.` in the
staged validation plan, whose document status stays
`No, it is not implemented.` while Steps 4 to 8 are not started.

Evidence, all on the staged tree:

- R1 repair, red first: with the round 1 `cache_lock.py` restored from the
  index, `ghog single` on `test_git_cliff_cache_lock_tdd.py` (with the new
  support and cases) exit 2: the late wake-up and the liveness queries
  crossing W both failed with `DID NOT RAISE LockWaitError`. With the repaired
  module (restored and hash-verified) the four Step 3 test files pass.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7639 tests: round 1's 7636
  plus the three new lock cases), on index tree
  `78c002416187a2ba1488ea1915eb4099d7b5ed3a`. No budget was changed and no
  exclusion is accepted (`ghog exclude --list`: `exclusions=0`). Check, lint
  and types passed in that walk.
- `rg -n 'getmtime|st_mtime|age' tools/release_workflow/git_cliff/cache_lock.py`:
  no match; the two other `rg` checks are unchanged (`.gitignore` line 124,
  no process start in the support).
- Line counts: `cache_lock.py` 377, `git_cliff_support.py` 327, lock test
  255; every Python file stays below 550.
- Markdown check (whole repository, the transcript included) and cSpell on
  the validation plan: clean. `commit-plan-check`: ready, 12 paths, two
  groups, subjects unchanged.

Architecture, performance and integrity are unchanged from round 1: the
repair adds one clock read per poll inside the existing transition and one
local variable in `acquire`; no new dependency, no new state on disk.

Please check in particular: that no path publishes or replaces a record once
the deadline has passed, counting the mutex entry, the record read and the
liveness queries; that a lock freed at exactly W is still taken; that the
deadline is never reset and the waiting callback stays single; the
`LockWaitError` fields when no live holder was ever seen; and the reconciled
validation plan rows, including the kept architecture correction.

### Implementation report for step 3 git-cliff-provisioning (round 2)

Step 3, "Cache layout, entry record, reuse check and the cache lock", is the
third of eight steps of the git-cliff-provisioning plan. It adds the cache of
the executing checkout, the lock-free reuse check and the provisioning lock of
one version and platform; nothing calls them before Step 5.

Cache, `tools/release_workflow/git_cliff/cache.py` (design "Cache layout and
the local integrity record" and "Reuse check and the use guard"; design
decisions Q03, Q07 and Q12):

- `CachePin` (protocol: `version`, `triple`) and `Guard` (protocol: `path`,
  `handle`, `sha256_and_size()`, `close()`, `retain()`), met by
  `manifest.AdmittedPin` and `windows_guard.UseGuard`.
- `CacheLayout(tooling_root, namespace="production")` (frozen): `root` is
  `<tooling_root>/.tools/git-cliff`, or its `evidence` folder; any other
  namespace raises `ValueError`. `version_dir`, `entry_dir`, `executable`,
  `record`, `lock_path` and `attempt_dir(pin, kind, owner, token)`. A version
  directory name must match `[0-9]+\.[0-9]+\.[0-9]+` and a triple
  `[a-z0-9_]+(-[a-z0-9_]+)+`, otherwise `ValueError` ("not a cache place"),
  so no production pin resolves into `evidence/`. Attempt names are
  `.staging-<pid>-<created>-<token>` and `.retired-...` with a positive PID
  and creation time and a lowercase hexadecimal token; `parse_attempt(name)`
  (static) returns `Attempt(kind, owner, token)` for a canonical name and
  `None` otherwise (leading zeros, suffixes, other kinds).
- `EntryRecord` (frozen, keyword-only, schema 1): `version`, `triple`,
  `asset`, `asset_sha256`, `executable_sha256`, `executable_size`,
  `provisioned`. `__post_init__` refuses another schema, an empty name, a
  digest that is not 64 lowercase hexadecimal characters, a size below 1 and
  a `provisioned` time without an offset. `encode()` writes one JSON line in
  a fixed key order; `decode()` uses `lock_records.decode_object` with the
  `entry` label and requires exactly the eight keys.
- `OwnerFile(owner, children=())` (frozen, schema 1): `with_child`, `encode`,
  `decode` with the `owner file` label and exactly four keys. The shared
  helpers `identity_fields`, `decode_children` (a list of objects holding
  exactly a positive `pid` and `created`) and `local_time` (ISO time with an
  offset) also serve the lock record.
- `check_entry(layout, pin, *, open_guard, probe) -> EntryCheck`, where
  `EntryCheck` is `ValidEntry(guard, record) | UnusableEntry(absent, reason)`:
  1. `open_guard(executable)`; `FileNotFoundError` returns the absent result,
     any other error propagates.
  2. `entry.json` read; missing, undecodable or naming another version or
     triple returns an invalid result, before any hash.
  3. `guard.sha256_and_size()`; a size or digest other than the record's
     returns an invalid result, before the probe.
  4. `probe(guard) -> ChildOutcome`; timed out, a status other than 0 or a
     first line other than `git-cliff <pin>` returns an invalid result.
  Every invalid result closes the guard. An `UnconfirmedEndError` from the
  probe calls `guard.retain()` and propagates; any other exception closes the
  guard and propagates. A valid result keeps the guard open for the caller.

Lock, `tools/release_workflow/git_cliff/cache_lock.py` (design "Provisioning
lock, contention and recovery"; design decisions Q03 and Q04):

- `LockRecord(owner, started, caller, children=())` (frozen, schema 1, six
  keys, non-empty caller, `started` with an offset).
- `LockSeams` (frozen, keyword-only): `clock` and `sleep` required; `probe`
  (`process_state`), `current` (`current_identity`), `mutex`
  (`transition_mutex`) and `now` (local time with offset) default to the
  item 1 primitives.
- `CacheLock(layout, pin, *, caller, seams)`; the first transition creates
  the version directory with its parents and names the mutex
  `Global\llm-shared-git-cliff-<dev>-<ino>-<namespace>-<version>-<triple>`
  from `stat` of `layout.root`.
- `acquire(wait_seconds, on_wait)`: deadline fixed once. Each poll enters the
  mutex and reads the record. A live holder is returned. Absent, or present
  with owner and every child `DEAD` (owner probed first, children only then):
  if the clock is past the deadline nothing is done (round 1 repair below);
  otherwise this caller's record is published (flushed temporary from
  `tempfile.mkstemp` beside it, then `Path.rename`, which Windows never lets
  replace) or replaces the dead one with `Path.replace` in the same
  transition. The first holder gets `on_wait(holder, W)` once; then
  `sleep(min(0.25, remaining))` until the deadline, where
  `LockWaitError(path, last_live_holder, W)` is raised (message: path, PID,
  start time, caller kind, W and `LOCK_WAIT_REMEDY`, the design's lock-wait
  remedy). The temporary is always unlinked. An unverifiable record
  raises `LockRecordError` at once; acquiring a held lock is refused.
- `record_child(identity)`, `release()` and `retain_record()`: each change
  rereads the record under the mutex and requires it to equal the held one;
  `release` unlinks it. After `retain_record()`, `release` returns without
  touching anything and `record_child` and `recover_attempts` raise
  `LockRecordError`.
- `recover_attempts()`: refused unless held; one `os.scandir` of the version
  directory; for each directory (not following links) whose name parses as an
  attempt: probe the name owner; read `owner.json` (missing: no children;
  another read error or an invalid file: keep); require the same owner and
  every child `DEAD`; then `shutil.rmtree`, a refusal keeping the directory.
  Returns the removed names.

Ignore rule: the root `.gitignore` ends with a comment and
`/.tools/git-cliff/` (design "Ignore rule", requirement Q05, plan Q01).

Tests (no process, no native call, no real wait):

- `git_cliff_support.py`: `FakeClock` (monotonic, `now`, `sleep`, scheduled
  actions), `ProcessStates` (undeclared is `UNKNOWN`, queries recorded),
  `UncontendedMutex` (can declare entries abandoned), `LockWorld` (lock built
  on those seams, `hold`, `attempt`, `declare`, `on_wait` recording),
  `synthetic_pin()` from a generated archive with its real size and SHA-256,
  `entry_record`, `install_entry`, `FakeGuard` and `FakeGuardOpener` over
  scenario files, `FakeProbe`, and `deny_writes`.
- `test_git_cliff_cache_tdd.py`: fixed paths, evidence namespace, refused
  names and namespace, attempt names both ways, the `.gitignore` line, entry
  record round trip and thirteen invalid records, owner file round trip and
  refusals, and every reuse outcome in order, including the valid reuse under
  `deny_writes` and the retained guard on an unconfirmed probe end.
- `test_git_cliff_cache_pbt.py`: attempt names and entry records round-trip.
- `test_git_cliff_cache_lock_tdd.py`: publication and key order, mutex names
  in both namespaces, a live holder until W (4 sleeps of 0.25 s, 5 polls, one
  callback, exact message), release mid-wait, a holder change, child
  recording, release and a replaced record, retention, refused double
  acquisition and retention, the caller kind, the default seams and eleven
  unverifiable records.
- `test_git_cliff_cache_lock_recovery_tdd.py`: dead owner and children
  recovered in one transition; a live or `UNKNOWN` child, an `UNKNOWN` owner
  and an abandoned mutex keep the record; eight attempt verdicts for both
  kinds; non-attempt entries and an unreadable owner file kept; recovery
  refused without the lock; a refused removal kept.

Code review round 1 repair (R1, wait deadline at publication):

- `CacheLock._poll(deadline) -> tuple[LockRecord | None, bool]`: inside the
  mutex it reads the record and probes the actors as before; a live holder
  returns `(holder, False)`. Otherwise it reads `seams.clock()` and, when the
  time is past the deadline, returns `(None, False)` without publishing its
  record and without replacing a dead one. Only then does it publish and
  return `(None, True)`. Entering the mutex, reading the record and every
  liveness query thus count against W.
- `acquire` keeps `last`, the last live holder seen: the first one gets the
  single `on_wait` callback; after a poll that did not acquire, the remaining
  time is computed and `LockWaitError(path, last, W)` is raised once it is not
  positive. The deadline is still fixed once. A poll at exactly W may still
  publish (`clock() > deadline` refuses only a later time).
- `LockWaitError(path, holder | None, wait)`: names the last live holder's
  PID, start time and caller kind; with no live holder ever seen (proving a
  dead holder itself ran past W), the message says `not acquired before its
  deadline` and `owner` and `started` are `None`. The remedy text is
  unchanged.
- Test support: `FakeClock.oversleep` adds a fixed late wake-up to every
  sleep; `LockWorld.query_seconds` makes each liveness query take fake time.
- New lock cases: a lock freed at exactly W is taken by the last poll (4
  sleeps, record stamped one second later); a waiter oversleeping 0.1 s per
  sleep wakes at 1.05 s after the holder released at 1.0 s and fails naming
  that holder, with no record and no temporary left; two liveness queries of
  0.6 s proving a dead holder and child cross W at the first poll, so the
  dead record stays byte-identical, no callback, no sleep, no holder named.
  The last two failed (`DID NOT RAISE LockWaitError`) on the round 1 module.
- Validation plan: Step 3 back to Yes with the repair and its evidence; the
  reviewer's correction that only `EntryRecord` validates its values when
  built is kept, and the records bullet no longer says otherwise.

Documentation: the validation plan entry and the `git_cliff/__init__.py`
docstring described in the change summary.

Writer notes: `.reviews/a.git-cliff-provisioning.step3.journal.md` and
`.reviews/a.git-cliff-provisioning.step3.handoff.md`.

### Change summary for step 3 git-cliff-provisioning (round 2)

Staged paths (12), grouped in the root `a.commit` (two groups, checker
`ready: true`):

1. `feat(release): add the git-cliff cache and its lock`:
   `.gitignore`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/cache_lock.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_pbt.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache_lock/test_git_cliff_cache_lock_recovery_tdd.py`.
   The ignore rule travels with the first code that writes under the cache
   path (design "Ignore rule", plan decision Q01).
2. `docs(git-cliff-provisioning): record step 3 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Membership, order and subjects are unchanged since round 1; the bodies now
mention the deadline repair (group 1) and the round 1 repair record
(group 2). Changed since round 1: `cache_lock.py`, `git_cliff_support.py`,
`test_git_cliff_cache_lock_tdd.py` and the validation plan.

Steps 1 and 2 of this plan are committed and pushed (`644f0041` is the base
of this review). The review transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md`, holding rounds
1 and 2, stays unstaged for the residual commit.

### Writer response for step 3 git-cliff-provisioning (round 2)

Writer response:

Writer response to round 1:

- R1 (P2), accepted and repaired: the deadline is now enforced at
  publication. `_poll` receives the fixed deadline and reads the clock inside
  the mutex after entering it, reading the record and probing the actors;
  past the deadline it publishes nothing and replaces no dead record, and
  `acquire` raises `LockWaitError` with the last live holder seen. The
  original deadline and the single waiting callback are kept, and a lock
  freed at exactly W is still taken. The requested regressions exist: a late
  wake-up (fake clock oversleep) finding the lock freed after W, and liveness
  queries that advance fake time past W while a dead record is proven; both
  failed on the round 1 module and assert no new record, no replacement, one
  or no callback and the unchanged deadline.
- On the suggested extra expiry check before starting another poll: not
  added. After a sleep the next poll only reads the record under the mutex,
  and the check inside the mutex already refuses publication and recovery
  past W; a poll after W that still finds a live holder refreshes the holder
  named by the error. No other path publishes.
- Validation plan: the attributable round 1 edit is reconciled. The step is
  back to `Yes` with the repair and its evidence, the missing-work list is
  removed, the performance and coverage verdicts reflect the repair, and the
  reviewer's architecture correction (only `EntryRecord` validates its values
  when built; `OwnerFile` and `LockRecord` rely on typed inputs and strict
  decoding) is kept, with the implementation record's records bullet aligned.
- `a.commit`: membership, order and subjects unchanged; the two bodies now
  describe the deadline repair.

No disagreement.

### Reviewer focus for step 3 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-3-round-2 -->

## Round 2 by reviewer - Step 3

- Recorded: 2026-11-18T21:45:50+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: answer

### Assessed index identity for step 3 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 78c002416187a2ba1488ea1915eb4099d7b5ed3a

Assessed index tree: 78c002416187a2ba1488ea1915eb4099d7b5ed3a

### Implementation check for step 3 git-cliff-provisioning (exchange 1) (round 2)

Result:

Yes. Step 3 has been fully implemented.

R1 is resolved. The staged tree 78c002416187a2ba1488ea1915eb4099d7b5ed3a checks the original deadline inside the mutex after reading the record and probing all required identities. A late wake-up cannot authorize acquisition; slow DEAD probes cannot authorize replacement after W. The last live holder is retained for diagnostics, no-live-holder expiry has optional owner/start fields, and on_wait remains single. Acquisition at exactly W and before W remains covered.

Reviewed the exact Step 3 plan, staged changes, the round-to-round code and test diff, validation rows and a.commit. Cache layout, strict persisted records, ordered guard/record/hash/probe reuse, guard retention, ownership and DEAD-only recovery remain consistent with the plan. No architecture, complexity, line-budget or feature-integrity issue found. No implementation repair was made.

Static unit-test assessment: the three new cases exercise exactly-W release, oversleep with release and slow liveness queries with a dead child. They assert record preservation or absence and callback/diagnostic behavior. Existing tests cover holder changes, pre-W success, ownership and conservative recovery. Mutex entry precedes the same deadline check; there is no separate delayed-mutex regression. Coverage scope is tools, with tests and initializers omitted; no unit-test gap identified and no unreferenced top-level support symbol found. No reviewer test or coverage run.

Validation plan effects:

Only the exact Step 3 validation rows were amended: recorded independent round 2 agreement, R1 closure and the writer-reported 7639-test result on the assessed tree. The exact Yes sentence remains; no missing-work list remains. Other steps, document-level status and umbrella are unchanged. This is polishing-only review metadata, not a substantive repair. Attribution succeeded. The launcher returns an attributable patch without staging it, so this metadata remains unstaged for requestor reconciliation; no direct index mutation was substituted.

### Pre-repair mandatory checks and coverage for step 3 git-cliff-provisioning (exchange 1) (round 2)

Before assessment, captured the index, ordered validation state for all 12 staged paths, validation-plan baseline blob and umbrella digest; wrote the retained manifest. The index matched the request exactly: 78c002416187a2ba1488ea1915eb4099d7b5ed3a. No literal Human guidance block authorizes implementation repair.

### Resolved validation set and sources for step 3 git-cliff-provisioning (exchange 1) (round 2)

Request and current resolver contract agree: ghog day --full=speed --whole-suite, source project, with no additive plan/request commands. Sampled .review-validation at assessment time: absent. The built-in speed default is completed with the bound whole-suite selector. Scope fingerprint: 686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6; proof speed. Writer reports exit 0, 7639 tests, cov=100, outliers=0, excluded=0 on the exact request tree, plus red-first regression evidence. These are writer results, not reviewer executions.

### Resolver drift and direction for step 3 git-cliff-provisioning (exchange 1) (round 2)

None. Static comparison of the current loader, default-completion and resolver contract with the request found identical commands and sources. No validation walk was repeated.

### Repository state around validation for step 3 git-cliff-provisioning (exchange 1) (round 2)

Before/after index trees match 78c002416187a2ba1488ea1915eb4099d7b5ed3a. The validation comparator reports acceptable=false solely for the permitted Step 3 validation-plan metadata amendment; no implementation, test, ignored or untracked validation side effect occurred. The umbrella remains unchanged at 20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c. Attribution is true. The pre-existing unstaged transcript remains core-owned.

### Repair inventory for step 3 git-cliff-provisioning (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 3 git-cliff-provisioning (exchange 1) (round 2)

Independent commit-plan-check.bat --format json returned exit 0, state valid, ready true, no diagnostics. Every staged path appears exactly once in two dependency-ordered groups: (1) feat(release): add the git-cliff cache and its lock, 11 paths; (2) docs(git-cliff-provisioning): record step 3 validation, one path. Reviewed a.commit: membership, order, scopes, conventional subjects and updated bodies fit the delivered Step 3 work. No change made to a.commit. The attributable metadata update remains within the existing documentation group.

### Findings and boundaries for step 3 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 3 git-cliff-provisioning (exchange 1) (round 2)

Reconcile and stage the attributable Step 3 validation metadata through the requestor workflow. Present the registered human convergence choice; this recommendation does not authorize a commit. The requestor owns final staging, transcript handling and any authorized commit.

### Decision rationale for step 3 git-cliff-provisioning (exchange 1) (round 2)

Recommend commit-ready. R1 is closed and no new blocking finding remains. No substantive repair was made in this round.

Readiness floor:

1. Identity: pass; exact plan, Step 3, round 2, occurrence 1, umbrella, host identities and request index agree.
2. Completeness: pass; Step 3 and R1 rework match the plan.
3. Validation and coverage: pass; exact-tree writer speed evidence and static coverage assessment show no gap; no reviewer execution was needed.
4. Attribution and staged scope: pass; assessed implementation stays unchanged; only attributable, permitted Step 3 review metadata remains unstaged and is explicitly disclosed.
5. Findings: pass; R1 resolved, none unresolved or crossing the step boundary.
6. Commit plan: pass; independently valid, ready, accurately grouped.

The recommendation is advisory. Commit authorization belongs to the human convergence gate.

### Final reviewer decision for step 3 git-cliff-provisioning (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-3-round-2 -->

## Round 2 by human - Step 3 - human-confirmation

- Recorded: 2026-11-18T22:03:32+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 3
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 4

- Recorded: 2026-11-19T00:36:45+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 4
- Outcome: request

### Review identity for step 4 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 4
Review round: 1

### Code review evidence for step 4 git-cliff-provisioning (round 1)

request_index_tree: ad2afb2d6d3ae846f798808026913665bfcc5307
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): extract the git-cliff archive member
group 1 path: tools/release_workflow/git_cliff/archive.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_archive/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_pbt.py
group 2: feat(release): download git-cliff in a worker
group 2 path: tools/release_workflow/git_cliff/network.py
group 2 path: tools/release_workflow/git_cliff/download_worker.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: tools/release_workflow/git_cliff/__init__.py
group 2 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_network/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3: test(release): record step 4 native checks
group 3 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 3 path: tests/unit/tools/release_workflow/git_cliff_native_probes.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4: docs(git-cliff-provisioning): record step 4 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 4 path: .vscode/settings.json
staged path: .vscode/settings.json
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_probes.py
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/archive.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/network.py
```

### Validation scope for step 4 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 4 git-cliff-provisioning (round 1)

Writer assessment for Step 4 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and its implementation check records
`Yes. Step 4 has been fully implemented.` in the staged validation plan,
whose document status stays `No, it is not implemented.` while Steps 5 to 8
are not started.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the four new test files and the bootstrap
  test failed at collection on the missing `network`, `download_worker` and
  `archive` modules (exit 4); the bootstrap test alone then failed its five
  worker-kind cases (exit 2). With the modules and the entry kind they pass,
  with `test_codepage_tdd.py` and the evidence test.
- By hand, the real worker started through the bootstrap against a closed
  loopback port printed one `retryable` JSON line and exited 75.
- Native record: the recorder with `--milestone step-4`, after the last
  source change, passed 9 of 9 checks (0.50 s to 1.23 s; the worker check
  10.57 s for its 10 s deadline) and the stalled-runner timeout (3.08 s);
  the validator accepts `native_checks.v1.json` for the current sources.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after two walks that failed: the first at check (typing of the canned
  handler and test helpers, `PLR0911` in `bootstrap.main`, radon C on the
  worker's argument parser, `RUF043`), the second only on the record's
  digests, stale after those edits, before the recorder rerun.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7719 tests, slowest call
  0.83 s, outside this step), on index tree
  `ad2afb2d6d3ae846f798808026913665bfcc5307`. No budget was changed and no
  exclusion is accepted (`ghog exclude --list`: `exclusions=0`). The archive
  property test was trimmed to 10 examples after a default-level walk
  measured 0.203 s of lifecycle CPU (inside the band, over the 0.100 s
  ceiling); it is no longer reported.
- `rg -n 'CERT_NONE|check_hostname|_create_unverified_context|Retry-After'
  tools/release_workflow/git_cliff`, `rg -n 'extractall|extract\('
  tools/release_workflow/git_cliff/archive.py` and `rg -n 'api.github.com'`
  on `network.py` and `download_worker.py`: no match.
- Line counts: `network.py` 120, `download_worker.py` 155, `archive.py` 100,
  `bootstrap.py` 227, `git_cliff_support.py` 401, recorder 278 (598 before
  the split), probes 470; every Python file stays below 550.
- Markdown check and cSpell on the validation plan: clean, after the user
  added `getinfo` to the project dictionary.

Architecture: `network` is the only module touching `urllib`, `ssl` and
`http.client`; `download_worker` depends only on it; the bootstrap reaches
the worker only after its readiness gate, and its tables keep the worker's
internal statuses apart from the public ones (plan decision Q15). `archive`
depends on `cache.EXECUTABLE` and a pin protocol, not the manifest.
Performance: streaming, hashing and extraction are linear in bytes with at
most one extra byte read; metadata is one bounded read. Feature integrity:
the release kinds keep their gate, dispatcher and statuses, and the
cross-site status contract still holds.

Please check in particular: that no path disables certificate verification
or reads a response header; the size cap (at most one extra byte read,
nothing beyond the size written) and that an HTTP error creates no file;
the retry classification, including certificate, TLS, protocol and local
errors; the worker's argument contract, its single outcome line and the
`min(30, remaining)` socket timeout; the bootstrap's worker branch and the
unchanged release statuses; the extraction's refusal of a wrong directory
size in both directions; and the recorder split and the worker deadline
check, including its proxy bypass and its observations.

### Implementation report for step 4 git-cliff-provisioning (round 1)

Step 4, "Network client, download worker, verification and extraction", is
the fourth of eight steps of the git-cliff-provisioning plan. It adds the
download path the Step 5 service will call; nothing calls it yet.

Network client, `tools/release_workflow/git_cliff/network.py` (design
"Network path", "Archive verification", "Time budgets and retries"; design
decisions Q06 and Q08):

- `build_opener(*, proxies=None, context=None)`: `ProxyHandler` with
  `urllib.request.getproxies()` or the declared proxies, `HTTPSHandler` with
  `ssl.create_default_context()` or the declared context; nothing changes
  `verify_mode` or `check_hostname`. The default redirect handler follows
  the 302 to `release-assets.githubusercontent.com`.
- `stream_archive(opener, url, target, *, expected_size, socket_timeout) ->
  Received(size, sha256)`: `opener.open(url, timeout=socket_timeout)`, then
  the target opened `wb` (so an HTTP error creates no file); chunks of
  `min(64 KiB, expected_size - size + 1)`; a chunk that would pass the size
  raises `SizeOverflowError` before it is written. A short body is returned.
- `fetch_metadata(opener, url, *, socket_timeout) -> bytes`: one read of at
  most `METADATA_LIMIT + 1` (4 MiB plus one) bytes; more is a size overflow.
- `classify(error)`: `HTTPError` 429 or 500 to 599 retryable, any other
  `HTTPError` fatal; a `URLError` whose reason is
  `ssl.SSLCertVerificationError`, or that error itself, fatal; any other
  `URLError`, `ConnectionError`, `TimeoutError`, `ssl.SSLError` or
  `http.client.HTTPException` retryable; everything else (size overflow,
  local `OSError` such as a denied write, `ValueError`) fatal.

Worker, `tools/release_workflow/git_cliff/download_worker.py` (design
"Deadline enforcement"; plan decisions Q10 and Q15):

- `WorkerRequest` (frozen, keyword-only): `mode` (`archive` or
  `metadata`), `url` (HTTPS only), `target` and `expected_size` (both for an
  archive, neither for metadata; size at least 1), `remaining` (finite,
  positive).
- `worker_arguments(request)` writes `--mode`, `--url`, optional `--target`
  and `--expected-size`, then `--remaining` with `repr(float)`;
  `parse_request(arguments)` reads exactly that form (pairs only, each known
  option once, the three required present, the size ASCII digits).
- `worker_command(runtime, tooling_root, request)` returns `(runtime, ["-I",
  "-X", "utf8", "<tooling_root>/tools/release_workflow/bootstrap.py",
  "--entry-kind", "git-cliff-worker", "--", *arguments])`.
- `main(arguments, *, opener=None) -> int`: invalid arguments give
  `{"outcome": "fatal", "error": "invalid worker arguments: ..."}` and 65;
  otherwise the socket timeout is `min(30, remaining)`, the archive outcome
  is `{"outcome": "ok", "size", "sha256"}` and the metadata outcome
  `{"outcome": "ok", "metadata": <UTF-8 text>}`; any exception of the
  attempt becomes `{"outcome": classify(error), "error": "<type>: <text>"}`.
  Exactly one JSON line goes to stdout, nothing to stderr; the status is
  `STATUSES[outcome]` (0, 75, 65).

Bootstrap, `tools/release_workflow/bootstrap.py` (plan decision Q15):

- Module-level `_ENGINES` (three release kinds to `tools.release_workflow.cli`,
  `git-cliff-worker` to the worker module) and `_UNNORMALIZED_KINDS`
  (`git-cliff-worker`). `entry` accepts the kinds of `_ENGINES`. `main`
  imports `_ENGINES[kind]` after the unchanged readiness gate; for an
  unnormalized kind it returns `Worker.main(arguments)` unchanged, otherwise
  it calls the engine as before and returns `status if status in {0, 1, 2,
  3} else _normalized(status)` (diagnostic, 1). `main` still holds exactly
  one set literal, which `test_codepage_tdd.py` evaluates.

Archive, `tools/release_workflow/git_cliff/archive.py` (design "Archive
verification" and "Single-member extraction"; plan decision Q10):

- `verify_archive(path, pin)`: size, then SHA-256, of the staged file, in
  1 MiB reads; `VerificationError` names which differs.
- `extract_member(path, pin, target_dir) -> (sha256, size)`:
  `ZipFile(path).getinfo(pin.member)`, `archive.open(info)` copied to
  `target_dir / "git-cliff.exe"` opened `xb`, hashed; `KeyError` (missing
  member), `BadZipFile` (not an archive, CRC), `EOFError` and `zlib.error`
  become `ExtractionError`, and so does a written size other than
  `info.file_size`. No other member is read; no member name becomes a path.

Native evidence:

- The recorder `git_cliff_native_checks.py` (598 lines, in the 550 to 650
  band) was split as the Step 2 validation recorded: the kernel helpers,
  check bodies and helper parents moved unchanged to the new
  `git_cliff_native_probes.py` (outside the plan's file list); the recorder
  keeps the catalog, the runner, the record and the command line, and
  dispatches `--helper` to the probes module. Every check's sources now list
  the probes module.
- New `worker-ends-at-deadline` (milestone `step-4`, bound 60 s): a
  temporary tooling root with a `.staging-<recorder pid>-<created>-<token>`
  directory and its `owner.json`; a loopback TCP listener that accepts one
  connection and never answers; the real worker started with
  `worker_command(sys.executable, repository root, archive request to
  <https://127.0.0.1>:<port>/git-cliff.zip)` through `run_contained` with
  `NO_PROXY=127.0.0.1` in its environment, a 10 s deadline and a recording
  callback adding the child to `owner.json`. Observation: timed out, the
  endpoint saw the connection, the owner file lists exactly the outcome's
  identity, the worker is `DEAD` afterwards, and its stdout is empty.
  Sources: the Step 2 set, the probes module, `bootstrap.py`,
  `download_worker.py`, `network.py` and `cache.py`.
- `native_checks.v1.json`: milestone `step-4`, commit `d55d6b94` (the base;
  the uncommitted sources bind through their digests), 9 passed checks
  (0.50 s to 1.23 s; the worker check 10.57 s) and the stalled-runner
  timeout (3.08 s).
- `test_git_cliff_native_evidence_tdd.py`: milestones `step-2` and `step-4`,
  the worker check in the catalog with its sources, digests over the union of
  sources, the committed record at `step-4`, and a `step-4` record without
  the worker check refused.

Tests:

- `git_cliff_support.py`: `Canned` (status and body, redirect location,
  stalled read) and `CannedWeb` (answers by URL or an exception, an opener of
  `ProxyHandler({})`, a certificate-free `HTTPSHandler` and a `BaseHandler`
  with `handler_order` 100 that answers first, recording `(url, timeout)` and
  every read size).
- `test_git_cliff_network_tdd.py`, `test_git_cliff_download_worker_tdd.py`,
  `test_git_cliff_archive_tdd.py`, `test_git_cliff_archive_pbt.py` and the
  bootstrap additions cover the plan's test list.

Documentation: the validation plan entry, the `git_cliff/__init__.py`
docstring and the cSpell word `getinfo` in `.vscode/settings.json`, which the
user approved.

Writer notes: `.reviews/a.git-cliff-provisioning.step4.journal.md` and
`.reviews/a.git-cliff-provisioning.step4.handoff.md`.

### Change summary for step 4 git-cliff-provisioning (round 1)

Staged paths (20), grouped in the root `a.commit` (four groups, checker
`ready: true`):

1. `feat(release): extract the git-cliff archive member`:
   `tools/release_workflow/git_cliff/archive.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_archive/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_pbt.py`.
2. `feat(release): download git-cliff in a worker`:
   `tools/release_workflow/git_cliff/network.py`,
   `tools/release_workflow/git_cliff/download_worker.py`,
   `tools/release_workflow/bootstrap.py`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_download_worker/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`.
3. `test(release): record step 4 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_probes.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
4. `docs(git-cliff-provisioning): record step 4 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`,
   `.vscode/settings.json` (cSpell word `getinfo`).

Steps 1 to 3 of this plan are committed and pushed (`d55d6b94` is the base
of this review). This round's transcript entry is appended to
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and stays
unstaged for the residual commit.

### Writer response for step 4 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 4 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- The native check recorder was split before the Step 4 check was added:
  the Step 2 validation recorded that the 598-line recorder would meet the
  split guidance in Step 4. The new `git_cliff_native_probes.py` is outside
  the plan's file list; the code moved unchanged, apart from names made
  public for the cross-module use and the new check.
- The worker check uses an HTTPS URL to a loopback listener that accepts and
  never answers, so the worker stalls in the TLS handshake under its 30 s
  socket timeout while the 10 s deadline ends it. Its environment sets
  `NO_PROXY=127.0.0.1` (other variables inherited), so a proxy declared by
  the environment cannot answer in its place.
- `classify`: a certificate verification failure is fatal (a retry from the
  same source would not change it); other TLS errors and `http.client`
  protocol errors are retryable, as connection-level failures; a local
  `OSError` such as a denied write into staging is fatal, not a connection
  error.
- `fetch_metadata` caps the body at 4 MiB (`METADATA_LIMIT`), which the
  design does not size; the GitHub release metadata of a tag is far smaller.
- The worker accepts HTTPS URLs only, takes an injectable `opener` in
  `main`, and reports every failure of its attempt as an outcome line rather
  than raising, so the parent always reads one line or sees a non-internal
  status (a bootstrap readiness or crash status).
- `stream_archive` opens the target with `wb` only after the response
  arrived, so an HTTP error creates no file and a second attempt overwrites
  the first's partial file.
- One test-environment adjustment: the in-memory scenario filesystem raises
  `ValueError` on a seek before the start of a file, where a real file
  raises `OSError`, which `zipfile` handles; the not-a-ZIP test content is
  therefore longer than the 22-byte end record.

### Reviewer focus for step 4 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-4-round-1 -->

## Round 1 by human - Step 4 - escalation

- Recorded: 2026-11-19T11:30:04+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: escalation

exchange was abandoned while waiting for reviewer

<!-- review-entry-id: escalation-round-1 -->

## Round 1 by human - Step 4 - human-reclaim

- Recorded: 2026-11-19T19:03:48+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: human-reclaim

Human decision to resume code review round 1 for step 4 in place.

The recorded escalation was a stopped handoff rather than a failure. The
requestor published round 1 for implementation step 4 and entered its bounded
wait. No reviewer session was active while that wait ran, so the exchange
reached its timeout with the answer still absent, and the protocol escalated it
with the reason that the exchange was abandoned while waiting for the reviewer.

No review work was lost and no artifact was damaged. At this decision the
request is present at 22399 bytes, the answer is absent because no reviewer
answer was ever published, and the staged index tree still matches the round 1
`request_index_tree`. The round 1 request and its immutable evidence remain
authoritative, and the artifact shape names the reviewer as the actor to
resume.

The human chose to reclaim the same request rather than archive it and publish
a fresh round. The requestor waits again for the round 1 answer once the
reviewer session is running.

<!-- review-entry-id: human-reclaim-round-1 -->

## Round 1 by reviewer - Step 4

- Recorded: 2026-11-19T08:33:55+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: answer

### Assessed index identity for step 4 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: ad2afb2d6d3ae846f798808026913665bfcc5307

Assessed index tree: ad2afb2d6d3ae846f798808026913665bfcc5307

### Implementation check for step 4 git-cliff-provisioning (exchange 1) (round 1)

Result:

Yes. Step 4 has been fully implemented.

The staged archive, network and worker modules satisfy the Step 4 plan: verified archive size and SHA-256 before extraction, exact member selection to a fixed exclusive output, ZIP error and size checks, proxy-aware TLS-verified urllib access, bounded reads, required retry classification, strict worker arguments, one JSON result and worker statuses 0/75/65. Bootstrap dispatch preserves these worker statuses after readiness while keeping the release entry kinds' public status normalization.

The tests exercise these contracts with in-memory HTTP routing and ZIP fixtures. The native evidence includes the real worker's deadline termination and owner identity, plus all eight existing checks. The recorder split preserves catalog dispatch and the bounded runner; the refreshed evidence binds both recorder modules. The Step 5 integration is correctly deferred. No missing implementation, architecture, performance or feature-integrity issue was found.

Validation plan effects:

Updated only the Step 4 coverage paragraph in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md` to record the writer's full-speed evidence and the independent static assessment. The exact Yes result is retained. No other step or umbrella row was edited.

The patch is attributable to the recorded pre-edit blob `b0ac14f43c52167dc98bb17ba7744bdfca37800a`. It remains unstaged review metadata; the index is unchanged. There were no implementation or test repairs.

### Pre-repair mandatory checks and coverage for step 4 git-cliff-provisioning (exchange 1) (round 1)

Writer evidence for request index `ad2afb2d6d3ae846f798808026913665bfcc5307`: 7,719 passing tests, `cov=100 outliers=0 excluded=0 proof=speed`, from `ghog day --full=speed --whole-suite`. The native record reports nine passing checks, including worker deadline termination (10.571 s), and the stalled-recorder timeout demonstration (3.084 s).

The reviewer assessed production coverage statically against the tests and found no gap. The configured gate measures production `tools` with its configured omissions; no measured coverage claim is made for test helpers or native recorder modules. No reviewer test, native check or coverage measurement was run.

### Resolved validation set and sources for step 4 git-cliff-provisioning (exchange 1) (round 1)

The request and current resolver agree on `ghog day --full=speed --whole-suite`, source `project`. Bound scope: whole; proof: speed; fingerprint `686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6`. The `.review-validation` marker was sampled and is absent; there are no extra request commands. The requestor owns execution of this set.

### Resolver drift and direction for step 4 git-cliff-provisioning (exchange 1) (round 1)

None. The command, source and whole-suite selector agree with the current resolver.

### Repository state around validation for step 4 git-cliff-provisioning (exchange 1) (round 1)

Request, baseline and assessed index trees are all `ad2afb2d6d3ae846f798808026913665bfcc5307`. The umbrella digest remains `20d33b54a61c645055c81982c205f05156767827d0233567b218b7504fe0661c`.

The ordered validation-state comparison reports only the validation plan as changed (`acceptable: false` for that tracked path). This is the intentional Step 4 review-metadata edit, independently attributed to its recorded blob, not a validation command side effect; no validation command ran. No other tracked, untracked or ignored validation path changed. The pre-existing unstaged review transcript was left untouched. No writer work was staged or reverted.

### Repair inventory for step 4 git-cliff-provisioning (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 4 git-cliff-provisioning (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json`: exit 0, `state: valid`, `ready: true`, no diagnostics. All 20 received staged paths appear exactly once. Ordered groups:

1. `feat(release): extract the git-cliff archive member` (4 paths).
2. `feat(release): download git-cliff in a worker` (10 paths).
3. `test(release): record step 4 native checks` (4 paths).
4. `docs(git-cliff-provisioning): record step 4 validation` (2 paths).

Grouping, dependency order and subjects accurately describe the received scope. The native probe split is justified by the recorder's size and retains its responsibility boundary; the disclosed spelling-setting change belongs with documentation. No `a.commit` amendment was necessary. The complete ordered groups and staged-path inventory are retained in the evidence manifest.

### Findings and boundaries for step 4 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 4 git-cliff-provisioning (exchange 1) (round 1)

No implementation rework is requested. Reconcile the attributable, unstaged Step 4 validation-note update through the owning workflow before committing. The commit decision remains with the human; this assessment neither authorizes nor performs a commit.

### Decision rationale for step 4 git-cliff-provisioning (exchange 1) (round 1)

All six readiness results pass: exact identity and index, complete Step 4 implementation, writer validation plus static coverage assessment, attributable staged scope, no unresolved current or carried findings, and mechanically valid and accurately grouped `a.commit`. No substantive repair was made. Recommend `commit-ready` as an advisory assessment.

### Final reviewer decision for step 4 git-cliff-provisioning (exchange 1) (round 1)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-4-round-1 -->

## Round 1 by human - Step 4 - human-confirmation

- Recorded: 2026-11-19T20:05:54+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 4
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-1 -->

## Round 1 by requestor - Step 5

- Recorded: 2026-11-20T11:26:51+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 5
- Outcome: request

### Review identity for step 5 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 5
Review round: 1

### Code review evidence for step 5 git-cliff-provisioning (round 1)

request_index_tree: da1a91ca73e4f9d40e69e7af64b39fdfa55236cb
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the git-cliff failure contract
group 1 path: tools/release_workflow/git_cliff/messages.py
group 1 path: tools/release_workflow/git_cliff/budget.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
group 2: feat(release): start git-cliff through one object
group 2 path: tools/release_workflow/git_cliff/invocation.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
group 3: feat(release): provision git-cliff under its lock
group 3 path: tools/release_workflow/git_cliff/cache.py
group 3 path: tools/release_workflow/git_cliff/installation.py
group 3 path: tools/release_workflow/git_cliff/provisioning.py
group 3 path: tools/release_workflow/git_cliff/__init__.py
group 3 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
group 4: test(release): record step 5 native checks
group 4 path: tests/unit/tools/release_workflow/git_cliff_native_service.py
group 4 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 5: docs(git-cliff-provisioning): record step 5 validation
group 5 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_service.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/budget.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/invocation.py
staged path: tools/release_workflow/git_cliff/messages.py
staged path: tools/release_workflow/git_cliff/provisioning.py
```

### Validation scope for step 5 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 5 git-cliff-provisioning (round 1)

Writer assessment for Step 5 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and its implementation check records
`Yes. Step 5 has been fully implemented.` in the staged validation plan,
whose document status stays `No, it is not implemented.` while Steps 6 to 8
are not started.

Evidence, all on the staged tree:

- Tests first: `ghog single` on the four new test leaves and the budget test
  failed at collection on the missing `provisioning`, `messages`,
  `invocation` and `installation` modules (exit 4, 7 errors). With the
  modules, the new leaves, the budget test and the cache test pass (220
  tests); two later additions (a refused recovery listing, a never-ending
  staging probe in the installation leaf) pass too.
- Native record: the recorder with `--milestone step-5`, after the last
  covered source change, passed 14 of 14 checks (the five service checks
  3.0 s to 4.8 s) and the stalled-runner timeout (3.07 s); the validator
  accepts `native_checks.v1.json` for the current sources.
- `ghog day --whole-suite`, the command printed by `pw scope day`, exit 0
  after two walks that failed: the first at check (exception messages, a
  single-item membership test, an untyped outcome payload, typed
  expectations, a context manager's return type, a grade C test now split),
  the second only on the record, still `step-4` before the recorder run.
- Review validation, `ghog day --full=speed --whole-suite` (the built-in
  default; no `.review-validation`): exit 0 with
  `cov=100 outliers=0 excluded=0 proof=speed` (7852 tests, slowest call
  0.77 s, outside this step), on index tree
  `da1a91ca73e4f9d40e69e7af64b39fdfa55236cb`. Two earlier speed walks
  failed: one at check (`ANN401` on a test helper, fixed), one at full on two
  lifecycle CPU overruns outside this step
  (`tests/unit/tools/shared_lifecycle/test_audit_declarations/test_audit_declarations_tdd.py`,
  0.141 s and 0.156 s in the full suite); `ghog single` on that file passed
  with both at 0.031 s, and the printed rerun accepted them inside the band.
  No budget was changed and no exclusion is accepted.
- `rg -n 'sys\.stdout|print\(' tools/release_workflow/git_cliff`: only the
  worker's outcome line. `rg -n 'GIT_CLIFF_' tools/release_workflow/git_cliff`:
  the removal rule only in `invocation.py`; `budget.py` matches the override's
  own name.
- Line counts: `messages.py` 144, `invocation.py` 158, `installation.py` 330,
  `provisioning.py` 289, `git_cliff_children_fake.py` 453,
  `git_cliff_native_service.py` 343, recorder 316; every Python file stays
  below 550.
- Markdown check and cSpell on the validation plan: clean.

Architecture: the service reaches the Windows layer, time, standard error
and the worker runtime only through `ProvisioningSeams`, bound in
`production_seams`; `installation` depends on its `InstallSeams` protocol,
not on `provisioning`; only `invocation` builds git-cliff child requests and
holds the `GIT_CLIFF_*` rule; every failure leaves as `ProvisioningError`,
mapped once at the service boundary. Performance: reuse is one guard, one
record, one hash and one probe; provisioning is at most two attempts, one
probe and one listing of the version directory. Feature integrity: no
existing command imports the new modules; `BudgetSettingError` keeps its
message and status.

Please check in particular: the flow order and the error mapping of
`provision` (platform, reuse, lock, recheck, recovery, install, release,
guard, ready line); the guard lifetime in `GitCliffInvocation` (closed after
the child, at once without a child, retained on an unconfirmed end) and the
passthrough refusal of captured output; the retry decision inside D and its
time-left checks; `retire_entry` from each state; the staging removal and
`retain_record()` split between ended and unconfirmed children; the fake's
parent-death model (snapshot then restore) and whether the lifecycle cases
prove what the design rows claim; and the native service checks, including
the job-handle duplicate that keeps a child alive after its caller was
killed.

### Implementation report for step 5 git-cliff-provisioning (round 1)

Step 5, "Provisioning service, invocation object and failure contract", is
the fifth of eight steps of the git-cliff-provisioning plan. It composes the
Step 1 to 4 primitives into the design's target flow; no engine operation
calls it before item 4, and no pin is admitted before Step 7.

Failure contract, `tools/release_workflow/git_cliff/messages.py` (design
"Messages, statuses and the failure contract"):

- `Stage` (eleven stages) and the read-only `REMEDIES`; the lock-wait remedy
  is `cache_lock.LOCK_WAIT_REMEDY`.
- `ProvisioningError(ValueError)`: `exit_code = 2`, `stage`, `version` (None
  before any pin exists), `path`, `detail`; its text is `diagnostic()`,
  `git-cliff <pin> unavailable at <path> (<stage> stage): <detail>. <remedy>`.
- `permission_failure(version, error, fallback)`: the permission stage naming
  the nearest existing directory above the refused path.
- `downloading_line`, `ready_line`, `waiting_line` (holder PID, its start as
  local time with offset, the caller's own W).
- `budget.BudgetSettingError` keeps the refused text as `value`.

Invocation object, `tools/release_workflow/git_cliff/invocation.py` (design
"The provisioning entry point for items 4 and 5", "Version probe"; design
decision Q09):

- `engine_environment(environment=None)`: the given or process environment
  without any `GIT_CLIFF_*` name in any case, the only place of that rule.
- `probe_request(executable, *, inherited, deadline, record=None)`:
  `--version` in the executable's directory under the engine policy.
- `GitCliffInvocation(executable, version, guard, *, launch)`, single-use:
  `run(arguments, *, policy, cwd, environment=None, output="capture",
  deadline=None)` builds one `ChildRequest` with the guard handle in
  `inherited` and hands it to the launcher (`run_contained` in production).
  Engine: environment filtered, stdin closed, output as asked. Passthrough:
  environment as given (None inherits), stdin and output inherited; a
  capture request is refused. The guard is closed in `finally`, so once the
  child ended or at once when no child was created; on `UnconfirmedEndError`
  it is retained first. A refused or unconfirmed start is
  `ProvisioningError(CONTAINMENT)`. `close()` and the block form release an
  unused invocation.

Installation, `tools/release_workflow/git_cliff/installation.py` (design
"Download, verification and extraction", "Publication", "Child process
lifecycle", "Time budgets and retries"):

- `install(layout, pin, budget, seams, lock)`: `.staging-<pid>-<created>-<token>/`
  and `owner.json`; worker attempts through `worker_command` and the
  launcher, each recorded by `lock.record_child` then in the owner file
  (temporary file and replace) before it resumes; D's deadline fixed before
  the first attempt; only a retryable outcome is retried, after the 5 s delay,
  when time remains after it; `verify_archive`, `extract_member`, archive
  removed; recorded staging probe within 15 s (`cache.probe_problem`, now
  public); `entry.json`; `owner.json` removed; `retire_entry`; publication by
  `staging.rename(entry)`.
- Failures: an ended child's failure removes staging and propagates (the
  caller releases the lock); `UnconfirmedEndError` calls
  `lock.retain_record()`, keeps staging, and is the containment stage. A file
  operation refused in staging (publication included) is the permission stage
  naming the directory; a recording failure caused by `PermissionError` is the
  permission stage, any other recording failure the containment stage.
- `retire_entry(layout, pin, attempt)`: no entry, nothing; otherwise rename
  `git-cliff.exe` to `.retired-<pid>-<created>-<token>.exe` when present, then
  the directory to `<pin>/.retired-<pid>-<created>-<token>/`; either refusal is
  the in-use stage.
- `InstallSeams`: the protocol of the seams it uses, so `installation` does
  not import `provisioning`.

Service, `tools/release_workflow/git_cliff/provisioning.py` (design "Target
flow", "Reuse check and the use guard", "Provisioning lock, contention and
recovery"; plan decision Q18):

- `ProvisioningSeams` (the plan's ten seams plus `now`, the local time of the
  record stamps) and `production_seams(runtime)`.
- `provision(tooling_root, pin, budget, *, seams, caller)`: missing pin is the
  configuration stage; platform check; reuse check (`check_entry` with a
  record-free probe inheriting the guard) returning silently; otherwise
  `CacheLock.acquire(W, waiting line)`, recheck, `recover_attempts`,
  `install`; release; guard on the new entry (a failure is the extraction
  stage, once, without the ready line); ready line.
- Error mapping at its boundary: `LockWaitError` to lock wait (naming the
  last live holder, or none), `PermissionError` to permission, other lock
  `OSError` (unverifiable record, unavailable mutex) to lock wait, reuse-probe
  containment to containment, an unreadable entry to extraction. A lock record
  that cannot be removed fails the call, or is added as a note to the failure
  already raised.
- `provisioning_budget(environment, *, tooling_root, pin)`: the budget-setting
  stage for a refused value; `configured_pin(configuration)`: the validated
  `[git-cliff] version` or None.

Tests: `git_cliff_children_fake.py` (scripted children by role, recording
before resume, guard copies for the child's lifetime, reaps, unconfirmed ends;
a world whose guards and busy directories refuse renames, and whose simulated
parent death snapshots the cache, closes the dying caller's guards and lets a
second caller continue from exactly that state), and the leaves
`test_git_cliff_messages`, `test_git_cliff_invocation`,
`test_git_cliff_installation` and `test_git_cliff_provisioning` (reuse and
entry point, contention, budget, lifecycle).

Native checks: `git_cliff_native_service.py` (new, beside the 470-line probes
module) adds five `step-5` checks through the service with killed helper
callers, a temporary tooling root, the synthetic pin 9.9.9 and a stand-in
executable (pip's distlib console launcher, a shebang, a ZIP `__main__.py`
printing `git-cliff 9.9.9`); the recorder catalog, helper dispatch and the
evidence validator follow; `native_checks.v1.json` holds milestone `step-5`.

Also staged: the validation plan's Step 5 sections and the
`git_cliff/__init__.py` docstring.

Writer notes: `.reviews/a.git-cliff-provisioning.step5.journal.md` and
`.reviews/a.git-cliff-provisioning.step5.handoff.md`.

### Change summary for step 5 git-cliff-provisioning (round 1)

Staged paths (25), grouped in the root `a.commit` (five groups, checker
`ready: true`):

1. `feat(release): add the git-cliff failure contract`:
   `tools/release_workflow/git_cliff/messages.py`,
   `tools/release_workflow/git_cliff/budget.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`.
2. `feat(release): start git-cliff through one object`:
   `tools/release_workflow/git_cliff/invocation.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py`.
3. `feat(release): provision git-cliff under its lock`:
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/installation.py`,
   `tools/release_workflow/git_cliff/provisioning.py`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py`.
4. `test(release): record step 5 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_service.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
5. `docs(git-cliff-provisioning): record step 5 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 4 of this plan are committed and pushed (`d9c38262` is the base
of this review). This round's transcript entry is appended to
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and stays
unstaged for the residual commit.

### Writer response for step 5 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 5 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- `ProvisioningSeams` adds `now` to the plan's ten seams, for the entry and
  lock record stamps; `installation` takes the `InstallSeams` protocol rather
  than importing `provisioning`, which imports it.
- `GitCliffInvocation` is single-use: the plan's "close the object's own
  guard only after the child exits, or at once when creation fails" leaves no
  guard for a second run. `run` keeps the plan's six keyword parameters with a
  `PLR0913` suppression. A passthrough start must state `output="inherit"`;
  capture is refused rather than silently ignored.
- The caller resolves the budget once before `provision`, as the plan's
  signature takes a resolved `budget`; `provisioning_budget` gives the
  budget-setting stage its pin and path. `BudgetSettingError` gained `value`
  so the diagnostic does not repeat the remedy.
- The new entry is guarded after the lock release, in the plan's flow order;
  a guard that cannot open is the extraction stage once (plan Q18).
- Failure mapping beyond the design's table: a file operation refused in
  staging, the publication rename included, is the permission stage naming
  the nearest existing directory; a recording failure is the permission stage
  when caused by `PermissionError`, otherwise containment; an unreadable
  entry during the reuse check is the extraction stage (delete and retry); an
  unverifiable lock record or an unavailable transition mutex is the lock-wait
  stage; a lock record that cannot be removed fails a successful call, or
  becomes a note on the failure already raised.
- Simulated parent death: the fake raises a `BaseException` at the boundary
  after snapshotting the cache tree; the cleanup the code then runs is undone
  by restoring that snapshot, which is what a killed process leaves.
- Long waits in tests use a fake clock that wakes 29.75 s late, so a 360 s
  wait costs twelve polls within the CPU budget.
- Native checks: the worker check points `HTTPS_PROXY` and `HTTP_PROXY` at a
  silent local endpoint and runs the worker through this checkout's bootstrap
  (the temporary root holds no checkout); the guard checks take a duplicate of
  the helper's job handle, so the child outlives its killed caller until the
  recorder closes it, then the rename succeeds. The stand-in also performs
  its own short reads of the executable (launcher and ZIP import), so the
  refusal during the run is the service-level behavior; the guard alone was
  proven by the Step 2 checks.

### Reviewer focus for step 5 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-1 -->

## Round 1 by reviewer - Step 5

- Recorded: 2026-11-20T11:38:48+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: da1a91ca73e4f9d40e69e7af64b39fdfa55236cb

Assessed index tree: 870f63b9f6f1321b6de10ed0dd4c8181b654f2db

### Implementation check for step 5 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 5 has NOT been fully implemented.

The ordinary reuse and installation paths match the plan. Five findings affect recovery, timeout enforcement, reporting, handle ownership and native evidence.

Validation plan effects:

Updated and staged only the Step 5 verdict, missing-work list and feature integrity note in the validation plan.

### Pre-repair mandatory checks and coverage for step 5 git-cliff-provisioning (exchange 1) (round 1)

The requestor reported 7,852 passing tests and 100% measured coverage on the request tree. The independent scope-bound `ghog affected --no-cov` run exited 0 with zero failures and warnings. Static inspection found failure paths beyond the existing assertions. The coverage gate measures `tools` and excludes tests and package initializers.

### Resolved validation set and sources for step 5 git-cliff-provisioning (exchange 1) (round 1)

`ghog day --full=speed --whole-suite` (project). The reviewer checked the requestor's proof for the captured whole-suite scope.

### Resolver drift and direction for step 5 git-cliff-provisioning (exchange 1) (round 1)

The current resolver returned the same command, scope and project source.

### Repository state around validation for step 5 git-cliff-provisioning (exchange 1) (round 1)

The requested tree was `da1a91ca73e4f9d40e69e7af64b39fdfa55236cb`. The assessed tree is `870f63b9f6f1321b6de10ed0dd4c8181b654f2db`. The boundary check reported the validation plan, the resulting index change and the ignored focused-test log. The umbrella digest matched.

### Repair inventory for step 5 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- Polishing only (review metadata). Updated the Step 5 validation rows. Implementation and tests received no reviewer edits.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
- `tests/unit/tools/release_workflow/git_cliff_children_fake.py`
- `tests/unit/tools/release_workflow/git_cliff_native_checks.py`
- `tests/unit/tools/release_workflow/git_cliff_native_service.py`
- `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`
- `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`
- `tools/release_workflow/git_cliff/__init__.py`
- `tools/release_workflow/git_cliff/budget.py`
- `tools/release_workflow/git_cliff/cache.py`
- `tools/release_workflow/git_cliff/installation.py`
- `tools/release_workflow/git_cliff/invocation.py`
- `tools/release_workflow/git_cliff/messages.py`
- `tools/release_workflow/git_cliff/provisioning.py`

### Commit plan assessment for step 5 git-cliff-provisioning (exchange 1) (round 1)

The independent checker exited 0, state `valid`, ready `true`, with 25 staged paths and zero diagnostics. Ordered groups follow.

1. `feat(release): add the git-cliff failure contract` (5 paths)
2. `feat(release): start git-cliff through one object` (3 paths)
3. `feat(release): provision git-cliff under its lock` (12 paths)
4. `test(release): record step 5 native checks` (4 paths)
5. `docs(git-cliff-provisioning): record step 5 validation` (1 paths)

Group membership and dependency order are accurate. The final group's body still records a Yes verdict. Refresh it after addressing the findings.

### Findings and boundaries for step 5 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- Preserve an existing staging directory when `mkdir()` fails. At `installation.py:185`, a name collision raises `FileExistsError` and the handler at line 188 recursively deletes the directory this call never created. Force a collision with a sentinel file and verify its contents survive.
- Keep one absolute download deadline through worker creation, recording and the native wait. At `installation.py:251`, an already exhausted budget reaches `WorkerRequest` as a nonpositive duration and raises a bare `ValueError`. Time spent recording a suspended worker also gets added to D because the native wait starts with the earlier duration. Exercise both delays with a fake clock and verify the download-stage error and child cleanup.
- Preserve a local archive write denial across the worker boundary. `network.stream_archive` can raise `PermissionError` opening the target. `download_worker.main` emits a generic fatal outcome and `installation.py:258` reports the download stage with a proxy remedy. Carry the local failure and its path through the worker result, then assert the permission stage and directory remedy.
- Release the newly opened guard if the ready message fails. At `provisioning.py:189`, a broken or closed stderr can raise before the invocation takes ownership. The native handle then remains open in a long-lived caller and prevents later retirement. Inject a failing ready-line writer and verify that the published entry can be renamed after the call.
- Make the two native guard checks identify the inherited guard. `git_cliff_native_service.py:256` observes a rename refusal while the target is itself the running stand-in executable. Its image or its own file accesses can produce the same result. Verify the child's inherited handle refers to the guarded file or add a control that distinguishes those causes, then refresh the Step 5 native record.

Boundary-crossing work: None.

### Writer instructions for step 5 git-cliff-provisioning (exchange 1) (round 1)

Address the five missing-work items in the Step 5 validation plan, refresh the affected native evidence and commit description, and submit the revised index for review.

### Decision rationale for step 5 git-cliff-provisioning (exchange 1) (round 1)

Identity and staged attribution pass. The commit-plan checker accepts the grouping. Implementation completeness, regression coverage and native guard evidence remain open. Changes requested.

### Final reviewer decision for step 5 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-1 -->

## Round 2 by requestor - Step 5

- Recorded: 2026-11-20T12:18:45+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 5
Review round: 2

### Code review evidence for step 5 git-cliff-provisioning (round 2)

request_index_tree: 5053bad4a8a44df5f5c146fcdcb59cf5fa3c0acb
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(release): count the child deadline from its call
group 1 path: tools/release_workflow/windows_child.py
group 1 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
group 2: feat(release): add the git-cliff failure contract
group 2 path: tools/release_workflow/git_cliff/messages.py
group 2 path: tools/release_workflow/git_cliff/budget.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
group 3: feat(release): start git-cliff through one object
group 3 path: tools/release_workflow/git_cliff/invocation.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
group 4: feat(release): provision git-cliff under its lock
group 4 path: tools/release_workflow/git_cliff/download_worker.py
group 4 path: tools/release_workflow/git_cliff/cache.py
group 4 path: tools/release_workflow/git_cliff/installation.py
group 4 path: tools/release_workflow/git_cliff/provisioning.py
group 4 path: tools/release_workflow/git_cliff/__init__.py
group 4 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
group 5: test(release): record step 5 native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_service.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(git-cliff-provisioning): record step 5 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_service.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/budget.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/invocation.py
staged path: tools/release_workflow/git_cliff/messages.py
staged path: tools/release_workflow/git_cliff/provisioning.py
staged path: tools/release_workflow/windows_child.py
```

### Validation scope for step 5 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 5 git-cliff-provisioning (round 2)

Writer assessment for Step 5 of the git-cliff-provisioning plan, round 2: the
step is fully implemented after the five round 1 repairs, and the rerun
implementation check records `Yes. Step 5 has been fully implemented.` in the
staged validation plan (the reviewer's missing-work list is removed, its
document status stays `No, it is not implemented.` while Steps 6 to 8 are
not started).

Evidence, all on the staged tree:

- Repairs, tests first where they apply: the installation leaf adds a staging
  name collision (sentinel kept), an owner file that cannot be written
  (staging this call created removed), a budget spent before the first
  attempt and a worker-reported write denial; the `windows_child` leaf adds
  recording time taken from the wait (frozen clock elsewhere); the worker leaf
  adds a target it cannot write (path reported, none for an HTTP error); the
  provisioning leaf adds a broken ready line (guard released, entry renamed
  afterwards); the messages leaf adds `denied_write`. `ghog single` on these
  leaves exit 0 (235 tests, then the installation leaf again).
- Native record: the recorder with `--milestone step-5`, after the last
  covered source change (`windows_child.py`, `download_worker.py`, the
  service checks), passed 14 of 14 (the five service checks 2.0 s to 12.3 s)
  and the stalled-runner timeout (3.04 s). The guard checks now also observe
  `inherited_handle_is_guard: true` and `control_without_guard: renamed`. A
  first rerun failed only the run variant's rename after the child, still
  refused by the stand-in's interpreter (a job member with its own inherited
  copy) before the job was ended until empty.
- Review validation, `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed` (7862 tests,
  slowest call 0.31 s, outside this step), on index tree
  `5053bad4a8a44df5f5c146fcdcb59cf5fa3c0acb`. An earlier speed walk on the
  repaired tree stopped at `cov=99` on the new owner-file branch, now tested.
  No budget was changed and no exclusion is accepted.
- `rg -n 'sys\.stdout|print\(' tools/release_workflow/git_cliff`: only the
  worker's outcome line. `rg -n 'GIT_CLIFF_' tools/release_workflow/git_cliff`:
  the removal rule only in `invocation.py`.
- Line counts: `installation.py` 351, `provisioning.py` 297, `messages.py`
  150, `download_worker.py` 163, `windows_child.py` 607 (in the 550 to 650
  band since Step 2, below the ceiling), `git_cliff_native_service.py` 412.
- Markdown check and cSpell on the validation plan: clean.

Architecture: unchanged boundaries; the deadline fix lives where the wait
happens (`run_contained`), and the worker's local-failure path is part of its
private outcome contract with the installation. Performance: unchanged
bounds. Feature integrity: `run_contained` callers only get a shorter wait
when creation or recording took time; the worker's outcome gains a field only
for local file failures.

Please check in particular: the deadline counted from the `run_contained`
call and the spent-D check of the download loop; the staging removal rule
after a collision or an owner-file failure; the worker's `path` rule (local
`OSError` with a file name, not a URL error) and its permission mapping; the
ready-line guard release; and the native guard checks' handle identification,
job emptying and guard-free control.

### Implementation report for step 5 git-cliff-provisioning (round 2)

Step 5, "Provisioning service, invocation object and failure contract", is
the fifth of eight steps of the git-cliff-provisioning plan. It composes the
Step 1 to 4 primitives into the design's target flow; no engine operation
calls it before item 4, and no pin is admitted before Step 7.

Failure contract, `tools/release_workflow/git_cliff/messages.py` (design
"Messages, statuses and the failure contract"):

- `Stage` (eleven stages) and the read-only `REMEDIES`; the lock-wait remedy
  is `cache_lock.LOCK_WAIT_REMEDY`.
- `ProvisioningError(ValueError)`: `exit_code = 2`, `stage`, `version` (None
  before any pin exists), `path`, `detail`; its text is `diagnostic()`,
  `git-cliff <pin> unavailable at <path> (<stage> stage): <detail>. <remedy>`.
- `permission_failure(version, error, fallback)`: the permission stage naming
  the nearest existing directory above the refused path.
- `downloading_line`, `ready_line`, `waiting_line` (holder PID, its start as
  local time with offset, the caller's own W).
- `budget.BudgetSettingError` keeps the refused text as `value`.

Invocation object, `tools/release_workflow/git_cliff/invocation.py` (design
"The provisioning entry point for items 4 and 5", "Version probe"; design
decision Q09):

- `engine_environment(environment=None)`: the given or process environment
  without any `GIT_CLIFF_*` name in any case, the only place of that rule.
- `probe_request(executable, *, inherited, deadline, record=None)`:
  `--version` in the executable's directory under the engine policy.
- `GitCliffInvocation(executable, version, guard, *, launch)`, single-use:
  `run(arguments, *, policy, cwd, environment=None, output="capture",
  deadline=None)` builds one `ChildRequest` with the guard handle in
  `inherited` and hands it to the launcher (`run_contained` in production).
  Engine: environment filtered, stdin closed, output as asked. Passthrough:
  environment as given (None inherits), stdin and output inherited; a
  capture request is refused. The guard is closed in `finally`, so once the
  child ended or at once when no child was created; on `UnconfirmedEndError`
  it is retained first. A refused or unconfirmed start is
  `ProvisioningError(CONTAINMENT)`. `close()` and the block form release an
  unused invocation.

Installation, `tools/release_workflow/git_cliff/installation.py` (design
"Download, verification and extraction", "Publication", "Child process
lifecycle", "Time budgets and retries"):

- `install(layout, pin, budget, seams, lock)`: `.staging-<pid>-<created>-<token>/`
  and `owner.json`; worker attempts through `worker_command` and the
  launcher, each recorded by `lock.record_child` then in the owner file
  (temporary file and replace) before it resumes; D's deadline fixed before
  the first attempt; only a retryable outcome is retried, after the 5 s delay,
  when time remains after it; `verify_archive`, `extract_member`, archive
  removed; recorded staging probe within 15 s (`cache.probe_problem`, now
  public); `entry.json`; `owner.json` removed; `retire_entry`; publication by
  `staging.rename(entry)`.
- Failures: an ended child's failure removes staging and propagates (the
  caller releases the lock); `UnconfirmedEndError` calls
  `lock.retain_record()`, keeps staging, and is the containment stage. A file
  operation refused in staging (publication included) is the permission stage
  naming the directory; a recording failure caused by `PermissionError` is the
  permission stage, any other recording failure the containment stage.
- `retire_entry(layout, pin, attempt)`: no entry, nothing; otherwise rename
  `git-cliff.exe` to `.retired-<pid>-<created>-<token>.exe` when present, then
  the directory to `<pin>/.retired-<pid>-<created>-<token>/`; either refusal is
  the in-use stage.
- `InstallSeams`: the protocol of the seams it uses, so `installation` does
  not import `provisioning`.

Service, `tools/release_workflow/git_cliff/provisioning.py` (design "Target
flow", "Reuse check and the use guard", "Provisioning lock, contention and
recovery"; plan decision Q18):

- `ProvisioningSeams` (the plan's ten seams plus `now`, the local time of the
  record stamps) and `production_seams(runtime)`.
- `provision(tooling_root, pin, budget, *, seams, caller)`: missing pin is the
  configuration stage; platform check; reuse check (`check_entry` with a
  record-free probe inheriting the guard) returning silently; otherwise
  `CacheLock.acquire(W, waiting line)`, recheck, `recover_attempts`,
  `install`; release; guard on the new entry (a failure is the extraction
  stage, once, without the ready line); ready line.
- Error mapping at its boundary: `LockWaitError` to lock wait (naming the
  last live holder, or none), `PermissionError` to permission, other lock
  `OSError` (unverifiable record, unavailable mutex) to lock wait, reuse-probe
  containment to containment, an unreadable entry to extraction. A lock record
  that cannot be removed fails the call, or is added as a note to the failure
  already raised.
- `provisioning_budget(environment, *, tooling_root, pin)`: the budget-setting
  stage for a refused value; `configured_pin(configuration)`: the validated
  `[git-cliff] version` or None.

Tests: `git_cliff_children_fake.py` (scripted children by role, recording
before resume, guard copies for the child's lifetime, reaps, unconfirmed ends;
a world whose guards and busy directories refuse renames, and whose simulated
parent death snapshots the cache, closes the dying caller's guards and lets a
second caller continue from exactly that state), and the leaves
`test_git_cliff_messages`, `test_git_cliff_invocation`,
`test_git_cliff_installation` and `test_git_cliff_provisioning` (reuse and
entry point, contention, budget, lifecycle).

Native checks: `git_cliff_native_service.py` (new, beside the 470-line probes
module) adds five `step-5` checks through the service with killed helper
callers, a temporary tooling root, the synthetic pin 9.9.9 and a stand-in
executable (pip's distlib console launcher, a shebang, a ZIP `__main__.py`
printing `git-cliff 9.9.9`); the recorder catalog, helper dispatch and the
evidence validator follow; `native_checks.v1.json` holds milestone `step-5`.

Also staged: the validation plan's Step 5 sections and the
`git_cliff/__init__.py` docstring.

Round 1 repairs (code review round 1, five findings):

- `installation`: staging creation and its owner file are separate steps; a
  failed `mkdir()` removes nothing, a failed owner file removes only the
  directory this call created. The download loop checks what remains of D at
  the top of each attempt and fails the download stage when it is spent. A
  worker outcome naming a local `path` is the permission stage
  (`messages.denied_write`), not retried.
- `windows_child.run_contained`: the deadline counts from the call (injectable
  `clock`); the root wait receives what remains, down to zero, so creation and
  recording are taken from it.
- `download_worker.main`: a local `OSError` with a file name that is not a URL
  error adds that `path` to its fatal outcome.
- `provisioning`: the new entry's guard is wrapped in its invocation before
  the ready line; a ready line that cannot be written closes it.
- `git_cliff_native_service`: the guard checks name the file of the child's
  inherited handle value, end the job until it counts no active process
  before the rename after the child, and run a guard-free control of the
  stand-in; the record is refreshed (14 of 14).

Writer notes: `.reviews/a.git-cliff-provisioning.step5.journal.md` and
`.reviews/a.git-cliff-provisioning.step5.handoff.md`.

### Change summary for step 5 git-cliff-provisioning (round 2)

Staged paths (30), grouped in the root `a.commit` (six groups, checker
`ready: true`); round 2 adds `tools/release_workflow/windows_child.py`,
`tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`,
`tools/release_workflow/git_cliff/download_worker.py` and
`tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`:

1. `fix(release): count the child deadline from its call`:
   `tools/release_workflow/windows_child.py`,
   `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`.
2. `feat(release): add the git-cliff failure contract`:
   `tools/release_workflow/git_cliff/messages.py`,
   `tools/release_workflow/git_cliff/budget.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`.
3. `feat(release): start git-cliff through one object`:
   `tools/release_workflow/git_cliff/invocation.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py`.
4. `feat(release): provision git-cliff under its lock`:
   `tools/release_workflow/git_cliff/download_worker.py`,
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/installation.py`,
   `tools/release_workflow/git_cliff/provisioning.py`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py`.
5. `test(release): record step 5 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_service.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
6. `docs(git-cliff-provisioning): record step 5 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 4 of this plan are committed and pushed (`d9c38262` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` stays unstaged
for the residual commit.

### Writer response for step 5 git-cliff-provisioning (round 2)

Writer response:

Writer response to round 1 (changes-requested, five findings, no reviewer
code repair). All five are accepted and repaired; there is no disagreement.

- Staging ownership: `install` now separates the creation of staging from its
  owner file. A `mkdir()` failure, a name collision included, raises the
  permission stage without removing anything; only a directory this call
  created is removed when its owner file cannot be written. The installation
  leaf forces a collision (fixed token) over a directory holding a sentinel,
  which survives, and no worker starts.
- One absolute download deadline: the download loop checks what remains of D
  at the top of every attempt and fails the download stage before building a
  `WorkerRequest` when it is spent, so no nonpositive budget reaches it. The
  recording delay is fixed where the wait happens: `run_contained` now counts
  its deadline from its own call (new injectable `clock`), so creation and
  recording are taken from the wait, down to zero, instead of extending D.
  Tests: the installation leaf spends D before the first attempt (no worker,
  staging removed, lock released) and keeps the after-delay case; the
  `windows_child` leaf runs on a frozen clock and adds recording time taken
  from the wait (1750 ms left of 2.5 s, then zero).
- Local write denial: the worker adds the `path` of a local `OSError` that is
  not a URL error (an `HTTPError` carries its URL as `filename`, so it names
  none) to its fatal outcome; the installation reports the permission stage
  naming that directory through the new `messages.denied_write`, without a
  retry. Tests in the worker, installation and messages leaves.
- Ready line: the new guard is wrapped in its invocation first; if the ready
  line cannot be written, the invocation is closed before the failure leaves.
  The provisioning leaf injects a failing writer and renames the published
  executable afterwards.
- Native guard evidence: both guard checks now name the file behind the
  handle value the child inherited (`GetFinalPathNameByHandleW` on a copy
  closed before any rename), which must be the guarded executable, and run a
  control of the same stand-in without any guard, whose rename succeeds while
  it runs. The first recorder rerun also showed that the stand-in's own
  interpreter, a job member, holds an inherited copy too: the check now ends
  the job and waits until it counts no active process before the rename after
  the child. The recorder then passed 14 of 14.

The reviewer's validation-plan edits (No verdict, missing work, feature
integrity note) are superseded by the implementation check rerun: the Step 5
analysis is back to Yes, the repairs are recorded and the missing-work list is
removed. `a.commit` gains a first group for the `windows_child` change, and the
worker change joins the service group; the final group's body mentions the
round 1 repairs.

### Reviewer focus for step 5 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-2 -->

## Round 2 by reviewer - Step 5

- Recorded: 2026-11-20T12:24:09+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 5053bad4a8a44df5f5c146fcdcb59cf5fa3c0acb

Assessed index tree: 7a443a75a4e2c6ded3a8d90236a49f3bdf8558ce

### Implementation check for step 5 git-cliff-provisioning (exchange 1) (round 2)

Result:

No. Step 5 has NOT been fully implemented.

The sentinel survives a collision, the broken ready line releases the guard, and both recorded native cases identify the inherited handle and include a guard-free control. The early budget check, record-time deduction and worker path on open failure cover part of the two carried findings. The remaining cases are listed below.

Validation plan effects:

Updated and staged only the Step 5 verdict and missing-work list in docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md.

### Pre-repair mandatory checks and coverage for step 5 git-cliff-provisioning (exchange 1) (round 2)

The writer reported 7,862 tests and 100% coverage in its whole-suite speed walk on the request tree. The independent scope-bound `ghog affected --no-cov` run exited 0 with zero failures and warnings. The static test review identified a deadline transition and error cases that the current assertions miss or explicitly accept.

### Resolved validation set and sources for step 5 git-cliff-provisioning (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` (project source, requestor evidence).

### Resolver drift and direction for step 5 git-cliff-provisioning (exchange 1) (round 2)

The current resolver produced the same command, order and source.

### Repository state around validation for step 5 git-cliff-provisioning (exchange 1) (round 2)

The request tree matched 5053bad4a8a44df5f5c146fcdcb59cf5fa3c0acb. The focused run changed only its ignored log within the validation capture. The assessed tree is 7a443a75a4e2c6ded3a8d90236a49f3bdf8558ce after staging the attributable validation-plan patch. The umbrella digest matched before and after.

### Repair inventory for step 5 git-cliff-provisioning (exchange 1) (round 2)

Repairs made:

- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md — review metadata only. Updated the Step 5 verdict and concrete missing work.

Paths staged:

- docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
- tests/unit/tools/release_workflow/git_cliff_children_fake.py
- tests/unit/tools/release_workflow/git_cliff_native_checks.py
- tests/unit/tools/release_workflow/git_cliff_native_service.py
- tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
- tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
- `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py`
- tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
- `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py`
- tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
- `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py`
- tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
- tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
- tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
- `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py`
- tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
- tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
- tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
- tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
- tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
- `tools/release_workflow/git_cliff/__init__.py`
- tools/release_workflow/git_cliff/budget.py
- tools/release_workflow/git_cliff/cache.py
- tools/release_workflow/git_cliff/download_worker.py
- tools/release_workflow/git_cliff/installation.py
- tools/release_workflow/git_cliff/invocation.py
- tools/release_workflow/git_cliff/messages.py
- tools/release_workflow/git_cliff/provisioning.py
- tools/release_workflow/windows_child.py

### Commit plan assessment for step 5 git-cliff-provisioning (exchange 1) (round 2)

Independent checker returned valid, ready, exit 0, and zero diagnostics. Its six ordered subjects cover 29 staged paths. The request prose says 30. The file grouping is accurate. Before committing, align the validation commit body with the final Step 5 verdict.

1. fix(release): count the child deadline from its call (2 paths)
2. feat(release): add the git-cliff failure contract (5 paths)
3. feat(release): start git-cliff through one object (3 paths)
4. feat(release): provision git-cliff under its lock (14 paths)
5. test(release): record step 5 native checks (4 paths)
6. docs(git-cliff-provisioning): record step 5 validation (1 paths)

### Findings and boundaries for step 5 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings:

- Carry the original monotonic download expiry from `installation._download` into the contained run. The remaining duration is sampled before command construction and is restarted in `_Run.__init__`. Recording can also consume the budget, yet `_pre_resume` still resumes the worker and a zero-time wait can report success. Exercise a delay between sampling and launcher entry, and recording past expiry. Require a download-stage timeout and settlement of any suspended child before it can run.
- Attach the archive target to failures from opening, writing and closing the output stream. `download_worker.main` uses `OSError.filename`, which may be absent on a buffered write or flush. The parent then reports a download failure and a proxy remedy. Exercise a target that opens successfully and raises a filename-less write error, and a response read that fails separately. Verify that the former names the local target directory and the latter keeps its network diagnostic.
- Keep the ready-message guard cleanup and preserve the public `provision()` failure contract. The new regression expects a raw `OSError` from `provisioning.py` when stderr is broken, bypassing `ProvisioningError` and its engine status 2. Give the caller a typed diagnostic that identifies the reporting failure, preserve the cause, and assert that the published entry can still be renamed.

Boundary-crossing work: None.

### Writer instructions for step 5 git-cliff-provisioning (exchange 1) (round 2)

Complete the three items under Missing work for Step 5, exercise each failure through its caller, refresh the native evidence for affected sources, and update the validation plan and commit description before requesting another review.

### Decision rationale for step 5 git-cliff-provisioning (exchange 1) (round 2)

Identity and staged attribution passed. The focused suite passed and the mechanical commit-plan check passed. Completeness, static test coverage and absence of unresolved findings prevent a commit-ready recommendation.

### Final reviewer decision for step 5 git-cliff-provisioning (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-5-round-2 -->

## Round 3 by requestor - Step 5

- Recorded: 2026-11-20T12:51:29+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: request

### Review identity for step 5 git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 5
Review round: 3

### Code review evidence for step 5 git-cliff-provisioning (round 3)

request_index_tree: 594013eefdd02590437447450fb150aaa2f0295d
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: fix(release): bound a contained child by its expiry
group 1 path: tools/release_workflow/windows_child.py
group 1 path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
group 2: feat(release): add the git-cliff failure contract
group 2 path: tools/release_workflow/git_cliff/messages.py
group 2 path: tools/release_workflow/git_cliff/budget.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
group 3: feat(release): start git-cliff through one object
group 3 path: tools/release_workflow/git_cliff/invocation.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
group 4: feat(release): provision git-cliff under its lock
group 4 path: tools/release_workflow/git_cliff/network.py
group 4 path: tools/release_workflow/git_cliff/download_worker.py
group 4 path: tools/release_workflow/git_cliff/cache.py
group 4 path: tools/release_workflow/git_cliff/installation.py
group 4 path: tools/release_workflow/git_cliff/provisioning.py
group 4 path: tools/release_workflow/git_cliff/__init__.py
group 4 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
group 5: test(release): record step 5 native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_service.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(git-cliff-provisioning): record step 5 validation
group 6 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_service.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/budget.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/invocation.py
staged path: tools/release_workflow/git_cliff/messages.py
staged path: tools/release_workflow/git_cliff/network.py
staged path: tools/release_workflow/git_cliff/provisioning.py
staged path: tools/release_workflow/windows_child.py
```

### Validation scope for step 5 git-cliff-provisioning (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 5 git-cliff-provisioning (round 3)

Writer assessment for Step 5 of the git-cliff-provisioning plan, round 3: the
step is fully implemented after the round 1 and round 2 repairs, and the rerun
implementation check records `Yes. Step 5 has been fully implemented.` in the
staged validation plan (the reviewer's round 2 missing-work list is removed;
the document status stays `No, it is not implemented.` while Steps 6 to 8 are
not started).

Evidence, all on the staged tree:

- Round 2 repairs, each through its caller: the installation leaf reaches a
  worker's resume past D after a delay at launcher entry and after a
  recording that spends D (download stage, the worker never ran, staging and
  lock released) and a download line that cannot be written (reporting
  stage); the `windows_child` leaf covers the earlier of `expires` and the
  call-relative deadline bounding the wait and children recorded past their
  bound never resumed; the network leaf covers write and close failures that
  name no file, a target that cannot be opened (all naming the target) and a
  stalled read naming none; the worker leaf a write failure naming no file
  still reported with its path; the contention leaf a waiting line and the
  provisioning leaf a ready line that cannot be written (reporting stage,
  cause kept, guard released, entry renamed afterwards); the messages leaf
  `announce`. `ghog single` on these leaves exit 0 (288 tests).
- Native record: the recorder with `--milestone step-5`, after the last
  covered source change (`windows_child.py`, `network.py`, the service
  modules), passed 14 of 14 (the five service checks 2.1 s to 5.6 s) and the
  stalled-runner timeout (3.04 s).
- Default walk exit 0 after fixing its check findings (`PT011`, `TRY301`,
  radon C on the fake launcher, now split, and `MD050` on five bare
  `__init__.py` paths of the round 2 answer in the transcript, now code
  spans; the transcript stays unstaged).
- Review validation, `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed` (7879 tests,
  slowest call 0.31 s, outside this step), on index tree
  `594013eefdd02590437447450fb150aaa2f0295d`. No budget was changed and no
  exclusion is accepted.
- `rg -n 'sys\.stdout|print\(' tools/release_workflow/git_cliff`: only the
  worker's outcome line. `rg -n 'GIT_CLIFF_' tools/release_workflow/git_cliff`:
  the removal rule only in `invocation.py`.
- Line counts: `installation.py` 356, `provisioning.py` 301, `messages.py`
  165, `network.py` 148, `windows_child.py` 619 (in the 550 to 650 band
  since Step 2, below the ceiling), `git_cliff_children_fake.py` 485.
- Markdown check and cSpell on the validation plan and the transcript: clean.

Architecture: unchanged boundaries; the absolute expiry is a field of the
child request, honored by the launcher where the resume and the wait happen;
the target-failure rule lives in the network adapter; standard-error writes
go through one messages helper. Performance: unchanged bounds (one extra
clock read per child, one wrapper call per written chunk). Feature integrity:
`expires` is optional; a `run_contained` caller sees a child never resumed
only when its own bound was already spent; `reporting` is a twelfth stage
beside the design's eleven, recorded in the validation plan.

Please check in particular: `_Run`'s earlier-bound computation, the
no-resume path and its teardown; the installation's `expires=deadline`
without a duration; `_on_target` around open, write and close, and that
response reads stay unwrapped; and `announce` with the ready line's guard
release.

### Implementation report for step 5 git-cliff-provisioning (round 3)

Step 5, "Provisioning service, invocation object and failure contract", is
the fifth of eight steps of the git-cliff-provisioning plan. It composes the
Step 1 to 4 primitives into the design's target flow; no engine operation
calls it before item 4, and no pin is admitted before Step 7.

Failure contract, `tools/release_workflow/git_cliff/messages.py` (design
"Messages, statuses and the failure contract"):

- `Stage` (eleven stages) and the read-only `REMEDIES`; the lock-wait remedy
  is `cache_lock.LOCK_WAIT_REMEDY`.
- `ProvisioningError(ValueError)`: `exit_code = 2`, `stage`, `version` (None
  before any pin exists), `path`, `detail`; its text is `diagnostic()`,
  `git-cliff <pin> unavailable at <path> (<stage> stage): <detail>. <remedy>`.
- `permission_failure(version, error, fallback)`: the permission stage naming
  the nearest existing directory above the refused path.
- `downloading_line`, `ready_line`, `waiting_line` (holder PID, its start as
  local time with offset, the caller's own W).
- `budget.BudgetSettingError` keeps the refused text as `value`.

Invocation object, `tools/release_workflow/git_cliff/invocation.py` (design
"The provisioning entry point for items 4 and 5", "Version probe"; design
decision Q09):

- `engine_environment(environment=None)`: the given or process environment
  without any `GIT_CLIFF_*` name in any case, the only place of that rule.
- `probe_request(executable, *, inherited, deadline, record=None)`:
  `--version` in the executable's directory under the engine policy.
- `GitCliffInvocation(executable, version, guard, *, launch)`, single-use:
  `run(arguments, *, policy, cwd, environment=None, output="capture",
  deadline=None)` builds one `ChildRequest` with the guard handle in
  `inherited` and hands it to the launcher (`run_contained` in production).
  Engine: environment filtered, stdin closed, output as asked. Passthrough:
  environment as given (None inherits), stdin and output inherited; a
  capture request is refused. The guard is closed in `finally`, so once the
  child ended or at once when no child was created; on `UnconfirmedEndError`
  it is retained first. A refused or unconfirmed start is
  `ProvisioningError(CONTAINMENT)`. `close()` and the block form release an
  unused invocation.

Installation, `tools/release_workflow/git_cliff/installation.py` (design
"Download, verification and extraction", "Publication", "Child process
lifecycle", "Time budgets and retries"):

- `install(layout, pin, budget, seams, lock)`: `.staging-<pid>-<created>-<token>/`
  and `owner.json`; worker attempts through `worker_command` and the
  launcher, each recorded by `lock.record_child` then in the owner file
  (temporary file and replace) before it resumes; D's deadline fixed before
  the first attempt; only a retryable outcome is retried, after the 5 s delay,
  when time remains after it; `verify_archive`, `extract_member`, archive
  removed; recorded staging probe within 15 s (`cache.probe_problem`, now
  public); `entry.json`; `owner.json` removed; `retire_entry`; publication by
  `staging.rename(entry)`.
- Failures: an ended child's failure removes staging and propagates (the
  caller releases the lock); `UnconfirmedEndError` calls
  `lock.retain_record()`, keeps staging, and is the containment stage. A file
  operation refused in staging (publication included) is the permission stage
  naming the directory; a recording failure caused by `PermissionError` is the
  permission stage, any other recording failure the containment stage.
- `retire_entry(layout, pin, attempt)`: no entry, nothing; otherwise rename
  `git-cliff.exe` to `.retired-<pid>-<created>-<token>.exe` when present, then
  the directory to `<pin>/.retired-<pid>-<created>-<token>/`; either refusal is
  the in-use stage.
- `InstallSeams`: the protocol of the seams it uses, so `installation` does
  not import `provisioning`.

Service, `tools/release_workflow/git_cliff/provisioning.py` (design "Target
flow", "Reuse check and the use guard", "Provisioning lock, contention and
recovery"; plan decision Q18):

- `ProvisioningSeams` (the plan's ten seams plus `now`, the local time of the
  record stamps) and `production_seams(runtime)`.
- `provision(tooling_root, pin, budget, *, seams, caller)`: missing pin is the
  configuration stage; platform check; reuse check (`check_entry` with a
  record-free probe inheriting the guard) returning silently; otherwise
  `CacheLock.acquire(W, waiting line)`, recheck, `recover_attempts`,
  `install`; release; guard on the new entry (a failure is the extraction
  stage, once, without the ready line); ready line.
- Error mapping at its boundary: `LockWaitError` to lock wait (naming the
  last live holder, or none), `PermissionError` to permission, other lock
  `OSError` (unverifiable record, unavailable mutex) to lock wait, reuse-probe
  containment to containment, an unreadable entry to extraction. A lock record
  that cannot be removed fails the call, or is added as a note to the failure
  already raised.
- `provisioning_budget(environment, *, tooling_root, pin)`: the budget-setting
  stage for a refused value; `configured_pin(configuration)`: the validated
  `[git-cliff] version` or None.

Tests: `git_cliff_children_fake.py` (scripted children by role, recording
before resume, guard copies for the child's lifetime, reaps, unconfirmed ends;
a world whose guards and busy directories refuse renames, and whose simulated
parent death snapshots the cache, closes the dying caller's guards and lets a
second caller continue from exactly that state), and the leaves
`test_git_cliff_messages`, `test_git_cliff_invocation`,
`test_git_cliff_installation` and `test_git_cliff_provisioning` (reuse and
entry point, contention, budget, lifecycle).

Native checks: `git_cliff_native_service.py` (new, beside the 470-line probes
module) adds five `step-5` checks through the service with killed helper
callers, a temporary tooling root, the synthetic pin 9.9.9 and a stand-in
executable (pip's distlib console launcher, a shebang, a ZIP `__main__.py`
printing `git-cliff 9.9.9`); the recorder catalog, helper dispatch and the
evidence validator follow; `native_checks.v1.json` holds milestone `step-5`.

Also staged: the validation plan's Step 5 sections and the
`git_cliff/__init__.py` docstring.

Round 1 repairs (code review round 1, five findings):

- `installation`: staging creation and its owner file are separate steps; a
  failed `mkdir()` removes nothing, a failed owner file removes only the
  directory this call created. The download loop checks what remains of D at
  the top of each attempt and fails the download stage when it is spent. A
  worker outcome naming a local `path` is the permission stage
  (`messages.denied_write`), not retried.
- `windows_child.run_contained`: the deadline counts from the call (injectable
  `clock`); the root wait receives what remains, down to zero, so creation and
  recording are taken from it.
- `download_worker.main`: a local `OSError` with a file name that is not a URL
  error adds that `path` to its fatal outcome.
- `provisioning`: the new entry's guard is wrapped in its invocation before
  the ready line; a ready line that cannot be written closes it.
- `git_cliff_native_service`: the guard checks name the file of the child's
  inherited handle value, end the job until it counts no active process
  before the rename after the child, and run a guard-free control of the
  stand-in; the record is refreshed (14 of 14).

Round 2 repairs (code review round 2, three findings):

- `windows_child`: `ChildRequest.expires`, an absolute instant on the run's
  clock; `run_contained` takes the earlier of it and its call-relative
  deadline, checks it after recording and, once passed, never resumes the
  child (the teardown ends it suspended; timed out).
- `installation`: each worker request carries D's expiry (`expires=deadline`)
  and no duration; the worker still receives what remains for its socket
  timeout. The download line goes through `messages.announce`.
- `network.stream_archive`: opening, each write and the close of the target
  run through `_on_target`, which raises an `OSError` naming the target from
  its cause; the target is closed on any failure; the size check moved to
  `_within`. Response reads are not wrapped.
- `messages`: `Stage.REPORTING` and its remedy; `announce(write, line, *,
  version, path)` turns an `OSError` or `ValueError` of the stream into that
  stage with the error as cause.
- `provisioning`: the waiting and ready lines go through `announce`; the
  ready line still closes the new invocation first.
- Test support: the fake launcher honors `expires` like `run_contained`
  (records `ran` and the launch time; `entry_seconds` spends time before
  creation); its creation moved to `_create`.

Writer notes: `.reviews/a.git-cliff-provisioning.step5.journal.md` and
`.reviews/a.git-cliff-provisioning.step5.handoff.md`.

### Change summary for step 5 git-cliff-provisioning (round 3)

Staged paths (31), grouped in the root `a.commit` (six groups, checker
`ready: true`). Round 2 added `tools/release_workflow/windows_child.py`,
`tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`,
`tools/release_workflow/git_cliff/download_worker.py` and
`tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`;
round 3 adds `tools/release_workflow/git_cliff/network.py` and
`tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`.
The first group's subject changed with the expiry repair:

1. `fix(release): bound a contained child by its expiry`:
   `tools/release_workflow/windows_child.py`,
   `tests/unit/tools/release_workflow/test_windows_child/test_windows_child_tdd.py`.
2. `feat(release): add the git-cliff failure contract`:
   `tools/release_workflow/git_cliff/messages.py`,
   `tools/release_workflow/git_cliff/budget.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_messages/test_git_cliff_messages_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_budget/test_git_cliff_budget_tdd.py`.
3. `feat(release): start git-cliff through one object`:
   `tools/release_workflow/git_cliff/invocation.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_invocation/test_git_cliff_invocation_tdd.py`.
4. `feat(release): provision git-cliff under its lock`:
   `tools/release_workflow/git_cliff/network.py`,
   `tools/release_workflow/git_cliff/download_worker.py`,
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/installation.py`,
   `tools/release_workflow/git_cliff/provisioning.py`,
   `tools/release_workflow/git_cliff/__init__.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_installation/test_git_cliff_installation_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_contention_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_budget_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_lifecycle_tdd.py`.
5. `test(release): record step 5 native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_service.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
6. `docs(git-cliff-provisioning): record step 5 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 4 of this plan are committed and pushed (`d9c38262` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` stays unstaged
for the residual commit.

### Writer response for step 5 git-cliff-provisioning (round 3)

Writer response:

Writer response to round 2 (changes-requested, three findings, no reviewer
code repair). All three are accepted and repaired; there is no disagreement.

- Absolute download expiry: `ChildRequest` gains `expires`, an absolute
  instant on the launcher's monotonic clock (the seams' clock in production).
  Each worker request carries D's expiry itself instead of a duration, so the
  sample before command construction and the restart in `_Run.__init__` are
  gone. `run_contained` bounds the wait by the earlier of `expires` and its
  deadline counted from the call, and checks that bound after recording: a
  child past it is never resumed, the teardown ends it suspended and the
  outcome is timed out, which the installation reports as the download stage.
  Tests: the installation leaf reaches the worker's resume past D after a
  delay at launcher entry and after a recording that spends D (no run, no
  write, staging and lock released); the `windows_child` leaf covers the
  earlier bound reaching the wait and children recorded past their bound
  never resumed. One older case, a negative deadline, moved there, since such
  a child now never runs.
- Target failures: `network.stream_archive` wraps opening, every write and
  the close of the target; an `OSError` there is raised again naming the
  target, from its cause, and the target is closed on any failure; a failed
  response read is not wrapped and keeps its network error. Tests: the
  network leaf (write and close failures naming no file, a target that cannot
  be opened, a stalled read naming none) and the worker leaf (a write failure
  naming no file still reports the path); the installation leaf already maps
  a reported path to the permission stage.
- Reporting failures: `messages.announce` writes every standard-error line
  (download, waiting, ready). A stream that raises `OSError` or `ValueError`
  is a new `reporting` stage of `ProvisioningError` (status 2, remedy: check
  the calling command's console or redirection), with the original error as
  cause; the ready line still closes the new invocation's guard first. This
  adds a twelfth stage beside the design's eleven; the validation plan's
  feature integrity notes it. Tests: messages (`announce` with both error
  kinds), installation (download line), contention (waiting line) and
  provisioning (ready line, the published executable renamed afterwards).

Also from round 2: the change summary now counts 31 staged paths; the final
group's body matches the Yes verdict restored by the rerun implementation
check, which supersedes the reviewer's No and missing-work rows. The default
walk found MD050 in the transcript on bare `__init__.py` paths of the round 2
answer; those five lines are now code spans (polishing, transcript unstaged).

### Reviewer focus for step 5 git-cliff-provisioning (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-5-round-3 -->

## Round 3 by reviewer - Step 5

- Recorded: 2026-11-20T12:55:40+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: answer

### Assessed index identity for step 5 git-cliff-provisioning (exchange 1) (round 3)

Baseline index tree: 594013eefdd02590437447450fb150aaa2f0295d

Assessed index tree: 594013eefdd02590437447450fb150aaa2f0295d

### Implementation check for step 5 git-cliff-provisioning (exchange 1) (round 3)

Result:

Yes. Step 5 has been fully implemented.

I traced the original download expiry through worker launch, pre-resume checking and the native wait. The tests cover a worker delayed at entry or while recording, settlement without resume, and the remaining time supplied to the wait. The worker retains the target path on open, write and close errors. A stalled response read keeps its network classification. Stderr failures now reach callers as a `ProvisioningError` with status 2 and the original cause. The ready-line case also verifies that the guard closes and the published executable can be renamed. The earlier staging sentinel and native guard checks still apply.

Validation plan effects:

The staged Step 5 validation plan already records the Yes verdict, the three repairs and their evidence. The writer documents the additional `reporting` stage for a broken console or redirection. It supplies a remedy specific to that stream while preserving the eleven planned stages.

### Pre-repair mandatory checks and coverage for step 5 git-cliff-provisioning (exchange 1) (round 3)

The independent scope-bound `ghog affected --no-cov` run passed with zero failures and warnings. The writer reported 7,879 tests, 100% coverage, zero speed outliers, zero exclusions, and fourteen passing native checks on the refreshed milestone. Static review of the changed failure paths found matching assertions.

### Resolved validation set and sources for step 5 git-cliff-provisioning (exchange 1) (round 3)

`ghog day --full=speed --whole-suite` from the project configuration. The requestor supplied the executed result.

### Resolver drift and direction for step 5 git-cliff-provisioning (exchange 1) (round 3)

The current resolver and the request agree on the command, its order and the project source.

### Repository state around validation for step 5 git-cliff-provisioning (exchange 1) (round 3)

The request, baseline and assessed index trees all equal `594013eefdd02590437447450fb150aaa2f0295d`. The validation capture detected only the ignored focused-test log. The umbrella digest comparison passed.

### Repair inventory for step 5 git-cliff-provisioning (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 5 git-cliff-provisioning (exchange 1) (round 3)

Independent checker returned valid and ready, exit 0 with zero diagnostics. All 31 staged paths are accounted for exactly once. The six subjects in order are:

1. `fix(release): bound a contained child by its expiry` (2 paths)
2. `feat(release): add the git-cliff failure contract` (5 paths)
3. `feat(release): start git-cliff through one object` (3 paths)
4. `feat(release): provision git-cliff under its lock` (16 paths)
5. `test(release): record step 5 native checks` (4 paths)
6. `docs(git-cliff-provisioning): record step 5 validation` (1 paths)

### Findings and boundaries for step 5 git-cliff-provisioning (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 5 git-cliff-provisioning (exchange 1) (round 3)

Present the advisory recommendation at the human commit gate.

### Decision rationale for step 5 git-cliff-provisioning (exchange 1) (round 3)

Exact review identity, implementation completeness, focused validation and static coverage, staged attribution, resolution of the carried findings, and commit grouping all passed. The reviewer made no substantive repairs. Step 5 is commit-ready for the human decision.

### Final reviewer decision for step 5 git-cliff-provisioning (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-5-round-3 -->

## Round 3 by human - Step 5 - human-confirmation

- Recorded: 2026-11-20T13:45:11+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 5
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
