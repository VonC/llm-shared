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

Yes. Step 1 has been fully implemented.

The round 6 reviewer confirms the Step 1 code deliverable under plan Q05=A. The repairs of rounds 1 through 5 are present, including R5-1: every proved continuation into a listed file requires its predecessor, and the regression cases cover missing ancestors, foreign, unreadable and incomplete predecessors alongside a complete-history control and the boot boundary. No unresolved code finding remains. The read-only adapters and shared builders are implemented; the writer reports a green whole-suite speed gate with 6166 tests and 100% coverage over `tools`. The reviewer assessed coverage statically and did not repeat the gate. This is not host support: the registry remains empty, every live validation row stays open, and Steps 6 through 8 remain blocked until both hosts have a pinned profile.

### Goal for Step 1

Establish usable read-only evidence for both hosts before enabling any delivery.

### Step 1 improvement expectations

- Both hosts have explicit supported profiles or implementation stops for design review before delivery work.
- Record the actual supported host versions, independent pre-input source, input/result/clear signatures and Claude positive no-task proof, with evidence limits. If neither Codex candidate works or required Claude proof cannot be validated, return the unresolved point to design review; do not silently enable hooks or ship one host.
- Validate the documented Codex candidate set across all host-session date partitions, including older active sessions, timestamp-resolution boundaries, a second matching file and total bytes scanned. Incomplete enumeration or latest-input evidence fails closed; subsequent checks retain and reprove the same unique identity.
- Validate the consolidated Codex native image contract: one direct child, query rights only, complete allocation-metadata walk with exactly one committed matching image allocation, both native image-name APIs, GLOBALROOT read/execute open sharing read/delete, successful class-44 identity query and hashing through the same retained handle. Verify the pinned digest and exact same-release manifest; refresh all mutable bindings before input. Exclude memory reads and module enumeration.
- Record each validated `RtlGetVersion` build number and observed update revision. Cover unsupported/invalid builds, denied/unavailable APIs, every non-success identity status, rename/stale paths, tunneling, identical and other pinned-release replacements, actual updater behavior and process/handle races. No replacement exception applies. Later session-file version disagreement stops consumption and claim.
- Validate Claude's complete generation/session marker coverage with existing explicit launcher settings only (Q18=A), root/nested record classification, timestamp semantics, ordering, design item 1's generation completeness and closure for every writer and documented current-source exclusion. An installed TUIOS integration, alone or combined with launcher settings, and missing or uncertain provenance stays pending. Install no hooks. Include every attach path to an existing session id, with and without the launcher settings and including nested print-mode resume, while the original root runs and after it exits; record its shapes, whether its turns close under design item 1 or which conservative trigger holds them pending, whether its turn input persists before that turn's first tool runs, and whether its closing records persist last, against the original-process controls (design item 1, case 6). Cover checkpointing enabled and disabled, print-mode resume, `--continue`, in-process `/resume`, a first tool that starts background work, a local command that executes work, such as bash-mode input, and closing-record ordering after parallel calls and fan-out leaves. Apply confirmed Q26=A: roots with no records in the Q19 read set fall under the fourth disclosed limit, including persistence-disabled roots resuming an existing session id, other configuration roots and transcripts removed without detectable evidence. Validate recorded parent coverage through ordinary exit, host kill, TaskStop and timeout; record which end paths leave unrecorded work running after the parent ends. Open parent turns, unmatched starts, partially recorded work, detected missing history and incomplete reads remain pending. A recorded start needs its own validated terminal record; parent termination alone is insufficient. Validate rejection of a target without a fresh persisted startup/clear marker, interactive handling of the print-only persistence flag, configuration-root resolution for each bound pane and retention/deletion behavior. Preserve all input-before-effect and closing-record-last checks for recorded work. Cover interactive background sessions, reattachment, nested roots, Monitor, subagents and schedules. No collector, new source or supported profile is introduced. Read all checkout Claude-project transcripts active since the last OS boot and all relevant durable schedule definitions regardless of boot (Q19=A), with complete generation ranges, enumeration and record byte accounting. Validate activity selection and true-boot semantics; unresolved Windows fast startup, missing history, uncertain activity or schedule restoration stays pending. Cover all in-scope host-managed waiting mechanisms, typed/slash input and notifications, subagent commands, compaction and documented lifecycle paths.
- Validate Q21=A's fixed boot instant from the creation timestamp of a validated process that starts at boot. Cover concrete source selection, timestamp stability under forward/backward changes, uptime semantics, comparison tolerance and fast startup. Never select history using current time minus uptime; detected net backward movement beyond the validated tolerance stays pending. Disclose undetectable backward changes since boot, including offsetting changes. No event-log or general extra channel is approved. The uptime value must count time spent in sleep and hibernation. Validate this, and test suspension between boot and the decision. An uptime that excludes suspended time would hide a backward change of up to the suspended duration.
- **Confirmed design Q25=A:** Require evidence for the host background
  `wait-answer` start as one recognized invocation form, turn closure, terminal
  record and notification resumption. The required transport covers every
  Claude requestor route; Codex retains attached waiting.
