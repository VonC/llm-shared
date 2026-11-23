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

## Round 1 by requestor - Step 6

- Recorded: 2026-11-20T19:23:14+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 6
- Outcome: request

### Review identity for step 6 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 6
Review round: 1

### Code review evidence for step 6 git-cliff-provisioning (round 1)

request_index_tree: 70dbca4a6e5a6af9d1a28c1643d5ead9ab4083b5
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): give Git an input stream
group 1 path: tools/release_workflow/git.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/conftest.py
group 2: refactor(release): provision any install target
group 2 path: tools/release_workflow/git_cliff/archive.py
group 2 path: tools/release_workflow/git_cliff/cache.py
group 2 path: tools/release_workflow/git_cliff/cache_lock.py
group 2 path: tools/release_workflow/git_cliff/download_worker.py
group 2 path: tools/release_workflow/git_cliff/manifest.py
group 2 path: tools/release_workflow/git_cliff/installation.py
group 2 path: tools/release_workflow/git_cliff/provisioning.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 3: feat(release): build the snapshot-tag fixture
group 3 path: tools/release_workflow/git_cliff/fixture_history.py
group 4: feat(release): compare two git-cliff versions
group 4 path: tools/release_workflow/git_cliff/comparison.py
group 5: feat(release): acquire git-cliff evidence candidates
group 5 path: tools/release_workflow/git_cliff/candidates.py
group 6: feat(release): add the reviewed evidence bundle
group 6 path: tools/release_workflow/git_cliff/bundle.py
group 7: test(release): cover the evidence modules
group 7 path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
group 7 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 7 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
group 7 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
group 8: feat(release): run the evidence harness by hand
group 8 path: tools/release_workflow/git_cliff/harness.py
group 8 path: tools/release_workflow/git_cliff/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
group 9: docs(git-cliff-provisioning): record step 6 validation
group 9 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/archive.py
staged path: tools/release_workflow/git_cliff/bundle.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
staged path: tools/release_workflow/git_cliff/candidates.py
staged path: tools/release_workflow/git_cliff/comparison.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/fixture_history.py
staged path: tools/release_workflow/git_cliff/harness.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/git_cliff/provisioning.py
```

### Validation scope for step 6 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 6 git-cliff-provisioning (round 1)

Writer assessment for Step 6 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and the implementation check records `Yes. Step 6
has been fully implemented.` in the staged validation plan (the document
status stays `No, it is not implemented.` while Steps 7 and 8 are not
started).

Evidence, all on the staged tree:

- Red first: `ghog single` on the new leaves and the impacted ones failed at
  collection on the missing names (exit 4, 11 errors).
- Targeted: `ghog single` on the Step 6 leaves, `test_git` and the cache,
  provisioning, installation, cache lock, manifest, worker and archive leaves,
  472 passed (after one lifecycle CPU overrun of the bundle round-trip
  property test, now 8 examples on the in-memory `tmp_path`).
- Native record: the recorder with `--milestone step-5`, after the edits of
  the covered sources (`cache.py`, `cache_lock.py`, `installation.py`,
  `provisioning.py`, `download_worker.py`), passed 14 of 14 and the stalled
  runner timeout demonstration; the evidence leaf accepts the record on the
  final sources.
- Default walk: `ghog day --whole-suite` exit 0. Earlier walks stopped at
  check (typing of JSON test helpers, magic values, a pairwise loop, two
  grade C tests, now split) and at the affected tests (the `read_only_git`
  stand-in without the new `stream` keyword, now updated).
- Review validation, `ghog day --full=speed --whole-suite` (built-in default,
  no `.review-validation`): exit 0 with `cov=100 outliers=0 excluded=0
  proof=speed`, 8057 tests, slowest call 0.31 s (outside this step), on index
  tree `70dbca4a6e5a6af9d1a28c1643d5ead9ab4083b5`. No budget was changed and
  no exclusion is accepted.
- `rg -n 'manifest' tools/release_workflow/git_cliff/harness.py
  tools/release_workflow/git_cliff/comparison.py
  tools/release_workflow/git_cliff/candidates.py`: docstrings and the import
  of `PLATFORM_TRIPLE` and `asset_url`, reads only.
  `rg -n 'pragma: no cover' tools/release_workflow/git_cliff`: only the
  harness `if __name__ == "__main__":` line.
- Line counts: `candidates.py` 432, `fixture_history.py` 225,
  `comparison.py` 291, `bundle.py` 546, `harness.py` 301, `git.py` 348;
  every Python file below 550; the advisory overruns are recorded as
  variance in the validation plan.
- Markdown check and cSpell on the validation plan: clean.

Architecture: candidates reach the cache, lock, worker, archive check,
extraction, probe, guard and invocation only through
`provisioning.provision_target` and an `InstallTarget`; production keeps
`manifest_target`, with unchanged behavior. Git stays one boundary, with the
input stream as its parameter. The harness is the only composition root
(`HarnessContext`); the other modules take every resource as a parameter.
Performance: linear in cases, hunks, entries and output bytes; the ranges take
one pass over each listing; `difflib` runs only where outputs differ, which
the plan's complexity bound allows for this by-hand harness. Feature
integrity: production provisioning, the reuse check, `GitExecutionContext.run`
without input and the worker's outcome line are unchanged; the manifest still
admits no pin.

Please check in particular: `InstallTarget` and `manifest_target` keeping
production identical; the acceptance of `candidates` (record under the lock,
listing on a first acquisition, `before_publish` timing); the non-reusable
first acquisition; `run_comparison`'s worktree cleanup; the strict bundle
reader and the review binding; and the harness's rerun path (ranges, fixture
hashes, digests).

### Implementation report for step 6 git-cliff-provisioning (round 1)

Step 6, "Compatibility evidence harness", is the sixth of eight steps of the
git-cliff-provisioning plan. It ships the internal comparison modules the
evidence run of Step 7 uses by hand; nothing in a release, a build or a
`gcliff` call imports them, and the manifest still admits no pin.

Git input stream, `tools/release_workflow/git.py` (plan decision Q09):

- `GitExecutionContext.run(arguments, *, cwd, check=True, input=None)`:
  given bytes go through `subprocess.run(input=...)` without `stdin`; without
  them the existing stdin rule applies. `_execute` takes them as `stream`, and
  a new `_spawn` holds both process starts. The `read_only_git` stand-in in
  `tests/unit/tools/release_workflow/conftest.py` accepts the new keyword.

Provisioning of any install target (Step 3 to 5 modules):

- `installation.InstallTarget` (frozen): version, triple, asset, size,
  member, URL, `accept(archive) -> sha256` (a `VerificationError` is the
  verification stage), `before_publish()` (run after the entry record is
  written and the owner file removed, before retirement and publication),
  `reusable` and `entry_asset`. `install(layout, target, budget, seams,
  lock)` uses the target everywhere the pin was used. `manifest_target(pin)`
  keeps production exactly: verify against the manifest size and digest,
  record the manifest digest, nothing before publication, reusable, no
  archive comparison on reuse.
- `provisioning.provision_target(layout, target, budget, *, seams, caller)`
  runs the unchanged flow in the layout's namespace; `provision` calls it with
  `manifest_target(pin)` in production. A non-reusable target skips the
  lock-free check and the recheck under the lock (`_reuse`).
- `cache.check_entry(..., asset_sha256=None)`: when given, the record's
  `asset_sha256` must equal it, compared after the record read and before the
  hash, so the candidate order is archive digest, executable, probe.
- `archive.archive_identity(path)` (SHA-256 and size of a staged file, used
  by `verify_archive`) and the narrower `ArchiveMember` protocol of
  `extract_member`; `download_worker.outcome_fields(stdout)`, the parent's
  reading of the outcome line, now used by the installation;
  `cache_lock.publish_file`, the former private `_publish`;
  `manifest.asset_url(version, asset)`, behind `download_url`.
- The native record is refreshed at milestone `step-5` (14 of 14 passed),
  since `cache.py`, `cache_lock.py`, `installation.py`, `provisioning.py`
  and `download_worker.py` are covered sources.

Fixture history, `tools/release_workflow/git_cliff/fixture_history.py`
(design "Frozen inputs and the coverage matrix", Q14):

- 20 declared commits and four annotated tags (`v0.1.0`, `v0.2.0-SNAPSHOT`,
  `v0.2.0`, `v0.3.0-SNAPSHOT`, in `TAGS`); one merge; messages for every
  group and skip rule of the dev_workflow `cliff.toml`, a breaking change, a
  fix whose body matches the security parser, a revert and an unconventional
  commit.
- `stream()`: commits with `deleteall` and every file inline, `from` and
  `merge` in parent order, author and committer with fixed dates and two
  zones; tags with tagger, date, zone and message; `done` at the end.
- `environment(source, global_config)`, `build(git, directory)` (`init
  --quiet --template= --object-format=sha1 --initial-branch=main`, then
  `fast-import --quiet --done` with the stream as input, then `for-each-ref
  --format=%(refname)%00%(objectname) refs/heads/main refs/tags`, each with
  `CONFIG`), `FixtureHashes` and `verify`.

Comparison, `tools/release_workflow/git_cliff/comparison.py` (design
"Frozen inputs and the coverage matrix", "Outputs and classification", Q13):

- `FrozenInputs` (pin, baseline, llm-shared commit, `CliffToml`, fixture
  hashes, ranges, `CandidateIdentity` values, `FLAGS`, `ENVIRONMENT`),
  `RangeCase`, `RunDigest`, `CaseResult` (hunk identifiers `<case> #<n>`),
  `ComparisonResult`, `Workspace`.
- `history_ranges(git, *, cwd, revision, repository)`: `rev-list
  --topo-order --reverse` and the tag records reachable from the revision,
  ordered in one pass; full history, consecutive pairs, last tag to HEAD.
- `run_environment(source, home)`; `run_comparison(inputs, invocations, git,
  workspace)`: `worktree add --detach` of the frozen commit with
  `core.hooksPath` on an empty directory, baseline then pin per case through a
  fresh invocation each (`-c <bundle copy> -w <directory> -s footer --
  [range]`, engine policy, captured output, `RUN_SECONDS` = 120), worktree
  removed and `worktree prune` in `finally`; `differing_hunks` (unified diff,
  three lines of context, line endings kept); `verify_rerun`.

Candidates, `tools/release_workflow/git_cliff/candidates.py` (design
"Candidate lifecycle and admission order", "Candidate cache"; plan decision
Q19):

- `parse_listing(version, metadata)` and `AssetListing`; `Candidate` with its
  validation; `EVIDENCE_ONLY_VERSIONS`, `UPSTREAM_DIGEST`,
  `EVIDENCE_ONLY_HTTPS` and `TRUST_BASIS` (the evidence-only basis states the
  authorization of 2026-11-13 and that HTTPS anchored the first download).
- `TrustRecord(path, version)`: `read`, `require`, `write_once` (through
  `publish_file` without replacement; an existing record is a
  `CandidateError`, never rewritten) and `compare(received)` (a
  `VerificationError` naming the record).
- `acquire_candidate(tooling_root, version, budget, seams, *, trust_path)`:
  an existing record is the identity (`provision_candidate`); otherwise the
  metadata worker (`WorkerRequest(mode="metadata")`, record-free, expiring 60
  s after it started, one retry after 5 s for a retryable failure), the trust
  kind decided before any download, and `provision_target` in the evidence
  namespace with a non-reusable target whose acceptance compares with the
  listed size and published digest and writes the record in
  `before_publish`; a record found under the lock is compared instead.
- `provision_candidate(...)`: target with `entry_asset` = the recorded digest;
  its acceptance compares every new download with the record.

