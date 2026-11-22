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

The round 6 reviewer confirms the Step 1 code deliverable under plan Q05=A. The repairs of rounds 1 through 5 are present, including R5-1: every proved continuation into a listed file requires its predecessor, and the regression cases cover missing ancestors, foreign, unreadable and incomplete predecessors alongside a complete-history control and the boot boundary. No unresolved code finding remains. The read-only adapters and shared builders are implemented; the writer reports a green whole-suite speed gate with 6166 tests and 100% coverage over `tools`. The reviewer assessed coverage statically and did not repeat the gate. This is not host support: the registry remains empty, every live validation row stays open, and Steps 6 through 8 remain blocked until both hosts have a pinned profile. Since the user's 2026-11-20 amendment of plan Q05, Steps 6 through 8 proceed code-first and only input to a real pane waits for both pinned profiles.

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

Plan Q05=A keeps these rows open without blocking Steps 2 through 5; as amended on 2026-11-20, Steps 6 through 8 also proceed code-first, and no real pane receives input until both hosts have a pinned profile. No row below is validated.

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

Yes. Step 4 has been fully implemented.

The marker, validator, marked claim, receiving instructions and Claude background answer-wait rule are present. After code review round 1, the locked claim verifier also refuses an error checkout snapshot, such as one whose receipt names another checkout, before it uses any parsed field. Regression cases cover the requestor, the reviewer and the validator. Under plan Q05=A the pinned profile registry stays empty and the live-host dependencies remain open with the Step 1 live matrix.

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

- **Answer-wait transport (Q25=A)**: `rules/run_commands.md` gains "Claude requestors wait for answers in the background": every Claude requestor starts each `wait-answer` through a host background mechanism on every requestor route, as one recognized invocation form, ends its turn and resumes from the completion notification; a foreground or moved wait leaves the reviewer pending; Codex keeps its attached wait. The three requestor instructions link to that rule.
- **Marker and binding** (`tools/resume_paused_marker.py`): the marker `<launch_id>.rp1.<pane_uuid>.<role>.<binding>` puts the random launch id first, then the version, the full pane UUID, one of the five role tokens and the SHA-256 binding. It is ASCII, at most 153 characters, and appears once after `--resume-paused`. The binding hashes the canonical UTF-8 JSON (sorted keys, compact separators) of schema `resume-paused-assignment` version 1, holding the checkout key, the prompt SHA-256, the receiver host, session, pane and role, the pair after any swap, and the exact exchange with its occurrence and selected round. `resolve_assignment` rebuilds it from saved routing: a swap is a pair pane given the other pair role, allowed only for a saved requestor pause, and unknown routing, an unrouted pane or a wrong role never resolves. `ResultLine` renders `resume-paused <launch_id> <outcome>[ g<generation>]` in at most 100 characters.
- **Pane and input evidence** (`tools/resume_paused_input.py`): TUIOS discovery and capture run as argument lists; records keep the full `window_id`, the `session` string, `cwd`, harness, program-status apps and agent session id, and host identification uses strong evidence first. `ClaudeInputProver` requires the marked command as the latest typed input of the transcript named by the pane's agent session id, at or after the pause snapshot, in the checkout, under a pinned profile. `CodexInputProver` ties the pane through the pinned screen signatures, then proves the unique session file; later calls re-prove it with the carried session identity and launch id (Q14, Q15).
- **Validator** (`tools/resume_paused_validation.py`, `bin/resume_paused_validate.bat`): marker, saved pause, resolved routing, live exchange observation, binding and host, consumption stage (unconsumed, consumed by this launch's schema 3 receipt, or for a reviewer the requestor's receipt), live pane identity (never an inherited `TUIOS_PANE_ID`) and complete input. It returns typed non-secret JSON with the reasons, the compact failure line and the bytes read, and exits 0 valid, 3 refused, 2 invalid. It writes nothing and caches nothing.
- **Marked claim** (Q03, Q04): `CoordinationRecord.marked_claim` holds the launch id, pane, host, assignment binding, round, occurrence and issued generation, which must equal the record's ownership generation. `OwnershipService.claim(marked=...)` always issues a generation with the binding, any other new claim clears it, and current-owner transitions keep it. The ownership store and exchange store forward it. `claim_selected(marked=...)` runs `tools/resume_paused_claim.py`'s verifier under the transition lock before any backfill: it re-parses the marker, requires the claimed role, the Codex carried identity and launch id, the current prompt, routing and locked round and occurrence, the same exact exchange, the claimant host, the binding and the consuming receipt. Any refusal leaves every artifact unchanged. The claim reads no host session file and needs no TUIOS. `claim` accepts `--resume-paused-marker`, `--carried-session` and `--carried-launch-id`; callers without them keep the manual path.
- **Receiving instructions**: `resume-session.md` accepts `--resume-paused <marker>`, reads receipt schemas 1 to 3 by their `Prompt`, `SHA-256` and `Project root` lines, treats an accepted marker as consent for the author override, validates before the receipt, journal and claim, writes schema 3 only on a marked resume, keeps a written receipt on later refusal and emits the compact result first. `review-resume.md` gains "Continue a marked review role": validator before claim, claim with the marker, no role or consent question, `--override` only for the marker's role conflict.
- **Receiver harness (Q02=A)**: `tests/unit/tools/resume_paused_receiver_test_support.py` declares a checkout with a prepared exchange and routed prompt and runs validate, receipt, validate, journal, validate, claim with the real validator and locked claim, changing evidence before each protected step.
- **Tests**: leaves `test_resume_paused_marker` (tdd and pbt), `test_resume_paused_input`, `test_resume_paused_claims` (binding and claim files), `test_resume_paused_validation` (validator and sequences, launcher smoke, receiver instruction contract) and `test_instruction_structure/test_requestor_answer_wait_transport_tdd.py`.
- **Validation evidence**: each leaf passed in focus; the first regression run caught existing claim callers without the new arguments, fixed by default reads; `ghog day --whole-suite` exited 0 after strict-typing and lint fixes; `ghog day --full=speed --whole-suite` exited 0 with 6768 tests, 100% coverage, no outlier and no exclusion. Grep inspection of the four new modules found no shell command, bulk launcher, token or digest, inherited pane variable, input sending, write, preparation or migration.
- **Deviations from the planned file list**: `tools/resume_paused_input.py` holds the pane and input evidence, separated from the validator by responsibility. Test leaves `test_resume_paused_marker` and `test_resume_paused_input` follow the one-leaf-per-module rule. The claims leaf adds `test_resume_paused_claims_binding_tdd.py` and the validation leaf adds `test_resume_paused_receiver_contract_tdd.py`. `tests/memory_filesystem.py` registers the claims and validation leaves.
- **Error snapshots** (code review round 1): `read_checkout_snapshot` keeps the prompt, routing and receipt it parsed when it rejects a receipt's `Project root`. The marked claim verifier now refuses such an error snapshot as `checkout-unreadable` before rebuilding the assignment, and the shared receipt-consumption checks never read one. Requestor and reviewer regressions validate a good receipt, change only its root, and see the locked claim refused with coordination, transcript, prompt, receipt and generation unchanged. The validator refuses the same receipt.

### Live host dependencies of Step 4

These rows belong to the Step 1 live matrix and stay open under plan Q05=A; they gate profile pinning, so any input to a real pane, not this code.

- [ ] Codex: the pane-tied pre-input version and pinned screen profile of a receiving pane; until a release is pinned, `UnpinnedCodexVersions` reports them unavailable and the validator refuses.
- [ ] Claude: the logged form of the marked slash command in the transcript of each pinned version, which the input proof compares exactly.
- [ ] Claude: the transcript root that holds a pane's agent session (`%USERPROFILE%\.claude\projects` by default) under each launcher configuration.