- **Confirmed design Q24=A:** Validate the operation-based exception below without
  claiming writer identity; the decision itself establishes no supported profile.
- Validate Q22=A as qualified by Q24=A on initial activation and later continuation: exclude only starts in the Q23-bound requestor file ordered after the marked resume input by validated creation ordering that parse as validated requestor review-exchange operations, with their own lifecycle records, whichever root wrote them. Every other start, including the requestor's other post-marker work, stays in scope. Keep earlier starts, other transcripts and recognized reviewer `wait-any-request` starts in scope, including starts inside the proposed exception and former-reviewer starts after role switching. Ambiguous file binding, operation classification or ordering remains pending. Preserve complete reads/classification needed for the exception, byte accounting, exact takeover proof and fresh required bindings in both panes. The exception removes only starts that validated creation ordering places after the marked resume input, with those starts' own lifecycle records. File position alone never places a record after the marker. Terminal, stop and completion records after the marker still match in-scope starts ordered before it. This includes any such record the host writes into a later session file after a clear. A start whose order relative to the marker is uncertain stays in scope. Inside the excluded range, a start that invokes the review-exchange launcher counts as a reviewer watcher unless its operation parses as a validated requestor operation. A start qualifies only when its complete recorded command matches exactly one recognized requestor invocation form with a requestor-only operation. Chained, piped, wrapped or multi-operation commands, and operations either role may run, stay in scope under normal start/end matching. Validate the recognized invocation forms for each pinned version. A recognized watcher stays in scope under normal start/end matching and blocks until its validated terminal record.
- Validate Q23=A: bind the proved requestor's post-marker range through the session
  file in which acceptance proved its marked resume. On initial activation and
  later continuation, require current session identity source `report`; a first
  timestamped record that is the validated TUIOS SessionStart marker for `startup`
  or `clear`, at or after creation of the requestor shell's single direct Claude
  child; no later SessionStart other than `compact`; the proved marked input in
  that file; unchanged process identity across the read; and validated ordering
  and design item 1's completeness and closure for every writer (Q24=A). Missing or uncertain evidence remains pending.
  This covers the command's `--clear` and a manual clear before the run. Q19=A
  retains pre-clear transcripts and Q22=A retains earlier starts and matches
  their lifecycle records across files. Design item 1's complete-generation rule still
  governs the reviewer's absence proof. Validate the clear-marker shape, process
  precedence and cross-file lifecycle matching in disposable sessions; timestamp
  comparison retains Q21=A's disclosed clock limitation. No new channel is added,
  and the human choice itself establishes no supported profile.