Bundle, `tools/release_workflow/git_cliff/bundle.py` (design "Outputs and
classification", "Statuses"; plan decision Q16):

- `Bundle` and its parts; strict `read` (via `lock_records.decode_object`,
  then each member's form, then the listed file digests) and `write`;
  `canonical_projection`, `with_review`, `refreshed`; `require_complete` and
  `require_admissible` as listed in the validation plan. The default location
  is `tools/release_workflow/git_cliff/bundles/<pin>`; `pins` defaults to the
  shipped `ADMITTED_PINS`.

Harness, `tools/release_workflow/git_cliff/harness.py` (design "The
harness", Q15):

- `main(arguments, *, context=None)`, `HarnessContext`,
  `production_context()`, `evidence_git(source, *, checkout, temporary)`.
  A comparison: budget once, existing bundle of the same pair, baseline then
  pin acquired, fixture built and verified, inputs frozen (HEAD commit,
  `rev-parse <commit>:tools/dev_workflow`, `cat-file blob
  <submodule>:cliff.toml` in the submodule, copied into the bundle) or reused
  with the same ranges, comparison, `verify_rerun`, `write` with
  `refreshed`. A review: `with_review` over the current bundle and today's
  local date. Expected failures print one diagnostic and return 2.

Tests: `git_cliff_harness_fake.py` (new), the children fake (metadata role,
versions from cache paths, evidence namespace, `run_output`), the support
module (any version), and the leaves `test_git_cliff_fixture`,
`test_git_cliff_comparison`, `test_git_cliff_candidates` (acquisition and
records), `test_git_cliff_bundle` (model, review binding, property test) and
`test_git_cliff_harness`, plus additions to `test_git`, the cache,
provisioning, worker and archive leaves.

Also staged: the validation plan's Step 6 sections and the
`git_cliff/__init__.py` docstring.

Writer notes: `.reviews/a.git-cliff-provisioning.step6.journal.md` and
`.reviews/a.git-cliff-provisioning.step6.handoff.md`.

### Change summary for step 6 git-cliff-provisioning (round 1)

Staged paths (38), grouped in the root `a.commit` (nine groups, checker
`ready: true`):

1. `feat(release): give Git an input stream`:
   `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/conftest.py`.
2. `refactor(release): provision any install target`:
   `tools/release_workflow/git_cliff/archive.py`,
   `tools/release_workflow/git_cliff/cache.py`,
   `tools/release_workflow/git_cliff/cache_lock.py`,
   `tools/release_workflow/git_cliff/download_worker.py`,
   `tools/release_workflow/git_cliff/manifest.py`,
   `tools/release_workflow/git_cliff/installation.py`,
   `tools/release_workflow/git_cliff/provisioning.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
3. `feat(release): build the snapshot-tag fixture`:
   `tools/release_workflow/git_cliff/fixture_history.py`.
4. `feat(release): compare two git-cliff versions`:
   `tools/release_workflow/git_cliff/comparison.py`.
5. `feat(release): acquire git-cliff evidence candidates`:
   `tools/release_workflow/git_cliff/candidates.py`.
6. `feat(release): add the reviewed evidence bundle`:
   `tools/release_workflow/git_cliff/bundle.py`.
7. `test(release): cover the evidence modules`:
   `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`, and the
   `test_git_cliff_fixture`, `test_git_cliff_comparison`,
   `test_git_cliff_candidates` and `test_git_cliff_bundle` leaves with their
   `__init__.py` files. The shared harness fake imports all four modules, so
   their tests follow them.
8. `feat(release): run the evidence harness by hand`:
   `tools/release_workflow/git_cliff/harness.py`,
   `tools/release_workflow/git_cliff/__init__.py`, and the
   `test_git_cliff_harness` leaf with its `__init__.py`.
9. `docs(git-cliff-provisioning): record step 6 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 5 of this plan are committed and pushed (`1cfda502` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` stays unstaged
for the residual commit.

### Writer response for step 6 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 6 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- Candidates reuse the Step 5 flow instead of a copy of it: `InstallTarget`
  carries the acceptance and the hook a candidate needs, and
  `manifest_target(pin)` keeps production behavior unchanged. This edits
  covered sources, so the native record was rerun at `step-5`.
- The release metadata is read before the candidate lock, not under it as the
  plan's step list reads: the listing is needed to size the download and
  writes nothing. The trust record is read, compared and written only under
  the lock, inside the acceptance, so a record another acquisition wrote while
  this one waited is compared and kept.
- A first acquisition is never reusable: without a trust record no cached
  entry can be tied to a record, and reusing one would skip the record write.
- Signatures that differ in shape from the plan's list: `TrustRecord(path,
  version).write_once(candidate)` and `.compare(received)` (a record object
  instead of path arguments), `provision_candidate(..., *, trust_path)`,
  `run_comparison(inputs, invocations, git, workspace)` (the directories and
  the explicit environment), `read(directory)` and `write(directory, bundle)`,
  `require_admissible(bundle, *, location=None, pins=ADMITTED_PINS)` with
  `require_complete` holding the completeness checks, and `main(arguments, *,
  context=None)`. `invocations` maps each version to a provider of fresh
  invocation objects, since an invocation is single-use.
- A tampered listed file is refused by `read`, the only way a committed
  bundle is loaded, rather than again by `require_admissible`.
- The pin's trust must be `upstream-digest` for completeness: admission must
  rest on upstream integrity data.
- Ranges are recomputed on every run and must equal the bundle's on a rerun,
  so a new or moved tag fails instead of silently changing the cases.
- `harness.py` has its own test leaf, which the plan's file list lacks, so it
  reaches full coverage on its own.
- The fixture Git environment drops every inherited `GIT_*` and points
  `GIT_CONFIG_GLOBAL` at an empty file the harness writes in its temporary
  directory; no hook can run because `init --template=` creates none and no
  configuration names one. The worktree add passes `core.hooksPath` on an
  empty directory, since llm-shared's own repository configuration still
  applies there.
- Hunks keep line endings, so a carriage return or a missing last line feed is
  a visible difference rather than an empty hunk beside two differing
  digests.

### Reviewer focus for step 6 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-1 -->

## Round 1 by reviewer - Step 6

- Recorded: 2026-11-20T19:31:18+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: 70dbca4a6e5a6af9d1a28c1643d5ead9ab4083b5

Assessed index tree: ba674bb30cb20e905c59f5b38fd4c087ccd00517

### Implementation check for step 6 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 6 has NOT been fully implemented.

The Git input stream, fixture generator, canonical review digest and write-once trust publication are present. Production still verifies the admitted manifest target. Six findings affect the evidence harness.

Validation plan effects:

Updated the Step 6 verdict and added six missing-work items immediately after the implementation section.

### Pre-repair mandatory checks and coverage for step 6 git-cliff-provisioning (exchange 1) (round 1)

The writer reports 8,057 tests, 100% coverage, a green speed walk, and 14 passing native checks. The independent focused run on the bound whole scope returned exit 0 with zero failures and warnings. The round log was newer than its start marker. The static review identified missing behavioral cases in the areas listed below.

### Resolved validation set and sources for step 6 git-cliff-provisioning (exchange 1) (round 1)

Both request and Step 6 resolver select `ghog day --full=speed --whole-suite` from the project default.

### Resolver drift and direction for step 6 git-cliff-provisioning (exchange 1) (round 1)

None.

### Repository state around validation for step 6 git-cliff-provisioning (exchange 1) (round 1)

Request and baseline index `70dbca4a6e5a6af9d1a28c1643d5ead9ab4083b5`. Assessed index `ba674bb30cb20e905c59f5b38fd4c087ccd00517`. The ordered comparison identified the reviewer’s Step 6 validation metadata and the ignored focused log. The umbrella digest matched before and after.

### Repair inventory for step 6 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md` (review metadata only).

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`

### Commit plan assessment for step 6 git-cliff-provisioning (exchange 1) (round 1)

Independent `commit-plan-check.bat --format json` returned exit 0, state `valid`, ready `true` and zero diagnostics. The 38 staged paths are listed once across the nine ordered groups below.

1. `feat(release): give Git an input stream` covers `tools/release_workflow/git.py`, `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`, `tests/unit/tools/release_workflow/conftest.py`.
2. `refactor(release): provision any install target` covers `tools/release_workflow/git_cliff/archive.py`, `tools/release_workflow/git_cliff/cache.py`, `tools/release_workflow/git_cliff/cache_lock.py`, `tools/release_workflow/git_cliff/download_worker.py`, `tools/release_workflow/git_cliff/manifest.py`, `tools/release_workflow/git_cliff/installation.py`, `tools/release_workflow/git_cliff/provisioning.py`, `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
3. `feat(release): build the snapshot-tag fixture` covers `tools/release_workflow/git_cliff/fixture_history.py`.
4. `feat(release): compare two git-cliff versions` covers `tools/release_workflow/git_cliff/comparison.py`.
5. `feat(release): acquire git-cliff evidence candidates` covers `tools/release_workflow/git_cliff/candidates.py`.
6. `feat(release): add the reviewed evidence bundle` covers `tools/release_workflow/git_cliff/bundle.py`.
7. `test(release): cover the evidence modules` covers `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`, `tests/unit/tools/release_workflow/git_cliff_children_fake.py`, `tests/unit/tools/release_workflow/git_cliff_support.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py`.
8. `feat(release): run the evidence harness by hand` covers `tools/release_workflow/git_cliff/harness.py`, `tools/release_workflow/git_cliff/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py`.
9. `docs(git-cliff-provisioning): record step 6 validation` covers `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

### Findings and boundaries for step 6 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- **The admission check accepts an unsupported exclusion of status 69.** `bundle.py:478` checks only the revision shape and `excludes_69`. Empty commands, categories and observations pass, as does an observation of 69 alongside that assertion. Require the audit commands, source references and findings for the design’s exit-path categories, the required corroborating observations, and consistency with the recorded statuses. Cover absent evidence and contradictory status 69 in the admission tests.
- **The bundle can certify candidate identities and a matrix its files do not substantiate.** `bundle.py:395` hashes the trust files without decoding them. The passing sample uses one-field trust files that the real `TrustRecord` rejects. `_inputs_problem` accepts one range and `_outputs_problem` accepts the same reduced list. Require two distinct candidates, reconcile each real trust record with the recorded identity, and validate full-history and required fixture ranges and tag hashes. Reject missing cases, duplicate cases and a manifest identity that differs from the reviewed candidate.
- **A rerun can silently substitute frozen inputs.** `harness.py:224–232` restores the commit and configuration descriptor but reconstructs the candidate identities, flags and environment names. `fixture_history.verify` visits only the recorded tags. If an executable digest changes while output stays identical, the rerun succeeds and rewrites the bundle. Compare the complete recorded inputs with the actual run, including the copied configuration bytes and exact fixture hashes, before rendering or writing. Test input drift with identical output and verify the prior bundle survives.
- **Worktree cleanup can leave a registration in the shared checkout.** `comparison.py:269–275` creates the worktree before entering `try`, suppresses filesystem deletion errors and ignores a failed Git prune. Cover partial creation and Windows removal failures. Remove the specific registered worktree through Git, verify cleanup and surface cleanup errors while preserving the original comparison failure.
- **First acquisition permits a transport downgrade.** `candidates.py` uses the default redirect handling from `network.build_opener` for metadata and archives. Python’s standard redirect handler permits a redirect from HTTPS to HTTP. The 2.7.0 first download has no upstream digest, so its trust assertion requires certificate-verified HTTPS on every hop. Enforce that requirement before following redirects and cover it with offline adapter tests for metadata and archive acquisition.
- **Concurrent first callers can retire a just-published valid candidate.** `candidates.py:428` fixes `reusable=False` before locking. A waiter that now has a trust record still downloads and tries to retire the winner’s entry, which can fail while the winner holds its Windows use guard. Re-read trust and check for a matching reusable entry under the lock. Bind the returned guard to the verified entry before another publisher can replace it. Exercise the interleaving with the first invocation still open and assert one installation and an unchanged trust record.

Boundary-crossing work: None.

### Writer instructions for step 6 git-cliff-provisioning (exchange 1) (round 1)

Address all six missing-work items in the Step 6 validation plan, add focused regression cases and refresh validation and native evidence for any covered sources that change. Publish the updated index for round 2.

### Decision rationale for step 6 git-cliff-provisioning (exchange 1) (round 1)

Identity passes. Implementation completeness fails. Focused validation passes and the writer reports full measured coverage, but static test assessment finds gaps. Staged attribution passes. Six findings remain open. The mechanical commit-plan check passes. Changes are requested.

### Final reviewer decision for step 6 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-1 -->

## Round 2 by requestor - Step 6

- Recorded: 2026-11-20T20:10:31+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 6
Review round: 2

### Code review evidence for step 6 git-cliff-provisioning (round 2)

request_index_tree: 95f36ab5176c36b77e29e1cdad3ef051a6e11d59
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): give Git an input stream
group 1 path: tools/release_workflow/git.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/conftest.py
group 2: fix(release): follow redirects only to HTTPS
group 2 path: tools/release_workflow/git_cliff/network.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
group 2 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 3: refactor(release): provision any install target
group 3 path: tools/release_workflow/git_cliff/archive.py
group 3 path: tools/release_workflow/git_cliff/cache.py
group 3 path: tools/release_workflow/git_cliff/cache_lock.py
group 3 path: tools/release_workflow/git_cliff/download_worker.py
group 3 path: tools/release_workflow/git_cliff/manifest.py
group 3 path: tools/release_workflow/git_cliff/installation.py
group 3 path: tools/release_workflow/git_cliff/provisioning.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4: feat(release): build the snapshot-tag fixture
group 4 path: tools/release_workflow/git_cliff/fixture_history.py
group 5: feat(release): compare two git-cliff versions
group 5 path: tools/release_workflow/git_cliff/comparison.py
group 6: feat(release): acquire git-cliff evidence candidates
group 6 path: tools/release_workflow/git_cliff/candidates.py
group 7: feat(release): add the reviewed evidence bundle
group 7 path: tools/release_workflow/git_cliff/bundle.py
group 8: test(release): cover the evidence modules
group 8 path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
group 8 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
group 8 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
group 9: feat(release): run the evidence harness by hand
group 9 path: tools/release_workflow/git_cliff/harness.py
group 9 path: tools/release_workflow/git_cliff/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
group 10: docs(git-cliff-provisioning): record step 6 validation
group 10 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/archive.py
staged path: tools/release_workflow/git_cliff/bundle.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
staged path: tools/release_workflow/git_cliff/candidates.py
staged path: tools/release_workflow/git_cliff/comparison.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/fixture_history.py
staged path: tools/release_workflow/git_cliff/harness.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/git_cliff/network.py
staged path: tools/release_workflow/git_cliff/provisioning.py
```

### Validation scope for step 6 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 6 git-cliff-provisioning (round 2)

Writer assessment for Step 6 of the git-cliff-provisioning plan, round 2: the
step is fully implemented after the round 1 repairs, and the rerun
implementation check records `Yes. Step 6 has been fully implemented.` in the
staged validation plan (the reviewer's round 1 missing-work list is done and
removed; the document status stays `No, it is not implemented.` while Steps
7 and 8 are not started).

Evidence, all on the staged tree:

- Round 1 repairs, each through its leaf: the bundle leaf covers every audit
  and observation gap (no command, missing, repeated or empty category,
  blank reference or finding, no exclusion, missing observation, observed
  69, failing success, passing failure), one version for both candidates, a
  missing full history, a broken chain, a duplicate or missing case, other
  fixture tags, a manifest entry with another digest, and the trust record
  reconciliation on read (another identity, an invalid record); the harness
  leaf an executable drift with identical outputs and changed `cliff.toml`
  bytes, both failing before any run with the bundle unchanged; the fixture
  leaf tags missing from either side; the comparison leaf a partial
  creation, a refused removal, cleanup problems noted on a run failure and a
  Git that cannot list; the network leaf HTTP, uppercase HTTP and FTP
  redirects refused for an archive and for release metadata; the candidates
  leaf the concurrent first acquisition, with one download and no
  retirement; the provisioning leaf a target allowing no reuse.
  `ghog single` on the repaired leaves: 433 passed.
- Native record: the recorder with `--milestone step-5`, after the edits of
  the covered sources `network.py`, `installation.py` and `provisioning.py`,
  passed 14 of 14 and the stalled runner timeout demonstration.
- Default walk: `ghog day --whole-suite` exit 0 after splitting two grade C
  checks of `bundle.py` and two typing fixes in the tests.
- Review validation, `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed`, 8090 tests,
  slowest call 0.31 s (outside this step), on index tree
  `95f36ab5176c36b77e29e1cdad3ef051a6e11d59`. No budget was changed and no
  exclusion is accepted.
- `rg -n 'manifest'` on the harness, comparison and candidates modules: reads
  only. `rg -n 'pragma: no cover' tools/release_workflow/git_cliff`: only the
  harness entry line.
- Line counts: `bundle.py` 622 (550 to 650 band, below the ceiling),
  `candidates.py` 442, `comparison.py` 341, `harness.py` 318,
  `fixture_history.py` 235, `network.py` 170; every other Python file below
  550.
- Markdown check and cSpell on the validation plan and the transcript: clean
  (the word `deleteall` added to the project and user dictionaries).

Architecture: the HTTPS-only rule lives in the network adapter; the reuse
decision is the target's own function, asked by the flow at each check; the
cleanup and its verification stay in the comparison. Performance: one trust
record read per reuse check, three more Git calls and one listing pass per
comparison, linear completeness checks (sets and counters). Feature
integrity: production downloads now refuse a redirect off HTTPS as a fatal
failure; GitHub's redirect stays on HTTPS.

Please check in particular: `_matrix_complete` and `chained_ranges`;
`_audit_problem` and `_observation_problem`; `_reconcile` in `read`;
`_require_frozen` in the harness; `_removal_problems` and `_clean` with the
original failure kept; `_HttpsRedirects`; and `_Flow._reuse` with the
candidate's `reusable_asset` under the lock.

### Implementation report for step 6 git-cliff-provisioning (round 2)

Step 6, "Compatibility evidence harness", is the sixth of eight steps of the
git-cliff-provisioning plan. It ships the internal comparison modules the
evidence run of Step 7 uses by hand; nothing in a release, a build or a
`gcliff` call imports them, and the manifest still admits no pin.

Git input stream, `tools/release_workflow/git.py` (plan decision Q09):

- `GitExecutionContext.run(arguments, *, cwd, check=True, input=None)`:
  given bytes go through `subprocess.run(input=...)` without `stdin`; without
  them the existing stdin rule applies. `_execute` takes them as `stream`, and
  a new `_spawn` holds both process starts. The `read_only_git` stand-in in
  `tests/unit/tools/release_workflow/conftest.py` accepts the new keyword.

Provisioning of any install target (Step 3 to 5 modules):

- `installation.InstallTarget` (frozen): version, triple, asset, size,
  member, URL, `accept(archive) -> sha256` (a `VerificationError` is the
  verification stage), `before_publish()` (run after the entry record is
  written and the owner file removed, before retirement and publication)
  and `reuse`, a function asked before each reuse check for the archive
  digest a reused entry must record (None allows no reuse at that check;
  production has no function and compares no archive digest). `install(layout, target, budget, seams,
  lock)` uses the target everywhere the pin was used. `manifest_target(pin)`
  keeps production exactly: verify against the manifest size and digest,
  record the manifest digest, nothing before publication, reusable, no
  archive comparison on reuse.
- `provisioning.provision_target(layout, target, budget, *, seams, caller)`
  runs the unchanged flow in the layout's namespace; `provision` calls it with
  `manifest_target(pin)` in production. `_reuse` asks the target's function
  before the lock-free check and again before the recheck under the lock.
- `cache.check_entry(..., asset_sha256=None)`: when given, the record's
  `asset_sha256` must equal it, compared after the record read and before the
  hash, so the candidate order is archive digest, executable, probe.
- `archive.archive_identity(path)` (SHA-256 and size of a staged file, used
  by `verify_archive`) and the narrower `ArchiveMember` protocol of
  `extract_member`; `download_worker.outcome_fields(stdout)`, the parent's
  reading of the outcome line, now used by the installation;
  `cache_lock.publish_file`, the former private `_publish`;
  `manifest.asset_url(version, asset)`, behind `download_url`.
- The native record is refreshed at milestone `step-5` (14 of 14 passed),
  since `cache.py`, `cache_lock.py`, `installation.py`, `provisioning.py`
  and `download_worker.py` are covered sources.

Fixture history, `tools/release_workflow/git_cliff/fixture_history.py`
(design "Frozen inputs and the coverage matrix", Q14):

- 20 declared commits and four annotated tags (`v0.1.0`, `v0.2.0-SNAPSHOT`,
  `v0.2.0`, `v0.3.0-SNAPSHOT`, in `TAGS`); one merge; messages for every
  group and skip rule of the dev_workflow `cliff.toml`, a breaking change, a
  fix whose body matches the security parser, a revert and an unconventional
  commit.
- `stream()`: commits with `deleteall` and every file inline, `from` and
  `merge` in parent order, author and committer with fixed dates and two
  zones; tags with tagger, date, zone and message; `done` at the end.
- `environment(source, global_config)`, `build(git, directory)` (`init
  --quiet --template= --object-format=sha1 --initial-branch=main`, then
  `fast-import --quiet --done` with the stream as input, then `for-each-ref
  --format=%(refname)%00%(objectname) refs/heads/main refs/tags`, each with
  `CONFIG`), `FixtureHashes` and `verify`.

Comparison, `tools/release_workflow/git_cliff/comparison.py` (design
"Frozen inputs and the coverage matrix", "Outputs and classification", Q13):

- `FrozenInputs` (pin, baseline, llm-shared commit, `CliffToml`, fixture
  hashes, ranges, `CandidateIdentity` values, `FLAGS`, `ENVIRONMENT`),
  `RangeCase`, `RunDigest`, `CaseResult` (hunk identifiers `<case> #<n>`),
  `ComparisonResult`, `Workspace`.
- `history_ranges(git, *, cwd, revision, repository)`: `rev-list
  --topo-order --reverse` and the tag records reachable from the revision,
  ordered in one pass; full history, consecutive pairs, last tag to HEAD.
- `run_environment(source, home)`; `run_comparison(inputs, invocations, git,
  workspace)`: `worktree add --detach` of the frozen commit with
  `core.hooksPath` on an empty directory, baseline then pin per case through a
  fresh invocation each (`-c <bundle copy> -w <directory> -s footer --
  [range]`, engine policy, captured output, `RUN_SECONDS` = 120), worktree
  removed and `worktree prune` in `finally`; `differing_hunks` (unified diff,
  three lines of context, line endings kept); `verify_rerun`.

Candidates, `tools/release_workflow/git_cliff/candidates.py` (design
"Candidate lifecycle and admission order", "Candidate cache"; plan decision
Q19):

- `parse_listing(version, metadata)` and `AssetListing`; `Candidate` with its
  validation; `EVIDENCE_ONLY_VERSIONS`, `UPSTREAM_DIGEST`,
  `EVIDENCE_ONLY_HTTPS` and `TRUST_BASIS` (the evidence-only basis states the
  authorization of 2026-11-13 and that HTTPS anchored the first download).
- `TrustRecord(path, version)`: `read`, `require`, `write_once` (through
  `publish_file` without replacement; an existing record is a
  `CandidateError`, never rewritten) and `compare(received)` (a
  `VerificationError` naming the record).
- `acquire_candidate(tooling_root, version, budget, seams, *, trust_path)`:
  an existing record is the identity (`provision_candidate`); otherwise the
  metadata worker (`WorkerRequest(mode="metadata")`, record-free, expiring 60
  s after it started, one retry after 5 s for a retryable failure), the trust
  kind decided before any download, and `provision_target` in the evidence
  namespace with a target whose acceptance compares with the listed size and
  published digest and writes the record in `before_publish`; a record
  found under the lock is compared instead, and the reuse function reads the
  record before each check, so a published matching entry is reused.
- `provision_candidate(...)`: the same target with the record present; its
  acceptance compares every new download with the record.

Bundle, `tools/release_workflow/git_cliff/bundle.py` (design "Outputs and
classification", "Statuses"; plan decision Q16):

- `Bundle` and its parts; strict `read` (via `lock_records.decode_object`,
  then each member's form, then the listed file digests) and `write`;
  `canonical_projection`, `with_review`, `refreshed`; `require_complete` and
  `require_admissible` as listed in the validation plan. The default location
  is `tools/release_workflow/git_cliff/bundles/<pin>`; `pins` defaults to the
  shipped `ADMITTED_PINS`.

Harness, `tools/release_workflow/git_cliff/harness.py` (design "The
harness", Q15):

- `main(arguments, *, context=None)`, `HarnessContext`,
  `production_context()`, `evidence_git(source, *, checkout, temporary)`.
  A comparison: budget once, existing bundle of the same pair, baseline then
  pin acquired, fixture built and verified, inputs frozen (HEAD commit,
  `rev-parse <commit>:tools/dev_workflow`, `cat-file blob
  <submodule>:cliff.toml` in the submodule, copied into the bundle) or reused
  and compared field by field, with the copied `cliff.toml` bytes, before
  any run, comparison, `verify_rerun`, `write` with `refreshed`. A review: `with_review` over the current bundle and today's
  local date. Expected failures print one diagnostic and return 2.

Tests: `git_cliff_harness_fake.py` (new), the children fake (metadata role,
versions from cache paths, evidence namespace, `run_output`), the support
module (any version), and the leaves `test_git_cliff_fixture`,
`test_git_cliff_comparison`, `test_git_cliff_candidates` (acquisition and
records), `test_git_cliff_bundle` (model, review binding, property test) and
`test_git_cliff_harness`, plus additions to `test_git`, the cache,
provisioning, worker and archive leaves.

Also staged: the validation plan's Step 6 sections and the
`git_cliff/__init__.py` docstring.

Code review round 1 repairs (round 2 of this exchange):

- `bundle.py`: audit evidence (`AUDIT_CATEGORIES`, commands, references,
  findings) and observations (`OBSERVATIONS`, no 69, consistent statuses);
  trust record reconciliation in `read`; two distinct versions, the full
  matrix (`comparison.chained_ranges`), the fixture's tags, and the manifest
  identity in `require_complete`. 622 lines.
- `harness.py`: complete frozen-input comparison and copied `cliff.toml`
  bytes before any run; the temporary directory resolved to its long form.
- `fixture_history.verify`: every tag of either side, in order.
- `comparison.py`: `worktree add` inside the guarded block; cleanup through
  `worktree remove --force`, deletion, prune and a verifying listing; cleanup
  problems fail a successful run or are noted on the failure raised.
- `network.py`: HTTPS-only redirect handler, `InsecureRedirectError` (fatal);
  `git_cliff_support.CannedWeb.opener` now builds on the network opener.
- `installation.InstallTarget.reuse` replaces `reusable` and `entry_asset`;
  `provisioning._reuse` asks it before each check; `candidates` gives the
  trust record's digest read at that moment, and `trust_record_bytes`.
- Native record refreshed at `step-5` after the covered-source edits, 14 of
  14 passed.
- Tests: the bundle, comparison, fixture, candidates, harness, network and
  provisioning leaves, and the harness fake's samples (full matrix, real
  trust records, complete audit) and declared Git failures per action.

Writer notes: `.reviews/a.git-cliff-provisioning.step6.journal.md` and
`.reviews/a.git-cliff-provisioning.step6.handoff.md`.

### Change summary for step 6 git-cliff-provisioning (round 2)

Staged paths (40), grouped in the root `a.commit` (ten groups, checker
`ready: true`). Round 2 adds `tools/release_workflow/git_cliff/network.py` and
`tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
grouped with `tests/unit/tools/release_workflow/git_cliff_support.py` in a new
second group:

1. `feat(release): give Git an input stream`: `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS`:
   `tools/release_workflow/git_cliff/network.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target`: `archive.py`,
   `cache.py`, `cache_lock.py`, `download_worker.py`, `manifest.py`,
   `installation.py`, `provisioning.py` (all in
   `tools/release_workflow/git_cliff/`), the archive, cache, worker and
   provisioning test files, and `native_checks.v1.json`.
4. `feat(release): build the snapshot-tag fixture`: `fixture_history.py`.
5. `feat(release): compare two git-cliff versions`: `comparison.py`.
6. `feat(release): acquire git-cliff evidence candidates`: `candidates.py`.
7. `feat(release): add the reviewed evidence bundle`: `bundle.py`.
8. `test(release): cover the evidence modules`: `git_cliff_harness_fake.py`,
   `git_cliff_children_fake.py`, and the fixture, comparison, candidates and
   bundle leaves with their `__init__.py` files.
9. `feat(release): run the evidence harness by hand`: `harness.py`,
   `git_cliff/__init__.py`, and the harness leaf with its `__init__.py`.
10. `docs(git-cliff-provisioning): record step 6 validation`:
    `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 5 of this plan are committed and pushed (`1cfda502` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and
`.vscode/settings.json` (the new cSpell word `deleteall` the transcript
needs) stay unstaged for the residual commit.

### Writer response for step 6 git-cliff-provisioning (round 2)

Writer response:

Writer response:

All six round 1 findings are accepted and repaired; there is no
disagreement. The reviewer's staged edit of the validation plan was kept as
the basis of the rerun implementation check, which now records `Yes. Step 6
has been fully implemented.` with the repairs; its missing-work list is done
and removed.

1. Unsupported exclusion of 69: `bundle._audit_problem` requires the audit's
   revision, at least one non-blank command, each of `AUDIT_CATEGORIES`
   (error return, argument-parsing errors, propagated helper statuses, panics
   and abnormal termination) exactly once with non-blank references and a
   finding, and `excludes_69`; `_observation_problem` requires the observed
   success, usage error and failing render with their commands, refuses any
   observed 69, a success other than 0 and a failure reported as 0. The bundle
   leaf covers each absence and contradiction.
2. Identities and matrix: `read` decodes both trust records with
   `TrustRecord` and refuses one whose asset, size, digest or trust differs
   from the candidate identity of the inputs, or that is not a valid record;
   the sample bundle now carries real trust records. `require_complete`
   refuses one version for both candidates, ranges that are not llm-shared's
   full history and chained tag ranges then exactly the fixture's
   (`comparison.chained_ranges`, the rule `history_ranges` uses, so a missing
   or duplicate case is refused), fixture tags other than `TAGS`, and a
   manifest entry of the pin that does not name this bundle with the reviewed
   asset, size and digest.
3. Rerun substitution: before any git-cliff run, the harness compares every
   field of the frozen inputs it observes (candidate identities and
   executable digests, flags and environment names included) and the digest
   of the copied `cliff.toml` with the bundle's, and fails naming the changed
   fields; the bundle keeps its bytes. `fixture_history.verify` compares the
   branch and every tag of either side in order. The harness leaf covers an
   executable drift with identical outputs and changed `cliff.toml` bytes.
4. Worktree registration: `worktree add` runs inside the guarded block; the
   cleanup runs `worktree remove --force <path>`, deletes what is left,
   prunes, and lists the worktrees to verify the path is no longer
   registered. Any problem (a refused deletion, a failed prune, a still
   registered or unlistable worktree, a Git that cannot run) fails a
   successful comparison, or is added as a note to the failure already
   raised, which keeps propagating. The harness's temporary directory is
   resolved to its long form, the form Git lists. The comparison leaf covers
   a partial creation, a refused removal, notes on a run failure and a Git
   that cannot list.
5. Transport downgrade: `network.build_opener` installs an HTTPS-only redirect
   handler; a redirect to HTTP, any case, or another scheme raises
   `InsecureRedirectError` before it is opened, which `classify` treats as
   fatal. This holds for every download and metadata lookup, production
   included; GitHub's redirect to its asset host stays on HTTPS. The network
   leaf covers an archive (no target created) and release metadata; the
   canned opener is now the network module's own, with the canned handler
   added.
6. Concurrent first callers: `InstallTarget.reuse` is now a function the flow
   asks before each reuse check, the recheck under the lock included, for the
   archive digest a reused entry must record (None allows no reuse at that
   check). A candidate's reads its trust record each time, so a waiter whose
   record another first acquisition wrote checks and reuses that published
   entry with its own guard instead of downloading and retiring it. The
   candidates leaf plays the interleaving with the first invocation still
   open: one download, no retirement, the record written once.

Covered sources changed again (`network.py`, `installation.py`,
`provisioning.py`), so the recorder was rerun at `step-5`: 14 of 14 passed.
`bundle.py` grew to 622 lines, in the 550 to 650 band, below the ceiling;
the checks stay in the module the plan names. The new cSpell word
`deleteall` (fast-import's command, quoted in the round 1 request of the
transcript) is in the project dictionary, which joins the residual commit
with the transcript.

### Reviewer focus for step 6 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-2 -->

## Round 2 by reviewer - Step 6

- Recorded: 2026-11-20T20:17:55+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 95f36ab5176c36b77e29e1cdad3ef051a6e11d59

Assessed index tree: 26585e932a1560acfbf79e9e440aab4575091b54

### Implementation check for step 6 git-cliff-provisioning (exchange 1) (round 2)

Result:

No. Step 6 has NOT been fully implemented.

The HTTPS redirect restriction covers metadata and archives. Reruns compare all frozen fields, the copied configuration bytes and the complete fixture hashes before comparison. Bundle reads reconcile both trust files, and admission checks fixture ranges, distinct versions, audit categories and the manifest identity. Partial worktree creation is cleaned up, and a waiter using the same trust record can reuse the winner. The four findings below remain open.

Validation plan effects:

Updated the Step 6 verdict and recorded four actionable cases under `Missing work for Step 6`.

### Pre-repair mandatory checks and coverage for step 6 git-cliff-provisioning (exchange 1) (round 2)

The writer reports 8,090 tests, `cov=100 outliers=0 excluded=0 proof=speed`, exit 0, on the request tree. The native record passed 14 of 14 checks. The reviewer’s independent `ghog affected --no-cov` using the exchange scope returned exit 0, zero failures and zero warnings. Static review found four missing behavioral cases.

### Resolved validation set and sources for step 6 git-cliff-provisioning (exchange 1) (round 2)

The request and the independent Step 6 resolver both select `ghog day --full=speed --whole-suite` from the project default.

### Resolver drift and direction for step 6 git-cliff-provisioning (exchange 1) (round 2)

None.

### Repository state around validation for step 6 git-cliff-provisioning (exchange 1) (round 2)

The request and baseline index both identify `95f36ab5176c36b77e29e1cdad3ef051a6e11d59`. The assessed tree is `26585e932a1560acfbf79e9e440aab4575091b54`. The ordered comparison found the attributable Step 6 validation edit, its index effect and the ignored focused-run log. The umbrella digest matched.

### Repair inventory for step 6 git-cliff-provisioning (exchange 1) (round 2)

Repairs made:

- Updated the reviewed step’s validation metadata.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`

### Commit plan assessment for step 6 git-cliff-provisioning (exchange 1) (round 2)

The independent checker returned `valid`, ready `true`, with 10 ordered groups covering all 40 staged paths. Diagnostics were empty.

1. `feat(release): give Git an input stream` groups `tools/release_workflow/git.py`, `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`, `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS` groups `tools/release_workflow/git_cliff/network.py`, `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`, `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target` groups `tools/release_workflow/git_cliff/archive.py`, `tools/release_workflow/git_cliff/cache.py`, `tools/release_workflow/git_cliff/cache_lock.py`, `tools/release_workflow/git_cliff/download_worker.py`, `tools/release_workflow/git_cliff/manifest.py`, `tools/release_workflow/git_cliff/installation.py`, `tools/release_workflow/git_cliff/provisioning.py`, `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
4. `feat(release): build the snapshot-tag fixture` groups `tools/release_workflow/git_cliff/fixture_history.py`.
5. `feat(release): compare two git-cliff versions` groups `tools/release_workflow/git_cliff/comparison.py`.
6. `feat(release): acquire git-cliff evidence candidates` groups `tools/release_workflow/git_cliff/candidates.py`.
7. `feat(release): add the reviewed evidence bundle` groups `tools/release_workflow/git_cliff/bundle.py`.
8. `test(release): cover the evidence modules` groups `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`, `tests/unit/tools/release_workflow/git_cliff_children_fake.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py`.
9. `feat(release): run the evidence harness by hand` groups `tools/release_workflow/git_cliff/harness.py`, `tools/release_workflow/git_cliff/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py`.
10. `docs(git-cliff-provisioning): record step 6 validation` groups `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

### Findings and boundaries for step 6 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings:

- **Check every recorded pin status.** In `bundle.py`, `_observation_problem` collapses observations by name before inspecting their statuses. A later success can hide an earlier status 69 or a contradictory success status. `_outputs_problem` also ignores the pin's status on comparison cases. Check each observation and each pin result against the exclusion, and check each named observation for consistency. Add admission tests with a current review for a repeated observation and a pin comparison returning 69.
- **Verify the llm-shared ranges against the frozen history.** `_matrix_complete` infers the expected tags from the submitted ranges. Full history alone passes for llm-shared when the fixture matrix is complete, even when the frozen commit has reachable release tags. Skipping an intermediate tag or repeating a tag can also produce a self-consistent chain. Bind the expected ordered, unique llm-shared tags to the frozen revision independently of the range list. Test omitted and repeated project ranges with matching output rows.
- **Report cleanup failures at the harness entry point.** `comparison._clean` attaches the worktree cleanup diagnostic to the primary exception with `add_note`. `harness.main` prints only the exception text, so the operator sees the comparison failure and misses the cleanup failure and worktree path. Preserve the primary diagnostic and report its cleanup notes on stderr. Exercise both failures together through `harness.main` and verify the exit status and both messages.
- **Bind the fresh installation to the returned use guard.** `_Flow._locked` releases the version lock after `install`, and `_Flow.run` then opens the executable by path. Different bundle directories share the evidence cache but have independent trust records, so another installation can replace that path during the gap. Acquire the guard while publication is still protected, or revalidate the guarded entry against the caller's verified identity. Add a deterministic two-bundle concurrency test covering this interval and checking the identity held by the first invocation.

Boundary-crossing work: None.

### Writer instructions for step 6 git-cliff-provisioning (exchange 1) (round 2)

Complete the four items under `Missing work for Step 6`. Exercise admission with a current review, the normal harness stderr path, and separate bundle trust records. Refresh the writer’s validation evidence on the resulting index.

### Decision rationale for step 6 git-cliff-provisioning (exchange 1) (round 2)

Identity passes for Step 6, round 2, occurrence 1. Completeness fails on four behaviors. The focused check and writer’s coverage evidence pass, and static inspection finds missing regression cases, so the validation and coverage criterion remains open. Staged attribution passes. Four carried findings remain open. The independent commit-plan check passes. The disposition is `changes-requested`.

### Final reviewer decision for step 6 git-cliff-provisioning (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-6-round-2 -->

## Round 3 by requestor - Step 6

- Recorded: 2026-11-20T21:03:00+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 6
Review round: 3

### Code review evidence for step 6 git-cliff-provisioning (round 3)

request_index_tree: 95ce496729582667f2373b1e4c9511e7991c9ba6
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): give Git an input stream
group 1 path: tools/release_workflow/git.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/conftest.py
group 2: fix(release): follow redirects only to HTTPS
group 2 path: tools/release_workflow/git_cliff/network.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
group 2 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 3: refactor(release): provision any install target
group 3 path: tools/release_workflow/git_cliff/archive.py
group 3 path: tools/release_workflow/git_cliff/cache.py
group 3 path: tools/release_workflow/git_cliff/cache_lock.py
group 3 path: tools/release_workflow/git_cliff/download_worker.py
group 3 path: tools/release_workflow/git_cliff/manifest.py
group 3 path: tools/release_workflow/git_cliff/installation.py
group 3 path: tools/release_workflow/git_cliff/provisioning.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4: feat(release): build the snapshot-tag fixture
group 4 path: tools/release_workflow/git_cliff/fixture_history.py
group 5: feat(release): compare two git-cliff versions
group 5 path: tools/release_workflow/git_cliff/comparison.py
group 6: feat(release): acquire git-cliff evidence candidates
group 6 path: tools/release_workflow/git_cliff/candidates.py
group 7: feat(release): add the reviewed evidence bundle
group 7 path: tools/release_workflow/git_cliff/bundle.py
group 8: feat(release): check a bundle before admission
group 8 path: tools/release_workflow/git_cliff/bundle_checks.py
group 9: test(release): cover the evidence modules
group 9 path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
group 9 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py
group 10: feat(release): run the evidence harness by hand
group 10 path: tools/release_workflow/git_cliff/harness.py
group 10 path: tools/release_workflow/git_cliff/__init__.py
group 10 path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
group 10 path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
group 11: docs(git-cliff-provisioning): record step 6 validation
group 11 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/archive.py
staged path: tools/release_workflow/git_cliff/bundle.py
staged path: tools/release_workflow/git_cliff/bundle_checks.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
staged path: tools/release_workflow/git_cliff/candidates.py
staged path: tools/release_workflow/git_cliff/comparison.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/fixture_history.py
staged path: tools/release_workflow/git_cliff/harness.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/git_cliff/network.py
staged path: tools/release_workflow/git_cliff/provisioning.py
```

### Validation scope for step 6 git-cliff-provisioning (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 6 git-cliff-provisioning (round 3)

Writer assessment for Step 6 of the git-cliff-provisioning plan, round 3: the
step is fully implemented after the round 2 repairs, and the rerun
implementation check records `Yes. Step 6 has been fully implemented.` in the
staged validation plan (the reviewer's round 2 missing-work list is done and
removed; the document status stays `No, it is not implemented.` while Steps
7 and 8 are not started).

Evidence, all on the staged tree:

- Round 2 repairs, each through its leaf: the new bundle checks leaf covers,
  with a current approved review, a repeated success hiding a 69 and one
  hiding a status 1, and a pin comparison returning 69; a skipped tag, a
  repeated tag and full history alone with tags recorded, each with matching
  output rows; the harness leaf a comparison failure and a worktree cleanup
  note printed together through `harness.main` (status 2, both messages, no
  bundle) and the recorded llm-shared tags of a first run; the comparison
  leaf `history_tags`; the candidates leaf two bundles with different trust
  records sharing the evidence cache, the second acquisition run at the
  first caller's lock release and refused at the in-use stage, the first
  invocation keeping the verified bytes. `ghog single` on the bundle, bundle
  checks, candidates, comparison, harness, provisioning and installation
  leaves: 281 passed.
- Native record: the recorder with `--milestone step-5`, after the edit of
  the covered source `provisioning.py`, passed 14 of 14 and the stalled
  runner timeout demonstration.
- Default walk: `ghog day --whole-suite` exit 0 after splitting one grade C
  check (`_observation_issue` out of `_observation_problem`).
- Review validation, `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed`, 8097 tests,
  slowest call 0.32 s (outside this step), on index tree
  `95ce496729582667f2373b1e4c9511e7991c9ba6`. A first speed walk on an
  earlier tree failed on CPU only: two tests of
  `tests/unit/tools/shared_lifecycle/test_audit_declarations` (outside this
  step, passing in focus) and the bundle round-trip property test, whose
  examples rebuilt the synthetic archives; `sample_candidate` in the harness
  fake is now cached (deterministic archive, frozen identity), the focused
  rerun with `--full=speed` passed, and the walk above passed. No budget was
  changed and no exclusion is accepted.
- `rg -n 'manifest'` on the harness, comparison, candidates and bundle checks
  modules: reads only (`bundle_checks` reads `ADMITTED_PINS`).
  `rg -n 'pragma: no cover' tools/release_workflow/git_cliff`: only the
  harness entry line.
- Line counts: `bundle.py` 451 and `bundle_checks.py` 233 (split from the 639
  lines the round 2 checks reached), `candidates.py` 442, `comparison.py`
  346, `harness.py` 327, `provisioning.py` 349, `fixture_history.py` 235;
  every Python file below 550.
- Markdown check and cSpell on the validation plan and the transcript: clean.

Architecture: `bundle` keeps the model, its strict codec and the review
binding; `bundle_checks` holds the admission rules and depends on `bundle`,
never the reverse; the recorded tags come from the comparison's Git reads,
and the guard is opened by the provisioning flow under its own lock.
Performance: one more pass over `rev-list` and the tag listing per
comparison (the one `history_ranges` already made), linear checks per
observation and per case. Feature integrity: production provisioning now
guards a freshly published entry before it releases the lock, with the same
ready line and stages; the guard is closed if the release fails.

Please check in particular: `_observation_issue` and `_outputs_problem`;
`_matrix_complete` with `FrozenInputs.llm_shared_tags` and
`comparison.history_tags`; `harness.main` printing the notes; `_Flow._locked`
guarding before `_release`; and the two-bundle test in the candidates leaf.

### Implementation report for step 6 git-cliff-provisioning (round 3)

Step 6, "Compatibility evidence harness", is the sixth of eight steps of the
git-cliff-provisioning plan. It ships the internal comparison modules the
evidence run of Step 7 uses by hand; nothing in a release, a build or a
`gcliff` call imports them, and the manifest still admits no pin.

Git input stream, `tools/release_workflow/git.py` (plan decision Q09):

- `GitExecutionContext.run(arguments, *, cwd, check=True, input=None)`:
  given bytes go through `subprocess.run(input=...)` without `stdin`; without
  them the existing stdin rule applies. `_execute` takes them as `stream`, and
  a new `_spawn` holds both process starts. The `read_only_git` stand-in in
  `tests/unit/tools/release_workflow/conftest.py` accepts the new keyword.

Provisioning of any install target (Step 3 to 5 modules):

- `installation.InstallTarget` (frozen): version, triple, asset, size,
  member, URL, `accept(archive) -> sha256` (a `VerificationError` is the
  verification stage), `before_publish()` (run after the entry record is
  written and the owner file removed, before retirement and publication)
  and `reuse`, a function asked before each reuse check for the archive
  digest a reused entry must record (None allows no reuse at that check;
  production has no function and compares no archive digest). `install(layout, target, budget, seams,
  lock)` uses the target everywhere the pin was used. `manifest_target(pin)`
  keeps production exactly: verify against the manifest size and digest,
  record the manifest digest, nothing before publication, reusable, no
  archive comparison on reuse.
- `provisioning.provision_target(layout, target, budget, *, seams, caller)`
  runs the unchanged flow in the layout's namespace; `provision` calls it with
  `manifest_target(pin)` in production. `_reuse` asks the target's function
  before the lock-free check and again before the recheck under the lock.
- `cache.check_entry(..., asset_sha256=None)`: when given, the record's
  `asset_sha256` must equal it, compared after the record read and before the
  hash, so the candidate order is archive digest, executable, probe.
- `archive.archive_identity(path)` (SHA-256 and size of a staged file, used
  by `verify_archive`) and the narrower `ArchiveMember` protocol of
  `extract_member`; `download_worker.outcome_fields(stdout)`, the parent's
  reading of the outcome line, now used by the installation;
  `cache_lock.publish_file`, the former private `_publish`;
  `manifest.asset_url(version, asset)`, behind `download_url`.
- The native record is refreshed at milestone `step-5` (14 of 14 passed),
  since `cache.py`, `cache_lock.py`, `installation.py`, `provisioning.py`
  and `download_worker.py` are covered sources.

Fixture history, `tools/release_workflow/git_cliff/fixture_history.py`
(design "Frozen inputs and the coverage matrix", Q14):

- 20 declared commits and four annotated tags (`v0.1.0`, `v0.2.0-SNAPSHOT`,
  `v0.2.0`, `v0.3.0-SNAPSHOT`, in `TAGS`); one merge; messages for every
  group and skip rule of the dev_workflow `cliff.toml`, a breaking change, a
  fix whose body matches the security parser, a revert and an unconventional
  commit.
- `stream()`: commits with `deleteall` and every file inline, `from` and
  `merge` in parent order, author and committer with fixed dates and two
  zones; tags with tagger, date, zone and message; `done` at the end.
- `environment(source, global_config)`, `build(git, directory)` (`init
  --quiet --template= --object-format=sha1 --initial-branch=main`, then
  `fast-import --quiet --done` with the stream as input, then `for-each-ref
  --format=%(refname)%00%(objectname) refs/heads/main refs/tags`, each with
  `CONFIG`), `FixtureHashes` and `verify`.

Comparison, `tools/release_workflow/git_cliff/comparison.py` (design
"Frozen inputs and the coverage matrix", "Outputs and classification", Q13):

- `FrozenInputs` (pin, baseline, llm-shared commit, `CliffToml`, fixture
  hashes, ranges, `CandidateIdentity` values, `FLAGS`, `ENVIRONMENT`),
  `RangeCase`, `RunDigest`, `CaseResult` (hunk identifiers `<case> #<n>`),
  `ComparisonResult`, `Workspace`.
- `history_ranges(git, *, cwd, revision, repository)`: `rev-list
  --topo-order --reverse` and the tag records reachable from the revision,
  ordered in one pass; full history, consecutive pairs, last tag to HEAD.
- `run_environment(source, home)`; `run_comparison(inputs, invocations, git,
  workspace)`: `worktree add --detach` of the frozen commit with
  `core.hooksPath` on an empty directory, baseline then pin per case through a
  fresh invocation each (`-c <bundle copy> -w <directory> -s footer --
  [range]`, engine policy, captured output, `RUN_SECONDS` = 120), worktree
  removed and `worktree prune` in `finally`; `differing_hunks` (unified diff,
  three lines of context, line endings kept); `verify_rerun`.

Candidates, `tools/release_workflow/git_cliff/candidates.py` (design
"Candidate lifecycle and admission order", "Candidate cache"; plan decision
Q19):

- `parse_listing(version, metadata)` and `AssetListing`; `Candidate` with its
  validation; `EVIDENCE_ONLY_VERSIONS`, `UPSTREAM_DIGEST`,
  `EVIDENCE_ONLY_HTTPS` and `TRUST_BASIS` (the evidence-only basis states the
  authorization of 2026-11-13 and that HTTPS anchored the first download).
- `TrustRecord(path, version)`: `read`, `require`, `write_once` (through
  `publish_file` without replacement; an existing record is a
  `CandidateError`, never rewritten) and `compare(received)` (a
  `VerificationError` naming the record).
- `acquire_candidate(tooling_root, version, budget, seams, *, trust_path)`:
  an existing record is the identity (`provision_candidate`); otherwise the
  metadata worker (`WorkerRequest(mode="metadata")`, record-free, expiring 60
  s after it started, one retry after 5 s for a retryable failure), the trust
  kind decided before any download, and `provision_target` in the evidence
  namespace with a target whose acceptance compares with the listed size and
  published digest and writes the record in `before_publish`; a record
  found under the lock is compared instead, and the reuse function reads the
  record before each check, so a published matching entry is reused.
- `provision_candidate(...)`: the same target with the record present; its
  acceptance compares every new download with the record.

Bundle, `tools/release_workflow/git_cliff/bundle.py` (design "Outputs and
classification", "Statuses"; plan decision Q16):

- `Bundle` and its parts; strict `read` (via `lock_records.decode_object`,
  then each member's form, then the listed file digests) and `write`;
  `canonical_projection`, `covered_sha256`, `with_review`, `refreshed`;
  `require_complete` and `require_admissible` as listed in the validation
  plan, in `bundle_checks.py` since round 3 of this exchange. The default location
  is `tools/release_workflow/git_cliff/bundles/<pin>`; `pins` defaults to the
  shipped `ADMITTED_PINS`.

Harness, `tools/release_workflow/git_cliff/harness.py` (design "The
harness", Q15):

- `main(arguments, *, context=None)`, `HarnessContext`,
  `production_context()`, `evidence_git(source, *, checkout, temporary)`.
  A comparison: budget once, existing bundle of the same pair, baseline then
  pin acquired, fixture built and verified, inputs frozen (HEAD commit,
  `rev-parse <commit>:tools/dev_workflow`, `cat-file blob
  <submodule>:cliff.toml` in the submodule, copied into the bundle) or reused
  and compared field by field, with the copied `cliff.toml` bytes, before
  any run, comparison, `verify_rerun`, `write` with `refreshed`. A review: `with_review` over the current bundle and today's
  local date. Expected failures print one diagnostic and return 2.

Tests: `git_cliff_harness_fake.py` (new), the children fake (metadata role,
versions from cache paths, evidence namespace, `run_output`), the support
module (any version), and the leaves `test_git_cliff_fixture`,
`test_git_cliff_comparison`, `test_git_cliff_candidates` (acquisition and
records), `test_git_cliff_bundle` (model, review binding, property test) and
`test_git_cliff_harness`, plus additions to `test_git`, the cache,
provisioning, worker and archive leaves.

Also staged: the validation plan's Step 6 sections and the
`git_cliff/__init__.py` docstring.

Code review round 1 repairs (round 2 of this exchange):

- `bundle.py`: audit evidence (`AUDIT_CATEGORIES`, commands, references,
  findings) and observations (`OBSERVATIONS`, no 69, consistent statuses);
  trust record reconciliation in `read`; two distinct versions, the full
  matrix (`comparison.chained_ranges`), the fixture's tags, and the manifest
  identity in `require_complete`. 622 lines.
- `harness.py`: complete frozen-input comparison and copied `cliff.toml`
  bytes before any run; the temporary directory resolved to its long form.
- `fixture_history.verify`: every tag of either side, in order.
- `comparison.py`: `worktree add` inside the guarded block; cleanup through
  `worktree remove --force`, deletion, prune and a verifying listing; cleanup
  problems fail a successful run or are noted on the failure raised.
- `network.py`: HTTPS-only redirect handler, `InsecureRedirectError` (fatal);
  `git_cliff_support.CannedWeb.opener` now builds on the network opener.
- `installation.InstallTarget.reuse` replaces `reusable` and `entry_asset`;
  `provisioning._reuse` asks it before each check; `candidates` gives the
  trust record's digest read at that moment, and `trust_record_bytes`.
- Native record refreshed at `step-5` after the covered-source edits, 14 of
  14 passed.
- Tests: the bundle, comparison, fixture, candidates, harness, network and
  provisioning leaves, and the harness fake's samples (full matrix, real
  trust records, complete audit) and declared Git failures per action.

Code review round 2 repairs (round 3 of this exchange):

- `bundle_checks.py` (new, 233 lines): the admission rules split from
  `bundle.py`, which keeps the model, the strict codec and the review
  binding (451 lines, `covered_sha256` now public). `_observation_issue`
  checks each observation on its own before the presence check;
  `_outputs_problem` refuses a pin result of 69; `_matrix_complete` requires
  llm-shared's recorded tags once each and the ranges to be exactly their
  chain, then the fixture's.
- `comparison.py`: `history_tags(git, *, cwd, revision)` gives each tag
  reachable from the revision with its commit, in history order, in one
  pass; `FrozenInputs.llm_shared_tags` records them; the bundle encodes them
  as a list of `{name, commit}`.
- `harness.py`: `_inputs` records the tags and chains llm-shared's ranges
  from them; `main` prints each note of a failure after its diagnostic.
- `provisioning.py`: `_locked` guards the published entry before releasing
  the lock and closes the guard when the release fails; `run` prints the
  ready line only for an installation.
- Native record refreshed at `step-5` after the edit of `provisioning.py`,
  14 of 14 passed.
- Tests: the new bundle checks leaf (completeness and admissibility, with
  the round 2 regressions), the bundle leaf reduced to storage and binding,
  the candidates leaf's two-bundle guard test, the harness leaf's cleanup
  note and recorded tags, the comparison leaf's `history_tags`; the harness
  fake's sample inputs record one llm-shared tag.

Writer notes: `.reviews/a.git-cliff-provisioning.step6.journal.md` and
`.reviews/a.git-cliff-provisioning.step6.handoff.md`.

### Change summary for step 6 git-cliff-provisioning (round 3)

Staged paths (44), grouped in the root `a.commit` (eleven groups, checker
`ready: true`). Round 3 adds `tools/release_workflow/git_cliff/bundle_checks.py`
in its own group after the bundle, and the new leaf
`tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/` (three
files) in the test group:

1. `feat(release): give Git an input stream`: `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS`:
   `tools/release_workflow/git_cliff/network.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target`: `archive.py`,
   `cache.py`, `cache_lock.py`, `download_worker.py`, `manifest.py`,
   `installation.py`, `provisioning.py` (all in
   `tools/release_workflow/git_cliff/`), the archive, cache, worker and
   provisioning test files, and `native_checks.v1.json`; round 3 adds the
   guard opened before the lock release.
4. `feat(release): build the snapshot-tag fixture`: `fixture_history.py`.
5. `feat(release): compare two git-cliff versions`: `comparison.py`, with
   `history_tags` and `FrozenInputs.llm_shared_tags`.
6. `feat(release): acquire git-cliff evidence candidates`: `candidates.py`.
7. `feat(release): add the reviewed evidence bundle`: `bundle.py` (model,
   strict codec, review binding).
8. `feat(release): check a bundle before admission`: `bundle_checks.py`.
9. `test(release): cover the evidence modules`: `git_cliff_harness_fake.py`,
   `git_cliff_children_fake.py`, and the fixture, comparison, candidates,
   bundle and bundle checks leaves with their `__init__.py` files.
10. `feat(release): run the evidence harness by hand`: `harness.py`,
    `git_cliff/__init__.py`, and the harness leaf with its `__init__.py`.
11. `docs(git-cliff-provisioning): record step 6 validation`:
    `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 5 of this plan are committed and pushed (`1cfda502` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and
`.vscode/settings.json` (the cSpell word `deleteall` the transcript needs)
stay unstaged for the residual commit.

### Writer response for step 6 git-cliff-provisioning (round 3)

Writer response:

Writer response:

All four round 2 findings are accepted and repaired; there is no
disagreement. The reviewer's staged edit of the validation plan was kept as
the basis of the rerun implementation check, which again records `Yes. Step 6
has been fully implemented.` with the round 2 repairs; its missing-work list
is done and removed.

1. Every recorded pin status: `bundle_checks._observation_issue` checks each
   observation on its own, in the recorded order, before any grouping by
   name: a 69, a blank command, a success other than 0 and a usage error or
   failing render reported as 0 are each refused, so a later observation of
   the same name hides nothing; the presence of each of `OBSERVATIONS` is
   checked after. `_outputs_problem` refuses a comparison case where the pin
   returned 69. The bundle checks leaf covers, with a current approved
   review, a repeated success hiding a 69 and one hiding a status 1, and a
   pin comparison returning 69.
2. llm-shared ranges bound to the frozen history: `FrozenInputs` now records
   `llm_shared_tags`, each tag reachable from the frozen commit with its
   commit, in history order (`comparison.history_tags`, one pass over
   `rev-list` and the tag listing). Completeness requires each recorded tag
   once and the ranges to be exactly `chained_ranges` of the recorded tags,
   then exactly the fixture's, so full history alone, an omitted or a
   repeated tag are refused even with matching output rows. A rerun compares
   the recorded tags with the ones Git reports, field by field, before any
   run. The bundle checks leaf covers a skipped tag, a repeated tag and full
   history alone with tags recorded, each with matching outputs; the harness
   leaf the recorded tags of a first run; the comparison leaf
   `history_tags`.
3. Cleanup failures at the entry point: `harness.main` prints the failure's
   diagnostic, then each note it carries, on standard error with the harness
   prefix, and returns 2. The harness leaf runs a comparison whose git-cliff
   run does not end with a worktree still registered after its removal:
   status 2, the comparison failure first, then the cleanup note naming the
   worktree path, and no bundle written.
4. Fresh installation bound to the guard: `_Flow._locked` now opens the use
   guard of the entry it just published while the version lock is still
   held, then releases the lock; the guard is closed if the release fails.
   An entry that cannot be guarded keeps the extraction stage of plan Q18.
   The candidates leaf plays two bundles sharing the evidence cache with
   different trust records for the baseline: the second bundle's
   acquisition runs the moment the first caller's lock record is removed,
   and is refused at the in-use stage because the first invocation already
   holds its guard; the executable keeps the bytes the first caller
   verified.

To keep `bundle.py` below the 550 to 650 band after these checks grew it to
639 lines, the admission rules (`require_complete`, `require_admissible` and
their checks, `KINDS`, `AUDIT_CATEGORIES`, `OBSERVATIONS`) moved to the new
`tools/release_workflow/git_cliff/bundle_checks.py` (233 lines), with
`covered_sha256` made public in `bundle` (451 lines); their tests moved to the
new leaf `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/`.
This deviates from the plan's `bundle.require_admissible` name only by
module; the validation plan records it. Step 7 imports it from
`bundle_checks`.

`provisioning.py` changed again, so the recorder was rerun at `step-5`: 14
of 14 passed. The guard order change is recorded under feature integrity:
production provisioning now guards a fresh entry before releasing the lock,
with the same ready line and stages.

### Reviewer focus for step 6 git-cliff-provisioning (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-3 -->

## Round 3 by reviewer - Step 6

- Recorded: 2026-11-20T21:13:54+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 git-cliff-provisioning (exchange 1) (round 3)

Baseline index tree: 95ce496729582667f2373b1e4c9511e7991c9ba6

Assessed index tree: 95ce496729582667f2373b1e4c9511e7991c9ba6

### Implementation check for step 6 git-cliff-provisioning (exchange 1) (round 3)

Result:

Yes. Step 6 has been fully implemented.

Each raw observation and each pin comparison result is now checked for status 69. The harness captures ordered tag names and commits from Git at the frozen revision, and bundle admission checks the range matrix against that inventory. Regression tests cover hidden statuses and missing or repeated ranges with matching outputs. The harness CLI reports both the primary comparison error and the worktree cleanup note. Fresh installation acquires its use guard under the version lock. The two-bundle regression verifies the first caller still holds its verified bytes when a competing installation attempts retirement.

Validation plan effects:

The writer’s Step 6 verdict and implementation notes already describe the repairs and the move of admission checks to `bundle_checks.py`. The earlier work list is complete.

### Pre-repair mandatory checks and coverage for step 6 git-cliff-provisioning (exchange 1) (round 3)

The writer reports 8,097 tests with `cov=100 outliers=0 excluded=0 proof=speed`, exit 0 on the request tree, and 14 of 14 native checks. The reviewer’s independent `ghog affected --no-cov` with the exchange scope completed with zero failures and warnings. The coverage gate measures `tools` with its configured exclusions. The staged regression tests exercise the four previously missing behaviors.

### Resolved validation set and sources for step 6 git-cliff-provisioning (exchange 1) (round 3)

The request and independent Step 6 resolver both select `ghog day --full=speed --whole-suite` from the project default.

### Resolver drift and direction for step 6 git-cliff-provisioning (exchange 1) (round 3)

None.

### Repository state around validation for step 6 git-cliff-provisioning (exchange 1) (round 3)

The request, baseline and assessed tree are `95ce496729582667f2373b1e4c9511e7991c9ba6`. The ordered comparison reports only the ignored focused-run log. The umbrella digest matches. Git's default whitespace check flags the CRLF endings in `bundle_checks.py`. Its check with CRLF recognized as a line ending passes.

### Repair inventory for step 6 git-cliff-provisioning (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 git-cliff-provisioning (exchange 1) (round 3)

The independent checker returned `valid`, ready `true`, with 11 ordered groups covering all 44 staged paths. Diagnostics were empty. The admission rules follow the storage model they import.

1. `feat(release): give Git an input stream` groups `tools/release_workflow/git.py`, `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`, `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS` groups `tools/release_workflow/git_cliff/network.py`, `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`, `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target` groups `tools/release_workflow/git_cliff/archive.py`, `tools/release_workflow/git_cliff/cache.py`, `tools/release_workflow/git_cliff/cache_lock.py`, `tools/release_workflow/git_cliff/download_worker.py`, `tools/release_workflow/git_cliff/manifest.py`, `tools/release_workflow/git_cliff/installation.py`, `tools/release_workflow/git_cliff/provisioning.py`, `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
4. `feat(release): build the snapshot-tag fixture` groups `tools/release_workflow/git_cliff/fixture_history.py`.
5. `feat(release): compare two git-cliff versions` groups `tools/release_workflow/git_cliff/comparison.py`.
6. `feat(release): acquire git-cliff evidence candidates` groups `tools/release_workflow/git_cliff/candidates.py`.
7. `feat(release): add the reviewed evidence bundle` groups `tools/release_workflow/git_cliff/bundle.py`.
8. `feat(release): check a bundle before admission` groups `tools/release_workflow/git_cliff/bundle_checks.py`.
9. `test(release): cover the evidence modules` groups `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`, `tests/unit/tools/release_workflow/git_cliff_children_fake.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py`.
10. `feat(release): run the evidence harness by hand` groups `tools/release_workflow/git_cliff/harness.py`, `tools/release_workflow/git_cliff/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py`.
11. `docs(git-cliff-provisioning): record step 6 validation` groups `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

### Findings and boundaries for step 6 git-cliff-provisioning (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 6 git-cliff-provisioning (exchange 1) (round 3)

The human commit decision can proceed on the assessed tree.

### Decision rationale for step 6 git-cliff-provisioning (exchange 1) (round 3)

All six readiness checks pass for Step 6, round 3, occurrence 1. The request matches the index, implementation is complete, validation and measured coverage pass, staging is attributable to the writer, all carried findings are closed, and the commit plan covers the staged paths. The move of the admission API to `bundle_checks` is documented and its consumers use that module. The recommendation is `commit-ready`.

### Final reviewer decision for step 6 git-cliff-provisioning (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-3 -->

## Round 3 by human - Step 6 - human-confirmation

- Recorded: 2026-11-20T21:30:50+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Rework and review again
Outcome: another-round
Guidance: Rework and review again: normalize `tools/release_workflow/git_cliff/bundle_checks.py`
to LF line endings, the only CRLF file among the staged paths (flagged by
Git's default whitespace check in the round 3 answer). Line endings only, no
content change; validate on the new tree and review it in round 4.

<!-- review-entry-id: human-confirmation-round-3 -->

## Round 4 by requestor - Step 6

- Recorded: 2026-11-20T21:40:54+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: request

### Review identity for step 6 git-cliff-provisioning (round 4)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 6
Review round: 4

### Code review evidence for step 6 git-cliff-provisioning (round 4)

request_index_tree: 19c9b249b649246e667c35a49a618aba8e5f412a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): give Git an input stream
group 1 path: tools/release_workflow/git.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/conftest.py
group 2: fix(release): follow redirects only to HTTPS
group 2 path: tools/release_workflow/git_cliff/network.py
group 2 path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
group 2 path: tests/unit/tools/release_workflow/git_cliff_support.py
group 3: refactor(release): provision any install target
group 3 path: tools/release_workflow/git_cliff/archive.py
group 3 path: tools/release_workflow/git_cliff/cache.py
group 3 path: tools/release_workflow/git_cliff/cache_lock.py
group 3 path: tools/release_workflow/git_cliff/download_worker.py
group 3 path: tools/release_workflow/git_cliff/manifest.py
group 3 path: tools/release_workflow/git_cliff/installation.py
group 3 path: tools/release_workflow/git_cliff/provisioning.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 4: feat(release): build the snapshot-tag fixture
group 4 path: tools/release_workflow/git_cliff/fixture_history.py
group 5: feat(release): compare two git-cliff versions
group 5 path: tools/release_workflow/git_cliff/comparison.py
group 6: feat(release): acquire git-cliff evidence candidates
group 6 path: tools/release_workflow/git_cliff/candidates.py
group 7: feat(release): add the reviewed evidence bundle
group 7 path: tools/release_workflow/git_cliff/bundle.py
group 8: feat(release): check a bundle before admission
group 8 path: tools/release_workflow/git_cliff/bundle_checks.py
group 9: test(release): cover the evidence modules
group 9 path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
group 9 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py
group 9 path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py
group 10: feat(release): run the evidence harness by hand
group 10 path: tools/release_workflow/git_cliff/harness.py
group 10 path: tools/release_workflow/git_cliff/__init__.py
group 10 path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
group 10 path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
group 11: docs(git-cliff-provisioning): record step 6 validation
group 11 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/conftest.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_harness_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_support.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/archive.py
staged path: tools/release_workflow/git_cliff/bundle.py
staged path: tools/release_workflow/git_cliff/bundle_checks.py
staged path: tools/release_workflow/git_cliff/cache.py
staged path: tools/release_workflow/git_cliff/cache_lock.py
staged path: tools/release_workflow/git_cliff/candidates.py
staged path: tools/release_workflow/git_cliff/comparison.py
staged path: tools/release_workflow/git_cliff/download_worker.py
staged path: tools/release_workflow/git_cliff/fixture_history.py
staged path: tools/release_workflow/git_cliff/harness.py
staged path: tools/release_workflow/git_cliff/installation.py
staged path: tools/release_workflow/git_cliff/manifest.py
staged path: tools/release_workflow/git_cliff/network.py
staged path: tools/release_workflow/git_cliff/provisioning.py
```

### Validation scope for step 6 git-cliff-provisioning (round 4)

Validation scope: the whole suite.

### Requestor assessment for step 6 git-cliff-provisioning (round 4)

Writer assessment for Step 6 of the git-cliff-provisioning plan, round 4: a
replacement round the user asked for at the round 3 convergence gate, for line
endings only. Step 6 stays fully implemented: the staged validation plan
records `Yes. Step 6 has been fully implemented.`, unchanged since round 3.

Change since the round 3 assessed tree
`95ce496729582667f2373b1e4c9511e7991c9ba6`: `tools/release_workflow/git_cliff/bundle_checks.py`
converted from CRLF to LF line endings. `git diff 95ce4967 19c9b249` touches
only that file, and `git diff --ignore-cr-at-eol 95ce4967 19c9b249` is empty.
`git diff --cached --check` is clean, and `git ls-files --eol` reports no
staged `i/crlf` file.

Evidence, on the staged tree:

- Review validation, `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed`, 8097 tests,
  slowest call 0.31 s (outside this step), on index tree
  `19c9b249b649246e667c35a49a618aba8e5f412a`. No budget was changed and no
  exclusion is accepted.
- No covered source of the native record changed, so the step-5 record
  (14 of 14) stands.
- The readiness checker reports `valid`, ready `true`, 11 groups and 44
  staged paths; `a.commit` is unchanged since round 3.
- Markdown check and cSpell on the validation plan and the transcript: clean.

Please confirm that the only change is the line endings of `bundle_checks.py`.

### Implementation report for step 6 git-cliff-provisioning (round 4)

Step 6, "Compatibility evidence harness", is the sixth of eight steps of the
git-cliff-provisioning plan. It ships the internal comparison modules the
evidence run of Step 7 uses by hand; nothing in a release, a build or a
`gcliff` call imports them, and the manifest still admits no pin.

Git input stream, `tools/release_workflow/git.py` (plan decision Q09):

- `GitExecutionContext.run(arguments, *, cwd, check=True, input=None)`:
  given bytes go through `subprocess.run(input=...)` without `stdin`; without
  them the existing stdin rule applies. `_execute` takes them as `stream`, and
  a new `_spawn` holds both process starts. The `read_only_git` stand-in in
  `tests/unit/tools/release_workflow/conftest.py` accepts the new keyword.

Provisioning of any install target (Step 3 to 5 modules):

- `installation.InstallTarget` (frozen): version, triple, asset, size,
  member, URL, `accept(archive) -> sha256` (a `VerificationError` is the
  verification stage), `before_publish()` (run after the entry record is
  written and the owner file removed, before retirement and publication)
  and `reuse`, a function asked before each reuse check for the archive
  digest a reused entry must record (None allows no reuse at that check;
  production has no function and compares no archive digest). `install(layout, target, budget, seams,
  lock)` uses the target everywhere the pin was used. `manifest_target(pin)`
  keeps production exactly: verify against the manifest size and digest,
  record the manifest digest, nothing before publication, reusable, no
  archive comparison on reuse.
- `provisioning.provision_target(layout, target, budget, *, seams, caller)`
  runs the unchanged flow in the layout's namespace; `provision` calls it with
  `manifest_target(pin)` in production. `_reuse` asks the target's function
  before the lock-free check and again before the recheck under the lock.
- `cache.check_entry(..., asset_sha256=None)`: when given, the record's
  `asset_sha256` must equal it, compared after the record read and before the
  hash, so the candidate order is archive digest, executable, probe.
- `archive.archive_identity(path)` (SHA-256 and size of a staged file, used
  by `verify_archive`) and the narrower `ArchiveMember` protocol of
  `extract_member`; `download_worker.outcome_fields(stdout)`, the parent's
  reading of the outcome line, now used by the installation;
  `cache_lock.publish_file`, the former private `_publish`;
  `manifest.asset_url(version, asset)`, behind `download_url`.
- The native record is refreshed at milestone `step-5` (14 of 14 passed),
  since `cache.py`, `cache_lock.py`, `installation.py`, `provisioning.py`
  and `download_worker.py` are covered sources.

Fixture history, `tools/release_workflow/git_cliff/fixture_history.py`
(design "Frozen inputs and the coverage matrix", Q14):

- 20 declared commits and four annotated tags (`v0.1.0`, `v0.2.0-SNAPSHOT`,
  `v0.2.0`, `v0.3.0-SNAPSHOT`, in `TAGS`); one merge; messages for every
  group and skip rule of the dev_workflow `cliff.toml`, a breaking change, a
  fix whose body matches the security parser, a revert and an unconventional
  commit.
- `stream()`: commits with `deleteall` and every file inline, `from` and
  `merge` in parent order, author and committer with fixed dates and two
  zones; tags with tagger, date, zone and message; `done` at the end.
- `environment(source, global_config)`, `build(git, directory)` (`init
  --quiet --template= --object-format=sha1 --initial-branch=main`, then
  `fast-import --quiet --done` with the stream as input, then `for-each-ref
  --format=%(refname)%00%(objectname) refs/heads/main refs/tags`, each with
  `CONFIG`), `FixtureHashes` and `verify`.

Comparison, `tools/release_workflow/git_cliff/comparison.py` (design
"Frozen inputs and the coverage matrix", "Outputs and classification", Q13):

- `FrozenInputs` (pin, baseline, llm-shared commit, `CliffToml`, fixture
  hashes, ranges, `CandidateIdentity` values, `FLAGS`, `ENVIRONMENT`),
  `RangeCase`, `RunDigest`, `CaseResult` (hunk identifiers `<case> #<n>`),
  `ComparisonResult`, `Workspace`.
- `history_ranges(git, *, cwd, revision, repository)`: `rev-list
  --topo-order --reverse` and the tag records reachable from the revision,
  ordered in one pass; full history, consecutive pairs, last tag to HEAD.
- `run_environment(source, home)`; `run_comparison(inputs, invocations, git,
  workspace)`: `worktree add --detach` of the frozen commit with
  `core.hooksPath` on an empty directory, baseline then pin per case through a
  fresh invocation each (`-c <bundle copy> -w <directory> -s footer --
  [range]`, engine policy, captured output, `RUN_SECONDS` = 120), worktree
  removed and `worktree prune` in `finally`; `differing_hunks` (unified diff,
  three lines of context, line endings kept); `verify_rerun`.

Candidates, `tools/release_workflow/git_cliff/candidates.py` (design
"Candidate lifecycle and admission order", "Candidate cache"; plan decision
Q19):

- `parse_listing(version, metadata)` and `AssetListing`; `Candidate` with its
  validation; `EVIDENCE_ONLY_VERSIONS`, `UPSTREAM_DIGEST`,
  `EVIDENCE_ONLY_HTTPS` and `TRUST_BASIS` (the evidence-only basis states the
  authorization of 2026-11-13 and that HTTPS anchored the first download).
- `TrustRecord(path, version)`: `read`, `require`, `write_once` (through
  `publish_file` without replacement; an existing record is a
  `CandidateError`, never rewritten) and `compare(received)` (a
  `VerificationError` naming the record).
- `acquire_candidate(tooling_root, version, budget, seams, *, trust_path)`:
  an existing record is the identity (`provision_candidate`); otherwise the
  metadata worker (`WorkerRequest(mode="metadata")`, record-free, expiring 60
  s after it started, one retry after 5 s for a retryable failure), the trust
  kind decided before any download, and `provision_target` in the evidence
  namespace with a target whose acceptance compares with the listed size and
  published digest and writes the record in `before_publish`; a record
  found under the lock is compared instead, and the reuse function reads the
  record before each check, so a published matching entry is reused.
- `provision_candidate(...)`: the same target with the record present; its
  acceptance compares every new download with the record.

Bundle, `tools/release_workflow/git_cliff/bundle.py` (design "Outputs and
classification", "Statuses"; plan decision Q16):

- `Bundle` and its parts; strict `read` (via `lock_records.decode_object`,
  then each member's form, then the listed file digests) and `write`;
  `canonical_projection`, `covered_sha256`, `with_review`, `refreshed`;
  `require_complete` and `require_admissible` as listed in the validation
  plan, in `bundle_checks.py` since round 3 of this exchange. The default location
  is `tools/release_workflow/git_cliff/bundles/<pin>`; `pins` defaults to the
  shipped `ADMITTED_PINS`.

Harness, `tools/release_workflow/git_cliff/harness.py` (design "The
harness", Q15):

- `main(arguments, *, context=None)`, `HarnessContext`,
  `production_context()`, `evidence_git(source, *, checkout, temporary)`.
  A comparison: budget once, existing bundle of the same pair, baseline then
  pin acquired, fixture built and verified, inputs frozen (HEAD commit,
  `rev-parse <commit>:tools/dev_workflow`, `cat-file blob
  <submodule>:cliff.toml` in the submodule, copied into the bundle) or reused
  and compared field by field, with the copied `cliff.toml` bytes, before
  any run, comparison, `verify_rerun`, `write` with `refreshed`. A review: `with_review` over the current bundle and today's
  local date. Expected failures print one diagnostic and return 2.

Tests: `git_cliff_harness_fake.py` (new), the children fake (metadata role,
versions from cache paths, evidence namespace, `run_output`), the support
module (any version), and the leaves `test_git_cliff_fixture`,
`test_git_cliff_comparison`, `test_git_cliff_candidates` (acquisition and
records), `test_git_cliff_bundle` (model, review binding, property test) and
`test_git_cliff_harness`, plus additions to `test_git`, the cache,
provisioning, worker and archive leaves.

Also staged: the validation plan's Step 6 sections and the
`git_cliff/__init__.py` docstring.

Code review round 1 repairs (round 2 of this exchange):

- `bundle.py`: audit evidence (`AUDIT_CATEGORIES`, commands, references,
  findings) and observations (`OBSERVATIONS`, no 69, consistent statuses);
  trust record reconciliation in `read`; two distinct versions, the full
  matrix (`comparison.chained_ranges`), the fixture's tags, and the manifest
  identity in `require_complete`. 622 lines.
- `harness.py`: complete frozen-input comparison and copied `cliff.toml`
  bytes before any run; the temporary directory resolved to its long form.
- `fixture_history.verify`: every tag of either side, in order.
- `comparison.py`: `worktree add` inside the guarded block; cleanup through
  `worktree remove --force`, deletion, prune and a verifying listing; cleanup
  problems fail a successful run or are noted on the failure raised.
- `network.py`: HTTPS-only redirect handler, `InsecureRedirectError` (fatal);
  `git_cliff_support.CannedWeb.opener` now builds on the network opener.
- `installation.InstallTarget.reuse` replaces `reusable` and `entry_asset`;
  `provisioning._reuse` asks it before each check; `candidates` gives the
  trust record's digest read at that moment, and `trust_record_bytes`.
- Native record refreshed at `step-5` after the covered-source edits, 14 of
  14 passed.
- Tests: the bundle, comparison, fixture, candidates, harness, network and
  provisioning leaves, and the harness fake's samples (full matrix, real
  trust records, complete audit) and declared Git failures per action.

Code review round 2 repairs (round 3 of this exchange):

- `bundle_checks.py` (new, 233 lines): the admission rules split from
  `bundle.py`, which keeps the model, the strict codec and the review
  binding (451 lines, `covered_sha256` now public). `_observation_issue`
  checks each observation on its own before the presence check;
  `_outputs_problem` refuses a pin result of 69; `_matrix_complete` requires
  llm-shared's recorded tags once each and the ranges to be exactly their
  chain, then the fixture's.
- `comparison.py`: `history_tags(git, *, cwd, revision)` gives each tag
  reachable from the revision with its commit, in history order, in one
  pass; `FrozenInputs.llm_shared_tags` records them; the bundle encodes them
  as a list of `{name, commit}`.
- `harness.py`: `_inputs` records the tags and chains llm-shared's ranges
  from them; `main` prints each note of a failure after its diagnostic.
- `provisioning.py`: `_locked` guards the published entry before releasing
  the lock and closes the guard when the release fails; `run` prints the
  ready line only for an installation.
- Native record refreshed at `step-5` after the edit of `provisioning.py`,
  14 of 14 passed.
- Tests: the new bundle checks leaf (completeness and admissibility, with
  the round 2 regressions), the bundle leaf reduced to storage and binding,
  the candidates leaf's two-bundle guard test, the harness leaf's cleanup
  note and recorded tags, the comparison leaf's `history_tags`; the harness
  fake's sample inputs record one llm-shared tag.

Round 4 of this exchange (human rework at the round 3 gate):

- `bundle_checks.py`: line endings normalized from CRLF to LF, like every
  other staged file; no content change.

Writer notes: `.reviews/a.git-cliff-provisioning.step6.journal.md` and
`.reviews/a.git-cliff-provisioning.step6.handoff.md`.

### Change summary for step 6 git-cliff-provisioning (round 4)

Staged paths (44), grouped in the root `a.commit` (eleven groups, checker
`ready: true`), unchanged since round 3 except the line endings of
`tools/release_workflow/git_cliff/bundle_checks.py` (CRLF to LF). Round 3 added
that module in its own group after the bundle, and the new leaf
`tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/` (three
files) in the test group:

1. `feat(release): give Git an input stream`: `tools/release_workflow/git.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS`:
   `tools/release_workflow/git_cliff/network.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`,
   `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target`: `archive.py`,
   `cache.py`, `cache_lock.py`, `download_worker.py`, `manifest.py`,
   `installation.py`, `provisioning.py` (all in
   `tools/release_workflow/git_cliff/`), the archive, cache, worker and
   provisioning test files, and `native_checks.v1.json`; round 3 adds the
   guard opened before the lock release.
4. `feat(release): build the snapshot-tag fixture`: `fixture_history.py`.
5. `feat(release): compare two git-cliff versions`: `comparison.py`, with
   `history_tags` and `FrozenInputs.llm_shared_tags`.
6. `feat(release): acquire git-cliff evidence candidates`: `candidates.py`.
7. `feat(release): add the reviewed evidence bundle`: `bundle.py` (model,
   strict codec, review binding).
8. `feat(release): check a bundle before admission`: `bundle_checks.py`.
9. `test(release): cover the evidence modules`: `git_cliff_harness_fake.py`,
   `git_cliff_children_fake.py`, and the fixture, comparison, candidates,
   bundle and bundle checks leaves with their `__init__.py` files.
10. `feat(release): run the evidence harness by hand`: `harness.py`,
    `git_cliff/__init__.py`, and the harness leaf with its `__init__.py`.
11. `docs(git-cliff-provisioning): record step 6 validation`:
    `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Steps 1 to 5 of this plan are committed and pushed (`1cfda502` is the base
of this review). The transcript
`docs/v0.14.0/review.code.v0.14.0.git-cliff-provisioning.md` and
`.vscode/settings.json` (the cSpell word `deleteall` the transcript needs)
stay unstaged for the residual commit.

### Human guidance and writer response for step 6 git-cliff-provisioning (round 4)

Human guidance:

Rework and review again: normalize `tools/release_workflow/git_cliff/bundle_checks.py`
to LF line endings, the only CRLF file among the staged paths (flagged by
Git's default whitespace check in the round 3 answer). Line endings only, no
content change; validate on the new tree and review it in round 4.

Writer response:

Writer response:

Round 3 closed with no unresolved finding and a `commit-ready`
recommendation. At the convergence gate the user chose `Rework and review
again` for the one flaw the round 3 answer noted under repository state:
`tools/release_workflow/git_cliff/bundle_checks.py` had CRLF line endings,
the only CRLF file among the staged paths, which Git's default whitespace
check flags. The split script that created it in round 3 wrote it without
forcing LF.

The file is now LF, like every other staged file. This is the only change
since the round 3 assessed tree `95ce496729582667f2373b1e4c9511e7991c9ba6`:
`git diff 95ce4967 <round 4 tree>` touches only that file (233 lines
replaced), and the same diff with `--ignore-cr-at-eol` is empty. `git diff
--cached --check` is clean and `git ls-files --eol` reports no staged
`i/crlf` file. No code, test, validation plan or `a.commit` content changed;
the readiness checker still reports 11 groups and 44 paths.

### Reviewer focus for step 6 git-cliff-provisioning (round 4)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-6-round-4 -->

## Round 4 by reviewer - Step 6

- Recorded: 2026-11-20T21:44:54+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: answer

### Assessed index identity for step 6 git-cliff-provisioning (exchange 1) (round 4)

Baseline index tree: 19c9b249b649246e667c35a49a618aba8e5f412a

Assessed index tree: 19c9b249b649246e667c35a49a618aba8e5f412a

### Implementation check for step 6 git-cliff-provisioning (exchange 1) (round 4)

Result:

Yes. Step 6 has been fully implemented.

The only file changed since the reviewed round 3 tree is `tools/release_workflow/git_cliff/bundle_checks.py`. Ignoring carriage returns at end of line yields an empty tree diff. This preserves the implementation and regression coverage assessed in round 3.

Validation plan effects:

The staged Step 6 verdict remains accurate.

### Pre-repair mandatory checks and coverage for step 6 git-cliff-provisioning (exchange 1) (round 4)

On the round 4 tree the writer reports 8,097 tests, `cov=100 outliers=0 excluded=0 proof=speed`, exit 0. The reviewer’s independent `ghog affected --no-cov` using the exchange scope returned exit 0 with zero failures and warnings. The measured source scope is `tools` with the configured exclusions.

### Resolved validation set and sources for step 6 git-cliff-provisioning (exchange 1) (round 4)

Both the request and the reviewer’s project resolver select `ghog day --full=speed --whole-suite` from the project default.

### Resolver drift and direction for step 6 git-cliff-provisioning (exchange 1) (round 4)

None.

### Repository state around validation for step 6 git-cliff-provisioning (exchange 1) (round 4)

Round 3 tree `95ce496729582667f2373b1e4c9511e7991c9ba6` and round 4 tree `19c9b249b649246e667c35a49a618aba8e5f412a` differ only in `bundle_checks.py`. The request, baseline and assessed round 4 tree match. The ordered boundary check found only the ignored focused-run log. The umbrella digest matched.

### Repair inventory for step 6 git-cliff-provisioning (exchange 1) (round 4)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 6 git-cliff-provisioning (exchange 1) (round 4)

The independent checker returned `valid`, ready `true`, with 11 ordered groups covering all 44 staged paths. Diagnostics were empty.

1. `feat(release): give Git an input stream` groups `tools/release_workflow/git.py`, `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`, `tests/unit/tools/release_workflow/conftest.py`.
2. `fix(release): follow redirects only to HTTPS` groups `tools/release_workflow/git_cliff/network.py`, `tests/unit/tools/release_workflow/test_git_cliff_network/test_git_cliff_network_tdd.py`, `tests/unit/tools/release_workflow/git_cliff_support.py`.
3. `refactor(release): provision any install target` groups `tools/release_workflow/git_cliff/archive.py`, `tools/release_workflow/git_cliff/cache.py`, `tools/release_workflow/git_cliff/cache_lock.py`, `tools/release_workflow/git_cliff/download_worker.py`, `tools/release_workflow/git_cliff/manifest.py`, `tools/release_workflow/git_cliff/installation.py`, `tools/release_workflow/git_cliff/provisioning.py`, `tests/unit/tools/release_workflow/test_git_cliff_archive/test_git_cliff_archive_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_cache/test_git_cliff_cache_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_download_worker/test_git_cliff_download_worker_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_provisioning/test_git_cliff_provisioning_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`.
4. `feat(release): build the snapshot-tag fixture` groups `tools/release_workflow/git_cliff/fixture_history.py`.
5. `feat(release): compare two git-cliff versions` groups `tools/release_workflow/git_cliff/comparison.py`.
6. `feat(release): acquire git-cliff evidence candidates` groups `tools/release_workflow/git_cliff/candidates.py`.
7. `feat(release): add the reviewed evidence bundle` groups `tools/release_workflow/git_cliff/bundle.py`.
8. `feat(release): check a bundle before admission` groups `tools/release_workflow/git_cliff/bundle_checks.py`.
9. `test(release): cover the evidence modules` groups `tests/unit/tools/release_workflow/git_cliff_harness_fake.py`, `tests/unit/tools/release_workflow/git_cliff_children_fake.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_fixture/test_git_cliff_fixture_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_comparison/test_git_cliff_comparison_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_candidates/test_git_cliff_candidates_records_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_review_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle/test_git_cliff_bundle_pbt.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_tdd.py`, `tests/unit/tools/release_workflow/test_git_cliff_bundle_checks/test_git_cliff_bundle_checks_review_tdd.py`.
10. `feat(release): run the evidence harness by hand` groups `tools/release_workflow/git_cliff/harness.py`, `tools/release_workflow/git_cliff/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/__init__.py`, `tests/unit/tools/release_workflow/test_git_cliff_harness/test_git_cliff_harness_tdd.py`.
11. `docs(git-cliff-provisioning): record step 6 validation` groups `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

### Findings and boundaries for step 6 git-cliff-provisioning (exchange 1) (round 4)

Unresolved findings: None.

Boundary-crossing work: None.

### Human guidance response for step 6 git-cliff-provisioning (exchange 1) (round 4)

Human guidance:

Rework and review again: normalize `tools/release_workflow/git_cliff/bundle_checks.py`
to LF line endings, the only CRLF file among the staged paths (flagged by
Git's default whitespace check in the round 3 answer). Line endings only, no
content change; validate on the new tree and review it in round 4.

Guidance response:

Confirmed. The writer normalized `tools/release_workflow/git_cliff/bundle_checks.py` to LF. Comparing the two Git trees with `--ignore-cr-at-eol --exit-code` returned 0 with an empty diff. The default `git diff --cached --check` passed, and `git ls-files --eol` reports LF in the index for this file and zero CRLF files across all 44 staged paths.

### Writer instructions for step 6 git-cliff-provisioning (exchange 1) (round 4)

The human commit decision can proceed on the assessed round 4 tree.

### Decision rationale for step 6 git-cliff-provisioning (exchange 1) (round 4)

All six readiness checks pass for Step 6, round 4, occurrence 1. The identity and index match, implementation is complete, validation and coverage pass, staged attribution is intact, no findings remain open, and the commit plan is valid. The recommendation is `commit-ready`.

### Final reviewer decision for step 6 git-cliff-provisioning (exchange 1) (round 4)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-6-round-4 -->

## Round 4 by human - Step 6 - human-confirmation

- Recorded: 2026-11-20T21:55:22+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 6
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-4 -->

## Round 1 by requestor - Step 7

- Recorded: 2026-11-21T11:25:23+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 7
- Outcome: request

### Review identity for step 7 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 7
Review round: 1

### Code review evidence for step 7 git-cliff-provisioning (round 1)

request_index_tree: 3445bcdc71b6268fe1491b342e58e78684ad2176
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the approved 2.14.2 evidence
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json
group 2: feat(release): admit git-cliff 2.14.2 as default
group 2 path: tools/release_workflow/git_cliff/manifest.py
group 3: test(release): tie the admitted pin to its bundle
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
group 4: docs(git-cliff-provisioning): record step 7 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
staged path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json
staged path: tools/release_workflow/git_cliff/manifest.py
```

### Validation scope for step 7 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 7 git-cliff-provisioning (round 1)

Writer assessment for Step 7 of the git-cliff-provisioning plan, round 1: the
step is fully implemented, and the implementation check records `Yes. Step 7
has been fully implemented.` in the staged validation plan (the document
status stays `No, it is not implemented.` while Step 8 is not started).

Evidence, all on the staged tree:

- Evidence run by hand: the harness exit 0, 19 cases, every status 0, one
  differing case with 9 hunks; `require_complete` passed on the annotated
  bundle before the user's review; the user approved on 2026-11-21 and the
  harness's `--review approved` recorded it (`covered_sha256` `51862d50...`).
- Red first: `ghog single` on the admission, schemas, configuration and
  manifest tests failed at the empty pin table (exit 2, 8 failures; the three
  tests that read only the bundle already passed).
- Targeted: `ghog single` on the same files plus the manifest and
  bundle-checks leaves, exit 0, after the manifest edit.
- Default walk: `ghog day --whole-suite` exit 0 (check and 266 affected
  tests); no source was reformatted.
- Review validation, `ghog day --full=speed --whole-suite` (built-in default,
  no `.review-validation`): exit 0 with `cov=100 outliers=0 excluded=0
  proof=speed`, 8106 tests, slowest call 0.31 s (outside this step), on index
  tree `3445bcdc71b6268fe1491b342e58e78684ad2176`, identical before and after
  the walk. No budget was changed and no exclusion is accepted.
- `rg -n '2\.14\.2' tools/release_workflow/git_cliff/manifest.py`: the one
  admitted pin (lines 183 to 190) and three docstring mentions.
- Line counts: `manifest.py` 195, `test_git_cliff_admission_tdd.py` 132,
  `test_schemas_tdd.py` 200, `test_configuration_tdd.py` 341,
  `test_git_cliff_manifest_tdd.py` 200; every Python file below 650; the
  advisory overruns are recorded as variance in the validation plan.
- Native check record: unchanged; `manifest.py` is not a covered source.
- Markdown check and cSpell on the validation plan: clean.

Architecture: the manifest stays a table importing only `dataclasses` and
`re`; the harness never wrote it, and the pin entered by a hand edit copying
the bundle's identity; no production module imports `bundle` or
`bundle_checks` outside the harness. Performance: one more pin validated once
at import, lookups unchanged. Feature integrity: an omitted `[git-cliff]
version` now reads the defaulted 2.14.2, a declared 2.14.2 is accepted and
other versions list `tested: 2.14.2`; no engine command reads that value
before the Step 8 launcher; 2.7.0 stays a configuration error.

Please check in particular: the classification reason against the bundle's
hunks and the ranged cases; the audit's references and findings per category
(and the stated limit on the Windows abnormal-termination statuses); the
observed statuses against the audit; the admission leaf's use of
`require_admissible` with the shipped defaults; and the manifest entry against
the bundle's 2.14.2 candidate.

### Implementation report for step 7 git-cliff-provisioning (round 1)

Step 7, "Evidence run, user review and admission of 2.14.2", is the seventh
of eight steps of the git-cliff-provisioning plan. It runs the Step 6 harness
by hand, records the exit-path audit and the classification in the committed
bundle, takes the user's review, and only then admits 2.14.2 in the manifest.
No production module changes behavior beyond the configuration default that
the admitted pin now gives.

Evidence run (by hand, outside pytest, network):

- Command, from the project root with the project interpreter:
  `python -m tools.release_workflow.git_cliff.harness --bundle
  tools\release_workflow\git_cliff\bundles\2.14.2 --pin 2.14.2 --baseline
  2.7.0`, exit 0. 2.7.0 was acquired under the evidence-only exception of
  2026-11-13 (`evidence-only-https` trust); 2.14.2 from its release metadata
  (`upstream-digest` trust), 7,428,304 bytes, digest
  `6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131`, the
  identity the design names.
- Frozen inputs: llm-shared commit `4eed876b` with its 13 reachable tags, the
  `cliff.toml` bytes of the dev_workflow commit `f90bfc67` (copied into the
  bundle, identical to `tools/dev_workflow/cliff.toml`), the fixture hashes,
  both candidate identities with their executable digests.
- Results: 19 cases (14 llm-shared, 5 fixture), every status 0, 18 identical
  outputs; llm-shared's full history differs in 9 hunks.

Classification (hand-written in `bundle.json`):

- The 9 hunks are one change: 59 commit lines dated before the `v0.14.0` tag
  but not reachable from it leave the `v0.14.0` section (2.7.0 orders commits
  by date, `topo_order = false`) for Unreleased (2.14.2); their text is
  unchanged. Pairs: #1 and #5 (16 Features lines), #2 and #6 (38
  Documentation lines), #3 with #7 and #8 (one Performance and one Testing
  line), #4 and #9 (3 Miscellaneous Tasks lines).
- Each is `intentional`, citing git-cliff 2.14.1's release notes, Bug Fixes:
  "(changelog) Assign commits to releases by graph reachability" (#1601,
  e86c95e), implemented at `git-cliff/src/lib.rs:388` of `v2.14.2`.
- Checked by hand: `git merge-base --is-ancestor` on seven moved commits
  (none is an ancestor of `v0.14.0`); a rerun of the full history with both
  executables reproduced both recorded digests and showed `v0.14.0` spanning
  lines 77 to 449 in 2.7.0's output, which contains every removed line; the
  ranged cases `v0.13.0..v0.14.0` and `v0.14.0..HEAD` are identical in both
  versions.

Exit-path audit (`audit` member):

- Revision `5d996de8220d26c0cb8ff329d31791570cab262f` (annotated tag object
  `1ba9dcc4`), shallow clone in a temporary directory outside the repository;
  clap `v4.6.6` (commit `4a622b43`, the clap and clap_builder versions of
  git-cliff's `Cargo.lock`); the standard library sources of rustc 1.98.1
  (commit `48a229ce`, read from the executable). The eight commands are
  recorded with placeholders for the temporary directory.
- Error return: `main` returns `Result<()>`; an `Err` is reported by std as
  `ExitCode::FAILURE` (1); `write_changelog` errors give `process::exit(1)`;
  success 0; no other exit value in the git-cliff or git-cliff-core sources.
- Argument-parsing errors: clap's `Error::exit` is its only process exit:
  `USAGE_CODE` 2, `SUCCESS_CODE` 0 for help and version.
- Propagated helper statuses: a failing `cmd /C` helper becomes an error
  message, never the status; the only other `Command` uses are in test
  modules; the update check discards its errors; the bundle's `cliff.toml`
  starts no helper.
- Panics and abnormal termination: the release profile is `panic =
  "unwind"`, so a main-thread panic exits 101 (std `rt.rs`); aborts, stack
  overflow, access violation and Ctrl+C give Windows statuses of
  `0xC0000000` or more; no panic hook, `catch_unwind` or `process::abort`.
- `excludes_69` is true.

Observed statuses (`observed_statuses` member), the 2.14.2 evidence
executable after a digest check against its entry record, in the comparison's
explicit environment: success 0, usage error (`--no-such-option`) 2, failing
render (`--body "{{ undefined_variable }}"`) 1, panic (a `cliff.toml` copy
with `sort_commits = "sideways"`, reaching the `expect` at `lib.rs:721`) 101.

User review:

- `require_complete` passed on the annotated bundle; the classification
  table, audit, observed statuses and listed files were then presented to the
  user, who approved on 2026-11-21.
- `python -m tools.release_workflow.git_cliff.harness --bundle
  tools\release_workflow\git_cliff\bundles\2.14.2 --review approved` wrote
  `review`: approved, `user`, `2026-11-21`, `covered_sha256`
  `51862d50267598f7a3325f46fd494b448b2636a42cd0acf765081f573f384862`. The step
  journal records the same decision with its date, before the manifest edit.

Manifest, `tools/release_workflow/git_cliff/manifest.py`:

- `ADMITTED_PINS` holds one `AdmittedPin`: `2.14.2`, default, triple
  `x86_64-pc-windows-msvc`, asset `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip`,
  size 7,428,304, the digest above, member `git-cliff-2.14.2/git-cliff.exe`,
  evidence `tools/release_workflow/git_cliff/bundles/2.14.2`; still passed
  through `validate_pins`. Module docstring and constant comment updated.

Tests:

- New leaf `tests/unit/tools/release_workflow/test_git_cliff_acceptance/`
  with `test_git_cliff_admission_tdd.py`: the shipped manifest is exactly
  that pin and its default; the committed bundle passes `require_admissible`
  with the shipped manifest and the default location; the review is the
  user's dated approval of the recomputed projection; the listed digests
  equal the committed files; the pin is the bundle's upstream-digest 2.14.2
  candidate; the 2.7.0 record stays evidence-only and no pin carries its
  version or digest; `version = 2.7.0` is a configuration error listing
  `tested: 2.14.2`.
- `test_schemas_tdd.py`: the shipped `version` rule defaults to 2.14.2 and
  refuses 2.15.0 with `tested: 2.14.2`.
- `test_configuration_tdd.py`: an omitted key yields the defaulted 2.14.2
  with its source information; a declared 2.14.2 is kept as written;
  `version = 2.15.0` reports `tested: 2.14.2`.
- `test_git_cliff_manifest_tdd.py` (not in the plan's file list): its test of
  the shipped empty tuple would fail; `tested: none` is now proven on a
  synthetic empty table, and a new test proves the shipped table valid,
  defaulting to 2.14.2 and listing it.

Also staged: the validation plan's Step 7 sections.

Writer notes: `.reviews/a.git-cliff-provisioning.step7.journal.md` and
`.reviews/a.git-cliff-provisioning.step7.handoff.md`.

### Change summary for step 7 git-cliff-provisioning (round 1)

Staged paths (11), grouped in the root `a.commit` (four groups, checker
`ready: true`):

1. `feat(release): add the approved 2.14.2 evidence`:
   `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json`.
2. `feat(release): admit git-cliff 2.14.2 as default`:
   `tools/release_workflow/git_cliff/manifest.py`.
3. `test(release): tie the admitted pin to its bundle`:
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`,
   `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`,
   `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`.
4. `docs(git-cliff-provisioning): record step 7 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Every staged file has LF line endings. The review transcript stays out of
`a.commit`, for its residual commit after the review.

### Writer response for step 7 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 7 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- The classification, audit and observed statuses were written into
  `bundle.json` through the `bundle` module's own `read`, `replace` and
  `write` (LF, the harness's formatting), then read back and checked with
  `require_complete` before the review; the harness's `--review approved` was
  the only writer of the `review` member.
- Each of the 9 hunks gets its own entry naming its pair, with one shared
  upstream reason, because the bundle checks classify hunk by hunk.
- The audit reads the standard library at the rustc commit embedded in the
  executable, so the 101 and the `ExitCode::FAILURE` mapping rest on the
  compiler that built the asset. The Windows abnormal-termination statuses
  (`0xC0000409` for an abort, `0xC00000FD` for a stack overflow,
  `0xC0000005`, `0xC000013A`) are standard platform values, not read in that
  source; the observations corroborate the audit and do not prove the
  exclusion of 69, as the design states.
- The observation commands are recorded with placeholders (`<git-cliff
  2.14.2>`, `<bundle>`, `<llm-shared checkout>`), so no local path enters the
  bundle; the observations ran the evidence executable directly, outside the
  containment layer, after checking its digest against its entry record.
- `test_git_cliff_manifest_tdd.py` is updated outside the plan's file list,
  since its shipped-empty test would break; the empty-table behavior keeps its
  proof on a synthetic table.
- The admission leaf reads the committed bundle once per module through a
  cached reader and calls `require_admissible` with its defaults, so the
  shipped manifest and the default bundle location are what it checks.
- `manifest.py` is not a source the native check record covers, so the
  record is unchanged.

### Reviewer focus for step 7 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-1 -->

## Round 1 by reviewer - Step 7

- Recorded: 2026-11-21T11:31:30+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: 3445bcdc71b6268fe1491b342e58e78684ad2176

Assessed index tree: 3ac5a87f6ba76cdb72bfdd27692a9b655e941af0

### Implementation check for step 7 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 7 has NOT been fully implemented.

The manifest admits the approved 2.14.2 candidate as the sole default and the configuration tests cover the default, explicit selection, and refusal of 2.7.0. The admission leaf calls `require_admissible(bundle)` with the shipped defaults. The approval and dated journal entry precede admission. The checkout conversion described below breaks the reader on the target platform.

Validation plan effects:

Updated and staged the Step 7 verdict, missing work and feature integrity paragraphs in the validation plan. The capture and attribution checks identified only those edits.

### Pre-repair mandatory checks and coverage for step 7 git-cliff-provisioning (exchange 1) (round 1)

The requestor reports 8,106 passing tests with the speed and coverage gates green on the received index. Static inspection found no uncovered production branch in the data-only manifest change. The 19 comparison cases report success. All nine hunks in the full-history case pair up as moves between release sections, consistent with the cited upstream graph-reachability change and the identical tagged ranges. The audit identifies the error, parser, helper and unwind paths. The observed 0, 2, 1 and 101 corroborate those paths. The listed abnormal Windows statuses are platform examples.

### Resolved validation set and sources for step 7 git-cliff-provisioning (exchange 1) (round 1)

`ghog day --full=speed --whole-suite` (project default). The round binds the whole-suite speed scope.

### Resolver drift and direction for step 7 git-cliff-provisioning (exchange 1) (round 1)

The current resolver returned the same command and project source as the request.

### Repository state around validation for step 7 git-cliff-provisioning (exchange 1) (round 1)

The request-time tree matched the received index. The evidence comparison flags only the validation plan and index, attributable to the staged Step 7 assessment. The umbrella digest matched before and after.

### Repair inventory for step 7 git-cliff-provisioning (exchange 1) (round 1)

Repairs made:

- Assessment metadata only in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Paths staged:

- `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`
- `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py`
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py`
- `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`
- `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`
- `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json`
- `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml`
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json`
- `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json`
- `tools/release_workflow/git_cliff/manifest.py`

### Commit plan assessment for step 7 git-cliff-provisioning (exchange 1) (round 1)

The independent checker returned `valid`, `ready=true`, with all 11 staged files assigned once and zero diagnostics. The ordered subjects were:

1. `feat(release): add the approved 2.14.2 evidence` (4 paths)
2. `feat(release): admit git-cliff 2.14.2 as default` (1 paths)
3. `test(release): tie the admitted pin to its bundle` (5 paths)
4. `docs(git-cliff-provisioning): record step 7 validation` (1 paths)

The grouping matches the received implementation. Refresh the validation group body when recording the checkout fix.

### Findings and boundaries for step 7 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- `tools/release_workflow/git_cliff/bundles/2.14.2/` lacks a Git attribute that preserves the bytes of the three files in `bundle.json`'s `files` map. With `core.autocrlf=true`, `git cat-file --filters` on each staged blob yields SHA-256 prefixes `dc56e564`, `5c008948` and `c7f21c0e` for `cliff.toml`, the pin trust record and the baseline trust record respectively. The approved hashes start with `b5e0d216`, `af14a2a0` and `4abba8ef`. All three match with conversion disabled. `bundle.read` hashes working-tree bytes, so admission fails immediately on a fresh CRLF checkout.

Boundary-crossing work: None.

### Writer instructions for step 7 git-cliff-provisioning (exchange 1) (round 1)

Set path-scoped LF checkout attributes for the hashed bundle files. Exercise admission on Git checkout-filtered bytes with `core.autocrlf=true`, checking the three approved digests and `require_admissible`. The existing approved LF files already contain the required bytes.

### Decision rationale for step 7 git-cliff-provisioning (exchange 1) (round 1)

Changes requested. Identity, staged attribution, static production coverage and mechanical grouping passed. The checkout failure leaves the admission criterion and its validation incomplete.

### Final reviewer decision for step 7 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-7-round-1 -->

## Round 2 by requestor - Step 7

- Recorded: 2026-11-21T11:48:13+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: request

### Review identity for step 7 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 7
Review round: 2

### Code review evidence for step 7 git-cliff-provisioning (round 2)

request_index_tree: 1df956952cb44027f71a51e894ebd08d86e79b3f
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): add the approved 2.14.2 evidence
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json
group 1 path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json
group 1 path: .gitattributes
group 2: feat(release): admit git-cliff 2.14.2 as default
group 2 path: tools/release_workflow/git_cliff/manifest.py
group 3: test(release): tie the admitted pin to its bundle
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
group 4: docs(git-cliff-provisioning): record step 7 validation
group 4 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: .gitattributes
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py
staged path: tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json
staged path: tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json
staged path: tools/release_workflow/git_cliff/manifest.py
```

### Validation scope for step 7 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 7 git-cliff-provisioning (round 2)

Writer assessment for Step 7 of the git-cliff-provisioning plan, round 2: the
step is fully implemented, and the implementation check records `Yes. Step 7
has been fully implemented.` in the staged validation plan (the document
status stays `No, it is not implemented.` while Step 8 is not started).

Evidence, all on the staged tree:

- Evidence run by hand: the harness exit 0, 19 cases, every status 0, one
  differing case with 9 hunks; `require_complete` passed on the annotated
  bundle before the user's review; the user approved on 2026-11-21 and the
  harness's `--review approved` recorded it (`covered_sha256` `51862d50...`).
- Red first: `ghog single` on the admission, schemas, configuration and
  manifest tests failed at the empty pin table (exit 2, 8 failures; the three
  tests that read only the bundle already passed).
- Targeted: `ghog single` on the same files plus the manifest and
  bundle-checks leaves, exit 0, after the manifest edit.
- Default walk: `ghog day --whole-suite` exit 0 (check and 266 affected
  tests); no source was reformatted.
- Review validation, `ghog day --full=speed --whole-suite` (built-in default,
  no `.review-validation`): exit 0 with `cov=100 outliers=0 excluded=0
  proof=speed`, 8107 tests, slowest call 0.31 s (outside this step), on index
  tree `1df956952cb44027f71a51e894ebd08d86e79b3f`, identical before and after
  the walk. No budget was changed and no exclusion is accepted.
- `rg -n '2\.14\.2' tools/release_workflow/git_cliff/manifest.py`: the one
  admitted pin (lines 183 to 190) and three docstring mentions.
- Line counts: `manifest.py` 195, `test_git_cliff_admission_tdd.py` 149,
  `test_schemas_tdd.py` 200, `test_configuration_tdd.py` 341,
  `test_git_cliff_manifest_tdd.py` 200; every Python file below 650; the
  advisory overruns are recorded as variance in the validation plan.
- Native check record: unchanged; `manifest.py` is not a covered source.
- Markdown check and cSpell on the validation plan and the transcript: clean.
- Round 1 repair: the admission leaf's checkout test failed with the
  `.gitattributes` line removed and passes with it (`ghog single` on the
  leaf). By hand, Git's checkout filter with `core.autocrlf=true` wrote the
  staged bundle files with the approved digests `b5e0d216`, `af14a2a0` and
  `4abba8ef` (the same blobs under a path without the attribute give the
  reported `dc56e564`, `5c008948` and `c7f21c0e`), and `read` plus
  `require_admissible` accepted the checked-out directory.

Architecture: the manifest stays a table importing only `dataclasses` and
`re`; the harness never wrote it, and the pin entered by a hand edit copying
the bundle's identity; no production module imports `bundle` or
`bundle_checks` outside the harness. Performance: one more pin validated once
at import, lookups unchanged. Feature integrity: an omitted `[git-cliff]
version` now reads the defaulted 2.14.2, a declared 2.14.2 is accepted and
other versions list `tested: 2.14.2`; no engine command reads that value
before the Step 8 launcher; 2.7.0 stays a configuration error.

Please check in particular the round 1 repair: the `-text` attribute (scope
and choice over `eol=lf`), the checkout test's reach under the suite's
process-free policy, the by-hand checkout evidence, the restored validation
verdict, and `.gitattributes` in the evidence bundle group of `a.commit`.

### Implementation report for step 7 git-cliff-provisioning (round 2)

Step 7, "Evidence run, user review and admission of 2.14.2", is the seventh
of eight steps of the git-cliff-provisioning plan. It runs the Step 6 harness
by hand, records the exit-path audit and the classification in the committed
bundle, takes the user's review, and only then admits 2.14.2 in the manifest.
No production module changes behavior beyond the configuration default that
the admitted pin now gives.

Evidence run (by hand, outside pytest, network):

- Command, from the project root with the project interpreter:
  `python -m tools.release_workflow.git_cliff.harness --bundle
  tools\release_workflow\git_cliff\bundles\2.14.2 --pin 2.14.2 --baseline
  2.7.0`, exit 0. 2.7.0 was acquired under the evidence-only exception of
  2026-11-13 (`evidence-only-https` trust); 2.14.2 from its release metadata
  (`upstream-digest` trust), 7,428,304 bytes, digest
  `6ece2112b3f4af462190ecbea4aeb1315fff6af415629b597f84319073c31131`, the
  identity the design names.
- Frozen inputs: llm-shared commit `4eed876b` with its 13 reachable tags, the
  `cliff.toml` bytes of the dev_workflow commit `f90bfc67` (copied into the
  bundle, identical to `tools/dev_workflow/cliff.toml`), the fixture hashes,
  both candidate identities with their executable digests.
- Results: 19 cases (14 llm-shared, 5 fixture), every status 0, 18 identical
  outputs; llm-shared's full history differs in 9 hunks.

Classification (hand-written in `bundle.json`):

- The 9 hunks are one change: 59 commit lines dated before the `v0.14.0` tag
  but not reachable from it leave the `v0.14.0` section (2.7.0 orders commits
  by date, `topo_order = false`) for Unreleased (2.14.2); their text is
  unchanged. Pairs: #1 and #5 (16 Features lines), #2 and #6 (38
  Documentation lines), #3 with #7 and #8 (one Performance and one Testing
  line), #4 and #9 (3 Miscellaneous Tasks lines).
- Each is `intentional`, citing git-cliff 2.14.1's release notes, Bug Fixes:
  "(changelog) Assign commits to releases by graph reachability" (#1601,
  e86c95e), implemented at `git-cliff/src/lib.rs:388` of `v2.14.2`.
- Checked by hand: `git merge-base --is-ancestor` on seven moved commits
  (none is an ancestor of `v0.14.0`); a rerun of the full history with both
  executables reproduced both recorded digests and showed `v0.14.0` spanning
  lines 77 to 449 in 2.7.0's output, which contains every removed line; the
  ranged cases `v0.13.0..v0.14.0` and `v0.14.0..HEAD` are identical in both
  versions.

Exit-path audit (`audit` member):

- Revision `5d996de8220d26c0cb8ff329d31791570cab262f` (annotated tag object
  `1ba9dcc4`), shallow clone in a temporary directory outside the repository;
  clap `v4.6.6` (commit `4a622b43`, the clap and clap_builder versions of
  git-cliff's `Cargo.lock`); the standard library sources of rustc 1.98.1
  (commit `48a229ce`, read from the executable). The eight commands are
  recorded with placeholders for the temporary directory.
- Error return: `main` returns `Result<()>`; an `Err` is reported by std as
  `ExitCode::FAILURE` (1); `write_changelog` errors give `process::exit(1)`;
  success 0; no other exit value in the git-cliff or git-cliff-core sources.
- Argument-parsing errors: clap's `Error::exit` is its only process exit:
  `USAGE_CODE` 2, `SUCCESS_CODE` 0 for help and version.
- Propagated helper statuses: a failing `cmd /C` helper becomes an error
  message, never the status; the only other `Command` uses are in test
  modules; the update check discards its errors; the bundle's `cliff.toml`
  starts no helper.
- Panics and abnormal termination: the release profile is `panic =
  "unwind"`, so a main-thread panic exits 101 (std `rt.rs`); aborts, stack
  overflow, access violation and Ctrl+C give Windows statuses of
  `0xC0000000` or more; no panic hook, `catch_unwind` or `process::abort`.
- `excludes_69` is true.

Observed statuses (`observed_statuses` member), the 2.14.2 evidence
executable after a digest check against its entry record, in the comparison's
explicit environment: success 0, usage error (`--no-such-option`) 2, failing
render (`--body "{{ undefined_variable }}"`) 1, panic (a `cliff.toml` copy
with `sort_commits = "sideways"`, reaching the `expect` at `lib.rs:721`) 101.

User review:

- `require_complete` passed on the annotated bundle; the classification
  table, audit, observed statuses and listed files were then presented to the
  user, who approved on 2026-11-21.
- `python -m tools.release_workflow.git_cliff.harness --bundle
  tools\release_workflow\git_cliff\bundles\2.14.2 --review approved` wrote
  `review`: approved, `user`, `2026-11-21`, `covered_sha256`
  `51862d50267598f7a3325f46fd494b448b2636a42cd0acf765081f573f384862`. The step
  journal records the same decision with its date, before the manifest edit.

Manifest, `tools/release_workflow/git_cliff/manifest.py`:

- `ADMITTED_PINS` holds one `AdmittedPin`: `2.14.2`, default, triple
  `x86_64-pc-windows-msvc`, asset `git-cliff-2.14.2-x86_64-pc-windows-msvc.zip`,
  size 7,428,304, the digest above, member `git-cliff-2.14.2/git-cliff.exe`,
  evidence `tools/release_workflow/git_cliff/bundles/2.14.2`; still passed
  through `validate_pins`. Module docstring and constant comment updated.

Tests:

- New leaf `tests/unit/tools/release_workflow/test_git_cliff_acceptance/`
  with `test_git_cliff_admission_tdd.py`: the shipped manifest is exactly
  that pin and its default; the committed bundle passes `require_admissible`
  with the shipped manifest and the default location; the review is the
  user's dated approval of the recomputed projection; the listed digests
  equal the committed files; the pin is the bundle's upstream-digest 2.14.2
  candidate; the 2.7.0 record stays evidence-only and no pin carries its
  version or digest; `version = 2.7.0` is a configuration error listing
  `tested: 2.14.2`.
- `test_schemas_tdd.py`: the shipped `version` rule defaults to 2.14.2 and
  refuses 2.15.0 with `tested: 2.14.2`.
- `test_configuration_tdd.py`: an omitted key yields the defaulted 2.14.2
  with its source information; a declared 2.14.2 is kept as written;
  `version = 2.15.0` reports `tested: 2.14.2`.
- `test_git_cliff_manifest_tdd.py` (not in the plan's file list): its test of
  the shipped empty tuple would fail; `tested: none` is now proven on a
  synthetic empty table, and a new test proves the shipped table valid,
  defaulting to 2.14.2 and listing it.

Code review round 1 repair, checkout bytes:

- `.gitattributes` gains a comment and the line
  `tools/release_workflow/git_cliff/bundles/** -text`. Git then converts no
  line ending in a bundle directory, in either direction, so the committed
  blob, every checkout and the digests `bundle.json` lists stay the same
  bytes; `git check-attr` reports `text: unset` for all four bundle files.
- The admission leaf adds
  `test_git_keeps_the_bytes_of_the_listed_files_on_every_checkout`: the
  attribute line is present in `.gitattributes`, each listed file holds no
  carriage return, and its CRLF conversion would change its digest. It failed
  with the line removed and passes with it.
- By hand, outside pytest: `git -c core.autocrlf=true checkout-index
  --prefix=<scratch>/` of `.gitattributes` and the four staged bundle files
  wrote `cliff.toml`, `trust.2.14.2.json` and `trust.2.7.0.json` with SHA-256
  prefixes `b5e0d216`, `af14a2a0` and `4abba8ef` (the approved digests) and no
  carriage return; the same blobs through `git -c core.autocrlf=true cat-file
  --filters` under a path without the attribute gave `dc56e564`, `5c008948`
  and `c7f21c0e`, the digests the round 1 answer reported. `bundle.read` and
  `require_admissible` (shipped manifest, default location) accepted the
  checked-out directory, its review still covering `51862d50...`.
- The validation plan's Step 7 sections are back to `Yes`, with the repair in
  the analysis, implementation, new data, coverage and feature-integrity
  entries; the reviewer's missing-work section is removed since its two items
  are done. `a.commit` adds `.gitattributes` to the bundle group and the
  repair to the test and validation bodies.

Also staged: the validation plan's Step 7 sections.

Writer notes: `.reviews/a.git-cliff-provisioning.step7.journal.md` and
`.reviews/a.git-cliff-provisioning.step7.handoff.md`.

### Change summary for step 7 git-cliff-provisioning (round 2)

Staged paths (12), grouped in the root `a.commit` (four groups, checker
`ready: true`); round 2 adds `.gitattributes` to group 1:

1. `feat(release): add the approved 2.14.2 evidence`:
   `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json`,
   `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json`,
   `.gitattributes`.
2. `feat(release): admit git-cliff 2.14.2 as default`:
   `tools/release_workflow/git_cliff/manifest.py`.
3. `test(release): tie the admitted pin to its bundle`:
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`,
   `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`,
   `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`.
4. `docs(git-cliff-provisioning): record step 7 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`.

Changed since round 1: `.gitattributes` (new attribute line), the admission
test module (one test and its docstring), the validation plan (the reviewer's
round 1 edits replaced by the repaired verdict), and the bodies of groups 1, 3
and 4. Every staged file has LF line endings. The review transcript stays out
of `a.commit`, for its residual commit after the review.

### Writer response for step 7 git-cliff-provisioning (round 2)

Writer response:

Writer response:

The round 1 finding is accepted: with `core.autocrlf=true`, Git converted the
bundle's three hashed files to CRLF on checkout and `bundle.read` refused
them. I reproduced the reviewer's three CRLF digests before the repair.

- Attribute: `tools/release_workflow/git_cliff/bundles/** -text` rather than
  `eol=lf`. Unsetting `text` stops every line-ending conversion in both
  directions, so the bytes recorded in a bundle are the bytes committed and
  checked out, whatever they hold. `eol=lf` protects today's LF files too, but
  it would normalize a future `cliff.toml` copy that holds CRLF on commit, and
  that copy would then lose the digest the harness recorded for it. The
  pattern covers the whole bundle directory, `bundle.json` included, so later
  bundles need no new line.
- Test: the suite never starts Git (its repository fixtures declare a
  non-executable Git port, and the design keeps these tests process-free), so
  the admission leaf cannot run Git's checkout filter. It checks the attribute
  line and that each listed file would change its digest under a CRLF
  conversion, so removing the line fails the test (shown red, then green).
- Admission on Git checkout-filtered bytes, as asked, ran by hand outside
  pytest: `checkout-index` with `core.autocrlf=true` wrote the approved digests,
  and `read` plus `require_admissible` accepted that checked-out directory.
- The reviewer's validation-plan edits were the right verdict for round 1;
  with both missing-work items done, I restored `Yes`, recorded the repair in
  each affected section and removed the missing-work section.
- `a.commit`: `.gitattributes` joins the evidence bundle group, since its line
  exists to keep that bundle's bytes; the group order and subjects are
  unchanged.

No disagreement.

### Reviewer focus for step 7 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-7-round-2 -->

## Round 2 by reviewer - Step 7

- Recorded: 2026-11-21T11:51:54+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: answer

### Assessed index identity for step 7 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 1df956952cb44027f71a51e894ebd08d86e79b3f

Assessed index tree: 1df956952cb44027f71a51e894ebd08d86e79b3f

### Implementation check for step 7 git-cliff-provisioning (exchange 1) (round 2)

Result:

Yes. Step 7 has been fully implemented.

The approved evidence covers the sole default pin, git-cliff 2.14.2. The three listed hashes survive a checkout with `core.autocrlf=true`. The raw-byte Git attribute applies to the evidence bundle directory and preserves both LF and CRLF input as recorded by the harness.

Validation plan effects:

The staged Step 7 validation now records the repair, checkout proof and completed verdict. It addresses both missing-work items.

### Pre-repair mandatory checks and coverage for step 7 git-cliff-provisioning (exchange 1) (round 2)

I applied Git's actual checkout filter to each of the four staged bundle blobs with `core.autocrlf=true`, then read the resulting files from a temporary directory. The three listed SHA-256 prefixes were `b5e0d216`, `af14a2a0` and `4abba8ef`. `require_admissible` accepted the result with its shipped defaults and approval digest `51862d50267598f7a3325f46fd494b448b2636a42cd0acf765081f573f384862`. The process-free unit test guards the attribute declaration and the hash sensitivity of these three files. The requestor reports 8,107 passing tests, 100% measured coverage and zero speed outliers. Static assessment found the manifest data exercised by the admission, manifest and configuration tests.

### Resolved validation set and sources for step 7 git-cliff-provisioning (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` (project source).

### Resolver drift and direction for step 7 git-cliff-provisioning (exchange 1) (round 2)

The current resolver and the request agree on command, source and whole-suite scope.

### Repository state around validation for step 7 git-cliff-provisioning (exchange 1) (round 2)

Both captures matched the request-time index `1df956952cb44027f71a51e894ebd08d86e79b3f`. Validation-state comparison passed and the umbrella digest matched.

### Repair inventory for step 7 git-cliff-provisioning (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 7 git-cliff-provisioning (exchange 1) (round 2)

The independent checker returned `valid` and `ready=true` for 12 staged paths with zero diagnostics. The conventional subjects and dependency order match the staged work.

1. `feat(release): add the approved 2.14.2 evidence`
  - `tools/release_workflow/git_cliff/bundles/2.14.2/bundle.json`
  - `tools/release_workflow/git_cliff/bundles/2.14.2/cliff.toml`
  - `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.14.2.json`
  - `tools/release_workflow/git_cliff/bundles/2.14.2/trust.2.7.0.json`
  - `.gitattributes`
2. `feat(release): admit git-cliff 2.14.2 as default`
  - `tools/release_workflow/git_cliff/manifest.py`
3. `test(release): tie the admitted pin to its bundle`
  - `tests/unit/tools/release_workflow/test_git_cliff_acceptance/__init__.py`
  - `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_admission_tdd.py`
  - `tests/unit/tools/release_workflow/test_git_cliff_manifest/test_git_cliff_manifest_tdd.py`
  - `tests/unit/tools/release_workflow/test_schemas/test_schemas_tdd.py`
  - `tests/unit/tools/release_workflow/test_configuration/test_configuration_tdd.py`
4. `docs(git-cliff-provisioning): record step 7 validation`
  - `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`

### Findings and boundaries for step 7 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 7 git-cliff-provisioning (exchange 1) (round 2)

Present the advisory recommendation at the human commit gate.

### Decision rationale for step 7 git-cliff-provisioning (exchange 1) (round 2)

Recommend `commit-ready`. Exchange identity, implementation completeness, validation and coverage, staged scope and commit grouping all passed. The checkout proof closes the outstanding finding.

### Final reviewer decision for step 7 git-cliff-provisioning (exchange 1) (round 2)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-7-round-2 -->

## Round 2 by human - Step 7 - human-confirmation

- Recorded: 2026-11-22T01:37:15+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 7
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-2 -->

## Round 1 by requestor - Step 8

- Recorded: 2026-11-22T12:12:48+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: unrecorded
- Implementation step: 8
- Outcome: request

### Review identity for step 8 git-cliff-provisioning (round 1)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 8
Review round: 1

### Code review evidence for step 8 git-cliff-provisioning (round 1)

request_index_tree: e758993d997e2500c0b3df211d6322265095d811
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --full=cov --whole-suite` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): observe worktree presence for gcliff
group 1 path: tools/release_workflow/git.py
group 1 path: tools/release_workflow/paths.py
group 1 path: tests/unit/tools/release_workflow/repository_simulation.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
group 2: feat(release): add the gcliff launcher
group 2 path: tools/release_workflow/invocation.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: tools/release_workflow/git_cliff/launcher.py
group 2 path: tools/release_workflow/git_cliff/__init__.py
group 2 path: bin/gcliff.bat
group 2 path: bin/gcliff.doskey
group 2 path: .gitattributes
group 3: test(release): drive gcliff through the simulation
group 3 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 3 path: tests/unit/tools/release_workflow/gcliff_simulation.py
group 3 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 4: test(release): accept gcliff on the shipped manifest
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
group 5: test(release): record the final native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(wiki): document git-cliff provisioning
group 6 path: wiki/reference/git-cliff-provisioning.md
group 6 path: wiki/reference/aliases-and-launchers.md
group 6 path: wiki/reference/automation-and-direct-invocation.md
group 6 path: wiki/README.md
group 7: docs(git-cliff-provisioning): record step 8 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 7 path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: .gitattributes
staged path: bin/gcliff.bat
staged path: bin/gcliff.doskey
staged path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/gcliff_simulation.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/launcher.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/paths.py
staged path: wiki/README.md
staged path: wiki/reference/aliases-and-launchers.md
staged path: wiki/reference/automation-and-direct-invocation.md
staged path: wiki/reference/git-cliff-provisioning.md
```

### Validation scope for step 8 git-cliff-provisioning (round 1)

Validation scope: the whole suite.

### Requestor assessment for step 8 git-cliff-provisioning (round 1)

Writer assessment for Step 8 of the git-cliff-provisioning plan, round 1: the
step is fully implemented. The implementation check records `Yes. Step 8 has
been fully implemented.` in the staged validation plan, whose document status
now reads `Yes, it is implemented.` since every step reads Yes, and the
umbrella row of item 3 is completed with its requirement and validation plan.

Evidence, on the staged tree:

- Red first: `ghog single` on the Git, paths, invocation, bootstrap, source
  contract, launcher and acceptance tests failed at the first boundary
  (exit 5, `WorktreePresence` missing from `tools.release_workflow.git`).
- Targeted: the same targets green (exit 0, 278 tests) after the
  implementation; later additions green in focus.
- Native recorder by hand, outside pytest:
  `python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone final --output
  tests\unit\tools\release_workflow\test_git_cliff_native_evidence\native_checks.v1.json`,
  exit 0, 15 of 15 checks passed on the final covered sources, plus the
  recorder timeout demonstration; the validator accepts the record (`ghog
  single` on the evidence leaf after the last walk).
- By hand: the first `bin\gcliff.bat --version` from a directory outside any
  worktree downloaded, verified and published 2.14.2 into this checkout's
  ignored cache with the downloading and ready lines, then printed
  `git-cliff 2.14.2`; the next call reused it silently; `--frobnicate`
  returned git-cliff's usage status 2; `--tag 50^%` returned 69 with the
  `cliff.toml` diagnostic; `git status` stayed clean.
- Default walk `ghog day --whole-suite`: exit 0 on the final tree.
- Review validation `ghog day --full=speed --whole-suite` (built-in default,
  no `.review-validation`): exit 0 with `cov=100 outliers=0 excluded=0
  proof=speed`, 8204 tests, slowest call 0.31 s (outside this step), on index
  tree `e758993d997e2500c0b3df211d6322265095d811`, identical before and after
  the walk. No budget was changed and no exclusion is accepted.
- Plan's final coverage proof `ghog day --full=cov --whole-suite` (passed as a
  plan validation command): exit 0 on the same tree, reusing that speed proof
  (`proof=speed reused=all`); an earlier full run on the tree before the last
  two test additions reported 8201 tests with `cov=100`.
- `rg -n 'gcliff' senv.doskey`: no match. `rg -n 'returning 1'
  bin/gcliff.bat`: no match. `test_codepage_tdd.py` is unchanged and passes.
- Line counts: every Python file below 550; advisory overruns recorded as
  variance in the validation plan.
- Markdown check and cSpell: clean on the four wiki pages, the validation
  plan and the umbrella draft.

Architecture: the launcher is an entry adapter composing the configuration
reader, the manifest, the Git adapter, the path policy and the provisioning
service; selection depends on the caller's directory only; the bootstrap
keeps its tables at module level and its single status set; `paths` imports
only `WorktreePresence` from `git`. Performance: constant work per call, one
Git process for the presence. Feature integrity: the release launchers,
discovery for every other caller and the engine commands are unchanged.

Please check in particular: the launcher's 69 boundary (every path before the
child, the refused and unconfirmed child, the console filter failure) and
that the invocation guard is released on each; `find_worktree` against
`discover_project`; the bootstrap's status tables and the unchanged cross-site
contract; the derivation of `bin/gcliff.bat`; the final native check's
method (silent pipe, handle scan of the launcher) and its observations; and
the acceptance rows against the plan's ownership map.

### Implementation report for step 8 git-cliff-provisioning (round 1)

Step 8, "The gcliff launcher, integrated acceptance, final native checks and
documentation", is the last of eight steps of the git-cliff-provisioning plan.
It ships `gcliff`, the typed worktree presence it needs, the integrated
acceptance tests, the final native check record and the reference
documentation.

Worktree presence and discovery:

- `git.py`: `WorktreePresence` (`INSIDE`, `NO_WORKTREE`, `NO_REPOSITORY`) and
  `GitExecutionContext.worktree_presence(*, cwd)`, one `rev-parse
  --is-inside-work-tree` call through `run` with `check=False`: `true\n` is
  inside, `false\n` (a bare repository or a `.git` directory) is no worktree,
  exit 128 whose stderr starts with `fatal: not a git repository` is no
  repository (the controlled environment sets `LC_ALL=C`), and every other
  answer raises `GitCommandError`.
- `paths.py`: `find_worktree(start, git)` inspects the configuration, asks the
  presence once and, inside a worktree, returns the identity through
  `_discovered`, the helper `discover_project` now also uses, so the
  configuration is inspected once per call. `discover_project` keeps its
  behavior; its tests are unchanged.

Entry kind and bootstrap:

- `invocation.py`: `gcliff-batch` joins `ENTRY_KINDS`; `validate_arguments`
  applies the batch guard to it as to every `-batch` kind.
- `bootstrap.py`: `_ENGINES` maps the kind to
  `tools.release_workflow.git_cliff.launcher`, `_UNNORMALIZED_KINDS` holds it,
  and `_unnormalized` calls a `Launcher` protocol with the arguments, the
  original cwd, the tooling root and the verified identity. `_FAILURE_STATUS`
  gives `gcliff-batch` 69 for readiness and invocation failures and for an
  execution failure before the launcher or escaping it; every other kind keeps
  `(2, 1)`. `InvocationError.kind` carries the kind once recognized, so a
  repeated `--entry-kind` in gcliff arguments is 69 while a release kind keeps
  2. `main` keeps its one status set literal, which the cross-site contract of
  `test_codepage_tdd.py` reads.

Launcher (`tools/release_workflow/git_cliff/launcher.py`):

- `main(arguments, *, original_cwd, tooling_root, runtime, environment=None,
  seams=None)`: the batch guard (diagnostic naming `cliff.toml`), the Git
  context from the caller's environment and directory, `find_worktree`, the
  whole configuration and `configured_pin` inside a worktree or
  `default_version` outside one, `admitted` from the seam's pin table,
  `provisioning_budget`, then `provision(..., caller="gcliff")`.
- The run: `invocation.run(arguments, policy=Policy.PASSTHROUGH,
  cwd=original_cwd, environment=environment, output="inherit")` inside the
  console filter, inside `with invocation:`; with `environment=None` the
  child inherits the process environment as is. The child's status is
  returned unchanged.
- Every failure before the child, a refused creation, an unconfirmed end, an
  interruption or a filter that cannot register writes one `gcliff: <detail>`
  line and returns `GCLIFF_UNAVAILABLE = 69`.
- `LauncherSeams(provisioning, console=ignore_console_interrupts,
  pins=ADMITTED_PINS)` and `production_seams(runtime)`; `main` binds the
  production seams with the verified runtime's interpreter when none is given.

Batch file and alias:

- `bin/gcliff.bat` is `bin/release_workflow.bat` with three changes:
  `set "_release_status=69"` followed by a comment line, `--entry-kind
  gcliff-batch`, and `goto cleanup` in place of the five normalization lines.
  It was derived by a script from the release launcher and written with CRLF;
  `.gitattributes` gives it `text eol=crlf`; the index holds LF.
- `bin/gcliff.doskey`: `gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*`, one
  line; `senv.doskey` is unchanged.

Tests:

- Launcher leaf `test_git_cliff_launcher/` (29 cases): every launcher case of
  the plan through the launcher simulation, with the provisioning world as the
  fake provisioning seam and fake child launcher and a fake kernel for the
  console filter; plus status 101, an interruption, a filter that cannot
  register, a manifest admitting no pin, `main` without seams and the
  production seams.
- `test_launchers/test_gcliff_source_tdd.py`: the derivation equality, the
  69 assignment before the record checks, no normalization, the code page
  restore after a readiness error and after a child return, the alias
  fragment, `senv.doskey` without a gcliff macro, the attribute line.
- Bootstrap, invocation, Git and paths leaves: the plan's cases.
- Acceptance leaf: `test_git_cliff_acceptance_tdd.py` and
  `test_gcliff_acceptance_tdd.py`, every Step 8 row of the ownership map
  against the shipped manifest; rows that download use a synthetic 2.14.2
  table through the launcher seams, since no test downloads the published
  asset.
- Support: `launcher_simulation.py` (gcliff entry with seams,
  `worktree_presence` routed to the sandbox), `gcliff_simulation.py` (new,
  the scenario builder), `repository_simulation.py` (declared presences),
  `git_cliff_children_fake.py` (a `gcliff --version` run inherits standard
  input, so it is a run, not a probe).

Final native record:

- Milestone `final`: the 14 checks of Steps 2, 4 and 5 on the final sources
  and the new `guard-held-by-gcliff-run-after-launcher-killed`
  (`git_cliff_native_launcher.py`, 17.4 s of a 120 s bound), all passed.
- That check runs the warm-up `bin\gcliff.bat --version`, then the production
  launcher with `--from-context <named pipe>` on a pipe the recorder serves
  and never writes, so git-cliff waits on its own file object and no handle
  the launcher shares has a pending read. It finds git-cliff and its launcher
  (the interpreter that created it) in a process snapshot, scans the
  launcher's handle values for the job (`IsProcessInJob`, duplicate kept) and
  the guard (the handle naming the executable), kills the launcher, then
  observes git-cliff alive, its handle of the guard's value naming the
  executable, the rename refused, and the rename allowed once the job ended
  git-cliff and during a guard-free control run. The rename is undone at
  once, so the production entry stays valid.
- The validator requires both the Step 5 stand-in check and the new check at
  `final`, and binds the launcher, the batch file and the modules on its path.

Documentation: `wiki/reference/git-cliff-provisioning.md` (new), the
git-cliff launcher section of `aliases-and-launchers.md`, the provisioning
availability and the statuses 2 and 69 in
`automation-and-direct-invocation.md`, and the link in `wiki/README.md`.

Also staged: the validation plan's Step 8 sections and document status, and
the umbrella row of item 3.

Writer notes: `.reviews/a.git-cliff-provisioning.step8.journal.md` and
`.reviews/a.git-cliff-provisioning.step8.handoff.md`.

### Change summary for step 8 git-cliff-provisioning (round 1)

Staged paths (32), grouped in the root `a.commit` (seven groups, checker
`ready: true`):

1. `feat(release): observe worktree presence for gcliff`:
   `tools/release_workflow/git.py`, `tools/release_workflow/paths.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py`.
2. `feat(release): add the gcliff launcher`:
   `tools/release_workflow/invocation.py`, `tools/release_workflow/bootstrap.py`,
   `tools/release_workflow/git_cliff/launcher.py`,
   `tools/release_workflow/git_cliff/__init__.py`, `bin/gcliff.bat`,
   `bin/gcliff.doskey`, `.gitattributes`.
3. `test(release): drive gcliff through the simulation`:
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/gcliff_simulation.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
4. `test(release): accept gcliff on the shipped manifest`:
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py`.
5. `test(release): record the final native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_launcher.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
6. `docs(wiki): document git-cliff provisioning`:
   `wiki/reference/git-cliff-provisioning.md`,
   `wiki/reference/aliases-and-launchers.md`,
   `wiki/reference/automation-and-direct-invocation.md`, `wiki/README.md`.
7. `docs(git-cliff-provisioning): record step 8 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`,
   `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`.

Every staged file has LF line endings in the index (`bin/gcliff.bat` checks
out with CRLF through its attribute). The review transcript stays out of
`a.commit`, for its residual commit after the review.

### Writer response for step 8 git-cliff-provisioning (round 1)

Writer response:

Writer response:

This is the first round of the Step 8 code review; there is no earlier
reviewer feedback to answer.

Choices worth checking, all recorded in the step notes and in the staged
validation plan:

- The plan says the inherited-guard check after a killed launcher "now starts
  `bin\gcliff.bat` ... instead of the stand-in caller". The final milestone
  keeps the Step 5 stand-in check, as part of "every check of Steps 2, 4 and
  5", and adds the production check under its own name; the validator
  requires both at `final`.
- `_FAILURE_STATUS` gives 69 to an execution failure of `gcliff-batch` too
  (an interruption or an unexpected error before the launcher, or an error
  escaping it): no git-cliff status is known then, and the design reserves 69
  for every failure before git-cliff starts. The plan names readiness and
  invocation failures explicitly.
- A refused child creation and an unconfirmed end are reported as 69 with the
  containment diagnostic: the first means git-cliff never started, the second
  that its status is unknown.
- `LauncherSeams` carries the pin table, so the acceptance rows that download
  can use a synthetic 2.14.2 archive the fake worker delivers; every other row
  selects from the shipped manifest. The configuration domain always uses the
  shipped manifest.
- The launcher passes its `environment` argument unchanged to the run: in
  production it is None, so git-cliff inherits the process environment as is,
  never an uppercased copy of `os.environ`.
- The final native check keeps git-cliff alive on a named pipe it reads
  (`--from-context`), not on its standard input, because the launcher shares
  the standard input file object and the recorder queries the names of the
  launcher's handles. It kills the launcher's interpreter directly; the venv
  redirector above it then exits on its own.
- Test-side files outside the plan's list: `gcliff_simulation.py`,
  `git_cliff_native_launcher.py` (the service module had 412 lines),
  `repository_simulation.py`, `git_cliff_children_fake.py`; `.gitattributes`
  gains the batch file's line.

### Reviewer focus for step 8 git-cliff-provisioning (round 1)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-1 -->

## Round 1 by reviewer - Step 8

- Recorded: 2026-11-22T20:58:21+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 git-cliff-provisioning (exchange 1) (round 1)

Baseline index tree: e758993d997e2500c0b3df211d6322265095d811

Assessed index tree: 78226956f62aa7863036aa5da800f367c2b6de00

### Implementation check for step 8 git-cliff-provisioning (exchange 1) (round 1)

Result:

No. Step 8 has NOT been fully implemented.

The production entry point, alias, project discovery, pin selection and reference pages are present. The final recorder can stop an unrelated launcher, three paths can return the wrong status, and the AC6 acceptance test can miss regressions.

Validation plan effects:

The reviewer changed and staged only the Step 8 assessment, missing-work items, coverage discussion and integrity conclusions in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`. The umbrella digest was identical before and after.

### Pre-repair mandatory checks and coverage for step 8 git-cliff-provisioning (exchange 1) (round 1)

Static review of the request-time tree and its tests. Writer-reported results were 8,204 passing tests, 100% measured coverage, no duration outliers and 15 passing final native checks. Reviewer inspection found the behavioral coverage gaps below. No reviewer test walk or native recorder was needed or run.

### Resolved validation set and sources for step 8 git-cliff-provisioning (exchange 1) (round 1)

Project default `ghog day --full=speed --whole-suite`, followed by the plan addition `ghog day --full=cov --whole-suite`. The request binds both to whole-suite scope.

### Resolver drift and direction for step 8 git-cliff-provisioning (exchange 1) (round 1)

None. The project has no `.review-validation` override. The speed default and the plan's final coverage command both resolve under the whole-suite requirement. Their order and sources match the request.

### Repository state around validation for step 8 git-cliff-provisioning (exchange 1) (round 1)

The before/after validation comparison flagged exactly the validation plan as tracked and reported no untracked or ignored side effects. Its pre-edit blob matched the index. Patch attribution and hunk inspection confirmed every edit was in Step 8. The staged comparison preserves all 32 paths and the protected umbrella digest.

### Repair inventory for step 8 git-cliff-provisioning (exchange 1) (round 1)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 8 git-cliff-provisioning (exchange 1) (round 1)

Independent commit-plan checks before and after the metadata edit returned ready, exit 0, 7 groups, 32 paths and zero diagnostics. Position, subject and ordered path membership match the request for every group.

1. `feat(release): observe worktree presence for gcliff` (5 paths)
2. `feat(release): add the gcliff launcher` (7 paths)
3. `test(release): drive gcliff through the simulation` (8 paths)
4. `test(release): accept gcliff on the shipped manifest` (2 paths)
5. `test(release): record the final native checks` (4 paths)
6. `docs(wiki): document git-cliff provisioning` (4 paths)
7. `docs(git-cliff-provisioning): record step 8 validation` (2 paths)

### Findings and boundaries for step 8 git-cliff-provisioning (exchange 1) (round 1)

Unresolved findings:

- High. `tests/unit/tools/release_workflow/git_cliff_native_launcher.py:156` returns the first system-wide match for the cached executable. The caller at line 250 starts its own batch process but never checks that its selected launcher belongs to that process. A simultaneous legitimate invocation can lose its launcher, and the recorded observations can describe the wrong run. Establish ownership before destructive operations and fail safely on ambiguity. Cover competing candidates with simulated identities before refreshing native evidence.
- `tools/release_workflow/bootstrap.py:219` captures cwd and configures streams while the entry kind is still unset. For a valid gcliff call, an OSError there returns the release readiness status 2 and an interruption returns 1. Determine the applicable status before either fallible operation. Inject failures at both boundaries and preserve the existing release behavior.
- `tools/release_workflow/git_cliff/launcher.py:128` handles failures from leaving the console context as launch failures even after the invocation returned its outcome. Handler removal at `windows_child.py:616` can raise through the checked native binding. Preserve the confirmed exit status and test removal failure after a distinct child status as well as registration failure before the child.
- `bin/gcliff.bat:65` expands an inherited environment variable named `ERRORLEVEL` in preference to cmd's dynamic exit status. An inherited value of 0 can hide a failed child. Preserve the actual exit status across cleanup and cover caller-defined ERRORLEVEL for successful and failing children while preserving the environment contract.
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py:205` runs already-imported command and configuration functions after deleting provisioning entries from the module cache. Eager imports during command initialization escape observation. Comparing output with an invalid budget also misses a lookup whose result is discarded. Exercise fresh command imports and observe budget-key access during the specified operations. The separate configuration fresh-import test already covers that import boundary.

Boundary-crossing work: None.

### Writer instructions for step 8 git-cliff-provisioning (exchange 1) (round 1)

Address the five findings in the reviewed step and add the specified regression cases. Refresh final native evidence after the recorder verifies process ownership, run the required writer validation, and reconcile the validation document and umbrella completion claim with the resulting evidence before submitting the new staged tree.

### Decision rationale for step 8 git-cliff-provisioning (exchange 1) (round 1)

Exact request identity and baseline index passed. Implementation completeness failed on recorder ownership and status propagation. Validation and coverage evidence failed on the native attribution and behavioral test gaps despite the writer's green suite. Staged attribution passed. Five current findings remain open in this first round. Mechanical commit grouping passed. Disposition is changes-requested.

### Final reviewer decision for step 8 git-cliff-provisioning (exchange 1) (round 1)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-1 -->

## Round 2 by requestor - Step 8

- Recorded: 2026-11-22T21:53:29+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 git-cliff-provisioning (round 2)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 8
Review round: 2

### Code review evidence for step 8 git-cliff-provisioning (round 2)

request_index_tree: 49e106ef77109426c899a0888bfa4d1e883da801
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --full=cov --whole-suite` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): observe worktree presence for gcliff
group 1 path: tools/release_workflow/git.py
group 1 path: tools/release_workflow/paths.py
group 1 path: tests/unit/tools/release_workflow/repository_simulation.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
group 2: feat(release): add the gcliff launcher
group 2 path: tools/release_workflow/invocation.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: tools/release_workflow/git_cliff/launcher.py
group 2 path: tools/release_workflow/git_cliff/__init__.py
group 2 path: bin/gcliff.bat
group 2 path: bin/gcliff.doskey
group 2 path: .gitattributes
group 3: test(release): drive gcliff through the simulation
group 3 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 3 path: tests/unit/tools/release_workflow/gcliff_simulation.py
group 3 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 4: test(release): accept gcliff on the shipped manifest
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
group 5: test(release): record the final native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_ownership.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(wiki): document git-cliff provisioning
group 6 path: wiki/reference/git-cliff-provisioning.md
group 6 path: wiki/reference/aliases-and-launchers.md
group 6 path: wiki/reference/automation-and-direct-invocation.md
group 6 path: wiki/README.md
group 7: docs(git-cliff-provisioning): record step 8 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 7 path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: .gitattributes
staged path: bin/gcliff.bat
staged path: bin/gcliff.doskey
staged path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/gcliff_simulation.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_ownership.py
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/launcher.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/paths.py
staged path: wiki/README.md
staged path: wiki/reference/aliases-and-launchers.md
staged path: wiki/reference/automation-and-direct-invocation.md
staged path: wiki/reference/git-cliff-provisioning.md
```

### Validation scope for step 8 git-cliff-provisioning (round 2)

Validation scope: the whole suite.

### Requestor assessment for step 8 git-cliff-provisioning (round 2)

Writer assessment for Step 8 of the git-cliff-provisioning plan, round 2: the
step is fully implemented. The five round 1 findings are repaired, and the new
implementation check records `Yes. Step 8 has been fully implemented.` in the
staged validation plan, with the repairs listed and the missing-work section
removed; the document status stays `Yes, it is implemented.` and the umbrella
row of item 3 stays completed.

Evidence, on the staged tree:

- Targeted: `ghog single` on the bootstrap, launcher, launchers, acceptance,
  native ownership, native evidence, version acceptance and configuration
  leaves, exit 0 (400 tests) before the recorder; the evidence and ownership
  leaves again after it.
- Native recorder by hand, outside pytest, after the last edit of a covered
  source: `python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone final --output
  tests\unit\tools\release_workflow\test_git_cliff_native_evidence\native_checks.v1.json`,
  exit 0, 16 of 16 checks passed, among them the ownership-bound launcher
  check (10.4 s) and the inherited `ERRORLEVEL` check (22.8 s); recorder
  timeout demonstration within its bound.
- By hand: `bin\gcliff.bat --frobnicate` with an inherited `ERRORLEVEL=0`
  returned 2; `--version` with `ERRORLEVEL=7` returned 0; a `get_env`
  template showed git-cliff receiving `seen=7`.
- Default walk `ghog day --whole-suite`: exit 0 after the repairs and the
  recorder.
- Review validation `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed`, 8229 tests, slowest
  call 0.31 s (outside this step), on index tree
  `49e106ef77109426c899a0888bfa4d1e883da801`, identical before and after the
  walk. No budget was changed and no exclusion is accepted.
- Plan validation `ghog day --full=cov --whole-suite`: exit 0 on the same
  tree, reusing that speed proof (`proof=speed reused=all`).
- `rg -n 'gcliff' senv.doskey` and `rg -n 'returning 1' bin/gcliff.bat`: no
  match. `test_codepage_tdd.py` is unchanged and passes.
- Line counts: every Python file below 550 (the largest new or changed:
  `test_git_cliff_acceptance_tdd.py` 407, `git_cliff_native_launcher.py` 382,
  `test_bootstrap_tdd.py` 381); advisory overruns recorded as variance.
- Markdown check and cSpell: clean on the validation plan and the wiki pages.

Please check in particular: `owned_run` and how the launcher check builds its
table and opens the processes before ending anything; `requested_kind` and
the early-failure statuses; `_run` after a filter removal failure; the
`ERRORLEVEL` deletion's place in `bin/gcliff.bat` and the new native check;
and the collection-time fresh import with its watched budget name.

### Implementation report for step 8 git-cliff-provisioning (round 2)

Step 8, "The gcliff launcher, integrated acceptance, final native checks and
documentation", is the last of eight steps of the git-cliff-provisioning plan.
It ships `gcliff`, the typed worktree presence it needs, the integrated
acceptance tests, the final native check record and the reference
documentation.

Worktree presence and discovery:

- `git.py`: `WorktreePresence` (`INSIDE`, `NO_WORKTREE`, `NO_REPOSITORY`) and
  `GitExecutionContext.worktree_presence(*, cwd)`, one `rev-parse
  --is-inside-work-tree` call through `run` with `check=False`: `true\n` is
  inside, `false\n` (a bare repository or a `.git` directory) is no worktree,
  exit 128 whose stderr starts with `fatal: not a git repository` is no
  repository (the controlled environment sets `LC_ALL=C`), and every other
  answer raises `GitCommandError`.
- `paths.py`: `find_worktree(start, git)` inspects the configuration, asks the
  presence once and, inside a worktree, returns the identity through
  `_discovered`, the helper `discover_project` now also uses, so the
  configuration is inspected once per call. `discover_project` keeps its
  behavior; its tests are unchanged.

Entry kind and bootstrap:

- `invocation.py`: `gcliff-batch` joins `ENTRY_KINDS`; `validate_arguments`
  applies the batch guard to it as to every `-batch` kind.
- `bootstrap.py`: `_ENGINES` maps the kind to
  `tools.release_workflow.git_cliff.launcher`, `_UNNORMALIZED_KINDS` holds it,
  and `_unnormalized` calls a `Launcher` protocol with the arguments, the
  original cwd, the tooling root and the verified identity. `_FAILURE_STATUS`
  gives `gcliff-batch` 69 for readiness and invocation failures and for an
  execution failure before the launcher or escaping it; every other kind keeps
  `(2, 1)`. Since round 1, `requested_kind` reads the kind of a well-formed
  prefix before the cwd capture and the stream setup, so a failure of either,
  or a repeated `--entry-kind` in gcliff arguments, is 69 for gcliff while a
  release kind or a malformed prefix keeps 2 or 1. `main` keeps its one status
  set literal, which the cross-site contract of `test_codepage_tdd.py` reads.

Launcher (`tools/release_workflow/git_cliff/launcher.py`):

- `main(arguments, *, original_cwd, tooling_root, runtime, environment=None,
  seams=None)`: the batch guard (diagnostic naming `cliff.toml`), the Git
  context from the caller's environment and directory, `find_worktree`, the
  whole configuration and `configured_pin` inside a worktree or
  `default_version` outside one, `admitted` from the seam's pin table,
  `provisioning_budget`, then `provision(..., caller="gcliff")`.
- The run: `invocation.run(arguments, policy=Policy.PASSTHROUGH,
  cwd=original_cwd, environment=environment, output="inherit")` inside the
  console filter, inside `with invocation:`; with `environment=None` the
  child inherits the process environment as is. The child's status is
  returned unchanged; since round 1, also when leaving the filter fails after
  git-cliff ended, which writes its `gcliff:` line.
- Every failure before the child, a refused creation, an unconfirmed end, an
  interruption or a filter that cannot register writes one `gcliff: <detail>`
  line and returns `GCLIFF_UNAVAILABLE = 69`.
- `LauncherSeams(provisioning, console=ignore_console_interrupts,
  pins=ADMITTED_PINS)` and `production_seams(runtime)`; `main` binds the
  production seams with the verified runtime's interpreter when none is given.

Batch file and alias:

- `bin/gcliff.bat` is `bin/release_workflow.bat` with four changes:
  `set "_release_status=69"` followed by a comment line, `--entry-kind
  gcliff-batch`, `goto cleanup` in place of the five normalization lines, and
  (round 1) a comment line and `set "ERRORLEVEL="` between the child and the
  status capture, inside `setlocal`.
  It was derived by a script from the release launcher and written with CRLF;
  `.gitattributes` gives it `text eol=crlf`; the index holds LF.
- `bin/gcliff.doskey`: `gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*`, one
  line; `senv.doskey` is unchanged.

Tests:

- Launcher leaf `test_git_cliff_launcher/` (30 cases): every launcher case of
  the plan through the launcher simulation, with the provisioning world as the
  fake provisioning seam and fake child launcher and a fake kernel for the
  console filter; plus status 101, an interruption, a filter that cannot
  register, a filter removal failing after a status-3 run (round 1), a
  manifest admitting no pin, `main` without seams and the production seams.
- `test_launchers/test_gcliff_source_tdd.py`: the derivation equality (four
  changes), the 69 assignment before the record checks, no normalization, the
  `ERRORLEVEL` deletion only after the child, the code page restore after a
  readiness error and after a child return, the alias fragment, `senv.doskey`
  without a gcliff macro, the attribute line.
- Bootstrap leaf: the plan's cases, plus (round 1) fault injection at the cwd
  capture and the stream setup for gcliff, a release kind and a malformed
  prefix, and `requested_kind`. Invocation, Git and paths leaves: the plan's
  cases.
- Acceptance leaf: `test_git_cliff_acceptance_tdd.py` and
  `test_gcliff_acceptance_tdd.py`, every Step 8 row of the ownership map
  against the shipped manifest; rows that download use a synthetic 2.14.2
  table through the launcher seams, since no test downloads the published
  asset. Round 1: the operations free of git-cliff run on command modules
  imported fresh at collection (27 modules, about 0.09 s of CPU, more than one
  test lifecycle may spend), each in its own case, with the budget variable's
  name watched in the command environment and in `os.environ`, and a control
  case for the watch.
- Support: `launcher_simulation.py` (gcliff entry with seams,
  `worktree_presence` routed to the sandbox, `patch_git` for a given context
  class), `gcliff_simulation.py` (new, the scenario builder),
  `repository_simulation.py` (declared presences), `git_cliff_children_fake.py`
  (a `gcliff --version` run inherits standard input, so it is a run, not a
  probe).

Final native record:

- Milestone `final`: the 14 checks of Steps 2, 4 and 5 on the final sources
  and two new checks in `git_cliff_native_launcher.py`, all 16 passed:
  `guard-held-by-gcliff-run-after-launcher-killed` (10.4 s of a 120 s bound)
  and `gcliff-status-with-inherited-errorlevel` (22.8 s of 120 s).
- The launcher check runs the warm-up `bin\gcliff.bat --version`, then the
  production launcher with `--from-context <named pipe>` on a pipe the
  recorder serves and never writes, so git-cliff waits on its own file object
  and no handle the launcher shares has a pending read. Since round 1 it takes
  git-cliff and its launcher from `git_cliff_native_ownership.owned_run`, the
  one run whose chain of older parents reaches the check's own `cmd.exe`, and
  opens each checked against its recorded creation time. It scans the
  launcher's handle values for the job (`IsProcessInJob`, duplicate kept) and
  the guard (the handle naming the executable), kills the launcher, then
  observes git-cliff alive, its handle of the guard's value naming the
  executable, the rename refused, and the rename allowed once the job ended
  git-cliff and during a guard-free control run of its own child. The rename
  is undone at once, so the production entry stays valid.
- The `ERRORLEVEL` check builds a one-release context from this git-cliff's
  own `--context` output, then runs `bin\gcliff.bat` with `ERRORLEVEL=0` and
  `--frobnicate` (status 2), and with `ERRORLEVEL=7` and a template printing
  `get_env(name="ERRORLEVEL")` (status 0, output `seen=7`).
- The validator requires the Step 5 stand-in check and both new checks at
  `final`, and binds the launcher, the batch file, the ownership rule and the
  modules on their path.

Documentation: `wiki/reference/git-cliff-provisioning.md` (new), the
git-cliff launcher section of `aliases-and-launchers.md`, the provisioning
availability and the statuses 2 and 69 in
`automation-and-direct-invocation.md`, and the link in `wiki/README.md`.

Also staged: the validation plan's Step 8 sections and document status, and
the umbrella row of item 3.

Writer notes: `.reviews/a.git-cliff-provisioning.step8.journal.md` and
`.reviews/a.git-cliff-provisioning.step8.handoff.md`.

### Change summary for step 8 git-cliff-provisioning (round 2)

Staged paths (35), grouped in the root `a.commit` (seven groups, checker
`ready: true`). Round 2 adds three paths to group 5 and amends the messages of
groups 2 to 5 for the repairs; boundaries and order are unchanged.

1. `feat(release): observe worktree presence for gcliff`:
   `tools/release_workflow/git.py`, `tools/release_workflow/paths.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py`.
2. `feat(release): add the gcliff launcher`:
   `tools/release_workflow/invocation.py`, `tools/release_workflow/bootstrap.py`,
   `tools/release_workflow/git_cliff/launcher.py`,
   `tools/release_workflow/git_cliff/__init__.py`, `bin/gcliff.bat`,
   `bin/gcliff.doskey`, `.gitattributes`.
3. `test(release): drive gcliff through the simulation`:
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/gcliff_simulation.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
4. `test(release): accept gcliff on the shipped manifest`:
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py`.
5. `test(release): record the final native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_ownership.py` (new),
   `tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py` (new),
   `tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py` (new),
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_launcher.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
6. `docs(wiki): document git-cliff provisioning`:
   `wiki/reference/git-cliff-provisioning.md`,
   `wiki/reference/aliases-and-launchers.md`,
   `wiki/reference/automation-and-direct-invocation.md`, `wiki/README.md`.
7. `docs(git-cliff-provisioning): record step 8 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`,
   `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`.

Every staged file has LF line endings in the index (`bin/gcliff.bat` checks
out with CRLF through its attribute). The review transcript stays out of
`a.commit`, for its residual commit after the review.

### Writer response for step 8 git-cliff-provisioning (round 2)

Writer response:

Writer response:

All five round 1 findings are accepted and repaired; none is disputed. The
reviewer's staged validation plan edits (the No verdict, the missing work and
the integrity notes) were the starting point of the new implementation check,
which records Yes again with the repairs and removes the missing-work section
now that each item is done.

1. High, final native check ownership: the check no longer takes the first
   system-wide run of the executable. `git_cliff_native_ownership.owned_run`
   picks the one run whose chain of parents, each created no later than its
   child, reaches the check's own `cmd.exe` by PID and creation time; none yet
   keeps it waiting, two own runs or a run started by the root itself stop it
   with `OwnershipError` before anything is ended. The run and its launcher
   are then opened and checked against their recorded creation times before
   the launcher is killed or the job ended. Competing candidates are covered
   with simulated tables in the new unit leaf (a foreign run of the same image
   listed first or last, foreign runs only, two own runs, a run without a
   launcher, a reused root PID, a parent newer than its child, a missing
   parent, an unreadable creation time, a parent cycle). The record was
   refreshed with this recorder: 16 checks passed.
2. Early bootstrap failures: `requested_kind` reads the kind of a well-formed
   prefix before the cwd capture, so an `OSError` there or in the stream setup
   is 69 for a gcliff call and 2 for a release kind, and an interruption is 69
   or 1; a malformed prefix keeps the release statuses. `InvocationError.kind`
   is gone, since the requested kind now covers the repeated `--entry-kind`
   too. Fault injection covers both boundaries for both kinds.
3. Console filter removal: `_run` keeps the outcome once git-cliff ended; a
   failure leaving the filter then writes its `gcliff:` line and returns
   git-cliff's status. The launcher leaf adds removal failing after a status-3
   run, beside the existing registration failure (69, no run).
4. Inherited `ERRORLEVEL`: `bin/gcliff.bat` runs `set "ERRORLEVEL="` between
   the child and the capture, inside its `setlocal`. A probe showed that this
   deletion leaves cmd's dynamic status unchanged, also when no such variable
   exists. The child still inherits the caller's variable, and `endlocal`
   restores it for the caller. The source contract checks the order. A new
   final native check runs the production batch file with `ERRORLEVEL=0` and a
   usage error (2), then with `ERRORLEVEL=7` and a `get_env` template (0, and
   git-cliff printed `seen=7`). The release launchers read `%ERRORLEVEL%` the
   same way; that pre-existing behavior of items 1 and 2 is outside this step
   and left unchanged.
5. Operations free of git-cliff: a fresh import of the release package costs
   about 0.09 s of CPU (27 modules), more than one test lifecycle may spend, so
   the command entry points and the modules they import lazily are imported
   fresh once at collection, the originals restored at once. `version`,
   `versions check` and a configuration load each run on those fresh modules,
   so their eager imports are the fresh package's and a lazy import loads
   anew; the budget variable's name is watched in the command environment (a
   name object recording every comparison, the case-insensitive `upper()` one
   included) and in `os.environ`, and none is recorded. A control test shows
   the watch recording a budget resolution, a discarded lookup and an
   `os.environ` lookup.

### Reviewer focus for step 8 git-cliff-provisioning (round 2)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-2 -->

## Round 2 by reviewer - Step 8

- Recorded: 2026-11-22T21:57:33+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 git-cliff-provisioning (exchange 1) (round 2)

Baseline index tree: 49e106ef77109426c899a0888bfa4d1e883da801

Assessed index tree: cf33b030b02431a89c63a32d5e1f79dac1f79642

### Implementation check for step 8 git-cliff-provisioning (exchange 1) (round 2)

Result:

No. Step 8 has NOT been fully implemented.

The writer repaired all three reported production status paths. Process identity and import isolation improved. The native recorder and AC6 test still leave the two gaps below.

Validation plan effects:

Only Step 8 rows in `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md` were edited and staged by the reviewer. They record the remaining work, behavioral coverage gaps and improved process isolation. The protected umbrella digest matched.

### Pre-repair mandatory checks and coverage for step 8 git-cliff-provisioning (exchange 1) (round 2)

Writer evidence on the matching request tree reports 8,229 tests, 100% coverage, zero duration outliers, final coverage proof and 16 passed native checks. Reviewer assessed the staged code, regression cases and native evidence statically. The reviewer did not repeat a suite or run the native recorder.

### Resolved validation set and sources for step 8 git-cliff-provisioning (exchange 1) (round 2)

`ghog day --full=speed --whole-suite` (project) then `ghog day --full=cov --whole-suite` (plan). The mandatory scope is the bound whole suite.

### Resolver drift and direction for step 8 git-cliff-provisioning (exchange 1) (round 2)

None. The current project default, whole-suite requirement and step 8 coverage command match the request in order and source. No project override is present.

### Repository state around validation for step 8 git-cliff-provisioning (exchange 1) (round 2)

Pre-edit validation blob matched the writer's staged blob. Validation-state comparison flagged only the reviewer's expected step 8 edit, with no untracked or ignored side effects. Patch attribution succeeded and all changed hunks were within the reviewed step. All 35 paths retained their original group membership.

### Repair inventory for step 8 git-cliff-provisioning (exchange 1) (round 2)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 8 git-cliff-provisioning (exchange 1) (round 2)

Independent checks returned ready before and after the metadata edit. Positions, subjects, ordered path membership and staged inventory match the request, with no diagnostics.

1. `feat(release): observe worktree presence for gcliff` (5 paths)
2. `feat(release): add the gcliff launcher` (7 paths)
3. `test(release): drive gcliff through the simulation` (8 paths)
4. `test(release): accept gcliff on the shipped manifest` (2 paths)
5. `test(release): record the final native checks` (7 paths)
6. `docs(wiki): document git-cliff provisioning` (4 paths)
7. `docs(git-cliff-provisioning): record step 8 validation` (2 paths)

### Findings and boundaries for step 8 git-cliff-provisioning (exchange 1) (round 2)

Unresolved findings:

- The native guard check at `tests/unit/tools/release_workflow/git_cliff_native_launcher.py:335` accepts the first matching descendant of its own batch process. A valid cache hit also starts a guarded `--version` process before the actual passthrough run (`tools/release_workflow/git_cliff/provisioning.py:216`). Both processes have the same image and launcher parent. If the snapshot catches the probe, the recorder may fail on an already-exited process or exercise the probe instead of the child waiting on its unique pipe. Gate the observation on positive readiness from that invocation's pipe, retaining the new ownership checks. Exercise the probe-to-run transition and failure to reach readiness, then refresh final native evidence.
- `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py:317` imports the fresh command package at collection. The process-environment watcher is first installed inside the parametrized test, after import. A command module could read and discard the budget variable during normal startup and all three AC6 cases would still pass. Cover the import interval with the watcher and prove it observes a discarded import-time lookup. The current tests already cover eager provisioning imports and lookups during command execution.

Boundary-crossing work: None.

### Writer instructions for step 8 git-cliff-provisioning (exchange 1) (round 2)

Close the two evidence gaps, refresh the native record, rerun writer validation and reconcile the completion metadata with the results before submitting another round.

### Decision rationale for step 8 git-cliff-provisioning (exchange 1) (round 2)

Exact identity passed. Implementation completeness and validation evidence remain open for the two acceptance boundaries above. Staged attribution passed. The three status findings are closed, and the two evidence findings are partially resolved. Ordered commit grouping passed. Changes requested.

### Final reviewer decision for step 8 git-cliff-provisioning (exchange 1) (round 2)

Decision: changes-requested. The writer must address the concrete instructions and publish another review round. This advisory answer does not authorize a commit.

<!-- review-entry-id: answer-step-8-round-2 -->

## Round 3 by requestor - Step 8

- Recorded: 2026-11-23T00:25:33+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: request

### Review identity for step 8 git-cliff-provisioning (round 3)

Umbrella draft: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
Implementation plan: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
Implementation step: 8
Review round: 3

### Code review evidence for step 8 git-cliff-provisioning (round 3)

request_index_tree: 7a727d1b38074448e10ab31f781e299e549b510a
resolved_validation_set:

- `ghog day --full=speed --whole-suite` (sources: project)
- `ghog day --full=cov --whole-suite` (sources: plan)

test_scope:
{"fingerprint": "686958cdf490661b3207a810e06364a48e923f6bf1c8c33c9a555c7f23cc75b6", "group": null, "proof": "speed", "requirement": "docs/v0.14.0/feature-request.v0.14.0.git-cliff-provisioning.md", "scope": "whole"}

commit_plan_result:

```text
state: valid
ready: true
group 1: feat(release): observe worktree presence for gcliff
group 1 path: tools/release_workflow/git.py
group 1 path: tools/release_workflow/paths.py
group 1 path: tests/unit/tools/release_workflow/repository_simulation.py
group 1 path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
group 1 path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
group 2: feat(release): add the gcliff launcher
group 2 path: tools/release_workflow/invocation.py
group 2 path: tools/release_workflow/bootstrap.py
group 2 path: tools/release_workflow/git_cliff/launcher.py
group 2 path: tools/release_workflow/git_cliff/__init__.py
group 2 path: bin/gcliff.bat
group 2 path: bin/gcliff.doskey
group 2 path: .gitattributes
group 3: test(release): drive gcliff through the simulation
group 3 path: tests/unit/tools/release_workflow/launcher_simulation.py
group 3 path: tests/unit/tools/release_workflow/gcliff_simulation.py
group 3 path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
group 3 path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
group 3 path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
group 4: test(release): accept gcliff on the shipped manifest
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
group 4 path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
group 5: test(release): record the final native checks
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_ownership.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
group 5 path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
group 5 path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
group 6: docs(wiki): document git-cliff provisioning
group 6 path: wiki/reference/git-cliff-provisioning.md
group 6 path: wiki/reference/aliases-and-launchers.md
group 6 path: wiki/reference/automation-and-direct-invocation.md
group 6 path: wiki/README.md
group 7: docs(git-cliff-provisioning): record step 8 validation
group 7 path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
group 7 path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: .gitattributes
staged path: bin/gcliff.bat
staged path: bin/gcliff.doskey
staged path: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
staged path: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md
staged path: tests/unit/tools/release_workflow/gcliff_simulation.py
staged path: tests/unit/tools/release_workflow/git_cliff_children_fake.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_checks.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_launcher.py
staged path: tests/unit/tools/release_workflow/git_cliff_native_ownership.py
staged path: tests/unit/tools/release_workflow/launcher_simulation.py
staged path: tests/unit/tools/release_workflow/repository_simulation.py
staged path: tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py
staged path: tests/unit/tools/release_workflow/test_git/test_git_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py
staged path: tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py
staged path: tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py
staged path: tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py
staged path: tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py
staged path: tools/release_workflow/bootstrap.py
staged path: tools/release_workflow/git.py
staged path: tools/release_workflow/git_cliff/__init__.py
staged path: tools/release_workflow/git_cliff/launcher.py
staged path: tools/release_workflow/invocation.py
staged path: tools/release_workflow/paths.py
staged path: wiki/README.md
staged path: wiki/reference/aliases-and-launchers.md
staged path: wiki/reference/automation-and-direct-invocation.md
staged path: wiki/reference/git-cliff-provisioning.md
```

### Validation scope for step 8 git-cliff-provisioning (round 3)

Validation scope: the whole suite.

### Requestor assessment for step 8 git-cliff-provisioning (round 3)

Writer assessment for Step 8 of the git-cliff-provisioning plan, round 3: the
step is fully implemented. Both round 2 findings are repaired, and the new
implementation check records `Yes. Step 8 has been fully implemented.` in the
staged validation plan, with the round 2 repairs and both recorder runs listed
and the missing-work section removed; the document status stays
`Yes, it is implemented.` and the umbrella row of item 3 stays completed.

Evidence, on the staged tree:

- Targeted: `ghog single` on the native ownership and acceptance leaves, exit
  0, after the repairs; the native evidence and ownership leaves again after
  the recorder.
- Probe by hand before the change: `GetNamedPipeClientProcessId` on the
  silent pipe failed with error 1168 before git-cliff 2.14.2 opened it, then
  named exactly that git-cliff process.
- Native recorder by hand, outside pytest, after the last edit of a covered
  source: the first run passed 15 of 16 checks (the unchanged Step 5 stand-in
  check observed the rename still refused after its job ended, in a run slower
  overall, as the writer response details); the immediate rerun,
  `python -m tests.unit.tools.release_workflow.git_cliff_native_checks
  --milestone final --output
  tests\unit\tools\release_workflow\test_git_cliff_native_evidence\native_checks.v1.json`,
  exit 0, passed all 16 (launcher check 10.9 s, `ERRORLEVEL` check 11.6 s,
  stand-in run check 16.4 s), and is the committed record.
- Default walk `ghog day --whole-suite`: exit 0 after the repairs.
- Review validation `ghog day --full=speed --whole-suite` (built-in default):
  exit 0 with `cov=100 outliers=0 excluded=0 proof=speed`, 8234 tests, slowest
  call 0.31 s (outside this step), on index tree
  `7a727d1b38074448e10ab31f781e299e549b510a`, identical before and after the
  walk. No budget was changed and no exclusion is accepted.
- Plan validation `ghog day --full=cov --whole-suite`: exit 0 on the same
  tree, reusing that speed proof (`proof=speed reused=all`).
- `rg -n 'gcliff' senv.doskey` and `rg -n 'returning 1' bin/gcliff.bat`: no
  match. `test_codepage_tdd.py` is unchanged and passes.
- Line counts: every Python file below 550 (the largest:
  `test_git_cliff_acceptance_tdd.py` 453, `test_bootstrap_tdd.py` 381,
  `git_cliff_native_launcher.py` 378); advisory overruns recorded as variance.
- Markdown check and cSpell: clean on the validation plan.

Please check in particular: `await_ready_run` and the pipe client as the only
possible run, with the probe-to-run and never-ready cases; the control run's
pipe check; the recorder's `TimeoutError` classification; `_watched_imports`
around the collection-time import and its in-memory control module; and the
account of the transient recorder failure and its rerun.

### Implementation report for step 8 git-cliff-provisioning (round 3)

Step 8, "The gcliff launcher, integrated acceptance, final native checks and
documentation", is the last of eight steps of the git-cliff-provisioning plan.
It ships `gcliff`, the typed worktree presence it needs, the integrated
acceptance tests, the final native check record and the reference
documentation.

Worktree presence and discovery:

- `git.py`: `WorktreePresence` (`INSIDE`, `NO_WORKTREE`, `NO_REPOSITORY`) and
  `GitExecutionContext.worktree_presence(*, cwd)`, one `rev-parse
  --is-inside-work-tree` call through `run` with `check=False`: `true\n` is
  inside, `false\n` (a bare repository or a `.git` directory) is no worktree,
  exit 128 whose stderr starts with `fatal: not a git repository` is no
  repository (the controlled environment sets `LC_ALL=C`), and every other
  answer raises `GitCommandError`.
- `paths.py`: `find_worktree(start, git)` inspects the configuration, asks the
  presence once and, inside a worktree, returns the identity through
  `_discovered`, the helper `discover_project` now also uses, so the
  configuration is inspected once per call. `discover_project` keeps its
  behavior; its tests are unchanged.

Entry kind and bootstrap:

- `invocation.py`: `gcliff-batch` joins `ENTRY_KINDS`; `validate_arguments`
  applies the batch guard to it as to every `-batch` kind.
- `bootstrap.py`: `_ENGINES` maps the kind to
  `tools.release_workflow.git_cliff.launcher`, `_UNNORMALIZED_KINDS` holds it,
  and `_unnormalized` calls a `Launcher` protocol with the arguments, the
  original cwd, the tooling root and the verified identity. `_FAILURE_STATUS`
  gives `gcliff-batch` 69 for readiness and invocation failures and for an
  execution failure before the launcher or escaping it; every other kind keeps
  `(2, 1)`. Since round 1, `requested_kind` reads the kind of a well-formed
  prefix before the cwd capture and the stream setup, so a failure of either,
  or a repeated `--entry-kind` in gcliff arguments, is 69 for gcliff while a
  release kind or a malformed prefix keeps 2 or 1. `main` keeps its one status
  set literal, which the cross-site contract of `test_codepage_tdd.py` reads.

Launcher (`tools/release_workflow/git_cliff/launcher.py`):

- `main(arguments, *, original_cwd, tooling_root, runtime, environment=None,
  seams=None)`: the batch guard (diagnostic naming `cliff.toml`), the Git
  context from the caller's environment and directory, `find_worktree`, the
  whole configuration and `configured_pin` inside a worktree or
  `default_version` outside one, `admitted` from the seam's pin table,
  `provisioning_budget`, then `provision(..., caller="gcliff")`.
- The run: `invocation.run(arguments, policy=Policy.PASSTHROUGH,
  cwd=original_cwd, environment=environment, output="inherit")` inside the
  console filter, inside `with invocation:`; with `environment=None` the
  child inherits the process environment as is. The child's status is
  returned unchanged; since round 1, also when leaving the filter fails after
  git-cliff ended, which writes its `gcliff:` line.
- Every failure before the child, a refused creation, an unconfirmed end, an
  interruption or a filter that cannot register writes one `gcliff: <detail>`
  line and returns `GCLIFF_UNAVAILABLE = 69`.
- `LauncherSeams(provisioning, console=ignore_console_interrupts,
  pins=ADMITTED_PINS)` and `production_seams(runtime)`; `main` binds the
  production seams with the verified runtime's interpreter when none is given.

Batch file and alias:

- `bin/gcliff.bat` is `bin/release_workflow.bat` with four changes:
  `set "_release_status=69"` followed by a comment line, `--entry-kind
  gcliff-batch`, `goto cleanup` in place of the five normalization lines, and
  (round 1) a comment line and `set "ERRORLEVEL="` between the child and the
  status capture, inside `setlocal`.
  It was derived by a script from the release launcher and written with CRLF;
  `.gitattributes` gives it `text eol=crlf`; the index holds LF.
- `bin/gcliff.doskey`: `gcliff="%LLM_SHARED_DIR%\bin\gcliff.bat" $*`, one
  line; `senv.doskey` is unchanged.

Tests:

- Launcher leaf `test_git_cliff_launcher/` (30 cases): every launcher case of
  the plan through the launcher simulation, with the provisioning world as the
  fake provisioning seam and fake child launcher and a fake kernel for the
  console filter; plus status 101, an interruption, a filter that cannot
  register, a filter removal failing after a status-3 run (round 1), a
  manifest admitting no pin, `main` without seams and the production seams.
- `test_launchers/test_gcliff_source_tdd.py`: the derivation equality (four
  changes), the 69 assignment before the record checks, no normalization, the
  `ERRORLEVEL` deletion only after the child, the code page restore after a
  readiness error and after a child return, the alias fragment, `senv.doskey`
  without a gcliff macro, the attribute line.
- Bootstrap leaf: the plan's cases, plus (round 1) fault injection at the cwd
  capture and the stream setup for gcliff, a release kind and a malformed
  prefix, and `requested_kind`. Invocation, Git and paths leaves: the plan's
  cases.
- Acceptance leaf: `test_git_cliff_acceptance_tdd.py` and
  `test_gcliff_acceptance_tdd.py`, every Step 8 row of the ownership map
  against the shipped manifest; rows that download use a synthetic 2.14.2
  table through the launcher seams, since no test downloads the published
  asset. Round 1: the operations free of git-cliff run on command modules
  imported fresh at collection (27 modules, about 0.09 s of CPU, more than one
  test lifecycle may spend), each in its own case, with the budget variable's
  name watched in the command environment and in `os.environ`, and a control
  case for the watch. Round 2: `os.environ` is watched during that
  collection-time import too, restored right after it, and the cases require
  no recorded read; a control module served from memory looks the variable up
  while it is imported, and the watch records it.
- Support: `launcher_simulation.py` (gcliff entry with seams,
  `worktree_presence` routed to the sandbox, `patch_git` for a given context
  class), `gcliff_simulation.py` (new, the scenario builder),
  `repository_simulation.py` (declared presences), `git_cliff_children_fake.py`
  (a `gcliff --version` run inherits standard input, so it is a run, not a
  probe).

Final native record:

- Milestone `final`: the 14 checks of Steps 2, 4 and 5 on the final sources
  and two new checks in `git_cliff_native_launcher.py`, all 16 passed in the
  committed run: `guard-held-by-gcliff-run-after-launcher-killed` (10.9 s of a
  120 s bound) and `gcliff-status-with-inherited-errorlevel` (11.6 s of
  120 s). The run before it, right after the round 2 repairs, failed one Step 5
  stand-in check transiently; see the writer response.
- The launcher check runs the warm-up `bin\gcliff.bat --version`, then the
  production launcher with `--from-context <named pipe>` on a pipe the
  recorder serves and never writes, so git-cliff waits on its own file object
  and no handle the launcher shares has a pending read. Since round 2 it waits
  until that pipe names its client (`GetNamedPipeClientProcessId`), which only
  the run does, never the guarded reuse probe the same launcher starts first;
  then, as since round 1, `git_cliff_native_ownership.owned_run` must find that
  client descending from the check's own `cmd.exe` through older parents, and
  the check opens the run and its launcher checked against their recorded
  creation times. A run that never opens the pipe is `NotReadyError`, recorded
  `timed-out`. It scans the
  launcher's handle values for the job (`IsProcessInJob`, duplicate kept) and
  the guard (the handle naming the executable), kills the launcher, then
  observes git-cliff alive, its handle of the guard's value naming the
  executable, the rename refused, and the rename allowed once the job ended
  git-cliff and during a guard-free control run, checked through its own
  pipe's client. The rename is undone at once, so the production entry stays
  valid.
- The `ERRORLEVEL` check builds a one-release context from this git-cliff's
  own `--context` output, then runs `bin\gcliff.bat` with `ERRORLEVEL=0` and
  `--frobnicate` (status 2), and with `ERRORLEVEL=7` and a template printing
  `get_env(name="ERRORLEVEL")` (status 0, output `seen=7`).
- The validator requires the Step 5 stand-in check and both new checks at
  `final`, and binds the launcher, the batch file, the ownership rule and the
  modules on their path.

Documentation: `wiki/reference/git-cliff-provisioning.md` (new), the
git-cliff launcher section of `aliases-and-launchers.md`, the provisioning
availability and the statuses 2 and 69 in
`automation-and-direct-invocation.md`, and the link in `wiki/README.md`.

Also staged: the validation plan's Step 8 sections and document status, and
the umbrella row of item 3.

Writer notes: `.reviews/a.git-cliff-provisioning.step8.journal.md` and
`.reviews/a.git-cliff-provisioning.step8.handoff.md`.

### Change summary for step 8 git-cliff-provisioning (round 3)

Staged paths (35), grouped in the root `a.commit` (seven groups, checker
`ready: true`). Round 3 keeps the round 2 membership and amends the messages
of groups 4 and 5 for the repairs; boundaries and order are unchanged.

1. `feat(release): observe worktree presence for gcliff`:
   `tools/release_workflow/git.py`, `tools/release_workflow/paths.py`,
   `tests/unit/tools/release_workflow/repository_simulation.py`,
   `tests/unit/tools/release_workflow/test_git/test_git_tdd.py`,
   `tests/unit/tools/release_workflow/test_paths/test_paths_tdd.py`.
2. `feat(release): add the gcliff launcher`:
   `tools/release_workflow/invocation.py`, `tools/release_workflow/bootstrap.py`,
   `tools/release_workflow/git_cliff/launcher.py`,
   `tools/release_workflow/git_cliff/__init__.py`, `bin/gcliff.bat`,
   `bin/gcliff.doskey`, `.gitattributes`.
3. `test(release): drive gcliff through the simulation`:
   `tests/unit/tools/release_workflow/launcher_simulation.py`,
   `tests/unit/tools/release_workflow/gcliff_simulation.py`,
   `tests/unit/tools/release_workflow/git_cliff_children_fake.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_launcher/test_git_cliff_launcher_tdd.py`,
   `tests/unit/tools/release_workflow/test_launchers/test_gcliff_source_tdd.py`,
   `tests/unit/tools/release_workflow/test_bootstrap/test_bootstrap_tdd.py`,
   `tests/unit/tools/release_workflow/test_invocation/test_invocation_tdd.py`.
4. `test(release): accept gcliff on the shipped manifest`:
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_git_cliff_acceptance_tdd.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_acceptance/test_gcliff_acceptance_tdd.py`.
5. `test(release): record the final native checks`:
   `tests/unit/tools/release_workflow/git_cliff_native_ownership.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_ownership/__init__.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_ownership/test_git_cliff_native_ownership_tdd.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_checks.py`,
   `tests/unit/tools/release_workflow/git_cliff_native_launcher.py`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/native_checks.v1.json`,
   `tests/unit/tools/release_workflow/test_git_cliff_native_evidence/test_git_cliff_native_evidence_tdd.py`.
6. `docs(wiki): document git-cliff provisioning`:
   `wiki/reference/git-cliff-provisioning.md`,
   `wiki/reference/aliases-and-launchers.md`,
   `wiki/reference/automation-and-direct-invocation.md`, `wiki/README.md`.
7. `docs(git-cliff-provisioning): record step 8 validation`:
   `docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.validation.md`,
   `docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md`.

Every staged file has LF line endings in the index (`bin/gcliff.bat` checks
out with CRLF through its attribute). The review transcript stays out of
`a.commit`, for its residual commit after the review.

### Writer response for step 8 git-cliff-provisioning (round 3)

Writer response:

Writer response:

Both round 2 findings are accepted and repaired; none is disputed. The
reviewer's staged validation plan edits (the No verdict and the missing work)
were the starting point of the new implementation check, which records Yes
again with the round 2 repairs and removes the missing-work section.

1. Run and reuse probe: on a valid entry the launcher first runs the guarded
   `--version` reuse probe, which has the same image and the same launcher
   parent as the run. The check now takes its run only once its own pipe
   names that client: `GetNamedPipeClientProcessId` fails (error 1168) until
   a process opens the pipe, which the probe never does, and then names
   exactly the process that opened it, checked by hand against git-cliff 2.14.2
   before the change. `await_ready_run` waits for that client, then
   `owned_run(..., run=client)` must find it descending from the check's own
   `cmd.exe`, or the check stops with `OwnershipError` before ending
   anything; no client within the bound raises `NotReadyError`, a
   `TimeoutError` that the recorder now records `timed-out`. Its clock and
   sleep are injected, so the unit leaf covers the probe-to-run transition, a
   probe still listed beside the run (where `owned_run` without the client
   would refuse two runs), a run that never opens its pipe and a pipe client
   outside the check's own tree. The control run, which also waits on a
   silent pipe, checks that pipe's client before its rename attempt.
2. Import-time budget reads: the collection-time fresh import now runs inside
   `_watched_imports`, with `os.environ` replaced by the watch and restored in
   `finally` right after it; the parametrized tests require that no read was
   recorded during that import. A control module, served from memory by a
   meta-path finder (the pytest temporary directory is an in-memory
   filesystem the import system cannot read), looks the budget variable up
   and discards it while it is imported, and the watch records that lookup.

Native record: the first rerun after these repairs passed 15 of 16 checks.
The Step 5 stand-in check `guard-held-by-git-cliff-run-after-caller-killed`,
unchanged since its earlier passing runs, observed the rename still refused
after its job had ended (`after_child: refused`, every other observation as
expected), in a run slower overall (another guard check took 15.4 s instead
of about 5 s): a transient outside holder of the freshly written stand-in,
such as an antivirus scan, is the likely cause. The immediate rerun passed all
16 checks, that one in 16.4 s of its 60 s bound, and is the committed record.
Both runs are in the step journal.

### Reviewer focus for step 8 git-cliff-provisioning (round 3)

Check the exact plan step, staged implementation, test evidence, repaired path inventory, and a.commit accuracy.

<!-- review-entry-id: request-step-8-round-3 -->

## Round 3 by reviewer - Step 8

- Recorded: 2026-11-23T00:28:03+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: answer

### Assessed index identity for step 8 git-cliff-provisioning (exchange 1) (round 3)

Baseline index tree: 7a727d1b38074448e10ab31f781e299e549b510a

Assessed index tree: 7a727d1b38074448e10ab31f781e299e549b510a

### Implementation check for step 8 git-cliff-provisioning (exchange 1) (round 3)

Result:

Yes. Step 8 has been fully implemented.

The recorder now obtains the client PID from its own named pipe and requires a matching executable and process ancestry before it acts. The regression cases cover the preceding probe, a lingering probe, a client outside the batch tree and readiness timeout. The fresh command imports now run with budget reads observed, with a discarded import-time lookup as a positive control. Both round 2 findings are closed.

Validation plan effects:

The staged step 8 rows already record the correct Yes verdict and both repairs. The reviewer made no tracked changes. The umbrella digest matched.

### Pre-repair mandatory checks and coverage for step 8 git-cliff-provisioning (exchange 1) (round 3)

The writer reports 8,234 tests, 100% coverage and zero duration outliers for the request tree. The staged final native record contains 16 passed observations, each matching its expectation within its bound. The writer disclosed an earlier run in which one pre-existing stand-in check saw a refused rename after job exit. The cause remains unconfirmed. That check passed on the rerun. Reviewer evidence was static and the reviewer did not repeat the suite or the native recorder.

### Resolved validation set and sources for step 8 git-cliff-provisioning (exchange 1) (round 3)

Whole-suite `ghog day --full=speed --whole-suite` (project), followed by `ghog day --full=cov --whole-suite` (plan). The writer recorded a green speed walk and reuse of that proof for coverage.

### Resolver drift and direction for step 8 git-cliff-provisioning (exchange 1) (round 3)

None. The built-in speed default, whole-suite requirement and step 8 final coverage command match the request. There is no project override.

### Repository state around validation for step 8 git-cliff-provisioning (exchange 1) (round 3)

Baseline and assessed trees both equal `7a727d1b38074448e10ab31f781e299e549b510a`. The ordered validation-state comparison was acceptable with zero changed paths. The protected umbrella's digest matched.

### Repair inventory for step 8 git-cliff-provisioning (exchange 1) (round 3)

Repairs made: None.

Paths staged: None.

### Commit plan assessment for step 8 git-cliff-provisioning (exchange 1) (round 3)

The independent checker returned ready, exit 0, with 35 staged paths in seven groups and zero diagnostics. All positions, subjects and ordered path lists match the request. The changes since round 2 belong to the acceptance tests, native checks and step validation groups.

1. `feat(release): observe worktree presence for gcliff` (5 paths)
2. `feat(release): add the gcliff launcher` (7 paths)
3. `test(release): drive gcliff through the simulation` (8 paths)
4. `test(release): accept gcliff on the shipped manifest` (2 paths)
5. `test(release): record the final native checks` (7 paths)
6. `docs(wiki): document git-cliff provisioning` (4 paths)
7. `docs(git-cliff-provisioning): record step 8 validation` (2 paths)

### Findings and boundaries for step 8 git-cliff-provisioning (exchange 1) (round 3)

Unresolved findings: None.

Boundary-crossing work: None.

### Writer instructions for step 8 git-cliff-provisioning (exchange 1) (round 3)

No further implementation work was identified for step 8. The requestor owns the convergence decision.

### Decision rationale for step 8 git-cliff-provisioning (exchange 1) (round 3)

All six readiness criteria pass. Identity and index match, the implementation covers the step, the writer's validation and the reviewed regression evidence support the acceptance rows, staged scope is attributable, all carried findings are closed and the commit plan is accurate. The reviewer made no substantive repairs. The recommendation is advisory.

### Final reviewer decision for step 8 git-cliff-provisioning (exchange 1) (round 3)

Decision: commit-ready (advisory). The evidence floor is complete, but this recommendation does not authorize a commit; authority remains at the durable human gate.

<!-- review-entry-id: answer-step-8-round-3 -->

## Round 3 by human - Step 8 - human-confirmation

- Recorded: 2026-11-23T01:32:46+01:00
- Exchange: code/code/v0.14.0/git-cliff-provisioning
- Umbrella: docs/v0.14.0/draft.v0.14.0.sibling_release_tooling.md
- Reviewed document: docs/v0.14.0/plan.v0.14.0.git-cliff-provisioning.md
- Requestor LLM nature: claude
- Reviewer LLM nature: codex
- Implementation step: 8
- Outcome: human-confirmation

Human choice: Commit
Outcome: continue-owning-workflow

<!-- review-entry-id: human-confirmation-round-3 -->
