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

This verdict is the round 6 code-review result for the code deliverable that plan Q05=A scopes. It does not certify the obligations that design Q27=B and Q28=A, consolidated on 2026-11-17, added later: the conservative boot-boundary and schedule handling of Step 1 stays open in the follow-up section below and must be complete before any profile is pinned, and the all-pane idle guard belongs to Step 7.

### Goal for Step 1

Establish usable read-only evidence for both hosts before enabling any delivery.

### Step 1 improvement expectations

- Both hosts have explicit supported profiles or implementation stops for design review before delivery work.
- Record the actual supported host versions, independent pre-input source, input/result/clear signatures and Claude positive no-task proof, with evidence limits. If neither Codex candidate works or required Claude proof cannot be validated, return the unresolved point to design review; do not silently enable hooks or ship one host.
- Validate the documented Codex candidate set across all host-session date partitions, including older active sessions, timestamp-resolution boundaries, a second matching file and total bytes scanned. Incomplete enumeration or latest-input evidence fails closed; subsequent checks retain and reprove the same unique identity.
- Validate the consolidated Codex native image contract: one direct child, query rights only, complete allocation-metadata walk with exactly one committed matching image allocation, both native image-name APIs, GLOBALROOT read/execute open sharing read/delete, successful class-44 identity query and hashing through the same retained handle. Verify the pinned digest and exact same-release manifest; refresh all mutable bindings before input. Exclude memory reads and module enumeration.
- Record each validated `RtlGetVersion` build number and observed update revision. Cover unsupported/invalid builds, denied/unavailable APIs, every non-success identity status, rename/stale paths, tunneling, identical and other pinned-release replacements, actual updater behavior and process/handle races. No replacement exception applies. Later session-file version disagreement stops consumption and claim.
- Validate Claude's complete generation/session marker coverage with existing explicit launcher settings only (Q18=A), root/nested record classification, timestamp semantics, ordering, design item 1's generation completeness and closure for every writer and documented current-source exclusion. An installed TUIOS integration, alone or combined with launcher settings, and missing or uncertain provenance stays pending. Install no hooks. Include every attach path to an existing session id, with and without the launcher settings and including nested print-mode resume, while the original root runs and after it exits; record its shapes, whether its turns close under design item 1 or which conservative trigger holds them pending, whether its turn input persists before that turn's first tool runs, and whether its closing records persist last, against the original-process controls (design item 1, case 6). Cover checkpointing enabled and disabled, print-mode resume, `--continue`, in-process `/resume`, a first tool that starts background work, a local command that executes work, such as bash-mode input, and closing-record ordering after parallel calls and fan-out leaves. Apply confirmed Q26=A: roots with no records in the Q19 read set fall under the fourth disclosed limit, including persistence-disabled roots resuming an existing session id, other configuration roots and transcripts removed without detectable evidence. Apply confirmed design Q27=B: a local shell command that runs before its input is recorded falls under the fifth disclosed limit for Claude roots without a TUIOS pane; validate local-command completion records, an idle signature that rejects a running local command, and fresh validated idle evidence from every live Claude pane of the checkout, the proved requestor included after its Q25=A turn closure, on initial activation and later continuation. Validate recorded parent coverage through ordinary exit, host kill, TaskStop and timeout; record which end paths leave unrecorded work running after the parent ends. Open parent turns, unmatched starts, partially recorded work, detected missing history and incomplete reads remain pending. A recorded start needs its own validated terminal record; parent termination alone is insufficient. Validate rejection of a target without a fresh persisted startup/clear marker, interactive handling of the print-only persistence flag, configuration-root resolution for each bound pane and retention/deletion behavior. Preserve all input-before-effect and closing-record-last checks for recorded work other than Q27=B's local shell input. Cover interactive background sessions, reattachment, nested roots, Monitor, subagents and schedules. No collector, new source or supported profile is introduced. Under confirmed design Q28=A, cases the agent cannot reproduce stay recorded as designed fail-closed, not reproduced, only with tested conservative handling: an affected activation stays pending, an unproved boot boundary discharges no ordinary work, no schedule ends by an untested expiry or restart assumption, and every Codex image recheck stays mandatory. Read all checkout Claude-project transcripts active since the last OS boot and all relevant durable schedule definitions regardless of boot (Q19=A), with complete generation ranges, enumeration and record byte accounting. Validate activity selection and true-boot semantics; unresolved Windows fast startup, missing history, uncertain activity or schedule restoration stays pending. Cover all in-scope host-managed waiting mechanisms, typed/slash input and notifications, subagent commands, compaction and documented lifecycle paths.
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
- The implementation agent runs controlled disposable validation; existing review panes are excluded. Claude reviewer watchers must start through host background mechanisms. An in-scope recognizable-record gap stays pending and returns to design review with a specifically named extra evidence proposal. Each activation report discloses detached foreground/hook processes, unavailable earlier hook configuration history and undetectable backward clock changes since boot, including offsetting changes (Q21=A), plus Q26=A's fourth limit for roots with no records and design Q27=B's fifth limit for a running local shell command whose input is not yet recorded. Optional detaching-launcher rejection is defense in depth, never absence proof. Only Q21's named boot-instant process metadata is additionally approved; no event-log or general extra channel is approved. Both hosts and all remaining gates remain required. These expectations record no implementation-check result or completed status.
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

