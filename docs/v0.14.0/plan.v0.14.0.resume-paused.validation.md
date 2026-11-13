# v0.14.0 resume-paused implementation tracking and validation

No, it is not implemented

Track the eight steps of [the implementation plan](plan.v0.14.0.resume-paused.md). No implementation check has taken place; host profiles, shared parsers, marked receivers and bulk delivery remain to be implemented.

## File-based IO cost clarification for resume-paused validation

Read the exact artifact-home declaration, prompt/receipt and selected exchange paths, plus the private journal index when needed. Index checkout/pane identities once per observation; avoid broad document or Markdown scans. Full latest-input proof may require reading candidate host session files, so account for bytes read and reject incomplete evidence. Re-read mutable prompt, receipt, routing, live pane/input and claim evidence at every safety boundary; never cache it as authorization. The bulk reader writes none of these files. Receiver-only persisted updates retain existing atomic replacement and locked claim semantics.

## Complexity and deadline validation scope

Review each step against the plan's map-based discovery and byte-proportional evidence costs. Fresh mutable safety evidence is mandatory. Check the fixed 100-second action, 60-second stall and separate 120-second-per-receiver limits using fake clocks; no new Step 0 timeout/xfail gate is planned.

The [deferred senv integration checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up) remains unchecked. Later completion evidence must distinguish installed grammar fixtures from the separate all-eligible-session startup/restoration integration, and carry that follow-up into the completion handoff.

## Step 1. Validate pane-tied host profiles before input

### Analysis of Step 1 implementation state

Not started. Step 1 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 1

Establish usable read-only evidence for both hosts before enabling any delivery.

### Step 1 improvement expectations

- Both hosts have explicit supported profiles or implementation stops for design review before delivery work.
- Record the actual supported host versions, independent pre-input source, input/result/clear signatures and Claude positive no-task proof, with evidence limits. If neither Codex candidate works or required Claude proof cannot be validated, return the unresolved point to design review; do not silently enable hooks or ship one host.
- Validate the documented Codex candidate set across all host-session date partitions, including older active sessions, timestamp-resolution boundaries, a second matching file and total bytes scanned. Incomplete enumeration or latest-input evidence fails closed; subsequent checks retain and reprove the same unique identity.
- Validate the consolidated Codex native image contract: one direct child, query rights only, complete allocation-metadata walk with exactly one committed matching image allocation, both native image-name APIs, GLOBALROOT read/execute open sharing read/delete, successful class-44 identity query and hashing through the same retained handle. Verify the pinned digest and exact same-release manifest; refresh all mutable bindings before input. Exclude memory reads and module enumeration.
- Record each validated `RtlGetVersion` build number and observed update revision. Cover unsupported/invalid builds, denied/unavailable APIs, every non-success identity status, rename/stale paths, tunneling, identical and other pinned-release replacements, actual updater behavior and process/handle races. No replacement exception applies. Later session-file version disagreement stops consumption and claim.
- Validate Claude's complete generation/session marker coverage with existing explicit launcher settings only (Q18=A), root/nested attribution, timestamp semantics, ordering, design item 1's generation-scoped exclusivity and documented current-source exclusion. An installed TUIOS integration, alone or combined with launcher settings, and missing or uncertain provenance stays pending. Install no hooks. Include every attach path to an existing session id, with and without the launcher settings and including nested print-mode resume, while the original root runs and after it exits; record where each attach first fails design item 1's positive attribution, and whether its turn input persists before that turn's first tool runs, against the original-process controls (design item 1, case 6). Read all checkout Claude-project transcripts active since the last OS boot and all relevant durable schedule definitions regardless of boot (Q19=A), with complete generation ranges, enumeration and record byte accounting. Validate activity selection and true-boot semantics; unresolved Windows fast startup, missing history, uncertain activity or schedule restoration stays pending. Cover all in-scope host-managed waiting mechanisms, typed/slash input and notifications, subagent commands, compaction and documented lifecycle paths.
- Validate Q21=A's fixed boot instant from the creation timestamp of a validated process that starts at boot. Cover concrete source selection, timestamp stability under forward/backward changes, uptime semantics, comparison tolerance and fast startup. Never select history using current time minus uptime; detected net backward movement beyond the validated tolerance stays pending. Disclose undetectable backward changes since boot, including offsetting changes. No event-log or general extra channel is approved. The uptime value must count time spent in sleep and hibernation. Validate this, and test suspension between boot and the decision. An uptime that excludes suspended time would hide a backward change of up to the suspended duration.
- Validate Q22=A's exception only for proved-requestor current-generation starts proved created after marked resume, with their own lifecycle records, on initial activation and later continuation. Keep earlier starts, other transcripts and recognized reviewer `wait-any-request` starts in scope, including starts inside the proposed exception and former-reviewer starts after role switching. Ambiguous generation/order remains pending. Preserve complete reads/classification needed for the exception, byte accounting, exact takeover proof and fresh required bindings in both panes. The exception removes only starts that validated creation ordering places after the marked resume input, with those starts' own lifecycle records. File position alone never places a record after the marker. Terminal, stop and completion records after the marker still match in-scope starts ordered before it. This includes any such record the host writes into a later session file after a clear. A start whose order relative to the marker is uncertain stays in scope. Inside the excluded range, a start that invokes the review-exchange launcher counts as a reviewer watcher unless its operation parses as a validated requestor operation. Validate the recognized invocation forms for each pinned version. A recognized watcher stays in scope under normal start/end matching and blocks until its validated terminal record.
- Validate Q23=A: bind the proved requestor's post-marker range through the session
  file in which acceptance proved its marked resume. On initial activation and
  later continuation, require current session identity source `report`; a first
  timestamped record that is the validated TUIOS SessionStart marker for `startup`
  or `clear`, at or after creation of the requestor shell's single direct Claude
  child; no later SessionStart other than `compact`; the proved marked input in
  that file; unchanged process identity across the read; and validated ordering
  and design item 1's generation-scoped exclusivity. Missing or uncertain evidence remains pending.
  This covers the command's `--clear` and a manual clear before the run. Q19=A
  retains pre-clear transcripts and Q22=A retains earlier starts and matches
  their lifecycle records across files. Design item 1's complete-generation rule still
  governs the reviewer's absence proof. Validate the clear-marker shape, process
  precedence and cross-file lifecycle matching in disposable sessions; timestamp
  comparison retains Q21=A's disclosed clock limitation. No new channel is added,
  and the human choice itself establishes no supported profile.
