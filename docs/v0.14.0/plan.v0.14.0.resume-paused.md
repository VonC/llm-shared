# v0.14.0 resume-paused implementation plan

Implement the human-launched resume workflow through shared artifact parsing, independently validated receivers and guarded pane delivery.

## Plan goal and scope for resume-paused

Implement [the requirement](feature-request.v0.14.0.resume-paused.md) and [the consolidated design](design.v0.14.0.resume-paused.md) beside [the canonical draft](draft.v0.14.0.resume-paused.md). The numbered steps below cover both Claude and Codex on Windows with Python 3.12 compatibility.

- **Step 1 goal**: Establish usable read-only evidence for both hosts before enabling any delivery.
- **Step 2 goal**: Provide strict shared inputs and a pure exact-exchange observation boundary.
- **Step 3 goal**: Make newly paused sessions carry complete machine-readable assignments while retaining manual and installed-launcher readability.
- **Step 4 goal**: Bind human launch consent to independently proved latest input and the exact receipt/claim operation.
- **Step 5 goal**: Classify every prompt-bearing checkout and produce deterministic safe preview actions.
- **Step 6 goal**: Execute one safe action at a time per checkout while independent checkouts progress concurrently.
- **Step 7 goal**: Separate acceptance, consumption and current ownership, then safely handle reviewer continuation.
- **Step 8 goal**: Expose human-only command/reporting and validate the full two-host workflow with fake TUIOS.

Implement the documented `resume_paused [--dry-run] [--clear] [--except NAME[,NAME...]] [--switch-roles NAME[,NAME...]]` interface. Agents must never launch the bulk CLI, including preview or at a person's request. Tests use injected fake TUIOS; the separate receiving validator is agent-callable and read-only.

The [deferred senv integration checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up) remains unchecked and must appear in validation and completion handoffs. This delivery preserves installed `tuitp` grammar through fixtures; it does not validate full eligible-session startup/restoration coverage. No automatic legacy routing converter, live delivery experiment, claim-history file or authorization/continuation artifact belongs to this implementation.

## File-based IO cost clarification for resume-paused

Read the exact artifact-home declaration, prompt/receipt and selected exchange paths, plus the private journal index when needed. Index checkout/pane identities once per observation; avoid broad document or Markdown scans. Full latest-input proof may require reading candidate host session files, so account for bytes read and reject incomplete evidence. Re-read mutable prompt, receipt, routing, live pane/input and claim evidence at every safety boundary; never cache it as authorization. The bulk reader writes none of these files. Receiver-only persisted updates retain existing atomic replacement and locked claim semantics.

## Complexity and evidence-cost bounds

Discovery and grouping cost O(P + C) for P panes and C checkouts using maps keyed by canonical root and full UUID. Each refresh costs the evidence actually inspected: O(P + J + B + E), where J is relevant journal bytes, B is host-input evidence bytes and E is exact exchange evidence. Do not promise constant-time transcript lookup or skip a required fresh check to meet a timing estimate. Independent workers may each refresh this state; measure that cost instead of hiding it behind stale caches. Avoid pairwise pane searches and repeated broad artifact scans. The fixed 100-second delivery/acceptance and 120-second post-acceptance budgets are design requirements, not asymptotic claims.

## Confirmed source and test-tree facts

The current tree contains root `tools`, Windows launchers under `bin`, canonical session workflows under `instructions`, templates, unit packages and process acceptance packages. No bulk resume module or shared session prompt/receipt parser exists. The private session journal is instruction-managed; `review_artifact_journal.py` is the separate implementation-step journal, not a bulk-session authority.

`ReviewArtifactConfiguration.load` resolves without preparing a home. `derive_artifact_paths`, `ReviewExchangeObserver` and `observe_transition` supply reusable exact-path observation. Normal core/home preparation and migration are forbidden in the bulk reader. `claim_selected` already rechecks selected round/occurrence under the transition lock; retain that transaction. Ownership issuance already advances a generation and stores only a token digest. Existing record-replacement transitions must preserve the added current-claim binding; new claims must clear or replace it.

### Physical-line baselines for existing changed files

Counts were taken at HEAD `f182d418` before plan edits, including blank lines, by iterating physical text lines, matching `bin/check_big_files.bat`. That launcher's configurable default is 700; this plan applies the write-plans policy ceiling of **650**. Only Python files use the size bands. Every new file listed in a step has baseline 0 (absent).

| Existing file | Lines | Policy and change |
| --- | --- | --- |
| `tools/review_exchange_models_coordination.py` (existing, to be updated) | 311 | Below 550; safe to extend, ceiling 650 |
| `tools/review_exchange_ownership.py` (existing, to be updated) | 184 | Below 550; safe to extend, ceiling 650 |
| `tools/review_exchange_ownership_store.py` (existing, to be updated) | 275 | Below 550; safe to extend, ceiling 650 |
| `tools/review_exchange_store.py` (existing, to be updated) | 607 | 550–650 at risk; forwarding only, split if >650 |
| `tools/review_resume_identity.py` (existing, to be updated) | 169 | Below 550; safe to extend, ceiling 650 |
| `tools/review_exchange_cli_resume.py` (existing, to be updated) | 431 | Below 550; safe to extend, ceiling 650 |
| `tools/review_exchange_cli_parser.py` (existing, to be updated) | 184 | Below 550; safe to extend, ceiling 650 |
| `instructions/pause-session.md` (existing, to be updated) | 285 | Non-Python; no Python size band |
| `templates/pause-session.template.md` (existing, to be updated) | 128 | Non-Python; no Python size band |
| `instructions/status-session.md` (existing, to be updated) | 115 | Non-Python; no Python size band |
| `instructions/list-session.md` (existing, to be updated) | 77 | Non-Python; no Python size band |
| `templates/status-session.template.md` (existing, to be updated) | 31 | Non-Python; no Python size band |
| `templates/list-session.template.md` (existing, to be updated) | 33 | Non-Python; no Python size band |
| `templates/resume-session.template.md` (existing, to be updated) | 20 | Non-Python; no Python size band |
| `instructions/resume-session.md` (existing, to be updated) | 232 | Non-Python; no Python size band |
| `instructions/review-resume.md` (existing, to be updated) | 146 | Non-Python; no Python size band |
| `README.md` (existing, to be updated) | 110 | Non-Python; no Python size band |
| `wiki/how-to/pause-and-resume-a-session.md` (existing, to be updated) | 231 | Non-Python; no Python size band |
| `docs/v0.14.0/feature-request.v0.14.0.resume-paused.md` (plan-writing edit already applied) | 597 | Non-Python; IO clarification takes it to 601; no implementation edit planned |
| `docs/v0.14.0/design.v0.14.0.resume-paused.md` (plan-writing edit already applied) | 721 | Non-Python; IO clarification takes it to 725; no implementation edit planned |