### Open code follow-up for Step 1

Design Q28=A, consolidated on 2026-11-17, requires code that the round 6 code review did not cover. These rows stay open until the named tests pass in the scope-resolved walk; they must close before any profile is pinned, and they do not block Steps 2 through 5.

- [ ] `tools/resume_paused_profiles.py`: `BootDecision` reports a resolved or unresolved boundary; only a profile that records validated true-boot semantics, sleep-inclusive uptime and its tolerance basis resolves it. Test: `test_resume_paused_profiles_tdd.py`.
- [ ] `tools/resume_paused_claude_generation.py` (new): the ledger's generation and continuation checks are extracted before the ledger grows past its 642 of 650 lines. Test: `test_resume_paused_claude_generation/test_resume_paused_claude_generation_tdd.py` (new).
- [ ] `tools/resume_paused_claude_ledger.py`: an unresolved boundary excludes no earlier ordinary work; missing or incomplete required history stays pending; a recurring firing, an assumed expiry or a host restart closes no schedule. Test: `test_resume_paused_claude_ledger/test_resume_paused_claude_ledger_boot_tdd.py` (new), with an older unmatched task under an unproved boundary, a resolved true-boot control, complete older history with matched ends, missing or incomplete history and durable schedules without validated termination.
- [ ] `tools/resume_paused_codex.py`: unchanged, with every process, image, path and manifest recheck kept mandatory while the real-updater experiment is deferred. Test: `test_resume_paused_codex_tdd.py`.

The all-pane idle guard of design Q27=B is Step 7 runtime work, not a Step 1 row: Step 1 validates only the screen profile's idle signature, which must reject a running local command, and pinning a profile does not wait for Step 7.

### Live validation checklist for Step 1

Plan Q05=A keeps these rows open without blocking Steps 2 through 5. Steps 6 through 8 stay blocked until both hosts have a pinned profile. No row below is validated.