- Validate turn closure with and without a background start: record persistence order and identify the last closing record. An idle screen alone is insufficient; require every tool call's result, every result's call and the validated final record. Apply the closure condition to every input-bearing record and every chain tip of every in-scope transcript. This includes the proved requestor's transcript: Q24=A excludes only validated requestor review-exchange starts, not an unclosed requestor turn. Preserve these checks under the confirmed Q18-Q20 scopes as qualified by Q26=A for roots with no records.
- Every potential Claude wait remains pending: no permitted current-liveness source exists. Positive absence within the Q26=A scope requires complete start/end persistence for recorded host-managed waiting mechanisms (Q20=A), plus fresh idle/empty-input and stable bindings. Unmatched starts stay pending across host-process generation changes: forced termination left background commands running on 2026-11-12, and no recorded cleanup proof has been observed. A validated true OS boot bounds ordinary surviving processes but never discards durable schedules. Lifecycle experiments establish record shapes rather than presumed cleanup. Unmatched starts, old snapshots and notification delays never prove liveness or absence; ownership fencing and lease expiry do not prove absence either.
- The implementation agent runs controlled disposable validation; existing review panes are excluded. Claude reviewer watchers must start through host background mechanisms. An in-scope recognizable-record gap stays pending and returns to design review with a specifically named extra evidence proposal. Each activation report discloses detached foreground/hook processes, unavailable earlier hook configuration history and undetectable backward clock changes since boot, including offsetting changes (Q21=A), plus Q26=A's fourth limit for roots with no records. Optional detaching-launcher rejection is defense in depth, never absence proof. Only Q21's named boot-instant process metadata is additionally approved; no event-log or general extra channel is approved. Both hosts and all remaining gates remain required. These expectations record no implementation-check result or completed status.
- Q01 is settled: Step 1 creates `tests/unit/tools/resume_paused_test_support.py` with pure synthetic host, pane and session builders; baseline 0, below-550 safe-to-extend band, ceiling 650. Later unit and acceptance tests import the builders as read dependencies; scenario assertions remain local. Split support by responsibility if needed.
- Validate candidate transcripts' recorded `cwd` against the resolved checkout under the design's path rules: project-directory encoding is lossy. Exclude another checkout's transcript only on validated evidence; otherwise retain it. Include checkout-subdirectory session directories unless validation proves they cannot hold a reviewer watcher for this checkout. Enumerate/read completely with byte accounting. Apply Q21=A fixed-boundary protection and Q22=A requestor-operation handling as qualified by Q24=A only with validated contracts; uncertain evidence stays pending. Parse only required classified structural fields in memory, never print or retain conversations/tool payloads, and report counts and reasons only. Determine schedule survival/restoration for every pinned version; a validated none makes the regardless-of-boot set empty by contract.

### What was implemented for Step 1