No existing Python file scheduled for modification is over 650. `tools/review_exchange_store.py` is the sole risk-band mutation target; ownership behavior belongs in its existing ownership-store delegate. Advisory additions are roughly 5–40 lines for forwarding modules, 20–100 for coordination/claim support and 100–400 per new responsibility module or test scenario file. These estimates never impose a lower mandatory ceiling.

Read-only dependencies inspected include artifact configuration (197 lines), observer (196), paths (240), core (538), human transitions (489) and review status (650). Do not extend the 650-line status collector for bulk planning; use the focused adapter. If any dependency must become a mutation target, recount it and apply the same bands before editing.

### Existing tests to preserve and new test layout

Relevant regression packages include artifact-home/configuration, review-resume/identity/instruction/wait, coordination models, ownership/store, lifecycle and instruction structure. Representative existing files have 261 lines (artifact configuration), 184 (selected claims), 405 (ownership), 487 (coordination models), 107 (resume instruction), 341 (resume CLI) and 113 (ownership store). Keep new cases in the step-specific leaves below to avoid growing shared regression files unnecessarily. Run the relevant existing package alongside each new leaf through groundhog.

Every new unit test follows `tests/unit/tools/test_resume_paused_<area>/test_resume_paused_<area>_tdd.py`; create its listed `__init__.py`. Parsing/path/routing properties also use explicit `_pbt.py` files. Property-based testing is useful for malformed/duplicate JSON, canonicalization round trips and pane-order invariance; temporal transport/claim scenarios use deterministic state transitions rather than random sleeps. Step 8 adds larger process-boundary acceptance tests in the existing `tests/acceptance` tree convention.

## Shared execution command checklist

Apply this checklist to every step, including changes to prior-step files.

1. Start or resume the implementation step journal using the canonical step-journal workflow. Recount all involved files before editing; absent new files have baseline 0.
2. Read the canonical fast-Python-tests instruction before writing tests. Add the step's failing tests first, with injected host signals, clocks, process observations and temporary private artifacts.
3. Implement only the step's responsibilities and run its new tests plus relevant existing regression packages with the targeted command below.
4. Inspect the step's changed paths with `rg` for the contracts listed in that step. Check canonical adapters remain redirects, no raw logs/capabilities are persisted and no live bulk CLI is called.
5. Resolve the effort gate with the scope command below and execute its exact printed command. Follow printed repair/restart lines until exit 0; do not freeze a group selector. The requirement currently selects whole suite. Groundhog owns checks/tests; do not call check or pytest directly.
6. Count physical lines after edits. A Python file over 650 requires a responsibility split before completion. Record advisory-estimate variance at or below 650 without inventing missing work.
7. Record command, revision, resolved scope, result and actual complete lifecycle timing in the step journal. Implementation-check later replaces validation placeholders with evidence; writing this plan establishes none.

## Ready-to-run commands shared by all steps

Commands run from the checkout root in PowerShell. Before execution, replace `<LLM_SHARED_DIR>` with the absolute canonical instruction supplier directory, following `rules/run_commands.md`; never execute the placeholder literally. Run the commands printed by the gate resolver exactly as printed.

Physical line counts before and after, substituting the step's explicit paths:

```powershell
$stepPaths = @('tools/resume_paused_profiles.py')
foreach ($stepPath in $stepPaths) {
    if (Test-Path -LiteralPath $stepPath) {
        $physicalLines = ([System.IO.File]::ReadLines((Join-Path $PWD $stepPath)) | Measure-Object).Count
        '{0} {1}' -f $physicalLines, $stepPath
    } else {
        '0 {0} (absent)' -f $stepPath
    }
}
```

Targeted tests, substituting all listed step test files and applicable regression files:

```powershell
& '<LLM_SHARED_DIR>/bin/ghog.bat' single tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py
```

Scope-resolved shared gate and a ready-to-run inspection example:

```powershell
& '<LLM_SHARED_DIR>/bin/prompt_workflow.bat' scope day
rg -n 'resume_paused|resume-paused|Schema|claim_selected' tools instructions templates bin -g '*.py' -g '*.md' -g '*.bat'
```

The grep result is inspection evidence, not a substitute for behavior tests. Never run the bulk launcher from an agent, even for help or dry-run; exercise its parser/main with injected caller/transport in tests. A human owns any later live validation.

## Runtime files and release order

The nonblocking OS guard is keyed by the canonical checkout digest and lives outside checkout/artifact home; it contains no authorization. Receiver-generated prompts/receipts and journal updates stay in the existing private locations. The bulk reader never prepares/migrates a home or writes those records. Test fixtures use temporary directories and fake host sessions. Install updated session instructions, review tools, validator and bulk command together before enabling marked delivery on either host; mixed old readers must fail closed.

## Step 0 assessment and deadline ownership

Do not add a separate timeout/xfail Step 0. The first step is the required host-evidence feasibility gate. Steps 6 and 7 own fake-clock tests for the existing 100/60/120-second limits; no new performance requirement or pending xfail is needed. Groundhog records complete test lifecycle timing without real delivery waits.

## Numbered implementation steps

A bare Qxx in a framing line means the consolidated design decision table; requirement decisions are explicitly written as requirement Qxx. Plan questions below are separate pending implementation choices.

### Step 1. Validate pane-tied host profiles before input

#### Step 1 analysis and intent