- [ ] Claude: local-command completion and the all-pane idle guard of design Q27=B, the proved requestor pane included, on each pinned version.
- [ ] Claude: turn closure for every input kind and chain tip, including parallel calls, fan-out leaves, notifications, slash input and compaction.
- [ ] Claude: every attach and continuation path, with and without launcher settings, original alive and exited.
- [ ] Claude: launcher-only provenance and root or nested classification.
- [ ] Claude: lifecycle records of PowerShell, Bash, moved foreground work, Monitor, subagents and schedules.
- [ ] Claude: checkout transcript discovery with lossy project names and sub-directories.
- [ ] Claude: boot-process source and tolerance (design Q28=A: clock, sleep and fast-startup cases recorded as not reproduced, with tested conservative handling and a recorded tolerance basis).
- [ ] Claude: schedule survival and restoration (seven-day expiry recorded as not reproduced; design Q28=A discharges no schedule by an untested expiry or restart).
- [ ] Claude: requestor-operation exception, requestor file binding and background `wait-answer` transport.
- [ ] Claude: recorded parent coverage through exit, kill, TaskStop and timeout; fresh delivery-time guards.
- [ ] Claude: the evidence that proves a clear continuation between two session files, such as the pane's reported session id changing while its Claude process stays the same, and how a caller records that pair.
- [ ] Claude: the message content block types, the leaf shapes and the call-to-result parent linkage of each pinned version, parallel calls included.
- [ ] Claude: the tool result containers of each pinned version: which tools return a result that is not an object, and that a result flagged `is_error` starts, creates and deletes nothing.
- [ ] Codex: image identity under rename, stale paths, tunneling, replacements, junction retargeting and races (real updater run recorded as not reproduced; every image recheck stays mandatory under design Q28=A).
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

Yes. Step 2 has been fully implemented.

The shared readers and the read-only observation boundary exist. Reviewer round 2 confirmed that orphan evidence is classified under the observation lock and that lock entry, acquisition and exit failures become damaged results; the remaining read-accounting gap is repaired: the observer's exact exchange paths record each read where its bytes are consumed, before decoding or parsing, so malformed envelopes, coordination records and undecodable transcripts stay in the damaged snapshot's account. Tests compare whole checkout trees before and after every read, make every home preparation, migration, review-core construction and filesystem mutation fail, and check every read account against an independent recorder, on success and on rejection.

Independent reviewer round 3 confirms the read-accounting repair and its three rejected-evidence regression cases. No carried finding remains. The current resolver still selects `ghog day --full=speed --whole-suite`; the requestor reports 6467 passing tests and 100% line coverage over `tools`. The reviewer assessed coverage statically and did not repeat the walk.

### Goal for Step 2

Provide strict shared inputs and a pure exact-exchange observation boundary.

### Step 2 improvement expectations

- A canonical checkout snapshot distinguishes unused, used, malformed and unresolved inputs without creating directories or claiming roles.
- Read-only tests establish zero prompt/receipt/journal/review/authorization writes. Compatibility fixtures preserve prompt heading, Session role, and exact Prompt/SHA-256/Project root receipt grammar without importing senv.
- Unknown routing fields preserve the pause and produce unresolved-target skips; contradictory JSON/table data produces an error. Both outcomes have explicit tests.

### What was implemented for Step 2

The step delivers four read-only modules, the legacy routing study and one unit-test leaf per module.