### New types or classes introduced for Step 4

- `Marker`, `AssignedPane`, `LiveExchange`, `AssignedExchange`, `Assignment`, `ResultLine`: marker and binding values.
- `PaneRecord`, `CarriedIdentity`, `InputEvidence`, `PaneDiscovery`, `PaneCapture`, `InputProver`, `CodexVersions`, `SubprocessRunner`, `TuiosDiscovery`, `ClaudeInputProver`, `UnpinnedCodexVersions`, `CodexInputProver`: pane and input evidence.
- `ValidationRequest`, `ValidationResult`, `ReceiverValidator`, `Validator`, `BuildReader`: receiver validation.
- `MarkedClaimEvidence`, `MarkedClaimBinding`: durable marked claim evidence; `MarkedClaimVerifier`: the verifier type `claim_selected` accepts.
- Test-only: `ReceiverCheckout`, `FakeDiscovery`, `FakeProver`, `ReceiverHarness`, `Step`, `SequenceOutcome`.

### Architecture check for Step 4

- **Pure values**: the marker module performs no IO and depends only on the shared values and routing schema.
- **Ports and adapters**: the validator depends on the `PaneDiscovery`, `InputProver` and evidence-source protocols; TUIOS, subprocess, the filesystem and the Windows build reader stay in adapters composed by `default_validator`.
- **Review core boundary**: the review exchange modules gain only the generic `MarkedClaimEvidence` value and a verifier callable; they import nothing from resume-paused. The CLI adapter wires `tools/resume_paused_claim.py` in, and the claim adapter reaches the core only through `claim_selected`.
- **Import direction**: marker, then input, then claim, then validation; the claim and validator share the receipt-consumption helpers in the claim module. No cycle.
- **File size**: every file is below 650 lines; `tools/review_exchange_store.py` is at 611 in the risk band and changed only by forwarding, as the plan's split guidance asks.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 4