- **Issues**: Neither host profile is validated. In particular, Codex has no version in discovery, and Claude watcher absence after restart is unproved.
- **Fix intent**: Implement injected read-only host evidence adapters and document supported version/layout signatures with sanitized synthetic fixtures.
- **Expected outcome**: Both hosts have explicit supported profiles or implementation stops for design review before delivery work.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Clearing and delivery confirmation; Q06, Q08, Q14–Q17. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Read cost follows the selected evidence bytes; return only typed allowlisted facts.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 1 implementation

**Files involved**:

- `tools/resume_paused_profiles.py` (new, to be created).
- `tools/resume_paused_claude.py` (new, to be created).
- `tools/resume_paused_codex.py` (new, to be created).
- `tools/resume_paused_windows.py` (new, to be created).
- `docs/v0.14.0/resume-paused.profile-evidence.md` (new, to be created).
- `tests/unit/tools/test_resume_paused_profiles/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py` (new, to be created).

**Tests first**: Prove Codex pre-input version from its attributable pane banner or pane-tied process metadata; reject caller CLI versions and post-delivery metadata as pre-input proof. Exercise Claude session-id/version/cwd linkage, watcher start/completion/restart, positive no-task evidence, and notification-versus-typed-input distinctions. Reject ambiguous, masked, truncated and unsupported evidence. Cover recognized caller ancestry inside and outside TUIOS and ordinary human shells with unavailable ancestry.

**Types and behavior**: Define typed host/profile/input observations, subprocess and clock protocols, and minimal allowlisted parsing. Codex initial complete-input proof requires one unique matched session file, exact latest user text/cwd/time, and unique launch-prefix then Working in its pane. Later validation retains only nonsecret matched identity and launch id, then rechecks the same unique file/latest input and live bindings after scroll-off. Confirm supported Codex new-conversation syntax from read-only evidence; never experiment by typing.

Define the Codex candidate set in the profile evidence document: enumerate regular session JSONL files under the configured host session root across all date partitions, including older partitions containing a still-running conversation. Select files modified since delivery, allowing only the documented filesystem timestamp resolution at the lower boundary. Judge uniqueness across that entire set, retaining only session metadata and the latest complete user-input record. Account for all metadata and record bytes scanned; incomplete enumeration or records fail closed. Tests include an older-partition session, a second matching file, timestamp boundaries, later input and measured bytes read. Subsequent fresh validation rechecks candidate uniqueness and the retained file identity.

**Completion criteria**: Record the actual supported host versions, independent pre-input source, input/result/clear signatures and Claude positive no-task proof, with evidence limits. If neither Codex candidate works or required Claude proof cannot be validated, return the unresolved point to design review; do not silently enable hooks or ship one host. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 1 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_profiles.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_claude.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_codex.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_windows.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_profiles/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_profiles/test_resume_paused_profiles_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Keep host-specific parsing in its own adapter and Windows ancestry separate from profile policy. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 1**: No Step 0 xfail gate: fake clocks will test agreed deadlines in Steps 6–7. Profile feasibility is a functional prerequisite, not a new wall-time benchmark.

### Step 2. Parse pause artifacts and observe exact review state without writes

#### Step 2 analysis and intent

- **Issues**: Session artifacts currently have instruction-defined formats; normal artifact-home preparation and review-core construction can mutate state.
- **Fix intent**: Add exact-byte prompt/receipt and versioned JSON routing readers; reuse side-effect-free configuration/path resolution, validated observer and nonblocking observation locks.
- **Expected outcome**: A canonical checkout snapshot distinguishes unused, used, malformed and unresolved inputs without creating directories or claiming roles.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Discovery and evidence model; saved routing; Q01 and Q09; legacy routing study; existing tuitp compatibility. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 2 implementation

**Files involved**:

- `tools/resume_paused_models.py` (new, to be created).
- `tools/resume_paused_artifacts.py` (new, to be created).
- `tools/resume_paused_review.py` (new, to be created).
- `docs/v0.14.0/resume-paused.legacy-routing-study.md` (new, to be created).
- `tests/unit/tools/test_resume_paused_artifacts/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py` (new, to be created).

**Tests first**: Cover missing/empty/unreadable prompts, schema 1/2/3 receipts, malformed roots/digests/timestamps, consumed versus replaced prompts, default/custom homes and missing directories. Snapshot before/after trees and reject writes or prepare_home/migration calls. Test exact round/occurrence, damaged artifacts and busy observation locks. Add generated/property cases for JSON strictness, duplicate keys, path aliases and round trips.

Unknown routing fields preserve the rest of the pause but yield an unresolved-target skip; they do not make the whole prompt a parse error. A JSON/table contradiction is an error. Test both outcomes explicitly.

**Types and behavior**: Model canonical Windows roots, routing targets, prompt digests, marked receipts and exact exchange identities. Read routing only from one versioned JSON block and generate its readable table from that object. Preserve legacy manual readability while table-only/missing routing skips bulk. Reuse ReviewArtifactConfiguration.load, derive_artifact_paths, ReviewExchangeObserver and observe_transition without ReviewExchangeCore preparation or migration. Document the separate table-to-JSON study, including digest/used-receipt hazards; implement no bulk converter.

**Completion criteria**: Read-only tests establish zero prompt/receipt/journal/review/authorization writes. Compatibility fixtures preserve prompt heading, Session role, and exact Prompt/SHA-256/Project root receipt grammar without importing senv. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 2 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_models.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_artifacts.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_review.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_artifacts/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_artifacts/test_resume_paused_artifacts_pbt.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Separate artifact syntax from review observation; keep legacy conversion research in its study document. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 2**: Use deterministic IO-count assertions for exact paths; do not introduce mutable-evidence caches.

### Step 3. Emit JSON routing at pause and align manual artifact readers

#### Step 3 analysis and intent

- **Issues**: The pause template has only a prose routing table, and existing readers describe schema 1/2 only.
- **Fix intent**: Update canonical pause instructions/templates to capture JSON routing from read-only evidence and make the status and list receipt readers schema-3 aware.
- **Expected outcome**: Historical authorship and intended assignments remain separate; unresolved targets are explicit and never guessed.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Saved routing and role resolution; Q01, Q03 and Q10; compatible mixed-install release. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 3 implementation