- **Shared values**: `tools/resume_paused_models.py` defines canonical Windows checkout roots (case, separator, repeated or trailing separator and extended-prefix spellings share one key; dot segments, trailing dots or spaces and reserved characters fail), prompt digests, agent ids, full pane UUIDs, offset timestamps and single-line text, which also refuses the U+2028 and U+2029 separators that would split a JSON or table line.
- **Routing schema**: `tools/resume_paused_routing.py` defines schema `resume-paused-routing` version 1 with pause identity, observation, resumed, requestor and reviewer targets and the exact exchange. A part may be `{"unknown": reason}` (unresolved, pause kept) or, for a pair slot or the exchange, `{"not_applicable": reason}`. Unrecognized keys, wrong types, other versions, pair applicability, slot roles, foreign checkouts, one pane assigned to two targets and a resumed target differing from its pair slot are errors. The exchange derives its complete identity from the reviewed document and leaves the current round to live state.
- **Artifact readers**: `tools/resume_paused_artifacts.py` loads the home through `ReviewArtifactConfiguration.load`, validates the existing ignore bytes without creating anything, reads the prompt's exact bytes and the receipt, and returns a `CheckoutSnapshot` with the resume-session state (no saved prompt, unused, new since use, used, error), the exact paths read and their byte account. Receipts of schemas 1, 2 and 3 parse; schema 3 adds `Launch id`, `Receiving pane` and `Assignment binding`. Routing is read only from one top-level fenced block opened by `` ```json resume-paused-routing ``; the readable table is rendered from that object and must equal the rendering when present; a legacy table beside the JSON, two blocks, two tables or a header contradiction is an error, and table-only or routing-free prompts are classified for a bulk skip.
- **Exact-exchange observation**: `tools/resume_paused_review.py` rebuilds the saved context, derives the exact paths, takes the nonblocking `observe_transition` lock first and classifies through `ReviewExchangeObserver` and `current_request_occurrence`, without `ReviewExchangeCore`, preparation or migration; the caller supplies the review configuration, loaded once per checkout as the status collector does. Only an empty artifact set is not live. A held lock is busy with or without a coordination record, and so is a record changing between the two probes; an orphan request or answer keeps its abandoned state and an orphan tombstone its interrupted state; another occurrence, an earlier round, or another document, umbrella or step is a changed selection; unreadable, invalid or inconsistent evidence and any lock entry, acquisition or exit failure are damaged. An observed snapshot carries state, round, occurrence, owner, next actor, ownership generation and role natures, never the token digest. The reused store reads through accounted exact paths, a `Path` subclass that records the consumed bytes at the read and decodes text from those bytes without a second read, so the snapshot reports every exact path in order with its bytes, including reads that parsing then rejects.
- **Legacy routing study**: `docs/v0.14.0/resume-paused.legacy-routing-study.md` explains why the prose table cannot be read as routing, the digest and used-receipt hazards of any rewrite, the manual resume and fresh pause path, and the preconditions a separate converter would need; no converter is implemented.
- **Installed launcher grammar**: a local replay of the launcher's heading and field readers, copied without importing senv, reads the same author, title and `Session role` from a prompt carrying routing, and the same `Prompt`, `SHA-256` and `Project root` values from a schema 3 receipt.
- **Deviations from the planned file list**: the first models module (653 lines) and test module (732) exceeded the 650-line ceiling, so the routing schema moved to the new `tools/resume_paused_routing.py`, and the tests were split into `tests/unit/tools/test_resume_paused_artifacts/`, `test_resume_paused_models/`, `test_resume_paused_routing/` and `test_resume_paused_review/` after the module they test. `tests/memory_filesystem.py` registers the artifact and review leaves with the memory-backed scratch filesystem. Under the user's exception of 2026-11-18, twelve bare `__init__.py` path lines of the committed code-review transcript were wrapped in code spans to clear `MD050`, the only change to that transcript.
- **Read accounting**: the checkout snapshot's exact reads and bytes start with the `.review-artifacts.ini` declaration that the configuration load reads, both when the home resolves and when the declaration is refused. An independent recorder of `Path` reads confirms every account: a custom-home snapshot reads the declaration, the ignore file and the prompt; a populated exchange reads the coordination record four times (two stability probes, the adapter's own read and the observer's), then the request and the transcript; a malformed orphan answer, a malformed coordination record and an undecodable transcript each stay in the damaged account.
- **Validation evidence**: `ghog single` on the four leaves exit 0 after the round 2 repairs; contract inspection of the four modules (with the Grep tool, `rg` being unavailable in the shell) found no preparation, migration, core, write, claim, token-digest, process or TUIOS call; each review request is validated by `ghog day --full=speed --whole-suite` (6464 tests, coverage 100%, no outlier or exclusion before round 2), and the repaired tree is validated by the same walk before the round 3 request.

### New types or classes introduced for Step 2