- **No new `O(n^2)` or `O(n log n)` path**: marker and result parsing are single regular-expression matches; discovery is one pass over the agent records; the Claude transcript lookup is one pass over the enumeration and one read; the Codex proof reuses Step 1's single pass over candidate files; the assignment digest hashes a small canonical object.
- **Read cost**: one validation reads the declaration, ignore file, prompt and receipt, the exact exchange paths, one TUIOS listing and the receiving pane's input evidence, and reports the bytes read; a marked claim adds one checkout snapshot read under the lock.
- **No cache**: every validation and claim rereads fresh evidence.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 4

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`), line coverage; the `ghog day --full=speed --whole-suite` walk measured 100%. Each new module has its own leaf: `test_resume_paused_marker`, `test_resume_paused_input`, `test_resume_paused_claims` (also covering the coordination binding and ownership threading) and `test_resume_paused_validation`. The validator's `__main__` guard carries the repository's thin-launcher coverage exclusion. Existing review leaves keep covering the changed review modules.

Line coverage alone missed the error snapshot that retains valid parsed fields; reviewer round 1 found it, and the claims leaf now covers it for both roles, beside the missing prompt, changed digest or routing and another launch.

No, there is no unit-tested class below 100% that needs completing for Step 4. No, none of the staged test files' top-level symbols is unreferenced.

### Feature integrity for Step 4

- **Manual claims and consent**: claims without a marker keep their path, including callers that predate the new arguments; manual resume keeps its author consent and writes schema 2.
- **Review protocol**: role conflicts, fencing, isolation and the existing resume, lifecycle, ownership and CLI regressions pass; records without a marked binding parse as before.
- **Reporting**: claim results and status outputs are unchanged; the validator is a new read-only command.
- **Mixed installs**: an older `resume-session` stops on a schema 3 receipt and older review readers reject the new coordination field, the documented fail-closed behavior until all readers ship together.

The marked claim now refuses every receipt the existing checkout and root rules reject, so its fresh evidence boundary matches the validator's.

No existing feature or reporting capability appears impaired.

## Step 5. Build the read-only checkout planner and duplicate protections

### Analysis of Step 5 implementation state

Yes. Step 5 has been fully implemented.

The read-only planner indexes every discovered pane once, refuses the whole run for a recognized agent caller, failed discovery or an unmatched `--except` or `--switch-roles` name, and gives each prompt-bearing checkout one typed result. Duplicate evidence comes from every pane of the checkout, excluded and caller panes included. Saved targets are validated against live discovery and protected, and the planned markers bind to the rebuilt assignment. After code review rounds 1 to 3, a `review-resume` role is selected only at the head of its arguments, and the other role offered as an alternative keeps it uncertain whatever the punctuation, while an explanatory mention does not; only a strictly later time proves a resume, an undated reviewer-only command never counts for another pause, TUIOS readiness gates an idle pane, and selector names are normalized once per run. Evidence readers that later steps compose stay injected ports with fixed contracts.

### Goal for Step 5

Classify every prompt-bearing checkout and produce deterministic safe preview actions.

### Step 5 improvement expectations

- Preview and execution share the same classified plan, with no guessed target or mutation.
- One planned result per discovered prompt-bearing checkout, including used and skipped prompts; omitted panes are counted. Global validation failures yield no input. Dry-run makes zero transport mutations.
- Test pane-label-only `--except` scope, no pane-label matching by `--switch-roles`, skips for a missing UUID or a target without an agent (including CMD), changed-host classification errors, and ambiguous multiple exchanges with no saved identity. No counterpart input reaches a shell or ambiguous pairing.

### What was implemented for Step 5

- **Discovery and activity** (`tools/resume_paused_evidence.py`): `observe_panes` runs `tuios list-agents --all-sessions --json` once as an argument list and parses, from the same output, the strict pane records and each pane's activity (TUIOS state, `blocked_by`, `draft_held`, `ready`, waiting question). Failed or malformed discovery is a failure, never an empty listing; a repeated pane id gets no activity.
- **Input eligibility**: blocked, question, draft, busy and unknown panes receive nothing, and an idle or done pane whose readiness is negative or absent is not ready. A busy Claude pane skips without any capture; a busy Codex pane gets one injected capture, and only a supported idle empty-input verdict overrides the stale `working` status (requirement Q03), never a blocked status or a draft.
- **Counted commands**: `classify_command` recognizes `resume-session` and `review-resume` after the `/`, `$` or `$llm-shared:` prefix, whatever trailing context or punctuation follows, and reads the role a `review-resume` selects from its marker, or from a role word, `--role <role>` or `as <role>` heading its arguments; a role phrase inside prose selects nothing. The other role offered as an alternative keeps the role uncertain whatever the punctuation: in another selection form anywhere, joined by `or`, `nor`, a slash or a vertical bar on either side (`reviewer (or requestor)`), or listed bare right after the head (`reviewer and requestor`); any other mention of it, such as `as reviewer while the requestor is busy`, is explanatory. `counted` applies Q14/Q26: `resume-session` always counts, a reviewer-only `review-resume` counts only for a saved reviewer pause, and a missing or contradictory role is uncertain.
- **Session journal index**: `read_session_journal` reads the private journal under `USERPROFILE` strictly (UTF-8, known entry headings, offset timestamps cut to microseconds, canonical checkout paths) and indexes resume entries by checkout. A missing journal holds no entry; an unreadable or malformed one is an error, never absence. It never writes the journal and never treats it as prompt authority.
- **Duplicate verdict**: `classify_duplicates` gathers, in pane id order, a resume journal entry strictly later than the pause, counted commands strictly later than the pause and a pane blocked on the author-override question, from every pane of the checkout. Proven older evidence, and a proved reviewer-only command for a non-reviewer pause whatever its time, are ignored; an equal timestamp, an unreadable history, an undated command that could count, an uncertain role or an unreadable journal is reported as uncertain. The planner skips on certain evidence and fails the checkout on uncertainty alone.
- **Code review round 1 repairs**: explicit role selection in place of any role word; the strictly later boundary with equal times uncertain, for journal entries and commands; undated reviewer-only commands ignored for a non-reviewer pause; TUIOS `ready` parsed strictly and required for an idle or done pane, which otherwise skips as `pane-not-ready` while the fresh Codex override of stale working status stays; exclusion and switch names case-folded once per run and shared by every checkout.
- **Code review round 2 repair**: role selection only at the head of the arguments; `/review-resume reviewer or requestor` and `/review-resume after Alex signs in as reviewer` stay uncertain and fail a requestor pause's checkout through duplicate classification, while an explicit reviewer selection followed by ordinary explanatory text still leaves it resumable.
- **Code review round 3 repair**: punctuation no longer decides between an alternative and an explanation; disjunctions, bare lists after the head and second selection forms do. `/review-resume reviewer (or requestor)` fails a requestor pause's checkout without any command, and `/review-resume as reviewer while the requestor is busy` leaves it planned, like the semicolon form.
- **Planner** (`tools/resume_paused_planner.py`): `plan_run` refuses an agent caller (dry run included) and failed discovery before reading any checkout, then requires every `--except` name to equal a session, a complete pane label or a checkout folder name, and every `--switch-roles` name a session or folder name, exactly and case-insensitively. It groups panes by canonical root, reads each discovered checkout's saved pause once, and plans each prompt-bearing checkout in isolation, in root order. An unreadable pause or evidence fails only that checkout; an excluded folder skips it; a switch naming a checkout without a saved requestor pair fails it.
- **Used prompts and later continuation**: a used prompt reports its receipt with the known resumer. Only when a schema 3 receipt shows that the resolved requestor of a saved requestor pair consumed it does the plan hold a conditional reviewer continuation. A receipt from the other pair pane is the expected skip that asks for `--switch-roles`, a mismatch while the switch names the checkout fails it, and any other receipt is an already-used skip.
- **Routing, pauser and targets**: missing, table-only and unknown routing skip, an unknown exchange is reported as ambiguous pairing with no counterpart action, invalid routing fails, and an unsupported pausing agent skips. Each saved target is checked by full pane UUID, TUIOS session, host and checkout. A missing UUID, a saved session absent from discovery, a shell pane without an agent and an unusable pane path skip; a reused UUID, a session reassignment, another host, another checkout or contradictory host evidence fail. A changed label or agent session id is a note.
- **Protections and commands**: the resumed target is protected by exclusion (session or pane label), the caller's own pane and its activity; the counterpart reviewer of a saved requestor pause is protected statically (exclusion, caller pane, shell) and stays conditional on takeover, its activity checked when it is activated. `--switch-roles` swaps only the saved pair's panes. The saved exchange is observed read-only through the injected observer; each planned command is the native resume or review-resume command with a fresh marker bound to the assignment that `resolve_assignment` rebuilds, the resume first, and only the resume carries `--clear`.
- **Plan vocabulary** (`tools/resume_paused_plan_model.py`): request, run-wide refusals, skip and error reasons, actions, checkout plans and the run plan, with its failure verdict and input permission (never in a dry run or after a run-wide refusal). One result per prompt-bearing checkout, used and skipped prompts included; omitted panes are counted.
- **Tests**: leaves `test_resume_paused_evidence` (tdd and pbt), `test_resume_paused_planner` (tdd, pbt and the declared-evidence builder `planner_world.py`) and `test_resume_paused_plan_model`. Properties cover discovery-order invariance of the whole plan, exclusions never lifting duplicate protection, and command classification over prefixes, letter case and trailing context.
- **Validation evidence**: the new leaves passed in focus with `ghog single`; `ghog day --whole-suite` (the selector printed by `pw scope day`, default level) exited 0 after strict-typing, lint, complexity and file-size fixes; the round 1 requestor walk `ghog day --full=speed --whole-suite` exited 0 with 6910 tests, 100% coverage, no outlier and no exclusion, after one uncovered line (the default journal reader) gained its test, and the round 2 and 3 walks with 6928 and 6942 tests on the same terms. Grep inspection of the three new modules found no write, process start other than the injected listing runner, capability, claim or input path, and no bulk launcher exists.
- **Deviations from the planned file list**: the typed plan vocabulary moved to `tools/resume_paused_plan_model.py` when formatting took the planner past 650 lines; the evidence and plan model modules have their own test leaves under the one-leaf-per-module rule, and the planner leaf adds `planner_world.py`. `tests/memory_filesystem.py` registers the evidence leaf, whose default journal reader test reads a scratch file.

### Composition dependencies of Step 5

The planner receives these readers as ports; Step 8 composes the production adapters with the Step 1 and Step 2 readers, and Steps 6 and 7 refresh them before each input.

- [ ] Command history per pane: Claude agent-log prompt lines and Codex screen commands with their times; `None` (unreadable) keeps duplicate protection uncertain.
- [ ] Screen probe for a busy Codex pane: `UNSUPPORTED` while no Codex profile is pinned (plan Q05=A), so no stale-working override applies yet.
- [ ] Exchange observer over `observe_saved_exchange` and snapshot reader over `read_checkout_snapshot`, both read-only.

### New types or classes introduced for Step 5

- `PaneActivity`, `PaneObservation`, `Activity`, `ScreenVerdict`, `Eligibility`, `ScreenProbe`: pane activity and input eligibility.
- `CommandKind`, `ClassifiedCommand`, `ObservedCommand`, `CommandHistory`: counted command evidence.
- `JournalResume`, `JournalIndex`: the session journal index.
- `DuplicateSignal`, `DuplicateEvidence`, `DuplicateVerdict`, `PauseFacts`: checkout-wide duplicate evidence.
- `GlobalReason`, `GlobalFailure`, `SkipReason`, `ErrorReason`, `CheckoutOutcome`, `ActionKind`, `PlanRequest`, `PlannedAction`, `CheckoutPlan`, `RunPlan`: the plan vocabulary.
- `ExchangeObserver`, `PlannerPorts`: the planner's ports.
- Test-only: `World`, `FakeHistory`, `FakeProbe`, `FakeExchanges` and the typed world-change builders.

### Architecture check for Step 5

- **Pure model**: the plan model holds values only and imports other modules for typing alone.
- **Ports and adapters**: the planner depends on injected ports for snapshots, exchanges, command histories, screen captures, the journal and launch ids; the only concrete readers are the argument-list listing runner and the journal reader in the evidence module, both read-only.
- **Separation**: duplicate evidence and eligibility classification sit in the evidence module, routing resolution and target validation in the planner, as the plan's split guidance asks; argument parsing stays for Step 8.
- **Import direction**: models, routing, artifacts, marker and input, then evidence, then plan model, then planner. No cycle, and no review-core import beyond the exchange observation snapshot type.
- **File size**: planner 543 and plan model 194 lines are below the 550 safe-to-extend band; evidence is 580 lines, in the 550 to 650 band and below the ceiling, holding one responsibility (duplicate evidence and input eligibility) whose docstring carries the review fixes.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 5

- **No new `O(n^2)` or `O(n log n)` path over panes**: one pass builds the UUID and root maps; each saved target is one map lookup; exclusion and switch names are case-folded once per run into sets that every checkout shares, then looked up. Sorting the checkout roots, and the panes of one checkout for deterministic evidence order, is `O(C log C)` and `O(p log p)` over small per-run sets, which the plan's map-based bound tolerates.
- **Read cost**: one listing, one snapshot read per discovered checkout, one exchange observation per paired or reviewer checkout reaching its targets, and the journal once; a capture happens only for a busy Codex resume target.
- **No cache**: plans are rebuilt from fresh evidence on every run; Step 6 revalidates before each input.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 5

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`), line coverage; every requestor speed walk so far measured 100%, and the replacement round's walk measures the latest repairs. Each new module has its own leaf designed to reach 100%: `test_resume_paused_evidence` exercises every eligibility, classification, journal and duplicate branch with declared inputs; `test_resume_paused_planner` reaches every refusal, skip and error of the planner, including a raising snapshot reader; `test_resume_paused_plan_model` covers the run verdict and request defaults.