**Files involved**:

- `instructions/pause-session.md` (existing, to be updated).
- `templates/pause-session.template.md` (existing, to be updated).
- `instructions/status-session.md` (existing, to be updated).
- `instructions/list-session.md` (existing, to be updated).
- `templates/status-session.template.md` (existing, to be updated).
- `templates/list-session.template.md` (existing, to be updated).
- `templates/resume-session.template.md` (existing, to be updated).
- `tests/unit/tools/test_resume_paused_pause_contract/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py` (new, to be created).

**Tests first**: Contract-test JSON block/table agreement, full pane UUID and session string, exact exchange scope or explicit not-applicable, author-versus-role separation, missing evidence and no routing question. Test manual legacy prompt and schema 1/2 readability plus schema 3 grammar. Exercise installed tuitp waiting_prompt input grammar through local fixtures only.

Contract-test the pause replacement guard (requirement Q29=A, acceptance criterion 14): a different recorded pausing pane or saved role guards replacement of an unused or new prompt even for the same host; unknown values alone establish no difference; legacy prompts retain the agent-id comparison; declining preserves the old checkpoint. Capture never contacts the counterpart or launches `resume_paused`.

**Types and behavior**: Require the pausing host to capture resolved root, pausing identity, intended resumed/requestor/reviewer pair, evidence source and exchange occurrence/current round. Preserve first heading and Session role. Keep provider-specific adapters as canonical redirects; do not duplicate workflow bodies. Update the receipt template additively with a marked schema-3 variant while retaining manual schema-2 rules.

**Completion criteria**: New pause examples parse under Step 2, readable tables derive from JSON, and legacy fixtures remain valid. `pause-session`, `status-session` and `list-session` describe schema-3 compatible readers; `resume-session` gains its schema-3 reader and writer together in Step 4. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 3 addendums

**Line-budget checkpoint**:

- `tests/unit/tools/test_resume_paused_pause_contract/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Keep JSON schema parsing in Step 2 modules and workflow policy in root instructions; do not grow provider adapters. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 3**: No timeout or xfail gate; use small in-memory contract fixtures.

### Step 4. Validate marked receivers and fence every protected mutation

#### Step 4 analysis and intent

- **Issues**: Inherited pane variables cannot establish receiver identity, and marked consent must not outlive a changed latest input or claim generation.
- **Fix intent**: Provide an agent-callable read-only validator separate from the human-only CLI, then connect its fresh results to receiving instructions and the existing locked selected claim.
- **Expected outcome**: A valid marker authorizes only its bound overrides; mismatch stops before protected writes without fallback consent questions.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Target-bound consent; takeover observation; Q02–Q04, Q11 and Q13–Q15. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 4 implementation

**Files involved**:

- `tools/resume_paused_marker.py` (new, to be created).
- `tools/resume_paused_validation.py` (new, to be created).
- `tools/resume_paused_claim.py` (new, to be created).
- `bin/resume_paused_validate.bat` (new, to be created).
- `tools/review_exchange_models_coordination.py` (existing, to be updated).
- `tools/review_exchange_ownership.py` (existing, to be updated).
- `tools/review_exchange_ownership_store.py` (existing, to be updated).
- `tools/review_exchange_store.py` (existing, to be updated).
- `tools/review_resume_identity.py` (existing, to be updated).
- `tools/review_exchange_cli_resume.py` (existing, to be updated).
- `tools/review_exchange_cli_parser.py` (existing, to be updated).
- `instructions/resume-session.md` (existing, to be updated).
- `instructions/review-resume.md` (existing, to be updated).
- `tests/unit/tools/test_resume_paused_validation/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_claims/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py` (new, to be created).

**Tests first**: Test version/encoding/duplicate/length rejection, canonical UTF-8 JSON SHA-256, root/digest/role/pair/session/pane/host mismatches and exact exchange round/occurrence. Test shared-daemon inherited-pane spoofing, two matching session files, newer user input, missing/ambiguous session evidence and Codex prefix scroll-off after initial proof. At every protected-write hook change evidence and assert no write/claim. Test truthful consumed receipt retained if later claim fails; manual unmarked consent remains unchanged. Instruction-contract tests cover schema-3 receipt reuse detection in `resume-session`. Test new claim clears/replaces old binding, idempotent/current-owner transitions retain it, and competing pickups invalidate it.

Test success and failure compact-result grammar and the 100-character bound. Smoke-test the separate agent-callable `bin/resume_paused_validate.bat` with temporary fixtures for argument forwarding, UTF-8 JSON output and exit codes, following the existing review-resume launcher smoke-test convention. This invokes only the read-only validator, never the bulk launcher.

**Types and behavior**: Encode compact markers with random launch id first, full pane UUID, role and assignment digest. Return typed nonsecret validation JSON and a nonsecret initial matched-session identity for subsequent fresh checks. Revalidate immediately before receipt replacement, journal writes, backfill and ownership claim; do not cache authorization. Persist schema-3 nonsecret receipt bindings only in the receiver. `resume-session` reads schema 1, 2 and 3 receipts for reuse detection and writes the schema-3 variant only on a marked resume. Extend CoordinationRecord with marked launch/pane/host/assignment/round/occurrence/issued-generation evidence. Thread optional marked-claim context through parser, CLI, `claim_selected`, store and `OwnershipService` (input and derivation per plan Q04); retain locked round/occurrence rechecks and stale-record comparison. Keep ownership capabilities in session memory and existing digest storage only; no claim history or authorization file.

The source of that validated claim binding remains pending plan Q04. Do not treat caller-copied fields as an accepted implementation choice. Before implementation, apply the user's selected option and its corresponding prompt/routing/exchange-change tests while retaining fresh pre-claim receiver validation and the locked round/occurrence rechecks.

**Completion criteria**: Both receiving workflows invoke fresh validation before each protected mutation. Every receiving outcome emits the profile's compact result of at most 100 characters (launch id, outcome, optional claim generation, never a token or digest); on a stopping Claude turn it is the first line of the final response, and a failure emits it before stopping or asking. Marked claim evidence is atomic with its generation, never added by a later bulk write. Existing manual claim, role conflict, fencing and review isolation regressions pass. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 4 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_marker.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_validation.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_claim.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/review_exchange_models_coordination.py`: before 311; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tools/review_exchange_ownership.py`: before 184; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tools/review_exchange_ownership_store.py`: before 275; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tools/review_exchange_store.py`: before 607; 550–650 at risk; ceiling 650. Forwarding additions only; extract ownership delegation if the ceiling would be exceeded.
- `tools/review_resume_identity.py`: before 169; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tools/review_exchange_cli_resume.py`: before 431; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tools/review_exchange_cli_parser.py`: before 184; below 550, safe to extend; ceiling 650. Advisory additions 5–100.
- `tests/unit/tools/test_resume_paused_validation/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validation_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_validation/test_resume_paused_validate_launcher_smoke_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_claims/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_claims/test_resume_paused_claims_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Keep marker encoding, receiver validation and marked-claim adaptation separate. The 607-line store is at risk: add only forwarding; if it would exceed 650, extract ownership delegation into the existing ownership-store responsibility. Put new tests in separate leaves. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 4**: Fresh validation uses injected clocks and exact files; no real host input or artificial wall-time gate.

