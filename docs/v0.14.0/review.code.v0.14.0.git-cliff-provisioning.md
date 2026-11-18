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