Behavior cases now include head selections beside explanatory mentions of the other role with varied punctuation (semicolon, comma, plain clause, parenthesis) and alternatives with varied punctuation (`or`, `nor`, slash, bar, parenthesized `or`, `and`, comma, semicolon, bare parenthesis) in unit and property tests, the parenthesized alternative and the plain explanatory clause through duplicate classification and the requestor checkout, the restored `reviewer or requestor` regression and its variants, a role phrase embedded in prose (`after Alex signs in as reviewer`) and a second selection of the other role, both through duplicate classification and the planner for a requestor pause, the same undated reviewer command for each pause role, earlier, equal and later times for journal entries and commands, and idle or done panes with negative or absent readiness through discovery and planning.

No, there is no unit-tested class below 100% that needs completing for Step 5.

### Feature integrity for Step 5

- **Existing readers**: snapshot, routing, marker, discovery and exchange observation modules are only imported, unchanged; the validator, claim and receiving instructions keep their behavior.
- **Manual workflows**: nothing changes for manual `resume-session` or `review-resume`; the planner writes no receipt, journal or claim.
- **Reporting**: no existing output changes; the plan is a new in-memory result for the later report.

No existing feature or reporting capability appears impaired.

## Step 6. Deliver guarded pane actions with bounded acceptance

### Analysis of Step 6 implementation state

Yes. Step 6 has been fully implemented.

The guarded delivery executes a Step 5 plan under a nonblocking per-checkout OS guard, one safe action at a time per checkout and independent checkouts concurrently. Every clear, resume, reviewer command and recovery Enter is preceded, under the held guard, by fresh identity, protection, eligibility, selector, injected and profile checks. Each send has its own fixed 100-second fake-clock budget, enforced at every step: each blocking transport call is bounded by the time left, each injected check and each nested read of an acceptance proof (version evidence, pane capture, session files, transcripts) starts only while time is left and reads the time left when it starts, and no result completed after the deadline is acted on. Acceptance needs the supported profile and the Step 1 full latest-input proof, and uncertain submission is never retyped. Only Codex may get one recovery Enter, after a proved-empty pre-input capture and identical captures of the exact command as the whole input box with exactly the pinned footer layout below it, the last one taken after the recovery checks. Code review round 1 found six gaps, round 2 two partial repairs and round 3 one remaining deadline gap in chained checks and nested proof reads; all are repaired with regression tests. The user amended plan Q05 on 2026-11-20 so Steps 6 to 8 proceed code-first; the profile registry stays empty, so no real pane receives input, and the production adapters and live host evidence below remain open rows.

### Goal for Step 6

Execute one safe action at a time per checkout while independent checkouts progress concurrently.

### Step 6 improvement expectations

- Every input is freshly eligible and targets exactly one current full pane identity; uncertain submission never causes retyping.
- Injected transport captures exact argv and zero unintended input. Recovery is at most one pane-targeted Enter without retype or deadline reset. No bulk artifact writes or live CLI delivery occur during tests.

### What was implemented for Step 6