### Step 5. Build the read-only checkout planner and duplicate protections

#### Step 5 analysis and intent

- **Issues**: Filtering selected panes too early would hide duplicate evidence; eligibility must protect caller, active turns, questions and drafts.
- **Fix intent**: Collect all panes first, aggregate by canonical root, apply global argument validation, then resolve saved assignments and per-checkout actions.
- **Expected outcome**: Preview and execution share the same classified plan, with no guessed target or mutation.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Discovery; duplicate protection and safe eligibility; saved role switching; Q08 and Q10; reporting. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Use map-based discovery/grouping and explicit fresh evidence costs from the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 5 implementation

**Files involved**:

- `tools/resume_paused_planner.py` (new, to be created).
- `tools/resume_paused_evidence.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_planner/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py` (new, to be created).

**Tests first**: Cover harness/app/name precedence and contradictions, all-session discovery, duplicate roots, exact case-insensitive exclusions/session/folder names, unmatched global exclusions/switches, per-checkout inapplicable switches and target UUID conflicts. Include excluded/caller panes in duplicate evidence. Cover receipt, later journal resume, pending override and attributable counted commands; exclude selected reviewer review-resume for non-reviewer pauses but count it for reviewer pauses. Cover busy, blocked/question, nonempty draft, caller pane and fresh-idle-versus-stale-working states. Property-test pane order invariance and exclusions never removing duplicate protection.

An `--except` pane label excludes only matching panes; `--switch-roles` never matches pane labels. Test saved UUID missing, listed UUID without an agent (including a CMD shell), and UUID now running another host: respectively skip, skip and classification error, with no reviewer input sent to a shell. Multiple live exchanges without a saved exact identity yield ambiguous pairing and no counterpart action.

**Types and behavior**: Define immutable checkout plans and typed skip/error reasons. Swap only the saved requestor pair for --switch-roles. Use full live UUID, root, session and host; agent session id is supporting evidence and may change after clear. Enforce human-only caller rejection in dry-run too. Resolve unmatched global arguments before any input; isolate checkout errors so independent valid work can continue. Read the exact private session journal as an index, never an authority or a writer.

**Completion criteria**: One planned result per discovered prompt-bearing checkout, including used and skipped prompts; omitted panes are counted. Global validation failures yield no input. Dry-run makes zero transport mutations. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 5 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_planner.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_evidence.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_planner/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_planner/test_resume_paused_planner_pbt.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Separate duplicate evidence classification from routing/planning and keep argument parsing for Step 8. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 5**: Index panes by root/UUID once per observation; rebuild mutable safety evidence before inputs. Busy panes skip immediately.

### Step 6. Deliver guarded pane actions with bounded acceptance

#### Step 6 analysis and intent

- **Issues**: Transport success does not prove command submission, and concurrent human invocations can race.
- **Fix intent**: Add nonblocking per-checkout OS guards outside artifact homes, shell-free TUIOS transport and a deadline-driven clear/delivery state machine.
- **Expected outcome**: Every input is freshly eligible and targets exactly one current full pane identity; uncertain submission never causes retyping.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Clearing and delivery confirmation; Q05–Q07; 100-second action and 60-second stall limits. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 6 implementation

**Files involved**:

- `tools/resume_paused_guard.py` (new, to be created).
- `tools/resume_paused_transport.py` (new, to be created).
- `tools/resume_paused_delivery.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_delivery/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py` (new, to be created).

**Tests first**: Test guard contention/release and independent-checkout concurrency with deterministic barriers, including two processes on Windows. Recheck changed prompt/routing/digest/duplicates/selector/protection immediately before clear, resume and recovery Enter. Cover wildcard selector collisions, shell metacharacters as inert arguments, unconfirmed clear, Claude redundant clear with later prompt, and background-shell report-only behavior. Use fake clocks for 100-second action limits including recovery and 60-second stall. Permit Codex one Enter only after input was proved empty and two identical full captures prove this launch's exact unsubmitted command without Working/placeholder; wrong UUID, edits, expiry or ambiguous capture forbids it.

**Types and behavior**: Call tuios by argument array using ask-agent --select with live session/name, --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- and the native marked command. Resolve the wildcard selector to exactly the validated UUID before every send; preserve caller environment. Clear only the resumed conversation, never counterpart. Accept only supported profile evidence plus full latest-input proof from Step 1. Requestor precedes reviewer; no duplicate work per pane. Hold checkout OS guard through protected sequence and release on every exit.

**Completion criteria**: Injected transport captures exact argv and zero unintended input. Recovery is at most one pane-targeted Enter without retype or deadline reset. No bulk artifact writes or live CLI delivery occur during tests. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 6 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_guard.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_transport.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tools/resume_paused_delivery.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_delivery/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_delivery/test_resume_paused_delivery_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Separate OS locking, transport and orchestration; split delivery into clear/acceptance helpers if it approaches 650. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 6**: Owning step for fake-clock 100/60-second checks; no real 100-second sleeps or xfail placeholders.