- **Profile policy** (`tools/resume_paused_profiles.py`): verdicts, counted reasons, byte accounting, process identity, clock and command protocols, a pinned-profile registry that ships empty, caller classification from agent markers and ancestry, the Q21 boot comparison and the disclosed limits, including the fifth from design Q27=B.
- **Windows observations** (`tools/resume_paused_windows.py`): the `WindowsApi` protocol, pure direct-child and ancestry helpers, and `Win32Api`, which uses `PROCESS_QUERY_INFORMATION` only, an allocation-metadata walk, the native image name, the class 44 identity query, same-handle hashing and shared file reads.
- **Codex evidence** (`tools/resume_paused_codex.py`): release-layout parsing, the exact eight-key layout-1 manifest check, `CodexImageProver` with proof, recheck and release, and the session-file input proof with later refresh.
- **Claude evidence** (`tools/resume_paused_claude.py`, `tools/resume_paused_claude_graph.py`, `tools/resume_paused_claude_ledger.py`): allowlisted transcript parsing, record shapes, latest typed input, the in-memory marked-input match, review-exchange command classification and process-generation lookup; `TranscriptGraph`, which orders the records of one transcript by their parent links; and `ClaudeLedger`, which reports absence or pending with counted reasons.
- **Code review round 1 repairs**: R1 closure over every identified record, sidechains included, with repeated identifiers, unidentified inputs and missing parents pending. R2 pinned version and closed-world classification for every transcript read, schedule-only reads included. R3 each start matched to its own later end; a preceding end, a reused identifier and an unrelated session's end close nothing, and only a clear-marked file continues an earlier one. R4 checkout, report-sourced identity and unchanged process binding for the bound transcript, and the requestor-operation exception after a proved marked input. R5 missing or non-string linkage identifiers, timestamps without a timezone and repeated JSON keys rejected. R6 a process listing only when the walk ends with `ERROR_NO_MORE_FILES`. R7 well-typed Codex session identity and the single `input_text` message shape. R8 pane proof on the pinned submitted-command prefix, whole-token launch id and whole-line working pattern.
- **Code review round 2 repairs**: R2-1 a parent loop is counted, every input needs a final record below it that follows the pinned Stop summary and is reached before any other input, and a pinned leaf shape counts only under an input whose turn closed. R2-2 a call identifier shared by two calls or two results is pending, and a result must be recorded below its call in the parent chain. R2-3 an end closes a start only when strictly later; in another file it also needs a continuation pair the caller proved, `LedgerScope.continuations`, into a file that begins with a clear marker, so a clear marker alone closes nothing. No caller supplies such a pair yet. R2-4 the bound transcript needs at least one recorded `cwd` and none outside the checkout; a non-string `cwd` rejects the transcript. R2-5 a recognized invocation is one line naming `review_exchange.bat` by its exact file name; a line break or a longer file name keeps the start in scope. R2-6 each record keeps the type of every message content block, the profile pins the allowed block types, and a message, content or block of an unexpected JSON type rejects the transcript.
- **Code review round 3 repairs**: R3-1 the requestor exception covers the qualifying start record, never its task id; that start still counts as a use of its identifier, so an earlier or later start sharing it stays pending with the reuse, with or without a terminal record. R3-2 a pinned leaf needs an instant strictly before the final record of its turn; a leaf recorded at or after it, or with an unknown instant on either side, is pending. R3-3 `continuation_places` numbers each file along its single proved chain in one pass; a file with two proved successors or predecessors, or on a loop, is placed nowhere, so its link closes nothing.
- **Code review round 4 repairs**: R4-1 every transcript read since boot needs a complete generation, not only the bound one: its first timestamped record is an accepted marker and no later SessionStart other than a compaction follows. Another writer's transcript accepts the startup marker, or a clear marker only as the later file of a proved continuation; the bound process creation is never applied to it. R4-2 a supplied background task id, task id, queue status or `is_error` flag of the wrong type, or an empty one, rejects the transcript; a tool result whose container is not an object, or is absent, is unclassified unless it is a recorded error or every tool it answers is listed in the profile's `plain_result_tools`; a schedule creation without a nonempty string id is unrecognized; and a recorded error creates and deletes no schedule.
- **Code review round 5 repair**: R5-1 a proved continuation into a listed file needs its earlier file in the scope: an earlier file missing from the enumeration, or excluded as another checkout's transcript, counts `continuation-predecessor-missing`, link by link, so a missing ancestor in a chain of clears is counted too. An unreadable or incomplete earlier file stays pending under its own read reason, and one older than the boot boundary stays under the boot rule.
- **Shared builders** (`tests/unit/tools/resume_paused_test_support.py`): declared Windows observations, Codex sessions and manifests, Claude records and sources, with no assertion.
- **Evidence document**: a 2026-11-15 section records the delivery, the unchanged support status and the self-observation of the binding.
- **Pane tie and carried launch id**: `prove_codex_pane` requires this delivery's launch id on exactly one captured line, which must be a submitted-command line, followed by a line matching the profile's working pattern; the input proof carries the launch id, the delivered command must contain it, and the refresh rejects a proof from another delivery.
- **Real enumeration**: `list_jsonl_files` lists regular JSONL files under a root across all sub-directories and reports an incomplete enumeration on any listing error, symbolic link or junction; `DirectorySessionStore` and `DirectoryTranscriptSource` put it behind the two store protocols with an injected whole-file reader.
- **Validation evidence**: the round 6 review request records the writer's `ghog day --full=speed --whole-suite` walk on the staged tree that holds these repairs, with its time, exit code, coverage and outliers. The reviewer's findings of rounds 2 to 5 were static counterexamples; the writer turned each one into a test that fails without its repair.

### Live validation checklist for Step 1

Plan Q05=A keeps these rows open without blocking Steps 2 through 5. Steps 6 through 8 stay blocked until both hosts have a pinned profile. No row below is validated.

- [ ] Claude: local-command completion and the pane-idle guard of design Q27=B on each pinned version.
- [ ] Claude: turn closure for every input kind and chain tip, including parallel calls, fan-out leaves, notifications, slash input and compaction.
- [ ] Claude: every attach and continuation path, with and without launcher settings, original alive and exited.
- [ ] Claude: launcher-only provenance and root or nested classification.
- [ ] Claude: lifecycle records of PowerShell, Bash, moved foreground work, Monitor, subagents and schedules.
- [ ] Claude: checkout transcript discovery with lossy project names and sub-directories.
- [ ] Claude: boot-process source and tolerance (design Q28=A: clock, sleep and fast-startup cases recorded as not reproduced).
- [ ] Claude: schedule survival and restoration (seven-day expiry recorded as not reproduced).
- [ ] Claude: requestor-operation exception, requestor file binding and background `wait-answer` transport.
- [ ] Claude: recorded parent coverage through exit, kill, TaskStop and timeout; fresh delivery-time guards.
- [ ] Claude: the evidence that proves a clear continuation between two session files, such as the pane's reported session id changing while its Claude process stays the same, and how a caller records that pair.
- [ ] Claude: the message content block types, the leaf shapes and the call-to-result parent linkage of each pinned version, parallel calls included.
- [ ] Claude: the tool result containers of each pinned version: which tools return a result that is not an object, and that a result flagged `is_error` starts, creates and deletes nothing.
- [ ] Codex: image identity under rename, stale paths, tunneling, replacements, junction retargeting and races (real updater run recorded as not reproduced).
- [ ] Codex: pinned release, build, digest and manifest set.
- [ ] Codex: unique full-input and pane proof, refresh after scroll-off, timestamp resolution.
- [ ] Codex: version-specific input, result, clear, idle and busy signatures.
- [ ] Both: caller classification against real agent and human shells.