- `ArtifactError`, `SessionRole`, `CanonicalRoot`, `PromptDigest`: shared values.
- `Unresolved`, `NotApplicable`, `PaneIdentity`, `RoutingTarget`, `SavedExchange`, `PauseIdentity`, `RoutingObservation`, `PairSlot`, `SavedRouting`: routing schema.
- `PromptState`, `RoutingState`, `PromptMetadata`, `RoutingReading`, `UsageReceipt`, `CheckoutSnapshot`: artifact readings.
- `ExchangeObservationKind`, `ExchangeSnapshot`: exact-exchange observation.

### Architecture check for Step 2

- **Pure values and schema**: `resume_paused_models` and `resume_paused_routing` perform no IO; they import only the shared host vocabulary, the review identity model and its timestamp validator.
- **Read adapters**: `resume_paused_artifacts` is the filesystem adapter over the pure parsers, and `resume_paused_review` follows the existing `review_status` read pattern: exact paths, the observation lock and the observer, with the review configuration supplied by the caller. Its accounted path type only records and decodes whole-file reads of the exact exchange paths it hands to the unchanged store.
- **Import direction**: models, then routing, then artifacts; the review adapter imports the routing type for annotations only. No cycle, and no module imports TUIOS, a process API or a writing path.
- **File size**: all files are below the 650-line ceiling after the responsibility split; `resume_paused_artifacts.py` has 578 lines and `resume_paused_review.py` 346.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 2

- **No new `O(n^2)` or `O(n log n)` path**: prompt and receipt parsing are single passes over their lines; the fence scan visits each line once; the table comparison is linear in its rows; target consistency uses one map keyed by pane UUID.
- **Read cost**: one checkout reads at most the declaration, the ignore file, the prompt and the receipt, each once. One observation reads the coordination record four times (two stability probes, the adapter's own read and the observer's), each present request, answer or tombstone once, and the transcript once when a round is known. Every observation, successful or damaged, returns these paths in order with the bytes each read consumed; text is decoded from those bytes, so accounting adds no read. The independent recorder checks success and rejection paths.
- **No cache**: nothing mutable is retained between calls; each call reads fresh evidence.
- **Plan-bound alignment**: within the plan's evidence-proportional bound for exact-path reads.