### Step 7. Confirm takeover and activate only a verified missing reviewer

#### Step 7 analysis and intent

- **Issues**: Receipt alone cannot prove requestor ownership; waiter state and prior uncertain reviewer delivery cannot be guessed.
- **Fix intent**: Observe exact schema-3 receipt/current marked claim and host result evidence under a separate fixed deadline for every receiver.
- **Expected outcome**: Only proven requestor takeover and positive no-wait evidence permit a missing counterpart action.
- **Framing**: [Design](design.v0.14.0.resume-paused.md), Takeover observation and later reviewer continuation; design Q04, Q12–Q17. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 7 implementation

**Files involved**:

- `tools/resume_paused_takeover.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_takeover/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py` (new, to be created).

**Tests first**: Test receipt/claim agreement, current generation, competing pickup, normal owner transitions, log eviction/masking and daemon restart. Leave exact active reviewer first, then require current requestor generation. Cover global wait latest reviewer input with no later input and Claude currently running watcher started after latest input, including restarted after an answer. Activate only with validated positive Claude no-task evidence including host restart, or fresh supported Codex idle/empty/no-active-turn capture. Cover unknown wait status, uncertain previous activation, unchanged later continuation, prompt/exchange replacement and repeated switch flag. Give each receiver its own 120-second fake-clock observation bound.

Test event-driven observation where available, otherwise bounded reads with backoff capped at five seconds, under the fake clock. Verify cadence does not reset the per-receiver deadline or reuse stale safety evidence.

**Types and behavior**: Observe only allowlisted compact result patterns (maximum 100 characters) or durable receipt/marked-claim fields. Never persist or print raw conversations, logs, tokens or token digests as result evidence. Require exact launch/pane/assignment/current generation for takeover. Reconstruct later missing-reviewer work solely from unchanged prompt, receipt and current claim; introduce no continuation file. Reapply all normal protections before activation without clearing/resuming requestor. Expected pending/completion-unconfirmed outcomes are successful unless an independent failure occurs; marker mismatch or repeated consent question fails.

**Completion criteria**: Paused reviewer resumes only itself; non-requestor roles never activate a pair. Requestor receipt without current bound claim cannot trigger counterpart. No-wait ambiguity yields pending/no input, and uncertain earlier delivery is never resent. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 7 addendums

**Line-budget checkpoint**:

- `tools/resume_paused_takeover.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_takeover/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_takeover/test_resume_paused_takeover_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Keep takeover observation separate from delivery; extract reviewer-wait classification if needed before exceeding 650. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 7**: Owning step for 120-second-per-receiver checks with fake time; bound starts after acceptance and is distinct from delivery.

### Step 8. Ship the CLI and validate the complete installed workflow

#### Step 8 analysis and intent

- **Issues**: All readers and receivers must ship together, and local format compatibility cannot establish deferred launcher integration.
- **Fix intent**: Wire public arguments, self-locating Windows launcher, reporting/exit policy, documentation and end-to-end acceptance scenarios.
- **Expected outcome**: Humans can preview or resume eligible panes with deterministic outcomes and clear compatibility limits.
- **Framing**: [Requirement](feature-request.v0.14.0.resume-paused.md), Command contract; [Design](design.v0.14.0.resume-paused.md), reporting and exit semantics; acceptance examples and validation boundaries. Apply the shared execution command checklist and ready-to-run commands above.
- **Complexity impact**: Keep responsibilities bounded; account for exact-path reads and fresh evidence as described in the shared complexity section.
- **Feature preservation**: Preserve legacy manual consent/readability, review-role isolation and existing ownership fencing while adding only the behavior assigned here.

#### Step 8 implementation

**Files involved**:

- `tools/resume_paused.py` (new, to be created).
- `bin/resume_paused.bat` (new, to be created).
- `README.md` (existing, to be updated).
- `wiki/how-to/pause-and-resume-a-session.md` (existing, to be updated).
- `wiki/reference/resume-paused.md` (new, to be created).
- `tests/unit/tools/test_resume_paused_cli/__init__.py` (new, to be created).
- `tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py` (new, to be created).
- `tests/acceptance/resume_paused/__init__.py` (new, to be created).
- `tests/acceptance/resume_paused/fakes.py` (new, to be created).
- `tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py` (new, to be created).
- `tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_acceptance_tdd.py` (new, to be created).

**Tests first**: Exercise CLI parser/help and recognized agent rejection (including preview), whole no-input dry run, independent failures, single-agent resume, cross-host author override, requestor/reviewer role conflict, switched pair and later continuation, --clear, blocked/draft/busy panes, custom homes, malformed artifacts, duplicate guard race and exact receiver protected-write failures. Run process-boundary acceptance with fake tuios and real temporary artifact files, invoking receiver validation/claim code rather than merely asserting expected mocks. Cover installed tuitp grammar fixtures and legacy manual resumes. Assert no live TUIOS is needed or invoked.

Verify `bin/resume_paused.bat` statically: its self-locating launcher selects the shared Python and forwards arguments only to `tools/resume_paused.py`. Agents never execute it, including help or preview. Parser/main acceptance uses injected caller/transport; live Windows launcher and pane-delivery validation remains human evidence, distinct from these automated checks. Receiver test harnesses prove their executed sequence and instruction contract, not arbitrary live-agent compliance. Shared support and acceptance grouping remain pending Q01–Q03, with their exact proposed files listed below rather than silently adopted.

**Types and behavior**: Implement only documented --dry-run, --clear, repeatable --except NAME[,NAME...] and --switch-roles forms; no timeout overrides. Use one compact line per prompt-bearing checkout and omitted-pane count; distinguish accepted/unconfirmed, reviewer pending, exclusions, contention and errors. Exit 0 for expected skips/pending/success, 1 for execution/classification failures, 2 for syntax. State human-only and agent prohibition in help and canonical docs. Ship updated pause/resume/status/list instructions, validator and review tools together; older installs fail closed on new marked data.

**Completion criteria**: All acceptance criteria map to passing scenarios; targeted tests and scope-resolved whole-suite groundhog gate pass in the same cycle. Record supported profiles and remaining external evidence honestly. Completion handoff retains the unchecked requirement deferred-senv checklist and full all-eligible-session integration obligation; do not mark that separate effort complete. Run this step's listed test files with the shared targeted command, inspect its affected contracts with `rg`, and obtain exit 0 from the exact command printed by the scope resolver in the same repair cycle. Later steps remain unimplemented until separately checked.

#### Step 8 addendums

**Line-budget checkpoint**:

- `tools/resume_paused.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_cli/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/unit/tools/test_resume_paused_cli/test_resume_paused_cli_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/acceptance/resume_paused/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/acceptance/resume_paused/fakes.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/acceptance/resume_paused/test_resume_paused_acceptance/__init__.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.
- `tests/acceptance/resume_paused/test_resume_paused_acceptance/test_resume_paused_acceptance_tdd.py`: before 0; below 550, safe to extend; ceiling 650. Advisory initial size 0–400.