### New types or classes introduced for Step 1

- `Host`, `Verdict`, `CallerOrigin`, `Reason`, `ReadAccount`, `ProcessIdentity`, `CommandResult`, `Clock`, `CommandRunner`: shared vocabulary and injected protocols.
- `HostProfile`, `ProfileDecision`, `ProfileRegistry`, `CallerDecision`, `BootObservation`, `BootDecision`: profile and boundary policy.
- `ProcessRecord`, `ImageWalk`, `WindowsApi`, `Win32Api`, `JsonlFile`: Windows and file observations.
- `DirectorySessionStore`, `DirectoryTranscriptSource`: real directory access behind the store protocols.
- `ReleaseLayout`, `CodexImageProof`, `CodexImageDecision`, `CodexImageProver`, `SessionFile`, `SessionStore`, `CodexInputQuery`, `CodexInputProof`, `CodexInputDecision`: Codex evidence.
- `ClaudeLedgerProfile`, `ParseScope`, `RecordFact`, `ExchangeCall`, `TranscriptRejectedError`, `TranscriptFile`, `TranscriptSource`: Claude parsing.
- `TranscriptGraph`: Claude record graph.
- `Absence`, `LedgerScope`, `LedgerDecision`, `ClaudeLedger`: Claude ledger.
- `CodexPaneProfile`: pinned Codex screen signatures.
- `FakeWindowsApi`, `FakeSessionStore`, `FakeTranscriptSource`: test-only declared observations.

### Architecture check for Step 1

- **Ports and adapters**: policy and both host modules depend on the `WindowsApi`, `SessionStore` and `TranscriptSource` protocols; only `Win32Api` touches `ctypes`.
- **Import direction**: `resume_paused_profiles` imports no sibling; `resume_paused_windows` imports none; the Codex and Claude modules import those two and not each other; the graph imports the Claude parsing module, and the ledger imports the parsing and graph modules.
- **Read-only boundary**: no module writes a file, sends input, starts a process or calls the bulk command.
- **File size**: all new files are below the 650-line ceiling. The largest implementation module, `tools/resume_paused_claude_ledger.py`, has 642 lines; the largest test file, the first ledger test file, has 578. The plan explicitly makes advisory estimates nonblocking. The ledger was split from the parsing module, and the record graph from the ledger, by responsibility; ordering and evidence-completeness tests occupy separate files.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 1

- **No new `O(n^2)` or `O(n log n)` path**: parsing and the ledger make single passes with set and map lookups; reason codes are sorted once over a fixed small set of codes. The record graph numbers each transcript's records in one depth-first walk, so "is this record below that one" is two map lookups, and it walks each record at most once to find its turn. The proved continuation pairs are indexed once: each file gets its chain head and position in one pass over the pairs, and "does this file continue that one" is two map lookups. No reachable-pair set is built; a test numbers a chain of a thousand clears and finds one entry per file. The files a continuation leads into are indexed once per decision, so each transcript's accepted first markers come from one set lookup.
- **Read cost**: bytes read follow the selected transcripts and session files and are accounted per file.
- **Windows path**: one process listing per proof, one allocation walk per binding check, one hash per image per invocation.
- **Plan-bound alignment**: within the plan's evidence-proportional bound.

