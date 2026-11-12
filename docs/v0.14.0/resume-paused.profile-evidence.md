# Resume-paused host evidence feasibility

## Step 1 investigation outcome

Step 1 is **incomplete**. Read-only observations on 2026-11-10 and disposable
experiments on 2026-11-12 have not established a supported profile for either
host. This document records the
feasibility stop required by
[Step 1 of the implementation plan](plan.v0.14.0.resume-paused.md#step-1-validate-pane-tied-host-profiles-before-input).
It does not authorize delivery or change a confirmed design decision.

The observed environment used TUIOS 0.12.1 with its pure-Go backend. Claude
transcripts reported version 2.1.321. Follow-up kernel-image queries returned
pane-linked release paths naming Codex 0.167.0 in five processes. The reviewer's
2026-11-11 image-identity observations resolve the strict attribution contract
within process metadata; the writer has since reproduced the primitive but
has not validated a complete profile. An observed
version alone does not establish a supported input, result, clearing or
task-state profile. Claude ledger completeness remains unproved.

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

## Codex independent version findings

Both pre-input sources allowed by the
[design](design.v0.14.0.resume-paused.md#clearing-and-delivery-confirmation-for-resume-paused)
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
Launch-time resume, timestamp semantics and single-writer behavior after root
exit still need validation. A backward clock step between generations is
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

Q22=A excludes from the absence check only validated new work of the proved
requestor pane's current process generation. Earlier starts, every other
transcript and recognized reviewer `wait-any-request` starts remain in scope,
including starts inside the proposed exception and former-reviewer starts
after role switching, under normal start/end matching.
Uncertain generation or ordering stays pending. Read and classify the evidence
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
requestor operation. Validate the recognized invocation forms for each pinned
version. A recognized watcher stays in scope under normal start/end matching
and blocks until its validated terminal record.

Under Q23=A, bind the proved requestor's post-marker range through the session
file in which acceptance proved its marked resume. On initial activation and
later continuation, require current session identity source `report`; a first
timestamped record that is the validated TUIOS SessionStart marker for `startup`
or `clear`, at or after creation of the requestor shell's single direct Claude
child; no later SessionStart other than `compact`; the proved marked input in
that file; unchanged process identity across the read; and validated ordering
and single-writer behavior. Missing or uncertain evidence remains pending.
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
[deferred senv integration checklist](feature-request.v0.14.0.resume-paused.md#deferred-senv-integration-follow-up)
also remains unchecked.