All non-Python file baselines are recorded above; new non-Python files start at 0. Recount all files at execution time.

**Split guidance**: Keep CLI limited to parsing/composition/rendering. Acceptance fixtures and scenario groups use separate modules before reaching 650. No advisory estimate is an independent completion gate.

**Full workflow timing run readiness**: Use the shared ready-to-run targeted command with all test paths listed in this step, then the scope-resolved shared gate. Fixtures must include setup, measured action and cleanup in the timing record; no live TUIOS dependency.

**Time-gated status for Step 8**: Full acceptance uses injected time and controlled synchronization; record complete lifecycle timing through groundhog and preserve shared test budgets.

## Completion handoff and validation limits

Map the requirement acceptance criteria to Step 8 scenarios and record profile feasibility, fake-run evidence and whole-suite scope separately from human live validation. Keep the [deferred senv checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up) unchecked: its separate effort still owes eligible-layout coverage for both hosts/review pairs, startup and daemon restoration, opt-out/native modes and saved/live pane-identity continuity. Open that effort at completion and revisit it when launch-time behavior changes. Preserve [the design's compatibility limits](design.v0.14.0.resume-paused.md#existing-tuitp-compatibility-and-later-shared-integration). No claim of full topic integration may rely on grammar fixtures alone.

## Open questions for the v0.14.0 resume-paused implementation plan

### Q01: Shared synthetic evidence fixtures across implementation steps

Question description: Step 1 establishes host profiles, but later unit leaves and process acceptance tests need the same synthetic pane/session observations. Which file layout should own reusable fixture builders so the tests exercise one profile contract without importing another test module?

#### BBQ for Q01

Several cooks need the same measured ingredients; copying each recipe's measurements lets them drift. In this picture: the cooks are the unit and acceptance scenarios, the measurements are synthetic host/profile records, and the shared recipe card is a neutral test-support module.

#### Options for Q01

- Option A: Create `tests/unit/tools/resume_paused_test_support.py` in Step 1, new, with pure synthetic host, pane and session builders imported by unit leaves and `tests/acceptance/resume_paused`, following the existing `review_exchange_test_support.py` convention; split by responsibility if growth would exceed 650 physical lines.
  - pro: One evidence vocabulary and no cross-imports from test functions; later steps extend helpers by responsibility.
  - con: Introduces a shared support module that must stay free of scenario-specific assertions.
- Option B: Keep fixture builders local to each step's test leaf and recreate acceptance inputs independently.
  - pro: Each suite is self-contained and has no shared support dependency.
  - con: Duplicated supported-profile fixtures can disagree as layouts and negative cases evolve.

#### Recommended option for Q01

Option A: The profiles are shared contracts across receiver, planner and transport tests. A neutral pure support module follows the existing repository convention without sharing runtime safety caches.

#### Answer to Q01: option A

Option A: The profiles are shared contracts across receiver, planner and transport tests. A neutral pure support module follows the existing repository convention without sharing runtime safety caches. If accepted, add `tests/unit/tools/resume_paused_test_support.py` to Step 1 (new, baseline 0, below 550 safe-to-extend band, ceiling 650), record it as a read dependency in later steps, and keep scenario assertions local.

User decision: confirmed — Option A. Create shared pure synthetic evidence builders in Step 1; keep scenario assertions local.

Decision date: 2026-11-10. User selected A. Rationale: one evidence vocabulary across unit and acceptance tests follows the existing test-support convention and reduces fixture drift.

### Q02: Receiver write-boundary harness for receipt and journal regressions

Question description: Step 4 requires fresh validation before receipt replacement, journal writes, backfill and claims. The claim path is executable Python, while receipt/journal sequencing is currently expressed in LLM instructions. How should tests distinguish an executed protected-write boundary from a textual instruction assertion?

#### BBQ for Q02

Checking that a kitchen checklist says to wash hands does not show the cook did so before each dish. In this picture: the checklist is the receiving instruction, hand washing is fresh marker validation, dishes are receipt/journal/claim mutations, and an observed cooking rehearsal is the receiver sequencing harness.

#### Options for Q02

- Option A: Add a test-only receiver harness at `tests/unit/tools/resume_paused_receiver_test_support.py` in Step 4, shared with Step 8 acceptance. Execute the documented validation/write sequence against temporary receipt/journal files using the real validator module and real locked claim, changing evidence between every protected step, plus separate instruction-contract tests.
  - pro: Evidence explicitly separates executed data-path protection from the instruction contract; stale-input changes can be injected at every boundary.
  - con: The test harness must be maintained alongside instruction sequencing and cannot prove that an arbitrary live agent obeys it.
- Option B: Use instruction-text checks for receipt/journal sequencing and execute only the existing Python claim boundary.
  - pro: Requires less test support and avoids modeling an LLM workflow.
  - con: Cannot demonstrate the intended no-write behavior for receipt/journal changes after evidence becomes stale.

#### Recommended option for Q02

Option A: A declared harness plus text-contract checks gives useful deterministic regression coverage while stating its live-agent proof limit. It adds no production receipt writer or new authorization mechanism.

#### Answer to Q02: option A

Option A: A declared harness plus text-contract checks gives useful deterministic regression coverage while stating its live-agent proof limit. It adds no production receipt writer or new authorization mechanism. If accepted, list `tests/unit/tools/resume_paused_receiver_test_support.py` in Step 4 (new, baseline 0, below 550 safe-to-extend band, ceiling 650) as shared support used by Step 8. The harness calls the real validator and locked claim with evidence changes between protected steps. Carry the explicit live-agent proof limit into Step 8 acceptance and the validation plan.

User decision: confirmed — Option A. Add the shared test-only receiver harness with real validator and locked-claim calls, evidence changes between protected steps, and separate instruction-contract checks. Preserve the explicit limit: this cannot prove arbitrary live-agent compliance.

Decision date: 2026-11-10. User selected A. Rationale: executable stale-evidence scenarios provide regression evidence for receipt and journal write boundaries alongside instruction checks.

### Q03: Acceptance scenario grouping before the final matrix grows

Question description: Step 8 lists one acceptance scenario file for a large matrix spanning caller rejection, protected writes, paired continuation, transport races and compatibility. How should that matrix be divided so each responsibility stays readable without turning advisory size estimates into a stricter limit?

#### BBQ for Q03

A pantry is easier to inspect when shelves group ingredients by use before the pile becomes too large. In this picture: the pantry is the acceptance package, the shelves are scenario modules, the ingredients are end-to-end cases, and the shelf capacity is the existing 650-line Python ceiling.

#### Options for Q03

- Option A: Start Step 8 with separate CLI/safety, delivery and paired-continuation acceptance modules under the listed leaf, sharing only package fakes.
  - pro: Makes coverage ownership visible and reduces pressure to grow one large scenario file.
  - con: Adds several small modules and requires clear fixture ownership.
- Option B: Keep one acceptance file initially, extracting by responsibility only if it would exceed 650 physical lines.
  - pro: Minimizes initial file count and remains valid under the existing line-budget policy.
  - con: The full matrix can become difficult to navigate before it reaches the ceiling.

#### Recommended option for Q03

Option A: The scenario groups already follow distinct implementation steps. Splitting by those responsibilities improves review without inventing a mandatory lower size target.

#### Answer to Q03: option A

Option A: The scenario groups already follow distinct implementation steps. Splitting by those responsibilities improves review without inventing a mandatory lower size target. If accepted, replace the single scenario file in Step 8 with three new modules under `tests/acceptance/resume_paused/test_resume_paused_acceptance/`: `test_resume_paused_cli_safety_tdd.py` owns caller rejection, dry run, exclusion and switch validation, reporting/exit codes, `tuitp` grammar and legacy manual resumes; `test_resume_paused_delivery_tdd.py` owns clear, transport, guard races, recovery Enter and receiver protected-write failures; `test_resume_paused_continuation_tdd.py` owns takeover, reviewer leave-alone, pending/activation, later and switched continuation. Each starts at baseline 0 in the below-550 safe-to-extend band with ceiling 650. Realign validation expectations; the eight numbered steps do not change.

User decision: confirmed — Option A. Start Step 8 with separate CLI/safety, delivery and continuation acceptance modules, using the approved shared test support. Keep the existing 650-line ceiling and eight numbered steps.

Decision date: 2026-11-10. User selected A in the native choice. Rationale: separate responsibilities make coverage ownership visible and scenarios easier to review.

### Q04: Source of the durable marked-claim binding

Question description: Step 4 records launch id, pane, host, assignment binding, round, occurrence and issued generation in the coordination record, and Step 7 treats that record as takeover proof. Should `claim` record values it derives from the marker, or values the receiver copies from an earlier validator result?

#### BBQ for Q04

A grill cook writes the order ticket from the customer's own order card rather than a waiter's retelling. In this picture: the card is the marker, the retelling is validator output copied into claim arguments, and the ticket is the durable marked claim later trusted by the bulk tool.

#### Options for Q04

- Option A: `claim` accepts the raw marker and, for Codex, the carried session identity and launch id. Under the transition lock it parses the marker, recomputes the assignment digest from the current prompt, routing and locked exchange, and records only derived nonsecret values. Pane and complete-input proof come from the validator call immediately before, as required by the design.
  - pro: No hand-copied durable values; digest validation shares the round/occurrence lock, without adding TUIOS or host session-file dependencies to claim.
  - con: Adds marker parsing and assignment reconstruction dependencies to claim; live pane/input proof still depends on the preceding separate call.
- Option B: The receiver passes the validator's returned binding fields as claim arguments; `claim` checks syntax and the locked round/occurrence only.
  - pro: Keeps claim generic and smallest.
  - con: A stale or mistyped field can become takeover proof without matching the current prompt and exchange at claim time.
- Option C: `claim` runs the full validator in process, including live pane and complete-input proof, and records its result.
  - pro: Gives the narrowest window between proof and record.
  - con: Adds TUIOS calls and host session-file reads to the review claim path and couples claim tests to host evidence adapters.

#### Recommended option for Q04

Option A: Derive durable takeover evidence without moving host evidence into the review exchange core; retain the design's separate fresh pre-claim validator call.

#### Answer to Q04: option A

Option A: Derive durable takeover evidence without moving host evidence into the review exchange core; retain the design's separate fresh pre-claim validator call. If accepted, thread an optional raw marker and carried Codex identity through parser, CLI, `claim_selected`, store and `OwnershipService`; under the transition lock recompute and compare the assignment digest and record only derived nonsecret fields. Add Step 4 tests for a marker no longer matching the current prompt, routing or exchange, including atomic rejection without a claim write. Existing Step 4 files own this work and retain their recorded baselines and 650-line ceilings.

User decision: confirmed — Option A. Derive the durable marked-claim binding from the raw marker and current assignment under the transition lock, carrying the required Codex identity. Retain separate fresh live pane/input validation immediately before claiming ownership.

Decision date: 2026-11-10. User selected A. Rationale: reconstructing and checking current assignment data prevents stale copied binding fields from becoming takeover evidence while keeping host observation separate from claim handling.