The step stays inside the plan's complexity target. No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 2

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`), line coverage; all four modules are inside it. The statements below are a static assessment of each leaf against its module; the `--full=speed` walk measured 100% before rounds 1 and 2 and measures the repaired tree again before round 3.

- **`tools/resume_paused_models.py`**: every line is exercised by `test_resume_paused_models`, including UNC, extended and drive spellings, every rejection and both digest forms.
- **`tools/resume_paused_routing.py`**: every line is exercised by `test_resume_paused_routing`: each contradiction and malformed form, explicit unknowns and not-applicable parts, a non-pair resumed target, exchange identity and rejections, and exhaustive missing-key, wrong-type and added-key cases.
- **`tools/resume_paused_artifacts.py`**: every line is exercised by `test_resume_paused_artifacts`: each prompt and receipt failure, homes, declaration accounting on success and refusal, routing states, rendering of unknown and absent parts, the launcher grammar, duplicate keys and generated round trips.
- **`tools/resume_paused_review.py`**: every line is exercised by `test_resume_paused_review`: a populated exchange with its complete read account, genuine absence, orphan request and tombstone, a malformed orphan answer, a held lock with and without a record, a changing record, lock entry, acquisition and exit failures, both changed-selection forms, another step, damaged evidence, and recorder-checked read accounts for a malformed orphan answer, a malformed coordination record and an undecodable transcript.

No, there is no unit-tested class below 100% that needs completing for Step 2.

### Feature integrity for Step 2

- **Existing feature behavior**: no existing production module changed; the new modules have no caller yet.
- **Reporting or diagnostics**: unchanged; the review transcript repair touches only twelve list lines, and `MD050` no longer fails the Markdown gate.
- **Compatibility note**: prompts and receipts keep the grammar the installed launcher parses. The memory-backed scratch filesystem now also serves the two new leaves; other scenarios are unchanged.

No existing feature or reporting capability appears impaired.

## Step 3. Emit JSON routing at pause and align manual artifact readers

### Analysis of Step 3 implementation state

Yes. Step 3 has been fully implemented.

The routing capture, JSON/table contract, replacement guard, receipt template and status/list readers are implemented. After code review round 1, pause's own check of the existing prompt's receipt also accepts schemas 1 to 3, as status-session does, instead of relying only on the schema 1/2 resume state table. The contract tests pin that reader with used, new-since-use and malformed schema 3 receipts. The resume command's own schema 3 reader and writer remain assigned to Step 4.

### Goal for Step 3

Make newly paused sessions carry complete machine-readable assignments while retaining manual and installed-launcher readability.

### Step 3 improvement expectations

- Historical authorship and intended assignments remain separate; unresolved targets are explicit and never guessed.
- New pause examples parse under Step 2, readable tables derive from JSON, and legacy fixtures remain valid. `pause-session`, `status-session` and `list-session` describe schema-3 compatible readers; `resume-session` gains its schema-3 reader and writer in Step 4.
- Contract tests cover requirement Q29=A and acceptance criterion 14: differing known pane or role guards replacement, unknown values alone do not, legacy agent-id comparison survives, and declining preserves the old checkpoint. Capture contacts no counterpart and never launches the bulk CLI.

### What was implemented for Step 3

The step changes seven canonical session documents and adds one contract-test leaf; no production Python module changed.

- **Routing capture**: `instructions/pause-session.md` takes pane identities from the `tuios list-agents --all-sessions --json` records: the full 36-character `window_id`, the `session` string, the `name` label and a non-empty `agent_session_id`. It keeps historical authorship and the saved role apart from intended assignments, and has a session holding a live exchange role save `requestor` or `reviewer`. Missing evidence becomes `{"unknown": "<reason>"}`, a single-agent pause writes `{"not_applicable": "<reason>"}` for both pair slots and the exchange, and the instruction forbids a routing question, contacting the counterpart and launching `resume_paused`.
- **JSON block and table**: the new subsections specify the exact fence line, every key of schema `resume-paused-routing` version 1, the pairing, checkout-spelling and single-line rules, and the thirteen table rows, with one code span per accepted cell form and the `none` and `not applicable` substitutions. A worked paired code-review example is embedded verbatim from the Step 2 renderer. A second block or table, or a cell that differs from the rendering, is documented as a bulk routing error that leaves manual resume intact.
- **Replacement guard**: a decision table asks before replacing an unused or new prompt when its agent id differs or is missing, or when its known pausing pane (full UUID and session string, never the label) or saved role differs, even with the same agent id. The old prompt's pane and role come from its routing block, or for a legacy prompt from a `Session role` line holding exactly one role token. Unknown values alone are no difference, legacy prompts keep the agent-id comparison, declining preserves the old checkpoint, and the guard applies at pause time only.
- **Pause receipt reader** (code review round 1): before the guard, pause accepts the existing prompt's receipt in schema 1, 2 or 3, as status-session does, and classifies it by its `Prompt`, `SHA-256` and `Project root` lines, never by its schema; a receipt that misses a line of its schema, carries another one or names another schema is malformed and stops the pause without replacing the prompt.
- **Publishing**: the `- Session role:` line holds the routing's `pause.session_role` token alone, and the read-back checks that the block parses as strict JSON and that each cell equals its rendering.
- **Template**: `templates/pause-session.template.md` replaces the prose routing bullets and the six-column table with the JSON skeleton naming every schema key and the thirteen-row table skeleton; its `Session role` placeholder asks for one token.
- **Receipt template**: `templates/resume-session.template.md` keeps every schema 2 line, writes `Schema` as 2 for a manual resume or 3 for a marked resume, and adds `Launch id`, `Receiving pane` and `Assignment binding` as marked-resume-only lines that a manual resume omits. Its meaning section states that schema 3 only adds non-secret bindings.
- **Status and list readers**: `instructions/status-session.md` accepts receipt schemas 1, 2 and 3 with exactly their own lines and classifies each by `Prompt`, `SHA-256` and `Project root`; it also names an unprocessed prompt's saved routing state (resolved, unresolved, error, table only or none) without deriving routing from a table or checking live panes. `instructions/list-session.md` accepts the same schemas, adds the receiving pane of a schema 3 receipt to its disk check result, and reports an invalid receipt as `cannot check`. The two response templates carry these values.
- **Contract tests**: `tests/unit/tools/test_resume_paused_pause_contract/test_resume_paused_pause_contract_tdd.py` checks the example against the renderer, every rendered cell of five routing variants (paired, single agent, unknowns, bare values, specification) against the documented row forms, the template skeleton's keys and rows, prompts filled from the template (resolved, unresolved and single-agent routing parse under Step 2, a header role contradicting the JSON is an error, prose-table and routing-free legacy prompts stay readable), receipts of schemas 1, 2 and 3 filled from the template, pause's reading of a schema 3 receipt (same bytes used, other bytes new since previous use, a missing or extra line or an unknown schema malformed), the launcher's heading, `Session role`, `Prompt`, `SHA-256` and `Project root` readers, the capture, guard and reader rules, and the six adapters of each session command as canonical redirects.
- **Validation evidence**: the new leaf failed first as expected (50 failures before the documents changed), then `ghog single` on it with the Step 2 artifact and routing leaves and the interactive-menu pointer test passed 347 tests. Grep inspection of the seven documents found `resume_paused` only as a prohibition or the future invocation and no capability, token, real pane id or private path. `ghog day --whole-suite`, the command printed by `pw scope day`, exited 0 after a typing fix in two test helpers. For the round 1 repair, the four new pause receipt rules failed against the earlier instruction and pass after it; the requestor's speed walk validates the repaired tree before round 2.
- **Deviation from the planned file list**: none; every planned file changed and no other tracked file did.

### New types or classes introduced for Step 3

- None. The step adds documentation contracts and test helpers only; it reuses the Step 2 types (`SavedRouting`, `RoutingTarget`, `SavedExchange`, `RoutingState`, `PromptState`) and functions (`parse_prompt`, `parse_receipt`, `parse_routing_json`, `render_routing_section`, `render_routing_table`, `classify_usage`).

### Architecture check for Step 3

- **Workflow policy in root instructions**: the routing, guard and reader rules live in the canonical `instructions` and `templates` files; the provider adapters stay one-line redirects, and a test pins them.
- **Schema in Step 2 modules**: no schema rule is duplicated in code; the tests derive keys, rows and cells from the Step 2 renderer and parsers, so a schema change there fails the documentation contract rather than drifting silently.
- **Test dependencies**: the leaf imports the Step 2 test leaves' launcher replay and routing builders and the production readers; it imports no senv code, no TUIOS client and no process API.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 3

- **No new `O(n^2)` or `O(n log n)` path**: no production code changed. The test helpers scan each shipped file once per call, fold text linearly and match each rendered cell against its row's few documented forms.
- **Read cost**: each shipped document is read once per test session through a cached reader of immutable files; parsing works on in-memory bytes, with no scratch files.
- **Plan-bound alignment**: the documented capture adds one read-only TUIOS listing per pause, already required before this step.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 3

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`). Step 3 changes no file under `tools`, so no class file's coverage moves; the Step 2 modules it exercises keep their own 100% leaves. The staged test module sits outside the gate as test code: every top-level helper, fixture builder and constant it defines is referenced by its tests, and the vulture step of `check.bat` passed.

