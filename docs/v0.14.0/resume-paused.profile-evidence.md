# Resume-paused host evidence feasibility

## Step 1 investigation outcome

Step 1 is **incomplete**. Read-only observations on 2026-11-10 did not
establish a supported profile for either host. This document records the
feasibility stop required by
[Step 1 of the implementation plan](plan.v0.14.0.resume-paused.md#step-1-validate-pane-tied-host-profiles-before-input).
It does not authorize delivery or change a confirmed design decision.

The observed environment used TUIOS 0.12.1 with its pure-Go backend. Claude
transcripts reported version 2.1.321. Follow-up kernel-image queries returned
pane-linked release paths naming Codex 0.167.0 in five processes. The reviewer's
2026-11-11 image-identity observations resolve the strict attribution contract
within process metadata; the requestor has not validated it. An observed
version alone does not establish a supported input, result, clearing or
task-state profile. Claude ledger completeness remains unproved.

## Read-only observation boundary

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
coverage of every enabled background mechanism and validated cleanup across
process generations. These guarantees remain unproved for the observed host.

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
session. Also validate installed integration alone and both sources together,
including duplicate or merged SessionStart records. The recorded command
cannot distinguish the sources; command-line inspection is excluded because
it reads process memory. The deferred senv effort must preserve launch settings or
affected panes remain pending. The shared command installs nothing and
operates independently of the launcher.

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
validation plans remain unchanged; no step has been marked complete, and
no later step is enabled by these findings.

After design consolidation, Step 1 of the implementation and validation plans
must be revised to the converged Codex identity, build-pinning and image-name
contract and to the Claude marker-source and pending rules before Step 1
resumes. The plans are not edited during this design review.

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