- **OS guard** (`tools/resume_paused_guard.py`): `CheckoutGuard.acquire` locks one byte of an empty file named by the SHA-256 of the canonical checkout key, in a folder of the user's temporary directory, without waiting. Another holder makes the checkout an immediate `held` skip; an unopenable file or a temporary folder inside the checkout is `unavailable` and fails the checkout. `GuardLease` releases on every exit of its `with` block, exceptions included, and the OS drops the lock with its handle. The file holds no content and authorizes nothing.
- **Transport** (`tools/resume_paused_transport.py`): `ask_arguments` builds `tuios ask-agent --select 'session:S name:N' --yes --stall-timeout 60000 --timeout 100000 --lines 1 --json -- <command>`, the command one inert argument after `--`; `enter_arguments` builds `tuios send-keys -s S -w <full pane id> Enter`. `selector_value` turns each space of the live session and name into the documented `*` wildcard and refuses any other glob or non-printing character; `resolve_selector` matches more broadly than TUIOS (any letter case, a wildcard crossing any character) and requires exactly the validated UUID among every listed pane, so a collision is an error before input. `TuiosTransport` runs discovery, `select`, captures, the ask and the Enter, each on a runner bounded by the seconds the delivery grants, inheriting the caller environment; the ask's exit code is report-only.
- **Runner bound** (`tools/resume_paused_input.py`): `SubprocessRunner` takes its process bound as a parameter (default 30 seconds), so the delivery's runner factory can bound each call by the remaining budget of its send.
- **Delivery vocabulary and ports** (`tools/resume_paused_delivery_model.py`): send phases, outcomes, refusals with their severity, guard states, reports, the profile, log, transport, guard, sleeper, pre-send check and takeover ports. `UnpinnedProfiles` refuses every pane while no profile is pinned, and `NoTakeover` keeps every conditional reviewer pending until Step 7.
- **Fresh pre-send checks** (`tools/resume_paused_delivery_checks.py`): `target_refusal` requires the planned UUID listed once, in its session, with its host and checkout, not the caller's pane nor an excluded session or label, and eligible as Step 5 decides; before the recovery Enter a stale working status is tolerated while a blocked, draft-holding, not-ready or unknown pane refuses it. `PlanRecheck` replans the checkout through `plan_checkout` from the same fresh observation and requires the same native command and marker identity (pane, role, assignment binding), so a changed prompt digest, routing or exchange, a later duplicate or an uncertain history refuses the send; before the Enter only the target's own activity is read as ready. A reviewer continuation matches a planned reviewer.
- **Single-checkout replan** (`tools/resume_paused_planner.py`): `plan_checkout` plans one checkout from a fresh observation with the same checkout gates, or returns `None` when the checkout has no live pane or no saved prompt.
- **State machine** (`tools/resume_paused_delivery.py`): `deliver_run` delivers nothing for a dry run or a run-wide refusal and runs one worker per planned checkout on a thread pool, at most one input operation per pane. Each worker holds its guard across the protected sequence: the resume first, then each conditional reviewer through the injected takeover, which may deliver it under the same guard with its own checks (the seam for Step 7's all-pane idle guard); a reviewer after an unaccepted resume is never attempted. `--clear` clears only a resume action: a Claude clear logged after the pause with no later prompt is skipped as redundant, otherwise the clear must be confirmed (Claude: a clear event after the send and a ready pane; Codex: one more pinned cleared line than the pre-clear capture, on an empty input box), and an unconfirmed clear fails the action with no resume.
- **Acceptance and deadlines**: each send has its own 100-second budget, recovery included, with backoff from half a second to five seconds that never passes the deadline; the 60-second stall bound belongs to the ask. Acceptance needs the pane's supported profile and the Step 1 input prover's full proof from the send instant, plus, for Claude, the command's prompt event in the agent log. A Codex send needs a pre-input capture whose input box shows only the placeholder (a draft skips, an unreadable layout fails); a Claude send needs a readable agent log. Unproved acceptance at the deadline is an unconfirmed failure, never retyped.
- **Codex recovery Enter**: at most one per send. A capture must show exactly the send's command as the whole input box, once on screen, with exactly the pinned footer layout below it; then the fresh recovery checks (the selector included) and an unchanged profile, then a last identical capture, all before the deadline. An edit, a working, placeholder or draft line, a repeat, a failed capture or check, a changed profile or an expired budget withholds it for good, with a note. A refused Enter is still spent. A background-shell line is reported only.
- **Tests**: leaves `test_resume_paused_guard`, `test_resume_paused_transport` (tdd and pbt), `test_resume_paused_delivery_model`, `test_resume_paused_delivery_checks` and `test_resume_paused_delivery` (tdd for run, guard, Claude, clear and pairs, tdd for Codex recovery and screen readings, and the declared world `delivery_world.py`), plus `test_resume_paused_planner_replan_tdd.py` in the planner leaf and the runner bound in the input leaf. Fake clocks drive every deadline: a stalled ask spending 60 seconds, an ask exhausting the budget, one ending half a second before it, backoff ending exactly at 100 seconds. Deterministic barriers prove concurrent checkouts and the per-pane exclusion.
- **Code review round 1 repairs**: the recovery checks resolve the selector again from their fresh listing (a collision appearing after the ask withholds the Enter, which still names the full UUID). Every blocking transport call of a send gets its remaining budget as its bound (`TuiosTransport` builds one bounded runner per call; the ask gets the whole 100 seconds, later calls at most 30), and a proof, capture or check completing at or after the deadline is never acted on. A footer signature makes the profile account for the whole input box: any other line below the input line, such as a multiline draft, reads as other text, and the last ownership capture now follows the recovery checks. A Codex clear needs one more pinned cleared line than the pre-clear capture. The guard refuses a temporary folder that is the checkout itself, treats only `EACCES` and `EDEADLK` as contention (any other lock or seek error is unavailability of that checkout) and closes its descriptor on every failed acquisition.
- **Code review round 2 repairs**: `DeliveryPorts.provers` holds one prover factory per host, and each acceptance proof uses a prover built for the remaining budget, so a capture the Codex input prover takes is bounded by it (a proof started half a second before the deadline grants its capture half a second). No step starts once the budget is spent: a slow log read starts no proof, a slow listing or check ends the preparation as `deadline-passed`, and the recovery stops before its last capture. `InputScreen.footer_lines` pins the exact footer layout, one line per entry in order, so a repeated, missing or footer-shaped extra line below the input line is unrecognized, for an empty box as for an owned one.
- **Code review round 3 repairs**: the prover factory receives the send's remaining-time callable (`Remaining`) instead of a figure computed before the proof. `tools/resume_paused_budget.py` adds the budget-bounded readers a factory composes the provers from: `BoundedVersions`, `BoundedCapture`, `BoundedSessionStore` and `BoundedTranscriptSource` each read the time left at their own call, read nothing once it is spent, and the capture is bounded by what is left then (a version read spending 0.3 of the last 0.5 seconds leaves the capture 0.2, one spending a second skips it). The injected checks stop before each check once the budget is spent, so a second check never runs after a first one spent it.
- **Validation evidence**: the new leaves passed in focus with `ghog single`; `ghog day --whole-suite` (the selector printed by `pw scope day`, default level) exited 0 after strict-typing and lint fixes and after the dependency refactor of the implementation check, and the requestor's `ghog day --full=speed --whole-suite` walk measures each round. Grep inspection of the five new modules found no shell use, file write other than the empty guard file, bulk launcher or token.
- **Deviations from the planned file list**: the plan names the guard, transport and delivery modules with one delivery leaf. Delivery is split into vocabulary and ports, fresh checks, the state machine and, since round 3, the budget-bounded proof readers (`tools/resume_paused_budget.py`), as its split guidance allows, and each module has its own leaf under the one-leaf-per-module rule. `plan_checkout` joins the planner and the runner bound joins the input module. The plan's two-process guard test runs two independent OS handles in one process, which Windows locks exactly as two processes, because this repository's tests never start a process; the cross-process run stays a live row below. The transport property tests draw each word through one integer over the same alphabet and lengths, with 40 examples as the sibling evidence properties.

### Composition dependencies of Step 6

The delivery receives these adapters as ports; Step 8 composes them, and none may report a supported profile before both hosts are pinned (plan Q05 as amended on 2026-11-20).

- [ ] Profile gate from pane-tied version evidence (Step 1 adapters) with each pinned profile's clear command, background-shell line and Codex input-box signatures; `UnpinnedProfiles` until then.
- [ ] Claude agent-log reader of prompt and clear events in the profile's logged form, `None` when unreadable.
- [ ] Input prover factories: `ClaudeInputProver` and `CodexInputProver` (Step 4) per host, each built per proof from the budget-bounded readers of `tools/resume_paused_budget.py` over the send's remaining-time callable.
- [ ] `PlanRecheck` over `plan_checkout` bound to the run's request and Step 5 readers, plus Step 7's all-pane idle guard on every Claude reviewer send.
- [ ] `TuiosTransport` with a factory of `SubprocessRunner`s bounded by the granted seconds; `CheckoutGuard` with the native lock; a real clock and sleeper.

### Live host dependencies of Step 6

These rows belong with the Step 1 live matrix; synthetic fixtures cannot establish them.

- [ ] Guard contention between two real processes on Windows, and release when an invocation is killed.
- [ ] TUIOS selector globs: letter case, what `*` crosses, and the match set of `--select` for a name holding a wildcard.
- [ ] `ask-agent --json` behavior on a stall, a timeout and a refused pane, against the report-only exit code.
- [ ] Whether TUIOS reports `draft_held` for a pane's own unsubmitted command, which refuses the Codex recovery Enter.
- [ ] Codex input-box, placeholder, working, cleared and exact footer layout signatures and the new-conversation command of each pinned release, including whether a new conversation wipes an earlier cleared line (then a pane cleared before the run fails its clear confirmation, closed); Claude `/clear` and prompt log forms and readiness after a clear.

### New types or classes introduced for Step 6

- `LockPrimitive`, `NativeFileLock`, `GuardLease`, `CheckoutGuard`: the per-checkout OS guard, over the model's `GuardState`.
- `Selection`, `AskOutcome`, `TuiosTransport`: the shell-free transport.
- `GuardState`, `Phase`, `DeliveryOutcome`, `ClearOutcome`, `Refusal`, `ActionReport`, `CheckoutDelivery`, `SendStep`, `InputScreen`, `DeliveryProfile`, `LogKind`, `LogEvent`, `DeliveryPorts`: the delivery vocabulary.
- `PreSendCheck`, `ProfileGate`, `AgentLog`, `Sleeper`, `PaneTransport`, `GuardPort`, `PairDelivery`, `Takeover`, with the defaults `UnpinnedProfiles` and `NoTakeover`: the delivery ports.
- `TargetContext`, `PlanRecheck`: fresh pre-send checks.
- `Remaining`, `ProverFactory`, `BoundedCapture`, `BoundedVersions`, `BoundedSessionStore`, `BoundedTranscriptSource`: the per-proof remaining-time bound and the budget-bounded proof readers.
- `InputLine` and the private state-machine classes `_PaneSlots`, `_Recovery`, `_ActionDelivery`, `_CheckoutWorker`.
- Test-only: `World`, `FakeClock`, `FakeTransport`, `FakeLog`, `LogPort`, `FakeProver`, `FakeProfiles`, `FakeProbe`, `FakeGuard` and the declared-plan builders.

### Architecture check for Step 6

- **Ports and adapters**: the state machine depends only on the delivery model's ports, the fresh checks and the plan model. TUIOS argument lists and selector globs stay in the transport adapter behind `PaneTransport.select`, `ask` and `enter`; the native `msvcrt` lock stays in the guard adapter, which uses the model's `GuardState` and re-exports it. The model imports adapters for typing only.
- **Separation**: OS locking, transport and orchestration are separate modules, as the plan's split guidance asks; vocabulary and fresh checks are split from the state machine. Takeover observation stays for Step 7 behind the `Takeover` seam, argument parsing and reporting for Step 8.
- **Reuse**: the fresh checks reuse Step 5's eligibility and host classification, and `PlanRecheck` reuses the planner instead of duplicating its gates.
- **Import direction**: plan model and delivery model, then checks and guard, then the state machine; transport depends on Step 4 and Step 5 readers only. No cycle.
- **File size**: guard 188, transport 154, delivery model 349, checks 206 and budget readers 106 lines are below the 550 safe-to-extend mark; the delivery state machine is 573 lines after three review rounds, whose fix notes its docstring carries, and the planner 558 after `plan_checkout`, both in the 550 to 650 band and below the ceiling.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 6

- **No new `O(n^2)` or `O(n log n)` path**: each send takes one listing; locating the target, checking the selector and building the activity map are single passes over the panes. A capture is read in single passes: input box, working or placeholder lines below it, command occurrences.
- **Bounded observation**: polling backs off to five seconds within each 100-second budget, so a send makes a bounded number of acceptance reads. Each read costs the evidence it inspects (agent log, input proof, capture), as the plan's evidence-cost section allows, with no cache of mutable evidence.
- **Replanning**: `PlanRecheck` replans one checkout, not the run, before each send.
- **Concurrency**: at most eight checkout workers share one run; the per-pane slot set is a constant-time lock and set operation.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 6

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`), line coverage, so every new module is measured; protocol method bodies compile to no executable line. Each module has its own leaf designed to reach 100%:

- `test_resume_paused_guard`: guard path spellings, acquisition, contention and unavailable lock states, a raising lock attempt, unopenable files, temporary folders in, equal to or beside the checkout or unparsable, release on exceptions and on a failed unlock, and the native lock through two handles, a blocked folder and a seek failure that is not contention.
- `test_resume_paused_transport`: argument lists with metacharacters, every selector-value case, unique, colliding and unresolved selectors, both runners of `TuiosTransport` and its `select`; properties for plain and glob names and arbitrary commands.
- `test_resume_paused_delivery_model`: checkout failure verdicts, the fixed budget and the default ports.
- `test_resume_paused_budget`: each bounded reader with time left (the capture capped at the call bound and bounded by the time left at its own call) and with the budget spent (nothing read).
- `test_resume_paused_delivery_checks`: every identity, protection, eligibility and recovery-readiness refusal, the stale working override, and `PlanRecheck` over the real planner for unchanged plans, a changed digest, a later duplicate, an uncertain history, a removed prompt, busy targets, reviewer continuations and unreadable markers.
- `test_resume_paused_delivery`: run, guard, concurrency, per-pane exclusion, profile, prover and log refusals, Claude acceptance and deadlines, redundant, needed and unconfirmed clears, pairs and the takeover seam; Codex empty-input refusals, recovery used, withheld for every condition (a new selector collision, an edit during the recovery checks, a multiline draft, a repeated or missing footer, a recovery check spending the budget included) and never repeated, the bound granted to every call and to each prover, the concrete Codex prover's capture granted the last half second, a log read or a proof or capture completing after the deadline, Codex clears (an old banner with an unrelated change included) and the pure screen readings.
- The planner leaf covers `plan_checkout`; the input leaf covers the runner bound and its unchanged environment.

No, there is no unit-tested class below 100% that needs completing for Step 6.

### Feature integrity for Step 6

- **Existing readers and planner**: `plan_run` and every Step 5 classification are unchanged; `plan_checkout` adds an entry point over the same checkout planner.
- **Runner**: `SubprocessRunner` keeps its 30-second default, argument list, `shell=False` and inherited environment for every existing caller.
- **Manual workflows and receivers**: nothing changes for manual `resume-session` or `review-resume`, the validator or the claim; delivery writes no receipt, journal, claim or other artifact beyond the empty guard file outside the checkout.
- **Reporting**: no existing output changes; reports are new in-memory results for Step 8.

No existing feature or reporting capability appears impaired.

## Step 7. Confirm takeover and activate only a verified missing reviewer

### Analysis of Step 7 implementation state

Yes. Step 7 has been fully implemented.

The Step 6 `Takeover` seam is implemented by `MarkedTakeover`. Every accepted resume's receiver is observed read-only under its own 120-second fake-clock bound, with backoff from half a second capped at five seconds that never extends the bound, a remaining-time check before every read, and every look re-reading all evidence. Observation binds the saved prompt the plan accepted: an older receipt of that prompt keeps the receiver waiting, and a prompt changed since planning fails, even before any receipt exists. A requestor settles only on its proved takeover: its schema 3 receipt and the exchange's current marked claim agree on launch, pane, host and binding, at the current generation, and the binding rebuilds as the requestor assignment at the claimed round. A conditional reviewer is then decided from fresh evidence on initial activation and later continuation alike. The exact active reviewer is left alone first, and a competing pickup, a missing claim, an unknown wait, a question on the pane, an uncertain earlier delivery or a non-requestor receipt leaves it pending with no input. Positive no-wait evidence is a fresh supported idle, empty-input capture for Codex, and the injected lifecycle-ledger decision over a scope binding the proved requestor's pane and marked input for Claude. The decision is refreshed under the checkout guard immediately before the send, together with the design Q27=B all-pane idle guard. Every Claude reviewer outcome carries `limits=claude-wait-scope`, the worker's own report after an unaccepted requestor included. The amended plan Q05 keeps the profile registry empty, so the result source, the Claude ledger and the Claude screen profile are composition rows for Step 8, and their host signatures are live rows below.

Code review round 1 found six gaps, all repaired: observation now binds the accepted prompt digest, both idle checks refuse a question reported without a blocking reason, the worker's `requestor-not-accepted` report of a Claude reviewer carries the limits, no exchange read starts once the saved-prompt read spent the bound, the guard's budget is checked after the last screen reading, and pane discovery is one linear scan in discovery order. Round 2 found one more: the guard sampled its remaining time twice before a capture, so a budget expiring between the two samples could start a capture with a nonpositive timeout; the time left is now sampled once, immediately before each capture, and bounds that capture.

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

- **Seam extension** (`tools/resume_paused_delivery_model.py`, `tools/resume_paused_delivery.py`): `ReceiverState` and the report fields `receiver` and `generation` record what the observation saw (`claimed`, `consumed`, `completion-unconfirmed`, `failed`); `Takeover.received` is called by `_CheckoutWorker._sequence` for every resume report before any conditional reviewer is decided; `PairDelivery.root` names the guarded checkout and `PairDelivery.digest` the plan's accepted prompt. `NoTakeover.received` returns the report unobserved. `CLAUDE_WAIT_SCOPE` lives in the delivery model, so the worker's own `requestor-not-accepted` report of a Claude reviewer carries it.
- **Durable evidence** (`tools/resume_paused_review.py`, `tools/resume_paused_plan_model.py`, `tools/resume_paused_planner.py`): `ExchangeSnapshot.marked_claim` carries the record's non-secret marked claim binding, never a token or digest; `CheckoutPlan.digest` records the digest of the saved prompt the plan accepted, the new prompt's when an older receipt names other bytes; `marked_command` renders a native marked command with the planner's own spelling, so the requestor's marked input is rebuilt from its receipt.
- **Proofs** (`tools/resume_paused_takeover_proof.py`): `read_pause` reads the saved pause and `read_exchange` its saved exchange, composed by `read_durable`; `consumption` needs the accepted prompt and this launch's schema 3 receipt from the planned host (no receipt, or an older receipt of the accepted prompt, waits; a prompt other than the accepted one fails as replaced, receipt or not; another launch, a removed prompt or an unmarked receipt fails), rebuilding the requestor marker from the receipt for a continuation; `takeover_ready` adds a live exchange whose requestor nature is the requestor's host; `current_claim` requires the marked claim of this launch, pane, host and binding at the current generation, owned by the requestor in the same occurrence, rebuilds the binding as the requestor assignment at the claimed round and names the counterpart, whose recorded nature must agree. A missing claim waits and a superseded or foreign claim blocks: a competing pickup.
- **Reviewer wait** (`tools/resume_paused_reviewer_wait.py`): `reviewer_active` leaves alone a reviewer owning the current generation when its pane agrees (the current marked claim names it, or its latest typed command is a reviewer `review-resume`); `prior_delivery` treats a marked reviewer entry since the receipt, undated or malformed, as an uncertain earlier delivery, never resent; `ReviewerWait.verdict` requires a resting pane (a question refuses it even without a blocking reason), a readable history, then a supported `IDLE_EMPTY` capture for Codex or a `WaitAbsence` decision proving absence for Claude, over a `WaitScope` carrying the receipt time, the proved requestor's pane and its rebuilt marked input (the Q23=A file binding and the Q24=A exception) on both routes. Ledger reasons become `ledger-<code>` notes; `UnprovedAbsence` proves nothing while no ledger profile is pinned.
- **Design Q27=B guard** (`tools/resume_paused_pane_guard.py`): `AllPaneIdleGuard` is the pre-send check of every Claude reviewer send, run by Step 6 on the send's fresh listing under the held guard. Every live Claude pane of the checkout, subdirectories, the requestor and the target included, taken in one linear scan in discovery order, must rest in TUIOS and read idle under the pinned `ClaudeScreens` profile. A busy, blocked, questioning, draft-holding, unreadable or unknown-layout pane, or a Claude pane whose directory cannot be read, keeps activation pending. Captures stay inside the guard's own 30-second budget: the time left is sampled once immediately before each capture and bounds it, so none starts once the budget is spent or with a nonpositive timeout, and the budget is checked again after each capture and each screen reading, so no capture or idle reading completed after it authorizes the send. `UnpinnedClaudeScreens` reads every screen unknown.
- **Takeover** (`tools/resume_paused_takeover.py`): `MarkedTakeover.received` watches one receiver for 120 seconds, checking the bound before the saved-prompt read, between it and the exchange read, and after. A requestor settles `claimed` on its proved takeover and any other receiver `consumed` on its receipt; at the bound a receipt alone stays `consumed` and nothing durable is `completion-unconfirmed`, both successes, an older receipt of the accepted prompt included. A failed result line for this launch, a pane blocked on a question, another launch's receipt, a prompt changed since planning or damaged evidence fails. `MarkedTakeover.reviewer` refuses a reviewer after a non-requestor or failed resume, then decides, bound to the plan's prompt through `Activation.digest`: proofs, leave-alone, current claim, the planned reviewer as the proved counterpart, then the wait verdict. It delivers through `PairDelivery.deliver` with the refreshed decision and the Q27=B guard as pre-send checks; their refusals report pending, before a Codex recovery Enter only the durable takeover is refreshed, and an accepted reviewer is watched until its marked claim is current. `ResultSource` lines (the marker grammar, at most 100 characters) are supplementary and only `failed` acts; `NoResults` reads none.
- **Reviewer marker rebinding**: the delivered reviewer marker keeps the planned launch id but binds the exchange's live occurrence and round, which the reviewer's validator rebuilds, so a requestor that published a new round since planning keeps a valid reviewer marker; a round that moves again before the send stops it pending (`reviewer-binding-changed`), and a planned marker that does not parse fails (`reviewer-marker-unreadable`).
- **Limits**: every Claude reviewer outcome carries `limits=claude-wait-scope`; `preview_notes` gives it to a conditional Claude reviewer preview; `CLAUDE_WAIT_LIMITS` defines the five disclosed limits (`DISCLOSED_LIMITS`): the three Q20=A limits with Q21=A's undetectable backward clock changes since the last OS boot, Q26=A's roots without records including work surviving a recorded parent's end after ordinary exit, kill, `TaskStop` or timeout, and Q27=B's running local command in a Claude root without a TUIOS pane, for Step 8's help and reference.
- **Tests**: leaves `test_resume_paused_takeover_proof`, `test_resume_paused_reviewer_wait`, `test_resume_paused_pane_guard` and `test_resume_paused_takeover` (tdd for observation and for activation, with the declared world `takeover_world.py`), plus cases in the delivery, delivery model and review leaves. Fake clocks drive every bound: backoff filling exactly 120 seconds, a read or a failure read completing after it, a slow capture shrinking the guard's next one. The takeover leaf covers the plan's list: receipt and claim agreement, current generation, competing pickup, normal owner transitions, log eviction, masking and daemon restart, the leave-alone check, a global or restarted Claude watcher and the ledger blockers (open turns, unmatched starts, partial records, missing history, incomplete reads, a changed Q23 binding), unknown waits, an uncertain earlier delivery, an unchanged and a switched continuation, prompt or exchange replacement, and each Q27=B case: a busy non-target pane, a busy requestor, a running local command behind a closed-looking transcript, unreadable and unknown screens, a change between check and send, the all-idle control and the guard on continuation. Two runs go through the real Step 6 delivery. The round 1 regressions add: an older receipt, then a claim, and an older receipt alone at the bound; a prompt changing before any receipt or behind an older one, and a plan that read other bytes; a saved-prompt read spending the bound with zero exchange reads; questions with no blocking reason on the Claude target, a non-target Claude pane and a Codex target, on both routes; the last pane's screen reading spending the guard's budget; the budget expiring between a pane's TUIOS check and its capture, and a sweep over every clock call proving no capture starts with a nonpositive timeout (round 2); discovery order with one capture per pane; the limits on the worker's report after a refused and an unconfirmed requestor; the plan's recorded digest and its hand-off to the takeover.
- **Validation evidence**: the new and changed leaves passed in focus with `ghog single`; `ghog day --whole-suite` (the selector printed by `pw scope day`, default level) exited 0 after strict-typing and lint fixes, then `ghog day --full=speed --whole-suite` before the round 1 request. After the round 1 repairs, and again after the round 2 repair, the changed leaves passed in focus before the whole-suite speed walk recorded in the next request. Grep inspection of the four new modules found no shell use, file write, token or bulk launcher.
- **Deviations from the planned file list**: the plan names `tools/resume_paused_takeover.py` with one leaf. Following its split guidance, the proofs, the reviewer-wait classification and the Q27=B guard are separate modules (`tools/resume_paused_takeover_proof.py`, `tools/resume_paused_reviewer_wait.py`, `tools/resume_paused_pane_guard.py`), each with its own leaf under the one-leaf-per-module rule. The Q27=B unit cases the plan places in `test_resume_paused_takeover_tdd.py` are there, run through the takeover with the real guard, and the guard's own leaf reaches its module. The seam extension changes Step 6's model and worker, the marked claim joins the Step 2 exchange snapshot, and `marked_command` joins the planner. Round 1 adds `CheckoutPlan.digest` to the Step 5 plan model, set by the planner. The Q23=A and Q24=A record classification itself stays in Step 1's ledger; Step 7 passes it the requestor binding and acts on its decision.

### Composition dependencies of Step 7

Step 8 composes these ports; none may prove anything before both hosts are pinned (plan Q05 as amended on 2026-11-20).

- [ ] `ResultSource` per host profile: Claude `turn_end` logged form or the session-id-tied transcript, Codex screen rebuild or the Q14-matched session file, restricted to the result grammar; `NoResults` until then.
- [ ] `WaitAbsence` over `ClaudeLedger`: a `LedgerScope` built from the scope's panes (bound transcript of the reported session id, the pane's Claude process identity rechecked after the read, the fixed boot boundary, Q23=A startup or clear markers, proved continuations, the requestor's marked input); `UnprovedAbsence` until then.
- [ ] `ClaudeScreens` from the pinned Claude screen profile; `UnpinnedClaudeScreens` until then.
- [ ] `ReviewerWait` over the oldest-first command history and the Codex `ScreenProbe` of Step 5; `TakeoverPorts` over the run's clock, sleeper, transport, saved-pause reader and exchange observer; `MarkedTakeover` as `DeliveryPorts.takeover`; `preview_notes` in preview reporting and `CLAUDE_WAIT_LIMITS` in help and reference.

### Live host dependencies of Step 7

These rows belong with the Step 1 live matrix; synthetic fixtures cannot establish them.

- [ ] Claude screen idle signature of each pinned release, rejecting a running local command, a question and a draft.
- [ ] The compact result line's Claude logged form and Codex on-screen rebuild, and the blocked or question state TUIOS reports for a repeated consent question.
- [ ] The Claude ledger profile itself (Step 1 live rows): background start, terminal and notification shapes, Q23=A startup and clear markers, and the Q24=A requestor invocation forms.

### New types or classes introduced for Step 7

- `ReceiverState`: the post-acceptance observation of one receiver, recorded with its generation on `ActionReport`.
- `ProofState`, `Proof`, `Durable`: the pure consumption and takeover proofs over one fresh durable read.
- `WaitScope`, `WaitAbsence`, `UnprovedAbsence`, `WaitVerdict`, `ReviewerWait`: the reviewer-wait classification and its Claude ledger port.
- `ClaudeScreen`, `ClaudeScreens`, `UnpinnedClaudeScreens`, `PaneCapture`, `AllPaneIdleGuard`: the design Q27=B guard and its screen profile port.
- `ResultSource`, `NoResults`, `TakeoverPorts`, `Activation`, `MarkedTakeover` and the private `_Watch`, `_Seen`, `_Gate`, `_Candidate`, `_Recorded`, `_ReviewerGate`: the takeover.
- Test-only: `Declared`, `FakeSnapshots`, `FakeExchanges`, `FakeAbsence`, `FakeScreens`, `FakeResults`, `TakeoverWorld`, `FakePair` and the declared builders.

### Architecture check for Step 7

- **Ports and adapters**: the takeover depends on the delivery model's ports (`PairDelivery`, `PaneTransport`, `PreSendCheck`, `Sleeper`), its own injected ports (`ResultSource`, `WaitAbsence`, `ClaudeScreens`) and pure readers; it reads no file, host log or process itself. Host formats stay behind the ports Step 8 composes.
- **Separation**: proofs are pure functions over values; the reviewer-wait classification and the Q27=B guard are separate modules, as the plan's split guidance allows; observation timing lives in the takeover alone. The takeover delivers only through Step 6's worker, so every normal protection, the clear rule and the per-pane slot still apply.
- **Reuse**: the proof reuses `resolve_assignment` and the Step 2 receipt and exchange readers, the wait reuses Step 5's `classify_command`, `CommandHistory` and `ScreenProbe`, the guard reuses `pane_host` and `CanonicalRoot`, and the takeover reuses the planner's `marked_command`, Step 6's backoff constants and `CALL_BOUND_SECONDS`.
- **Import direction**: plan model, delivery model and readers, then the proof, the wait and the guard, then the takeover; the delivery state machine imports none of them. No cycle.
- **File size**: takeover 549, proof 288, reviewer wait 216 and pane guard 209 lines are below the 550 safe-to-extend mark; the delivery state machine is 595 and the planner 571 lines after the seam, `marked_command` and the plan digest, both in the 550 to 650 band and below the ceiling.

No DDD-Hexagonal violation or adapter smell is visible. No, there is nothing that needs to be addressed.

### Performance check for Step 7

- **No new `O(n^2)` or `O(n log n)` path**: each look locates its pane in one pass over the listing; the Q27=B guard takes the checkout's Claude panes in one linear scan in discovery order, with no sort and no cap on their number, then one capture each, so each refreshed listing costs `O(P + C)` for `P` panes and `C` matching Claude panes; history scans are single passes.
- **Bounded observation**: each receiver gets at most 120 seconds with backoff capped at five, so at most about thirty looks, each costing the evidence it reads (saved pause, exchange record, listing, result lines), as the plan's evidence-cost section allows; nothing mutable is cached.
- **Decision cost**: one decision reads the saved pause, the exchange, the reviewer history and, for Claude, one ledger decision; the pre-send refresh repeats it once under the guard, by design.

No, there is no performance issue that needs to be addressed.

### Unit test coverage check for Step 7

The coverage gate measures `tools` (`pyproject.toml`, `[tool.coverage.run]`), line coverage, so every new module is measured; protocol method bodies compile to no executable line. Each module has its own leaf designed to reach 100%:

- `test_resume_paused_takeover_proof`: the durable read (pair, single, unreadable), the rebuilt marker, every consumption verdict with and without an intended digest, the intended digest through the takeover proofs, every readiness and claim verdict, a reviewer's own receipt, a receipt on an unrouted pane, normal owner transitions and a switched pair.
- `test_resume_paused_reviewer_wait`: leave-alone with and without a marked claim, every prior-delivery case, every resting refusal (a question without a blocking reason included), an unreadable history, the Codex verdicts, the Claude ledger decisions and the default absence port.
- `test_resume_paused_pane_guard`: the all-idle control with subdirectory, other-checkout, look-alike and Codex panes, discovery order with one capture per pane, every resting refusal (a question on the target or another pane included), busy and unknown screens, an unreadable capture, unclassifiable panes inside and outside the check, contradictory host evidence, the budget bound, a capture, a middle reading or the last reading spending the budget, the budget expiring before a capture and the sweep over every clock call, other phases, a Codex reviewer and the unpinned profile.
- `test_resume_paused_takeover`: the observation tdd (every receiver outcome, failure, masked line and bound case, older receipts, prompts changed since planning, the deadline between the two reads) and the activation tdd (every decision refusal, older receipts and changed prompts, questions on both routes, the gate refresh and recovery, rebinding, the Q27=B cases, the reviewer watch, limits, previews, the default result source and two real-delivery runs).
- The delivery, delivery model and review leaves cover the seam call, `root`, `digest`, `NoTakeover.received`, the limits on the worker's report and the marked claim field; the planner leaf covers `marked_command` and the plan's digest.

No, there is no unit-tested class below 100% that needs completing for Step 7.

### Feature integrity for Step 7

- **Delivery**: with `NoTakeover`, every Step 6 outcome is unchanged; reports gain two fields with defaults. The reviewer still goes only through the worker's guarded, checked and slot-protected delivery.
- **Readers and planner**: the exchange snapshot and the checkout plan each add one field with a default; `plan_run`, `plan_checkout`, every plan outcome and every command spelling are unchanged, `marked_command` being the same rendering moved into a function.
- **Manual workflows and receivers**: nothing changes for manual `resume-session` or `review-resume`, the validator or the claim; the takeover writes no receipt, journal, claim or other artifact.
- **Reporting**: no existing output changes; the new report fields, notes and `preview_notes` are inputs to Step 8's reporting.

No existing feature or reporting capability appears impaired.

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