A green coverage percentage over `tools` cannot establish this Markdown behavior, so the contract leaf pins it directly. Reviewer round 1 found that pause's receipt check was not covered; the guard rules now pin pause's schema 1 to 3 reader, and executable cases check a marked receipt's used, new-since-use and malformed outcomes.

No, there is no unit-tested class below 100% that needs completing for Step 3. No, none of the staged files' top-level symbols is unreferenced.

### Feature integrity for Step 3

- **Existing feature behavior**: manual pause, status, list and resume keep working: legacy prompts with a prose table or no routing still parse, schema 1 and 2 receipts still classify, and a manual resume still writes schema 2. The worktree's `resume-session.md` is unchanged until Step 4, so a schema 3 receipt stops it, which is the documented fail-closed mixed-install behavior.
- **Installed launcher**: the prompt keeps its first-line heading and `- Session role:` line, and every receipt schema keeps the `Prompt`, `SHA-256` and `Project root` lines; the local replay of the launcher's readers proves both.
- **Reporting or diagnostics**: status gains the saved routing state and list the receiving pane of a schema 3 receipt; existing outputs are unchanged otherwise.

A valid schema 3 receipt no longer stops a later pause: its existing-prompt check accepts schemas 1 to 3 independently of Step 4's deferred resume command.

