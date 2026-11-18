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
