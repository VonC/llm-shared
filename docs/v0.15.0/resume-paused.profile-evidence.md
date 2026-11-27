# Resume-paused host evidence feasibility

## Step 1 investigation outcome

Step 1 is **incomplete**. Read-only observations on 2026-11-10 and disposable
experiments on 2026-11-12 through 2026-11-14 have not established a supported profile for either
host. This document records the
feasibility stop required by
[Step 1 of the implementation plan](plan.v0.15.0.resume-paused.md#step-1-validate-pane-tied-host-profiles-before-input).
It does not authorize delivery or change a confirmed design decision.

Q25=A adds a Step 1 obligation to validate the Claude requestor background
`wait-answer` start, turn closure, terminal record and notification resumption;
no evidence for that complete transport contract has been collected yet.

The observed environment used TUIOS 0.12.1 with its pure-Go backend. Claude
transcripts reported version 2.1.321. Follow-up kernel-image queries returned
pane-linked release paths naming Codex 0.167.0 in five processes. The reviewer's
2026-11-11 image-identity observations resolve the strict attribution contract
within process metadata; the writer has since reproduced the primitive but
has not validated a complete profile. An observed
version alone does not establish a supported input, result, clearing or
task-state profile. Claude ledger completeness remains unproved.

## Live validation campaign from 2026-11-26

The Step 1 live validation checklist resumed on 2026-11-26. The user chose
the split of work: the implementation agent sends diagnostic input only to
disposable Claude and Codex instances it starts in its own TUIOS session, and
the user performs host-level steps (hibernation, restart, clock steps and a
probe in a human shell). The user then left host auto-update on and asked
that resume-paused work whatever the Claude version, rather than pin one
version: that direction reopens the version-pinned profile model and is not
yet a consolidated design decision. The first runs below are read-only: they
sent no input, changed no setting and read native files only in memory,
retaining counts, versions and shape names.

### Read-only host baseline on 2026-11-26

| Fact | Observed value |
| --- | --- |
| `RtlGetVersion` | status 0, build 26200; update revision 9911 (9711 on 2026-11-12 to 14) |
| Host versions | Claude Code 2.1.332, Codex CLI 0.172.0, TUIOS 0.13.3 with its pure-Go backend |
| Boot-process creation (session 0) | `Registry` first; `System` and `smss.exe` 14.6 s later, 5 ms apart |
| Uptime from `GetTickCount64` | 13.4 days |
| Uptime from `QueryUnbiasedInterruptTime` | 4.95 days shorter: standby and hibernation excluded |
| Current time minus `GetTickCount64` | 2.2 s after `System` creation, 16.8 s after `Registry` creation |
| Fast startup | disabled by system policy (`HiberbootEnabled` 0) |
| Sleep states | S0 low-power idle and hibernation; S1 to S3 and hybrid sleep unavailable |

`GetTickCount64` counted the 4.95 days of standby and hibernation since boot
that `QueryUnbiasedInterruptTime` excludes, so only the former is a
sleep-inclusive uptime candidate. After 13.4 days the computed boot instant
lay after the fixed creation instants, never before them. These are single
observations, not the Q21=A validation: the hibernation, restart and clock-step
runs remain. Fast startup cannot be reproduced on this machine while the
policy holds.

### Read-only Claude transcript census on 2026-11-26

The Step 1 parser read every transcript of the checkout's encoded project
directory and of one encoded sub-directory: 38 files, 148485349 bytes and
52212 records, all accepted, each written by a single Claude version. They span
twelve versions, from 2.1.319 to 2.1.332, within two weeks. The checkout's
encoded name extends the encoded names of two other directories (the home
folder and the main checkout), so a name-prefix rule alone would attribute it
to them; the recorded `cwd` of every record that carries one was the checkout
or a directory inside it.

For the three 2.1.332 transcripts:

- Each generation began with `SessionStart:startup` or `SessionStart:clear`
  `hook_success` as its first timestamped record. Every Stop summary named the
  same single TUIOS handler.
- Non-object tool results came from PowerShell and Bash only with `is_error`
  set and no started task, and from `ToolSearch` once without an error.
- 118 chain tips were tool results, the fan-out shape reported on
  2026-11-13; other tips were one each of `turn_duration`, `local_command`,
  `away_summary` and an in-flight tool call.
- Inputs attached to `turn_duration`, `hook_success`, `compact_boundary`,
  `informational`, `away_summary`, a tool result or another input. Some user
  inputs carry no `origin`; their kinds still need a controlled run.

Every version from 2.1.319 on writes `api-request-blob` records whose message
content repeats `tool_use` blocks of earlier assistant records, and
occasionally a `tool_result` block. Because the record graph collects calls
and results from every record, a real transcript shows `tool-call-duplicate`
for each repeated identifier: 128 in one 2.1.332 transcript, 227 in one
2.1.325 transcript, including the 31-record print-mode control of
2026-11-14. The failure is closed, since the transcript stays pending, but no
real transcript of these versions could prove absence until calls and results
are read only from the record kinds that own them. The synthetic fixtures held
no such record. The user's direction of 2026-11-26 is not to repair this for
each release but to stop depending on host transcript formats, so that any LLM
can resume a session; that direction is not yet a consolidated design
decision.

### Read-only Codex session-root census on 2026-11-26

The configured Codex session root held 810 regular JSONL files, all in
year, month and day partitions, 5836655123 bytes in total, from 38 CLI
versions. Every modification time was a multiple of 100 ns with a sub-second
part. The 21 files of version 0.172.0 ended with a final newline; 18 held one
`session_meta` record and 3 held two, and the input proof rejects a file with
more than one. Their user messages appeared only as `response_item` messages
with role `user`: 170 with one `input_text` block and 18 with two. No
`event_msg` `user_message` record was present. The controlled Codex runs must
show which of these shapes a typed input takes and what a second
`session_meta` means.

## Adapter delivery with an empty profile registry on 2026-11-15

The four Step 1 modules and their tests now exist: profile policy, the
query-only Windows binding, the Codex image and input proofs, and the Claude
transcript ledger. The shipped registry pins no profile, so every real pane
still classifies as unsupported or pending. This delivery changes no support
claim in this document. Delivering code ahead of the remaining live matrix is
plan question Q05; the local-command failure below is design question Q27, and
the cases the agent cannot reproduce are design question Q28. The user
confirmed Q05=A, Q27=B and Q28=A on 2026-11-15. Design exchange 8 reviewed
Q27 and Q28, and on 2026-11-17 the user accepted the clarified Q28 wording and
consolidated both into the design; plan review exchange 2 reviewed plan Q05,
and the user consolidated it into the plan's implementation decisions that
day.
Q27=B adds a fifth disclosed limit, for a running local command whose input is
not yet recorded, and a guard requiring every live Claude pane of the
checkout, the proved requestor included, to be freshly idle. Q28=A records the
cases below as designed fail-closed, not reproduced: that label is not
evidence, and an activation that needs an unresolved predicate stays pending.
Sections dated before 2026-11-17 describe four limits as they stood then.

One new runtime observation comes from the unit suite on Windows build 26200.
The binding inspects the test process itself with `PROCESS_QUERY_INFORMATION`
only. Its allocation walk completed and mapped the native image name to
exactly one committed image allocation. The image file, opened through the
`\\?\GLOBALROOT` prefix for read and execute, returned `STATUS_SUCCESS` from
class 44, and hashing through that same handle matched a separate shared read
of the file. Invalid handles and missing paths returned no evidence. This
confirms the binding against one more image on this build; it is not a Codex
pane validation and pins nothing.

The synthetic fixtures encode the record shapes observed above. They test
that the code applies the designed rules; they do not show that a host
provides the evidence. The Claude ledger takes its closed-world sets (record,
attachment and tool names, Stop handlers, allowed leaf and input-parent
shapes) from a profile object that validation must supply.

## Recorded local-command ordering failure on 2026-11-14

After Q26 consolidation, an owned disposable interactive Claude 2.1.325
session executed a local shell command before its input appeared in its
existing native transcript. This fails Step 1's input-before-effect contract
for a root contributing records. Q26's exception for roots with no records
does not cover this case. Both host profiles remain unsupported.

The diagnostic used a new detached TUIOS session and the existing launcher
settings. After an initial model turn ended, local shell mode (`!`) ran a
PowerShell inspection script. While executing, that script read its own
complete transcript, saved only structural facts, then waited three seconds.
The transcript observations were:

| Observation | Local time (UTC+01:00) | Bytes | Records | Local-command input present |
| --- | --- | --- | --- | --- |
| Before local input | 23:39:11.100 | 414265 | 46 | No |
| Inside the executing command | 23:39:34.228 | 414265 | 46 | No |
| After the command returned | 23:39:44.559 | 423490 | 54 | Yes, one record |
| After Claude exited | 23:41:57.848 | 426962 | 60 | Yes, one record |

Every read ended with a complete final newline. Before and during execution,
the transcript ended with the initial turn's `stop_hook_summary` and linked
`turn_duration`. The later local-command input was record 49, a `user` record
with string content linked to that earlier `turn_duration`; record 50 was
the local result. The input's stored timestamp preceded the during-command
observation, but the record was absent from that observation. A timestamp
assigned before execution does not prove that the record was persisted then.

The probe establishes an ordering failure, not an actual unsafe activation.
It did not validate pane guards, other roots, local-command completion
semantics, or background mechanisms. It installed no hook or evidence source,
contacted no reviewer and sent no input to existing panes. The owned Claude
process exited, its TUIOS session was removed, and the owned shell and Claude
processes and their direct children were absent at cleanup. Structural
evidence and diagnostic scripts remain in the private Step 1 artifact home;
no native transcript, screen capture or tool payload was copied there.

### Design return required by local-command persistence ordering

The approved transcript source cannot distinguish this executing command
from the preceding completed turn during the observed gap. Rejecting a
local-command record after it appears cannot close that gap. Further parsing
cannot satisfy the unchanged input-before-effect obligation for this version.

A concrete proposal for design assessment is an additional disclosed limit
for local commands whose input is not yet persisted, including work they
start during that gap. Adopting it would explicitly weaken the ordering
contract and accept possible activation while such work is running. It must
retain blocking for recorded open work and require separate validation of
local-command completion; Q26 alone does not authorize that change.

If that risk is unacceptable, support requires a specifically named,
independently validated source that observes local execution before effects,
or an enforced execution restriction covering every relevant root. Neither
has been established by this probe; a user instruction to avoid local shell
mode is not enforcement. No option is selected here. Step 1 remains
incomplete, adapter implementation has not started, and the validation plan
is unchanged. Q01-Q26 remain as confirmed; no new review was opened.

The user later selected
[Q27=B](design.v0.15.0.resume-paused.md#design-decisions-for-resume-paused)
on 2026-11-15, consolidated on 2026-11-17: the proposal above becomes the
fifth disclosed limit, combined with an all-pane idle guard whose signature
must reject a running local command. Recorded open work still blocks, and
local-command completion still needs its own validation.

## Persistence-disabled Claude counterexample on 2026-11-14

Claude 2.1.325 executed both foreground and host-managed background work with
`--print --no-session-persistence`. A new session created no transcript; a
resume of an existing session left its saved transcript unchanged. This is a
counterexample to the required complete transcript ledger, including Q20's
host-managed waiting scope. Q24's operation exception and Q25's background
transport do not supply evidence for work absent from the ledger.

These were owned, bounded print-mode diagnostics in the checkout, using the
existing explicit launcher settings and only the PowerShell tool. No existing
pane received input or task control. No hook was installed, no reviewer was
contacted and the bulk command was not invoked. The runs did not validate
pane identity or a production task-observation channel. Native `RtlGetVersion`
returned Windows build 26200 with status zero; update revision was 9711.

The command forms were `claude --print --session-id <new-id>` for the control,
the same form plus `--no-session-persistence` for a new session, and
`claude --print --resume <control-id> --no-session-persistence` for the two
resume cases. All used `--output-format stream-json --verbose`, the existing
`--settings <launcher-settings>`, `--strict-mcp-config`, `--tools PowerShell`,
`--allowedTools PowerShell` and `--permission-mode dontAsk`. A bounded system
prompt and diagnostic input restricted each run to one private inspection
script. The script recorded only structural evidence and returned; the
background variant also waited 15 seconds. No permission bypass was used.

| Case | Complete run seconds | Tool executed | Own input/call persisted when tool ran | Transcript result |
| --- | --- | --- | --- | --- |
| Normal persisted control | 28.548 | Yes | Both | One new file; final 31 records, 73549 bytes |
| New session, persistence disabled | 34.452 | Yes | Neither | No session file; no existing file changed |
| Resume saved control, persistence disabled | 36.264 | Yes | Neither | Saved control unchanged |
| Resume with explicit background tool, persistence disabled | 42.795 | Yes | Neither | Saved control unchanged |

All four CLI runs exited zero. The normal control contained one
`stop_hook_summary` and ended with a `cost-state` record. This is an observed
print-mode shape, not a validated universal closing-record contract. During
both resume cases the inspector read the same 31-record, 73549-byte file,
with a final newline and no input or tool call for the new diagnostic turn.

The final case used exactly the requested PowerShell command with
`run_in_background=true`. Its live JSON event stream contained
`system/task_started` with `task_type=local_bash`, then
`system/task_notification` with `status=completed`, matching both task id and
tool-use id. A successful model result preceded the completion notification;
another initialization and successful result followed it. The final stream
was parsed in memory. Only event kinds, matching identifiers, flags, counts
and timings were saved privately, never conversation or tool payloads. These
stream events establish that the bounded task ran; they are not an approved
production evidence source and do not validate Q25's full `wait-answer` route.

The final audit read all 13 regular JSONL files under this checkout's encoded
Claude project directory, including nested files: 41570735 bytes, all ending
with a newline. Only the control marker appeared, in one file. None of the
three persistence-disabled diagnostic input markers appeared. This complete
content scan supplements the before/after metadata checks; the negative
finding does not depend only on modification times. It is a bounded diagnostic
audit, not validation of Q19's full checkout/subdirectory discovery contract.
The background task completed, all four CLI executions returned, and no
Claude or PowerShell process created during the diagnostic interval remained
at cleanup. Native host transcripts were not copied into artifacts.

### Design return required by the persistence counterexample

Step 1 requires roots without session persistence to return to design review.
The tested root can resume a saved session and start an in-scope background
task without adding an input, open turn, start, or terminal record to that
session's transcript. More transcript parsing or stricter closure checks cannot
detect the missing work. This finding leaves both profiles unsupported and
later implementation steps blocked; no supported adapter or profile test was
created and no validation-plan implementation status was changed.

A concrete candidate source for design assessment is Claude's print-mode
`--output-format stream-json` task lifecycle feed, whose start and completion
events were observed here even when session persistence was disabled. Using
it for affirmative absence would require a managed launch boundary covering
every relevant root, durable lifecycle history across root exit and restart,
and proof that unmanaged roots and surviving work cannot escape that boundary.
A stream from one root, an instruction to avoid the flag, or a launcher
default is insufficient. This candidate would reopen the current evidence,
launcher-integration and persisted-artifact boundaries; it is not selected,
installed, implemented or proved complete by this experiment. If those
boundaries remain unchanged, this tested Claude version cannot meet the
current automatic-activation contract. Q01-Q25 remain unchanged.

The user selected
[Q26=A](design.v0.15.0.resume-paused.md#design-decisions-for-resume-paused)
on 2026-11-14. Work of roots with no records in Q19's read set becomes a
fourth disclosed limit, which qualifies the statement above that this tested
version cannot meet the automatic-activation contract. Both plans now carry
the limit and its validation obligations. The reviewer reports that Claude
2.1.325 help describes the stream format as print-only, so it cannot observe
interactive or background sessions. No collector was selected, and the
decision establishes no supported profile.

## Initial read-only observation boundary

The investigation used discovery, pane capture, window details and process
detection commands. It inspected the process identified by a pane's shell
process group and its direct Codex child, then read that executable's Windows
file and product version metadata. Claude transcript paths were derived from
the working directory and session identifier reported for each pane.

Discovery and captures were parsed in memory. Only schema names, versions,
counts and boolean findings were retained. No conversation bodies, task
identifiers, machine paths, pane identifiers or ownership capabilities are
included here. No pane input was sent, no conversation was cleared, and no
background task was enumerated through a live task-management interface,
started, stopped or duplicated. The bulk launcher was never run.

## Disposable validation boundary on 2026-11-12

The implementation agent subsequently created a dedicated detached TUIOS
session for diagnostic Claude and Codex instances, then killed that session.
Only disposable instances received diagnostic input; Claude started bounded
background commands. Existing working and review panes received no
input or task control. Existing launcher settings were reused; no hook or
additional evidence channel was installed. Descendant observations and forced
termination concerned only the owned disposable Claude process tree, never
production discovery. The bulk launcher was not invoked.

The candidate versions were Claude 2.1.322 and Codex 0.167.2. These differ
from the earlier observations and are not supported profiles. Native runtime
build evidence was Windows build 26200; update revision 9711 was recorded.
Private scratch probes retain only allowlisted metadata and sanitized
results. No raw transcript was copied into an artifact.

### Writer-reproduced query-only image results

The disposable Codex process admitted a complete `VirtualQueryEx` walk of
1869 regions, with exactly one matching committed image allocation.
`QueryFullProcessImageNameW` and `GetMappedFileNameW` agreed. The native-path
file handle returned `STATUS_SUCCESS` from class 44; hashing through that
same handle read 368380208 bytes. The exact eight-key layout-1 manifest
agreed on entrypoint, version and release directory. Rechecking the retained
handle and native image name succeeded. The combined probe took 0.386 seconds.
This establishes primitive feasibility for this candidate, rather than a
supported profile. The process was launched directly as a pane root; the
required shell-plus-single-direct-child linkage was not exercised.

A separate disposable copied executable reproduced a unique matching image,
original-handle acceptance and same-handle hashing. A byte-identical copy
returned `STATUS_UNSUCCESSFUL` (`0xC0000001`); read-only file access and limited
process-query rights returned `STATUS_ACCESS_DENIED` (`0xC0000022`). That run
took 0.105 seconds. Directory rename attempts on copied executables returned
Windows error 5. They do not validate renamed-original acceptance, stale
paths, tunneled recreation, replacement, junction retargeting or actual
updater behavior. Races and supported input/result/clear signatures also
remain outstanding.

An additional 0.052-second copied-executable probe renamed the executable
file successfully, retained `STATUS_SUCCESS` for its original handle and
accepted a newly opened handle to that renamed original. An identical file
recreated at the old name returned `STATUS_UNSUCCESSFUL`. After rename the
full image-name/allocation corroboration failed with zero matching
allocations, which must reject the full profile. Directory rename was denied
both before and after opening the candidate file handle. This reproduces
file-identity behavior across a file rename, but does not establish the
remaining directory/updater and race obligations.

### Writer-observed Claude forced-exit continuity

With existing launcher settings and managed integration reported as not
installed, the disposable Claude transcript recorded `SessionStart:startup`
before the first typed user entry. Typed input had `origin.kind` equal to
`human` and `promptSource` equal to `typed`. A 15-second PowerShell background
command produced `toolUseResult.backgroundTaskId`, a terminal
`queue-operation` enqueue with status `completed`, its dequeue, and a user
record with `origin.kind` equal to `task-notification` and `promptSource`
equal to `system`. These are observations of this mechanism, not complete
generation coverage.

A second 120-second PowerShell command recorded its background start. After
forced termination of the disposable Claude process, its owned PowerShell
and console-host descendants immediately survived with unchanged creation
identities. A later complete transcript read contained two background starts
and one terminal notification, with all 87 records parsed and a complete
final newline. All saved descendants were absent at a subsequent check;
their natural completion was not observed. The transcript's unmatched start
cannot establish either present liveness or termination.

This counterexample prevents assuming forced parent exit cleans up all
background work. The consolidated design already requires pending for
unproved continuity or cleanup; this result does not establish that ordinary
same-generation positive absence is impossible. It also does not authorize
a new evidence source. Startup generation binding, the remaining marker-source
checks and complete coverage of every enabled host-managed waiting mechanism remain
unvalidated.

### Writer-observed Monitor and schedule records

A second disposable Claude session used the same existing launcher settings.
Its startup attachment had session, version and timestamp fields, but no
explicit host process id or creation identity. The `session-owner` records
contained account, organization and session fields rather than process
generation. These shapes alone do not validate complete-generation binding.

A bounded `Monitor` watched a disposable signal file. Its successful start
used `toolUseResult.taskId`, `timeoutMs` and `persistent`, rather than the
PowerShell start's `backgroundTaskId`. Creating the signal produced a terminal
enqueue with status `completed`, then dequeue and a system task notification.
The start-to-notification interval was about 43.5 seconds; this includes the
deliberate delay before the signal, not a notification-latency guarantee.
A complete read then parsed 91 records and 562386 bytes with a final newline.
The monitor finished before subsequent probes.

One nonrecurring, session-scoped `CronCreate` probe recorded input keys
`cron`, `prompt`, `recurring` and `durable`. Its result supplied `id`,
`humanSchedule`, `recurring`, `durable` and `nextFireAt`. `CronDelete` then
confirmed cancellation of that exact job before its scheduled time; its
result supplied `id`. A complete read after cancellation parsed 146 records
and 832906 bytes with a final newline. No scheduled wakeup was allowed to
run. This establishes creation/deletion shapes only, not restored-schedule
coverage or positive absence across every enabled mechanism.

A requested foreground sleep was rejected by the diagnostic host before
execution. Foreground-to-background movement therefore remains untested;
the rejected command is not evidence of a lifecycle-contract failure.

### Writer-observed Codex direct-child linkage

A second disposable Codex instance ran as the single direct child of a CMD
pane root. Its idle banner reported 0.167.2 and empty input. The query-only
probe found 1985 regions and one matching image allocation; the native name,
class-44 identity, retained-handle recheck and eight-key layout-1 manifest
agreed. The same-handle hash again read 368380208 bytes and matched the first
probe. This run took 0.369 seconds. It adds an observed direct-child launch
shape without establishing linkage races or the full supported profile.

Read-only [official Codex command documentation](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
describes `/new` as starting a fresh conversation and `/clear` as starting
one while also clearing the visible terminal. Syntax was confirmed from that
source; neither command was tried in an existing working or review pane.
Version-specific clear-result signatures remain unvalidated.

A tool-free diagnostic input produced the requested fixed reply in four
seconds. Enumerating all 719 regular JSONL files across the configured session
root's date partitions yielded one candidate modified since the delivery
boundary. Reading its 151781 bytes found 18 complete records, one
`session_meta`, matching cwd and version 0.167.2, and the exact latest input
as `response_item` with role `user`. No `event_msg/user_message` record was
present. The read was stable and took 0.318 seconds including enumeration.
The native file needed a read-only stream allowing concurrent write/delete
sharing; the default whole-file reader failed on the live writer's sharing.
This identifies an actual input shape, not a supported recovery layout.

That scratch scan used a provisional one-millisecond lower-bound allowance.
Filesystem timestamp resolution, metadata byte accounting, older-partition
activity, duplicate matches and linkage races remain unvalidated. UTC
boundaries must be compared as UTC values; a local-kind PowerShell datetime
conversion initially excluded the live candidate and was corrected before
accepting the scan. No raw session content was persisted by the probe.

## Claude generation experiments on 2026-11-13

The writer created a new detached diagnostic TUIOS session with Claude
2.1.323 and the existing explicit launcher settings. No hook was installed;
existing working and reviewer panes received no input. Native transcripts
were parsed in memory, with only structural facts and byte counts retained.
An initial bypass-mode launch stopped at its first-run consent dialog and
was declined; the successful diagnostic used ordinary permissions.

### Startup and clear observations for Claude 2.1.323

The pane reported its session identity with source `report`. Its shell had
one direct Claude child. The first timestamped transcript record was
`SessionStart:startup` `hook_success`, after that child's creation; six
untimestamped metadata records preceded it. A no-tool turn ended with
`stop_hook_summary` and `turn_duration`. The complete initial read contained
46 records and 392680 bytes, with a final newline. These are observed shapes,
not proof of a universal closure or persistence guarantee.

A bounded background PowerShell sleep returned `backgroundTaskId`. Clearing
while it ran changed the reported session id without replacing the child
process. The new file's first timestamped record was
`SessionStart:clear` `hook_success`. Its subsequently persisted `local_command`
record had an earlier timestamp, confirming that file order is not event
creation order. The task's matching terminal `queue-operation` enqueue,
with status `completed`, arrived in the new file approximately 89 seconds
after the start result in the old file. A following turn ended with the
same two closing system record types. The complete reads contained 60
records and 418279 bytes before the clear boundary and 54 records and
416144 bytes in the new file after completion, both with final newlines.
This supports retaining pre-clear starts and matching terminal records
across files; it does not validate all host-managed waiting mechanisms.

### Concurrent resume counterexample to unconditional single-writer ownership

A second owned pane launched Claude with `--resume` for the first pane's
current session, using the same explicit launcher settings and its
SessionStart hook. The later plain-resume experiment below covers an attach
without those settings.
Both distinct, live direct Claude children reported the
same session id with identity source `report`. The resumed process wrote
`SessionStart:resume` and a diagnostic turn into that same transcript.
After orderly exit of the original child was verified, the resumed child
accepted another no-tool diagnostic input and wrote further records to the
same file. That complete read contained 76 records and 448429 bytes with a
final newline. Both diagnostics were then exited and the owned TUIOS session
was removed after checking cleanup.

Thus a transcript is not unconditionally exclusive to one root process,
and another root can write after the original exits. This contradicts the
literal single-writer requirement in the earlier generation contract.
The later noncompact SessionStart rejection already makes this observed
case pending; the experiment does **not** establish an unsafe acceptance
or defeat that rejection rule. It also does not show that a transcript
without a later marker has multiple writers.

The first independent review requested generation-scoped exclusivity in
design item 1: every record from the accepted first timestamped marker
through the complete read must come from the pane's current direct child.
That contract first relied on a validated attach signature for every
append-capable root. The plain-resume experiment below found an append path
without one, and the later review replaced the signature list with positive
attribution, described in the positive attribution section. The Stop-only run
then showed that no approved source identifies the writer; the not-adopted
checkpoint section records the replacement completeness and closure contract
and design Q24. Confirmed Q24=A replaced the writer condition with validated
operation content and closure; no evidence source was added. Validation status
remains unchanged. Both hosts remain
unsupported; the remaining feasibility matrix, adapters, tests and
implementation gates are still outstanding.

### Plain resume observations without launcher settings

A fresh owned diagnostic used Claude 2.1.323 and the existing explicit
launcher settings for its original process. Its first timestamped record was
`SessionStart:startup`; its no-tool turn ended with `stop_hook_summary` and
`turn_duration`. The complete original-only prefix contained 46 records and
392608 bytes, with a final newline.

A second owned process used plain `--resume` for that session without the
launcher settings while the original child remained alive. Both children
were verified alive. The same native file grew to 52 records and 397816
bytes, ending in a newline. The appended prefix contained two
`file-history-snapshot` records, then the diagnostic user input, `api-request`,
assistant reply and `turn_duration`. No new `SessionStart` or
`stop_hook_summary` appeared. The first snapshot's message id had no matching
user record; the second matched the new input. This establishes that the
SessionStart rule alone does not detect this append path. It does not
establish acceptance by a complete profile.

The plain input carried `isSidechain=false`, `promptSource=typed`,
`origin.kind=human`, `turnOrigin=human`, `entrypoint=cli` and
`userType=external`, with the same session, version and checkout. A subsequent
no-tool control input in the original process carried those same markings
and the same `turnPosition`. The two inputs shared a parent UUID, creating
a visible branch only when the original's next input persisted. That
control turn again ended with `stop_hook_summary` and `turn_duration`. The
complete read then contained 61 records and 416880 bytes with a final newline.
Root-interactive markings alone do not distinguish the observed second root;
a later branch cannot supply detection before that branch exists.

After both earlier children had exited, a third owned process used plain
`--resume` for the same session. Its diagnostic input and reply also appended
without a new `SessionStart` or `stop_hook_summary`, preceded by two snapshots
and followed by `turn_duration`. The complete read contained 75 records and
426101 bytes. Its orderly exit left 84 records and 428453 bytes; both reads
ended in a newline. Every owned Claude child was verified absent before the
diagnostic TUIOS session was removed. The owned experiment ran for about
seven minutes, including startup, controls and cleanup. No task, schedule,
new hook or additional evidence source was used. Only allowlisted structural
facts were retained; conversation and tool payloads remained in memory.

### Historical positive attribution candidate after plain-resume review

The following candidate is superseded history after the Stop-only run and
its independent review. No approved source proves positive writer attribution;
the current design instead requires complete coverage and closure for every
writer. The earlier proposal is preserved here to explain the experiment.

Independent review replaced the initial list of negative rejection checks
with positive closed-world attribution of every record from the accepted
marker to the end of the read. Any later SessionStart other than `compact`,
whatever its hook outcome, means pending. Other records must form one parent
chain except validated tool-call fan-out, subagent sidechains and compaction
boundaries. Every model turn, whatever starts it, must close with its own
linked `stop_hook_summary` whose recorded handlers equal the validated
launcher Stop handler set, followed by the validated final record. Every
snapshot must link to an input in the chain or match a validated
original-process form. Local-command and metadata records need their own
classification. An unattributed record, second input-bearing child, unclosed
or differently closed turn, or unlinked snapshot means pending.

These are unvalidated attribution rules, not proven host guarantees.
Legitimate tool-call fan-out cannot be rejected as arbitrary branching.
Root-interactive markings classify records but do not identify their writer.
Apply the closure condition to the last turn of every in-scope history
transcript as well as the bound file. A later rejection cannot retrospectively
authorize a read that lacked it.

Validate all agreed E1-E3 append paths against ordinary original-process
controls, including snapshot-disabled operation, nested print-mode and roots
whose own explicit settings carry a Stop handler. The latter may match the
launcher Stop summary without producing a SessionStart marker. Determine
whether the recorded command distinguishes the pane's launcher settings
instance. Also validate persistence before effect: a turn's input persists
before it runs any tool or starts any waiting mechanism. An original-turn
and foreign-first-turn diagnostic tool must inspect whether its own input
and tool-use records are already on disk. A lag measurement does not establish
this property. Record where each attach first fails attribution and the
persistence order. An attach that passes, or failed ordering, returns to
design review with a concrete proposal before any new human question.

No new source, hook installation, disclosed limit or human decision is
introduced. Both profiles remain unsupported; no adapter, fixture,
validation status or delivery capability is enabled.

### Reviewer observation of branching and closure on 2026-11-13

The independent reviewer reports a complete read of its own `tuitp`-launched
Claude 2.1.323 session: 777 records and 2949158 bytes with a final newline.
Fifteen parents had two children; each was an assistant record carrying a
`tool_use` block, with the tool-result user record and the next assistant
record as children. Each of three closed turns, two started by task
notifications, ended with `stop_hook_summary` whose child was `turn_duration`.
Each summary had `hookCount` 1 and `hookInfos` entries containing `command`
and `durationMs`; the command named TUIOS. The one snapshot linked to its
input. A slash-command input carried `origin.kind` `human` without
`promptSource`. These are reviewer observations, not writer validation.

### Stop-only resume controls for Claude 2.1.325

A further owned disposable run used Claude 2.1.325 on native Windows build
26200, update revision 9711. The original process used the existing explicit
launcher settings. Two separate roots resumed its session while it remained
alive: one used only the exact launcher Stop command, the other used only a
different successful Stop command. File checkpointing was explicitly disabled
for all three processes. These were launch-local settings; no installed hook
or additional evidence channel was changed. Existing working and review panes
received no input.

The original ready turn had one `SessionStart:startup`, a matching
`stop_hook_summary` and its `turn_duration` child. The complete read contained
44 records and 413749 bytes with a final newline. The same-handler resume
subsequently produced an input linked to the original's latest turn-duration
record, tool call and result, reply, matching Stop summary and final
`turn_duration`. At that complete read there was still exactly one SessionStart,
no snapshots and no second human-input child. All 94 records and 502250 bytes
were parsed, with a final newline. The Stop summary records the command,
not an identity unique to the original launcher instance.

The different-handler control also appended without SessionStart. Its summary
failed the launcher-handler comparison, as expected; the complete read contained
107 records and 528039 bytes. A later no-tool input in the original process
created a second human-input child of its earlier tail. That read contained
112 records and 533369 bytes. Both reads had final newlines. The later branch
does not detect the same-handler writer at the earlier 94-record read.

Both the foreign input and the original's later control inherited turn position
4/4 and parent record 72. The different-handler turn emitted a Stop
`hook_success` attachment absent from the TUIOS Stop turns. Turn numbering
follows the conversation; the attachment reflects configuration. Neither
identifies the writer.

The metadata record named `session-owner` contains account and organization
identifiers, rather than a process-generation identifier; those values and
the recorded modes agreed across these roots. Repeated metadata also appeared
during original-process turns. These observations do not classify every
metadata shape or establish a complete supported profile. They defeat using
handler equality as writer identity, and leave the existing snapshot condition
empty when checkpointing is disabled.

Each process's diagnostic tool inspected the native file during its own
execution, retaining only structural facts:

| Diagnostic sample | Records | Bytes | Own input present | Own tool call present |
| --- | --- | --- | --- | --- |
| Original-process corrected probe | 67 | 453628 | Yes | Yes |
| Same-handler resume, first tool | 78 | 472869 | Yes | No |
| Different-handler resume, first tool | 99 | 509366 | Yes | No |

The original's first attempt failed because the diagnostic command included
sentence punctuation; only its corrected retry supplies a successful
original-process sample. Both resumed processes succeeded on their first tool.
Their tool-call records appeared in subsequent complete reads. The samples
support input-before-tool ordering in these executions, but do not prove the
universal persistence-before-effect contract. Tool-call persistence lag alone
does not violate the design's input-before-effect condition.

All owned Claude processes exited, their shell processes were removed with
the disposable session, and process absence was verified. The final complete
read contained 126 records and 538912 bytes with a final newline. The run took
approximately ten minutes including controls, inspection and cleanup. No
background work or schedule was started. Conversation and tool payloads were
parsed only in memory; saved artifacts contain allowlisted facts and counts.

### Checkpoint coverage proposal not adopted after independent review

The writer proposed requiring an input-linked `file-history-snapshot` for
every externally supplied input, in addition to rejecting unlinked snapshots
and requiring matched turn closure. Independent review did not adopt it.
A checkpoint-enabled foreign root can link its own input snapshot. Rejecting
it depends on an unlinked resume-time snapshot of unknown cause, another
foreign-signature heuristic. Requiring checkpointing rejects disabled
originals without proving which root wrote a record; snapshot coverage for
notification, slash and local-command inputs is itself unvalidated.

Keep an unlinked snapshot only as a conservative pending trigger. The design
now requires complete ledger coverage and closure for every writer: persist
every turn input before any tool or waiting effect, and persist closing records
after every other record of that turn, including fan-out leaves. Every
input-bearing record and every chain tip of every in-scope transcript needs
closure. Classify all append paths, with checkpointing enabled and disabled,
concurrently and after the original exits. The first-tool samples support the
input ordering in those runs only; the universal properties remain unproved.
Any root able to run without session persistence is outside the ledger and
must return to review.
Under Q26=A, confirmed on 2026-11-14, the work of such a root is the fourth
disclosed limit instead.

The user confirmed design Q24=A on 2026-11-14: only validated requestor
review-exchange starts in the Q23-bound file ordered after the marked resume
input by validated creation ordering, with their own lifecycle records, are
excluded, whichever root wrote them. Every other start stays in scope.
Completeness and closure replace Q23's writer-exclusivity condition. The choice
qualifies Q22/Q23 and requires fresh independent review; it is not validation.
No source, hook installation, disclosed limit or one-host delivery is approved.
Both host profiles remain unsupported. The remaining feasibility matrix,
production adapters, tests and implementation gates are still outstanding.
Validation-plan wording is aligned; implementation statuses are unchanged.

## Codex independent version findings

Both pre-input sources allowed by the
[design](design.v0.15.0.resume-paused.md#clearing-and-delivery-confirmation-for-resume-paused)
were investigated across the five observed Codex panes.

| Candidate | Observation | Feasibility result |
| --- | --- | --- |
| Attributable pane banner | Captures requested complete, unwrapped scrollback. Each returned the recent source, zero history rows and no recognized Codex version banner. | No version could be proved from the available captures. A successful capture response did not establish retained startup history. |
| Pane-tied process metadata | Each pane's shell process resolved to a Windows process with one direct Codex executable child. Neither file nor product version metadata supplied a version. The executable launch junction paths contained no version, and the process arguments did not provide one. The later kernel-image paths do carry a version. | Process linkage was observable, but it did not establish the host version. |

Discovery itself supplied no Codex version. No caller-installed CLI version
or post-delivery session metadata was substituted for the missing proof.
These findings concern the observed environment; they do not establish that
every Codex installation lacks usable process metadata or a retained banner.

Codex clear syntax, its clear-result signature, full-input acceptance and
later identity checks remain unvalidated. No profile or synthetic fixture
should label these signatures as supported until the complete profile is
validated. The following kernel-image observation provides a candidate
version source. The 2026-11-11 identity-query contract addresses attribution to
the originally loaded executable, including after rename and name reuse.
Its supported-build and lifecycle validation remains a blocking prerequisite.

### Follow-up Codex executable candidate

A further read-only probe invoked `--version` on the exact executable path
reported for each pane-linked Codex child process, outside the target panes.
All five probes returned `codex-cli 0.167.0` with exit zero. Each file's SHA-256
hash remained equal before and after its probe, and each original host process
retained its process identifier and creation time. No target input was sent.

This establishes a reproducible version response from those executable files.
It does not yet prove that a file at the reported path is the unchanged image
loaded by the already-running host. The profile must establish that attribution
and reject replacement or restart races before this candidate can satisfy
Q06. The installed caller command was not used as a substitute. The
[official Codex example](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)
documents `codex --version`, but does not establish running-image attribution.

### Independently reproduced Codex kernel-image channel

The independent reviewer identified `QueryFullProcessImageNameW` and
`GetMappedFileNameW` as a way to query the loaded executable rather than the
unversioned `current` junction exposed by ordinary process listings. The writer
reproduced both queries on five pane-linked Codex child processes. Both APIs
resolved each image to a standalone release directory naming version 0.167.0.
The same release's `codex-package.json` agreed on version, target and entrypoint.

The observed manifest has `layoutVersion` 1 and exactly eight keys:
`entrypoint`, `execServer`, `layoutVersion`, `pathDir`, `resourcesDir`, `target`,
`variant` and `version`. This is an observed schema, without an established
upstream compatibility guarantee. The design pins the layout and schema and
requires the profile's image digest; unknown layouts remain unsupported.

The reviewer separately tested a disposable sleeper: retargeting a junction
left its loaded image path unchanged; deletion and rewriting were refused;
renaming the release directory succeeded and left a stale path. These are
reviewer observations, not writer validation of the Codex lifecycle. Missing
paths, manifest disagreement and a different image at an old name must fail
closed. Controlled updater, rename and replacement experiments remain due.
The later Q14 session file must agree with the pre-input version before the
receiver consumes or claims; it cannot select the profile after delivery.

### Reviewer-observed Codex image identity on 2026-11-11

The reviewer observed `NtQueryInformationProcess` class 44,
`ProcessImageFileMapping`, return `STATUS_SUCCESS` for seven running Codex
images. On disposable sleepers it accepted original and renamed-original
handles, but returned `STATUS_UNSUCCESSFUL` for unrelated files, byte-identical
copies and replacements after tunneled recreation. Directory rename could
leave a stale kernel name. Limited process-query rights and read-only file
handles returned `STATUS_ACCESS_DENIED`; the observed query required
`PROCESS_QUERY_INFORMATION` and file execute access. These are reviewer
observations, not requestor validation.

The design opens the corroborated kernel-name file through the
`\\?\GLOBALROOT` prefix with read and execute access, sharing read and delete
only, and requires `STATUS_SUCCESS` from the identity
query before hashing through that same handle. It retains the handle and
invocation-only digest cache keyed by process id, creation time and kernel
image name. Each input rechecks process identity, both image-name APIs,
manifest agreement and the identity query. Missing files, failed opens and
every other query result are unsupported evidence. Creation-time ordering
is superseded by file identity; no same-user replacement exception applies.

Microsoft does not document class 44. Profiles pin validated OS build numbers
and record the update revision observed during validation. Runtime build
metadata is the `dwBuildNumber` that `RtlGetVersion` returns. System file
versions, such as Python's `sys.getwindowsversion().platform_version`, are not
build evidence. Missing or invalid
decimal metadata or a build outside the pinned set means unsupported evidence
and no input. The update revision is evidence rather than a runtime pin;
non-success queries within a pinned build still fail closed.
Supported-build access/status handling, same-handle hashing and races,
directory rename, tunneling, byte-identical and other pinned-release
replacements, and actual updater rename/cleanup remain to validate. The
primitive query should accept the renamed original; full profile support
still requires the supported path/layout. This resolves the strict attribution
contract within approved process metadata, without reading process memory.

### Reviewer-observed image address source on 2026-11-12

On a disposable sleeper on Windows 11 build 26200, the reviewer observed
`EnumProcessModulesEx` denied with error 5 under query rights alone; it succeeded
only with `PROCESS_VM_READ`. A query-rights-only `VirtualQueryEx` walk of 499
regions found exactly one `MEM_IMAGE` allocation whose `GetMappedFileNameW`
name matched the native `QueryFullProcessImageNameW` name. These are reviewer
observations, not requestor validation. The design uses this allocation-metadata
walk over the same process handle, requiring exactly one committed matching
allocation and a complete walk. Module enumeration, process environment block
reads and other sources needing memory-read rights are excluded. Native-name
comparison and missing, ambiguous or incomplete results remain to validate.

## Claude transcript and task-state findings

Four pane-reported Claude session identifiers resolved to their corresponding
transcripts. The observed records contained version, session and working
directory fields, with version 2.1.321 and matching session identifiers.
Some historical working-directory values differed from the discovery value;
complete canonical path and latest-input validation remains implementation
work rather than an established profile.

The first inspected transcript contained background-task start results,
task-status attachments and task notifications. Its task-status attachments
recorded individual running tasks. They did not expose a complete current
task inventory, a positive zero-task assertion or a host-process generation
binding. The session-owner record identified session/account ownership; it
did not establish task absence or a restart boundary.

Task completion notifications and individual task statuses are useful
lifecycle evidence. The inspected records do not establish that every task
start, completion and restart transition is represented in a complete ledger.
In particular, an old running status or completion notification does not
prove current task state after host restart. No authoritative schema contract
or observed positive absence record was validated to close that gap.

Missing task indicators and background-shell counts were not interpreted as
proof that no task remains. No permitted channel supplies current Claude
watcher liveness in this delivery: every potential wait stays pending with
no input. Requirement Q04=A excludes descendant background-process
enumeration. Positive absence, watcher lifecycle and typed-input distinction
still require complete validated evidence.

The follow-up schema scan covered all four matching transcripts. Among the
task, background, session and restart record categories examined, it found
individual task-status attachments, session-context attachments and
session-owner records. None supplied a complete task snapshot or a
host-process generation field. All scanned lines parsed successfully. This
bounded schema check does not establish a complete host lifecycle contract.

### Claude documented task interfaces

The [official command reference](https://code.claude.com/docs/en/commands)
describes `/tasks` as the current session's background-work view. The
[background-command reference](https://code.claude.com/docs/en/interactive-mode#background-bash-commands)
describes cleanup on exit and distinguishes an exited session from one that
continues in the background. Neither page establishes a complete transcript
ledger or a positive current zero-task record. These general descriptions do
not validate restart or abnormal-exit behavior for the observed version.
No `/tasks` command was sent, and no task interface was operated.

On 2026-11-12 the independent reviewer assessed `/tasks` against the approved
read-only boundary and did not recommend it. Typing it changes the latest
input used by Q16 and opens a task-control dialog. Its current-process
registry cannot exclude commands orphaned by an earlier host process, and
coverage of monitors, subagents, schedules and wakeups is undocumented.
Reading the display would also require a validated screen-layout profile.
This assessment proposes no additional channel and authorizes no pane input.

### Independent review's Claude lifecycle-ledger proposal

The reviewer proposed a generation-bounded transcript ledger using
`toolUseResult.backgroundTaskId` starts and terminal `queue-operation`
notifications, distinguishing `origin.kind` and `promptSource` for typed input
and task notifications. It also identified restored `CronCreate` schedules,
background subagents and work surviving clear as completeness obligations.
The design now records the exact candidate contract and validation boundaries.

This does not validate the ledger. A start without a terminal record warrants
pending with no input; the proved-global-wait branch is unavailable for Claude
in this delivery because there is no permitted current-liveness proof.
Positive absence separately requires complete
start/end coverage of every in-scope host-managed waiting mechanism (Q20=A)
and continued accounting for
unmatched starts across process generations. Forced termination in the
writer's disposable 2026-11-12 probes left commands running, so generation
changes cannot establish cleanup. These guarantees remain unproved for the
observed host.

### Review evidence and settled launcher source

The reviewer observed eleven PowerShell-tool background starts, all recorded
with `taskType` equal to `local_bash`; no Bash-tool background start was
observed. Subagent command placement in the main or subagent transcript
remains unverified. Host documentation describes retained tasks when a session
continues in the background. Such a task cannot be counted as ended merely
because a pane's process generation changed.

The reviewer also observed existing TUIOS executable SessionStart commands,
recorded as `hook_success` with `SessionStart:startup` or
`SessionStart:compact`, and pane identity source `report`, despite the managed
integration being reported as not installed. On 2026-11-11 the reviewer traced
the source to senv `tuitp_windows.py`, function `write_claude_hooks`: it generates
TUIOS Claude hooks in a temporary configuration and copies them into
launcher-owned settings. `tuitp.pane.bat` passes that existing file to Claude
via `--settings`. The reviewer's pane had 14 hook events invoking TUIOS Claude
integration. This is reviewer-observed source and launch behavior, not
requestor validation or universal TUIOS injection. The pinned
[TUIOS integration documentation](https://github.com/Gaurav-Gosain/tuios/blob/850335c0c08bb8b802406fcc7f254355c89af04a/integrations/claude-code/README.md)
describes installed settings hooks. Its
[Claude event map](https://github.com/Gaurav-Gosain/tuios/blob/850335c0c08bb8b802406fcc7f254355c89af04a/internal/integration/hook_claude.go)
reports identity and transcript path for SessionStart. A pane with neither the
launcher settings nor an installed TUIOS integration has no marker and stays
pending. Reading a recorded command installs nothing. Validate that startup
is the first relevant record and covers the complete process generation and
session. Q18=A now limits eligible profiles to existing explicit launcher
settings only. An installed TUIOS integration, alone or combined with launcher
settings, and missing or uncertain provenance remains pending;
inspect documented excluded sources without installing hooks. Root/nested
reporting, source exclusion and complete persistence still need validation.
The recorded command
cannot distinguish the sources; command-line inspection is excluded because
it reads process memory. The deferred senv effort must preserve launch settings or
affected panes remain pending. The shared command installs nothing and
operates independently of the launcher.

### Independent reviewer observations on 2026-11-12

The reviewer inspected only its own `tuitp`-launched Claude 2.1.322 pane,
read-only, and reported the following. These are attributed reviewer
observations, not reproduced writer validation or supported-profile evidence.

| Observation | Reported evidence and limit |
| --- | --- |
| Startup ordering | First timestamped record was a TUIOS `SessionStart:startup` `hook_success`, 41 seconds after process creation; five untimestamped metadata records preceded it. The hook ran for 14.8 seconds. This is one ordering observation, not a general persistence guarantee. |
| Complete transcript read | 850 records, final newline, 17 top-level record types and 20 attachment types. A running `task_status` snapshot followed compaction. Three `backgroundTaskId` starts each had a terminal enqueue. Snapshots are not inventories. |
| Pane metadata | No process field in the TUIOS pane record; its activity log had evicted its first eight entries, including startup. Neither supplies durable generation binding. |
| Settings | No user, project or local settings file held TUIOS hooks; their modification times preceded process creation. This does not prove historical configuration continuity or exclude every documented hook source. |
| Launcher source | `tuitp` generates hooks with `tuios integration install claude-code --no-skill` in a temporary `CLAUDE_CONFIG_DIR`, increases timeouts and passes explicit settings only to root Claude. It uses `--resume` for native restoration and retries failures within five minutes, up to three times, in the same pane shell. A new session can conceal an earlier process's unmatched background start. |
| Persistence order | Of 703 timestamped records, 43 appeared after records carrying later timestamps, by up to 42.4 seconds. This shows event timestamps and file order can differ; it does not validate timestamp semantics or turn closure for every mechanism. |
| Unrecorded hooks | Launcher settings defined 14 hook events. Across about 120 calls, the pane activity log showed PreToolUse/PostToolUse execution, while the transcript held only two SessionStart hook records. Hook execution and configuration history cannot be reconstructed from those records. |
| Interactive marking | Every record carrying `entrypoint` in the reviewer's interactive session had value `cli`. Nested-session discrimination remains an experiment, not a validated binding rule. |
| Project-directory encoding, 2026-11-12 | The reviewer observed this checkout's Claude project-directory name turning `_` as well as path separators into `-`. This lossy name cannot uniquely identify a checkout. Sessions launched from checkout subdirectories use other project directories. This is reviewer observation, not writer validation. |

The resulting candidate binds the direct child's creation time to the first
timestamped startup marker and rejects later noncompact SessionStart records.
Launch-time resume, timestamp semantics and item 1's generation
completeness and closure for every writer still need validation. A backward clock step between generations is
unobservable through approved sources and is a reported Q20=A limit. Late
records also require a turn-closure experiment: every call and result must
match, and the validated final turn record must be present. An idle screen
alone does not prove persistence. Current hook files and modification times
do not alone exclude earlier or dynamically changed handlers; copies and
renames can preserve old times, and skill/subagent hooks appear mid-session.
Record-level root/nested discrimination is separate from that missing history.
A version-pinned closed-world
classification rejects unknown records, tools, result shapes and open calls,
but cannot replace complete persistence proof: a known foreground tool or hook
could leave work without introducing a new record type.

On 2026-11-12 the user confirmed Q18=A, Q19=A and Q20=A. Q19 requires every
transcript in this checkout's Claude project directory with activity since
the last OS boot and complete relevant durable schedule definitions regardless
of boot, with all enumeration and record bytes accounted. Validate activity
selection and true-boot semantics, including conservative Windows fast-startup
handling. Missing history, uncertain activity or schedule restoration stays
pending. A true boot can bound ordinary surviving processes but does not
discharge durable schedules restored after reboot.

Q20 limits positive absence to host-managed waiting mechanisms: background
tasks, Monitor, subagents/commands, schedules/wakeups and foreground work moved
into background. Complete start/end persistence remains mandatory for every
enabled in-scope mechanism. Claude reviewer watchers must use host background
mechanisms. Report three residual limits at activation: processes detached
by completed foreground commands or hooks may be missed; earlier hook-handler
configuration history is unavailable; backward clock changes between process
generations are unobservable. Descendant enumeration remains excluded.
Q26=A, confirmed on 2026-11-14, adds a fourth limit for work of roots with no
records in Q19's read set. Q27=B, confirmed on 2026-11-15 and consolidated on
2026-11-17, adds a fifth limit for a running local shell command whose input
is not yet recorded, with an all-pane idle guard; Q28=A keeps the cases the
agent cannot reproduce on tested conservative handling.
Ownership fencing and lease expiry cannot prove watcher absence. Optional
validated rejection of recorded detaching launchers is defense in depth only.
Unknown or incomplete in-scope evidence stays pending. These decisions approve
no new source or hook installation and establish no supported profile. Both
hosts require disposable validation and all other gates. These decisions and
aligned documents were independently reviewed in exchange 2 round 8 before
human-authorized consolidation.

Round 4 requires candidate-level recorded `cwd` validation under the design's
path rules. Exclude another checkout's transcript only on validated evidence;
otherwise keep it in scope. Include checkout-subdirectory session directories
unless validation proves they cannot hold a reviewer watcher for this checkout.
Parse classified structural fields only in memory; never print or retain
conversation content or tool payloads. Report counts, byte costs and classified
reasons only. The user confirmed Q21=A, Q22=A and Q23=A on 2026-11-12; their contracts
below qualify the earlier Q19/Q20 scope statements without replacing their
historical answer records. Neither host is supported until disposable validation
and all remaining gates pass.

Q21=A selects a boot instant recorded once at boot from a validated boot
process's creation timestamp within process metadata. Never select history
using current time minus uptime. Validate the concrete boot process, timestamp
stability under clock changes, uptime semantics, comparison tolerance and
Windows fast startup. Compare fixed and computed instants and keep detected
net backward movement beyond the validated tolerance pending. The disclosed
Q20 clock limit now covers undetectable backward changes since boot, including
offsetting changes, rather than only changes between process generations.
Only that named boot-instant metadata source is approved; event logs and
general extra channels remain excluded. No boot source or tolerance is yet
validated by the choice.

The uptime value must count time spent in sleep and hibernation. Validate this,
and test suspension between boot and the decision. An uptime that excludes
suspended time would hide a backward change of up to the suspended duration.

Q22=A, as qualified by Q24=A, excludes only validated requestor review-exchange
starts in the Q23-bound file ordered after marked input by validated creation
ordering, with their own lifecycle records, whichever root wrote them. All
other work, including the requestor's own other post-marker work, stays in scope.
Earlier starts, every other transcript and reviewer `wait-any-request` remain in scope,
including starts inside the proposed exception and former-reviewer starts
after role switching, under normal start/end matching.
Uncertain file binding, operation classification or ordering stays pending. Read and classify the evidence
needed to establish the exception, account for every byte and refresh exact
takeover proof and both panes' required bindings before activation. Validate
initial activation and later continuation; no general live-pane exclusion is
approved. These are requirements for future experiments, not new observations.

The exception removes only starts that validated creation ordering places after
the marked resume input, with those starts' own lifecycle records. File position
alone never places a record after the marker. Terminal, stop and completion
records after the marker still match in-scope starts ordered before it. This
includes any such record the host writes into a later session file after a
clear. A start whose order relative to the marker is uncertain stays in scope.

Inside the excluded range, a start that invokes the review-exchange launcher
counts as a reviewer watcher unless its operation parses as a validated
requestor operation. A start qualifies only when its complete recorded command matches exactly one recognized requestor invocation form with a requestor-only operation. Chained, piped, wrapped or multi-operation commands, and operations either role may run, stay in scope under normal start/end matching. Validate the recognized invocation forms for each pinned
version. A recognized watcher stays in scope under normal start/end matching
and blocks until its validated terminal record.

Under Q23=A, bind the proved requestor's post-marker range through the session
file in which acceptance proved its marked resume. On initial activation and
later continuation, require current session identity source `report`; a first
timestamped record that is the validated TUIOS SessionStart marker for `startup`
or `clear`, at or after creation of the requestor shell's single direct Claude
child; no later SessionStart other than `compact`; the proved marked input in
that file; unchanged process identity across the read; and validated ordering
and item 1's completeness and closure for every writer (Q24=A). Missing or uncertain evidence remains pending.
This covers the command's `--clear` and a manual clear before the run. Q19=A
retains pre-clear transcripts and Q22=A retains earlier starts and matches
their lifecycle records across files. Item 1's complete-generation rule still
governs the reviewer's absence proof. Validate the clear-marker shape, process
precedence and cross-file lifecycle matching in disposable sessions; timestamp
comparison retains Q21=A's disclosed clock limitation. No new channel is added,
and the human choice itself establishes no supported profile.

### Reviewer-reported Claude schedule documentation on 2026-11-12

The reviewer reports that Claude 2.1.322's `CronCreate` description shown to its
session says `durable` has no effect, jobs are session-only and disappear when
Claude exits, and recurring jobs expire automatically after seven days. This
is host documentation, not runtime validation or a launch-time-resume contract.
Step 1 must determine schedule survival and restoration for each pinned version,
including launch-time and in-process resume. A validated none makes the relevant
regardless-of-boot schedule set empty by contract, never by assumption.

The proposed notification-persistence bound proves at most past liveness,
even if a hard bound could be established. It does not establish current
liveness at the later decision time. The design retains pending for an
unproved wait and requires positive absence before activation.

The 2026-11-11 identity query supersedes the earlier Codex creation-time proposal with the
reviewer-observed image-identity query above. Path, timestamp and digest checks
alone remain insufficient; strict attribution now has a concrete contract.
Support still depends on disposable validation. No same-user replacement
exception or process-memory channel was authorized.

## Design-review return for the two evidence gaps

The independent review proposed a candidate channel for each original gap:

1. Codex kernel-image queries and the same-release manifest provide
   reproducible pane-tied path and release metadata. The reviewer's 2026-11-11
   class-44 observations resolve original-loaded-image attribution as a strict
   contract. Validate each supported Windows build, the pinned digest through
   the identity-checked handle, and lifecycle/race rules before enabling
   support. There is no same-user replacement exception or process-memory read.
2. Claude's proposed transcript ledger gives a testable persistence contract,
   with explicit completeness, restart, schedules and liveness requirements.
   It still requires controlled disposable validation; current read-only
   observations do not prove positive absence.

Design Q14's session-file choice remains in force. No hook was installed or
assumed universal. Requiring hooks for independent version proof would require
explicitly reopening that decision. The kernel-image channel stays within
the confirmed process-metadata choice. No weaker task-state rule has been
selected by this investigation.

## Deferred implementation and validation boundaries

No host adapter, shared synthetic builder or profile test was created.
Synthetic fixtures can test a validated contract, but cannot establish that
an actual host provides the necessary evidence. The implementation and
validation plans now align their Step 1 expectations with the consolidated
design. Validation status and evidence placeholders are unchanged; no step
has been marked complete and no later step is enabled by these findings.

Following design consolidation, Step 1 of both plans was revised to the
converged Codex identity, build-pinning and image-name contract and to the
Claude marker-source and pending rules before the disposable experiments.
This alignment supplies expectations, not proof that the contracts pass.

Once the design gaps are resolved, Step 1 still needs all planned tests and
adapters. Its Codex session-file proof must enumerate regular JSONL files
across every date partition, including older active conversations, and
judge uniqueness across all candidates modified since delivery. The
filesystem timestamp resolution and lower-bound allowance must be explicitly
validated. Every refresh must account for metadata and record bytes, reject
incomplete enumeration or records, and recheck uniqueness, latest complete
input and live pane bindings. None of those obligations was tested here.

The supported input/result/clear signatures, actual lifecycle timing and
groundhog gates remain outstanding. The separate
[deferred senv integration checklist](feature-request.v0.15.0.resume-paused.md#deferred-senv-integration-follow-up)
also remains unchecked.