- Validate turn closure with and without a background start: record persistence order and identify the last closing record. An idle screen alone is insufficient; require every tool call's result, every result's call and the validated final record. Apply the closure condition to the last turn of every in-scope transcript. This includes the proved requestor's transcript: Q22=A excludes validated post-marker starts, not an unclosed requestor turn. Preserve these checks under the confirmed Q18-Q20 scopes.
- Every potential Claude wait remains pending: no permitted current-liveness source exists. Positive absence requires complete start/end persistence for host-managed waiting mechanisms (Q20=A), plus fresh idle/empty-input and stable bindings. Unmatched starts stay pending across host-process generation changes: forced termination left background commands running on 2026-11-12, and no recorded cleanup proof has been observed. A validated true OS boot bounds ordinary surviving processes but never discards durable schedules. Lifecycle experiments establish record shapes rather than presumed cleanup. Unmatched starts, old snapshots and notification delays never prove liveness or absence; ownership fencing and lease expiry do not prove absence either.
- The implementation agent runs controlled disposable validation; existing review panes are excluded. Claude reviewer watchers must start through host background mechanisms. An in-scope recognizable-record gap stays pending and returns to design review with a specifically named extra evidence proposal. Each activation report discloses detached foreground/hook processes, unavailable earlier hook configuration history and undetectable backward clock changes since boot, including offsetting changes (Q21=A). Optional detaching-launcher rejection is defense in depth, never absence proof. Only Q21's named boot-instant process metadata is additionally approved; no event-log or general extra channel is approved. Both hosts and all remaining gates remain required. These expectations record no implementation-check result or completed status.
- Q01 is settled: Step 1 creates `tests/unit/tools/resume_paused_test_support.py` with pure synthetic host, pane and session builders; baseline 0, below-550 safe-to-extend band, ceiling 650. Later unit and acceptance tests import the builders as read dependencies; scenario assertions remain local. Split support by responsibility if needed.
- Validate candidate transcripts' recorded `cwd` against the resolved checkout under the design's path rules: project-directory encoding is lossy. Exclude another checkout's transcript only on validated evidence; otherwise retain it. Include checkout-subdirectory session directories unless validation proves they cannot hold a reviewer watcher for this checkout. Enumerate/read completely with byte accounting. Apply Q21=A fixed-boundary protection and Q22=A narrow requestor-work handling only with validated contracts; uncertain evidence stays pending. Parse only required classified structural fields in memory, never print or retain conversations/tool payloads, and report counts and reasons only. Determine schedule survival/restoration for every pinned version; a validated none makes the regardless-of-boot set empty by contract.

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