No existing feature or reporting capability appears impaired.

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

- Every Claude reviewer activation outcome and conditional-activation preview carries `limits=claude-wait-scope`, defined in help/reference as the three Q20=A limits plus Q26=A's fourth limit and design Q27=B's fifth limit. Fake-clock takeover tests cover emission and preserve other result/exit semantics; the disclosed clock scope includes Q21=A's undetectable backward changes since boot. Validate Q24=A on initial activation and continuation: only validated requestor review-exchange operations in the Q23-bound file qualify regardless of writer, with validated creation ordering after marked input. Retain all other-work blockers; ambiguous file binding, classification or ordering remains pending. Exercise Step 1's validated Q23=A startup-or-clear binding for the requestor's marked-input file after command-driven and prior manual clear; refresh every condition and reject changed or missing evidence. Keep the reviewer's complete-generation rule and earlier-start lifecycle matching across session files.

Under Q26=A, help/reference name work of roots with no records in Q19's read
set: persistence-disabled roots, other configuration roots, transcripts removed
without detectable evidence and unrecorded work surviving a recorded parent's
validated end. Include the end paths established by Step 1. Injected-ledger
tests on initial activation and later continuation verify that such invisible
work is a disclosed possible duplicate-watcher limit when every other gate
passes. Verify that open recorded parent turns, unmatched starts, partially
recorded work, detected missing history and incomplete reads still block.
Do not infer completion of a recorded start from its parent's termination.

- Design Q27=B: `tools/resume_paused_takeover.py` composes the all-pane idle guard from the Step 5 planner's TUIOS discovery and Step 1's pinned screen profile, and passes it to Step 6's delivery as a pre-send check refreshed under the checkout OS guard. Every live Claude pane of the checkout, the proved requestor included after its Q25=A turn closure, needs fresh validated idle evidence; Q23=A and Q24=A grant no screen exemption, and a busy, unreadable or unknown-layout pane keeps activation pending. `test_resume_paused_takeover_tdd.py` covers a busy non-target pane, a busy requestor pane before its turn closes, a running local command behind a closed-looking transcript, unreadable and unknown screens, a state change between check and send, an all-idle control and later continuation; `test_resume_paused_continuation_tdd.py` exercises the composition end to end, not only the limits string.

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

- CLI help and the reference page define `limits=claude-wait-scope` as all three Q20=A limits plus Q26=A's fourth limit and design Q27=B's fifth limit, with Q21=A's since-boot clock scope. Parser/help tests and `test_resume_paused_cli_safety_tdd.py` verify code presence and meaning on every Claude activation outcome and conditional-activation preview; continuation acceptance covers emission through actual fake activation paths.

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