The step stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 1

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`); all six implementation modules are inside it. The percentages below are the writer's measured coverage from the walk named above.

- **`tools/resume_paused_profiles.py`**: covered at 100% by `test_resume_paused_profiles`.
- **`tools/resume_paused_windows.py`**: covered at 100% by `test_resume_paused_windows`; two failure branches that need a failing kernel call carry a coverage exclusion comment. Its `Win32Api` and junction tests run on Windows only.
- **`tools/resume_paused_codex.py`**: covered at 100% by `test_resume_paused_codex`.
- **`tools/resume_paused_claude.py`**: covered at 100% by `test_resume_paused_claude`, including malformed lifecycle fields and the plain and failed result flags.
- **`tools/resume_paused_claude_graph.py`**: covered at 100% by `test_resume_paused_claude_graph`, which tests ordering, turns, loops and call faults directly.
- **`tools/resume_paused_claude_ledger.py`**: covered at 100% by `test_resume_paused_claude_ledger`, with one regression case per round 1 finding and one regression group per round 2 finding: allowed-leaf open sidechains and loops, shared and out-of-order call identifiers, unrelated clear-marked files and equal instants for tasks and schedules, absent, mixed and malformed bound `cwd`, multiline and wrong-launcher commands, and unknown or malformed message content. Its second test file holds one group per round 3 finding: starts sharing a covered task id, pinned leaves at or after their turn's final record, and long, branching and looping continuation chains. Its third holds one group per round 4 finding: other writers' missing, resume, unproved clear and restart markers next to complete, compacted and early-started ones; malformed task identifiers, schedule creations without an identifier, plain and absent result containers, recorded errors and validated plain tools; and, for round 5, absent, foreign, unreadable, incomplete and pre-boot predecessors of a cleared file, a missing ancestor in a chain of clears and the complete chain.

No, there is no unit-tested class below 100% that needs completing for Step 1.

### Feature integrity for Step 1

- **Existing feature behavior**: no existing module is imported differently or changed; the new modules have no caller yet.
- **Reporting or diagnostics**: unchanged.
- **Compatibility note**: `instructions/pause-session.md` regains the wording an existing structure test pins; `.markdownlint-baseline.json` is unchanged. Under the user's exceptions of 2026-11-15 (plan Q06 and Q07), 26 headings of the design review transcript gained an exchange qualifier, and the two v0.14.0 review transcripts received a whitespace-only list-spacing repair; `rvw_status` still reports a trustworthy idle state.

No existing feature or reporting capability appears impaired.

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

Q25=A is confirmed. Verify that `rules/run_commands.md` requires each Claude
requestor `wait-answer` to start through a host background mechanism as one
recognized invocation form, end the turn and resume from the completion
notification on every route. Verify references from
`instructions/review-requestor.md`, `instructions/spec-review-requestor.md`
and `instructions/code-review-requestor.md`. Foreground or moved waits stay
in scope and leave the reviewer pending with that reason. Require Step 1
evidence for the background start, turn closure, terminal record and notification
resumption. Preserve Codex attached waiting. This records a validation
obligation, not an implementation or host-support result.

Require `tests/unit/tools/test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`
to exist and pass: it checks that the shared rule requires Claude background
`wait-answer` on every requestor route, retains Codex attached waiting and is
referenced by all three requestor instructions. Existing instruction-structure
tests must still pass.

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

- Every Claude reviewer activation outcome and conditional-activation preview carries `limits=claude-wait-scope`, defined in help/reference as the three Q20=A limits plus Q26=A's fourth limit. Fake-clock takeover tests cover emission and preserve other result/exit semantics; the disclosed clock scope includes Q21=A's undetectable backward changes since boot. Validate Q24=A on initial activation and continuation: only validated requestor review-exchange operations in the Q23-bound file qualify regardless of writer, with validated creation ordering after marked input. Retain all other-work blockers; ambiguous file binding, classification or ordering remains pending. Exercise Step 1's validated Q23=A startup-or-clear binding for the requestor's marked-input file after command-driven and prior manual clear; refresh every condition and reject changed or missing evidence. Keep the reviewer's complete-generation rule and earlier-start lifecycle matching across session files.

Under Q26=A, help/reference name work of roots with no records in Q19's read
set: persistence-disabled roots, other configuration roots, transcripts removed
without detectable evidence and unrecorded work surviving a recorded parent's
validated end. Include the end paths established by Step 1. Injected-ledger
tests on initial activation and later continuation verify that such invisible
work is a disclosed possible duplicate-watcher limit when every other gate
passes. Verify that open recorded parent turns, unmatched starts, partially
recorded work, detected missing history and incomplete reads still block.
Do not infer completion of a recorded start from its parent's termination.

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

- CLI help and the reference page define `limits=claude-wait-scope` as all three Q20=A limits plus Q26=A's fourth limit, with Q21=A's since-boot clock scope. Parser/help tests and `test_resume_paused_cli_safety_tdd.py` verify code presence and meaning on every Claude activation outcome and conditional-activation preview; continuation acceptance covers emission through actual fake activation paths.

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