## Step 2. Parse pause artifacts and observe exact review state without writes

### Analysis of Step 2 implementation state

Not started. Step 2 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 2

Provide strict shared inputs and a pure exact-exchange observation boundary.

### Step 2 improvement expectations

- A canonical checkout snapshot distinguishes unused, used, malformed and unresolved inputs without creating directories or claiming roles.
- Read-only tests establish zero prompt/receipt/journal/review/authorization writes. Compatibility fixtures preserve prompt heading, Session role, and exact Prompt/SHA-256/Project root receipt grammar without importing senv.
- Unknown routing fields preserve the pause and produce unresolved-target skips; contradictory JSON/table data produces an error. Both outcomes have explicit tests.

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

## Step 3. Emit JSON routing at pause and align manual artifact readers

### Analysis of Step 3 implementation state

Not started. Step 3 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 3

Make newly paused sessions carry complete machine-readable assignments while retaining manual and installed-launcher readability.

### Step 3 improvement expectations

- Historical authorship and intended assignments remain separate; unresolved targets are explicit and never guessed.
- New pause examples parse under Step 2, readable tables derive from JSON, and legacy fixtures remain valid. `pause-session`, `status-session` and `list-session` describe schema-3 compatible readers; `resume-session` gains its schema-3 reader and writer in Step 4.
- Contract tests cover requirement Q29=A and acceptance criterion 14: differing known pane or role guards replacement, unknown values alone do not, legacy agent-id comparison survives, and declining preserves the old checkpoint. Capture contacts no counterpart and never launches the bulk CLI.

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

## Step 4. Validate marked receivers and fence every protected mutation

### Analysis of Step 4 implementation state

Not started. Step 4 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 4

Bind human launch consent to independently proved latest input and the exact receipt/claim operation.

### Step 4 improvement expectations

- A valid marker authorizes only its bound overrides; mismatch stops before protected writes without fallback consent questions.
- Both receiving workflows invoke fresh validation before each protected mutation. Every outcome emits the compact result of at most 100 characters (launch id, outcome and optional generation, no token/digest); it is the first final-response line on a stopping Claude turn and precedes stopping or asking on failure. Test success/failure grammar and length. Marked claim evidence is atomic with its generation, never added by a later bulk write. Existing manual claim, role conflict, fencing and review isolation regressions pass.
- The new `test_resume_paused_validate_launcher_smoke_tdd.py` in the Step 4 validation leaf checks the agent-callable read-only validator launcher's argument forwarding, UTF-8 JSON and exit codes with temporary fixtures; baseline 0, below-550 safe-to-extend band, ceiling 650.
- Q02 is settled: Step 4 creates shared test-only `tests/unit/tools/resume_paused_receiver_test_support.py`, used by Step 8 acceptance. It calls the real validator and locked claim against temporary receipt/journal files, changing evidence before every protected step; baseline 0, below-550 safe-to-extend band, ceiling 650. Separate instruction-contract checks complement its executed sequence; neither proves arbitrary live-agent compliance. It adds no production receipt writer or new authorization mechanism.
- Q04 is settled: thread raw marker and carried Codex identity/launch id through parser, CLI, `claim_selected`, store and `OwnershipService`. Under the transition lock, parse the marker and derive assignment binding from current prompt/routing/locked exchange, rejecting changes atomically with no claim write. For Codex, require carried session identity and launch id; test missing identity/id and launch-id mismatch with the marker. Persist only derived nonsecret launch id, pane, host, assignment binding, round, occurrence and issued generation. The claim reads no host session file and has no TUIOS dependency; retain the separate fresh pane/complete-input validator call immediately before claim.

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

## Step 5. Build the read-only checkout planner and duplicate protections

### Analysis of Step 5 implementation state

Not started. Step 5 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 5

Classify every prompt-bearing checkout and produce deterministic safe preview actions.

### Step 5 improvement expectations

- Preview and execution share the same classified plan, with no guessed target or mutation.
- One planned result per discovered prompt-bearing checkout, including used and skipped prompts; omitted panes are counted. Global validation failures yield no input. Dry-run makes zero transport mutations.
- Test pane-label-only `--except` scope, no pane-label matching by `--switch-roles`, skips for a missing UUID or a target without an agent (including CMD), changed-host classification errors, and ambiguous multiple exchanges with no saved identity. No counterpart input reaches a shell or ambiguous pairing.

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

## Step 6. Deliver guarded pane actions with bounded acceptance

### Analysis of Step 6 implementation state

Not started. Step 6 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 6

Execute one safe action at a time per checkout while independent checkouts progress concurrently.

### Step 6 improvement expectations

- Every input is freshly eligible and targets exactly one current full pane identity; uncertain submission never causes retyping.
- Injected transport captures exact argv and zero unintended input. Recovery is at most one pane-targeted Enter without retype or deadline reset. No bulk artifact writes or live CLI delivery occur during tests.

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

## Step 7. Confirm takeover and activate only a verified missing reviewer

### Analysis of Step 7 implementation state

Not started. Step 7 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 7

Separate acceptance, consumption and current ownership, then safely handle reviewer continuation.

### Step 7 improvement expectations

- Only proven requestor takeover and positive no-wait evidence permit a missing counterpart action.
- Paused reviewer resumes only itself; non-requestor roles never activate a pair. Requestor receipt without current bound claim cannot trigger counterpart. No-wait ambiguity yields pending/no input, and uncertain earlier delivery is never resent.
- Fake-clock tests cover event-driven observation or bounded-read backoff capped at five seconds, without extending the separate 120-second-per-receiver deadline or reusing stale safety evidence.

- Every Claude reviewer activation outcome and conditional-activation preview carries `limits=claude-wait-scope`, defined in help/reference as the three Q20=A limits. Fake-clock takeover tests cover emission and preserve other result/exit semantics; the disclosed clock scope includes Q21=A's undetectable backward changes since boot. Validate Q22=A on initial activation and continuation, including retained earlier/other-pane/reviewer-watcher blockers and pending on ambiguous generation/order. Exercise Step 1's validated Q23=A startup-or-clear binding for the requestor's marked-input file after command-driven and prior manual clear; refresh every condition and reject changed or missing evidence. Keep the reviewer's complete-generation rule and earlier-start lifecycle matching across session files.

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

## Step 8. Ship the CLI and validate the complete installed workflow

### Analysis of Step 8 implementation state

Not started. Step 8 is not implemented because its planned code, contract changes and focused validation have not been delivered or checked.

### Goal for Step 8

Expose human-only command/reporting and validate the full two-host workflow with fake TUIOS.

### Step 8 improvement expectations

- Humans can preview or resume eligible panes with deterministic outcomes and clear compatibility limits.
- All acceptance criteria map to passing scenarios; targeted tests and scope-resolved whole-suite groundhog gate pass in the same cycle. Record supported profiles and remaining external evidence honestly. Completion handoff retains the unchecked requirement deferred-senv checklist and full all-eligible-session integration obligation; do not mark that separate effort complete.
- Verify the bulk launcher statically for self-location, shared Python selection and argument forwarding to `tools/resume_paused.py`; agents never execute it. Injected parser/main and process acceptance do not establish live Windows launcher or pane-delivery behavior, which requires human evidence. Preserve the receiver harness's live-agent proof limit.
- Q03 is settled: Step 8 creates `test_resume_paused_cli_safety_tdd.py` (caller rejection/dry run/exclusion and switch validation/reporting and exit codes/`tuitp` grammar/legacy manual resumes), `test_resume_paused_delivery_tdd.py` (clear/transport/guard races/recovery Enter/receiver protected-write failures), and `test_resume_paused_continuation_tdd.py` (takeover/reviewer leave-alone/pending and activation/later and switched continuation) in the acceptance leaf. Each is new, baseline 0, below-550 safe-to-extend band, ceiling 650. They use approved Step 1 builders, Step 4 receiver harness and acceptance fakes; the eight numbered steps remain unchanged.

- CLI help and the reference page define `limits=claude-wait-scope` as all three Q20=A limits, with Q21=A's since-boot clock scope. Parser/help tests and `test_resume_paused_cli_safety_tdd.py` verify code presence and meaning on every Claude activation outcome and conditional-activation preview; continuation acceptance covers emission through actual fake activation paths.

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
